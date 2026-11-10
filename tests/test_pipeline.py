import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from seqcarto.omimage import Geometry, plan_scene
from seqcarto.pipeline import analyze, timecode

FPS = 25
W, H = 160, 90
# three "shots" that differ clearly in brightness/saturation, 40 frames each
SHOTS = [(20, 20, 20), (230, 230, 230), (0, 200, 0)]
SHOT_LEN = 40


@pytest.fixture(scope="module")
def video(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("video") / "shots.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    assert writer.isOpened()
    for color in SHOTS:
        for i in range(SHOT_LEN):
            frame = np.full((H, W, 3), color, np.uint8)
            # a moving bar so frames within a shot are not identical
            cv2.rectangle(frame, (i * 3, 30), (i * 3 + 8, 60), (255, 255, 255), -1)
            writer.write(frame)
    writer.release()
    return path


def test_plan_scene_short_scene_has_one_keyframe():
    plan = plan_scene(0, 100, 140, fps=25)
    assert len(plan.keyframes) == 1
    assert len(plan.thumbnails) == 5
    assert plan.width == 500
    assert all(100 <= f < 140 for f in plan.keyframes + plan.thumbnails)


def test_plan_scene_long_scene():
    plan = plan_scene(0, 0, 25 * 60, fps=25)  # 60 s -> 12 keyframes
    assert len(plan.keyframes) == 12
    assert len(plan.thumbnails) == 60
    assert plan.thumbnails == sorted(plan.thumbnails)


def test_timecode():
    assert timecode(0) == "00:00:00.000"
    assert timecode(3725.5) == "01:02:05.500"


def test_analyze_end_to_end(video, tmp_path):
    out = analyze(str(video), tmp_path, show_progress=False)
    manifest = json.loads((out / "manifest.json").read_text())

    scenes = manifest["scenes"]
    assert [(s["start_frame"], s["end_frame"]) for s in scenes] == [
        (0, 40), (40, 80), (80, 120)
    ]
    assert manifest["source"]["frames"] == 120

    geo = Geometry.for_video(W, H)
    for scene, color in zip(scenes, SHOTS):
        img = cv2.imread(str(out / scene["omimage"]))
        assert img.shape == (geo.total_h, 500, 3)
        # keyframe band corner, thumbnail band, stripe band carry the shot colour
        for y in (5, geo.big_h + 2, geo.big_h + geo.small_h + 2):
            assert np.abs(img[y, 2].astype(int) - color).max() < 40

    assert (out / "scenes.csv").read_text().count("\n") == 4
    assert len(manifest["stripes"]["tiles"]) == 1


def test_end_limits_analysis(video, tmp_path):
    out = analyze(str(video), tmp_path, end_seconds=2.0, show_progress=False)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["scenes"][-1]["end_frame"] <= 51
