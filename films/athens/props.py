"""Athens props and characters, in the same flat outlined style as draw.py.

Everything draws in local coordinates (origin on the ground, y up negative)
through Canvas.push, like the cats.
"""
import math

import numpy as np

import draw as D
from draw import OUT, mix, lerp, clamp

# ------------------------------------------------------------------ colours
MARBLE = (246, 240, 224)
MARBLE_S = (214, 204, 184)
MARBLE_D = (182, 170, 150)
ROCK = (204, 168, 124)
ROCK_S = (172, 136, 98)
ROCK_D = (140, 108, 80)
OLIVE = (122, 146, 98)
OLIVE_L = (168, 184, 140)
OLIVE_TRUNK = (118, 98, 80)
GBLUE = (34, 96, 176)          # Greek doors and shutters
GBLUE_L = (80, 150, 220)
BOUG = (214, 46, 136)          # bougainvillea
BOUG_L = (240, 100, 176)
WHITEWASH = (250, 246, 236)
OCHRE = (238, 196, 120)
TERRA = (206, 110, 58)         # vase clay
TERRA_L = (226, 140, 84)
BLACKFIG = (36, 26, 22)
HONEY = (240, 172, 40)
HONEY_L = (255, 206, 90)
YOGURT = (252, 250, 242)

SOCRATES = dict(body=(228, 222, 208), dark=(176, 166, 152), belly=(252, 250, 244),
                ear=(240, 170, 170), eye=(206, 172, 60), stripes=False, collar=None)
STREET_CATS = [
    dict(body=(62, 58, 68), dark=(40, 38, 46), belly=(246, 244, 240), ear=(230, 150, 160),
         eye=(220, 200, 60), stripes=False, collar=None),
    dict(body=(176, 140, 104), dark=(132, 100, 72), belly=(236, 220, 196), ear=(240, 170, 160),
         eye=(120, 190, 90), stripes=True, collar=None),
    dict(body=(246, 240, 232), dark=(206, 196, 186), belly=(255, 255, 255), ear=(250, 180, 190),
         eye=(90, 170, 230), stripes=False, collar=None),
    dict(body=(214, 176, 132), dark=(176, 136, 96), belly=(246, 232, 210), ear=(240, 170, 160),
         eye=(200, 160, 60), stripes=True, collar=None),
    dict(body=(110, 104, 112), dark=(80, 76, 86), belly=(200, 196, 200), ear=(230, 160, 170),
         eye=(230, 190, 70), stripes=True, collar=None),
]


# =================================================================== owls

OWL = dict(body=(150, 112, 80), dark=(112, 82, 58), belly=(236, 222, 196), disc=(226, 206, 176),
           spot=(250, 244, 230), brow=(255, 252, 244))
OWL_GRAN = dict(body=(140, 128, 116), dark=(104, 94, 86), belly=(226, 220, 210), disc=(220, 212, 200),
                spot=(250, 248, 240), brow=(255, 255, 255))


def owl(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", flap=0.0, wet=0.0, sling=False,
        gran=False, look=(0.0, 0.0), seed=3.0, hop=0.0):
    """A little owl (Athene noctua). Origin between the feet; about 80 px tall at s=1.

    flap: 0 folded wings .. 1 wings spread; sling: a leaf bandage on the right wing.
    """
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = OWL_GRAN if gran else OWL
    body, dark, belly = p["body"], p["dark"], p["belly"]
    if wet:
        body = mix(body, D.WATER_TINT, 0.35 * wet)
        dark = mix(dark, D.WATER_TINT, 0.35 * wet)
        belly = mix(belly, D.WATER_TINT, 0.25 * wet)
    c.push(x, y - hop, s, flip=face < 0)
    # wings (behind the body when spread)
    if flap > 0.05:
        for side in (-1, 1):
            up = math.sin(t * 22 + side) * 0.35 * flap
            ang = math.radians(-20 - 60 * flap) + up
            wx, wy = side * 22, -44
            tip = (wx + side * math.cos(ang) * 60 * flap, wy + math.sin(ang) * 46)
            c.poly([(wx, wy - 10), tip, (wx + side * 46 * flap, wy + 14), (wx, wy + 12)], dark, w=2.5)
            for k in range(3):
                u = 0.4 + 0.2 * k
                c.circle(lerp(wx, tip[0], u), lerp(wy, tip[1], u) + 6, 3, p["spot"], ol=None)
    # feet
    for fx in (-9, 9):
        c.ellipse(fx, -3, 7, 4, (230, 190, 90), w=2)
    # body
    c.ellipse(0, -34, 30, 34, body, w=3)
    c.ellipse(2, -28, 20, 24, belly, ol=None)
    for k in range(7):                                # streaks on the belly
        bx = -10 + (k % 4) * 7 + (3 if k > 3 else 0)
        by = -40 + (k // 4) * 12 + (k % 2) * 4
        c.line([(bx, by), (bx + 1, by + 6)], dark, 2.5)
    # folded wings
    if flap <= 0.05:
        for side in (-1, 1):
            c.ellipse(side * 24, -34, 11, 24, dark, w=2.5)
            for k in range(3):
                c.circle(side * 24 + side * 2, -46 + k * 10, 2.4, p["spot"], ol=None)
    if sling:
        c.ellipse(26, -36, 11, 9, (110, 170, 90), w=2)    # olive-leaf bandage
        c.line([(18, -36), (34, -36)], (70, 120, 60), 1.5, cap=False)
    # head
    hy = -78
    c.ellipse(0, hy, 30, 25, body, w=3)
    for k in range(9):                                # white spots on the crown
        a = math.radians(200 + k * 17)
        c.circle(math.cos(a) * 20, hy + math.sin(a) * 15 - 2, 2.2, p["spot"], ol=None)
    c.ellipse(-11, hy + 4, 13, 12, p["disc"], ol=None)
    c.ellipse(11, hy + 4, 13, 12, p["disc"], ol=None)
    # eyes
    for ex in (-11, 11):
        ey = hy + 2
        if eyes == "closed":
            c.arc(ex, ey, 7, 5, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 4, 7, 7, 200, 340, OUT, 2.5)
        else:
            big = 1.2 if eyes == "wide" else 1.0
            c.circle(ex, ey, 8.5 * big, (252, 214, 60), w=2)
            lx, ly = look
            c.circle(ex + lx * 2.5, ey + ly * 2.5, 4.4 * big, (20, 16, 18), ol=None)
            c.circle(ex + lx * 2.5 + 1.6, ey + ly * 2.5 - 1.8, 1.5, (255, 255, 255), ol=None)
    # white eyebrows (the little owl's frown that makes it look so wise)
    c.line([(-20, hy - 8), (-4, hy - 4)], p["brow"], 3.5)
    c.line([(20, hy - 8), (4, hy - 4)], p["brow"], 3.5)
    if gran:                                          # spectacles
        for ex in (-11, 11):
            c.circle(ex, hy + 2, 11, None, w=2)
        c.line([(-1, hy + 1), (1, hy + 1)], OUT, 2, cap=False)
    # beak
    m = 4 * mouth
    c.poly([(-5, hy + 8), (5, hy + 8), (0, hy + 18 - m * 0.3)], (232, 200, 120), w=1.8)
    if mouth > 0.05:
        c.poly([(-4, hy + 13), (4, hy + 13), (0, hy + 16 + m)], (190, 110, 90), w=1.5)
    if wet > 0.05:
        rng = np.random.default_rng(int(seed * 10))
        for k in range(4):
            px, py = rng.uniform(-28, 28), rng.uniform(-90, -20)
            fall = ((t * 1.3 + k * 0.37) % 1.0) * 30
            c.ellipse(px, py + fall, 2.2, 3.5, (170, 210, 255), ol=None)
    c.pop()


# ============================================================ Socrates cat

def _head_pos(pose, head_dy=0.0):
    if pose == "sit":
        return 18, -106 + head_dy
    if pose == "crouch":
        return 52, -40 - 38 + 14 + head_dy
    if pose == "sleep":
        return 46, -40
    return 52, -48 - 38 + head_dy


def beard(c, x, y, s, face, pose, head_dy=0.0, col=(252, 250, 244), t=0.0, drip=False, size=1.0):
    """A white beard tuft under a cat's chin (Socrates' own, or a yogurt one)."""
    hx, hy = _head_pos(pose, head_dy)
    c.push(x, y, s, flip=face < 0)
    wob = math.sin(t * 3) * 1.5
    pts = [(hx - 4, hy + 18), (hx + 30, hy + 16), (hx + 26 + wob, hy + 34 * size),
           (hx + 18 + wob, hy + 48 * size), (hx + 10, hy + 36 * size), (hx + 2, hy + 30 * size)]
    c.poly(pts, col, w=2)
    c.line([(hx + 14, hy + 26), (hx + 16 + wob, hy + 40 * size)], mix(col, (0, 0, 0), 0.12), 1.5, cap=False)
    if drip:
        k = (t * 0.8) % 1.0
        c.ellipse(hx + 18 + wob, hy + 50 * size + k * 30, 3, 4, col, w=1.5)
        c.ellipse(hx + 26, hy + 14, 4, 3, HONEY_L, ol=None)   # a blob of honey on the nose
    c.pop()


def street_cat(c, x, y, k, s=1.0, face=1, pose="sit", t=0.0, walk=0.0, eyes="open", mouth=0.0, look=(0, 0)):
    D.cat(c, x, y, STREET_CATS[k % len(STREET_CATS)], s, face, pose, walk=walk, t=t, eyes=eyes, mouth=mouth,
          seed=3.1 + k * 0.7, look=look)


# =================================================================== airship

def airship(c, x, y, s=1.0, t=0.0, part="all", face=1, rope=0.0, lit=0.0):
    """Silver honey airship. Origin at the envelope's centre. part: back | front | all.

    The gondola (an open deck with a rail) hangs below at about y=+100; things placed on
    the deck between drawing 'back' and 'front' sit inside it. rope: length of a dangling rope.
    """
    c.push(x, y, s, flip=face < 0)
    if part in ("back", "all"):
        # fins at the tail
        silver, silver_d = (214, 220, 230), (168, 176, 190)
        c.poly([(-190, -20), (-262, -84), (-238, -10)], (60, 120, 200), w=3)
        c.poly([(-190, 20), (-262, 84), (-238, 10)], (60, 120, 200), w=3)
        c.poly([(-200, -4), (-275, -6), (-275, 6), (-200, 4)], (50, 104, 180), w=3)
        # envelope
        c.ellipse(0, 0, 240, 74, silver, w=3.5)
        c.ellipse(10, 18, 220, 46, mix(silver, (255, 255, 255), 0.25), ol=None)
        c.ellipse(0, -40, 170, 16, (240, 244, 250), ol=None)
        for px in (-150, -80, 0, 80, 150):
            c.arc(px, 0, 26, 72, 270, 450, silver_d, 2)
        c.rect(-120, -14, 130, 22, (40, 100, 180), w=2.5, r=4)        # banner band
        c.text(5, 4, "ΜΕΛΙ  ·  HONEY", 22, (255, 220, 110))
        c.ellipse(232, 0, 14, 22, (200, 160, 70), w=2.5)              # nose cap
        # cables to the gondola
        for gx in (-50, 50):
            c.line([(gx * 1.6, 66), (gx, 96)], (90, 90, 100), 2, cap=False)
        # gondola back wall
        c.rect(-90, 88, 90, 140, (176, 110, 60), w=3, r=6)
        if rope > 0:
            pts = [(70 + 6 * math.sin(t * 2 + u * 3) * u, 140 + rope * u) for u in np.linspace(0, 1, 10)]
            c.line(pts, (180, 150, 100), 4)
            c.circle(pts[-1][0], pts[-1][1], 5, (180, 150, 100), w=1.5)
    if part in ("front", "all"):
        # honey jars on the deck edge and the front rail
        for k, jx in enumerate((-70, -40, 40, 66)):
            honey_jar(c, jx, 118, 0.55)
        c.rect(-96, 118, 96, 150, (196, 128, 70), w=3, r=5)
        for k in range(7):
            c.line([(-80 + k * 26, 122), (-80 + k * 26, 146)], (150, 92, 50), 2, cap=False)
        c.rect(-100, 112, 100, 122, (150, 92, 50), w=2.5, r=3)
        # propeller at the back of the gondola
        spin = t * 30
        c.rect(-112, 124, -96, 132, (100, 100, 110), w=2)
        for k in range(2):
            a = spin + k * math.pi
            c.ellipse(-116, 128 + math.sin(a) * 18, 4, abs(math.cos(a)) * 18 + 3, (120, 120, 130), w=1.5)
        if lit > 0:
            c.circle(90, 128, 6, mix((150, 150, 150), (255, 230, 140), lit), w=2)
    c.pop()


def honey_jar(c, x, y, s=1.0, lid=True, label=True):
    c.push(x, y, s)
    c.rect(-18, -40, 18, 0, HONEY, w=2.5, r=8)
    c.rect(-12, -34, -6, -8, HONEY_L, ol=None, r=3)
    if label:
        c.rect(-13, -26, 13, -12, (250, 244, 226), w=1.5, r=2)
        c.circle(0, -19, 3.5, (60, 110, 190), ol=None)
    if lid:
        c.rect(-20, -48, 20, -38, (60, 110, 190), w=2.5, r=3)
        c.line([(-20, -43), (20, -43)], (250, 250, 250), 1.5, cap=False)
    c.pop()


# ================================================================ landmarks

def parthenon(c, x, base, w, h, col=MARBLE, shade=MARBLE_S, dark=MARBLE_D, ol=OUT, lw=2.5, ruin=True,
              lit=0.0, detail=True):
    """Front of the Parthenon: steps, 8 fluted columns, frieze and a pediment.

    (x, base): centre of the bottom step; w: width of the top step; h: height to the roof peak.
    """
    steps_h = h * 0.08
    col_h = h * 0.58
    ent_h = h * 0.16
    ped_h = h * 0.18
    x0, x1 = x - w / 2, x + w / 2
    # steps
    for k in range(3):
        e = (2 - k) * w * 0.012
        y1 = base - k * steps_h / 3
        c.rect(x0 - e, y1 - steps_h / 3, x1 + e, y1, mix(col, shade, 0.4 if k % 2 else 0.1), ol=ol, w=lw * 0.8)
    top = base - steps_h
    # dark interior behind the columns
    c.rect(x0 + w * 0.04, top - col_h, x1 - w * 0.04, top, mix(dark, (60, 50, 50), 0.35 if not lit else 0.0),
           ol=None)
    if lit:
        c.rect(x0 + w * 0.04, top - col_h, x1 - w * 0.04, top, mix((120, 110, 140), (255, 220, 150), lit * 0.6),
               ol=None)
    n = 8
    cw = w / n * 0.62
    for k in range(n):
        cx = x0 + w * (k + 0.5) / n
        c.poly([(cx - cw * 0.5, top), (cx - cw * 0.42, top - col_h), (cx + cw * 0.42, top - col_h),
                (cx + cw * 0.5, top)], col, ol=ol, w=lw)
        if detail:
            for f in (-0.22, 0.0, 0.22):
                c.line([(cx + cw * f, top - 3), (cx + cw * f * 0.85, top - col_h + 6)], shade, max(1, lw * 0.6),
                       cap=False)
        c.rect(cx - cw * 0.62, top - col_h - h * 0.025, cx + cw * 0.62, top - col_h, col, ol=ol, w=lw * 0.8)
    # entablature: architrave + triglyph frieze + cornice
    ey = top - col_h - h * 0.025
    c.rect(x0, ey - ent_h * 0.42, x1, ey, col, ol=ol, w=lw)
    c.rect(x0, ey - ent_h * 0.85, x1, ey - ent_h * 0.42, mix(col, shade, 0.5), ol=ol, w=lw)
    if detail:
        m = 16
        for k in range(m + 1):
            tx = x0 + w * k / m
            c.rect(tx - w * 0.008, ey - ent_h * 0.82, tx + w * 0.008, ey - ent_h * 0.45, dark, ol=None)
    c.rect(x0 - w * 0.015, ey - ent_h, x1 + w * 0.015, ey - ent_h * 0.85, col, ol=ol, w=lw)
    # pediment (with its famous broken middle)
    py = ey - ent_h
    if ruin:
        c.poly([(x0 - w * 0.015, py), (x - w * 0.16, py - ped_h * 0.68), (x - w * 0.12, py - ped_h * 0.52),
                (x - w * 0.05, py - ped_h * 0.6), (x + w * 0.02, py - ped_h * 0.42), (x + w * 0.1, py - ped_h * 0.7),
                (x + w * 0.16, py - ped_h * 0.68), (x1 + w * 0.015, py)], col, ol=ol, w=lw)
        c.poly([(x0 + w * 0.06, py - 2), (x - w * 0.12, py - ped_h * 0.45), (x + w * 0.1, py - ped_h * 0.45),
                (x1 - w * 0.06, py - 2)], mix(col, shade, 0.6), ol=None)
    else:
        c.poly([(x0 - w * 0.015, py), (x, py - ped_h), (x1 + w * 0.015, py)], col, ol=ol, w=lw)
        c.poly([(x0 + w * 0.06, py - 2), (x, py - ped_h * 0.8), (x1 - w * 0.06, py - 2)], mix(col, shade, 0.6),
               ol=None)
    return py - ped_h * 0.7


def acropolis_rock(c, x, base, w, h, top_w=None, col=ROCK, shade=ROCK_S, dark=ROCK_D, ol=OUT, lw=2.5,
                   green=(120, 150, 90), seed=1):
    """The flat-topped rock of the Acropolis with its walls. Returns the y of the flat top."""
    top_w = top_w or w * 0.62
    ty = base - h
    pts = [(x - w / 2, base), (x - w * 0.42, base - h * 0.35), (x - top_w / 2 - w * 0.04, ty + h * 0.12),
           (x - top_w / 2, ty), (x + top_w / 2, ty), (x + top_w / 2 + w * 0.05, ty + h * 0.16),
           (x + w * 0.44, base - h * 0.3), (x + w / 2, base)]
    c.poly(pts, col, ol=ol, w=lw)
    # cliff shading and cracks
    c.poly([(x + top_w / 2, ty), (x + top_w / 2 + w * 0.05, ty + h * 0.16), (x + w * 0.44, base - h * 0.3),
            (x + w / 2, base), (x + w * 0.2, base), (x + top_w * 0.3, ty + h * 0.2)], shade, ol=None)
    rng = np.random.default_rng(seed)
    for _ in range(9):
        cx = rng.uniform(x - top_w / 2, x + top_w / 2)
        c.line([(cx, ty + h * 0.08), (cx + rng.uniform(-8, 8), ty + h * rng.uniform(0.25, 0.45))], dark, 1.5,
               cap=False)
    # wall along the top
    c.rect(x - top_w / 2 - 2, ty - h * 0.06, x + top_w / 2 + 2, ty + 2, mix(col, (255, 255, 255), 0.2), ol=ol,
           w=lw * 0.8)
    # bushes on the slopes
    for _ in range(14):
        bx = rng.uniform(x - w * 0.45, x + w * 0.45)
        by = rng.uniform(base - h * 0.35, base - 4)
        r = rng.uniform(5, 12) * w / 600
        c.circle(bx, by, r, green, ol=None)
    return ty - h * 0.06


def olive_tree(c, x, y, s=1.0, seed=0, leaf=OLIVE, leaf_l=OLIVE_L, trunk=OLIVE_TRUNK, t=0.0, ol=OUT):
    """A gnarled olive tree with a silvery, cloudy crown."""
    rng = np.random.default_rng(seed)
    c.push(x, y, s)
    lean = rng.uniform(-14, 14)
    c.poly([(-16, 0), (-8, -40), (-14 + lean, -80), (-4 + lean, -110), (8 + lean, -110), (6 + lean, -76),
            (14, -36), (20, 0)], trunk, ol=ol, w=2.5)
    c.line([(-2, -20), (2 + lean * 0.5, -70)], mix(trunk, (0, 0, 0), 0.25), 2, cap=False)
    c.line([(lean, -100), (-40 + lean, -130)], trunk, 8)
    c.line([(lean + 4, -100), (44 + lean, -128)], trunk, 8)
    sway = math.sin(t * 0.8 + seed) * 2
    blobs = [(-46, -138, 34), (44, -136, 34), (0, -160, 42), (-22, -120, 28), (26, -118, 28), (0, -132, 34)]
    for bx, by, r in blobs:
        c.ellipse(bx + lean + sway, by, r * 1.15, r * 0.8, leaf, ol=ol, w=2.5)
    for bx, by, r in blobs:
        c.ellipse(bx + lean + sway, by, r * 1.1, r * 0.74, leaf, ol=None)
    for _ in range(26):                                   # silvery leaf glints
        bx, by, r = blobs[rng.integers(len(blobs))]
        px = bx + lean + sway + rng.uniform(-r, r)
        py = by + rng.uniform(-r * 0.6, r * 0.6)
        a = rng.uniform(0, math.pi)
        c.line([(px - 5 * math.cos(a), py - 3 * math.sin(a)), (px + 5 * math.cos(a), py + 3 * math.sin(a))],
               leaf_l, 2.5)
    for _ in range(7):                                    # olives
        bx, by, r = blobs[rng.integers(len(blobs))]
        c.circle(bx + lean + sway + rng.uniform(-r * 0.8, r * 0.8), by + rng.uniform(0, r * 0.6), 3.2,
                 (70, 80, 50), ol=None)
    c.pop()


def caryatid(c, x, base, h, col=MARBLE, shade=MARBLE_S, ol=OUT, lw=2.5, k=0):
    """One stone maiden holding up the roof on her head."""
    w = h * 0.2
    top = base - h
    # plinth
    c.rect(x - w * 0.7, base - h * 0.08, x + w * 0.7, base, col, ol=ol, w=lw)
    # dress (a fluted column of drapery)
    by = base - h * 0.08
    c.poly([(x - w * 0.55, by), (x - w * 0.42, top + h * 0.3), (x + w * 0.42, top + h * 0.3), (x + w * 0.55, by)],
           col, ol=ol, w=lw)
    for f in (-0.3, -0.1, 0.1, 0.3):
        c.line([(x + w * f, by - 2), (x + w * f * 0.8, top + h * 0.34)], shade, max(1, lw * 0.6), cap=False)
    knee = 1 if k % 2 else -1                              # one knee bent, like the real ones
    c.ellipse(x + knee * w * 0.2, base - h * 0.42, w * 0.18, h * 0.06, mix(col, shade, 0.3), ol=None)
    # shoulders and arms
    c.ellipse(x, top + h * 0.32, w * 0.5, h * 0.06, col, ol=ol, w=lw)
    # head, hair and the capital on top
    c.ellipse(x, top + h * 0.2, w * 0.24, h * 0.085, col, ol=ol, w=lw)
    c.ellipse(x, top + h * 0.13, w * 0.3, h * 0.05, mix(col, shade, 0.35), ol=ol, w=lw * 0.8)
    for side in (-1, 1):                                   # long braids
        c.line([(x + side * w * 0.22, top + h * 0.17), (x + side * w * 0.3, top + h * 0.34)], shade, 3)
    c.rect(x - w * 0.34, top + h * 0.03, x + w * 0.34, top + h * 0.095, col, ol=ol, w=lw * 0.8, r=3)
    c.rect(x - w * 0.5, top, x + w * 0.5, top + h * 0.035, col, ol=ol, w=lw * 0.8)


def caryatid_porch(c, x, base, w, h, col=MARBLE, shade=MARBLE_S, dark=MARBLE_D, ol=OUT, lw=2.5):
    """The Porch of the Maidens: six caryatids under a heavy roof on a tall base."""
    podium_h = h * 0.3
    c.rect(x - w / 2, base - podium_h, x + w / 2, base, mix(col, shade, 0.25), ol=ol, w=lw)
    for k in range(1, 4):
        c.line([(x - w / 2, base - podium_h * k / 4), (x + w / 2, base - podium_h * k / 4)], shade, 1.5, cap=False)
    # back wall (the temple behind)
    wall_top = base - h * 1.02
    c.rect(x - w * 0.62, wall_top, x + w * 0.62, base - podium_h, mix(dark, (80, 70, 70), 0.3), ol=ol, w=lw)
    for k in range(5):
        yy = wall_top + (base - podium_h - wall_top) * k / 5
        c.line([(x - w * 0.62, yy), (x + w * 0.62, yy)], mix(dark, (60, 50, 50), 0.4), 1.5, cap=False)
    mh = h * 0.6
    for k in range(6):
        cx = x - w / 2 + w * (k + 0.5) / 6
        caryatid(c, cx, base - podium_h, mh, col, shade, ol, lw, k)
    # the roof they hold
    ry = base - podium_h - mh
    c.rect(x - w / 2 - 6, ry - h * 0.06, x + w / 2 + 6, ry, col, ol=ol, w=lw)
    c.rect(x - w / 2 - 12, ry - h * 0.12, x + w / 2 + 12, ry - h * 0.06, mix(col, shade, 0.3), ol=ol, w=lw)
    for k in range(18):
        dx = x - w / 2 + w * (k + 0.5) / 18
        c.circle(dx, ry - h * 0.03, 2.5, shade, ol=None)


def broken_column(c, x, base, h, r=20, col=MARBLE, shade=MARBLE_S, ol=OUT, lw=2.5, lying=False, top_break=True):
    if lying:
        c.rect(x - h / 2, base - 2 * r, x + h / 2, base, col, ol=ol, w=lw, r=4)
        for k in range(1, 4):
            c.line([(x - h / 2 + 6, base - 2 * r * k / 4), (x + h / 2 - 6, base - 2 * r * k / 4)], shade, 1.5,
                   cap=False)
        c.ellipse(x + h / 2, base - r, r * 0.45, r, mix(col, shade, 0.3), ol=ol, w=lw)
        return
    c.rect(x - r * 1.35, base - 12, x + r * 1.35, base, col, ol=ol, w=lw)
    pts = [(x - r, base - 12), (x - r, base - h)]
    if top_break:
        pts += [(x - r * 0.4, base - h - 10), (x + r * 0.1, base - h + 4), (x + r * 0.6, base - h - 6),
                (x + r, base - h + 2)]
    else:
        pts += [(x + r, base - h)]
    pts += [(x + r, base - 12)]
    c.poly(pts, col, ol=ol, w=lw)
    for f in (-0.5, 0.0, 0.5):
        c.line([(x + r * f, base - 14), (x + r * f, base - h + 10)], shade, 1.5, cap=False)
    for yy in (base - h * 0.4, base - h * 0.75):
        if yy < base - 20:
            c.line([(x - r, yy), (x + r, yy)], shade, 1.5, cap=False)


def marble_block(c, x, base, w, h, col=MARBLE, shade=MARBLE_S, ol=OUT, lw=2.5):
    c.rect(x - w / 2, base - h, x + w / 2, base, col, ol=ol, w=lw, r=3)
    c.rect(x - w / 2, base - h, x + w / 2, base - h + 8, mix(col, (255, 255, 255), 0.3), ol=None, r=3)
    c.line([(x - w / 2 + 6, base - h * 0.45), (x + w / 2 - 10, base - h * 0.5)], shade, 1.5, cap=False)


def temple_far(c, x, base, w, h, col, shade, ol=None, lw=1.5, n=6):
    """A small simplified temple (Hephaestus) for far backgrounds."""
    c.rect(x - w / 2 - 6, base - h * 0.08, x + w / 2 + 6, base, col, ol=ol, w=lw)
    top = base - h * 0.08
    ch = h * 0.6
    c.rect(x - w / 2 + 4, top - ch, x + w / 2 - 4, top, shade, ol=None)
    for k in range(n):
        cx = x - w / 2 + w * (k + 0.5) / n
        c.rect(cx - w / n * 0.28, top - ch, cx + w / n * 0.28, top, col, ol=ol, w=lw)
    c.rect(x - w / 2, top - ch - h * 0.12, x + w / 2, top - ch, col, ol=ol, w=lw)
    c.poly([(x - w / 2 - 4, top - ch - h * 0.12), (x, top - ch - h * 0.32), (x + w / 2 + 4, top - ch - h * 0.12)],
           col, ol=ol, w=lw)


# ================================================================ the Plaka

def bougainvillea(c, x, y, rx, ry, seed=0, col=BOUG, col_l=BOUG_L, leaf=(70, 130, 70), ol=OUT):
    rng = np.random.default_rng(seed)
    c.ellipse(x, y, rx, ry, leaf, ol=ol, w=2)
    for _ in range(int(rx * ry / 30)):
        a = rng.uniform(0, math.tau)
        r = math.sqrt(rng.uniform(0, 1))
        px, py = x + math.cos(a) * rx * r * 0.95, y + math.sin(a) * ry * r * 0.95
        c.circle(px, py, rng.uniform(3, 5.5), col if rng.random() < 0.6 else col_l, ol=None)


def house(c, x0, x1, base, h, wall, rng, door=True, roof="flat", shutter=GBLUE, balcony=False, boug=False,
          seed=0, sign=None):
    """A Plaka house: whitewashed or ochre wall, blue door and shutters, maybe a tiled roof."""
    c.rect(x0, base - h, x1, base, wall, w=2.5)
    w = x1 - x0
    if roof == "tile":
        c.poly([(x0 - 10, base - h + 2), (x0 + w * 0.5, base - h - 34), (x1 + 10, base - h + 2)],
               (200, 104, 70), w=2.5)
        for k in range(1, 4):
            c.line([(x0 - 10 + (w * 0.5 + 10) * k / 4, base - h + 2 - 36 * k / 4),
                    (x1 + 10 - (w * 0.5 + 10) * k / 4, base - h + 2 - 36 * k / 4)], (170, 84, 56), 2, cap=False)
    else:
        c.rect(x0 - 4, base - h - 8, x1 + 4, base - h, mix(wall, (0, 0, 0), 0.1), w=2)
    # windows with shutters
    rows = max(1, int((h - 110) // 90) + 1)
    for r in range(rows):
        wy = base - h + 30 + r * 90
        if wy + 60 > base - 110 and door:
            break
        for wx in np.arange(x0 + 26, x1 - 50, 80):
            c.rect(wx, wy, wx + 34, wy + 50, (60, 70, 90), w=2)
            c.rect(wx - 14, wy, wx, wy + 50, shutter, w=2)
            c.rect(wx + 34, wy, wx + 48, wy + 50, shutter, w=2)
            for k in range(1, 5):
                c.line([(wx - 13, wy + k * 10), (wx - 1, wy + k * 10)], mix(shutter, (0, 0, 0), 0.3), 1, cap=False)
                c.line([(wx + 35, wy + k * 10), (wx + 47, wy + k * 10)], mix(shutter, (0, 0, 0), 0.3), 1, cap=False)
            if rng.random() < 0.5:                       # a flower pot on the ledge
                c.rect(wx + 4, wy + 50, wx + 30, wy + 62, (200, 110, 70), w=1.5, r=2)
                for k in range(4):
                    c.circle(wx + 8 + k * 6, wy + 46, 4, (230, 60, 70) if k % 2 else (90, 150, 80), w=1)
    if balcony:
        by = base - h + 120
        c.rect(x0 + 10, by, x1 - 10, by + 8, (230, 226, 216), w=2)
        for bx in np.arange(x0 + 16, x1 - 10, 12):
            c.line([(bx, by - 30), (bx, by)], (60, 60, 70), 2, cap=False)
        c.line([(x0 + 12, by - 30), (x1 - 12, by - 30)], (60, 60, 70), 3, cap=False)
    if door:
        dx = x0 + w * 0.5
        c.rect(dx - 26, base - 96, dx + 26, base, shutter, w=2.5, r=0)
        c.ellipse(dx, base - 96, 26, 18, shutter, w=2.5)
        c.rect(dx - 24, base - 96, dx + 24, base - 2, shutter, ol=None)
        c.line([(dx, base - 110), (dx, base)], mix(shutter, (0, 0, 0), 0.3), 2, cap=False)
        c.circle(dx + 12, base - 46, 2.5, (240, 200, 90), ol=None)
        c.rect(dx - 34, base - 6, dx + 34, base, mix(wall, (0, 0, 0), 0.15), w=1.5)
    if sign:
        c.rect(x0 + w * 0.5 - 70, base - h + 8, x0 + w * 0.5 + 70, base - h + 36, (250, 244, 226), w=2, r=4)
        c.text(x0 + w * 0.5, base - h + 22, sign, 15, GBLUE)
    if boug:
        bougainvillea(c, x1 - 20, base - h + 30, 60, 38, seed=seed)
        rr = np.random.default_rng(seed + 9)
        for k in range(10):
            c.circle(x1 - 30 + rr.uniform(-30, 30), base - h + 60 + rr.uniform(0, 120) * (k / 10), 4,
                     BOUG_L if k % 2 else BOUG, ol=None)


def souvlaki_stand(c, x, base, s=1.0, t=0.0, smoke=True):
    c.push(x, base, s)
    # umbrella
    c.line([(0, -60), (0, -230)], (110, 90, 70), 4)
    for k in range(6):
        a0 = -math.pi + k * math.pi / 6
        a1 = a0 + math.pi / 6
        col = (40, 110, 200) if k % 2 else (250, 250, 250)
        c.poly([(0, -232), (math.cos(a0) * 110, -200 - math.sin(a0) * -10), (math.cos(a1) * 110,
                -200 - math.sin(a1) * -10)], col, w=2)
    # cart
    c.rect(-80, -100, 80, -30, (40, 110, 200), w=3, r=6)
    c.rect(-80, -112, 80, -100, (210, 214, 222), w=2.5)
    c.text(0, -64, "SOUVLAKI", 17, (255, 255, 255), stroke=1.5)
    for wx in (-56, 56):
        c.circle(wx, -24, 20, (70, 70, 80), w=3)
        c.circle(wx, -24, 7, (200, 200, 210), w=2)
    # skewers on the grill
    for k in range(5):
        sx = -50 + k * 25
        c.line([(sx - 12, -116), (sx + 14, -124)], (190, 190, 190), 2, cap=False)
        for j in range(3):
            c.ellipse(sx - 6 + j * 7, -119 - j * 2, 6, 5, (170, 100, 60) if j != 1 else (220, 90, 60), w=1.5)
    # pita breads
    c.ellipse(-60, -114, 14, 5, (240, 214, 160), w=1.5)
    if smoke:
        for k in range(4):
            u = (t * 0.35 + k / 4) % 1.0
            c.circle(-20 + k * 14 + 18 * math.sin(t + k), -130 - u * 90, 8 + 14 * u,
                     mix((230, 230, 236), (250, 246, 236), u), ol=None)
    c.pop()


def taverna_table(c, x, base, s=1.0):
    """A little square taverna table with a blue-and-white check cloth, and a blue chair."""
    c.push(x, base, s)
    c.line([(-50, 0), (-46, -70)], (120, 90, 60), 5)
    c.line([(50, 0), (46, -70)], (120, 90, 60), 5)
    c.rect(-70, -84, 70, -66, (250, 250, 250), w=2.5)
    for k in range(7):
        c.rect(-70 + k * 20, -84, -60 + k * 20, -66, (60, 120, 210), ol=None)
    c.poly([(-70, -66), (70, -66), (64, -50), (-64, -50)], (250, 250, 250), w=2)
    for k in range(7):
        c.poly([(-70 + k * 20, -66), (-60 + k * 20, -66), (-58 + k * 19, -50), (-62 + k * 19, -50)],
               (60, 120, 210), ol=None)
    c.pop()


def chair(c, x, base, s=1.0, col=GBLUE):
    c.push(x, base, s)
    for lx in (-22, 22):
        c.line([(lx, 0), (lx, -46)], col, 5)
    c.line([(-22, -46), (-22, -110)], col, 5)
    c.rect(-28, -52, 28, -44, (220, 190, 120), w=2)
    for k in range(3):
        c.line([(-22, -70 - k * 14), (-6, -70 - k * 14)], col, 4)
    c.pop()


def yogurt_bowl(c, x, base, s=1.0, eaten=0.0, honey=True):
    c.push(x, base, s)
    c.poly([(-46, -34), (46, -34), (34, 0), (-34, 0)], (210, 120, 70), w=3)
    for k in range(5):                                   # a meander band, like a vase
        c.rect(-36 + k * 15, -24, -28 + k * 15, -16, BLACKFIG, ol=None)
    c.ellipse(0, -34, 46, 10, (190, 106, 62), w=3)
    if eaten < 1:
        hgt = 14 * (1 - eaten)
        c.ellipse(0, -36 - hgt * 0.5, 40 * (1 - eaten * 0.4), 8 + hgt * 0.5, YOGURT, w=2)
        if honey and eaten < 0.5:
            c.line([(-22, -40 - hgt * 0.6), (-6, -44 - hgt * 0.7), (8, -40 - hgt * 0.6), (22, -44 - hgt * 0.6)],
                   HONEY, 5)
            c.circle(0, -46 - hgt * 0.7, 6, HONEY_L, w=1.5)
    c.pop()


def basil_pot(c, x, base, s=1.0):
    c.push(x, base, s)
    c.poly([(-22, -36), (22, -36), (16, 0), (-16, 0)], (200, 110, 70), w=2.5)
    for dx, dy, r in ((-12, -48, 12), (10, -50, 13), (0, -62, 14), (-2, -46, 12)):
        c.circle(dx, dy, r, (80, 150, 70), w=2)
    c.pop()


# ============================================================ black-figure

def meander(c, x0, x1, y, h, col=BLACKFIG):
    """Greek key band between x0 and x1, top at y, height h."""
    c.rect(x0, y, x1, y + 3, col, ol=None)
    c.rect(x0, y + h - 3, x1, y + h, col, ol=None)
    step = h * 1.2
    x = x0 + 4
    lw = max(1.5, h * 0.09)
    while x + step < x1:
        a, b = y + h * 0.22, y + h * 0.78
        pts = [(x, b), (x, a), (x + step * 0.75, a), (x + step * 0.75, b - h * 0.18), (x + step * 0.3, b - h * 0.18),
               (x + step * 0.3, a + h * 0.22)]
        c.line(pts, col, lw, cap=False)
        c.line([(x, b), (x + step, b)], col, lw, cap=False)
        x += step


def bf_figure(c, x, base, s=1.0, kind="athena", arm=0.0, col=BLACKFIG, inc=TERRA_L, face=1):
    """Black-figure people from a Greek vase, in profile.

    kind: athena (helmet, spear, shield) | poseidon (beard, trident) | person.
    arm: 0..1 raises the front arm.
    """
    c.push(x, base, s, flip=face < 0)
    # legs and long robe
    if kind == "athena":
        c.poly([(-22, 0), (-12, -90), (16, -90), (26, 0)], col, ol=None)
        for f in (-6, 4, 14):
            c.line([(f, -6), (f * 0.6, -84)], inc, 1.5, cap=False)
    else:
        c.poly([(-24, 0), (-14, -6), (-2, -60), (6, -60), (20, -4), (30, 0), (14, 0), (2, -40), (-10, 0)],
               col, ol=None)
        c.poly([(-16, -50), (16, -50), (12, -92), (-12, -92)], col, ol=None)
        c.line([(-14, -56), (14, -56)], inc, 1.5, cap=False)
    # torso and head
    c.ellipse(0, -104, 16, 20, col, ol=None)
    c.circle(4, -136, 13, col, ol=None)
    c.poly([(14, -138), (22, -132), (15, -128)], col, ol=None)      # nose
    c.circle(10, -139, 2, inc, ol=None)                             # incised eye
    if kind == "athena":
        c.poly([(-12, -142), (2, -158), (16, -146), (14, -136), (-10, -134)], col, ol=None)   # helmet
        c.poly([(-14, -150), (-4, -172), (14, -166), (4, -154)], col, ol=None)                 # crest
        c.line([(-6, -170), (8, -164)], inc, 1.5, cap=False)
        c.circle(-22, -98, 26, col, ol=None)                                                   # shield
        c.circle(-22, -98, 18, None, ol=inc, w=1.5)
        c.circle(-22, -98, 5, inc, ol=None)
    elif kind == "poseidon":
        c.poly([(6, -128), (18, -124), (12, -108), (2, -114)], col, ol=None)                    # beard
        for k in range(3):
            c.line([(6 + k * 4, -124), (6 + k * 3, -112)], inc, 1, cap=False)
        c.poly([(-8, -148), (6, -152), (14, -144), (-10, -140)], col, ol=None)                  # hair band
    else:
        c.poly([(-8, -146), (12, -150), (14, -142), (-8, -136)], col, ol=None)
    # arm with a staff
    ang = math.radians(-20 - 70 * arm)
    sx, sy = 6, -112
    hx, hy = sx + math.cos(ang) * 34, sy + math.sin(ang) * 34
    c.line([(sx, sy), (hx, hy)], col, 7)
    if kind == "athena":
        c.line([(hx - 8, hy + 90), (hx + 6, hy - 70)], col, 3, cap=False)
        c.poly([(hx + 6, hy - 70), (hx + 1, hy - 86), (hx + 12, hy - 68)], col, ol=None)
    elif kind == "poseidon":
        c.line([(hx - 6, hy + 90), (hx + 6, hy - 60)], col, 3, cap=False)
        for k in (-1, 0, 1):
            c.line([(hx + 6 + k * 8, hy - 60), (hx + 6 + k * 8 + 1, hy - 80)], col, 3, cap=False)
        c.line([(hx - 2, hy - 60), (hx + 14, hy - 60)], col, 3, cap=False)
    c.pop()


def bf_owl(c, x, base, s=1.0, col=BLACKFIG, inc=TERRA_L, blink=False):
    c.push(x, base, s)
    c.ellipse(0, -40, 26, 36, col, ol=None)
    c.ellipse(0, -84, 26, 22, col, ol=None)
    c.poly([(-22, -96), (-14, -112), (-8, -98)], col, ol=None)
    c.poly([(22, -96), (14, -112), (8, -98)], col, ol=None)
    for ex in (-10, 10):
        if blink:
            c.line([(ex - 7, -86), (ex + 7, -86)], inc, 2, cap=False)
        else:
            c.circle(ex, -86, 8, inc, ol=None)
            c.circle(ex, -86, 3.5, col, ol=None)
    c.poly([(-3, -78), (3, -78), (0, -70)], inc, ol=None)
    for k in range(4):
        c.arc(0, -40 + k * 8 - 10, 14, 6, 20, 160, inc, 1.5)
    for fx in (-8, 8):
        c.line([(fx, -4), (fx, 2)], col, 4, cap=False)
    c.pop()


def bf_olive(c, x, base, grow=1.0, col=BLACKFIG, inc=TERRA_L, seed=4):
    """A black-figure olive tree that grows from a sprout (grow 0..1)."""
    if grow <= 0.02:
        return
    c.push(x, base, 0.3 + 0.7 * grow)
    c.poly([(-10, 0), (-5, -90), (5, -90), (12, 0)], col, ol=None)
    for side in (-1, 1):
        c.line([(0, -80), (side * 50, -130)], col, 6)
    rng = np.random.default_rng(seed)
    n = int(40 * grow)
    for k in range(n):
        a = rng.uniform(0, math.tau)
        r = math.sqrt(rng.uniform(0, 1))
        lx, ly = math.cos(a) * 90 * r, -140 + math.sin(a) * 60 * r
        ang = rng.uniform(0, math.pi)
        c.ellipse(lx, ly, 11, 4, col, ol=None) if abs(math.cos(ang)) > 0.5 else c.ellipse(lx, ly, 4, 9, col, ol=None)
    for k in range(int(10 * grow)):
        a = rng.uniform(0, math.tau)
        r = math.sqrt(rng.uniform(0, 1))
        c.circle(math.cos(a) * 80 * r, -140 + math.sin(a) * 50 * r, 4, inc, ol=None)
    c.pop()
