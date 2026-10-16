"""Shared drawing, music and sounds for the interactive story "Pip's Birthday Surprise".

Every clip in clips/<id>/ imports from here. The question close-up (closeup, cat_front, the listen
pose) comes unchanged from interactive/pond_or_tree/shared.py; this file adds:

* Backdrops for Q1 (apple tree on the left, beehive meadow on the right) and Q2 (balloons left,
  flowers right, in the party room).
* The kitchen, the apple orchard, the flowery meadow with the beehive, the party room.
* Props: the birthday cake, the banner ("HAPPY BIRTHDAY, PIP": ONE c.text call, see banner()),
  balloons, a vase of flowers, a watering can, a honey pot, a cushion, mixing bowl...
* Two new characters: Hedgie the hedgehog and Buzzy the bee.
"""
import math

import numpy as np
from PIL import ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from audio import MAJ, MIN, TAU, band, env_adsr, place, SR
from films.moonfish.scenes import cached, view, smooth, track, arc_y  # noqa: F401
from films.copenhagen.props import candle  # noqa: F401
from interactive.pond_or_tree import shared as P
from interactive.pond_or_tree.shared import (closeup, cat_front, blink4, listen_amount, word_time,  # noqa: F401
                                             point_track, sparkle, SKY, GRASS, GRASS_D, GRASS_L, LEAF,
                                             LEAF_D, LEAF_L, TRUNK, TRUNK_D, WATER, WATER_L)

# A translation sets WORDS = {(event_id, english_word): its_word} so animation cued on a word (pointing,
# ingredients, sparkles...) follows the translated line. Empty for English.
WORDS = {}


def word(eid, w):
    return WORDS.get((eid, w.lower()), w)


def word_time(tl, eid, w):
    """Rough time a word is spoken inside a line (by its position in the text)."""
    return P.word_time(tl, eid, word(eid, w))

APPLE, APPLE_D = (226, 58, 52), (170, 36, 36)
HONEY, HONEY_D = (250, 184, 40), (214, 140, 20)
PINK, PINK_D = (255, 160, 190), (236, 120, 160)
CREAM = (255, 246, 228)
SPONGE = (246, 206, 140)
BANNER_TEXT = "HAPPY BIRTHDAY, PIP"


# ================================================================== sounds

def sfx_bonk(rng):
    d = 0.5
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 320 * np.exp(-t * 6) + 110
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 9)
    x += band(rng.standard_normal(n), 100, 1200) * np.exp(-t * 40) * 0.6
    return x * 0.7


def sfx_knock(rng):
    d = 0.18
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 80, 900) * np.exp(-t * 45)
    x += np.sin(TAU * 140 * t) * np.exp(-t * 30) * 0.8
    return x / (np.abs(x).max() + 1e-9) * 0.7


def sfx_buzz(rng):
    d = 1.2
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 230 + 18 * np.sin(TAU * 5 * t) + 30 * np.sin(TAU * 0.8 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum(np.sin(h * ph) / h for h in range(1, 9))
    x = band(x, 150, 3000) * (0.7 + 0.3 * np.sin(TAU * 31 * t)) * env_adsr(n, 0.15, 0.3)
    return x / (np.abs(x).max() + 1e-9) * 0.35


def sfx_ding(rng):
    d = 1.4
    t = np.arange(int(d * SR)) / SR
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * k) for f, g, k in ((1568, 0.6, 3), (2349, 0.3, 4), (3136, 0.2, 6)))
    return x * np.minimum(1, t / 0.003) * 0.6


def sfx_puff(rng):
    d = 0.45
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 200, 1600) * np.sin(np.pi * t / d) ** 2
    return x / (np.abs(x).max() + 1e-9) * 0.5


def sfx_water(rng):
    d = 1.6
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 1500, 9000) * (0.6 + 0.4 * np.sin(TAU * 13 * t)) * env_adsr(n, 0.1, 0.4)
    for _ in range(18):
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        drop = np.sin(TAU * np.cumsum(rng.uniform(900, 1700) * (1 + 2 * tt / 0.05)) / SR) * np.exp(-tt * 70)
        place(x, rng.uniform(0.05, 1.4), drop * 0.2)
    return x / (np.abs(x).max() + 1e-9) * 0.4


def sfx_bang(rng):
    d = 0.6
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 100, 6000) * np.exp(-t * 18)
    x += np.sin(TAU * 90 * t) * np.exp(-t * 12) * 0.7
    return x / (np.abs(x).max() + 1e-9) * 0.8


def sfx_tada(rng):
    d = 1.6
    n = int(d * SR)
    out = np.zeros(n)
    for k, m in enumerate((72, 76, 79, 84)):
        f = 440 * 2 ** ((m - 69) / 12)
        nn = int((d - k * 0.09) * SR)
        tt = np.arange(nn) / SR
        x = (np.sin(TAU * f * tt) + 0.4 * np.sin(2 * TAU * f * tt) + 0.2 * np.sin(3 * TAU * f * tt)) * np.exp(-tt * 2.5)
        place(out, k * 0.09, x * np.minimum(1, tt / 0.005), 0.3)
    return out


def sfx_roll(rng):
    d = 1.6
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 60, 500) * (0.6 + 0.4 * np.sin(TAU * 9 * t)) * env_adsr(n, 0.1, 0.3)
    return x / (np.abs(x).max() + 1e-9) * 0.4


def sfx_stir(rng):
    d = 1.5
    n = int(d * SR)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 300, 2500) * (0.5 + 0.5 * np.sin(TAU * 2.6 * t)) ** 2 * env_adsr(n, 0.1, 0.3)
    return x / (np.abs(x).max() + 1e-9) * 0.3


EXTRA_SFX = {**P.EXTRA_SFX,
             "bonk": (sfx_bonk, 0.6), "knock": (sfx_knock, 0.7), "buzz": (sfx_buzz, 0.35),
             "ding": (sfx_ding, 0.45), "puff": (sfx_puff, 0.4), "water": (sfx_water, 0.5),
             "bang": (sfx_bang, 0.6), "tada": (sfx_tada, 0.5), "roll": (sfx_roll, 0.45),
             "stir": (sfx_stir, 0.4)}

# ================================================================== music

MOODS = {
    **P.MOODS,
    "wake":    dict(bpm=92, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.5, oct=77, vol=0.7),
    "orchard": dict(bpm=108, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=74, vol=0.75),
    "meadow":  dict(bpm=100, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=True, mel=0.6, oct=79, vol=0.75),
    "bake":    dict(bpm=104, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.55, oct=76, vol=0.75),
    "party":   dict(bpm=120, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (65, MAJ)], drums=True, mel=0.7, oct=72, vol=0.8),
}


# ================================================================== camera + small helpers

def cam(c, x0, y0, w):
    """Crop a w-wide 16:9 window at (x0, y0) of canvas c and blow it up to the full frame."""
    h = w * 9 / 16
    box = (int(round(x0 * SS)), int(round(y0 * SS)), int(round((x0 + w) * SS)), int(round((y0 + h) * SS)))
    return Canvas(c.img.crop(box).resize((W * SS, H * SS)))


def between(tl, t, a, b, fa=0.0, fb=0.0):
    return tl.t(a, fa) <= t < tl.t(b, fb)


def hearts(c, x, y, t, n=3, col=(255, 110, 150), rise=70, spread=30):
    """Little hearts floating up from (x, y)."""
    for k in range(n):
        u = ((t * 0.5) + k / n) % 1.0
        hx, hy = x + spread * math.sin(t * 1.3 + k * 2), y - rise * u
        r = 5 + 3 * math.sin(math.pi * u)
        cc = mix(col, (255, 255, 255), u * 0.6)
        c.circle(hx - r * 0.8, hy, r, cc, ol=None)
        c.circle(hx + r * 0.8, hy, r, cc, ol=None)
        c.poly([(hx - r * 1.75, hy + r * 0.4), (hx + r * 1.75, hy + r * 0.4), (hx, hy + r * 2.3)], cc, ol=None)


def dizzy_stars(c, x, y, t, r=34, n=3):
    for k in range(n):
        a = t * 5 + k * 2 * math.pi / n
        sparkle(c, x + math.cos(a) * r, y + math.sin(a) * r * 0.35, 9, (255, 230, 90))


def bubble(c, x, y, rx, ry, k, tail, draw=None):
    """A thought bubble growing in (k 0..1). tail = (x, y) of the thinker's head. draw(c) draws the
    contents centred on (0, 0) in a local space that is scaled by k."""
    if k <= 0.02:
        return
    tx, ty = tail
    for f, r in ((0.25, 7), (0.5, 11)):
        c.circle(lerp(tx, x, f), lerp(ty, y + ry * 0.8, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 36):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * 0.92 * k, y + math.sin(a) * ry * 0.9 * k, 0.32 * min(rx, ry) * k,
                 (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)
    if draw:
        c.push(x, y, k)
        draw(c)
        c.pop()


def confetti(c, x, y, dt, n=40, seed=3, spread=420, up=520):
    """A confetti burst from (x, y), dt seconds after it popped."""
    if dt <= 0:
        return
    rng = np.random.default_rng(seed)
    cols = [(255, 90, 110), (255, 210, 70), (90, 170, 255), (130, 220, 120), (200, 130, 255), (255, 150, 60)]
    for k in range(n):
        vx = rng.uniform(-spread, spread)
        vy = -rng.uniform(up * 0.5, up)
        drag = math.exp(-1.6 * dt)
        px = x + vx * (1 - drag) / 1.6 + 14 * math.sin(dt * 6 + k)
        py = y + vy * (1 - drag) / 1.6 + 120 * dt * dt
        if py > H + 10:
            continue
        a = dt * 8 + k
        wv = 6 * abs(math.cos(a))
        c.rect(px - wv, py - 3, px + wv, py + 3, cols[k % len(cols)], ol=None)


# ================================================================== food + garden props

def apple(c, x, y, r=12, leaf=True):
    c.circle(x, y, r, APPLE, w=2)
    c.ellipse(x + r * 0.25, y + r * 0.35, r * 0.6, r * 0.45, APPLE_D, ol=None)
    c.circle(x, y, r, None, w=2)
    c.ellipse(x - r * 0.38, y - r * 0.35, r * 0.24, r * 0.17, (255, 190, 180), ol=None)
    c.line([(x, y - r * 0.8), (x + r * 0.15, y - r * 1.25)], TRUNK_D, max(1.5, r * 0.16), cap=False)
    if leaf:
        c.ellipse(x + r * 0.45, y - r * 1.1, r * 0.4, r * 0.2, LEAF, w=1.2)


# apples hanging in the apple tree (local coordinates, tree s=1)
TREE_APPLES = [(-120, -320), (110, -400), (-30, -420), (170, -300), (40, -540), (-200, -430), (60, -330),
               (-100, -470), (150, -470), (-160, -350), (0, -360)]


def apple_tree(c, x, base, s=1.0, t=0.0, shake=0.0, apples=None):
    """The big apple tree. shake 0..1 makes the crown wobble. apples: indices of TREE_APPLES still on the
    tree (None = all). Returns a function giving the world position of apple k."""
    wob = shake * (14 * math.sin(t * 31) + 6 * math.sin(t * 19))
    sway = 3 * math.sin(t * math.pi) + wob

    def ax(dx, dy):
        return dx + sway * (-dy / 500)
    c.push(x, base, s)
    c.poly([(-46, 0), (-34, -60), (-30, -260), (30, -260), (34, -60), (50, 0), (70, 6), (-72, 6)], TRUNK)
    c.line([(-6, -30), (-10, -200)], TRUNK_D, 4, cap=False)
    c.line([(14, -60), (18, -180)], TRUNK_D, 3, cap=False)
    c.stroke([(-20, -230), (ax(-110, -300), -300)], TRUNK, 20)
    c.stroke([(20, -220), (ax(120, -310), -310)], TRUNK, 22)
    blobs = [(-150, -330, 90), (150, -340, 92), (-70, -440, 105), (80, -450, 108), (0, -540, 95),
             (-190, -420, 70), (200, -430, 72), (0, -350, 100)]
    for dx, dy, r in blobs:
        c.circle(ax(dx, dy), dy, r, LEAF)
    for dx, dy, r in blobs:
        c.circle(ax(dx, dy), dy, r - 6, LEAF, ol=None)
    for dx, dy, r in ((-90, -470, 46), (60, -500, 40), (150, -360, 40), (-150, -360, 40)):
        c.circle(ax(dx, dy), dy, r, LEAF_L, ol=None)
    idx = range(len(TREE_APPLES)) if apples is None else apples
    for k in idx:
        dx, dy = TREE_APPLES[k]
        apple(c, ax(dx, dy), dy, 15)
    c.pop()

    def pos(k):
        dx, dy = TREE_APPLES[k]
        return x + ax(dx, dy) * s, base + dy * s
    return pos


def beehive(c, x, y, s=1.0):
    """A straw beehive (skep) on a tree stump. (x, y) = bottom of the stump."""
    c.push(x, y, s)
    c.rect(-58, -64, 58, 0, (150, 104, 66), w=3, r=6)
    c.ellipse(0, -64, 58, 12, (196, 150, 104), w=3)
    for k in range(3):
        c.arc(0, -64, 20 + k * 13, 4 + k * 2.6, 0, 360, (150, 104, 66), 2)
    pts = [(math.cos(a) * 74, -66 - math.sin(a) * 120) for a in np.linspace(0, math.pi, 30)]
    c.poly(pts, (244, 196, 96), w=3)
    for k in range(1, 6):
        yy = k * 21
        hw = 74 * math.sqrt(max(0.0, 1 - (yy / 120) ** 2))
        c.line([(-hw + 2, -66 - yy), (0, -66 - yy + 7), (hw - 2, -66 - yy)], HONEY_D, 3, cap=False)
    c.ellipse(0, -84, 17, 12, (90, 56, 30), w=2.5)
    c.ellipse(16, -70, 6, 9, HONEY, w=1.5)
    c.pop()


def honey_pot(c, x, y, s=1.0):
    """A little clay pot of honey with a wooden dipper. (x, y) = bottom."""
    c.push(x, y, s)
    c.line([(4, -54), (22, -92)], (150, 100, 60), 5)
    for k in range(3):
        c.ellipse(22 + k * 2.4, -92 - k * 6, 8 - k, 4, (190, 130, 70), w=1.5)
    c.ellipse(0, -28, 32, 28, (214, 150, 76), w=3)
    c.rect(-20, -60, 20, -46, (214, 150, 76), w=3, r=3)
    c.ellipse(0, -60, 24, 7, (196, 130, 60), w=2.5)
    c.ellipse(0, -60, 17, 4.5, HONEY, ol=None)
    c.poly([(-14, -58), (-8, -58), (-8, -36), (-11, -30), (-14, -36)], HONEY, ol=None)
    c.circle(-11, -32, 3.5, HONEY, ol=None)
    c.rect(-32, -34, 32, -26, (230, 80, 80), ol=None)
    c.ellipse(-12, -18, 6, 4, (236, 180, 110), ol=None)
    c.pop()


def watering_can(c, x, y, s=1.0, ang=0.0):
    """Watering can held by its handle at (x, y); ang tilts it (radians, + = spout down).
    Returns the world position of the spout's rose (where the water comes out)."""
    ca, sa = math.cos(ang), math.sin(ang)

    def R(px, py):
        py += 40
        return x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)
    col, dark = (80, 170, 210), (56, 130, 176)
    c.line([R(-22, -20), R(-16, -40), R(14, -40), R(22, -20)], OUT, 9 * s)
    c.line([R(-22, -20), R(-16, -40), R(14, -40), R(22, -20)], dark, 5 * s)
    c.poly([R(24, 6), R(62, -24), R(68, -18), R(30, 16)], col, w=2.5)
    rx, ry = R(68, -24)
    c.circle(rx, ry, 9 * s, dark, w=2.5)
    c.poly([R(-26, -20), R(26, -20), R(30, 24), R(-30, 24)], col, w=3)
    c.line([R(-26, -8), R(27, -8)], dark, 3, cap=False)
    return R(74, -28)


def water_drops(c, x, y, t, vx=120, n=14, fall=0.5, spread=26, col=(150, 205, 250)):
    """A sprinkle of drops leaving (x, y), each living `fall` seconds (periodic)."""
    for k in range(n):
        u = ((t / fall) + k / n) % 1.0
        dx = vx * u * fall + spread * math.sin(k * 2.3) * u
        dy = 900 * (u * fall) ** 2 + 10 * u
        c.ellipse(x + dx, y + dy, 3, 5, col, ol=None)


def flower_head(c, x, y, kind, r=14, petals=1.0):
    """kind: poppy | daisy | rose | tulip. petals 0..1 (0 = blown away, just the centre)."""
    if kind == "poppy":
        if petals > 0.05:
            for k in range(5):
                a = k * 2 * math.pi / 5 + 0.3
                c.circle(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, r * 0.62 * petals, (236, 56, 50), w=2)
        c.circle(x, y, r * 0.32, (40, 30, 40), w=1.5)
    elif kind == "daisy":
        if petals > 0.05:
            for k in range(9):
                a = k * 2 * math.pi / 9
                c.ellipse(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.36 * petals,
                          r * 0.36 * petals, (255, 255, 255), w=1.5)
        c.circle(x, y, r * 0.36, (255, 206, 50), w=1.5)
    elif kind == "rose":
        if petals > 0.05:
            c.circle(x, y, r * 0.95 * petals, (250, 120, 160), w=2)
            c.arc(x, y, r * 0.6 * petals, r * 0.55 * petals, 200, 520, (210, 70, 120), 2)
            c.arc(x + r * 0.1, y - r * 0.05, r * 0.3 * petals, r * 0.28 * petals, 0, 300, (210, 70, 120), 2)
        else:
            c.circle(x, y, r * 0.25, (120, 170, 80), w=1.5)
    else:   # tulip
        c.poly([(x - r * 0.8, y - r * 0.6), (x - r * 0.4, y - r), (x, y - r * 0.5), (x + r * 0.4, y - r),
                (x + r * 0.8, y - r * 0.6), (x + r * 0.6, y + r * 0.5), (x - r * 0.6, y + r * 0.5)],
               (255, 140, 60), w=2)


FLOWER_PETAL_COLS = {"poppy": (236, 56, 50), "daisy": (255, 255, 255), "rose": (250, 120, 160)}
BOUQUET = [(-34, -66, "poppy"), (30, -70, "rose"), (0, -96, "daisy"), (-16, -84, "rose"), (18, -92, "poppy"),
           (-40, -94, "daisy"), (42, -96, "daisy"), (4, -124, "poppy"), (-24, -118, "rose"), (28, -122, "daisy")]


def bouquet(c, x, y, s=1.0, t=0.0, petals=1.0, n=None):
    """A bunch of poppies, daisies and roses; (x, y) = where the stems meet (bottom)."""
    c.push(x, y, s)
    items = BOUQUET if n is None else BOUQUET[:n]
    for dx, dy, kind in items:
        sw = 2 * math.sin(t * 1.7 + dx)
        c.line([(0, 0), (dx * 0.8 + sw, dy + 10)], (80, 150, 70), 3, cap=False)
    for dx, dy, kind in items:
        if dx in (-34, 30):
            c.ellipse(dx * 0.5, dy * 0.5, 9, 4, LEAF, w=1.2)
    for dx, dy, kind in items:
        sw = 2 * math.sin(t * 1.7 + dx)
        flower_head(c, dx + sw, dy, kind, 15, petals)
    c.pop()


def vase(c, x, y, s=1.0, col=(90, 150, 230)):
    """A round vase; (x, y) = bottom. The flowers go in at (x, y - 66 s)."""
    c.push(x, y, s)
    c.poly([(-16, -66), (16, -66), (14, -56), (36, -30), (30, -4), (20, 0), (-20, 0), (-30, -4), (-36, -30),
            (-14, -56)], col, w=3)
    c.ellipse(0, -66, 17, 5, mix(col, OUT, 0.35), w=2)
    c.line([(-26, -30), (26, -30)], (255, 255, 255), 3, cap=False)
    c.ellipse(-14, -40, 5, 9, mix(col, (255, 255, 255), 0.5), ol=None)
    c.pop()


def stool(c, x, y, s=1.0):
    """A little round stool; (x, y) = floor. Top at y - 70 s."""
    c.push(x, y, s)
    for dx in (-30, 30):
        c.line([(dx * 0.7, -64), (dx, 0)], (150, 100, 66), 8)
    c.ellipse(0, -70, 50, 12, (196, 130, 80), w=3)
    c.rect(-50, -70, 50, -60, (170, 110, 70), w=3, r=4)
    c.ellipse(0, -72, 50, 11, (210, 150, 96), w=3)
    c.pop()


# ================================================================== baking

def mixing_bowl(c, x, y, s=1.0, level=1.0, batter=(250, 226, 170), spoon=None):
    """Big mixing bowl; (x, y) = bottom. level 0..1 how full. spoon = angle (radians) of the stirring
    spoon, or None."""
    c.push(x, y, s)
    if spoon is not None:
        sx, sy = 26 * math.cos(spoon), -78 + 8 * math.sin(spoon)
        c.line([(sx, sy), (sx + 30, sy - 70)], OUT, 10)
        c.line([(sx, sy), (sx + 30, sy - 70)], (210, 160, 100), 6)
    c.ellipse(0, -80, 96, 20, (230, 236, 246), w=3)
    if level > 0.02:
        c.ellipse(0, -80 + 10 * (1 - level), 82 * (0.7 + 0.3 * level), 14 * (0.7 + 0.3 * level), batter, ol=None)
        if spoon is not None:
            c.arc(10 * math.cos(spoon * 0.5), -78, 30, 6, 200, 340, mix(batter, OUT, 0.15), 2)
    if spoon is not None:
        sx, sy = 26 * math.cos(spoon), -78 + 8 * math.sin(spoon)
        c.ellipse(sx, sy + 2, 12, 6, (210, 160, 100), w=2)
    c.poly([(-96, -80), (96, -80), (80, -30), (50, -4), (-50, -4), (-80, -30)], (120, 180, 230), w=3)
    c.ellipse(0, -2, 46, 6, (100, 150, 200), w=2.5)
    c.line([(-88, -66), (88, -66)], (255, 255, 255), 4, cap=False)
    c.pop()


def egg(c, x, y, r=11, ang=0.0):
    c.ellipse(x, y, r * 0.8, r, (255, 248, 236), w=2)


def flour_bag(c, x, y, s=1.0, tip=0.0):
    c.push(x, y, s)
    c.poly([(-36, 0), (-40, -86), (-30, -100), (30, -100), (40, -86), (36, 0)], (240, 232, 214), w=3)
    c.poly([(-30, -100), (-20, -112), (20, -112), (30, -100)], (226, 216, 196), w=2.5)
    c.ellipse(0, -48, 18, 16, (200, 186, 160), ol=None)
    c.ellipse(0, -48, 9, 8, (240, 232, 214), ol=None)
    c.pop()


def egg_box(c, x, y, s=1.0, n=3):
    c.push(x, y, s)
    for k in range(n):
        egg(c, -24 + k * 24, -26, 12)
    c.rect(-42, -24, 42, 0, (200, 170, 120), w=3, r=4)
    for k in range(4):
        c.line([(-36 + k * 24, -22), (-36 + k * 24, -4)], (170, 140, 96), 2, cap=False)
    c.pop()


def milk_bottle(c, x, y, s=1.0, tilt=0.0):
    """(x, y) = bottom (it tilts around it). Returns the mouth position."""
    ca, sa = math.cos(tilt), math.sin(tilt)

    def R(px, py):
        return x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)
    c.poly([R(-24, 0), R(-24, -70), R(-12, -90), R(-12, -104), R(12, -104), R(12, -90), R(24, -70), R(24, 0)],
           (250, 252, 255), w=3)
    c.poly([R(-24, -30), R(24, -30), R(24, -54), R(-24, -54)], (110, 170, 240), ol=None)
    c.poly([R(-13, -104), R(13, -104), R(13, -112), R(-13, -112)], (110, 170, 240), w=2)
    return R(0, -110)


def cake(c, x, y, s=1.0, t=0.0, candle_on=False, sliced=False):
    """The birthday cake: pink icing, cream and sprinkles (no apples or honey shown: both branches lead
    to it). (x, y) = bottom of the plate. candle_on adds a lit candle (it replaces the cherry)."""
    c.push(x, y, s)
    c.ellipse(0, -6, 118, 18, (250, 250, 252), w=3)
    c.ellipse(0, -8, 98, 12, (236, 236, 244), ol=None)
    top, bot, rx = -104, -16, 92
    c.ellipse(0, bot, rx, 17, SPONGE, w=3)
    c.rect(-rx, top, rx, bot, SPONGE, ol=None)
    c.line([(-rx, top), (-rx, bot)], OUT, 3, cap=False)
    c.line([(rx, top), (rx, bot)], OUT, 3, cap=False)
    c.rect(-rx + 1.5, -66, rx - 1.5, -56, CREAM, ol=None)
    c.arc(0, -61, rx, 15, 0, 180, mix(CREAM, OUT, 0.15), 2)
    # icing: top + a dripping front edge, one outlined shape
    pts = []
    for k in range(41):
        xx = -rx - 2 + (2 * rx + 4) * k / 40
        e = math.sqrt(max(0.0, 1 - (xx / (rx + 2)) ** 2))
        drip = 9 + 12 * abs(math.sin(xx / 13.0)) ** 3
        pts.append((xx, top + 19 * e + drip * (0.3 + 0.7 * e)))
    for k in range(41):
        xx = rx + 2 - (2 * rx + 4) * k / 40
        e = math.sqrt(max(0.0, 1 - (xx / (rx + 2)) ** 2))
        pts.append((xx, top - 19 * e))
    c.poly(pts, PINK, w=3)
    c.ellipse(-30, top - 6, 26, 6, (255, 196, 216), ol=None)
    rng = np.random.default_rng(12)
    cols = [(255, 255, 255), (255, 214, 80), (110, 190, 255), (140, 220, 120), (200, 140, 255)]
    for k in range(26):
        a = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.uniform(0.05, 0.85))
        px, py = math.cos(a) * rr * 80, top + math.sin(a) * rr * 15
        q = rng.uniform(0, math.pi)
        c.line([(px - 4 * math.cos(q), py - 1.5 * math.sin(q)), (px + 4 * math.cos(q), py + 1.5 * math.sin(q))],
               cols[k % 5], 2.5)
    for k in range(7):
        a = math.pi * (0.1 + 0.8 * k / 6)
        px, py = math.cos(a) * 74, top + math.sin(a) * 13
        c.circle(px, py - 5, 11, (255, 255, 255), w=2)
        c.circle(px, py - 13, 6, (255, 255, 255), w=2)
    if candle_on:
        candle(c, 0, top + 4, 1.1, t, True, col=(150, 205, 255))
        for k in range(4):
            c.line([(-8, top - 6 - k * 10), (8, top - 12 - k * 10)], (255, 255, 255), 3, cap=False)
    else:
        c.line([(2, top - 20), (10, top - 38)], (90, 140, 60), 2.5)
        c.circle(0, top - 12, 12, (220, 40, 60), w=2.5)
        c.circle(-4, top - 16, 3.5, (255, 180, 190), ol=None)
    c.pop()


def cake_slice(c, x, y, s=1.0):
    """A slice of the cake on a little plate; (x, y) = plate centre."""
    c.push(x, y, s)
    c.ellipse(0, 6, 46, 11, (250, 250, 252), w=2.5)
    c.poly([(-30, 0), (30, -6), (30, -40), (-30, -34)], SPONGE, w=2.5)
    c.rect(-29, -22, 29, -16, CREAM, ol=None)
    c.poly([(-32, -34), (32, -40), (34, -50), (-30, -44)], PINK, w=2.5)
    c.circle(6, -54, 7, (255, 255, 255), w=2)
    c.pop()


# ================================================================== party props

BALLOON_COLS = [(240, 70, 80), (255, 210, 60), (70, 140, 240), (120, 210, 110), (200, 120, 240), (255, 150, 60)]


def party_balloon(c, x, y, r, col, t=0.0, string=110, seed=0.0, sway=1.0):
    """(x, y) = centre of the balloon. The string hangs `string` px below the knot."""
    sw = sway * 4 * math.sin(t * 1.3 + seed)
    bx = x + sw
    if string > 0:
        pts = [(bx + 6 * math.sin(u * 6 + t * 2 + seed) * u - sw * u, y + r + 6 + string * u)
               for u in np.linspace(0, 1, 8)]
        c.line(pts, (110, 100, 110), 2, cap=False)
    c.poly([(bx - 6, y + r + 8), (bx + 6, y + r + 8), (bx, y + r - 4)], mix(col, OUT, 0.25), w=1.5)
    c.ellipse(bx, y, r * 0.86, r, col, w=3)
    c.ellipse(bx - r * 0.32, y - r * 0.42, r * 0.17, r * 0.27, mix(col, (255, 255, 255), 0.6), ol=None)


def balloon_bunch(c, x, y, t=0.0, n=5, s=1.0, seed=0.0):
    """A bunch of balloons tied to a little weight at (x, y) on the floor."""
    spots = [(-40, -250, 0), (30, -270, 1), (-5, -320, 2), (60, -330, 3), (-60, -330, 4), (20, -380, 5)]
    for k, (dx, dy, ci) in enumerate(spots[:n]):
        bx, by = x + dx * s + 4 * math.sin(t * 1.2 + k + seed), y + dy * s
        c.line([(x, y - 14), (bx, by + 40 * s)], (110, 100, 110), 2, cap=False)
    for k, (dx, dy, ci) in enumerate(spots[:n]):
        bx, by = x + dx * s + 4 * math.sin(t * 1.2 + k + seed), y + dy * s
        party_balloon(c, bx, by, 40 * s, BALLOON_COLS[ci], t, string=0, sway=0)
    c.rect(x - 14, y - 16, x + 14, y, (230, 80, 120), w=2.5, r=4)


def banner(c, x0, x1, y, t=0.0):
    """Bunting with the ribbon "HAPPY BIRTHDAY, PIP". The words are ONE c.text call (so a translation can
    swap them through draw.TEXTS); the ribbon grows to fit whatever text is shown."""
    s = D.TEXTS.get(BANNER_TEXT, BANNER_TEXT)
    size = 30
    tw = D.font(size, D.is_armenian(s)).getlength(s) / SS
    xm = (x0 + x1) / 2
    hw = tw / 2 + 30
    sag = 16

    def sy(x):
        u = (x - x0) / (x1 - x0)
        return y + sag * 4 * u * (1 - u)
    c.line([(x0, y), (xm - hw, sy(xm - hw))], (120, 100, 90), 2.5, cap=False)
    c.line([(xm + hw, sy(xm + hw)), (x1, y)], (120, 100, 90), 2.5, cap=False)
    cols = [(240, 80, 100), (255, 200, 60), (80, 160, 240), (120, 200, 110)]
    for side in (-1, 1):
        a, b = (x0 + 14, xm - hw - 14) if side < 0 else (xm + hw + 14, x1 - 14)
        n = max(1, int((b - a) / 40))
        for k in range(n + 1):
            fx = lerp(a, b, k / max(1, n))
            fy = sy(fx)
            c.poly([(fx - 15, fy), (fx + 15, fy), (fx, fy + 36)], cols[k % 4], w=2)
    yt = sy(xm)
    c.poly([(xm - hw - 26, yt + 2), (xm - hw, yt + 2), (xm - hw, yt + 54), (xm - hw - 26, yt + 54),
            (xm - hw - 14, yt + 28)], (236, 90, 120), w=2.5)
    c.poly([(xm + hw + 26, yt + 2), (xm + hw, yt + 2), (xm + hw, yt + 54), (xm + hw + 26, yt + 54),
            (xm + hw + 14, yt + 28)], (236, 90, 120), w=2.5)
    c.rect(xm - hw, yt - 4, xm + hw, yt + 60, (255, 250, 236), w=3, r=10)
    c.text(xm, yt + 28, BANNER_TEXT, size, (226, 70, 110))


def cushion(c, x, y, s=1.0, squash=0.0):
    """A big soft floor cushion; (x, y) = floor."""
    c.push(x, y, s)
    h = 46 * (1 - 0.4 * squash)
    w = 110 * (1 + 0.12 * squash)
    c.rect(-w, -h, w, 0, (150, 110, 220), w=3, r=22)
    c.rect(-w + 12, -h + 6, w - 12, -h + 14, (180, 150, 240), ol=None, r=4)
    c.circle(0, -h / 2, 5, (110, 80, 180), w=1.5)
    for sx in (-1, 1):
        c.circle(sx * (w - 4), -6, 8, (255, 200, 80), w=2)
    c.pop()


# ================================================================== characters

SPINE, SPINE_L = (124, 88, 64), (164, 122, 88)
HOG_FACE, HOG_FEET = (244, 220, 186), (110, 78, 58)
HOG_BACK = [(-30, -82), (0, -86), (-52, -64), (24, -76), (-14, -64), (-62, -40), (10, -62), (-36, -50),
            (-46, -80)]


def hedgehog(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, curl=0.0, spin=0.0,
             apples=0, hop=0.0, seed=0.0, look=(0.0, 0.0)):
    """Hedgie, a kind little hedgehog, facing right; (x, y) = between the feet.
    curl > 0.5 rolls him into a spiky ball (spin turns it). apples: how many apples stick to his spines."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y - hop, s, flip=face < 0)
    if curl > 0.5:
        r = 46
        cx, cy = 0, -r
        n = 26
        pts = []
        for k in range(2 * n):
            a = spin + k * math.pi / n
            rr = r * (1.2 if k % 2 == 0 else 0.94)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        c.poly(pts, SPINE)
        c.circle(cx, cy, r * 0.82, SPINE_L, ol=None)
        for k in range(9):
            a = spin + k * 0.7
            c.line([(cx + math.cos(a) * r * 0.3, cy + math.sin(a) * r * 0.3),
                    (cx + math.cos(a) * r * 0.74, cy + math.sin(a) * r * 0.74)], SPINE, 3)
        fa = spin + 0.6
        fx, fy = cx + math.cos(fa) * r * 0.42, cy + math.sin(fa) * r * 0.42
        c.circle(fx, fy, r * 0.32, HOG_FACE, ol=None)
        c.circle(cx + math.cos(fa) * r * 0.6, cy + math.sin(fa) * r * 0.6, 5, (40, 30, 34), ol=None)
        for k in range(apples):
            a = spin + k * 2.39 + 3.6
            apple(c, cx + math.cos(a) * r * 1.02, cy + math.sin(a) * r * 1.02, 12, leaf=False)
        c.pop()
        return
    # feet
    for fx, ph in ((-34, 0.0), (-18, math.pi), (16, math.pi), (32, 0.0)):
        sw = math.sin(walk + ph) * 6 if walk else 0.0
        lift = -max(0.0, math.cos(walk + ph)) * 4 if walk else 0.0
        c.ellipse(fx + sw, -5 + lift, 10, 6, HOG_FEET, w=2)
    # spiny back
    cx, cy, rx, ry = -10, -36, 58, 40
    pts = []
    n = 24
    for k in range(n + 1):
        a = math.radians(14 + 180 * k / n)
        rr = 1.26 if k % 2 == 0 else 1.0
        pts.append((cx + rx * rr * math.cos(a), cy - ry * rr * math.sin(a)))
    for k in range(1, 12):
        a = math.radians(194 + 180 * k / 12)
        pts.append((cx + rx * math.cos(a), cy - ry * 0.75 * math.sin(a)))
    c.poly(pts, SPINE)
    for k in range(9):
        a = math.radians(30 + 150 * k / 8)
        c.line([(cx + rx * 0.45 * math.cos(a), cy - ry * 0.45 * math.sin(a)),
                (cx + rx * 0.95 * math.cos(a), cy - ry * 0.95 * math.sin(a))], SPINE_L, 3)
    # face + snout
    c.ellipse(26, -30, 30, 26, HOG_FACE)
    c.poly([(36, -46), (80, -30), (78, -22), (36, -12)], HOG_FACE)
    c.ellipse(28, -26, 26, 22, HOG_FACE, ol=None)
    c.circle(80, -27, 6.5, (40, 30, 34), w=1.5)
    c.circle(78, -29, 2, (255, 255, 255), ol=None)
    c.circle(20, -56, 9, HOG_FACE, w=2.5)
    c.circle(20, -56, 5, (250, 170, 170), ol=None)
    ex, ey = 42, -38
    if eyes == "closed":
        c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex + look[0] * 1.5, ey + look[1] * 1.5, 5 * big, 6.5 * big, (30, 22, 26), ol=None)
        c.circle(ex + 1.5 + look[0] * 1.5, ey - 2.5 + look[1] * 1.5, 2, (255, 255, 255), ol=None)
    c.circle(44, -20, 6, (250, 160, 160), ol=None)
    if mouth > 0.05:
        c.ellipse(60, -16, 6, 2 + 6 * mouth, D.MOUTH, w=2)
    else:
        c.arc(58, -20, 7, 5, 20, 160, OUT, 2)
    for px, py in HOG_BACK[:apples]:
        apple(c, px, py, 12, leaf=False)
    c.pop()


BEE_Y, BEE_K = (255, 206, 60), (54, 40, 44)


def bee(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", wave=0.0, carry=False, seed=0.0, look=(0.0, 0.0)):
    """Buzzy, a cheerful bee, flying, facing right; (x, y) = centre of her body. carry=True: she holds a
    honey pot below her."""
    if eyes == "open" and D.blink(t, seed + 0.7):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    if carry:
        c.line([(-2, 22), (-6, 40)], OUT, 2, cap=False)
        c.line([(10, 22), (6, 40)], OUT, 2, cap=False)
        honey_pot(c, 0, 100, 0.75)
    flap = abs(math.sin(t * 38 + seed))
    for wx, k in ((-16, 1.0), (2, 0.85)):
        c.ellipse(wx, -24 - 6 * flap, 13 * k, (12 + 12 * flap) * k, (226, 242, 255), ol=(120, 150, 190), w=2)
    c.poly([(-28, 0), (-46, 6), (-28, 12)], BEE_K, w=1.5)
    for lx in (-8, 6, 18):
        c.line([(lx, 20), (lx - 3, 30)], BEE_K, 2.5, cap=False)
    c.ellipse(0, 4, 32, 23, BEE_Y, w=3)
    for sx in (-17, -3):
        ry = 23 * math.sqrt(1 - (sx / 32) ** 2) - 1.5
        c.ellipse(sx, 4, 5.5, ry, BEE_K, ol=None)
    c.ellipse(0, 4, 32, 23, None, w=3)
    if wave > 0:
        k = math.sin(t * 10)
        c.line([(18, 14), (30 + 3 * k, -4 - 6 * wave)], BEE_K, 3)
    c.circle(32, -6, 18, BEE_Y, w=3)
    c.line([(28, -22), (22, -40)], BEE_K, 2.5, cap=False)
    c.circle(22, -41, 4, BEE_K, ol=None)
    c.line([(36, -22), (42, -39)], BEE_K, 2.5, cap=False)
    c.circle(42, -40, 4, BEE_K, ol=None)
    ex, ey = 38, -10
    if eyes == "closed":
        c.arc(ex, ey, 5, 3.5, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 2, 5, 5, 200, 340, OUT, 2.5)
    else:
        c.ellipse(ex + look[0], ey + look[1], 4.5, 6, (30, 22, 26), ol=None)
        c.circle(ex + 1.5 + look[0], ey - 2.5 + look[1], 1.8, (255, 255, 255), ol=None)
    c.circle(40, 2, 4.5, (255, 150, 140), ol=None)
    if mouth > 0.05:
        c.ellipse(45, 3, 4, 1.5 + 4 * mouth, D.MOUTH, w=1.5)
    else:
        c.arc(44, 1, 5, 4, 20, 160, OUT, 2)
    c.pop()


def little_bees(c, cx, cy, t, n=4, r=90, s=0.42):
    """Small bees looping around (cx, cy); periodic."""
    for k in range(n):
        a = t * (1.1 + 0.2 * k) + k * 2 * math.pi / n
        x = cx + math.cos(a) * r * (1 + 0.2 * k % 2)
        y = cy + math.sin(a * 2) * r * 0.35
        face = -1 if math.sin(a) > 0 else 1
        bee(c, x, y, s, face, t + k, seed=k)


# ================================================================== the places

def room_bg():
    """The cats' room (the moonfish room: rug, plant, the windowsill), day."""
    from films.moonfish.scenes import room
    return room(False)


GL = 610                  # ground line of the outdoor places


def orchard_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, SKY))
        D.cloud(c, 230, 100, 0.9)
        D.cloud(c, 1040, 70, 0.7)
        pts = [(x, 410 + 34 * math.sin(x / 230 + 0.4)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (156, 208, 136), ol=None)
        for x, s in ((90, 0.5), (300, 0.42), (1120, 0.55), (1230, 0.45)):
            D.tree(c, x, 470, s)
        # a little fence far back
        for x in range(0, 380, 38):
            c.rect(x, 480, x + 12, 552, (214, 176, 128), w=2)
        c.rect(0, 500, 392, 510, (196, 156, 110), w=2)
        c.rect(0, GL - 40, W, H, GRASS, ol=None)
        c.rect(0, GL + 40, W, H, GRASS_D, ol=None)
        rng = np.random.default_rng(21)
        cols = [(250, 120, 150), (255, 230, 90), (255, 255, 255), (180, 140, 250)]
        for _ in range(60):
            D.flower(c, rng.uniform(0, W), rng.uniform(GL - 20, H - 8), cols[rng.integers(4)], rng.uniform(0.55, 0.9))
        D.bush(c, 1160, GL - 30, 0.9)
        D.bush(c, 60, GL - 26, 0.8)
        return c.img
    return cached("bd_orchard", make)


HIVE = (1080, GL - 6)


def meadow_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, SKY))
        D.cloud(c, 300, 90, 0.8)
        D.cloud(c, 900, 120, 0.6)
        pts = [(x, 400 + 30 * math.sin(x / 190 + 1.4)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (170, 214, 130), ol=None)
        pts = [(x, 470 + 24 * math.sin(x / 140 + 0.3)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (150, 204, 116), ol=None)
        rng = np.random.default_rng(31)
        cols = [(250, 120, 150), (255, 230, 90), (255, 255, 255), (180, 140, 250), (255, 160, 80)]
        for _ in range(140):
            D.flower(c, rng.uniform(0, W), rng.uniform(470, GL - 30), cols[rng.integers(5)], rng.uniform(0.4, 0.6))
        D.tree(c, 1220, 500, 0.7)
        c.rect(0, GL - 40, W, H, GRASS, ol=None)
        c.rect(0, GL + 40, W, H, GRASS_D, ol=None)
        for _ in range(70):
            D.flower(c, rng.uniform(0, W), rng.uniform(GL - 20, H - 8), cols[rng.integers(5)], rng.uniform(0.7, 1.0))
        # a little patch of soil for the thirsty flowers
        c.ellipse(780, GL + 6, 150, 18, (150, 110, 80), ol=None)
        beehive(c, HIVE[0], HIVE[1], 1.0)
        return c.img
    return cached("bd_meadow", make)


THIRSTY = [(680, "tulip"), (740, "poppy"), (800, "daisy"), (860, "tulip"), (910, "rose")]


def thirsty_flowers(c, t, perk=1.0):
    """The flowers in the soil patch. perk 0 = drooping and pale, 1 = upright and bright."""
    for k, (x, kind) in enumerate(THIRSTY):
        h = lerp(70, 110, perk) + 6 * (k % 2)
        lean = lerp(36, 0, perk) * (1 if k % 2 else -1)
        sw = 2 * math.sin(t * 1.5 + k) * perk
        top = (x + lean + sw, GL - h + lerp(26, 0, perk))
        c.line([(x, GL + 4), (x + lean * 0.3, GL - h * 0.5), top], (90, 150, 70), 4, cap=False)
        c.ellipse(x - 12, GL - 26, 14, 6, LEAF, w=1.5)
        c.ellipse(x + 12, GL - 40, 14, 6, LEAF, w=1.5)
        flower_head(c, top[0], top[1], kind, lerp(11, 17, perk), 1.0)


KCY = 600                 # kitchen counter top (where the cats stand)
OVEN = (210, 250, 430, 540)


def kitchen_bg():
    def make():
        wall = (255, 240, 206)
        c = Canvas(bg=wall)
        for y in range(330, KCY, 34):            # tiles behind the counter
            for x in range(0, W, 34):
                c.rect(x + 1, y + 1, x + 33, y + 33, (232, 244, 248) if (x // 34 + y // 34) % 2 else (210, 232, 240),
                       ol=None)
        c.rect(0, 326, W, 332, (200, 200, 210), ol=None)
        # window with curtains
        win = D.gradient(260 * SS, 190 * SS, [(0, (120, 190, 245)), (1, (210, 236, 255))])
        c.img.paste(win, (520 * SS, 90 * SS))
        c.circle(720, 140, 26, (255, 222, 90), ol=None)
        D.cloud(c, 590, 160, 0.45)
        c.rect(520, 90, 780, 280, None, w=7)
        c.line([(650, 90), (650, 280)], (250, 250, 250), 5, cap=False)
        for sx in (-1, 1):
            x0 = 520 if sx < 0 else 780
            c.poly([(x0 - sx * 10, 74), (x0 + sx * 40, 74), (x0 + sx * 26, 200), (x0 + sx * 46, 300),
                    (x0 - sx * 6, 300)], (240, 110, 110), w=2.5)
        c.rect(500, 70, 800, 80, (190, 130, 90), w=2, r=4)
        # shelf with jars and cups
        c.rect(880, 200, 1220, 214, (190, 130, 90), w=2.5, r=3)
        for x, col, hh in ((910, (230, 150, 90), 60), (970, (150, 200, 120), 46), (1030, (240, 200, 90), 70),
                           (1090, (200, 140, 220), 50), (1150, (120, 180, 230), 62)):
            c.rect(x - 22, 200 - hh, x + 22, 200, mix(col, (255, 255, 255), 0.5), w=2.5, r=6)
            c.rect(x - 24, 200 - hh - 10, x + 24, 200 - hh, col, w=2.5, r=3)
        # hanging pans
        for x, r in ((380, 34), (450, 26)):
            c.line([(x, 60), (x, 110 - r)], (120, 120, 130), 3, cap=False)
            c.circle(x, 130, r, (120, 126, 140), w=3)
            c.circle(x, 130, r - 8, (150, 156, 170), ol=None)
        # the oven (built into the wall)
        x0, y0, x1, y1 = OVEN
        c.rect(x0, y0, x1, y1, (236, 236, 242), w=3, r=10)
        c.rect(x0 + 14, y0 + 14, x1 - 14, y0 + 50, (200, 200, 212), w=2, r=6)
        for k in range(3):
            c.circle(x0 + 50 + k * 64, y0 + 32, 10, (90, 90, 100), w=2)
        c.rect(x0 + 24, y0 + 70, x1 - 24, y1 - 30, (70, 60, 70), w=3, r=10)
        c.rect(x0 + 40, y0 + 62, x1 - 40, y0 + 72, (180, 180, 190), w=2, r=4)
        # the counter (front)
        c.rect(0, KCY - 14, W, KCY + 6, (240, 236, 230), w=3)
        c.rect(0, KCY + 6, W, H, (196, 140, 96), ol=None)
        for x in range(0, W, 213):
            c.rect(x + 8, KCY + 24, x + 205, H + 20, (210, 156, 110), w=3, r=8)
            c.rect(x + 90, KCY + 44, x + 124, KCY + 52, (150, 100, 70), ol=None, r=3)
        return c.img
    return cached("bd_kitchen", make)


PFLOOR = 570              # party room: where the wall meets the floor
PY = 650                  # where the cats stand
DOOR = (70, 220, 250, PFLOOR)
TABLE = (920, 1210, 450)  # x0, x1, top y
CAKE_AT = (1065, 452)


def party_bg(banner_on=True, table=True):
    """The living room, ready for the party. The banner is part of it when banner_on."""
    def make():
        wall = (255, 226, 218)
        c = Canvas(bg=wall)
        for x in range(0, W, 60):
            c.rect(x + 26, 0, x + 34, PFLOOR, (255, 236, 230), ol=None)
        c.rect(0, 420, W, PFLOOR, (236, 196, 200), ol=None)
        c.rect(0, 414, W, 424, (214, 160, 170), ol=None)
        c.rect(0, PFLOOR, W, H, (206, 150, 104), ol=None)
        for y in range(PFLOOR + 26, H, 40):
            c.line([(0, y), (W, y)], (186, 132, 90), 2, cap=False)
        c.rect(0, PFLOOR - 8, W, PFLOOR + 4, (180, 120, 90), ol=None)
        # door
        x0, y0, x1, y1 = DOOR
        c.rect(x0 - 14, y0 - 14, x1 + 14, y1, (236, 236, 240), w=3)
        c.rect(x0, y0, x1, y1, (178, 112, 72), w=3)
        c.rect(x0 + 22, y0 + 24, x1 - 22, y0 + 150, (192, 126, 84), w=2.5, r=6)
        c.rect(x0 + 22, y0 + 180, x1 - 22, y1 - 24, (192, 126, 84), w=2.5, r=6)
        c.circle(x1 - 24, y0 + 170, 9, (250, 210, 80), w=2)
        # window
        win = D.gradient(250 * SS, 210 * SS, [(0, (120, 190, 245)), (1, (210, 236, 255))])
        c.img.paste(win, (940 * SS, 120 * SS))
        D.cloud(c, 1010, 180, 0.5)
        c.circle(1140, 160, 24, (255, 222, 90), ol=None)
        c.rect(940, 120, 1190, 330, None, w=7)
        c.line([(1065, 120), (1065, 330)], (250, 250, 250), 5, cap=False)
        c.rect(924, 326, 1206, 342, (255, 250, 240), w=2.5, r=3)
        for sx, xx in ((-1, 940), (1, 1190)):
            c.poly([(xx - sx * 8, 104), (xx + sx * 34, 104), (xx + sx * 20, 230), (xx + sx * 38, 340),
                    (xx - sx * 4, 340)], (120, 190, 170), w=2.5)
        c.rect(920, 96, 1210, 106, (190, 130, 90), w=2, r=4)
        # a picture on the wall (Whiskers' painting of a fish)
        c.rect(560, 230, 700, 340, (255, 250, 240), w=6)
        c.rect(572, 242, 688, 328, (180, 220, 250), ol=None)
        c.ellipse(626, 286, 34, 18, (255, 160, 80), w=2)
        c.poly([(660, 286), (684, 268), (684, 304)], (255, 160, 80), w=2)
        c.circle(606, 280, 3.5, OUT, ol=None)
        # plant
        c.rect(300, PFLOOR - 70, 360, PFLOOR + 10, (190, 100, 70), w=3, r=6)
        for dx, dy in ((-30, -10), (0, -40), (30, -12), (-15, -30), (18, -36)):
            c.ellipse(330 + dx, PFLOOR - 70 + dy, 14, 30, (80, 160, 90))
        # rug
        c.ellipse(640, 664, 330, 46, (110, 170, 220), w=3)
        c.ellipse(640, 664, 270, 32, (150, 200, 240), ol=None)
        if table:
            tx0, tx1, ty = TABLE
            for lx in (tx0 + 26, tx1 - 26):
                c.rect(lx - 7, ty, lx + 7, PFLOOR + 30, (150, 100, 66), w=2.5)
            c.poly([(tx0 - 12, ty), (tx1 + 12, ty), (tx1 + 4, ty + 62), (tx0 - 4, ty + 62)], (255, 255, 255), w=3)
            for k in range(8):
                xx = lerp(tx0, tx1, (k + 0.5) / 8)
                c.circle(xx, ty + 56, 8, (255, 160, 190), ol=None)
            c.rect(tx0 - 14, ty - 8, tx1 + 14, ty + 2, (255, 255, 255), w=3, r=4)
        if banner_on:
            banner(c, 290, 900, 70)
        return c.img
    return cached(("bd_party", banner_on, table), make)


# ================================================================== question backdrops

def q1_backdrop():
    """Behind Whiskers: the apple tree on the left, the beehive meadow on the right (soft focus)."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, SKY))
        D.cloud(c, 520, 90, 0.7)
        D.cloud(c, 820, 60, 0.6)
        pts = [(x, 400 + 30 * math.sin(x / 210)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, H), (0, H)], (150, 205, 130), ol=None)
        c.rect(0, 470, W, H, GRASS, ol=None)
        c.rect(0, 560, W, H, GRASS_D, ol=None)
        apple_tree(c, 200, 570, 0.95)
        for x, y in ((140, 600), (260, 610), (330, 596)):
            apple(c, x, y, 14)
        rng = np.random.default_rng(4)
        cols = [(250, 120, 150), (255, 230, 90), (255, 255, 255), (180, 140, 250)]
        for _ in range(60):
            D.flower(c, rng.uniform(820, W), rng.uniform(480, 700), cols[rng.integers(4)], rng.uniform(0.7, 1.1))
        beehive(c, 1090, 560, 1.15)
        for k, (x, y) in enumerate(((990, 330), (1170, 300), (1220, 420), (960, 450))):
            bee(c, x, y, 0.55, -1 if k % 2 else 1, 0.3 * k, seed=k)
        img = c.img.filter(ImageFilter.GaussianBlur(1.6 * SS))
        return img
    return cached("bd_q1_bg", make)


def q2_backdrop():
    """The party room (no banner yet): balloons on the left, a vase of flowers on the right (soft focus)."""
    def make():
        c = Canvas(party_bg(banner_on=False, table=False).copy())
        balloon_bunch(c, 200, 640, 0.0, n=6, s=1.25)
        stool(c, 1080, 650, 1.3)
        vase(c, 1080, 650 - 91, 1.3)
        bouquet(c, 1080, 650 - 91 - 80, 1.3)
        img = c.img.filter(ImageFilter.GaussianBlur(1.6 * SS))
        return img
    return cached("bd_q2_bg", make)
