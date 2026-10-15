"""intro: Whiskers and Luna play with the big red ball in the garden; the super-duper mega kick sends
it far away; Whiskers turns to the viewer and asks Q1 (pond or big tree). Ends in the listening pose."""
import math

import draw as D
from draw import ease, lerp, clamp
from interactive.pond_or_tree import shared as S

CAMX = 300
WX0, LX0 = 1010, 1320          # where Whiskers and Luna stand (world x)
BALL_R = 22


def bounce(t, P=1.5):
    u = (t % P) / P
    v = u * 2 if u < 0.5 else 2 - u * 2
    x = lerp(WX0 + 90, LX0 - 90, ease(v))
    y = S.GY - BALL_R - 70 * math.sin(math.pi * ((u * 2) % 1.0))
    return x, y


def ball_pos(tl, t):
    """World position + spin of the ball."""
    T = tl.t
    if t < T("i_brag"):
        x, y = bounce(t)
        return x, y, x / 18
    rest = (WX0 + 100, S.GY - BALL_R)
    if t < T("i_kick", 0.36):
        x0, y0 = bounce(T("i_brag"))
        u = ease((t - T("i_brag")) / 0.6)
        x = lerp(x0, rest[0], u)
        return x, lerp(y0, rest[1], u), x / 18
    u = tl.prog("i_kick", t, 0.36, 0.8)
    x = lerp(rest[0], CAMX + 1450, u)
    y = rest[1] - 760 * math.sin(min(1.0, u * 1.25) * math.pi / 2)
    return x, y, t * 14


def garden(tl, t):
    T = tl.t
    c = S.view(S.garden_bg(False), CAMX)
    c.push(-CAMX, 0)
    bx, by, spin = ball_pos(tl, t)
    looking_up = T("i_kick", 0.4) <= t < T("i_where", 1)
    # Whiskers
    wx, pose, eyes, wy, squash, face = WX0, "stand", "open", S.GY, 1.0, 1
    walk = 0.0
    if T("i_brag") <= t < T("i_kick"):
        u = ease((t - T("i_brag", 0.5)) / 1.2)
        wx = lerp(WX0, WX0 - 150, u)
        walk = wx / 12 if 0 < u < 1 else 0.0
        pose = "walk" if 0 < u < 1 else "stand"
    if t >= T("i_kick"):
        k = tl.prog("i_kick", t)
        if k < 0.3:
            wx = lerp(WX0 - 150, WX0 + 30, ease(k / 0.3))
            pose, walk = "walk", wx / 8
        elif k < 0.5:
            u = (k - 0.3) / 0.2
            wx = lerp(WX0 + 30, WX0 + 70, u)
            pose, wy, eyes = "leap", S.GY + S.arc_y(u, 60), "wide"
        else:
            wx = WX0 + 70
            squash = 1 - 0.2 * max(0.0, 1 - (k - 0.5) / 0.1)
    if T("i_where") <= t < T("i_where", 1) + 0.3:
        eyes = "wide"
    if T("i_think") <= t:
        face = -1
    look = (1, -1) if looking_up else (1, 0.2)
    D.cat(c, wx, wy, D.WHISKERS, 1.0, face, pose, walk=walk, t=t, mouth=tl.mouth("whiskers", t), eyes=eyes,
          look=look, squash=squash, seed=0)
    # Luna
    lface = -1
    leyes = "open"
    if T("i_kick", 0.4) <= t < T("i_gone", 1):
        leyes = "wide"
    lx = LX0
    if T("i_pass_l") <= t < T("i_pass", 1):
        hop = abs(math.sin(t * 7)) * 8
    else:
        hop = 0
    D.cat(c, lx, S.GY - hop, D.LUNA, 1.0, lface, "stand", t=t, mouth=tl.mouth("luna", t), eyes=leyes,
          look=(1, -1) if looking_up else (1, 0.2), seed=1.3)
    # ball (in front)
    if by > -60:
        S.ball(c, bx, by, BALL_R, spin)
    c.pop()
    # twinkle where the ball vanished
    k = tl.prog("i_gone", t, 0.0, 0.7)
    if 0 < k < 1:
        r = 26 * math.sin(math.pi * k)
        S.sparkle(c, 1150, 60, r)
    return c


def ask(tl, t):
    T = tl.t
    e = tl.ev("c_q")
    ph = t - 46
    cues = [(S.word_time(tl, "c_q", "pond"), -1), (S.word_time(tl, "c_q", "up in"), 1)]
    point = S.point_track(tl, t, cues, e.end + 0.1)
    listen = S.listen_amount(t, t_on=T("c_end", 0.1), dur=0.5)
    lean = ease((t - tl.scenes["ask"][0]) / 0.6) * (1 - ease((t - T("c_q")) / 0.5)) \
        + ease((t - T("c_q", 0.0)) / 0.5) * 0.4 * (1 - ease((t - T("c_end")) / 0.5))
    look = (0.0, 0.0) if t < S.word_time(tl, "c_q", "pond") - 0.3 else None
    happy = 1.0 if T("c_help") <= t < S.word_time(tl, "c_help", "will") else 0.0
    return S.closeup(S.q1_backdrop(), t, ph, listen=listen, mouth=tl.mouth("whiskers", t), point=point,
                     look=look, lean=lean, happy=happy)


SCENE_FUNCS = {"garden": garden, "ask": ask}
CONTINUOUS = {"ask"}          # hard cut to the close-up
