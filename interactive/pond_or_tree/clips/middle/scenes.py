"""middle: the clue leads to the lake. The ball is bobbing by the bank -- Whiskers reaches for it, and it
floats away, all the way to a little island. Pip lands in his balloon: take my boat, or my balloon?
Whiskers turns to the viewer and asks Q2. Ends in the listening pose."""
import math

import draw as D
from draw import ease, lerp, clamp
from interactive.pond_or_tree import shared as S

POST_X = 900
BOAT = (1040, 652)
BALLOON_X = 150
BALL_R = 22


def ball_xy(tl, t):
    T = tl.t
    x = S.smooth(t, [(T("m_drift", 0.15), 640), (T("m_no"), 1150), (T("m_island", 0.75), 2030)], r=0.4)
    if x < 1960:
        y = 642 + 4 * math.sin(t * 2.4)
    else:
        y = lerp(642, 586, clamp((x - 1960) / 60))
    return x, y


def pip_inside(tl, t):
    def draw(c):
        D.mouse(c, -6, -66, 2.0, 1, t, mouth=tl.mouth("pip", t), proud=True,
                eyes="happy" if tl.t("m_pip", 0.9) < t else "open")
    return draw


def river(tl, t):
    T = tl.t
    camx = S.smooth(t, [(0, 0), (T("m_no"), 0), (T("m_island", 0.7), 1440), (T("m_pip_in"), 1440),
                        (T("m_pip_in", 0.85), 0)], r=0.4)
    c = S.lake_view(camx)
    c.push(-camx, 0)
    S.water_glints(c, 560, 2600, 660, 710, t, n=40)
    # Pip's boat at its post
    c.rect(POST_X - 7, 560, POST_X + 7, 690, S.TRUNK, w=2.5)
    c.line([(POST_X, 590), (BOAT[0] - 120, BOAT[1] - 40)], (150, 120, 80), 3, cap=False)
    bob = 3 * math.sin(t * 1.8)
    S.rowboat(c, BOAT[0], BOAT[1], 1.0, bob=bob)
    # the balloon comes down to land behind the cats
    if t >= T("m_pip_in", 0.1):
        u = tl.prog("m_pip_in", t, 0.1, 1.0)
        by = lerp(-80, 592, ease(u))
        flame = 1.0 if u < 0.6 else 0.0
        S.balloon(c, BALLOON_X, by, 0.7, t, flame=flame, inside=pip_inside(tl, t))
    # ball
    bx, by = ball_xy(tl, t)
    S.ball(c, bx, by, BALL_R, bx / 20)
    if T("m_drift") <= t < T("m_island", 0.7):
        for k in range(2):
            r = 26 + 30 * ((t * 0.9 + k * 0.5) % 1.0)
            c.ellipse(bx, by + 16, r, r * 0.25, None, ol=S.WATER_L, w=2)
    # Luna
    lx = S.smooth(t, [(0, -300), (T("m_arrive", 0.9), 290)])
    lmov = t < T("m_arrive", 0.95)
    D.cat(c, lx, S.LY, D.LUNA, 1.0, 1, "walk" if lmov else "stand", walk=lx / 12 if lmov else 0, t=t,
          mouth=tl.mouth("luna", t), seed=1.3, look=(1, 0.4),
          eyes="wide" if T("m_drift", 0.4) <= t < T("m_island") else "open")
    # Whiskers
    wx = S.smooth(t, [(0, -150), (T("m_arrive", 0.9), 420)])
    wmov = t < T("m_arrive", 0.95)
    pose = "walk" if wmov else "stand"
    eyes = "open"
    if T("m_reach", 0.3) <= t < T("m_drift", 0.6):
        pose = "crouch"
        wx += 30 * ease(tl.prog("m_reach", t, 0.3, 0.7)) * (1 - ease(tl.prog("m_drift", t, 0.3, 0.6)))
    if T("m_drift", 0.4) <= t < T("m_island"):
        eyes = "wide"
    face = -1 if T("m_pip", 0.0) <= t < T("m_pip", 0.4) else 1
    D.cat(c, wx, S.LY, D.WHISKERS, 1.0, face, pose, walk=wx / 12 if wmov else 0, t=t,
          mouth=tl.mouth("whiskers", t), eyes=eyes, look=(1, 0.6) if pose == "crouch" else (1, 0.2), seed=0,
          tail=math.sin(t * 6) if pose == "crouch" else None)
    c.pop()
    # sparkles on "boat" and "balloon" as Pip names them
    for word, (sx, sy) in (("boat", (BOAT[0], BOAT[1] - 90)), ("balloon", (BALLOON_X + 60, 160))):
        t0 = S.word_time(tl, "m_pip", word)
        k = clamp((t - t0) / 0.9)
        if 0 < k < 1 and camx < 5:
            S.sparkle(c, sx, sy, 22 * math.sin(math.pi * k))
    return c


def ask(tl, t):
    T = tl.t
    e = tl.ev("c_q")
    ph = t - 34
    cues = [(S.word_time(tl, "c_q", "boat"), -1), (S.word_time(tl, "c_q", "balloon"), 1)]
    point = S.point_track(tl, t, cues, e.end + 0.1)
    listen = S.listen_amount(t, t_on=T("c_end", 0.1), dur=0.5)
    s0 = tl.scenes["ask"][0]
    lean = ease((t - s0) / 0.6) * (1 - ease((t - T("c_q")) / 0.5)) \
        + ease((t - T("c_q")) / 0.5) * 0.4 * (1 - ease((t - T("c_end")) / 0.5))
    look = None
    if t < T("c_think", 0.45):
        look = (0.6, -1.0)                          # "Hmm." -- thinking
    elif t < S.word_time(tl, "c_q", "boat") - 0.3:
        look = (0.0, 0.0)
    return S.closeup(S.q2_backdrop(), t, ph, listen=listen, mouth=tl.mouth("whiskers", t), point=point,
                     look=look, lean=lean)


SCENE_FUNCS = {"river": river, "ask": ask}
CONTINUOUS = {"ask"}
