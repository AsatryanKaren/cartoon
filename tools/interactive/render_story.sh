#!/bin/bash
# Render every clip of an interactive story and copy it into the app.
# usage: tools/interactive/render_story.sh <story>            e.g. pond_or_tree  or  pond_or_tree_hy
#        tools/interactive/render_story.sh <story> intro pond  (only these clips)
# Clips without words (q*_listen) get the soft looping pad. A story whose clips folder has no
# q*_listen clip (a translation) copies them from the original story named by $LISTEN_FROM.
set -e
cd "$(dirname "$0")/../.."
story=$1; shift
LIB="${CATCUTE_DIR:-$HOME/Desktop/catcute}"
OUT="$LIB/Interactive/$story"
APP="app/public/stories/$story"
clips=${@:-$(ls interactive/$story/clips | grep -v __)}
mkdir -p "$OUT" "$APP"
for c in $clips; do
  python3 render.py --film interactive/$story/clips/$c 2>&1 | grep -E "done|Error|error|Duration|Traceback|Speech is"
  case $c in q*_listen) python3 tools/interactive/listen_pad.py "$OUT/$c.mp4" "build/pad.wav" ;; esac
done
if [ -n "$LISTEN_FROM" ]; then cp "$LIB/Interactive/$LISTEN_FROM"/q*_listen.mp4 "$OUT/"; fi
cp "$OUT"/*.mp4 "$APP/"
cp "interactive/$story/story.json" "$APP/"
[ -f "interactive/$story/cover.png" ] && cp "interactive/$story/cover.png" "$APP/"
for f in "$APP"/*.mp4; do echo "$(basename "$f") $(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")"; done
echo "Now add the story to app/public/stories/index.json (if new), test, commit."
