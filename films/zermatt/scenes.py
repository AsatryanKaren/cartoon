"""Scenes of "Whiskers and the Chocolate Mountain". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.zermatt import props as P

CHOCO = dict(body=(128, 76, 44), dark=(92, 52, 30), belly=(170, 112, 70), ear=(206, 140, 116),
             eye=(126, 190, 70), stripes=True, collar=None)
PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "wolli": 5.0, "berta": 6.0}

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


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, pal=None, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, pal or PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    x = smooth(t, keys)
    v = speed(t, keys)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "wolli":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / (14 * s))) * 5 * s if moving else kw.pop("hop", 0.0)
        P.sheep(c, x, y, s, face, t, mouth=mouth, walk=x / (11 * s) if moving else 0.0, hop=hop,
                seed=SEED["wolli"], **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def wolli(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("wolli", t))
    P.sheep(c, x, y, s, face, t, mouth=mouth, seed=SEED["wolli"], **kw)


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def T_in(tl, t, a, b):
    return tl.t(a) <= t < tl.t(b)


def sky(w, h, stops):
    return D.gradient(w * SS, h * SS, stops)


def soft_clouds(c, t, seed, n, w, ymax, s=(0.6, 1.1), speed_=6.0, col=(255, 255, 255)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x0, y, sc = rng.uniform(0, w), rng.uniform(40, ymax), rng.uniform(*s)
        x = (x0 + t * speed_ * sc) % (w + 300) - 150
        D.cloud(c, x, y, sc, col)


# =================================================================== title

def title_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (92, 160, 232)), (0.55, (190, 222, 246)), (1, (220, 236, 240))]))
        P.peak(c, 160, 470, 560, 260)
        P.peak(c, 1180, 470, 520, 230)
        P.matterhorn(c, 790, 520, 0.95)
        c.poly([(0, 470), (200, 450), (420, 480), (640, 500), (900, 482), (1100, 460), (W, 470), (W, H), (0, H)],
               (120, 178, 92), ol=None)
        c.poly([(0, 560), (260, 520), (560, 548), (860, 536), (1100, 520), (W, 540), (W, H), (0, H)],
               (106, 168, 80), ol=None)
        for x, y, s in ((60, 500, 0.7), (110, 512, 0.55), (1170, 500, 0.7), (1230, 508, 0.6), (1010, 494, 0.5)):
            P.pine(c, x, y, s)
        P.chalet(c, 360, 520, 0.36)
        P.chalet(c, 470, 530, 0.3, wide=0.8)
        P.chalet(c, 1080, 526, 0.32)
        c.poly([(0, 640), (300, 600), (640, 620), (980, 604), (W, 630), (W, H), (0, H)], (132, 190, 96), ol=None)
        rng = np.random.default_rng(3)
        P.meadow_flowers(c, rng, 0, W, 560, 720, 260)
        for x in (180, 260, 1100, 1180, 1220):
            P.edelweiss(c, x, 690 - (x % 40), 1.1)
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    soft_clouds(c, t, 2, 4, W, 200)
    # cats on the meadow
    kat(c, tl, t, "whiskers", 300, 668, 0.8, 1, "sit", look=(1, -1), mouth=0)
    kat(c, tl, t, "luna", 390, 670, 0.76, 1, "sit", look=(1, -1), tail=math.sin(t * 1.5), mouth=0)
    P.chough(c, (t * 60) % (W + 200) - 100, 250 + 20 * math.sin(t), t, 1.0, 1, fly=1)
    D.butterfly(c, 520 + 40 * math.sin(t * 0.8), 600 + 20 * math.sin(t * 1.7), t, 0.6)
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(330, 84 - 30 * (1 - k), "Whiskers and the", 40, mix((92, 160, 232), (255, 252, 240), k),
           stroke=3 * k, stroke_fill=(70, 40, 30))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(330, 150, "CHOCOLATE", 24 + 46 * k2, mix((92, 160, 232), (150, 86, 46), k2), stroke=5 * k2,
           stroke_fill=(255, 246, 228))
    c.text(330, 214, "MOUNTAIN", 22 + 40 * k2, mix((92, 160, 232), (150, 86, 46), k2), stroke=5 * k2,
           stroke_fill=(255, 246, 228))
    return finish(c, tl, t)


# =================================================================== hedge

GROUND = 610
HEDGE_X = 930


def hedge_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (110, 180, 240)), (0.6, (200, 230, 250)), (1, (220, 240, 250))]))
        D.cloud(c, 700, 110, 0.9)
        D.cloud(c, 1100, 70, 0.7)
        # far hills and the fence
        c.poly([(0, 470), (300, 430), (700, 460), (1000, 420), (W, 450), (W, H), (0, H)], (140, 196, 110), ol=None)
        D.tree(c, 760, 470, 0.9)
        D.tree(c, 1180, 470, 0.75, leaf=(80, 150, 80))
        for x in range(300, W + 40, 44):
            c.rect(x, 470, x + 16, 540, (246, 240, 226), w=2, r=3)
        c.rect(290, 488, W, 498, (246, 240, 226), w=2)
        c.rect(290, 516, W, 526, (246, 240, 226), w=2)
        c.rect(0, 530, W, H, (118, 182, 88), ol=None)
        for y in range(560, H, 30):
            c.line([(0, y), (W, y + 4)], (108, 172, 80), 2, cap=False)
        # the cats' house: wall, window and sill on the left
        c.rect(-10, 120, 250, 560, (236, 214, 178), w=3)
        c.poly([(-30, 130), (120, 40), (270, 130)], (176, 80, 60), w=3)
        c.rect(40, 240, 210, 400, (150, 190, 226), w=3)
        c.line([(125, 240), (125, 400)], (250, 250, 250), 5, cap=False)
        c.line([(40, 320), (210, 320)], (250, 250, 250), 5, cap=False)
        c.rect(30, 396, 220, 412, (250, 246, 236), w=2.5, r=3)
        P.geraniums(c, 46, 204, 382)
        rng = np.random.default_rng(5)
        for k in range(40):
            D.flower(c, rng.uniform(260, 1260), rng.uniform(560, 700),
                     [(250, 120, 140), (250, 210, 80), (190, 140, 240), (255, 255, 255)][k % 4], rng.uniform(0.6, 0.9))
        return c.img
    return cached("hedge", make)


def hedge_bush(c, t, shake, wool):
    """The big hedge; it shakes; Wolli's wool pokes out while she is stuck inside."""
    jig = math.sin(t * 30) * 6 * shake
    c.push(HEDGE_X + jig, GROUND + 10, 1.0)
    col = (66, 140, 70)
    for dx, dy, r in ((-150, -60, 70), (150, -60, 70), (-80, -120, 90), (80, -120, 90), (0, -170, 90), (0, -70, 100)):
        c.circle(dx, dy, r, col)
    for dx, dy, r in ((-150, -60, 64), (150, -60, 64), (-80, -120, 84), (80, -120, 84), (0, -170, 84), (0, -70, 94)):
        c.circle(dx, dy, r, col, ol=None)
    rng = np.random.default_rng(4)
    for k in range(30):
        c.circle(rng.uniform(-180, 180), rng.uniform(-230, -30), rng.uniform(6, 12), (84, 160, 84), ol=None)
    if wool > 0:
        for dx, dy, r in ((-30, -110, 22), (0, -124, 26), (30, -108, 22), (10, -90, 18)):
            c.circle(dx, dy, r * wool, P.WOOL, w=2)
    c.pop()


def leaves_burst(c, x, y, dt):
    if dt < 0 or dt > 1.2:
        return
    rng = np.random.default_rng(12)
    for k in range(14):
        a = rng.uniform(-math.pi, 0)
        v = rng.uniform(150, 320)
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 260 * dt * dt
        c.ellipse(px, py, 7, 4, (80, 160, 80), w=1.5)


def hedge(tl, t):
    T = tl.t
    c = Canvas(hedge_bg().copy())
    shake = 1.0 if (T_in(tl, t, "g_shake", "g_pip") or T("g_pop") <= t < T("g_pop", 0.5)) else 0.0
    if T("g_narr", 0.85) <= t < T("g_narr", 1) + 0.3:
        shake = 0.6
    popped = t >= T("g_pop", 0.5)
    hedge_bush(c, t, shake, 0.0 if popped else 1.0)
    # Wolli pops out of the hedge and lands in front of it
    if popped:
        u = clamp((t - T("g_pop", 0.5)) / 0.6)
        wx = lerp(HEDGE_X, HEDGE_X - 70, u)
        wy = GROUND - math.sin(math.pi * u) * 120
        sad = t < T("g_where")
        happy = T("g_zermatt") <= t < T("g_glow", 1) or t >= T("g_spoon")
        wolli(c, tl, t, wx, wy, 1.05, -1, eyes="happy" if happy and tl.mouth("wolli", t) < 0.2 else ("sad" if sad else "open"),
              look=(1, 0))
        leaves_burst(c, HEDGE_X, GROUND - 120, t - T("g_pop", 0.5))
    # Pip runs in
    if t >= T("g_pip") - 0.5:
        actor(c, tl, t, "pip", [(T("g_pip") - 0.5, 1350), (T("g_pip", 0.6), 650)], GROUND + 6, 1.4, -1,
              eyes="wide" if t < T("g_pop", 0.6) else "open")
    # Luna
    lface = 1
    kat(c, tl, t, "luna", 480, GROUND, 1.0, lface, "sit" if t < T("g_home") else "stand",
        eyes="happy" if T_in(tl, t, "g_spoon", "g_end") else ("wide" if T("g_pop", 0.5) <= t < T("g_wolli") else "open"),
        look=(1, 0), mouth=laughing(t) * 0.5 if T("g_spoon", 0.6) <= t else tl.mouth("luna", t))
    # Whiskers: napping until he hears "chocolate"
    wx = 250
    if t < T("g_ears"):
        kat(c, tl, t, "whiskers", wx, GROUND + 6, 1.0, 1, "sleep", mouth=0)
        D.zzz(c, wx + 60, GROUND - 90, t)
    elif t < T("g_spoon"):
        startle = clamp((t - T("g_ears")) / 0.3)
        dream = T("g_dream") <= t < T("g_home", 0.4)
        kat(c, tl, t, "whiskers", wx, GROUND + 6, 1.0, 1, "sit",
            eyes="happy" if dream else "wide", look=(1, -0.5), head_dy=-10 * startle)
    else:
        hop = abs(math.sin((t - T("g_spoon")) * 7)) * 22 if t > T("g_spoon", 0.4) else 0
        kat(c, tl, t, "whiskers", wx, GROUND + 6 - hop, 1.0, 1, "stand",
            eyes="happy" if tl.mouth("whiskers", t) < 0.1 else "open")
    # dream: a chocolate Matterhorn
    k = min(ease((t - T("g_choc", 0.6)) / 0.4), 1 - ease((t - T("g_home", 0.5)) / 0.3))
    if k > 0.02:
        P.thought_bubble(c, 420, 210, 170, 110, k, tail=(300, 470))
        if k > 0.6:
            P.matterhorn(c, 420, 286, 0.36 * k, P.MATTER_CHOC, skirt=False)
            for j in range(5):
                u = (t * 0.6 + j / 5) % 1
                c.circle(330 + 40 * j, 300 - 30 * u, 4, (255, 240, 180), ol=None)
    return finish(c, tl, t)


# ================================================================= trailer

ROAD = 610
TRW = 2 * W


def trailer_far(phase):
    """Wrapped strip of distant mountains for the road (phase: dusk or night)."""
    def make():
        if phase == "dusk":
            st = [(0, (70, 70, 140)), (0.45, (220, 130, 140)), (0.75, (255, 196, 140)), (1, (255, 210, 150))]
            m1, m2 = (110, 90, 130), (80, 70, 110)
        else:
            st = [(0, (14, 20, 54)), (0.7, (40, 50, 100)), (1, (60, 66, 120))]
            m1, m2 = (40, 50, 86), (30, 38, 70)
        c = Canvas(sky(TRW + W, H, st), size=(TRW + W, H))
        if phase == "night":
            D.stars(c, 7, 160, TRW + W, 360)
        rng = np.random.default_rng(31)
        for k in range(12):
            x = k * TRW / 12 + rng.uniform(-50, 50)
            for dx in (0, TRW):
                if x + dx < TRW + W + 300:
                    P.peak(c, x + dx, 470, rng.uniform(300, 460), rng.uniform(170, 260), col=m1, shade=m2,
                           snow=mix((250, 250, 255), m1, 0.35 if phase == "night" else 0.1))
        for k in range(10):
            x = k * TRW / 10 + 60
            for dx in (0, TRW):
                c.poly([(x + dx - 200, 520), (x + dx, 470 + 20 * math.sin(k)), (x + dx + 200, 520)],
                       mix(m2, (20, 40, 30), 0.5), ol=None)
        c.rect(0, 510, TRW + W, H, mix(m2, (30, 60, 40), 0.6), ol=None)
        for k in range(30):
            x = k * TRW / 30 + 20
            for dx in (0, TRW):
                P.pine(c, x + dx, 540 + 10 * math.sin(k * 3), 0.5, col=mix(m2, (30, 70, 50), 0.6),
                       dark=mix(m2, (10, 30, 20), 0.6))
        c.rect(0, ROAD - 14, TRW + W, H, (70, 66, 72) if phase == "dusk" else (40, 40, 54), ol=None)
        for x in range(0, TRW + W, 90):
            c.rect(x, ROAD + 40, x + 46, ROAD + 46, (230, 220, 160) if phase == "dusk" else (150, 150, 120), ol=None)
        c.rect(0, ROAD + 90, TRW + W, H, (90, 130, 70) if phase == "dusk" else (34, 54, 50), ol=None)
        return c.img
    return cached(("trailer_far", phase), make)


def trailer_inside_bg():
    def make():
        c = Canvas(bg=(70, 46, 34))
        for k in range(9):
            y = 60 + k * 70
            c.rect(0, y, W, y + 40, (110, 74, 48), ol=None)
        c.rect(0, 560, W, H, (196, 160, 90), ol=None)       # straw floor
        rng = np.random.default_rng(8)
        for k in range(160):
            x, y = rng.uniform(0, W), rng.uniform(560, H)
            c.line([(x, y), (x + rng.uniform(-20, 20), y + rng.uniform(-4, 4))], (226, 196, 120), 2)
        return c.img
    return cached("trailer_inside", make)


def moon_stripes(c, t):
    """Moonlight through the slats sliding past while the trailer drives."""
    for k in range(6):
        x = (k * 260 - t * 120) % (W + 400) - 200
        c.poly([(x, 100), (x + 60, 100), (x + 160, 560), (x + 100, 560)], (130, 120, 150), ol=None)


def trailer_scene(tl, t):
    T = tl.t
    if t < T("tr_three"):
        return trailer_drive(tl, t, "dusk")
    if t < T("tr_night"):
        return trailer_inside(tl, t)
    if t < T("tr_taxi"):
        return trailer_drive(tl, t, "night")
    return taxi_ride(tl, t)


def trailer_drive(tl, t, phase):
    s0 = tl.scenes["trailer"][0]
    camx = ((t - s0) * 260) % TRW
    c = view(trailer_far(phase), camx)
    bounce = 2 * math.sin(t * 9)
    x, y = 900, ROAD + 24
    s = 0.95
    # passengers' heads peeking over the trailer side
    top = y - 196 * s + bounce
    tx = x + s * (-560 + 70)
    night = phase == "night"
    if night:
        c.tint = ((20, 30, 80), 0.35)
    P.sheep(c, tx + 40, top + 60, 0.7, 1, t, eyes="closed" if night else "open", seed=7)
    P.sheep(c, tx + 230, top + 64, 0.65, -1, t, eyes="closed" if night else "open", seed=8)
    kat(c, tl, t, "luna", tx + 110, top + 62, 0.7, 1, "sit", eyes="closed" if night else "happy", mouth=0)
    kat(c, tl, t, "whiskers", tx + 175, top + 62, 0.7, 1, "sit", eyes="closed" if night else "open", mouth=0)
    P.sheep_trailer(c, x, y + bounce, s, t, spin=-t * 8, night=night)
    c.tint = None
    if night:
        D.moon(c, 1080, 110, 36, sky=(20, 28, 66))
    return finish(c, tl, t)


def trailer_inside(tl, t):
    T = tl.t
    c = Canvas(trailer_inside_bg().copy())
    moon_stripes(c, t)
    sway = 6 * math.sin(t * 1.6)
    c.push(sway, 0, 1.0)
    # other sheep dozing at the back
    for x, y, s, f, sd in ((150, 600, 1.1, 1, 9), (1120, 600, 1.15, -1, 10), (980, 560, 0.9, -1, 11)):
        P.sheep(c, x, y, s, f, t, eyes="closed", seed=sd)
    # Wolli lying down, with the cats snuggled into her wool
    P.sheep(c, 640, 690, 1.9, 1, t, eyes="closed" if t > T("tr_three", 0.6) else "happy",
            mouth=tl.mouth("wolli", t), seed=5)
    c.rect(-40, 650, W + 40, H + 10, (196, 160, 90), ol=None)
    kat(c, tl, t, "luna", 500, 600, 0.95, 1, "sleep", mouth=0)
    talk = T("tr_bed") - 0.2 <= t < T("tr_bed", 1) + 0.2
    kat(c, tl, t, "whiskers", 730, 586, 0.95, -1, "sleep" if not talk else "sit", eyes="closed",
        head_dy=10 if talk else 0)
    c.pop()
    if not talk:
        D.zzz(c, 790, 470, t)
    return finish(c, tl, t)


def valley_bg():
    def make():
        VW = W
        c = Canvas(sky(VW, H, [(0, (120, 186, 240)), (0.6, (214, 234, 250)), (1, (230, 240, 244))]))
        P.peak(c, 260, 440, 600, 280)
        P.peak(c, 1080, 440, 560, 300)
        P.matterhorn(c, 680, 440, 0.62)
        c.poly([(0, 440), (W, 440), (W, H), (0, H)], (118, 176, 92), ol=None)
        c.poly([(0, 380), (180, 420), (360, 480), (360, 520), (0, 520)], (90, 140, 80), ol=None)
        c.poly([(W, 370), (1080, 420), (900, 480), (900, 520), (W, 520)], (90, 140, 80), ol=None)
        for x in (60, 140, 230, 1090, 1170, 1240):
            P.pine(c, x, 450 + (x % 50), 0.7)
        # the river Vispa
        c.poly([(0, 520), (W, 506), (W, 540), (0, 556)], (120, 190, 220), ol=None)
        for x in range(0, W, 60):
            c.line([(x, 532 - x * 0.012), (x + 26, 532 - x * 0.012)], (220, 240, 250), 2, cap=False)
        c.rect(0, 560, W, 650, (150, 146, 150), ol=None)
        c.rect(0, 650, W, H, (106, 160, 84), ol=None)
        rng = np.random.default_rng(6)
        P.meadow_flowers(c, rng, 0, W, 660, 720, 80)
        for x in range(0, W, 120):
            c.rect(x, 602, x + 60, 608, (230, 230, 230), ol=None)
        c.rect(30, 470, 230, 500, (250, 250, 250), w=2.5, r=6)
        c.text(130, 485, "ZERMATT  2 km", 16, (200, 40, 50))
        return c.img
    return cached("valley", make)


def taxi_ride(tl, t):
    T = tl.t
    c = Canvas(valley_bg().copy())
    u = tl.prog("tr_taxi", t, 0.0, 1.0)
    u2 = tl.prog("tr_zoom", t)
    x = lerp(-160, 520, ease(u)) + lerp(0, 1000, u2 ** 1.6)
    y = 640 + 2 * math.sin(t * 14)
    # passengers in the windows
    P.taxi(c, x, y, 1.0, spin=x / 24)
    kat(c, tl, t, "luna", x - 70, y - 66, 0.55, 1, "sit", eyes="happy", mouth=tl.mouth("luna", t))
    kat(c, tl, t, "whiskers", x + 22, y - 66, 0.55, 1, "sit", mouth=0, look=(1, -1))
    P.taxi_windows(c, x, y, 1.0)
    # Wolli rides on the back step, ears flapping
    wolli(c, tl, t, x - 150, y - 18, 0.6, 1, eyes="happy")
    return finish(c, tl, t)


# ================================================================= village

VW = W + 640
VG = 600            # street level


def village_bg():
    def make():
        c = Canvas(sky(VW, H, [(0, (104, 172, 236)), (0.55, (200, 228, 250)), (1, (220, 236, 246))]), size=(VW, H))
        D.cloud(c, 300, 90, 0.8)
        D.cloud(c, 1100, 60, 0.6)
        P.peak(c, 200, 420, 560, 260)
        P.peak(c, 760, 400, 500, 200)
        P.matterhorn(c, 1560, 420, 0.88)
        c.rect(0, 380, VW, VG, (110, 160, 90), ol=None)
        # back row of chalets with a gap for the mountain
        for x, s, f, wd in ((80, 0.95, 2, 1.0), (330, 1.05, 3, 0.9), (600, 0.9, 2, 1.1), (870, 1.0, 2, 0.95),
                            (1110, 1.0, 3, 1.0), (1860, 0.95, 2, 1.0)):
            P.chalet(c, x, VG - 40, s, floors=f, wide=wd)
        # cobbled street
        c.rect(0, VG - 40, VW, H, (196, 186, 170), ol=None)
        rng = np.random.default_rng(2)
        for y in range(VG - 30, H, 22):
            for x in range(int(rng.uniform(-20, 0)), VW, 40):
                c.ellipse(x + (y % 44) * 0.5, y, 16, 7, (184, 172, 156), ol=None)
        c.rect(0, VG - 44, VW, VG - 36, (150, 140, 128), ol=None)
        # the cuckoo-clock shop window (front, at street level)
        sx = 1290
        c.rect(sx - 110, 320, sx + 110, VG - 40, P.LARCH, w=3)
        c.rect(sx - 96, 380, sx + 96, VG - 60, (190, 220, 236), w=3)
        c.rect(sx - 110, 300, sx + 110, 340, (250, 244, 226), w=2.5, r=4)
        c.text(sx, 320, "CUCKOO CLOCKS", 18, (120, 50, 30))
        for k, (cx_, cy_) in enumerate(((sx - 60, 400), (sx + 60, 400))):
            P.cuckoo_clock(c, cx_, cy_, 0.42, 0, 0.0, swing=False)
        # Berta's chocolate shop at the far right
        bx = VW - 150
        c.rect(bx - 120, 330, bx + 120, VG - 40, (236, 214, 178), w=3)
        c.rect(bx - 130, 300, bx + 130, 344, (120, 70, 40), w=3, r=6)
        c.text(bx, 322, "BERTA'S CHOCOLATE", 16, (255, 240, 200))
        c.rect(bx - 30, 420, bx + 30, VG - 40, (120, 70, 40), w=3, r=5)
        c.rect(bx - 104, 380, bx - 44, 460, (190, 220, 236), w=2.5)
        for k in range(3):
            P.choc_matterhorn(c, bx - 74, 456 - 0 * k, 0.35)
        P.geraniums(c, bx - 110, bx - 40, 466)
        return c.img
    return cached("village", make)


def village(tl, t):
    T = tl.t
    s0 = tl.scenes["village"][0]
    pan = ease(clamp((t - s0) / max(0.1, T("v_look") - s0)))
    camx = lerp(0, VW - W, pan)
    c = view(village_bg(), camx)
    sx = 1290 - camx            # shop window on screen
    # the cuckoo in the shop window
    pop = 0.0
    if T("v_cuckoo", 0.3) <= t < T("v_stretch", 0.5):
        pop = ease(clamp((t - T("v_cuckoo", 0.3)) / 0.15))
    P.cuckoo_clock(c, sx - 60, 400, 0.42, pop, t, swing=True)
    if pop > 0:
        c.text(sx - 60, 360 - 10 * pop, "CUCKOO!", 18 + 14 * pop, (255, 250, 220), stroke=3, stroke_fill=(110, 60, 30))
    P.cuckoo_clock(c, sx + 60, 400, 0.42, 0, t + 1.3, swing=True)
    # a horse carriage passing at the back
    hk = tl.prog("v_narr", t)
    if 0 < hk < 1:
        hx = lerp(-200, W + 200, hk)
        horse_carriage(c, hx, VG - 30, t)
    # scent wisps from the chocolate shop
    if t >= T("v_sniff"):
        for k in range(4):
            u = ((t - T("v_sniff")) * 0.5 + k / 4) % 1
            px = lerp(VW - 150 - camx, 700, u)
            pts = [(px + 140 * v, 430 + 26 * k + 12 * math.sin(t * 3 + v * 7 + k)) for v in np.linspace(0, 1, 10)]
            c.line(pts, mix((170, 110, 70), (236, 214, 190), u), 7 * (1 - u) + 2)
    # walkers: everyone enters with the pan
    walk_end = T("v_look")
    wkeys = [(s0, -300), (walk_end, 230)]
    lkeys = [(s0, -150), (walk_end, 460)]
    kkeys = [(s0, -20), (walk_end, 680)]
    if t >= T("v_cuckoo") - 0.4:
        kkeys = [(s0, -20), (walk_end, 680)]
    if t >= T("v_follow"):
        lkeys = lkeys + [(T("v_follow", 0.2), 460), (T("v_follow", 1), 1500)]
        wkeys = wkeys + [(T("v_follow", 0.3), 230), (T("v_follow", 1), 1400)]
        kkeys = kkeys + [(T("v_follow"), 680), (T("v_follow", 0.9), 1600)]
    # Wolli
    wx = actor(c, tl, t, "wolli", wkeys, VG + 30, 0.95, 1,
               eyes="happy" if T_in(tl, t, "v_stretch", "v_family") else "open", look=(1, -1))
    lpose = "stand"
    actor(c, tl, t, "luna", lkeys, VG + 30, 1.0, 1, lpose,
          eyes="happy" if T_in(tl, t, "v_look", "v_see") else ("wide" if T_in(tl, t, "v_cuckoo", "v_stretch") else "open"),
          look=(1, -1) if T_in(tl, t, "v_look", "v_rocky") else (1, 0),
          mouth=laughing(t) * 0.6 if T("v_stretch") <= t < T("v_stretch", 1) else tl.mouth("luna", t))
    # Whiskers
    jumping = T("v_cuckoo", 0.3) <= t < T("v_cuckoo", 0.85)
    if jumping:
        u = (t - T("v_cuckoo", 0.3)) / (T("v_cuckoo", 0.85) - T("v_cuckoo", 0.3))
        kx = smooth(t, kkeys) - 40 * math.sin(math.pi * u)
        ky = VG + 30 - math.sin(math.pi * u) * 70
        kat(c, tl, t, "whiskers", kx, ky, 1.0, 1, "leap", eyes="wide", mouth=0.8)
    else:
        sniff = T_in(tl, t, "v_sniff", "v_follow")
        pose = "stand"
        actor(c, tl, t, "whiskers", kkeys, VG + 30, 1.0, 1, pose,
              eyes="closed" if sniff else ("wide" if T_in(tl, t, "v_cuckoo", "v_cuckoo") else "open"),
              look=(1, -1) if T_in(tl, t, "v_see", "v_cuckoo") else (1, 0),
              head_dy=-6 if sniff else 0)
    return finish(c, tl, t)


def horse_carriage(c, x, y, t):
    """A small horse-drawn carriage trotting past at the back of the street."""
    c.push(x, y, 0.55)
    brown = (150, 96, 60)
    for k, lx in enumerate((50, 110)):
        sw = math.sin(t * 9 + k * 2) * 10
        c.stroke([(lx, -70), (lx + sw, 0)], brown, 12)
    c.ellipse(80, -90, 60, 30, brown)
    c.stroke([(130, -100), (160, -150)], brown, 24)
    c.ellipse(178, -150, 26, 16, brown)
    c.poly([(150, -170), (160, -190), (166, -168)], brown, w=2)
    c.stroke([(26, -100), (10, -60)], (60, 40, 30), 8)
    c.rect(-160, -150, 10, -40, (40, 70, 110), w=3, r=8)
    c.rect(-150, -140, -70, -96, (190, 220, 236), w=2)
    P.wheel(c, -130, -30, 30, -t * 6)
    P.wheel(c, -20, -30, 30, -t * 6)
    c.pop()


# =============================================================== chocolate

FLOOR = 650
VAT_X, VAT_RIM = 690, 480
STEP_X, STEP_TOP = 420, 580


def choc_bg():
    def make():
        c = Canvas(bg=(240, 222, 190))
        # wood panelling and shelves
        c.rect(0, 380, W, FLOOR, (160, 104, 62), ol=None)
        for x in range(0, W, 80):
            c.line([(x, 380), (x, FLOOR)], (130, 82, 48), 3, cap=False)
        c.rect(0, 372, W, 386, (120, 76, 44), ol=None)
        for y in (120, 230):
            c.rect(20, y, 400, y + 14, (130, 82, 48), w=2.5)
            rng = np.random.default_rng(y)
            x = 30
            while x < 380:
                w = rng.uniform(26, 40)
                col = [(200, 40, 50), (240, 200, 70), (60, 110, 180), (250, 250, 250), (120, 70, 40)][rng.integers(5)]
                c.rect(x, y - 60, x + w, y, col, w=2)
                c.rect(x, y - 40, x + w, y - 26, (250, 240, 220), ol=None)
                x += w + 6
        for y in (150, 260):
            c.rect(880, y, 1260, y + 14, (130, 82, 48), w=2.5)
            for k in range(5):
                P.choc_matterhorn(c, 920 + 72 * k, y, 0.5)
        # alphorn on the wall
        # (drawn per frame so it can be taken down)
        # the chocolate fountain: copper pipe and pouring stream
        c.rect(660, 0, 720, 150, (196, 120, 70), w=3)
        c.rect(640, 150, 740, 180, (210, 136, 80), w=3, r=8)
        c.rect(0, FLOOR, W, H, (150, 110, 80), ol=None)
        for x in range(-40, W, 70):
            c.line([(x, FLOOR), (x + 60, H)], (130, 94, 66), 3, cap=False)
        c.rect(0, FLOOR - 4, W, FLOOR + 4, (110, 74, 44), ol=None)
        return c.img
    return cached("choc", make)


def vat(c, t, splash=0.0):
    """The big copper vat of melted chocolate (front part drawn after anything inside)."""
    c.ellipse(VAT_X, VAT_RIM, 170, 34, (226, 140, 80), w=3)
    c.ellipse(VAT_X, VAT_RIM + 2, 154, 26, (110, 62, 34), ol=None)
    # swirls
    for k in range(3):
        a = t * 1.5 + k * 2.1
        c.arc(VAT_X + 30 * math.cos(a), VAT_RIM + 4 + 6 * math.sin(a), 50 - 12 * k, 10 - 2 * k, 200, 340,
              (150, 92, 54), 3)


def vat_front(c):
    c.poly([(VAT_X - 170, VAT_RIM), (VAT_X + 170, VAT_RIM), (VAT_X + 150, FLOOR - 10), (VAT_X - 150, FLOOR - 10)],
           (206, 120, 64), w=3)
    c.ellipse(VAT_X, VAT_RIM, 170, 34, None, w=3) if False else None
    c.arc(VAT_X, VAT_RIM, 170, 34, 0, 180, OUT, 3)
    c.line([(VAT_X - 166, VAT_RIM + 40), (VAT_X + 166, VAT_RIM + 40)], (236, 160, 96), 4, cap=False)
    c.line([(VAT_X - 160, VAT_RIM + 100), (VAT_X + 160, VAT_RIM + 100)], (176, 100, 50), 4, cap=False)
    for side in (-1, 1):
        c.ellipse(VAT_X + side * 176, VAT_RIM + 30, 12, 20, (180, 104, 56), w=2.5)


def stream(c, t):
    """Chocolate pouring from the pipe into the vat."""
    pts = [(VAT_X + 4 * math.sin(t * 6 + v * 5), lerp(178, VAT_RIM, v)) for v in np.linspace(0, 1, 8)]
    c.stroke(pts, (120, 70, 38), 22, ol=(70, 40, 24))
    c.line([(VAT_X - 4, 190), (VAT_X - 4, VAT_RIM - 10)], (160, 100, 60), 4, cap=False)
    for k in range(3):
        u = (t * 1.3 + k / 3) % 1
        c.ellipse(VAT_X, VAT_RIM + 2, 20 + 60 * u, 4 + 10 * u, None) if False else None
        c.arc(VAT_X, VAT_RIM + 2, 20 + 60 * u, 4 + 10 * u, 0, 360, mix((150, 92, 54), (110, 62, 34), u), 2)


def choc_splash(c, x, y, dt):
    if dt < 0 or dt > 1.4:
        return
    rng = np.random.default_rng(21)
    for k in range(18):
        a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        v = rng.uniform(220, 460)
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 520 * dt * dt
        if py < FLOOR:
            c.circle(px, py, rng.uniform(6, 12) * (1 - dt / 1.6), (110, 62, 34), w=2)


def chocolate(tl, t):
    T = tl.t
    c = Canvas(choc_bg().copy())
    # alphorn hanging on the wall until Berta hands it over
    if t < T("c_end", 0.3):
        P.alphorn(c, 40, 345, 560, 330, 1.2)
    stream(c, t)
    vat(c, t)
    # step box beside the vat
    c.rect(STEP_X - 60, STEP_TOP, STEP_X + 50, FLOOR, (176, 120, 70), w=3, r=4)
    c.line([(STEP_X - 60, STEP_TOP + 20), (STEP_X + 50, STEP_TOP + 20)], (140, 92, 52), 3, cap=False)
    # Berta behind her counter
    laugh = T_in(tl, t, "c_laugh", "c_gift")
    arm = 0.0
    if T_in(tl, t, "c_gift", "c_save"):
        arm = 0.6
    if T_in(tl, t, "c_horn", "c_end"):
        arm = 1.0
    P.berta(c, 1040, 520, 0.95, t, mouth=tl.mouth("berta", t), laugh=laugh, arm=arm,
            ring=1.0 if T("c_berta", 0.85) <= t < T("c_taste") else 0.2)
    c.rect(860, 500, 1280, FLOOR, (186, 128, 76), w=3)
    c.rect(850, 488, 1280, 512, (210, 150, 96), w=3)
    for k in range(3):
        P.choc_matterhorn(c, 900 + 50 * k, 492, 0.42)
    # friends
    wolli(c, tl, t, 110, FLOOR + 6, 1.0, 1, eyes="happy" if laugh or t >= T("c_gift") else "open")
    kat(c, tl, t, "luna", 260, FLOOR, 1.0, 1, "sit",
        eyes="happy" if laugh else ("wide" if T_in(tl, t, "c_lean", "c_purpose") else "open"),
        mouth=laughing(t) * 0.6 if laugh else tl.mouth("luna", t))
    # Whiskers: on the step, leans, slips, falls in, climbs out as a chocolate cat
    fell = t >= T("c_lean", 0.6)
    if t < T("c_taste"):
        actor(c, tl, t, "whiskers", [(tl.scenes["chocolate"][0], 360), (T("c_berta", 0.7), 360),
                                    (T("c_berta", 1), STEP_X - 10)], STEP_TOP, 1.0, 1, eyes="wide")
    elif t < T("c_lean", 0.55):
        lean = ease(tl.prog("c_lean", t, 0.0, 0.5))
        kat(c, tl, t, "whiskers", STEP_X - 10 + 30 * lean, STEP_TOP, 1.0, 1, "crouch" if lean > 0.3 else "stand",
            eyes="happy", look=(1, 1), head_dy=10 * lean)
    elif t < T("c_lean", 0.72):
        u = tl.prog("c_lean", t, 0.55, 0.72)
        kat(c, tl, t, "whiskers", lerp(STEP_X + 20, VAT_X, u), lerp(STEP_TOP, VAT_RIM - 40, u) - math.sin(math.pi * u) * 60,
            1.0, 1, "leap", eyes="wide", mouth=0.9)
    if fell:
        splash_t = t - T("c_lean", 0.72)
        choc_splash(c, VAT_X, VAT_RIM, splash_t)
        if t < T("c_out", 0.3):
            pass                                                   # under the chocolate
        elif t < T("c_out", 0.9):
            u = tl.prog("c_out", t, 0.3, 0.9)
            kat(c, tl, t, "whiskers", VAT_X - 30, VAT_RIM + 30 - 30 * ease(u), 1.0, -1, "swim", pal=CHOCO,
                eyes="closed" if u < 0.5 else "open", mouth=0)
        else:
            sc = T_in(tl, t, "c_out", "c_end")
            u = tl.prog("c_purpose", t, 0.0, 0.25)
            kx = lerp(VAT_X - 120, STEP_X - 10, u)
            licking = T_in(tl, t, "c_laugh", "c_gift")
            kat(c, tl, t, "whiskers", kx if t < T("c_purpose", 0.25) else STEP_X - 10, STEP_TOP, 1.0,
                1 if t >= T("c_gift") else -1, "sit", pal=CHOCO,
                eyes="happy" if licking or T_in(tl, t, "c_save", "c_horn") else "open",
                mouth=0.5 + 0.4 * math.sin(t * 12) if licking else tl.mouth("whiskers", t))
            # drips
            for k in range(3):
                u2 = (t * 0.8 + k / 3) % 1
                c.ellipse(STEP_X - 30 + 25 * k, STEP_TOP - 60 + 60 * u2, 3, 5, (110, 62, 34), ol=None)
    vat_front(c)
    if t < T("c_lean", 0.72):
        pass
    # gifts: little chocolate Matterhorns in Luna's and Whiskers' paws
    if t >= T("c_gift", 0.6):
        P.choc_matterhorn(c, 290, FLOOR - 64, 0.5)
        if t >= T("c_save"):
            P.choc_matterhorn(c, STEP_X + 22, STEP_TOP - 64, 0.5)
        else:
            k = ease(tl.prog("c_gift", t, 0.6, 1.0))
            P.choc_matterhorn(c, lerp(1000, STEP_X + 22, k), lerp(480, STEP_TOP - 64, k), 0.5)
    if t >= T("c_end", 0.3):
        P.alphorn(c, 120, 600, 420, 520, 0.8)
    return finish(c, tl, t)


# =============================================================== cog train

SLOPE = math.atan2(330, W)


def slope_y(x):
    return 660 - x * math.tan(SLOPE)


def cog_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (96, 164, 232)), (0.6, (200, 228, 250)), (1, (226, 240, 246))]))
        D.cloud(c, 260, 110, 0.8)
        P.peak(c, 300, 360, 600, 200)
        P.matterhorn(c, 900, 420, 0.85)
        # meadows falling away to the valley on the left
        c.poly([(0, 420), (400, 380), (800, 360), (W, 330), (W, H), (0, H)], (120, 176, 90), ol=None)
        c.poly([(0, 560), (360, 520), (520, 600), (0, 700)], (96, 150, 80), ol=None)
        # the tiny village far below
        for k, (x, y) in enumerate(((60, 620), (100, 640), (140, 616), (180, 646), (40, 664), (210, 610))):
            P.chalet(c, x, y, 0.16)
        c.poly([(0, slope_y(0) + 6), (W, slope_y(W) + 6), (W, H), (0, H)], (104, 160, 82), ol=None)
        rng = np.random.default_rng(9)
        for k in range(80):
            x = rng.uniform(0, W)
            y = rng.uniform(slope_y(x) + 30, H)
            c.circle(x, y, rng.uniform(2, 4), [(250, 250, 250), (250, 220, 80), (200, 120, 220)][k % 3], ol=None)
        # track: sleepers, rails, rack
        for x in range(0, W + 30, 26):
            y = slope_y(x)
            c.line([(x - 4, y + 4), (x + 8, y + 18)], (110, 80, 60), 4, cap=False)
        c.line([(0, slope_y(0) + 6), (W, slope_y(W) + 6)], (90, 90, 96), 4, cap=False)
        c.line([(0, slope_y(0) + 12), (W, slope_y(W) + 12)], (60, 60, 66), 3, cap=False)
        # catenary posts
        for x in range(80, W, 300):
            y = slope_y(x)
            c.line([(x, y + 6), (x, y - 220)], (90, 90, 96), 5)
            c.line([(x, y - 210), (x + 40, y - 210)], (90, 90, 96), 4)
        c.line([(0, slope_y(0) - 200), (W, slope_y(W) - 200)], (60, 60, 60), 1.5, cap=False)
        return c.img
    return cached("cog", make)


def cogtrain(tl, t):
    T = tl.t
    c = Canvas(cog_bg().copy())
    s0, s1 = tl.scenes["cogtrain"]
    u = clamp((t - s0) / (T("ct_top", 0.8) - s0))
    front = lerp(-120, 1500, u)
    ang = SLOPE
    L = 300
    cars = [(front - 160, True), (front - 160 - L - 16, False)]
    for cx, is_front in cars:
        cy = slope_y(cx) - 4
        P.cog_car(c, cx, cy, ang, L, 130, front=is_front)
    # passengers in the front car windows
    cx = front - 160
    cy = slope_y(cx) - 4
    for k, who in enumerate(("wolli", "luna", "whiskers")):
        wx_local = -L / 2 + 24 + k * (L - 40) / 3 + (L - 80) / 6
        px, py = P.rot([(wx_local, -130 + 76)], -ang, cx, cy)[0]
        if who == "wolli":
            P.sheep(c, px - 26, py + 46, 0.55, 1, t, mouth=tl.mouth("wolli", t), eyes="happy" if t > T("ct_tiny") else "open",
                    look=(-1, 1))
        else:
            kat(c, tl, t, who, px - 14, py + 58, 0.5, 1 if who == "whiskers" else -1, "sit",
                eyes="happy" if who == "luna" else "open", look=(1, -1), mouth=0)
    # redraw the wall below the windows on top of the passengers
    c_lower(c, cx, cy, ang, L, 130)
    P.chough(c, (t * 80) % (W + 300) - 150, 180 + 30 * math.sin(t * 0.7), t, 0.9, 1, fly=1)
    return finish(c, tl, t)


def c_lower(c, x, y, ang, length, height, col=(206, 40, 44)):
    hl = length / 2
    pts = P.rot([(-hl, -height + 76), (hl, -height + 76), (hl, 0), (-hl, 0)], -ang, x, y)
    c.poly(pts, col, w=3)
    pts2 = P.rot([(-hl, -20), (hl, -20), (hl, 0), (-hl, 0)], -ang, x, y)
    c.poly(pts2, mix(col, (0, 0, 0), 0.3), ol=None)
    pts3 = P.rot([(-hl + 10, -height + 92), (hl - 10, -height + 92)], -ang, x, y)
    c.line(pts3, (250, 250, 250), 4, cap=False)
    for wx in (-hl + 50, hl - 50):
        px, py = P.rot([(wx, 4)], -ang, x, y)[0]
        P.wheel(c, px, py, 16)


# ================================================================== meadow

MG = 610
WHISK_X = 500
BELL = (890, 604)
MAMA_X = 1060


def meadow_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (92, 120, 200)), (0.45, (236, 170, 150)), (0.7, (255, 210, 150)), (1, (255, 220, 170))]))
        P.peak(c, 180, 420, 560, 220, col=(130, 120, 160), shade=(104, 96, 136), snow=(255, 236, 230))
        P.matterhorn(c, 760, 460, 0.92, P.matter_pal(0.35, (255, 170, 130)))
        # rolling high meadow
        c.poly([(0, 470), (300, 446), (600, 470), (900, 450), (W, 470), (W, H), (0, H)], (126, 170, 90), ol=None)
        c.poly([(0, 540), (400, 520), (760, 548), (960, 520), (1100, 498), (W, 510), (W, H), (0, H)],
               (110, 160, 80), ol=OUT, w=2)
        # rock outcrop on the right (the chough sits here)
        c.poly([(1120, 520), (1150, 470), (1210, 452), (1260, 480), (1280, 520)], (140, 132, 136), w=2.5)
        c.poly([(1150, 470), (1210, 452), (1200, 470), (1160, 480)], (170, 164, 166), ol=None)
        c.rect(0, MG - 30, W, H, (120, 174, 88), ol=None)
        c.poly([(0, MG - 30), (W, MG - 40), (W, MG - 20), (0, MG - 10)], (110, 160, 80), ol=None)
        rng = np.random.default_rng(14)
        P.meadow_flowers(c, rng, 0, W, 520, 720, 260)
        for k in range(14):
            P.edelweiss(c, rng.uniform(20, W - 20), rng.uniform(640, 715), rng.uniform(0.9, 1.3))
        return c.img
    return cached("meadow", make)


def puff(c, x, y, dt, col=(250, 250, 250)):
    if dt < 0 or dt > 1.0:
        return
    for k in range(5):
        a = k * 1.3
        r = 8 + 30 * dt
        c.circle(x + math.cos(a) * 26 * dt + 30 * dt, y + math.sin(a) * 16 * dt - 20 * dt, r * (1 - dt * 0.6),
                 mix(col, (200, 200, 200), dt), ol=None)


def tears(c, x, y, t):
    for k in range(2):
        u = (t * 1.2 + k * 0.5) % 1
        c.ellipse(x + (k * 2 - 1) * 12, y + 30 * u, 3, 5, (150, 200, 250), w=1)


def meadow(tl, t):
    T = tl.t
    c = Canvas(meadow_bg().copy())
    # evening falls through the scene; brightens a little with the reunion
    dusk = 0.35 * tl.prog("m_sank", t, 0, 1) + 0.15 * tl.prog("m_think", t, 0, 1) - 0.25 * tl.prog("m_bwoo", t, 0.3, 1)
    # the Matterhorn catches the sound: a warm rim glow while the alphorn plays
    if T("m_bwoo") <= t:
        k = math.sin(math.pi * clamp(tl.prog("m_bwoo", t, 0.05, 1.0))) * 0.8
        P.matterhorn(c, 760, 460, 0.92, P.matter_pal(0.35 + 0.4 * k, (255, 170, 130)), glow_rim=((255, 230, 160), k))
    # chough on the rock flies off at the squawk
    fly_t = t - T("m_blow2", 0.3)
    if fly_t < 0:
        P.chough(c, 1200, 456, t, 1.1, -1)
    elif fly_t < 3:
        P.chough(c, 1200 + 160 * fly_t, 456 - 140 * fly_t, t, 1.1, 1, fly=1)
    # the flock comes over the hill
    if t >= T("m_bwoo", 0.6):
        u = clamp((t - T("m_bwoo", 0.6)) / (T("m_flock", 1) - T("m_bwoo", 0.6)))
        for k, (fx, fy, fs, sd) in enumerate(((1180, 520, 0.7, 21), (1250, 536, 0.75, 22), (1130, 548, 0.8, 23),
                                             (1220, 566, 0.85, 24), (1290, 590, 0.9, 25))):
            uk = clamp(u * 1.6 - k * 0.12)
            if uk <= 0:
                continue
            x = lerp(fx + 260, fx - 40, ease(uk))
            P.sheep(c, x, fy, fs, -1, t + k, walk=x / 10 if uk < 1 else 0, seed=sd, eyes="happy" if uk >= 1 else "open")
    # Mama sheep
    mama_in = clamp((t - T("m_flock", 0.3)) / (T("m_found") - T("m_flock", 0.3))) if t >= T("m_flock", 0.3) else 0
    if mama_in > 0:
        mx = lerp(1400, MAMA_X, ease(mama_in))
        P.sheep(c, mx, MG + 10, 1.25, -1, t, walk=mx / 12 if mama_in < 1 else 0, seed=30,
                eyes="happy" if t >= T("m_found") else "open", tilt=1 if t >= T("m_hug") else 0)
    # Wolli
    wk = [(tl.scenes["meadow"][0], 285)]
    if t >= T("m_found") - 0.6:
        wk = [(T("m_found") - 0.6, 285), (T("m_found", 1) + 0.6, MAMA_X - 130)]
    sad = T_in(tl, t, "m_sank", "m_saved")
    calling = T_in(tl, t, "m_mama", "m_quick")
    wface = 1 if (calling or t >= T("m_bwoo")) else 1
    weyes = "sad" if sad else ("happy" if t >= T("m_found") or T_in(tl, t, "m_saved", "m_friend") else "open")
    wx = actor(c, tl, t, "wolli", wk, MG + 6, 1.0, wface, eyes=weyes, look=(1, -1) if calling else (1, 0),
               tilt=1 if t >= T("m_hug") else 0, blush=T_in(tl, t, "m_special", "m_breath"))
    if T_in(tl, t, "m_never", "m_give"):
        tears(c, wx + 60, MG - 100, t)
    # Wolli's chocolate gift
    if T("m_give", 0.5) <= t < T("m_found") - 0.6:
        P.choc_matterhorn(c, wx + 66, MG - 60, 0.5)
    # Luna
    covering = T_in(tl, t, "m_blow2", "m_broken")
    kat(c, tl, t, "luna", 105, MG, 1.0, 1, "sit",
        eyes="closed" if covering else ("happy" if t >= T("m_found") else "open"),
        look=(1, 0), mouth=tl.mouth("luna", t), head_dy=8 if covering else 0)
    # Whiskers and the alphorn
    blowing = T_in(tl, t, "m_blow1", "m_broken") or T_in(tl, t, "m_breath", "m_found")
    giving = T_in(tl, t, "m_think", "m_breath")
    face = -1 if giving else 1
    if blowing:
        cheeks = 1.0 if (T_in(tl, t, "m_bwoo", "m_flock") or T("m_blow1", 0.25) <= t < T("m_blow1", 0.6)
                         or T("m_blow2", 0.2) <= t < T("m_blow2", 0.7)) else 0.4
        squash = 1.0 + 0.04 * cheeks * math.sin(t * 20)
        mpx, mpy = WHISK_X + 69, MG - 71
        P.alphorn(c, mpx, mpy, BELL[0], BELL[1], 1.0)
        kat(c, tl, t, "whiskers", WHISK_X, MG, 1.0, 1, "stand",
            eyes="closed" if T_in(tl, t, "m_bwoo", "m_flock") else ("wide" if T_in(tl, t, "m_blow2", "m_broken") else "open"),
            mouth=0.25, squash=squash)
        P.alphorn(c, mpx, mpy, mpx + 40, mpy + 6, 1.0, painted=False) if False else None
    else:
        P.alphorn(c, WHISK_X + 80, MG - 4, BELL[0], BELL[1], 1.0)
        held = giving and t < T("m_give", 0.5)
        kat(c, tl, t, "whiskers", WHISK_X, MG, 1.0, face, "sit" if not giving else "stand",
            eyes="happy" if T_in(tl, t, "m_special", "m_breath") or t >= T("m_found") else "open",
            look=(0, 1) if T_in(tl, t, "m_think", "m_give") else (1, 0))
        if held:
            P.choc_matterhorn(c, WHISK_X - 70, MG - 70, 0.5)
    # sounds
    if T_in(tl, t, "m_blow1", "m_blow2"):
        puff(c, BELL[0] + 20, BELL[1] - 30, (t - T("m_blow1", 0.35)) / 0.8)
    if T_in(tl, t, "m_blow2", "m_broken"):
        dt = t - T("m_blow2", 0.25)
        if 0 < dt < 1.2:
            for k in range(3):
                c.text(BELL[0] + 40 + 30 * k + 10 * math.sin(t * 20 + k), BELL[1] - 60 - 40 * dt - 20 * k,
                       "!" if k % 2 else "?", 30, (255, 230, 120), stroke=2)
    if T_in(tl, t, "m_bwoo", "m_found"):
        P.sound_rings(c, BELL[0] + 16, BELL[1] - 28, T("m_bwoo"), t, n=5, speed=180, maxr=520)
        for k in range(4):
            u = ((t - T("m_bwoo")) * 0.4 + k / 4) % 1
            c.text(BELL[0] + 40 + 260 * u, BELL[1] - 60 - 160 * u + 20 * math.sin(t * 3 + k), "♪",
                   26 + 10 * (1 - u), mix((255, 240, 180), (240, 200, 150), u), stroke=2)
    # hearts for the reunion
    if t >= T("m_found"):
        for k in range(4):
            u = ((t - T("m_found")) * 0.5 + k / 4) % 1
            hx = (wx + MAMA_X) / 2 + 30 * math.sin(k * 2 + t)
            heart(c, hx, MG - 150 - 120 * u, 10 * (1 - u * 0.5), (240, 90, 110))
    if dusk > 0:
        P.overlay(c, (50, 40, 90), dusk * 0.5)
    return finish(c, tl, t)


def heart(c, x, y, r, col):
    c.circle(x - r * 0.5, y, r * 0.6, col, ol=None)
    c.circle(x + r * 0.5, y, r * 0.6, col, ol=None)
    c.poly([(x - r * 1.05, y + r * 0.2), (x + r * 1.05, y + r * 0.2), (x, y + r * 1.3)], col, ol=None)


# =============================================================== alpenglow

def glow_ground(c, gk):
    c.poly([(0, 540), (300, 520), (640, 548), (1000, 520), (W, 536), (W, H), (0, H)],
           mix((40, 50, 70), (110, 150, 90), gk), ol=None)
    # foreground hill where everyone sits
    c.poly([(0, 600), (240, 570), (560, 590), (760, 620), (W, 640), (W, H), (0, H)],
           mix((30, 36, 54), (86, 130, 70), gk), ol=OUT, w=2)


def glow_sky(k):
    """Pre-dawn blue -> pink -> golden morning (k 0..1)."""
    q = int(round(k * 24))

    def make():
        kk = q / 24
        top = mix(mix((24, 30, 76), (110, 120, 200), clamp(kk * 1.5)), (120, 180, 240), clamp(kk * 2 - 1))
        mid = mix(mix((70, 60, 120), (246, 160, 170), clamp(kk * 1.6)), (255, 214, 150), clamp(kk * 2 - 1))
        low = mix(mix((110, 80, 130), (255, 196, 170), clamp(kk * 1.6)), (255, 236, 190), clamp(kk * 2 - 1))
        c = Canvas(sky(W, H, [(0, top), (0.55, mid), (1, low)]))
        if kk < 0.5:
            D.stars(c, 4, int(60 * (1 - kk * 2)), W, 200)
        glow = mix((255, 120, 150), (255, 200, 90), clamp(kk * 2 - 0.8))
        gk = clamp(kk * 1.4)
        night = clamp(1 - kk * 2.2)
        P.peak(c, 180, 520, 620, 260, col=mix((70, 70, 110), (190, 150, 170), gk), shade=mix((50, 52, 90), (160, 120, 150), gk),
               snow=mix((150, 160, 200), mix((255, 220, 220), (255, 236, 200), gk), gk))
        P.peak(c, 1140, 520, 560, 240, col=mix((70, 70, 110), (190, 150, 170), gk), shade=mix((50, 52, 90), (160, 120, 150), gk),
               snow=mix((150, 160, 200), mix((255, 220, 220), (255, 236, 200), gk), gk))
        P.matterhorn(c, 690, 540, 1.05, P.matter_pal(gk, glow, night=night))
        glow_ground(c, gk)
        return c.img
    return cached(("glow", q), make)


def alpenglow(tl, t):
    T = tl.t
    k = ease(tl.prog("a_glow", t, 0.0, 1.0)) * 0.85 + 0.15 * tl.prog("a_gold", t, 0, 1)
    k = clamp(k)
    c = Canvas(glow_sky(k).copy())
    # sun appears on the horizon right side late
    if k > 0.7:
        sk = (k - 0.7) / 0.3
        c.glow(1180, 540 - 40 * sk, 110, 110, (255, 246, 200), mix((255, 214, 150), (255, 236, 190), 0.5), steps=8)
        c.circle(1180, 540 - 40 * sk, 30, (255, 248, 210), ol=None)
        glow_ground(c, clamp(int(round(k * 24)) / 24 * 1.4))
    tint = (mix((30, 30, 70), (255, 200, 150), k), 0.35 * (1 - k))
    c.tint = tint
    # the flock and friends on the hill
    for x, y, s, f, sd in ((960, 652, 0.6, -1, 21), (1060, 662, 0.65, -1, 22), (1160, 668, 0.6, -1, 23),
                           (880, 664, 0.55, -1, 24)):
        P.sheep(c, x, y, s, f, t + sd, eyes="happy" if k > 0.5 else "open", seed=sd, look=(-1, -1))
    P.sheep(c, 690, 660, 0.85, -1, t, seed=30, eyes="happy" if k > 0.4 else "open")
    wolli(c, tl, t, 560, 650, 0.7, -1, eyes="happy" if T("a_gold") <= t and tl.mouth("wolli", t) < 0.2 else "open",
          look=(-1, -1))
    kat(c, tl, t, "luna", 330, 652, 0.75, 1, "sit", look=(1, -1),
        eyes="happy" if T_in(tl, t, "a_proud", "a_hold") and tl.mouth("luna", t) < 0.1 else "open")
    kat(c, tl, t, "whiskers", 420, 646, 0.78, 1, "sit", look=(1, -1),
        eyes="happy" if t >= T("a_proud", 0.5) else ("wide" if T_in(tl, t, "a_glow", "a_proud") and k > 0.5 else "open"))
    c.tint = None
    return finish(c, tl, t, 0.35)


# ==================================================================== home

SILL = 556


def home_bg():
    def make():
        wall = (232, 214, 186)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, H, mix(wall, (255, 255, 255), 0.25), ol=None)
        win = Canvas(sky(860 * 1, 470, [(0, (90, 110, 190)), (0.5, (240, 160, 150)), (1, (255, 210, 150))]),
                     size=(860, 470))
        win.glow(620, 380, 160, 120, (255, 240, 190), (250, 190, 150), steps=8)
        win.circle(620, 380, 34, (255, 244, 200), ol=None)
        win.poly([(0, 360), (300, 330), (600, 380), (860, 340), (860, 470), (0, 470)], (90, 140, 80), ol=None)
        for x, sx in ((120, 0.8), (720, 1.0)):
            D.tree(win, x, 400, sx, leaf=(70, 130, 70))
        for x in range(40, 860, 46):
            win.rect(x, 390, x + 14, 440, (236, 226, 210), ol=None)
        win.rect(0, 404, 860, 412, (236, 226, 210), ol=None)
        D.bush(win, 420, 470, 1.6, col=(60, 126, 66))
        c.img.paste(win.img, (330 * SS, 74 * SS))
        c.rect(326, 70, 1194, 548, None, w=10)
        c.line([(760, 76), (760, 546)], (246, 242, 236), 10, cap=False)
        c.rect(326, 70, 1194, 548, None, ol=(246, 242, 236), w=6)
        # curtains
        for x0, x1 in ((270, 340), (1180, 1250)):
            c.rect(x0, 30, x1, 600, (200, 60, 60), r=10)
            for xx in range(int(x0) + 16, int(x1), 22):
                c.line([(xx, 40), (xx, 590)], (170, 46, 50), 3, cap=False)
            for yy in range(60, 600, 60):
                c.circle(lerp(x0, x1, 0.5), yy, 4, (250, 250, 250), ol=None)
        c.rect(250, 20, 1270, 36, (150, 100, 60))
        c.rect(0, 600, W, H, mix(wall, (0, 0, 0), 0.08), ol=None)
        c.rect(290, SILL - 6, 1230, SILL + 26, (250, 246, 236), r=5)
        P.geraniums(c, 1000, 1160, SILL - 14)
        return c.img
    return cached("home", make)


def home(tl, t):
    T = tl.t
    c = Canvas(home_bg().copy())
    out = 0.0
    if T("h_cuckoo", 0.1) <= t < T("h_cuckoo", 0.8):
        u = tl.prog("h_cuckoo", t, 0.1, 0.8)
        out = abs(math.sin(u * math.pi * 2)) if u < 1 else 0
    P.cuckoo_clock(c, 140, 120, 0.9, out, t)
    if out > 0.05:
        c.text(140, 80, "CUCKOO!", 22 + 14 * out, (255, 250, 220), stroke=3, stroke_fill=(110, 60, 30))
    curl = t >= T("h_curl")
    c.tint = ((255, 170, 120), 0.08)
    if not curl:
        startle = T_in(tl, t, "h_cuckoo", "h_words")
        kat(c, tl, t, "luna", 460, SILL, 1.2, 1, "sit",
            eyes="happy" if T("h_words", 0.5) <= t else "open",
            mouth=laughing(t) * 0.6 if T("h_words", 0.9) <= t else tl.mouth("luna", t))
        # Luna shares her chocolate Matterhorn with Pip
        P.choc_matterhorn(c, 560, SILL - 6, 0.55)
        D.mouse(c, 640, SILL + 2, 1.8, -1 if t < T("h_better") else 1, t, mouth=tl.mouth("pip", t),
                eyes="happy" if T("h_words", 0.5) <= t else "open")
        hop = math.sin(math.pi * clamp(tl.prog("h_cuckoo", t, 0.1, 0.45))) * 40 if startle else 0
        kat(c, tl, t, "whiskers", 860, SILL - hop, 1.2, -1, "sit",
            eyes="wide" if startle and t < T("h_cuckoo", 0.7) else "open",
            look=(1, -0.5) if T_in(tl, t, "h_cuckoo", "h_curl") else (1, 0.3))
        if T_in(tl, t, "h_words", "h_curl"):
            # grumpy glare lines at the clock
            for k in range(3):
                c.line([(760 - 20 * k, 380 - 12 * k), (740 - 20 * k, 372 - 12 * k)], OUT, 3)
    else:
        kat(c, tl, t, "luna", 520, SILL + 2, 1.1, 1, "sleep", mouth=0)
        D.mouse(c, 680, SILL + 2, 1.5, -1, t, eyes="closed")
        kat(c, tl, t, "whiskers", 830, SILL + 2, 1.1, -1, "sleep", mouth=0)
        D.zzz(c, 850, 430, t)
    c.tint = None
    k = ease(tl.prog("h_end", t, 0.15, 0.45))
    if k > 0:
        c.text(W / 2, 650, "The End", 30 + 44 * k, mix((232, 214, 186), (255, 250, 236), k), stroke=4 * k,
               stroke_fill=(90, 50, 40))
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "hedge": hedge, "trailer": trailer_scene, "village": village,
               "chocolate": chocolate, "cogtrain": cogtrain, "meadow": meadow, "alpenglow": alpenglow,
               "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["tr_three", "tr_night", "tr_taxi", "h_curl"]
