"""Props for Episode 5 "Rivers and Lakes": the river-journey landscape (one big cached panorama from
the snowy Alps down to the sea), Ollie the otter, Drip the raindrop, lake animals, diagrams and icons."""
import math
from functools import lru_cache

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease
from world import kit as K

# ============================================================================ colours

WATER = (78, 158, 230)
WATER_D = (52, 124, 200)
WATER_L = (150, 210, 250)
FOAM = (232, 246, 255)
SAND = (236, 214, 156)
BANK = (170, 140, 96)
ROCK = (150, 140, 162)
ROCK_D = (118, 108, 134)
SNOW = (250, 252, 255)
SNOW_D = (206, 222, 242)
GRASS = (122, 192, 96)
GRASS_D = (96, 166, 80)
GRASS_L = (150, 210, 110)

# ======================================================================= panorama

PW, PH = 4800, 1240           # the whole journey landscape (output px)

MOUNTAIN = [(-60, 900), (-60, 560), (60, 470), (170, 400), (300, 330), (420, 245), (500, 190), (560, 150),
            (620, 175), (700, 230), (800, 300), (900, 390), (1000, 450), (1120, 500), (1260, 540),
            (1400, 600), (1500, 700), (1500, 900)]
BACK_MOUNTAIN = [(-60, 700), (-60, 330), (40, 260), (130, 215), (200, 240), (300, 300), (360, 380), (360, 700)]
SNOW_TOP = [(330, 318), (420, 245), (500, 190), (560, 150), (620, 175), (700, 230), (800, 300), (830, 330)]
SNOW_BOTTOM_Y = 330          # wavy edge of the snow cap, around this height

J = (930, 470)               # where the tiny streams join into the river
STREAMS = [
    [(470, 300), (560, 360), (680, 400), (800, 440), J],
    [(600, 330), (680, 360), (780, 400), (870, 445), J],
    [(745, 312), (800, 360), (860, 410), J],
    [(400, 330), (470, 380), (600, 430), (760, 455), J],
]
RIVER1 = [J, (1000, 512), (1090, 545), (1200, 575), (1320, 620), (1430, 670), (1560, 705), (1720, 735),
          (1860, 770), (1990, 805), (2060, 825)]
RIVER1_W = (14, 100)
LAKE = (2360, 845, 430, 100)      # centre x, y, rx, ry
RIVER2 = [(2700, 862), (2760, 870), (2900, 892), (3060, 905), (3230, 918), (3400, 935), (3560, 948), (3720, 962), (3840, 975), (3960, 990)]
RIVER2_W = (96, 150)
HORIZON = 760
COAST = [(3330, HORIZON), (3450, 810), (3600, 860), (3700, 885), (3725, 950), (3750, 1050), (3810, 1150),
         (3840, PH + 20)]


def resample(pts, n=14):
    s = K.spline(pts, n)
    d = [0.0]
    for a, b in zip(s, s[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return s, d


@lru_cache(None)
def _path(key):
    pts = {"r1": RIVER1, "r2": RIVER2, "s0": STREAMS[0], "s1": STREAMS[1], "s2": STREAMS[2],
           "s3": STREAMS[3]}[key]
    return resample(pts)


def path_at(key, u):
    """(x, y, angle) at fraction u along a river/stream centre line."""
    s, d = _path(key)
    L = d[-1] * clamp(u)
    for i in range(1, len(s)):
        if d[i] >= L:
            f = (L - d[i - 1]) / max(1e-6, d[i] - d[i - 1])
            a, b = s[i - 1], s[i]
            return lerp(a[0], b[0], f), lerp(a[1], b[1], f), math.atan2(b[1] - a[1], b[0] - a[0])
    a, b = s[-2], s[-1]
    return b[0], b[1], math.atan2(b[1] - a[1], b[0] - a[0])


def _edges(key, w0, w1, extra=0.0, u0=0.0, u1=1.0):
    s, d = _path(key)
    L = d[-1]
    left, right = [], []
    for i, (x, y) in enumerate(s):
        if d[i] < L * u0 - 1e-6 or d[i] > L * u1 + 1e-6:
            continue
        j0, j1 = max(0, i - 1), min(len(s) - 1, i + 1)
        dx, dy = s[j1][0] - s[j0][0], s[j1][1] - s[j0][1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        w = lerp(w0, w1, d[i] / L) / 2 + extra
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def ribbon(c, key, w0, w1, col, ol=OUT, extra=0.0, u=1.0, lw=3, u0=0.0):
    """Filled river band along a path; width grows from w0 to w1."""
    left, right = _edges(key, w0, w1, extra, u0, u)
    if len(left) > 1:
        c.poly(left + right[::-1], col, ol=ol, w=lw)


def ribbon_lines(c, key, w0, w1, u0, u1, col=OUT, lw=3):
    left, right = _edges(key, w0, w1, 0.0, u0, u1)
    for side in (left, right):
        if len(side) > 1:
            c.line(side, col, lw)


def lake_poly(cx, cy, rx, ry, wob=0.0, n=60, seed=0):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6, 3)
    pts = []
    for a in np.linspace(0, math.tau, n, endpoint=False):
        f = 1 + wob * (0.5 * math.sin(3 * a + ph[0]) + 0.3 * math.sin(5 * a + ph[1]) + 0.2 * math.sin(2 * a + ph[2]))
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    return pts


def pine(c, x, y, s=1.0, col=(60, 130, 90)):
    c.push(x, y, s)
    c.rect(-5, -14, 5, 0, (120, 84, 56), w=2)
    for k, (w, h) in enumerate(((34, 44), (28, 40), (20, 34))):
        yy = -14 - k * 22
        c.poly([(-w, yy), (0, yy - h), (w, yy)], col, w=2.5)
    c.pop()


def rock(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-26, 0), (-20, -18), (-4, -26), (16, -20), (26, 0)], (170, 162, 176), w=2.5)
    c.line([(-6, -18), (4, -6)], (140, 132, 150), 2)
    c.pop()


@lru_cache(None)
def panorama():
    """The whole journey as one big picture: snowy mountains (left), hills, the river, a lake, the sea."""
    c = Canvas(D.gradient(PW * SS, PH * SS, [(0, (110, 180, 246)), (0.55, (200, 232, 255)),
                                             (1, (220, 240, 255))]), size=(PW, PH))
    rng = np.random.default_rng(5)
    # far mountains / hills in the haze
    far = [(-60, 720), (200, 520), (420, 600), (700, 470), (980, 560), (1300, 480), (1600, 600), (1900, 540),
           (2200, 640), (2500, 600), (2800, 680), (3100, 650), (3400, HORIZON), (3400, PH), (-60, PH)]
    c.poly(far, (176, 190, 226), ol=None)
    for px, py in ((700, 470), (1300, 480), (1900, 540)):
        c.poly([(px - 60, py + 44), (px, py), (px + 60, py + 44), (px + 30, py + 34), (px, py + 46),
                (px - 26, py + 32)], (236, 242, 252), ol=None)
    far2 = [(1200, 700), (1500, 640), (1800, 690), (2100, 650), (2400, 700), (2700, 690), (3000, 720),
            (3300, HORIZON), (3300, PH), (1200, PH)]
    c.poly(far2, (150, 196, 170), ol=None)
    # the back mountain + the big snowy mountain
    c.poly(BACK_MOUNTAIN, (168, 160, 186), w=3)
    c.poly([(40, 260), (130, 215), (200, 240), (230, 268), (180, 262), (140, 282), (100, 262), (70, 284)], SNOW,
           w=2.5)
    c.poly(MOUNTAIN, ROCK, w=3)
    # shadow side
    c.poly([(560, 150), (620, 175), (700, 230), (800, 300), (900, 390), (1000, 450), (1120, 500), (980, 560),
            (820, 520), (700, 420), (620, 300)], ROCK_D, ol=None)
    for x0, y0, x1, y1 in ((380, 420, 460, 470), (250, 480, 330, 520), (640, 480, 720, 520),
                           (520, 520, 600, 560)):
        c.line([(x0, y0), (x1, y1)], ROCK_D, 3)
    # snow cap with a wavy bottom edge
    bottom = []
    for i, x in enumerate(np.linspace(830, 330, 15)):
        bottom.append((x, SNOW_BOTTOM_Y - 18 + (16 if i % 2 else -8) + (x - 580) * 0.02))
    c.poly(SNOW_TOP + bottom, SNOW, w=3)
    c.poly([(560, 150), (620, 175), (700, 230), (800, 300), (830, 330), (760, 322), (690, 300), (620, 250)],
           SNOW_D, ol=None)
    # hills, front of the mountain: green land all the way to the coast
    hills = [(-60, 780), (120, 700), (300, 640), (480, 600), (640, 560), (780, 520), (880, 500), (960, 492),
             (1100, 540), (1260, 575), (1400, 640), (1550, 690), (1750, 720), (1950, 745), (2200, 735),
             (2500, 742), (2800, 760), (3050, 770), (3330, HORIZON)] + COAST[1:] + [(-60, PH + 20)]
    c.poly(hills, GRASS, w=3)
    for pts in ([(-60, 900), (200, 820), (500, 760), (800, 700), (1100, 690), (1500, 760), (1500, PH), (-60, PH)],
                [(1300, 900), (1700, 860), (2100, 980), (2500, 1000), (2900, 960), (3300, 1000), (3700, 1060),
                 (3800, PH), (1300, PH)]):
        c.poly(pts, GRASS_D, ol=None)
    # beach + sea
    sea = [(3330, HORIZON), (PW + 20, HORIZON), (PW + 20, PH + 20)] + list(reversed(COAST[1:]))
    beach = [(x - 70 - (y - HORIZON) * 0.15, y) for x, y in COAST] + list(reversed(COAST))
    c.poly(beach, SAND, ol=None)
    c.poly(sea, WATER, ol=None)
    c.poly([(3330, HORIZON), (PW + 20, HORIZON), (PW + 20, 820), (3430, 820)], (110, 180, 238), ol=None)
    c.line(COAST, OUT, 3)
    c.line([(3330, HORIZON), (PW + 20, HORIZON)], (240, 250, 255), 3, cap=False)
    # river banks, then the lake, then the river water on top (the mouths stay open)
    U1_IN, U2_OUT, U2_SEA = 0.955, 0.05, 0.815
    ribbon(c, "r1", *RIVER1_W, BANK, extra=8, ol=None)
    ribbon(c, "r2", *RIVER2_W, BANK, extra=9, ol=None, u=U2_SEA)
    cx, cy, rx, ry = LAKE
    c.poly(lake_poly(cx, cy, rx + 18, ry + 14, 0.06, seed=2), BANK, w=3)
    c.poly(lake_poly(cx, cy, rx, ry, 0.06, seed=2), WATER, w=3)
    c.poly(lake_poly(cx + 10, cy - 18, rx * 0.78, ry * 0.55, 0.05, seed=3), (100, 176, 238), ol=None)
    ribbon(c, "r1", *RIVER1_W, WATER, ol=None)
    ribbon(c, "r2", *RIVER2_W, WATER, ol=None)
    ribbon(c, "r1", RIVER1_W[0] * 0.35, RIVER1_W[1] * 0.4, (104, 180, 240), ol=None, u=U1_IN - 0.03)
    ribbon(c, "r2", RIVER2_W[0] * 0.4, RIVER2_W[1] * 0.4, (104, 180, 240), ol=None, u0=U2_OUT + 0.03,
           u=U2_SEA - 0.02)
    ribbon_lines(c, "r1", *RIVER1_W, 0.0, U1_IN - 0.02)
    ribbon_lines(c, "r2", *RIVER2_W, U2_OUT + 0.02, U2_SEA)
    # outer bank lines
    for key, wv, a_, b_ in (("r1", RIVER1_W, 0.0, U1_IN - 0.045), ("r2", RIVER2_W, U2_OUT + 0.045, U2_SEA)):
        left, right = _edges(key, *wv, 8 if key == "r1" else 9, a_, b_)
        for side in (left, right):
            c.line(side, OUT, 3)
    # reed and stones round the lake
    for k in range(9):
        a = rng.uniform(0, math.tau)
        x, y = cx + math.cos(a) * (rx + 24), cy + math.sin(a) * (ry + 18)
        if y > cy - 20 and abs(x - 2760) > 80 and abs(x - 1990) > 80:
            for j in range(3):
                c.line([(x + j * 6, y), (x + j * 6 + rng.uniform(-4, 4), y - rng.uniform(26, 40))], (90, 150, 70), 3)
                c.ellipse(x + j * 6, y - 34, 3, 8, (150, 100, 60), ol=None)
    # trees, pines, rocks, flowers
    for x, y, s in ((1150, 470, 0.5), (1210, 485, 0.45), (1280, 505, 0.55), (300, 610, 0.6), (380, 590, 0.5),
                    (160, 670, 0.7), (720, 520, 0.4)):
        pine(c, x, y, s * 1.6)
    for x, y, s in ((1620, 660, 0.45), (2050, 715, 0.5), (2600, 720, 0.45), (2900, 740, 0.5), (3150, 750, 0.4),
                    (1500, 860, 0.7), (2150, 1050, 0.8), (2950, 1060, 0.75), (1750, 1010, 0.6)):
        D.tree(c, x, y, s)
    for x, y in ((1000, 640), (1360, 760), (2700, 1000), (3300, 1010), (600, 680)):
        rock(c, x, y, 1.0)
    for k in range(40):
        x = rng.uniform(900, 3500)
        y = rng.uniform(780, PH - 20)
        if abs(y - (cy)) < ry + 40 and abs(x - cx) < rx + 40:
            continue
        D.flower(c, x, y, [(255, 120, 140), (255, 220, 90), (190, 140, 240), (255, 255, 255)][k % 4], 0.8)
    return c.img


class Cam:
    """Camera on the panorama: (cx, cy) world point at the screen centre."""

    def __init__(self, cx, cy):
        self.x0 = clamp(cx - W / 2, 0, PW - W)
        self.y0 = clamp(cy - H / 2, 0, PH - H)

    def xy(self, x, y):
        return x - self.x0, y - self.y0


def view(cx, cy):
    cam = Cam(cx, cy)
    x0, y0 = int(round(cam.x0 * SS)), int(round(cam.y0 * SS))
    cam.x0, cam.y0 = x0 / SS, y0 / SS
    c = Canvas(panorama().crop((x0, y0, x0 + W * SS, y0 + H * SS)))
    return c, cam


def flow(c, cam, key, w0, w1, t, speed=90, spacing=80, lanes=(-0.22, 0.0, 0.22), col=FOAM, k=1.0, lw=3,
         dash=22):
    """Animated foam dashes flowing downstream (draw inside c.push(-cam.x0, -cam.y0))."""
    if k <= 0.01:
        return
    s, d = _path(key)
    L = d[-1]
    off = (t * speed) % spacing
    for li, lane in enumerate(lanes):
        pos = off + li * spacing / len(lanes)
        while pos < L:
            u = pos / L
            x, y, a = path_at(key, u)
            if cam.x0 - 60 < x < cam.x0 + W + 60 and cam.y0 - 60 < y < cam.y0 + H + 60:
                w = lerp(w0, w1, u)
                nx, ny = -math.sin(a), math.cos(a)
                px, py = x + nx * w * lane, y + ny * w * lane
                dl = dash * k * lerp(0.6, 1.2, u)
                c.line([(px - math.cos(a) * dl / 2, py - math.sin(a) * dl / 2),
                        (px + math.cos(a) * dl / 2, py + math.sin(a) * dl / 2)], col, lw)
            pos += spacing


def ripples(c, x, y, t, n=3, rx=60, ry=10, col=FOAM, speed=0.6, seed=0):
    for k in range(n):
        u = (t * speed + k / n + seed * 0.37) % 1
        c.ellipse(x, y, rx * (0.4 + u), ry * (0.4 + u), None, ol=mix(col, WATER, u), w=2.5)


def water_front(c, x, y, w, t, col=WATER, depth=26):
    """Water over the lower part of something floating at (x, y): a little band + foam."""
    c.rect(x - w / 2, y - 2, x + w / 2, y + depth, col, ol=None, r=depth / 2)
    for k in range(5):
        dx = (k - 2) / 2 * (w / 2 - 20) + 6 * math.sin(t * 3 + k)
        c.ellipse(x + dx, y, 22 + 5 * math.sin(t * 4 + k * 2), 6, FOAM, ol=None)


# =========================================================================== Drip

DROP = (130, 200, 252)
DROP_D = (50, 110, 190)


def _drop_outline(x, y, r, n=28):
    pts = [(x, y - r * 2.1)]
    for a in np.linspace(-0.25 * math.pi, 1.25 * math.pi, n):
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    return pts


def drip(c, x, y, s=1.0, t=0.0, mouth=0.0, eyes="open", vapour=0.0, look=(0.0, 0.0), squash=0.0, wave=0.0):
    """Drip the raindrop. (x, y) = bottom of the drop. vapour 0..1 turns him into a see-through wisp."""
    if eyes == "open" and D.blink(t, 7.0):
        eyes = "closed"
    r = 24
    c.push(x, y - r * s, s)
    pts = _drop_outline(0, 0, r)
    if vapour < 0.5:
        body = mix(DROP, (255, 255, 255), vapour * 0.8)
        c.poly(pts, body, ol=DROP_D, w=3)
        c.ellipse(-9, -10, 5, 9, (235, 248, 255), ol=None)
        c.circle(-10, -26, 3, (235, 248, 255), ol=None)
    else:
        # wispy, dotted: invisible vapour
        for i in range(0, len(pts), 2):
            c.circle(pts[i][0], pts[i][1], 2.4, (255, 255, 255), ol=None)
    if vapour < 0.85:
        ey = -2
        for ex in (-8, 8):
            if eyes == "closed":
                c.arc(ex, ey, 5, 4, 20, 160, OUT, 2.5)
            elif eyes == "happy":
                c.arc(ex, ey + 3, 5, 5, 200, 340, OUT, 2.5)
            else:
                c.ellipse(ex + look[0] * 1.5, ey + look[1] * 1.5, 3.6, 5.2, OUT, ol=None)
                c.circle(ex + look[0] * 1.5 + 1.2, ey - 2 + look[1] * 1.5, 1.3, (255, 255, 255), ol=None)
        c.circle(-15, 7, 3.5, (255, 170, 190), ol=None)
        c.circle(15, 7, 3.5, (255, 170, 190), ol=None)
        if mouth > 0.08:
            c.ellipse(0, 10, 4 + 2 * mouth, 2 + 5 * mouth, D.MOUTH, w=1.5)
        else:
            c.arc(0, 7, 6, 5, 20, 160, OUT, 2.2)
        if wave > 0:
            a = math.sin(t * 10) * 0.6
            c.line([(18, 2), (30 + 4 * math.cos(a), -10 + 6 * math.sin(a))], DROP_D, 3)
    c.pop()


# ========================================================================== Ollie

FUR = (138, 94, 60)
FUR_D = (104, 68, 44)
CREAM = (238, 210, 166)


def otter(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", pose="swim", look=(0.0, 0.0), paddle=1.0,
          wave=0.0):
    """Ollie the river otter. (x, y) = waterline under his middle.
    pose "swim": side view, head up; "back": floating on his back, face turned to us."""
    if eyes == "open" and D.blink(t, 3.3):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    sw = math.sin(t * 6) * paddle
    if pose == "swim":
        # tail
        c.poly([(-58, -14), (-150, -2 + 6 * sw), (-150, 4 + 6 * sw), (-58, 8)], FUR_D)
        # body
        c.ellipse(0, -10, 78, 26, FUR)
        c.ellipse(10, 4, 60, 10, CREAM, ol=None)
        # front paw
        c.ellipse(52 + 8 * sw, 8, 12, 7, FUR_D, w=2)
        # head
        hx, hy = 80, -34
        c.circle(hx - 18, hy - 22, 8, FUR_D, w=2.5)
        c.ellipse(hx, hy, 32, 28, FUR)
        c.ellipse(hx + 18, hy + 10, 18, 12, CREAM, w=2)
        c.ellipse(hx + 32, hy + 2, 7, 5, (50, 34, 30), ol=None)
        for k in (-1, 1):
            c.line([(hx + 24, hy + 10), (hx + 54, hy + 6 + k * 8)], OUT, 1.5)
        if mouth > 0.08:
            c.ellipse(hx + 22, hy + 18, 7 + 2 * mouth, 2 + 6 * mouth, D.MOUTH, w=2)
        else:
            c.arc(hx + 22, hy + 13, 9, 6, 30, 150, OUT, 2.2)
        ex, ey = hx + 8, hy - 8
        if eyes == "closed":
            c.arc(ex, ey, 6, 5, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
        else:
            c.ellipse(ex + look[0] * 2, ey + look[1] * 2, 5, 6.5, OUT, ol=None)
            c.circle(ex + look[0] * 2 + 1.6, ey - 2.2, 1.7, (255, 255, 255), ol=None)
    else:
        # floating on his back: feet and tail up on the left, face on the right
        c.poly([(-60, -12), (-136, -24 - 4 * sw), (-134, -16 - 4 * sw), (-60, 2)], FUR_D)
        for fx in (-52, -36):
            c.ellipse(fx, -34 + 3 * math.sin(t * 5 + fx), 9, 13, FUR_D, w=2)
        c.ellipse(0, -10, 72, 24, FUR)
        c.ellipse(4, -22, 56, 12, CREAM, ol=None)
        # paws on the tummy (one waves)
        c.ellipse(18, -32, 10, 8, FUR_D, w=2)
        if wave > 0:
            a = math.sin(t * 9) * 0.5
            c.stroke([(36, -30), (46 + 10 * math.sin(a), -58 - 6 * math.cos(a))], FUR, 9)
        else:
            c.ellipse(38, -32, 10, 8, FUR_D, w=2)
        # face, turned toward us
        hx, hy = 78, -30
        for ex_ in (-20, 20):
            c.circle(hx + ex_, hy - 22, 8, FUR_D, w=2.5)
        c.circle(hx, hy, 30, FUR)
        c.ellipse(hx, hy + 12, 20, 13, CREAM, w=2)
        c.ellipse(hx, hy + 4, 7, 5, (50, 34, 30), ol=None)
        for k in (-1, 1):
            for j in (-1, 1):
                c.line([(hx + k * 12, hy + 10), (hx + k * 36, hy + 6 + j * 6)], OUT, 1.5)
        if mouth > 0.08:
            c.ellipse(hx, hy + 16, 6 + 2 * mouth, 2 + 6 * mouth, D.MOUTH, w=2)
        else:
            c.arc(hx - 5, hy + 12, 6, 5, 20, 160, OUT, 2)
            c.arc(hx + 5, hy + 12, 6, 5, 20, 160, OUT, 2)
        for ex_ in (-11, 11):
            ex, ey = hx + ex_, hy - 8
            if eyes == "closed":
                c.arc(ex, ey, 6, 5, 20, 160, OUT, 2.5)
            elif eyes == "happy":
                c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
            else:
                c.ellipse(ex + look[0] * 2, ey + look[1] * 2, 5, 6.5, OUT, ol=None)
                c.circle(ex + look[0] * 2 + 1.6, ey - 2.2, 1.7, (255, 255, 255), ol=None)
    c.pop()


# =================================================================== lake animals

def duck(c, x, y, s=1.0, face=1, t=0.0, baby=False):
    c.push(x, y + math.sin(t * 2 + x) * 2, s, flip=face < 0)
    body = (250, 236, 150) if baby else (236, 226, 210)
    c.ellipse(0, -10, 26, 14, body, w=2.5)
    c.poly([(-22, -16), (-34, -24), (-26, -8)], body, w=2)
    hc = body if baby else (60, 140, 90)
    c.circle(20, -30, 11, hc, w=2.5)
    c.poly([(29, -32), (42, -28), (29, -25)], (250, 170, 60), w=2)
    c.circle(23, -33, 2, OUT, ol=None)
    c.ellipse(-2, -12, 12, 6, mix(body, (0, 0, 0), 0.1), ol=None)
    c.pop()


def heron(c, x, y, s=1.0, face=1, t=0.0, dip=0.0):
    """Grey heron standing in the shallows; dip 0..1 bends the neck down to the water."""
    c.push(x, y, s, flip=face < 0)
    leg = (220, 170, 90)
    c.line([(-6, 0), (-4, -70)], leg, 3)
    c.line([(6, 0), (4, -70)], leg, 3)
    c.ellipse(0, -86, 34, 20, (180, 186, 200), w=2.5)
    c.poly([(-30, -90), (-56, -80), (-30, -78)], (120, 126, 146), w=2)
    hx = lerp(30, 70, dip)
    hy = lerp(-150, -40, dip)
    c.stroke([(22, -96), (36, -116 + 20 * dip), (24, -130 + 50 * dip), (hx, hy)], (226, 230, 238), 7)
    c.circle(hx, hy, 9, (236, 240, 246), w=2.5)
    c.line([(hx - 6, hy - 6), (hx - 20, hy - 12)], OUT, 2)
    c.poly([(hx + 6, hy - 3), (hx + 32, hy + 2 + 6 * dip), (hx + 6, hy + 4)], (240, 196, 80), w=2)
    c.circle(hx + 2, hy - 2, 1.8, OUT, ol=None)
    c.pop()


def deer(c, x, y, s=1.0, face=1, t=0.0, drink=0.0):
    """A deer bending down to drink (drink 0..1)."""
    c.push(x, y, s, flip=face < 0)
    fur, dark, belly = (196, 130, 80), (150, 96, 60), (246, 226, 196)
    for lx in (-34, -22, 26, 38):
        c.stroke([(lx, -50), (lx + 2, -2)], dark if lx in (-22, 38) else fur, 6)
    c.ellipse(0, -62, 52, 24, fur)
    c.ellipse(4, -50, 36, 10, belly, ol=None)
    for k in range(4):
        c.circle(-20 + 12 * k, -70 + 3 * (k % 2), 3, (255, 240, 220), ol=None)
    c.poly([(-50, -70), (-62, -78), (-56, -60)], belly, w=2)
    hx, hy = 70 + 6 * drink, lerp(-120, -20, drink)
    c.stroke([(36, -74), (hx - 8, hy)], fur, 18)
    c.ellipse(hx + 6, hy + 4, 18, 12, fur)
    c.ellipse(hx + 20, hy + 8, 6, 5, OUT, ol=None)
    c.ellipse(hx - 8, hy - 12, 6, 12, fur, w=2)
    c.circle(hx + 4, hy - 2, 2.5, OUT, ol=None)
    c.pop()


def sun(c, x, y, r, t=0.0, face=True):
    c.glow(x, y, r * 2.4, r * 2.4, (255, 246, 190), (200, 232, 255), steps=8)
    for k in range(12):
        a = k * math.tau / 12 + t * 0.3
        c.line([(x + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2),
                (x + math.cos(a) * r * 1.55, y + math.sin(a) * r * 1.55)], (255, 210, 80), 5)
    c.circle(x, y, r, (255, 222, 96), ol=(230, 160, 50), w=3)
    if face:
        c.arc(x - r * 0.33, y - r * 0.1, r * 0.14, r * 0.12, 200, 340, OUT, 2.5)
        c.arc(x + r * 0.33, y - r * 0.1, r * 0.14, r * 0.12, 200, 340, OUT, 2.5)
        c.arc(x, y + r * 0.2, r * 0.3, r * 0.22, 20, 160, OUT, 2.5)
        c.circle(x - r * 0.55, y + r * 0.2, r * 0.12, (255, 170, 120), ol=None)
        c.circle(x + r * 0.55, y + r * 0.2, r * 0.12, (255, 170, 120), ol=None)


def rain_cloud(c, x, y, s=1.0, t=0.0, face=True, col=(236, 240, 250), rain=0.0, eyes="open"):
    """A puffy outlined cloud with a little face; rain 0..1 lets drops fall from it."""
    c.push(x, y, s)
    lobes = ((-70, 6, 36), (-30, -22, 46), (24, -30, 52), (70, 0, 38), (0, 10, 44))
    for dx, dy, r in lobes:
        c.circle(dx, dy, r + 3, OUT, ol=None)
    for dx, dy, r in lobes:
        c.circle(dx, dy, r, col, ol=None)
    c.ellipse(-10, -26, 30, 12, (255, 255, 255), ol=None)
    if face:
        if eyes == "closed":
            c.arc(-18, 2, 7, 5, 20, 160, OUT, 2.5)
            c.arc(18, 2, 7, 5, 20, 160, OUT, 2.5)
        else:
            c.circle(-18, 0, 4, OUT, ol=None)
            c.circle(18, 0, 4, OUT, ol=None)
        c.arc(0, 10, 8, 6, 20, 160, OUT, 2.5)
        c.circle(-32, 12, 5, (255, 200, 210), ol=None)
        c.circle(32, 12, 5, (255, 200, 210), ol=None)
    c.pop()
    if rain > 0.01:
        rng = np.random.default_rng(3)
        for k in range(int(10 * rain)):
            dx = rng.uniform(-90, 90) * s
            u = (t * 1.4 + rng.random()) % 1
            yy = y + 40 * s + u * 160 * s
            c.line([(x + dx, yy), (x + dx - 3, yy + 14 * s)], (110, 170, 240), 3)


# ======================================================================= diagrams

def lake_map(ic, k=1.0, t=0.0):
    """Inset: a lake seen from above, with land all around it."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.rect(0, 0, w, h, GRASS, ol=None)
    rng = np.random.default_rng(4)
    for _ in range(14):
        x, y = rng.uniform(10, w - 10), rng.uniform(10, h - 10)
        if ((x - w / 2) / 150) ** 2 + ((y - h / 2) / 80) ** 2 > 1.3:
            ic.circle(x, y, rng.uniform(10, 16), (80, 150, 80), w=2)
    ic.line([(30, 0), (60, 40), (110, 70), (150, h / 2 - 20)], WATER, 10)
    ic.line([(w - 140, h / 2 + 20), (w - 90, h / 2 + 50), (w - 50, h - 20), (w - 30, h)], WATER, 12)
    ic.poly(lake_poly(w / 2, h / 2, 140, 74, 0.1, seed=5), BANK, w=3)
    ic.poly(lake_poly(w / 2, h / 2, 128, 64, 0.1, seed=5), WATER, w=3)
    K.text(ic, w / 2, h / 2, "Lake", 34, (255, 255, 255), stroke=3, stroke_fill=WATER_D)
    if k > 0.3:
        K.text(ic, w / 2, 22, "Land all around", 26, (255, 255, 255), stroke=3, stroke_fill=(50, 100, 50))
        for a in (-0.5, 0.5, math.pi - 0.5, math.pi + 0.5):
            x0, y0 = w / 2 + math.cos(a) * 190, h / 2 + math.sin(a) * 110
            x1, y1 = w / 2 + math.cos(a) * 150, h / 2 + math.sin(a) * 84
            K.arrow(ic, x0, y0, x1, y1, (255, 236, 110), 5, clamp((k - 0.3) / 0.4), head=12)


def _arc_pts(cx, cy, rx, ry, a0, a1, n=30):
    return [(cx + math.cos(a) * rx, cy + math.sin(a) * ry) for a in np.linspace(math.radians(a0),
                                                                               math.radians(a1), n)]


def arc_arrow(c, cx, cy, rx, ry, a0, a1, k, col=(255, 236, 110), w=9, head=20):
    """Curved arrow along an ellipse from angle a0 to a1 (degrees), grown to k."""
    if k <= 0.02:
        return
    pts = _arc_pts(cx, cy, rx, ry, a0, lerp(a0, a1, k))
    (x1, y1), (x0, y0) = pts[-1], pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - math.cos(ang) * head * 0.6, y1 - math.sin(ang) * head * 0.6
    c.stroke(pts[:-1] + [(bx, by)], col, w)
    px, py = -math.sin(ang), math.cos(ang)
    tip = (x1 + math.cos(ang) * head * 0.5, y1 + math.sin(ang) * head * 0.5)
    c.poly([tip, (bx + px * head * 0.75, by + py * head * 0.75), (bx - px * head * 0.75, by - py * head * 0.75)],
           col, w=3)


CYCLE = [  # (from angle, to angle, label, label position)
    (40, -40, "Vapour rises", (0.86, 0.47)),
    (-60, -120, "Clouds", (0.5, 0.07)),
    (-140, -220, "Rain falls", (0.13, 0.47)),
    (140, 50, "Rivers flow to the sea", (0.5, 0.93)),
]


def cycle_scene(ic, t, ks, drop_u=None, labels=True):
    """The water cycle as a circle of arrows over a little landscape.
    ks: growth of the 4 arrows (vapour, clouds, rain, river); drop_u: Drip's position 0..1 round the loop."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 205, 250)), (0.62, (215, 238, 255)),
                                                       (0.63, (80, 160, 228)), (1, (60, 136, 210))]), (0, 0))
    hy = h * 0.63
    # land on the left with a snowy mountain, the sea on the right
    ic.poly([(0, hy - 20), (w * 0.55, hy - 10), (w * 0.62, hy + 30), (w * 0.58, h), (0, h)], GRASS, w=3)
    mx = w * 0.2
    ic.poly([(mx - 120, hy), (mx, hy - 150), (mx + 120, hy)], ROCK, w=3)
    ic.poly([(mx - 46, hy - 92), (mx, hy - 150), (mx + 46, hy - 92), (mx + 20, hy - 100), (mx, hy - 86),
             (mx - 22, hy - 102)], SNOW, w=2.5)
    ic.line([(mx + 20, hy - 60), (mx + 80, hy - 20), (w * 0.35, hy + 20), (w * 0.48, hy + 40), (w * 0.6, hy + 30)],
            WATER, 12)
    for k in range(4):
        x = w * 0.66 + k * 70
        ic.arc(x, hy + 34, 20, 7, 200, 340, (200, 232, 255), 3)
        ic.arc(x + 34, hy + 64, 20, 7, 200, 340, (200, 232, 255), 3)
    sun(ic, w * 0.9, h * 0.15, 32, t, face=False)
    rain_cloud(ic, w * 0.36, h * 0.2, 0.62, t, face=False, rain=ks[2] if ks[2] > 0 else 0)
    # vapour wiggles over the sea
    if ks[0] > 0:
        for k in range(3):
            x = w * 0.72 + k * 40
            u = (t * 0.5 + k / 3) % 1
            pts = [(x + 6 * math.sin(j * 0.9 + t * 4), hy - 10 - j * 9 - u * 30) for j in range(8)]
            ic.line(pts, mix((255, 255, 255), (150, 205, 250), u), 3)
    # the circle of arrows
    cx, cy, rx, ry = w / 2, h * 0.5, w * 0.36, h * 0.36
    for (a0, a1, lab, (lx, ly)), k in zip(CYCLE, ks):
        arc_arrow(ic, cx, cy, rx, ry, a0, a1, ease(k), (255, 236, 110), 10, 26)
        if labels and k > 0.5:
            K.label(ic, w * lx, h * ly, lab, 22, k=clamp((k - 0.5) * 2))
    if drop_u is not None:
        a = math.radians(40 - 360 * drop_u)
        drip(ic, cx + math.cos(a) * rx, cy + math.sin(a) * ry + 16, 0.6, t, eyes="happy")


# ========================================================================= icons

def icon_downhill(c, x, y, r, t=0.0):
    """A snowy mountain with a river running down to the sea."""
    c.ellipse(x + r * 0.45, y + r * 0.62, r * 0.5, r * 0.18, WATER, w=2)
    c.poly([(x - r * 0.95, y + r * 0.6), (x - r * 0.3, y - r * 0.75), (x + r * 0.35, y + r * 0.6)], ROCK, w=2.5)
    c.poly([(x - r * 0.52, y - r * 0.3), (x - r * 0.3, y - r * 0.75), (x - r * 0.08, y - r * 0.3)], SNOW, w=2)
    c.line([(x - r * 0.3, y - r * 0.3), (x - r * 0.15, y + r * 0.1), (x + r * 0.15, y + r * 0.35),
            (x + r * 0.45, y + r * 0.6)], WATER, 6)
    K.arrow(c, x + r * 0.15, y - r * 0.55, x + r * 0.8, y + r * 0.05, (240, 90, 80), 5, 1.0, head=12)


def icon_fresh(c, x, y, r, t=0.0):
    """A happy water drop with a green tick: fresh water."""
    drip(c, x - r * 0.1, y + r * 0.62, r / 40, t, eyes="happy")
    c.circle(x + r * 0.55, y + r * 0.45, r * 0.3, (90, 190, 100), w=2.5)
    c.line([(x + r * 0.42, y + r * 0.45), (x + r * 0.52, y + r * 0.56), (x + r * 0.7, y + r * 0.33)],
           (255, 255, 255), 4)


def icon_cycle(c, x, y, r, t=0.0):
    """Circle of arrows round a raindrop."""
    for a0 in (-80, 40, 160):
        arc_arrow(c, x, y, r * 0.78, r * 0.78, a0 + t * 40, a0 + 95 + t * 40, 1.0, (70, 150, 230), 6, 14)
    drip(c, x, y + r * 0.35, r / 60, t, eyes="happy")


def icon_uphill(c, x, y, r, t=0.0, down=False):
    """A slope with a river; the arrow goes up (wrong) or down (right)."""
    c.poly([(x - r * 1.1, y + r * 0.7), (x - r * 1.1, y - r * 0.6), (x + r * 1.1, y + r * 0.7)], GRASS, w=3)
    c.line([(x - r * 1.05, y - r * 0.45), (x, y + r * 0.1), (x + r * 1.0, y + r * 0.66)], WATER, 10)
    if down:
        K.arrow(c, x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.1, (90, 190, 100), 8, 1.0, head=20)
    else:
        K.arrow(c, x + r * 0.6, y + r * 0.1, x - r * 0.6, y - r * 0.6, (240, 90, 80), 8, 1.0, head=20)


def icon_downhill_q(c, x, y, r, t=0.0):
    icon_uphill(c, x, y, r, t, down=True)
