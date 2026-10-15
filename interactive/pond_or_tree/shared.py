"""Shared drawing, music and sounds for the interactive story "Whiskers and the Lost Ball".

Every clip in clips/<id>/ imports from here. Highlights:

* cat_front(): Whiskers (or Luna) facing the camera, used whenever Whiskers talks to the child.
* closeup(): the question shot. Its idle motion is periodic (2 s; blinks every 4 s) and keyed to
  a phase `ph`, so the end of a talking clip flows into the 4 s listen loop and back out again.
* Backdrops for Q1 (pond on the left, big tree on the right) and Q2 (boat left, balloon right).
* The garden at home, the day pond, the big climbing tree, the lake with the island, a rowboat.
"""
import math

import numpy as np
from PIL import ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from audio import MAJ, MIN, TAU, band, env_adsr, place, SR
from films.moonfish.scenes import cached, view, smooth, track, actor, arc_y, PAL, SEED  # noqa: F401
from films.venice.props import balloon as _venice_balloon
from films.london.props import robin, nest  # noqa: F401
from films.copenhagen.props import duck  # noqa: F401

BALL = (226, 52, 52)
BALL_D = (176, 30, 36)
STAR = (255, 222, 90)
SKY = [(0, (112, 186, 245)), (0.62, (206, 234, 255)), (1, (206, 234, 255))]
SUNSET = [(0, (96, 92, 170)), (0.4, (236, 146, 128)), (0.62, (255, 204, 140)), (1, (255, 204, 140))]
GRASS, GRASS_D, GRASS_L = (118, 190, 92), (96, 166, 80), (150, 210, 120)
WATER, WATER_D, WATER_L = (84, 160, 210), (60, 130, 186), (170, 220, 245)
LEAF, LEAF_D, LEAF_L = (86, 160, 80), (64, 128, 66), (120, 190, 100)
TRUNK, TRUNK_D = (140, 96, 62), (110, 72, 46)
EVENING = ((255, 150, 110), 0.18)       # canvas tint for sunset scenes


# ================================================================== sounds

def sfx_boing(rng):
    d = 0.6
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 160 + 260 * np.exp(-t * 5) + 40 * np.sin(TAU * 14 * t) * np.exp(-t * 3)
    x = np.sin(TAU * np.cumsum(f) / SR) + 0.3 * np.sin(2 * TAU * np.cumsum(f) / SR)
    return x * env_adsr(n, 0.005, 0.15, 3.0) * 0.6


def sfx_tweet(rng):
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        d = 0.12
        n = int(d * SR)
        t = np.arange(n) / SR
        f = 3200 + 1400 * np.sin(np.pi * t / d) + rng.uniform(-200, 200)
        x = np.sin(TAU * np.cumsum(f) / SR) * env_adsr(n, 0.01, 0.04)
        place(out, k * 0.17, x, 0.5)
    return out


def sfx_flame(rng):
    d = 1.2
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 80, 1800) * env_adsr(n, 0.08, 0.4)
    return x / (np.abs(x).max() + 1e-9) * 0.6 * (0.8 + 0.2 * np.sin(TAU * 9 * t))


def sfx_plip(rng):
    d = 0.35
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 600 * (1 + 2 * t / d)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 18)
    x += band(rng.standard_normal(n), 400, 3000) * np.exp(-t * 25) * 0.4
    return x * 0.6


def sfx_pop(rng):
    d = 0.25
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 900 - 500 * t / d
    return np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 20) * 0.6


EXTRA_SFX = {"boing": (sfx_boing, 0.55), "tweet": (sfx_tweet, 0.4), "flame": (sfx_flame, 0.5),
             "plip": (sfx_plip, 0.45), "pop": (sfx_pop, 0.45)}

# ================================================================== music

MOODS = {
    "play":   dict(bpm=116, prog=[(60, MAJ), (65, MAJ), (57, MIN), (55, MAJ)], drums=True, mel=0.7, oct=72, vol=0.8),
    "ask":    dict(bpm=72, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.25, oct=77, vol=0.55),
    "pondday": dict(bpm=96, prog=[(55, MAJ), (52, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.55, oct=79, vol=0.75),
    "climb":  dict(bpm=108, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.6, oct=74, vol=0.75),
    "river":  dict(bpm=88, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.45, oct=76, vol=0.7),
    "sail":   dict(bpm=104, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=True, mel=0.6, oct=77, vol=0.75),
    "fly":    dict(bpm=84, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.55, oct=79, vol=0.7),
    "home":   dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}

# ================================================================== props


def ball(c, x, y, r=22, spin=0.0):
    """The big red ball; (x, y) = centre."""
    c.circle(x, y, r, BALL)
    c.ellipse(x, y + r * 0.35, r * 0.9, r * 0.55, BALL_D, ol=None)
    c.circle(x, y, r, None)
    # a yellow star that turns with the spin
    pts = []
    for k in range(10):
        a = spin + k * math.pi / 5 - math.pi / 2
        rr = r * (0.42 if k % 2 == 0 else 0.18)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, STAR, w=1.2)
    c.ellipse(x - r * 0.4, y - r * 0.45, r * 0.25, r * 0.16, (255, 190, 190), ol=None)


def big_tree(c, x, base, s=1.0, t=0.0, apples=False):
    """The big tree (local: trunk at 0, ground at 0). ~560 tall at s=1."""
    c.push(x, base, s)
    c.poly([(-46, 0), (-34, -60), (-30, -260), (30, -260), (34, -60), (50, 0), (70, 6), (-72, 6)], TRUNK)
    c.line([(-6, -30), (-10, -200)], TRUNK_D, 4, cap=False)
    c.line([(14, -60), (18, -180)], TRUNK_D, 3, cap=False)
    c.stroke([(-20, -230), (-110, -300)], TRUNK, 20)
    c.stroke([(20, -220), (120, -310)], TRUNK, 22)
    sway = 3 * math.sin(t * math.pi)
    blobs = [(-150, -330, 90), (150, -340, 92), (-70, -440, 105), (80, -450, 108), (0, -540, 95),
             (-190, -420, 70), (200, -430, 72), (0, -350, 100)]
    for dx, dy, r in blobs:
        c.circle(dx + sway * (-dy / 500), dy, r, LEAF)
    for dx, dy, r in blobs:
        c.circle(dx + sway * (-dy / 500), dy, r - 6, LEAF, ol=None)
    for dx, dy, r in ((-90, -470, 46), (60, -500, 40), (150, -360, 40), (-150, -360, 40)):
        c.circle(dx + sway * (-dy / 500), dy, r, LEAF_L, ol=None)
    if apples:
        for dx, dy in ((-120, -320), (110, -400), (-30, -420), (170, -300), (40, -560), (-200, -430)):
            c.circle(dx + sway * (-dy / 500), dy, 9, (230, 70, 60), w=2)
    c.pop()


def reeds(c, x, y, s=1.0, t=0.0, n=4):
    for k in range(n):
        dx = (k - n / 2) * 14 * s
        sw = 3 * math.sin(t * math.pi + k)
        h = (120 + 20 * (k % 2)) * s
        c.line([(x + dx, y), (x + dx + sw - 6 * s, y - h)], (60, 120, 70), 4 * s, cap=False)
        c.ellipse(x + dx + sw - 6 * s, y - h + 18 * s, 5 * s, 16 * s, (130, 86, 56), ol=None)


def rowboat(c, x, y, s=1.0, face=1, bob=0.0, inside=None, oar=None):
    """Pip's little red rowboat. (x, y) = waterline centre. inside(c) draws the crew in local
    coordinates (seats at y about -30). oar = angle of the oars (radians) or None."""
    c.push(x, y + bob, s, flip=face < 0)
    c.line([(-118, -40), (126, -46)], mix((200, 70, 60), OUT, 0.4), 6)      # far rim
    if inside:
        inside(c)
    if oar is not None:
        for side in (1,):
            ax, ay = 0, -42
            ex, ey = ax - 40 + 150 * math.cos(oar), ay + 40 + 30 * math.sin(oar)
            c.line([(ax, ay), (ex, ey)], OUT, 8)
            c.line([(ax, ay), (ex, ey)], (210, 160, 100), 4)
            c.ellipse(ex, ey, 18, 7, (210, 160, 100), w=2)
    hull = [(-130, -44), (134, -50), (110, -6), (80, 8), (-90, 8), (-118, -10)]
    c.poly(hull, (214, 72, 62), w=3)
    c.poly([(-126, -36), (130, -42), (124, -30), (-122, -26)], (250, 246, 236), ol=None)
    c.text(10, -12, "PIP", 16, (255, 236, 160))
    c.pop()


def balloon(c, x, y, s=1.0, t=0.0, flame=0.0, inside=None):
    """Pip's hot-air balloon (the Venice one, in red & yellow, no sign). (x, y) = basket bottom."""
    _venice_balloon(c, x, y, s, t, flame=flame, sign=False, inside=inside,
                    cols=((232, 80, 72), (255, 214, 92)))


def water_glints(c, x0, x1, y0, y1, ph, n=26, seed=4, col=WATER_L):
    """Sparkles on water; periodic with period 2 s in ph."""
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        a = 0.5 + 0.5 * math.sin(math.pi * ph + k * 1.7)
        c.line([(x - 10 * a - 4, y), (x + 10 * a + 4, y)], col, 2.5, cap=False)


def sparkle(c, x, y, r, col=(255, 250, 200)):
    c.poly([(x, y - r), (x + r * 0.25, y - r * 0.25), (x + r, y), (x + r * 0.25, y + r * 0.25),
            (x, y + r), (x - r * 0.25, y + r * 0.25), (x - r, y), (x - r * 0.25, y - r * 0.25)], col, w=1.5)


# ================================================================== the front-facing cat

def blink4(ph):
    """Blink every 4 s (period-4 safe for the listen loop)."""
    return 2.0 <= ph % 4.0 < 2.14


def cat_front(c, x, y, pal, s=1.0, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), ear=0.0, tilt=0.0,
              paw_l=None, paw_r=None, breath=0.0, blink=False, ball_hug=False):
    """A cat facing the camera, from the chest up. (x, y) = bottom of the chest.
    paw_l / paw_r: (px, py) local targets for a raised paw (viewer's left / right), or None.
    ear: 0..1 raises the viewer's-right ear (listening). tilt: head tilt in degrees."""
    if eyes == "open" and blink:
        eyes = "closed"
    body, dark, belly, earc = pal["body"], pal["dark"], pal["belly"], pal["ear"]
    c.push(x, y, s)
    k = 1 + 0.012 * breath
    # chest
    c.ellipse(0, -40, 150 * k, 150 * k, body)
    c.ellipse(0, -10, 86 * k, 120 * k, belly, ol=None)
    if pal["stripes"]:
        for sx in (-1, 1):
            for dy in (-120, -90, -60):
                c.line([(sx * 150 * k * 0.86, dy), (sx * 112, dy + 12)], dark, 7)
    piv = (0, -175)
    a = math.radians(tilt)

    def R(px, py):
        dx, dy = px - piv[0], py - piv[1]
        return piv[0] + dx * math.cos(a) - dy * math.sin(a), piv[1] + dx * math.sin(a) + dy * math.cos(a)

    def E(px, py, rx, ry, fill, ol=OUT, w=3):
        qx, qy = R(px, py)
        c.ellipse(qx, qy, rx, ry, fill, ol, w)

    def Pg(pts, fill, ol=OUT, w=3):
        c.poly([R(px, py) for px, py in pts], fill, ol, w)

    def L(pts, fill, w=3):
        c.line([R(px, py) for px, py in pts], fill, w, cap=False)

    # collar (Luna)
    if pal["collar"]:
        c.rect(-74, -192, 74, -172, pal["collar"], w=3, r=8)
        c.circle(0, -160, 13, (250, 210, 70), w=2.5)
        c.line([(-6, -160), (6, -160)], OUT, 2, cap=False)
    # ears
    er = ear
    Pg([(-128, -318), (-104, -446), (-42, -384)], body)
    Pg([(-114, -330), (-100, -424), (-58, -380)], earc, ol=None)
    tip = (104 + 14 * er, -446 - 38 * er)
    Pg([(42, -384), tip, (128, -318)], body)
    Pg([(58, -380), (tip[0] - 4, tip[1] + 22), (114, -330)], earc, ol=None)
    # head + cheek fluff
    Pg([(-128, -250), (-162, -226), (-130, -214), (-150, -192), (-110, -200)], body)
    Pg([(128, -250), (162, -226), (130, -214), (150, -192), (110, -200)], body)
    E(0, -290, 142, 122, body)
    if pal["stripes"]:
        for dx in (-26, 0, 26):
            L([(dx, -408), (dx * 0.8, -372)], dark, 9)
        for sx in (-1, 1):
            L([(sx * 140, -300), (sx * 112, -296)], dark, 7)
            L([(sx * 138, -270), (sx * 114, -272)], dark, 7)
    # muzzle
    E(-26, -236, 34, 25, belly, ol=None)
    E(26, -236, 34, 25, belly, ol=None)
    E(0, -224, 26, 18, belly, ol=None)
    # eyes
    lx, ly = look
    for sx in (-1, 1):
        ex, ey = R(sx * 54, -300)
        if eyes == "closed":
            c.arc(ex, ey + 2, 22, 12, 20, 160, OUT, 4)
        elif eyes == "happy":
            c.arc(ex, ey + 10, 22, 20, 200, 340, OUT, 4.5)
        else:
            big = 1.15 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 27 * big, 32 * big, (255, 255, 255), w=3)
            ix, iy = ex + lx * 8, ey + ly * 8
            c.ellipse(ix, iy, 20 * big, 25 * big, pal["eye"], ol=None)
            c.ellipse(ix, iy, 9 * big, 19 * big, (25, 20, 25), ol=None)
            c.circle(ix + 7, iy - 9, 6, (255, 255, 255), ol=None)
            c.circle(ix - 6, iy + 9, 2.5, (255, 255, 255), ol=None)
    # nose
    Pg([(-15, -262), (15, -262), (0, -246)], D.NOSE, w=2)
    # mouth
    if mouth > 0.05:
        h = 8 + 26 * mouth
        mx, my = R(0, -226 + h * 0.5)
        c.ellipse(mx, my, 16 + 6 * mouth, h, D.MOUTH, w=2.5)
        tx, ty = R(0, -226 + h * 0.85)
        c.ellipse(tx, ty, 10, 4 + 4 * mouth, D.TONGUE, ol=None)
    else:
        for sx in (-1, 1):
            cx, cy = R(sx * 10, -240)
            c.arc(cx, cy, 10, 8, 10, 170, OUT, 3)
    # whiskers
    for sx in (-1, 1):
        for dy in (-8, 4, 16):
            L([(sx * 52, -238 + dy * 0.4), (sx * 128, -246 + dy * 1.6)], OUT, 2)
    # paws
    if ball_hug:
        ball(c, 0, -60, 58, 0.3)
        for sx in (-1, 1):
            c.ellipse(sx * 52, -40, 30, 24, body)
            for k2 in (-1, 0, 1):
                c.line([(sx * 52 + k2 * 10, -30), (sx * 52 + k2 * 10, -20)], OUT, 2, cap=False)
    for sx, paw in ((-1, paw_l), (1, paw_r)):
        if paw is None:
            continue
        sh = (sx * 104, -110)
        c.stroke([sh, (lerp(sh[0], paw[0], 0.5), lerp(sh[1], paw[1], 0.5) + 10), paw], body, 46)
        c.ellipse(paw[0], paw[1], 32, 28, body)
        c.ellipse(paw[0], paw[1] + 6, 14, 10, earc, ol=None)
        for k2 in (-1, 0, 1):
            c.circle(paw[0] + k2 * 13, paw[1] - 12, 5, earc, ol=None)
    c.pop()


# ================================================================== the question close-up

def listen_amount(t, t_on=None, t_off=None, dur=0.5):
    """0..1 how far into the listening pose (ear up, paw at ear)."""
    k = 1.0
    if t_on is not None:
        k = min(k, ease((t - t_on) / dur))
    if t_off is not None:
        k = min(k, 1 - ease((t - t_off) / dur))
    return clamp(k)


def closeup(bg, t, ph, listen=0.0, mouth=0.0, point=0.0, look=None, eyes="open", happy=0.0, lean=0.0):
    """The question shot: Whiskers facing the viewer in front of a backdrop.

    ph: idle phase (seconds); all idle motion is periodic in it (2 s, blinks 4 s).
    listen: 0..1 listening pose (ear up, head tilt, paw cupped at the ear, sound arcs).
    point: -1 = paw points to the left option, +1 = to the right option, 0 = none.
    """
    c = Canvas(bg.copy())
    w2 = math.sin(math.pi * ph)                 # period 2 s
    bob = 4 * w2
    ear = listen
    tilt = 7 * listen + 1.5 * listen * w2
    lk = look if look is not None else (0.9 * point, -0.2 * abs(point))
    paw_l = paw_r = None
    if point < -0.02:
        u = ease(-point)
        paw_l = (lerp(-110, -240, u), lerp(-40, -250, u) + 3 * w2)
    if point > 0.02:
        u = ease(point)
        paw_r = (lerp(110, 240, u), lerp(-40, -250, u) + 3 * w2)
    if listen > 0.02:
        u = ease(listen)
        paw_r = (lerp(110, 168, u), lerp(-40, -352, u) + 2 * w2)
    x, y, s = 640, 772 + bob * 0.5 + 20 * lean, 1.12 + 0.06 * lean
    cat_front(c, x, y, D.WHISKERS, s, t, mouth=mouth, eyes="happy" if happy > 0.5 else eyes, look=lk,
              ear=ear, tilt=tilt, paw_l=paw_l, paw_r=paw_r, breath=w2, blink=blink4(ph))
    if listen > 0.3:
        # little sound arcs flowing into the raised ear, period 2 s
        a = clamp((listen - 0.3) / 0.7)
        ex, ey = x + 150 * s, y - 470 * s
        for k in range(3):
            u = ((ph / 2.0) + k / 3) % 1.0
            r = lerp(60, 24, u)
            col = mix((255, 255, 255), (255, 240, 170), u)
            vis = math.sin(math.pi * u) * a
            if vis > 0.08:
                c.arc(ex + 70 + 110 * (1 - u), ey + 20, r, r * 1.2, 120, 240, mix(OUT, col, 0.4 + 0.6 * vis),
                      3 + 3 * vis)
    return c


def q1_backdrop():
    """Garden behind Whiskers: the pond on the left, the big tree on the right (soft focus)."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, SKY))
        D.cloud(c, 240, 110, 0.9)
        D.cloud(c, 800, 80, 0.7)
        pts = [(x, 400 + 30 * math.sin(x / 210)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (150, 205, 130), ol=None)
        c.rect(0, 470, W, H, GRASS, ol=None)
        c.rect(0, 560, W, H, GRASS_D, ol=None)
        # the pond (left)
        c.ellipse(230, 560, 250, 74, WATER, ol=(50, 96, 120), w=4)
        c.ellipse(230, 548, 200, 46, mix(WATER, WATER_L, 0.35), ol=None)
        for px, py, r in ((130, 560, 30), (300, 580, 26), (360, 540, 20)):
            D.lily_pad(c, px, py, r)
        D.frog(c, 300, 578, 1.1, -1, 0.5)
        reeds(c, 450, 560, 1.0, 0, 5)
        reeds(c, 40, 560, 0.9, 0.7, 4)
        D.flower(c, 470, 620, (250, 140, 180))
        # the big tree (right)
        big_tree(c, 1090, 560, 0.95)
        D.bush(c, 880, 560, 0.8)
        for x in range(520, 760, 60):
            D.flower(c, x, 600 + (x % 3) * 12, (255, 230, 90), 0.8)
        img = c.img.filter(ImageFilter.GaussianBlur(1.6 * SS))
        return img
    return cached("q1_bg", make)


def q2_backdrop():
    """The lake behind Whiskers: the rowboat on the left, the balloon on the right, the island far off."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, SKY))
        D.cloud(c, 980, 90, 0.8)
        D.cloud(c, 200, 70, 0.6)
        pts = [(x, 330 + 26 * math.sin(x / 170 + 1)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (130, 180, 140), ol=None)
        c.rect(0, 360, W, H, WATER, ol=None)
        for k in range(8):
            c.line([(0, 380 + k * 22), (W, 380 + k * 22)], mix(WATER, WATER_L, 0.25), 2, cap=False)
        # island far away, with the tiny red ball
        c.ellipse(900, 396, 110, 22, (214, 196, 140), ol=(120, 100, 70), w=2)
        c.ellipse(900, 390, 80, 14, (130, 190, 100), ol=None)
        D.tree(c, 860, 392, 0.28)
        ball(c, 940, 378, 11)
        # near shore
        c.poly([(0, 560), (W, 600), (W, H), (0, H)], GRASS, ol=None)
        c.poly([(0, 620), (W, 650), (W, H), (0, H)], GRASS_D, ol=None)
        # boat (left) moored at a post
        c.rect(320, 470, 334, 600, TRUNK, w=2.5)
        c.line([(327, 500), (260, 520)], (150, 120, 80), 3, cap=False)
        rowboat(c, 200, 540, 1.05)
        reeds(c, 380, 590, 0.9, 0, 4)
        # balloon (right) on the grass
        balloon(c, 1100, 640, 0.95)
        img = c.img.filter(ImageFilter.GaussianBlur(1.6 * SS))
        return img
    return cached("q2_bg", make)


# ================================================================== home garden

GW, GY = 2200, 600        # garden world width and ground line
HOUSE_X = 640
STREAM_X = 1700           # the garden ends at a stream here


def garden_bg(sunset=False):
    def make():
        c = Canvas(D.gradient(GW * SS, H * SS, SUNSET if sunset else SKY), size=(GW, H))
        rng = np.random.default_rng(7)
        if not sunset:
            for x in range(200, GW, 560):
                D.cloud(c, x + rng.uniform(-60, 60), rng.uniform(70, 150), rng.uniform(0.6, 1.0))
        else:
            c.circle(1900, 330, 70, (255, 226, 150), ol=None)
        pts = [(x, 420 + 36 * math.sin(x / 260)) for x in range(0, GW + 50, 50)]
        c.poly(pts + [(GW, H), (0, H)], (150, 200, 130) if not sunset else (170, 150, 140), ol=None)
        for x in range(500, GW, 470):
            D.tree(c, x + rng.uniform(-60, 60), 470, rng.uniform(0.6, 0.85))
        c.rect(0, GY - 40, STREAM_X + 40, H, GRASS, ol=None)
        c.rect(0, GY + 30, STREAM_X + 40, H, GRASS_D, ol=None)
        # the stream at the end of the garden
        c.poly([(STREAM_X + 40, GY - 40), (STREAM_X + 80, GY - 10), (STREAM_X + 60, H), (GW, H), (GW, GY - 40)],
               WATER, ol=None)
        c.poly([(STREAM_X + 20, GY - 40), (STREAM_X + 50, GY + 20), (STREAM_X + 30, H), (STREAM_X - 10, H),
                (STREAM_X - 10, GY - 40)], GRASS_D, ol=None)
        for k in range(6):
            yy = GY - 20 + k * 24
            c.line([(STREAM_X + 120, yy), (GW, yy)], mix(WATER, WATER_L, 0.3), 2, cap=False)
        # a little jetty
        c.rect(STREAM_X - 40, GY - 6, STREAM_X + 150, GY + 8, (170, 120, 80), w=2.5)
        for px in (STREAM_X + 60, STREAM_X + 140):
            c.rect(px - 6, GY + 6, px + 6, GY + 60, TRUNK_D, w=2)
        # house
        hx = HOUSE_X
        c.rect(hx, 250, hx + 380, GY - 10, (250, 226, 196), w=3)
        c.poly([(hx - 30, 258), (hx + 190, 120), (hx + 410, 258)], (196, 90, 70), w=3)
        c.rect(hx + 250, 130, hx + 290, 200, (170, 90, 70), w=2.5)
        c.rect(hx + 40, 400, hx + 130, GY - 10, (150, 96, 70), w=3, r=6)
        c.circle(hx + 116, 500, 5, (250, 210, 70), w=1.5)
        # the windowsill window
        c.rect(hx + 190, 320, hx + 340, 450, (140, 196, 236) if not sunset else (255, 210, 140), w=4)
        c.line([(hx + 265, 320), (hx + 265, 450)], (250, 250, 250), 5, cap=False)
        c.line([(hx + 190, 385), (hx + 340, 385)], (250, 250, 250), 5, cap=False)
        c.rect(hx + 176, 446, hx + 354, 462, (255, 250, 240), w=2.5, r=3)
        for dx in (-30, 0, 30):
            D.flower(c, hx + 265 + dx, 446, (250, 120, 150), 0.7)
        # bushes, flowers, fence posts
        for x in list(range(80, HOUSE_X - 60, 260)) + list(range(HOUSE_X + 480, STREAM_X - 100, 300)):
            D.bush(c, x + rng.uniform(-40, 40), GY - 34, rng.uniform(0.7, 1.0))
        cols = [(250, 120, 150), (255, 230, 90), (180, 140, 250), (255, 255, 255)]
        for _ in range(110):
            D.flower(c, rng.uniform(0, STREAM_X - 20), rng.uniform(GY - 10, H - 6), cols[rng.integers(4)],
                     rng.uniform(0.55, 0.9))
        return c.img
    return cached(("garden", sunset), make)


# ================================================================== lake with the island

LW_, LY = 2600, 600       # lake world width, bank ground line
BANK_X = 520              # left bank ends here; water beyond
ISLAND = (2150, 610)      # island centre (waterline)


def lake_bg():
    def make():
        c = Canvas(D.gradient(LW_ * SS, H * SS, SKY), size=(LW_, H))
        rng = np.random.default_rng(9)
        for x in range(150, LW_, 600):
            D.cloud(c, x + rng.uniform(-60, 60), rng.uniform(70, 150), rng.uniform(0.6, 1.0))
        pts = [(x, 380 + 40 * math.sin(x / 240 + 2)) for x in range(0, LW_ + 50, 50)]
        c.poly(pts + [(LW_, H), (0, H)], (130, 180, 140), ol=None)
        for x in range(100, LW_, 260):
            D.tree(c, x + rng.uniform(-40, 40), 420, rng.uniform(0.35, 0.5), leaf=(100, 160, 110))
        c.rect(0, 440, LW_, H, WATER, ol=None)
        for k in range(10):
            yy = 460 + k * 26
            c.line([(0, yy), (LW_, yy)], mix(WATER, WATER_L, 0.22), 2, cap=False)
        # island
        ix, iy = ISLAND
        c.ellipse(ix, iy, 190, 44, (214, 196, 140), ol=(120, 100, 70), w=3)
        c.ellipse(ix, iy - 12, 150, 30, (130, 190, 100), ol=None)
        D.tree(c, ix - 60, iy - 20, 0.6)
        D.bush(c, ix + 90, iy - 14, 0.5)
        # left bank
        c.poly([(0, LY - 40), (BANK_X, LY - 40), (BANK_X + 50, LY + 10), (BANK_X + 20, H), (0, H)], GRASS, w=3)
        c.poly([(0, LY + 30), (BANK_X + 30, LY + 30), (BANK_X + 20, H), (0, H)], GRASS_D, ol=None)
        for x in range(30, BANK_X, 90):
            D.flower(c, x + rng.uniform(-20, 20), LY + rng.uniform(0, 80), (255, 255, 255), 0.7)
        reeds(c, BANK_X + 40, LY + 30, 1.0, 0, 4)
        return c.img
    return cached("lake", make)


def lake_view(camx):
    return view(lake_bg(), camx)


# ================================================================== close-up helpers for clips

def word_time(tl, eid, word):
    """Rough time a word is spoken inside a line (by its position in the text)."""
    e = tl.ev(eid)
    i = e.text.lower().find(word.lower())
    return e.start + e.dur * max(0, i) / max(1, len(e.text))


def point_track(tl, t, cues, hold_end):
    """cues: [(time, side)], side -1/+1. Returns the point value (eased), 0 after hold_end."""
    v = 0.0
    for k, (t0, side) in enumerate(cues):
        t1 = cues[k + 1][0] if k + 1 < len(cues) else hold_end
        if t0 - 0.3 <= t < t1:
            up = ease((t - t0 + 0.3) / 0.35)
            down = 1 - ease((t - t1 + 0.3) / 0.3) if k + 1 == len(cues) else 1.0
            v = side * min(up, down)
    return v
