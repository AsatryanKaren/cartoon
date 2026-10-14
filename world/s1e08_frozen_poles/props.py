"""Episode 8 props: Pebble the penguin, Bjorn the polar bear, Arctic animals, ice and diagrams.

Flat outlined style with draw.Canvas primitives. Characters are drawn in local space with the
origin between the feet, facing right (face=-1 mirrors them).
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K

ICE = (236, 246, 255)
ICE_SH = (196, 222, 242)
ICE_D = (150, 190, 226)
SEA = (40, 92, 160)
SEA_D = (26, 64, 124)
SNOW = (250, 252, 255)


# ================================================================== Pebble the penguin

PEB = dict(black=(38, 42, 58), white=(252, 252, 250), feet=(244, 150, 160), beak=(52, 46, 56),
           beak2=(226, 90, 70), cheek=(255, 170, 180))


def pebble(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", flap=0.0, waddle=0.0, hot=0.0,
           slide=0.0, seed=1.0, look=(0.0, 0.0)):
    """Pebble, a little Adelie penguin. (x, y) = feet; about 135*s tall.
    flap: 0..1 flippers wave; waddle: phase for rocking; hot: 0..1 red face, sweat and steam;
    slide: 1 = lying on the belly (tobogganing)."""
    p = PEB
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    blk = mix(p["black"], (150, 40, 50), 0.35 * hot)
    wht = mix(p["white"], (255, 170, 150), 0.45 * hot)
    c.push(x, y, s, flip=face < 0)
    if slide > 0.5:
        # tobogganing: lying flat, flippers back, feet kicking
        kick = math.sin(t * 16) * 4
        for fx in (-62, -54):
            c.ellipse(fx, -8 + kick * (1 if fx < -58 else -1), 10, 5, p["feet"], w=2)
        c.ellipse(-4, -24, 60, 24, blk)
        c.ellipse(0, -14, 50, 12, wht, ol=None)
        c.poly([(-10, -40), (-40, -50), (-24, -34)], blk, w=2)
        hx, hy = 52, -34
        c.circle(hx, hy, 22, blk)
        c.circle(hx + 6, hy - 6, 7, wht, ol=None)
        c.circle(hx + 7, hy - 6, 3.6, (20, 20, 30), ol=None)
        c.poly([(hx + 18, hy), (hx + 36, hy + 4), (hx + 18, hy + 8)], p["beak"], w=1.5)
        c.pop()
        return
    rock = math.sin(waddle) * 5 if waddle else 0.0
    for fx, ph in ((-12, 0), (12, math.pi)):
        lift = -max(0.0, math.sin(waddle + ph)) * 5 if waddle else 0
        c.ellipse(fx + 6, -3 + lift, 13, 5.5, p["feet"], w=2)
    # far flipper
    fa = math.sin(t * 14) * flap
    c.poly([(rock - 18, -84), (rock - 44, -46 - 30 * fa), (rock - 26, -44)], blk, w=2)
    c.ellipse(rock, -52, 36, 50, blk)
    c.ellipse(rock + 8, -46, 26, 40, wht, ol=None)
    # near flipper
    c.poly([(rock + 2, -82), (rock - 22, -38 - 34 * fa), (rock - 4, -40)], blk, w=2)
    hx, hy = rock * 1.4 + 6, -106
    c.circle(hx, hy, 28, blk)
    c.ellipse(hx + 6, hy + 18, 18, 8, wht, ol=None)
    c.ellipse(hx + 4, hy + 9, 8, 4, p["cheek"] if not hot else (255, 110, 110), ol=None)
    # eye with the white Adelie eye ring
    ex, ey = hx + 12, hy - 6
    c.circle(ex, ey, 8.5, (255, 255, 255), ol=None)
    if eyes == "closed":
        c.arc(ex, ey, 5, 3.5, 20, 160, (20, 20, 30), 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 5, 5, 200, 340, (20, 20, 30), 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.circle(ex + 1 + look[0] * 2, ey + look[1] * 2, 4 * big, (20, 20, 30), ol=None)
        c.circle(ex + 2 + look[0] * 2, ey - 1.5 + look[1] * 2, 1.4, (255, 255, 255), ol=None)
    # beak (opens with the voice)
    op = 10 * clamp(mouth)
    bx, by = hx + 24, hy + 2
    c.poly([(bx - 4, by - 6), (bx + 20, by - 1 - op * 0.3), (bx - 2, by + 1)], p["beak"], w=1.5)
    c.poly([(bx - 2, by + 1), (bx + 16, by + 3 + op), (bx - 4, by + 6)], p["beak"], w=1.5)
    if op > 2:
        c.poly([(bx, by + 1), (bx + 12, by + op * 0.6 + 1), (bx, by + 4)], p["beak2"], ol=None)
    if hot > 0.05:
        rng = np.random.default_rng(int(seed * 10) + 3)
        for k in range(4):
            u = (t * 1.2 + k / 4) % 1
            sx = hx + rng.uniform(-26, 20)
            c.ellipse(sx, hy - 10 + 40 * u, 3.5, 5.5, (150, 210, 255), w=1.5)
        for k in range(3):
            u = (t * 0.8 + k / 3) % 1
            sx = hx - 16 + 16 * k + 6 * math.sin(t * 4 + k)
            c.arc(sx, hy - 40 - 40 * u, 7, 10, 90, 270, mix((255, 255, 255), (200, 200, 210), u), 3 * hot)
    c.pop()


def penguin_icon(c, x, y, r, t=0.0):
    """Little penguin for cards (centred at (x, y), fits radius r)."""
    pebble(c, x - r * 0.05, y + r * 0.78, r / 92, 1, t, eyes="happy")


# ===================================================================== Bjorn the polar bear

BEAR = dict(fur=(250, 248, 238), shade=(222, 218, 200), dark=(196, 190, 170), nose=(30, 28, 36),
            eye=(30, 28, 36), pad=(70, 64, 70))


def bjorn(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), wave=0.0, seed=3.0,
          tint=None):
    """Bjorn the polar bear, sitting (side view, facing right). (x, y) = ground under him.
    About 330*s tall to the ears; head at about (+70, -250)*s. wave 0..1 lifts his near paw."""
    p = BEAR
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    breathe = math.sin(t * 1.6 + seed) * 2
    # back haunch + far leg
    c.ellipse(-50, -70, 92, 72, p["shade"])
    c.ellipse(-4, -14, 40, 16, p["shade"])
    # body
    c.ellipse(10, -140 - breathe, 84, 110, p["fur"])
    c.ellipse(-60, -62, 70, 58, p["fur"], ol=None)
    c.arc(-60, -62, 70, 58, 110, 250, OUT, 3)
    # hind foot
    c.ellipse(-10, -12, 46, 16, p["fur"])
    for k in range(3):
        c.circle(28 + k * 0, -16 + k * 8 - 8, 0.1, p["pad"], ol=None)
    # far front leg
    c.rect(38, -130, 74, -8, p["shade"], r=16)
    c.ellipse(64, -8, 24, 10, p["shade"])
    # near front leg (can wave)
    if wave > 0.01:
        a = math.radians(lerp(100, -40, ease(wave)) + 12 * math.sin(t * 8) * wave)
        sx, sy = 20, -150
        ex, ey = sx + math.cos(a) * 110, sy - math.sin(a) * 110 + 0
        ex2, ey2 = sx + math.cos(math.radians(-80)) * 0, sy
        c.stroke([(sx, sy), (ex, ey)], p["fur"], 36)
        c.circle(ex, ey, 22, p["fur"])
        for k in range(3):
            pa = a + math.radians(-30 + 30 * k)
            c.circle(ex + math.cos(pa) * 12, ey - math.sin(pa) * 12, 4.5, p["pad"], ol=None)
    else:
        c.rect(6, -136, 46, -6, p["fur"], r=18)
        c.ellipse(36, -6, 28, 11, p["fur"])
        for k in range(3):
            c.line([(46 + k * 7, -12), (48 + k * 7, -2)], p["dark"], 2)
    # head
    hx, hy = 72 + 3 * math.sin(t * 0.9 + seed), -246 - breathe
    for ex in (-30, 6):
        c.circle(hx + ex, hy - 40, 15, p["fur"])
        c.circle(hx + ex, hy - 39, 8, p["dark"], ol=None)
    c.ellipse(hx, hy, 52, 46, p["fur"])
    c.ellipse(hx + 48, hy + 12, 40, 26, p["fur"])
    c.ellipse(hx - 4, hy + 8, 44, 34, p["fur"], ol=None)
    c.ellipse(hx + 84, hy + 4, 11, 9, p["nose"], ol=None)
    c.ellipse(hx + 86, hy + 1, 4, 2.5, (120, 120, 130), ol=None)
    ex, ey = hx + 28, hy - 12
    if eyes == "closed":
        c.arc(ex, ey, 7, 5, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 7, 7, 200, 340, OUT, 3)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        c.circle(ex + look[0] * 2, ey + look[1] * 2, 5.5 * big, p["eye"], ol=None)
        c.circle(ex + 1.5 + look[0] * 2, ey - 2 + look[1] * 2, 1.8, (255, 255, 255), ol=None)
    # mouth
    if mouth > 0.05:
        hh = 3 + 14 * mouth
        c.ellipse(hx + 58, hy + 30 + hh * 0.4, 14 + 3 * mouth, hh, D.MOUTH, w=2.5)
        c.ellipse(hx + 58, hy + 30 + hh * 0.8, 8, 2 + 3 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 62, hy + 24, 16, 8, 20, 160, OUT, 3)
    c.pop()


def bear_icon(c, x, y, r, t=0.0):
    """Polar bear head for cards (centred at (x, y), radius r)."""
    p = BEAR
    s = r / 50
    c.push(x, y, s)
    for ex in (-30, 30):
        c.circle(ex, -32, 14, p["fur"])
        c.circle(ex, -31, 7, p["dark"], ol=None)
    c.ellipse(0, 0, 44, 40, p["fur"])
    c.ellipse(0, 16, 22, 16, (255, 255, 255))
    c.ellipse(0, 8, 9, 7, p["nose"], ol=None)
    c.arc(0, 18, 8, 6, 20, 160, OUT, 2.5)
    for ex in (-16, 16):
        c.circle(ex, -8, 4.5, p["eye"], ol=None)
        c.circle(ex + 1.5, -9.5, 1.4, (255, 255, 255), ol=None)
    c.pop()


# ================================================================== more Arctic animals

def arctic_fox(c, x, y, s=1.0, face=1, t=0.0, peek=1.0):
    """A small white Arctic fox sitting, big fluffy tail. (x, y) = ground. peek<1 sinks it into snow."""
    fur, sh = (252, 252, 250), (214, 220, 232)
    c.push(x, y + 120 * (1 - peek) * s, s, flip=face < 0)
    sw = math.sin(t * 2.2) * 8
    c.ellipse(-46, -20 - sw * 0.3, 40, 18, fur)
    c.ellipse(-70, -26 - sw * 0.5, 16, 12, fur, ol=None)
    c.ellipse(-4, -40, 30, 40, fur)
    c.ellipse(6, -34, 18, 26, sh, ol=None)
    c.rect(4, -40, 18, -2, fur, r=6)
    hx, hy = 14, -88
    c.poly([(hx - 22, hy - 8), (hx - 18, hy - 38), (hx - 4, hy - 16)], fur, w=2.5)
    c.poly([(hx + 4, hy - 18), (hx + 14, hy - 40), (hx + 20, hy - 10)], fur, w=2.5)
    c.ellipse(hx, hy, 24, 20, fur)
    c.poly([(hx + 14, hy - 6), (hx + 44, hy + 6), (hx + 14, hy + 14)], fur, w=2.5)
    c.circle(hx + 44, hy + 6, 4, (30, 28, 36), ol=None)
    c.circle(hx + 12, hy - 4, 3.5, (30, 28, 36), ol=None)
    c.circle(hx + 13, hy - 5, 1.2, (255, 255, 255), ol=None)
    c.pop()


def walrus(c, x, y, s=1.0, face=1, t=0.0, seed=0.0):
    """A walrus lying on an ice floe. (x, y) = ground under the belly."""
    br, br_d, tusk = (176, 120, 96), (146, 94, 74), (252, 246, 226)
    c.push(x, y, s, flip=face < 0)
    bob = math.sin(t * 1.5 + seed) * 2
    c.poly([(-120, -10), (-150, -24), (-146, 0), (-110, 0)], br_d, w=2.5)
    c.ellipse(-30, -40, 100, 42, br)
    c.ellipse(60, -64 + bob, 46, 40, br)
    c.ellipse(86, -56 + bob, 24, 18, (196, 146, 120))
    for dx in (-8, 8):
        c.poly([(86 + dx - 4, -46 + bob), (86 + dx + 4, -46 + bob), (88 + dx * 1.2, 0 + bob)], tusk, w=2)
    for dy in (-60, -54, -48):
        c.circle(96, dy + bob, 1.5, OUT, ol=None)
    c.circle(66, -80 + bob, 4, (30, 24, 24), ol=None)
    c.ellipse(20, -6, 26, 9, br_d)
    c.pop()


def seal(c, x, y, s=1.0, face=1, t=0.0, head_only=False, seed=0.0):
    """A grey seal: lying on the ice, or just its head out of the water (head_only)."""
    g, gd = (150, 156, 170), (120, 126, 142)
    c.push(x, y, s, flip=face < 0)
    if head_only:
        bob = math.sin(t * 2 + seed) * 4
        c.ellipse(0, -18 + bob, 26, 24, g)
        c.ellipse(16, -12 + bob, 14, 10, (176, 182, 194), ol=None)
        c.circle(6, -26 + bob, 4.5, (24, 24, 30), ol=None)
        c.circle(7, -27.5 + bob, 1.5, (255, 255, 255), ol=None)
        c.circle(28, -16 + bob, 3, (24, 24, 30), ol=None)
        c.pop()
        return
    c.poly([(-70, -10), (-100, -26), (-96, 2), (-64, 0)], gd, w=2.5)
    c.ellipse(-10, -24, 70, 26, g)
    c.ellipse(52, -38, 26, 22, g)
    c.ellipse(70, -34, 12, 9, (176, 182, 194), ol=None)
    c.circle(54, -46, 4, (24, 24, 30), ol=None)
    c.circle(80, -38, 3, (24, 24, 30), ol=None)
    rng = np.random.default_rng(int(seed) + 2)
    for _ in range(6):
        c.circle(rng.uniform(-60, 30), rng.uniform(-36, -14), rng.uniform(2, 4), gd, ol=None)
    c.pop()


# ============================================================================ ice + snow

def floe(c, x, y, w, h, seed=0, col=ICE, side=ICE_SH):
    """A flat floating ice floe seen from the side: top surface ellipse-ish + a thick edge."""
    rng = np.random.default_rng(seed)
    n = 14
    top = []
    for i in range(n):
        a = math.pi + math.pi * i / (n - 1)
        top.append((x + math.cos(a) * w * rng.uniform(0.92, 1.0), y + math.sin(a) * h * rng.uniform(0.8, 1.0)))
    edge = [(x + w, y), (x + w * 0.96, y + h * 0.7), (x - w * 0.96, y + h * 0.7), (x - w, y)]
    c.poly([(x - w, y)] + edge[::-1][1:] + [(x + w, y)], side, w=3)
    c.poly(top + [(x + w, y + h * 0.15), (x - w, y + h * 0.15)], col, w=3)


def berg(c, x, base, w, h, seed=0, col=ICE, shade=ICE_SH):
    """A jagged iceberg / ice mountain."""
    rng = np.random.default_rng(seed)
    pts = [(x - w, base)]
    k = 7
    for i in range(1, k):
        u = i / k
        px = x - w + 2 * w * u
        py = base - h * math.sin(math.pi * u) ** 0.7 * rng.uniform(0.75, 1.05)
        pts.append((px, py))
    pts.append((x + w, base))
    c.poly(pts, col, w=3)
    sh = [pts[i] for i in range(len(pts) // 2, len(pts))]
    c.poly([(sh[0][0], sh[0][1])] + sh[1:] + [(sh[0][0] + 10, base)], shade, ol=None)


def snowfall(c, t, box=(0, 0, W, H), n=60, seed=1, speed=40.0, size=(1.5, 3.5), k=1.0):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    for _ in range(n):
        px, py = rng.uniform(0, 1), rng.uniform(0, 1)
        r = rng.uniform(*size)
        sp = speed * rng.uniform(0.6, 1.4)
        y = y0 + ((py * (y1 - y0) + t * sp) % (y1 - y0))
        x = x0 + ((px * (x1 - x0) + 14 * math.sin(t * 0.8 + py * 9)) % (x1 - x0))
        c.circle(x, y, r * k, (255, 255, 255), ol=None)


def ice_cap(c, x, y, r, lon0, lat0, north=True, edge=74.0, roll=0.0, col=(246, 250, 255), seed=0):
    """White polar ice drawn over a kit globe(c, x, y, r, lon0, lat0, roll=roll).
    Points of the cap edge on the far side are pushed onto the globe's rim."""
    pts = []
    rng = np.random.default_rng(seed + (1 if north else 2))
    wob = rng.uniform(-2.5, 2.5, 36)
    for i, lon in enumerate(range(-180, 180, 10)):
        lat = (edge + wob[i]) * (1 if north else -1)
        sx, sy, vis = K.globe_xy(x, y, r, lon, lat, lon0, lat0, roll)
        if not vis:
            dx, dy = sx - x, sy - y
            d = math.hypot(dx, dy) or 1
            sx, sy = x + dx / d * r, y + dy / d * r
        pts.append((sx, sy))
    # is the pole itself visible? if not the cap is a sliver along the rim
    px, py, pvis = K.globe_xy(x, y, r, 0, 90 if north else -90, lon0, lat0, roll)
    if not pvis:
        dx, dy = px - x, py - y
        d = math.hypot(dx, dy) or 1
        # sort the rim-pushed points by angle so the polygon hugs the rim
        ang0 = math.atan2(dy, dx)
        pts.sort(key=lambda p: ((math.atan2(p[1] - y, p[0] - x) - ang0 + math.pi) % (2 * math.pi)))
    c.poly(pts, col, ol=None)


def pole_pin(c, x, y, k=1.0, col=(226, 56, 60)):
    """A little flag pin standing on a point (x, y)."""
    if k <= 0.01:
        return
    c.push(x, y, K.pop(k))
    c.line([(0, 0), (0, -34)], OUT, 3)
    c.poly([(0, -34), (22, -28), (0, -20)], col, w=2)
    c.circle(0, 0, 4, col, w=2)
    c.pop()


# ================================================================== the striped pole gag

def striped_pole(c, x, base, h, w=16, t=0.0, wobble=0.0):
    """A candy-striped barber/scratching pole standing up from (x, base)."""
    sway = math.sin(t * 18) * wobble * 6
    top = (x + sway, base - h)
    c.rect(x - w / 2 + sway * 0.5, base - h, x + w / 2 + sway * 0.5, base, (255, 255, 255), w=2.5)
    n = int(h / (w * 0.9))
    for i in range(n):
        y0 = base - i * h / n
        y1 = y0 - h / n * 0.5
        c.poly([(x - w / 2 + sway * 0.5, y0), (x + w / 2 + sway * 0.5, y0 - h / n * 0.4),
                (x + w / 2 + sway * 0.5, y1 - h / n * 0.4), (x - w / 2 + sway * 0.5, y1)], (226, 60, 70), ol=None)
    c.rect(x - w / 2 + sway * 0.5, base - h, x + w / 2 + sway * 0.5, base, None, w=2.5)
    c.circle(top[0] - sway * 0.5, top[1], w * 0.6, (250, 210, 70), w=2.5)


def pole_dream(ic, t, scratch=0.0):
    """Thought bubble picture: a globe with a giant stripy pole on top, a tiny Whiskers scratching it."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS


def dream(c, x, y, s, t, scratch=0.0):
    """Drawn straight into a thought bubble centred at (x, y)."""
    c.push(x, y, s)
    K.globe(c, 0, 50, 46, lon=-t * 30, lat=12, style="toy")
    ice_cap(c, 0, 50, 46, -t * 30, 12, True, 72)
    striped_pole(c, 0, 50 - 44, 74, 12, t, wobble=scratch)
    # tiny Whiskers stretching up the pole, claws out
    pose = "stand"
    D.cat(c, -30, 6, D.WHISKERS, 0.32, 1, pose, t=t, eyes="happy" if scratch > 0 else "open",
          walk=t * 10 * scratch)
    if scratch > 0:
        for k in range(3):
            yy = -40 + k * 9 + (t * 60 % 8)
            c.line([(-14, yy), (-8, yy + 6)], (255, 255, 255), 2)
    c.pop()


# ============================================================================ diagrams

def cut_antarctica(ic, t, k_land=1.0):
    """Inset: Antarctica cut open -- thick ice lying on top of land, the sea at the sides."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 200, 245)), (1, (215, 236, 255))]), (0, 0))
    sea_y = 150
    ic.rect(0, sea_y, w, h, SEA, ol=None)
    for i in range(6):
        ic.arc(30 + i * 70, sea_y + 20, 16, 6, 200, 340, (100, 150, 210), 2)
    # land (rock) hump
    land = [(40, h)] + [(40 + (w - 80) * u, sea_y + 30 - 50 * math.sin(math.pi * u) ** 0.6
                         + 8 * math.sin(u * 19)) for u in np.linspace(0, 1, 24)] + [(w - 40, h)]
    ic.poly(land, (150, 112, 86), w=3)
    for i in range(5):
        ic.circle(90 + i * 60, h - 22 + 6 * math.sin(i), 5, (120, 88, 66), ol=None)
    # the thick ice sheet on top
    top = [(30 + (w - 60) * u, sea_y - 8 - 66 * math.sin(math.pi * u) ** 0.5) for u in np.linspace(0, 1, 24)]
    land_top = [(p[0], p[1]) for p in land[1:-1]][::-1]
    ic.poly(top + land_top, ICE, w=3)
    for i in range(4):
        ic.line([(80 + i * 70, sea_y - 40 + 6 * i % 3), (110 + i * 70, sea_y - 36 + 6 * i % 3)], ICE_SH, 3)
    pebble(ic, w / 2 + 10, sea_y - 80, 0.32, -1, t, eyes="happy")
    K.label(ic, 96, 40, "Thick ice", 24, tip=(150, sea_y - 50), k=1.0, col=(40, 110, 190))
    K.label(ic, w - 100, h - 34, "Land!", 28, tip=(w / 2 + 40, sea_y + 20), k=k_land, col=(150, 80, 40))


def cut_arctic(ic, t, k=1.0):
    """Inset: the Arctic cut open -- a slab of sea ice floating on deep ocean, a seal under it."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 200, 245)), (0.3, (200, 230, 255)),
                                                       (0.301, (60, 120, 190)), (1, (20, 50, 110))]), (0, 0))
    wl = h * 0.3
    bob = 2 * math.sin(t * 1.6)
    ic.poly([(20, wl - 18 + bob), (w - 30, wl - 14 + bob), (w - 20, wl + 26 + bob), (34, wl + 30 + bob)],
            ICE, w=3)
    ic.line([(20, wl + bob), (w - 24, wl + bob)], ICE_SH, 2, cap=False)
    # ice cube in a glass (the comparison), top right
    # seal swimming under the ice
    sx = (t * 50) % (w + 160) - 80
    seal(ic, sx, h - 50, 0.5, 1, t)
    for i in range(4):
        u = (t * 0.7 + i / 4) % 1
        ic.circle(60 + i * 90, h - 20 - u * (h - wl - 50), 3 + i % 2 * 2, (150, 200, 245), w=1.5)
    bjorn(ic, w * 0.6, wl - 16 + bob, 0.18, -1, t)
    K.label(ic, 110, 26, "Sea ice", 24, tip=(110, wl - 10), k=k, col=(40, 110, 190))
    K.label(ic, w - 130, h - 30, "Ocean. No land!", 24, k=clamp(k * 1.5 - 0.3), col=(30, 70, 140))


def torch(c, x, y, s=1.0, on=1.0):
    """A torch (flashlight) pointing right; (x, y) = the lens centre."""
    c.push(x, y, s)
    c.rect(-90, -13, -26, 13, (70, 120, 200), r=6, w=2.5)
    c.poly([(-30, -14), (0, -24), (0, 24), (-30, 14)], (90, 140, 220), w=2.5)
    c.rect(-2, -26, 6, 26, (200, 200, 210), r=3, w=2)
    c.rect(-70, -18, -58, -12, (230, 70, 70), r=2, w=1.5)
    if on > 0:
        c.ellipse(4, 0, 4, 22, mix((255, 255, 255), (255, 240, 150), 0.5), ol=None)
    c.pop()


def _surface_x(cx, cy, R, yy):
    return cx - math.sqrt(max(0.0, R * R - (yy - cy) ** 2))


def torch_diagram(ic, t, k_straight=1.0, k_slant=1.0):
    """Two torches with equal beams shine on a ball: straight on (middle) -> a small, bright, hot
    spot; at a slant (top) -> the same light spread over a long strip, thin and weak."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    cx, cy, R = w * 0.66, h * 0.56, 120
    K.globe(ic, cx, cy, R, lon=-20, lat=0, style="earth")
    ice_cap(ic, cx, cy, R, -20, 0, True, 74)
    ice_cap(ic, cx, cy, R, -20, 0, False, 70)
    band = 34
    for kind, y0, kk in (("straight", cy - band / 2, k_straight), ("slant", cy - R + 2, k_slant)):
        if kk <= 0.01:
            continue
        y1 = y0 + band
        tx = 70
        torch(ic, tx, (y0 + y1) / 2, 0.75)
        reach = ease(clamp(kk * 1.6))
        xs0, xs1 = _surface_x(cx, cy, R, y0), _surface_x(cx, cy, R, y1)
        bright = kind == "straight"
        col = (255, 244, 140) if bright else (255, 246, 190)
        a = 0.85 if bright else 0.45
        # the beam (equal width for both)
        bx0 = lerp(tx + 6, xs0, reach)
        bx1 = lerp(tx + 6, xs1, reach)
        beam = Canvas(size=(int(w), int(h)), bg=(0, 0, 0))
        beam.poly([(tx + 6, y0 + 4), (bx0, y0), (bx1, y1), (tx + 6, y1 - 4)], (255, 255, 255), ol=None)
        mask = beam.img.convert("L").point(lambda v: int(v * a * 0.75))
        ic.img.paste(col, (0, 0), mask)
        if reach >= 0.99:
            # the lit patch on the ball: same light, small area (hot) or long strip (weak)
            pts = []
            for yy in np.linspace(y0, y1, 12):
                pts.append((_surface_x(cx, cy, R, yy), yy))
            if bright:
                ic.stroke(pts, (255, 214, 60), 12, ol=(255, 140, 40))
                K.sparkles(ic, pts[6][0] + 10, pts[6][1], 26, t, 5, 1.0, seed=2, col=(255, 230, 120))
            else:
                ic.line(pts, (255, 248, 210), 7)
    K.label(ic, 150, h - 30, "Straight: strong and hot!", 22, tip=(cx - R + 10, cy + 10),
            k=clamp(k_straight * 2 - 1), col=(200, 90, 30))
    K.label(ic, 160, 30, "Slant: spread thin and weak", 22, tip=(cx - 40, cy - R + 20),
            k=clamp(k_slant * 2 - 1), col=(60, 110, 190))


def days_diagram(ic, t, k_summer=1.0, k_winter=0.0):
    """Inset: in summer the sun circles low and never sets; in winter it stays dark."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    win = clamp(k_winter)
    sky0 = mix((120, 190, 250), (14, 18, 50), win)
    sky1 = mix((214, 238, 255), (40, 40, 90), win)
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, sky0), (0.72, sky1), (0.721, ICE), (1, ICE_SH)]),
                 (0, 0))
    hy = h * 0.72
    if win < 0.5:
        # the sun goes round and round, low in the sky, never dipping below the horizon
        a = t * 2.2
        sx = w / 2 + math.cos(a) * w * 0.36
        sy = hy - 56 + math.sin(a) * 26
        pts = [(w / 2 + math.cos(u) * w * 0.36, hy - 56 + math.sin(u) * 26) for u in np.linspace(0, math.tau, 50)]
        for i in range(0, len(pts) - 1, 2):
            ic.line([pts[i], pts[i + 1]], (255, 236, 110), 3)
        ic.circle(sx, sy, 18, (255, 216, 80), w=2.5)
        K.text(ic, w / 2, 30, "Summer: the sun never sets!", 24, (200, 90, 30), stroke=2,
               stroke_fill=(255, 255, 255))
    else:
        rng = np.random.default_rng(4)
        for _ in range(30):
            ic.circle(rng.uniform(0, w), rng.uniform(0, hy - 10), rng.uniform(0.8, 2), (255, 250, 220), ol=None)
        D.moon(ic, w * 0.8, 50, 18, sky=sky0)
        K.text(ic, w / 2, 30, "Winter: dark for weeks!", 24, (255, 236, 150), stroke=2)
    # a little igloo-less ice hill and Bjorn
    bjorn(ic, w * 0.24, h * 0.94, 0.17, 1, t, eyes="happy" if win < 0.5 else "closed")


def never_diagram(ic, t, k=1.0, cross=0.0):
    """Inset: a globe -- polar bear at the top (north), penguin at the bottom (south). They never meet."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    cx, cy, R = w / 2, h / 2 + 6, 104
    K.globe(ic, cx, cy, R, lon=-t * 20, lat=0)
    ice_cap(ic, cx, cy, R, -t * 20, 0, True, 72)
    ice_cap(ic, cx, cy, R, -t * 20, 0, False, 70)
    # the hot middle
    ic.line([(cx - R + 2, cy), (cx + R - 2, cy)], (255, 120, 60), 5, cap=False)
    bear_icon(ic, cx, cy - R - 26, 30, t)
    penguin_icon(ic, cx + 2, cy + R + 22, 34, t)
    K.text(ic, cx + R + 70, cy - R + 10, "North", 26, (255, 255, 255), stroke=3)
    K.text(ic, cx + R + 70, cy + R - 10, "South", 26, (255, 255, 255), stroke=3)
    if cross > 0.01:
        ic.push(cx, cy, K.pop(cross))
        ic.circle(0, 0, 44, (255, 255, 255), ol=(226, 56, 60), w=6)
        ic.line([(-30, -30), (30, 30)], (226, 56, 60), 8)
        ic.pop()
        K.label(ic, max(cx - R - 50, 96), cy, "Never meet!", 24, k=cross, col=(200, 40, 50))


def thermometer(c, x, y, s=1.0, level=0.2, t=0.0):
    """A big cartoon thermometer; level 0..1 fills it (red when high)."""
    c.push(x, y, s)
    col = mix((90, 160, 240), (236, 60, 50), clamp(level * 1.4 - 0.2))
    c.rect(-16, -150, 16, 0, (255, 255, 255), r=16, w=3)
    hh = 20 + 120 * clamp(level)
    c.rect(-8, -hh, 8, 0, col, ol=None, r=8)
    c.circle(0, 8, 24, col, w=3)
    for i in range(5):
        c.line([(16, -30 - i * 24), (26, -30 - i * 24)], OUT, 2)
    c.pop()


def envelope(c, x, y, s=1.0, ang=0.0, col=(255, 250, 236), heart=True):
    """A little letter (message)."""
    c.push(x, y, s)
    c.rect(-30, -20, 30, 20, col, r=3, w=2.5)
    c.line([(-28, -18), (0, 4), (28, -18)], OUT, 2.5)
    if heart:
        c.circle(-4, 6, 4, (230, 80, 100), ol=None)
        c.circle(4, 6, 4, (230, 80, 100), ol=None)
        c.poly([(-8, 7), (8, 7), (0, 15)], (230, 80, 100), ol=None)
    c.pop()


def globe_pin_icon(north=True):
    """Card icon: a globe with a red pin on its North (or South) Pole."""
    def draw(c, x, y, r, t=0.0):
        K.globe(c, x, y, r * 0.8, lon=-t * 25, lat=0)
        ice_cap(c, x, y, r * 0.8, -t * 25, 0, True, 72)
        ice_cap(c, x, y, r * 0.8, -t * 25, 0, False, 70)
        py = y - r * 0.8 if north else y + r * 0.8
        c.push(x, py, 1.0)
        if north:
            c.line([(0, 0), (0, -r * 0.45)], OUT, 3)
            c.poly([(0, -r * 0.45), (r * 0.3, -r * 0.37), (0, -r * 0.27)], (226, 56, 60), w=2)
        else:
            c.line([(0, 0), (0, r * 0.45)], OUT, 3)
            c.poly([(0, r * 0.45), (r * 0.3, r * 0.37), (0, r * 0.27)], (70, 130, 230), w=2)
        c.circle(0, 0, 5, (226, 56, 60) if north else (70, 130, 230), w=2)
        c.pop()
    return draw


def icon_poles(c, x, y, r, t=0.0):
    """Remember card 1: a globe with N at the top and S at the bottom."""
    K.globe(c, x, y, r * 0.78, lon=-t * 25, lat=0)
    ice_cap(c, x, y, r * 0.78, -t * 25, 0, True, 72)
    ice_cap(c, x, y, r * 0.78, -t * 25, 0, False, 70)
    for yy, L, col in ((y - r * 0.82, "N", (226, 56, 60)), (y + r * 0.82, "S", (40, 44, 70))):
        c.circle(x + r * 0.62, yy, r * 0.26, (255, 255, 255), w=2)
        K.text(c, x + r * 0.62, yy + 1, L, r * 0.36, col)


def icon_animals(c, x, y, r, t=0.0):
    """Remember card 2: polar bear on top, penguin below."""
    bear_icon(c, x - r * 0.28, y - r * 0.32, r * 0.5, t)
    penguin_icon(c, x + r * 0.32, y + r * 0.2, r * 0.6, t)


def icon_slant(c, x, y, r, t=0.0):
    """Remember card 3: a pale sun with slanting rays onto snow, and a cold thermometer."""
    c.circle(x - r * 0.4, y - r * 0.4, r * 0.3, (255, 236, 150), w=2)
    for i in range(3):
        c.line([(x - r * 0.15 + i * 8, y - r * 0.28 + i * 4), (x + r * 0.7, y + r * 0.1 + i * 8)],
               (255, 230, 120), 3)
    c.rect(x - r * 0.9, y + r * 0.42, x + r * 0.9, y + r * 0.62, ICE, r=6, w=2)
    thermometer(c, x + r * 0.62, y + r * 0.2, r / 300, 0.05)
