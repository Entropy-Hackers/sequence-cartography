import json
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer

import pytest

from seqcarto.pipeline import analyze
from seqcarto.server import Handler


@pytest.fixture(scope="module")
def server(video, tmp_path_factory):
    root = tmp_path_factory.mktemp("out")
    analyze(str(video), root, show_progress=False)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, root=root.resolve()))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def get(url, headers=None):
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}))


def test_index_and_api(server):
    assert b"Sequence Cartography" in get(server + "/").read()
    videos = json.loads(get(server + "/api/videos").read())
    assert len(videos) == 1 and videos[0]["slug"] == "shots" and videos[0]["scenes"] == 3
    assert videos[0]["video"] is None  # .avi is not browser-playable
    manifest = json.loads(get(server + "/data/shots/manifest.json").read())
    img = get(server + "/data/shots/" + manifest["scenes"][0]["omimage"])
    assert img.headers["Content-Type"] == "image/jpeg"


def test_range_request(server, video):
    # the source is served even if the browser cannot play it
    r = get(server + "/video/shots", {"Range": "bytes=10-19"})
    assert r.status == 206
    assert r.read() == video.read_bytes()[10:20]


def test_no_path_traversal(server):
    with pytest.raises(urllib.error.HTTPError) as e:
        get(server + "/data/%2e%2e/%2e%2e/etc/hosts")
    assert e.value.code == 404
