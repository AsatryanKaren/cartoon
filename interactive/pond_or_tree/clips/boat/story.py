"""Interactive clip "boat" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "boat"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 32
EDGE_FADES = False
SCENES = ['row', 'home']
MUSIC = {'row': 'sail', 'home': 'home'}

S = Say
A = Act

SCRIPT = [
    A("row", 1.0, "b_push", [("plip", 0.6)]),
    S("narrator", "Everyone jumped into Pip's little boat. Row, row, row!", "row", "b_narr"),
    A("row", 1.8, "b_row", [("plip", 0.2), ("plip", 0.5), ("plip", 0.8)]),
    S("luna", "Whiskers! We're going round in circles!", "row", "b_circle"),
    S("whiskers", "I'm just warming up!", "row", "b_warm"),
    A("row", 1.8, "b_cross", [("plip", 0.15), ("plip", 0.45), ("plip", 0.75)]),
    S("luna", "Got it!", "row", "b_got", [("boing", 0.0)]),
    S("pip", "Hooray! Now, home we go!", "row", "b_hooray"),
    A("home", 2.2, "b_float", [("plip", 0.3), ("plip", 0.6)]),
    S("whiskers", "Home sweet home!", "home", "b_home"),
    A("home", 0.9, "b_end"),
]
