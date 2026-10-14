"""Episode 9 props: Sir Rufus the weather-vane rooster, Hazel the squirrel, the farm on the hill
in four seasons (cached), the tree through the year, rainbow, the Sun and the tilted Earth, insets
and icons."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K

TAU = 2 * math.pi
TILT = 23.5


def squash_x(c, k):
    """Scale the current transform horizontally by k (k < 0 mirrors): for spinning things."""
    ox, oy, sx, sy = c.tf[-1]
    c.tf[-1] = (ox, oy, sx * k, sy)


def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


# ================================================================== Sir Rufus

GOLD = (238, 176, 66)
GOLD_D = (204, 134, 44)
GOLD_L = (255, 222, 130)
HACKLE = (244, 140, 52)
COMB = (226, 52, 54)
BEAK = (250, 204, 70)
LEG = (240, 186, 60)
TAILS = [(40, 120, 110), (34, 86, 104), (196, 92, 40), (70, 140, 84), (32, 70, 88)]


def rooster(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", flap=0.0, look=(0.0, 0.0), squash=1.0,
            proud=0.0, seed=1.0):
    """Sir Rufus (origin: between his feet). face 1 = looking right. squash: horizontal scale while
    the wind turns him (cos of the vane angle; its sign also mirrors him). flap 0..1 lifts a wing."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    squash_x(c, squash)
    breathe = math.sin(t * 2.2 + seed) * 1.5
    # legs + toes
    for lx in (-9, 9):
        c.stroke([(lx, -42), (lx - 2, -4)], LEG, 4)
        for dx in (-9, 0, 10):
            c.line([(lx - 2, -3), (lx - 2 + dx, 0)], LEG, 3)
    # tail: big sickle feathers fanning up and back
    for i, col in enumerate(TAILS):
        a = -0.5 + i * 0.32
        wav = math.sin(t * 2.5 + i) * 3
        pts = []
        for j in range(9):
            u = j / 8
            ang = math.radians(200 + 70 * u + i * 12)
            rr = 40 + 70 * u
            pts.append((-34 + math.cos(ang) * rr * 0.7 - 20 * u, -84 + math.sin(ang) * rr * (0.9 + 0.1 * a)
                        + 40 * u * u + wav * u))
        c.stroke(pts, col, 13 - i)
    # body
    c.ellipse(0, -72 + breathe, 46 + 3 * proud, 36, GOLD)
    c.ellipse(10, -62 + breathe, 26, 18, GOLD_L, ol=None)
    for k in range(3):
        c.arc(-4 + k * 14, -60 + breathe, 10, 6, 20, 160, GOLD_D, 2)
    # wing (lifts with flap)
    wing = [(14, -86), (-18, -88), (-40, -74), (-34, -58), (-6, -54), (18, -66)]
    wing = rot(wing, 12, -82, -70 * flap)
    c.poly([(px, py + breathe) for px, py in wing], GOLD_D)
    for k in range(3):
        fx, fy = rot([(-30 + 10 * k, -66)], 12, -82, -70 * flap)[0]
        c.line([(fx, fy + breathe), (fx - 8, fy + 8 + breathe)], (170, 104, 34), 2)
    # neck hackle + head
    hy = -134 + breathe - 6 * proud
    c.poly([(4, -98 + breathe), (36, -104 + breathe), (46, hy + 10), (22, hy - 6), (10, hy + 12)], HACKLE)
    for k in range(4):
        c.line([(14 + 7 * k, hy + 18), (10 + 7 * k, -96 + breathe)], (220, 110, 40), 2)
    hx = 32
    # comb
    for dx, dy, r in ((-10, -16, 8), (0, -21, 9), (10, -18, 8), (18, -12, 6)):
        c.circle(hx + dx, hy + dy, r, COMB)
    c.circle(hx, hy, 18, GOLD)
    # beak (opens with mouth)
    m = clamp(mouth) * 9
    c.poly([(hx + 14, hy - 4), (hx + 32, hy + 1), (hx + 14, hy + 3)], BEAK, w=2)
    c.poly([(hx + 14, hy + 4), (hx + 28, hy + 5 + m), (hx + 13, hy + 9 + m * 0.6)], mix(BEAK, (200, 140, 40), 0.3),
           w=2)
    # wattle
    c.ellipse(hx + 12, hy + 18 + m * 0.5, 6, 10, COMB, w=2)
    # eye
    ex, ey = hx + 6, hy - 4
    if eyes == "closed":
        c.arc(ex, ey, 5, 3.5, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 2, 5, 4, 200, 340, OUT, 2.5)
    elif eyes == "proud":
        c.circle(ex, ey, 5.5, (255, 255, 255), w=2)
        c.circle(ex + 1.5 + look[0] * 1.5, ey + 1, 2.8, (30, 24, 30), ol=None)
        c.line([(ex - 6, ey - 2), (ex + 7, ey - 1)], GOLD_D, 3)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        c.circle(ex, ey, 5.5 * big, (255, 255, 255), w=2)
        c.circle(ex + 1.5 + look[0] * 1.8, ey + look[1] * 1.8, 2.8 * big, (30, 24, 30), ol=None)
        c.circle(ex + 2.5, ey - 1.5, 1.0, (255, 255, 255), ol=None)
    # metal shine
    c.arc(-12, -84 + breathe, 22, 12, 200, 260, (255, 246, 210), 3)
    c.pop()


def vane(c, x, y, h=60, s=1.0, ang=0.0, t=0.0, letters=True):
    """Weather-vane post standing on a roof at (x, y); returns the top (where Rufus stands).
    ang: how far the vane has turned (radians, used for the arrow's squash)."""
    c.push(x, y, s)
    c.stroke([(0, 0), (0, -h)], (90, 84, 96), 5)
    # the compass cross (E-W across, N-S in perspective)
    cy = -h * 0.42
    c.line([(-56, cy), (56, cy)], (90, 84, 96), 4)
    c.line([(-24, cy + 12), (24, cy - 12)], (90, 84, 96), 4)
    if letters:
        for L, lx, ly, sz in (("W", -70, cy, 20), ("E", 70, cy, 20), ("N", 34, cy - 18, 15), ("S", -34, cy + 18, 17)):
            K.text(c, lx, ly, L, sz, (255, 255, 255), stroke=3)
    c.circle(0, -h, 6, GOLD, w=2)
    # the arrow the rooster stands on (turns with him)
    k = math.cos(ang)
    c.push(0, -h, 1.0)
    squash_x(c, k if abs(k) > 0.05 else 0.05)
    c.line([(-66, 0), (60, 0)], (90, 84, 96), 4)
    c.poly([(60, -9), (80, 0), (60, 9)], GOLD, w=2)
    c.poly([(-66, 0), (-82, -14), (-58, -14), (-50, 0), (-58, 14), (-82, 14)], GOLD, w=2)
    c.pop()
    c.pop()
    return x, y - h * s


# ===================================================================== Hazel

FUR = (196, 108, 58)
FUR_D = (160, 82, 44)
FUR_L = (226, 146, 86)
CREAM = (250, 226, 190)
ACORN = (176, 120, 60)
ACORN_CAP = (120, 80, 44)


def acorn(c, x, y, r=10):
    c.ellipse(x, y + r * 0.25, r * 0.8, r, ACORN, w=2)
    c.ellipse(x - r * 0.25, y, r * 0.2, r * 0.45, mix(ACORN, (255, 255, 255), 0.3), ol=None)
    c.ellipse(x, y - r * 0.55, r * 0.95, r * 0.45, ACORN_CAP, w=2)
    c.line([(x, y - r * 0.95), (x + r * 0.2, y - r * 1.3)], ACORN_CAP, 2.5)


def hazel(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), hold=True, hop=0.0, seed=2.0,
          wave=0.0):
    """Hazel the red squirrel sitting up (origin: feet). hold: she holds an acorn; wave lifts a paw."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y - hop, s, flip=face < 0)
    sw = math.sin(t * 2.8 + seed) * 4
    # bushy tail
    pts = [(-14, -12), (-42, -34), (-52, -70), (-40 - sw * 0.5, -108), (-12 - sw, -122), (6 - sw, -110)]
    pts = K.spline(pts, 6)
    c.stroke(pts, FUR, 38)
    c.line(pts[2:-2], FUR_L, 16)
    # body
    c.ellipse(0, -38, 24, 32, FUR)
    c.ellipse(8, -34, 13, 22, CREAM, ol=None)
    # feet
    c.ellipse(10, -4, 16, 6, FUR_D, w=2)
    # head
    hx, hy = 12, -78
    for ex, tip in ((-4, (-10, -114)), (12, (10, -116))):
        c.poly([(hx + ex - 8, hy - 12), (hx + tip[0], hy + tip[1] + 78), (hx + ex + 8, hy - 14)], FUR, w=2.5)
        c.line([(hx + tip[0], hy + tip[1] + 78), (hx + tip[0] - 3, hy + tip[1] + 70)], FUR_D, 3)
    c.circle(hx, hy, 20, FUR)
    c.ellipse(hx + 13, hy + 6, 11, 8, CREAM, ol=None)
    c.circle(hx + 23, hy + 3, 3.5, (60, 36, 30), ol=None)
    # eye
    ex, ey = hx + 6, hy - 4
    if eyes == "closed":
        c.arc(ex, ey, 5, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 2, 5, 4, 200, 340, OUT, 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 5.5 * big, 6.5 * big, (30, 24, 30), ol=None)
        c.circle(ex + 1.8 + look[0], ey - 2 + look[1], 1.8, (255, 255, 255), ol=None)
    c.circle(ex - 4, hy + 8, 3.5, (250, 150, 140), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 15, hy + 13, 3.5, 1.5 + 4 * mouth, (120, 40, 50), w=1.5)
    else:
        c.arc(hx + 15, hy + 11, 4, 3, 20, 160, OUT, 2)
    c.line([(hx + 22, hy + 6), (hx + 36, hy + 2)], OUT, 1)
    c.line([(hx + 22, hy + 8), (hx + 36, hy + 10)], OUT, 1)
    # paws + acorn
    if hold:
        acorn(c, 24, -50, 10)
        c.circle(16, -46, 6, FUR, w=2)
        c.circle(28, -44, 6, FUR, w=2)
    if wave > 0.01:
        a = math.sin(t * 9) * 20 * wave
        px, py = rot([(10, -100)], 4, -56, a)[0]
        c.stroke([(4, -56), (px, py)], FUR, 9)
        c.circle(px, py, 6, FUR, w=2)
    elif not hold:
        c.circle(18, -46, 6, FUR, w=2)
    c.pop()


# ================================================================ the tree

BARK = (128, 88, 60)
BARK_D = (100, 66, 44)
CROWN = [(-86, -222, 56), (78, -232, 58), (0, -282, 70), (-30, -206, 62), (42, -196, 58), (-110, -172, 44),
         (108, -176, 44), (-56, -268, 50), (56, -276, 50)]
SEASON_LEAF = {"spring": (150, 212, 110), "summer": (66, 156, 66), "autumn": (234, 138, 48)}


def _branches(c):
    c.poly([(-24, 0), (24, 0), (14, -150), (-12, -150)], BARK)
    for a, b, w in (((0, -140), (-84, -214), 13), ((2, -150), (76, -232), 13), ((0, -150), (2, -284), 13),
                    ((-40, -180), (-118, -176), 9), ((40, -190), (116, -180), 9), ((-20, -230), (-58, -276), 8),
                    ((30, -240), (60, -282), 8)):
        c.stroke([a, b], BARK, w)
    c.line([(-6, -30), (-4, -110)], BARK_D, 3)
    c.line([(8, -20), (6, -90)], BARK_D, 3)


def season_tree(c, x, y, s=1.0, season="summer", t=0.0):
    """The same tree in each season. Origin = base of the trunk."""
    c.push(x, y, s)
    _branches(c)
    if season == "winter":
        for a, b in (((-84, -214), (-30, -170)), ((76, -232), (30, -186)), ((2, -284), (0, -220)),
                     ((-118, -176), (-60, -178)), ((116, -180), (60, -186))):
            c.line([(a[0], a[1] - 7), (lerp(a[0], b[0], 0.7), lerp(a[1], b[1], 0.7) - 7)], (252, 253, 255), 6)
        c.pop()
        return
    col = SEASON_LEAF[season]
    crown = CROWN if season != "autumn" else CROWN[:7]
    for dx, dy, r in crown:
        c.circle(dx, dy, r + 2, col)
    for dx, dy, r in crown:
        c.circle(dx, dy, r - 2, col, ol=None)
    rng = np.random.default_rng(4)
    if season == "spring":
        for _ in range(46):
            dx, dy, r = crown[rng.integers(len(crown))]
            a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.85)
            px, py = dx + math.cos(a) * d, dy + math.sin(a) * d
            for k in range(5):
                b = k * TAU / 5
                c.circle(px + math.cos(b) * 4, py + math.sin(b) * 4, 3.6, (255, 196, 214), ol=None)
            c.circle(px, py, 2.4, (255, 236, 120), ol=None)
    elif season == "summer":
        for _ in range(9):
            dx, dy, r = crown[rng.integers(len(crown))]
            a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.7)
            c.circle(dx + math.cos(a) * d, dy + math.sin(a) * d, 8, (226, 60, 50), w=2)
        for dx, dy, r in crown[:4]:
            c.arc(dx - r * 0.2, dy - r * 0.2, r * 0.6, r * 0.5, 200, 280, (120, 200, 110), 4)
    else:
        for _ in range(40):
            dx, dy, r = crown[rng.integers(len(crown))]
            a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.85)
            col2 = [(250, 200, 70), (220, 80, 50), (240, 160, 60)][rng.integers(3)]
            c.ellipse(dx + math.cos(a) * d, dy + math.sin(a) * d, 7, 5, col2, ol=None)
    c.pop()


def leaf(c, x, y, r, ang, col):
    pts = rot([(x - r, y), (x, y - r * 0.55), (x + r, y), (x, y + r * 0.55)], x, y, ang)
    c.poly(pts, col, w=1.5)
    c.line(rot([(x - r, y), (x + r * 0.8, y)], x, y, ang), mix(col, (0, 0, 0), 0.3), 1.2)


LEAF_COLS = [(240, 150, 50), (226, 90, 50), (250, 200, 70), (200, 110, 40)]


def falling_leaves(c, t, box, n=14, k=1.0, wind=0.0, seed=3, size=9):
    """Leaves drifting down (and sideways in the wind) inside box = (x0, y0, x1, y1)."""
    if k <= 0.01:
        return
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for i in range(int(n * k)):
        sp = rng.uniform(40, 80)
        u = (rng.random() + t * sp / (y1 - y0)) % 1
        yy = y0 + u * (y1 - y0)
        xx = x0 + (rng.random() * (x1 - x0) + 40 * math.sin(t * 1.5 + i) + wind * t * 260) % (x1 - x0)
        leaf(c, xx, yy, size * rng.uniform(0.8, 1.2), math.degrees(t * rng.uniform(1, 3)) + i * 40,
             LEAF_COLS[i % 4])


def snowfall(c, t, box, n=60, k=1.0, seed=2, speed=50):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for i in range(int(n * k)):
        r = rng.uniform(2, 4.5)
        u = (rng.random() + t * speed * (0.6 + r / 6) / (y1 - y0)) % 1
        xx = x0 + rng.random() * (x1 - x0) + 14 * math.sin(t * 1.3 + i)
        c.circle(xx, y0 + u * (y1 - y0), r, (255, 255, 255), ol=(190, 205, 230), w=1)


def petals(c, t, box, n=16, k=1.0, seed=5):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for i in range(int(n * k)):
        u = (rng.random() + t * 0.12) % 1
        xx = x0 + (rng.random() * (x1 - x0) + t * 30 + 30 * math.sin(t * 2 + i)) % (x1 - x0)
        c.ellipse(xx, y0 + u * (y1 - y0), 5, 3, (255, 200, 220), ol=None)


def rain(c, t, box, n=70, k=1.0, seed=3, col=(200, 220, 250), speed=800, length=22, slant=4):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for i in range(int(n * k)):
        x = rng.uniform(x0, x1)
        y = y0 + (rng.random() * (y1 - y0) + t * speed * rng.uniform(0.85, 1.15)) % (y1 - y0)
        c.line([(x, y), (x - slant, y + length)], col, 2.5)


# ============================================================== the farm

GROUND_Y = 540
SKIES = {"spring": [(0, (140, 200, 250)), (1, (226, 242, 255))],
         "summer": [(0, (80, 164, 244)), (1, (196, 232, 255))],
         "autumn": [(0, (110, 170, 230)), (0.8, (242, 222, 196)), (1, (250, 230, 200))],
         "winter": [(0, (160, 182, 212)), (1, (232, 238, 246))],
         "rain": [(0, (112, 120, 142)), (1, (182, 186, 198))]}
GROUNDS = {"spring": ((150, 210, 110), (120, 190, 90)), "summer": ((130, 196, 84), (104, 176, 70)),
           "autumn": ((196, 186, 96), (170, 160, 80)), "winter": ((244, 248, 255), (222, 232, 246)),
           "rain": ((150, 150, 90), (128, 132, 76))}
BARN = (196, 58, 50)
BARN_D = (150, 40, 40)
ROOF = (96, 70, 66)
PEAK = (272, 222)
TREE_XY = (1030, 600)
TREE_S = 1.25
SUNS = {"spring": (1150, 120, 44), "summer": (1120, 84, 52), "autumn": (1160, 150, 42), "winter": (1170, 330, 36)}


def barn(c, snow=False):
    x0, x1, top, bot = 120, 424, 344, 590
    c.rect(x0, top, x1, bot, BARN)
    for xx in range(x0 + 24, x1, 24):
        c.line([(xx, top + 4), (xx, bot - 4)], BARN_D, 2, cap=False)
    c.poly([(x0 - 24, top + 8), (PEAK[0], PEAK[1]), (x1 + 24, top + 8)], ROOF)
    if snow:
        c.poly([(x0 - 24, top + 8), (PEAK[0], PEAK[1]), (x1 + 24, top + 8), (x1 + 10, top + 16),
                (PEAK[0], PEAK[1] + 24), (x0 - 10, top + 16)], (250, 252, 255), w=2)
    # hayloft
    c.rect(PEAK[0] - 30, top - 70, PEAK[0] + 30, top - 14, (60, 40, 40), w=3)
    c.rect(PEAK[0] - 30, top - 70, PEAK[0] + 30, top - 14, None, ol=(255, 250, 240), w=5)
    # big door with a white X
    dx0, dx1, dy0 = 200, 344, 440
    c.rect(dx0, dy0, dx1, bot, BARN_D)
    c.rect(dx0, dy0, dx1, bot, None, ol=(255, 250, 240), w=7)
    c.line([(dx0 + 4, dy0 + 4), (dx1 - 4, bot - 4)], (255, 250, 240), 6)
    c.line([(dx1 - 4, dy0 + 4), (dx0 + 4, bot - 4)], (255, 250, 240), 6)
    c.line([(272, dy0), (272, bot)], (255, 250, 240), 5)


def fence(c, x0, x1, y, col=(236, 222, 196)):
    for xx in range(int(x0), int(x1), 46):
        c.rect(xx - 5, y - 46, xx + 5, y, col, w=2, r=2)
    c.rect(x0 - 10, y - 38, x1, y - 30, col, w=2)
    c.rect(x0 - 10, y - 20, x1, y - 12, col, w=2)


@lru_cache(None)
def farm_bg(season="autumn"):
    return _farm(season, False)


def _farm(season, alt):
    """The farm on the hill: sky, hills, barn (no vane), fence and the big tree, for one season
    (or "rain": autumn under grey clouds). Returns a supersampled image."""
    tree_season = "autumn" if season == "rain" else season
    c = Canvas(D.gradient(W * SS, H * SS, SKIES[season]) if not alt else Image.new("RGB", (W * SS, H * SS),
                                                                                     (255, 0, 255)))
    if season in SUNS:
        sx, sy, sr = SUNS[season]
        pale = season == "winter"
        c.glow(sx, sy, sr * 2.6, sr * 2.6, (255, 250, 220) if not pale else (250, 246, 230),
               SKIES[season][0][1], steps=8)
        c.circle(sx, sy, sr, (255, 226, 100) if not pale else (255, 240, 190), ol=(236, 170, 60), w=3)
    if season != "rain":
        for x, y, s in ((380, 110, 0.9), (720, 70, 0.7), (900, 160, 0.6)):
            D.cloud(c, x, y, s, (255, 255, 255) if season != "winter" else (240, 244, 250))
    else:
        for x, y, s in ((200, 70, 1.6), (520, 50, 1.9), (860, 80, 1.7), (1160, 60, 1.6), (380, 130, 1.3),
                        (720, 140, 1.4), (1020, 150, 1.2)):
            D.cloud(c, x, y, s, (150, 156, 172))
            D.cloud(c, x + 10, y - 8, s * 0.8, (170, 176, 190))
    g0, g1 = GROUNDS[season]
    far = mix(g0, SKIES[season][-1][1], 0.45)
    c.poly([(0, 470), (180, 420), (420, 452), (700, 400), (980, 440), (1280, 410), (1280, 720), (0, 720)], far,
           ol=None)
    c.poly([(0, GROUND_Y), (300, 510), (640, 528), (960, 500), (1280, 520), (1280, 720), (0, 720)], g0)
    c.poly([(0, 640), (400, 610), (800, 630), (1280, 600), (1280, 720), (0, 720)], g1, ol=None)
    # a little path
    c.poly([(560, 720), (610, 600), (640, 532), (660, 532), (700, 600), (760, 720)],
           mix(g0, (230, 210, 170), 0.6 if season != "winter" else 0.1), ol=None)
    barn(c, snow=season == "winter")
    fence(c, 450, 880, 586, (236, 222, 196) if season != "winter" else (220, 210, 196))
    rng = np.random.default_rng(1)
    if season == "spring":
        for _ in range(26):
            D.flower(c, rng.uniform(20, 1260), rng.uniform(600, 700), [(255, 200, 220), (255, 240, 120),
                                                                        (200, 170, 255)][rng.integers(3)], 0.8)
    if season in ("autumn", "rain"):
        for i in range(30):
            leaf(c, TREE_XY[0] + rng.uniform(-200, 200), rng.uniform(600, 700), 7, rng.uniform(0, 180),
                 LEAF_COLS[i % 4])
    if season == "winter":
        c.poly([(TREE_XY[0] - 160, 620), (TREE_XY[0] + 180, 610), (TREE_XY[0] + 140, 640), (TREE_XY[0] - 120, 646)],
               (232, 240, 252), ol=None)
    D.bush(c, 470, 590, 0.8, (90, 160, 80) if season != "winter" else (220, 230, 245))
    season_tree(c, TREE_XY[0], TREE_XY[1], TREE_S, tree_season)
    if season == "rain":
        c.img.paste((60, 64, 90), (0, 0, W * SS, H * SS), Image.new("L", (W * SS, H * SS), 40))
    return c.img


@lru_cache(None)
def fg_mask(season="autumn"):
    """L mask of everything in front of the sky (hills, barn, tree, clouds) for one farm background:
    the pixels that stay the same when the sky behind them changes colour."""
    a = np.asarray(farm_bg(season)).astype(np.int16)
    b = np.asarray(_farm(season, True)).astype(np.int16)
    m = (np.abs(a - b).max(axis=2) < 4).astype(np.uint8) * 255
    return Image.fromarray(m, "L")


def farm_mix(a, b, k):
    """Crossfade between two cached farm backgrounds."""
    if k <= 0.001:
        return farm_bg(a).copy()
    if k >= 0.999:
        return farm_bg(b).copy()
    return Image.blend(farm_bg(a), farm_bg(b), k)


# ============================================================= sky effects

RAINBOW = [(236, 80, 80), (250, 160, 60), (250, 226, 80), (100, 196, 100), (80, 150, 236), (100, 90, 200),
           (156, 100, 210)]


def rainbow(c, cx, cy, r, k=1.0, w=14, alpha_col=None):
    """A rainbow arc grown from the left (k 0..1)."""
    if k <= 0.01:
        return
    for i, col in enumerate(RAINBOW):
        rr = r - i * w
        c.arc(cx, cy, rr, rr, 180, 180 + 180 * k, col, w + 1)


def storm_cloud(c, x, y, s=1.0, flash=0.0):
    col = mix((110, 112, 130), (250, 250, 230), flash * 0.6)
    D.cloud(c, x, y, s, col)
    if flash > 0.05:
        pts = [(x - 6, y + 16 * s), (x + 14, y + 44 * s), (x - 4, y + 48 * s), (x + 18, y + 90 * s)]
        c.line(pts, mix((255, 250, 180), (255, 255, 255), 0.5), 5 * flash + 1)
        c.glow(x, y + 40 * s, 120 * s, 80 * s, (255, 252, 220), (190, 192, 204), steps=4)


# ================================================================ space

def sun(c, x, y, r, t=0.0, face=True, glow=1.0):
    """The Sun for the space diagram, with a big soft glow and a happy face."""
    if glow > 0.01:
        c.glow(x, y, r * 2.3, r * 2.3, (255, 210, 110), (46, 40, 96), steps=12)
    for k in range(16):
        a = k * TAU / 16 + t * 0.2
        r0, r1 = r * 1.08, r * (1.32 + 0.08 * math.sin(t * 3 + k))
        c.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)],
               (255, 200, 80), 6)
    c.circle(x, y, r, (255, 222, 96), ol=(236, 150, 50), w=4)
    c.circle(x - r * 0.25, y - r * 0.25, r * 0.5, (255, 236, 150), ol=None)
    if face:
        c.arc(x - r * 0.32, y - r * 0.08, r * 0.14, r * 0.12, 200, 340, OUT, 3)
        c.arc(x + r * 0.32, y - r * 0.08, r * 0.14, r * 0.12, 200, 340, OUT, 3)
        c.arc(x, y + r * 0.2, r * 0.3, r * 0.22, 20, 160, OUT, 3)
        c.circle(x - r * 0.55, y + r * 0.2, r * 0.12, (255, 170, 120), ol=None)
        c.circle(x + r * 0.55, y + r * 0.2, r * 0.12, (255, 170, 120), ol=None)


_night = {}


def night_mask(r_ss, ang_deg):
    """L mask (2r x 2r supersampled px): the half of a disc facing away from the Sun.
    ang_deg: screen direction toward the Sun (0 = right, 90 = down)."""
    key = (int(r_ss), int(round(ang_deg / 3)) * 3)
    if key in _night:
        return _night[key]
    R = key[0]
    yy, xx = np.mgrid[0:2 * R, 0:2 * R] + 0.5
    dx, dy = (xx - R) / R, (yy - R) / R
    inside = dx * dx + dy * dy <= 1.0
    a = math.radians(key[1])
    d = dx * math.cos(a) + dy * math.sin(a)
    m = np.clip(0.5 - d * 3.0, 0, 1) * inside * 150
    img = Image.fromarray(m.astype(np.uint8), "L")
    if len(_night) > 200:
        _night.clear()
    _night[key] = img
    return img


def tilted_earth(c, x, y, r, lon=0.0, sun_xy=None, axis=1.0, lat=10.0, roll=-TILT, style="earth", glow_north=0.0,
                 t=0.0, axis_col=(255, 255, 255)):
    """A small Earth leaning by the axial tilt, with its axis stick; the side away from sun_xy is
    in shadow. glow_north lights up the top (northern) half."""
    np_ = K.globe_xy(x, y, r, 0, 90, lon, lat, roll)
    sp_ = K.globe_xy(x, y, r, 0, -90, lon, lat, roll)
    ax, ay = np_[0] - x, np_[1] - y
    L = math.hypot(ax, ay) or 1
    ux, uy = ax / L, ay / L
    if axis > 0.01:
        # back part of the axis (below the south pole)
        c.line([(x - ux * r * 1.45, y - uy * r * 1.45), (x - ux * r * 0.9, y - uy * r * 0.9)], axis_col, 4)
    K.globe(c, x, y, r, lon=lon, lat=lat, roll=roll, style=style)
    if sun_xy is not None:
        ang = math.degrees(math.atan2(sun_xy[1] - y, sun_xy[0] - x))
        rs = int(r * c.scale * SS)
        m = night_mask(rs, ang)
        px, py = c.P(x, y)
        c.img.paste((10, 14, 50), (int(px - rs), int(py - rs), int(px - rs) + 2 * rs, int(py - rs) + 2 * rs), m)
    if glow_north > 0.01:
        # equator line, and a warm glow on the northern half
        pts = []
        for lo in range(-180, 181, 6):
            gx, gy, vis = K.globe_xy(x, y, r, lo, 0, lon, lat, roll)
            if vis:
                pts.append((gx, gy))
        if len(pts) > 1:
            c.line(pts, mix((255, 255, 255), (255, 220, 80), glow_north), 3)
    if axis > 0.01:
        k = clamp(axis)
        c.line([(x + ux * r * 0.9, y + uy * r * 0.9), (x + ux * r * lerp(0.9, 1.5, k), y + uy * r * lerp(0.9, 1.5, k))],
               axis_col, 4)
        c.circle(x + ux * r * lerp(0.9, 1.5, k), y + uy * r * lerp(0.9, 1.5, k), 4, (255, 90, 80), w=1.5)
    c.circle(x, y, r, None, ol=OUT, w=3)
    return (ux, uy)


def dashed_ellipse(c, cx, cy, rx, ry, col=(200, 200, 255), w=3, dash=10, k=1.0, a0=0.0):
    n = 120
    for i in range(0, int(n * k), 2):
        a = a0 + TAU * i / n
        b = a0 + TAU * (i + 1) / n
        c.line([(cx + rx * math.cos(a), cy - ry * math.sin(a)), (cx + rx * math.cos(b), cy - ry * math.sin(b))],
               col, w, cap=False)


# ================================================================= insets

def day_bar(c, x, y, w, frac, label=None, size=22):
    """A day/night bar: yellow part = daytime, dark blue = night."""
    c.rect(x, y, x + w, y + 30, (40, 44, 96), r=14, w=3)
    c.rect(x, y, x + w * frac, y + 30, (255, 214, 80), r=14, w=3)
    K.text(c, x + w * frac / 2, y + 15, "Day", size, (110, 70, 20))
    if frac < 0.85:
        K.text(c, x + w * (1 + frac) / 2, y + 15, "Night", size, (220, 226, 255))


def sky_inset(ic, t, summer=True, k=1.0):
    """Summer: the sun climbs high, long days. Winter: the sun stays low, short days."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    sky = [(0, (100, 176, 246)), (1, (210, 238, 255))] if summer else [(0, (150, 170, 206)), (1, (230, 234, 246))]
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), sky), (0, 0))
    ground = (120, 190, 90) if summer else (244, 248, 255)
    ic.poly([(0, h - 90), (w * 0.4, h - 104), (w, h - 92), (w, h), (0, h)], ground, w=2)
    # the sun's path across the sky
    top = 50 if summer else 150
    pts = [(lerp(30, w - 30, u), h - 92 - (h - 92 - top) * math.sin(math.pi * u)) for u in np.linspace(0, 1, 30)]
    ic.line(pts, (255, 255, 255), 2)
    u = 0.15 + 0.35 * ease(k)
    sx, sy = lerp(30, w - 30, u), h - 92 - (h - 92 - top) * math.sin(math.pi * u)
    ic.circle(sx, sy, 26, (255, 222, 96), ol=(236, 160, 50), w=3)
    if summer:
        for j in range(3):
            ic.line([(sx + 16 * j - 16, sy + 34), (sx + 16 * j - 26, sy + 100)], (255, 236, 120), 5)
    K.text(ic, w / 2, 26, "Sun high: strong and warm" if summer else "Sun low: weak and cold", 24,
           (48, 40, 60))
    day_bar(ic, 30, h - 56, w - 60, 0.66 if summer else 0.33)


# ================================================================== icons

def icon_seasons(c, x, y, r, t=0.0):
    """A ball in four parts: flower, sun, leaf, snowflake."""
    cols = [(255, 196, 214), (255, 226, 110), (240, 150, 60), (200, 226, 255)]
    K.pie(c, x, y, r * 0.95, cols, 1.0)
    q = r * 0.45
    for (dx, dy), kind in zip(((q, -q), (q, q), (-q, q), (-q, -q)), ("flower", "sun", "leaf", "snow")):
        px, py = x + dx, y + dy
        if kind == "flower":
            for k in range(5):
                a = k * TAU / 5
                c.circle(px + math.cos(a) * r * 0.1, py + math.sin(a) * r * 0.1, r * 0.08, (240, 110, 150), w=1)
            c.circle(px, py, r * 0.06, (255, 230, 90), ol=None)
        elif kind == "sun":
            c.circle(px, py, r * 0.13, (250, 180, 40), w=1.5)
        elif kind == "leaf":
            leaf(c, px, py, r * 0.17, -30, (210, 90, 40))
        else:
            for k in range(3):
                a = k * math.pi / 3
                c.line([(px - math.cos(a) * r * 0.15, py - math.sin(a) * r * 0.15),
                        (px + math.cos(a) * r * 0.15, py + math.sin(a) * r * 0.15)], (70, 120, 200), 2.5)


def icon_tilt(c, x, y, r, t=0.0):
    tilted_earth(c, x, y, r * 0.72, lon=-t * 30, axis=1.0, lat=10)


def icon_rainbow(c, x, y, r, t=0.0):
    for i, col in enumerate(RAINBOW[:6]):
        rr = r * 0.85 - i * r * 0.1
        c.arc(x, y + r * 0.3, rr, rr, 180, 360, col, r * 0.1 + 1)
    c.circle(x - r * 0.6, y - r * 0.55, r * 0.22, (255, 222, 96), ol=(236, 160, 50), w=2)
    c.push(x + r * 0.5, y + r * 0.2, r / 120)
    for dx, dy, rr in ((-30, 0, 20), (0, -12, 26), (30, 0, 20), (0, 6, 20)):
        c.circle(dx, dy, rr, (240, 244, 252), ol=None)
    for k in range(3):
        c.line([(-20 + 20 * k, 28), (-24 + 20 * k, 44)], (90, 150, 230), 5)
    c.pop()


def icon_closer(c, x, y, r, t=0.0):
    """Quiz: 'the Earth gets closer to the Sun'."""
    c.circle(x - r * 0.45, y, r * 0.42, (255, 222, 96), ol=(236, 160, 50), w=2)
    K.globe(c, x + r * 0.55, y, r * 0.25, lon=-t * 30, lat=10)
    K.arrow(c, x + r * 0.95, y - r * 0.45, x + r * 0.15, y - r * 0.45, (255, 120, 90), 5, 1.0, head=12)


def icon_snow_wind(c, x, y, r, t=0.0):
    for k in range(3):
        a = k * math.pi / 3
        c.line([(x - r * 0.4 - math.cos(a) * r * 0.32, y - r * 0.1 - math.sin(a) * r * 0.32),
                (x - r * 0.4 + math.cos(a) * r * 0.32, y - r * 0.1 + math.sin(a) * r * 0.32)], (90, 150, 230), 5)
    for k in range(3):
        yy = y - r * 0.3 + k * r * 0.3
        c.line([(x + r * 0.05, yy), (x + r * 0.75, yy)], (150, 170, 210), 5)
        c.arc(x + r * 0.75, yy - r * 0.1, r * 0.1, r * 0.1, -90, 120, (150, 170, 210), 5)


def icon_sun_rain(c, x, y, r, t=0.0):
    c.circle(x - r * 0.35, y - r * 0.2, r * 0.38, (255, 222, 96), ol=(236, 160, 50), w=2)
    c.push(x + r * 0.35, y + r * 0.0, r / 110)
    for dx, dy, rr in ((-30, 0, 22), (0, -14, 28), (30, 0, 22), (0, 6, 22)):
        c.circle(dx, dy, rr + 2, OUT, ol=None)
    for dx, dy, rr in ((-30, 0, 22), (0, -14, 28), (30, 0, 22), (0, 6, 22)):
        c.circle(dx, dy, rr, (240, 244, 252), ol=None)
    for k in range(3):
        c.line([(-22 + 22 * k, 34), (-28 + 22 * k, 56)], (90, 150, 230), 6)
    c.pop()
