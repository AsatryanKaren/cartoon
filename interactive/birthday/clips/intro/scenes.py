"""intro: a sunny morning in the cats' room. Luna wakes up happy on the rug, hops onto the windowsill and
wakes Whiskers: today is Pip's birthday! Cake? Yes, a surprise cake -- but it needs something sweet:
apples from the tree in the garden, or honey from the bees in the meadow (two thought bubbles).
Whiskers turns to the viewer and asks Q1. Ends in the listening pose."""
import math

import draw as D
import film
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S

SILL = 372                    # top of the windowsill (world y)
WX = 990                      # Whiskers asleep on the sill
LX_RUG, LX_SILL = 520, 862    # Luna: on the rug, then on the sill
WIDE = (0, 0, 1280)
CLOSE = (470, 100, 800)


def luna_pose(tl, t):
    """x, y, scale, pose, face, eyes"""
    T = tl.t
    if t < T("i_open", 0.35):
        return LX_RUG, 612, 1.0, "sleep", 1, "closed"
    if t < T("i_hop"):
        happy = t < T("i_narr", 0.9)
        hop = abs(math.sin((t - T("i_narr", 0.5)) * 7)) * 10 if T("i_narr", 0.5) <= t < T("i_narr", 1) else 0
        pose = "sit" if t < T("i_narr", 0.3) else "stand"
        return LX_RUG, 612 - hop, 1.0, pose, 1, "happy" if happy else "open"
    k = tl.prog("i_hop", t)
    if k < 0.45:
        x = lerp(LX_RUG, 760, ease(k / 0.45))
        return x, 612, 1.0, "walk", 1, "open"
    if k < 0.85:
        u = (k - 0.45) / 0.4
        x = lerp(760, LX_SILL, ease(u))
        y = lerp(612, SILL, u) - 120 * math.sin(math.pi * u)
        return x, y, lerp(1.0, 0.8, u), "leap", 1, "open"
    hop = 0.0
    if T("i_wake") <= t < T("i_wake", 1):
        hop = abs(math.sin((t - T("i_wake")) * 8)) * 8
    eyes = "happy" if T("i_bake") <= t < T("i_bake", 0.5) else "open"
    return LX_SILL, SILL - hop, 0.8, "stand" if t < T("i_up") else "sit", 1, eyes


def room(tl, t):
    T = tl.t
    c = Canvas(S.room_bg().copy())
    # sunbeam sparkles in the morning air
    for k in range(5):
        u = ((t * 0.12) + k / 5) % 1.0
        S.sparkle(c, 820 + 60 * k, 140 + 200 * u, 5 * math.sin(math.pi * u), (255, 250, 210))
    # Whiskers on the sill
    if t < T("i_up"):
        D.cat(c, WX, SILL, D.WHISKERS, 0.8, -1, "sleep", t=t, mouth=0.0, seed=0)
        D.zzz(c, WX - 50, SILL - 60, t)
    else:
        k = clamp((t - T("i_up")) / 0.25)
        eyes = "wide" if t < T("i_up", 1) else "open"
        if T("i_cake", 0.6) <= t < T("i_bake"):
            eyes = "wide"
        if T("i_dream") <= t < T("i_sweet"):
            eyes = "happy"
        look = (1, 0.2)
        if T("i_sweet") <= t < T("i_options"):
            look = (0.6, -1)
        if T("i_options") <= t:
            look = (1, -0.6)
        jump = 26 * math.sin(math.pi * k) if k < 1 else 0
        mouth = tl.mouth("whiskers", t)
        if T("i_dream", 0.1) <= t < T("i_dream", 0.9):
            mouth = 0.3 + 0.3 * math.sin(t * 9)            # licking his lips
        D.cat(c, WX, SILL - jump, D.WHISKERS, 0.8, -1, "sit", t=t, mouth=mouth, seed=0, eyes=eyes, look=look)
    # Luna
    lx, ly, ls, lpose, lface, leyes = luna_pose(tl, t)
    D.cat(c, lx, ly, D.LUNA, ls, lface, lpose, walk=lx / 12 if lpose == "walk" else 0, t=t,
          mouth=tl.mouth("luna", t), seed=1.3, eyes=leyes, look=(1, -0.3))
    if lpose == "sleep":
        D.zzz(c, lx + 50, ly - 70, t + 1)
    if T("i_narr", 0.2) <= t < T("i_narr", 1):
        S.hearts(c, lx + 30, ly - 120, t, n=3)
    # thought bubbles
    k = ease(tl.prog("i_dream", t, 0.0, 0.25)) * (1 - ease(tl.prog("i_sweet", t, 0.4, 0.8)))
    S.bubble(c, 1140, 200, 95, 66, k, (WX - 30, SILL - 110), lambda cc: S.cake(cc, 0, 40, 0.5, t))
    ka = ease((t - S.word_time(tl, "i_options", "apple") + 0.2) / 0.4) * (1 - ease(tl.prog("i_think", t, 0.3, 0.9)))
    S.bubble(c, 690, 225, 82, 66, ka, (LX_SILL + 10, SILL - 120),
             lambda cc: S.apple_tree(cc, 0, 50, 0.17, t))
    kb = ease((t - S.word_time(tl, "i_options", "bees") + 0.2) / 0.4) * (1 - ease(tl.prog("i_think", t, 0.3, 0.9)))
    S.bubble(c, 870, 182, 82, 62, kb, (LX_SILL + 10, SILL - 120), lambda cc: _hive(cc, t))
    # camera: wide on the room, then in on the sill as Luna hops up
    z = ease(tl.prog("i_hop", t, 0.35, 0.95))
    x0 = lerp(WIDE[0], CLOSE[0], z)
    y0 = lerp(WIDE[1], CLOSE[1], z)
    w = lerp(WIDE[2], CLOSE[2], z)
    return S.cam(c, x0, y0, w)


def _hive(c, t):
    S.beehive(c, 0, 48, 0.42)
    S.bee(c, 34, -30, 0.36, -1, t)
    S.bee(c, -40, -10, 0.32, 1, t + 1)


def ask(tl, t):
    T = tl.t
    e = tl.ev("c_q")
    ph = t - film.FILM_SECONDS
    cues = [(S.word_time(tl, "c_q", "apples"), -1), (S.word_time(tl, "c_q", "honey"), 1)]
    point = S.point_track(tl, t, cues, e.end + 0.1)
    listen = S.listen_amount(t, t_on=T("c_end", 0.1), dur=0.5)
    lean = ease((t - tl.scenes["ask"][0]) / 0.6) * (1 - ease((t - T("c_q")) / 0.5)) \
        + ease((t - T("c_q", 0.0)) / 0.5) * 0.4 * (1 - ease((t - T("c_end")) / 0.5))
    look = (0.0, 0.0) if t < S.word_time(tl, "c_q", "apples") - 0.3 else None
    happy = 1.0 if T("c_help") <= t < S.word_time(tl, "c_help", "will") else 0.0
    return S.closeup(S.q1_backdrop(), t, ph, listen=listen, mouth=tl.mouth("whiskers", t), point=point,
                     look=look, lean=lean, happy=happy)


SCENE_FUNCS = {"room": room, "ask": ask}
CONTINUOUS = {"ask"}          # hard cut to the close-up
