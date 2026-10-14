"""Props for Episode 10 "Day and Night, Earth and Sun": Professor Hoot the owl, the torch and its
beam, Luna's old globe with a night side, the Sun, Moon phases, the day/night shading on the magic
map, the Hawaii night beach, a birthday cake, a 24-hour clock and the season-recap cards."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, LW, lerp, clamp, mix, ease
from world import kit as K
from films.athens import props as ATH

TAU = 2 * math.pi


# ====================================================================== helpers

def soft_poly(c, pts, col, alpha):
    """Translucent polygon (light beams, night shading) in c's current transform."""
    if alpha <= 0.01:
        return
    m = Image.new("L", c.img.size, 0)
    ImageDraw.Draw(m).polygon([c.P(x, y) for x, y in pts], fill=int(255 * clamp(alpha)))
    c.img.paste(col, (0, 0), m)


def sprite(c, x, y, size, angle, fn):
    """Draw fn(sc, cx, cy) into a transparent square sprite, rotate it (degrees, counter-clockwise)
    and paste it centred at (x, y)."""
    n = int(size * SS)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    sc = Canvas(img)
    fn(sc, size / 2, size / 2)
    if abs(angle) > 0.01:
        img = img.rotate(angle, resample=Image.BICUBIC)
    px, py = c.P(x, y)
    c.img.paste(img, (int(px - n / 2), int(py - n / 2)), img)


# ================================================================ Professor Hoot

CAP = (60, 56, 92)


def owl(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", flap=0.0, look=(0.0, 0.0), hop=0.0, cap=True):
    """Professor Hoot: a wise owl with spectacles and a little scholar's cap.
    (x, y) = feet; about 135*s tall with the cap."""
    ATH.owl(c, x, y, s * 1.0, face, t, mouth, eyes, flap, gran=True, look=look, seed=5.0, hop=hop * s)
    if cap:
        c.push(x, y - hop * s, s, flip=face < 0)
        hy = -78 - 22
        c.rect(-15, hy - 4, 15, hy + 6, CAP, r=3, w=2.5)
        c.poly([(-30, hy - 6), (0, hy - 16), (30, hy - 6), (0, hy + 3)], CAP, w=2.5)
        sw = math.sin(t * 2.5) * 3
        c.line([(0, hy - 7), (22, hy - 4), (24 + sw * 0.3, hy + 14)], (255, 200, 70), 2.5)
        c.circle(24 + sw * 0.3, hy + 17, 3.5, (255, 200, 70), w=1.5)
        c.pop()


# ============================================================ torch and beams

def torch(c, x, y, s=1.0, ang=0.0, on=1.0):
    """A torch (flashlight). (x, y) = the lamp end; it points along ang (degrees, 0 = right)."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)

    def R(px, py):
        return x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s
    body = [R(-70, -9), R(-14, -9), R(0, -16), R(0, 16), R(-14, 9), R(-70, 9)]
    c.poly(body, (226, 70, 80), w=2.5)
    c.poly([R(-60, -9), R(-54, -9), R(-54, 9), R(-60, 9)], (255, 214, 90), ol=None)
    c.poly([R(-3, -16), R(2, -16), R(2, 16), R(-3, 16)], (220, 224, 236), w=2)
    c.poly([R(-40, -12), R(-30, -12), R(-30, -9), R(-40, -9)], (60, 60, 70), w=1.5)
    if on > 0.05:
        px, py = R(4, 0)
        c.circle(px, py, 6 * s * on, (255, 252, 210), ol=None)


def beam(c, x, y, ang, length, w0, w1, k=1.0, col=(255, 244, 170)):
    """A soft cone of light from (x, y) along ang (degrees)."""
    if k <= 0.01:
        return
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    px, py = -sa, ca
    L = length * k
    for f, al in ((1.0, 0.18), (0.7, 0.18), (0.4, 0.2)):
        pts = [(x + px * w0 * f, y + py * w0 * f), (x + ca * L + px * w1 * f, y + sa * L + py * w1 * f),
               (x + ca * L - px * w1 * f, y + sa * L - py * w1 * f), (x - px * w0 * f, y - py * w0 * f)]
        soft_poly(c, pts, col, al * k)


# ============================================================== Luna's old globe

def lit_old_globe(c, x, y, s=1.0, lon=0.0, sun=None, glow=0.0, t=0.0, r=100):
    """K.old_globe with an optional night side: sun = (lon, lat) where the 'torch' is overhead."""
    c.push(x, y, s)
    gy = -(r + 70)
    if glow > 0.01:
        K._halo(c, 0, gy, r, glow, (255, 236, 150))
    c.ellipse(0, -8, 70, 16, K.WOOD_D)
    c.ellipse(0, -16, 64, 14, K.WOOD)
    c.rect(-10, -64, 10, -14, K.WOOD, r=4)
    c.ellipse(0, -66, 22, 8, K.WOOD_D)
    c.stroke([(0, -66), (0, gy + r + 6)], K.BRASS, 7)
    ring = r + 12
    a = math.radians(-23.5)

    def half(u0):
        pts = []
        for i in range(25):
            u = u0 + math.pi * i / 24
            px, py = math.cos(u) * ring, math.sin(u) * ring
            pts.append((px * math.cos(a) - py * math.sin(a), gy + px * math.sin(a) + py * math.cos(a)))
        return pts
    c.stroke(half(math.pi / 2), K.BRASS_D, 6)
    K.globe(c, 0, gy, r, lon, 18, "toy", roll=-23.5, sun=sun)
    pts = half(-math.pi / 2)
    c.stroke(pts, K.BRASS, 7)
    for p in (pts[0], pts[-1]):
        c.circle(p[0], p[1], 6, K.BRASS, w=2)
    if glow > 0.01:
        K.sparkles(c, 0, gy, r * 1.5, t, n=12, k=glow, seed=9)
    c.pop()


# ======================================================================= the Sun

def sun(c, x, y, r, t=0.0, face=True, rays=True, glow=True, mouth=0.0):
    """A big friendly Sun with soft glow and turning rays."""
    if glow:
        K._halo(c, x, y, r * 1.05, 1.0, (255, 226, 120))
    if rays:
        n = 14
        for i in range(n):
            a = TAU * i / n + t * 0.15
            r0, r1 = r * 1.08, r * (1.32 + 0.06 * math.sin(t * 3 + i))
            w = r * 0.09
            px, py = -math.sin(a) * w, math.cos(a) * w
            c.poly([(x + math.cos(a) * r0 + px, y + math.sin(a) * r0 + py),
                    (x + math.cos(a) * r1, y + math.sin(a) * r1),
                    (x + math.cos(a) * r0 - px, y + math.sin(a) * r0 - py)], (255, 200, 70), w=2)
    c.circle(x, y, r, (255, 214, 80), w=3)
    c.circle(x - r * 0.12, y - r * 0.12, r * 0.78, (255, 230, 120), ol=None)
    if face and r > 20:
        for ex in (-0.3, 0.3):
            c.arc(x + ex * r, y - 0.08 * r, 0.12 * r, 0.1 * r, 200, 340, OUT, max(2, r * 0.035))
        c.circle(x - 0.5 * r, y + 0.18 * r, 0.1 * r, (255, 170, 110), ol=None)
        c.circle(x + 0.5 * r, y + 0.18 * r, 0.1 * r, (255, 170, 110), ol=None)
        if mouth > 0.05:
            c.ellipse(x, y + 0.26 * r, 0.14 * r, 0.06 * r + 0.08 * r * mouth, D.MOUTH, w=2)
        else:
            c.arc(x, y + 0.14 * r, 0.22 * r, 0.16 * r, 20, 160, OUT, max(2, r * 0.035))


# ====================================================================== the Moon

MOON = (246, 242, 214)
MOON_D = (226, 220, 186)
MOON_NIGHT = (70, 74, 110)


def moon_ball(c, x, y, r, sun_dir=180.0, dark=MOON_NIGHT, outline=True):
    """The Moon as a ball lit from direction sun_dir (degrees on screen, 180 = from the left):
    the half facing the Sun is bright, the other half dark."""
    c.circle(x, y, r, dark, ol=None)
    a = math.radians(sun_dir)
    pts = [(x + math.cos(a + u) * r, y + math.sin(a + u) * r) for u in np.linspace(-math.pi / 2, math.pi / 2, 30)]
    c.poly(pts, MOON, ol=None)
    for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.15, 0.12), (-0.05, 0.4, 0.1)):
        px, py = x + dx * r, y + dy * r
        if math.cos(math.atan2(py - y, px - x) - a) * math.hypot(px - x, py - y) > -rr * r * 0.3:
            c.circle(px, py, rr * r, MOON_D, ol=None)
    if outline:
        c.circle(x, y, r, None, ol=OUT, w=LW)


def moon_phase(c, x, y, r, phase, dark=MOON_NIGHT, outline=True, glow=False):
    """The Moon as we see it from Earth. phase 0 = new, 0.25 = first quarter (right half lit),
    0.5 = full, 0.75 = last quarter (left half lit)."""
    phase %= 1.0
    if glow:
        K._halo(c, x, y, r, 0.5 * math.sin(math.pi * phase) ** 2, (230, 230, 200))
    c.circle(x, y, r, dark, ol=None)
    k = math.cos(TAU * phase)          # terminator ellipse x-scale: 1 new .. -1 full
    right = phase < 0.5                # waxing: lit on the right
    s = 1 if right else -1
    pts = []
    for u in np.linspace(-math.pi / 2, math.pi / 2, 40):     # the lit limb
        pts.append((x + s * math.cos(u) * r, y + math.sin(u) * r))
    for u in np.linspace(math.pi / 2, -math.pi / 2, 40):     # back along the terminator
        pts.append((x + s * k * math.cos(u) * r, y + math.sin(u) * r))
    if abs(k) < 0.999 or k < 0:
        c.poly(pts, MOON, ol=None)
    if phase > 0.06 and phase < 0.94:
        for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.15, 0.12), (-0.05, 0.4, 0.1)):
            px = dx
            lit_edge = k if right else -k
            if (right and px > lit_edge * math.sqrt(max(0, 1 - dy * dy)) * 0.9) or \
                    (not right and px < -lit_edge * math.sqrt(max(0, 1 - dy * dy)) * 0.9) or abs(phase - 0.5) < 0.12:
                c.circle(x + dx * r, y + dy * r, rr * r, MOON_D, ol=None)
    if outline:
        c.circle(x, y, r, None, ol=OUT, w=max(1.5, min(LW, r * 0.06)))


# ============================================================ day / night on the map

def sun_dot(lon, lat, slon, slat):
    p, ps = np.radians(lat), math.radians(slat)
    return np.sin(p) * math.sin(ps) + np.cos(p) * math.cos(ps) * np.cos(np.radians(lon) - math.radians(slon))


def night_overlay(c, v, slon, slat=0.0, k=1.0, col=(14, 18, 60), strength=0.62):
    """Darken the night side of the magic map seen through MapView v (Sun overhead at slon, slat)."""
    if k <= 0.01:
        return
    x0, y0, x1, y1 = v.rect()
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    step = 4
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    xs = np.linspace(x0, x1, nx)
    ys = np.linspace(y0, y1, ny)
    mx = v.cx + (xs - W / 2) / v.z
    my = v.cy + (ys - H / 2) / v.z
    lon = mx / K.MW * 360 - 180
    lat = 90 - my / K.MH * 180
    LON, LAT = np.meshgrid(lon, lat)
    d = sun_dot(LON, LAT, slon, slat)
    night = np.clip(0.5 - d * 6, 0, 1) * strength * k
    m = Image.fromarray((night * 255).astype(np.uint8), "L")
    bx0, by0, bx1, by1 = int(x0 * SS), int(y0 * SS), int(x1 * SS), int(y1 * SS)
    m = m.resize((bx1 - bx0, by1 - by0), Image.BILINEAR)
    c.img.paste(col, (bx0, by0, bx1, by1), m)
    # a soft golden glow line along the terminator
    tw = np.clip(1 - np.abs(d) * 14, 0, 1) * 0.35 * k
    m2 = Image.fromarray((tw * 255).astype(np.uint8), "L").resize((bx1 - bx0, by1 - by0), Image.BILINEAR)
    c.img.paste((255, 200, 120), (bx0, by0, bx1, by1), m2)


# ================================================================== Hawaii beach

SAND = (238, 214, 160)
SAND_D = (210, 182, 128)
SEA_N = (28, 50, 104)
SEA_N2 = (40, 70, 130)
HORIZON = 330
SHORE = 520
MOON_XY = (930, 130)


def palm(c, x, y, s=1.0, t=0.0, lean=0.18, col=(48, 110, 80), trunk=(120, 92, 70)):
    c.push(x, y, s)
    pts = []
    for i in range(9):
        u = i / 8
        pts.append((lean * 260 * u * u, -280 * u))
    for i in range(len(pts) - 1):
        c.stroke([pts[i], pts[i + 1]], trunk, 20 - i)
    tx, ty = pts[-1]
    sw = math.sin(t * 1.3) * 3
    for ang in (-170, -140, -105, -70, -35, -5, 25):
        a = math.radians(ang + sw)
        ex, ey = tx + math.cos(a) * 120, ty + math.sin(a) * 70 + 40
        mid = (tx + math.cos(a) * 60, ty + math.sin(a) * 50 - 14)
        c.poly([(tx, ty), mid, (ex, ey), (mid[0] + 6, mid[1] + 18)], col, w=2.5)
    for dx in (-8, 8):
        c.circle(tx + dx, ty + 8, 8, (130, 90, 60), w=2)
    c.pop()


@lru_cache(None)
def beach_bg():
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (10, 14, 46)), (HORIZON / H, (40, 50, 110)),
                                           (HORIZON / H + 0.001, SEA_N), (SHORE / H, SEA_N2),
                                           (SHORE / H + 0.001, SAND), (1, SAND_D)]))
    D.stars(c, 11, 120, W, HORIZON - 20)
    rng = np.random.default_rng(4)
    for _ in range(8):
        K.star(c, rng.uniform(0, W), rng.uniform(10, HORIZON - 60), rng.uniform(4, 7), (255, 248, 210))
    D.moon(c, MOON_XY[0], MOON_XY[1], 46, sky=(20, 26, 70))
    # far island hills
    c.poly([(0, HORIZON), (90, HORIZON - 50), (200, HORIZON - 20), (290, HORIZON - 70), (420, HORIZON)],
           (22, 34, 64), ol=None)
    c.line([(0, HORIZON), (W, HORIZON)], (70, 90, 150), 2, cap=False)
    # sand ripples + shells
    for k in range(10):
        x = rng.uniform(40, W - 40)
        y = rng.uniform(SHORE + 60, H - 20)
        c.arc(x, y, 30, 6, 200, 340, SAND_D, 2)
    for x, y in ((180, 650), (1060, 610), (720, 690)):
        c.ellipse(x, y, 10, 6, (250, 200, 200), w=2)
    palm(c, 110, SHORE + 70, 1.1, 0.0)
    palm(c, 1190, SHORE + 60, 0.9, 0.0, lean=-0.2)
    return c.img


def sea_glints(c, t, y0=HORIZON + 10, y1=SHORE - 6, n=40, seed=2):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = (rng.uniform(0, W) + t * rng.uniform(6, 14)) % W
        y = rng.uniform(y0, y1)
        a = 0.5 + 0.5 * math.sin(t * rng.uniform(1, 3) + i)
        c.line([(x - 14, y), (x + 14, y)], mix(SEA_N2, (150, 170, 220), 0.4 * a), 2, cap=False)


def moon_path(c, t, x=MOON_XY[0]):
    """The Moon's shimmering road of light on the sea (where the 'Moon Fish' swims)."""
    for i in range(14):
        y = HORIZON + 12 + i * 13
        w = 10 + i * 4 + 6 * math.sin(t * 3 + i)
        c.ellipse(x + 6 * math.sin(t * 2 + i * 0.7), y, w, 2.2, (200, 206, 220), ol=None)


def surf(c, t, y=SHORE):
    """Gentle surf line at the water's edge."""
    pts = [(x, y + 5 * math.sin(x / 70 + t * 1.6)) for x in range(-10, W + 20, 20)]
    c.poly(pts + [(W + 10, y + 26), (-10, y + 26)], (60, 92, 150), ol=None)
    c.line(pts, (210, 226, 250), 4)


# ===================================================================== small bits

def cake(c, x, y, s=1.0, t=0.0, k=1.0):
    """A little birthday cake with one candle. (x, y) = bottom centre."""
    if k <= 0.01:
        return
    c.push(x, y, s * K.pop(k))
    c.rect(-46, -48, 46, 0, (250, 214, 226), r=8, w=3)
    c.rect(-46, -48, 46, -36, (255, 250, 250), r=6, w=2)
    for dx in (-30, -10, 10, 30):
        c.circle(dx, -34, 5, (255, 250, 250), ol=None)
    for dx, col in ((-28, (230, 70, 80)), (0, (90, 170, 230)), (28, (250, 200, 70))):
        c.circle(dx, -20, 4, col, ol=None)
    c.rect(-4, -76, 4, -48, (120, 180, 240), r=2, w=2)
    f = 1 + 0.15 * math.sin(t * 18)
    c.ellipse(0, -86, 6 * f, 10 * f, (255, 200, 60), w=2)
    c.ellipse(0, -84, 3, 5, (255, 250, 200), ol=None)
    c.pop()


def clock24(c, x, y, r, hours, t=0.0):
    """A 24-hour day dial: a yellow day half and a blue night half, with a hand at `hours`."""
    c.circle(x, y, r + 6, (255, 255, 255), w=3)
    pts_day = [(x, y)] + [(x + math.cos(a) * r, y + math.sin(a) * r) for a in np.linspace(math.pi, 2 * math.pi, 30)]
    pts_night = [(x, y)] + [(x + math.cos(a) * r, y + math.sin(a) * r) for a in np.linspace(0, math.pi, 30)]
    c.poly(pts_day, (255, 226, 120), ol=None)
    c.poly(pts_night, (60, 70, 140), ol=None)
    sun(c, x, y - r * 0.55, r * 0.17, t, face=False, glow=False)
    moon_phase(c, x - r * 0.08, y + r * 0.55, r * 0.17, 0.2, outline=False, dark=(60, 70, 140))
    for i in range(24):
        a = math.radians(90 + i * 15)
        r0 = r * (0.86 if i % 6 else 0.76)
        c.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r, y + math.sin(a) * r)],
               OUT, 2 if i % 6 else 3, cap=False)
    a = math.radians(90 + hours * 15)
    c.stroke([(x, y), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)], (226, 70, 80), 6)
    c.circle(x, y, 7, (226, 70, 80), w=2)
    c.circle(x, y, r, None, ol=OUT, w=3)


def sky_view(ic, hour, t=0.0, home=True):
    """Inset 'the sky at home': the Sun climbing up from the left and setting on the right as the
    Earth turns (hour: local solar time 0..24)."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    alt = math.cos(math.radians((hour - 12) * 15))          # -1 midnight .. 1 noon
    day = clamp(alt * 4 + 0.5)
    top = mix((20, 24, 70), (100, 176, 246), day)
    bot = mix((50, 56, 120), (210, 236, 255), day)
    if -0.3 < alt < 0.35:
        bot = mix(bot, (255, 170, 110), 1 - abs(alt - 0.02) / 0.33)
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, top), (1, bot)]), (0, 0))
    gy = h - 46
    if day < 0.6:
        D.stars(ic, 5, 18, w, gy - 20, col=mix((255, 250, 220), bot, day / 0.6))
    # Sun on an arc from left (east, sunrise) to right (west, sunset)
    u = ((hour - 6) / 12)
    sx = lerp(26, w - 26, u)
    sy = gy - alt * (gy - 40)
    if alt > -0.2:
        sun(ic, sx, sy, 22, t, face=True, glow=False)
    ic.poly([(0, gy), (w * 0.3, gy - 12), (w * 0.6, gy - 4), (w, gy - 14), (w, h), (0, h)],
            mix((40, 70, 50), (120, 190, 92), day), ol=None)
    hx = w * 0.5
    ic.rect(hx - 18, gy - 26, hx + 18, gy - 2, mix((120, 110, 120), (250, 240, 220), day), ol=None)
    ic.poly([(hx - 24, gy - 26), (hx, gy - 46), (hx + 24, gy - 26)], mix((90, 60, 60), (232, 120, 100), day),
            ol=None)
    ic.rect(hx - 5, gy - 18, hx + 5, gy - 8, (255, 226, 130) if day < 0.5 else (150, 200, 240), ol=None)


# ======================================================================= recap

def card_bg(ic, top, bot):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, top), (1, bot)]), (0, 0))
    return w, h


def try_draw(fn, *a, **kw):
    """Cameos come from other episodes' props; never let one of them break this finale."""
    try:
        fn(*a, **kw)
        return True
    except Exception:
        return False
