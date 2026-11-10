"""Sequence Cartography: map a video into scenes and OM overview images."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("seqcarto")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"


def main() -> None:
    from .cli import main as _main

    raise SystemExit(_main())
