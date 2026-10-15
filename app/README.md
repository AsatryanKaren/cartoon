# Whiskers & Luna: interactive stories (prototype)

A React app where the cartoon stops at decision points, Whiskers asks the child a question out loud,
the app **listens to the spoken answer**, and the story continues on the chosen path.
No backend yet: stories and clips are static files in `public/stories/`.

## Run it on your Mac

```bash
cd cartoon/app
npm install        # first time only
npm run dev        # opens http://localhost:5173
```

Open the page in **Chrome** (or Safari / Edge), tap a story, and allow the microphone once.
Turn the volume up and answer out loud when Whiskers asks.

Testing shortcuts (keyboard, for grown-ups): `1` / `2` answer the question, `N` skips ahead,
`H` shows what the microphone heard.

## How it works

| Part | File | Role |
|---|---|---|
| Story data | `public/stories/<id>/story.json` + clips | The story graph: clips, questions, keywords, branches |
| Story engine | `src/engine/storyEngine.ts` | Pure state machine: clip → question → listen → re-ask → auto-choose → branch (unit-tested) |
| Speech | `src/speech/` | `SpeechRecognizer` interface; `WebSpeechRecognizer` uses the browser's speech recognition. Swap in an on-device recognizer later without touching the player |
| Player | `src/components/Player.tsx` | Preloads all clips, runs the engine, listens only during the silent "listening" loop (so it never hears the cartoon itself) |
| Video | `src/components/VideoStage.tsx` | Two stacked videos for seamless clip changes |
| Picker | `src/components/StoryPicker.tsx` | Lists stories from `public/stories/index.json` |

A question in `story.json`:

```json
"q1": { "type": "question", "listen": "q1_listen.mp4", "reask": "q1_reask.mp4", "auto": "q1_auto.mp4",
        "timeoutSec": 7, "maxReasks": 1, "default": "pond",
        "choices": [ { "id": "pond", "keywords": ["pond", "water", "fish"], "next": "pond" },
                     { "id": "tree", "keywords": ["tree", "climb", "up"],   "next": "tree" } ] }
```

If nobody answers within `timeoutSec`, Whiskers asks again (`reask`); after `maxReasks` he picks `default` himself (`auto`).

## Add a new story

1. Make the clips with the cartoon engine (see `interactive/pond_or_tree/` for the pattern).
2. Put the `.mp4` clips, `story.json` and `cover.png` in `public/stories/<new_id>/`.
3. Add the story to `public/stories/index.json`.

## Commands

`npm run dev`: develop · `npm test`: engine tests · `npm run build`: production build in `dist/` · `npm run lint`

## Notes

- Speech recognition: in Chrome the browser sends audio to Google's speech service; Safari uses Apple's.
  For a real children's product, replace `WebSpeechRecognizer` with on-device recognition (privacy laws for children).
- Any HTTPS static host (Vercel, Netlify, GitHub Pages) can serve `dist/`; the microphone works on HTTPS and on localhost only.
