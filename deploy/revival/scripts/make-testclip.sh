#!/bin/sh
# Reproducible 24 s test clip with three hard cuts (frames 150, 300, 450 at 25 fps).
# Usage: deploy/revival/scripts/make-testclip.sh [output dir, default data/movies]
set -e
out=${1:-data/movies}
mkdir -p "$out"
docker run --rm --user "$(id -u):$(id -g)" -v "$(cd "$out" && pwd)":/m --entrypoint ffmpeg \
  sequence-cartography-bibbox-video-score-server -loglevel error \
  -f lavfi -i testsrc2=size=640x360:rate=25:duration=6 \
  -f lavfi -i smptebars=size=640x360:rate=25:duration=6 \
  -f lavfi -i mandelbrot=size=640x360:rate=25 \
  -f lavfi -i rgbtestsrc=size=640x360:rate=25:duration=6 \
  -filter_complex "[2]trim=duration=6,setpts=PTS-STARTPTS[m];[0][1][m][3]concat=n=4:v=1:a=0,format=yuv420p" \
  -c:v libx264 -y /m/testclip.mp4
echo "$out/testclip.mp4"
