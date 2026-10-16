"""Interactive clip "kitchen" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "kitchen"
PLACE = "Interactive/birthday"
FILM_SECONDS = 32
EDGE_FADES = False
SCENES = ['kitchen', 'ask']
MUSIC = {'kitchen': 'bake', 'ask': 'ask'}

S = Say
A = Act

SCRIPT = [
    A("kitchen", 1.2, "k_open", [("puff", 0.55)]),
    S("narrator", "At home, they mixed the flour, the eggs and the milk.", "kitchen", "k_narr", [("clink", 0.45), ("stir", 0.8)]),
    A("kitchen", 0.8, "k_stir", [("stir", 0.0)]),
    S("whiskers", "Just a little taste... a little more... a little more...", "kitchen", "k_taste"),
    S("luna", "Whiskers! Leave some for the cake!", "kitchen", "k_leave"),
    A("kitchen", 2.0, "k_oven", [("whoosh", 0.1), ("ding", 0.8)]),
    S("narrator", "And now the cake is ready: round, soft and yummy.", "kitchen", "k_ready", [("tada", 0.0)]),
    S("luna", "Now we must decorate the house before Pip comes.", "kitchen", "k_decor"),
    A("kitchen", 0.5, "k_cut"),
    S("whiskers", "Hmm. What do you think?", "ask", "c_think"),
    S("whiskers", "How shall we decorate: with balloons, or with flowers?", "ask", "c_q"),
    A("ask", 1.0, "c_end"),
]
