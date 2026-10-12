"""Scenes of Episode 5 "Rivers and Lakes". One function per scene: (tl, t) -> Canvas.

The adventure (peak -> river -> lake -> sea) is one continuous camera journey over a big cached
panorama (props.panorama): from the snowy Alps, downhill along the river, through a lake, to the sea.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e05_rivers_lakes import props as P
from world.s1e03_five_oceans import props as P3
from world.s1e02_seven_continents import props as P2

CONTINUOUS = ("map", "river", "lake", "sea")


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


def hop(a, b, u, h=80):
    u = ease(u)
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 5, "Rivers and Lakes")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
WIN = (170, 40, 1110, SY - 34)


@lru_cache(None)
def rainy_home():
    c = Canvas(K.home_bg("day").copy())
    x0, y0, x1, y1 = WIN
    for x, y, s in ((960, 120, 1.6), (820, 90, 1.2), (400, 110, 1.5), (620, 150, 1.1), (260, 80, 1.0)):
        D.cloud(c, x, y, s, (190, 196, 210))
    a = (x0 * SS, y0 * SS, x1 * SS, y1 * SS)
    c.img.paste((120, 130, 152), a, Image.new("L", (a[2] - a[0], a[3] - a[1]), 120))
    for mx in (483, 797):
        c.rect(mx - 6, y0, mx + 6, y1, (255, 250, 240), w=2)
    return c.img


def window_rain(c, t, k=1.0):
    if k <= 0.01:
        return
    x0, y0, x1, y1 = WIN
    rng = np.random.default_rng(2)
    for i in range(int(70 * k)):
        x = rng.uniform(x0 + 6, x1 - 6)
        sp = rng.uniform(500, 700)
        y = y0 + (rng.uniform(0, 1) * (y1 - y0) + t * sp) % (y1 - y0)
        if y + 18 < y1:
            c.line([(x, y), (x - 3, y + 18)], (210, 225, 245), 2)
    # bigger drops trickling down the glass
    for i in range(7):
        x = rng.uniform(x0 + 20, x1 - 20)
        y = y0 + ((t * 30 + rng.uniform(0, 400)) % (y1 - y0 - 20))
        c.line([(x, y0 + 4), (x, y)], (190, 210, 236), 2)
        c.ellipse(x, y, 4, 6, (220, 236, 252), ol=(150, 170, 200), w=1.5)


def journey_inset(ic, t, k):
    """Rain -> river -> sea, as three little pictures with arrows."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (180, 220, 250)), (1, (230, 245, 255))]), (0, 0))
    xs = (90, 260, 430)
    P.rain_cloud(ic, xs[0], 70, 0.55, t, face=False, rain=1.0)
    ic.poly([(xs[1] - 60, 140), (xs[1] - 30, 60), (xs[1] + 60, 140)], P.GRASS, w=2.5)
    ic.line([(xs[1] - 40, 112), (xs[1] - 10, 120), (xs[1] + 20, 130), (xs[1] + 60, 136)], P.WATER, 9)
    ic.rect(xs[2] - 70, 90, xs[2] + 70, 150, P.WATER, r=10, w=2.5)
    for dx in (-40, 0, 40):
        ic.arc(xs[2] + dx, 110, 14, 6, 200, 340, (220, 240, 255), 3)
    for (a, b), kk in zip(((xs[0], xs[1]), (xs[1], xs[2])), (k * 2, k * 2 - 1)):
        K.arrow(ic, a + 50, 100, b - 70, 100, (240, 110, 90), 6, clamp(kk), head=14)
    for x, s in zip(xs, ("Rain", "River", "Sea")):
        K.text(ic, x, h - 22, s, 26, (48, 40, 60))


def sill_globe_lon(t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def sill(tl, t):
    T = tl.t
    c = Canvas(rainy_home().copy())
    window_rain(c, t)
    spins = [(T("s_adv", 0.2), 200), (T("s_hold", 0.3), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        grumpy = T("s_where") <= t < T("s_where", 1)
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit",
            look=(1, -1) if grumpy else (1, -0.4), head_dy=4 if grumpy else 0)
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_follow") else -1, proud=tl.talking("pip", t))
    else:
        luna_xy = hop((LUNA_X, SY), cush_spots["luna"], hopk, 160)
        pip_xy = hop((PIP_X, SY), cush_spots["pip"], clamp(hopk * 1.3), 90)
        if hopk < 1:
            K.cushion(c, CUSH_X, SY, CREW_S, t)
            kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes="wide")
            kat(c, tl, t, "luna", luna_xy[0], luna_xy[1], CAT_S, -1, "leap" if 0.05 < hopk < 0.95 else "sit")
            kat(c, tl, t, "pip", pip_xy[0], pip_xy[1], 1.1, -1)
        else:
            e = ease(fly)
            x = lerp(CUSH_X, gcx, e)
            y = lerp(SY, gcy + 40, e) - 80 * math.sin(math.pi * e)
            s = CREW_S * lerp(1, 0.15, e ** 1.5)
            K.crew(c, tl, t, x, y, s, 1, fly=min(1, fly * 3), eyes={"whiskers": "wide"},
                   look={"luna": (1, -1), "pip": (1, -1)})
    kj = tl.prog("s_adv", t, 0.15, 0.3) * (1 - tl.prog("s_follow", t, 0.5, 0.8))
    if kj > 0.01:
        jk = tl.prog("s_adv", t, 0.3, 0.9)
        K.inset(c, 640, 150, 520, 220, kj, lambda ic: journey_inset(ic, t, jk))
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

RIVERS = {
    "nile": [(33, -1), (32.5, 3.5), (31.5, 9.5), (32.5, 15.6), (33.5, 18), (31.5, 20), (31.5, 22), (32.8, 24),
             (32.6, 26), (31.2, 30), (31, 31.5)],
    "amazon": [(-76, -12), (-75.5, -7), (-74, -4.5), (-70, -3.5), (-65, -3.5), (-60, -3.2), (-55, -2.2),
               (-52, -1.5), (-50, -0.2)],
    "mississippi": [(-95, 47.5), (-93, 45), (-91, 42), (-90, 38.5), (-89.5, 35), (-91, 32), (-90, 29.5)],
    "yangtze": [(91, 33), (97, 32), (101, 28), (104, 29), (107, 29.7), (111, 30.5), (115, 30), (118, 31.5),
                (121.5, 31.5)],
    "volga": [(33, 57), (38, 57.5), (44, 56.3), (49, 55.7), (49, 53), (46, 49), (47.5, 46.5)],
    "ganges": [(79, 30.5), (81, 26), (85, 25.5), (88, 24.5), (90, 22.5)],
    "danube": [(8.5, 48), (12, 48.8), (16.5, 48.2), (19, 47.5), (20, 45), (23, 44), (27, 44), (29.5, 45)],
    "congo": [(25.5, -11), (26, -5), (25, 0.5), (21, 2), (18, 0), (16, -3), (12.5, -6)],
    "rhine": [(8.7, 46.6), (9.4, 47.6), (7.6, 47.6), (8.2, 49), (7.6, 50.4), (6.8, 51.2), (6, 51.9), (4.1, 52)],
    "murray": [(148, -36.5), (144, -35.8), (141, -34.2), (139.5, -35.5)],
    "mackenzie": [(-117, 61.5), (-121, 63.5), (-127, 66), (-134, 68.5)],
    "parana": [(-48, -20), (-52, -22), (-55, -25.5), (-58.5, -27.5), (-60, -32), (-58.5, -34)],
}
ALPS = (9.0, 46.6)
AMAZON_MID = (-60, -3.2)
GO_PATH = [(-62, -6), (-48, 10), (-28, 28), (-8, 40), ALPS]


def map_rivers(c, v, k=1.0, hl=None, hk=0.0, t=0.0):
    """Rivers as blue lines; hl names one to glow (hk 0..1)."""
    if k <= 0.01:
        return
    w = 2.2 * v.z ** 0.6
    for name, pts in RIVERS.items():
        s = [v.xy(lo, la) for lo, la in K.spline(pts, 8)]
        n = max(2, int(len(s) * clamp(k)))
        s = s[:n]
        if not any(-50 < x < W + 50 and -50 < y < H + 50 for x, y in s):
            continue
        big = name in ("nile", "amazon")
        ww = w * (1.6 if big else 1.0) * (1 + (1.2 * hk if name == hl else 0))
        if name == hl and hk > 0.01:
            c.line(s, (255, 236, 110), ww + 10 * hk * (0.8 + 0.2 * math.sin(t * 6)))
        c.line(s, (30, 70, 140), ww + 3)
        c.line(s, (90, 180, 255), ww)


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40
    end = -14 * (tl.t("m_narr", 1) - t0) + 40
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_flat", t, 0.0, 0.3)))


V0 = (0, 0, 1.0)
VN = (25, 14, 2.2)
VA = (-60, -8, 2.4)
VZ = (ALPS[0], ALPS[1] - 1, 4.5)


def map_cam(tl, t):
    k1 = ease(tl.prog("m_nile", t, 0.0, 0.35))
    k2 = ease(tl.prog("m_amazon", t, 0.0, 0.3))
    k3 = ease(tl.prog("m_path", t, 0.05, 0.9))
    if k3 > 0:
        return K.lerp_view(VA, VZ, k3)
    if k2 > 0:
        return K.lerp_view(VN, VA, k2)
    return K.lerp_view(V0, VN, k1)


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        K.globe(c, lerp(760, 640, k), lerp(300, 360, k), r, lon=space_globe_lon(tl, t), lat=18, glow=0.5)
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        K.crew(c, tl, t, lerp(-200, 200, fk), lerp(820, 640, fk), lerp(1.0, 0.75, fk), 1, fly=1.0,
               look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_rivers"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        if k >= 1:
            K.map_labels(c, K.MapView(0, 0, 1), "continents", tl.prog("m_flat", t, 0.85, 1.0))
        K.crew(c, tl, t, 170, 660, 0.75, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    cam = map_cam(tl, t)
    c, v = K.map_view(*cam, t=t)
    lab = 1 - tl.prog("m_nile", t, 0.0, 0.2)
    K.map_labels(c, v, "continents", lab)
    rk = tl.prog("m_rivers", t, 0.3, 1.0) * 0.5 + tl.prog("m_riv", t) * 0.5
    hl, hk = None, 0.0
    if T("m_nile") <= t < T("m_amazon"):
        hl, hk = "nile", tl.prog("m_nile", t, 0.3, 0.5)
    elif T("m_amazon") <= t < T("m_path"):
        hl, hk = "amazon", tl.prog("m_amazon", t, 0.25, 0.45)
    elif t >= T("m_path"):
        hl, hk = "rhine", tl.prog("m_path", t, 0.6, 0.85)
    map_rivers(c, v, rk, hl, hk, t)
    # sparkles running along the rivers when they appear
    if T("m_rivers") <= t < T("m_nile"):
        K.label(c, 640, 46, "Blue lines = rivers", 30, k=tl.prog("m_rivers", t, 0.4, 0.6)
                * (1 - tl.prog("m_nile", t, 0.0, 0.1)))
    if hl == "nile":
        x, y = v.xy(32, 16)
        K.label(c, x + 340, y + 110, "The Nile: very, very long!", 30, tip=(x + 70, y + 40), k=tl.prog("m_nile", t, 0.4, 0.6))
        K.map_label(c, v, 20, 6, "Africa", 30, k=tl.prog("m_nile", t, 0.3, 0.5))
        # a little ruler showing its length
        a, b = v.xy(33, -1), v.xy(31, 31.5)
        rk2 = tl.prog("m_nileact", t, 0.0, 0.7)
        if rk2 > 0:
            xx = max(a[0], b[0]) + 45
            K.arrow(c, xx, a[1], xx, lerp(a[1], b[1], rk2), (255, 236, 110), 7, 1.0, head=18)
            K.arrow(c, xx, lerp(a[1], b[1], rk2), xx, a[1], (255, 236, 110), 7, 1.0, head=18)
    if hl == "amazon":
        x, y = v.xy(-62, -3.2)
        K.label(c, x + 40, y - 150, "The Amazon: the most water!", 30, tip=(x, y - 10),
                k=tl.prog("m_amazon", t, 0.4, 0.6))
        K.map_label(c, v, -58, -16, "South America", 28, k=tl.prog("m_amazon", t, 0.3, 0.5))
        sk = tl.prog("m_amzact", t, 0.0, 1.0) * (1 - tl.prog("m_path", t, 0.0, 0.2))
        if sk > 0:
            for i, (lo, la) in enumerate(RIVERS["amazon"][2::2]):
                px, py = v.xy(lo, la)
                u = (t * 1.2 + i * 0.3) % 1
                for j in (-1, 1):
                    c.circle(px + j * 14 * u, py - 26 * math.sin(math.pi * u), 5 * (1 - u) + 1, (150, 210, 255),
                             w=1.5)
    if t >= T("m_path"):
        K.map_label(c, v, ALPS[0] + 0.5, ALPS[1] + 1.7, "The Alps", 34, k=tl.prog("m_path", t, 0.75, 0.9))
        u = tl.prog("m_path", t, 0.1, 0.85)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        x, y, ang = K.path_point(v, GO_PATH, u)
        K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, 1, fly=1)
        K.flash(c, tl.prog("m_path", t, 0.9, 1.0))
    else:
        laugh = T("m_laugh") <= t < T("m_alps")
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
        K.crew(c, tl, t, 170, 660, 0.75, 1, fly=1.0, eyes=eyes,
               look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
               extra={"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None)
        bk = tl.prog("m_bath", t, 0.2, 0.4) * (1 - tl.prog("m_laugh", t, 0.6, 1.0))
        if bk > 0.01:
            K.bubble(c, 300, 430, 100, 66, bk, tail=(150, 570))
            c.push(300, 440, bk)
            c.ellipse(0, 10, 70, 22, (250, 250, 255), w=3)
            c.ellipse(0, 4, 60, 12, P.WATER, ol=None)
            for k in range(4):
                c.circle(-36 + 24 * k, -8 - 6 * (k % 2), 10, (255, 255, 255), w=1.5)
            c.pop()
    return c


# ================================================================== adventure

CLOUD = (380, 112)
SNOW_SPOT = (440, 262)
HOVER = (1080, 330)
PEAK_CAM = (720, 360)
LAKE_CAM = (2330, 770)
SEA_CAM = (4070, 820)
CREW_S2 = 0.95


def cam_for(u):
    x, y, _ = P.path_at("r1", u)
    return x + 160, y - 110


def floating_crew(c, tl, t, x, y, s=CREW_S2, face=1, fly=0.0, **kw):
    """The friends on the cushion, floating at water level y (with a little water in front)."""
    K.crew(c, tl, t, x, y + 12 * s, s, face, fly=fly, **kw)
    if fly < 0.5:
        P.water_front(c, x, y + 4, 250 * s, t, depth=12)


def drip_on(c, tl, t, x, y, s=1.0, **kw):
    P.drip(c, x, y - 4 + 3 * math.sin(t * 3), s, t, tl.mouth("drip", t), **kw)


def snow_drips(c, t, k):
    """Melting snow: drops falling from the snow's edge."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(8)
    for i in range(int(12 * k)):
        x = rng.uniform(360, 820)
        y0 = P.SNOW_BOTTOM_Y - 6 + (x - 580) * 0.02
        u = (t * 0.9 + rng.random()) % 1
        c.ellipse(x, y0 + u * 40, 3, 5, (150, 210, 255), ol=P.DROP_D, w=1)


def streams(c, cam, t, k, hl=0.0):
    """The tiny streams on the mountain side (k grows them)."""
    if k <= 0.01:
        return
    for i, key in enumerate(("s0", "s1", "s2", "s3")):
        kk = clamp(k * 1.4 - i * 0.12)
        if kk <= 0:
            continue
        s, d = P._path(key)
        n = max(2, int(len(s) * kk))
        pts = s[:n]
        if hl > 0.01:
            c.line(pts, (255, 236, 110), 12 + 3 * math.sin(t * 6))
        c.line(pts, OUT, 9)
        c.line(pts, P.WATER, 6)
        if kk >= 1:
            P.flow(c, cam, key, 6, 6, t, speed=60, spacing=46, lanes=(0.0,), dash=8, lw=2)


def peak(tl, t):
    T = tl.t
    gk = ease(tl.prog("p_go", t, 0.2, 1.0))
    cu_end = 0.14
    cx, cy = PEAK_CAM
    ex, ey = cam_for(cu_end)
    c, cam = P.view(lerp(cx, ex, gk), lerp(cy, ey, gk))
    c.push(-cam.x0, -cam.y0)
    # sun peeks out to melt the snow
    sk = ease(tl.prog("p_melt", t, 0.2, 0.5))
    if sk > 0:
        P.sun(c, 1250, lerp(260, 110, sk), 46, t)
    streams(c, cam, t, tl.prog("p_meltact", t, 0.3, 1.0) * 0.6 + tl.prog("p_streams", t, 0.0, 0.6) * 0.4,
            hl=tl.prog("p_streams", t, 0.3, 0.5) * (1 - tl.prog("p_join", t, 0.6, 0.9)))
    snow_drips(c, t, tl.prog("p_melt", t, 0.4, 0.8) * (1 - tl.prog("p_go", t, 0.0, 0.5)))
    P.flow(c, cam, "r1", *P.RIVER1_W, t, speed=120, spacing=90, lanes=(-0.2, 0.15))
    # the little rain cloud
    P.rain_cloud(c, *CLOUD, 1.0, t, rain=0.3 if t > T("p_narr", 0.5) else 0.0,
                 eyes="closed" if T("p_drop") <= t < T("p_drop", 0.4) else "open")
    # Drip: falls from the cloud, lands on the snow, rides the stream down to the river
    if t >= T("p_drop", 0.25):
        fk = tl.prog("p_drop", t, 0.25, 0.8)
        if fk < 1:
            x, y = lerp(CLOUD[0] + 10, SNOW_SPOT[0], fk), lerp(CLOUD[1] + 60, SNOW_SPOT[1], ease(fk) ** 1.6)
            P.drip(c, x, y, 1.1, t, eyes="happy")
        else:
            uk = tl.prog("p_meltact", t, 0.4, 1.0) * 0.08 + tl.prog("p_join", t, 0.0, 0.9) * 0.92
            if uk <= 0:
                x, y = SNOW_SPOT[0], SNOW_SPOT[1]
                bounce = abs(math.sin(t * 5)) * 6 if tl.talking("drip", t) else 0
                P.drip(c, x, y - bounce, 1.3, t, tl.mouth("drip", t), look=(1, 0))
            elif uk < 1 or t < T("p_go", 0.2):
                if uk < 0.02:
                    x, y = lerp(SNOW_SPOT[0], P.STREAMS[0][0][0], uk / 0.02), lerp(SNOW_SPOT[1], P.STREAMS[0][0][1],
                                                                                    uk / 0.02)
                else:
                    x, y, _ = P.path_at("s0", (uk - 0.02) / 0.98)
                P.drip(c, x, y + 8, 1.3, t, tl.mouth("drip", t), eyes="happy" if uk < 1 else "open", look=(1, 0))
            else:
                du = lerp(0.0, cu_end + 0.05, ease(tl.prog("p_go", t, 0.2, 1.0)))
                x, y, _ = P.path_at("r1", du)
                drip_on(c, tl, t, x, y + 8, 1.3)
    # the friends: fly in, hover, then land on the river and slide away
    lk = ease_out(tl.prog("p_land", t, 0.0, 0.8))
    if t < T("p_go", 0.2):
        x, y = lerp(1500, HOVER[0], lk), lerp(80, HOVER[1], lk)
        eyes = {"whiskers": "wide"} if T("p_melt") <= t < T("p_meltact") else {}
        K.crew(c, tl, t, x, y, CREW_S2, -1, fly=1.0, eyes=eyes,
               look={"luna": (-1, 0.3), "whiskers": (-1, 0.2), "pip": (-1, 0.3)})
    else:
        jk = tl.prog("p_go", t, 0.2, 0.5)
        x0, y0, _ = P.path_at("r1", 0.06)
        if jk < 1:
            x, y = hop(HOVER, (x0, y0 + 10), jk, 60)
            K.crew(c, tl, t, x, y, CREW_S2, 1, fly=1 - jk, eyes={"whiskers": "wide"})
        else:
            u = lerp(0.06, cu_end, ease(tl.prog("p_go", t, 0.5, 1.0)))
            x, y, _ = P.path_at("r1", u)
            floating_crew(c, tl, t, x, y, eyes={"luna": "happy", "pip": "happy", "whiskers": "wide"})
            sk2 = t - T("p_go", 0.5)
            if 0 < sk2 < 0.8:
                for k in range(3):
                    rr = 40 + 120 * sk2 + 30 * k
                    c.ellipse(x0, y0 + 8, rr, rr * 0.2, None, ol=mix((240, 250, 255), P.WATER, sk2 / 0.8), w=3)
    c.pop()
    # labels (screen space)
    def sxy(px, py):
        return px - cam.x0, py - cam.y0
    kt = tl.prog("p_streams", t, 0.35, 0.55) * (1 - tl.prog("p_join", t, 0.5, 0.7))
    tx, ty = sxy(640, 420)
    K.label(c, tx - 230, ty + 150, "Tiny streams", 30, tip=(tx - 40, ty), k=kt)
    kj = tl.prog("p_join", t, 0.4, 0.6) * (1 - tl.prog("p_river", t, 0.0, 0.2))
    jx, jy = sxy(*P.J)
    K.label(c, jx - 120, jy + 150, "They join together...", 30, tip=(jx - 6, jy + 8), k=kj)
    kr = tl.prog("p_river", t, 0.45, 0.65) * (1 - tl.prog("p_jump", t, 0.0, 0.3))
    rx, ry, _ = P.path_at("r1", 0.2)
    rx, ry = sxy(rx, ry)
    K.label(c, rx - 40, ry - 150, "...into a river!", 34, tip=(rx, ry - 30), k=kr, col=(30, 90, 170))
    km = tl.prog("p_melt", t, 0.45, 0.65) * (1 - tl.prog("p_streams", t, 0.0, 0.2))
    mx, my = sxy(600, 336)
    K.label(c, mx + 120, my + 150, "Melting snow", 30, tip=(mx, my + 10), k=km)
    K.sub_band(c, tl, t)
    return c


# ----------------------------------------------------------------------- river

def river_u(tl, t):
    """The cushion's place along the upper river."""
    T = tl.t
    keys = [(T("v_open"), 0.14), (T("v_hello", 1), 0.26), (T("v_down", 1), 0.36), (T("v_downact", 1), 0.40),
            (T("v_snack", 1), 0.42), (T("v_paddle", 0.55), 0.41), (T("v_paddle", 0.62), 0.415),
            (T("v_paddle", 0.95), 0.56), (T("v_laugh", 1), 0.58), (T("v_on", 1), 0.93)]
    return K.smooth(t, keys, 0.2)


def river(tl, t):
    T = tl.t
    u = river_u(tl, t)
    cx, cy = cam_for(min(u, 0.8))
    k_on = ease(tl.prog("v_on", t, 0.3, 1.0))
    cx, cy = lerp(cx, LAKE_CAM[0], k_on), lerp(cy, LAKE_CAM[1], k_on)
    c, cam = P.view(cx, cy)
    c.push(-cam.x0, -cam.y0)
    P.flow(c, cam, "r1", *P.RIVER1_W, t, speed=130, spacing=90)
    x, y, ang = P.path_at("r1", u)
    paddling = T("v_paddle") <= t < T("v_paddle", 0.62)
    sliding = T("v_paddle", 0.62) <= t < T("v_purpose")
    backwards = T("v_snack", 0.6) <= t < T("v_laugh", 0.5)
    face = -1 if backwards else 1
    # Ollie: slides in from behind, passes, then swims along in front
    ok = tl.prog("v_hello", t, 0.0, 1.0)
    ou = lerp(u - 0.25, u + 0.22, ease(ok)) if t < T("v_name") else u + 0.22
    if t < T("v_hello"):
        ou = u - 0.3
    ox, oy, _ = P.path_at("r1", clamp(ou))
    on_back = t >= T("v_cant")
    o_eyes = "happy" if (T("v_cant") <= t < T("v_cant", 0.3)) or t >= T("v_laugh") else "open"
    if ou > 0 and t >= T("v_hello"):
        P.otter(c, ox, oy + 10, 0.85, 1 if not on_back else -1, t, tl.mouth("ollie", t), o_eyes,
                "back" if on_back else "swim", look=(-1, 0) if T("v_name") <= t < T("v_snack") else (0, 0))
        P.water_front(c, ox, oy + 10, 170, t, depth=10)
    # Drip bobs next to the cushion
    dx, dy, _ = P.path_at("r1", clamp(u + 0.115 * face))
    drip_on(c, tl, t, dx, dy + 6, 1.15, eyes="happy" if T("v_laugh") <= t < T("v_on") else "open",
            look=(-1, 0) if backwards else (1, 0))
    # the friends
    eyes, extra = {}, {}
    if T("v_hello") <= t < T("v_name"):
        eyes = {"whiskers": "wide", "luna": "wide", "pip": "wide"}
    if paddling:
        eyes = {"whiskers": "wide"}
        extra = {"whiskers": {"pose": "crouch", "dy": -4}}
    if sliding:
        eyes = {"whiskers": "wide", "luna": "wide", "pip": "wide"}
    if T("v_purpose", 0.45) <= t < T("v_on"):
        extra = {"whiskers": {"pose": "sleep", "dy": 4}}
    if T("v_laugh") <= t < T("v_on"):
        eyes = {"luna": "happy", "pip": "happy"}
        extra.update({"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}})
    jit = math.sin(t * 40) * 3 if paddling else 0
    floating_crew(c, tl, t, x + jit, y, CREW_S2, face, eyes=eyes, extra=extra,
                  look={"luna": (face, 0), "pip": (face, 0)})
    if paddling:
        # paws paddling like mad + splashes behind + sweat
        wx, wy = x - face * 52 * CREW_S2, y - 30
        for k in range(2):
            a = t * 22 + k * math.pi
            px, py = wx - face * 30 + math.cos(a) * 16, wy + 14 + math.sin(a) * 10
            c.circle(px, py, 8, D.WHISKERS["body"], w=2)
        rng = np.random.default_rng(int(t * 12))
        for k in range(6):
            c.circle(x + face * 150 + rng.uniform(-30, 30), y - rng.uniform(0, 60), rng.uniform(4, 9),
                     P.FOAM, ol=P.WATER_D, w=1.5)
        c.ellipse(wx + 20, wy - 70, 4, 7, (170, 220, 255), ol=P.DROP_D, w=1.5)
    if sliding and t < T("v_cant"):
        for k in range(4):
            yy = y - 20 - k * 22
            c.line([(x - 200 - 30 * k, yy), (x - 120 - 30 * k, yy)], (255, 255, 255), 4)
    c.pop()
    # teaching: big downhill arrows
    dk = tl.prog("v_down", t, 0.35, 0.6) * (1 - tl.prog("v_snack", t, 0.0, 0.15))
    if dk > 0.01:
        a = P.path_at("r1", clamp(u - 0.25))
        b = P.path_at("r1", clamp(u + 0.25))
        ax, ay, bx, by = a[0] - cam.x0, a[1] - cam.y0 - 170, b[0] - cam.x0, b[1] - cam.y0 - 170
        K.arrow(c, ax, ay, bx, by, (255, 236, 110), 12, ease_out(dk), head=30)
        K.label(c, (ax + bx) / 2, (ay + by) / 2 - 60, "Downhill!", 40, k=dk, col=(30, 90, 170))
        K.label(c, 150, 120, "High mountains", 26, k=tl.prog("v_down", t, 0.4, 0.6) * (1 - tl.prog("v_snack", t)))
        K.label(c, 1120, 620, "Low sea", 26, k=tl.prog("v_down", t, 0.7, 0.9) * (1 - tl.prog("v_snack", t)))
    # Whiskers' fish snack, far up the river
    bk = tl.prog("v_snack", t, 0.1, 0.3) * (1 - tl.prog("v_paddle", t, 0.0, 0.1))
    if bk > 0.01:
        K.bubble(c, 230, 150, 110, 70, bk, tail=(x - cam.x0 - 50, y - cam.y0 - 100))
        P2.fish_snack(c, 230, 150, 2.0 * bk, (250, 160, 90))
    uk = tl.prog("v_paddle", t, 0.15, 0.3) * (1 - tl.prog("v_paddle", t, 0.55, 0.62))
    K.label(c, x - cam.x0 + 60, y - cam.y0 - 200, "Paddle! Paddle!", 30, k=uk)
    ck = tl.prog("v_cant", t, 0.4, 0.6) * (1 - tl.prog("v_purpose", t, 0.0, 0.2))
    K.label(c, 640, 70, "Water always flows downhill", 32, k=ck)
    K.sub_band(c, tl, t)
    return c


# ------------------------------------------------------------------------ lake

LAKE_SPOT = (2230, 850)
OLLIE_LAKE = (2480, 872)


def lake_animals(c, tl, t):
    T = tl.t
    dk = tl.prog("l_drinkact", t, 0.0, 0.3) * (1 - tl.prog("l_next", t, 0.0, 0.3))
    drink = max(0.15 + 0.1 * math.sin(t * 0.7), dk)
    P.deer(c, 1985, 955, 0.8, 1, t, drink)
    P.heron(c, 2640, 790, 0.75, -1, t, dip=tl.prog("l_drinkact", t, 0.2, 0.5) * (1 - tl.prog("l_go", t, 0, 0.3)))
    bx = 2560 - 40 * math.sin(t * 0.25)
    P.duck(c, bx, 905, 0.8, -1, t)
    for k in range(3):
        P.duck(c, bx + 44 + 30 * k, 908, 0.45, -1, t + k, baby=True)


def lake(tl, t):
    T = tl.t
    gk = ease(tl.prog("l_go", t, 0.15, 1.0))
    c, cam = P.view(lerp(LAKE_CAM[0], SEA_CAM[0], gk), lerp(LAKE_CAM[1], SEA_CAM[1], gk))
    c.push(-cam.x0, -cam.y0)
    P.flow(c, cam, "r1", *P.RIVER1_W, t, speed=130, spacing=90)
    P.flow(c, cam, "r2", *P.RIVER2_W, t, speed=110, spacing=110)
    cx_, cy_, rx_, ry_ = P.LAKE
    for i, (lx, ly) in enumerate(((2150, 800), (2420, 830), (2620, 860), (2300, 900))):
        P.ripples(c, lx, ly, t, 2, 50, 8, seed=i)
    lake_animals(c, tl, t)
    # cushion: from the river mouth into the lake, then out to the river and down to the sea
    ik = ease(tl.prog("l_open", t, 0.0, 0.9))
    x1, y1, _ = P.path_at("r1", 0.93)
    if gk <= 0:
        x, y = lerp(x1, LAKE_SPOT[0], ik), lerp(y1, LAKE_SPOT[1], ik)
    else:
        u2 = ease(tl.prog("l_go", t, 0.0, 1.0)) * 0.85
        x2, y2, _ = P.path_at("r2", u2)
        k0 = ease(tl.prog("l_go", t, 0.0, 0.25))
        x, y = lerp(LAKE_SPOT[0], x2, k0), lerp(LAKE_SPOT[1], y2, k0)
    # Ollie floats on his back
    P.otter(c, lerp(2200, OLLIE_LAKE[0], ik) + (gk * 1400), OLLIE_LAKE[1] + 3 * math.sin(t * 2), 0.85, -1, t,
            tl.mouth("ollie", t), "happy" if T("l_fresh") <= t < T("l_animals") else "open", "back",
            wave=1.0 if T("l_animals", 0.9) <= t < T("l_next") else 0.0)
    P.water_front(c, lerp(2200, OLLIE_LAKE[0], ik) + gk * 1400, OLLIE_LAKE[1], 180, t, depth=8)
    # Whiskers' sip
    sip = T("l_sip") <= t < T("l_fresh", 1)
    eyes, extra = {}, {}
    if sip:
        extra = {"whiskers": {"pose": "crouch", "dy": 0,
                              "mouth": 0.4 + 0.3 * math.sin(t * 18) if t < T("l_fresh") else tl.mouth("whiskers", t)}}
        eyes = {"whiskers": "closed" if t < T("l_fresh") else "wide"}
    if T("l_last") <= t < T("l_last", 1):
        eyes = {"whiskers": "closed"} if t > T("l_last", 0.75) else {}
    if sip:
        s_ = CREW_S2
        K.crew(c, tl, t, x, y + 12 * s_, s_, 1, who=("luna", "pip"), look={"luna": (-1, 0.3), "pip": (-1, 0.3)})
        kat(c, tl, t, "whiskers", x - 100 * s_, y + 12 * s_ - 40 * s_, 0.62 * s_, -1, "crouch",
            eyes=eyes["whiskers"], mouth=extra["whiskers"]["mouth"])
        P.water_front(c, x, y + 4, 250 * s_, t, depth=12)
        if t < T("l_fresh"):
            P.ripples(c, x - 190 * s_, y + 8, t, 3, 30, 6, speed=1.4)
    else:
        floating_crew(c, tl, t, x, y, CREW_S2, 1, eyes=eyes, extra=extra)
    dx = x + 170 if not sip else x + 160
    drip_on(c, tl, t, dx, y + 4, 1.15)
    c.pop()
    # teaching insets
    kl = tl.prog("l_what", t, 0.2, 0.4) * (1 - tl.prog("l_last", t, 0.0, 0.2))
    if kl > 0.01:
        lk = tl.prog("l_whatact", t, 0.0, 0.8)
        K.inset(c, 640, 170, 460, 280, kl, lambda ic: P.lake_map(ic, lk, t))
    kb = tl.prog("l_last", t, 0.1, 0.3) * (1 - tl.prog("l_sip", t, 0.0, 0.2))
    if kb > 0.01:
        wx, wy = x - cam.x0 - 50, y - cam.y0 - 110
        K.bubble(c, wx - 150, wy - 150, 90, 66, kb, tail=(wx - 20, wy - 20))
        c.push(wx - 150, wy - 150, kb)
        P3.icon_salt(c, 0, 0, 50, t)
        c.pop()
    kf = tl.prog("l_fresh", t, 0.3, 0.6) * (1 - tl.prog("l_next", t, 0.0, 0.2))
    K.label(c, 640, 90, "Fresh water: not salty!", 38, k=kf, col=(30, 110, 60))
    K.sub_band(c, tl, t)
    return c


# ------------------------------------------------------------------------- sea

SEA_SPOT = (3930, 985)
DRIP_SEA = (4080, 975)
OLLIE_SEA = (3790, 1000)
NEW_CLOUD = (4180, 600)


def sea_waves(c, cam, t):
    rng = np.random.default_rng(3)
    for k in range(26):
        x = rng.uniform(3700, 4800)
        y = rng.uniform(800, 1200)
        if x < cam.x0 - 50 or x > cam.x0 + W + 50:
            continue
        xx = x + 20 * math.sin(t * 0.8 + k)
        if y > 960 or x > 3800:
            c.arc(xx, y, 22, 7, 200, 340, (180, 222, 250), 3)


def sea(tl, t):
    T = tl.t
    c, cam = P.view(*SEA_CAM)
    c.push(-cam.x0, -cam.y0)
    P.sun(c, 4560, 560, 52, t)
    P.flow(c, cam, "r2", *P.RIVER2_W, t, speed=110, spacing=110)
    sea_waves(c, cam, t)
    # the friends float in at the river mouth
    ak = ease(tl.prog("e_open", t, 0.0, 0.9))
    x2, y2, _ = P.path_at("r2", 0.85)
    x, y = lerp(x2, SEA_SPOT[0], ak), lerp(y2, SEA_SPOT[1], ak)
    P.otter(c, OLLIE_SEA[0] + 30 * math.sin(t * 0.4), OLLIE_SEA[1], 0.8, 1, t, tl.mouth("ollie", t),
            "happy" if t >= T("e_bye") else "open", "back", wave=1.0 if t >= T("e_bye") else 0.0)
    P.water_front(c, OLLIE_SEA[0] + 30 * math.sin(t * 0.4), OLLIE_SEA[1], 170, t, depth=8)
    look_up = T("e_up") <= t < T("e_rain", 1)
    look = {w_: (1, -1) for w_ in ("luna", "whiskers", "pip")} if look_up else {}
    eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if t >= T("e_bye") else {}
    floating_crew(c, tl, t, x, y, CREW_S2, 1, eyes=eyes, look=look)
    # Drip: bobbing, jumping for joy, then rising as invisible vapour into a cloud
    rk = ease(tl.prog("e_up", t, 0.4, 1.0) * 0.35 + tl.prog("e_rise", t, 0.0, 1.0) * 0.65)
    dx = lerp(x + 150, DRIP_SEA[0], ak)
    dy = DRIP_SEA[1]
    ck = ease(tl.prog("e_rise", t, 0.6, 1.0) * 0.5 + tl.prog("e_vapour", t, 0.0, 0.6) * 0.5)
    cloud_x = NEW_CLOUD[0] - 520 * ease(tl.prog("e_rain", t, 0.1, 1.0)) * (1 - ease(tl.prog("e_roundact", t, 0.0, 1.0)))
    if rk < 1:
        jump = abs(math.sin(t * 7)) * 30 if T("e_made") <= t < T("e_made", 1) else 0
        yy = lerp(dy, NEW_CLOUD[1] + 30, rk) - jump
        P.drip(c, dx + 40 * math.sin(rk * 6), yy + 3 * math.sin(t * 3), 1.2, t, tl.mouth("drip", t),
               eyes="happy" if t >= T("e_made") and t < T("e_end") else "open", vapour=rk, look=(0, -1 if rk else 0))
    # vapour rising from the sea
    vk = tl.prog("e_up", t, 0.5, 1.0) * (1 - tl.prog("e_cycle", t, 0.0, 0.2))
    if vk > 0.01:
        for k in range(7):
            bx = 3900 + k * 110
            u = (t * 0.35 + k / 7) % 1
            pts = [(bx + 8 * math.sin(j * 0.8 + t * 3 + k), 940 - j * 14 - u * 160) for j in range(9)]
            c.line(pts, mix((255, 255, 255), (200, 230, 255), u), 3 * vk)
    if ck > 0.01:
        P.rain_cloud(c, cloud_x, NEW_CLOUD[1], ck, t, rain=tl.prog("e_rain", t, 0.3, 0.6) * (1 - tl.prog(
            "e_cycle", t, 0.0, 0.2)), eyes="closed" if T("e_bye") <= t else "open")
        if rk >= 1:
            # Drip peeks out of the bottom of his new cloud
            P.drip(c, cloud_x + 10, NEW_CLOUD[1] + 95 * ck, 0.9 * ck, t, tl.mouth("drip", t), eyes="happy"
                   if t >= T("e_byeact") else "open", wave=1.0 if t >= T("e_bye") else 0.0)
    c.pop()
    # labels and the water cycle diagram
    vl = tl.prog("e_vapour", t, 0.3, 0.5) * (1 - tl.prog("e_rain", t, 0.0, 0.2))
    K.label(c, 1000, 380, "Invisible vapour", 30, tip=(860, 330), k=vl)
    K.label(c, 1000, 230, "Clouds", 30, tip=(cloud_x - cam.x0 + 100, NEW_CLOUD[1] - cam.y0), k=tl.prog(
        "e_vapour", t, 0.7, 0.9) * (1 - tl.prog("e_rain", t, 0.0, 0.2)))
    ik = tl.prog("e_cycle", t, 0.0, 0.12) * (1 - tl.prog("e_bye", t, 0.0, 0.25))
    if ik > 0.01:
        ks = [tl.prog("e_cycle", t, 0.1 + 0.22 * i, 0.3 + 0.22 * i) for i in range(4)]
        du = (tl.prog("e_cycle", t, 0.1, 0.98) + tl.prog("e_round", t, 0.0, 1.0) + tl.prog("e_roundact", t)) % 1.0
        K.inset(c, 640, 285, 820, 480, ik, lambda ic: P.cycle_scene(ic, t, ks, du))
        K.label(c, 640, 40, "The water cycle", 34, k=tl.prog("e_round", t, 0.1, 0.3), col=(30, 90, 170))
    K.sub_band(c, tl, t)
    return c


# ==================================================================== remember

FACTS = ["Rivers flow downhill, all the way to the sea.",
         "River and lake water is fresh, not salty.",
         "Water goes round and round in the water cycle."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_downhill, P.icon_fresh, P.icon_cycle], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Does a river flow uphill, or downhill?", ["Uphill", "Downhill"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_uphill, P.icon_downhill_q], number=1, answer_text="Downhill!")
    else:
        c = K.quiz_card(t, "Is lake water salty, or fresh?", ["Salty", "Fresh"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P3.icon_salt, P.icon_fresh], number=2, answer_text="Fresh, not salty!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def rainbow(c, k):
    if k <= 0.01:
        return
    cols = [(240, 90, 90), (250, 170, 70), (250, 230, 90), (110, 200, 110), (90, 160, 240), (150, 110, 220)]
    for i, col in enumerate(cols):
        r = 380 - i * 13
        c.arc(640, 470, r, r * 0.9, 180, 180 + 180 * k, mix(col, (238, 160, 140), 0.25), 13)


def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("evening").copy())
    rainbow(c, ease(tl.prog("h_narr", t, 0.4, 1.0)))
    for mx in (483, 797):
        c.rect(mx - 6, WIN[1], mx + 6, WIN[3], (255, 250, 240), w=2)
    lon = sill_globe_lon(t, [(T("h_pip", 0.3), 300)])
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    # Drip on the window glass
    dk = tl.prog("h_pip", t, 0.2, 0.5)
    if dk > 0:
        wink = T("h_wink") <= t < T("h_wink", 0.8)
        P.drip(c, 960, lerp(150, 230, ease(dk)) + 4 * math.sin(t * 2), 1.4, t,
               eyes="happy" if wink else "open", look=(-1, 0.5))
        if wink:
            K.sparkles(c, 960, 200, 60, t, 6, 1.0, seed=3)
    gcx, gcy = K.GLOBE_X, SY - 170
    e = ease(back)
    x = lerp(gcx, CUSH_X, e)
    y = lerp(gcy + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    sleep = t >= T("h_curl", 0.2)
    extra = {"whiskers": {"pose": "sleep", "dy": 6}} if sleep else None
    lk = (1, -1) if t >= T("h_pip") else (1, -0.5)
    K.crew(c, tl, t, x, y, s, 1, fly=1 - back, extra=extra, look={"luna": lk, "pip": lk})
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Deserts", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "peak": peak, "river": river, "lake": lake,
               "sea": sea, "remember": remember, "quiz": quiz, "home": home}
