"""London props and new characters, drawn with draw.Canvas primitives.

Landmarks (Big Ben, the Palace of Westminster, the London Eye, Tower Bridge,
St Paul's), a red open-top double-decker, a phone box, a sentry box, the Royal
Air Mail balloon, fish and chips and a tea set -- and the locals: Ruby (a
robin postbird), Biscuit (a corgi King's Guard) and Gus (a seagull) with his
three chicks.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import OUT, W, H, SS, mix, clamp, lerp, ease

STONE = (222, 198, 146)
STONE_D = (186, 160, 112)
SLATE = (74, 86, 100)
GOLD = (236, 196, 84)
RED = (214, 40, 46)
RED_D = (160, 26, 34)
CREAM = (250, 244, 222)


# ------------------------------------------------------------------ helpers

def _rot(px, py, a):
    ca, sa = math.cos(a), math.sin(a)
    return px * ca - py * sa, px * sa + py * ca


def rain(c, t, n=160, seed=3, speed=900.0, slant=0.18, col=(200, 215, 240), alpha=1.0, x0=0, y0=0, w=W, h=H):
    """Slanted rain streaks over a rectangle."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, w + 200, n)
    ph = rng.uniform(0, 1, n)
    ln = rng.uniform(14, 30, n)
    sp = rng.uniform(0.8, 1.2, n)
    for k in range(n):
        y = ((t * speed * sp[k] / h + ph[k]) % 1.0) * (h + 60) - 30
        x = (xs[k] - y * slant) % (w + 200) - 100
        c.line([(x0 + x, y0 + y), (x0 + x - ln[k] * slant, y0 + y - ln[k])], col, 1.6, cap=False)


def splashes(c, t, y0, y1, n=24, seed=5, col=(210, 225, 245)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = rng.uniform(0, W), rng.uniform(y0, y1)
        u = (t * 2.2 + rng.uniform(0, 1)) % 1.0
        if u < 0.5:
            r = 3 + 14 * u
            c.ellipse(x, y, r, r * 0.3, None, ol=col, w=1.5)


def shade_bottom(c, tl, t, strength=0.5, top=560, _masks={}):
    """Darken the bottom of the frame softly while a subtitle shows."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    if q not in _masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _masks[q] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((16, 18, 34), (0, top * SS, W * SS, H * SS), _masks[q])


# ------------------------------------------------------------------ Big Ben

def clock_face(c, x, y, r, hours=4.0, minutes=0.0, lit=0.0, ol=OUT, w=2.5):
    """Big Ben's dial: gold frame, white face, Roman-ish ticks, black hands."""
    c.circle(x, y, r * 1.14, GOLD, ol=ol, w=w)
    c.circle(x, y, r * 1.02, mix(GOLD, (150, 110, 40), 0.35), ol=None)
    face = mix((246, 244, 232), (255, 236, 160), lit)
    c.circle(x, y, r, face, ol=ol, w=w * 0.8)
    for k in range(12):
        a = k * math.tau / 12
        ca, sa = math.sin(a), -math.cos(a)
        big = k % 3 == 0
        c.line([(x + ca * r * 0.72, y + sa * r * 0.72), (x + ca * r * (0.9 if big else 0.86), y + sa * r *
                                                                       (0.9 if big else 0.86))],
               (40, 36, 40), max(1.2, r * (0.07 if big else 0.04)), cap=False)
    c.circle(x, y, r * 0.62, None, ol=mix(face, (60, 50, 50), 0.25), w=max(1, r * 0.02))
    ha = (hours % 12 + minutes / 60) / 12 * math.tau
    ma = minutes / 60 * math.tau
    c.line([(x, y), (x + math.sin(ha) * r * 0.5, y - math.cos(ha) * r * 0.5)], (30, 28, 34), max(2, r * 0.08))
    c.line([(x, y), (x + math.sin(ma) * r * 0.82, y - math.cos(ma) * r * 0.82)], (30, 28, 34), max(1.5, r * 0.05))
    c.circle(x, y, max(2, r * 0.07), GOLD, ol=None)


def big_ben(c, x, base, h, hours=4.0, minutes=0.0, stone=STONE, shade=STONE_D, roof=SLATE, lit=0.0, w=2.0,
            detail=True):
    """The Elizabeth Tower. (x, base) = foot centre; h = height to the spire tip."""
    u = h / 100.0
    c.push(x, base)
    # shaft
    c.rect(-8 * u, -56 * u, 8 * u, 0, stone, w=w)
    c.rect(4 * u, -56 * u, 8 * u, 0, shade, ol=None)
    if detail:
        for dx in (-4.5, -1.5, 1.5):
            c.line([(dx * u, -54 * u), (dx * u, -3 * u)], shade, max(1, 0.6 * u), cap=False)
        for k in range(1, 9):
            yy = -k * 6 * u
            c.line([(-8 * u, yy), (8 * u, yy)], shade, max(1, 0.4 * u), cap=False)
    # clock stage
    c.rect(-10 * u, -76 * u, 10 * u, -56 * u, stone, w=w)
    c.rect(6 * u, -76 * u, 10 * u, -56 * u, shade, ol=None)
    for side in (-1, 1):
        c.poly([(side * 10 * u, -76 * u), (side * 10.8 * u, -80 * u), (side * 9.2 * u, -76 * u)], GOLD, w=w * 0.6)
    clock_face(c, 0, -66 * u, 7.2 * u, hours, minutes, lit, w=w * 0.9)
    # belfry with arches
    c.rect(-8.6 * u, -85 * u, 8.6 * u, -76 * u, stone, w=w)
    for dx in (-5.2, 0, 5.2):
        c.rect((dx - 1.5) * u, -83.5 * u, (dx + 1.5) * u, -77.5 * u, mix(roof, (20, 20, 30), 0.3), ol=None,
               r=1.4 * u)
    # spire roof
    c.poly([(-9.5 * u, -85 * u), (-4 * u, -95 * u), (4 * u, -95 * u), (9.5 * u, -85 * u)], roof, w=w)
    c.poly([(-4 * u, -95 * u), (0, -100 * u), (4 * u, -95 * u)], roof, w=w)
    c.line([(-5 * u, -90 * u), (5 * u, -90 * u)], GOLD, max(1, 0.7 * u), cap=False)
    c.line([(0, -100 * u), (0, -106 * u)], GOLD, max(1.5, 0.8 * u))
    for side in (-1, 1):
        c.poly([(side * 9.5 * u, -85 * u), (side * 8.6 * u, -91 * u), (side * 7.7 * u, -85 * u)], roof, w=w * 0.7)
    c.pop()


def parliament(c, x0, x1, base, h, stone=STONE, shade=STONE_D, roof=SLATE, rng_seed=2, win=None):
    """The long gothic Palace of Westminster with pinnacles and the Victoria Tower at x1."""
    rng = np.random.default_rng(rng_seed)
    c.rect(x0, base - h, x1 - 60, base, stone, w=2)
    c.rect(x0, base - h * 0.45, x1 - 60, base - h * 0.42, shade, ol=None)
    x = x0 + 8
    while x < x1 - 70:
        c.rect(x, base - h * 0.85, x + 5, base - h * 0.15, win or shade, ol=None)
        x += 13
    x = x0
    while x < x1 - 60:
        ph = h * rng.uniform(0.15, 0.3)
        c.rect(x, base - h - ph, x + 6, base - h, stone, ol=None)
        c.poly([(x - 1, base - h - ph), (x + 3, base - h - ph - 10), (x + 7, base - h - ph)], roof, ol=None)
        x += 26
    c.poly([(x0, base - h), (x0 + 20, base - h - 14), (x1 - 80, base - h - 14), (x1 - 60, base - h)], roof, w=2)
    # Victoria Tower: square and stout
    c.rect(x1 - 70, base - h * 2.3, x1, base, stone, w=2)
    c.rect(x1 - 20, base - h * 2.3, x1, base, shade, ol=None)
    for k in range(4):
        c.rect(x1 - 58 + k * 13, base - h * 2.1, x1 - 52 + k * 13, base - h * 0.6, shade, ol=None)
    for dx in (-72, -6):
        c.rect(x1 + dx, base - h * 2.5, x1 + dx + 8, base - h * 2.3, stone, w=1.5)
    c.line([(x1 - 35, base - h * 2.3), (x1 - 35, base - h * 2.75)], (60, 60, 70), 2)
    c.rect(x1 - 35, base - h * 2.75, x1 - 18, base - h * 2.65, (40, 80, 160), ol=None)


# ------------------------------------------------------------- London Eye

def london_eye(c, x, cy, r, t=0.0, spin=0.02, rim=(244, 246, 250), cap=(220, 236, 248), ol=OUT, legs=True, w=2.0):
    a0 = t * spin
    if legs:
        for dx in (-0.62, -0.45):
            c.line([(x, cy), (x + dx * r, cy + r * 1.12)], mix(rim, (120, 130, 150), 0.3), max(2, r * 0.035))
    for k in range(32):
        a = a0 + k * math.tau / 32
        c.line([(x, cy), (x + math.cos(a) * r, cy + math.sin(a) * r)], mix(rim, (150, 160, 180), 0.4),
               max(1, r * 0.006), cap=False)
    c.circle(x, cy, r, None, ol=ol, w=max(2.5, r * 0.03) + 2)
    c.circle(x, cy, r, None, ol=rim, w=max(2, r * 0.03))
    c.circle(x, cy, r * 0.93, None, ol=mix(rim, (150, 160, 180), 0.3), w=max(1, r * 0.01))
    for k in range(32):
        a = a0 + k * math.tau / 32
        px, py = x + math.cos(a) * r * 1.03, cy + math.sin(a) * r * 1.03
        c.ellipse(px, py, r * 0.035, r * 0.022, cap, ol=ol, w=1)
    c.circle(x, cy, r * 0.05, rim, ol=ol, w=1.5)


# ------------------------------------------------------------ Tower Bridge

BRIDGE_BLUE = (120, 170, 214)


def bridge_tower(c, x, base, s, stone=STONE, shade=STONE_D, roof=SLATE, w=2.0):
    """One gothic tower of Tower Bridge. (x, base) = foot centre at the road deck."""
    c.push(x, base, s)
    c.rect(-38, -250, 38, 40, stone, w=w)                   # body (down into the pier)
    c.rect(18, -250, 38, 40, shade, ol=None)
    c.rect(-38, -250, 38, 40, None, w=w)
    c.rect(-22, -40, 22, 0, mix(shade, (40, 40, 50), 0.4), w=w * 0.7, r=16)   # road arch
    for wy in (-200, -150, -100):
        c.rect(-12, wy, 12, wy + 30, mix(roof, (20, 20, 30), 0.2), w=w * 0.6, r=8)
    for side in (-1, 1):
        c.rect(side * 38 - 8, -300, side * 38 + 8, -230, stone, w=w)
        c.poly([(side * 38 - 9, -300), (side * 38, -326), (side * 38 + 9, -300)], roof, w=w)
        c.line([(side * 38, -326), (side * 38, -336)], GOLD, 2)
    c.poly([(-32, -250), (-20, -296), (20, -296), (32, -250)], roof, w=w)
    c.poly([(-10, -296), (0, -318), (10, -296)], roof, w=w)
    c.line([(0, -318), (0, -332)], GOLD, 2)
    c.pop()


def tower_bridge(c, x, base, s=1.0, open_=0.0, stone=STONE, shade=STONE_D, roof=SLATE, blue=BRIDGE_BLUE,
                 water=None, w=2.0, towers=True):
    """Tower Bridge. (x, base) = centre of the road deck. open_ 0..1 raises the bascules."""
    span = 175 * s
    # high walkways
    for dy in (-232, -212):
        c.rect(x - span, base + dy * s, x + span, base + (dy + 14) * s, blue, w=w)
    for k in range(12):
        xx = x - span + (k + 0.5) * span * 2 / 12
        c.line([(xx - 6 * s, base - 218 * s), (xx + 6 * s, base - 232 * s)], CREAM, 1.5, cap=False)
    # side suspension spans
    for side in (-1, 1):
        x0 = x + side * span
        x1 = x + side * (span + 330 * s)
        pts = [(lerp(x0, x1, q), base - (200 - 170 * math.sin(math.pi * q / 2) ** 0.7) * s) for q in np.linspace(0, 1, 12)]
        c.line(pts, OUT, 8 * s + 4)
        c.line(pts, blue, 8 * s)
        c.rect(min(x0, x1), base - 8 * s, max(x0, x1), base + 6 * s, mix(stone, (90, 90, 100), 0.35), w=w)
        for k in range(1, 8):
            xx = lerp(x0, x1, k / 8)
            yy = base - (200 - 170 * math.sin(math.pi * (k / 8) / 2) ** 0.7) * s
            c.line([(xx, yy), (xx, base - 8 * s)], blue, 2, cap=False)
    # bascules
    ang = open_ * math.radians(72)
    L = span - 38 * s
    for side in (-1, 1):
        px = x + side * (span - 38 * s)
        pts = []
        for qx, qy in ((0, -8 * s), (L, -8 * s), (L, 8 * s), (0, 8 * s)):
            rx, ry = _rot(-side * qx, qy, side * ang)
            pts.append((px + rx, base + ry))
        c.poly(pts, mix(stone, (90, 90, 100), 0.35), w=w)
        # railing on the bascule
        a, b = pts[0], pts[1]
        c.line([a, b], blue, 3 * s + 1, cap=False)
    if towers:
        for side in (-1, 1):
            bridge_tower(c, x + side * span, base, s, stone, shade, roof, w)
    # piers
    for side in (-1, 1):
        c.rect(x + side * span - 55 * s, base + 40 * s, x + side * span + 55 * s, base + 70 * s,
               mix(stone, (80, 80, 90), 0.3), w=w)


# -------------------------------------------------------------- St Paul's

def st_pauls(c, x, base, s=1.0, col=(214, 206, 190), shade=(180, 172, 160), dome=(150, 165, 170), ol=OUT):
    c.push(x, base, s)
    c.rect(-90, -70, 90, 0, col, ol=ol)
    c.rect(-40, -100, 40, -70, col, ol=ol)
    for k in range(-3, 4):
        c.rect(k * 11 - 3, -96, k * 11 + 3, -72, shade, ol=None)
    c.ellipse(0, -100, 48, 52, dome, ol=ol)
    c.rect(-50, -104, 50, -96, col, ol=ol)
    c.rect(-8, -170, 8, -146, col, ol=ol)
    c.ellipse(0, -172, 8, 8, dome, ol=ol)
    c.line([(0, -180), (0, -196)], GOLD, 3)
    c.circle(0, -198, 4, GOLD, ol=None)
    for side in (-1, 1):
        c.rect(side * 78 - 12, -120, side * 78 + 12, -70, col, ol=ol)
        c.poly([(side * 78 - 12, -120), (side * 78, -140), (side * 78 + 12, -120)], dome, ol=ol)
    c.pop()


# -------------------------------------------------------------- street

def phone_box(c, x, y, s=1.0, part="all", lit=0.0):
    """Red K6 telephone box. part: 'back' (dark inside), 'front' (frame + glazing bars), 'all'."""
    c.push(x, y, s)
    if part in ("back", "all"):
        c.rect(-40, -200, 40, 0, RED, w=2.5, r=4)
        c.rect(-30, -160, 30, -14, mix((50, 60, 70), (255, 230, 150), lit), w=2)
    if part in ("front", "all"):
        if part == "front":
            # frame around the window so cats appear inside
            c.rect(-40, -200, 40, -160, RED, w=2.5, r=4)
            c.rect(-40, -160, -30, 0, RED, ol=None)
            c.rect(30, -160, 40, 0, RED, ol=None)
            c.rect(-40, -14, 40, 0, RED, ol=None)
            c.rect(-40, -200, 40, 0, None, w=2.5, r=4)
            c.rect(-30, -160, 30, -14, None, w=2)
        for k in range(1, 3):
            c.line([(-30 + 20 * k, -160), (-30 + 20 * k, -14)], RED, 3, cap=False)
        for k in range(1, 8):
            c.line([(-30, -160 + k * 18.3), (30, -160 + k * 18.3)], RED, 3, cap=False)
        c.rect(-34, -186, 34, -172, (250, 250, 245), w=1.5)
        c.text(0, -179, "TELEPHONE", 9, (30, 30, 30))
        c.poly([(-42, -200), (0, -214), (42, -200)], RED, w=2.5)
        c.circle(0, -206, 5, GOLD, w=1.5)
    c.pop()


def sentry_box(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-56, -250, 56, 0, (236, 230, 214), w=2.5)
    c.rect(-42, -220, 42, 0, (60, 52, 50), w=2)
    c.poly([(-64, -250), (0, -300), (64, -250)], (236, 230, 214), w=2.5)
    c.poly([(-48, -256), (0, -290), (48, -256)], (60, 80, 140), ol=None)
    c.circle(0, -268, 8, GOLD, w=1.5)
    c.pop()


def railings(c, x0, x1, y, h=90, col=(30, 32, 40), gold=GOLD, step=14):
    c.rect(x0, y - h, x1, y - h + 6, col, ol=None)
    c.rect(x0, y - 14, x1, y - 8, col, ol=None)
    x = x0
    while x <= x1:
        c.line([(x, y), (x, y - h - 8)], col, 3, cap=False)
        c.poly([(x - 4, y - h - 6), (x, y - h - 16), (x + 4, y - h - 6)], gold, ol=None)
        x += step


def lamp_post(c, x, y, s=1.0, lit=0.0, col=(40, 46, 56)):
    c.push(x, y, s)
    c.rect(-6, -190, 6, 0, col, w=2)
    c.rect(-12, -14, 12, 0, col, w=2)
    for side in (-1, 1):
        c.line([(0, -190), (side * 22, -200), (side * 28, -186)], col, 4)
        c.rect(side * 28 - 9, -200, side * 28 + 9, -172, mix((255, 240, 190), (255, 210, 120), lit), w=2, r=3)
    c.circle(0, -198, 6, GOLD, w=1.5)
    c.pop()


def plane_tree(c, x, y, s=1.0, leaf=(104, 160, 92), trunk=(150, 132, 104)):
    c.push(x, y, s)
    c.rect(-10, -150, 10, 0, trunk, w=2, r=4)
    for dx, dy, r in ((-50, -170, 48), (45, -175, 50), (0, -215, 58), (-10, -150, 44), (30, -140, 40)):
        c.circle(dx, dy, r, leaf)
    for dx, dy, r in ((-50, -170, 43), (45, -175, 45), (0, -215, 53), (-10, -150, 39), (30, -140, 35)):
        c.circle(dx, dy, r, leaf, ol=None)
    c.pop()


def townhouse_row(c, x0, x1, base, rng, h=(200, 260), night=0.0):
    """Georgian brick / stucco terraced houses with sash windows and coloured doors."""
    walls = [(196, 120, 92), (236, 228, 210), (178, 106, 82), (220, 208, 186), (206, 140, 104)]
    doors = [(30, 40, 60), (180, 40, 50), (40, 100, 70), (40, 70, 140), (230, 190, 60)]
    x = x0
    while x < x1:
        w = rng.uniform(120, 160)
        hh = rng.uniform(*h)
        wall = walls[rng.integers(len(walls))]
        c.rect(x, base - hh, x + w, base, wall, w=2)
        c.rect(x - 2, base - hh - 10, x + w + 2, base - hh, mix(wall, (255, 255, 255), 0.3), w=2)
        for k in range(rng.integers(2, 4)):
            cx = x + 16 + k * 22
            c.rect(cx, base - hh - 26, cx + 12, base - hh - 10, (150, 90, 70), w=1.5)
        for fy in np.arange(base - hh + 20, base - 70, 54):
            for fx in (x + 18, x + w / 2 - 12, x + w - 42):
                c.rect(fx, fy, fx + 24, fy + 34, mix((70, 90, 120), (255, 214, 130), night), w=1.5)
                c.line([(fx, fy + 17), (fx + 24, fy + 17)], (240, 240, 240), 1.5, cap=False)
        dx = x + w / 2 - 14
        c.rect(dx, base - 56, dx + 28, base, doors[rng.integers(len(doors))], w=2, r=10)
        c.circle(dx + 20, base - 28, 2.5, GOLD, ol=None)
        x += w


def shop_row(c, x0, x1, base, rng, h=(170, 220)):
    """London high street: shops with awnings and signs on the ground floor."""
    walls = [(226, 214, 190), (196, 120, 92), (238, 232, 222), (170, 186, 196), (214, 176, 140)]
    awn = [(40, 110, 70), (180, 40, 50), (40, 70, 140), (230, 170, 50), (120, 60, 130)]
    signs = ["TEA", "BOOKS", "SWEETS", "HATS", "PIES", "TOYS", "CAKES", "UMBRELLAS"]
    x = x0
    k = 0
    while x < x1:
        w = rng.uniform(150, 200)
        hh = rng.uniform(*h) + 80
        wall = walls[rng.integers(len(walls))]
        a = awn[rng.integers(len(awn))]
        c.rect(x, base - hh, x + w, base, wall, w=2)
        for fy in np.arange(base - hh + 18, base - 120, 50):
            for fx in np.arange(x + 16, x + w - 30, 42):
                c.rect(fx, fy, fx + 22, fy + 32, (70, 90, 120), w=1.5)
        c.rect(x + 6, base - 104, x + w - 6, base - 82, mix(a, (20, 20, 20), 0.3), w=1.5)
        c.text(x + w / 2, base - 93, signs[k % len(signs)], 12, CREAM)
        c.rect(x + 12, base - 76, x + w - 12, base - 6, (150, 190, 210), w=2)
        n = int((w - 12) // 22)
        for q in range(n):
            c.poly([(x + 6 + q * (w - 12) / n, base - 82), (x + 6 + (q + 1) * (w - 12) / n, base - 82),
                    (x + 6 + (q + 1) * (w - 12) / n, base - 66), (x + 6 + q * (w - 12) / n, base - 66)],
                   a if q % 2 == 0 else CREAM, ol=None)
        c.line([(x + 6, base - 66), (x + w - 6, base - 66)], OUT, 2, cap=False)
        x += w
        k += 1


# ------------------------------------------------------------------- bus

def bus(c, x, y, s=1.0, face=1, wheel=0.0, part="all", sign="LONDON"):
    """Open-top red double-decker. (x, y) = road under the middle; the top deck floor is y - 170*s.
    part: 'back' (body), 'front' (top-deck front railing), 'all'."""
    c.push(x, y, s, flip=face < 0)
    if part in ("back", "all"):
        # body
        c.rect(-230, -170, 230, -24, RED, w=2.5, r=14)
        c.rect(-230, -100, 230, -94, CREAM, ol=None)
        c.rect(-230, -170, 230, -24, None, w=2.5, r=14)
        # lower deck windows
        for k in range(6):
            wx = -210 + k * 62
            c.rect(wx, -150, wx + 50, -108, (150, 196, 220), w=2, r=5)
            c.line([(wx + 8, -144), (wx + 20, -116)], (220, 240, 250), 3, cap=False)
        # driver cab + door
        c.rect(178, -150, 222, -40, (150, 196, 220), w=2, r=6)
        c.rect(-196, -90, -160, -30, (60, 50, 50), w=2)
        c.text(30, -62, sign, 22, GOLD, stroke=1.5)
        c.rect(150, -92, 212, -74, (30, 30, 30), w=1.5)
        c.text(181, -83, "11", 12, (255, 220, 90))
        c.circle(222, -40, 6, (255, 240, 170), w=1.5)
        # wheels
        for wx in (-140, 150):
            c.circle(wx, -24, 26, (40, 40, 46), w=2.5)
            c.circle(wx, -24, 12, (180, 180, 190), w=2)
            for k in range(4):
                a = wheel + k * math.pi / 2
                c.line([(wx, -24), (wx + math.cos(a) * 11, -24 + math.sin(a) * 11)], (90, 90, 100), 2, cap=False)
        # top deck: back panel of the railing
        c.rect(-230, -206, 230, -170, mix(RED, (0, 0, 0), 0.2), w=2.5, r=8)
        for k in range(5):
            sx = -190 + k * 90
            c.rect(sx, -214, sx + 56, -190, (40, 46, 70), w=2, r=8)
    if part in ("front", "all"):
        c.rect(-232, -200, 232, -170, RED, w=2.5, r=6)
        c.line([(-232, -206), (232, -206)], (230, 230, 236), 4, cap=False)
        for k in range(16):
            px = -224 + k * 30
            c.line([(px, -206), (px, -200)], (230, 230, 236), 3, cap=False)
    c.pop()


# --------------------------------------------------------------- balloon

def balloon(c, x, y, s=1.0, t=0.0, part="all", flame=0.0, sway=0.0):
    """Royal Air Mail balloon. (x, y) = bottom of the basket. part: 'back' | 'front' | 'all'.
    The basket rim is at y - 70*s; the envelope's top at about y - 470*s."""
    c.push(x, y, s)
    if part in ("back", "all"):
        ex, cy = sway * 10, ENV_CY
        # ropes
        for dx, ex2 in ((-78, -0.95), (-34, -0.4), (34, 0.4), (78, 0.95)):
            c.line([(dx, -72), (ex + ex2 * 40, ENV_SKIRT)], (120, 90, 60), 2, cap=False)
        # envelope: striped gores
        cols = [RED, CREAM, (40, 70, 150), CREAM]
        n = 10
        vs = np.linspace(0, 1, 18)
        for k in range(n):
            u0, u1 = k / n, (k + 1) / n
            pts = [_env_pt(u0, v, ex, cy) for v in vs] + [_env_pt(u1, v, ex, cy) for v in vs[::-1]]
            c.poly(pts, cols[k % 4], ol=None)
        outline = [_env_pt(0, v, ex, cy) for v in vs] + [_env_pt(1, v, ex, cy) for v in vs[::-1]]
        c.poly(outline, None, w=3)
        c.ellipse(ex - 60, cy - 70, 26, 44, mix(CREAM, (255, 255, 255), 0.6), ol=None)
        # band with lettering
        c.rect(ex - 146, cy - 2, ex + 146, cy + 34, GOLD, w=2, r=6)
        c.text(ex, cy + 16, "ROYAL AIR MAIL", 21, RED_D)
        # skirt + burner
        c.rect(ex - 30, ENV_SKIRT - 4, ex + 30, ENV_SKIRT + 10, (90, 90, 100), w=2)
        if flame > 0.02:
            fl = flame * (0.85 + 0.15 * math.sin(t * 40))
            c.poly([(ex - 14, ENV_SKIRT + 4), (ex, ENV_SKIRT + 4 - 80 * fl), (ex + 14, ENV_SKIRT + 4)],
                   (255, 170, 60), ol=None)
            c.poly([(ex - 7, ENV_SKIRT + 4), (ex, ENV_SKIRT + 4 - 46 * fl), (ex + 7, ENV_SKIRT + 4)],
                   (255, 240, 160), ol=None)
        # basket back rim
        c.rect(-82, -76, 82, -66, (170, 120, 70), w=2, r=4)
    if part in ("front", "all"):
        basket_col = (196, 146, 86)
        c.poly([(-80, -70), (80, -70), (72, 0), (-72, 0)], basket_col, w=2.5)
        for k in range(1, 4):
            yy = -70 + k * 17.5
            c.line([(-80 + k * 2, yy), (80 - k * 2, yy)], mix(basket_col, (100, 60, 30), 0.4), 2, cap=False)
        for k in range(-3, 4):
            c.line([(k * 22, -70), (k * 20, 0)], mix(basket_col, (100, 60, 30), 0.3), 1.5, cap=False)
        c.rect(-86, -76, 86, -66, (150, 100, 56), w=2.5, r=4)
        # little mail badge
        c.rect(-26, -54, 26, -24, RED, w=2, r=4)
        c.text(0, -39, "MAIL", 11, CREAM)
    c.pop()


ENV_CY, ENV_R, ENV_SKIRT = -390, 150, -236


def _env_pt(u, v, ex, cy):
    """Point on the balloon envelope: u across 0..1, v down 0..1 (crown to skirt)."""
    if v < 0.7:
        th = v / 0.7 * math.pi * 0.62
        y, hw = cy - ENV_R * math.cos(th), ENV_R * math.sin(th)
    else:
        q = (v - 0.7) / 0.3
        y0, hw0 = cy - ENV_R * math.cos(math.pi * 0.62), ENV_R * math.sin(math.pi * 0.62)
        y, hw = lerp(y0, ENV_SKIRT, q), lerp(hw0, 30, q ** 0.8)
    return ex - hw * math.cos(math.pi * u), y


def mail_sack(c, x, y, s=1.0, wiggle=0.0):
    c.push(x, y, s)
    c.poly([(-24, 0), (-28 + wiggle * 3, -40), (-10, -52), (12, -52), (26 - wiggle * 3, -40), (24, 0)],
           (214, 196, 160), w=2)
    c.line([(-12, -46), (12, -46)], (120, 90, 60), 3)
    c.text(0, -22, "POST", 9, RED_D)
    c.pop()


# ------------------------------------------------------------------ radio

def radio(c, x, y, s=1.0, glow=0.0, t=0.0):
    c.push(x, y, s)
    wood, dark = (160, 100, 56), (120, 72, 40)
    c.poly([(-60, 0), (-60, -80)] + [(-60 * math.cos(a), -80 - 50 * math.sin(a)) for a in np.linspace(0, math.pi, 14)] +
           [(60, -80), (60, 0)], wood, w=2.5)
    c.poly([(-44, -12), (-44, -78)] + [(-44 * math.cos(a), -78 - 36 * math.sin(a)) for a in np.linspace(0, math.pi, 12)] +
           [(44, -78), (44, -12)], (220, 196, 150), w=2)
    for k in range(-3, 4):
        c.line([(k * 11, -100 + abs(k) * 2), (k * 11, -50)], dark, 2, cap=False)
    c.rect(-38, -44, 38, -24, mix((240, 220, 160), (255, 220, 120), glow), w=1.5, r=4)
    c.line([(-14 + 8 * math.sin(t * 0.3), -42), (-14 + 8 * math.sin(t * 0.3), -26)], RED, 2, cap=False)
    for kx in (-28, 28):
        c.circle(kx, -18 + 4, 6, dark, w=1.5)
    if glow > 0.05:
        for k in range(3):
            u = (t * 0.9 + k / 3) % 1.0
            c.arc(70, -90, 14 + 30 * u, 14 + 30 * u, -40, 40, mix((80, 60, 50), (250, 228, 190), u), 3)
    c.pop()


def side_table(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-70, -100, 70, -88, (150, 96, 60), w=2, r=3)
    for dx in (-56, 50):
        c.rect(dx, -88, dx + 8, 0, (130, 82, 50), w=2)
    c.pop()


# ------------------------------------------------------------------- food

def chips_cone(c, x, y, s=1.0, chips=8, fish=True):
    """A paper cone of fish and chips. (x, y) = bottom tip."""
    c.push(x, y, s)
    rng = np.random.default_rng(4)
    for k in range(chips):
        cx = rng.uniform(-22, 22)
        a = rng.uniform(-0.5, 0.5)
        dx, dy = math.sin(a) * 22, -math.cos(a) * 22
        c.stroke([(cx, -52), (cx + dx, -52 + dy)], (246, 206, 110), 6)
    if fish:
        c.ellipse(10, -72, 26, 12, (214, 150, 60))
        c.poly([(30, -72), (44, -84), (42, -60)], (214, 150, 60))
        for k in range(3):
            c.arc(4 + k * 9, -72, 4, 8, 280, 80, (180, 120, 40), 1.5)
    c.poly([(-34, -58), (34, -58), (0, 0)], (246, 244, 236), w=2)
    c.poly([(-34, -58), (34, -58), (20, -36), (-20, -36)], (236, 232, 222), ol=None)
    c.line([(-24, -46), (24, -46)], (170, 190, 220), 3, cap=False)
    c.pop()


def fried_fish(c, x, y, s=1.0, ang=0.0):
    c.push(x, y, s)
    pts = [_rot(px, py, ang) for px, py in ((-26, 0), (-14, -12), (12, -12), (24, 0), (12, 12), (-14, 12))]
    c.poly(pts, (214, 150, 60), w=2)
    tail = [_rot(px, py, ang) for px, py in ((22, 0), (38, -12), (36, 12))]
    c.poly(tail, (214, 150, 60), w=2)
    c.pop()


def chip(c, x, y, s=1.0, ang=0.3):
    dx, dy = math.cos(ang) * 11 * s, math.sin(ang) * 11 * s
    c.stroke([(x - dx, y - dy), (x + dx, y + dy)], (246, 206, 110), 6 * s)


def kiosk(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-110, -170, 110, 0, (40, 90, 140), w=2.5)
    c.rect(-96, -120, 96, -60, (255, 236, 190), w=2)
    c.rect(-110, -60, 110, -50, (230, 230, 236), w=2)
    c.rect(-120, -200, 120, -170, CREAM, w=2.5, r=4)
    c.text(0, -185, "FISH & CHIPS", 20, RED_D)
    for k in range(6):
        c.poly([(-120 + k * 40, -170), (-80 + k * 40, -170), (-80 + k * 40, -150), (-120 + k * 40, -150)],
               RED if k % 2 == 0 else CREAM, w=1.5)
    # a fryer and a row of wrapped cones
    for k in range(4):
        chips_cone(c, -60 + k * 40, -62, 0.45, chips=5, fish=k % 2 == 0)
    c.pop()


def teapot(c, x, y, s=1.0, col=(240, 244, 250), trim=(60, 100, 180)):
    c.push(x, y, s)
    c.stroke([(26, -30), (44, -44), (52, -54)], col, 7)
    c.arc(-30, -28, 12, 14, 90, 270, OUT, 7)
    c.arc(-30, -28, 12, 14, 90, 270, col, 4)
    c.ellipse(0, -26, 30, 26, col)
    c.line([(-28, -26), (28, -26)], trim, 3, cap=False)
    c.ellipse(0, -50, 14, 5, col)
    c.circle(0, -56, 4, trim)
    c.pop()


def teacup(c, x, y, s=1.0, col=(240, 244, 250), trim=(60, 100, 180), steam=0.0, t=0.0):
    c.push(x, y, s)
    c.ellipse(0, 0, 18, 4, col, w=1.5)
    c.arc(13, -10, 6, 6, 270, 90, OUT, 3)
    c.poly([(-12, -18), (12, -18), (8, -2), (-8, -2)], col, w=1.5)
    c.ellipse(0, -18, 12, 3, (170, 110, 60), w=1.5)
    c.line([(-11, -12), (11, -12)], trim, 2, cap=False)
    if steam > 0:
        for k in range(2):
            u = (t * 0.6 + k * 0.5) % 1.0
            c.line([(k * 6 - 3 + math.sin(t * 3 + k) * 3, -24 - 30 * u), (k * 6 - 3, -24 - 30 * u - 8)],
                   mix((255, 255, 255), (200, 200, 210), u), 2)
    c.pop()


def scone(c, x, y, s=1.0, jam=True):
    c.push(x, y, s)
    c.ellipse(0, -8, 16, 10, (230, 186, 120))
    c.ellipse(0, -14, 13, 4, (250, 246, 232), ol=None)
    if jam:
        c.ellipse(0, -17, 9, 3, (200, 30, 60), ol=None)
    c.pop()


def cake_stand(c, x, y, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, -110)], GOLD, 4)
    c.circle(0, -116, 6, GOLD, w=1.5)
    for k, (yy, r) in enumerate(((-6, 46), (-46, 36), (-84, 26))):
        c.ellipse(0, yy, r, 6, (246, 248, 252), w=1.5)
        if k == 0:
            for dx in (-24, 0, 24):
                scone(c, dx, yy - 2, 0.75)
        elif k == 1:
            for dx, col in ((-18, (250, 190, 210)), (0, (200, 230, 160)), (18, (250, 220, 140))):
                c.rect(dx - 8, yy - 14, dx + 8, yy - 2, col, w=1.5, r=2)
        else:
            for dx in (-10, 10):
                c.ellipse(dx, yy - 6, 7, 6, (250, 170, 180), w=1.5)
                c.circle(dx, yy - 13, 2.5, (220, 30, 40), ol=None)
    c.pop()


# =============================================================== characters

def robin(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", fly=0.0, hop=0.0, cap=True, bag=True,
          seed=3.3, wave=0.0):
    """Ruby the robin postbird. (x, y) = feet. About 70 tall at s=1."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    brown, breast, belly = (150, 104, 70), (236, 104, 50), (246, 232, 214)
    c.push(x, y - hop, s, flip=face < 0)
    if fly <= 0:
        for fx in (-6, 6):
            c.line([(fx, -14), (fx, 0)], (110, 70, 50), 2.5, cap=False)
            c.line([(fx, 0), (fx + 6, 0)], (110, 70, 50), 2, cap=False)
    # tail
    c.poly([(-22, -30), (-44, -42), (-40, -30), (-20, -22)], mix(brown, (0, 0, 0), 0.15))
    # body
    c.ellipse(0, -34, 26, 24, brown)
    c.ellipse(8, -32, 17, 18, breast, ol=None)
    c.ellipse(4, -16, 14, 7, belly, ol=None)
    # wing
    if fly > 0:
        flap = math.sin(t * 22) * 0.9
        tip = (-14 - 10 * math.cos(flap), -48 - 34 * math.sin(flap))
        c.poly([(-12, -40), tip, (6, -42)], mix(brown, (0, 0, 0), 0.12))
    else:
        lift = wave * (0.5 + 0.5 * math.sin(t * 12))
        c.poly([(-16, -40), (8, -42 - 14 * lift), (4, -28 + 4 * lift), (-18, -26)], mix(brown, (0, 0, 0), 0.12))
    # head (same circle, top)
    c.circle(14, -52, 16, brown)
    c.ellipse(20, -46, 11, 9, breast, ol=None)
    # beak
    if mouth > 0.05:
        c.poly([(28, -54), (40, -53), (29, -50)], (60, 50, 40), w=1.5)
        c.poly([(28, -49), (38, -45 + 4 * mouth), (28, -46 + 2 * mouth)], (60, 50, 40), w=1.5)
    else:
        c.poly([(28, -54), (40, -51), (28, -47)], (60, 50, 40), w=1.5)
    # eye
    if eyes == "closed":
        c.arc(20, -56, 4, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(20, -54, 4, 4, 200, 340, OUT, 2)
    else:
        c.circle(20, -56, 4.2, (20, 18, 22), ol=None)
        c.circle(21.5, -57.5, 1.4, (255, 255, 255), ol=None)
    if cap:
        c.poly([(2, -64), (4, -74), (24, -74), (26, -64)], (40, 70, 150), w=1.5)
        c.rect(0, -66, 30, -62, (30, 40, 90), w=1.5)
        c.circle(14, -70, 2.5, GOLD, ol=None)
    if bag and fly <= 0:
        c.line([(16, -60), (-10, -24)], (110, 70, 40), 2, cap=False)
        c.rect(-20, -28, 0, -14, (200, 50, 50), w=1.5, r=2)
    c.pop()


def gull(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", fly=0.0, walk=0.0, fish=False, chip=False,
         seed=5.1, sad=0.0):
    """Gus the seagull. (x, y) = feet. About 95 tall at s=1."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    white, grey, dgrey = (248, 248, 250), (170, 180, 192), (80, 86, 100)
    legs = (240, 160, 110)
    c.push(x, y, s, flip=face < 0)
    if fly <= 0:
        for k, fx in enumerate((-8, 8)):
            sw = math.sin(walk + k * math.pi) * 6 if walk else 0
            c.line([(fx, -26), (fx + sw, 0)], legs, 3, cap=False)
            c.poly([(fx + sw - 4, 0), (fx + sw + 10, 0), (fx + sw + 4, -4)], legs, w=1.5)
    # tail
    c.poly([(-30, -50), (-56, -60), (-52, -44), (-28, -36)], white)
    c.poly([(-48, -58), (-56, -60), (-52, -44), (-46, -46)], dgrey, ol=None)
    c.ellipse(0, -46, 36, 24, white)
    # wing
    if fly > 0:
        flap = math.sin(t * 14) * 0.9
        tip = (-34 - 10 * math.cos(flap), -60 - 50 * math.sin(flap))
        c.poly([(-16, -54), tip, (-40, -50 - 30 * math.sin(flap)), (10, -50)], grey)
        c.poly([(tip[0] - 4, tip[1] + 4), tip, (tip[0] + 10, tip[1] + 8)], dgrey, ol=None)
    else:
        c.poly([(-30, -54), (20, -60), (14, -40), (-36, -42)], grey)
        c.poly([(-36, -42), (-44, -48), (-30, -54)], dgrey, w=1.5)
    # neck + head
    c.ellipse(24, -64, 16, 20, white, ol=None)
    c.circle(28, -78, 17, white)
    # scruffy tuft
    for k in range(3):
        c.line([(22 + k * 5, -94), (18 + k * 5 - 2, -104 + k * 2)], OUT, 2)
    # beak
    by = -76
    if mouth > 0.05:
        c.poly([(40, by - 4), (64, by - 2), (40, by + 2)], (250, 210, 60), w=1.5)
        c.poly([(40, by + 4), (60, by + 6 + 8 * mouth), (40, by + 8 + 4 * mouth)], (250, 210, 60), w=1.5)
        c.circle(57, by + 5 + 6 * mouth, 2.5, (220, 50, 40), ol=None)
    else:
        c.poly([(40, by - 4), (64, by), (40, by + 5)], (250, 210, 60), w=1.5)
        c.circle(56, by + 2, 2.5, (220, 50, 40), ol=None)
    # eye with a cheeky brow
    if eyes == "closed":
        c.arc(34, -82, 4.5, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(34, -80, 4.5, 4.5, 200, 340, OUT, 2)
    else:
        c.circle(34, -82, 5, (255, 236, 150), w=1.5)
        c.circle(35, -82, 2.4, (20, 18, 22), ol=None)
    c.line([(28, -90 + 3 * sad), (40, -88 - 2 * sad)], OUT, 2.2)
    if fish:
        fried_fish(c, 60, by + 10, 0.7, 0.4)
    elif chip:
        c.stroke([(52, by + 2), (74, by + 6)], (246, 206, 110), 5)
    c.pop()


def chick(c, x, y, s=1.0, t=0.0, seed=0.0, beak=None):
    """A fluffy grey seagull chick, beak open and cheeping."""
    bob = abs(math.sin(t * 6 + seed * 3)) * 4
    op = beak if beak is not None else max(0.0, math.sin(t * 9 + seed * 5))
    c.push(x, y - bob, s)
    c.ellipse(0, -20, 18, 18, (190, 192, 200))
    for k in range(5):
        a = -math.pi * (0.15 + 0.7 * k / 4)
        c.line([(math.cos(a) * 16, -20 + math.sin(a) * 16), (math.cos(a) * 22, -20 + math.sin(a) * 22)],
               (190, 192, 200), 3)
    c.circle(-5, -26, 3, (20, 18, 22), ol=None)
    c.circle(7, -26, 3, (20, 18, 22), ol=None)
    c.poly([(-4, -20), (4, -20 - 5 * op), (10, -20)], (250, 200, 60), w=1.5)
    c.poly([(-4, -18), (4, -12 + 2 * op), (10, -18)], (250, 200, 60), w=1.5)
    c.pop()


def nest(c, x, y, s=1.0, part="back"):
    c.push(x, y, s)
    twig = (150, 110, 70)
    if part == "back":
        c.ellipse(0, -14, 70, 18, mix(twig, (60, 40, 30), 0.4))
    else:
        c.ellipse(0, -6, 74, 20, twig)
        rng = np.random.default_rng(3)
        for _ in range(16):
            a = rng.uniform(0, math.pi)
            px, py = math.cos(a) * 66, -6 + math.sin(a) * 14
            c.line([(px - 14, py - 3), (px + 14, py + 3)], mix(twig, (60, 40, 30), 0.3), 2)
    c.pop()


CORGI = dict(fur=(226, 146, 70), white=(252, 248, 240), dark=(186, 110, 48))


def corgi_guard(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), march=0.0,
                hat_dy=0.0, wiggle=0.0, nose=0.0, seed=4.2):
    """Biscuit: a corgi King's Guard standing to attention in a huge bearskin hat.
    (x, y) = feet. About 260 tall at s=1 (hat included)."""
    if eyes == "open" and D.blink(t, seed * 1.3):
        eyes = "closed"
    fur, white, dark = CORGI["fur"], CORGI["white"], CORGI["dark"]
    tunic, trousers = (200, 30, 40), (36, 36, 48)
    c.push(x, y, s, flip=face < 0)
    # legs (short!) -- one lifts when marching
    lift = max(0.0, math.sin(march * math.pi)) * 26 if march else 0
    c.rect(-22, -54, -4, -lift * 0.0, trousers, w=2)
    c.rect(4, -54 - lift, 22, -lift, trousers, w=2)
    c.line([(-13, -54), (-13, -4)], RED, 2, cap=False)
    c.ellipse(-12, -4, 15, 7, (20, 20, 24), w=2)
    c.ellipse(14, -4 - lift, 15, 7, (20, 20, 24), w=2)
    # fluffy tail stub peeking out behind
    c.ellipse(-36 + 3 * wiggle * math.sin(t * 20), -72, 12, 9, fur)
    # tunic
    c.rect(-34, -128, 34, -50, tunic, w=2.5, r=16)
    c.rect(-34, -66, 34, -56, (250, 250, 250), w=2)         # white belt
    c.rect(-6, -68, 6, -54, GOLD, w=1.5)
    for by in (-118, -100, -82):
        c.circle(0, by, 3.5, GOLD, w=1)
    c.rect(-34, -128, 34, -118, (30, 30, 50), w=2, r=4)      # collar
    # arms at the sides
    for side in (-1, 1):
        c.rect(side * 34 - 9, -122, side * 34 + 9, -68, tunic, w=2, r=8)
        c.circle(side * 34, -64, 9, white, w=2)
    # head
    hx, hy = 6, -158
    c.poly([(hx - 30, hy - 6), (hx - 40, hy - 46), (hx - 10, hy - 22)], fur)   # ears poke out sideways
    c.poly([(hx + 30, hy - 6), (hx + 42, hy - 46), (hx + 12, hy - 22)], fur)
    c.ellipse(hx, hy, 34, 30, fur)
    c.ellipse(hx + 4, hy + 10, 22, 18, white, ol=None)
    c.poly([(hx - 2, hy - 30), (hx + 6, hy - 8), (hx + 12, hy - 30)], white, ol=None)
    # snout
    c.ellipse(hx + 22, hy + 8, 16, 11, white)
    nose_x = hx + 36 + 2 * nose * math.sin(t * 30)
    c.ellipse(nose_x, hy + 4, 6, 5, (40, 30, 34), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 26, hy + 16, 5, 1 + 4 * mouth, (120, 40, 50), w=1.5)
    else:
        c.arc(hx + 26, hy + 13, 6, 4, 20, 160, OUT, 2)
    # eyes
    lx, ly = look
    for ex in (hx - 4, hx + 16):
        ey = hy - 4
        if eyes == "closed":
            c.arc(ex, ey, 5, 3, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 2, 5, 5, 200, 340, OUT, 2.5)
        elif eyes == "squeeze":
            c.line([(ex - 5, ey - 3), (ex + 5, ey)], OUT, 2.5)
            c.line([(ex - 5, ey + 3), (ex + 5, ey)], OUT, 2.5)
        else:
            c.ellipse(ex, ey, 5.5, 6.5, (255, 255, 255), w=2)
            c.circle(ex + 1 + lx * 2.5, ey + ly * 2, 3.2, (40, 26, 20), ol=None)
            c.circle(ex + 2 + lx * 2.5, ey - 1.5 + ly * 2, 1.1, (255, 255, 255), ol=None)
    # chin strap
    c.line([(hx - 28, hy - 18), (hx - 8, hy + 22), (hx + 30, hy + 18)], GOLD, 2.5, cap=False)
    # bearskin hat
    c.push(hx - 2, hy - 24 - hat_dy)
    fluff = (28, 26, 32)
    c.ellipse(0, -52, 40, 62, fluff)
    for k in range(9):
        a = -math.pi * k / 8
        c.circle(math.cos(a) * 36, -52 + math.sin(a) * 56, 9, fluff, ol=None)
    c.ellipse(-12, -78, 10, 18, (60, 58, 70), ol=None)
    c.ellipse(-30, -40, 8, 14, (255, 255, 255), w=1.5)       # white plume
    c.pop()
    c.pop()
