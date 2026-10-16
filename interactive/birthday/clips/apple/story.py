"""Interactive clip "apple" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "apple"
PLACE = "Interactive/birthday"
FILM_SECONDS = 40
EDGE_FADES = False
SCENES = ['orchard']
MUSIC = {'orchard': 'orchard'}

S = Say
A = Act

CAST = {**CAST, "hedgie": Voice("am_echo", 0.95, 2, ["Fred"], 170, "en-us+m3", 40, 150)}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "hedgie": (235, 205, 160)}

SCRIPT = [
    A("orchard", 1.3, "a_arrive"),
    S("narrator", "So off they went, to the apple tree.", "orchard", "a_narr"),
    S("luna", "Look at all the red apples! But they're so high.", "orchard", "a_high"),
    S("whiskers", "Easy. I'll shake the tree.", "orchard", "a_shake"),
    A("orchard", 2.6, "a_shakeit", [("whoosh", 0.12), ("whoosh", 0.32), ("plip", 0.5), ("plip", 0.6), ("bonk", 0.74)]),
    S("whiskers", "Ouch! An apple fell right on my head.", "orchard", "a_bonk"),
    S("whiskers", "I meant to do that. On purpose.", "orchard", "a_purpose"),
    A("orchard", 1.1, "a_hog_in"),
    S("hedgie", "Hello! I'm Hedgie. Are you gathering apples?", "orchard", "a_hog"),
    S("hedgie", "Watch how I do it. Roll, roll!", "orchard", "a_roll"),
    A("orchard", 3.0, "a_rolling", [("roll", 0.08), ("plip", 0.3), ("plip", 0.42), ("plip", 0.55), ("roll", 0.6), ("boing", 0.82)]),
    S("luna", "How clever you are, Hedgie! Now we have lots of apples.", "orchard", "a_clever"),
    S("whiskers", "Thank you, Hedgie! Let's go home.", "orchard", "a_go"),
    A("orchard", 1.4, "a_exit"),
]
