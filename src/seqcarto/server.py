"""Local viewer: serves the web UI, analysis results and source videos.

Routes::

    /                    viewer (static index.html)
    /api/videos          list of analyzed videos (one per manifest.json)
    /data/<path>         files below the output root (manifests, images)
    /video/<slug>        the source video of an analysis, with HTTP Range support
"""

from __future__ import annotations

import json
import mimetypes
import re
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Containers browsers can usually play directly.
PLAYABLE = {".mp4", ".m4v", ".webm", ".mov", ".ogv"}
CHUNK = 1 << 16


def list_videos(root: Path) -> list[dict]:
    videos = []
    for manifest_path in sorted(root.glob("*/manifest.json")):
        try:
            m = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        slug = manifest_path.parent.name
        src = m.get("source", {})
        video = _video_path(root, slug)
        scenes = m.get("scenes", [])
        fps = src.get("fps") or 0
        videos.append({
            "slug": slug,
            "title": src.get("title", slug),
            "url": src.get("url"),
            "scenes": len(scenes),
            "duration_seconds": round(src.get("frames", 0) / fps, 3) if fps else None,
            "created": m.get("created"),
            "video": f"/video/{slug}" if video and video.suffix.lower() in PLAYABLE else None,
            "video_note": None if video else "source video not found",
        })
    return videos


def _video_path(root: Path, slug: str) -> Path | None:
    manifest_path = root / slug / "manifest.json"
    try:
        src = json.loads(manifest_path.read_text()).get("source", {})
    except (OSError, json.JSONDecodeError):
        return None
    for candidate in (src.get("path"), root / "_downloads" / src.get("file", "")):
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "seqcarto"

    def __init__(self, *args, root: Path, **kwargs):
        self.root = root
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):  # quiet
        pass

    def do_GET(self):  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        if path in ("/", "/index.html"):
            body = files("seqcarto").joinpath("viewer/index.html").read_bytes()
            return self._send_bytes(body, "text/html; charset=utf-8")
        if path == "/api/videos":
            body = json.dumps(list_videos(self.root)).encode()
            return self._send_bytes(body, "application/json")
        if path.startswith("/data/"):
            target = (self.root / path[len("/data/"):]).resolve()
            if not target.is_relative_to(self.root) or not target.is_file():
                return self.send_error(HTTPStatus.NOT_FOUND)
            return self._send_file(target, cache=target.suffix != ".json")
        if m := re.fullmatch(r"/video/([^/]+)", path):
            video = _video_path(self.root, m.group(1))
            if video is None:
                return self.send_error(HTTPStatus.NOT_FOUND)
            return self._send_file(video)
        self.send_error(HTTPStatus.NOT_FOUND)

    def _send_bytes(self, body: bytes, ctype: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, cache: bool = False) -> None:
        size = path.stat().st_size
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        start, end = 0, size - 1
        status = HTTPStatus.OK
        if rng := re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "")):
            a, b = rng.groups()
            if a:
                start = int(a)
                end = min(int(b), size - 1) if b else size - 1
            elif b:  # suffix range: last N bytes
                start = max(0, size - int(b))
            if start > end or start >= size:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            status = HTTPStatus.PARTIAL_CONTENT
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-store")
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(CHUNK, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # browser cancelled (normal while seeking)


def serve(root: Path, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    root = root.resolve()
    httpd = ThreadingHTTPServer((host, port), partial(Handler, root=root))
    url = f"http://{host}:{httpd.server_address[1]}/"
    print(f"Sequence Cartography viewer: {url}  (results: {root})  Ctrl+C to stop")
    if open_browser:
        import webbrowser

        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
