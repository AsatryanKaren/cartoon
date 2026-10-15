"""Interactive clip "q1_reask" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "q1_reask"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 6
EDGE_FADES = False
SCENES = ['ask']
MUSIC = {'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("ask", 0.6, "r_in"),
    S("whiskers", "Hmm? The pond... or the tree? Tell me!", "ask", "r_q"),
    A("ask", 1.0, "r_end"),
]
