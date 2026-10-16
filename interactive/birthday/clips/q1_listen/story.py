"""Interactive clip "q1_listen" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "q1_listen"
PLACE = "Interactive/birthday"
FILM_SECONDS = 4
EDGE_FADES = False
SCENES = ['ask']
MUSIC = {'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("ask", 1.0, "l_loop"),
]
