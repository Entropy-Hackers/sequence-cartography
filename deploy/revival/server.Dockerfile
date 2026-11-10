# Revival image for the Video Score server/celery containers.
# Replaces the from-source ffmpeg/OpenCV build of server/Dockerfile with
# Debian ffmpeg and OpenCV wheels; application code is unchanged.
FROM python:3.7-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    CELERY_BROKER_URL=redis://redis:6379/0 \
    CELERY_RESULT_BACKEND=redis://redis:6379/0 \
    C_FORCE_ROOT=true

RUN sed -i -e "s|deb.debian.org/debian-security|archive.debian.org/debian-security|g" -e "s|deb.debian.org/debian|archive.debian.org/debian|g" /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg postgresql-client build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/movieannotator
COPY deploy/revival/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server/entrypoint.sh server/*.py server/uwsgi.* ./
COPY server/uwsgi.ini /etc/uwsgi.ini
RUN chmod 755 entrypoint.sh && mkdir -p /data/movies

EXPOSE 5000
CMD ["./entrypoint.sh"]
