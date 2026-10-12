"""Props and new characters for "Whiskers and the Chocolate Mountain" (Zermatt).

Everything uses the flat cartoon style of draw.py: local space, origin at the
feet / base, y up is negative.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease

# ------------------------------------------------------------- palettes

ROCK = (128, 116, 120)
ROCK_D = (88, 80, 92)
SNOW = (250, 250, 255)
SNOW_SH = (204, 214, 238)

MATTER_DAY = dict(rock=(132, 120, 126), rock_d=(92, 84, 98), snow=(250, 250, 255), snow_sh=(206, 214, 238),
                  ol=(70, 60, 74))
MATTER_CHOC = dict(rock=(132, 84, 50), rock_d=(98, 58, 34), snow=(255, 246, 228), snow_sh=(236, 214, 186),
                   ol=(64, 36, 24))


def matter_pal(k_glow=0.0, glow=(255, 150, 140), night=0.0, nightcol=(60, 70, 120)):
    """Matterhorn palette: day colours pushed toward an alpenglow colour and/or night."""
    p = {}
    for key, col in MATTER_DAY.items():
        if key == "ol":
            p[key] = col
            continue
        g = 0.75 if key.startswith("snow") else 0.45
        cc = mix(col, glow, k_glow * g)
        p[key] = mix(cc, nightcol, night * (0.55 if key.startswith("snow") else 0.65))
    return p


def _pts(x, base, s, pts):
    return [(x + px * s, base + py * s) for px, py in pts]


# The famous silhouette: a crooked pyramid with its summit hooked to the right.
MATTER_SIL = [(-330, 0), (-250, -70), (-200, -120), (-160, -175), (-128, -228), (-96, -288), (-70, -340),
              (-44, -392), (-22, -428), (-2, -452), (14, -458), (30, -446), (40, -420), (56, -380), (74, -330),
              (96, -286), (124, -250), (150, -226), (190, -186), (236, -132), (290, -70), (360, 0)]
MATTER_EDGE = [(14, -458), (8, -400), (0, -330), (-6, -250), (2, -170), (10, -90), (14, 0)]   # front ridge


def matterhorn(c, x, base, s=1.0, pal=None, glow_rim=None, skirt=True):
    """The Matterhorn. s=1 is ~460 px tall. pal from matter_pal()."""
    p = pal or MATTER_DAY
    ol = p["ol"]
    sil = _pts(x, base, s, MATTER_SIL)
    c.poly(sil, p["rock"], ol=ol, w=2.5)
    # shaded right (north-east) face
    c.poly(_pts(x, base, s, MATTER_EDGE) + _pts(x, base, s, MATTER_SIL[::-1][:12]), p["rock_d"], ol=None)
    # snow: streaks and ledges, more on the left face
    snow_bits = [
        [(-2, -452), (14, -458), (24, -440), (12, -420), (4, -400), (-10, -410), (-20, -428)],
        [(-60, -350), (-40, -366), (-20, -352), (-12, -320), (-30, -330), (-50, -322)],
        [(-112, -262), (-80, -280), (-44, -268), (-20, -240), (-50, -248), (-90, -240)],
        [(-170, -168), (-130, -190), (-80, -178), (-40, -150), (-90, -152), (-140, -140)],
        [(-250, -70), (-200, -96), (-140, -88), (-90, -64), (-150, -60), (-210, -50)],
        [(-24, -300), (-8, -310), (-4, -270), (-16, -262)],
    ]
    for bit in snow_bits:
        c.poly(_pts(x, base, s, bit), p["snow"], ol=None)
    for bit in ([(30, -420), (52, -390), (44, -370), (28, -392)],
                [(70, -320), (100, -286), (90, -272), (64, -300)],
                [(130, -244), (170, -208), (150, -200), (120, -226)],
                [(200, -170), (250, -120), (230, -112), (190, -150)],
                [(270, -84), (320, -36), (290, -34), (256, -70)]):
        c.poly(_pts(x, base, s, bit), p["snow_sh"], ol=None)
    if glow_rim is not None:
        col, k = glow_rim
        if k > 0.01:
            rim = _pts(x, base, s, MATTER_SIL[:12])
            c.line(rim, mix(p["rock"], col, k), 4 * s + 1, cap=False)
    c.poly(sil, None, ol=ol, w=2.5)
    if skirt:
        # glacier / snow skirt at the foot
        c.poly(_pts(x, base, s, [(-330, 0), (-260, -40), (-180, -22), (-80, -50), (20, -24), (120, -46),
                                 (240, -20), (360, 0)]), p["snow"], ol=ol, w=2)
        c.poly(_pts(x, base, s, [(20, -24), (120, -46), (240, -20), (360, 0), (40, 0)]), p["snow_sh"], ol=None)


def choc_matterhorn(c, x, y, s=1.0):
    """A little chocolate Matterhorn (a sweet), base centre at x, y. s=1 is ~60 px tall."""
    k = s * 0.13
    matterhorn(c, x, y, k, MATTER_CHOC, skirt=False)
    c.rect(x - 46 * s, y - 2, x + 50 * s, y + 6 * s, (110, 64, 36), w=2, r=2)


def peak(c, x, base, w, h, col=(120, 128, 160), shade=(96, 100, 134), snow=SNOW, cap=0.35, ol=None):
    """A simple background mountain."""
    top = (x, base - h)
    c.poly([(x - w / 2, base), top, (x + w / 2, base)], col, ol=ol, w=2)
    c.poly([top, (x + w / 2, base), (x + w * 0.1, base)], shade, ol=None)
    yb = base - h * (1 - cap)
    lx, rx = lerp(x, x - w / 2, cap), lerp(x, x + w / 2, cap)
    c.poly([top, (rx, yb), (lerp(rx, lx, 0.3), yb - 10), (lerp(rx, lx, 0.5), yb + 12),
            (lerp(rx, lx, 0.75), yb - 6), (lx, yb)], snow, ol=None)


# ------------------------------------------------------------- village

LARCH = (104, 62, 40)
LARCH_D = (74, 42, 28)
STONE = (178, 172, 166)
SLATE = (118, 116, 124)
GERANIUM = (230, 40, 54)


def geraniums(c, x0, x1, y, t=0.0, s=1.0):
    """A window box overflowing with red geraniums."""
    c.rect(x0, y, x1, y + 12 * s, (150, 96, 56), w=2, r=2)
    n = max(2, int((x1 - x0) / (12 * s)))
    for k in range(n + 1):
        px = lerp(x0 + 4, x1 - 4, k / n)
        c.circle(px, y - 2 + 3 * math.sin(k * 2.3), 6.5 * s, (60, 130, 60), ol=None)
    for k in range(n):
        px = lerp(x0 + 8, x1 - 8, (k + 0.5) / n)
        py = y - 8 * s + 3 * math.sin(k * 1.7)
        c.circle(px, py, 5.5 * s, GERANIUM, w=1.5)
        c.circle(px - 3, py - 2, 2, (255, 120, 120), ol=None)


def chalet(c, x, y, s=1.0, wall=LARCH, floors=2, wide=1.0, flowers=True, lit=False, sign=None):
    """A dark larch-wood Zermatt chalet on a stone base. x is the centre, y the ground."""
    c.push(x, y, s)
    hw = 110 * wide
    fh = 70
    base_h = 60
    top = -base_h - floors * fh
    # stone ground floor
    c.rect(-hw, -base_h, hw, 0, STONE, w=2.5)
    for yy in (-40, -20):
        for xx in range(int(-hw) + 18, int(hw), 36):
            c.line([(xx + (10 if yy == -40 else 0), yy), (xx + 20 + (10 if yy == -40 else 0), yy)],
                   mix(STONE, (0, 0, 0), 0.18), 2, cap=False)
    # wooden floors
    c.rect(-hw + 6, top, hw - 6, -base_h, wall, w=2.5)
    for yy in range(int(top) + 12, -base_h, 12):
        c.line([(-hw + 8, yy), (hw - 8, yy)], mix(wall, (0, 0, 0), 0.22), 1.5, cap=False)
    # gable roof with wide overhang
    peak_y = top - 70 * wide
    c.poly([(-hw - 34, top + 6), (0, peak_y), (hw + 34, top + 6)], SLATE, w=2.5)
    c.poly([(-hw - 34, top + 6), (0, peak_y), (0, peak_y + 14), (-hw - 20, top + 14)],
           mix(SLATE, (255, 255, 255), 0.15), ol=None)
    c.poly([(-hw + 10, top), (0, peak_y + 14), (hw - 10, top)], wall, ol=OUT, w=2)
    c.circle(0, top - 26 * wide, 9, (240, 236, 220), w=2)        # round gable window
    # windows with white frames, shutters and geraniums
    win_col = (255, 222, 140) if lit else (70, 86, 110)
    for f in range(floors):
        wy = -base_h - f * fh - 52
        for wx in np.linspace(-hw + 44, hw - 44, max(2, int(2 * wide) + 1)):
            c.rect(wx - 14, wy, wx + 14, wy + 30, win_col, ol=(250, 248, 240), w=3)
            c.line([(wx, wy), (wx, wy + 30)], (250, 248, 240), 2, cap=False)
            c.rect(wx - 24, wy, wx - 15, wy + 30, (60, 110, 70), w=1.5)
            c.rect(wx + 15, wy, wx + 24, wy + 30, (60, 110, 70), w=1.5)
            if flowers:
                geraniums(c, wx - 22, wx + 22, wy + 32)
    # door in the stone base
    c.rect(-18, -46, 18, 0, LARCH_D, w=2.5, r=4)
    c.circle(10, -22, 2.5, (230, 200, 90), ol=None)
    if sign:
        c.rect(-hw + 16, -base_h - 4, hw - 16, -base_h + 18, (250, 244, 226), w=2, r=3)
        c.text(0, -base_h + 7, sign, 15, (110, 50, 40))
    c.pop()


def pine(c, x, y, s=1.0, col=(46, 104, 72), dark=(32, 80, 58)):
    c.push(x, y, s)
    c.rect(-6, -24, 6, 0, (100, 70, 50), w=2)
    for k, (w, h) in enumerate(((52, 50), (42, 46), (30, 42))):
        yy = -20 - k * 34
        c.poly([(-w, yy), (0, yy - h - 20), (w, yy)], col, w=2)
        c.poly([(0, yy - h - 20), (w, yy), (w * 0.2, yy)], dark, ol=None)
    c.pop()


def edelweiss(c, x, y, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, -18)], (110, 150, 100), 2.5)
    for k in range(7):
        a = k * math.tau / 7 - math.pi / 2
        c.ellipse(math.cos(a) * 7, -22 + math.sin(a) * 7, 5, 5, (246, 246, 236), w=1.2)
    c.circle(0, -22, 3.5, (236, 210, 90), w=1)
    c.pop()


def meadow_flowers(c, rng, x0, x1, y0, y1, n, cols=((250, 250, 250), (250, 220, 70), (200, 120, 220),
                                                     (90, 130, 230), (240, 90, 100))):
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        col = cols[rng.integers(len(cols))]
        r = rng.uniform(2, 4) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        c.circle(x, y, r, col, ol=None)


# ------------------------------------------------------------- characters

WOOL = (250, 248, 240)
WOOL_SH = (226, 222, 214)
SHEEP_BLACK = (36, 30, 36)
HORN = (226, 206, 168)


def sheep(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, seed=5.0, horns=True,
          look=(0.0, 0.0), tilt=0.0, hop=0.0, wool=WOOL, blush=False):
    """A Valais black-nosed sheep: a big cloud of wool, black face, black ears and knees."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y - hop, s, flip=face < 0)
    by = -70
    sh = mix(wool, (150, 150, 160), 0.25)

    def leg(lx, ph, col):
        sw = math.sin(walk + ph) if walk else 0.0
        lift = -max(0.0, math.cos(walk + ph)) * 6 if walk else 0.0
        foot = (lx + sw * 10, lift)
        c.stroke([(lx, by + 20), foot], col, 13)
        c.stroke([(lerp(lx, foot[0], 0.55), by + 20 + (foot[1] - by - 20) * 0.55), foot], SHEEP_BLACK, 13)
        c.ellipse(foot[0] + 2, foot[1] - 2, 8, 5, SHEEP_BLACK, w=2)

    leg(-40, math.pi, sh)
    leg(34, 0, sh)
    # wool body: a cloud of overlapping puffs
    puffs = [(-56, -6, 26), (-36, -26, 28), (-8, -32, 30), (22, -28, 28), (46, -10, 24), (40, 14, 24),
             (10, 22, 26), (-24, 20, 26), (-52, 14, 22)]
    for px, py, r in puffs:
        c.circle(px, by + py, r, wool, w=2.5)
    c.ellipse(-4, by - 2, 56, 34, wool, ol=None)
    for px, py, r in puffs[:4]:
        c.circle(px + 3, by + py + 4, r * 0.55, mix(wool, (255, 255, 255), 0.5), ol=None)
    c.circle(-66, by - 14, 9, wool, w=2)                          # tail puff
    leg(-24, 0, wool)
    leg(48, math.pi, wool)
    # head
    hx, hy = 64 + tilt * 4, by - 34 + tilt * 6
    # ears stick out sideways
    c.ellipse(hx - 26, hy - 4, 16, 7, SHEEP_BLACK, w=2)
    c.ellipse(hx + 24, hy - 2, 15, 7, SHEEP_BLACK, w=2)
    c.ellipse(hx, hy + 6, 22, 28, SHEEP_BLACK, w=2.5)
    c.ellipse(hx + 2, hy + 26, 15, 11, SHEEP_BLACK, ol=None)
    # curly horns
    if horns:
        for side in (-1, 1):
            cx_, cy_ = hx + side * 18, hy - 18
            pts = [(cx_ + side * 8 * u * math.cos(u * 5.5), cy_ + 8 * u * math.sin(u * 5.5)) for u in np.linspace(0.2, 1.2, 10)]
            c.stroke(pts, HORN, 5, ol=(120, 100, 70))
    # woolly topknot
    for dx, dy, r in ((-14, -22, 11), (0, -28, 12), (14, -22, 11), (-6, -16, 9), (8, -16, 9)):
        c.circle(hx + dx, hy + dy, r, wool, w=2)
    for dx, dy, r in ((-6, -16, 9), (8, -16, 9), (0, -22, 10)):
        c.circle(hx + dx, hy + dy, r, wool, ol=None)
    # eyes: white so they read on the black face
    for ex in (hx - 9, hx + 9):
        ey = hy + 2
        if eyes == "closed":
            c.arc(ex, ey, 5.5, 4, 20, 160, (240, 240, 240), 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 5.5, 5, 200, 340, (240, 240, 240), 2.5)
        elif eyes == "sad":
            c.ellipse(ex, ey, 5.5, 6.5, (255, 255, 255), w=1.5)
            c.ellipse(ex + look[0] * 1.5, ey + 1.5, 3.2, 4.2, (40, 30, 30), ol=None)
            c.line([(ex - 6, ey - 9 + (2 if ex < hx else -2)), (ex + 6, ey - 9 + (-2 if ex < hx else 2))],
                   (240, 240, 240), 2)
        else:
            big = 1.2 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 5.5 * big, 6.5 * big, (255, 255, 255), w=1.5)
            c.ellipse(ex + 0.8 + look[0] * 1.5, ey + 0.5 + look[1] * 1.5, 3.2, 4.2, (40, 30, 30), ol=None)
            c.circle(ex + 1.8 + look[0] * 1.5, ey - 1.2 + look[1] * 1.5, 1.2, (255, 255, 255), ol=None)
    if blush:
        for ex in (hx - 14, hx + 14):
            c.ellipse(ex, hy + 14, 5, 3, (210, 110, 130), ol=None)
    # nose + mouth (light so they read on black)
    c.ellipse(hx + 2, hy + 20, 5, 3, (90, 80, 90), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 2, hy + 28, 5 + 2 * mouth, 2 + 5 * mouth, (200, 90, 110), w=1.5)
    else:
        c.arc(hx + 2, hy + 24, 6, 4, 20, 160, (170, 150, 160), 2)
    c.pop()


COW = dict(body=(150, 92, 58), patch=(250, 244, 234), muzzle=(240, 180, 176), dark=(104, 60, 36))


def berta(c, x, y, s=1.0, t=0.0, mouth=0.0, eyes="open", seed=6.0, arm=0.0, ring=0.0, laugh=False):
    """Berta the chocolatier cow, seen from the counter up (x, y = counter top, centre)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = COW
    c.push(x, y + (abs(math.sin(t * 12)) * 4 if laugh else 0), s)
    # body + apron
    c.ellipse(0, -40, 110, 110, p["body"], w=3)
    c.ellipse(-50, -80, 34, 40, p["patch"], ol=None)
    c.poly([(-62, -100), (62, -100), (80, 0), (-80, 0)], (250, 250, 252), w=2.5)
    c.rect(-34, -64, 34, -30, (232, 232, 238), w=2, r=4)                # apron pocket
    c.ellipse(0, -46, 14, 10, (110, 64, 36), ol=None)                    # chocolate smudge
    # arms
    ang = arm
    for side in (-1, 1):
        ax, ay = side * 92, -110
        if side == 1:
            hx_, hy_ = ax + 30 + 30 * ang, ay + 70 - 120 * ang
        else:
            hx_, hy_ = ax - 20, ay + 100
        c.stroke([(ax, ay), (hx_, hy_)], p["body"], 30)
        c.ellipse(hx_, hy_, 16, 14, p["dark"], w=2.5)
    # big bell on a strap
    c.rect(-44, -158, 44, -146, (200, 50, 60), w=2.5, r=4)
    for k in range(4):
        c.circle(-30 + 20 * k, -152, 3, (250, 230, 120), ol=None)
    sw = 0.3 * math.sin(t * 6) * ring
    bx, by = 0 + 30 * sw, -118
    c.poly([(bx - 20, by - 26), (bx + 20, by - 26), (bx + 34, by + 14), (bx - 34, by + 14)], (226, 180, 70), w=2.5)
    c.ellipse(bx, by + 14, 34, 8, (180, 130, 50), w=2.5)
    c.circle(bx + 10 * sw, by + 20, 6, (120, 90, 40), w=2)
    # head
    hx, hy = 0, -240
    for side in (-1, 1):
        c.ellipse(hx + side * 72, hy - 20, 26, 12, p["body"], w=2.5)          # ears
        c.ellipse(hx + side * 72, hy - 20, 16, 6, p["muzzle"], ol=None)
        c.poly([(hx + side * 30, hy - 56), (hx + side * 54, hy - 96), (hx + side * 44, hy - 50)],
               (246, 236, 214), w=2)                                         # horns
    c.ellipse(hx, hy, 62, 66, p["body"], w=3)
    c.ellipse(hx + 18, hy - 30, 24, 22, p["patch"], ol=None)
    # little flower crown + headscarf
    c.poly([(hx - 58, hy - 40), (hx, hy - 76), (hx + 58, hy - 40), (hx + 40, hy - 50), (hx, hy - 64),
            (hx - 40, hy - 50)], (210, 50, 60), w=2)
    for k in range(5):
        D.flower(c, hx - 40 + 20 * k, hy - 46 - 10 * math.sin(k / 4 * math.pi) + 26, (255, 255, 255), 0.55)
    c.ellipse(hx, hy + 36, 46, 32, p["muzzle"], w=2.5)
    for nx in (-14, 14):
        c.ellipse(hx + nx, hy + 30, 6, 8, (180, 110, 110), ol=None)
    for ex in (hx - 24, hx + 24):
        ey = hy - 10
        if eyes == "closed" or laugh:
            c.arc(ex, ey + (3 if laugh else 0), 8, 6, 200 if laugh else 20, 340 if laugh else 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 8, 7, 200, 340, OUT, 3)
        else:
            c.ellipse(ex, ey, 9, 11, (255, 255, 255), w=2)
            c.ellipse(ex + 1, ey + 1, 5.5, 7, (70, 40, 30), ol=None)
            c.circle(ex + 2.5, ey - 2.5, 2, (255, 255, 255), ol=None)
        for k in range(3):
            c.line([(ex - 8 + 6 * k, ey - 12), (ex - 10 + 6 * k, ey - 17)], OUT, 1.5, cap=False)  # lashes
    if mouth > 0.05 or laugh:
        m = max(mouth, 0.7 if laugh else 0)
        c.ellipse(hx, hy + 52 + 4 * m, 16, 4 + 10 * m, D.MOUTH, w=2)
        c.ellipse(hx, hy + 56 + 8 * m, 10, 3 + 2 * m, D.TONGUE, ol=None)
    else:
        c.arc(hx, hy + 46, 18, 10, 20, 160, OUT, 2.5)
    c.pop()


def chough(c, x, y, t, s=1.0, face=1, fly=0.0):
    """Alpine chough: glossy black, yellow beak, red legs."""
    c.push(x, y, s, flip=face < 0)
    blk = (34, 32, 44)
    if fly > 0:
        f = math.sin(t * 18)
        c.poly([(-6, -14), (-30, -14 - 26 * f), (8, -16)], blk, w=2)
        c.poly([(0, -14), (22, -14 - 22 * f), (12, -18)], mix(blk, (90, 90, 110), 0.3), w=2)
    c.ellipse(0, -14, 18, 10, blk, w=2)
    c.poly([(-16, -14), (-30, -10), (-28, -18)], blk, w=2)
    c.circle(16, -22, 8, blk, w=2)
    c.poly([(22, -24), (32, -20), (22, -18)], (250, 210, 60), w=1.5)
    c.circle(18, -24, 1.8, (255, 255, 255), ol=None)
    if not fly:
        for lx in (-4, 4):
            c.line([(lx, -6), (lx, 0)], (220, 50, 50), 2.5)
    c.pop()


# ------------------------------------------------------------- objects

WOOD = (214, 160, 98)
WOOD_D = (150, 100, 56)


def alphorn(c, x0, y0, x1, y1, s=1.0, painted=True):
    """A long alphorn: mouthpiece at (x0, y0), the bell resting at (x1, y1), curving up at the end."""
    n = 18
    pts = []
    for i in range(n + 1):
        u = i / n
        px = lerp(x0, x1, u)
        py = lerp(y0, y1, u)
        pts.append((px, py))
    for i in range(n):
        u = i / n
        wdt = (4 + 9 * u ** 2) * s
        c.line([pts[i], pts[i + 1]], OUT, wdt + 5 * s, cap=True)
    for i in range(n):
        u = i / n
        wdt = (4 + 9 * u ** 2) * s
        c.line([pts[i], pts[i + 1]], WOOD, wdt, cap=True)
    # dark bindings
    for u in (0.2, 0.4, 0.6, 0.78):
        px, py = lerp(x0, x1, u), lerp(y0, y1, u)
        c.circle(px, py, (3 + 5 * u ** 2) * s, WOOD_D, ol=None)
    # curved bell turning upward
    dirx = 1 if x1 >= x0 else -1
    bx, by = x1 + dirx * 14 * s, y1 - 22 * s
    c.poly([(x1 - dirx * 4 * s, y1 + 7 * s), (x1 - dirx * 4 * s, y1 - 7 * s), (bx - dirx * 14 * s, by - 6 * s),
            (bx + dirx * 18 * s, by - 6 * s), (x1 + dirx * 14 * s, y1 + 8 * s)], WOOD, w=2.5)
    c.ellipse(bx + dirx * 2 * s, by - 6 * s, 17 * s, 6 * s, (90, 56, 30), w=2.5)
    if painted:
        c.circle(x1 + dirx * 8 * s, y1 - 4 * s, 4 * s, (250, 250, 240), ol=None)
    c.circle(x0, y0, 3.5 * s, (60, 40, 30), ol=None)


def cuckoo_clock(c, x, y, s=1.0, out=0.0, t=0.0, swing=True):
    """A carved cuckoo clock (x, y = top of roof). out: 0..1 how far the bird pops out."""
    c.push(x, y, s)
    wood, dark = (122, 74, 42), (84, 50, 28)
    # pendulum & weights
    a = 0.35 * math.sin(t * 3.2) if swing else 0
    px, py = 0 + math.sin(a) * 110, 120 + math.cos(a) * 110
    c.line([(0, 140), (px, py + 40)], (200, 170, 80), 2.5)
    c.circle(px, py + 46, 12, (230, 190, 80), w=2)
    for wx, wy in ((-30, 220 + 8 * math.sin(t * 0.3)), (30, 196 - 8 * math.sin(t * 0.3))):
        c.line([(wx, 140), (wx, wy)], (170, 160, 150), 1.5, cap=False)
        c.ellipse(wx, wy + 22, 10, 24, (120, 80, 40), w=2)
        for k in range(3):
            c.line([(wx - 8, wy + 12 + 10 * k), (wx + 8, wy + 12 + 10 * k)], dark, 1.5, cap=False)
    # house body
    c.rect(-62, 30, 62, 150, wood, w=2.5)
    c.poly([(-84, 46), (0, -10), (84, 46), (72, 52), (0, 6), (-72, 52)], dark, w=2.5)
    # carved leaves on the roof and a little bird on top
    for k in range(5):
        c.ellipse(-40 + 20 * k, 2 + abs(k - 2) * 10, 10, 6, (60, 110, 60), w=1.5)
    c.circle(0, -12, 7, dark, w=1.5)
    # door
    c.rect(-18, 34, 18, 64, (60, 34, 20), w=2)
    if out > 0.02:
        bx = 0
        by = 50 + 40 * out * 0          # bird slides forward (toward the viewer: we just grow it)
        k = 0.4 + 0.6 * out
        c.push(bx, by, k)
        c.line([(0, 6), (0, 40 * out)], (60, 60, 60), 2, cap=False)
        c.ellipse(0, 0, 20, 14, (110, 140, 190), w=2)
        c.circle(16, -8, 10, (110, 140, 190), w=2)
        c.poly([(24, -10), (40, -6 + 4 * math.sin(t * 20)), (24, -4)], (250, 200, 60), w=1.5)
        c.circle(18, -11, 2.2, OUT, ol=None)
        c.poly([(-18, -2), (-34, -12), (-30, 4)], (90, 116, 170), w=1.5)
        c.pop()
    else:
        c.line([(0, 34), (0, 64)], dark, 1.5, cap=False)
    # clock face
    c.circle(0, 104, 32, (250, 244, 226), w=2.5)
    for k in range(12):
        an = k * math.tau / 12
        c.line([(math.sin(an) * 26, 104 - math.cos(an) * 26), (math.sin(an) * 30, 104 - math.cos(an) * 30)],
               OUT, 2, cap=False)
    ha, ma = t * 0.05, t * 0.6
    c.line([(0, 104), (math.sin(ha) * 16, 104 - math.cos(ha) * 16)], OUT, 3)
    c.line([(0, 104), (math.sin(ma) * 24, 104 - math.cos(ma) * 24)], OUT, 2)
    c.pop()


def rot(pts, ang, ox=0.0, oy=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(ox + px * ca - py * sa, oy + px * sa + py * ca) for px, py in pts]


def wheel(c, x, y, r, t_spin=0.0):
    c.circle(x, y, r, (40, 40, 46), w=2.5)
    c.circle(x, y, r * 0.5, (180, 180, 186), w=2)
    for k in range(3):
        a = t_spin + k * math.tau / 3
        c.line([(x, y), (x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45)], (90, 90, 96), 2, cap=False)


def sheep_trailer(c, x, y, s=1.0, t=0.0, spin=0.0, night=False, heads=()):
    """Little green truck pulling a wooden sheep trailer. x, y: front bumper on the road."""
    c.push(x, y, s)
    green, gdark = (64, 128, 86), (44, 96, 64)
    # trailer
    tx0, tx1 = -560, -210
    c.rect(tx0, -190, tx1, -40, (170, 116, 70), w=3, r=6)
    for k in range(6):
        yy = -176 + 22 * k
        c.rect(tx0 + 10, yy, tx1 - 10, yy + 10, (128, 84, 48) if k % 2 else (196, 140, 90), ol=None)
    for hx, hy, face in heads:
        pass
    c.rect(tx0, -196, tx1, -186, (110, 70, 40), w=2.5, r=3)
    c.line([(tx1, -60), (-170, -60)], OUT, 6)
    wheel(c, tx0 + 90, -30, 30, spin)
    wheel(c, tx1 - 90, -30, 30, spin)
    # truck
    c.rect(-210, -120, 0, -36, green, w=3, r=10)
    c.poly([(-120, -120), (-110, -210), (-30, -210), (-6, -140), (0, -120)], green, w=3)
    c.poly([(-104, -200), (-38, -200), (-18, -140), (-104, -140)], (255, 232, 160) if night else (170, 210, 230), w=2.5)
    c.rect(-206, -150, -124, -122, gdark, w=2, r=3)
    c.rect(-12, -96, 4, -80, (255, 240, 170) if night else (250, 250, 220), w=2, r=3)
    c.rect(-210, -56, 0, -44, (70, 70, 76), ol=None)
    wheel(c, -160, -30, 30, spin)
    wheel(c, -50, -30, 30, spin)
    if night:
        c.poly([(4, -92), (260, -140), (260, -30)], (255, 246, 190), ol=None)
    c.pop()


def taxi(c, x, y, s=1.0, spin=0.0):
    """A tiny boxy Zermatt electric taxi. x, y: centre of the base on the road."""
    c.push(x, y, s)
    body, trim = (238, 242, 246), (60, 150, 120)
    c.rect(-120, -150, 110, -30, body, w=3, r=12)
    c.rect(-120, -60, 110, -44, trim, ol=None)
    c.rect(-104, -136, -16, -76, (160, 210, 236), w=2.5, r=6)
    c.rect(-4, -136, 70, -76, (160, 210, 236), w=2.5, r=6)
    c.poly([(80, -136), (110, -110), (110, -76), (80, -76)], (160, 210, 236), w=2.5)
    c.rect(-120, -150, 110, -30, None, w=3, r=12)
    c.rect(-60, -166, 20, -150, (250, 220, 70), w=2, r=3)
    c.text(-20, -158, "TAXI", 11, OUT)
    c.circle(104, -46, 6, (255, 240, 170), w=2)
    wheel(c, -70, -26, 24, spin)
    wheel(c, 64, -26, 24, spin)
    c.pop()


def taxi_windows(c, x, y, s=1.0):
    """Redraw only the window frames (to put over passengers)."""
    c.push(x, y, s)
    c.rect(-104, -136, -16, -76, None, w=2.5, r=6)
    c.rect(-4, -136, 70, -76, None, w=2.5, r=6)
    c.rect(-120, -76, 110, -30, (238, 242, 246), w=3, r=10)
    c.rect(-120, -60, 110, -44, (60, 150, 120), ol=None)
    c.circle(104, -46, 6, (255, 240, 170), w=2)
    c.pop()


def cog_car(c, x, y, ang, length=300, height=120, col=(206, 40, 44), front=False):
    """One car of the red cog railway, drawn tilted by `ang` (radians, uphill to the right).
    (x, y) is the centre of the car's floor on the track."""
    def P(pts):
        return rot(pts, -ang, x, y)
    hl = length / 2
    c.poly(P([(-hl, -height), (hl - (30 if front else 0), -height), (hl, -height + 30 if front else -height),
              (hl, 0), (-hl, 0)]), col, w=3)
    c.poly(P([(-hl, -20), (hl, -20), (hl, 0), (-hl, 0)]), mix(col, (0, 0, 0), 0.3), ol=None)
    c.poly(P([(-hl, -height), (hl, -height), (hl, -height + 14), (-hl, -height + 14)]),
           (240, 240, 240), ol=None)
    for k in range(3):
        wx = -hl + 24 + k * (length - 40) / 3
        c.poly(P([(wx, -height + 26), (wx + (length - 80) / 3, -height + 26), (wx + (length - 80) / 3, -height + 76),
                  (wx, -height + 76)]), (190, 226, 244), w=2.5)
    c.poly(P([(-hl, -height), (hl - (30 if front else 0), -height), (hl, -height + 30 if front else -height),
              (hl, 0), (-hl, 0)]), None, w=3)
    # pantograph
    if front:
        a, b = P([(-40, -height)])[0], P([(0, -height - 40)])[0]
        c.line([a, b], (60, 60, 60), 3)
        cc = P([(20, -height)])[0]
        c.line([b, cc], (60, 60, 60), 3)
    for wx in (-hl + 50, hl - 50):
        px, py = P([(wx, 4)])[0]
        wheel(c, px, py, 16)


def thought_bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 9), (0.65, 14)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def sound_rings(c, x, y, t0, t, col=(255, 240, 190), n=4, speed=160.0, maxr=420.0, face=1):
    """Expanding arcs of sound coming from a point (the alphorn's bell)."""
    if t < t0:
        return
    for k in range(n):
        r = ((t - t0) * speed + k * maxr / n) % maxr
        a = 1 - r / maxr
        if r < 6:
            continue
        a0, a1 = (-60, 60) if face > 0 else (120, 240)
        c.arc(x, y, r, r * 0.8, a0, a1, mix((120, 100, 80), col, a), max(1.0, 5 * a))


_shade_masks = {}


def shade_bottom(c, tl, t, strength=0.5, top=560):
    """Darken the bottom of the frame softly while a subtitle shows (readability on bright scenes)."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    if k <= 0:
        return
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    if q not in _shade_masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _shade_masks[q] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((20, 16, 30), (0, top * SS, W * SS, H * SS), _shade_masks[q])


def overlay(c, col, alpha):
    if alpha <= 0.003:
        return
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha))
    c.d = ImageDraw.Draw(c.img)
