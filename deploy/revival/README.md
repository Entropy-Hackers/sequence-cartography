# Revival: historic Video Score stack (milestone M0)

Runs the unchanged Video Score application (Angular 9 client, Flask 1.0, Celery, PostgreSQL 9.6) in containers.

```bash
export HOST_UID=$(id -u) HOST_GID=$(id -g)     # the worker writes into ./data as you
docker compose -f docker-compose.yml -f deploy/revival/docker-compose.revival.yml up -d --build
deploy/revival/scripts/make-testclip.sh          # 24 s clip with cuts at frames 150/300/450, or copy own videos into data/movies/
```

- App: http://127.0.0.1:8077 · Adminer: http://127.0.0.1:8078 (postgres/postgres, DB `users_dev`) · Flower: http://127.0.0.1:8079
- The DB is recreated and seeded on every new server container (`entrypoint.sh`). Seeded films reference files that are not in the repo.
- Register a local file: insert a row into `movies` with `source='FILESYSTEM'` and `uri='<file name in data/movies>'`, then call `/api/movie/<id>/setparams` and POST `{"command": "[MOVIE] MAKE STRIPES" | "[MOVIE] ANALYZE CUTS" | "[MOVIE] MAKE DOC AND IMAGES"}` to `/api/movie/<id>/command`. The document is shown at `/document/<id>`.

Changes compared with upstream, all needed to run it in 2026:

| What | Why |
|---|---|
| `server.Dockerfile`: Python 3.7 (Debian 11 from archive.debian.org), Debian ffmpeg, OpenCV wheels | upstream image compiles ffmpeg/OpenCV from source and mixes Python 2 packages with 2018 pins, it no longer builds |
| `requirements.txt`: Celery 4.3, redis 3.2, flower 0.9.3, psycopg2-binary, transitive pins | Celery 4.2.1 does not import on Python 3.7 (`async` keyword) |
| Flower command | upstream `-celery A ...` is not parseable |
| `server/app/scenedetect/detectors/content_detector.py`: `list(cv2.split(...))` | OpenCV 4 returns a tuple |

YouTube sources do not work (pafy/youtube-dl are dead).

Verified on 2026-11-10 (macOS arm64, Docker 20.10): a 10-minute clip at 60 fps ran through stripes, 141 cuts, the document and 240 sub-OM images, and the document renders in the client.

Verified on 2026-11-10 on tsv100 (Ubuntu 22.04, x86_64, Docker 29) with `make-testclip.sh`: cuts found exactly at 150/300/450, four document sections with eight sub-OM images.

Known upstream behaviour (kept as is): videos shorter than 1500 frames get no stripe tile; re-running "MAKE DOC AND IMAGES" creates another document.
