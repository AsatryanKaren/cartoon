#!/bin/bash
# usage: tools/publish_film.sh <name> <PLACE>
set -e
cd "$(dirname "$0")/.."
BRANCH=$(git rev-parse --abbrev-ref HEAD)
LIB="${CATCUTE_DIR:-$HOME/Desktop/catcute}"
name=$1; place=$2
title=$(python3 -c "import film; film.load('$name'); print(film.TITLE)")
src="$LIB/$place/$title.mp4"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src")
echo "duration $dur"
python3 -c "import sys; d=float('$dur'); sys.exit(0 if abs(d-355)<0.05 else 1)"
mkdir -p "catcute/$place"
size=$(stat -c %s "$src")
if [ "$size" -gt 90000000 ]; then
  echo "large ($size bytes): re-encoding repo copy"
  ffmpeg -v error -y -i "$src" -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -c:a copy -movflags +faststart "catcute/$place/$title.mp4"
else
  cp "$src" "catcute/$place/"
fi
cp "$LIB/$place/$title.srt" "catcute/$place/"
python3 - "$name" "$place" "$title" <<'PY'
import sys, re
name, place, title = sys.argv[1:]
s = open('FILMS.md').read()
lines = s.split('\n')
# remove idea line for this place
lines = [l for l in lines if not (l.startswith('- [ ] **') and l[8:].lower().startswith(place.lower()))]
entry = f"- [x] **{place}**: *{title}* (`films/{name}`, `catcute/{place}/`)"
i = lines.index('## Ideas (not made yet)')
# insert at end of Done block (before blank line preceding Ideas)
j = i - 1
while lines[j] == '':
    j -= 1
lines.insert(j + 1, entry)
open('FILMS.md', 'w').write('\n'.join(lines))
PY
git add "films/$name" "catcute/$place" FILMS.md
git commit -qm "Film: $title ($place)"
for i in 1 2 3 4; do git push -q origin "$BRANCH" && break; sleep $((2**i)); done
git log --oneline | head -1
