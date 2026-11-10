"""Scene detection with PySceneDetect."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scenedetect import ContentDetector, SceneManager, open_video

# Defaults taken over from the 2018/19 prototype.
DEFAULT_THRESHOLD = 35.0
DEFAULT_MIN_SCENE_LEN = 25  # frames


@dataclass
class VideoInfo:
    fps: float
    width: int
    height: int
    frames: int  # number of frames covered by the detected scenes


def detect_scenes(
    path: Path,
    threshold: float = DEFAULT_THRESHOLD,
    min_scene_len: int = DEFAULT_MIN_SCENE_LEN,
    end_seconds: float | None = None,
    show_progress: bool = False,
) -> tuple[list[tuple[int, int]], VideoInfo]:
    """Return scenes as ``[(start_frame, end_frame_exclusive), ...]`` and video info."""
    video = open_video(str(path))
    fps = float(video.frame_rate)
    if fps <= 0:
        raise ValueError(f"cannot determine frame rate of {path}")
    width, height = video.frame_size

    manager = SceneManager()
    manager.add_detector(
        ContentDetector(threshold=threshold, min_scene_len=min_scene_len)
    )
    manager.detect_scenes(
        video=video, end_time=end_seconds, show_progress=show_progress
    )
    # start_in_scene=True: a video without cuts is one scene, not an empty list.
    scene_list = manager.get_scene_list(start_in_scene=True)
    scenes = [(s.frame_num, e.frame_num) for s, e in scene_list]
    scenes = [(s, e) for s, e in scenes if e > s]
    frames = scenes[-1][1] if scenes else 0
    return scenes, VideoInfo(fps=fps, width=width, height=height, frames=frames)
