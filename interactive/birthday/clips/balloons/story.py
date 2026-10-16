"""Interactive clip "balloons" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "balloons"
PLACE = "Interactive/birthday"
FILM_SECONDS = 31
EDGE_FADES = False
SCENES = ['party']
MUSIC = {'party': 'party'}

S = Say
A = Act

SCRIPT = [
    A("party", 1.0, "b_open"),
    S("narrator", "Luna and Whiskers started blowing up balloons.", "party", "b_narr", [("puff", 0.3), ("puff", 0.7)]),
    S("luna", "Red, yellow, blue... How pretty!", "party", "b_colors"),
    S("whiskers", "I'll blow up the biggest balloon of all. Phoo... phoo...", "party", "b_big", [("puff", 0.72), ("puff", 0.9)]),
    A("party", 2.6, "b_grow", [("puff", 0.05), ("puff", 0.25), ("puff", 0.42), ("whoosh", 0.65)]),
    S("whiskers", "Help! I'm flying!", "party", "b_fly"),
    S("luna", "Whiskers, come down!", "party", "b_down"),
    A("party", 1.8, "b_pop", [("bang", 0.12), ("whoosh", 0.2), ("boing", 0.6)]),
    S("whiskers", "Phew... That was fun! Shall we do it again?", "party", "b_again"),
    S("luna", "No! Look, the house is ready.", "party", "b_no"),
    A("party", 1.6, "b_end"),
]
