"""Paris -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync with the speech. Static backgrounds are drawn once and cached; wide or
tall backgrounds are cropped by a moving camera.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.paris import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA, "colette": P.COLETTE}
SEED = {"whiskers": 0.0, "luna": 1.3, "colette": 2.6, "pip": 2.1}
NIGHT = ((40, 50, 115), 0.35)
DUSK = ((120, 70, 130), 0.18)

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


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", pal=None, walk=0.0, **kw):
    """Draw one of the cats (with Colette's beret)."""
    mouth = kw.pop("mouth", tl.mouth(who, t))
    hd = kw.get("head_dy", 0.0)
    D.cat(c, x, y, pal or PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if who == "colette":
        P.beret(c, x, y, s, face, pose, walk, hd)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", pal=None, **kw):
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
    elif who == "gaston":
        mouth = kw.pop("mouth", tl.mouth("gaston", t))
        P.bulldog(c, x, y, s, face, t, walk=x / 14 if moving else 0.0, mouth=mouth, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kitty(c, tl, t, who, x, y, s, face, pose, pal, walk=x / 12 if moving else 0.0, **kw)
    return x


def mouth_croissant(c, x, y, s, face, pose="stand", walk=0.0):
    hx, hy = P.head_pos(pose, walk)
    P.croissant(c, x + face * (hx + 18) * s, y + (hy + 22) * s, 0.55 * s, 0.25 * face)


def poof(c, x, y, k, r=120, seed=1):
    """A flour cloud: k=0 start, 1 gone."""
    if not 0 <= k < 1:
        return
    rng = np.random.default_rng(seed)
    a = 1 - ease(k)
    for _ in range(16):
        ang, d = rng.uniform(0, math.tau), rng.uniform(0.1, 1.0)
        rr = r * (0.3 + 0.7 * ease(min(1, k * 3))) * d
        px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr * 0.7
        c.circle(px, py, (18 + 34 * rng.random()) * (0.5 + 0.8 * a) * (0.4 + 0.6 * min(1, k * 4)),
                 mix((255, 255, 255), (235, 228, 215), 1 - a), ol=None)


def sky_bands(c, x0, y0, x1, y1, stops, n=24):
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        col = stops[-1][1]
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= u0 <= p1:
                col = mix(c0, c1, (u0 - p0) / max(1e-6, p1 - p0))
                break
        c.rect(x0, lerp(y0, y1, u0), x1, lerp(y0, y1, u1) + 1, col, ol=None)


def skyline(c, rng, x0, x1, base, hmin, hmax, col, win=None, p=0.3, roofs=True):
    x = x0
    while x < x1:
        w = min(rng.uniform(50, 120), x1 - x)
        h = rng.uniform(hmin, hmax)
        c.rect(x, base - h, x + w + 1, base + 2, col, ol=None)
        if roofs:
            c.poly([(x, base - h), (x + 8, base - h - 18), (x + w - 8, base - h - 18), (x + w, base - h)], col,
                   ol=None)
            if rng.random() < 0.6:
                cx = x + rng.uniform(10, w - 20)
                c.rect(cx, base - h - 30, cx + 9, base - h - 10, col, ol=None)
        if win:
            for wy in np.arange(base - h + 14, base - 6, 16):
                for wx in np.arange(x + 8, x + w - 8, 14):
                    if rng.random() < p:
                        c.rect(wx, wy, wx + 5, wy + 7, win, ol=None)
        x += w


# =================================================================== night panorama (title + sparkle)

TOWER = (960, 548, 420)          # x, base y, height
NIGHT_SKY = (34, 40, 92)


def panorama_back():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (10, 14, 40)), (0.45, NIGHT_SKY), (0.75, (84, 66, 128)),
                                               (1, (84, 66, 128))]))
        D.stars(c, 11, 150, W, 420)
        D.moon(c, 1185, 92, 40, sky=(16, 22, 60))
        rng = np.random.default_rng(4)
        skyline(c, rng, -20, W + 40, 540, 30, 80, (58, 54, 104), win=(220, 180, 120), p=0.15)
        return c.img
    return cached("pan_back", make)


def panorama_front():
    def make():
        c = rgba(W, H)
        rng = np.random.default_rng(9)
        skyline(c, rng, -40, W + 40, 600, 40, 70, (40, 40, 82), win=(255, 205, 120), p=0.3)
        # stone balustrade of the Sacre-Coeur terrace
        stone, sd = (126, 118, 150), (96, 90, 122)
        c.rect(-10, 600, W + 10, 618, stone, w=2.5)
        for x in range(10, W, 44):
            c.poly([(x, 620), (x + 26, 620), (x + 20, 640), (x + 26, 668), (x + 20, 690), (x + 6, 690), (x, 668),
                    (x + 6, 640)], sd, w=2)
        c.rect(-10, 688, W + 10, H + 10, stone, w=2.5)
        c.rect(-10, 590, W + 10, 604, mix(stone, (255, 255, 255), 0.15), w=2.5, r=3)
        return c.img
    return cached("pan_front", make)


def tower_glow_mask():
    def make():
        from PIL import ImageDraw, ImageFilter
        m = Image.new("L", (W * SS, H * SS), 0)
        x, y, h = TOWER
        ImageDraw.Draw(m).ellipse([(x - 0.2 * h) * SS, (y - 0.95 * h) * SS, (x + 0.2 * h) * SS, (y + 0.05 * h) * SS],
                                  fill=255)
        return m.filter(ImageFilter.GaussianBlur(60 * SS))
    return cached("tglow", make)


def panorama(t, lights, sparkle):
    c = Canvas(panorama_back().copy())
    x, y, h = TOWER
    if lights > 0.05:
        a = 0.45 * lights
        c.img.paste(Image.new("RGB", c.img.size, (255, 190, 100)), (0, 0),
                    tower_glow_mask().point(lambda v: int(v * a)))
    P.eiffel(c, x, y, h, col=(70, 62, 92), lights=lights, sparkle=sparkle, t=t, w=2.0)
    paste_layer(c, panorama_front())
    return c


SILL = 592       # where the cats sit on the balustrade


def title(tl, t):
    T = tl.t
    c = panorama(t, 1.0, 0.6 + 0.4 * math.sin(t * 1.3) ** 2)
    c.tint = ((30, 36, 90), 0.3)
    kitty(c, tl, t, "luna", 300, SILL, 0.85, 1, "sit", look=(1, -1), tail=math.sin(t * 1.5), mouth=0)
    D.mouse(c, 386, SILL, 1.0, 1, t, eyes="open")
    kitty(c, tl, t, "whiskers", 470, SILL, 0.9, 1, "sit", look=(1, -1), mouth=0)
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.7))
    c.text(430, 150 - 30 * (1 - k), "Whiskers and the", 44, mix((30, 34, 80), (255, 230, 170), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(430, 240, "CITY OF LIGHTS", 24 + 52 * k2, mix((30, 34, 80), (255, 236, 160), k2), stroke=5 * k2)
    return c


# =================================================================== postcard

SILL_Y = 372


def postcard_art(c, x, y, s, t, border=True):
    """The postcard: the Eiffel Tower sparkling at night. (x, y) top-left; 300x200 units."""
    c.push(x, y, s)
    if border:
        c.rect(-10, -10, 310, 210, (252, 250, 240), w=3, r=6)
    sky_bands(c, 0, 0, 300, 200, [(0, (16, 22, 64)), (0.7, (60, 56, 120)), (1, (110, 80, 140))], n=16)
    D.stars(c, 3, 26, 300, 110)
    rng = np.random.default_rng(2)
    skyline(c, rng, 0, 300, 200, 12, 34, (40, 40, 80), win=(255, 210, 120), p=0.3, roofs=False)
    P.eiffel(c, 200, 192, 170, col=(70, 62, 92), lights=1.0, sparkle=0.8, t=t, w=1.2)
    c.text(70, 40, "PARIS", 26, (255, 225, 140), stroke=2)
    c.rect(0, 0, 300, 200, None, w=2)
    c.pop()


def card_flight(c, x, y, ang, s=1.0):
    """The small postcard tumbling through the air, as a rotated quad."""
    pts = []
    for px, py in ((-30, -20), (30, -20), (30, 20), (-30, 20)):
        pts.append((x + (px * math.cos(ang) - py * math.sin(ang)) * s, y + (px * math.sin(ang) + py * math.cos(ang)) * s))
    c.poly(pts, (252, 250, 240), w=2)
    inner = [(lerp(x, px, 0.78), lerp(y, py, 0.78)) for px, py in pts]
    c.poly(inner, (50, 52, 110), ol=None)
    c.circle(x + 6 * s, y, 4 * s, (255, 210, 110), ol=None)


def postcard(tl, t):
    T = tl.t
    c = Canvas(MF.room(False).copy())
    # --- the basket slides in
    bx = smooth(t, [(T("p_basket"), -220), (T("p_basket", 0.8), 300)])
    jig = 0.0
    if T("p_jump", 0.8) < t < T("p_jump", 1.0):
        jig = math.sin(t * 40) * 4
    lid = 0.0
    if t >= T("p_jump"):
        lid = ease(tl.prog("p_jump", t, 0.0, 0.08)) * (1 - ease(tl.prog("p_jump", t, 0.78, 0.86)))
    if t > T("p_jump"):
        P.basket(c, bx + jig, 612, 1.2, back=True)
    # cats already inside the basket
    if t >= T("p_jump", 0.3):
        dk = ease(tl.prog("p_jump", t, 0.3, 0.4))
        kitty(c, tl, t, "luna", bx - 34, 600, 0.72, 1, "sit", head_dy=lerp(0, 60, ease(tl.prog("p_jump", t, 0.7, 0.8))),
              look=(1, -1))
    if t >= T("p_jump", 0.66):
        kitty(c, tl, t, "whiskers", bx + 30, 600, 0.72, -1, "sit",
              head_dy=lerp(-10, 60, ease(tl.prog("p_jump", t, 0.7, 0.8))), eyes="happy")
    if t > T("p_basket") - 0.1:
        P.basket(c, bx + jig, 612, 1.2, lid=lid)

    # --- Whiskers on the windowsill
    card_on_face = T("p_wind", 0.75) <= t < T("p_mmf", 0.25)
    if t < T("p_mmf", 0.1):
        D.cat(c, 960, SILL_Y, D.WHISKERS, 0.8, 1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
        if t < T("p_wind", 0.6):
            D.zzz(c, 1010, 300, t)
    elif t < T("p_jump", 0.35):
        startle = clamp((t - T("p_mmf", 0.1)) / 0.3)
        eyes = "wide" if t < T("p_card") else "open"
        if T("p_crois") <= t < T("p_crois", 1) + 0.3:
            eyes = "happy"
        face = -1
        D.cat(c, 960, SILL_Y, D.WHISKERS, 0.8, face, "sit", t=t, mouth=tl.mouth("whiskers", t), eyes=eyes,
              head_dy=-8 * (1 - startle), look=(1, 0.6))
    elif t < T("p_jump", 0.68):
        u = tl.prog("p_jump", t, 0.35, 0.68)
        D.cat(c, lerp(960, bx + 30, u), lerp(SILL_Y, 600, u) + arc_y(u, 140), D.WHISKERS, 0.75, -1, "leap",
              t=t, eyes="wide", mouth=0.4)
    # the card
    if T("p_wind") <= t < T("p_wind", 0.75):
        u = tl.prog("p_wind", t, 0.0, 0.75)
        card_flight(c, lerp(1250, 1000, ease(u)) + 60 * math.sin(u * 7), lerp(-40, 338, u), u * 9, 1.0)
    elif card_on_face:
        card_flight(c, 1000, 338, 0.3, 1.0)
    elif T("p_mmf", 0.25) <= t < T("p_card"):
        u = tl.prog("p_mmf", t, 0.25, 0.9)
        card_flight(c, lerp(1000, 760, u), lerp(338, 600, ease(u)), 0.3 + u * 6, 1.0)
    elif T("p_says", 1) <= t < T("p_jump"):
        card_flight(c, 760, 606, math.pi / 2 + 0.1, 0.7)

    # --- Luna
    if t < T("p_jump", 0.05):
        lx = 640 if t < T("p_card") else 700
        if t >= T("p_says", 1):
            lx = 700
        sit = t < T("p_wind", 0.5)
        lf = 1
        if t >= T("p_plan") - 0.3:
            lf = -1
        kitty(c, tl, t, "luna", lx, 612, 1.0, lf, "sit" if sit else "stand",
              look=(1, -1) if t < T("p_card") else (1, -0.5),
              eyes="happy" if T("p_says") <= t < T("p_crois") else "open")
    elif t < T("p_jump", 0.3):
        u = tl.prog("p_jump", t, 0.05, 0.3)
        D.cat(c, lerp(700, bx - 34, u), 612 + arc_y(u, 170) - 12 * u, D.LUNA, 0.9, -1, "leap", t=t, seed=1.3)

    # --- close-up of the postcard
    k = ease(tl.prog("p_card", t, 0.0, 0.12)) * (1 - ease(tl.prog("p_says", t, 0.92, 1.0)))
    if t > T("p_says", 1):
        k = 0
    if k > 0.01:
        s = 2.2 * k
        postcard_art(c, 640 - 150 * s, 330 - 100 * s, s, t)
    return c


# =================================================================== train

TW = 2400        # countryside period


def wrap_draw(fn):
    """Draw something periodic: fn(c, dx) is called for dx in (-TW, 0, TW)."""
    def go(c):
        for dx in (-TW, 0, TW):
            fn(c, dx)
    return go


def country_far(night=False):
    def make():
        if night:
            sky = [(0, (14, 18, 48)), (0.6, (40, 44, 96)), (1, (60, 60, 110))]
        else:
            sky = [(0, (110, 180, 240)), (0.6, (200, 230, 255)), (1, (220, 238, 255))]
        c = Canvas(D.gradient((TW + W) * SS, H * SS, sky), size=(TW + W, H))
        rng = np.random.default_rng(3)
        clouds = [(rng.uniform(0, TW), rng.uniform(60, 200), rng.uniform(0.6, 1.1)) for _ in range(6)]
        for dx in (0, TW):
            if not night:
                for x, y, s in clouds:
                    D.cloud(c, x + dx, y, s)
        pts = [(x, 430 + 40 * math.sin(math.tau * x / 1200) + 20 * math.sin(math.tau * x / 800 + 1))
               for x in range(0, TW + W + 40, 40)]
        c.poly(pts + [(TW + W, H), (0, H)], (150, 200, 150) if not night else (40, 60, 80), ol=None)
        pts = [(x, 480 + 25 * math.sin(math.tau * x / 600 + 2)) for x in range(0, TW + W + 40, 40)]
        c.poly(pts + [(TW + W, H), (0, H)], (130, 190, 110) if not night else (34, 52, 66), ol=None)
        # far villages and church spires
        for vx in (300, 1500):
            for dx in (0, TW):
                x0 = vx + dx
                for k in range(4):
                    hx = x0 + k * 34
                    c.rect(hx, 470, hx + 28, 496, (240, 225, 200) if not night else (60, 60, 90), ol=None)
                    c.poly([(hx - 3, 470), (hx + 14, 456), (hx + 31, 470)], (200, 100, 80) if not night else
                           (60, 40, 60), ol=None)
                c.rect(x0 + 140, 430, x0 + 152, 496, (230, 220, 200) if not night else (60, 60, 90), ol=None)
                c.poly([(x0 + 138, 430), (x0 + 146, 404), (x0 + 154, 430)], (110, 110, 130), ol=None)
        return c.img
    return cached(("cfar", night), make)


def country_near(night=False):
    def make():
        c = rgba(TW + W, H)
        ground = (110, 180, 90) if not night else (30, 50, 50)
        c.rect(0, 560, TW + W, H, ground, ol=None)
        c.rect(0, 640, TW + W, H, mix(ground, (0, 0, 0), 0.1), ol=None)
        rng = np.random.default_rng(7)
        trees = [(rng.uniform(0, TW), rng.uniform(0.6, 0.9)) for _ in range(9)]
        for dx in (0, TW):
            for x, s in trees:
                if x + dx < TW + W + 200:
                    if night:
                        P.tree_round(c, x + dx, 566, s * 1.2, leaf=(30, 60, 60))
                    else:
                        P.tree_round(c, x + dx, 566, s * 1.2)
        # track: ballast, sleepers, rails
        c.rect(0, 588, TW + W, 612, (150, 140, 130) if not night else (60, 60, 80), ol=None)
        for x in range(0, TW + W, 24):
            c.rect(x, 594, x + 12, 610, (120, 85, 60) if not night else (50, 40, 50), ol=None)
        c.rect(0, 596, TW + W, 600, (90, 90, 100), ol=None)
        # grass and flowers in front
        for _ in range(500):
            x, y = rng.uniform(0, TW), rng.uniform(616, H)
            for dx in (0, TW):
                if x + dx < TW + W:
                    c.line([(x + dx, y), (x + dx + rng.uniform(-6, 6), y - rng.uniform(12, 28))],
                           mix(ground, (40, 90, 30), 0.4), 2, cap=False)
        if not night:
            for _ in range(70):
                x, y = rng.uniform(0, TW), rng.uniform(625, H - 10)
                col = [(255, 255, 255), (250, 150, 190), (255, 220, 90)][rng.integers(3)]
                for dx in (0, TW):
                    if x + dx < TW + W:
                        D.flower(c, x + dx, y, col, 0.6)
        # fence posts
        for x in range(0, TW, 160):
            for dx in (0, TW):
                if x + dx < TW + W:
                    c.rect(x + dx, 540, x + dx + 8, 590, (170, 130, 90) if not night else (60, 50, 60), w=2)
        c.rect(0, 552, TW + W, 556, (170, 130, 90) if not night else (60, 50, 60), ol=None)
        return c.img
    return cached(("cnear", night), make)


def travel(tl, t, base=260.0):
    """Distance the train has travelled (px of near layer), slowing during tr_arrive."""
    T = tl.t
    t0 = T("tr_arrive", 0.3)
    if t < t0:
        return base * t
    d = base * t0
    steps = 20
    dt = (t - t0) / steps
    for k in range(steps):
        tt = t0 + (k + 0.5) * dt
        d += base * (1 - 0.85 * ease(tl.prog("tr_arrive", tt, 0.3, 1.0))) * dt
    return d


def train_outside(tl, t, arrive):
    T = tl.t
    d = travel(tl, t)
    far_off = (d * 0.12) % TW
    near_off = d % TW
    c = view(country_far(), far_off)
    if arrive:
        # Paris on the horizon
        u = tl.prog("tr_arrive", t)
        px = lerp(1300, 980, ease(u))
        rng = np.random.default_rng(5)
        skyline(c, rng, px - 420, px + 600, 492, 10, 30, (170, 180, 205), roofs=True)
        P.eiffel(c, px, 488, 300, col=(150, 140, 170), ol=(120, 110, 140), w=1.5)
    paste_layer(c, country_near(), near_off)
    wheel = d / 18
    shake = math.sin(t * 20) * 1.2
    P.train(c, 860 + 30 * math.sin(t * 0.4), 592 + shake, 0.95, t * (1.6 if not arrive else 1.0), wheel)
    return c


def train_inside_bg():
    def make():
        c = rgba(W, H)
        wall = (120, 70, 60)
        c.rect(0, 0, W, 90, wall, ol=None)
        c.rect(0, 0, 130, H, wall, ol=None)
        c.rect(1150, 0, W, H, wall, ol=None)
        c.rect(0, 400, W, H, wall, ol=None)
        for x in range(10, W, 60):
            c.line([(x, 410), (x, H)], mix(wall, (0, 0, 0), 0.15), 2, cap=False)
        c.rect(126, 86, 1154, 404, None, w=14)
        c.rect(126, 86, 1154, 404, None, ol=(200, 170, 90), w=4)
        c.line([(640, 90), (640, 400)], (200, 170, 90), 8, cap=False)
        # curtains
        for x0, x1 in ((110, 220), (1060, 1170)):
            c.poly([(x0, 70), (x1, 70), (x1 - 20, 260), (x1 - 4, 420), (x0, 420)], (200, 60, 70), w=3)
            for k in range(1, 4):
                xx = lerp(x0, x1, k / 4)
                c.line([(xx, 75), (xx - 8, 415)], (160, 40, 55), 3, cap=False)
        c.rect(90, 50, 1190, 72, (200, 170, 90), w=3, r=8)
        # luggage rack shadow and table
        c.rect(0, 420, W, 440, (70, 40, 40), ol=None)
        # seat
        seat = (60, 100, 150)
        c.rect(60, 470, 1220, 720, seat, w=3, r=30)
        c.rect(90, 440, 1190, 520, mix(seat, (255, 255, 255), 0.1), w=3, r=24)
        for x in range(150, 1180, 120):
            c.circle(x, 600, 5, mix(seat, (0, 0, 0), 0.3), ol=None)
        return c.img
    return cached("train_in", make)


BASKET_IN = (640, 662, 1.55)


def train_inside(tl, t):
    T = tl.t
    d = travel(tl, t)
    SH = 230          # look lower through the window so hills and trees show
    fx = int(round(((d * 0.12) % TW) * SS))
    c = Canvas(Image.new("RGB", (W * SS, H * SS), (110, 160, 90)))
    c.img.paste(country_far().crop((fx, SH * SS, fx + W * SS, H * SS)), (0, 0))
    nx = int(round((d % TW) * SS))
    part = country_near().crop((nx, SH * SS, nx + W * SS, H * SS))
    c.img.paste(part, (0, 0), part)
    paste_layer(c, train_inside_bg())
    bx, by, bs = BASKET_IN
    jig = math.sin(t * 22) * 1.5
    lid = ease(tl.prog("tr_inside", t, 0.1, 0.7))
    P.basket(c, bx + jig, by, bs, back=True)
    rise = ease(tl.prog("tr_inside", t, 0.4, 1.0))
    happy = T("tr_cheese") <= t < T("tr_cheese", 1) + 0.3
    kitty(c, tl, t, "luna", bx - 74, by - 30, 0.9, 1, "sit", head_dy=lerp(60, -40, rise),
          eyes="wide" if T("tr_pip") <= t < T("tr_what", 1) else "open", look=(1, -0.3))
    kitty(c, tl, t, "whiskers", bx + 74, by - 30, 0.9, -1, "sit", head_dy=lerp(60, -40, rise),
          eyes="happy" if happy else ("wide" if T("tr_pip") <= t < T("tr_what", 1) else "open"), look=(1, -0.3))
    if t >= T("tr_rustle", 0.5):
        u = ease(tl.prog("tr_rustle", t, 0.5, 1.0))
        py = by - bs * 60 - 50 * u
        D.mouse(c, bx + 2, py, 1.5, 1 if t < T("tr_brave") else -1, t, mouth=tl.mouth("pip", t),
                proud=T("tr_brave") <= t < T("tr_brave", 1) + 0.3)
        # cheese wedge Pip found
        c.poly([(bx - 30, py - 10), (bx - 4, py - 30), (bx - 4, py - 8)], (250, 210, 80), w=2)
        c.circle(bx - 14, py - 16, 3, (220, 170, 50), ol=None)
    shake = 0
    if T("tr_rustle") <= t < T("tr_rustle", 0.6):
        shake = math.sin(t * 50) * 4
    P.basket(c, bx + jig + shake, by, bs, lid=lid, tag=True)
    return c


def train(tl, t):
    T = tl.t
    if t < T("tr_inside"):
        return train_outside(tl, t, False)
    if t < T("tr_arrive"):
        return train_inside(tl, t)
    return train_outside(tl, t, True)


# =================================================================== arrival (the quay)

AW = 2600
AG = 652


def bouquiniste(c, x, y, w=120):
    c.rect(x, y - 44, x + w, y, (40, 110, 80), w=2.5)
    c.poly([(x - 4, y - 44), (x + w + 4, y - 44), (x + w, y - 58), (x, y - 58)], (50, 130, 95), w=2.5)
    for k in range(4):
        c.rect(x + 10 + k * 26, y - 36, x + 30 + k * 26, y - 12, [(220, 80, 80), (240, 220, 140), (90, 140, 210),
                                                                 (250, 250, 240)][k], w=1.5)


def quay_bg():
    def make():
        c = Canvas(D.gradient(AW * SS, H * SS, [(0, (120, 185, 240)), (0.62, (215, 236, 255)), (1, (215, 236, 255))]),
                   size=(AW, H))
        rng = np.random.default_rng(14)
        for x in range(200, AW, 560):
            D.cloud(c, x + rng.uniform(-80, 80), rng.uniform(70, 170), rng.uniform(0.7, 1.1))
        # far bank: Eiffel Tower and rooftops
        P.eiffel(c, 1900, 470, 470, w=2.2)
        x = -30
        while x < AW:
            w = rng.uniform(150, 240)
            if 1720 < x + w / 2 < 2080:
                x += w
                continue
            floors = int(rng.integers(3, 5))
            c.push(x, 470, 0.5)
            P.building(c, 0, 0, w * 2 - 6, floors, mix((236, 222, 196), (200, 210, 230), 0.35),
                       mix((120, 130, 160), (200, 210, 230), 0.35), rng)
            c.pop()
            x += w
        for x in (1760, 2040):
            P.tree_round(c, x, 472, 0.7, leaf=(110, 170, 110))
        # river
        c.rect(0, 470, AW, 528, (90, 140, 190), ol=None)
        for _ in range(80):
            x, y = rng.uniform(0, AW), rng.uniform(476, 524)
            c.line([(x, y), (x + rng.uniform(20, 50), y)], (150, 190, 225), 2, cap=False)
        # parapet
        stone = (215, 200, 170)
        c.rect(-5, 528, AW + 5, 580, stone, w=2.5)
        c.rect(-5, 520, AW + 5, 532, mix(stone, (255, 255, 255), 0.25), w=2.5, r=3)
        for x in range(0, AW, 70):
            c.line([(x, 532), (x, 580)], mix(stone, (0, 0, 0), 0.12), 2, cap=False)
        # sidewalk
        walk = (196, 190, 184)
        c.rect(0, 580, AW, H, walk, ol=None)
        for y in range(596, H, 22):
            off = 0 if (y // 22) % 2 else 18
            for x in range(-40 + off, AW, 36):
                c.rect(x, y, x + 34, y + 20, mix(walk, (255, 255, 255), rng.uniform(0, 0.2)), ol=None)
        # bouquinistes, lamps, trees
        for x in (380, 900, 1360, 2200):
            bouquiniste(c, x, 522)
        for x in (180, 700, 1180, 1660, 2120, 2480):
            P.tree_round(c, x, 600, 1.15)
        for x in (520, 1040, 1540, 2000, 2380):
            P.street_lamp(c, x, 596, 1.1)
        return c.img
    return cached("quay", make)


def arrival(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["arrival"]
    # camera
    camx = smooth(t, [(T("a_narr", 0.1), 0), (T("a_walk", 1), 700), (T("a_go", 0.2), 700), (s1, AW - W)], 0.6)
    c = view(quay_bg(), camx)
    c.push(-camx, 0)
    bx = 260
    lid = ease(tl.prog("a_out", t, 0.0, 0.2))
    P.basket(c, bx, AG, 1.2, back=True)
    P.basket(c, bx, AG, 1.2, lid=lid)
    # Colette sits on the bouquiniste box until she hops down
    if t < T("a_luna"):
        kitty(c, tl, t, "colette", 1420, 478, 0.85, -1, "sit", look=(1, 0.5),
              tail=math.sin(t * 1.4), eyes="happy" if T("a_bonjour", 0.2) < t < T("a_bonjour", 0.6) else "open")
    elif t < T("a_luna", 0.4):
        u = tl.prog("a_luna", t, 0.0, 0.4)
        D.cat(c, lerp(1420, 1380, u), lerp(478, AG, u) + arc_y(u, 60), P.COLETTE, 0.9, -1, "leap", t=t)
        P.beret(c, lerp(1420, 1380, u), lerp(478, AG, u) + arc_y(u, 60), 0.9, -1, "leap")
    else:
        actor(c, tl, t, "colette", [(T("a_luna", 0.4), 1380), (T("a_go", 0.25), 1380), (s1, 2950)], AG, 0.9,
              face=-1)
    # the travellers hop out of the basket and walk along the quay
    hop = tl.prog("a_out", t, 0.2, 0.75)
    walk_end = T("a_walk", 1)
    keys = {"luna": [(T("a_out", 0.45), 430), (T("a_narr", 0.2), 430), (walk_end, 1200), (T("a_go", 0.2), 1200),
                     (s1, 2780)],
            "whiskers": [(T("a_out", 0.75), 560), (T("a_narr", 0.25), 560), (walk_end, 960),
                         (T("a_go", 0.1), 960), (s1, 2650)],
            "pip": [(T("a_out", 0.6), 340), (T("a_narr", 0.3), 340), (walk_end, 1080), (T("a_go", 0.3), 1080),
                    (s1, 2900)]}
    starts = {"luna": (0.2, 0.45, bx - 30, 430), "pip": (0.35, 0.6, bx, 340), "whiskers": (0.5, 0.75, bx + 30, 560)}
    for who in ("whiskers", "luna", "pip"):
        a, b, x0, x1 = starts[who]
        if t < T("a_out", a):
            continue
        if t < T("a_out", b):
            u = tl.prog("a_out", t, a, b)
            x, y = lerp(x0, x1, u), lerp(AG - 60, AG, u) + arc_y(u, 90)
            if who == "pip":
                D.mouse(c, x, y, 1.4, 1, t, eyes="wide")
            else:
                D.cat(c, x, y, PAL[who], 1.0, 1, "leap", t=t, seed=SEED[who])
            continue
        if who == "pip":
            actor(c, tl, t, "pip", keys["pip"], AG + 2, 1.4, face=1,
                  eyes="happy" if T("a_narr") <= t < T("a_narr", 1) else "open")
        else:
            look = (1, -1) if T("a_narr", 0.3) <= t < T("a_walk") else (1, 0)
            eyes = "open"
            if who == "whiskers" and T("a_best") <= t < T("a_best", 1) + 0.6:
                eyes = "happy"
            face = 1
            if who == "pip" or (t >= T("a_walk", 1) and who != "whiskers"):
                face = 1
            actor(c, tl, t, who, keys[who], AG + (4 if who == "luna" else 0), 1.0, face=face, look=look, eyes=eyes)
    c.pop()
    return c


# =================================================================== bakery

FLOOR = 640
TRAY = (600, 760, 548)          # table x0, x1, top
SACK = 1000
DOOR = (1050, 1230)


def bakery_bg():
    def make():
        wall = (250, 230, 196)
        c = Canvas(bg=wall)
        for x in range(0, W, 48):
            c.rect(x + 20, 0, x + 26, 380, mix(wall, (255, 255, 255), 0.4), ol=None)
        # tiles
        c.rect(0, 380, W, 620, (245, 245, 240), ol=None)
        for y in range(380, 620, 30):
            c.line([(0, y), (W, y)], (205, 215, 225), 2, cap=False)
        for x in range(0, W, 30):
            c.line([(x, 380), (x, 620)], (205, 215, 225), 2, cap=False)
        c.rect(0, 372, W, 384, (70, 110, 170), ol=None)
        # chequered floor
        c.rect(0, 620, W, H, (240, 236, 228), ol=None)
        for y in range(620, H, 34):
            for x in range(0, W + 40, 68):
                xx = x + (34 if (y // 34) % 2 else 0)
                c.rect(xx, y, xx + 34, y + 34, (60, 62, 74), ol=None)
        # shelves with bread
        wood = (165, 110, 70)
        for y in (170, 260, 350):
            c.rect(40, y, 560, y + 12, wood, w=2)
        rng = np.random.default_rng(3)
        for k in range(9):
            P.baguette(c, 70 + k * 18, 140, 0.9, -1.35 + rng.uniform(-0.1, 0.1))
        c.rect(50, 120, 250, 170, (200, 150, 90), w=2, r=6)
        for k in range(5):
            x = 300 + k * 52
            c.ellipse(x, 146, 24, 22, (210, 150, 80))
            c.arc(x, 140, 14, 8, 200, 340, (240, 200, 140), 3)
        for k in range(7):
            x = 70 + k * 70
            c.ellipse(x, 240, 30, 18, (200, 130, 70))
            for j in (-12, 0, 12):
                c.line([(x + j - 4, 228), (x + j + 4, 248)], (240, 200, 140), 2.5)
        for k in range(8):
            P.croissant(c, 70 + k * 62, 336, 0.9)
        # window with lettering
        c.rect(620, 110, 1010, 380, (180, 215, 235), w=6, r=6)
        c.rect(620, 300, 1010, 380, (150, 190, 210), ol=None)
        c.rect(640, 220, 760, 300, (230, 220, 200), w=2)
        c.rect(780, 200, 900, 300, (220, 200, 180), w=2)
        c.rect(620, 110, 1010, 380, None, w=6, r=6)
        c.text(815, 160, "BOULANGERIE", 28, (215, 170, 60), stroke=2)
        c.rect(610, 372, 1020, 386, wood, w=2)
        # door
        x0, x1 = DOOR
        c.rect(x0, 130, x1, 622, (90, 140, 120), w=3)
        c.rect(x0 + 20, 150, x1 - 20, 420, (190, 220, 235), w=3)
        c.circle(x0 + 26, 470, 7, (230, 190, 70))
        # sacks of flour
        for x, s in ((SACK + 40, 1.0), (SACK, 1.1)):
            c.push(x, FLOOR, s)
            c.poly([(-40, 0), (-44, -70), (-30, -96), (30, -96), (44, -70), (40, 0)], (236, 226, 205), w=3)
            c.poly([(-30, -96), (-16, -112), (0, -100), (16, -112), (30, -96)], (236, 226, 205), w=2.5)
            c.text(0, -48, "FARINE", 13, (150, 110, 70))
            c.pop()
        return c.img
    return cached("bakery", make)


def counter(c):
    wood = (175, 115, 72)
    c.rect(40, 400, 580, 640, wood, w=3)
    for x in range(60, 580, 104):
        c.rect(x, 488, x + 88, 620, mix(wood, (255, 255, 255), 0.12), w=2, r=4)
    c.rect(30, 470, 590, 488, mix(wood, (0, 0, 0), 0.2), w=3)
    c.rect(50, 392, 570, 470, (200, 230, 240), w=3, r=6)
    for k in range(6):
        x = 90 + k * 82
        if k % 2:
            c.ellipse(x, 452, 26, 10, (230, 120, 140))
            c.ellipse(x, 446, 20, 6, (255, 200, 210), ol=None)
        else:
            c.rect(x - 28, 440, x + 28, 458, (150, 90, 60), w=2, r=8)
            c.rect(x - 24, 436, x + 24, 444, (110, 60, 40), ol=None)
    c.line([(60, 410), (100, 400)], (255, 255, 255), 3)


def tray_table(c, n_left):
    x0, x1, top = TRAY
    wood = (150, 100, 60)
    c.stroke([(x0 + 14, top), (x0 + 14, FLOOR)], wood, 8)
    c.stroke([(x1 - 14, top), (x1 - 14, FLOOR)], wood, 8)
    c.rect(x0, top, x1, top + 12, wood, w=2.5)
    c.rect(x0 + 6, top - 6, x1 - 6, top + 2, (190, 190, 200), w=2)
    for k in range(n_left):
        P.croissant(c, x0 + 34 + k * 30, top - 14, 0.8, 0.1 * ((k * 7) % 3 - 1))


def bakery(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["bakery"]
    c = Canvas(bakery_bg().copy())
    # bell above the door
    ring = 0.0
    for ev, f in (("b_arrive", 0.15), ("b_chase", 0.25)):
        dt = t - T(ev, f)
        if 0 < dt < 1.0:
            ring = math.sin(dt * 30) * (1 - dt)
    c.line([(1140, 108), (1140, 120)], D.OUT, 2)
    c.push(1140, 120)
    c.poly([(-10 + 6 * ring, 0), (10 + 6 * ring, 0), (14 + 8 * ring, 20), (-14 + 8 * ring, 20)], (240, 200, 70), w=2)
    c.pop()

    # stack of croissants Whiskers has taken
    taken = sum(1 for f in (0.12, 0.42, 0.75) if t >= T("b_stack", f))
    fallen = t >= T("b_poof", 0.25)

    # --- Gaston
    gk = [(s0, 330), (T("b_poof", 0.05), 330), (T("b_poof", 0.9), 720), (T("b_still", 0.2), 720),
          (T("b_still", 0.9), 770), (T("b_chase", 0.3), 770), (T("b_chase", 1.0), 1500)]
    gx = smooth(t, gk)
    behind = gx < 585
    gface = -1 if t < T("b_hey") - 0.1 else 1
    brow = 0.0
    arm = 0.0
    hold = "pin"
    if T("b_hey") <= t:
        brow = 0.8
    if T("b_statue") <= t < T("b_achoo"):
        brow = 0.2
    if t >= T("b_monster"):
        brow, arm = 1.0, 1.0
    gy = lerp(560, FLOOR, clamp((gx - 540) / 60))
    kneading = t < T("b_hey") - 0.1
    g_eyes = "wide" if T("b_achoo", 0.6) <= t < T("b_monster") else "open"

    def draw_gaston():
        v = (smooth(t + 0.05, gk) - smooth(t - 0.05, gk)) / 0.1
        mv = abs(v) > 20
        P.bulldog(c, gx, gy + (math.sin(t * 12) * 2 if kneading else 0), 1.25, gface, t,
                  walk=gx / 14 if mv else 0.0, mouth=tl.mouth("gaston", t), brow=brow, arm=arm,
                  hold=hold if t >= T("b_monster") else None, eyes=g_eyes)

    if behind:
        draw_gaston()
    counter(c)
    tray_table(c, 5 - taken if not fallen else 0)

    # --- friends near the door
    fk_end = T("b_chase", 0.75)
    for who, x, y, s in (("pip", 1100, FLOOR + 2, 1.4), ("luna", 1150, FLOOR + 4, 1.0), ("colette", 1250, FLOOR, 0.95)):
        enter = [(s0, 1350 + (x - 1100)), (T("b_arrive", 0.8), x), (T("b_chase", 0.35), x), (fk_end, 1500 + x - 1100)]
        laugh = T("b_achoo", 0.7) <= t < T("b_monster")
        eyes = "happy" if laugh else ("wide" if T("b_poof", 0.3) <= t < T("b_achoo") else "open")
        if who == "pip":
            actor(c, tl, t, "pip", enter, y, s, face=-1, eyes=eyes)
        else:
            actor(c, tl, t, who, enter, y, s, face=-1, pose="sit" if T("b_sneak") < t < T("b_chase", 0.2) else "stand",
                  eyes=eyes, look=(1, 0))

    # --- Whiskers
    flour = 0.0
    if t >= T("b_poof", 0.3):
        flour = 1.0
    if t >= T("b_achoo", 0.85):
        flour = 0.45
    pal = P.floured(D.WHISKERS, flour)
    wk = [(s0, 1380), (T("b_arrive", 1), 1000), (T("b_narr", 1), 960), (T("b_sneak", 0.9), 830),
          (T("b_wobble", 0.1), 830), (T("b_poof", 0.0), 900), (T("b_chase", 0.1), 900), (T("b_chase", 0.75), 1500)]
    wx = smooth(t, wk)
    v = (smooth(t + 0.05, wk) - smooth(t - 0.05, wk)) / 0.1
    moving = abs(v) > 20
    wface = -1
    if moving and v > 0 and t > T("b_chase"):
        wface = 1
    pose = "walk" if moving else "stand"
    eyes = "open"
    sneaking = T("b_sneak") <= t < T("b_sneak", 0.95)
    if sneaking:
        pose = "crouch"
    if T("b_narr") <= t < T("b_sneak"):
        eyes = "happy"
    if T("b_stack") <= t < T("b_wobble"):
        eyes = "happy"
    if T("b_wobble") <= t < T("b_poof", 0.3):
        eyes = "wide"
    statue = T("b_poof", 0.3) <= t < T("b_achoo")
    squash = 1.0
    if statue:
        eyes, pose = "wide", "stand"
    if T("b_achoo") <= t < T("b_achoo", 0.85):
        squash = 1 + 0.1 * math.sin(math.pi * tl.prog("b_achoo", t, 0.0, 0.85))
        eyes = "closed"
    if T("b_achoo", 0.85) <= t < T("b_chase"):
        eyes = "wide"
        squash = 1 - 0.12 * math.sin(math.pi * tl.prog("b_achoo", t, 0.85, 1.0))
    head_dy = 0.0
    if sneaking:
        head_dy = 0
    wy = FLOOR
    if T("b_wobble") <= t < T("b_poof", 0.1):
        wy = FLOOR + 0
    walk = wx / 12 if moving else 0.0
    if pose == "crouch":
        walk = 0.0
    nose = 0.0
    if T("b_still") <= t < T("b_achoo"):
        nose = math.sin(t * 30) * 2 * tl.prog("b_still", t)
    D.cat(c, wx, wy + nose * 0.2, pal, 1.0, wface, pose, walk=walk if pose != "crouch" else 0.0, t=t,
          mouth=0.0 if statue else tl.mouth("whiskers", t), eyes=eyes, squash=squash, seed=0.0,
          head_dy=head_dy, look=(1, -0.6) if sneaking else (1, 0))
    if t >= T("b_poof", 0.3):
        mouth_croissant(c, wx, wy, 1.0, wface, pose, walk)
    # stack on his head
    if taken and not fallen:
        hx, hy = P.head_pos("stand" if not sneaking else "crouch", walk)
        wob = 0.0
        if T("b_wobble") <= t:
            wob = math.sin(t * 9) * (0.3 + 0.7 * tl.prog("b_wobble", t)) + (tl.prog("b_poof", t, 0, 0.25) * 2.5)
        for k in range(taken):
            ang = wob * 0.25 * (k + 1)
            px = wx + wface * hx + math.sin(ang) * 22 * (k + 1)
            py = wy + hy - 40 - 18 * k * math.cos(ang)
            P.croissant(c, px, py, 0.8, ang)
    if fallen and t < T("b_poof", 0.9):
        u = tl.prog("b_poof", t, 0.25, 0.9)
        for k in range(3):
            P.croissant(c, wx - 40 + k * 50 + 60 * u * (k - 1), FLOOR - 140 + 400 * u * u - 200 * u, 0.8, u * 6 + k)
    # the croissant pops from the tray into the stack
    for f in (0.12, 0.42, 0.75):
        dt = t - T("b_stack", f)
        if -0.25 < dt < 0:
            u = 1 + dt / 0.25
            P.croissant(c, lerp(TRAY[0] + 140, wx - 52, u), lerp(TRAY[2] - 14, FLOOR - 140, u) + arc_y(u, 40), 0.8)

    if not behind:
        draw_gaston()
    poof(c, SACK - 50, FLOOR - 70, tl.prog("b_poof", t, 0.25, 1.0) if t >= T("b_poof", 0.25) else -1, 170, 3)
    poof(c, wx - 60, FLOOR - 100, tl.prog("b_achoo", t, 0.82, 1.0) * 0.7 + tl.prog("b_monster", t) * 0.3
         if t >= T("b_achoo", 0.82) else -1, 150, 5)
    return c


# =================================================================== seine

SW = 4000
WATER = 640         # boat waterline
FAR_Q = 455         # top of the far quay wall


def louvre(c, x0, x1, base, wall=(232, 216, 186), roof=(100, 112, 140)):
    h = 150
    c.rect(x0, base - h, x1, base, wall, w=2.5)
    for x in np.arange(x0 + 20, x1 - 10, 34):
        for y in (base - 120, base - 70):
            c.rect(x, y, x + 14, y + 34, (120, 135, 170), w=1.5, r=6)
    c.poly([(x0 - 4, base - h), (x0 + 20, base - h - 40), (x1 - 20, base - h - 40), (x1 + 4, base - h)], roof, w=2.5)
    # pavilions
    for px in (x0 + 10, (x0 + x1) / 2 - 70, x1 - 150):
        c.rect(px, base - h - 30, px + 140, base, wall, w=2.5)
        c.poly([(px - 6, base - h - 30), (px + 18, base - h - 100), (px + 122, base - h - 100), (px + 146, base - h - 30)],
               roof, w=2.5)
        c.poly([(px + 30, base - h - 30), (px + 70, base - h - 56), (px + 110, base - h - 30)], wall, w=2)
        for x in range(int(px) + 20, int(px) + 130, 32):
            c.rect(x, base - 120, x + 14, base - 86, (120, 135, 170), w=1.5, r=6)


def notre_dame(c, x, base, s=1.0, col=(214, 200, 176)):
    c.push(x, base, s)
    c.rect(-150, -150, 150, 0, col, w=2.5)
    for side in (-1, 1):
        cx = side * 110
        c.rect(cx - 50, -310, cx + 50, 0, col, w=2.5)
        for k in (-1, 1):
            c.rect(cx + k * 20 - 8, -290, cx + k * 20 + 8, -220, (110, 100, 120), w=1.5, r=8)
    c.rect(-60, -230, 60, -170, col, w=2)
    c.circle(0, -200, 40, (180, 120, 160), w=2.5)
    c.circle(0, -200, 26, (120, 90, 160), ol=None)
    for k in (-1, 0, 1):
        c.rect(k * 60 - 22, -110, k * 60 + 22, 0, (110, 100, 120), w=2, r=22)
    c.rect(-160, -160, 160, -146, mix(col, (0, 0, 0), 0.15), w=2)
    # spire behind
    c.poly([(230, -140), (250, -380), (270, -140)], (120, 120, 140), w=2)
    c.rect(170, -150, 330, 0, col, w=2)
    c.pop()


def seine_bg(sunset):
    def make():
        if sunset:
            sky = [(0, (80, 70, 140)), (0.4, (230, 130, 120)), (0.62, (255, 196, 130)), (1, (255, 196, 130))]
            tint = ((240, 140, 110), 0.28)
            water = (110, 90, 140)
        else:
            sky = [(0, (115, 182, 240)), (0.62, (215, 236, 255)), (1, (215, 236, 255))]
            tint = None
            water = (80, 135, 190)
        c = Canvas(D.gradient(SW * SS, H * SS, sky), size=(SW, H))
        rng = np.random.default_rng(21)
        if not sunset:
            for x in range(150, SW, 500):
                D.cloud(c, x + rng.uniform(-60, 60), rng.uniform(70, 170), rng.uniform(0.7, 1.1))
        sky_img = c.img.copy()
        c.tint = tint
        # far bank buildings
        x = -20
        rng2 = np.random.default_rng(5)
        while x < SW:
            w = rng2.uniform(150, 230)
            if 1300 < x < 3050:
                x = 3050
                continue
            if 3330 < x < 3900:
                x = 3900
                continue
            floors = int(rng2.integers(4, 6))
            c.push(x, FAR_Q, 0.62)
            P.building(c, 0, 0, w / 0.62 - 6, floors, (236, 222, 196), (110, 122, 150), rng2)
            c.pop()
            x += w
        louvre(c, 1340, 3020, FAR_Q - 4)
        P.pyramid(c, 2180, FAR_Q, 0.9)
        notre_dame(c, 3560, FAR_Q, 0.75)
        for x in range(60, SW, 260):
            P.tree_round(c, x + rng.uniform(-30, 30), FAR_Q + 4, 0.8, leaf=(100, 160, 100))
        # far quay wall
        stone = (200, 186, 160)
        c.rect(-5, FAR_Q, SW + 5, 492, stone, w=2.5)
        for x in range(0, SW, 60):
            c.line([(x, FAR_Q), (x, 492)], mix(stone, (0, 0, 0), 0.12), 2, cap=False)
        # water
        c.tint = None
        c.rect(0, 492, SW, H, water, ol=None)
        for _ in range(500):
            x, y = rng.uniform(0, SW), rng.uniform(500, H)
            c.line([(x, y), (x + rng.uniform(20, 70) * (y / 600), y)], mix(water, (255, 255, 255), 0.3), 2,
                   cap=False)
        # near quay (foreground, left)
        c.tint = tint
        stone2 = (190, 176, 150)
        c.poly([(-5, 610), (760, 610), (780, H + 5), (-5, H + 5)], stone2, w=3)
        c.rect(-5, 600, 770, 616, mix(stone2, (255, 255, 255), 0.2), w=2.5, r=3)
        for y in range(640, H, 36):
            for x in range(-20 + (y % 72), 760, 80):
                c.rect(x, y, x + 76, y + 32, mix(stone2, (0, 0, 0), 0.05), w=1.5)
        c.circle(700, 650, 10, None, ol=(60, 60, 60), w=3)
        c.tint = None
        from PIL import ImageChops
        mask = ImageChops.difference(c.img, sky_img).convert("L").point(lambda v: 255 if v > 0 else 0)
        layer = c.img.convert("RGBA")
        layer.putalpha(mask)
        return sky_img, layer
    return cached(("seine", sunset), make)


ROOF = -112          # boat roof (boat-local y)


def seine(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["seine"]
    bk = [(s0, 1060), (T("s_jump", 0.62), 1060), (s1, 3400)]
    bxw = smooth(t, bk, 0.5)
    camx = clamp(bxw - 640, 0, SW - W)
    k = ease(tl.prog("s_sleepy", t, 0.1, 1.0) * 0.35 + tl.prog("s_nap", t) * 0.65)
    (dsky, dlay), (esky, elay) = seine_bg(False), seine_bg(True)
    x0 = int(round(camx * SS))
    box = (x0, 0, x0 + W * SS, H * SS)

    def mixk(a, b):
        a, b = a.crop(box), b.crop(box)
        return Image.blend(a, b, k) if 0 < k < 1 else (a if k <= 0 else b)
    c = Canvas(mixk(dsky, esky).convert("RGB"))
    # the sun sinks behind the rooftops
    c.circle(lerp(1050, 760, k), lerp(110, 420, k), lerp(46, 66, k), mix((255, 232, 110), (255, 200, 130), k),
             ol=None)
    lay = mixk(dlay, elay)
    c.img.paste(lay, (0, 0), lay)
    c.push(-camx, 0)
    bob = 3 * math.sin(t * 1.6)
    roof_y = WATER + ROOF + bob
    # wake
    moving = t > T("s_jump", 0.62)
    if moving:
        for j in range(5):
            u = ((t * 0.8 + j / 5) % 1.0)
            c.line([(bxw - 320 - 300 * u, WATER + 6 + 14 * j % 30), (bxw - 260 - 300 * u, WATER + 6 + 14 * j % 30)],
                   (235, 245, 255), 3)
    P.boat(c, bxw, WATER, 1.0, t)
    gaston_on = s0 <= t < T("s_float", 0.5)
    tint_cat = None
    if k > 0:
        c.tint = ((240, 140, 110), 0.2 * k)

    # --- Gaston on the quay, shaking the rolling pin
    if gaston_on:
        gx = smooth(t, [(s0, -200), (T("s_jump", 0.5), 420)])
        P.bulldog(c, gx, 668, 1.15, 1, t, walk=gx / 14 if t < T("s_jump", 0.5) else 0.0,
                  mouth=0.4 + 0.3 * math.sin(t * 12) if t > T("s_jump", 0.6) else 0.0, brow=1.0, arm=1.0,
                  hold="pin")

    # --- who is where: on the quay, in the air, or on the roof
    def jumper(who, i, quay_x, roof_lx, a, b, s=0.85):
        """Returns (x, y, state)."""
        ja, jb = T("s_jump", a), T("s_jump", b)
        if t < ja:
            return quay_x, 664, "quay"
        if t < jb:
            u = (t - ja) / (jb - ja)
            return lerp(quay_x, bxw + roof_lx, u), lerp(664, roof_y, u) + arc_y(u, 150), "air"
        return bxw + roof_lx, roof_y, "roof"

    whisk_in = smooth(t, [(s0, -160), (T("s_vite", 0.9), 300)])
    states = {
        "colette": jumper("colette", 0, 560, 130, 0.0, 0.18),
        "luna": jumper("luna", 1, 460, 10, 0.08, 0.28),
        "pip": jumper("pip", 2, 380, 70, 0.16, 0.36),
        "whiskers": jumper("whiskers", 3, whisk_in, -120, 0.3, 0.55),
    }
    # Colette leaves to the far quay at s_wave
    if t >= T("s_wave"):
        u = tl.prog("s_wave", t, 0.0, 0.6)
        cx0 = bxw + 130
        if u < 1:
            states["colette"] = (lerp(cx0, cx0 + 120, u), lerp(roof_y, FAR_Q + 2, u) + arc_y(u, 120), "far_air")
        else:
            states["colette"] = (smooth(T("s_wave", 0.6), bk, 0.5) + 250, FAR_Q + 2, "far")
    asleep = T("s_sleepy", 0.3) <= t < T("s_wake", 0.5)
    for who in ("colette", "luna", "whiskers", "pip"):
        x, y, st = states[who]
        sc = 0.8
        if st in ("far_air", "far"):
            u = tl.prog("s_wave", t, 0.0, 0.6)
            sc = lerp(0.8, 0.42, u)
        if who == "pip":
            if st == "air":
                D.mouse(c, x, y, 1.15, 1, t, eyes="wide")
            else:
                pe = "happy" if T("s_cheese") <= t < T("s_cheese", 1) + 0.4 else "open"
                if asleep:
                    pe = "closed"
                D.mouse(c, x, y, 1.15, -1 if st == "roof" and T("s_bye") <= t < T("s_wave") else 1, t,
                        mouth=tl.mouth("pip", t), eyes=pe, proud=T("s_cheese") <= t < T("s_cheese", 1))
            continue
        pal = PAL[who]
        if who == "whiskers":
            fl = 0.45 * (1 - ease(tl.prog("s_float", t, 0.0, 0.4)))
            pal = P.floured(D.WHISKERS, fl)
        if st == "quay":
            face = 1
            pose = "stand"
            walk = 0.0
            if who == "whiskers":
                mv = t < T("s_vite", 0.9)
                pose = "walk" if mv else "stand"
                walk = x / 12 if mv else 0
            elif who == "colette":
                face = -1 if t < T("s_vite", 0.6) else 1
            kitty(c, tl, t, who, x, y, 1.0 * sc / 0.8 * 0.95, face, pose, pal, walk=walk,
                  eyes="wide" if who != "colette" else "open")
            if who == "whiskers":
                mouth_croissant(c, x, y, 0.95, 1, pose, walk)
            continue
        if st in ("air", "far_air"):
            D.cat(c, x, y, pal, sc, 1, "leap", t=t, seed=SEED[who])
            if who == "colette":
                P.beret(c, x, y, sc, 1, "leap")
            continue
        # on the roof (or Colette on the far quay)
        face = 1
        pose = "sit"
        eyes = "open"
        look = (1, 0)
        if who == "luna":
            face = 1 if t < T("s_flour") - 0.2 else -1
            if T("s_louvre") <= t < T("s_bye"):
                face, look = -1, (1, -0.6)
            if T("s_flour") <= t < T("s_float"):
                eyes = "happy"
            if T("s_bye") <= t < T("s_wave", 0.8):
                face = 1
            if T("s_sleepy", 0.6) <= t < T("s_wake"):
                pose = "sleep"
            if t >= T("s_wake"):
                pose, eyes = "stand", "wide"
                face = -1 if int((t - T("s_wake")) * 2) % 2 else 1
        elif who == "whiskers":
            if T("s_purpose") <= t < T("s_purpose", 1):
                eyes = "happy"
            if T("s_flour") <= t < T("s_float", 0.4):
                eyes = "closed" if t > T("s_float") else "open"
            if T("s_float") <= t < T("s_float", 0.4):
                pose = "stand"
            if T("s_louvre") <= t < T("s_bye"):
                look = (1, -0.6)
            if asleep:
                pose = "sleep"
            if t >= T("s_wake", 0.5):
                pose, eyes = "sit", "wide"
        elif who == "colette":
            face = -1
            if st == "far":
                face = -1
            if T("s_louvre") <= t < T("s_louvre", 1):
                face = -1
        kitty(c, tl, t, who, x, y, sc, face, pose, pal, eyes=eyes, look=look,
              tail=math.sin(t * 1.8) if pose == "sit" else None)
        if who == "whiskers" and T("s_float") <= t < T("s_float", 0.45):
            poof(c, x, y - 60, tl.prog("s_float", t, 0.05, 0.45), 90, 8)
        if who == "colette" and st == "far" and t < T("s_sleepy"):
            # wave a paw
            c.stroke([(x - 10 * sc, y - 60 * sc), (x - 26 * sc, y - (110 + 10 * math.sin(t * 9)) * sc)],
                     P.COLETTE["body"], 10 * sc)
    c.tint = None
    if asleep and T("s_sleepy", 0.4) <= t:
        D.zzz(c, bxw - 60, roof_y - 70, t)
    c.pop()
    return c


# =================================================================== montmartre

MH = 2 * H
STREET = 1340
STAIR = (470, 1180, 640)      # foot x, top x, top y
DUSK_SKY = [(0, (40, 40, 100)), (0.35, (110, 80, 150)), (0.55, (230, 140, 140)), (0.7, (250, 190, 140)),
            (1, (250, 190, 140))]


def stair_y(x):
    x0, x1, ytop = STAIR
    if x <= x0:
        return STREET
    if x >= x1:
        return ytop
    return STREET - (x - x0) * (STREET - ytop) / (x1 - x0)


def montmartre_bg():
    def make():
        c = Canvas(D.gradient(W * SS, MH * SS, DUSK_SKY), size=(W, MH))
        D.stars(c, 8, 50, W, 300, col=(255, 240, 220))
        # the hill and the basilica
        c.poly([(-10, 700), (300, 610), (900, 600), (W + 10, 640), (W + 10, MH), (-10, MH)], (90, 120, 100), ol=None)
        P.sacre_coeur(c, 640, 610, 1.0, col=(248, 240, 236), shade=(220, 205, 205), tint_win=(110, 90, 130))
        c.rect(300, 600, 990, 626, (220, 210, 205), w=2.5)
        # gardens on the slope
        rng = np.random.default_rng(31)
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(680, 1000)
            if abs(x - stair_x_at(y)) < 120:
                continue
            P.tree_round(c, x, y, rng.uniform(0.6, 0.9), leaf=(70, 120, 90))
        # left: Montmartre houses and a cafe
        x = -20
        for w, floors, wall in ((240, 5, (240, 220, 190)), (220, 6, (232, 206, 196)), (160, 4, (236, 226, 200))):
            top = P.building(c, x, STREET - 40, w, floors, wall, (100, 106, 140), rng,
                             night=0.5, shop=((200, 50, 60), "CAFE") if floors == 5 else None)
            x += w
        # the staircase: retaining wall, steps, handrail, lamps
        x0, x1, ytop = STAIR
        stone, tread = (176, 166, 160), (214, 206, 198)
        n = 25
        rise = (STREET - ytop) / n
        run = (x1 - x0) / n
        pts = [(x0 - 20, STREET + 10)]
        for k in range(n):
            pts += [(x0 + k * run, STREET - k * rise - rise), (x0 + (k + 1) * run, STREET - k * rise - rise)]
        pts += [(W + 10, ytop), (W + 10, MH + 10), (x0 - 20, MH + 10)]
        c.poly(pts, stone, w=3)
        for k in range(n):
            y = STREET - (k + 1) * rise
            c.rect(x0 + k * run, y, x0 + (k + 1) * run + 1, y + 7, tread, ol=None)
        for y in range(int(ytop) + 60, MH, 46):
            for xx in range(int(x0 + (STREET - y) * run / rise) + 20, W, 92):
                c.rect(xx, y, xx + 88, y + 42, mix(stone, (0, 0, 0), 0.03), ol=mix(stone, (0, 0, 0), 0.18), w=1.5)
        # lamps along the stairs
        for k in (4, 12, 20):
            lx = x0 + k * run + 20
            ly = STREET - k * rise
            P.lamp_glow(c, lx, ly, 1.0, (230, 150, 140), 1.0)
            P.street_lamp(c, lx, ly, 1.0, lit=1.0)
        # iron handrail
        c.line([(x0 - 6, STREET - 70), (x1 + 10, ytop - 70)], (40, 40, 50), 4)
        for k in range(0, n + 1, 3):
            xx = x0 + k * run
            c.line([(xx, STREET - k * rise), (xx - 6, STREET - k * rise - 70)], (40, 40, 50), 3)
        # cobbled street
        c.rect(-10, STREET - 6, x0, MH + 10, (150, 140, 150), ol=None)
        for y in range(STREET, MH, 20):
            for xx in range(-20 + (y % 40), int(x0), 30):
                c.ellipse(xx, y + 8, 13, 8, (170, 160, 168), ol=None)
        P.lamp_glow(c, 40, STREET, 1.1, (230, 150, 140), 1.0)
        P.street_lamp(c, 40, STREET, 1.1, lit=1.0)
        return c.img
    return cached("montmartre", make)


def stair_x_at(y):
    x0, x1, ytop = STAIR
    return x0 + (STREET - y) * (x1 - x0) / (STREET - ytop)


def pierre_painting(c, progress):
    sky_bands(c, -48, -174, 48, -92, [(0, (90, 70, 140)), (1, (240, 160, 140))], n=8)
    c.rect(-48, -112, 48, -92, (80, 110, 90), ol=None)
    c.ellipse(0, -124, 16, 16, (250, 245, 240), ol=None)
    c.rect(-16, -124, 16, -104, (250, 245, 240), ol=None)
    c.ellipse(-24, -114, 7, 8, (250, 245, 240), ol=None)
    c.ellipse(24, -114, 7, 8, (250, 245, 240), ol=None)


def montmartre(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["montmartre"]
    # Whiskers' path: arrive, then lead the climb
    wk = [(s0, -150), (T("m_lost", 0.9), 420), (T("m_come", 0.7), 420), (T("m_climb", 0.05), 470),
          (T("m_climb", 0.95), 1220)]
    lk = [(s0, -280), (T("m_lost", 0.95), 220), (T("m_come", 1.0), 220), (T("m_climb", 0.15), 400),
          (s1, 1180)]
    pk = [(s0, -360), (T("m_lost", 1.0), 100), (T("m_come", 1.0), 100), (T("m_climb", 0.2), 320),
          (s1, 1130)]
    wx, lx, px = smooth(t, wk), smooth(t, lk), smooth(t, pk)
    wy, ly, py = stair_y(wx), stair_y(lx), stair_y(px)
    camy = H - H * ease(tl.prog("m_look_up", t, 0.0, 0.6)) + H * ease(tl.prog("m_come", t, 0.0, 0.45))
    if t >= T("m_climb"):
        follow = clamp((wy + ly) / 2 - 500, 0, H)
        camy = lerp(H, follow, ease(tl.prog("m_climb", t, 0.0, 0.25)))
    c = view(montmartre_bg(), 0, camy)
    c.push(0, -camy)
    c.tint = DUSK
    # Pierre and his easel
    P.easel(c, 1060, STREET, 1.1, pierre_painting)
    talking = tl.talking("pierre", t)
    P.pigeon(c, 930, STREET, 1.4, -1 if t < T("m_climb") else 1, t, mouth=tl.mouth("pierre", t),
             brush=1.0 if not talking else 0.4, wing=(0.6 + 0.4 * math.sin(t * 5)) if talking else 0.0)
    # Pip
    actor(c, tl, t, "pip", pk, py + 2, 1.3, face=1,
          eyes="wide" if T("m_look_up") <= t < T("m_tired") else "open")
    # Luna
    sad = T("m_sad") <= t < T("m_come", 0.5)
    lpose = "sit" if (T("m_sad") <= t < T("m_come", 0.9)) else "stand"
    leyes = "closed" if sad and t < T("m_pierre") else "open"
    if T("m_come", 0.6) <= t < T("m_climb"):
        leyes = "happy"
    look = (1, -1) if T("m_look_up") <= t < T("m_tired", 0.5) else (1, 0)
    actor(c, tl, t, "luna", lk, ly + 4, 1.0, face=1, pose=lpose, eyes=leyes, look=look,
          head_dy=8 if sad and t < T("m_pierre") else 0)
    # Whiskers: looks this way and that
    wface = 1
    if T("m_way") <= t < T("m_way", 1):
        wface = 1 if tl.prog("m_way", t) < 0.45 else -1
    if T("m_lostline") <= t < T("m_pierre"):
        wface = -1
    if T("m_come") <= t < T("m_come", 0.7):
        wface = -1
    weyes = "open"
    if T("m_come", 0.4) <= t < T("m_climb"):
        weyes = "happy"
    actor(c, tl, t, "whiskers", wk, wy, 1.0, face=wface, eyes=weyes, look=look)
    c.tint = None
    c.pop()
    return c


# =================================================================== sparkle

def sparkle(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["sparkle"]
    lights = 0.15 + 0.85 * ease(tl.prog("x_sparkle", t, 0.0, 0.18))
    sp = ease(tl.prog("x_sparkle", t, 0.25, 0.4))
    if t >= T("x_narr", 0.6):
        sp = 1 - 0.5 * ease(tl.prog("x_narr", t, 0.6, 1.0))
    c = panorama(t, lights, sp)
    # golden flash on the sky when the lights come on
    flash = math.exp(-max(0, t - T("x_sparkle")) * 3) if t >= T("x_sparkle") else 0
    c.tint = ((30, 36, 90), 0.3 - 0.12 * lights)
    walk_in = T("x_top", 0.9)
    lk = [(s0, -150), (walk_in, 300)]
    wk = [(s0, -40), (walk_in, 470)]
    pk = [(s0, -250), (walk_in, 386)]
    lx, wx, px = smooth(t, lk), smooth(t, wk), smooth(t, pk)
    arrived = t >= walk_in + 0.2
    # Luna
    lface = 1
    leyes = "open"
    if T("x_beautiful") <= t < T("x_beautiful", 1):
        leyes = "happy"
    if T("x_saved", 0.5) <= t < T("x_purpose", 1):
        lface = 1
        leyes = "wide" if t < T("x_purpose") else "happy"
    if t >= T("x_share"):
        leyes = "happy"
    llook = (1, -1) if T("x_bong") <= t < T("x_saved") else (1, 0)
    actor(c, tl, t, "luna", lk, SILL, 0.85, face=lface, pose="sit" if arrived else "stand", look=llook, eyes=leyes,
          tail=math.sin(t * 1.5))
    # Pip
    actor(c, tl, t, "pip", pk, SILL, 1.0, face=1, eyes="happy" if t >= T("x_share") else "open",
          proud=T("x_nine") <= t < T("x_nine", 1))
    # Whiskers
    wpose = "sit" if arrived else "stand"
    if T("x_top", 0.92) <= t < T("x_nine"):
        wpose = "sleep"
    wface = 1
    if T("x_saved") <= t < T("x_purpose", 1):
        wface = -1
    weyes = "open"
    if T("x_purpose") <= t:
        weyes = "happy"
    actor(c, tl, t, "whiskers", wk, SILL, 0.9, face=wface, pose=wpose, eyes=weyes,
          look=(1, -1) if T("x_bong") <= t < T("x_saved") else (1, 0))
    c.tint = None
    # the croissant
    if T("x_saved", 0.3) <= t:
        u = ease(tl.prog("x_saved", t, 0.3, 0.7))
        cx, cy = lerp(470 + 30, 400, u), lerp(SILL - 20, SILL - 70, u)
        sh = tl.prog("x_share", t, 0.2, 0.8)
        if sh <= 0:
            P.croissant(c, cx, cy + 3 * math.sin(t * 3), 1.3, 0.1)
            if u > 0.95:
                for k in range(3):
                    a = t * 2 + k * 2.1
                    c.circle(cx + 40 * math.cos(a), cy - 10 + 18 * math.sin(a), 2.5, (255, 240, 170), ol=None)
        else:
            e = ease(sh)
            # half to Luna, half to Whiskers, a crumb for Pip
            P.croissant(c, lerp(cx - 14, 300 + 0.85 * 34, e), lerp(cy, SILL - 0.85 * 92, e), 0.75, -0.3)
            P.croissant(c, lerp(cx + 14, 470 - 0.9 * 34, e), lerp(cy, SILL - 0.9 * 92, e), 0.75, 0.3)
            c.circle(lerp(cx, 386 + 20, e), lerp(cy, SILL - 38, e), 4, (226, 160, 70), w=1.5)
    if flash > 0.01:
        k = flash * 0.35
        c = Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, (255, 220, 140)), k))
    # move in closer for the heart-to-heart, back out at the end
    z = ease(tl.prog("x_beautiful", t, 0.0, 0.5)) * (1 - ease(tl.prog("x_narr", t, 0.3, 1.0)))
    if z > 0.001:
        x0, y0 = lerp(0, 110, z), lerp(0, 170, z)
        w = lerp(W, 900, z)
        box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + w * H / W))
        c = Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))
    return c


# =================================================================== home

def night_hills():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (14, 18, 48)), (0.6, (40, 44, 96)), (1, (70, 60, 110))]))
        D.stars(c, 23, 160, W, 420)
        D.moon(c, 260, 130, 60, sky=(20, 26, 64))
        c.poly([(0, 470), (250, 430), (600, 480), (900, 440), (W, 470), (W, H), (0, H)], (38, 60, 78), ol=None)
        # home with a lit window, far right
        c.rect(1060, 440, 1180, 520, (60, 60, 90))
        c.poly([(1046, 444), (1120, 390), (1194, 444)], (80, 50, 70))
        c.rect(1100, 466, 1140, 496, (255, 220, 120), w=2)
        c.poly([(0, 540), (W, 520), (W, H), (0, H)], (30, 50, 60), ol=None)
        c.rect(0, 600, W, 612, (60, 60, 80), ol=None)
        for x in range(0, W, 24):
            c.rect(x, 604, x + 12, 616, (50, 40, 50), ol=None)
        c.rect(0, 602, W, 606, (100, 100, 120), ol=None)
        return c.img
    return cached("nhills", make)


def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    if t < T("h_sill"):
        c = Canvas(night_hills().copy())
        u = tl.prog("h_train", t, 0.0, 1.0) * 0.5 + tl.prog("h_narr", t) * 0.5
        x = lerp(-150, 1900, u)
        c.tint = ((30, 36, 90), 0.25)
        P.train(c, x, 602, 0.7, t, x / 14, cars=3, night=1.0)
        c.tint = None
        return c
    c = Canvas(MF.room(True).copy())
    # the postcard pinned by the window, a little tower on the sill
    postcard_art(c, 662, 150, 0.27, t)
    c.circle(702, 147, 4, (220, 60, 60), w=1.5)
    c.tint = ((30, 36, 90), 0.25)
    P.eiffel(c, 1062, 371, 60, w=1.2)
    D.cat(c, 870, 372, D.LUNA, 0.8, -1, "sleep", t=t + 1, seed=1.3, mouth=tl.mouth("luna", t))
    D.cat(c, 965, 372, D.WHISKERS, 0.8, 1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
    D.mouse(c, 918, 336, 1.0, 1, t, eyes="closed")
    c.tint = None
    D.zzz(c, 1010, 300, t)
    x0, y0 = 610, 110
    c = Canvas(c.img.crop((x0 * SS, y0 * SS, (x0 + W // 2) * SS, (y0 + H // 2) * SS)).resize((W * SS, H * SS)))
    k = ease(tl.prog("h_end", t, 0.25, 0.5))
    if k > 0:
        c.text(W / 2, 655, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "postcard": postcard, "train": train, "arrival": arrival, "bakery": bakery,
               "seine": seine, "montmartre": montmartre, "sparkle": sparkle, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["tr_inside", "tr_arrive", "h_sill"]
