"""Scenes of "Whiskers and the Wobbly Bicycle". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
Static backgrounds are drawn once and cached; the canal street is one wide
world that four scenes look at with a panning camera.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.amsterdam import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA, "bram": P.BRAM}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "bram": 3.7, "joost": 5.0, "mies": 7.0}

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


def speed(t, keys, r=0.25):
    return (smooth(t + 0.05, keys, r) - smooth(t - 0.05, keys, r)) / 0.1


def arc_y(u, h):
    return -4 * h * u * (1 - u)


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", r=0.25, **kw):
    x = smooth(t, keys, r)
    v = speed(t, keys, r)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def rider(c, tl, t, who, x, y, s=0.8, face=1, dist=None, pal=None, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t) if who else 0.0)
    P.bike_cat(c, x, y, pal or PAL[who], s, face, x * face if dist is None else dist, t, mouth=mouth,
               seed=SEED.get(who, 0.0), **kw)


def tilted(c, x, y, ang, fn, box=420):
    """Draw fn(cc) (local origin = (0, 0) at the wheels' contact point) rotated by ang degrees about it."""
    if abs(ang) < 0.3:
        c.push(x, y)
        fn(c)
        c.pop()
        return
    size = box * SS
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cc = Canvas(layer)
    cc.tint = c.tint
    ox, oy, sx, sy = c.tf[-1]
    cc.tf = [(box / 2, box * 0.72, sx, sy)]
    fn(cc)
    rot = layer.rotate(ang, resample=Image.BICUBIC, center=(size / 2, size * 0.72))
    px, py = (ox + sx * x - box / 2) * SS, (oy + sy * y - box * 0.72) * SS
    c.img.paste(rot, (int(round(px)), int(round(py))), rot)


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


_shade = {}


def shade_bottom(c, tl, t, strength=0.5, top=560):
    """Soft dark band under the subtitles while somebody speaks."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    if (q, top) not in _shade:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.4 * (q / 20) * 255
        _shade[(q, top)] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((18, 20, 36), (0, top * SS, W * SS, H * SS), _shade[(q, top)])


def finish(c, tl, t, strength=0.5):
    shade_bottom(c, tl, t, strength)
    return c


def thought_bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 9), (0.65, 14)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def splash_fx(c, x, y, dt, s=1.0):
    if not 0 <= dt < 1.2:
        return
    u = dt / 1.2
    rng = np.random.default_rng(3)
    for k in range(14):
        a = math.radians(rng.uniform(200, 340))
        v = rng.uniform(120, 260) * s
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 260 * dt * dt
        if py < y + 10:
            c.circle(px, py, (5 + 4 * rng.random()) * (1 - u * 0.6) * s, (210, 236, 250), w=1.5)
    for k in range(3):
        rr = (40 + 90 * u + 30 * k) * s
        c.ellipse(x, y + 4, rr, rr * 0.18, None, ol=mix((230, 245, 255), P.WATER, u), w=3)


def bang(c, x, y, s, label, col=(255, 230, 90)):
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        r = (60 if k % 2 == 0 else 38) * s
        pts.append((x + math.cos(a) * r * 1.3, y + math.sin(a) * r))
    c.poly(pts, col, w=3)
    c.text(x, y, label, 26 * s, (220, 60, 40), stroke=2, stroke_fill=(255, 255, 255))


def petals(c, t, n=40, seed=3, region=(0, 0, W, H), speed=50.0):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = region
    for k in range(n):
        u = (rng.random() + t * speed / (y1 - y0) * rng.uniform(0.7, 1.3)) % 1.0
        x = x0 + (rng.random() * (x1 - x0) + 30 * math.sin(t * 1.5 + k)) % (x1 - x0)
        y = y0 + u * (y1 - y0)
        col = P.TULIP_COLS[k % len(P.TULIP_COLS)]
        c.ellipse(x, y, 5, 3 + 2 * abs(math.sin(t * 4 + k)), col, ol=None)


# ======================================================== the canal world

CW = 4400
STREET = 588          # where cats stand on the street
QUAY = 600            # front edge of the quay (where you can sit)
HB = (2300, 726, 0.9)  # houseboat x, waterline, scale
DECK = HB[1] - 44 * HB[2]
ROOF = HB[1] - 164 * HB[2]      # the cabin roof terrace
ROOF_X = {"luna": HB[0] - 50, "whiskers": HB[0] + 40, "bram": HB[0] + 132}


def canal_world(sunset):
    def make():
        if sunset:
            sky = [(0, (70, 62, 132)), (0.22, (160, 100, 160)), (0.42, (246, 150, 120)), (0.6, (255, 204, 140)),
                   (1, (255, 204, 140))]
        else:
            sky = [(0, (104, 172, 236)), (0.5, (200, 230, 252)), (1, (200, 230, 252))]
        c = Canvas(D.gradient(CW * SS, H * SS, sky), size=(CW, H))
        rng = np.random.default_rng(12)
        if sunset:
            c.glow(3500, 250, 620, 240, (255, 236, 180), (252, 170, 120), steps=12)
            for x in range(200, CW, 650):
                D.cloud(c, x + rng.uniform(-80, 80), rng.uniform(50, 120), rng.uniform(0.6, 1.0), col=(255, 186, 170))
        else:
            for x in range(150, CW, 520):
                D.cloud(c, x + rng.uniform(-80, 80), rng.uniform(40, 120), rng.uniform(0.6, 1.0))
        c.tint = ((255, 140, 80), 0.16) if sunset else None
        P.house_row(c, -30, CW + 30, 474, np.random.default_rng(7), lit=0.5 if sunset else None)
        street = (178, 122, 98)
        c.rect(-5, 474, CW + 5, 600, street, ol=None)
        c.rect(-5, 472, CW + 5, 482, (196, 186, 172), ol=None)
        for k, y in enumerate(range(494, 598, 13)):
            c.line([(0, y), (CW, y)], mix(street, (0, 0, 0), 0.12), 1.5, cap=False)
            for x in range((k % 2) * 14, CW, 28):
                c.line([(x, y), (x, y + 13)], mix(street, (0, 0, 0), 0.1), 1.2, cap=False)
        sky_c = (255, 190, 140)
        for x in range(260, CW, 560):
            if sunset:
                P.lamp_glow(c, x, 492, 0.95, 1.0, sky_c)
            P.lamp_post(c, x, 492, 0.95, lit=1.0 if sunset else 0.0)
        for x in (520, 1330, 1960, 3080, 3980):
            P.elm(c, x, 490, 1.0, leaf=(100, 150, 80) if sunset else (92, 156, 84))
        bike_cols = [(200, 60, 60), (40, 44, 52), (60, 110, 180), (60, 140, 90), (230, 200, 80)]
        for k, x in enumerate((160, 700, 1180, 1460, 2620, 3280, 3640, 4200)):
            P.bicycle(c, x, 498, 0.55, 1 if k % 2 else -1, 0.4 * k, col=bike_cols[k % len(bike_cols)])
        # quay edge and water
        c.rect(-5, 596, CW + 5, 616, (200, 190, 176), w=2.5)
        for x in range(0, CW, 46):
            c.line([(x, 598), (x, 614)], (170, 160, 150), 1.5, cap=False)
        water = (90, 100, 130) if sunset else P.WATER
        c.rect(-5, 616, CW + 5, H + 5, water, ol=None)
        for _ in range(900):
            x, y = rng.uniform(0, CW), rng.uniform(624, H)
            col = mix(water, (255, 200, 140) if sunset else (255, 255, 255), 0.3)
            c.line([(x, y), (x + rng.uniform(16, 50) * (y / 640), y)], col, 2, cap=False)
        for x in range(120, CW, 380):
            P.bollard(c, x, 606, 1.0)
        c.tint = None
        return c.img
    return cached(("canal", sunset), make)


def water_glints(c, t, camx, sunset=False):
    rng = np.random.default_rng(5)
    for k in range(18):
        x = (rng.uniform(0, W) - camx * 0.0 + t * 18 * rng.uniform(0.5, 1.5)) % W
        y = rng.uniform(630, 712)
        a = 0.5 + 0.5 * math.sin(t * 2 + k)
        col = (255, 220, 170) if sunset else (230, 245, 255)
        c.line([(x, y), (x + 14 + 10 * a, y)], col, 2, cap=False)


TRAFFIC_PALS = [P.SNOWY, P.CREAM, P.SOOT, P.GINGER2, P.BRAM]
TRAFFIC_COLS = [(200, 60, 60), (60, 110, 180), (40, 44, 52), (60, 140, 90), (230, 200, 80)]


def traffic(c, t, camx, lane=548, n=4, seed=1, s=0.62, flowers=0, band=None):
    """Background cyclists going both ways (world coords, inside c.push(-camx))."""
    rng = np.random.default_rng(seed)
    span = W + 600
    for k in range(n):
        v = rng.uniform(110, 170) * (1 if k % 2 == 0 else -1)
        ph = rng.uniform(0, span)
        x = camx - 300 + (ph + v * t) % span
        y = lane + (k % 2) * 16
        pal = TRAFFIC_PALS[(k + seed) % len(TRAFFIC_PALS)]
        P.bike_cat(c, x, y, pal, s, 1 if v > 0 else -1, abs(x) if v > 0 else -x, t, seed=k * 0.7,
                   bike_col=TRAFFIC_COLS[(k + seed) % len(TRAFFIC_COLS)], flowers=flowers, eyes="happy")


def canal_view(sunset, camx):
    return view(canal_world(sunset), clamp(camx, 0, CW - W))


# ================================================================== title

def title(tl, t):
    camx = 1800 + 40 * tl.prog("t_hold", t)
    c = canal_view(True, camx)
    c.push(-camx, 0)
    traffic(c, t, camx, lane=552, n=2, seed=4)
    P.houseboat(c, *HB[:2], HB[2], t, bike=False, bob=False)
    kat(c, tl, t, "whiskers", ROOF_X["luna"] + 10, ROOF, 0.74, 1, "sit", eyes="happy", mouth=0, tail=math.sin(t * 1.5))
    kat(c, tl, t, "luna", ROOF_X["bram"] - 10, ROOF, 0.72, -1, "sit", look=(-1, -0.5), mouth=0)
    c.pop()
    water_glints(c, t, camx, True)
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(W / 2, 92 - 30 * (1 - k), "Whiskers and the", 44, mix((90, 70, 130), (255, 248, 236), k),
           stroke=3 * k, stroke_fill=(70, 40, 80))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 172, "WOBBLY BICYCLE", 28 + 52 * k2, mix((90, 70, 130), (255, 150, 50), k2), stroke=5 * k2,
           stroke_fill=(70, 30, 50))
    return finish(c, tl, t)


# ================================================================= letter

WIN = (320, 70, 960, 470)       # window opening
MULL = 640
TRANSOM = 250
SILL = 476


def outside(night):
    def make():
        if night:
            sky = [(0, (16, 22, 60)), (0.6, (46, 52, 108)), (1, (70, 66, 120))]
        else:
            sky = [(0, (120, 186, 245)), (0.6, (206, 236, 255)), (1, (220, 240, 255))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        if night:
            D.stars(c, 31, 70, W, 330)
            D.moon(c, 420, 150, 34, sky=(30, 36, 84))
        else:
            for x, y, s in ((420, 130, 0.8), (780, 100, 0.6), (900, 190, 0.5)):
                D.cloud(c, x, y, s)
        c.tint = ((30, 36, 90), 0.45) if night else None
        c.poly([(300, 380), (500, 340), (720, 372), (1000, 336), (1000, 520), (300, 520)], (130, 190, 120), ol=None)
        # neighbours' roofs
        for x, w, h, col in ((560, 140, 70, (190, 90, 70)), (720, 110, 90, (170, 80, 70)), (840, 140, 60, (200, 110, 80))):
            c.rect(x, 400 - h, x + w, 420, (236, 220, 200), w=2)
            c.poly([(x - 10, 400 - h), (x + w / 2, 400 - h - 46), (x + w + 10, 400 - h)], col, w=2)
            c.rect(x + w / 2 - 12, 400 - h + 16, x + w / 2 + 12, 400 - h + 40,
                   (255, 220, 130) if night else (120, 160, 200), w=1.5)
        c.rect(300, 420, 1000, 520, (110, 170, 96), ol=None)
        for x in range(300, 1000, 22):
            c.rect(x, 404, x + 12, 446, (240, 236, 226), w=1.5)
        c.rect(300, 418, 1000, 424, (240, 236, 226), w=1.5)
        D.tree(c, 420, 450, 1.0, leaf=(250, 196, 210) if not night else (200, 160, 190))
        for dx, dy in ((-40, -150), (20, -200), (50, -140), (-20, -175), (0, -130)):
            c.circle(420 + dx, 450 + dy, 8, (255, 236, 244), ol=None)
        for k, x in enumerate(range(330, 1000, 34)):
            P.tulip(c, x, 470, P.TULIP_COLS[k % len(P.TULIP_COLS)], 0.9)
        c.tint = None
        return c.img
    return cached(("outside", night), make)


def room_front(night, open_):
    def make():
        wall = (232, 236, 212) if not night else (110, 110, 140)
        c = Canvas(bg=wall)
        if night:
            c.tint = ((40, 40, 100), 0.35)
            wall_ = (232, 236, 212)
        else:
            wall_ = wall
        for x in range(0, W, 48):
            c.rect(x + 20, 0, x + 26, H, mix(wall_, (255, 255, 255), 0.35), ol=None)
        for x in range(24, W, 48):
            for y in range(40, 640, 64):
                c.circle(x + (y // 64 % 2) * 24, y, 3, (200, 170, 190), ol=None)
        # skirting, wainscot, floor
        c.rect(0, 560, W, H, (196, 150, 110), ol=None)
        c.rect(0, 556, W, 566, (240, 236, 226), ol=None)
        for y in range(586, H, 30):
            c.line([(0, y), (W, y)], (176, 130, 92), 2, cap=False)
        # framed pictures of earlier trips: the moon pond, Rome, Paris, the White Mountain
        frames = [(70, 120, "moon"), (70, 300, "rome"), (1120, 120, "paris"), (1120, 300, "mont")]
        for fx, fy, kind in frames:
            c.rect(fx, fy, fx + 110, fy + 130, (150, 100, 60), w=3)
            c.rect(fx + 10, fy + 10, fx + 100, fy + 120,
                   (40, 44, 96) if kind == "moon" else (170, 210, 240), w=1.5)
            cx, by = fx + 55, fy + 110
            if kind == "moon":
                c.circle(cx + 20, fy + 40, 12, (250, 246, 215), ol=None)
                c.ellipse(cx, by - 4, 40, 8, (60, 80, 140), ol=None)
                c.ellipse(cx, by - 4, 14, 3, (250, 246, 215), ol=None)
            elif kind == "rome":
                c.rect(fx + 18, fy + 60, fx + 92, by, (220, 180, 130), w=1.5)
                for k in range(4):
                    c.rect(fx + 24 + k * 17, fy + 70, fx + 34 + k * 17, fy + 86, (150, 110, 80), ol=None, r=4)
                    c.rect(fx + 24 + k * 17, fy + 92, fx + 34 + k * 17, by - 4, (150, 110, 80), ol=None, r=4)
            elif kind == "paris":
                c.poly([(cx - 26, by), (cx, fy + 20), (cx + 26, by)], (150, 104, 74), w=1.5)
                c.rect(cx - 16, by - 34, cx + 16, by - 30, (150, 104, 74), ol=None)
            else:
                c.poly([(fx + 12, by), (cx, fy + 30), (fx + 98, by)], (150, 150, 170), w=1.5)
                c.poly([(cx - 16, fy + 50), (cx, fy + 30), (cx + 16, fy + 50), (cx, fy + 44)], (255, 255, 255), ol=None)
        # window frame
        fr = (250, 248, 240)
        x0, y0, x1, y1 = WIN
        c.rect(x0 - 22, y0 - 22, x1 + 22, y1 + 6, fr, w=3)
        c.rect(x0, y0, x1, y1, (0, 0, 0), ol=None)                 # opening (made transparent below)
        c.rect(MULL - 7, y0, MULL + 7, y1, fr, w=2)
        c.rect(x0, TRANSOM - 6, MULL, TRANSOM + 6, fr, w=2)
        if not open_:
            c.rect(MULL, TRANSOM - 6, x1, TRANSOM + 6, fr, w=2)
        c.rect(x0, y0, x1, y1, None, w=3)
        # sill
        c.rect(x0 - 50, SILL - 8, x1 + 50, SILL + 8, fr, w=3, r=3)
        c.rect(x0 - 40, SILL + 8, x1 + 40, SILL + 26, mix(fr, (0, 0, 0), 0.12), w=2.5)
        # curtains with tie-backs
        cur = (90, 140, 200)
        for side in (-1, 1):
            cx_ = x0 - 60 if side < 0 else x1 + 60
            pts = [(cx_ - 70 * side * -1 * 0 - 60, 20), (cx_ + 60, 20), (cx_ + 40 * side, 300), (cx_ + 66, 600),
                   (cx_ - 66, 600), (cx_ - 40 * side * -1 * 0 - 30 * side, 300)]
            c.poly([(cx_ - 64, 18), (cx_ + 64, 18), (cx_ + 22 * side, 300), (cx_ + 60, 590), (cx_ - 60, 590),
                    (cx_ + 22 * side - 30, 300)], cur, w=2.5)
            for k in range(-2, 3):
                c.line([(cx_ + k * 22, 26), (cx_ + 10 * side + k * 6, 300), (cx_ + k * 20, 584)],
                       mix(cur, (0, 0, 0), 0.18), 2, cap=False)
            c.rect(cx_ + 10 * side - 36, 292, cx_ + 10 * side + 24, 306, (240, 200, 90), w=2, r=5)
        c.rect(150, 10, W - 150, 22, (150, 100, 60), w=2, r=4)
        c.tint = None
        img = c.img.convert("RGBA")
        mask = Image.new("L", img.size, 255)
        md = ImageDraw.Draw(mask)
        panes = [(x0 + 3, y0 + 3, MULL - 7, TRANSOM - 6), (x0 + 3, TRANSOM + 6, MULL - 7, y1 - 2)]
        if open_:
            panes.append((MULL + 7, y0 + 3, x1 - 3, y1 - 2))
        else:
            panes += [(MULL + 7, y0 + 3, x1 - 3, TRANSOM - 6), (MULL + 7, TRANSOM + 6, x1 - 3, y1 - 2)]
        for a, b, cc, d in panes:
            md.rectangle([a * SS, b * SS, cc * SS, d * SS], fill=0)
        img.putalpha(mask)
        # a faint sheen on the closed glass
        return img
    return cached(("front", night, open_), make)


def glass_sheen(c, open_):
    for (a, b) in ((340, 90), (660, 90)):
        if open_ and a > MULL:
            continue
        c.line([(a + 20, b + 140), (a + 90, b + 20)], (235, 245, 255), 3, cap=False)
        c.line([(a + 40, b + 150), (a + 100, b + 46)], (235, 245, 255), 2, cap=False)


def letter_card():
    def make():
        img = P.letter_img()
        w, h = img.size
        card = Image.new("RGB", (w + 20 * SS, h + 20 * SS), (240, 226, 196))
        card.paste(img, (10 * SS, 10 * SS))
        return card
    return cached("letter_card", make)


def paste_card(c, card, cx, cy, sc):
    cw, ch = card.size
    im = card.resize((max(2, int(cw * sc)), max(2, int(ch * sc))))
    hw, hh = cw / SS * sc / 2, ch / SS * sc / 2
    c.rect(cx - hw + 8, cy - hh + 8, cx + hw + 8, cy + hh + 8, (120, 110, 100), ol=None)
    c.img.paste(im, (int((cx - hw) * SS), int((cy - hh) * SS)))
    c.rect(cx - hw, cy - hh, cx + hw, cy + hh, None, w=2.5)


JOOST_STAND = (920, 600, 1.45)


def basket_load(c, tl, t, bx, by, s, cats=("luna", "whiskers"), pip=None, blanket=False, eyes=None):
    """The stork's basket with its passengers. (bx, by) = rim centre."""
    P.stork_basket(c, bx, by, s, "back")
    pos = {"luna": -40, "whiskers": 38}
    for who in cats:
        e = eyes.get(who, "open") if eyes else "open"
        kat(c, tl, t, who, bx + pos[who] * s - 14 * s, by + 34 * s, 0.62 * s / 0.8, 1, "sit", eyes=e,
            look=(1, 0.3) if who == "luna" else (1, 0.6))
    if pip:
        pip(c)
    P.stork_basket(c, bx, by, s, "front", blanket=blanket)


def knock_dx(tl, t):
    dx = 0.0
    for ev, f in (("l_narr", 0.72), ("l_knock", 0.1), ("l_knock", 0.55)):
        for k in range(3):
            dt = t - (tl.t(ev, f) + k * 0.2)
            if 0 <= dt < 0.18:
                dx = max(dx, 14 * math.sin(math.pi * dt / 0.18))
    return dx


def zoom(c, x0=170, y0=40, w=940):
    """Crop a part of the frame and blow it up to full size (closer framing for the window scenes)."""
    h = w * H / W
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def letter(tl, t):
    T = tl.t
    open_ = t >= T("l_window", 0.5)
    c = Canvas(outside(False).copy())
    jx, jy, js = JOOST_STAND
    # --- Joost outside the window
    basket_on = T("l_hop", 0.3) <= t
    if t < T("l_narr", 0.55):
        u = tl.prog("l_narr", t, 0.0, 0.55)
        if u > 0:
            fx, fy = lerp(1320, jx, ease(u)), lerp(40, jy - 148 * js, ease(u))
            P.stork(c, fx, fy, 1.25, -1, t, "fly", flap=t * 6, seed=5)
    elif t < T("l_go", 0.45):
        head = knock_dx(tl, t) + (18 if open_ else 0)
        hold = "letter" if T("l_joost") <= t < T("l_joost", 1) + 0.3 else None
        tip = P.stork(c, jx, jy, js, -1, t, "stand", mouth=tl.mouth("joost", t), head_dx=head, hold=hold,
                      eyes="happy" if T("l_suitcase") <= t < T("l_hop") else "open")
        if basket_on:
            k = ease(tl.prog("l_hop", t, 0.3, 0.7))
            bx, by = tip[0] + 16, tip[1] + 96 * k + 10
            c.line([tip, (bx - 60, by)], (120, 90, 60), 2.5, cap=False)
            c.line([tip, (bx + 60, by)], (120, 90, 60), 2.5, cap=False)
            inside = [w for w, a in (("luna", 0.1), ("whiskers", 0.25)) if t >= T("l_go", a + 0.2)]
            basket_load(c, tl, t, bx, by, 0.72, inside, eyes={"whiskers": "happy", "luna": "happy"})
    else:
        u = tl.prog("l_go", t, 0.45, 1.0)
        fx, fy = lerp(jx - 10, 200, u ** 1.3), lerp(jy - 148 * js, -260, u ** 0.9)
        tip = P.stork(c, fx, fy, 1.3, -1, t, "fly", flap=t * 7)
        bx, by = tip[0] + 10, tip[1] + 92
        c.line([tip, (bx - 60, by)], (120, 90, 60), 2.5, cap=False)
        c.line([tip, (bx + 60, by)], (120, 90, 60), 2.5, cap=False)
        basket_load(c, tl, t, bx, by, 0.72, eyes={"whiskers": "happy", "luna": "happy"})
    # --- the room in front
    front = room_front(False, open_)
    c.img.paste(front, (0, 0), front)
    if not open_:
        glass_sheen(c, False)
    # --- cats on the sill
    wx, lx = 470, 800
    leap = {"luna": (0.1, lx), "whiskers": (0.25, wx)}
    if t < T("l_sofas"):
        talk = T("l_closed") - 0.2 <= t < T("l_closed", 1) + 0.2
        kat(c, tl, t, "whiskers", wx, SILL, 1.0, 1, "sit" if talk else "sleep", eyes="closed",
            head_dy=8 if talk else 0)
        if not talk:
            D.zzz(c, 530, 400, t)
    elif t < T("l_go", 0.25):
        excited = t >= T("l_suitcase")
        dreamy = T("l_cheese", 0.5) <= t < T("l_suitcase")
        hop = abs(math.sin((t - T("l_suitcase")) * 8)) * 18 if T("l_suitcase", 0.5) < t < T("l_hop", 0.2) else 0
        kat(c, tl, t, "whiskers", wx, SILL - hop, 1.0, 1, "stand" if excited else "sit",
            eyes="happy" if dreamy or (excited and tl.mouth("whiskers", t) < 0.1) else "open",
            look=(1, -0.6) if t < T("l_cheese") else (0.3, -1))
    if t < T("l_go", 0.45):
        for who, (a, x0) in leap.items():
            ta, tb = T("l_go", a), T("l_go", a + 0.2)
            if who == "whiskers" and t < ta:
                continue
            if t < ta:
                look = (1, -1) if t < T("l_joost") else (0.6, -0.8)
                kat(c, tl, t, "luna", lx, SILL, 1.0, 1, "sit", look=look,
                    eyes="happy" if T("l_parade") <= t < T("l_parade", 1) else "open")
            elif t < tb:
                u = (t - ta) / (tb - ta)
                tx = c_target = 780 + (-40 if who == "luna" else 38) * 0.72
                kat(c, tl, t, who, lerp(x0, c_target, u), lerp(SILL, 380, u) + arc_y(u, 120), lerp(1.0, 0.6, u),
                    1, "leap", eyes="happy")
    # Joost's letter, read aloud
    k = min(ease(tl.prog("l_bram", t, 0.0, 0.15)), 1 - ease(tl.prog("l_sofas", t, 0.0, 0.2)))
    if k > 0.01:
        paste_card(c, letter_card(), 470, 240, 0.8 * k)
    # Whiskers dreams of cheese and stroopwafels
    k = min(ease(tl.prog("l_cheese", t, 0.3, 0.6)), 1 - ease(tl.prog("l_suitcase", t, 0.4, 0.8)))
    if k > 0.02:
        thought_bubble(c, 520, 220, 150, 92, k, tail=(500, 360))
        if k > 0.6:
            P.cheese_side(c, 470, 262, 46 * k, 34 * k)
            P.cheese_side(c, 470, 228, 40 * k, 30 * k, label=False)
            P.stroopwafel(c, 590, 220, 36 * k)
    return finish(zoom(c), tl, t)


# ================================================================= flight

FW_ = 7800
HORIZON = 430


def flight_strip():
    def make():
        h = H - HORIZON
        c = Canvas(Image.new("RGB", (FW_ * SS, h * SS), (110, 180, 120)), size=(FW_, h))
        rng = np.random.default_rng(8)
        # sea
        sea = (60, 130, 190)
        c.rect(-5, 0, 2500, h + 5, sea, ol=None)
        c.rect(-5, 0, 2500, 14, (120, 170, 210), ol=None)
        for _ in range(500):
            x, y = rng.uniform(0, 2500), rng.uniform(10, h)
            c.arc(x, y, 9 + y / 30, 4, 200, 340, (200, 230, 250), 2)
        # a ferry far below
        c.push(1300, 160, 0.9)
        c.poly([(-90, 0), (90, 0), (110, -20), (-110, -20)], (240, 240, 245), w=2)
        c.rect(-60, -40, 50, -20, (250, 250, 250), w=2)
        c.rect(-20, -58, 0, -40, (220, 60, 60), w=2)
        c.line([(-110, 6), (-260, 14)], (230, 245, 255), 3)
        c.pop()
        # beach and dunes
        c.poly([(2480, h + 5), (2480, 0), (2560, 0), (2640, h + 5)], (240, 220, 160), ol=None)
        c.poly([(2560, 0), (2900, 0), (2900, h + 5), (2640, h + 5)], (190, 200, 120), ol=None)
        c.push(2600, 60, 0.5)                   # lighthouse
        c.rect(-14, -120, 14, 0, (250, 250, 250), w=2)
        for k in range(3):
            c.rect(-14, -110 + k * 36, 14, -92 + k * 36, (220, 60, 60), ol=None)
        c.rect(-18, -136, 18, -120, (60, 60, 70), w=2)
        c.pop()
        # tulip fields: slanted coloured stripes with little canals
        x = 2900
        k = 0
        while x < 6300:
            w = rng.uniform(120, 200)
            for j in range(7):
                y0, y1 = j * h / 7, (j + 1) * h / 7
                sl = 0.55
                col = P.TULIP_COLS[(k + j) % len(P.TULIP_COLS)] if (k + j) % 4 else (120, 180, 90)
                c.poly([(x + y0 * sl, y0), (x + w + y0 * sl, y0), (x + w + y1 * sl, y1), (x + y1 * sl, y1)], col,
                       ol=None)
                for r in range(1, 4):
                    yy = lerp(y0, y1, r / 4)
                    c.line([(x + yy * sl, yy), (x + w + yy * sl, yy)], mix(col, (0, 0, 0), 0.12), 1.5, cap=False)
            c.line([(x, 0), (x + h * 0.55, h)], (90, 150, 200), 6, cap=False)
            x += w
            k += 1
        for j in range(8):
            c.line([(2900, j * h / 7), (6300, j * h / 7)], (100, 160, 90), 3, cap=False)
        # windmills and farms on the fields
        for x, y, s in ((3150, 40, 0.42), (3600, 120, 0.6), (4150, 30, 0.4), (4500, 170, 0.75), (5100, 60, 0.5),
                        (5600, 140, 0.65)):
            pass
        # the city on the horizon
        c.rect(6300, 0, FW_ + 5, h + 5, (120, 160, 120), ol=None)
        c.push(0, 0)
        crng = np.random.default_rng(4)
        x = 6400
        while x < FW_:
            w = crng.uniform(40, 60)
            P.canal_house(c, x, 140, w, crng.uniform(90, 130), P.HOUSE_WALLS[int(crng.integers(12))], crng,
                          P.GABLES[int(crng.integers(8))])
            x += w
        c.pop()
        c.rect(6300, 140, FW_ + 5, 170, (80, 130, 160), ol=None)
        x = 6400
        while x < FW_:
            w = crng.uniform(40, 60)
            P.canal_house(c, x, 300, w, crng.uniform(100, 140), P.HOUSE_WALLS[int(crng.integers(12))], crng,
                          P.GABLES[int(crng.integers(8))])
            x += w
        # church tower (Westerkerk-like)
        c.push(7000, 140, 0.8)
        c.rect(-26, -200, 26, 0, (150, 80, 60), w=2)
        c.rect(-20, -260, 20, -200, (230, 220, 200), w=2)
        c.rect(-14, -310, 14, -260, (60, 90, 140), w=2)
        c.poly([(-10, -310), (0, -350), (10, -310)], (60, 90, 140), w=2)
        c.circle(0, -230, 10, (250, 230, 120), w=1.5)
        c.pop()
        c.rect(6300, 300, FW_ + 5, h + 5, (80, 130, 160), ol=None)
        return c.img
    return cached("flight_strip", make)


MILLS = [(3200, 70, 0.42), (3650, 150, 0.58), (4150, 50, 0.4), (4550, 190, 0.72), (5150, 90, 0.5),
         (5650, 170, 0.66), (6050, 60, 0.45)]


def flight(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["flight"]
    keys = [(s0, 0), (T("f_rainbow"), 2200), (T("f_tulips"), 2900), (T("f_mills", 1), 5000), (s1, FW_ - W)]
    camx = smooth(t, keys, 1.0)
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (96, 160, 230)), (0.6, (196, 226, 250)), (1, (220, 236, 250))]))
    # far clouds (slow)
    rng = np.random.default_rng(6)
    for k in range(6):
        x = (rng.uniform(0, W + 400) - camx * 0.15) % (W + 400) - 200
        D.cloud(c, x, rng.uniform(60, 300), rng.uniform(0.6, 1.0), col=(250, 252, 255))
    strip = flight_strip()
    x0 = int(round(clamp(camx, 0, FW_ - W) * SS))
    c.img.paste(strip.crop((x0, 0, x0 + W * SS, (H - HORIZON) * SS)), (0, HORIZON * SS))
    # haze at the horizon
    c.rect(0, HORIZON - 6, W, HORIZON + 4, (200, 226, 240), ol=None)
    # windmills standing on the fields (turning)
    c.push(-camx, HORIZON)
    for mx, my, ms in MILLS:
        if -200 < mx - camx < W + 200:
            P.windmill(c, mx, my, ms, t * 1.4 + mx)
    c.pop()
    # the stork
    bob = 14 * math.sin(t * 2.2)
    jx, jy = 470 + 20 * math.sin(t * 0.7), 230 + bob
    tip = P.stork(c, jx, jy, 1.25, 1, t, "fly", flap=t * 5.5, mouth=tl.mouth("joost", t))
    bx, by = tip[0] + 6, tip[1] + 100
    c.line([tip, (bx - 64, by)], (120, 90, 60), 2.5, cap=False)
    c.line([tip, (bx + 64, by)], (120, 90, 60), 2.5, cap=False)
    pip_up = t >= T("f_pip") - 0.15
    wrig = T("f_wriggle") <= t < T("f_pip") - 0.15

    def pip(cc):
        if pip_up:
            u = ease(tl.prog("f_pip", t, 0.0, 0.15) if t < T("f_pip", 0.15) else 1.0)
            px = bx + (0 if t < T("f_land") else 2)
            py = by + 30 * (1 - u) + (0 if t < T("f_land", 0.3) else -4)
            D.mouse(cc, px, py, 0.95, 1, t, mouth=tl.mouth("pip", t), proud=T("f_pip") <= t < T("f_pip", 1),
                    eyes="happy" if t >= T("f_rainbow") else "open")
    eyes = {"whiskers": "closed" if T("f_fragile") <= t < T("f_wriggle") else
            ("wide" if wrig or T("f_pip") <= t < T("f_pip", 0.5) else
             ("happy" if t >= T("f_mills") else "open")), "luna": "happy" if t >= T("f_rainbow") else "open"}
    basket_load(c, tl, t, bx, by + (3 * math.sin(t * 30) if wrig else 0), 0.9, pip=pip,
                blanket=not pip_up or t < T("f_pip", 0.2), eyes=eyes)
    if wrig:
        for k in range(3):
            c.circle(bx - 20 + k * 20 + 4 * math.sin(t * 20 + k), by + 2 - 4 * abs(math.sin(t * 14 + k)), 7,
                     (220, 80, 80), w=1.5)
    # near clouds in front (fast)
    for k in range(4):
        x = (rng.uniform(0, W + 800) - camx * 1.6) % (W + 800) - 400
        D.cloud(c, x, rng.uniform(380, 640), rng.uniform(1.1, 1.6), col=(255, 255, 255))
    # seagulls over the sea
    if camx < 2600:
        for k in range(3):
            gx = (300 + k * 350 - camx * 0.6 + t * 30) % (W + 200) - 100
            gy = 140 + 40 * k + 8 * math.sin(t * 3 + k)
            fl = 8 * math.sin(t * 8 + k)
            c.line([(gx - 18, gy - fl), (gx, gy), (gx + 18, gy - fl)], (60, 60, 70), 3)
    return finish(c, tl, t)


# ================================================================== canal

def canal(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["canal"]
    hbx, hby, hbs = HB
    cam_keys = [(s0, 0), (T("c_walk", 1), 360), (T("c_dodge", 1), 380), (T("c_bram", 1), 1500),
                (T("c_hop"), 1760), (T("c_hop", 1), 1740)]
    camx = smooth(t, cam_keys, 0.8)
    c = canal_view(False, camx)
    c.push(-camx, 0)
    traffic(c, t, camx, lane=540, n=4, seed=2)
    # Whiskers and Luna along the street
    wk = [(s0, 60), (T("c_walk", 1), 820), (T("c_bram", 0.6), 820), (T("c_hop"), 2190)]
    lk = [(s0 - 0.5, -60), (T("c_walk", 1), 700), (T("c_bram", 0.6), 700), (T("c_hop"), 2110)]
    hop_a, hop_b = T("c_hop", 0.25), T("c_hop", 0.75)
    deck_w, deck_l = ROOF_X["whiskers"], ROOF_X["luna"]
    # the two ringing bikes
    ring_t = T("c_ring", 0.42)
    b1 = 820 + (t - ring_t) * -420
    b2 = 820 + (t - T("c_dodge", 0.45)) * 460
    jump = 0.0
    if T("c_ring", 0.25) <= t < T("c_ring", 0.6):
        jump = arc_y(tl.prog("c_ring", t, 0.25, 0.6), 130)
    side = 0.0
    if t >= T("c_dodge", 0.25):
        side = -28 * ease(tl.prog("c_dodge", t, 0.25, 0.45))
    if t >= T("c_bram", 0.6):
        side = -28 * (1 - ease(tl.prog("c_bram", t, 0.6, 1.0)))
    # the houseboat and Bram
    if t < hop_b:
        P.houseboat(c, hbx, hby, hbs, t, bike=False, bob=False)

    def draw_bram():
        bram_face = -1
        wave = T("c_bram") <= t < T("c_bram", 1)
        kat(c, tl, t, "bram", ROOF_X["bram"], ROOF, 0.74, bram_face, "sit",
            eyes="happy" if T("c_orange", 0.5) <= t < T("c_finally", 1) and tl.mouth("bram", t) < 0.1 else "open",
            head_dy=-6 * abs(math.sin(t * 6)) if wave else 0)
    # street actors (behind the boat cabin when they walk past it)
    if t < hop_a:
        lx = actor(c, tl, t, "luna", lk, STREET + side * 0.4, 0.8, eyes="happy" if t < T("c_ring") else "open")
        if jump < 0:
            kat(c, tl, t, "whiskers", 820, STREET + jump, 0.8, 1, "leap", eyes="wide")
        else:
            crouch = T("c_dodge", 0.3) <= t < T("c_bram", 0.6)
            if crouch:
                kat(c, tl, t, "whiskers", 820, STREET + side, 0.8, 1, "crouch", eyes="wide", look=(1, 0))
            else:
                actor(c, tl, t, "whiskers", wk, STREET + side, 0.8,
                      eyes="wide" if T("c_ring") <= t < T("c_dodge", 1) else "open")
    if T("c_ring") - 1.5 < t < T("c_ring") + 3:
        P.bike_cat(c, b1, STREET + 6, P.SNOWY, 0.8, -1, -b1, t, eyes="open", bike_col=(60, 110, 180),
                   mouth=0.4 if abs(b1 - 820) < 200 else 0)
        if abs(b1 - 820) < 260:
            c.text(b1 + 30, STREET - 170, "RING!", 22, (255, 230, 80), stroke=2)
    if T("c_dodge") - 1.0 < t < T("c_dodge", 1) + 1:
        P.bike_cat(c, b2, STREET + 10, P.CREAM, 0.8, 1, b2, t, bike_col=(200, 60, 60))
        if abs(b2 - 820) < 260:
            c.text(b2 - 20, STREET - 170, "RING RING!", 22, (255, 230, 80), stroke=2)
    if t >= hop_b:
        P.houseboat(c, hbx, hby, hbs, t, bike=False, bob=False)
    if hop_a <= t < hop_b:
        P.houseboat(c, hbx, hby, hbs, t, bike=False, bob=False)
        u = (t - hop_a) / (hop_b - hop_a)
        kat(c, tl, t, "luna", lerp(2110, deck_l, u), lerp(STREET, ROOF, u) + arc_y(u, 70), 0.76, 1, "leap")
        u2 = clamp(u * 1.2 - 0.2)
        kat(c, tl, t, "whiskers", lerp(2190, deck_w, u2), lerp(STREET, ROOF, u2) + arc_y(u2, 70), 0.76, 1,
            "leap" if u2 > 0 else "stand")
    draw_bram()
    if t >= hop_b:
        kat(c, tl, t, "luna", deck_l, ROOF, 0.72, 1, "sit",
            look=(1, 0) if t >= T("c_orange") else (0, 0))
        proud = t >= T("c_finally")
        kat(c, tl, t, "whiskers", deck_w, ROOF, 0.74, 1, "sit", eyes="happy" if proud and tl.mouth("whiskers", t) < 0.1
            else "open", head_dy=-6 if proud else 0)
    c.pop()
    water_glints(c, t, camx)
    return finish(zoom(c, 128, 144, 1024), tl, t)


# ================================================================= market

MW = 2700
MG = 650          # ground line for characters
STALL = (250, 650)
MIES_X = 450
BIG = (800, 64)   # giant cheese x, radius
RACK = (2340, 2500)


def market_bg():
    def make():
        c = Canvas(D.gradient(MW * SS, H * SS, [(0, (110, 176, 236)), (0.55, (206, 232, 252)), (1, (206, 232, 252))]),
                   size=(MW, H))
        rng = np.random.default_rng(31)
        for x in range(200, MW, 600):
            D.cloud(c, x + rng.uniform(-60, 60), rng.uniform(40, 110), rng.uniform(0.6, 0.9))
        P.house_row(c, -20, 1050, 440, np.random.default_rng(9), 220, 300, s=0.9)
        P.house_row(c, 1600, MW + 20, 440, np.random.default_rng(10), 220, 300, s=0.9)
        # the weigh house (Waag) with its tower
        stone, roof = (234, 216, 174), (120, 70, 60)
        c.rect(1060, 230, 1590, 440, stone, w=3)
        for gx in (1060, 1235, 1415):
            pts = [(gx, 230)]
            for i in range(3):
                pts += [(gx + 14 * i, 230 - 26 * i - 26), (gx + 14 * (i + 1), 230 - 26 * i - 26)]
            pts += [(gx + 175 - p[0] + gx, p[1]) for p in reversed(pts[1:])] + [(gx + 175, 230)]
            c.poly(pts, stone, w=2.5)
        c.rect(1290, 70, 1360, 230, stone, w=2.5)
        c.poly([(1280, 74), (1325, 10), (1370, 74)], roof, w=2.5)
        c.circle(1325, 120, 22, (250, 250, 240), w=2)
        c.line([(1325, 120), (1325, 104)], OUT, 2.5)
        c.line([(1325, 120), (1337, 124)], OUT, 2.5)
        for k in range(6):
            wx = 1090 + k * 84
            c.rect(wx, 300, wx + 40, 360, (90, 110, 140), w=2)
            c.rect(wx - 8, 300, wx, 360, (200, 60, 50), w=1.5)
            c.rect(wx + 40, 300, wx + 48, 360, (200, 60, 50), w=1.5)
        c.rect(1280, 380, 1370, 440, (110, 70, 50), w=2.5, r=10)
        c.text(1325, 268, "WAAG", 26, (110, 60, 50))
        # the square
        ground = (196, 172, 146)
        c.rect(-5, 440, MW + 5, H + 5, ground, ol=None)
        c.rect(-5, 438, MW + 5, 446, (170, 150, 130), ol=None)
        for _ in range(2600):
            x, y = rng.uniform(0, MW), rng.uniform(450, H)
            r = 3 + (y - 440) / 40
            c.arc(x, y, r * 1.6, r * 0.8, 200, 340, mix(ground, (0, 0, 0), 0.14), 1.5)
        # rows of cheeses on straw, and loaded stretchers
        c.rect(880, 470, 2150, 520, (226, 206, 130), ol=None)
        for row, y in enumerate((486, 506)):
            for x in range(900 + row * 18, 2140, 38):
                P.cheese_side(c, x, y, 17, 11, label=False)
        for x in (1000, 1500, 1950):
            P.stretcher(c, x, 560, 0.75)
        # clog shop
        P.canal_house(c, 2280, 440, 280, 300, (60, 110, 90), np.random.default_rng(2), "bell")
        c.rect(2310, 340, 2530, 420, (120, 170, 200), w=2.5)
        c.rect(2300, 316, 2540, 340, (250, 214, 90), w=2)
        c.text(2420, 328, "KLOMPEN", 18, (120, 60, 30))
        for k in range(5):
            P.clog(c, 2340 + k * 42, 400, 0.8, face=1 if k % 2 else -1)
        return c.img
    return cached("market", make)


def stall_back(c, t):
    x0, x1 = STALL
    for px in (x0 + 10, x1 - 10):
        c.rect(px - 6, 300, px + 6, 620, P.WOOD_D, w=2)
    # striped awning
    n = 8
    for k in range(n):
        xa, xb = lerp(x0 - 20, x1 + 20, k / n), lerp(x0 - 20, x1 + 20, (k + 1) / n)
        c.poly([(xa, 290), (xb, 290), (xb, 340), (xa, 340)], (220, 60, 60) if k % 2 == 0 else (255, 250, 240),
               w=2)
        c.arc((xa + xb) / 2, 340, (xb - xa) / 2, 12, 0, 180, OUT, 2)
    c.rect(x0 - 24, 278, x1 + 24, 292, (200, 50, 50), w=2)
    c.rect(x0 + 120, 240, x1 - 120, 278, (255, 250, 236), w=2)
    c.text((x0 + x1) / 2, 259, "KAAS", 22, (200, 60, 50))


def stall_front(c, t, n_waffles=6):
    x0, x1 = STALL
    c.rect(x0, 520, x1, 640, (176, 120, 70), w=3)
    for k in range(1, 6):
        c.line([(x0 + k * (x1 - x0) / 6, 524), (x0 + k * (x1 - x0) / 6, 636)], (150, 100, 58), 2, cap=False)
    c.rect(x0 - 10, 510, x1 + 10, 526, (200, 150, 90), w=2.5)
    c.rect(x0 + 60, 560, x1 - 60, 600, (255, 248, 230), w=2)
    c.text((x0 + x1) / 2, 580, "STROOPWAFELS", 20, (150, 80, 30))
    # wares on the counter
    P.cheese_side(c, x0 + 50, 512, 36, 26)
    P.cheese_side(c, x0 + 50, 486, 30, 22, label=False)
    for k in range(n_waffles):
        P.stroopwafel(c, x1 - 120 + (k % 3) * 34, 500 - (k // 3) * 6, 15)
    # steam from the griddle
    for k in range(3):
        u = (t * 0.5 + k / 3) % 1.0
        pts = [(x1 - 60 + 10 * k + 5 * math.sin(t * 3 + v * 6 + k), 490 - 50 * u - 26 * v) for v in np.linspace(0, 1, 5)]
        c.line(pts, mix((255, 255, 255), (230, 220, 200), u), 3 * (1 - u) + 1)


def held_waffle(c, x, y, s, face, bite=0.0, pose="sit"):
    hx, hy = (18, -106) if pose == "sit" else (52, -86)
    px, py = x + face * (hx + 30) * s, y + (hy + 22) * s
    P.stroopwafel(c, px, py, 16 * s, bite)


def market(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["market"]
    ra, rb = T("m_roll", 0.06), T("m_roll", 0.8)
    crash = t >= rb
    wheel_keys = [(ra, BIG[0]), (lerp(ra, rb, 0.3), 1050), (rb, RACK[0] - 60)]
    if t < ra:
        wx = BIG[0] + (3 * math.sin(t * 40) if T("m_careful") <= t < ra else 0)
    elif t < rb:
        u = (t - ra) / (rb - ra)
        wx = lerp(BIG[0], RACK[0] - 60, u ** 1.6)
    else:
        wx = RACK[0] - 60 + 30 * ease(tl.prog("m_roll", t, 0.8, 0.86))
    cam_keys = [(s0, 0), (T("m_lean", 1), 220), (ra, 260), (rb, RACK[0] - 760), (s1, RACK[0] - 820)]
    if t < ra:
        camx = smooth(t, cam_keys, 0.5)
    else:
        camx = clamp(max(smooth(t, cam_keys, 0.5), wx - 640), 0, MW - W)
    c = view(market_bg(), clamp(camx, 0, MW - W))
    c.push(-camx, 0)
    stall_back(c, t)
    talk_m = tl.mouth("mies", t)
    P.mies(c, MIES_X, 530, 0.95, 1, t, mouth=talk_m, wave=1.0 if T("m_careful") <= t < T("m_careful", 1) else 0.0,
           eyes="happy" if T("m_eat") <= t < T("m_lean") else ("wide" if T("m_careful") <= t < rb else "open"),
           look=(1, 0))
    stall_front(c, t, 6 if t < T("m_hallo", 0.6) else 3)
    # the cheese pile and the giant cheese
    c.rect(860, MG - 14, 1010, MG, P.WOOD, w=2)
    P.cheese_side(c, 930, MG - 14, 60, 34)
    P.cheese_side(c, 930, MG - 48, 52, 30, label=False)
    ang = (wx - BIG[0]) / BIG[1]
    P.cheese_wheel(c, wx, MG - BIG[1], BIG[1], ang)
    # Luna and Bram
    flee = t >= T("m_purpose")
    lk = [(T("m_purpose"), 330), (T("m_purpose", 0.9), RACK[0] - 360)]
    bk = [(T("m_purpose", 0.1), 200), (T("m_ride"), RACK[0] - 480)]
    if not flee:
        kat(c, tl, t, "bram", 200, MG, 0.82, 1, "sit", look=(1, 0),
            eyes="wide" if ra <= t < rb else "open")
        kat(c, tl, t, "luna", 330, MG, 0.82, 1, "sit", look=(1, 0),
            eyes="happy" if T("m_eat") <= t < T("m_lean") else ("wide" if t >= T("m_careful") else "open"))
        if T("m_hallo", 0.6) <= t:
            held_waffle(c, 200, MG, 0.82, 1)
            held_waffle(c, 330, MG, 0.82, 1)
    else:
        actor(c, tl, t, "luna", lk, MG, 0.82, eyes="wide" if t < T("m_ride") else "happy")
        actor(c, tl, t, "bram", bk, MG, 0.82,
              mouth=laughing(t) * 0.7 if T("m_ride", 1) <= t else tl.mouth("bram", t),
              eyes="happy" if t >= T("m_ride") else "open")
    # Whiskers
    if t < T("m_lean"):
        e = "happy" if T("m_eat") <= t < T("m_genius") else "open"
        kat(c, tl, t, "whiskers", 620, MG, 0.85, -1, "sit", eyes=e,
            mouth=0.6 * abs(math.sin(t * 9)) if T("m_eat") <= t < T("m_eat", 1) else tl.mouth("whiskers", t))
        if t >= T("m_hallo", 0.6):
            bite = tl.prog("m_eat", t, 0.1, 0.9)
            held_waffle(c, 620, MG, 0.85, -1, bite)
    elif t < ra:
        u = ease(tl.prog("m_lean", t, 0.0, 0.8))
        x = lerp(620, BIG[0] - BIG[1] - 40, u)
        kat(c, tl, t, "whiskers", x, MG, 0.85, -1, "sit", eyes="happy" if t < T("m_careful") else "wide",
            head_dy=4 * u)
        held_waffle(c, x, MG, 0.85, -1, 0.9)
    elif t < rb:
        u = (t - ra) / (rb - ra)
        if u < 0.08:
            v = u / 0.08
            kat(c, tl, t, "whiskers", lerp(BIG[0] - BIG[1] - 40, wx, v), lerp(MG, MG - 2 * BIG[1], v) + arc_y(v, 60),
                0.85, 1, "leap", eyes="wide")
        else:
            kat(c, tl, t, "whiskers", wx, MG - 2 * BIG[1] + 4, 0.85, -1, "walk", walk=t * 26, eyes="wide",
                mouth=0.7, squash=1.0 + 0.04 * math.sin(t * 26))
            for k in range(3):
                c.line([(wx - 100 - k * 30, MG - 40 - k * 30), (wx - 160 - k * 40, MG - 40 - k * 30)],
                       (255, 255, 255), 3)
    else:
        u = tl.prog("m_roll", t, 0.8, 0.97)
        x = lerp(wx, RACK[0] - 160, u)
        if u < 1:
            kat(c, tl, t, "whiskers", x, lerp(MG - 2 * BIG[1], MG, u) + arc_y(u, 160), 0.85, -1, "leap", eyes="wide")
        else:
            dazed = t < T("m_purpose")
            kat(c, tl, t, "whiskers", x, MG, 0.85, 1, "sit", eyes="closed" if dazed else "open", look=(-1, 0))
            hx, hy = x + 18 * 0.85, MG - 106 * 0.85
            P.clog(c, hx, hy - 24, 0.75, face=-1)
            if dazed:
                for k in range(3):
                    a = t * 4 + k * 2.1
                    c.text(hx + 40 * math.cos(a), hy - 50 + 12 * math.sin(a), "*", 26, (255, 230, 90), stroke=2)
    # the clog rack: full until the crash, then clogs flying everywhere
    rx0, rx1 = RACK
    rng = np.random.default_rng(17)
    c.rect(rx0, MG - 150, rx0 + 10, MG, P.WOOD_D, w=2)
    c.rect(rx1 - 10, MG - 150, rx1, MG, P.WOOD_D, w=2)
    for row in range(3):
        y = MG - 120 + row * 44
        c.line([(rx0, y), (rx1, y)], P.WOOD, 5)
        for k in range(4):
            x = rx0 + 22 + k * 38
            dt = t - rb
            if dt < 0:
                P.clog(c, x, y + 26, 0.62, face=1 if k % 2 else -1)
            else:
                vx, vy = rng.uniform(-320, 120), rng.uniform(-420, -200)
                land = MG - rng.uniform(0, 30)
                gx = x + vx * min(dt, 1.4)
                gy = min(land, y + 26 + vy * dt + 520 * dt * dt)
                P.clog(c, gx, gy, 0.62, face=1 if k % 2 else -1)
    if 0 <= t - rb < 0.6:
        bang(c, RACK[0] - 10, MG - 150, 1.0 + 0.4 * (t - rb), "BONK!")
    c.pop()
    return finish(c, tl, t)


# ================================================================= lesson

def lesson(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["lesson"]
    hbx = HB[0]
    # positions
    sa, sb = T("le_splash"), T("le_splash", 0.3)
    w_keys = [(T("le_wobble"), 2800), (T("le_which", 1), 3300), (sb, 3380)]
    l_keys = [(T("le_luna", 0.15), 2960), (T("le_luna", 1), 3440), (T("le_flying", 0.2), 3500),
              (T("le_flying", 1), 3150), (T("le_wobble", 0.5), 3050), (T("le_splash", 0.5), 3200),
              (T("le_giveup"), 3290)]
    cam = [(s0, 2280), (T("le_luna", 1), 2600), (T("le_flying", 1), 2560), (T("le_which", 1), 2780),
           (sb, 2840)]
    camx = smooth(t, cam, 0.8)
    c = canal_view(False, camx)
    c.push(-camx, 0)
    traffic(c, t, camx, lane=536, n=3, seed=7)
    P.houseboat(c, *HB[:2], HB[2], t)
    # Bram watches, cheering
    bram_x = smooth(t, [(s0, 2560), (T("le_narr", 1), 2680), (T("le_splash", 0.4), 2680),
                        (T("le_giveup", 0.2), 3180)], 0.4)
    kat(c, tl, t, "bram", bram_x, STREET - 6, 0.8, 1, "sit" if t < T("le_splash", 0.4) else "stand",
        eyes="happy" if T("le_luna") <= t < T("le_wobble") else ("wide" if sa <= t < T("le_splash", 0.6) else "open"))
    # parked bikes until they get on
    if t < T("le_luna", 0.15):
        P.bicycle(c, 2960, STREET, 0.8, 1, 0.0, col=(60, 110, 180))
    if t < T("le_wobble"):
        P.bicycle(c, 2800, STREET + 4, 0.8, 1, 0.0, col=(240, 140, 40))
    # Luna
    if t < T("le_luna", 0.15):
        actor(c, tl, t, "luna", [(s0, 2400), (T("le_narr", 1), 2880)], STREET, 0.8)
    else:
        lx = smooth(t, l_keys, 0.4)
        v = speed(t, l_keys, 0.4)
        face = 1 if v >= -5 else -1
        stop = abs(v) < 5
        rider(c, tl, t, "luna", lx, STREET - 14, 0.8, face, dist=lx * face, bike_col=(60, 110, 180),
              eyes="happy" if T("le_luna") <= t < T("le_flying", 1) else ("wide" if sa <= t < T("le_giveup") else "open"),
              arm_up=1.0 if T("le_flying") <= t < T("le_flying", 1) else 0.0)
    # Whiskers
    if t < T("le_wobble"):
        actor(c, tl, t, "whiskers", [(s0, 2320), (T("le_narr", 1), 2740)], STREET + 4, 0.8,
              eyes="wide" if T("le_flying") <= t else "open")
    elif t < sb:
        x = smooth(t, w_keys, 0.3)
        wob = math.sin((t - T("le_wobble")) * 5.5) * 13 + math.sin(t * 13) * 4
        y = STREET + 4 + 8 * math.sin(t * 3)
        if t >= T("le_which", 1):
            u = (t - T("le_which", 1)) / max(1e-6, sb - T("le_which", 1))
            wob = lerp(wob, -70, ease(u))
            y = lerp(y, STREET + 70, u * u)
        mouth = tl.mouth("whiskers", t) if tl.talking("whiskers", t) else 0.45

        def draw(cc, x=x):
            P.bike_cat(cc, 0, 0, D.WHISKERS, 0.8, 1, x, t, mouth=mouth, eyes="wide", bike_col=(240, 140, 40))
        tilted(c, x, y, wob, draw)
    else:
        # in the canal, then sitting on the edge, dripping
        u = tl.prog("le_splash", t, 0.3, 1.0)
        sx = 3430
        if u < 0.45:
            v = u / 0.45
            D.cat(c, sx, 680 - 18 * math.sin(v * math.pi), D.WHISKERS, 0.8, 1, "swim", t=t, eyes="wide",
                  mouth=0.6, wet=1.0)
        elif u < 0.7:
            v = (u - 0.45) / 0.25
            kat(c, tl, t, "whiskers", sx - 10 * v, lerp(680, QUAY + 2, v) + arc_y(v, 50), 0.8, -1, "leap", wet=1.0)
        else:
            kat(c, tl, t, "whiskers", sx - 10, QUAY + 2, 0.8, -1, "sit", wet=1.0, eyes="closed" if t < T("le_giveup") else "open",
                look=(0, 1), head_dy=6)
        splash_fx(c, 3400, 640, t - sb, 1.0)
        # bubbles where the bike sank
        for k in range(3):
            bu = ((t - sb) * 0.8 + k / 3) % 1.0
            if t - sb > 0.6:
                c.circle(3460 + 10 * k, 700 - 50 * bu, 4 + 2 * k, None, ol=(220, 240, 255), w=2)
    c.pop()
    water_glints(c, t, camx)
    return finish(zoom(c, 128, 144, 1024), tl, t)


# =================================================================== dusk

def dusk(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["dusk"]
    rs = T("d_try")
    let_go = T("d_doing", 0.3)
    wk = [(rs, 3100), (T("d_try", 1), 3330), (T("d_letgo", 1), 3720), (T("d_ride", 0.45), 3980),
          (T("d_ride", 0.7), 4040), (T("d_riding", 1), 3820), (s1, 3780)]
    wx_ride = smooth(t, wk, 0.6)
    cam = [(s0, 2560), (rs, 2600), (T("d_try", 1), 2860), (T("d_letgo", 0.5), 3040), (T("d_ride", 0.6), 3160),
           (s1, 3080)]
    camx = smooth(t, cam, 0.8)
    c = canal_view(True, camx)
    c.tint = ((255, 150, 90), 0.06)
    c.push(-camx, 0)
    traffic(c, t, camx, lane=536, n=2, seed=9)
    sitx = 3080
    dry = clamp(1 - tl.prog("d_bram", t))
    if t < rs:
        kat(c, tl, t, "whiskers", sitx, QUAY + 2, 0.8, 1, "sit", wet=0.4 + 0.6 * dry,
            eyes="closed" if t < T("d_bram") else "open", look=(-0.8, 0.6) if t < T("d_bram") else (-1, 0),
            head_dy=8 if t < T("d_trick") else 0)
        lx = actor(c, tl, t, "luna", [(T("d_sit", 0.1), 3500), (T("d_sit", 1), 3180)], QUAY + 2, 0.78, face=-1,
                   pose="sit" if t > T("d_sit", 1) else "stand",
                   eyes="happy" if T("d_promise") <= t else "open")
        actor(c, tl, t, "bram", [(T("d_sit", 0.0), 2650), (T("d_sit", 0.9), 2960)], QUAY + 2, 0.78, face=1,
              pose="sit" if t > T("d_sit", 1) else "stand",
              eyes="happy" if T("d_bram", 0.6) <= t < T("d_trick") else "open")
        P.bicycle(c, 3250, STREET - 12, 0.8, -1, 0.0, col=(240, 140, 40))
    else:
        # Bram cheers from the side
        kat(c, tl, t, "bram", 2960, QUAY + 2, 0.78, 1, "sit", eyes="happy")
        # Whiskers rides; Luna holds the seat, then lets go
        face = 1 if speed(t, wk, 0.6) >= -5 else -1
        hold = t < let_go
        if hold:
            lxx = wx_ride - 96
        else:
            lxx = smooth(t, [(let_go, wx_ride if False else smooth(let_go, wk, 0.6) - 96),
                             (let_go + 0.6, smooth(let_go, wk, 0.6) - 70)], 0.3)
        wob = 0.0
        if T("d_ride") <= t < T("d_ride", 0.3):
            wob = 14 * math.sin((t - T("d_ride")) * 16) * (1 - tl.prog("d_ride", t, 0.0, 0.3))
        elif t < let_go:
            wob = 4 * math.sin(t * 7)
        look = (-1, 0) if T("d_letgo") <= t < T("d_ride", 0.2) else (1, 0)
        e = "wide" if T("d_letgo", 0.4) <= t < T("d_ride", 0.25) else ("happy" if t >= T("d_ride", 0.3) and
                                                                      tl.mouth("whiskers", t) < 0.1 else "open")
        arm = 1.0 if t >= T("d_riding") and face < 0 else 0.0

        def draw(cc):
            P.bike_cat(cc, 0, 0, D.WHISKERS, 0.8, face, wx_ride * face, t, mouth=tl.mouth("whiskers", t), eyes=e,
                       look=look, bike_col=(240, 140, 40), arm_up=arm)
        moving_luna = hold or t < let_go + 0.6
        kat(c, tl, t, "luna", lxx, STREET + 4, 0.78, 1, "walk" if moving_luna else "sit",
            walk=lxx / 9.6, eyes="happy" if t >= T("d_letgo") else "open", look=(1, -0.3))
        if hold:
            # Luna's paw on the saddle
            sx, sy = wx_ride + P.SADDLE[0] * 0.8, STREET - 4 + P.SADDLE[1] * 0.8 + 6
            c.stroke([(lxx + 40, STREET - 58), (sx - 6, sy)], D.LUNA["body"], 9)
            c.ellipse(sx - 4, sy, 6, 5, D.LUNA["body"], w=2)
        tilted(c, wx_ride, STREET - 4, wob, draw)
        if T("d_ride", 0.3) <= t < T("d_ride", 0.5) or T("d_riding", 0.6) <= t < T("d_riding", 0.8):
            c.text(wx_ride + 40 * face, STREET - 180, "RING RING!", 22, (255, 230, 90), stroke=2)
    c.pop()
    c.tint = None
    water_glints(c, t, camx, True)
    return finish(zoom(c, 128, 144, 1024), tl, t)


# ================================================================= parade

def deck_y(x):
    return 470 + 0.00019 * (x - 640) ** 2


def parade_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (100, 170, 236)), (0.5, (206, 232, 252)), (1, (206, 232, 252))]))
        for x, y, s in ((200, 90, 0.8), (700, 60, 0.7), (1100, 110, 0.9)):
            D.cloud(c, x, y, s)
        P.house_row(c, -20, W + 20, 420, np.random.default_rng(21), 220, 300, s=0.85)
        for x in (90, 1190):
            P.elm(c, x, 430, 0.9)
        c.rect(-5, 418, W + 5, 432, (196, 186, 172), w=2)
        water = P.WATER
        c.rect(-5, 432, W + 5, H + 5, water, ol=None)
        rng = np.random.default_rng(2)
        for _ in range(240):
            x, y = rng.uniform(0, W), rng.uniform(440, H)
            c.line([(x, y), (x + rng.uniform(16, 44), y)], mix(water, (255, 255, 255), 0.3), 2, cap=False)
        # moored boat with flowers
        c.push(1060, 520, 0.5)
        c.poly([(-200, -30), (200, -30), (220, 0), (-210, 0)], (60, 90, 140), w=3)
        P.tulip_bunch(c, -100, -30, 1.2, 7, 5)
        P.tulip_bunch(c, 80, -30, 1.2, 7, 6)
        c.pop()
        # the bridge
        brick = (176, 92, 70)
        pts = [(x, deck_y(x)) for x in range(-20, W + 40, 20)]
        c.poly(pts + [(W + 20, H + 5), (-20, H + 5)], brick, w=3)
        for k in range(1, 8):
            ys = [(x, deck_y(x) + k * 30) for x in range(-20, W + 40, 40)]
            c.line(ys, mix(brick, (0, 0, 0), 0.15), 1.5, cap=False)
        for ax in (220, 640, 1060):
            top = deck_y(ax) + 90
            c.ellipse(ax, H + 30, 150, H + 30 - top, mix(water, (0, 0, 0), 0.35), w=3)
            c.ellipse(ax, H + 30, 136, H + 30 - top - 14, mix(water, (0, 0, 0), 0.2), ol=None)
            for k in range(-6, 7):
                a = math.pi / 2 + k * 0.2
                c.line([(ax + math.cos(a) * 150, H + 30 - math.sin(a) * (H + 30 - top)),
                        (ax + math.cos(a) * 168, H + 30 - math.sin(a) * (H + 50 - top))], (226, 210, 180), 3,
                       cap=False)
        # stone cap along the deck
        cap = [(x, deck_y(x) + 2) for x in range(-20, W + 40, 20)]
        c.line(cap, (226, 214, 190), 10, cap=False)
        return c.img
    return cached("parade_bg", make)


def railing(c, t):
    rail = [(x, deck_y(x) + 36) for x in range(-20, W + 40, 20)]
    for x in range(10, W, 64):
        y = deck_y(x) + 36
        c.line([(x, y), (x, y + 34)], (50, 60, 70), 4, cap=False)
    c.line(rail, (50, 60, 70), 5, cap=False)
    for x in range(40, W, 128):
        y = deck_y(x) + 36
        c.rect(x - 34, y - 2, x + 34, y + 16, (120, 80, 50), w=2)
        P.tulip_bunch(c, x, y, 0.8, 6, int(x), t)


def parade(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["parade"]
    c = Canvas(parade_bg().copy())
    # bunting across the canal
    P.bunting(c, -20, W + 20, 50, 70, 24)
    P.bunting(c, -20, W + 20, 140, 40, 28, cols=((240, 240, 240), P.ORANGE))
    # Joost flies over the parade
    jx = lerp(-200, W + 200, tl.prog("p_narr", t, 0.0, 1.0) * 0.4 + tl.prog("p_ride", t) * 0.6)
    if t < T("p_ride", 1):
        P.stork(c, jx, 220 + 20 * math.sin(t * 2), 0.8, 1, t, "fly", flap=t * 6)
    else:
        u = tl.prog("p_bell", t, 0.0, 1.0) * 0.5 + tl.prog("p_wobble", t) * 0.2 + tl.prog("p_end", t) * 0.3
        P.stork(c, lerp(W + 200, -200, u), 200 + 20 * math.sin(t * 2), 0.8, -1, t, "fly", flap=t * 6)
    # the parade: a line of decorated bicycles, our three friends in the middle
    gk = [(s0, -1100), (T("p_hooray"), 760), (T("p_wobble", 1), 900), (s1, 1900)]
    gx = smooth(t, gk, 0.6)
    for k in range(6):
        x = gx + (260 + 230 * k if k < 3 else -560 - 230 * (k - 3))
        if -200 < x < W + 200:
            P.bike_cat(c, x, deck_y(x), TRAFFIC_PALS[k % 4], 0.78, 1, x, t, seed=k * 0.9,
                       bike_col=TRAFFIC_COLS[k % 5], flowers=8, eyes="happy")
    pip_cheer = T("p_faster") <= t < T("p_faster", 1)

    def pip_in_basket(cc):
        D.mouse(cc, 60, -92 - (6 * abs(math.sin(t * 8)) if pip_cheer else 0), 0.62, 1, t,
                mouth=tl.mouth("pip", t), eyes="happy" if t >= T("p_bell") else "open", proud=pip_cheer)
    for who, off, col in (("bram", -330, (60, 140, 90)), ("luna", -170, (60, 110, 180)), ("whiskers", 0, (240, 140, 40))):
        x = gx + off
        if -200 < x < W + 200:
            arm = 1.0 if (who == "luna" and T("p_wobble") <= t) or (who == "bram" and T("p_hooray") <= t < T("p_bell")) \
                else 0.0
            if who == "whiskers" and T("p_wobble") <= t < T("p_wobble", 1):
                arm = 1.0
            rider(c, tl, t, who, x, deck_y(x), 0.85, 1, dist=x, flowers=10, bike_col=col,
                  front_fn=pip_in_basket if who == "whiskers" else None, arm_up=arm,
                  eyes="happy" if tl.mouth(who, t) < 0.1 else "open")
    if T("p_bell") <= t < T("p_bell", 1):
        k = tl.prog("p_bell", t)
        c.text(gx + 60, deck_y(gx) - 190 - 10 * math.sin(k * 20), "RING RING RING!", 24, (255, 230, 90), stroke=2)
    railing(c, t)
    # Mies cheering in the front corner
    P.mies(c, 1150, 780, 1.15, -1, t, mouth=tl.mouth("mies", t),
           wave=1.0 if T("p_ride", 0.5) <= t else 0.0, eyes="happy" if tl.mouth("mies", t) < 0.1 else "open")
    petals(c, t, 46, 3, speed=60)
    return finish(c, tl, t)


# =================================================================== home

def town_night():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (14, 18, 52)), (0.6, (40, 46, 100)), (1, (70, 64, 120))]))
        D.stars(c, 41, 140, W, 420)
        D.moon(c, 860, 220, 110, sky=(26, 32, 76))
        rng = np.random.default_rng(5)
        x = -10
        while x < W:
            w = rng.uniform(90, 160)
            h = rng.uniform(80, 170)
            c.rect(x, H - h, x + w, H, (40, 44, 80), ol=None)
            c.poly([(x - 8, H - h), (x + w / 2, H - h - 50), (x + w + 8, H - h)], (52, 50, 90), ol=None)
            for wx in range(int(x) + 20, int(x + w) - 20, 40):
                if rng.random() < 0.5:
                    c.rect(wx, H - h + 30, wx + 18, H - h + 52, (255, 214, 120), ol=None)
            x += w
        return c.img
    return cached("town_night", make)


def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    if t < T("h_sill"):
        c = Canvas(town_night().copy())
        u = tl.prog("h_fly", t) * 0.45 + tl.prog("h_narr", t) * 0.55
        jx, jy = lerp(-250, W + 250, u), 260 - 60 * math.sin(u * math.pi)
        tip = P.stork(c, jx, jy, 0.9, 1, t, "fly", flap=t * 5)
        bx, by = tip[0] + 6, tip[1] + 74
        c.line([tip, (bx - 46, by)], (120, 90, 60), 2, cap=False)
        c.line([tip, (bx + 46, by)], (120, 90, 60), 2, cap=False)

        def pip(cc):
            D.mouse(cc, bx, by + 2, 0.7, 1, t, eyes="happy")
        basket_load(c, tl, t, bx, by, 0.66, pip=pip, eyes={"whiskers": "happy", "luna": "happy"})
        return finish(c, tl, t)
    c = Canvas(outside(True).copy())
    jx, jy, js = JOOST_STAND
    gone = T("h_teach", 0.1)
    if t < gone:
        P.stork(c, jx, jy, js, -1, t, "stand", mouth=tl.mouth("joost", t), head_dx=18,
                wing_wave=1.0 if T("h_bye") <= t < T("h_bye", 1) + 0.4 else 0.0)
    else:
        u = tl.prog("h_teach", t, 0.1, 1.0)
        if u < 1:
            P.stork(c, lerp(jx, 220, u ** 1.2), lerp(jy - 148 * js, -200, u ** 0.8), 1.3, -1, t, "fly", flap=t * 7)
    front = room_front(True, True)
    c.img.paste(front, (0, 0), front)
    c.tint = ((40, 40, 100), 0.18)
    # souvenirs on the sill: a pot of tulips and a pair of little clogs
    c.rect(330, SILL - 46, 390, SILL, (200, 110, 70), w=2.5, r=4)
    P.tulip_bunch(c, 360, SILL - 44, 1.2, 5, 11, t * 0.3)
    P.clog(c, 900, SILL, 0.8, face=-1)
    P.clog(c, 940, SILL, 0.8, face=-1)
    curl = t >= T("h_curl")
    if not curl:
        talk_l = T("h_lesson") <= t
        kat(c, tl, t, "luna", 470, SILL, 1.0, 1, "sit", eyes="happy" if talk_l else "open", look=(1, 0))
        D.mouse(c, 625, SILL, 1.5, 1, t, mouth=tl.mouth("pip", t), proud=T("h_teach") <= t < T("h_teach", 1),
                eyes="happy" if T("h_lesson", 0.5) <= t else "open")
        kat(c, tl, t, "whiskers", 790, SILL, 1.0, -1, "sit",
            eyes="happy" if T("h_lesson", 0.95) <= t else "open", look=(-1, 0.3) if t >= T("h_teach") else (1, -0.6))
    else:
        kat(c, tl, t, "luna", 520, SILL, 0.95, 1, "sleep", mouth=0)
        D.mouse(c, 640, SILL - 4, 1.2, -1, t, eyes="closed")
        kat(c, tl, t, "whiskers", 770, SILL, 0.95, -1, "sleep", mouth=0)
        D.zzz(c, 800, 380, t)
    c.tint = None
    c = zoom(c)
    k = ease(tl.prog("h_end", t, 0.15, 0.45))
    if k > 0:
        c.text(W / 2, 630, "The End", 30 + 44 * k, mix((150, 140, 170), (255, 236, 200), k), stroke=4 * k,
               stroke_fill=(60, 40, 60))
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "letter": letter, "flight": flight, "canal": canal, "market": market,
               "lesson": lesson, "dusk": dusk, "parade": parade, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["h_sill", "h_curl"]
