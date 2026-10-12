"""Scenes of Episode 2 "The Seven Continents". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py; the episode's
characters and props (Albert the albatross, animals, landmarks) are in props.py.
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e02_seven_continents import props as P

CONTINUOUS = ("map", "ice")      # the sill flashes white into space; the dive flashes white onto the ice
EXTRA_CUTS = ()

STYLE = "continents"
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
    """0..1 visibility: fades in after event-point a, out after event-point b ((id, frac) pairs)."""
    T = tl.t
    ta, tb = T(*a), T(*b)
    return clamp((t - ta) / fade) * (1 - clamp((t - tb) / fade))


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 2, "The Seven Continents")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45            # cushion scale; cats on it are 0.62 * 1.45 = 0.9
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
WIN = (170, 40, 1110, SY - 34)


def rainy_bg():
    """The home window on a grey, rainy morning."""
    def make():
        c = Canvas(K.home_bg("day").copy())
        x0, y0, x1, y1 = WIN
        box = (x0 * SS, y0 * SS, x1 * SS, y1 * SS)
        piece = c.img.crop(box)
        grey = D.gradient(piece.size[0], piece.size[1], [(0, (120, 132, 156)), (1, (176, 188, 204))])
        from PIL import Image
        piece = Image.blend(piece, grey, 0.62)
        c.img.paste(piece, box[:2])
        for cx, cy, s in ((330, 90, 1.0), (640, 70, 1.2), (950, 110, 0.9), (480, 150, 0.7)):
            D.cloud(c, cx, cy, s, col=(150, 158, 176))
        # window frame repainted over the clouds' edges
        frame = (255, 250, 240)
        for mx in (483, 797):
            c.rect(mx - 6, y0, mx + 6, y1, frame, w=2)
        c.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 6, None, ol=frame, w=14)
        c.rect(x0 - 21, y0 - 21, x1 + 21, y1 + 10, None, ol=OUT, w=3)
        return c.img
    return cached("rainy", make)


def rain(c, t, n=70):
    x0, y0, x1, y1 = WIN
    rng = np.random.default_rng(4)
    for i in range(n):
        x = rng.uniform(x0 + 6, x1 - 6)
        sp = rng.uniform(380, 520)
        y = y0 + ((rng.uniform(0, 1) * (y1 - y0) + t * sp) % (y1 - y0))
        if abs(x - 483) < 9 or abs(x - 797) < 9:
            continue
        c.line([(x, y), (x - 3, min(y1 - 2, y + 16))], (214, 226, 240), 2, cap=False)


def sill_globe_lon(tl, t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def globe_inset(ic, t):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    K.globe(ic, w / 2, h / 2 - 12, 78, lon=-t * 25 + 30, lat=20, style=STYLE, glow=0.3)
    K.text(ic, w / 2, h - 22, "Each colour = a continent", 22, (255, 255, 255), stroke=3)


def sill(tl, t):
    T = tl.t
    c = Canvas(rainy_bg().copy())
    rain(c, t)
    spins = [(T("s_open", 0.15), 260), (T("s_narr", 0.2), 200), (T("s_seven", 0.7), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(tl, t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    laugh = T("s_cheese2") <= t < T("s_many")
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if T("s_blobs") <= t < T("s_blobs", 1) or T("s_cheese") <= t < T("s_cheese2", 0.3):
            w_eyes = "wide"
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.5))
        lean = -8 * math.exp(-max(0, t - T("s_narr", 0.2)) * 3) if t > T("s_narr", 0.2) else 0
        kw = {"eyes": "happy", "mouth": laughing(t)} if laugh else {}
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", head_dy=lean, look=(-1, -0.4), **kw)
        kwp = {"eyes": "happy", "mouth": laughing(t + 0.3)} if laugh else {}
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, -1 if T("s_many") <= t < T("s_glow") else 1,
            proud=tl.talking("pip", t), **kwp)
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

    # thought bubbles: sweets? cheese?
    wx, wy = CUSH_X - 52 * CREW_S + 20, SY - 40 * CREW_S - 120
    kb = window(tl, t, ("s_blobs", 0.45), ("s_cont", 0.35))
    if kb > 0.01:
        K.bubble(c, 300, 200, 110, 70, kb, tail=(wx, wy))
        for i, col in enumerate(((240, 100, 140), (110, 190, 240), (250, 200, 70))):
            P.sweet(c, 300 + (i - 1) * 62 * kb, 200 + (8 if i == 1 else -6) * kb, 18 * kb, col)
    kc = window(tl, t, ("s_cheese", 0.35), ("s_many", 0.0))
    if kc > 0.01:
        K.bubble(c, 300, 200, 110, 70, kc, tail=(wx, wy))
        P.cheese(c, 290, 204, 44 * kc)
        if kc > 0.6:
            K.text(c, 372, 168, "?", 50, (226, 70, 80), stroke=3, stroke_fill=(255, 255, 255))
    # teaching moments
    kg = tl.prog("s_cont", t, 0.4, 0.6) * (1 - tl.prog("s_cheese", t, 0.0, 0.2))
    K.label(c, 860, 92, "Continent = a big piece of land", 26, tip=(gcx + 64, gcy - 50), k=kg)
    ki = window(tl, t, ("s_cont", 0.55), ("s_many", 0.0))
    if ki > 0.01:
        K.inset(c, 1000, 190, 300, 210, ki, lambda ic: globe_inset(ic, t), bg=(20, 20, 50))
    k7 = window(tl, t, ("s_seven", 0.0), ("s_glow", 0.3))
    if k7 > 0.01:
        c.push(gcx + 170, gcy - 110, pop(k7))
        c.circle(0, 0, 54, (226, 70, 80), w=4)
        K.text(c, 0, 4, "7", 76, (255, 255, 255), stroke=4)
        c.pop()
        K.sparkles(c, gcx + 170, gcy - 110, 90, t, 8, k7, seed=12)
    K.sub_band(c, tl, t)
    # push in to the glowing globe and flash white into space
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
# where the cushion stops on each continent, and where its big name goes
PTS = {"Europe": (6, 46), "Africa": (22, -6), "Asia": (96, 38), "Australia": (132, -27),
       "Antarctica": (140, -72), "South America": (-60, -20), "North America": (-98, 40)}
NAMES = {"Europe": (26, 60), "Africa": (17, 13), "Asia": (92, 58), "Australia": (134, -45),
         "Antarctica": (80, -82), "South America": (-56, -2), "North America": (-104, 58)}
HL = {"Europe": ["europe"], "Africa": ["africa"], "Asia": ["asia"], "Australia": ["australia"],
      "Antarctica": ["antarctica"], "South America": ["south america"],
      "North America": ["north america", "greenland"]}
SWEEP = ["North America", "South America", "Europe", "Africa", "Asia", "Australia", "Antarctica"]
SONG_A = ["Africa", "Antarctica", "Asia", "Australia"]

V_WORLD = (0, 0, 1.0)
VIEWS = {"Europe": (38, 48, 2.6), "Africa": (52, 2, 2.0), "Asia": (95, 30, 1.35), "Australia": (162, -24, 2.4),
         "Antarctica": (140, -62, 2.0), "South America": (-30, -16, 2.2), "North America": (-62, 40, 1.8)}

# (event, waypoints, from view, to view, camera zoom dip, facing)
LEGS = [
    ("u_eu", [HOME, PTS["Europe"]], V_WORLD, VIEWS["Europe"], 0.0, 1),
    ("u_af", [PTS["Europe"], (14, 32), (18, 14), PTS["Africa"]], VIEWS["Europe"], VIEWS["Africa"], 0.2, 1),
    ("u_as", [PTS["Africa"], (44, 18), (70, 32), PTS["Asia"]], VIEWS["Africa"], VIEWS["Asia"], 0.2, 1),
    ("u_au", [PTS["Asia"], (108, 16), (122, -6), PTS["Australia"]], VIEWS["Asia"], VIEWS["Australia"], 0.2, 1),
    ("u_an", [PTS["Australia"], (138, -46), PTS["Antarctica"]], VIEWS["Australia"], VIEWS["Antarctica"], 0.1, 1),
    ("v_sa", [PTS["Antarctica"], (90, -76), (20, -77), (-45, -72), (-62, -58), (-66, -36), PTS["South America"]],
     VIEWS["Antarctica"], VIEWS["South America"], 0.5, -1),
    ("v_na", [PTS["South America"], (-76, 6), (-92, 22), PTS["North America"]], VIEWS["South America"],
     VIEWS["North America"], 0.2, -1),
    ("v_all", [PTS["North America"], (-62, 50), (-28, 53), HOME], VIEWS["North America"], V_WORLD, 0.0, 1),
]
ROUTE = [HOME] + [p for leg in LEGS for p in leg[1][1:]]


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40
    end = -14 * (tl.t("m_narr", 1) - t0) + 40
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_narr", t, 0.2, 1.0)))


def albert_fly(c, tl, t, x, y, s, face=1, flap=0.25, **kw):
    P.albatross(c, x, y, s, face, t, tl.mouth("albert", t), flap=flap, **kw)


def chips(c, tl, t):
    """The song banner at the top: 4 A's + 2 Americas + Europe = 7."""
    T = tl.t
    if t < T("m_as") or t >= T("m_go", 0.3):
        return
    fade = 1 - tl.prog("m_go", t, 0.0, 0.3)
    if t < T("m_sum"):
        parts = [("4 A's", ("m_as", 0.1), (236, 90, 90)), ("+ 2 Americas", ("m_ams", 0.1), (255, 150, 60)),
                 ("+ Europe", ("m_eu", 0.15), (150, 110, 220)), ("= 7", ("m_eu", 0.7), (70, 170, 90))]
    else:
        parts = [("4", ("m_sum", 0.25), (236, 90, 90)), ("+ 2", ("m_sum", 0.42), (255, 150, 60)),
                 ("+ 1", ("m_sum", 0.58), (150, 110, 220)), ("= 7 continents!", ("m_sum", 0.8), (70, 170, 90))]
    size = 34
    gap = 22
    widths = [K.text_w(p[0], size) + 36 for p in parts]
    total = sum(widths) + gap * (len(parts) - 1)
    x = 640 - total / 2
    for (txt, (ev, fr), col), w_ in zip(parts, widths):
        k = clamp((t - T(ev, fr)) / 0.3) * fade
        if k > 0.01:
            c.push(x + w_ / 2, 58, pop(k))
            c.rect(-w_ / 2, -30, w_ / 2, 30, col, r=30, w=3)
            K.text(c, 0, 1, txt, size, (255, 255, 255), stroke=2)
            c.pop()
        x += w_ + gap


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        # ---- up in space: a colourful globe
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        gx, gy = lerp(760, 640, k), 360
        K.globe(c, gx, gy, r, lon=space_globe_lon(tl, t), lat=lerp(18, 0, ease(tl.prog("m_narr", t, 0.2, 1))),
                style=STYLE, glow=0.5)
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        mk = ease(tl.prog("m_narr", t, 0.3, 1.0))
        x = lerp(lerp(-200, 260, fk), 170, mk)
        y = lerp(lerp(820, 600, fk), 660, mk)
        K.crew(c, tl, t, x, y, lerp(1.0, 0.75, mk), 1, fly=1.0, eyes={"whiskers": "wide"},
               look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_colours"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        K.globe_to_map(c, tl.prog("m_flat", t, 0.05, 0.85), t, 230, style=STYLE, lon=0)
        K.crew(c, tl, t, 170, 660, 0.75, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    c, v = K.map_view(*V_WORLD, style=STYLE, t=t)
    # names pop in one by one, west to east, each with its number
    for i, name in enumerate(SWEEP):
        k = clamp((t - T("m_names", 0.04 + 0.13 * i)) / 0.25)
        big = 0
        if T("m_as") <= t < T("m_421"):
            if name in SONG_A and t >= T("m_as", 0.45 + 0.15 * SONG_A.index(name)) and t < T("m_ams"):
                big = 1
            if name in ("North America", "South America") and T("m_ams", 0.45) <= t < T("m_eu"):
                big = 1
            if name == "Europe" and T("m_eu", 0.15) <= t:
                big = 1
        lo, la = K.CONTINENT_LABELS[name]
        hk = 0.0
        if T("m_as") <= t < T("m_go"):
            if name in SONG_A:
                hk = clamp((t - T("m_as", 0.45 + 0.15 * SONG_A.index(name))) / 0.3)
            elif "America" in name:
                hk = clamp((t - T("m_ams", 0.45 if name.startswith("North") else 0.8)) / 0.3)
            else:
                hk = clamp((t - T("m_eu", 0.15)) / 0.3)
            hk *= 1 - tl.prog("m_go", t, 0.0, 0.3)
        for h in HL[name]:
            P_hl(c, v, h, hk, t)
        size = 22 + 10 * big
        K.map_label(c, v, lo, la, name, size, (255, 255, 255) if not big else (255, 244, 150), k)
        if k > 0.01 and t < T("m_as"):
            x, y = v.xy(lo, la)
            bx = x - K.text_w(name, 22) / 2 - 20
            c.push(bx, y, pop(k))
            c.circle(0, 0, 15, (226, 70, 80), w=2.5)
            K.text(c, 0, 1, str(i + 1), 20, (255, 255, 255))
            c.pop()
    chips(c, tl, t)
    # the route preview and the friends shrinking onto home
    pk = tl.prog("m_path", t, 0.0, 0.4)
    if t >= T("m_path"):
        u = ease(tl.prog("m_path", t, 0.3, 0.95))
        if u > 0.001:
            K.map_path(c, v, ROUTE, u, col=(255, 255, 255), w=3, dash=8, gap=9, head=u < 0.99)
        hx, hy = v.xy(*HOME)
        K.you_are_here(c, hx, hy, t, tl.prog("m_path", t, 0.3, 0.5), "Start: home!", 22, side=-1)
    # Albert
    bk = ease_out(tl.prog("m_bird", t, 0.0, 0.8))
    if bk > 0:
        ax = lerp(1450, 930, bk) + 8 * math.sin(t * 1.3)
        ay = lerp(140, 530, bk) + 10 * math.sin(t * 2.0)
        flap = 0.9 if bk < 1 else 0.25
        if T("m_wings") <= t < T("m_how"):
            flap = 0.0
        s = 0.85
        if pk > 0:
            hx, hy = v.xy(*HOME)
            e = ease(pk)
            ax, ay, s = lerp(ax, hx + 26, e), lerp(ay, hy - 22, e), lerp(0.85, 0.12, e)
        if t < T("m_path", 0.4) or True:
            eyes = "happy" if T("m_421", 0.7) <= t < T("m_sum") else "open"
            albert_fly(c, tl, t, ax, ay, s, -1, flap=flap, eyes=eyes)
        kw = window(tl, t, ("m_wings", 0.05), ("m_how", 0.0))
        if kw > 0.01:
            K.label(c, 790, 230, "Longest wings of any bird!", 28, tip=(ax - 40, ay - 130), k=kw)
    # the friends on their cushion in front of the map
    sk = ease(pk)
    hx, hy = v.xy(*HOME)
    x, y, s = lerp(170, hx - 6, sk), lerp(660, hy + 4, sk), lerp(0.75, 0.13, sk)
    eyes = {}
    extra = None
    if T("m_sum") <= t < T("m_sum2", 1):
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
        extra = {"luna": {"mouth": laughing(t)}}
    if T("m_421") <= t < T("m_sum"):
        eyes = {"whiskers": "happy"}
    K.crew(c, tl, t, x, y, s, 1, fly=1.0, eyes=eyes, extra=extra,
           look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    # Whiskers' sum
    kb = window(tl, t, ("m_421", 0.2), ("m_sum", 0.15))
    if kb > 0.01:
        K.bubble(c, 330, 420, 120, 66, kb, tail=(150, 570))
        c.push(330, 420, kb)
        K.text(c, 0, 0, "421 ?!", 52, (226, 70, 80), stroke=3, stroke_fill=(255, 255, 255))
        c.pop()
    return c


def P_hl(c, v, name, k, t, col=(255, 255, 230)):
    """Same as K.map_highlight, but with the source box clamped to the mask (the kit version
    crashes with 'box offset can't be negative' when the map edge sits a hair inside the screen)."""
    if k <= 0.01:
        return
    from PIL import Image
    mask = K._continent_mask(K.CONTINENT_IDS[name])
    x0, y0, x1, y1 = v.rect()
    sx0, sy0 = max(0, int(math.ceil(x0 * SS))), max(0, int(math.ceil(y0 * SS)))
    sx1, sy1 = min(W * SS, int(x1 * SS)), min(H * SS, int(y1 * SS))
    if sx1 - sx0 < 2 or sy1 - sy0 < 2:
        return
    mx0, my0 = v.cx + (sx0 / SS - W / 2) / v.z, v.cy + (sy0 / SS - H / 2) / v.z
    mx1, my1 = v.cx + (sx1 / SS - W / 2) / v.z, v.cy + (sy1 / SS - H / 2) / v.z
    mw, mh = mask.size
    box = (clamp(mx0 * SS, 0, mw), clamp(my0 * SS, 0, mh), clamp(mx1 * SS, 0, mw), clamp(my1 * SS, 0, mh))
    piece = mask.resize((sx1 - sx0, sy1 - sy0), Image.BILINEAR, box=box)
    a = clamp(k) * (0.45 + 0.15 * math.sin(t * 5))
    piece = piece.point(lambda q: int(q * a))
    c.img.paste(col, (sx0, sy0, sx1, sy1), piece)


# ======================================================================== tour

def leg_state(tl, t):
    """Camera view, current leg index and its progress u at time t."""
    T = tl.t
    cur, u = None, 0.0
    for i, leg in enumerate(LEGS):
        if leg[0] in tl.by_id and t >= T(leg[0]):
            cur = i
    if cur is None:
        return V_WORLD, -1, 1.0
    ev, pts, v0, v1, dip, face = LEGS[cur]
    u = ease(tl.prog(ev, t, 0.05, 0.92))
    lon, lat, z = K.lerp_view(v0, v1, u)
    z *= 1 - dip * math.sin(math.pi * u)
    return (lon, lat, z), cur, u


def crew_icon(c, tl, t, v, x, y, face, eyes=None, flap=0.25, extra=None):
    s = 0.19 * v.z ** 0.7
    K.crew(c, tl, t, x, y + 4, s, face, fly=1, eyes=eyes, extra=extra)
    sa = 0.22 * v.z ** 0.7
    albert_fly(c, tl, t, x + face * 105 * s, y - 120 * s + 6 * math.sin(t * 2), sa, face, flap=flap)


def draw_route(c, tl, t, v, cur, u):
    K.map_path(c, v, ROUTE, 1.0, col=(255, 255, 255), w=2, dash=6, gap=10, head=False)
    for i, leg in enumerate(LEGS):
        if i < cur:
            K.map_path(c, v, leg[1], 1.0, head=False)
        elif i == cur and u > 0.001:
            K.map_path(c, v, leg[1], u, head=u < 0.99)


def stop_names(c, tl, t, v, upto, cur_name, k_big):
    """Names of the continents visited so far (small) and the current one (big)."""
    for name in upto:
        lo, la = NAMES[name]
        if name == cur_name:
            K.map_label(c, v, lo, la, name, 44, (255, 255, 255), k_big)
        else:
            K.map_label(c, v, lo, la, name, 24, (255, 255, 255), 1.0)


def caption(ic, w, h, s, col=(48, 40, 60)):
    ic.rect(w / 2 - K.text_w(s, 30) / 2 - 20, h - 52, w / 2 + K.text_w(s, 30) / 2 + 20, h - 12,
            (255, 255, 255), r=20, w=3)
    K.text(ic, w / 2, h - 32, s, 30, col)


def bg_grad(ic, top, bot):
    w, h = ic.img.size
    ic.img.paste(D.gradient(w, h, [(0, top), (1, bot)]), (0, 0))


def europe_inset(ic, t, kc):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (150, 200, 245), (226, 240, 255))
    D.cloud(ic, 90, 60, 0.5)
    ic.rect(0, 250, w, h, (130, 196, 110), ol=None)
    P.eiffel(ic, 120, 256, 210, t=t)
    P.cat_crowd(ic, 300, 262, 1.0 + 0.0 * kc, t)
    if kc > 0.01:
        for i in range(3):
            cx = 300 + (i - 1) * 70 + 10
            c_y = 262 - 100 - 14 - 22 * (1 - pop(kc))
            ic.poly([(cx - 16, c_y), (cx - 18, c_y - 22), (cx - 8, c_y - 12), (cx, c_y - 26), (cx + 8, c_y - 12),
                     (cx + 18, c_y - 22), (cx + 16, c_y)], (255, 210, 70), w=2)
    caption(ic, w, h, "Europe", (120, 80, 200))


def africa_inset(ic, t, kp, roar):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (255, 190, 110), (255, 236, 170))
    ic.circle(w - 70, 70, 34, (255, 246, 200), ol=None)
    ic.rect(0, 240, w, h, (232, 196, 110), ol=None)
    if kp > 0.01:
        P.pyramids(ic, w - 120, 244, 0.55 * pop(kp))
    # acacia tree
    ic.line([(60, 250), (66, 170)], (120, 80, 50), 6)
    ic.ellipse(66, 166, 54, 16, (110, 160, 70))
    P.elephant(ic, 300, 262, 0.55, t, face=-1)
    P.lion(ic, 120, 272, 0.62, t, roar)
    caption(ic, w, h, "Africa", (200, 130, 20))


def bars_inset(ic, t, k):
    """Bar chart of continent sizes: Asia is the biggest."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (255, 255, 255), (238, 244, 252))
    if k > 0.8:
        K.text(ic, w / 2, 30, "Asia is the biggest!", 28, (210, 70, 90), stroke=1, stroke_fill=(255, 255, 255))
    else:
        K.text(ic, w / 2, 30, "How big is each continent?", 24, (48, 40, 60))
    n = len(P.SIZES)
    x0, base, bw = 34, h - 64, (w - 68) / n
    for i, (name, a) in enumerate(P.SIZES):
        kk = clamp(k * 1.6 - i * 0.1)
        hh = (base - 70) * a / P.SIZES[0][1] * ease_out(kk)
        col = P.CCOL[name] if name != "Antarctica" else (200, 214, 232)
        bx = x0 + i * bw
        if hh > 1:
            ic.rect(bx + 4, base - hh, bx + bw - 4, base, col, r=4, w=2)
        short = {"North America": "N.Am.", "South America": "S.Am.", "Antarctica": "Ant.",
                 "Australia": "Aus.", "Europe": "Eur.", "Africa": "Afr."}.get(name, name)
        K.text(ic, bx + bw / 2, base + 16, short, 16, (48, 40, 60))
    ic.line([(x0, base), (w - x0, base)], OUT, 3)
    if k > 0.6:
        K.star(ic, x0 + bw / 2, base - (base - 70) - 16, 14 + 2 * math.sin(t * 6), (255, 210, 60), ol=OUT)


def asia_inset(ic, t, kw):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (176, 222, 250), (230, 246, 255))
    for mx, mh in ((60, 90), (180, 70), (330, 100)):
        ic.poly([(mx - 90, 200), (mx, 200 - mh), (mx + 90, 200)], (150, 176, 200), ol=None)
    ic.rect(0, 196, w, h, (120, 186, 100), ol=None)
    if kw > 0.01:
        P.great_wall(ic, 150, 200, 0.62 * pop(kw), 380)
    P.panda(ic, 96, 252, 0.62, t, chew=1)
    caption(ic, w, h, "Asia", (210, 70, 90))


def australia_inset(ic, t, ksnack):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (130, 196, 245), (240, 220, 180))
    ic.ellipse(330, 214, 120, 30, (196, 110, 70), ol=None)      # a big red rock far away
    ic.rect(0, 226, w, h, (226, 150, 90), ol=None)
    hopk = abs(math.sin(t * 3.2))
    P.kangaroo(ic, 190, 250, 0.82, t, hop=26 * hopk)
    if ksnack > 0.01:
        for i in range(3):
            fx = 226 + 28 * i
            fy = 250 - 26 * hopk - 90 - 40 * pop(clamp(ksnack * 2 - i * 0.3)) - 10 * i
            P.fish_snack(ic, fx, fy, 0.75 * clamp(ksnack * 2 - i * 0.3), [(120, 180, 230), (250, 170, 80),
                                                                          (150, 210, 120)][i])
    caption(ic, w, h, "Australia", (40, 150, 140))


def tour(tl, t):
    T = tl.t
    if t >= T("u_an2"):
        return dive(tl, t)
    view, cur, u = leg_state(tl, t)
    c, v = K.map_view(*view, style=STYLE, t=t)
    stops = ["Europe", "Africa", "Asia", "Australia", "Antarctica"]
    name = stops[cur]
    arrived = tl.prog(LEGS[cur][0], t, 0.85, 1.0)
    # glow over the continent we are visiting
    pulse = 1.0
    if name == "Asia" and T("u_as1", 0.5) <= t < T("u_as2"):
        pulse = 1.0 + 0.6 * abs(math.sin(t * 4))
    for h in HL[name]:
        P_hl(c, v, h, min(1.0, arrived * pulse), t)
    draw_route(c, tl, t, v, cur, u)
    stop_names(c, tl, t, v, stops[:cur + 1], name, arrived)
    x, y, ang = K.path_point(v, LEGS[cur][1], u)
    eyes = None
    if T("u_eu2") <= t < T("u_eu2", 1) or T("u_au2") <= t < T("u_au3", 1):
        eyes = {"whiskers": "happy"}
    crew_icon(c, tl, t, v, x, y, LEGS[cur][5], eyes=eyes, flap=0.6 if u < 0.95 else 0.2)
    if name == "Asia":
        kb = window(tl, t, ("u_as1", 0.35), ("u_as2", 0.05))
        K.label(c, 640, 70, "The BIGGEST continent!", 34, k=kb, col=(200, 50, 70))
        kbar = window(tl, t, ("u_as1", 0.6), ("u_as2", 0.1))
        if kbar > 0.01:
            kk = tl.prog("u_big", t, 0.0, 0.7)
            K.inset(c, 260, 420, 460, 280, kbar, lambda ic: bars_inset(ic, t, kk))
        ka = window(tl, t, ("u_as2", 0.15), ("u_au", 0.12))
        if ka > 0.01:
            kw = tl.prog("u_as3", t, 0.45, 0.75)
            K.inset(c, 250, 420, 420, 280, ka, lambda ic: asia_inset(ic, t, kw))
    kins = {
        "Europe": window(tl, t, ("u_eu1", 0.2), ("u_af", 0.12)),
        "Africa": window(tl, t, ("u_af1", 0.1), ("u_as", 0.12)),
        "Australia": window(tl, t, ("u_au1", 0.1), ("u_an", 0.12)),
    }.get(name, 0.0)
    if kins > 0.01:
        if name == "Europe":
            kc = tl.prog("u_eu2", t, 0.2, 0.5)
            fn = lambda ic: europe_inset(ic, t, kc)                     # noqa: E731
        elif name == "Africa":
            kp = tl.prog("u_af1", t, 0.6, 0.8)
            roar = clamp(math.sin(math.pi * tl.prog("u_af1", t, 0.22, 0.4)))
            fn = lambda ic: africa_inset(ic, t, kp, roar)              # noqa: E731
        else:
            ks = tl.prog("u_au2", t, 0.3, 0.7)
            fn = lambda ic: australia_inset(ic, t, ks)                  # noqa: E731
        K.inset(c, 960, 280, 440, 320, kins, fn)
    if name == "Antarctica":
        ka = tl.prog("u_an1", t, 0.5, 0.8)
        lo, la = PTS["Antarctica"]
        x2, y2 = v.xy(lo, la)
        K.label(c, x2 + 120, y2 - 200, "The bottom of the world", 28, tip=(x2 + 20, y2 - 20), k=ka)
    K.sub_band(c, tl, t)
    return c


# ---------------------------------------------------------------- the dive

def sky_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (96, 150, 220)), (0.7, (190, 220, 245)), (1, (236, 246, 255))]))
        return c.img
    return cached("sky", make)


def speed_clouds(c, t, speed=900, seed=5, y0=0, y1=H, n=7, s=1.0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        y = rng.uniform(y0, y1)
        sc = rng.uniform(0.5, 1.1) * s
        x = W + 200 - ((rng.uniform(0, W + 400) + t * speed * sc) % (W + 400))
        D.cloud(c, x, y, sc)


def dive(tl, t):
    T = tl.t
    c = Canvas(sky_bg().copy())
    speed_clouds(c, t, 700)
    land = tl.prog("u_land", t, 0.0, 1.0)
    e = ease(land)
    bob = 6 * math.sin(t * 2.6)
    cx, cy, s = lerp(560, 760, e), lerp(470, 900, e ** 1.5) + bob, lerp(1.15, 1.6, e)
    sun_k = tl.prog("u_an2", t, 0.6, 0.85)
    eyes = {"whiskers": "happy"} if T("u_an2") <= t < T("u_an2", 0.6) else None
    look = {"luna": (1, -0.4), "pip": (-1, -0.4)}
    if land > 0:
        eyes = {"whiskers": "wide", "luna": "wide", "pip": "wide"}
    K.crew(c, tl, t, cx, cy, s, 1, fly=1.0, eyes=eyes, look=look)
    # Whiskers' sunglasses (same spot crew() puts him)
    wx = cx - 52 * s
    wy = cy + 6 * math.sin(t * 2.6) - 40 * s
    P.sunglasses(c, wx, wy - bob + 6 * math.sin(t * 2.6) - 6 * math.sin(t * 2.6), 0.62 * s, 1, "sit", k=sun_k)
    # Albert gliding alongside
    ax, ay = lerp(980, 1100, e), lerp(250, 760, e ** 1.3) + 8 * math.sin(t * 1.7)
    albert_fly(c, tl, t, ax, ay, 0.75, 1, flap=0.15)
    # daydream: a sunny beach
    kb = window(tl, t, ("u_an2", 0.3), ("u_land", 0.15))
    if kb > 0.01:
        K.bubble(c, 300, 170, 150, 90, kb, tail=(wx + 10, wy - 120 * s * 0.62))
        P.beach(c, 300, 180, 1.05 * kb, t)
    if land > 0:
        for i in range(14):
            rng = np.random.default_rng(i)
            x = rng.uniform(0, W)
            y = (rng.uniform(0, H) - t * 1800) % H
            c.line([(x, y), (x, y + 120)], (255, 255, 255), 3, cap=False)
    K.sub_band(c, tl, t)
    K.flash(c, tl.prog("u_land", t, 0.7, 1.0), (255, 255, 255))
    return c


# ========================================================================= ice

GROUND = 520
ICE_CUSH = (250, GROUND + 70)
W_SPOT = (610, GROUND + 92)
ALBERT_SPOT = (870, GROUND + 70)


def ice_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (130, 186, 236)), (0.5, (214, 234, 250)), (0.51, (240, 248, 255)),
                                               (1, (206, 228, 246))]))
        c.glow(1040, 110, 160, 110, (255, 252, 230), (190, 220, 248), steps=8)
        c.circle(1040, 110, 34, (255, 248, 210), ol=None)
        # far ice mountains
        for mx, mh, mw in ((120, 120, 180), (360, 170, 220), (640, 110, 160), (860, 190, 240), (1160, 140, 200)):
            c.poly([(mx - mw, 362), (mx, 362 - mh), (mx + mw, 362)], (232, 242, 252), ol=(150, 180, 210), w=2)
            c.poly([(mx, 362 - mh), (mx + mw, 362), (mx + mw * 0.2, 362)], (200, 222, 244), ol=None)
        # ice cliffs + flat ice sheet
        c.rect(0, 360, W, H, (240, 248, 255), ol=None)
        for i in range(9):
            x = i * 160 - 40
            c.poly([(x, 362), (x + 40, 330), (x + 110, 336), (x + 160, 362)], (226, 240, 252),
                   ol=(160, 190, 220), w=2)
        c.line([(0, 362), (W, 362)], (160, 190, 220), 2)
        rng = np.random.default_rng(6)
        for _ in range(14):
            x, y = rng.uniform(0, W), rng.uniform(400, 700)
            c.ellipse(x, y, rng.uniform(40, 120), rng.uniform(5, 10), (220, 236, 250), ol=None)
        for _ in range(6):
            x, y = rng.uniform(80, W - 80), rng.uniform(420, 690)
            c.line([(x, y), (x + 30, y + 6), (x + 50, y + 2)], (180, 206, 232), 2)
        return c.img
    return cached("ice", make)


def snowfall(c, t, n=60):
    rng = np.random.default_rng(9)
    for i in range(n):
        x0 = rng.uniform(0, W)
        sp = rng.uniform(40, 90)
        y = (rng.uniform(0, H) + t * sp) % H
        x = x0 + 14 * math.sin(t * 1.3 + i) - t * 20 % W
        c.circle(x % W, y, rng.uniform(2, 4.5), (255, 255, 255), ol=None)


def snow_mound(c, x, y, w):
    c.ellipse(x, y, w, 26, (250, 252, 255), ol=(170, 200, 228), w=2.5)
    c.ellipse(x - w * 0.3, y - 10, w * 0.4, 16, (255, 255, 255), ol=None)


def poof(c, x, y, k):
    if 0 < k < 1:
        rng = np.random.default_rng(3)
        for i in range(14):
            a = rng.uniform(math.pi, math.tau)
            d = 30 + 120 * ease_out(k) * rng.uniform(0.5, 1.0)
            c.circle(x + math.cos(a) * d, y + math.sin(a) * d * 0.7, (14 + rng.uniform(0, 10)) * (1 - k),
                     (255, 255, 255), ol=(190, 214, 236), w=2)


def frozen_whiskers(c, tl, t, x, y, s, frost, sun, face=1, pose="sit", **kw):
    pal = P.frozen(D.WHISKERS, frost)
    mouth = kw.pop("mouth", tl.mouth("whiskers", t))
    D.cat(c, x, y, pal, s, face, pose, t=t, mouth=mouth, seed=0.0, **kw)
    if pose == "sit":
        P.sunglasses(c, x, y, s, face, pose, k=sun, frost=frost)
        P.icicles(c, x, y, s, face, pose, k=frost, t=t)


def ice(tl, t):
    T = tl.t
    c = Canvas(ice_bg().copy())
    snowfall(c, t)
    # ---- the cushion floats down with everybody; Whiskers jumps into the snow
    dk = ease_out(tl.prog("i_open", t, 0.0, 0.42))
    cx, cy = ICE_CUSH[0], lerp(-80, ICE_CUSH[1], dk)
    jump = tl.prog("i_open", t, 0.42, 0.62)
    off = tl.prog("i_off", t, 0.0, 1.0)
    frost = ease(tl.prog("i_freeze", t, 0.05, 0.7)) * (1 - tl.prog("i_off", t, 0.0, 0.25))
    laugh = T("i_laugh") <= t < T("i_go")
    chatter = 0.0
    if T("i_freeze", 0.6) <= t < T("i_cold") or tl.talking("whiskers", t) and t < T("i_cold"):
        chatter = 3 * math.sin(t * 60)
    cush_s = 1.4
    top = cy - 40 * cush_s
    # Whiskers back onto the cushion at the end
    back = tl.prog("i_off", t, 0.0, 0.3)
    lift = ease(tl.prog("i_off", t, 0.3, 1.0))
    cy_lift = cy - 760 * lift
    eyes = {}
    look = {"luna": (1, 0), "pip": (1, 0)}
    extra = {}
    if laugh:
        eyes = {"luna": "happy", "pip": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t + 0.2)}}
    if T("i_pip") <= t < T("i_pip", 1):
        eyes["pip"] = "happy"
    # crew minus Whiskers (he gets his own palette)
    # crew() without Whiskers (he gets his own frosty palette below)
    K.crew(c, tl, t, cx, cy_lift, cush_s, 1, fly=clamp(1 - dk + lift), who=("luna", "pip"), eyes=eyes, look=look,
           extra=extra)
    sun = 1.0
    wpos_cush = (cx - 52 * cush_s, top - 0 + (cy_lift - cy))
    if jump <= 0 and dk < 1:
        bob = math.sin(t * 2.6) * 6 * (1 - dk)
        frozen_whiskers(c, tl, t, wpos_cush[0], wpos_cush[1] + bob, 0.62 * cush_s, 0, sun, 1, "sit",
                        eyes="happy")
    elif jump <= 0:
        frozen_whiskers(c, tl, t, wpos_cush[0], wpos_cush[1], 0.62 * cush_s, 0, sun, 1, "sit", eyes="happy")
    elif jump < 1:
        x, y = hop(wpos_cush, (W_SPOT[0], W_SPOT[1] - 20), jump, 160)
        frozen_whiskers(c, tl, t, x, y, lerp(0.62 * cush_s, 1.15, jump), 0, sun, 1, "leap", eyes="happy")
    elif back <= 0:
        sink = ease_out(clamp((t - T("i_open", 0.62)) / 0.3))
        wy = W_SPOT[1] - 20 + 30 * sink
        e_ = "wide" if frost < 0.5 else "open"
        if laugh or T("i_purpose") <= t < T("i_purpose", 1):
            e_ = "closed" if T("i_purpose") <= t else "open"
        frozen_whiskers(c, tl, t, W_SPOT[0] + chatter, wy, 1.15, frost, sun, 1, "sit", eyes=e_, look=(0.6, 0))
        snow_mound(c, W_SPOT[0] + 10, W_SPOT[1] + 6, 110)
        if frost > 0.3:
            K.sparkles(c, W_SPOT[0] + 10, wy - 80, 80, t, 6, frost, seed=15, col=(220, 240, 255))
    else:
        if back < 1:
            x, y = hop((W_SPOT[0], W_SPOT[1] + 10), wpos_cush, back, 150)
            frozen_whiskers(c, tl, t, x, y, lerp(1.15, 0.62 * cush_s, back), frost, sun, -1, "leap")
            poof(c, W_SPOT[0], W_SPOT[1], back)
            snow_mound(c, W_SPOT[0] + 10, W_SPOT[1] + 6, 110)
        else:
            frozen_whiskers(c, tl, t, wpos_cush[0], wpos_cush[1] + math.sin(t * 2.6) * 6, 0.62 * cush_s, frost,
                            sun, 1, "sit", eyes="wide")
    poof(c, W_SPOT[0], W_SPOT[1], tl.prog("i_open", t, 0.6, 0.95))
    # ---- Albert lands, then waves
    ak = ease_out(tl.prog("i_open", t, 0.55, 1.0))
    if t < T("i_off", 0.2):
        if ak < 1:
            ax, ay = lerp(1400, ALBERT_SPOT[0], ak), lerp(80, ALBERT_SPOT[1] - 80, ak)
            albert_fly(c, tl, t, ax, ay, 0.9, -1, flap=0.8)
        else:
            wave = tl.prog("i_go", t, 0.0, 0.2) if t >= T("i_go") else 0.0
            a_eyes = "happy" if laugh or T("i_cold") <= t < T("i_cold", 0.15) else "open"
            P.albatross(c, ALBERT_SPOT[0], ALBERT_SPOT[1], 1.1, -1, t, tl.mouth("albert", t), a_eyes, stand=True,
                        wave=wave)
    else:
        k2 = ease(tl.prog("i_off", t, 0.2, 1.0))
        albert_fly(c, tl, t, lerp(ALBERT_SPOT[0], 700, k2), lerp(ALBERT_SPOT[1] - 80, -200, k2), 0.9, -1, flap=1.0)
    # ---- penguins waddle in
    pk = tl.prog("i_penguins", t, 0.0, 0.9)
    if t >= T("i_penguins"):
        for i, (px, sc) in enumerate(((1010, 0.85), (1100, 1.0), (1190, 0.9), (1240, 0.6))):
            x = lerp(px + 420, px, ease_out(clamp(pk * 1.3 - i * 0.12)))
            moving = 0 < pk * 1.3 - i * 0.12 < 1
            wad = t * 9 if moving else 0
            hopy = abs(math.sin(t * 9)) * 6 if moving else 0
            pe = "happy" if laugh or T("i_pip") <= t < T("i_pip", 1) else "open"
            P.penguin(c, x, GROUND + 70 + i % 2 * 26 - hopy, sc, -1, t, wad, pe, flap=1.0 if laugh else 0.0,
                      seed=i * 0.9)
    # ---- teaching moments
    kt = window(tl, t, ("i_cold", 0.1), ("i_people", 0.05))
    if kt > 0.01:
        c.push(1130, 330, pop(kt))
        P.thermometer(c, 0, 0, 1.0, lerp(0.75, 0.04, ease(tl.prog("i_cold", t, 0.2, 0.7))), t)
        P.snowflake(c, 56, -150, 26)
        c.pop()
        K.label(c, 760, 100, "The coldest place on Earth!", 32, k=kt, col=(40, 100, 200))
    kice = window(tl, t, ("i_cold", 0.62), ("i_people", 0.05))
    K.label(c, 420, 430, "Thick ice everywhere!", 28, tip=(420, 520), k=kice)
    ks = window(tl, t, ("i_people", 0.15), ("i_penguins", 0.2))
    if ks > 0.01:
        def st(ic):
            w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
            bg_grad(ic, (170, 210, 245), (240, 248, 255))
            ic.rect(0, 160, w, h, (246, 250, 255), ol=None)
            P.station(ic, w / 2, 176, 1.0)
            caption(ic, w, h, "Scientists only visit", (40, 100, 200))
        K.inset(c, 1000, 200, 380, 260, ks, st)
    K.sub_band(c, tl, t)
    K.flash(c, 1 - tl.prog("i_open", t, 0.0, 0.25), (255, 255, 255))
    return c


# ======================================================================= tour2

def sa_inset(ic, t, kl):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (150, 210, 240), (220, 244, 230))
    ic.poly([(200, 180), (300, 60), (360, 110), (420, 50), (w + 40, 180)], (160, 150, 170), ol=(110, 100, 120), w=2)
    ic.poly([(300, 60), (322, 86), (284, 82)], (255, 255, 255), ol=None)
    ic.poly([(420, 50), (440, 76), (402, 74)], (255, 255, 255), ol=None)
    ic.rect(0, 180, w, h, (90, 160, 80), ol=None)
    ic.poly([(0, 230), (120, 214), (220, 240), (0, 262)], (90, 160, 220), ol=None)       # the river
    for i, (x, s) in enumerate(((30, 0.6), (90, 0.75), (160, 0.55), (60, 0.5), (200, 0.7))):
        P.jungle_tree(ic, x, 250 + (i % 2) * 14, s, col=[(60, 150, 70), (40, 130, 60), (80, 170, 80)][i % 3])
    ic.circle(130 + 4 * math.sin(t * 3), 140, 8, (255, 80, 60), w=2)       # a bright bird
    if kl > 0.01:
        P.llama(ic, 350, 216, 0.5 * pop(kl), t, face=-1)
    caption(ic, w, h, "South America", (60, 140, 50))


def na_inset(ic, t, kb):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    bg_grad(ic, (120, 180, 240), (230, 244, 255))
    ic.poly([(-20, 200), (110, 90), (220, 200)], (150, 160, 180), ol=(100, 110, 130), w=2)
    ic.poly([(110, 90), (138, 120), (90, 116)], (255, 255, 255), ol=None)
    ic.rect(0, 196, w, h, (176, 196, 110), ol=None)
    P.eagle(ic, 250 + 20 * math.sin(t * 0.8), 86 + 6 * math.sin(t * 1.6), 0.55, t)
    if kb > 0.01:
        P.bison(ic, 140, 262, 0.75 * pop(kb), t, face=1)
    caption(ic, w, h, "North America", (210, 110, 30))


def tour2(tl, t):
    T = tl.t
    view, cur, u = leg_state(tl, t)
    c, v = K.map_view(*view, style=STYLE, t=t)
    order = ["Europe", "Africa", "Asia", "Australia", "Antarctica", "South America", "North America"]
    name = {5: "South America", 6: "North America"}.get(cur)
    if name:
        arrived = tl.prog(LEGS[cur][0], t, 0.85, 1.0)
        for h in HL[name]:
            P_hl(c, v, h, arrived, t)
        upto = order[:cur + 1]
    else:
        arrived = 1.0
        upto = order
        # all seven glow one after another with their numbers
        for i, nm in enumerate(SWEEP):
            k = clamp((t - T("v_all", 0.35 + 0.08 * i)) / 0.25)
            for h in HL[nm]:
                P_hl(c, v, h, k * (1 - tl.prog("v_bye2", t, 0.3, 0.9)), t)
    draw_route(c, tl, t, v, cur, u)
    if name:
        stop_names(c, tl, t, v, upto, name, arrived)
    else:
        for i, nm in enumerate(SWEEP):
            lo, la = K.CONTINENT_LABELS[nm]
            k = clamp((t - T("v_all", 0.35 + 0.08 * i)) / 0.25)
            K.map_label(c, v, lo, la, nm, 22, (255, 255, 255), 1.0)
            if k > 0.01:
                x, y = v.xy(lo, la)
                bx = x - K.text_w(nm, 22) / 2 - 20
                c.push(bx, y, pop(k))
                c.circle(0, 0, 15, (226, 70, 80), w=2.5)
                K.text(c, 0, 1, str(i + 1), 20, (255, 255, 255))
                c.pop()
    x, y, ang = K.path_point(v, LEGS[cur][1], u)
    face = LEGS[cur][5]
    if t < T("v_bye"):
        crew_icon(c, tl, t, v, x, y, face, flap=0.6 if u < 0.95 else 0.2)
    else:
        s = 0.19 * v.z ** 0.7
        K.crew(c, tl, t, x, y + 4, s, 1, fly=1)
        # Albert, big in front of the map, waves goodbye and glides away
        bk = ease_out(tl.prog("v_bye", t, 0.0, 0.3))
        gk = ease(tl.prog("v_bye2", t, 0.0, 1.0))
        ax = lerp(lerp(x + 20, 1000, bk), 1500, gk)
        ay = lerp(lerp(y - 20, 420, bk), 120, gk) + 8 * math.sin(t * 2)
        albert_fly(c, tl, t, ax, ay, lerp(0.15, 0.85, bk) * lerp(1, 0.6, gk), 1, flap=0.5 if gk > 0 else 0.3)
    if name == "South America":
        k = window(tl, t, ("v_sa1", 0.15), ("v_na", 0.12))
        if k > 0.01:
            kl = tl.prog("v_sa2", t, 0.1, 0.4)
            K.inset(c, 960, 280, 440, 320, k, lambda ic: sa_inset(ic, t, kl))
    elif name == "North America":
        k = window(tl, t, ("v_na1", 0.1), ("v_all", 0.12))
        if k > 0.01:
            kb = tl.prog("v_na1", t, 0.55, 0.8)
            K.inset(c, 960, 280, 440, 320, k, lambda ic: na_inset(ic, t, kb))
    else:
        kc = window(tl, t, ("v_all1", 0.3), ("v_bye2", 0.5))
        K.label(c, 640, 46, "7 continents!", 36, k=kc, col=(200, 50, 70))
    K.sub_band(c, tl, t)
    return c


# ==================================================================== remember

FACTS = ["The Earth's land is split into seven continents.",
         "Asia is the biggest continent.",
         "Antarctica is the coldest continent. It is covered in ice."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_seven, P.icon_biggest, P.icon_cold], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "How many continents are there? Five, or seven?", ["Five", "Seven"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_number(5, (90, 150, 230)), P.icon_number(7, (226, 90, 90))], number=1,
                        answer_text="Seven continents!")
    else:
        c = K.quiz_card(t, "Which continent is the coldest? Africa, or Antarctica?",
                        ["Africa", "Antarctica"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.icon_hot, P.icon_cold], number=2, answer_text="Antarctica! Brrr!")
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
    # Pip's "seven!" over the glowing globe
    k7 = window(tl, t, ("h_pip", 0.1), ("h_nap", 0.3))
    if k7 > 0.01:
        c.push(gcx + 170, gcy - 110, pop(k7))
        c.circle(0, 0, 54, (226, 70, 80), w=4)
        K.text(c, 0, 4, "7", 76, (255, 255, 255), stroke=4)
        c.pop()
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "The Five Oceans", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "tour": tour, "ice": ice, "tour2": tour2,
               "remember": remember, "quiz": quiz, "home": home}
