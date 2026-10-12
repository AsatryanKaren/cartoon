"""Scenes of Episode 3 "The Five Oceans". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py; the tinted oceans,
Bluebell, Nipper and the diagrams come from props.py.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e03_five_oceans import props as P

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


def note(c, x, y, k, col=(255, 255, 255)):
    """A little music note."""
    if k <= 0.05:
        return
    c.push(x, y, 0.6 + 0.4 * k)
    c.ellipse(0, 0, 9, 7, col, w=2.5)
    c.line([(8, -2), (8, -34), (20, -26)], OUT, 3)
    c.pop()


def song_notes(c, x, y, t, k=1.0, n=4, col=(255, 255, 255)):
    if k <= 0.01:
        return
    for i in range(n):
        u = (t * 0.45 + i / n) % 1
        note(c, x + 40 * math.sin(u * 5 + i) + i * 24, y - 150 * u, (1 - u) * k, col)


# ======================================================================= title

def title(tl, t):
    c = K.title_card(tl, t, 0.0, 3, "The Five Oceans")
    K.sub_band(c, tl, t)
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


def bath_bubble(c, t, k):
    """Whiskers imagines the globe in a bubble bath."""
    if k <= 0.01:
        return
    x, y = 300, 200
    K.bubble(c, x, y, 120, 84, k, tail=(250, 380))
    if k < 0.6:
        return
    c.push(x, y + 10, k)
    c.rect(-80, -6, 80, 40, (240, 244, 250), r=16, w=3)
    for fx in (-64, 64):
        c.rect(fx - 6, 36, fx + 6, 50, (200, 170, 90), r=3, w=2)
    K.globe(c, 6, -30, 34, lon=-t * 40, lat=15, style="toy")
    for i in range(7):
        bx = -70 + i * 23
        c.circle(bx, -6 - 6 * math.sin(i * 2.1), 12 + 3 * math.sin(t * 3 + i), (255, 255, 255), w=2)
    # rubber duck
    c.ellipse(-50, -22, 14, 10, (255, 214, 60), w=2)
    c.circle(-40, -36, 8, (255, 214, 60), w=2)
    c.poly([(-33, -36), (-24, -34), (-33, -31)], (250, 140, 40), w=1.5)
    c.pop()


def five_card(ic, t):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (120, 190, 250)), (1, (60, 140, 220))]), (0, 0))
    P.icon_five(ic, w / 2, h / 2 - 14, 74, t)
    K.text(ic, w / 2, h - 26, "5 big oceans", 28, (255, 255, 255), stroke=3)


def sill(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("day").copy())
    spins = [(T("s_open", 0.15), 260), (T("s_sea", 0.3), 200), (T("s_hold", 0.3), 360), (T("s_glow"), 900)]
    lon = sill_globe_lon(tl, t, spins)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=glow_k, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170

    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    cush_spots = {"luna": (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), "pip": (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S)}
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        w_eyes = "open"
        if T("s_five") <= t < T("s_five2", 1):
            w_eyes = "wide"
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.5))
        lean = -8 * math.exp(-max(0, t - T("s_sea", 0.3)) * 3) if t > T("s_sea", 0.3) else 0
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", head_dy=lean, look=(-1, -0.4))
        kat(c, tl, t, "pip", PIP_X, SY, 1.1, 1 if t < T("s_pip") else -1, proud=tl.talking("pip", t))
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
    kb = tl.prog("s_blue", t, 0.45, 0.7) * (1 - tl.prog("s_sea", t, 0.3, 0.6))
    bath_bubble(c, t, kb)
    kg = tl.prog("s_sea", t, 0.2, 0.45) * (1 - tl.prog("s_five", t, 0.0, 0.2))
    K.label(c, 860, 200, "Blue = water", 30, tip=(gcx + 70, gcy - 50), k=kg)
    kf = tl.prog("s_five", t, 0.35, 0.6) * (1 - tl.prog("s_hold", t, 0.0, 0.3))
    if kf > 0.01:
        K.inset(c, 960, 175, 320, 250, kf, lambda ic: five_card(ic, t))
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, gcx, gcy, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ========================================================================= map

HOME = (2, 48.5)
MEET = (-150, 12)
GO_PATH = [HOME, (-30, 44), (-80, 36), (-122, 24), MEET]
GLOBE_R = 230
ORDER = [("m_pac", "pacific"), ("m_atl", "atlantic"), ("m_ind", "indian"), ("m_arc", "arctic"),
         ("m_sou", "southern")]


def globe_keys(tl):
    T = tl.t
    lon = [(T("m_fly"), 30), (T("m_narr", 1), -80), (T("m_turn1", 0.9), -165), (T("m_half", 1), -172),
           (T("m_turn2", 0.9), -32), (T("m_atl", 1), -28), (T("m_turn3", 0.9), 78), (T("m_ind", 1), 82),
           (T("m_turn4", 0.9), 30), (T("m_arc", 1), 26), (T("m_turn5", 0.9), 60), (T("m_sou", 1), 64),
           (T("m_count", 1), 40), (T("m_five", 1), 0)]
    lat = [(T("m_fly"), 15), (T("m_turn1", 0.9), 2), (T("m_turn2", 0.1), 2), (T("m_turn2", 0.9), 12),
           (T("m_turn3", 0.1), 12), (T("m_turn3", 0.9), -14), (T("m_turn4", 0.1), -14), (T("m_turn4", 0.9), 66),
           (T("m_turn5", 0.1), 66), (T("m_turn5", 0.9), -64), (T("m_count", 0.2), -64), (T("m_five", 1), 0)]
    return lon, lat


def hl_ks(tl, t):
    return {name: tl.prog(ev, t, 0.0, 0.2) for ev, name in ORDER}


def tally(c, tl, t, k=1.0):
    """Panel on the left listing the oceans as they are named (Pip counts them at the end)."""
    if k <= 0.01:
        return
    T = tl.t
    x0, y0 = lerp(-320, 30, ease_out(k)), 120
    shown = [i for i, (ev, _) in enumerate(ORDER) if t >= T(ev)]
    if not shown:
        return
    hgt = 62 * len(shown) + 26
    c.rect(x0 + 6, y0 + 8, x0 + 296, y0 + hgt + 8, (12, 12, 34), ol=None, r=22)
    c.rect(x0, y0, x0 + 290, y0 + hgt, (255, 252, 242), r=22, w=4)
    counted = sum(1 for f in (0.02, 0.2, 0.42, 0.6, 0.78) if t >= T("m_five", f)) if t >= T("m_five") else 0
    for i in shown:
        ev, name = ORDER[i]
        y = y0 + 44 + 62 * i
        kk = tl.prog(ev, t, 0.0, 0.15)
        lit = i < counted
        c.push(x0 + 42, y, pop(kk) * (1.18 if lit and i == counted - 1 and t < T("m_five", 1) else 1.0))
        c.circle(0, 0, 22, P.OCOL[name], w=3)
        K.text(c, 0, 1, str(i + 1) if lit or t >= T("m_five") else "", 26, (40, 50, 80))
        c.pop()
        K.text(c, x0 + 80, y, P.SHORT[name], 32, (48, 40, 60) if not lit else (40, 100, 190), anchor="lm")


def map_(tl, t):
    T = tl.t
    if t < T("m_flat"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        lon_k, lat_k = globe_keys(tl)
        lon = K.smooth(t, lon_k, 0.35)
        lat = K.smooth(t, lat_k, 0.35)
        k = ease_out(tl.prog("m_fly", t, 0.0, 1.0) * 0.5 + tl.prog("m_narr", t) * 0.5)
        mk = ease(tl.prog("m_five", t, 0.3, 1.0))
        r = lerp(60, GLOBE_R, k)
        gx, gy = lerp(lerp(800, 720, k), 640, mk), lerp(330, 360, mk)
        hl = hl_ks(tl, t)
        P.ocean_globe(c, gx, gy, r, lon, lat, hl, t, glow=0.5)
        # name tag on the ocean being shown
        turns = ["m_turn2", "m_turn3", "m_turn4", "m_turn5", "m_count"]
        for i, (ev, name) in enumerate(ORDER):
            kk = tl.prog(ev, t, 0.05, 0.25) * (1 - tl.prog(turns[i], t, 0.0, 0.15))
            if kk > 0.01:
                lx, ly, vis = K.globe_xy(gx, gy, r, P.LAB[name][0], P.LAB[name][1], lon, lat)
                if not vis:
                    lx, ly = gx, gy
                tx, ty = (gx + 300, gy - 210) if lx >= gx - 40 else (gx - 300, gy - 210)
                tx = clamp(tx, 360, 1130)
                K.label(c, tx, ty, P.NAMES[name], 34, tip=(lx, ly), k=kk, col=(30, 60, 120))
        kh = tl.prog("m_half", t, 0.1, 0.3) * (1 - tl.prog("m_turn2", t, 0.0, 0.2))
        K.label(c, gx, 60, "Almost half the world!", 30, k=kh, col=(150, 110, 0))
        kf = tl.prog("m_five", t, 0.8, 1.0)
        if kf > 0.01:
            c.push(gx, gy, pop(kf))
            K.text(c, 0, 0, "5!", 120, (255, 236, 110), stroke=6)
            c.pop()
        tally(c, tl, t, tl.prog("m_pac", t, 0.0, 0.2))
        fk = ease_out(tl.prog("m_fly", t, 0.0, 0.8))
        x = lerp(-200, 170, fk)
        y = lerp(820, 662, fk)
        K.crew(c, tl, t, x, y, 0.72, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)},
               eyes={"whiskers": "wide"} if t < T("m_pac") else None)
        K.flash(c, 1 - tl.prog("m_fly", t, 0.0, 0.3))
    elif t < T("m_join"):
        c = Canvas(K.space_bg().copy())
        K.twinkle(c, t)
        k = tl.prog("m_flat", t, 0.05, 0.85)
        if k < 1:
            P.globe_to_map(c, k, GLOBE_R, 0.0, t)
        else:
            v = K.MapView(0, 0, 1)
            K.draw_map(c, v)
            for name in P.OCEANS:
                P.ocean_highlight(c, v, name, 1.0, t)
            K.map_labels(c, v, "oceans", tl.prog("m_flat", t, 0.85, 1.0))
        K.label(c, 640, 46, "The map: all five oceans", 28, k=tl.prog("m_flat", t, 0.3, 0.45))
        K.crew(c, tl, t, 170, 662, 0.72, 1, fly=1.0, look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    else:
        c = map_scene(tl, t)
    K.sub_band(c, tl, t)
    return c


JOINS = [((-120, -44), (-112, -62)), ((-28, -40), (-24, -62)), ((84, -44), (88, -62)),
         ((-14, 58), (-8, 74)), ((-172, 56), (-170, 70)), ((122, -6), (134, 2)), ((28, -38), (8, -40))]


def map_scene(tl, t):
    T = tl.t
    pk = tl.prog("m_path", t, 0.3, 1.0)
    cam = K.lerp_view((0, 0, 1.0), (MEET[0] + 10, MEET[1], 2.4), ease(pk))
    c, v = K.map_view(*cam, t=t)
    fade = 1 - tl.prog("m_path", t, 0.0, 0.3)
    for name in P.OCEANS:
        P.ocean_highlight(c, v, name, 1.0 if name == "pacific" else fade, t)
    K.map_labels(c, v, "oceans", 1 - tl.prog("m_path", t, 0.4, 0.6))
    # the oceans are all joined up
    jk = tl.prog("m_join", t, 0.2, 0.5) * fade
    if jk > 0.01:
        for i, (a, b) in enumerate(JOINS):
            ax, ay = v.xy(*a)
            bx, by = v.xy(*b)
            kk = clamp(jk * 2 - i * 0.12)
            ph = 0.5 + 0.5 * math.sin(t * 4 + i)
            K.arrow(c, ax, ay, bx, by, (255, 255, 255), 6, kk, head=14)
            K.arrow(c, bx, by, ax, ay, (255, 255, 255), 6, kk, head=14)
            K.sparkles(c, (ax + bx) / 2, (ay + by) / 2, 30, t, 3, kk * ph, seed=i + 40)
        K.label(c, 640, 46, "One big world ocean!", 30, k=jk, col=(30, 90, 170))
    # Whiskers dreams of napping on the biggest ocean
    bk = tl.prog("m_vote", t, 0.2, 0.4) * (1 - tl.prog("m_path", t, 0.0, 0.2))
    if bk > 0.01:
        K.bubble(c, 330, 410, 120, 70, bk, tail=(170, 590))
        if bk > 0.6:
            c.push(330, 430, bk)
            c.ellipse(0, 10, 100, 20, (64, 146, 222), w=3)
            for j in range(3):
                c.arc(-60 + 60 * j, 14, 12, 5, 200, 340, (200, 230, 255), 3)
            K.cushion(c, 0, 4, 0.45, t)
            D.cat(c, 0, -14, D.WHISKERS, 0.45, 1, "sleep", t=t)
            D.zzz(c, 20, -40, t)
            c.pop()
    # home pin + dotted path + the cushion flying along it
    hx, hy = v.xy(*HOME)
    hk = tl.prog("m_vote", t, 0.8, 1.0) * (1 - tl.prog("m_path", t, 0.7, 0.85))
    K.you_are_here(c, hx, hy, t, hk, "Home" if t < T("m_path", 0.3) else "", size=24)
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.15, 0.8)
        K.map_path(c, v, GO_PATH, max(u, 0.0001), head=u > 0.02)
        if t >= T("m_path", 0.1):
            x, y, ang = K.path_point(v, GO_PATH, u)
            K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, -1 if math.cos(ang) < 0 else 1, fly=1)
        dk = tl.prog("m_path", t, 0.8, 0.95)
        if dk > 0:
            mx, my = v.xy(*MEET)
            K.label(c, mx + 40, my - 120, "Middle of the Pacific", 30, tip=(mx, my - 30), k=dk, col=(30, 90, 170))
    if t < T("m_path", 0.25):
        sk = ease(tl.prog("m_path", t, 0.0, 0.25))
        x = lerp(170, hx, sk)
        y = lerp(662, hy + 6, sk)
        s = lerp(0.72, 0.16, sk)
        eyes = {"whiskers": "happy"} if T("m_vote") <= t < T("m_path") else {}
        K.crew(c, tl, t, x, y, s, 1, fly=1.0, eyes=eyes,
               look={"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)})
    return c


# ========================================================================= sea

HORIZON = 300
WL = 590
CUSH = (330, WL - 4)
WHALE = (930, WL - 30)
WHALE_S = 0.95


def sea_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (96, 170, 238)), (HORIZON / H, (210, 236, 255)),
                                               (HORIZON / H + 0.001, (100, 178, 234)), (1, (34, 100, 180))]))
        c.glow(1080, 100, 220, 160, (255, 250, 210), (150, 205, 248), steps=10)
        c.circle(1080, 100, 46, (255, 232, 120), ol=None)
        D.cloud(c, 210, 100, 0.9)
        D.cloud(c, 600, 66, 0.6)
        D.cloud(c, 820, 170, 0.5)
        c.line([(0, HORIZON), (W, HORIZON)], (240, 250, 255), 3, cap=False)
        for (x, y) in ((430, 150), (470, 136)):
            c.arc(x, y, 10, 6, 200, 340, OUT, 2)
            c.arc(x + 20, y, 10, 6, 200, 340, OUT, 2)
        return c.img
    return cached("sea", make)


def underwater(c, boxes, a=0.78, bg=None):
    """Blend the sea back over the lower parts of floating things (a = how hidden they are)."""
    bg = bg or sea_bg()
    for x0, y0, x1, y1 in boxes:
        box = (int(max(0, x0) * SS), int(max(0, y0) * SS), int(min(W, x1) * SS), int(min(H, y1) * SS))
        if box[2] > box[0] and box[3] > box[1]:
            if a >= 0.999:
                c.img.paste(bg.crop(box), box[:2])
            else:
                c.img.paste(Image.blend(c.img.crop(box), bg.crop(box), a), box[:2])


def waves(c, t, y0, y1, n_rows=6, col=(150, 206, 244), speed=30, seed=2, amp=1.0):
    """Animated little wave strokes in the band y0..y1 (amp makes them bigger)."""
    rng = np.random.default_rng(seed)
    for j in range(n_rows):
        f = j / max(1, n_rows - 1)
        y = lerp(y0, y1, f)
        scale = lerp(0.5, 1.3, f) * (0.7 + 0.5 * amp)
        off = (t * speed * scale * (1 if j % 2 else -0.7) + rng.uniform(0, 300)) % (160 * scale)
        x = -160 * scale + off
        while x < W + 60:
            pts = [(x + k * 6 * scale, y + math.sin(k * 0.9) * 3 * scale * amp) for k in range(7)]
            c.line(pts, col, 3 * scale)
            x += 160 * scale


def foam(c, x, w, t, y=WL):
    for k in range(5):
        dx = (k - 2) / 2 * w + 8 * math.sin(t * 3 + k)
        c.ellipse(x + dx, y + 2, 26 + 6 * math.sin(t * 4 + k * 2), 6, (230, 246, 255), ol=None)


def dino(c, x, y, s=1.0):
    """A big friendly dinosaur silhouette (for the size comparison). (x, y) = feet."""
    col = (120, 180, 100)
    c.push(x, y, s)
    c.poly([(-60, -70), (-170, -40), (-60, -50)], col, w=2.5)
    for lx in (-30, 20):
        c.rect(lx - 12, -60, lx + 12, 0, mix(col, (0, 0, 0), 0.12), r=6, w=2.5)
    c.ellipse(-10, -80, 70, 40, col, w=2.5)
    c.stroke([(40, -100), (64, -140), (76, -160)], col, 24)
    c.ellipse(90, -170, 30, 18, col, w=2.5)
    c.circle(100, -176, 3.5, OUT, ol=None)
    c.pop()


def size_inset(ic, t, k):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (180, 220, 250)), (1, (90, 160, 220))]), (0, 0))
    gy = h - 46
    ic.line([(0, gy), (w, gy)], (255, 255, 255), 3, cap=False)
    P.whale(ic, 190, gy - 52, 0.5 * pop(k), 1, t, look=(1, 0))
    dk = clamp(k * 2 - 0.6)
    if dk > 0:
        dino(ic, w - 150, gy, 0.75 * pop(dk))
        D.cat(ic, w - 40, gy, D.WHISKERS, 0.22 * pop(dk), -1, "sit", t=t)
    K.text(ic, 190, h - 22, "Blue whale", 24, (255, 255, 255), stroke=3)
    if dk > 0.5:
        K.text(ic, w - 150, h - 22, "Dinosaur", 22, (255, 255, 255), stroke=3)
        K.text(ic, w - 34, h - 22, "Whiskers", 18, (255, 255, 255), stroke=3)
    K.text(ic, w / 2, 26, "The biggest animal ever!", 28, (226, 70, 80), stroke=3, stroke_fill=(255, 255, 255))


def bleh(c, x, y, k, t):
    """Comic burst: BLEH!"""
    if k <= 0.01:
        return
    c.push(x, y, pop(k))
    pts = []
    for i in range(16):
        a = i * math.tau / 16
        r = 90 if i % 2 == 0 else 62
        pts.append((math.cos(a) * r * 1.3, math.sin(a) * r))
    c.poly(pts, (255, 236, 110), w=3)
    K.text(c, 0, 2, "BLEH!", 46, (60, 160, 70), stroke=3, stroke_fill=(255, 255, 255))
    c.pop()


def sea(tl, t):
    T = tl.t
    c = Canvas(sea_bg().copy())
    gust = tl.prog("sea_gust", t, 0.0, 0.6) * (1 - tl.prog("sea_dive", t, 0.0, 1.0) * 0.5)
    amp = 1 + 1.4 * ease(gust)
    waves(c, t, HORIZON + 14, WL - 40, 6, (150, 206, 244), 20 + 40 * gust, amp=amp)
    bob = (3 + 9 * gust) * math.sin(t * (2 + 1.5 * gust))
    down = ease(tl.prog("sea_down", t, 0.35, 1.0))
    # Bluebell: a dark shape under the water while she sings, then she rises
    rise = ease_out(tl.prog("sea_rise", t, 0.0, 0.6))
    if T("sea_song") <= t and rise <= 0:
        u = tl.prog("sea_song", t, 0.0, 1.0) * 0.5 + tl.prog("sea_what", t) * 0.5
        sx = lerp(1300, 980, ease(u))
        c.ellipse(sx, WL + 70, 330, 50, (40, 110, 186), ol=None)
        song_notes(c, sx - 100, WL - 30, t, tl.prog("sea_song", t, 0.1, 0.3))
    wy = lerp(WL + 230, WHALE[1], rise) + bob * 0.6 + down * 260
    laugh = (T("sea_laugh") <= t < T("sea_laugh", 1)) or (T("sea_laugh2") <= t < T("sea_laugh2", 1))
    if rise > 0:
        b_eyes = "happy" if laugh or (T("sea_big") <= t < T("sea_big", 0.5)) else "open"
        look = (-1, 0)
        if T("sea_thirst") <= t < T("sea_laugh"):
            look = (-1, 0.5)
        P.whale(c, WHALE[0], wy, WHALE_S, -1, t, tl.mouth("bluebell", t), b_eyes, look)
    # spouts
    bx, by = P.blowhole(WHALE[0], wy, WHALE_S, -1)
    P.spout(c, bx, by, tl.prog("sea_rise", t, 0.55, 1.0), 0.9, t)
    P.spout(c, bx, by, tl.prog("sea_hello", t, 0.0, 0.5), 0.6, t)
    # the friends on the floating cushion
    land = tl.prog("sea_land", t, 0.0, 0.5)
    cy = lerp(-120, CUSH[1], ease(land)) + bob + down * 260
    cs = 1.2
    sip = T("sea_thirst", 0.6) <= t < T("sea_bleh")
    jump = tl.prog("sea_bleh", t, 0.0, 0.5)
    eyes, look, extra = {}, {"luna": (1, 0), "whiskers": (1, 0), "pip": (1, 0)}, {}
    if laugh:
        eyes = {"luna": "happy", "pip": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}}
    if T("sea_rise", 0.4) <= t < T("sea_hello", 0.4):
        eyes.update({"luna": "wide", "pip": "wide", "whiskers": "wide"})
    if T("sea_purpose") <= t < T("sea_laugh2", 1):
        eyes["whiskers"] = "happy" if t >= T("sea_laugh2") else "closed"
    whisk_free = sip or (T("sea_bleh") <= t < T("sea_laugh"))
    if whisk_free:
        K.crew(c, tl, t, CUSH[0], cy, cs, 1, fly=1 - land, who=("luna", "pip"), eyes=eyes,
               look={"luna": (-1, 0.3), "pip": (-1, 0.3)}, extra=extra)
        if sip:
            # Whiskers crouches at the edge and laps the sea water
            wx = CUSH[0] - 150
            kat(c, tl, t, "whiskers", wx, cy - 30, 0.74, -1, "crouch",
                mouth=0.3 + 0.3 * math.sin(t * 18) if t >= T("sea_sip") else tl.mouth("whiskers", t),
                look=(1, 1))
            if t >= T("sea_sip"):
                for k in range(2):
                    u = (t * 1.5 + k / 2) % 1
                    c.ellipse(wx - 60, WL + 2, 20 + 50 * u, 4 + 8 * u, None,
                              ol=mix((255, 255, 255), (100, 170, 230), u), w=2)
        else:
            a = (CUSH[0] - 150, cy - 30)
            b = (CUSH[0] - 52 * cs, cy - 40 * cs)
            x, y = hop(a, b, jump, 220)
            kat(c, tl, t, "whiskers", x, y, 0.74, -1 if jump < 0.5 else 1, "leap" if 0.02 < jump < 0.98 else "sit",
                eyes="closed", mouth=0.9, squash=1.1)
            # salt flying off
            for i in range(5):
                u = (t * 2 + i / 5) % 1
                c.rect(x + 40 * math.cos(i * 1.3) * (1 + u) - 4, y - 80 - 50 * u - 4,
                       x + 40 * math.cos(i * 1.3) * (1 + u) + 4, y - 80 - 50 * u + 4, (255, 255, 255), w=1.5)
    else:
        if T("sea_purpose") <= t < T("sea_purpose", 1):
            extra = {**extra, "whiskers": {"proud": True}}
        K.crew(c, tl, t, CUSH[0], cy, cs, 1, fly=1 - land, eyes=eyes, look=look, extra=extra)
    # magic bubble before the dive
    mb = tl.prog("sea_down", t, 0.0, 0.3)
    if mb > 0:
        P.magic_bubble(c, CUSH[0], cy - 70, 170, t, mb)
    underwater(c, [(CUSH[0] - 230, WL + 2, CUSH[0] + 200, H), (WHALE[0] - 340, WL + 2, W, H)], 0.72)
    if land > 0.5 and down < 0.2:
        foam(c, CUSH[0], 140 * cs, t)
    if rise > 0.3 and down < 0.2:
        foam(c, WHALE[0] - 40, 260, t)
    waves(c, t, WL + 30, H - 20, 4, (160, 214, 248), 28 + 40 * gust, seed=7, amp=amp)
    sk = t - T("sea_land", 0.5)
    if 0 < sk < 1.0:
        for k in range(3):
            rr = 60 + 160 * sk + 40 * k
            c.ellipse(CUSH[0], WL + 4, rr, rr * 0.16, None, ol=mix((240, 250, 255), (100, 170, 230), sk), w=3)
    # wind streaks
    if gust > 0.01:
        rng = np.random.default_rng(11)
        for i in range(9):
            u = (t * 0.7 + rng.random()) % 1
            y = rng.uniform(60, 520)
            x = lerp(-300, W + 100, u)
            pts = [(x + j * 30, y + 10 * math.sin(j * 0.6 + t * 3)) for j in range(8)]
            c.line(pts, mix((255, 255, 255), (180, 220, 250), 0.3), 4)
    # singing
    if rise > 0.5:
        sing = max(tl.prog("sea_rise", t, 0.6, 1.0) * (1 - tl.prog("sea_hello", t, 0.3, 0.6)),
                   tl.prog("sea_dive", t, 0.4, 0.6))
        song_notes(c, WHALE[0] - 300, WL - 140, t, sing)
    # Whiskers' bleh
    bleh(c, CUSH[0] - 40, 300, tl.prog("sea_bleh", t, 0.0, 0.15) * (1 - tl.prog("sea_laugh", t, 0.6, 1.0)), t)
    # teaching insets
    kz = tl.prog("sea_big", t, 0.15, 0.35) * (1 - tl.prog("sea_thirst", t, 0.0, 0.2))
    if kz > 0.01:
        sk2 = tl.prog("sea_big", t, 0.2, 0.9)
        K.inset(c, 640, 160, 620, 260, kz, lambda ic: size_inset(ic, t, sk2))
    ks = tl.prog("sea_why", t, 0.4, 0.8) * (1 - tl.prog("sea_purpose", t, 0.6, 0.9))
    if ks > 0.01:
        k1 = tl.prog("sea_salt1", t, 0.0, 0.8)
        k2 = tl.prog("sea_salt2", t, 0.0, 0.8) * 0.8 + tl.prog("sea_saltact", t, 0.0, 0.5) * 0.2
        K.inset(c, 640, 180, 620, 320, ks, lambda ic: P.salt_diagram(ic, t, k1, k2))
    kw = tl.prog("sea_wind", t, 0.0, 0.2) * (1 - tl.prog("sea_dive", t, 0.0, 0.2))
    if kw > 0.01:
        wk = tl.prog("sea_wind", t, 0.2, 1.0) * 0.6 + tl.prog("sea_windact", t) * 0.4
        K.inset(c, 640, 170, 560, 290, kw, lambda ic: P.wind_diagram(ic, t, wk))
    K.sub_band(c, tl, t)
    K.flash(c, tl.prog("sea_down", t, 0.75, 1.0), (40, 110, 190))
    return c


# ======================================================================== deep

DEEP_LEVELS = 12


def deep_bg(level):
    def make():
        d = level / (DEEP_LEVELS - 1)
        top = mix((70, 160, 226), (8, 16, 44), d ** 0.8)
        bot = mix((24, 86, 168), (2, 6, 24), d ** 0.7)
        c = Canvas(D.gradient(W * SS, H * SS, [(0, top), (1, bot)]))
        return c.img
    return cached(("deep", level), make)


def deep_bg_at(d):
    f = clamp(d) * (DEEP_LEVELS - 1)
    i = int(f)
    j = min(DEEP_LEVELS - 1, i + 1)
    a = f - i
    if a < 0.05 or i == j:
        return deep_bg(i)
    if a > 0.95:
        return deep_bg(j)
    return Image.blend(deep_bg(i), deep_bg(j), a)


def depth_meter(c, d, k=1.0):
    """Depth gauge on the right: the marker goes down as they sink."""
    if k <= 0.01:
        return
    x, y0, y1 = 1210, 90, 520
    c.rect(x - 16, y0 - 6, x + 16, y1 + 6, (255, 255, 255), r=16, w=3)
    for i in range(10):
        f = i / 9
        c.rect(x - 11, lerp(y0, y1, f) - 2, x + 11, lerp(y0, y1, f) + 22, mix((120, 200, 250), (10, 20, 60), f),
               ol=None, r=4)
    y = lerp(y0, y1, clamp(d))
    c.poly([(x - 26, y), (x - 46, y - 14), (x - 46, y + 14)], (255, 214, 70), w=3)
    K.text(c, x, y0 - 30, "deep", 22, (255, 255, 255), stroke=3)


def deep(tl, t):
    T = tl.t
    d = K.smooth(t, [(T("d_open"), 0.0), (T("d_dark", 1), 0.75), (T("d_mount", 0.5), 1.0), (T("d_cosy", 1), 1.0),
                     (T("d_up", 0.9), 0.15)], 0.4)
    c = Canvas(deep_bg_at(d).copy())
    P.rays(c, 60 - 40 * t % 230, 0, H, t, k=clamp(1 - d * 1.6))
    # floating specks
    rng = np.random.default_rng(8)
    for i in range(46):
        x = (rng.uniform(0, W) + 8 * t * rng.uniform(-1, 1)) % W
        y = (rng.uniform(0, H) - t * rng.uniform(4, 14) - d * 300) % H
        c.circle(x, y, rng.uniform(1.2, 3), mix((220, 240, 255), (120, 150, 200), d), ol=None)
    # sea creatures: fish near the top, jellies in the middle, the angler down in the dark
    fk = clamp(1 - d * 1.5)
    if fk > 0.05:
        for i in range(7):
            x = (W + 200 - ((t * 90 + i * 60) % (W + 400)))
            y = 140 + 30 * (i % 3) + 10 * math.sin(t * 2 + i) - d * 400
            P.fish(c, x, y, 0.7, -1, t + i, (255, 180, 70) if i % 2 else (255, 120, 90))
    jk = clamp(1 - abs(d - 0.55) * 2.6)
    if jk > 0.05:
        for i, (jx, jy) in enumerate(((200, 260), (330, 160), (1080, 220))):
            P.jelly(c, jx, jy - (d - 0.55) * 500 + 10 * math.sin(t * 1.2 + i), 0.9, t + i,
                    [(240, 160, 220), (180, 170, 255), (140, 220, 240)][i])
    ak = tl.prog("d_lamp", t, 0.0, 0.3) * (1 - tl.prog("d_up", t, 0.0, 0.3))
    if ak > 0.01:
        ax = lerp(-150, 230, ease_out(ak))
        P.angler(c, ax, 330 + 10 * math.sin(t * 1.5), 1.0, 1, t, lamp=0.6 + 0.4 * abs(math.sin(t * 2)))
    # Bluebell swims, the friends ride along in their bubble
    sw = 6 * math.sin(t * 1.3)
    wx, wy = 520, 450 + sw
    if t < T("d_open", 0.6):
        wy += (1 - ease_out(tl.prog("d_open", t, 0.0, 0.6))) * -300
    P.whale(c, wx, wy, 0.58, 1, t, tl.mouth("bluebell", t), "happy" if t >= T("d_up") else "open", (1, -0.3))
    bx, by = 960, 400 + sw * 0.8
    if t < T("d_open", 0.6):
        by += (1 - ease_out(tl.prog("d_open", t, 0.0, 0.6))) * -300
    eyes = {}
    if T("d_dark") <= t < T("d_deep"):
        eyes = {"luna": "wide", "pip": "wide", "whiskers": "wide"}
    if T("d_cosy") <= t < T("d_up", 0.5):
        eyes = {"whiskers": "happy"}
    look = {"luna": (-1, 0), "pip": (-1, 0), "whiskers": (-1, 0)}
    if T("d_lamp") <= t < T("d_up"):
        look = {"luna": (-1, 0.3), "pip": (-1, 0.3), "whiskers": (-1, 0.3)}
    K.crew(c, tl, t, bx, by + 40, 0.62, -1, fly=0.0, eyes=eyes, look=look)
    P.magic_bubble(c, bx, by - 10, 120, t, 1.0)
    # bubbles rising from the blowhole
    for i in range(6):
        u = (t * 0.6 + i / 6) % 1
        c.circle(wx + 124 + 10 * math.sin(t * 3 + i), wy - 40 - u * 380, 4 + 6 * u, None,
                 ol=(200, 230, 255), w=2)
    if t >= T("d_up"):
        song_notes(c, wx + 160, wy - 70, t, tl.prog("d_up", t, 0.0, 0.2) * (1 - tl.prog("d_up", t, 0.7, 0.9)))
    depth_meter(c, d, 1.0)
    kd = tl.prog("d_dark", t, 0.2, 0.5) * (1 - tl.prog("d_deep", t, 0.1, 0.3))
    K.label(c, 960, 210, "Darker and darker...", 26, k=kd, col=(30, 40, 90))
    km = tl.prog("d_deep", t, 0.25, 0.45) * (1 - tl.prog("d_lamp", t, 0.0, 0.2))
    if km > 0.01:
        mk = tl.prog("d_deep", t, 0.5, 1.0) * 0.4 + tl.prog("d_mount", t, 0.0, 0.6) * 0.6
        K.inset(c, 560, 190, 600, 320, km, lambda ic: P.trench_diagram(ic, t, mk))
    K.sub_band(c, tl, t)
    K.flash(c, 1 - tl.prog("d_open", t, 0.0, 0.3), (40, 110, 190))
    K.flash(c, tl.prog("d_up", t, 0.8, 1.0), (255, 236, 210))
    return c


# ======================================================================= beach

B_HOR = 300
LOW, HIGH = 380, 492
MOON = (1060, 112)
ROCK_X = 1060
NIP = (1060, 560)
B_CUSH = (330, 640)
POST_X = 690


def beach_sky():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (92, 80, 168)), (0.25, (196, 120, 160)),
                                               (B_HOR / H, (255, 196, 140)), (B_HOR / H + 0.001, (90, 120, 190)),
                                               (1, (60, 96, 170))]))
        c.circle(260, B_HOR - 6, 40, (255, 214, 120), ol=None)
        c.line([(0, B_HOR), (W, B_HOR)], (255, 236, 210), 3, cap=False)
        rng = np.random.default_rng(2)
        for _ in range(30):
            c.circle(rng.uniform(0, W), rng.uniform(0, 150), rng.uniform(0.8, 1.8), (255, 250, 230), ol=None)
        D.cloud(c, 560, 90, 0.5, col=(250, 210, 220))
        return c.img
    return cached("beach", make)


def beach(tl, t):
    T = tl.t
    c = Canvas(beach_sky().copy())
    mg = tl.prog("b_moon", t, 0.1, 0.4) * (1 - tl.prog("b_bye", t, 0.0, 0.5))
    if mg > 0.01:
        K._halo(c, MOON[0], MOON[1], 40, mg, (255, 250, 210))
    D.moon(c, MOON[0], MOON[1], 40, sky=(120, 100, 170))
    # tide: the water's edge moves up and down the beach
    tk = tl.prog("b_tideact", t, 0.05, 0.42)
    tk2 = tl.prog("b_tideact", t, 0.58, 0.95)
    shore = lerp(LOW, HIGH, ease(tk) * (1 - ease(tk2)))
    waves(c, t, B_HOR + 10, shore - 16, 4, (130, 160, 220), 16)
    # Moon Fish on the water
    mfk = tl.prog("b_moonfish", t, 0.0, 0.3) * (1 - tl.prog("b_bye", t, 0.0, 0.3))
    if mfk > 0.01:
        D.moon_fish(c, 820, 330, t, 0.6 * pop(mfk))
    # Bluebell waves goodbye far away
    if t >= T("b_bye"):
        bk = tl.prog("b_bye", t, 0.0, 0.4)
        fx, fy = 860, B_HOR + 18
        c.push(fx, fy + 30 * (1 - ease_out(bk)), 0.35)
        wv = math.sin(t * 3) * 0.2
        c.poly([(0, 0), (-16, -50), (-70, -90 + 20 * wv), (-50, -60), (0, -40), (50, -60), (70, -90 - 20 * wv),
                (16, -50)], P.BODY, w=4)
        c.pop()
        c.rect(fx - 60, fy + 2, fx + 60, fy + 40, (90, 120, 190), ol=None)
        P.spout(c, fx - 120, fy, tl.prog("b_bye", t, 0.3, 1.0), 0.45, t)
        song_notes(c, fx - 40, fy - 40, t, bk * 0.8)
    # sand
    wet = [(0, shore + 30)] + [(x, shore + 30 + 6 * math.sin(x * 0.01)) for x in range(0, W + 1, 80)] + [(W, H), (0, H)]
    c.poly([(0, shore)] + [(x, shore + 4 * math.sin(x * 0.012 + t * 1.5)) for x in range(0, W + 1, 40)]
           + [(W, H), (0, H)], (210, 180, 130), ol=None)
    c.poly(wet, (240, 214, 160), ol=None)
    # foamy edge
    for x in range(-20, W + 40, 70):
        c.ellipse(x + 10 * math.sin(t * 2 + x), shore + 2, 40, 6, (240, 248, 255), ol=None)
    # shells
    for sx, sy in ((520, 620), (880, 680), (170, 560)):
        c.arc(sx, sy, 10, 8, 180, 360, (250, 200, 210), 3)
    # tide post with marks
    c.rect(POST_X - 9, 330, POST_X + 9, 540, (150, 100, 60), r=3, w=2.5)
    for my, lab in ((HIGH - 4, "high"), (LOW + 24, "low")):
        c.line([(POST_X - 9, my), (POST_X + 9, my)], (255, 255, 255), 3, cap=False)
    # water over the post's foot (tide in)
    if shore > 400:
        c.rect(POST_X - 12, 400, POST_X + 12, shore, (90, 120, 190), ol=None)
    # rock pool + Nipper's rock
    c.ellipse(900, 640, 110, 28, (110, 160, 210), w=3)
    c.ellipse(880, 636, 40, 6, (200, 230, 250), ol=None)
    c.poly([(ROCK_X - 110, 580), (ROCK_X - 80, 540), (ROCK_X - 20, 524), (ROCK_X + 60, 530), (ROCK_X + 110, 570),
            (ROCK_X + 120, 600), (ROCK_X - 116, 600)], (130, 120, 120), w=3)
    c.ellipse(ROCK_X - 30, 540, 30, 8, (160, 150, 150), ol=None)
    # Nipper
    laugh = T("b_laugh") <= t < T("b_bye", 0.3)
    snip = abs(math.sin(t * 12)) if (tl.talking("nipper", t) and t < T("b_hey", 1)) or laugh else 0.0
    nx = NIP[0] + 0 * t
    P.crab(c, nx, NIP[1] - 30, 0.8, -1, t, tl.mouth("nipper", t), "happy" if laugh else "open", snip,
           walk=t * 3 if T("b_hey") <= t < T("b_hey", 0.4) else 0.0)
    # the friends on the cushion on the sand
    eyes, extra = {}, {}
    look = {"luna": (1, 0), "whiskers": (1, -0.3), "pip": (1, 0)}
    if T("b_hey") <= t < T("b_hey", 0.6):
        eyes = {"whiskers": "wide", "pip": "wide", "luna": "wide"}
    if T("b_moon") <= t < T("b_moonfish"):
        look = {"luna": (1, -1), "whiskers": (1, -1), "pip": (1, -1)}
    if T("b_moonfish") <= t < T("b_laugh"):
        look["whiskers"] = (1, 0.3)
    if laugh:
        eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"}
        extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}}
    land = tl.prog("b_open", t, 0.0, 0.6)
    cx = B_CUSH[0]
    cy = lerp(-100, B_CUSH[1], ease(land))
    K.crew(c, tl, t, cx, cy, 1.1, 1, fly=1 - land, eyes=eyes, look=look, extra=extra)
    # labels and diagrams
    hk = tl.prog("b_tideact", t, 0.3, 0.4) * (1 - tl.prog("b_tideact", t, 0.55, 0.6))
    K.label(c, POST_X + 140, HIGH - 70, "High tide!", 30, tip=(POST_X + 12, HIGH - 4), k=hk, col=(30, 90, 170))
    lk = tl.prog("b_tideact", t, 0.85, 0.95) * (1 - tl.prog("b_pull", t, 0.3, 0.5))
    lk = max(lk, tl.prog("b_tide", t, 0.5, 0.7) * (1 - tl.prog("b_tideact", t, 0.0, 0.1)))
    K.label(c, POST_X + 140, LOW - 40, "Low tide", 30, tip=(POST_X + 12, LOW + 22), k=lk, col=(150, 90, 30))
    ck = tl.prog("b_tideact", t, 0.0, 0.1) * (1 - tl.prog("b_tideact", t, 0.92, 1.0))
    if ck > 0.01:
        clock(c, 1180, 230, 50 * pop(ck), tl.prog("b_tideact", t) * 12)
        K.text(c, 1180, 300, "hours go by", 22, (255, 255, 255), stroke=3)
    km = tl.prog("b_moon", t, 0.3, 0.5) * (1 - tl.prog("b_moonfish", t, 0.0, 0.2))
    if km > 0.01:
        mk = tl.prog("b_moon", t, 0.4, 1.0) * 0.5 + tl.prog("b_moonact", t, 0.0, 0.6) * 0.5
        K.inset(c, 560, 180, 560, 300, km, lambda ic: P.tide_diagram(ic, t, mk))
    K.sub_band(c, tl, t)
    K.flash(c, 1 - tl.prog("b_open", t, 0.0, 0.3), (255, 236, 210))
    return c


def clock(c, x, y, r, turns):
    if r < 2:
        return
    c.circle(x, y, r, (255, 252, 240), w=3)
    for i in range(12):
        a = i * math.tau / 12
        c.circle(x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, 2, OUT, ol=None)
    a = turns * math.tau - math.pi / 2
    c.line([(x, y), (x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7)], OUT, 4)
    a2 = turns * math.tau / 12 - math.pi / 2
    c.line([(x, y), (x + math.cos(a2) * r * 0.45, y + math.sin(a2) * r * 0.45)], OUT, 5)


# ==================================================================== remember

FACTS = ["There are five oceans.",
         "The Pacific is the biggest and deepest ocean.",
         "Sea water is salty."]


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [P.icon_five, P.icon_pacific, P.icon_salt], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "Which ocean is the biggest? The Atlantic, or the Pacific?",
                        ["Atlantic", "Pacific"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[P.icon_atlantic, P.icon_pacific], number=1, answer_text="The Pacific!")
    else:
        c = K.quiz_card(t, "Is sea water salty, or sweet?",
                        ["Salty", "Sweet"], 0,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[P.icon_salt, P.icon_sweet], number=2, answer_text="Salty!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

BOWL_X = 112


def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("evening").copy())
    spins = [(T("h_pip", 0.3), 300)]
    lon = sill_globe_lon(tl, t, spins)
    back = tl.prog("h_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    gcx, gcy = K.GLOBE_X, SY - 170
    drink = tl.prog("h_bowl", t, 0.0, 1.0)
    P.bowl(c, BOWL_X, SY, 1.0, 1.0 - 0.3 * drink)
    e = ease(back)
    x = lerp(gcx, CUSH_X, e)
    y = lerp(gcy + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    away = T("h_narr", 0.7) <= t < T("h_pip", 0.4)
    sleep = t >= T("h_curl", 0.2)
    look = {"luna": (1, -0.5), "pip": (1, -0.5)}
    if away:
        K.crew(c, tl, t, x, y, s, 1, fly=1 - back, who=("luna", "pip"), look={"luna": (-1, 0), "pip": (-1, 0)})
        j1 = tl.prog("h_narr", t, 0.7, 1.0)
        j2 = tl.prog("h_pip", t, 0.0, 0.4)
        seat = (CUSH_X - 52 * CREW_S, SY - 40 * CREW_S)
        spot = (BOWL_X + 92, SY)
        if j2 > 0:
            wx, wy = hop(spot, seat, j2, 90)
            kat(c, tl, t, "whiskers", wx, wy, CAT_S, 1, "leap" if j2 < 0.95 else "sit")
        elif j1 < 1:
            wx, wy = hop(seat, spot, j1, 90)
            kat(c, tl, t, "whiskers", wx, wy, CAT_S, -1, "leap" if j1 > 0.05 else "sit")
        else:
            kat(c, tl, t, "whiskers", spot[0], spot[1], CAT_S, -1, "crouch")
    else:
        extra = {"whiskers": {"pose": "sleep", "dy": 6}} if sleep else None
        K.crew(c, tl, t, x, y, s, 1, fly=1 - back, extra=extra, look=look)
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    K.flash(c, 0.6 * (1 - tl.prog("h_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("h_next", t, 0.0, 0.25), "Next time:", "Mountains and Volcanoes", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "map": map_, "sea": sea, "deep": deep, "beach": beach,
               "remember": remember, "quiz": quiz, "home": home}
