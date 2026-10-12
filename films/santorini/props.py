"""Santorini props and characters: Captain Stelios the pelican, Fasolaki the donkey,
cube houses, blue domes, windmills, bell towers, caldera cliffs, boats, food, the puzzle.

Characters are drawn in local space: origin between the feet, facing right, y up negative.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, mix, clamp, ease

WHITE = (250, 250, 246)
WHITE_SH = (214, 222, 236)
BLUE = (34, 92, 186)
BLUE_LT = (70, 140, 220)
DOME = (28, 86, 178)
DOME_LT = (66, 130, 214)
SEA = (22, 74, 150)
SEA_LT = (46, 118, 196)
CLIFF = [(150, 84, 64), (176, 108, 76), (120, 70, 62), (196, 140, 98), (98, 70, 70)]
OCHRE = (236, 196, 120)
PINK = (242, 120, 170)

_shade_masks = {}


# ================================================================ helpers

def shade_bottom(c, tl, t, strength=0.5, top=548):
    """Darken the bottom of the frame softly while a subtitle shows (white text on bright scenes)."""
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
    c.img.paste((16, 18, 40), (0, top * SS, W * SS, H * SS), _shade_masks[q])


def overlay(c, col, alpha):
    """Mix the whole frame toward a colour (dusk, dawn)."""
    if alpha <= 0.003:
        return
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha))
    c.d = ImageDraw.Draw(c.img)


def rgba_canvas(w, h):
    return Canvas(Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)), size=(w, h))


def sun(c, x, y, r, sky, core=(255, 236, 150), halo=(255, 200, 120), steps=10):
    c.glow(x, y, r * 3.2, r * 3.2, halo, sky, steps=steps)
    c.circle(x, y, r * 1.12, mix(core, halo, 0.4), ol=None)
    c.circle(x, y, r, core, ol=None)


def gull(c, x, y, t, s=1.0, col=(255, 255, 255), seed=0.0):
    k = math.sin(t * 7 + seed)
    c.push(x, y, s)
    c.line([(-22, -6 * k), (-10, -2 - 4 * k), (0, 0)], OUT, 4)
    c.line([(22, -6 * k), (10, -2 - 4 * k), (0, 0)], OUT, 4)
    c.line([(-20, -6 * k), (-10, -2 - 4 * k), (0, 0)], col, 2)
    c.line([(20, -6 * k), (10, -2 - 4 * k), (0, 0)], col, 2)
    c.pop()


def sea_glints(c, t, x0, x1, y0, y1, n=40, seed=1, col=(150, 200, 250), speed=1.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        f = (y - y0) / max(1, y1 - y0)
        ph = rng.uniform(0, 6.28)
        a = 0.5 + 0.5 * math.sin(t * 2.2 * speed + ph)
        if a < 0.25:
            continue
        L = (8 + 22 * f) * a
        dx = 10 * math.sin(t * 0.6 * speed + ph)
        c.line([(x - L + dx, y), (x + L + dx, y)], col, 1.5 + 1.5 * f, cap=False)


def sparkle_path(c, t, sx, y0, y1, w0, w1, n=18, col=(255, 230, 160), seed=3):
    """Sun's glittering road on the sea, from the horizon (y0) toward the viewer (y1)."""
    rng = np.random.default_rng(seed)
    for k in range(n):
        f = rng.uniform(0, 1) ** 1.3
        y = lerp(y0, y1, f)
        hw = lerp(w0, w1, f)
        x = sx + rng.uniform(-hw, hw)
        a = 0.5 + 0.5 * math.sin(t * 3 + k * 1.7)
        L = (6 + 26 * f) * (0.4 + 0.6 * a)
        c.line([(x - L, y), (x + L, y)], col, 1.5 + 2 * f, cap=False)


# ================================================================ architecture

def cube_house(c, x, y, w, h, rng=None, col=WHITE, shade=WHITE_SH, door=True, shutter=BLUE, roof="flat", lw=2.5):
    """A whitewashed cube house, (x, y) = bottom-left."""
    r = rng if rng is not None else np.random.default_rng(int(x * 7 + y))
    if roof == "vault":
        c.ellipse(x + w / 2, y - h, w / 2, h * 0.28, col, w=lw)
    c.rect(x, y - h, x + w, y, col, w=lw, r=3)
    c.rect(x + w * 0.78, y - h + 3, x + w - 2, y - 2, shade, ol=None)
    if roof == "flat":
        c.rect(x - 3, y - h - 5, x + w + 3, y - h + 2, col, w=lw, r=2)
    if door and w > 26 and h > 34:
        dw = min(16, w * 0.3)
        dx = x + r.uniform(0.15, 0.55) * (w - dw)
        c.rect(dx, y - min(30, h * 0.6), dx + dw, y, shutter, w=1.5, r=dw * 0.45)
        if w > 50:
            wx = x + w * 0.72 - 6 if dx < x + w * 0.5 else x + w * 0.18
            c.rect(wx, y - h * 0.68, wx + 13, y - h * 0.68 + 14, shutter, w=1.5, r=2)
    elif h > 20:
        wx = x + w * 0.35
        c.rect(wx, y - h * 0.65, wx + max(6, w * 0.25), y - h * 0.65 + max(6, h * 0.25), shutter, w=1.5, r=2)


def dome_church(c, x, y, s=1.0, dome=DOME, dome_lt=DOME_LT, bell_gable=True, t=0.0, ring=0.0):
    """Little white chapel with a blue dome. (x, y) = bottom centre."""
    c.push(x, y, s)
    c.rect(-60, -70, 60, 0, WHITE, r=3)
    c.rect(30, -66, 58, -2, WHITE_SH, ol=None)
    c.rect(-14, -46, 14, 0, (60, 110, 190), w=2, r=12)
    # drum + dome
    c.rect(-36, -96, 36, -68, WHITE, r=2)
    for k in range(-2, 3):
        c.rect(k * 13 - 3, -90, k * 13 + 3, -76, (60, 110, 190), w=1.2, r=2)
    c.ellipse(0, -96, 40, 44, dome)
    c.rect(-44, -96, 44, -60, WHITE, ol=None)
    c.rect(-38, -98, 38, -92, WHITE, w=2)
    c.ellipse(-12, -116, 12, 14, dome_lt, ol=None)
    c.line([(0, -140), (0, -160)], (250, 250, 250), 4)
    c.line([(0, -140), (0, -160)], OUT, 1.5)
    c.line([(-7, -152), (7, -152)], OUT, 2)
    if bell_gable:
        c.poly([(34, -70), (34, -104), (46, -116), (58, -104), (58, -70)], WHITE)
        c.rect(40, -100, 52, -84, (60, 70, 90), w=1.5, r=6)
        sw = math.sin(t * 9) * 0.5 * ring
        bx, by = 46 + 4 * math.sin(sw), -90
        c.ellipse(bx, by, 4, 5, (210, 170, 70), w=1.2)
    c.pop()


def bell_tower(c, x, y, s=1.0, t=0.0, ring=0.0, dome=DOME):
    """A white open belfry with two arched openings and swinging bells."""
    c.push(x, y, s)
    c.rect(-46, -150, 46, 0, WHITE, r=2)
    c.rect(26, -146, 44, -2, WHITE_SH, ol=None)
    c.poly([(-46, -150), (-46, -190), (0, -230), (46, -190), (46, -150)], WHITE)
    for k, bx in enumerate((-20, 20)):
        c.rect(bx - 14, -200 + abs(bx) * 0.5, bx + 14, -152, (90, 110, 150), w=2, r=12)
        sw = math.sin(t * 8 + k * 1.3) * 0.6 * ring
        c.push(bx, -186 + abs(bx) * 0.5)
        hx, hy = math.sin(sw) * 18, math.cos(sw) * 18
        c.line([(0, 0), (hx * 0.6, hy * 0.6)], OUT, 2)
        c.poly([(hx - 9, hy + 6), (hx - 6, hy - 6), (hx + 6, hy - 6), (hx + 9, hy + 6)], (220, 176, 70), w=1.5)
        c.pop()
    c.ellipse(0, -232, 12, 10, dome, w=2)
    c.line([(0, -242), (0, -262)], OUT, 2)
    c.line([(-6, -254), (6, -254)], OUT, 2)
    c.pop()


def windmill(c, x, y, s=1.0, ang=0.0, roof=(170, 120, 80), sail=(250, 246, 236)):
    """Cycladic windmill: round white tower, thatched cone cap, eight spoked sails."""
    c.push(x, y, s)
    c.poly([(-46, 0), (-40, -150), (40, -150), (46, 0)], WHITE)
    c.poly([(22, -148), (40, -150), (46, 0), (28, 0)], WHITE_SH, ol=None)
    c.rect(-12, -40, 12, 0, (120, 80, 60), w=2, r=10)
    c.rect(-8, -110, 8, -92, (120, 80, 60), w=1.5, r=5)
    c.poly([(-48, -148), (0, -196), (48, -148)], roof)
    for k in range(4):
        c.line([(-40 + 20 * k, -150), (-20 + 10 * k, -170)], mix(roof, OUT, 0.3), 1.5, cap=False)
    hx, hy = 0, -160
    for k in range(8):
        a = ang + k * math.tau / 8
        ex, ey = hx + math.cos(a) * 120, hy + math.sin(a) * 120
        c.line([(hx, hy), (ex, ey)], (110, 80, 60), 3)
        b = a + 0.32
        p1 = (hx + math.cos(a) * 40, hy + math.sin(a) * 40)
        p2 = (hx + math.cos(b) * 112, hy + math.sin(b) * 112)
        c.poly([p1, (ex, ey), p2, (hx + math.cos(b) * 48, hy + math.sin(b) * 48)], sail, w=1.5)
        c.line([(ex, ey), (hx + math.cos(a + math.tau / 8) * 120, hy + math.sin(a + math.tau / 8) * 120)],
               (110, 80, 60), 1, cap=False)
    c.circle(hx, hy, 8, (110, 80, 60), w=2)
    c.pop()


def cliff_band(c, x0, x1, top_fn, bottom, seed=0, cols=CLIFF, ol=(70, 46, 46)):
    """A cliff face with coloured horizontal rock strata between top_fn(x) and a straight bottom."""
    xs = list(np.arange(x0, x1 + 1, 16))
    top = [(x, top_fn(x)) for x in xs]
    c.poly(top + [(x1, bottom), (x0, bottom)], cols[0], ol=ol, w=3)
    rng = np.random.default_rng(seed)
    n = 7
    for k in range(1, n):
        f = k / n
        col = cols[k % len(cols)]
        ph = rng.uniform(0, 6)
        amp = rng.uniform(6, 16)
        pts_a = [(x, lerp(top_fn(x), bottom, f) + amp * math.sin(x / 90 + ph)) for x in xs]
        pts_b = [(x, lerp(top_fn(x), bottom, min(1, f + 0.08)) + amp * math.sin(x / 90 + ph + 0.4)) for x in xs]
        c.poly(pts_a + pts_b[::-1], col, ol=None)
    # cracks and boulders
    for k in range(int((x1 - x0) / 40)):
        x = rng.uniform(x0, x1)
        y = lerp(top_fn(x), bottom, rng.uniform(0.15, 0.95))
        c.line([(x, y), (x + rng.uniform(-14, 14), y + rng.uniform(14, 40))], mix(cols[2], OUT, 0.3), 2)


def village_top(c, x0, x1, top_fn, seed=0, density=1.0, domes=2, scale=1.0, mills=()):
    """White houses and blue domes crowding the top edge of a cliff."""
    rng = np.random.default_rng(seed)
    items = []
    x = x0
    while x < x1:
        w = rng.uniform(28, 62) * scale
        h = rng.uniform(24, 48) * scale
        y = top_fn(x + w / 2) + rng.uniform(4, 30) * scale
        items.append((y, "house", x, w, h))
        x += w * rng.uniform(0.55, 0.95) / density
    for k in range(domes):
        dx = lerp(x0, x1, (k + 0.5) / domes) + rng.uniform(-40, 40)
        items.append((top_fn(dx) + 10 * scale, "dome", dx, 0, 0))
    # second, lower row cascading down the cliff
    x = x0 + 20
    while x < x1:
        w = rng.uniform(26, 50) * scale
        h = rng.uniform(22, 36) * scale
        y = top_fn(x + w / 2) + rng.uniform(40, 80) * scale
        if rng.random() < 0.7:
            items.append((y, "house", x, w, h))
        x += w * rng.uniform(0.9, 1.6) / density
    items.sort(key=lambda it: it[0])
    for y, kind, x, w, h in items:
        if kind == "house":
            vault = rng.random() < 0.25
            cube_house(c, x, y, w, h, rng, door=w > 36 * scale,
                       shutter=[BLUE, (60, 150, 200), (200, 80, 60)][int(rng.integers(3))] if rng.random() < 0.3 else BLUE,
                       roof="vault" if vault else "flat", lw=2 * min(1, scale + 0.2))
            if rng.random() < 0.18:
                bougainvillea(c, x + w * 0.8, y - h * 0.3, 0.6 * scale, rng)
        else:
            dome_church(c, x, y, 0.55 * scale, bell_gable=rng.random() < 0.5)
    for mx, ms in mills:
        windmill(c, mx, top_fn(mx) + 6, ms)


def bougainvillea(c, x, y, s, rng):
    for k in range(9):
        c.circle(x + rng.uniform(-18, 18) * s, y + rng.uniform(-12, 18) * s, rng.uniform(5, 9) * s,
                 (226, 70, 150) if k % 3 else (190, 40, 120), ol=None)


def volcano_island(c, x, y, w, h, col=(70, 58, 62), top=(96, 76, 76), ol=(40, 30, 36), smoke=0.0, t=0.0):
    """Nea Kameni: a low, dark, lumpy island in the middle of the caldera."""
    pts = []
    for k in range(13):
        u = k / 12
        bump = math.sin(u * math.pi) ** 0.8 * h * (0.75 + 0.25 * math.sin(u * 17))
        pts.append((x - w / 2 + w * u, y - bump))
    c.poly(pts + [(x + w / 2, y), (x - w / 2, y)], col, ol=ol, w=2)
    c.poly([(x - w * 0.2, y - h * 0.86), (x - w * 0.05, y - h * 1.02), (x + w * 0.12, y - h * 0.86)], top, ol=None)
    if smoke > 0:
        for k in range(4):
            u = (t * 0.15 + k / 4) % 1.0
            c.circle(x - w * 0.05 + 30 * u, y - h - 10 - 60 * u, 8 + 14 * u, mix((240, 240, 240), (200, 200, 210), u),
                     ol=None)


def caique(c, x, y, s=1.0, hull=(40, 110, 190), stripe=(240, 210, 60), trim=(220, 60, 50), bob=0.0, sail=False):
    """A little Greek fishing boat (caique), (x, y) = waterline centre."""
    c.push(x, y + bob, s)
    c.poly([(-90, -30), (90, -36), (70, 8), (-70, 8)], hull)
    c.poly([(-88, -24), (88, -30), (84, -22), (-84, -18)], stripe, ol=None)
    c.poly([(-80, -6), (80, -12), (76, -4), (-76, 0)], trim, ol=None)
    c.poly([(90, -36), (104, -52), (96, -30)], hull, w=2)
    c.rect(-40, -60, 4, -32, WHITE, w=2, r=3)
    c.rect(-34, -54, -24, -44, BLUE_LT, w=1.5)
    c.rect(-16, -54, -6, -44, BLUE_LT, w=1.5)
    c.line([(20, -32), (20, -110)], (110, 80, 60), 3)
    if sail:
        c.poly([(22, -108), (22, -40), (78, -42)], (250, 244, 230), w=2)
    c.line([(20, -110), (-70, -32)], OUT, 1, cap=False)
    c.pop()


def stone_wall(c, x0, x1, y, h=26, col=WHITE, sh=WHITE_SH):
    c.rect(x0, y - h, x1, y, col, w=2.5, r=4)
    c.rect(x0 + 2, y - 6, x1 - 2, y - 1, sh, ol=None)


def cactus(c, x, y, s=1.0):
    """Prickly pear: stacked green paddles with pink fruit."""
    c.push(x, y, s)
    g, g2 = (100, 160, 90), (130, 190, 110)
    for px, py, rx, ry in ((0, -24, 18, 26), (-22, -58, 14, 20), (20, -62, 15, 22), (4, -92, 13, 18)):
        c.ellipse(px, py, rx, ry, g)
        c.ellipse(px - 4, py - 4, rx * 0.5, ry * 0.5, g2, ol=None)
    for fx, fy in ((-28, -76), (-14, -76), (30, -82), (10, -108)):
        c.ellipse(fx, fy, 5, 6, (230, 90, 120), w=1.5)
    c.pop()


# ================================================================ pelican

def _riders(c, riders, bx0, by0, L, t, pouch_pts):
    """Heads (and paws) of the passengers peeking out of the pouch between the open bills."""
    n = len(riders)
    order = sorted(range(n), key=lambda k: riders[k][0] == "pip")
    for k in order:
        who, pal = riders[k]
        px = bx0 + 56 + (L - 60) * k / max(1, n - 1) if n > 1 else bx0 + 80
        py = by0 - 6 + 2 * math.sin(t * 3 + k)
        if who == "pip":
            D.mouse(c, px - 4, py + 26, 0.8, 1, t, eyes="open", proud=True)
        else:
            D.cat(c, px - 30 * 0.6, py + 8, pal, 0.6, 1, "swim", t=t, seed=k * 1.3,
                  mouth=(pal or {}).get("_mouth", 0.0), eyes=(pal or {}).get("_eyes", "open"))
    # lower bill lip across the front
    c.poly(pouch_pts[:8] + [(bx0 + (L - 6) * 0.7, by0 + 26), (bx0, by0 + 22)], PEL_POUCH, ol=None)


PEL_W = (252, 250, 244)
PEL_SH = (222, 220, 222)
PEL_BEAK = (246, 190, 90)
PEL_POUCH = (250, 160, 90)
PEL_LEG = (240, 150, 100)
CAP = (30, 50, 100)


def pelican(c, x, y, s=1.0, face=1, t=0.0, beak=0.0, eyes="open", pouch=0.0, riders=(), walk=0.0, seed=4.0,
            wing_up=0.0):
    """Captain Stelios standing. beak: 0..1 open. pouch: 0..1 bulge. riders: [(pal or 'pip', dx)] in pouch."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    # legs + webbed feet
    for lx, ph in ((-22, 0), (6, math.pi)):
        sw = math.sin(walk + ph) * 10 if walk else 0
        lift = -max(0, math.cos(walk + ph)) * 6 if walk else 0
        c.stroke([(lx, -46), (lx + sw * 0.5, -20 + lift), (lx + sw, lift)], PEL_LEG, 6)
        c.poly([(lx + sw - 12, lift), (lx + sw + 16, lift), (lx + sw + 4, lift - 8)], PEL_LEG, w=2)
    # tail
    c.poly([(-70, -86), (-104, -74), (-72, -64)], PEL_W)
    # body
    c.ellipse(-16, -82, 60, 44, PEL_W)
    c.ellipse(-4, -66, 40, 22, (255, 255, 252), ol=None)
    # wing (folded) with dark flight feathers
    wy = -96 - 30 * wing_up
    c.poly([(-70, wy + 18), (-96, wy + 26), (-82, wy + 6)], (40, 40, 48), w=2)
    c.ellipse(-30, wy + 10, 46, 26, PEL_SH)
    for k in range(3):
        c.arc(-40 + 16 * k, wy + 14, 12, 8, 20, 160, mix(PEL_SH, OUT, 0.35), 2)
    # neck (S-curve)
    nk = [(18, -100), (30, -128), (24, -150), (30, -172)]
    c.stroke(nk, PEL_W, 26)
    c.line(nk, PEL_W, 26)
    hx, hy = 34, -182
    # pouch (behind the lower bill)
    open_a = max(beak * 0.55, 0.72 if riders else 0.0)
    bx0, by0 = hx + 14, hy + 4
    L = 120 if riders else 108
    tip_up = (bx0 + math.cos(-open_a) * L, by0 + math.sin(-open_a) * L)
    low_tip = (bx0 + L * 0.96, by0 + 10)
    bulge = 22 + 46 * pouch
    pouch_pts = [(bx0, by0 + 6)]
    for k in range(1, 10):
        u = k / 10
        pouch_pts.append((bx0 + (L - 6) * u, by0 + 10 + bulge * math.sin(math.pi * u ** 0.85) * (1 - 0.15 * u)))
    pouch_pts.append(low_tip)
    c.poly(pouch_pts + [(bx0 + L * 0.5, by0 + 8)], PEL_POUCH, w=2.5)
    for k in range(2):
        c.arc(bx0 + 40 + 18 * k, by0 + 12 + bulge * 0.5, 14, 6, 200, 340, mix(PEL_POUCH, OUT, 0.3), 1.5)
    # riders peeking out of the pouch (heads and paws over the lower bill)
    if riders:
        _riders(c, riders, bx0, by0, L, t, pouch_pts)
    # lower bill
    c.line([(bx0, by0 + 8), low_tip], mix(PEL_BEAK, OUT, 0.15), 6)
    # head
    c.ellipse(hx, hy, 26, 22, PEL_W)
    # fisherman's cap
    c.ellipse(hx - 4, hy - 16, 26, 12, CAP, w=2.5)
    c.rect(hx - 28, hy - 18, hx + 20, hy - 10, CAP, w=2.5, r=4)
    c.ellipse(hx + 16, hy - 10, 14, 4, (20, 30, 60), w=2)
    c.rect(hx - 26, hy - 14, hx + 18, hy - 11, (200, 200, 210), ol=None)
    # upper bill (hinges open)
    ux = [(bx0 - 4, by0 - 6), tip_up]
    perp = (math.sin(open_a) * 7, math.cos(open_a) * 7)
    c.poly([(bx0 - 6, by0 - 8), (tip_up[0], tip_up[1] - 2), (tip_up[0] + 6, tip_up[1] + 8),
            (bx0 + 4 + perp[0], by0 + perp[1])], PEL_BEAK, w=2.5)
    c.line([(lerp(bx0, tip_up[0], 0.2), lerp(by0, tip_up[1], 0.2) - 1), (tip_up[0] - 8, tip_up[1] - 1)],
           mix(PEL_BEAK, (255, 255, 255), 0.4), 2, cap=False)
    # eye
    ex, ey = hx + 6, hy - 2
    if eyes == "closed":
        c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
    else:
        c.circle(ex, ey, 6.5, (255, 255, 255), w=2)
        c.circle(ex + 1.5, ey, 3.6, (40, 30, 30), ol=None)
        c.circle(ex + 2.5, ey - 1.5, 1.2, (255, 255, 255), ol=None)
    c.arc(ex, ey - 8, 8, 4, 200, 330, OUT, 2)          # bushy brow
    c.pop()


def pelican_fly(c, x, y, s=1.0, face=1, t=0.0, beak=0.0, riders=(), flap_speed=5.0, glide=False, seed=4.0):
    """Captain Stelios in flight: neck tucked, great wings beating. (x, y) = body centre."""
    c.push(x, y, s, flip=face < 0)
    ph = 0.0 if glide else math.sin(t * flap_speed)
    wing_far = [(-10, -20), (-40 - 20 * ph, -110 * (0.35 + 0.65 * ph) - 20), (-110, -60 * ph - 40), (-60, -10)]
    c.poly(wing_far, mix(PEL_SH, (180, 180, 190), 0.3))
    c.poly([wing_far[1], wing_far[2], (-80 - 30 * ph, -40 * ph - 30)], (40, 40, 48), w=2)
    # trailing legs + tail
    c.stroke([(-60, 6), (-104, 14)], PEL_LEG, 5)
    c.poly([(-104, 8), (-120, 4), (-116, 20)], PEL_LEG, w=1.5)
    c.poly([(-70, -10), (-108, -16), (-104, 2), (-72, 6)], PEL_W)
    c.ellipse(-6, -2, 74, 34, PEL_W)
    c.ellipse(4, 10, 50, 16, (255, 255, 252), ol=None)
    # head on tucked neck
    hx, hy = 70, -22
    c.ellipse(52, -12, 26, 20, PEL_W, ol=None)
    bx0, by0 = hx + 14, hy + 4
    L = 124 if riders else 112
    open_a = max(beak * 0.4, 0.72 if riders else 0.0)
    tip_up = (bx0 + math.cos(-open_a) * L, by0 + math.sin(-open_a) * L)
    low_tip = (bx0 + L * 0.96, by0 + 10)
    bulge = 62 if riders else 24
    pouch_pts = [(bx0, by0 + 6)]
    for k in range(1, 10):
        u = k / 10
        pouch_pts.append((bx0 + (L - 6) * u, by0 + 10 + bulge * math.sin(math.pi * u ** 0.85) * (1 - 0.15 * u)))
    pouch_pts.append(low_tip)
    c.poly(pouch_pts + [(bx0 + L * 0.5, by0 + 8)], PEL_POUCH, w=2.5)
    if riders:
        _riders(c, riders, bx0, by0, L, t, pouch_pts)
    c.line([(bx0, by0 + 8), low_tip], mix(PEL_BEAK, OUT, 0.15), 6)
    c.ellipse(hx, hy, 26, 22, PEL_W)
    c.ellipse(hx - 4, hy - 16, 26, 12, CAP, w=2.5)
    c.rect(hx - 28, hy - 18, hx + 20, hy - 10, CAP, w=2.5, r=4)
    c.ellipse(hx + 16, hy - 10, 14, 4, (20, 30, 60), w=2)
    c.rect(hx - 26, hy - 14, hx + 18, hy - 11, (200, 200, 210), ol=None)
    perp = (math.sin(open_a) * 7, math.cos(open_a) * 7)
    c.poly([(bx0 - 6, by0 - 8), (tip_up[0], tip_up[1] - 2), (tip_up[0] + 6, tip_up[1] + 8),
            (bx0 + 4 + perp[0], by0 + perp[1])], PEL_BEAK, w=2.5)
    ex, ey = hx + 6, hy - 2
    if D.blink(t, seed):
        c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
    else:
        c.circle(ex, ey, 6.5, (255, 255, 255), w=2)
        c.circle(ex + 1.5, ey, 3.6, (40, 30, 30), ol=None)
        c.circle(ex + 2.5, ey - 1.5, 1.2, (255, 255, 255), ol=None)
    c.arc(ex, ey - 8, 8, 4, 200, 330, OUT, 2)
    # near wing
    wing = [(-30, -10), (-10 - 30 * ph, -130 * (0.3 + 0.7 * ph) - 10), (-120, -80 * ph - 20), (-70, 4)]
    c.poly(wing, PEL_W)
    c.poly([wing[1], wing[2], (-90 - 30 * ph, -60 * ph - 20)], (40, 40, 48), w=2)
    for k in range(3):
        u = (k + 1) / 4
        a = (lerp(wing[0][0], wing[1][0], u), lerp(wing[0][1], wing[1][1], u))
        b = (lerp(wing[3][0], wing[2][0], u), lerp(wing[3][1], wing[2][1], u))
        c.line([a, (lerp(a[0], b[0], 0.5), lerp(a[1], b[1], 0.5))], PEL_SH, 2)
    c.pop()


# ================================================================ donkey

DONK = (150, 136, 130)
DONK_DK = (110, 98, 96)
DONK_LT = (226, 218, 208)
BLANKET = (206, 60, 60)
BAG = (236, 180, 80)


def donkey(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, mouth=0.0, eyes="open", bags=True, rider=None,
           head_dy=0.0, ears=0.0, seed=6.0, tired=0.0):
    """Fasolaki. rider: callable(c, x, y) drawn sitting on the saddle (local coords). tired: 0..1 droop."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    by = -104
    bob = math.sin(walk * 2) * 2.5 if walk else 0
    # tail
    tw = math.sin(t * 2.5 + seed) * 0.4
    tp = [(-70, by - 6), (-86 + 6 * tw, by + 20), (-90 + 10 * tw, by + 50)]
    c.stroke(tp, DONK, 6)
    c.ellipse(-90 + 10 * tw, by + 58, 7, 12, DONK_DK, w=2)

    def leg(lx, ph, col):
        if walk:
            sw = math.sin(walk + ph) * 14
            lift = -max(0.0, math.cos(walk + ph)) * 8
        else:
            sw, lift = 0, 0
        c.stroke([(lx, by + 18), (lx + sw * 0.4, by + 66 + lift * 0.5), (lx + sw, lift - 6)], col, 12)
        c.rect(lx + sw - 8, lift - 10, lx + sw + 8, lift, (60, 50, 50), w=2, r=2)

    leg(-48, math.pi, DONK_DK)
    leg(42, 0, DONK_DK)
    # body
    c.ellipse(0, by + bob, 76, 40, DONK)
    c.ellipse(6, by + 20 + bob, 52, 14, DONK_LT, ol=None)
    leg(-36, 0, DONK)
    leg(54, math.pi, DONK)
    # blanket + saddlebags
    c.poly([(-40, by - 36 + bob), (34, by - 36 + bob), (40, by + 8 + bob), (-46, by + 8 + bob)], BLANKET, w=2.5)
    c.line([(-44, by - 2 + bob), (38, by - 2 + bob)], (250, 210, 80), 3, cap=False)
    c.line([(-42, by - 26 + bob), (36, by - 26 + bob)], (60, 110, 190), 3, cap=False)
    for k in range(7):
        c.line([(-46 + 14 * k, by + 8 + bob), (-46 + 14 * k, by + 16 + bob)], (250, 210, 80), 2.5)
    if bags:
        c.rect(-26, by - 14 + bob, 14, by + 30 + bob, BAG, w=2.5, r=6)
        for k in range(3):
            c.line([(-24, by - 4 + 12 * k + bob), (12, by - 4 + 12 * k + bob)], (200, 120, 60), 3, cap=False)
        c.rect(-28, by - 18 + bob, 16, by - 10 + bob, (150, 90, 50), w=2, r=3)
    # neck + head
    droop = 26 * tired + head_dy
    nx, ny = 56, by - 18 + bob
    hx, hy = 92, by - 56 + droop + bob
    c.poly([(nx - 22, ny + 22), (nx - 16, ny - 18), (hx - 14, hy - 10), (hx + 6, hy + 12), (nx + 22, ny + 18)], DONK)
    # mane
    for k in range(6):
        u = k / 5
        mx, my = lerp(nx - 18, hx - 14, u), lerp(ny - 16, hy - 14, u)
        c.ellipse(mx - 2, my - 4, 7, 9, DONK_DK, ol=None)
    # ears (long!)
    ea = ears * 0.5 + tired * 0.6
    for k, (ex, sw) in enumerate(((hx - 14, -0.15), (hx - 2, 0.25))):
        a = -1.75 + sw + ea + 0.08 * math.sin(t * 1.7 + k)
        tip = (ex + math.cos(a) * 58, hy - 10 + math.sin(a) * 58)
        mid = (ex + math.cos(a) * 30, hy - 10 + math.sin(a) * 30)
        perp = (-math.sin(a) * 11, math.cos(a) * 11)
        c.poly([(ex - 7, hy - 8), (mid[0] - perp[0], mid[1] - perp[1]), tip, (mid[0] + perp[0], mid[1] + perp[1]),
                (ex + 7, hy - 10)], DONK)
        c.poly([(mid[0] - perp[0] * 0.5, mid[1] - perp[1] * 0.5), tip, (mid[0] + perp[0] * 0.5, mid[1] + perp[1] * 0.5)],
               (236, 190, 190), ol=None)
        c.line([tip, (lerp(mid[0], tip[0], 0.6), lerp(mid[1], tip[1], 0.6))], (60, 50, 50), 5)
    # head
    c.ellipse(hx, hy, 30, 24, DONK)
    c.ellipse(hx + 30, hy + 14, 24, 18, DONK_LT)
    c.circle(hx + 40, hy + 8, 3, (90, 70, 70), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 34, hy + 26, 10, 3 + 6 * mouth, (120, 40, 50), w=2)
    else:
        c.arc(hx + 34, hy + 22, 10, 5, 20, 160, OUT, 2)
    # forelock
    c.poly([(hx - 18, hy - 20), (hx - 4, hy - 30), (hx + 6, hy - 18), (hx - 6, hy - 12)], DONK_DK, ol=None)
    ex, ey = hx + 6, hy - 4
    if eyes == "closed":
        c.arc(ex, ey, 7, 5, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 7, 7, 200, 340, OUT, 2.5)
    else:
        c.ellipse(ex, ey, 7, 8.5, (255, 255, 255), w=2)
        c.ellipse(ex + 1.5, ey + 0.5, 4.5, 5.5, (60, 40, 40), ol=None)
        c.circle(ex + 2.5, ey - 2, 1.5, (255, 255, 255), ol=None)
        if tired > 0.3:
            c.line([(ex - 8, ey - 3), (ex + 8, ey - 3)], DONK, 4, cap=False)   # heavy lids
    # bridle with a little bell
    c.line([(hx - 18, hy + 8), (hx + 14, hy + 20)], (200, 60, 60), 3)
    c.line([(hx - 20, hy + 14), (nx - 10, ny + 10)], (60, 110, 190), 3)
    c.circle(nx - 2, ny + 22, 6, (230, 190, 70), w=2)
    if rider is not None:
        rider(c, -2, by - 34 + bob)
    c.pop()


def bags_bundle(c, x, y, s=1.0):
    """The woven saddlebags, carried by a cat (drawn over the back)."""
    c.push(x, y, s)
    c.rect(-26, -22, 22, 16, BAG, w=2.5, r=7)
    for k in range(3):
        c.line([(-24, -12 + 10 * k), (20, -12 + 10 * k)], (200, 120, 60), 3, cap=False)
    c.rect(-28, -26, 24, -18, (150, 90, 50), w=2, r=3)
    c.pop()


# ================================================================ food

def fritter(c, x, y, s=1.0):
    c.push(x, y, s)
    c.ellipse(0, 0, 13, 9, (214, 90, 50), w=1.8)
    c.ellipse(-3, -2, 6, 3, (240, 140, 70), ol=None)
    c.circle(4, 1, 2, (90, 150, 70), ol=None)
    c.pop()


def octopus(c, x, y, s=1.0, t=0.0, col=(226, 110, 120), dry=True, sway=0.0, stretch=1.0):
    """An octopus hanging by its head (dry=True) from a line at (x, y)."""
    c.push(x, y, s)
    for k in range(8):
        u = (k - 3.5) / 3.5
        base = (u * 14, 30)
        pts = [base]
        for j in range(1, 6):
            v = j / 5
            pts.append((u * 14 + u * 10 * v + sway * 14 * v * v + 4 * math.sin(t * 2 + k + v * 3),
                        30 + 56 * v * stretch))
        c.stroke(pts, col, 6 - 1.0 * abs(u))
        for j in (2, 3, 4):
            c.circle(pts[j][0] + 2, pts[j][1], 1.6, (255, 220, 210), ol=None)
    c.ellipse(0, 14, 18, 24, col)
    c.ellipse(-5, 8, 6, 9, mix(col, (255, 255, 255), 0.35), ol=None)
    c.arc(-6, 20, 4, 3, 20, 160, OUT, 1.8)
    c.arc(6, 20, 4, 3, 20, 160, OUT, 1.8)
    c.pop()


def grill(c, x, y, t=0.0, smoke=True):
    c.push(x, y)
    c.rect(-60, -50, 60, 0, (70, 70, 80), r=4)
    c.rect(-64, -58, 64, -48, (110, 110, 120), r=3)
    for k in range(7):
        c.circle(-48 + 16 * k, -58, 5, (255, 120 + 30 * (k % 2), 50), ol=None)
    for k in range(9):
        c.line([(-58 + 14.5 * k, -66), (-58 + 14.5 * k, -56)], (40, 40, 44), 2, cap=False)
    c.line([(-62, -62), (62, -62)], (40, 40, 44), 2, cap=False)
    for k, ox in enumerate((-30, 20)):
        c.push(ox, -68)
        for j in range(4):
            c.stroke([(0, 0), (14 + 6 * j, -4 + 3 * j), (26 + 6 * j, 2 + 2 * j)], (190, 80, 70), 5)
        c.pop()
    if smoke:
        for k in range(4):
            u = (t * 0.45 + k / 4) % 1.0
            c.circle(-20 + 20 * k + 10 * math.sin(t * 2 + k), -80 - 90 * u, 10 + 16 * u,
                     mix((245, 245, 245), (220, 220, 225), u), ol=None)
    c.pop()


def table(c, x, y, w=150, cloth=(250, 250, 250), check=BLUE):
    """Taverna table with a blue-and-white checked cloth, (x, y) = floor centre."""
    c.rect(x - w / 2 + 10, y - 60, x - w / 2 + 18, y, (110, 80, 60), w=2)
    c.rect(x + w / 2 - 18, y - 60, x + w / 2 - 10, y, (110, 80, 60), w=2)
    c.rect(x - w / 2, y - 76, x + w / 2, y - 50, cloth, w=2.5, r=3)
    for k in range(int(w / 14)):
        if k % 2 == 0:
            c.rect(x - w / 2 + 14 * k, y - 63, x - w / 2 + 14 * k + 14, y - 51, check, ol=None)
            c.rect(x - w / 2 + 14 * k + 7, y - 75, x - w / 2 + 14 * k + 14 + 7, y - 64,
                   mix(check, (255, 255, 255), 0.4), ol=None)


def chair(c, x, y, face=1):
    c.push(x, y, 1.0, flip=face < 0)
    c.rect(-14, -40, 14, -34, BLUE_LT, w=2)
    c.line([(-12, -34), (-12, 0)], BLUE_LT, 4)
    c.line([(12, -34), (12, 0)], BLUE_LT, 4)
    c.line([(-12, -40), (-14, -84)], BLUE_LT, 4)
    c.line([(-14, -64), (-14, -80)], BLUE_LT, 4)
    c.pop()


def plate(c, x, y, food="fritters", t=0.0, n=4):
    c.ellipse(x, y, 34, 9, (255, 255, 255), w=2)
    c.ellipse(x, y, 24, 5, (220, 230, 240), ol=None)
    if food == "fritters":
        for k in range(n):
            fritter(c, x - 16 + 11 * k, y - 4 - 4 * (k % 2), 0.75)
    elif food == "octopus":
        for j in range(3):
            c.stroke([(x - 18 + 10 * j, y - 2), (x - 6 + 10 * j, y - 12), (x + 6 + 10 * j, y - 6)], (190, 80, 70), 5)
        c.ellipse(x + 18, y - 6, 5, 3, (250, 230, 120), w=1.2)


# ================================================================ crowd

CROWD_COLS = [(70, 46, 70), (60, 40, 64), (84, 52, 74), (52, 36, 58)]


def person(c, x, y, s=1.0, col=(60, 40, 64), clap=0.0, t=0.0, seed=0, hat=False, kid=False):
    """A backlit sunset-watcher (silhouette). clap: 0..1 arms up clapping."""
    c.push(x, y, s * (0.7 if kid else 1.0))
    c.rect(-16, -70, 16, 0, col, ol=None, r=8)
    c.circle(0, -84, 13, col, ol=None)
    if hat:
        c.ellipse(0, -94, 20, 5, col, ol=None)
        c.ellipse(0, -98, 11, 8, col, ol=None)
    if clap > 0:
        k = abs(math.sin(t * 11 + seed))
        for side in (-1, 1):
            hx = side * (4 + 10 * k)
            c.line([(side * 12, -62), (hx, -108)], col, 7)
            c.circle(hx, -110, 5, col, ol=None)
    c.pop()


# ================================================================ puzzle

def puzzle_art(w, h, sun=False, hole=True):
    """The jigsaw picture: Oia at sunset. Returns an RGB PIL image of w x h (output px) at SS."""
    c = Canvas(D.gradient(w * SS, h * SS, [(0, (250, 150, 110)), (0.38, (255, 200, 130)), (0.5, (255, 220, 150)),
                                           (0.52, (40, 90, 170)), (1, (20, 60, 130))]), size=(w, h))
    sx, sy, r = w * 0.62, h * 0.42, h * 0.11
    if sun:
        c.glow(sx, sy, r * 2.6, r * 2.6, (255, 240, 170), (255, 205, 135), steps=8)
        c.circle(sx, sy, r, (255, 240, 150), ol=None)
        for k in range(10):
            yy = h * 0.53 + k * h * 0.03
            c.line([(sx - r * (1.3 - 0.06 * k), yy), (sx + r * (1.3 - 0.06 * k), yy)], (255, 210, 120), 2, cap=False)
    volcano_island(c, w * 0.8, h * 0.52, w * 0.22, h * 0.05, col=(90, 60, 80), top=(110, 76, 90), ol=None)

    def top(x):
        return h * 0.36 + (x / w) * h * 0.25

    c.push(0, 0, 1.0)
    cliff_band(c, -10, w * 0.5, lambda x: h * 0.62 + (x / w) * h * 0.18, h + 10, seed=2)
    c.pop()
    rng = np.random.default_rng(9)
    for k in range(18):
        x = rng.uniform(-10, w * 0.45)
        y = h * 0.66 + (x / w) * h * 0.18 + rng.uniform(-4, 30)
        cube_house(c, x, y, rng.uniform(18, 34), rng.uniform(14, 26), rng, door=False, lw=1.2)
    dome_church(c, w * 0.22, h * 0.72, 0.42, bell_gable=False)
    windmill(c, w * 0.08, h * 0.66, 0.35, 0.3)
    # jigsaw seams
    nx, ny = 8, 5
    for i in range(1, nx):
        x = w * i / nx
        c.line([(x, 0), (x, h)], (0, 0, 0), 1, cap=False)
    for j in range(1, ny):
        y = h * j / ny
        c.line([(0, y), (w, y)], (0, 0, 0), 1, cap=False)
    img = c.img
    if hole:
        hole_img = Canvas(img)
        # the piece around the sun: cell (4, 1) -> x in [w*4/8, w*5/8], y in [h/5, 2h/5]  (+ tabs)
        x0, x1, y0, y1 = w * 4 / 8, w * 5 / 8, h * 0.315, h * 0.525
        x0, x1 = x0 + w * 0.0625, x1 + w * 0.0625
        dark = (90, 58, 46)
        hole_img.rect(x0, y0, x1, y1, dark, ol=None)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        hole_img.circle(cx, y0, h * 0.035, dark, ol=None)
        hole_img.circle(x1, cy, h * 0.035, dark, ol=None)
        hole_img.circle(x0, cy, h * 0.035, img.getpixel((int(x0 * SS - 5 * SS), int(cy * SS))) if False else dark, ol=None)
    return img


def piece(c, x, y, s=1.0, rot=0.0):
    """The missing sun piece (a jigsaw piece with half a sun)."""
    c.push(x, y, s)
    col = (255, 205, 135)
    c.rect(-22, -18, 22, 18, col, w=2)
    c.circle(0, -18, 7, col, w=2)
    c.circle(22, 0, 7, col, w=2)
    c.rect(-20, -16, 20, 16, col, ol=None)
    c.circle(0, 0, 11, (255, 240, 150), ol=None)
    c.pop()
