"""balloons: the living room, banner up and the cake on the table. Luna blows up red, yellow and blue
balloons; Whiskers blows up the biggest balloon of all -- it grows and grows and lifts him off the floor.
Pop! He drops softly onto a big cushion. "Shall we do it again?" No: the house is ready (more balloons
pop into place all over the room)."""
import math

import draw as D
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S

PY = 640
LX, WX = 400, 640
CUSH = 820
WEIGHT = (250, PY)
LUNA_B = [((205, 395), 0), ((275, 365), 1), ((236, 318), 2)]       # where Luna's three balloons end up
GREEN = (120, 210, 110)
EXTRA = [((520, 210), 4), ((780, 190), 5), ((140, 160), 3), ((1240, 220), 0), ((880, 300), 2), ((400, 240), 1)]


def luna_balloons(c, tl, t):
    T = tl.t
    mx, my = LX + 70, PY - 74
    tied = []
    for k, ((bx, by), ci) in enumerate(LUNA_B):
        a, b = T("b_narr", k / 3), T("b_narr", (k + 1) / 3)
        if t < a:
            continue
        u = (t - a) / (b - a)
        if u < 0.7:
            r = 36 * ease(u / 0.7)
            S.party_balloon(c, mx + r * 0.86 + 2, my - r * 0.25, max(3, r), S.BALLOON_COLS[ci], t, string=0, sway=0)
        else:
            v = ease(min(1.0, (u - 0.7) / 0.3)) if t < b else 1.0
            x = lerp(mx + 36, bx, v)
            y = lerp(my - 9, by, v)
            tied.append((x, y, ci, v))
    for x, y, ci, v in tied:
        sway = 4 * math.sin(t * 1.3 + ci)
        c.line([(WEIGHT[0], WEIGHT[1] - 14), (x + sway, y + 44)], (110, 100, 110), 2, cap=False)
    for x, y, ci, v in tied:
        S.party_balloon(c, x + 4 * math.sin(t * 1.3 + ci), y, 40, S.BALLOON_COLS[ci], t, string=0, sway=0)
    c.rect(WEIGHT[0] - 14, WEIGHT[1] - 16, WEIGHT[0] + 14, WEIGHT[1], (230, 80, 120), w=2.5, r=4)
    # "Red, yellow, blue": a sparkle on each as Luna names it
    for word, ((bx, by), ci) in zip(("red", "yellow", "blue"), LUNA_B):
        k = clamp((t - S.word_time(tl, "b_colors", word)) / 0.7)
        if 0 < k < 1:
            S.sparkle(c, bx + 30, by - 30, 16 * math.sin(math.pi * k))


def whiskers_state(tl, t):
    """x, y, pose, eyes, balloon (cx, cy, r) or None, popped-time or None"""
    T = tl.t
    hx = WX - 52                                   # his head (he faces left)
    mx, my = WX - 70, PY - 74
    phoos = [S.word_time(tl, "b_big", "phoo"), S.word_time(tl, "b_big", "phoo") + 0.0]
    t1 = S.word_time(tl, "b_big", "phoo")
    if t < t1:
        return WX, PY, "stand", "open", None
    if t < T("b_grow"):
        r = 10 + 14 * ease((t - t1) / max(0.3, T("b_grow") - t1))
        return WX, PY, "stand", "closed", (mx - r * 0.86 - 2, my - r * 0.25, r)
    k = tl.prog("b_grow", t)
    if k < 0.45:
        r = lerp(24, 70, ease(k / 0.45)) + 4 * math.sin(t * 14)
        return WX, PY, "stand", "closed", (mx - r * 0.86 - 2, my - r * 0.25, r)
    if k < 0.65:
        u = ease((k - 0.45) / 0.2)
        r = lerp(70, 115, u)
        cx = lerp(mx - 70 * 0.86, WX + 10, u)
        cy = lerp(my - 18, PY - 140 - r, u)
        return WX, PY, "stand", "wide", (cx, cy, r)
    u = ease((k - 0.65) / 0.35)
    r = 115
    y = lerp(PY, 400, u)
    x = WX + 30 * u
    return x, y, "leap", "wide", (x + 10, y - 140 - r, r)


def party(tl, t):
    T = tl.t
    c = Canvas(S.party_bg(True).copy())
    S.cake(c, S.CAKE_AT[0], S.CAKE_AT[1], 0.75, t)
    # the house gets ready: balloons pop into place everywhere
    for k, ((bx, by), ci) in enumerate(EXTRA):
        a = ease(tl.prog("b_no", t, 0.25 + 0.1 * k, 0.4 + 0.1 * k)) if t < T("b_end") else 1.0
        if a > 0:
            S.party_balloon(c, bx, by, 38 * a, S.BALLOON_COLS[ci], t, string=60 * a, seed=k)
    luna_balloons(c, tl, t)
    # cushion
    land = T("b_pop", 0.5)
    sq = 0.0
    if land <= t < land + 0.3:
        sq = math.sin(math.pi * (t - land) / 0.3)
    S.cushion(c, CUSH, PY + 4, 0.8, sq)
    # ---- Luna
    flying = T("b_grow", 0.65) <= t < T("b_pop", 0.5)
    leyes = "wide" if flying or T("b_pop", 0.1) <= t < T("b_pop", 0.6) else "open"
    if T("b_colors", 0.6) <= t < T("b_big") or T("b_no", 0.5) <= t:
        leyes = "happy"
    lhop = abs(math.sin(t * 7)) * 16 if T("b_down") <= t < T("b_down", 1) else 0
    lface = -1 if T("b_colors") <= t < T("b_colors", 0.7) else 1
    D.cat(c, LX, PY - lhop, D.LUNA, 1.0, lface, "stand", t=t, mouth=0.0 if t < T("b_colors") else tl.mouth("luna", t),
          seed=1.3, eyes="closed" if t < T("b_colors") and T("b_narr") <= t else leyes,
          look=(1, -1) if flying else (1, 0))
    # ---- Whiskers
    if t < T("b_pop", 0.12):
        wx, wy, pose, weyes, bal = whiskers_state(tl, t)
        if bal is not None:
            cx, cy, r = bal
            if pose == "leap" or r > 80:
                c.line([(cx, cy + r + 8), (wx - 30, wy - 70)], (110, 100, 110), 2.5, cap=False)
            S.party_balloon(c, cx, cy, r, GREEN, t, string=0, sway=0)
        dangle = 0.0
        if pose == "leap":
            dangle = 3 * math.sin(t * 3)
            wx += 20 * math.sin(t * 1.4) * tl.prog("b_grow", t, 0.8, 1.0)
        D.cat(c, wx + dangle, wy, D.WHISKERS, 1.0, -1, pose, t=t, mouth=tl.mouth("whiskers", t), seed=0,
              eyes=weyes if not tl.talking("whiskers", t) or pose == "leap" else "open", look=(1, 1 if pose == "leap" else 0))
    else:
        tp = T("b_pop", 0.12)
        if t < land:
            u = (t - tp) / (land - tp)
            x0 = WX + 30
            wx = lerp(x0, CUSH, ease(u))
            wy = lerp(400, PY - 30, u * u)
            D.cat(c, wx, wy, D.WHISKERS, 1.0, -1, "leap", t=t, seed=0, eyes="wide", mouth=0.5)
            dt = t - tp
            if dt < 0.35:                                   # the pop
                k = dt / 0.35
                cx, cy = x0 + 10, 400 - 140 - 115
                for j in range(12):
                    a = j * math.pi / 6
                    c.line([(cx + math.cos(a) * 60 * (0.5 + k), cy + math.sin(a) * 60 * (0.5 + k)),
                            (cx + math.cos(a) * 100 * (0.5 + k), cy + math.sin(a) * 100 * (0.5 + k))],
                           (255, 230, 120), 5)
                for j in range(6):
                    a = j * 1.1 + 0.3
                    c.ellipse(cx + math.cos(a) * 140 * k, cy + math.sin(a) * 140 * k + 200 * k * k, 9, 5, GREEN, w=1.5)
        else:
            happy = T("b_again") <= t < T("b_no")
            D.cat(c, CUSH, PY - 30 + 12 * sq, D.WHISKERS, 1.0, -1, "sit", t=t, mouth=tl.mouth("whiskers", t), seed=0,
                  eyes="happy" if happy or t >= T("b_no", 0.6) else ("closed" if t < land + 0.5 else "open"),
                  squash=1 - 0.2 * sq)
    z = ease(tl.prog("b_no", t, 0.2, 0.9))
    return S.cam(c, lerp(130, 0, z), lerp(60, 0, z), lerp(1100, 1280, z))


SCENE_FUNCS = {"party": party}
