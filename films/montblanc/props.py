"""Mountain props and the new characters for "Whiskers and the White Mountain".

All drawn with draw.Canvas primitives in the same flat outlined style.
Characters are in local space: origin between the feet, facing right.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix

SNOW = (246, 249, 255)
SNOW_SH = (200, 214, 238)
SNOW_DEEP = (170, 188, 222)
ROCK = (112, 108, 120)
ROCK_D = (84, 80, 96)
PINE = (46, 104, 78)
PINE_D = (34, 80, 62)


# ------------------------------------------------------------- scenery

def peak(c, x, base, w, h, rock=ROCK, snow=SNOW, shade=SNOW_SH, cap=0.45, seed=0, ol=OUT):
    """A pointed snow-capped mountain: rock body, jagged snow cap, shaded right flank."""
    rng = np.random.default_rng(seed)
    top = (x, base - h)
    c.poly([(x - w / 2, base), top, (x + w / 2, base)], rock, ol=ol, w=2.5)
    c.poly([top, (x + w / 2, base), (x + w * 0.08, base)], mix(rock, (40, 40, 60), 0.25), ol=None)
    # snow cap with a zigzag lower edge
    k = cap
    lx, rx = x - w / 2 * k, x + w / 2 * k
    yb = base - h * (1 - k)
    pts = [top, (rx, yb)]
    n = 6
    for i in range(1, n):
        u = i / n
        px = lerp(rx, lx, u)
        py = yb + (rng.uniform(10, 26) if i % 2 else -rng.uniform(0, 10)) * (h / 300)
        pts.append((px, py))
    pts.append((lx, yb))
    c.poly(pts, snow, ol=ol, w=2.5)
    c.poly([top, (rx, yb), (lerp(rx, lx, 0.45), yb + 8 * h / 300)], shade, ol=None)


def mont_blanc(c, x, base, s=1.0, snow=SNOW, shade=SNOW_SH, rock=ROCK, ol=OUT, glow=None):
    """The Mont Blanc massif: jagged rock needles on the left, the great rounded white dome."""
    prof = [(-760, 0), (-700, -120), (-655, -250), (-630, -175), (-600, -315), (-576, -205),
            (-548, -265), (-515, -170), (-470, -225), (-400, -260), (-320, -300), (-220, -352),
            (-130, -398), (-55, -424), (0, -430), (45, -427), (115, -406), (205, -362), (300, -300),
            (400, -235), (500, -170), (610, -95), (760, 0)]
    P = [(x + dx * s, base + dy * s) for dx, dy in prof]
    c.poly(P, snow, ol=ol, w=3)
    # needles: rock with little snow ledges
    needles = [(-700, -120), (-655, -250), (-630, -175), (-600, -315), (-576, -205), (-548, -265),
               (-515, -170), (-470, -225)]
    for (ax, ay), (bx, by) in zip(needles, needles[1:]):
        c.poly([(x + ax * s, base + ay * s), (x + bx * s, base + by * s),
                (x + (ax + bx) / 2 * s, base)], rock, ol=None)
    c.line([(x + dx * s, base + dy * s) for dx, dy in [(-760, 0)] + needles + [(-400, -260)]], ol, 3)
    for dx, dy in needles[1::2]:
        c.poly([(x + dx * s, base + dy * s), (x + (dx + 14) * s, base + (dy + 40) * s),
                (x + (dx - 12) * s, base + (dy + 34) * s)], snow, ol=None)
    # shaded right flank of the dome
    c.poly([(x, base - 430 * s), (x + 45 * s, base - 427 * s), (x + 115 * s, base - 406 * s),
            (x + 205 * s, base - 362 * s), (x + 300 * s, base - 300 * s), (x + 400 * s, base - 235 * s),
            (x + 500 * s, base - 170 * s), (x + 610 * s, base - 95 * s), (x + 740 * s, base - 3 * s),
            (x + 330 * s, base - 3 * s), (x + 150 * s, base - 200 * s), (x + 40 * s, base - 330 * s)],
           shade, ol=None)
    # rock bands peeking through on the lower slopes
    for dx, dy, ww in ((-300, -110, 80), (-170, -50, 100), (230, -70, 70), (390, -36, 90), (-40, -150, 50)):
        c.poly([(x + (dx - ww / 2) * s, base + dy * s), (x + (dx + ww * 0.1) * s, base + (dy - 46) * s),
                (x + (dx + ww * 0.25) * s, base + (dy - 40) * s), (x + (dx + ww / 2) * s, base + dy * s)],
               mix(rock, snow, 0.55), ol=None)
    if glow:
        # warm light catching the summit at sunrise
        c.poly([(x - 55 * s, base - 424 * s), (x, base - 430 * s), (x + 45 * s, base - 427 * s),
                (x + 115 * s, base - 406 * s), (x + 60 * s, base - 380 * s), (x - 90 * s, base - 380 * s)],
               glow, ol=None)


def pine(c, x, y, s=1.0, snowy=True, col=PINE, dark=PINE_D):
    c.push(x, y, s)
    c.rect(-6, -26, 6, 0, (110, 76, 52), w=2)
    for k, (w2, top, bot) in enumerate(((52, -96, -20), (42, -136, -62), (30, -170, -104))):
        c.poly([(-w2, bot), (0, top), (w2, bot)], col, w=2.5)
        c.poly([(0, top), (w2, bot), (w2 * 0.2, bot)], dark, ol=None)
        if snowy:
            sw = w2 * 0.55
            c.poly([(0, top), (sw, top + (bot - top) * 0.55), (sw * 0.3, top + (bot - top) * 0.42),
                    (-sw * 0.2, top + (bot - top) * 0.6), (-sw, top + (bot - top) * 0.5)], SNOW, ol=None)
    c.pop()


def snow_mound(c, x, y, rx, ry, col=SNOW, shade=SNOW_SH, ol=OUT):
    """A hump of snow sitting on the ground line y (height ry)."""
    pts = [(x + rx * math.cos(a), y - ry * math.sin(a) * (1 + 0.08 * math.sin(a * 5)))
           for a in np.linspace(0, math.pi, 24)]
    c.poly([(x + rx + 16, y + 6)] + pts + [(x - rx - 16, y + 6)], col, ol=None)
    c.line([(x + rx + 16, y + 4)] + pts + [(x - rx - 16, y + 4)], ol, 2.5)
    c.poly([(x + rx * 0.9, y)] + [(x + rx * 0.9 * math.cos(a), y - ry * 0.55 * math.sin(a))
                                   for a in np.linspace(0, math.pi / 2, 8)] + [(x, y)], shade, ol=None)
    c.rect(x - rx - 18, y + 1, x + rx + 18, y + 8, col, ol=None)


def chalet(c, x, y, s=1.0, lit=False, snow_roof=True, wall=(170, 110, 64), night=False):
    """Little wooden alpine chalet; origin at the bottom centre."""
    c.push(x, y, s)
    c.rect(-80, -110, 80, 0, (150, 140, 140), w=2.5)            # stone base
    c.rect(-80, -110, 80, -40, wall, w=2.5)
    for yy in range(-100, -40, 12):
        c.line([(-78, yy), (78, yy)], mix(wall, (60, 30, 20), 0.35), 1.5, cap=False)
    win = (255, 214, 110) if lit else (120, 170, 210)
    for wx in (-48, 22):
        c.rect(wx, -92, wx + 26, -62, win, w=2.5)
        c.line([(wx + 13, -92), (wx + 13, -62)], OUT, 2, cap=False)
        c.rect(wx - 8, -94, wx - 2, -60, (60, 120, 70), w=1.5)
        c.rect(wx + 28, -94, wx + 34, -60, (60, 120, 70), w=1.5)
        for fx in range(wx + 3, wx + 26, 8):                    # window box flowers
            c.circle(fx, -60, 3.5, (225, 60, 70), w=1)
    c.rect(-12, -38, 14, 0, (110, 70, 44), w=2.5)
    c.poly([(-112, -104), (0, -178), (112, -104), (96, -98), (0, -160), (-96, -98)], (120, 70, 50), w=2.5)
    c.poly([(-96, -104), (0, -168), (96, -104)], mix(wall, (90, 50, 30), 0.25), w=2.5)
    c.rect(-10, -146, 10, -126, win, w=2)
    if snow_roof:
        c.poly([(-118, -102), (0, -184), (118, -102), (100, -96), (60, -112), (20, -108), (-30, -116),
                (-80, -104), (-104, -94)], SNOW, w=2.5)
    c.rect(36, -200, 54, -150, (140, 120, 110), w=2)             # chimney
    c.rect(32, -206, 58, -198, SNOW if snow_roof else (120, 100, 95), w=2)
    c.pop()


def church(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-40, -100, 40, 0, (245, 236, 220), w=2.5)
    c.poly([(-50, -96), (0, -140), (50, -96)], (110, 80, 70), w=2.5)
    c.rect(-18, -230, 18, -100, (245, 236, 220), w=2.5)
    c.circle(0, -200, 9, (240, 210, 110), w=2)
    c.poly([(-24, -228), (0, -300), (24, -228)], (80, 110, 100), w=2.5)
    c.circle(0, -262, 12, (80, 110, 100), w=2.5)
    c.line([(0, -300), (0, -318)], OUT, 2.5)
    c.rect(-8, -40, 8, 0, (120, 80, 60), w=2)
    c.pop()


def sun(c, x, y, r, t=0.0, rays=True, col=(255, 236, 140), halo=(255, 190, 120), sky=(255, 160, 120)):
    c.glow(x, y, r * 3.2, r * 3.2, halo, sky, steps=10)
    if rays:
        for k in range(12):
            a = k * math.tau / 12 + t * 0.08
            p0 = (x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 1.25)
            p1 = (x + math.cos(a) * r * (1.9 + 0.15 * math.sin(t * 2 + k)), y + math.sin(a) * r * (1.9 + 0.15 * math.sin(t * 2 + k)))
            c.line([p0, p1], mix(col, halo, 0.3), 6)
    c.circle(x, y, r, col, ol=None)
    c.circle(x - r * 0.2, y - r * 0.2, r * 0.7, mix(col, (255, 255, 230), 0.5), ol=None)


def soft_cloud(c, x, y, s=1.0, col=(255, 255, 255), shade=None):
    """Puffy cloud with a flat shaded bottom (for seas of cloud)."""
    c.push(x, y, s)
    if shade:
        c.ellipse(0, 20, 110, 26, shade, ol=None)
    for dx, dy, r in ((-70, 4, 34), (-30, -18, 44), (20, -26, 50), (66, -6, 38), (95, 10, 26), (-100, 14, 22)):
        c.circle(dx, dy, r, col, ol=None)
    c.ellipse(0, 14, 115, 22, col, ol=None)
    c.pop()


def eagle(c, x, y, t, s=1.0, face=1):
    flap = math.sin(t * 5)
    c.push(x, y, s, flip=face < 0)
    col, dark = (120, 80, 50), (80, 52, 34)
    c.poly([(-6, 0), (-40, -18 - 22 * flap), (-70, -10 - 28 * flap), (-30, 8)], dark, w=2)
    c.poly([(6, 0), (40, -18 - 22 * flap), (70, -10 - 28 * flap), (30, 8)], dark, w=2)
    c.ellipse(0, 4, 26, 10, col, w=2)
    c.poly([(-24, 4), (-42, -2), (-42, 12)], dark, w=2)
    c.circle(26, -2, 9, (250, 250, 245), w=2)
    c.poly([(33, -4), (44, 0), (33, 3)], (250, 200, 60), w=1.5)
    c.circle(28, -4, 1.8, OUT, ol=None)
    c.pop()


def cow(c, x, y, s=1.0, face=1, t=0.0):
    c.push(x, y, s, flip=face < 0)
    for lx in (-30, -18, 22, 34):
        c.stroke([(lx, -30), (lx, 0)], (245, 240, 235), 8)
    c.ellipse(0, -44, 50, 26, (250, 248, 242), w=2.5)
    c.ellipse(-16, -50, 16, 12, (120, 80, 60), ol=None)
    c.ellipse(18, -36, 12, 9, (120, 80, 60), ol=None)
    hy = -56 + 2 * math.sin(t * 2)
    c.ellipse(52, hy, 16, 20, (250, 248, 242), w=2.5)
    c.ellipse(56, hy + 12, 13, 10, (245, 180, 180), w=2)
    c.poly([(42, hy - 18), (36, hy - 30), (48, hy - 20)], (240, 230, 200), w=1.5)
    c.circle(54, hy - 4, 2.5, OUT, ol=None)
    c.circle(44, hy + 26, 6, (230, 190, 60), w=2)                # cowbell
    c.stroke([(-50, -50), (-60, -26 + 3 * math.sin(t * 3))], (250, 248, 242), 4)
    c.pop()


def snowfall(c, t, n=120, seed=1, speed=60.0, drift=20.0, size=(1.5, 4.0), col=(255, 255, 255),
             camx=0.0, camy=0.0, parallax=1.0, region=(0, 0, W, H), streak=0.0):
    """Cheap falling snow: one numpy pass, then direct ellipse calls in screen space."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, 1, n)
    y0 = rng.uniform(0, 1, n)
    sz = rng.uniform(size[0], size[1], n)
    sp = speed * (0.6 + 0.8 * rng.uniform(0, 1, n)) * (sz / size[1]) ** 0.5
    ph = rng.uniform(0, math.tau, n)
    rx0, ry0, rx1, ry1 = region
    rw, rh = rx1 - rx0 + 40, ry1 - ry0 + 40
    xs = (x0 * rw + drift * t * sp / speed + 14 * np.sin(t * 1.3 + ph) - camx * parallax) % rw + rx0 - 20
    ys = (y0 * rh + sp * t - camy * parallax) % rh + ry0 - 20
    d = c.d
    colc = c.c(col)
    if streak:
        vx, vy = drift / speed, 1.0
        for x, y, r in zip(xs, ys, sz):
            d.line([(x * SS, y * SS), ((x - vx * streak * r) * SS, (y - vy * streak * r) * SS)],
                   fill=colc, width=max(1, int(r * SS * 0.9)))
    for x, y, r in zip(xs, ys, sz):
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=colc)


_shade_masks = {}


def shade_bottom(c, tl, t, strength=0.5, top=548):
    """Darken the bottom of the frame softly while a subtitle shows (white text on snow)."""
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
    c.img.paste((16, 18, 34), (0, top * SS, W * SS, H * SS), _shade_masks[q])


def overlay(c, col, alpha):
    """Mix the whole frame toward a colour (fog, whiteout, dusk)."""
    if alpha <= 0.003:
        return
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha))
    c.d = ImageDraw.Draw(c.img)


# ------------------------------------------------------------- vehicles

TRAIN_RED = (214, 44, 50)
TRAIN_DARK = (160, 30, 40)


def train_car(c, x, y, length=420, loco=False, inside=None, t=0.0, height=170):
    """A red mountain train car. inside(c, k, wx0, wy0, wx1, wy1) draws passengers in window k.

    Origin: bottom-left at the rail level.
    """
    top = y - height
    c.rect(x, top, x + length, y - 26, TRAIN_RED, r=14)
    c.rect(x + 4, top + 4, x + length - 4, top + 22, (235, 235, 240), ol=None, r=10)  # roof
    wins = []
    if loco:
        c.poly([(x + length, top + 20), (x + length + 44, top + 70), (x + length + 44, y - 26),
                (x + length, y - 26)], TRAIN_RED)
        c.poly([(x + length + 3, top + 34), (x + length + 34, top + 72), (x + length + 3, top + 72)],
               (170, 210, 235), w=2)
        c.circle(x + length + 30, y - 50, 9, (255, 240, 170), w=2)
        c.rect(x + 40, top - 16, x + 100, top + 2, (90, 90, 100), w=2)      # pantograph
        c.line([(x + 50, top - 16), (x + 82, top - 52), (x + 112, top - 16)], OUT, 3)
        c.line([(x + 60, top - 54), (x + 104, top - 54)], OUT, 3)
        wins = [(x + 40, top + 40, x + length - 40, y - 84)]
    else:
        n = 2
        ww = (length - 40) / n
        for k in range(n):
            wins.append((x + 20 + k * ww + 8, top + 40, x + 20 + (k + 1) * ww - 8, y - 84))
    for (a, b, cc, d) in wins:
        c.rect(a, b, cc, d, (70, 84, 112), w=3, r=8)
    if inside:
        for k, wbox in enumerate(wins):
            inside(c, k, *wbox)
    low = max(d for (_, _, _, d) in wins)
    c.rect(x + 1.5, low, x + length - 1.5, y - 27, TRAIN_RED, ol=None)
    c.line([(x, y - 27), (x, low)], OUT, 3, cap=False)
    c.line([(x + length, y - 27), (x + length, low)], OUT, 3, cap=False)
    c.rect(x + 1.5, y - 66, x + length - 1.5, y - 52, (245, 245, 245), ol=None)
    if loco:
        c.text(x + length / 2, y - 59, "MONT-BLANC EXPRESS", 11, TRAIN_DARK)
    for (a, b, cc, d) in wins:
        c.rect(a, b, cc, d, None, w=3, r=8)
        c.line([(a + 12, b + 10), (a + 46, b + 10)], (230, 240, 250), 3)
    c.rect(x, y - 26, x + length, y - 18, (60, 60, 70), ol=None)
    for wx in (x + 50, x + 110, x + length - 110, x + length - 50):
        c.circle(wx, y - 12, 14, (70, 70, 80), w=2.5)
        a = t + wx
        c.line([(wx, y - 12), (wx + 10 * math.cos(a), y - 12 + 10 * math.sin(a))], (150, 150, 160), 2.5)


def cable_cabin(c, x, y, s=1.0, swing=0.0, inside=None):
    """Cable-car cabin hanging from its carriage. (x, y) is the grip point on the cable."""
    c.push(x, y, s)
    ang = swing
    ca, sa = math.cos(ang), math.sin(ang)

    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)

    # carriage wheels on the cable
    c.rect(-40, -14, 40, 6, (90, 90, 100), w=2.5, r=4)
    for wx in (-26, 26):
        c.circle(wx, -8, 8, (60, 60, 70), w=2)
    # hanger arm
    c.line([R(0, 6), R(0, 70)], OUT, 9)
    c.line([R(0, 6), R(0, 70)], (150, 150, 160), 5)
    # cabin body (rotated rectangle as polygon)
    body = [R(-130, 70), R(130, 70), R(140, 250), R(-140, 250)]
    c.poly([R(-120, 62), R(120, 62), R(130, 74), R(-130, 74)], (190, 190, 200), w=2.5)
    c.poly(body, (226, 44, 56), w=3)
    win = [R(-118, 86), R(118, 86), R(124, 196), R(-124, 196)]
    c.poly(win, (176, 214, 240), w=3)
    if inside:
        inside(c, R)
    # window frame bars over passengers
    c.poly([R(-128, 196), R(128, 196), R(134, 214), R(-134, 214)], (226, 44, 56), ol=None)
    for bx in (-40, 40):
        c.line([R(bx, 86), R(bx * 1.03, 196)], (226, 44, 56), 6)
    c.poly(win, None, w=3)
    c.poly([R(-138, 214), R(138, 214), R(140, 250), R(-140, 250)], (190, 36, 48), w=3)
    c.line([R(-110, 92), R(-70, 92)], (240, 248, 255), 3)
    c.pop()


def sled(c, x, y, s=1.0, ang=0.0):
    c.push(x, y, s)
    ca, sa = math.cos(ang), math.sin(ang)

    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)
    c.poly([R(-150, -30), R(150, -30), R(150, -16), R(-150, -16)], (170, 110, 60), w=2.5)
    for k in range(-130, 140, 40):
        c.line([R(k, -30), R(k, -16)], (120, 76, 40), 2, cap=False)
    for k in (-110, 0, 110):
        c.line([R(k, -16), R(k, -4)], (110, 70, 40), 5)
    pts = [R(-160, 0), R(150, 0), R(175, -10), R(185, -30)]
    c.line(pts, OUT, 9)
    c.line(pts, (210, 60, 60), 5)
    c.pop()


# ------------------------------------------------------------ characters

BRUNO = dict(white=(248, 242, 232), brown=(176, 98, 48), dark=(120, 62, 32), muzzle=(255, 250, 244))


def bruno(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, mouth=0.0, eyes="open", lantern=False, sit=False,
          seed=3.3, tail=None):
    """Bruno the Saint Bernard: big, white and brown, droopy ears, a little barrel at his collar."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = BRUNO
    c.push(x, y, s, flip=face < 0)
    wag = math.sin(t * 5 + seed) if tail is None else tail
    if sit:
        by = -110
        # tail on the ground
        c.stroke([(-70, -14), (-110, -10 + 5 * wag), (-140, -22 + 8 * wag)], p["brown"], 22)
        c.ellipse(-30, -64, 80, 62, p["white"], w=3)              # haunch
        c.ellipse(-50, -84, 50, 40, p["brown"], ol=None)
        c.ellipse(30, -110, 62, 86, p["white"], w=3)              # chest
        c.ellipse(4, -150, 40, 38, p["brown"], ol=None)
        for fx in (30, 72):
            c.stroke([(fx, -90), (fx + 6, -6)], p["white"], 26)
            c.ellipse(fx + 12, -8, 22, 11, p["white"], w=3)
        hx, hy = 60, -206
    else:
        by = -112
        c.stroke([(-112, by - 18), (-148, by - 52 - 10 * wag), (-166, by - 96 - 14 * wag)], p["brown"], 22)
        c.circle(-166, by - 100 - 14 * wag, 10, p["white"], ol=None)

        def leg(lx, ph, col, top):
            sw = math.sin(walk + ph) if walk else 0.0
            lift = -max(0.0, math.cos(walk + ph)) * 10 if walk else 0.0
            foot = (lx + sw * 16, lift - 4)
            c.stroke([(lx, by + top), foot], col, 30)
            c.ellipse(foot[0] + 8, foot[1], 20, 10, col, w=3)

        leg(-74, math.pi, mix(p["white"], (150, 140, 150), 0.3), 10)
        leg(66, 0, mix(p["white"], (150, 140, 150), 0.3), 10)
        c.ellipse(0, by, 122, 66, p["white"], w=3)
        c.ellipse(-16, by - 22, 84, 36, p["brown"], ol=None)      # saddle patch
        c.ellipse(-88, by - 6, 28, 30, p["brown"], ol=None)
        leg(-56, 0, p["white"], 44)
        leg(84, math.pi, p["white"], 44)
        bob = math.sin(walk * 2) * 3 if walk else 0
        hx, hy = 118, by - 72 + bob
    # head
    c.poly([(hx - 40, hy - 18), (hx - 62, hy + 30), (hx - 38, hy + 42), (hx - 22, hy + 6)], p["dark"], w=3)  # ear
    c.ellipse(hx, hy, 50, 46, p["brown"], w=3)
    c.ellipse(hx + 6, hy - 6, 9, 34, p["white"], ol=None)          # blaze
    c.ellipse(hx + 22, hy + 22, 38, 26, p["muzzle"], w=2.5)        # muzzle / jowls
    c.ellipse(hx + 52, hy + 8, 11, 8, (40, 30, 34), w=2)           # nose
    c.circle(hx + 49, hy + 5, 2.5, (140, 130, 140), ol=None)
    for ex in (hx + 4, hx + 30):
        ey = hy - 12
        if eyes == "closed":
            c.arc(ex, ey, 7, 5, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 7, 7, 200, 340, OUT, 3)
        else:
            c.ellipse(ex, ey, 6.5, 7.5, (255, 255, 255), w=2)
            c.ellipse(ex + 1.5, ey + 1, 4.2, 5.2, (90, 50, 30), ol=None)
            c.circle(ex + 2.5, ey - 1.5, 1.6, (255, 255, 255), ol=None)
        c.line([(ex - 8, ey - 12), (ex + 6, ey - 15)], p["dark"], 3)  # kind brows
    if mouth > 0.05:
        h = 4 + 12 * mouth
        c.ellipse(hx + 30, hy + 34 + h * 0.4, 14, h, D.MOUTH, w=2)
        c.ellipse(hx + 30, hy + 34 + h * 0.8, 9, 3 + 2 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 30, hy + 26, 16, 10, 20, 160, OUT, 2.5)
    # collar and barrel
    c.rect(hx - 34, hy + 40, hx + 30, hy + 52, (200, 40, 50), w=2.5, r=4)
    c.ellipse(hx - 2, hy + 74, 22, 18, (176, 116, 62), w=2.5)
    c.line([(hx - 16, hy + 62), (hx - 16, hy + 86)], (90, 90, 100), 3, cap=False)
    c.line([(hx + 12, hy + 62), (hx + 12, hy + 86)], (90, 90, 100), 3, cap=False)
    c.circle(hx + 22, hy + 74, 4, (110, 70, 40), w=1.5)
    if lantern:
        c.line([(hx + 24, hy + 50), (hx + 70, hy + 70)], OUT, 3)
        lx, ly = hx + 72, hy + 96 + 3 * math.sin(t * 3)
        c.circle(lx, ly - 2, 28, mix((255, 236, 160), (255, 255, 255), 0.3), ol=None)
        c.rect(lx - 12, ly - 22, lx + 12, ly + 16, (255, 220, 120), w=2.5, r=3)
        c.circle(lx, ly - 4, 6, (255, 250, 210), ol=None)
        c.poly([(lx - 14, ly - 22), (lx, ly - 34), (lx + 14, ly - 22)], (60, 60, 70), w=2)
    c.pop()


MARGOT = dict(fur=(158, 112, 70), dark=(110, 76, 48), belly=(214, 180, 130), beret=(56, 72, 150))


def margot(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, wave=0.0, seed=4.4, hop=0.0):
    """Margot the marmot: round, brown, buck teeth, a little blue beret."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = MARGOT
    c.push(x, y - hop, s, flip=face < 0)
    c.ellipse(-22, -12, 12, 9, p["dark"], w=2.5)                    # bushy tail
    for fx, ph in ((-8, 0), (10, math.pi)):
        lift = -max(0.0, math.cos(walk + ph)) * 5 if walk else 0
        c.ellipse(fx + (math.sin(walk + ph) * 5 if walk else 0), lift - 3, 9, 5, p["dark"], w=2)
    c.ellipse(0, -32, 24, 32, p["fur"], w=2.5)
    c.ellipse(6, -28, 14, 22, p["belly"], ol=None)
    hx, hy = 4, -70
    c.circle(hx - 12, hy - 14, 6, p["fur"], w=2)
    c.circle(hx - 12, hy - 14, 3, p["dark"], ol=None)
    c.circle(hx + 12, hy - 16, 6, p["fur"], w=2)
    c.circle(hx + 12, hy - 16, 3, p["dark"], ol=None)
    c.ellipse(hx, hy, 20, 18, p["fur"], w=2.5)
    c.ellipse(hx + 11, hy + 6, 11, 9, p["belly"], ol=None)
    c.ellipse(hx + 20, hy + 1, 4, 3, (50, 34, 30), ol=None)
    # beret
    c.ellipse(hx - 2, hy - 17, 17, 6, p["beret"], w=2)
    c.line([(hx - 2, hy - 23), (hx - 1, hy - 28)], p["beret"], 3)
    for ex in (hx + 2, hx + 14):
        ey = hy - 3
        if eyes == "closed":
            c.arc(ex, ey, 3.5, 2.5, 20, 160, OUT, 2)
        elif eyes == "happy":
            c.arc(ex, ey + 1, 3.5, 3.5, 200, 340, OUT, 2)
        elif eyes == "wide":
            c.circle(ex, ey, 4, (255, 255, 255), w=1.5)
            c.circle(ex + 0.5, ey, 2.2, (25, 20, 25), ol=None)
        else:
            c.ellipse(ex, ey, 2.6, 3.2, (25, 20, 25), ol=None)
            c.circle(ex + 0.8, ey - 1.2, 1, (255, 255, 255), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 13, hy + 13, 4, 1.5 + 4 * mouth, D.MOUTH, w=1.5)
    c.rect(hx + 10, hy + 8, hx + 17, hy + 14, (255, 255, 250), w=1.2, r=1)   # buck teeth
    c.line([(hx + 13.5, hy + 8), (hx + 13.5, hy + 14)], OUT, 1, cap=False)
    for dy in (-1, 2):
        c.line([(hx + 22, hy + 4), (hx + 34, hy + 1 + dy * 2)], OUT, 1, cap=False)
    # paws: held at the chest, or one waving
    c.ellipse(14, -46, 6, 5, p["dark"], w=1.8)
    if wave:
        a = -1.2 + 0.5 * math.sin(t * 10)
        c.stroke([(-6, -50), (-6 + 22 * math.cos(a), -50 + 22 * math.sin(a))], p["fur"], 7)
    else:
        c.ellipse(4, -44, 6, 5, p["dark"], w=1.8)
    c.pop()


def whiskers_scarf(c, x, y, s=1.0, face=1, pose="stand", t=0.0, head_dy=0.0, walk=0.0):
    """A cosy green striped scarf for Whiskers, drawn over the cat (same pose/position)."""
    if pose in ("stand", "walk"):
        bob = math.sin(walk * 2) * 2 if walk else 0
        hx, hy = 52, -48 - 38 + bob + head_dy
    elif pose == "crouch":
        hx, hy = 52, -40 - 38 + 14 + head_dy
    elif pose == "sit":
        hx, hy = 18, -106 + head_dy
    elif pose == "leap":
        hx, hy = 58, -48 - 26
    else:
        return
    col, stripe = (60, 150, 100), (240, 240, 230)
    c.push(x, y, s, flip=face < 0)
    flap = math.sin(t * 6) * 5
    tail = [(hx - 18, hy + 26), (hx - 46, hy + 30 + flap), (hx - 52, hy + 44 + flap), (hx - 22, hy + 38)]
    c.poly(tail, col, w=2.5)
    c.line([(hx - 36, hy + 31 + flap * 0.7), (hx - 40, hy + 41 + flap * 0.7)], stripe, 3, cap=False)
    c.rect(hx - 24, hy + 22, hx + 24, hy + 34, col, w=2.5, r=5)
    for sx in (-12, 2, 16):
        c.line([(hx + sx, hy + 23), (hx + sx, hy + 33)], stripe, 3, cap=False)
    c.pop()


def postcard_img(w=420, h=280):
    """The postcard picture: Mont Blanc in summer-blue sky, 'Greetings from MONT BLANC'."""
    c = Canvas(D.gradient(w * SS, h * SS, [(0, (110, 180, 240)), (0.75, (210, 236, 255)), (1, (210, 236, 255))]),
               size=(w, h))
    sun(c, w * 0.12, h * 0.42, 16, rays=False, sky=(150, 205, 245), halo=(220, 235, 250))
    mont_blanc(c, w * 0.55, h * 0.9, 0.42)
    peak(c, w * 0.08, h * 0.95, 160, 120, seed=3)
    c.poly([(0, h * 0.86), (w * 0.4, h * 0.8), (w, h * 0.88), (w, h), (0, h)], (110, 170, 90), ol=None)
    for px in (30, 70, 330, 380):
        pine(c, px, h * 0.98, 0.35, snowy=False)
    c.text(w / 2, 30, "Greetings from", 20, (255, 255, 255), stroke=2)
    c.text(w / 2, 62, "MONT BLANC", 34, (230, 50, 60), stroke=3, stroke_fill=(255, 255, 255))
    return c.img
