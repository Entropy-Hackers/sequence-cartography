from pathlib import Path

import cv2
import numpy as np
import pytest

FPS = 25
W, H = 160, 90
# three "shots" that differ clearly in brightness/saturation, 40 frames each
SHOTS = [(20, 20, 20), (230, 230, 230), (0, 200, 0)]
SHOT_LEN = 40


@pytest.fixture(scope="session")
def video(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("video") / "shots.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    assert writer.isOpened()
    for color in SHOTS:
        for i in range(SHOT_LEN):
            frame = np.full((H, W, 3), color, np.uint8)
            # a moving bar so frames within a shot are not identical
            cv2.rectangle(frame, (i * 3, 30), (i * 3 + 8, 60), (128, 128, 128), -1)
            writer.write(frame)
    writer.release()
    return path
