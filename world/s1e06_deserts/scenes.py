"""Scenes of Episode 6 "Deserts". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e06_deserts import props as P

CONTINUOUS = ("map",)            # the sill flashes white straight into space
EXTRA_CUTS = ()


def hop(a, b, u, h=80):
    """Point on a jump arc from a to b."""
    u = ease(u)
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


def blend_img(a, b, k):
    if k <= 0.001:
        return a.copy()
    if k >= 0.999:
        return b.copy()
    return Image.blend(a, b, k)


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 6, "Deserts")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45            # cushion scale; cats on it are 0.62 * 1.45 = 0.9
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
GCX, GCY = K.GLOBE_X, SY - 170
AFRICA_LON = 15


def sill_globe_lon(tl, t):
    T = tl.t
    lon = 20.0 - 4 * t
    for ts, amount in ((T("s_open", 0.15), 260), (T("s_hold", 0.3), 360), (T("s_glow"), 900)):
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    # turn Africa to the front while Luna talks about the Sahara
    t0 = T("s_sahara")
    raw0 = 20.0 - 4 * t0 - 260 * (1 - math.exp(-(t0 - T("s_open", 0.15)) / 0.9))
    target = AFRICA_LON + 360 * round((raw0 - AFRICA_LON) / 360)
    k = ease(tl.prog("s_sahara", t, 0.05, 0.45)) * (1 - ease(tl.prog("s_hold", t, 0.25, 0.9)))
    return lerp(lon, target, k)


def sill(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("day").copy())
    lon = sill_globe_lon(tl, t)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if T("s_bath") <= t < T("s_hold"):
            w_eyes = "happy"
        if T("s_rain") <= t < T("s_rain", 0.6):
            w_eyes = "wide"
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.5))
        lean = -8 * math.exp(-max(0, t - T("s_sahara", 0.1)) * 3) if t > T("s_sahara", 0.1) else 0
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", head_dy=lean, look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_what") or t > T("s_rain", 0.2) else -1,
            proud=tl.talking("pip", t))
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
            x = lerp(CUSH_X, GCX, e)
            y = lerp(SY, GCY + 40, e) - 80 * math.sin(math.pi * e)
            s = CREW_S * lerp(1, 0.15, e ** 1.5)
            K.crew(c, tl, t, x, y, s, 1, fly=min(1, fly * 3), eyes={"whiskers": "wide"},
                   look={"luna": (1, -1), "pip": (1, -1)})

    # the Sahara on the globe
    sx, sy, vis = K.globe_xy(GCX, GCY, 100, 10, 22, lon, 18, -23.5)
    ks = tl.prog("s_sahara", t, 0.5, 0.7) * (1 - tl.prog("s_what", t, 0.7, 1.0))
    if ks > 0.01 and vis:
        c.circle(sx, sy, 14 + 3 * math.sin(t * 6), None, ol=(226, 60, 60), w=4)
        K.label(c, 420, 190, "The Sahara, in Africa", 28, tip=(sx - 14, sy - 8), k=ks)
    # what makes a desert: very little rain
    kr = tl.prog("s_rain", t, 0.25, 0.4) * (1 - tl.prog("s_hold", t, 0.0, 0.25))
    if kr > 0.01:
        k1 = tl.prog("s_rain", t, 0.35, 0.5)
        k2 = tl.prog("s_rain", t, 0.6, 0.75)
        K.inset(c, 948, 182, 460, 250, kr, lambda ic: P.rain_diagram(ic, t, k1, k2))
        K.label(c, 948, 340, "Desert = very little rain", 28, k=tl.prog("s_rainact", t, 0.3, 0.5)
                * (1 - tl.prog("s_hold", t, 0.0, 0.25)), col=(200, 100, 30))
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, GCX, GCY, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
SAHARA = (10, 23)
LANDING = (6, 25)
GO_PATH = [HOME, (-2, 40), (2, 31), LANDING]
CREW_MAP = (170, 660)


def desert_outline(c, v, poly, k, t, col=(255, 236, 90), w=5):
    if k <= 0.01:
        return
    pts = [v.xy(lo, la) for lo, la in K.spline(poly + poly[:3], 8)]
    n = len(pts)
    pts = pts[8:n - 8]                       # closed-ish loop without the doubled ends
    pts.append(pts[0])
    pul = 0.5 + 0.5 * math.sin(t * 5)
    c.line(pts, OUT, (w + 4) * k)
    c.line(pts, mix(col, (255, 255, 255), 0.4 * pul), w * k)


def poly_centre(poly):
    return sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)


def map_(tl, t):
    T = tl.t
    look = {"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)}
    if t < T("m_flat"):
        # ---- up in space
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        gx, gy = lerp(760, 640, k), 360
        raw = 90 - 14 * (t - T("m_fly"))
        lon = lerp(raw, 0, ease(tl.prog("m_narr", t, 0.1, 1.0)))
        K.globe(c, gx, gy, r, lon=lon, lat=lerp(18, 0, ease(tl.prog("m_narr", t, 0.3, 1.0))), glow=0.5)
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        x = lerp(-200, CREW_MAP[0], fk)
        y = lerp(820, CREW_MAP[1], fk)
        K.crew(c, tl, t, x, y, 0.75, 1, fly=1.0, look=look, eyes={"whiskers": "wide"} if t < T("m_narr", 0.5) else None)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_flat", 1):
        # ---- the globe flattens into the map
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        K.crew(c, tl, t, CREW_MAP[0], CREW_MAP[1], 0.75, 1, fly=1.0, look=look)
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def third_pie(ic, t, k):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    K.pie(ic, w / 2, 92, 66, [P.SAND, (120, 190, 92), (120, 190, 92)], k, gap=3)
    if k > 0.4:
        K.text(ic, w / 2 + 28, 66, "Sahara", 20, (150, 90, 30), stroke=2, stroke_fill=(255, 255, 255))
    K.text(ic, w / 2, h - 46, "About 1 of 3", 24, (60, 50, 70))
    K.text(ic, w / 2, h - 20, "parts of Africa", 22, (60, 50, 70))


def map_scene(tl, t):
    T = tl.t
    v0 = (0, 0, 1.0)
    v1 = (14, 27, 2.2)
    v2 = (LANDING[0], LANDING[1], 3.6)
    cam = K.lerp_view(v0, v1, ease(tl.prog("m_zoom", t, 0.05, 0.95)))
    cam = K.lerp_view(cam, v2, ease(tl.prog("m_path", t, 0.35, 1.0)))
    c, v = K.map_view(*cam, t=t)
    lab_k = 1 - tl.prog("m_zoom", t, 0.0, 0.4)
    K.map_labels(c, v, "continents", lab_k)
    # all the deserts of the world light up one by one
    fade = 1 - tl.prog("m_zoom", t, 0.0, 0.5)
    for i, poly in enumerate(K.DESERTS):
        kd = tl.prog("m_yellow", t, 0.38 + 0.09 * i, 0.5 + 0.09 * i) * fade
        if i == 0:
            kd = max(kd, tl.prog("m_zoom", t, 0.5, 0.9) * (1 - tl.prog("m_path", t, 0.6, 0.9)))
        desert_outline(c, v, poly, kd, t)
        if 0 < kd < 1 or (kd > 0 and i > 0):
            cx, cy = v.xy(*poly_centre(poly))
            K.sparkles(c, cx, cy, 40 * v.z ** 0.5, t, 6, kd * fade, seed=10 + i)
    K.label(c, 640, 52, "Yellow = desert", 30, k=tl.prog("m_yellow", t, 0.3, 0.45) * fade, col=(170, 100, 20))
    # the Sahara, the biggest hot desert
    ks = tl.prog("m_zoom", t, 0.6, 0.9) * (1 - tl.prog("m_path", t, 0.0, 0.3))
    K.map_label(c, v, SAHARA[0], SAHARA[1] - 1, "SAHARA", 22 * v.z ** 0.6, (255, 236, 110), ks)
    K.map_label(c, v, 22, 2, "Africa", 18 * v.z ** 0.6, (255, 255, 255), ks)
    kb = tl.prog("m_big", t, 0.45, 0.6) * (1 - tl.prog("m_litter", t, 0.0, 0.2))
    K.label(c, 640, 52, "The biggest hot desert!", 32, k=kb, col=(200, 90, 30))
    # about a third of Africa
    kt = tl.prog("m_third", t, 0.25, 0.5) * (1 - tl.prog("m_litter", t, 0.0, 0.2))
    if kt > 0.01:
        K.map_highlight(c, v, "africa", kt * 0.7, (140, 240, 140), t)
        # repaint the Sahara's sand on top of the green glow so it stays yellow
        sp = [v.xy(lo, la) for lo, la in K.spline(K.DESERTS[0] + K.DESERTS[0][:3], 8)]
        c.poly(sp[8:len(sp) - 8], (236, 206, 128), ol=None)
        desert_outline(c, v, K.DESERTS[0], 1.0, t)
        K.map_label(c, v, SAHARA[0], SAHARA[1] - 1, "SAHARA", 22 * v.z ** 0.6, (255, 236, 110), ks)
        pk = tl.prog("m_third", t, 0.4, 0.9)
        K.inset(c, 1100, 230, 240, 250, kt, lambda ic: third_pie(ic, t, pk))
    # home pin + dotted path + the cushion flying along it
    hx, hy = v.xy(*HOME)
    hk = tl.prog("m_path", t, 0.0, 0.15) * (1 - tl.prog("m_path", t, 0.75, 0.9))
    K.you_are_here(c, hx, hy, t, hk, "Home", side=-1)
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.2, 0.85)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        if t >= T("m_path", 0.2):
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.6, 1, fly=1)
    # the friends on their cushion, hovering in front of the map
    if t < T("m_path", 0.25):
        sk = ease(tl.prog("m_path", t, 0.0, 0.25))
        sx, sy, _ = K.path_point(v, GO_PATH, 0.0)
        x = lerp(CREW_MAP[0], sx, sk)
        y = lerp(CREW_MAP[1], sy + 6, sk)
        s = lerp(0.75, 0.16 * v.z ** 0.6, sk)
        laugh = T("m_laugh") <= t < T("m_laugh", 1)
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
        if T("m_luna") <= t < T("m_laugh"):
            eyes["luna"] = "wide"
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None
        K.crew(c, tl, t, x, y, s, 1, fly=1.0, eyes=eyes, extra=extra,
               look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
        bk = tl.prog("m_litter", t, 0.1, 0.3) * (1 - tl.prog("m_laugh", t, 0.6, 1.0))
        if bk > 0.01:
            K.bubble(c, 330, 420, 110, 70, bk, tail=(150, 560))
            c.push(330, 440, bk)
            P.litter_box(c, 0, 0, 0.9)
            c.pop()
    return c


# ======================================================================= dunes

GROUND = 610
CUSH = (290, 556)
CAMEL_X, CAMEL_Y, CAMEL_S = 905, 655, 0.82
DAY_SUN = (1080, 100)


@lru_cache(None)
def dunes_bg():
    c = Canvas(P.sky_image("day").copy())
    P.sun(c, DAY_SUN[0], DAY_SUN[1], 46, 0.0, sky=(132, 192, 242))
    far, far_d = mix(P.SAND, (255, 255, 255), 0.4), mix(P.SAND_D, (255, 255, 255), 0.4)
    for x0, x1, px, py in ((-200, 520, 180, 400), (260, 980, 640, 386), (720, 1500, 1080, 410)):
        P.dune_shape(c, x0, x1, 480, px, py, far, far_d, ripples=False)
    mid, mid_d = mix(P.SAND, (255, 255, 255), 0.18), mix(P.SAND_D, (255, 255, 255), 0.18)
    P.dune_shape(c, 380, 1500, 640, 960, 470, mid, mid_d, rng_seed=4)
    c.rect(-10, GROUND, W + 10, H + 10, P.SAND, ol=None)
    c.line([(-10, GROUND), (W + 10, GROUND)], mix(P.SAND_D, P.SAND, 0.5), 2)
    rng = np.random.default_rng(8)
    for _ in range(26):
        x, y = rng.uniform(450, W), rng.uniform(GROUND + 10, H)
        c.arc(x, y, rng.uniform(18, 34), 5, 200, 340, P.SAND_D, 2)
    for x, y in ((1180, 650), (560, 690), (1240, 700)):
        for a in (-0.5, -0.2, 0.1, 0.4):
            c.line([(x, y), (x + math.sin(a) * 26, y - 22)], (150, 140, 80), 2.5)
    P.dune_shape(c, -260, 780, 730, CUSH[0] + 10, CUSH[1] - 8, rng_seed=2)
    return c.img


def rider_spots(x, y, s, face, lie=0.0, walk=0.0):
    sp = P.camel_spots(x, y, s, face, lie, walk)
    return {"whiskers": sp["back"], "luna": sp["front"], "pip": sp["top"]}


def draw_riders(c, tl, t, spots, face, who, scale=0.6, eyes=None, extra=None):
    eyes, extra = eyes or {}, extra or {}
    for w_ in ("luna", "whiskers", "pip"):
        if w_ not in who:
            continue
        x, y = spots[w_]
        kw = dict(extra.get(w_, {}))
        if w_ in eyes:
            kw["eyes"] = eyes[w_]
        kat(c, tl, t, w_, x, y, scale * (1.3 if w_ == "pip" else 1.0), face, kw.pop("pose", "sit"), **kw)


def dunes(tl, t):
    T = tl.t
    c = Canvas(dunes_bg().copy())
    P.heat_shimmer(c, 470, t, 700, W)
    # wind and blowing sand
    gk = tl.prog("d_gust", t, 0.0, 0.3) * (1 - tl.prog("d_hello", t, 0.0, 0.3))
    if gk > 0.01:
        P.wind_lines(c, 80, 200, t, gk, 900, 5)
        P.sand_grains(c, CUSH[0] + 30, CUSH[1] - 12, t, gk, 50, 420, 70, seed=3)
        P.sand_grains(c, 960, 470, t, gk, 40, 320, 50, seed=5)
    # Humphrey walks in from the right, later everyone rides off to the left
    ride = tl.prog("d_ride", t, 0.35, 1.0)
    in_k = ease(tl.prog("d_gust", t, 0.2, 1.0))
    cx = lerp(1500, CAMEL_X, in_k) - 1500 * ease(ride) ** 1.3
    walk = (1500 - cx) / (CAMEL_S * 38) if 0 < in_k < 1 or ride > 0 else 0.0
    laugh = T("d_laugh") <= t < T("d_laugh", 1)
    hump_eyes = "happy" if (T("d_fat") <= t < T("d_fat", 0.45)) or laugh else "open"
    if t >= T("d_gust"):
        jig = math.sin(t * 30) * 3 if T("d_fat") <= t < T("d_fat", 0.4) else 0
        P.camel(c, cx + jig, CAMEL_Y, CAMEL_S, -1, t, tl.mouth("humphrey", t), hump_eyes,
                look=(-1, 0) if t < T("d_straw") else (1, -0.6) if t < T("d_hop") else (-1, 0),
                walk=walk, chew=0.0 if tl.talking("humphrey", t) else 1.0)
    spots = rider_spots(cx, CAMEL_Y, CAMEL_S, -1, walk=walk)
    # the cushion lands on the top of the dune
    land = tl.prog("d_land", t, 0.0, 0.5)
    cy = lerp(-140, CUSH[1], ease(land))
    cush_s = 1.1
    top = cy - 40 * cush_s
    seat = {"whiskers": (CUSH[0] - 52 * cush_s, top), "luna": (CUSH[0] + 46 * cush_s, top),
            "pip": (CUSH[0] + 104 * cush_s, top)}
    w_up = tl.prog("d_straw", t, 0.0, 0.32)
    o_up = tl.prog("d_ride", t, 0.0, 0.3)
    eyes = {}
    if T("d_know") <= t < T("d_know", 1):
        eyes["whiskers"] = "happy"
    if T("d_straw", 0.45) <= t < T("d_straw", 0.9):
        eyes["whiskers"] = "closed"
    if T("d_nothing") <= t < T("d_fat", 0.6):
        eyes["whiskers"] = "wide"
    if laugh:
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
    look = {"luna": (1, -0.5), "whiskers": (1, -0.5), "pip": (1, -0.5)}
    lmouth = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else {}
    # cushion (+ whoever is still on it)
    cush_fly = tl.prog("d_ride", t, 0.3, 1.0)
    on_cush = []
    if w_up <= 0:
        on_cush.append("whiskers")
    if o_up <= 0:
        on_cush += ["luna", "pip"]
    if cush_fly <= 0:
        K.crew(c, tl, t, CUSH[0], cy, cush_s, 1, fly=1 - land, who=tuple(on_cush) or ("none",),
               eyes=eyes, look=look, extra=lmouth)
        if land >= 1 and not on_cush:
            pass
    else:
        e = ease(cush_fly)
        K.cushion(c, lerp(CUSH[0], cx + 260, e), lerp(cy, 330, e) + 8 * math.sin(t * 3), lerp(cush_s, 0.6, e), t, 1)
        K.sparkles(c, lerp(CUSH[0], cx + 260, e), lerp(cy, 330, e) - 20, 70, t, 8, 1.0, seed=6)
    # sand puff when the cushion lands
    sk = t - T("d_land", 0.5)
    if 0 < sk < 1.0:
        for k in range(6):
            a = math.pi + k / 5 * math.pi
            rr = 40 + 140 * sk
            c.circle(CUSH[0] + math.cos(a) * rr * 1.2, CUSH[1] - 6 + math.sin(a) * rr * 0.3,
                     14 * (1 - sk) + 2, P.SAND_L, ol=None)
    # Whiskers hops onto the camel's back
    if w_up > 0:
        if w_up < 1:
            x, y = hop(seat["whiskers"], spots["whiskers"], w_up, 150)
            kat(c, tl, t, "whiskers", x, y, lerp(0.68, 0.6, w_up), 1 if w_up < 0.5 else -1,
                "leap" if 0.05 < w_up < 0.95 else "sit", eyes="happy")
        else:
            draw_riders(c, tl, t, spots, -1, ("whiskers",), 0.6, eyes, lmouth)
    if o_up > 0:
        for who, d in (("luna", 0.0), ("pip", 0.15)):
            u = clamp((o_up - d) / 0.85)
            if u < 1:
                x, y = hop(seat[who], spots[who], u, 160)
                kat(c, tl, t, who, x, y, (0.68 if who == "luna" else 0.83) if u < 0.5 else
                    (0.6 if who == "luna" else 0.78), 1 if u < 0.5 else -1,
                    "leap" if who != "pip" and 0.05 < u < 0.95 else "sit")
            else:
                draw_riders(c, tl, t, spots, -1, (who,), 0.6, eyes, lmouth)
    # the straw
    stk = tl.prog("d_straw", t, 0.36, 0.45) * (1 - tl.prog("d_fat", t, 0.3, 0.45))
    if stk > 0.01 and w_up >= 1:
        hx, hy = P.camel_hump(cx, CAMEL_Y, CAMEL_S, -1)
        wx, wy = spots["whiskers"]
        mx, my = wx - 22, wy - 56
        bend = (mx - 26, my - 30)
        end = (hx + 14, hy + 40)
        tip = (lerp(bend[0], end[0], stk), lerp(bend[1], end[1], stk))
        P.straw(c, [(mx, my), bend, tip])
        if T("d_straw", 0.5) <= t < T("d_straw", 0.95):
            for k in range(3):
                u = (t * 2 + k / 3) % 1
                c.circle(mx + 30 + 20 * u, my - 40 - 40 * u, 4 + 4 * u, (255, 255, 255), w=2)
        if T("d_nothing") <= t < T("d_fat"):
            c.push(mx + 10, my - 70, pop(tl.prog("d_nothing", t, 0.0, 0.3)))
            K.text(c, 0, 0, "?", 60, (255, 236, 110), stroke=4)
            c.pop()
    # teaching: dunes, the hump, many days without a drink
    kd = tl.prog("d_dunes", t, 0.15, 0.3) * (1 - tl.prog("d_hello", t, 0.0, 0.2))
    if kd > 0.01:
        dk = tl.prog("d_dunes", t, 0.3, 1.0) * 0.6 + tl.prog("d_windact", t) * 0.4
        K.inset(c, 560, 168, 440, 240, kd, lambda ic: P.dune_diagram(ic, t, dk))
    kh = tl.prog("d_fat", t, 0.5, 0.65) * (1 - tl.prog("d_purpose", t, 0.0, 0.2))
    if kh > 0.01:
        kf = tl.prog("d_fat", t, 0.6, 1.0) * 0.4 + tl.prog("d_hump", t, 0.0, 0.4) * 0.6
        kx = tl.prog("d_hump", t, 0.45, 0.75)
        K.inset(c, 470, 175, 480, 280, kh, lambda ic: P.hump_diagram(ic, t, kf, kx))
        K.label(c, 470, 362, "Many days without a drink!", 26, k=tl.prog("d_store", t, 0.5, 0.7),
                col=(40, 110, 170))
    # 'Hardly ever rains' -- a dry little cloud
    kc = tl.prog("d_drop", t, 0.1, 0.3) * (1 - tl.prog("d_know", t, 0.0, 0.2))
    if kc > 0.01:
        c.push(560, 150, pop(kc))
        P.cloud(c, 0, 0, 1.2)
        K.text(c, 0, 8, "0 drops", 22, (90, 110, 150))
        c.pop()
    K.sub_band(c, tl, t)
    return c


# ======================================================================= oasis

HORIZON = 410
POND = (770, 560, 240, 50)
O_CUSH = (600, 648)
O_CAMEL = (250, 650, 0.8)
FOX_AT = (1040, 652)
O_SUN0, O_SUN1 = (1050, 110), (1010, 470)
TINT = {"day": None, "dusk": ((150, 70, 110), 0.28), "night": ((24, 30, 80), 0.55)}


def oasis_fg(c):
    far, far_d = mix(P.SAND, (255, 255, 255), 0.4), mix(P.SAND_D, (255, 255, 255), 0.4)
    for x0, x1, px, py in ((-200, 600, 220, 380), (380, 1060, 760, 395), (860, 1500, 1160, 372)):
        P.dune_shape(c, x0, x1, HORIZON + 40, px, py, far, far_d, ripples=False)
    c.rect(-10, HORIZON + 30, W + 10, H + 10, P.SAND, ol=None)
    c.line([(-10, HORIZON + 30), (W + 10, HORIZON + 30)], mix(P.SAND_D, P.SAND, 0.5), 2)
    # green ring of grass around the pond
    px, py, rx, ry = POND
    c.ellipse(px, py - 6, rx + 120, ry + 50, (150, 200, 100), ol=None)
    c.ellipse(px, py - 4, rx + 70, ry + 30, (120, 186, 90), ol=None)
    P.palm(c, 470, 520, 0.62, 0, lean=-0.1, seed=2)
    P.palm(c, 640, 500, 0.8, 0, lean=-0.18, seed=3)
    P.palm(c, 960, 500, 0.95, 0, lean=0.14, seed=4)
    P.palm(c, 1120, 540, 0.75, 0, lean=0.2, seed=5)
    c.ellipse(px, py, rx, ry, (80, 170, 230), w=3)
    c.ellipse(px - 30, py - 10, rx * 0.7, ry * 0.45, (120, 196, 245), ol=None)
    for dx in (-140, -40, 80, 170):
        c.arc(px + dx, py + 6, 26, 5, 200, 340, (230, 246, 255), 2.5)
    for x in (560, 610, 900, 1000, 1030, 700):
        for a in (-0.5, -0.2, 0.15, 0.45):
            c.line([(x, py + ry + 2), (x + math.sin(a) * 22, py + ry - 24)], (70, 150, 70), 3)
    rng = np.random.default_rng(3)
    for _ in range(18):
        x, y = rng.uniform(0, W), rng.uniform(640, H)
        c.arc(x, y, rng.uniform(18, 30), 5, 200, 340, P.SAND_D, 2)


@lru_cache(None)
def oasis_layer(which):
    return P.layer(oasis_fg, TINT[which])


def oasis_frame(t, k_dusk, k_night, sun_k, moon_k=0.0):
    """Sky (day -> dusk -> night), sun / moon, then the oasis foreground."""
    if k_night > 0:
        sky = blend_img(P.sky_image("dusk"), P.sky_image("night"), k_night)
    else:
        sky = blend_img(P.sky_image("day"), P.sky_image("dusk"), k_dusk)
    c = Canvas(sky)
    if sun_k < 1:
        x = lerp(O_SUN0[0], O_SUN1[0], ease(sun_k))
        y = lerp(O_SUN0[1], O_SUN1[1], ease(sun_k))
        P.sun(c, x, y, 44, t, col=mix((255, 230, 110), (255, 150, 80), k_dusk), rays=sun_k < 0.3)
    if moon_k > 0:
        D.moon(c, 220, lerp(260, 110, ease(moon_k)), 40, sky=(22, 25, 66))
    if k_night > 0:
        fg = blend_img(oasis_layer("dusk")[0], oasis_layer("night")[0], k_night)
    else:
        fg = blend_img(oasis_layer("day")[0], oasis_layer("dusk")[0], k_dusk)
    c.img.paste(fg, (0, 0), oasis_layer("day")[1])
    return c


def fox_hole(c, x, y, k):
    if k <= 0.01:
        return
    c.ellipse(x - 6, y - 4, 84 * k, 18 * k, (120, 84, 50), ol=None)


def fox_mound(c, x, y):
    c.ellipse(x, y + 18, 110, 30, P.SAND, w=3)
    c.ellipse(x - 20, y + 10, 60, 10, P.SAND_L, ol=None)


def oasis(tl, t):
    T = tl.t
    dusk = tl.prog("o_sunset", t, 0.0, 0.85)
    c = oasis_frame(t, dusk, 0.0, tl.prog("o_sunset", t, 0.0, 1.0))
    if dusk < 0.3:
        P.heat_shimmer(c, HORIZON + 16, t, 0, 420)
    # Humphrey walks in with the friends on his back; the cushion floats behind
    ax, ay, asc = O_CAMEL
    wk = tl.prog("o_open", t, 0.0, 0.85)
    cx = lerp(-380, ax, ease_out(wk))
    walk = (cx + 380) / (asc * 38) if wk < 1 else 0.0
    P.camel(c, cx, ay, asc, 1, t, tl.mouth("humphrey", t), "happy" if T("o_laugh") <= t < T("o_laugh", 1) else "open",
            look=(1, 0), walk=walk, chew=1.0)
    spots = rider_spots(cx, ay, asc, 1, walk=walk)
    down = tl.prog("o_look", t, 0.0, 0.6)
    land = tl.prog("o_narr", t, 0.0, 0.6)
    cush_s = 1.15
    if land < 1:
        e = ease(land)
        kx = lerp(cx - 240, O_CUSH[0], e)
        ky = lerp(400 + 8 * math.sin(t * 3), O_CUSH[1], e)
        K.cushion(c, kx, ky, lerp(0.6, cush_s, e), t, 1 - e)
        K.sparkles(c, kx, ky - 20, 60, t, 7, 1 - e, seed=6)
    laugh = T("o_laugh") <= t < T("o_laugh", 1)
    eyes = {}
    if laugh:
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
    if T("o_huge") <= t < T("o_huge", 1):
        eyes["pip"] = "wide"
    if T("o_q") <= t < T("o_q", 1):
        eyes["luna"] = "wide"
    look = {"luna": (1, -0.5), "whiskers": (1, -0.5), "pip": (1, -0.5)}
    lmouth = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else {}
    top = O_CUSH[1] - 40 * cush_s
    seat = {"whiskers": (O_CUSH[0] - 52 * cush_s, top), "luna": (O_CUSH[0] + 46 * cush_s, top),
            "pip": (O_CUSH[0] + 104 * cush_s, top)}
    if land >= 1:
        if down >= 1:
            K.crew(c, tl, t, O_CUSH[0], O_CUSH[1], cush_s, 1, eyes=eyes, look=look, extra=lmouth)
        else:
            K.cushion(c, O_CUSH[0], O_CUSH[1], cush_s, t)
    if down < 1:
        for who, d in (("whiskers", 0.0), ("luna", 0.1), ("pip", 0.2)):
            u = clamp((down - d) / 0.8)
            if u <= 0:
                draw_riders(c, tl, t, spots, 1, (who,), 0.6, eyes)
            else:
                x, y = hop(spots[who], seat[who], u, 120)
                sc = lerp(0.6, 0.713, u) * (1.3 if who == "pip" else 1.0)
                kat(c, tl, t, who, x, y, sc, 1, "leap" if who != "pip" and 0.05 < u < 0.95 else "sit")
    # Fizz pops out of her burrow
    fx, fy = FOX_AT
    fk = ease_out(tl.prog("o_fizz", t, 0.0, 0.3))
    fox_hole(c, fx, fy, tl.prog("o_look", t, 0.3, 0.8))
    if fk > 0:
        wig = tl.prog("o_cool", t, 0.0, 0.15) * (1 - tl.prog("o_tuna", t, 0.0, 0.3))
        feyes = "happy" if laugh else "open"
        P.fennec(c, fx, fy + 190 * (1 - fk), 0.95, -1, t, tl.mouth("fizz", t), feyes, wiggle=wig)
    fox_mound(c, fx, fy)
    # heat leaving the ears
    kh = tl.prog("o_cool", t, 0.05, 0.25) * (1 - tl.prog("o_cool", t, 0.6, 0.75))
    if kh > 0.01:
        for ex, ey in P.fox_ears(fx, fy, 0.95, -1):
            for i in range(3):
                u = (t * 0.8 + i / 3) % 1
                pts = [(ex + (i - 1) * 16 + 6 * math.sin(j * 1.3 + t * 6), ey - 10 - u * 70 - j * 7) for j in range(6)]
                c.line(pts, mix((240, 80, 50), (255, 200, 120), u), 4 * kh)
        K.label(c, fx - 10, 250, "Heat out!", 28, k=kh, col=(220, 70, 40))
    ke = tl.prog("o_cool", t, 0.55, 0.7) * (1 - tl.prog("o_tuna", t, 0.0, 0.2))
    if ke > 0.01:
        K.inset(c, 700, 170, 380, 220, ke, lambda ic: P.hear_diagram(ic, t, 1.0))
    # Whiskers' tuna thought
    bk = tl.prog("o_tuna", t, 0.15, 0.3) * (1 - tl.prog("o_laugh", t, 0.6, 1.0))
    if bk > 0.01:
        K.bubble(c, 700, 300, 100, 62, bk, tail=(seat["whiskers"][0] + 20, seat["whiskers"][1] - 110))
        c.push(700, 302, bk)
        P.tuna_tin(c, 0, 0, 1.2)
        c.pop()
    # 'An oasis' label
    ko = tl.prog("o_what", t, 0.55, 0.7) * (1 - tl.prog("o_fizz", t, 0.0, 0.2))
    K.label(c, 770, 270, "Oasis: water + palm trees", 30, tip=(770, 520), k=ko, col=(40, 120, 60))
    # 'no clouds like a blanket'
    kb = tl.prog("o_blanket", t, 0.15, 0.3) * (1 - tl.prog("o_sunset", t, 0.5, 0.7))
    if kb > 0.01:
        c.push(640, 150, pop(kb))
        P.cloud(c, 0, 0, 1.4)
        c.line([(-70, -60), (70, 50)], (226, 50, 50), 9)
        c.line([(70, -60), (-70, 50)], (226, 50, 50), 9)
        c.pop()
        K.label(c, 640, 250, "No clouds to keep the warm in", 26, k=kb)
    K.sub_band(c, tl, t)
    return c


# ======================================================================= night

def night(tl, t):
    T = tl.t
    kn = tl.prog("n_open", t, 0.0, 0.7)
    c = oasis_frame(t, 1.0, max(kn, 0.001), 1.0, moon_k=tl.prog("n_open", t, 0.55, 1.0))
    # twinkles (brighter when Pip looks up) and a shooting star
    sk = 0.5 + 0.5 * tl.prog("n_stars", t, 0.0, 0.3)
    rng = np.random.default_rng(21)
    for i in range(30):
        x, y = rng.uniform(0, W), rng.uniform(0, 360)
        k = 0.5 + 0.5 * math.sin(t * rng.uniform(1.5, 4) + i)
        if k > 0.5:
            K.star(c, x, y, (3 + 7 * (k - 0.5)) * sk * kn, (255, 250, 220))
    ss = tl.prog("n_starsact", t, 0.1, 0.6)
    if 0 < ss < 1:
        x0, y0 = 300 + 600 * ss, 60 + 120 * ss
        c.line([(x0 - 120 * min(1, ss * 3), y0 - 24 * min(1, ss * 3)), (x0, y0)], (255, 250, 220), 4)
        K.star(c, x0, y0, 10, (255, 250, 220))
    c.tint = ((30, 36, 90), 0.3 * kn)
    ax, ay, asc = O_CAMEL
    P.camel(c, ax, ay, asc, 1, t, tl.mouth("humphrey", t),
            "happy" if T("n_laugh") <= t < T("n_laugh", 1) else "open", look=(1, -0.5), lie=1.0, chew=0.5)
    laugh = T("n_laugh") <= t < T("n_laugh", 1)
    shiver = T("n_open", 0.5) <= t < T("n_stars")
    jit = math.sin(t * 60) * 3 if shiver else 0
    eyes = {}
    if shiver:
        eyes = {"whiskers": "wide", "luna": "open", "pip": "open"}
    if T("n_stars") <= t < T("n_starsact", 1):
        eyes = {"whiskers": "open", "luna": "wide", "pip": "wide"}
    if T("n_ice") <= t < T("n_ice", 1):
        eyes["luna"] = "wide"
    if laugh:
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
    up = T("n_stars") <= t < T("n_starsact", 1)
    look = {w: (1, -1) if up else (1, -0.5) for w in ("luna", "whiskers", "pip")}
    lmouth = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else {}
    off = tl.prog("n_off", t, 0.15, 1.0)
    e = ease(off)
    cush_s = 1.15
    x = lerp(O_CUSH[0], 760, e) + jit
    y = lerp(O_CUSH[1], -160, e ** 1.2) - 60 * math.sin(math.pi * e)
    K.crew(c, tl, t, x, y, cush_s * lerp(1, 0.4, e), 1, fly=min(1, off * 3), eyes=eyes, look=look, extra=lmouth)
    fx, fy = FOX_AT
    wave = tl.prog("n_off", t, 0.0, 0.2)
    P.fennec(c, fx, fy, 0.95, -1, t, tl.mouth("fizz", t), "happy" if laugh else "open", wave=wave,
             look=(0, -1) if up else (0, 0))
    fox_mound(c, fx, fy)
    c.tint = None
    if shiver:
        for k in range(3):
            K.text(c, x - 70 + k * 6, y - 150 - 4 * k, "~", 30, (200, 230, 255), stroke=2)
    # hot day / cold night
    kt = tl.prog("n_brr", t, 0.5, 0.7) * (1 - tl.prog("n_stars", t, 0.0, 0.2))
    if kt > 0.01:
        k_day = tl.prog("n_brr", t, 0.6, 0.9)
        k_night = tl.prog("n_temp", t, 0.3, 0.8)
        K.inset(c, 640, 170, 560, 260, kt, lambda ic: P.temp_diagram(ic, t, k_day, k_night))
    # Antarctica, the biggest desert of all
    ka = tl.prog("n_ant", t, 0.35, 0.5) * (1 - tl.prog("n_bowl", t, 0.0, 0.2))
    if ka > 0.01:
        k_s = tl.prog("n_antact", t, 0.2, 0.6)
        K.inset(c, 640, 180, 620, 290, ka, lambda ic: P.ant_diagram(ic, t, k_s), bg=(20, 20, 50))
    # the empty water bowl
    bk = tl.prog("n_bowl", t, 0.2, 0.35) * (1 - tl.prog("n_laugh", t, 0.6, 1.0))
    if bk > 0.01:
        K.bubble(c, 640, 330, 100, 62, bk, tail=(O_CUSH[0] - 40, O_CUSH[1] - 150))
        c.push(640, 355, bk)
        P.bowl(c, 0, 0, 1.0, 0.0)
        c.pop()
    K.sub_band(c, tl, t)
    return c


# ==================================================================== remember

FACTS = ["A desert is a place where very little rain falls.",
         "The Sahara, in Africa, is the biggest hot desert.",
         "A camel's hump stores fat, not water."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_rain, P.icon_sahara, P.icon_hump], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "What makes a place a desert? Lots of heat, or very little rain?",
                        ["Lots of heat", "Very little rain"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_heat, P.icon_rain], number=1, answer_text="Very little rain!")
    else:
        c = K.quiz_card(t, "What is inside a camel's hump? Water, or fat?",
                        ["Water", "Fat"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.icon_water_drop, P.icon_fat], number=2, answer_text="Fat! A food store.")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("evening").copy())
    lon = 20.0 - 4 * t
    ts = T("h_pip", 0.3)
    if t > ts:
        lon -= 300 * (1 - math.exp(-(t - ts) / 0.9))
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    e = ease(back)
    x = lerp(GCX, CUSH_X, e)
    y = lerp(GCY + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    sleep = t >= T("h_curl", 0.2)
    shake = T("h_sand", 0.7) <= t < T("h_sand", 1)
    extra = {}
    if sleep:
        extra["whiskers"] = {"pose": "sleep", "dy": 6}
    elif shake:
        extra["whiskers"] = {"squash": 1 + 0.06 * math.sin(t * 40)}
    eyes = {"whiskers": "closed"} if shake else {}
    K.crew(c, tl, t, x + (math.sin(t * 50) * 3 if shake else 0), y, s, 1, fly=1 - back, extra=extra, eyes=eyes,
           look={"luna": (1, -0.5), "pip": (1, -0.5)})
    # a little sand falls out of Whiskers' fur
    st = t - T("h_sand", 0.72)
    if st > 0:
        wx = CUSH_X - 52 * CREW_S
        rng = np.random.default_rng(4)
        for i in range(30):
            d = rng.uniform(0, 0.5)
            u = clamp((st - d) / 0.6)
            if u <= 0:
                continue
            px = wx + rng.uniform(-50, 50) + rng.uniform(-20, 20) * u
            py = lerp(SY - 130 + rng.uniform(0, 80), SY - 6, u * u)
            c.circle(px, py, 2.5, P.SAND_D, ol=None)
        pk = clamp(st / 1.2)
        c.ellipse(wx + 40, SY - 4, 30 * pk, 7 * pk, P.SAND, ol=P.SAND_D, w=1.5)
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Rainforests", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "dunes": dunes, "oasis": oasis, "night": night,
               "remember": remember, "quiz": quiz, "home": home}
