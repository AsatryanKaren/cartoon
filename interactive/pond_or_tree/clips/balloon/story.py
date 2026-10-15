"""Interactive clip "balloon" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "balloon"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 32
EDGE_FADES = False
SCENES = ['fly', 'home']
MUSIC = {'fly': 'fly', 'home': 'home'}

S = Say
A = Act

SCRIPT = [
    A("fly", 1.0, "bl_lift", [("flame", 0.1)]),
    S("narrator", "Everyone climbed into Pip's balloon. Up, up, up they went!", "fly", "bl_narr", [("flame", 0.5)]),
    A("fly", 1.2, "bl_rise"),
    S("whiskers", "Wow! Everything looks so tiny down there!", "fly", "bl_tiny"),
    A("fly", 0.8, "bl_over"),
    S("pip", "Leave it to me! I'm the bravest mouse in the meadow!", "fly", "bl_pip"),
    A("fly", 1.8, "bl_rope", [("whoosh", 0.1), ("boing", 0.5), ("whoosh", 0.65)]),
    S("luna", "You did it, Pip! You got the ball!", "fly", "bl_got"),
    A("home", 2.2, "bl_float", [("flame", 0.2)]),
    S("whiskers", "Home sweet home!", "home", "bl_home"),
    A("home", 0.9, "bl_end"),
]
