"""Interactive clip "flowers" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "flowers"
PLACE = "Interactive/birthday"
FILM_SECONDS = 30
EDGE_FADES = False
SCENES = ['pick', 'room']
MUSIC = {'pick': 'meadow', 'room': 'party'}

S = Say
A = Act

SCRIPT = [
    A("pick", 1.0, "f_open"),
    S("narrator", "Luna and Whiskers picked flowers in the garden.", "pick", "f_narr"),
    S("luna", "Poppies, daisies, roses... How pretty!", "pick", "f_names"),
    A("pick", 0.8, "f_carry"),
    A("room", 1.0, "f_vase"),
    S("whiskers", "Let me smell them too... Ah... ah... achoo!", "room", "f_sniff", [("whoosh", 0.92)]),
    A("room", 2.0, "f_blow", [("whoosh", 0.05), ("whoosh", 0.3)]),
    S("luna", "Whiskers! The petals flew everywhere!", "room", "f_petals"),
    S("whiskers", "Well... now the whole house is decorated.", "room", "f_deco"),
    S("luna", "That's true. It's even prettier now.", "room", "f_true"),
    A("room", 1.4, "f_end"),
]
