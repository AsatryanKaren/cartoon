"""Props, landmarks and new characters for "Whiskers and the Loch Ness Secret".

All drawn in the shared flat style: origin at the bottom centre unless noted,
local units = output pixels at s=1, characters face right (face=-1 mirrors).
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.munich.props import shade_bottom, overlay, sparkles, ripple, rot  # noqa: F401  (read-only reuse)

# palette
STONE = (184, 166, 146)
STONE_SH = (146, 130, 118)
STONE_D = (118, 104, 98)
SLATE = (86, 92, 108)
SLATE_D = (64, 68, 84)
ROCK = (96, 86, 92)
ROCK_D = (72, 64, 72)
GRASS = (98, 146, 84)
HEATHER = (164, 96, 170)
HEATHER_L = (198, 136, 200)
SALTIRE = (0, 94, 184)
TARTAN_RED = (196, 36, 46)
TARTAN_GREEN = (40, 92, 64)
TARTAN_NAVY = (34, 44, 92)
SHORTBREAD = (240, 206, 140)
SHORTBREAD_D = (214, 170, 100)
NESSIE = (84, 168, 150)
NESSIE_D = (58, 130, 118)
NESSIE_L = (196, 232, 196)


# ================================================================ helpers

def jag(x0, x1, y, n, amp, seed=0, down=True):
    """Zigzag fringe points from x0 to x1 around height y (for shaggy fur)."""
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n + 1):
        u = i / n
        x = lerp(x0, x1, u)
        if i % 2:
            pts.append((x, y + (amp * rng.uniform(0.7, 1.2)) * (1 if down else -1)))
        else:
            pts.append((x, y))
    return pts


def tartan(c, x0, y0, x1, y1, base=TARTAN_RED, bands=((TARTAN_NAVY, 0.22), (TARTAN_GREEN, 0.12)),
           line=(250, 230, 120), step=26, ol=OUT, w=2.5, r=0):
    """A rectangle of tartan: base colour with crossing bands and thin over-check lines."""
    c.rect(x0, y0, x1, y1, base, ol=None, r=r)
    wdt = x1 - x0
    hgt = y1 - y0
    for col, f in bands:
        bw = step * f * 2.2
        x = x0 + step * 0.3
        while x < x1 - 2:
            c.rect(x, y0, min(x1, x + bw), y1, mix(col, base, 0.35), ol=None)
            x += step
        y = y0 + step * 0.3
        while y < y1 - 2:
            c.rect(x0, y, x1, min(y1, y + bw), mix(col, base, 0.25), ol=None)
            y += step
    if line:
        x = x0 + step * 0.75
        while x < x1:
            c.line([(x, y0), (x, y1)], line, 1.2, cap=False)
            x += step
        y = y0 + step * 0.75
        while y < y1:
            c.line([(x0, y), (x1, y)], line, 1.2, cap=False)
            y += step
    if ol:
        c.rect(x0, y0, x1, y1, None, ol=ol, w=w, r=r)
    return wdt, hgt


def fog_layer(seed=0, density=1.0, col=(232, 234, 238)):
    """A soft, blobby sea-fog (haar) layer: returns (rgb_image, alpha_mask) at supersampled size."""
    w, h = W * SS // 4, H * SS // 4
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    rng = np.random.default_rng(seed)
    for _ in range(int(70 * density)):
        x, y = rng.uniform(-50, w + 50), rng.uniform(h * 0.15, h * 1.05)
        rx, ry = rng.uniform(60, 180), rng.uniform(20, 50)
        md.ellipse([x - rx, y - ry, x + rx, y + ry], fill=int(rng.uniform(120, 230)))
    md.rectangle([0, int(h * 0.55), w, h], fill=210)
    mask = mask.filter(ImageFilter.GaussianBlur(30)).resize((W * SS, H * SS), Image.BILINEAR)
    return Image.new("RGB", (W * SS, H * SS), col), mask


_fog_scaled = {}


def apply_fog(c, fog, k):
    """Composite a fog layer at strength k (0..1), quantised so masks can be cached."""
    q = int(round(clamp(k) * 24))
    if q <= 0:
        return
    key = (id(fog[1]), q)
    if key not in _fog_scaled:
        _fog_scaled[key] = fog[1].point(lambda a, q=q: int(a * q / 24))
        if len(_fog_scaled) > 80:
            _fog_scaled.pop(next(iter(_fog_scaled)))
    c.img.paste(fog[0], (0, 0), _fog_scaled[key])


def hill(c, pts_y, x0, x1, col, ol=None, base=H + 400, lw=2.5):
    n = len(pts_y)
    xs = np.linspace(x0, x1, 70)
    ys = np.interp(np.linspace(0, n - 1, 70), np.arange(n), pts_y)
    ys = [y + 0 for y in ys]
    pts = [(x0, base)] + list(zip(xs, ys)) + [(x1, base)]
    c.poly(pts, col, ol=None)
    if ol:
        c.line(list(zip(xs, ys)), ol, lw)


def heather_patch(c, x, y, w, seed=0, col=HEATHER, light=HEATHER_L, n=None):
    """Clumps of purple heather: dark green tufts dotted with purple bells."""
    rng = np.random.default_rng(seed)
    n = n or int(w / 14)
    for _ in range(n):
        px = x + rng.uniform(-w / 2, w / 2)
        py = y + rng.uniform(-6, 6)
        r = rng.uniform(8, 16)
        c.ellipse(px, py - r * 0.4, r * 1.3, r * 0.7, (70, 98, 66), ol=None)
        for _k in range(5):
            c.circle(px + rng.uniform(-r, r), py - r * 0.4 + rng.uniform(-r * 0.6, r * 0.3), rng.uniform(2.5, 4.5),
                     mix(col, light, rng.uniform(0, 1)), ol=None)


def thistle(c, x, y, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (2, -60)], (80, 130, 80), 4)
    for side in (-1, 1):
        c.poly([(0, -24), (side * 22, -34), (side * 10, -28), (side * 18, -20)], (90, 150, 90), w=1.5)
    c.ellipse(2, -66, 10, 9, (110, 160, 100), w=2)
    for k in range(7):
        a = math.radians(-150 + k * 20)
        c.line([(2, -72), (2 + math.cos(a) * 14, -72 + math.sin(a) * 16)], (170, 80, 190), 3.5)
    c.pop()


def saltire(c, x, y, s=1.0, t=0.0, pole=90):
    """Scotland's flag: white cross on blue, on a little pole. origin = pole foot."""
    c.push(x, y, s)
    c.line([(0, 0), (0, -pole)], (90, 80, 70), 3)
    fw, fh = 54, 34
    pts = []
    top = -pole
    for k in range(9):
        u = k / 8
        pts.append((u * fw, top + 3 * math.sin(t * 4 + u * 5) * u))
    bot = [(px, py + fh) for px, py in reversed(pts)]
    c.poly(pts + bot, SALTIRE, w=2)
    m = lambda u, v: (u * fw, top + 3 * math.sin(t * 4 + u * 5) * u + v * fh)  # noqa: E731
    c.line([m(0.04, 0.08), m(0.96, 0.92)], (255, 255, 255), 5, cap=False)
    c.line([m(0.04, 0.92), m(0.96, 0.08)], (255, 255, 255), 5, cap=False)
    c.pop()


def smoke_puff(c, x, y, k, s=1.0, seed=0, col=(236, 234, 228)):
    """A cannon smoke cloud growing and fading with k in 0..1."""
    if k <= 0 or k >= 1:
        return
    rng = np.random.default_rng(seed)
    a = 1 - k
    for i in range(9):
        ang = rng.uniform(0, math.tau)
        d = rng.uniform(10, 70) * (0.3 + k) * s
        r = rng.uniform(18, 40) * (0.4 + 1.2 * k) * s
        c.circle(x + math.cos(ang) * d + 40 * k * s, y + math.sin(ang) * d * 0.6 - 30 * k * s, r,
                 mix((150, 150, 150), col, 0.4 + 0.6 * a), ol=None)


# ================================================================ food & things

def shortbread(c, x, y, s=1.0, ang=0.0, bite=0.0):
    """A shortbread finger (centre origin)."""
    c.push(x, y, s)
    w2 = 26 * (1 - 0.45 * bite)
    pts = rot([(-26, -10), (-26 + 2 * w2, -10), (-26 + 2 * w2, 10), (-26, 10)], ang)
    c.poly(pts, SHORTBREAD, w=2)
    for k in range(3):
        px = -18 + k * 14
        if px < -26 + 2 * w2 - 6:
            for py in (-4, 4):
                q = rot([(px, py)], ang)[0]
                c.circle(q[0], q[1], 1.6, SHORTBREAD_D, ol=None)
    c.pop()


def tablet(c, x, y, s=1.0):
    """A square of Scottish tablet: pale, crumbly fudge (centre origin)."""
    c.push(x, y, s)
    c.rect(-14, -11, 14, 11, (246, 222, 170), w=2, r=2)
    c.rect(-10, -8, 6, -2, (255, 238, 200), ol=None)
    for dx, dy in ((-6, 4), (5, 2), (8, -6)):
        c.circle(dx, dy, 1.4, (214, 180, 120), ol=None)
    c.pop()


def tablet_bag(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-26, 0), (26, 0), (30, -56), (-30, -56)], (250, 248, 240), w=2.5)
    c.poly([(-30, -56), (30, -56), (24, -64), (-24, -64)], (230, 226, 216), w=2)
    for k in range(4):
        c.line([(-26 + k * 17, -4), (-29 + k * 19, -52)], (200, 60, 70), 3, cap=False)
    c.text(0, -28, "TABLET", 11, (60, 40, 40))
    c.pop()


def tin(c, x, y, s=1.0, lid=0.0, label=True):
    """The tartan shortbread tin (round, seen from slightly above). lid: 0 on, 1 off (leaning beside)."""
    c.push(x, y, s)
    rw, rh, h = 70, 22, 70
    c.ellipse(0, 0, rw, rh, mix(TARTAN_RED, (0, 0, 0), 0.3), w=2.5)
    tartan(c, -rw, -h, rw, 0, ol=None, step=22)
    c.line([(-rw, -h), (-rw, 0)], OUT, 2.5)
    c.line([(rw, -h), (rw, 0)], OUT, 2.5)
    c.arc(0, 0, rw, rh, 0, 180, OUT, 2.5)
    # inside / or lid on top
    if lid < 0.5:
        c.ellipse(0, -h, rw, rh, TARTAN_RED, w=2.5)
        c.ellipse(0, -h, rw - 10, rh - 5, (250, 238, 210), w=2)
        if label:
            c.text(0, -h, "SHORTBREAD", 13, (150, 30, 40))
    else:
        c.ellipse(0, -h, rw, rh, (210, 210, 216), w=2.5)
        c.ellipse(0, -h + 3, rw - 8, rh - 5, (232, 232, 238), ol=None)
        for dx in (-30, 6, 30):
            c.circle(dx, -h + 6, 3, SHORTBREAD_D, ol=None)       # crumbs
    c.pop()


def tin_lid_leaning(c, x, y, s=1.0):
    """The lid propped on its edge, inside facing us (shows the printed contest)."""
    c.push(x, y, s)
    c.ellipse(0, -60, 50, 62, TARTAN_RED, w=2.5)
    c.ellipse(0, -60, 42, 54, (250, 240, 214), w=2)
    c.text(0, -84, "WIN!", 13, (190, 40, 50))
    nessie_icon(c, 0, -46, 0.35)
    c.pop()


def nessie_icon(c, x, y, s=1.0, col=NESSIE):
    """A tiny printed picture of the monster (three humps and a head) for the lid / photo."""
    c.push(x, y, s)
    c.line([(-80, 10), (90, 10)], (90, 140, 200), 4)
    for hx in (-40, 0):
        c.arc(hx, 10, 16, 20, 180, 360, col, 7)
    c.stroke([(28, 10), (34, -20), (44, -40), (58, -42)], col, 9, ol=None)
    c.circle(60, -42, 7, col, ol=None)
    c.pop()


def lid_card(c, x, y, k, t=0.0):
    """Close-up of the inside of the lid: the contest text."""
    if k <= 0.02:
        return
    c.push(x, y, 0.4 + 0.6 * ease(k))
    c.ellipse(0, 0, 330, 200, TARTAN_RED, w=4)
    c.ellipse(0, 0, 300, 176, (252, 244, 222), w=3)
    c.text(0, -110, "GRAND CONTEST!", 34, (190, 40, 50), stroke=0)
    c.text(0, -62, "Photograph the", 28, (60, 40, 50))
    c.text(0, -24, "LOCH NESS MONSTER", 36, (30, 90, 80))
    c.text(0, 18, "and win", 26, (60, 40, 50))
    c.text(0, 60, "SHORTBREAD FOR LIFE!", 34, (190, 40, 50))
    nessie_icon(c, 0, 130, 0.9)
    for k2, px in enumerate((-190, 190)):
        shortbread(c, px, 125, 1.3, ang=0.4 * (1 if k2 else -1))
    c.pop()


def camera(c, x, y, s=1.0, ang=0.0, flash=0.0):
    """Pip's little box camera (centre origin)."""
    c.push(x, y, s)
    c.poly(rot([(-22, -14), (22, -14), (22, 14), (-22, 14)], ang), (60, 60, 70), w=2)
    c.poly(rot([(-14, -20), (-2, -20), (-2, -14), (-14, -14)], ang), (60, 60, 70), w=2)
    p = rot([(6, 0)], ang)[0]
    c.circle(p[0], p[1], 10, (40, 40, 48), w=2)
    c.circle(p[0], p[1], 6, (110, 150, 200), ol=None)
    c.circle(p[0] - 2, p[1] - 2, 2, (230, 240, 255), ol=None)
    q = rot([(16, -9)], ang)[0]
    c.circle(q[0], q[1], 2.5, (220, 70, 60), ol=None)
    if flash > 0:
        c.glow(p[0], p[1], 60 * flash, 60 * flash, (255, 255, 240), (255, 250, 200), steps=6)
    c.pop()


def photo(c, x, y, k, t=0.0, blink_eye=False):
    """The one photo: two grinning cats at the loch, and 'a funny rock' behind them."""
    if k <= 0.02:
        return
    c.push(x, y, 0.3 + 0.7 * ease(k))
    c.rect(-250, -190, 250, 190, (252, 250, 244), w=3, r=6)
    sky = [(0, (60, 70, 130)), (1, (150, 130, 170))]
    c.rect(-226, -168, 226, 120, (100, 96, 150), ol=None)
    for i in range(10):
        c.rect(-226, -168 + i * 16, 226, -168 + (i + 1) * 16, mix(sky[0][1], sky[1][1], i / 9), ol=None)
    c.poly([(-226, -40), (-120, -80), (-20, -50), (80, -90), (226, -60), (226, 0), (-226, 0)], (60, 70, 90),
           ol=None)
    c.rect(-226, -10, 226, 120, (50, 70, 110), ol=None)
    # the 'rock': a dark green hump... with an eye
    c.ellipse(80, 0, 90, 46, (60, 110, 100), ol=OUT, w=2)
    c.rect(-10, 0, 172, 50, (50, 70, 110), ol=None)
    c.line([(-12, 0), (172, 0)], (90, 120, 160), 2)
    if not blink_eye:
        c.ellipse(120, -22, 6, 7, (255, 255, 255), w=1.5)
        c.circle(122, -22, 3.2, (30, 30, 30), ol=None)
    else:
        c.arc(120, -22, 6, 4, 20, 160, OUT, 2)
    c.rect(-226, 60, 226, 120, (130, 120, 110), ol=None)
    D.cat(c, -150, 118, D.LUNA, 0.62, 1, "sit", t=0.0, eyes="happy", seed=1.3)
    D.cat(c, -60, 118, D.WHISKERS, 0.62, -1, "sit", t=0.0, eyes="happy", mouth=0.5)
    c.rect(-226, -168, 226, 120, None, ol=OUT, w=2.5)
    c.text(0, 158, "Loch Ness", 24, (80, 70, 80))
    c.pop()


# ================================================================ Edinburgh

def castle_rock(c, x, y, s=1.0, night=0.0, lit=0.0, t=0.0, ol=OUT, flag=True):
    """Edinburgh Castle on its volcanic rock (classic north view). origin = bottom centre, ~760 x 480."""
    c.push(x, y, s)
    rk = mix(ROCK, (40, 40, 80), night * 0.5)
    rkd = mix(ROCK_D, (30, 30, 60), night * 0.5)
    st = mix(STONE, (90, 90, 130), night * 0.55)
    sts = mix(STONE_SH, (70, 70, 110), night * 0.55)
    sl = mix(SLATE, (40, 40, 70), night * 0.4)
    gr = mix(GRASS, (40, 60, 80), night * 0.6)
    # green slopes at the foot
    c.poly([(-420, 0), (-380, -70), (-300, -100), (300, -100), (390, -60), (430, 0)], gr, ol=ol, w=2.5)
    # the rock
    rock = [(-380, -40), (-330, -96), (-290, -150), (-230, -190), (-160, -212), (-80, -226), (20, -232),
            (110, -230), (190, -220), (250, -196), (300, -150), (334, -96), (360, -40), (300, -30), (-300, -30)]
    c.poly(rock, rk, ol=ol, w=2.5)
    for px, top, bot in ((-250, -180, -60), (-170, -205, -80), (-60, -222, -50), (60, -226, -70), (160, -218, -60),
                         (240, -196, -70), (-320, -120, -50), (300, -150, -50)):
        c.poly([(px, top), (px + 26, top + 10), (px + 14, bot), (px - 8, bot + 6)], rkd, ol=None)
    for px in (-200, -110, 0, 100, 200, 270):
        c.line([(px, -200), (px + 8, -140), (px - 4, -80)], rkd, 2)
    # trees at the foot
    rng = np.random.default_rng(3)
    for k in range(18):
        tx = -380 + k * 45 + rng.uniform(-10, 10)
        r = rng.uniform(16, 26)
        c.circle(tx, -40 - r * 0.5, r, mix((70, 120, 70), (30, 40, 70), night * 0.6), ol=ol, w=2)
    # ---- the castle on top
    # long barracks (left)
    c.rect(-300, -270, -120, -200, st, ol=ol, w=2.5)
    c.poly([(-306, -270), (-114, -270), (-130, -290), (-290, -290)], sl, ol=ol, w=2.5)
    for row in (-255, -230):
        for wx in range(-288, -130, 18):
            c.rect(wx, row, wx + 8, row + 12, mix((60, 60, 80), (255, 210, 120), lit), ol=None)
    # curtain wall along the cliff
    c.rect(-330, -210, 320, -186, sts, ol=ol, w=2.5)
    for bx in range(-326, 316, 16):
        c.rect(bx, -218, bx + 9, -208, sts, ol=ol, w=1.5)
    # great hall + palace (centre right)
    c.rect(-110, -300, 60, -206, st, ol=ol, w=2.5)
    c.poly([(-116, -300), (66, -300), (50, -326), (-100, -326)], sl, ol=ol, w=2.5)
    for wx in range(-96, 50, 26):
        c.rect(wx, -282, wx + 12, -258, mix((60, 60, 80), (255, 210, 120), lit), ol=ol, w=1.5)
        c.rect(wx, -244, wx + 12, -222, mix((60, 60, 80), (255, 210, 120), lit), ol=ol, w=1.5)
    # palace block with crow-stepped gables and a turret
    c.rect(60, -330, 170, -206, st, ol=ol, w=2.5)
    steps = [(60, -330), (60, -344), (74, -344), (74, -356), (88, -356), (88, -366), (142, -366), (142, -356),
             (156, -356), (156, -344), (170, -344), (170, -330)]
    c.poly(steps, st, ol=ol, w=2.5)
    for wx in (76, 104, 132):
        c.rect(wx, -312, wx + 14, -286, mix((60, 60, 80), (255, 210, 120), lit), ol=ol, w=1.5)
        c.rect(wx, -266, wx + 14, -240, mix((60, 60, 80), (255, 210, 120), lit), ol=ol, w=1.5)
    # clock-tower turret with an ogee cap
    c.rect(150, -400, 180, -330, st, ol=ol, w=2.5)
    c.poly([(146, -400), (184, -400), (176, -414), (170, -430), (165, -444), (160, -430), (154, -414)], sl,
           ol=ol, w=2.5)
    c.circle(165, -380, 8, (250, 246, 230), ol=ol, w=1.5)
    # half-moon battery (curved wall, right)
    c.poly([(176, -206), (176, -268), (210, -280), (250, -278), (282, -262), (296, -232), (296, -206)], sts,
           ol=ol, w=2.5)
    for bx in range(180, 296, 14):
        c.rect(bx, -282 + (bx - 180) * 0.12, bx + 8, -272 + (bx - 180) * 0.12, sts, ol=ol, w=1.5)
    # the tower on the left end (Argyle)
    c.rect(-150, -350, -110, -270, st, ol=ol, w=2.5)
    for bx in (-152, -138, -124):
        c.rect(bx, -360, bx + 10, -350, st, ol=ol, w=1.5)
    if flag:
        saltire(c, -130, -360, 1.0, t, pole=60)
    c.pop()


def tenement(c, x, y, w, h, col, seed=0, roof=SLATE, gable=False, lit=0.0, shop=None, ol=OUT, door=True):
    """A tall old stone house of the Old Town. origin = bottom left."""
    rng = np.random.default_rng(seed)
    c.rect(x, y - h, x + w, y, col, ol=ol, w=2.5)
    dark = mix(col, (0, 0, 0), 0.18)
    # stone courses
    for yy in range(int(y - h + 20), int(y - 10), 34):
        c.line([(x + 3, yy), (x + w - 3, yy)], mix(col, (0, 0, 0), 0.07), 1.5, cap=False)
    # roof
    if gable:
        top = y - h
        sx = (w - 30) / 8
        pts = [(x, top)]
        for i in range(4):
            pts += [(x + i * sx, top - 22 - i * 22), (x + (i + 1) * sx, top - 22 - i * 22)]
        pts.append((x + w / 2, top - 22 - 4 * 22 + 4))
        for i in range(3, -1, -1):
            pts += [(x + w - (i + 1) * sx, top - 22 - i * 22), (x + w - i * sx, top - 22 - i * 22)]
        pts.append((x + w, top))
        c.poly(pts, col, ol=ol, w=2.5)
        c.rect(x + w / 2 - 9, top - 62, x + w / 2 + 9, top - 40, (40, 40, 60), ol=ol, w=1.5)
    else:
        c.poly([(x - 6, y - h), (x + w + 6, y - h), (x + w - 10, y - h - 34), (x + 10, y - h - 34)], roof, ol=ol,
               w=2.5)
        for cx_ in (x + 24, x + w - 34):
            c.rect(cx_, y - h - 62, cx_ + 22, y - h - 28, dark, ol=ol, w=2)
            for k in range(3):
                c.rect(cx_ + 2 + k * 7, y - h - 72, cx_ + 7 + k * 7, y - h - 62, (190, 110, 80), ol=ol, w=1.2)
    # windows
    cols = max(2, int(w // 46))
    gap = w / cols
    floors = int((h - 70) // 62)
    for f in range(floors):
        wy = y - h + 22 + f * 62
        for k in range(cols):
            wx = x + gap * k + gap / 2 - 10
            on = rng.random() < lit
            glass = (255, 214, 120) if on else mix((70, 86, 120), col, 0.15)
            c.rect(wx, wy, wx + 20, wy + 34, glass, ol=ol, w=2)
            c.line([(wx + 10, wy), (wx + 10, wy + 34)], (240, 236, 226), 2, cap=False)
            c.line([(wx, wy + 17), (wx + 20, wy + 17)], (240, 236, 226), 2, cap=False)
    # ground floor: shop or door
    if shop:
        name, scol = shop
        c.rect(x + 8, y - 84, x + w - 8, y, scol, ol=ol, w=2.5)
        c.rect(x + 14, y - 82, x + w - 14, y - 62, mix(scol, (0, 0, 0), 0.3), ol=None)
        c.text(x + w / 2, y - 72, name, 13, (255, 240, 200))
        c.rect(x + 18, y - 56, x + w - 52, y - 6, (170, 210, 230), ol=ol, w=2)
        c.rect(x + w - 44, y - 58, x + w - 16, y, mix(scol, (0, 0, 0), 0.35), ol=ol, w=2)
    elif door:
        dx = x + w / 2
        c.rect(dx - 16, y - 54, dx + 16, y, (80, 50, 40), ol=ol, w=2, r=4)


def close_arch(c, x, y, name="Advocate's Close", w=56, h=110):
    """The dark, narrow opening of a close (alley) with its little name sign. origin = bottom centre."""
    c.rect(x - w / 2 - 8, y - h - 10, x + w / 2 + 8, y, STONE_SH, ol=OUT, w=2.5)
    c.poly([(x - w / 2, y), (x - w / 2, y - h + w / 2)] +
           [(x + math.cos(a) * w / 2, y - h + w / 2 - math.sin(a) * w / 2) for a in np.linspace(math.pi, 0, 12)] +
           [(x + w / 2, y)], (30, 26, 34), ol=OUT, w=2.5)
    c.poly([(x - w / 2 + 6, y), (x - 6, y - h + 30), (x + 6, y - h + 30), (x + w / 2 - 6, y)], (44, 40, 50),
           ol=None)
    c.rect(x - 58, y - h - 40, x + 58, y - h - 16, (30, 40, 70), ol=OUT, w=2)
    c.text(x, y - h - 28, name, 11, (240, 230, 200))


def st_giles(c, x, y, s=1.0, col=STONE_SH, ol=OUT):
    """The crown spire of St Giles' Cathedral: tower with an open stone crown. origin = bottom centre."""
    c.push(x, y, s)
    c.rect(-46, -300, 46, 0, col, ol=ol, w=2.5)
    for wy in (-270, -200):
        c.poly([(-14, wy + 50), (-14, wy + 12), (0, wy), (14, wy + 12), (14, wy + 50)], (50, 50, 70), ol=ol, w=2)
    c.rect(-52, -312, 52, -296, col, ol=ol, w=2)
    for bx in range(-50, 50, 12):
        c.rect(bx, -320, bx + 7, -312, col, ol=ol, w=1.2)
    # the crown: four flying ribs rising to the central lantern
    for sx in (-1, 1):
        pts = [(sx * 46, -320)] + [(sx * 46 * (1 - u), -320 - 70 * math.sin(u * math.pi / 2)) for u in
                                   np.linspace(0.1, 1, 8)]
        c.stroke(pts, col, 7, ol=ol)
        pts = [(sx * 22, -320)] + [(sx * 22 * (1 - u), -320 - 56 * math.sin(u * math.pi / 2)) for u in
                                   np.linspace(0.1, 1, 6)]
        c.stroke(pts, col, 5, ol=ol)
        for k in range(3):
            px = sx * (46 - k * 14)
            py = -320 - 70 * math.sin((k * 14 / 46) * math.pi / 2)
            c.poly([(px - 4, py), (px, py - 14), (px + 4, py)], col, ol=ol, w=1.2)
    c.rect(-10, -404, 10, -384, col, ol=ol, w=2)
    c.poly([(-8, -404), (0, -446), (8, -404)], col, ol=ol, w=2)
    c.pop()


def badger_piper(c, x, y, s=1.0, face=1, t=0.0, playing=True, seed=3.3):
    """A badger in a kilt playing the bagpipes. origin between the feet, ~170 tall."""
    c.push(x, y + (abs(math.sin(t * 4.4)) * -2 if playing else 0), s, flip=face < 0)
    grey, dark, white = (150, 150, 156), (40, 40, 46), (246, 246, 246)
    # legs + socks + shoes
    for lx in (-14, 14):
        c.rect(lx - 8, -46, lx + 8, -6, (240, 240, 232), ol=OUT, w=2)
        c.rect(lx - 8, -46, lx + 8, -38, TARTAN_RED, ol=None)
        c.ellipse(lx + 4, -4, 13, 6, (30, 30, 34), w=2)
    # kilt
    c.poly([(-34, -110), (34, -110), (40, -46), (-40, -46)], TARTAN_GREEN, ol=OUT, w=2.5)
    for k in range(7):
        kx = -36 + k * 12
        c.line([(kx * 0.86, -108), (kx, -48)], mix(TARTAN_NAVY, TARTAN_GREEN, 0.3), 3, cap=False)
    c.line([(-38, -76), (38, -76)], (220, 60, 60), 2, cap=False)
    c.rect(-10, -100, 10, -76, (240, 240, 236), ol=OUT, w=2, r=4)          # sporran
    c.circle(0, -84, 3, dark, ol=None)
    # body / jacket
    c.ellipse(0, -140, 36, 40, (40, 44, 70), w=2.5)
    for by in (-160, -146, -132):
        c.circle(6, by, 2.5, (230, 200, 90), ol=None)
    # bag under the arm, drones over the shoulder
    puff = 1 + 0.06 * math.sin(t * 3)
    for k, (dx, ln) in enumerate(((-8, 92), (-24, 80), (-38, 68))):
        bx0, by0 = -18 + k * 2, -150
        tip = (bx0 + dx - 26, by0 - ln)
        c.line([(bx0, by0), tip], (30, 30, 36), 6)
        c.rect(tip[0] - 5, tip[1] - 8, tip[0] + 5, tip[1] + 2, (240, 236, 220), ol=OUT, w=1.5)
        c.line([(bx0 + (tip[0] - bx0) * 0.5 - 4, by0 + (tip[1] - by0) * 0.5),
                (bx0 + (tip[0] - bx0) * 0.5 + 4, by0 + (tip[1] - by0) * 0.5)], (240, 236, 220), 4, cap=False)
    c.ellipse(-20, -144, 26 * puff, 20 * puff, TARTAN_RED, w=2.5)
    c.line([(-40, -140), (2, -150)], TARTAN_NAVY, 3, cap=False)
    # chanter in the paws
    c.line([(22, -150), (26, -100)], (30, 30, 36), 6)
    c.ellipse(24, -134, 8, 6, grey, w=2)
    c.ellipse(26, -112, 8, 6, grey, w=2)
    # head
    hx, hy = 14, -196
    c.ellipse(hx, hy, 28, 24, white, w=2.5)
    c.poly([(hx - 18, hy - 20), (hx - 4, hy - 22), (hx + 20, hy + 8), (hx + 10, hy + 12)], dark, ol=None)
    c.poly([(hx - 26, hy - 6), (hx - 22, hy - 18), (hx - 10, hy + 14), (hx - 18, hy + 16)], dark, ol=None)
    c.circle(hx - 22, hy - 18, 7, grey, w=2)
    c.circle(hx + 26, hy + 2, 4, dark, ol=None)
    eye = (hx + 4, hy - 4)
    if D.blink(t, seed) or playing:
        c.arc(eye[0], eye[1] + 1, 4, 3, 200, 340, white, 2)
    else:
        c.circle(eye[0], eye[1], 2.5, white, ol=None)
    # blowpipe into the mouth, puffed cheek
    c.line([(hx + 20, hy + 10), (-6, -160)], (30, 30, 36), 4)
    if playing:
        c.circle(hx + 14, hy + 8, 8 + 2 * math.sin(t * 6), white, w=2)
    # glengarry cap
    c.poly([(hx - 22, hy - 18), (hx + 16, hy - 26), (hx + 12, hy - 36), (hx - 18, hy - 30)], TARTAN_NAVY, w=2)
    c.line([(hx - 22, hy - 20), (hx - 32, hy - 8 + 3 * math.sin(t * 5))], (40, 40, 60), 2)
    c.pop()


DOUGAL = dict(fur=(186, 184, 190), dark=(136, 134, 146), light=(222, 222, 228))


def dougal(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, wag=None, sit=False, hop=0.0,
           seed=5.5, bonnet=True, ol=OUT, col=None):
    """Dougal the Skye terrier: long, low and shaggy, with a tartan bonnet. ~95 tall, ~150 long."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = dict(DOUGAL)
    if col:
        p = dict(fur=col[0], dark=col[1], light=col[2])
    fur, dark, light = p["fur"], p["dark"], p["light"]
    c.push(x, y - hop, s, flip=face < 0)
    wagv = math.sin(t * 12) if wag is None else wag
    # tail: a plume
    if sit:
        bx, by = -6, -36
        c.stroke([(-34, -16), (-50, -26), (-58, -44 - 6 * wagv)], fur, 10, ol=ol)
        c.ellipse(-4, -30, 34, 30, fur, ol=ol, w=2.5)
        c.poly(jag(-38, 30, -10, 10, 12, seed=2), fur, ol=None)
        c.ellipse(16, -6, 12, 6, dark, ol=ol, w=2)
        c.ellipse(-20, -6, 12, 6, dark, ol=ol, w=2)
        hx, hy = 22, -70
    else:
        c.stroke([(-56, -50), (-74, -64), (-78 + 8 * wagv, -86)], fur, 11, ol=ol)
        for k, lx in enumerate((-40, 34, -28, 46)):
            ph = walk + (math.pi if k % 2 else 0)
            fx = lx + (math.sin(ph) * 8 if walk else 0)
            lift = -max(0.0, math.cos(ph)) * 5 if walk else 0
            c.ellipse(fx, -4 + lift, 10, 6, dark if k < 2 else mix(dark, fur, 0.4), ol=ol, w=2)
        c.ellipse(0, -44, 64, 24, fur, ol=ol, w=2.5)
        # long hair hanging to the ground
        c.poly([(-62, -40)] + jag(-62, 64, -12, 16, 10, seed=1) + [(64, -40)], fur, ol=None)
        c.line(jag(-62, 64, -12, 16, 10, seed=1), ol, 2) if ol else None
        for k in range(6):
            px = -50 + k * 20
            c.line([(px, -54), (px + 4, -22)], dark, 2, cap=False)
        hx, hy = 64, -70
    # head
    c.ellipse(hx, hy, 24, 21, fur, ol=ol, w=2.5)
    # ears: pricked, with feathery fringes
    for ex, lean in ((hx - 14, -0.3), (hx + 4, 0.2)):
        tip = (ex + 10 * lean, hy - 46)
        c.poly([(ex - 9, hy - 14), tip, (ex + 9, hy - 14)], fur, ol=ol, w=2)
        c.poly([(ex - 9, hy - 18), (ex - 16, hy - 28), (ex - 9, hy - 26), (ex - 14, hy - 38), (tip[0], tip[1])],
               light, ol=None)
    # muzzle + nose
    c.ellipse(hx + 20, hy + 6, 14, 10, light, ol=ol, w=2)
    c.circle(hx + 32, hy + 2, 5, (30, 28, 32), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 22, hy + 16, 6, 2 + 6 * mouth, (120, 40, 50), ol=ol, w=1.5)
        c.ellipse(hx + 22, hy + 18 + 3 * mouth, 4, 2 + 2 * mouth, (240, 120, 130), ol=None)
    else:
        c.arc(hx + 22, hy + 13, 6, 3, 10, 170, ol or OUT, 1.5)
    # eyes peeking through a long fringe
    for ex in (hx - 2, hx + 12):
        if eyes == "closed":
            c.arc(ex, hy - 4, 4, 3, 20, 160, OUT, 2)
        elif eyes == "happy":
            c.arc(ex, hy - 2, 4, 4, 200, 340, OUT, 2)
        else:
            c.circle(ex, hy - 4, 3.6 if eyes != "wide" else 4.6, (30, 24, 28), ol=None)
            c.circle(ex + 1, hy - 5.5, 1.2, (255, 255, 255), ol=None)
    c.poly([(hx - 20, hy - 14)] + jag(hx - 20, hx + 22, hy - 10, 7, 7, seed=4) + [(hx + 22, hy - 16), (hx, hy - 22)],
           light, ol=None)
    if bonnet:
        c.ellipse(hx - 2, hy - 20, 22, 7, TARTAN_RED, ol=ol, w=2)
        c.rect(hx - 20, hy - 22, hx + 16, hy - 16, TARTAN_NAVY, ol=None)
        c.line([(hx - 18, hy - 19), (hx + 14, hy - 19)], (240, 210, 90), 1.5, cap=False)
        c.circle(hx - 2, hy - 30, 6, (220, 40, 50), ol=ol, w=1.5)
    c.pop()


HAMISH = dict(coat=(206, 112, 52), dark=(168, 82, 38), light=(234, 150, 84), horn=(240, 228, 196),
              muzzle=(222, 160, 136))


def hamish(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, peek=0.0, head_dy=0.0, seed=6.6, dizzy=0.0):
    """Hamish the Highland cow: ginger, shaggy, long horns, a fringe over his eyes.
    origin between the hooves; ~330 long, back at y=-190 (riders sit at x in -90..60)."""
    p = HAMISH
    c.push(x, y, s, flip=face < 0)
    by = -128
    # tail
    tw = math.sin(t * 2.5 + seed)
    c.stroke([(-140, by - 30), (-158, by + 10 + 6 * tw), (-160, by + 50)], p["coat"], 9)
    c.poly(jag(-172, -146, by + 50, 4, 16, seed=7), p["dark"], ol=OUT, w=1.5)
    # legs
    for k, lx in enumerate((-96, 80, -70, 104)):
        ph = walk + (math.pi if k in (1, 2) else 0)
        sw = math.sin(ph) * 10 if walk else 0
        lift = -max(0.0, math.cos(ph)) * 6 if walk else 0
        col = p["dark"] if k < 2 else p["coat"]
        c.stroke([(lx, by + 30), (lx + sw, lift - 8)], col, 24)
        c.rect(lx + sw - 12, lift - 14, lx + sw + 12, lift, (60, 40, 30), ol=OUT, w=2, r=3)
    # body: a big shaggy barrel
    c.ellipse(0, by - 8, 150, 70, p["coat"], w=2.5)
    c.poly([(-148, by - 4)] + jag(-148, 148, by + 52, 24, 16, seed=1) + [(148, by - 4)], p["coat"], ol=None)
    c.line(jag(-148, 148, by + 52, 24, 16, seed=1), OUT, 2)
    rng = np.random.default_rng(2)
    for _ in range(22):
        px, py = rng.uniform(-130, 120), rng.uniform(by - 60, by + 40)
        c.arc(px, py, 10, 8, 200, 340, p["dark"], 2.5)
    for _ in range(10):
        px, py = rng.uniform(-110, 100), rng.uniform(by - 66, by - 30)
        c.arc(px, py, 9, 6, 200, 330, p["light"], 2.5)
    # head
    bob = math.sin(walk * 2) * 3 if walk else 0
    hx, hy = 150, by - 26 + head_dy + bob
    # ears + horns (behind head outline)
    for side in (-1, 1):
        ex = hx + side * 30
        c.ellipse(ex + side * 8, hy - 18, 18, 8, p["dark"], w=2)
    for side in (-1, 1):
        base = (hx + side * 20, hy - 40)
        pts = [base, (hx + side * 62, hy - 52), (hx + side * 92, hy - 76), (hx + side * 98, hy - 104)]
        c.stroke(pts, p["horn"], 10)
        c.stroke(pts[-2:], (120, 100, 80), 6, ol=None)
    c.ellipse(hx, hy, 46, 50, p["coat"], w=2.5)
    # muzzle
    jaw = mouth * 10
    c.ellipse(hx + 2, hy + 38 + jaw * 0.3, 32, 20 + jaw * 0.4, p["muzzle"], w=2.5)
    if mouth > 0.05:
        c.ellipse(hx + 2, hy + 50 + jaw * 0.5, 16, 3 + jaw * 0.5, (120, 40, 50), w=1.5)
    for nx in (-10, 14):
        c.ellipse(hx + nx, hy + 34, 5, 4, (110, 60, 60), ol=None)
    # eyes (only when the fringe lifts) and the big fringe
    if peek > 0.05:
        for ex in (hx - 16, hx + 18):
            c.ellipse(ex, hy - 4, 7, 8, (255, 255, 255), w=2)
            c.circle(ex + 1, hy - 3, 4, (40, 30, 30), ol=None)
            c.circle(ex + 2, hy - 5, 1.3, (255, 255, 255), ol=None)
    lift = peek * 34
    c.poly([(hx - 46, hy - 16 - lift * 0.3), (hx - 30, hy - 52), (hx, hy - 60), (hx + 30, hy - 52),
            (hx + 46, hy - 16 - lift * 0.3)] + jag(hx + 46, hx - 46, hy + 18 - lift, 12, 14, seed=5),
           p["light"], w=2)
    for k in range(6):
        px = hx - 30 + k * 12
        c.line([(px, hy - 46), (px + 2, hy + 6 - lift)], p["coat"], 2.5, cap=False)
    if dizzy > 0:
        for k in range(4):
            a = t * 5 + k * math.tau / 4
            sx, sy = hx + math.cos(a) * 50, hy - 90 + math.sin(a) * 12
            c.poly([(sx, sy - 9), (sx + 3, sy - 3), (sx + 9, sy), (sx + 3, sy + 3), (sx, sy + 9), (sx - 3, sy + 3),
                    (sx - 9, sy), (sx - 3, sy - 3)], (255, 220, 80), w=1.5)
    c.pop()


def stag(c, x, y, s=1.0, face=1, t=0.0, roar=0.0, col=(160, 84, 52), ol=OUT):
    """A red deer stag with a great crown of antlers. origin between the hooves, ~260 tall."""
    c.push(x, y, s, flip=face < 0)
    dark = mix(col, (0, 0, 0), 0.25)
    by = -110
    for lx, cc in ((-50, dark), (44, dark), (-36, col), (58, col)):
        c.stroke([(lx, by + 6), (lx + 2, by + 56), (lx, -4)], cc, 10, ol=ol)
    c.ellipse(0, by, 70, 32, col, ol=ol, w=2.5)
    c.ellipse(-62, by - 6, 12, 12, (236, 214, 180), ol=ol, w=2)
    # neck with mane
    ang = -0.15 * roar
    hx, hy = 82, by - 80 + 10 * roar
    c.poly([(36, by - 20), (60, by - 64), (hx - 4, hy + 6), (hx + 10, hy + 18), (74, by + 10)], col, ol=ol, w=2.5)
    c.poly([(40, by - 10)] + jag(40, 64, by - 60, 6, 10, seed=3) + [(64, by - 60)], dark, ol=None)
    c.ellipse(hx + 8, hy + 8, 26, 15, col, ol=ol, w=2.5)
    c.ellipse(hx + 28, hy + 14 + 4 * roar, 10, 8 + 4 * roar, dark, ol=ol, w=2)
    c.circle(hx + 6, hy + 2, 3, OUT, ol=None)
    c.ellipse(hx - 10, hy - 6, 6, 12, col, ol=ol, w=2)
    ant = (130, 100, 70)
    for side in (-1, 1):
        bx = hx + (2 if side < 0 else 10)
        pts = [(bx, hy - 6), (bx - 10 * side - 4, hy - 50), (bx - 22 * side - 6, hy - 96), (bx - 16 * side - 2, hy - 130)]
        c.line(pts, ant, 5)
        for k, (u, ln) in enumerate(((0.3, 24), (0.55, 28), (0.8, 22))):
            px = lerp(pts[0][0], pts[-1][0], u) - 10 * side * u
            py = lerp(pts[0][1], pts[-1][1], u)
            c.line([(px, py), (px + 20, py - ln)], ant, 4)
    c.pop()


def goose(c, x, y, s=1.0, face=1, t=0.0, flap=None, seed=0.0, part="all", tint=None, carry=False):
    """A greylag goose in flight, side-on, facing right. origin = middle of the back.
    part: 'back' draws far wing + body + head, 'front' the near wing, 'all' both."""
    body = (150, 142, 130)
    belly = (214, 208, 196)
    wing = (118, 112, 106)
    wing_d = (84, 80, 78)
    if tint:
        body, belly, wing, wing_d = [mix(col, tint[0], tint[1]) for col in (body, belly, wing, wing_d)]
    ph = t * (7.0 if not carry else 9.0) + seed if flap is None else flap
    up = math.sin(ph)
    c.push(x, y, s, flip=face < 0)
    if part in ("all", "back"):
        # far wing
        c.poly([(-14, -2), (20, -6), (-10 - 20 * up, -60 * up - 6), (-40 - 30 * up, -50 * up)], wing_d, w=2)
        # body
        c.poly([(-70, 6), (-88, 2), (-74, 14)], (240, 240, 240), w=2)
        c.ellipse(-6, 10, 66, 22, body, w=2.5)
        c.ellipse(0, 20, 52, 11, belly, ol=None)
        # feet tucked
        c.poly([(-56, 26), (-74, 30), (-60, 22)], (240, 140, 90), w=1.5)
        # neck + head
        c.stroke([(48, 2), (76, -4), (98, -10)], body, 13)
        c.ellipse(108, -12, 16, 11, mix(body, (60, 60, 60), 0.15), w=2.5)
        c.poly([(120, -16), (142, -10), (120, -5)], (244, 150, 80), w=2)
        c.circle(112, -16, 2.6, (25, 20, 25), ol=None)
        c.circle(113, -17, 0.9, (255, 255, 255), ol=None)
    if part in ("all", "front"):
        # near wing: flaps through the body line
        tip = (-30 - 34 * up, -74 * up + 10)
        c.poly([(-24, 0), (28, -2), (14 - 10 * up, -40 * up), tip, (-46 - 10 * up, -20 * up + 6)], wing, w=2.5)
        for k in range(3):
            c.line([(-14 + 14 * k, -2), (tip[0] * (0.6 + 0.12 * k) + 4 * k, tip[1] * (0.6 + 0.12 * k))],
                   wing_d, 2)
    c.pop()


def goose_vee(c, x, y, t, n=7, s=0.25, spread=(60, 22), face=1, tint=None, seed=0.0):
    """A distant V of geese (small)."""
    for k in range(n):
        side = 1 if k % 2 else -1
        row = (k + 1) // 2
        gx = x - face * row * spread[0] * s / 0.25
        gy = y + side * row * spread[1] * s / 0.25 + math.sin(t * 1.5 + k) * 3
        goose(c, gx, gy, s, face, t, seed=seed + k * 0.9, tint=tint)


def bobby_statue(c, x, y, s=1.0, ol=OUT, glint=0.0):
    """Greyfriars Bobby: a granite fountain pillar with the little bronze dog on top. origin = base centre."""
    c.push(x, y, s)
    gran = (156, 96, 88)
    gran_d = (124, 74, 70)
    c.rect(-70, -26, 70, 0, gran_d, ol=ol, w=2.5)
    c.rect(-54, -60, 54, -26, gran, ol=ol, w=2.5)
    c.ellipse(-30, -40, 10, 6, (100, 140, 170), ol=ol, w=1.5)       # the little drinking trough
    c.rect(-30, -200, 30, -60, gran, ol=ol, w=2.5)
    c.rect(-22, -180, 22, -100, gran_d, ol=None)
    c.text(0, -150, "BOBBY", 11, (240, 214, 150))
    c.rect(-44, -222, 44, -200, gran, ol=ol, w=2.5)
    c.rect(-38, -232, 38, -222, gran_d, ol=ol, w=2)
    # the bronze dog (a Skye terrier, sitting)
    bronze = (122, 92, 58)
    bronze_l = (168, 132, 84)
    dougal(c, 0, -232, 0.55, 1, 0.0, eyes="open", sit=True, bonnet=False, wag=0.0, ol=ol,
           col=(bronze, mix(bronze, (0, 0, 0), 0.25), bronze_l), seed=99.0)
    # his famous shiny nose
    c.circle(0 + 0.55 * (22 + 32), -232 + 0.55 * (-70 + 2), 2.8, (240, 200, 110), ol=None)
    if glint > 0:
        sparkles(c, 24, -268, glint * 10, n=5, r=26, seed=3, col=(255, 236, 160))
    c.pop()


def gravestone(c, x, y, w=40, h=60, col=(150, 150, 150), ol=OUT, kind=0):
    if kind == 0:
        c.rect(x - w / 2, y - h + w / 2, x + w / 2, y, col, ol=ol, w=2)
        c.circle(x, y - h + w / 2, w / 2, col, ol=ol, w=2)
        c.rect(x - w / 2 + 2, y - h + w / 2, x + w / 2 - 2, y - 2, col, ol=None)
    elif kind == 1:
        c.rect(x - 5, y - h, x + 5, y, col, ol=ol, w=2)
        c.rect(x - w / 2, y - h * 0.75, x + w / 2, y - h * 0.6, col, ol=ol, w=2)
        c.rect(x - 4, y - h + 1, x + 4, y - 2, col, ol=None)
    else:
        c.rect(x - w / 2, y - h, x + w / 2, y, col, ol=ol, w=2)
        c.poly([(x - w / 2 - 4, y - h), (x, y - h - 16), (x + w / 2 + 4, y - h)], col, ol=ol, w=2)
    c.line([(x - w / 4, y - h * 0.45), (x + w / 4, y - h * 0.45)], mix(col, (0, 0, 0), 0.3), 2, cap=False)


def kirk(c, x, y, s=1.0, col=(166, 154, 140), roof=SLATE, ol=OUT):
    """Greyfriars Kirk: a plain long Scottish church with gothic windows. origin = bottom centre."""
    c.push(x, y, s)
    c.rect(-260, -170, 260, 0, col, ol=ol, w=2.5)
    c.poly([(-270, -170), (270, -170), (230, -250), (-230, -250)], roof, ol=ol, w=2.5)
    for wx in range(-210, 220, 84):
        c.poly([(wx - 18, -40), (wx - 18, -120), (wx, -144), (wx + 18, -120), (wx + 18, -40)], (80, 90, 120), ol=ol,
               w=2)
        c.line([(wx, -142), (wx, -40)], col, 3, cap=False)
    # gable end with a big window
    c.poly([(-340, 0), (-340, -200), (-300, -260), (-260, -200), (-260, 0)], mix(col, (0, 0, 0), 0.08), ol=ol, w=2.5)
    c.poly([(-316, -60), (-316, -170), (-300, -196), (-284, -170), (-284, -60)], (80, 90, 120), ol=ol, w=2)
    c.pop()


def iron_railing(c, x0, x1, y, h=70, col=(40, 44, 50)):
    c.line([(x0, y - h + 10), (x1, y - h + 10)], col, 4, cap=False)
    c.line([(x0, y - 12), (x1, y - 12)], col, 4, cap=False)
    for x in range(int(x0), int(x1) + 1, 14):
        c.line([(x, y), (x, y - h)], col, 3, cap=False)
        c.poly([(x - 4, y - h), (x, y - h - 10), (x + 4, y - h)], col, ol=None)


def cannon(c, x, y, s=1.0, recoil=0.0, face=1, ol=OUT):
    """The One O'Clock Gun on its carriage. origin = between wheels, barrel points 'face'."""
    c.push(x - face * recoil * 30 * s, y, s, flip=face < 0)
    c.poly([(-90, -20), (40, -40), (50, -26), (-80, 0)], (110, 74, 48), ol=ol, w=2.5)
    # barrel
    c.poly([(-60, -56), (120, -66), (122, -44), (-60, -32)], (60, 66, 62), ol=ol, w=2.5)
    c.rect(116, -70, 132, -40, (60, 66, 62), ol=ol, w=2.5, r=3)
    c.ellipse(-62, -44, 14, 14, (60, 66, 62), ol=ol, w=2.5)
    c.line([(-40, -54), (100, -62)], (110, 118, 112), 3, cap=False)
    # wheel
    c.circle(0, -30, 32, (110, 74, 48), ol=ol, w=3)
    c.circle(0, -30, 24, None, ol=(80, 52, 34), w=3)
    for k in range(8):
        a = k * math.pi / 4
        c.line([(0, -30), (math.cos(a) * 24, -30 + math.sin(a) * 24)], (80, 52, 34), 3, cap=False)
    c.circle(0, -30, 6, (60, 60, 60), ol=ol, w=2)
    c.pop()


def time_ball_sign(c, x, y, text="ONE O'CLOCK GUN"):
    c.rect(x - 92, y - 26, x + 92, y, (30, 50, 40), ol=OUT, w=2, r=4)
    c.text(x, y - 13, text, 14, (240, 220, 160))


# ================================================================ Highlands

def loch_castle(c, x, y, s=1.0, col=(176, 160, 140), ol=OUT, night=0.0):
    """A castle on a little island in a loch, joined to the shore by an arched stone bridge.
    origin = waterline at the island centre."""
    c.push(x, y, s)
    st = mix(col, (60, 60, 100), night * 0.5)
    sh = mix(st, (0, 0, 0), 0.18)
    c.poly([(-150, 0), (-130, -24), (120, -26), (150, 0)], mix((100, 110, 90), (40, 50, 70), night * 0.5), ol=ol, w=2)
    # bridge to the right
    c.rect(130, -32, 330, -22, sh, ol=ol, w=2)
    for k in range(4):
        bx = 150 + k * 46
        c.rect(bx, -22, bx + 12, 0, sh, ol=ol, w=1.5)
    # walls
    c.rect(-120, -90, 110, -20, st, ol=ol, w=2.5)
    for bx in range(-118, 106, 14):
        c.rect(bx, -98, bx + 8, -90, st, ol=ol, w=1.5)
    # keep
    c.rect(-50, -170, 40, -60, st, ol=ol, w=2.5)
    for bx in range(-50, 40, 14):
        c.rect(bx, -180, bx + 8, -170, st, ol=ol, w=1.5)
    c.rect(-90, -130, -56, -60, sh, ol=ol, w=2)
    c.poly([(-94, -130), (-73, -156), (-52, -130)], SLATE, ol=ol, w=2)
    for wx, wy in ((-30, -140), (10, -140), (-10, -100)):
        c.rect(wx, wy, wx + 10, wy + 16, (50, 50, 70) if night < 0.5 else (255, 210, 120), ol=ol, w=1.5)
    saltire(c, 30, -180, 0.6, 0.0, pole=50)
    c.pop()


def urquhart(c, x, y, s=1.0, col=(150, 140, 130), ol=OUT, night=0.0):
    """The ruined tower of the castle on Loch Ness, on its grassy point. origin = waterline centre."""
    c.push(x, y, s)
    st = mix(col, (50, 50, 90), night * 0.55)
    sh = mix(st, (0, 0, 0), 0.2)
    c.poly([(-200, 0), (-170, -30), (-60, -46), (140, -40), (220, 0)], mix(GRASS, (30, 40, 70), night * 0.6), ol=ol,
           w=2.5)
    # broken walls
    c.poly([(-150, -34), (-150, -70), (-130, -74), (-120, -60), (-100, -66), (-80, -40)], sh, ol=ol, w=2)
    c.poly([(60, -42), (60, -76), (80, -70), (96, -84), (120, -64), (120, -40)], sh, ol=ol, w=2)
    # the tower with its broken top
    c.poly([(-40, -44), (-40, -190), (-26, -200), (-12, -186), (4, -208), (20, -196), (34, -204), (34, -44)], st,
           ol=ol, w=2.5)
    for wy in (-170, -130, -90):
        c.rect(-12, wy, 2, wy + 20, (40, 40, 60), ol=ol, w=1.5)
    c.line([(-40, -110), (34, -110)], sh, 2, cap=False)
    c.pop()


def nessie(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", rise=1.0, shy=0.0, look=(0.0, 0.0),
           humps=True, seed=9.1, tint=None, lower=0.0, blush=0.6, water=None):
    """Nessie: a gentle, shy plesiosaur. origin = waterline where her neck leaves the water, facing right.
    rise: 0..1 how far her neck is out of the water. shy: tucks the head down and away.
    lower: bends the neck down to the shore (for riders). ~300 tall at rise=1."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    body, dark, light = NESSIE, NESSIE_D, NESSIE_L
    if tint:
        body, dark, light = [mix(col, tint[0], tint[1]) for col in (body, dark, light)]
    c.push(x, y, s, flip=face < 0)
    sway = math.sin(t * 1.1 + seed) * 6
    # humps and tail behind
    if humps and rise > 0.2:
        hk = clamp((rise - 0.2) / 0.5)
        for k, (hx, hr) in enumerate(((-140, 56), (-270, 44))):
            hh = hr * 0.8 * hk
            c.poly([(hx + math.cos(a) * hr, -math.sin(a) * hh) for a in np.linspace(0, math.pi, 16)], body, w=2.5)
            for sx in (-0.4, 0, 0.4):
                c.circle(hx + sx * hr, -hh * 0.55, 5, dark, ol=None)
        c.stroke([(-330, -4), (-360, -16 * hk), (-374, -6 * hk)], body, 12)
        for hx, hr in ((-140, 56), (-270, 44)):
            c.line([(hx - hr - 10, 1), (hx + hr + 10, 1)], (170, 190, 230), 2)
    # neck: a gentle S, height scales with rise
    hgt = 290 * rise
    pts = []
    for i in range(10):
        u = i / 9
        px = 10 * math.sin(u * math.pi) + 44 * u ** 2 + sway * u - shy * 30 * u ** 2
        py = -hgt * u
        # lowering to the shore: the neck arcs forward and down
        px += lower * 210 * u ** 1.4
        py = lerp(py, -hgt * (0.55 * math.sin(u * math.pi * 0.9)), lower)
        pts.append((px, py))
    wid = [lerp(70, 34, (i / 9) ** 0.8) for i in range(10)]
    for i in range(9):
        c.line([pts[i], pts[i + 1]], OUT, wid[i] + 2 * D.LW)
    for i in range(9):
        c.line([pts[i], pts[i + 1]], body, wid[i])
    for i in range(1, 8):
        c.line([pts[i], pts[i + 1]], mix(body, light, 0.55), wid[i] * 0.3)
    for i in range(1, 8):
        px, py = pts[i]
        c.circle(px - wid[i] * 0.3, py, 4, dark, ol=None)
    hx, hy = pts[-1]
    tilt = shy * 0.5 + lower * 0.6
    hy += shy * 14
    # head
    c.push(hx, hy, 1.3)
    cr = rot([(4, -4)], tilt)[0]
    sn = rot([(34, 2)], tilt)[0]
    c.circle(cr[0], cr[1], 24, body, w=2.5)
    c.ellipse(sn[0], sn[1], 27, 15, body, w=2.5)
    c.circle(cr[0], cr[1], 22.5, body, ol=None)
    c.ellipse(sn[0] - 4, sn[1], 24, 13.5, body, ol=None)
    # little horns
    for bx in (-2, 14):
        a = rot([(bx, -24), (bx - 2, -40)], tilt)
        c.line(a, body, 6)
        c.circle(a[1][0], a[1][1], 5, light, w=2)
    # cheek blush + nostrils + mouth
    cp = rot([(28, 6)], tilt)[0]
    if blush > 0:
        c.ellipse(cp[0], cp[1], 9, 5, mix(body, (250, 140, 160), blush), ol=None)
    np_ = rot([(52, -8)], tilt)[0]
    c.circle(np_[0], np_[1], 2.2, OUT, ol=None)
    mp = rot([(36, 10), (48, 8)], tilt)
    if mouth > 0.05:
        mc = rot([(42, 11)], tilt)[0]
        c.ellipse(mc[0], mc[1], 7, 2 + 5 * mouth, (110, 40, 60), w=1.5)
    else:
        c.line(mp, OUT, 2)
    # big gentle eye with lashes
    ep = rot([(18, -10)], tilt)[0]
    lx, ly = look
    if eyes == "closed":
        c.arc(ep[0], ep[1], 7, 5, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ep[0], ep[1] + 3, 7, 6, 200, 340, OUT, 2.5)
    else:
        c.ellipse(ep[0], ep[1], 9, 10, (255, 255, 255), w=2)
        c.ellipse(ep[0] + 2 + lx * 2.5, ep[1] + 1 + ly * 3 + shy * 2, 5.5, 7, (40, 70, 60), ol=None)
        c.circle(ep[0] + 3 + lx * 2.5, ep[1] - 2 + ly * 3 + shy * 2, 2, (255, 255, 255), ol=None)
    for k in range(3):
        a = math.radians(-120 + k * 25)
        c.line([(ep[0] + math.cos(a) * 9, ep[1] + math.sin(a) * 10),
                (ep[0] + math.cos(a) * 15, ep[1] + math.sin(a) * 15)], OUT, 1.8)
    c.pop()
    c.pop()
    return (x + face * hx * s, y + hy * s)


def neck_points(rise=1.0, lower=0.0, t=0.0, seed=9.1, shy=0.0):
    """Points along Nessie's neck in local space (to place riders)."""
    sway = math.sin(t * 1.1 + seed) * 6
    hgt = 290 * rise
    out = []
    for i in range(10):
        u = i / 9
        px = 10 * math.sin(u * math.pi) + 44 * u ** 2 + sway * u - shy * 30 * u ** 2 + lower * 210 * u ** 1.4
        py = lerp(-hgt * u, -hgt * (0.55 * math.sin(u * math.pi * 0.9)), lower)
        out.append((px, py))
    return out


def bubbles(c, x, y, t, k, n=8, seed=0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        ph = (t * rng.uniform(0.8, 1.4) + rng.uniform(0, 1)) % 1.0
        if ph > k:
            continue
        bx = x + rng.uniform(-50, 50)
        c.circle(bx, y - 4 - ph * 6, 3 + 5 * ph, None, ol=(200, 230, 240), w=2)
