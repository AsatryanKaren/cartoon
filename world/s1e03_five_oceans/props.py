"""Props for Episode 3: the five oceans (tinted on the globe and the map), Bluebell the blue whale,
Nipper the crab, deep-sea creatures, and the little teaching diagrams."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, LW, lerp, clamp, mix, ease
from world import kit as K

# ============================================================================ the five oceans

OCEANS = ["pacific", "atlantic", "indian", "arctic", "southern"]
NAMES = {"pacific": "Pacific Ocean", "atlantic": "Atlantic Ocean", "indian": "Indian Ocean",
         "arctic": "Arctic Ocean", "southern": "Southern Ocean"}
SHORT = {"pacific": "Pacific", "atlantic": "Atlantic", "indian": "Indian", "arctic": "Arctic",
         "southern": "Southern"}
OCOL = {"pacific": (40, 236, 226), "atlantic": (140, 236, 100), "indian": (255, 120, 196),
        "arctic": (240, 248, 255), "southern": (150, 110, 255)}
# where each ocean faces the viewer on the globe (lon, lat)
FACE = {"pacific": (-165, 2), "atlantic": (-32, 12), "indian": (78, -14), "arctic": (10, 72),
        "southern": (60, -68)}
# label spots on the globe / map
LAB = {"pacific": (-150, 5), "atlantic": (-38, 22), "indian": (78, -22), "arctic": (-10, 82),
       "southern": (40, -61)}

# Americas split line (lon by lat) between the Pacific (west) and the Atlantic (east)
_B_LAT = [-90, -56, -50, -40, -30, -20, -10, 0, 5, 10, 15, 20, 30, 40, 50, 60, 90]
_B_LON = [-67, -67, -70, -68, -65, -65, -70, -78, -77, -83, -90, -100, -100, -100, -95, -100, -100]


@lru_cache(None)
def ocean_ids(width):
    """uint8 raster (width/2 x width): 0 land/lake, 1..5 = index in OCEANS + 1."""
    arr, _ = K._raster(width, True, False)
    h = width // 2
    water = (arr == K.OCEAN) | (arr == K.WAVE)
    lake = Image.new("L", (width, h), 0)
    d = ImageDraw.Draw(lake)
    for poly in K.LAKES:
        d.polygon([K._xy(lo, la, width, h) for lo, la in poly], fill=255)
    water &= np.array(lake) == 0
    lon = ((np.arange(width) + 0.5) / width * 360 - 180)[None, :]
    lat = (90 - (np.arange(h) + 0.5) / h * 180)[:, None]
    bnd = np.interp(lat, _B_LAT, _B_LON)
    ind_e = np.interp(lat, [-90, -44, -38, -12, -9, -5, 0, 90], [147, 147, 135, 128, 120, 105, 100, 100])
    out = np.zeros((h, width), np.uint8)
    atl = (lon >= bnd) & ((lon < 20) | ((lat >= 30) & (lon < 60)))
    ind = (lat < 30) & (lon >= 20) & (lon < ind_e)
    pac = ~atl & ~ind
    out[water & pac] = 1
    out[water & atl] = 2
    out[water & ind] = 3
    out[water & (lat > 66)] = 4
    out[water & (lat < -60)] = 5
    return out


def _tint(rgb, ids, hl, t):
    """Blend ocean pixels toward their highlight colours. hl: {name: k}."""
    for name, k in hl.items():
        if k <= 0.01:
            continue
        i = OCEANS.index(name) + 1
        a = clamp(k) * (0.55 + 0.12 * math.sin(t * 4 + i))
        m = ids == i
        rgb[m] = rgb[m] * (1 - a) + np.array(OCOL[name], np.float32) * a
    return rgb


TEXW = 2048


@lru_cache(None)
def _tex():
    return K.texture("earth", TEXW, False).astype(np.float32)


def ocean_globe_image(r_ss, lon, lat, hl, t=0.0):
    """RGBA image of the Earth with some oceans tinted (hl: {name: k})."""
    rs = max(4, int(round(r_ss)))
    half = rs > 240
    rr = rs // 2 if half else rs
    tex = _tex()
    ids = ocean_ids(TEXW)
    th = tex.shape[0]
    inside, rows, lonb, latb, shade, spec = K._globe_geom(rr, round(lat, 1), 0.0, th)
    glon = lonb + lon
    cols = ((glon + 540.0) * (TEXW / 360.0)).astype(np.int32) % TEXW
    rgb = tex[rows, cols].copy()
    rgb = _tint(rgb, ids[rows, cols], hl, t)
    rgb *= shade[:, None]
    rgb += spec[:, None]
    np.clip(rgb, 0, 255, out=rgb)
    out = np.zeros((2 * rr, 2 * rr, 4), np.uint8)
    out[inside, :3] = rgb.astype(np.uint8)
    out[inside, 3] = 255
    img = Image.fromarray(out, "RGBA")
    if half:
        img = img.resize((2 * rs, 2 * rs), Image.BILINEAR)
    return img


def ocean_globe(c, x, y, r, lon=0.0, lat=10.0, hl=None, t=0.0, glow=0.0):
    if glow > 0.01:
        K._halo(c, x, y, r, glow, (200, 236, 255))
    img = ocean_globe_image(r * c.scale * SS, lon, lat, hl or {}, t)
    px, py = c.P(x, y)
    c.img.paste(img, (int(round(px - img.size[0] / 2)), int(round(py - img.size[1] / 2))), img)
    c.circle(x, y, r, None, ol=OUT, w=LW + 1)


@lru_cache(None)
def _ocean_mask(i):
    """L mask (SS px per map unit) of ocean i (1..5) for the flat map."""
    ids = ocean_ids(K.MW * SS * 2)
    m = Image.fromarray(((ids == i) * 255).astype(np.uint8), "L")
    return m.reduce(2)


def ocean_highlight(c, v, name, k=1.0, t=0.0):
    """Tint one ocean on the magic map (like K.map_highlight, but for oceans)."""
    if k <= 0.01:
        return
    i = OCEANS.index(name) + 1
    mask = _ocean_mask(i)
    x0, y0, x1, y1 = v.rect()
    sx0, sy0 = max(0, int(x0 * SS)), max(0, int(y0 * SS))
    sx1, sy1 = min(W * SS, int(x1 * SS)), min(H * SS, int(y1 * SS))
    if sx1 - sx0 < 2 or sy1 - sy0 < 2:
        return
    mx0, my0 = v.cx + (sx0 / SS - W / 2) / v.z, v.cy + (sy0 / SS - H / 2) / v.z
    mx1, my1 = v.cx + (sx1 / SS - W / 2) / v.z, v.cy + (sy1 / SS - H / 2) / v.z
    piece = mask.resize((sx1 - sx0, sy1 - sy0), Image.BILINEAR, box=(mx0 * SS, my0 * SS, mx1 * SS, my1 * SS))
    a = clamp(k) * (0.5 + 0.1 * math.sin(t * 4 + i))
    piece = piece.point(lambda q: int(q * a))
    c.img.paste(OCOL[name], (sx0, sy0, sx1, sy1), piece)


@lru_cache(None)
def tinted_map():
    """The flat 'earth' map (level 1) with all five oceans tinted (for the globe -> map morph)."""
    img = K.map_image("earth", 1).copy()
    for i, name in enumerate(OCEANS):
        m = _ocean_mask(i + 1).resize(img.size).point(lambda q: int(q * 0.55))
        img.paste(OCOL[name], (0, 0, img.size[0], img.size[1]), m)
    return img


def globe_to_map(c, k, r=230, lon=0.0, t=0.0):
    """Like K.globe_to_map, with all five oceans tinted on both the globe and the map."""
    e = ease(k)
    gw, gh = lerp(2 * r, K.MW, e), lerp(2 * r, K.MH, e)
    rad = lerp(r, 6, ease(clamp(k * 1.4)))
    x0, y0 = W / 2 - gw / 2, H / 2 - gh / 2
    ww, hh = max(4, int(gw * SS)), max(4, int(gh * SS))
    m = tinted_map().resize((ww, hh), Image.BILINEAR)
    if e < 0.999:
        hl = {n: 1.0 for n in OCEANS}
        g = ocean_globe_image(r * SS, lon, 0.0, hl, t).convert("RGB").resize((ww, hh), Image.BILINEAR)
        img = Image.blend(g, m, clamp((e - 0.15) / 0.6))
    else:
        img = m
    mask = Image.new("L", (ww, hh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, ww - 1, hh - 1], radius=rad * SS, fill=255)
    c.rect(x0 + 10, y0 + 12, x0 + gw + 10, y0 + gh + 12, (12, 12, 34), ol=None, r=rad)
    c.img.paste(img, (int(x0 * SS), int(y0 * SS)), mask)
    c.rect(x0, y0, x0 + gw, y0 + gh, None, ol=OUT, w=4, r=rad)


# ============================================================================== Bluebell

BODY = (92, 128, 178)
BODY_D = (70, 100, 148)
BELLY = (176, 200, 226)
MOTTLE = (128, 160, 204)

_TOP = [(312, 4), (304, -26), (270, -52), (190, -70), (70, -78), (-50, -72), (-150, -56), (-230, -36),
        (-290, -18), (-334, -8)]
_BOT = [(-334, 8), (-292, 14), (-220, 32), (-120, 56), (0, 72), (110, 80), (196, 72), (258, 50), (300, 24)]


def whale(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), swim=1.0, seed=3.0):
    """Bluebell, a blue whale seen from the side, facing right (face=1). (x, y) = body centre.
    Nose at about +312*s, tail flukes at about -420*s, back top at -78*s, belly at +80*s."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    wv = math.sin(t * 1.6) * swim
    # flukes (behind the body)
    fa = 0.35 * wv
    def rot(px, py, a=fa, ox=-326, oy=0):
        px, py = px - ox, py - oy
        return ox + px * math.cos(a) - py * math.sin(a), oy + px * math.sin(a) + py * math.cos(a)
    fl = [(-322, -6), (-372, -40), (-418, -64), (-424, -50), (-400, -18), (-388, 0), (-400, 18), (-424, 50),
          (-418, 64), (-372, 40), (-322, 6)]
    c.poly([rot(*p) for p in fl], BODY_D)
    # far flipper
    c.poly([(70, 52), (40, 92 + 6 * wv), (14, 98 + 6 * wv), (36, 58)], BODY_D, w=2.5)
    # body
    body = _TOP + _BOT
    c.poly(body, BODY)
    # pale belly with throat pleats
    belly = [(-40, 66), (0, 72), (110, 80), (196, 72), (258, 50), (300, 24), (306, 14), (250, 30), (180, 44),
             (100, 50), (20, 54)]
    c.poly(belly, BELLY, ol=None)
    for k in range(4):
        f = k / 4
        pts = [(lerp(-10, 40, f) + 40 * j, lerp(58, 74, f) + j * lerp(-1.5, 1.2, f) * 4) for j in range(7)]
        c.line(pts, mix(BELLY, BODY_D, 0.45), 2)
    # mottles on the back
    rng = np.random.default_rng(int(seed * 10))
    for _ in range(9):
        mx, my = rng.uniform(-260, 160), rng.uniform(-60, -20)
        c.ellipse(mx, my, rng.uniform(8, 16), rng.uniform(4, 7), MOTTLE, ol=None)
    # dorsal fin
    c.poly([(-226, -32), (-196, -58), (-176, -44), (-186, -40)], BODY_D, w=2.5)
    # mouth (long curving line; opens by dropping the lower jaw)
    jaw = 18 * clamp(mouth)
    if jaw > 1:
        c.poly([(306, 10), (250, 22), (180, 28), (250, 22 + jaw), (300, 14 + jaw * 0.6)], (120, 50, 70), w=2.5)
        c.ellipse(262, 22 + jaw * 0.5, 16, jaw * 0.35, (230, 120, 140), ol=None)
    c.line([(308, 8), (270, 18), (220, 24), (176, 26), (160, 22)], OUT, 3)
    # cheek blush
    c.ellipse(178, 40, 16, 8, (210, 150, 190), ol=None)
    # eye
    ex, ey = 160, 6
    if eyes == "closed":
        c.arc(ex, ey, 10, 7, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(ex, ey + 4, 10, 9, 200, 340, OUT, 3)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 11 * big, 12 * big, (255, 255, 255), w=2.5)
        c.ellipse(ex + 2 + look[0] * 3, ey + 1 + look[1] * 3, 5.5, 7, (30, 30, 50), ol=None)
        c.circle(ex + 4 + look[0] * 3, ey - 2, 2, (255, 255, 255), ol=None)
    for k in range(3):                                     # lashes
        a = math.radians(-120 + k * 30)
        c.line([(ex + math.cos(a) * 12, ey + math.sin(a) * 13), (ex + math.cos(a) * 18, ey + math.sin(a) * 19)],
               OUT, 2)
    # blowhole
    c.ellipse(214, -66, 9, 3, BODY_D, ol=OUT, w=2)
    # near flipper
    c.poly([(120, 46), (84, 100 + 8 * wv), (58, 108 + 8 * wv), (86, 54)], BODY, w=2.5)
    c.pop()


def blowhole(x, y, s, face):
    return x + face * 214 * s, y - 66 * s


def spout(c, x, y, k, s=1.0, t=0.0):
    """Water spray shooting up from the blowhole at (x, y); k 0..1 is the life of the spout."""
    if k <= 0.01 or k >= 0.99:
        return
    grow = ease(clamp(k * 3))
    fade = 1 - clamp((k - 0.55) / 0.45)
    h = 190 * s * grow
    col = mix((170, 214, 245), (245, 250, 255), fade)
    if fade > 0.3:
        c.poly([(x - 7 * s, y), (x - 16 * s, y - h * 0.7), (x + 16 * s, y - h * 0.7), (x + 7 * s, y)], col, w=2)
    top = y - h * 0.78 + (1 - fade) * 40 * s
    for dx, dy, r in ((-34, 6, 26), (34, 6, 26), (-14, -14, 30), (16, -16, 30), (0, 10, 28)):
        rr = r * s * grow * (0.6 + 0.4 * fade)
        if rr > 1:
            c.circle(x + dx * s * (1 + (1 - fade) * 0.8), top + dy * s, rr, col, w=2)
    rng = np.random.default_rng(3)
    for i in range(10):
        side = -1 if i % 2 else 1
        u = clamp(k * 1.4 - 0.2 + rng.uniform(-0.1, 0.1))
        dx = side * (40 + rng.uniform(0, 50)) * s * u
        dy = -h * 0.75 + (h * 0.9) * u * u
        c.circle(x + dx, y + dy, 5 * s, col, w=1.5)


# ================================================================================ Nipper

CRAB = (232, 94, 70)
CRAB_D = (190, 66, 50)
CRAB_L = (252, 150, 120)


def crab(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", snip=0.0, walk=0.0, seed=5.0):
    """Nipper the crab, front-ish view. (x, y) = feet on the ground; about 120*s tall with eyes."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    bob = abs(math.sin(walk * 2)) * 4
    # legs
    for side in (-1, 1):
        for k in range(3):
            ph = math.sin(walk * 3 + k + side) * 6
            bx, by = side * (34 + 6 * k), -30 + 8 * k
            c.stroke([(bx, by - bob), (side * (62 + 10 * k), -38 + 8 * k + ph - bob), (side * (70 + 12 * k), -4)],
                     CRAB_D, 7)
    # body
    c.ellipse(0, -40 - bob, 58, 32, CRAB)
    c.ellipse(-10, -50 - bob, 30, 12, CRAB_L, ol=None)
    for k in (-1, 0, 1):
        c.circle(k * 22, -56 - bob + abs(k) * 6, 3, CRAB_D, ol=None)
    # eye stalks
    for side in (-1, 1):
        ex, ey = side * 18, -96 - bob
        c.stroke([(side * 14, -64 - bob), (ex, ey + 8)], CRAB_D, 6)
        if eyes == "closed":
            c.circle(ex, ey, 11, CRAB_L, w=2.5)
            c.arc(ex, ey, 7, 5, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.circle(ex, ey, 11, CRAB_L, w=2.5)
            c.arc(ex, ey + 3, 7, 6, 200, 340, OUT, 2.5)
        else:
            c.circle(ex, ey, 11, (255, 255, 255), w=2.5)
            c.circle(ex + 2, ey + 1, 5, (30, 24, 30), ol=None)
            c.circle(ex + 3.5, ey - 1, 1.6, (255, 255, 255), ol=None)
    # mouth
    if mouth > 0.05:
        c.ellipse(0, -34 - bob, 9, 3 + 7 * mouth, D.MOUTH, w=2)
    else:
        c.arc(0, -38 - bob, 12, 8, 20, 160, OUT, 2.5)
    # claws
    op = 0.25 + 0.45 * clamp(snip)
    for side in (-1, 1):
        ax, ay = side * 56, -50 - bob
        cx_, cy_ = side * 86, -84 - bob
        c.stroke([(ax, ay), (side * 78, -62 - bob), (cx_, cy_ + 14)], CRAB_D, 9)
        c.push(cx_, cy_, 1.0)
        a0 = -math.pi / 2 - side * 0.2
        up = [(math.cos(a0 - side * op) * r, math.sin(a0 - side * op) * r) for r in (0, 30)]
        lo = [(math.cos(a0 + side * op) * r, math.sin(a0 + side * op) * r) for r in (0, 26)]
        c.poly([(0, 6), (side * -14, -2), up[1], (side * 6, -4)], CRAB, w=2.5)
        c.poly([(0, 6), (side * 12, 0), lo[1], (side * 2, -6)], CRAB_L, w=2.5)
        c.circle(0, 6, 14, CRAB, w=2.5)
        c.pop()
    c.pop()


# =========================================================================== deep things

def fish(c, x, y, s=1.0, face=1, t=0.0, col=(255, 190, 80), stripe=(255, 255, 255)):
    c.push(x, y, s, flip=face < 0)
    w = math.sin(t * 9) * 5
    c.poly([(-24, 0), (-42, -14 + w), (-40, 14 + w)], mix(col, (0, 0, 0), 0.15), w=2)
    c.ellipse(0, 0, 28, 16, col, w=2.5)
    c.line([(-4, -14), (-4, 14)], stripe, 4, cap=False)
    c.circle(14, -3, 4, (255, 255, 255), w=1.5)
    c.circle(15, -3, 2, (20, 20, 30), ol=None)
    c.pop()


def jelly(c, x, y, s=1.0, t=0.0, col=(240, 160, 220)):
    c.push(x, y, s)
    pulse = 1 + 0.08 * math.sin(t * 3)
    for k in range(5):
        dx = -20 + 10 * k
        pts = [(dx + 6 * math.sin(t * 3 + j * 0.8 + k), 4 + j * 12) for j in range(6)]
        c.line(pts, mix(col, (255, 255, 255), 0.3), 3)
    c.poly([(-32 * pulse, 6)] + [(math.cos(a) * 32 * pulse, -math.sin(a) * 30 / pulse + 6)
                                  for a in np.linspace(0, math.pi, 16)] + [(32 * pulse, 6)], col, w=2.5)
    c.ellipse(-10, -10, 8, 5, mix(col, (255, 255, 255), 0.6), ol=None)
    c.pop()


def angler(c, x, y, s=1.0, face=1, t=0.0, lamp=1.0):
    """A friendly deep-sea anglerfish with its glowing lamp."""
    c.push(x, y, s, flip=face < 0)
    lx, ly = 70 + 4 * math.sin(t * 2), -78 + 4 * math.cos(t * 2.3)
    if lamp > 0.01:
        c.glow(lx, ly, 90 * lamp, 90 * lamp, (255, 250, 190), (14, 26, 60), steps=8)
    body = (70, 66, 110)
    c.poly([(-50, 0), (-82, -24), (-78, 24)], mix(body, (0, 0, 0), 0.2), w=2.5)
    c.ellipse(0, 0, 56, 44, body, w=3)
    c.stroke([(20, -38), (40, -80), (lx - 6, ly + 2)], body, 4)
    c.circle(lx, ly, 9, mix((255, 240, 150), (255, 255, 230), lamp), w=2)
    # big grin with tiny teeth
    c.poly([(54, 4), (20, 26), (50, 24)], (40, 20, 40), w=2)
    for k in range(3):
        c.poly([(24 + 9 * k, 24 - k), (28 + 9 * k, 17 - k), (32 + 9 * k, 23 - k)], (255, 255, 255), ol=None)
    c.circle(26, -12, 10, (255, 255, 255), w=2)
    c.circle(29, -12, 5, (20, 20, 30), ol=None)
    c.circle(31, -14, 1.6, (255, 255, 255), ol=None)
    c.pop()


def magic_bubble(c, x, y, r, t=0.0, k=1.0):
    """A shimmering see-through bubble outline around the friends."""
    if k <= 0.01:
        return
    r = r * K.pop(k)
    c.circle(x, y, r, None, ol=(220, 244, 255), w=5)
    c.circle(x, y, r + 3, None, ol=(120, 180, 230), w=2)
    c.arc(x, y, r * 0.8, r * 0.8, 200, 250, (255, 255, 255), 6)
    c.circle(x + r * 0.45, y - r * 0.55, 6, (255, 255, 255), ol=None)
    K.sparkles(c, x, y, r, t, 5, k, seed=13, col=(220, 244, 255))


def rays(c, x0, top, bottom, t, k=1.0, col=(200, 236, 255)):
    """Soft sunlight shafts from the surface (drawn as pale stripes blended in)."""
    if k <= 0.01:
        return
    m = Image.new("L", c.img.size, 0)
    d = ImageDraw.Draw(m)
    for i in range(6):
        x = (x0 + i * 230 + 40 * math.sin(t * 0.4 + i)) * SS
        w = (40 + 20 * (i % 3)) * SS
        d.polygon([(x, top * SS), (x + w, top * SS), (x + w * 3 + 160 * SS, bottom * SS),
                   (x + 160 * SS, bottom * SS)], fill=int(40 * k))
    c.img.paste(col, (0, 0, c.img.size[0], c.img.size[1]), m)


# ============================================================================== diagrams

ROCK = (150, 140, 136)
ROCK_D = (118, 108, 104)
SEA = (64, 146, 222)
SEA_D = (40, 108, 186)
SALT = (255, 255, 255)


def salt_diagram(ic, t, k1, k2):
    """Rock -> rain -> river carries salt -> sea; the sun lifts the water up, the salt stays."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 205, 250)), (1, (226, 242, 255))]), (0, 0))
    gy = h - 70
    # sea on the right
    ic.poly([(w * 0.56, gy + 6), (w, gy - 4), (w, h), (w * 0.5, h)], SEA, w=3)
    for j in range(3):
        xx = w * 0.62 + j * 60
        ic.arc(xx, gy + 20, 12, 5, 200, 340, (200, 230, 255), 3)
    # ground + rocky mountain on the left
    ic.poly([(0, gy - 10), (w * 0.56, gy + 8), (w * 0.5, h), (0, h)], (140, 196, 104), w=3)
    ic.poly([(10, gy), (80, gy - 150), (120, gy - 120), (170, gy - 190), (250, gy - 30), (260, gy)], ROCK, w=3)
    ic.poly([(150, gy - 162), (170, gy - 190), (190, gy - 152), (176, gy - 158)], (250, 250, 255), w=2)
    for px, py in ((60, gy - 60), (120, gy - 80), (180, gy - 100), (200, gy - 50), (90, gy - 30)):
        ic.circle(px, py, 4, ROCK_D, ol=None)
    # river from the mountain to the sea
    riv = [(150, gy - 40), (190, gy - 10), (250, gy + 2), (320, gy - 2), (380, gy + 8), (w * 0.58, gy + 10)]
    ic.line(riv, (40, 110, 190), 16)
    ic.line(riv, (110, 180, 240), 10)
    # rain cloud over the mountain
    D.cloud(ic, 140, 54, 0.62, col=(214, 222, 236))
    if k1 > 0.01:
        for i in range(10):
            u = (t * 1.4 + i / 10) % 1
            rx = 92 + (i * 37) % 110
            ry = 74 + u * 90
            ic.line([(rx, ry), (rx - 3, ry + 10)], (70, 130, 220), 3)
        # salt bits riding the river
        sp = K.spline(riv, 10)
        for i in range(9):
            u = (t * 0.25 + i / 9) % 1
            if u > k1 * 1.2:
                continue
            p = sp[int(u * (len(sp) - 1))]
            ic.rect(p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4, SALT, w=1.5)
        K.text(ic, 130, gy - 210 + 4, "salt in rocks", 22, (70, 60, 70), stroke=2, stroke_fill=(255, 255, 255))
        K.text(ic, 300, gy + 36, "river", 24, (30, 90, 170), stroke=2, stroke_fill=(255, 255, 255))
    # salt collecting in the sea
    rng = np.random.default_rng(4)
    n = int(18 * clamp(k1 * 1.3 + k2))
    for i in range(n):
        sx, sy = rng.uniform(w * 0.6, w - 20), rng.uniform(gy + 12, h - 12)
        ic.rect(sx - 4, sy - 4, sx + 4, sy + 4, SALT, w=1.5)
    if k1 > 0.3:
        K.text(ic, w * 0.8, h - 26, "salty sea", 26, (255, 255, 255), stroke=3, stroke_fill=SEA_D)
    # sun lifts the water up; the salt stays
    if k2 > 0.01:
        sx, sy = w - 70, 56
        ic.circle(sx, sy, 32 * K.pop(k2), (255, 220, 90), w=3)
        for i in range(3):
            u = (t * 0.6 + i / 3) % 1
            bx = w * 0.66 + i * 70
            by = gy - 10 - u * 120
            pts = [(bx + 8 * math.sin(j * 1.3 + t * 3), by - j * 8) for j in range(6)]
            ic.line(pts, (90, 160, 236), 4)
            ic.poly([(bx - 8, by - 44), (bx + 8, by - 44), (bx + 8 * math.sin(t * 3), by - 58)], (90, 160, 236),
                    w=1.5)
        D.cloud(ic, w * 0.74, 60, 0.45 * clamp(k2 * 2))
        if k2 > 0.4:
            K.label(ic, w * 0.56, 128, "water goes up", 22, k=clamp((k2 - 0.4) * 3), col=(30, 90, 170))
        if k2 > 0.7:
            K.label(ic, w * 0.82, gy - 26, "salt stays!", 24, k=clamp((k2 - 0.7) * 4), col=(200, 50, 60))


def wind_diagram(ic, t, k):
    """Wind blows over the water and pushes it into bumps (waves)."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (160, 210, 250)), (1, (226, 242, 255))]), (0, 0))
    wy = h * 0.62
    amp = 4 + 26 * ease(k)
    pts = [(x, wy - amp * max(0, math.sin(x * 0.045 - t * 3)) ** 1.5 * clamp(x / (w * 0.4) + 0.1))
           for x in np.linspace(0, w, 80)]
    ic.poly(pts + [(w, h), (0, h)], SEA, w=3)
    for x in range(40, int(w), 90):
        ic.arc(x + (t * 30) % 90, wy + 30, 14, 5, 200, 340, (200, 230, 255), 3)
    # puffing wind cloud with a face
    cx, cy = 70, 64
    D.cloud(ic, cx, cy, 0.5)
    ic.circle(cx + 6, cy - 4, 3, OUT, ol=None)
    ic.circle(cx + 24, cy - 4, 3, OUT, ol=None)
    ic.circle(cx + 36, cy + 8, 6, D.MOUTH, w=2)
    # wind arrows
    for i in range(3):
        u = (t * 0.8 + i / 3) % 1
        x0 = 120 + u * (w - 260)
        y0 = 70 + i * 34 + 20 * u
        K.arrow(ic, x0, y0, x0 + 110, y0 + 14, (255, 255, 255), 6, 1.0, head=16)
    K.text(ic, w / 2 + 40, 40, "wind", 30, (60, 90, 140), stroke=2, stroke_fill=(255, 255, 255))
    if k > 0.5:
        K.label(ic, w * 0.72, wy - 70, "waves!", 26, k=clamp((k - 0.5) * 3), col=(30, 90, 170))


def trench_diagram(ic, t, k):
    """The tallest mountain would fit inside the deepest part of the Pacific, with water above it."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    surf = 46
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (170, 220, 255)), (surf / h, (170, 220, 255)),
                                                       (surf / h + 0.01, (60, 140, 214)), (1, (14, 30, 80))]), (0, 0))
    ic.line([(0, surf), (w, surf)], (230, 246, 255), 3, cap=False)
    floor = h - 70
    tx = w * 0.5
    sea_floor = [(0, surf + 110), (tx - 90, surf + 120), (tx - 30, h - 12), (tx + 30, h - 12), (tx + 90, surf + 120),
                 (w, surf + 110), (w, h), (0, h)]
    ic.poly(sea_floor, (120, 100, 90), w=3)
    # the mountain drops into the trench
    mh = (h - 12 - surf) * 0.8
    my = lerp(-mh - 40, h - 12, ease(k))
    mw = 70
    ic.poly([(tx - mw, my), (tx - 16, my - mh * 0.8), (tx, my - mh), (tx + 20, my - mh * 0.85), (tx + mw, my)],
            (150, 140, 136), w=3)
    ic.poly([(tx - 16, my - mh * 0.8), (tx, my - mh), (tx + 20, my - mh * 0.85), (tx + 8, my - mh * 0.8),
             (tx - 4, my - mh * 0.86)], (250, 250, 255), w=2)
    if k > 0.9:
        K.label(ic, tx + 170, my - mh - 6, "tallest mountain", 22, tip=(tx + 14, my - mh), k=clamp((k - 0.9) * 10))
        K.label(ic, tx - 160, h - 40, "deepest sea", 22, tip=(tx - 34, h - 22), k=clamp((k - 0.9) * 10),
                col=(30, 60, 140))
        # the peak is still under water
        for kk in range(4):
            yy = lerp(my - mh - 6, surf + 6, kk / 3)
            ic.circle(tx + 4 * math.sin(t * 3 + kk), yy, 3 + kk, (220, 240, 255), w=1.5)


def tide_diagram(ic, t, k):
    """The Moon pulls the sea: the water around the Earth stretches toward the Moon."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    ex, ey, r = w * 0.32, h / 2 - 6, 70
    st = 1 + 0.32 * ease(k) + 0.03 * math.sin(t * 3) * k
    ic.ellipse(ex + 4 * k, ey, (r + 18) * st, (r + 18) / (1 + 0.1 * k), (90, 170, 240), ol=(40, 100, 180), w=3)
    K.globe(ic, ex, ey, r, lon=-t * 25, lat=20)
    mx, my = w - 80, h / 2 - 6
    D.moon(ic, mx, my, 34, sky=(30, 30, 70))
    if k > 0.2:
        bx = ex + (r + 18) * st + 4 * k
        for i, dy in enumerate((-34, 0, 34)):
            u = (t * 0.8 + i / 3) % 1
            K.arrow(ic, bx + 10, ey + dy * 0.6, bx + 46 + 14 * u, ey + dy * 0.6, (255, 236, 110), 5,
                    clamp((k - 0.2) * 3), head=12)
        K.text(ic, bx + 40, ey - 52, "pull!", 24, (255, 236, 110), stroke=3)
    K.text(ic, mx, my + 56, "Moon", 24, (255, 255, 255), stroke=3)
    K.text(ic, ex, h - 22, "Earth", 24, (255, 255, 255), stroke=3)


# ================================================================================ icons

def icon_five(c, x, y, r, t=0.0):
    """Five little ocean drops around a big 5."""
    for i, name in enumerate(OCEANS):
        a = -math.pi / 2 + i * math.tau / 5 + t * 0.4
        px, py = x + math.cos(a) * r * 0.66, y + math.sin(a) * r * 0.66
        rr = r * 0.26
        c.poly([(px, py - rr * 1.5), (px + rr * 0.9, py), (px, py + rr), (px - rr * 0.9, py)], OCOL[name], w=2)
        c.circle(px, py + rr * 0.15, rr * 0.86, OCOL[name], ol=None)
    K.text(c, x, y + 2, "5", r * 0.8, (40, 100, 190), stroke=3, stroke_fill=(255, 255, 255))


def icon_pacific(c, x, y, r, t=0.0):
    ocean_globe(c, x, y, r * 0.95, FACE["pacific"][0] - t * 10, 5, {"pacific": 1.0}, t)


def icon_atlantic(c, x, y, r, t=0.0):
    ocean_globe(c, x, y, r * 0.95, FACE["atlantic"][0] - t * 10, 10, {"atlantic": 1.0}, t)


def icon_salt(c, x, y, r, t=0.0):
    """A salt shaker sprinkling salt over a little wave."""
    c.ellipse(x, y + r * 0.6, r * 0.95, r * 0.32, SEA, w=2.5)
    c.arc(x - r * 0.3, y + r * 0.55, r * 0.2, r * 0.08, 200, 340, (220, 240, 255), 3)
    c.arc(x + r * 0.3, y + r * 0.62, r * 0.2, r * 0.08, 200, 340, (220, 240, 255), 3)
    c.push(x + r * 0.18, y - r * 0.32, 1.0)
    sw = r * 0.34
    c.rect(-sw, -r * 0.5, sw, r * 0.5, (245, 248, 252), r=sw * 0.6, w=2.5)
    c.rect(-sw * 0.9, -r * 0.62, sw * 0.9, -r * 0.4, (190, 196, 210), r=sw * 0.3, w=2.5)
    for dx in (-0.4, 0, 0.4):
        c.circle(dx * sw, -r * 0.52, 1.8, OUT, ol=None)
    K.text(c, 0, 4, "S", r * 0.4, (90, 100, 130))
    c.pop()
    for i in range(5):
        u = (t * 1.3 + i / 5) % 1
        c.rect(x - r * 0.25 + i * r * 0.07 - 3, y - r * 0.1 + u * r * 0.55 - 3, x - r * 0.25 + i * r * 0.07 + 3,
               y - r * 0.1 + u * r * 0.55 + 3, SALT, w=1)


def icon_sweet(c, x, y, r, t=0.0):
    """A big swirly lollipop."""
    c.line([(x + r * 0.1, y + r * 0.1), (x + r * 0.55, y + r * 0.9)], (250, 250, 250), 7)
    c.circle(x - r * 0.1, y - r * 0.15, r * 0.62, (255, 130, 170), w=3)
    pts = []
    for i in range(60):
        a = i * 0.32
        rr = r * 0.56 * i / 60
        pts.append((x - r * 0.1 + math.cos(a) * rr, y - r * 0.15 + math.sin(a) * rr))
    c.line(pts, (255, 255, 255), 5)


def bowl(c, x, y, s=1.0, full=1.0):
    c.push(x, y, s)
    c.ellipse(0, -4, 44, 12, (90, 150, 220), w=2.5)
    c.poly([(-46, -8), (46, -8), (36, 14), (-36, 14)], (90, 150, 220), w=2.5)
    if full > 0.05:
        c.ellipse(0, -8, 38 * full + 2, 7 * full + 1, (170, 214, 250), ol=None)
    K.text(c, 0, 4, "W", 16, (255, 255, 255))
    c.pop()
