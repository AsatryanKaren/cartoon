"""q1_reask: starts and ends in the listening pose (so it joins the listen loop both ways)."""
from interactive.birthday import shared as S


def ask(tl, t):
    e = tl.ev("r_q")
    listen = S.listen_amount(t, t_off=e.start - 0.55, dur=0.45) + S.listen_amount(t, t_on=e.end + 0.15, dur=0.5)
    cues = [(S.word_time(tl, "r_q", "Apples"), -1), (S.word_time(tl, "r_q", "honey"), 1)]
    point = S.point_track(tl, t, cues, e.end + 0.1)
    look = None
    if t < S.word_time(tl, "r_q", "Apples") - 0.3:
        look = (0.0, 0.0)
    lean = S.ease((t - e.start + 0.5) / 0.4) * (1 - S.ease((t - e.end) / 0.5))
    return S.closeup(S.q1_backdrop(), t, t, listen=min(1.0, listen), mouth=tl.mouth("whiskers", t), point=point,
                     look=look, lean=lean)


SCENE_FUNCS = {"ask": ask}
