"""Lisbon props and new characters, in the flat cartoon style of draw.py.

Characters: Tiago (a curly black Portuguese water dog), Avo Lurdes (his white-
curled grandmother in a black fado shawl), Dom Pavao (the castle peacock),
seagulls. Landmarks: Belem Tower, the Discoveries monument, the 25 de Abril
bridge, Cristo Rei, the Santa Justa lift, Sao Jorge castle, tiled houses,
red roofs. Things: the yellow scooter with its sidecar, tram 28, a grill of
sardines, custard tarts, a Portuguese guitar, lanterns, fireworks.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease

# ------------------------------------------------------------------ colours
YELLOW = (250, 200, 40)
YELLOW_D = (214, 158, 20)
CREAM = (250, 242, 220)
TILE_BLUE = (40, 90, 175)
TILE_WHITE = (240, 244, 250)
TERRACOTTA = (206, 96, 60)
TERRACOTTA_D = (168, 72, 46)
LIMESTONE = (236, 226, 200)
LIMESTONE_D = (200, 186, 156)
BRIDGE_RED = (204, 72, 46)
BRIDGE_RED_D = (150, 50, 34)
IRON = (70, 70, 82)
SARDINE = (178, 196, 212)
SARDINE_D = (70, 100, 140)

TIAGO = dict(body=(46, 46, 56), curl=(78, 78, 94), muzzle=(238, 234, 226), chest=(238, 234, 226),
             ear=(36, 36, 44), nose=(20, 20, 26), eye=(120, 80, 40))
AVO = dict(body=(236, 232, 224), curl=(210, 204, 196), muzzle=(250, 248, 242), chest=(250, 248, 242),
           ear=(214, 208, 200), nose=(40, 34, 36), eye=(90, 70, 50))


def R(ang, x, y):
    ca, sa = math.cos(ang), math.sin(ang)
    return (x * ca - y * sa, x * sa + y * ca)


def shade_bottom(c, tl, t, strength=0.5, top=540, _masks={}):
    """Darken the bottom of the frame softly while a subtitle shows."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    key = (q, top)
    if key not in _masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _masks[key] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((18, 14, 26), (0, top * SS, W * SS, H * SS), _masks[key])


def rotated(c, draw_fn, px, py, ang_deg, box=(-400, -400, 400, 400)):
    """Draw draw_fn(canvas) in a local space whose origin is (px, py) of c, rotated by ang_deg
    (positive = counter-clockwise on screen) and paste it onto c with transparency."""
    x0, y0, x1, y1 = box
    sc = c.scale
    w, h = int((x1 - x0) * sc * SS), int((y1 - y0) * sc * SS)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cc = Canvas(img)
    cc.tint = c.tint
    cc.push(-x0 * sc, -y0 * sc, sc)
    draw_fn(cc)
    if abs(ang_deg) > 0.05:
        # rotate about the local origin, which sits at (-x0, -y0) in the image
        img = img.rotate(ang_deg, resample=Image.BICUBIC, center=(-x0 * sc * SS, -y0 * sc * SS))
    gx, gy = c.P(px, py)
    c.img.paste(img, (int(gx + x0 * sc * SS), int(gy + y0 * sc * SS)), img)


# ======================================================================= dogs

def _curls(c, cx, cy, rx, ry, col, n=10, r=7, seed=0, a0=0.0, a1=math.tau):
    rng = np.random.default_rng(seed)
    for k in range(n):
        a = lerp(a0, a1, (k + 0.5) / n)
        px = cx + math.cos(a) * rx * rng.uniform(0.3, 0.85)
        py = cy + math.sin(a) * ry * rng.uniform(0.3, 0.85)
        c.arc(px, py, r, r * 0.8, 200, 520 if False else 340, col, 2.5)


def _dog_head(c, hx, hy, pal, t, mouth, eyes, look, ear_flap=0.0, glasses=False, cap=None, seed=0.0):
    body, curl = pal["body"], pal["curl"]
    # floppy ears (behind)
    flap = math.sin(t * 3 + seed) * 2 + ear_flap
    c.ellipse(hx - 26, hy + 8 + flap, 13, 26, pal["ear"])
    # head with curly top
    c.ellipse(hx, hy, 34, 31, body)
    for k, (dx, dy) in enumerate(((-20, -26), (-6, -32), (9, -31), (21, -24))):
        c.circle(hx + dx, hy + dy, 10, body)
    c.ellipse(hx, hy - 8, 32, 26, body, ol=None)
    for dx, dy in ((-14, -22), (2, -26), (-24, -6), (14, -18)):
        c.arc(hx + dx, hy + dy, 6, 5, 200, 340, curl, 2.5)
    # muzzle
    c.ellipse(hx + 26, hy + 12, 22, 15, pal["muzzle"])
    c.ellipse(hx + 44, hy + 4, 8, 6, pal["nose"], w=2)
    c.circle(hx + 46, hy + 2, 2, (120, 120, 130), ol=None)
    # mouth
    if mouth > 0.05:
        h = 3 + 10 * mouth
        c.ellipse(hx + 32, hy + 22 + h * 0.4, 9, h, D.MOUTH, w=2)
        c.ellipse(hx + 32, hy + 22 + h * 0.8, 6, 3 + 2 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 30, hy + 18, 10, 6, 10, 170, OUT, 2)
    # eyes
    ex, ey = hx + 12, hy - 6
    if eyes == "closed":
        c.arc(ex, ey, 7, 5, 20, 160, (240, 240, 240) if pal is TIAGO else OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 7, 7, 200, 340, (240, 240, 240) if pal is TIAGO else OUT, 3)
    else:
        big = 1.2 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 8 * big, 9 * big, (255, 255, 255), w=2.5)
        lx, ly = look
        c.circle(ex + 2 + lx * 2.5, ey + 1 + ly * 2.5, 5 * big, pal["eye"], ol=None)
        c.circle(ex + 2 + lx * 2.5, ey + 1 + ly * 2.5, 2.6 * big, (20, 15, 20), ol=None)
        c.circle(ex + 3.5 + lx * 2.5, ey - 1.5 + ly * 2.5, 1.6, (255, 255, 255), ol=None)
    # eyebrow tuft
    c.arc(ex - 2, ey - 14, 9, 4, 200, 330, pal["curl"], 3)
    if glasses:
        c.circle(ex, ey, 11, None, ol=(200, 170, 80), w=2)
        c.line([(ex - 11, ey), (hx - 18, ey - 4)], (200, 170, 80), 2, cap=False)
    # near ear
    c.ellipse(hx - 14, hy + 10 + flap, 12, 25, pal["ear"])
    for k in range(3):
        c.arc(hx - 14, hy + flap + k * 12, 6, 4, 20, 160, pal["curl"], 2)
    if cap is not None:
        # a flat fisherman's cap
        c.ellipse(hx - 2, hy - 32, 34, 12, cap)
        c.ellipse(hx + 26, hy - 28, 18, 6, mix(cap, (0, 0, 0), 0.25))
        c.ellipse(hx - 4, hy - 36, 26, 9, cap, ol=None)


def dog(c, x, y, s=1.0, face=1, t=0.0, pal=TIAGO, pose="stand", walk=0.0, mouth=0.0, eyes="open",
        look=(0.0, 0.0), arm=0.0, arm2=None, scarf=(250, 200, 40), cap=(40, 60, 110), shawl=None,
        glasses=False, tail=None, seed=3.0, head_dy=0.0, hold=None):
    """A curly water dog. pose: stand | walk | sit. arm: raise of the near front paw (sit) in 0..1
    (0 down, 0.5 forward, 1 up waving). hold(c, px, py): draws something held in that paw."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    body, curl = pal["body"], pal["curl"]
    c.push(x, y, s, flip=face < 0)
    wag = math.sin(t * 7 + seed) if tail is None else tail
    if pose == "sit":
        # plumed tail on the ground behind
        pts = [(-34 - 30 * u, -12 - 30 * u + 8 * wag * u) for u in np.linspace(0, 1, 7)]
        c.stroke(pts, body, 12)
        c.circle(pts[-1][0], pts[-1][1], 11, body)
        c.ellipse(-8, -30, 40, 30, body)                      # haunch
        _curls(c, -8, -30, 40, 30, curl, n=7, r=6, seed=1)
        c.ellipse(8, -70, 34, 46, body)                       # chest
        c.ellipse(20, -72, 18, 32, pal["chest"], ol=None)
        if shawl:
            c.poly([(-26, -106), (40, -106), (46, -60), (10, -40), (-30, -64)], shawl)
            for k in range(6):
                c.line([(-26 + k * 12, -52 + abs(k - 2.5) * 4), (-24 + k * 12, -40 + abs(k - 2.5) * 4)], shawl, 2)
        # far paw on the ground
        c.ellipse(30, -6, 12, 7, body)
        # near front leg / arm
        sh = (18, -84)
        if arm2 is not None:
            pass
        ang = math.radians(lerp(80, -60, arm))   # 80 = hanging down, -60 = up
        ex = (sh[0] + math.cos(ang) * 34, sh[1] + math.sin(ang) * 34)
        if arm <= 0.02:
            c.stroke([sh, (14, -40), (12, -8)], body, 14)
            c.ellipse(16, -6, 12, 7, body)
        else:
            px, py = ex[0] + math.cos(ang - 0.4) * 30, ex[1] + math.sin(ang - 0.4) * 30
            c.stroke([sh, ex, (px, py)], body, 14)
            c.circle(px, py, 9, body)
            if hold:
                hold(c, px, py)
        hx, hy = 24, -128 + head_dy
        if scarf:
            c.poly([(hx - 22, hy + 26), (hx + 18, hy + 26), (hx - 2, hy + 48)], scarf, w=2)
        _dog_head(c, hx, hy, pal, t, mouth, eyes, look, glasses=glasses, cap=cap, seed=seed)
        if shawl:
            # headscarf for Avo
            pass
    else:
        by = -54
        tp = [(-52 - 8 * u + 10 * wag * u * u, by - 8 - 60 * u + 6 * u * u) for u in np.linspace(0, 1, 7)]
        c.stroke(tp, body, 12)
        c.circle(tp[-1][0] + 4, tp[-1][1] - 2, 13, body)
        _curls(c, tp[-1][0] + 4, tp[-1][1] - 2, 10, 10, curl, n=3, r=5, seed=2)

        def leg(hx_, phase, col):
            if walk:
                sw = math.sin(walk + phase)
                foot = (hx_ + sw * 14, -max(0.0, math.cos(walk + phase)) * 8)
            else:
                foot = (hx_, 0)
            c.stroke([(hx_, by + 6), foot], col, 15)
            c.ellipse(foot[0] + 4, foot[1] - 3, 11, 6.5, col)

        dk = mix(body, (0, 0, 0), 0.25)
        leg(-34, math.pi, dk)
        leg(34, 0, dk)
        c.ellipse(0, by, 60, 32, body)
        _curls(c, 0, by, 60, 32, curl, n=10, r=7, seed=3)
        leg(-26, 0, body)
        leg(40, math.pi, body)
        c.ellipse(34, by + 4, 22, 22, pal["chest"], ol=None)
        bob = math.sin(walk * 2) * 2 if walk else 0
        hx, hy = 62, by - 40 + bob + head_dy
        if scarf:
            c.poly([(hx - 26, hy + 24), (hx + 10, hy + 30), (hx - 12, hy + 50)], scarf, w=2)
        _dog_head(c, hx, hy, pal, t, mouth, eyes, look, glasses=glasses, cap=cap, seed=seed)
    c.pop()


# ==================================================================== peacock

PEA_BLUE = (30, 90, 190)
PEA_BLUE_D = (20, 60, 140)
PEA_GREEN = (40, 150, 110)
PEA_GREEN_D = (24, 104, 80)
PEA_GOLD = (220, 180, 60)


def _eye_spot(c, x, y, r):
    c.ellipse(x, y, r * 1.0, r * 1.25, PEA_GOLD, ol=None)
    c.ellipse(x, y, r * 0.75, r * 0.95, (40, 160, 150), ol=None)
    c.ellipse(x, y + r * 0.1, r * 0.45, r * 0.55, (20, 40, 110), ol=None)


def peacock(c, x, y, s=1.0, face=1, t=0.0, fan=0.0, mouth=0.0, walk=0.0, eyes="open", seed=5.0, bow=0.0,
            look=(0.0, 0.0)):
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    shimmer = math.sin(t * 6) * 0.04
    # tail: open fan or long train
    if fan > 0.02:
        R0 = 200 * ease(fan)
        cx, cy = -16, -84
        n = 23
        for k in range(n):
            a = math.radians(lerp(-178, -2, k / (n - 1))) + shimmer * math.sin(k)
            tip = (cx + math.cos(a) * R0, cy + math.sin(a) * R0 * 0.9)
            c.line([(cx, cy), tip], PEA_GREEN_D, 9 * fan, cap=False)
        c.ellipse(cx, cy, R0 * 0.96, R0 * 0.86, PEA_GREEN, ol=OUT, w=3)
        c.rect(cx - R0 - 4, cy + 2, cx + R0 + 4, cy + R0, None, ol=None) if False else None
        # lower half of the ellipse hidden behind the body -> cut by drawing nothing below cy
        for ring, rr in ((0.92, 15), (0.7, 12), (0.48, 9)):
            m = int(20 * ring) + 2
            for k in range(m):
                a = math.radians(lerp(-172, -8, k / (m - 1)))
                ex, ey = cx + math.cos(a) * R0 * ring, cy + math.sin(a) * R0 * ring * 0.86
                if ey < cy + 10:
                    _eye_spot(c, ex, ey, rr * fan)
        # cover the part of the fan below the body line
        c.poly([(cx - R0 - 8, cy + 6), (cx + R0 + 8, cy + 6), (cx + R0 + 8, cy + R0), (cx - R0 - 8, cy + R0)],
               None, ol=None) if False else None
    else:
        pts = [(-20, -70), (-90, -50), (-170, -20), (-200, -6), (-180, 4), (-90, -18), (-10, -40)]
        c.poly(pts, PEA_GREEN, w=2.5)
        for k, (ex, ey) in enumerate(((-176, -6), (-140, -20), (-140, -6), (-104, -32), (-104, -18), (-70, -40))):
            _eye_spot(c, ex, ey, 6)
    # legs
    st = math.sin(walk) * 10 if walk else 0
    for lx, ph in ((-6, 0), (10, math.pi)):
        sw = math.sin(walk + ph) * 10 if walk else 0
        c.line([(lx, -44), (lx + sw, -2)], (150, 150, 160), 4)
        c.line([(lx + sw - 8, 0), (lx + sw + 10, 0)], (150, 150, 160), 3)
    # body
    c.ellipse(0, -70, 36, 32, PEA_BLUE)
    c.ellipse(-14, -66, 24, 20, PEA_BLUE_D, ol=None)
    for k in range(3):
        c.arc(-18 + k * 8, -62, 10, 6, 20, 160, (190, 170, 120), 2)
    # neck + head
    hx, hy = 28 + 18 * bow, -150 + 70 * bow
    c.stroke([(14, -88), (24, -118), (hx, hy + 10)], PEA_BLUE, 18)
    c.circle(hx, hy, 15, PEA_BLUE)
    for k, dx in enumerate((-8, 0, 8)):
        tip = (hx + dx - 4, hy - 34 + abs(dx) * 0.6)
        c.line([(hx + dx * 0.4, hy - 12), tip], (40, 70, 140), 2, cap=False)
        c.circle(tip[0], tip[1], 4, PEA_BLUE, w=1.5)
    # face: white stripe, eye, beak
    c.ellipse(hx + 4, hy - 1, 7, 4, (250, 250, 250), ol=None)
    if eyes == "closed":
        c.arc(hx + 5, hy - 2, 4, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(hx + 5, hy + 1, 4, 4, 200, 340, OUT, 2)
    else:
        c.circle(hx + 5 + look[0], hy - 2 + look[1], 3.2, (20, 15, 20), ol=None)
        c.circle(hx + 6, hy - 3, 1.1, (255, 255, 255), ol=None)
    op = 6 * mouth
    c.poly([(hx + 12, hy - 3), (hx + 28, hy + 1), (hx + 12, hy + 3)], (190, 170, 150), w=1.5)
    c.poly([(hx + 12, hy + 3), (hx + 24, hy + 4 + op), (hx + 12, hy + 6 + op * 0.4)], (170, 150, 130), w=1.5)
    c.pop()


def gull(c, x, y, s=1.0, face=1, t=0.0, fly=True, seed=0.0):
    c.push(x, y, s, flip=face < 0)
    if fly:
        f = math.sin(t * 9 + seed)
        for side in (-1, 1):
            tip = (side * 46, -6 - 22 * f)
            mid = (side * 20, -4 - 10 * f)
            c.poly([(0, 0), mid, tip, (side * 22, 4)], (235, 238, 242), w=2)
            c.line([mid, tip], (110, 116, 130), 3, cap=False)
        c.ellipse(0, 0, 16, 8, (250, 250, 252), w=2)
        c.circle(14, -4, 7, (250, 250, 252), w=2)
        c.poly([(19, -5), (30, -3), (19, -1)], (245, 190, 60), w=1.5)
    else:
        c.line([(-4, -10), (-4, 0)], (240, 170, 60), 3)
        c.line([(6, -10), (6, 0)], (240, 170, 60), 3)
        c.ellipse(0, -24, 24, 15, (250, 250, 252), w=2.5)
        c.ellipse(-8, -26, 18, 9, (150, 156, 170), w=2)
        c.circle(18, -40, 10, (250, 250, 252), w=2.5)
        c.circle(21, -43, 2, OUT, ol=None)
        c.poly([(26, -40), (40, -38), (26, -34)], (245, 190, 60), w=1.5)
    c.pop()


# ============================================================== scooter & co

def wheel(c, x, y, r, ang, tyre=(40, 40, 46), hub=(210, 210, 216)):
    c.circle(x, y, r, tyre)
    c.circle(x, y, r * 0.62, (190, 190, 196), w=2)
    for k in range(5):
        a = ang + k * math.tau / 5
        c.line([(x, y), (x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6)], (120, 120, 130), 2, cap=False)
    c.circle(x, y, r * 0.22, hub, w=2)


def scooter(c, x, y, s=1.0, t=0.0, wheel_ang=0.0, rider=None, side=None, sidecar=True, lights=False, bump=0.0):
    """The yellow scooter with its round sidecar. rider(c) draws the driver sitting on the seat at (−40, −108);
    side(c) draws passengers in the sidecar (feet at about (20, −30)); the tub front is drawn after."""
    c.push(x, y + bump, s)
    # far wheels
    wheel(c, -78, -24, 24, wheel_ang)
    wheel(c, 92, -24, 24, wheel_ang)
    # scooter body
    c.poly([(-120, -40), (-118, -86), (-90, -110), (-30, -112), (0, -96), (8, -44), (60, -44), (78, -150),
            (96, -150), (104, -60), (110, -36), (-110, -30)], YELLOW, w=3)
    c.ellipse(-60, -70, 64, 40, YELLOW, ol=None)
    c.arc(-60, -70, 64, 40, 190, 300, YELLOW_D, 4)
    c.rect(-90, -122, -10, -108, (120, 70, 50), w=2.5, r=6)          # seat
    c.line([(76, -150), (60, -182)], (90, 90, 100), 6)               # steering
    c.line([(44, -186), (84, -178)], (60, 60, 70), 7)                # handlebar
    c.circle(92, -166, 11, (255, 250, 200) if not lights else (255, 240, 150), w=2.5)
    if lights:
        c.poly([(100, -166), (240, -200), (240, -130)], (255, 240, 160), ol=None)
    c.rect(-128, -76, -116, -60, (220, 60, 50), w=2)                 # rear light
    if rider:
        rider(c)
    if sidecar:
        # sidecar arm and wheel (nearer the viewer, a little lower)
        c.push(10, 10, 1.0)
        if side:
            side(c)
        # tub
        tub = [(-110, -40), (-108, -78), (-60, -92), (40, -92), (110, -70), (140, -48), (120, -20), (-100, -16)]
        c.poly(tub, YELLOW, w=3)
        c.line([(-100, -78), (100, -76)], YELLOW_D, 4, cap=False)
        c.poly([(70, -88), (96, -128), (110, -124), (100, -80)], (200, 230, 245), w=2)   # windscreen
        c.line([(-90, -50), (110, -48)], (255, 236, 150), 3, cap=False)
        wheel(c, 20, -12, 22, wheel_ang)
        c.pop()
    c.pop()


def tram(c, x, y, s=1.0, t=0.0, inside=None, wheel_ang=0.0, lit=False, number="28", face=1, pole=True):
    """Lisbon's little yellow tram (remodelado). Origin: rail level at the middle.
    inside(c) draws passengers between the back wall and the window pillars (seat level y=-70)."""
    c.push(x, y, s, flip=face < 0)
    L = 190
    if pole:
        c.line([(-40, -262), (60, -330)], (60, 60, 70), 4)
        c.circle(60, -330, 5, (60, 60, 70), ol=None)
    # wheels / bogie
    c.rect(-150, -34, 150, -16, (60, 60, 66), w=2)
    for wx in (-100, 100):
        wheel(c, wx, -18, 18, wheel_ang, tyre=(50, 50, 56), hub=(150, 150, 160))
    # back wall + interior
    c.rect(-L, -250, L, -36, YELLOW, w=3, r=10)
    inner = (255, 236, 170) if lit else (120, 110, 100)
    for k in range(6):
        wx = -L + 34 + k * 56
        c.rect(wx, -196, wx + 46, -120, inner, ol=None)
    if inside:
        inside(c)
    # front: lower panel, pillars, roof
    c.rect(-L, -122, L, -36, YELLOW, w=3, r=6)
    c.line([(-L + 4, -112), (L - 4, -112)], YELLOW_D, 3, cap=False)
    c.rect(-L + 6, -70, L - 6, -60, CREAM, ol=None)
    for k in range(7):
        wx = -L + 34 + k * 56 - 10
        c.rect(wx, -200, wx + 10, -118, YELLOW, ol=None)
    c.rect(-L, -206, L, -196, CREAM, ol=None)
    c.line([(-L, -200), (L, -200)], OUT, 2, cap=False)
    for k in range(6):
        wx = -L + 34 + k * 56
        c.rect(wx, -196, wx + 46, -120, None, ol=OUT, w=2)
    c.rect(-L, -260, L, -206, CREAM, w=3, r=12)
    c.rect(-L + 30, -278, L - 30, -256, (180, 180, 186), w=2.5, r=8)   # roof
    # destination box + number
    c.rect(L - 70, -252, L - 8, -214, (30, 30, 36), w=2, r=3)
    c.text(L - 39, -233, number, 24, (255, 220, 90))
    c.rect(-L + 8, -252, -L + 120, -214, (30, 30, 36), w=2, r=3)
    c.text(-L + 64, -233, "Graça", 18, (255, 240, 200))
    # headlight + bumper
    c.circle(L - 8, -84, 9, (255, 250, 210), w=2)
    c.rect(-L - 6, -46, L + 6, -36, (60, 60, 66), w=2, r=3)
    c.text(0, -88, "CARRIS", 16, (90, 70, 20))
    c.pop()


def grill(c, x, y, s=1.0, t=0.0, n=5, smoke=True, glow=1.0, cooked=1.0, taken=0):
    c.push(x, y, s)
    for lx in (-50, 50):
        c.line([(lx, -60), (lx * 1.1, 0)], (60, 60, 66), 5)
    c.rect(-70, -96, 70, -60, (80, 80, 88), w=3, r=4)
    c.rect(-64, -96, 64, -82, mix((255, 120, 40), (90, 40, 30), 1 - glow), ol=None)
    for k in range(9):
        c.circle(-56 + k * 14, -92, 5, mix((255, 200, 80), (120, 60, 40), 1 - glow) if k % 2 else
                 mix((255, 150, 50), (100, 50, 36), 1 - glow), ol=None)
    for k in range(7):
        c.line([(-66 + k * 22, -100), (-66 + k * 22, -96)], (40, 40, 46), 2)
    c.line([(-70, -100), (70, -100)], (40, 40, 46), 3)
    for k in range(taken, n):
        sardine(c, -48 + k * (96 / max(1, n - 1)), -106, 0.55, ang=-0.4 + 0.2 * (k % 2), cooked=cooked)
    if smoke:
        for k in range(5):
            u = ((t * 0.4) + k / 5) % 1.0
            sx = -30 + k * 15 + math.sin(t * 2 + k) * 12 * u
            c.circle(sx, -120 - 160 * u, 10 + 22 * u, mix((236, 236, 240), (200, 200, 210), u), ol=None)
    c.pop()


def sardine(c, x, y, s=1.0, ang=0.0, cooked=1.0, bite=0.0):
    body = mix(SARDINE, (180, 150, 110), 0.35 * cooked)
    back = mix(SARDINE_D, (90, 70, 60), 0.4 * cooked)
    c.push(x, y, s)
    def P(px, py):
        return R(ang, px, py)
    pts = [P(-50, 0), P(-26, -11), P(20, -12), P(46, -2), P(20, 10), P(-26, 9)]
    c.poly(pts, body, w=2.5)
    c.line([P(-36, -5), P(-10, -9), P(30, -8)], back, 5)
    c.poly([P(-48, 0), P(-68, -14), P(-62, 0), P(-68, 14)], body, w=2.5)
    ex, ey = P(32, -3)
    c.circle(ex, ey, 3, OUT, ol=None)
    if cooked > 0.3:
        for k in range(3):
            a, b = P(-24 + k * 18, -8), P(-30 + k * 18, 8)
            c.line([a, b], (90, 60, 40), 2.5, cap=False)
    if bite > 0:
        bx, by = P(46 - 30 * bite, -2)
        c.circle(bx + 10, by, 14 * bite + 4, None, ol=None)
    c.pop()


def plate(c, x, y, s=1.0, n=3, eaten=0):
    c.push(x, y, s)
    c.ellipse(0, 0, 70, 14, (250, 250, 252), w=2.5)
    c.ellipse(0, -1, 52, 9, (230, 236, 244), ol=None)
    c.arc(0, 0, 62, 11, 0, 180, TILE_BLUE, 2)
    for k in range(eaten, n):
        sardine(c, -26 + k * 26, -10 - k * 4, 0.5, ang=-0.15)
    # bread slice
    c.pop()


def nata(c, x, y, s=1.0, bite=0.0):
    c.push(x, y, s)
    c.poly([(-26, -14), (26, -14), (20, 4), (-20, 4)], (214, 160, 86), w=2.5)
    for k in range(6):
        c.line([(-20 + k * 8, -12), (-17 + k * 7, 2)], (180, 120, 60), 1.5, cap=False)
    c.ellipse(0, -14, 27, 9, (214, 160, 86), w=2.5)
    c.ellipse(0, -15, 22, 7, (255, 214, 90), ol=None)
    for dx, dy, r in ((-8, -16, 4), (6, -14, 3), (12, -17, 2.5), (-2, -12, 2)):
        c.ellipse(dx, dy, r * 1.3, r * 0.7, (130, 70, 30), ol=None)
    if bite > 0:
        c.circle(24, -12, 10 * bite, (250, 236, 210), ol=None)
    c.pop()


def guitar(c, x, y, s=1.0, ang=0.0, t=0.0, strum=0.0):
    """Portuguese guitar: pear-shaped body, round soundhole, fan of tuning screws. Origin at body centre."""
    c.push(x, y, s)
    def P(px, py):
        return R(ang, px, py)
    body = [P(math.cos(a) * 44 - 10, math.sin(a) * 40) for a in np.linspace(0, math.tau, 30)]
    c.poly(body, (210, 150, 80), w=2.5)
    c.poly([P(math.cos(a) * 34 + 20, math.sin(a) * 30) for a in np.linspace(0, math.tau, 24)],
           (210, 150, 80), ol=None)
    hx, hy = P(-6, 0)
    c.circle(hx, hy, 10, (60, 40, 30), w=2)
    c.circle(hx, hy, 14, None, ol=(150, 100, 40), w=2)
    a1, a2 = P(30, -6), P(110, -5)
    b1, b2 = P(30, 6), P(110, 5)
    c.poly([a1, a2, b2, b1], (110, 70, 40), w=2)
    # fan head
    fan = [P(110, -8), P(150, -22), P(156, 0), P(150, 22), P(110, 8)]
    c.poly(fan, (200, 180, 120), w=2)
    for k in range(6):
        p0 = P(116, -6 + k * 2.4)
        p1 = P(150, -18 + k * 7.2)
        c.line([p0, p1], (160, 140, 90), 1.5, cap=False)
    for k in range(4):
        sp = P(-30, -6 + k * 4)
        ep = P(110, -4 + k * 2.7)
        vib = math.sin(t * 60 + k) * strum
        c.line([sp, (ep[0], ep[1] + vib)], (250, 250, 240), 1, cap=False)
    c.pop()


def music_notes(c, x, y, t, t0, n=4, col=(255, 240, 200), s=1.0, rise=140):
    if t < t0:
        return
    for k in range(n):
        u = ((t - t0) * 0.45 + k / n) % 1.0
        nx = x + 40 * math.sin(k * 2.3 + t * 1.5) * u + (k - n / 2) * 18
        ny = y - rise * u
        a = 1 - u
        cc = mix((255, 255, 255), col, a)
        c.push(nx, ny, s * (0.7 + 0.5 * a))
        c.ellipse(0, 0, 7, 5.5, cc, w=2)
        c.line([(6, 0), (6, -24)], cc, 3)
        if k % 2:
            c.line([(6, -24), (16, -16)], cc, 3)
        c.pop()


# ================================================================= landmarks

def battlements(c, x0, x1, y, h=14, w=16, gap=10, col=LIMESTONE):
    xx = x0
    while xx + w <= x1 + 0.1:
        c.rect(xx, y - h, xx + w, y + 2, col, w=2)
        xx += w + gap


def belem_tower(c, x, y, s=1.0):
    """Torre de Belem: the bastion, the tall tower, little domed watch-turrets."""
    c.push(x, y, s)
    st, sd = LIMESTONE, LIMESTONE_D
    # bastion (wide, low, on the water)
    c.rect(-150, -120, 160, 0, st, w=3)
    c.rect(-150, -16, 160, 0, sd, w=2)
    for k in range(6):
        c.rect(-130 + k * 50, -96, -116 + k * 50, -70, (90, 80, 70), w=2, r=6)
    # shield battlements with crosses
    xx = -148
    while xx < 150:
        c.poly([(xx, -120), (xx, -140), (xx + 18, -140), (xx + 18, -120)], st, w=2)
        c.arc(xx + 9, -140, 9, 6, 180, 360, OUT, 2)
        c.line([(xx + 9, -136), (xx + 9, -126)], (180, 60, 50), 2, cap=False)
        c.line([(xx + 5, -131), (xx + 13, -131)], (180, 60, 50), 2, cap=False)
        xx += 26
    for tx in (-160, 168):
        _turret(c, tx, -120, 0.8)
    # the tower
    c.rect(-70, -400, 70, -120, st, w=3)
    c.rect(-80, -300, 80, -284, sd, w=2.5)                       # balcony
    for k in range(5):
        c.arc(-56 + k * 28, -284, 12, 10, 0, 180, OUT, 2)
    for wy in (-250, -190):
        c.rect(-20, wy, 20, wy + 44, (80, 70, 64), w=2.5, r=18)
    c.rect(-28, -360, 28, -320, (80, 70, 64), w=2.5, r=14)
    c.circle(0, -230, 4, (180, 60, 50), ol=None)
    # top terrace + battlements
    c.rect(-76, -412, 76, -400, sd, w=2.5)
    battlements(c, -76, 76, -412, 14, 14, 9, st)
    for tx in (-74, 74):
        _turret(c, tx, -400, 0.7)
    c.rect(-30, -470, 30, -412, st, w=2.5)
    battlements(c, -30, 30, -470, 12, 10, 6, st)
    c.pop()


def _turret(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-16, -56, 16, 0, LIMESTONE, w=2.5)
    c.rect(-6, -46, 6, -24, (90, 80, 70), w=1.5, r=4)
    c.ellipse(0, -58, 20, 8, LIMESTONE_D, w=2)
    c.poly([(-18, -60), (-12, -80), (0, -92), (12, -80), (18, -60)], LIMESTONE, w=2.5)
    for k in range(3):
        c.arc(0, -64 - k * 8, 14 - k * 4, 4, 0, 180, LIMESTONE_D, 1.5)
    c.circle(0, -96, 4, LIMESTONE, w=1.5)
    c.pop()


def discoveries(c, x, y, s=1.0):
    """Padrao dos Descobrimentos: a stone caravel prow with explorers climbing toward the river."""
    c.push(x, y, s)
    st, sd = (240, 234, 216), (206, 196, 174)
    # base platform
    c.rect(-260, -20, 220, 0, sd, w=2.5)
    # the tall slab with the sword-cross
    c.poly([(-60, -20), (-50, -330), (10, -330), (20, -20)], st, w=3)
    c.line([(-20, -300), (-20, -60)], sd, 6, cap=False)
    c.line([(-40, -250), (0, -250)], sd, 6, cap=False)
    # ramps (two sides of the prow) with figures
    c.poly([(-260, -20), (-60, -140), (-40, -120), (-40, -20)], st, w=3)
    c.poly([(0, -20), (0, -120), (20, -140), (210, -40), (220, -20)], st, w=3)
    for k in range(7):
        u = k / 6
        fx, fy = lerp(30, 190, u), lerp(-128, -46, u)
        c.ellipse(fx, fy - 10, 8, 14, sd, w=1.5)
        c.circle(fx + 2, fy - 28, 6, sd, w=1.5)
    for k in range(6):
        u = k / 5
        fx, fy = lerp(-220, -70, u), lerp(-40, -128, u)
        c.ellipse(fx, fy - 10, 8, 14, sd, w=1.5)
        c.circle(fx - 2, fy - 28, 6, sd, w=1.5)
    # Henry the Navigator at the prow holding a little ship
    c.ellipse(-46, -148, 10, 18, sd, w=1.5)
    c.circle(-42, -172, 7, sd, w=1.5)
    # sails carved at the top
    c.poly([(-48, -330), (-44, -360), (8, -360), (12, -330)], st, w=2.5)
    c.pop()


def caravel(c, x, y, s=1.0, t=0.0, bob=True):
    """An old explorers' ship with square red-cross sails."""
    c.push(x, y + (math.sin(t * 1.6) * 3 if bob else 0), s)
    c.poly([(-120, -40), (130, -40), (100, 0), (-96, 0)], (140, 90, 50), w=3)
    c.poly([(-120, -40), (-130, -70), (-70, -70), (-70, -40)], (150, 100, 56), w=2.5)
    c.line([(-110, -26), (110, -26)], (110, 70, 40), 3, cap=False)
    for mx, h in ((-40, 170), (40, 150)):
        c.line([(mx, -40), (mx, -40 - h)], (110, 70, 40), 5)
        c.poly([(mx - 46, -40 - h + 20), (mx + 46, -40 - h + 20), (mx + 50, -60), (mx - 50, -60)], (248, 244, 230),
               w=2.5)
        cy = -40 - h / 2 - 10
        c.rect(mx - 8, cy - 30, mx + 8, cy + 30, (200, 40, 40), ol=None)
        c.rect(mx - 30, cy - 8, mx + 30, cy + 8, (200, 40, 40), ol=None)
        c.poly([(mx, -40 - h), (mx + 24, -40 - h + 8), (mx, -40 - h + 14)], (200, 40, 40), w=1.5)
    c.poly([(110, -40), (170, -80), (120, -40)], (248, 244, 230), w=2)
    c.pop()


def bridge(c, x0, x1, deck, towers, top, col=BRIDGE_RED, cold=BRIDGE_RED_D, far=False):
    """The 25 de Abril suspension bridge. towers: x positions; top: tower top y; deck: deck y."""
    w = 2 if far else 3
    # main cables (catenaries between towers, plus side spans)
    pts_all = []
    xs = [x0] + list(towers) + [x1]
    for a, b in zip(xs, xs[1:]):
        ya = top if a in towers else deck - 10
        yb = top if b in towers else deck - 10
        sag = 0.62 if (a in towers and b in towers) else 0.2
        seg = []
        for u in np.linspace(0, 1, 24):
            xx = lerp(a, b, u)
            yy = lerp(ya, yb, u) + (deck - 20 - min(ya, yb)) * sag * 4 * u * (1 - u)
            seg.append((xx, yy))
        pts_all.append(seg)
        for xx, yy in seg[1:-1:2]:
            c.line([(xx, yy), (xx, deck)], cold, 1.2 if far else 1.6, cap=False)
    for seg in pts_all:
        c.line(seg, col, 3 if far else 4)
    # deck truss
    c.rect(x0, deck - 2, x1, deck + (10 if far else 18), col, w=w)
    step = 16 if far else 24
    xx = x0
    while xx < x1:
        c.line([(xx, deck + 1), (xx + step / 2, deck + (9 if far else 16))], cold, 1.5, cap=False)
        c.line([(xx + step / 2, deck + (9 if far else 16)), (xx + step, deck + 1)], cold, 1.5, cap=False)
        xx += step
    # towers
    for tx in towers:
        tw = 10 if far else 16
        sp = 18 if far else 30
        for side in (-1, 1):
            c.rect(tx + side * sp - tw / 2, top, tx + side * sp + tw / 2, deck + 40, col, w=w)
        for yy in np.linspace(top + 20, deck - 20, 4):
            c.rect(tx - sp, yy - 4, tx + sp, yy + 4, col, w=1.5)


def cristo_rei(c, x, y, s=1.0, col=(232, 226, 210)):
    c.push(x, y, s)
    c.poly([(-26, 0), (-18, -150), (18, -150), (26, 0)], col, w=2)
    for k in range(4):
        c.line([(-22 + k * 0.5, -30 - k * 30), (22 - k * 0.5, -30 - k * 30)], mix(col, OUT, 0.2), 1.5, cap=False)
    c.rect(-24, -162, 24, -150, col, w=2)
    c.poly([(-8, -162), (-10, -210), (10, -210), (8, -162)], col, w=2)
    c.rect(-40, -206, 40, -198, col, w=2)
    c.circle(0, -218, 7, col, w=2)
    c.pop()


def cross_flag(c, x, y, s=1.0, t=0.0):
    """A small Portuguese flag on a pole (green / red with a gold sphere)."""
    c.push(x, y, s)
    c.line([(0, 0), (0, -80)], (90, 80, 70), 3)
    wv = [math.sin(t * 4 + k) * 3 for k in range(4)]
    pts = [(0, -80), (20, -80 + wv[1]), (40, -80 + wv[2]), (54, -80 + wv[3]),
           (54, -50 + wv[3]), (40, -50 + wv[2]), (20, -50 + wv[1]), (0, -50)]
    c.poly(pts, (210, 40, 40), w=2)
    c.poly([(0, -80), (20, -80 + wv[1]), (20, -50 + wv[1]), (0, -50)], (30, 120, 60), ol=None)
    c.circle(20, -65 + wv[1], 6, (250, 210, 60), w=1.5)
    c.pop()


def castle_wall(c, x0, x1, y, h, col=(210, 186, 150), cold=(176, 150, 116), towers=(), seed=0):
    rng = np.random.default_rng(seed)
    c.rect(x0, y - h, x1, y, col, w=3)
    for k in range(int((x1 - x0) / 40) * int(h / 26) // 2):
        bx, by = rng.uniform(x0 + 10, x1 - 30), rng.uniform(y - h + 14, y - 10)
        c.rect(bx, by, bx + 26, by + 12, cold, ol=None)
    battlements(c, x0, x1, y - h, 18, 22, 14, col)
    for tx, tw, th in towers:
        c.rect(tx - tw / 2, y - h - th, tx + tw / 2, y, col, w=3)
        for k in range(3):
            c.rect(tx - tw / 2 + 12, y - h - th + 30 + k * 60, tx - tw / 2 + 26, y - h - th + 44 + k * 60,
                   (90, 70, 60), ol=None)
        battlements(c, tx - tw / 2, tx + tw / 2, y - h - th, 18, 18, 12, col)


def santa_justa(c, x, y, s=1.0, cabin_y=None, inside=None, lit=False):
    """The Santa Justa lift: a tall neo-gothic iron tower with a walkway at the top.
    cabin_y: height (0..1) of the lift cabin; inside(c, cx, cy) draws riders in the cabin."""
    c.push(x, y, s)
    ir, ird = (84, 84, 98), (54, 54, 66)
    Wd, Ht = 120, 560
    c.rect(-Wd / 2, -Ht, Wd / 2, 0, ir, w=3)
    # lattice: pointed arches and crosses
    for row in range(10):
        yy = -Ht + 30 + row * 52
        for col in range(3):
            xx = -Wd / 2 + 10 + col * 34
            c.rect(xx, yy, xx + 30, yy + 46, (150, 170, 200) if not lit else (255, 220, 140), ol=None)
            c.poly([(xx, yy + 18), (xx + 15, yy), (xx + 30, yy + 18)], ir, ol=None)
            c.line([(xx, yy + 46), (xx + 30, yy + 18)], ird, 1.5, cap=False)
            c.line([(xx + 30, yy + 46), (xx, yy + 18)], ird, 1.5, cap=False)
            c.rect(xx, yy, xx + 30, yy + 46, None, ol=ird, w=2)
    if cabin_y is not None:
        cy = lerp(-30, -Ht + 90, cabin_y)
        c.rect(-44, cy - 76, 44, cy, (150, 110, 70), w=3, r=4)
        c.rect(-36, cy - 66, 36, cy - 24, (250, 236, 200), w=2)
        if inside:
            inside(c, 0, cy - 22)
        c.rect(-44, cy - 30, 44, cy, (150, 110, 70), w=2.5)
        c.line([(0, cy - 76), (0, -Ht)], (40, 40, 46), 2, cap=False)
    # crown: platform, little pointed turrets
    c.rect(-Wd / 2 - 16, -Ht - 20, Wd / 2 + 16, -Ht, ird, w=2.5)
    c.rect(-Wd / 2 + 6, -Ht - 90, Wd / 2 - 6, -Ht - 20, ir, w=2.5)
    for k in range(4):
        c.rect(-Wd / 2 + 16 + k * 24, -Ht - 78, -Wd / 2 + 32 + k * 24, -Ht - 34, (150, 170, 200), w=1.5, r=6)
    c.rect(-Wd / 2 - 16, -Ht - 104, Wd / 2 + 16, -Ht - 90, ird, w=2.5)
    for k in range(9):
        c.line([(-Wd / 2 - 12 + k * 18, -Ht - 104), (-Wd / 2 - 12 + k * 18, -Ht - 122)], ird, 2, cap=False)
    c.line([(-Wd / 2 - 16, -Ht - 122), (Wd / 2 + 16, -Ht - 122)], ird, 3, cap=False)
    for sx in (-1, 1):
        c.poly([(sx * Wd / 2 - 6, -Ht - 90), (sx * Wd / 2, -Ht - 130), (sx * Wd / 2 + 6, -Ht - 90)], ir, w=2)
    # the walkway to the hill on the right
    c.rect(Wd / 2 + 16, -Ht - 20, Wd / 2 + 260, -Ht, ird, w=2.5)
    for k in range(10):
        c.line([(Wd / 2 + 20 + k * 24, -Ht), (Wd / 2 + 32 + k * 24, -Ht - 18)], ir, 2, cap=False)
    c.pop()


# ================================================================ buildings

def tile_pattern(c, x0, y0, x1, y1, base=TILE_WHITE, ink=TILE_BLUE, size=22, style=0):
    """Azulejos: a wall of blue-and-white painted tiles."""
    c.rect(x0, y0, x1, y1, base, ol=None)
    ny = int((y1 - y0) // size) + 1
    nx = int((x1 - x0) // size) + 1
    for j in range(ny):
        for i in range(nx):
            cx, cy = x0 + (i + 0.5) * size, y0 + (j + 0.5) * size
            if cx > x1 or cy > y1:
                continue
            r = size * 0.32
            if style == 0:
                c.poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], ink, ol=None)
                c.circle(cx, cy, r * 0.35, base, ol=None)
            elif style == 1:
                c.circle(cx, cy, r * 0.9, ink, ol=None)
                c.circle(cx, cy, r * 0.5, base, ol=None)
                c.circle(cx - size / 2, cy - size / 2, r * 0.4, ink, ol=None)
            else:
                for a in range(4):
                    ang = a * math.pi / 2 + math.pi / 4
                    c.ellipse(cx + math.cos(ang) * r * 0.6, cy + math.sin(ang) * r * 0.6, r * 0.38, r * 0.38, ink,
                              ol=None)
    for j in range(ny + 1):
        yy = y0 + j * size
        if yy <= y1:
            c.line([(x0, yy), (x1, yy)], mix(base, ink, 0.25), 1, cap=False)
    for i in range(nx + 1):
        xx = x0 + i * size
        if xx <= x1:
            c.line([(xx, y0), (xx, y1)], mix(base, ink, 0.25), 1, cap=False)


def window(c, x, y, w=40, h=64, shutter=(60, 130, 90), frame=(250, 250, 245), balcony=True, lit=False,
           glass=(70, 90, 120)):
    c.rect(x - w / 2 - 5, y - h - 5, x + w / 2 + 5, y + 4, frame, w=2)
    c.rect(x - w / 2, y - h, x + w / 2, y, (255, 214, 130) if lit else glass, w=2)
    c.line([(x, y - h), (x, y)], frame, 2.5, cap=False)
    if shutter:
        for sx in (-1, 1):
            c.rect(x + sx * (w / 2 + 3) - (14 if sx > 0 else 0) + (0 if sx > 0 else -14) + (14 if sx < 0 else 0)
                   - (0 if sx < 0 else 0),
                   y - h, x + sx * (w / 2 + 3) + (14 if sx > 0 else 0) - (14 if sx < 0 else 0) + (14 if sx < 0 else 0),
                   y, shutter, w=2) if False else None
    if balcony:
        c.rect(x - w / 2 - 12, y - 4, x + w / 2 + 12, y + 4, (80, 80, 90), w=1.5)
        c.line([(x - w / 2 - 10, y - 26), (x + w / 2 + 10, y - 26)], (50, 50, 60), 2.5, cap=False)
        for k in range(7):
            xx = x - w / 2 - 8 + k * (w + 16) / 6
            c.line([(xx, y - 26), (xx, y - 4)], (50, 50, 60), 1.5, cap=False)


def house(c, x, base, w, h, wall, roof=TERRACOTTA, tiles=None, floors=None, lit=False, door=True, seed=0,
          shutter=None):
    """A narrow Lisbon town house. tiles: (ink, style) to cover the facade with azulejos."""
    rng = np.random.default_rng(seed)
    top = base - h
    if tiles:
        c.rect(x, top, x + w, base, wall, w=3)
        tile_pattern(c, x + 2, top + 2, x + w - 2, base - 2, base=TILE_WHITE if tiles[0] != "white" else wall,
                     ink=tiles[0] if tiles[0] != "white" else TILE_BLUE, size=tiles[2] if len(tiles) > 2 else 18,
                     style=tiles[1])
        c.rect(x, top, x + w, base, None, ol=OUT, w=3)
    else:
        c.rect(x, top, x + w, base, wall, w=3)
    c.rect(x - 4, top - 8, x + w + 4, top + 4, (250, 248, 240), w=2)
    c.poly([(x - 8, top - 6), (x + 8, top - 30), (x + w - 8, top - 30), (x + w + 8, top - 6)], roof, w=2.5)
    for k in range(int(w / 14)):
        c.line([(x + 6 + k * 14, top - 28), (x + 2 + k * 14, top - 8)], TERRACOTTA_D, 1.5, cap=False)
    floors = floors or max(1, int((h - 70) / 90))
    nwin = max(1, int(w / 70))
    for f in range(floors):
        wy = top + 100 + f * 90
        if wy > base - 40:
            break
        for k in range(nwin):
            wx = x + (k + 0.5) * w / nwin
            window(c, wx, wy, 34, 56, balcony=rng.random() < 0.6, lit=lit and rng.random() < 0.7,
                   frame=(250, 250, 245))
    if door:
        dx = x + w * rng.uniform(0.3, 0.7)
        c.rect(dx - 18, base - 64, dx + 18, base, (110, 70, 50), w=2.5, r=4)
        c.arc(dx, base - 64, 18, 12, 180, 360, OUT, 2)


def roofs(c, x0, x1, y0, y1, seed=0, density=1.0, walls=((250, 246, 236), (246, 226, 180), (240, 200, 170),
                                                        (220, 230, 236), (250, 222, 140)), scale=1.0, tint=None):
    """A hillside of little white and pastel houses with red roofs (for views from above)."""
    rng = np.random.default_rng(seed)
    rows = int((y1 - y0) / (22 * scale)) + 1
    for j in range(rows):
        yy = y0 + j * 22 * scale
        xx = x0 - rng.uniform(0, 40) * scale
        while xx < x1:
            w = rng.uniform(34, 70) * scale
            h = rng.uniform(26, 44) * scale
            wall = walls[rng.integers(len(walls))]
            roof = mix(TERRACOTTA, (230, 130, 90), rng.uniform(0, 0.5))
            c.rect(xx, yy - h, xx + w, yy + 12 * scale, wall, w=1.5)
            if rng.random() < 0.7:
                c.poly([(xx - 3, yy - h), (xx + w * 0.5, yy - h - 14 * scale), (xx + w + 3, yy - h)], roof, w=1.5)
            else:
                c.poly([(xx - 3, yy - h), (xx + 6, yy - h - 12 * scale), (xx + w - 6, yy - h - 12 * scale),
                        (xx + w + 3, yy - h)], roof, w=1.5)
            for k in range(int(w / (18 * scale))):
                wx = xx + 6 * scale + k * 18 * scale
                c.rect(wx, yy - h + 8 * scale, wx + 7 * scale, yy - h + 18 * scale, (80, 90, 110), ol=None)
            xx += w + rng.uniform(-6, 4) * scale


def laundry(c, x0, y0, x1, y1, t=0.0, seed=0, n=5):
    rng = np.random.default_rng(seed)
    pts = []
    for u in np.linspace(0, 1, 12):
        pts.append((lerp(x0, x1, u), lerp(y0, y1, u) + 18 * 4 * u * (1 - u)))
    c.line(pts, (90, 90, 100), 1.5, cap=False)
    cols = [(240, 80, 80), (255, 255, 255), (90, 160, 230), (250, 210, 70), (140, 210, 140), (240, 150, 200)]
    for k in range(n):
        u = (k + 0.7) / (n + 0.4)
        px = lerp(x0, x1, u)
        py = lerp(y0, y1, u) + 18 * 4 * u * (1 - u)
        col = cols[rng.integers(len(cols))]
        sw = math.sin(t * 2.2 + k * 1.3 + seed) * 4
        kind = rng.integers(3)
        if kind == 0:     # shirt
            c.poly([(px - 14, py), (px + 14, py), (px + 12 + sw, py + 34), (px - 12 + sw, py + 34)], col, w=1.5)
            c.poly([(px - 14, py), (px - 22 + sw * 0.5, py + 12), (px - 12, py + 14)], col, w=1.5)
            c.poly([(px + 14, py), (px + 22 + sw * 0.5, py + 12), (px + 12, py + 14)], col, w=1.5)
        elif kind == 1:   # sock pair
            for dx in (-6, 6):
                c.poly([(px + dx - 4, py), (px + dx + 4, py), (px + dx + 4 + sw, py + 20), (px + dx + 10 + sw, py + 24),
                        (px + dx - 2 + sw, py + 26)], col, w=1.5)
        else:             # towel
            c.rect(px - 16, py, px + 16, py + 30, col, w=1.5)
            c.line([(px - 14 + sw * 0.3, py + 24), (px + 14 + sw * 0.3, py + 24)], mix(col, (255, 255, 255), 0.5), 2,
                   cap=False)
        c.line([(px - 8, py - 3), (px - 8, py + 3)], (160, 110, 70), 2, cap=False)


def garland(c, x0, y0, x1, y1, t=0.0, sag=40, lanterns=True, seed=0, glow=False):
    """String of paper lanterns and little paper flags across a street."""
    rng = np.random.default_rng(seed)
    pts = [(lerp(x0, x1, u), lerp(y0, y1, u) + sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 20)]
    c.line(pts, (70, 60, 60), 1.5, cap=False)
    cols = [(240, 70, 70), (250, 200, 60), (80, 170, 230), (130, 210, 120), (240, 130, 200), (250, 140, 60)]
    n = int(abs(x1 - x0) / 28)
    for k in range(n):
        u = (k + 0.5) / n
        px = lerp(x0, x1, u)
        py = lerp(y0, y1, u) + sag * 4 * u * (1 - u)
        col = cols[(k + seed) % len(cols)]
        sw = math.sin(t * 2 + k) * 2
        if lanterns and k % 3 == 1:
            if glow:
                c.circle(px + sw, py + 20, 20, mix(col, (255, 240, 200), 0.3), ol=None)
            c.ellipse(px + sw, py + 18, 10, 13, col, w=1.5)
            c.line([(px + sw - 6, py + 10), (px + sw + 6, py + 10)], mix(col, OUT, 0.4), 1, cap=False)
            c.line([(px + sw - 6, py + 26), (px + sw + 6, py + 26)], mix(col, OUT, 0.4), 1, cap=False)
        else:
            c.poly([(px - 8, py), (px + 8, py), (px + sw * 0.5, py + 18)], col, w=1)


def firework(c, x, y, t, t0, col, r=90, dur=1.6):
    if t < t0 or t > t0 + dur + 0.6:
        return
    u = (t - t0)
    if u < 0.6:
        k = u / 0.6
        c.circle(x, lerp(y + 300, y, ease(k)), 3, (255, 240, 200), ol=None)
        return
    k = clamp((u - 0.6) / dur)
    rr = r * ease(min(1, k * 1.6))
    fade = 1 - k
    for j in range(14):
        a = j * math.tau / 14
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr + 30 * k * k
        cc = mix((40, 30, 70), col, fade)
        c.line([(x + math.cos(a) * rr * 0.6, y + math.sin(a) * rr * 0.6 + 30 * k * k), (px, py)], cc, 3, cap=False)
        c.circle(px, py, 4 * fade + 1, mix((40, 30, 70), (255, 255, 230), fade), ol=None)


def gift_tile(c, x, y, s=1.0):
    """Avo's present: a square azulejo with two cats painted in blue."""
    c.push(x, y, s)
    c.rect(-50, -50, 50, 50, TILE_WHITE, w=3, r=3)
    c.rect(-44, -44, 44, 44, None, ol=TILE_BLUE, w=2)
    for cx, cy in ((-44, -44), (44, -44), (-44, 44), (44, 44)):
        c.circle(cx, cy, 6, TILE_BLUE, ol=None)
    for dx, flip in ((-14, 1), (16, -1)):
        c.push(dx, 30, 0.32, flip=flip < 0)
        c.ellipse(-6, -26, 30, 24, TILE_BLUE, ol=None)
        c.ellipse(6, -56, 26, 36, TILE_BLUE, ol=None)
        c.ellipse(18, -100, 28, 25, TILE_BLUE, ol=None)
        c.poly([(-4, -110), (0, -140), (14, -118)], TILE_BLUE, ol=None)
        c.poly([(24, -120), (40, -140), (42, -108)], TILE_BLUE, ol=None)
        c.stroke([(-30, -12), (-50, -40), (-44, -70)], TILE_BLUE, 10, ol=None)
        c.pop()
    # heart between them
    c.circle(-3, -26, 4, (60, 120, 200), ol=None)
    c.circle(3, -26, 4, (60, 120, 200), ol=None)
    c.poly([(-7, -24), (7, -24), (0, -16)], (60, 120, 200), ol=None)
    c.pop()


def cork_tree(c, x, y, s=1.0, leaf=(96, 140, 70), trunk=(150, 90, 60)):
    c.push(x, y, s)
    c.poly([(-10, 0), (-8, -60), (-40, -100), (-30, -104), (0, -76), (26, -110), (36, -104), (10, -60), (12, 0)],
           trunk, w=2.5)
    c.rect(-9, -40, 11, 0, (200, 110, 70), ol=None)        # stripped cork, reddish
    for dx, dy, r in ((-50, -110, 34), (0, -130, 44), (50, -110, 34), (-20, -100, 30), (24, -100, 30)):
        c.circle(dx, dy, r, leaf)
    for dx, dy, r in ((-50, -110, 29), (0, -130, 39), (50, -110, 29), (-20, -100, 25), (24, -100, 25)):
        c.circle(dx, dy, r, leaf, ol=None)
    c.pop()


def windmill(c, x, y, s=1.0, t=0.0):
    c.push(x, y, s)
    c.poly([(-26, 0), (-20, -90), (20, -90), (26, 0)], (250, 248, 240), w=2.5)
    c.poly([(-24, -88), (0, -116), (24, -88)], (90, 80, 70), w=2.5)
    c.rect(-8, -30, 8, 0, (120, 80, 50), w=2)
    ang = t * 1.5
    for k in range(4):
        a = ang + k * math.pi / 2
        tip = (math.cos(a) * 70, -96 + math.sin(a) * 70)
        c.line([(0, -96), tip], (110, 80, 50), 3)
        side = (math.cos(a + 0.25) * 64, -96 + math.sin(a + 0.25) * 64)
        mid = (math.cos(a + 0.4) * 22, -96 + math.sin(a + 0.4) * 22)
        c.poly([(math.cos(a) * 20, -96 + math.sin(a) * 20), tip, side, mid], (250, 250, 250), w=1.5)
    c.circle(0, -96, 5, (110, 80, 50), w=1.5)
    c.pop()


def heart(c, x, y, r, col):
    c.circle(x - r * 0.5, y, r * 0.6, col, ol=None)
    c.circle(x + r * 0.5, y, r * 0.6, col, ol=None)
    c.poly([(x - r * 1.05, y + r * 0.15), (x + r * 1.05, y + r * 0.15), (x, y + r * 1.2)], col, ol=None)


def hearts(c, x, y, t, t0, n=4, col=(240, 80, 110)):
    if t < t0:
        return
    for k in range(n):
        u = ((t - t0) * 0.5 + k / n) % 1.0
        hx = x + 30 * math.sin(k * 2.1 + t * 2) * u + (k - n / 2) * 14
        hy = y - 120 * u
        heart(c, hx, hy, 7 * (1 - u * 0.5), mix(col, (255, 255, 255), u * 0.6))


def cinnamon_cloud(c, x, y, k, t):
    if k <= 0:
        return
    rng = np.random.default_rng(4)
    for j in range(16):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(10, 90) * ease(min(1, k * 2))
        r = rng.uniform(14, 30) * (1 - 0.5 * k)
        c.circle(x + math.cos(a) * d * 1.4, y + math.sin(a) * d * 0.7 - 20 * k, r,
                 mix((176, 110, 60), (220, 180, 140), k), ol=None)
