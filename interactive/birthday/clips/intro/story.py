"""Interactive clip "intro" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "intro"
PLACE = "Interactive/birthday"
FILM_SECONDS = 40
EDGE_FADES = False
SCENES = ['room', 'ask']
MUSIC = {'room': 'wake', 'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("room", 2.0, "i_open", [("purr", 0.05)]),
    S("narrator", "One sunny morning, Luna woke up very happy.", "room", "i_narr"),
    A("room", 1.4, "i_hop", [("whoosh", 0.3)]),
    S("luna", "Whiskers, wake up! Today is Pip's birthday!", "room", "i_wake"),
    A("room", 1.0, "i_up", [("boing", 0.1)]),
    S("whiskers", "A birthday...? So there will be cake?", "room", "i_cake"),
    S("luna", "Yes! Let's bake a surprise cake for Pip.", "room", "i_bake"),
    A("room", 0.8, "i_dream"),
    S("whiskers", "But a cake needs something sweet.", "room", "i_sweet"),
    S("luna", "There's an apple tree in the garden, and bees with honey in the meadow.", "room", "i_options"),
    A("room", 0.8, "i_think"),
    S("whiskers", "Hello, friend! Will you help us?", "ask", "c_help"),
    S("whiskers", "What shall we put in the cake: apples, or honey?", "ask", "c_q"),
    A("ask", 1.0, "c_end"),
]
