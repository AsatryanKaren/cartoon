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

### Voices (natural, free): Kokoro

The film uses [Kokoro](https://github.com/thewh1teagle/kokoro-onnx), a free neural voice model
that runs offline on your Mac (a few seconds per line). Install it once:

```bash
pip install kokoro-onnx soundfile
mkdir -p build/models && cd build/models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ../..
```

| Character | Kokoro voice | Speed | Pitch |
|-----------|--------------|-------|-------|
| Narrator  | `bm_george` (British man) | 0.95 | 0 |
| Whiskers  | `am_michael` (American man) | 0.92 | 0 |
| Luna      | `af_heart` (American woman) | 1.05 | 0 |
| Pip       | `af_sky`, pitched up | 1.1 | +4 semitones (small mouse) |

To change a voice, edit `CAST` in `story.py` and re-render; only changed lines are regenerated.
Other voices: `af_bella`, `af_nicole`, `af_sky`, `am_michael`, `am_fenrir`, `am_echo`,
`bm_fable`, `bm_lewis`, `bf_emma` and more (names starting with `b` are British).

If Kokoro is not installed, the pipeline falls back to the macOS `say` voices
(Daniel, Eddy, Flo, Junior; `--premium` picks Premium/Enhanced when installed), and then to
`espeak-ng` (robotic). Force one with `--tts kokoro|say|espeak`.

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

- **Even better voices:** ElevenLabs (paid), added as another backend in `timeline.speak`.
- **3D version:** Blender (free) driven by Python scripts, low-poly cute style, about
  30-90 minutes per render. It can reuse `story.py` and `timeline.py` unchanged.
