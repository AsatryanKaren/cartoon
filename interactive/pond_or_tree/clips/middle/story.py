"""Interactive clip "middle" of "Whiskers and the Lost Ball" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.pond_or_tree.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "middle"
PLACE = "Interactive/pond_or_tree"
FILM_SECONDS = 34
EDGE_FADES = False
SCENES = ['river', 'ask']
MUSIC = {'river': 'river', 'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("river", 1.2, "m_arrive"),
    S("luna", "There it is! Your ball! In the water!", "river", "m_see"),
    S("whiskers", "My ball! Come here, ball. Nice ball.", "river", "m_reach"),
    A("river", 1.8, "m_drift", [("plip", 0.1)]),
    S("whiskers", "Oh no! It's floating away!", "river", "m_no"),
    S("narrator", "The ball floated far across the lake, to a little island.", "river", "m_island"),
    A("river", 1.0, "m_pip_in", [("flame", 0.1)]),
    S("pip", "Hello, friends! Need some help? Take my boat... or my balloon!", "river", "m_pip"),
    A("river", 0.5, "m_cut"),
    S("whiskers", "Hmm. What do you think?", "ask", "c_think"),
    S("whiskers", "How should we get it back home: by boat, or by balloon?", "ask", "c_q"),
    A("ask", 1.0, "c_end"),
]
