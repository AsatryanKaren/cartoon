"""Berlin props and characters, in the same flat outlined style as draw.py.

Everything draws in local coordinates (origin on the ground, y up negative)
through Canvas.push, like the cats. Text sizes are multiplied by c.scale,
because Canvas.text does not follow the transform's scale.
"""
import math

import numpy as np

import draw as D
from draw import OUT, mix, lerp, clamp, ease

# ------------------------------------------------------------------ colours
SAND = (236, 218, 170)          # Brandenburg Gate sandstone
SAND_S = (206, 186, 140)
SAND_D = (170, 150, 110)
PATINA = (104, 168, 146)        # green copper of the quadriga
PATINA_D = (66, 120, 104)
STONE = (222, 210, 184)         # Reichstag
STONE_S = (192, 178, 152)
GLASS = (176, 214, 232)
CONCRETE = (236, 236, 240)
CONCRETE_S = (200, 202, 212)
SILVER = (196, 204, 218)
SILVER_D = (150, 158, 176)
BRICK = (184, 78, 56)
BRICK_D = (150, 58, 44)
UYELLOW = (252, 204, 30)        # U-Bahn yellow
UYELLOW_D = (220, 166, 10)
UBLUE = (20, 80, 170)
WALLGREY = (214, 212, 204)
PRETZEL = (176, 100, 44)
PRETZEL_L = (214, 140, 70)
JAM = (210, 30, 50)
RIVER = (70, 116, 160)
RIVER_L = (120, 170, 210)

BERTI = dict(fur=(150, 96, 56), dark=(112, 68, 38), belly=(238, 208, 158), ear=(214, 150, 110),
             crown=(250, 204, 60), bow=(214, 40, 50))
HILDE = dict(fur=(178, 98, 50), dark=(126, 64, 32), snout=(214, 150, 96), apron=(252, 252, 248),
             hat=(255, 255, 255), glass=(60, 60, 80))


def _text(c, x, y, s, size, fill, **kw):
    c.text(x, y, s, size * c.scale, fill, **kw)


# ====================================================================== Berti

def berti(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, arm=0.0, wave=False,
          look=(0.0, 0.0), seed=3.7, flag=False, brush=False, clap=0.0, hop=0.0):
    """Berti the Berlin bear: a round brown bear cub on two legs with a little gold crown.

    arm: 0 = front paw down, 1 = raised (pointing up and forward). wave: waggle the raised paw.
    flag: holds a little Berlin pennant. clap: 0..1 paws together.
    """
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = BERTI
    c.push(x, y - hop, s, flip=face < 0)
    bob = abs(math.sin(walk)) * 3 if walk else 0.0
    # legs
    for lx, ph, col in ((-16, math.pi, p["dark"]), (16, 0.0, p["fur"])):
        sw = math.sin(walk + ph) * 9 if walk else 0.0
        lift = -max(0.0, math.cos(walk + ph)) * 6 if walk else 0.0
        c.stroke([(lx, -40), (lx + sw, -8 + lift)], col, 20)
        c.ellipse(lx + sw + 5, -6 + lift, 15, 8, col, w=2.5)
    # back arm
    c.stroke([(-26, -96 - bob), (-38, -58 - bob)], p["dark"], 15)
    c.circle(-38, -56 - bob, 9, p["dark"], w=2.5)
    # body
    c.ellipse(0, -74 - bob, 42, 48, p["fur"], w=3)
    c.ellipse(8, -66 - bob, 26, 32, p["belly"], ol=None)
    # head
    hx, hy = 8 + 3 * look[0], -140 - bob
    for ex in (-18, 32):
        c.circle(hx + ex, hy - 26, 14, p["fur"], w=3)
        c.circle(hx + ex, hy - 26, 7, p["ear"], ol=None)
    c.ellipse(hx, hy, 38, 34, p["fur"], w=3)
    # crown
    cx0, cy0 = hx + 6, hy - 30
    c.poly([(cx0 - 15, cy0), (cx0 - 17, cy0 - 18), (cx0 - 8, cy0 - 9), (cx0, cy0 - 21), (cx0 + 8, cy0 - 9),
            (cx0 + 17, cy0 - 18), (cx0 + 15, cy0)], p["crown"], w=2)
    for k in (-17, 0, 17):
        c.circle(cx0 + k, cy0 - 19 - (2 if k == 0 else 0), 2.6, (255, 240, 170), w=1.2)
    c.circle(cx0, cy0 - 6, 2.6, (210, 50, 60), ol=None)
    # muzzle, nose, eyes
    c.ellipse(hx + 20, hy + 10, 19, 14, p["belly"], w=2)
    c.ellipse(hx + 30, hy + 2, 7, 5, (40, 28, 26), ol=None)
    c.circle(hx + 28, hy + 0.5, 1.6, (150, 140, 140), ol=None)
    for ex in (hx + 0, hx + 22):
        ey = hy - 9
        if eyes == "closed":
            c.arc(ex, ey, 6, 4, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 3)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 5.5 * big, 6.5 * big, (255, 255, 255), w=2)
            c.ellipse(ex + 1 + look[0] * 1.5, ey + 1 + look[1] * 1.5, 3.4 * big, 4.4 * big, (40, 26, 20), ol=None)
            c.circle(ex + 2 + look[0] * 1.5, ey - 1 + look[1] * 1.5, 1.3, (255, 255, 255), ol=None)
    if mouth > 0.05:
        h = 2 + 8 * mouth
        c.ellipse(hx + 24, hy + 15 + h * 0.4, 7, h, D.MOUTH, w=2)
        c.ellipse(hx + 24, hy + 15 + h * 0.8, 4.5, 2 + 1.5 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 24, hy + 12, 7, 5, 20, 160, OUT, 2)
    # bow tie
    bx, by = hx + 2, hy + 36
    c.poly([(bx, by), (bx - 13, by - 8), (bx - 13, by + 8)], p["bow"], w=2)
    c.poly([(bx, by), (bx + 13, by - 8), (bx + 13, by + 8)], p["bow"], w=2)
    c.circle(bx, by, 4, p["bow"], w=2)
    # front arm
    sx, sy = 26, -98 - bob
    if clap > 0:
        hand = (lerp(40, 30, clap), lerp(-70, -96, clap) - bob)
    else:
        a = math.radians(lerp(80, -40, arm))
        if wave:
            a += 0.35 * math.sin(t * 9)
        hand = (sx + 40 * math.cos(a), sy + 40 * math.sin(a))
    c.stroke([(sx, sy), hand], p["fur"], 15)
    c.circle(hand[0], hand[1], 9.5, p["fur"], w=2.5)
    if clap > 0:
        c.circle(hand[0] - 6, hand[1] + 2, 9, p["dark"], w=2.5)
    if flag:
        fx, fy = hand
        c.line([(fx, fy + 16), (fx, fy - 60)], (90, 70, 50), 3)
        wav = math.sin(t * 5)
        pts = [(fx, fy - 60), (fx + 40, fy - 54 + 3 * wav), (fx, fy - 38)]
        c.poly(pts, (250, 250, 250), w=2)
        c.line([(fx + 1, fy - 58), (fx + 36, fy - 54 + 3 * wav)], (210, 40, 50), 2, cap=False)
        c.circle(fx + 12, fy - 51, 4, (40, 30, 30), ol=None)
    if brush:
        fx, fy = hand
        c.line([(fx - 4, fy + 6), (fx + 26, fy - 30)], (150, 100, 60), 4)
        c.ellipse(fx + 29, fy - 34, 5, 7, (240, 80, 90), w=1.5)
    c.pop()


# ====================================================================== Hilde

def hilde(c, x, y, s=1.0, face=-1, t=0.0, mouth=0.0, eyes="open", lean=0.0, arm=0.0, seed=6.2,
          hold=None):
    """Oma Hilde, a jolly old dachshund, seen behind her counter. (x, y) = counter top centre.

    lean: 0..1 leans over the counter.  arm: 0..1 reaches out.  hold(c, x, y): draws what she holds.
    """
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = HILDE
    c.push(x, y, s, flip=face < 0)
    ly = -10 * lean
    lx = 18 * lean
    # body + apron
    c.ellipse(lx * 0.5, -46 + ly * 0.5, 36, 50, p["fur"], w=3)
    c.poly([(lx * 0.5 - 24, -70 + ly), (lx * 0.5 + 26, -70 + ly), (lx * 0.5 + 30, 0), (lx * 0.5 - 28, 0)],
           p["apron"], w=2.5)
    c.rect(lx * 0.5 - 12, -40 + ly, lx * 0.5 + 12, -26 + ly, mix(p["apron"], (200, 60, 60), 0.6), w=1.5, r=2)
    # head
    hx, hy = 12 + lx, -104 + ly
    c.ellipse(hx - 16, hy + 20, 12, 30, p["dark"], w=2.5)         # far ear
    c.ellipse(hx, hy, 30, 27, p["fur"], w=3)
    c.ellipse(hx + 36, hy + 8, 32, 15, p["snout"], w=2.5)          # long snout
    c.ellipse(hx + 66, hy + 2, 8, 6.5, (40, 28, 26), w=1.5)
    c.circle(hx + 64, hy, 2, (160, 150, 150), ol=None)
    if mouth > 0.05:
        h = 2 + 7 * mouth
        c.ellipse(hx + 44, hy + 20 + h * 0.4, 9, h, D.MOUTH, w=2)
    else:
        c.arc(hx + 46, hy + 15, 12, 5, 20, 160, OUT, 2)
    for ex in (hx + 4, hx + 24):
        ey = hy - 6
        if eyes == "closed":
            c.arc(ex, ey, 5, 3.5, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 2, 5, 5, 200, 340, OUT, 2.5)
        else:
            c.circle(ex, ey, 4.5, (255, 255, 255), w=1.5)
            c.circle(ex + 1, ey + 0.5, 2.6, (40, 26, 20), ol=None)
        c.circle(ex, ey, 9, None, ol=p["glass"], w=2)                # round glasses
    c.line([(hx + 13, hy - 7), (hx + 15, hy - 7)], p["glass"], 2, cap=False)
    # near floppy ear
    c.ellipse(hx - 6, hy + 22, 13, 32, p["dark"], w=2.5)
    # little white paper hat
    c.poly([(hx - 26, hy - 18), (hx + 22, hy - 24), (hx + 16, hy - 44), (hx - 20, hy - 40)], p["hat"], w=2.5)
    c.line([(hx - 24, hy - 24), (hx + 20, hy - 29)], (210, 50, 60), 3, cap=False)
    # paws on the counter / reaching
    reach = arm
    px_, py_ = lerp(30, 90, reach) + lx, lerp(-4, -30, reach) + ly
    c.stroke([(lx * 0.5 + 20, -60 + ly), (px_, py_)], p["fur"], 14)
    c.ellipse(px_ + 4, py_, 10, 7, p["fur"], w=2.5)
    c.ellipse(lx * 0.5 - 18, -4, 10, 7, p["fur"], w=2.5)
    if hold:
        hold(c, px_ + 8, py_ - 6)
    c.pop()


# ====================================================================== food

def pretzel(c, x, y, s=1.0, ang=0.0, bite=0.0):
    """A big Berlin pretzel (centre x, y), about 110 px wide at s=1."""
    c.push(x, y, s)
    col, light = PRETZEL, PRETZEL_L

    def loop(pts, w):
        c.stroke(pts, col, w)
        c.line(pts, light, w * 0.35, cap=False)

    k = np.linspace(0, 1, 18)
    for side in (-1, 1):
        pts = [(side * (12 + 38 * math.sin(math.pi * u)) + side * 6 * u, -30 + 62 * u - 34 * math.sin(math.pi * u) * (1 - u))
               for u in k]
        loop(pts, 14)
    loop([(-30, 26), (0, -4), (30, 26)], 14)
    loop([(-44, 20), (0, 34), (44, 20)], 14)
    rng = np.random.default_rng(3)
    for _ in range(14):
        px, py = rng.uniform(-48, 48), rng.uniform(-30, 32)
        c.rect(px - 1.5, py - 1.5, px + 1.5, py + 1.5, (255, 255, 255), ol=None)
    c.pop()


def pretzel_ring(c, x, y, s=1.0, part="front"):
    """The pretzel worn like a necklace: ring around a neck at (x, y)."""
    c.push(x, y, s)
    if part == "back":
        c.arc(0, 0, 46, 16, 180, 360, OUT, 18)
        c.arc(0, 0, 46, 16, 180, 360, PRETZEL, 12)
    else:
        c.arc(0, 0, 46, 16, 0, 180, OUT, 18)
        c.arc(0, 0, 46, 16, 0, 180, PRETZEL, 12)
        c.arc(0, 0, 46, 16, 20, 160, PRETZEL_L, 4)
        for a in (30, 70, 110, 150):
            r = math.radians(a)
            c.rect(46 * math.cos(r) - 1.5, 16 * math.sin(r) - 1.5, 46 * math.cos(r) + 1.5, 16 * math.sin(r) + 1.5,
                   (255, 255, 255), ol=None)
    c.pop()


def berliner(c, x, y, s=1.0, bite=0.0):
    """Berliner doughnut: round, golden, sugar-dusted, with jam inside."""
    c.push(x, y, s)
    c.ellipse(0, 0, 30, 24, (222, 150, 70), w=2.5)
    c.ellipse(0, 4, 26, 6, (250, 228, 190), ol=None)
    rng = np.random.default_rng(5)
    for _ in range(18):
        px, py = rng.uniform(-22, 22), rng.uniform(-18, 0)
        c.circle(px, py, 1.6, (255, 255, 255), ol=None)
    if bite > 0:
        c.circle(26, -4, 14 * bite, (255, 236, 210), w=2)
        c.circle(24, -4, 8 * bite, JAM, ol=None)
    c.pop()


def currywurst(c, x, y, s=1.0):
    """Sliced sausage with red sauce in a paper tray, with a little wooden fork."""
    c.push(x, y, s)
    c.poly([(-40, -14), (40, -14), (32, 6), (-32, 6)], (250, 250, 246), w=2.5)
    for k in range(5):
        c.ellipse(-26 + k * 13, -16, 8, 6, (190, 100, 70), w=1.5)
    c.ellipse(0, -18, 36, 6, (206, 60, 40), ol=None)
    for k in range(6):
        c.circle(-24 + k * 10, -19, 1.4, (240, 190, 60), ol=None)
    c.line([(18, -18), (34, -40)], (210, 180, 130), 3)
    c.pop()


def jam_blob(c, x, y, s=1.0, k=1.0):
    c.push(x, y, s)
    c.ellipse(0, 0, 13 * k, 9 * k, JAM, w=1.5)
    c.circle(10 * k, 6 * k, 4 * k, JAM, w=1.2)
    c.circle(-6 * k, 9 * k, 3 * k, JAM, ol=None)
    c.circle(-3, -3, 3 * k, (250, 120, 130), ol=None)
    c.pop()


# ====================================================================== snack stand

def imbiss(c, x, base, s=1.0, t=0.0):
    """Hilde's snack stand: counter top at local y -150 (returns nothing)."""
    c.push(x, base, s)
    wood, wood_d = (120, 160, 90), (90, 126, 66)
    # kiosk body
    c.rect(-210, -330, 210, 0, (250, 240, 214), w=3)
    c.rect(-196, -300, 196, -150, (70, 60, 70), w=2.5)              # dark hatch
    # shelves of pretzels and doughnuts inside
    for k in range(4):
        pretzel(c, -150 + k * 46, -268, 0.34)
    c.line([(-190, -246), (190, -246)], (150, 120, 90), 4, cap=False)
    for k in range(5):
        berliner(c, 30 + k * 34, -230, 0.5)
    c.line([(-190, -208), (190, -208)], (150, 120, 90), 4, cap=False)
    # grill with sausages + steam
    c.rect(-180, -196, -40, -176, (60, 60, 66), w=2)
    for k in range(5):
        c.rect(-172 + k * 26, -194, -152 + k * 26, -184, (190, 100, 70), w=1.2, r=4)
    for k in range(3):
        u = (t * 0.5 + k / 3) % 1.0
        c.circle(-140 + k * 40 + 10 * math.sin(t * 2 + k), -200 - 60 * u, 6 + 8 * u,
                 mix((255, 255, 255), (70, 60, 70), u), ol=None)
    # counter
    c.rect(-226, -158, 226, -142, wood, w=3, r=3)
    c.rect(-210, -142, 210, 0, wood_d, w=3)
    for k in range(-200, 210, 40):
        c.line([(k, -138), (k, -4)], mix(wood_d, (0, 0, 0), 0.15), 2, cap=False)
    # striped awning
    for k in range(10):
        x0 = -240 + k * 48
        c.poly([(x0, -360), (x0 + 48, -360), (x0 + 48, -320), (x0, -320)],
               (214, 44, 50) if k % 2 == 0 else (255, 250, 240), w=2)
        c.arc(x0 + 24, -320, 24, 12, 0, 180, OUT, 2)
        c.ellipse(x0 + 24, -320, 23, 11, (214, 44, 50) if k % 2 == 0 else (255, 250, 240), ol=None)
    # sign on top
    c.rect(-170, -420, 170, -362, (250, 210, 60), w=3, r=8)
    _text(c, 0, -391, "IMBISS HILDE", 30, (150, 40, 40))
    # menu board on the side
    c.rect(150, -140, 250, -20, (40, 50, 50), w=2.5, r=4)
    for k, txt in enumerate(("Currywurst", "Brezel", "Berliner")):
        _text(c, 200, -118 + k * 34, txt, 13, (250, 250, 240))
    c.pop()


# ====================================================================== landmarks

def quadriga(c, x, base, s=1.0, col=PATINA, dark=PATINA_D, lw=2.0):
    """The goddess of victory driving four horses, seen from the front (base = top of the gate)."""
    c.push(x, base, s)
    c.rect(-70, -14, 70, 0, mix(col, (255, 255, 255), 0.2), ol=OUT, w=lw)
    # chariot + Victoria behind the horses
    c.rect(-30, -76, 30, -30, dark, ol=OUT, w=lw)
    # wings
    c.poly([(-6, -112), (-44, -150), (-38, -116), (-24, -98)], col, ol=OUT, w=lw)
    c.poly([(6, -112), (44, -150), (38, -116), (24, -98)], col, ol=OUT, w=lw)
    c.poly([(-14, -66), (14, -66), (8, -118), (-8, -118)], col, ol=OUT, w=lw)   # robe
    c.circle(0, -126, 8, col, ol=OUT, w=lw)
    # staff with wreath and little eagle
    c.line([(16, -110), (22, -186)], dark, 3.5, cap=False)
    c.line([(16, -110), (12, -100)], dark, 3.5, cap=False)
    c.circle(22, -180, 10, None, ol=dark, w=3.5)
    c.poly([(14, -196), (22, -204), (30, -196), (22, -190)], dark, ol=None)
    c.line([(10, -110), (16, -110)], col, 4, cap=False)
    # four horses, heads up, outer ones turned out
    for k, hx in enumerate((-51, -17, 17, 51)):
        turn = (-1 if hx < 0 else 1) * (1.0 if abs(hx) > 30 else 0.35)
        c.ellipse(hx, -42, 15, 26, col, ol=OUT, w=lw)                       # chest
        for lx in (-7, 7):
            raised = abs(hx) > 30 and lx * turn > 0
            if raised:
                c.line([(hx + lx, -36), (hx + lx + 9 * turn, -26), (hx + lx + 4 * turn, -16)], dark, 4.5)
            else:
                c.line([(hx + lx, -30), (hx + lx, -12)], dark, 4.5, cap=False)
        c.poly([(hx - 7, -58), (hx + 7, -58), (hx + 6 * turn + 6, -84), (hx + 6 * turn - 6, -84)], col,
               ol=OUT, w=lw)                                                     # neck
        c.ellipse(hx + 8 * turn, -90, 8, 13, col, ol=OUT, w=lw)                 # head
        c.poly([(hx + 8 * turn - 6, -100), (hx + 8 * turn - 3, -110), (hx + 8 * turn, -100)], col, ol=OUT, w=1.5)
        c.poly([(hx + 8 * turn + 1, -100), (hx + 8 * turn + 5, -110), (hx + 8 * turn + 7, -99)], col, ol=OUT, w=1.5)
        c.line([(hx + 8 * turn - 4, -101), (hx - 6, -66)], dark, 2.5, cap=False)    # mane
    c.pop()


def brandenburg_gate(c, x, base, s=1.0, col=SAND, shade=SAND_S, dark=SAND_D, lw=2.5, quad=True, night=0.0):
    """The Brandenburg Gate seen from the front: about 640 wide and 540 tall at s=1."""
    c.push(x, base, s)
    ol = OUT
    # side wings (lower guard houses)
    for side in (-1, 1):
        c.rect(side * 300, -170, side * 360, 0, shade, ol=ol, w=lw)
        c.rect(side * 296, -186, side * 364, -170, col, ol=ol, w=lw)
        c.rect(side * 314, -140, side * 346, -40, dark, ol=ol, w=lw * 0.8)
    # passage shadows (ceiling)
    c.rect(-300, -236, 300, -214, mix(dark, (60, 50, 50), 0.4), ol=None)
    # steps
    c.rect(-320, -14, 320, 0, shade, ol=ol, w=lw)
    # columns
    xs = (-262, -158, -58, 58, 158, 262)
    for cx in xs:
        c.rect(cx - 15, -214, cx + 15, -14, col, ol=ol, w=lw)
        c.rect(cx - 15, -214, cx - 5, -14, shade, ol=None)
        for fx in (-1, 5, 10):
            c.line([(cx + fx, -208), (cx + fx, -20)], shade, 1.2, cap=False)
        c.rect(cx - 20, -224, cx + 20, -214, col, ol=ol, w=lw)               # capital
        c.rect(cx - 19, -22, cx + 19, -14, col, ol=ol, w=lw * 0.8)           # base
    # entablature
    c.rect(-306, -262, 306, -224, col, ol=ol, w=lw)
    c.rect(-306, -262, 306, -252, shade, ol=None)
    for k in range(-290, 300, 34):
        c.rect(k, -250, k + 12, -228, shade, ol=None)                         # triglyphs
        c.line([(k + 4, -250), (k + 4, -228)], dark, 1, cap=False)
        c.line([(k + 8, -250), (k + 8, -228)], dark, 1, cap=False)
    c.rect(-316, -272, 316, -262, col, ol=ol, w=lw)                           # cornice
    # attic: stepped block with a relief panel
    c.rect(-270, -300, 270, -272, col, ol=ol, w=lw)
    c.rect(-190, -350, 190, -300, col, ol=ol, w=lw)
    c.rect(-160, -340, 160, -308, shade, ol=dark, w=1.2)
    for k in range(9):
        fx = -140 + k * 35
        c.circle(fx, -324, 6, mix(shade, dark, 0.4), ol=None)
        c.line([(fx - 8, -312), (fx + 8, -312)], mix(shade, dark, 0.4), 3, cap=False)
    c.rect(-200, -358, 200, -350, col, ol=ol, w=lw)
    if night > 0:
        for cx in xs:
            c.rect(cx - 15, -214, cx + 15, -14, mix(col, (255, 220, 140), 0.25 * night), ol=None)
    if quad:
        quadriga(c, 0, -358, 1.0, lw=lw * 0.8)
    c.pop()


def german_flag(c, x, y, s=1.0, t=0.0, pole=120):
    c.push(x, y, s)
    c.line([(0, 0), (0, -pole)], (220, 220, 220), 3)
    w, h = 54, 34
    for k, col in enumerate(((30, 30, 34), (214, 40, 40), (250, 204, 40))):
        pts = []
        for u in np.linspace(0, 1, 6):
            pts.append((2 + u * w, -pole + k * h / 3 + 3 * math.sin(t * 4 + u * 4) * u))
        for u in np.linspace(1, 0, 6):
            pts.append((2 + u * w, -pole + (k + 1) * h / 3 + 3 * math.sin(t * 4 + u * 4) * u))
        c.poly(pts, col, ol=None)
    c.pop()


def berlin_flag(c, x, y, s=1.0, t=0.0, pole=150, w=90, h=58):
    """White flag with red stripes and the black Berlin bear."""
    c.push(x, y, s)
    c.line([(0, 0), (0, -pole)], (230, 230, 230), 4)
    c.circle(0, -pole - 4, 5, (250, 210, 70), w=1.5)

    def P(u, v):
        return (2 + u * w, -pole + v * h + 5 * math.sin(t * 4 + u * 4) * u)

    def quad(u0, v0, u1, v1, col):
        c.poly([P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)], col, ol=None)
    quad(0, 0, 1, 1, (250, 250, 250))
    quad(0, 0, 1, 0.2, (220, 40, 46))
    quad(0, 0.8, 1, 1, (220, 40, 46))
    bx, by = P(0.42, 0.5)
    bear_silhouette(c, bx, by + 13, 0.3, (30, 26, 26))
    c.line([P(u, 0) for u in np.linspace(0, 1, 6)] + [P(1, 1)] + [P(u, 1) for u in np.linspace(1, 0, 6)],
           OUT, 1.5, cap=False)
    c.pop()


def bear_silhouette(c, x, y, s=1.0, col=(30, 26, 26)):
    """The heraldic Berlin bear walking upright (feet at x, y), ~120 tall at s=1."""
    c.push(x, y, s)
    c.line([(-12, -34), (-20, -4)], col, 16)
    c.line([(12, -34), (20, -4)], col, 16)
    c.ellipse(-24, -2, 12, 6, col, ol=None)
    c.ellipse(24, -2, 12, 6, col, ol=None)
    c.ellipse(0, -56, 30, 36, col, ol=None)
    c.ellipse(-30, -60, 8, 10, col, ol=None)                       # stubby tail
    c.line([(18, -76), (44, -84)], col, 13)                        # raised paws
    c.line([(18, -62), (44, -60)], col, 13)
    for px, py in ((48, -86), (48, -60)):
        for k in range(3):
            c.line([(px, py - 4 + k * 4), (px + 7, py - 6 + k * 4)], (220, 40, 46), 2, cap=False)
    c.circle(12, -100, 20, col, ol=None)                           # head
    c.circle(0, -116, 8, col, ol=None)                             # ear
    c.ellipse(32, -96, 13, 9, col, ol=None)                        # snout
    c.ellipse(36, -88, 6, 3, (220, 40, 46), ol=None)               # tongue
    c.pop()


def bear_badge(c, x, y, r, t=0.0):
    """A round sign with a smiling cartoon bear face (Berti-like)."""
    p = BERTI
    c.circle(x, y, r, (250, 214, 80), w=3)
    c.circle(x, y, r * 0.86, (255, 244, 220), w=2)
    s = r / 60
    for ex in (-26, 26):
        c.circle(x + ex * s, y - 24 * s, 12 * s, p["fur"], w=2)
        c.circle(x + ex * s, y - 24 * s, 6 * s, p["ear"], ol=None)
    c.circle(x, y + 2 * s, 30 * s, p["fur"], w=2.5)
    c.ellipse(x, y + 12 * s, 14 * s, 10 * s, p["belly"], ol=None)
    c.ellipse(x, y + 7 * s, 5 * s, 3.5 * s, (40, 28, 26), ol=None)
    c.arc(x, y + 14 * s, 6 * s, 4 * s, 20, 160, OUT, 2)
    for ex in (-11, 11):
        c.circle(x + ex * s, y - 6 * s, 3.2 * s, (40, 28, 26), ol=None)


def reichstag(c, x, base, s=1.0, col=STONE, shade=STONE_S, lw=2.0, glow=0.0, flags=True, t=0.0):
    """The Reichstag with its glass dome, about 700 wide and 320 tall at s=1."""
    c.push(x, base, s)
    ol = OUT
    c.rect(-340, -200, 340, 0, col, ol=ol, w=lw)
    c.rect(-340, -28, 340, 0, shade, ol=ol, w=lw)
    # windows
    for row, yy in enumerate((-160, -110, -64)):
        for k in range(-300, 310, 34):
            if -140 < k < 140:
                continue
            wc = (80, 96, 120) if not glow else mix((80, 96, 120), (255, 214, 130), glow)
            c.rect(k - 8, yy - 14, k + 8, yy + 14, wc, ol=None)
    # corner towers
    for side in (-1, 1):
        x0 = side * 340
        x1 = side * 270
        c.rect(min(x0, x1), -250, max(x0, x1), 0, col, ol=ol, w=lw)
        c.rect(min(x0, x1) - 4, -262, max(x0, x1) + 4, -250, shade, ol=ol, w=lw)
        for yy in (-220, -170, -120, -70):
            c.rect(side * 305 - 10, yy - 14, side * 305 + 10, yy + 14, (80, 96, 120) if not glow else
                   mix((80, 96, 120), (255, 214, 130), glow), ol=None)
        if flags:
            german_flag(c, side * 305, -262, 0.7, t + side, pole=70)
    # dome (glass, with ribs)
    gc = GLASS if not glow else mix(GLASS, (255, 236, 170), glow)
    c.rect(-110, -262, 110, -232, shade, ol=ol, w=lw)
    c.ellipse(0, -262, 92, 92, gc, ol=ol, w=lw)
    c.rect(-96, -262, 96, -150, col, ol=None)
    c.rect(-110, -262, 110, -232, shade, ol=ol, w=lw)
    for k in range(1, 4):
        c.arc(0, -262, 92, 92 * k / 4, 180, 360, mix(gc, (90, 120, 140), 0.5), 1.4)
    for k in range(-3, 4):
        c.line([(k * 26, -262), (k * 10, -352)], mix(gc, (90, 120, 140), 0.5), 1.4, cap=False)
    c.arc(0, -262, 92, 92, 180, 360, ol, lw)
    c.rect(-110, -262, 110, -232, shade, ol=ol, w=lw)
    # portico with columns and a pediment
    c.rect(-140, -214, 140, -28, col, ol=ol, w=lw)
    for k in range(6):
        cx = -110 + k * 44
        c.rect(cx - 9, -186, cx + 9, -28, mix(col, (255, 255, 255), 0.25), ol=ol, w=lw * 0.7)
    c.rect(-148, -214, 148, -186, col, ol=ol, w=lw)
    _text(c, 0, -200, "DEM DEUTSCHEN VOLKE", 12, (120, 100, 70))
    c.poly([(-152, -214), (0, -258), (152, -214)], col, ol=ol, w=lw)
    for k in range(5):
        c.rect(-100 + k * 44, -24, -60 + k * 44, -20, shade, ol=None)
    c.pop()


def tv_tower(c, x, base, h, lit=0.0, col=CONCRETE, shade=CONCRETE_S, ol=OUT, lw=2.5, t=0.0, beacon=True):
    """The Fernsehturm: thin concrete shaft, a silver ball, a red-and-white antenna. h = total height."""
    c.push(x, base, h / 1000.0)
    w = lw * 1000.0 / h
    sph_y, sph_r = -640, 78
    # base pavilion
    c.poly([(-90, 0), (-60, -50), (60, -50), (90, 0)], mix(col, shade, 0.4), ol=ol, w=w)
    # shaft
    c.poly([(-34, -40), (-17, sph_y + 40), (17, sph_y + 40), (34, -40)], col, ol=ol, w=w)
    c.poly([(8, -40), (6, sph_y + 40), (17, sph_y + 40), (34, -40)], shade, ol=None)
    c.line([(-34, -40), (-17, sph_y + 40)], ol, w, cap=False)
    # ball
    c.circle(0, sph_y, sph_r, SILVER, ol=ol, w=w)
    c.ellipse(26, sph_y + 8, 44, 66, SILVER_D, ol=None)
    c.circle(-4, sph_y - 4, 64, SILVER, ol=None)
    for k in (-3, -2, -1, 1, 2, 3):                            # facets
        a0, a1 = (90, 270) if k < 0 else (270, 450)
        c.arc(0, sph_y, abs(k) * 22, sph_r, a0, a1, mix(SILVER, SILVER_D, 0.7), w * 0.5)
    c.line([(0, sph_y - sph_r), (0, sph_y + sph_r)], mix(SILVER, SILVER_D, 0.7), w * 0.5, cap=False)
    for yy in (-50, -24, 24, 50):
        hw = math.sqrt(max(0, sph_r ** 2 - yy ** 2))
        c.line([(-hw, sph_y + yy), (hw, sph_y + yy)], mix(SILVER, SILVER_D, 0.7), w * 0.5, cap=False)
    # window band
    wcol = mix((70, 80, 100), (255, 220, 140), lit)
    c.rect(-76, sph_y - 6, 76, sph_y + 10, wcol, ol=ol, w=w * 0.7)
    if lit > 0:
        for k in range(-70, 72, 10):
            c.rect(k, sph_y - 3, k + 5, sph_y + 7, mix(wcol, (255, 250, 220), 0.6), ol=None)
    c.circle(-30, sph_y - 40, 14, mix(SILVER, (255, 255, 255), 0.7), ol=None)
    # upper shaft and antenna
    c.rect(-12, sph_y - 130, 12, sph_y - sph_r + 4, col, ol=ol, w=w)
    c.rect(-8, -1000 + 80, 8, sph_y - 130, (240, 240, 240), ol=ol, w=w)
    for k in range(5):
        y0 = sph_y - 130 - k * 40
        c.rect(-8, y0 - 20, 8, y0, (220, 50, 50), ol=None)
    c.rect(-4, -1000, 4, -920, (220, 50, 50), ol=ol, w=w * 0.7)
    if beacon and (math.sin(t * 3) > 0.2 or lit == 0):
        c.circle(0, -1002, 7, (255, 80, 70), ol=None)
    c.pop()


def berliner_dom(c, x, base, s=1.0, col=(150, 160, 150), dome=(96, 140, 120), lw=2.0, ol=OUT):
    """Berlin Cathedral silhouette: a big green dome and corner towers."""
    c.push(x, base, s)
    c.rect(-150, -150, 150, 0, col, ol=ol, w=lw)
    c.rect(-60, -200, 60, -150, col, ol=ol, w=lw)
    c.ellipse(0, -200, 60, 90, dome, ol=ol, w=lw)
    c.rect(-62, -200, 62, -150, col, ol=None)
    c.line([(-62, -200), (62, -200)], ol, lw, cap=False)
    c.rect(-8, -310, 8, -286, dome, ol=ol, w=lw)
    c.circle(0, -318, 6, (240, 200, 70), ol=ol, w=lw * 0.6)
    for side in (-1, 1):
        c.rect(side * 150 - 26, -200, side * 150 + 26, 0, col, ol=ol, w=lw)
        c.ellipse(side * 150, -200, 26, 34, dome, ol=ol, w=lw)
        c.rect(side * 150 - 27, -200, side * 150 + 27, -180, col, ol=None)
        c.line([(side * 150 - 26, -200), (side * 150 + 26, -200)], ol, lw, cap=False)
    for k in range(-120, 130, 30):
        c.rect(k - 6, -120, k + 6, -60, mix(col, (40, 50, 50), 0.4), ol=None, r=5)
    c.pop()


def oberbaum(c, x, base, s=1.0, deck_y=-170, lw=2.5):
    """The Oberbaum Bridge: red brick arches over the river, an arcade for the U-Bahn on top,
    and two towers in the middle. base = water line. About 1100 wide at s=1."""
    c.push(x, base, s)
    ol = OUT
    L = 560
    c.rect(-L, deck_y + 50, L, 30, BRICK, ol=ol, w=lw)
    # river arches
    for k in range(-3, 4):
        ax = k * 150
        c.ellipse(ax, 30, 62, 110, (50, 70, 100), ol=ol, w=lw)
    c.rect(-L - 4, 26, L + 4, 60, RIVER, ol=None)
    # road deck
    c.rect(-L, deck_y + 50, L, deck_y + 70, BRICK_D, ol=ol, w=lw)
    # the arcade (viaduct for the trains)
    c.rect(-L, deck_y - 10, L, deck_y + 50, BRICK, ol=ol, w=lw)
    for k in range(-L + 20, L - 10, 40):
        c.rect(k, deck_y + 4, k + 24, deck_y + 50, (90, 50, 50), ol=None)
        c.ellipse(k + 12, deck_y + 6, 12, 10, (90, 50, 50), ol=None)
    c.rect(-L, deck_y - 18, L, deck_y - 6, BRICK_D, ol=ol, w=lw)
    # towers
    for tx in (-70, 70):
        c.rect(tx - 36, deck_y - 170, tx + 36, deck_y + 50, BRICK, ol=ol, w=lw)
        c.rect(tx - 40, deck_y - 186, tx + 40, deck_y - 170, BRICK_D, ol=ol, w=lw)
        for k in range(5):
            c.rect(tx - 40 + k * 18, deck_y - 198, tx - 30 + k * 18, deck_y - 186, BRICK_D, ol=ol, w=lw * 0.7)
        c.poly([(tx - 20, deck_y - 198), (tx, deck_y - 260), (tx + 20, deck_y - 198)], (90, 110, 120), ol=ol, w=lw)
        for yy in (deck_y - 140, deck_y - 90, deck_y - 40):
            c.rect(tx - 9, yy - 18, tx + 9, yy + 14, (60, 50, 60), ol=None)
            c.ellipse(tx, yy - 18, 9, 8, (60, 50, 60), ol=None)
    c.pop()


# ====================================================================== vehicles

def ubahn_car(c, x, y, s=1.0, doors=0.0, length=440, inside=None, front=None, win_col=(150, 196, 220),
              night=0.0):
    """One yellow U-Bahn car (bottom of the wheels at y, centred at x). doors: 0 shut .. 1 open.

    front: None, 'left' or 'right' -- which end has the driver's cab (rounded).
    inside(c, door_x): draw something in each open doorway (door_x = local door centre).
    """
    c.push(x, y, s)
    L = length / 2
    top, bot = -150, -26
    c.rect(-L, top, L, bot, UYELLOW, w=3, r=10 if front is None else 4)
    if front:
        fx = L if front == "right" else -L
        sgn = 1 if front == "right" else -1
        c.poly([(fx - 2 * sgn, top), (fx + 22 * sgn, top + 30), (fx + 26 * sgn, bot), (fx - 2 * sgn, bot)],
               UYELLOW, w=3)
        c.poly([(fx + 2 * sgn, top + 10), (fx + 18 * sgn, top + 34), (fx + 20 * sgn, top + 70), (fx + 2 * sgn, top + 70)],
               win_col, w=2)
        c.circle(fx + 16 * sgn, bot - 16, 5, (255, 250, 210), w=1.5)
    c.rect(-L, bot - 18, L, bot, UYELLOW_D, w=2)
    c.rect(-L, top, L, top + 10, (240, 240, 236), w=2)
    door_xs = (-L * 0.5, L * 0.5)
    # windows between the doors
    for wx0, wx1 in ((-L + 18, door_xs[0] - 44), (door_xs[0] + 44, door_xs[1] - 44), (door_xs[1] + 44, L - 18)):
        if wx1 - wx0 > 20:
            c.rect(wx0, top + 22, wx1, top + 72, mix(win_col, (40, 50, 70), night), w=2.5, r=6)
            c.line([(wx0 + 10, top + 64), (wx0 + 30, top + 30)], (240, 250, 255), 2, cap=False)
    for dx in door_xs:
        c.rect(dx - 34, top + 14, dx + 34, bot - 4, (50, 50, 60), w=2.5)
        if inside is not None and doors > 0.05:
            inside(c, dx)
        o = 30 * clamp(doors)
        for side in (-1, 1):
            a = dx + side * (17 + o) - 17
            c.rect(a, top + 14, a + 34, bot - 4, UYELLOW, w=2.5)
            c.rect(a + 6, top + 22, a + 28, top + 70, mix(win_col, (40, 50, 70), night), w=2, r=4)
    # U sign
    c.rect(-14, top + 80, 14, top + 108, UBLUE, w=2, r=3)
    _text(c, 0, top + 94, "U", 18, (255, 255, 255))
    # bogies
    for bx in (-L * 0.72, L * 0.72):
        c.rect(bx - 46, -26, bx + 46, -10, (60, 60, 66), w=2)
        for wx in (-26, 26):
            c.circle(bx + wx, -10, 10, (70, 70, 76), w=2)
    c.pop()


def ubahn_train(c, x, y, s=1.0, cars=3, doors=0.0, inside=None, night=0.0, face=1):
    """A short train of cars; x is the centre of the first (leading) car. Leads to the right if face=1."""
    for k in range(cars):
        cx = x - face * k * 452 * s
        front = None
        if k == 0:
            front = "right" if face > 0 else "left"
        elif k == cars - 1:
            front = "left" if face > 0 else "right"
        ubahn_car(c, cx, y, s, doors=doors, inside=inside, front=front, night=night)


def moving_van(c, x, y, s=1.0, door=0.0, wheel=0.0, inside=None, lights=0.0):
    """A friendly moving van facing right (wheel bottoms at y). door: side roller door 0 shut .. 1 open.

    inside(c): draws what is seen through the open side door.
    """
    c.push(x, y, s)
    box = (250, 248, 240)
    red = (206, 58, 52)
    c.ellipse(0, 4, 300, 12, (70, 70, 80), ol=None)
    # cab
    c.poly([(150, -60), (150, -230), (230, -230), (290, -150), (300, -60)], red, w=3)
    c.poly([(166, -218), (226, -218), (272, -152), (166, -152)], (190, 226, 250), w=2.5)
    c.line([(186, -210), (204, -168)], (255, 255, 255), 3)
    c.rect(282, -118, 302, -100, mix((255, 236, 150), (255, 255, 230), lights), w=2)
    c.rect(150, -84, 304, -60, mix(red, (0, 0, 0), 0.25), w=2.5)
    # box
    c.rect(-290, -300, 156, -60, box, w=3, r=6)
    c.rect(-290, -84, 156, -60, (200, 200, 206), w=2.5)
    # side door opening
    ox0, ox1, oy0, oy1 = -250, -60, -270, -90
    c.rect(ox0, oy0, ox1, oy1, (50, 44, 52), w=2.5)
    if inside is not None:
        inside(c)
    d = clamp(door)
    if d < 0.98:
        y_bottom = lerp(oy1, oy0 + 6, d)
        c.rect(ox0, oy0, ox1, y_bottom, (236, 232, 222), w=2.5)
        yy = oy0 + 12
        while yy < y_bottom - 4:
            c.line([(ox0 + 4, yy), (ox1 - 4, yy)], (196, 192, 186), 2, cap=False)
            yy += 14
        if d < 0.05:
            c.rect(-170, -106, -140, -98, (110, 110, 120), w=1.5, r=2)
    else:
        c.rect(ox0, oy0, ox1, oy0 + 10, (236, 232, 222), w=2)
    # side painting: smiling bear badge + BERLIN
    bear_badge(c, 4, -170, 62)
    _text(c, 4, -264, "BERLIN", 30, red, stroke=2, stroke_fill=OUT)
    _text(c, 112, -170, "Umzüge", 16, (60, 60, 70))
    for k in range(-280, 150, 30):
        c.line([(k, -290), (k + 14, -290)], (220, 40, 46), 4, cap=False)
    # wheels
    for wx in (-200, 210):
        c.circle(wx, -32, 34, (44, 44, 52), w=3)
        c.circle(wx, -32, 15, (190, 190, 200), w=2)
        for k in range(3):
            a = wheel + k * math.tau / 3
            c.line([(wx, -32), (wx + 12 * math.cos(a), -32 + 12 * math.sin(a))], (110, 110, 120), 3, cap=False)
    c.pop()


def river_boat(c, x, y, s=1.0, face=1, t=0.0, night=0.0):
    """A white sightseeing boat on the Spree (waterline at y)."""
    c.push(x, y + 2 * math.sin(t * 2), s, flip=face < 0)
    c.poly([(-170, -40), (170, -40), (150, 0), (-160, 0)], (250, 250, 250), w=2.5)
    c.rect(-170, -18, 170, -10, (40, 80, 160), ol=None)
    c.rect(-130, -86, 110, -40, (236, 240, 246), w=2.5, r=6)
    for k in range(8):
        wx = -120 + k * 28
        c.rect(wx, -78, wx + 20, -54, mix((120, 170, 210), (255, 220, 140), night), w=1.5, r=3)
    c.rect(-136, -94, 116, -86, (40, 80, 160), w=2)
    c.line([(-150, -40), (-150, -110)], (200, 200, 200), 2)
    c.poly([(-150, -110), (-120, -104), (-150, -96)], (214, 44, 50), ol=None)
    c.pop()


# ====================================================================== street

def ampelmann(c, x, y, s=1.0, green=False):
    """A Berlin pedestrian light with the little hat man."""
    c.push(x, y, s)
    c.line([(0, 0), (0, -150)], (70, 70, 80), 5, cap=False)
    c.rect(-18, -230, 18, -150, (40, 40, 46), w=2.5, r=5)
    for k, on in ((0, not green), (1, green)):
        cy = -210 + k * 40
        col = ((230, 50, 40) if k == 0 else (60, 200, 90)) if on else (70, 70, 74)
        c.circle(0, cy, 14, col, w=1.5)
        if on:
            m = (40, 20, 20) if k == 0 else (20, 70, 30)
            c.ellipse(0, cy - 9, 7, 2, m, ol=None)
            c.rect(-3, cy - 13, 3, cy - 9, m, ol=None)
            c.circle(0, cy - 6, 2.5, m, ol=None)
            if k == 0:
                c.rect(-3, cy - 4, 3, cy + 9, m, ol=None)
                c.line([(-8, cy - 3), (-8, cy + 6)], m, 2, cap=False)
                c.line([(8, cy - 3), (8, cy + 6)], m, 2, cap=False)
            else:
                c.rect(-2.5, cy - 4, 2.5, cy + 4, m, ol=None)
                c.line([(0, cy + 4), (-6, cy + 10)], m, 2, cap=False)
                c.line([(0, cy + 4), (6, cy + 10)], m, 2, cap=False)
                c.line([(0, cy - 2), (-7, cy + 2)], m, 2, cap=False)
                c.line([(0, cy - 2), (7, cy - 4)], m, 2, cap=False)
    c.pop()


def linden(c, x, y, s=1.0, leaf=(96, 150, 80), leaf_l=(130, 180, 100), trunk=(110, 86, 64), ol=OUT):
    c.push(x, y, s)
    c.rect(-10, -150, 10, 0, trunk, ol=ol, w=2)
    blobs = ((-46, -160, 46), (40, -168, 48), (0, -214, 56), (-10, -150, 44), (30, -120, 34))
    for dx, dy, r in blobs:
        c.circle(dx, dy, r, leaf, ol=ol, w=2)
    for dx, dy, r in blobs:
        c.circle(dx, dy, r - 3, leaf, ol=None)
    for dx, dy, r in ((-30, -180, 18), (24, -196, 20), (-6, -232, 18)):
        c.circle(dx, dy, r, leaf_l, ol=None)
    c.pop()


def gas_lamp(c, x, y, s=1.0, lit=0.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, -170)], (50, 70, 70), 5, cap=False)
    c.rect(-8, -12, 8, 0, (50, 70, 70), ol=None)
    c.poly([(-16, -200), (16, -200), (11, -172), (-11, -172)], mix((240, 240, 220), (255, 230, 150), lit), w=2)
    c.poly([(-20, -200), (0, -214), (20, -200)], (50, 70, 70), w=2)
    c.pop()


def altbau(c, x0, w, base, h, wall, rng, roof=(150, 90, 70), win=(110, 140, 170), lit=None, balcony=True,
           ol=OUT, lw=2.0):
    """A Berlin 'Altbau' apartment house: tall windows, a cornice, little balconies."""
    c.rect(x0, base - h, x0 + w, base + 2, wall, ol=ol, w=lw)
    c.rect(x0 - 4, base - h - 10, x0 + w + 4, base - h, mix(wall, (0, 0, 0), 0.15), ol=ol, w=lw)
    floors = max(2, int(h / 62))
    cols = max(2, int(w / 46))
    for f in range(floors):
        yy = base - h + 22 + f * (h - 30) / floors
        for k in range(cols):
            xx = x0 + (k + 0.5) * w / cols
            col = win
            if lit is not None and rng.random() < lit:
                col = (255, 214, 130)
            c.rect(xx - 10, yy, xx + 10, yy + 30, col, ol=ol, w=lw * 0.6)
            c.rect(xx - 13, yy - 4, xx + 13, yy, mix(wall, (255, 255, 255), 0.4), ol=None)
        if balcony and f > 0 and rng.random() < 0.5:
            k = rng.integers(cols)
            xx = x0 + (k + 0.5) * w / cols
            c.rect(xx - 18, yy + 30, xx + 18, yy + 36, mix(wall, (0, 0, 0), 0.25), ol=ol, w=lw * 0.6)
            for bx in range(-16, 18, 6):
                c.line([(xx + bx, yy + 30), (xx + bx, yy + 18)], (60, 60, 70), 1.2, cap=False)
            if rng.random() < 0.7:
                for fx in (-10, 0, 10):
                    c.circle(xx + fx, yy + 16, 5, ((230, 70, 90), (250, 200, 60), (240, 120, 160))[rng.integers(3)],
                             ol=None)


def skyline(c, x0, x1, base, rng, hmin, hmax, cols, win=None, p=0.3, ol=None):
    x = x0
    while x < x1:
        w = rng.uniform(40, 100)
        h = rng.uniform(hmin, hmax)
        col = cols[rng.integers(len(cols))]
        c.rect(x, base - h, x + w + 1, base + 2, col, ol=ol, w=1.2)
        if win:
            for wy in np.arange(base - h + 8, base - 6, 14):
                for wx in np.arange(x + 6, x + w - 6, 12):
                    if rng.random() < p:
                        c.rect(wx, wy, wx + 5, wy + 6, win, ol=None)
        x += w


# ====================================================================== home

def cushion(c, x, y, w=70, h=34, col=(90, 150, 220), pattern=0, ang=0.0):
    """A soft square cushion lying flat (bottom centre at x, y)."""
    c.push(x, y)
    hw = w / 2
    c.poly([(-hw, -2), (-hw - 4, -h * 0.5), (-hw + 2, -h), (0, -h - 4), (hw - 2, -h), (hw + 4, -h * 0.5), (hw, -2),
            (0, 2)], col, w=2.5)
    light = mix(col, (255, 255, 255), 0.45)
    if pattern == 0:
        for k in (-1, 0, 1):
            c.line([(k * w * 0.28, -h + 6), (k * w * 0.28, -6)], light, 3, cap=False)
    elif pattern == 1:
        for px, py in ((-hw * 0.5, -h * 0.35), (hw * 0.4, -h * 0.65), (hw * 0.45, -h * 0.25), (-hw * 0.4, -h * 0.75)):
            c.circle(px, py, 4, light, ol=None)
    else:
        c.poly([(0, -h + 8), (8, -h * 0.5), (0, -8), (-8, -h * 0.5)], light, ol=None)
    c.circle(0, -h * 0.5, 3, mix(col, (0, 0, 0), 0.3), ol=None)
    c.pop()


def box(c, x, y, w, h, label=None, tape=True, col=(206, 162, 108)):
    """A cardboard moving box (bottom centre at x, y)."""
    c.rect(x - w / 2, y - h, x + w / 2, y, col, w=2.5)
    c.rect(x - w / 2, y - h, x + w / 2, y - h + 8, mix(col, (0, 0, 0), 0.12), ol=None)
    if tape:
        c.rect(x - 6, y - h, x + 6, y - h + 18, (230, 214, 170), ol=None)
    if label:
        _text(c, x, y - h * 0.5, label, 13, (90, 60, 40))


def armchair(c, x, y, s=1.0, col=(120, 80, 140)):
    c.push(x, y, s)
    dark = mix(col, (0, 0, 0), 0.25)
    c.rect(-90, -170, 90, -60, dark, w=3, r=26)
    c.rect(-80, -80, 80, -30, col, w=3, r=14)
    c.rect(-104, -120, -66, -20, col, w=3, r=16)
    c.rect(66, -120, 104, -20, col, w=3, r=16)
    for lx in (-84, 84):
        c.rect(lx - 6, -20, lx + 6, 0, (90, 60, 40), w=2)
    c.pop()


def paint_pot(c, x, y, col, s=1.0):
    c.push(x, y, s)
    c.rect(-14, -26, 14, 0, (200, 204, 210), w=2, r=3)
    c.ellipse(0, -26, 14, 5, col, w=2)
    c.poly([(-14, -24), (-10, -14), (-6, -24)], col, ol=None)
    c.pop()


# ====================================================================== East Side Gallery

SEG = 112                    # width of one wall segment (px)
WALL_H = 250                 # wall height


def mural(c, kind, x0, x1, top, base, t=0.0, seed=0):
    """Paint one mural over the wall between x0 and x1 (already-clipped flat area)."""
    rng = np.random.default_rng(seed)
    w = x1 - x0
    mid = (x0 + x1) / 2
    hgt = base - top
    if kind == "rainbow":
        c.rect(x0, top, x1, base, (120, 196, 240), ol=None)
        cols = [(230, 60, 60), (250, 150, 50), (250, 220, 60), (90, 190, 90), (70, 130, 220), (150, 90, 200)]
        for k, col in enumerate(cols):
            r = w * 0.48 - k * 14
            c.ellipse(mid, base - 10, r, r * 0.9, col, ol=None)
        c.ellipse(mid, base - 10, w * 0.48 - 84, (w * 0.48 - 84) * 0.9, (120, 196, 240), ol=None)
        for cx in (x0 + w * 0.12, x1 - w * 0.12):
            D.cloud(c, cx, base - 30, 0.8)
    elif kind == "sun":
        c.rect(x0, top, x1, base, (255, 170, 60), ol=None)
        for k in range(16):
            a = k * math.tau / 16
            c.poly([(mid, top + hgt * 0.5), (mid + math.cos(a) * w, top + hgt * 0.5 + math.sin(a) * w),
                    (mid + math.cos(a + 0.18) * w, top + hgt * 0.5 + math.sin(a + 0.18) * w)],
                   (255, 200, 80), ol=None)
        r = hgt * 0.3
        c.circle(mid, top + hgt * 0.5, r, (255, 230, 70), w=3)
        c.circle(mid - r * 0.35, top + hgt * 0.45, r * 0.1, OUT, ol=None)
        c.circle(mid + r * 0.35, top + hgt * 0.45, r * 0.1, OUT, ol=None)
        c.arc(mid, top + hgt * 0.53, r * 0.5, r * 0.4, 20, 160, OUT, 4)
        c.circle(mid - r * 0.6, top + hgt * 0.6, r * 0.13, (255, 150, 120), ol=None)
        c.circle(mid + r * 0.6, top + hgt * 0.6, r * 0.13, (255, 150, 120), ol=None)
    elif kind == "hearts":
        c.rect(x0, top, x1, base, (250, 190, 210), ol=None)
        for _ in range(int(w / 26)):
            hx, hy = rng.uniform(x0 + 20, x1 - 20), rng.uniform(top + 30, base - 20)
            r = rng.uniform(10, 26)
            col = [(230, 50, 90), (250, 100, 140), (200, 40, 120), (255, 255, 255)][rng.integers(4)]
            heart(c, hx, hy, r, col)
    elif kind == "flowers":
        c.rect(x0, top, x1, base, (150, 210, 250), ol=None)
        c.rect(x0, base - hgt * 0.35, x1, base, (110, 190, 90), ol=None)
        for _ in range(int(w / 22)):
            fx = rng.uniform(x0 + 12, x1 - 12)
            fy = rng.uniform(base - hgt * 0.3, base - 8)
            col = [(240, 80, 90), (250, 210, 60), (240, 140, 200), (255, 255, 255), (170, 110, 220)][rng.integers(5)]
            c.line([(fx, fy), (fx, fy - 30)], (60, 130, 60), 3, cap=False)
            for k in range(5):
                a = k * math.tau / 5
                c.circle(fx + math.cos(a) * 8, fy - 34 + math.sin(a) * 8, 6, col, ol=None)
            c.circle(fx, fy - 34, 5, (255, 200, 60), ol=None)
    elif kind == "doves":
        c.rect(x0, top, x1, base, (60, 90, 170), ol=None)
        for _ in range(int(w / 70) + 2):
            dx, dy = rng.uniform(x0 + 30, x1 - 30), rng.uniform(top + 40, base - 40)
            dove(c, dx, dy, rng.uniform(0.7, 1.2), flap=rng.uniform(0, 1))
        for _ in range(12):
            sx, sy = rng.uniform(x0, x1), rng.uniform(top, base)
            c.circle(sx, sy, 2, (255, 250, 200), ol=None)
    elif kind == "faces":
        cols = [(250, 90, 80), (80, 180, 230), (250, 210, 60), (130, 200, 90), (220, 120, 220)]
        c.rect(x0, top, x1, base, (40, 40, 60), ol=None)
        n = max(2, int(w / 90))
        for k in range(n):
            fx = x0 + (k + 0.5) * w / n
            fy = top + hgt * (0.45 + 0.12 * math.sin(k * 2.1))
            col = cols[k % len(cols)]
            r = min(w / n * 0.42, hgt * 0.32)
            c.circle(fx, fy, r, col, w=3)
            c.circle(fx - r * 0.35, fy - r * 0.15, r * 0.14, (255, 255, 255), w=2)
            c.circle(fx + r * 0.35, fy - r * 0.15, r * 0.14, (255, 255, 255), w=2)
            c.circle(fx - r * 0.33, fy - r * 0.13, r * 0.07, OUT, ol=None)
            c.circle(fx + r * 0.37, fy - r * 0.13, r * 0.07, OUT, ol=None)
            c.arc(fx, fy + r * 0.15, r * 0.5, r * 0.45, 20, 160, OUT, 4)
    elif kind == "car":
        c.rect(x0, top, x1, base, (240, 236, 220), ol=None)
        cx, cy = mid, top + hgt * 0.6
        # cracks around a little car bursting through the wall
        for k in range(9):
            a = k * math.tau / 9 + 0.3
            pts = [(cx, cy)]
            r = 0
            for j in range(4):
                r += rng.uniform(20, 40)
                pts.append((cx + math.cos(a + rng.uniform(-0.2, 0.2)) * r * 1.4,
                            cy + math.sin(a + rng.uniform(-0.2, 0.2)) * r))
            c.line(pts, (120, 116, 110), 2.5, cap=False)
        c.ellipse(cx, cy, 70, 46, (190, 186, 176), ol=None)
        c.rect(cx - 60, cy - 30, cx + 60, cy + 22, (90, 180, 200), w=3, r=18)
        c.rect(cx - 40, cy - 52, cx + 40, cy - 26, (90, 180, 200), w=3, r=12)
        c.rect(cx - 32, cy - 46, cx + 32, cy - 30, (220, 240, 250), w=2, r=6)
        for hx in (-40, 40):
            c.circle(cx + hx, cy - 6, 10, (255, 250, 200), w=2)
        c.rect(cx - 20, cy + 4, cx + 20, cy + 16, (60, 60, 70), w=1.5, r=3)
        c.circle(cx - 40, cy + 24, 12, (50, 50, 56), w=2)
        c.circle(cx + 40, cy + 24, 12, (50, 50, 56), w=2)
    elif kind == "hands":
        c.rect(x0, top, x1, base, (255, 220, 120), ol=None)
        for side in (-1, 1):
            hx = mid + side * 40
            arm0 = mid + side * (w / 2 + 10)
            col = (250, 170, 120) if side < 0 else (170, 110, 80)
            c.stroke([(arm0, top + hgt * 0.62), (hx + side * 20, top + hgt * 0.52)], col, 34)
            c.circle(hx, top + hgt * 0.5, 24, col, w=3)
        heart(c, mid, top + hgt * 0.24, 22, (230, 50, 90))
    elif kind == "bubbles":
        c.rect(x0, top, x1, base, (110, 70, 160), ol=None)
        for _ in range(int(w / 12)):
            bx, by = rng.uniform(x0, x1), rng.uniform(top, base)
            r = rng.uniform(6, 30)
            col = [(250, 120, 180), (120, 220, 240), (250, 230, 100), (140, 240, 140)][rng.integers(4)]
            c.circle(bx, by, r, col, ol=None)
            c.circle(bx - r * 0.3, by - r * 0.3, r * 0.25, mix(col, (255, 255, 255), 0.6), ol=None)
    elif kind == "bear":
        c.rect(x0, top, x1, base, (250, 250, 246), ol=None)
        c.rect(x0, top, x1, top + hgt * 0.16, (220, 40, 46), ol=None)
        c.rect(x0, base - hgt * 0.16, x1, base, (220, 40, 46), ol=None)
        bear_silhouette(c, mid - 20, base - hgt * 0.2, hgt / 170, (40, 34, 34))
    elif kind == "blank":
        c.rect(x0, top, x1, base, (252, 252, 248), ol=None)


def clip_draw(c, x0, y0, x1, y1, fn):
    """Run fn(canvas) clipped to the box (needs an unscaled canvas)."""
    w, h = int(math.ceil(x1 - x0)), int(math.ceil(y1 - y0))
    tmp = D.Canvas(size=(w, h))
    tmp.push(-x0, -y0)
    fn(tmp)
    px, py = c.P(x0, y0)
    c.img.paste(tmp.img, (int(round(px)), int(round(py))))


def heart(c, x, y, r, col, ol=None):
    c.circle(x - r * 0.5, y - r * 0.2, r * 0.58, col, ol=ol, w=2)
    c.circle(x + r * 0.5, y - r * 0.2, r * 0.58, col, ol=ol, w=2)
    c.poly([(x - r * 1.05, y), (x + r * 1.05, y), (x, y + r * 1.1)], col, ol=None)
    c.poly([(x - r * 1.0, y - 0.1 * r), (x + r * 1.0, y - 0.1 * r), (x, y + r * 0.4)], col, ol=None)


def dove(c, x, y, s=1.0, flap=0.0):
    c.push(x, y, s)
    k = math.sin(flap * math.tau)
    c.ellipse(0, 0, 22, 10, (255, 255, 255), w=2)
    c.circle(20, -6, 8, (255, 255, 255), w=2)
    c.poly([(27, -6), (36, -4), (27, -2)], (250, 180, 60), ol=None)
    c.poly([(-6, -4), (10, -4), (0, -30 * k - 6)], (255, 255, 255), w=2)
    c.poly([(-20, 0), (-36, -8), (-34, 6)], (255, 255, 255), w=2)
    c.circle(22, -8, 1.5, OUT, ol=None)
    c.pop()


def painted_cats(c, x0, x1, top, base, prog=1.0):
    """Whiskers' painting: a sun, its beam, two cats sitting together, a heart. prog 0..1 reveals it."""
    w = x1 - x0
    hgt = base - top
    mid = (x0 + x1) / 2

    def stage(a, b):
        return clamp((prog - a) / (b - a))
    k = stage(0.0, 0.18)
    if k > 0:
        c.circle(x0 + w * 0.22, top + hgt * 0.22, 26 * k, (255, 210, 60), w=2.5)
    k = stage(0.15, 0.32)
    if k > 0:
        c.poly([(x0 + w * 0.22, top + hgt * 0.22), (x0 + w * (0.22 + 0.7 * k), base - 10),
                (x0 + w * (0.22 + 0.25 * k), base - 10)], (255, 236, 150), ol=None)
    k = stage(0.3, 0.6)
    if k > 0:
        pal = dict(D.WHISKERS)
        c.push(0, 0)
        D.cat(c, mid - 26, base - 14, pal, 0.62 * k + 0.001, 1, "sit", t=0.0, eyes="happy", tail=0.4)
        c.pop()
    k = stage(0.58, 0.86)
    if k > 0:
        D.cat(c, mid + 46, base - 14, D.LUNA, 0.62 * k + 0.001, -1, "sit", t=0.0, eyes="happy", tail=0.4)
    k = stage(0.86, 1.0)
    if k > 0:
        heart(c, mid + 12, top + hgt * 0.2, 20 * k, (230, 50, 90), ol=OUT)


def wall_run(c, x0, x1, base, plan, t=0.0, top_y=None, prog=None):
    """A run of East Side Gallery wall from x0 to x1 (ground at base).

    plan: list of (kind, n_segments, seed). The rounded concrete cap runs along the top.
    """
    top = base - WALL_H if top_y is None else top_y
    x = x0
    for kind, n, seed in plan:
        xe = min(x1, x + n * SEG)

        def paint(tc, kind=kind, x=x, xe=xe, seed=seed):
            if kind == "cats":
                mural(tc, "blank", x, xe, top, base, t, seed)
                painted_cats(tc, x, xe, top, base, 1.0 if prog is None else prog)
            else:
                mural(tc, kind, x, xe, top, base, t, seed)
        clip_draw(c, x, top, xe, base, paint)
        x = xe
    # segment seams and the outline
    for k in np.arange(x0, x1 + 1, SEG):
        c.line([(k, top + 4), (k, base)], (60, 56, 60), 1.6, cap=False)
    c.rect(x0, top, x1, base, None, w=2.5)
    c.rect(x0 - 2, top - 14, x1 + 2, top + 4, (226, 224, 218), w=2.5, r=9)
