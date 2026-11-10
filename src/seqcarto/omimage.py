"""OM images: one composite overview image per scene.

Layout (same as the 2018/19 prototype)::

    +--------------------+--------------------+----
    |  keyframe (500px)  |  keyframe          |  ...   one every ~5 s
    +----+----+----+----+----+----+----+----+---
    |thmb|thmb|thmb|thmb|thmb|thmb|thmb|thmb| ...    five per keyframe (100px)
    +----+----+----+----+----+----+----+----+---
    |  slit-scan: centre pixel column of every frame, scaled to width |
    +-----------------------------------------------------------------+

The video is read sequentially exactly once; frames are picked up as they
pass by, so no seeking is needed.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

log = logging.getLogger(__name__)

SMALL_WIDTH = 100
THUMBS_PER_KEYFRAME = 5
BIG_WIDTH = SMALL_WIDTH * THUMBS_PER_KEYFRAME
SECONDS_PER_KEYFRAME = 5.0
STRIPE_TILE_WIDTH = 1500  # frames per overview stripe tile


@dataclass(frozen=True)
class Geometry:
    small_h: int
    big_h: int

    @classmethod
    def for_video(cls, width: int, height: int) -> Geometry:
        return cls(
            small_h=max(1, round(SMALL_WIDTH * height / width)),
            big_h=max(1, round(BIG_WIDTH * height / width)),
        )

    @property
    def stripe_h(self) -> int:
        return self.big_h

    @property
    def total_h(self) -> int:
        return self.big_h + self.small_h + self.stripe_h


@dataclass
class ScenePlan:
    index: int
    start: int  # first frame
    end: int  # exclusive
    keyframes: list[int]
    thumbnails: list[int]

    @property
    def width(self) -> int:
        return len(self.thumbnails) * SMALL_WIDTH


def plan_scene(index: int, start: int, end: int, fps: float) -> ScenePlan:
    duration = end - start
    n_big = max(1, round(duration / (SECONDS_PER_KEYFRAME * fps)))
    n_small = n_big * THUMBS_PER_KEYFRAME
    d_small = duration / n_small
    d_big = duration / n_big
    last = end - 1

    def clamp(f: float) -> int:
        return min(last, start + int(f + 0.5))

    return ScenePlan(
        index=index,
        start=start,
        end=end,
        keyframes=[clamp(d_big / 2 + j * d_big) for j in range(n_big)],
        thumbnails=[clamp(i * d_small) for i in range(n_small)],
    )


@dataclass
class _SceneCanvas:
    plan: ScenePlan
    geo: Geometry
    image: np.ndarray = field(init=False)
    columns: list[np.ndarray] = field(default_factory=list)
    wanted: dict[int, list[tuple[str, int]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.image = np.zeros((self.geo.total_h, self.plan.width, 3), np.uint8)
        for j, f in enumerate(self.plan.keyframes):
            self.wanted.setdefault(f, []).append(("big", j))
        for i, f in enumerate(self.plan.thumbnails):
            self.wanted.setdefault(f, []).append(("small", i))

    def add_frame(self, frame_no: int, frame: np.ndarray, column: np.ndarray) -> None:
        self.columns.append(column)
        g = self.geo
        for kind, slot in self.wanted.pop(frame_no, ()):
            if kind == "big":
                x = slot * BIG_WIDTH
                self.image[0 : g.big_h, x : x + BIG_WIDTH] = cv2.resize(
                    frame, (BIG_WIDTH, g.big_h), interpolation=cv2.INTER_AREA
                )
            else:
                x = slot * SMALL_WIDTH
                y = g.big_h
                self.image[y : y + g.small_h, x : x + SMALL_WIDTH] = cv2.resize(
                    frame, (SMALL_WIDTH, g.small_h), interpolation=cv2.INTER_AREA
                )

    def finish(self) -> np.ndarray:
        if self.columns:
            g = self.geo
            stripe = np.concatenate(self.columns, axis=1)
            y = g.big_h + g.small_h
            self.image[y : y + g.stripe_h, :] = cv2.resize(
                stripe, (self.plan.width, g.stripe_h), interpolation=cv2.INTER_AREA
            )
        return self.image


@dataclass
class RenderResult:
    scenes: list[ScenePlan]
    omimages: list[Path]
    stripe_tiles: list[Path]
    frames_read: int


def render(
    video_path: Path,
    scenes: list[tuple[int, int]],
    fps: float,
    out_dir: Path,
    progress: Callable[[int], None] | None = None,
) -> RenderResult:
    """Read the video once and write one OM image per scene plus overview stripe tiles."""
    om_dir = out_dir / "omimages"
    stripe_dir = out_dir / "stripes"
    om_dir.mkdir(parents=True, exist_ok=True)
    stripe_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise OSError(f"cannot open video: {video_path}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    geo = Geometry.for_video(width, height)
    plans = [plan_scene(i, s, e, fps) for i, (s, e) in enumerate(scenes)]
    total = plans[-1].end if plans else 0

    done_plans: list[ScenePlan] = []
    omimages: list[Path] = []
    tiles: list[Path] = []
    tile_cols: list[np.ndarray] = []

    def flush_tile() -> None:
        if tile_cols:
            p = stripe_dir / f"stripe_{len(tiles):05d}.jpg"
            cv2.imwrite(str(p), np.concatenate(tile_cols, axis=1))
            tiles.append(p)
            tile_cols.clear()

    def write_scene(canvas: _SceneCanvas, end: int) -> None:
        plan = canvas.plan
        if end < plan.end:  # video ended early: trim the scene
            log.warning("scene %d truncated at frame %d (planned %d)", plan.index, end, plan.end)
            plan.end = end
        if canvas.wanted:
            log.warning("scene %d: %d frames could not be read", plan.index, len(canvas.wanted))
        p = om_dir / f"scene_{plan.index:05d}.jpg"
        cv2.imwrite(str(p), canvas.finish())
        omimages.append(p)
        done_plans.append(plan)

    frame_no = 0
    scene_iter = iter(plans)
    current = next(scene_iter, None)
    canvas = _SceneCanvas(current, geo) if current else None
    try:
        while canvas is not None and frame_no < total:
            ok, frame = cap.read()
            if not ok or frame is None:
                log.warning("video ended at frame %d, expected %d", frame_no, total)
                break
            mid = frame.shape[1] // 2
            column = cv2.resize(
                frame[:, mid : mid + 1], (1, geo.stripe_h), interpolation=cv2.INTER_AREA
            )
            canvas.add_frame(frame_no, frame, column)
            tile_cols.append(column)
            if len(tile_cols) == STRIPE_TILE_WIDTH:
                flush_tile()
            frame_no += 1
            if progress:
                progress(frame_no)
            if frame_no == canvas.plan.end:
                write_scene(canvas, frame_no)
                current = next(scene_iter, None)
                canvas = _SceneCanvas(current, geo) if current else None
        if canvas is not None and frame_no > canvas.plan.start:
            write_scene(canvas, frame_no)
        flush_tile()
    finally:
        cap.release()

    return RenderResult(done_plans, omimages, tiles, frame_no)
