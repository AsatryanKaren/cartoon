"""Scenes of "Whiskers and the Dancing Lights". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
Static layers are cached; the northern lights are a small numpy field
screen-blended over the sky (and mirrored on the fjord).
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.norway import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "tuva": 3.3, "magnus": 4.4}

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


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def tuva(c, tl, t, x, y, s=1.3, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("tuva", t))
    P.puffin(c, x, y, s, face, t, mouth=mouth, **kw)


def magnus(c, tl, t, x, y, s=0.8, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("magnus", t))
    P.moose(c, x, y, s, face, t, mouth=mouth, **kw)


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
    elif who == "tuva":
        hop = abs(math.sin(x / (9 * s))) * 7 * s if moving else kw.pop("hop", 0.0)
        tuva(c, tl, t, x, y, s, face, walk=x / (6 * s) if moving else 0.0, hop=hop, **kw)
    elif who == "magnus":
        magnus(c, tl, t, x, y, s, face, walk=x / (40 * s) if moving else 0.0, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def arc(u, h):
    return -4 * h * u * (1 - u)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def bubble(c, x, y, rx, ry, k, tail=(0, 0), fill=(255, 255, 255)):
    """Thought bubble scaled by k with two trailing puffs toward tail."""
    if k <= 0.02:
        return
    for f, r in ((0.35, 8), (0.65, 13)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)
    if fill != (255, 255, 255):
        c.ellipse(x, y, rx * k * 0.92, ry * k * 0.85, fill, ol=None)


def hearts(c, x, y, t, t0, n=4, col=(240, 80, 110)):
    """Little hearts floating up from (x, y) since time t0."""
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


def steam_puffs(c, x, y, t, n=3, s=1.0):
    for k in range(n):
        u = (t * 1.2 + k / n) % 1.0
        c.circle(x + 18 * math.sin(k * 2 + t * 3) * u, y - 50 * u * s, (6 + 10 * u) * s,
                 mix((255, 255, 255), (220, 220, 230), u), ol=None)


# ======================================================== the night fjord

HORIZON = 430
RIBBONS = [(0.62, 0.05, 0.7, 1.0, 0.30, -0.15, 0.75),
           (0.48, 0.06, 1.0, -0.8, 0.26, 0.2, 1.15),
           (0.36, 0.04, 1.4, 0.6, 0.22, 0.45, 1.1)]


def night_sky():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (6, 10, 34)), (0.4, (14, 30, 70)), (HORIZON / H, (34, 66, 104)),
                                               (HORIZON / H + 0.001, (16, 34, 70)), (1, (6, 14, 36))]))
        D.stars(c, 21, 140, W, HORIZON - 40)
        D.stars(c, 22, 40, W, HORIZON - 60, col=(200, 220, 255))
        return c.img
    return cached("night_sky", make)


def fjord_front():
    """Mountains around the fjord (RGBA), with their dark reflection in the water."""
    def make():
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img)
        far = (40, 56, 96)
        P.norway_mountain(c, 640, HORIZON + 4, 520, 150, far, snow=(150, 170, 206), seed=3, snowline=0.4,
                          ol=(24, 30, 56))
        P.norway_mountain(c, 920, HORIZON + 4, 420, 190, mix(far, (0, 0, 0), 0.1), snow=(150, 170, 206), seed=4,
                          ol=(24, 30, 56))
        mid = (26, 36, 70)
        c.poly([(-20, HORIZON + 4), (-20, 120), (60, 140), (140, 190), (230, 230), (330, 300), (420, 360),
                (520, HORIZON + 4)], mid, ol=(14, 18, 40), w=2.5)
        c.poly([(-20, 120), (60, 140), (140, 190), (100, 196), (40, 160), (-20, 150)], (120, 140, 180), ol=None)
        c.poly([(W + 20, HORIZON + 4), (W + 20, 160), (1200, 190), (1110, 250), (1040, 300), (980, 360),
                (900, HORIZON + 4)], mid, ol=(14, 18, 40), w=2.5)
        c.poly([(W + 20, 160), (1200, 190), (1150, 218), (1190, 206), (W + 20, 186)], (120, 140, 180), ol=None)
        # village on the right shore, warm windows
        for x, s in ((960, 0.42), (1010, 0.36), (1060, 0.44), (1120, 0.38)):
            P.red_house(c, x, HORIZON + 2, s, lit=True, snow_roof=True)
        P.stave_church(c, 1180, HORIZON + 2, 0.4, col=(50, 34, 30), roof=(36, 26, 24))
        c.rect(-20, HORIZON, W + 20, HORIZON + 5, (18, 26, 52), ol=None)
        # dark mirror of everything above the waterline
        top = HORIZON - 320
        band = img.crop((0, top * SS, W * SS, HORIZON * SS)).transpose(Image.FLIP_TOP_BOTTOM)
        r, g, b, a = band.split()
        dark = Image.merge("RGBA", (r.point(lambda v: int(v * 0.45)), g.point(lambda v: int(v * 0.5)),
                                    b.point(lambda v: int(v * 0.65)), a.point(lambda v: int(v * 0.85))))
        img.alpha_composite(dark, (0, HORIZON * SS))
        # a few warm window reflections
        for x in (948, 972, 1048, 1072, 1110):
            c.rect(x - 2, HORIZON + 12, x + 2, HORIZON + 30, (200, 160, 90), ol=None)
        return img
    return cached("fjord_front", make)


def water_glints(c, t, y0=HORIZON + 10, y1=H, n=26, seed=4, col=(120, 160, 210)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = rng.uniform(0, W)
        y = rng.uniform(y0, y1)
        w = rng.uniform(10, 40) * (0.6 + 0.4 * math.sin(t * 1.5 + k))
        c.line([(x - w, y), (x + w, y)], col, 2, cap=False)


def night_fjord(t, aurora=1.0, fg=None, clouds=None):
    """Night fjord frame: sky -> (clouds) -> aurora -> mountains -> fg layer."""
    img = night_sky().copy()
    if clouds is not None:
        clouds(img)
    P.apply_aurora(img, t, RIBBONS, aurora, (0, 0, W, HORIZON), mirror=(HORIZON, H))
    img.paste(fjord_front(), (0, 0), fjord_front())
    c = Canvas(img)
    water_glints(c, t, col=mix((60, 90, 150), (120, 230, 170), clamp(aurora * 0.6)))
    if fg is not None:
        im = fg()
        c.img.paste(im, (0, 0), im)
    return c


# =================================================================== title

def title_fg():
    def make():
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img)
        rock = (40, 46, 76)
        c.poly([(-20, H + 10), (-20, 600), (80, 580), (200, 572), (330, 590), (420, 640), (470, H + 10)], rock,
               ol=(16, 20, 40), w=3)
        c.poly([(-20, 606), (80, 582), (200, 574), (330, 592), (300, 604), (180, 590), (60, 600)], P.SNOW_SH, ol=None)
        for x, y, s in ((1160, 720, 1.0), (1240, 730, 0.85), (40, 640, 0.7)):
            P.pine(c, x, y, s, col=(24, 46, 56), dark=(16, 34, 44))
        return img
    return cached("title_fg", make)


def title(tl, t):
    c = night_fjord(t, 0.6 + 0.5 * ease(tl.prog("t_open", t, 0.0, 0.6)), title_fg)
    c.tint = ((30, 70, 80), 0.32)
    kat(c, tl, t, "luna", 170, 584, 0.7, 1, "sit", look=(1, -1), tail=math.sin(t * 1.4))
    kat(c, tl, t, "whiskers", 255, 588, 0.72, 1, "sit", look=(1, -1), eyes="happy" if t > 9 else "open")
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.15, 0.7))
    c.text(W / 2, 92 - 30 * (1 - k), "Whiskers and the", 44, mix((10, 20, 50), (235, 255, 240), k),
           stroke=3 * k, stroke_fill=(10, 30, 50))
    k2 = ease(tl.prog("t_open", t, 0.35, 1.0))
    c.text(W / 2, 170, "DANCING LIGHTS", 28 + 54 * k2, mix((10, 20, 50), (170, 255, 200), k2), stroke=5 * k2,
           stroke_fill=(30, 20, 70))
    return finish(c, tl, t)


# ===================================================================== van

SILL = 432
VAN_X, VAN_Y, VAN_S = 840, 692, 0.95


def street_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (130, 186, 236)), (0.6, (214, 234, 250)), (1, (214, 234, 250))]))
        D.cloud(c, 980, 90, 0.9)
        D.cloud(c, 1200, 160, 0.6)
        # houses down the street
        for x, w, h, col in ((760, 160, 300, (226, 196, 150)), (930, 140, 250, (200, 120, 100)),
                             (1080, 210, 330, (236, 222, 196))):
            c.rect(x, 560 - h, x + w, 560, col, w=2.5)
            c.poly([(x - 12, 560 - h), (x + w / 2, 560 - h - 60), (x + w + 12, 560 - h)], (150, 80, 70), w=2.5)
            for wy in range(int(560 - h + 40), 500, 80):
                for wx in range(int(x) + 24, int(x + w) - 30, 56):
                    c.rect(wx, wy, wx + 28, wy + 38, (170, 210, 240), w=2)
        D.tree(c, 1230, 560, 0.9, leaf=(230, 150, 60))
        D.tree(c, 700, 560, 0.8, leaf=(220, 120, 50))
        # sidewalk + road
        c.rect(0, 556, W, 600, (200, 196, 190), ol=None)
        c.line([(0, 556), (W, 556)], OUT, 2.5, cap=False)
        for x in range(0, W, 90):
            c.line([(x, 558), (x - 10, 598)], (170, 166, 160), 2, cap=False)
        c.rect(0, 600, W, H, (110, 112, 120), ol=None)
        c.rect(0, 598, W, 606, (150, 150, 156), ol=None)
        for x in range(30, W, 160):
            c.rect(x, 680, x + 80, 688, (240, 236, 220), ol=None)
        # the cats' house (left)
        wall = (244, 222, 178)
        c.rect(-10, 0, 640, 560, wall, w=3)
        for y in range(20, 560, 34):
            c.line([(-10, y), (640, y)], mix(wall, (150, 110, 70), 0.25), 2, cap=False)
        c.rect(-10, 0, 640, 24, (150, 80, 70), w=3)
        # window (open) with warm room inside
        c.rect(150, 210, 470, SILL, (120, 92, 80), w=3)
        c.rect(158, 218, 462, SILL, (250, 214, 160), ol=None)
        c.rect(158, 330, 462, SILL, (220, 170, 120), ol=None)
        c.rect(380, 250, 440, 320, (150, 100, 60), w=2)                  # framed moon picture
        c.rect(386, 256, 434, 314, (40, 46, 96), ol=None)
        c.circle(418, 272, 8, (250, 246, 215), ol=None)
        c.rect(190, 284, 230, 330, (190, 100, 70), w=2, r=4)             # plant
        for dx, dy in ((-12, -6), (0, -20), (12, -8)):
            c.ellipse(210 + dx, 284 + dy, 8, 16, (80, 160, 90), w=2)
        for x0, x1 in ((120, 160), (460, 500)):                          # shutters
            c.rect(x0, 200, x1, SILL, (70, 120, 170), w=2.5)
            for y in range(214, SILL - 6, 18):
                c.line([(x0 + 4, y), (x1 - 4, y)], (50, 96, 146), 2, cap=False)
        c.rect(130, SILL, 490, SILL + 18, (250, 246, 236), w=3, r=3)        # outer sill
        c.rect(70, 450, 130, 556, (120, 80, 60), w=2)                     # front door edge
        c.rect(-10, 450, 70, 556, (160, 70, 60), w=2.5)
        c.circle(56, 506, 4, (250, 210, 70), w=1.5)
        for x in (520, 590):                                              # flower box
            D.flower(c, x, 556, (230, 80, 90), 1.0)
            D.flower(c, x + 30, 556, (250, 200, 80), 0.9)
        return c.img
    return cached("street", make)


def van_motion(tl, t):
    """Van x position and wheel angle."""
    T = tl.t
    keys = [(T("v_open"), 1700), (T("v_narr", 0.75), VAN_X)]
    if t < T("v_narr", 0.75):
        u = clamp((t - T("v_open")) / (T("v_narr", 0.75) - T("v_open")))
        x = lerp(1700, VAN_X, 1 - (1 - u) ** 2)
    elif t < T("v_drive", 0.15):
        x = VAN_X
    else:
        u = max(0.0, t - T("v_drive", 0.15))
        x = VAN_X + 60 * u * u + 30 * u
    return x, -x / 32


def aurora_bubble(c, x, y, k, t):
    bubble(c, x, y, 120, 64, k, tail=(x - 90, y + 110), fill=(18, 30, 70))
    if k < 0.9:
        return
    D.stars(c, 3, 0, 1, 1)
    for j, (col, dy) in enumerate((((90, 255, 160), 6), ((150, 120, 255), -14), ((90, 230, 200), 22))):
        pts = [(x - 90 + 180 * u, y + dy + 12 * math.sin(u * 6 + t * 2 + j)) for u in np.linspace(0, 1, 12)]
        c.line(pts, col, 5 - j)
    for k2 in range(6):
        c.circle(x - 80 + 32 * k2, y - 40 + 8 * (k2 % 2), 1.6, (255, 255, 230), ol=None)
    c.poly([(x - 100, y + 52), (x - 50, y + 26), (x, y + 44), (x + 60, y + 18), (x + 104, y + 50)], (30, 40, 70),
           ol=None)


def van(tl, t):
    T = tl.t
    c = Canvas(street_bg().copy())
    vx, wheel = van_motion(tl, t)
    door = ease(tl.prog("v_narr", t, 0.8, 1.0)) * (1 - ease(tl.prog("v_jump", t, 0.55, 0.75)))
    # who is in the crate (drawn inside the van, in van-local coordinates)
    w_in = t >= T("v_sneak", 0.5)
    l_in = t >= T("v_jump", 0.45)
    CR_X, CR_B = -30, -76            # top crate (local)

    def inside(cc):
        cc.rect(-188, -210, 38, -78, (36, 40, 56), ol=None)
        P.crate(cc, -140, -76, 0.85, lid=0.0, label="NORGE")
        P.crate(cc, -140, -150, 0.6, lid=0.0, label="FISK")
        P.crate(cc, CR_X, CR_B, 0.85, lid=1.0 if t >= T("v_narr", 0.95) and not t >= T("v_jump", 0.6) else 0.0)
        if w_in:
            bob = 3 * math.sin(t * 8)
            munch = T("v_sneak", 0.6) <= t < T("v_stop")
            kat(c, tl, t, "whiskers", CR_X - 10, CR_B - 20 + bob, 0.85, 1 if not l_in else -1, "sit",
                eyes="happy" if munch else "open", mouth=0.3 + 0.3 * math.sin(t * 14) if munch else tl.mouth("whiskers", t),
                head_dy=6)
            if munch:
                P.fish(cc, CR_X + 36, CR_B - 100 + bob, 0.7, -0.4)
        if l_in:
            kat(c, tl, t, "luna", CR_X + 24, CR_B - 18, 0.8, -1, "sit", eyes="wide" if t < T("v_pip") else "open")
        if w_in or l_in:
            P.crate(cc, CR_X, CR_B, 0.85, lid=0.0 if t >= T("v_jump", 0.6) else None)

    P.fish_van(c, vx, VAN_Y, VAN_S, t, door=door, wheel=wheel, inside=inside)
    # sniff lines drifting from the van to Whiskers
    if T("v_fish") <= t < T("v_sneak"):
        for k in range(3):
            u = ((t * 0.5) + k / 3) % 1.0
            pts = [(lerp(700, 420, v) , lerp(520, 330, v) + 10 * math.sin(v * 9 + t * 3 + k * 2)) for v in
                   np.linspace(max(0, u - 0.35), u, 7)]
            c.line(pts, (200, 220, 160), 3)
    # --- Whiskers on the sill, sniffing, then the leap
    wx0 = 380
    if t < T("v_sneak", 0.15):
        sniff = T("v_fish") <= t < T("v_sneak")
        crouch = t >= T("v_wait", 0.3)
        if crouch:
            kat(c, tl, t, "whiskers", wx0, SILL, 0.9, 1, "crouch", tail=math.sin(t * 10), eyes="wide", look=(1, 0.5),
                mouth=0)
        else:
            sleepy = t < T("v_fish")
            kat(c, tl, t, "whiskers", wx0, SILL, 0.9, 1, "sit", eyes="closed" if sleepy or sniff else "open",
                head_dy=-6 if sniff else 0, look=(1, 0))
            if t < T("v_look"):
                D.zzz(c, wx0 + 40, SILL - 120, t)
    elif t < T("v_sneak", 0.5):
        u = tl.prog("v_sneak", t, 0.15, 0.5)
        tx = VAN_X + CR_X * VAN_S - 10
        ty = VAN_Y + (CR_B - 70) * VAN_S
        kat(c, tl, t, "whiskers", lerp(wx0, tx, u), lerp(SILL, ty, u) + arc(u, 120), 0.9, 1, "leap",
            eyes="happy", mouth=0.6)
    # --- Luna on the sill
    lx0 = 250
    if t < T("v_jump", 0.1):
        alarmed = t >= T("v_sneak", 0.2)
        pose = "stand" if T("v_stop") - 0.3 <= t else "sit"
        dreamy = T("v_dance") <= t < T("v_dance", 1) + 0.3
        kat(c, tl, t, "luna", lx0, SILL, 0.9, 1, pose, eyes="wide" if alarmed and t < T("v_stop", 1) else
            ("happy" if dreamy else "open"), look=(1, -0.6) if dreamy else (1, 0.3))
        kb = ease(tl.prog("v_dance", t, 0.0, 0.15)) * (1 - ease(tl.prog("v_fish", t, 0.6, 0.95)))
        aurora_bubble(c, 300, 120, kb, t)
    elif t < T("v_jump", 0.45):
        u = tl.prog("v_jump", t, 0.1, 0.45)
        tx = VAN_X + (CR_X + 24) * VAN_S
        ty = VAN_Y + (CR_B - 70) * VAN_S
        kat(c, tl, t, "luna", lerp(lx0, tx, u), lerp(SILL, ty, u) + arc(u, 140), 0.9, 1, "leap", eyes="wide")
    # --- Pip pops onto the sill
    if t >= T("v_jump", 0.7):
        k = ease(tl.prog("v_jump", t, 0.7, 0.95))
        wave = T("v_pip") <= t
        D.mouse(c, lerp(150, 300, k), SILL, 1.3, 1, t, walk=t * 12 if k < 1 else 0, mouth=tl.mouth("pip", t),
                hop=abs(math.sin(t * 8)) * 10 if wave else 0, proud=wave, eyes="wide" if t < T("v_drive", 0.6) else "open")
    return finish(c, tl, t)


# =================================================================== plane

PW = 3 * W


def plane_sky():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (90, 150, 220)), (0.55, (250, 206, 190)), (0.7, (255, 228, 196)),
                                               (1, (255, 228, 196))]))
        c.glow(1040, 420, 300, 160, (255, 246, 210), (252, 214, 192), steps=10)
        return c.img
    return cached("plane_sky", make)


def plane_ground():
    """Wide strip (RGBA, y from 420 to H): sea, islands, then the snowy fjord coast."""
    def make():
        hh = H - 420
        img = Image.new("RGBA", (PW * SS, hh * SS), (0, 0, 0, 0))
        c = Canvas(img, size=(PW, hh))
        c.rect(0, 70, PW, hh, (60, 120, 180), ol=None)
        rng = np.random.default_rng(3)
        for k in range(60):
            x, y = rng.uniform(0, PW), rng.uniform(90, hh)
            c.line([(x, y), (x + rng.uniform(20, 60), y)], (110, 170, 220), 2, cap=False)
        for x in (900, 1300, 1500):
            c.ellipse(x, 120, 60, 12, (110, 140, 100), w=2)
        x0 = 1800
        for k, x in enumerate(range(x0, PW + 300, 170)):
            h = 120 + 60 * math.sin(k * 1.7) + 30 * (k % 2)
            P.norway_mountain(c, x, 110, 260, h, (100, 120, 150), snow=P.SNOW, seed=k, snowline=0.6)
        c.rect(x0 - 120, 100, PW, 112, (210, 222, 240), ol=None)
        for k, x in enumerate(range(x0 + 60, PW, 340)):          # fjord fingers of sea reaching inland
            c.poly([(x, 112), (x + 40, 60 + 10 * (k % 2)), (x + 70, 112)], (60, 120, 180), ol=None)
        return img
    return cached("plane_ground", make)


def plane_clouds():
    def make():
        img = Image.new("RGBA", (2 * W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img, size=(2 * W, H))
        rng = np.random.default_rng(8)
        for k in range(12):
            x = rng.uniform(0, 2 * W)
            y = rng.uniform(60, 400)
            for dx in (0, -2 * W, 2 * W):
                D.cloud(c, x + dx, y, rng.uniform(0.7, 1.5), col=(255, 250, 246))
        return img
    return cached("plane_clouds", make)


def hold_bg():
    def make():
        c = Canvas(bg=(70, 78, 96))
        c.ellipse(640, 420, 760, 520, (96, 104, 124), ol=None)
        for x in range(40, W, 150):                                   # ribs
            c.line([(x, 0), (x + (x - 640) * 0.06, H)], (60, 66, 84), 12, cap=False)
        c.rect(0, 600, W, H, (60, 64, 76), ol=None)
        for x in range(0, W, 60):
            c.line([(x, 600), (x - 20, H)], (50, 54, 66), 3, cap=False)
        # strapped crates and boxes
        for x, y, s in ((100, 600, 1.4), (260, 600, 1.4), (180, 488, 1.4), (1160, 600, 1.4)):
            P.crate(c, x, y, s, label="FISK")
        for x in (80, 340):
            c.line([(x, 360), (x + 120, 610)], (200, 160, 60), 6, cap=False)
        c.rect(980, 470, 1100, 600, (176, 140, 96), w=2.5)
        c.text(1040, 535, "BERGEN", 18, (90, 60, 40))
        # porthole frame (the view is pasted in per frame)
        c.circle(820, 250, 92, (150, 156, 170), w=4)
        c.circle(820, 250, 76, (30, 30, 40), w=3)
        return c.img
    return cached("hold", make)


def porthole_view():
    def make():
        vw = 3 * W
        c = Canvas(D.gradient(vw * SS, 200 * SS, [(0, (120, 180, 240)), (1, (230, 240, 255))]), size=(vw, 200))
        c.rect(0, 140, vw, 200, (50, 110, 170), ol=None)
        for k, x in enumerate(range(0, vw + 200, 110)):
            P.norway_mountain(c, x, 150, 200, 70 + 40 * math.sin(k * 1.3) + 20 * (k % 3), (110, 120, 150),
                              snow=P.SNOW, seed=k, snowline=0.7, ol=None)
        for k, x in enumerate(range(40, vw, 260)):
            c.poly([(x, 152), (x + 30, 132), (x + 70, 152)], (50, 110, 170), ol=None)
        return c.img
    return cached("porthole_view", make)


def porthole_mask():
    def make():
        m = Image.new("L", (152 * SS, 152 * SS), 0)
        Canvas(m)
        from PIL import ImageDraw
        ImageDraw.Draw(m).ellipse([0, 0, 152 * SS - 1, 152 * SS - 1], fill=255)
        return m
    return cached("porthole_mask", make)


def plane(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["plane"]
    if T("pl_munch") <= t < T("pl_land"):
        return plane_hold(tl, t)
    img = plane_sky().copy()
    cl = plane_clouds()
    cx = int(((t - s0) * 90) % (2 * W))
    far = cl.crop((cx * SS, 0, (cx + W) * SS, H * SS))
    img.paste(far, (0, 0), far)
    landing = t >= T("pl_land")
    if landing:
        gx = PW - W - 400 + (t - T("pl_land")) * 60
    else:
        u = clamp((t - s0) / max(1e-3, T("pl_munch") - s0))
        gx = lerp(0, PW - W - 600, u ** 1.4)
    gx = int(gx)
    gr = plane_ground().crop((gx * SS, 0, (gx + W) * SS, (H - 420) * SS))
    img.paste(gr, (0, 420 * SS), gr)
    c = Canvas(img)
    if landing:
        u = tl.prog("pl_land", t)
        px, py, tilt = lerp(560, 1500, u ** 1.3), lerp(300, 470, u), 0.12
        sc = 0.7 - 0.25 * u
    else:
        px, py, tilt = 620, 300 + 12 * math.sin(t * 1.3), 0.02 * math.sin(t * 0.9)
        sc = 0.8
    P.cargo_plane(c, px, py, sc, t, tilt)
    return finish(c, tl, t)


def plane_hold(tl, t):
    T = tl.t
    img = hold_bg().copy()
    pv = porthole_view()
    vx = int(((t - T("pl_munch")) * 70) % (2 * W))
    crop = pv.crop((vx * SS, 20 * SS, (vx + 152) * SS, 172 * SS))
    img.paste(crop, ((820 - 76) * SS, (250 - 76) * SS), porthole_mask())
    c = Canvas(img)
    c.circle(820, 250, 76, None, w=3)
    c.line([(770, 210), (800, 190)], (255, 255, 255), 4)
    # the open crate in the middle with two cats
    cx, cy = 560, 640
    P.crate(c, cx, cy, 1.5, lid=1.0, label="NORGE")
    shake = 2 * math.sin(t * 30) * (1 if T("pl_land") - 1 < t else 0)
    munch = T("pl_munch") <= t < T("pl_look")
    kat(c, tl, t, "whiskers", cx - 50, cy - 70 + shake, 1.0, 1, "sit", head_dy=4,
        eyes="happy" if munch and tl.mouth("whiskers", t) < 0.1 else "open")
    if munch:
        P.fish(c, cx + 10, cy - 168, 0.9, -0.3)
    look = t >= T("pl_munch", 0.8)
    if look:
        # Luna climbs to the porthole
        u = ease(tl.prog("pl_munch", t, 0.8, 1.0))
        kat(c, tl, t, "luna", lerp(cx + 40, 700, u), lerp(cy - 70, 390, u), 1.0, 1, "stand",
            eyes="wide" if t >= T("pl_look") else "open", look=(1, -1))
        c.rect(640, 390, 780, 410, (176, 140, 96), w=2.5)                  # shelf she stands on
    else:
        kat(c, tl, t, "luna", cx + 40, cy - 70, 1.0, -1, "sit", eyes="open", look=(-1, 0))
    P.crate(c, cx, cy, 1.5, lid=None, label="NORGE")
    for k in range(2):                                              # fish bones on the floor
        bx = 300 + k * 60
        c.line([(bx, 690), (bx + 40, 690)], (230, 230, 220), 3)
        for j in range(4):
            c.line([(bx + 8 + j * 8, 682), (bx + 8 + j * 8, 698)], (230, 230, 220), 2, cap=False)
    return finish(c, tl, t)


# ================================================================= harbour

HW = 2 * W + 300
WHARF = 612
STAND_X = 2020
CRATE_X = 520


def harbour_bg():
    def make():
        c = Canvas(D.gradient(HW * SS, H * SS, [(0, (110, 176, 236)), (0.6, (210, 232, 250)), (1, (210, 232, 250))]),
                   size=(HW, H))
        for x, y, s in ((300, 90, 1.0), (1200, 70, 0.8), (2300, 110, 1.1)):
            D.cloud(c, x, y, s)
        # the mountain behind the town (Fløyen), green with patches of snow
        P.norway_mountain(c, 900, 470, 1500, 330, (90, 140, 96), snow=P.SNOW, seed=2, snowline=0.18, flat=0.4)
        P.norway_mountain(c, 2300, 470, 1300, 260, (80, 128, 90), snow=P.SNOW, seed=5, snowline=0.15, flat=0.4)
        rng = np.random.default_rng(6)
        for k in range(30):
            x = rng.uniform(0, HW)
            P.pine(c, x, rng.uniform(420, 470), rng.uniform(0.25, 0.4), snowy=False, col=(60, 110, 76), dark=(46, 90, 62))
        # little white houses on the hill
        for k in range(14):
            x = 80 + k * 190 + rng.uniform(-30, 30)
            P.red_house(c, x, 440 + rng.uniform(0, 30), 0.3, lit=False)
        # Bryggen: the row of wooden harbour houses
        cols = [(196, 56, 46), (232, 172, 66), (246, 226, 150), (240, 236, 226), (214, 104, 56), (160, 64, 48),
                (232, 190, 90), (190, 60, 50), (246, 234, 214), (220, 140, 60)]
        x = 160
        k = 0
        while x < HW - 120:
            w = [110, 126, 100, 120, 116][k % 5]
            h = [190, 160, 210, 170, 200][k % 5]
            P.bryggen_house(c, x, 540, w, h, cols[k % len(cols)], seed=k)
            x += w + 4
            k += 1
        # wharf
        c.rect(0, 540, HW, 652, (170, 130, 90), ol=None)
        for y in range(552, 652, 18):
            c.line([(0, y), (HW, y)], (142, 104, 70), 2, cap=False)
        c.line([(0, 540), (HW, 540)], OUT, 2.5, cap=False)
        c.rect(0, 648, HW, 660, (120, 86, 58), ol=None)
        for x in range(30, HW, 120):
            c.rect(x, 650, x + 16, 700, (110, 78, 52), w=2)
        # water
        c.rect(0, 660, HW, H, (40, 96, 156), ol=None)
        for k in range(50):
            x, y = rng.uniform(0, HW), rng.uniform(672, H)
            c.line([(x, y), (x + rng.uniform(20, 50), y)], (90, 150, 210), 2, cap=False)
        # fish market stall on the left
        c.rect(30, 400, 300, 556, (240, 240, 236), w=2.5)
        for k in range(7):
            a = 30 + k * 270 / 7
            c.poly([(a, 400), (a + 270 / 7, 400), (a + 270 / 7, 440), (a, 440)],
                   (60, 110, 180) if k % 2 == 0 else (250, 250, 246), w=2)
        c.rect(40, 500, 290, 540, (200, 160, 110), w=2.5)
        for k in range(8):
            P.fish(c, 64 + k * 30, 504, 0.55, -0.3 + 0.1 * (k % 3), (170, 186, 200) if k % 2 else (230, 130, 110))
        c.text(165, 470, "FISKETORGET", 20, (60, 110, 180))
        # flags along the wharf
        for x in (420, 1300, 1700, 2500):
            P.flag(c, x, 548, 1.0, 0.0, pole=150)
        # barrels, ropes, a bollard
        for x in (1150, 1190):
            c.ellipse(x, 600, 22, 30, (150, 100, 60), w=2.5)
            c.line([(x - 22, 590), (x + 22, 590)], (90, 70, 60), 3, cap=False)
        c.rect(1460, 570, 1490, 610, (60, 60, 70), w=2.5, r=6)
        # waffle stand
        P.waffle_stand(c, STAND_X, 620, 0.9)
        return c.img
    return cached("harbour_bg", make)


def table(c, x, y):
    """Small round barrel-table on the wharf; top at y."""
    c.ellipse(x, y + 46, 34, 44, (150, 100, 60), w=2.5)
    c.line([(x - 34, y + 30), (x + 34, y + 30)], (90, 70, 60), 3, cap=False)
    c.line([(x - 34, y + 66), (x + 34, y + 66)], (90, 70, 60), 3, cap=False)
    c.ellipse(x, y, 50, 12, (200, 160, 110), w=2.5)


def harbour(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["harbour"]
    camx = smooth(t, [(s0, 0), (T("hb_walk", 0.1), 0), (T("hb_walk", 0.95), 1200), (s1, 1200)], 0.5)
    camx = clamp(camx, 0, HW - W)
    c = view(harbour_bg(), camx)
    c.push(-camx, 0)
    # waving flags on top of the static ones
    for x in (420, 1300, 1700, 2500):
        if -100 < x - camx < W + 100:
            P.flag(c, x, 548, 1.0, t, pole=150)
    # the crate
    pop = tl.prog("hb_pop", t, 0.12, 0.35)
    P.crate(c, CRATE_X, WHARF, 1.3, lid=ease(pop))
    # --- cats pop out of the crate
    out = tl.prog("hb_pop", t, 0.35, 0.6)
    WX, LX = 400, 650
    if t < T("hb_pop", 0.35):
        if pop > 0.3:
            kat(c, tl, t, "whiskers", CRATE_X - 20, WHARF - 70, 0.9, 1, "sit", eyes="wide")
            kat(c, tl, t, "luna", CRATE_X + 30, WHARF - 80 + 30 * (1 - pop), 0.9, -1, "sit", eyes="wide")
            P.crate(c, CRATE_X, WHARF, 1.3, lid=None)
    elif t < T("hb_pop", 0.6):
        kat(c, tl, t, "whiskers", lerp(CRATE_X - 20, WX, out), lerp(WHARF - 100, WHARF, out) + arc(out, 70), 1.0, -1,
            "leap", eyes="happy")
        kat(c, tl, t, "luna", lerp(CRATE_X + 20, LX, out), lerp(WHARF - 100, WHARF, out) + arc(out, 90), 1.0, 1,
            "leap", eyes="happy")
    # positions after the pop
    walk0, walk1 = T("hb_walk", 0.1), T("hb_walk", 0.95)
    WX2, LX2, TX2 = 1960, 1760, 2120
    burn0, burn1 = T("hb_burn"), T("hb_burn", 1)
    if t >= T("hb_pop", 0.6):
        # Luna
        lkeys = [(T("hb_pop", 0.6), LX), (walk0 + 0.3, LX), (walk1 - 0.4, LX2)]
        leyes = "happy" if (T("hb_purpose") <= t < T("hb_purpose", 1) + 0.3) or t >= T("hb_end") else "open"
        lface = 1
        if t < walk0:
            lface = 1
        lmouth = laughing(t) * 0.6 if T("hb_purpose", 0.4) <= t < T("hb_brown") else tl.mouth("luna", t)
        actor(c, tl, t, "luna", lkeys, WHARF, 1.0, lface, eyes=leyes, mouth=lmouth)
        # Whiskers (special business at the stand)
        if t < burn0:
            wkeys = [(T("hb_pop", 0.6), WX), (walk0, WX), (walk1 - 0.8, WX2)]
            face = 1
            excited = t >= T("hb_ten")
            hop = abs(math.sin(t * 9)) * 14 if T("hb_ten") <= t < T("hb_ten", 1) else 0
            x = smooth(t, wkeys)
            if abs(speed(t, wkeys)) > 20:
                actor(c, tl, t, "whiskers", wkeys, WHARF, 1.0, face)
            else:
                kat(c, tl, t, "whiskers", x, WHARF - hop, 1.0, 1 if t >= walk0 else -1 if t < T("hb_tuva") else 1,
                    "stand", eyes="happy" if excited and tl.mouth("whiskers", t) < 0.1 else "open", look=(1, -0.5))
        elif t < T("hb_brown"):
            u = tl.prog("hb_burn", t)
            if u < 0.12:
                kat(c, tl, t, "whiskers", WX2, WHARF, 1.0, 1, "stand", head_dy=-10, look=(1, -1), eyes="happy")
                P.waffle(c, WX2 + 70, WHARF - 160 + 40 * u / 0.12, 1.0, steam=1.0, t=t)
            elif u < 0.85 or t < T("hb_purpose"):
                v = (u - 0.12) / 0.73
                hop = abs(math.sin(v * math.pi * 4)) * 90 if u < 0.85 else 0
                hx = WX2 - 140 * math.sin(v * math.pi * 2) * 0.5 if u < 0.85 else WX2 - 20
                face = 1 if math.sin(v * math.pi * 8) > 0 else -1
                yowl = u < 0.85
                kat(c, tl, t, "whiskers", hx, WHARF - hop, 1.0, face if yowl else 1, "stand" if yowl else "sit",
                    eyes="wide" if yowl else "closed", mouth=0.9 if yowl else tl.mouth("whiskers", t),
                    head_dy=0)
                if yowl:
                    wx_ = hx + 60 * face + 40 * math.sin(v * 20)
                    P.waffle(c, wx_, WHARF - hop - 190 - 40 * abs(math.sin(v * 14)), 0.9, steam=1.0, t=t)
                    steam_puffs(c, hx + 70 * face, WHARF - hop - 120, t * 2, 3, 0.8)
                else:
                    # tongue out, cooling it
                    steam_puffs(c, WX2 + 0, WHARF - 150, t, 2, 0.6)
            else:
                kat(c, tl, t, "whiskers", WX2 - 20, WHARF, 1.0, 1, "sit", eyes="closed")
        else:
            # brown cheese waffle on the barrel table
            happy = t >= T("hb_taste")
            kat(c, tl, t, "whiskers", WX2 - 20, WHARF, 1.0, 1, "sit",
                eyes="happy" if happy and tl.mouth("whiskers", t) < 0.15 or T("hb_taste", 0.6) <= t else "open",
                look=(1, 0.6), mouth=0.4 + 0.3 * math.sin(t * 14) if T("hb_taste", 0.1) <= t < T("hb_taste", 0.9)
                else tl.mouth("whiskers", t))
            if t >= T("hb_love"):
                hearts(c, WX2 + 20, WHARF - 150, t, T("hb_love"))
        # the barrel table appears for the brown cheese
        if t >= T("hb_brown"):
            table(c, WX2 + 80, WHARF - 56)
            bite = 0.2 + 0.6 * tl.prog("hb_taste", t, 0.1, 0.9) if t >= T("hb_taste") else 0
            P.waffle(c, WX2 + 80, WHARF - 64, 1.0, bite=bite, cheese=True)
        # Tuva
        tkeys = [(T("hb_pop", 0.6), 1400), (T("hb_pop", 1.0), 860), (walk0 + 0.6, 860), (walk1, TX2)]
        on_counter = t >= walk1
        if not on_counter:
            actor(c, tl, t, "tuva", tkeys, WHARF, 1.3, -1, wing=0.8 if tl.talking("tuva", t) else 0.0,
                  eyes="happy" if tl.talking("tuva", t) and t > T("hb_waffle") else "open")
        else:
            hopk = ease(clamp((t - walk1) / 0.5))
            ty = lerp(WHARF, WHARF - 108, hopk) + arc(hopk, 50)
            serving = T("hb_brown") - 0.6 <= t < T("hb_brown", 0.6)
            flap = T("hb_hot") <= t < T("hb_hot", 1)
            tuva(c, tl, t, TX2, ty, 1.3, -1, wing=1.0 if flap or serving else 0.0,
                 fly=0.6 if flap else 0.0, eyes="happy" if t >= T("hb_love") else "open")
    # waffles on the counter + the waffle iron
    stand_top = 620 - 120 * 0.9
    P.waffle_iron(c, STAND_X - 70, stand_top + 4, 1.0, t, open_=0.6)
    if T("hb_walk") <= t:
        steam_puffs(c, STAND_X - 70, stand_top - 30, t, 3, 0.8)
    n_plate = 3 if t < T("hb_burn") else 2
    c.ellipse(STAND_X + 60, stand_top + 2, 46, 10, (250, 250, 246), w=2)
    for k in range(n_plate):
        P.waffle(c, STAND_X + 60, stand_top - 2 - k * 6, 0.9)
    c.pop()
    return finish(c, tl, t)
