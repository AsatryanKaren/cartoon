"""Interactive clip "honey" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "honey"
PLACE = "Interactive/birthday"
FILM_SECONDS = 40
EDGE_FADES = False
SCENES = ['meadow']
MUSIC = {'meadow': 'meadow'}

S = Say
A = Act

CAST = {**CAST, "buzzy": Voice("af_nova", 1.1, 4, ["Samantha"], 190, "en-us+f4", 80, 175)}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "buzzy": (255, 235, 120)}

SCRIPT = [
    A("meadow", 1.3, "h_arrive", [("buzz", 0.3)]),
    S("narrator", "So off they went, to the flowery meadow.", "meadow", "h_narr"),
    S("luna", "Can you hear that? Bzzz... The bees are here.", "meadow", "h_hear", [("buzz", 0.35)]),
    S("whiskers", "Honey... I love honey so much.", "meadow", "h_love"),
    A("meadow", 0.9, "h_fly_in", [("buzz", 0.0)]),
    S("buzzy", "Bzzz! Hello! I'm Buzzy. What are you looking for?", "meadow", "h_bee"),
    S("luna", "We're baking a birthday cake for Pip. Could you give us a little honey?", "meadow", "h_ask"),
    S("buzzy", "Of course! But first, help me water the flowers.", "meadow", "h_water"),
    A("meadow", 3.2, "h_watering", [("water", 0.12), ("water", 0.6), ("splash", 0.78)]),
    S("whiskers", "I watered the flowers... and myself. On purpose.", "meadow", "h_wet"),
    A("meadow", 1.0, "h_fetch", [("buzz", 0.0)]),
    S("buzzy", "Well done! Here's a little pot of sweet honey.", "meadow", "h_pot"),
    S("whiskers", "Thank you, Buzzy! Let's go home.", "meadow", "h_go", [("buzz", 0.6)]),
    A("meadow", 1.4, "h_exit"),
]
