"""Prague -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in sync
with the speech. Static backgrounds are drawn once and cached; big "world"
backgrounds are viewed through a camera (x, y, zoom) and characters are drawn
in world coordinates through the camera transform.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.montblanc.props import shade_bottom
from films.prague import props as P

SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "kaspar": 0.6, "bones": 3.1}
PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ------------------------------------------------------------------ helpers

def track(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def arc_y(u, height):
    return -4 * height * u * (1 - u)


def sky(w, h, stops):
    return D.gradient(int(w * SS), int(h * SS), stops)


def world_view(bg, x0, y0, z=1.0):
    """Camera onto a big cached background (SS pixels). Returns a Canvas whose transform maps world -> screen."""
    w, h = W / z, H / z
    if abs(z - 1) < 1e-3:
        xi, yi = int(round(x0 * SS)), int(round(y0 * SS))
        img = bg.crop((xi, yi, xi + W * SS, yi + H * SS))
    else:
        img = bg.resize((W * SS, H * SS), Image.BILINEAR, box=(x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS))
    c = Canvas(img)
    c.push(-x0 * z, -y0 * z, z)
    return c


def cam_box(cx, cy, z, ww, wh):
    """Top-left of a camera centred on (cx, cy) at zoom z, clamped inside a world ww x wh."""
    w, h = W / z, H / z
    return clamp(cx - w / 2, 0, ww - w), clamp(cy - h / 2, 0, wh - h)


def crop(c, x0, y0, w):
    h = w * H / W
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def screen(c):
    """A plain screen-space canvas on the same image (drop any camera transform)."""
    return Canvas(c.img)


def overlay(c, col, alpha):
    if alpha <= 0.003:
        return c
    return Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha)))


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def puppet(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("kaspar", t))
    P.kaspar(c, x, y, s, face, t, mouth=mouth, seed=SEED["kaspar"], **kw)


def skeleton(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("bones", t))
    P.bones(c, x, y, s, face, t, mouth=mouth, seed=SEED["bones"], **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """Draw a character moving along x keyframes; faces the way it moves."""
    x = smooth(t, keys)
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth("pip", t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        kw.pop("hop", None)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "kaspar":
        puppet(c, tl, t, x, y, s, face, walk=x / 11 if moving else 0.0, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kitty(c, tl, t, who, x, y, s, face, pose, walk=x / 12 if moving else 0.0, **kw)
    return x


def head_pos(x, y, s, face, pose="stand", head_dy=0.0):
    if pose == "sit":
        hx, hy = 18, -106 + head_dy
    elif pose == "crouch":
        hx, hy = 52, -64 + head_dy
    elif pose == "leap":
        hx, hy = 58, -74
    else:
        hx, hy = 52, -86 + head_dy
    return x + face * hx * s, y + hy * s


def sparkles(c, x, y, t, r=40, n=6, k=1.0, col=(255, 250, 210)):
    for i in range(n):
        a = t * 1.5 + i * math.tau / n
        u = 0.5 + 0.5 * math.sin(t * 4 + i * 1.7)
        s = 7 * u * k
        if s < 1:
            continue
        px, py = x + math.cos(a) * r, y + math.sin(a) * r * 0.8
        c.line([(px - s, py), (px + s, py)], col, 2.5, cap=False)
        c.line([(px, py - s), (px, py + s)], col, 2.5, cap=False)


def hearts(c, x, y, t, k=1.0):
    for i in range(3):
        u = (t * 0.5 + i / 3) % 1.0
        hx, hy = x + 30 * math.sin(u * 5 + i * 2), y - 80 * u
        r = 7 * k * (1 - u * 0.5)
        if r < 1:
            continue
        col = (240, 90, 120)
        c.circle(hx - r * 0.55, hy, r * 0.6, col, ol=None)
        c.circle(hx + r * 0.55, hy, r * 0.6, col, ol=None)
        c.poly([(hx - r * 1.1, hy + r * 0.15), (hx + r * 1.1, hy + r * 0.15), (hx, hy + r * 1.3)], col, ol=None)


def shiver(c, x, y, t, k=1.0):
    """Little 'scared' wobble lines beside a character."""
    for side in (-1, 1):
        for j in range(2):
            px = x + side * (50 + 10 * j)
            off = 3 * math.sin(t * 30 + j)
            c.line([(px + off, y - 10 - 12 * j), (px + off + side * 4, y + 6 - 12 * j)], (255, 255, 255), 2.5 * k)


def bubble(c, x, y, r, k, draw_fn, t, bg=(214, 232, 250), tail=(0, 1)):
    """A round thought bubble with a picture drawn by draw_fn(sub) in a 240x240 canvas."""
    if k <= 0.01:
        return
    rr = r * ease(k)
    for i, (dx, dy, br) in enumerate(((tail[0] * 30, tail[1] * 150, 8), (tail[0] * 14, tail[1] * 124, 13))):
        c.circle(x + dx * k, y + dy * k - 20 * tail[1], br * k, (255, 255, 255), w=2)
    sub = Canvas(Image.new("RGB", (240 * SS, 240 * SS), bg), size=(240, 240))
    draw_fn(sub)
    m = Image.new("L", sub.img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, 240 * SS - 1, 240 * SS - 1], fill=255)
    sz = max(2, int(2 * rr * SS))
    c.img.paste(sub.img.resize((sz, sz)), (int((x - rr) * SS), int((y - rr) * SS)), m.resize((sz, sz)))
    c.circle(x, y, rr, None, w=4)


# night-time and warm tints
NIGHT = ((30, 36, 90), 0.3)
FIRE = ((255, 150, 70), 0.1)

DUSK_SKY = [(0, (40, 52, 110)), (0.35, (110, 96, 160)), (0.6, (226, 140, 150)), (0.78, (250, 186, 150)),
            (1, (250, 200, 160))]
DAWN_SKY = [(0, (96, 120, 190)), (0.4, (200, 160, 190)), (0.62, (255, 196, 160)), (0.8, (255, 222, 170)),
            (1, (255, 230, 190))]
WINTER_SKY = [(0, (150, 180, 220)), (0.6, (214, 226, 240)), (1, (236, 238, 244))]
NIGHT_SKY = [(0, (14, 18, 52)), (0.5, (36, 44, 100)), (0.85, (70, 70, 130)), (1, (90, 84, 140))]


def river_band(c, x0, x1, y0, y1, top=P.RIVER, bottom=P.RIVER_D, n=10):
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        c.rect(x0, lerp(y0, y1, u0), x1, lerp(y0, y1, u1) + 1, mix(top, bottom, u0), ol=None)


def ripples(c, t, y0, y1, n=40, seed=1, col=P.RIVER_L, drift=0.0, xmin=0, xmax=W, lw=2.0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = rng.uniform(xmin, xmax)
        y = rng.uniform(y0, y1)
        ln = rng.uniform(14, 40) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        ph = rng.uniform(0, math.tau)
        k = 0.5 + 0.5 * math.sin(t * 1.8 + ph)
        xx = (x - drift * t + 6 * math.sin(t * 0.9 + ph) - xmin) % (xmax - xmin + 80) + xmin - 40
        if k > 0.2:
            c.line([(xx - ln * k / 2, y), (xx + ln * k / 2, y)], col, lw, cap=False)


# =================================================================== title

def prague_panorama(c, w, base, sky_stops, lit=0.3, castle_x=None, hill_col=(120, 120, 150), snow=True,
                    seed=3, bridge=True, far_col=None):
    """Prague from the river: castle hill, roofs and spires, the Charles Bridge across the Vltava."""
    cx = castle_x if castle_x is not None else w * 0.72
    P.hill(c, cx - 520, cx + 560, base - 30, base - 190, hill_col, snow=snow)
    P.castle(c, cx, base - 160, 0.6, snow=snow, lit=lit)
    # roofs climbing the hill (Mala Strana) and the old town on the other side
    P.roofscape(c, cx - 420, cx + 480, base - 120, seed + 1, 0.55, lit=lit, snow=snow)
    P.roofscape(c, cx - 520, cx + 560, base - 50, seed + 2, 0.7, lit=lit, snow=snow)
    P.roofscape(c, -20, cx - 480, base - 20, seed + 3, 0.75, lit=lit, snow=snow)
    P.tyn_church(c, cx - 760 if cx - 760 > 120 else 160, base - 60, 0.42, snow=snow)
    P.roofscape(c, -20, w + 20, base + 6, seed + 4, 0.8, lit=lit, snow=snow, spires=True)


def title_bg():
    def make():
        c = Canvas(sky(W, H, DUSK_SKY))
        D.stars(c, 4, 40, W, 220)
        D.moon(c, 1120, 110, 30, sky=(60, 64, 120))
        base = 450
        prague_panorama(c, W, base, DUSK_SKY, lit=0.35, castle_x=1040)
        river_band(c, 0, W, base + 6, H, (150, 140, 180), (60, 80, 130))
        # reflections of lit windows
        rng = np.random.default_rng(2)
        for k in range(40):
            x = rng.uniform(0, W)
            y = rng.uniform(base + 20, base + 70)
            c.rect(x, y, x + rng.uniform(6, 16), y + 2, (250, 220, 150), ol=None)
        # Charles Bridge across the foreground of the river
        P.bridge_side(c, -60, W + 60, 560, 0.75, water=(70, 86, 136))
        P.bridge_tower(c, 80, 540, 0.58)
        for x in (300, 600, 900, 1200):
            P.lamp(c, x, 530, 0.6)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    ripples(c, t, 650, H, 30, seed=4, col=(170, 180, 220))
    for k, (sx, sy) in enumerate(((260, 690), (340, 700))):
        P.swan(c, sx + 12 * t % 400, sy, 0.45, 1, t, seed=k)
    # tiny cats sitting on the parapet, watching the city
    c.tint = ((40, 40, 90), 0.25)
    kitty(c, tl, t, "luna", 690, 512, 0.32, 1, "sit", mouth=0, look=(1, -1))
    kitty(c, tl, t, "whiskers", 740, 512, 0.34, -1, "sit", mouth=0, eyes="happy")
    c.tint = None
    P.snowfall(c, t, seed=1, n=90)
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(600, 70 - 30 * (1 - k), "Whiskers and the", 44, mix((200, 190, 230), (255, 250, 240), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(600, 140, "CHIMNEY CAKE", 24 + 52 * k2, mix((200, 190, 230), (255, 214, 120), k2), stroke=5 * k2)
    if k2 > 0.9:
        sparkles(c, 600, 140, t, r=260, n=8, k=k2)
    return c


# =================================================================== chimney (home, winter night)

FX, FY = 330, 532          # fireplace centre-bottom
WIN = (760, 110, 320, 260)


def snowy_window():
    def make():
        c = Canvas(sky(320, 260, NIGHT_SKY), size=(320, 260))
        D.stars(c, 9, 25, 320, 150)
        D.moon(c, 250, 60, 22, sky=(36, 44, 100))
        c.poly([(0, 200), (80, 176), (170, 196), (260, 170), (320, 186), (320, 260), (0, 260)], (200, 210, 236),
               ol=None)
        c.poly([(0, 230), (120, 214), (320, 226), (320, 260), (0, 260)], (230, 236, 250), ol=None)
        for x, s in ((40, 0.32), (80, 0.4), (290, 0.36)):
            P.fir(c, x, 214, s, col=(40, 80, 80), dark=(30, 60, 66))
        return c.img
    return cached("snowwin", make)


def draw_window(c, t, extra=None):
    sub = Canvas(snowy_window().copy(), size=(320, 260))
    P.snowfall(sub, t, seed=6, n=26, w=320, h=260, speed=30)
    if extra:
        extra(sub)
    c.img.paste(sub.img, (760 * SS, 110 * SS))
    c.rect(756, 106, 1084, 374, None, w=8)
    c.line([(920, 110), (920, 370)], (150, 150, 180), 6, cap=False)
    c.line([(760, 240), (1080, 240)], (150, 150, 180), 6, cap=False)
    c.rect(740, 370, 1100, 392, (150, 146, 170), r=4)
    c.ellipse(920, 368, 150, 8, P.SNOW, ol=None)


def room_bg():
    def make():
        c = Canvas(MF.room(True).copy())
        # warm the room up: firelight on the walls
        warm = Image.new("RGB", c.img.size, (255, 170, 100))
        mask = Image.new("L", c.img.size, 0)
        ImageDraw.Draw(mask).ellipse([(FX - 520) * SS, (FY - 520) * SS, (FX + 520) * SS, (FY + 300) * SS], fill=90)
        mask = mask.filter(ImageFilter.GaussianBlur(80 * SS))
        c.img.paste(warm, (0, 0), mask)
        P.fireplace(c, FX, FY, fire=0)
        # stockings on the mantel
        for k, col in enumerate(((220, 60, 60), (90, 150, 220), (90, 180, 110))):
            sx = FX - 90 + k * 90
            c.poly([(sx - 10, -190 + FY), (sx + 10, -190 + FY), (sx + 10, -150 + FY), (sx + 24, -140 + FY),
                    (sx + 20, -128 + FY), (sx - 10, -134 + FY)], col, w=2)
            c.rect(sx - 12, -192 + FY, sx + 12, -182 + FY, (250, 250, 250), w=1.5)
        # a garland across the mantel
        for k in range(14):
            gx = FX - 140 + k * 21
            c.circle(gx, FY - 214 + 6 * math.sin(k), 9, P.PINE, w=1.5)
        return c.img
    return cached("roombg", make)


def room_frame(tl, t, fire=1.0, shake=0.0, win_extra=None, tree_x=120):
    c = Canvas(room_bg().copy())
    draw_window(c, t, win_extra)
    P.fireplace(c, FX + shake, FY, t, fire=fire)
    P.fir(c, tree_x, 560, 1.7, lights=P.BULBS, t=t, star=True)
    # presents under the tree
    for k, (dx, col) in enumerate(((-50, (220, 60, 60)), (10, (80, 140, 220)), (60, (250, 200, 60)))):
        c.rect(tree_x + dx - 18, 530, tree_x + dx + 18, 562, col, w=2)
        c.line([(tree_x + dx, 530), (tree_x + dx, 562)], (255, 255, 255), 3, cap=False)
    return c


def bubble_clock(t, mode):
    def fn(sub):
        sub.img.paste(sky(240, 240, [(0, (150, 180, 230)), (1, (220, 230, 250))]), (0, 0))
        sub.rect(40, 30, 200, 240, (176, 166, 158), w=2)
        P.orloj_dial(sub, 120, 130, 62, t, hand=t * 0.4)
        if mode == "skel":
            P.bones(sub, 178, 230, 0.45, -1, t, ring=1.0, eyes="happy")
        for dx in (-30, 30):
            sub.rect(120 + dx - 14, 34, 120 + dx + 14, 60, (34, 30, 40), w=2)
            P.apostle(sub, 120 + dx + 6 * math.sin(t * 2), 62, 0.36, P.APOSTLE_COLS[int(t) % 12])
    return fn


def bubble_cake(t):
    def fn(sub):
        sub.img.paste(sky(240, 240, [(0, (255, 226, 190)), (1, (255, 240, 220))]), (0, 0))
        P.trdelnik(sub, 120, 190, 1.6, vertical=True, steam=1.0, t=t)
        sparkles(sub, 120, 120, t, r=70, n=6, col=(255, 200, 90))
    return fn


def chimney(tl, t):
    T = tl.t
    s0 = tl.scenes["chimney"][0]
    rum = tl.prog("c_rumble", t, 0.0, 0.8)
    shake = 4 * math.sin(t * 40) * (1 if 0 < rum < 1 else 0)
    c = room_frame(tl, t, fire=1.0 - 0.7 * (T("c_rumble", 0.78) <= t < T("c_soot", 0.6)), shake=shake)
    c.tint = FIRE
    LY = 604
    # soot crumbs falling in the fireplace while the rumble goes on
    if 0 < rum < 1:
        rng = np.random.default_rng(int(t * 12))
        for k in range(8):
            c.circle(FX + rng.uniform(-60, 60), FY - 160 + rng.uniform(0, 140), 3, (50, 46, 50), ol=None)
    # ---- Kasparek tumbles out
    k_x, k_y, k_s = 430, LY + 4, 0.9
    if t >= T("c_rumble", 0.78):
        u = tl.prog("c_rumble", t, 0.78, 1.0) * 0.5 + tl.prog("c_soot", t, 0.0, 0.5) * 0.5
        x = lerp(FX, k_x, ease(u))
        y = lerp(FY - 40, k_y, ease(u)) + arc_y(u, 70)
        sooty = 1.0 - 0.85 * tl.prog("c_soot", t, 0.55, 0.95)
        untied = tl.prog("c_untie", t, 0.1, 0.95)
        tangle = 1.0 - untied
        jump = 0.0
        wave = 0.0
        arms = 0.0
        eyes = "open"
        if t < T("c_soot", 0.5):
            eyes = "wide"
        if T("c_ahoj") <= t < T("c_ahoj", 0.4):
            wave = 1.0
        if T("c_noon") <= t < T("c_show", 1.0):
            jump = abs(math.sin((t - T("c_noon")) * 5)) * 16 * tl.prog("c_noon", t, 0.6, 1.0)
            arms = 1.0 if t >= T("c_show") else 0.0
        if T("c_knots", 0.7) <= t < T("c_untie"):
            arms = 1.0
        if t >= T("c_untie", 0.95) and t < T("c_noon"):
            eyes = "happy"
        if T("c_cake") <= t < T("c_think", 1):
            eyes = "happy"
        face = -1 if t >= T("c_ahoj") and t < T("c_pip") else 1
        if t >= T("c_end"):
            ex = tl.prog("c_end", t)
            x = lerp(k_x, 1400, ease(ex))
            face = 1
        puppet(c, tl, t, x, y, k_s, face, sooty=sooty, tangle=tangle, bar=untied > 0.9, jump=jump, wave=wave,
               arms_up=arms, eyes=eyes, walk=t * 9 if t >= T("c_end") else 0.0)
        if t < T("c_soot", 0.2):
            P.chimney_soot(c, FX, FY - 40, tl.prog("c_rumble", t, 0.78, 1.0) * 0.5 + tl.prog("c_soot", t, 0, 0.2) * 0.5)
        if T("c_soot", 0.55) <= t < T("c_soot", 1.0):
            P.chimney_soot(c, x, y - 60, tl.prog("c_soot", t, 0.55, 1.0) * 0.8 + 0.2, seed=5)
    # ---- Pip arrives from the right and unties the knots
    if t >= T("c_pip"):
        pip_keys = [(T("c_pip"), 1300), (T("c_pip", 1.0), 500), (T("c_untie"), 500), (T("c_untie", 0.25), 380),
                    (T("c_untie", 0.5), 470), (T("c_untie", 0.75), 390), (T("c_untie", 1.0), 500)]
        if t >= T("c_end"):
            pip_keys += [(T("c_end"), 500), (T("c_end", 1.0), 520)]
        hop = abs(math.sin(t * 9)) * 18 if T("c_untie") <= t < T("c_untie", 1.0) else 0.0
        actor(c, tl, t, "pip", pip_keys, LY + 6 - hop, 1.0, -1, proud=T("c_paws") <= t < T("c_paws", 1.0),
              eyes="happy" if T("c_untie", 1.0) <= t < T("c_noon") else "open")
    # ---- Luna sits by the fire
    lx = 640
    l_face = -1
    l_eyes = "open"
    if T("c_clock") <= t < T("c_skel", 1.0):
        l_eyes = "happy"
    if t < T("c_end"):
        kitty(c, tl, t, "luna", lx, LY, 0.82, l_face, "sit", eyes=l_eyes,
              look=(-1, 0) if t < T("c_clock") else (-0.5, -1))
    else:
        actor(c, tl, t, "luna", [(T("c_end"), lx), (T("c_end", 1.0), 1500)], LY, 0.82)
    # ---- Whiskers dozes on the rug, startles, sulks, then can't resist the cake
    wx = 780
    if t < T("c_rumble", 0.3):
        D.cat(c, wx, LY + 10, D.WHISKERS, 0.82, -1, "sleep", t=t, mouth=0)
        D.zzz(c, wx - 40, LY - 50, t)
    elif t < T("c_no", 0.35):
        startled = T("c_rumble", 0.78) <= t < T("c_soot", 0.6)
        pose = "crouch" if startled else "stand"
        kitty(c, tl, t, "whiskers", wx, LY + 10, 0.82, -1, pose, eyes="wide" if startled or t < T("c_hey", 1) else "open",
              look=(-1, 0))
        if startled:
            shiver(c, wx, LY - 60, t)
    elif t < T("c_think"):
        D.cat(c, wx, LY + 10, D.WHISKERS, 0.82, 1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
    elif t < T("c_end"):
        pose = "sit" if t < T("c_which") else "stand"
        kitty(c, tl, t, "whiskers", wx, LY + 10, 0.82, -1, pose, eyes="wide" if t < T("c_which") else "happy",
              look=(-1, -0.5))
        if t >= T("c_which"):
            hearts(c, wx - 50, LY - 120, t, 0.8)
    else:
        actor(c, tl, t, "whiskers", [(T("c_end"), wx), (T("c_end", 0.8), 1500)], LY + 10, 0.82)
    c.tint = None
    # thought bubbles over Luna (the clock, the skeleton) and over Whiskers (the cake)
    kb = tl.prog("c_clock", t, 0.0, 0.25) * (1 - tl.prog("c_no", t, 0.0, 0.2))
    if kb > 0:
        bubble(c, lx - 60, 300, 100, kb, bubble_clock(t, "skel" if t >= T("c_skel") else "clock"), t,
               tail=(0.5, 1))
    kc = tl.prog("c_cake", t, 0.0, 0.25) * (1 - tl.prog("c_which", t, 0.6, 1.0))
    if kc > 0:
        bubble(c, wx + 40, 320, 95, kc, bubble_cake(t), t, tail=(-0.3, 1))
    # frame: closer on the hearth
    return crop(c, 40, 120, 1060)


# =================================================================== barge (night river -> dawn in Prague)

RW = 2600      # width of the river backgrounds
RB = 470       # river bank line


def night_river_bg():
    def make():
        c = Canvas(sky(RW, H, NIGHT_SKY), size=(RW, H))
        D.stars(c, 11, 220, RW, 330)
        D.moon(c, 520, 120, 40, sky=(30, 36, 90))
        # far snowy hills
        c.poly([(0, 400)] + [(x, 360 - 50 * math.sin(x / 260) - 20 * math.sin(x / 90)) for x in range(0, RW + 40, 40)]
               + [(RW, 400), (RW, RB), (0, RB)], (120, 130, 176), ol=None)
        c.poly([(0, 440)] + [(x, 410 - 30 * math.sin(x / 190 + 1) - 12 * math.sin(x / 60)) for x in range(0, RW + 40, 40)]
               + [(RW, RB), (0, RB)], (160, 170, 210), ol=None)
        rng = np.random.default_rng(3)
        # dark pine forests and a little village with a church
        for x in range(0, RW, 26):
            if 1200 < x < 1560:
                continue
            if rng.random() < 0.75:
                P.fir(c, x + rng.uniform(-8, 8), RB - rng.uniform(0, 20), rng.uniform(0.35, 0.6),
                      col=(40, 70, 86), dark=(30, 56, 72))
        for k in range(6):
            hx = 1220 + k * 56
            P.house(c, hx, RB - 4, 50, rng.uniform(46, 70), mix(P.WALLS[k], (60, 70, 120), 0.45), rng,
                    roof=mix(P.ROOF, (60, 70, 120), 0.45), lit=0.8)
        P.spire(c, 1390, RB - 70, 0.6, kind=1, body=mix(P.STONE, (60, 70, 120), 0.45),
                col=mix(P.COPPER, (60, 70, 120), 0.4))
        c.rect(0, RB - 6, RW, RB + 6, (220, 228, 246), ol=None)
        river_band(c, 0, RW, RB + 6, H, (46, 64, 112), (24, 34, 70))
        # moon path on the water
        for k in range(10):
            y = RB + 20 + k * 22
            c.rect(520 - 50 + k * 4, y, 520 + 50 - k * 4, y + 4, (220, 220, 200), ol=None)
        for x in range(1220, 1560, 56):
            c.rect(x + 14, RB + 14, x + 26, RB + 40, (200, 180, 110), ol=None)
        return c.img
    return cached("nightriver", make)


def dawn_river_bg():
    def make():
        c = Canvas(sky(RW, H, DAWN_SKY), size=(RW, H))
        for k in range(8):
            c.circle(1500, RB - 60, 60 + k * 16, mix((255, 240, 200), (255, 218, 176), k / 8), ol=None)
        D.cloud(c, 600, 140, 1.2, (255, 236, 226))
        D.cloud(c, 2100, 110, 1.0, (255, 236, 226))
        base = RB
        prague_panorama(c, RW, base, DAWN_SKY, lit=0.0, castle_x=1700, hill_col=(150, 136, 160), seed=8)
        # left part: the river bank before the city: snowy trees and a few houses
        river_band(c, 0, RW, base + 6, H, (190, 170, 200), (90, 110, 160))
        for k in range(30):
            x = 120 + k * 83
            c.rect(x, base + 24 + (k * 37) % 60, x + 30, base + 27 + (k * 37) % 60, (255, 230, 200), ol=None)
        return c.img
    return cached("dawnriver", make)


def barge_riders(c, tl, t, bx, by, s, phase):
    """The friends on the barge (barge-local positions scaled by s)."""
    T = tl.t
    wx, wy = bx + 40 * s, by - 80 * s
    lx, ly = bx - 150 * s, by - 78 * s
    kx, ky = bx - 236 * s, by - 30 * s
    if phase == "home":
        D.cat(c, lx + 20, ly + 2, D.LUNA, 0.58 * s / 0.75, 1, "sleep", t=t + 1, seed=1.3)
        D.cat(c, wx, wy + 2, D.WHISKERS, 0.6 * s / 0.75, -1, "sleep", t=t, mouth=0)
        D.zzz(c, wx - 30, wy - 40, t)
        return
    cs = 0.58 * s / 0.75
    # Luna on the trees at the bow
    leyes = "wide" if T("b_look") <= t < T("b_look", 1) else "open"
    kitty(c, tl, t, "luna", lx, ly, cs, 1, "sit", eyes=leyes, look=(1, -1 if t >= T("b_dawn") else 0))
    # Whiskers: asleep, wakes for the forest line, counts spires, nods off again
    if t < T("b_forest") or (T("b_forest", 1) + 0.4 <= t < T("b_look")):
        D.cat(c, wx, wy + 2, D.WHISKERS, cs, -1, "sleep", t=t, mouth=0)
        D.zzz(c, wx - 30, wy - 40, t)
    elif t < T("b_count", 1) + 0.6:
        bob = 6 * math.sin((t - T("b_count")) * 6) if t >= T("b_count") else 0
        eyes = "closed" if t > T("b_count", 0.8) else "open"
        kitty(c, tl, t, "whiskers", wx, wy, cs, 1 if t >= T("b_look") else -1, "sit", head_dy=bob, eyes=eyes,
              look=(1, -1))
    else:
        D.cat(c, wx, wy + 2, D.WHISKERS, cs, 1, "sleep", t=t, mouth=0)
        D.zzz(c, wx + 20, wy - 40, t)
    # Kasparek at the bow, by the lantern
    arms = 1.0 if T("b_look") <= t < T("b_look", 1) else 0.0
    jump = abs(math.sin(t * 7)) * 10 if T("b_look") <= t < T("b_look", 1) else 0.0
    puppet(c, tl, t, kx, ky, 0.5 * s / 0.75, 1, arms_up=arms, jump=jump,
           eyes="closed" if t < T("b_dawn", 0.3) and t > T("b_narr", 0.6) else "open")


def barge(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["barge"]
    dawn = ease(tl.prog("b_dawn", t, 0.1, 0.8))
    # cameras: the night pan, then the dawn pan towards the castle
    cam_n = lerp(0, RW - W, (t - s0) / max(1e-6, T("b_dawn", 1.0) - s0))
    cam_d = lerp(500, 1100, ease(tl.prog("b_dawn", t) * 0.3 + tl.prog("b_look", t) * 0.2 +
                                 tl.prog("b_count", t) * 0.2 + tl.prog("b_swans", t) * 0.3))
    if dawn < 1:
        a = Canvas(night_river_bg()).img.crop((int(cam_n * SS), 0, int(cam_n * SS) + W * SS, H * SS))
        if dawn > 0:
            b = dawn_river_bg().crop((int(cam_d * SS), 0, int(cam_d * SS) + W * SS, H * SS))
            a = Image.blend(a, b, dawn)
        c = Canvas(a)
    else:
        c = Canvas(dawn_river_bg().crop((int(cam_d * SS), 0, int(cam_d * SS) + W * SS, H * SS)))
    night = 1 - dawn
    ripples(c, t, RB + 20, H, 40, seed=5, col=mix((255, 230, 200), (100, 120, 180), night), drift=60)
    # swans gliding alongside at dawn
    if t >= T("b_swans") - 0.5:
        u = tl.prog("b_swans", t)
        for k, (dx, dy) in enumerate(((0, 0), (90, 26), (180, -8))):
            P.swan(c, lerp(1400, 780, ease(u)) + dx + 30 * k * u, 690 + dy, 0.7, -1 if u < 0.6 else 1, t, seed=k)
    bx, by, bs = 560, 640, 0.78
    c.tint = (mix((255, 200, 170), (30, 36, 90), night), 0.12 + 0.2 * night)
    P.barge(c, bx, by, bs, 1, t, lantern=1.0)
    barge_riders(c, tl, t, bx, by + 2 * math.sin(t * 1.4), bs, "go")
    c.tint = None
    if night > 0.05:
        P.snowfall(c, t, seed=2, n=int(60 * night) + 1, speed=30)
    return c


# =================================================================== bridge (Charles Bridge)

BW = 3200
DECK = 640


def bridge_bg():
    def make():
        c = Canvas(sky(BW, H, WINTER_SKY), size=(BW, H))
        D.cloud(c, 400, 120, 1.3, (250, 250, 255))
        D.cloud(c, 1500, 90, 1.0, (250, 250, 255))
        D.cloud(c, 2600, 130, 1.2, (250, 250, 255))
        # across the river: castle hill and the Lesser Town
        base = 380
        P.hill(c, 200, 1500, base, base - 210, (176, 186, 206))
        P.castle(c, 820, base - 180, 0.62, snow=True)
        P.roofscape(c, 200, 1500, base - 70, 21, 0.5)
        P.roofscape(c, -20, BW + 20, base, 22, 0.62)
        river_band(c, 0, BW, base, 480, (150, 186, 214), (110, 150, 190))
        # back parapet with saints and lamps
        c.rect(0, 470, BW, 512, P.STONE_D, w=2.5)
        c.rect(0, 462, BW, 474, P.STONE, w=2)
        c.rect(0, 456, BW, 464, P.SNOW, ol=None)
        for k in range(7):
            sx = 260 + k * 460
            P.statue(c, sx, 462, 0.95, kind=k % 3)
            P.lamp(c, sx + 230, 470, 0.95, lit=0)
        # cobbled deck
        c.rect(0, 512, BW, H, (196, 186, 174), ol=None)
        rng = np.random.default_rng(4)
        for r in range(9):
            y = 520 + r * 24
            off = (r % 2) * 22
            for x in range(-40 + off, BW, 44):
                c.ellipse(x, y, 19, 9, mix((206, 198, 186), (170, 160, 150), rng.random()), ol=(150, 140, 130), w=1)
        for k in range(40):
            x = rng.uniform(0, BW)
            c.ellipse(x, rng.uniform(516, 530), rng.uniform(20, 50), 5, P.SNOW, ol=None)
        # the Old Town Bridge Tower at the far end
        P.bridge_tower(c, 2980, DECK + 40, 1.0)
        return c.img
    return cached("bridgebg", make)


def bridge(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["bridge"]
    stop = T("br_sniff")
    run0, run1 = T("br_run"), s1
    kx = smooth(t, [(s0, 120), (stop, 2200), (T("br_cinn", 1), 2260), (run1, 3200)])
    lx = smooth(t, [(s0, 0), (stop, 2060), (T("br_cinn", 1), 2100), (run1, 3100)])
    wx = smooth(t, [(s0, -120), (stop, 1920), (run0, 1920), (T("br_run", 0.6), 3100), (run1, 3300)])
    camx = clamp(smooth(t, [(s0, 0), (stop, 1600), (run1, BW - W)]), 0, BW - W)
    c = world_view(bridge_bg(), camx, 0)
    # the street musician by a statue
    P.musician_dog(c, 1180, DECK - 20, 0.95, 1, t)
    P.notes(c, 1180, DECK - 180, t, 0.9, col=(120, 90, 160))
    # a few snow-capped pigeons? no: a little crowd of passers-by
    for k, (px, col, ears) in enumerate(((700, (190, 150, 120), 2), (1550, (160, 160, 170), 1), (2500, (210, 170, 110), 0))):
        P.kid_back(c, px, DECK + 70, 0.9, col, kind=k, ears=ears, t=t)
    y = DECK + 40
    actor(c, tl, t, "kaspar", [(s0, 120), (stop, 2200), (T("br_cinn", 1), 2260), (run1, 3200)], y - 6, 0.62,
          wave=1.0 if T("br_hurry") <= t < T("br_hurry", 0.5) else 0.0)
    actor(c, tl, t, "luna", [(s0, 0), (stop, 2060), (T("br_cinn", 1), 2100), (run1, 3100)], y, 0.7)
    sniff = T("br_sniff") <= t < T("br_run")
    actor(c, tl, t, "whiskers", [(s0, -120), (stop, 1920), (run0, 1920), (T("br_run", 0.6), 3100), (run1, 3300)],
          y + 4, 0.72, head_dy=-6 * abs(math.sin(t * 8)) if sniff else 0.0,
          eyes="closed" if sniff and t < T("br_cinn") else ("happy" if sniff else "open"))
    if sniff:
        # a curl of cinnamon scent drifting in from the right
        sc = screen(c)
        hx, hy = head_pos(1920 - camx, y + 4, 0.72, 1)
        for j in range(2):
            pts = [(hx + 420 - 400 * u, hy - 90 + 70 * u + 16 * math.sin(u * 10 + t * 3 + j * 2) - 18 * j)
                   for u in np.linspace(0, 1, 18)]
            sc.line(pts, (250, 214, 160), 3)
    c = screen(c)
    shade_bottom(c, tl, t, 0.45)
    return c


# =================================================================== market (Old Town Square)

MW = 1600
MG = 676           # where the characters stand
TOWER_X, TOWER_B, TOWER_S = 1400, 640, 0.45


def tower_pt(lx, ly, x=TOWER_X, b=TOWER_B, s=TOWER_S):
    return x + lx * s, b + ly * s


def market_bg():
    def make():
        c = Canvas(sky(MW, H, WINTER_SKY), size=(MW, H))
        D.cloud(c, 300, 90, 1.0, (250, 250, 255))
        D.cloud(c, 1000, 60, 0.8, (250, 250, 255))
        P.tyn_church(c, 520, 470, 0.62)
        rng = np.random.default_rng(31)
        # facades around the square
        x = -20
        k = 0
        while x < 1300:
            w = rng.uniform(100, 150)
            h = rng.uniform(150, 230) if not (330 < x < 700) else rng.uniform(110, 140)
            P.house(c, x, 560, w, h, P.WALLS[k % len(P.WALLS)], rng, gable=int(rng.integers(3)), lit=0.3)
            x += w - 2
            k += 1
        # cobbled square
        c.rect(0, 560, MW, H, (200, 192, 184), ol=None)
        for r in range(7):
            y = 572 + r * 22
            off = (r % 2) * 20
            for xx in range(-40 + off, MW, 40):
                c.ellipse(xx, y, 17, 8, mix((210, 202, 194), (176, 168, 160), rng.random()), ol=(156, 148, 140), w=1)
        for k in range(30):
            c.ellipse(rng.uniform(0, MW), rng.uniform(566, 600), rng.uniform(20, 60), 5, P.SNOW, ol=None)
        P.orloj_tower(c, TOWER_X, TOWER_B, TOWER_S)
        return c.img
    return cached("marketbg", make)


def orloj_parts(c, tl, t, x, b, s, hand=0.0, door=0.0, shutters=1.0, parade=None, crow=0.0, ring=0.0,
                bones_kw=None, cal=0.0):
    """Moving parts of the clock drawn on top of the tower (tower-local coords)."""
    c.push(x, b, s)
    P.orloj_dial(c, 0, -760, 150, t, hand=hand)
    P.calendar_dial(c, 0, -440, 110, cal)
    # apostle windows: shutters or the parade
    for side, dx in enumerate((-60, 60)):
        if parade is not None:
            u = parade
            i = int(u * 6) % 6
            f = u * 6 - int(u * 6)
            ax = dx + lerp(-34, 34, f)
            P.apostle(c, ax, -972, 1.15, P.APOSTLE_COLS[(i * 2 + side) % 12], k=i * 2 + side)
            body = (176, 166, 158)
            lite = mix(body, (255, 255, 255), 0.18)
            c.rect(dx - 80, -1100, dx - 35, -960, lite, ol=None)
            c.rect(dx + 35, -1100, dx + 80, -960, lite, ol=None)
            c.rect(dx - 34, -1070, dx + 34, -970, None, w=2.5)
        if shutters > 0:
            for sd in (-1, 1):
                w = 34 * shutters
                x0 = dx - 34 if sd < 0 else dx + 34 - w
                c.rect(x0, -1068, x0 + w, -970, P.WOOD, w=2)
                c.line([(x0 + w / 2, -1060), (x0 + w / 2, -976)], P.WOOD_D, 1.5, cap=False)
    P.rooster(c, 0, -1104, 1.1, crow=crow, t=t)
    # little door beside the dial
    if door > 0:
        c.rect(205, -960, 275, -850, (30, 24, 30), w=2.5, r=6)
        c.rect(275 - 70 * (1 - door), -960, 275 + 10 * door, -850, (110, 74, 50), w=2, r=4)
    c.pop()
    if bones_kw is not None:
        bx, by = x + 215 * s, b - 712 * s
        skeleton(c, tl, t, bx, by, s * 0.85, -1, ring=ring, **bones_kw)


def market(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["market"]
    camx = smooth(t, [(s0, 0), (T("m_stall", 1.0), 320)])
    c = world_view(market_bg(), camx, 0)
    # big Christmas tree and the stalls
    P.fir(c, 790, 600, 2.3, lights=P.BULBS, t=t, star=True)
    P.stall(c, 180, 610, 0.8, roof=(60, 120, 90), goods="gingerbread", sign="PERNÍK", t=t, rng_seed=2)
    P.stall(c, 470, 612, 0.8, roof=(200, 60, 60), goods="puppets", sign="LOUTKY", t=t)
    P.stall(c, 1110, 614, 0.85, roof=(60, 90, 160), goods="mugs", sign="PUNČ", t=t)
    P.stall(c, 980, 640, 0.95, roof=(200, 60, 60), goods="cakes", sign="TRDELNÍK", t=t)
    P.trdelnik(c, 930, 574, 0.6, vertical=True, steam=1.0, t=t)
    # the clock: the hand creeps towards noon, the skeleton rings at m_bong
    ring = 1.0 if T("m_bong") <= t < T("m_bong", 0.5) else 0.0
    door = 1.0 if T("m_bong", 0.75) <= t < T("m_bong", 0.95) else 0.0
    orloj_parts(c, tl, t, TOWER_X, TOWER_B, TOWER_S, hand=-0.2 + 0.002 * (t - s0), door=door, ring=ring,
                bones_kw=dict(mouth=0, eyes="happy" if ring else "open",
                              wave=1.0 if T("m_aah") <= t < T("m_hide", 1) else 0.0))
    for k, (px, col, ears) in enumerate(((150, (190, 150, 120), 2), (330, (150, 150, 160), 1),
                                         (1250, (210, 170, 110), 0), (1360, (120, 110, 100), 2))):
        P.kid_back(c, px, MG + 60, 0.85, col, kind=k + 1, ears=ears, t=t)
    # ---- the cast
    lx, kx0, wx = 640, 760, 880
    l_eyes = "happy" if T("m_stuck") <= t < T("m_hat", 1) else "open"
    if T("m_bong", 0.4) <= t:
        l_eyes = "wide" if t < T("m_aah", 0.5) else "open"
    lpose = "sit"
    kitty(c, tl, t, "luna", lx, MG, 0.8, 1, lpose, eyes=l_eyes,
          mouth=(0.4 + 0.3 * math.sin(t * 14)) if T("m_hat", 0.6) <= t < T("m_bong") else tl.mouth("luna", t))
    # Kasparek fetches a cake and sets it down for Whiskers
    gift = tl.prog("m_gift", t)
    kx = smooth(t, [(s0, kx0), (T("m_stall"), kx0), (T("m_stall", 0.6), 930), (T("m_gift"), 930),
                    (T("m_gift", 0.8), kx0), (s1, kx0)])
    holding = T("m_stall", 0.6) <= t < T("m_eat")
    kface = -1 if t < T("m_gift") and t > T("m_stall", 0.6) else 1
    k_jump = abs(math.sin(t * 9)) * 12 if T("m_stuck") <= t < T("m_hat", 1) else 0.0
    puppet(c, tl, t, kx, MG - 2, 0.66, kface, jump=k_jump, eyes="happy" if k_jump else "open",
           walk=kx / 11 if T("m_stall") <= t < T("m_gift", 0.8) else 0.0,
           mouth=(0.5 + 0.4 * math.sin(t * 15)) if k_jump else tl.mouth("kaspar", t))
    # ---- Whiskers and the chimney cake
    cake_s = 1.5
    w_face = -1
    if t < T("m_eat"):
        # waits, licking his lips; the cake comes to rest in front of him
        kitty(c, tl, t, "whiskers", wx, MG + 4, 0.82, w_face, "sit", eyes="happy" if t >= T("m_gift") else "open",
              look=(-1, 0))
        if holding:
            hx, hy = kx + 10, MG - 70 * 0.66
            if t >= T("m_gift", 0.7):
                u = tl.prog("m_gift", t, 0.7, 1.0)
                hx, hy = lerp(hx, wx - 80, u), lerp(hy, MG - 24, u)
            P.trdelnik(c, hx, hy, cake_s * 0.7, ang=0.0)
    elif t < T("m_eat", 0.75):
        u = tl.prog("m_eat", t, 0.0, 0.75)
        kitty(c, tl, t, "whiskers", wx, MG + 4, 0.82, w_face, "crouch", eyes="happy",
              mouth=0.5 + 0.5 * math.sin(t * 16), look=(-1, 0))
        hx, hy = head_pos(wx, MG + 4, 0.82, w_face, "crouch")
        cxx = lerp(wx - 80, hx - 10, ease(u))
        P.trdelnik(c, cxx, lerp(MG - 24, hy, ease(u)), cake_s * 0.7, ang=0.0, length=1.0 - 0.1 * u)
    elif t < T("m_bong", 0.4):
        # head stuck in the cake: wobbly blind walking, then the proud "hat"
        hat = t >= T("m_hat")
        if T("m_eat", 0.75) <= t < T("m_hat"):
            sway = smooth(t, [(T("m_eat", 0.8), wx), (T("m_eat", 0.85), wx - 30), (T("m_eat", 0.95), wx + 30),
                              (T("m_stuck"), wx - 20), (T("m_stuck", 0.6), wx + 20), (T("m_hat"), wx)], 0.3)
            face = -1 if int(t * 1.6) % 2 else 1
            kitty(c, tl, t, "whiskers", sway, MG + 4, 0.82, face, "walk", walk=t * 9, eyes="closed")
            hx, hy = head_pos(sway, MG + 4, 0.82, face, "walk")
            c.push(hx, hy, 1.0, flip=face < 0)
            P.trdelnik(c, 6, 0, cake_s * 0.62 * 1.0, ang=0.15 * math.sin(t * 5))
            c.pop()
        else:
            kitty(c, tl, t, "whiskers", wx, MG + 4, 0.82, w_face, "sit", eyes="happy", look=(-1, 0))
            hx, hy = head_pos(wx, MG + 4, 0.82, w_face, "sit")
            P.trdelnik(c, hx - 2, hy - 18, 0.9, vertical=True)
    elif t < T("m_bong", 0.75):
        # the bell! Whiskers leaps sky-high and the cake shoots off towards the clock
        u = tl.prog("m_bong", t, 0.4, 0.75)
        kitty(c, tl, t, "whiskers", wx, MG + 4 + arc_y(u, 120), 0.82, w_face, "leap", eyes="wide")
        hx, hy = head_pos(wx, MG + 4 + arc_y(u, 120), 0.82, w_face, "leap")
        dx, dy = tower_pt(240, -905)
        cx_ = lerp(hx, dx, ease(u))
        cy_ = lerp(hy - 20, dy, u) + arc_y(u, 160)
        P.trdelnik(c, cx_, cy_, 0.9 - 0.5 * u, ang=t * 14)
    else:
        # hiding behind Luna, trembling
        kitty(c, tl, t, "whiskers", lx - 70, MG + 2, 0.8, 1, "crouch", eyes="wide", look=(1, -1),
              head_dy=2 * math.sin(t * 30))
        shiver(c, lx - 30, MG - 60, t)
    if T("m_bong", 0.3) <= t < T("m_bong", 0.95):
        sc = screen(c)
        # 'DING!' burst by the skeleton
        bx, by = tower_pt(215, -760)
        sc.text(bx - camx - 60, by - 40, "DING!", 30, (255, 236, 120), stroke=3)
        c = sc
    c = screen(c)
    shade_bottom(c, tl, t, 0.5)
    return c


# =================================================================== clock (the Orloj)

CW, CH = 1800, 1900
CX, CB, CS = 900, 1760, 0.8          # tower position in the clock world
CG = 1790                            # ground line for the cast
LEDGE = (CX + 215 * CS, CB - 712 * CS)
SIT = (CX + 290 * CS, CB - 712 * CS)     # where Whiskers sits on the wide ledge
DOOR = (CX + 240 * CS, CB - 850 * CS)    # bottom-centre of the little door


def clock_bg():
    def make():
        c = Canvas(sky(CW, CH, [(0, (120, 160, 214)), (0.6, (200, 216, 238)), (1, (230, 234, 244))]), size=(CW, CH))
        D.cloud(c, 300, 300, 1.4, (250, 250, 255))
        D.cloud(c, 1500, 220, 1.2, (250, 250, 255))
        rng = np.random.default_rng(41)
        # tall houses either side
        for x0, x1, seed in ((-20, 560, 1), (1240, CW + 20, 2)):
            x = x0
            k = seed
            while x < x1:
                w = rng.uniform(140, 200)
                P.house(c, x, CB, w, rng.uniform(420, 600), P.WALLS[k % len(P.WALLS)], rng, lit=0.2,
                        roof_h=rng.uniform(80, 120))
                x += w - 2
                k += 1
        c.rect(0, CB, CW, CH, (200, 192, 184), ol=None)
        for r in range(7):
            y = CB + 10 + r * 22
            off = (r % 2) * 20
            for xx in range(-40 + off, CW, 40):
                c.ellipse(xx, y, 17, 8, mix((210, 202, 194), (176, 168, 160), rng.random()), ol=(156, 148, 140), w=1)
        for k in range(20):
            c.ellipse(rng.uniform(0, CW), rng.uniform(CB + 4, CB + 30), rng.uniform(20, 60), 5, P.SNOW, ol=None)
        P.orloj_tower(c, CX, CB, CS)
        P.fir(c, 300, CB + 10, 1.6, lights=P.BULBS)
        P.fir(c, 1500, CB + 10, 1.6, lights=P.BULBS)
        return c.img
    return cached("clockbg", make)


def crowd(c, t, y, bounce=0.0, n=9, x0=420, x1=1400):
    rng = np.random.default_rng(9)
    cols = [(190, 150, 120), (150, 150, 160), (210, 170, 110), (120, 110, 100), (230, 220, 210), (170, 120, 90)]
    for k in range(n):
        px = lerp(x0, x1, k / max(1, n - 1)) + rng.uniform(-30, 30)
        P.kid_back(c, px, y + rng.uniform(0, 30), rng.uniform(0.8, 1.0), cols[k % len(cols)], kind=k,
                   ears=int(rng.integers(3)), t=t, bounce=bounce)


def clock(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["clock"]
    keys_cx = [(s0, 900), (T("k_narr", 0.85), 900), (T("k_stop", 1), 900), (T("k_door"), 900),
               (T("k_door", 0.6), 1000), (T("k_next"), 1000), (T("k_smile"), 1080), (T("k_smile", 1), 1080),
               (T("k_brave", 0.6), 960), (T("k_fix", 1), 960), (T("k_climb", 0.3), 1050), (T("k_climb", 1), 1050)]
    keys_cy = [(s0, 1152), (T("k_narr", 0.85), 1152), (T("k_stop", 1), 1400), (T("k_door"), 1400),
               (T("k_door", 0.6), 1260), (T("k_next"), 1300), (T("k_smile"), 1140), (T("k_smile", 1), 1140),
               (T("k_brave", 0.6), 1400), (T("k_fix", 1), 1400), (T("k_climb", 0.3), 1330), (T("k_climb", 0.7), 1150),
               (T("k_climb", 1), 1120)]
    keys_z = [(s0, 1.3), (T("k_narr", 0.85), 1.3), (T("k_stop", 1), 0.74), (T("k_door"), 0.74),
              (T("k_door", 0.6), 0.9), (T("k_next"), 0.85), (T("k_smile"), 1.35), (T("k_smile", 1), 1.35),
              (T("k_brave", 0.6), 0.74), (T("k_fix", 1), 0.74), (T("k_climb", 0.3), 0.85), (T("k_climb", 1), 1.15)]
    z = smooth(t, keys_z, 0.4)
    x0, y0 = cam_box(smooth(t, keys_cx, 0.4), smooth(t, keys_cy, 0.4), z, CW, CH)
    c = world_view(clock_bg(), x0, y0, z)
    # the golden hand creeps to one minute to noon -- then sticks
    hand = lerp(-0.16, -0.03, ease(tl.prog("k_narr", t, 0.0, 0.85)))
    if t >= T("k_narr", 0.85):
        hand = -0.03 + 0.012 * math.sin((t - T("k_narr", 0.85)) * 30) * math.exp(-(t - T("k_narr", 0.85)) * 3)
    door = 1.0 if T("k_climb", 0.72) <= t < T("k_climb", 0.97) else 0.0
    point = T("k_door", 0.3) <= t < T("k_door", 1.0)
    orloj_parts(c, tl, t, CX, CB, CS, hand=hand, door=door,
                bones_kw=dict(eyes="happy" if T("k_smile", 0.5) <= t else ("closed" if T("k_dear") <= t < T("k_dear", 0.2) else "open"),
                              wave=1.0 if point or T("k_climb", 0.5) <= t < T("k_climb", 0.8) else 0.0,
                              nod=1.0 if T("k_noshow") <= t < T("k_noshow", 1) else 0.0))
    # a puff of sugar from the little door when the clock jams
    if T("k_narr", 0.85) <= t < T("k_stop", 0.6):
        u = tl.prog("k_narr", t, 0.85, 1.0) * 0.4 + tl.prog("k_stop", t, 0.0, 0.6) * 0.6
        rng = np.random.default_rng(3)
        for k in range(14):
            a = rng.uniform(0, math.tau)
            r = 60 * u * rng.uniform(0.5, 1.2)
            c.circle(DOOR[0] + math.cos(a) * r, DOOR[1] - 40 + math.sin(a) * r, 5 * (1 - u) + 1, (255, 250, 236), w=1)
    if point:
        sparkles(c, DOOR[0], DOOR[1] - 44, t, r=50, n=6, col=(255, 240, 150))
    # the friends down on the square
    k_y = CG
    puppet(c, tl, t, 880, k_y - 4, 0.62, 1, eyes="wide" if T("k_noshow", 0.6) <= t < T("k_where") else "open",
           arms_up=1.0 if T("k_noshow", 0.7) <= t < T("k_where") else 0.0)
    kitty(c, tl, t, "luna", 760, k_y, 0.7, 1, "sit", look=(1, -1) if t < T("k_where") else (1, 0))
    if t < T("k_climb"):
        scared = t < T("k_brave", 0.5)
        if T("k_fix") <= t:
            kitty(c, tl, t, "whiskers", 1000, k_y, 0.72, 1, "stand", look=(1, -1), eyes="open")
        elif T("k_where") <= t < T("k_flew", 1):
            kitty(c, tl, t, "whiskers", 1000, k_y, 0.72, -1, "sit", eyes="wide" if t >= T("k_flew") else "open",
                  look=(-1, 0) if t < T("k_flew") else (1, -1))
        else:
            kitty(c, tl, t, "whiskers", 1000, k_y, 0.72, 1, "crouch" if scared else "sit", eyes="wide",
                  look=(1, -1), head_dy=1.5 * math.sin(t * 30) if scared else 0)
            if scared and T("k_next") <= t:
                shiver(c, 1030, k_y - 50, t)
    else:
        # the climb: square -> lower ledge -> beside Mr Bones -> in through the little door
        pts = [(0.0, (1000, k_y)), (0.3, (CX + 215 * CS, CB - 500 * CS)), (0.62, SIT), (0.75, SIT),
               (0.85, (DOOR[0] + 10, DOOR[1])), (1.0, (DOOR[0] + 10, DOOR[1]))]
        u = tl.prog("k_climb", t)
        for (u0, p0), (u1, p1) in zip(pts, pts[1:]):
            if u <= u1:
                f = (u - u0) / max(1e-6, u1 - u0)
                x = lerp(p0[0], p1[0], ease(f))
                y = lerp(p0[1], p1[1], ease(f)) + (arc_y(f, 60) if u1 <= 0.62 else 0)
                break
        pose = "leap" if u < 0.62 and 0.05 < (u % 0.31) < 0.27 else ("crouch" if u < 0.62 else "walk")
        if u < 0.85:
            face = 1 if u < 0.62 else -1
            kitty(c, tl, t, "whiskers", x, y, 0.6 if u > 0.3 else lerp(0.72, 0.6, u / 0.3), face, pose,
                  walk=t * 10 if pose == "walk" else 0.0, eyes="open", look=(1, -1))
    crowd(c, t, CG + 90, bounce=0.0)
    c = screen(c)
    shade_bottom(c, tl, t, 0.4)
    return c


# =================================================================== gears (inside the clock)

GA, RA = (640, 330), 170
GB, RB2 = (900, 560), 120
MESH = (GA[0] + RA * 0.749, GA[1] + RA * 0.663)
BEAM = 548


def gears_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (40, 30, 34)), (0.6, (76, 52, 44)), (1, (54, 38, 36))]))
        # the back of the big dial, glowing with daylight
        c.glow(1060, 300, 360, 360, (255, 236, 190), (76, 52, 44), steps=14)
        c.circle(1060, 300, 250, (120, 160, 200), w=4)
        c.circle(1060, 300, 236, (150, 190, 226), ol=None)
        c.ellipse(1060, 380, 220, 150, (226, 170, 110), ol=None)
        c.ellipse(1060, 420, 180, 110, (110, 90, 100), ol=None)
        for k in range(24):
            a = k * math.tau / 24
            c.circle(1060 + math.cos(a) * 236, 300 + math.sin(a) * 236, 7, P.GOLD_D, ol=None)
        for k in range(12):
            a = k * math.tau / 12
            c.line([(1060, 300), (1060 + math.cos(a) * 236, 300 + math.sin(a) * 236)], (110, 140, 180), 2, cap=False)
        # light beams
        mask = Image.new("L", c.img.size, 0)
        md = ImageDraw.Draw(mask)
        for k in range(3):
            y = 160 + k * 120
            md.polygon([(880 * SS, y * SS), (880 * SS, (y + 50) * SS), (0, (y + 260) * SS), (0, (y + 120) * SS)],
                       fill=40)
        mask = mask.filter(ImageFilter.GaussianBlur(14 * SS))
        c.img.paste(Image.new("RGB", c.img.size, (255, 230, 170)), (0, 0), mask)
        # wooden frame: posts and beams
        for x in (90, 460, 1220):
            c.rect(x - 16, 0, x + 16, H, P.WOOD_D, w=2)
        c.rect(0, 70, W, 96, P.WOOD_D, w=2)
        # chains and the pendulum weights
        for x in (200, 330):
            for k in range(14):
                c.ellipse(x, 100 + k * 18, 5, 9, (150, 140, 120), w=1.5)
            c.rect(x - 16, 360, x + 16, 430, (90, 86, 90), w=2, r=4)
        return c.img
    return cached("gearsbg", make)


def gears(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["gears"]
    c = Canvas(gears_bg().copy())
    run = max(0.0, t - T("g_turn", 0.2))
    stuck_jit = 0.02 * math.sin(t * 25) if t < T("g_turn", 0.2) else 0.0
    spin = run * 0.6 + stuck_jit
    # small gears behind
    P.gear(c, 300, 230, 80, spin * 2.1, teeth=10, col=(200, 160, 70))
    P.gear(c, 420, 470, 62, -spin * 2.7, teeth=9, col=(200, 160, 70))
    P.gear(c, 1150, 610, 90, -spin * 1.9, teeth=11)
    # the two big wheels
    P.gear(c, GA[0], GA[1], RA, spin, teeth=18)
    P.gear(c, GB[0], GB[1], RB2, -spin * RA / RB2 + 0.08, teeth=13)
    # the beam Whiskers walks along
    c.rect(-10, BEAM, 820, BEAM + 26, P.WOOD, w=2.5)
    c.rect(-10, BEAM + 26, 820, BEAM + 40, P.WOOD_D, ol=None)
    # the chimney cake, wedged between the teeth, getting shorter as Whiskers eats
    eat = tl.prog("g_munch", t, 0.05, 0.95)
    if eat < 1:
        P.trdelnik(c, MESH[0], MESH[1], 0.9, ang=0.65, length=max(0.08, 1.0 - eat))
        if t >= T("g_munch"):
            rng = np.random.default_rng(int(t * 8))
            for k in range(6):
                c.circle(MESH[0] + rng.uniform(-30, 30), MESH[1] + rng.uniform(0, 80), 2.5, (255, 248, 230), ol=None)
    # Whiskers
    wx = smooth(t, [(s0, 80), (T("g_look", 1), 380), (T("g_there", 1), 560), (T("g_born", 1), 700), (s1, 700)])
    walking = T("g_look") <= t < T("g_born", 1)
    if t < T("g_munch") or t >= T("g_turn"):
        happy = t >= T("g_turn", 0.4)
        if happy:
            kitty(c, tl, t, "whiskers", 700, BEAM, 0.8, 1, "sit", eyes="happy", look=(1, -1))
            sparkles(c, MESH[0], MESH[1], t, r=60, n=6, k=0.8)
        else:
            moving = walking and abs(smooth(t + 0.05, [(s0, 80), (T("g_look", 1), 380), (T("g_there", 1), 560),
                                                       (T("g_born", 1), 700)]) - wx) > 0.5
            kitty(c, tl, t, "whiskers", wx, BEAM, 0.8, 1, "walk" if moving else "stand",
                  walk=wx / 12 if moving else 0.0, look=(1, -1),
                  eyes="wide" if T("g_there") <= t < T("g_there", 0.4) else "open")
    else:
        kitty(c, tl, t, "whiskers", 700, BEAM, 0.8, 1, "stand", eyes="happy", head_dy=-10 + 4 * math.sin(t * 14),
              mouth=0.4 + 0.5 * abs(math.sin(t * 12)))
    # warm lantern glow on the left
    c.glow(140, 140, 70, 70, (255, 220, 140), (76, 52, 44), steps=6)
    c.rect(126, 120, 154, 160, P.LIGHT, w=2, r=4)
    return c


# =================================================================== noon (the clock strikes; the puppet show)

def theatre_bg():
    def make():
        bg = market_bg().crop((160 * SS, 0, 160 * SS + W * SS, H * SS))
        bg = Image.blend(bg, Image.new("RGB", bg.size, (60, 50, 70)), 0.25)
        c = Canvas(bg)
        P.fir(c, 120, 620, 2.0, lights=P.BULBS)
        P.fir(c, 1170, 620, 2.0, lights=P.BULBS)
        P.puppet_theatre(c, 640, 720, 1.0)
        return c.img
    return cached("theatrebg", make)


def noon(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["noon"]
    if t < T("n_show"):
        z = smooth(t, [(s0, 0.74), (T("n_narr", 0.3), 1.0), (T("n_parade", 1), 1.0), (T("n_thanks", 0.4), 1.35),
                       (T("n_laugh", 1), 1.35)], 0.4)
        cx = smooth(t, [(s0, 900), (T("n_narr", 0.3), 960), (T("n_parade", 1), 960), (T("n_thanks", 0.4), 1110),
                        (T("n_laugh", 1), 1110)], 0.4)
        cy = smooth(t, [(s0, 1400), (T("n_narr", 0.3), 1060), (T("n_parade", 1), 1060), (T("n_thanks", 0.4), 1110),
                        (T("n_laugh", 1), 1110)], 0.4)
        x0, y0 = cam_box(cx, cy, z, CW, CH)
        c = world_view(clock_bg(), x0, y0, z)
        par_u = tl.prog("n_narr", t, 0.1, 1.0) * 0.5 + tl.prog("n_parade", t, 0.0, 0.8) * 0.5
        shut = 1.0 - ease(tl.prog("n_strike", t, 0.6, 1.0)) + ease(tl.prog("n_parade", t, 0.8, 1.0))
        parade = par_u if 0 < par_u < 1 or T("n_narr") <= t < T("n_parade", 0.8) else None
        ringing = t < T("n_narr", 1.0)
        crow = 1.0 if T("n_parade", 0.8) <= t < T("n_thanks", 0.3) else 0.0
        laugh = T("n_laugh") <= t < T("n_laugh", 1)
        orloj_parts(c, tl, t, CX, CB, CS, hand=(t - T("n_strike")) * 0.002, shutters=min(1.0, shut), parade=parade,
                    crow=crow, ring=1.0 if ringing else 0.0, cal=(t - s0) * 0.01,
                    bones_kw=dict(eyes="happy" if ringing or laugh or t >= T("n_round") else "open", laugh=laugh))
        # Whiskers on the ledge beside Mr Bones
        w_eyes = "happy" if t < T("n_thanks") or laugh or t >= T("n_round", 0.6) else "open"
        kitty(c, tl, t, "whiskers", SIT[0] + 6, SIT[1], 0.6, -1, "sit", eyes=w_eyes, look=(-1, -0.3),
              mouth=(0.4 + 0.4 * math.sin(t * 13)) if laugh else tl.mouth("whiskers", t))
        if T("n_thanks") <= t < T("n_thanks", 1):
            hearts(c, SIT[0], SIT[1] - 90, t, 0.7)
        if T("n_strike") <= t < T("n_narr", 1.0):
            sc = screen(c)
            bx, by = LEDGE
            sc.text((bx - x0) * z - 70, (by - 150 - y0) * z, "DING!", 28, (255, 236, 120), stroke=3)
        crowd(c, t, CG + 90, bounce=1.0)
        c = screen(c)
        shade_bottom(c, tl, t, 0.4)
        return c
    # ---- the puppet show
    c = Canvas(theatre_bg().copy())
    curtain = ease(tl.prog("n_curtain", t, 0.0, 0.7)) * (1 - ease(tl.prog("n_end", t, 0.2, 1.0)))
    stage = 588
    if curtain > 0.05:
        # Kasparek presents the play; puppet Whiskers marches into a cardboard clock with a cake
        bow = ease(tl.prog("n_bye", t, 0.3, 0.7)) * (1 - ease(tl.prog("n_bye", t, 0.7, 1.0)))
        puppet(c, tl, t, 500, stage, 0.75, 1, wave=1.0 if T("n_bye") <= t < T("n_bye", 0.3) or T("n_story") <= t < T("n_story", 0.2) else 0.0,
               bow=bow, eyes="happy" if t >= T("n_play") else "open", bar=True)
        # the cardboard clock prop
        c.rect(740, stage - 210, 820, stage, (176, 166, 158), w=2)
        c.poly([(734, stage - 210), (780, stage - 250), (826, stage - 210)], P.GOTHIC_D, w=2)
        P.orloj_dial(c, 780, stage - 150, 32, t, hand=(t - T("n_play")) * 3 if t >= T("n_play", 0.5) else 0)
        play = tl.prog("n_play", t)
        px = lerp(600, 760, ease(min(1, play * 1.6)))
        if play < 0.7:
            P.puppet_cat(c, px, stage, 0.75, t, walk=t * 8 if 0 < play < 0.6 else 0.0)
            P.trdelnik(c, 720, stage - 12, 0.5, ang=0.0)
        else:
            P.puppet_cat(c, 770, stage - 60, 0.6, t)   # peeking out of the clock
        P.puppet_bones(c, 880, stage, 0.55, t)
    P.puppet_curtains(c, 640, 720, 1.0, curtain)
    # the audience: little animals and our two cats in the front row
    laugh = T("n_play", 0.4) <= t < T("n_play", 1.0)
    for k, (px, col, ears) in enumerate(((360, (190, 150, 120), 2), (520, (150, 150, 160), 1), (700, (230, 220, 210), 0),
                                         (860, (210, 170, 110), 1), (1020, (120, 110, 100), 2))):
        P.kid_back(c, px, 790, 1.15, col, kind=k, ears=ears, t=t, bounce=1.0 if laugh else 0.0)
    kitty(c, tl, t, "luna", 120, 730, 0.95, 1, "sit", eyes="happy" if laugh or t >= T("n_bye") else "open",
          look=(1, -1))
    w_eyes = "happy" if laugh or t >= T("n_bye") else "open"
    kitty(c, tl, t, "whiskers", 230, 735, 1.0, 1, "sit", eyes=w_eyes, look=(1, -1))
    if T("n_play", 0.5) <= t < T("n_bye"):
        hearts(c, 260, 600, t, 0.8)
    c = screen(c)
    shade_bottom(c, tl, t, 0.45)
    return c


# =================================================================== home

def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    if t < T("h_sill"):
        cam = lerp(RW - W, 300, (t - s0) / max(1e-6, T("h_sill") - s0))
        c = Canvas(night_river_bg().crop((int(cam * SS), 0, int(cam * SS) + W * SS, H * SS)))
        ripples(c, t, RB + 20, H, 40, seed=5, col=(100, 120, 180), drift=-60)
        c.tint = ((30, 36, 90), 0.3)
        P.barge(c, 700, 640, 0.78, -1, t, trees=False, lantern=1.0)
        # (mirrored barge: riders placed by hand)
        D.cat(c, 760, 616, D.LUNA, 0.6, -1, "sleep", t=t + 1, seed=1.3)
        D.cat(c, 640, 618, D.WHISKERS, 0.62, -1, "sleep", t=t, mouth=0)
        c.tint = None
        D.zzz(c, 620, 560, t)
        P.snowfall(c, t, seed=3, n=50, speed=26)
        return c
    c = room_frame(tl, t, fire=0.45)
    c.tint = ((30, 36, 90), 0.12)
    SY = 372
    kitty(c, tl, t, "luna", 850, SY, 0.8, 1, "sit", eyes="happy" if t >= T("h_lick") else "open", look=(1, 0))
    pip_x = 940
    gift = t >= T("h_gift", 0.3)
    D.mouse(c, pip_x, SY, 1.0, 1, t, mouth=tl.mouth("pip", t),
            eyes="happy" if gift else "open", proud=T("h_pip") <= t < T("h_pip", 1),
            hop=abs(math.sin(t * 8)) * 6 if T("h_gift", 0.6) <= t < T("h_noon") else 0)
    if gift:
        u = ease(tl.prog("h_gift", t, 0.3, 0.7))
        P.trdelnik(c, lerp(1010, 978, u), SY, 0.42, vertical=True, steam=0.6, t=t)
        if t < T("h_noon"):
            sparkles(c, lerp(1010, 978, u), SY - 26, t, r=22, n=4, k=0.8)
    if t < T("h_noon", 0.6):
        kitty(c, tl, t, "whiskers", 1040, SY, 0.8, -1, "sit", eyes="happy" if T("h_lick") <= t else "open",
              look=(-1, 0.3))
    else:
        D.cat(c, 1046, SY, D.WHISKERS, 0.75, -1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
        D.zzz(c, 1010, SY - 70, t)
    c.tint = None
    zk = ease(tl.prog("h_end", t, 0.0, 0.6))
    w = lerp(800, 640, zk)
    h = w * H / W
    cx, cy = lerp(860, 930, zk), lerp(310, 320, zk)
    box = tuple(int(round(v * SS)) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    c = Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))
    k = ease(tl.prog("h_end", t, 0.3, 0.55))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 40 * k, mix((250, 228, 190), (240, 170, 60), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "chimney": chimney, "barge": barge, "bridge": bridge, "market": market,
               "clock": clock, "gears": gears, "noon": noon, "home": home}

CONTINUOUS = {"clock"}
EXTRA_CUTS = ["n_show", "h_sill"]
