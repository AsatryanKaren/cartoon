"""apple: under the big apple tree in the garden. The apples hang too high, so Whiskers shakes the tree:
apples rain down and one bonks him on the head (on purpose, of course). Hedgie the hedgehog shows how
he gathers apples: he rolls into a spiky ball through the fallen apples and they all stick to his
spines. Everyone heads home with lots of apples."""
import math

import draw as D
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S

GL = S.GL
TREE_X, TREE_S = 720, 0.9
LX, WX0, WX1 = 380, 540, 606          # Luna; Whiskers before / while shaking
HX = 1150                             # where Hedgie stops
BONK = 0                              # the apple that falls on Whiskers' head
# apples that fall: (index, start fraction of a_shakeit, ground x)
FALLS = [(2, 0.30, 830), (5, 0.34, 880), (9, 0.39, 930), (7, 0.44, 980), (3, 0.48, 1030), (6, 0.53, 1080),
         (10, 0.57, 800), (BONK, 0.62, 760)]
STAY = [1, 4, 8]                      # still in the tree afterwards


def apple_state(tl, t, k, f0, gx, tree_pos):
    """Position of a falling apple (or None while it is still in the tree)."""
    T = tl.t
    t0 = T("a_shakeit", f0)
    if t < t0:
        return None
    sx, sy = tree_pos(k)
    fall = 0.38
    if k == BONK:
        hx, hy = WX1 + 52, GL - 86 - 40
        if t < t0 + fall:
            u = (t - t0) / fall
            return lerp(sx, hx, u), lerp(sy, hy, u * u), 0.0
        u = clamp((t - t0 - fall) / 0.6)
        return lerp(hx, gx, u), lerp(hy, GL - 14, u) - 90 * math.sin(math.pi * u), u * 6
    if t < t0 + fall:
        u = (t - t0) / fall
        return sx, lerp(sy, GL - 14, u * u), 0.0
    u = ease(clamp((t - t0 - fall) / 0.5))
    hop = 30 * math.sin(math.pi * clamp((t - t0 - fall) / 0.25))
    return lerp(sx, gx, u), GL - 14 - hop, u * 4


def hedgie_state(tl, t):
    """x, curl, spin, face, walk, picked-x (apples with x >= it are on his spines)."""
    T = tl.t
    if t < T("a_hog_in"):
        return 1500, 0, 0, -1, 0, 9999
    if t < T("a_rolling"):
        x = S.smooth(t, [(T("a_hog_in"), 1450), (T("a_hog_in", 1), HX)], r=0.2)
        return x, 0, 0, -1, (x / 9 if t < T("a_hog_in", 1) else 0), 9999
    k = tl.prog("a_rolling", t)
    if k < 0.08:
        return HX, 0, 0, -1, 0, 9999
    if k < 0.5:                                        # roll left through the apples
        u = ease((k - 0.08) / 0.42)
        x = lerp(HX, 735, u)
        return x, 1, -(HX - x) / 46, -1, 0, x - 20
    if k < 0.78:                                       # and back again
        u = ease((k - 0.5) / 0.28)
        x = lerp(735, 1000, u)
        return x, 1, -(HX - 735) / 46 + (x - 735) / 46, 1, 0, 0
    if t < T("a_exit", 0.2):
        return 1000, 0, 0, -1, 0, 0
    x = S.smooth(t, [(T("a_exit", 0.2), 1000), (T("a_exit", 1), 330)], r=0.2)
    return x, 0, 0, -1, x / 9, 0


def orchard(tl, t):
    T = tl.t
    c = Canvas(S.orchard_bg().copy())
    shake = 0.0
    if T("a_shakeit", 0.12) <= t < T("a_shakeit", 0.72):
        shake = min(1.0, tl.prog("a_shakeit", t, 0.12, 0.2)) * (1 - tl.prog("a_shakeit", t, 0.66, 0.72))
    # which apples are still up in the tree
    up = list(STAY) + [k for k, f0, _ in FALLS if t < T("a_shakeit", f0)]
    tree_pos = S.apple_tree(c, TREE_X, GL, TREE_S, t, shake, apples=up)
    # fallen apples (on the ground until Hedgie rolls over them)
    hx, curl, spin, hface, hwalk, picked = hedgie_state(tl, t)
    n_on = 0
    for k, f0, gx in FALLS:
        p = apple_state(tl, t, k, f0, gx, tree_pos)
        if p is None:
            continue
        if t >= T("a_rolling") and gx >= picked:
            n_on += 1
            continue
        S.apple(c, p[0], p[1], 14)
    # ---- Luna
    lx = S.smooth(t, [(0, -220), (T("a_arrive", 0.9), LX), (T("a_exit", 0.1), LX), (T("a_exit", 1), -250)])
    lmov = t < T("a_arrive", 0.95) or t > T("a_exit", 0.1)
    leyes = "open"
    if T("a_shakeit", 0.72) <= t < T("a_bonk", 0.6):
        leyes = "wide"
    if T("a_rolling", 0.82) <= t < T("a_exit") or T("a_purpose", 0.5) <= t < T("a_hog_in"):
        leyes = "happy"
    llook = (1, -1) if T("a_high") <= t < T("a_shakeit", 0.7) else (1, 0.1)
    D.cat(c, lx, GL, D.LUNA, 1.0, -1 if t > T("a_exit", 0.1) else 1, "walk" if lmov else "stand",
          walk=lx / 12 if lmov else 0, t=t, mouth=tl.mouth("luna", t), seed=1.3, eyes=leyes, look=llook)
    # ---- Whiskers
    T0 = T("a_shakeit")
    wx = S.smooth(t, [(0, -100), (T("a_arrive", 0.9), WX0), (T0, WX0), (T("a_shakeit", 0.12), WX1),
                      (T("a_exit"), WX1), (T("a_exit", 0.9), -150)], r=0.2)
    moving = t < T("a_arrive", 0.95) or T0 <= t < T("a_shakeit", 0.12) or t > T("a_exit")
    face = -1 if t > T("a_exit") else 1
    eyes, squash, look = "open", 1.0, (1, 0.1)
    if T("a_high") <= t < T("a_shake"):
        look = (1, -1)
    if T("a_shakeit", 0.12) <= t < T("a_shakeit", 0.72):
        wx += 5 * math.sin(t * 31)
        eyes = "closed"
    bonk_t = T("a_shakeit", 0.62) + 0.38
    if bonk_t <= t < T("a_purpose"):
        squash = 1 - 0.22 * max(0.0, 1 - (t - bonk_t) / 0.25)
        eyes = "closed" if t < T("a_bonk", 0.5) else "wide"
    if T("a_purpose", 0.4) <= t < T("a_hog_in"):
        eyes = "happy"
    if T("a_rolling", 0.82) <= t < T("a_go", 1):
        eyes = "happy"
    D.cat(c, wx, GL, D.WHISKERS, 1.0, face, "walk" if moving else "stand", walk=abs(wx) / 12 if moving else 0,
          t=t, mouth=tl.mouth("whiskers", t), seed=0, eyes=eyes, look=look, squash=squash)
    if bonk_t <= t < T("a_exit", 0.6):
        hx_, hy_ = wx + 52 * face, GL - 86 * squash - 30
        c.ellipse(hx_ - 2, hy_, 11, 8, (255, 150, 160), w=2)         # the bump
        if t < T("a_purpose"):
            S.dizzy_stars(c, hx_, hy_ - 6, t)
    # ---- Hedgie
    if hx < 1450 or t >= T("a_hog_in"):
        heyes = "happy" if (T("a_hog") <= t < T("a_hog", 0.3) or t >= T("a_rolling", 0.82)) else "open"
        hop = 0.0
        if T("a_rolling", 0.78) <= t < T("a_rolling", 0.95):
            hop = 40 * math.sin(math.pi * tl.prog("a_rolling", t, 0.78, 0.95))
        S.hedgehog(c, hx, GL, 1.15, hface, t, mouth=tl.mouth("hedgie", t), eyes=heyes, walk=hwalk, curl=curl,
                   spin=spin, apples=n_on, hop=hop, seed=0.4)
        if curl:
            for k in range(3):                            # dust puffs behind the rolling ball
                u = ((t * 2.2) + k / 3) % 1.0
                c.circle(hx - hface * (50 + 40 * u), GL - 10 - 10 * u, 8 + 10 * u, (236, 226, 200), ol=None)
    # sparkles on the apples Hedgie carries
    k = tl.prog("a_rolling", t, 0.8, 1.0)
    if 0 < k < 1:
        for j in range(3):
            S.sparkle(c, 960 + j * 40, GL - 110 - 10 * j, 14 * math.sin(math.pi * k))
    return S.cam(c, 180, 90, 1060)


SCENE_FUNCS = {"orchard": orchard}
