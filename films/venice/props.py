"""Venice props and new characters, drawn with draw.Canvas primitives.

Landmarks (St Mark's Basilica, the Campanile, the Doge's Palace, the Rialto
Bridge), Venetian palazzi, gondolas and striped mooring poles, a hot-air
balloon, Murano glass -- and the locals: Bepi (a singing egret gondolier),
Nonna Vetra (an old glassmaker cat) and a great many pigeons.
Characters are in local space: origin between the feet, facing right.
"""
import math

import numpy as np

import draw as D
from draw import OUT, mix, lerp, clamp, ease

# ------------------------------------------------------------------ colours

WATER = (64, 142, 150)
WATER_D = (44, 112, 126)
WATER_L = (130, 196, 196)
LAGOON = (92, 162, 190)
STONE = (236, 228, 212)
STONE_D = (204, 194, 176)
BRICK = (178, 84, 62)
GOLD = (240, 192, 72)
GOND = (34, 30, 40)
RED = (204, 52, 58)
NAVY = (40, 60, 120)
GLASS = (172, 226, 240)
GLASS_D = (110, 176, 206)

LUNA_NOBELL = dict(D.LUNA, collar=None)
NONNA = dict(body=(238, 228, 212), dark=(196, 170, 140), belly=(255, 252, 246), ear=(250, 180, 180),
             eye=(214, 160, 60), stripes=False, collar=None)


def head_pos(pose, walk=0.0, head_dy=0.0):
    """Where draw.cat puts the head centre (cat-local coordinates)."""
    if pose == "sit":
        return 18, -106 + head_dy
    if pose == "crouch":
        return 52, -64 + head_dy
    if pose == "leap":
        return 58, -74
    if pose == "sleep":
        return 46, -40
    if pose == "swim":
        return 30, -30
    bob = math.sin(walk * 2) * 2 if walk else 0
    return 52, -86 + bob + head_dy


def collar(c, x, y, s, face, pose, walk=0.0, head_dy=0.0, bell=None, t=0.0, ring=0.0):
    """Luna's blue collar drawn on its own: bell None (lost), 'gold' or 'glass'."""
    hx, hy = head_pos(pose, walk, head_dy)
    c.push(x, y, s, flip=face < 0)
    c.rect(hx - 20, hy + 24, hx + 22, hy + 31, D.LUNA["collar"], w=2, r=3)
    if bell == "gold":
        c.circle(hx + 6, hy + 35, 5, (250, 210, 70), w=2)
    elif bell == "glass":
        sw = math.sin(t * 18) * 0.35 * ring
        glass_bell(c, hx + 6, hy + 31, 0.42, ang=sw, shine=0.5 + 0.5 * ring)
    c.pop()


# ------------------------------------------------------------------ glass

def glass_bell(c, x, y, s=1.0, ang=0.0, shine=0.0, col=GLASS, dark=GLASS_D, glow=0.0):
    """A Murano glass bell hanging from (x, y); ~44 units tall at s=1."""
    hot = (255, 170, 70)
    if glow > 0:
        col, dark = mix(col, hot, glow), mix(dark, (230, 110, 40), glow)
    ca, sa = math.cos(ang), math.sin(ang)

    def P(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    shape = [(-4, 0), (4, 0), (10, 6), (14, 14), (15, 26), (18, 36), (24, 42), (-24, 42), (-18, 36),
             (-15, 26), (-14, 14), (-10, 6)]
    c.circle(*P(0, 46), 5 * s, dark, w=1.5)
    c.poly([P(*p) for p in shape], col, w=max(1.5, 2.5 * s))
    c.poly([P(*p) for p in [(-9, 9), (-6, 9), (-8, 30), (-14, 38), (-15, 34), (-11, 26)]],
           mix(col, (255, 255, 255), 0.7), ol=None)
    c.line([P(-20, 40), P(20, 40)], dark, 2 * s, cap=False)
    c.rect(*P(-3, -7), *P(3, 0), mix(col, (255, 255, 255), 0.3), w=1.5, r=1)
    if shine > 0.05:
        r = 9 * s * shine
        px, py = P(10, 14)
        c.line([(px - r, py), (px + r, py)], (255, 255, 255), 2, cap=False)
        c.line([(px, py - r), (px, py + r)], (255, 255, 255), 2, cap=False)


def squashed_bell(c, x, y, s=1.0):
    c.ellipse(x, y - 2 * s, 9 * s, 3.5 * s, (236, 190, 60), w=2)
    c.line([(x - 5 * s, y - 2 * s), (x + 4 * s, y - 3 * s)], (180, 130, 40), 1.5, cap=False)


def glass_mouse(c, x, y, s=1.0):
    """A little pink glass mouse with a red glass scarf (Whiskers' present for Pip)."""
    body, hi = (246, 196, 214), (255, 236, 244)
    c.push(x, y, s)
    c.line([(-16, -6), (-28, -12), (-34, -6)], mix(body, OUT, 0.3), 2.5)
    c.ellipse(0, -10, 18, 11, body, w=2)
    c.circle(14, -20, 8, body, w=2)
    c.circle(8, -28, 5, body, w=1.5)
    c.circle(16, -29, 5, body, w=1.5)
    c.circle(23, -18, 2, (230, 110, 140), ol=None)
    c.circle(15, -22, 1.6, OUT, ol=None)
    c.rect(4, -16, 14, -11, (220, 50, 60), w=1.5, r=2)
    c.ellipse(-4, -14, 7, 3, hi, ol=None)
    c.pop()


def vase(c, x, y, s, col, kind=0):
    c.push(x, y, s)
    hi = mix(col, (255, 255, 255), 0.55)
    if kind == 0:
        c.poly([(-8, -50), (8, -50), (6, -40), (18, -20), (14, 0), (-14, 0), (-18, -20), (-6, -40)], col, w=2)
    elif kind == 1:
        c.ellipse(0, -18, 18, 18, col, w=2)
        c.rect(-6, -44, 6, -32, col, w=2)
    else:
        c.poly([(-16, -40), (16, -40), (8, 0), (-8, 0)], col, w=2)
    c.ellipse(-6, -22, 3, 10, hi, ol=None)
    c.pop()


def fritola(c, x, y, r=12, rot=0.0):
    """A Venetian carnival doughnut: golden ball dusted with sugar."""
    c.circle(x, y - r, r, (214, 140, 60), w=2)
    c.circle(x - r * 0.25, y - r * 1.25, r * 0.45, (236, 176, 90), ol=None)
    for k in range(7):
        a = rot + k * 2.4
        rr = r * (0.3 + 0.55 * ((k * 37) % 10) / 10)
        c.circle(x + math.cos(a) * rr, y - r + math.sin(a) * rr, 1.6, (255, 255, 250), ol=None)


def mask(c, x, y, s=1.0, col=(220, 60, 90), trim=GOLD, feather=(90, 170, 220)):
    """A carnival eye mask with a feather."""
    c.push(x, y, s)
    c.line([(14, -10), (26, -40), (34, -48)], feather, 6)
    c.poly([(-26, -4), (-18, -14), (0, -10), (18, -14), (26, -4), (18, 8), (4, 6), (0, 2), (-4, 6), (-18, 8)],
           col, w=2)
    for ex in (-11, 11):
        c.ellipse(ex, -3, 6, 3.5, (30, 24, 34), ol=None)
    c.line([(-24, -5), (-18, -13), (0, -9), (18, -13), (24, -5)], trim, 2, cap=False)
    c.pop()


# ---------------------------------------------------------------- vehicles

def _env_w(y):
    """Half-width of the balloon envelope at height y (local units)."""
    R, cy = 130.0, -350.0
    if y <= cy:
        return math.sqrt(max(0.0, R * R - (y - cy) ** 2))
    return 34 + (R - 34) * math.cos(math.pi / 2 * min(1.0, (y - cy) / 180))


def balloon(c, x, y, s=1.0, t=0.0, flame=0.0, sign=True, inside=None, cols=(RED, GOLD)):
    """Hot-air balloon; (x, y) = bottom centre of the basket. ~480 units tall."""
    c.push(x, y, s)
    ys = np.linspace(-479, -170, 30)
    n = 8
    th = np.linspace(-math.pi / 2, math.pi / 2, n + 1)
    for k in range(n):
        u0, u1 = math.sin(th[k]), math.sin(th[k + 1])
        left = [(u0 * _env_w(yy), yy) for yy in ys]
        right = [(u1 * _env_w(yy), yy) for yy in ys[::-1]]
        col = cols[k % 2]
        c.poly(left + right, col, ol=None)
    for k in range(1, n):
        u = math.sin(th[k])
        c.line([(u * _env_w(yy), yy) for yy in ys], mix(OUT, cols[0], 0.3), 1.5, cap=False)
    outline = [(_env_w(yy), yy) for yy in ys] + [(-_env_w(yy), yy) for yy in ys[::-1]]
    c.poly(outline, None, w=3)
    c.ellipse(-60, -420, 20, 34, mix(cols[1], (255, 255, 255), 0.5), ol=None)
    # skirt + ropes
    c.rect(-34, -176, 34, -150, mix(cols[0], OUT, 0.35), w=2.5, r=4)
    for sx in (-1, 1):
        c.line([(sx * 30, -150), (sx * 52, -82)], (90, 70, 60), 2, cap=False)
        c.line([(sx * 12, -150), (sx * 22, -82)], (90, 70, 60), 2, cap=False)
    # burner
    c.rect(-12, -136, 12, -120, (150, 150, 160), w=2, r=3)
    if flame > 0.02:
        fl = flame * (0.85 + 0.15 * math.sin(t * 40))
        c.poly([(-10, -136), (0, -136 - 42 * fl), (10, -136)], (255, 170, 60), ol=None)
        c.poly([(-5, -136), (0, -136 - 26 * fl), (5, -136)], (255, 240, 150), ol=None)
    if inside:
        inside(c)
    # basket
    bas, bas_d = (178, 120, 70), (140, 90, 50)
    c.rect(-56, -84, 56, 0, bas, w=3, r=6)
    for yy in (-62, -40, -20):
        c.line([(-54, yy), (54, yy)], bas_d, 2, cap=False)
    for xx in range(-44, 50, 16):
        c.line([(xx, -82), (xx, -2)], bas_d, 1.5, cap=False)
    c.rect(-60, -90, 60, -78, (120, 76, 44), w=3, r=5)
    if sign:
        c.rect(-44, -60, 44, -32, NAVY, w=2, r=3)
        c.text(0, -46, "VENEZIA", 13, (255, 230, 150))
    c.pop()


def gondola(c, x, y, s=1.0, face=1, t=0.0, bob=True):
    """A black gondola; (x, y) = middle at the waterline. Prow (ferro) at +x. ~470 long."""
    dy = 2.5 * math.sin(t * 2.2) if bob else 0
    c.push(x, y + dy, s, flip=face < 0)
    hull = [(-236, -78), (-226, -66), (-200, -44), (-160, -20), (-120, -4), (0, 4), (120, -4), (170, -22),
            (200, -42), (218, -60), (228, -74), (214, -76), (196, -54), (170, -40), (0, -34), (-170, -42),
            (-210, -60)]
    c.poly(hull, GOND, w=3)
    c.line([(-200, -48), (-160, -36), (0, -30), (170, -36), (196, -50)], (90, 86, 110), 2, cap=False)
    c.line([(-170, -26), (0, -14), (150, -24)], (70, 66, 86), 2, cap=False)
    # ferro: the silver comb on the prow
    fe = (214, 218, 228)
    c.poly([(214, -76), (226, -74), (236, -110), (246, -118), (230, -122), (222, -112)], fe, w=2)
    for k in range(6):
        yy = -80 - k * 6
        c.line([(226 + k * 1.5, yy), (240 + k * 1.5, yy - 2)], fe, 3.5)
    c.circle(236, -126, 5, fe, w=2)
    # seat with red cushion and gold trim
    c.rect(-40, -52, 60, -36, (150, 30, 44), w=2.5, r=5)
    c.line([(-36, -48), (56, -48)], GOLD, 2, cap=False)
    c.poly([(-56, -64), (-40, -64), (-40, -36), (-56, -36)], (90, 60, 40), w=2)
    c.circle(-48, -68, 5, GOLD, w=1.5)
    # forcola (oarlock) at the stern
    c.poly([(-150, -44), (-142, -78), (-132, -70), (-138, -44)], (130, 90, 60), w=2)
    c.pop()


def oar_pts(x, y, s, face, ang):
    """Endpoints of Bepi's oar from his hands; ang = angle below horizontal (radians)."""
    L = 210 * s
    return (x, y), (x + face * math.cos(ang) * L, y + math.sin(ang) * L)


def oar(c, x0, y0, x1, y1):
    c.line([(x0, y0), (x1, y1)], OUT, 9)
    c.line([(x0, y0), (x1, y1)], (196, 150, 96), 5)
    a = math.atan2(y1 - y0, x1 - x0)
    px, py = -math.sin(a), math.cos(a)
    bx, by = x1 - math.cos(a) * 40, y1 - math.sin(a) * 40
    c.poly([(bx + px * 5, by + py * 5), (x1 + px * 8, y1 + py * 8), (x1 - px * 8, y1 - py * 8),
            (bx - px * 5, by - py * 5)], (196, 150, 96), w=2)


def mooring_pole(c, x, y, h=200, col=(40, 80, 170), col2=(250, 250, 250), cap=GOLD, top=None):
    top = y - h if top is None else top
    c.rect(x - 7, top, x + 7, y + 30, col2, w=2.5)
    k = 0
    yy = top + 8
    while yy < y + 20:
        c.poly([(x - 7, yy + 10), (x + 7, yy), (x + 7, yy + 10), (x - 7, yy + 20)], col, ol=None)
        yy += 26
    c.rect(x - 7, top, x + 7, y + 30, None, w=2.5)
    c.ellipse(x, top - 2, 9, 6, cap, w=2)


# --------------------------------------------------------------- characters

def egret(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", hands=None, wave=0.0, hat=True,
          walk=0.0, seed=3.3, laugh=False):
    """Bepi: a tall white egret gondolier in a striped shirt and straw boater.

    hands: (hx, hy) in local units where his wing tips meet (holding the oar), or None.
    """
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    hop = abs(math.sin(t * 9)) * 4 if laugh else 0
    c.push(x, y - hop, s, flip=face < 0)
    white, shade = (252, 252, 250), (220, 224, 232)
    leg = (60, 56, 60)
    foot = (230, 190, 60)
    for k, lx in enumerate((-8, 10)):
        sw = math.sin(walk + k * math.pi) * 10 if walk else 0
        c.line([(lx, -92), (lx + sw * 0.5, -46), (lx + sw, 0)], OUT, 6)
        c.line([(lx, -92), (lx + sw * 0.5, -46), (lx + sw, 0)], leg, 3)
        c.line([(lx + sw - 6, 0), (lx + sw + 12, 0)], foot, 3)
    # tail plumes
    c.poly([(-26, -118), (-62, -96), (-58, -88), (-24, -100)], white, w=2.5)
    c.poly([(-24, -110), (-54, -84), (-46, -80), (-20, -98)], shade, w=2)
    # body = striped shirt
    c.ellipse(0, -128, 32, 42, white, w=3)
    for yy in (-150, -134, -118, -102):
        half = math.sqrt(max(0.0, 1 - ((yy + 128) / 42) ** 2)) * 30
        c.line([(-half, yy), (half, yy)], NAVY, 6, cap=False)
    c.ellipse(0, -128, 32, 42, None, w=3)
    # neck (S curve) and red scarf
    neck = [(6, -160), (16, -184), (6, -206), (12, -226)]
    c.stroke(neck, white, 14)
    c.poly([(-6, -166), (20, -166), (24, -156), (-4, -154)], RED, w=2)
    c.poly([(-2, -158), (-16, -140), (-8, -138), (4, -156)], RED, w=2)
    # head
    hx, hy = 16, -234
    c.ellipse(hx, hy, 17, 14, white, w=3)
    # plume crest
    c.line([(hx - 12, hy - 4), (hx - 34, hy + 6 + 3 * math.sin(t * 3))], OUT, 2.5)
    c.line([(hx - 12, hy - 1), (hx - 30, hy + 12 + 3 * math.sin(t * 3 + 1))], OUT, 2)
    # beak
    op = 0.45 * clamp(mouth)
    bx = hx + 12
    up = [(bx, hy - 5), (bx + 46, hy + 2 - op * 26), (bx, hy + 2)]
    lo = [(bx, hy + 1), (bx + 42, hy + 4 + op * 26), (bx, hy + 7)]
    c.poly(lo, (226, 176, 50), w=2)
    c.poly(up, (246, 200, 70), w=2)
    # eye
    if eyes == "closed":
        c.arc(hx + 4, hy - 3, 5, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(hx + 4, hy, 5, 5, 200, 340, OUT, 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.circle(hx + 4, hy - 3, 5 * big, (255, 230, 120), w=2)
        c.circle(hx + 5, hy - 3, 2.6 * big, (20, 20, 24), ol=None)
        c.circle(hx + 6, hy - 4.5, 1, (255, 255, 255), ol=None)
    # straw boater
    if hat:
        c.ellipse(hx - 2, hy - 13, 26, 5, (236, 206, 130), w=2.5)
        c.rect(hx - 16, hy - 30, hx + 12, hy - 12, (236, 206, 130), w=2.5, r=3)
        c.rect(hx - 16, hy - 20, hx + 12, hy - 14, RED, w=1.5)
    # wings / arms
    if hands is not None:
        ax, ay = hands
        for sx, col in ((-4, shade), (6, white)):
            c.poly([(sx - 8, -150), (sx + 10, -148), (ax + 4, ay + 4), (ax - 6, ay)], col, w=2.5)
    else:
        lift = wave
        tip = (40, -70 - 120 * lift)
        c.poly([(-6, -150), (14, -146), (tip[0] + 6, tip[1]), (tip[0] - 10, tip[1] + 6)], white, w=2.5)
        if lift > 0:
            for k in range(3):
                c.line([(tip[0] - 4 + k * 6, tip[1]), (tip[0] - 6 + k * 8, tip[1] - 14)], white, 6)
                c.line([(tip[0] - 4 + k * 6, tip[1]), (tip[0] - 6 + k * 8, tip[1] - 14)], OUT, 1, cap=False)
    c.pop()


def egret_head(face, x, y, s):
    return x + face * 28 * s, y - 234 * s


def notes(c, x, y, t, k=1.0, col=(255, 250, 220)):
    """Floating music notes."""
    if k <= 0.02:
        return
    for i in range(3):
        u = (t * 0.45 + i / 3) % 1.0
        nx, ny = x + 26 * u + 18 * math.sin(u * 6 + i), y - 70 * u
        a = k * (1 - u)
        if a < 0.05:
            continue
        cc = mix((80, 80, 110), col, min(1, a * 1.5))
        c.ellipse(nx, ny, 6, 4.5, cc, w=1.5)
        c.line([(nx + 5, ny), (nx + 5, ny - 18)], OUT, 2, cap=False)
        if i % 2:
            c.line([(nx + 5, ny - 18), (nx + 12, ny - 12)], OUT, 2, cap=False)


def nonna_extras(c, x, y, s, face, pose, walk=0.0, head_dy=0.0):
    """Nonna Vetra's red polka-dot headscarf, round glasses and leather apron."""
    hx, hy = head_pos(pose, walk, head_dy)
    c.push(x, y, s, flip=face < 0)
    if pose == "sit":
        c.poly([(-6, -84), (34, -84), (40, -14), (-4, -14)], (150, 96, 60), w=2.5)
        c.line([(-6, -84), (6, -110 + head_dy + 30)], (120, 76, 46), 2, cap=False)
    # headscarf
    pts = [(hx - 34 + 68 * u, hy - 8 - 26 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)]
    c.poly(pts, RED, w=2.5)
    for dx, dy in ((-16, -18), (0, -26), (16, -20), (-6, -14), (10, -12)):
        c.circle(hx + dx, hy + dy, 2.5, (255, 255, 255), ol=None)
    c.poly([(hx - 32, hy - 10), (hx - 48, hy - 2), (hx - 44, hy + 8), (hx - 30, hy - 2)], RED, w=2)
    # glasses
    for ex in (hx - 2, hx + 22):
        c.ellipse(ex, hy - 4, 10, 10, None, w=2)
    c.line([(hx + 8, hy - 5), (hx + 12, hy - 5)], OUT, 2, cap=False)
    c.pop()


def pigeon(c, x, y, s=1.0, face=1, t=0.0, peck=0.0, fly=0.0, seed=0.0, col=None):
    """A small grey pigeon. peck 0..1 lowers the head; fly 0..1 flaps wings and tucks feet."""
    body = col or (156, 158, 176)
    dark = mix(body, OUT, 0.3)
    c.push(x, y, s, flip=face < 0)
    if fly < 0.5:
        c.line([(-2, -8), (-4, 0)], (220, 120, 120), 2.5, cap=False)
        c.line([(4, -8), (5, 0)], (220, 120, 120), 2.5, cap=False)
    c.poly([(-14, -16), (-30, -22), (-28, -12)], dark, w=2)
    c.ellipse(0, -16, 16, 11, body, w=2)
    if fly > 0:
        f = math.sin(t * 30 + seed * 5)
        for side in (-1, 1):
            c.poly([(-6, -20), (8, -20), (2 + side * 2, -20 - 26 * f * side), (-14, -20 - 20 * f * side)],
                   mix(body, (255, 255, 255), 0.15), w=2)
    else:
        c.ellipse(-3, -17, 10, 6, dark, ol=None)
        c.line([(-8, -15), (2, -14)], (90, 90, 104), 1.5, cap=False)
    hx, hy = lerp(12, 18, peck), lerp(-28, -10, peck)
    c.ellipse(8, -24 + 6 * peck, 6, 7, (110, 150, 130), ol=None)
    c.circle(hx, hy, 7, body, w=2)
    c.ellipse(hx - 2, hy + 6, 6, 3, (150, 110, 160), ol=None)
    c.poly([(hx + 6, hy - 1), (hx + 12, hy + 1), (hx + 6, hy + 3)], (230, 180, 120), w=1.2)
    c.circle(hx + 2, hy - 2, 1.8, (220, 90, 40), ol=None)
    c.circle(hx + 2, hy - 2, 0.9, OUT, ol=None)
    c.pop()


# ---------------------------------------------------------------- landmarks

def campanile(c, x, base, s=1.0, angel=True):
    """St Mark's bell tower: brick shaft, white belfry, green pyramid, golden angel. ~560 tall."""
    c.push(x, base, s)
    br, br_l = BRICK, mix(BRICK, (255, 220, 200), 0.25)
    c.rect(-44, -330, 44, 0, br, w=3)
    for px in (-30, -10, 10, 30):
        c.rect(px - 4, -326, px + 4, -4, br_l, ol=None)
    c.rect(-48, -14, 48, 0, STONE_D, w=2.5)
    # small loggia at the foot
    c.rect(-70, -40, 70, 0, STONE, w=2.5)
    for k in range(5):
        ax = -56 + k * 28
        c.rect(ax - 8, -30, ax + 8, 0, (120, 100, 90), w=1.5, r=8)
    # belfry
    c.rect(-48, -338, 48, -330, STONE, w=2.5)
    c.rect(-44, -392, 44, -338, STONE, w=2.5)
    for k in range(4):
        ax = -30 + k * 20
        c.rect(ax - 7, -384, ax + 7, -344, (70, 60, 70), w=1.5, r=7)
    c.circle(-30 + 20 * 1.5, -362, 6, GOLD, ol=None)
    c.rect(-48, -398, 48, -392, STONE, w=2.5)
    # attic
    c.rect(-44, -440, 44, -398, br, w=2.5)
    c.circle(0, -420, 12, STONE, w=2)
    c.rect(-48, -446, 48, -440, STONE, w=2.5)
    # spire
    c.poly([(-46, -446), (0, -548), (46, -446)], (104, 168, 136), w=3)
    c.poly([(0, -548), (46, -446), (14, -446)], (84, 144, 116), ol=None)
    if angel:
        c.rect(-2, -560, 2, -548, GOLD, ol=None)
        c.poly([(-6, -560), (0, -580), (6, -560)], GOLD, w=1.5)
        c.poly([(0, -574), (14, -582), (6, -566)], GOLD, w=1.2)
        c.circle(0, -584, 4, GOLD, w=1.2)
    c.pop()


def basilica(c, x, base, s=1.0):
    """St Mark's Basilica facade with its golden arches and five domes. ~640 wide, ~330 tall."""
    c.push(x, base, s)
    marble, marble_d = (240, 226, 204), (214, 196, 170)
    dome, dome_d = (150, 160, 178), (122, 130, 152)
    # domes behind
    for dx, r, h in ((-220, 50, -250), (220, 50, -250), (-110, 60, -270), (110, 60, -270), (0, 74, -290)):
        c.rect(dx - r * 0.7, h, dx + r * 0.7, h + 40, marble_d, w=2)
        pts = [(dx + r * math.cos(a), h - r * 0.95 * math.sin(a)) for a in np.linspace(0, math.pi, 16)]
        c.poly(pts + [(dx - r, h + 6), (dx + r, h + 6)], dome, w=2.5)
        c.poly([(dx, h - r * 0.95)] + [(dx + r * math.cos(a), h - r * 0.95 * math.sin(a))
                                      for a in np.linspace(0, math.pi / 2, 8)] + [(dx + r * 0.3, h + 6)],
               dome_d, ol=None)
        c.rect(dx - 6, h - r - 22, dx + 6, h - r + 4, dome_d, w=1.5)
        c.circle(dx, h - r - 28, 6, GOLD, w=1.5)
        c.line([(dx, h - r - 34), (dx, h - r - 50)], GOLD, 2, cap=False)
        c.line([(dx - 6, h - r - 44), (dx + 6, h - r - 44)], GOLD, 2, cap=False)
    # upper storey with ogee arches
    c.rect(-300, -220, 300, -130, marble, w=3)
    for k in range(5):
        ax = -240 + k * 120
        wdt = 50 if k != 2 else 64
        pts = [(ax - wdt, -130), (ax - wdt, -190)]
        pts += [(ax + wdt * math.cos(a), -190 - wdt * 0.7 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)]
        pts += [(ax + wdt, -130)]
        c.poly(pts, GOLD if k != 2 else (70, 100, 170), w=2.5)
        # ogee crown
        c.poly([(ax - wdt - 6, -192), (ax, -256 - (12 if k == 2 else 0)), (ax + wdt + 6, -192),
                (ax + wdt * 0.6, -200), (ax, -232), (ax - wdt * 0.6, -200)], marble_d, w=2)
        c.circle(ax, -260 - (12 if k == 2 else 0), 5, GOLD, w=1.5)
        if k == 2:
            for sx, sy in ((-30, -170), (0, -200), (30, -170), (-15, -150), (15, -150), (0, -165)):
                c.circle(ax + sx, sy, 3, GOLD, ol=None)
        else:
            c.poly([(ax - 20, -150), (ax, -176), (ax + 20, -150)], (200, 90, 70), ol=None)
            c.circle(ax, -160, 8, (60, 90, 160), ol=None)
    # terrace balustrade and the four bronze horses (tiny)
    c.rect(-306, -136, 306, -124, marble_d, w=2.5)
    for hx in (-26, -10, 10, 26):
        c.ellipse(hx, -146, 7, 5, (130, 110, 70), w=1.5)
        c.circle(hx + 6, -154, 3, (130, 110, 70), w=1)
    # lower storey with five portals
    c.rect(-300, -124, 300, 0, marble, w=3)
    for k in range(5):
        ax = -240 + k * 120
        wdt = 46 if k != 2 else 56
        top = -96 if k != 2 else -112
        c.rect(ax - wdt - 6, top - 10, ax + wdt + 6, 0, marble_d, w=2)
        pts = [(ax - wdt, 0), (ax - wdt, top)]
        pts += [(ax + wdt * math.cos(a), top - wdt * 0.6 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)]
        pts += [(ax + wdt, 0)]
        c.poly(pts, GOLD, w=2.5)
        # lunette picture + dark doorway
        c.rect(ax - wdt * 0.55, top + 22, ax + wdt * 0.55, 0, (70, 46, 50), w=2, r=wdt * 0.5)
        c.circle(ax, top - 6, 7, (80, 120, 190), ol=None)
        for cxx in (ax - wdt - 3, ax + wdt + 3):
            c.rect(cxx - 3, top, cxx + 3, 0, (200, 120, 110), ol=None)
    c.pop()


def doge_palace(c, x, base, s=1.0, n=9):
    """Doge's Palace: white arcades below, a pink diamond-patterned wall above. (x = left edge)"""
    c.push(x, base, s)
    w = n * 50
    pink, pink_d = (240, 196, 186), (222, 160, 156)
    c.rect(0, -300, w, -150, pink, w=3)
    for row in range(5):
        for k in range(n * 2):
            dx = k * 25 + (12 if row % 2 else 0)
            dy = -290 + row * 28
            if dx + 10 < w:
                c.poly([(dx + 6, dy), (dx + 12, dy - 7), (dx + 18, dy), (dx + 12, dy + 7)], pink_d, ol=None)
    for k in range(n // 2 + 1):
        wx = 30 + k * 100
        if wx + 20 < w:
            c.rect(wx - 14, -260, wx + 14, -196, (60, 56, 80), w=2, r=12)
            c.rect(wx - 18, -200, wx + 18, -192, STONE, w=1.5)
    # crenellations
    for k in range(int(w / 25)):
        c.poly([(k * 25 + 4, -300), (k * 25 + 12, -316), (k * 25 + 20, -300)], STONE, w=1.5)
    # upper loggia (gothic tracery) and lower arcade
    c.rect(0, -150, w, -80, STONE, w=3)
    for k in range(n * 2):
        ax = 12.5 + k * 25
        c.rect(ax - 8, -138, ax + 8, -84, (90, 80, 96), w=1.5, r=8)
        if k < n * 2 - 1:
            c.circle(ax + 12.5, -142, 4, (90, 80, 96), ol=None)
    c.rect(0, -80, w, 0, STONE, w=3)
    for k in range(n):
        ax = 25 + k * 50
        c.rect(ax - 18, -66, ax + 18, 0, (96, 86, 100), w=2, r=17)
    c.pop()


def column_lion(c, x, base, s=1.0):
    """The granite column topped by the winged lion of St Mark."""
    c.push(x, base, s)
    c.rect(-22, -24, 22, 0, STONE_D, w=2.5)
    c.rect(-14, -330, 14, -24, (170, 160, 160), w=2.5)
    c.rect(-24, -346, 24, -330, STONE, w=2.5)
    lion = (110, 140, 120)
    c.ellipse(0, -362, 24, 13, lion, w=2)
    c.circle(20, -376, 11, lion, w=2)
    c.poly([(-6, -366), (-36, -404), (-18, -380), (-28, -398), (4, -372)], lion, w=2)
    c.line([(-22, -360), (-36, -350)], lion, 4)
    c.pop()


def chimney(c, x, y, s=1.0, col=(214, 120, 90)):
    """Venetian funnel chimney."""
    c.rect(x - 5 * s, y - 26 * s, x + 5 * s, y, col, w=2)
    c.poly([(x - 6 * s, y - 26 * s), (x - 14 * s, y - 44 * s), (x + 14 * s, y - 44 * s), (x + 6 * s, y - 26 * s)],
           col, w=2)


def gothic_window(c, x, y, w, h, col=(60, 58, 80), sill=STONE, shutters=None):
    """Ogee-arched window, (x, y) = bottom centre."""
    if shutters:
        c.rect(x - w - w * 0.7, y - h, x - w, y, shutters, w=1.5)
        c.rect(x + w, y - h, x + w + w * 0.7, y, shutters, w=1.5)
    pts = [(x - w, y), (x - w, y - h * 0.7), (x - w * 0.5, y - h * 0.8), (x, y - h), (x + w * 0.5, y - h * 0.8),
           (x + w, y - h * 0.7), (x + w, y)]
    c.poly(pts, col, w=1.8)
    c.rect(x - w - 3, y, x + w + 3, y + 4, sill, w=1.2)


def palazzo(c, x, base, w, h, wall, rng, water=True, night=0.0, lit=None, flowers=True):
    """A Venetian house standing in the water: pastel wall, ogee windows, funnel chimney."""
    dark = mix(wall, OUT, 0.25)
    c.rect(x, base - h, x + w, base + 2, wall, w=2.5)
    c.rect(x - 3, base - h - 8, x + w + 3, base - h, mix(wall, (255, 255, 255), 0.4), w=2)
    # weathering patches
    for _ in range(2):
        px, py = x + rng.uniform(10, w - 30), base - rng.uniform(30, h - 30)
        c.ellipse(px, py, rng.uniform(8, 18), rng.uniform(5, 10), mix(wall, (255, 255, 255), 0.15), ol=None)
    floors = max(1, int((h - 50) / 70))
    shut = [(70, 120, 80), (60, 100, 70), (120, 70, 50)][int(rng.integers(3))]
    for f in range(floors):
        fy = base - 62 - f * 70
        nwin = max(1, int(w / 46))
        gap = w / nwin
        for k in range(nwin):
            wx = x + gap * (k + 0.5)
            col = (60, 58, 80)
            if lit is not None and rng.random() < 0.55:
                col = mix(col, (255, 210, 120), lit)
            gothic_window(c, wx, fy, 9, 38, col, shutters=shut if rng.random() < 0.4 else None)
            if flowers and f == 0 and rng.random() < 0.4:
                c.rect(wx - 12, fy + 2, wx + 12, fy + 9, (150, 90, 60), w=1.5)
                for fx in (-7, 0, 7):
                    c.circle(wx + fx, fy, 4, [(230, 70, 90), (250, 160, 60), (240, 100, 160)][int(rng.integers(3))],
                             ol=None)
    if w > 120 and rng.random() < 0.6:
        bx = x + w / 2
        c.rect(bx - 34, base - 62 - 70 + 4, bx + 34, base - 62 - 70 + 12, STONE, w=1.5)
        for k in range(7):
            c.line([(bx - 30 + k * 10, base - 62 - 70 + 4), (bx - 30 + k * 10, base - 62 - 70 - 14)], STONE, 3)
        c.line([(bx - 34, base - 62 - 70 - 14), (bx + 34, base - 62 - 70 - 14)], STONE, 3)
    if water:
        dx = x + w * rng.uniform(0.3, 0.7)
        c.rect(dx - 18, base - 44, dx + 18, base + 2, (54, 50, 64), w=2, r=17)
        c.rect(x, base - 10, x + w, base + 2, mix(wall, (60, 110, 90), 0.5), ol=None)
    for _ in range(int(rng.integers(1, 3))):
        chimney(c, x + rng.uniform(16, w - 16), base - h - 8, 1.0, mix(wall, (200, 90, 70), 0.5))


def rialto(c, x, base, s=1.0, col=STONE, shade=STONE_D):
    """The Rialto Bridge seen face-on: one great arch, shop arcades and the central portico.

    Only the stone is drawn, so whatever was drawn before shows through the arch.
    (x, base) = centre of the arch at the waterline. ~900 wide.
    """
    c.push(x, base, s)
    span, rise = 340, 170
    # deck/body outline: arch underside from (-span, 0) to (span, 0)
    arch = [(span * math.cos(a), -rise * math.sin(a)) for a in np.linspace(0, math.pi, 30)]
    deck_y = -rise - 40
    outer = [(-450, 0), (-450, -60), (-300, deck_y + 30), (0, deck_y), (300, deck_y + 30), (450, -60), (450, 0),
             (span, 0)] + arch + [(-span, 0)]
    c.poly(outer, col, w=3)
    # arch ring stones
    inner = [((span + 22) * math.cos(a), -(rise + 22) * math.sin(a)) for a in np.linspace(0, math.pi, 30)]
    c.line(inner, shade, 3, cap=False)
    for a in np.linspace(0.1, math.pi - 0.1, 13):
        c.line([(span * math.cos(a), -rise * math.sin(a)), ((span + 22) * math.cos(a), -(rise + 22) * math.sin(a))],
               shade, 2, cap=False)
    # balustrade
    c.line([(-450, -66), (-300, deck_y + 24), (0, deck_y - 6), (300, deck_y + 24), (450, -66)], shade, 3, cap=False)
    # shop arcades on the ramps
    for side in (-1, 1):
        for k in range(5):
            u = (k + 0.5) / 5
            ax = side * lerp(70, 300, u)
            ay = lerp(deck_y, deck_y + 30, u) - 10
            c.rect(ax - 18, ay - 50, ax + 18, ay, shade, w=2)
            c.rect(ax - 10, ay - 40, ax + 10, ay, (90, 80, 90), w=1.5, r=10)
        roof = [(side * 50, deck_y - 60), (side * 310, deck_y - 22), (side * 310, deck_y - 6), (side * 50, deck_y - 44)]
        c.poly(roof, (200, 110, 80), w=2)
    # central portico
    c.rect(-56, deck_y - 80, 56, deck_y + 4, col, w=2.5)
    c.rect(-24, deck_y - 62, 24, deck_y + 4, (90, 80, 90), w=2, r=22)
    c.poly([(-66, deck_y - 80), (0, deck_y - 118), (66, deck_y - 80)], col, w=2.5)
    c.circle(0, deck_y - 94, 8, shade, w=1.5)
    for sx in (-40, 40):
        c.rect(sx - 4, deck_y - 76, sx + 4, deck_y + 2, shade, ol=None)
    c.pop()


def furnace(c, x, y, s=1.0, t=0.0, heat=1.0):
    """Glassmaker's furnace: brick dome with a glowing mouth. (x, y) = bottom centre."""
    c.push(x, y, s)
    br = (150, 84, 62)
    pts = [(160 * math.cos(a), -40 - 190 * math.sin(a)) for a in np.linspace(0, math.pi, 24)]
    c.poly([(170, 0)] + pts + [(-170, 0)], br, w=3)
    for row in range(1, 9):
        yy = -40 - row * 20
        half = 160 * math.sqrt(max(0, 1 - ((yy + 40) / -190) ** 2))
        c.line([(-half + 6, yy), (half - 6, yy)], mix(br, OUT, 0.25), 1.5, cap=False)
        for k in range(-6, 7):
            bx = k * 26 + (13 if row % 2 else 0)
            if abs(bx) < half - 10:
                c.line([(bx, yy), (bx, yy + 20)], mix(br, OUT, 0.25), 1.5, cap=False)
    flick = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7.3)
    mouth = [(70 * math.cos(a), -70 - 80 * math.sin(a)) for a in np.linspace(0, math.pi, 16)]
    c.poly([(70, -60)] + mouth + [(-70, -60)], mix((120, 40, 20), (255, 200, 90), heat * flick), w=3)
    c.poly([(50, -64)] + [(50 * math.cos(a), -70 - 56 * math.sin(a)) for a in np.linspace(0, math.pi, 12)] +
           [(-50, -64)], mix((160, 60, 30), (255, 245, 190), heat * flick), ol=None)
    for k in range(3):
        fx = -30 + k * 30
        fh = 30 + 16 * math.sin(t * 9 + k * 2)
        c.poly([(fx - 14, -64), (fx, -64 - fh * heat), (fx + 14, -64)], mix((200, 80, 40), (255, 140, 40), heat),
               ol=None)
    c.rect(-90, -64, 90, -50, (120, 110, 110), w=2.5)
    c.rect(-176, -14, 176, 0, (110, 100, 100), w=2.5)
    c.pop()


def radio(c, x, y, s=1.0, on=0.0, t=0.0, talk=0.0):
    """An old wooden radio; (x, y) = bottom centre."""
    c.push(x, y, s)
    wood = (156, 96, 56)
    c.rect(-70, -96, 70, 0, wood, w=3, r=16)
    c.rect(-56, -82, 6, -14, (226, 206, 160), w=2, r=8)
    for k in range(5):
        c.line([(-50, -72 + k * 12), (0, -72 + k * 12)], mix((226, 206, 160), OUT, 0.25), 1.5, cap=False)
    c.rect(16, -82, 58, -56, mix((90, 80, 60), (255, 220, 120), on * (0.7 + 0.3 * talk)), w=2, r=4)
    c.line([(24 + 26 * on, -80), (24 + 26 * on, -58)], (200, 40, 40), 2, cap=False)
    c.circle(26, -32, 9, (100, 60, 40), w=2)
    c.circle(48, -32, 9, (100, 60, 40), w=2)
    c.pop()
    if on > 0.5:
        notes(c, x - 20 * s, y - 100 * s, t, k=0.4 + 0.6 * talk)


def stall(c, x, y, s=1.0, rng_seed=3):
    """Carnival stall with a striped awning: fritole doughnuts and masks."""
    c.push(x, y, s)
    c.rect(-110, -92, 110, 0, (170, 110, 70), w=3)
    c.rect(-110, -100, 110, -88, (130, 80, 50), w=2.5)
    for k in range(4):
        c.line([(-110 + k * 73, -86), (-110 + k * 73, -4)], (140, 90, 56), 2, cap=False)
    c.rect(-104, -210, -96, -100, (120, 80, 50), w=2)
    c.rect(96, -210, 104, -100, (120, 80, 50), w=2)
    for k in range(8):
        x0 = -124 + k * 31
        col = RED if k % 2 == 0 else (250, 246, 236)
        c.poly([(x0, -250), (x0 + 31, -250), (x0 + 31, -206), (x0 + 15.5, -194), (x0, -206)], col, w=2)
    c.line([(-124, -250), (124, -250)], OUT, 3)
    # pile of fritole
    for k, (dx, dy) in enumerate(((-60, -100), (-40, -100), (-20, -100), (-50, -118), (-30, -118), (-40, -136))):
        fritola(c, dx, dy, 11, k)
    # masks on display
    mask(c, 40, -150, 0.8)
    mask(c, 74, -176, 0.7, col=(70, 120, 210), feather=(240, 200, 80))
    mask(c, 50, -116, 0.7, col=(250, 220, 80), feather=(220, 70, 120))
    c.text(0, -64, "FRITOLE", 15, (255, 240, 200), stroke=1.5)
    c.pop()


def cafe_table(c, x, y, s=1.0, cloth=(250, 250, 246)):
    c.push(x, y, s)
    c.line([(0, -46), (0, 0)], (60, 60, 70), 4)
    c.line([(-16, 0), (16, 0)], (60, 60, 70), 4)
    c.ellipse(0, -48, 34, 8, cloth, w=2.5)
    for side in (-1, 1):
        cx = side * 48
        c.line([(cx, -30), (cx, 0)], (80, 70, 60), 3)
        c.line([(cx + side * 10, -60), (cx + side * 10, 0)], (80, 70, 60), 3)
        c.line([(cx - 8, -30), (cx + side * 12, -30)], (80, 70, 60), 3)
    c.pop()


def lamp_post(c, x, y, s=1.0, lit=0.0):
    c.push(x, y, s)
    c.rect(-4, -190, 4, 0, (50, 50, 60), w=1.5)
    c.rect(-10, -14, 10, 0, (50, 50, 60), w=1.5)
    for side in (-1, 1):
        c.line([(0, -170), (side * 26, -176)], (50, 50, 60), 3)
        c.poly([(side * 26 - 9, -176), (side * 26 + 9, -176), (side * 26 + 6, -200), (side * 26 - 6, -200)],
               mix((230, 220, 180), (255, 230, 140), lit), w=2)
    c.pop()


def murano_isle(c, x, y, s=1.0):
    """Murano on the horizon: low coloured houses, a lighthouse and a brick bell tower."""
    c.push(x, y, s)
    rng = np.random.default_rng(12)
    xx = -200
    while xx < 200:
        w = rng.uniform(26, 46)
        h = rng.uniform(26, 50)
        col = [(226, 150, 110), (236, 200, 130), (220, 120, 110), (240, 220, 190)][int(rng.integers(4))]
        c.rect(xx, -h, xx + w, 0, col, w=1.5)
        c.poly([(xx - 2, -h), (xx + w / 2, -h - 10), (xx + w + 2, -h)], (180, 80, 60), w=1.5)
        xx += w
    c.rect(150, -110, 168, 0, BRICK, w=1.5)
    c.poly([(148, -110), (159, -136), (170, -110)], (100, 160, 130), w=1.5)
    c.rect(-190, -90, -176, 0, (250, 250, 250), w=1.5)
    c.rect(-192, -100, -174, -90, (60, 60, 70), w=1.5)
    c.rect(-60, -80, -48, -40, (150, 90, 70), w=1.5)
    c.pop()
