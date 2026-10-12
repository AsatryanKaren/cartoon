"""Barcelona props and characters, drawn in the flat cartoon style of draw.py.

Coordinates are output pixels; characters use draw.py's local space (origin
between the feet, facing right, y up is negative).
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import W, H, SS, OUT, mix, lerp

# ------------------------------------------------------------------ palettes

PACO = dict(body=(62, 60, 72), dark=(40, 38, 48), belly=(248, 246, 240), ear=(232, 150, 160),
            eye=(236, 196, 60), stripes=False, collar=None)
GOLD = dict(body=(222, 178, 64), dark=(186, 140, 40), belly=(246, 214, 120), ear=(236, 190, 90),
            eye=(170, 120, 30), stripes=False, collar=None)
SAND = (240, 214, 160)
STONE = (226, 200, 160)
STONE_D = (194, 162, 122)
TILE_COLS = [(46, 120, 196), (60, 170, 120), (250, 200, 60), (236, 120, 50), (220, 70, 70), (250, 246, 236),
             (120, 200, 220), (150, 90, 170)]
LIZARD_COLS = [(70, 170, 90), (110, 196, 80), (40, 130, 170), (250, 206, 60), (236, 128, 44), (60, 150, 210),
               (180, 220, 90)]
BOWL_BLUE = (52, 104, 196)


def tinted(pal, col, k):
    """A palette mixed toward a colour (seasick green, spicy red, ...)."""
    if k <= 0:
        return pal
    return dict(pal, body=mix(pal["body"], col, k), dark=mix(pal["dark"], col, k * 0.9),
                belly=mix(pal["belly"], col, k * 0.6), ear=mix(pal["ear"], col, k * 0.5))


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
    bob = math.sin(walk * 2) * 2 if walk else 0
    return 52, -86 + bob + head_dy


def rot(pts, ang, cx=0.0, cy=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


# ------------------------------------------------------------------ mosaic

_mosaic_cache = {}


def mosaic_img(w, h, cols, cell=12, seed=0, grout=(250, 244, 228)):
    """Broken-tile (trencadis) texture, supersampled, w x h output pixels."""
    key = (int(w), int(h), tuple(cols), cell, seed, grout)
    if key in _mosaic_cache:
        return _mosaic_cache[key]
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (max(1, int(w * SS)), max(1, int(h * SS))), grout)
    d = ImageDraw.Draw(img)
    nx, ny = int(w // cell) + 2, int(h // cell) + 2
    gx = (np.arange(nx + 1)[None, :] * cell + rng.uniform(-0.35, 0.35, (ny + 1, nx + 1)) * cell) * SS
    gy = (np.arange(ny + 1)[:, None] * cell + rng.uniform(-0.35, 0.35, (ny + 1, nx + 1)) * cell) * SS
    gw = max(1, int(1.3 * SS))
    for j in range(ny):
        for i in range(nx):
            q = [(gx[j, i], gy[j, i]), (gx[j, i + 1], gy[j, i + 1]), (gx[j + 1, i + 1], gy[j + 1, i + 1]),
                 (gx[j + 1, i], gy[j + 1, i])]
            if rng.random() < 0.45:
                a = cols[rng.integers(len(cols))]
                b = cols[rng.integers(len(cols))]
                d.polygon([q[0], q[1], q[2]], fill=a, outline=grout, width=gw)
                d.polygon([q[0], q[2], q[3]], fill=b, outline=grout, width=gw)
            else:
                d.polygon(q, fill=cols[rng.integers(len(cols))], outline=grout, width=gw)
    _mosaic_cache[key] = img
    return img


def mosaic(c, kind, args, cols, seed=0, cell=12, ol=OUT, w=3, grout=(250, 244, 228)):
    """Fill a polygon ('poly', pts) or ellipse ('ellipse', (cx, cy, rx, ry)) with broken tiles."""
    if kind == "poly":
        P = [c.P(x, y) for x, y in args]
    else:
        cx, cy, rx, ry = args
        box = c._box(cx, cy, rx, ry)
        P = [(box[0], box[1]), (box[2], box[3])]
    xs, ys = [p[0] for p in P], [p[1] for p in P]
    x0, y0 = int(math.floor(min(xs))), int(math.floor(min(ys)))
    x1, y1 = int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    bw, bh = x1 - x0, y1 - y0
    if bw < 2 or bh < 2:
        return
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    if kind == "poly":
        md.polygon([(x - x0, y - y0) for x, y in P], fill=255)
    else:
        md.ellipse([0, 0, bw - 1, bh - 1], fill=255)
    tex = mosaic_img(bw / SS + 1, bh / SS + 1, cols, cell, seed, grout).crop((0, 0, bw, bh))
    c.img.paste(tex, (x0, y0), mask)
    if ol:
        if kind == "poly":
            c.poly(args, None, ol=ol, w=w)
        else:
            c.ellipse(*args, None, ol=ol, w=w)


# ------------------------------------------------------------------ marina

GULL_W = (250, 250, 252)
GULL_G = (176, 186, 200)
GULL_D = (60, 64, 74)
BEAK = (250, 200, 50)
FEET = (246, 150, 70)


def marina(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, fly=False, flap=None, eyes="open", walk=0.0, seed=5.5,
           flower=True, wave=0.0):
    """Marina the seagull. fly: wings out and flapping. flap: wing phase override."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    if fly:
        ph = t * 9 if flap is None else flap
        up = math.sin(ph)
        # far wing
        c.poly([(-4, -46), (-30, -46 - 70 * up), (-56, -40 - 86 * up), (-20, -38)], mix(GULL_G, OUT, 0.25), w=2.5)
        c.poly([(-30, -46 - 70 * up), (-56, -40 - 86 * up), (-40, -44 - 64 * up)], GULL_D, ol=None)
        body_y = -44
    else:
        body_y = -40
        for fx, ph in ((-8, 0), (8, math.pi)):
            lift = -max(0.0, math.cos(walk + ph)) * 6 if walk else 0
            c.line([(fx * 0.6, body_y + 14), (fx, lift - 2)], FEET, 3.5)
            c.poly([(fx - 7, lift), (fx + 9, lift), (fx + 2, lift - 6)], FEET, w=1.5)
    # tail
    c.poly([(-30, body_y - 6), (-62, body_y - 14), (-60, body_y + 4), (-28, body_y + 8)], GULL_W, w=2.5)
    c.poly([(-50, body_y - 12), (-62, body_y - 14), (-60, body_y + 4), (-50, body_y + 2)], GULL_D, ol=None)
    # body
    c.ellipse(0, body_y, 38, 24, GULL_W, w=3)
    # head
    hx, hy = (34, body_y - 14) if fly else (26, body_y - 30)
    if not fly:
        c.poly([(10, body_y - 14), (hx - 12, hy + 4), (hx + 6, hy + 10), (24, body_y - 6)], GULL_W, ol=None)
    c.circle(hx, hy, 18, GULL_W, w=3)
    if not fly:
        c.poly([(10, body_y - 14), (hx - 10, hy + 8), (hx + 6, hy + 12), (24, body_y - 4)], GULL_W, ol=None)
    # near wing
    if fly:
        c.poly([(8, -48), (-16, -50 - 80 * up), (-40, -44 - 98 * up), (-14, -38)], GULL_G, w=2.5)
        c.poly([(-16, -50 - 80 * up), (-40, -44 - 98 * up), (-26, -48 - 72 * up)], GULL_D, ol=None)
    else:
        lift = wave
        c.poly([(-26, body_y - 10), (14, body_y - 18 - 30 * lift), (20, body_y - 8 - 20 * lift), (-8, body_y + 8),
                (-40, body_y + 6)], GULL_G, w=2.5)
        c.poly([(-40, body_y + 6), (-26, body_y - 10), (-52, body_y + 0)], GULL_D, w=2)
    # beak: upper and lower jaw
    open_ = 4 + 12 * mouth
    c.poly([(hx + 14, hy - 2), (hx + 40, hy + 2), (hx + 14, hy + 6)], BEAK, w=2)
    c.poly([(hx + 14, hy + 6), (hx + 34, hy + 4 + open_ * 0.6), (hx + 13, hy + 8 + open_ * 0.4)], BEAK, w=2)
    c.circle(hx + 31, hy + 4 + open_ * 0.4, 2.5, (230, 70, 60), ol=None)
    # eye
    ex, ey = hx + 6, hy - 5
    if eyes == "closed":
        c.arc(ex, ey, 5, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 5, 5, 200, 340, OUT, 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 5.5 * big, 6.5 * big, (255, 255, 255), w=2)
        c.ellipse(ex + 1.2, ey, 3 * big, 4 * big, (30, 26, 30), ol=None)
        c.circle(ex + 2.2, ey - 1.8, 1.3, (255, 255, 255), ol=None)
    c.arc(ex, ey - 7, 7, 4, 200, 330, OUT, 2)          # little brow
    if flower:
        fx, fy = hx - 10, hy - 16
        for k in range(6):
            a = k * math.tau / 6
            c.circle(fx + 6 * math.cos(a), fy + 6 * math.sin(a), 5, (226, 50, 70), w=1.5)
        c.circle(fx, fy, 4, (250, 210, 80), w=1.5)
    c.pop()


# ------------------------------------------------------------------- paco

def paco_hat(c, x, y, s, face, pose, walk=0.0, head_dy=0.0):
    """Flat-brimmed black Cordobes hat with a red band."""
    hx, hy = head_pos(pose, walk, head_dy)
    c.push(x, y, s, flip=face < 0)
    c.rect(hx - 20, hy - 58, hx + 22, hy - 30, (34, 32, 40), w=2.5, r=3)
    c.rect(hx - 20, hy - 38, hx + 22, hy - 31, (210, 40, 50), ol=None)
    c.ellipse(hx + 1, hy - 30, 44, 8, (34, 32, 40), w=2.5)
    c.ellipse(hx - 4, hy - 56, 12, 2, (80, 78, 90), ol=None)
    c.pop()


def paco_scarf(c, x, y, s, face, pose, walk=0.0, head_dy=0.0, t=0.0):
    hx, hy = head_pos(pose, walk, head_dy)
    c.push(x, y, s, flip=face < 0)
    flap = math.sin(t * 5) * 3
    c.poly([(hx - 20, hy + 24), (hx + 22, hy + 24), (hx + 4, hy + 46)], (210, 40, 50), w=2)
    c.poly([(hx - 16, hy + 26), (hx - 34, hy + 40 + flap), (hx - 24, hy + 44 + flap)], (210, 40, 50), w=2)
    for dx, dy in ((-6, 30), (6, 32), (2, 40)):
        c.circle(hx + dx, hy + dy, 2, (255, 230, 200), ol=None)
    c.pop()


def guitar(c, x, y, s=1.0, ang=0.0, face=1):
    """Spanish guitar centred on its lower bout; ang rotates (radians, + = clockwise)."""
    c.push(x, y, s, flip=face < 0)
    body = (214, 150, 80)
    dark = (150, 90, 44)
    neck_pts = rot([(20, -5), (98, -5), (98, 5), (20, 5)], ang)
    c.poly(neck_pts, (110, 66, 36), w=2)
    head = rot([(96, -8), (120, -10), (120, 10), (96, 8)], ang)
    c.poly(head, (90, 52, 30), w=2)
    for k in range(3):
        px, py = rot([(102 + 7 * k, -12)], ang)[0]
        c.circle(px, py, 2.2, (240, 230, 210), w=1)
    ux, uy = rot([(30, 0)], ang)[0]
    c.circle(0, 0, 30, body, w=3)
    c.circle(ux, uy, 23, body, w=3)
    c.circle(0, 0, 27, body, ol=None)
    c.circle(ux * 0.5, uy * 0.5, 20, body, ol=None)
    hx, hy = rot([(14, 0)], ang)[0]
    c.circle(hx, hy, 9, (60, 36, 24), w=2)
    c.circle(hx, hy, 11.5, None, ol=dark, w=1.5)
    bx, by = rot([(-14, 0)], ang)[0]
    c.poly(rot([(-17, -9), (-11, -9), (-11, 9), (-17, 9)], ang), dark, w=1.5)
    for k in (-3, 0, 3):
        a, b = rot([(-14, k), (100, k * 0.6)], ang)
        c.line([a, b], (250, 240, 220), 0.8, cap=False)
    c.pop()


def paco(c, x, y, s=1.0, face=1, pose="sit", t=0.0, mouth=0.0, eyes="open", look=(0, 0), head_dy=0.0,
         walk=0.0, play=0.0, guitar_on=True, **kw):
    """Paco: a tuxedo cat in a Cordobes hat. pose sit = playing guitar (play = strumming 0..1)."""
    if guitar_on and pose != "sit":
        # guitar slung on his back
        c.push(x, y, s, flip=face < 0)
        guitar(c, -22, -66, 0.9, ang=-2.4)
        c.pop()
    D.cat(c, x, y, PACO, s, face, pose, t=t, mouth=mouth, eyes=eyes, look=look, head_dy=head_dy, walk=walk,
          seed=3.7, **kw)
    paco_scarf(c, x, y, s, face, pose, walk, head_dy, t)
    paco_hat(c, x, y, s, face, pose, walk, head_dy)
    if guitar_on and pose == "sit":
        c.push(x, y, s, flip=face < 0)
        guitar(c, 4, -40, 0.85, ang=-0.32)
        # fretting paw on the neck and strumming paw
        c.ellipse(70, -64, 10, 7, PACO["belly"], w=2)
        sw = math.sin(t * 22) * 9 * play
        c.ellipse(12 + sw * 0.3, -44 + sw, 11, 8, PACO["belly"], w=2)
        c.pop()


def statue_cat(c, x, y, s=1.0, face=1, t=0.0, wink=0.0, bow=0.0):
    """The golden 'living statue' cat on a box, top hat in paw."""
    c.push(x, y, s, flip=face < 0)
    c.rect(-56, -70, 56, 0, (120, 110, 140), w=3, r=3)
    c.rect(-48, -62, 48, -8, (140, 130, 160), ol=None)
    c.rect(-30, -44, 30, -24, (230, 196, 90), w=2, r=2)
    c.text(0, -34, "ARTE", 13, (110, 80, 30))
    c.pop()
    D.cat(c, x, y - 70 * s, GOLD, s, face, "sit", t=t, eyes="open" if wink < 0.5 else "open", seed=9.0,
          head_dy=18 * bow, look=(0.6, 0.2), tail=0.0)
    hx, hy = head_pos("sit", 0, 18 * bow)
    c.push(x, y - 70 * s, s, flip=face < 0)
    if wink >= 0.5:
        ex, ey = hx + 22, hy - 4
        c.ellipse(ex, ey, 9, 11, GOLD["body"], ol=None)
        c.arc(ex, ey - 1, 7, 5, 20, 160, OUT, 3)
    # top hat held up / tipped
    ax = 50
    ay = -150 + 50 * bow
    c.ellipse(ax - 4, ay + 34, 10, 8, GOLD["body"], w=2)
    c.rect(ax - 20, ay - 10, ax + 16, ay + 22, (196, 150, 50), w=2.5, r=2)
    c.ellipse(ax - 2, ay + 22, 28, 6, (196, 150, 50), w=2.5)
    for k in range(3):
        a = t * 2 + k * 2.1
        c.circle(-30 + 50 * math.cos(a) * 0.4 + k * 30, -168 + 8 * math.sin(a * 1.3), 1.6, (255, 246, 190), ol=None)
    c.pop()


# ------------------------------------------------------------------- bowl

def bowl(c, x, y, s=1.0, kind="blue", food=0.0, ang=0.0, t=0.0):
    """Whiskers' breakfast bowl. kind: blue (the old one) | mosaic (the new one)."""
    c.push(x, y, s)
    pts = rot([(-50, -36), (50, -36), (36, 0), (-36, 0)], ang, 0, -18)
    rim = rot([(0, -36)], ang, 0, -18)[0]
    if kind == "mosaic":
        mosaic(c, "poly", pts, [(52, 104, 196), (90, 160, 230), (60, 170, 160), (250, 246, 236),
                                (130, 210, 220), (80, 190, 140), (250, 206, 70)], seed=7, cell=12,
               grout=(30, 50, 100))
        # the old blue piece in the middle
        cx, cy = rot([(0, -16)], ang, 0, -18)[0]
        c.poly([(cx - 12, cy - 9), (cx + 10, cy - 11), (cx + 14, cy + 6), (cx - 8, cy + 9)], BOWL_BLUE, w=2)
        c.circle(cx + 1, cy - 1, 3, (250, 246, 236), ol=None)
    else:
        c.poly(pts, BOWL_BLUE, w=3)
        for k in range(5):
            px = -32 + 16 * k
            q = rot([(px, -20)], ang, 0, -18)[0]
            c.circle(q[0], q[1], 5, (250, 246, 236), ol=None)
            c.circle(q[0], q[1], 2, (240, 200, 70), ol=None)
        c.line([rot([(-44, -30)], ang, 0, -18)[0], rot([(44, -30)], ang, 0, -18)[0]], (250, 246, 236), 2, cap=False)
    c.ellipse(rim[0], rim[1], 50, 9, mix(BOWL_BLUE, OUT, 0.35) if kind == "blue" else (60, 90, 150), w=3)
    if food > 0:
        c.ellipse(rim[0], rim[1] - 1, 40 * food, 6 * food, (170, 110, 70), ol=None)
        for k in range(5):
            c.circle(rim[0] - 26 + 13 * k, rim[1] - 3, 4 * food, (196, 130, 80), ol=None)
    if kind == "mosaic":
        tw = 0.5 + 0.5 * math.sin(t * 3)
        c.circle(rim[0] + 30, rim[1] + 16, 2 + 2 * tw, (255, 255, 240), ol=None)
    c.pop()


SHARDS = [((-30, -4), [(-14, -8), (12, -10), (8, 6), (-12, 8)]),
          ((14, 2), [(-10, -6), (14, -4), (6, 8), (-8, 6)]),
          ((-6, 10), [(-12, -4), (10, -6), (12, 4), (-6, 6)]),
          ((40, 8), [(-8, -6), (10, -2), (0, 6)]),
          ((-48, 10), [(-6, -6), (8, -4), (2, 6), (-8, 4)]),
          ((26, -10), [(-6, -5), (8, -6), (6, 4), (-4, 5)])]


def shards(c, x, y, s=1.0, n=6, spread=1.0, lift=0.0):
    """Broken blue bowl pieces scattered on the floor."""
    for k, ((dx, dy), pts) in enumerate(SHARDS[:n]):
        ox, oy = x + dx * spread * s, y + dy * spread * s - lift * (k % 3 + 1) * 10
        c.poly([(ox + px * s, oy + py * s) for px, py in pts], BOWL_BLUE, w=2)
        c.circle(ox, oy, 2.5 * s, (250, 246, 236), ol=None)


def bundle(c, x, y, s=1.0):
    """A little red-and-white bundle holding the pieces."""
    c.push(x, y, s)
    c.ellipse(0, -18, 26, 20, (220, 64, 70), w=2.5)
    for dx in (-12, 0, 12):
        c.line([(dx, -36), (dx, 0)], (250, 236, 236), 2, cap=False)
    c.line([(-24, -18), (24, -18)], (250, 236, 236), 2, cap=False)
    c.poly([(-6, -36), (-16, -50), (0, -42), (14, -52), (6, -36)], (220, 64, 70), w=2)
    c.pop()


# ------------------------------------------------------------------ sea

def dolphin(c, x, y, s=1.0, ang=0.0, face=1):
    c.push(x, y, s, flip=face < 0)
    body = [(-60, 0), (-40, -12), (-6, -18), (30, -14), (54, -6), (70, -2), (54, 4), (30, 10), (-10, 12),
            (-44, 8)]
    c.poly(rot(body, ang), (110, 150, 196), w=3)
    c.poly(rot([(-40, 4), (-6, 8), (30, 8), (52, 3), (30, 10), (-10, 12), (-44, 8)], ang), (232, 240, 250), ol=None)
    c.poly(rot([(-8, -17), (-22, -38), (6, -18)], ang), (110, 150, 196), w=2.5)
    c.poly(rot([(-58, 0), (-78, -14), (-72, 0), (-80, 12)], ang), (110, 150, 196), w=2.5)
    c.poly(rot([(4, 6), (-10, 22), (16, 8)], ang), (96, 136, 184), w=2)
    ex, ey = rot([(40, -6)], ang)[0]
    c.circle(ex, ey, 2.8, (20, 20, 30), ol=None)
    a, b = rot([(52, 0), (64, -1)], ang)
    c.line([a, b], OUT, 1.5, cap=False)
    c.pop()


def ship(c, x, y, s=1.0, t=0.0):
    """Big white passenger ship, bow to the right. (x, y) = waterline at the stern."""
    c.push(x, y, s)
    L = 980
    hull = [(0, -110), (L - 60, -110), (L + 40, -150), (L - 20, 0), (40, 0)]
    c.poly(hull, (250, 250, 250), w=3)
    c.poly([(40, 0), (L - 20, 0), (L + 4, -40), (12, -40)], (40, 70, 130), ol=None)
    c.line([(10, -48), (L + 2, -48)], (210, 50, 60), 7, cap=False)
    c.poly(hull, None, w=3)
    for k in range(18):
        c.circle(70 + k * 48, -78, 7, (120, 170, 220), w=2)
    # superstructure
    c.rect(80, -190, 640, -110, (246, 246, 246), w=3, r=4)
    c.rect(130, -260, 560, -190, (246, 246, 246), w=3, r=4)
    for k in range(10):
        c.rect(100 + k * 52, -170, 132 + k * 52, -146, (90, 140, 200), w=2, r=3)
    for k in range(7):
        c.rect(150 + k * 56, -240, 186 + k * 56, -216, (90, 140, 200), w=2, r=3)
    # funnel
    c.poly([(300, -260), (420, -260), (440, -360), (310, -360)], (210, 50, 60), w=3)
    c.rect(306, -350, 438, -326, (250, 200, 60), ol=None)
    c.poly([(300, -260), (420, -260), (440, -360), (310, -360)], None, w=3)
    # mast and flag
    c.line([(580, -260), (580, -380)], OUT, 4)
    wav = math.sin(t * 6) * 4
    c.poly([(580, -380), (630, -374 + wav), (630, -350 + wav), (580, -356)], (230, 60, 60), w=2)
    c.rect(580, -372, 630, -364, (250, 200, 60), ol=None)
    # lifeboats
    for k in range(3):
        c.ellipse(190 + k * 140, -196, 44, 12, (250, 140, 50), w=2)
    c.pop()


def smoke_puffs(c, x, y, t, n=6, col=(236, 236, 240), drift=-80.0):
    for k in range(n):
        u = ((t * 0.35 + k / n) % 1.0)
        c.circle(x + drift * u * 2.2 + 10 * math.sin(t + k), y - 120 * u, 14 + 34 * u, mix(col, (200, 210, 230), u),
                 ol=None)


def fishing_boat(c, x, y, s=1.0, col=(40, 120, 190), stripe=(250, 200, 60), face=1, bob=0.0, mast=True):
    """A Catalan 'llaut': rounded wooden boat with a painted eye."""
    c.push(x, y + bob, s, flip=face < 0)
    hull = [(-90, -44), (-60, -30), (40, -30), (96, -54), (84, -20), (50, 0), (-60, 0), (-86, -20)]
    c.poly(hull, col, w=3)
    c.poly([(-84, -30), (-60, -24), (40, -24), (90, -42), (88, -36), (40, -18), (-60, -18), (-86, -24)],
           stripe, ol=None)
    c.poly([(-60, 0), (50, 0), (70, -12), (-76, -12)], (250, 246, 236), ol=None)
    c.poly(hull, None, w=3)
    c.ellipse(66, -32, 8, 5, (255, 255, 255), w=1.5)
    c.circle(68, -32, 3, (20, 20, 30), ol=None)
    if mast:
        c.line([(0, -30), (0, -120)], (120, 80, 50), 4)
        c.line([(0, -110), (60, -42)], (120, 80, 50), 2, cap=False)
    c.pop()


def golden_fish(c, x, y, s=1.0, t=0.0):
    """The big golden fish sculpture on the seafront (a lattice of gold)."""
    c.push(x, y, s)
    body = [(-160, -40), (-80, -96), (40, -110), (140, -70), (180, -30), (150, -10), (40, -20), (-90, -10)]
    c.poly(body, (232, 186, 90), w=3)
    for k in range(-6, 8):
        c.line([(-150 + k * 22, -14), (-110 + k * 22, -104)], (196, 146, 60), 2, cap=False)
    c.poly([(-160, -40), (-220, -100), (-200, -40), (-226, 10)], (232, 186, 90), w=3)
    c.poly(body, None, w=3)
    for px in (-60, 40, 120):
        c.line([(px, -14), (px, 60)], (150, 150, 160), 5, cap=False)
    c.pop()


def palm(c, x, y, s=1.0, lean=0.15, t=0.0):
    c.push(x, y, s)
    pts = [(lean * 220 * (u ** 1.3) - 0, -260 * u) for u in np.linspace(0, 1, 9)]
    c.stroke(pts, (160, 116, 70), 18)
    for k, (yy) in enumerate(np.linspace(-20, -240, 9)):
        xx = lean * 220 * ((-yy / 260) ** 1.3)
        c.line([(xx - 9, yy), (xx + 9, yy - 6)], (120, 84, 50), 2, cap=False)
    tx, ty = pts[-1]
    sway = math.sin(t * 1.2) * 0.05
    for k in range(7):
        a = -math.pi + k * math.pi / 6 + sway
        fr = [(tx + math.cos(a) * 110 * u, ty + math.sin(a) * 60 * u + 50 * u * u) for u in np.linspace(0, 1, 7)]
        c.stroke(fr, (70, 150, 80), 10)
    c.circle(tx, ty + 6, 10, (130, 90, 50), w=2)
    c.pop()


# --------------------------------------------------------------- landmarks

def spire(c, x, base, w, h, col=STONE, shade=STONE_D, finial=True, rng=None):
    """One Sagrada Familia bell tower: tall rounded cone with slots and a coloured finial."""
    pts = []
    for u in np.linspace(0, 1, 14):
        hw = w / 2 * (1 - u ** 1.6) ** 0.8
        pts.append((x - hw, base - h * u))
    pts += [(x + w / 2 * (1 - u ** 1.6) ** 0.8, base - h * u) for u in np.linspace(1, 0, 14)]
    c.poly(pts, col, w=2.5)
    sh = [(x, base - h)] + [(x + w / 2 * (1 - u ** 1.6) ** 0.8, base - h * u) for u in np.linspace(1, 0, 14)] + \
         [(x + w * 0.12, base)]
    c.poly(sh, shade, ol=None)
    c.poly(pts, None, w=2.5)
    # slot windows in rows
    for j in range(1, 9):
        u = j / 11
        hw = w / 2 * (1 - u ** 1.6) ** 0.8
        yy = base - h * u
        for k in range(-1, 2):
            sx = x + k * hw * 0.5
            c.rect(sx - 1.6, yy - 9, sx + 1.6, yy + 3, (110, 86, 70), ol=None)
    if finial:
        ty = base - h
        c.line([(x, ty + 8), (x, ty - 16)], (120, 100, 80), 3)
        for dx, dy, r, cc in ((0, -24, 9, (240, 200, 60)), (-7, -16, 6, (220, 60, 50)), (7, -16, 6, (220, 60, 50)),
                              (0, -36, 5, (250, 250, 250))):
            c.circle(x + dx, ty + dy, r, cc, w=1.8)


def crane(c, x, base, h, jib=260, counter=90, t=0.0, swing=0.0, col=(240, 196, 50), hook_y=None):
    """Tower crane: lattice mast, jib with trolley and hook."""
    mw = 18
    c.rect(x - mw / 2, base - h, x + mw / 2, base, None, ol=col, w=3)
    for y0 in np.arange(base, base - h, -mw):
        c.line([(x - mw / 2, y0), (x + mw / 2, y0 - mw)], col, 2, cap=False)
    top = base - h
    c.poly([(x - counter, top), (x + jib, top), (x + jib, top - 10), (x - counter, top - 10)], col, w=2)
    for xx in np.arange(x - counter, x + jib, 20):
        c.line([(xx, top), (xx + 10, top - 10)], mix(col, OUT, 0.3), 1.5, cap=False)
    c.poly([(x - 8, top - 10), (x, top - 44), (x + 8, top - 10)], col, w=2)
    c.line([(x, top - 44), (x + jib * 0.7, top - 10)], OUT, 1.2, cap=False)
    c.line([(x, top - 44), (x - counter, top - 10)], OUT, 1.2, cap=False)
    c.rect(x - counter, top - 4, x - counter + 40, top + 22, (150, 150, 160), w=2)
    c.rect(x - 14, top + 2, x + 14, top + 26, (90, 120, 170), w=2, r=2)
    tx = x + jib * (0.55 + 0.25 * math.sin(t * 0.3 + swing))
    hy = hook_y if hook_y is not None else top + 120 + 40 * math.sin(t * 0.4 + swing)
    c.rect(tx - 9, top + 2, tx + 9, top + 10, (80, 80, 90), ol=None)
    c.line([(tx, top + 10), (tx, hy)], OUT, 1.5, cap=False)
    c.poly([(tx - 5, hy), (tx + 5, hy), (tx + 2, hy + 10), (tx + 7, hy + 12), (tx, hy + 16)], (230, 60, 50), w=1.5)


def sagrada(c, x, base, s=1.0, col=STONE, shade=STONE_D, detail=True):
    """The Sagrada Familia (simplified): 8 bell towers, the tall central towers and the facade."""
    c.push(x, base, s)
    # the tall central towers (the unfinished heart of the church)
    spire(c, 0, -170, 110, 700, col=mix(col, (255, 255, 255), 0.12), shade=shade)
    spire(c, -120, -170, 84, 520, col=col, shade=shade)
    spire(c, 120, -170, 84, 520, col=col, shade=shade)
    c.circle(0, -890, 14, (250, 250, 250), w=2)
    for a in range(4):
        aa = a * math.pi / 2
        c.line([(0, -890), (math.cos(aa) * 26, -890 + math.sin(aa) * 26)], (250, 250, 250), 5)
    # main nave block
    c.poly([(-330, 0), (-330, -260), (-250, -330), (250, -330), (330, -260), (330, 0)], shade, w=3)
    c.poly([(-330, 0), (-330, -260), (-250, -330), (60, -330), (60, 0)], col, ol=None)
    c.poly([(-330, 0), (-330, -260), (-250, -330), (250, -330), (330, -260), (330, 0)], None, w=3)
    # facade towers (front, four of them)
    for k, dx in enumerate((-300, -200, 200, 300)):
        spire(c, dx, -60, 70, 520 if k in (1, 2) else 470, col=col, shade=shade)
    # portal: three organic arches
    for dx, w, h in ((-130, 90, 200), (0, 120, 250), (130, 90, 200)):
        c.poly([(dx - w / 2, 0)] + [(dx + w / 2 * math.cos(a), -h + h * 0.45 * (1 - math.sin(a)) - 0)
                                    for a in np.linspace(math.pi, 0, 12)] + [(dx + w / 2, 0)],
               mix(shade, OUT, 0.35), w=2.5)
        c.poly([(dx - w / 2 + 12, 0)] + [(dx + (w / 2 - 12) * math.cos(a), -h + 20 + h * 0.4 * (1 - math.sin(a)))
                                         for a in np.linspace(math.pi, 0, 12)] + [(dx + w / 2 - 12, 0)],
               (90, 70, 66), ol=None)
    if detail:
        rng = np.random.default_rng(3)
        for _ in range(60):     # knobbly 'melting' decoration over the portals
            px = rng.uniform(-200, 200)
            py = rng.uniform(-330, -230)
            c.circle(px, py, rng.uniform(5, 12), mix(col, shade, rng.uniform(0, 0.6)), w=1.5)
        for dx in (-250, 250):
            c.rect(dx - 14, -230, dx + 14, -120, (120, 96, 90), w=2, r=12)
    c.pop()


def gaudi_house(c, x, base, w=300, floors=5, wall=(110, 180, 200), seed=1):
    """A wavy Gaudi house (Casa Batllo-like): mosaic facade, bone balconies, dragon roof."""
    fh = 70
    h = floors * fh + 30
    left = [(x + 8 * math.sin(u * 7), base - h * u) for u in np.linspace(0, 1, 10)]
    right = [(x + w + 8 * math.sin(u * 7 + 1), base - h * u) for u in np.linspace(1, 0, 10)]
    c.poly(left + right, wall, w=3)
    mosaic(c, "poly", left + right, [mix(wall, (255, 255, 255), 0.3), wall, (80, 150, 200), (170, 210, 200),
                                      (230, 170, 120), (140, 120, 190)], seed=seed, cell=16, grout=(236, 232, 220))
    # dragon-scale roof
    roof = [(x - 10, base - h)]
    for k, u in enumerate(np.linspace(0, 1, 13)):
        roof.append((x - 10 + (w + 20) * u, base - h - 40 - 30 * math.sin(math.pi * u) - (8 if k % 2 else 0)))
    roof.append((x + w + 10, base - h))
    c.poly(roof, (210, 110, 90), w=3)
    for k in range(10):
        u = (k + 0.5) / 10
        c.arc(x - 10 + (w + 20) * u, base - h - 30 - 24 * math.sin(math.pi * u), 14, 10, 0, 180,
              (250, 190, 120), 2)
    c.rect(x + w * 0.18 - 8, base - h - 100, x + w * 0.18 + 8, base - h - 50, (240, 220, 180), w=2, r=6)
    c.circle(x + w * 0.18, base - h - 106, 11, (240, 200, 60), w=2)
    # windows with mask-like balconies
    for j in range(floors):
        yy = base - 30 - j * fh - fh / 2
        for i in range(3):
            wx = x + w * (0.2 + 0.3 * i)
            c.ellipse(wx, yy, 26, 24, (40, 60, 90), w=2.5)
            c.ellipse(wx - 6, yy - 6, 8, 7, (120, 170, 210), ol=None)
            if j > 0:
                c.poly([(wx - 30, yy + 18), (wx + 30, yy + 18), (wx + 22, yy + 30), (wx - 22, yy + 30)],
                       (244, 236, 214), w=2)
                for dx in (-12, 12):
                    c.ellipse(wx + dx, yy + 22, 5, 3.5, (40, 40, 50), ol=None)
    c.rect(x + w * 0.3, base - 90, x + w * 0.7, base, (60, 80, 100), w=3, r=30)


def eixample(c, x, base, w, floors, wall, rng, shutters=(70, 130, 96), awning=None):
    """An ordinary Barcelona block with iron balconies and shutters."""
    fh = 64
    h = floors * fh + 40
    c.rect(x, base - h, x + w, base, wall, w=3)
    c.rect(x - 6, base - h - 14, x + w + 6, base - h, mix(wall, OUT, 0.25), w=2.5)
    cols = max(2, int(w // 70))
    for j in range(floors):
        yy = base - 40 - j * fh - fh / 2 - 10
        for i in range(cols):
            wx = x + (i + 0.5) * w / cols
            c.rect(wx - 14, yy - 22, wx + 14, yy + 16, (60, 70, 90), w=2)
            c.rect(wx - 22, yy - 22, wx - 14, yy + 16, shutters, w=1.5)
            c.rect(wx + 14, yy - 22, wx + 22, yy + 16, shutters, w=1.5)
            if j > 0:
                c.rect(wx - 26, yy + 14, wx + 26, yy + 20, (60, 60, 70), w=1.5)
                for k in range(7):
                    xx = wx - 24 + 8 * k
                    c.line([(xx, yy + 2), (xx, yy + 14)], (60, 60, 70), 1.5, cap=False)
                c.line([(wx - 26, yy + 2), (wx + 26, yy + 2)], (60, 60, 70), 2, cap=False)
                if rng.random() < 0.4:
                    for k in range(3):
                        c.circle(wx - 14 + 14 * k, yy + 10, 5, [(220, 60, 80), (250, 160, 60), (230, 90, 160)][k],
                                 ol=None)
    if awning:
        c.rect(x + 10, base - 70, x + w - 10, base, (60, 50, 50), w=2)
        for k in range(int((w - 20) // 24)):
            c.rect(x + 10 + 24 * k, base - 96, x + 34 + 24 * k, base - 70, awning if k % 2 else (250, 246, 236),
                   ol=None)
        c.rect(x + 10, base - 96, x + w - 10, base - 70, None, w=2)


def plane_tree(c, x, y, s=1.0, leaf=(110, 170, 80)):
    c.push(x, y, s)
    c.stroke([(0, 0), (-4, -90), (2, -170)], (200, 186, 150), 18)
    for px, py in ((-6, -40), (4, -100), (-2, -140)):
        c.ellipse(px, py, 7, 5, (160, 150, 120), ol=None)
    for dx, dy, r in ((-60, -200, 56), (50, -210, 58), (0, -250, 66), (-20, -180, 50), (40, -170, 48)):
        c.circle(dx, dy, r, leaf)
    for dx, dy, r in ((-60, -200, 50), (50, -210, 52), (0, -250, 60), (-20, -180, 44), (40, -170, 42)):
        c.circle(dx, dy, r, leaf, ol=None)
    for dx, dy, r in ((-30, -250, 22), (40, -230, 18), (-70, -210, 14)):
        c.circle(dx, dy, r, mix(leaf, (255, 255, 200), 0.25), ol=None)
    c.pop()


def flower_stall(c, x, base, s=1.0, rng_seed=1):
    rng = np.random.default_rng(rng_seed)
    c.push(x, base, s)
    c.rect(-90, -150, 90, 0, (60, 110, 80), w=3, r=3)
    c.poly([(-110, -150), (110, -150), (90, -190), (-90, -190)], (40, 90, 66), w=3)
    for k in range(8):
        c.rect(-80 + 20 * k, -150, -70 + 20 * k, -130, (250, 246, 236) if k % 2 else (220, 70, 80), ol=None)
    for row, yy in enumerate((-90, -50, -10)):
        for k in range(6):
            bx = -74 + 29 * k + (row % 2) * 8
            c.rect(bx - 11, yy, bx + 11, yy + 22, (150, 110, 80), w=1.5)
            col = [(230, 60, 80), (250, 200, 60), (250, 130, 170), (250, 250, 250), (170, 100, 220),
                   (250, 140, 60)][rng.integers(6)]
            for j in range(4):
                c.circle(bx - 8 + 5 * j, yy - 4 - 5 * (j % 2), 6, col, w=1.2)
    c.pop()


def colom(c, x, base, s=1.0):
    """The tall Columbus column at the bottom of La Rambla."""
    c.push(x, base, s)
    c.rect(-60, -80, 60, 0, (200, 186, 160), w=3)
    c.rect(-40, -160, 40, -80, (190, 176, 150), w=3)
    c.poly([(-14, -160), (14, -160), (10, -500), (-10, -500)], (120, 140, 120), w=3)
    for yy in range(-470, -170, 40):
        c.line([(-11, yy), (11, yy + 10)], (100, 120, 100), 2, cap=False)
    c.ellipse(0, -508, 24, 10, (200, 176, 90), w=2.5)
    c.circle(0, -526, 16, (200, 176, 90), w=2.5)
    c.rect(-8, -580, 8, -526, (100, 120, 100), w=2)
    c.circle(0, -588, 9, (100, 120, 100), w=2)
    c.line([(6, -570), (40, -600)], (100, 120, 100), 5)
    c.pop()


def glories(c, x, base, s=1.0, col=(90, 120, 170)):
    """The rounded 'bullet' tower on the Barcelona skyline."""
    c.push(x, base, s)
    pts = [(-40, 0), (-40, -160)] + [(-40 * math.cos(a), -160 - 70 * math.sin(a)) for a in np.linspace(0, math.pi, 10)][::-1] + [(40, -160), (40, 0)]
    pts = [(-40, 0), (-40, -160)] + [(40 * math.cos(a), -160 - 70 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)] + [(40, 0)]
    c.poly(pts, col, w=2.5)
    for k in range(10):
        c.line([(-36, -14 - 18 * k), (36, -14 - 18 * k)], mix(col, (255, 255, 255), 0.3), 1.5, cap=False)
    c.pop()


def hotel_sail(c, x, base, s=1.0, col=(150, 190, 220)):
    """The sail-shaped glass hotel at the end of the beach."""
    c.push(x, base, s)
    c.poly([(-30, 0), (-30, -250), (40, -200), (60, 0)], col, w=2.5)
    for k in range(12):
        c.line([(-28, -18 - 19 * k), (52 - 0.3 * k, -18 - 16 * k)], mix(col, (255, 255, 255), 0.35), 1.2, cap=False)
    c.pop()


def gingerbread(c, x, base, s=1.0, wall=(196, 150, 100), tower=True, seed=2):
    """A Park Guell gatehouse: gingerbread walls, an icing roof and a chequered spire."""
    c.push(x, base, s)
    c.rect(-90, -150, 90, 0, wall, w=3)
    rng = np.random.default_rng(seed)
    for _ in range(30):
        px, py = rng.uniform(-82, 82), rng.uniform(-142, -8)
        c.rect(px - 6, py - 4, px + 6, py + 4, mix(wall, (250, 236, 210), 0.5), ol=None)
    c.rect(-24, -80, 24, 0, (90, 60, 40), w=2.5, r=20)
    c.ellipse(-50, -110, 14, 18, (60, 50, 60), w=2)
    c.ellipse(50, -110, 14, 18, (60, 50, 60), w=2)
    # wavy icing roof
    roof = [(-104, -150)] + [(-104 + 208 * u, -150 - 70 * math.sin(math.pi * u) - 12 * math.sin(u * 18))
                             for u in np.linspace(0, 1, 18)] + [(104, -150)]
    c.poly(roof, (250, 246, 236), w=3)
    mosaic(c, "poly", roof, [(250, 246, 236), (160, 110, 80), (240, 240, 230), (130, 90, 70)], seed=seed + 4,
           cell=14, ol=OUT, grout=(236, 226, 210))
    for k in range(9):
        u = (k + 0.5) / 9
        c.ellipse(-104 + 208 * u, -150 + 6, 10, 10, (250, 246, 236), w=2)
    if tower:
        c.push(70, -170)
        pts = [(-18, 0), (-12, -150), (12, -150), (18, 0)]
        c.poly(pts, (250, 250, 250), w=2.5)
        for j in range(10):
            for i in range(3):
                if (i + j) % 2:
                    yy = -15 * j
                    hw0 = 18 - 6 * j / 10
                    hw1 = 18 - 6 * (j + 1) / 10
                    xa0 = -hw0 + 2 * hw0 * i / 3
                    xa1 = -hw0 + 2 * hw0 * (i + 1) / 3
                    xb0 = -hw1 + 2 * hw1 * i / 3
                    xb1 = -hw1 + 2 * hw1 * (i + 1) / 3
                    c.poly([(xa0, yy), (xa1, yy), (xb1, yy - 15), (xb0, yy - 15)], (50, 100, 190), ol=None)
        c.poly(pts, None, w=2.5)
        c.ellipse(0, -156, 20, 10, (210, 70, 60), w=2)
        for a in range(4):
            aa = a * math.pi / 2
            c.line([(0, -180), (math.cos(aa) * 14, -180 + math.sin(aa) * 14)], (250, 250, 250), 6)
        c.line([(0, -166), (0, -180)], (250, 250, 250), 5)
        c.pop()
    c.pop()


def lizard(c, x, y, s=1.0):
    """El Drac: the mosaic lizard of Park Guell, head to the left, tail curling up to the right."""
    c.push(x, y, s)
    spine = [(-150, -40), (-110, -50), (-60, -58), (0, -60), (60, -56), (110, -48), (150, -56), (180, -80),
             (186, -110), (170, -130), (150, -126)]
    widths = [26, 34, 40, 42, 40, 32, 22, 16, 11, 8, 5]
    left, right = [], []
    for k, (px, py) in enumerate(spine):
        a = spine[max(0, k - 1)]
        b = spine[min(len(spine) - 1, k + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        wv = widths[k]
        left.append((px + nx * wv, py + ny * wv))
        right.append((px - nx * wv, py - ny * wv))
    body = left + right[::-1]
    # legs (behind)
    for lx, d in ((-90, -1), (80, 1)):
        leg = [(lx - 14, -40), (lx + 14, -40), (lx + 24 * d + 10, -6), (lx + 30 * d + 16, 0), (lx + 30 * d - 14, 0),
               (lx + 24 * d - 10, -10)]
        mosaic(c, "poly", leg, LIZARD_COLS, seed=abs(21 + lx), cell=10)
    mosaic(c, "poly", body, LIZARD_COLS, seed=5, cell=13)
    # blue and orange spots along the back
    for k in (2, 3, 4, 5):
        px, py = spine[k]
        c.circle(px, py - 18, 11, (40, 110, 200), w=2)
        c.circle(px, py - 18, 5, (250, 140, 40), ol=None)
    for lx, d in ((-60, -1), (120, 1)):
        leg = [(lx - 14, -50), (lx + 14, -50), (lx + 24 * d + 10, -12), (lx + 30 * d + 18, -4), (lx + 30 * d - 14, -4),
               (lx + 24 * d - 10, -16)]
        mosaic(c, "poly", leg, LIZARD_COLS, seed=abs(31 + lx), cell=10)
        for k in range(3):
            c.ellipse(lx + 30 * d - 10 + 12 * k, -4, 6, 4, (70, 170, 90), w=1.5)
    # head
    head = [(-140, -66), (-196, -70), (-236, -54), (-246, -38), (-226, -24), (-180, -18), (-140, -18)]
    mosaic(c, "poly", head, LIZARD_COLS, seed=9, cell=10)
    c.poly([(-246, -38), (-226, -34), (-200, -36)], (60, 40, 40), w=2)
    c.circle(-196, -62, 12, (250, 220, 70), w=2.5)
    c.circle(-198, -62, 6, (30, 30, 30), ol=None)
    c.circle(-195, -65, 2, (255, 255, 255), ol=None)
    c.pop()


def stone_steps(c, x0, x1, top, n, step_h=26, col=(232, 210, 170)):
    for k in range(n):
        y = top + k * step_h
        inset = (n - k) * 6
        c.rect(x0 - k * 8, y, x1 + k * 8, y + step_h, mix(col, (255, 255, 255), 0.1 * (k % 2)), w=2)
        c.line([(x0 - k * 8 + 4, y + 4), (x1 + k * 8 - 4, y + 4)], mix(col, (255, 255, 255), 0.4), 2, cap=False)


# ------------------------------------------------------------------- food

def plate(c, x, y, s=1.0, kind="bravas", eaten=0.0):
    """A little tapas plate. eaten 0..1 empties it."""
    c.push(x, y, s)
    c.ellipse(0, 0, 46, 13, (250, 248, 240), w=2.5)
    c.ellipse(0, -1, 36, 9, (232, 228, 216), ol=None)
    k = 1 - eaten
    if k > 0.02:
        if kind == "bravas":
            for i, (dx, dy) in enumerate(((-18, -6), (0, -8), (16, -6), (-8, -14), (8, -15), (-2, -22))):
                if i / 6 < k:
                    c.rect(dx - 8, dy - 7, dx + 8, dy + 5, (246, 200, 90), w=1.5, r=2)
            if k > 0.3:
                c.ellipse(0, -14, 18 * k, 6, (220, 70, 40), ol=None)
                c.ellipse(-4, -18, 8 * k, 3, (250, 246, 230), ol=None)
        elif kind == "tortilla":
            c.poly([(-24, -6), (24 * k, -6), (24 * k, -18), (-14, -24), (-24, -18)], (250, 214, 110), w=2)
            c.line([(-24, -18), (-14, -24)], (200, 140, 60), 3)
        elif kind == "olives":
            for i in range(int(round(7 * k))):
                c.ellipse(-20 + 7 * i, -7 - 4 * (i % 2), 6, 5, (110, 140, 50), w=1.5)
        elif kind == "croquetas":
            for i in range(int(round(4 * k))):
                c.ellipse(-18 + 12 * i, -9 - 3 * (i % 2), 9, 6, (200, 130, 60), w=1.5)
        elif kind == "pan":
            for i in range(int(round(2 * k + 0.4))):
                c.rect(-26 + 26 * i, -16, -2 + 26 * i, -4, (230, 170, 100), w=1.5, r=3)
                c.rect(-23 + 26 * i, -16, -5 + 26 * i, -10, (210, 70, 60), ol=None)
        elif kind == "churros":
            for i in range(int(round(4 * k))):
                pts = [(-28 + i * 4, -6 - i * 5), (24 + i * 4, -10 - i * 5)]
                c.stroke(pts, (220, 160, 80), 8)
                for j in range(5):
                    xx = -24 + i * 4 + 11 * j
                    c.line([(xx, -9 - i * 5), (xx + 4, -7 - i * 5)], (180, 110, 50), 1.2, cap=False)
    c.pop()


def choc_cup(c, x, y, s=1.0, level=1.0, steam_t=None):
    c.push(x, y, s)
    c.poly([(-24, -40), (24, -40), (18, 0), (-18, 0)], (250, 246, 236), w=2.5)
    c.arc(30, -24, 10, 11, -90, 90, OUT, 3)
    if level > 0:
        c.ellipse(0, -40, 23, 6, (110, 60, 40), w=2)
    c.ellipse(0, 1, 30, 6, (250, 246, 236), w=2)
    if steam_t is not None:
        for k in range(2):
            u = (steam_t * 0.6 + k * 0.5) % 1.0
            pts = [(-6 + 12 * k + 4 * math.sin(steam_t * 3 + v * 5), -48 - 40 * u - 20 * v) for v in np.linspace(0, 1, 5)]
            c.line(pts, mix((255, 255, 255), (230, 220, 210), u), 3 * (1 - u) + 1)
    c.pop()


def jamon(c, x, y, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, 30)], (120, 100, 80), 2, cap=False)
    c.poly([(-6, 30), (6, 30), (24, 90), (30, 150), (0, 176), (-26, 150), (-20, 90)], (176, 76, 66), w=2.5)
    c.poly([(-14, 110), (20, 110), (26, 150), (0, 168), (-20, 150)], (236, 210, 190), ol=None)
    c.rect(-6, 22, 6, 34, (240, 236, 220), w=1.5)
    c.pop()


def steam_puff(c, x, y, k, s=1.0):
    if k <= 0:
        return
    for j, (dx, dy, r) in enumerate(((0, 0, 10), (8, -10, 12), (-6, -20, 14))):
        c.circle(x + dx * s, y + dy * s - 30 * k * s, r * s * (0.5 + k), mix((255, 255, 255), (220, 220, 230), k),
                 w=1.5)


def flame(c, x, y, s=1.0, t=0.0):
    fl = 1 + 0.2 * math.sin(t * 30)
    c.push(x, y, s)
    c.poly([(0, 0), (40 * fl, -14), (70 * fl, 0), (40 * fl, 14)], (250, 120, 40), w=2)
    c.poly([(4, 0), (34 * fl, -7), (52 * fl, 0), (34 * fl, 7)], (255, 220, 80), ol=None)
    c.pop()


def sea_glass(c, x, y, col, s=1.0, tw=0.0):
    c.push(x, y, s)
    c.poly([(-8, -2), (-2, -7), (8, -5), (7, 4), (-4, 5)], col, w=1.8)
    c.poly([(-5, -2), (-1, -5), (3, -4)], mix(col, (255, 255, 255), 0.6), ol=None)
    if tw > 0:
        r = 10 * tw
        c.line([(-r, -14), (r, -14)], (255, 255, 240), 2, cap=False)
        c.line([(0, -14 - r), (0, -14 + r)], (255, 255, 240), 2, cap=False)
    c.pop()


def shell(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-14, 0)] + [(14 * math.cos(a), -16 * math.sin(a)) for a in np.linspace(math.pi, 0, 10)] + [(14, 0)],
           (250, 196, 180), w=2)
    for k in range(-2, 3):
        c.line([(0, 2), (k * 6, -12)], (220, 150, 140), 1.5, cap=False)
    c.rect(-4, -1, 4, 4, (250, 196, 180), w=1.5)
    c.pop()


def blue_tile(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-12, -12, 12, 12, (250, 246, 236), w=2)
    c.circle(0, 0, 7, (50, 100, 190), ol=None)
    for a in range(4):
        aa = a * math.pi / 2 + math.pi / 4
        c.circle(math.cos(aa) * 9, math.sin(aa) * 9, 3, (50, 100, 190), ol=None)
    c.pop()


# ------------------------------------------------------------------ frame fx

_shade_masks = {}


def shade_bottom(c, tl, t, strength=0.5, top=540):
    """Darken the bottom of the frame softly while a subtitle shows."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    if k <= 0:
        return
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    key = (q, top)
    if key not in _shade_masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _shade_masks[key] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((20, 16, 30), (0, top * SS, W * SS, H * SS), _shade_masks[key])


def overlay(c, col, alpha):
    if alpha <= 0.003:
        return
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha))
    c.d = ImageDraw.Draw(c.img)
