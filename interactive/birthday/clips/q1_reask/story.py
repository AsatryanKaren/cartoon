"""Interactive clip "q1_reask" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "q1_reask"
PLACE = "Interactive/birthday"
FILM_SECONDS = 5
EDGE_FADES = False
SCENES = ['ask']
MUSIC = {'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("ask", 0.6, "r_in"),
    S("whiskers", "Hmm? Apples... or honey? Tell me!", "ask", "r_q"),
    A("ask", 1.0, "r_end"),
]
