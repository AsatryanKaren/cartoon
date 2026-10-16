## The project
Repo: /home/user/cartoon. Code-generated 2D cartoons (Python + Pillow + numpy, 1280x720, 24 fps, flat cartoon style with dark outlines, 2x supersampled), Kokoro neural voices (installed, models in build/models), procedural music, synthesized sfx, burned-in subtitles. **Every episode must be exactly 5:55 (355 s)**; the pipeline guarantees it: spoken lines (`Say`) take their speech length, silent action moments (`Act`, weighted) stretch to fill the rest.

This is a NEW educational series, **"Whiskers & Luna's World"**, where children (ages 4–8) learn geography. READ FIRST: `world/SERIES.md` (series guide, the fixed 7-part episode format, the season list) and `CLAUDE.md`. Then `common.py` (format, Say/Act/Voice, shared CAST and SUBTITLE_COLORS, PLACE/TITLE output, hooks MUSIC/MOODS/MUSIC_CUES/EXTRA_SFX), `draw.py` (Canvas + characters: `cat()` poses stand/walk/sit/sleep/crouch/leap/swim, eyes open/closed/happy/wide, mouth, wet, squash; `mouse()` = Pip; moon, tree, cloud, zzz...; palettes WHISKERS, LUNA), `audio.py` (MOODS format; sfx meow, splash, clink, whoosh, ribbit, purr; helpers tone/band/env_adsr/place/SR). Reference implementations: `films/moonfish/` (base patterns: event ids, `tl.t(id, frac)`, `tl.prog`, `actor`, `smooth`, cached backgrounds, camera pan/tilt, CONTINUOUS, EXTRA_CUTS) and travel films in `films/` (rome, paris, montblanc, london, barcelona…: props.py, sounds.py, subtitle dark band, new characters). You may IMPORT read-only from any of them.

## Characters (same as the travel films)
Whiskers (lazy orange tabby, food and naps, big heart, "on purpose" running joke), Luna (curious grey cat, blue collar + bell — the explorer; in this series she owns the old globe), Pip (brave mouse, red scarf), narrator. Their voices are fixed in `common.CAST` — never change them. Each episode adds 1–2 animal guides with new Kokoro voices (extend CAST and SUBTITLE_COLORS in story.py, e.g. `CAST = {**CAST, "tula": Voice("bf_alice", 0.95, 0, ["Alex"], 170, "en-gb+f2", 45, 150)}`). Never use bm_george, am_michael, af_heart, af_sky for guides. Voices: af_alloy af_aoede af_bella af_jessica af_kore af_nicole af_nova af_river af_sarah am_adam am_echo am_eric am_fenrir am_liam am_onyx am_puck am_santa bf_alice bf_emma bf_isabella bf_lily bm_daniel bm_fable bm_lewis (3rd Voice field = pitch semitones).

## Teaching quality (most important)
- Facts must be CORRECT and simple. Teach exactly 3 key facts per episode through the story (shown, not lectured), then show them on the "Remember!" card, then the quiz (narrator asks, ~3 s pause shown by a countdown or ticking, then reveals the answer). Use on-screen labels and simple diagrams (arrows, maps, cut-aways) where they help.
- Still funny and warm: Whiskers' mistake must be a real laugh that also demonstrates a fact.
- Speech about 140–160 s total (`python3 timeline.py --film world/<episode>` prints speech vs action; ≈2.6 words/s). Give visual teaching moments (map flights, diagrams, the Remember card, quiz pauses) enough Act weight.

## Files and naming
- Episode folder: `world/s1eNN_<slug>/` with `__init__.py`, `story.py`, `scenes.py` (+ `props.py`, `sounds.py` if needed). story.py: `from common import *`, `TITLE = "NN - <Topic>"` (e.g. "01 - Our Planet"), `PLACE = "World/Season 1"`, SCENES, SCRIPT. The on-screen title card should read "Whiskers & Luna's World" + episode number and topic.
- Render: `python3 render.py --film world/s1eNN_<slug> ...`; output goes to `/root/Desktop/catcute/World/Season 1/NN - <Topic>.mp4`.
- Create/edit ONLY your own episode folder (and `world/kit.py` only if you are told you own it). Do NOT modify shared engine files (`common.py`, `draw.py`, `audio.py`, `timeline.py`, `render.py`, `film.py`), README, FILMS.md, CLAUDE.md, world/SERIES.md, catcute/, films/, or other episodes. If a shared change is truly needed, describe it in your report.
- No git commands except `git status`/`git diff`. Do not install packages. Several other agents work in this checkout at the same time.

## Quality loop
1. `python3 timeline.py --film world/<episode>` until timing is good.
2. `python3 render.py --film world/<episode> --stills 24` → `out/world_<episode>_contact_sheet.png`; LOOK at it with the Read tool; check moments with `--still <seconds>`. Fix layout problems, unreadable labels/subtitles (dark band behind subtitles on bright scenes), wrong facing, empty frames. Cache static layers (aim < 0.3 s/frame). Iterate several times.
3. Final: `python3 render.py --film world/<episode> --jobs 1` (only 4 cores shared with other renders; may take 40–70 min; run in background with its log in /tmp/render_<episode>.log, and wait, don't give up). Must end with `duration=355.000000s`.

## Final report (compact)
Title, output .mp4 path, synopsis, the 3 facts + quiz questions, scene list, guides + voices, files created, the `[done]` render line.

## The series kit (already built — use it, do NOT edit it)
`world/kit.py` (by Episode 1) sets the look of the whole series. Read `world/KIT.md` (quick reference) and the docstring at the top of `world/kit.py`, and study Episode 1 `world/s1e01_our_planet/` (story.py + scenes.py) as THE reference episode — copy its patterns: title card, home on the windowsill with Luna's globe, the flying nap cushion as the way of travelling, the magic map camera with dotted path, insets, Remember card, quiz with 3-2-1 ticks + chime, end card with "Next time: <next topic>". Episodes must look like one series. `world/kit.py` is read-only for you: if you find a kit bug, work around it in your own folder and describe it in your report.
Episode 1's 3 facts were: the Earth is round like a ball; almost three quarters of the Earth is water; maps show North, South, East, West. Its guide was Grandpa Shelby the turtle (bm_lewis). Don't repeat those facts as the main facts (a quick callback is fine).
IMPORTANT: Episode 1's first final render crashed on frames the stills hadn't sampled. Before the final render, smoke-test EVERY scene: e.g. render each scene's start/middle/end with `--still`, or run `python3 render.py --film world/<episode> --from <a> --to <a+1>` for a 1-second slice of each scene.


Scratch files: keep helper scripts/logs in your own scratch subfolder (e.g. <scratch>/<your-film>/), never shared with other agents.
