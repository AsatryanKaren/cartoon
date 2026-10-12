"""Dublin and the west of Ireland: places, things and new characters (flat style, local space).

Characters are drawn in local space like draw.cat: origin between the feet,
facing right, y up is negative.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import W, H, SS, OUT, lerp, clamp, mix, ease

# ------------------------------------------------------------------ colours
GRASS = (110, 178, 84)
GRASS_D = (78, 146, 66)
GRASS_L = (150, 205, 104)
STONE = (168, 166, 158)
STONE_D = (120, 118, 114)
STONE_L = (200, 198, 188)
BRICK = (170, 82, 64)
BRICK_D = (136, 62, 50)
RIVER = (74, 104, 120)
RIVER_D = (52, 78, 96)
RIVER_L = (140, 170, 180)
SEA = (52, 104, 150)
SEA_D = (36, 76, 120)
FOAM = (236, 244, 248)
CREAM = (238, 228, 200)
CREAM_D = (206, 192, 160)
WOOD = (122, 78, 48)
WOOD_D = (90, 56, 36)
GOLD = (240, 196, 70)
DOOR_COLS = [(206, 46, 52), (40, 90, 170), (246, 196, 50), (40, 130, 84), (240, 120, 40), (120, 60, 150),
             (30, 150, 160), (220, 90, 140)]
RAINBOW = [(232, 64, 64), (246, 146, 50), (250, 222, 70), (90, 190, 90), (70, 140, 220), (90, 80, 180),
           (150, 90, 190)]


# ------------------------------------------------------------- small things

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


def bottle(c, x, y, s=1.0, ang=0.0, map_in=True, cork=True):
    """A green glass bottle lying on its side (ang in degrees), with a rolled map inside."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def R(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)

    glass = (90, 170, 120)
    body = [R(px, py) for px, py in ((-40, -16), (18, -16), (30, -8), (44, -6), (44, 6), (30, 8), (18, 16),
                                     (-40, 16), (-44, 10), (-44, -10))]
    c.poly(body, glass, w=2.5)
    if map_in:
        c.poly([R(-30, -8), R(14, -8), R(14, 8), R(-30, 8)], (240, 222, 170), w=1.5)
        c.line([R(-8, -8), R(-8, 8)], (200, 60, 60), 2, cap=False)
    c.poly([R(-38, -12), R(10, -12), R(10, -8), R(-38, -8)], (190, 235, 205), ol=None)
    if cork:
        c.poly([R(44, -6), R(54, -5), R(54, 5), R(44, 6)], (190, 140, 90), w=2)


def map_img(w=520, h=380, path=1.0, t=0.0):
    """The old map from the bottle: Ireland, a dotted path from Dublin west to the cliffs, a rainbow."""
    from draw import Canvas
    c = Canvas(Image.new("RGB", (w * SS, h * SS), (238, 222, 176)), size=(w, h))
    c.rect(6, 6, w - 6, h - 6, None, ol=(170, 130, 80), w=3, r=8)
    sea = (190, 214, 214)
    c.rect(20, 20, w - 20, h - 20, sea, ol=None, r=6)
    for k in range(6):
        y = 50 + k * 55
        c.arc(80 + 60 * (k % 3), y, 14, 5, 200, 340, (150, 184, 190), 2)
    # Ireland (a friendly blobby outline)
    isl = [(250, 46), (300, 40), (340, 60), (360, 96), (352, 140), (372, 186), (366, 240), (340, 290),
           (296, 322), (232, 332), (176, 318), (150, 290), (166, 256), (136, 232), (150, 200), (128, 170),
           (150, 140), (138, 110), (172, 92), (196, 60)]
    c.poly(isl, (150, 200, 120), ol=(90, 120, 70), w=2.5)
    for px, py in ((210, 140), (270, 220), (230, 270), (300, 120)):
        c.circle(px, py, 6, (110, 170, 96), ol=None)
    # Dublin and the cliffs
    dx, dy = 352, 190
    cx, cy = 150, 230
    c.circle(dx, dy, 7, (200, 60, 60), w=2)
    c.text(dx + 4, dy - 22, "Dublin", 14, (90, 60, 40))
    # dotted path
    n = 18
    for k in range(int(n * path)):
        u = k / (n - 1)
        px = lerp(dx, cx, u)
        py = lerp(dy, cy, u) - 40 * math.sin(math.pi * u)
        c.circle(px, py, 2.6, (150, 70, 50), ol=None)
    # the rainbow ending at the cliffs
    for i, col in enumerate(RAINBOW):
        c.arc(cx + 50, cy + 10, 70 - i * 4, 60 - i * 4, 180, 360, col, 4)
    c.line([(cx - 9, cy - 9), (cx + 9, cy + 9)], (200, 40, 40), 4)
    c.line([(cx - 9, cy + 9), (cx + 9, cy - 9)], (200, 40, 40), 4)
    c.text(w / 2, h - 40, "Follow the rainbow!", 20, (110, 70, 40))
    return c.img


def soda_bread(c, x, y, s=1.0, bitten=0.0):
    c.push(x, y, s)
    crust, inner = (200, 150, 90), (236, 214, 170)
    c.ellipse(0, -18, 40, 24, crust, w=2.5)
    c.ellipse(-6, -24, 24, 10, mix(crust, (255, 255, 255), 0.25), ol=None)
    c.line([(-22, -30), (22, -8)], (150, 104, 60), 3, cap=False)
    c.line([(-22, -8), (22, -30)], (150, 104, 60), 3, cap=False)
    if bitten > 0:
        for k in range(int(1 + 3 * bitten)):
            c.circle(30 - k * 8, -26 + k * 2, 10, inner, ol=None)
    c.pop()


def clover(c, x, y, s=1.0, ang=0.0, col=(70, 170, 70)):
    c.push(x, y, s)
    a = math.radians(ang)
    c.line([(0, 0), (6 * math.sin(a) - 2, 22)], (60, 130, 60), 3)
    for k in range(4):
        aa = a + k * math.pi / 2 + math.pi / 4
        for side in (-0.42, 0.42):
            px = math.cos(aa + side) * 9
            py = math.sin(aa + side) * 9
            c.circle(px, py, 6.2, col, w=1.5)
    c.circle(0, 0, 2.5, mix(col, (255, 255, 255), 0.3), ol=None)
    c.pop()


def chowder_pot(c, x, y, s=1.0, t=0.0, steam=1.0, glow=1.0):
    c.push(x, y, s)
    c.ellipse(0, -40, 70, 50, (50, 46, 50), w=3)
    c.ellipse(0, -76, 66, 14, (70, 64, 70), w=3)
    c.ellipse(0, -76, 58, 10, mix((240, 180, 70), (255, 220, 120), 0.5 + 0.5 * math.sin(t * 2)), ol=None)
    for k in range(4):
        bx = -40 + k * 26 + 6 * math.sin(t * 3 + k)
        c.circle(bx, -77, 3 + 2 * abs(math.sin(t * 4 + k)), (255, 236, 160), ol=None)
    c.arc(0, -90, 70, 40, 200, 340, (60, 56, 60), 3)
    if steam > 0:
        for k in range(3):
            u = (t * 0.4 + k / 3) % 1
            sx = -24 + 24 * k + 10 * math.sin(t * 2 + k)
            c.circle(sx, -100 - 70 * u, 8 + 8 * u, mix((255, 255, 255), (220, 210, 200), u), ol=None)
    c.pop()


# ----------------------------------------------------------------- rainbow

def rainbow(img, cx, cy, r, band=16, alpha=0.6, reveal=1.0, a0=180.0, a1=360.0):
    """Translucent rainbow arc drawn straight onto a supersampled image.

    reveal sweeps the arc in from a0 toward a1 (0..1)."""
    if alpha <= 0.01 or reveal <= 0.01:
        return
    end = a0 + (a1 - a0) * clamp(reveal)
    pad = int(band * len(RAINBOW) + 4)
    x0, y0 = int((cx - r - pad) * SS), int((cy - r - pad) * SS)
    x1, y1 = int((cx + r + pad) * SS), int((cy + pad) * SS)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.size[0], x1), min(img.size[1], y1)
    if x1 <= x0 or y1 <= y0:
        return
    layer = Image.new("RGB", (x1 - x0, y1 - y0))
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    ld, md = ImageDraw.Draw(layer), ImageDraw.Draw(mask)
    for i, col in enumerate(RAINBOW):
        rr = (r - i * band) * SS
        box = [cx * SS - rr - x0, cy * SS - rr - y0, cx * SS + rr - x0, cy * SS + rr - y0]
        ld.arc(box, a0, end, fill=col, width=int(band * SS) + 2)
        md.arc(box, a0, end, fill=int(255 * alpha), width=int(band * SS) + 2)
    img.paste(layer, (x0, y0), mask)


# ---------------------------------------------------------------- landscape

def stone_wall(c, pts, s=1.0, seed=0, col=STONE, dark=STONE_D):
    """A dry-stone wall along a polyline of ground points."""
    rng = np.random.default_rng(seed)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        L = math.hypot(xb - xa, yb - ya)
        n = max(1, int(L / (14 * s)))
        for row in range(2):
            for k in range(n):
                u = (k + 0.5 * (row % 2)) / n
                px, py = lerp(xa, xb, u), lerp(ya, yb, u) - (8 + 12 * row) * s
                rx, ry = rng.uniform(7, 10) * s, rng.uniform(5, 7) * s
                cc = mix(col, dark, rng.uniform(0, 0.5))
                c.ellipse(px, py, rx, ry, cc, ol=dark, w=1.2 * s)


def round_tower(c, x, base, s=1.0, col=STONE, dark=STONE_D, ol=OUT):
    c.push(x, base, s)
    c.poly([(-28, 0), (-22, -300), (22, -300), (28, 0)], col, ol=ol)
    c.poly([(8, 0), (10, -300), (22, -300), (28, 0)], dark, ol=None)
    c.poly([(-26, -298), (0, -370), (26, -298)], mix(dark, (60, 60, 70), 0.3), ol=ol)
    for wy in (-260, -180, -110):
        c.rect(-5, wy - 14, 5, wy, (60, 56, 60), ol=None)
    c.rect(-7, -64, 7, -40, (60, 56, 60), ol=None, r=5)   # the high door
    c.pop()


def castle_ruin(c, x, base, s=1.0, col=STONE, dark=STONE_D, ivy=True, ol=OUT):
    c.push(x, base, s)
    # main keep with a broken top
    c.poly([(-80, 0), (-80, -230), (-60, -230), (-60, -245), (-40, -245), (-40, -230), (-20, -230), (0, -205),
            (16, -215), (40, -180), (60, -190), (60, -150), (80, -150), (80, 0)], col, ol=ol)
    c.poly([(40, 0), (40, -180), (60, -190), (60, -150), (80, -150), (80, 0)], dark, ol=None)
    for wx, wy in ((-50, -170), (-10, -120), (-50, -80), (20, -150)):
        c.rect(wx - 7, wy - 22, wx + 7, wy, (60, 58, 64), ol=None, r=6)
    c.rect(-22, -50, 6, 0, (60, 58, 64), ol=None, r=12)
    # a broken side wall
    c.poly([(80, 0), (80, -90), (110, -80), (130, -96), (150, -60), (170, -64), (170, 0)], col, ol=ol)
    if ivy:
        for k, (ix, iy, r) in enumerate(((-78, -40, 22), (-70, -90, 16), (78, -30, 18), (160, -20, 16),
                                         (-60, -200, 12))):
            c.circle(ix, iy, r, (70, 140, 70), ol=None)
            c.circle(ix + 6, iy - 6, r * 0.6, (90, 162, 82), ol=None)
    c.pop()


def cottage(c, x, base, s=1.0, wall=(246, 244, 236), lit=0.0, smoke_t=None):
    """A whitewashed cottage with a thatched roof and a red door."""
    c.push(x, base, s)
    c.rect(-110, -110, 110, 0, wall)
    c.poly([(-126, -100), (-90, -176), (90, -176), (126, -100)], (196, 160, 90))
    for k in range(9):
        xx = -100 + k * 25
        c.line([(xx, -170), (xx - 8, -106)], (170, 132, 70), 2, cap=False)
    c.rect(66, -200, 88, -164, STONE)
    c.rect(-18, -76, 18, 0, (200, 44, 50))
    win = mix((80, 90, 120), (255, 214, 120), lit)
    for wx in (-70, 60):
        c.rect(wx - 20, -84, wx + 20, -46, win, w=2.5)
        c.line([(wx, -84), (wx, -46)], wall, 2, cap=False)
    c.pop()
    if smoke_t is not None:
        for k in range(4):
            u = (smoke_t * 0.25 + k / 4) % 1
            c.circle(x + 77 * s + 30 * u * s, base - 210 * s - 90 * u * s, (8 + 14 * u) * s,
                     mix((240, 240, 240), (200, 206, 214), u), ol=None)


def sheep(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, graze=0.0, seed=0.0, lamb=False, baa=0.0, eyes="open",
          clover_on=False, wool=(246, 246, 240)):
    """Fluffy white sheep (or lamb) with a black face and legs."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    black = (48, 44, 50)
    for lx, ph in ((-30, 0), (-14, math.pi), (18, math.pi), (32, 0)):
        sw = math.sin(walk + ph) * 6 if walk else 0
        c.stroke([(lx, -30), (lx + sw, 0)], black, 7)
    for dx, dy, r in ((-34, -50, 20), (-14, -62, 22), (10, -62, 22), (30, -52, 20), (-24, -38, 18), (20, -38, 18),
                      (0, -44, 24)):
        c.circle(dx, dy, r, wool, w=2.5)
    for dx, dy, r in ((-34, -50, 16), (-14, -62, 18), (10, -62, 18), (30, -52, 16), (0, -48, 22)):
        c.circle(dx, dy, r, wool, ol=None)
    hx = 52
    hy = -54 + 22 * graze + 2 * math.sin(t * 2 + seed)
    c.ellipse(hx - 14, hy - 8, 12, 5, black, w=2)              # ear
    c.ellipse(hx, hy, 15, 19 if not lamb else 16, black, w=2)
    c.circle(hx - 4, hy - 16, 9, wool, ol=None)                # woolly top knot
    if eyes == "closed":
        c.arc(hx + 3, hy - 4, 4, 3, 20, 160, (255, 255, 255), 2)
    elif eyes == "happy":
        c.arc(hx + 3, hy - 2, 4, 4, 200, 340, (255, 255, 255), 2)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        c.circle(hx + 4, hy - 4, 4.5 * big, (255, 255, 255), ol=None)
        c.circle(hx + 5, hy - 4, 2.3 * big, (30, 26, 30), ol=None)
    if baa > 0.05:
        c.ellipse(hx + 6, hy + 12, 5, 2 + 5 * baa, D.MOUTH, w=1.5)
    if clover_on:
        clover(c, -10, -78, 0.8)
    c.pop()


def pony(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, seed=0.7):
    """A small dappled grey Connemara pony."""
    c.push(x, y, s, flip=face < 0)
    body, dark, mane = (196, 192, 196), (150, 146, 154), (90, 84, 96)
    by = -96
    c.stroke([(-74, by - 10), (-96, by + 20 + 6 * math.sin(t * 3 + seed)), (-92, by + 50)], mane, 12)

    def leg(lx, ph, col):
        sw = math.sin(walk + ph) if walk else 0.0
        lift = -max(0.0, math.cos(walk + ph)) * 10 if walk else 0.0
        knee = (lx + sw * 10, by + 50)
        foot = (lx + sw * 16, lift)
        c.stroke([(lx, by + 10), knee, foot], col, 13)
        c.rect(foot[0] - 8, foot[1] - 8, foot[0] + 8, foot[1], (60, 50, 50), w=2)

    leg(-56, math.pi, dark)
    leg(50, 0, dark)
    c.ellipse(0, by, 80, 38, body)
    for dx, dy in ((-30, -10), (10, 6), (36, -14), (-50, 8)):
        c.circle(dx, by + dy, 7, dark, ol=None)
    leg(-44, 0, body)
    leg(62, math.pi, body)
    # neck and head
    c.poly([(48, by - 26), (86, by - 86), (112, by - 74), (78, by + 10)], body)
    c.stroke([(56, by - 30), (84, by - 84)], mane, 10)
    c.ellipse(112, by - 68, 30, 18, body)
    c.ellipse(132, by - 62, 14, 12, (170, 164, 170), ol=None)
    c.circle(138, by - 64, 2.5, OUT, ol=None)
    c.poly([(90, by - 84), (96, by - 104), (102, by - 82)], body, w=2)
    if D.blink(t, seed):
        c.arc(108, by - 74, 4, 3, 20, 160, OUT, 2)
    else:
        c.circle(108, by - 74, 4, (30, 26, 30), ol=None)
        c.circle(109, by - 75.5, 1.3, (255, 255, 255), ol=None)
    # harness
    c.line([(60, by - 20), (60, by + 26)], (150, 40, 40), 5, cap=False)
    c.line([(100, by - 80), (128, by - 56)], (150, 40, 40), 3, cap=False)
    c.pop()


def caravan(c, x, y, s=1.0, t=0.0, roll=0.0, smoke=True):
    """A painted barrel-top caravan, facing right (shafts to the right). y = ground."""
    c.push(x, y, s)
    red, green, yellow = (196, 48, 48), (44, 120, 80), (246, 200, 60)
    # shafts toward the pony
    c.line([(150, -66), (300, -76)], WOOD_D, 6)
    # wheels (back one first)
    for wx, r in ((-110, 56), (110, 46)):
        c.circle(wx, -r, r, red, w=3)
        c.circle(wx, -r, r - 8, mix(red, (255, 255, 255), 0.15), ol=None)
        for k in range(10):
            a = roll + k * math.tau / 10
            c.line([(wx, -r), (wx + math.cos(a) * (r - 6), -r + math.sin(a) * (r - 6))], yellow, 3, cap=False)
        c.circle(wx, -r, 9, yellow, w=2)
    # body
    c.rect(-160, -150, 150, -70, red, w=3, r=4)
    c.rect(-160, -84, 150, -70, green, w=2)
    for k in range(6):
        xx = -140 + k * 52
        c.circle(xx, -77, 3, yellow, ol=None)
    # barrel roof
    c.poly([(-170, -150)] + [(-170 + 330 * u, -150 - 110 * math.sin(math.pi * u) ** 0.7) for u in np.linspace(0, 1, 16)] +
           [(160, -150)], green, w=3)
    for u in (0.2, 0.4, 0.6, 0.8):
        xx = -170 + 330 * u
        c.line([(xx, -150), (xx, -150 - 106 * math.sin(math.pi * u) ** 0.7)], yellow, 2, cap=False)
    # window with flowers, decoration
    c.rect(-70, -136, -10, -96, (250, 230, 150), w=2.5, r=4)
    c.line([(-40, -136), (-40, -96)], red, 2, cap=False)
    for k, col in enumerate(((240, 90, 140), (250, 200, 60), (240, 90, 140))):
        c.circle(-60 + k * 20, -96, 6, col, w=1.5)
    for k in range(4):
        c.circle(40 + k * 26, -112, 7, yellow, w=1.5)
        c.circle(40 + k * 26, -112, 3, red, ol=None)
    # chimney
    c.rect(-110, -248, -94, -214, (60, 60, 66), w=2)
    if smoke:
        for k in range(4):
            u = (t * 0.35 + k / 4) % 1
            c.circle(-102 - 40 * u, -258 - 70 * u, 6 + 12 * u, mix((245, 245, 245), (210, 214, 220), u), ol=None)
    # front seat board
    c.rect(130, -112, 176, -104, WOOD, w=2)
    c.pop()


def ferry(c, x, y, s=1.0, t=0.0, smoke=True, riders=None):
    """A big green-and-white ferry, bow to the right; y = waterline."""
    c.push(x, y, s)
    green, dgreen, white = (40, 140, 90), (26, 100, 66), (246, 248, 244)
    # hull
    c.poly([(-360, -70), (330, -70), (420, -110), (380, 10), (-340, 10), (-370, -20)], green, w=3)
    c.poly([(-360, -20), (390, -20), (380, 10), (-340, 10)], dgreen, ol=None)
    c.line([(-360, -70), (420, -110)], white, 3, cap=False)
    c.text(120, -44, "IRISH SEA FERRY", 18, white)
    # decks
    c.rect(-300, -150, 260, -70, white, w=3, r=6)
    c.rect(-240, -220, 160, -150, white, w=3, r=6)
    c.rect(-150, -270, 40, -220, white, w=3, r=6)
    for row, (x0, x1, yy) in enumerate(((-280, 240, -118), (-220, 140, -190))):
        for xx in range(int(x0), int(x1), 36):
            c.rect(xx, yy - 12, xx + 22, yy + 8, (90, 140, 190), w=1.5, r=3)
    c.rect(-130, -262, 20, -240, (90, 140, 190), w=1.5, r=3)
    # funnel with a shamrock
    c.poly([(-60, -270), (-50, -340), (10, -340), (20, -270)], green, w=3)
    c.rect(-56, -352, 6, -334, (40, 40, 44), w=2)
    clover(c, -20, -300, 1.1, col=(250, 250, 240))
    if smoke:
        for k in range(5):
            u = (t * 0.3 + k / 5) % 1
            c.circle(-25 - 160 * u, -370 - 50 * u, 12 + 22 * u, mix((240, 240, 240), (200, 206, 214), u), ol=None)
    # rail on the front deck
    c.line([(260, -100), (360, -110)], white, 3, cap=False)
    for k in range(5):
        xx = 270 + 20 * k
        c.line([(xx, -102 - 2 * k), (xx, -84 - 2 * k)], white, 2, cap=False)
    c.pop()


# ------------------------------------------------------------------ Dublin

def georgian_house(c, x, base, w=230, h=360, brick=BRICK, door=(206, 46, 52), seed=0):
    """One Dublin Georgian terrace house: brick, sash windows, a bright door with a fanlight."""
    rng = np.random.default_rng(seed)
    c.rect(x, base - h, x + w, base, brick, w=2.5)
    # brick texture
    for k in range(int(h / 16)):
        yy = base - 16 * k
        c.line([(x + 2, yy), (x + w - 2, yy)], mix(brick, BRICK_D, 0.5), 1, cap=False)
    # parapet
    c.rect(x - 2, base - h - 14, x + w + 2, base - h, mix(brick, (60, 40, 40), 0.25), w=2.5)
    # windows: three floors of tall sashes
    for fl, (wy, wh) in enumerate(((base - h + 40, 56), (base - h + 120, 80), (base - h + 220, 74))):
        for k in range(2):
            wx = x + w * (0.25 + 0.5 * k)
            c.rect(wx - 22, wy, wx + 22, wy + wh, (244, 242, 236), w=2)
            c.rect(wx - 17, wy + 5, wx + 17, wy + wh - 5, (80, 104, 140), ol=None)
            c.line([(wx - 17, wy + wh / 2), (wx + 17, wy + wh / 2)], (244, 242, 236), 3, cap=False)
            c.line([(wx, wy + 5), (wx, wy + wh - 5)], (244, 242, 236), 2, cap=False)
            c.line([(wx - 10, wy + 10), (wx - 2, wy + 22)], (150, 176, 206), 2, cap=False)
            if fl == 1 and rng.random() < 0.6:
                c.rect(wx - 26, wy + wh, wx + 26, wy + wh + 8, (40, 40, 44), w=1.5)   # little iron balcony
                for j in range(7):
                    c.line([(wx - 24 + 8 * j, wy + wh), (wx - 24 + 8 * j, wy + wh + 8)], (40, 40, 44), 1.5,
                           cap=False)
    # the door, fanlight, columns and steps
    dx = x + w / 2
    c.rect(dx - 62, base - 118, dx + 62, base - 10, (236, 232, 222), w=2)
    for side in (-1, 1):
        c.rect(dx + side * 50 - 8, base - 116, dx + side * 50 + 8, base - 12, (250, 248, 240), w=1.5)
    c.ellipse(dx, base - 114, 40, 30, (236, 232, 222), w=2)
    c.ellipse(dx, base - 114, 32, 24, (255, 226, 140), w=1.5)
    for k in range(7):
        a = math.pi + k * math.pi / 6
        c.line([(dx, base - 114), (dx + math.cos(a) * 31, base - 114 + math.sin(a) * 23)], (236, 232, 222), 1.5,
               cap=False)
    c.rect(dx - 32, base - 114, dx + 32, base - 12, (236, 232, 222), ol=None)
    c.rect(dx - 28, base - 112, dx + 28, base - 12, door, w=2)
    for py in (-100, -62):
        c.rect(dx - 22, base + py, dx - 4, base + py + 30, mix(door, (0, 0, 0), 0.15), w=1.2)
        c.rect(dx + 4, base + py, dx + 22, base + py + 30, mix(door, (0, 0, 0), 0.15), w=1.2)
    c.circle(dx, base - 70, 5, GOLD, w=1.5)     # brass knocker
    c.circle(dx + 18, base - 54, 3, GOLD, ol=None)
    c.rect(dx - 44, base - 12, dx + 44, base, (200, 196, 188), w=1.5)
    # railings
    for xx in range(int(x + 4), int(dx - 50), 10):
        c.line([(xx, base - 4), (xx, base - 40)], (40, 40, 44), 2, cap=False)
    for xx in range(int(dx + 54), int(x + w - 2), 10):
        c.line([(xx, base - 4), (xx, base - 40)], (40, 40, 44), 2, cap=False)


def hapenny_bridge(c, x0, x1, deck, s=1.0, col=(246, 246, 242), shade=(196, 200, 206), lamps=True, lit=0.0):
    """The Ha'penny Bridge: a shallow white cast-iron arch with lattice sides and three lamp arches.

    deck(u) gives the deck height at fraction u (it rises gently to the middle)."""
    n = 40
    top = [(lerp(x0, x1, k / n), deck(k / n)) for k in range(n + 1)]
    under = [(lerp(x0, x1, k / n), deck(k / n) + 34 * s + 70 * s * (1 - math.sin(math.pi * k / n)) ** 0.0 * 0
              + 0) for k in range(n + 1)]
    # the arch: a thin rib under the deck that springs from the quays
    arch = [(lerp(x0, x1, k / n), deck(k / n) + 30 * s + (deck(0) + 120 * s - deck(k / n) - 30 * s) *
             (1 - math.sin(math.pi * k / n)) ** 2) for k in range(n + 1)]
    c.poly(top + list(reversed(arch)), None, ol=None)
    # lattice railing (draw first: behind the rib)
    rail_h = 30 * s
    c.line(top, col, 4 * s, cap=False)
    c.line([(px, py - rail_h) for px, py in top], col, 4 * s, cap=False)
    for k in range(n):
        (xa, ya), (xb, yb) = top[k], top[k + 1]
        c.line([(xa, ya), (xb, yb - rail_h)], shade, 1.6 * s, cap=False)
        c.line([(xa, ya - rail_h), (xb, yb)], shade, 1.6 * s, cap=False)
    c.line([(px, py - rail_h) for px, py in top], OUT, 1.5, cap=False)
    # deck girder
    c.poly(top + [(px, py + 12 * s) for px, py in reversed(top)], col, ol=OUT, w=2)
    # ornamental circles between deck and rib
    for k in range(2, n - 1, 3):
        px, py = top[k]
        ay = arch[k][1]
        if ay - py > 26 * s:
            r = min(10 * s, (ay - py - 12 * s) / 2.5)
            c.circle(px, py + 12 * s + (ay - py - 12 * s) / 2, r, None, ol=col, w=2.4 * s)
    c.line(arch, col, 7 * s, cap=False)
    c.line(arch, shade, 2.5 * s, cap=False)
    # three ornamental lamp standards over the walkway (the arches seen edge-on)
    if lamps:
        for u in (0.22, 0.5, 0.78):
            px, py = lerp(x0, x1, u), deck(u)
            hgt = 120 * s
            c.rect(px - 4 * s, py - hgt, px + 4 * s, py, col, ol=OUT, w=1.5)
            for side in (-1, 1):
                c.arc(px + side * 12 * s, py - hgt + 24 * s, 12 * s, 14 * s, 180 if side < 0 else 270,
                      270 if side < 0 else 360, col, 3 * s)
            ly = py - hgt - 4 * s
            if lit > 0:
                c.circle(px, ly - 8 * s, 18 * s, mix((255, 240, 180), (255, 255, 255), 0.3), ol=None)
            c.rect(px - 8 * s, ly - 20 * s, px + 8 * s, ly, mix((250, 240, 200), (255, 220, 120), lit), w=2)
            c.poly([(px - 10 * s, ly - 20 * s), (px, ly - 30 * s), (px + 10 * s, ly - 20 * s)], (60, 60, 66), w=1.5)


def quay_building(c, x, base, w, h, col, roof=(90, 96, 110), seed=0, lit=0.0):
    rng = np.random.default_rng(seed)
    c.rect(x, base - h, x + w, base, col, w=2)
    c.rect(x - 3, base - h - 10, x + w + 3, base - h, roof, w=2)
    rows = int((h - 40) / 46)
    cols = max(1, int(w / 40))
    for r in range(rows):
        for k in range(cols):
            wx = x + (k + 0.5) * w / cols
            wy = base - h + 26 + r * 46
            lt = lit > 0 and rng.random() < 0.5
            c.rect(wx - 9, wy, wx + 9, wy + 26, mix((70, 90, 120), (255, 214, 120), lit if lt else 0), w=1.5)


def custom_house(c, x, base, s=1.0, col=(232, 226, 210), dome=(90, 150, 130)):
    """Dublin's Custom House: long classical front with a green copper dome (far away)."""
    c.push(x, base, s)
    c.rect(-200, -70, 200, 0, col, w=2)
    c.rect(-60, -100, 60, -70, col, w=2)
    c.poly([(-66, -100), (0, -124), (66, -100)], col, w=2)
    for k in range(9):
        xx = -180 + k * 45
        c.rect(xx - 6, -60, xx + 6, -10, mix(col, (150, 140, 120), 0.4), ol=None)
    c.rect(-22, -170, 22, -124, col, w=2)
    c.ellipse(0, -172, 24, 30, dome, w=2)
    c.line([(0, -202), (0, -224)], OUT, 2, cap=False)
    c.circle(0, -226, 4, GOLD, w=1)
    c.pop()


def spire(c, x, base, h=420, s=1.0):
    """The Spire of Dublin: a thin silver needle."""
    c.poly([(x - 7 * s, base), (x, base - h * s), (x + 7 * s, base)], (214, 220, 228), w=1.5)
    c.line([(x + 2 * s, base), (x, base - h * s)], (240, 244, 250), 1.5, cap=False)


# ------------------------------------------------------------------- pub

def pub_musician(c, x, y, s=1.0, face=1, t=0.0, kind="badger", play=1.0, seed=0.0):
    """Seated session musicians: a badger with a tin whistle, a fox with a bodhran drum."""
    c.push(x, y, s, flip=face < 0)
    if kind == "badger":
        fur, dark, light = (120, 118, 124), (50, 46, 52), (240, 240, 236)
    else:
        fur, dark, light = (214, 110, 50), (150, 70, 34), (250, 240, 226)
    bob = abs(math.sin(t * 6.2 + seed)) * 3 * play
    # stool
    c.rect(-30, -50, 30, -40, WOOD, w=2)
    c.line([(-24, -40), (-30, 0)], WOOD_D, 5)
    c.line([(24, -40), (30, 0)], WOOD_D, 5)
    c.ellipse(0, -76 - bob, 32, 36, fur, w=2.5)
    c.ellipse(8, -72 - bob, 18, 24, light, ol=None)
    c.ellipse(14, -36, 14, 8, dark, w=2)
    hx, hy = 14, -126 - bob
    if kind == "badger":
        c.circle(hx - 18, hy - 18, 8, dark, w=2)
        c.ellipse(hx, hy, 26, 24, light, w=2.5)
        c.poly([(hx - 22, hy - 12), (hx - 4, hy - 22), (hx + 24, hy + 4), (hx + 20, hy + 12)], dark, ol=None)
        c.poly([(hx - 22, hy + 8), (hx - 6, hy - 6), (hx + 14, hy + 16), (hx + 6, hy + 20)], dark, ol=None)
        c.ellipse(hx + 6, hy - 2, 3, 3.5, (255, 255, 255), ol=None)
        c.ellipse(hx + 26, hy + 6, 6, 5, (30, 26, 30), ol=None)
        # tin whistle
        c.line([(hx + 26, hy + 14), (hx + 62, hy + 50)], (200, 200, 210), 5, cap=False)
        c.circle(hx + 50 + 2 * math.sin(t * 9), hy + 38, 5, fur, w=1.5)
        c.circle(hx + 38, hy + 26, 5, fur, w=1.5)
    else:
        for ex in (-14, 6):
            c.poly([(hx + ex - 8, hy - 14), (hx + ex, hy - 38), (hx + ex + 8, hy - 14)], fur, w=2)
        c.ellipse(hx, hy, 24, 22, fur, w=2.5)
        c.poly([(hx + 6, hy + 2), (hx + 40, hy + 8), (hx + 8, hy + 18)], light, w=2)
        c.circle(hx + 40, hy + 7, 4, (30, 26, 30), ol=None)
        c.arc(hx + 6, hy - 4, 4, 3, 200, 340, OUT, 2)
        # bodhran
        hit = math.sin(t * 12.4 + seed)
        c.ellipse(-10, -96 - bob, 12, 40, (230, 214, 180), w=2.5)
        c.ellipse(-14, -96 - bob, 6, 34, (200, 170, 120), ol=None)
        c.line([(28, -110 - bob), (6 + 8 * hit, -96 - bob + 10 * hit)], WOOD_D, 4)
    c.pop()


def dancer(c, x, y, s=1.0, face=1, t=0.0, col=(60, 120, 200), fur=(170, 140, 120), seed=0.0, step=1.0):
    """A little rabbit Irish-dancing: arms straight down, feet flicking fast."""
    c.push(x, y - abs(math.sin(t * 7 + seed)) * 12 * step, s, flip=face < 0)
    kick = math.sin(t * 14 + seed) * step
    c.stroke([(-6, -40), (-6 - 14 * max(0, kick), -6 + 8 * max(0, kick))], fur, 8)
    c.stroke([(8, -40), (8 + 16 * max(0, -kick), -4 + 10 * max(0, -kick))], fur, 8)
    c.poly([(-22, -40), (24, -40), (14, -96), (-12, -96)], col, w=2.5)        # dress with a wide skirt
    for k in range(3):
        c.circle(-12 + k * 12, -60, 3, (250, 220, 90), ol=None)
    c.line([(-12, -90), (-16, -50)], fur, 5)
    c.line([(14, -90), (18, -50)], fur, 5)
    c.circle(2, -112, 18, fur, w=2.5)
    for ex in (-6, 8):
        c.ellipse(ex, -146, 5, 18, fur, w=2)
    c.arc(8, -114, 3, 3, 200, 340, OUT, 1.8)
    c.circle(19, -108, 3, D.NOSE, ol=None)
    c.pop()


# -------------------------------------------------------------- characters

FERGAL = dict(fur=(176, 128, 84), dark=(126, 88, 58), light=(236, 214, 182), tip=(50, 40, 40),
              jumper=CREAM, jumper_d=CREAM_D, cap=(110, 100, 90))


def fergal(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, play=0.0, wave=0.0, seed=0.6,
           sit=False, reins=False, hop=0.0, look=(0.0, 0.0)):
    """Fergal the hare: tall ears with dark tips, a cream cable-knit jumper, often a fiddle."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = FERGAL
    c.push(x, y - hop, s, flip=face < 0)
    # feet / legs
    if sit:
        c.ellipse(10, -14, 34, 12, p["fur"], w=2.5)
        c.ellipse(40, -6, 22, 7, p["fur"], w=2.5)
    else:
        for fx, ph in ((-12, 0), (18, math.pi)):
            sw = math.sin(walk + ph) * 10 if walk else 0
            lift = -max(0.0, math.cos(walk + ph)) * 8 if walk else 0
            c.stroke([(fx * 0.6, -40), (fx + sw, -6 + lift)], p["fur"], 14)
            c.ellipse(fx + sw + 10, -5 + lift, 22, 7, p["fur"], w=2.5)
    # tail
    c.circle(-34, -58, 11, (250, 248, 240), w=2)
    # body in the jumper
    c.ellipse(0, -76, 36, 44, p["jumper"], w=3)
    c.rect(-30, -44, 30, -36, p["jumper_d"], ol=None, r=3)
    for k in (-16, 0, 16):
        for j in range(5):
            yy = -104 + j * 13
            c.arc(k, yy, 5, 6, 90, 270, p["jumper_d"], 2)
            c.arc(k, yy + 6, 5, 6, 270, 450, p["jumper_d"], 2)
    hx, hy = 14, -142
    # ears (behind the head)
    ew = math.sin(t * 2.2 + seed) * 4
    for ex, lean in ((-6, -10), (12, 6)):
        top = (hx + ex + lean + ew, hy - 96)
        c.poly([(hx + ex - 9, hy - 18), (top[0] - 10, top[1] + 30), top, (top[0] + 10, top[1] + 26),
                (hx + ex + 10, hy - 18)], p["fur"], w=2.5)
        c.poly([(top[0] - 6, top[1] + 20), top, (top[0] + 7, top[1] + 18)], p["tip"], ol=None)
        c.poly([(hx + ex - 3, hy - 22), (top[0] - 3, top[1] + 32), (top[0] + 4, top[1] + 30),
                (hx + ex + 4, hy - 22)], (236, 180, 170), ol=None)
    # head
    c.ellipse(hx, hy, 30, 28, p["fur"], w=3)
    c.ellipse(hx + 16, hy + 10, 16, 12, p["light"], ol=None)
    for ex in (hx - 2, hx + 18):
        ey = hy - 6
        if eyes == "closed":
            c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 6.5 * big, 8 * big, (255, 255, 255), w=2)
            c.ellipse(ex + 1.5 + look[0] * 2, ey + 1 + look[1] * 2, 4 * big, 5.5 * big, (120, 80, 40), ol=None)
            c.ellipse(ex + 1.5 + look[0] * 2, ey + 1 + look[1] * 2, 2, 4, (25, 20, 25), ol=None)
            c.circle(ex + 3, ey - 2, 1.5, (255, 255, 255), ol=None)
    c.ellipse(hx + 30, hy + 4, 5, 4, (220, 120, 130), w=1.5)
    if mouth > 0.05:
        h = 3 + 8 * mouth
        c.ellipse(hx + 24, hy + 15 + h * 0.4, 7, h, D.MOUTH, w=2)
        c.rect(hx + 20, hy + 13, hx + 28, hy + 19, (255, 255, 255), w=1)
    else:
        c.arc(hx + 22, hy + 12, 4, 3, 0, 180, OUT, 2)
        c.rect(hx + 21, hy + 14, hx + 27, hy + 19, (255, 255, 255), w=1)
    for dy in (-2, 3):
        c.line([(hx + 32, hy + 8), (hx + 52, hy + 4 + dy * 2)], OUT, 1.2, cap=False)
    # flat cap
    c.ellipse(hx + 2, hy - 24, 26, 10, p["cap"], w=2.5)
    c.ellipse(hx + 20, hy - 20, 16, 5, mix(p["cap"], (0, 0, 0), 0.2), w=2)
    # arms and fiddle
    if play > 0:
        fx, fy = hx + 6, hy + 34
        c.poly([(fx - 4, fy - 6), (fx + 46, fy + 14), (fx + 40, fy + 30), (fx - 10, fy + 10)], (150, 70, 30), w=2.5)
        c.ellipse(fx + 10, fy + 8, 16, 11, (180, 90, 40), ol=None)
        c.line([(fx + 40, fy + 22), (fx + 76, fy + 36)], (40, 30, 30), 5)          # neck
        c.ellipse(fx + 80, fy + 38, 6, 5, (40, 30, 30), ol=None)
        c.stroke([(-16, -100), (fx + 70, fy + 36)], p["jumper"], 11)                # left arm to the neck
        bow = math.sin(t * 9.0 + seed) * 26 * play
        bx, by = fx + 14 + bow * 0.4, fy + 18
        c.line([(bx - 50 - bow, by - 30), (bx + 40 - bow, by + 26)], (120, 80, 50), 3, cap=False)
        c.stroke([(20, -96), (bx - 10 - bow * 0.5, by + 30)], p["jumper"], 11)
        c.circle(bx - 10 - bow * 0.5, by + 30, 6, p["fur"], w=2)
    elif reins:
        c.stroke([(14, -96), (44, -74)], p["jumper"], 11)
        c.circle(46, -72, 6, p["fur"], w=2)
        c.line([(46, -72), (110, -90)], (120, 70, 40), 2, cap=False)
    else:
        wv = wave
        c.stroke([(-20, -96), (-30, -56)], p["jumper"], 11)
        c.circle(-30, -52, 6, p["fur"], w=2)
        if wv > 0:
            a = math.sin(t * 10) * 0.4
            ex2, ey2 = 42 + 10 * math.sin(a), -150 - 20 * math.cos(a)
            c.stroke([(22, -98), (ex2, ey2)], p["jumper"], 11)
            c.circle(ex2, ey2 - 4, 7, p["fur"], w=2)
        else:
            c.stroke([(22, -96), (34, -58)], p["jumper"], 11)
            c.circle(35, -54, 6, p["fur"], w=2)
    c.pop()


BRIDIE = dict(black=(44, 42, 50), white=(248, 246, 240), grey=(90, 88, 98), eye=(130, 80, 40))


def bridie(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, sit=False, seed=3.3, tail=None,
           worried=False, look=(0.0, 0.0)):
    """Bridie the Border Collie: black and white, one ear up and one flopped, a white-tipped tail."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = BRIDIE
    c.push(x, y, s, flip=face < 0)
    wag = math.sin(t * (9 if not worried else 3) + seed) if tail is None else tail
    if sit:
        c.stroke([(-40, -14), (-80, -8 + 4 * wag), (-104, -20 + 6 * wag)], p["black"], 16)
        c.circle(-106, -22 + 6 * wag, 9, p["white"], w=2)
        c.ellipse(-16, -40, 46, 40, p["black"], w=3)
        c.ellipse(20, -72, 34, 56, p["black"], w=3)
        c.ellipse(32, -68, 22, 44, p["white"], ol=None)
        for fx in (16, 44):
            c.stroke([(fx, -50), (fx + 4, -6)], p["white"], 15)
            c.ellipse(fx + 10, -6, 14, 7, p["white"], w=2.5)
        hx, hy = 40, -134
    else:
        by = -72
        c.stroke([(-62, by - 6), (-96, by + 10 + 8 * wag), (-118, by - 4 + 12 * wag)], p["black"], 16)
        c.circle(-120, by - 6 + 12 * wag, 9, p["white"], w=2)

        def leg(lx, ph, col):
            sw = math.sin(walk + ph) if walk else 0.0
            lift = -max(0.0, math.cos(walk + ph)) * 9 if walk else 0.0
            foot = (lx + sw * 14, lift - 2)
            c.stroke([(lx, by + 8), foot], col, 15)
            c.ellipse(foot[0] + 6, foot[1], 13, 7, p["white"], w=2.5)

        leg(-46, math.pi, p["grey"])
        leg(42, 0, p["grey"])
        c.ellipse(0, by, 72, 36, p["black"], w=3)
        c.ellipse(50, by + 4, 30, 30, p["white"], ol=None)        # white chest ruff
        c.ellipse(10, by + 22, 40, 10, p["white"], ol=None)
        leg(-34, 0, p["black"])
        leg(54, math.pi, p["white"])
        bob = math.sin(walk * 2) * 3 if walk else 0
        hx, hy = 82, by - 46 + bob
    # head
    c.poly([(hx - 26, hy - 14), (hx - 26, hy - 54), (hx - 4, hy - 26)], p["black"], w=2.5)     # ear up
    flop = 4 * math.sin(t * 2 + seed)
    c.poly([(hx + 6, hy - 28), (hx + 26, hy - 44 + flop), (hx + 30, hy - 26 + flop), (hx + 18, hy - 18)],
           p["black"], w=2.5)
    c.ellipse(hx, hy, 34, 30, p["black"], w=3)
    c.poly([(hx + 2, hy - 30), (hx + 10, hy - 30), (hx + 18, hy + 6), (hx - 4, hy + 6)], p["white"], ol=None)  # blaze
    c.ellipse(hx + 24, hy + 12, 24, 14, p["white"], w=2.5)                                   # muzzle
    c.ellipse(hx + 44, hy + 6, 8, 6, (30, 26, 30), w=1.5)
    for ex in (hx - 6, hx + 18):
        ey = hy - 8
        if eyes == "closed":
            c.arc(ex, ey, 6, 4, 20, 160, (230, 230, 230), 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 6, 6, 200, 340, (230, 230, 230), 2.5)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 6 * big, 7 * big, (255, 255, 255), w=1.5)
            c.ellipse(ex + 1 + look[0] * 2, ey + 1 + look[1] * 2, 3.8 * big, 4.8 * big, p["eye"], ol=None)
            c.circle(ex + 1 + look[0] * 2, ey + 1 + look[1] * 2, 1.8, (25, 20, 25), ol=None)
            c.circle(ex + 2.5, ey - 1.5, 1.3, (255, 255, 255), ol=None)
        if worried:
            c.line([(ex - 7, ey - 10), (ex + 6, ey - 14)], (200, 200, 200), 2.5)
    if mouth > 0.05:
        h = 3 + 10 * mouth
        c.ellipse(hx + 28, hy + 22 + h * 0.4, 10, h, D.MOUTH, w=2)
        c.ellipse(hx + 28, hy + 22 + h * 0.8, 6, 2 + 2 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 28, hy + 16, 10, 6, 20, 160, OUT, 2)
    c.rect(hx - 26, hy + 26, hx + 18, hy + 34, (200, 50, 60), w=2, r=3) if not sit else \
        c.rect(hx - 20, hy + 28, hx + 22, hy + 36, (200, 50, 60), w=2, r=3)
    c.pop()


def gull(c, x, y, t, s=1.0, face=1, seed=0.0):
    c.push(x, y, s, flip=face < 0)
    k = math.sin(t * 6 + seed)
    c.ellipse(0, 0, 18, 7, (250, 250, 250), w=2)
    c.poly([(-4, -2), (-20, -16 - 14 * k), (-34, -6 - 12 * k)], (250, 250, 250), w=2)
    c.poly([(4, -2), (16, -16 - 14 * k), (30, -8 - 12 * k)], (230, 232, 236), w=2)
    c.circle(16, -4, 6, (250, 250, 250), w=2)
    c.poly([(21, -4), (30, -2), (21, 0)], (240, 190, 60), ol=None)
    c.pop()


def puffin(c, x, y, s=1.0, face=1, t=0.0, seed=0.0):
    c.push(x, y, s, flip=face < 0)
    bob = math.sin(t * 2 + seed) * 2
    c.ellipse(0, -22 + bob, 14, 22, (30, 30, 36), w=2)
    c.ellipse(5, -18 + bob, 9, 16, (250, 250, 250), ol=None)
    c.circle(4, -44 + bob, 11, (30, 30, 36), w=2)
    c.ellipse(6, -44 + bob, 8, 7, (240, 240, 240), ol=None)
    c.poly([(12, -48 + bob), (26, -42 + bob), (12, -36 + bob)], (240, 110, 40), w=1.5)
    c.circle(6, -46 + bob, 2, (20, 20, 20), ol=None)
    c.line([(-2, 0), (-2, -4)], (240, 110, 40), 3)
    c.line([(6, 0), (6, -4)], (240, 110, 40), 3)
    c.pop()


def rain_streaks(c, t, k=1.0, seed=1, n=110, speed=900.0, col=(200, 214, 236), slant=0.25, x0=0, x1=W):
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    m = int(n * k)
    for i in range(m):
        x = rng.uniform(x0 - 100, x1)
        y0 = rng.uniform(0, H)
        y = (y0 + speed * t) % (H + 60) - 30
        ln = rng.uniform(16, 30)
        xx = x + slant * y
        c.line([(xx, y), (xx + slant * ln, y + ln)], col, 1.6, cap=False)
