# Notes for Claude

- `FILMS.md` is the film checklist. Read it before making a new film: never remake a film marked `[x]`.
  After a new film is rendered, tick it in `FILMS.md` (title, `films/<name>`, `catcute/<Place>/`).
- Each film lives in `films/<name>/` (`story.py` with `TITLE` and `PLACE`, `scenes.py`). Shared engine
  files are in the repo root; voices of narrator, Whiskers, Luna and Pip in `common.CAST` never change.
- Every film must be exactly 355 s (5:55). `python3 render.py --film <name>` saves to
  `~/Desktop/catcute/<PLACE>/<TITLE>.mp4`.
- Finished videos are also committed to `catcute/<PLACE>/<TITLE>.mp4` (+ `.srt`) so they are saved on GitHub.
- Second series: **Whiskers & Luna's World** (geography, educational) in `world/`. Its guide, format and
  episode checklist are in `world/SERIES.md`: read it first, never remake a ticked episode, tick each finished one.
  Episodes render with `--film world/s1eNN_slug`; videos go to `catcute/World/Season N/`.
