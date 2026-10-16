"""Interactive clip "ending" of "Pip's Birthday Surprise" (see ../../SPEC.md)."""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act  # noqa: F401
from interactive.birthday.shared import MOODS, EXTRA_SFX  # noqa: F401

TITLE = "ending"
PLACE = "Interactive/birthday"
FILM_SECONDS = 26
EDGE_FADES = False
SCENES = ['party', 'thanks']
MUSIC = {'party': 'party', 'thanks': 'home'}

S = Say
A = Act

SCRIPT = [
    A("party", 1.4, "e_open", [("knock", 0.3), ("knock", 0.45), ("knock", 0.6)]),
    S("narrator", "Knock, knock! It was Pip at the door.", "party", "e_knock"),
    A("party", 1.4, "e_door", [("whoosh", 0.1)]),
    S("luna", "Surprise! Happy birthday, Pip!", "party", "e_surprise", [("tada", 0.0)]),
    S("pip", "Wow! Is this for me? What a beautiful cake!", "party", "e_wow"),
    A("party", 0.5, "e_cut"),
    S("whiskers", "And you helped too, friend. Thank you!", "thanks", "e_thanks"),
    S("luna", "The best present is the one we make together, with love.", "thanks", "e_moral"),
    S("pip", "Thank you, friends! Let's eat cake!", "thanks", "e_eat"),
    S("whiskers", "Finally!", "thanks", "e_finally"),
    A("thanks", 2.2, "e_end"),
]
