# Cat Cartoons

Code-generated 2D cartoons about cats: drawn frame by frame in Python, with voices,
music, sound effects and subtitles. Every film is exactly **5:55 (355 s)**, 1280x720, 24 fps.

**Film 1: Whiskers and the Moon Fish.** Whiskers (a lazy orange tabby) and Luna (a curious
grey cat) go looking for the legendary glowing Moon Fish, meet Pip the brave mouse, and find
out the "fish" is the moon's reflection. *The best thing you find is who you find along the way.*

## Setup on a Mac

```bash
brew install ffmpeg python
cd cartoon
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 render.py            # -> out/film.mp4 + out/film.srt
```

Voices come from the built-in `say` command. Install the voices once under
**System Settings → Accessibility → Spoken Content → System Voice → Manage Voices**:

| Character | Voice |
|-----------|-------|
| Narrator  | Daniel (English UK) |
| Whiskers  | Eddy (English (US)) |
| Luna      | Flo (English (US)) |
| Pip       | Junior |

`python3 timeline.py --list-voices` shows what is installed. To use free higher-quality
voices, download "Daniel (Premium)" or "Daniel (Enhanced)" in the same panel and render with
`--premium`. Characters keep the same voices in every film (see `CAST` in `story.py`).

On Linux (or a Mac without `say`) the pipeline falls back to `espeak-ng`, which is
robotic but keeps everything working.

## Useful commands

```bash
python3 render.py --stills 24            # contact sheet of 24 frames -> out/contact_sheet.png
python3 render.py --still 130            # one frame at 130 s
python3 render.py --from 95 --to 160     # render only part of the film
python3 timeline.py                      # generate speech, print scene timings
```

## How it works

| File | Role |
|------|------|
| `story.py` | Script, cast and voices. Spoken lines (`Say`) and weighted silent action moments (`Act`), each with optional id and sound effects. |
| `timeline.py` | Generates speech (cached in `build/voices`), then stretches the action moments by weight so the total is exactly 355 s. Mouth tracks from speech volume; `.srt` export. |
| `draw.py` | Canvas (2x supersampled), cats, Pip, frogs, butterfly, moon, trees, Moon Fish reflection, subtitles. |
| `scenes.py` | One function per scene: title, morning, legend, garden, meadow, pond, realize, home. Animation is keyed to script event ids, so it stays in sync whatever the speech length. |
| `audio.py` | Procedural music per scene mood, ducked under speech; synthesised meow, splash, clink, whoosh, ribbit and purr; final mix. |
| `render.py` | Renders frame chunks in parallel straight into ffmpeg, joins them, muxes audio and checks the length is exactly 355 s. |

To make a new film, write a new script in `story.py` (or copy it) and add scene functions.
The timing rule takes care of the exact 5:55 length.

## Next steps

- **Better voices:** free Premium/Enhanced macOS voices (`--premium`), or ElevenLabs (paid),
  added as another backend in `timeline.speak`.
- **3D version:** Blender (free) driven by Python scripts, low-poly cute style, about
  30-90 minutes per render. It can reuse `story.py` and `timeline.py` unchanged.
