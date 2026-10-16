# «Վիսկերսը և կորած գնդակը»: Armenian version of "Whiskers and the Lost Ball"

The same interactive story as `../pond_or_tree/` (which is not changed), spoken in Eastern Armenian.

- `lines.py`: every Armenian line, by the English event id, plus the on-screen words (Վերջ, ՊԻՊ).
- `clips/<id>/`: each clip imports the English clip's pictures and timing and swaps in the Armenian lines
  (`LANG = "hy"`). Clips are a few seconds longer than the English ones because Armenian takes longer to say.
  The two silent listening loops are the English files (no words in them).
- `story.json`: the story graph for the app, `lang: "hy-AM"`, keywords with `*` stems (ծառ* matches ծառի, ծառը).
- Voice: `armenian_tts.py` (repo root), Pocket TTS Eastern Armenian (mnjoyan/pocket-tts-armenian, CC-BY-4.0).
  It clones each character's usual English voice, so Whiskers, Luna, Pip and the narrator keep their voices.
  Needs `pip install pocket-tts sentencepiece` and huggingface.co allowed; the model downloads by itself.

Render one clip: `python3 render.py --film interactive/pond_or_tree_hy/clips/intro`
(output: `~/Desktop/catcute/Interactive/pond_or_tree_hy/intro.mp4`), then copy the mp4s to
`app/public/stories/pond_or_tree_hy/`.

Every line was read back with Whisper (openai/whisper-large-v3-turbo) and weak takes were re-recorded.
