"""Scenes of Episode 1 "Our Planet". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py.
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e01_our_planet import props as P

CONTINUOUS = ("map",)            # the sill flashes white straight into space
EXTRA_CUTS = ("w_noedge",)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def hop(a, b, u, h=80):
    """Point on a jump arc from a to b."""
    u = ease(u)
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


# ======================================================================= title

def title(tl, t):
    c = K.title_card(tl, t, 0.0, 1, "Our Planet")
    return c


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45            # cushion scale; cats on it are 0.62 * 1.45 = 0.9
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548


def sill_globe_lon(tl, t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def flat_or_ball(ic, k):
    """Inset diagram: zoomed in, the ground looks flat; zoomed out, it is a ball."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 205, 250)), (1, (220, 240, 255))]), (0, 0))
    e = ease(k)
    R = 80 * (2400 / 80) ** (1 - e)
    top = 116 - 16 * e
    cx, cy = w / 2, top + R
    if R > 1500:
        ic.rect(0, top, w, h, (120, 190, 92), ol=OUT, w=3)
    else:
        ic.circle(cx, cy, R, (64, 146, 222), w=3)
        pts = [(cx + math.cos(a) * R, cy + math.sin(a) * R) for a in np.linspace(-2.2, -0.9, 30)]
        ic.poly([(cx, cy)] + pts, (120, 190, 92), ol=None)
        ic.circle(cx, cy, R, None, ol=OUT, w=3)
    s = lerp(0.42, 0.1, e)
    D.cat(ic, cx - 10 * s, top + 1, D.WHISKERS, s, 1, "stand", t=0)
    if k < 0.45:
        K.text(ic, w / 2, h - 34, "Looks flat...", 30, (48, 40, 60))
    else:
        K.text(ic, w / 2, h - 30, "...but it's a ball!", 30, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))


def earth_in_space(ic, t):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    K.globe(ic, w / 2, h / 2 - 8, 74, lon=-t * 25, lat=20, glow=0.4)
    K.text(ic, w / 2, h - 22, "The Earth", 26, (255, 255, 255), stroke=3)


def sill(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("day").copy())
    spins = [(T("s_open", 0.15), 260), (T("s_narr", 0.2), 200), (T("s_hold", 0.6), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(tl, t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    speaking_to_globe = t < T("s_glow")
    if hopk <= 0:
        # Whiskers on his cushion, Luna by the globe, Pip at its foot
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "wide" if tl.talking("whiskers", t) and t < T("s_globe") else "open"
        if T("s_space") <= t < T("s_flat"):
            w_eyes = "wide"
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.5))
        lean = -8 * math.exp(-max(0, t - T("s_narr", 0.2)) * 3) if t > T("s_narr", 0.2) else 0
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", head_dy=lean, look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_round") or t > T("s_space2", 1) else -1,
            proud=tl.talking("pip", t))
    else:
        luna_xy = hop((LUNA_X, SY), cush_spots["luna"], hopk, 160)
        pip_xy = hop((PIP_X, SY), cush_spots["pip"], clamp(hopk * 1.3), 90)
        if hopk < 1:
            K.cushion(c, CUSH_X, SY, CREW_S, t)
            kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes="wide")
            kat(c, tl, t, "luna", luna_xy[0], luna_xy[1], CAT_S, -1, "leap" if 0.05 < hopk < 0.95 else "sit")
            kat(c, tl, t, "pip", pip_xy[0], pip_xy[1], 1.1 * lerp(1, 0.75 / 0.75, hopk), -1)
        else:
            e = ease(fly)
            x = lerp(CUSH_X, gcx, e)
            y = lerp(SY, gcy + 40, e) - 80 * math.sin(math.pi * e)
            s = CREW_S * lerp(1, 0.15, e ** 1.5)
            K.crew(c, tl, t, x, y, s, 1, fly=min(1, fly * 3), eyes={"whiskers": "wide"},
                   look={"luna": (1, -1), "pip": (1, -1)})

    # teaching moments
    kg = tl.prog("s_globe", t, 0.35, 0.55) * (1 - tl.prog("s_round", t, 0.6, 0.9))
    K.label(c, 800, 205, "Globe = a little Earth", 26, tip=(gcx + 70, gcy - 60), k=kg)
    ks = tl.prog("s_space", t, 0.15, 0.4) * (1 - tl.prog("s_flat", t, 0.0, 0.25))
    if ks > 0.01:
        K.inset(c, 975, 170, 320, 230, ks, lambda ic: earth_in_space(ic, t), bg=(20, 20, 50))
    kz = tl.prog("s_big", t, 0.1, 0.3) * (1 - tl.prog("s_hold", t, 0.0, 0.2))
    if kz > 0.01:
        zk = tl.prog("s_zoom", t, 0.1, 0.8)
        K.inset(c, 640, 160, 440, 250, kz, lambda ic: flat_or_ball(ic, zk))
    K.sub_band(c, tl, t)
    # push in to the glowing globe and flash white into space
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
MEET = (-32, 8)
GO_PATH = [HOME, (-12, 36), (-26, 20), MEET]
WORDS = {"N": "Never", "E": "Eat", "S": "Soggy", "W": "Waffles"}


def waffle(c, x, y, r):
    c.rect(x - r, y - r, x + r, y + r, (236, 180, 90), r=8, w=3)
    for k in range(1, 4):
        f = -r + 2 * r * k / 4
        c.line([(x + f, y - r + 4), (x + f, y + r - 4)], (196, 132, 60), 3)
        c.line([(x - r + 4, y + f), (x + r - 4, y + f)], (196, 132, 60), 3)
    c.rect(x - 10, y - 12, x + 10, y + 4, (255, 236, 150), r=3, w=2)


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40
    end = -14 * (tl.t("m_flatline", 1) - t0) + 40
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_flatline", t, 0.1, 1.0)))


def map_crew(c, tl, t, x, y, s, **kw):
    K.crew(c, tl, t, x, y, s, 1, fly=1.0, **kw)


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        # ---- up in space: the Earth is a ball
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        gx, gy = lerp(760, 640, k), lerp(300, 360, tl.prog("m_flatline", t))
        lon = space_globe_lon(tl, t)
        K.globe(c, gx, gy, r, lon=lon, lat=lerp(18, 0, ease(tl.prog("m_flatline", t))), glow=0.5)
        K.label(c, gx + r * 0.9 + 60, gy - r * 0.8, "The Earth", 28, tip=(gx + r * 0.62, gy - r * 0.5),
                k=tl.prog("m_wow", t, 0.2, 0.4))
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        mk = ease(tl.prog("m_flatline", t, 0.0, 0.6))
        x = lerp(lerp(-200, 260, fk), 170, mk)
        y = lerp(lerp(820, 600, fk), 660, mk)
        s = lerp(1.0, 0.75, mk)
        map_crew(c, tl, t, x, y, s, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
                 eyes={"whiskers": "wide"} if t < T("m_wow") else None)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_home"):
        # ---- the globe flattens into the map
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        if k >= 1:
            K.map_labels(c, K.MapView(0, 0, 1), "continents", tl.prog("m_flat", t, 0.85, 1.0))
        K.label(c, 640, 46, "A map = the globe, flattened out", 28, k=tl.prog("m_flat", t, 0.3, 0.45)
                * (1 - tl.prog("m_flat", t, 0.92, 1.0)))
        map_crew(c, tl, t, 170, 660, 0.75, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    # camera: whole world, then off along the dotted path to the middle of the ocean
    pk = tl.prog("m_path", t, 0.3, 1.0)
    cam = K.lerp_view((0, 0, 1.0), (MEET[0], MEET[1], 2.6), ease(pk))
    c, v = K.map_view(*cam, t=t)
    lab_k = 1 - tl.prog("m_path", t, 0.0, 0.2)
    K.map_labels(c, v, "continents", lab_k)
    K.map_labels(c, v, "oceans", tl.prog("m_blue", t, 0.4, 0.7) * lab_k)
    # you are here
    hk = tl.prog("m_home", t, 0.45, 0.75) * (1 - tl.prog("m_path", t, 0.7, 0.85))
    hx, hy = v.xy(*HOME)
    K.you_are_here(c, hx, hy, t, hk, "You are here!" if t < T("m_path") else "", side=1)
    # dotted path + the cushion flying along it
    if t >= T("m_go", 0.5):
        u = tl.prog("m_path", t, 0.15, 0.8)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        if t >= T("m_path", 0.1):
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, -1 if math.cos(ang) < 0 else 1, fly=1)
    # big compass in the middle while directions are explained
    grow = ease(tl.prog("m_compass", t, 0.0, 1.0)) * (1 - ease(tl.prog("m_laugh", t, 0.0, 1.0)))
    if t >= T("m_dirs"):
        dim = 0.45 * grow
        if dim > 0.01:
            K.flash(c, dim, (20, 20, 50))
        lit = set()
        if t > T("m_ns", 0.05):
            lit.add("N")
        if t > T("m_ns", 0.5):
            lit.add("S")
        if t > T("m_ew", 0.05):
            lit.add("E")
        if t > T("m_ew", 0.5):
            lit.add("W")
        words = None
        if T("m_nesw") <= t < T("m_laugh", 1):
            order = "NESW"
            n = sum(1 for i in range(4) if t > T("m_nesw", 0.05 + 0.12 * i))
            lit = set(order[:n]) if t < T("m_waffle") else set(order)
            words = WORDS
        if t > T("m_laugh", 0.3):
            lit = set()
        x = lerp(1160, 640, grow)
        y = lerp(575, 330, grow)
        r = lerp(52, 150, grow)
        kk = tl.prog("m_dirs", t, 0.4, 0.8)
        K.compass(c, x, y, r, kk, t, lit, words)
        # direction arrows on the map while N/S and E/W are named
        if grow > 0.9:
            ak = tl.prog("m_ns", t, 0.0, 0.25)
            K.arrow(c, 640, 330 - 220, 640, 330 - 300, (255, 236, 90), 8, ak * (1 - tl.prog("m_ns", t, 0.45, 0.5)))
            K.arrow(c, 640, 330 + 220, 640, 330 + 300, (255, 236, 90), 8, tl.prog("m_ns", t, 0.5, 0.75)
                    * (1 - tl.prog("m_ew", t, 0.0, 0.1)))
            K.arrow(c, 640 + 220, 330, 640 + 330, 330, (255, 236, 90), 8, tl.prog("m_ew", t, 0.0, 0.25)
                    * (1 - tl.prog("m_ew", t, 0.45, 0.5)))
            K.arrow(c, 640 - 220, 330, 640 - 330, 330, (255, 236, 90), 8, tl.prog("m_ew", t, 0.5, 0.75)
                    * (1 - tl.prog("m_nesw", t, 0.0, 0.1)))
            for txt, (lx, ly), a, b in (("Up = North", (640, 30), ("m_ns", 0.1), ("m_ns", 0.48)),
                                        ("Down = South", (640, 650), ("m_ns", 0.55), ("m_ew", 0.05)),
                                        ("East", (1060, 250), ("m_ew", 0.1), ("m_ew", 0.48)),
                                        ("West", (220, 250), ("m_ew", 0.55), ("m_nesw", 0.08))):
                kk2 = (1 if t > T(*a) else 0) * (1 if t < T(*b) else 0)
                if kk2:
                    K.label(c, lx, ly, txt, 30, k=min(1, (t - T(*a)) * 4))
    # the friends on their cushion, hovering in front of the map
    if t < T("m_path", 0.25):
        sk = ease(tl.prog("m_path", t, 0.0, 0.25))
        x = lerp(170, hx, sk)
        y = lerp(660, hy + 6, sk)
        s = lerp(0.75, 0.16, sk)
        laugh = T("m_laugh") <= t < T("m_laugh", 1)
        eyes = {"luna": "happy", "pip": "happy"} if laugh else {}
        if T("m_waffle") <= t < T("m_laugh", 1):
            eyes["whiskers"] = "happy"
        map_crew(c, tl, t, x, y, s, eyes=eyes, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
                 extra={"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None)
        bk = tl.prog("m_waffle", t, 0.1, 0.3) * (1 - tl.prog("m_laugh", t, 0.6, 1.0))
        if bk > 0.01:
            K.bubble(c, 300, 420, 90, 64, bk, tail=(150, 560))
            waffle(c, 300, 420, 40 * bk)
    return c


# ========================================================================= sea

HORIZON = 300
WL = 586               # waterline in front
CUSH = (380, WL - 4)
TURTLE = (905, WL + 6)


def sea_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (100, 176, 240)), (HORIZON / H, (214, 238, 255)),
                                               (HORIZON / H + 0.001, (110, 186, 236)), (1, (36, 106, 186))]))
        c.glow(1060, 110, 220, 160, (255, 250, 210), (150, 205, 248), steps=10)
        c.circle(1060, 110, 48, (255, 232, 120), ol=None)
        D.cloud(c, 230, 110, 0.9)
        D.cloud(c, 620, 70, 0.6)
        D.cloud(c, 820, 180, 0.5)
        c.line([(0, HORIZON), (W, HORIZON)], (240, 250, 255), 3, cap=False)
        # a far-away island to show that land is small out here
        c.ellipse(140, HORIZON + 2, 46, 9, (120, 170, 100), ol=None)
        c.line([(140, HORIZON - 6), (146, HORIZON - 30)], (130, 100, 70), 2)
        c.ellipse(150, HORIZON - 32, 12, 5, (90, 160, 90), ol=None)
        for (x, y) in ((420, 150), (460, 135)):
            c.arc(x, y, 10, 6, 200, 340, OUT, 2)
            c.arc(x + 20, y, 10, 6, 200, 340, OUT, 2)
        return c.img
    return cached("sea", make)


def underwater(c, boxes):
    """Repaint the sea over the lower parts of floating things."""
    bg = sea_bg()
    for x0, y0, x1, y1 in boxes:
        a = (int(max(0, x0) * SS), int(y0 * SS), int(min(W, x1) * SS), int(min(H, y1) * SS))
        if a[2] > a[0] and a[3] > a[1]:
            c.img.paste(bg.crop(a), (a[0], a[1]))


def foam(c, x, w, t, y=WL):
    for k in range(5):
        dx = (k - 2) / 2 * w + 8 * math.sin(t * 3 + k)
        c.ellipse(x + dx, y + 2, 26 + 6 * math.sin(t * 4 + k * 2), 6, (230, 246, 255), ol=None)


def loop_inset(ic, t, k_lap):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    cx, cy, r = w / 2, h / 2 - 14, 76
    ang = -math.pi / 2 + k_lap * math.tau          # turtle position on the ring
    rx, ry = 120, 34

    def ring(front):
        pts = []
        for a in np.linspace(0, math.tau, 80):
            if (math.sin(a) > 0) == front:
                pts.append((cx + math.cos(a) * rx, cy + 22 + math.sin(a) * ry))
        for i in range(0, len(pts) - 1, 2):
            ic.line([pts[i], pts[i + 1]], (255, 236, 110), 4)
    ring(False)
    tx, ty = cx + math.cos(ang) * rx, cy + 22 + math.sin(ang) * ry
    if math.sin(ang) <= 0:
        P.turtle(ic, tx, ty, 0.16, 1 if math.cos(ang) < 0 else -1, t)
    K.globe(ic, cx, cy, r, lon=-t * 20, lat=15)
    ring(True)
    if math.sin(ang) > 0:
        P.turtle(ic, tx, ty, 0.2, 1 if math.cos(ang) < 0 else -1, t)
    if k_lap >= 1:
        K.text(ic, w / 2, h - 24, "Back where he started!", 26, (255, 236, 110), stroke=3)
    else:
        K.text(ic, w / 2, h - 24, "All the way around", 26, (255, 255, 255), stroke=3)


def pie_inset(ic, t, k_water, k_land):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    cx, cy, r = 130, h / 2, 88
    blue, green = (64, 146, 222), (120, 190, 92)
    ic.circle(cx, cy, r, (236, 240, 246), ol=(170, 176, 190), w=3)
    # three water quarters, then the land quarter
    for i in range(3):
        if k_water * 3 > i:
            sub = clamp(k_water * 3 - i)
            _quarter(ic, cx, cy, r * pop(sub), i, blue)
    if k_land > 0:
        _quarter(ic, cx, cy, r * pop(k_land), 3, green)
    for i in range(3):
        if k_water * 3 > i + 0.5:
            K.text(ic, cx + math.cos(math.radians(-45 + 90 * i)) * r * 0.55,
                   cy + math.sin(math.radians(-45 + 90 * i)) * r * 0.55, "~", 34, (230, 245, 255))
    x0 = 270
    if k_water > 0.3:
        K.text(ic, x0, cy - 40, "3 parts water", 32, blue, anchor="lm", stroke=1, stroke_fill=(255, 255, 255))
    if k_land > 0.3:
        K.text(ic, x0, cy + 40, "1 part land", 32, (80, 150, 60), anchor="lm", stroke=1,
               stroke_fill=(255, 255, 255))


def _quarter(c, cx, cy, r, i, col):
    a0 = math.radians(-90 + 90 * i)
    a1 = math.radians(-90 + 90 * (i + 1))
    mid = (a0 + a1) / 2
    ox, oy = math.cos(mid) * 3, math.sin(mid) * 3
    pts = [(cx + ox, cy + oy)] + [(cx + ox + math.cos(a) * r, cy + oy + math.sin(a) * r)
                                  for a in np.linspace(a0, a1, 18)]
    c.poly(pts, col, w=3)


def sea(tl, t):
    T = tl.t
    c = Canvas(sea_bg().copy())
    P.sea_waves(c, t, HORIZON + 14, WL - 40, 6, (150, 206, 244), 20)
    # the turtle rises from the deep
    rise = ease_out(tl.prog("sea_hello", t, 0.0, 0.25))
    ty = lerp(WL + 150, TURTLE[1], rise)
    if t > T("sea_bubbles"):
        rng = np.random.default_rng(5)
        for k in range(10):
            u = (t * 0.9 + k / 10) % 1
            bx = TURTLE[0] - 120 + rng.uniform(-60, 60) + 6 * math.sin(t * 4 + k)
            by = WL + 40 - u * 90
            if t < T("sea_hello", 0.3) and by > WL - 10:
                c.circle(bx, by, 4 + 6 * rng.random(), (200, 236, 255), w=2)
    hopk = tl.prog("sea_hop", t, 0.05, 0.75)
    laugh = T("sea_laugh") <= t < T("sea_laugh", 1) or T("sea_soup", 0.7) <= t < T("sea_laugh")
    sh_eyes = "happy" if laugh or tl.talking("shelby", t) and t < T("sea_hello", 0.5) else "open"
    on_shell = hopk >= 1
    if rise > 0:
        if on_shell:
            P.turtle_crew(c, tl, t, TURTLE[0], ty, 1.0, -1, shelby_eyes=sh_eyes,
                          eyes={"whiskers": "happy"} if laugh else None)
        else:
            P.turtle(c, TURTLE[0], ty, 1.0, -1, t, tl.mouth("shelby", t), sh_eyes,
                     look=(-1, 0) if t < T("sea_climb") else (0, -1))
    # the friends on the floating cushion (they hop over to the shell at the end)
    land = tl.prog("sea_land", t, 0.0, 0.5)
    cy = lerp(-120, CUSH[1], ease(land)) + 3 * math.sin(t * 2)
    jitter = 0.0
    if T("sea_rock") <= t < T("sea_rock", 1):
        jitter = math.sin(t * 50) * 4
    cush_s = 1.2
    if hopk <= 0:
        eyes = {}
        look = {"luna": (1, 0), "whiskers": (1, 0), "pip": (1, 0)}
        if T("sea_rock") <= t < T("sea_name", 0.3):
            eyes["whiskers"] = "wide"
        if laugh:
            eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy" if t >= T("sea_laugh") else "open"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if t >= T("sea_laugh") and laugh \
            else None
        K.crew(c, tl, t, CUSH[0] + jitter, cy, cush_s, 1, fly=1 - land, eyes=eyes, look=look, extra=extra)
    elif not on_shell:
        K.cushion(c, CUSH[0], cy, cush_s, t)
        top = cy - 40 * cush_s
        for who, dx, tx, tyy, sc0, sc1, d in (("whiskers", -52, 62, -84, 0.74, 0.55, 0.0),
                                              ("luna", 46, -20, -96, 0.74, 0.55, 0.1),
                                              ("pip", 104, -82, -80, 0.9, 0.7, 0.2)):
            u = clamp((hopk - d) / 0.75)
            a = (CUSH[0] + dx * cush_s, top)
            b = (TURTLE[0] + tx, ty + tyy)
            x, y = hop(a, b, u, 120)
            pose = "leap" if 0.05 < u < 0.95 else "sit"
            kat(c, tl, t, who, x, y, lerp(sc0, sc1, u), 1 if u < 0.95 else -1, pose)
    if on_shell:
        pk = tl.prog("sea_hop", t, 0.75, 1.0)
        if pk < 1:
            K.cushion(c, CUSH[0], cy - 200 * ease(pk), 1.2 * (1 - pk), t, 1)
            K.sparkles(c, CUSH[0], cy - 200 * ease(pk), 120, t, 12, 1 - pk, seed=6)
    underwater(c, [(CUSH[0] - 190, WL + 2, CUSH[0] + 190, H), (TURTLE[0] - 260, WL + 2, TURTLE[0] + 330, H)])
    if land > 0.5:
        foam(c, CUSH[0], 140 * cush_s, t)
    if rise > 0.3:
        foam(c, TURTLE[0] - 40, 200, t)
    P.sea_waves(c, t, WL + 30, H - 20, 4, (160, 214, 248), 28, seed=7)
    # splash when the cushion lands
    sk = t - T("sea_land", 0.5)
    if 0 < sk < 1.0:
        for k in range(3):
            rr = 60 + 160 * sk + 40 * k
            c.ellipse(CUSH[0], WL + 4, rr, rr * 0.16, None, ol=mix((240, 250, 255), (100, 170, 230), sk), w=3)
    # teaching insets
    kl = tl.prog("sea_around", t, 0.25, 0.4) * (1 - tl.prog("sea_much", t, 0.0, 0.2))
    if kl > 0.01:
        lap = ease(tl.prog("sea_around", t, 0.4, 1.0) * 0.5 + tl.prog("sea_loop", t, 0.0, 0.7) * 0.5)
        K.inset(c, 640, 165, 400, 260, kl, lambda ic: loop_inset(ic, t, lap), bg=(20, 20, 50))
    kp = tl.prog("sea_four", t, 0.1, 0.3) * (1 - tl.prog("sea_climb", t, 0.0, 0.2))
    if kp > 0.01:
        kw = tl.prog("sea_pie", t, 0.0, 0.85)
        kland = tl.prog("sea_land1", t, 0.2, 0.45)
        K.inset(c, 640, 165, 500, 240, kp, lambda ic: pie_inset(ic, t, kw, kland))
    K.sub_band(c, tl, t)
    return c


# ======================================================================== swim

PATH1 = [MEET, (-14, -22), (12, -41), (45, -42), (80, -40), (115, -43), (150, -48), (182, -50)]
PATH2 = [(-184, -50), (-150, -52), (-115, -54), (-85, -58), (-64, -60), (-45, -46), (-34, -15), MEET]
EDGE_L = (-180, -50)


def icon_crew(c, tl, t, x, y, s, face=1, eyes=None):
    P.turtle_crew(c, tl, t, x, y, s, face, eyes=eyes)
    if s > 0.1:
        for k in range(3):
            c.ellipse(x - face * (70 + 30 * k) * s, y + 4, (30 - 6 * k) * s, 5 * s, (220, 240, 255), ol=None)


def path_u_for_lon(pts, lon_target):
    """Approximate fraction along a path where its longitude reaches lon_target."""
    sp = K.spline(pts)
    d = [0.0]
    for a, b in zip(sp, sp[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    for i, p in enumerate(sp):
        if p[0] >= lon_target:
            return d[i] / d[-1]
    return 1.0


def swim(tl, t):
    T = tl.t
    if t >= T("w_noedge"):
        return swim_close(tl, t)
    if t >= T("w_globe"):
        return swim_globe(tl, t)
    u_edge = path_u_for_lon(PATH1, 179.5)
    eyes = {}
    if T("w_edge") <= t < T("w_space", 0.2):
        eyes = {"whiskers": "closed" if t > T("w_edge", 0.6) else "wide", "luna": "wide", "pip": "wide"}
    if T("w_eyes") <= t:
        eyes = {"whiskers": "closed" if t < T("w_space") else "wide"}
    if t < T("w_fall", 0.62):
        # east along PATH1, the camera following, until the map's right edge
        keys = [(T("w_go"), 0.0), (T("w_more", 1), u_edge * 0.86), (T("w_edge", 1), u_edge * 0.94),
                (T("w_fall", 0.3), u_edge * 1.06)]
        u = K.smooth(t, keys, 0.3)
        lon_cam = K.smooth(t, [(T("w_go"), MEET[0] + 10), (T("w_more", 0.8), 140), (T("w_edge", 0.3), 150)], 0.4)
        c, v = K.map_view(lon_cam, -30, 2.0, t=t)
        K.map_labels(c, v, ["Africa", "Australia", "Indian Ocean", "Pacific Ocean", "Atlantic Ocean",
                            "South America", "Antarctica"])
        K.map_path(c, v, PATH1, min(u, u_edge), head=False)
        x, y, ang = K.path_point(v, PATH1, u)
        icon_crew(c, tl, t, x, y, 0.42, 1, eyes)
        K.map_clip(c, v)
        if T("w_edge") <= t:
            ex, ey = v.xy(180, -50)
            K.label(c, ex - 30, 180, "The edge?!", 32, tip=(ex, 260), k=tl.prog("w_edge", t, 0.2, 0.4),
                    col=(200, 40, 50))
        qk = tl.prog("w_fall", t, 0.32, 0.4) * (1 - tl.prog("w_fall", t, 0.55, 0.6))
        if qk > 0:
            ex, ey = v.xy(180, -50)
            c.push(ex + 60, ey - 40, pop(qk))
            K.text(c, 0, 0, "?", 80, (255, 236, 110), stroke=4)
            c.pop()
        wk = tl.prog("w_fall", t, 0.56, 0.62)
        if wk > 0:
            whip(c, wk)
    else:
        # out of the left edge, back in the ocean -- then zoom out to see both edges
        u2 = K.smooth(t, [(T("w_fall", 0.62), 0.0), (T("w_join"), 0.12), (T("w_joinact", 1), 0.3)], 0.3)
        zk = ease(tl.prog("w_join", t, 0.2, 1.0))
        cam = K.lerp_view((-150, -30, 2.0), (0, 0, 1.0), zk)
        c, v = K.map_view(*cam, t=t)
        K.map_labels(c, v, ["Pacific Ocean", "Atlantic Ocean", "South America"])
        if zk > 0:
            K.map_path(c, v, PATH1, zk * 0.999, head=False)
        u_in = path_u_for_lon(PATH2, -179.5)
        uu = u_in + (1 - u_in) * u2 if t > T("w_fall", 0.62) else 0
        K.map_path(c, v, PATH2, max(0.001, uu if zk <= 0 else uu), head=False)
        x, y, ang = K.path_point(v, PATH2, max(uu, 0.0))
        if t < T("w_fall", 0.72):
            x, y, ang = K.path_point(v, PATH2, lerp(0, u_in + 0.01, tl.prog("w_fall", t, 0.64, 0.72)))
        icon_crew(c, tl, t, x, y, lerp(0.42, 0.24, zk), 1, eyes)
        K.map_clip(c, v)
        sk = t - T("w_fall", 0.78)
        if 0 < sk < 1:
            for k in range(3):
                rr = 30 + 120 * sk + 25 * k
                c.ellipse(x, y + 6, rr, rr * 0.25, None, ol=mix((255, 255, 255), (64, 146, 222), sk), w=3)
        wk = 1 - tl.prog("w_fall", t, 0.62, 0.68)
        if 0 < wk < 1:
            whip(c, wk)
        # both edges glow: they are the same place
        jk = tl.prog("w_joinact", t, 0.0, 0.3)
        if jk > 0:
            lx, ly = v.xy(-180, -50)
            rx, ry = v.xy(180, -50)
            for ex, side in ((lx, 1), (rx, -1)):
                K.sparkles(c, ex, ly, 40, t, 8, jk, seed=int(ex))
                c.circle(ex, ly, 12 + 3 * math.sin(t * 6), (255, 236, 110), w=3)
            K.label(c, lx + 150, ly - 120, "Same ocean!", 28, tip=(lx + 8, ly - 10), k=jk)
            K.label(c, rx - 150, ry - 120, "Same ocean!", 28, tip=(rx - 8, ry - 10), k=tl.prog("w_joinact", t, 0.3, 0.6))
    K.sub_band(c, tl, t)
    return c


def whip(c, k):
    """Whip-pan streaks."""
    K.flash(c, 0.5 * math.sin(math.pi * k), (255, 255, 255))
    rng = np.random.default_rng(int(k * 20))
    for i in range(18):
        y = rng.uniform(0, H)
        x = rng.uniform(-200, W)
        c.line([(x, y), (x + rng.uniform(200, 500), y)], (255, 255, 255), rng.uniform(2, 6), cap=False)


def ring_on_globe(c, cx, cy, r, lon0, lat0, lat=-48, col=(255, 236, 110), front=True):
    pts = []
    for lo in np.arange(-180, 181, 4):
        x, y, vis = K.globe_xy(cx, cy, r, lo, lat, lon0, lat0)
        pts.append((x, y, vis))
    for i in range(0, len(pts) - 1, 2):
        a, b = pts[i], pts[i + 1]
        if a[2] == front and b[2] == front:
            c.line([a[:2], b[:2]], OUT if not front else col, 6 if front else 4)


def swim_globe(tl, t):
    T = tl.t
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    mk = tl.prog("w_globe", t, 0.0, 0.3)
    lon0 = -30 + 70 * (t - T("w_globe"))
    if mk < 1:
        K.globe_to_map(c, 1 - mk, t, 240, lon=lon0)
    else:
        lat0 = lerp(0, -28, ease(tl.prog("w_globe", t, 0.3, 0.6)))
        K.globe(c, 640, 360, 240, lon=lon0, lat=lat0, glow=0.3)
        ring_on_globe(c, 640, 360, 240, lon0, lat0, front=True)
        x, y, vis = K.globe_xy(640, 360, 240, lon0, -48, lon0, lat0)
        P.turtle(c, x, y + 4, 0.22, 1, t)
        K.label(c, 640, 70, "No edge! Round and round!", 32, k=tl.prog("w_globe", t, 0.5, 0.7))
        K.arrow(c, x + 60, y + 30, x + 150, y + 10, (255, 236, 110), 7, tl.prog("w_globe", t, 0.6, 0.8))
    K.sub_band(c, tl, t)
    return c


def swim_close(tl, t):
    """Close-up riding Shelby across the sea (for the punchline)."""
    T = tl.t
    c = Canvas(sea_bg().copy())
    P.sea_waves(c, t, HORIZON + 14, WL - 40, 6, (150, 206, 244), 60)
    laugh = t >= T("w_laugh")
    eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
    bob = 4 * math.sin(t * 2.5)
    P.turtle_crew(c, tl, t, 700, WL + 6 + bob, 1.15, 1, eyes=eyes, shelby_eyes="happy" if laugh else "open")
    underwater(c, [(380, WL + 2, 1080, H)])
    foam(c, 700, 240, t)
    for k in range(4):
        u = (t * 0.8 + k / 4) % 1
        c.ellipse(700 - 220 - 260 * u, WL + 4, 40 * (1 - u) + 10, 6, (230, 246, 255), ol=None)
    P.sea_waves(c, t, WL + 30, H - 20, 4, (160, 214, 248), 90, seed=7)
    if t >= T("w_purpose"):
        # a little sailor-song note or two
        for k in range(3):
            u = (t * 0.6 + k / 3) % 1
            K.text(c, 640 + 40 * k + 30 * u, 280 - 120 * u, "~" if k % 2 else "♪", 34, (255, 255, 255), stroke=2)
    gk = 1 - tl.prog("w_purpose", t, 0.0, 0.3)
    if gk > 0.01:
        def draw(ic):
            w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
            ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
            lon0 = 70 * t
            K.globe(ic, w / 2, h / 2, 90, lon=lon0, lat=-28)
            ring_on_globe(ic, w / 2, h / 2, 90, lon0, -28)
            x, y, _ = K.globe_xy(w / 2, h / 2, 90, lon0, -48, lon0, -28)
            P.turtle(ic, x, y + 2, 0.1, 1, t)
        K.inset(c, 200, 150, 260, 230, gk * tl.prog("w_noedge", t, 0.0, 0.15), draw, bg=(20, 20, 50))
    K.sub_band(c, tl, t)
    return c


# ==================================================================== remember

FACTS = ["The Earth is round, like a ball.",
         "Almost three quarters of the Earth is water.",
         "Maps show four directions: North, South, East and West."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [K.icon_globe, K.icon_water, K.icon_compass], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Is the Earth flat like a pancake, or round like a ball?",
                        ["Flat like a pancake", "Round like a ball"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.pancake, K.icon_globe], number=1, answer_text="Round like a ball!")
    else:
        c = K.quiz_card(t, "Is there more land, or more water on Earth?",
                        ["More water", "More land"], 0,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.water_icon, P.land_icon], number=2, answer_text="More water!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("evening").copy())
    spins = [(T("h_pip", 0.3), 300)]
    lon = sill_globe_lon(tl, t, spins)
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    e = ease(back)
    x = lerp(gcx, CUSH_X, e)
    y = lerp(gcy + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    sleep = t >= T("h_curl", 0.2)
    extra = {"whiskers": {"pose": "sleep", "dy": 6}} if sleep else None
    K.crew(c, tl, t, x, y, s, 1, fly=1 - back, extra=extra,
           look={"luna": (1, -0.5), "pip": (1, -0.5)})
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "The Seven Continents", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "sea": sea, "swim": swim, "remember": remember,
               "quiz": quiz, "home": home}
