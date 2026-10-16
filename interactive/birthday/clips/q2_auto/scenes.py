"""q2_auto: nobody answered -- Whiskers picks balloons (the left option). Starts in the listening pose."""
from interactive.birthday import shared as S


def ask(tl, t):
    e = tl.ev("a_say")
    listen = S.listen_amount(t, t_off=e.start - 0.5, dur=0.45)
    choose = S.word_time(tl, "a_say", "choose")
    pick = S.word_time(tl, "a_say", "Balloons")
    look = (0.6, -1.0) if t < choose else None             # "Hmm..." looks up, thinking
    point = S.point_track(tl, t, [(pick, -1)], 99.0)
    happy = 1.0 if choose - 0.1 <= t < pick - 0.3 else 0.0
    return S.closeup(S.q2_backdrop(), t, t, listen=listen, mouth=tl.mouth("whiskers", t), point=point,
                     look=look, happy=happy)


SCENE_FUNCS = {"ask": ask}
