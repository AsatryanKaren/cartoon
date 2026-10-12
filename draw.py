"""Drawing toolkit and characters (flat cartoon style, 2x supersampled).

All coordinates are in output pixels (1280x720). The Canvas draws at SS times
that size and shrinks at the end, which gives smooth edges. Characters are
drawn in their own local space: origin between the feet, facing right, y up
is negative. `Canvas.push` moves/scales/mirrors that space.
"""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import WIDTH as W, HEIGHT as H

SS = 2
OUT = (48, 34, 40)
LW = 3


# ------------------------------------------------------------------ helpers

def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def mix(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "/Library/Fonts/Arial Rounded Bold.ttf",
    "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


@lru_cache(None)
def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, int(size * SS))
    return ImageFont.load_default(int(size * SS))


def gradient(w, h, stops):
    """Vertical gradient image (w, h already supersampled). stops: [(pos, rgb)]"""
    y = np.linspace(0, 1, h)[:, None]
    rgb = np.zeros((h, 3))
    for c in range(3):
        rgb[:, c] = np.interp(y[:, 0], [p for p, _ in stops], [col[c] for _, col in stops])
    arr = np.repeat(rgb[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


# ------------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, img=None, size=(W, H), bg=(0, 0, 0)):
        self.img = img if img is not None else Image.new("RGB", (size[0] * SS, size[1] * SS), bg)
        self.d = ImageDraw.Draw(self.img)
        self.tf = [(0.0, 0.0, 1.0, 1.0)]
        self.tint = None            # (rgb, amount): mixes every colour, e.g. for night

    # transform stack
    def push(self, x, y, s=1.0, flip=False):
        ox, oy, sx, sy = self.tf[-1]
        self.tf.append((ox + sx * x, oy + sy * y, sx * s * (-1 if flip else 1), sy * s))

    def pop(self):
        self.tf.pop()

    def P(self, x, y):
        ox, oy, sx, sy = self.tf[-1]
        return ((ox + sx * x) * SS, (oy + sy * y) * SS)

    @property
    def scale(self):
        return abs(self.tf[-1][3])

    @property
    def flipped(self):
        return self.tf[-1][2] < 0

    def c(self, col):
        if col is None or self.tint is None:
            return col
        return mix(col, self.tint[0], self.tint[1])

    def _w(self, w):
        return max(1, int(round(w * self.scale * SS)))

    def _box(self, cx, cy, rx, ry):
        x0, y0 = self.P(cx - rx, cy - ry)
        x1, y1 = self.P(cx + rx, cy + ry)
        return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

    # primitives
    def ellipse(self, cx, cy, rx, ry, fill, ol=OUT, w=LW):
        self.d.ellipse(self._box(cx, cy, rx, ry), fill=self.c(fill),
                       outline=self.c(ol) if ol else None, width=self._w(w) if ol else 0)

    def circle(self, cx, cy, r, fill, ol=OUT, w=LW):
        self.ellipse(cx, cy, r, r, fill, ol, w)

    def poly(self, pts, fill, ol=OUT, w=LW):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=self.c(fill),
                       outline=self.c(ol) if ol else None, width=self._w(w) if ol else 0)

    def rect(self, x0, y0, x1, y1, fill, ol=OUT, w=LW, r=0):
        a, b = self.P(x0, y0), self.P(x1, y1)
        box = [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]
        self.d.rounded_rectangle(box, radius=r * self.scale * SS, fill=self.c(fill),
                                 outline=self.c(ol) if ol else None, width=self._w(w) if ol else 0)

    def line(self, pts, fill, w=LW, cap=True):
        P = [self.P(x, y) for x, y in pts]
        ww = self._w(w)
        self.d.line(P, fill=self.c(fill), width=ww, joint="curve")
        if cap and ww > 2:
            r = ww / 2
            for x, y in (P[0], P[-1]):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=self.c(fill))

    def stroke(self, pts, fill, w, ol=OUT):
        """Thick outlined stroke (tails, legs)."""
        if ol:
            self.line(pts, ol, w + 2 * LW)
        self.line(pts, fill, w)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w=LW):
        if self.flipped:
            a0, a1 = 180 - a1, 180 - a0
        self.d.arc(self._box(cx, cy, rx, ry), a0, a1, fill=self.c(fill), width=self._w(w))

    def text(self, x, y, s, size, fill, anchor="mm", stroke=0, stroke_fill=OUT):
        self.d.text(self.P(x, y), s, font=font(size), fill=self.c(fill), anchor=anchor,
                    stroke_width=int(stroke * SS), stroke_fill=self.c(stroke_fill), align="center")

    def glow(self, cx, cy, rx, ry, inner, outer, steps=10):
        """Fake soft glow: concentric ellipses fading from outer to inner colour."""
        for k in range(steps, 0, -1):
            f = k / steps
            self.ellipse(cx, cy, rx * f, ry * f, mix(inner, outer, f ** 0.7), ol=None)

    def finish(self):
        return self.img.reduce(SS) if SS > 1 else self.img


# ----------------------------------------------------------------- palettes

WHISKERS = dict(body=(243, 152, 62), dark=(205, 108, 38), belly=(255, 226, 180),
                ear=(255, 168, 160), eye=(126, 190, 70), stripes=True, collar=None)
LUNA = dict(body=(156, 160, 176), dark=(118, 121, 140), belly=(230, 230, 238),
            ear=(250, 180, 192), eye=(80, 160, 225), stripes=False, collar=(70, 120, 220))
NOSE = (240, 120, 140)
MOUTH = (120, 40, 50)
TONGUE = (240, 120, 130)
WATER_TINT = (90, 120, 170)


def blink(t, seed=0.0):
    return ((t + seed * 1.7) % 3.9) < 0.13


# ---------------------------------------------------------------------- cat

def cat(c, x, y, pal, s=1.0, face=1, pose="stand", walk=0.0, t=0.0, mouth=0.0,
        eyes="open", look=(0.0, 0.0), tail=None, wet=0.0, head_dy=0.0, seed=0.0, squash=1.0):
    """Draw a cat. pose: stand | walk | sit | sleep | crouch | leap | swim.

    walk: distance-based phase (radians) for the leg cycle.
    mouth: 0..1 jaw openness.  eyes: open | closed | happy | wide.
    """
    if eyes == "open" and blink(t, seed):
        eyes = "closed"
    body, dark, belly = pal["body"], pal["dark"], pal["belly"]
    if wet:
        body, dark, belly = (mix(body, WATER_TINT, 0.35 * wet), mix(dark, WATER_TINT, 0.35 * wet),
                             mix(belly, WATER_TINT, 0.3 * wet))
    c.push(x, y, s, flip=face < 0)
    c.push(0, 0, 1.0)
    ox, oy, sx, sy = c.tf[-1]
    c.tf[-1] = (ox, oy, sx * (2 - squash), sy * squash)   # squash & stretch
    tail_wave = math.sin(t * 2.2 + seed) if tail is None else tail

    if pose == "sleep":
        _cat_sleep(c, pal, body, dark, belly, t, mouth)
    elif pose == "sit":
        _cat_sit(c, pal, body, dark, belly, t, mouth, eyes, look, tail_wave, head_dy)
    elif pose == "swim":
        _cat_swim(c, pal, body, dark, belly, t, mouth, eyes, look)
    else:
        _cat_stand(c, pal, body, dark, belly, pose, walk, t, mouth, eyes, look, tail_wave, head_dy)

    if wet > 0.05:
        rng = np.random.default_rng(int(seed * 100) + 7)
        for k in range(5):
            px, py = rng.uniform(-40, 60), rng.uniform(-110, -20)
            fall = ((t * 1.3 + k * 0.37) % 1.0) * 40
            c.ellipse(px, py + fall, 2.5, 4, (170, 210, 255), ol=None)
    c.pop()
    c.pop()


def _tail(c, base, length, wave, body, curl=1.0):
    pts = []
    for i in range(9):
        u = i / 8
        ang = math.radians(-100 - 50 * u * curl) + 0.45 * wave * u
        r = length * u
        pts.append((base[0] + math.cos(ang) * r * 0.9 - 18 * u, base[1] + math.sin(ang) * r))
    c.stroke(pts, body, 12)


def _head(c, hx, hy, pal, body, dark, belly, mouth, eyes, look, t):
    ear = pal["ear"]
    # ears
    c.poly([(hx - 26, hy - 14), (hx - 22, hy - 48), (hx - 2, hy - 28)], body)
    c.poly([(hx + 4, hy - 30), (hx + 22, hy - 48), (hx + 28, hy - 12)], body)
    c.poly([(hx - 21, hy - 19), (hx - 19, hy - 40), (hx - 8, hy - 28)], ear, ol=None)
    c.poly([(hx + 9, hy - 29), (hx + 19, hy - 40), (hx + 22, hy - 17)], ear, ol=None)
    c.ellipse(hx, hy, 35, 31, body)
    if pal["stripes"]:
        for dx in (-9, 0, 9):
            c.line([(hx + dx, hy - 30), (hx + dx * 0.8, hy - 20)], dark, 4)
    # muzzle
    c.ellipse(hx + 12, hy + 12, 17, 11, belly, ol=None)
    # eyes
    for ex in (hx - 2, hx + 22):
        ey = hy - 4
        if eyes == "closed":
            c.arc(ex, ey - 1, 7, 5, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 7, 7, 200, 340, OUT, 3)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 7.5 * big, 9.5 * big, (255, 255, 255), w=2.5)
            lx, ly = look
            c.ellipse(ex + 1.5 + lx * 2.5, ey + ly * 2.5, 5 * big, 7 * big, pal["eye"], ol=None)
            c.ellipse(ex + 1.5 + lx * 2.5, ey + ly * 2.5, 2.2, 5.5 * big, (25, 20, 25), ol=None)
            c.circle(ex + 3 + lx * 2.5, ey - 3 + ly * 2.5, 1.8, (255, 255, 255), ol=None)
    # nose + mouth
    c.poly([(hx + 13, hy + 5), (hx + 21, hy + 5), (hx + 17, hy + 10)], NOSE, w=1.5)
    if mouth > 0.05:
        h = 2 + 9 * mouth
        c.ellipse(hx + 17, hy + 15 + h * 0.5, 6 + 2 * mouth, h, MOUTH, w=2)
        c.ellipse(hx + 17, hy + 15 + h * 0.9, 4, 2 + 2 * mouth, TONGUE, ol=None)
    else:
        c.arc(hx + 13, hy + 12, 4, 3, 0, 180, OUT, 2)
        c.arc(hx + 21, hy + 12, 4, 3, 0, 180, OUT, 2)
    # whiskers
    for dy in (-2, 4):
        c.line([(hx + 30, hy + 10), (hx + 52, hy + 6 + dy * 1.5)], OUT, 1.5, cap=False)
        c.line([(hx + 2, hy + 10), (hx - 18, hy + 6 + dy * 1.5)], OUT, 1.5, cap=False)
    if pal["collar"]:
        c.rect(hx - 20, hy + 24, hx + 22, hy + 31, pal["collar"], w=2, r=3)
        c.circle(hx + 6, hy + 35, 5, (250, 210, 70), w=2)


def _cat_stand(c, pal, body, dark, belly, pose, walk, t, mouth, eyes, look, tail_wave, head_dy):
    crouch = pose == "crouch"
    leap = pose == "leap"
    by = -40 if crouch else -48
    # tail
    _tail(c, (-46, by - 6), 60, tail_wave * (2.5 if crouch else 1), body, curl=0.6 if leap else 1.0)

    def leg(hx, phase, col):
        if leap:
            front = hx > 0
            foot = (hx + (34 if front else -34), by + 32 if front else by + 28)
        elif crouch:
            foot = (hx + 4, 0)
        else:
            sw = math.sin(walk + phase)
            foot = (hx + sw * 12, -max(0.0, math.cos(walk + phase)) * 7 if walk else 0)
        c.stroke([(hx, by + 4), foot], col, 13)
        c.ellipse(foot[0] + 3, foot[1] - 2, 9, 5.5, col)

    leg(-30, math.pi, dark)
    leg(30, 0, dark)
    c.ellipse(0, by, 54, 30 if not crouch else 26, body)
    c.ellipse(6, by + 12, 36, 12, belly, ol=None)
    if pal["stripes"]:
        for dx in (-30, -14, 2, 18):
            c.line([(dx, by - 28), (dx + 5, by - 13)], dark, 5)
    leg(-24, 0, body)
    leg(36, math.pi, body)
    bob = math.sin(walk * 2) * 2 if walk else 0
    hx, hy = 52, by - 38 + bob + head_dy + (14 if crouch else 0)
    if leap:
        hx, hy = 58, by - 26
    _head(c, hx, hy, pal, body, dark, belly, mouth, eyes, look, t)


def _cat_sit(c, pal, body, dark, belly, t, mouth, eyes, look, tail_wave, head_dy):
    # tail curled on the ground
    pts = [(-30 + 70 * u, -6 - 14 * math.sin(math.pi * u) + 4 * tail_wave * u) for u in np.linspace(0, 1, 9)]
    c.stroke([(-36, -14)] + pts, body, 12)
    c.ellipse(-6, -26, 36, 26, body)                  # haunch
    c.ellipse(6, -56, 32, 44, body)                   # chest
    c.ellipse(16, -46, 18, 30, belly, ol=None)
    if pal["stripes"]:
        for dy in (-80, -64):
            c.line([(-20, dy), (-8, dy + 6)], pal["dark"], 5)
    c.ellipse(4, -6, 11, 7, body)                     # paws
    c.ellipse(26, -6, 11, 7, body)
    _head(c, 18, -106 + head_dy, pal, body, dark, belly, mouth, eyes, look, t)


def _cat_sleep(c, pal, body, dark, belly, t, mouth):
    breathe = 1 + 0.03 * math.sin(t * 2.0)
    c.ellipse(0, -28 * breathe, 62, 28 * breathe, body)
    if pal["stripes"]:
        for dx in (-34, -16, 2):
            c.line([(dx, -52), (dx + 5, -38)], dark, 5)
    pts = [(-55 + 100 * u, -6 + 6 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 9)]
    c.stroke(pts, body, 12)
    _head(c, 46, -40, pal, body, dark, belly, mouth, "closed", (0, 0), t)


def _cat_swim(c, pal, body, dark, belly, t, mouth, eyes, look):
    for k in (-1, 1):
        px = 30 + 26 * k + 6 * math.sin(t * 9 + k)
        c.ellipse(px, -4, 10, 6, body)
    _head(c, 30, -30 + 3 * math.sin(t * 5), pal, body, dark, belly, mouth, eyes, look, t)


# -------------------------------------------------------------------- mouse

PIP = dict(body=(176, 156, 142), belly=(232, 216, 200), ear=(255, 176, 186), scarf=(220, 50, 50))


def mouse(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, mouth=0.0, eyes="open", hop=0.0, proud=False, seed=2.0):
    if eyes == "open" and blink(t, seed):
        eyes = "closed"
    p = PIP
    c.push(x, y - hop, s, flip=face < 0)
    # tail
    pts = [(-16 - 30 * u, -10 - 18 * u + 6 * math.sin(t * 3 + u * 4) * u) for u in np.linspace(0, 1, 8)]
    c.stroke(pts, p["ear"], 3)
    # feet
    for fx, ph in ((-6, 0), (8, math.pi)):
        lift = -max(0.0, math.cos(walk + ph)) * 4 if walk else 0
        c.ellipse(fx + (math.sin(walk + ph) * 4 if walk else 0), lift - 2, 6, 3.5, p["ear"], w=2)
    if proud:
        c.ellipse(2, -22, 15, 20, p["body"], w=2.5)
        c.ellipse(5, -18, 9, 13, p["belly"], ol=None)
        hx, hy = 6, -46
    else:
        c.ellipse(0, -16, 20, 15, p["body"], w=2.5)
        c.ellipse(4, -12, 12, 8, p["belly"], ol=None)
        hx, hy = 18, -30
    # scarf (flaps behind)
    flap = math.sin(t * 7) * 4
    c.poly([(hx - 14, hy + 8), (hx - 30, hy + 12 + flap), (hx - 26, hy + 18 + flap), (hx - 10, hy + 14)],
           p["scarf"], w=2)
    c.rect(hx - 14, hy + 7, hx + 10, hy + 14, p["scarf"], w=2, r=3)
    # head
    c.circle(hx - 8, hy - 14, 9, p["body"], w=2.5)
    c.circle(hx - 8, hy - 14, 5.5, p["ear"], ol=None)
    c.circle(hx + 6, hy - 15, 9, p["body"], w=2.5)
    c.circle(hx + 6, hy - 15, 5.5, p["ear"], ol=None)
    c.ellipse(hx, hy, 13, 11, p["body"], w=2.5)
    c.circle(hx + 13, hy + 1, 3, NOSE, w=1.5)
    if eyes == "closed":
        c.arc(hx + 4, hy - 3, 3.5, 2.5, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(hx + 4, hy, 3.5, 3.5, 200, 340, OUT, 2)
    else:
        c.ellipse(hx + 4, hy - 3, 3, 3.6, (25, 20, 25), ol=None)
        c.circle(hx + 5, hy - 4.5, 1.1, (255, 255, 255), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 8, hy + 6, 3, 1 + 3.5 * mouth, MOUTH, w=1.5)
    for dy in (-1, 2):
        c.line([(hx + 13, hy + 2), (hx + 25, hy + dy * 2)], OUT, 1, cap=False)
    c.pop()


# --------------------------------------------------------------------- props

def frog(c, x, y, s=1.0, face=1, t=0.0, croak=0.0, laugh=False, seed=0.0):
    c.push(x, y - (abs(math.sin(t * 9)) * 6 if laugh else 0), s, flip=face < 0)
    green, light = (95, 175, 80), (190, 225, 140)
    c.ellipse(0, -14, 24, 15, green)
    if croak > 0:
        c.ellipse(14, -6, 9 * (0.6 + croak), 7 * (0.6 + croak), light, w=2)
    c.ellipse(-4, -2, 10, 5, green)
    for ex in (-6, 10):
        c.circle(ex, -28, 7, green)
        if laugh or blink(t, seed):
            c.arc(ex, -27, 4, 3, 200, 340, OUT, 2)
        else:
            c.circle(ex, -28, 4, (255, 255, 255), w=1.5)
            c.circle(ex + 1, -28, 2, (20, 20, 20), ol=None)
    if laugh:
        c.ellipse(6, -12, 10, 5, MOUTH, w=2)
    else:
        c.arc(4, -16, 14, 6, 20, 160, OUT, 2)
    c.pop()


def lily_pad(c, x, y, r=34):
    c.ellipse(x, y, r, r * 0.35, (60, 130, 70), ol=(30, 70, 45))
    c.poly([(x, y), (x + r, y - 3), (x + r, y + 4)], (30, 60, 80), ol=None)


def butterfly(c, x, y, t, s=1.0, col=(170, 110, 220), col2=(255, 210, 80)):
    k = 0.25 + 0.75 * abs(math.sin(t * 16))
    c.push(x, y, s)
    for side in (-1, 1):
        c.ellipse(side * 11 * k, -6, 12 * k, 11, col, w=2)
        c.ellipse(side * 8 * k, 7, 8 * k, 7, col2, w=2)
    c.ellipse(0, 0, 2.5, 11, OUT, ol=None)
    c.line([(0, -10), (-5, -18)], OUT, 1.5, cap=False)
    c.line([(0, -10), (5, -18)], OUT, 1.5, cap=False)
    c.pop()


def moon(c, x, y, r, col=(250, 246, 215), sky=(45, 55, 105)):
    c.glow(x, y, r * 2.4, r * 2.4, (120, 130, 175), sky, steps=8)
    c.circle(x, y, r, col, ol=None)
    for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.15, 0.12), (-0.05, 0.4, 0.1)):
        c.circle(x + dx * r, y + dy * r, rr * r, (232, 226, 190), ol=None)


def stars(c, rng_seed, n, w, h, col=(255, 250, 220)):
    rng = np.random.default_rng(rng_seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.8, 2.2)
        c.circle(x, y, r, col, ol=None)


def tree(c, x, y, s=1.0, leaf=(90, 165, 85), trunk=(130, 90, 60)):
    c.push(x, y, s)
    c.rect(-12, -120, 12, 0, trunk, r=4)
    for dx, dy, r in ((-40, -140, 46), (40, -140, 46), (0, -180, 56), (0, -130, 50)):
        c.circle(dx, dy, r, leaf)
    for dx, dy, r in ((-40, -140, 40), (40, -140, 40), (0, -180, 50), (0, -130, 44)):
        c.circle(dx, dy, r, leaf, ol=None)
    c.pop()


def bush(c, x, y, s=1.0, col=(80, 155, 80)):
    c.push(x, y, s)
    for dx, r in ((-30, 26), (30, 26), (0, 36)):
        c.circle(dx, -r + 4, r, col)
    for dx, r in ((-30, 22), (30, 22), (0, 32)):
        c.circle(dx, -r + 4, r, col, ol=None)
    c.pop()


def flower(c, x, y, col, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, -26)], (70, 140, 70), 3)
    for k in range(5):
        a = k * math.tau / 5
        c.circle(math.cos(a) * 6, -30 + math.sin(a) * 6, 5, col, w=1.5)
    c.circle(0, -30, 4, (255, 215, 80), w=1.5)
    c.pop()


def cloud(c, x, y, s=1.0, col=(255, 255, 255)):
    c.push(x, y, s)
    for dx, dy, r in ((-40, 0, 26), (0, -14, 34), (40, 0, 26), (0, 6, 26)):
        c.circle(dx, dy, r, col, ol=None)
    c.pop()


def moon_fish(c, x, y, t, s=1.0, broken=0.0):
    """The glowing 'fish' -- really the moon's wobbling reflection on the water."""
    c.push(x, y, s)
    water = (32, 52, 98)
    c.glow(0, 0, 120, 30, (150, 165, 190), water, steps=10)
    if broken > 0:
        rng = np.random.default_rng(int(t * 6))
        for k in range(10):
            dx = rng.uniform(-90, 90) * (0.5 + broken)
            dy = rng.uniform(-14, 14)
            c.ellipse(dx, dy, rng.uniform(6, 22) * (1.2 - broken * 0.5), 3, (250, 246, 215), ol=None)
    else:
        wob = math.sin(t * 2.4) * 6
        c.ellipse(wob * 0.3, 0, 52, 16, (240, 236, 200), ol=None)
        c.ellipse(wob * 0.3, 0, 40, 11, (255, 252, 230), ol=None)
        # ripple slivers that read as a tail and fins
        c.poly([(46 + wob, 0), (78 + wob, -14), (72 + wob * 1.3, 0), (78 + wob, 14)], (240, 236, 200), ol=None)
        for k in range(3):
            dx = -30 + 30 * k + wob * (k - 1)
            c.ellipse(dx, 20 + 3 * math.sin(t * 3 + k), 18, 2.2, (220, 220, 200), ol=None)
    c.pop()


def zzz(c, x, y, t):
    for k in range(3):
        u = (t * 0.35 + k / 3) % 1.0
        c.text(x + 20 * u + 10 * k, y - 60 * u, "z", 18 + 10 * u,
               mix((255, 255, 255), (60, 70, 120), u), stroke=1.5)


@lru_cache(None)
def font_px(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def subtitle(img, text, col, size=30, width=52):
    """Burn a subtitle into a finished (output-resolution) frame."""
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if cur and len(cur) + len(w_) + 1 > width:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    d = ImageDraw.Draw(img)
    y = H - 34 - (size + 10) * (len(lines) - 1)
    for ln in lines:
        d.text((W / 2, y), ln, font=font_px(size), fill=col, anchor="mm",
               stroke_width=3, stroke_fill=(20, 15, 20))
        y += size + 10
