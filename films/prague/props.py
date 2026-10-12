"""Props, buildings and new characters for the Prague film (flat cartoon style).

Everything draws with the shared Canvas (draw.py) in output-pixel units;
local origin is usually the bottom-centre of the object.
"""
import math

import numpy as np

import draw as D
from draw import OUT, lerp, mix

# ------------------------------------------------------------------ palette
ROOF = (198, 76, 54)
ROOF_D = (160, 56, 44)
COPPER = (112, 182, 152)
COPPER_D = (78, 140, 120)
GOTHIC = (104, 96, 104)
GOTHIC_D = (78, 72, 82)
GOTHIC_L = (136, 128, 132)
STONE = (222, 210, 188)
STONE_D = (186, 172, 150)
SNOW = (248, 250, 255)
SNOW_D = (214, 224, 242)
GOLD = (242, 196, 70)
GOLD_D = (196, 148, 44)
RIVER = (74, 112, 150)
RIVER_D = (52, 84, 124)
RIVER_L = (150, 186, 214)
WOOD = (150, 98, 60)
WOOD_D = (112, 70, 44)
PINE = (52, 116, 86)
PINE_D = (36, 88, 66)
WALLS = [(244, 226, 190), (236, 196, 146), (250, 238, 220), (226, 186, 150), (240, 212, 204),
         (206, 220, 196), (246, 220, 160), (222, 206, 226), (214, 230, 236)]
LIGHT = (255, 226, 130)


# ================================================================= buildings

def window(c, x, y, w=14, h=20, col=(70, 72, 98), frame=(252, 250, 244), lit=False, arch=False):
    fill = LIGHT if lit else col
    if arch:
        c.rect(x - w / 2, y - h / 2 + w / 2, x + w / 2, y + h / 2, fill, w=1.5)
        c.ellipse(x, y - h / 2 + w / 2, w / 2, w / 2, fill, w=1.5)
        c.rect(x - w / 2 + 1, y - h / 2 + w / 2, x + w / 2 - 1, y - h / 2 + w / 2 + 3, fill, ol=None)
    else:
        c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill, w=1.5)
    c.line([(x, y - h / 2 + 2), (x, y + h / 2 - 1)], frame, 1.2, cap=False)
    c.line([(x - w / 2 + 1, y + 1), (x + w / 2 - 1, y + 1)], frame, 1.2, cap=False)


def house(c, x, base, w, h, wall, rng, roof=ROOF, snow=True, gable=None, lit=0.0, roof_h=None):
    """A Prague town house: pastel wall, red roof (plain or baroque gable), rows of windows."""
    rh = roof_h if roof_h is not None else rng.uniform(0.35, 0.6) * w
    gable = gable if gable is not None else rng.integers(3)
    c.rect(x, base - h, x + w, base, wall, w=2)
    if gable == 0:
        # pitched roof seen from the side (slope)
        c.poly([(x - 4, base - h), (x + w * 0.15, base - h - rh), (x + w * 0.85, base - h - rh),
                (x + w + 4, base - h)], roof, w=2)
        if snow:
            c.poly([(x + w * 0.15, base - h - rh), (x + w * 0.85, base - h - rh), (x + w * 0.9, base - h - rh * 0.8),
                    (x + w * 0.1, base - h - rh * 0.8)], SNOW, w=1.5)
        # dormer
        dx = x + w / 2
        c.rect(dx - 8, base - h - rh * 0.65, dx + 8, base - h - rh * 0.25, wall, w=1.5)
        c.poly([(dx - 11, base - h - rh * 0.62), (dx, base - h - rh * 0.85), (dx + 11, base - h - rh * 0.62)], roof, w=1.5)
    elif gable == 1:
        # baroque curly gable
        g = rh
        pts = [(x, base - h), (x + w * 0.12, base - h - g * 0.35), (x + w * 0.22, base - h - g * 0.45),
               (x + w * 0.3, base - h - g * 0.8), (x + w * 0.5, base - h - g * 1.05), (x + w * 0.7, base - h - g * 0.8),
               (x + w * 0.78, base - h - g * 0.45), (x + w * 0.88, base - h - g * 0.35), (x + w, base - h)]
        c.poly(pts, wall, w=2)
        c.poly([(x + w * 0.3, base - h - g * 0.8), (x + w * 0.5, base - h - g * 1.05), (x + w * 0.7, base - h - g * 0.8)],
               SNOW if snow else wall, w=1.5)
        c.circle(x + w * 0.5, base - h - g * 1.05 - 5, 4, GOLD, w=1.5)
        window(c, x + w / 2, base - h - g * 0.45, 10, 14, lit=lit > 0.5 and rng.random() < 0.6)
    else:
        # pitched front gable (triangle) with red roof
        c.poly([(x - 3, base - h), (x + w / 2, base - h - rh), (x + w + 3, base - h)], roof, w=2)
        if snow:
            c.poly([(x + w / 2, base - h - rh), (x + w / 2 - w * 0.18, base - h - rh * 0.64),
                    (x + w / 2 + w * 0.18, base - h - rh * 0.64)], SNOW, w=1.5)
        window(c, x + w / 2, base - h - rh * 0.35, 9, 12, lit=lit > 0.5 and rng.random() < 0.6)
    # cornice band
    c.rect(x, base - h, x + w, base - h + 5, mix(wall, (255, 255, 255), 0.4), w=1.5)
    # window grid
    cols = max(2, int(w // 30))
    rows = max(1, int((h - 30) // 38))
    for r in range(rows):
        for k in range(cols):
            wx = x + (k + 0.5) * w / cols
            wy = base - h + 30 + r * 38
            if wy > base - 22:
                continue
            window(c, wx, wy, 12, 18, lit=lit > 0 and rng.random() < lit)
    # door / arcade at street level
    if w > 60:
        c.rect(x + w / 2 - 9, base - 26, x + w / 2 + 9, base, mix(wall, (90, 60, 50), 0.6), w=1.5, r=6)


def spire(c, x, base, s=1.0, col=COPPER, body=STONE, kind=0, ball=True):
    """A church spire: kind 0 = slim needle, 1 = onion dome + needle, 2 = gothic dark needle."""
    c.push(x, base, s)
    if kind == 2:
        c.rect(-16, -140, 16, 0, GOTHIC, w=2)
        c.poly([(-20, -140), (0, -260), (20, -140)], GOTHIC_D, w=2)
        for dx in (-20, 20):
            c.poly([(dx - 5, -140), (dx, -170), (dx + 5, -140)], GOTHIC_D, w=1.5)
        window(c, 0, -100, 8, 22, col=(50, 46, 60), arch=True)
        if ball:
            c.circle(0, -262, 4, GOLD, w=1.5)
    elif kind == 1:
        c.rect(-14, -110, 14, 0, body, w=2)
        window(c, 0, -80, 8, 18, arch=True)
        c.ellipse(0, -124, 18, 18, col, w=2)
        c.rect(-4, -150, 4, -128, col, w=1.5)
        c.ellipse(0, -154, 8, 9, col, w=1.5)
        c.poly([(-4, -160), (0, -196), (4, -160)], col, w=1.5)
        if ball:
            c.circle(0, -198, 3.5, GOLD, w=1.2)
    else:
        c.rect(-12, -100, 12, 0, body, w=2)
        window(c, 0, -72, 7, 16, arch=True)
        c.poly([(-15, -100), (0, -200), (15, -100)], col, w=2)
        c.poly([(-15, -100), (0, -200), (-4, -100)], mix(col, (0, 0, 0), 0.15), ol=None)
        if ball:
            c.circle(0, -202, 3.5, GOLD, w=1.2)
    c.pop()


def st_vitus(c, x, base, s=1.0, col=GOTHIC, dark=GOTHIC_D, roof=COPPER):
    """St Vitus Cathedral: the great south tower with a green cupola, and the twin west spires."""
    c.push(x, base, s)
    # long nave roof
    c.poly([(-150, -110), (-120, -150), (170, -150), (200, -110)], roof, w=2)
    c.rect(-150, -110, 200, 0, col, w=2)
    for k in range(8):
        window(c, -130 + k * 42, -60, 14, 50, col=(70, 80, 120), arch=True)
        c.poly([(-150 + k * 44, -110), (-140 + k * 44, -140), (-130 + k * 44, -110)], dark, w=1.5)
    # twin west spires (left)
    for dx in (-140, -96):
        c.rect(dx - 16, -250, dx + 16, -100, col, w=2)
        c.poly([(dx - 18, -250), (dx, -380), (dx + 18, -250)], dark, w=2)
        for pdx in (-18, 18):
            c.poly([(dx + pdx - 4, -250), (dx + pdx, -276), (dx + pdx + 4, -250)], dark, w=1.2)
        window(c, dx, -200, 10, 34, col=(60, 60, 80), arch=True)
    c.ellipse(-118, -170, 14, 14, (200, 120, 160), w=1.5)    # rose window
    # the great south tower with its green copper helmet
    c.rect(40, -300, 92, -120, col, w=2)
    window(c, 66, -250, 14, 40, col=(60, 60, 80), arch=True)
    c.ellipse(66, -318, 32, 22, roof, w=2)
    c.rect(56, -360, 76, -330, roof, w=1.5)
    c.ellipse(66, -366, 16, 12, roof, w=1.5)
    c.poly([(60, -372), (66, -410), (72, -372)], roof, w=1.5)
    c.circle(66, -412, 4, GOLD, w=1.2)
    # flying buttress pinnacles along the roof
    for k in range(6):
        px = 110 + k * 16
        c.poly([(px - 3, -150), (px, -176), (px + 3, -150)], dark, w=1)
    c.pop()


def castle(c, x, base, s=1.0, snow=True, lit=0.0, rng_seed=7):
    """Prague Castle on its hill: the long palace front with rows of windows, and St Vitus behind."""
    rng = np.random.default_rng(rng_seed)
    c.push(x, base, s)
    st_vitus(c, 40, -60, 0.95)
    # long palace
    c.rect(-330, -110, 300, 0, (242, 232, 210), w=2)
    c.poly([(-334, -110), (-320, -132), (290, -132), (304, -110)], ROOF, w=2)
    if snow:
        c.poly([(-320, -132), (290, -132), (294, -126), (-324, -126)], SNOW, ol=None)
    for r in range(3):
        for k in range(24):
            window(c, -316 + k * 26, -88 + r * 30, 9, 14, lit=lit > 0 and rng.random() < lit)
    # a few side wings and little towers
    c.rect(-380, -80, -330, 0, (236, 222, 196), w=2)
    c.poly([(-384, -80), (-355, -110), (-326, -80)], ROOF, w=2)
    spire(c, -300, -132, 0.4, kind=0)
    spire(c, 260, -132, 0.38, kind=1)
    c.pop()


def hill(c, x0, x1, base, top, col, snow=True):
    pts = [(x0, base)]
    n = 24
    for k in range(n + 1):
        u = k / n
        xx = lerp(x0, x1, u)
        yy = base - (base - top) * math.sin(math.pi * min(1, u * 1.2)) ** 0.8
        pts.append((xx, yy))
    pts.append((x1, base))
    c.poly(pts, col, ol=None)
    if snow:
        for k in range(n):
            u = (k + 0.5) / n
            xx = lerp(x0, x1, u)
            yy = base - (base - top) * math.sin(math.pi * min(1, u * 1.2)) ** 0.8
            c.ellipse(xx, yy + 6, 12, 4, SNOW, ol=None)


def roofscape(c, x0, x1, base, seed, scale=1.0, lit=0.0, snow=True, spires=True):
    """A row of red roofs and pastel walls with spires sticking up here and there."""
    rng = np.random.default_rng(seed)
    x = x0
    while x < x1:
        w = rng.uniform(60, 120)
        h = rng.uniform(70, 140)
        c.push(x, base, scale)
        house(c, 0, 0, w, h, WALLS[int(rng.integers(len(WALLS)))], rng, snow=snow, lit=lit)
        if spires and rng.random() < 0.28:
            spire(c, w / 2, -h - 4, rng.uniform(0.55, 0.85), kind=int(rng.integers(3)))
        c.pop()
        x += (w + rng.uniform(-6, 4)) * scale


def bridge_tower(c, x, base, s=1.0, snow=True):
    """The Old Town Bridge Tower: dark gothic gate with a steep roof and corner pinnacles."""
    c.push(x, base, s)
    c.rect(-70, -330, 70, 0, GOTHIC, w=2.5)
    for k in range(6):
        c.line([(-70, -300 + k * 50), (70, -300 + k * 50)], GOTHIC_D, 1.5, cap=False)
    # gate arch
    c.rect(-38, -130, 38, 0, (40, 34, 44), w=2)
    c.ellipse(0, -130, 38, 38, (40, 34, 44), w=2)
    c.rect(-36, -130, 36, -110, (40, 34, 44), ol=None)
    # coats of arms band and statues niche
    c.rect(-56, -220, 56, -160, GOTHIC_L, w=2)
    for k in range(5):
        c.rect(-48 + k * 20, -212, -36 + k * 20, -172, (176, 152, 120), w=1.2, r=4)
    window(c, -30, -270, 14, 34, col=(50, 46, 60), arch=True)
    window(c, 30, -270, 14, 34, col=(50, 46, 60), arch=True)
    # steep roof
    c.poly([(-74, -330), (-40, -460), (40, -460), (74, -330)], GOTHIC_D, w=2.5)
    c.poly([(-40, -460), (0, -500), (40, -460)], GOTHIC_D, w=2)
    if snow:
        c.poly([(-74, -330), (74, -330), (66, -350), (-66, -350)], SNOW, w=1.5)
    for dx in (-70, 70):
        c.rect(dx - 10, -380, dx + 10, -320, GOTHIC, w=1.8)
        c.poly([(dx - 12, -380), (dx, -430), (dx + 12, -380)], GOTHIC_D, w=1.8)
        c.circle(dx, -432, 3, GOLD, w=1)
    c.circle(0, -503, 5, GOLD, w=1.5)
    c.pop()


def bridge_side(c, x0, x1, deck, s=1.0, arch_w=150, col=STONE_D, dark=(150, 136, 118), water=None, statues=True,
                snow=True):
    """Charles Bridge seen from the side: a row of stone arches with statues on the parapet."""
    n = int((x1 - x0) / (arch_w * s)) + 1
    c.rect(x0, deck - 26 * s, x1, deck + 30 * s, col, w=2)
    for k in range(n):
        ax = x0 + k * arch_w * s
        # pier with a cutwater
        c.rect(ax - 18 * s, deck + 30 * s, ax + 18 * s, deck + 140 * s, col, w=2)
        c.poly([(ax - 18 * s, deck + 110 * s), (ax, deck + 92 * s), (ax + 18 * s, deck + 110 * s)], dark, w=1.5)
        # arch opening
        mx = ax + arch_w * s / 2
        c.ellipse(mx, deck + 120 * s, (arch_w / 2 - 18) * s, 80 * s, water or RIVER_D, w=2)
    c.rect(x0, deck + 120 * s, x1, deck + 150 * s, water or RIVER_D, ol=None)
    c.line([(x0, deck + 30 * s), (x1, deck + 30 * s)], dark, 2, cap=False)
    # parapet
    c.rect(x0, deck - 40 * s, x1, deck - 26 * s, col, w=2)
    if snow:
        c.rect(x0, deck - 44 * s, x1, deck - 38 * s, SNOW, ol=None)
    if statues:
        for k in range(n):
            sx = x0 + (k + 0.5) * arch_w * s
            statue(c, sx, deck - 40 * s, 0.45 * s, kind=k % 3, snow=snow)


def statue(c, x, y, s=1.0, kind=0, snow=True, col=(70, 66, 70), halo=True):
    """A dark baroque saint on a pedestal (Charles Bridge style)."""
    c.push(x, y, s)
    c.rect(-26, -60, 26, 0, STONE_D, w=2)
    c.rect(-30, -66, 30, -58, STONE, w=1.5)
    # robed figure
    c.poly([(-22, -66), (-16, -150), (16, -150), (24, -66)], col, w=2)
    c.circle(0, -166, 15, col, w=2)
    if kind == 0:
        c.line([(14, -140), (30, -190)], col, 5)          # raised arm with a cross
        c.line([(26, -200), (34, -170)], GOLD_D, 3)
        c.line([(20, -188), (40, -184)], GOLD_D, 3)
    elif kind == 1:
        c.ellipse(-24, -120, 12, 20, col, w=2)              # holding a book
        c.rect(-34, -128, -14, -112, (120, 90, 60), w=1.5)
    else:
        c.poly([(-16, -140), (-50, -110), (-44, -100), (-12, -126)], col, w=2)   # arm stretched out
    if halo:
        for k in range(5):
            a = math.pi * (0.15 + 0.7 * k / 4)
            c.circle(-math.cos(a) * 24, -170 - math.sin(a) * 24, 3.2, GOLD, w=1)
    if snow:
        c.ellipse(0, -181, 12, 4, SNOW, ol=None)
        c.rect(-28, -70, 28, -66, SNOW, ol=None)
    c.pop()


def lamp(c, x, y, s=1.0, lit=0.6):
    c.push(x, y, s)
    c.line([(0, 0), (0, -150)], (50, 48, 56), 5)
    c.rect(-12, -8, 12, 0, (50, 48, 56), ol=None)
    c.poly([(-12, -150), (12, -150), (16, -178), (-16, -178)], LIGHT if lit else (200, 210, 220), w=2)
    c.poly([(-18, -178), (0, -194), (18, -178)], (50, 48, 56), w=2)
    c.pop()


def tyn_church(c, x, base, s=1.0, snow=True):
    """The Church of Our Lady before Tyn: two dark towers bristling with little golden-tipped spires."""
    c.push(x, base, s)
    body = (120, 110, 112)
    # nave gable between towers
    c.poly([(-70, -260), (0, -360), (70, -260)], body, w=2)
    c.rect(-70, -260, 70, 0, body, w=2)
    window(c, 0, -300, 16, 40, col=(70, 70, 100), arch=True)
    for dx in (-110, 110):
        c.rect(dx - 40, -420, dx + 40, 0, body, w=2.5)
        for r in range(3):
            window(c, dx, -360 + r * 90, 14, 40, col=(60, 60, 84), arch=True)
        # tall dark helmet
        c.poly([(dx - 46, -420), (dx, -620), (dx + 46, -420)], GOTHIC_D, w=2.5)
        # cluster of little spires around the helmet
        for k, (px, py, hh) in enumerate(((-46, -420, 70), (46, -420, 70), (-30, -470, 64), (30, -470, 64),
                                          (-16, -520, 56), (16, -520, 56))):
            c.poly([(dx + px - 7, py), (dx + px, py - hh), (dx + px + 7, py)], GOTHIC_D, w=1.8)
            c.circle(dx + px, py - hh - 3, 4, GOLD, w=1.2)
        c.circle(dx, -626, 7, GOLD, w=1.5)
        c.line([(dx, -634), (dx, -650)], GOLD_D, 2, cap=False)
        if snow:
            c.poly([(dx - 46, -420), (dx + 46, -420), (dx + 36, -436), (dx - 36, -436)], SNOW, w=1.2)
    c.pop()


# ================================================================== the clock

def gear(c, x, y, r, ang, teeth=12, col=GOLD, dark=GOLD_D, hub=True, spokes=4, w=2.0):
    pts = []
    for k in range(teeth * 4):
        a = ang + k * math.tau / (teeth * 4)
        rr = r * (1.0 if (k % 4) in (1, 2) else 0.84)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, col, w=w)
    c.circle(x, y, r * 0.66, mix(col, dark, 0.35), w=w * 0.8)
    for k in range(spokes):
        a = ang + k * math.tau / spokes
        c.line([(x, y), (x + math.cos(a) * r * 0.66, y + math.sin(a) * r * 0.66)], col, max(3, r * 0.12), cap=False)
    if hub:
        c.circle(x, y, r * 0.18, dark, w=w * 0.8)
        c.circle(x, y, r * 0.07, (80, 60, 40), ol=None)


def orloj_dial(c, x, y, r, t=0.0, hand=0.0, moon_ph=0.3):
    """The astronomical dial: blue sky, dark earth, golden zodiac ring and the sun hand."""
    c.circle(x, y, r * 1.08, GOLD_D, w=2.5)
    c.circle(x, y, r, (40, 36, 46), w=2)
    # sky (upper) and night (lower)
    sky = [(0, (90, 160, 220)), (1, (120, 190, 240))]
    c.circle(x, y, r * 0.92, (86, 152, 214), ol=None)
    # orange dawn/dusk bands and the black night circle
    c.ellipse(x, y + r * 0.28, r * 0.9, r * 0.64, (220, 140, 60), ol=None)
    c.ellipse(x, y + r * 0.42, r * 0.78, r * 0.52, (56, 46, 54), ol=None)
    c.ellipse(x, y + r * 0.62, r * 0.58, r * 0.32, (30, 26, 36), ol=None)
    # gold roman numerals ring (dots stand in for numerals)
    for k in range(24):
        a = k * math.tau / 24
        px, py = x + math.cos(a) * r * 0.97, y + math.sin(a) * r * 0.97
        c.circle(px, py, r * 0.035, GOLD, w=1)
    # hour lines of the tropical circles
    c.circle(x, y, r * 0.92, None, w=1.5)
    c.circle(x, y - r * 0.08, r * 0.5, None, w=1.5)
    # the offset zodiac ring
    zx, zy = x + math.cos(hand * 0.3) * r * 0.18, y - r * 0.2
    c.circle(zx, zy, r * 0.62, None, w=3)
    c.circle(zx, zy, r * 0.62, None, w=1)
    d = c.d
    for k in range(12):
        a = k * math.tau / 12 + hand * 0.08
        px, py = zx + math.cos(a) * r * 0.62, zy + math.sin(a) * r * 0.62
        c.circle(px, py, r * 0.05, GOLD, w=1)
    # hands: golden hand with the sun, and the moon ball
    a = hand - math.pi / 2
    c.line([(x, y), (x + math.cos(a) * r * 0.98, y + math.sin(a) * r * 0.98)], GOLD, 5)
    c.line([(x, y), (x + math.cos(a) * r * 0.98, y + math.sin(a) * r * 0.98)], GOLD_D, 1.5, cap=False)
    # golden hand tip
    hx, hy = x + math.cos(a) * r * 1.0, y + math.sin(a) * r * 1.0
    c.circle(hx, hy, r * 0.06, GOLD, w=1.5)
    sx, sy = x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6
    c.circle(sx, sy, r * 0.1, (255, 220, 90), w=1.5)
    for k in range(8):
        aa = k * math.tau / 8 + t
        c.line([(sx + math.cos(aa) * r * 0.11, sy + math.sin(aa) * r * 0.11),
                (sx + math.cos(aa) * r * 0.16, sy + math.sin(aa) * r * 0.16)], (255, 220, 90), 2, cap=False)
    a2 = hand * 0.93 - math.pi / 2 + 2.2
    mx, my = x + math.cos(a2) * r * 0.78, y + math.sin(a2) * r * 0.78
    c.line([(x, y), (mx, my)], (60, 56, 64), 3, cap=False)
    c.circle(mx, my, r * 0.07, (220, 220, 210), w=1.5)
    c.ellipse(mx + r * 0.03 * moon_ph, my, r * 0.05, r * 0.07, (40, 36, 46), ol=None)
    c.circle(x, y, r * 0.06, GOLD, w=1.5)


def calendar_dial(c, x, y, r, ang=0.0):
    c.circle(x, y, r * 1.06, GOLD_D, w=2.5)
    c.circle(x, y, r, (236, 220, 180), w=2)
    cols = [(110, 150, 90), (210, 160, 80), (140, 110, 170), (90, 140, 190)]
    for k in range(12):
        a = ang + k * math.tau / 12
        px, py = x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72
        c.circle(px, py, r * 0.16, cols[k % 4], w=1.5)
        c.circle(px, py, r * 0.08, mix(cols[k % 4], (255, 255, 255), 0.4), ol=None)
    c.circle(x, y, r * 0.45, (190, 40, 50), w=2)
    c.circle(x, y, r * 0.3, (240, 220, 160), w=1.5)
    c.circle(x, y, r * 0.12, GOLD, w=1.5)


def apostle(c, x, y, s=1.0, col=(90, 120, 190), k=0, bow=0.0):
    """A little carved apostle in a robe, with a golden halo."""
    c.push(x, y, s)
    c.poly([(-16, 0), (-12, -54), (12, -54), (16, 0)], col, w=2)
    c.poly([(-12, -54), (0, -44), (12, -54), (10, -36), (-10, -36)], mix(col, (255, 255, 255), 0.25), w=1.5)
    hy = -66 + 4 * bow
    c.circle(0, hy - 2, 14, GOLD, w=1.5)
    c.circle(0, hy, 10, (240, 206, 170), w=1.8)
    c.ellipse(0, hy + 7, 8, 5, (230, 230, 230) if k % 2 else (140, 100, 70), ol=None)  # beard
    c.circle(-3, hy - 2, 1.4, OUT, ol=None)
    c.circle(4, hy - 2, 1.4, OUT, ol=None)
    # attribute: key, book, sword, cross...
    if k % 4 == 0:
        c.line([(14, -40), (22, -10)], GOLD_D, 3)
        c.circle(14, -42, 4, None, w=2)
    elif k % 4 == 1:
        c.rect(6, -38, 22, -24, (180, 60, 60), w=1.5)
    elif k % 4 == 2:
        c.line([(16, -50), (18, -6)], (200, 206, 216), 3)
        c.line([(10, -40), (24, -40)], GOLD_D, 2.5)
    else:
        c.line([(16, -54), (16, -14)], WOOD_D, 3)
        c.line([(9, -44), (23, -44)], WOOD_D, 3)
    c.pop()


APOSTLE_COLS = [(90, 120, 190), (190, 70, 70), (80, 150, 100), (200, 150, 60), (140, 90, 170), (60, 140, 170),
                (210, 110, 80), (110, 110, 160), (170, 70, 120), (90, 160, 140), (220, 170, 90), (120, 90, 70)]


def rooster(c, x, y, s=1.0, crow=0.0, t=0.0):
    c.push(x, y, s)
    flap = math.sin(t * 18) * crow
    c.ellipse(0, -20, 22, 16, GOLD, w=2)
    # tail
    for k in range(3):
        c.poly([(-16, -26), (-34 - k * 4, -50 + k * 10), (-24 + k * 2, -24)], GOLD_D, w=1.5)
    # wing
    c.poly([(-8, -24), (14, -30 - 18 * flap), (16, -14)], GOLD_D, w=1.5)
    # head
    hy = -44 - 4 * crow
    c.circle(16, hy, 10, GOLD, w=2)
    c.poly([(10, hy - 9), (14, hy - 18), (18, hy - 11), (22, hy - 18), (24, hy - 7)], (220, 60, 50), w=1.5)
    c.poly([(25, hy - 2), (34 + 4 * crow, hy + 1 - 4 * crow), (25, hy + 4)], (240, 170, 60), w=1.5)
    if crow > 0.3:
        c.poly([(25, hy + 3), (32, hy + 8), (25, hy + 6)], (240, 170, 60), w=1.2)
    c.circle(19, hy - 2, 1.8, OUT, ol=None)
    c.line([(20, hy + 8), (22, hy + 14)], (220, 60, 50), 3)
    c.line([(-4, -6), (-4, 4)], GOLD_D, 2.5)
    c.line([(6, -6), (6, 4)], GOLD_D, 2.5)
    c.pop()


def orloj_tower(c, x, base, s=1.0, snow=True):
    """Static part of the Old Town Hall tower with the clock housing (dial etc. drawn on top separately).

    Local coordinates: x centred, base = ground. Key anchor points (local, unscaled):
      dial centre (0, -760), dial radius 150; calendar centre (0, -440), radius 110;
      apostle windows at (-46, -1020) and (46, -1020) (60 x 80); rooster at (0, -1110);
      skeleton ledge at (215, -700); little door at (232, -880).
    """
    c.push(x, base, s)
    body = (176, 166, 158)
    dark = (140, 130, 124)
    # the tower block
    c.rect(-300, -1500, 300, 0, body, w=3)
    for k in range(18):
        c.line([(-300, -60 - k * 80), (300, -60 - k * 80)], mix(body, dark, 0.5), 1.5, cap=False)
    # top: gallery and the gothic roof with corner turrets
    c.rect(-320, -1540, 320, -1500, dark, w=2.5)
    for k in range(16):
        c.rect(-316 + k * 40, -1576, -300 + k * 40, -1540, dark, w=1.5)
    c.poly([(-300, -1576), (-180, -1820), (180, -1820), (300, -1576)], GOTHIC_D, w=3)
    c.poly([(-180, -1820), (0, -1930), (180, -1820)], GOTHIC_D, w=3)
    for dx in (-300, 300):
        c.rect(dx - 30, -1660, dx + 30, -1540, dark, w=2)
        c.poly([(dx - 34, -1660), (dx, -1780), (dx + 34, -1660)], GOTHIC_D, w=2)
        c.circle(dx, -1784, 6, GOLD, w=1.5)
    c.circle(0, -1936, 9, GOLD, w=2)
    if snow:
        c.poly([(-300, -1576), (300, -1576), (290, -1594), (-290, -1594)], SNOW, w=1.5)
    for k in range(3):
        window(c, -120 + k * 120, -1400, 30, 70, col=(60, 58, 74), arch=True)
    # clock housing: pointed gothic frame
    c.rect(-250, -1180, 250, -260, mix(body, (255, 255, 255), 0.18), w=3)
    c.poly([(-250, -1180), (0, -1300), (250, -1180)], mix(body, (255, 255, 255), 0.18), w=3)
    c.line([(-250, -1180), (0, -1296), (250, -1180)], GOLD_D, 2, cap=False)
    # sculpted crockets along the pointed arch
    for k in range(9):
        u = k / 8
        px = lerp(-250, 250, u)
        py = -1180 - 120 * (1 - abs(u - 0.5) * 2)
        c.circle(px, py - 6, 7, GOLD_D, w=1.2)
    # rooster niche
    c.rect(-34, -1170, 34, -1100, (60, 54, 66), w=2, r=6)
    # apostle windows (dark openings; apostles drawn later)
    for dx in (-60, 60):
        c.rect(dx - 34, -1070, dx + 34, -970, (34, 30, 40), w=2.5)
        c.ellipse(dx, -1070, 34, 26, (34, 30, 40), w=2.5)
        c.rect(dx - 32, -1072, dx + 32, -1060, (34, 30, 40), ol=None)
    # little stone ledges for the side figures
    for dx in (-215, 215):
        c.rect(dx - 34, -712, dx + 34, -696, STONE_D, w=2)
        c.rect(dx - 30, -500, dx + 30, -486, STONE_D, w=2)
    # the left side figures: Vanity (with a mirror) on the upper ledge, the Miser below
    _side_figure(c, -215, -712, 0)
    _side_figure(c, -215, -500, 1)
    _side_figure(c, 215, -500, 2)
    # little maintenance door beside the dial
    c.rect(214, -930, 252, -850, (110, 74, 50), w=2, r=4)
    c.circle(244, -888, 3, GOLD, w=1)
    # gothic entrance at street level
    c.rect(-70, -180, 70, 0, (54, 46, 54), w=2.5)
    c.ellipse(0, -180, 70, 60, (54, 46, 54), w=2.5)
    c.rect(-68, -182, 68, -170, (54, 46, 54), ol=None)
    c.pop()


def _side_figure(c, x, y, kind):
    c.push(x, y)
    if kind == 0:     # vanity with mirror
        c.poly([(-18, 0), (-14, -90), (14, -90), (18, 0)], (190, 90, 110), w=2)
        c.circle(0, -104, 14, (240, 206, 170), w=1.8)
        c.circle(-24, -96, 9, (200, 220, 240), w=1.8)
        c.line([(-16, -60), (-24, -86)], (240, 206, 170), 4)
    elif kind == 1:   # miser with a purse
        c.poly([(-18, 0), (-14, -90), (14, -90), (18, 0)], (90, 110, 80), w=2)
        c.circle(0, -104, 14, (240, 206, 170), w=1.8)
        c.poly([(-16, -118), (0, -132), (16, -118)], (120, 70, 50), w=1.5)
        c.ellipse(20, -50, 10, 12, GOLD_D, w=1.5)
    else:             # a musician angel with a lute
        c.poly([(-18, 0), (-14, -90), (14, -90), (18, 0)], (100, 120, 170), w=2)
        c.circle(0, -104, 14, (240, 206, 170), w=1.8)
        c.ellipse(-10, -56, 12, 16, WOOD, w=1.5)
        c.line([(-10, -70), (10, -98)], WOOD_D, 3)
    c.pop()


# ================================================================== characters

KASPAR_RED = (214, 52, 52)
KASPAR_YEL = (250, 200, 60)
KASPAR_GRN = (70, 150, 90)
WOODSKIN = (246, 206, 160)


def kaspar(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, wave=0.0, eyes="open", tangle=0.0,
           jump=0.0, sooty=0.0, bar=True, arms_up=0.0, bow=0.0, seed=0.0):
    """Kasparek, the wooden marionette jester (feet at origin, ~130 tall at s=1).

    walk: phase of a floppy puppet walk; wave: 0..1 waving arm; tangle: knot of strings around him;
    sooty: 0..1 covered in black soot; bar: draw the floating wooden control bar with strings.
    """
    if eyes == "open" and D.blink(t, seed + 0.7):
        eyes = "closed"
    soot = (60, 56, 60)

    def col(cc):
        return mix(cc, soot, 0.75 * sooty)

    bob = abs(math.sin(walk)) * 5 if walk else 0.0
    c.push(x, y - jump - bob, s, flip=face < 0)
    tilt = math.sin(t * 2.0 + seed) * 2 + bow * 14
    # legs: two floppy segments each
    hipy = -52
    for side, ph in ((-1, 0.0), (1, math.pi)):
        sw = math.sin(walk + ph) if walk else 0.0
        kx = side * 6 + sw * 10
        ky = hipy + 26 - max(0, math.cos(walk + ph)) * 6 * (1 if walk else 0)
        fx = side * 6 + sw * 14
        fy = -max(0, math.cos(walk + ph)) * 8 if walk else 0
        c.stroke([(side * 6, hipy), (kx, ky)], col(KASPAR_GRN), 8)
        c.stroke([(kx, ky), (fx, fy - 4)], col(KASPAR_GRN), 7)
        c.circle(kx, ky, 4.5, col(WOOD), w=1.5)
        c.poly([(fx - 7, fy - 8), (fx + 14, fy - 6), (fx + 18, fy - 12), (fx + 10, fy), (fx - 7, fy)],
               col(KASPAR_RED), w=1.8)
    # body: tunic split red | yellow, with a ruff collar
    c.push(0, 0, 1.0)
    c.poly([(-17, hipy + 4), (-14, -92), (14, -92), (17, hipy + 4)], col(KASPAR_RED), w=2)
    c.poly([(0, hipy + 4), (0, -92), (14, -92), (17, hipy + 4)], col(KASPAR_YEL), w=2)
    c.rect(-18, hipy - 2, 18, hipy + 5, col(WOOD_D), w=1.5)
    for k in range(3):
        c.circle(-7, -80 + k * 9, 2.2, col(KASPAR_YEL), w=1)
    # arms: shoulder -> elbow -> hand, floppy; the front arm can wave
    for side in (-1, 1):
        sx, sy = side * 15, -88
        if side == 1 and wave > 0:
            ang = math.radians(-60 - 30 * math.sin(t * 9)) if wave > 0.5 else math.radians(-20)
            ex, ey = sx + 16, sy - 10 * wave
            hx, hy = ex + math.cos(ang) * 16, ey + math.sin(ang) * 16 * wave - 6 * wave
        elif arms_up > 0:
            ex, ey = sx + side * 14, sy - 12 * arms_up
            hx, hy = ex + side * 6, ey - 18 * arms_up
        else:
            swing = math.sin(walk + (0 if side > 0 else math.pi)) * 8 if walk else math.sin(t * 2 + side) * 2
            ex, ey = sx + side * 5 + swing * 0.5, sy + 18
            hx, hy = sx + side * 4 + swing, sy + 34
        c.stroke([(sx, sy), (ex, ey)], col(KASPAR_YEL if side > 0 else KASPAR_RED), 7)
        c.stroke([(ex, ey), (hx, hy)], col(KASPAR_YEL if side > 0 else KASPAR_RED), 6)
        c.circle(ex, ey, 3.5, col(WOOD), w=1.2)
        c.circle(hx, hy, 5.5, col(WOODSKIN), w=1.8)
        if side == 1:
            hand_front = (hx, hy)
        else:
            hand_back = (hx, hy)
    # ruff collar
    pts = []
    for k in range(13):
        a = math.pi * k / 12
        r = 21 if k % 2 == 0 else 15
        pts.append((math.cos(a) * r, -94 + math.sin(a) * r * 0.35))
    c.poly([(-21, -94)] + pts + [(21, -94)], col((252, 250, 244)), w=1.5)
    c.pop()
    # head (round wooden head with a hinged jaw)
    c.push(0, -112, 1.0)
    hx, hy = math.sin(math.radians(tilt)) * 4, 0
    jaw = 7 * mouth
    c.rect(hx - 11, hy + 4, hx + 13, hy + 12 + jaw, col(WOODSKIN), w=1.8, r=4)
    if mouth > 0.05:
        c.rect(hx - 8, hy + 6, hx + 10, hy + 8 + jaw, (120, 40, 50), ol=None)
    c.circle(hx, hy - 4, 18, col(WOODSKIN), w=2)
    c.circle(hx + 9, hy + 2, 5.5, col((250, 150, 150)), ol=None)      # rosy cheeks
    c.circle(hx - 9, hy + 2, 4.5, col((250, 150, 150)), ol=None)
    c.circle(hx + 13, hy - 3, 6, col((222, 70, 60)), w=1.8)           # big red nose
    if eyes == "closed":
        c.arc(hx + 3, hy - 9, 3.5, 2.5, 20, 160, OUT, 2)
        c.arc(hx - 7, hy - 9, 3.5, 2.5, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(hx + 3, hy - 7, 3.5, 3.5, 200, 340, OUT, 2)
        c.arc(hx - 7, hy - 7, 3.5, 3.5, 200, 340, OUT, 2)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        for ex in (hx + 3, hx - 7):
            c.ellipse(ex, hy - 9, 3.6 * big, 4.4 * big, (255, 255, 255), w=1.5)
            c.circle(ex + 1, hy - 9, 2.0, (30, 26, 30), ol=None)
    if mouth <= 0.05:
        c.arc(hx + 2, hy + 6, 7, 4, 10, 170, OUT, 2)
    # jester hat: two floppy points with bells
    sway = math.sin(t * 3 + seed) * 4 + (math.sin(walk * 2) * 6 if walk else 0)
    c.poly([(hx - 18, hy - 12), (hx - 38, hy - 28 + sway), (hx - 32, hy - 10 + sway * 0.5), (hx - 2, hy - 20)],
           col(KASPAR_YEL), w=1.8)
    c.poly([(hx + 18, hy - 12), (hx + 40, hy - 32 - sway), (hx + 34, hy - 12 - sway * 0.5), (hx + 2, hy - 20)],
           col(KASPAR_RED), w=1.8)
    c.poly([(hx - 18, hy - 12), (hx - 6, hy - 34), (hx + 6, hy - 34), (hx + 18, hy - 12)], col(KASPAR_RED), w=1.8)
    c.poly([(hx - 18, hy - 12), (hx - 6, hy - 34), (hx, hy - 34), (hx, hy - 12)], col(KASPAR_YEL), ol=None)
    c.rect(hx - 19, hy - 16, hx + 19, hy - 10, col(KASPAR_GRN), w=1.5, r=2)
    c.circle(hx - 38, hy - 28 + sway, 4, GOLD, w=1.2)
    c.circle(hx + 40, hy - 32 - sway, 4, GOLD, w=1.2)
    c.pop()
    # the floating control bar and strings (a touch of Christmas magic)
    if bar:
        by = -186 + 4 * math.sin(t * 2.3 + seed)
        bx = 2 * math.sin(t * 1.7)
        scol = (250, 246, 236)
        for px, py in ((hand_front[0], hand_front[1]), (hand_back[0], hand_back[1]), (0, -146)):
            if tangle > 0.5:
                break
            c.line([(px, py), (bx + px * 0.6, by)], scol, 1.0, cap=False)
        c.rect(bx - 26, by - 3, bx + 26, by + 3, WOOD, w=1.5, r=2)
        c.rect(bx - 3, by - 14, bx + 3, by + 12, WOOD, w=1.5, r=2)
    if tangle > 0:
        rng = np.random.default_rng(5)
        pts = [(rng.uniform(-30, 30), rng.uniform(-150, -20)) for _ in range(int(14 * tangle) + 2)]
        c.line(pts, (250, 246, 236), 1.4, cap=False)
        for k in range(int(5 * tangle)):
            c.ellipse(rng.uniform(-24, 24), rng.uniform(-140, -30), 5, 4, None, w=1.2)
    c.pop()


BONE = (240, 232, 210)
BONE_D = (200, 188, 160)


def bones(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, ring=0.0, eyes="open", nod=0.0, laugh=False, wave=0.0,
          seed=0.0):
    """Mister Bones, the friendly skeleton of the clock (feet at origin, ~180 tall at s=1).

    ring: 0..1 bell-ringing swing of the right arm; wave: wave with the left (hourglass) arm.
    """
    if eyes == "open" and D.blink(t, seed + 2.2):
        eyes = "closed"
    shake = math.sin(t * 22) * 2 if laugh else 0.0
    c.push(x, y, s, flip=face < 0)
    # legs
    for dx in (-10, 10):
        c.stroke([(dx, -70), (dx * 1.1, -36)], BONE, 6, ol=OUT)
        c.circle(dx * 1.1, -36, 5, BONE, w=1.5)
        c.stroke([(dx * 1.1, -36), (dx * 1.2, -6)], BONE, 5, ol=OUT)
        c.ellipse(dx * 1.2 + 6, -4, 10, 5, BONE, w=1.5)
    # pelvis
    c.ellipse(0, -74, 20, 11, BONE, w=2)
    c.ellipse(-7, -74, 5, 4, (60, 50, 60), ol=None)
    c.ellipse(7, -74, 5, 4, (60, 50, 60), ol=None)
    # spine and ribs
    c.line([(0, -82), (0, -150)], BONE_D, 6)
    for k in range(4):
        yy = -138 + k * 12
        ww = 24 - k * 2.5
        c.arc(0, yy, ww, 9, 200, 340, OUT, 6)
        c.arc(0, yy, ww, 9, 200, 340, BONE, 3.5)
    c.ellipse(0, -152, 26, 6, BONE, w=1.8)                # shoulders / collarbone
    # right arm (front): pulls the bell rope; bell in hand
    sw = math.sin(t * 9) * ring
    ex, ey = 32, -126 + 6 * sw
    hx, hy = 40 + 10 * sw, -104 - 30 * ring + 14 * sw
    c.stroke([(24, -152), (ex, ey)], BONE, 5)
    c.stroke([(ex, ey), (hx, hy)], BONE, 4.5)
    c.circle(hx, hy, 5, BONE, w=1.5)
    # bell hanging from the hand
    ba = 0.5 * sw
    bx, by = hx + math.sin(ba) * 8, hy + 6
    c.push(bx, by, 1.0)
    c.poly([(-10, 22), (-7, 4), (0, 0), (7, 4), (10, 22)], GOLD, w=1.8)
    c.ellipse(0, 22, 11, 3.5, GOLD_D, w=1.5)
    c.circle(math.sin(ba) * 5, 25, 3, GOLD_D, w=1)
    c.pop()
    # left arm (back): holds the hourglass, or waves
    if wave > 0:
        a = math.radians(-70 - 25 * math.sin(t * 8))
        lx, ly = -34, -140
        hx2, hy2 = lx + math.cos(a) * 26 * -1, ly + math.sin(a) * 26
        c.stroke([(-24, -152), (lx, ly)], BONE, 5)
        c.stroke([(lx, ly), (hx2, hy2)], BONE, 4.5)
        c.circle(hx2, hy2, 5, BONE, w=1.5)
    else:
        c.stroke([(-24, -152), (-34, -124)], BONE, 5)
        c.stroke([(-34, -124), (-26, -104)], BONE, 4.5)
        c.push(-26, -100, 1.0)
        c.rect(-10, -18, 10, -14, WOOD, w=1.5)
        c.rect(-10, 14, 10, 18, WOOD, w=1.5)
        c.poly([(-8, -14), (8, -14), (1, 0), (8, 14), (-8, 14), (-1, 0)], (220, 236, 250), w=1.5)
        sand = (0.5 + 0.5 * math.sin(t * 0.3))
        c.poly([(-6, 14), (6, 14), (0, 14 - 10 * sand)], (230, 200, 120), ol=None)
        c.pop()
    # skull
    hy = -184 + nod * 6 + shake
    hxx = 2
    jaw = 10 * mouth + (6 + 4 * math.sin(t * 18) if laugh else 0)
    c.ellipse(hxx + 2, hy + 18 + jaw * 0.6, 17, 9, BONE, w=2)               # jaw
    for k in range(5):
        c.line([(hxx - 8 + k * 5, hy + 12 + jaw * 0.6), (hxx - 8 + k * 5, hy + 18 + jaw * 0.6)], BONE_D, 1.2,
               cap=False)
    if jaw > 1:
        c.ellipse(hxx + 2, hy + 14 + jaw * 0.3, 12, 2 + jaw * 0.4, (70, 40, 60), ol=None)
    c.ellipse(hxx, hy - 4, 30, 26, BONE, w=2.2)
    c.ellipse(hxx, hy + 12, 18, 8, BONE, ol=None)
    # teeth row
    c.rect(hxx - 11, hy + 10, hxx + 13, hy + 16, (252, 250, 240), w=1.5, r=2)
    for k in range(4):
        c.line([(hxx - 6 + k * 6, hy + 10), (hxx - 6 + k * 6, hy + 16)], BONE_D, 1, cap=False)
    # big friendly eye sockets
    for ex in (hxx - 11, hxx + 11):
        c.ellipse(ex, hy - 6, 9, 10, (54, 44, 60), w=1.5)
        if eyes == "closed":
            c.arc(ex, hy - 6, 5, 3, 20, 160, (255, 236, 160), 2)
        elif eyes == "happy":
            c.arc(ex, hy - 3, 5, 5, 200, 340, (255, 236, 160), 2)
        else:
            big = 1.4 if eyes == "wide" else 1.0
            c.circle(ex + 1.5, hy - 5, 3.2 * big, (255, 236, 160), ol=None)
            c.circle(ex + 2.5, hy - 6.5, 1.2, (255, 255, 255), ol=None)
    c.poly([(hxx - 3, hy + 4), (hxx + 3, hy + 4), (hxx, hy - 1)], (70, 56, 70), ol=None)
    c.pop()


def swan(c, x, y, s=1.0, face=1, t=0.0, seed=0.0):
    c.push(x, y + 1.5 * math.sin(t * 1.6 + seed), s, flip=face < 0)
    c.ellipse(0, -10, 34, 14, (252, 252, 250), w=2)
    c.poly([(-30, -12), (-44, -26), (-24, -20)], (252, 252, 250), w=2)
    c.poly([(-14, -16), (14, -30), (18, -14)], (236, 238, 242), w=1.8)
    c.line([(22, -14), (26, -40), (22, -56)], OUT, 9)
    c.line([(22, -14), (26, -40), (22, -56)], (252, 252, 250), 6)
    c.circle(26, -58, 7, (252, 252, 250), w=2)
    c.poly([(30, -61), (42, -56), (30, -54)], (240, 130, 50), w=1.5)
    c.poly([(30, -61), (32, -56), (30, -54)], (40, 36, 40), ol=None)
    c.circle(26, -60, 1.5, OUT, ol=None)
    c.pop()


def fir(c, x, y, s=1.0, col=PINE, dark=PINE_D, snow=True, lights=None, t=0.0, star=False):
    """A Christmas fir tree; lights = list of colours for twinkly bulbs."""
    c.push(x, y, s)
    c.rect(-8, -16, 8, 0, WOOD_D, w=1.5)
    for k, (w, y0, y1) in enumerate(((60, -16, -70), (48, -50, -104), (36, -84, -134), (24, -116, -160))):
        c.poly([(-w, y0), (0, y1), (w, y0)], col, w=2)
        c.poly([(-w, y0), (0, y1), (-w * 0.3, y0)], dark, ol=None)
        if snow:
            c.poly([(-w * 0.45, y1 + (y0 - y1) * 0.55), (0, y1 + 4), (w * 0.45, y1 + (y0 - y1) * 0.55),
                    (0, y1 + (y0 - y1) * 0.4)], SNOW, ol=None)
    if lights:
        rng = np.random.default_rng(int(x) % 97)
        for k in range(18):
            u = rng.random()
            yy = lerp(-24, -140, u)
            ww = lerp(54, 12, u)
            xx = rng.uniform(-ww, ww)
            on = 0.5 + 0.5 * math.sin(t * 3 + k * 1.3)
            cc = lights[k % len(lights)]
            c.circle(xx, yy, 3.5, mix(mix(cc, (90, 90, 90), 0.5), cc, on), ol=None)
    if star:
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = 12 if k % 2 == 0 else 5
            pts.append((math.cos(a) * r, -166 + math.sin(a) * r))
        c.poly(pts, GOLD, w=1.5)
    c.pop()


BULBS = [(255, 90, 90), (255, 220, 90), (120, 200, 255), (140, 230, 140), (255, 160, 220)]


def barge(c, x, y, s=1.0, face=1, t=0.0, trees=True, lantern=1.0):
    """A long, low river barge loaded with Christmas trees; a little cabin and a lantern."""
    c.push(x, y + 2 * math.sin(t * 1.4), s, flip=face < 0)
    hull = (70, 64, 80)
    # trees (lying stacked on deck)
    if trees:
        for row, (yy, n, cc) in enumerate(((-44, 6, PINE_D), (-60, 5, PINE), (-74, 4, PINE_D))):
            for k in range(n):
                px = -230 + row * 30 + k * 64
                c.poly([(px - 6, yy + 10), (px + 60, yy - 8), (px + 64, yy + 12), (px - 4, yy + 16)], cc, w=1.8)
                c.ellipse(px + 30, yy + 2, 22, 5, SNOW, ol=None)
                c.rect(px - 14, yy + 6, px - 2, yy + 13, WOOD_D, w=1.2)
    # cabin at the stern
    c.rect(170, -86, 250, -26, (196, 70, 60), w=2)
    c.poly([(162, -86), (210, -106), (258, -86)], (110, 60, 50), w=2)
    c.rect(162, -90, 258, -86, SNOW, ol=None)
    window(c, 210, -56, 22, 20, lit=lantern > 0.3)
    # chimney with smoke
    c.rect(226, -118, 236, -96, (60, 54, 60), w=1.5)
    # hull
    c.poly([(-280, -30), (270, -30), (290, -10), (260, 14), (-260, 14), (-296, -20)], hull, w=2.5)
    c.rect(-276, -34, 272, -26, (190, 70, 60), w=1.5)
    c.line([(-270, -2), (270, -2)], mix(hull, (255, 255, 255), 0.2), 2, cap=False)
    c.text(-120, -8, "VLTAVA", 11, (236, 220, 180))
    # lantern on a pole at the bow
    c.line([(-270, -30), (-270, -110)], (60, 54, 60), 3)
    c.line([(-270, -110), (-250, -110)], (60, 54, 60), 3, cap=False)
    c.rect(-257, -104, -243, -86, LIGHT if lantern > 0.3 else (200, 200, 190), w=1.5, r=2)
    c.pop()


def stall(c, x, y, s=1.0, roof=(200, 60, 60), wall=(170, 116, 70), sign=None, goods=None, rng_seed=1, lights=True,
          t=0.0):
    """A wooden Christmas-market hut with a snowy pitched roof and fairy lights."""
    rng = np.random.default_rng(rng_seed)
    c.push(x, y, s)
    c.rect(-90, -130, 90, 0, wall, w=2)
    for k in range(6):
        c.line([(-90 + k * 30, -130), (-90 + k * 30, 0)], mix(wall, (0, 0, 0), 0.18), 1.5, cap=False)
    c.rect(-80, -110, 80, -54, (70, 46, 34), w=2)            # serving hatch
    c.rect(-94, -58, 94, -46, mix(wall, (255, 255, 255), 0.2), w=2)
    c.poly([(-112, -126), (0, -196), (112, -126)], roof, w=2)
    c.poly([(-112, -126), (0, -196), (112, -126), (100, -122), (0, -184), (-100, -122)], SNOW, ol=None)
    c.poly([(-60, -160), (0, -196), (60, -160), (0, -178)], SNOW, ol=None)
    if lights:
        for k in range(11):
            u = k / 10
            px = lerp(-104, 104, u)
            py = -126 - 64 * (1 - abs(u - 0.5) * 2) + 6
            on = 0.5 + 0.5 * math.sin(t * 3 + k * 1.7)
            cc = BULBS[k % len(BULBS)]
            c.circle(px, py, 3.2, mix(mix(cc, (80, 80, 80), 0.5), cc, on), ol=None)
    if sign:
        c.rect(-56, -150, 56, -128, (250, 240, 214), w=1.8, r=4)
        c.text(0, -139, sign, 13, (150, 50, 40))
    if goods == "cakes":
        for k in range(4):
            trdelnik(c, -54 + k * 36, -70, 0.55, vertical=True)
    elif goods == "gingerbread":
        for k in range(5):
            gx = -60 + k * 30
            c.circle(gx, -74, 11, (196, 130, 70), w=1.5)
            c.arc(gx, -74, 7, 7, 200, 340, (255, 255, 255), 1.5)
    elif goods == "puppets":
        for k in range(4):
            px = -54 + k * 36
            c.line([(px, -110), (px, -88)], (240, 240, 230), 1, cap=False)
            c.circle(px, -82, 6, WOODSKIN, w=1.2)
            c.rect(px - 6, -76, px + 6, -60, BULBS[k], w=1.2)
    elif goods == "mugs":
        for k in range(5):
            c.rect(-62 + k * 28, -78, -46 + k * 28, -60, (220, 60, 50) if k % 2 else (250, 250, 240), w=1.5, r=2)
    c.pop()


def trdelnik(c, x, y, s=1.0, ang=0.0, vertical=False, bitten=0.0, steam=0.0, t=0.0, length=1.0):
    """A chimney cake: a hollow golden tube of dough rolled in sugar, with spiral grooves."""
    c.push(x, y, s)
    L = 60 * length
    R = 18
    if vertical:
        c.rect(-R, -L, R, 0, (214, 150, 70), w=2, r=4)
        c.ellipse(0, -L, R, 5, (120, 70, 40), w=1.8)
        for k in range(int(5 * length) + 1):
            yy = -6 - k * 11
            c.line([(-R + 1, yy), (R - 1, yy - 6)], (176, 110, 50), 2, cap=False)
        rng = np.random.default_rng(3)
        for k in range(int(20 * length)):
            c.circle(rng.uniform(-R + 3, R - 3), rng.uniform(-L + 3, -3), 1.2, (255, 250, 236), ol=None)
    else:
        ca, sa = math.cos(ang), math.sin(ang)

        def P(u, v):
            return (u * ca - v * sa, u * sa + v * ca)
        c.poly([P(-L / 2, -R), P(L / 2, -R), P(L / 2, R), P(-L / 2, R)], (214, 150, 70), w=2)
        for k in range(int(5 * length) + 1):
            u = -L / 2 + 6 + k * 11
            if u > L / 2 - 4:
                break
            c.line([P(u, -R + 1), P(u + 6, R - 1)], (176, 110, 50), 2, cap=False)
        # open end
        pts = [P(L / 2 + 5 * math.cos(a), R * math.sin(a)) for a in np.linspace(0, math.tau, 16)]
        c.poly(pts, (214, 150, 70), w=1.8)
        pts = [P(L / 2 + 3.5 * math.cos(a), (R - 5) * math.sin(a)) for a in np.linspace(0, math.tau, 16)]
        c.poly(pts, (110, 64, 36), ol=None)
        rng = np.random.default_rng(3)
        for k in range(int(18 * length)):
            c.circle(*P(rng.uniform(-L / 2 + 3, L / 2 - 3), rng.uniform(-R + 3, R - 3)), 1.2, (255, 250, 236),
                     ol=None)
    if steam > 0:
        for k in range(3):
            u = (t * 0.6 + k / 3) % 1.0
            c.circle(-10 + k * 10 + 4 * math.sin(t * 3 + k), -L - 10 - 40 * u, 5 + 6 * u,
                     mix((255, 255, 255), (230, 230, 230), u), ol=None)
    c.pop()


def cake_spit(c, x, y, s=1.0, t=0.0):
    """Chimney cakes turning on spits over glowing coals (the trdelnik grill)."""
    c.push(x, y, s)
    c.rect(-80, -40, 80, 0, (60, 56, 60), w=2)
    for k in range(9):
        cc = mix((255, 120, 40), (255, 220, 120), 0.5 + 0.5 * math.sin(t * 5 + k * 1.3))
        c.circle(-64 + k * 16, -44, 7, cc, ol=None)
    for k, yy in enumerate((-70, -104)):
        c.line([(-90, yy), (90, yy)], (120, 120, 130), 3, cap=False)
        trdelnik(c, -36 + k * 50, yy, 0.8, ang=0.0, t=t)
    c.rect(-94, -110, -86, 0, (80, 76, 80), w=1.5)
    c.rect(86, -110, 94, 0, (80, 76, 80), w=1.5)
    c.pop()


def musician_dog(c, x, y, s=1.0, face=1, t=0.0, play=1.0):
    """A shaggy old street-musician dog with an accordion and a hat."""
    c.push(x, y, s, flip=face < 0)
    fur, dark = (176, 140, 104), (130, 96, 70)
    sq = 1 + 0.25 * math.sin(t * 6) * play
    # sitting body
    c.ellipse(0, -40, 40, 40, fur, w=2)
    c.ellipse(-20, -6, 16, 8, fur, w=2)
    c.ellipse(24, -6, 16, 8, fur, w=2)
    # accordion
    w = 26 * sq
    c.rect(-6 - w, -70, -6 + w, -24, (200, 40, 50), w=2)
    for k in range(5):
        xx = -6 - w + (k + 1) * 2 * w / 6
        c.line([(xx, -70), (xx, -24)], (130, 20, 30), 2, cap=False)
    c.rect(-6 - w - 10, -72, -6 - w, -22, (250, 250, 240), w=1.5)
    c.rect(-6 + w, -72, -6 + w + 10, -22, (250, 250, 240), w=1.5)
    # head
    c.ellipse(10, -96, 28, 24, fur, w=2)
    c.ellipse(-14, -90, 10, 22, dark, w=2)          # floppy ear
    c.ellipse(34, -90, 14, 9, (200, 170, 136), w=1.5)
    c.circle(46, -92, 5, (40, 34, 40), ol=None)
    c.arc(18, -102, 4, 3, 200, 340, OUT, 2)
    c.arc(30, -102, 4, 3, 200, 340, OUT, 2)
    # hat
    c.ellipse(10, -118, 30, 6, (60, 56, 66), w=2)
    c.rect(-6, -144, 26, -118, (60, 56, 66), w=2)
    c.rect(-6, -126, 26, -120, (200, 40, 50), ol=None)
    c.pop()
    # a hat on the ground for coins
    c.ellipse(x + 60 * face * s, y - 4 * s, 22 * s, 7 * s, (60, 56, 66), w=2)
    c.circle(x + 56 * face * s, y - 7 * s, 3 * s, GOLD, ol=None)


def notes(c, x, y, t, k=1.0, col=(255, 250, 220)):
    for i in range(3):
        u = (t * 0.6 + i / 3) % 1.0
        nx, ny = x + 30 * u + 10 * math.sin(t * 3 + i), y - 70 * u
        r = 5 * k
        if r < 1:
            continue
        cc = mix(col, (200, 200, 220), u)
        c.ellipse(nx, ny, r * 1.2, r, cc, w=1.5)
        c.line([(nx + r, ny), (nx + r, ny - 16 * k)], cc, 2, cap=False)


def snowfall(c, t, seed=1, n=70, w=1280, h=720, speed=40.0, size=1.0, drift=15.0, col=(255, 255, 255)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(1.2, 3.4) * size
        v = speed * (0.6 + r / 3.4)
        ph = rng.uniform(0, math.tau)
        y = (y0 + v * t) % (h + 20) - 10
        x = (x0 + drift * math.sin(t * 0.8 + ph) + 8 * t) % (w + 20) - 10
        c.circle(x, y, r, col, ol=None)


def puppet_theatre(c, x, y, s=1.0, curtain=0.0, t=0.0):
    """Back part of a little wooden marionette theatre: painted frame, stage floor, backdrop.

    curtain: 0 closed .. 1 open. Returns nothing; front curtains drawn by puppet_curtains().
    Local: stage floor at y=-120, opening from x=-200..200, y=-420..-120.
    """
    c.push(x, y, s)
    # booth
    c.rect(-250, -500, 250, 0, (150, 40, 50), w=3)
    c.rect(-210, -430, 210, -120, (60, 90, 150), w=2.5)          # backdrop: night sky over Prague
    for k in range(9):
        px = -190 + k * 46
        c.poly([(px, -120), (px + 10, -200 - (k % 3) * 30), (px + 20, -120)], (40, 60, 110), ol=None)
    c.circle(130, -360, 22, (250, 240, 200), ol=None)
    c.rect(-210, -132, 210, -120, WOOD, w=2)                      # stage floor
    # painted top board
    c.poly([(-260, -500), (-200, -560), (200, -560), (260, -500)], (220, 170, 60), w=3)
    c.rect(-120, -556, 120, -508, (250, 236, 200), w=2, r=8)
    c.text(0, -532, "DIVADLO", 22, (150, 40, 50))
    c.circle(-220, -520, 12, GOLD, w=2)
    c.circle(220, -520, 12, GOLD, w=2)
    c.rect(-250, -120, 250, 0, (120, 30, 40), w=3)
    for k in range(5):
        c.circle(-180 + k * 90, -60, 18, (220, 170, 60), w=2)
    c.pop()


def puppet_curtains(c, x, y, s=1.0, curtain=0.0):
    c.push(x, y, s)
    k = curtain
    for side in (-1, 1):
        inner = side * lerp(0, 196, k)
        outer = side * 214
        pts = [(outer, -432), (inner, -432)]
        for j in range(9):
            u = j / 8
            pts.append((inner + side * 30 * k * u ** 2 + 4 * math.sin(u * 9), lerp(-432, -118, u)))
        pts.append((outer, -118))
        c.poly(pts, (200, 40, 50), w=2)
        for j in range(4):
            fx = lerp(inner, outer, (j + 0.5) / 4)
            c.line([(fx, -428), (fx + side * 6, -122)], (160, 26, 36), 2, cap=False)
    c.rect(-216, -446, 216, -424, (220, 170, 60), w=2)
    c.pop()


def puppet_cat(c, x, y, s=1.0, t=0.0, walk=0.0, mouth=0.0):
    """A marionette of Whiskers: blocky orange wooden cat with stripes, on strings."""
    c.push(x, y, s)
    body, dark = (243, 152, 62), (205, 108, 38)
    sw = math.sin(walk)
    for dx, ph in ((-24, 0), (24, math.pi)):
        c.stroke([(dx, -30), (dx + 6 * math.sin(walk + ph), 0)], dark, 8)
    c.rect(-36, -60, 36, -24, body, w=2, r=10)
    for dx in (-18, 0, 18):
        c.line([(dx, -60), (dx + 3, -48)], dark, 4)
    # the round "chimney cake" belly joke: a little tube on its head
    c.circle(44, -72, 20, body, w=2)
    c.poly([(30, -84), (32, -104), (44, -90)], body, w=1.8)
    c.poly([(46, -90), (56, -104), (60, -82)], body, w=1.8)
    c.circle(40, -76, 2.5, OUT, ol=None)
    c.circle(52, -76, 2.5, OUT, ol=None)
    c.circle(50, -68, 3, D.NOSE, ol=None)
    if mouth > 0.1:
        c.ellipse(48, -60, 5, 3 + 3 * mouth, D.MOUTH, w=1.2)
    c.stroke([(-36, -44), (-54, -64 + 6 * sw)], body, 7)
    c.pop()
    # strings and the floating control cross
    bx, by = x + 6 * s, y - 190 * s + 3 * math.sin(t * 2)
    for px, py in ((-24, -30), (24, -30), (44, -92), (-36, -50)):
        c.line([(x + px * s, y + py * s), (bx + px * 0.4 * s, by)], (250, 246, 236), 1.0, cap=False)
    c.rect(bx - 30 * s, by - 3 * s, bx + 30 * s, by + 3 * s, WOOD, w=1.5)
    c.rect(bx - 3 * s, by - 16 * s, bx + 3 * s, by + 14 * s, WOOD, w=1.5)


def puppet_bones(c, x, y, s=1.0, t=0.0):
    """A little marionette skeleton for the show (Mr Bones' tiny double)."""
    bones(c, x, y, s, 1, t, ring=0.6, eyes="happy")
    bx, by = x, y - 240 * s + 3 * math.sin(t * 2.2)
    for px, py in ((-26, -104), (40, -104), (0, -200)):
        c.line([(x + px * s, y + py * s), (bx + px * 0.4 * s, by)], (250, 246, 236), 1.0, cap=False)
    c.rect(bx - 30 * s, by - 3 * s, bx + 30 * s, by + 3 * s, WOOD, w=1.5)


def kid_back(c, x, y, s=1.0, col=(150, 120, 100), kind=0, t=0.0, bounce=0.0, ears=0):
    """An audience member seen from behind (little animals in hats and scarves)."""
    c.push(x, y - abs(math.sin(t * 8 + x)) * 6 * bounce, s)
    c.ellipse(0, -30, 30, 32, col, w=2)
    scarf = BULBS[kind % len(BULBS)]
    c.rect(-22, -56, 22, -46, scarf, w=1.5, r=4)
    hy = -78
    if ears == 0:       # cat
        c.poly([(-24, hy - 6), (-18, hy - 40), (-4, hy - 22)], col, w=2)
        c.poly([(4, hy - 22), (18, hy - 40), (24, hy - 6)], col, w=2)
    elif ears == 1:     # rabbit
        c.ellipse(-10, hy - 36, 7, 22, col, w=2)
        c.ellipse(10, hy - 36, 7, 22, col, w=2)
    elif ears == 2:     # bear
        c.circle(-18, hy - 18, 9, col, w=2)
        c.circle(18, hy - 18, 9, col, w=2)
    c.circle(0, hy, 26, col, w=2)
    if kind % 3 == 0:   # bobble hat
        c.poly([(-24, hy - 6), (0, hy - 40), (24, hy - 6)], scarf, w=2)
        c.circle(0, hy - 42, 7, (255, 255, 255), w=1.5)
    c.pop()


def chimney_soot(c, x, y, k, seed=2):
    """A billowing soot cloud, k=0 (burst) .. 1 (gone)."""
    if not 0 <= k < 1:
        return
    rng = np.random.default_rng(seed)
    a = 1 - k
    for i in range(16):
        ang = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        v = rng.uniform(40, 170)
        px = x + math.cos(ang) * v * (0.3 + k)
        py = y + math.sin(ang) * v * (0.3 + k) * 0.8 - 30 * k
        r = rng.uniform(16, 36) * (0.5 + k) * a + 2
        c.circle(px, py, r, mix((70, 66, 72), (140, 136, 140), k), ol=None)


def fireplace(c, x, y, t=0.0, fire=1.0, s=1.0):
    """A brick fireplace with a mantel, set against the wall (floor at y)."""
    c.push(x, y, s)
    brick = (178, 92, 70)
    c.rect(-130, -300, 130, 0, brick, w=2.5)
    for r in range(12):
        off = 0 if r % 2 else 18
        yy = -300 + r * 25
        c.line([(-130, yy), (130, yy)], mix(brick, (0, 0, 0), 0.2), 1.2, cap=False)
        for k in range(8):
            xx = -130 + off + k * 36
            if -130 < xx < 130:
                c.line([(xx, yy), (xx, yy + 25)], mix(brick, (0, 0, 0), 0.2), 1.2, cap=False)
    c.rect(-150, -210, 150, -190, (120, 80, 60), w=2.5)            # mantel
    c.rect(-80, -170, 80, 0, (40, 30, 34), w=2.5)
    c.ellipse(0, -170, 80, 40, (40, 30, 34), w=2.5)
    c.rect(-78, -172, 78, -150, (40, 30, 34), ol=None)
    # logs and fire
    c.rect(-50, -22, 50, -8, WOOD, w=1.5, r=6)
    c.rect(-40, -32, 44, -20, WOOD_D, w=1.5, r=6)
    if fire > 0:
        c.glow(0, -50, 90 * fire, 70 * fire, (255, 200, 110), (60, 40, 40), steps=6)
        for k in range(5):
            fx = -36 + k * 18
            h = (40 + 30 * math.sin(t * 7 + k * 1.7)) * fire
            c.poly([(fx - 14, -24), (fx + 2 * math.sin(t * 9 + k), -24 - h), (fx + 14, -24)], (250, 140, 50), ol=None)
            c.poly([(fx - 7, -24), (fx + 2 * math.sin(t * 11 + k), -24 - h * 0.6), (fx + 7, -24)], (255, 222, 110),
                   ol=None)
    c.pop()
