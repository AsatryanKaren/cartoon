# world/kit.py: shared series kit (quick reference)

`from world import kit as K`. Screen is 1280x720. Full details are in the docstring at the top of `kit.py`.
Episode 1 (`world/s1e01_our_planet/`) is the reference episode: copy its `scenes.py` patterns.

## Characters

| Function | Purpose |
|---|---|
| `kat(c, tl, t, who, x, y, s, face, pose, **kw)` | Whiskers, Luna or Pip, with mouths that follow the speech |
| `cushion(c, x, y, s, t, fly)` | the flying nap cushion, the series' way to travel |
| `crew(c, tl, t, x, y, s, face, fly, who, eyes={}, look={}, extra={})` | the friends riding the cushion (`extra` sets per-character pose, dy or mouth) |
| `track`, `smooth`, `pop`, `ease_out` | keyframes and easing |

## Home (episode format parts 1 and 7)

| Function | Purpose |
|---|---|
| `home_bg("day" \| "evening" \| "night")` | cached room with big window and window seat; `.copy()` it before drawing |
| `SILL_Y`, `GLOBE_X`, `SPOT` | where the characters sit and where the globe stands |
| `old_globe(c, x, y, s, lon, glow, t)` | Luna's spinning, glowing globe on its stand |

## Earth and map

| Function | Purpose |
|---|---|
| `globe(c, x, y, r, lon, lat, style, roll, sun, glow)` | globe at any size; style `earth`, `continents` or `toy`; `sun=(lon, lat)` adds a night side |
| `globe_xy(...)` | screen position of a place on a globe |
| `globe_to_map(c, k, t, r, lon)` | globe flattens into the map as k goes 0 → 1 |
| `map_view(lon, lat, zoom, style, labels, t)` → `(canvas, MapView)` | zoomable, pannable world map in starry space |
| `MapView.xy(lon, lat)` | screen position of a place on the map |
| `lerp_view(a, b, k)` | camera move between two views |
| `draw_map`, `map_clip` | draw the map; `map_clip` hides anything past its edges |
| `map_labels(c, v, "continents" \| "oceans" \| "all" \| [names], k)`, `map_label` | names on the map |
| `map_highlight(c, v, "africa", k)` | glow over one continent |
| `map_path(c, v, waypoints, u)`, `path_point` | dotted travel path with an arrow, and the position of a moving icon on it |
| `you_are_here(c, x, y, t, k, text)` | bouncing pin with a label |
| `CONTINENT_LABELS`, `OCEAN_LABELS` | name positions |

## Cards

| Function | Purpose |
|---|---|
| `title_card(tl, t, t0, ep, topic)` | series title over a spinning Earth |
| `remember_card(t, facts, ks, icons, active)` | "Remember!" card, 3 rows sliding in |
| `quiz_card(t, question, choices, answer, ask, count, reveal, icons, number, answer_text)` | question, two picture choices, 3-2-1 countdown, green answer banner |
| `end_card(c, k, "Next time:", topic, t)` | closing ribbon |
| `icon_globe`, `icon_water`, `icon_compass`, `pie(...)` | ready-made icons |

## Helpers

| Function | Purpose |
|---|---|
| `text` | text that follows scaling |
| `label` | tag with an arrow |
| `arrow` | arrow |
| `compass(c, x, y, r, k, t, lit, words)` | compass rose |
| `inset(c, x, y, w, h, k, draw_fn)` | popup picture card |
| `bubble`, `sparkles`, `star`, `flash`, `zoom` | small effects |
| `sub_band(c, tl, t)` | dark band behind subtitles; use it on every bright scene |
| `space_bg()`, `twinkle()` | starry backdrop |

## Sound

- `MOODS = {**K.KIT_MOODS, ...}` adds the moods w_intro, w_home, w_wonder, w_map, w_sea, w_funny, w_remember, w_quiz and w_night.
- `EXTRA_SFX = {**K.KIT_SFX, ...}` adds the sounds spin, ding, tick, chime, sparkle and pop.
- **Quiz pattern:** `Act(..., id="q1_count", sfx=[("tick", 0), ("tick", .333), ("tick", .667)])`, weighted to about 3 s, then `Say(answer, sfx=[("chime", 0)])`.
