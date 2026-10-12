"""Scenes of Episode 4 "Mountains and Volcanoes". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py; Tashi, Iggy, the blanket,
the backdrops, the volcano and the diagrams come from props.py.
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e04_mountains_volcanoes import props as P

CONTINUOUS = ("map",)            # the sill flashes white straight into space
EXTRA_CUTS = ()


def hop(a, b, u, h=80):
    """Point on a jump arc from a to b."""
    u = ease(u)
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


def window(tl, t, a, b, fade=0.25):
    """1 between events/fractions a=(id, frac) and b=(id, frac), fading in and out."""
    return tl.prog(a[0], t, a[1], a[1] + fade) * (1 - tl.prog(b[0], t, b[1], b[1] + fade))


def shake(c, amt, t):
    """Camera shake: a slightly zoomed, jittered copy of the frame."""
    if amt <= 0.01:
        return c
    dx = math.sin(t * 53) * 6 * amt
    dy = math.cos(t * 47) * 5 * amt
    return K.zoom(c, 640 + dx, 360 + dy, 1 + 0.03 * amt)


# ======================================================================= title

def title(tl, t):
    c = K.title_card(tl, t, 0.0, 4, "Mountains and Volcanoes")
    kb = clamp((t - 1.6) / 0.6)
    if kb > 0.5:
        # a wider ribbon so the long topic fits
        K.ribbon(c, 640, 640, 760, 66, k=1.0)
        K.text(c, 640, 640, "Episode 4:  Mountains and Volcanoes", 36, (255, 255, 255), stroke=3)
    return c


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45            # cushion scale; cats on it are 0.62 * 1.45 = 0.9
CAT_S = 0.9
LUNA_X0 = 870
PIP_X0 = 548
BL = 266                 # blanket length
BL_L0, BL_R0 = 742, 1008
BL_L1, BL_R1 = 822, 962
BL_LM, BL_RM = 760, 990  # after the slow push (before the fold)


def sill_globe_lon(tl, t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def blanket_ends(tl, t):
    slow = ease(tl.prog("s_pieces", t, 0.1, 1.0))
    fold = ease(tl.prog("s_fold", t, 0.25, 0.75))
    xl = lerp(lerp(BL_L0, BL_LM, slow), BL_L1, fold)
    xr = lerp(lerp(BL_R0, BL_RM, slow), BL_R1, fold)
    return xl, xr


def mini_range(ic):
    """Close-up of the bumps on the globe: little mountains."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 205, 250)), (1, (220, 240, 255))]), (0, 0))
    for i, (x, ww, hh) in enumerate(((60, 70, 90), (150, 90, 130), (240, 70, 100))):
        P.peak(ic, x, h - 40, ww, hh, (140, 132, 150), 0.4, seed=40 + i)
    ic.rect(0, h - 44, w, h, (120, 176, 90), ol=OUT, w=3)
    K.text(ic, w / 2, h - 20, "Mountains!", 28, (255, 255, 255), stroke=3)


def sill(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("day").copy())
    spins = [(T("s_open", 0.15), 260), (T("s_hold", 0.3), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(tl, t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170

    xl, xr = blanket_ends(tl, t)
    pts, amp = P.blanket(c, xl, xr, SY, BL)

    # Luna: sits on the blanket, walks to its left end and pushes; Pip hops over to the right end
    walk_k = tl.prog("s_show", t, 0.55, 1.0) * 0.4 + tl.prog("s_push", t, 0.0, 0.6) * 0.6
    luna_push = (xl - 52, SY)
    luna_xy = (lerp(LUNA_X0, luna_push[0], ease(walk_k)), SY)
    pip_k = tl.prog("s_push", t, 0.1, 0.55)
    pip_push = (xr + 24, SY)
    pip_xy = hop((PIP_X0, SY), pip_push, pip_k, 230)
    pushing = T("s_push", 0.6) <= t < T("s_foldact", 0.4)

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    laugh = T("s_laugh") <= t < T("s_laugh", 1)
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if T("s_foldact") <= t < T("s_laugh", 1):
            w_eyes = "happy"
        if T("s_fold", 0.3) <= t < T("s_foldact"):
            w_eyes = "wide"
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.3))
        # Luna
        moving = 0.02 < walk_k < 0.98
        if walk_k <= 0.02:
            kat(c, tl, t, "luna", LUNA_X0, SY - 6, CAT_S, -1, "sit", look=(-1, -0.4),
                eyes="happy" if laugh else "open", **({"mouth": laughing(t)} if laugh else {}))
        else:
            ph = (t - T("s_show")) * 9 if moving or pushing else 0.0
            pose = "walk" if moving or pushing else "stand"
            face = -1 if walk_k < 0.5 and moving else 1
            kat(c, tl, t, "luna", luna_xy[0], SY, CAT_S, face, pose, walk=ph,
                eyes="happy" if laugh else "open", **({"mouth": laughing(t)} if laugh else {}))
        # Pip
        pface = 1 if pip_k <= 0 else -1
        kat(c, tl, t, "pip", pip_xy[0], pip_xy[1], 1.1, pface, walk=(t * 10 if pushing else 0.0),
            proud=tl.talking("pip", t) and pip_k <= 0, eyes="happy" if laugh else "open")
    else:
        lstart = (luna_push[0], SY)
        l2 = hop(lstart, cush_spots["luna"], hopk, 170)
        p2 = hop(pip_push, cush_spots["pip"], clamp(hopk * 1.15), 240)
        if hopk < 1:
            K.cushion(c, CUSH_X, SY, CREW_S, t)
            kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes="wide")
            kat(c, tl, t, "luna", l2[0], l2[1], CAT_S, -1, "leap" if 0.05 < hopk < 0.95 else "sit")
            kat(c, tl, t, "pip", p2[0], p2[1], 1.1, -1)
        else:
            e = ease(fly)
            x = lerp(CUSH_X, gcx, e)
            y = lerp(SY, gcy + 40, e) - 80 * math.sin(math.pi * e)
            s = CREW_S * lerp(1, 0.15, e ** 1.5)
            K.crew(c, tl, t, x, y, s, 1, fly=min(1, fly * 3), eyes={"whiskers": "wide"},
                   look={"luna": (1, -1), "pip": (1, -1)})

    # --- teaching moments
    km = window(tl, t, ("s_mount", 0.2), ("s_grow", 0.5))
    if km > 0.01:
        K.label(c, 905, 200, "Bumps = mountains", 26, tip=(gcx + 60, gcy - 50), k=km)
        K.inset(c, 920, 330, 300, 190, km, mini_range)
    # push arrows + labels while pushing
    if pushing and t < T("s_fold", 0.75):
        ak = tl.prog("s_pieces", t, 0.0, 0.2)
        K.arrow(c, xl - 150, SY - 150, xl - 40, SY - 150, (255, 236, 90), 9, ak)
        K.arrow(c, xr + 150, SY - 150, xr + 40, SY - 150, (255, 236, 90), 9, ak)
        K.text(c, xl - 96, SY - 186, "push", 28, (255, 255, 255), stroke=4) if ak > 0.5 else None
        K.text(c, xr + 96, SY - 186, "push", 28, (255, 255, 255), stroke=4) if ak > 0.5 else None
    kmt = window(tl, t, ("s_fold", 0.75), ("s_nap", 0.6))
    if kmt > 0.01:
        top = min(pts, key=lambda p: p[1])
        K.label(c, top[0] + 60, top[1] - 90, "A mountain!", 30, tip=(top[0], top[1] - 6), k=kmt)
    # the crust diagram: two giant pieces of land pushing together
    kc = window(tl, t, ("s_pieces", 0.05), ("s_nap", 0.3))
    if kc > 0.01:
        kk = tl.prog("s_pieces", t, 0.1, 1.0) * 0.5 + tl.prog("s_fold", t, 0.25, 0.8) * 0.5
        K.inset(c, 360, 170, 440, 270, kc, lambda ic: P.crust_inset(ic, t, kk))
    # "Nap Mountain" sign
    kn = window(tl, t, ("s_nap", 0.5), ("s_pip2", 0.3))
    if kn > 0.01:
        top = min(pts, key=lambda p: p[1])
        K.label(c, top[0] + 10, top[1] - 70, "Nap Mountain", 28, k=kn, bg=(255, 236, 150))
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
EVEREST = (86.9, 28.0)
GO_PATH = [HOME, (30, 46), (55, 40), (75, 33), EVEREST]
RANGES = [("Rocky Mountains", (-112, 44), (-112, 33)), ("Andes", (-69, -22), (-58, -32)),
          ("Alps", (9, 46.3), (24, 52)), ("Himalayas", EVEREST, (86, 40))]


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40
    end = -14 * (tl.t("m_flat") - t0) + 40
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_narr", t, 0.3, 1.0)))


def map_crew(c, tl, t, x, y, s, **kw):
    K.crew(c, tl, t, x, y, s, 1, fly=1.0, **kw)


def mountain_icons(c, v, t, ks, names_k=1.0, big=None):
    """Little snowy mountains on the map ranges (ks: pop-in per range)."""
    for i, (name, ll, lab) in enumerate(RANGES):
        k = ks[i]
        if k <= 0.01:
            continue
        x, y = v.xy(*ll)
        s = 0.55 * v.z ** 0.6 * pop(k)
        if big == i:
            s *= 1 + 0.15 * math.sin(t * 6) + 0.3
        for dx, hh in ((-22, 34), (0, 50), (22, 30)):
            P.peak(c, x + dx * s, y + 14 * s, 18 * s, hh * s, (150, 140, 156), 0.45, seed=60 + i + dx)
        if names_k > 0.01:
            K.map_label(c, v, lab[0], lab[1], name, 22 * min(1.6, v.z ** 0.5), k=k * names_k)


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        r = lerp(60, 230, k)
        gx, gy = lerp(760, 640, k), 360
        K.globe(c, gx, gy, r, lon=space_globe_lon(tl, t), lat=lerp(18, 0, ease(tl.prog("m_narr", t, 0.3, 1.0))),
                glow=0.5)
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        x = lerp(-200, 210, fk)
        y = lerp(820, 640, fk)
        map_crew(c, tl, t, x, y, 0.8, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
                 eyes={"whiskers": "wide"} if t < T("m_narr", 0.5) else None)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_all"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        if k >= 1:
            K.map_labels(c, K.MapView(0, 0, 1), "continents", tl.prog("m_flat", t, 0.85, 1.0))
        map_crew(c, tl, t, lerp(210, 170, k), lerp(640, 660, k), lerp(0.8, 0.75, k),
                 look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


def map_scene(tl, t):
    T = tl.t
    pk = tl.prog("m_path", t, 0.3, 1.0)
    cam = K.lerp_view((0, 0, 1.0), (EVEREST[0] - 6, EVEREST[1] + 2, 2.6), ease(pk))
    c, v = K.map_view(*cam, t=t)
    lab_k = 1 - tl.prog("m_all", t, 0.0, 0.3)
    K.map_labels(c, v, "continents", lab_k)
    K.map_highlight(c, v, "asia", tl.prog("m_him", t, 0.3, 0.6) * (1 - tl.prog("m_path", t, 0.5, 0.8)), t=t)
    if t < T("m_path"):
        K.map_label(c, v, 100, 52, "Asia", 26, k=tl.prog("m_him", t, 0.35, 0.6))
    ks = [tl.prog("m_all", t, 0.25 + 0.15 * i, 0.4 + 0.15 * i) for i in range(4)]
    names_k = 1 - tl.prog("m_path", t, 0.0, 0.3)
    big = 3 if t >= T("m_him", 0.6) else None
    mountain_icons(c, v, t, ks, names_k, big)
    hx, hy = v.xy(*HOME)
    K.you_are_here(c, hx, hy, t, tl.prog("m_all", t, 0.0, 0.2) * (1 - tl.prog("m_path", t, 0.6, 0.8)),
                   "Home" if t < T("m_path") else "", side=-1)
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.12, 0.85)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        if t >= T("m_path", 0.1):
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, 1, fly=1)
        ex, ey = v.xy(*EVEREST)
        K.label(c, ex + 40, ey - 120, "The Himalayas", 30, tip=(ex, ey - 26), k=tl.prog("m_path", t, 0.8, 0.95))
    if t < T("m_path", 0.12):
        sk = ease(tl.prog("m_path", t, 0.0, 0.12))
        laugh = T("m_laugh") <= t < T("m_laugh", 1)
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
        x = lerp(170, hx, sk)
        y = lerp(660, hy + 6, sk)
        s = lerp(0.75, 0.16, sk)
        map_crew(c, tl, t, x, y, s, eyes=eyes, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
                 extra={"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None)
    return c


# ======================================================================= peaks

LEDGE = (300, 594)
TASHI = (1010, 562)
CREW_P = 1.1


def snowfall(c, t, n=50, k=1.0, seed=2):
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(int(n * k)):
        sp = rng.uniform(30, 80)
        x = (rng.uniform(0, W) + 30 * math.sin(t * 0.8 + i) - t * 40) % W
        y = (rng.uniform(0, H) + t * sp) % H
        c.circle(x, y, rng.uniform(2, 4.5), (255, 255, 255), ol=None)


def breath(c, x, y, t, k=1.0):
    """Little frosty breath puffs."""
    if k <= 0.01:
        return
    u = (t * 1.2) % 1
    c.circle(x + 22 * u, y - 10 * u, (5 + 10 * u) * k, mix((255, 255, 255), (220, 236, 255), u), ol=None)


def peaks(tl, t):
    T = tl.t
    c = Canvas(P.himalaya_bg().copy())
    snowfall(c, t, 30 + 50 * tl.prog("p_cold", t, 0.0, 0.3), seed=4)
    ev = P.everest_top()
    # snow plume streaming off Everest's top
    for k in range(4):
        u = (t * 0.25 + k / 4) % 1
        c.ellipse(ev[0] + 60 + 220 * u, ev[1] + 10 + 18 * u, 26 * (1 - u) + 4, 8 * (1 - u) + 2,
                  (255, 255, 255), ol=None)

    # Tashi climbs up onto her rock (from behind it) at the start
    rise = ease_out(tl.prog("p_look", t, 0.0, 0.9))
    if rise > 0:
        laugh = False
        teyes = "happy" if tl.talking("tashi", t) and t < T("p_hello", 0.4) else "open"
        tail = 0.0
        if t >= T("p_bye"):
            tail = 0.8 * math.sin(t * 5)
        P.snow_leopard(c, TASHI[0], TASHI[1] + 230 * (1 - rise), 1.0, -1, t, tl.mouth("tashi", t), teyes,
                       look=(-1, -0.2) if t < T("p_ever") else (-0.6, -0.6), tail=tail)
        if rise < 1:
            P.tashi_rock(c)

    # the friends on the cushion: land on the ledge, take off at the end
    land = ease(tl.prog("p_land", t, 0.0, 0.7))
    go = ease(tl.prog("p_go", t, 0.1, 1.0))
    x = lerp(-160, LEDGE[0], land) + 900 * go
    y = lerp(260, LEDGE[1], land) - 520 * go - 60 * math.sin(math.pi * go)
    cold = tl.prog("p_cold", t, 0.0, 0.2)
    shiver = math.sin(t * 60) * 2.2 * cold * (1 - go)
    eyes, look, extra = {}, {}, {}
    look = {"luna": (1, -0.6), "whiskers": (1, -0.6), "pip": (1, -0.6)}
    if T("p_hello") <= t < T("p_ever"):
        look = {"luna": (1, 0), "whiskers": (1, 0), "pip": (1, 0)}
    if T("p_narr") <= t < T("p_hello", 0.3):
        eyes = {"pip": "wide", "whiskers": "wide"}
    if cold > 0 and t < T("p_volc"):
        eyes = {"whiskers": "wide"}
    if T("p_volc") <= t < T("p_bye"):
        eyes = {"whiskers": "happy"}
    fly = max(1 - land, tl.prog("p_go", t, 0.0, 0.3))
    K.crew(c, tl, t, x + shiver, y, CREW_P, 1, fly=fly, eyes=eyes, look=look, extra=extra)
    if 0.01 < cold and go < 0.05:
        wx = x - 52 * CREW_P + 0.62 * CREW_P * 50
        wy = y - 40 * CREW_P - 0.62 * CREW_P * 100
        breath(c, wx, wy, t, cold)
        breath(c, x + 104 * CREW_P + 18, y - 40 * CREW_P - 40, t + 0.4, cold * 0.7)

    # --- teaching moments
    ke = window(tl, t, ("p_ever", 0.3), ("p_sky", 0.1))
    if ke > 0.01:
        K.sparkles(c, ev[0], ev[1] + 10, 50, t, 8, ke, seed=9)
        K.label(c, ev[0] + 250, ev[1] + 40, "Mount Everest", 32, tip=(ev[0] + 14, ev[1] + 6), k=ke)
        K.label(c, ev[0] + 250, ev[1] + 100, "The tallest on Earth!", 24, k=tl.prog("p_ever", t, 0.6, 0.8) * ke,
                bg=(255, 236, 150))
    ks = window(tl, t, ("p_sky", 0.1), ("p_deep", 0.0))
    if ks > 0.01:
        kk = tl.prog("p_sky", t, 0.55, 1.0) * 0.15 + tl.prog("p_skyact", t, 0.0, 0.7) * 0.85
        K.inset(c, 640, 210, 460, 330, ks, lambda ic: P.skyscraper_inset(ic, t, kk))
    kd = window(tl, t, ("p_deep", 0.3), ("p_cold", 0.0))
    if kd > 0.01:
        kk = tl.prog("p_hide", t, 0.15, 1.0) * 0.6 + tl.prog("p_hideact", t, 0.0, 0.5) * 0.4
        K.inset(c, 640, 210, 460, 330, kd, lambda ic: P.trench_inset(ic, t, kk))
    kc = window(tl, t, ("p_higher", 0.05), ("p_warm", 0.3))
    if kc > 0.01:
        kk = tl.prog("p_higher", t, 0.1, 1.0) * 0.5 + tl.prog("p_coldact", t, 0.0, 0.8) * 0.5
        K.inset(c, 640, 210, 460, 330, kc, lambda ic: P.cold_inset(ic, t, kk))
        K.label(c, 1080, 70, "Higher = colder", 28, k=tl.prog("p_coldact", t, 0.1, 0.3) * kc,
                bg=(210, 230, 255))
    kv = window(tl, t, ("p_volc", 0.4), ("p_go", 0.2))
    if kv > 0.01:
        lx = x + 46 * CREW_P
        K.bubble(c, lx + 150, 330, 92, 70, kv, tail=(lx + 30, y - 160))
        P.icon_volcano(c, lx + 150, 330, 50 * kv, t)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== trip

GALAPAGOS = (-90.5, -0.6)
TRIP_PATH = [EVEREST, (60, 18), (25, 8), (-10, 2), (-40, -4), (-62, -6), (-78, -2), GALAPAGOS]


def trip(tl, t):
    T = tl.t
    u = K.smooth(t, [(T("tr_go", 0.3), 0.0), (T("tr_path", 0.75), 1.0)], 0.4)
    a = (EVEREST[0] - 6, EVEREST[1] + 2, 2.6)
    mid = (0, 5, 1.0)
    b = (GALAPAGOS[0] + 4, GALAPAGOS[1] + 2, 2.6)
    k1 = ease(tl.prog("tr_go", t, 0.0, 1.0) * 0.4 + tl.prog("tr_narr", t, 0.0, 0.5) * 0.6)
    k2 = ease(tl.prog("tr_path", t, 0.2, 0.9))
    cam = K.lerp_view(a, mid, k1) if k2 <= 0 else K.lerp_view(mid, b, k2)
    c, v = K.map_view(*cam, t=t)
    K.map_labels(c, v, ["Asia", "Africa", "South America", "Pacific Ocean", "Atlantic Ocean", "Indian Ocean"],
                 1 - k2 * 0.6)
    mountain_icons(c, v, t, [0, 0, 1, 1], names_k=0.0)
    K.map_path(c, v, TRIP_PATH, max(u, 0.0001), head=u > 0.02)
    x, y, ang = K.path_point(v, TRIP_PATH, u)
    K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, -1, fly=1)
    gx, gy = v.xy(*GALAPAGOS)
    K.you_are_here(c, gx, gy, t, tl.prog("tr_narr", t, 0.4, 0.7), "Galapagos Islands", side=1)
    K.flash(c, tl.prog("tr_path", t, 0.85, 1.0) * 0.8)
    K.sub_band(c, tl, t)
    return c


# ===================================================================== volcano

HOVER = (330, 470)
IGGY = (1020, 540)
ROD_TIP = (712, 286)
FISH_HANG = (712, 336)


def lava_cool_stream(c, pts, u, t, cool):
    """Lava stream whose lower end has cooled into dark new rock (cool 0..1)."""
    if u <= 0.01:
        return
    if cool <= 0.01:
        P.lava_stream(c, pts, u, t)
        return
    sp = K.spline(pts, 8)
    n = max(2, int(len(sp) * clamp(u)))
    seg = sp[:n]
    split = max(2, int(n * (1 - 0.6 * cool)))
    hot = seg[:split]
    rock = seg[split - 1:]
    if len(hot) > 1:
        c.line(hot, (150, 30, 20), 20)
        c.line(hot, (250, 110, 30), 14)
        c.line(hot, (255, 220, 90), 5)
    if len(rock) > 1:
        c.line(rock, OUT, 22)
        c.line(rock, (60, 56, 64), 16)


def whiskers_paw(x, y, s):
    """Where Whiskers' front paw is, for the crew at (x, y) scale s."""
    return x - 52 * s + 0.62 * s * 32, y - 40 * s - 0.62 * s * 34


def volcano(tl, t):
    T = tl.t
    c = Canvas(P.island_bg().copy())
    # gentle sea sparkle
    for i in range(8):
        xx = (i * 167 + t * 18) % W
        c.arc(xx, 400 + (i % 3) * 50, 16, 5, 200, 340, (220, 240, 255), 2)
    # --- the volcano: steam, rumble, eruption, cooling
    rumble = tl.prog("v_rumble", t, 0.0, 0.5)
    erupt = tl.prog("v_erupt", t, 0.0, 0.15)
    calm = tl.prog("v_cool", t, 0.0, 1.0) * 0.6 + tl.prog("v_islandact", t, 0.0, 1.0) * 0.3
    P.crater_glow(c, 0.25 + 0.4 * rumble + 0.35 * erupt - 0.3 * calm, t)
    P.smoke(c, P.CRATER[0], P.CRATER[1] - 4, t, 0.6 + 0.4 * erupt, n=6, big=0.7 + 0.8 * erupt,
            col=(214, 212, 220) if erupt <= 0 else (170, 164, 172))
    lu = ease(tl.prog("v_erupt", t, 0.15, 0.9))
    cool = ease(tl.prog("v_cool", t, 0.1, 1.0) * 0.5 + tl.prog("v_coolact", t, 0.0, 1.0) * 0.5)
    lava_cool_stream(c, P.LAVA_LEFT, lu, t, cool)
    P.lava_stream(c, P.LAVA_RIGHT, lu * 0.85, t) if cool < 0.5 else lava_cool_stream(c, P.LAVA_RIGHT,
                                                                                         lu * 0.85, t, cool)
    # new black rock where the lava reached the sea
    if lu >= 0.98:
        nk = ease(tl.prog("v_erupt", t, 0.85, 1.0))
        c.ellipse(712, 368, 50 * nk, 12 * nk, (60, 56, 64), ol=OUT, w=2.5)
        if cool < 1:
            P.smoke(c, 712, 360, t, (1 - cool) * nk, n=5, big=0.5, col=(240, 244, 250), seed=6)
    P.lava_fountain(c, P.CRATER[0], P.CRATER[1], t, erupt * (1 - 0.8 * calm), n=28, h=190)
    if 0 < rumble < 1 or (T("v_shake") <= t < T("v_erupt") and rumble > 0):
        for i in range(5):
            u = (t * 1.4 + i / 5) % 1
            c.circle(P.CRATER[0] + 40 * math.sin(i * 1.9), P.CRATER[1] - 60 * u, 3 + 3 * (1 - u),
                     (255, 190, 90), ol=None)

    # --- Iggy on his rock
    laugh = T("v_laugh") <= t < T("v_laugh", 1)
    ieyes = "happy" if laugh or (tl.talking("iggy", t) and t < T("v_hello", 0.25)) else "open"
    if T("v_erupt") <= t < T("v_erupt", 0.3):
        ieyes = "wide"
    lift = 1.0 if tl.talking("iggy", t) else 0.3
    P.iguana(c, IGGY[0], IGGY[1], 1.0, -1, t, tl.mouth("iggy", t), ieyes,
             look=(-1, 0) if t < T("v_magma") else (-0.5, -0.8), lift=lift)

    # --- the friends hovering on the cushion
    land = ease(tl.prog("v_land", t, 0.0, 0.7))
    up = ease(tl.prog("v_bye", t, 0.2, 1.0))
    x = lerp(-200, HOVER[0], land) + 1100 * up
    y = lerp(200, HOVER[1], land) - 400 * up
    eyes, extra = {}, {}
    look = {"luna": (1, -0.3), "whiskers": (1, -0.6), "pip": (1, -0.3)}
    if T("v_choc") <= t < T("v_hello", 0.2):
        eyes = {"whiskers": "happy"}
    if T("v_rumble") <= t < T("v_toast"):
        eyes = {"whiskers": "wide", "luna": "wide", "pip": "wide"}
    if T("v_hot") <= t < T("v_oven"):
        eyes = {"whiskers": "wide"}
    if T("v_purpose", 0.8) <= t < T("v_laugh", 1):
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
        if t >= T("v_laugh"):
            extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}}
    if T("v_island") <= t:
        look = {"luna": (1, 0), "whiskers": (1, 0), "pip": (1, 0)}
    K.crew(c, tl, t, x, y, CREW_P, 1, fly=1.0, eyes=eyes, look=look, extra=extra)

    # --- the fishing-rod gag
    px, py = whiskers_paw(x, y, CREW_P)
    rod_out = ease(tl.prog("v_fish", t, 0.0, 0.25)) * (1 - ease(tl.prog("v_fish", t, 0.68, 0.9)))
    hold = tl.prog("v_toast", t, 0.3, 0.5) * (1 - tl.prog("v_purpose", t, 0.8, 1.0))
    burnt = ease(tl.prog("v_fish", t, 0.38, 0.6))
    if hold > 0.01 and t < T("v_laugh", 1):
        tipx = lerp(px + 70, ROD_TIP[0], rod_out)
        tipy = lerp(py - 40, ROD_TIP[1], rod_out)
        # telescopic rod: segments getting thinner
        segs = 4
        for i in range(segs):
            a0, a1 = i / segs, (i + 1) / segs
            c.line([(lerp(px, tipx, a0), lerp(py, tipy, a0)), (lerp(px, tipx, a1), lerp(py, tipy, a1))],
                   OUT, 9 - i * 1.5)
            c.line([(lerp(px, tipx, a0), lerp(py, tipy, a0)), (lerp(px, tipx, a1), lerp(py, tipy, a1))],
                   (196, 140, 80) if i % 2 == 0 else (226, 180, 110), 6 - i * 1.2)
        hang = lerp(30, FISH_HANG[1] - ROD_TIP[1], rod_out)
        sway = 4 * math.sin(t * 3)
        fx, fy = tipx + sway, tipy + hang
        c.line([(tipx, tipy), (fx, fy)], (60, 60, 70), 1.5)
        if t < T("v_purpose", 0.85):
            P.fish(c, fx, fy + 30, 0.8, burnt, ang=90)
            if burnt > 0.3:
                P.smoke(c, fx, fy + 20, t, burnt * 0.6, n=4, big=0.3, col=(110, 106, 112), seed=11)
        # puff when it gets toasted
        pk = tl.prog("v_fish", t, 0.55, 0.7)
        if 0 < pk < 1:
            for i in range(6):
                a = i * math.tau / 6
                c.circle(fx + math.cos(a) * 40 * pk, fy + 30 + math.sin(a) * 30 * pk, 18 * (1 - pk) + 4,
                         (120, 116, 122), ol=None)
        if T("v_purpose", 0.85) <= t:
            # a bite out of it: crumbs
            P.fish(c, fx, fy + 30, 0.8, 1.0, ang=90)
            c.circle(fx + 8, fy + 10, 12, (110, 160, 214) if False else (186, 214, 240), ol=None)
            for i in range(5):
                u = ((t - T("v_purpose", 0.85)) * 1.5 + i / 5) % 1
                c.circle(fx + 10 + 12 * math.sin(i * 2), fy + 20 + 80 * u, 3, (40, 34, 36), ol=None)
        if T("v_hot") <= t < T("v_oven"):
            K.text(c, x - 70 + 4 * math.sin(t * 30), y - 200, "HOT!", 44, (240, 80, 50), stroke=4, stroke_fill=(255, 255, 255))
    # hot-chocolate thought bubble
    kb = window(tl, t, ("v_choc", 0.2), ("v_hello", 0.3))
    if kb > 0.01:
        wx = x - 52 * CREW_P
        K.bubble(c, wx + 30, 220, 96, 70, kb, tail=(wx + 10, y - 150))
        P.mug(c, wx + 30, 228, 56 * kb, t)
        K.arrow(c, wx + 140, 210, 860, 150, (255, 236, 90), 7, kb)
    # labels on the real volcano
    kv = window(tl, t, ("v_hello", 0.3), ("v_magma", 0.1))
    if kv > 0.01:
        K.label(c, 1110, 60, "Volcano", 32, tip=(990, 130), k=kv)
    # inside a volcano (cut-away)
    kc = window(tl, t, ("v_magma", 0.1), ("v_rumble", 0.0))
    if kc > 0.01:
        km = tl.prog("v_magma", t, 0.25, 0.9)
        kl = tl.prog("v_lava", t, 0.3, 0.9)
        K.inset(c, 560, 200, 440, 300, kc, lambda ic: P.cutaway_inset(ic, t, km, kl))
    kn = window(tl, t, ("v_oven", 0.4), ("v_purpose", 0.3))
    if kn > 0.01:
        K.label(c, 990, 380, "Never go near lava!", 28, k=kn, col=(255, 255, 255), bg=(220, 70, 60))
    kr = window(tl, t, ("v_cool", 0.4), ("v_island", 0.2))
    if kr > 0.01:
        K.label(c, 560, 260, "New rock!", 30, tip=(700, 360), k=kr)
    ki = window(tl, t, ("v_island", 0.2), ("v_bye", 0.3))
    if ki > 0.01:
        kk = tl.prog("v_island", t, 0.3, 1.0) * 0.4 + tl.prog("v_islandact", t, 0.0, 0.7) * 0.6
        K.inset(c, 560, 200, 440, 300, ki, lambda ic: P.island_inset(ic, t, kk))
    K.sub_band(c, tl, t)
    c = shake(c, tl.prog("v_rumble", t, 0.0, 0.3) * (1 - tl.prog("v_erupt", t, 0.3, 0.6)) * 0.8
              + 0.6 * math.sin(math.pi * tl.prog("v_erupt", t, 0.0, 0.3)), t)
    K.flash(c, 0.35 * math.sin(math.pi * tl.prog("v_erupt", t, 0.0, 0.12)), (255, 220, 160))
    return c


# ==================================================================== remember

FACTS = ["Mountains grow when the land pushes together.",
         "Mount Everest is the tallest mountain on Earth.",
         "Volcanoes have hot, melted rock inside."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_push, P.icon_everest, P.icon_volcano], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Which is the tallest mountain on Earth?",
                        ["Mount Everest", "Nap Mountain"], 0,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_everest, P.icon_blanket], number=1, answer_text="Mount Everest!")
    else:
        c = K.quiz_card(t, "What is inside a volcano?",
                        ["Hot chocolate", "Hot melted rock"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.icon_mug, P.icon_magma], number=2, answer_text="Hot melted rock!")
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
    pts, amp = P.blanket(c, BL_L1, BL_R1, SY, BL)
    top = min(pts, key=lambda p: p[1])
    gcx, gcy = K.GLOBE_X, SY - 170
    e = ease(back)
    x = lerp(gcx, CUSH_X, e)
    y = lerp(gcy + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    # Whiskers hops from the cushion up onto Nap Mountain and falls asleep there
    hk = tl.prog("h_nap", t, 0.05, 0.4)
    who = ("whiskers", "luna", "pip") if hk <= 0 else ("luna", "pip")
    K.crew(c, tl, t, x, y, s, 1, fly=1 - back, who=who, look={"luna": (1, -0.5), "pip": (1, -0.5)})
    if hk > 0:
        a = (CUSH_X - 52 * CREW_S, SY - 40 * CREW_S)
        b = (top[0] - 6, top[1] + 10)
        wx, wy = hop(a, b, hk, 200)
        asleep = t >= T("h_curl", 0.2)
        if hk < 1:
            kat(c, tl, t, "whiskers", wx, wy, CAT_S, 1, "leap" if 0.05 < hk < 0.95 else "sit")
        elif asleep:
            kat(c, tl, t, "whiskers", wx, wy, CAT_S, 1, "sleep")
            D.zzz(c, wx + 20, wy - 70, t)
        else:
            kat(c, tl, t, "whiskers", wx, wy, CAT_S, 1, "sit", eyes="happy")
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Rivers and Lakes", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "peaks": peaks, "trip": trip, "volcano": volcano,
               "remember": remember, "quiz": quiz, "home": home}
