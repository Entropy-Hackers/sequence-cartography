# Sequence Cartography

Mapping moving images: Sequence Cartography turns a video into a navigable map of its scenes.

For every detected scene it renders an **OM image**, a composite overview made of three bands:

1. **Keyframes**: one large frame roughly every 5 seconds
2. **Thumbnails**: five small frames per keyframe
3. **Slit-scan stripe**: the centre pixel column of every frame, laid out over time

Sources can be local video files or online videos.

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run seqcarto analyze path/to/video.mp4          # local file
uv run seqcarto analyze https://youtu.be/<id>      # online video (downloaded via yt-dlp)
uv run seqcarto analyze video.mp4 --end 180        # only the first 3 minutes
```

Options: `-o/--output` (default `./output`), `-t/--threshold` (default 35), `-m/--min-scene-len` in frames (default 25), `-q/--quiet`.

## Viewer

```bash
uv run seqcarto view            # opens http://127.0.0.1:8765/
```

The viewer lists every analyzed video in `./output`. For each one it shows the video player, a slit-scan timeline of the whole video with scene cuts, and all OM images. Clicking the timeline or an OM image jumps the video to that moment; ↑/↓ steps through scenes. Playback in the browser needs an MP4/WebM source; other formats such as AVI still show all images.

## Output

```
output/<video>/
  manifest.json        source info, parameters, scenes with timecodes and frame indices
  scenes.csv           index, start_frame, end_frame, start_time, end_time
  omimages/scene_00000.jpg …
  stripes/stripe_00000.jpg …   slit-scan of the whole video, 1500 frames per tile
```

The video is read twice, both times sequentially: once for scene detection (PySceneDetect `ContentDetector`) and once to render all OM images. Frames are never sought.

## Development

```bash
uv run pytest
```

## History

The original 2018/19 prototype is kept for reference in [`legacy/`](legacy/).

## License

TBD
