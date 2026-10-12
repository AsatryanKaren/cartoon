"""Venice -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in sync
with the speech. Static backgrounds are drawn once and cached; wide backgrounds
are cropped by a moving camera.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.montblanc.props import shade_bottom
from films.venice import props as P

SEED = {"whiskers": 0.0, "luna": 1.3, "vetra": 2.6, "pip": 2.1, "bepi": 3.3}
SUNSET = ((255, 130, 90), 0.16)
NIGHT = ((30, 36, 90), 0.3)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def view(bg, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    return Canvas(bg.crop((x, y, x + W * SS, y + H * SS)))


def paste_layer(c, layer, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    part = layer.crop((x, y, x + W * SS, y + H * SS))
    c.img.paste(part, (0, 0), part)


def rgba(w, h):
    return Canvas(Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)), size=(w, h))


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


def zoom(c, cx, cy, z, wmin):
    """Move the camera in: z=0 full frame, z=1 a box of width wmin centred near (cx, cy)."""
    if z <= 0.001:
        return c
    w = lerp(W, wmin, z)
    h = w * H / W
    x0 = clamp(lerp(0, cx - w / 2, z), 0, W - w)
    y0 = clamp(lerp(0, cy - h / 2, z), 0, H - h)
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def crop(c, x0, y0, w):
    h = w * H / W
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def overlay(c, col, alpha):
    if alpha <= 0.003:
        return c
    return Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha)))


# ------------------------------------------------------------------ the cast

def luna_bell(tl, t):
    """Luna's bell through the film: gold, then none, then the new glass one."""
    if t < tl.t("b_pop", 0.2):
        return "gold"
    if t < tl.t("m_ring", 0.28):
        return None
    return "glass"


RINGS = [("m_ring", 0.2), ("m_ring", 0.6), ("m_sings", 0.9), ("f_lift", 0.6), ("h_ring", 0.1), ("h_ring", 0.45),
         ("h_end", 0.1)]


def ring_amount(tl, t):
    k = 0.0
    for eid, f in RINGS:
        t0 = tl.t(eid, f) - 0.15
        if t >= t0:
            k = max(k, math.exp(-(t - t0) * 2.5))
    return k


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    hd = kw.get("head_dy", 0.0)
    if who == "luna":
        bell = kw.pop("bell", luna_bell(tl, t))
        D.cat(c, x, y, P.LUNA_NOBELL, s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
        if pose not in ("sleep", "swim"):
            P.collar(c, x, y, s, face, pose, walk, hd, bell=bell, t=t, ring=ring_amount(tl, t))
    elif who == "vetra":
        D.cat(c, x, y, P.NONNA, s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
        P.nonna_extras(c, x, y, s, face, pose, walk, hd)
    else:
        D.cat(c, x, y, D.WHISKERS, s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", ox=0.0, **kw):
    """Draw a character walking along x keyframes (world x; drawn at x - ox); faces the way it moves."""
    x = smooth(t, keys) - ox
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth("pip", t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        kw.pop("hop", None)
        D.mouse(c, x, y, s, face, t, walk=(x + ox) / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "bepi":
        mouth = kw.pop("mouth", tl.mouth("bepi", t))
        P.egret(c, x, y, s, face, t, mouth=mouth, walk=(x + ox) / 14 if moving else 0.0, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kitty(c, tl, t, who, x, y, s, face, pose, walk=(x + ox) / 12 if moving else 0.0, **kw)
    return x


def mouth_point(x, y, s, face, pose, walk=0.0, head_dy=0.0):
    hx, hy = P.head_pos(pose, walk, head_dy)
    return x + face * (hx + 17) * s, y + (hy + 18) * s


def bepi_rowing(c, tl, t, gx, gy, gs, gface=1, speed=1.0, mouth=None, eyes="open", sing=0.0, laugh=False,
                rowing=True, hands_up=False, wave=0.0):
    """Bepi standing on the stern of a gondola at (gx, gy), rowing."""
    bx = gx - gface * 176 * gs
    by = gy - 46 * gs + 2.5 * math.sin(t * 2.2)
    s = gs * 0.95
    ph = t * 2.4 * speed
    sw = math.sin(ph) if rowing else 0.0
    hx_l, hy_l = 34 + 10 * sw, -136
    m = tl.mouth("bepi", t) if mouth is None else mouth
    if wave > 0:
        P.egret(c, bx, by, s, gface, t, mouth=m, eyes=eyes, hands=None, wave=wave, laugh=laugh)
    else:
        hands = (hx_l, hy_l)
        P.egret(c, bx, by, s, gface, t, mouth=m, eyes=eyes, hands=hands, laugh=laugh)
        x0, y0 = bx + gface * hx_l * s, by + hy_l * s
        ang = math.radians(62 + 8 * sw)
        tipx = x0 + gface * math.cos(ang) * 230 * s
        tipy = y0 + math.sin(ang) * 230 * s
        tipx -= gface * 40 * s * (1 + sw)
        P.oar(c, x0, y0, tipx, tipy)
    if sing > 0.02:
        hx, hy = P.egret_head(gface, bx, by, s)
        P.notes(c, hx + gface * 40, hy - 10, t, sing)
    return bx, by


def ripples(c, t, y0, y1, n=40, seed=1, speed=30.0, col=P.WATER_L, drift=0.0, xmin=0, xmax=W, lw=2.0):
    """Animated short highlight dashes on water."""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = rng.uniform(xmin, xmax)
        y = rng.uniform(y0, y1)
        ln = rng.uniform(14, 40) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        ph = rng.uniform(0, math.tau)
        k = 0.5 + 0.5 * math.sin(t * 1.8 + ph)
        xx = (x - drift * t + 6 * math.sin(t * 0.9 + ph)) % (xmax - xmin + 80) + xmin - 40
        if k > 0.2:
            c.line([(xx - ln * k / 2, y), (xx + ln * k / 2, y)], col, lw, cap=False)


def splash(c, x, y, k, size=1.0, seed=3):
    """Water splash: k = 0 (impact) .. 1 (gone)."""
    if not 0 <= k < 1:
        return
    rng = np.random.default_rng(seed)
    a = 1 - k
    for i in range(14):
        ang = math.radians(rng.uniform(200, 340))
        v = rng.uniform(120, 260) * size
        px = x + math.cos(ang) * v * k
        py = y + math.sin(ang) * v * k * 1.2 + 300 * k * k * size
        c.circle(px, py, rng.uniform(4, 9) * size * (0.4 + a), (210, 238, 250), w=1.5)
    c.ellipse(x, y, (40 + 90 * k) * size, (10 + 14 * k) * size * a + 2, (190, 230, 245), w=2)
    if k < 0.5:
        u = k / 0.5
        h = 90 * size * math.sin(math.pi * u)
        c.poly([(x - 30 * size, y), (x - 14 * size, y - h), (x, y - h * 0.6), (x + 14 * size, y - h),
                (x + 30 * size, y)], (210, 238, 250), w=2)


def bubbles(c, x, y, t, k=1.0, seed=2):
    rng = np.random.default_rng(seed)
    for i in range(6):
        u = (t * 0.9 + i / 6) % 1.0
        c.circle(x + rng.uniform(-24, 24) + 4 * math.sin(t * 5 + i), y - 60 * u, (3 + 4 * rng.random()) * k,
                 (220, 245, 255), w=1.5)


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


def sky(w, h, stops):
    return D.gradient(w * SS, h * SS, stops)


DAY_SKY = [(0, (110, 176, 236)), (0.55, (196, 228, 250)), (1, (226, 240, 252))]
GOLD_SKY = [(0, (98, 130, 200)), (0.35, (236, 170, 150)), (0.62, (255, 210, 150)), (1, (255, 226, 170))]
SUNSET_SKY = [(0, (70, 70, 150)), (0.3, (200, 110, 140)), (0.55, (250, 150, 100)), (0.68, (255, 196, 120)),
              (1, (255, 210, 140))]


# =================================================================== Grand Canal (title)

CANAL_BASE = 452        # waterline of the far bank


def far_bank(c, x0, x1, base, seed, scale=1.0, lit=None):
    rng = np.random.default_rng(seed)
    walls = [(232, 160, 120), (240, 206, 150), (226, 130, 116), (244, 226, 200), (214, 150, 150),
             (236, 186, 120), (200, 120, 100)]
    x = x0
    while x < x1:
        w = rng.uniform(110, 210)
        h = rng.uniform(170, 290)
        c.push(x, base, scale)
        P.palazzo(c, 0, 0, w, h, walls[int(rng.integers(len(walls)))], rng, lit=lit)
        c.pop()
        x += (w + rng.uniform(-2, 6)) * scale


def water_band(c, x0, x1, y0, y1, top=P.WATER, bottom=P.WATER_D, n=12):
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        c.rect(x0, lerp(y0, y1, u0), x1, lerp(y0, y1, u1) + 1, mix(top, bottom, u0), ol=None)


def title_bg():
    def make():
        c = Canvas(sky(W, H, GOLD_SKY))
        c.glow(1000, 330, 260, 200, (255, 236, 190), (255, 214, 156), steps=10)
        c.circle(1000, 330, 46, (255, 240, 200), ol=None)
        # Santa Maria della Salute far right-ish: dome on the skyline
        c.push(1060, CANAL_BASE, 1.0)
        c.rect(-90, -150, 90, 0, (240, 230, 214), w=2.5)
        c.rect(-60, -210, 60, -150, (240, 230, 214), w=2.5)
        pts = [(80 * math.cos(a), -210 - 90 * math.sin(a)) for a in np.linspace(0, math.pi, 20)]
        c.poly(pts, (220, 216, 210), w=2.5)
        c.rect(-14, -330, 14, -298, (240, 230, 214), w=2)
        c.poly([(-14, -330), (0, -350), (14, -330)], (200, 196, 190), w=2)
        for k in range(5):
            c.rect(-80 + k * 36, -130, -64 + k * 36, -20, (90, 80, 100), w=1.5, r=8)
        c.pop()
        far_bank(c, -20, 960, CANAL_BASE, 5, 0.85)
        far_bank(c, 1160, W + 40, CANAL_BASE, 9, 0.8)
        water_band(c, 0, W, CANAL_BASE, H, (240, 186, 140), (80, 120, 150))
        # sun reflection
        for k in range(10):
            y = CANAL_BASE + 14 + k * 24
            c.rect(1000 - 40 + k * 3, y, 1000 + 40 - k * 3, y + 5, (255, 236, 190), ol=None)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    ripples(c, t, CANAL_BASE + 20, H, 50, seed=4, col=(255, 226, 180))
    # mooring poles
    for px, col in ((120, (40, 80, 170)), (172, (40, 80, 170)), (1160, (200, 50, 60)), (1210, (200, 50, 60))):
        P.mooring_pole(c, px, 640, 300, col)
    s0, s1 = tl.scenes["title"]
    gx = lerp(220, 860, (t - s0) / (s1 - s0))
    gy = 620
    c.tint = ((255, 160, 100), 0.12)
    P.gondola(c, gx, gy, 0.95, 1, t)
    kitty(c, tl, t, "luna", gx - 10, gy - 36, 0.62, 1, "sit", mouth=0, look=(1, -1), bell="gold")
    kitty(c, tl, t, "whiskers", gx + 60, gy - 36, 0.66, -1, "sit", mouth=0, eyes="happy")
    bepi_rowing(c, tl, t, gx, gy, 0.95, 1, mouth=0.3 + 0.3 * math.sin(t * 3), sing=0.8, eyes="happy")
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(640, 104 - 30 * (1 - k), "Whiskers and the", 44, mix((240, 200, 160), (255, 255, 245), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(640, 186, "SINGING GLASS", 24 + 52 * k2, mix((240, 200, 160), (255, 236, 150), k2), stroke=5 * k2)
    if k2 > 0.9:
        sparkles(c, 640, 186, t, r=260, n=8, k=k2)
    return c


# =================================================================== bell (home, morning)

RADIO = (300, 600)
HOLE = (600, 520)
BELL_REST = (930, 614)


def window_view():
    """The view out of the window: meadow hills under a morning sky (320 x 260)."""
    def make():
        c = Canvas(sky(320, 260, [(0, (120, 190, 245)), (1, (205, 235, 255))]), size=(320, 260))
        c.circle(250, 60, 30, (255, 222, 90), ol=None)
        D.cloud(c, 90, 90, 0.6)
        c.poly([(0, 200), (80, 176), (170, 196), (260, 170), (320, 186), (320, 260), (0, 260)], (130, 196, 110),
               ol=None)
        c.poly([(0, 230), (120, 214), (320, 226), (320, 260), (0, 260)], (110, 180, 96), ol=None)
        return c.img
    return cached("winview", make)


def draw_window(c, extra=None):
    """Repaint the window panes (with `extra(c)` drawn in window-local coordinates) and the frame."""
    sub = Canvas(window_view().copy(), size=(320, 260))
    if extra:
        extra(sub)
    c.img.paste(sub.img, (760 * SS, 110 * SS))
    c.rect(756, 106, 1084, 374, None, w=8)
    c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
    c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
    c.rect(740, 370, 1100, 392, (255, 250, 240), r=4)


def room_bg():
    def make():
        c = Canvas(MF.room(False).copy())
        c.rect(HOLE[0] - 24, HOLE[1] - 50, HOLE[0] + 24, HOLE[1] + 4, (46, 34, 40), r=23)
        # a little shelf with a framed photo of Luna's bell (keepsake)
        return c.img
    return cached("roombg", make)


def yarn(c, x, y, r=16, rot=0.0):
    c.circle(x, y - r, r, (220, 70, 90), w=2.5)
    for k in range(3):
        a = rot + k * 1.1
        c.arc(x + math.cos(a) * 4, y - r + math.sin(a) * 4, r * 0.7, r * 0.5, math.degrees(a), math.degrees(a) + 140,
              (250, 140, 150), 2)


def radio_bubble(c, x, y, k, t):
    """A dreamy round picture of Venice above the radio while it talks."""
    if k <= 0.01:
        return
    r = 120 * ease(k)
    for i, (dx, dy, rr) in enumerate(((30, 150, 8), (14, 128, 13))):
        c.circle(x + dx * k, y + dy * k - 20, rr * k, (255, 255, 255), w=2)
    sub = Canvas(sky(240, 240, GOLD_SKY), size=(240, 240))
    sub.push(120, 150, 0.5)
    for px, w_, h_, col in ((-230, 90, 160, (232, 160, 120)), (-140, 80, 200, (240, 206, 150)),
                            (120, 90, 180, (226, 130, 116)), (205, 70, 150, (244, 226, 200))):
        sub.rect(px, -h_, px + w_, 0, col, w=2)
        for wy in range(-h_ + 30, -20, 50):
            P.gothic_window(sub, px + w_ / 2, wy + 30, 8, 30)
    sub.pop()
    sub.rect(0, 150, 240, 240, P.WATER, ol=None)
    ripples(sub, t, 160, 236, 12, seed=8, xmax=240)
    P.gondola(sub, 100 + 10 * math.sin(t), 196, 0.32, 1, t)
    P.glass_bell(sub, 160, 34, 1.5, ang=0.25 * math.sin(t * 3), shine=0.5 + 0.5 * math.sin(t * 4))
    sparkles(sub, 160, 70, t, r=40, n=5)
    m = Image.new("L", sub.img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, 240 * SS - 1, 240 * SS - 1], fill=255)
    sz = max(2, int(2 * r * SS))
    c.img.paste(sub.img.resize((sz, sz)), (int((x - r) * SS), int((y - r) * SS)), m.resize((sz, sz)))
    c.circle(x, y, r, None, w=4)


def bell(tl, t):
    T = tl.t
    c = Canvas(room_bg().copy())
    s0 = tl.scenes["bell"][0]
    # the window (balloon rising over the meadow during b_window / b_ball)
    bal = None
    if t >= T("b_window"):
        u = ease(tl.prog("b_window", t, 0.0, 1.0))
        bal = (190, lerp(330, 200, u) - 6 * tl.prog("b_ball", t) - 10 * tl.prog("b_run", t))

    def extra(sub):
        if bal:
            P.balloon(sub, bal[0], bal[1], 0.26, t, flame=1.0 if T("b_window", 0.25) < t < T("b_window", 0.6) else 0,
                      sign=False)
    draw_window(c, extra)
    # radio
    on = 1.0 if t >= T("b_sad", 0.5) else 0.0
    talk = tl.mouth("radio", t)
    P.radio(c, RADIO[0], RADIO[1], 1.0, on=on, t=t, talk=talk)
    radio_bubble(c, RADIO[0] + 20, 300, tl.prog("b_radio", t, 0.0, 0.15) * (1 - tl.prog("b_go", t, 0.0, 0.3)), t)

    # --- the yarn ball and Luna playing
    yk = [(s0, 200), (T("b_play", 0.5), 760), (T("b_play", 1.0), 560), (T("b_narr", 1), 620),
          (T("b_pop", 0.1), 700), (T("b_pop", 0.45), -120)]
    if t < T("b_pop", 0.5):
        yx = smooth(t, yk, 0.15)
        yarn(c, yx, 640, 16, -yx / 16)
    bell_state = luna_bell(tl, t)
    # bell flying off and rolling to rest under the window
    if T("b_pop", 0.2) <= t:
        u = tl.prog("b_pop", t, 0.2, 0.42)
        if u < 1:
            bx = lerp(760, BELL_REST[0], u)
            by = lerp(560, BELL_REST[1], u) + arc_y(u, 90) - abs(math.sin(u * 9)) * 18 * (1 - u)
            c.circle(bx, by - 8, 8, (250, 210, 70), w=2)
        elif t < T("b_pop", 0.78):
            c.circle(BELL_REST[0], BELL_REST[1] - 8, 8, (250, 210, 70), w=2)
        elif not (T("b_pop", 0.78) <= t < T("b_look", 0.3)):
            P.squashed_bell(c, BELL_REST[0], BELL_REST[1], 2.0)
            if T("b_squash") <= t < T("b_mouse"):
                sparkles(c, BELL_REST[0], BELL_REST[1] - 10, t, r=26, n=4, k=0.5, col=(255, 230, 150))

    # Luna
    if t < T("b_pop", 0.5):
        lk = [(s0, 60), (T("b_play", 0.55), 690), (T("b_play", 1.0), 540), (T("b_narr", 0.5), 640),
              (T("b_pop", 0.12), 700), (T("b_pop", 0.5), -160)]
        pose = "stand"
        if T("b_narr", 0.3) <= t < T("b_pop", 0.05):
            pose = "sit"
        lx = smooth(t, lk, 0.15)
        hop = abs(math.sin(t * 7)) * 22 if T("b_play") <= t < T("b_play", 1) else 0
        if T("b_pop", 0.12) <= t < T("b_pop", 0.24):
            u = tl.prog("b_pop", t, 0.12, 0.24)
            D.cat(c, lerp(700, 610, u), 612 + arc_y(u, 70), P.LUNA_NOBELL, 0.9, -1, "leap", t=t, seed=1.3)
            P.collar(c, lerp(700, 610, u), 612 + arc_y(u, 70), 0.9, -1, "leap", bell=bell_state)
        else:
            actor(c, tl, t, "luna", lk, 612 - hop, 0.9, face=1, pose=pose,
                  eyes="happy" if T("b_narr") <= t < T("b_narr", 1) else "open", tail=math.sin(t * 6))
        if T("b_narr", 0.3) <= t < T("b_narr", 1):
            sparkles(c, 640 + 0.9 * 24, 612 - 0.9 * 70, t, r=20, n=4, k=0.8, col=(255, 230, 120))
    elif t >= T("b_look", 0.65):
        lk = [(T("b_look", 0.65), -120), (T("b_seen"), 600), (T("b_squash"), 600), (T("b_squash", 0.4), 800)]
        sad = T("b_squash", 0.3) <= t < T("b_go")
        lpose = "sit" if T("b_squash", 0.5) <= t < T("b_window", 0.3) else "stand"
        leyes = "open"
        if T("b_sad") <= t < T("b_radio"):
            leyes = "closed"
        if T("b_you") <= t < T("b_love"):
            leyes = "wide"
        lface = 1
        look = (0.3, 0.8) if sad else (1, 0)
        if T("b_radio") <= t < T("b_go"):
            lface, look = -1, (1, -0.6)
        if t >= T("b_window", 0.2):
            look = (1, -1)
        if t >= T("b_run", 0.15):
            lk = lk + [(T("b_run", 0.15), 800), (T("b_run", 0.6), -200)]
        actor(c, tl, t, "luna", lk, 612, 0.9, face=lface, pose=lpose, eyes=leyes, look=look,
              head_dy=8 if sad and lpose == "sit" else 0)

    # Whiskers
    wy_sill = 372
    if t < T("b_pop", 0.6):
        D.cat(c, 960, wy_sill, D.WHISKERS, 0.8, 1, "sleep", t=t)
        D.zzz(c, 1010, 300, t)
    elif t < T("b_pop", 0.78):
        u = tl.prog("b_pop", t, 0.6, 0.78)
        D.cat(c, lerp(960, BELL_REST[0] - 30, u), lerp(wy_sill, 614, u * u) + arc_y(u, 40), D.WHISKERS, 0.85, 1,
              "sleep", t=t)
    elif t < T("b_look"):
        land = tl.prog("b_pop", t, 0.78, 0.86)
        sq = 1 - 0.25 * math.sin(math.pi * land)
        if T("b_oof", 0.55) <= t:
            kitty(c, tl, t, "whiskers", BELL_REST[0] - 30, 614, 0.85, 1, "sit", look=(0.5, 1))
        else:
            D.cat(c, BELL_REST[0] - 30, 614, D.WHISKERS, 0.85, 1, "sleep", t=t, squash=sq,
                  mouth=tl.mouth("whiskers", t))
            if land < 1:
                for k in range(5):
                    a = k * 1.25 + t * 6
                    c.circle(BELL_REST[0] - 20 + 50 * math.cos(a), 560 + 14 * math.sin(a), 4, (255, 230, 90), w=1.5)
    else:
        wk = [(T("b_look"), BELL_REST[0] - 30), (T("b_look", 0.3), 1030)]
        if t >= T("b_run", 0.2):
            wk = wk + [(T("b_run", 0.2), 1030), (T("b_run", 0.75), -200)]
        face = -1
        eyes = "open"
        look = (1, 0)
        if t < T("b_seen"):
            eyes = "wide"
            look = (1, 1)
            if T("b_look", 0.4) <= t < T("b_look", 0.75):
                face = 1 if (t * 2.2) % 1 < 0.5 else -1
                look = (1, 0)
        if T("b_mouse") <= t < T("b_pip"):
            look = (-1, 0) if (t * 1.5) % 1 < 0.5 else (1, -0.5)
        if T("b_pip") <= t < T("b_sad"):
            eyes = "wide"
        if T("b_sad") <= t < T("b_radio"):
            look = (0.2, 1)
        if T("b_radio") <= t < T("b_go"):
            look = (1, -0.6)
        if T("b_love") <= t < T("b_window"):
            eyes = "happy"
        if t >= T("b_window", 0.2):
            face, look = 1, (1, -1)
        pose = "sit" if T("b_squash") <= t < T("b_go") else "stand"
        actor(c, tl, t, "whiskers", wk, 614, 0.85, face=face, pose=pose, eyes=eyes, look=look,
              head_dy=-6 if T("b_go") <= t < T("b_go", 1) else 0)

    # Pip
    if t >= T("b_pip"):
        pk = [(T("b_pip"), HOLE[0]), (T("b_sad"), HOLE[0]), (T("b_sad", 0.45), RADIO[0] + 80),
              (T("b_window"), RADIO[0] + 80), (T("b_window", 0.7), 915)]
        rise = ease(tl.prog("b_pip", t, 0.0, 0.2))
        proud = (T("b_pip") <= t < T("b_pip", 1)) or (T("b_ball") <= t < T("b_ball", 1)) or t >= T("b_run", 0.5)
        pface = -1
        if t >= T("b_window", 0.7):
            pface = 1 if t < T("b_run") else -1
        actor(c, tl, t, "pip", pk, HOLE[1] + 24 + 20 * (1 - rise), 1.0, face=pface, proud=proud,
              eyes="happy" if t >= T("b_run", 0.5) else "open")
    # a gentle push-in while the bell is found to be squashed
    z = ease(tl.prog("b_squash", t, 0.0, 0.3)) * (1 - ease(tl.prog("b_pip", t, 0.0, 0.4)))
    w = lerp(1000, 720, z)
    h = w * H / W
    cx = lerp(740, 860, z)
    x0, y0 = clamp(cx - w / 2, 0, W - w), H - h - lerp(0, 60, z)
    return crop(c, x0, y0, w)


# =================================================================== balloon flight

PW = 4400        # panorama width
VEN_X = 3640     # Venice in the panorama


def pano_bg():
    def make():
        c = Canvas(sky(PW, H, DAY_SKY), size=(PW, H))
        rng = np.random.default_rng(6)
        for _ in range(16):
            D.cloud(c, rng.uniform(0, PW), rng.uniform(60, 330), rng.uniform(0.6, 1.3))
        # home hills
        pts = [(x, 560 + 30 * math.sin(x / 260) + 16 * math.sin(x / 90)) for x in range(0, 1500, 30)]
        c.poly(pts + [(1500, H), (0, H)], (130, 196, 110), ol=None)
        c.poly([(x, 620 + 20 * math.sin(x / 200 + 1)) for x in range(0, 1500, 30)] + [(1500, H), (0, H)],
               (110, 180, 96), ol=None)
        # the Alps
        from films.montblanc import props as MB
        for k, (px, w_, h_) in enumerate(((1350, 600, 260), (1650, 700, 380), (1980, 640, 300), (2250, 760, 420),
                                         (2560, 600, 300), (2820, 560, 220))):
            MB.peak(c, px, 640, w_, h_, seed=k, cap=0.5)
        for k, (px, w_, h_) in enumerate(((1500, 500, 200), (1850, 520, 230), (2400, 520, 200), (2700, 480, 160))):
            MB.peak(c, px, 680, w_, h_, rock=(96, 110, 120), seed=k + 9, cap=0.35)
        c.poly([(1150, H), (1250, 650), (2900, 660), (3050, H)], (90, 140, 100), ol=None)
        # plain and lagoon
        c.poly([(2900, 640), (3100, 560), (PW, 560), (PW, H), (2900, H)], (150, 196, 120), ol=None)
        c.poly([(3050, H), (3150, 590), (PW, 580), (PW, H)], P.LAGOON, ol=None)
        water_band(c, 3150, PW, 590, H, P.LAGOON, (70, 140, 176))
        # Venice: an island city floating on the lagoon
        c.push(VEN_X, 640, 1.0)
        c.ellipse(0, 10, 420, 56, (226, 214, 190), w=3)
        rows = [(-20, 0.55, 380), (6, 0.7, 400), (34, 0.85, 360)]
        walls = [(232, 160, 120), (240, 206, 150), (226, 130, 116), (244, 226, 200), (214, 150, 150)]
        for ry, sc, half in rows:
            x = -half
            while x < half:
                w_ = rng.uniform(26, 50) * sc
                h_ = rng.uniform(28, 54) * sc
                col = walls[int(rng.integers(len(walls)))]
                c.rect(x, ry - h_, x + w_, ry, col, w=1.5)
                c.poly([(x - 2, ry - h_), (x + w_ / 2, ry - h_ - 10 * sc), (x + w_ + 2, ry - h_)], (190, 90, 70), w=1.5)
                x += w_
        # the Grand Canal S-curve
        c.line([(-360, 24), (-200, 40), (-60, 18), (80, 44), (240, 26), (380, 40)], (90, 160, 190), 7, cap=False)
        P.campanile(c, 60, 0, 0.3)
        for dx, r in ((-40, 16), (-10, 20), (20, 16)):
            c.poly([(dx + r * math.cos(a), -20 - r * math.sin(a)) for a in np.linspace(0, math.pi, 10)],
                   (150, 160, 178), w=2)
        c.pop()
        for k in range(6):
            P.gondola(c, VEN_X - 300 + k * 140, 700 + (k % 2) * 10, 0.12, 1 if k % 2 else -1, bob=False)
        return c.img
    return cached("pano", make)


def meadow_bg():
    def make():
        c = Canvas(sky(W, H, DAY_SKY))
        D.cloud(c, 200, 120, 1.0)
        D.cloud(c, 1000, 90, 0.8)
        c.poly([(x, 520 + 30 * math.sin(x / 220)) for x in range(0, W + 40, 40)] + [(W, H), (0, H)],
               (140, 200, 120), ol=None)
        # the cats' cottage
        c.push(170, 560, 1.0)
        c.rect(-110, -150, 110, 0, (250, 228, 190), w=3)
        c.poly([(-130, -150), (0, -240), (130, -150)], (196, 90, 70), w=3)
        c.rect(-70, -110, -20, -60, (120, 180, 230), w=2.5)
        c.rect(30, -90, 76, 0, (150, 96, 60), w=2.5)
        c.rect(60, -230, 84, -180, (170, 80, 60), w=2)
        c.pop()
        c.rect(0, 580, W, H, (120, 186, 100), ol=None)
        for x in range(320, W, 60):
            c.rect(x, 548, x + 8, 600, (200, 170, 130), w=1.5)
        c.line([(320, 560), (W, 560)], (200, 170, 130), 5, cap=False)
        c.line([(320, 580), (W, 580)], (200, 170, 130), 5, cap=False)
        rng = np.random.default_rng(2)
        for _ in range(60):
            D.flower(c, rng.uniform(0, W), rng.uniform(620, H), [(250, 220, 90), (255, 255, 255), (240, 120, 160)][
                int(rng.integers(3))], 0.7)
        return c.img
    return cached("meadow", make)


def cats_in_basket(tl, t, wh_eyes="open", lu_eyes="open", look=(1, 0), wface=1, lface=1, lmouth=None, wmouth=None):
    def fn(c):
        kitty(c, tl, t, "luna", -30, -50, 0.72, lface, "sit", eyes=lu_eyes, look=look,
              **({} if lmouth is None else {"mouth": lmouth}))
        kitty(c, tl, t, "whiskers", 28, -48, 0.75, wface, "sit", eyes=wh_eyes, look=look,
              **({} if wmouth is None else {"mouth": wmouth}))
    return fn


def flight(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["flight"]
    if t < T("v_narr"):
        # take-off from the meadow
        c = Canvas(meadow_bg().copy())
        u = tl.prog("v_lift", t, 0.5, 1.0)
        by = 610 - 900 * ease(u) ** 1.4
        flame = 1.0 if (T("v_lift", 0.1) < t < T("v_lift", 0.3) or T("v_lift", 0.55) < t < T("v_lift", 0.8)) else 0
        aboard = t >= T("v_lift", 0.42)
        P.balloon(c, 820, by, 0.72, t, flame, inside=cats_in_basket(tl, t, "wide", "happy", (0, -1)) if aboard else None)
        if not aboard:
            for who, x0, dl in (("luna", -120, 0.0), ("whiskers", -260, 0.06)):
                a, b = T("v_lift", 0.05 + dl), T("v_lift", 0.3 + dl)
                if t < b:
                    actor(c, tl, t, who, [(a, x0), (b, 720)], 610, 0.8)
                else:
                    u2 = tl.prog("v_lift", t, 0.3 + dl, 0.42)
                    D.cat(c, lerp(720, 820, u2), 610 + arc_y(u2, 90) - 40 * u2,
                          P.LUNA_NOBELL if who == "luna" else D.WHISKERS, 0.75, 1, "leap", t=t)
        # Pip waving from the fence
        D.mouse(c, 380, 546, 1.0, 1, t, eyes="happy", proud=True, hop=abs(math.sin(t * 6)) * 6)
        return c
    # flying south: one long panorama
    cam = smooth(t, [(T("v_narr"), 0), (T("v_venice", 0.55), PW - W), (s1, PW - W)], 0.6)
    c = view(pano_bg(), cam)
    bx = 430 + 30 * math.sin(t * 0.6)
    by = 330 + 10 * math.sin(t * 1.1)
    if t >= T("v_land"):
        u = tl.prog("v_land", t, 0.15, 1.0)
        bx = lerp(430, 700, u)
        by = 330 + 700 * ease(u) ** 1.6
    flame = 1.0 if (T("v_alps", 0.55) < t < T("v_alps", 0.75) or T("v_land", 0.15) < t < T("v_land", 0.3)) else 0.0
    looking_down = t >= T("v_look", 0.5)
    weyes = "closed" if T("v_down") <= t < T("v_look", 0.4) else ("wide" if looking_down else "open")
    if T("v_canals") <= t < T("v_land"):
        weyes = "open"
    look = (1, 1) if looking_down else (1, 0)
    lface = 1
    if T("v_look") <= t < T("v_look", 1):
        lface = -1
    P.balloon(c, bx, by, 0.55, t, flame, inside=cats_in_basket(tl, t, weyes, "happy" if looking_down else "open",
                                                               look, 1, lface))
    # gulls near Venice
    if cam > PW - W - 400:
        for k in range(3):
            gx = (900 + k * 120 + t * 40 * (1 + k * 0.2)) % (W + 200) - 100
            gy = 200 + 40 * k + 10 * math.sin(t * 2 + k)
            f = math.sin(t * 8 + k)
            c.line([(gx - 18, gy - 8 * f), (gx, gy), (gx + 18, gy - 8 * f)], (250, 250, 250), 4)
            c.line([(gx - 18, gy - 8 * f), (gx, gy), (gx + 18, gy - 8 * f)], OUT, 1.5, cap=False)
    shade_bottom(c, tl, t, 0.45)
    # close-ups on the basket for the "don't look down" moment
    z = ease(tl.prog("v_down", t, 0.0, 0.25)) * (1 - ease(tl.prog("v_venice", t, 0.0, 0.25)))
    if z > 0:
        c = zoom(c, bx, by - 70, z, 560)
    return c


# =================================================================== St Mark's Square

SQW = 2640
SQ_BASE = 520      # where the buildings meet the pavement
SQ_Y = 610         # feet line in the square
BALLOON_X = 190
STALL_X = 1280


def procuratie(c, x0, x1, base):
    """Arcaded building along the square (Procuratie)."""
    c.rect(x0, base - 230, x1, base, (240, 232, 214), w=3)
    for row, (y0, y1, wdt) in enumerate(((base - 220, base - 160, 14), (base - 150, base - 92, 14),
                                         (base - 80, base, 20))):
        x = x0 + 22
        while x < x1 - 12:
            c.rect(x - wdt, y0, x + wdt, y1, (100, 90, 100) if row == 2 else (80, 76, 96), w=1.5, r=wdt)
            x += 44
    c.rect(x0 - 4, base - 236, x1 + 4, base - 226, (220, 210, 190), w=2)


def san_giorgio(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-80, -60, 80, 0, (244, 238, 226), w=2)
    c.poly([(-50, -60), (0, -90), (50, -60)], (244, 238, 226), w=2)
    c.poly([(30 * math.cos(a), -90 - 34 * math.sin(a)) for a in np.linspace(0, math.pi, 10)], (200, 200, 206), w=2)
    c.rect(96, -150, 116, 0, BRICK_L, w=2)
    c.poly([(94, -150), (106, -184), (118, -150)], (104, 168, 136), w=2)
    c.pop()


BRICK_L = (200, 110, 86)


def square_bg():
    def make():
        c = Canvas(sky(SQW, H, DAY_SKY), size=(SQW, H))
        rng = np.random.default_rng(3)
        for _ in range(7):
            D.cloud(c, rng.uniform(0, SQW), rng.uniform(40, 200), rng.uniform(0.6, 1.1))
        # waterfront beyond the Piazzetta
        water_band(c, 1700, SQW, 470, SQ_BASE + 40, P.LAGOON, (80, 150, 180))
        san_giorgio(c, 2280, 474, 0.9)
        for k in range(4):
            P.mooring_pole(c, 1820 + k * 210, 540, 70, (40, 80, 170))
        for k in range(3):
            P.gondola(c, 1900 + k * 230, 548, 0.32, 1, bob=False)
        procuratie(c, -10, 330, SQ_BASE)
        P.basilica(c, 730, SQ_BASE, 1.0)
        P.doge_palace(c, 1230, SQ_BASE, 0.9, n=10)
        P.campanile(c, 1110, SQ_BASE + 20, 0.86)
        # pavement: pale stone with a white grid in perspective
        c.rect(0, SQ_BASE, SQW, H, (214, 204, 188), ol=None)
        for k in range(8):
            y = SQ_BASE + 6 + (k ** 1.6) * 6
            c.line([(0, y), (SQW, y)], (240, 234, 222), 3, cap=False)
        for x in range(-400, SQW + 400, 120):
            c.line([(x, SQ_BASE), (x + (x - SQW / 2) * 0.3, H)], (240, 234, 222), 3, cap=False)
        # the quay edge at the far right
        c.rect(1700, SQ_BASE + 36, SQW, SQ_BASE + 46, (200, 190, 176), w=2)
        P.column_lion(c, 1830, SQ_BASE + 40, 0.8)
        P.column_lion(c, 2110, SQ_BASE + 40, 0.8)
        for x in (520, 980, 1640):
            P.lamp_post(c, x, SQ_BASE + 50, 1.0)
        for x in (60, 1450, 1560):
            P.cafe_table(c, x, SQ_BASE + 64, 0.8)
        P.stall(c, STALL_X, SQ_Y - 10, 0.85)
        return c.img
    return cached("square", make)


def pigeon_flock(n, seed, x0, x1, y0, y1):
    rng = np.random.default_rng(seed)
    return [(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(0, 10), 1 if rng.random() < 0.5 else -1,
             rng.uniform(0.85, 1.15), rng.uniform(-1, 1)) for _ in range(n)]


FLOCK = pigeon_flock(46, 7, 120, 1900, SQ_Y - 40, H - 10)


def draw_pigeons(c, tl, t, cam, target=None, pull=0.0, fly=0.0, chase=None, extra_fly=0.0):
    """The square's pigeons. pull: 0..1 drifting toward `target` x; chase: (x, y) they swarm around."""
    T = tl.t
    items = []
    for i, (px, py, ph, face, s, jit) in enumerate(FLOCK):
        x, y = px, py
        f = 0.0
        if target is not None and pull > 0:
            k = clamp(pull * (1.2 - abs(px - target) / 2400))
            x = lerp(px, target + jit * 120 + (60 if px > target else -60), k)
            y = lerp(py, SQ_Y + 20 + jit * 30, k * 0.7)
            face = 1 if target > px else -1
        if chase is not None and fly > 0:
            ang = t * (3 + jit) + i
            rad = 60 + 120 * abs(jit)
            cx, cy = chase
            k = clamp(fly * 1.4 - (i % 7) * 0.05)
            x = lerp(x, cx + math.cos(ang) * rad - 80 - (i % 5) * 30, k)
            y = lerp(y, cy - 90 + math.sin(ang * 1.3) * 60 - (i % 4) * 20, k)
            f = k
            face = 1 if math.sin(ang) < 0 else -1
            face = 1 if k > 0.6 else face
        sx = x - cam
        if -60 < sx < W + 60:
            items.append((y, sx, face, s, ph, f))
    for y, sx, face, s, ph, f in sorted(items):
        peck = max(0.0, math.sin(t * 2.3 + ph * 3)) ** 3 if f < 0.3 else 0
        P.pigeon(c, sx, y, 1.15 * s, face, t, peck=peck, fly=f, seed=ph)
    if extra_fly > 0:
        for k in range(10):
            u = clamp(extra_fly * 1.3 - k * 0.04)
            gx = lerp(1300 - k * 60, 200 + k * 90, u)
            gy = lerp(-40 - k * 20, SQ_Y + 20 + (k % 3) * 30, ease(u))
            P.pigeon(c, gx, gy, 1.1, -1, t, fly=1.0 if u < 0.95 else 0.0, seed=k)


def square(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["square"]
    cam = smooth(t, [(s0, 0), (T("q_narr", 0.15), 0), (T("q_lots", 0.2), 420), (T("q_late", 1), 460),
                     (T("q_sniff"), 700), (T("q_swarm", 0.1), 700), (T("q_run", 0.8), SQW - W)], 0.5)
    c = view(square_bg(), cam)
    # balloon parked on the left
    land = ease(tl.prog("q_arrive", t, 0.0, 0.35))
    bxw = BALLOON_X
    by = lerp(SQ_Y - 300, SQ_Y, land)
    P.balloon(c, bxw - cam, by, 0.62, t, 0.0,
              inside=cats_in_basket(tl, t, "wide", "happy", (1, 0)) if t < T("q_arrive", 0.45) else None)
    # whiskers' route
    wk = [(T("q_arrive", 0.45), bxw + 40), (T("q_arrive", 0.9), 560), (T("q_lots", 1), 600),
          (T("q_smell", 0.3), 600), (T("q_smell", 1), 1160), (T("q_shoo", 1), 1160),
          (T("q_swarm", 0.12), 1180), (T("q_run", 0.9), SQW + 200)]
    lk = [(T("q_arrive", 0.5), bxw - 10), (T("q_arrive", 0.95), 440), (T("q_lots", 1), 470),
          (T("q_smell", 0.5), 470), (T("q_sniff", 1), 940), (T("q_swarm", 0.3), 960), (T("q_run", 1), SQW + 100)]
    wx = smooth(t, wk)
    # the doughnut
    has_d = T("q_roll", 0.55) <= t
    if T("q_roll", 0.0) <= t < T("q_roll", 0.55):
        u = tl.prog("q_roll", t, 0.0, 0.55)
        dx = lerp(STALL_X - 60, 1210, u)
        dy = lerp(SQ_Y - 96, SQ_Y + 4, min(1, u * 2.5)) - abs(math.sin(u * 8)) * 20 * (1 - u)
        P.fritola(c, dx - cam, dy, 12, u * 9)
    pull = ease(tl.prog("q_roll", t, 0.3, 1.0))
    fly = ease(tl.prog("q_shoo", t, 0.75, 1.0)) if t < T("q_swarm") else 1.0
    extra = tl.prog("q_lots", t, 0.0, 1.0) if t < T("q_roll") else 1.0
    if t < T("q_lots"):
        extra = 0.0
    draw_pigeons(c, tl, t, cam, target=1190 if t >= T("q_roll") else None, pull=pull,
                 fly=fly if t >= T("q_shoo") else 0.0, chase=(wx - 40, SQ_Y), extra_fly=0 if t >= T("q_shoo", 0.8) else extra)
    if t >= T("q_arrive", 0.45):
        lface = 1
        look = (1, 0)
        if T("q_late") <= t < T("q_late", 1):
            look = (1, -1)
        actor(c, tl, t, "luna", lk, SQ_Y + 4, 0.8, face=lface, look=look, ox=cam,
              eyes="happy" if T("q_narr") <= t < T("q_late") else "open")
        weyes = "open"
        hd = 0
        if T("q_smell") <= t < T("q_sniff", 1):
            weyes, hd = "closed", -8 + 3 * math.sin(t * 8)
        if T("q_roll", 0.6) <= t < T("q_shoo"):
            weyes = "happy"
        if t >= T("q_shoo", 0.8):
            weyes = "wide"
        wlook = (1, 0)
        wface = 1
        if T("q_shoo") <= t < T("q_shoo", 0.8):
            wface = -1
        actor(c, tl, t, "whiskers", wk, SQ_Y + 6, 0.85, face=wface, eyes=weyes, look=wlook, head_dy=hd, ox=cam)
        if has_d:
            v = (smooth(t + 0.05, wk) - smooth(t - 0.05, wk)) / 0.1
            face = wface if abs(v) < 20 else (1 if v > 0 else -1)
            moving = abs(v) > 20
            mx, my = mouth_point(wx - cam, SQ_Y + 6, 0.85, face, "walk" if moving else "stand", wx / 12 if moving else 0)
            P.fritola(c, mx + face * 4, my + 12, 11)
    shade_bottom(c, tl, t, 0.5)
    return c


# =================================================================== canal (quay, Rialto, lagoon)

CW = 3400
QUAY_TOP = 560
QUAY_X = 430
GOND_X, GOND_Y, GOND_S = 760, 640, 0.85


def canal_bg():
    def make():
        c = Canvas(sky(CW, H, DAY_SKY), size=(CW, H))
        rng = np.random.default_rng(11)
        for _ in range(8):
            D.cloud(c, rng.uniform(0, CW), rng.uniform(40, 170), rng.uniform(0.6, 1.0))
        far_bank(c, -30, CW + 30, CANAL_BASE, 21)
        water_band(c, 0, CW, CANAL_BASE, H, P.WATER, P.WATER_D)
        for k in range(12):
            x = 300 + k * 280 + rng.uniform(-40, 40)
            col = [(40, 80, 170), (200, 50, 60), (30, 130, 90)][k % 3]
            P.mooring_pole(c, x, CANAL_BASE + 16, 150, col)
            P.mooring_pole(c, x + 22, CANAL_BASE + 20, 130, col)
        return c.img
    return cached("canal", make)


def quay_layer():
    def make():
        c = rgba(CW, H)
        c.rect(-20, QUAY_TOP, QUAY_X, H + 10, (206, 196, 180), w=3)
        c.rect(-20, QUAY_TOP, QUAY_X + 6, QUAY_TOP + 14, (230, 222, 206), w=2.5)
        for y in range(QUAY_TOP + 34, H, 30):
            c.line([(-20, y), (QUAY_X, y)], (180, 170, 156), 2, cap=False)
            for x in range((y // 30) % 2 * 40, QUAY_X, 80):
                c.line([(x, y), (x, y + 30)], (180, 170, 156), 2, cap=False)
        c.rect(-20, 640, QUAY_X, 652, (120, 150, 110), ol=None)
        # a lamp and a flower pot on the quay
        P.lamp_post(c, 80, QUAY_TOP + 4, 1.0)
        return c.img
    return cached("quay", make)


def rialto_bg():
    def make():
        c = Canvas(sky(W, H, DAY_SKY))
        D.cloud(c, 260, 110, 0.9)
        D.cloud(c, 980, 80, 0.7)
        # distant palazzi seen through the arch
        far_bank(c, 160, 1120, 524, 31, 0.45)
        water_band(c, 0, W, 520, H, P.WATER, P.WATER_D)
        return c.img
    return cached("rialto_bg", make)


def rialto_front():
    def make():
        c = rgba(W, H)
        P.rialto(c, 640, 524, 1.0)
        rng = np.random.default_rng(41)
        P.palazzo(c, -40, 524, 230, 420, (226, 130, 116), rng)
        P.palazzo(c, 1090, 524, 230, 400, (240, 206, 150), rng)
        return c.img
    return cached("rialto_front", make)


def lagoon_bg(sunset=False):
    def make():
        stops = SUNSET_SKY if sunset else DAY_SKY
        c = Canvas(sky(W, H, stops))
        if sunset:
            c.glow(980, 380, 300, 160, (255, 230, 170), (255, 196, 130), steps=10)
            c.circle(980, 400, 50, (255, 236, 180), ol=None)
        else:
            D.cloud(c, 300, 120, 1.0)
            D.cloud(c, 900, 160, 0.7)
        top, bot = ((240, 160, 120), (90, 90, 140)) if sunset else (P.LAGOON, (60, 130, 170))
        water_band(c, 0, W, 430, H, top, bot)
        if sunset:
            # Venice skyline ahead with the bell tower
            c.tint = ((120, 60, 90), 0.35)
            far_bank(c, 700, W + 40, 432, 51, 0.4)
            P.campanile(c, 1040, 432, 0.42)
            for dx, r in ((900, 22), (940, 28), (980, 22)):
                c.poly([(dx + r * math.cos(a), 400 - r * math.sin(a)) for a in np.linspace(0, math.pi, 10)] +
                       [(dx - r, 432), (dx + r, 432)], (150, 140, 170), w=2)
            c.tint = None
        else:
            P.murano_isle(c, 1010, 434, 0.9)
            c.push(0, 0)
            far_bank(c, -20, 260, 432, 61, 0.3)
            c.pop()
        return c.img
    return cached(("lagoon", sunset), make)


def canal(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["canal"]
    wet = 1.0
    if t >= T("g_row"):
        wet = 1 - ease(tl.prog("g_row", t, 0.0, 1.0) * 0.5 + tl.prog("g_bridge", t) * 0.5)
    # ---------------------------------------------------------- B: the Rialto Bridge
    if T("g_rialto") <= t < T("g_quiet"):
        c = Canvas(rialto_bg().copy())
        ripples(c, t, 530, H, 40, seed=5)
        u = ease(tl.prog("g_bridge", t, 0.0, 0.9))
        if t < T("g_bridge"):
            u = 0
        lead = tl.prog("g_rialto", t) * 0.15 if t < T("g_bridge") else 0.15
        u = lerp(lead, 1.0, u)
        gx, gy = lerp(300, 640, u), lerp(705, 526, u)
        gs = lerp(1.0, 0.12, u ** 0.7)
        under = gy < 560

        def gond(c):
            P.gondola(c, gx, gy, gs, 1, t)
            kitty(c, tl, t, "luna", gx - 10 * gs, gy - 36 * gs, 0.62 * gs / 0.85, 1, "sit", look=(1, -1))
            kitty(c, tl, t, "whiskers", gx + 70 * gs, gy - 36 * gs, 0.66 * gs / 0.85, 1, "sit", wet=wet,
                  look=(1, -1), eyes="wide" if t >= T("g_bridge") else "open")
            bepi_rowing(c, tl, t, gx, gy, gs, 1, sing=1.0 if t < T("g_bridge", 0.7) else 0.0,
                        eyes="happy")
        if under:
            gond(c)
            paste_layer(c, rialto_front())
        else:
            paste_layer(c, rialto_front())
            gond(c)
        return c
    # ---------------------------------------------------------- C: the open lagoon
    if t >= T("g_quiet"):
        c = Canvas(lagoon_bg(False).copy())
        ripples(c, t, 440, H, 50, seed=6, col=(170, 220, 236), drift=60)
        gx = smooth(t, [(T("g_lagoon", 0.25), 600), (s1, 1500)])
        gy = 610
        P.gondola(c, gx, gy, 1.1, 1, t)
        lface = -1 if T("g_quiet") <= t < T("g_think", 1) else 1
        kitty(c, tl, t, "luna", gx + 10, gy - 40, 0.8, lface, "sit", look=(1, 0))
        weyes = "open"
        hd = 0
        if T("g_think") <= t < T("g_sing"):
            weyes, hd = "closed", 6
        if T("g_meow") <= t < T("g_lagoon", 0.5):
            weyes = "happy"
        kitty(c, tl, t, "whiskers", gx + 100, gy - 40, 0.84, 1 if t < T("g_think") else -1, "sit", wet=wet * 0.3,
              eyes=weyes, head_dy=hd, look=(1, 0.5) if t < T("g_sing") else (-1, 0))
        sing = 1.0 if (T("g_sing") <= t < T("g_lagoon", 0.6)) else 0.0
        bepi_rowing(c, tl, t, gx, gy, 1.1, 1, sing=sing, eyes="happy" if sing else "open")
        if T("g_meow") <= t < T("g_lagoon", 0.4):
            hx, hy = gx + 100 + 18 * 0.84 * -1, gy - 40 - 140 * 0.84
            P.notes(c, hx - 10, hy - 20, t * 1.6, 1.0, col=(255, 200, 150))
        # Bepi wincing at the meow
        return c
    # ---------------------------------------------------------- A: the quay
    cam = 0.0
    if t >= T("g_row"):
        cam = smooth(t, [(T("g_row", 0.15), 0), (T("g_rialto") + 1.0, 1300)], 0.4)
    c = view(canal_bg(), cam)
    ripples(c, t, CANAL_BASE + 20, H, 50, seed=3)
    gx = GOND_X + smooth(t, [(T("g_row", 0.15), 0), (T("g_rialto") + 1.0, 1300)], 0.4) - cam
    if t < T("c_hook"):
        gx += smooth(t, [(s0, 220), (T("c_leap", 0.6), 0)], 0.3)
    gy = GOND_Y
    paste_layer(c, quay_layer(), cam)
    # Whiskers' run, leap and splash
    WATER_X, WATER_Y = 560, 660
    whisk_drawn = False
    under = False
    if t < T("c_leap", 0.35):
        wk = [(s0, -120), (T("c_leap", 0.35), 360)]
        wx = actor(c, tl, t, "whiskers", wk, QUAY_TOP + 4, 0.85, eyes="wide")
        mx, my = mouth_point(wx, QUAY_TOP + 4, 0.85, 1, "walk", wx / 12)
        P.fritola(c, mx + 4, my + 12, 11)
        whisk_drawn = True
    elif t < T("c_leap", 0.55):
        u = tl.prog("c_leap", t, 0.35, 0.55)
        x, y = lerp(360, WATER_X, u), lerp(QUAY_TOP + 4, WATER_Y, u) + arc_y(u, 110)
        D.cat(c, x, y, D.WHISKERS, 0.85, 1, "leap", t=t, eyes="wide", mouth=0.6)
        whisk_drawn = True
    # pigeons that chased him wheel away -- and one steals the doughnut!
    if t < T("c_hook"):
        for k in range(8):
            u = tl.prog("c_leap", t, 0.0, 1.0)
            px = lerp(-200 - k * 50, 700 + k * 40, u) if u < 0.5 else lerp(300 + k * 60, 300 + k * 160, (u - 0.5) * 2)
            py = 470 + (k % 3) * 30 + 30 * math.sin(t * 3 + k) - (300 * (u - 0.5) * 2 if u > 0.5 else 0)
            P.pigeon(c, px, py, 1.1, 1, t, fly=1.0, seed=k)
        if T("c_leap", 0.55) <= t:
            u = tl.prog("c_leap", t, 0.55, 1.0) if t < T("c_blub") else 1.0
            u2 = tl.prog("c_blub", t) if t >= T("c_blub") else 0
            u3 = tl.prog("c_hook", t)
            fx = lerp(WATER_X + 30, 900, u2)
            fy = WATER_Y - 14 - 260 * ease(u2)
            if u2 > 0:
                P.pigeon(c, fx - 10, fy - 6, 1.3, 1, t, fly=1.0, seed=9)
            P.fritola(c, fx + 4, fy + 12, 11)
    if T("c_leap", 0.55) <= t < T("c_hook", 0.2):
        k = tl.prog("c_leap", t, 0.55, 0.95)
        splash(c, WATER_X, WATER_Y, k, 1.0)
        if t >= T("c_leap", 0.78):
            rise = ease(tl.prog("c_leap", t, 0.78, 0.95))
            D.cat(c, WATER_X - 20, WATER_Y + 20 * (1 - rise), D.WHISKERS, 0.85, 1, "swim", t=t, wet=1,
                  mouth=tl.mouth("whiskers", t), eyes="wide")
            bubbles(c, WATER_X + 10, WATER_Y - 30, t, 1.0 if t < T("c_hook") else 0)
            whisk_drawn = True
        else:
            bubbles(c, WATER_X, WATER_Y - 6, t, 0.8)
            under = True
    # water in front of a swimmer (hide the body)
    # gondola and Bepi
    P.gondola(c, gx, gy, GOND_S, 1, t)
    seat_w, seat_l = gx + 70 * GOND_S, gx - 10 * GOND_S
    sy = gy - 36 * GOND_S
    if T("c_hook", 0.2) <= t < T("c_hook", 0.7):
        u = tl.prog("c_hook", t, 0.2, 0.7)
        x, y = lerp(WATER_X - 20, seat_w, u), lerp(WATER_Y, sy, u) + arc_y(u, 120)
        D.cat(c, x, y, D.WHISKERS, 0.75, 1, "leap" if u < 0.9 else "sit", t=t, wet=1, eyes="wide")
        if u < 0.2:
            splash(c, WATER_X, WATER_Y, 0.3 + u, 0.6)
    elif t >= T("c_hook", 0.7):
        weyes = "open"
        wface = -1
        if T("c_bath") <= t < T("c_bath", 1):
            weyes = "happy"
        if t >= T("c_glass"):
            wface = 1
        kitty(c, tl, t, "whiskers", seat_w, sy, 0.66, wface, "sit", wet=wet, eyes=weyes, look=(1, 0))
    # Luna: arrives on the quay, then hops into the gondola
    if t >= T("c_leap", 0.4):
        if t < T("c_bepi", 0.6):
            lk = [(T("c_leap", 0.4), -120), (T("c_blub", 1), 330)]
            leyes = "wide" if t < T("c_fish") else "open"
            if T("c_bath") <= t < T("c_bepi"):
                leyes = "happy"
            actor(c, tl, t, "luna", lk, QUAY_TOP + 4, 0.8, eyes=leyes)
        elif t < T("c_bepi", 0.95):
            u = tl.prog("c_bepi", t, 0.6, 0.95)
            D.cat(c, lerp(330, seat_l, u), lerp(QUAY_TOP + 4, sy, u) + arc_y(u, 80), P.LUNA_NOBELL, 0.7, 1, "leap",
                  t=t, seed=1.3)
        else:
            lface = 1 if t < T("c_glass") else 1
            kitty(c, tl, t, "luna", seat_l, sy, 0.62, lface, "sit", look=(1, 0) if t < T("c_andiamo") else (-1, 0),
                  eyes="happy" if T("c_andiamo", 0.6) <= t else "open")
    # Bepi
    laugh = T("c_fish") <= t < T("c_fish", 1)
    rowing = t >= T("g_row") or t < T("c_leap", 0.6)
    sing = 1.0 if t >= T("g_row") else 0.0
    wave = 0.0
    if T("c_bepi") <= t < T("c_bepi", 0.6):
        wave = math.sin(math.pi * tl.prog("c_bepi", t, 0.0, 0.6))
    if T("c_hook", 0.05) <= t < T("c_hook", 0.75):
        # reach the oar down to scoop Whiskers out
        bx = gx - 176 * GOND_S
        by = gy - 46 * GOND_S
        P.egret(c, bx, by, GOND_S * 0.95, -1, t, mouth=0, eyes="wide", hands=(30, -130))
        u = tl.prog("c_hook", t, 0.05, 0.75)
        x0, y0 = bx - 30 * GOND_S, by - 130 * GOND_S * 0.95
        ex = lerp(WATER_X + 10, seat_w, ease(clamp((u - 0.2) / 0.5)))
        ey = lerp(WATER_Y + 10, sy + 10, ease(clamp((u - 0.2) / 0.5))) + arc_y(clamp((u - 0.2) / 0.5), 120)
        if u < 0.2:
            ex, ey = lerp(x0 - 60, WATER_X + 10, u / 0.2), lerp(y0 + 60, WATER_Y + 10, u / 0.2)
        P.oar(c, x0, y0, ex, ey)
    else:
        bepi_rowing(c, tl, t, gx, gy, GOND_S, 1, sing=sing, laugh=laugh, rowing=rowing, wave=wave,
                    eyes="happy" if laugh or sing else "open")
    z = ease(tl.prog("c_fish", t, 0.0, 0.4)) * (1 - ease(tl.prog("g_row", t, 0.0, 0.3)))
    if z > 0:
        c = zoom(c, gx - 60, gy - 150, z, 820)
    return c


# =================================================================== Murano workshop

FURN_X, FURN_Y = 900, 590
FLOOR = 600
DOOR = (1130, 250, 1250, 600)


def workshop_bg():
    def make():
        c = Canvas(bg=(170, 96, 66))
        # brick wall
        for row in range(0, 30):
            y = row * 22
            for k in range(-1, 40):
                x = k * 50 + (25 if row % 2 else 0)
                c.rect(x + 2, y + 2, x + 48, y + 20, mix((176, 100, 70), (150, 80, 56), ((k * 7 + row * 3) % 5) / 5),
                       ol=None)
        # plaster patches
        for x, y, rx, ry in ((200, 150, 120, 70), (640, 260, 90, 60), (1000, 90, 140, 50)):
            c.ellipse(x, y, rx, ry, (226, 196, 160), ol=None)
        # ceiling beams
        c.rect(0, 0, W, 40, (90, 60, 44), w=3)
        for x in range(60, W, 220):
            c.rect(x, 0, x + 30, 60, (110, 74, 52), w=2.5)
        # shelves of Murano glass
        rng = np.random.default_rng(5)
        cols = [(80, 170, 230), (240, 90, 120), (120, 210, 140), (250, 190, 70), (170, 120, 230), (240, 140, 60)]
        for sy in (190, 320):
            c.rect(40, sy, 560, sy + 12, (120, 80, 50), w=2.5)
            x = 64
            while x < 540:
                P.vase(c, x, sy, rng.uniform(0.7, 1.1), cols[int(rng.integers(len(cols)))], int(rng.integers(3)))
                x += rng.uniform(40, 64)
        # stone floor
        c.rect(0, FLOOR - 40, W, H, (150, 136, 124), ol=None)
        for y in range(FLOOR - 20, H, 36):
            c.line([(0, y), (W, y)], (126, 114, 104), 2, cap=False)
        # workbench with tools
        c.rect(570, 470, 700, 486, (110, 74, 52), w=2.5)
        c.rect(580, 486, 592, FLOOR - 10, (100, 66, 46), w=2)
        c.rect(678, 486, 690, FLOOR - 10, (100, 66, 46), w=2)
        P.furnace(c, FURN_X, FURN_Y, 1.0, t=0.0, heat=0.0)
        return c.img
    return cached("workshop", make)


def door_view(sunset):
    def make():
        x0, y0, x1, y1 = DOOR
        w, h = x1 - x0, y1 - y0
        c = Canvas(sky(w, h, SUNSET_SKY if sunset else DAY_SKY), size=(w, h))
        top, bot = ((240, 160, 120), (120, 100, 140)) if sunset else (P.LAGOON, (60, 130, 170))
        water_band(c, 0, w, h * 0.55, h, top, bot, n=6)
        if sunset:
            c.circle(w * 0.5, h * 0.5, 30, (255, 236, 180), ol=None)
        return c.img
    return cached(("door", sunset), make)


def glow_layer():
    def make():
        m = Image.new("L", (W * SS, H * SS), 0)
        ImageDraw.Draw(m).ellipse([(FURN_X - 300) * SS, (FURN_Y - 360) * SS, (FURN_X + 300) * SS, (FURN_Y + 80) * SS],
                                  fill=255)
        return m.filter(ImageFilter.GaussianBlur(70 * SS))
    return cached("glow", make)


def blowpipe(c, x0, y0, x1, y1, glob=0.0, hot=1.0):
    c.line([(x0, y0), (x1, y1)], OUT, 7)
    c.line([(x0, y0), (x1, y1)], (150, 150, 160), 3.5)
    if glob > 0:
        col = mix((160, 220, 240), (255, 170, 60), hot)
        c.circle(x1, y1, glob, col, w=2)
        c.circle(x1 - glob * 0.35, y1 - glob * 0.35, glob * 0.25, mix(col, (255, 255, 255), 0.6), ol=None)


def murano(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["murano"]
    c = Canvas(workshop_bg().copy())
    sunset = t >= T("m_ring")
    x0, y0, x1, y1 = DOOR
    c.img.paste(door_view(sunset), (x0 * SS, y0 * SS))
    c.rect(x0 - 10, y0 - 10, x1 + 10, y1, None, w=10)
    c.rect(x0 - 14, y0 - 14, x1 + 14, y0, (120, 80, 50), w=3)
    # warm flickering light from the furnace
    flick = 0.3 + 0.06 * math.sin(t * 11) + 0.04 * math.sin(t * 17.3)
    c.img.paste(Image.new("RGB", c.img.size, (255, 170, 80)), (0, 0), glow_layer().point(lambda v: int(v * flick)))
    c.d = ImageDraw.Draw(c.img)
    P.furnace(c, FURN_X, FURN_Y, 1.0, t=t, heat=1.0)
    # Bepi at the door at the end
    if t >= T("m_quick", 0.0):
        k = ease(tl.prog("m_quick", t, 0.0, 0.25))
        P.egret(c, lerp(1320, 1180, k), FLOOR + 20, 1.0, -1, t, mouth=tl.mouth("bepi", t), eyes="wide",
                wave=0.6 + 0.3 * math.sin(t * 8))
    # --- positions
    lk = [(s0, -150), (T("m_arrive", 0.8), 250), (T("m_truth"), 250), (T("m_truth", 0.6), 320), (T("m_help"), 320),
          (T("m_help", 0.6), 250)]
    wk = [(s0, -300), (T("m_arrive", 0.9), 400), (T("m_help", 0.3), 400), (T("m_help", 0.9), 430)]
    vk = [(s0, 760), (T("m_arrive", 0.7), 760), (T("m_welcome"), 700), (T("m_help"), 700), (T("m_help", 0.6), 1040),
          (T("m_shape"), 1040), (T("m_shape", 0.1), 760)]
    if t >= T("m_ring"):
        wk = wk + [(T("m_ring"), 430), (T("m_ring", 0.6), 440)]
    if t >= T("m_quick", 0.3):
        lk = lk + [(T("m_quick", 0.3), 250), (s1, 1300)]
        wk = wk + [(T("m_quick", 0.4), 440), (s1, 1300)]
    vx = smooth(t, vk)
    vface = 1 if (t < T("m_welcome") or T("m_blow") <= t < T("m_gently") or T("m_shape") <= t < T("m_there")) else -1
    blowing_v = t < T("m_welcome") or T("m_shape", 0.1) <= t < T("m_shape", 0.8)
    whisk_blow = T("m_help", 0.9) <= t < T("m_shape", 0.15)
    # Nonna Vetra
    kitty(c, tl, t, "vetra", vx, FLOOR + 10, 0.95, vface, "sit",
          eyes="wide" if T("m_gently") <= t < T("m_gently", 1) else ("happy" if T("m_there") <= t < T("m_ring") else "open"),
          head_dy=-8 * abs(math.sin(t * 10)) if T("m_gently") <= t < T("m_gently", 1) else 0)
    # the glass on its pipe
    glob_r = 0.0
    hot = 1.0
    if t < T("m_welcome"):
        spin = math.sin(t * 6) * 6
        blowpipe(c, vx + 40, FLOOR - 40, FURN_X - 60, FURN_Y - 110 + spin, 14, 1.0)
    elif t < T("m_help", 0.6):
        blowpipe(c, 560, FLOOR - 40, 700, 470, 0, 0)       # pipe resting on the bench
        c.circle(706, 466, 6, (200, 120, 60), w=1.5)
    # Whiskers blowing
    wx = smooth(t, wk)
    if whisk_blow:
        mx, my = mouth_point(wx, FLOOR + 10, 0.9, 1, "stand")
        u = tl.prog("m_blow", t, 0.0, 1.0)
        glob_r = 16 + 150 * ease(u) ** 1.2
        if t >= T("m_gently"):
            glob_r = 166 + 6 * math.sin(t * 9)
        if t >= T("m_shape"):
            glob_r = lerp(166, 30, ease(tl.prog("m_shape", t, 0.0, 0.15)))
        hot = 1 - 0.92 * ease(u)
        tipx = mx + 150 + glob_r * 0.9
        blowpipe(c, mx + 4, my + 2, tipx, my + 2, glob_r, hot)
    elif T("m_shape", 0.15) <= t < T("m_there", 0.5):
        u = tl.prog("m_shape", t, 0.15, 0.85)
        spin = math.sin(t * 9) * 8
        tip = (lerp(FURN_X - 40, vx + 150, ease(clamp((u - 0.6) / 0.4))), FURN_Y - 110 + spin * (1 - u))
        blowpipe(c, vx + 40, FLOOR - 40, tip[0], tip[1], 0 if u > 0.98 else 20, 1.0)
        if u > 0.98 or t >= T("m_there"):
            glow = 1 - ease(tl.prog("m_shape", t, 0.85, 1.0) * 0.5 + tl.prog("m_there", t) * 0.5)
            P.glass_bell(c, tip[0], tip[1] - 6, 1.6, glow=glow, shine=1 - glow)
            sparkles(c, tip[0], tip[1] + 30, t, r=46, n=6, k=1 - glow * 0.5)
    elif T("m_there", 0.5) <= t < T("m_ring", 0.3):
        # the bell floats over onto Luna's collar
        u = ease(tl.prog("m_ring", t, 0.0, 0.3)) if t >= T("m_ring") else 0
        lx_ = smooth(t, lk)
        tx, ty = lerp(vx + 150, lx_ + 0.95 * 24, u), lerp(FURN_Y - 116, FLOOR + 10 - 0.95 * 75, u)
        P.glass_bell(c, tx, ty, lerp(1.6, 0.42 * 0.95, u), shine=1.0)
        sparkles(c, tx, ty + 30, t, r=40, n=5)
    # Luna
    lx = smooth(t, lk)
    leyes = "open"
    if T("m_oh") <= t < T("m_help"):
        leyes = "happy"
    if T("m_blow") <= t < T("m_shape"):
        leyes = "wide"
    if T("m_ring", 0.2) <= t < T("m_quick"):
        leyes = "happy"
    lface = 1
    shake = 0.0
    if T("m_ring", 0.3) <= t < T("m_sings", 1):
        shake = 6 * math.sin(t * 20) * ring_amount(tl, t)
    actor(c, tl, t, "luna", lk, FLOOR + 10, 0.95, face=lface, eyes=leyes, look=(1, 0),
          head_dy=shake, pose="sit" if T("m_oh") <= t < T("m_help", 0.3) else "stand")
    if T("m_truth") <= t < T("m_help"):
        hearts(c, 330, FLOOR - 160, t, 1.0)
    if T("m_ring", 0.3) <= t < T("m_quick"):
        P.notes(c, lx + 40, FLOOR - 140, t, 0.8, col=(200, 240, 255))
    # Whiskers
    weyes = "open"
    wface = 1
    hd = 0
    if T("m_pause") <= t < T("m_me"):
        weyes, hd = "closed", 10
        wface = 1 if (t * 0.8) % 1 < 0.5 else -1
    if T("m_me") <= t < T("m_truth", 1):
        wface = -1
        hd = 6
        weyes = "open" if t < T("m_oh") else "happy"
    if whisk_blow:
        weyes = "closed" if t < T("m_gently") else "wide"
        wface = 1
    if T("m_ring") <= t:
        weyes = "happy"
    if T("m_quick") <= t < T("m_quick", 0.4):
        weyes = "wide"
    if whisk_blow:
        D.cat(c, wx, FLOOR + 10, D.WHISKERS, 0.9, 1, "stand", t=t, eyes=weyes, mouth=0.15,
              squash=1 + 0.06 * math.sin(t * 5))
        if t < T("m_gently"):
            for k in (0, 1):
                c.circle(wx + 0.9 * (70 + 14 * k), FLOOR + 10 - 0.9 * 70, 6 + 4 * math.sin(t * 6), (250, 150, 150), ol=None)
    else:
        actor(c, tl, t, "whiskers", wk, FLOOR + 10, 0.9, face=wface, eyes=weyes, head_dy=hd,
              pose="sit" if T("m_pause") <= t < T("m_truth", 1) else "stand")
    # heart-to-heart close-up
    z = ease(tl.prog("m_pause", t, 0.2, 0.6)) * (1 - ease(tl.prog("m_help", t, 0.0, 0.4)))
    c = zoom(c, 330, FLOOR - 100, z, 640)
    return c


# =================================================================== flood (acqua alta at sunset)

FLOOD_Y = 588      # water level in the square


def flood_layer():
    def make():
        c = rgba(SQW, H)
        water_band(c, 0, SQW, FLOOD_Y, H, (150, 140, 190), (70, 80, 140))
        # reflections of the buildings
        for x0, x1, col in ((-10, 330, (240, 226, 200)), (430, 1030, (236, 200, 120)), (1060, 1160, (200, 110, 86)),
                            (1230, 1680, (240, 196, 186))):
            for k in range(8):
                y = FLOOD_Y + 8 + k * 16
                c.rect(x0 + 10 + 6 * k, y, x1 - 10 - 6 * k, y + 4, mix(col, (150, 140, 190), 0.45 + 0.07 * k), ol=None)
        return c.img
    return cached("flood", make)


def flood(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["flood"]
    if t < T("f_narr"):
        # racing back across the lagoon at sunset
        c = Canvas(lagoon_bg(True).copy())
        ripples(c, t, 440, H, 60, seed=9, col=(255, 210, 170), drift=260)
        gx, gy = 560 + 20 * math.sin(t * 2), 620
        P.gondola(c, gx, gy, 1.0, 1, t)
        kitty(c, tl, t, "luna", gx - 10, gy - 36, 0.74, 1, "sit", look=(1, -0.5), eyes="wide")
        kitty(c, tl, t, "whiskers", gx + 80, gy - 36, 0.78, 1, "sit", look=(1, -0.5), eyes="wide")
        bepi_rowing(c, tl, t, gx, gy, 1.0, 1, speed=2.2, eyes="open")
        # bell tower bongs
        for k in range(3):
            u = ((t - s0) * 0.7 + k / 3) % 1.0
            c.arc(1040, 250, 30 + 60 * u, 20 + 40 * u, 200, 340, mix((255, 240, 200), (230, 150, 120), u), 3)
        for k in range(2):
            sx = (t * 400 + k * 640) % (W + 200) - 100
            c.line([(W - sx, 650 + k * 30), (W - sx + 80, 650 + k * 30)], (255, 230, 200), 3, cap=False)
        c.tint = None
        return c
    # the flooded square
    cam = smooth(t, [(T("f_narr"), SQW - W), (T("f_across", 0.05), SQW - W), (T("f_across", 0.9), 0)], 0.6)
    c = view(square_bg(), cam)
    c = overlay(c, (255, 130, 90), 0.28)
    paste_layer(c, flood_layer(), cam)
    ripples(c, t, FLOOD_Y + 6, H, 40, seed=12, col=(255, 210, 180))
    # tables poking out of the water, pigeons perched on them
    for x in (1450, 1560, 60):
        sx = x - cam
        if -80 < sx < W + 80:
            c.ellipse(sx, FLOOD_Y - 10 + 64 - 64 * 0.8 - 6, 34 * 0.8, 8 * 0.8, (250, 250, 246), w=2.5)
            P.pigeon(c, sx - 8, FLOOD_Y - 14, 1.0, 1, t, peck=0)
    # balloon waiting on the left, basket in the water
    bal_y = FLOOD_Y + 14
    lift = 0.0
    if t >= T("f_lift"):
        lift = ease(tl.prog("f_lift", t, 0.15, 1.0)) ** 1.3
    aboard = t >= T("f_ciao", 0.7)
    flame = 1.0 if T("f_ciao", 0.7) < t < T("f_lift", 0.5) else 0.0
    cats_in = None
    if aboard:
        lm = (0.9 * math.sin(t * 9) ** 2) if T("f_lift", 0.5) < t < T("f_lift", 0.8) else 0.0
        cats_in = cats_in_basket(tl, t, "happy", "happy", (-1, 0), -1, -1)
    P.balloon(c, BALLOON_X - cam, bal_y - 820 * lift, 0.62, t, flame, inside=cats_in)
    # gondola route: in from the water on the right, across the square to the balloon
    gk = [(T("f_narr"), SQW + 350), (T("f_flood", 0.5), 2250), (T("f_across", 0.05), 2250),
          (T("f_across", 0.92), BALLOON_X + 330)]
    gxw = smooth(t, gk, 0.5)
    gx = gxw - cam
    gy = FLOOD_Y + 26
    moving = abs(smooth(t + 0.05, gk) - smooth(t - 0.05, gk)) > 2
    P.gondola(c, gx, gy, 0.85, -1, t)
    if moving and t >= T("f_across"):
        splash(c, gx - 210, gy, (t * 1.5) % 1.0, 0.35, seed=int(t * 1.5))
    sy = gy - 36 * 0.85
    if not aboard:
        if t < T("f_ciao", 0.2):
            leyes = "wide" if t < T("f_gondola") else "happy"
            kitty(c, tl, t, "luna", gx + 10 * 0.85, sy, 0.62, -1, "sit", eyes=leyes)
            kitty(c, tl, t, "whiskers", gx - 70 * 0.85, sy, 0.66, -1, "sit",
                  eyes="wide" if T("f_never") <= t < T("f_gondola", 0.5) else "open")
        else:
            u = tl.prog("f_ciao", t, 0.2, 0.7)
            bx = BALLOON_X - cam
            D.cat(c, lerp(gx + 8, bx - 14, u), lerp(sy, bal_y - 60 * 0.62, u) + arc_y(u, 90), P.LUNA_NOBELL, 0.6, -1,
                  "leap", t=t, seed=1.3)
            D.cat(c, lerp(gx - 60, bx + 14, u), lerp(sy, bal_y - 60 * 0.62, u) + arc_y(u, 110), D.WHISKERS, 0.62, -1,
                  "leap", t=t)
    wave = 0.0
    if t >= T("f_ciao"):
        wave = 0.5 + 0.5 * math.sin(t * 7)
    bepi_rowing(c, tl, t, gx, gy, 0.85, -1, speed=1.6 if moving else 0.6, sing=1.0 if moving and t >= T("f_across") else 0.0,
                eyes="happy" if t >= T("f_gondola") else "open", wave=wave, rowing=moving)
    c.tint = None
    shade_bottom(c, tl, t, 0.35)
    return c


# =================================================================== home

def night_bg(dawn):
    def make():
        if dawn:
            stops = [(0, (90, 110, 180)), (0.5, (240, 170, 170)), (0.8, (255, 214, 160)), (1, (255, 226, 170))]
        else:
            stops = [(0, (14, 18, 48)), (0.6, (40, 44, 96)), (1, (70, 60, 110))]
        c = Canvas(sky(W, H, stops))
        if not dawn:
            D.stars(c, 23, 160, W, 460)
            D.moon(c, 1040, 130, 56, sky=(20, 26, 64))
        else:
            c.glow(640, 560, 400, 140, (255, 236, 190), (255, 214, 160), steps=8)
        hill = (50, 70, 90) if not dawn else (120, 170, 110)
        c.poly([(0, 520), (250, 480), (600, 530), (900, 490), (W, 520), (W, H), (0, H)], hill, ol=None)
        c.push(1100, 560, 0.5)
        c.rect(-110, -150, 110, 0, (250, 228, 190) if dawn else (70, 70, 100), w=3)
        c.poly([(-130, -150), (0, -240), (130, -150)], (196, 90, 70) if dawn else (80, 50, 70), w=3)
        c.rect(-70, -110, -20, -60, (255, 220, 120), w=2.5)
        c.pop()
        c.poly([(0, 600), (W, 580), (W, H), (0, H)], mix(hill, (0, 0, 0), 0.15), ol=None)
        return c.img
    return cached(("night", dawn), make)


def home_window(tl, t):
    def extra(sub):
        # the balloon resting in the meadow, its envelope sagging
        P.balloon(sub, 220, 232, 0.2, t, 0, sign=False)
    return extra


def rainbow_spots(c, t, k, seed=4):
    if k <= 0.02:
        return
    rng = np.random.default_rng(seed)
    cols = [(255, 120, 120), (255, 200, 110), (255, 250, 140), (150, 230, 150), (140, 200, 255), (200, 160, 255)]
    for i in range(14):
        x = rng.uniform(560, 1260) + 20 * math.sin(t * 1.3 + i)
        y = rng.uniform(120, 500) + 12 * math.cos(t * 1.1 + i)
        if 750 < x < 1090 and 100 < y < 395:
            continue
        r = rng.uniform(6, 12) * k
        for j, col in enumerate(cols):
            c.circle(x + j * r * 0.55, y, r * 0.5, mix((250, 228, 190), col, 0.6 * k), ol=None)


def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    if t < T("h_sill"):
        u = tl.prog("h_narr", t, 0.3, 1.0)
        c = Canvas(Image.blend(night_bg(False), night_bg(True), ease(u)))
        v = tl.prog("h_fly", t) * 0.6 + tl.prog("h_narr", t) * 0.4
        bx = lerp(-150, 980, v)
        by = lerp(300, 470, ease(v))
        c.tint = ((30, 36, 90), 0.4 * (1 - u))
        P.balloon(c, bx, by, 0.4, t, 1.0 if (t * 0.5) % 1 < 0.15 else 0,
                  inside=cats_in_basket(tl, t, "closed", "closed", (0, 0)))
        c.tint = None
        if u < 0.5:
            D.zzz(c, bx + 30, by - 110, t)
        return c
    c = Canvas(room_bg().copy())
    draw_window(c, home_window(tl, t))
    k_ring = ring_amount(tl, t)
    rainbow_spots(c, t, max(0.25, k_ring) if t >= T("h_ring") else 0.25 * tl.prog("h_sill", t))
    SY = 372
    # Luna on the left, Pip in the middle, Whiskers on the right of the sill
    shake = 5 * math.sin(t * 20) * k_ring
    kitty(c, tl, t, "luna", 850, SY, 0.8, 1, "sit", eyes="happy" if t >= T("h_ring") else "open",
          head_dy=shake, look=(1, 0))
    if t >= T("h_ring"):
        P.notes(c, 900, SY - 130, t, 0.6, col=(200, 240, 255))
    pip_x = 930
    D.mouse(c, pip_x, SY, 1.0, 1 if t < T("h_gift") else 1, t, mouth=tl.mouth("pip", t),
            eyes="happy" if t >= T("h_gift", 0.6) else "open", proud=T("h_pip") <= t < T("h_pip", 1),
            hop=abs(math.sin(t * 8)) * 6 if T("h_gift", 0.6) <= t < T("h_nap") else 0)
    if t >= T("h_gift", 0.3):
        u = ease(tl.prog("h_gift", t, 0.3, 0.7))
        P.glass_mouse(c, lerp(1010, 966, u), SY, 1.0)
        sparkles(c, lerp(1010, 966, u), SY - 18, t, r=22, n=4, k=0.8)
    if t < T("h_nap", 0.5):
        kitty(c, tl, t, "whiskers", 1030, SY, 0.8, -1, "sit", eyes="happy" if t >= T("h_ring") else "open",
              look=(1, 0.3))
    else:
        D.cat(c, 1036, SY, D.WHISKERS, 0.75, -1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
        D.zzz(c, 1000, SY - 70, t)
    # close-up on the windowsill, pushing in slowly at the end
    zk = ease(tl.prog("h_end", t, 0.0, 0.6))
    w = lerp(760, 640, zk)
    h = w * H / W
    cx, cy = lerp(880, 930, zk), lerp(300, 320, zk)
    box = tuple(int(round(v * SS)) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    c = Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))
    k = ease(tl.prog("h_end", t, 0.3, 0.55))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 40 * k, mix((120, 100, 90), (255, 250, 230), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "bell": bell, "flight": flight, "square": square, "canal": canal,
               "murano": murano, "flood": flood, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["v_narr", "g_rialto", "g_quiet", "f_narr", "h_sill"]
