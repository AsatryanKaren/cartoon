"""Interactive clip "tree" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "tree"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 38
EDGE_FADES = False
SCENES = ['tree']
MUSIC = {'tree': 'climb'}

S = Say
A = Act

CAST = {**CAST, "bird": Voice("bf_lily", 1.05, 3, ["Kate"], 186, "en-gb+f4", 72, 172)}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "bird": (180, 225, 255)}

SCRIPT = [
    A("tree", 1.3, "t_arrive"),
    S("narrator", "So off they went, to the big tree.", "tree", "t_narr"),
    S("luna", "It's so tall! Is your ball up there?", "tree", "t_tall"),
    S("whiskers", "Leave it to me. I am an excellent climber.", "tree", "t_brag"),
    A("tree", 2.6, "t_climb", [("whoosh", 0.08), ("whoosh", 0.4), ("whoosh", 0.72)]),
    S("bird", "Tweet! Hello! Are you looking for a big red ball?", "tree", "t_bird", [("tweet", 0.0)]),
    S("bird", "I saw it from up here! It bounced down the hill, all the way to the river!", "tree", "t_clue"),
    A("tree", 1.0, "t_view"),
    S("luna", "I can see the river from here!", "tree", "t_see"),
    A("tree", 2.0, "t_slip", [("whoosh", 0.1), ("whoosh", 0.4), ("plip", 0.78)]),
    S("whiskers", "I meant to do that. On purpose.", "tree", "t_purpose"),
    S("whiskers", "Thank you, bird! To the river!", "tree", "t_go", [("tweet", 0.6)]),
    A("tree", 1.4, "t_exit"),
]
