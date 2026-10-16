"""Interactive clip "q1_auto" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "q1_auto"
PLACE = "Interactive/birthday"
FILM_SECONDS = 5
EDGE_FADES = False
SCENES = ['ask']
MUSIC = {'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("ask", 0.5, "a_in"),
    S("whiskers", "Hmm... I'll choose! Apples!", "ask", "a_say"),
    A("ask", 0.8, "a_end"),
]
