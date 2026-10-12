"""Scenes of "Whiskers and the Yellow Tram". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
Static layers are cached; the tram on Lisbon's steep hills is drawn into its
own layer and rotated (props.rotated).
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.lisbon import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "tiago": 3.3, "avo": 4.4, "pavao": 5.5}
CINNAMON = {**D.LUNA, "body": (176, 140, 120), "dark": (150, 112, 92), "belly": (226, 200, 180)}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


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


def etrack(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]


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
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def tiago(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("tiago", t))
    P.dog(c, x, y, s, face, t, P.TIAGO, mouth=mouth, seed=SEED["tiago"], **kw)


def avo(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("avo", t))
    kw.setdefault("pose", "sit")
    P.dog(c, x, y, s, face, t, P.AVO, mouth=mouth, seed=SEED["avo"], scarf=None, cap=None, shawl=(34, 30, 40),
          glasses=True, **kw)


def pavao(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("pavao", t))
    P.peacock(c, x, y, s, face, t, mouth=mouth, seed=SEED["pavao"], **kw)


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def arc(u, h):
    return -4 * h * u * (1 - u)


def finish(c, tl, t, strength=0.55):
    c.tf = [(0.0, 0.0, 1.0, 1.0)]
    c.tint = None
    P.shade_bottom(c, tl, t, strength)
    return c


def cam(bg, cx, cy, z=1.0):
    """Canvas showing the part of the world image bg centred on (cx, cy) at zoom z.
    Draw world-space things afterwards: the transform is already set."""
    bw, bh = bg.size[0] / SS, bg.size[1] / SS
    if z <= 1.001:
        x0 = clamp(cx - W / 2, 0, bw - W)
        y0 = clamp(cy - H / 2, 0, bh - H)
        if bw == W and bh == H:
            c = Canvas(bg.copy())
        else:
            c = Canvas(bg.crop((int(x0 * SS), int(y0 * SS), int(x0 * SS) + W * SS, int(y0 * SS) + H * SS)))
        c.push(-x0, -y0, 1.0)
        return c
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, bw - w)
    y0 = clamp(cy - h / 2, 0, bh - h)
    crop = bg.crop((int(x0 * SS), int(y0 * SS), int((x0 + w) * SS), int((y0 + h) * SS)))
    c = Canvas(crop.resize((W * SS, H * SS), Image.BILINEAR))
    c.push(-x0 * z, -y0 * z, z)
    return c


def paste_scroll(c, img, off, tile_w=None):
    off_px = int(off * SS)
    if tile_w:
        tw = tile_w * SS
        off_px %= tw
        piece = img.crop((off_px, 0, off_px + W * SS, H * SS))
        c.img.paste(piece, (0, 0), piece)
        if off_px + W * SS > tw:
            rest = img.crop((0, 0, off_px + W * SS - tw, H * SS))
            c.img.paste(rest, (tw - off_px, 0), rest)
    else:
        piece = img.crop((off_px, 0, off_px + W * SS, H * SS))
        c.img.paste(piece, (0, 0), piece)


def bubble(c, x, y, rx, ry, k, tail=(0, 0), fill=(255, 255, 255)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 8), (0.65, 13)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, fill, ol=None)


def smell(c, x0, y0, x1, y1, t, k=1.0, col=(255, 236, 200)):
    """Wavy smell wisps drifting from (x0, y0) to (x1, y1)."""
    if k <= 0.02:
        return
    for j in range(3):
        pts = []
        ph = t * 3 + j * 2.1
        for u in np.linspace(0, 1, 16):
            px = lerp(x0, x1, u)
            py = lerp(y0, y1, u) + 10 * math.sin(u * 12 + ph) + (j - 1) * 14
            pts.append((px, py))
        cut = int(16 * k)
        if cut >= 2:
            c.line(pts[:cut], mix((255, 255, 255), col, 0.5), 5)
            c.line(pts[:cut], col, 3)


def cobbles(c, x0, y0, x1, y1, seed=0, light=(236, 232, 222), dark=(60, 60, 66), waves=True):
    """Calcada portuguesa: white stone pavement with black wave patterns."""
    c.rect(x0, y0, x1, y1, light, ol=None)
    if waves:
        for row in range(int((y1 - y0) / 40) + 1):
            yy = y0 + 14 + row * 40
            pts = [(x, yy + 9 * math.sin(x / 38 + row)) for x in range(int(x0), int(x1) + 20, 16)]
            c.line(pts, dark, 6, cap=False)
    rng = np.random.default_rng(seed)
    for _ in range(int((x1 - x0) * (y1 - y0) / 900)):
        px, py = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.circle(px, py, 1.4, mix(light, dark, 0.25), ol=None)


def ground_shadow(c, x, y, rx, ry=None, k=0.25):
    c.ellipse(x, y, rx, ry or rx * 0.18, mix((0, 0, 0), (120, 120, 120), 0.5), ol=None) if False else None


# ===================================================================== title

RIVER_Y = 470


def lisbon_panorama(sunset=0.0):
    """Wide view of Lisbon: the Tagus, the bridge, roofs climbing to the castle."""
    def make():
        sky = [(0, mix((110, 170, 235), (60, 70, 140), sunset)), (0.45, mix((190, 220, 245), (240, 140, 120), sunset)),
               (0.66, mix((255, 226, 170), (255, 190, 120), sunset)), (1, (255, 226, 170))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        c.glow(1040, 330, 150, 150, (255, 246, 210), mix((255, 226, 170), (255, 190, 120), sunset), steps=8)
        c.circle(1040, 330, 40, (255, 240, 190), ol=None)
        D.cloud(c, 220, 230, 0.8, col=(255, 246, 236))
        D.cloud(c, 700, 190, 0.6, col=(255, 246, 236))
        # far bank + Cristo Rei
        far = (176, 160, 170)
        c.poly([(560, RIVER_Y), (620, 418), (760, 402), (900, 410), (1080, 396), (1290, 410), (1290, RIVER_Y)],
               far, ol=None)
        P.cristo_rei(c, 1130, 400, 0.45, col=(214, 200, 196))
        # the river
        c.rect(0, RIVER_Y - 4, W, 560, (110, 160, 210), ol=None)
        for k in range(26):
            x = (k * 151) % W
            y = RIVER_Y + 10 + (k * 37) % 70
            c.line([(x, y), (x + 40, y)], (200, 225, 245), 2, cap=False)
        c.ellipse(1040, RIVER_Y + 30, 60, 10, (255, 236, 190), ol=None)
        # the bridge
        P.bridge(c, 540, 1290, 440, (720, 1040), 300, far=True)
        # a caravel on the river
        P.caravel(c, 860, 520, 0.28, bob=False)
        # the hill of the old town with the castle on top
        hill = [(-20, 600), (-20, 330), (80, 300), (200, 268), (330, 262), (430, 300), (560, 360), (660, 420),
                (760, 470), (760, 600)]
        c.poly(hill, (226, 210, 186), ol=None)
        P.castle_wall(c, 140, 420, 290, 46, towers=((180, 60, 50), (300, 70, 66), (390, 54, 40)), seed=1)
        P.cross_flag(c, 190, 194, 0.55)
        D.tree(c, 470, 330, 0.35, leaf=(110, 150, 80))
        D.tree(c, 110, 320, 0.4, leaf=(110, 150, 80))
        hill_y = lambda x: float(np.interp(x, [p[0] for p in hill], [p[1] for p in hill])) + 16
        P.roofs(c, -20, 760, 300, 620, seed=2, scale=1.0, top_fn=hill_y, row=34)
        # the near street with the tram line
        c.rect(0, 588, W, H, (200, 192, 180), ol=None)
        cobbles(c, 0, 600, W, H, seed=3)
        c.rect(0, 664, W, 670, (120, 120, 130), ol=None)
        c.rect(0, 678, W, 684, (120, 120, 130), ol=None)
        c.line([(0, 30), (W, 60)], (60, 60, 70), 1.5, cap=False)
        return c.img
    return cached(("pano", sunset), make)


def tram_cats(tl, t, luna=True, whiskers=True, whiskers_sleep=False, luna_look=(1, 0), luna_lean=0.0,
              whiskers_eyes="open", luna_eyes="open", wx=73, lx=-39, s=0.7):
    """Draw-callback putting the cats in the tram's windows (window centres at -133 + 56 k)."""
    def inside(c):
        if whiskers:
            if whiskers_sleep:
                kat(c, tl, t, "whiskers", wx - 20, -122, s, 1, "sleep")
            else:
                kat(c, tl, t, "whiskers", wx, -84, s, 1, "sit", eyes=whiskers_eyes, look=(1, 0))
        if luna:
            kat(c, tl, t, "luna", lx, -84 - luna_lean, s, 1, "sit", look=luna_look, eyes=luna_eyes)
    return inside


def title(tl, t):
    T = tl.t
    c = Canvas(lisbon_panorama().copy())
    # seagulls
    for k in range(3):
        gx = (t * 40 + k * 430) % (W + 200) - 100
        P.gull(c, gx, 140 + 30 * k + 8 * math.sin(t * 1.3 + k), 0.6 - 0.1 * k, 1, t, seed=k)
    # the tram crosses the street, the cats at the windows
    u = tl.prog("t_open", t, 0.0, 1.0) * 0.6 + tl.prog("t_hold", t) * 0.4
    tx = lerp(-260, 880, u)
    P.tram(c, tx, 664, 1.05, t, inside=tram_cats(tl, t, luna_look=(-1, -0.6), whiskers_eyes="happy",
                                                    luna_eyes="happy"),
           wheel_ang=tx / 15)
    k = ease(tl.prog("t_open", t, 0.25, 0.7))
    c.text(W / 2, 70 - 30 * (1 - k), "Whiskers and the", 44, mix((150, 190, 235), (255, 252, 240), k),
           stroke=3 * k, stroke_fill=(40, 60, 110))
    k2 = ease(tl.prog("t_open", t, 0.5, 1.0))
    if k2 > 0:
        c.text(W / 2, 150, "YELLOW TRAM", 28 + 56 * k2, mix((150, 190, 235), P.YELLOW, k2), stroke=5 * k2,
               stroke_fill=(120, 60, 20))
    return finish(c, tl, t)


# ====================================================================== sill

SILL = 430
STREET_Y = 650


def home_bg(night=False):
    def make():
        if night:
            sky = [(0, (20, 24, 64)), (0.6, (50, 50, 110)), (1, (70, 60, 120))]
        else:
            sky = [(0, (120, 182, 240)), (0.6, (210, 232, 250)), (1, (214, 234, 250))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        nc = (40, 40, 90)
        dk = 0.55 if night else 0.0
        if night:
            D.stars(c, 8, 90, W, 300)
            D.moon(c, 1000, 120, 40, sky=(30, 34, 80))
        else:
            D.cloud(c, 900, 100, 0.9)
            D.cloud(c, 1180, 170, 0.6)
        # houses across the street
        for x, w, h, col in ((660, 190, 300, (234, 214, 170)), (850, 170, 250, (196, 150, 130)),
                             (1020, 260, 330, (226, 226, 210))):
            col = mix(col, nc, dk)
            c.rect(x, 560 - h, x + w, 560, col, w=2.5)
            c.poly([(x - 10, 560 - h), (x + w / 2, 560 - h - 56), (x + w + 10, 560 - h)], mix((150, 80, 70), nc, dk),
                   w=2.5)
            for wy in range(int(560 - h + 40), 500, 80):
                for wx in range(int(x) + 24, int(x + w) - 30, 56):
                    lit = night and ((wx + wy) // 7) % 3 != 0
                    c.rect(wx, wy, wx + 28, wy + 38, (255, 214, 130) if lit else mix((170, 210, 240), nc, dk), w=2)
        D.tree(c, 1250, 560, 0.9, leaf=mix((110, 170, 80), nc, dk))
        D.tree(c, 640, 560, 0.7, leaf=mix((100, 160, 80), nc, dk))
        # pavement + road
        c.rect(0, 556, W, 600, mix((200, 196, 190), nc, dk), ol=None)
        c.line([(0, 556), (W, 556)], OUT, 2.5, cap=False)
        c.rect(0, 600, W, H, mix((110, 112, 120), nc, dk), ol=None)
        c.rect(0, 598, W, 606, mix((150, 150, 156), nc, dk), ol=None)
        for x in range(30, W, 160):
            c.rect(x, 690, x + 80, 696, mix((240, 236, 220), nc, dk), ol=None)
        if night:
            c.glow(600, 420, 90, 90, (255, 230, 160), (60, 60, 110), steps=8)
        c.rect(596, 420, 604, 556, (50, 50, 60), w=2)
        c.rect(584, 400, 616, 428, (255, 230, 150) if night else (230, 230, 210), w=2.5, r=4)
        c.poly([(580, 402), (600, 386), (620, 402)], (50, 50, 60), w=2)
        # the cats' house (left)
        wall = mix((244, 222, 178), nc, dk * 0.8)
        c.rect(-10, 0, 560, 556, wall, w=3)
        for y in range(20, 556, 34):
            c.line([(-10, y), (560, y)], mix(wall, (150, 110, 70), 0.25), 2, cap=False)
        c.rect(-10, 0, 560, 24, mix((150, 80, 70), nc, dk), w=3)
        room = (255, 214, 150) if night else (250, 214, 160)
        c.rect(130, 200, 450, SILL, (120, 92, 80), w=3)
        c.rect(138, 208, 442, SILL, room, ol=None)
        c.rect(138, 330, 442, SILL, mix(room, (200, 140, 100), 0.5), ol=None)
        c.rect(360, 240, 420, 310, (150, 100, 60), w=2)
        c.rect(366, 246, 414, 304, (40, 46, 96), ol=None)
        c.circle(398, 262, 8, (250, 246, 215), ol=None)
        for x0, x1 in ((92, 132), (448, 488)):
            c.rect(x0, 190, x1, SILL, mix((70, 130, 170), nc, dk), w=2.5)
            for y in range(204, SILL - 6, 18):
                c.line([(x0 + 4, y), (x1 - 4, y)], mix((50, 104, 140), nc, dk), 2, cap=False)
        c.rect(100, SILL, 480, SILL + 18, mix((250, 246, 236), nc, dk * 0.6), w=3, r=3)
        c.rect(30, 446, 90, 556, mix((160, 70, 60), nc, dk), w=2.5)
        c.circle(78, 500, 4, (250, 210, 70), w=1.5)
        for x in (500, 535):
            D.flower(c, x, 556, mix((230, 80, 90), nc, dk), 1.0)
        return c.img
    return cached(("home", night), make)


SC_X = 860        # where the scooter stops


def tiago_rider(tl, t, **kw):
    def rider(c):
        tiago(c, tl, t, -56, -110, 0.85, 1, pose="sit", arm=kw.pop("arm", 0.5), **kw)
    return rider


def sidecar_cats(tl, t, whiskers=True, luna=True, sleep=False, flap=0.0, w_eyes="open", l_eyes="open",
                 look=(1, -0.2)):
    def side(c):
        if luna:
            kat(c, tl, t, "luna", 190, -66, 0.62, 1, "sit", eyes="closed" if sleep else l_eyes, look=look,
                head_dy=6 if sleep else 0)
        if whiskers:
            kat(c, tl, t, "whiskers", 110, -66, 0.62, 1, "sit", eyes="closed" if sleep else w_eyes, look=look,
                head_dy=8 if sleep else 0)
    return side


def sill(tl, t):
    T = tl.t
    c = Canvas(home_bg().copy())
    # ----- the scooter arrives, parks, and leaves
    if t >= T("s_scooter"):
        arr = ease(tl.prog("s_scooter", t, 0.0, 0.6))
        if t < T("s_go", 0.25):
            sx = lerp(1500, SC_X, arr)
        else:
            u = t - T("s_go", 0.25)
            sx = SC_X + 120 * u * u + 40 * u
        parked = T("s_scooter", 0.6) <= t < T("s_go", 0.1)
        in_car = t >= T("s_hop", 0.85)
        rider = None
        if not parked:
            rider = tiago_rider(tl, t, arm=0.5, eyes="happy" if t >= T("s_go") else "open")
        side = sidecar_cats(tl, t, l_eyes="happy", w_eyes="happy") if in_car else None
        P.scooter(c, sx, STREET_Y, 0.9, t, wheel_ang=-sx / 25, rider=rider, side=side,
                  bump=-abs(math.sin(t * 14)) * 2 if not parked else 0)
        if not parked and t < T("s_scooter", 0.6) or t >= T("s_go", 0.25):
            for k in range(3):
                pu = ((t * 2 + k / 3) % 1.0)
                c.circle(sx + 130 + 40 * pu, STREET_Y - 50 - 20 * pu, 8 + 14 * pu, mix((210, 210, 214), (240, 240, 244), pu),
                         ol=None)
    # ----- the grill on the pavement, and Tiago
    grill_on = T("s_scooter", 0.7) <= t < T("s_go", 0.1)
    gx = 720
    if grill_on:
        k = ease(tl.prog("s_scooter", t, 0.7, 0.85))
        taken = 1 if t >= T("s_eat", 0.25) else 0
        P.grill(c, gx, 600, 0.9 * k, t, n=5, taken=taken)
    if T("s_scooter", 0.6) <= t < T("s_go", 0.1):
        u = tl.prog("s_scooter", t, 0.6, 0.75)
        tx = lerp(SC_X - 40, 810, u)
        playing = T("s_fest", 0.6) <= t < T("s_come", 0.5)
        if playing:
            hold = lambda cc, px, py: None
            tiago(c, tl, t, tx, 604, 0.95, -1, pose="sit", arm=0.35, eyes="happy")
            P.guitar(c, tx - 20, 604 - 70, 0.8, ang=-0.5, t=t, strum=1.0)
            P.music_notes(c, tx - 40, 604 - 170, t, T("s_fest", 0.6), n=3, col=(255, 230, 150))
        else:
            toss = T("s_eat", 0.0) <= t < T("s_eat", 0.3)
            wave = T("s_tiago") <= t < T("s_tiago", 0.4) or T("s_hop") <= t < T("s_hop", 1)
            arm = 1.0 if wave else (0.75 if toss else 0.45)
            tiago(c, tl, t, tx, 604, 0.95, -1, pose="sit" if u >= 1 else "walk", walk=tx / 10, arm=arm,
                  eyes="happy" if (T("s_come", 1) <= t) else "open",
                  hold=(lambda cc, px, py: P.sardine(cc, px - 10, py - 4, 0.4, ang=0.3)) if t < T("s_eat", 0.1)
                  and t >= T("s_tiago", 0.6) else None)
    # sardine flying to Whiskers
    if T("s_eat", 0.05) <= t < T("s_eat", 0.35):
        u = tl.prog("s_eat", t, 0.05, 0.35)
        fx, fy = lerp(760, 520, u), lerp(470, 470, u) + arc(u, 120)
        P.sardine(c, fx, fy, 0.45, ang=u * 8)
    # ----- Whiskers
    wx = 360
    if t < T("s_yes", 0.6):
        if t < T("s_dream"):
            kat(c, tl, t, "whiskers", wx - 30, SILL, 0.9, 1, "sleep")
            if t >= T("s_open", 0.3):
                for k in range(2):
                    pass
        else:
            wide = t >= T("s_yes")
            kat(c, tl, t, "whiskers", wx, SILL, 0.9, 1, "sit",
                eyes="wide" if wide else ("closed" if t < T("s_look") else "open"), look=(1, 0),
                head_dy=-6 if wide else 0)
    elif t < T("s_eat", 0.35):
        u = tl.prog("s_yes", t, 0.6, 1.0) * 0.4 + tl.prog("s_eat", t, 0.0, 0.35) * 0.6
        x = lerp(wx, 520, u)
        kat(c, tl, t, "whiskers", x, lerp(SILL, 556, u) + arc(u, 90), 0.9, 1, "leap", eyes="happy")
    elif t < T("s_hop", 0.6):
        chew = 0.3 + 0.3 * math.sin(t * 13) if t < T("s_eat", 1) else 0
        kat(c, tl, t, "whiskers", 520, 556, 0.9, 1, "sit", mouth=chew if chew else tl.mouth("whiskers", t),
            eyes="happy" if chew or T("s_hop") <= t else "open", look=(1, 0))
        if chew:
            P.sardine(c, 548, 520, 0.4, ang=0.2, bite=tl.prog("s_eat", t, 0.4, 1.0))
    elif t < T("s_hop", 0.85):
        u = tl.prog("s_hop", t, 0.6, 0.85)
        kat(c, tl, t, "whiskers", lerp(520, SC_X - 20, u), lerp(556, STREET_Y - 40, u) + arc(u, 120), 0.75, 1,
            "leap")
    # ----- Luna
    lx = 230
    if t < T("s_eat", 0.5):
        excited = T("s_look") <= t < T("s_look", 1)
        kat(c, tl, t, "luna", lx, SILL, 0.9, 1, "sit" if t < T("s_look") else "stand",
            eyes="happy" if excited else "open", look=(1, -0.2))
    elif t < T("s_eat", 0.8):
        u = tl.prog("s_eat", t, 0.5, 0.8)
        kat(c, tl, t, "luna", lerp(lx, 440, u), lerp(SILL, 556, u) + arc(u, 90), 0.9, 1, "leap")
    elif t < T("s_hop", 0.65):
        kat(c, tl, t, "luna", 440, 556, 0.9, 1, "sit", eyes="happy" if T("s_come") <= t < T("s_come", 1) else "open",
            look=(1, -0.3))
    elif t < T("s_hop", 0.9):
        u = tl.prog("s_hop", t, 0.65, 0.9)
        kat(c, tl, t, "luna", lerp(440, SC_X + 60, u), lerp(556, STREET_Y - 40, u) + arc(u, 150), 0.75, 1, "leap")
    # ----- smell wisps from the grill / the scooter
    if t < T("s_look"):
        k = tl.prog("s_open", t, 0.1, 0.8)
        smell(c, 1280, 420, 420, SILL - 60, t, k)
    elif T("s_scooter", 0.8) <= t < T("s_eat"):
        smell(c, gx, 470, 420, SILL - 80, t, 1.0)
    # ----- Pip on the sill
    if t >= T("s_hop", 0.6):
        k = ease(tl.prog("s_hop", t, 0.6, 1.0))
        talk = T("s_pip") <= t < T("s_pip", 1)
        D.mouse(c, lerp(100, 300, k), SILL, 1.3, 1, t, walk=t * 12 if k < 1 else 0, mouth=tl.mouth("pip", t),
                hop=abs(math.sin(t * 8)) * 10 if (talk or t >= T("s_go")) else 0, proud=talk or t >= T("s_go"))
    return finish(c, tl, t)


# ====================================================================== ride

ROAD_Y = 650
V_RIDE = 330.0


def darken(img, k, col=(30, 34, 80)):
    """Night version of an RGBA layer."""
    a = np.asarray(img).astype(np.float32)
    rgb = a[..., :3] * (1 - k) + np.array(col, np.float32) * k
    out = np.concatenate([rgb, a[..., 3:]], axis=2).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def ride_layers(night):
    def make():
        tw = 2 * W
        # far hills: a white village with a castle, a windmill
        far = Image.new("RGBA", (tw * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(far, size=(tw, H))

        def hill(x):
            return 430 - 50 * math.sin(x * math.tau / tw * 2) - 20 * math.sin(x * math.tau / tw * 5 + 1)
        c.poly([(0, H)] + [(x, hill(x)) for x in range(0, tw + 40, 30)] + [(tw, H)], (176, 186, 130), ol=None)
        vx = 700
        for k in range(9):
            hx = vx + k * 34 - 150
            hy = hill(hx) + 6
            c.rect(hx, hy - 24 - (k % 3) * 6, hx + 30, hy + 10, (250, 248, 240), w=1.5)
            c.poly([(hx - 2, hy - 24 - (k % 3) * 6), (hx + 15, hy - 34 - (k % 3) * 6), (hx + 32, hy - 24 - (k % 3) * 6)],
                   P.TERRACOTTA, w=1.5)
        P.castle_wall(c, vx - 40, vx + 60, hill(vx) - 30, 30, towers=((vx - 20, 26, 20), (vx + 40, 26, 30)), seed=4)
        P.windmill(c, 1900, hill(1900) + 6, 0.5, t=0.0)
        P.windmill(c, 2200, hill(2200) + 6, 0.4, t=1.0)
        # middle: golden fields, cork oaks, sunflowers, a farmhouse
        mid = Image.new("RGBA", (tw * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(mid, size=(tw, H))

        def mh(x):
            return 500 - 18 * math.sin(x * math.tau / tw * 3) - 8 * math.sin(x * math.tau / tw * 7)
        c.poly([(0, H)] + [(x, mh(x)) for x in range(0, tw + 40, 30)] + [(tw, H)], (226, 196, 110), ol=None)
        for row in range(4):
            y = 520 + row * 22
            for x in range(0, tw, 26):
                c.line([(x + row * 8, y), (x + 12 + row * 8, y - 4)], (200, 166, 80), 2, cap=False)
        for x in (180, 620, 1010, 1500, 1890, 2380):
            P.cork_tree(c, x, mh(x) + 30, 0.7)
        for k in range(26):
            x = 1150 + k * 14
            y = mh(x) + 26 + (k % 2) * 6
            c.line([(x, y), (x, y - 30)], (80, 140, 60), 2.5)
            for j in range(8):
                a = j * math.tau / 8
                c.circle(x + math.cos(a) * 7, y - 34 + math.sin(a) * 7, 4, (250, 200, 40), ol=None)
            c.circle(x, y - 34, 4.5, (120, 80, 40), ol=None)
        fx = 340
        c.rect(fx, mh(fx) - 30, fx + 90, mh(fx) + 20, (250, 250, 246), w=2)
        c.rect(fx, mh(fx) - 30, fx + 90, mh(fx) - 22, (60, 110, 190), ol=None)
        c.poly([(fx - 6, mh(fx) - 30), (fx + 45, mh(fx) - 54), (fx + 96, mh(fx) - 30)], P.TERRACOTTA, w=2)
        c.rect(fx + 36, mh(fx) - 6, fx + 54, mh(fx) + 20, (60, 110, 190), w=1.5)
        c.rect(fx + 64, mh(fx) - 60, fx + 76, mh(fx) - 40, (250, 250, 246), w=1.5)
        if night:
            far = darken(far, 0.62)
            mid = darken(mid, 0.58)
        return far, mid
    return cached(("ride_layers", night), make)


def ride_sky(night):
    def make():
        if night:
            c = Canvas(D.gradient(W * SS, H * SS, [(0, (14, 18, 52)), (0.6, (40, 44, 100)), (1, (60, 56, 110))]))
            D.stars(c, 12, 140, W, 380)
            D.moon(c, 980, 110, 34, sky=(24, 28, 70))
        else:
            c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 172, 236)), (0.6, (206, 230, 250)), (1, (226, 238, 250))]))
            for x, y, sc in ((200, 110, 1.0), (640, 70, 0.7), (1060, 150, 0.9)):
                D.cloud(c, x, y, sc)
        return c.img
    return cached(("ride_sky", night), make)


def ride_frame(night, pos):
    c = Canvas(ride_sky(night).copy())
    far, mid = ride_layers(night)
    paste_scroll(c, far, pos * 0.12, tile_w=2 * W)
    paste_scroll(c, mid, pos * 0.4, tile_w=2 * W)
    nc = (30, 34, 80)
    dk = 0.6 if night else 0.0
    c.rect(0, ROAD_Y - 70, W, H, mix((120, 120, 128), nc, dk), ol=None)
    c.rect(0, ROAD_Y - 74, W, ROAD_Y - 66, mix((176, 170, 160), nc, dk), ol=None)
    for k in range(-1, 9):
        x = k * 180 - (pos % 180)
        c.rect(x, ROAD_Y + 26, x + 90, ROAD_Y + 32, mix((240, 236, 220), nc, dk), ol=None)
    for k in range(-1, 6):
        x = k * 300 - (pos * 0.9 % 300)
        c.rect(x, ROAD_Y - 110, x + 8, ROAD_Y - 70, mix((250, 250, 250), nc, dk), w=1.5)
        c.rect(x, ROAD_Y - 102, x + 8, ROAD_Y - 94, mix((230, 60, 50), nc, dk), ol=None)
    return c


def bridge_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (90, 110, 180)), (0.35, (240, 160, 160)), (0.55, (255, 206, 150)),
                                               (1, (255, 220, 170))]))
        c.glow(1000, 330, 170, 170, (255, 246, 200), (255, 206, 150), steps=9)
        c.circle(1000, 330, 46, (255, 240, 190), ol=None)
        D.cloud(c, 260, 140, 0.8, col=(255, 220, 220))
        D.cloud(c, 760, 90, 0.6, col=(255, 220, 220))
        # Lisbon on the far bank (right), Cristo Rei on the near-left hill
        c.tint = ((250, 200, 170), 0.35)
        hill = [(560, 470), (640, 400), (780, 360), (900, 330), (1010, 352), (1150, 330), (1290, 360), (1290, 470)]
        c.poly(hill, (226, 200, 180), ol=None)
        hy = lambda x: float(np.interp(x, [p[0] for p in hill], [p[1] for p in hill])) + 10
        P.castle_wall(c, 860, 980, 336, 30, towers=((880, 30, 24), (950, 34, 30)), seed=6)
        P.roofs(c, 560, 1290, 330, 480, seed=8, scale=0.7, top_fn=hy, row=30)
        c.tint = ((250, 190, 170), 0.3)
        c.poly([(-20, 480), (-20, 380), (80, 360), (200, 380), (260, 480)], (176, 150, 150), ol=None)
        P.cristo_rei(c, 100, 372, 0.9, col=(226, 210, 204))
        c.tint = None
        # river
        c.rect(0, 470, W, H, (120, 150, 200), ol=None)
        for k in range(40):
            x = (k * 173) % W
            y = 490 + (k * 41) % 220
            c.line([(x, y), (x + 50, y)], (230, 200, 200), 2, cap=False)
        c.ellipse(1000, 520, 90, 14, (255, 230, 190), ol=None)
        P.caravel(c, 520, 640, 0.6, bob=False)
        # the bridge itself
        P.bridge(c, -40, 1320, 420, (300, 1110), 30)
        return c.img
    return cached("bridge_bg", make)


def ride(tl, t):
    T = tl.t
    if t < T("r_wake"):
        t0 = tl.scenes["ride"][0]
        pos = V_RIDE * (t - t0)
        night_k = ease(tl.prog("r_night", t, 0.0, 0.3))
        if night_k <= 0:
            c = ride_frame(False, pos)
        elif night_k >= 1:
            c = ride_frame(True, pos)
        else:
            a, b = ride_frame(False, pos), ride_frame(True, pos)
            c = Canvas(Image.blend(a.img, b.img, night_k))
        night = night_k > 0.5
        c.tint = ((30, 34, 80), 0.35 * night_k) if night_k > 0 else None
        bump = 0.0
        for fr in (0.3, 0.7):
            bt = T("r_ride", fr)
            if bt <= t < bt + 0.45:
                bump = -12 * math.sin(math.pi * (t - bt) / 0.45)
        sleep = t >= T("r_night", 0.25)
        P.scooter(c, 520, ROAD_Y + 20, 1.0, t, wheel_ang=-pos / 24, bump=bump - abs(math.sin(t * 13)) * 1.5,
                  rider=tiago_rider(tl, t, arm=0.5, eyes="happy" if T("r_ride", 0.45) <= t < T("r_ride", 0.6) else "open"),
                  side=sidecar_cats(tl, t, sleep=sleep, w_eyes="happy" if t < T("r_ride", 0.5) else "open",
                                    l_eyes="happy"), lights=night)
        c.tint = None
        if sleep:
            D.zzz(c, 520 + 40 + 110, ROAD_Y + 20 - 26 - 130, t)
        else:
            for k in range(4):
                u = (t * 2.5 + k / 4) % 1.0
                yy = ROAD_Y - 120 - k * 16
                c.line([(820 - 500 * u, yy), (880 - 500 * u, yy)], (255, 255, 255), 2, cap=False)
        if T("r_ride", 0.5) <= t < T("r_ride", 0.5) + 0.8:
            c.text(700, ROAD_Y - 220, "beep beep!", 26, (255, 230, 120), stroke=3)
        # roadside grass tufts in front
        for k in range(-1, 6):
            x = k * 330 - (pos * 1.3 % 330)
            D.bush(c, x + 100, H + 26, 0.9, col=mix((90, 150, 80), (30, 34, 80), 0.6 * night_k))
        return finish(c, tl, t)
    # ---- crossing the big red bridge at sunrise
    c = Canvas(bridge_bg().copy())
    u = clamp((t - T("r_wake")) / (tl.scenes["ride"][1] - T("r_wake")))
    sx = lerp(-160, 1180, u)
    P.scooter(c, sx, 418, 0.42, t, wheel_ang=-sx / 10, bump=-abs(math.sin(t * 13)) * 0.8,
              rider=tiago_rider(tl, t, arm=0.5, eyes="happy"),
              side=sidecar_cats(tl, t, sleep=t < T("r_wake", 0.5), l_eyes="happy" if t >= T("r_luna") else "open",
                                look=(1, -0.6)))
    # the near tower legs pass in front of the scooter
    for tx in (300, 1110):
        for side in (-1,):
            c.rect(tx + side * 30 - 8, 30, tx + side * 30 + 8, 460, P.BRIDGE_RED, w=3)
    for k in range(3):
        gx = (t * 60 + k * 460) % (W + 200) - 100
        P.gull(c, gx, 520 + 40 * k, 0.6, 1, t, seed=k)
    return finish(c, tl, t)


# ===================================================================== belem

BW = 2300
PROM = 640


def belem_bg():
    def make():
        c = Canvas(D.gradient(BW * SS, H * SS, [(0, (110, 176, 238)), (0.55, (206, 230, 250)), (1, (220, 236, 250))]),
                   size=(BW, H))
        for x, y, sc in ((300, 90, 1.0), (900, 140, 0.8), (1500, 80, 1.1), (2100, 130, 0.7)):
            D.cloud(c, x, y, sc)
        # far bank + the bridge far upstream
        c.poly([(0, 450), (300, 430), (900, 440), (1500, 420), (2300, 436), (2300, 470), (0, 470)], (170, 180, 170),
               ol=None)
        P.bridge(c, 1650, 2300, 430, (1900, 2240), 330, far=True)
        P.cristo_rei(c, 2100, 430, 0.4, col=(220, 214, 206))
        # river
        c.rect(0, 460, BW, PROM - 40, (90, 150, 205), ol=None)
        for k in range(60):
            x = (k * 197) % BW
            y = 480 + (k * 53) % 110
            c.line([(x, y), (x + 50, y)], (190, 220, 245), 2, cap=False)
        # Belem Tower standing in the water
        P.belem_tower(c, 420, 590, 0.9)
        c.ellipse(420, 594, 200, 14, (70, 120, 180), ol=None)
        # Discoveries monument on the bank
        P.discoveries(c, 1500, PROM - 40, 1.05)
        # promenade: calcada with waves, a low wall with lamp posts
        c.rect(0, PROM - 46, BW, PROM - 30, (220, 210, 190), w=2)
        cobbles(c, 0, PROM - 30, BW, H, seed=9)
        for x in range(160, BW, 420):
            c.rect(x - 4, PROM - 190, x + 4, PROM - 30, (60, 70, 80), w=1.5)
            c.ellipse(x, PROM - 196, 14, 10, (250, 246, 220), w=2)
        return c.img
    return cached("belem_bg", make)


def shop_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 180, 236)), (1, (210, 232, 250))]))
        # the old pastry shop: tiled facade, blue awnings, a gold sign
        c.rect(-10, 40, 980, 560, (246, 240, 226), w=3)
        P.tile_pattern(c, -8, 42, 978, 120, style=1, size=26)
        c.rect(-10, 120, 980, 140, (250, 248, 240), w=2.5)
        c.text(485, 96, "PASTÉIS DE BELÉM", 38, (40, 70, 150), stroke=2, stroke_fill=(250, 250, 255))
        for k in range(4):
            x = 60 + k * 230
            c.rect(x, 230, x + 170, 520, (70, 90, 120), w=3)
            c.rect(x + 10, 240, x + 160, 510, (250, 220, 160), ol=None)
            # trays of tarts in the windows
            for j in range(3):
                c.rect(x + 18, 330 + j * 60, x + 152, 336 + j * 60, (180, 170, 160), ol=None)
                for i in range(5):
                    P.nata(c, x + 32 + i * 26, 330 + j * 60, 0.45)
            # blue striped awning
            pts = [(x - 16, 200), (x + 186, 200), (x + 200, 250), (x - 30, 250)]
            c.poly(pts, (50, 90, 170), w=2.5)
            for j in range(6):
                xa, xb = x - 16 + j * 34, x - 30 + j * 38
                c.poly([(xa, 200), (xa + 17, 200), (xb + 19, 250), (xb, 250)], (250, 250, 255), ol=None)
            c.line([(x - 30, 250), (x + 200, 250)], OUT, 2.5, cap=False)
        c.rect(980, 140, W + 10, 560, (240, 210, 150), w=3)
        P.window(c, 1080, 300, 44, 70, balcony=True)
        P.window(c, 1200, 300, 44, 70, balcony=True)
        # pavement
        cobbles(c, 0, 556, W, H, seed=11)
        c.line([(0, 556), (W, 556)], OUT, 2.5, cap=False)
        # tram stop sign
        c.rect(1060, 360, 1068, 600, (60, 60, 66), w=2)
        c.circle(1064, 350, 26, P.YELLOW, w=3)
        c.text(1064, 351, "28", 22, (40, 40, 46))
        return c.img
    return cached("shop_bg", make)


TABLE_X, TABLE_Y = 470, 600


def cafe_table(c, x, y):
    c.line([(x, y - 96), (x, y - 4)], (60, 60, 66), 6)
    c.ellipse(x, y - 2, 34, 6, (60, 60, 66), ol=None)
    c.ellipse(x, y - 100, 120, 14, (250, 250, 252), w=3)


def belem(tl, t):
    T = tl.t
    if t < T("b_nata"):
        u = tl.prog("b_narr", t, 0.0, 1.0) * 0.45 + tl.prog("b_look", t) * 0.55
        camx = lerp(W / 2, BW - W / 2 - 340, ease(u))
        c = cam(belem_bg(), camx, H / 2)
        # gulls, a caravel sailing past
        P.caravel(c, 900 + (t - T("b_narr")) * 25, 560, 0.5, t)
        for k in range(4):
            gx = 300 + k * 520 + 30 * math.sin(t * 0.7 + k)
            P.gull(c, gx, 180 + 50 * (k % 2) + 10 * math.sin(t + k), 0.6, 1 if k % 2 else -1, t, seed=k)
        # Tiago and the cats stroll along the promenade
        wx = camx - 120
        walk = wx / 10
        tiago(c, tl, t, wx + 150, PROM + 25, 0.85, 1, pose="walk", walk=walk, eyes="happy")
        kat(c, tl, t, "luna", wx, PROM + 25, 0.75, 1, "walk", walk=wx / 9, look=(0, -0.6))
        kat(c, tl, t, "whiskers", wx - 140, PROM + 25, 0.75, 1, "walk", walk=wx / 9)
        return finish(c, tl, t)
    # ---- outside the pastry shop
    c = Canvas(shop_bg().copy())
    cinn = T("b_sneeze", 0.5) <= t < T("b_ok", 0.4)
    shake = T("b_ok", 0.0) <= t < T("b_ok", 0.4)
    # Tiago
    leaving = t >= T("b_end")
    if not leaving:
        laugh = T("b_sneeze", 0.6) <= t < T("b_purpose")
        point = T("b_plan") <= t < T("b_plan", 1)
        tiago(c, tl, t, 860, 610, 1.0, -1, pose="sit", arm=1.0 if point else (0.5 if t < T("b_eat") else 0.3),
              eyes="happy" if laugh or t < T("b_eat") else "open",
              mouth=laughing(t) if laugh else tl.mouth("tiago", t))
        if point:
            c.text(1000, 260, "28", 30, (255, 220, 90), stroke=3) if False else None
    else:
        u = tl.prog("b_end", t)
        P.scooter(c, lerp(900, 1700, ease(u)), 690, 0.8, t, wheel_ang=-u * 40,
                  rider=tiago_rider(tl, t, arm=0.8, eyes="happy"), sidecar=True)
    # the table with the tarts
    cafe_table(c, TABLE_X, TABLE_Y)
    n0 = 12
    eat = clamp(tl.prog("b_eat", t) * 0.25 + tl.prog("b_gobble", t, 0.0, 0.85) * 0.75)
    left = n0 - int(round(eat * n0))
    if t >= T("b_nata", 0.15):
        pop = ease(tl.prog("b_nata", t, 0.15, 0.4))
        k = 0
        for row, cnt in enumerate((5, 4, 2, 1)):
            for i in range(cnt):
                if k < left:
                    P.nata(c, TABLE_X - (cnt - 1) * 22 + i * 44, TABLE_Y - 108 - row * 18 - 20 * (1 - pop), 0.8)
                k += 1
    # Whiskers on a chair at the table
    full = clamp(tl.prog("b_gobble", t, 0.3, 1.0))
    sneezing = T("b_sneeze", 0.0) <= t < T("b_sneeze", 0.6)
    eating = T("b_eat") <= t < T("b_gobble", 0.9)
    chew = 0.3 + 0.35 * math.sin(t * 16) if eating else 0.0
    wx = TABLE_X - 150
    c.rect(wx - 50, TABLE_Y - 64, wx + 50, TABLE_Y - 54, (120, 80, 50), w=2)
    c.line([(wx - 40, TABLE_Y - 54), (wx - 44, TABLE_Y)], (120, 80, 50), 4)
    c.line([(wx + 40, TABLE_Y - 54), (wx + 44, TABLE_Y)], (120, 80, 50), 4)
    if sneezing:
        u = tl.prog("b_sneeze", t, 0.0, 0.6)
        ach = u < 0.75
        kat(c, tl, t, "whiskers", wx, TABLE_Y - 62, 0.9, 1, "sit", eyes="closed",
            mouth=0.5 * u if ach else 1.0, head_dy=-10 * u if ach else 10, squash=1.0 + 0.03 * full)
    else:
        kat(c, tl, t, "whiskers", wx, TABLE_Y - 62, 0.9, 1, "sit",
            mouth=chew if eating else tl.mouth("whiskers", t),
            eyes="happy" if eating or T("b_purpose") <= t < T("b_purpose", 1) else "open",
            squash=1.0 - 0.12 * full, look=(1, 0))
    if eating:
        P.nata(c, wx + 52, TABLE_Y - 150, 0.6, bite=(t * 3) % 1)
    if T("b_gobble", 0.85) <= t < T("b_sneeze", 0.45):
        # a shake of cinnamon on top
        c.push(wx + 70, TABLE_Y - 190)
        c.rect(-10, -30, 10, 10, (240, 236, 226), w=2, r=4)
        c.rect(-10, -36, 10, -26, (160, 160, 170), w=2, r=2)
        c.pop()
        for k in range(8):
            u = (t * 2 + k / 8) % 1.0
            c.circle(wx + 70 + math.sin(k) * 10, TABLE_Y - 150 + 60 * u, 2, (150, 90, 50), ol=None)
    # Luna, next to the table (turns cinnamon-brown in the sneeze)
    lx = TABLE_X + 140
    if t < T("b_ok", 0.6) or True:
        pal = CINNAMON if cinn else None
        if shake:
            u = tl.prog("b_ok", t, 0.0, 0.4)
            kat(c, tl, t, "luna", lx + 6 * math.sin(t * 40), TABLE_Y, 0.9, -1, "stand", pal=pal if u < 0.5 else None,
                eyes="closed")
            P.cinnamon_cloud(c, lx, TABLE_Y - 60, u, t)
        else:
            walk_off = tl.prog("b_ok", t, 0.6, 1.0) + tl.prog("b_end", t)
            x = lerp(lx, 1300, ease(walk_off * 0.5))
            annoyed = T("b_sneeze", 0.6) <= t < T("b_go")
            kat(c, tl, t, "luna", x, TABLE_Y, 0.9, -1 if walk_off <= 0 else 1, "stand" if walk_off <= 0 else "walk",
                walk=x / 10, pal=pal, eyes="closed" if annoyed else "open", look=(-1, 0))
    if T("b_sneeze", 0.45) <= t < T("b_sneeze", 0.9):
        u = tl.prog("b_sneeze", t, 0.45, 0.9)
        P.cinnamon_cloud(c, lerp(wx + 80, lx, u), TABLE_Y - 140 + 40 * u, u, t)
        c.text(wx + 40, TABLE_Y - 260, "AH-CHOO!", 40, (255, 240, 200), stroke=4, stroke_fill=(120, 60, 30))
    if leaving:
        u = tl.prog("b_end", t)
        x = lerp(wx, 1300, ease(u))
        kat(c, tl, t, "whiskers", x, TABLE_Y, 0.9, 1, "walk", walk=x / 10, squash=0.9)
    return finish(c, tl, t)


# ====================================================================== tram

def street_line(x):
    """The steep street of the climb (world coords): rises to the right."""
    return 1300 - 0.25 * x


SW_, SH_ = 2600, 1400
SLOPE_DEG = math.degrees(math.atan(0.25))


def steep_bg():
    def make():
        c = Canvas(D.gradient(SW_ * SS, SH_ * SS, [(0, (100, 166, 236)), (0.5, (200, 228, 250)), (1, (220, 236, 250))]),
                   size=(SW_, SH_))
        for x, y, sc in ((300, 200, 1.2), (1100, 120, 0.9), (1900, 240, 1.1), (2400, 100, 0.8)):
            D.cloud(c, x, y, sc)
        # houses stepping up the hill
        rng = np.random.default_rng(21)
        x = -40
        k = 0
        walls = [(250, 214, 120), (240, 170, 160), (250, 246, 236), (170, 210, 220), (250, 200, 140)]
        tops = []
        while x < SW_ + 40:
            w = rng.uniform(170, 240)
            base = street_line(x + w) - 30
            h = rng.uniform(420, 560)
            tiles = None
            if k % 3 == 1:
                tiles = (P.TILE_BLUE, k % 2, 20)
            elif k % 5 == 3:
                tiles = ((40, 130, 110), 2, 20)
            P.house(c, x, base + 160, w, h + 160, walls[k % len(walls)], tiles=tiles, seed=k, door=False)
            tops.append((x, x + w, base + 160 - h - 160))
            x += w
            k += 1
        # laundry lines between neighbouring windows
        for j, (a0, a1, top) in enumerate(tops[:-1]):
            if j % 2 == 0:
                y0 = top + 150
                P.laundry(c, a1 - 60, y0, a1 + 80, y0 - 30, seed=j, n=3)
        # the street: cobbles, rails
        pts = [(0, street_line(0) - 34), (SW_, street_line(SW_) - 34), (SW_, SH_), (0, SH_)]
        c.poly(pts, (190, 184, 176), ol=None)
        for k2 in range(0, SW_, 26):
            for j in range(6):
                yy = street_line(k2) - 30 + j * 26
                c.arc(k2 + (j % 2) * 13, yy, 12, 6, 200, 340, (160, 154, 146), 2)
        for off in (0, 18):
            c.line([(0, street_line(0) + off), (SW_, street_line(SW_) + off)], (110, 110, 120), 4, cap=False)
        c.line([(0, street_line(0) - 34), (SW_, street_line(SW_) - 34)], OUT, 2.5, cap=False)
        # tram wire
        c.line([(0, street_line(0) - 420), (SW_, street_line(SW_) - 420)], (60, 60, 70), 2, cap=False)
        # a low wall + railing along the downhill side, with a view gap
        return c.img
    return cached("steep_bg", make)


def tram_climb_pos(tl, t):
    u = tl.prog("tr_narr", t) * 0.3 + tl.prog("tr_climb", t) * 0.7
    return lerp(250, 2250, u)


def alfama_strip():
    """Tiled facades seen through the tram windows (2 W wide tile, scrolls)."""
    def make():
        tw = 2 * W
        img = Image.new("RGB", (tw * SS, H * SS), (230, 220, 200))
        c = Canvas(img, size=(tw, H))
        c.rect(0, 0, tw, H, (130, 180, 230), ol=None)
        walls = [(250, 214, 120), (240, 170, 160), (250, 246, 236), (170, 210, 220), (250, 200, 140), (230, 240, 236)]
        x = 0
        k = 0
        while x < tw:
            w = 260 if k % 2 else 300
            if x + w > tw:
                w = tw - x
            tiles = (P.TILE_BLUE, k % 3, 30) if k % 2 == 0 else None
            P.house(c, x, H + 40, w, H + 10, walls[k % len(walls)], tiles=tiles, seed=k + 40, door=False)
            x += w
            k += 1
        for j in range(4):
            P.laundry(c, 200 + j * 640, 120, 420 + j * 640, 150, seed=j + 3, n=4)
        return img
    return cached("alfama_strip", make)


def stop_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 170, 236)), (1, (214, 234, 250))]))
        # castle walls high above
        P.castle_wall(c, 520, 1290, 260, 80, towers=((640, 90, 70), (900, 100, 90), (1180, 90, 60)), seed=12)
        P.cross_flag(c, 900, 100, 0.8)
        c.poly([(480, 300), (520, 200), (1290, 200), (1290, 330)], (150, 160, 110), ol=None)
        c.poly([(400, 340), (520, 260), (1290, 260), (1290, 380)], (130, 150, 100), ol=None)
        for x in (560, 760, 1060, 1240):
            D.tree(c, x, 380, 0.7, leaf=(100, 150, 80))
        # houses on the left
        P.house(c, -20, 590, 220, 520, (250, 214, 120), tiles=(P.TILE_BLUE, 0, 22), seed=3, door=True)
        P.house(c, 200, 590, 200, 470, (240, 170, 160), seed=4, door=True)
        P.house(c, 400, 590, 180, 330, (250, 246, 236), tiles=((40, 130, 110), 2, 20), seed=5, door=True)
        # street, rails
        cobbles(c, 0, 586, W, H, seed=13)
        for yy in (650, 668):
            c.line([(0, yy), (W, yy)], (110, 110, 120), 4, cap=False)
        c.line([(0, 586), (W, 586)], OUT, 2.5, cap=False)
        c.line([(0, 250), (W, 240)], (60, 60, 70), 2, cap=False)
        # stop sign
        c.rect(860, 400, 868, 640, (60, 60, 66), w=2)
        c.rect(800, 360, 930, 410, P.YELLOW, w=3, r=6)
        c.text(865, 386, "Castelo 28", 20, (40, 40, 46))
        return c.img
    return cached("stop_bg", make)


def tram(tl, t):
    T = tl.t
    if t < T("tr_look"):
        bg = steep_bg()
        x = tram_climb_pos(tl, t)
        y = street_line(x) + 10
        c = cam(bg, x + 60, y - 200)
        sway = math.sin(t * 5) * 0.6
        inside = tram_cats(tl, t, whiskers_eyes="happy" if t < T("tr_climb", 0.5) else "closed",
                           luna_eyes="happy", luna_look=(1, -0.5))
        P.rotated(c, lambda cc: P.tram(cc, 0, 0, 1.0, t, inside=inside, wheel_ang=x / 18), x, y,
                  SLOPE_DEG + sway, box=(-260, -360, 260, 30))
        for k in range(2):
            gx = x - 500 + ((t * 70 + k * 600) % 1200)
            P.gull(c, gx, y - 520 - 40 * k, 0.6, 1, t, seed=k)
        return finish(c, tl, t)
    if t < T("tr_stop"):
        # inside view: the tram's windows up close, Alfama sliding past
        t0 = T("tr_look")
        off = (t - t0) * 160
        c = Canvas(Image.new("RGB", (W * SS, H * SS)))
        strip = alfama_strip()
        tw = 2 * W * SS
        o = int(off * SS) % tw
        piece = strip.crop((o, 0, min(tw, o + W * SS), H * SS))
        c.img.paste(piece, (0, 0))
        if o + W * SS > tw:
            c.img.paste(strip.crop((0, 0, o + W * SS - tw, H * SS)), (tw - o, 0))
        sway = math.sin(t * 4) * 3
        look = T("tr_look") <= t < T("tr_look", 1)
        inside = tram_cats(tl, t, whiskers_sleep=t >= T("tr_zzz", 0.85), luna_look=(1, -0.6) if look else (-1, 0),
                           luna_eyes="happy" if look else "open", whiskers_eyes="closed", s=0.75)
        P.tram(c, 660, 1010 + sway, 3.0, t, inside=inside, pole=False)
        if t >= T("tr_zzz", 0.85):
            D.zzz(c, 660 + 3.0 * 75, 1010 - 3.0 * 175 + sway, t)
        return finish(c, tl, t)
    # ---- the castle stop: Luna hops off, the tram rolls on with Whiskers asleep
    c = Canvas(stop_bg().copy())
    go = T("tr_hop", 0.6)
    if t < go:
        tx = 520
    else:
        u = t - go
        tx = 520 + 40 * u * u + 30 * u
    P.tram(c, tx, 660, 1.2, t, wheel_ang=tx / 20,
           inside=tram_cats(tl, t, luna=t < T("tr_stop", 0.7), whiskers_sleep=True,
                            luna_look=(-1, 0.3), luna_eyes="open"))
    if t >= T("tr_stop", 0.1) and tx < 1500:
        D.zzz(c, tx + 1.2 * 50, 660 - 1.2 * 170, t)
    # Luna
    if t < T("tr_stop", 0.7):
        pass
    elif t < T("tr_hop", 0.15):
        u = tl.prog("tr_stop", t, 0.7, 1.0) * 0.6 + tl.prog("tr_hop", t, 0, 0.15) * 0.4
        kat(c, tl, t, "luna", lerp(470, 380, u), lerp(560, 690, u) + arc(u, 80), 0.8, -1, "leap")
    elif t < T("tr_wait"):
        worried = t >= go
        kat(c, tl, t, "luna", 380, 690, 0.8, 1, "stand" if not worried else "stand",
            eyes="wide" if worried else "happy", look=(1, -0.3))
    else:
        u = tl.prog("tr_wait", t, 0.0, 1.0) * 0.6 + tl.prog("tr_gone", t, 0.0, 0.5) * 0.4
        x = lerp(380, 1000, ease(u))
        if u < 1:
            kat(c, tl, t, "luna", x, 690, 0.8, 1, "walk", walk=x / 7, eyes="wide")
        else:
            kat(c, tl, t, "luna", 1000, 690, 0.8, 1, "sit", eyes="closed" if t > T("tr_gone", 0.8) else "open",
                head_dy=8, tail=0.0)
    return finish(c, tl, t)


# ==================================================================== castle

WALK_Y = 600
DUSK = ((120, 60, 110), 0.35)


def castle_bg(dusk=False):
    def make():
        if dusk:
            sky = [(0, (60, 50, 120)), (0.5, (220, 120, 130)), (0.8, (255, 180, 120)), (1, (255, 200, 140))]
        else:
            sky = [(0, (100, 166, 236)), (0.7, (206, 230, 250)), (1, (220, 236, 250))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        if not dusk:
            D.cloud(c, 300, 110, 1.0)
            D.cloud(c, 980, 80, 0.8)
        else:
            c.glow(1100, 470, 160, 160, (255, 230, 170), (255, 190, 130), steps=8)
        c.tint = ((90, 50, 100), 0.3) if dusk else None
        # inner towers and keep
        P.castle_wall(c, -20, 1300, 470, 120, towers=((150, 150, 180), (620, 170, 230), (1120, 150, 160)), seed=14)
        P.cross_flag(c, 620, 70, 1.0)
        for k in range(3):
            c.rect(560 + k * 50, 200, 580 + k * 50, 240, (90, 70, 60), ol=None)
        # umbrella pines and olive trees
        for x, sc in ((330, 1.0), (900, 0.9)):
            c.rect(x - 8, 380, x + 8, 520, (120, 80, 60), w=2)
            c.ellipse(x, 370, 120 * sc, 46 * sc, (80, 130, 70))
            c.ellipse(x - 10, 360, 100 * sc, 34 * sc, (100, 150, 80), ol=None)
        # the courtyard
        c.rect(0, 470, W, 560, (196, 176, 140), ol=None)
        c.line([(0, 470), (W, 470)], OUT, 2.5, cap=False)
        # the near walkway on the wall, with battlements in front
        c.rect(0, 560, W, H, (214, 190, 150), w=3)
        rng = np.random.default_rng(3)
        for _ in range(60):
            x, y = rng.uniform(0, W), rng.uniform(570, 710)
            c.rect(x, y, x + 40, y + 16, (190, 166, 128), ol=None)
        c.tint = None
        return c.img
    return cached(("castle_bg", dusk), make)


def view_bg():
    """From the castle wall: red roofs tumbling down to the river and the bridge."""
    def make():
        VW = 1700
        c = Canvas(D.gradient(VW * SS, H * SS, [(0, (110, 170, 236)), (0.5, (206, 230, 250)), (1, (220, 236, 250))]),
                   size=(VW, H))
        D.cloud(c, 300, 90, 0.9)
        D.cloud(c, 1200, 120, 0.8)
        c.poly([(0, 300), (500, 290), (1100, 280), (1700, 296), (1700, 330), (0, 330)], (176, 186, 176), ol=None)
        P.bridge(c, 900, 1700, 300, (1150, 1560), 200, far=True)
        P.cristo_rei(c, 1640, 300, 0.4, col=(220, 214, 206))
        c.rect(0, 320, VW, 420, (100, 156, 210), ol=None)
        for k in range(40):
            x = (k * 211) % VW
            y = 330 + (k * 37) % 80
            c.line([(x, y), (x + 40, y)], (190, 220, 245), 2, cap=False)
        P.caravel(c, 700, 400, 0.4, bob=False)
        P.roofs(c, -20, VW + 20, 400, 700, seed=31, scale=1.3, row=34)
        # Sao Vicente's white towers + the Pantheon dome
        c.push(1100, 470, 0.8)
        c.ellipse(0, -84, 50, 46, (250, 248, 240), w=2.5)
        c.rect(-60, -84, 60, 20, (250, 248, 240), w=2.5)
        c.rect(-6, -150, 6, -126, (250, 248, 240), w=2)
        c.pop()
        c.push(420, 480, 0.8)
        for sx in (-1, 1):
            c.rect(sx * 70 - 20, -150, sx * 70 + 20, 0, (250, 248, 240), w=2.5)
            c.poly([(sx * 70 - 22, -150), (sx * 70, -180), (sx * 70 + 22, -150)], (250, 248, 240), w=2.5)
        c.rect(-50, -100, 50, 0, (250, 248, 240), w=2.5)
        c.pop()
        # the castle wall in front
        c.rect(0, 610, VW, H, (214, 190, 150), w=3)
        P.battlements(c, 0, VW, 610, 26, 34, 22, (214, 190, 150))
        return c.img
    return cached("view_bg", make)


def castle(tl, t):
    T = tl.t
    if t < T("c_view"):
        c = Canvas(castle_bg().copy())
        # a peahen pecking in the courtyard
        P.peacock(c, 1000, 540, 0.45, -1, t, bow=0.5 + 0.5 * math.sin(t * 2), seed=7)
        if t < T("c_pavao"):
            u = tl.prog("c_narr", t) * 0.3 + tl.prog("c_search", t) * 0.7
            keys = [(T("c_narr"), 200), (T("c_narr", 0.8), 640), (T("c_search", 0.3), 640), (T("c_search", 0.8), 380)]
            x = actor(c, tl, t, "luna", keys, WALK_Y + 40, 0.9, 1, look=(0, -0.3))
            if T("c_search", 0.3) <= t < T("c_search", 0.5):
                c.text(x + 40, WALK_Y - 140, "Whiskers?", 26, (255, 255, 255), stroke=3)
            pk = ease(tl.prog("c_search", t, 0.5, 1.0))
            pavao(c, tl, t, lerp(1400, 820, pk), WALK_Y + 40, 1.0, -1, walk=t * 6 if 0 < pk < 1 else 0)
            return finish(c, tl, t)
        fan = ease(tl.prog("c_pavao", t, 0.0, 0.3)) * (1 - ease(tl.prog("c_look", t, 0.7, 1.0)))
        pavao(c, tl, t, 820, WALK_Y + 40, 1.0, -1, fan=fan, eyes="happy" if t >= T("c_look") else "open")
        sad = T("c_lost") <= t < T("c_lost", 1)
        kat(c, tl, t, "luna", 470, WALK_Y + 40, 0.9, 1, "sit", eyes="open" if not sad else "open",
            head_dy=8 if sad else 0, look=(1, -0.6 if fan > 0.5 else 0))
        if T("c_lost", 0.2) <= t < T("c_lost", 1):
            k = ease(tl.prog("c_lost", t, 0.2, 0.4))
            bubble(c, 330, 330, 80, 60, k, tail=(470, WALK_Y - 110))
            if k > 0.9:
                kat(c, tl, t, "whiskers", 320, 380, 0.45, 1, "sit", mouth=0, eyes="happy")
        return finish(c, tl, t)
    # the view over the red roofs
    bg = view_bg()
    u = tl.prog("c_view", t)
    z = 1.0 + 0.5 * ease(tl.prog("c_miss", t, 0.0, 1.0) * 0.6 + tl.prog("c_end", t) * 0.4)
    camx = lerp(W / 2, 1700 - W / 2, ease(u)) if t < T("c_miss") else 1700 - W / 2
    if z > 1.0:
        camx = lerp(1700 - W / 2, 1200, (z - 1) / 0.5)
    c = cam(bg, camx, H / 2 + (z - 1) * 260, z)
    # a tiny tram far below
    tx = 200 + ((t - T("c_view")) * 50) % 1400
    P.tram(c, tx, 560, 0.14, t, pole=False)
    for k in range(3):
        gx = 200 + ((t * 50 + k * 500) % 1500)
        P.gull(c, gx, 250 + 40 * k, 0.5, 1, t, seed=k)
    sad = t >= T("c_miss")
    kat(c, tl, t, "luna", 1180, 616, 0.8, 1, "sit", look=(1, 0.4), eyes="closed" if T("c_miss", 0.6) <= t else "open",
        head_dy=10 if sad else 0, tail=0.0 if sad else None)
    pavao(c, tl, t, 1360, 616, 0.8, -1, look=(0, 0))
    return finish(c, tl, t)


# ====================================================================== lost

def estrela(c, x, y, s=1.0):
    """The white Estrela basilica: a big dome between two bell towers."""
    c.push(x, y, s)
    st = (246, 242, 230)
    c.rect(-200, -200, 200, 0, st, w=3)
    for k in range(5):
        c.rect(-150 + k * 70, -180, -130 + k * 70, 0, mix(st, OUT, 0.08), w=2)
    c.poly([(-120, -200), (0, -250), (120, -200)], st, w=3)
    c.rect(-70, -330, 70, -240, st, w=3)
    c.ellipse(0, -340, 80, 80, (220, 220, 214), w=3)
    c.rect(-80, -340, 80, -250, st, ol=None)
    c.line([(-80, -340), (80, -340)], OUT, 3, cap=False)
    c.rect(-12, -450, 12, -410, st, w=2)
    c.circle(0, -456, 8, (220, 190, 90), w=2)
    for sx in (-1, 1):
        c.rect(sx * 170 - 30, -330, sx * 170 + 30, -200, st, w=3)
        c.rect(sx * 170 - 12, -300, sx * 170 + 12, -260, (90, 80, 70), w=2, r=8)
        c.ellipse(sx * 170, -340, 34, 30, (220, 220, 214), w=2.5)
        c.rect(sx * 170 - 34, -340, sx * 170 + 34, -330, st, ol=None)
        c.rect(sx * 170 - 5, -390, sx * 170 + 5, -366, st, w=2)
    c.pop()


def terminus_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 170, 236)), (1, (226, 236, 246))]))
        D.cloud(c, 200, 110, 0.8)
        estrela(c, 820, 586, 1.0)
        for x in (360, 1220):
            c.ellipse(x, 380, 30, 160, (60, 110, 70))
            c.rect(x - 5, 520, x + 5, 590, (110, 80, 60), w=2)
        D.tree(c, 120, 590, 0.9, leaf=(100, 160, 80))
        cobbles(c, 0, 586, W, H, seed=17)
        for yy in (650, 668):
            c.line([(0, yy), (W, yy)], (110, 110, 120), 4, cap=False)
        c.line([(0, 586), (W, 586)], OUT, 2.5, cap=False)
        c.rect(1060, 420, 1068, 640, (60, 60, 66), w=2)
        c.rect(990, 380, 1140, 428, P.YELLOW, w=3, r=6)
        c.text(1065, 404, "End of line", 20, (40, 40, 46))
        return c.img
    return cached("terminus_bg", make)


def stair_y(x):
    """Stepped alley rising to the right: step tread height at x."""
    k = int(max(0, x - 120) // 60)
    return 690 - min(k, 15) * 22


def stairs_bg(dusk=False):
    def make():
        if dusk:
            sky = [(0, (50, 40, 100)), (0.6, (210, 110, 120)), (1, (255, 180, 120))]
        else:
            sky = [(0, (110, 170, 236)), (1, (214, 234, 250))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        c.tint = ((80, 40, 90), 0.35) if dusk else None
        walls = [(250, 214, 120), (240, 170, 160), (250, 246, 236), (170, 210, 220), (250, 200, 140)]
        x = -30
        k = 0
        while x < W + 30:
            w = 190 + (k * 37) % 80
            tiles = (P.TILE_BLUE, k % 3, 20) if k % 2 == 0 else None
            P.house(c, x, 700, w, 640 - 10 * k, walls[k % 5], tiles=tiles, seed=60 + k, door=False, lit=dusk)
            x += w
            k += 1
        for j in range(3):
            P.laundry(c, 100 + j * 420, 150 + 20 * j, 300 + j * 420, 170 + 20 * j, seed=j + 7, n=4)
        # the steps
        for k in range(17):
            x0 = 120 + k * 60 if k else -20
            y = 690 - min(k, 15) * 22
            c.rect(x0, y, W + 20, H + 10, (206, 196, 180), w=2.5)
            c.line([(x0, y + 4), (W + 20, y + 4)], (236, 228, 214), 3, cap=False)
        # lamp
        c.rect(1000, 250, 1008, stair_y(1004), (50, 50, 60), w=2)
        c.rect(986, 220, 1022, 254, (255, 230, 150) if dusk else (230, 230, 210), w=2.5, r=4)
        if dusk:
            P.garland(c, -20, 120, 700, 160, sag=50, seed=2)
            P.garland(c, 500, 200, 1300, 150, sag=60, seed=4)
        c.tint = None
        return c.img
    return cached(("stairs_bg", dusk), make)


LIFT_BASE = 1240
LIFT_S = 1.45


def lift_bg():
    def make():
        LW_, LH_ = W, 1300
        c = Canvas(D.gradient(LW_ * SS, LH_ * SS, [(0, (100, 160, 236)), (0.5, (206, 230, 250)), (1, (226, 236, 246))]),
                   size=(LW_, LH_))
        D.cloud(c, 200, 150, 1.0)
        D.cloud(c, 1100, 260, 0.8)
        # the castle on its hill, far to the right
        c.poly([(700, 560), (880, 430), (1040, 400), (1300, 440), (1300, 600)], (190, 196, 160), ol=None)
        P.castle_wall(c, 900, 1240, 420, 50, towers=((960, 50, 50), (1100, 60, 70), (1210, 40, 30)), seed=21)
        P.cross_flag(c, 1100, 302, 0.6)
        c.poly([(-20, 640), (300, 600), (600, 540), (900, 470), (1300, 470), (1300, LIFT_BASE), (-20, LIFT_BASE)],
               (214, 200, 180), ol=None)
        hy = lambda x: float(np.interp(x, [-20, 300, 600, 900, 1300], [640, 600, 540, 470, 470])) + 6
        P.roofs(c, -20, 1300, 460, 800, seed=22, scale=0.8, row=28, top_fn=hy)
        # Baixa: neat grid of pastel buildings below
        cols = [(250, 214, 120), (240, 200, 180), (250, 246, 236), (200, 220, 230)]
        for k in range(8):
            x = -20 + k * 170
            if 420 < x < 760:
                continue
            P.house(c, x, LIFT_BASE + 20, 170, 520, cols[k % 4], seed=80 + k, door=True)
        cobbles(c, 0, LIFT_BASE, LW_, LH_, seed=23)
        return c.img
    return cached("lift_bg", make)


def lost(tl, t):
    T = tl.t
    if t < T("l_wander"):
        c = Canvas(terminus_bg().copy())
        P.tram(c, 560, 660, 1.2, t, inside=None)
        if t < T("l_narr", 0.5):
            # still asleep inside
            c2 = c
            kat(c2, tl, t, "whiskers", 560 + 1.2 * 53, 660 - 1.2 * 122, 0.84, 1, "sleep") if False else None
            D.zzz(c, 630, 420, t)
        else:
            u = tl.prog("l_narr", t, 0.5, 1.0)
            x = lerp(760, 900, u)
            kat(c, tl, t, "whiskers", x, lerp(560, 690, u) + arc(u, 60), 0.85, 1, "leap" if u < 1 else "stand",
                eyes="open")
            if u >= 1:
                pass
        if t >= T("l_narr", 1):
            look = -1 if (t * 1.3) % 2 < 1 else 1
            kat(c, tl, t, "whiskers", 900, 690, 0.85, look, "stand", eyes="wide")
        return finish(c, tl, t)
    if t < T("l_lift"):
        c = Canvas(stairs_bg().copy())
        u = tl.prog("l_wander", t) * 0.7 + tl.prog("l_streets", t) * 0.3
        # up the steps, then back down again
        x = lerp(80, 1050, u / 0.6) if u < 0.6 else lerp(1050, 600, (u - 0.6) / 0.4)
        face = 1 if u < 0.6 else -1
        moving = 0.0 < u < 1.0
        kat(c, tl, t, "whiskers", x, stair_y(x + 20), 0.8, face, "walk" if moving else "stand", walk=x / 9,
            eyes="wide" if t >= T("l_streets") else "open")
        P.gull(c, 1004, 216, 0.8, -1, t, fly=False)
        return finish(c, tl, t)
    if t < T("l_dusk"):
        bg = lift_bg()
        u = ease(tl.prog("l_lift", t, 0.05, 0.85))
        top = LIFT_BASE - 560 * LIFT_S
        cy = lerp(LIFT_BASE - 200, 360, u)
        c = cam(bg, W / 2, cy)
        cab_u = u

        def inside(cc, cx, cyy):
            kat(cc, tl, t, "whiskers", cx - 8, cyy, 0.38, 1, "sit", eyes="wide" if cab_u > 0.9 else "open",
                look=(1, -0.4))

        if t < T("l_castle", 0.2):
            P.santa_justa(c, 520, LIFT_BASE, LIFT_S, cabin_y=cab_u, inside=inside)
        else:
            P.santa_justa(c, 520, LIFT_BASE, LIFT_S, cabin_y=1.0)
            # out on the top walkway, pointing at the castle
            k = ease(tl.prog("l_castle", t, 0.2, 0.5))
            kat(c, tl, t, "whiskers", lerp(560, 720, k), top - 20 * LIFT_S, 0.6, 1, "stand", walk=k * 20,
                eyes="happy" if t > T("l_castle", 0.5) else "open", look=(1, -0.3))
        return finish(c, tl, t)
    # sunset: running through the Alfama, nose first
    t0 = T("l_dusk")
    off = (t - t0) * 260
    c = Canvas(Image.new("RGB", (W * SS, H * SS)))
    strip = dusk_strip()
    tw = 2 * W * SS
    o = int(off * SS) % tw
    c.img.paste(strip.crop((o, 0, min(tw, o + W * SS), H * SS)), (0, 0))
    if o + W * SS > tw:
        c.img.paste(strip.crop((0, 0, o + W * SS - tw, H * SS)), (tw - o, 0))
    cobbles(c, 0, 600, W, H, seed=5, light=(200, 180, 170), dark=(70, 50, 60), waves=False)
    for k in range(3):
        gx = (k * 520 - off * 1.0) % (W + 400) - 200
        P.garland(c, gx - 200, 80, gx + 300, 90, t, sag=50, seed=k, glow=True)
    for k in range(2):
        gx = (k * 700 + 300 - off) % (W + 600) - 300
        P.grill(c, gx, 640, 0.7, t, n=4)
    sniff = tl.prog("l_dusk", t, 0.7, 1.0) > 0
    kat(c, tl, t, "whiskers", 560, 660, 0.9, 1, "walk", walk=t * 14, eyes="closed" if sniff else "open",
        look=(1, -0.2), head_dy=-6 if sniff else 0)
    smell(c, 1280, 470, 680, 560, t, 1.0)
    return finish(c, tl, t)


def dusk_strip():
    def make():
        img = alfama_strip().copy()
        a = np.asarray(img).astype(np.float32)
        a = a * 0.6 + np.array((150, 70, 90), np.float32) * 0.4
        return Image.fromarray(a.astype(np.uint8), "RGB")
    return cached("dusk_strip", make)


# ==================================================================== alfama

AVO_HOUSE_Y = 600


def avo_bg(night=False):
    def make():
        if night:
            sky = [(0, (20, 20, 60)), (0.6, (50, 40, 100)), (1, (80, 50, 110))]
        else:
            sky = [(0, (60, 50, 120)), (0.55, (220, 120, 130)), (1, (255, 180, 120))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        if night:
            D.stars(c, 33, 50, W, 160)
        c.tint = ((60, 40, 90), 0.25 if not night else 0.4)
        # Avo's house: all blue tiles
        P.house(c, 120, AVO_HOUSE_Y, 520, 560, (240, 244, 250), tiles=(P.TILE_BLUE, 0, 24), seed=91, door=False,
                lit=True)
        c.tint = ((60, 40, 90), 0.25 if not night else 0.4)
        c.rect(330, AVO_HOUSE_Y - 110, 430, AVO_HOUSE_Y, (40, 80, 150), w=3, r=6)
        c.arc(380, AVO_HOUSE_Y - 110, 50, 30, 180, 360, OUT, 3)
        c.circle(410, AVO_HOUSE_Y - 54, 4, (240, 210, 90), ol=None)
        P.house(c, -100, AVO_HOUSE_Y, 220, 480, (250, 200, 140), seed=92, door=False, lit=True)
        P.house(c, 640, AVO_HOUSE_Y, 260, 520, (240, 170, 160), seed=93, door=True, lit=True)
        P.house(c, 900, AVO_HOUSE_Y, 400, 420, (250, 230, 170), tiles=((40, 130, 110), 2, 20), seed=94, door=True,
                lit=True)
        # flower pots
        for x in (150, 300, 470, 600):
            c.rect(x - 14, AVO_HOUSE_Y - 26, x + 14, AVO_HOUSE_Y, (200, 100, 60), w=2)
            for j in range(3):
                c.circle(x - 8 + j * 8, AVO_HOUSE_Y - 34, 7, (230, 70, 90), w=1.5)
        c.tint = None
        cobbles(c, 0, AVO_HOUSE_Y, W, H, seed=25, light=(214, 200, 196), dark=(80, 60, 70))
        c.line([(0, AVO_HOUSE_Y), (W, AVO_HOUSE_Y)], OUT, 2.5, cap=False)
        P.garland(c, -20, 60, 700, 90, sag=60, seed=1, glow=night)
        P.garland(c, 600, 100, 1300, 70, sag=50, seed=3, glow=night)
        if night:
            P.garland(c, -20, 190, 1300, 200, sag=80, seed=5, glow=True)
        return c.img
    return cached(("avo_bg", night), make)


GRILL_X = 560
AVO_X, TIAGO_X, W_X = 400, 200, 860


def alfama(tl, t):
    T = tl.t
    if T("a_song2") <= t < T("a_run"):
        # up at the castle, at dusk: the music floats up to Luna
        c = Canvas(castle_bg(True).copy())
        perk = t >= T("a_song2", 0.4)
        go = tl.prog("a_follow", t, 0.7, 1.0)
        if go <= 0:
            kat(c, tl, t, "luna", 520, WALK_Y + 40, 0.9, 1, "sit", eyes="wide" if perk else "closed",
                head_dy=-4 if perk else 10, look=(-1, 0.4) if perk else (0, 0))
        else:
            x = lerp(520, -100, go)
            kat(c, tl, t, "luna", x, WALK_Y + 40, 0.9, -1, "walk", walk=x / 7, eyes="happy")
        pavao(c, tl, t, 820, WALK_Y + 40, 1.0, -1, fan=0.0, eyes="happy" if t >= T("a_follow") else "open")
        P.music_notes(c, 300, 720, t, T("a_song2") - 1.0, n=6, col=(255, 230, 170), rise=500)
        return finish(c, tl, t)
    if T("a_run") <= t < T("a_luna"):
        c = Canvas(stairs_bg(True).copy())
        u = tl.prog("a_run", t)
        x = lerp(1250, 60, u)
        kat(c, tl, t, "luna", x, stair_y(x + 20), 0.8, -1, "walk", walk=x / 6, eyes="open", look=(-1, 0.3))
        P.music_notes(c, 200, 600, t, T("a_run"), n=4, col=(255, 230, 170), rise=300)
        return finish(c, tl, t)
    c = Canvas(avo_bg().copy())
    playing = T("a_song") <= t < T("a_luna")
    # Tiago with his guitar
    if playing:
        tiago(c, tl, t, TIAGO_X, 640, 1.0, 1, pose="sit", arm=0.35, eyes="closed", mouth=0.0)
        P.guitar(c, TIAGO_X + 34, 570, 0.85, ang=0.45, t=t, strum=1.0)
        P.music_notes(c, TIAGO_X + 60, 470, t, T("a_song"), n=5, col=(255, 230, 170), rise=380)
    else:
        tiago(c, tl, t, TIAGO_X, 640, 1.0, 1, pose="sit", arm=0.4 if t < T("a_fado") else 0.9,
              eyes="happy" if t >= T("a_hug") else "open",
              hold=(lambda cc, px, py: P.guitar(cc, px + 10, py - 10, 0.6, ang=-0.8)) if t >= T("a_fado", 0.4) else None)
    # Avo by her grill
    singing = playing
    avo(c, tl, t, AVO_X, 630, 1.0, 1, arm=0.6 if T("a_avo", 0.5) <= t < T("a_plate", 0.6) else 0.0,
        eyes="closed" if singing else ("happy" if t >= T("a_hug") else "open"),
        mouth=(0.35 + 0.3 * math.sin(t * 3.1)) if singing else tl.mouth("avo", t))
    P.grill(c, GRILL_X, 640, 1.0, t, n=5, glow=1.0)
    # the plate of sardines
    plate_k = ease(tl.prog("a_plate", t, 0.0, 0.4))
    if t >= T("a_plate"):
        px = lerp(GRILL_X, 740, plate_k) if t < T("a_cant", 0.5) else lerp(740, 700, tl.prog("a_cant", t, 0.5, 0.8))
        P.plate(c, px, 665, 0.8, n=3)
    # Whiskers
    if t < T("a_luna"):
        if t < T("a_avo", 0.3):
            u = tl.prog("a_avo", t, 0.0, 0.3)
            x = lerp(1350, W_X, ease(u))
            kat(c, tl, t, "whiskers", x, 670, 0.9, -1, "walk" if u < 1 else "stand", walk=x / 9)
        else:
            sad = T("a_cant") <= t
            kat(c, tl, t, "whiskers", W_X, 670, 0.9, -1, "sit",
                eyes="closed" if T("a_cant", 0.4) <= t < T("a_fado") else "open",
                head_dy=10 if sad else 0, look=(-1, 0.5) if t < T("a_cant") else (-1, 0),
                tail=0.0 if sad else None)
    else:
        # reunion
        u = ease(tl.prog("a_luna", t) * 0.5 + tl.prog("a_whis", t) * 0.5)
        hug = t >= T("a_hug")
        wx = lerp(W_X, 820, u) if not hug else 820
        lx = lerp(-80, 670, ease(tl.prog("a_luna", t, 0, 1) * 0.6 + tl.prog("a_whis", t) * 0.4)) if not hug else 700
        kat(c, tl, t, "whiskers", wx, 670, 0.9, -1, "stand", eyes="happy" if hug else "wide", squash=1.0)
        kat(c, tl, t, "luna", lx, 670, 0.9, 1, "stand" if hug or lx >= 679 else "walk", walk=lx / 7,
            eyes="happy" if hug else "open")
        if hug:
            P.hearts(c, 745, 540, t, T("a_hug"), n=4)
    return finish(c, tl, t)


# ===================================================================== festa

def night_panorama():
    def make():
        a = np.asarray(lisbon_panorama(1.0)).astype(np.float32)
        a = a * 0.45 + np.array((16, 18, 56), np.float32) * 0.55
        c = Canvas(Image.fromarray(a.astype(np.uint8), "RGB"))
        D.stars(c, 41, 80, W, 260)
        for k in range(60):
            x, y = (k * 97) % 760, 330 + (k * 53) % 260
            c.rect(x, y, x + 6, y + 8, (255, 214, 130), ol=None)
        return c.img
    return cached("night_pano", make)


DANCER_PALS = [
    {**D.WHISKERS, "body": (60, 60, 66), "dark": (40, 40, 46), "belly": (240, 240, 240), "stripes": False},
    {**D.LUNA, "body": (250, 250, 250), "dark": (220, 220, 220), "belly": (255, 255, 255), "collar": (230, 60, 60)},
    {**D.WHISKERS, "body": (180, 130, 90), "dark": (140, 100, 70), "collar": (60, 160, 80)},
    {**D.LUNA, "body": (120, 100, 90), "dark": (90, 76, 70), "belly": (230, 214, 200), "collar": (250, 200, 40)},
]


def festa(tl, t):
    T = tl.t
    if t >= T("f_fire"):
        # fireworks over the river, seen from the street above the roofs
        c = Canvas(night_panorama().copy())
        for k, (fx, fy, col) in enumerate(((300, 150, (255, 120, 120)), (700, 110, (140, 220, 255)),
                                           (1000, 170, (255, 230, 120)), (520, 200, (180, 255, 160)),
                                           (880, 230, (255, 160, 230)))):
            P.firework(c, fx, fy, t, T("f_fire", 0.05 + 0.17 * k), col, r=120)
        kat(c, tl, t, "luna", 560, 680, 0.9, 1, "sit", look=(0.5, -1), eyes="happy" if (t * 0.7) % 3 < 1 else "open")
        kat(c, tl, t, "whiskers", 680, 680, 0.9, -1, "sit", look=(-0.5, -1), mouth=0)
        P.hearts(c, 640, 540, t, T("f_fire", 0.5), n=3)
        return finish(c, tl, t)
    c = Canvas(avo_bg(True).copy())
    # crowd dancing in the back
    for k in range(6):
        x = 80 + k * 210
        hop = abs(math.sin(t * 5 + k)) * 14
        face = 1 if math.sin(t * 1.5 + k) > 0 else -1
        D.cat(c, x, 610 - hop, DANCER_PALS[k % 4], 0.55, face, "stand", t=t, seed=k + 9,
              eyes="happy", mouth=0.3 if k % 2 else 0)
    # grills glowing at the sides
    P.grill(c, 120, 665, 0.8, t, n=5)
    P.grill(c, 1180, 665, 0.8, t, n=5)
    dancing = t < T("f_share") or t >= T("f_fire", 0.4)
    # Tiago and Avo dancing
    if dancing:
        tiago(c, tl, t, 320, 665 - abs(math.sin(t * 5)) * 16, 0.85, 1 if math.sin(t * 2) > 0 else -1,
              pose="sit", arm=1.0, eyes="happy")
        avo(c, tl, t, 980, 665 - abs(math.sin(t * 5 + 1)) * 10, 0.85, -1 if math.sin(t * 2) > 0 else 1, arm=1.0,
            eyes="happy")
    else:
        tiago(c, tl, t, 260, 665, 0.85, 1, pose="sit", arm=0.3, eyes="happy")
        avo(c, tl, t, 1020, 665, 0.85, -1, eyes="happy")
    if dancing:
        ang = t * 3.0
        for who, ph in (("whiskers", 0.0), ("luna", math.pi)):
            x = 640 + math.cos(ang + ph) * 90
            hop = abs(math.sin(t * 6 + ph)) * 20
            face = 1 if math.sin(ang + ph) < 0 else -1
            kat(c, tl, t, who, x, 672 - hop, 0.85, face, "stand", eyes="happy")
        P.music_notes(c, 640, 520, t, T("f_narr"), n=4, col=(255, 230, 170))
    else:
        P.plate(c, 640, 672, 0.9, n=4, eaten=min(3, int(tl.prog("f_share", t, 0.6, 1.0) * 1 +
                                                       tl.prog("f_eat", t) * 2)))
        chew = T("f_eat") <= t < T("f_luna")
        give = T("f_share", 0.5) <= t < T("f_eat", 0.5)
        kat(c, tl, t, "whiskers", 520, 672, 0.9, 1, "sit", eyes="happy" if chew else "open",
            mouth=(0.3 + 0.3 * math.sin(t * 13)) if chew else tl.mouth("whiskers", t))
        kat(c, tl, t, "luna", 770, 672, 0.9, -1, "sit", eyes="happy" if chew or t >= T("f_next") else "open",
            mouth=(0.3 + 0.3 * math.sin(t * 12)) if chew else tl.mouth("luna", t))
        if give:
            u = tl.prog("f_share", t, 0.5, 1.0)
            P.sardine(c, lerp(600, 720, u), 600 + arc(u, 40), 0.5)
        if t >= T("f_next", 0.5):
            P.hearts(c, 645, 560, t, T("f_next", 0.5), n=3)
    return finish(c, tl, t)


# ====================================================================== home

def home(tl, t):
    T = tl.t
    if t < T("h_pip"):
        c = Canvas(home_bg(True).copy())
        c.tint = ((20, 20, 60), 0.3)
        arr = ease(tl.prog("h_open", t, 0.0, 0.7))
        if t < T("h_narr", 0.6):
            sx = lerp(1500, SC_X, arr)
        else:
            u = t - T("h_narr", 0.6)
            sx = SC_X + 120 * u * u + 40 * u
        in_car = t < T("h_open", 0.85)
        P.scooter(c, sx, STREET_Y, 0.9, t, wheel_ang=-sx / 25, lights=True,
                  rider=tiago_rider(tl, t, arm=1.0 if T("h_narr", 0.3) <= t < T("h_narr", 0.7) else 0.5,
                                    eyes="happy"),
                  side=sidecar_cats(tl, t, l_eyes="happy", w_eyes="happy") if in_car else None)
        # the cats hop up to the sill
        hop = tl.prog("h_open", t, 0.85, 1.0) * 0.4 + tl.prog("h_narr", t, 0.0, 0.25) * 0.6
        if not in_car:
            for who, x0, x1 in (("luna", SC_X + 230, 230), ("whiskers", SC_X + 160, 360)):
                if hop < 1:
                    kat(c, tl, t, who, lerp(x0, x1, hop), lerp(STREET_Y - 80, SILL, hop) + arc(hop, 120), 0.9, -1,
                        "leap")
                else:
                    kat(c, tl, t, who, x1, SILL, 0.9, 1, "sit", eyes="happy")
        c.tint = None
        # Avo's tile, hung by the window
        k = ease(tl.prog("h_narr", t, 0.5, 0.8))
        if k > 0:
            P.gift_tile(c, 520, 300, 0.55 * k)
        return finish(c, tl, t)
    bg = home_bg(True)
    c = cam(bg, 380, 330, 1.9)
    c.tint = ((20, 20, 60), 0.12)
    P.gift_tile(c, 520, 300, 0.55)
    end = t >= T("h_moral")
    kat(c, tl, t, "luna", 210, SILL, 0.9, 1, "sit", eyes="happy" if end else "open")
    kat(c, tl, t, "whiskers", 330, SILL, 0.9, 1, "sit", eyes="happy" if end or t >= T("h_miss", 0.6) else "open")
    talk = T("h_pip") <= t < T("h_pip", 1)
    got = t >= T("h_miss", 0.3)
    D.mouse(c, 420, SILL, 1.1, -1, t, mouth=tl.mouth("pip", t), proud=talk or got,
            hop=abs(math.sin(t * 8)) * 8 if talk else 0, eyes="happy" if got else "open")
    if got:
        P.sardine(c, 436, SILL - 60, 0.4, ang=-1.2, cooked=1.0)
    else:
        P.sardine(c, 380, SILL - 10, 0.4, ang=0.0)
    if end:
        P.hearts(c, 300, SILL - 150, t, T("h_moral", 0.3), n=3)
    c.tint = None
    c.tf = [(0.0, 0.0, 1.0, 1.0)]
    k = ease(tl.prog("h_end", t, 0.25, 0.55))
    if k > 0:
        c.text(W / 2, 110, "The End", 30 + 44 * k, mix((40, 40, 90), (255, 236, 180), k), stroke=4 * k,
               stroke_fill=(50, 30, 60))
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "sill": sill, "ride": ride, "belem": belem, "tram": tram, "castle": castle,
               "lost": lost, "alfama": alfama, "festa": festa, "home": home}
CONTINUOUS = set()
EXTRA_CUTS = ["r_wake", "b_nata", "tr_look", "tr_stop", "c_view", "l_wander", "l_lift", "l_dusk",
              "a_song2", "a_run", "a_luna", "f_fire", "h_pip"]
