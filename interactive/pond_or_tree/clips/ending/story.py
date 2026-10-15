"""Interactive clip "ending" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "ending"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 30
EDGE_FADES = False
SCENES = ['sill', 'thanks']
MUSIC = {'sill': 'home', 'thanks': 'home'}

S = Say
A = Act

SCRIPT = [
    A("sill", 1.2, "e_open", [("purr", 0.1)]),
    S("narrator", "That evening, Whiskers held his ball very, very tight.", "sill", "e_narr"),
    S("whiskers", "I'll never kick you that far again. Probably.", "sill", "e_never"),
    A("sill", 0.5, "e_cut"),
    S("whiskers", "And you! You helped us choose! Thank you, friend!", "thanks", "e_thanks"),
    S("luna", "When friends help each other, lost things get found.", "thanks", "e_moral"),
    S("pip", "Bye bye!", "thanks", "e_bye"),
    A("thanks", 2.0, "e_end"),
]
