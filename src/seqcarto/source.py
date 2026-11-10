"""Resolve an input (local file or online video URL) to a local video file."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

# Prefer H.264 video-only streams: OpenCV decodes them everywhere and no
# ffmpeg merge step is needed. Analysis does not need more than 720p.
YTDLP_FORMAT = (
    "bv*[height<=720][vcodec^=avc1]/bv*[height<=720]/b[height<=720]/bv*/b"
)


@dataclass
class Source:
    path: Path
    slug: str
    title: str
    url: str | None = None


def is_url(value: str) -> bool:
    return bool(_URL_RE.match(value))


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return slug or "video"


def resolve(value: str, cache_dir: Path) -> Source:
    """Return a local video for ``value``, downloading it first if it is a URL."""
    if is_url(value):
        return _download(value, cache_dir)
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"video not found: {path}")
    return Source(path=path, slug=slugify(path.stem), title=path.stem)


def _download(url: str, cache_dir: Path) -> Source:
    import yt_dlp

    cache_dir.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": YTDLP_FORMAT,
        "outtmpl": str(cache_dir / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
    return Source(
        path=path,
        slug=slugify(info["id"]),
        title=info.get("title") or info["id"],
        url=info.get("webpage_url") or url,
    )
