"""End-to-end analysis: source -> scenes -> OM images -> manifest."""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from . import __version__
from .detect import DEFAULT_MIN_SCENE_LEN, DEFAULT_THRESHOLD, detect_scenes
from .omimage import STRIPE_TILE_WIDTH, render
from .source import resolve

log = logging.getLogger(__name__)


def timecode(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def analyze(
    input_: str,
    output_root: Path,
    threshold: float = DEFAULT_THRESHOLD,
    min_scene_len: int = DEFAULT_MIN_SCENE_LEN,
    end_seconds: float | None = None,
    show_progress: bool = True,
) -> Path:
    """Analyze a video and return the output directory containing ``manifest.json``."""
    source = resolve(input_, output_root / "_downloads")
    out_dir = output_root / source.slug
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("detecting scenes in %s", source.path)
    scenes, info = detect_scenes(
        source.path, threshold, min_scene_len, end_seconds, show_progress
    )
    log.info("%d scenes, %d frames at %.3f fps", len(scenes), info.frames, info.fps)

    with tqdm(total=info.frames, unit="frame", desc="rendering", disable=not show_progress) as bar:
        result = render(
            source.path, scenes, info.fps, out_dir,
            progress=lambda n: bar.update(n - bar.n),
        )

    fps = info.fps
    scene_entries = []
    for plan, img in zip(result.scenes, result.omimages, strict=True):
        scene_entries.append({
            "index": plan.index,
            "start_frame": plan.start,
            "end_frame": plan.end,
            "start_time": timecode(plan.start / fps),
            "end_time": timecode(plan.end / fps),
            "duration_seconds": round((plan.end - plan.start) / fps, 3),
            "omimage": img.relative_to(out_dir).as_posix(),
            "omimage_width": plan.width,
            "keyframes": plan.keyframes,
            "thumbnails": plan.thumbnails,
        })

    manifest = {
        "generator": f"seqcarto {__version__}",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "title": source.title,
            "url": source.url,
            "file": source.path.name,
            "fps": fps,
            "width": info.width,
            "height": info.height,
            "frames": result.frames_read,
        },
        "parameters": {
            "detector": "ContentDetector",
            "threshold": threshold,
            "min_scene_len": min_scene_len,
            "end_seconds": end_seconds,
        },
        "stripes": {
            "frames_per_tile": STRIPE_TILE_WIDTH,
            "tiles": [p.relative_to(out_dir).as_posix() for p in result.stripe_tiles],
        },
        "scenes": scene_entries,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    with open(out_dir / "scenes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "start_frame", "end_frame", "start_time", "end_time"])
        for s in scene_entries:
            w.writerow([s["index"], s["start_frame"], s["end_frame"], s["start_time"], s["end_time"]])

    return out_dir
