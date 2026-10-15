# Interactive story "Whiskers and the Lost Ball" (pond_or_tree): clip contract

The React app (`app/`) plays this story from `story.json`. Every clip is a separate short video
made by the cartoon engine. Clip ids and file names must match `story.json` exactly.

| Clip | What happens | Length |
|---|---|---|
| intro | Story starts at home/garden; the ball goes missing; ends with Whiskers turning to the viewer and asking **Q1: "Where should we look first: by the pond, or up in the big tree?"** | 40–60 s |
| q1_listen | **Seamless loop**: Whiskers looks at the viewer, ear raised, small idle motion; no speech; quiet music | exactly 4 s |
| q1_reask | Whiskers asks again, shorter: "Hmm? The pond… or the tree? Tell me!" | 4–7 s |
| q1_auto | Nobody answered: "Hmm… I'll choose! Let's try the pond!" | 4–6 s |
| pond | Branch: they search by the pond (frogs, splash…), find a clue, NOT the ball | 30–45 s |
| tree | Branch: they climb the big tree (bird nest, view…), find a clue, NOT the ball | 30–45 s |
| middle | Both branches lead here: clue leads to the ball; it gets far away; ends with **Q2: "How should we get it back home: by boat, or by balloon?"** | 25–40 s |
| q2_listen | Seamless loop, like q1_listen | exactly 4 s |
| q2_reask | "Boat… or balloon? You choose!" | 4–7 s |
| q2_auto | "Hmm… I'll choose! The boat!" | 4–6 s |
| boat | Branch: home by boat | 25–40 s |
| balloon | Branch: home by balloon | 25–40 s |
| ending | Both branches lead here: home on the windowsill, thank the viewer for helping ("You helped us choose!"), moral | 20–35 s |

Rules: clips join with hard cuts, so the start of each clip must make sense after the end of the
previous one (same place or a clear new scene). No fade to black at clip edges (`EDGE_FADES = False`).
A listen loop's last frame must flow into its first frame.
