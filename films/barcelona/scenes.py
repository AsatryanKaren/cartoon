"""Scenes of "Whiskers and the Mosaic Bowl". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
Static backgrounds are drawn once and cached; wide ones are panned with a camera.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.barcelona import props as P
from films.moonfish.scenes import room as home_room

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "paco": 3.7, "marina": 5.5}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def view(bg, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    return Canvas(bg.crop((x, y, x + W * SS, y + H * SS)))


def track(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def speed(t, keys):
    return (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1


def arc_y(u, h):
    return -4 * h * u * (1 - u)


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="sit", pal=None, walk=0.0, bundle=False, **kw):
    """Whiskers or Luna; mouth from the voice track unless given."""
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, pal or PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if bundle:
        hx, hy = P.head_pos(pose, walk, kw.get("head_dy", 0.0))
        c.push(x, y, s, flip=face < 0)
        if pose == "sit":
            P.bundle(c, -34, -40, 0.75)
        elif pose in ("stand", "walk"):
            P.bundle(c, -16, -66, 0.75)
        c.pop()


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """Moves a character along x keys; walks while moving and faces the way it goes."""
    x = smooth(t, keys)
    v = speed(t, keys)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "marina":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        P.marina(c, x, y, s, face, t, mouth=mouth, walk=x / (8 * s) if moving else 0.0, **kw)
    elif who == "paco":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        if moving:
            pose = "walk"
        P.paco(c, x, y, s, face, pose, t=t, mouth=mouth, walk=x / (12 * s) if moving else 0.0, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def notes(c, x, y, t, n=4, col=(255, 250, 230)):
    """Little music notes floating up from a guitar."""
    for k in range(n):
        u = (t * 0.45 + k / n) % 1.0
        nx = x + 40 * math.sin(t * 1.5 + k * 2) + 30 * u
        ny = y - 140 * u
        a = 1 - u
        cc = mix((60, 40, 50), col, a)
        c.circle(nx, ny, 6, cc, ol=None)
        c.line([(nx + 5, ny), (nx + 5, ny - 22)], cc, 2.5, cap=False)
        if k % 2:
            c.line([(nx + 5, ny - 22), (nx + 14, ny - 16)], cc, 2.5, cap=False)


def sparkle_star(c, x, y, r, col=(255, 250, 210)):
    if r <= 0.5:
        return
    c.poly([(x, y - r), (x + r * 0.25, y - r * 0.25), (x + r, y), (x + r * 0.25, y + r * 0.25), (x, y + r),
            (x - r * 0.25, y + r * 0.25), (x - r, y), (x - r * 0.25, y - r * 0.25)], col, ol=None)


def hearts(c, x, y, t, n=3):
    for k in range(n):
        u = (t * 0.5 + k / n) % 1.0
        hx = x + 20 * math.sin(t * 2 + k * 2)
        hy = y - 70 * u
        r = 7 * (1 - u * 0.5)
        col = mix((240, 90, 110), (250, 228, 190), u * u)
        c.circle(hx - r * 0.55, hy, r * 0.6, col, ol=None)
        c.circle(hx + r * 0.55, hy, r * 0.6, col, ol=None)
        c.poly([(hx - r * 1.1, hy + r * 0.1), (hx + r * 1.1, hy + r * 0.1), (hx, hy + r * 1.3)], col, ol=None)


def choc_moustache(c, x, y, s, face, pose="sit", head_dy=0.0):
    hx, hy = P.head_pos(pose, 0, head_dy)
    c.push(x, y, s, flip=face < 0)
    brown = (110, 62, 40)
    c.ellipse(hx + 9, hy + 13, 9, 4.5, brown, ol=None)
    c.ellipse(hx + 25, hy + 13, 9, 4.5, brown, ol=None)
    c.circle(hx + 1, hy + 10, 3.5, brown, ol=None)
    c.circle(hx + 33, hy + 10, 3.5, brown, ol=None)
    c.pop()


# =================================================================== title

def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (38, 46, 110)), (0.28, (130, 86, 150)), (0.5, (240, 140, 120)),
                                               (0.61, (255, 196, 130)), (1, (255, 196, 130))]))
        D.stars(c, 6, 30, W, 120, col=(255, 240, 220))
        c.glow(880, 430, 360, 220, (255, 226, 170), (246, 160, 124), steps=12)
        c.circle(880, 432, 62, (255, 226, 130), ol=None)
        c.circle(880, 432, 52, (255, 240, 180), ol=None)
        # skyline silhouette, warmed by the sunset
        c.tint = ((120, 70, 120), 0.5)
        c.poly([(-40, 442), (60, 380), (170, 352), (280, 364), (400, 442)], (90, 130, 90), w=2.5)
        c.rect(150, 334, 210, 356, (190, 170, 140), w=2)
        rng = np.random.default_rng(5)
        x = 380
        while x < W:
            w = rng.uniform(30, 70)
            h = rng.uniform(16, 52)
            c.rect(x, 442 - h, x + w, 442, mix((220, 190, 170), (180, 150, 160), rng.uniform()), w=1.5)
            x += w + rng.uniform(-6, 4)
        P.hotel_sail(c, 330, 442, 0.42)
        P.glories(c, 720, 442, 0.4)
        P.sagrada(c, 1070, 442, 0.3, detail=False)
        P.crane(c, 1170, 442, 250, jib=90, counter=30)
        c.tint = None
        # sea
        sea = D.gradient(W * SS, 170 * SS, [(0, (230, 150, 140)), (0.3, (150, 100, 140)), (1, (60, 56, 110))])
        c.img.paste(sea, (0, 442 * SS))
        for k in range(14):
            y = 450 + k * 9
            wdt = 60 - 3 * k
            c.rect(880 - wdt, y, 880 + wdt, y + 2.5, (255, 220, 150), ol=None)
        # beach
        c.poly([(0, 600), (300, 590), (700, 606), (1000, 594), (W, 604), (W, H), (0, H)], (226, 168, 128), ol=None)
        c.poly([(0, 660), (500, 650), (W, 664), (W, H), (0, H)], (210, 150, 120), ol=None)
        c.tint = ((120, 60, 90), 0.25)
        P.fishing_boat(c, 190, 640, 1.0, col=(40, 120, 190), face=1)
        P.palm(c, 1170, 716, 1.25, lean=-0.18)
        P.palm(c, 1250, 724, 1.0, lean=-0.05)
        c.tint = None
        return c.img
    return cached("title", make)


def tile_title(c, cx, y, text, size, k):
    """Big title in multicoloured mosaic letters."""
    f = D.font(size)
    widths = [f.getlength(ch) / SS for ch in text]
    total = sum(widths)
    x = cx - total / 2
    for i, (ch, wd) in enumerate(zip(text, widths)):
        if ch != " ":
            col = P.TILE_COLS[(i * 3) % 6]
            c.text(x + wd / 2, y, ch, size, mix((40, 46, 110), col, k), stroke=5 * k, stroke_fill=(50, 30, 60))
        x += wd


def title(tl, t):
    c = Canvas(title_bg().copy())
    # glitter on the sea
    rng = np.random.default_rng(int(t * 5))
    for k in range(10):
        gx = 880 + rng.uniform(-120, 120)
        gy = rng.uniform(452, 560)
        c.rect(gx - 8, gy, gx + 8, gy + 2, (255, 240, 200), ol=None)
    # little waves on the shore
    for k in range(3):
        u = (t * 0.25 + k / 3) % 1.0
        c.line([(x, 598 + 6 * u + 3 * math.sin(x / 40 + k)) for x in range(0, W + 40, 40)],
               mix((255, 240, 220), (226, 168, 128), u), 3 * (1 - u) + 1, cap=False)
    c.tint = ((110, 60, 100), 0.3)
    kat(c, tl, t, "whiskers", 470, 680, 0.78, 1, "sit", look=(1, -1))
    kat(c, tl, t, "luna", 560, 684, 0.74, 1, "sit", look=(1, -1), tail=math.sin(t * 1.5))
    c.tint = None
    mx = lerp(-100, 1400, (t / 13.0))
    P.marina(c, mx, 300 + 20 * math.sin(t * 2), 0.6, 1, t, fly=True)
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(W / 2, 80 - 30 * (1 - k), "Whiskers and the", 44, mix((40, 46, 110), (255, 246, 230), k),
           stroke=3 * k, stroke_fill=(70, 40, 80))
    k2 = ease(tl.prog("t_open", t, 0.25, 0.9))
    tile_title(c, W / 2, 160, "MOSAIC BOWL", int(28 + 56 * k2), k2)
    return finish(c, tl, t)


# ==================================================================== bowl

BX, BY = 700, 628          # the bowl on the floor
ZX, ZY, ZW = 300, 186, 944  # zoomed-in view of the room
WX = 520                   # Whiskers' spot


def butterfly_pos(tl, t):
    T = tl.t
    if t < T("b_fly"):
        return None
    u = tl.prog("b_fly", t, 0.0, 0.9)
    if t < T("b_crash", 0.3):
        x = lerp(950, BX + 10, ease(u)) + 30 * math.sin(t * 3) * (1 - u)
        y = lerp(230, BY - 64, ease(u)) + 24 * math.sin(t * 4.3) * (1 - u)
        return x, y
    v = clamp((t - T("b_crash", 0.3)) / 2.5)
    if v >= 1:
        return None
    return lerp(BX + 10, 1000, ease(v)) + 20 * math.sin(t * 5), lerp(BY - 64, 160, ease(v))


def bowl_scene(tl, t):
    T = tl.t
    c = Canvas(home_room(False).copy())
    crash_t = T("b_crash", 0.42)
    # --- the bowl, its pieces, the bundle
    if t < T("b_crash", 0.36):
        P.bowl(c, BX, BY, 1.0, "blue", food=1.0)
    elif t < crash_t:
        u = (t - T("b_crash", 0.36)) / (crash_t - T("b_crash", 0.36))
        P.bowl(c, BX + 20 * u, BY - 30 * math.sin(math.pi * u), 1.0, "blue", ang=1.4 * u)
    else:
        pack = tl.prog("b_pack", t, 0.1, 0.8)
        fly = clamp((t - crash_t) / 0.35)
        spread = (0.3 + 0.9 * ease(fly)) * (1 - 0.8 * pack)
        lift = math.sin(math.pi * fly) * 3 if fly < 1 else 0
        if pack < 1:
            P.shards(c, BX, BY - 4, 1.0, spread=spread, lift=lift)
        if pack > 0:
            P.bundle(c, BX, BY + 8, ease(pack))
    if t >= crash_t and t < crash_t + 0.4:
        k = (t - crash_t) / 0.4
        for a in range(8):
            ang = a * math.tau / 8
            r0, r1 = 40 + 60 * k, 60 + 80 * k
            c.line([(BX + math.cos(ang) * r0, BY - 20 + math.sin(ang) * r0 * 0.6),
                    (BX + math.cos(ang) * r1, BY - 20 + math.sin(ang) * r1 * 0.6)], (255, 240, 160), 4)
    # --- Whiskers
    wy = 615
    if t < T("b_crash"):
        lb = butterfly_pos(tl, t)
        look = (1, 0.6)
        if lb:
            dx, dy = lb[0] - (WX + 18), lb[1] - (wy - 106)
            L = math.hypot(dx, dy) or 1
            look = (dx / L, dy / L)
        eyes = "happy" if t < T("b_hello") and tl.mouth("whiskers", t) < 0.1 else ("wide" if lb else "open")
        kat(c, tl, t, "whiskers", WX, wy, 1.0, 1, "sit", eyes=eyes, look=look)
        if t < T("b_hello"):
            hearts(c, 600, 470, t)
    elif t < crash_t:
        u = tl.prog("b_crash", t, 0.0, 0.42)
        if u < 0.45:
            wig = math.sin(t * 30) * 4
            kat(c, tl, t, "whiskers", WX + wig * 0.3, wy, 1.0, 1, "crouch", eyes="wide", tail=math.sin(t * 25))
        else:
            v = (u - 0.45) / 0.55
            x = lerp(WX, BX - 60, v)
            y = wy + arc_y(v, 150) + lerp(0, BY - wy - 10, v)
            kat(c, tl, t, "whiskers", x, y, 1.0, 1, "leap", eyes="wide")
    else:
        v = clamp((t - crash_t) / 0.9)
        if v < 1:
            x = lerp(BX - 60, 590, v)
            y = BY - 10 + arc_y(v, 90) + lerp(0, wy - BY + 10, v)
            kat(c, tl, t, "whiskers", x, y, 1.0, -1 if v < 0.5 else 1, "stand", eyes="wide",
                squash=1 - 0.2 * math.sin(math.pi * v))
        else:
            sad = t < T("b_hola")
            eyes = "wide" if t < T("b_oh") else ("open" if t < T("b_food") else "happy")
            look = (0.6, 0.9) if sad else (1, -0.6)
            if t >= T("b_pack"):
                eyes, look = "happy", (1, 0)
            kat(c, tl, t, "whiskers", 590, wy, 1.0, 1, "sit", eyes=eyes, look=look,
                head_dy=8 if sad and t >= T("b_oh") else 0)
            if T("b_oh", 0.6) <= t < T("b_hola"):       # one tear
                u = ((t - T("b_oh", 0.6)) * 0.8) % 1.0
                c.ellipse(590 + 26, wy - 100 + 50 * u, 4, 6, (140, 200, 250), w=1.5)
    # --- Luna
    lkeys = [(T("b_sad"), 940), (T("b_sad", 1), 830)]
    lface = -1
    leyes = "open"
    if T("b_look") <= t < T("b_crash", 0.5):
        leyes = "wide"
    if T("b_food", 0.5) <= t:
        leyes = "happy"
    if t < T("b_sad") or t >= T("b_sad", 1):
        lx = 940 if t < T("b_sad") else 830
        look = (-1, -0.4) if T("b_fly") <= t < T("b_crash", 0.6) else (-1, 0.3)
        if T("b_gull") <= t:
            look = (1, -1) if t < T("b_broke") or T("b_never") <= t < T("b_food") else (-1, 0)
        if t >= T("b_pack"):
            look = (-1, 0.6)
        kat(c, tl, t, "luna", lx, 615, 1.0, lface, "sit", eyes=leyes, look=look, tail=math.sin(t * 1.5))
    else:
        actor(c, tl, t, "luna", lkeys, 615, 1.0, -1)
    # --- Marina flies in to the window sill
    if t >= T("b_gull"):
        u = tl.prog("b_gull", t, 0.0, 0.75)
        if u < 1:
            mx = lerp(1340, 1000, ease(u))
            my = lerp(140, 370, ease(u)) + arc_y(u, 40)
            P.marina(c, mx, my, 0.9, -1, t, fly=True, flap=t * 12)
        else:
            hop = 0.0
            wave = 0.0
            if t >= T("b_pack"):
                wave = abs(math.sin(t * 6))
            P.marina(c, 1000, 372 - hop, 0.9, -1, t, mouth=tl.mouth("marina", t), wave=wave,
                     eyes="happy" if T("b_secret") <= t < T("b_secret", 1) else "open")
    # --- butterfly
    b = butterfly_pos(tl, t)
    if b:
        D.butterfly(c, b[0], b[1], t, 0.8)
    c = Canvas(c.img.crop((ZX * SS, ZY * SS, (ZX + ZW) * SS, (ZY + ZW * H // W) * SS)).resize((W * SS, H * SS),
                                                                                         Image.BILINEAR))
    return finish(c, tl, t)


# ==================================================================== ship

HORIZON = 380
SHIP_X, SHIP_Y, SHIP_S = 30, 650, 0.8


def ship_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (84, 164, 232)), (HORIZON / H, (206, 232, 250)),
                                               (HORIZON / H + 0.001, (70, 150, 206)), (1, (28, 84, 156))]))
        for x, y, s in ((200, 120, 1.0), (640, 70, 0.8), (1100, 150, 1.1)):
            D.cloud(c, x, y, s)
        return c.img
    return cached("ship_bg", make)


def skyline_layer():
    """Barcelona seen from the sea, as an RGBA strip (1100 x 330), base at the bottom."""
    def make():
        w, h = 1100, 330
        c = Canvas(Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)), size=(w, h))
        c.tint = ((170, 196, 222), 0.3)
        c.poly([(-20, h), (40, h - 90), (130, h - 130), (240, h - 120), (330, h)], (110, 160, 100), w=2.5)
        c.rect(110, h - 150, 170, h - 128, (200, 180, 150), w=2)
        P.colom(c, 380, h, 0.35)
        rng = np.random.default_rng(8)
        x = 300
        while x < w:
            bw = rng.uniform(34, 70)
            bh = rng.uniform(26, 70)
            c.rect(x, h - bh, x + bw, h, mix((240, 220, 190), (230, 190, 170), rng.uniform()), w=1.5)
            for wy in range(int(h - bh + 8), h - 6, 14):
                for wx in range(int(x + 6), int(x + bw - 6), 12):
                    c.rect(wx, wy, wx + 5, wy + 6, (120, 150, 190), ol=None)
            x += bw + rng.uniform(-4, 6)
        P.sagrada(c, 640, h - 30, 0.25, detail=False)
        P.crane(c, 720, h - 30, 220, jib=70, counter=24)
        P.glories(c, 860, h, 0.55)
        P.hotel_sail(c, 1040, h, 0.5)
        for px in (420, 520, 980):
            P.palm(c, px, h, 0.3, lean=0.1)
        return c.img
    return cached("skyline", make)


def sea_waves(c, t, y0=HORIZON + 10, y1=H, v=60.0, col=(150, 200, 236)):
    rng = np.random.default_rng(2)
    k = 0
    y = y0
    while y < y1:
        depth = (y - y0) / (y1 - y0)
        sp = v * (0.3 + 1.5 * depth)
        n = 5 + int(4 * depth)
        for j in range(n):
            x = (rng.uniform(0, W + 200) - t * sp) % (W + 200) - 100
            w = 14 + 40 * depth
            c.arc(x, y, w, 5 + 4 * depth, 200, 340, mix(col, (255, 255, 255), 0.3 * depth), 2 + 2 * depth)
        y += 16 + 26 * depth
        k += 1


def dolphin_jump(c, t, x0, period, phase, s=1.0, y=670):
    p = ((t + phase) % period) / period
    if p > 0.6:
        return
    u = p / 0.6
    x = x0 + 260 * u
    yy = y - 200 * math.sin(math.pi * u)
    ang = -math.cos(math.pi * u) * 0.8
    P.dolphin(c, x, yy, s, ang=ang)
    for uu, xx in ((0.0, x0), (1.0, x0 + 260)):
        d = abs(u - uu)
        if d < 0.25:
            k = 1 - d / 0.25
            for j in range(5):
                c.circle(xx + (j - 2) * 12, y - 10 - 20 * k * (1 - abs(j - 2) / 3), 6 * k + 2, (240, 250, 255), ol=None)


def ship_scene(tl, t):
    T = tl.t
    c = Canvas(ship_bg().copy())
    # Barcelona rises on the horizon
    if t >= T("s_land"):
        u = ease(tl.prog("s_land", t, 0.0, 1.0))
        sx = lerp(1320, 380, u) - 30 * clamp((t - T("s_mira")) / 6)
        sky = skyline_layer()
        c.img.paste(sky, (int(sx * SS), int((HORIZON + 4 - 330) * SS)), sky)
        c.rect(0, HORIZON, W, HORIZON + 6, (70, 150, 206), ol=None)
    sea_waves(c, t)
    bob = 4 * math.sin(t * 1.3)
    sy = SHIP_Y + bob
    P.smoke_puffs(c, SHIP_X + 380 * SHIP_S, sy - 360 * SHIP_S, t, col=(236, 236, 240))
    P.ship(c, SHIP_X, sy, SHIP_S, t)
    deck = sy - 110 * SHIP_S
    # passengers on the bow deck
    sick = 0.0
    if T("s_sick") - 0.3 <= t:
        sick = 1 - clamp((t - T("s_land", 0.2)) / 1.5)
    wpal = P.tinted(D.WHISKERS, (130, 200, 90), 0.5 * sick)
    look_dolph = T("s_dolph") <= t < T("s_land")
    excited = t >= T("s_mira")
    kat(c, tl, t, "luna", 600, deck, 0.66, 1, "sit", look=(1, 0.5) if look_dolph else (1, -0.2),
        eyes="happy" if excited and tl.mouth("luna", t) < 0.1 else ("wide" if look_dolph else "open"))
    kat(c, tl, t, "whiskers", 700, deck, 0.66, 1, "sit", pal=wpal,
        eyes="closed" if sick > 0.5 else ("wide" if excited else "open"), head_dy=6 * sick,
        look=(1, -0.3))
    P.bundle(c, 752, deck, 0.6)
    # railing in front of them
    rail_y = deck - 26
    c.line([(SHIP_X + 470 * SHIP_S, rail_y), (SHIP_X + 930 * SHIP_S, rail_y - 6)], (240, 240, 240), 4)
    for k in range(9):
        x = SHIP_X + (480 + 56 * k) * SHIP_S
        c.line([(x, rail_y), (x, deck)], (240, 240, 240), 3)
    c.line([(SHIP_X + 470 * SHIP_S, rail_y), (SHIP_X + 930 * SHIP_S, rail_y - 6)], None or OUT, 1, cap=False)
    # bow wake and the sea in front of the hull
    for k in range(4):
        u = (t * 0.8 + k / 4) % 1.0
        c.ellipse(SHIP_X + 1000 * SHIP_S - 40 * u, sy - 6, 30 + 40 * u, 7, mix((255, 255, 255), (70, 150, 206), u),
                  ol=None)
    c.poly([(0, sy - 10)] + [(x, sy - 6 + 5 * math.sin(x / 50 - t * 3)) for x in range(0, W + 40, 40)] +
           [(W, H), (0, H)], (40, 110, 180), ol=None)
    sea_waves(c, t * 1.3, sy + 10, H, 90.0, col=(120, 180, 226))
    # dolphins
    if T("s_dolph") - 0.6 <= t < T("s_land", 0.5):
        dolphin_jump(c, t, 900, 2.4, 0.0, 0.9)
        dolphin_jump(c, t, 1010, 2.4, 0.9, 0.75, y=690)
    # Marina glides alongside
    mx = 940 + 60 * math.sin(t * 0.6)
    my = 210 + 20 * math.sin(t * 1.1)
    if T("s_mira") - 1.0 <= t:
        mx, my = lerp(mx, 860, clamp(t - T("s_mira") + 1)), lerp(my, 250, clamp(t - T("s_mira") + 1))
    P.marina(c, mx, my, 0.75, 1, t, fly=True, mouth=tl.mouth("marina", t), flap=t * 6)
    return finish(c, tl, t)


# ================================================================== rambla

RW = 3840
GY = 560        # pavement top
RY = 664        # walking line


def rambla_bg():
    def make():
        c = Canvas(D.gradient(RW * SS, H * SS, [(0, (100, 176, 238)), (0.7, (222, 238, 250)), (1, (222, 238, 250))]),
                   size=(RW, H))
        for x, y in ((300, 90), (1300, 60), (2100, 110), (3100, 70)):
            D.cloud(c, x, y, 0.9)
        # harbour glimpse at the far left
        c.rect(0, GY - 70, 560, GY, (70, 150, 210), ol=None)
        for x in (60, 200):
            P.fishing_boat(c, x + 80, GY - 30, 0.45, col=(220, 80, 70) if x > 100 else (40, 120, 190))
        rng = np.random.default_rng(12)
        walls = [(240, 214, 170), (236, 186, 140), (226, 206, 186), (250, 226, 180), (232, 170, 130), (220, 196, 160)]
        x = 520
        while x < 2280:
            w = rng.uniform(250, 320)
            P.eixample(c, x, GY, w, int(rng.integers(5, 7)), walls[rng.integers(len(walls))], rng,
                       awning=[(200, 60, 60), (60, 120, 170), (60, 140, 90)][rng.integers(3)] if rng.random() < 0.6 else None)
            x += w + 6
        P.gaudi_house(c, 2300, GY, w=320, floors=5, seed=4)
        x = 2650
        while x < 3260:
            w = rng.uniform(250, 300)
            P.eixample(c, x, GY, w, int(rng.integers(5, 7)), walls[rng.integers(len(walls))], rng)
            x += w + 6
        # La Boqueria market gate
        mx = 3280
        c.rect(mx, GY - 300, mx + 560, GY, (180, 160, 140), w=3)
        c.poly([(mx + 60, GY), (mx + 60, GY - 200)] + [(mx + 280 + 220 * math.cos(a), GY - 200 - 90 * math.sin(a))
                                                      for a in np.linspace(math.pi, 0, 16)] + [(mx + 500, GY)],
               (60, 50, 60), w=3)
        P.mosaic(c, "poly", [(mx + 70, GY - 210)] + [(mx + 280 + 205 * math.cos(a), GY - 210 - 80 * math.sin(a))
                                                      for a in np.linspace(math.pi, 0, 16)] + [(mx + 490, GY - 210)],
                 [(220, 70, 70), (250, 200, 60), (60, 140, 200), (80, 170, 110), (240, 140, 60)], seed=3, cell=18)
        c.rect(mx + 150, GY - 330, mx + 410, GY - 280, (250, 246, 230), w=3, r=6)
        c.text(mx + 280, GY - 305, "MERCAT", 30, (180, 50, 60))
        for k in range(6):
            sx = mx + 90 + 70 * k
            c.rect(sx, GY - 60, sx + 50, GY, [(220, 70, 70), (250, 160, 60), (110, 180, 80)][k % 3], w=2)
            for j in range(3):
                c.circle(sx + 10 + 15 * j, GY - 64, 8, [(250, 90, 60), (250, 210, 70), (120, 200, 90)][(k + j) % 3],
                         w=1.5)
        P.colom(c, 270, GY + 10, 0.78)
        # the pavement with its famous wavy pattern
        c.rect(0, GY, RW, H, (232, 220, 196), ol=None)
        for k in range(9):
            y0 = GY + 14 + k * 20
            pts = [(x, y0 + 7 * math.sin(x / 34 + k * 0.6)) for x in range(0, RW + 20, 20)]
            c.line(pts, (200, 184, 156), 4, cap=False)
        c.rect(0, GY - 6, RW, GY + 4, (190, 176, 150), ol=None)
        for x in range(160, RW, 400):
            P.plane_tree(c, x, GY + 40, 1.05)
        P.flower_stall(c, 1020, GY + 54, 0.85, 1)
        P.flower_stall(c, 1560, GY + 54, 0.85, 2)
        P.palm(c, 420, GY + 30, 1.0, lean=0.12)
        return c.img
    return cached("rambla", make)


def rambla_cam(tl, t):
    T = tl.t
    s0 = tl.scenes["rambla"][0]
    return smooth(t, [(s0, 0), (T("r_walk", 1), 1300), (T("r_guitar", 0.05), 1300), (T("r_guitar", 1), 2400),
                      (T("r_finally", 0.3), 2400), (T("r_finally", 1) + 1, 2560)], r=0.5)


def rambla(tl, t):
    T = tl.t
    camx = rambla_cam(tl, t)
    c = view(rambla_bg(), camx)
    c.push(-camx, 0)
    s0 = tl.scenes["rambla"][0]
    # the golden statue
    wink = 1.0 if T("r_statue", 0.12) <= t < T("r_statue", 0.4) else 0.0
    bow = math.sin(math.pi * tl.prog("r_statue", t, 0.45, 0.95))
    P.statue_cat(c, 2060, RY + 6, 0.8, -1, t, wink=wink, bow=bow)
    # Paco busking with his guitar
    pk = [(T("r_vamos", 0.6), 3020), (T("r_finally", 1) + 1.2, 3700)]
    if t < T("r_vamos", 0.6):
        play = 1.0 if t < T("r_paco") or tl.mouth("paco", t) < 0.05 else 0.3
        P.paco(c, 3020, RY, 0.9, -1, "sit", t, mouth=tl.mouth("paco", t), play=play,
               eyes="happy" if t < T("r_paco") else "open")
        notes(c, 2980, RY - 140, t)
    else:
        actor(c, tl, t, "paco", pk, RY, 0.85, -1)
    c.rect(2900, RY - 6, 2980, RY + 8, (120, 70, 50), w=2, r=4)          # open guitar case with coins
    for k in range(4):
        c.circle(2914 + 16 * k, RY - 4, 4, (250, 210, 70), w=1)
    # the cats stroll down La Rambla
    lk = [(s0, 80), (T("r_walk", 1), 1880), (T("r_guitar", 0.05), 1880), (T("r_guitar", 0.9), 2740),
          (T("r_finally", 0.4), 2740), (T("r_finally", 1) + 1.2, 3620)]
    wk = [(s0 + 0.6, -40), (T("r_walk", 1), 1750), (T("r_guitar", 0.15), 1750), (T("r_guitar", 1), 2600),
          (T("r_finally", 0.6), 2600), (T("r_finally", 1) + 1.2, 3500)]
    startle = T("r_statue", 0.12) <= t < T("r_statue", 0.4)
    lface = 1
    leyes = "happy" if T("r_paco") <= t < T("r_vamos") else "open"
    actor(c, tl, t, "luna", lk, RY, 0.8, lface, eyes=leyes, look=(1, -0.3))
    hop = 30 * math.sin(math.pi * clamp((t - T("r_statue", 0.12)) / 0.4)) if startle else 0
    weyes = "wide" if T("r_wink") <= t < T("r_statue", 1) else ("happy" if t >= T("r_vamos", 0.5) else "open")
    actor(c, tl, t, "whiskers", wk, RY - hop, 0.8, 1, eyes=weyes, bundle=True,
          look=(1, -0.6) if T("r_wink") <= t < T("r_statue", 1) else (1, 0))
    # Marina hovers above them
    lx = smooth(t, lk)
    P.marina(c, lx + 90 + 30 * math.sin(t * 0.8), 300 + 18 * math.sin(t * 1.3), 0.7, 1, t, fly=True,
             mouth=tl.mouth("marina", t))
    c.pop()
    return finish(c, tl, t)


# =================================================================== tapas

TY = 600      # table top


def tapas_bg():
    def make():
        wall = (240, 214, 160)
        c = Canvas(bg=wall)
        # azulejo tiles on the lower wall
        tile = Canvas(Image.new("RGB", (40 * SS, 40 * SS), (248, 244, 232)), size=(40, 40))
        tile.circle(20, 20, 9, (40, 90, 170), ol=None)
        tile.circle(20, 20, 4, (250, 200, 60), ol=None)
        for a in range(4):
            aa = a * math.pi / 2 + math.pi / 4
            tile.circle(20 + math.cos(aa) * 20, 20 + math.sin(aa) * 20, 8, (40, 90, 170), ol=None)
        tile.rect(0, 0, 40, 40, None, ol=(200, 196, 186), w=1)
        for x in range(0, W, 40):
            for y in range(300, TY, 40):
                c.img.paste(tile.img, (x * SS, y * SS))
        c.rect(0, 292, W, 304, (180, 90, 60), ol=None)
        # arched doorway onto the street
        c.rect(70, 70, 330, 300, (250, 236, 210), ol=None)
        c.poly([(70, 300), (70, 150)] + [(200 + 130 * math.cos(a), 150 - 90 * math.sin(a))
                                         for a in np.linspace(math.pi, 0, 14)] + [(330, 300)], (150, 210, 240), w=4)
        c.rect(70, 230, 330, 300, (230, 200, 150), ol=None)
        P.plane_tree(c, 150, 290, 0.5)
        c.poly([(70, 300), (70, 150)] + [(200 + 130 * math.cos(a), 150 - 90 * math.sin(a))
                                         for a in np.linspace(math.pi, 0, 14)] + [(330, 300)], None, w=5)
        # shelf with jars, hanging hams, menu board
        c.rect(440, 120, 900, 134, (140, 90, 56), w=2.5)
        for k in range(8):
            jx = 470 + 56 * k
            col = [(230, 190, 80), (120, 160, 70), (210, 90, 60), (240, 230, 200)][k % 4]
            c.rect(jx - 16, 70, jx + 16, 120, col, w=2, r=6)
            c.rect(jx - 12, 62, jx + 12, 72, (150, 110, 80), w=2)
        for k, hx in enumerate((520, 640, 760)):
            c.line([(440, 150), (900, 150)], (120, 90, 60), 4, cap=False)
            P.jamon(c, hx, 150, 0.62)
        c.rect(960, 70, 1210, 270, (50, 60, 56), w=6, r=4)
        c.rect(960, 70, 1210, 270, None, ol=(150, 100, 60), w=6)
        c.text(1085, 110, "TAPAS", 34, (250, 246, 230))
        for k, s in enumerate(("Patatas bravas", "Tortilla", "Croquetas", "Churros")):
            c.text(1085, 152 + 28 * k, s, 17, (250, 236, 200))
        # string of paper fans/garland
        for k in range(14):
            x = 20 + 92 * k
            c.poly([(x, 20), (x + 46, 20), (x + 23, 48)], [(220, 60, 60), (250, 200, 60)][k % 2], w=1.5)
        c.line([(0, 20), (W, 20)], OUT, 2, cap=False)
        return c.img
    return cached("tapas_bg", make)


def table_front(c):
    c.rect(-10, TY, W + 10, TY + 26, (170, 104, 60), w=3)
    c.rect(-10, TY + 26, W + 10, H + 10, (130, 76, 44), w=3)
    for x in range(40, W, 160):
        c.line([(x, TY + 40), (x + 60, TY + 40)], (150, 92, 54), 3, cap=False)
    c.rect(-10, TY + 4, W + 10, TY + 10, (196, 130, 80), ol=None)


PLATES = [("bravas", 580), ("tortilla", 700), ("croquetas", 820), ("olives", 460), ("pan", 900)]


def tapas(tl, t):
    T = tl.t
    c = Canvas(tapas_bg().copy())
    sit_y = TY + 70
    S_ = 1.9
    # --- Luna (left), Paco (right), Marina on a chair back
    luna_laugh = T("ta_moust") <= t < T("ta_end", 1)
    kat(c, tl, t, "luna", 250, sit_y, S_, 1, "sit", eyes="happy" if luna_laugh and tl.mouth("luna", t) < 0.1 else "open",
        look=(1, 0.2), mouth=laughing(t) * 0.5 if T("ta_purpose") <= t else tl.mouth("luna", t))
    paco_laugh = T("ta_purpose") <= t
    P.paco(c, 1010, sit_y, S_, -1, "sit", t, mouth=laughing(t, 1.1) * 0.6 if paco_laugh else tl.mouth("paco", t),
           eyes="happy" if paco_laugh else "open", look=(1, 0.2), guitar_on=False)
    c.rect(1130, 330, 1240, 346, (120, 70, 40), w=2.5, r=3)         # chair back
    c.rect(1134, 346, 1146, TY, (120, 70, 40), w=2)
    c.rect(1224, 346, 1236, TY, (120, 70, 40), w=2)
    P.marina(c, 1185, 334, 1.1, -1, t, mouth=tl.mouth("marina", t),
             eyes="happy" if T("ta_moust") <= t else "open")
    # --- Whiskers in the middle: eating, spicy, churros
    spicy = clamp((t - T("ta_spicy", 0.15)) / 0.6) * (1 - clamp((t - T("ta_churro", 0.4)) / 1.2))
    wpal = P.tinted(D.WHISKERS, (236, 50, 40), 0.6 * spicy)
    eat = T("ta_eat") <= t < T("ta_careful", 0.8) or T("ta_spicy") <= t < T("ta_spicy", 0.15)
    hop = 0.0
    if T("ta_spicy", 0.25) <= t < T("ta_churros", 0.3):
        hop = abs(math.sin((t - T("ta_spicy", 0.25)) * 7)) * 40
    head_dy = 10 + 6 * math.sin(t * 14) if eat else 0
    mouth = tl.mouth("whiskers", t)
    if eat:
        mouth = 0.4 + 0.4 * math.sin(t * 14)
    if T("ta_churro", 0.1) <= t < T("ta_churro", 0.95):
        head_dy = 6 + 4 * math.sin(t * 10)
        mouth = 0.3 + 0.3 * math.sin(t * 10)
    weyes = "open"
    if T("ta_lot") <= t < T("ta_eat") or T("ta_purpose") <= t:
        weyes = "happy" if mouth < 0.1 else "open"
    if T("ta_spicy", 0.15) <= t < T("ta_churros"):
        weyes = "wide"
    if T("ta_churro", 0.1) <= t < T("ta_churro", 0.95):
        weyes = "happy"
    kat(c, tl, t, "whiskers", 640, sit_y - hop, S_, 1, "sit", pal=wpal, eyes=weyes, mouth=mouth, head_dy=head_dy,
        look=(0.3, 1) if eat else (0, 0))
    hx, hy = 640 + 18 * S_, sit_y - hop + (-106 + head_dy) * S_
    if spicy > 0.3:
        for k, ex in enumerate((-24, 26)):
            ph = (t * 1.6 + k * 0.5) % 1.0
            P.steam_puff(c, hx + ex * S_, hy - 40 * S_, ph, 1.3)
    if T("ta_fire") <= t < T("ta_fire", 1):
        P.flame(c, hx + 30 * S_, hy + 18 * S_, 1.4, t)
    if t >= T("ta_churro", 0.95):
        choc_moustache(c, 640, sit_y - hop, S_, 1, "sit", head_dy)
    # --- the table and the food
    table_front(c)
    eat_u = tl.prog("ta_eat", t)
    n_eaten = eat_u * 4.2
    stack = 0
    for k, (kind, px) in enumerate(PLATES):
        if kind == "bravas":
            e = clamp((t - T("ta_spicy")) / 0.8)
        else:
            idx = [1, 2, 3, 4][["tortilla", "croquetas", "olives", "pan"].index(kind)]
            e = clamp(n_eaten - (idx - 1))
        if e >= 1 and kind != "bravas":
            stack += 1
            continue
        P.plate(c, px, TY + 14, 1.15, kind, eaten=e)
    for k in range(stack):
        c.ellipse(700, TY + 12 - 9 * k, 46, 12, (250, 248, 240), w=2)
    # churros and chocolate arrive
    if t >= T("ta_churros", 0.3):
        u = ease(clamp((t - T("ta_churros", 0.3)) / 0.6))
        cx = lerp(980, 640, u)
        chew = tl.prog("ta_churro", t, 0.1, 0.95)
        P.plate(c, cx - 70, TY + 14, 0.85, "churros", eaten=chew * 0.9)
        P.choc_cup(c, cx + 60, TY + 18, 0.9, steam_t=t)
    # a dribble of hot sauce on the table in front of Whiskers
    if T("ta_spicy") <= t:
        c.ellipse(560, TY + 18, 10, 3, (220, 70, 40), ol=None)
    return finish(c, tl, t)


# ================================================================= sagrada

SH = 1440
SAG_X, SAG_BASE, SAG_S = 640, 1290, 1.12
STREET = 1395


def sagrada_bg():
    def make():
        c = Canvas(D.gradient(W * SS, SH * SS, [(0, (70, 150, 230)), (0.6, (190, 224, 250)), (1, (220, 236, 250))]),
                   size=(W, SH))
        for x, y, s in ((180, 160, 1.0), (1100, 260, 0.9), (900, 80, 0.7)):
            D.cloud(c, x, y, s)
        # neighbouring blocks
        rng = np.random.default_rng(4)
        P.eixample(c, -60, SAG_BASE + 40, 220, 8, (230, 200, 170), rng)
        P.eixample(c, 1120, SAG_BASE + 40, 240, 8, (236, 186, 150), rng)
        P.sagrada(c, SAG_X, SAG_BASE, SAG_S)
        # plaza
        c.rect(0, SAG_BASE, W, SH, (220, 206, 180), ol=None)
        c.rect(0, SAG_BASE - 4, W, SAG_BASE + 6, (180, 166, 140), ol=None)
        for k in range(5):
            y = SAG_BASE + 30 + k * 26
            c.line([(0, y), (W, y)], (204, 190, 164), 2, cap=False)
        for x in (120, 1160):
            P.plane_tree(c, x, STREET - 20, 0.9)
        for x in (330, 950):
            c.rect(x - 50, STREET - 30, x + 50, STREET - 20, (150, 100, 60), w=2)
            c.rect(x - 44, STREET - 20, x - 36, STREET, (80, 80, 90), ol=None)
            c.rect(x + 36, STREET - 20, x + 44, STREET, (80, 80, 90), ol=None)
        return c.img
    return cached("sagrada", make)


def sagrada_cam(tl, t):
    T = tl.t
    s0 = tl.scenes["sagrada"][0]
    return smooth(t, [(s0, 0), (s0 + 0.8, 0), (T("sa_tilt", 1) + 1.5, SH - H), (T("sa_beauty", 0.1), SH - H),
                      (T("sa_beauty", 0.9), 360), (T("sa_time", 0.5), 360), (T("sa_end", 0.4), SH - H)], r=0.4)


def sagrada(tl, t):
    T = tl.t
    camy = sagrada_cam(tl, t)
    c = view(sagrada_bg(), 0, camy)
    c.push(0, -camy)
    P.crane(c, 220, SAG_BASE - 80, 1020, jib=330, counter=110, t=t, swing=0.0)
    P.crane(c, 1080, SAG_BASE - 40, 880, jib=-260 if False else 220, counter=90, t=t, swing=2.0,
            col=(236, 110, 60))
    s0 = tl.scenes["sagrada"][0]
    walk_end = T("sa_narr", 0.9)
    lk = [(T("sa_tilt", 0.6), -120), (walk_end, 560)]
    wk = [(T("sa_tilt", 0.7), -260), (walk_end + 0.4, 420)]
    pk = [(T("sa_tilt", 0.5), 1400), (walk_end, 820)]
    look_up = (0.2, -1)
    actor(c, tl, t, "luna", lk, STREET, 0.8, 1, eyes="wide" if T("sa_why") <= t < T("sa_why", 1) else "open",
          look=look_up if t >= T("sa_narr", 0.5) else (1, 0))
    actor(c, tl, t, "whiskers", wk, STREET, 0.8, 1, bundle=True,
          eyes="happy" if T("sa_beauty", 0.5) <= t < T("sa_end") else "open",
          look=look_up if t >= T("sa_narr", 0.7) else (1, 0))
    actor(c, tl, t, "paco", pk, STREET, 0.8, -1)
    mx = smooth(t, [(T("sa_tilt", 0.4), 1400), (walk_end, 700)])
    P.marina(c, mx, STREET - 330 + 20 * math.sin(t * 1.2), 0.7, -1 if mx > 700 else 1, t, fly=True,
             mouth=tl.mouth("marina", t))
    c.pop()
    return finish(c, tl, t)


# ==================================================================== beach

SEA_Y = 330
SHORE = 446
BAG = (430, 600)
WSX, WSY = 600, 604


def beach_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (96, 176, 240)), (SEA_Y / H, (214, 236, 250)),
                                               (SEA_Y / H + 0.001, (60, 150, 206)), (SHORE / H, (110, 190, 220)),
                                               (SHORE / H + 0.001, (238, 214, 160)), (1, (246, 222, 170))]))
        D.cloud(c, 300, 110, 1.1)
        D.cloud(c, 980, 70, 0.8)
        P.hotel_sail(c, 110, SEA_Y + 2, 0.9)
        P.golden_fish(c, 1010, SEA_Y - 6, 0.75)
        for x in (760, 860, 1210):
            P.palm(c, x, SEA_Y + 4, 0.55, lean=0.1)
        c.rect(220, SEA_Y - 30, 700, SEA_Y + 2, (226, 210, 180), w=2)
        for x in range(240, 690, 40):
            c.rect(x, SEA_Y - 22, x + 20, SEA_Y - 10, (120, 160, 200), ol=None)
        # sailing boat far out
        c.poly([(560, SEA_Y + 34), (640, SEA_Y + 34), (626, SEA_Y + 44), (574, SEA_Y + 44)], (250, 250, 250), w=2)
        c.poly([(600, SEA_Y - 26), (600, SEA_Y + 32), (636, SEA_Y + 32)], (250, 250, 250), w=2)
        # sand texture and the boats on the beach
        rng = np.random.default_rng(6)
        for _ in range(160):
            x, y = rng.uniform(0, W), rng.uniform(SHORE + 30, H)
            c.circle(x, y, rng.uniform(1, 2.2), (220, 190, 130), ol=None)
        P.fishing_boat(c, 1110, 560, 1.1, col=(40, 120, 190), stripe=(250, 200, 60), face=-1)
        P.fishing_boat(c, 1230, 640, 0.9, col=(210, 70, 60), stripe=(250, 246, 236), face=-1, mast=False)
        c.ellipse(220, 690, 120, 18, (230, 200, 140), ol=None)
        # a striped beach umbrella
        c.line([(130, 680), (150, 470)], (120, 90, 60), 5)
        for k in range(6):
            a0 = math.pi + k * math.pi / 6
            a1 = a0 + math.pi / 6
            c.poly([(150, 470), (150 + 120 * math.cos(a0), 490 + 40 * math.sin(a0) * 0 + 30),
                    (150 + 120 * math.cos(a1), 490 + 30)], [(230, 60, 60), (250, 246, 236)][k % 2], w=2)
        return c.img
    return cached("beach", make)


def shoreline(tl, t):
    """y of the water's edge (bigger during the wave)."""
    T = tl.t
    base = SHORE + 12 + 8 * math.sin(t * 1.1)
    if T("be_nap", 0.3) <= t:
        base += 30 * clamp((t - T("be_nap", 0.3)) / 3)
    if T("be_wave") <= t < T("be_gone", 1):
        u = (t - T("be_wave")) / (T("be_wave", 1) - T("be_wave"))
        surge = math.sin(math.pi * clamp(u * 0.9)) if u < 1.1 else 0
        base += 200 * surge
    return base


def beach(tl, t):
    T = tl.t
    c = Canvas(beach_bg().copy())
    # far waves glittering
    rng = np.random.default_rng(3)
    for k in range(18):
        x = (rng.uniform(0, W) - t * 20) % W
        y = rng.uniform(SEA_Y + 8, SHORE - 10)
        c.arc(x, y, 14, 4, 200, 340, (200, 236, 250), 2)
    edge = shoreline(tl, t)
    wave_x0 = 220
    c.poly([(0, SHORE - 4), (W, SHORE - 4)] + [(x, edge + 10 * math.sin(x / 50 + t * 2) * (x > wave_x0) -
                                                 (edge - SHORE - 12) * clamp((wave_x0 - x) / 200))
                                                for x in range(W, -40, -40)],
           (110, 190, 220), ol=None)
    c.line([(x, edge + 10 * math.sin(x / 50 + t * 2) * (x > wave_x0) - (edge - SHORE - 12) * clamp((wave_x0 - x) / 200))
            for x in range(0, W + 40, 40)], (250, 252, 255), 6, cap=False)
    # --- the bundle: on the sand, then carried off by the sea
    gone = t >= T("be_wave", 0.45)
    if not gone:
        P.bundle(c, BAG[0], BAG[1], 0.9)
        P.shards(c, BAG[0] - 60, BAG[1] + 4, 0.7, n=4, spread=0.8)
    else:
        u = clamp((t - T("be_wave", 0.45)) / 5.0)
        bx = lerp(BAG[0], 760, ease(u))
        by = lerp(BAG[1], SEA_Y + 50, ease(u)) + 4 * math.sin(t * 3)
        if u < 1:
            P.bundle(c, bx, by, 0.9 * (1 - 0.6 * u))
    # --- sea glass found after Luna looks
    glass_cols = [(80, 190, 140), (90, 160, 230), (240, 200, 110), (220, 240, 240), (60, 140, 110)]
    glass_pos = [(700, 560), (770, 620), (860, 580), (520, 650), (940, 640)]
    if t >= T("be_look", 0.7):
        collect = tl.prog("be_shell", t, 0.0, 1.0)
        for k, ((gx, gy), col) in enumerate(zip(glass_pos, glass_cols)):
            u = clamp((t - T("be_glass", 0.15 * k)) / 0.8)
            x = lerp(gx, 660 + 18 * k, ease(collect))
            y = lerp(gy, WSY + 14, ease(collect))
            tw = max(0.0, math.sin((t * 2 + k) * 2.0)) if collect < 0.5 else 0
            P.sea_glass(c, x, y, col, 1.1, tw=tw)
    # --- characters
    wet = 0.0
    if T("be_wave", 0.35) <= t:
        wet = 1 - clamp((t - T("be_shell")) / 4)
    sleeping = t < T("be_wave", 0.5)
    if sleeping:
        kat(c, tl, t, "whiskers", WSX, WSY, 1.0, 1, "sleep", mouth=0, wet=wet)
        if T("be_narr", 0.5) <= t:
            D.zzz(c, WSX + 60, WSY - 80, t)
    else:
        jolt = clamp((t - T("be_wave", 0.5)) / 0.3)
        stand = T("be_wake", 0.6) <= t < T("be_left")
        if stand:
            x = smooth(t, [(T("be_wake", 0.6), WSX), (T("be_gone", 0.4), WSX + 60)])
            kat(c, tl, t, "whiskers", x, WSY, 1.0, -1 if t < T("be_gone", 0.3) else 1, "stand", wet=wet,
                eyes="wide", look=(1, -0.6), walk=x / 12)
        else:
            sad = T("be_left") <= t < T("be_look", 0.5)
            x = WSX if t < T("be_left") else WSX + 60
            kat(c, tl, t, "whiskers", x, WSY, 1.0, 1, "sit", wet=wet,
                eyes="wide" if t < T("be_left") else ("happy" if t >= T("be_shell", 0.5) else "open"),
                head_dy=-14 * (1 - jolt) + (8 if sad else 0), look=(0.4, 0.9) if sad else (1, 0.2))
            if t >= T("be_left"):
                # the last blue piece, in his paws
                P.shards(c, x + 34, WSY - 10, 0.8, n=1, spread=0)
    # Luna: building a sandcastle, then runs to Whiskers
    cx, cy = 900, 600
    build = clamp((t - tl.scenes["beach"][0]) / 9)
    c.poly([(cx - 50, cy), (cx - 40, cy - 30 * build), (cx + 40, cy - 30 * build), (cx + 50, cy)], (226, 196, 140), w=2)
    if build > 0.4:
        for dx in (-30, 0, 30):
            h = 30 * build + 26 * (build - 0.4) / 0.6 * (1.4 if dx == 0 else 1)
            c.poly([(cx + dx - 12, cy - 28 * build), (cx + dx, cy - h - 30 * build * 0.5), (cx + dx + 12, cy - 28 * build)],
                   (226, 196, 140), w=2)
    lk = [(T("be_wave", 0.5), 800), (T("be_wake", 0.3), 790)]
    if t < T("be_wave", 0.5):
        kat(c, tl, t, "luna", 800, 606, 0.95, 1, "sit", eyes="happy" if t < T("be_nap") else "open",
            look=(1, 0.4))
    else:
        lookp = T("be_look") <= t < T("be_shell")
        actor(c, tl, t, "luna", lk, 606, 0.95, -1, pose="sit" if t >= T("be_wake", 0.3) else "stand",
              eyes="happy" if T("be_shell") <= t else ("wide" if t < T("be_left") else "open"),
              look=(1, 0.8) if lookp else (-1, 0))
    # Paco strums softly by the boats
    P.paco(c, 1060, 640, 0.85, -1, "sit", t, mouth=tl.mouth("paco", t),
           play=0.6 if t < T("be_wave") or t >= T("be_shell") else 0.0,
           eyes="closed" if t < T("be_wave") else ("wide" if t < T("be_look") else "open"))
    if t < T("be_wave"):
        notes(c, 1020, 520, t, 3)
    # Marina: on the sand, then flies off and brings a shell
    if t < T("be_glass", 0.2):
        P.marina(c, 330, 640, 0.75, 1, t, mouth=tl.mouth("marina", t),
                 eyes="closed" if t < T("be_wave") else "open")
    elif t < T("be_glass", 1.0):
        u = tl.prog("be_glass", t, 0.2, 1.0)
        mx = lerp(330, 640, u) + 160 * math.sin(math.pi * u)
        my = 640 + arc_y(u, 260)
        P.marina(c, mx, my, 0.75, 1, t, fly=True)
        if u > 0.45:
            P.shell(c, mx + 20, my - 10, 1.0)
    else:
        P.marina(c, 520, 640, 0.75, 1, t, mouth=tl.mouth("marina", t), eyes="happy")
        P.shell(c, 590, WSY + 18, 1.1)
    if T("be_look", 0.7) <= t < T("be_glass", 1):
        for k in range(3):
            sparkle_star(c, 700 + 120 * k, 540 + 30 * (k % 2), 10 * abs(math.sin(t * 4 + k)))
    return finish(c, tl, t)


# ===================================================================== park

PW = 2 * W
STEP_Y = 650       # walking line on the lowest step (left half)
BENCH_Y = 628      # sitting line on the bench (right half)


def park_bg():
    def make():
        c = Canvas(D.gradient(PW * SS, H * SS, [(0, (90, 160, 230)), (0.45, (250, 214, 170)), (1, (250, 214, 170))]),
                   size=(PW, H))
        c.circle(2250, 200, 46, (255, 236, 160), ol=None)
        # ------------- right half: view over the city to the sea
        sea_y = 290
        c.rect(W, sea_y, PW, sea_y + 40, (90, 160, 210), ol=None)
        rng = np.random.default_rng(9)
        c.rect(W, sea_y + 30, PW, 520, (230, 200, 170), ol=None)
        for _ in range(240):
            x = rng.uniform(W, PW)
            y = rng.uniform(sea_y + 34, 520)
            w = rng.uniform(16, 36)
            c.rect(x, y, x + w, y + w * 0.6, mix((240, 220, 190), (220, 170, 140), rng.uniform()), w=1)
        P.sagrada(c, 1830, 470, 0.22, detail=False)
        P.glories(c, 2220, 480, 0.6)
        P.crane(c, 1900, 470, 190, jib=60, counter=20)
        # hill trees in front of the city
        for k in range(16):
            x = W - 40 + k * 90 + rng.uniform(-20, 20)
            c.circle(x, 520 + rng.uniform(-10, 10), rng.uniform(40, 60), (110, 160, 90), ol=None)
        for x in (1360, 2460):
            P.palm(c, x, 560, 0.9, lean=0.1 if x < 2000 else -0.12)
        # the serpentine mosaic bench (its back)
        top = [(x, 520 + 26 * math.sin((x - W) / 120)) for x in range(W - 20, PW + 30, 20)]
        back = top + [(PW + 20, 600), (W - 20, 600)]
        P.mosaic(c, "poly", back, P.TILE_COLS, seed=12, cell=15)
        c.line(top, (250, 246, 236), 8)
        c.line(top, OUT, 2, cap=False)
        c.rect(W - 20, 600, PW + 20, 640, (226, 206, 170), w=3)
        P.mosaic(c, "poly", [(W - 20, 640), (PW + 20, 640), (PW + 20, H + 4), (W - 20, H + 4)],
                 [(232, 214, 180), (210, 190, 160), (250, 240, 214)], seed=13, cell=22)
        # ------------- left half: the dragon stairway
        P.gingerbread(c, 250, 330, 0.95, seed=2)
        P.gingerbread(c, 1010, 330, 0.95, wall=(206, 160, 110), tower=False, seed=5)
        for x in (520, 760):
            P.palm(c, x, 340, 0.8, lean=0.05 * (1 if x < 640 else -1))
        c.rect(0, 330, W + 40, 360, (214, 190, 150), ol=None)
        P.stone_steps(c, 360, 920, 360, 12, 30)
        # side walls with mosaic crenellations
        for side in (-1, 1):
            x0 = 330 if side < 0 else 950
            wall = [(x0, 360), (x0 + side * -0, 720), (x0 + side * 400, 720), (x0 + side * 400, 360)]
            c.poly(wall, (206, 170, 120), w=3)
            for k in range(6):
                bx = x0 + side * (30 + 64 * k)
                P.mosaic(c, "ellipse", (bx, 372, 30, 18), [(250, 246, 236), (60, 120, 196), (250, 200, 60),
                                                          (220, 70, 70)], seed=20 + k, cell=8)
            for j in range(4):
                for k in range(5):
                    rx = x0 + side * (40 + 72 * k)
                    ry = 420 + 70 * j
                    c.rect(rx - 20, ry, rx + 20, ry + 24, mix((206, 170, 120), (250, 236, 210), 0.35), ol=None)
        P.lizard(c, 700, 560, 1.15)
        # the basin under the lizard's mouth
        c.ellipse(450, 600, 70, 18, (190, 160, 120), w=3)
        c.ellipse(450, 596, 56, 12, (110, 180, 220), ol=None)
        return c.img
    return cached("park", make)


def park_cam(tl, t):
    T = tl.t
    return smooth(t, [(T("pa_build"), 0), (T("pa_build", 0.22), W)], r=0.6)


BOWL_SPOT = (1960 + 0, BENCH_Y - 4)


def park(tl, t):
    T = tl.t
    camx = park_cam(tl, t)
    c = view(park_bg(), camx)
    c.push(-camx, 0)
    # the lizard's fountain
    for k in range(10):
        u = (t * 1.5 + k / 10) % 1.0
        x = 700 - 1.15 * 230 - 20 - 50 * u
        y = 560 - 1.15 * 36 + arc_y(u, 30) + 60 * u * u
        c.circle(x, y, 3 + 2 * (1 - u), (190, 230, 250), ol=None)
    dance = t >= T("pa_dance")
    s0 = tl.scenes["park"][0]
    # positions: stairs (left half), then the bench (right half)
    move0, move1 = T("pa_build", 0.0), T("pa_build", 0.24)
    lk = [(s0, -100), (T("pa_up", 0.8), 220), (move0, 220), (move1, 1700)]
    wk = [(s0 + 0.4, -240), (T("pa_up", 1), 120), (move0 + 0.2, 120), (move1 + 0.3, 1850)]
    pk = [(s0, 1500), (T("pa_up", 0.8), 1070), (move0, 1070), (move1, 2120)]
    building = T("pa_build", 0.24) + 0.3 <= t
    if not dance:
        if t < move1 + 0.4:
            actor(c, tl, t, "luna", lk, STEP_Y, 0.85, 1, eyes="wide" if T("pa_lizard") <= t < T("pa_gaudi") else "open",
                  look=(1, -0.3))
            actor(c, tl, t, "whiskers", wk, STEP_Y + 6, 0.85, 1,
                  eyes="wide" if T("pa_like") <= t < T("pa_secret") else ("happy" if T("pa_secret", 0.6) <= t else "open"),
                  look=(1, -0.2))
            actor(c, tl, t, "paco", pk, STEP_Y, 0.85, -1)
        else:
            kat(c, tl, t, "luna", 1700, BENCH_Y, 0.8, 1, "sit", eyes="happy" if T("pa_better") <= t else "open",
                look=(1, 0.6))
            weyes = "happy" if T("pa_better") <= t and tl.mouth("whiskers", t) < 0.1 else "open"
            kat(c, tl, t, "whiskers", 1850, BENCH_Y, 0.8, 1, "sit", eyes=weyes, look=(1, 0.7))
            P.paco(c, 2120, BENCH_Y, 0.8, -1, "sit", t, mouth=tl.mouth("paco", t),
                   play=1.0 if T("pa_ole", 0.8) <= t else 0.0, look=(-1, 0.5))
    else:
        u = tl.prog("pa_dance", t)
        beat = t * 2.6
        for who, x0, ph in (("luna", 1690, 0.0), ("whiskers", 1880, 1.6)):
            hop = abs(math.sin(beat * math.pi + ph)) * 34
            face = 1 if int(beat + ph) % 2 == 0 else -1
            kat(c, tl, t, who, x0 + 40 * math.sin(beat * 0.5 + ph), BENCH_Y + 50 - hop, 0.8, face, "stand",
                eyes="happy", walk=beat * 3, mouth=0.4 if who == "whiskers" else 0.2,
                squash=1.0 + 0.08 * math.sin(beat * math.tau))
        P.paco(c, 2120, BENCH_Y, 0.8, -1, "sit", t, play=1.0, eyes="happy", mouth=laughing(t) * 0.4)
        notes(c, 2090, BENCH_Y - 130, t, 5)
    # the new bowl being made
    if T("pa_build", 0.25) <= t:
        bu = tl.prog("pa_build", t, 0.25, 0.95)
        bx, by = BOWL_SPOT
        if bu < 0.9:
            c.ellipse(bx, by - 30, 90, 50, (255, 246, 214), w=2)
            # ghost outline of the bowl
            for k in range(14):
                a = k / 14
                c.circle(bx - 44 + 88 * a, by - 54, 2.5, (150, 130, 110), ol=None)
            c.line([(bx - 50, by - 54), (bx - 36, by - 18)], (150, 130, 110), 2)
            c.line([(bx + 50, by - 54), (bx + 36, by - 18)], (150, 130, 110), 2)
            # pieces flying in: the old blue piece, sea glass, the shell, a tile from Paco
            pieces = [("blue", 1850, 0.0), ("glass", 1700, 0.15), ("shell", 2230, 0.3), ("tile", 2120, 0.45),
                      ("glass2", 1700, 0.6)]
            for kind, sx, t0 in pieces:
                v = clamp((bu - t0) / 0.25)
                if v <= 0:
                    continue
                px = lerp(sx, bx + (t0 - 0.3) * 50, ease(v))
                py = lerp(BENCH_Y - 120, by - 36, ease(v)) + arc_y(v, 80)
                if kind == "blue":
                    P.shards(c, px, py, 1.3, n=1, spread=0)
                elif kind == "shell":
                    P.shell(c, px, py, 1.4)
                elif kind == "tile":
                    P.blue_tile(c, px, py, 1.3)
                else:
                    P.sea_glass(c, px, py, (80, 190, 140) if kind == "glass" else (90, 160, 230), 1.5)
                if 0.95 < v and (bu - t0) < 0.33:
                    sparkle_star(c, px, py - 20, 16)
        else:
            k = clamp((bu - 0.9) / 0.1)
            c.ellipse(bx, by - 30, 100 * (0.8 + 0.4 * ease(k)), 52, (255, 246, 214), w=2)
            P.bowl(c, bx, by, 0.8 + 0.4 * ease(k), "mosaic", t=t)
            if t < T("pa_better", 0.5):
                for j in range(5):
                    a = j * math.tau / 5 + t
                    sparkle_star(c, bx + math.cos(a) * 70, by - 40 + math.sin(a) * 40, 12 * abs(math.sin(t * 5 + j)))
    # Marina
    if t < move1:
        mk = [(s0, 1500), (T("pa_up", 0.9), 1000)]
        mx = smooth(t, mk)
        if T("pa_up", 0.9) <= t < move0:
            P.marina(c, 1000, 330, 0.75, -1, t, mouth=tl.mouth("marina", t),
                     eyes="happy" if T("pa_secret") <= t else "open")
        else:
            P.marina(c, mx if t < move0 else lerp(1000, 2260, tl.prog("pa_build", t, 0.0, 0.24)),
                     300 + 10 * math.sin(t * 2), 0.75, 1 if t >= move0 else -1, t, fly=True)
    else:
        if dance:
            P.marina(c, 2260, 548 - abs(math.sin(t * 2.6 * math.pi)) * 20, 0.75, -1, t, eyes="happy",
                     wave=abs(math.sin(t * 8)))
        else:
            P.marina(c, 2260, 548, 0.75, -1, t, mouth=tl.mouth("marina", t))
    c.pop()
    # golden-hour glow, deepening to sunset during the dance
    sunset = 0.08 + 0.3 * tl.prog("pa_dance", t, 0.0, 0.8)
    P.overlay(c, (250, 120, 90), sunset if t >= T("pa_ole") else 0.0)
    if dance:
        for k in range(12):        # string of lights over the terrace
            x = 60 + k * 106
            y = 40 + 20 * math.sin(k * 0.9)
            on = 0.6 + 0.4 * math.sin(t * 4 + k)
            c.circle(x, y, 9, mix((250, 200, 90), (255, 250, 210), on), w=1.5)
        c.line([(60 + k * 106, 40 + 20 * math.sin(k * 0.9)) for k in range(12)], OUT, 1.5, cap=False)
    return finish(c, tl, t)


# ===================================================================== home

SILL = 528


def home_bg():
    def make():
        wall = (250, 228, 190)
        c = Canvas(bg=wall)
        for x in range(0, W, 128):
            c.rect(x + 56, 0, x + 72, H, mix(wall, (255, 255, 255), 0.25), ol=None)
        win = Canvas(D.gradient(860 * SS, 520 * SS, [(0, (110, 186, 245)), (1, (214, 238, 255))]), size=(860, 520))
        win.circle(680, 110, 56, (255, 222, 90), ol=None)
        win.glow(680, 110, 120, 120, (255, 236, 150), (180, 218, 250), steps=6)
        win.circle(680, 110, 56, (255, 222, 90), ol=None)
        D.cloud(win, 200, 120, 1.2)
        D.cloud(win, 520, 220, 0.8)
        win.poly([(0, 420), (200, 380), (460, 410), (860, 370), (860, 520), (0, 520)], (130, 190, 110), ol=None)
        D.tree(win, 120, 470, 0.9)
        D.tree(win, 760, 460, 0.7)
        win.rect(380, 380, 520, 470, (230, 200, 160), ol=None)
        win.poly([(370, 384), (450, 330), (530, 384)], (200, 90, 70), ol=None)
        c.img.paste(win.img, (210 * SS, 0))
        for x0, x1 in ((40, 200), (1080, 1240)):
            c.rect(x0, -10, x1, 560, (200, 70, 80), r=10)
            for xx in range(int(x0) + 24, int(x1), 34):
                c.line([(xx, 10), (xx, 550)], (176, 56, 66), 3, cap=False)
        return c.img
    return cached("home", make)


def home_frame(c):
    c.rect(210, -20, 1070, SILL, None, w=12)
    c.rect(210, -20, 1070, SILL, None, ol=(240, 240, 240), w=8)
    c.line([(640, -10), (640, SILL - 4)], (240, 240, 240), 12, cap=False)
    c.line([(214, 250), (1066, 250)], (240, 240, 240), 12, cap=False)
    c.rect(150, SILL - 6, 1130, SILL + 34, (255, 250, 240), r=6)
    c.rect(150, SILL + 34, 1130, H + 10, mix((250, 228, 190), (0, 0, 0), 0.06), ol=None)


def home(tl, t):
    T = tl.t
    c = Canvas(home_bg().copy())
    # Marina waves goodbye outside the window
    if T("h_curl", 0.2) <= t < T("h_moral", 1):
        u = clamp((t - T("h_curl", 0.2)) / 7.0)
        P.marina(c, lerp(1100, 160, u), 170 + 30 * math.sin(u * 6), 0.7, -1, t, fly=True)
    home_frame(c)
    curl = t >= T("h_curl")
    bx = 640
    if not curl:
        # Whiskers eating, then telling Pip about the bowl
        eating = t < T("h_pip")
        head_dy = 14 + 5 * math.sin(t * 12) if eating else 0
        mouth = 0.35 + 0.35 * math.sin(t * 12) if eating else tl.mouth("whiskers", t)
        kat(c, tl, t, "whiskers", 500, SILL, 1.05, 1, "sit", eyes="happy" if eating or T("h_room") <= t else "open",
            mouth=mouth, head_dy=head_dy, look=(1, 0.4))
        P.bowl(c, bx, SILL, 1.1, "mosaic", food=1 - clamp((t - T("h_open")) / 9), t=t)
        kat(c, tl, t, "luna", 340, SILL, 1.0, 1, "sit", eyes="happy" if T("h_piece") <= t else "open", look=(1, 0.2))
        pk = [(T("h_narr", 0.5), 1200), (T("h_narr", 1), 780)]
        if t >= T("h_room", 0.5):
            pk = [(T("h_room", 0.5), 780), (T("h_room", 0.9), 700), (T("h_curl", 0.2), 700)]
        actor(c, tl, t, "pip", pk, SILL, 1.6, -1, eyes="happy" if T("h_room") <= t else "open",
              proud=T("h_add") <= t < T("h_add", 1))
        if T("h_add", 0.5) <= t < T("h_room", 0.9):
            # Pip's little red bead for the bowl
            px = smooth(t, pk)
            c.circle(px - 30, SILL - 40, 7, (220, 50, 50), w=2)
        if T("h_room", 0.9) <= t:
            c.circle(bx + 18, SILL - 26, 5, (220, 50, 50), w=1.5)
            if t < T("h_room", 0.9) + 0.8:
                sparkle_star(c, bx + 18, SILL - 50, 18)
    else:
        P.bowl(c, bx, SILL, 1.1, "mosaic", food=0, t=t)
        c.circle(bx + 18, SILL - 26, 5, (220, 50, 50), w=1.5)
        kat(c, tl, t, "luna", 360, SILL + 2, 1.0, 1, "sleep", mouth=0)
        kat(c, tl, t, "whiskers", 860, SILL + 2, 1.0, -1, "sleep", mouth=0)
        D.mouse(c, 1000, SILL + 2, 1.4, -1, t, eyes="closed")
        D.zzz(c, 900, 420, t)
    k = ease(tl.prog("h_end", t, 0.1, 0.35))
    if k > 0:
        tile_title(c, W / 2, 640, "The End", int(30 + 40 * k), k)
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "bowl": bowl_scene, "ship": ship_scene, "rambla": rambla, "tapas": tapas,
               "sagrada": sagrada, "beach": beach, "park": park, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["h_curl"]
