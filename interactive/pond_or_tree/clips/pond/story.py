"""Interactive clip "pond" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "pond"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 38
EDGE_FADES = False
SCENES = ['pond']
MUSIC = {'pond': 'pondday'}

S = Say
A = Act

CAST = {**CAST, "frog": Voice("am_puck", 0.95, -3, ["Fred"], 170, "en-us+m2", 30, 150)}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "frog": (190, 240, 150)}

SCRIPT = [
    A("pond", 1.4, "p_arrive", [("ribbit", 0.5)]),
    S("narrator", "So off they went, to the pond.", "pond", "p_narr"),
    S("luna", "Ball! Are you here, ball?", "pond", "p_call"),
    A("pond", 1.0, "p_look", [("ribbit", 0.3)]),
    S("whiskers", "I'll look in the water. Very, very carefully.", "pond", "p_lean"),
    A("pond", 2.0, "p_fall", [("whoosh", 0.3), ("splash", 0.5)]),
    S("whiskers", "Blub! I meant to do that. On purpose.", "pond", "p_purpose"),
    A("pond", 1.0, "p_laugh", [("ribbit", 0.15), ("ribbit", 0.55)]),
    S("frog", "Ribbit! Are you looking for a big red ball?", "pond", "p_frog"),
    S("frog", "It bounced on my lily pad. Boing! Then it rolled all the way down to the river!", "pond", "p_clue"),
    S("luna", "Look! Round little tracks in the mud. They go to the river!", "pond", "p_tracks"),
    S("whiskers", "Thank you, frog! To the river!", "pond", "p_go"),
    A("pond", 1.6, "p_exit"),
]
