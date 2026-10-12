"""Props for Episode 7 "Rainforests": Coco the toucan, Mossy the sloth, the jaguar, monkeys,
a macaw, a harpy eagle, leafcutter ants, a blue dart frog, rain, the rainforest areas on the
globe / map, the tall layered forest backdrop and the "floors of a building" layer gauge."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease
from world import kit as K

TAU = 2 * math.pi


def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def sprite(c, x, y, size, angle, fn):
    """Draw fn(sc, cx, cy) into a transparent square sprite (size px), rotate it by angle degrees
    (counter-clockwise) and paste it centred at (x, y) in c's current transform."""
    n = int(size * SS)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    sc = Canvas(img)
    fn(sc, size / 2, size / 2)
    if abs(angle) > 0.01:
        img = img.rotate(angle, resample=Image.BICUBIC)
    px, py = c.P(x, y)
    c.img.paste(img, (int(px - n / 2), int(py - n / 2)), img)


# ===================================================================== Coco the toucan

T_BLACK = (34, 32, 40)
T_BIB = (255, 236, 150)
T_BEAK = (255, 146, 40)
T_BEAK_L = (255, 196, 70)
T_RED = (226, 60, 50)
T_EYE = (90, 176, 255)


def toucan(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", fly=0.0, seed=1.0, look=(0.0, 0.0)):
    """Coco the toco toucan. (x, y) = feet when perched. fly 0..1 flaps the wings."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    flap = math.sin(t * 17) if fly > 0.01 else 0.0
    # back wing when flying
    if fly > 0.01:
        a = -55 * flap * fly
        c.poly(rot([(-6, -66), (-30, -128), (-62, -120), (-40, -64)], -6, -66, a), (20, 20, 28))
    # tail
    c.poly([(-26, -34), (-64, -6), (-56, 4), (-18, -24)], T_BLACK)
    c.poly([(-26, -24), (-40, -20), (-28, -10)], (240, 240, 240), w=2)
    # feet
    if fly < 0.5:
        for fx in (-6, 8):
            c.line([(fx, -14), (fx, 0)], (90, 120, 200), 4)
            c.line([(fx - 6, 0), (fx + 8, 0)], (90, 120, 200), 4)
    # body + head
    c.ellipse(-4, -48, 30, 38, T_BLACK)
    c.circle(10, -86, 23, T_BLACK)
    c.ellipse(14, -68, 17, 15, T_BIB, ol=None)
    c.ellipse(4, -36, 16, 8, T_RED, ol=None)
    # folded wing
    if fly <= 0.01:
        c.ellipse(-12, -50, 20, 30, (20, 20, 28))
        c.arc(-12, -50, 14, 22, 30, 150, (60, 60, 70), 2)
    # eye
    ex, ey = 16, -92
    c.circle(ex, ey, 9, T_EYE, w=2)
    if eyes == "closed":
        c.arc(ex, ey, 6, 4, 200, 340, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 6, 5, 200, 340, OUT, 3)
    else:
        r = 6 if eyes == "wide" else 4.5
        c.circle(ex + 1 + look[0] * 2, ey + look[1] * 2, r, (20, 20, 20), ol=None)
        c.circle(ex - 1, ey - 2, 1.6, (255, 255, 255), ol=None)
    # beak: the lower jaw opens with the speech
    jaw = -16 * clamp(mouth)
    lower = rot([(26, -80), (70, -80), (104, -76), (68, -66), (26, -72)], 26, -78, -jaw)
    c.poly(lower, T_BEAK)
    if mouth > 0.1:
        c.poly([(28, -79), lower[1], lower[2], (96, -80), (60, -82)], (150, 40, 40), ol=None)
    upper = [(22, -102), (56, -108), (92, -96), (108, -80), (100, -78), (66, -82), (24, -80)]
    c.poly(upper, T_BEAK)
    c.line([(30, -98), (60, -103), (90, -92)], T_BEAK_L, 4)
    c.poly([(96, -92), (108, -80), (100, -78), (92, -82)], T_BLACK, ol=None)
    c.line([(28, -82), (66, -82), (100, -78)], OUT, 2)
    # front wing when flying
    if fly > 0.01:
        a = 60 * flap * fly
        c.poly(rot([(-4, -62), (-20, -132), (-56, -126), (-36, -58)], -4, -62, a), (30, 30, 38))
    c.pop()


# ===================================================================== Mossy the sloth

FUR = (156, 130, 102)
FUR_D = (118, 96, 74)
FACE = (238, 224, 196)
MASK = (92, 66, 50)
MOSS = (130, 156, 96)


def sloth(c, x, y, s=1.0, t=0.0, mouth=0.0, eyes="sleepy", wave=0.0, sway=1.0, seed=2.0):
    """Mossy the three-toed sloth hanging from a branch. (x, y) = the branch between his hands.
    eyes: sleepy | closed | open | happy. wave 0..1 lifts his right arm in a slooow wave."""
    sw = math.sin(t * 0.9) * 4 * sway
    c.push(x, y, s)
    hx = sw
    # legs hooked up on the branch behind
    for side in (-1, 1):
        c.stroke([(side * 30 + hx, 150), (side * 66, 60), (side * 70, 6)], FUR_D, 20)
        for k in range(3):
            c.arc(side * 70 + k * 4 - 4, -2, 6, 8, 180, 360, (60, 44, 34), 3)
    # body
    c.ellipse(hx, 110, 50, 58, FUR)
    for (mx, my, r) in ((-20, 96, 12), (16, 126, 10), (24, 88, 7), (-10, 140, 8)):
        c.ellipse(hx + mx, my, r, r * 0.7, MOSS, ol=None)
    # arms
    for side in (-1, 1):
        lift = wave if side > 0 else 0.0
        if lift > 0.01:
            ang = -40 * lift + 10 * math.sin(t * 1.4) * lift
            hand = rot([(side * 74, 30)], side * 30 + hx, 70, ang)[0]
            c.stroke([(side * 30 + hx, 76), hand], FUR, 20)
            for k in range(3):
                c.line([(hand[0] - 6 + k * 6, hand[1]), (hand[0] - 8 + k * 6, hand[1] - 12)], (60, 44, 34), 3)
        else:
            c.stroke([(side * 30 + hx, 76), (side * 40, 4)], FUR, 20)
            for k in range(3):
                c.arc(side * 40 + k * 5 - 5, -2, 6, 9, 180, 360, (60, 44, 34), 3)
    # head
    hy = 60
    c.circle(hx, hy, 36, FUR)
    c.ellipse(hx, hy + 4, 28, 24, FACE, ol=None)
    for side in (-1, 1):
        pts = [(hx + side * 4, hy - 6), (hx + side * 24, hy - 4), (hx + side * 26, hy + 6), (hx + side * 8, hy + 4)]
        c.poly(pts, MASK, ol=None)
        ex, ey = hx + side * 13, hy - 1
        if eyes == "closed" or (eyes != "closed" and D.blink(t * 0.5, seed)):
            c.arc(ex, ey, 5, 3, 0, 180, (30, 20, 20), 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 2, 5, 4, 200, 340, (30, 20, 20), 2.5)
        else:
            c.circle(ex, ey, 4.5, (20, 16, 16), ol=None)
            c.circle(ex - 1, ey - 1.5, 1.4, (255, 255, 255), ol=None)
            if eyes == "sleepy":
                c.rect(ex - 6, ey - 6, ex + 6, ey - 1, MASK, ol=None)
    c.ellipse(hx, hy + 12, 7, 5, (60, 40, 34), ol=None)
    if mouth > 0.08:
        c.ellipse(hx, hy + 22, 7, 2 + 6 * clamp(mouth), (120, 50, 50), w=2)
    else:
        c.arc(hx, hy + 18, 10, 6, 20, 160, (60, 40, 34), 2.5)
    c.pop()


# ===================================================================== jaguar

J_GOLD = (232, 176, 80)
J_DARK = (196, 136, 56)
J_CREAM = (252, 236, 196)
J_SPOT = (70, 46, 30)


def jaguar(c, x, y, s=1.0, face=1, t=0.0, eye=0.0, yawn=0.0):
    """A big jaguar lying asleep on the forest floor. (x, y) = ground under its middle.
    eye 0..1 opens one eye; yawn 0..1 opens the mouth."""
    breathe = 1 + 0.03 * math.sin(t * 1.6)
    c.push(x, y, s, flip=face < 0)
    # tail curled along the ground
    c.stroke([(-110, -28), (-150, -12), (-130, -4), (-60, -6)], J_GOLD, 16)
    for u in (0.3, 0.6):
        c.circle(lerp(-150, -80, u), -8, 4, J_SPOT, ol=None)
    c.ellipse(0, -42 * breathe, 124, 44 * breathe, J_GOLD)
    c.ellipse(10, -20, 100, 18, J_CREAM, ol=None)
    rng = np.random.default_rng(4)
    for _ in range(18):
        sx, sy = rng.uniform(-100, 90), rng.uniform(-72, -30)
        c.circle(sx, sy * breathe, rng.uniform(6, 10), None, ol=J_SPOT, w=3)
        c.circle(sx, sy * breathe, 2.4, J_SPOT, ol=None)
    # back leg + front paws
    c.ellipse(-70, -26, 40, 24, J_DARK)
    c.ellipse(110, -8, 44, 12, J_GOLD)
    c.ellipse(136, -6, 20, 9, J_CREAM)
    # head
    hx, hy = 116, -56
    for ex in (-18, 18):
        c.circle(hx + ex, hy - 30, 11, J_GOLD)
        c.circle(hx + ex, hy - 30, 5, J_SPOT, ol=None)
    c.ellipse(hx, hy, 42, 36, J_GOLD)
    for (sx, sy) in ((-20, -18), (0, -24), (20, -16), (-28, 2)):
        c.circle(hx + sx, hy + sy, 3.5, J_SPOT, ol=None)
    c.ellipse(hx + 14, hy + 14, 22, 15, J_CREAM)
    c.poly([(hx + 24, hy + 4), (hx + 36, hy + 4), (hx + 30, hy + 11)], (90, 50, 50), w=2)
    if yawn > 0.05:
        c.ellipse(hx + 20, hy + 26, 12, 4 + 12 * yawn, (140, 40, 50), w=2)
        c.poly([(hx + 12, hy + 20), (hx + 15, hy + 28), (hx + 18, hy + 20)], (255, 255, 255), ol=None)
        c.poly([(hx + 23, hy + 20), (hx + 26, hy + 28), (hx + 29, hy + 20)], (255, 255, 255), ol=None)
    else:
        c.arc(hx + 24, hy + 18, 8, 5, 20, 160, OUT, 2.5)
    for k, ex in enumerate((hx - 6, hx + 22)):
        if k == 1 and eye > 0.05:
            c.ellipse(ex, hy - 6, 9, 9 * eye, (210, 220, 90), w=2.5)
            c.ellipse(ex + 2, hy - 6, 3, 6 * eye, OUT, ol=None)
        else:
            c.arc(ex, hy - 6, 8, 5, 200, 340, OUT, 3)
    c.pop()


# ===================================================================== small animals

def monkey(c, hx, hy, s=1.0, t=0.0, ang=0.0, face=1, col=(132, 88, 54)):
    """A little monkey hanging by one arm from (hx, hy), swinging by ang (degrees)."""
    a = math.radians(ang)
    L = 52 * s
    sx, sy = hx + math.sin(a) * L, hy + math.cos(a) * L
    c.stroke([(hx, hy), (sx, sy)], col, 10 * s)
    c.circle(hx, hy, 6 * s, col, w=2)
    # tail curl
    c.stroke([(sx - 6 * s * face, sy + 50 * s), (sx - 34 * s * face, sy + 70 * s),
              (sx - 44 * s * face, sy + 50 * s), (sx - 36 * s * face, sy + 40 * s)], col, 7 * s)
    c.ellipse(sx, sy + 34 * s, 20 * s, 26 * s, col)
    c.ellipse(sx, sy + 38 * s, 12 * s, 16 * s, (214, 176, 130), ol=None)
    c.stroke([(sx + 10 * s * face, sy + 26 * s), (sx + 24 * s * face, sy + 44 * s)], col, 8 * s)
    # head
    px, py = sx + 10 * s * face, sy + 2 * s
    for ex in (-1, 1):
        c.circle(px + ex * 17 * s, py, 7 * s, (214, 176, 130), w=2)
    c.circle(px, py, 16 * s, col)
    c.ellipse(px + 2 * s * face, py + 3 * s, 11 * s, 10 * s, (232, 200, 160), ol=None)
    for ex in (-5, 7):
        c.circle(px + ex * s * face, py - 1 * s, 2.4 * s, OUT, ol=None)
    c.arc(px + 2 * s * face, py + 6 * s, 5 * s, 3 * s, 20, 160, OUT, 2)


def macaw(c, x, y, s=1.0, face=1, t=0.0):
    """A scarlet macaw perched. (x, y) = feet."""
    c.push(x, y, s, flip=face < 0)
    bob = math.sin(t * 3) * 2
    c.poly([(-6, -30), (-30, 40), (-18, 44), (6, -24)], (220, 40, 40))
    c.poly([(-12, -10), (-26, 40), (-20, 42)], (60, 110, 220), ol=None)
    c.ellipse(0, -40 + bob, 18, 30, (226, 44, 44))
    c.ellipse(-8, -34 + bob, 12, 22, (255, 210, 60), ol=None)
    c.ellipse(-10, -26 + bob, 10, 16, (60, 110, 220), ol=None)
    c.circle(6, -72 + bob, 15, (226, 44, 44))
    c.ellipse(12, -72 + bob, 8, 7, (255, 255, 255), ol=None)
    c.circle(13, -73 + bob, 2.5, OUT, ol=None)
    c.poly([(18, -80 + bob), (30, -76 + bob), (30, -64 + bob), (20, -66 + bob)], (60, 56, 60), w=2)
    for fx in (-4, 6):
        c.line([(fx, -12), (fx, 0)], (90, 90, 96), 3)
    c.pop()


def eagle(c, x, y, s=1.0, face=1, t=0.0):
    """A harpy eagle perched on top of an emergent tree. (x, y) = feet."""
    c.push(x, y, s, flip=face < 0)
    grey, dark, white = (150, 150, 160), (64, 64, 74), (244, 244, 240)
    c.poly([(-20, -40), (-50, 20), (-26, 22), (-6, -20)], dark)
    c.ellipse(0, -56, 34, 52, white)
    c.ellipse(-16, -60, 22, 46, dark)
    c.ellipse(0, -96, 34, 10, dark, ol=None)
    c.circle(6, -118, 26, grey)
    for k in (-1, 1):
        c.poly([(-4 + 8 * k, -140), (-14 + 10 * k, -168), (4 + 8 * k, -144)], dark)
    c.circle(14, -120, 6, (255, 255, 255), w=2)
    c.circle(15, -120, 3, OUT, ol=None)
    c.poly([(26, -118), (44, -112), (40, -98), (30, -104)], (50, 50, 56), w=2)
    for fx in (-10, 10):
        c.line([(fx, -10), (fx, 0)], (240, 200, 60), 6)
        c.line([(fx - 8, 0), (fx + 10, 0)], (240, 200, 60), 4)
    c.pop()


def ant(c, x, y, s=1.0, t=0.0, leaf=True, face=1):
    """A leafcutter ant carrying a bit of leaf. (x, y) = ground."""
    step = math.sin(t * 22 + x * 0.1)
    c.push(x, y, s, flip=face < 0)
    for k, lx in enumerate((-6, 0, 6)):
        d = step * 3 * (1 if k % 2 else -1)
        c.line([(lx, -6), (lx - 4 + d, 0)], (60, 30, 20), 1.5, cap=False)
        c.line([(lx, -6), (lx + 4 - d, 0)], (60, 30, 20), 1.5, cap=False)
    for bx, r in ((-9, 5), (0, 3.6), (8, 4)):
        c.circle(bx, -7, r, (150, 60, 40), ol=(60, 30, 20), w=1.2)
    if leaf:
        c.line([(10, -10), (12, -20)], (60, 30, 20), 1.2, cap=False)
        c.poly([(4, -20), (22, -30), (18, -14)], (110, 190, 80), ol=(40, 90, 40), w=1.2)
    c.pop()


def dart_frog(c, x, y, s=1.0, t=0.0, face=1):
    """A tiny blue poison dart frog. (x, y) = where it sits."""
    puff = 1 + 0.08 * max(0, math.sin(t * 5))
    c.push(x, y, s, flip=face < 0)
    blue, dark = (50, 120, 236), (20, 30, 60)
    c.ellipse(-10, -4, 12, 6, blue)
    c.ellipse(0, -16, 22, 14 * puff, blue)
    for (sx, sy, r) in ((-10, -20, 3), (2, -24, 2.5), (10, -14, 3), (-4, -12, 2)):
        c.circle(sx, sy, r, dark, ol=None)
    c.circle(12, -26, 6, blue)
    c.circle(13, -26, 3.4, dark, ol=None)
    c.circle(12, -27, 1, (255, 255, 255), ol=None)
    c.ellipse(16, -2, 8, 4, blue)
    c.pop()


def big_leaf(c, x, y, s=1.0, ang=0.0, water=0.0, col=(70, 160, 80)):
    """A giant leaf used as an umbrella. (x, y) = where the stem is held; ang tips it (deg).
    water 0..1 fills its cupped middle with rain."""
    pts = [(-120, -6), (-80, -34), (0, -46), (80, -34), (124, -6), (60, 4), (0, 8), (-60, 4)]
    pts = [(px * s, py * s) for px, py in pts]
    stem = [(0, 0), (0, 70 * s)]
    pts = rot([(x + px, y + py) for px, py in pts], x, y, ang)
    c.line(rot([(x + a, y + b) for a, b in stem], x, y, ang), (60, 120, 60), 5 * s)
    c.poly(pts, col, w=3)
    vein = rot([(x - 110 * s, y - 6 * s), (x + 116 * s, y - 6 * s)], x, y, ang)
    c.line(vein, mix(col, (255, 255, 255), 0.3), 3 * s)
    if water > 0.02:
        ww = 90 * s * (0.4 + 0.6 * water)
        wpts = rot([(x - ww, y - 8 * s - 14 * s * water), (x + ww, y - 8 * s - 14 * s * water),
                    (x + ww * 0.8, y - 6 * s), (x - ww * 0.8, y - 6 * s)], x, y, ang)
        c.poly(wpts, (120, 186, 246), ol=(60, 120, 200), w=2)


def rain(c, t, x0, y0, x1, y1, n=70, k=1.0, seed=3, col=(200, 226, 255), speed=900, length=26):
    """Falling rain streaks inside a box."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    hh = y1 - y0
    for i in range(int(n * k)):
        x = rng.uniform(x0, x1)
        ph = rng.random()
        y = y0 + ((t * speed / hh + ph) % 1.0) * hh
        c.line([(x, y), (x - 4, y + length)], col, 2, cap=False)


# ===================================================================== rainforests on Earth

# simplified outlines (lon, lat) of the big tropical rainforests
AMAZON = [(-79, 1), (-77, -6), (-74, -11), (-68, -14), (-62, -15), (-56, -12), (-50, -8), (-46, -4),
          (-49, 0), (-52, 3), (-58, 5), (-64, 6), (-70, 5), (-75, 4)]
CONGO = [(9, 4), (10, -2), (13, -5), (18, -6), (24, -5), (29, -2), (30, 2), (27, 4.5), (20, 5), (14, 5)]
BORNEO = [(109, 1), (111, -3), (116, -4), (119, 0), (118, 5), (116, 7), (112, 3)]
SUMATRA = [(95, 5), (98, 2), (102, -2), (106, -5), (104, -6), (100, -3), (96, 2)]
GUINEA = [(132, -1), (138, -2), (146, -5), (150, -8), (144, -9), (138, -8), (133, -4)]
CENTRAL = [(-92, 17), (-88, 16), (-84, 12), (-82, 9), (-78, 8), (-80, 10), (-84, 15), (-90, 18)]
FORESTS = [AMAZON, CONGO, BORNEO, SUMATRA, GUINEA, CENTRAL]
RF_COL = (24, 120, 46)
RF_LINE = (190, 255, 150)


def forests_on_globe(c, x, y, r, lon0, lat0, k=1.0, t=0.0, roll=0.0):
    """Paint the rainforests as dark green patches on a globe (only patches facing us)."""
    if k <= 0.01:
        return
    col = mix((120, 190, 92), RF_COL, k)
    for poly in FORESTS:
        pts = [K.globe_xy(x, y, r, lo, la, lon0, lat0, roll) for lo, la in poly]
        if all(p[2] for p in pts):
            c.poly([(p[0], p[1]) for p in pts], col, ol=mix(col, RF_LINE, 0.5 + 0.5 * math.sin(t * 5)), w=2)


def equator_on_globe(c, x, y, r, lon0, lat0, k=1.0, roll=0.0, col=(255, 210, 60), w=5, front=True):
    """Dashed equator line around a globe, drawn on as k goes 0 -> 1."""
    if k <= 0.01:
        return
    pts = []
    for i in range(int(90 * k) + 1):
        lo = lon0 - 90 + 180 * i / 90 if front else lon0 + 90 + 180 * i / 90
        pts.append(K.globe_xy(x, y, r, lo, 0, lon0, lat0, roll))
    for i in range(0, len(pts) - 1, 2):
        a, b = pts[i], pts[i + 1]
        if a[2] == front and b[2] == front:
            c.line([a[:2], b[:2]], col, w)


def forests_on_map(c, v, k=1.0, t=0.0, only=None):
    if k <= 0.01:
        return
    col = mix((120, 190, 92), RF_COL, k)
    for poly in (only or FORESTS):
        pts = [v.xy(lo, la) for lo, la in poly]
        c.poly(pts, col, ol=mix(col, RF_LINE, 0.5 + 0.5 * math.sin(t * 5)), w=2.5)


def equator_on_map(c, v, k=1.0, col=(255, 210, 60)):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = v.rect()
    _, ey = v.xy(0, 0)
    xe = lerp(x0, x1, ease(k))
    x = x0
    while x < xe:
        c.line([(x, ey), (min(x + 18, xe), ey)], col, 5, cap=False)
        x += 30


# ===================================================================== the tall forest

FH = 2880            # height of the whole forest (world px); x is screen px
ROOF = 600           # top of the canopy (the "roof")
CAN_BOT = 1320       # canopy -> understorey
UND_BOT = 2060       # understorey -> forest floor
GROUND = 2700        # forest floor surface
BRANCH_Y = 1140      # the sloth's branch
TOP_CAM, CAN_CAM, UND_CAM, FLOOR_CAM = 0.0, 780.0, 1480.0, 2160.0
EMERGENTS = [(170, 300, 1.25), (1010, 250, 1.1)]       # (x, crown y, size)


def branch_y(x):
    """Height of the sloth's branch at screen x."""
    return BRANCH_Y + 0.00012 * (x - 640) ** 2 - 0.02 * (x - 640)


def _crown(c, x, y, s, cols, seed):
    rng = np.random.default_rng(seed)
    blobs = [(rng.uniform(-110, 110) * s, rng.uniform(-50, 40) * s, rng.uniform(48, 74) * s) for _ in range(9)]
    for bx, by, r in blobs:
        c.circle(x + bx, y + by, r, cols[0])
    for bx, by, r in blobs:
        c.circle(x + bx, y + by, r - 3, cols[0], ol=None)
    for bx, by, r in blobs:
        c.circle(x + bx - r * 0.2, y + by - r * 0.25, r * 0.55, cols[1], ol=None)


def _palm(c, x, y, s, col):
    """An understorey palm / fern: fronds fanning out from (x, y)."""
    for a in range(-80, 81, 26):
        ang = math.radians(a - 90)
        tip = (x + math.cos(ang) * 150 * s, y + math.sin(ang) * 120 * s + abs(a) * 0.9 * s)
        mid = (x + math.cos(ang) * 80 * s, y + math.sin(ang) * 80 * s)
        c.line([(x, y), mid, tip], mix(col, (0, 0, 0), 0.3), 4 * s)
        for u in np.linspace(0.25, 0.95, 6):
            px, py = lerp(x, tip[0], u), lerp(y, tip[1], u) - 10 * s * math.sin(u * math.pi)
            c.ellipse(px, py, 18 * s * (1.1 - u), 7 * s, col, ol=None)


def _leafy(c, x, y, s, col, ang=0):
    pts = rot([(x - 50 * s, y), (x, y - 24 * s), (x + 60 * s, y), (x, y + 22 * s)], x, y, ang)
    c.poly(pts, col, w=2)
    c.line(rot([(x - 46 * s, y), (x + 56 * s, y)], x, y, ang), mix(col, (255, 255, 255), 0.25), 2)


@lru_cache(None)
def forest_image():
    """The whole rainforest from the emergent tree tops (top) down to the forest floor (bottom)."""
    c = Canvas(D.gradient(W * SS, FH * SS, [
        (0, (126, 196, 246)), (ROOF / FH * 0.8, (196, 232, 250)), (ROOF / FH, (120, 186, 104)),
        ((ROOF + 300) / FH, (84, 156, 82)), (CAN_BOT / FH, (56, 120, 70)), (UND_BOT / FH, (36, 82, 56)),
        (GROUND / FH, (26, 56, 42)), (1, (40, 30, 24))]), size=(W, FH))
    rng = np.random.default_rng(11)
    # sky details above the roof
    D.cloud(c, 640, 120, 1.1)
    D.cloud(c, 420, 210, 0.6)
    D.cloud(c, 860, 90, 0.7)
    # far trunks (dim), then near trunks
    for x in range(40, W, 95):
        xx = x + rng.uniform(-20, 20)
        c.rect(xx - 12, ROOF + 200, xx + 12, GROUND, (44, 84, 56), ol=None)
    trunk, trunk_d = (120, 84, 56), (90, 60, 40)
    for x, cy, s in EMERGENTS:
        c.poly([(x - 34, cy + 40), (x + 34, cy + 40), (x + 46, GROUND), (x - 46, GROUND)], trunk, w=3)
        c.line([(x - 10, cy + 80), (x - 14, GROUND - 40)], trunk_d, 4)
        # buttress roots
        for side in (-1, 1):
            c.poly([(x + side * 40, GROUND - 220), (x + side * 150, GROUND + 6), (x + side * 40, GROUND + 6)],
                   trunk, w=3)
    for x in (420, 760, 640, 300, 900):
        c.poly([(x - 20, ROOF + 40), (x + 20, ROOF + 40), (x + 28, GROUND), (x - 28, GROUND)], mix(trunk, (40, 60, 40), 0.35), w=3)
    # emergent crowns poking out above the roof
    for i, (x, cy, s) in enumerate(EMERGENTS):
        _crown(c, x, cy, s, [(70, 150, 70), (110, 190, 90)], 30 + i)
    # the canopy: a thick leafy roof
    for row, (yy, cols) in enumerate(((ROOF + 40, [(64, 146, 64), (110, 190, 86)]),
                                      (ROOF + 200, [(54, 130, 60), (90, 168, 76)]),
                                      (ROOF + 380, [(46, 116, 56), (76, 150, 70)]))):
        for x in range(-60, W + 120, 150):
            _crown(c, x + rng.uniform(-30, 30) + row * 50, yy + rng.uniform(-30, 30), 0.85, cols,
                   100 + row * 20 + x)
    # sun dapples in the canopy
    for _ in range(40):
        c.ellipse(rng.uniform(0, W), rng.uniform(ROOF + 520, CAN_BOT), rng.uniform(10, 26), rng.uniform(4, 9),
                  (150, 206, 110), ol=None)
    # vines and lianas hanging down
    for x in (120, 360, 560, 980, 1180):
        top = ROOF + 300 + rng.uniform(0, 200)
        bot = top + rng.uniform(500, 1100)
        pts = [(x + 14 * math.sin(u * 7), lerp(top, bot, u)) for u in np.linspace(0, 1, 20)]
        c.line(pts, (60, 110, 50), 5)
        for u in np.linspace(0.1, 0.95, 8):
            px, py = pts[int(u * 19)]
            c.ellipse(px + 8, py, 10, 5, (80, 150, 70), ol=None)
    # light shafts through the understorey
    for x in (250, 700, 1080):
        c.poly([(x - 30, CAN_BOT - 60), (x + 30, CAN_BOT - 60), (x + 160, GROUND), (x + 40, GROUND)],
               (70, 130, 84), ol=None)
    # understorey: palms, young trees and big leaves in the shade
    for i, x in enumerate((60, 330, 560, 820, 1080, 1250)):
        _palm(c, x, UND_BOT - rng.uniform(40, 260), 1.0 + 0.2 * (i % 2), (54, 124, 66))
    for _ in range(30):
        _leafy(c, rng.uniform(0, W), rng.uniform(CAN_BOT + 60, UND_BOT), rng.uniform(0.6, 1.1),
               (60, 132, 70), rng.uniform(-40, 40))
    # forest floor: ground, leaf litter, roots, mushrooms
    c.rect(-10, GROUND, W + 10, FH + 10, (74, 52, 36), ol=None)
    c.line([(0, GROUND), (W, GROUND)], (40, 28, 20), 4)
    for _ in range(160):
        x, y = rng.uniform(0, W), rng.uniform(GROUND + 4, FH)
        col = [(150, 96, 50), (120, 80, 44), (176, 120, 60), (96, 70, 40)][int(rng.integers(4))]
        c.ellipse(x, y, rng.uniform(8, 16), rng.uniform(3, 6), col, ol=None)
    for x in (480, 1180):
        for k in range(3):
            mx = x + k * 18
            c.rect(mx - 3, GROUND - 16 - k * 4, mx + 3, GROUND, (240, 230, 210), w=1.5)
            c.ellipse(mx, GROUND - 18 - k * 4, 11, 6, (226, 120, 70), w=1.5)
    for x in (40, 700, 1240):
        _palm(c, x, GROUND, 0.7, (46, 104, 58))
    # the sloth's long branch in the canopy (from the left emergent trunk)
    xs = np.linspace(150, 1060, 40)
    top = [(x, branch_y(x) - 13) for x in xs]
    bot = [(x, branch_y(x) + 13 - 6 * (x - 150) / 910) for x in xs[::-1]]
    c.poly(top + bot, (128, 90, 58), w=3)
    for x in (380, 700, 930):
        _leafy(c, x, branch_y(x) - 18, 0.6, (80, 160, 80), -20)
    return c.img


def forest_view(cam):
    """Fresh canvas showing the forest from world height cam (top of the screen) down."""
    cam = clamp(cam, 0, FH - H)
    y0 = int(round(cam * SS))
    return Canvas(forest_image().crop((0, y0, W * SS, y0 + H * SS)))


FRONT_LEAVES = [(40, 760, 1.5, 20), (1250, 1040, 1.6, -30), (80, 1420, 1.7, 10), (1230, 1800, 1.5, 200),
                (30, 2100, 1.6, -10), (1240, 2460, 1.4, 190), (60, 2860, 1.6, 0), (1240, 300, 1.3, 210)]


def front_leaves(c, cam, k=1.0):
    """Big blurry-close leaves in front that move faster than the forest (depth)."""
    for x, y, s, a in FRONT_LEAVES:
        sy = y - cam * 1.25
        if -200 < sy < H + 200:
            _leafy(c, x, sy, s * 1.6, (34, 92, 48), a)


# ===================================================================== layer gauge

LAYERS = [("Emergent", (140, 200, 246)), ("Canopy", (96, 176, 84)), ("Understorey", (60, 128, 72)),
          ("Forest floor", (98, 70, 48))]


def level_of(world_y):
    """0 = forest floor ... 3 = emergent layer, for a height in the forest."""
    return K.track(world_y, [(ROOF - 200, 3.0), ((ROOF + CAN_BOT) / 2, 2.0), ((CAN_BOT + UND_BOT) / 2, 1.0),
                             ((UND_BOT + GROUND) / 2, 0.0)])


def gauge(c, x, y, k, level, t=0.0):
    """'Floors of a building' gauge: 4 stacked floors with names and a marker at level (0..3).
    (x, y) = top-left. k pops it in."""
    if k <= 0.01:
        return
    w, fh = 186, 58
    c.push(x + w / 2, y, K.pop(k))
    x0 = -w / 2
    # roof
    c.poly([(x0 - 10, 0), (0, -34), (w / 2 + 10, 0)], (200, 80, 70), w=3)
    cur = int(round(level))
    for i, (name, col) in enumerate(LAYERS):
        fy = i * fh
        li = 3 - i
        lit = li == cur
        c.rect(x0, fy, x0 + w, fy + fh, mix(col, (255, 255, 255), 0.25 if lit else 0.0), w=3)
        if lit:
            c.rect(x0 + 3, fy + 3, x0 + w - 3, fy + fh - 3, None, ol=(255, 236, 90), w=4)
        K.text(c, 0, fy + fh / 2, name, 22 if len(name) < 11 else 20, (255, 255, 255), stroke=3)
    # marker: a red arrow pointing at the friends' level
    my = (3 - clamp(level, 0, 3)) * fh + fh / 2
    c.poly([(x0 - 34, my - 14), (x0 - 8, my), (x0 - 34, my + 14)], (226, 70, 80), w=3)
    c.pop()


# ===================================================================== small icons

def icon_rain(c, x, y, r, t=0.0):
    """Warm and rainy: a cloud with rain and a sun peeking out."""
    c.circle(x, y, r * 0.98, (150, 206, 246), ol=None)
    c.circle(x + r * 0.45, y - r * 0.4, r * 0.32, (255, 210, 70), w=2)
    for dx, dy, rr in ((-0.35, -0.1, 0.3), (0.05, -0.25, 0.38), (0.4, -0.05, 0.28), (0.0, 0.05, 0.3)):
        c.circle(x + dx * r, y + dy * r, rr * r, (236, 242, 250), ol=None)
    c.ellipse(x, y + 0.05 * r, 0.7 * r, 0.22 * r, (236, 242, 250), ol=None)
    for k in range(4):
        dx = -0.45 + 0.3 * k
        u = (t * 1.5 + k * 0.3) % 1
        c.line([(x + dx * r, y + (0.35 + 0.35 * u) * r), (x + (dx - 0.06) * r, y + (0.5 + 0.35 * u) * r)],
               (70, 140, 230), 3)


def icon_amazon(c, x, y, r, t=0.0):
    """South America with the Amazon rainforest in dark green."""
    c.circle(x, y, r, (90, 160, 226), ol=None)
    v = K.MapView(-60, -21, 1.0)
    sc = r / 132.0
    c.push(x, y, sc)
    for poly, col in ((K.SOUTH_AMERICA, (150, 200, 110)), (AMAZON, RF_COL)):
        pts = []
        for lo, la in poly:
            px, py = v.xy(lo, la)
            pts.append(((px - W / 2) * 1.0, (py - H / 2) * 1.0))
        c.poly(pts, col, w=2)
    c.pop()


def icon_layers(c, x, y, r, t=0.0):
    """Tiny 4-floor tree building with a monkey high up."""
    w = r * 1.2
    hh = r * 0.42
    for i, (name, col) in enumerate(LAYERS):
        fy = y - 2 * hh + i * hh
        c.rect(x - w / 2, fy, x + w / 2, fy + hh, col, w=2)
    c.circle(x + r * 0.15, y - hh * 0.5, r * 0.18, (132, 88, 54), w=2)
    c.circle(x + r * 0.15, y - hh * 0.45, r * 0.1, (232, 200, 160), ol=None)
    K.star(c, x - r * 0.25, y - hh * 0.5, r * 0.14, (255, 236, 90), ol=OUT)


def icon_cold(c, x, y, r, t=0.0):
    """Cold and dry: a snowflake over cracked sand."""
    c.rect(x - r * 0.8, y + r * 0.2, x + r * 0.8, y + r * 0.6, (236, 210, 150), r=6, w=2)
    c.line([(x - r * 0.3, y + r * 0.25), (x - r * 0.1, y + r * 0.55)], (180, 150, 100), 2)
    c.line([(x + r * 0.3, y + r * 0.25), (x + r * 0.2, y + r * 0.55)], (180, 150, 100), 2)
    for a in range(0, 180, 60):
        dx, dy = math.cos(math.radians(a)) * r * 0.45, math.sin(math.radians(a)) * r * 0.45
        c.line([(x - dx, y - r * 0.3 - dy), (x + dx, y - r * 0.3 + dy)], (110, 170, 230), 5)
    c.circle(x, y - r * 0.3, r * 0.08, (110, 170, 230), ol=None)
