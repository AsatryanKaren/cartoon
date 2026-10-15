"""pond: Whiskers and Luna search the pond. Whiskers looks in the water "very carefully" and falls in
(on purpose, of course); the frog saw the ball bounce on its lily pad and roll down to the river; round
tracks in the mud lead away. They hop across the lily pads and run off to the right, toward the river."""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, mix
from interactive.pond_or_tree import shared as S

GL = 580                                   # bank ground line
PADS = [(450, 604), (600, 616), (760, 604), (890, 614)]
FROG = (600, 612)
FROG2 = (890, 610)


def bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, S.SKY))
        D.cloud(c, 260, 110, 0.9)
        D.cloud(c, 980, 80, 0.7)
        pts = [(x, 420 + 34 * math.sin(x / 200 + 0.5)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (150, 205, 130), ol=None)
        for x in (120, 380, 1150):
            D.tree(c, x, 470, 0.6)
        c.rect(0, 480, W, H, S.GRASS, ol=None)
        # the water
        c.ellipse(650, 600, 440, 110, S.WATER, ol=(50, 96, 120), w=4)
        c.rect(300, 600, 1000, H, S.WATER, ol=None)
        for k in range(7):
            y = 530 + k * 26
            c.line([(330, y), (980, y)], mix(S.WATER, S.WATER_L, 0.25), 2, cap=False)
        # banks
        c.poly([(0, GL - 10), (300, GL - 6), (350, GL + 30), (330, H), (0, H)], S.GRASS, w=3)
        c.rect(0, GL + 40, 320, H, S.GRASS_D, ol=None)
        c.poly([(W, GL - 10), (990, GL - 6), (950, GL + 30), (970, H), (W, H)], S.GRASS, w=3)
        c.rect(975, GL + 40, W, H, S.GRASS_D, ol=None)
        c.ellipse(1110, GL + 16, 150, 18, (150, 116, 84), ol=None)
        # round little tracks in the mud, leading off to the right (toward the river)
        for k in range(8):
            x = 985 + k * 30
            y = GL + 14 + 8 * math.sin(k * 1.3)
            c.ellipse(x, y, 11, 6, (96, 70, 52), ol=None)
        S.reeds(c, 330, GL + 20, 1.0, 0, 4)
        S.reeds(c, 975, GL + 30, 0.9, 0.5, 3)
        for x in (60, 170, 240):
            D.flower(c, x, GL + 60, (250, 140, 180))
        return c.img
    return S.cached("pond_day", make)


def hops(t, t0, path, dt=0.45):
    """Hop along a list of x positions starting at t0; returns (x, lift, airborne)."""
    if t < t0:
        return path[0], 0.0, False
    k = int((t - t0) / dt)
    if k >= len(path) - 1:
        return path[-1], 0.0, False
    u = (t - t0) / dt - k
    return lerp(path[k], path[k + 1], u), -S.arc_y(u, 70), True


def pad_y(x):
    for px, py in PADS:
        if abs(x - px) < 50:
            return py - 6
    return GL


def pond(tl, t):
    T = tl.t
    c = Canvas(bg().copy())
    ph = t
    # duck swimming at the back
    dx = 700 + 120 * math.sin(t * 0.5)
    S.duck(c, dx, 566, 1.0, 1 if math.cos(t * 0.5) > 0 else -1, t, swim=True,
           laugh=1.0 if T("p_laugh") <= t < T("p_frog") else 0.0)
    for x, y in PADS:
        D.lily_pad(c, x, y, 44)
    S.water_glints(c, 340, 980, 640, 700, ph, n=10)
    laughing = T("p_laugh") <= t < T("p_frog")
    # frogs (they duck when a cat hops over)
    croak = tl.mouth("frog", t)
    D.frog(c, FROG[0], FROG[1], 1.3, -1 if t < T("p_clue", 0.3) else 1, t, croak, laugh=laughing, seed=0.4)
    D.frog(c, FROG2[0], FROG2[1], 1.0, -1, t, 0.0, laugh=laughing, seed=1.9)

    # ---- Luna
    lpath = [75, 450, 600, 760, 890, 1060]
    l0 = T("p_go", 0.75)
    if t < l0:
        lx = S.smooth(t, [(0, -280), (T("p_arrive", 0.85), 75)])
        moving = t < T("p_arrive", 0.95)
        D.cat(c, lx, GL, D.LUNA, 1.0, 1, "walk" if moving else "stand", walk=lx / 12 if moving else 0, t=t,
              mouth=tl.mouth("luna", t), seed=1.3, eyes="happy" if laughing else "open",
              look=(1, 0.2) if t < T("p_tracks") else (1, 0.5))
    else:
        x, lift, air = hops(t, l0, lpath)
        if x >= lpath[-1] - 1:
            x = lpath[-1] + (t - (l0 + 0.45 * (len(lpath) - 1))) * 260
        y = (pad_y(x) if 330 < x < 980 else GL) - lift
        D.cat(c, x, y, D.LUNA, 0.9 if 330 < x < 980 else 1.0, 1, "leap" if air else "walk", walk=x / 12, t=t,
              mouth=tl.mouth("luna", t), seed=1.3)

    # ---- Whiskers
    wpath = [260, 450, 600, 760, 890, 1060]
    w0 = T("p_go", 0.35)
    wet = 1.0 if t >= T("p_fall", 0.5) else 0.0
    if t < T("p_lean"):
        wx = S.smooth(t, [(0, -150), (T("p_arrive", 0.9), 250)])
        moving = t < T("p_arrive", 0.95)
        D.cat(c, wx, GL, D.WHISKERS, 1.0, 1, "walk" if moving else "stand", walk=wx / 12 if moving else 0, t=t,
              mouth=tl.mouth("whiskers", t), seed=0, look=(1, 0.3))
    elif t < T("p_fall", 0.3):
        k = tl.prog("p_lean", t)
        wob = 4 * math.sin(t * 14) * tl.prog("p_fall", t, 0, 0.3)
        D.cat(c, lerp(250, 290, ease(k)) + wob, GL, D.WHISKERS, 1.0, 1, "crouch", t=t,
              mouth=tl.mouth("whiskers", t), look=(1, 1), eyes="wide" if t > T("p_fall") else "open",
              tail=math.sin(t * 6))
    elif t < T("p_fall", 0.5):
        u = tl.prog("p_fall", t, 0.3, 0.5)
        D.cat(c, lerp(290, 420, u), GL + S.arc_y(u, 40) + 60 * u * u, D.WHISKERS, 1.0, 1, "leap", t=t,
              eyes="wide", mouth=0.6)
    elif t < T("p_laugh", 0.45):
        # splash, then swim
        dt = t - T("p_fall", 0.5)
        rng = np.random.default_rng(3)
        for k in range(18):
            ang = rng.uniform(math.pi * 1.15, math.pi * 1.85)
            sp = rng.uniform(220, 420)
            x = 420 + math.cos(ang) * sp * dt
            y = 640 + math.sin(ang) * sp * dt + 800 * dt * dt
            if y < 650:
                c.ellipse(x, y, 5, 7, (190, 225, 255), ol=None)
        for k in range(2):
            r = 40 + 200 * ((dt * 0.8 + k * 0.4) % 1.0)
            c.ellipse(420, 650, r, r * 0.22, None, ol=(170, 210, 240), w=2)
        x = 420 if t < T("p_laugh") else lerp(420, 330, tl.prog("p_laugh", t, 0, 0.45))
        D.cat(c, x, 656 + 5 * math.sin(t * 4), D.WHISKERS, 1.0, -1 if t >= T("p_laugh") else 1, "swim", t=t,
              wet=1, mouth=tl.mouth("whiskers", t), eyes="closed" if dt < 0.6 else "open")
    elif t < w0:
        u = tl.prog("p_laugh", t, 0.45, 0.75)
        x = lerp(330, 260, ease(u))
        D.cat(c, x, lerp(GL + 30, GL, ease(u)), D.WHISKERS, 1.0, 1, "stand", t=t, wet=wet,
              mouth=tl.mouth("whiskers", t), seed=0, eyes="happy" if T("p_go") <= t else "open",
              look=(1, 0.3) if t < T("p_tracks") else (1, 0.5))
    else:
        x, lift, air = hops(t, w0, wpath)
        if x >= wpath[-1] - 1:
            x = wpath[-1] + (t - (w0 + 0.45 * (len(wpath) - 1))) * 260
        y = (pad_y(x) if 330 < x < 980 else GL) - lift
        D.cat(c, x, y, D.WHISKERS, 0.9 if 330 < x < 980 else 1.0, 1, "leap" if air else "walk", walk=x / 12,
              t=t, mouth=tl.mouth("whiskers", t), seed=0, wet=wet * 0.6)
    # tracks glint when Luna spots them
    k = tl.prog("p_tracks", t, 0.0, 0.6)
    if 0 < k < 1:
        for j in range(3):
            S.sparkle(c, 1000 + j * 40, GL - 4, 14 * math.sin(math.pi * k))
    # camera: a little closer than the full set
    x0, y0, w = 20, 120, 1067
    img = c.img.crop((x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + w * 9 // 16) * SS)).resize((W * SS, H * SS))
    return Canvas(img)


SCENE_FUNCS = {"pond": pond}
