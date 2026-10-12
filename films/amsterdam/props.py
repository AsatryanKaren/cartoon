"""Props and new characters for "Whiskers and the Wobbly Bicycle" (Amsterdam).

Everything is drawn in the flat cartoon style of draw.py, local space with
origin on the ground (y up is negative) unless a docstring says otherwise.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix

# --------------------------------------------------------------- palettes

BRAM = dict(body=(58, 56, 68), dark=(38, 36, 46), belly=(250, 250, 248), ear=(240, 160, 172),
            eye=(236, 196, 64), stripes=False, collar=(250, 128, 30))
SNOWY = dict(body=(248, 246, 240), dark=(222, 216, 210), belly=(255, 255, 255), ear=(250, 180, 190),
             eye=(90, 170, 230), stripes=False, collar=(220, 60, 70))
CREAM = dict(body=(236, 206, 150), dark=(206, 170, 110), belly=(255, 240, 214), ear=(250, 176, 170),
             eye=(120, 180, 90), stripes=True, collar=None)
SOOT = dict(body=(80, 76, 86), dark=(60, 56, 66), belly=(150, 146, 156), ear=(230, 150, 160),
            eye=(130, 210, 120), stripes=False, collar=(60, 170, 110))
GINGER2 = dict(body=(200, 120, 70), dark=(160, 88, 50), belly=(250, 220, 190), ear=(250, 170, 160),
               eye=(110, 170, 220), stripes=True, collar=(70, 90, 200))

ORANGE = (250, 130, 30)
CHEESE = (255, 206, 70)
CHEESE_D = (230, 166, 40)
RIND = (240, 180, 50)
WOOD = (150, 100, 60)
WOOD_D = (110, 70, 42)
CLOG = (250, 214, 90)
BRICK = (176, 96, 76)
WATER = (64, 112, 130)
TULIP_COLS = [(232, 50, 60), (250, 210, 60), (240, 120, 170), (255, 140, 40), (170, 70, 170), (255, 255, 250)]


def _text(c, x, y, s, size, fill, **kw):
    c.text(x, y, s, size * c.scale, fill, **kw)


# ------------------------------------------------------------ canal houses

def canal_house(c, x0, base, w, h, wall, rng, gable="step", trim=(250, 248, 240), lit=None, door=None):
    """A narrow Amsterdam canal house, front view. lit: None or list-of-bools source (rng) for lit windows."""
    top = base - h
    g = w * 0.62
    cx = x0 + w / 2
    # gable outline (drawn as one polygon together with the body)
    if gable == "step":
        st = g / 3
        stepw = w * 0.11
        left = [(x0, top)]
        for i in range(3):
            left += [(x0 + stepw * i, top - st * (i + 1) + st), (x0 + stepw * i, top - st * (i + 1)),
                     (x0 + stepw * (i + 1), top - st * (i + 1))]
        pts = left + [(x0 + w - p[0] + x0, p[1]) for p in reversed(left)]
        peak_y = top - g
    elif gable == "bell":
        prof = [(0.0, 0.0), (0.1, -0.06), (0.14, -0.2), (0.1, -0.38), (0.18, -0.55), (0.3, -0.78), (0.38, -0.93),
                (0.5, -1.0)]
        left = [(x0 + u * w, top + v * g) for u, v in prof]
        pts = left[:-1] + [(x0 + w - (p[0] - x0), p[1]) for p in reversed(left)]
        peak_y = top - g
    elif gable == "neck":
        nw = 0.24 * w
        sh = 0.36 * g
        pts = [(x0, top), (x0 + 0.08 * w, top - sh * 0.4), (cx - nw, top - sh), (cx - nw, top - g * 0.95),
               (cx, top - g * 1.12), (cx + nw, top - g * 0.95), (cx + nw, top - sh),
               (x0 + 0.92 * w, top - sh * 0.4), (x0 + w, top)]
        peak_y = top - g * 1.12
    elif gable == "spout":
        pts = [(x0, top), (x0 + 0.1 * w, top - 0.1 * g), (cx, top - g * 0.95), (x0 + 0.9 * w, top - 0.1 * g),
               (x0 + w, top)]
        peak_y = top - g * 0.95
    else:   # flat with cornice
        pts = [(x0, top), (x0, top - 14), (x0 + w, top - 14), (x0 + w, top)]
        peak_y = top - 14
    body = [(x0, base)] + pts + [(x0 + w, base)]
    c.poly(body, wall, w=2.5)
    # white trim along the gable edge
    if gable in ("step", "bell", "neck", "spout"):
        c.line(pts, trim, 3, cap=False)
    else:
        c.rect(x0 - 4, top - 18, x0 + w + 4, top - 6, trim, w=2)
    if gable == "neck":
        for side in (-1, 1):
            c.circle(cx + side * (0.24 * w + 8), top - 0.36 * g - 6, 7, trim, w=1.5)
    # hoisting beam with its hook
    hy = peak_y + (22 if gable != "flat" else 34)
    if gable == "flat":
        hy = top - 4
    c.rect(cx - 5, hy - 6, cx + 5, hy + 4, (70, 50, 40), w=1.5)
    c.line([(cx, hy + 4), (cx, hy + 18)], (60, 60, 60), 1.5, cap=False)
    c.arc(cx + 3, hy + 20, 4, 4, 0, 200, (60, 60, 60), 2)
    # gable window
    if gable in ("step", "bell", "neck"):
        gy = top - g * 0.45
        c.rect(cx - 9, gy - 13, cx + 9, gy + 13, trim, w=1.5, r=8 if gable == "bell" else 0)
        c.rect(cx - 6, gy - 9, cx + 6, gy + 10, (60, 70, 90) if not lit else (255, 214, 120), ol=None,
               r=6 if gable == "bell" else 0)
    # windows
    n = 2 if w < 120 else 3
    floors = max(2, int((h - 70) / 62))
    fh = (h - 70) / floors
    ww = min(26, w / (n + 1) * 0.75)
    for f in range(floors):
        wy = top + 14 + f * fh
        wh = fh * 0.66 if f else fh * 0.55
        for k in range(n):
            wx = x0 + w * (k + 1) / (n + 1)
            on = lit is not None and rng.random() < lit
            glass = (255, 214, 120) if on else (70, 84, 110)
            c.rect(wx - ww / 2 - 3, wy - 3, wx + ww / 2 + 3, wy + wh + 3, trim, w=1.5)
            c.rect(wx - ww / 2, wy, wx + ww / 2, wy + wh, glass, ol=None)
            if not on:
                c.line([(wx - ww / 2 + 3, wy + wh * 0.7), (wx - ww / 2 + 9, wy + 3)], (130, 150, 180), 2, cap=False)
            c.line([(wx, wy), (wx, wy + wh)], trim, 2, cap=False)
            c.line([(wx - ww / 2, wy + wh * 0.45), (wx + ww / 2, wy + wh * 0.45)], trim, 2, cap=False)
    # door with a little stoop
    dcol = door or mix(wall, (30, 30, 40), 0.55)
    dx = x0 + w * (0.3 if rng.random() < 0.5 else 0.7)
    c.rect(dx - 13, base - 54, dx + 13, base - 6, dcol, w=2, r=4)
    c.rect(dx - 13, base - 66, dx + 13, base - 56, (255, 230, 150) if lit else (150, 170, 196), w=1.5)
    c.circle(dx + 7, base - 30, 2, (240, 210, 90), ol=None)
    c.rect(dx - 20, base - 7, dx + 20, base, (190, 180, 170), w=1.5)


HOUSE_WALLS = [(150, 68, 52), (118, 62, 50), (56, 84, 74), (52, 54, 64), (232, 216, 184), (238, 234, 224),
               (108, 128, 150), (204, 150, 82), (160, 52, 52), (130, 90, 70), (84, 104, 130), (190, 110, 80)]
GABLES = ["step", "bell", "neck", "spout", "flat", "bell", "step", "neck"]


def house_row(c, x0, x1, base, rng, hmin=210, hmax=320, lit=None, s=1.0):
    x = x0
    last = None
    while x < x1:
        w = rng.uniform(96, 150) * s
        h = rng.uniform(hmin, hmax) * s
        wall = HOUSE_WALLS[int(rng.integers(len(HOUSE_WALLS)))]
        if wall == last:
            wall = HOUSE_WALLS[(HOUSE_WALLS.index(wall) + 3) % len(HOUSE_WALLS)]
        last = wall
        canal_house(c, x, base, w, h, wall, rng, GABLES[int(rng.integers(len(GABLES)))], lit=lit)
        x += w


def elm(c, x, y, s=1.0, leaf=(92, 150, 84), trunk=(110, 84, 64)):
    c.push(x, y, s)
    c.poly([(-9, 0), (-6, -150), (6, -150), (9, 0)], trunk, w=2.5)
    c.line([(0, -110), (-36, -170)], trunk, 6)
    c.line([(0, -120), (34, -180)], trunk, 6)
    dark = mix(leaf, (0, 0, 0), 0.15)
    blobs = ((-60, -190, 46), (60, -196, 48), (0, -236, 56), (-20, -170, 44), (30, -160, 40), (-80, -150, 30),
             (84, -158, 30))
    for dx, dy, r in blobs:
        c.circle(dx, dy, r, dark)
    for dx, dy, r in blobs:
        c.circle(dx - 4, dy - 6, r * 0.82, leaf, ol=None)
    c.pop()


def lamp_post(c, x, y, s=1.0, lit=0.0):
    c.push(x, y, s)
    green = (40, 64, 58)
    c.rect(-7, -8, 7, 0, green, w=2)
    c.rect(-3, -150, 3, -8, green, w=2)
    c.line([(0, -150), (16, -158), (26, -150)], green, 4)
    glass = mix((200, 210, 200), (255, 230, 150), lit)
    c.poly([(16, -150), (36, -150), (32, -128), (20, -128)], glass, w=2)
    c.rect(14, -154, 38, -150, green, w=1.5)
    c.pop()


def lamp_glow(c, x, y, s, lit, sky):
    if lit > 0.02:
        c.glow(x + 26 * s, y - 140 * s, 60 * s, 60 * s, mix(sky, (255, 220, 140), 0.55 * lit), sky, steps=7)


def bollard(c, x, y, s=1.0):
    c.rect(x - 6 * s, y - 26 * s, x + 6 * s, y, (120, 40, 40), w=2, r=5 * s)
    c.rect(x - 7 * s, y - 20 * s, x + 7 * s, y - 16 * s, (245, 240, 230), ol=None)


def bunting(c, x0, x1, y, sag, n, cols=(ORANGE, (240, 240, 240), (40, 90, 180), (220, 50, 50))):
    pts = [(lerp(x0, x1, u), y + sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 30)]
    c.line(pts, (80, 70, 70), 2, cap=False)
    for k in range(n):
        u = (k + 0.5) / n
        x = lerp(x0, x1, u)
        yy = y + sag * 4 * u * (1 - u)
        c.poly([(x - 10, yy), (x + 10, yy), (x, yy + 22)], cols[k % len(cols)], w=1.5)


# ----------------------------------------------------------------- flowers

def tulip(c, x, y, col, s=1.0, sway=0.0):
    c.push(x, y, s)
    tx = sway * 4
    c.line([(0, 0), (tx, -30)], (70, 140, 70), 3)
    c.poly([(0, -4), (-12, -20), (-2, -14)], (90, 160, 80), w=1.2)
    c.poly([(tx - 8, -30), (tx - 9, -44), (tx - 3, -38), (tx, -47), (tx + 3, -38), (tx + 9, -44), (tx + 8, -30),
            (tx, -26)], col, w=1.5)
    c.pop()


def tulip_bunch(c, x, y, s=1.0, n=5, seed=0, t=0.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        dx = (k - (n - 1) / 2) * 7
        tulip(c, x + dx, y, TULIP_COLS[int(rng.integers(len(TULIP_COLS)))], s * rng.uniform(0.8, 1.0),
              sway=math.sin(t * 2 + k))


# ------------------------------------------------------------------ cheese

def cheese_side(c, x, y, rx, h, col=CHEESE, label=True):
    """A Gouda cheese lying flat, seen from the side a bit above: (x, y) bottom centre."""
    ry = rx * 0.32
    c.rect(x - rx, y - h, x + rx, y, col, w=2.5, r=h * 0.45)
    c.ellipse(x, y - h + 1, rx * 0.97, ry, mix(col, (255, 255, 255), 0.25), w=2)
    if label:
        c.rect(x - rx * 0.25, y - h * 0.62, x + rx * 0.25, y - h * 0.22, (240, 240, 230), w=1.2, r=2)
        c.line([(x - rx * 0.15, y - h * 0.42), (x + rx * 0.15, y - h * 0.42)], (200, 60, 50), 2, cap=False)


def cheese_wheel(c, x, y, r, ang=0.0, col=CHEESE):
    """A cheese standing on its edge, round face to us, rolling. (x, y) = centre."""
    c.circle(x, y, r, RIND)
    c.circle(x, y, r * 0.82, col, w=2)
    c.circle(x - r * 0.25, y - r * 0.3, r * 0.3, mix(col, (255, 255, 255), 0.35), ol=None)
    # the paper label turns as it rolls
    lx, ly = x + math.cos(ang) * r * 0.45, y + math.sin(ang) * r * 0.45
    c.circle(lx, ly, r * 0.2, (245, 242, 230), w=1.5)
    c.circle(lx, ly, r * 0.1, (210, 60, 50), ol=None)
    for k in range(3):
        a = ang + math.pi * 0.7 + k * 0.5
        c.circle(x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55, r * 0.05, mix(col, (0, 0, 0), 0.15),
                 ol=None)


def stretcher(c, x, y, s=1.0, n=3, pile=True):
    """A cheese-carriers' wooden stretcher (berrie) heaped with cheeses. (x, y) ground centre."""
    c.push(x, y, s)
    c.line([(-110, -40), (110, -40)], WOOD_D, 6)
    for lx in (-80, 80):
        c.line([(lx, -40), (lx - 6, 0)], WOOD_D, 5)
    c.rect(-80, -52, 80, -38, (220, 120, 60), w=2)
    if pile:
        for k in range(n):
            cheese_side(c, -54 + 54 * k, -52, 30, 22, label=k == 1)
        for k in range(n - 1):
            cheese_side(c, -27 + 54 * k, -70, 30, 22, label=False)
        if n >= 3:
            cheese_side(c, 0, -88, 30, 22)
    c.pop()


def stroopwafel(c, x, y, r, bite=0.0):
    c.circle(x, y, r, (196, 130, 60))
    c.circle(x, y, r * 0.86, (214, 152, 76), ol=None)
    for k in range(-3, 4):
        d = k * r / 3.6
        if abs(d) < r * 0.85:
            hw = math.sqrt((r * 0.86) ** 2 - d * d)
            c.line([(x - hw * 0.95, y + d), (x + hw * 0.95, y + d)], (176, 112, 50), 1.5, cap=False)
            c.line([(x + d, y - hw * 0.95), (x + d, y + hw * 0.95)], (176, 112, 50), 1.5, cap=False)
    if bite > 0:
        for k in range(3):
            c.circle(x + r * 0.8, y - r * 0.3 + k * r * 0.3, r * 0.3 * bite, (255, 255, 255), ol=None)


def clog(c, x, y, s=1.0, col=CLOG, face=1):
    c.push(x, y, s, flip=face < 0)
    c.poly([(-24, 0), (-30, -14), (-28, -28), (-4, -28), (8, -20), (26, -16), (38, -22), (36, -8), (28, 0)],
           col, w=2)
    c.ellipse(-16, -27, 11, 4, (70, 46, 30), w=1.5)
    c.circle(16, -10, 4, (230, 80, 60), ol=None)
    c.circle(8, -8, 2.5, (80, 150, 220), ol=None)
    c.circle(24, -9, 2.5, (80, 150, 220), ol=None)
    c.pop()


# --------------------------------------------------------------- windmill

def windmill(c, x, base, s=1.0, ang=0.0, body=(70, 84, 74), cap=(60, 60, 64), sail=(236, 230, 214), ol=OUT,
             w=2.5):
    c.push(x, base, s)
    c.poly([(-46, 0), (-30, -200), (30, -200), (46, 0)], body, ol=ol, w=w)
    for k in range(3):
        y0 = -40 - k * 56
        c.rect(-8, y0 - 22, 8, y0, (240, 236, 220), ol=ol, w=1.5)
    c.rect(-10, -26, 10, 0, (110, 60, 40), ol=ol, w=1.5, r=8)
    c.rect(-56, -112, 56, -104, (110, 80, 60), ol=ol, w=1.5)   # stage
    c.poly([(-34, -200), (-28, -232), (0, -244), (28, -232), (34, -200)], cap, ol=ol, w=w)
    hub = (0, -218)
    for k in range(4):
        a = ang + k * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        px, py = -sa, ca
        L, wd = 150, 26

        def P(u, v):
            return (hub[0] + ca * u + px * v, hub[1] + sa * u + py * v)
        c.line([P(0, 0), P(L, 0)], (90, 70, 56), 4, cap=False)
        c.poly([P(30, 2), P(L, 2), P(L, wd), P(30, wd)], sail, ol=ol, w=1.5)
        for u in (60, 90, 120):
            c.line([P(u, 2), P(u, wd)], mix(sail, (0, 0, 0), 0.25), 1.2, cap=False)
        c.line([P(30, wd * 0.5), P(L, wd * 0.5)], mix(sail, (0, 0, 0), 0.25), 1.2, cap=False)
    c.circle(hub[0], hub[1], 7, (90, 70, 56), ol=ol, w=1.5)
    c.pop()


# ---------------------------------------------------------------- bicycle

BIKE_BLACK = (44, 44, 52)


def wheel(c, x, y, r, ang, col=BIKE_BLACK):
    c.circle(x, y, r, None, ol=col, w=4)
    c.circle(x, y, r - 2, None, ol=(90, 90, 100), w=1.2)
    for k in range(6):
        a = ang + k * math.pi / 6
        c.line([(x - math.cos(a) * r, y - math.sin(a) * r), (x + math.cos(a) * r, y + math.sin(a) * r)],
               (170, 170, 180), 1.0, cap=False)
    c.circle(x, y, 3.5, (150, 150, 160), w=1.2)


RW, FW, WR = (-46, -30), (50, -30), 30
CRANK = (-4, -32)
SADDLE = (-20, -88)
HEAD = (36, -82)
GRIP = (22, -106)


def bicycle(c, x, y, s=1.0, face=1, ang=0.0, col=BIKE_BLACK, basket=True, flowers=0, seed=0, t=0.0,
            rider=None, front_fn=None, lean=0.0):
    """A Dutch 'omafiets'. rider(c) draws the cyclist in bike space between frame and front parts.
    front_fn(c) draws things in the basket. ang = wheel rotation (distance / radius)."""
    c.push(x, y, s, flip=face < 0)
    wheel(c, *RW, WR, ang)
    # fenders
    c.arc(RW[0], RW[1], WR + 4, WR + 4, 190, 330, col, 3)
    # frame
    c.line([CRANK, RW], col, 4)
    c.line([RW, (SADDLE[0] + 3, SADDLE[1] + 12)], col, 4)
    c.line([CRANK, (SADDLE[0] + 2, SADDLE[1] + 4)], col, 4)
    c.line([CRANK, (14, -58), HEAD], col, 4)
    c.line([HEAD, FW], col, 4)
    c.line([HEAD, (HEAD[0] - 2, GRIP[1] + 2)], col, 4)
    c.line([(HEAD[0] - 2, GRIP[1] + 2), (GRIP[0] + 2, GRIP[1])], col, 4)
    c.ellipse(SADDLE[0], SADDLE[1], 13, 4.5, (90, 60, 40), w=1.5)
    # chain guard
    c.poly([(-10, -38), (-44, -36), (-44, -26), (-6, -24)], mix(col, (255, 255, 255), 0.12), w=1.5)
    # crank & pedals
    for k in (0, 1):
        a = ang * 0.8 + k * math.pi
        px, py = CRANK[0] + math.cos(a) * 12, CRANK[1] + math.sin(a) * 12
        c.line([CRANK, (px, py)], (120, 120, 130), 2.5)
        c.rect(px - 5, py - 2, px + 5, py + 2, (40, 40, 40), ol=None)
    c.circle(CRANK[0], CRANK[1], 5, (150, 150, 160), w=1.5)
    if flowers:
        rng = np.random.default_rng(seed)
        for k in range(flowers):
            u = k / max(1, flowers - 1)
            fx, fy = lerp(CRANK[0], HEAD[0], u), lerp(CRANK[1], HEAD[1], u) - 4
            col_ = TULIP_COLS[int(rng.integers(len(TULIP_COLS)))]
            c.circle(fx, fy, 5, col_, w=1.2)
            c.ellipse(fx - 6, fy + 3, 5, 2.5, (90, 160, 80), ol=None)
    if rider:
        rider(c)
    wheel(c, *FW, WR, ang)
    c.arc(FW[0], FW[1], WR + 4, WR + 4, 210, 350, col, 3)
    # front light
    c.circle(HEAD[0] + 5, HEAD[1] + 6, 4, (250, 240, 200), w=1.5)
    if basket:
        if front_fn:
            front_fn(c)
        c.rect(44, -100, 82, -74, (190, 140, 80), w=2, r=3)
        for k in range(1, 4):
            c.line([(44 + k * 9.5, -100), (44 + k * 9.5, -74)], (150, 100, 60), 1.2, cap=False)
        c.line([(44, -87), (82, -87)], (150, 100, 60), 1.2, cap=False)
        if flowers:
            tulip_bunch(c, 63, -96, 0.55, 5, seed + 1, t)
    # little bell on the handlebar
    c.circle(GRIP[0] + 6, GRIP[1] - 4, 3.5, (230, 230, 120), w=1.2)
    c.pop()


def bike_cat(c, x, y, pal, s=1.0, face=1, dist=0.0, t=0.0, mouth=0.0, eyes="open", seed=0.0, look=(0.6, 0),
             flowers=0, front_fn=None, head_dy=0.0, wet=0.0, bike_col=BIKE_BLACK, wobble=0.0, arm_up=0.0,
             basket=True):
    """A cat riding a bicycle. dist = distance travelled (output px) for wheel and pedal rotation."""
    ang = dist / (WR * s)
    pedal = ang * 0.8

    def rider(cc):
        ks = 0.6
        ox, oy = SADDLE[0] + 8, SADDLE[1] - 2
        # far leg to the back pedal
        a1 = pedal + math.pi
        p1 = (CRANK[0] + math.cos(a1) * 12, CRANK[1] + math.sin(a1) * 12)
        cc.stroke([(ox - 2, oy - 8), ((ox + p1[0]) / 2 + 8, (oy + p1[1]) / 2), p1], pal["dark"], 8)
        D.cat(cc, ox, oy, pal, ks, 1, "sit", t=t, mouth=mouth, eyes=eyes, look=look, seed=seed,
              head_dy=head_dy, wet=wet, tail=math.sin(t * 3 + seed))
        # near leg to the front pedal
        a0 = pedal
        p0 = (CRANK[0] + math.cos(a0) * 12, CRANK[1] + math.sin(a0) * 12)
        cc.stroke([(ox + 2, oy - 8), ((ox + p0[0]) / 2 + 10, (oy + p0[1]) / 2 - 2), p0], pal["body"], 9)
        cc.ellipse(p0[0] + 2, p0[1] - 2, 6, 4, pal["body"], w=2)
        # arm to the handlebar (or waving)
        sh = (ox + 10, oy - 40)
        if arm_up > 0:
            wv = math.sin(t * 12) * 6
            hand = (sh[0] + 14 + wv, sh[1] - 34 * arm_up)
        else:
            hand = (GRIP[0] + 2, GRIP[1] + 1)
        cc.stroke([sh, hand], pal["body"], 8)
        cc.ellipse(hand[0], hand[1], 5, 4, pal["body"], w=2)

    bicycle(c, x, y, s, face, ang, bike_col, basket, flowers, int(seed * 10), t, rider, front_fn)


# --------------------------------------------------------------- houseboat

def houseboat(c, x, y, s=1.0, t=0.0, body=(46, 98, 80), cabin=(232, 210, 160), roof=(150, 60, 50), bike=True,
              bob=True):
    """A canal houseboat; (x, y) = waterline centre. Cabin on the right, open deck on the left
    (deck surface at y - 44*s, from x - 280*s to x - 70*s)."""
    c.push(x, y + (2 * math.sin(t * 1.2) if bob else 0), s)
    c.poly([(-290, -44), (290, -44), (300, -20), (280, 12), (-280, 12), (-300, -20)], body, w=3)
    c.line([(-284, -16), (284, -16)], (250, 200, 80), 3, cap=False)
    for k in range(5):                     # tyre fenders on the side
        c.circle(-220 + k * 110, -22, 11, None, ol=(40, 40, 40), w=4)
    # cabin
    c.rect(-60, -150, 262, -48, cabin, w=3)
    c.rect(-72, -164, 274, -146, roof, w=2.5, r=3)
    for k in range(4):
        wx = 0 + k * 66
        c.rect(wx, -128, wx + 42, -88, (110, 160, 190), w=2, r=3)
        c.line([(wx + 21, -128), (wx + 21, -88)], (250, 246, 236), 2, cap=False)
        c.rect(wx - 4, -86, wx + 46, -74, (200, 70, 60), w=1.5)          # flower box
        for f in range(4):
            c.circle(wx + 6 + f * 12, -88, 5, TULIP_COLS[(k + f) % len(TULIP_COLS)], w=1.2)
    c.rect(-48, -138, -16, -48, (80, 120, 100), w=2, r=3)               # door
    c.circle(-24, -92, 3, (240, 210, 90), ol=None)
    # roof garden: pots and a little chimney
    c.rect(230, -196, 246, -164, (90, 90, 96), w=2)
    for k, px in enumerate((40, 90, 200)):
        c.rect(px - 12, -182, px + 12, -164, (200, 110, 70), w=2)
        D.bush(c, px, -180, 0.45, col=(80, 150, 80))
    if bike:
        bicycle(c, 150, -164, 0.55, -1, 0.0, col=(200, 60, 60), basket=True)
    # deck rail (low) at the stern, the deck edge
    c.rect(-292, -48, 292, -40, (250, 246, 236), w=2)
    for k in range(5):
        c.line([(-280 + k * 50, -48), (-280 + k * 50, -70)], (240, 236, 226), 3, cap=False)
    c.line([(-282, -70), (-80, -70)], (240, 236, 226), 3, cap=False)
    c.pop()


# --------------------------------------------------------------- the stork

STORK_W = (250, 250, 248)
STORK_B = (40, 40, 48)
STORK_R = (240, 110, 60)
POST = (40, 90, 170)


def stork(c, x, y, s=1.0, face=1, t=0.0, pose="stand", flap=0.0, mouth=0.0, eyes="open", hold=None,
          head_dx=0.0, wing_wave=0.0, seed=5.0):
    """Joost, a white stork mailman with a blue cap and a satchel.

    pose 'stand': (x, y) = feet.  pose 'fly': (x, y) = body centre, flap = wing phase (radians).
    hold: None | 'letter' | 'basket' (the basket handle hangs from his beak).
    Returns the beak tip in output coordinates.
    """
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    if pose == "stand":
        # legs
        for lx in (-10, 8):
            c.line([(lx, -118), (lx + 2, -60), (lx, 0)], STORK_R, 5)
            c.line([(lx - 8, 0), (lx + 12, 0)], STORK_R, 4)
        # tail + body
        c.poly([(-56, -150), (-84, -142), (-78, -128), (-50, -130)], STORK_B, w=2.5)
        c.ellipse(-4, -148, 52, 32, STORK_W, w=3)
        # wing (folded), raised when waving
        if wing_wave > 0:
            wv = math.sin(t * 10) * 0.3
            a = -1.2 * wing_wave + wv
            c.push(0, -160)
            pts = [(0, 0), (-40, -10), (-70 * math.cos(a) - 10, 70 * math.sin(a) - 10), (-50 * math.cos(a), 50 * math.sin(a) + 8)]
            c.poly(pts, STORK_W, w=2.5)
            c.line([pts[2], pts[3]], STORK_B, 8)
            c.pop()
        else:
            c.poly([(14, -166), (-48, -164), (-66, -136), (-20, -128)], STORK_W, w=2.5)
            c.poly([(-48, -164), (-74, -142), (-66, -128), (-40, -138)], STORK_B, w=2)
        # satchel
        c.line([(20, -170), (-14, -126)], (110, 70, 40), 4)
        c.rect(-34, -134, 2, -108, (150, 96, 50), w=2.5, r=4)
        c.rect(-34, -134, 2, -124, (130, 80, 40), w=2, r=3)
        c.circle(-16, -124, 3, (240, 210, 90), w=1)
        # neck and head
        hx, hy = 34 + head_dx, -222
        c.stroke([(26, -160), (36, -186), (30 + head_dx * 0.6, -206), (hx, hy)], STORK_W, 16)
        c.circle(hx, hy, 16, STORK_W, w=2.5)
    else:
        a = math.sin(flap)

        def wing(col, tipcol, dx):
            up = 120 * a
            A_, B_, C_ = (24 + dx, -8), (-6 + dx, -8 - up * 0.6), (-44 + dx, -6 - up * 1.1)
            D_, E_, F_ = (-92 + dx, -2 - up * 0.95), (-80 + dx, -4 - up * 0.45), (-44 + dx, -4)
            c.poly([A_, B_, C_, D_, E_, F_], col, w=2.5)
            # black flight feathers along the outer part
            c.poly([B_, C_, D_, E_, (-40 + dx, -6 - up * 0.5)], tipcol, w=2)
            sg = 1 if a >= 0 else -1
            for k in range(4):
                u = 0.15 + 0.25 * k
                fx, fy = lerp(C_[0], D_[0], u), lerp(C_[1], D_[1], u)
                c.line([(fx, fy), (fx - 8, fy - 12 * sg)], tipcol, 4)
        wing(mix(STORK_W, (170, 170, 185), 0.45), (30, 30, 38), 14)
        # legs trailing
        for k in (0, 5):
            c.line([(-40, 4 + k), (-120, 10 + k)], STORK_R, 4)
        c.poly([(-50, -6), (-82, -12), (-80, 6), (-48, 8)], STORK_B, w=2)
        c.ellipse(0, 0, 56, 22, STORK_W, w=3)
        # satchel
        c.rect(-14, 6, 18, 28, (150, 96, 50), w=2.5, r=4)
        c.line([(-10, 6), (24, -14)], (110, 70, 40), 3)
        wing(STORK_W, STORK_B, 0)
        hx, hy = 82, -14
        c.stroke([(40, -6), (62, -12), (hx, hy)], STORK_W, 15)
        c.circle(hx, hy, 15, STORK_W, w=2.5)
    # beak (open with mouth)
    bx, by = hx + 10, hy + 2
    tip = (hx + 66, hy + 10 + 8 * mouth)
    c.poly([(bx, by - 6), (hx + 66, hy + 6 - 4 * mouth), (bx, by + 2)], STORK_R, w=2)
    c.poly([(bx, by + 2), tip, (bx, by + 7)], mix(STORK_R, (0, 0, 0), 0.12), w=2)
    # eye
    if eyes == "closed":
        c.arc(hx + 3, hy - 4, 5, 3.5, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(hx + 3, hy - 1, 5, 5, 200, 340, OUT, 2.5)
    else:
        c.circle(hx + 3, hy - 4, 5, (255, 255, 255), w=1.5)
        c.circle(hx + 4, hy - 4, 2.6, (20, 20, 25), ol=None)
    # mailman cap
    c.poly([(hx - 16, hy - 8), (hx - 14, hy - 26), (hx + 10, hy - 28), (hx + 14, hy - 10)], POST, w=2)
    c.poly([(hx + 6, hy - 12), (hx + 26, hy - 10), (hx + 14, hy - 6)], (30, 40, 60), w=1.5)
    c.rect(hx - 6, hy - 22, hx + 4, hy - 16, (240, 200, 70), ol=None)
    if hold == "letter":
        lx, ly = hx + 56, hy + 10
        c.rect(lx - 4, ly - 2, lx + 40, ly + 26, (255, 252, 240), w=2)
        c.line([(lx - 4, ly - 2), (lx + 18, ly + 12), (lx + 40, ly - 2)], (180, 170, 150), 1.5, cap=False)
        c.rect(lx + 28, ly + 1, lx + 37, ly + 10, (230, 80, 70), ol=None)
    ox, oy, sx, sy = c.tf[-1]
    out = (ox + sx * tip[0], oy + sy * tip[1])
    c.pop()
    return out


def stork_basket(c, x, y, s=1.0, part="front", blanket=False):
    """Wicker basket hung from Joost's beak; (x, y) = middle of the rim. Draw 'back', cats, then 'front'."""
    c.push(x, y, s)
    if part == "back":
        c.ellipse(0, 0, 92, 16, (120, 80, 44), w=2.5)
        c.arc(0, -10, 70, 60, 180, 360, (150, 100, 56), 6)
    else:
        if blanket:
            c.ellipse(0, 4, 84, 16, (220, 80, 80), w=2)
            for k in range(-3, 4):
                c.circle(k * 22, 4, 4, (255, 240, 230), ol=None)
        c.poly([(-92, 0), (92, 0), (74, 74), (-74, 74)], (200, 150, 86), w=3)
        for k in range(1, 4):
            c.line([(-92 + 4.5 * k * 1.0 + 0, k * 18), (92 - 4.5 * k, k * 18)], (160, 110, 60), 2, cap=False)
        for k in range(-4, 5):
            c.line([(k * 20, 2), (k * 16, 72)], (170, 120, 66), 1.5, cap=False)
        c.ellipse(0, 0, 92, 10, (220, 170, 100), w=2.5)
        c.rect(-36, 24, 36, 50, (255, 250, 236), w=2, r=3)
        c.text(0, 37, "POST", 15 * c.scale, POST)
    c.pop()


# ------------------------------------------------------------------- Mies

MIES_W = (252, 250, 246)
MIES_B = (50, 46, 54)


def mies(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", wave=0.0, seed=7.0, look=(0, 0)):
    """Mies, a jolly cow in a Dutch lace cap and a blue apron. Upper body only: (x, y) = waist."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    # body
    c.ellipse(0, -60, 62, 74, MIES_W, w=3)
    c.ellipse(-30, -86, 22, 18, MIES_B, ol=None)
    c.ellipse(36, -40, 16, 20, MIES_B, ol=None)
    c.poly([(-40, -100), (40, -100), (54, 10), (-54, 10)], (60, 100, 180), w=2.5)     # apron
    c.rect(-40, -104, 40, -96, (250, 250, 250), w=1.5)
    for k in range(4):
        c.circle(-24 + 16 * k, -50, 3, (255, 255, 255), ol=None)
    # arms
    if wave > 0:
        wv = math.sin(t * 10) * 10
        c.stroke([(44, -100), (70 + wv * 0.3, -150 * wave - 20 * (1 - wave) + wv * 0.4)], MIES_W, 18)
        c.ellipse(72 + wv * 0.3, -156 * wave - 20 * (1 - wave) + wv * 0.4, 10, 9, (60, 60, 60))
    else:
        c.stroke([(44, -96), (62, -40)], MIES_W, 18)
        c.ellipse(62, -36, 10, 9, (60, 60, 60))
    c.stroke([(-44, -96), (-60, -40)], MIES_W, 18)
    # head
    hx, hy = 8, -150
    for side in (-1, 1):
        c.ellipse(hx + side * 54, hy - 18, 20, 9, MIES_W, w=2.5)
        c.ellipse(hx + side * 56, hy - 18, 12, 5, (250, 180, 190), ol=None)
        c.poly([(hx + side * 26, hy - 40), (hx + side * 36, hy - 66), (hx + side * 40, hy - 62),
                (hx + side * 36, hy - 38)], (240, 230, 200), w=2)
    c.ellipse(hx, hy, 46, 44, MIES_W, w=3)
    c.ellipse(hx - 20, hy - 18, 14, 16, MIES_B, ol=None)
    c.ellipse(hx + 2, hy + 24, 34, 22, (250, 186, 190), w=2.5)
    c.ellipse(hx - 10, hy + 22, 5, 7, (180, 100, 110), ol=None)
    c.ellipse(hx + 14, hy + 22, 5, 7, (180, 100, 110), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 2, hy + 38, 12, 3 + 6 * mouth, D.MOUTH, w=2)
    else:
        c.arc(hx + 2, hy + 34, 12, 6, 20, 160, OUT, 2)
    for ex in (hx - 16, hx + 20):
        if eyes == "closed":
            c.arc(ex, hy - 6, 7, 5, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, hy - 3, 7, 7, 200, 340, OUT, 3)
        else:
            c.ellipse(ex, hy - 6, 8, 10, (255, 255, 255), w=2)
            c.circle(ex + 1.5 + look[0] * 2, hy - 5 + look[1] * 2, 4.5, (40, 30, 30), ol=None)
            c.circle(ex + 3, hy - 8, 1.6, (255, 255, 255), ol=None)
    # Volendam lace cap with pointed wings
    c.poly([(hx - 40, hy - 26), (hx - 30, hy - 52), (hx, hy - 60), (hx + 30, hy - 52), (hx + 40, hy - 26),
            (hx + 22, hy - 38), (hx - 22, hy - 38)], (255, 255, 255), w=2.5)
    for side in (-1, 1):
        c.poly([(hx + side * 36, hy - 34), (hx + side * 70, hy - 66), (hx + side * 64, hy - 30)],
               (255, 255, 255), w=2)
    for k in range(5):
        c.circle(hx - 20 + 10 * k, hy - 46, 2.2, (200, 205, 220), ol=None)
    c.pop()


# ------------------------------------------------------------------ letter

def letter_img(w=440, h=300):
    c = Canvas(bg=(255, 250, 236), size=(w, h))
    c.rect(6, 6, w - 6, h - 6, None, ol=(220, 190, 150), w=2)
    # a little drawing: canal house, houseboat, tulips, bicycle
    c.rect(20, 20, 200, 200, (180, 220, 245), ol=None)
    c.push(0, 0, 1.0)
    rng = np.random.default_rng(3)
    canal_house(c, 30, 160, 60, 100, (160, 52, 52), rng, "step")
    canal_house(c, 90, 160, 54, 120, (56, 84, 74), rng, "bell")
    canal_house(c, 144, 160, 52, 92, (204, 150, 82), rng, "neck")
    c.pop()
    c.rect(20, 160, 200, 200, (70, 120, 150), ol=None)
    houseboat(c, 110, 194, 0.26, bike=False)
    c.rect(20, 20, 200, 200, None, w=2)
    _text(c, 320, 48, "Dear Luna,", 22, (60, 50, 70))
    lines = ["Come to the", "TULIP PARADE!", "Bikes and flowers", "everywhere!"]
    for k, ln in enumerate(lines):
        _text(c, 320, 88 + k * 30, ln, 19 if k != 1 else 22, (200, 70, 60) if k == 1 else (60, 50, 70))
    _text(c, 330, 220, "Love, Bram", 20, (60, 50, 70))
    for k in range(6):
        tulip(c, 34 + k * 30, 270, TULIP_COLS[k], 0.9)
    bicycle(c, 380, 284, 0.42, 1, 0.3, col=(200, 60, 60))
    return c.img
