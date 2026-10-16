# Workflows: how everything here was made (and how to continue)

Everything is code. A new session (or person) can continue any of these from this file.
Checklists of what is already done: `FILMS.md` (travel films), `world/SERIES.md` (geography series),
the table at the bottom of this file (interactive stories). Never remake something already ticked.

## 0. Set up a machine

```
git clone https://github.com/asatryankaren/cartoon && cd cartoon
pip install -r requirements.txt          # Pillow, numpy, kokoro-onnx, soundfile
# Kokoro voice models (once): build/models/kokoro-v1.0.onnx and voices-v1.0.bin
#   from https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)
# ffmpeg must be installed (brew install ffmpeg / apt install ffmpeg)
```
Videos are written to `~/Desktop/catcute/<PLACE>/<TITLE>.mp4` (+ `.srt`); set `CATCUTE_DIR` to change that.
For the Armenian voice see section 4.

## 1. A travel film (5:55, `films/<name>/`)

1. Read `FILMS.md` and pick an idea that is not ticked.
2. Write `films/<name>/story.py` (`TITLE`, `PLACE`, `SCENES`, `SCRIPT` of `Say`/`Act`) and `scenes.py`.
   `python3 timeline.py --film <name>` shows speech vs action time (speech about 140-160 s).
3. Look at it: `python3 render.py --film <name> --stills 24` (contact sheet in `out/`), `--still <s>`.
4. Final: `python3 render.py --film <name>`. Must end with `duration=355.000000s`.
5. Publish: `tools/publish_film.sh <name> <PLACE>` copies the video to `catcute/<PLACE>/` (re-encodes copies
   over 90 MB for GitHub's 100 MB limit), ticks `FILMS.md`, commits and pushes.

**Many at once with agents:** give each agent `tools/prompts/travel_film_agent.md` plus one line:
"Your film: folder `films/<name>/`, PLACE `<Place>`, idea: <one sentence>". Agents only touch their own
folder; you run `publish_film.sh` when each finishes. About 4 renders at a time on a 4-core machine.

## 2. A geography episode ("Whiskers & Luna's World", `world/s<S>e<NN>_<slug>/`)

Same as a film, but read `world/SERIES.md` (fixed 7-part format) and `world/KIT.md` first; episodes import
`world/kit.py` for the shared look. Render with `--film world/s1e05_rivers`. Agent prompt:
`tools/prompts/world_episode_agent.md` + "Your episode: NN - <Topic>, folder ..., guide: ...".
Publish: `tools/publish_world.sh <episode_dir> <NN>` (copies to `catcute/World/Season N/`, ticks SERIES.md).
Season 2 ideas are at the bottom of `world/SERIES.md`.

## 3. An interactive voice story (the React app in `app/`)

A story is short clips plus a graph: clip → question → (child answers by voice) → branch clip → …
- Clip contract and the 13-clip pattern: `interactive/pond_or_tree/SPEC.md`. Each clip is a tiny film
  (`interactive/<story>/clips/<id>/story.py` with `FILM_SECONDS` of any length and `EDGE_FADES = False`).
- `interactive/<story>/story.json`: the graph and the answer keywords (format: `app/README.md`).
- Render all clips and copy them into the app: `tools/interactive/render_story.sh <story>`.
  The silent listening loops get a soft looping pad (`tools/interactive/listen_pad.py`).
- Add the story to `app/public/stories/index.json`. The mp4s in `app/public/stories/` ARE committed
  (`.gitignore` has an exception), otherwise the app shows a black screen.
- Test: `cd app && npm test && npm run build`, `npx vite --port 5173`, then
  `node tools/interactive/test_app_flow.mjs "<card title>"` (read its header: the test browser needs VP9 copies).
- Run on the Mac: `cd app && git pull && npm run dev`, open http://localhost:5173 in Chrome.

## 4. A story in another language (example: Armenian, `interactive/pond_or_tree_hy/`)

The English story stays untouched; the translation reuses its pictures and timing.
1. Translate every line; let a native speaker approve the text BEFORE recording.
2. `interactive/<story>_<lang>/lines.py`: lines by event id + on-screen words (`draw.TEXTS`, e.g. The End).
   Each clip's `story.py` imports the English clip, sets `LANG`, `PLACE`, and swaps the lines; `scenes.py`
   imports the English scenes. `FILM_SECONDS` = English length + the extra time the new speech takes.
3. Voice (Armenian): `armenian_tts.py`, Pocket TTS Eastern Armenian (huggingface.co/mnjoyan/pocket-tts-armenian),
   which copies each character's English voice. Needs `pip install pocket-tts sentencepiece transformers`
   and huggingface.co allowed (in a cloud session: Allowed domains `huggingface.co`, `*.huggingface.co`, `*.hf.co`).
   (Meta MMS has only WESTERN Armenian, `mms-tts-hyw`: not right for Eastern Armenian text.)
   For a new language: add a backend like `armenian_tts.py` and a branch in `timeline.speak`.
4. Check the voice: `python3 tools/voice_check/check_voices.py interactive/<story>` records every line,
   reads it back with Whisper, re-records weak takes, and writes `out/<story>_all_lines.mp3` to listen to.
5. Armenian text uses an Armenian font automatically (`draw.ARMENIAN_FONTS`); make a cover with Armenian title.
6. App: `"lang": "hy-AM"` in story.json (Chrome's speech recognition), keywords with `*` stems
   (`"ծառ*"` matches ծառը, ծառի), player words in `app/src/i18n.ts`, card `"language"` in index.json.
7. Render with `LISTEN_FROM=<english story> tools/interactive/render_story.sh <story>_<lang>`
   (copies the wordless listening loops from the English story).

## 5. YouTube

`YOUTUBE.md` has the titles, descriptions, tags and playlists used so far; channel art is in `branding/`
(`python3 branding/make_channel_art.py`). For new videos, write their texts in the same style there.

## Rules that never change

- Voices of narrator, Whiskers, Luna and Pip (`common.CAST`) never change.
- Films and episodes are exactly 355 s. Interactive clips are any whole number of seconds.
- Agree on a plan with the owner before building something new; show translations before recording.
- Never break the existing stories: new things go in new folders; shared engine changes must keep old output.

## Interactive stories

| Story | Folder | Language | Status |
|---|---|---|---|
| Whiskers and the Lost Ball | `interactive/pond_or_tree/` | English | [x] done, in the app |
| Վիսկերսը և կորած գնդակը | `interactive/pond_or_tree_hy/` | Armenian (hy-AM) | [x] done, in the app |
