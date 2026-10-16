#!/bin/bash
# usage: tools/publish_world.sh <episode_dir e.g. s1e01_our_planet> <NN>
set -e
cd "$(dirname "$0")/.."
BRANCH=$(git rev-parse --abbrev-ref HEAD)
LIB="${CATCUTE_DIR:-$HOME/Desktop/catcute}"
ep=$1; nn=$2
title=$(python3 -c "import film; film.load('world/$ep'); print(film.TITLE)")
place=$(python3 -c "import film; film.load('world/$ep'); print(film.PLACE)")
src="$LIB/$place/$title.mp4"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src"); echo "duration $dur"
python3 -c "import sys; sys.exit(0 if abs(float('$dur')-355)<0.05 else 1)"
mkdir -p "catcute/$place"
size=$(stat -c %s "$src")
if [ "$size" -gt 90000000 ]; then
  ffmpeg -v error -y -i "$src" -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -c:a copy -movflags +faststart "catcute/$place/$title.mp4"
else cp "$src" "catcute/$place/"; fi
cp "$LIB/$place/$title.srt" "catcute/$place/"
sed -i "s/^- \[ \] $nn - /- [x] $nn - /" world/SERIES.md
git add "world/$ep" world/kit.py world/SERIES.md "catcute/$place"
git commit -qm "Geography S1: $title"
for i in 1 2 3 4; do git push -q origin "$BRANCH" && break; sleep $((2**i)); done
git log --oneline | head -1
