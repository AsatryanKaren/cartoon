"""Scenes of Episode 8 "The Frozen Poles". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py; Pebble, Bjorn, the
Arctic animals, ice and the diagrams come from props.py.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e08_frozen_poles import props as P

CONTINUOUS = ("map",)            # the sill flashes white straight into space
EXTRA_CUTS = ()

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


def window(tl, t, a, b, fade=0.25):
    """1 between events/fractions a=(id, frac) and b=(id, frac), fading in and out."""
    return tl.prog(a[0], t, a[1], a[1] + fade) * (1 - tl.prog(b[0], t, b[1], b[1] + fade))


def between(tl, t, a, b):
    return tl.t(*a) <= t < tl.t(*b)


def breath(c, x, y, t, k=1.0, face=1):
    """Little frosty breath puffs."""
    if k <= 0.01:
        return
    u = (t * 1.2) % 1
    c.circle(x + face * 22 * u, y - 10 * u, (5 + 10 * u) * k, mix((255, 255, 255), (220, 236, 255), u), ol=None)


def question(c, x, y, k, t, col=(255, 236, 110)):
    if k <= 0.01:
        return
    c.push(x, y + 4 * math.sin(t * 5), pop(k))
    K.text(c, 0, 0, "?", 70, col, stroke=4)
    c.pop()


def peb_on_cushion(c, tl, t, x, y, s, face=1, fly=0.0, hot=0.0, eyes="open", mouth=None):
    """Pebble standing on the left end of the flying cushion (call after K.crew)."""
    bob = math.sin(t * 2.6) * 6 * fly
    m = tl.mouth("pebble", t) if mouth is None else mouth
    P.pebble(c, x - face * 124 * s, y + bob - 40 * s, 0.6 * s, face, t, m, eyes,
             flap=0.6 if tl.talking("pebble", t) else 0.0, hot=hot, seed=4.0)


def globe_here(ic, t, north=True, text="The bottom of the world"):
    """Inset: a globe tipped so we see the pole, with a red pin on it."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    lat0 = 35 if north else -35
    lon0 = -t * 15 + (10 if north else 20)
    cx, cy, r = w / 2, h / 2 - 8, min(w, h) * 0.34
    K.globe(ic, cx, cy, r, lon=lon0, lat=lat0)
    if north:
        P.ice_cap(ic, cx, cy, r, lon0, lat0, True, 78)
    px, py, _ = K.globe_xy(cx, cy, r, 0, 90 if north else -90, lon0, lat0)
    P.pole_pin(ic, px, py, 1.0, (226, 56, 60))
    K.text(ic, w / 2, h - 20, text, 22, (255, 255, 255), stroke=3)


def envelope_fly(c, a, b, u, s=1.0, col=(255, 250, 236)):
    if u <= 0:
        return
    x, y = hop(a, b, u, 120)
    P.envelope(c, x, y, s * (1 + 0.2 * math.sin(math.pi * clamp(u))), col=col)


# ======================================================================= title

def title(tl, t):
    c = K.title_card(tl, t, 0.0, 8, "The Frozen Poles")
    P.snowfall(c, t, n=40, k=clamp(t / 2.0), speed=50, seed=8)
    return c


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45            # cushion scale; cats on it are 0.62 * 1.45 = 0.9
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
OG_R = 100               # old globe radius


def sill_globe_lon(tl, t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def sill(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("day").copy())
    P.snowfall(c, t, box=(232, 46, 1050, 480), n=50, seed=3, speed=36, size=(2, 4))
    spins = [(T("s_open", 0.15), 260), (T("s_narr", 0.2), 200), (T("s_go", 0.6), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(tl, t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    # the white "whipped cream" ice at both ends of Luna's globe
    P.ice_cap(c, gcx, gcy, OG_R, lon, 18, True, 72, roll=-23.5)
    P.ice_cap(c, gcx, gcy, OG_R, lon, 18, False, 66, roll=-23.5)
    npx, npy, _ = K.globe_xy(gcx, gcy, OG_R, 0, 90, lon, 18, -23.5)
    spx, spy, _ = K.globe_xy(gcx, gcy, OG_R, 0, -90, lon, 18, -23.5)

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if between(tl, t, ("s_cream", 0.0), ("s_cream", 1.0)):
            w_eyes = "happy" if t > T("s_cream", 0.6) else "wide"
        if between(tl, t, ("s_pole", 0.3), ("s_scratch", 1.0)):
            w_eyes = "happy"
        look = (1, -0.6)
        if t < T("s_cream"):
            look = (1, -0.3)
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes, look=look)
        lean = -8 * math.exp(-max(0, t - T("s_narr", 0.2)) * 3) if t > T("s_narr", 0.2) else 0
        l_eyes = "closed" if between(tl, t, ("s_scratch", 0.2), ("s_scratch", 0.8)) else "open"
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", head_dy=lean, look=(-1, -0.4), eyes=l_eyes)
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_go") else -1, proud=tl.talking("pip", t))
        # cold breath: it's a chilly morning
        breath(c, CUSH_X - 52 * CREW_S + 40, SY - 40 * CREW_S - 92, t, 0.6)
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

    # --- teaching moments
    kc = window(tl, t, ("s_cream", 0.25), ("s_north", 0.1))
    K.label(c, 880, 110, "Whipped cream?", 28, tip=(npx + 10, npy - 4), k=kc, bg=(255, 244, 214))
    kn = window(tl, t, ("s_north", 0.35), ("s_pole", 0.1))
    if kn > 0.01:
        K.label(c, 880, 110, "North Pole", 32, tip=(npx + 10, npy - 4), k=kn, col=(200, 40, 50))
        K.label(c, 800, 190, "= the very top", 24, k=kn * tl.prog("s_north", t, 0.6, 0.8), bg=(255, 244, 190))
        K.label(c, 460, 120, "Ice!", 30, tip=(npx - 30, npy + 14), k=kn * tl.prog("s_north", t, 0.15, 0.3),
                col=(40, 110, 190), bg=(225, 242, 255))
    ks = window(tl, t, ("s_south", 0.25), ("s_pole", 0.1))
    if ks > 0.01:
        K.label(c, 860, 440, "South Pole", 32, tip=(spx + 10, spy + 4), k=ks, col=(40, 60, 140))
    # Whiskers' daydream: a giant stripy pole sticking out of the world
    kd = window(tl, t, ("s_pole", 0.2), ("s_go", 0.2))
    if kd > 0.01:
        bx, by = 300, 205
        K.bubble(c, bx, by, 140, 118, kd, tail=(CUSH_X - 60, SY - 150))
        scratch = 1.0 if between(tl, t, ("s_scratch", 0.0), ("s_scratch", 1.0)) else 0.0
        P.dream(c, bx + 6, by - 10, 1.05 * kd, t, scratch)
    K.sub_band(c, tl, t)
    # push in to the glowing globe and flash white into space
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
ANT = (24, -75)
GO_PATH = [HOME, (8, 22), (14, -18), (20, -48), ANT]
GX, GY, GR = 640, 330, 200


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40 - 26 * max(0.0, t - tl.t("m_spin")) * 0.7
    end = -14 * (tl.t("m_flat") - t0) + 40 - 26 * (tl.t("m_flat") - tl.t("m_spin")) * 0.7
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_nopole", t, 0.0, 1.0)))


def map_crew(c, tl, t, x, y, s, **kw):
    K.crew(c, tl, t, x, y, s, 1, fly=1.0, **kw)


def map_seaice(c, v, k=1.0, edge=79.0):
    """Floating white sea ice over the Arctic Ocean at the top of the map."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(11)
    wob = rng.uniform(-2.0, 2.0, 37)
    e = 90 - (90 - edge) * ease(k)
    pts = [v.xy(lo, e + wob[i] * ease(k)) for i, lo in enumerate(range(-180, 181, 10))]
    x0, y0 = v.xy(180, 90)
    x1, _ = v.xy(-180, 90)
    c.poly(pts + [(x0, y0), (x1, y0)], (244, 249, 255), ol=None)
    c.line(pts, (190, 216, 240), 2)


def spin_axis(c, x, y, r, t, k):
    """Dashed axis through the poles and a curly 'spinning' arrow round the middle."""
    if k <= 0.01:
        return
    col = (255, 236, 110)
    top, bot = y - r - 50, y + r + 50
    n = 12
    for i in range(n):
        a = lerp(top, bot, i / n)
        b = lerp(top, bot, (i + 0.5) / n)
        c.line([(x, lerp(y, a, k)), (x, lerp(y, b, k))], col, 4)
    # arrow round the middle (front half)
    pts = [(x + math.cos(u) * (r + 26), y + math.sin(u) * 26) for u in np.linspace(0.2, math.pi - 0.4, 24)]
    c.line(pts, col, 6)
    tip = pts[-1]
    c.poly([(tip[0] - 18, tip[1] - 12), (tip[0] + 6, tip[1] - 2), (tip[0] - 12, tip[1] + 14)], col, w=2)


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        # ---- up in space: the poles are the very top and bottom of the Earth
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, GR, k)
        lat = lerp(18, 0, ease(tl.prog("m_np", t, 0.0, 0.3)))
        gx, gy = lerp(760, GX, k), lerp(300, GY, k)
        lon = space_globe_lon(tl, t)
        K.globe(c, gx, gy, r, lon=lon, lat=lat, glow=0.5)
        P.ice_cap(c, gx, gy, r, lon, lat, True, 79)
        npx, npy, _ = K.globe_xy(gx, gy, r, 0, 90, lon, lat)
        spx, spy, _ = K.globe_xy(gx, gy, r, 0, -90, lon, lat)
        ka = tl.prog("m_spin", t, 0.0, 0.3) * (1 - tl.prog("m_nopole", t, 0.6, 1.0))
        spin_axis(c, gx, gy, r, t, ka)
        kn = tl.prog("m_np", t, 0.05, 0.2)
        P.pole_pin(c, npx, npy, kn)
        K.label(c, 930, 92, "North Pole: the very top", 28, tip=(npx + 14, npy - 20), k=kn, col=(200, 40, 50))
        ksp = tl.prog("m_np", t, 0.5, 0.65)
        if ksp > 0.01:
            c.push(spx, spy, pop(ksp))
            c.line([(0, 0), (0, 34)], OUT, 3)
            c.poly([(0, 34), (22, 28), (0, 20)], (70, 130, 230), w=2)
            c.circle(0, 0, 4, (70, 130, 230), w=2)
            c.pop()
        K.label(c, 930, 548, "South Pole: the very bottom", 28, tip=(spx + 14, spy + 20), k=ksp, col=(40, 60, 140))
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        x = lerp(-200, 200, fk)
        y = lerp(820, 640, fk)
        eyes = {"whiskers": "wide"} if t < T("m_narr", 0.6) else {}
        look = {"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)}
        if T("m_nopole") <= t:
            look["whiskers"] = (1, -1) if (t * 1.3) % 2 < 1 else (1, 1)
        map_crew(c, tl, t, x, y, 0.75, look=look, eyes=eyes)
        question(c, x - 40, y - 150, window(tl, t, ("m_nopole", 0.2), ("m_flat", 0.0)), t)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_mapnp"):
        # ---- the globe flattens into the map
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        if k >= 1:
            v = K.MapView(0, 0, 1)
            map_seaice(c, v, tl.prog("m_flat", t, 0.85, 1.0))
            K.map_labels(c, v, "continents", tl.prog("m_flat", t, 0.85, 1.0))
        K.label(c, 640, 46, "A map = the globe, flattened out", 28, k=tl.prog("m_flat", t, 0.3, 0.45)
                * (1 - tl.prog("m_flat", t, 0.92, 1.0)))
        map_crew(c, tl, t, 170, 660, 0.75, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    pk = tl.prog("m_path", t, 0.3, 1.0)
    cam = K.lerp_view((0, 0, 1.0), (ANT[0] - 4, -64, 2.4), ease(pk))
    c, v = K.map_view(*cam, t=t)
    map_seaice(c, v)
    lab_k = 1 - tl.prog("m_path", t, 0.0, 0.3)
    K.map_labels(c, v, ["North America", "South America", "Europe", "Africa", "Asia", "Australia"], lab_k)
    K.map_highlight(c, v, "antarctica", tl.prog("m_south", t, 0.2, 0.5), col=(140, 220, 255), t=t)
    K.map_label(c, v, *K.CONTINENT_LABELS["Antarctica"], "Antarctica", 22 * min(1.8, v.z ** 0.5), (40, 80, 150),
                k=tl.prog("m_south", t, 0.2, 0.5), stroke_col=(255, 255, 255))
    K.map_label(c, v, -10, 82.5, "Arctic Ocean", 22 * min(1.8, v.z ** 0.5), (40, 80, 150),
                k=tl.prog("m_mapnp", t, 0.2, 0.4) * lab_k, stroke_col=(255, 255, 255))
    # North at the top, South at the bottom
    x0, y0, x1, y1 = v.rect()
    kn = tl.prog("m_mapnp", t, 0.05, 0.2) * (1 - tl.prog("m_path", t, 0.0, 0.2))
    if kn > 0.01:
        K.arrow(c, 1190, 200, 1190, y0 + 6, (255, 236, 90), 9, kn)
        K.label(c, 1170, 236, "North Pole", 28, k=kn, col=(200, 40, 50))
    ks = tl.prog("m_mapnp", t, 0.5, 0.65) * (1 - tl.prog("m_path", t, 0.0, 0.2))
    if ks > 0.01:
        K.arrow(c, 1190, 560, 1190, y1 - 6, (255, 236, 90), 9, ks)
        K.label(c, 1170, 525, "South Pole", 28, k=ks, col=(40, 60, 140))
    hx, hy = v.xy(*HOME)
    K.you_are_here(c, hx, hy, t, tl.prog("m_mapnp", t, 0.0, 0.2) * (1 - tl.prog("m_path", t, 0.5, 0.7)),
                   "Home" if t < T("m_path") else "", side=-1)
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.12, 0.85)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        if t >= T("m_path", 0.1):
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, 1, fly=1)
        ax, ay = v.xy(*ANT)
        K.label(c, ax + 60, ay - 130, "Antarctica", 32, tip=(ax, ay - 24), k=tl.prog("m_path", t, 0.8, 0.95))
    if t < T("m_path", 0.12):
        sk = ease(tl.prog("m_path", t, 0.0, 0.12))
        x = lerp(170, hx, sk)
        y = lerp(660, hy + 6, sk)
        s = lerp(0.75, 0.16, sk)
        map_crew(c, tl, t, x, y, s, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    K.map_clip(c, v)
    K.flash(c, tl.prog("m_path", t, 0.88, 1.0) * 0.8)
    return c


# ======================================================================= south

S_HOR = 360
S_GROUND = 430
LAND = (330, 610)        # cushion on the ice
PEB = (930, 612)
CREW_P = 1.1


def south_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (126, 186, 238)), (S_HOR / H, (226, 236, 250)),
                                               (S_HOR / H + 0.001, (60, 110, 170)), (1, (60, 110, 170))]))
        c.glow(1040, 120, 200, 140, (255, 250, 220), (180, 214, 244), steps=10)
        c.circle(1040, 120, 34, (255, 244, 190), ol=None)
        D.cloud(c, 260, 100, 0.7)
        D.cloud(c, 700, 70, 0.5)
        # far ice mountains
        P.berg(c, 520, S_HOR + 16, 200, 120, seed=3)
        P.berg(c, 840, S_HOR + 16, 160, 90, seed=5)
        P.berg(c, 1160, S_HOR + 16, 210, 140, seed=7)
        # the sea on the left, with a floating iceberg
        c.rect(-10, S_HOR, 380, S_GROUND + 20, (60, 120, 190), ol=None)
        for i in range(6):
            c.arc(40 + i * 56, S_HOR + 30 + (i % 2) * 18, 16, 5, 200, 340, (130, 180, 230), 2)
        P.berg(c, 120, S_HOR + 26, 60, 64, seed=9)
        # the thick ice sheet (land under it!)
        pts = [(330, S_HOR + 6), (460, S_HOR + 2), (W + 10, S_HOR + 2), (W + 10, H + 10), (-10, H + 10),
               (-10, S_GROUND + 30), (120, S_GROUND + 8), (260, S_GROUND - 20)]
        c.poly(pts, (240, 246, 252), w=3)
        c.poly([(-10, S_GROUND + 30), (120, S_GROUND + 8), (260, S_GROUND - 20), (330, S_HOR + 6),
                (330, S_HOR + 30), (240, S_GROUND + 6), (100, S_GROUND + 34), (-10, S_GROUND + 56)],
               P.ICE_SH, ol=None)
        rng = np.random.default_rng(4)
        for _ in range(16):
            x, y = rng.uniform(380, 1260), rng.uniform(S_GROUND - 40, H - 10)
            c.ellipse(x, y, rng.uniform(30, 90), rng.uniform(3, 7), P.ICE_SH, ol=None)
        # a far penguin colony
        for i in range(9):
            x = 640 + i * 52 + rng.uniform(-12, 12)
            y = S_HOR + 30 + rng.uniform(-4, 10)
            P.pebble(c, x, y, 0.16 + 0.03 * rng.random(), -1 if i % 3 else 1, 0.0, eyes="open", seed=50 + i)
        return c.img
    return cached("south", make)


def south(tl, t):
    T = tl.t
    c = Canvas(south_bg().copy())
    P.snowfall(c, t, n=40, seed=5, speed=36, size=(1.5, 3.2))
    # a few colony penguins waddle while Pebble talks about them
    kp = window(tl, t, ("so_live", 0.0), ("so_hop", 0.0))
    if kp > 0.01:
        for i in range(4):
            x = 470 + i * 58 + 10 * math.sin(t * 1.5 + i)
            P.pebble(c, x, S_HOR + 64, 0.26, 1 if i % 2 else -1, t, waddle=t * 8 + i, flap=0.3, seed=60 + i)
        K.label(c, 590, S_HOR - 26, "Penguins live in the south!", 26, k=kp, col=(40, 60, 140))

    # Pebble toboggans in on her belly, then stands up
    sk = tl.prog("so_slide", t, 0.0, 0.7)
    on_cush = tl.prog("so_off", t, 0.05, 0.4)
    p_eyes = "happy" if tl.talking("pebble", t) and t < T("so_hello", 0.8) else "open"
    if between(tl, t, ("so_hop", 0.0), ("so_off", 0.0)):
        p_eyes = "wide"
    if t >= T("so_slide") and on_cush <= 0:
        px = lerp(1420, PEB[0], ease_out(sk))
        sliding = sk < 1
        P.pebble(c, px, PEB[1], 1.3, -1, t, tl.mouth("pebble", t), p_eyes,
                 flap=0.7 if tl.talking("pebble", t) else 0.0, slide=1.0 if sliding else 0.0, seed=4.0,
                 look=(-1, 0))
        if sliding:
            for k in range(3):
                c.ellipse(px + 80 + 40 * k, PEB[1] - 4, 20 - 5 * k, 4, P.ICE_SH, ol=None)

    # the friends on the cushion: land on the ice, take off at the end with Pebble
    land = ease(tl.prog("so_land", t, 0.0, 0.7))
    go = ease(tl.prog("so_off", t, 0.45, 1.0))
    x = lerp(-160, LAND[0], land) + 1000 * go
    y = lerp(220, LAND[1], land) - 640 * go - 80 * math.sin(math.pi * go)
    s = CREW_P * (1 - 0.4 * go)
    shiver = math.sin(t * 60) * 2.0 * (1 - go) * land
    eyes, look = {}, {"luna": (1, -0.2), "whiskers": (1, -0.2), "pip": (1, -0.2)}
    if T("so_narr") <= t < T("so_slide", 0.8):
        eyes = {"pip": "wide", "whiskers": "wide"}
    if between(tl, t, ("so_hop", 0.0), ("so_off", 0.5)):
        eyes = {"whiskers": "happy"}
    fly = max(1 - land, tl.prog("so_off", t, 0.3, 0.6))
    K.crew(c, tl, t, x + shiver, y, s, 1, fly=fly, eyes=eyes, look=look)
    if on_cush > 0:
        if on_cush < 1:
            hx, hy = hop((PEB[0], PEB[1]), (x - 124 * s, y - 40 * s), on_cush, 160)
            P.pebble(c, hx, hy, lerp(1.3, 0.6 * s, on_cush), -1 if on_cush < 0.5 else 1, t, flap=1.0, seed=4.0)
        else:
            peb_on_cushion(c, tl, t, x, y, s, 1, fly, eyes="happy")
    if 0.01 < land and go < 0.05:
        breath(c, x - 52 * s + 44, y - 40 * s - 70, t, 0.8)
        breath(c, x + 46 * s + 44, y - 40 * s - 70, t + 0.4, 0.6)
    # the message: from Pebble to Whiskers
    mk = tl.prog("so_msg", t, 0.5, 0.9)
    wx, wy = x - 52 * s + 30, y - 40 * s - 40
    if mk > 0 and go <= 0:
        if mk < 1:
            envelope_fly(c, (PEB[0] - 40, PEB[1] - 110), (wx, wy), mk)
        else:
            P.envelope(c, wx, wy, 0.9)
    elif go > 0:
        P.envelope(c, wx, wy, 0.9 * s / CREW_P)

    # --- teaching moments
    kn = window(tl, t, ("so_narr", 0.1), ("so_hello", 0.4))
    if kn > 0.01:
        K.inset(c, 1060, 170, 300, 240, kn, lambda ic: globe_here(ic, t, False, "Bottom of the world"))
        K.label(c, 600, 80, "Antarctica", 44, k=kn, col=(40, 60, 140))
    kc = window(tl, t, ("so_land1", 0.1), ("so_live", 0.0))
    if kc > 0.01:
        kl = tl.prog("so_land1", t, 0.3, 0.5)
        K.inset(c, 640, 210, 440, 280, kc, lambda ic: P.cut_antarctica(ic, t, kl))
        K.label(c, 640, 380, "Antarctica = a continent of ice", 26, k=tl.prog("so_cut", t, 0.1, 0.3) * kc,
                bg=(255, 244, 190))
    kb = window(tl, t, ("so_live", 0.5), ("so_hop", 0.0))
    if kb > 0.01:
        K.bubble(c, 1080, 300, 86, 70, kb, tail=(PEB[0] + 40, PEB[1] - 160))
        P.bear_icon(c, 1068, 304, 40 * kb, t)
        question(c, 1132, 270, kb, t, (226, 70, 80))
    kq = window(tl, t, ("so_float", 0.3), ("so_land1", 0.1))
    question(c, LAND[0] + 114 * CREW_P, LAND[1] - 170, kq, t)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== trip

EQ = (14, -2)
TRIP1 = [ANT, (22, -45), (18, -18), EQ]
BACK = [EQ, (28, -30), (32, -73)]
NORTH = [(32, -73), (8, -40), (-22, -4), (-34, 34), (-28, 66), (-6, 86)]
NP = (-6, 86)


def trip(tl, t):
    T = tl.t
    # where the little icon is: north to the hot middle, back south, then all the way north
    u1 = K.smooth(t, [(T("tr_fly", 0.2), 0.0), (T("tr_warm", 0.9), 1.0)], 0.4)
    u2 = K.smooth(t, [(T("tr_back", 0.3), 0.0), (T("tr_path", 0.3), 1.0)], 0.3)
    u3 = K.smooth(t, [(T("tr_path", 0.3), 0.0), (T("tr_path", 0.9), 1.0)], 0.3)
    a = (ANT[0] - 4, -64, 2.4)
    mid = (EQ[0], -20, 1.7)
    world = (0, 0, 1.0)
    b = (NP[0] + 4, 70, 2.2)
    k1 = ease(tl.prog("tr_fly", t, 0.0, 1.0) * 0.3 + tl.prog("tr_warm", t, 0.0, 1.0) * 0.7)
    k2 = ease(tl.prog("tr_back", t, 0.2, 1.0))
    k3 = ease(tl.prog("tr_path", t, 0.4, 0.95))
    if k3 > 0:
        cam = K.lerp_view(world, b, k3)
    elif k2 > 0:
        cam = K.lerp_view(mid, world, k2)
    else:
        cam = K.lerp_view(a, mid, k1)
    c, v = K.map_view(*cam, t=t)
    map_seaice(c, v)
    K.map_labels(c, v, ["Africa", "South America", "Europe", "Atlantic Ocean", "Antarctica"], 1 - k3 * 0.7)
    # the hot middle of the Earth
    ke = tl.prog("tr_warm", t, 0.1, 0.4) * (1 - tl.prog("tr_back", t, 0.6, 0.9))
    if ke > 0.01:
        xa, ya = v.xy(-180, 0)
        xb, _ = v.xy(180, 0)
        n = 60
        for i in range(n):
            if i % 2 == 0:
                c.line([(lerp(xa, xb, i / n), ya), (lerp(xa, xb, (i + 1) / n), ya)],
                       (255, 120, 60), 5 * ke, cap=False)
        ex, ey = v.xy(EQ[0] - 30, 0)
        K.label(c, ex, ey - 60, "The hot middle", 28, k=ke, col=(200, 70, 30), bg=(255, 240, 200))
    # sun beating down
    ksun = window(tl, t, ("tr_warm", 0.0), ("tr_back", 0.3))
    if ksun > 0.01:
        c.push(1150, 110, pop(ksun))
        for i in range(12):
            ang = i * math.pi / 6 + t * 0.6
            c.line([(math.cos(ang) * 62, math.sin(ang) * 62), (math.cos(ang) * 88, math.sin(ang) * 88)],
                   (255, 200, 60), 6)
        c.circle(0, 0, 50, (255, 216, 80), w=3)
        c.pop()
    # paths
    K.map_path(c, v, TRIP1, max(u1, 0.0001), head=u1 > 0.02 and u2 <= 0)
    if u2 > 0:
        K.map_path(c, v, BACK, u2, head=u3 <= 0, col=(180, 230, 255))
    if u3 > 0:
        K.map_path(c, v, NORTH, u3, head=True)
    hot = tl.prog("tr_warm", t, 0.2, 1.0) * (1 - tl.prog("tr_laugh", t, 0.0, 1.0) * 0.5) \
        * (1 - tl.prog("tr_back", t, 0.3, 1.0))
    peb_home = u2 >= 1
    if u3 > 0:
        x, y, ang = K.path_point(v, NORTH, u3)
    elif u2 > 0:
        x, y, ang = K.path_point(v, BACK, u2)
    else:
        x, y, ang = K.path_point(v, TRIP1, u1)
    s = 0.16 * v.z ** 0.8
    face = -1 if math.cos(ang) < -0.3 else 1
    K.crew(c, tl, t, x, y + 6, s, face, fly=1)
    if not peb_home:
        peb_on_cushion(c, tl, t, x, y + 6, s, face, 1.0, hot, mouth=0.0)
    else:
        px, py = v.xy(32, -73)
        P.pebble(c, px, py + 4, 0.18 * v.z ** 0.8, 1, t, flap=1.0, eyes="happy", seed=4.0)
    K.map_clip(c, v)

    # close-up of the friends with poor hot Pebble
    kz = window(tl, t, ("tr_warm", 0.05), ("tr_back", 0.0), 0.12)
    if kz > 0.01:
        bx = lerp(-260, 250, ease_out(kz))
        by = 650
        laugh = between(tl, t, ("tr_laugh", 0.0), ("tr_laugh", 1.0))
        eyes = {}
        if t < T("tr_stop"):
            eyes = {"luna": "wide", "pip": "wide"}
        if between(tl, t, ("tr_purpose", 0.0), ("tr_not", 0.0)):
            eyes = {"whiskers": "happy"}
        if laugh:
            eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None
        K.crew(c, tl, t, bx, by, 0.85, 1, fly=1.0, eyes=eyes, extra=extra,
               look={"luna": (-1, 0), "pip": (-1, 0), "whiskers": (-1, 0)})
        p_eyes = "wide" if between(tl, t, ("tr_not", 0.0), ("tr_laugh", 0.3)) else "open"
        peb_on_cushion(c, tl, t, bx, by, 0.85, 1, 1.0, hot, eyes=p_eyes)
        lvl = 0.12 + 0.85 * tl.prog("tr_warm", t, 0.0, 1.0) * (1 - 0.4 * tl.prog("tr_laugh", t))
        P.thermometer(c, bx + 210, 470 + 3 * math.sin(t * 2.6), 0.9 * pop(kz), lvl, t)
        kss = window(tl, t, ("tr_purpose", 0.4), ("tr_laugh", 0.6))
        K.label(c, bx + 60, 330, "Penguin sauna?!", 28, k=kss, col=(200, 70, 30), bg=(255, 240, 200))
    kd = window(tl, t, ("tr_stop", 0.25), ("tr_purpose", 0.15))
    if kd > 0.01:
        cross = tl.prog("tr_never", t, 0.2, 0.6)
        K.inset(c, 880, 270, 440, 360, kd, lambda ic: P.never_diagram(ic, t, 1.0, cross), bg=(20, 20, 50))
    kh = tl.prog("tr_back", t, 0.0, 0.3) * (1 - tl.prog("tr_path", t, 0.25, 0.4))
    if kh > 0.01:
        px, py = v.xy(32, -73)
        K.label(c, px + 120, py - 70, "Home, Pebble!", 26, tip=(px + 8, py - 20), k=kh)
    if u3 > 0.8:
        nx, ny = v.xy(*NP)
        K.you_are_here(c, nx, ny + 30, t, tl.prog("tr_path", t, 0.75, 0.85), "The Arctic", side=1)
    K.flash(c, tl.prog("tr_path", t, 0.9, 1.0) * 0.8)
    K.sub_band(c, tl, t)
    return c


# ======================================================================= north

N_HOR = 330
FLOE_Y = 560
N_LAND = (330, 606)
BJ = (1080, 616)
FOX = (560, 452)


def _north_layers(night=False):
    sky = [(0, (110, 176, 236)), (N_HOR / H, (214, 234, 252))] if not night else \
        [(0, (8, 12, 40)), (N_HOR / H, (30, 40, 92))]
    sea0, sea1 = ((44, 100, 170), (28, 70, 140)) if not night else ((20, 36, 80), (12, 22, 56))
    c = Canvas(D.gradient(W * SS, H * SS, sky + [(N_HOR / H + 0.001, sea0), (1, sea1)]))
    tint = None if not night else ((16, 22, 66), 0.45)
    if night:
        D.stars(c, 6, 120, W, N_HOR - 20)
        D.moon(c, 1120, 80, 26, sky=(10, 14, 44))
    else:
        c.glow(200, 250, 160, 90, (255, 246, 210), (190, 220, 248), steps=8)
        c.circle(200, 262, 30, (255, 236, 160), ol=None)    # low sun, near the horizon
        D.cloud(c, 620, 90, 0.6)
        D.cloud(c, 960, 140, 0.45)
    c.tint = tint
    P.berg(c, 360, N_HOR + 8, 120, 70, seed=21)
    P.berg(c, 900, N_HOR + 8, 90, 50, seed=22)
    for i in range(7):
        c.arc(80 + i * 180, N_HOR + 40 + (i % 3) * 24, 22, 5, 200, 340, mix(sea0, (255, 255, 255), 0.3), 2)
    # far and middle floes
    P.floe(c, 140, 420, 120, 18, seed=1)
    P.floe(c, 800, 410, 150, 20, seed=2)
    P.floe(c, 560, 470, 110, 18, seed=3)
    # the big floe in front
    pts = [(-10, FLOE_Y + 6), (200, FLOE_Y - 6), (520, FLOE_Y + 4), (760, FLOE_Y - 8), (1000, FLOE_Y - 2),
           (W + 10, FLOE_Y - 12), (W + 10, H + 10), (-10, H + 10)]
    c.poly(pts, P.ICE, w=3)
    c.poly([(-10, H - 40), (400, H - 52), (900, H - 44), (W + 10, H - 56), (W + 10, H + 10), (-10, H + 10)],
           P.ICE_SH, ol=None)
    rng = np.random.default_rng(9)
    for _ in range(10):
        x, y = rng.uniform(0, W), rng.uniform(FLOE_Y + 20, H - 60)
        c.ellipse(x, y, rng.uniform(30, 80), rng.uniform(3, 6), P.ICE_SH, ol=None)
    c.tint = None
    return c.img


def north_bg(night=0.0):
    day = cached("north_day", lambda: _north_layers(False))
    if night <= 0.001:
        return day
    nite = cached("north_night", lambda: _north_layers(True))
    if night >= 0.999:
        return nite
    return Image.blend(day, nite, night)


def aurora(c, t, k):
    """Northern lights: soft green and pink curtains rippling across the night sky."""
    if k <= 0.01:
        return
    sw, sh = W // 4, N_HOR // 4 + 10
    m = Image.new("L", (sw, sh), 0)
    m2 = Image.new("L", (sw, sh), 0)
    d, d2 = ImageDraw.Draw(m), ImageDraw.Draw(m2)
    for band, (y0, amp, ph, hgt) in enumerate(((22, 7, 0.0, 26), (40, 9, 1.7, 22), (14, 5, 3.1, 16))):
        for x in range(0, sw, 2):
            yy = y0 + amp * math.sin(x / 26 + t * 0.8 + ph) + 3 * math.sin(x / 9 - t * 1.6 + ph)
            inten = 0.6 + 0.4 * math.sin(x / 15 + t * 1.3 + band)
            v = int(200 * inten * k)
            d.line([(x, yy - hgt), (x, yy)], fill=v, width=2)
            if band == 1:
                d2.line([(x, yy - hgt - 10), (x, yy - hgt + 4)], fill=int(v * 0.6), width=2)
    m = m.filter(ImageFilter.GaussianBlur(2.5)).resize((W * SS, sh * 4 * SS), Image.BILINEAR)
    m2 = m2.filter(ImageFilter.GaussianBlur(2.5)).resize((W * SS, sh * 4 * SS), Image.BILINEAR)
    c.img.paste((120, 255, 170), (0, 0, W * SS, sh * 4 * SS), m)
    c.img.paste((230, 140, 230), (0, 0, W * SS, sh * 4 * SS), m2)


def north(tl, t):
    T = tl.t
    night = ease(tl.prog("no_night", t, 0.0, 0.8))
    c = Canvas(north_bg(night).copy())
    aurora(c, t, tl.prog("no_lights", t, 0.0, 0.5))
    c.tint = ((16, 22, 66), 0.4 * night) if night > 0.01 else None
    P.snowfall(c, t, n=30, seed=6, speed=30, size=(1.5, 3.0))

    # Arctic animals
    ka = tl.prog("no_animals", t, 0.0, 0.2)
    P.seal(c, 150, 410, 0.5, 1, t, seed=1)
    P.walrus(c, 800, 400, 0.5, -1, t, seed=1)
    P.walrus(c, 880, 404, 0.42, 1, t, seed=2.5)
    hop_y = -30 * math.sin(math.pi * ka) if 0 < ka < 1 else 0.0
    P.arctic_fox(c, FOX[0], FOX[1] - 8 + hop_y, 0.7, 1, t)
    P.seal(c, 680, 520, 0.8, -1, t, head_only=True, seed=2)
    for i, (txt, xy, tip, a) in enumerate((("Arctic fox", (520, 330), (FOX[0] + 10, FOX[1] - 90), 0.15),
                                            ("Walruses", (820, 300), (820, 350), 0.45),
                                            ("Seals", (330, 330), (170, 380), 0.7))):
        kk = window(tl, t, ("no_animals", a), ("no_pole", 0.2))
        K.label(c, xy[0], xy[1], txt, 26, tip=tip, k=kk)

    # Bjorn rises from behind a snowdrift
    rise = ease_out(tl.prog("no_rise", t, 0.0, 0.9))
    if rise > 0:
        b_eyes = "happy" if tl.talking("bjorn", t) and t < T("no_spot", 0.3) else "open"
        if t >= T("no_nap") and night > 0.5:
            b_eyes = "happy"
        wave = 0.0
        if between(tl, t, ("no_reply", 0.6), ("no_wave", 1.0)):
            wave = ease(tl.prog("no_reply", t, 0.6, 0.8)) * (1 - tl.prog("no_wave", t, 0.8, 1.0))
        look = (-1, 0) if t < T("no_lights") else (-0.5, -1)
        P.bjorn(c, BJ[0], BJ[1] + 300 * (1 - rise), 0.95, -1, t, tl.mouth("bjorn", t), b_eyes, look=look, wave=wave)
    if rise < 1:
        c.ellipse(BJ[0] - 20, FLOE_Y + 30, 200, 44, P.SNOW)
        c.ellipse(BJ[0] + 60, FLOE_Y + 16, 120, 34, P.SNOW)
        c.ellipse(BJ[0] - 60, FLOE_Y + 50, 140, 30, P.SNOW, ol=None)

    # the friends land on the big floe
    land = ease(tl.prog("no_land", t, 0.0, 0.7))
    x = lerp(-160, N_LAND[0], land)
    y = lerp(220, N_LAND[1], land)
    s = CREW_P
    eyes, look, extra = {}, {"luna": (1, 0), "whiskers": (1, 0), "pip": (1, 0)}, {}
    if between(tl, t, ("no_pole", 0.0), ("no_rise", 1.0)):
        look["whiskers"] = (-1, -0.3) if (t * 1.4) % 2 < 1 else (1, -0.3)
    if between(tl, t, ("no_rise", 0.3), ("no_spot", 0.4)):
        eyes = {"whiskers": "wide", "pip": "wide", "luna": "wide"}
    if t >= T("no_lights"):
        look = {"luna": (1, -1), "pip": (1, -1)}
        eyes = {"luna": "happy", "pip": "happy"}
    sleeping = T("no_nap", 0.6) <= t < T("no_lights", 0.6)
    if T("no_nap") <= t < T("no_nap", 0.6):
        eyes["whiskers"] = "happy"
    if sleeping:
        extra = {"whiskers": {"pose": "sleep", "dy": 6}}
    shiver = math.sin(t * 60) * 2.2 * land * (1 if between(tl, t, ("no_why", 0.0), ("no_why", 1.0)) else 0.3)
    K.crew(c, tl, t, x + shiver, y, s, 1, fly=1 - land, eyes=eyes, look=look, extra=extra)
    if sleeping:
        D.zzz(c, x - 52 * s + 10, y - 150, t)
    if land > 0.01:
        breath(c, x - 52 * s + 44, y - 40 * s - 70, t, 0.7 * land)
        breath(c, x + 46 * s + 44, y - 40 * s - 70, t + 0.4, 0.5 * land)
    # messages: Pebble's to Bjorn, Bjorn's back to Pebble
    wx, wy = x - 52 * s + 30, y - 40 * s - 40
    bpaw = (BJ[0] - 60, BJ[1] - 150)
    m1 = tl.prog("no_msg", t, 0.25, 0.6)
    if t < T("no_msg", 0.25):
        P.envelope(c, wx, wy, 0.9)
    elif m1 < 1:
        envelope_fly(c, (wx, wy), bpaw, m1)
    elif t < T("no_reply", 0.5):
        P.envelope(c, bpaw[0], bpaw[1], 0.9)
    m2 = tl.prog("no_reply", t, 0.5, 0.85)
    if 0 < m2 < 1:
        envelope_fly(c, bpaw, (wx, wy), m2, col=(214, 236, 255))
    elif m2 >= 1 and t < T("no_lights"):
        P.envelope(c, wx + 10, wy + 4, 0.9, col=(214, 236, 255))
    c.tint = None

    # --- teaching moments
    kn = window(tl, t, ("no_narr", 0.1), ("no_animals", 0.1))
    if kn > 0.01:
        K.inset(c, 1060, 170, 300, 240, kn, lambda ic: globe_here(ic, t, True, "Top of the world"))
        K.label(c, 600, 80, "The Arctic", 44, k=kn, col=(40, 60, 140))
    question(c, x - 30, y - 200, window(tl, t, ("no_pole", 0.3), ("no_rise", 0.5)), t)
    ks = window(tl, t, ("no_spot", 0.35), ("no_msg", 0.1))
    if ks > 0.01:
        K.inset(c, 600, 210, 320, 260, ks, lambda ic: globe_here(ic, t, True, "North Pole = the very top"))
    kc = window(tl, t, ("no_float", 0.15), ("no_why", 0.0))
    if kc > 0.01:
        K.inset(c, 600, 230, 460, 300, kc, lambda ic: P.cut_arctic(ic, t, tl.prog("no_float", t, 0.3, 0.6)))
        K.label(c, 600, 410, "The Arctic = frozen ocean", 26, k=tl.prog("no_cut", t, 0.05, 0.25) * kc,
                bg=(255, 244, 190))
    kt = window(tl, t, ("no_straight", 0.0), ("no_days", 0.0))
    if kt > 0.01:
        k_st = tl.prog("no_straight", t, 0.15, 0.7)
        k_sl = tl.prog("no_slant", t, 0.1, 0.6)
        K.inset(c, 600, 240, 560, 340, kt, lambda ic: P.torch_diagram(ic, t, k_st, k_sl), bg=(20, 20, 50))
    kd = window(tl, t, ("no_days", 0.0), ("no_night", 0.3))
    if kd > 0.01:
        kw = tl.prog("no_days", t, 0.48, 0.56)
        K.inset(c, 600, 230, 440, 290, kd, lambda ic: P.days_diagram(ic, t, 1.0, kw))
    K.label(c, 640, 440, "Northern lights!", 30, k=window(tl, t, ("no_lights", 0.3), ("no_aurora", 0.85)),
            col=(40, 120, 80), bg=(220, 255, 230))
    K.sub_band(c, tl, t)
    return c


# ==================================================================== remember

FACTS = ["The North Pole is at the top of the Earth. The South Pole is at the bottom.",
         "Polar bears live in the north. Penguins live in the south.",
         "The poles are the coldest places: the sun's light there is weak."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_poles, P.icon_animals, P.icon_slant], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def icon_south_peng(c, x, y, r, t=0.0):
    P.globe_pin_icon(False)(c, x - r * 0.15, y, r * 0.85, t)
    P.penguin_icon(c, x + r * 0.62, y + r * 0.2, r * 0.42, t)


def icon_north_peng(c, x, y, r, t=0.0):
    P.globe_pin_icon(True)(c, x - r * 0.15, y, r * 0.85, t)
    P.penguin_icon(c, x + r * 0.62, y - r * 0.3, r * 0.42, t)


def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Which pole is at the top of the Earth?", ["The North Pole", "The South Pole"], 0,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.globe_pin_icon(True), P.globe_pin_icon(False)], number=1,
                        answer_text="The North Pole!")
    else:
        c = K.quiz_card(t, "Where do penguins live?", ["Near the North Pole", "Near the South Pole"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[icon_north_peng, icon_south_peng], number=2, answer_text="Near the South Pole!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def pen_pals(c, x, y, k, t):
    """Thought bubble: Bjorn and Pebble with a letter flying between them."""
    if k <= 0.01:
        return
    K.bubble(c, x, y, 170, 92, k, tail=(PIP_X + 40, SY - 90))
    c.push(x, y, pop(k))
    P.bear_icon(c, -110, 4, 44, t)
    P.penguin_icon(c, 110, 6, 52, t)
    u = (math.sin(t * 2.2) + 1) / 2
    ex, ey = lerp(-50, 50, u), -16 - 26 * math.sin(math.pi * u)
    P.envelope(c, ex, ey, 0.8)
    c.pop()


def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("evening").copy())
    spins = [(T("h_pip", 0.3), 300)]
    lon = sill_globe_lon(tl, t, spins)
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    P.ice_cap(c, gcx, gcy, OG_R, lon, 18, True, 72, roll=-23.5)
    P.ice_cap(c, gcx, gcy, OG_R, lon, 18, False, 66, roll=-23.5)
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
    pen_pals(c, 900, 170, window(tl, t, ("h_pip", 0.1), ("h_nap", 0.4)), t)
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Weather and Seasons", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "south": south, "trip": trip, "north": north,
               "remember": remember, "quiz": quiz, "home": home}
