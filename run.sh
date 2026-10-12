#!/bin/zsh
# Usage: ./run.sh            -> render the full film
#        ./run.sh --preview 10 42.5   -> save preview PNGs at those times
cd "$(dirname "$0")"
export PATH="$PWD/.venv/bin:$PATH"
exec python render.py "$@"
