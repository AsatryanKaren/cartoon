"""q1_listen: a seamless 4 s loop. Whiskers looks at the viewer, ear up, paw at the ear, listening.
All motion is periodic (2 s; blink every 4 s), so the last frame flows into the first."""
from interactive.pond_or_tree import shared as S


def ask(tl, t):
    return S.closeup(S.q1_backdrop(), t, t, listen=1.0)


SCENE_FUNCS = {"ask": ask}
