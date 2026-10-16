# Interactive story "Pip's Birthday Surprise" (birthday): clip contract

The React app (`app/`) plays this story from `story.json`. Every clip is a separate short video
made by the cartoon engine (`python3 render.py --film interactive/birthday/clips/<id>`).
Clip ids and file names must match `story.json` exactly. Shared drawings, music and sounds: `shared.py`
(the question close-up itself comes from `interactive/pond_or_tree/shared.py`).

| Clip | What happens | Length |
|---|---|---|
| intro | The cats' room: Luna wakes Whiskers on the windowsill, it's Pip's birthday, a cake needs something sweet; close-up **Q1: "What shall we put in the cake: apples, or honey?"** (apple tree left, beehive right) | 40 s |
| q1_listen | **Seamless loop**: Whiskers listening, ear up; no speech; soft pad | exactly 4 s |
| q1_reask | "Hmm? Apples... or honey? Tell me!" | 5 s |
| q1_auto | "Hmm... I'll choose! Apples!" | 5 s |
| apple | Branch: Whiskers shakes the apple tree, an apple bonks his head; Hedgie the hedgehog rolls through the apples and they stick to his spines | 40 s |
| honey | Branch: the flowery meadow; Buzzy the bee asks for help watering the flowers; Whiskers waters them and himself; a pot of honey | 40 s |
| kitchen | Both branches lead here: flour, eggs, milk; Whiskers tastes the batter; oven, ding, the cake (pink icing, no apples/honey shown); close-up **Q2: "How shall we decorate: with balloons, or with flowers?"** (party room: balloons left, vase right) | 32 s |
| q2_listen | Seamless loop, like q1_listen (party-room backdrop) | exactly 4 s |
| q2_reask | "Balloons... or flowers? You choose!" | 5 s |
| q2_auto | "Hmm... I'll choose! Balloons!" | 5 s |
| balloons | Branch: blowing up balloons; Whiskers' giant balloon lifts him, pop, he lands on a cushion | 31 s |
| flowers | Branch: picking flowers in the garden, the vase; Whiskers sneezes the petals all over the room | 30 s |
| ending | Both branches lead here (neutral decorations: banner, two balloons, a small vase): Pip arrives, surprise, cake with a candle, close-up thanks to the viewer, moral, "Finally!", The End | 26 s |

New characters (voices set in the clip's story.py): `hedgie` (apple) `am_echo`, `buzzy` (honey) `af_nova`.

On-screen words (one `c.text` call each, swappable via `draw.TEXTS`): "HAPPY BIRTHDAY, PIP" (the banner in
balloons, flowers, ending; its ribbon grows to fit the text) and "The End".

Rules: clips join with hard cuts, so the start of each clip must make sense after the end of the
previous one. No fade to black at clip edges (`EDGE_FADES = False`). A listen loop's last frame must flow
into its first frame; the ask scenes use the idle phase `ph = t - FILM_SECONDS` so they end at phase 0.
