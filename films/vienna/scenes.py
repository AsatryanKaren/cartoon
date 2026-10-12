"""Scenes of "Whiskers and the Two Left Paws". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
Static layers are cached; a few shots use a zooming camera (`cam`) that
crops the cached background and draws characters through a scaled transform.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.vienna import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "ferdinand": 3.3, "mitzi": 4.4, "countess": 5.5}
BOW = (200, 40, 60)          # Whiskers' bow tie
LUNA_GOWN = (110, 160, 235)

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
    """Like track, but eased between keys."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def dance(c, tl, t, who, x, y, s=1.0, face=1, **kw):
    """Whiskers or Luna up on their hind legs (bow tie / gown when dressed)."""
    mouth = kw.pop("mouth", tl.mouth(who, t))
    dressed = kw.pop("dressed", False)
    if dressed:
        if who == "whiskers":
            kw.setdefault("bowtie", BOW)
        else:
            kw.setdefault("gown", LUNA_GOWN)
    P.dancer(c, x, y, s, face, PAL[who], t, mouth=mouth, seed=SEED[who], **kw)


def ferdinand(c, tl, t, x, y, s=0.8, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("ferdinand", t))
    P.horse(c, x, y, s, face, t, mouth=mouth, **kw)


def mitzi(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("mitzi", t))
    P.dancer(c, x, y, s, face, P.MITZI, t, mouth=mouth, seed=SEED["mitzi"], gown=(250, 250, 250), **kw)
    # her little white cap
    c.push(x, y - kw.get("hop", 0.0), s, flip=face < 0)
    hx, hy = 16 + kw.get("lean", 0.0), -140
    c.ellipse(hx - 4, hy - 30, 20, 7, (255, 255, 255), w=2)
    c.ellipse(hx - 4, hy - 36, 14, 7, (255, 255, 255), w=2)
    c.pop()


def countess(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("countess", t))
    P.dancer(c, x, y, s, face, P.COUNTESS, t, mouth=mouth, seed=SEED["countess"], gown=(170, 90, 200),
             tiara=True, **kw)


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


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def arc(u, h):
    return -4 * h * u * (1 - u)


def finish(c, tl, t, strength=0.55):
    c.tf = [(0.0, 0.0, 1.0, 1.0)]
    c.tint = None
    P.shade_bottom(c, tl, t, strength)
    return c


def cam(bg, cx, cy, z):
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


def hearts(c, x, y, t, t0, n=4, col=(240, 80, 110)):
    if t < t0:
        return
    for k in range(n):
        u = ((t - t0) * 0.5 + k / n) % 1.0
        hx = x + 30 * math.sin(k * 2.1 + t * 2) * u + (k - n / 2) * 14
        hy = y - 120 * u
        r = 7 * (1 - u * 0.5)
        col2 = mix(col, (255, 255, 255), u * 0.6)
        c.circle(hx - r * 0.5, hy, r * 0.6, col2, ol=None)
        c.circle(hx + r * 0.5, hy, r * 0.6, col2, ol=None)
        c.poly([(hx - r * 1.05, hy + r * 0.15), (hx + r * 1.05, hy + r * 0.15), (hx, hy + r * 1.2)], col2, ol=None)


def bubble(c, x, y, rx, ry, k, tail=(0, 0), fill=(255, 255, 255)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 8), (0.65, 13)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, fill, ol=None)


def dizzy(c, x, y, t, r=34):
    for k in range(3):
        a = t * 5 + k * math.tau / 3
        sx, sy = x + math.cos(a) * r, y + math.sin(a) * r * 0.35
        pts = []
        for j in range(10):
            rr = 8 if j % 2 == 0 else 3.5
            aa = j * math.pi / 5 - math.pi / 2
            pts.append((sx + math.cos(aa) * rr, sy + math.sin(aa) * rr))
        c.poly(pts, (255, 220, 80), w=1.5)


BAR = 3 * 60.0 / 172           # one waltz bar, in seconds


def couple(c, tl, t, cx, cy, s, ang, a, b, step=None, hop=True, lean=0.0, sep=52):
    """A waltzing pair turning around (cx, cy). a, b: dicts with keys who / pal / and dancer kwargs."""
    beat = (t % BAR) / BAR
    h = 7 * s * max(0.0, math.cos(beat * math.tau)) ** 6 if hop else 0.0
    st = t * 7.0 if step is None else step
    dx = math.cos(ang) * sep * s
    dep = math.sin(ang)
    pa = (cx - dx, cy - dep * 6 * s)
    pb = (cx + dx, cy + dep * 6 * s)
    fa = 1 if pb[0] >= pa[0] else -1
    items = [(pa, a, fa, -dep), (pb, b, -fa, dep)]
    items.sort(key=lambda it: it[3])
    for (px, py), d, f, dd in items:
        d = dict(d)
        who = d.pop("who", None)
        sc = s * (1 + 0.04 * dd)
        ln = d.pop("lean", lean)
        if who in ("whiskers", "luna"):
            dance(c, tl, t, who, px, py, sc, f, step=st, hop=h, lean=ln, **d)
        elif who == "countess":
            countess(c, tl, t, px, py, sc, f, step=st, hop=h, **d)
        else:
            P.dancer(c, px, py, sc, f, t=t, step=st, hop=h, lean=ln, **d)


# ===================================================================== title

def skyline_far(c, base, tint_col, tint_k, wheel_x=None):
    """Distant Vienna: St. Stephen's, Karlskirche dome, Opera roofs (drawn with an atmospheric tint)."""
    c.tint = (tint_col, tint_k)
    for x, w, h in ((380, 120, 70), (520, 140, 90), (640, 90, 60), (1180, 160, 80), (1290, 120, 60)):
        c.rect(x - w / 2, base - h, x + w / 2, base + 10, (190, 170, 160), w=2)
    P.opera(c, 560, base, 0.25)
    karlskirche(c, 1180, base, 0.55)
    P.stephansdom(c, 860, base, 0.5)
    c.tint = None


def karlskirche(c, x, y, s=1.0):
    c.push(x, y, s)
    st = (232, 222, 200)
    c.rect(-150, -120, 150, 0, st, w=3)
    c.rect(-70, -200, 70, -120, st, w=3)
    c.ellipse(0, -200, 70, 30, P.COPPER, w=3)
    c.poly([(-62, -210), (-50, -280), (0, -310), (50, -280), (62, -210)], P.COPPER, w=3)
    c.rect(-8, -330, 8, -306, P.COPPER, w=2)
    c.circle(0, -336, 6, P.GOLD, w=1.5)
    for sx in (-1, 1):
        c.rect(sx * 115 - 16, -260, sx * 115 + 16, -120, st, w=2.5)
        for k in range(5):
            c.arc(sx * 115, -240 + k * 26, 16, 6, 0, 180, P.STONE_D, 2)
        c.ellipse(sx * 115, -262, 20, 7, P.COPPER, w=2)
    c.poly([(-60, -120), (0, -160), (60, -120)], st, w=2.5)
    for k in range(4):
        c.rect(-46 + k * 28, -120, -38 + k * 28, -40, st, w=2)
    c.pop()


def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (34, 34, 92)), (0.38, (120, 80, 150)), (0.62, (246, 160, 130)),
                                               (0.78, (255, 210, 150)), (1, (255, 210, 150))]))
        D.stars(c, 5, 70, W, 220, col=(255, 246, 220))
        D.moon(c, 1150, 90, 26, sky=(60, 50, 110))
        skyline_far(c, 540, (200, 130, 150), 0.45)
        return c.img
    return cached("title_bg", make)


def rooftops():
    def make():
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img)
        # back row of houses with warm windows
        cols = [(214, 170, 150), (196, 150, 160), (226, 190, 150), (180, 140, 150), (210, 176, 170)]
        x = -20
        k = 0
        while x < W + 20:
            w = 150 + 40 * (k % 3)
            h = 70 + 26 * ((k * 7) % 4)
            col = cols[k % len(cols)]
            top = 560 - h
            c.rect(x, top, x + w, H, col, w=2.5)
            c.poly([(x - 6, top), (x + 20, top - 34), (x + w - 20, top - 34), (x + w + 6, top)], (110, 70, 80), w=2.5)
            for wy in range(int(top + 22), 700, 52):
                for wx in range(int(x) + 18, int(x + w) - 26, 40):
                    lit = ((wx * 7 + wy * 3) // 13) % 3 != 0
                    c.rect(wx, wy, wx + 20, wy + 30, (255, 214, 130) if lit else (90, 80, 110), w=1.5)
            x += w + 8
            k += 1
        # the near roof the cats dance on
        c.poly([(-20, H + 10), (-20, 620), (900, 610), (1010, H + 10)], (150, 70, 60), w=3)
        for k in range(1, 5):
            y = 610 + k * 24
            c.line([(-20, y + 2), (900 + 26 * k, y)], (120, 52, 46), 2.5, cap=False)
        for x in range(0, 960, 46):
            c.line([(x, 612), (x + 30, H)], (128, 58, 50), 2, cap=False)
        c.rect(-20, 602, 900, 616, (120, 50, 44), w=3, r=3)
        c.rect(140, 520, 190, 610, (170, 90, 80), w=3)
        c.rect(132, 510, 198, 524, (130, 60, 56), w=2.5)
        return img
    return cached("rooftops", make)


def title(tl, t):
    T = tl.t
    c = Canvas(title_bg().copy())
    P.riesenrad(c, 180, 360, 120, rot=t * 0.05, t=t, cabins=15, lit=0.6)
    c.img.paste(rooftops(), (0, 0), rooftops())
    # the two cats waltz on the roof ridge
    k = ease(tl.prog("t_open", t, 0.05, 0.4))
    ang = t * math.tau / (2 * BAR)
    c.tint = ((60, 40, 90), 0.2)
    couple(c, tl, t, 520, 608, 0.85, ang, dict(who="whiskers", dressed=True, arm=0.9, eyes="happy"),
           dict(who="luna", dressed=True, arm=0.9, eyes="happy"))
    c.tint = None
    P.music_notes(c, 520, 400, t, T("t_open", 0.2), n=4)
    k = ease(tl.prog("t_open", t, 0.2, 0.75))
    c.text(W / 2, 86 - 30 * (1 - k), "Whiskers and the", 44, mix((60, 50, 110), (255, 246, 225), k),
           stroke=3 * k, stroke_fill=(60, 30, 70))
    k2 = ease(tl.prog("t_open", t, 0.45, 1.0))
    c.text(W / 2, 168, "TWO LEFT PAWS", 28 + 54 * k2, mix((60, 50, 110), (255, 214, 120), k2), stroke=5 * k2,
           stroke_fill=(110, 40, 70))
    return finish(c, tl, t)


# ====================================================================== sill

SILL = 432


def street_bg(night=False):
    def make():
        if night:
            sky = [(0, (20, 24, 64)), (0.6, (50, 50, 110)), (1, (70, 60, 120))]
        else:
            sky = [(0, (126, 184, 238)), (0.6, (214, 234, 250)), (1, (214, 234, 250))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        if night:
            D.stars(c, 8, 90, W, 300)
            D.moon(c, 730, 160, 40, sky=(30, 34, 80))
        else:
            D.cloud(c, 980, 90, 0.9)
            D.cloud(c, 1200, 170, 0.6)
        dk = 0.55 if night else 0.0
        night_c = (40, 40, 90)
        for x, w, h, col in ((700, 170, 320, (226, 196, 150)), (880, 150, 260, (200, 130, 120)),
                             (1040, 240, 340, (236, 222, 196))):
            col = mix(col, night_c, dk)
            c.rect(x, 560 - h, x + w, 560, col, w=2.5)
            c.poly([(x - 12, 560 - h), (x + w / 2, 560 - h - 60), (x + w + 12, 560 - h)],
                   mix((150, 80, 70), night_c, dk), w=2.5)
            for wy in range(int(560 - h + 40), 500, 80):
                for wx in range(int(x) + 24, int(x + w) - 30, 56):
                    lit = night and ((wx + wy) // 7) % 3 != 0
                    c.rect(wx, wy, wx + 28, wy + 38, (255, 214, 130) if lit else mix((170, 210, 240), night_c, dk),
                           w=2)
        D.tree(c, 1250, 560, 0.9, leaf=mix((110, 170, 80), night_c, dk))
        # pavement + road
        c.rect(0, 556, W, 600, mix((200, 196, 190), night_c, dk), ol=None)
        c.line([(0, 556), (W, 556)], OUT, 2.5, cap=False)
        c.rect(0, 600, W, H, mix((110, 112, 120), night_c, dk), ol=None)
        c.rect(0, 598, W, 606, mix((150, 150, 156), night_c, dk), ol=None)
        for x in range(30, W, 160):
            c.rect(x, 686, x + 80, 692, mix((240, 236, 220), night_c, dk), ol=None)
        if night:
            # lamp post glow
            c.glow(640, 420, 90, 90, (255, 230, 160), (60, 60, 110), steps=8)
        c.rect(636, 420, 644, 600, (50, 50, 60), w=2)
        c.rect(624, 400, 656, 428, (255, 230, 150) if night else (230, 230, 210), w=2.5, r=4)
        c.poly([(620, 402), (640, 386), (660, 402)], (50, 50, 60), w=2)
        # the cats' house (left)
        wall = mix((244, 222, 178), night_c, dk * 0.8)
        c.rect(-10, 0, 600, 560, wall, w=3)
        for y in range(20, 560, 34):
            c.line([(-10, y), (600, y)], mix(wall, (150, 110, 70), 0.25), 2, cap=False)
        c.rect(-10, 0, 600, 24, mix((150, 80, 70), night_c, dk), w=3)
        # window with the room inside
        room = (255, 214, 150) if night else (250, 214, 160)
        c.rect(150, 210, 470, SILL, (120, 92, 80), w=3)
        c.rect(158, 218, 462, SILL, room, ol=None)
        c.rect(158, 340, 462, SILL, mix(room, (200, 140, 100), 0.5), ol=None)
        c.rect(380, 250, 440, 320, (150, 100, 60), w=2)
        c.rect(386, 256, 434, 314, (40, 46, 96), ol=None)
        c.circle(418, 272, 8, (250, 246, 215), ol=None)
        for x0, x1 in ((112, 152), (468, 508)):
            c.rect(x0, 200, x1, SILL, mix((90, 140, 90), night_c, dk), w=2.5)
            for y in range(214, SILL - 6, 18):
                c.line([(x0 + 4, y), (x1 - 4, y)], mix((70, 116, 70), night_c, dk), 2, cap=False)
        c.rect(120, SILL, 500, SILL + 18, mix((250, 246, 236), night_c, dk * 0.6), w=3, r=3)
        c.rect(40, 450, 110, 556, mix((160, 70, 60), night_c, dk), w=2.5)
        c.circle(96, 506, 4, (250, 210, 70), w=1.5)
        for x in (520, 560):
            D.flower(c, x, 556, mix((230, 80, 90), night_c, dk), 1.0)
        return c.img
    return cached(("street", night), make)


def fish(c, x, y, s=1.0, bite=0.0, col=(170, 186, 200)):
    c.push(x, y, s)
    body = [(-40, 0), (-20, -14), (20, -12), (34, 0), (20, 12), (-20, 14)]
    c.poly(body, col, w=2.5)
    c.poly([(-40, 0), (-58, -14), (-54, 0), (-58, 14)], col, w=2.5)
    c.circle(22, -3, 3, OUT, ol=None)
    if bite > 0:
        for k in range(int(bite * 4) + 1):
            c.circle(34 - k * 12, -2, 11, (250, 246, 236), ol=None)
    c.pop()


def bus_roof(tl, t, lid, w_in, l_in, peek=0.0, sleepy=False):
    """Roof-rack cargo for the orchestra bus: violin cases + the open double bass case with cats."""
    def roof(c):
        P.violin_case(c, -200, -246, 0.9)
        P.violin_case(c, 120, -246, 0.8, col=(40, 50, 70))
        P.bass_lid(c, -40, -246, 1.0, lid)

        def inside(cc):
            if l_in:
                kat(cc, tl, t, "luna", 30, -14 + 30 * (1 - peek), 0.6, 1, "sit", tail=0)
            if w_in:
                if sleepy:
                    kat(cc, tl, t, "whiskers", -60, -10, 0.6, 1, "sleep")
                else:
                    kat(cc, tl, t, "whiskers", -50, -14 + 30 * (1 - peek), 0.6, 1, "sit", tail=0)
        P.bass_case(c, -40, -246, 1.0, lid, inside=inside)
    return roof


BUS_X, BUS_Y, BUS_S = 900, 700, 0.85


def sill(tl, t):
    T = tl.t
    c = Canvas(street_bg().copy())
    # --- the bus arrives, waits, and leaves
    if t >= T("s_bus"):
        if t < T("s_drive", 0.15):
            u = clamp((t - T("s_bus")) / (T("s_bus", 1) + 0.6 - T("s_bus")))
            bx = lerp(1800, BUS_X, 1 - (1 - u) ** 2)
        else:
            u = t - T("s_drive", 0.15)
            bx = BUS_X + 70 * u * u + 20 * u
        lid = 0.85
        w_in = t >= T("s_sneak", 0.68)
        l_in = t >= T("s_sneak", 0.33)
        P.bus(c, bx, BUS_Y, BUS_S, t, wheel_ang=-bx / 30, roof=bus_roof(tl, t, lid, w_in, l_in, peek=1.0))
        if T("s_pip") <= t:
            P.music_notes(c, bx - 40, BUS_Y - 260, t, T("s_pip"), n=3, col=(255, 230, 160))
    # --- Whiskers on the sill
    wx = 380
    bite = clamp(tl.prog("s_narr", t, 0.0, 1.0) + tl.prog("s_look", t) * 0.5)
    paper_k = ease(tl.prog("s_look", t, 0.0, 0.12)) * (1 - ease(tl.prog("s_think", t, 0.3, 0.9)))
    if t < T("s_dance"):
        if t < T("s_look"):
            # eating his fish on the unwrapped newspaper
            P.newspaper(c, 330, SILL + 2, 0.5, open_=0.0 if t < T("s_open", 0.5) else 0.0)
            fish(c, 336, SILL - 18, 0.8, bite=bite)
            chew = 0.3 + 0.3 * math.sin(t * 13) if T("s_open", 0.6) <= t else 0
            kat(c, tl, t, "whiskers", wx, SILL, 0.9, -1, "sit", head_dy=8, mouth=chew,
                eyes="happy" if chew else "open")
        else:
            nope = T("s_nope") <= t < T("s_prize")
            wow = t >= T("s_prize", 0.6)
            kat(c, tl, t, "whiskers", wx, SILL, 0.9, -1 if not nope else 1, "sit",
                eyes="closed" if nope else ("wide" if wow else "open"), look=(1, -0.5) if wow else (1, 0))
            if wow:
                hearts(c, wx, SILL - 140, t, T("s_prize", 0.6), n=3, col=(150, 80, 60))
    elif t < T("s_twirl", 0.62):
        # up on his hind legs, then a wild twirl
        u = tl.prog("s_twirl", t, 0.0, 0.62)
        spin = t >= T("s_twirl")
        face = -1 if not spin else (1 if math.sin(u * 22) > 0 else -1)
        dance(c, tl, t, "whiskers", wx - 10 + 30 * math.sin(u * 7) * spin, SILL, 0.85, face,
              arm=0.9 if not spin else 1.0, arm2=0.2, eyes="happy" if not spin else "closed",
              step=u * 30 if spin else 0, lean=-10 * u if spin else 0, hop=abs(math.sin(u * 22)) * 8 * spin)
    elif t < T("s_bus", 0.4):
        kat(c, tl, t, "whiskers", wx + 10, SILL, 0.9, 1, "crouch", squash=0.7, eyes="closed", tail=0.2)
        dizzy(c, wx + 60, SILL - 80, t)
    elif t < T("s_sneak", 0.55):
        kat(c, tl, t, "whiskers", wx, SILL, 0.9, 1, "sit" if t < T("s_sneak", 0.4) else "crouch",
            eyes="wide" if t < T("s_narr2") else "open", look=(1, 0.3))
    elif t < T("s_sneak", 0.7):
        u = tl.prog("s_sneak", t, 0.55, 0.7)
        tx, ty = BUS_X + (-90) * BUS_S, BUS_Y - 262 * BUS_S
        kat(c, tl, t, "whiskers", lerp(wx, tx, u), lerp(SILL, ty, u) + arc(u, 110), lerp(0.9, 0.55, u), 1, "leap",
            eyes="happy")
    # --- Luna on the sill
    lx = 250
    if t < T("s_sneak", 0.2):
        excited = T("s_look") <= t < T("s_look", 1) or T("s_prize") <= t < T("s_prize", 1)
        laugh = T("s_twirl", 0.65) <= t < T("s_bus")
        pose = "stand" if T("s_bus") <= t else "sit"
        kat(c, tl, t, "luna", lx, SILL, 0.9, 1, pose, eyes="happy" if (excited or laugh) else "open",
            mouth=laughing(t) * 0.6 if laugh else tl.mouth("luna", t),
            look=(1, -0.4) if excited else (1, 0.2))
    elif t < T("s_sneak", 0.35):
        u = tl.prog("s_sneak", t, 0.2, 0.35)
        tx, ty = BUS_X + 30 * BUS_S, BUS_Y - 262 * BUS_S
        kat(c, tl, t, "luna", lerp(lx, tx, u), lerp(SILL, ty, u) + arc(u, 140), lerp(0.9, 0.55, u), 1, "leap")
    # --- Pip pops up on the sill to point at the bus
    if t >= T("s_twirl", 0.9):
        k = ease(tl.prog("s_twirl", t, 0.9, 1.0) * 0.4 + tl.prog("s_bus", t, 0, 0.3) * 0.6)
        wave = T("s_bus") <= t < T("s_bus", 1) or T("s_pip") <= t
        D.mouse(c, lerp(110, 170, k), SILL, 1.3, 1, t, walk=t * 12 if k < 1 else 0, mouth=tl.mouth("pip", t),
                hop=abs(math.sin(t * 8)) * 10 if wave else 0, proud=wave)
    # --- the newspaper close-up
    if paper_k > 0.02:
        c.push(860, 330, 0.4 + 1.2 * paper_k)
        P.newspaper(c, 0, 0, 1.0, open_=1.0, t=t)
        if t >= T("s_prize"):
            c.circle(60, -40, 52, None, ol=(220, 40, 50), w=3)
        c.pop()
    if T("s_prize", 0.6) <= t < T("s_dance"):
        k = ease(tl.prog("s_prize", t, 0.6, 1.0))
        bubble(c, 480, 180, 90, 60, k, tail=(wx + 10, SILL - 150))
        if k > 0.9:
            P.sachertorte(c, 480, 216, 0.95)
    return finish(c, tl, t)


# ======================================================================= bus

HILLS_Y = 470
RIVER_Y = 520
ROAD_Y = 700
V_BUS = 420.0          # px per second of the near layer


def bus_pos(tl, t):
    T = tl.t
    t0, ta, tb = tl.scenes["bus"][0], T("b_arrive", 0.1), T("b_arrive", 0.8)
    if t < ta:
        return V_BUS * (t - t0)
    d = tb - ta
    u = min(t, tb) - ta
    return V_BUS * (ta - t0) + V_BUS * (u - u * u / (2 * d))


def far_hills(tl):
    end = bus_pos(tl, tl.scenes["bus"][1])
    width = int(W + end * 0.12 + 40)
    vienna_x = width - 520

    def make():
        img = Image.new("RGBA", (width * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img, size=(width, H))
        def hill(x):
            return HILLS_Y - 60 - 40 * math.sin(x / 260) - 22 * math.sin(x / 97 + 1)
        pts = [(-20, H)]
        for x in range(-20, width + 60, 30):
            pts.append((x, hill(x)))
        pts.append((width + 60, H))
        c.poly(pts, (150, 180, 200), ol=None)
        # an abbey on a hill (like Melk, on the Danube)
        ax = 900
        c.push(ax, max(hill(ax - 100), hill(ax), hill(ax + 100)) + 14, 0.5)
        c.rect(-230, 0, 230, 60, (150, 180, 200), ol=None)
        c.rect(-200, -90, 200, 0, P.SCHON, w=3)
        c.poly([(-210, -90), (-190, -120), (190, -120), (210, -90)], (200, 110, 70), w=3)
        for k in range(-8, 9):
            c.rect(k * 22 - 6, -70, k * 22 + 6, -50, (120, 110, 100), ol=None)
        for sx in (-1, 1):
            c.rect(sx * 40 - 18, -200, sx * 40 + 18, -90, P.SCHON, w=3)
            c.ellipse(sx * 40, -206, 20, 26, P.COPPER, w=2.5)
            c.line([(sx * 40, -232), (sx * 40, -250)], OUT, 2)
        c.ellipse(0, -150, 46, 40, P.COPPER, w=3)
        c.pop()
        # Vienna on the horizon: the wheel, the cathedral spire
        c.tint = ((150, 180, 210), 0.35)
        P.riesenrad(c, vienna_x - 160, HILLS_Y - 150, 70, rot=0.2, cabins=12)
        P.stephansdom(c, vienna_x + 120, HILLS_Y - 30, 0.3)
        karlskirche(c, vienna_x + 330, HILLS_Y - 30, 0.3)
        for x in range(vienna_x - 300, vienna_x + 460, 46):
            c.rect(x, HILLS_Y - 60 - (x * 13) % 40, x + 40, HILLS_Y + 10, (230, 210, 190), w=2)
        c.tint = None
        return img
    return cached(("far_hills", width), make), vienna_x


def mid_tile():
    """Repeating vineyards and the Danube (RGBA, 2 x W wide)."""
    def make():
        tw = 2 * W
        img = Image.new("RGBA", (tw * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img, size=(tw, H))
        pts = [(0, H)]
        for x in range(0, tw + 40, 40):
            pts.append((x, HILLS_Y - 10 - 26 * math.sin(x * math.tau / tw * 2) - 12 * math.sin(x * math.tau / tw * 5)))
        pts.append((tw, H))
        c.poly(pts, (120, 170, 90), ol=None)
        for row in range(5):
            y = HILLS_Y + 6 + row * 9
            for x in range(0, tw, 18):
                c.circle(x + (row % 2) * 9, y - 22 * math.sin(x * math.tau / tw * 2), 4, (80, 140, 70), ol=None)
        for x in range(60, tw, 330):
            c.rect(x, HILLS_Y - 24, x + 44, HILLS_Y + 6, (250, 240, 220), w=2)
            c.poly([(x - 6, HILLS_Y - 24), (x + 22, HILLS_Y - 46), (x + 50, HILLS_Y - 24)], (200, 90, 70), w=2)
        # the river
        c.rect(0, RIVER_Y - 18, tw, RIVER_Y + 20, (90, 150, 210), ol=None)
        c.rect(0, RIVER_Y - 22, tw, RIVER_Y - 16, (160, 190, 120), ol=None)
        for x in range(0, tw, 70):
            c.line([(x, RIVER_Y - 4 + (x % 3) * 6), (x + 30, RIVER_Y - 4 + (x % 3) * 6)], (180, 215, 245), 2, cap=False)
        # near bank, grass verge
        c.rect(0, RIVER_Y + 20, tw, ROAD_Y - 80, (130, 190, 100), ol=None)
        c.line([(0, RIVER_Y + 20), (tw, RIVER_Y + 20)], (90, 140, 80), 2, cap=False)
        # a paddle steamer on the river
        sx = 1500
        c.rect(sx - 70, RIVER_Y - 30, sx + 70, RIVER_Y - 8, (250, 250, 246), w=2)
        c.rect(sx - 40, RIVER_Y - 46, sx + 40, RIVER_Y - 30, (250, 250, 246), w=2)
        c.rect(sx + 6, RIVER_Y - 70, sx + 18, RIVER_Y - 46, (200, 50, 50), w=2)
        c.ellipse(sx - 30, RIVER_Y - 18, 16, 14, (200, 50, 50), w=2)
        return img
    return cached("mid_tile", make)


def bus_scene_sky():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 170, 235)), (0.6, (210, 230, 250)), (1, (220, 236, 250))]))
        D.cloud(c, 260, 110, 1.0)
        D.cloud(c, 820, 70, 0.7)
        D.cloud(c, 1100, 150, 0.9)
        return c.img
    return cached("bus_sky", make)


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


def bus(tl, t):
    T = tl.t
    c = Canvas(bus_scene_sky().copy())
    pos = bus_pos(tl, t)
    far, vx = far_hills(tl)
    paste_scroll(c, far, pos * 0.12)
    paste_scroll(c, mid_tile(), pos * 0.35, tile_w=2 * W)
    # road
    c.rect(0, ROAD_Y - 80, W, H, (120, 120, 128), ol=None)
    c.rect(0, ROAD_Y - 84, W, ROAD_Y - 76, (170, 170, 176), ol=None)
    for k in range(-1, 9):
        x = k * 180 - (pos % 180)
        c.rect(x, ROAD_Y - 6, x + 90, ROAD_Y + 2, (240, 236, 220), ol=None)
    # roadside posts behind the bus
    for k in range(-1, 6):
        x = k * 300 - (pos * 0.9 % 300)
        c.rect(x, ROAD_Y - 120, x + 8, ROAD_Y - 80, (250, 250, 250), w=1.5)
        c.rect(x, ROAD_Y - 112, x + 8, ROAD_Y - 104, (30, 30, 30), ol=None)
    v = V_BUS if t < T("b_arrive", 0.1) else max(0.0, V_BUS * (1 - (t - T("b_arrive", 0.1)) / (T("b_arrive", 0.8) - T("b_arrive", 0.1))))
    bob = 2 * math.sin(t * 9) * (v / V_BUS)
    bump = 0.0
    for fr in (0.3, 0.75):
        bt = T("b_ride", fr)
        if bt <= t < bt + 0.5:
            bump = -14 * math.sin(math.pi * (t - bt) / 0.5)
    sleepy = t < T("b_look")
    peek = 1.0
    lid = 0.85
    roof = bus_roof(tl, t, lid, True, True, peek=peek, sleepy=sleepy)
    luna_up = t >= T("b_look")

    def roof2(cc):
        roof(cc) if not luna_up else None
        if luna_up:
            P.violin_case(cc, -200, -246, 0.9)
            P.violin_case(cc, 120, -246, 0.8, col=(40, 50, 70))
            P.bass_lid(cc, -40, -246, 1.0, lid)

            def inside(c3):
                kat(c3, tl, t, "whiskers", -50, -14, 0.6, 1, "sit", eyes="wide" if t < T("b_look", 1) else "open",
                    look=(1, -0.3))
                kat(c3, tl, t, "luna", 40, -20, 0.6, 1, "stand", look=(1, -0.3), eyes="happy" if t > T("b_look", 0.5) else "open")
            P.bass_case(cc, -40, -246, 1.0, lid, inside=inside)
    c.push(0, bob + bump)
    P.bus(c, 560, ROAD_Y, 1.2, t, wheel_ang=pos / 40, roof=roof2)
    c.pop()
    if sleepy and t >= T("b_ride", 0.1):
        D.zzz(c, 560 + (-100) * 1.2, ROAD_Y - 330 + bob + bump, t)
    if T("b_ride", 0.3) <= t < T("b_ride", 0.3) + 1.2 or T("b_ride", 0.75) <= t < T("b_ride", 0.75) + 1.2:
        bt = T("b_ride", 0.3) if t < T("b_ride", 0.75) else T("b_ride", 0.75)
        P.music_notes(c, 500, ROAD_Y - 330, t, bt, n=3, col=(255, 220, 160))
    # roadside bushes in front (fast)
    for k in range(-1, 5):
        x = k * 420 - (pos * 1.25 % 420)
        D.bush(c, x + 100, H + 20, 1.0, col=(80, 150, 80))
    return finish(c, tl, t)


# ====================================================================== city

SQ_Y = 600


def facade(c, x, w, h, col, base=560, roof=(120, 80, 70), seed=0):
    top = base - h
    c.rect(x, top, x + w, base, col, w=2.5)
    c.rect(x - 4, top - 14, x + w + 4, top, mix(col, (255, 255, 255), 0.3), w=2.5)
    c.poly([(x - 4, top - 14), (x + 14, top - 50), (x + w - 14, top - 50), (x + w + 4, top - 14)], roof, w=2.5)
    rows = int((h - 80) // 70)
    for r in range(rows):
        wy = top + 34 + r * 70
        for wx in range(int(x) + 20, int(x + w) - 30, 48):
            c.rect(wx, wy, wx + 26, wy + 40, (130, 160, 190), w=2)
            if r == 0:
                c.poly([(wx - 4, wy - 2), (wx + 13, wy - 14), (wx + 30, wy - 2)], mix(col, (255, 255, 255), 0.4), w=1.5)
            else:
                c.rect(wx - 4, wy - 6, wx + 30, wy - 1, mix(col, (255, 255, 255), 0.4), w=1.5)
    c.rect(x, base - 64, x + w, base, mix(col, (0, 0, 0), 0.08), w=2.5)
    for wx in range(int(x) + 16, int(x + w) - 40, 70):
        P.arch_window(c, wx + 22, base, 40, 56, (90, 70, 66), ww=2)


def square_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 180, 236)), (0.7, (214, 234, 250)), (1, (214, 234, 250))]))
        D.cloud(c, 240, 120, 0.9)
        D.cloud(c, 1120, 90, 0.7)
        P.stephansdom(c, 640, 540, 0.6)
        facade(c, -40, 240, 330, (236, 206, 170), base=560, seed=1)
        facade(c, 1060, 260, 360, (226, 186, 160), base=560, roof=(110, 90, 100), seed=2)
        # cobbled square
        c.rect(0, 540, W, H, (200, 186, 166), ol=None)
        c.line([(0, 540), (W, 540)], OUT, 2.5, cap=False)
        rng = np.random.default_rng(4)
        for y in range(552, H, 18):
            off = (y // 18) % 2 * 18
            for x in range(-20, W, 36):
                c.ellipse(x + off + rng.uniform(-3, 3), y, 14, 6, mix((200, 186, 166), (150, 136, 120),
                                                                       rng.uniform(0.15, 0.4)), ol=None)
        return c.img
    return cached("square_bg", make)


def ring_bg():
    """The Ringstrasse: plane trees, a café, the Opera, and Cafe Mitzi at the end (3 x W wide)."""
    def make():
        bw = 3 * W
        c = Canvas(D.gradient(bw * SS, H * SS, [(0, (120, 180, 236)), (0.7, (214, 234, 250)), (1, (214, 234, 250))]),
                   size=(bw, H))
        for x, s in ((300, 0.9), (1300, 0.7), (2300, 1.0), (3300, 0.8)):
            D.cloud(c, x, 100 + (x % 70), s)
        facade(c, 40, 280, 320, (230, 214, 186), base=540, seed=1)
        facade(c, 340, 240, 360, (214, 190, 170), base=540, roof=(90, 110, 120), seed=2)
        facade(c, 600, 300, 300, (240, 224, 196), base=540, seed=3)
        P.opera(c, 1500, 540, 0.75)
        facade(c, 2000, 260, 340, (226, 200, 176), base=540, seed=4)
        facade(c, 2280, 300, 300, (238, 220, 200), base=540, roof=(100, 80, 90), seed=5)
        # Cafe Mitzi: dark wood shop front with a striped awning
        x0 = 2620
        c.rect(x0, 200, x0 + 420, 540, (240, 226, 200), w=3)
        c.rect(x0 + 20, 380, x0 + 400, 540, (90, 50, 36), w=3)
        c.rect(x0 + 40, 400, x0 + 190, 520, (250, 220, 160), w=2.5)
        c.rect(x0 + 230, 400, x0 + 380, 520, (250, 220, 160), w=2.5)
        for k in range(3):
            P.slice_cake(c, x0 + 80 + k * 40, 512, 0.5, plate=False)
        for k in range(10):
            col = (200, 40, 50) if k % 2 == 0 else (255, 250, 240)
            c.poly([(x0 + 10 + k * 40, 330), (x0 + 50 + k * 40, 330), (x0 + 54 + k * 40, 372), (x0 + 14 + k * 40, 372)],
                   col, w=2)
        c.rect(x0 + 60, 250, x0 + 360, 310, (40, 30, 30), w=3, r=8)
        c.text(x0 + 210, 280, "CAFÉ MITZI", 30, P.GOLD)
        facade(c, 3060, 300, 330, (226, 210, 190), base=540, seed=6)
        # pavement + road
        c.rect(0, 540, bw, 580, (200, 196, 190), ol=None)
        c.line([(0, 540), (bw, 540)], OUT, 2.5, cap=False)
        c.rect(0, 580, bw, H, (130, 128, 132), ol=None)
        c.line([(0, 580), (bw, 580)], OUT, 2, cap=False)
        for x in range(0, bw, 26):
            c.line([(x, 590), (x - 12, H)], (120, 118, 122), 1.5, cap=False)
        # the tram rails
        for y in (612, 628):
            c.line([(0, y), (bw, y)], (100, 100, 110), 3, cap=False)
        # plane trees along the Ring
        for x in range(120, bw, 420):
            D.tree(c, x, 560, 1.0, leaf=(110, 170, 90))
        return c.img
    return cached("ring_bg", make)


def tram(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-260, -160, 260, -20, (220, 40, 50), w=3, r=16)
    c.rect(-260, -100, 260, -70, (250, 250, 246), ol=None)
    c.line([(-258, -100), (258, -100)], OUT, 2, cap=False)
    for k in range(7):
        c.rect(-236 + k * 70, -148, -186 + k * 70, -106, (160, 200, 230), w=2, r=4)
    c.line([(0, -160), (-40, -230)], OUT, 3)
    c.line([(-60, -230), (-20, -230)], OUT, 3)
    for wx in (-180, 180):
        c.circle(wx, -18, 18, (50, 46, 54), w=2.5)
    c.pop()


def city(tl, t):
    T = tl.t
    if t < T("c_ride"):
        c = Canvas(square_bg().copy())
        # the bass case on the cobbles (just unloaded)
        open_k = ease(tl.prog("c_tumble", t, 0.05, 0.2))
        P.bass_lid(c, 330, 660, 0.9, 0.9 * open_k)
        P.bass_case(c, 330, 660, 0.9, 0.9 * open_k)
        if t < T("c_tumble", 0.12):
            P.bass_case(c, 330, 660, 0.9, 0.0)
            jig = 3 * math.sin(t * 30) if T("c_narr", 0.6) <= t else 0
            if jig:
                c.text(330, 560, "!", 40, (255, 255, 255), stroke=3)
        # the cats tumble out, then stand facing the Fiaker
        for who, x_end, dt in (("luna", 240, 0.0), ("whiskers", 450, 0.08)):
            u = tl.prog("c_tumble", t, 0.12 + dt, 0.3 + dt)
            if t < T("c_tumble", 0.12 + dt):
                continue
            if u < 1:
                kat(c, tl, t, who, lerp(330, x_end, u), lerp(620, 680, u) + arc(u, 120), 0.85, 1, "leap",
                    eyes="wide")
            else:
                pose = "sit" if T("c_ferd") <= t else "stand"
                kat(c, tl, t, who, x_end, 680, 0.85, 1, pose, eyes="wide" if t < T("c_ferd") else "open",
                    look=(1, -0.6))
        # the Fiaker arrives from the right
        u = ease(tl.prog("c_tumble", t, 0.35, 0.9))
        fx = lerp(1900, 1080, u)
        moving = 0 < u < 1
        c.push(fx, 690, 0.8, flip=True)
        P.fiaker(c, 0, 0, 1.0, t, wheel_ang=-fx / 40)
        c.pop()
        hx = fx - 330 * 0.8
        ferdinand(c, tl, t, hx, 690, 0.8, -1, walk=fx / 30 if moving else 0.0,
                  bow=ease(tl.prog("c_ferd", t, 0.3, 0.6)) * (1 - ease(tl.prog("c_ferd", t, 0.8, 1.0))),
                  head_dy=0)
        return finish(c, tl, t)
    # ---------------- the ride round the Ring
    camk = [(T("c_ride"), 0), (T("c_opera"), 900), (T("c_opera", 1), 1200), (T("c_smell", 1), 2560)]
    camx = etrack(t, camk) if t < T("c_opera") else track(t, camk)
    c = Canvas(ring_bg().crop((int(camx * SS), 0, int(camx * SS) + W * SS, H * SS)))
    c.push(-camx, 0)
    # a red tram rolls the other way
    tx = 3600 - (t - T("c_ride")) * 260
    tram(c, tx, 640, 0.8)
    fx = camx + 380 + 40 * math.sin(t * 0.7)
    stop = t >= T("c_smell", 0.6)

    def seat(cc):
        kat(cc, tl, t, "luna", -128, -110, 0.75, 1, "sit", look=(1, -0.5) if t < T("c_opera", 1) else (1, 0),
            eyes="happy" if T("c_opera") <= t < T("c_opera", 1) else "open")
        sniff = T("c_smell", 0.6) <= t
        kat(cc, tl, t, "whiskers", -60, -110, 0.75, 1, "sit", eyes="closed" if sniff else "open",
            head_dy=-8 if sniff else 0, look=(1, -0.3))
    P.fiaker(c, fx, 690, 0.8, t, wheel_ang=fx / 40 if not stop else 0, seat=seat)
    ferdinand(c, tl, t, fx + 330 * 0.8, 690, 0.8, 1, walk=fx / 30)
    if t >= T("c_smell", 0.5):
        for k in range(3):
            u = ((t * 0.5) + k / 3) % 1.0
            pts = [(lerp(camx + 1000, fx - 30, v), lerp(430, 540, v) + 10 * math.sin(v * 9 + t * 3 + k * 2))
                   for v in np.linspace(max(0, u - 0.35), u, 7)]
            c.line(pts, (150, 100, 70), 3)
    return finish(c, tl, t)


# ====================================================================== cafe

def cafe_bg():
    def make():
        wall = (150, 96, 62)
        c = Canvas(bg=wall)
        # wood panels + gilded mirrors
        c.rect(0, 0, W, 60, (110, 66, 44), ol=None)
        for x in range(0, W, 160):
            c.rect(x + 10, 360, x + 150, 520, (130, 80, 50), w=2.5)
            c.rect(x + 22, 372, x + 138, 508, (140, 88, 56), ol=None)
        for x in (60, 360):
            c.rect(x, 90, x + 220, 330, P.GOLD, w=3, r=10)
            c.rect(x + 12, 102, x + 208, 318, (190, 200, 210), ol=None)
            c.line([(x + 40, 300), (x + 120, 120)], (220, 230, 236), 6)
            c.line([(x + 80, 310), (x + 160, 130)], (220, 230, 236), 3)
        # window with "Café" lettering and the street
        c.rect(640, 80, 860, 340, (60, 40, 30), w=3)
        c.rect(652, 92, 848, 328, (200, 226, 246), ol=None)
        c.rect(652, 250, 848, 328, (200, 196, 190), ol=None)
        D.tree(c, 760, 300, 0.5, leaf=(110, 170, 90))
        c.line([(750, 92), (750, 328)], (60, 40, 30), 5, cap=False)
        c.text(750, 140, "Café", 30, P.GOLD, stroke=1.5)
        # newspapers on wooden holders
        for k in range(3):
            x = 520 + k * 26
            c.line([(x, 140), (x, 250)], (90, 56, 40), 4)
            c.rect(x - 10, 150, x + 10, 244, (236, 232, 218), w=1.5)
        # floor: black and white tiles
        c.rect(0, 520, W, H, (230, 226, 216), ol=None)
        for row, y in enumerate(range(520, H, 40)):
            for k, x in enumerate(range(-40, W + 40, 80)):
                if (k + row) % 2 == 0:
                    c.rect(x + (row % 2) * 0, y, x + 80, y + 40, (60, 56, 60), ol=None)
        c.line([(0, 520), (W, 520)], OUT, 3, cap=False)
        # the cake counter + glass cabinet (right)
        c.rect(900, 300, 1270, 440, (210, 230, 240), w=3, r=6)
        for k, f in enumerate((P.sachertorte, P.strudel, P.sachertorte)):
            f(c, 960 + k * 110, 410, 0.55)
        for k in range(4):
            P.slice_cake(c, 950 + k * 90, 340, 0.55)
        c.line([(905, 370), (1265, 370)], (160, 190, 210), 3, cap=False)
        c.rect(890, 440, 1280, 540, (110, 60, 40), w=3)
        c.rect(890, 440, 1280, 456, (246, 244, 240), w=2.5)
        for x in range(910, 1270, 80):
            c.rect(x, 470, x + 60, 528, (130, 76, 50), w=2)
        return c.img
    return cached("cafe_bg", make)


def cafe(tl, t):
    T = tl.t
    c = cam(cafe_bg(), 800, 452, 1.35)
    P.chandelier(c, 610, 250, 0.7, t)
    TX, TY = 610, 640
    WX, LX = 750, 470          # Whiskers' and Luna's seats
    MX0, MX1 = 1080, 900       # Mitzi behind the counter / at the table
    to_table = tl.prog("f_slow", t, 0.3, 1.0)
    back = tl.prog("f_bye", t, 0.25, 1.0)
    at_counter = t < T("f_slow", 0.3) or (t >= T("f_bye", 0.25) and back >= 1)
    if at_counter:
        mitzi(c, tl, t, MX0, 470, 0.95, -1, arm=0.7 if T("f_mitzi") <= t < T("f_mitzi", 1) else 0.3,
              eyes="happy" if t >= T("f_bye") else "open",
              mouth=laughing(t) * 0.6 if T("f_bye") <= t < T("f_bye", 0.3) else tl.mouth("mitzi", t))
    # counter front over Mitzi's legs
    c.rect(890, 440, 1280, 540, (110, 60, 40), w=3)
    c.rect(890, 440, 1280, 456, (246, 244, 240), w=2.5)
    for x in range(910, 1270, 80):
        c.rect(x, 470, x + 60, 528, (130, 76, 50), w=2)
    if at_counter:
        P.cream_can(c, 1210, 436, 0.8)
    P.coffee_cup(c, 940, 436, 0.8, t)
    # chairs
    P.bentwood_chair(c, LX - 40, 662, 1.0, 1)
    P.bentwood_chair(c, WX + 40, 662, 1.0, -1)
    # the cats on their chairs
    eat = T("f_eat") <= t < T("f_eat", 1)
    chew = eat and math.sin(t * 6) > -0.3
    buried = clamp(tl.prog("f_cream", t, 0.3, 0.75))
    kat(c, tl, t, "luna", LX, 612, 0.95, 1, "sit",
        eyes="wide" if T("f_eat", 0.5) <= t < T("f_slow", 1) or T("f_cream", 0.4) <= t < T("f_cream", 0.8) else
        ("happy" if T("f_purpose") <= t else "open"),
        mouth=laughing(t) * 0.5 if T("f_purpose", 0.6) <= t < T("f_end") and not tl.talking("luna", t) else
        tl.mouth("luna", t))
    if buried < 0.9:
        kat(c, tl, t, "whiskers", WX, 612, 0.95, -1, "sit",
            eyes="happy" if eat else ("wide" if T("f_cream") <= t else "open"),
            mouth=(0.3 + 0.3 * math.sin(t * 14)) if chew else tl.mouth("whiskers", t), head_dy=8 if eat else 0)
    # the table and its cakes
    P.marble_table(c, TX, TY + 20, 1.1)
    top = TY + 20 - 72 * 1.1
    n_plates = int(clamp(tl.prog("f_eat", t, 0.05, 0.95)) * 9) if t < T("f_eat", 1) else 9
    if t >= T("f_eat"):
        for k in range(n_plates):
            c.ellipse(TX + 50, top - 4 - k * 7, 30, 6, (250, 250, 246), w=2)
    if t < T("f_eat"):
        if t >= T("f_yes"):
            P.sachertorte(c, TX - 10, top - 2, 0.6)
    elif t < T("f_eat", 1):
        u = tl.prog("f_eat", t) * 9 % 1.0
        food = [P.sachertorte, P.strudel][int(tl.prog("f_eat", t) * 9) % 2]
        food(c, TX + 10 + 40 * u, top - 2, 0.6 * (1 - 0.7 * u))
    else:
        P.slice_cake(c, TX, top - 2, 0.9)
    P.coffee_cup(c, TX - 50, top - 2, 0.8, t)
    # Mitzi comes over with the whipped cream
    if not at_counter:
        if t < T("f_cream"):
            mx = lerp(MX0, MX1, ease(to_table))
        elif t < T("f_bye", 0.25):
            mx = MX1
        else:
            mx = lerp(MX1, MX0, ease(back))
        walking = (0 < to_table < 1 and t < T("f_cream")) or 0 < back < 1
        face = 1 if (0 < back < 1) else -1
        mitzi(c, tl, t, mx, 650, 0.95, face, step=t * 9 if walking else 0, arm=1.0 if not walking else 0.4,
              eyes="happy" if T("f_purpose") <= t else "open",
              mouth=laughing(t) * 0.6 if T("f_purpose", 0.5) <= t < T("f_bye") else tl.mouth("mitzi", t))
        if face < 0:
            hx = mx - 52 * 0.95
            squirt = T("f_cream", 0.05) <= t < T("f_cream", 0.6)
            P.cream_can(c, hx, 650 - 96 * 0.95, 0.9, ang=1.9 if squirt else 0.3)
            if squirt:
                for k in range(8):
                    u = ((t * 3) + k / 8) % 1.0
                    c.circle(lerp(hx - 50, WX + 10, u), lerp(540, 500, u) + 10 * math.sin(k * 3 + t * 9), 7,
                             P.CREAM_W, w=1.5)
    # the cream mountain on Whiskers
    if buried > 0:
        P.cream_heap(c, WX, 616, 1.3, buried)
        if t >= T("f_purpose"):
            c.push(WX, 612, 0.95, flip=True)
            D._head(c, 18, -96, D.WHISKERS, D.WHISKERS["body"], D.WHISKERS["dark"], D.WHISKERS["belly"],
                    tl.mouth("whiskers", t), "open" if t < T("f_bye") else "happy", (1, 0), t)
            c.pop()
            P.cream_heap(c, WX - 14, 616 - 150, 0.55, 1.0)
    return finish(c, tl, t)


# ==================================================================== prater

PR_Y = 640


def prater_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 170, 236)), (0.6, (200, 226, 248)), (1, (210, 232, 248))]))
        D.cloud(c, 200, 120, 0.8)
        D.cloud(c, 560, 70, 0.6)
        # distant fun-fair
        for x, w, h, col in ((40, 120, 80, (250, 210, 120)), (180, 90, 110, (240, 140, 140)),
                             (1120, 140, 90, (160, 200, 240))):
            c.rect(x, 470 - h, x + w, 470, col, w=2.5)
            for k in range(int(w // 20)):
                c.poly([(x + k * 20, 470 - h), (x + k * 20 + 10, 470 - h - 16), (x + k * 20 + 20, 470 - h)],
                       (220, 60, 70) if k % 2 else (255, 250, 240), w=1.5)
        # carousel
        cx = 320
        c.rect(cx - 70, 400, cx + 70, 470, (255, 240, 220), w=2.5)
        c.poly([(cx - 90, 400), (cx, 340), (cx + 90, 400)], (220, 60, 70), w=2.5)
        for k in range(5):
            c.line([(cx - 60 + k * 30, 400), (cx - 60 + k * 30, 470)], P.GOLD, 2, cap=False)
        c.rect(0, 470, W, H, (120, 186, 96), ol=None)
        c.line([(0, 470), (W, 470)], (80, 140, 70), 3, cap=False)
        for x in (60, 480, 1240):
            D.tree(c, x, 500, 0.9, leaf=(90, 160, 80))
        # gravel dance floor
        c.ellipse(500, 640, 420, 70, (226, 210, 170), w=2.5)
        for k in range(40):
            a = k * 2.4
            c.circle(500 + math.cos(a) * 380 * ((k * 37) % 10) / 10, 640 + math.sin(a) * 60 * ((k * 53) % 10) / 10, 2,
                     (190, 176, 140), ol=None)
        for x in (90, 900):
            D.bush(c, x, 560, 0.8)
        for x, col in ((60, (230, 80, 90)), (100, (250, 200, 80)), (930, (200, 120, 230)), (980, (230, 80, 90))):
            D.flower(c, x, 580, col, 1.0)
        return c.img
    return cached("prater_bg", make)


def city_view():
    """Vienna at sunset, seen from high up in the Ferris wheel (taller than the frame: it slides down)."""
    def make():
        hh = 1100
        c = Canvas(D.gradient(W * SS, hh * SS, [(0, (60, 60, 130)), (0.25, (190, 110, 150)), (0.42, (255, 170, 120)),
                                                (0.55, (255, 214, 150)), (1, (255, 214, 150))]), size=(W, hh))
        c.circle(980, 500, 60, (255, 236, 160), ol=None)
        c.glow(980, 500, 160, 160, (255, 220, 150), (255, 180, 130), steps=6)
        base = 680
        c.tint = ((240, 160, 140), 0.4)
        for k, x in enumerate(range(-20, W + 40, 70)):
            h = 60 + (k * 37) % 70
            c.rect(x, base - h, x + 64, hh, (200, 160, 150), w=2)
        P.stephansdom(c, 520, base - 20, 0.42)
        karlskirche(c, 880, base - 10, 0.45)
        P.opera(c, 250, base, 0.3)
        c.tint = ((200, 120, 130), 0.25)
        for k, x in enumerate(range(-30, W + 40, 90)):
            h = 120 + (k * 53) % 90
            col = [(220, 170, 150), (200, 150, 160), (230, 190, 160)][k % 3]
            c.rect(x, base + 140 - h, x + 84, hh, col, w=2)
            c.poly([(x - 4, base + 140 - h), (x + 42, base + 110 - h), (x + 88, base + 140 - h)], (140, 80, 90), w=2)
            for wy in range(base + 160 - h, hh - 10, 46):
                for wx in range(x + 12, x + 74, 26):
                    c.rect(wx, wy, wx + 14, wy + 22, (255, 220, 140) if (wx + wy) % 3 else (120, 100, 130), w=1)
        for x in range(20, W, 140):
            D.tree(c, x, hh - 40, 0.6, leaf=(110, 150, 90))
        c.tint = None
        return c.img
    return cached("city_view", make)


def cabin_frame():
    def make():
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img)
        red = (200, 40, 46)
        c.rect(-10, -10, W + 10, 70, red, w=3)
        c.rect(-10, 560, W + 10, H + 10, red, w=3)
        c.rect(-10, -10, 80, H + 10, red, w=3)
        c.rect(1200, -10, W + 10, H + 10, red, w=3)
        for x in (420, 860):
            c.rect(x - 14, 60, x + 14, 570, red, w=3)
        c.rect(70, 60, 1210, 80, (170, 30, 40), ol=None)
        # bench
        c.rect(180, 600, 1100, 640, (130, 76, 50), w=3, r=6)
        c.rect(200, 640, 220, H + 10, (110, 60, 40), w=2)
        c.rect(1060, 640, 1080, H + 10, (110, 60, 40), w=2)
        return img
    return cached("cabin_frame", make)


def prater(tl, t):
    T = tl.t
    if t >= T("p_ride"):
        return prater_ride(tl, t)
    c = Canvas(prater_bg().copy())
    P.riesenrad(c, 930, 230, 210, rot=t * 0.04, t=t)
    P.fountain(c, 1110, 680, 0.8, t)
    # --- Ferdinand
    demo = T("p_demo") <= t < T("p_demo", 1)
    if demo:
        u = tl.prog("p_demo", t)
        ang = u * math.tau * 1.0
        fx = 640 + 140 * math.sin(ang)
        fy = 610 + 20 * math.cos(ang)
        face = 1 if math.cos(ang) > 0 else -1
        ferdinand(c, tl, t, fx, fy, 0.85, face, prance=1.0, walk=t * 9, eyes="happy")
        P.music_notes(c, fx, fy - 260, t, T("p_demo"), n=4, col=(255, 236, 170))
    else:
        count = T("p_123") <= t < T("p_123", 1)
        laugh = T("p_trip", 0.8) <= t < T("p_laugh")
        ferdinand(c, tl, t, 680 if t < T("p_trip") else 560, 610, 0.85, -1 if t < T("p_whoops") else 1, prance=0.6 if count else 0.0,
                  walk=t * 9 if count else 0.0, eyes="wide" if T("p_trip") <= t < T("p_trip", 0.8) else "open",
                  bow=0.3 if T("p_laugh") <= t else 0)
    # --- the cats
    if t < T("p_demo", 0.55):
        watch = demo
        kat(c, tl, t, "luna", 250, 660, 1.0, 1, "sit", eyes="happy" if watch else "open", look=(1, -0.5))
        kat(c, tl, t, "whiskers", 390, 670, 1.0, 1, "sit", eyes="wide" if watch else "open", look=(1, -0.5))
    elif t < T("p_trip"):
        # their own first waltz: wobbly
        u = tl.prog("p_demo", t, 0.55, 1.0) if t < T("p_whoops") else 1.0
        ang = (t - T("p_demo", 0.55)) * math.tau / (2.4 * BAR)
        if T("p_whoops") <= t:
            ang = (T("p_whoops") - T("p_demo", 0.55)) * math.tau / (2.4 * BAR) + 0.3 * math.sin(t * 9)
        ouch = T("p_whoops", 0.3) <= t < T("p_whoops", 0.6)
        couple(c, tl, t, 340, 672, 0.95, ang,
               dict(who="whiskers", arm=0.9, eyes="closed" if T("p_whoops") <= t else "open", lean=8),
               dict(who="luna", arm=0.9, eyes="wide" if ouch else "open", legs_up=1.0 if ouch else 0.0),
               step=t * 5)
    else:
        # Whiskers tumbles across the lawn into the fountain
        u = tl.prog("p_trip", t, 0.0, 0.75)
        if u < 1:
            # three bounces
            k = min(2, int(u * 3))
            uu = u * 3 - k
            x = lerp(380, 1060, u)
            y = 670 + arc(uu, 80 - 18 * k) - (30 * u if k == 2 else 0)
            kat(c, tl, t, "whiskers", x, y, 0.95, 1, "leap" if k < 2 else "leap", eyes="wide", mouth=0.6,
                squash=0.8 + 0.2 * math.sin(uu * math.pi))
        elif t < T("p_ride"):
            wet_sit = t >= T("p_trip", 0.88)
            if wet_sit:
                kat(c, tl, t, "whiskers", 1010, 700, 1.0, -1, "sit", wet=1.0, eyes="closed" if t < T("p_laugh") else
                    "open", head_dy=10)
            else:
                kat(c, tl, t, "whiskers", 1090, 680, 0.9, -1, "swim", wet=1.0, eyes="wide")
        if T("p_trip", 0.75) <= t < T("p_trip", 0.95):
            for k in range(10):
                a = k * 0.6
                uu = tl.prog("p_trip", t, 0.75, 0.95)
                c.circle(1090 + math.cos(a) * 90 * uu, 650 - math.sin(a) * 120 * uu + 160 * uu * uu, 6,
                         (180, 220, 250), w=1.5)
        kat(c, tl, t, "luna", 330 + 560 * ease(tl.prog("p_trip", t, 0.6, 1.0)), 680, 1.0, 1,
            "walk" if 0 < tl.prog("p_trip", t, 0.6, 1.0) < 1 else "sit",
            walk=t * 10, eyes="wide" if t < T("p_laugh") else "open")
    return finish(c, tl, t)


def prater_ride(tl, t):
    T = tl.t
    rise = ease(tl.prog("p_ride", t, 0.0, 0.85))
    view = city_view()
    oy = lerp(380, 130, rise) + 4 * math.sin(t * 0.8)
    c = Canvas(view.crop((0, int(oy * SS), W * SS, int(oy * SS) + H * SS)))
    # sun sinking in p_sunset
    k = tl.prog("p_sunset", t)
    if k > 0:
        c.tint = None
    # passing spokes of the wheel outside the window
    for j in range(3):
        x = (j * 520 + (t - T("p_ride")) * 30) % 1600 - 160
        c.line([(x, -10), (x + 300, H + 10)], (60, 64, 76), 5)
    fr = cabin_frame()
    c.img.paste(fr, (0, 0), fr)
    # the cats on the bench, side by side looking out
    sad = T("p_ride") <= t < T("p_brave")
    snug = t >= T("p_brave", 0.6)
    lean = 30 * ease(tl.prog("p_brave", t, 0.6, 1.0))
    kat(c, tl, t, "luna", 520 + lean, 610, 1.4, 1, "sit", eyes="happy" if snug else "open",
        look=(1, -0.2) if not T("p_sad") <= t < T("p_brave", 1) else (1, 0), head_dy=4 if sad else 0)
    kat(c, tl, t, "whiskers", 790, 612, 1.4, -1 if T("p_sad") <= t else 1, "sit", wet=0.3 * (1 - rise),
        eyes="happy" if snug else ("closed" if T("p_ride") <= t < T("p_ride", 0.5) else "open"),
        head_dy=10 if T("p_ride") <= t < T("p_sad") else 0)
    if snug:
        hearts(c, 660, 380, t, T("p_brave", 0.7), n=4)
    return finish(c, tl, t)


# ==================================================================== palace

def palace_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (50, 50, 120)), (0.35, (150, 90, 150)), (0.6, (250, 150, 120)),
                                               (1, (250, 180, 140))]))
        D.stars(c, 9, 40, W, 160)
        # the Gloriette on its hill
        c.poly([(-20, 330), (300, 230), (640, 170), (980, 230), (1300, 330), (1300, 470), (-20, 470)], (70, 100, 90),
               ol=None)
        c.tint = ((200, 140, 160), 0.3)
        P.gloriette(c, 640, 182, 0.75)
        c.tint = None
        P.palace(c, 640, 470, 0.88, lit=1.0)
        # parterre gardens
        c.rect(0, 470, W, H, (90, 130, 80), ol=None)
        c.line([(0, 470), (W, 470)], OUT, 2.5, cap=False)
        c.poly([(560, 470), (720, 470), (900, H), (380, H)], (226, 206, 170), ol=None)
        for sx in (-1, 1):
            for k in range(3):
                y0 = 490 + k * 70
                x0 = 640 + sx * (140 + k * 60)
                x1 = 640 + sx * (560 + k * 80)
                c.poly([(x0, y0), (x1, y0), (x1 + sx * 30, y0 + 50), (x0 + sx * 30, y0 + 50)], (70, 120, 70), w=2)
                for j in range(4):
                    fx = lerp(x0, x1, (j + 0.5) / 4) + sx * 15
                    c.circle(fx, y0 + 25, 9, [(240, 90, 110), (250, 210, 90), (200, 130, 230)][(j + k) % 3], w=1.5)
        for x in (60, 160, 1120, 1220):
            P.hedge_cone(c, x, 520, 1.0)
        P.fountain(c, 640, 560, 0.6, 0.0, water=False)
        return c.img
    return cached("palace_bg", make)


# ---- the maze (top-down, slightly oblique)

MZ_COLS, MZ_ROWS = 15, 9
MZ_X0, MZ_Y0 = 0, 112
MZ_CW, MZ_CH = W / MZ_COLS, (H - MZ_Y0) / MZ_ROWS
HEDGE_H = 26


def maze_grid():
    def make():
        nc, nr = (MZ_COLS - 1) // 2, (MZ_ROWS - 1) // 2
        grid = np.ones((MZ_ROWS, MZ_COLS), bool)       # True = hedge
        rng = np.random.default_rng(12)
        seen = np.zeros((nr, nc), bool)
        stack = [(nr - 1, nc // 2)]
        seen[stack[0]] = True
        grid[2 * stack[0][0] + 1, 2 * stack[0][1] + 1] = False
        while stack:
            r, cc = stack[-1]
            nbs = [(r + dr, cc + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                   if 0 <= r + dr < nr and 0 <= cc + dc < nc and not seen[r + dr, cc + dc]]
            if not nbs:
                stack.pop()
                continue
            nr2, nc2 = nbs[rng.integers(len(nbs))]
            seen[nr2, nc2] = True
            grid[2 * nr2 + 1, 2 * nc2 + 1] = False
            grid[r + nr2 + 1, cc + nc2 + 1] = False
            stack.append((nr2, nc2))
        entry = (MZ_ROWS - 1, 2 * (nc // 2) + 1)
        exit_ = (0, 2 * (nc // 2) + 1)
        grid[entry] = False
        grid[exit_] = False
        return grid, entry, exit_
    return cached("maze_grid", make)


def maze_bfs(grid, a, b):
    from collections import deque
    prev = {a: None}
    q = deque([a])
    while q:
        p = q.popleft()
        if p == b:
            break
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (p[0] + dr, p[1] + dc)
            if 0 <= n[0] < MZ_ROWS and 0 <= n[1] < MZ_COLS and not grid[n] and n not in prev:
                prev[n] = p
                q.append(n)
    path, p = [], b
    while p is not None:
        path.append(p)
        p = prev[p]
    return path[::-1]


def maze_routes():
    def make():
        grid, entry, exit_ = maze_grid()
        # the dead end furthest from the exit, among cells reachable early
        best, best_len = None, -1
        for r in range(1, MZ_ROWS, 2):
            for cc in range(1, MZ_COLS, 2):
                if grid[r, cc]:
                    continue
                n_open = sum(not grid[r + dr, cc + dc] for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if n_open != 1:
                    continue
                d1 = len(maze_bfs(grid, entry, (r, cc)))
                d2 = len(maze_bfs(grid, (r, cc), exit_))
                if d2 + min(d1, 20) > best_len and d1 < 40:
                    best, best_len = (r, cc), d2 + min(d1, 20)
        lost = maze_bfs(grid, entry, best)
        out = maze_bfs(grid, best, exit_)
        return lost, out
    return cached("maze_routes", make)


def cell_xy(rc):
    r, cc = rc
    return MZ_X0 + (cc + 0.5) * MZ_CW, MZ_Y0 + (r + 0.75) * MZ_CH


def path_pos(path, u):
    pts = [cell_xy(p) for p in path] + [cell_xy(path[-1])]
    n = len(path) - 1
    if n <= 0:
        return pts[0], 1
    f = clamp(u) * n
    i = min(n - 1, int(f))
    a, b = pts[i], pts[i + 1]
    k = f - i
    face = 1 if b[0] > a[0] + 1 else (-1 if b[0] < a[0] - 1 else 0)
    return (lerp(a[0], b[0], k), lerp(a[1], b[1], k)), face


def maze_layers():
    """Background (sky strip + gravel) and per-row hedge strips (RGBA) for occlusion."""
    def make():
        grid, entry, exit_ = maze_grid()
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (40, 40, 100)), (0.12, (160, 100, 150)), (0.2, (230, 150, 120)),
                                               (1, (230, 150, 120))]))
        P.palace(c, 640, MZ_Y0 + 10, 0.45, lit=1.0)
        c.rect(0, MZ_Y0, W, H, (214, 196, 160), ol=None)
        rows = []
        for r in range(MZ_ROWS):
            img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
            rc = Canvas(img)
            for cc in range(MZ_COLS):
                if not grid[r, cc]:
                    continue
                x0 = MZ_X0 + cc * MZ_CW
                y0 = MZ_Y0 + r * MZ_CH
                rc.rect(x0 - 1, y0 - HEDGE_H + MZ_CH * 0.35, x0 + MZ_CW + 1, y0 + MZ_CH, (50, 100, 56), ol=None)
                rc.rect(x0 - 1, y0 - HEDGE_H, x0 + MZ_CW + 1, y0 + MZ_CH * 0.35, (90, 160, 90), ol=None)
                for k in range(3):
                    rc.circle(x0 + MZ_CW * (0.2 + 0.3 * k), y0 - HEDGE_H + 10 + 6 * (k % 2), 7, (110, 180, 100),
                              ol=None)
            # outlines between hedge and gravel
            for cc in range(MZ_COLS):
                if not grid[r, cc]:
                    continue
                x0 = MZ_X0 + cc * MZ_CW
                y0 = MZ_Y0 + r * MZ_CH
                if r + 1 >= MZ_ROWS or not grid[r + 1, cc]:
                    rc.line([(x0, y0 + MZ_CH), (x0 + MZ_CW, y0 + MZ_CH)], OUT, 2.5, cap=False)
                if cc == 0 or not grid[r, cc - 1]:
                    rc.line([(x0, y0 - HEDGE_H), (x0, y0 + MZ_CH)], OUT, 2.5, cap=False)
                if cc + 1 >= MZ_COLS or not grid[r, cc + 1]:
                    rc.line([(x0 + MZ_CW, y0 - HEDGE_H), (x0 + MZ_CW, y0 + MZ_CH)], OUT, 2.5, cap=False)
                if r == 0 or not grid[r - 1, cc]:
                    rc.line([(x0, y0 - HEDGE_H), (x0 + MZ_CW, y0 - HEDGE_H)], OUT, 2.5, cap=False)
            rows.append(img)
        return c.img, rows
    return cached("maze_layers", make)


def palace(tl, t):
    T = tl.t
    if t < T("pa_maze"):
        c = Canvas(palace_bg().copy())
        u = ease(tl.prog("pa_narr", t, 0.0, 1.0) * 0.6 + tl.prog("pa_arrive", t, 0.0, 0.5) * 0.4)
        fx = lerp(-700, 520, u)
        moving = 0 < u < 1

        def seat(cc):
            if t < T("pa_arrive", 0.6):
                kat(cc, tl, t, "luna", -128, -110, 0.75, 1, "sit", look=(1, -0.6), eyes="happy")
                kat(cc, tl, t, "whiskers", -60, -110, 0.75, 1, "sit", look=(1, -0.6))
        P.fiaker(c, fx, 700, 0.8, t, wheel_ang=fx / 40, seat=seat)
        ferdinand(c, tl, t, fx + 330 * 0.8, 700, 0.8, 1, walk=fx / 30 if moving else 0.0)
        if t >= T("pa_arrive", 0.6):
            hop = tl.prog("pa_arrive", t, 0.6, 0.9)
            lx = lerp(fx - 100, 220, hop)
            wx = lerp(fx - 50, 330, hop)
            if hop < 1:
                kat(c, tl, t, "luna", lx, 690 + arc(hop, 90), 0.8, -1, "leap")
                kat(c, tl, t, "whiskers", wx, 690 + arc(hop, 110), 0.8, -1, "leap")
            else:
                point = T("pa_short") <= t
                kat(c, tl, t, "luna", 220, 690, 0.8, 1 if not point else -1, "stand", eyes="open")
                kat(c, tl, t, "whiskers", 330 + (0 if not point else -40 * ease(tl.prog("pa_short", t, 0.5, 1))), 690, 0.8,
                    -1 if point else 1, "stand" if not point else "walk", walk=t * 8 if point else 0,
                    eyes="happy" if point else "open")
        return finish(c, tl, t)
    # ---- inside the maze
    bg, rows = maze_layers()
    c = Canvas(bg.copy())
    lost, out = maze_routes()
    if t < T("pa_lost"):
        u = tl.prog("pa_maze", t, 0.0, 1.0)
        wpos, wf = path_pos(lost, u)
        lpos, lf = path_pos(lost, u - 0.08)
        moving = True
    elif t < T("pa_sniff", 0.4):
        wpos, wf = path_pos(lost, 1.0)
        lpos, lf = path_pos(lost, 0.92)
        moving = False
    else:
        u = tl.prog("pa_out", t, 0.0, 0.85) * 0.75 + tl.prog("pa_sniff", t, 0.4, 1.0) * 0.25
        wpos, wf = path_pos(out, u)
        # Luna follows close behind
        lpath = list(lost[-4:]) + list(out[1:]) if len(lost) >= 4 else out
        off = 3.0 / max(1, len(lpath) - 1)
        lpos, lf = path_pos(lpath, (u * (len(out) - 1) + 3) / max(1, len(lpath) - 1) - off)
        moving = 0 < u < 1
    actors = [("whiskers", wpos, wf), ("luna", lpos, lf)]
    s = 0.4
    for r in range(MZ_ROWS):
        c.img.paste(rows[r], (0, 0), rows[r])
        for who, (x, y), f in actors:
            if MZ_Y0 + r * MZ_CH <= y - MZ_CH * 0.75 + 1e-3 < MZ_Y0 + (r + 1) * MZ_CH:
                fc = f if f else (1 if who == "whiskers" else 1)
                sniff = who == "whiskers" and T("pa_sniff") <= t < T("pa_out", 0.2)
                kat(c, tl, t, who, x, y, s, fc, "walk" if moving else ("sit" if sniff else "stand"),
                    walk=(x + y) / (12 * s) if moving else 0, eyes="closed" if sniff else "open",
                    head_dy=-6 if sniff else 0)
    if T("pa_lost") <= t < T("pa_sniff", 0.3):
        for k, (x, y) in enumerate((wpos, lpos)):
            c.text(x + 10, y - 70 - 6 * math.sin(t * 5 + k), "?", 30, (255, 240, 120), stroke=3)
    if T("pa_sniff") <= t:
        x, y = wpos
        for k in range(3):
            uu = ((t * 0.6) + k / 3) % 1.0
            pts = [(x + 10 + 60 * v * math.sin(k + 1), y - 40 - 160 * v) for v in np.linspace(max(0, uu - 0.3), uu, 6)]
            c.line(pts, (150, 100, 70), 2.5)
    c.tint = None
    return finish(c, tl, t)


# ====================================================================== ball

FLOOR_Y = 420


def ball_bg():
    def make():
        wall = (246, 232, 200)
        c = Canvas(bg=wall)
        c.rect(0, 0, W, 50, (230, 206, 150), ol=None)
        c.line([(0, 50), (W, 50)], P.GOLD_D, 3, cap=False)
        # tall windows + mirrors between gilded pilasters
        for k, x in enumerate(range(40, W, 200)):
            c.rect(x - 16, 50, x + 16, FLOOR_Y, (250, 240, 214), w=2.5)
            c.rect(x - 22, 50, x + 22, 72, P.GOLD, w=2)
            c.rect(x - 22, FLOOR_Y - 20, x + 22, FLOOR_Y, P.GOLD, w=2)
        for k, x in enumerate(range(140, W, 200)):
            night = k % 2 == 0
            if night:
                P.arch_window(c, x, 390, 120, 300, (40, 50, 110), frame=P.GOLD_D, ww=4)
                c.line([(x, 120), (x, 390)], P.GOLD_D, 3, cap=False)
                c.line([(x - 60, 260), (x + 60, 260)], P.GOLD_D, 3, cap=False)
                for j in range(5):
                    c.circle(x - 44 + j * 22, 160 + (j * 37) % 70, 1.6, (255, 250, 220), ol=None)
            else:
                P.arch_window(c, x, 390, 120, 300, (200, 210, 220), frame=P.GOLD, ww=4)
                c.line([(x - 40, 360), (x + 20, 170)], (230, 236, 240), 6)
            c.ellipse(x, 86, 40, 14, P.GOLD, w=2)
        c.rect(0, FLOOR_Y - 8, W, FLOOR_Y, P.GOLD_D, ol=None)
        # parquet floor in perspective
        c.rect(0, FLOOR_Y, W, H, (200, 140, 80), ol=None)
        for k in range(-12, 13):
            c.line([(640 + k * 60, FLOOR_Y), (640 + k * 150, H)], (176, 118, 64), 2, cap=False)
        for y in (450, 490, 540, 600, 670):
            c.line([(0, y), (W, y)], (176, 118, 64), 2, cap=False)
        # soft shine on the floor
        c.ellipse(640, 560, 400, 70, (214, 156, 96), ol=None)
        c.ellipse(640, 560, 260, 44, (222, 168, 108), ol=None)
        # orchestra stage (left)
        c.poly([(0, 470), (230, 470), (290, 560), (0, 560)], (150, 40, 50), w=3)
        c.rect(0, 556, 300, 572, P.GOLD_D, w=2)
        # countess' dais (right)
        c.poly([(1080, 480), (W + 10, 480), (W + 10, 560), (1050, 560)], (150, 40, 50), w=3)
        c.rect(1100, 330, 1180, 486, P.GOLD, w=3, r=12)
        c.rect(1112, 344, 1168, 440, (170, 40, 60), ol=None)
        return c.img
    return cached("ball_bg", make)


def musicians(c, tl, t, playing, crashed=0.0):
    # violinists: sitting cats with violins (on the stage)
    for k, (x, pal) in enumerate(((50, P.GUESTS[0]), (140, P.GUESTS[3]))):
        D.cat(c, x, 520, pal, 0.55, 1, "sit", t=t, seed=k + 7, eyes="closed" if playing else "open")
        c.push(x, 520, 0.55)
        bow = 10 * math.sin(t * 8 + k) if playing else 0
        c.poly([(20, -66), (60, -76), (66, -62), (26, -54)], (170, 90, 40), w=2)
        c.line([(30, -96 + bow), (80, -40 + bow)], (240, 230, 200), 2.5)
        c.pop()
    # the drum + cymbal at the front of the stage
    dx = 230
    c.ellipse(dx, 560, 40, 12, (240, 240, 236), w=2.5)
    c.rect(dx - 40, 520, dx + 40, 560, (200, 40, 50), w=2.5)
    c.ellipse(dx, 520, 40, 12, (250, 246, 236), w=2.5)
    wob = math.sin(t * 25) * 10 * crashed
    c.line([(dx + 50, 560), (dx + 50, 470)], (90, 90, 100), 3)
    c.push(dx + 50, 470)
    c.poly([(-34, wob * 0.4), (34, -wob * 0.4), (30, 4 - wob * 0.4), (-30, 4 + wob * 0.4)], P.GOLD, w=2)
    c.pop()


GUEST_COUPLES = [(0, 1, 0), (2, 3, 1), (4, 5, 2), (1, 4, 3)]


def guests(c, tl, t, mode, t0=0.0, front=False):
    """Guest couples. mode: 'stand' | 'dance' | 'laugh' | 'clap'."""
    for k, (pa, pb, g) in enumerate(GUEST_COUPLES):
        base_ang = k * math.tau / 4
        if mode == "dance":
            phi = base_ang + (t - t0) * 0.22
        else:
            phi = base_ang + 0.6
        cx = 640 + 400 * math.cos(phi)
        cy = 520 + 50 * math.sin(phi)
        if (cy > 525) != front:
            continue
        s = 0.58 + 0.1 * math.sin(phi)
        a = dict(pal=P.GUESTS[pa], bowtie=(40, 40, 50), arm=0.9, seed=k)
        b = dict(pal=P.GUESTS[pb], gown=P.GOWNS[g], arm=0.9, seed=k + 3)
        if mode == "dance":
            couple(c, tl, t, cx, cy, s, t * math.tau / (2 * BAR) + k, a, b)
        else:
            laugh = mode == "laugh"
            for j, (d, dx, f) in enumerate(((a, -24, 1), (b, 24, -1))):
                d = dict(d)
                if laugh:
                    d.update(eyes="happy", mouth=laughing(t + j + k), arm=0.2, arm2=0.9)
                elif mode == "clap":
                    d.update(eyes="happy", arm=0.5 + 0.4 * abs(math.sin(t * 9 + k)), arm2=0.5 + 0.4 * abs(math.sin(t * 9 + k)))
                else:
                    d.update(arm=0.3)
                P.dancer(c, cx + dx * s * 2, cy, s, f if mode == "stand" else (-1 if cx > 640 else 1), t=t,
                         hop=abs(math.sin(t * 7 + k)) * 4 if laugh else 0, **d)


def window_peek(c, draw_fn, x=540, bottom=390, w=120, h=300):
    """Draw draw_fn(canvas) seen through the arched night window at x (world coords of c)."""
    from PIL import ImageDraw
    x0, y0 = c.P(x - w / 2, bottom - h)
    x1, y1 = c.P(x + w / 2, bottom)
    box = (int(max(0, x0)), int(max(0, y0)), int(min(c.img.size[0], x1)), int(min(c.img.size[1], y1)))
    if box[2] <= box[0] or box[3] <= box[1]:
        return
    sub = c.img.crop(box)
    sc = Canvas(sub)
    ox, oy, sx, sy = c.tf[-1]
    sc.tf = [(ox - box[0] / SS, oy - box[1] / SS, sx, sy)]
    draw_fn(sc)
    P.arch_window(sc, x, bottom, w, h, None, frame=P.GOLD_D, ww=4)
    sc.line([(x, bottom - h + w / 2 - 30), (x, bottom)], P.GOLD_D, 3, cap=False)
    sc.line([(x - w / 2, bottom - 130), (x + w / 2, bottom - 130)], P.GOLD_D, 3, cap=False)
    mask = Image.new("L", sub.size, 0)
    md = ImageDraw.Draw(mask)
    mc = Canvas(mask)
    mc.d = md
    mc.tf = sc.tf
    rx0, ry0 = mc.P(x - w / 2, bottom - h + w / 2)
    rx1, ry1 = mc.P(x + w / 2, bottom)
    md.rectangle([rx0, ry0, rx1, ry1], fill=255)
    ex0, ey0 = mc.P(x - w / 2, bottom - h)
    ex1, ey1 = mc.P(x + w / 2, bottom - h + w)
    md.ellipse([ex0, ey0, ex1, ey1], fill=255)
    c.img.paste(sub, box[:2], mask)


def ball(tl, t):
    T = tl.t
    # camera: close on the cats while they talk
    zk = [(T("ba_oh") - 0.1, 0.0), (T("ba_oh") + 0.9, 1.0), (T("ba_again", 0.6), 1.0), (T("ba_dance2") + 0.4, 0.0),
          (T("ba_more") - 0.6, 0.0), (T("ba_more") - 0.1, 0.7), (T("ba_end", 0.15), 0.7), (T("ba_end", 0.4), 0.0)]
    zz = etrack(t, zk)
    c = cam(ball_bg(), lerp(640, 600, zz), lerp(360, 470, zz), 1 + 0.6 * zz)
    # Ferdinand peeks in at a window during the happy dance
    if T("ba_dance2", 0.4) <= t < T("ba_end", 1):
        k = ease(tl.prog("ba_dance2", t, 0.4, 0.55))
        window_peek(c, lambda cc: ferdinand(cc, tl, t, 380 + 30 * k, 450 + 200 * (1 - k), 0.95, 1, eyes="happy",
                                            mouth=0.3 if T("ba_bravo") <= t < T("ba_cake") else 0.0))
    for x in (300, 640, 980):
        P.chandelier(c, x, 150, 1.0 if x == 640 else 0.8, t)
    dancing1 = T("ba_dance1") <= t < T("ba_dance1", 0.72)
    dancing2 = T("ba_dance2") <= t < T("ba_dance2", 1) or T("ba_end", 0.1) <= t
    playing = dancing1 or dancing2
    crashed = 1.0 - clamp((t - T("ba_dance1", 0.86)) / 1.5) if t >= T("ba_dance1", 0.86) else 0.0
    musicians(c, tl, t, playing, crashed)
    # guests behind
    if dancing1:
        mode, t0 = "dance", T("ba_dance1")
    elif T("ba_dance1", 0.86) <= t < T("ba_oh", 0.5):
        mode, t0 = "laugh", 0
    elif dancing2:
        join = T("ba_dance2", 0.3) <= t
        mode, t0 = ("dance" if join else "stand"), T("ba_dance2")
    elif T("ba_bravo") <= t < T("ba_end", 0.1):
        mode, t0 = "clap", 0
    else:
        mode, t0 = "stand", 0
    guests(c, tl, t, mode, t0, front=False)
    # the Countess on her dais (comes down to dance at the end)
    if t < T("ba_end", 0.1):
        countess(c, tl, t, 1140, 492, 0.75, -1, arm=0.8 if tl.talking("countess", t) else 0.3,
                 eyes="happy" if T("ba_dance2", 0.5) <= t else "open")
    # the cake
    if t >= T("ba_cake"):
        u = ease(tl.prog("ba_cake", t, 0.0, 0.7))
        cx = lerp(1400, 960, u)
        c.rect(cx - 90, 600, cx + 90, 616, (200, 200, 210), w=2.5)
        for wx in (cx - 70, cx + 70):
            c.circle(wx, 630, 12, (60, 60, 70), w=2)
        P.sachertorte(c, cx, 600, 1.4, cut=False)
        if u >= 1:
            for k in range(3):
                a = t * 3 + k * 2.1
                c.circle(cx + 70 * math.cos(a), 520 + 20 * math.sin(a), 3, (255, 250, 200), ol=None)
    # ---- Whiskers and Luna
    CX, CY = 640, 640
    if t < T("ba_dance1"):
        dance(c, tl, t, "luna", 590, CY, 0.95, 1, dressed=True, arm=0.2,
              eyes="happy" if T("ba_count", 0.6) <= t else "open")
        dance(c, tl, t, "whiskers", 700, CY, 0.95, -1, dressed=True, arm=0.2, look=(1, -0.5))
    elif t < T("ba_dance1", 0.72):
        ang = (t - T("ba_dance1")) * math.tau / (2.6 * BAR)
        wobble = 0.25 * math.sin(t * 4)
        couple(c, tl, t, CX + 60 * math.sin(t * 0.5), CY, 0.95, ang + wobble,
               dict(who="whiskers", dressed=True, arm=0.9, eyes="open", look=(0.5, 1)),
               dict(who="luna", dressed=True, arm=0.9, eyes="happy", legs_up=1.0 if math.sin(t * 3) > 0.9 else 0),
               step=t * 5)
    elif t < T("ba_oh"):
        # the slip: Whiskers skids across the floor into the drum
        u = tl.prog("ba_dance1", t, 0.72, 0.86)
        if t < T("ba_dance1", 0.86):
            x = lerp(640, 280, u)
            kat(c, tl, t, "whiskers", x, CY - 10 * math.sin(u * math.pi), 0.9, -1, "leap", eyes="wide", mouth=0.7)
        else:
            # legs sticking out of the drum
            c.push(230, 520)
            c.stroke([(-10, 0), (-30, -40)], D.WHISKERS["body"], 12)
            c.stroke([(10, 0), (24, -44)], D.WHISKERS["body"], 12)
            c.pop()
            dizzy(c, 230, 480, t, 40)
        dance(c, tl, t, "luna", 560, CY, 0.95, -1, dressed=True, arm=0.5, eyes="wide")
    else:
        sad = T("ba_oh") <= t < T("ba_paw", 0.7)
        if t < T("ba_dance2"):
            u = ease(tl.prog("ba_oh", t, 0.0, 0.3))
            kat(c, tl, t, "whiskers", lerp(300, 560, u), CY, 0.95, 1, "sit" if u >= 1 else "walk", walk=t * 8,
                eyes="closed" if sad and t < T("ba_paw") else "open", head_dy=12 if sad else 0, look=(1, 0))
            c.push(lerp(300, 560, u), CY, 0.95)
            c.pop()
            ul = ease(tl.prog("ba_paw", t, 0.0, 0.3))
            dance(c, tl, t, "luna", lerp(700, 680, ul), CY, 0.95, -1, dressed=True,
                  arm=lerp(0.3, 0.8, ul), eyes="happy" if t >= T("ba_paw", 0.5) else "open")
            # Whiskers gets up, takes her paw
            if t >= T("ba_again"):
                pass
        elif t < T("ba_bravo"):
            u = tl.prog("ba_dance2", t)
            ang = (t - T("ba_dance2")) * math.tau / (1.8 * BAR)
            cx = CX + 160 * math.sin(u * math.tau * 1.5)
            cy = CY - 10 * math.cos(u * math.tau * 1.5)
            twirl = 0.45 <= (u * 4) % 1.0 < 0.7
            couple(c, tl, t, cx, cy, 0.95 + 0.05 * math.sin(u * 6), ang,
                   dict(who="whiskers", dressed=True, arm=1.0, arm2=0.9 if twirl else 0.2, eyes="happy",
                        mouth=0.4 if twirl else 0.0, lean=10 * math.sin(t * 3)),
                   dict(who="luna", dressed=True, arm=1.0, arm2=0.9 if twirl else 0.2, eyes="happy",
                        legs_up=1.0 if twirl else 0.0),
                   step=t * 8, sep=52 if not twirl else 68)
            P.music_notes(c, cx, cy - 200, t, T("ba_dance2"), n=5)
        else:
            more = T("ba_more") <= t
            if t < T("ba_end", 0.1):
                dance(c, tl, t, "luna", 560, CY, 0.95, 1, dressed=True, arm=0.4 if not more else 0.9,
                      eyes="happy")
                dance(c, tl, t, "whiskers", 680, CY, 0.95, -1 if t < T("ba_cake") else (1 if t < T("ba_more") else -1),
                      dressed=True, arm=0.9 if more else 0.3, eyes="happy" if t < T("ba_cake") else "open",
                      look=(1, 0.3))
            else:
                ang = (t - T("ba_end")) * math.tau / (1.8 * BAR)
                couple(c, tl, t, CX - 60, CY, 0.95, ang, dict(who="whiskers", dressed=True, arm=1.0, eyes="happy"),
                       dict(who="luna", dressed=True, arm=1.0, eyes="happy"), step=t * 8)
                couple(c, tl, t, 1000, 560, 0.62, ang + 1, dict(who="countess", arm=1.0),
                       dict(pal=P.GUESTS[0], bowtie=(40, 40, 50), arm=1.0))
    guests(c, tl, t, mode, t0, front=True)
    if T("ba_bravo") <= t < T("ba_cake", 0.5):
        P.confetti(c, t, T("ba_bravo"), n=50)
    if T("ba_dance2", 0.6) <= t < T("ba_bravo"):
        P.confetti(c, t, T("ba_dance2", 0.6), n=30, seed=5)
    if T("ba_trip") <= t < T("ba_oh") or T("ba_dance1", 0.86) <= t < T("ba_trip"):
        c.text(230, 420, "CRASH!", 36, (255, 230, 80), stroke=3) if t < T("ba_dance1", 0.95) else None
    return finish(c, tl, t)


# ====================================================================== home

def home(tl, t):
    T = tl.t
    if t < T("h_pip"):
        # the bus drops them off at night, outside the window
        c = Canvas(street_bg(True).copy())
        u = tl.prog("h_open", t, 0.0, 1.0)
        bx = lerp(BUS_X, 1900, ease(tl.prog("h_narr", t, 0.3, 1.0)))
        c.tint = ((20, 20, 60), 0.35)
        P.bus(c, bx, BUS_Y, BUS_S, t, wheel_ang=-bx / 30, lights=True)
        c.tint = ((20, 20, 60), 0.15)
        # the cats walk up to the sill with the cake box
        hop = tl.prog("h_narr", t, 0.0, 0.3)
        for who, x0, x1 in (("luna", 700, 250), ("whiskers", 760, 380)):
            if hop < 1:
                x = lerp(x0, x1, hop)
                kat(c, tl, t, who, x, lerp(560, SILL, hop) + arc(hop, 80), 0.9, -1, "leap")
            else:
                kat(c, tl, t, who, x1, SILL, 0.9, 1, "sit", eyes="happy")
        if hop >= 1:
            c.rect(300, SILL - 46, 352, SILL, (250, 246, 236), w=2.5)
            c.line([(326, SILL - 46), (326, SILL)], (200, 40, 60), 3)
            c.line([(300, SILL - 24), (352, SILL - 24)], (200, 40, 60), 3)
        return finish(c, tl, t)
    # close-up on the sill, under the moon
    bg = street_bg(True)
    z = 2.0
    c = cam(bg, 440, 300, z)
    c.tint = ((20, 20, 60), 0.12)
    dancing = T("h_dance") <= t < T("h_moral", 0.2)
    # Luna with the cake box and a slice
    kat(c, tl, t, "luna", 210, SILL, 0.9, 1, "sit", eyes="happy" if dancing or t >= T("h_moral") else "open")
    c.rect(150, SILL - 40, 196, SILL, (250, 246, 236), w=2)
    c.line([(173, SILL - 40), (173, SILL)], (200, 40, 60), 2.5)
    P.slice_cake(c, 470, SILL - 2, 0.6)
    if dancing:
        u = tl.prog("h_dance", t)
        ang = (t - T("h_dance")) * math.tau / (2 * BAR)
        # Whiskers waltzes with tiny Pip standing on his paw
        cx = 340 + 30 * math.sin(u * math.tau)
        dance(c, tl, t, "whiskers", cx, SILL, 0.75, 1 if math.cos(ang) > 0 else -1, arm=0.7, eyes="happy",
              step=t * 6, hop=4 * abs(math.sin(t * 4)))
        f = 1 if math.cos(ang) > 0 else -1
        D.mouse(c, cx + f * 44, SILL - 64 - 4 * abs(math.sin(t * 4)), 0.9, -f, t, proud=True, eyes="happy",
                hop=0)
        P.music_notes(c, 330, SILL - 160, t, T("h_dance"), n=4, col=(255, 236, 170), s=0.8)
    else:
        end = t >= T("h_moral")
        kat(c, tl, t, "whiskers", 360, SILL, 0.9, -1 if not end else -1, "sit",
            eyes="happy" if end else "open", mouth=tl.mouth("whiskers", t))
        D.mouse(c, 440, SILL, 1.1, -1, t, mouth=tl.mouth("pip", t), proud=T("h_pip") <= t < T("h_pip", 1),
                hop=abs(math.sin(t * 8)) * 8 if T("h_pip") <= t < T("h_pip", 1) else 0,
                eyes="happy" if end else "open")
        if end:
            hearts(c, 300, SILL - 140, t, T("h_moral", 0.3), n=3)
    c.tint = None
    c.tf = [(0.0, 0.0, 1.0, 1.0)]
    k = ease(tl.prog("h_end", t, 0.3, 0.6))
    if k > 0:
        c.text(W / 2, 110, "The End", 30 + 44 * k, mix((40, 40, 90), (255, 236, 180), k), stroke=4 * k,
               stroke_fill=(50, 30, 60))
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "sill": sill, "bus": bus, "city": city, "cafe": cafe, "prater": prater,
               "palace": palace, "ball": ball, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["c_ride", "p_ride", "pa_maze", "h_pip"]
