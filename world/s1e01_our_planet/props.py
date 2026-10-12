"""Props for Episode 1: Grandpa Shelby the sea turtle, the ocean, small quiz icons."""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix
from world import kit as K

SHELL = (112, 140, 76)
SHELL_D = (84, 108, 58)
PATCH = (150, 172, 96)
SKIN = (158, 190, 126)
SKIN_D = (120, 152, 96)
BEARD = (250, 250, 244)
SEA = (52, 132, 204)
SEA_D = (38, 104, 178)
SEA_L = (130, 196, 240)


def turtle(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", paddle=1.0, look=(0.0, 0.0), seed=4.0):
    """Grandpa Shelby, side view. (x, y) = waterline under the shell centre; the shell top is
    about 105*s above it, the head about 120*s in front. Lower body is meant to be under water."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    sw = math.sin(t * 3.0) * paddle
    # back flipper
    c.push(-140, 6)
    c.poly([(0, 0), (-50, 10 + 8 * sw), (-44, 26 + 8 * sw), (4, 16)], SKIN_D)
    c.pop()
    # front flipper
    c.push(110, 4)
    a = 0.4 * sw
    pts = [(0, 0), (70 * math.cos(a), 30 + 70 * math.sin(a)), (60 * math.cos(a) - 18, 46 + 60 * math.sin(a)), (-10, 16)]
    c.poly(pts, SKIN_D)
    c.pop()
    # neck + head
    hx, hy = 196, -66
    c.stroke([(110, -18), (150, -40), (hx - 20, hy + 4)], SKIN, 38)
    c.ellipse(hx, hy, 50, 38, SKIN)
    for sx, sy, r in ((-24, -18, 5), (-34, 2, 4), (-10, -28, 4), (130 - hx, -30 - hy, 4)):
        c.circle(hx + sx, hy + sy, r, SKIN_D, ol=None)
    # mouth
    if mouth > 0.05:
        c.ellipse(hx + 26, hy + 16, 14 + 3 * mouth, 3 + 8 * mouth, D.MOUTH, w=2)
    else:
        c.arc(hx + 18, hy + 8, 22, 12, 20, 120, OUT, 2.5)
    # beard
    c.poly([(hx + 4, hy + 30), (hx + 30, hy + 26), (hx + 14, hy + 58), (hx + 8, hy + 46)], BEARD, w=2)
    # eye with heavy wise lid
    ex, ey = hx + 16, hy - 12
    if eyes == "closed":
        c.arc(ex, ey, 10, 7, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 4, 10, 9, 200, 340, OUT, 3)
    else:
        c.ellipse(ex, ey, 11, 12, (255, 255, 255), w=2.5)
        c.ellipse(ex + 2 + look[0] * 3, ey + 2 + look[1] * 2, 5, 7, (40, 30, 30), ol=None)
        c.circle(ex + 4 + look[0] * 3, ey - 1, 1.8, (255, 255, 255), ol=None)
        c.poly([(ex - 13, ey - 2), (ex - 11, ey - 12), (ex, ey - 15), (ex + 12, ey - 10), (ex + 13, ey - 2)],
               SKIN, w=2)
    # eyebrow
    for k in range(4):
        c.ellipse(ex - 10 + k * 7, ey - 20 - k * 1.5, 7, 4.5, BEARD, w=1.5)
    # spectacles
    c.circle(ex, ey, 16, None, ol=(90, 70, 50), w=3)
    c.line([(ex - 16, ey - 2), (hx - 34, hy - 10)], (90, 70, 50), 2.5)
    # shell
    c.ellipse(0, 0, 158, 30, SHELL_D)
    c.poly([(-150, 0)] + [(-150 * math.cos(u), -100 * math.sin(u)) for u in np.linspace(0.05, math.pi - 0.05, 24)]
           + [(150, 0)], SHELL)
    for px, py, r in ((0, -62, 30), (-66, -46, 25), (66, -46, 25), (-114, -18, 16), (114, -18, 16),
                      (-32, -20, 18), (32, -20, 18)):
        pts = [(px + math.cos(a) * r, py + math.sin(a) * r * 0.8) for a in np.linspace(0, math.tau, 7)[:-1]]
        c.poly(pts, PATCH, ol=SHELL_D, w=2.5)
    c.ellipse(0, 2, 156, 12, SHELL_D, ol=OUT, w=2.5)
    c.pop()


def turtle_crew(c, tl, t, x, y, s=1.0, face=1, eyes=None, look=None, shelby_eyes="open", paddle=1.0):
    """Shelby with the three friends riding on his shell (cats at 0.55*s)."""
    turtle(c, x, y, s, face, t, tl.mouth("shelby", t) if tl else 0.0, shelby_eyes, paddle)
    eyes, look = eyes or {}, look or {}
    for who, dx, dy in (("luna", 20, -96), ("whiskers", -62, -84), ("pip", 82, -80)):
        sc = 0.55 * s if who != "pip" else 0.7 * s
        kw = {}
        if who in eyes:
            kw["eyes"] = eyes[who]
        if who in look:
            kw["look"] = look[who]
        K.kat(c, tl, t, who, x + face * dx * s, y + dy * s, sc, face, "sit", **kw)


def sea_waves(c, t, y0, y1, n_rows=6, col=SEA_L, speed=30, seed=2):
    """Animated little wave strokes in the band y0..y1."""
    rng = np.random.default_rng(seed)
    for j in range(n_rows):
        f = j / max(1, n_rows - 1)
        y = lerp(y0, y1, f)
        scale = lerp(0.5, 1.3, f)
        off = (t * speed * scale * (1 if j % 2 else -0.7) + rng.uniform(0, 300)) % (160 * scale)
        x = -160 * scale + off
        while x < W + 60:
            pts = [(x + k * 6 * scale, y + math.sin(k * 0.9) * 3 * scale) for k in range(7)]
            c.line(pts, col, 3 * scale)
            x += 160 * scale


def pancake(c, x, y, r, t=0.0):
    for k in range(3):
        c.ellipse(x, y + 22 - k * 16, r * 0.95, r * 0.3, (232, 176, 96))
        c.ellipse(x, y + 18 - k * 16, r * 0.9, r * 0.22, (244, 200, 120), ol=None)
    c.rect(x - 12, y - 30, x + 12, y - 18, (255, 236, 140), r=3, w=2)
    c.poly([(x - r * 0.6, y - 18), (x + r * 0.5, y - 20), (x + r * 0.7, y - 4), (x - r * 0.3, y - 2)],
           (196, 110, 40), ol=None)


def land_icon(c, x, y, r, t=0.0):
    c.circle(x, y, r, (180, 224, 250), w=3)
    c.poly([(x - r * 0.95, y + r * 0.3), (x - r * 0.4, y - r * 0.2), (x, y + r * 0.05), (x + r * 0.5, y - r * 0.4),
            (x + r * 0.95, y + r * 0.3), (x + r * 0.6, y + r * 0.8), (x - r * 0.6, y + r * 0.8)], (120, 190, 92), w=3)
    c.rect(x - r * 0.08 - 20, y - r * 0.1, x - r * 0.08 - 14, y + r * 0.2, (130, 90, 60), ol=None)
    c.circle(x - r * 0.08 - 17, y - r * 0.2, 13, (80, 160, 80), w=2)


def water_icon(c, x, y, r, t=0.0):
    c.circle(x, y, r, SEA, w=3)
    for k in range(3):
        yy = y - r * 0.4 + k * r * 0.4
        pts = [(x - r * 0.6 + i * r * 0.15, yy + math.sin(i * 1.2 + t * 4) * 5) for i in range(9)]
        c.line(pts, (220, 240, 255), 4)
