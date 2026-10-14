"""Scenes of Episode 9 "Weather and Seasons". One function per scene: (tl, t) -> Canvas.

The farm (props.farm_bg) is cached once per season and crossfaded, so the same tree can turn
through spring, summer, autumn and winter. The orbit scene is a space diagram: the Sun in the
middle and the tilted Earth travelling round it, then a close-up of the leaning Earth.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e09_weather_seasons import props as P
from world.s1e05_rivers_lakes import props as P5
from world.s1e02_seven_continents import props as P2

CONTINUOUS = ("map",)
EXTRA_CUTS = ("o_aus",)


def laughing(t):
    return 0.5 + 0.4 * math.sin(t * 15)


def hop(a, b, u, h=80):
    u = ease(u)
    return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - 4 * h * u * (1 - u)


def ten(tl, t, a_id, a0, a1, b_id=None, b0=0.0, b1=0.3):
    """Fade in over event a (fractions a0..a1) and out over event b."""
    k = tl.prog(a_id, t, a0, a1)
    if b_id:
        k *= 1 - tl.prog(b_id, t, b0, b1)
    return k


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 9, "Weather and Seasons")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 300
CREW_S = 1.45
CAT_S = 0.9
LUNA_X = 880
PIP_X = 548
WIN = (170, 40, 1110, SY - 34)


@lru_cache(None)
def _window(mood="day"):
    x0, y0, x1, y1 = WIN
    ww, wh = x1 - x0, y1 - y0
    sky = {"day": [(0, (110, 176, 236)), (0.8, (240, 222, 196)), (1, (250, 230, 200))],
           "evening": [(0, (98, 92, 170)), (0.45, (238, 140, 130)), (1, (255, 210, 140))]}[mood]
    win = Canvas(D.gradient(ww * SS, wh * SS, sky), size=(ww, wh))
    eve = mood == "evening"
    if eve:
        win.glow(ww * 0.78, wh * 0.74, 240, 130, (255, 236, 170), (250, 170, 130), steps=10)
        win.circle(ww * 0.78, wh * 0.76, 40, (255, 220, 130), ol=None)
    else:
        win.circle(ww - 140, 80, 38, (255, 226, 100), ol=None)
        D.cloud(win, 560, 90, 0.7)
    tint = (60, 30, 60) if eve else (0, 0, 0)
    k = 0.2 if eve else 0.0
    win.poly([(0, wh * 0.72), (200, wh * 0.62), (420, wh * 0.7), (640, wh * 0.6), (ww, wh * 0.7), (ww, wh),
              (0, wh)], mix((206, 186, 110), tint, k), ol=None)
    win.poly([(0, wh * 0.86), (300, wh * 0.8), (700, wh * 0.85), (ww, wh * 0.8), (ww, wh), (0, wh)],
             mix((186, 160, 90), tint, k), ol=None)
    for hx, hw_, hh, col in ((700, 70, 60, (232, 120, 100)), (790, 56, 48, (240, 200, 120))):
        bx, by = hx, wh * 0.84
        win.rect(bx - hw_ / 2, by - hh, bx + hw_ / 2, by, mix((250, 240, 220), tint, k), ol=None)
        win.poly([(bx - hw_ / 2 - 8, by - hh), (bx, by - hh - 36), (bx + hw_ / 2 + 8, by - hh)], mix(col, tint, k),
                 ol=None)
        win.rect(bx - 8, by - hh * 0.6, bx + 8, by - hh * 0.25, (255, 226, 130) if eve else (150, 200, 240),
                 ol=None)
    P.season_tree(win, 200, wh * 0.95, 1.05, "autumn")
    P.season_tree(win, 900, wh * 0.9, 0.5, "autumn")
    return win.finish()


@lru_cache(None)
def autumn_home(mood="day"):
    c = Canvas(K.home_bg(mood).copy())
    x0, y0, x1, y1 = WIN
    c.img.paste(_window(mood).resize(((x1 - x0) * SS, (y1 - y0) * SS)), (x0 * SS, y0 * SS))
    for mx in (483, 797):
        c.rect(mx - 6, y0, mx + 6, y1, (255, 250, 240), w=2)
    c.rect(x0, y0, x1, y1, None, ol=OUT, w=2)
    return c.img


def window_leaves(c, t, k=1.0, wind=0.4):
    x0, y0, x1, y1 = WIN
    P.falling_leaves(c, t, (x0 + 14, y0 + 30, x1 - 14, y1 - 16), n=16, k=k, wind=wind, seed=7, size=10)


def seasons_inset(ic, t, k):
    """Four little trees in a row: the seasons, with arrows round."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (190, 226, 252)), (1, (236, 246, 255))]), (0, 0))
    names = ["Spring", "Summer", "Autumn", "Winter"]
    for i, (sea, nm) in enumerate(zip(("spring", "summer", "autumn", "winter"), names)):
        kk = clamp(k * 4 - i)
        if kk <= 0:
            continue
        x = 80 + i * 150
        ic.ellipse(x, h - 62, 60, 10, (130, 196, 96) if sea != "winter" else (240, 246, 255), w=2)
        P.season_tree(ic, x, h - 62, 0.42 * pop(kk), sea, t)
        K.text(ic, x, h - 28, nm, 24, (48, 40, 60))
        if i < 3 and kk >= 1:
            K.arrow(ic, x + 52, 110, x + 98, 110, (240, 110, 90), 5, clamp(k * 4 - i - 1), head=12)


def sill_globe_lon(t, spins):
    lon = 20.0
    for ts, amount in spins:
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    return lon - 4 * t


def sill(tl, t):
    T = tl.t
    c = Canvas(autumn_home().copy())
    window_leaves(c, t)
    spins = [(T("s_autumn", 0.3), 200), (T("s_hold", 0.3), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        worried = T("s_broken") <= t < T("s_broken", 1)
        wk = {}
        if worried:
            wk = dict(eyes="wide", look=(1, -1))
        elif T("s_skip") <= t < T("s_skip", 1):
            wk = dict(eyes="closed" if t > T("s_skip", 0.5) else "open", look=(1, -0.3))
        else:
            wk = dict(look=(1, -0.4))
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", **wk)
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_why") else -1, proud=tl.talking("pip", t))
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
    # a leaf tumbles past Whiskers' nose when he worries
    lk = tl.prog("s_broken", t, 0.0, 1.0)
    if 0 < lk < 1:
        P.leaf(c, lerp(260, 120, lk) + 20 * math.sin(lk * 9), lerp(300, 470, lk), 14, lk * 400, P.LEAF_COLS[0])
    # Luna's seasons inset
    kj = ten(tl, t, "s_autumn", 0.25, 0.4, "s_skip", 0.0, 0.25)
    if kj > 0.01:
        jk = tl.prog("s_autumn", t, 0.35, 1.0) * 0.6 + tl.prog("s_autact", t) * 0.4
        K.inset(c, 640, 160, 640, 250, kj, lambda ic: seasons_inset(ic, t, jk))
    # Whiskers dreams of his sunny nap spot
    bk = ten(tl, t, "s_skip", 0.15, 0.35, "s_why", 0.0, 0.3)
    if bk > 0.01:
        bx, by = 420, 170
        K.bubble(c, bx, by, 120, 80, bk, tail=(CUSH_X - 60, SY - 150))
        c.push(bx, by, bk)
        c.circle(40, -30, 26, (255, 222, 96), ol=(236, 160, 50), w=3)
        for k in range(8):
            a = k * math.tau / 8
            c.line([(40 + math.cos(a) * 32, -30 + math.sin(a) * 32), (40 + math.cos(a) * 42, -30 + math.sin(a) * 42)],
                   (255, 200, 80), 3)
        K.cushion(c, -20, 40, 0.42, t)
        kat(c, None, t, "whiskers", -30, 24, 0.3, 1, "sleep", mouth=0.0)
        c.pop()
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
FARM = (-0.6, 51.0)
GO_PATH = [HOME, (1.6, 49.9), (0.6, 50.6), FARM]
V0 = (0, 0, 1.0)
VE = (6, 49, 3.2)
VF = (0.8, 49.8, 8.0)


def space_globe_lon(tl, t):
    t0 = tl.t("m_fly")
    raw = -14 * (t - t0) + 40
    end = -14 * (tl.t("m_narr", 1) - t0) + 40
    target = round(end / 360) * 360
    return lerp(raw, target, ease(tl.prog("m_flat", t, 0.0, 0.3)))


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
    elif t < T("m_farm"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        K.globe_to_map(c, k, t, 230, lon=0)
        if k >= 1:
            K.map_labels(c, K.MapView(0, 0, 1), "continents", tl.prog("m_flat", t, 0.85, 1.0))
        K.crew(c, tl, t, 170, 660, 0.75, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        k1 = ease(tl.prog("m_farm", t, 0.0, 0.4))
        k2 = ease(tl.prog("m_path", t, 0.0, 0.8))
        cam = K.lerp_view(VE, VF, k2) if k2 > 0 else K.lerp_view(V0, VE, k1)
        c, v = K.map_view(*cam, t=t)
        K.map_labels(c, v, "continents", 1 - k1)
        K.map_highlight(c, v, "europe", tl.prog("m_farm", t, 0.2, 0.4) * (1 - tl.prog("m_path", t, 0.0, 0.3)), t=t)
        K.map_label(c, v, 14, 54, "Europe", 34, k=tl.prog("m_farm", t, 0.3, 0.5) * (1 - k2))
        hx, hy = v.xy(*HOME)
        K.you_are_here(c, hx, hy, t, tl.prog("m_farm", t, 0.3, 0.5), "Home" if t < T("m_path") else "", side=1)
        fk = tl.prog("m_farm", t, 0.65, 0.85)
        fx, fy = v.xy(*FARM)
        if fk > 0.01:
            # a tiny barn on the hill
            c.push(fx, fy, pop(fk) * max(0.6, v.z / 6))
            c.poly([(-26, 0), (-26, -26), (0, -44), (26, -26), (26, 0)], P.BARN, w=2.5)
            c.rect(-9, -16, 9, 0, P.BARN_D, w=2)
            c.pop()
            K.label(c, fx - 150, fy - 70, "The farm", 30, tip=(fx - 20, fy - 30), k=fk)
        if t >= T("m_path"):
            u = tl.prog("m_path", t, 0.15, 0.85)
            K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.32, 1, fly=1)
            K.flash(c, tl.prog("m_path", t, 0.88, 1.0))
        else:
            K.crew(c, tl, t, 170, 660, 0.75, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    K.sub_band(c, tl, t)
    return c


# ======================================================================== farm

SPOT = (640, 648)
CREW_F = 1.0
HAZ = (870, 604)
SEASONS = ("spring", "summer", "autumn", "winter")
TAG_X = {"spring": 540, "summer": 720, "autumn": 900, "winter": 1080}
TAG_Y = 50


def rufus_pose(tl, t, events_talk=("rufus",)):
    return tl.mouth("rufus", t)


def vane_angle(tl, t, spins):
    """Angle of the vane: each (event, a, b, turns) adds turns while that event runs from a to b."""
    ang = 0.0
    for ev, a, b, turns in spins:
        ang += ease(tl.prog(ev, t, a, b)) * turns * math.tau
    return ang + 0.12 * math.sin(t * 1.3)


def draw_rufus(c, tl, t, ang, flap=0.0, eyes="open", proud=0.0, s=0.85, look=(0.0, 0.0)):
    tx, ty = P.vane(c, P.PEAK[0], P.PEAK[1], 56, 1.0, ang, t)
    sq = math.cos(ang)
    face = 1 if sq >= 0 else -1
    P.rooster(c, tx, ty, s, face, t, tl.mouth("rufus", t), eyes, flap=flap, squash=max(0.06, abs(sq)), proud=proud,
              look=look)
    return tx, ty


def season_state(tl, t):
    """(background a, background b, blend, current season) for the tree through the year."""
    T = tl.t
    steps = [("f_spring", "autumn", "spring"), ("f_summer", "spring", "summer"), ("f_autumn", "summer", "autumn"),
             ("f_winter", "autumn", "winter"), ("f_fouract", "winter", "autumn")]
    a, b, k = "autumn", "autumn", 0.0
    for ev, s0, s1 in steps:
        if t >= T(ev):
            a, b = s0, s1
            k = ease(tl.prog(ev, t, 0.0, 0.3 if ev != "f_fouract" else 0.6))
    cur = b if k > 0.5 else a
    if t < T("f_spring"):
        cur = None
    return a, b, k, cur


def wind_streaks(c, t, k, y0=120, y1=520, n=8, seed=4):
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        y = rng.uniform(y0, y1)
        sp = rng.uniform(500, 800)
        x = (rng.random() * 1600 + t * sp) % 1700 - 200
        pts = [(x - 160 + j * 20, y + 8 * math.sin(j * 0.6 + t * 4 + i)) for j in range(9)]
        c.line(pts, mix((255, 255, 255), (200, 220, 240), 0.3), 3 * k)
        c.arc(pts[-1][0] + 4, pts[-1][1] - 10, 12, 10, -90, 120, (255, 255, 255), 3 * k)


def season_tags(c, tl, t, cur, k_all, k_cycle=0.0):
    if k_all <= 0.01:
        return
    T = tl.t
    for i, sea in enumerate(SEASONS):
        ev = ("f_spring", "f_summer", "f_autumn", "f_winter")[i]
        kk = tl.prog(ev, t, 0.0, 0.2) * k_all
        if kk <= 0.01:
            continue
        on = sea == cur
        col = {"spring": (226, 90, 140), "summer": (220, 140, 20), "autumn": (200, 90, 30), "winter": (60, 110, 200)}
        K.label(c, TAG_X[sea], TAG_Y + (6 * math.sin(t * 6) if on else 0), sea.capitalize(), 34 if on else 28, k=kk,
                col=col[sea] if on or k_cycle > 0 else (130, 120, 130),
                bg=(255, 250, 200) if on else (255, 255, 255))
        if i < 3 and k_cycle > 0:
            K.arrow(c, TAG_X[sea] + 66, TAG_Y, TAG_X[SEASONS[i + 1]] - 66, TAG_Y, (255, 255, 255), 5,
                    clamp(k_cycle * 3 - i), head=12)
    if k_cycle > 0.66:
        P5.arc_arrow(c, 810, TAG_Y + 20, 300, 50, 10, 170, clamp((k_cycle - 0.66) * 3), (255, 236, 110), 7, 18)


def farm(tl, t):
    T = tl.t
    a, b, k, cur = season_state(tl, t)
    c = Canvas(P.farm_mix(a, b, k))
    # weather particles
    autumn_k = 1.0 if cur in (None, "autumn") else 0.0
    if cur is not None and a != b:
        if b == "autumn":
            autumn_k = k
        elif a == "autumn":
            autumn_k = 1 - k
    wind_k = tl.prog("f_windact", t, 0.0, 0.2) * (1 - tl.prog("f_windact", t, 0.8, 1.0)) + \
        tl.prog("f_spin", t, 0.0, 0.3) * (1 - tl.prog("f_spin", t, 0.7, 1.0)) * 0.6
    P.falling_leaves(c, t, (700, 230, 1280, 640), n=12, k=autumn_k, wind=0.15 + wind_k * 1.5, seed=3)
    if wind_k > 0.01:
        P.falling_leaves(c, t * 1.6, (0, 150, 1280, 560), n=18, k=wind_k, wind=2.5, seed=9, size=11)
    wind_streaks(c, t, wind_k)
    spring_k = (k if b == "spring" else (1 - k) if a == "spring" else 0.0) if cur else 0.0
    P.petals(c, t, (760, 260, 1280, 640), 18, spring_k)
    winter_k = (k if b == "winter" else (1 - k) if a == "winter" else 0.0) if cur else 0.0
    P.snowfall(c, t, (0, 0, W, 700), 70, winter_k)
    summer_k = (k if b == "summer" else (1 - k) if a == "summer" else 0.0) if cur else 0.0
    if summer_k > 0.01:
        K.sparkles(c, P.SUNS["summer"][0], P.SUNS["summer"][1], 110, t, 8, summer_k, seed=5)
    # Sir Rufus on his vane
    ang = vane_angle(tl, t, [("f_spin", 0.05, 0.75, 2), ("f_windact", 0.05, 0.9, 3), ("f_wind", 0.1, 0.4, 1)])
    hello = T("f_hello") <= t < T("f_hello", 1)
    fly_k = tl.prog("f_go", t, 0.0, 0.35)
    proud = 1.0 if hello or T("f_friend") <= t < T("f_friend", 1) else 0.0
    r_eyes = "proud" if proud else "closed" if t < T("f_spin") else "open"
    if T("f_narr", 0.6) <= t < T("f_spin", 0.6):
        r_eyes = "closed"
    flap = max(0.6 * (1 - abs(math.sin(t * 6))) if hello else 0.0,
               0.8 * abs(math.sin(t * 10)) if T("f_space", 0.6) <= t else 0.0)
    if fly_k <= 0:
        tx, ty = draw_rufus(c, tl, t, ang, flap, r_eyes, proud, look=(1, 0.5))
        if hello:
            K.sparkles(c, tx + 10, ty - 70, 90, t, 8, tl.prog("f_hello", t, 0.0, 0.2), seed=11)
            K.label(c, tx + 230, ty - 80, "Sir Rufus", 30, k=tl.prog("f_hello", t, 0.3, 0.45), col=(170, 90, 20),
                    bg=(255, 244, 200))
    else:
        P.vane(c, P.PEAK[0], P.PEAK[1], 56, 1.0, ang, t)
    # Hazel the squirrel scampers in from the right
    hk = tl.prog("f_hazel", t, 0.0, 0.6)
    if t >= T("f_hazel"):
        hx = lerp(1360, HAZ[0], ease_out(hk))
        bounce = abs(math.sin(t * 16)) * 14 * (1 - hk) if hk < 1 else 0
        talking = tl.talking("hazel", t)
        winter_now = cur == "winter"
        P.hazel(c, hx, HAZ[1], 1.0, -1, t, tl.mouth("hazel", t), "happy" if T("f_four") <= t < T("f_four", 1)
                else "open", hop=bounce, look=(-1, 0), wave=1.0 if T("f_spring", 0.1) <= t < T("f_spring", 0.5) else 0)
        if winter_now:
            # a little woolly hat for the winter
            c.push(hx, HAZ[1], 1.0, flip=True)
            c.ellipse(12, -94, 18, 10, (90, 140, 220), w=2)
            c.circle(12, -106, 6, (255, 255, 255), w=2)
            c.pop()
    # the friends on the cushion
    lk = ease_out(tl.prog("f_land", t, 0.0, 0.8))
    gk = ease(tl.prog("f_go", t, 0.2, 1.0))
    x = lerp(1400, SPOT[0], lk)
    y = lerp(120, SPOT[1], lk) - 520 * gk
    x += 400 * gk
    eyes, extra, look = {}, {}, {}
    if T("f_spin") <= t < T("f_hello", 0.5):
        eyes = {"whiskers": "wide", "luna": "wide", "pip": "wide"}
    look = {"luna": (-1, -1), "pip": (-1, -1), "whiskers": (-1, -0.6)}
    if T("f_hazel") <= t < T("f_four", 1):
        look = {"luna": (1, -0.2), "pip": (1, -0.2), "whiskers": (1, -0.6)}
    if cur == "summer":
        extra["whiskers"] = {"pose": "sleep", "dy": 6}
    shiver = cur == "winter" and k > 0.5
    if shiver:
        eyes["whiskers"] = "wide"
    if T("f_windact") <= t < T("f_feel", 1):
        eyes.update({"pip": "wide", "luna": "happy"})
    face = -1 if T("f_narr") <= t < T("f_hazel") else 1
    if T("f_whyq") <= t:
        face = -1
        look = {"luna": (-1, -1), "pip": (-1, -1), "whiskers": (-1, -1)}
    jit = math.sin(t * 50) * 3 if shiver else 0
    gust = wind_k * 6 * math.sin(t * 9)
    K.crew(c, tl, t, x + jit + gust, y, CREW_F, face, fly=1 - lk + gk, eyes=eyes, look=look, extra=extra)
    if cur == "summer" and t > T("f_summer", 0.3):
        D.zzz(c, x - 70, y - 110, t)
    if shiver and t < T("f_four"):
        K.label(c, x - 150, y - 150, "Brrr!", 30, k=tl.prog("f_winter", t, 0.4, 0.6), col=(60, 110, 200))
        # snow on the friends' heads
        for dx in (-52, 46):
            c.ellipse(x + face * dx, y - 118 * CREW_F, 22, 7, (255, 255, 255), w=1.5)
    # Rufus flies down to the cushion and off they go to space
    if fly_k > 0:
        tx, ty = P.PEAK[0], P.PEAK[1] - 56
        ux = lerp(tx, x + 190, ease(fly_k))
        uy = lerp(ty, y - 30, ease(fly_k)) - 120 * math.sin(math.pi * fly_k)
        P.rooster(c, ux, uy, 0.7, 1, t, tl.mouth("rufus", t), "open", flap=abs(math.sin(t * 12)))
    # teaching: wind = moving air
    kw = ten(tl, t, "f_wind", 0.3, 0.5, "f_hazel", 0.0, 0.2)
    K.label(c, 760, 120, "Wind = moving air", 38, k=kw, col=(40, 100, 170))
    # winter: snow is frozen water from the clouds
    ks = ten(tl, t, "f_winter", 0.45, 0.65, "f_four", 0.0, 0.2)
    if ks > 0.01:
        K.label(c, 700, 150, "Snow = frozen water from clouds", 32, k=ks, col=(40, 90, 170))
    # the four season tags at the top
    kc = tl.prog("f_four", t, 0.0, 0.8) * (1 - tl.prog("f_whyq", t, 0.0, 0.3))
    k_all = 1 - tl.prog("f_whyq", t, 0.0, 0.3)
    season_tags(c, tl, t, cur if t < T("f_four") else None, k_all, kc)
    # Pip's question bubble: closer to the Sun?
    bk = ten(tl, t, "f_closer", 0.15, 0.35, "f_go", 0.0, 0.2)
    if bk > 0.01:
        px_, py_ = x + 110 * face * -1, y - 70
        K.bubble(c, 940, 200, 120, 80, bk, tail=(x - 104, y - 110))
        c.push(940, 200, bk)
        P.icon_closer(c, 0, 0, 90, t)
        K.text(c, 0, 60, "?", 40, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))
        c.pop()
    K.sub_band(c, tl, t)
    K.flash(c, tl.prog("f_go", t, 0.85, 1.0))
    return c


# ======================================================================= orbit

SUN = (640, 380)
SUN_R = 78
ORX, ORY = 430, 150
E_R = 50
POS = {"summer": 180, "autumn": 270, "winter": 360, "spring": 450}
POS_LABEL = {"summer": ("Summer", (226, 140, 20)), "autumn": ("Autumn", (200, 90, 30)),
             "winter": ("Winter", (60, 110, 200)), "spring": ("Spring", (210, 80, 140))}


def orbit_xy(th):
    a = math.radians(th)
    return SUN[0] + ORX * math.cos(a), SUN[1] - ORY * math.sin(a)


def earth_theta(tl, t):
    """The Earth's place on its orbit (degrees): a full trip during the narration, another in o_trip."""
    T = tl.t
    k1 = ease(clamp((t - T("o_open", 0.3)) / max(0.1, T("o_tilt", 0.55) - T("o_open", 0.3))))
    k2 = ease(tl.prog("o_trip", t, 0.0, 1.0))
    return 180 + 360 * k1 + 360 * k2


def orbit_crew(c, tl, t, k=1.0, eyes=None, extra=None):
    x, y = lerp(-200, 150, ease_out(k)), 640
    K.crew(c, tl, t, x, y, 0.62, 1, fly=1.0, eyes=eyes, extra=extra,
           look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    P.rooster(c, x + 128, y - 26, 0.5, 1, t, tl.mouth("rufus", t), "open",
              flap=0.4 * abs(math.sin(t * 5)) + (0.6 if tl.talking("rufus", t) else 0))


def ray(c, x0, y0, x1, y1, k, col=(255, 226, 90), w=7):
    K.arrow(c, x0, y0, x1, y1, col, w, k, head=16)


def orbit(tl, t):
    T = tl.t
    if t >= T("o_aus"):
        return closeup(tl, t)
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    ok = tl.prog("o_open", t, 0.0, 0.8)
    P.dashed_ellipse(c, SUN[0], SUN[1], ORX, ORY, (190, 196, 255), 3, k=ease(ok), a0=math.pi)
    # "one year" arrow along the front of the orbit
    yk = ten(tl, t, "o_tilt", 0.0, 0.25, "o_tiltact", 0.5, 1.0)
    if yk > 0.01:
        P5.arc_arrow(c, SUN[0], SUN[1], ORX + 34, ORY + 30, 150, 30, yk, (255, 236, 110), 7, 18)
        K.label(c, SUN[0], SUN[1] + ORY + 70, "One trip = one year", 30, k=yk)
    th = earth_theta(tl, t)
    ax_k = tl.prog("o_tilt", t, 0.55, 0.85)
    hl_sum = ten(tl, t, "o_summer", 0.0, 0.2, "o_not", 0.0, 0.3)
    hl_win = ten(tl, t, "o_winter", 0.0, 0.2, "o_not", 0.0, 0.3)
    # ghost Earths left at the four places once the second trip has passed them
    ghosts = []
    if t >= T("o_trip"):
        for sea, deg in POS.items():
            passed = th - 540 >= deg - 180 - 1e-6 or t >= T("o_trip", 1)
            if passed:
                ghosts.append((sea, deg))
    spin = -t * 40
    sun_drawn = False
    items = [(orbit_xy(deg)[1], "ghost", sea, deg) for sea, deg in ghosts]
    if t < T("o_trip", 1) - 0.05 or not ghosts:
        items.append((orbit_xy(th)[1], "earth", None, th))
    items.sort(key=lambda it: it[0])
    for yy, kind, sea, deg in items:
        if not sun_drawn and yy > SUN[1]:
            P.sun(c, SUN[0], SUN[1], SUN_R * pop(ok), t)
            sun_drawn = True
        x, y = orbit_xy(deg)
        sc = 1 + 0.12 * (y - SUN[1]) / ORY
        glow = 0.0
        if sea == "summer":
            glow = hl_sum
        if sea == "winter":
            glow = hl_win
        if glow > 0.01:
            c.circle(x, y, E_R * sc + 14 + 3 * math.sin(t * 6), None, ol=(255, 236, 110), w=5 * glow)
        P.tilted_earth(c, x, y, E_R * sc, lon=spin, sun_xy=SUN, axis=ax_k if kind == "earth" else 1.0,
                       roll=P.TILT, glow_north=glow)
        if kind == "ghost":
            name, col = POS_LABEL[sea]
            lx, ly = x, y + (E_R + 44) * (1 if deg % 360 in (270,) else -1) - (8 if deg % 360 == 90 else 0)
            if sea in ("summer", "winter"):
                ly = y + E_R + 46
            if sea == "spring":
                lx, ly = x + 150, y - 10
            K.label(c, lx, ly, name, 30, k=tl.prog("o_trip", t, 0.0, 0.1) if True else 1, col=col)
    if not sun_drawn:
        P.sun(c, SUN[0], SUN[1], SUN_R * pop(ok), t)
    # "Tilted!" with a straight-up guide line on the travelling Earth
    tk = ten(tl, t, "o_tiltact", 0.0, 0.3, "o_trip", 0.0, 0.2)
    if tk > 0.01:
        x, y = orbit_xy(th)
        for j in range(6):
            c.line([(x, y - E_R * 1.6 + j * 34), (x, y - E_R * 1.6 + j * 34 + 18)], (255, 255, 255), 3 * tk)
        K.label(c, x + 30, y - E_R - 110, "Tilted!", 36, tip=(x + 28, y - E_R - 30), k=tk, col=(200, 70, 60))
    sk = ten(tl, t, "o_same", 0.2, 0.4, "o_trip", 0.2, 0.4)
    K.label(c, 640, 70, "It always leans the same way", 32, k=sk)
    # summer / winter: sunbeams + sky insets
    if hl_sum > 0.01:
        ex, ey = orbit_xy(POS["summer"])
        for j, dy in enumerate((-40, -14, 12)):
            ray(c, SUN[0] - SUN_R - 10, SUN[1] + dy * 0.6, ex + E_R + 14, ey + dy, clamp(hl_sum * 2 - j * 0.3))
        K.inset(c, 240, 140, 400, 220, hl_sum, lambda ic: P.sky_inset(ic, t, True, tl.prog("o_summeract", t)))
    if hl_win > 0.01:
        ex, ey = orbit_xy(POS["winter"])
        for j, dy in enumerate((-40, -14, 12)):
            ray(c, SUN[0] + SUN_R + 10, SUN[1] + dy * 0.6, ex - E_R - 14, ey + dy, clamp(hl_win * 2 - j * 0.3),
                (255, 236, 160), 5)
        K.inset(c, 1040, 140, 400, 220, hl_win, lambda ic: P.sky_inset(ic, t, False, tl.prog("o_winteract", t)))
    # not closer: the same distance both sides
    dk = ten(tl, t, "o_tiltans", 0.3, 0.6, "o_aus", 0.0, 0.1)
    if dk > 0.01:
        for deg in (POS["summer"], POS["winter"]):
            ex, ey = orbit_xy(deg)
            side = -1 if deg == 180 else 1
            x0 = SUN[0] + side * (SUN_R + 18)
            x1 = ex - side * (E_R + 16)
            yy = SUN[1] + 110
            xe = lerp(x0, x1, ease_out(dk))
            c.line([(x0, yy), (xe, yy)], (255, 255, 255), 4)
            for xx in (x0, xe):
                c.line([(xx, yy - 14), (xx, yy + 14)], (255, 255, 255), 4)
        K.label(c, 640, 70, "Same distance all year!", 36, k=tl.prog("o_dist", t, 0.0, 0.3), col=(40, 120, 60))
    # bubble when Pip asks: closer?
    eyes = {}
    if T("o_not") <= t < T("o_not", 1):
        eyes = {"pip": "wide"}
    orbit_crew(c, tl, t, tl.prog("o_open", t, 0.2, 1.0), eyes=eyes)
    K.sub_band(c, tl, t)
    return c


CU = (470, 360)
CU_R = 230
CU_LON = 75


def closeup(tl, t):
    """The leaning Earth close up: our half leans toward the Sun (summer), Australia's half away."""
    T = tl.t
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    P.sun(c, 1250, 300, 170, t, face=False)
    lon = CU_LON + 6 * math.sin(t * 0.3)
    ux, uy = P.tilted_earth(c, CU[0], CU[1], CU_R, lon=lon, lat=0, sun_xy=(2600, 300), axis=1.0, roll=P.TILT,
                            glow_north=1.0)
    # sunbeams onto the top half (straight on) and the bottom half (glancing)
    rk = tl.prog("o_aus", t, 0.1, 0.6)
    for j, yy in enumerate((170, 230, 290)):
        ray(c, 1060, yy - 10, CU[0] + CU_R * 0.85 - j * 6, yy + 20, clamp(rk * 2 - j * 0.3), (255, 226, 90), 9)
    for j, yy in enumerate((470, 540)):
        ray(c, 1060, yy - 40, CU[0] + CU_R * 0.6 - j * 50, yy + 10, clamp(rk * 2 - j * 0.3 - 0.4), (255, 240, 170), 5)
    # pins: Europe and Australia
    ek = tl.prog("o_aus", t, 0.3, 0.5)
    ex, ey, ev = K.globe_xy(CU[0], CU[1], CU_R, 10, 50, lon, 0, P.TILT)
    ax, ay, av = K.globe_xy(CU[0], CU[1], CU_R, 134, -25, lon, 0, P.TILT)
    if ek > 0.01:
        P.tilted_earth  # noqa
        c.circle(ex, ey, 9 * pop(ek), (226, 56, 60), w=3)
        K.label(c, ex - 120, ey - 120, "Europe", 30, tip=(ex - 6, ey - 12), k=ek)
    ak = tl.prog("o_aus", t, 0.6, 0.8)
    if ak > 0.01:
        c.circle(ax, ay, 9 * pop(ak), (226, 56, 60), w=3)
        K.label(c, ax + 40, ay + 150, "Australia", 30, tip=(ax + 4, ay + 14), k=ak)
    # leaning toward / away
    tk = ten(tl, t, "o_ausact", 0.0, 0.3, "o_swap", 0.0, 0.2)
    K.label(c, 860, 120, "Leans toward the Sun", 28, tip=(CU[0] + 150, CU[1] - 170), k=tk)
    K.label(c, 860, 600, "Leans away", 28, tip=(CU[0] + 120, CU[1] + 190), k=tl.prog("o_ausact", t, 0.4, 0.7) *
            (1 - tl.prog("o_swap", t, 0.0, 0.2)))
    # summer / winter labels
    sk = tl.prog("o_swap", t, 0.15, 0.35)
    if sk > 0.01:
        K.label(c, ex - 40, ey - 200, "Summer!", 40, k=sk, col=(220, 120, 20), bg=(255, 246, 200))
        c.push(ex + 90, ey - 200, pop(sk))
        c.circle(0, 0, 22, (255, 222, 96), ol=(236, 160, 50), w=3)
        c.pop()
    wk = tl.prog("o_swap", t, 0.45, 0.65)
    if wk > 0.01:
        K.label(c, ax + 100, ay + 80, "Winter!", 40, k=wk, col=(50, 100, 200), bg=(230, 240, 255))
        c.push(ax + 210, ay + 80, pop(wk))
        for k in range(3):
            a = k * math.pi / 3
            c.line([(-math.cos(a) * 20, -math.sin(a) * 20), (math.cos(a) * 20, math.sin(a) * 20)], (90, 150, 230), 5)
        c.pop()
    # Whiskers' plan: a sunny holiday
    laugh = T("o_laugh") <= t < T("o_back")
    eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
    extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else None
    bk = ten(tl, t, "o_forever", 0.2, 0.4, "o_back", 0.0, 0.3)
    gk = ease(tl.prog("o_back", t, 0.2, 1.0))
    cx_, cy_ = lerp(1000, 1500, gk), lerp(650, 300, gk)
    K.crew(c, tl, t, cx_, cy_, 0.62, -1, fly=1.0, eyes=eyes, extra=extra,
           look={"luna": (-1, -0.5), "whiskers": (-1, -0.5), "pip": (-1, -0.5)})
    P.rooster(c, cx_ - 128, cy_ - 26, 0.5, -1, t, tl.mouth("rufus", t), "happy" if laugh else "open",
              flap=0.4 * abs(math.sin(t * 5)))
    if bk > 0.01:
        K.bubble(c, 1080, 470, 100, 66, bk, tail=(cx_ + 30, cy_ - 80))
        c.push(1080, 470, bk)
        c.circle(-36, -18, 18, (255, 222, 96), ol=(236, 160, 50), w=2)
        c.ellipse(0, 36, 70, 10, (244, 220, 150), w=2)
        c.line([(30, 34), (30, -16)], (140, 100, 70), 3)
        c.poly([(-6, -10), (30, -34), (66, -10)], (240, 90, 90), w=2)
        c.pop()
    K.sub_band(c, tl, t)
    K.flash(c, tl.prog("o_back", t, 0.8, 1.0))
    return c


# ===================================================================== weather

RAIN_BOX = (0, 160, W, 700)
STORM = (820, 420)
RB = (330, 600, 470)            # rainbow centre x, y and radius (opposite the sun, at upper right)


def weather(tl, t):
    T = tl.t
    sun_k = ease(tl.prog("w_sun", t, 0.0, 0.5)) * 0.75
    c = Canvas(P.farm_mix("rain", "autumn", sun_k))
    # far storm cloud flashing on the horizon
    fl = 0.0
    for ev in ("w_flash",):
        u = tl.prog(ev, t, 0.05, 0.5)
        if 0 < u < 1:
            fl = max(fl, 1 - abs(u * 4 % 2 - 1) if u < 0.5 else (1 - u) * 2 * 0.5)
    if t >= T("w_open"):
        P.storm_cloud(c, STORM[0], STORM[1] - 30, 0.75, fl)
    # rainbow: appears once the sun is out, opposite the sun
    rbk = ease(tl.prog("w_sun", t, 0.3, 1.0) * 0.5 + tl.prog("w_look", t, 0.0, 1.0) * 0.5)
    rbk *= 1 - 0.5 * tl.prog("w_flash", t, 0.0, 0.5)
    P.rainbow(c, RB[0], RB[1], RB[2], rbk, 16)
    # rain: heavy, then lighter when the sun comes out, then stops
    rk = 1.0 - 0.6 * tl.prog("w_sun", t, 0.0, 0.5) - 0.4 * tl.prog("w_purpose", t, 0.0, 1.0)
    P.rain(c, t, RAIN_BOX, 90, rk * ease(tl.prog("w_open", t, 0.0, 0.5)))
    # Sir Rufus back on the vane
    ang = vane_angle(tl, t, [("w_open", 0.0, 0.8, 1), ("w_byeact", 0.0, 0.6, 2)])
    r_eyes = "happy" if T("w_laugh") <= t < T("w_flash") else "proud" if T("w_sun") <= t < T("w_sun", 1) else "open"
    flap = 0.7 * (1 - abs(math.sin(t * 6))) if T("w_sun") <= t < T("w_sun", 1) or T("w_bye") <= t else 0.0
    tx, ty = draw_rufus(c, tl, t, ang, flap, r_eyes, look=(1, 0.5))
    # rooster counting: 1, 2, 3
    for i, f in enumerate((0.42, 0.62, 0.82)):
        nk = ten(tl, t, "w_count", f, f + 0.08, "w_thunder", 0.0, 0.2)
        if nk > 0.01:
            c.push(tx + 120 + i * 70, ty - 60, pop(nk))
            c.circle(0, 0, 28, (255, 255, 255), w=3)
            K.text(c, 0, 1, str(i + 1), 34, (226, 70, 80))
            c.pop()
    # rumble, far away
    rmk = tl.prog("w_rumble", t, 0.0, 1.0)
    if 0 < rmk < 1:
        c.push(STORM[0] + 4 * math.sin(t * 40), STORM[1] - 110, 1.0)
        K.text(c, 0, 0, "rumble... rumble...", 30, (90, 90, 120), stroke=3, stroke_fill=(255, 255, 255))
        c.pop()
    # Hazel under a big leaf umbrella
    hk = 1.0
    P.hazel(c, HAZ[0], HAZ[1], 1.0, -1, t, tl.mouth("hazel", t), "happy" if T("w_laugh") <= t < T("w_flash") else "open",
            look=(-1, 0))
    if rk > 0.3:
        c.push(HAZ[0] - 10, HAZ[1] - 130, 1.0)
        c.poly([(-60, 10), (-30, -24), (20, -30), (60, 6), (0, 0)], (200, 110, 40), w=2.5)
        c.line([(0, 0), (6, 60)], (120, 80, 40), 3)
        c.pop()
    # the friends: Whiskers sits apart so he can turn round on his own
    x, y = SPOT
    turn = tl.prog("w_rainbow", t, 0.05, 0.25)
    w_face = 1 if turn < 0.5 else -1
    look_rb = {"luna": (-1, -1), "pip": (-1, -1)}
    face_crew = 1
    if T("w_sun", 0.4) <= t < T("w_byeact"):
        face_crew = -1
    if T("w_flash") <= t < T("w_byeact"):
        look_rb = {"luna": (1, -0.6), "pip": (1, -0.6)}
        face_crew = 1
    gk = ease(tl.prog("w_byeact", t, 0.3, 1.0))
    yy = y - 520 * gk
    xx = x + 300 * gk
    eyes = {}
    extra = {}
    if T("w_flashq") <= t < T("w_flashq", 1):
        eyes = {"pip": "wide"}
    if T("w_laugh") <= t < T("w_flash"):
        eyes = {"luna": "happy", "pip": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}}
    if gk > 0:
        K.crew(c, tl, t, xx, yy, CREW_F, 1, fly=1.0, eyes={"whiskers": "happy"}, look={"luna": (1, -1), "pip": (1, -1)})
    else:
        K.crew(c, tl, t, xx, yy, CREW_F, face_crew, fly=0.0, who=("luna", "pip"), eyes=eyes, look=look_rb,
               extra=extra)
        # Whiskers on his own spot of the cushion, facing the sun until he turns
        wx = xx - 52 * CREW_F * face_crew
        wy = yy - 40 * CREW_F
        ws = 0.62 * CREW_F
        sunglasses = T("w_look", 0.75) <= t < T("w_byeact")
        staring = T("w_look", 0.5) <= t < T("w_rainbow", 0.1)
        w_eyes = "closed" if staring else "wide" if T("w_rainbow", 0.1) <= t < T("w_purpose") else "open"
        lying = T("w_purpose", 0.5) <= t < T("w_byeact")
        if lying:
            kat(c, tl, t, "whiskers", wx, wy + 4, ws, 1, "sleep")
            # sunglasses on his sleeping face
            c.push(wx, wy + 4, ws)
            for ex in (36, 58):
                c.ellipse(ex, -44, 10, 8, (30, 30, 40), w=2)
            c.line([(46, -46), (48, -46)], OUT, 3)
            c.pop()
        else:
            look_w = (1, -1) if staring else (w_face, -0.4)
            kat(c, tl, t, "whiskers", wx, wy, ws, w_face, "sit", eyes=w_eyes, look=look_w, head_dy=-4 if staring else 0)
            if sunglasses:
                P2.sunglasses(c, wx, wy, ws, w_face, "sit", -4 if staring else 0, tl.prog("w_look", t, 0.75, 0.95))
        if staring:
            for k in range(2):
                c.push(wx + 50 + k * 40, wy - 130 - 10 * math.sin(t * 5 + k), 1.0)
                K.text(c, 0, 0, "?", 34, (255, 255, 255), stroke=3)
                c.pop()
    # teaching: rain comes from clouds (the water cycle, with Drip)
    ck = ten(tl, t, "w_drip", 0.25, 0.4, "w_sun", 0.0, 0.2)
    if ck > 0.01:
        ks = [clamp(tl.prog("w_drip", t, 0.3, 1.0) * 1.3 - 0.0), clamp(tl.prog("w_drip", t, 0.3, 1.0) * 1.3 - 0.2),
              clamp(tl.prog("w_drip", t, 0.3, 1.0) * 1.3 - 0.35), clamp(tl.prog("w_dripact", t) * 1.5)]
        du = (tl.prog("w_drip", t, 0.3, 1.0) * 0.8 + tl.prog("w_dripact", t) * 0.4) % 1.0
        K.inset(c, 700, 250, 680, 400, ck, lambda ic: P5.cycle_scene(ic, t, ks, du))
    # teaching: sun behind you + rain in front = rainbow
    lk = ten(tl, t, "w_rainbow", 0.3, 0.5, "w_laugh", 0.5, 1.0)
    if lk > 0.01:
        sx, sy = P.SUNS["autumn"][:2]
        for j in range(3):
            K.arrow(c, sx - 60, sy + 30 + j * 26, lerp(sx - 60, 420, lk), lerp(sy + 30 + j * 26, 380 + j * 30, lk),
                    (255, 236, 120), 6, 1.0, head=16)
        K.label(c, 760, 70, "Sun behind you + rain in front = rainbow!", 30, k=lk, col=(40, 100, 170))
    tk = ten(tl, t, "w_turn", 0.1, 0.3, "w_rainbow", 0.2, 0.4)
    K.label(c, wx_safe(xx) - 30, yy - 200, "Turn around!", 30, k=tk)
    # teaching: light is faster than sound
    ik = ten(tl, t, "w_thunder", 0.15, 0.3, "w_bye", 0.2, 0.5)
    if ik > 0.01:
        sk = tl.prog("w_thunder", t, 0.25, 0.95)
        K.inset(c, 700, 230, 640, 280, ik, lambda ic: light_sound_inset(ic, t, sk))
    K.sub_band(c, tl, t)
    K.flash(c, fl * 0.35)
    K.flash(c, tl.prog("w_byeact", t, 0.85, 1.0))
    return c


def wx_safe(x):
    return x - 52 * CREW_F


def light_sound_inset(ic, t, k):
    """A race: the flash zooms straight to you; the rumble's sound waves come slowly after."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (150, 160, 190)), (1, (220, 226, 240))]), (0, 0))
    P.storm_cloud(ic, 90, 110, 0.9, 1.0 if (t * 2) % 1 < 0.15 else 0.4)
    # the listener: Pip's ear
    ic.circle(w - 70, 140, 34, (176, 156, 142), w=3)
    ic.circle(w - 70, 140, 20, (255, 176, 186), ol=None)
    # lane 1: light, very fast
    lx = lerp(170, w - 120, clamp(k * 6))
    K.arrow(ic, 170, 80, lx, 80, (255, 226, 60), 10, 1.0, head=22)
    K.text(ic, 330, 46, "Light: super fast!", 26, (48, 40, 60))
    # lane 2: sound, slower
    sx = lerp(170, w - 120, clamp(k * 1.2))
    for j in range(4):
        xx = sx - j * 34
        if xx > 170:
            ic.arc(xx, 200, 18, 34, -60, 60, (70, 70, 110), 5)
    K.text(ic, 330, 250, "Sound: slower...", 26, (48, 40, 60))


# ==================================================================== remember

FACTS = ["There are four seasons: spring, summer, autumn and winter.",
         "We have seasons because the Earth is tilted.",
         "A rainbow needs sun and rain together."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_seasons, P.icon_tilt, P.icon_rainbow], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Why do we have seasons?", ["Closer to the Sun", "The Earth is tilted"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_closer, P.icon_tilt], number=1, answer_text="The Earth is tilted!")
    else:
        c = K.quiz_card(t, "What makes a rainbow?", ["Snow and wind", "Sun and rain"], 1,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.icon_snow_wind, P.icon_sun_rain], number=2, answer_text="Sun and rain, together!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def home(tl, t):
    T = tl.t
    c = Canvas(autumn_home("evening").copy())
    window_leaves(c, t, 0.6, 0.2)
    lon = sill_globe_lon(t, [(T("h_pip", 0.3), 300)])
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    # Luna's globe is tilted too: show its leaning axis
    ak = ten(tl, t, "h_pip", 0.3, 0.5, "h_nap", 0.0, 0.3)
    if ak > 0.01:
        gx, gy = K.GLOBE_X, SY - 170
        nx, ny, _ = K.globe_xy(gx, gy, 100, 0, 90, lon, 18, -23.5)
        ux, uy = nx - gx, ny - gy
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        for j in range(-7, 8, 2):
            a0, a1 = j * 20, (j + 1) * 20
            c.line([(gx + ux * a0, gy + uy * a0), (gx + ux * a1, gy + uy * a1)], (226, 70, 80), 4 * ak)
        for j in range(-6, 7, 2):
            c.line([(gx, gy + j * 20), (gx, gy + (j + 1) * 20)], (255, 255, 255), 3 * ak)
        K.label(c, gx + 200, gy - 140, "Tilted, like the Earth!", 28, tip=(gx + ux * 150 + 6, gy + uy * 150), k=ak)
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
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Day and Night", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "farm": farm, "orbit": orbit, "weather": weather,
               "remember": remember, "quiz": quiz, "home": home}
