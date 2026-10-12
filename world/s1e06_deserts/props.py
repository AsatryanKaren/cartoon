"""Props for Episode 6 "Deserts": Humphrey the camel, Fizz the fennec fox, dunes, palm trees,
the desert backdrops and the little teaching diagrams and icons."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease
from world import kit as K

SAND = (240, 206, 132)
SAND_L = (252, 228, 168)
SAND_D = (214, 168, 98)
SAND_DD = (190, 140, 80)
FAT = (255, 226, 120)
FAT_D = (236, 190, 80)
WATER = (90, 170, 235)

# ============================================================================== Humphrey

CAMEL = (214, 164, 104)
CAMEL_D = (182, 130, 78)
CAMEL_L = (238, 206, 154)


def _eye(c, ex, ey, eyes, look=(0.0, 0.0), r=10, lid=True):
    if eyes == "closed":
        c.arc(ex, ey, r, r * 0.7, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 3, r, r * 0.9, 200, 340, OUT, 3)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, r * big, r * 1.1 * big, (255, 255, 255), w=2.5)
        c.ellipse(ex + 2 + look[0] * 3, ey + 1 + look[1] * 3, r * 0.5, r * 0.65, (40, 28, 30), ol=None)
        c.circle(ex + 4 + look[0] * 3, ey - 2 + look[1] * 2, r * 0.18, (255, 255, 255), ol=None)
        if lid and eyes != "wide":
            # sleepy camel lid
            c.poly([(ex - r - 1, ey - 2), (ex - r * 0.6, ey - r * 1.05), (ex + r * 0.6, ey - r * 1.05),
                    (ex + r + 1, ey - 2), (ex, ey - r * 0.3)], CAMEL_D, ol=None)
            c.line([(ex - r - 1, ey - 2), (ex, ey - r * 0.3), (ex + r + 1, ey - 2)], OUT, 2.5)
    for k in range(3):                                   # long eyelashes
        a = math.radians(-150 + k * 25)
        c.line([(ex + math.cos(a) * r, ey + math.sin(a) * r * 0.9),
                (ex + math.cos(a) * (r + 9), ey + math.sin(a) * (r + 8) - 2)], OUT, 2)


def camel(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), walk=0.0, lie=0.0,
          chew=0.0, seed=4.0, blanket=True):
    """Humphrey, a one-humped (dromedary) camel seen from the side, facing right (face=1).
    (x, y) = feet on the ground. About 345*s tall standing (head top), 400*s long.
    lie 0..1 folds the legs and lowers him onto the sand."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    lie = clamp(lie)
    by = lerp(-215, -78, lie)            # body centre
    bob = math.sin(walk * 2) * 3 if walk else 0.0
    by += bob
    # far legs
    if lie < 0.5:
        for hx, ph in ((-70, math.pi), (90, 0.0)):
            _camel_leg(c, hx, by + 30, walk, ph, CAMEL_D)
    else:
        for lx in (-70, 70):
            c.ellipse(lx, -14, 40, 13, CAMEL_D)
    # tail
    sw = math.sin(t * 2.4 + seed) * 6
    c.stroke([(-120, by - 8), (-132 + sw * 0.3, by + 30), (-130 + sw, by + 62)], CAMEL, 7)
    c.ellipse(-130 + sw, by + 70, 7, 12, (120, 84, 50), w=2)
    # body + hump
    c.ellipse(0, by, 126, 50, CAMEL)
    c.ellipse(-12, by - 52, 74, 60, CAMEL)
    c.ellipse(4, by + 2, 118, 45, CAMEL, ol=None)
    c.ellipse(-12, by - 44, 64, 46, CAMEL, ol=None)
    c.ellipse(-20, by - 70, 26, 14, CAMEL_L, ol=None)          # hump shine
    c.ellipse(10, by + 26, 80, 16, CAMEL_L, ol=None)           # belly
    if blanket:
        # a little striped saddle rug in front of the hump
        pts = [(46, by - 40), (98, by - 26), (90, by + 14), (40, by + 4)]
        c.poly(pts, (220, 70, 80), w=2.5)
        c.line([(44, by - 26), (94, by - 12)], (255, 210, 80), 4, cap=False)
        c.line([(42, by - 12), (92, by + 2)], (90, 150, 220), 4, cap=False)
        for k in range(4):
            fx = lerp(40, 90, k / 3)
            c.line([(fx, by + 4 + k * 3.3), (fx - 2, by + 14 + k * 3.3)], (255, 210, 80), 2.5)
    # near legs
    if lie < 0.5:
        for hx, ph in ((-90, 0.0), (70, math.pi)):
            _camel_leg(c, hx, by + 30, walk, ph, CAMEL)
    else:
        for lx in (-90, 50):
            c.ellipse(lx, -10, 44, 14, CAMEL)
            c.circle(lx + 30, -10, 9, CAMEL_D, w=2)
    # neck + head
    hx, hy = 212, lerp(-318, -196, lie) + bob
    nb = (96, by - 14)
    neck = [nb, (138, by - 24), (172, (by - 24 + hy) / 2 - 10), (hx - 22, hy + 6)]
    c.stroke(neck, CAMEL, 40)
    c.ellipse(hx - 26, hy + 10, 22, 22, CAMEL, ol=None)
    # ears
    c.ellipse(hx - 24, hy - 26, 8, 13, CAMEL_D)
    # head
    c.ellipse(hx, hy, 40, 27, CAMEL)
    c.ellipse(hx + 38, hy + 8, 28, 21, CAMEL_L)
    c.ellipse(hx + 10, hy + 2, 30, 20, CAMEL, ol=None)
    c.ellipse(hx + 32, hy + 7, 20, 15, CAMEL_L, ol=None)
    c.arc(hx + 52, hy - 2, 7, 4, 200, 330, OUT, 2.5)         # nostril
    # mouth
    ch = math.sin(t * 9) * 2.5 * chew
    jaw = 13 * clamp(mouth)
    if jaw > 1:
        c.ellipse(hx + 46, hy + 20 + jaw * 0.5, 16, 3 + jaw * 0.6, D.MOUTH, w=2)
        c.ellipse(hx + 46, hy + 24 + jaw * 0.8, 9, 2 + jaw * 0.25, D.TONGUE, ol=None)
    c.line([(hx + 26, hy + 18 + ch * 0.3), (hx + 44, hy + 22 + ch), (hx + 64, hy + 16 + ch * 0.5)], OUT, 2.5)
    c.ellipse(hx + 6, hy + 10, 9, 5, (236, 160, 140), ol=None)  # blush
    _eye(c, hx - 2, hy - 8, eyes, look, 10)
    c.pop()


def _camel_leg(c, hx, top, walk, ph, col):
    sw = math.sin(walk + ph) if walk else 0.0
    lift = max(0.0, math.cos(walk + ph)) * 10 if walk else 0.0
    foot = (hx + sw * 18, -lift)
    knee = (hx + sw * 8 + 4, lerp(top, foot[1], 0.5))
    c.stroke([(hx, top), knee, foot], col, 17)
    c.circle(knee[0], knee[1], 10, mix(col, (0, 0, 0), 0.08), w=2)
    c.ellipse(foot[0] + 4, foot[1] - 4, 15, 7, mix(col, (0, 0, 0), 0.12), w=2.5)


def camel_spots(x, y, s, face, lie=0.0, walk=0.0):
    """Where riders sit on the camel: {'front', 'back', 'top'} -> (x, y)."""
    by = lerp(-215, -78, lie) + (math.sin(walk * 2) * 3 if walk else 0.0)
    loc = {"front": (66, by - 34), "back": (-104, by - 34), "top": (-12, by - 110)}
    return {k: (x + face * px * s, y + py * s) for k, (px, py) in loc.items()}


def camel_hump(x, y, s, face, lie=0.0):
    by = lerp(-215, -78, lie)
    return x + face * -12 * s, y + (by - 60) * s


def camel_head(x, y, s, face, lie=0.0):
    return x + face * 230 * s, y + (lerp(-318, -196, lie) + 6) * s


# ============================================================================== Fizz

FOX = (244, 214, 160)
FOX_D = (214, 176, 118)
FOX_W = (255, 248, 236)
EAR_IN = (255, 184, 186)


def fennec(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), wiggle=0.0, wave=0.0,
           seed=7.0):
    """Fizz, a fennec fox sitting, facing right. (x, y) = feet. About 200*s tall to the ear tips."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    # bushy tail along the ground
    tw = math.sin(t * 3 + seed) * 4
    tail = [(-14, -10), (-44, -26 + tw * 0.5), (-80, -24 + tw), (-96, -12 + tw), (-82, -4 + tw * 0.5),
            (-46, -4), (-12, 0)]
    c.poly(tail, FOX)
    c.ellipse(-92, -14 + tw, 12, 10, (120, 84, 60), w=2.5)
    # body
    c.ellipse(0, -40, 32, 38, FOX)
    c.ellipse(10, -34, 17, 27, FOX_W, ol=None)
    # paws (one waves)
    c.stroke([(8, -24), (8, -3)], FOX, 9)
    c.ellipse(10, -3, 8, 4.5, FOX, w=2)
    if wave > 0.01:
        a = -0.6 - 0.9 * wave + 0.35 * math.sin(t * 12) * wave
        px, py = 26 + math.cos(a) * 34, -40 + math.sin(a) * 34
        c.stroke([(22, -44), (px, py)], FOX, 9)
        c.circle(px, py, 6, FOX, w=2)
    else:
        c.stroke([(24, -24), (25, -3)], FOX, 9)
        c.ellipse(27, -3, 8, 4.5, FOX, w=2)
    # ears: huge, they wiggle
    hx, hy = 16, -92
    wg = math.sin(t * 7) * 6 * wiggle + math.sin(t * 1.3 + seed) * 2
    for (bx0, tipx, tipy, bx1), dk in (((-10, -26, -196, 12), 1), ((14, 44, -200, 42), 0)):
        tip = (tipx + wg * (1 if dk else -1), tipy)
        base = [(bx0, hy - 14), tip, (bx1, hy - 12)]
        c.poly(base, FOX if not dk else FOX_D)
        inner = [(lerp(bx0, tip[0], 0.12) + 4, hy - 20), (lerp(bx0, tip[0], 0.85) + (bx1 - bx0) * 0.12,
                                                          lerp(hy - 14, tip[1], 0.85)), (bx1 - 5, hy - 18)]
        c.poly(inner, EAR_IN, ol=None)
        for k in range(3):                                  # ear fluff
            fy = lerp(hy - 24, tip[1], 0.2 + 0.15 * k)
            fx = lerp(lerp(bx0, tip[0], 0.2 + 0.15 * k), lerp(bx1, tip[0], 0.2 + 0.15 * k), 0.5)
            c.line([(fx - 5, fy + 4), (fx + 3, fy - 4)], FOX_W, 2)
    # head
    c.ellipse(hx, hy, 32, 27, FOX)
    c.ellipse(hx + 10, hy + 10, 22, 13, FOX_W, ol=None)
    c.poly([(hx + 22, hy - 4), (hx + 50, hy + 6), (hx + 24, hy + 16)], FOX_W, ol=None)
    c.line([(hx + 24, hy - 5), (hx + 50, hy + 4)], OUT, 2.5)
    c.line([(hx + 26, hy + 16), (hx + 48, hy + 10)], OUT, 2.5)
    c.circle(hx + 50, hy + 6, 6, (40, 30, 34), ol=None)
    c.circle(hx + 51, hy + 4, 1.8, (255, 255, 255), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 36, hy + 15, 6, 2 + 6 * mouth, D.MOUTH, w=2)
    else:
        c.arc(hx + 36, hy + 12, 6, 4, 20, 160, OUT, 2)
    c.ellipse(hx + 6, hy + 8, 7, 4, (255, 170, 170), ol=None)
    for ex in (hx + 2, hx + 22):
        ey = hy - 6
        if eyes == "closed":
            c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
        else:
            big = 1.25 if eyes == "wide" else 1.0
            c.ellipse(ex + look[0] * 1.5, ey + look[1] * 1.5, 6 * big, 8 * big, (40, 30, 34), ol=None)
            c.circle(ex + 2 + look[0] * 1.5, ey - 3, 2.2, (255, 255, 255), ol=None)
    c.pop()


def fox_ears(x, y, s, face):
    """Screen positions of Fizz's two ear tips."""
    return [(x + face * (-26) * s, y - 196 * s), (x + face * 44 * s, y - 200 * s)]


# ============================================================================== scenery

def palm(c, x, y, s=1.0, t=0.0, lean=0.12, dates=True, seed=1):
    """Date palm: curved ringed trunk and a crown of fronds. (x, y) = foot of the trunk."""
    c.push(x, y, s)
    hgt = 300
    pts = [(math.sin(u * 1.4) * lean * hgt * 0.9, -u * hgt) for u in np.linspace(0, 1, 12)]
    c.stroke(pts, (160, 112, 70), 22)
    for i in range(1, 11):
        px, py = pts[i]
        c.arc(px, py, 12, 5, 20, 160, (120, 82, 50), 2.5)
    tx, ty = pts[-1]
    sway = math.sin(t * 1.2 + seed) * 0.05
    for k, ang in enumerate((-170, -140, -110, -70, -40, -10, 15, 200)):
        a = math.radians(ang) + sway
        L = 130 if k not in (2, 3) else 110
        droop = 40 if abs(math.cos(a)) > 0.5 else 20
        tip = (tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + droop)
        mid = (tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.5 - 12)
        nx, ny = -(tip[1] - ty), tip[0] - tx
        nl = math.hypot(nx, ny) + 1e-6
        nx, ny = nx / nl * 16, ny / nl * 16
        col = (70, 158, 80) if k % 2 else (92, 178, 92)
        c.poly([(tx, ty), (mid[0] + nx, mid[1] + ny), tip, (mid[0] - nx, mid[1] - ny)], col, w=2.5)
        c.line([(tx, ty), mid, tip], mix(col, (0, 0, 0), 0.25), 2)
    if dates:
        for dx, dy in ((-10, 10), (4, 14), (14, 8), (-2, 20)):
            c.circle(tx + dx, ty + dy, 7, (170, 90, 50), w=2)
    c.pop()


def dune_shape(c, x0, x1, base, px, py, lit=SAND, shade=SAND_D, ripples=True, rng_seed=0):
    """One dune: smooth slope up from x0 to the crest (px, py), down to x1. Sun from the left:
    the slope right of the crest is in shadow."""
    left = [(lerp(x0, px, u), base - (base - py) * math.sin(u * math.pi / 2) ** 1.6) for u in np.linspace(0, 1, 18)]
    right = [(lerp(px, x1, u), base - (base - py) * (1 - u) ** 1.3) for u in np.linspace(0, 1, 18)]
    c.poly([(x0, base + 400)] + left + right[1:] + [(x1, base + 400)], lit, w=3)
    # shadow side: from the crest, a curved line down the face
    sh = [(px, py)] + [(lerp(px, x1, u) - 30 * math.sin(u * math.pi) * 0.0, base - (base - py) * (1 - u) ** 1.3)
                      for u in np.linspace(0, 1, 18)][1:]
    inner = [(lerp(px, lerp(px, x1, 0.25), u), lerp(py, base + 40, u)) for u in np.linspace(0, 1, 10)]
    c.poly(sh + [(x1, base + 400), (lerp(px, x1, 0.25), base + 400)] + inner[::-1], shade, ol=None)
    c.line(right, OUT, 3)
    if ripples:
        rng = np.random.default_rng(rng_seed)
        for _ in range(int(abs(px - x0) / 40)):
            u = rng.uniform(0.15, 0.95)
            rx = lerp(x0, px, u) + rng.uniform(-10, 10)
            ry = base - (base - py) * math.sin(u * math.pi / 2) ** 1.6 + rng.uniform(14, 60)
            c.arc(rx, ry, rng.uniform(16, 30), 5, 200, 340, mix(lit, (0, 0, 0), 0.12), 2)


def sky_canvas(stops):
    return Canvas(D.gradient(W * SS, H * SS, stops))


DAY_SKY = [(0, (110, 180, 240)), (0.5, (190, 222, 246)), (0.62, (252, 236, 200)), (1, (252, 236, 200))]
DUSK_SKY = [(0, (80, 70, 150)), (0.35, (220, 120, 140)), (0.62, (255, 186, 110)), (1, (255, 186, 110))]
NIGHT_SKY = [(0, (14, 18, 52)), (0.45, (34, 36, 92)), (0.62, (60, 56, 120)), (1, (60, 56, 120))]


@lru_cache(None)
def sky_image(which):
    stops = {"day": DAY_SKY, "dusk": DUSK_SKY, "night": NIGHT_SKY}[which]
    c = sky_canvas(stops)
    if which == "night":
        D.stars(c, 11, 160, W, H * 0.55)
    return c.img


KEY = (255, 0, 255)


def layer(draw_fn, tint=None):
    """Draw a foreground on a magenta key; returns (RGB image, L mask) for pasting over a sky."""
    c = Canvas(bg=KEY)
    if tint:
        c.tint = tint
    draw_fn(c)
    arr = np.array(c.img)
    mask = ~((arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255))
    return c.img, Image.fromarray((mask * 255).astype(np.uint8), "L")


def heat_shimmer(c, y, t, x0=0, x1=W, col=(255, 250, 230), n=7):
    for k in range(n):
        yy = y + k * 9
        ph = t * 3 + k * 1.3
        pts = [(x, yy + 3 * math.sin(x / 40 + ph)) for x in np.linspace(x0 + 40 * (k % 3), x1, 50)]
        segs = len(pts) // 5
        for j in range(0, len(pts) - segs, segs * 2):
            c.line(pts[j:j + segs], col, 2)


def sun(c, x, y, r=46, t=0.0, col=(255, 230, 110), rays=True):
    c.glow(x, y, r * 3.2, r * 2.6, mix(col, (255, 255, 255), 0.5), (255, 246, 214), steps=8) if rays else None
    if rays:
        for i in range(12):
            a = i / 12 * math.tau + t * 0.3
            c.line([(x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 1.25),
                    (x + math.cos(a) * r * 1.6, y + math.sin(a) * r * 1.6)], (255, 200, 80), 5)
    c.circle(x, y, r, col, ol=(236, 160, 60), w=3)


def sand_grains(c, x, y, t, k=1.0, n=40, spread=300, rise=60, seed=3, col=SAND_L):
    """Sand blowing off a crest to the right."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        u = (t * rng.uniform(0.6, 1.1) + rng.random()) % 1
        px = x + u * spread
        py = y - math.sin(u * math.pi) * rise * rng.uniform(0.3, 1) + rng.uniform(-10, 10)
        r = rng.uniform(1.5, 3.5) * k
        c.circle(px, py, r, col, ol=None)


def wind_lines(c, x, y, t, k=1.0, w=260, n=4, col=(255, 255, 255)):
    if k <= 0.01:
        return
    for i in range(n):
        u = (t * 0.9 + i / n) % 1
        xx = x + u * w
        yy = y + i * 26 - 30
        ln = 90 * k * math.sin(u * math.pi)
        if ln > 4:
            pts = [(xx + j * ln / 8, yy + 4 * math.sin(j * 0.9 + t * 4)) for j in range(9)]
            c.line(pts, col, 4)
            c.arc(xx + ln, yy - 8, 10, 10, 270, 450, col, 4)


def straw(c, pts, col=(240, 110, 150), stripe=(255, 255, 255)):
    c.stroke(pts, col, 7)
    for a, b in zip(pts, pts[1:]):
        for f in (0.25, 0.75):
            px, py = lerp(a[0], b[0], f), lerp(a[1], b[1], f)
            c.circle(px, py, 2.5, stripe, ol=None)


def tuna_tin(c, x, y, s=1.0):
    c.push(x, y, s)
    c.ellipse(0, 10, 44, 14, (170, 176, 190))
    c.rect(-44, -10, 44, 10, (190, 196, 210), ol=None)
    c.line([(-44, -10), (-44, 10)], OUT, 3)
    c.line([(44, -10), (44, 10)], OUT, 3)
    c.rect(-44, -8, 44, 6, (80, 140, 210), ol=None)
    K.text(c, 0, -1, "TUNA", 16, (255, 255, 255))
    c.ellipse(0, -10, 44, 14, (226, 230, 238))
    c.ellipse(0, -10, 34, 9, (236, 160, 140), ol=None)
    c.pop()


def bowl(c, x, y, s=1.0, full=0.0):
    c.push(x, y, s)
    c.ellipse(0, -30, 52, 14, (90, 90, 120))
    if full > 0:
        c.ellipse(0, -28, 44 * full, 10 * full, WATER, ol=None)
    c.poly([(-52, -30), (52, -30), (40, 0), (-40, 0)], (90, 130, 220))
    c.ellipse(0, -30, 52, 14, None, ol=OUT, w=3)
    K.text(c, 0, -14, "W", 20, (255, 255, 255))
    c.pop()


def litter_box(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-70, -40), (70, -40), (58, 10), (-58, 10)], (120, 190, 220))
    c.ellipse(0, -40, 70, 14, SAND)
    for dx in (-40, -10, 22, 46):
        c.circle(dx, -40 + (dx % 7) - 3, 3, SAND_D, ol=None)
    c.pop()


# ============================================================================== diagrams

def cloud(c, x, y, s=1.0, col=(255, 255, 255), dark=False):
    col = (150, 160, 180) if dark else col
    for dx, dy, r in ((-34, 6, 24), (-8, -10, 30), (24, -2, 26), (44, 10, 18), (0, 12, 26)):
        c.circle(x + dx * s, y + dy * s, r * s, col, w=2.5)
    for dx, dy, r in ((-34, 6, 22), (-8, -10, 28), (24, -2, 24), (44, 10, 16), (0, 12, 24)):
        c.circle(x + dx * s, y + dy * s, r * s, col, ol=None)


def drop(c, x, y, r, col=WATER, ol=OUT):
    c.poly([(x, y - r * 1.7), (x + r * 0.75, y - r * 0.35), (x - r * 0.75, y - r * 0.35)], col, ol=None)
    c.circle(x, y, r, col, ol=ol, w=2)
    c.poly([(x, y - r * 1.7), (x + r * 0.78, y - r * 0.5), (x - r * 0.78, y - r * 0.5)], col, ol=None)
    c.line([(x - r * 0.86, y - r * 0.45), (x, y - r * 1.75), (x + r * 0.86, y - r * 0.45)], OUT, 2)
    c.ellipse(x - r * 0.35, y - r * 0.2, r * 0.18, r * 0.3, (230, 245, 255), ol=None)


def rain_diagram(ic, t, k1, k2):
    """Two windows: a rainy green place (lots of rain) and a desert (very little rain)."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    half = w / 2
    # rainy side
    ic.img.paste((206, 222, 238), (0, 0, int(half * SS), int(h * SS)))
    ic.rect(0, h - 70, half, h, (120, 190, 92), ol=None)
    D.tree(ic, 70, h - 66, 0.45)
    D.bush(ic, 168, h - 64, 0.5)
    cloud(ic, half / 2, 52, 1.0, dark=True)
    if k1 > 0:
        rng = np.random.default_rng(2)
        for i in range(22):
            u = (t * 1.6 + rng.random()) % 1
            dx = rng.uniform(-60, 60)
            ic.line([(half / 2 + dx, 80 + u * (h - 160)), (half / 2 + dx - 3, 92 + u * (h - 160))],
                    (70, 130, 220), 3)
    K.text(ic, half / 2, h - 30, "Lots of rain", 24, (255, 255, 255), stroke=3)
    # desert side
    if k2 > 0:
        ic.img.paste((252, 236, 196), (int(half * SS), 0, int(w * SS), int(h * SS)))
        dune_shape(ic, half - 20, w + 60, h - 40, half + 150, h - 110, ripples=False)
        sun(ic, w - 50, 46, 22, t, rays=True)
        cloud(ic, half + 100, 56, 0.6)
        u = (t * 0.45) % 1
        if u < 0.6:
            drop(ic, half + 100, 86 + u * 110, 7)
        K.text(ic, half + half / 2, h - 30, "Very little rain", 24, (200, 110, 30), stroke=3,
               stroke_fill=(255, 255, 255))
    ic.line([(half, 0), (half, h)], OUT, 4, cap=False)


def dune_diagram(ic, t, k):
    """Wind blows the sand grains up a slope and they pile into a dune."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste((250, 238, 210), (0, 0, int(w * SS), int(h * SS)))
    gh = h - 60
    top = lerp(gh - 10, 70, ease(k))
    dune_shape(ic, 40, w + 60, gh, w * 0.62, top, ripples=False)
    ic.rect(0, gh, w, h, SAND, ol=None)
    ic.line([(0, gh), (w, gh)], OUT, 3)
    wind_lines(ic, 20, 90, t, 1.0, 180, 3, (110, 160, 220))
    rng = np.random.default_rng(4)
    for i in range(26):
        u = (t * 0.7 + rng.random()) % 1
        x = lerp(30, w * 0.62, u)
        slope_y = gh - (gh - top) * math.sin(clamp((x - 40) / (w * 0.62 - 40)) * math.pi / 2) ** 1.6
        ic.circle(x, slope_y - 8 - rng.uniform(0, 20), 3, SAND_DD, ol=None)
    K.text(ic, 80, 40, "Wind", 26, (70, 120, 200), stroke=2, stroke_fill=(255, 255, 255))
    K.text(ic, w / 2, h - 28, "The wind piles sand into dunes", 24, (120, 80, 40))


def hump_diagram(ic, t, k_fat, k_x):
    """Cut-away hump: inside is fat (a food store), not water."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste((250, 244, 230), (0, 0, int(w * SS), int(h * SS)))
    cx, base = 170, h - 46
    ic.rect(cx - 150, base - 30, cx + 150, base + 40, CAMEL, w=3, r=20)
    ic.ellipse(cx, base - 34, 112, 104, CAMEL, w=3)
    ic.rect(cx - 146, base - 26, cx + 146, base + 36, CAMEL, ol=None, r=18)
    # cut-away window
    ic.ellipse(cx, base - 44, 88, 78, (255, 244, 214), w=3)
    rng = np.random.default_rng(3)
    n = int(18 * k_fat)
    for i in range(n):
        a = rng.uniform(0, math.tau)
        rr = math.sqrt(rng.uniform(0, 1))
        px, py = cx + math.cos(a) * rr * 66, base - 44 + math.sin(a) * rr * 56
        ic.circle(px, py, rng.uniform(12, 20), FAT, ol=FAT_D, w=2)
    if k_fat > 0.4:
        K.label(ic, cx, base - 44, "FAT", 34, k=clamp((k_fat - 0.4) / 0.4), col=(190, 120, 30))
    # right side: food store vs not water
    x2 = w - 120
    if k_fat > 0.6:
        K.text(ic, x2, 52, "Food store!", 28, (90, 150, 60), stroke=2, stroke_fill=(255, 255, 255))
        for i, (dx, col) in enumerate(((-40, (230, 80, 80)), (0, (250, 200, 60)), (40, (120, 190, 80)))):
            ic.circle(x2 + dx, 98, 15, col, w=2)
    if k_x > 0:
        drop(ic, x2, 186, 26)
        kk = K.pop(k_x)
        ic.push(x2, 176, kk)
        ic.line([(-40, -40), (40, 40)], (226, 50, 50), 10)
        ic.line([(40, -40), (-40, 40)], (226, 50, 50), 10)
        ic.pop()
        K.text(ic, x2, h - 26, "Not water!", 28, (226, 50, 50), stroke=2, stroke_fill=(255, 255, 255))


def beetle(c, x, y, s=1.0, t=0.0):
    c.push(x, y, s)
    for k in (-1, 0, 1):
        ph = math.sin(t * 14 + k) * 3
        c.line([(k * 10, 0), (k * 12 - 6, 14 + ph)], OUT, 2.5)
        c.line([(k * 10, 0), (k * 12 + 6, 14 - ph)], OUT, 2.5)
    c.ellipse(0, 0, 22, 14, (60, 50, 70), w=2)
    c.line([(0, -14), (0, 14)], (30, 24, 36), 2)
    c.circle(24, 0, 8, (60, 50, 70), w=2)
    c.ellipse(-6, -5, 6, 3, (120, 110, 140), ol=None)
    c.pop()


def hear_diagram(ic, t, k):
    """A beetle walking under the sand; sound waves rise to a big fennec ear."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste((252, 238, 206), (0, 0, int(w * SS), int(h * SS)))
    gy = 80
    ic.rect(0, gy, w, h, SAND_D, ol=None)
    ic.line([(0, gy), (w, gy)], OUT, 3)
    rng = np.random.default_rng(1)
    for _ in range(40):
        ic.circle(rng.uniform(0, w), rng.uniform(gy + 8, h), rng.uniform(1.5, 3), SAND_DD, ol=None)
    bx = 80 + ((t * 30) % (w - 160))
    beetle(ic, bx, h - 48, 0.9, t)
    if k > 0:
        for i in range(3):
            u = (t * 1.2 + i / 3) % 1
            r = 20 + u * 70
            ic.arc(bx, h - 48, r, r * 0.8, 230, 310, mix((226, 90, 60), (252, 238, 206), u), 4)
    # a big ear sticking down from the top
    ic.poly([(w - 120, 0), (w - 70, 64), (w - 20, 0)], FOX, w=3)
    ic.poly([(w - 104, 0), (w - 70, 46), (w - 36, 0)], EAR_IN, ol=None)
    K.text(ic, 130, 36, "I can hear you!", 24, (190, 80, 40))


def temp_diagram(ic, t, k_day, k_night):
    """Hot day / cold night: sun + full red thermometer, moon + low blue thermometer."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    half = w / 2
    ic.img.paste((255, 226, 160), (0, 0, int(half * SS), int(h * SS)))
    ic.img.paste((40, 44, 100), (int(half * SS), 0, int(w * SS), int(h * SS)))
    sun(ic, 80, 74, 34, t)
    thermo(ic, 200, h - 66, 0.85, lerp(0.15, 0.95, ease(k_day)))
    K.text(ic, half / 2, h - 26, "Day: hot!", 28, (220, 70, 50), stroke=2, stroke_fill=(255, 255, 255))
    for sx, sy in ((half + 40, 30), (half + 200, 50), (w - 30, 120), (half + 140, 120), (half + 30, 150)):
        K.star(ic, sx, sy, 6, (255, 250, 210))
    D.moon(ic, half + 90, 80, 34, sky=(40, 44, 100))
    thermo(ic, w - 70, h - 66, 0.85, lerp(0.95, 0.2, ease(k_night)) if k_night > 0 else 0.95)
    if k_night > 0.3:
        K.text(ic, half + half / 2, h - 26, "Night: cold!", 28, (150, 200, 255), stroke=2,
               stroke_fill=(20, 24, 60))
    ic.line([(half, 0), (half, h)], OUT, 4, cap=False)


def thermo(c, x, y, s=1.0, level=1.0):
    c.push(x, y, s)
    c.rect(-16, -150, 16, 0, (255, 255, 255), r=16, w=3)
    c.circle(0, 10, 25, (255, 255, 255), w=3)
    col = mix((90, 160, 240), (230, 70, 70), clamp(level))
    top = lerp(-10, -136, clamp(level))
    c.rect(-8, top, 8, 4, col, ol=None, r=8)
    c.circle(0, 10, 18, col, ol=None)
    for k in range(5):
        yy = -28 - k * 24
        c.line([(16, yy), (25, yy)], OUT, 2.5)
    c.pop()


def snowflake(c, x, y, r, col=(140, 196, 240), w=3):
    for i in range(6):
        a = i * math.pi / 3
        c.line([(x, y), (x + math.cos(a) * r, y + math.sin(a) * r)], col, w)


def ant_diagram(ic, t, k):
    """Antarctica: the biggest desert of all (cold!) next to the Sahara, the biggest HOT desert."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    gx, gy, r = 150, h / 2 - 10, 104
    K.globe(ic, gx, gy, r, lon=20 + t * 6, lat=-64, glow=0.3)
    # a rare snowflake drifting down
    u = (t * 0.25) % 1
    snowflake(ic, gx - 30 + 10 * math.sin(t * 2), gy - r - 10 + u * 90, 9, (255, 255, 255), 3)
    K.text(ic, gx, h - 18, "Antarctica", 26, (255, 255, 255), stroke=3)
    x2 = 300
    K.text(ic, x2, 52, "Biggest desert", 28, (255, 255, 255), anchor="lm", stroke=3)
    K.text(ic, x2, 86, "of all: COLD!", 28, (150, 210, 255), anchor="lm", stroke=3)
    if k > 0:
        kk = K.pop(k)
        ic.push(x2 + 54, 176, kk)
        ic.circle(0, 0, 46, (255, 236, 180), w=3)
        sun(ic, 14, -18, 12, t, rays=False)
        dune_shape(ic, -46, 46, 34, -4, 6, ripples=False)
        ic.pop()
        K.text(ic, x2 + 112, 164, "Sahara: biggest", 24, (255, 220, 120), anchor="lm", stroke=3)
        K.text(ic, x2 + 112, 192, "HOT desert", 24, (255, 220, 120), anchor="lm", stroke=3)


# ============================================================================== icons

def icon_rain(c, x, y, r, t=0.0):
    """Very little rain: a dune under a small cloud with one drop."""
    c.circle(x, y, r * 0.95, (252, 236, 196), w=3)
    dune_shape(c, x - r * 0.9, x + r * 0.9, y + r * 0.62, x - r * 0.1, y + r * 0.15, ripples=False)
    c.circle(x, y, r * 0.95, None, ol=OUT, w=3)
    cloud(c, x - r * 0.05, y - r * 0.45, r / 110)
    drop(c, x + r * 0.05, y - r * 0.05, r * 0.13)


def icon_heat(c, x, y, r, t=0.0):
    """Lots of heat: a blazing sun."""
    sun(c, x, y - r * 0.05, r * 0.45, t, rays=True)


def icon_sahara(c, x, y, r, t=0.0):
    """The Sahara on a little globe turned to Africa (deserts are the yellow parts)."""
    K.globe(c, x, y, r * 0.95, lon=15, lat=14)
    gx, gy, _ = K.globe_xy(x, y, r * 0.95, 10, 23, 15, 14)
    c.circle(gx, gy, r * 0.32, None, ol=(226, 60, 60), w=3)


def icon_hump(c, x, y, r, t=0.0):
    """A camel hump cut open: full of fat."""
    c.rect(x - r * 0.9, y + r * 0.2, x + r * 0.9, y + r * 0.7, CAMEL, w=2.5, r=8)
    c.ellipse(x, y + r * 0.15, r * 0.7, r * 0.7, CAMEL, w=2.5)
    c.rect(x - r * 0.86, y + r * 0.24, x + r * 0.86, y + r * 0.66, CAMEL, ol=None, r=6)
    c.ellipse(x, y + r * 0.1, r * 0.52, r * 0.5, (255, 244, 214), w=2)
    for dx, dy in ((-0.2, 0.0), (0.18, -0.1), (0.0, 0.25), (0.25, 0.22), (-0.24, 0.28), (0.0, -0.22)):
        c.circle(x + dx * r, y + r * 0.1 + dy * r, r * 0.14, FAT, ol=FAT_D, w=1.5)


def icon_water_drop(c, x, y, r, t=0.0):
    drop(c, x, y + r * 0.25, r * 0.42)


def icon_fat(c, x, y, r, t=0.0):
    icon_hump(c, x, y - r * 0.1, r * 1.1, t)
