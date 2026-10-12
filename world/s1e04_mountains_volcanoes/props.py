"""Props for Episode 4: Tashi the snow leopard, Iggy the marine iguana, Whiskers' blanket, mountains,
the Himalaya and volcano-island backdrops, the volcano (smoke, lava, eruption) and the teaching
diagrams (land pushing together, Everest vs skyscrapers, Everest in the deepest ocean, colder
higher up, inside a volcano, a volcano making an island) plus the Remember / quiz icons."""
import math
from functools import lru_cache

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, LW, lerp, clamp, mix, ease
from world import kit as K

TAU = 2 * math.pi

# ================================================================== Tashi, snow leopard

LEO = dict(body=(226, 226, 214), shade=(196, 198, 190), belly=(250, 248, 240), spot=(88, 88, 98),
           eye=(150, 196, 150), ear=(236, 196, 196), nose=(214, 150, 150))


def _rosette(c, x, y, r):
    """A broken ring of dark spots (a leopard rosette)."""
    for i in range(4):
        a = i * TAU / 4 + 0.4
        c.ellipse(x + math.cos(a) * r, y + math.sin(a) * r, r * 0.42, r * 0.3, LEO["spot"], ol=None)


def snow_leopard(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), tail=0.0,
                 curl=0.0, seed=4.0):
    """Tashi sitting (side view, facing right for face=1). (x, y) = ground under her paws.
    About 190*s tall to the ear tips. tail: extra swish; curl 0..1 wraps the tail over her paws."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = LEO
    c.push(x, y, s, flip=face < 0)
    sw = math.sin(t * 1.4 + seed) * 0.5 + tail
    # the long, very thick tail: from the rump round the back and forward along the ground
    pts = []
    for i in range(14):
        u = i / 13
        if curl > 0:
            # wrap forward over the paws
            ang = math.pi * (1.0 - 1.1 * u)
            px = -44 + 70 * math.cos(ang) * (0.6 + 0.4 * u) + 70 * u * curl
            py = -20 + 10 * math.sin(ang * 0.5) * u - 8 * u
        else:
            px = -50 - 92 * math.sin(u * 1.9) + 16 * sw * u * u
            py = -26 + 20 * u - 64 * u * u + 34 * u ** 3 - 6 * sw * u
        pts.append((px, py))
    c.stroke(pts, p["body"], 30)
    for i in range(3, 13, 3):
        c.ellipse(pts[i][0], pts[i][1], 9, 7, p["spot"], ol=None)
    c.circle(pts[-1][0], pts[-1][1], 15, p["spot"], ol=OUT, w=2.5)
    # haunch and chest
    c.ellipse(-16, -40, 54, 40, p["body"])
    c.ellipse(14, -84, 42, 62, p["body"])
    c.ellipse(28, -72, 22, 40, p["belly"], ol=None)
    for (rx, ry, r) in ((-40, -50, 9), (-14, -60, 8), (-30, -26, 8), (0, -110, 7), (-6, -84, 7)):
        _rosette(c, rx, ry, r)
    # front legs
    for lx, col in ((10, p["shade"]), (36, p["body"])):
        c.rect(lx - 11, -60, lx + 11, -6, col, r=10)
        c.ellipse(lx + 4, -6, 15, 8, col)
    # head
    hx, hy = 36 + 2 * math.sin(t * 0.9 + seed), -150
    for ex in (-18, 22):                                        # small round ears
        c.circle(hx + ex, hy - 30, 14, p["body"])
        c.circle(hx + ex, hy - 29, 8, p["ear"], ol=None)
    c.ellipse(hx, hy, 44, 38, p["body"])
    for (sx, sy) in ((-22, -16), (-12, -26), (0, -30), (-28, -2), (12, -28)):
        c.ellipse(hx + sx, hy + sy, 4, 3.5, p["spot"], ol=None)
    c.ellipse(hx + 16, hy + 16, 24, 15, p["belly"], ol=None)     # muzzle
    for ex in (hx + 2, hx + 30):
        ey = hy - 6
        if eyes == "closed":
            c.arc(ex, ey - 1, 8, 6, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 8, 8, 200, 340, OUT, 3)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex, ey, 8 * big, 9.5 * big, (255, 255, 255), w=2.5)
            c.ellipse(ex + 1.5 + look[0] * 2.5, ey + look[1] * 2.5, 5.5 * big, 7 * big, p["eye"], ol=None)
            c.ellipse(ex + 1.5 + look[0] * 2.5, ey + look[1] * 2.5, 2.4, 5.5 * big, (25, 25, 30), ol=None)
            c.circle(ex + 3 + look[0] * 2.5, ey - 3 + look[1] * 2.5, 1.8, (255, 255, 255), ol=None)
    c.poly([(hx + 18, hy + 6), (hx + 28, hy + 6), (hx + 23, hy + 12)], p["nose"], w=1.5)
    if mouth > 0.05:
        hh = 2 + 10 * mouth
        c.ellipse(hx + 23, hy + 18 + hh * 0.5, 7 + 2 * mouth, hh, D.MOUTH, w=2)
        c.ellipse(hx + 23, hy + 18 + hh * 0.9, 4.5, 2 + 2 * mouth, D.TONGUE, ol=None)
    else:
        c.arc(hx + 18, hy + 15, 5, 3.5, 0, 180, OUT, 2)
        c.arc(hx + 28, hy + 15, 5, 3.5, 0, 180, OUT, 2)
    for dy in (-2, 4):
        c.line([(hx + 38, hy + 14), (hx + 62, hy + 10 + dy * 1.5)], OUT, 1.5, cap=False)
        c.line([(hx + 6, hy + 14), (hx - 16, hy + 10 + dy * 1.5)], OUT, 1.5, cap=False)
    c.pop()


# ===================================================================== Iggy, marine iguana

IGGY = dict(body=(84, 86, 94), dark=(56, 58, 66), red=(196, 96, 70), teal=(92, 160, 146), belly=(120, 122, 128))


def iguana(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), lift=0.0, seed=7.0):
    """Iggy lying on a rock (side view, facing right). (x, y) = ground under his belly.
    Head at about (+110, -70)*s; tail reaches back to about -200*s. lift 0..1 raises the head."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = IGGY
    c.push(x, y, s, flip=face < 0)
    sw = math.sin(t * 1.2 + seed)
    # tail
    top = [(-50, -40), (-110, -30), (-160, -16), (-196 + 6 * sw, -2), (-214 + 10 * sw, 14)]
    bot = [(-206 + 10 * sw, 18), (-160, 6), (-110, -8), (-50, -10)]
    c.poly(top + bot, p["body"])
    for i, (tx, ty) in enumerate(top[:-1]):
        c.poly([(tx - 8, ty + 1), (tx - 1, ty - 12 + i * 2), (tx + 6, ty + 1)], p["dark"], w=2)
    # far legs
    c.stroke([(-34, -16), (-56, 0)], p["dark"], 12)
    c.stroke([(52, -16), (66, 0)], p["dark"], 12)
    # body
    c.ellipse(4, -30, 70, 28, p["body"])
    c.ellipse(10, -14, 54, 10, p["belly"], ol=None)
    for (px, py, rx, ry, col) in ((-30, -36, 20, 10, p["red"]), (16, -40, 18, 9, p["teal"]),
                                  (44, -30, 12, 8, p["red"])):
        c.ellipse(px, py, rx, ry, col, ol=None)
    # back spikes
    for i in range(9):
        sx = -54 + i * 16
        sy = -30 - 26 * math.sin(math.pi * (i + 1) / 11)
        c.poly([(sx - 7, sy + 4), (sx, sy - 16), (sx + 7, sy + 4)], (236, 236, 226), w=2)
    # near legs with claws
    for (lx, fx) in ((-20, -40), (66, 82)):
        c.stroke([(lx, -18), (fx, -2)], p["body"], 14)
        for k in range(3):
            c.line([(fx + 4, -2), (fx + 12 + 4 * k, 2 + k)], OUT, 2.5)
    # neck + head (lifts a little when talking)
    hx, hy = 112, -64 - 10 * lift + 2 * math.sin(t * 0.8 + seed)
    c.poly([(48, -50), (hx - 26, hy - 12), (hx - 20, hy + 20), (56, -12)], p["body"], w=2.5)
    for i in range(3):
        sx = 64 + i * 12
        sy = lerp(-54, hy - 14, i / 3)
        c.poly([(sx - 6, sy + 4), (sx, sy - 13), (sx + 6, sy + 4)], (236, 236, 226), w=2)
    c.ellipse(hx, hy, 36, 25, p["body"])
    # white salty crust on his head (marine iguanas sneeze out salt!)
    for (bx, by, r) in ((-14, -20, 6), (-2, -24, 7), (10, -22, 6), (20, -16, 5), (-24, -12, 5)):
        c.circle(hx + bx, hy + by, r, (238, 238, 232), w=2)
    # mouth (lower jaw drops)
    jaw = 10 * clamp(mouth)
    if jaw > 1:
        c.poly([(hx + 34, hy + 6), (hx - 4, hy + 10), (hx + 30, hy + 10 + jaw)], (150, 60, 70), w=2)
    c.line([(hx + 34, hy + 6), (hx + 6, hy + 10), (hx - 8, hy + 6)], OUT, 2.5)
    c.circle(hx + 26, hy - 6, 2, OUT, ol=None)                  # nostril
    ex, ey = hx - 2, hy - 6
    if eyes == "closed":
        c.arc(ex, ey, 9, 7, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 4, 9, 8, 200, 340, OUT, 3)
    else:
        big = 1.2 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 10 * big, 10 * big, (255, 250, 230), w=2.5)
        c.ellipse(ex + 2 + look[0] * 3, ey + look[1] * 3, 5, 6.5, (40, 30, 30), ol=None)
        c.circle(ex + 3.5 + look[0] * 3, ey - 2.5, 1.8, (255, 255, 255), ol=None)
    c.pop()


# ================================================================== Whiskers' blanket

BLANKET = (120, 170, 220)
BLANKET_D = (84, 126, 184)
BLANKET_S = (250, 214, 110)


def blanket_profile(xl, xr, length, n=60, top_y=0.0):
    """Top curve of a blanket of fixed length squashed between xl and xr (two humps, bigger right)."""
    span = max(1.0, xr - xl)
    amp = 0.5 * math.sqrt(max(0.0, length ** 2 - span ** 2))
    pts = []
    for i in range(n + 1):
        u = i / n
        h = 0.62 * math.exp(-((u - 0.3) / 0.16) ** 2) + 1.0 * math.exp(-((u - 0.66) / 0.17) ** 2)
        h *= math.sin(math.pi * u) ** 0.4
        pts.append((lerp(xl, xr, u), top_y - amp * h))
    return pts, amp


def blanket(c, xl, xr, y, length, thick=16, snow=0.0):
    """Whiskers' striped blanket lying on the sill between xl and xr; squashed, it folds into
    mountains. snow 0..1 adds a little paper snow cap (just for fun)."""
    pts, amp = blanket_profile(xl, xr, length, top_y=y - thick)
    c.poly(pts + [(xr, y), (xl, y)], BLANKET)
    # folded stripes follow the hump shape (like rock layers)
    for off, col, w in ((8, BLANKET_S, 4), (22, BLANKET_D, 5), (36, BLANKET_S, 4), (50, BLANKET_D, 5)):
        lay = [(px, min(y - 3, py + off)) for px, py in pts[1:-1]]
        if any(py < y - 4 for _, py in lay):
            c.line(lay, col, w, cap=False)
    c.poly(pts + [(xr, y), (xl, y)], None, ol=OUT, w=3)
    # little tassels at both ends
    for ex, side in ((xl, -1), (xr, 1)):
        for k in range(3):
            c.line([(ex, y - 4 - k * 5), (ex + side * 10, y - 2 - k * 5)], BLANKET_S, 3)
    return pts, amp


# =================================================================== mountains / scenery

ROCK = (128, 120, 134)
ROCK_D = (98, 92, 108)
SNOW = (250, 252, 255)
SNOW_S = (206, 222, 242)


def peak(c, x, base, w, h, col=ROCK, snow=0.42, seed=0, shade=True, snow_col=SNOW, ol=OUT, lw=3):
    """A cartoon mountain with a jagged snow cap. (x, base) = bottom centre; w = half width."""
    rng = np.random.default_rng(seed)
    lx = x + rng.uniform(-0.08, 0.08) * w
    top = (lx, base - h)
    left = [(x - w, base)]
    right = [(x + w, base)]
    for f in (0.35, 0.7):
        left.append((lerp(x - w, lx, f) + rng.uniform(-8, 8), lerp(base, base - h, f) + rng.uniform(-10, 4)))
        right.insert(0, (lerp(x + w, lx, f) + rng.uniform(-8, 8), lerp(base, base - h, f) + rng.uniform(-10, 4)))
    pts = left + [top] + right
    c.poly(pts, col, ol=ol, w=lw)
    if shade:
        c.poly([top] + right + [(lx + w * 0.1, base)], mix(col, (40, 40, 70), 0.18), ol=None)
    if snow > 0:
        def at(px0, py0, px1, py1, f):
            return lerp(px0, px1, f), lerp(py0, py1, f)
        sl = at(top[0], top[1], x - w, base, snow)
        sr = at(top[0], top[1], x + w, base, snow)
        cap = [sl]
        for i in range(1, 6):
            f = i / 6
            cap.append((lerp(sl[0], sr[0], f), lerp(sl[1], sr[1], f) + (14 if i % 2 else -2) * (h / 300)))
        cap += [sr, top]
        c.poly(cap, snow_col, ol=None)
        if shade:
            c.poly([top, sr] + [(lerp(sl[0], sr[0], f), lerp(sl[1], sr[1], f) + (14 if int(f * 6) % 2 else -2)
                                 * (h / 300)) for f in (0.66, 0.5)], SNOW_S, ol=None)
        c.poly(pts, None, ol=ol, w=lw)
    return top


def tashi_rock(c):
    """Tashi's snowy rock on the right (also redrawn in front of her while she climbs up)."""
    c.poly([(560, H + 10), (600, 640), (700, 612), (860, 576), (1020, 560), (1180, 586), (1300, 610),
            (1300, H + 10)], (140, 132, 146))
    c.poly([(720, 612), (860, 572), (1020, 556), (1180, 582), (1290, 604), (1180, 596), (1020, 576),
            (860, 590)], SNOW, ol=None)


_EV = []


def everest_top():
    """Screen position of Everest's summit on himalaya_bg()."""
    himalaya_bg()
    return _EV[0]


@lru_cache(None)
def himalaya_bg():
    """The Himalayas: deep blue sky, far snowy range, Mount Everest in the middle with its snow
    plume, a rocky ledge in front (cushion lands left, Tashi sits on the rock at the right)."""
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (60, 110, 196)), (0.55, (150, 196, 240)), (1, (214, 232, 250))]))
    c.glow(240, 90, 70, 70, (255, 250, 220), (120, 160, 225), steps=6)
    c.circle(240, 90, 34, (255, 244, 190), ol=None)
    # far range (pale, no outline)
    far = (172, 186, 214)
    for i, (x, w, h) in enumerate(((60, 220, 330), (330, 240, 370), (1040, 240, 360), (1240, 220, 320))):
        peak(c, x, 560, w, h, far, 0.5, seed=10 + i, shade=False, snow_col=(236, 242, 252), ol=None)
    # Mount Everest: biggest, centre right; snow plume blowing off the top
    ev = peak(c, 720, 610, 380, 540, (140, 132, 150), 0.42, seed=3)
    _EV[:] = [ev]
    for k in range(6):
        c.ellipse(ev[0] + 50 + 34 * k, ev[1] + 6 + 4 * k, 34 - 3 * k, 12 - k, (246, 250, 255), ol=None)
    # mid range either side
    for i, (x, w, h) in enumerate(((190, 260, 300), (1140, 280, 320))):
        peak(c, x, 620, w, h, (122, 116, 136), 0.4, seed=20 + i)
    # foreground: snowy rocky ledge (left) and a rock for Tashi (right)
    c.poly([(-20, 600), (140, 566), (360, 572), (560, 590), (640, 640), (660, H + 10), (-20, H + 10)],
           (150, 140, 150))
    c.poly([(-20, 596), (140, 562), (360, 568), (560, 586), (610, 606), (420, 600), (200, 590), (-20, 612)],
           SNOW, ol=None)
    tashi_rock(c)
    # prayer flags between two poles
    for px, py in ((470, 590), (880, 576)):
        c.line([(px, py), (px, py - 150)], (110, 80, 60), 5)
    flag_cols = [(70, 120, 220), (250, 250, 250), (220, 70, 60), (90, 170, 90), (250, 210, 70)]
    pts = [(lerp(470, 880, u), lerp(440, 426, u) + 40 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 30)]
    c.line(pts, (90, 70, 60), 2)
    for i in range(1, 14):
        u = i / 14
        fx, fy = lerp(470, 880, u), lerp(440, 426, u) + 40 * math.sin(math.pi * u)
        c.poly([(fx - 9, fy), (fx + 9, fy), (fx + 8, fy + 20), (fx - 8, fy + 20)], flag_cols[i % 5], w=1.5)
    return c.img


@lru_cache(None)
def island_bg():
    """A Galapagos island: sky, sea, a big volcano across the bay (no lava; that is animated),
    and black lava rocks in front with Iggy's rock."""
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 190, 246)), (0.5, (214, 238, 255)),
                                           (0.5001, (70, 160, 210)), (1, (40, 110, 180))]))
    D.cloud(c, 160, 90, 0.8)
    D.cloud(c, 470, 60, 0.55)
    # little far islands
    for (x, w, h) in ((120, 90, 34), (300, 60, 22)):
        c.poly([(x - w, 360), (x - w * 0.3, 360 - h), (x + w * 0.2, 360 - h * 0.9), (x + w, 360)],
               (110, 120, 110), ol=None)
    # the volcano cone across the bay
    c.poly([(560, 368), (800, 190), (890, 132), (990, 128), (1070, 186), (1300, 330), (1300, 368)],
           (110, 100, 98))
    c.poly([(890, 132), (990, 128), (1070, 186), (1300, 330), (1300, 368), (1000, 368), (960, 220)],
           (90, 82, 82), ol=None)
    c.poly([(560, 368), (800, 190), (890, 132), (990, 128), (1070, 186), (1300, 330), (1300, 368)],
           None, ol=OUT, w=3)
    # green lower slopes
    c.poly([(560, 368), (660, 300), (760, 320), (900, 300), (1060, 316), (1200, 300), (1300, 330),
            (1300, 368)], (120, 160, 96), ol=OUT, w=3)
    # crater rim
    c.ellipse(940, 132, 52, 10, (70, 60, 62), ol=OUT, w=3)
    c.line([(0, 360), (W, 360)], (236, 248, 255), 3, cap=False)
    # black lava rocks in front
    c.poly([(-20, 610), (120, 580), (260, 600), (420, 586), (560, 616), (700, 600), (860, 560), (1000, 548),
            (1140, 566), (1300, 552), (1300, H + 10), (-20, H + 10)], (52, 50, 56))
    rng = np.random.default_rng(3)
    for _ in range(30):
        x, y = rng.uniform(0, W), rng.uniform(620, 712)
        c.ellipse(x, y, rng.uniform(10, 30), rng.uniform(4, 9), (70, 68, 76), ol=None)
    # Iggy's sunny rock
    c.poly([(860, 600), (900, 540), (1000, 520), (1120, 530), (1180, 580), (1160, 620), (880, 624)],
           (66, 64, 72))
    c.line([(912, 548), (1000, 530), (1110, 538)], (100, 98, 108), 3)
    return c.img


# Volcano geometry on island_bg (screen coords)
CRATER = (940, 128)
LAVA_LEFT = [(902, 134), (870, 170), (840, 210), (810, 250), (780, 290), (744, 330), (712, 362)]
LAVA_RIGHT = [(984, 134), (1010, 176), (1036, 214), (1070, 250), (1110, 290), (1150, 330)]


def smoke(c, x, y, t, k=1.0, n=7, big=1.0, col=(214, 212, 220), seed=2):
    """Rising puffs of smoke/steam from (x, y)."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        u = (t * 0.22 + i / n) % 1
        dx = rng.uniform(-20, 20) + 70 * u * big + 10 * math.sin(t + i)
        r = (16 + 46 * u) * big * k
        c.circle(x + dx, y - 200 * u * big, r, mix(col, (255, 255, 255), 0.2 * (1 - u)), ol=None)


def lava_stream(c, pts, u, t, w=14):
    """Glowing lava running down along pts (0..u of the way)."""
    if u <= 0.01:
        return
    sp = K.spline(pts, 8)
    n = max(2, int(len(sp) * clamp(u)))
    seg = sp[:n]
    c.line(seg, (150, 30, 20), w + 6)
    c.line(seg, (250, 110, 30), w)
    c.line(seg, (255, 220, 90), max(2, w * 0.35))
    hx, hy = seg[-1]
    c.circle(hx, hy, w * 0.75 + 2 * math.sin(t * 9), (255, 160, 50), ol=(150, 30, 20), w=2)


def lava_fountain(c, x, y, t, k=1.0, n=26, h=170, seed=5):
    """Blobs of lava thrown up out of the crater, falling back down (k = strength)."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        ph = rng.uniform(0, 1)
        u = (t * 0.9 + ph) % 1
        vx = rng.uniform(-1, 1) * 150
        hh = h * rng.uniform(0.5, 1.1) * k
        px = x + vx * u
        py = y - 4 * hh * u * (1 - u)
        r = rng.uniform(5, 12) * k * (1 - 0.4 * u)
        col = mix((255, 236, 120), (230, 70, 30), u)
        c.circle(px, py, r, col, ol=(120, 30, 20), w=1.5)


def crater_glow(c, k, t):
    if k <= 0.01:
        return
    c.glow(CRATER[0], CRATER[1], 120 * k, 60 * k, (255, 170, 80), (176, 140, 150), steps=8)
    c.ellipse(CRATER[0], CRATER[1], 48, 9, mix((70, 60, 62), (255, 150, 40), k), ol=OUT, w=3)


# ======================================================================== little props

def fish(c, x, y, s=1.0, burnt=0.0, face=1, ang=0.0):
    """A fish held by its tail (head down when ang=90). burnt 0..1 turns it into charcoal."""
    col = mix((150, 196, 230), (40, 34, 36), burnt)
    c.push(x, y, s, flip=face < 0)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def R(px, py):
        return px * ca - py * sa, px * sa + py * ca
    body = [R(30 * math.cos(a), 13 * math.sin(a)) for a in np.linspace(0, TAU, 24)]
    c.poly([R(-26, 0), R(-46, -14), R(-42, 0), R(-46, 14)], mix(col, (0, 0, 0), 0.15), w=2.5)
    c.poly(body, col, w=2.5)
    ex, ey = R(16, -3)
    if burnt > 0.5:
        c.line([(ex - 4, ey - 4), (ex + 4, ey + 4)], (255, 255, 255), 2)
        c.line([(ex - 4, ey + 4), (ex + 4, ey - 4)], (255, 255, 255), 2)
    else:
        c.circle(ex, ey, 3.5, (255, 255, 255), w=1.5)
        c.circle(ex + 1, ey, 1.6, OUT, ol=None)
    c.pop()


def mug(c, x, y, r, t=0.0, steam=1.0):
    """A mug of hot chocolate (centre x, y; r = size)."""
    c.rect(x - r * 0.6, y - r * 0.55, x + r * 0.5, y + r * 0.6, (232, 90, 90), r=r * 0.15, w=3)
    c.arc(x + r * 0.55, y, r * 0.28, r * 0.28, 270, 90, OUT, 7)
    c.arc(x + r * 0.55, y, r * 0.28, r * 0.28, 270, 90, (232, 90, 90), 4)
    c.ellipse(x - r * 0.05, y - r * 0.55, r * 0.55, r * 0.12, (130, 76, 50), w=2.5)
    c.ellipse(x - r * 0.05, y + r * 0.05, r * 0.24, r * 0.2, (255, 255, 255), ol=None)
    for k in range(3):
        if steam > 0:
            pts = [(x - r * 0.3 + k * r * 0.25 + r * 0.08 * math.sin(v * 6 + t * 3 + k), y - r * 0.7 - v * r * 0.6)
                   for v in np.linspace(0, 1, 8)]
            c.line(pts, (255, 255, 255), 3)


def thermometer(c, x, y, h, level, t=0.0):
    """Thermometer: bulb at (x, y), tube up to y - h; level 0..1 (red when warm, blue when cold)."""
    col = mix((90, 150, 240), (230, 70, 60), level)
    c.rect(x - 9, y - h, x + 9, y, (255, 255, 255), r=9, w=3)
    c.rect(x - 4, y - 8 - (h - 16) * clamp(level), x + 4, y, col, ol=None, r=4)
    c.circle(x, y + 6, 15, col, w=3)


# ============================================================================ insets

def _wh(ic):
    return ic.img.size[0] / SS, ic.img.size[1] / SS


def _sky(ic, top=(150, 205, 250), bot=(226, 242, 255)):
    w, h = _wh(ic)
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, top), (1, bot)]), (0, 0))


def crust_inset(ic, t, k):
    """Two giant pieces of land push together (k 0..0.5), then the land between them folds up into
    a mountain (k 0.5..1). Rock layers bend to show the folding."""
    w, h = _wh(ic)
    _sky(ic)
    cx, ground = w / 2, h - 78
    kp = ease(clamp(k / 0.5))
    kf = ease(clamp((k - 0.5) / 0.5))
    gap = 44 * (1 - kp)
    hmax = 92 * kf

    def top(x):
        d = (x - cx) / 90
        return ground - hmax * math.exp(-d * d) * (1 + 0.25 * math.cos(d * 3))
    layers = [((132, 196, 96), 0), ((196, 150, 100), 14), ((168, 120, 84), 34), ((140, 96, 70), 56)]
    for side in (-1, 1):
        x0 = 0 if side < 0 else cx + gap
        x1 = cx - gap if side < 0 else w
        xs = np.linspace(x0, x1, 40)
        prof = [(float(x), top(x)) for x in xs]
        ic.poly(prof + [(x1, h), (x0, h)], layers[1][0], ol=OUT, w=3)
        for col, off in layers[2:]:
            lay = [(x, y + off + 20 * (1 - kf) * 0) for x, y in prof]
            ic.poly(lay + [(x1, h), (x0, h)], col, ol=None)
            ic.line(lay, mix(col, (0, 0, 0), 0.25), 2, cap=False)
        ic.line(prof, layers[0][0], 7, cap=False)
        if hmax > 40:
            snowline = ground - hmax * 0.68
            cap = [(x, y) for x, y in prof if y < snowline]
            if len(cap) > 2:
                ic.poly(cap, SNOW, ol=None)
        ic.poly(prof + [(x1, h), (x0, h)], None, ol=OUT, w=3)
    # push arrows
    ak = clamp(k * 3) * (1 - clamp((k - 0.85) / 0.15) * 0.0)
    off = 10 * math.sin(t * 6)
    K.arrow(ic, 26 + off, ground + 50, 120 + off, ground + 50, (255, 236, 90), 9, ak, head=20)
    K.arrow(ic, w - 26 - off, ground + 50, w - 120 - off, ground + 50, (255, 236, 90), 9, ak, head=20)
    K.text(ic, 74, ground + 22, "push", 22, (255, 255, 255), stroke=3)
    K.text(ic, w - 74, ground + 22, "push", 22, (255, 255, 255), stroke=3)
    if k > 0.7:
        K.text(ic, cx, 30, "A mountain grows!", 30, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))
    else:
        K.text(ic, cx, 30, "Land pushes together...", 28, (48, 40, 60))


SKY_COLS = [(120, 150, 200), (200, 120, 110), (110, 170, 150), (210, 170, 90), (150, 130, 190)]


def skyscraper_inset(ic, t, k):
    """Everest next to a stack of 20 big skyscrapers (they pop on one by one)."""
    w, h = _wh(ic)
    _sky(ic, (120, 180, 246), (220, 240, 255))
    base = h - 46
    top_ = 60
    ic.rect(0, base, w, h, (120, 180, 96), ol=OUT, w=3)
    peak(ic, w * 0.66, base, 120, base - top_, (140, 132, 150), 0.4, seed=3)
    n = int(clamp(k) * 20 + 1e-6)
    bh = (base - top_) / 20
    for i in range(n):
        y1 = base - i * bh
        col = SKY_COLS[i % 5]
        bw = 22
        ic.rect(w * 0.24 - bw, y1 - bh, w * 0.24 + bw, y1, col, ol=OUT, w=1.5)
        for wx in (-12, -2, 8):
            ic.rect(w * 0.24 + wx, y1 - bh + 3, w * 0.24 + wx + 5, y1 - 3, (255, 248, 200), ol=None)
    if n:
        K.text(ic, w * 0.24 - 66, base - n * bh + bh / 2, str(n), 26, (226, 70, 80), stroke=3,
               stroke_fill=(255, 255, 255))
    K.text(ic, w * 0.66, base + 22, "Mount Everest", 22, (255, 255, 255), stroke=3)
    K.text(ic, w * 0.24, base + 22, "skyscrapers", 22, (255, 255, 255), stroke=3)
    if k >= 1:
        K.text(ic, w / 2, 26, "Almost 9 km high!", 30, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))


def trench_inset(ic, t, k):
    """Everest sinks into the deepest part of the ocean -- and its top is still under water."""
    w, h = _wh(ic)
    _sky(ic, (150, 205, 250), (200, 230, 255))
    sea_y = 50
    bottom = h - 28
    ic.img.paste(D.gradient(int(w * SS), int((h - sea_y) * SS), [(0, (70, 150, 220)), (1, (16, 30, 90))]),
                 (0, int(sea_y * SS)))
    # sea floor with a deep, narrow trench in the middle
    floor = 150
    tx = w / 2
    ic.poly([(0, floor), (tx - 120, floor + 10), (tx - 70, bottom), (tx + 70, bottom), (tx + 120, floor + 10),
             (w, floor), (w, h), (0, h)], (96, 84, 80), ol=OUT, w=3)
    # Everest (8.85 km) vs the deepest place (about 11 km): scaled
    depth = bottom - sea_y
    eh = depth * 8.85 / 10.9
    y_base = lerp(-20, bottom, ease(k))
    if k > 0:
        peak(ic, tx, y_base, 64, eh, (150, 140, 156), 0.4, seed=3)
    ic.line([(0, sea_y), (w, sea_y)], (236, 248, 255), 3, cap=False)
    for i in range(6):
        x = (i * 80 + t * 20) % (w + 40) - 20
        ic.arc(x, sea_y, 14, 6, 200, 340, (236, 248, 255), 2)
    if k >= 1:
        top_y = y_base - eh
        K.arrow(ic, tx + 100, top_y - 2, tx + 100, sea_y + 4, (255, 236, 90), 5, 1.0, head=12)
        K.arrow(ic, tx + 100, sea_y + 4, tx + 100, top_y - 2, (255, 236, 90), 5, 1.0, head=12)
        K.text(ic, w / 2, 24, "Still under water!", 30, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))
    else:
        K.text(ic, w / 2, 24, "The deepest ocean", 28, (48, 40, 60))


def cold_inset(ic, t, k):
    """The higher you go, the colder it gets: a mountain with a climbing dot and a thermometer."""
    w, h = _wh(ic)
    _sky(ic)
    base = h - 20
    mx = w * 0.42
    peak(ic, mx, base, 170, base - 34, (140, 132, 150), 0.36, seed=5)
    # green, warm foot of the mountain with little trees and flowers
    ic.poly([(mx - 170, base), (mx - 120, base - 40), (mx, base - 52), (mx + 120, base - 40), (mx + 170, base)],
            (110, 176, 90), ol=OUT, w=2.5)
    for tx in (-120, -80, 80, 120):
        ic.poly([(mx + tx - 9, base - 20), (mx + tx, base - 46), (mx + tx + 9, base - 20)], (60, 130, 70), w=2)
    for fx in (-40, 0, 40):
        ic.circle(mx + fx, base - 30, 4, (250, 120, 160), w=1.5)
    # climber (a little red-scarf dot: Pip!) going up
    u = ease(clamp(k))
    px = lerp(mx - 110, mx - 6, u)
    py = lerp(base - 44, 50, u)
    ic.circle(px, py, 8, (176, 156, 142), w=2)
    ic.rect(px - 7, py + 5, px + 7, py + 9, (220, 50, 50), ol=None)
    level = 1 - u
    thermometer(ic, w - 70, base - 30, h - 110, level, t)
    K.text(ic, w - 130, 70, "cold!", 26, (70, 120, 220), stroke=2, stroke_fill=(255, 255, 255))
    K.text(ic, w - 130, base - 40, "warm", 26, (220, 80, 60), stroke=2, stroke_fill=(255, 255, 255))
    if u > 0.6:
        for i in range(5):
            sx = mx - 60 + i * 30 + 6 * math.sin(t * 2 + i)
            sy = (40 + t * 30 + i * 37) % 120 + 20
            ic.circle(sx, sy, 3, (255, 255, 255), ol=None)


def cutaway_inset(ic, t, k_magma, k_lava):
    """Inside a volcano: magma deep underground, lava when it comes out of the top."""
    w, h = _wh(ic)
    _sky(ic, (140, 200, 246), (220, 240, 255))
    gy = h * 0.52
    cx = w / 2
    # underground
    ic.rect(0, gy, w, h, (150, 110, 80), ol=None)
    for y in (gy + 30, gy + 70):
        ic.line([(0, y), (w, y + 6)], (130, 92, 66), 3, cap=False)
    # the cone, cut in half
    ic.poly([(cx - 190, gy), (cx - 36, 52), (cx + 36, 52), (cx + 190, gy)], (120, 108, 104), ol=OUT, w=3)
    # magma: chamber + pipe
    glow = 0.5 + 0.5 * math.sin(t * 4)
    mcol = mix((240, 90, 30), (255, 170, 60), glow * 0.5)
    ic.glow(cx, h - 44, 120 * k_magma + 1, 50 * k_magma + 1, (255, 190, 90), (150, 110, 80), steps=6)
    if k_magma > 0.01:
        ic.ellipse(cx, h - 44, 100 * k_magma, 34 * k_magma, mcol, ol=(130, 30, 20), w=3)
        pipe_top = lerp(h - 60, 56, clamp(k_magma * 1.4 - 0.2))
        ic.rect(cx - 12, pipe_top, cx + 12, h - 60, mcol, ol=None)
        for i in range(4):
            u = (t * 0.6 + i / 4) % 1
            ic.circle(cx + 30 * math.sin(i * 2.1), h - 44 - 10 * u, 5 * (1 - u) + 1, (255, 230, 120), ol=None)
        K.label(ic, cx + 128, h - 92, "magma", 24, tip=(cx + 70, h - 58), k=clamp(k_magma * 2 - 0.6),
                col=(200, 60, 30))
    if k_lava > 0.01:
        lava_fountain(ic, cx, 54, t, k_lava * 0.6, n=12, h=60, seed=8)
        for side, kk in ((-1, k_lava), (1, k_lava * 0.9)):
            fl = [(cx + side * lerp(30, 180, f), lerp(54, gy - 4, f) - 4) for f in (0.0, 0.3, 0.6, 0.95)]
            lava_stream(ic, fl, kk, t, w=10)
        K.label(ic, cx + 150, 40, "lava", 24, tip=(cx + 70, 72), k=clamp(k_lava * 2 - 0.4), col=(200, 60, 30))
    K.text(ic, 90, gy + 18, "ground", 20, (255, 236, 210), stroke=2)


def island_inset(ic, t, k):
    """A volcano under the sea grows, layer of lava by layer, until it pops out as a new island."""
    w, h = _wh(ic)
    _sky(ic, (150, 205, 250), (220, 240, 255))
    sea_y = 112
    ic.img.paste(D.gradient(int(w * SS), int((h - sea_y) * SS), [(0, (80, 170, 230)), (1, (30, 70, 150))]),
                 (0, int(sea_y * SS)))
    floor = h - 26
    ic.rect(0, floor, w, h, (120, 100, 90), ol=OUT, w=3)
    cx = w / 2
    hh = lerp(24, floor - sea_y + 26, ease(clamp(k)))
    tw = 50 + hh * 0.55
    ic.poly([(cx - tw, floor), (cx - 26, floor - hh), (cx + 26, floor - hh), (cx + tw, floor)], (78, 72, 76),
            ol=OUT, w=3)
    top = floor - hh
    if k < 0.98:
        ic.glow(cx, top, 30, 12, (255, 190, 80), (78, 72, 76), steps=5)
        for i in range(5):
            u = (t * 0.7 + i / 5) % 1
            by = top - u * (top - sea_y)
            if by > sea_y + 4:
                ic.circle(cx + 10 * math.sin(i * 2 + t * 3), by, 3 + 3 * u, (220, 240, 255), w=1.5)
    if top < sea_y:
        # green top and a palm tree: a brand new island
        ic.poly([(cx - 26 - (sea_y - top) * 0.55, sea_y), (cx - 26, top), (cx + 26, top),
                 (cx + 26 + (sea_y - top) * 0.55, sea_y)], (120, 170, 90), ol=OUT, w=3)
        ic.line([(cx + 10, top + 2), (cx + 18, top - 40)], (130, 96, 60), 5)
        for a in (-150, -110, -60, -20):
            ar = math.radians(a)
            ic.line([(cx + 18, top - 40), (cx + 18 + math.cos(ar) * 26, top - 40 + math.sin(ar) * 10 + 12)],
                    (70, 150, 70), 6)
        smoke(ic, cx - 6, top - 6, t, 0.5, n=4, big=0.35)
    ic.line([(0, sea_y), (w, sea_y)], (236, 248, 255), 3, cap=False)
    if top < sea_y:
        K.text(ic, w / 2, 30, "A new island!", 32, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))
    else:
        K.text(ic, w / 2, 30, "A volcano under the sea...", 26, (48, 40, 60))


# ============================================================================== icons

def icon_push(c, x, y, r, t=0.0):
    """Remember fact 1: two arrows pushing land into a mountain."""
    peak(c, x, y + r * 0.6, r * 0.6, r * 1.05, (140, 132, 150), 0.4, seed=1)
    c.rect(x - r, y + r * 0.6 - 2, x + r, y + r * 0.6 + 6, (120, 176, 90), ol=None)
    K.arrow(c, x - r * 1.0, y + r * 0.35, x - r * 0.45, y + r * 0.35, (226, 70, 80), 6, 1.0, head=12)
    K.arrow(c, x + r * 1.0, y + r * 0.35, x + r * 0.45, y + r * 0.35, (226, 70, 80), 6, 1.0, head=12)


def icon_everest(c, x, y, r, t=0.0):
    """Remember fact 2 / quiz: the tallest mountain with a little flag on top."""
    tp = peak(c, x, y + r * 0.7, r * 0.85, r * 1.45, (140, 132, 150), 0.45, seed=3)
    c.line([(tp[0], tp[1]), (tp[0], tp[1] - r * 0.4)], OUT, 3)
    c.poly([(tp[0], tp[1] - r * 0.4), (tp[0] + r * 0.3, tp[1] - r * 0.32), (tp[0], tp[1] - r * 0.22)],
           (226, 70, 80), w=2)


def icon_volcano(c, x, y, r, t=0.0):
    """Remember fact 3 / quiz: a volcano with glowing lava."""
    smoke(c, x, y - r * 0.55, t, 0.5, n=4, big=0.3)
    c.poly([(x - r * 0.95, y + r * 0.7), (x - r * 0.25, y - r * 0.5), (x + r * 0.25, y - r * 0.5),
            (x + r * 0.95, y + r * 0.7)], (110, 100, 98), w=3)
    c.ellipse(x, y - r * 0.5, r * 0.25, r * 0.07, (255, 150, 40), ol=OUT, w=2)
    lava_stream(c, [(x - r * 0.2, y - r * 0.5), (x - r * 0.42, y - r * 0.12), (x - r * 0.64, y + r * 0.26)],
                1.0, t, w=r * 0.14)
    lava_fountain(c, x, y - r * 0.5, t, 0.35, n=6, h=r * 0.5, seed=2)


def icon_blanket(c, x, y, r, t=0.0):
    """Quiz: 'Nap Mountain', Whiskers' folded blanket."""
    blanket(c, x - r * 0.95, x + r * 0.95, y + r * 0.55, r * 3.2, thick=10)


def icon_mug(c, x, y, r, t=0.0):
    mug(c, x, y + r * 0.15, r * 0.9, t)


def icon_magma(c, x, y, r, t=0.0):
    """Quiz: hot melted rock (a volcano cut open, glowing inside)."""
    c.poly([(x - r * 0.95, y + r * 0.7), (x - r * 0.2, y - r * 0.6), (x + r * 0.2, y - r * 0.6),
            (x + r * 0.95, y + r * 0.7)], (120, 108, 104), w=3)
    c.ellipse(x, y + r * 0.45, r * 0.5, r * 0.2, (250, 120, 40), ol=(130, 30, 20), w=2)
    c.rect(x - r * 0.08, y - r * 0.55, x + r * 0.08, y + r * 0.35, (250, 120, 40), ol=None)
    lava_fountain(c, x, y - r * 0.6, t, 0.35, n=6, h=r * 0.5, seed=2)
