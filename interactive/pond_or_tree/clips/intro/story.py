"""Interactive clip "intro" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "intro"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 46
EDGE_FADES = False
SCENES = ['garden', 'ask']
MUSIC = {'garden': 'play', 'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("garden", 1.4, "i_open", [("boing", 0.15), ("boing", 0.6)]),
    S("narrator", "This is Whiskers. And this is his very favourite thing in the whole world: his big red ball!", "garden", "i_narr", [("boing", 0.3), ("boing", 0.75)]),
    S("luna", "Pass it to me, Whiskers!", "garden", "i_pass_l"),
    A("garden", 1.2, "i_pass", [("boing", 0.25), ("boing", 0.75)]),
    S("whiskers", "Watch this, Luna. My super-duper mega kick!", "garden", "i_brag"),
    A("garden", 2.2, "i_kick", [("whoosh", 0.32), ("boing", 0.38)]),
    A("garden", 1.0, "i_gone"),
    S("whiskers", "Uh oh. Where did my ball go?", "garden", "i_where"),
    S("luna", "It flew far, far away! Maybe it landed by the pond. Or maybe up in the big tree!", "garden", "i_options"),
    A("garden", 0.6, "i_think"),
    S("whiskers", "Hello, friend! Will you help me find my ball?", "ask", "c_help"),
    S("whiskers", "Where should we look first: by the pond, or up in the big tree?", "ask", "c_q"),
    A("ask", 1.0, "c_end"),
]
