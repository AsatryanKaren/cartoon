"""Scenes of Episode 7 "Rainforests". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py; the animals, the tall
layered forest and the layer gauge come from props.py.

The forest and climb scenes are one continuous world: a tall forest picture (props.forest_image,
FH px high) seen through a camera that tilts up and down (cam = world y of the top of the screen).
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e07_rainforests import props as P

CONTINUOUS = ("map", "climb")      # the sill flashes into space; the climb follows on from the floor
EXTRA_CUTS = ()

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def hop(a, b, u, h=80):
    """Point on a jump arc from a to b."""
    u = ease(clamp(u))
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


def keys_val(t, keys, r=0.25):
    """Smoothly interpolated value through [(time, value), ...] sorted by time."""
    keys = sorted(keys, key=lambda kv: kv[0])
    return K.smooth(t, keys, r)


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 7, "Rainforests")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
WIN = (170, 40, 1110, SY - 34)
GCX, GCY, GR = K.GLOBE_X, SY - 170, 100


def rainy_home():
    """The day room with a grey, rainy sky in the window."""
    def make():
        img = K.home_bg("day").copy()
        x0, y0, x1, y1 = [v * SS for v in WIN]
        win = img.crop((x0, y0, x1, y1))
        grey = D.gradient(x1 - x0, y1 - y0, [(0, (120, 130, 150)), (1, (170, 180, 192))])
        from PIL import Image
        win = Image.blend(win, grey, 0.55)
        img.paste(win, (x0, y0))
        c = Canvas(img)
        for cx, cy, s in ((330, 100, 1.1), (700, 80, 1.3), (980, 130, 0.9), (520, 160, 0.8)):
            D.cloud(c, cx, cy, s, (150, 156, 172))
        rng = np.random.default_rng(5)
        for _ in range(40):
            x, y = rng.uniform(WIN[0] + 10, WIN[2] - 10), rng.uniform(WIN[1] + 10, WIN[3] - 10)
            c.ellipse(x, y, 3, 4.5, (210, 224, 240), ol=(150, 166, 190), w=1)
        return c.img
    return cached("rainy_home", make)


def mullions(c, night=False):
    x0, y0, x1, y1 = WIN
    frame = (255, 250, 240)
    for mx in (483, 797):
        c.rect(mx - 6, y0, mx + 6, y1, frame, w=2)


def window_rain(c, t, k=1.0):
    P.rain(c, t, WIN[0] + 4, WIN[1] + 4, WIN[2] - 4, WIN[3] - 30, n=80, k=k, col=(222, 232, 248), speed=700)
    mullions(c)


def sill_globe_lon(t, spins):
    lon = 30.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def rain_trees(c, x, y, k):
    """Whiskers' idea of a rainforest: trees made of raindrops."""
    if k <= 0.01:
        return
    K.bubble(c, x, y, 150, 96, k, tail=(260, 390))
    c.push(x, y, pop(k))
    for dx, s in ((-70, 0.9), (0, 1.15), (70, 0.85)):
        c.rect(dx - 5, 20 * s, dx + 5, 62, (150, 196, 240), w=2)
        for (ox, oy) in ((0, -30), (-22, -6), (22, -6), (-12, 18), (12, 18)):
            px, py = dx + ox * s, oy * s
            c.poly([(px, py - 18 * s), (px + 11 * s, py + 2 * s), (px, py + 13 * s), (px - 11 * s, py + 2 * s)],
                   (110, 176, 246), w=2)
    K.text(c, 0, -76, "?", 40, (90, 130, 200), stroke=3, stroke_fill=(255, 255, 255))
    c.pop()


def warm_wet_inset(ic, t):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 210, 240)), (0.55, (200, 232, 240)),
                                                       (0.56, (70, 140, 70)), (1, (40, 100, 50))]), (0, 0))
    ic.circle(w - 60, 46, 26, (255, 214, 80), ol=None)
    for i, x in enumerate((60, 150, 250, 340)):
        D.tree(ic, x, h - 20 - 8 * (i % 2), 0.7 + 0.15 * (i % 2), leaf=(50, 140, 60))
    P.rain(ic, t, 0, 0, w, h - 30, n=40, col=(255, 255, 255), speed=500)
    K.text(ic, w / 2, h - 26, "Warm + wet!", 30, (255, 255, 255), stroke=3)


def sill(tl, t):
    T = tl.t
    c = Canvas(rainy_home().copy())
    window_rain(c, t)
    spins = [(T("s_open", 0.1), 200), (T("s_where", 0.4), 300), (T("s_hold", 0.6), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(t, spins)
    # stop near South America / Africa while the Equator and rainforests are shown
    show = tl.prog("s_eq", t, 0.0, 0.3) * (1 - tl.prog("s_hold", t, 0.5, 0.7))
    lon_show = -40 + 6 * math.sin(t * 0.5)
    lon = lerp(lon, lon_show + 360 * round((lon - lon_show) / 360), ease(show))
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    ek = tl.prog("s_eq", t, 0.3, 0.7) * (1 - tl.prog("s_glow", t, 0.3, 0.5))
    if ek > 0.01:
        P.equator_on_globe(c, GCX, GCY, GR, lon, 18, ek, roll=-23.5, w=5)
    fk = tl.prog("s_near", t, 0.1, 0.4) * (1 - tl.prog("s_glow", t, 0.3, 0.5))
    if fk > 0.01:
        P.forests_on_globe(c, GCX, GCY, GR, lon, 18, fk, t, roll=-23.5)

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if T("s_every", 0.6) <= t < T("s_made", 1):
            w_eyes = "wide"
        grumpy = t < T("s_every")
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.6) if grumpy else (1, -0.3), head_dy=4 if grumpy else 0)
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t > T("s_where") else -1, proud=tl.talking("pip", t))
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

    # teaching moments
    rain_trees(c, 470, 170, tl.prog("s_made", t, 0.05, 0.3) * (1 - tl.prog("s_warm", t, 0.0, 0.2)))
    kw = tl.prog("s_warm", t, 0.3, 0.5) * (1 - tl.prog("s_where", t, 0.1, 0.4))
    if kw > 0.01:
        K.inset(c, 920, 170, 400, 240, kw, lambda ic: warm_wet_inset(ic, t))
    K.label(c, 930, 120, "The Equator", 30, tip=(GCX + 92, GCY + 20), k=ek * (1 - tl.prog("s_hold", t, 0.0, 0.2)),
            col=(150, 100, 20))
    K.label(c, 330, 120, "Rainforests grow here", 28, tip=(GCX - 50, GCY + 26),
            k=fk * (1 - tl.prog("s_hold", t, 0.0, 0.2)), col=(30, 110, 50))
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, GCX, GCY, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
AMAZON_PT = (-62, -4)
GO_PATH = [HOME, (-18, 32), (-42, 12), AMAZON_PT]
LON_SHOW = -30


def space_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -16 * (t - t0) + 60
    t_set = tl.t("m_green", 0.4)
    end = -16 * (t_set - t0) + 60
    target = LON_SHOW + 360 * round((end - LON_SHOW) / 360)
    return lerp(raw, target, ease(tl.prog("m_green", t, 0.0, 0.4)))


def map_crew(c, tl, t, x, y, s, **kw):
    K.crew(c, tl, t, x, y, s, 1, fly=1.0, **kw)


LOOK_UP = {"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)}


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        gx, gy = lerp(760, 640, k), 340
        lon = space_lon(tl, t)
        lat = lerp(14, 0, ease(tl.prog("m_green", t, 0.3, 1.0)))
        K.globe(c, gx, gy, r, lon=lon, lat=lat, glow=0.5)
        fk = tl.prog("m_green", t, 0.1, 0.4)
        P.forests_on_globe(c, gx, gy, r, lon, lat, fk, t)
        ek = tl.prog("m_eqline", t, 0.15, 0.6)
        P.equator_on_globe(c, gx, gy, r, lon, lat, ek, w=6)
        K.label(c, gx - r - 120, gy - 110, "Equator", 30, tip=(gx - r * 0.75, gy + r * math.sin(math.radians(lat)) * 0.5),
                k=tl.prog("m_eqline", t, 0.5, 0.7), col=(150, 100, 20))
        K.label(c, gx + r + 110, gy - 150, "Rainforests", 30, tip=(gx + r * 0.1, gy + 20),
                k=tl.prog("m_green", t, 0.3, 0.5), col=(30, 110, 50))
        fkk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        x = lerp(-200, 170, fkk)
        y = lerp(820, 660, fkk)
        map_crew(c, tl, t, x, y, 0.75, look=LOOK_UP, eyes={"whiskers": "wide"} if t < T("m_eqline") else None)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_amazon"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=LON_SHOW)
        if k >= 1:
            v = K.MapView(0, 0, 1)
            kk = tl.prog("m_flat", t, 0.85, 1.0)
            P.forests_on_map(c, v, kk, t)
            P.equator_on_map(c, v, kk)
            K.map_labels(c, v, "continents", kk)
        map_crew(c, tl, t, 170, 660, 0.75, look=LOOK_UP)
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    zk = ease(tl.prog("m_amazon", t, 0.2, 0.9))
    cam = K.lerp_view((0, 0, 1.0), (-60, -10, 2.6), zk)
    # m_path: pull back to see home, then dive into the Amazon
    pk1 = ease(tl.prog("m_path", t, 0.0, 0.3))
    pk2 = ease(tl.prog("m_path", t, 0.78, 1.0))
    if pk1 > 0:
        cam = K.lerp_view(cam, (-30, 20, 1.4), pk1)
    if pk2 > 0:
        cam = K.lerp_view(cam, (AMAZON_PT[0], AMAZON_PT[1], 6.0), pk2)
    c, v = K.map_view(*cam, t=t)
    P.forests_on_map(c, v, 1.0, t)
    P.equator_on_map(c, v, 1.0)
    ex, ey = v.xy(-100, 0)
    lk = 1 - tl.prog("m_path", t, 0.0, 0.2)
    K.map_label(c, v, -105, 3.5, "Equator", 22 * min(1.6, v.z ** 0.5), (255, 220, 90), lk)
    K.map_labels(c, v, "continents", (1 - zk) * lk)
    K.map_highlight(c, v, "south america", tl.prog("m_amazon", t, 0.5, 0.8) * (1 - tl.prog("m_lot", t, 0.6, 1.0)),
                    t=t)
    ak = tl.prog("m_amazon", t, 0.6, 0.85) * lk
    if ak > 0.01:
        P.forests_on_map(c, v, 1.0, t, only=[P.AMAZON])
        x, y = v.xy(-62, -5)
        K.label(c, x + 40, y - 150, "The Amazon Rainforest", 32, tip=(x, y - 10), k=ak, col=(30, 110, 50))
        K.map_label(c, v, -60, -27, "South America", 22 * min(1.6, v.z ** 0.5), (255, 255, 255), ak)
    hk = tl.prog("m_lot", t, 0.1, 0.3) * lk
    if hk > 0.01:
        # how big: a dashed ring around the whole Amazon
        x, y = v.xy(-62, -5)
        rx, ry = 20 * v.z * 0.95 * 640 / 180 * 1.0, 11 * v.z * 640 / 180
        n = 36
        for i in range(0, n, 2):
            a0, a1 = TAU_(i / n), TAU_((i + 1) / n)
            c.line([(x + math.cos(a0) * rx, y + math.sin(a0) * ry), (x + math.cos(a1) * rx, y + math.sin(a1) * ry)],
                   (255, 236, 110), 5 * hk)
    # path + flying cushion
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.15, 0.85)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        hx, hy = v.xy(*HOME)
        K.you_are_here(c, hx, hy, t, tl.prog("m_path", t, 0.05, 0.2) * (1 - tl.prog("m_path", t, 0.7, 0.8)), "Home", side=1)
        if u > 0.0:
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, -1 if math.cos(ang) < 0 else 1, fly=1)
    if t < T("m_path", 0.15):
        sk = ease(tl.prog("m_path", t, 0.0, 0.15))
        hx, hy = v.xy(*HOME)
        x = lerp(170, hx, sk)
        y = lerp(660, hy + 6, sk)
        s = lerp(0.75, 0.16 * v.z ** 0.8, sk)
        eyes = {"whiskers": "wide"} if T("m_lot") <= t < T("m_path") else None
        map_crew(c, tl, t, x, y, s, look=LOOK_UP, eyes=eyes)
        bk = tl.prog("m_lot", t, 0.1, 0.3) * (1 - tl.prog("m_path", t, 0.0, 0.1))
        if bk > 0.01:
            K.bubble(c, 330, 420, 110, 70, bk, tail=(160, 560))
            c.push(330, 420, bk)
            for dx in (-46, 0, 46):
                D.tree(c, dx, 40, 0.32, leaf=(50, 140, 60))
            P.rain(c, t, -90, -60, 90, 40, n=16, col=(90, 150, 230), speed=200, length=12)
            c.pop()
    K.flash(c, tl.prog("m_path", t, 0.92, 1.0), (255, 255, 255))
    return c


def TAU_(u):
    return u * 2 * math.pi


# ======================================================== the forest (floor + climb, one world)

FX = P
GROUND = P.GROUND
CREW_X = 330
CRS = 1.2                         # cushion scale in the forest
LOG_X = 720                       # Coco's mossy log on the forest floor
JAG_X = 1130
UMB_X = 560                       # where Whiskers stands with his leaf umbrella
WLAND_X = 880                     # where Whiskers lands after his fall
MOSSY_X = 800
HANG_X = 560                      # where Whiskers hangs from the branch
COCO_BRANCH = (990, None)
TOP_CREW = (560, 470)
FROG = (930, 1790)
UPPER_Y = 905                     # the monkeys' upper branch


def plan(tl):
    """Keyframes for the camera, the crew's cushion and Coco (world coordinates)."""
    key = ("plan", id(tl))
    if key in _cache:
        return _cache[key]
    T = tl.t
    floor_y = GROUND
    und_y = P.UND_CAM + 540
    can_y = P.CAN_CAM + 560
    cam = [(T("f_land"), P.FLOOR_CAM), (T("f_up", 0.25), P.FLOOR_CAM), (T("c_rise", 1.0), P.UND_CAM),
           (T("c_rise2", 0.1), P.UND_CAM), (T("c_rise2", 1.0), P.CAN_CAM), (T("k_slip", 0.7), P.CAN_CAM), (T("k_yell", 1.0), P.FLOOR_CAM),
           (T("k_top", 0.05), P.FLOOR_CAM), (T("k_top", 0.95), P.TOP_CAM), (T("k_laugh", 1.0), P.TOP_CAM)]
    crew_y = [(T("f_land"), floor_y - 760), (T("f_land", 0.55), floor_y), (T("f_up", 0.25), floor_y),
              (T("c_rise", 1.0), und_y), (T("c_rise2", 0.1), und_y), (T("c_rise2", 1.0), can_y),
              (T("k_yawn", 0.25), can_y), (T("k_yawn", 0.85), floor_y), (T("k_top", 0.05), floor_y),
              (T("k_top", 0.95), TOP_CREW[1]), (T("k_laugh", 1.0), TOP_CREW[1])]
    crew_x = [(T("f_land"), CREW_X), (T("c_rise", 0.5), CREW_X), (T("c_rise2", 1.0), 300),
              (T("k_yawn", 0.25), 300), (T("k_yawn", 0.85), CREW_X), (T("k_top", 0.1), CREW_X),
              (T("k_top", 0.9), TOP_CREW[0]), (T("k_laugh", 1.0), TOP_CREW[0])]
    log_top = (LOG_X, GROUND - 62)
    perch = (990, P.branch_y(990) - 13)
    top_perch = (1000, 150)
    # Coco: (time, x, y, fly)
    coco = [(T("f_land"), 1500, GROUND - 900, 1), (T("f_flyin"), 1500, GROUND - 900, 1),
            (T("f_flyin", 0.95), *log_top, 1), (T("f_hola", 0.1), *log_top, 0),
            (T("f_up", 0.2), *log_top, 0), (T("f_up", 0.7), CREW_X + 330, GROUND - 160, 1),
            (T("c_rise", 1.0), CREW_X + 330, und_y - 160, 1), (T("c_rise2", 0.1), CREW_X + 330, und_y - 160, 1),
            (T("c_rise2", 1.0), *perch, 1), (T("c_canopy", 0.05), *perch, 0),
            (T("k_yawn", 0.2), *perch, 0), (T("k_yawn", 0.3), perch[0], perch[1] - 30, 1),
            (T("k_purpose", 0.1), log_top[0], log_top[1], 1), (T("k_purpose", 0.2), *log_top, 0),
            (T("k_top", 0.05), *log_top, 0), (T("k_top", 0.15), log_top[0] + 60, log_top[1] - 150, 1),
            (T("k_top", 0.9), top_perch[0], top_perch[1] - 40, 1), (T("k_top", 1.0), *top_perch, 0),
            (T("k_laugh", 1.0), *top_perch, 0)]
    out = dict(cam=cam, crew_y=crew_y, crew_x=crew_x, coco=coco)
    _cache[key] = out
    return out


def coco_at(tl, t):
    keys = plan(tl)["coco"]
    if t <= keys[0][0]:
        k0 = keys[0]
        return k0[1], k0[2], k0[3]
    for a, b in zip(keys, keys[1:]):
        if t < b[0]:
            u = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), max(a[3], b[3]) if 0 < u < 1 else a[3]
    k1 = keys[-1]
    return k1[1], k1[2], k1[3]


def whiskers_state(tl, t):
    """Where Whiskers is when he is NOT on the cushion: None, or dict(x, y, mode, ...)."""
    T = tl.t
    cx, cy = keys_val(t, plan(tl)["crew_x"]), keys_val(t, plan(tl)["crew_y"])
    seat = (cx - 52 * CRS, cy - 40 * CRS)
    # the umbrella gag on the forest floor
    if T("f_umb") <= t < T("f_layers", 0.95):
        a = tl.prog("f_umb", t, 0.0, 0.3)
        b = tl.prog("f_layers", t, 0.55, 0.95)
        if b > 0:
            x, y = hop((UMB_X, GROUND), seat, b, 110)
            return dict(x=x, y=y, mode="leap" if b < 0.95 else "sit", face=-1 if b < 0.95 else 1, s=lerp(0.9, 0.74, b))
        x, y = hop(seat, (UMB_X, GROUND), a, 110)
        return dict(x=x, y=y, mode="leap" if 0.02 < a < 0.95 else "stand", face=1, s=lerp(0.74, 0.9, a))
    # the sloth nap and the big fall
    if T("k_hang") <= t < T("k_yawn", 0.95):
        bx = HANG_X
        by = P.branch_y(bx) + 13
        a = tl.prog("k_hang", t, 0.0, 0.3)
        if a < 1:
            x, y = hop(seat, (bx, by - 40), a, 160)
            return dict(x=x, y=y, mode="leap", face=1, s=lerp(0.74, 0.9, a))
        if t < T("k_slip", 0.75):
            slip = 6 * ease(tl.prog("k_slip", t, 0.0, 0.7))
            return dict(x=bx, y=by + slip, mode="hang", ang=180, s=0.9,
                        eyes="wide" if t > T("k_slip", 0.1) else "closed")
        if t < T("k_yell", 1.0):
            u = clamp((t - T("k_slip", 0.75)) / max(1e-6, T("k_yell", 1.0) - T("k_slip", 0.75)))
            y = lerp(by + 40, GROUND - 60, u ** 1.15)
            x = lerp(bx, WLAND_X, ease(u)) + 30 * math.sin(u * 9)
            return dict(x=x, y=y, mode="tumble", ang=180 + 720 * u, s=0.9, eyes="wide")
        # landed next to the jaguar
        if t < T("k_yawn", 0.55):
            sq = 1 - 0.35 * math.exp(-(t - T("k_land")) * 6) * (t > T("k_land"))
            return dict(x=WLAND_X, y=GROUND, mode="sit", face=1, s=0.9, squash=sq,
                        eyes="wide" if t > T("k_eye", 0.3) else "closed" if t < T("k_land", 0.6) else "open",
                        dizzy=T("k_land") <= t < T("k_eye", 0.5))
        u = tl.prog("k_yawn", t, 0.55, 0.95)
        x, y = hop((WLAND_X, GROUND), seat, u, 200)
        return dict(x=x, y=y, mode="leap", face=-1, s=lerp(0.9, 0.74, u), eyes="wide")
    return None


def draw_whiskers(c, tl, t, st):
    mode = st["mode"]
    if mode in ("hang", "tumble"):
        def fn(sc, cx, cy):
            yoff = 0 if mode == "hang" else 70
            kat(sc, tl, t, "whiskers", cx - 10, cy + yoff, st["s"], 1, "stand", eyes=st.get("eyes", "open"))
        P.sprite(c, st["x"], st["y"], 380, st["ang"], fn)
        if mode == "hang" and st.get("eyes") == "closed":
            D.zzz(c, st["x"] + 60, st["y"] + 120, t)
        return
    kw = {}
    if "eyes" in st:
        kw["eyes"] = st["eyes"]
    if "squash" in st:
        kw["squash"] = st["squash"]
    kat(c, tl, t, "whiskers", st["x"], st["y"], st["s"], st.get("face", 1), mode, wet=st.get("wet", 0.0), **kw)
    if st.get("dizzy"):
        for k in range(3):
            a = t * 5 + k * 2.1
            K.star(c, st["x"] + math.cos(a) * 46, st["y"] - 120 + math.sin(a) * 12, 9, (255, 236, 90), ol=OUT)


def forest(tl, t):
    return jungle(tl, t)


def climb(tl, t):
    return jungle(tl, t)


def upper_branch(c):
    xs = np.linspace(360, 900, 24)
    top = [(x, UPPER_Y - 9 + 0.0004 * (x - 630) ** 2) for x in xs]
    bot = [(x, y + 18) for x, y in top[::-1]]
    c.poly(top + bot, (118, 84, 54), w=3)


def frog_leaf(c, t):
    x, y = FROG
    P._leafy(c, x, y + 4, 1.0, (70, 150, 76), -6)


def log(c):
    x, y = LOG_X, GROUND
    c.rect(x - 70, y - 62, x + 70, y, (120, 84, 56), r=14)
    c.ellipse(x + 70, y - 31, 14, 31, (176, 130, 86))
    c.ellipse(x + 70, y - 31, 7, 16, (140, 100, 66), w=2)
    for dx in (-50, -10, 30):
        c.ellipse(x + dx, y - 62, 24, 7, (100, 160, 80), ol=None)


def ants(c, t, k=1.0):
    for i in range(14):
        x = (i * 96 - t * 30) % (W + 120) - 60
        if 380 < x < 470 or 640 < x < 800:
            continue
        P.ant(c, x, GROUND + 14, 1.15, t, leaf=i % 3 != 2, face=-1)


def gauge_k(tl, t):
    T = tl.t
    a = tl.prog("f_layers", t, 0.45, 0.65)
    b = 1 - tl.prog("k_emergent", t, 0.3, 0.45)
    return a * b


def jungle(tl, t):
    T = tl.t
    pl = plan(tl)
    cam = keys_val(t, pl["cam"], 0.3)
    wst = whiskers_state(tl, t)
    if wst is not None and wst["mode"] == "tumble":
        cam = clamp(wst["y"] - 360, P.CAN_CAM, P.FLOOR_CAM)
    cam = clamp(cam, 0, P.FH - H)
    c = P.forest_view(cam)
    cx, cy = keys_val(t, pl["crew_x"]), keys_val(t, pl["crew_y"])
    landing = T("f_land") <= t < T("f_land", 0.6)
    c.push(0, -cam)
    vis = lambda y0, y1: y1 > cam - 50 and y0 < cam + H + 50   # noqa: E731

    # ---- emergent layer: the harpy eagle on the tallest tree
    if vis(0, 400):
        P.eagle(c, 200, 172, 0.8, 1, t)
    # ---- canopy: monkeys, macaw, butterflies, Mossy
    if vis(UPPER_Y - 40, P.CAN_BOT):
        upper_branch(c)
        for i, (mx, ph) in enumerate(((470, 0.0), (650, 1.7))):
            ang = 24 * math.sin(t * 2.2 + ph)
            P.monkey(c, mx, UPPER_Y + 0.0004 * (mx - 630) ** 2, 1.0, t, ang, 1 if i else -1)
        P.macaw(c, 390, P.branch_y(390) - 13, 0.9, 1, t)
        for i, (bx, by) in enumerate(((560, 1000), (900, 960), (250, 1060))):
            D.butterfly(c, bx + 40 * math.sin(t * 0.9 + i * 2), by + 20 * math.sin(t * 1.7 + i), t + i,
                        1.2, col=(70, 140, 250), col2=(40, 90, 200))
        wave = tl.prog("k_bye", t, 0.0, 0.5) * (1 - tl.prog("k_laugh", t, 0.5, 1.0))
        sl_eyes = "sleepy"
        if T("k_hello") <= t < T("k_nap", 1):
            sl_eyes = "open" if tl.talking("mossy", t) else "sleepy"
        P.sloth(c, MOSSY_X, P.branch_y(MOSSY_X) - 4, 0.95, t, tl.mouth("mossy", t), sl_eyes, wave)
    # ---- understorey: the little blue frog
    if vis(FROG[1] - 80, FROG[1] + 40):
        frog_leaf(c, t)
        P.dart_frog(c, FROG[0], FROG[1] - 4, 1.4, t, -1)
    # ---- forest floor: log, jaguar, ants
    if vis(GROUND - 300, P.FH):
        log(c)
        eye = 0.0
        yawn = 0.0
        if T("k_eye") <= t < T("k_yawn", 0.9):
            eye = ease(tl.prog("k_eye", t, 0.2, 0.6))
        yawn = math.sin(math.pi * tl.prog("k_yawn", t, 0.0, 0.7))
        if yawn > 0:
            eye = 0.4 * (1 - yawn)
        P.jaguar(c, JAG_X, GROUND + 2, 1.0, -1, t, eye, yawn)
        if eye < 0.1 and yawn < 0.05:
            D.zzz(c, JAG_X - 150, GROUND - 120, t)
        ants(c, t)

    # ---- Coco
    kx, ky, kfly = coco_at(tl, t)
    face = -1
    if T("f_up", 0.2) <= t < T("c_rise2", 1.0) or T("k_top", 0.05) <= t < T("k_top", 0.9):
        face = 1
    coco_eyes = "happy" if T("f_laugh") <= t < T("f_laugh", 1) or t >= T("k_laugh") else "open"
    P.toucan(c, kx, ky, 0.9, face, t, tl.mouth("coco", t), coco_eyes, fly=kfly)

    # ---- the friends on the cushion
    fly = 1.0 if not (T("f_land", 0.6) <= t < T("f_up", 0.2)) else 0.0
    if t >= T("k_yawn", 0.9) and t < T("k_top"):
        fly = 0.0
    who = ("whiskers", "luna", "pip") if wst is None else ("luna", "pip")
    eyes, look, extra = {}, {}, {}
    if T("f_banana") <= t < T("f_name", 0.3):
        eyes["whiskers"] = "wide"
    if T("f_land") <= t < T("f_up"):
        look = {"luna": (1, -0.3), "pip": (1, -0.3), "whiskers": (1, -0.3)}
        if T("f_block") <= t < T("f_block", 1):
            look = {"luna": (0.3, -1), "pip": (0.3, -1), "whiskers": (0.3, -1)}
    if T("c_rise") <= t < T("k_hang"):
        look = {"luna": (1, -0.6), "pip": (1, -0.6), "whiskers": (1, -0.6)}
    if T("k_slip", 0.7) <= t < T("k_yell", 1):
        eyes.update({"luna": "wide", "pip": "wide"})
    laugh = T("f_laugh") <= t < T("f_laugh", 1) or t >= T("k_laugh")
    if laugh:
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}}
    if T("k_purpose") <= t < T("k_purpose", 1):
        eyes["whiskers"] = "closed"
    if wst is None and T("f_fill", 0.8) <= t < T("f_up"):
        extra.setdefault("whiskers", {})["wet"] = 1.0
    K.crew(c, tl, t, cx, cy, CRS, 1, fly=fly, eyes=eyes, look=look, extra=extra, who=who)
    if landing:
        for i in range(6):
            u = (t - T("f_land")) * 0.8 + i * 0.13
            lx = CREW_X - 200 + i * 80 + 30 * math.sin(t * 3 + i)
            P._leafy(c, lx, cy - 300 + 400 * (u % 1), 0.4, (110, 180, 80), 40 * math.sin(t * 2 + i))

    # ---- Whiskers on his own (umbrella, hanging, falling, landing)
    if wst is not None:
        if T("f_umb") <= t < T("f_layers", 0.55):
            draw_umbrella_gag(c, tl, t, wst)
        else:
            draw_whiskers(c, tl, t, wst)
        if wst["mode"] == "sit" and T("k_land") <= t < T("k_land", 0.6):
            u = tl.prog("k_land", t, 0.0, 0.6)
            for i in range(8):
                a = -math.pi * (0.1 + 0.8 * i / 7)
                P._leafy(c, WLAND_X + math.cos(a) * 140 * u, GROUND - 30 + math.sin(a) * 120 * u + 80 * u * u,
                         0.35, (150, 110, 60), i * 40)
    c.pop()

    # ---- foreground, rain and teaching overlays
    P.front_leaves(c, cam)
    rk = tl.prog("f_drip", t, 0.0, 0.6) * (1 - tl.prog("f_year", t, 0.6, 1.0))
    if rk > 0.01:
        P.rain(c, t, 0, -30, W, H, n=110, k=rk, col=(190, 220, 255), speed=1100, length=30)
    # layer names
    for ev, name, kk in (("f_floor", "The forest floor", (0.0, 0.2)), ("c_under", "The understorey", (0.0, 0.2)),
                         ("c_canopy", "The canopy", (0.0, 0.2)), ("k_emergent", "The emergent layer", (0.0, 0.2))):
        a = tl.prog(ev, t, *kk) * (1 - tl.prog(ev, t, 0.85, 1.0))
        if ev == "c_canopy":
            a = tl.prog(ev, t, *kk) * (1 - tl.prog("c_most", t, 0.85, 1.0))
        if a > 0.01:
            K.label(c, 560, 56, name, 36, k=a, col=(40, 90, 40))
    # labels pointing at animals
    T0 = T
    if T0("f_floor") <= t < T0("f_layers"):
        K.label(c, 300, 430 - 60, "Ants", 26, tip=(250, GROUND + 4 - cam), k=tl.prog("f_floor", t, 0.25, 0.4))
        K.label(c, 990, 300, "Jaguar", 26, tip=(JAG_X, GROUND - 80 - cam), k=tl.prog("f_floor", t, 0.4, 0.55))
    if T0("f_block") <= t < T0("f_drip", 0.5):
        k = tl.prog("f_block", t, 0.2, 0.4)
        K.arrow(c, 640, 330, 640, 150, (255, 236, 110), 9, k)
        K.label(c, 640, 100, "Leaves block the sun", 28, k=tl.prog("f_block", t, 0.35, 0.5))
    if T0("f_year") <= t < T0("f_flyin", 0.8):
        K.label(c, 640, 90, "Warm and rainy all year!", 32, k=tl.prog("f_year", t, 0.2, 0.35), col=(30, 110, 50))
    if T0("c_frog") <= t < T0("c_rise2", 0.4):
        K.label(c, FROG[0] - 120, FROG[1] - cam - 120, "Blue frog", 26, tip=(FROG[0], FROG[1] - cam - 30),
                k=tl.prog("c_frog", t, 0.2, 0.4))
    if T0("c_animals") <= t < T0("c_more", 0.15):
        for i, (txt, lx, ly, tip) in enumerate((
                ("Monkeys", 560, 330, (500, UPPER_Y + 80)), ("Macaw", 250, 250, (390, P.branch_y(390) - 70)),
                ("Toucan", 1000, 220, (kx + 20, ky - 80)), ("Butterfly", 860, 300, (900, 960)))):
            K.label(c, lx, ly, txt, 26, tip=(tip[0], tip[1] - cam), k=tl.prog("c_animals", t, 0.1 + 0.2 * i, 0.25 + 0.2 * i))
    mk = tl.prog("c_more", t, 0.15, 0.3) * (1 - tl.prog("c_who", t, 0.0, 0.2))
    if mk > 0.01:
        many = tl.prog("c_more", t, 0.3, 1.0) * 0.6 + tl.prog("c_many", t) * 0.4
        K.inset(c, 640, 210, 560, 290, mk, lambda ic: so_many(ic, t, many))
    if T0("c_who", 0.6) <= t < T0("k_slow", 1):
        K.label(c, 1000, 470, "Mossy the sloth", 28,
                tip=(MOSSY_X + 40, P.branch_y(MOSSY_X) + 60 - cam), k=tl.prog("c_sloth", t, 0.0, 0.3))
    if T0("k_slow", 0.4) <= t < T0("k_nap", 0.5):
        snail_race(c, t, tl.prog("k_slow", t, 0.4, 0.6) * (1 - tl.prog("k_nap", t, 0.3, 0.5)))
    if T0("k_emergent") <= t < T0("k_air"):
        kk = tl.prog("k_emergent", t, 0.25, 0.4)
        K.label(c, 420, 170, "Tallest trees", 28, tip=(260, 300), k=kk)
        K.label(c, 320, 330, "Harpy eagle", 26, tip=(220, 110), k=tl.prog("k_emergent", t, 0.75, 0.9))
    if T0("k_air") <= t < T0("k_bye"):
        fresh_air(c, t, tl.prog("k_air", t, 0.1, 0.5))
    bk = tl.prog("k_bye", t, 0.0, 0.15) * (1 - tl.prog("k_laugh", t, 0.5, 0.9))
    if bk > 0.01:
        wave = tl.prog("k_bye", t, 0.0, 1.0)
        K.inset(c, 640, 180, 360, 240, bk, lambda ic: mossy_inset(ic, tl, t, wave))
    # falling: shout the layer names as he passes them
    if wst is not None and wst["mode"] == "tumble":
        lv = P.level_of(wst["y"])
        name = ["Forest floor!", "Understorey!", "Canopy!", "Canopy!"][int(round(clamp(lv, 0, 3)))]
        K.label(c, 980, 110, name, 34, k=1.0, col=(200, 50, 50))
    # the gauge: which floor of the forest are we on?
    gk = gauge_k(tl, t)
    if gk > 0.01:
        ly = cy
        if wst is not None and wst["mode"] in ("tumble", "hang"):
            ly = wst["y"]
        P.gauge(c, 1080, 150, gk, P.level_of(ly - 110), t)
    K.sub_band(c, tl, t)
    K.flash(c, 1 - tl.prog("f_land", t, 0.0, 0.25), (255, 255, 255))
    return c


def draw_umbrella_gag(c, tl, t, st):
    """Whiskers' giant-leaf umbrella fills with rain and tips over him."""
    T = tl.t
    fill = tl.prog("f_fill", t, 0.05, 0.6)
    tip = tl.prog("f_fill", t, 0.62, 0.74)
    wet = tl.prog("f_fill", t, 0.74, 0.8)
    x, y = st["x"], st["y"]
    holding = st["mode"] == "stand" and t < T("f_fill", 0.9)
    eyes = "open"
    if fill > 0.5 and tip <= 0:
        eyes = "wide"
    if wet > 0:
        eyes = "closed" if t < T("f_wet") else "happy" if tl.talking("whiskers", t) else "open"
    st = dict(st, eyes=eyes, wet=wet)
    if holding:
        lk = tl.prog("f_umb", t, 0.8, 0.95)
        draw_whiskers(c, tl, t, st)
        if lk > 0:
            c.push(x + 40, y - 150, pop(lk))
            P.big_leaf(c, 0, 0, 1.0, -70 * ease(tip), fill * (1 - tip))
            c.pop()
            if lk >= 1:
                c.stroke([(x + 40, y - 80), (x + 30, y - 64)], D.WHISKERS["body"], 10)
        if 0 < tip < 1 or (wet > 0 and t < T("f_fill", 0.9)):
            u = tl.prog("f_fill", t, 0.66, 0.84)
            if 0 < u < 1:
                for i in range(14):
                    dx = -50 + 100 * (i / 13) + 10 * math.sin(i * 3)
                    c.ellipse(x - 20 + dx * 0.6, y - 170 + 160 * u + 20 * math.sin(i), 9, 14, (130, 190, 250),
                              ol=(70, 130, 210), w=2)
    else:
        draw_whiskers(c, tl, t, st)
        if T("f_fill", 0.9) <= t < T("f_wet", 1):
            # the leaf lies on the ground
            P.big_leaf(c, x + 150, y - 10, 0.6, 8, 0)
    if wet > 0 and t < T("f_year", 0.5):
        for i in range(5):
            u = (t * 1.5 + i * 0.2) % 1
            c.ellipse(x - 40 + 20 * i, y - 140 + 140 * u, 3, 5, (140, 196, 250), ol=None)


def snail_race(c, t, k):
    """How slow? A snail would win a race against a sloth (well, almost)."""
    if k <= 0.01:
        return
    def draw(ic):
        w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
        ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (210, 236, 255)), (1, (190, 230, 170))]), (0, 0))
        K.text(ic, w / 2, 30, "Very... slow...", 28, (60, 80, 60))
        ic.line([(20, h - 40), (w - 20, h - 40)], (120, 160, 100), 4)
        u = (t * 0.03) % 1
        P.sloth(ic, 80 + 40 * u, h - 150, 0.45, t, 0, "sleepy", 0.0, sway=0.3)
        ic.line([(30, h - 150), (w - 30, h - 150)], (128, 90, 58), 8)
    K.inset(c, 400, 210, 380, 260, k, draw)


def so_many(ic, t, k):
    """Inset: so many different kinds of plants and animals."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (200, 240, 200)), (1, (150, 210, 150))]), (0, 0))
    items = []
    for row in range(3):
        for col in range(6):
            items.append((60 + col * 88, 62 + row * 74, (row * 6 + col)))
    n = int(k * len(items) + 0.999)
    for x, y, i in items[:n]:
        kind = i % 9
        if kind == 0:
            P.dart_frog(ic, x, y + 18, 1.0, t)
        elif kind == 1:
            D.butterfly(ic, x, y, t + i, 1.1, col=(70, 140, 250), col2=(40, 90, 200))
        elif kind == 2:
            D.flower(ic, x, y + 22, (240, 90, 130), 1.4)
        elif kind == 3:
            P.macaw(ic, x, y + 30, 0.55, 1, t)
        elif kind == 4:
            P.ant(ic, x, y + 10, 1.8, t)
        elif kind == 5:
            ic.circle(x, y, 18, (255, 160, 40))          # fruit
            ic.line([(x, y - 18), (x + 4, y - 26)], (90, 70, 40), 3)
            ic.ellipse(x + 10, y - 24, 9, 4, (90, 170, 80), ol=None)
        elif kind == 6:
            P.monkey(ic, x, y - 30, 0.5, t, 0, 1)
        elif kind == 7:
            D.flower(ic, x, y + 22, (255, 210, 60), 1.4)
            D.flower(ic, x + 18, y + 26, (180, 110, 230), 1.0)
        else:
            P.toucan(ic, x - 10, y + 32, 0.42, 1, t)
    K.text(ic, w / 2, h - 22, "So many kinds!", 30, (255, 255, 255), stroke=3, stroke_fill=(30, 90, 40))


def fresh_air(c, t, k):
    if k <= 0.01:
        return
    for i in range(10):
        u = (t * 0.25 + i / 10) % 1
        x = 100 + i * 115 + 20 * math.sin(t + i)
        y = 640 - 520 * u
        a = k * math.sin(math.pi * u)
        if a < 0.05:
            continue
        pts = [(x + 18 * math.sin(v * 6 + t * 2), y - v * 40) for v in np.linspace(0, 1, 10)]
        c.line(pts, mix((120, 190, 120), (255, 255, 255), a), 4)
        K.sparkles(c, x, y - 40, 20, t, n=2, k=a, seed=i)
    K.label(c, 860, 360, "Fresh air!", 34, k=k, col=(40, 120, 160))


def mossy_inset(ic, tl, t, wave):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (110, 180, 100)), (1, (60, 130, 70))]), (0, 0))
    ic.line([(0, 52), (w, 64)], (128, 90, 58), 22)
    P.sloth(ic, w / 2, 54, 0.85, t, tl.mouth("mossy", t), "open" if wave < 0.9 else "happy",
            min(1, wave * 1.4))
    K.text(ic, w / 2, h - 22, "Mossy", 26, (255, 255, 255), stroke=3)


# ==================================================================== remember

FACTS = ["Rainforests are warm and rainy. They grow near the Equator.",
         "The Amazon is the biggest rainforest in the world.",
         "Rainforests have layers. Most animals live high up in the canopy."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_rain, P.icon_amazon, P.icon_layers], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def icon_floor(c, x, y, r, t=0.0):
    c.rect(x - r, y - r * 0.7, x + r, y + r * 0.6, (40, 70, 50), r=10, w=2)
    c.rect(x - r, y + r * 0.2, x + r, y + r * 0.6, (110, 76, 48), r=6, w=2)
    for k in range(3):
        P.ant(c, x - r * 0.6 + k * r * 0.55, y + r * 0.3, 1.4, t)


def icon_canopy(c, x, y, r, t=0.0):
    c.rect(x - r, y - r * 0.7, x + r, y + r * 0.6, (150, 210, 245), r=10, w=2)
    for dx, dy, rr in ((-0.55, -0.35, 0.45), (0.0, -0.45, 0.5), (0.55, -0.35, 0.45), (-0.3, 0.1, 0.4),
                       (0.35, 0.1, 0.4)):
        c.circle(x + dx * r, y + dy * r, rr * r, (80, 160, 80))
    P.monkey(c, x - r * 0.1, y - r * 0.2, 0.55, t, 10 * math.sin(t * 2), 1)


def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Is a rainforest cold and dry, or warm and wet?",
                        ["Cold and dry", "Warm and wet"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_cold, P.icon_rain], number=1, answer_text="Warm and wet!")
    else:
        c = K.quiz_card(t, "Where do most rainforest animals live?",
                        ["On the forest floor", "High in the canopy"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[icon_floor, icon_canopy], number=2, answer_text="High up in the canopy!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def evening_rainbow():
    def make():
        c = Canvas(K.home_bg("evening").copy())
        cx, cy = 640, WIN[3] + 20
        for i, col in enumerate(((230, 80, 80), (250, 160, 60), (250, 230, 90), (110, 200, 100),
                                 (90, 150, 230), (150, 110, 220))):
            r = 300 - i * 12
            c.arc(cx, cy, r, r, 180, 360, mix(col, (250, 200, 170), 0.25), 12)
        mullions(c)
        return c.img
    return cached("evening_rainbow", make)


def home(tl, t):
    T = tl.t
    c = Canvas(evening_rainbow().copy())
    spins = [(T("h_pip", 0.3), 300)]
    lon = sill_globe_lon(t, spins)
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    e = ease(back)
    x = lerp(GCX, CUSH_X, e)
    y = lerp(GCY + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    sleep = t >= T("h_curl", 0.2)
    extra = {"whiskers": {"pose": "sleep", "dy": 6}} if sleep else None
    K.crew(c, tl, t, x, y, s, 1, fly=1 - back, extra=extra, look={"luna": (1, -0.5), "pip": (1, -0.5)})
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    K.label(c, 640, 130, "The rain stopped!", 28, k=tl.prog("h_narr", t, 0.6, 0.8) * (1 - tl.prog("h_pip", t, 0.5, 0.8)))
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "The Frozen Poles", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "forest": forest, "climb": climb,
               "remember": remember, "quiz": quiz, "home": home}
