"""Command line interface: ``seqcarto analyze <file|url>``."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from . import __version__
from .detect import DEFAULT_MIN_SCENE_LEN, DEFAULT_THRESHOLD


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="seqcarto", description="Sequence Cartography")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="detect scenes and render OM images")
    a.add_argument("input", help="video file or online video URL")
    a.add_argument("-o", "--output", type=Path, default=Path("output"),
                   help="output root directory (default: ./output)")
    a.add_argument("-t", "--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help=f"ContentDetector threshold (default: {DEFAULT_THRESHOLD})")
    a.add_argument("-m", "--min-scene-len", type=int, default=DEFAULT_MIN_SCENE_LEN,
                   help=f"minimum scene length in frames (default: {DEFAULT_MIN_SCENE_LEN})")
    a.add_argument("--end", type=float, metavar="SECONDS",
                   help="only analyze the first SECONDS of the video")
    a.add_argument("-q", "--quiet", action="store_true", help="no progress bars")

    v = sub.add_parser("view", help="browse results in the web viewer")
    v.add_argument("-o", "--output", type=Path, default=Path("output"),
                   help="output root directory (default: ./output)")
    v.add_argument("-p", "--port", type=int, default=8765, help="port (default: 8765)")
    v.add_argument("--no-browser", action="store_true", help="do not open a browser")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    if args.command == "analyze":
        from .pipeline import analyze

        out = analyze(
            args.input, args.output, args.threshold, args.min_scene_len,
            args.end, show_progress=not args.quiet,
        )
        print(out / "manifest.json")
    elif args.command == "view":
        from .server import serve

        serve(args.output, port=args.port, open_browser=not args.no_browser)
    return 0
