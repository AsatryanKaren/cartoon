"""Scenes of Episode 10 "Day and Night, Earth and Sun" (season finale). One function per scene:
(tl, t) -> Canvas. Animation is keyed to script event ids (tl.t("id", frac), tl.prog("id", t, a, b)).
The series look (home, globe, magic map, cards) comes from world/kit.py.
"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from world import kit as K
from world.kit import kat, pop, ease_out
from world.s1e10_day_night import props as P
from world.s1e01_our_planet import props as P1

try:                                   # cameos for the season recap (other episodes' guides)
    from world.s1e02_seven_continents import props as P2
except Exception:                      # pragma: no cover
    P2 = None
try:
    from world.s1e03_five_oceans import props as P3
except Exception:
    P3 = None
try:
    from world.s1e04_mountains_volcanoes import props as P4
except Exception:
    P4 = None
try:
    from world.s1e05_rivers_lakes import props as P5
except Exception:
    P5 = None
try:
    from world.s1e06_deserts import props as P6
except Exception:
    P6 = None
try:
    from world.s1e07_rainforests import props as P7
except Exception:
    P7 = None
try:
    from world.s1e08_frozen_poles import props as P8
except Exception:
    P8 = None
try:
    from films.prague import props as PR
except Exception:
    PR = None

CONTINUOUS = ("space",)          # the sill flashes white straight into space
EXTRA_CUTS = ()

TAU = 2 * math.pi
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


def hoot_mouth(tl, t):
    return tl.mouth("hoot", t)


def sun_for(lon0, lat0, dx, dy, dz=0.0):
    """(lon, lat) on a globe drawn with centre lon0/lat0 whose surface faces the view-space direction
    (dx right, dy up, dz toward the viewer) -- i.e. where to put the Sun overhead to light it from there."""
    n = math.sqrt(dx * dx + dy * dy + dz * dz) or 1
    x, y, z = dx / n, dy / n, dz / n
    p0 = math.radians(lat0)
    lat = math.degrees(math.asin(clamp(y * math.cos(p0) + z * math.sin(p0), -1, 1)))
    lon = lon0 + math.degrees(math.atan2(x, z * math.cos(p0) - y * math.sin(p0)))
    return lon, lat


def dizzy_stars(c, x, y, t, k=1.0, r=40):
    if k <= 0.02:
        return
    for i in range(4):
        a = t * 5 + i * TAU / 4
        K.star(c, x + math.cos(a) * r, y + math.sin(a) * r * 0.35, 9 * k, (255, 236, 110), ol=OUT)


# ======================================================================= title

def title(tl, t):
    return K.title_card(tl, t, 0.0, 10, "Day and Night, Earth and Sun")


# ======================================================================== sill

SY = K.SILL_Y
CUSH_X = 270
CREW_S = 1.45
CAT_S = 0.9
LUNA_X = 836
PIP_X = 478                      # on the book stack
BOOK_TOP = SY - 96
OWL_PERCH = (1066, SY - 76)
GCX, GCY = K.GLOBE_X, SY - 170
HOME = (2, 48.5)
HAWAII = (-157, 20.5)


def book_stack(c, x, y):
    for i, (w, h, col) in enumerate(((120, 34, (90, 140, 200)), (106, 30, (220, 90, 80)), (112, 32, (250, 200, 80)))):
        yy = y - sum(b for b in (34, 30, 32)[:i])
        dx = (-4, 6, -2)[i]
        c.rect(x - w / 2 + dx, yy - h, x + w / 2 + dx, yy, col, r=4, w=2.5)
        c.line([(x - w / 2 + dx + 8, yy - h / 2), (x + w / 2 + dx - 8, yy - h / 2)], (255, 255, 255), 2)


def sill_lon(tl, t):
    T = tl.t
    lon = 30.0 - 4 * t
    for ts, amount in ((T("s_open", 0.15), 220),):
        if t > ts:
            lon -= amount * (1 - math.exp(-(t - ts) / 0.9))
    # one full slow turn during s_turn
    lon -= 360 * ease(tl.prog("s_turn", t, 0.05, 0.9))
    lon -= 600 * ease(tl.prog("s_glow", t, 0.0, 1.0))
    return lon


def owl_flight(tl, t):
    """Professor Hoot's position on the sill scene: flying in during s_owl, then perched."""
    k = tl.prog("s_owl", t, 0.05, 0.75)
    if k <= 0:
        return None
    if k < 1:
        e = ease_out(k)
        x = lerp(1380, OWL_PERCH[0], e)
        y = lerp(60, OWL_PERCH[1], e) - 60 * math.sin(math.pi * e)
        return x, y, 1.0, 1
    return OWL_PERCH[0], OWL_PERCH[1], 0.0, 0


def sill(tl, t):
    T = tl.t
    c = Canvas(cached("dawn", lambda: K.home_bg("evening")).copy())
    book_stack(c, PIP_X, SY)
    torch_on = t >= T("s_torch", 0.85)
    dim = 0.38 * tl.prog("s_torch", t, 0.85, 1.0) * (1 - tl.prog("s_come", t, 0.3, 0.9))
    lon = sill_lon(tl, t)
    glow_k = ease(tl.prog("s_glow", t, 0.0, 0.5))
    hopk = tl.prog("s_glow", t, 0.08, 0.38)
    fly = tl.prog("s_glow", t, 0.4, 1.0)
    laugh = T("s_laugh") <= t < T("s_laugh", 1) or (T("s_nap", 0.75) <= t < T("s_laugh"))
    # the friends (drawn before the dimming so the globe + beam pop out of the dark)
    w_eyes = "open"
    if T("s_where") <= t < T("s_owl", 0.8):
        w_eyes = "open"
    if T("s_owl", 0.3) <= t < T("s_hello", 0.3):
        w_eyes = "wide"
    if laugh and t >= T("s_laugh"):
        w_eyes = "happy"
    owl_xy = owl_flight(tl, t)
    if hopk <= 0:
        K.cushion(c, CUSH_X, SY, CREW_S, t)
        kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes=w_eyes,
            look=(1, -0.5))
        lk = (-1, -0.2) if t < T("s_torch") else (-1, 0)
        kat(c, tl, t, "luna", LUNA_X, SY, CAT_S, -1, "sit", look=lk,
            eyes="happy" if laugh and t >= T("s_laugh") else "open")
        kat(c, tl, t, "pip", PIP_X - 6, BOOK_TOP, 1.05, 1, proud=tl.talking("pip", t),
            eyes="happy" if laugh and t >= T("s_laugh") else "open")
    else:
        luna_xy = hop((LUNA_X, SY), (CUSH_X + 46 * CREW_S, SY - 40 * CREW_S), hopk, 160)
        pip_xy = hop((PIP_X - 6, BOOK_TOP), (CUSH_X + 104 * CREW_S, SY - 40 * CREW_S), clamp(hopk * 1.3), 90)
        if hopk < 1:
            K.cushion(c, CUSH_X, SY, CREW_S, t)
            kat(c, tl, t, "whiskers", CUSH_X - 52 * CREW_S, SY - 40 * CREW_S, CAT_S, 1, "sit", eyes="wide")
            kat(c, tl, t, "luna", luna_xy[0], luna_xy[1], CAT_S, -1, "leap" if 0.05 < hopk < 0.95 else "sit")
            kat(c, tl, t, "pip", pip_xy[0], pip_xy[1], 1.05, -1)
        else:
            e = ease(fly)
            x = lerp(CUSH_X, GCX, e)
            y = lerp(SY, GCY + 40, e) - 80 * math.sin(math.pi * e)
            s = CREW_S * lerp(1, 0.15, e ** 1.5)
            K.crew(c, tl, t, x, y, s, 1, fly=min(1, fly * 3), eyes={"whiskers": "wide"},
                   look={"luna": (1, -1), "pip": (1, -1)})
    if dim > 0.01:
        K.flash(c, dim, (30, 26, 60))
    # the globe: lit by the torch from the left once it is on
    sun = (lon - 90 + 8, 0.0) if torch_on and t < T("s_come", 0.6) else None
    P.lit_old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, sun=sun, glow=glow_k, t=t)
    # Pip's torch and its beam
    if hopk <= 0:
        tx, ty = PIP_X + 30, BOOK_TOP - 46
        bk = tl.prog("s_torch", t, 0.85, 1.0) * (1 - tl.prog("s_come", t, 0.4, 0.8))
        if torch_on and bk > 0.01:
            P.beam(c, tx + 4, ty, -8, 150, 12, 120, bk)
        tk = tl.prog("s_torch", t, 0.4, 0.7)
        if tk > 0:
            P.torch(c, tx, ty, 0.95 * pop(tk), -8, 1.0 if torch_on else 0.0)
    # home dot on the little globe
    if torch_on and T("s_spin") <= t < T("s_come", 0.5):
        hx, hy, vis = K.globe_xy(GCX, GCY, 100, HOME[0], HOME[1], lon, 18, -23.5)
        if vis:
            c.circle(hx, hy, 7, (226, 56, 60), w=2.5)
    # Professor Hoot
    if owl_xy:
        ox, oy, flap, moving = owl_xy
        if T("s_glow", 0.4) <= t:
            e = ease(tl.prog("s_glow", t, 0.4, 1.0))
            ox, oy = lerp(OWL_PERCH[0], GCX + 30, e), lerp(OWL_PERCH[1], GCY, e) - 60 * math.sin(math.pi * e)
            flap = 1.0
        sc = 1.45 * (1 - 0.85 * ease(tl.prog("s_glow", t, 0.5, 1.0)))
        oeyes = "happy" if laugh and t >= T("s_laugh") else ("happy" if tl.talking("hoot", t) and
                                                             t < T("s_hello", 0.25) else "open")
        P.owl(c, ox, oy, sc, -1, t, hoot_mouth(tl, t), oeyes, flap, look=(-1, 0.2))
    # teaching moments
    if torch_on:
        kd = tl.prog("s_daynight", t, 0.05, 0.25) * (1 - tl.prog("s_come", t, 0.0, 0.2))
        kn = tl.prog("s_daynight", t, 0.5, 0.7) * (1 - tl.prog("s_come", t, 0.0, 0.2))
        K.label(c, GCX - 210, GCY - 150, "DAY", 34, tip=(GCX - 60, GCY - 40), k=kd, col=(200, 120, 20),
                bg=(255, 244, 190))
        K.label(c, GCX + 200, GCY - 160, "NIGHT", 34, tip=(GCX + 60, GCY - 40), k=kn, col=(255, 255, 255),
                bg=(60, 66, 140))
    kc = tl.prog("s_spin", t, 0.3, 0.5) * (1 - tl.prog("s_come", t, 0.0, 0.25))
    if kc > 0.01:
        hours = 24 * tl.prog("s_turn", t, 0.05, 0.9)
        K.label(c, 640, 50, "1 turn = 1 day = 24 hours", 32, k=kc)

        def dial(ic):
            ic.img.paste((250, 246, 236), (0, 0, ic.img.size[0], ic.img.size[1]))
            P.clock24(ic, 100, 96, 70, hours, t)
            K.text(ic, 100, 186, f"{int(hours)} hours" if hours < 23.9 else "24 hours!", 22, (48, 40, 60))
        K.inset(c, 1086, 180, 200, 210, kc, dial)
        # curved arrow around the globe while it turns
        ak = tl.prog("s_turn", t, 0.0, 0.2) * (1 - tl.prog("s_nap", t, 0.6, 1.0))
        if ak > 0.01:
            pts = [(GCX + math.cos(a) * 140, GCY + 120 + math.sin(a) * 26) for a in np.linspace(0.3, 2.8, 30)]
            c.line(pts, (255, 236, 110), 7)
            ex, ey = pts[-1]
            c.poly([(ex - 6, ey - 16), (ex - 22, ey + 2), (ex + 6, ey + 12)], (255, 236, 110), w=2.5)
    K.sub_band(c, tl, t)
    z = 1 + 2.5 * ease(tl.prog("s_glow", t, 0.55, 1.0))
    if z > 1.001:
        c = K.zoom(c, GCX, GCY, z)
    K.flash(c, tl.prog("s_glow", t, 0.8, 1.0))
    return c


# ======================================================================= space

EX, EY, ER = 520, 380, 228
LAT0 = 52
SUN_XY = (1250, 380)


def space_hour(tl, t):
    T = tl.t
    keys = [(T("p_fly"), 3.6), (T("p_watch", 1), 4.6), (T("p_turn1", 1), 6.2), (T("p_rise", 1), 7.4),
            (T("p_turn2", 1), 17.5), (T("p_set", 1), 18.6), (T("p_looks", 1), 20.0), (T("p_stop", 1), 20.6),
            (T("p_push", 0.25), 22.0), (T("p_push", 0.65), 46.0), (T("p_push", 0.8), 49.0),
            (T("p_purpose", 1), 54.0), (T("p_friend", 1), 56.0)]
    return K.smooth(t, keys, 0.35)


def lon_for_hour(hour):
    # Sun to the right: overhead at lon0 + 90; home (lon 2) has local time 12 + (2 - slon) / 15
    return 2 - 90 - (hour - 12) * 15


def earth_with_sun(c, x, y, r, lon0, lat0, glow=0.0):
    slon, slat = lon0 + 90, 0.0
    K.globe(c, x, y, r, lon=lon0, lat=lat0, sun=(slon, slat), glow=glow, glow_col=(150, 190, 255))
    return slon


def sunlight(c, k=1.0):
    """Soft sunlight streaming from the Sun on the right toward the Earth."""
    if k <= 0.01:
        return
    pts = [(SUN_XY[0] - 60, SUN_XY[1] - 170), (EX + 40, EY - ER - 20), (EX + 40, EY + ER + 20),
           (SUN_XY[0] - 60, SUN_XY[1] + 170)]
    P.soft_poly(c, pts, (255, 236, 160), 0.10 * k)
    for dy in (-120, 0, 120):
        K.arrow(c, SUN_XY[0] - 200, SUN_XY[1] + dy * 0.9, EX + ER + 50, EY + dy, (255, 226, 110), 6, k, head=18)


def space_crew_pos(tl, t):
    k = ease_out(tl.prog("p_fly", t, 0.0, 0.8))
    return lerp(1400, 1010, k), lerp(820, 640, k)


def space(tl, t):
    T = tl.t
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    hour = space_hour(tl, t)
    lon0 = lon_for_hour(hour)
    grow = ease_out(tl.prog("p_fly", t, 0.0, 1.0))
    r = lerp(120, ER, grow)
    P.sun(c, SUN_XY[0], SUN_XY[1], 150, t, face=True)
    K.label(c, 1090, 150, "The Sun", 28, tip=(1170, 250), k=tl.prog("p_wow", t, 0.05, 0.25)
            * (1 - tl.prog("p_watch", t, 0.6, 0.9)))
    sunlight(c, tl.prog("p_watch", t, 0.0, 0.3) * (1 - tl.prog("p_watch", t, 0.85, 1.0)) * 0.9)
    earth_with_sun(c, EX, EY, r, lon0, LAT0, glow=0.25)
    # day / night tags
    kt = tl.prog("p_wow", t, 0.3, 0.55) * (1 - tl.prog("p_watch", t, 0.7, 1.0))
    K.label(c, EX + 150, EY - ER - 20, "Day", 30, tip=(EX + 110, EY - 70), k=kt, col=(200, 120, 20),
            bg=(255, 244, 190))
    K.label(c, EX - 230, EY - ER, "Night", 30, tip=(EX - 120, EY - 60), k=kt, col=(255, 255, 255),
            bg=(60, 66, 140))
    # spin arrow
    ak = tl.prog("p_watch", t, 0.2, 0.5) * (1 - tl.prog("p_rise", t, 0.0, 0.2))
    if ak > 0.01:
        pts = [(EX + math.cos(a) * (ER + 34), EY + 40 + math.sin(a) * 60) for a in np.linspace(2.6, 0.5, 30)]
        c.line(pts, (255, 236, 110), 7)
        ex, ey = pts[-1]
        c.poly([(ex + 10, ey - 18), (ex - 10, ey + 6), (ex + 18, ey + 10)], (255, 236, 110), w=2.5)
        K.label(c, EX, EY + ER + 70, "It spins!", 28, k=ak)
    # home pin on the Earth
    hx, hy, vis = K.globe_xy(EX, EY, r, HOME[0], HOME[1], lon0, LAT0)
    hk = tl.prog("p_watch", t, 0.5, 0.8)
    push_k = tl.prog("p_push", t, 0.1, 0.9)
    if vis and hk > 0 and not (0 < push_k < 1):
        txt = ""
        if T("p_rise") <= t < T("p_turn2", 0.4):
            txt = "Sunrise!"
        elif T("p_set") <= t < T("p_looks", 0.6):
            txt = "Sunset!"
        elif t < T("p_rise"):
            txt = "Home"
        K.you_are_here(c, hx, hy, t, hk, txt, side=-1)
    # the sky at home (what we see as the Earth turns)
    sk = tl.prog("p_turn1", t, 0.0, 0.25) * (1 - tl.prog("p_friend", t, 0.0, 0.2))
    if sk > 0.01:
        K.inset(c, 1070, 118, 300, 196, sk, lambda ic: sky_inset(ic, hour, t))
    # Whiskers' mistake + the friends
    whiskers_gag(c, tl, t, r, lon0)
    # time zones at the end: two tags
    zk = tl.prog("p_friend", t, 0.15, 0.35)
    if zk > 0.01:
        K.label(c, EX + 250, EY + 150, "Day here", 26, tip=(EX + 140, EY + 60), k=zk, col=(200, 120, 20),
                bg=(255, 244, 190))
        K.label(c, EX - 250, EY + 170, "Night here", 26, tip=(EX - 140, EY + 60),
                k=tl.prog("p_friend", t, 0.4, 0.6), col=(255, 255, 255), bg=(60, 66, 140))
    K.flash(c, 1 - tl.prog("p_fly", t, 0.0, 0.3))
    K.flash(c, tl.prog("p_tomap", t, 0.5, 1.0), (255, 252, 235))
    K.sub_band(c, tl, t)
    return c


def sky_inset(ic, hour, t):
    P.sky_view(ic, hour % 24, t)
    w = ic.img.size[0] / SS
    K.text(ic, w / 2, 20, "The sky at home", 22, (255, 255, 255), stroke=3)


def whiskers_gag(c, tl, t, r, lon0):
    """The crew hovering in space; Whiskers jumps onto the North Pole to stop the Earth."""
    T = tl.t
    cx, cy = space_crew_pos(tl, t)
    pole = K.globe_xy(EX, EY, r, 0, 90, lon0, LAT0)
    u = tl.prog("p_push", t)
    laugh = T("p_laugh") <= t < T("p_laugh", 1)
    eyes = {"luna": "happy", "pip": "happy"} if laugh else {}
    look = {"luna": (-1, -0.6), "pip": (-1, -0.6), "whiskers": (-1, -0.6)}
    extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else {}
    w_on_cushion = u <= 0.04 or u >= 0.8 or t < T("p_push")
    who = ("whiskers", "luna", "pip") if w_on_cushion else ("luna", "pip")
    if t >= T("p_push", 0.8):
        dz = t < T("p_purpose")
        eyes["whiskers"] = "closed" if dz else ("happy" if laugh else "open")
    if T("p_stop") <= t < T("p_push"):
        eyes["whiskers"] = "wide"
    if T("p_push", 0.5) <= t < T("p_dizzy", 1):
        eyes["luna"] = "wide"
        eyes["pip"] = "wide"
    face = -1
    sc = 0.95
    if who == ("luna", "pip"):
        # crew() places two-rider layouts differently: keep Luna and Pip where they sit
        K.crew(c, tl, t, cx, cy, sc, face, fly=1, who=("luna", "pip", "whiskers"),
               eyes=eyes, look=look, extra={**extra, "whiskers": {"pose": "sit", "dy": 4000}})
    else:
        K.crew(c, tl, t, cx, cy, sc, face, fly=1, eyes=eyes, look=look, extra=extra)
    # Professor Hoot flapping beside them
    ok = ease_out(tl.prog("p_fly", t, 0.1, 0.9))
    ox, oy = lerp(1400, 1180, ok), lerp(700, 560, ok) + 8 * math.sin(t * 3)
    oeyes = "happy" if laugh else ("wide" if 0.4 < u < 0.8 else "open")
    P.owl(c, ox, oy, 1.0, -1, t, hoot_mouth(tl, t), oeyes, 1.0, look=(-1, -0.5))
    if t >= T("p_push", 0.8):
        hx, hy = cx + 52 * sc * 1.0, cy - 40 * sc - 110 * 0.62 * sc
        dizzy_stars(c, hx + 6, hy - 6, t, 1 - tl.prog("p_purpose", t, 0.2, 0.6), 34)
    if w_on_cushion:
        return
    # Whiskers' flight: jump to the pole, run in place, get flung off, tumble back
    seat = (cx + 52 * sc, cy - 40 * sc)
    stand = (pole[0], pole[1] + 4)
    if u < 0.16:
        k = (u - 0.04) / 0.12
        x, y = hop(seat, stand, k, 160)
        kat(c, tl, t, "whiskers", x, y, 0.62, -1, "leap", eyes="wide")
    elif u < 0.62:
        k = (u - 0.16) / 0.46
        run = t * (8 + 26 * k)
        jig = 3 * math.sin(run * 2)
        pose = "crouch" if k < 0.18 else "walk"
        kat(c, tl, t, "whiskers", stand[0], stand[1] + jig * 0.3, 0.62, -1, pose, walk=run,
            eyes="wide" if k > 0.5 else "open")
        if k > 0.25:
            for i in range(4):
                yy = stand[1] - 20 - 18 * i
                c.line([(stand[0] + 46, yy), (stand[0] + 46 + 40 + 20 * math.sin(t * 9 + i), yy)],
                       (255, 255, 255), 3, cap=False)
            if k > 0.5:
                for i in range(2):
                    dk = (t * 2 + i * 0.5) % 1
                    c.ellipse(stand[0] - 30 - 20 * dk + 50 * i, stand[1] - 90 + 30 * dk, 4, 6, (170, 210, 255),
                              w=1.5)
    else:
        k = (u - 0.62) / 0.18
        # flung up and around in a big loop, landing back on the cushion
        a0 = math.pi
        ang = lerp(0, TAU * 0.9, ease(k))
        mx, my = lerp(stand[0], seat[0], ease(k)), lerp(stand[1], seat[1], ease(k))
        x = mx + math.sin(ang) * 140 * math.sin(math.pi * k)
        y = my - 260 * math.sin(math.pi * k) + math.cos(ang + a0) * 30
        P.sprite(c, x, y - 50, 220, -720 * k,
                 lambda sc_, ox_, oy_: kat(sc_, tl, t, "whiskers", ox_, oy_ + 50, 0.62, -1, "leap", eyes="wide"))
        for i in range(5):
            kk = clamp(k - i * 0.04)
            c.circle(lerp(stand[0], x, kk), lerp(stand[1], y, kk) - 40, 6 - i, (255, 236, 110), ol=None)


# ========================================================================= map

PATH = [HOME, (-25, 47), (-60, 44), (-100, 38), (-130, 30), (-150, 23), HAWAII]
MAP_SLON = 2 - (8 - 12) * 15       # 8 o'clock in the morning at home


def map_(tl, t):
    T = tl.t
    pk = tl.prog("m_path", t, 0.25, 1.0)
    cam = K.lerp_view((-40, 10, 1.0), (HAWAII[0] + 20, HAWAII[1] + 6, 2.0), ease(pk))
    c, v = K.map_view(*cam, t=t)
    P.night_overlay(c, v, MAP_SLON, 0.0, ease(tl.prog("m_open", t, 0.1, 0.8)))
    K.map_clip(c, v)
    lab = 1 - tl.prog("m_path", t, 0.0, 0.2)
    # the Sun above the day side, the Moon above the night side
    sx, sy = v.xy(MAP_SLON, 0)
    nk = tl.prog("m_narr", t, 0.1, 0.4) * lab
    if nk > 0.01:
        P.sun(c, sx, 60, 30 * pop(nk), t, face=True, glow=False)
        K.label(c, sx, 118, "Day side", 26, k=nk, col=(200, 120, 20), bg=(255, 244, 190))
        mx, _ = v.xy(MAP_SLON - 180 + 360 if MAP_SLON - 180 < -180 else MAP_SLON - 180, 0)
        P.moon_phase(c, mx, 60, 26 * pop(nk), 0.5)
        K.label(c, mx, 118, "Night side", 26, k=tl.prog("m_narr", t, 0.4, 0.7) * lab, col=(255, 255, 255),
                bg=(60, 66, 140))
    # the two pins
    hx, hy = v.xy(*HOME)
    wx, wy = v.xy(*HAWAII)
    k1 = tl.prog("m_pins", t, 0.1, 0.4)
    k2 = tl.prog("m_pins", t, 0.5, 0.8)
    if k1 > 0:
        K.you_are_here(c, hx, hy, t, k1 * (1 - tl.prog("m_path", t, 0.4, 0.6)), "Home: morning!", side=1)
    if k2 > 0:
        K.you_are_here(c, wx, wy, t, k2, "Hawaii: night!", side=-1)
    # dotted path + the cushion
    if t >= T("m_path"):
        u = tl.prog("m_path", t, 0.1, 0.85)
        K.map_path(c, v, PATH, max(u, 0.0001), head=u > 0.02)
        x, y, ang = K.path_point(v, PATH, u)
        K.crew(c, tl, t, x, y + 6, 0.16 * v.z ** 0.8, -1, fly=1)
        P.owl(c, x + 30 * v.z ** 0.8, y - 40 * v.z ** 0.8, 0.16 * v.z ** 0.8, -1, t, 0, "open", 1.0)
    else:
        K.crew(c, tl, t, 1080, 640, 0.7, -1, fly=1, look={"luna": (-1, -1), "pip": (-1, -1), "whiskers": (-1, -1)})
        P.owl(c, 1200, 560, 0.8, -1, t, hoot_mouth(tl, t), "open", 1.0)
    K.flash(c, 1 - tl.prog("m_open", t, 0.0, 0.3))
    K.flash(c, tl.prog("m_path", t, 0.9, 1.0), (10, 14, 46))
    K.sub_band(c, tl, t)
    return c


# ====================================================================== hawaii

CUSH_H = (360, 640)
SHELBY = (900, P.SHORE + 34)
FISH_XY = (P.MOON_XY[0], 430)


def split_inset(ic, t):
    """Home has morning while Hawaii has night: two windows side by side."""
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    half = w / 2
    ic.img.paste(D.gradient(int(half * SS), int(h * SS), [(0, (110, 182, 246)), (1, (210, 236, 255))]), (0, 0))
    ic.img.paste(D.gradient(int(half * SS), int(h * SS), [(0, (14, 18, 56)), (1, (44, 50, 112))]),
                 (int(half * SS), 0))
    P.sun(ic, 70, 66, 30, t, face=True, glow=False)
    ic.rect(0, h - 56, half, h, (120, 190, 92), ol=None)
    # breakfast bowl + a fish
    ic.ellipse(half / 2 + 30, h - 70, 54, 14, (90, 140, 210), w=2.5)
    ic.poly([(half / 2 - 24, h - 72), (half / 2 + 84, h - 72), (half / 2 + 70, h - 46), (half / 2 - 10, h - 46)],
            (90, 140, 210), w=2.5)
    ic.ellipse(half / 2 + 30, h - 86, 26, 10, (250, 160, 80), w=2)
    ic.poly([(half / 2 + 54, h - 86), (half / 2 + 68, h - 96), (half / 2 + 68, h - 76)], (250, 160, 80), w=2)
    K.text(ic, half / 2, 26, "Home: breakfast!", 24, (48, 40, 60), stroke=2, stroke_fill=(255, 255, 255))
    D.stars(ic, 9, 22, w, h * 0.6)
    ic.rect(half, h - 56, w, h, (40, 60, 70), ol=None)
    P.moon_phase(ic, w - 70, 66, 26, 0.5)
    P1.turtle(ic, half + half / 2 - 10, h - 54, 0.36, 1, t, 0, "closed", 0.0)
    D.zzz(ic, half + half / 2 + 70, h - 120, t)
    K.text(ic, half + half / 2, 26, "Hawaii: bedtime!", 24, (255, 255, 255), stroke=3)
    ic.line([(half, 0), (half, h)], OUT, 4, cap=False)


def hawaii(tl, t):
    T = tl.t
    c = Canvas(P.beach_bg().copy())
    P.sea_glints(c, t)
    P.moon_path(c, t)
    # the Moon Fish (the moon's reflection) wobbling on the sea
    D.moon_fish(c, FISH_XY[0], FISH_XY[1], t, 0.75)
    fk = tl.prog("ha_fish", t, 0.2, 0.45) * (1 - tl.prog("ha_remember", t, 0.6, 1.0))
    if fk > 0.01:
        K.label(c, FISH_XY[0] - 160, FISH_XY[1] - 90, "The Moon Fish?!", 28, tip=(FISH_XY[0] - 50, FISH_XY[1] - 10),
                k=fk)
    rk = tl.prog("ha_remember", t, 0.3, 0.5) * (1 - tl.prog("ha_secret", t, 0.0, 0.3))
    if rk > 0.01:
        mx, my = P.MOON_XY
        K.arrow(c, mx, my + 60, FISH_XY[0], FISH_XY[1] - 30, (255, 236, 110), 6, rk)
        K.label(c, mx - 230, my + 20, "Just the Moon, shining in the water", 24, k=rk)
    P.surf(c, t)
    # Grandpa Shelby in the shallows
    sh_eyes = "closed"
    if T("ha_hello") <= t < T("ha_split"):
        sh_eyes = "happy" if t < T("ha_hello", 0.4) else "open"
    if t >= T("ha_time", 0.7):
        sh_eyes = "closed"
    P1.turtle(c, SHELBY[0], SHELBY[1], 0.95, -1, t, tl.mouth("shelby", t), sh_eyes, 0.3)
    c.rect(SHELBY[0] - 200, SHELBY[1] + 4, SHELBY[0] + 200, SHELBY[1] + 30, P.SAND, ol=None)
    c.ellipse(SHELBY[0], SHELBY[1] + 4, 170, 10, (200, 214, 240), ol=None)
    if t >= T("ha_time", 0.8):
        D.zzz(c, SHELBY[0] - 200, SHELBY[1] - 120, t)
    # the friends land on the sand
    land = ease(tl.prog("ha_land", t, 0.0, 0.6))
    up = ease(tl.prog("ha_up", t, 0.0, 1.0)) + 0.4 * ease(tl.prog("ha_secret", t, 0.8, 1.0))
    cx = CUSH_H[0]
    cy = lerp(-150, CUSH_H[1], land) - 700 * up
    laugh = False
    eyes, look, extra = {}, {"whiskers": (1, -0.3), "luna": (1, -0.3), "pip": (1, -0.3)}, {}
    w_pose = None
    if T("ha_fish") <= t < T("ha_remember", 0.5):
        eyes["whiskers"] = "wide"
        look["whiskers"] = (1, 0.4)
    if T("ha_wiggle") <= t < T("ha_remember", 0.4):
        wig = math.sin(t * 22) * 6
        w_pose = {"pose": "crouch", "dy": 8}
        extra["whiskers"] = {**w_pose}
        cx_w = wig
    else:
        cx_w = 0
    if T("ha_dry") <= t < T("ha_secret"):
        eyes["whiskers"] = "happy"
    if T("ha_break") <= t < T("ha_time"):
        look = {"whiskers": (1, 0), "luna": (1, 0), "pip": (1, 0)}
    if land > 0:
        K.crew(c, tl, t, cx + cx_w, cy, 1.15, 1, fly=1 - land + up, eyes=eyes, look=look, extra=extra)
    # Professor Hoot on the sand
    ok = ease(tl.prog("ha_land", t, 0.2, 0.8))
    if ok > 0:
        ox = lerp(-100, 640, ok)
        oy = lerp(300, 640, ok) - 700 * up
        P.owl(c, ox, oy, 1.1, 1, t, hoot_mouth(tl, t), "open", 1.0 if ok < 1 or up > 0 else 0.0,
              look=(1, -0.2))
    # every place has its own time
    sk = tl.prog("ha_time", t, 0.2, 0.4) * (1 - tl.prog("ha_fish", t, 0.0, 0.2))
    if sk > 0.01:
        K.inset(c, 640, 180, 620, 250, sk, lambda ic: split_inset(ic, t))
        K.label(c, 640, 330, "Every place has its own time", 28, k=tl.prog("ha_split", t, 0.1, 0.3) * sk)
    K.sub_band(c, tl, t)
    K.flash(c, tl.prog("ha_up", t, 0.6, 1.0), (255, 252, 235))
    return c


# ======================================================================== moon

M_SUN = (100, 360)
M_EARTH = (690, 420)
M_MOON = (1060, 230)
ORB = (640, 380, 360, 130)            # Moon orbit ellipse: cx, cy, rx, ry


def crew_corner(c, tl, t, laugh=False):
    eyes = {"luna": "happy", "pip": "happy", "whiskers": "happy"} if laugh else {}
    extra = {"luna": {"mouth": laughing(t)}, "pip": {"mouth": laughing(t)}} if laugh else {}
    K.crew(c, tl, t, 1080, 660, 0.62, -1, fly=1, eyes=eyes, extra=extra,
           look={"luna": (-1, -0.6), "pip": (-1, -0.6), "whiskers": (-1, -0.6)})
    P.owl(c, 1220, 590, 0.75, -1, t, hoot_mouth(tl, t), "happy" if laugh else "open", 1.0)


def moon(tl, t):
    T = tl.t
    if t >= T("mo_year"):
        return moon_year(tl, t)
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    ok = ease(tl.prog("mo_month", t, 0.0, 0.6))          # 0: mirror layout -> 1: orbit layout
    sun_r = lerp(170, 120, ok)
    P.sun(c, M_SUN[0] - 60 * ok, M_SUN[1], sun_r, t)
    ex, ey = lerp(M_EARTH[0], ORB[0], ok), lerp(M_EARTH[1], ORB[1], ok)
    er = lerp(110, 92, ok)
    lon0 = -t * 18
    # Moon position: fixed at first, then around the orbit (starting from the far right = full)
    orbit_u = tl.prog("mo_orbit", t, 0.0, 1.0) * 0.55 + tl.prog("mo_phase", t, 0.0, 1.0) * 0.25 \
        + tl.prog("mo_shapes", t, 0.0, 1.0) * 0.2
    alpha = math.radians(90) + TAU * orbit_u + math.radians(-25) * (1 - ok)
    ox_, oy_ = ORB[0] + ORB[2] * math.cos(alpha), ORB[1] - ORB[3] * math.sin(alpha)
    mx, my = lerp(M_MOON[0], ox_, ok), lerp(M_MOON[1], oy_, ok)
    mr = 44
    far = math.sin(alpha) > 0
    # orbit ring (back half)
    if ok > 0.01:
        ring_pts = [(ORB[0] + ORB[2] * math.cos(a), ORB[1] - ORB[3] * math.sin(a)) for a in np.linspace(0, TAU, 90)]
        for i in range(0, len(ring_pts) - 1, 2):
            a = i / len(ring_pts) * TAU
            if math.sin(a) > 0:
                c.line([ring_pts[i], ring_pts[i + 1]], mix((30, 30, 70), (255, 236, 110), ok), 4)
    if far or ok < 0.5:
        P.moon_ball(c, mx, my, mr)
    K.globe(c, ex, ey, er, lon=lon0, lat=20, sun=sun_for(lon0, 20, -1, 0, 0), glow=0.2,
            glow_col=(150, 190, 255))
    if ok > 0.01:
        for i in range(0, len(ring_pts) - 1, 2):
            a = i / len(ring_pts) * TAU
            if math.sin(a) <= 0:
                c.line([ring_pts[i], ring_pts[i + 1]], mix((30, 30, 70), (255, 236, 110), ok), 4)
    if not far and ok >= 0.5:
        P.moon_ball(c, mx, my, mr)
    K.label(c, ex, ey + er + 40, "Earth", 26, k=tl.prog("mo_open", t, 0.3, 0.6) * (1 - ok))
    K.label(c, mx + 10, my - 80, "Moon", 26, k=tl.prog("mo_open", t, 0.5, 0.8) * (1 - ok))
    # sunlight bouncing off the Moon like a mirror
    rk = tl.prog("mo_mirror", t, 0.2, 0.5) * (1 - ok)
    bk = tl.prog("mo_mirror", t, 0.55, 0.85) * (1 - ok)
    if rk > 0.01:
        K.arrow(c, M_SUN[0] + 190, M_SUN[1] - 70, mx - 60, my + 6, (255, 214, 70), 9, rk, head=26)
        K.label(c, 470, 200, "Sunlight", 26, k=rk, col=(200, 120, 20), bg=(255, 244, 190))
    if bk > 0.01:
        K.arrow(c, mx - 26, my + 50, ex + 90, ey - 70, (230, 236, 255), 8, bk, head=24)
        K.label(c, 980, 380, "Moonlight", 26, k=bk, col=(60, 66, 140))
    mk = tl.prog("mo_rays", t, 0.0, 0.3) * (1 - ok)
    if mk > 0.01:
        K.label(c, mx + 70, my - 110, "Like a mirror!", 28, k=mk)
        K.sparkles(c, mx, my, 70, t, 8, mk, seed=5)
    # once a month
    lk = tl.prog("mo_month", t, 0.5, 0.8) * (1 - tl.prog("mo_phase", t, 0.0, 0.2))
    K.label(c, 640, 60, "Around the Earth: about 1 month", 30, k=lk)
    # what we see from Earth
    vk = tl.prog("mo_orbit", t, 0.1, 0.3) * (1 - tl.prog("mo_shapes", t, 0.0, 0.15))
    if vk > 0.01:
        phase = ((math.degrees(alpha) - 180) / 360) % 1.0

        def seen(ic):
            w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
            ic.img.paste(D.gradient(int(w * SS), int(h * SS), [(0, (14, 18, 56)), (1, (44, 50, 112))]), (0, 0))
            P.moon_phase(ic, w / 2, h / 2 - 8, 52, phase, glow=True)
            K.text(ic, w / 2, h - 18, "We see", 22, (255, 255, 255), stroke=3)
        K.inset(c, 1120, 140, 220, 190, vk, seen, bg=(20, 20, 50))
    # the shapes, one by one
    sk = tl.prog("mo_shapes", t, 0.0, 0.1) * (1 - tl.prog("mo_year", t, 0.0, 0.1))
    if sk > 0.01 or (T("mo_phase", 0.5) <= t < T("mo_year")):
        sk = max(sk, tl.prog("mo_phase", t, 0.5, 0.7))
        c.rect(150, 548, 1130, 704, (20, 22, 56), r=24, w=3)
        names = [("Crescent", 0.12), ("Half moon", 0.25), ("Full moon", 0.5), ("Half moon", 0.75),
                 ("Crescent", 0.88)]
        for i, (nm, ph) in enumerate(names):
            kk = tl.prog("mo_shapes", t, 0.05 + 0.15 * i, 0.2 + 0.15 * i) if T("mo_shapes") <= t else 0
            if i == 2:
                kk = max(kk, tl.prog("mo_phase", t, 0.6, 0.8))
            if kk <= 0.01:
                continue
            x = 250 + 195 * i
            c.push(x, 606, pop(kk))
            P.moon_phase(c, 0, 0, 38, ph, glow=False)
            c.pop()
            K.text(c, x, 674, nm, 22, (255, 255, 255), stroke=2)
    crew_corner(c, tl, t)
    K.flash(c, 1 - tl.prog("mo_open", t, 0.0, 0.4))
    K.sub_band(c, tl, t, top=540)
    return c


Y_ORB = (640, 380, 440, 170)


def moon_year(tl, t):
    """Zoom out: the Earth's trip around the Sun takes a year, 365 days."""
    T = tl.t
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t)
    k = ease(tl.prog("mo_year", t, 0.0, 0.4))
    cx, cy, rx, ry = Y_ORB
    u = tl.prog("mo_trip", t, 0.0, 0.9)
    ang2 = math.radians(270) + TAU * ease(u)
    ex, ey = cx + rx * math.cos(ang2), cy - ry * math.sin(ang2)
    near = math.sin(ang2) < 0
    # orbit ring
    ring = [(cx + rx * math.cos(a), cy - ry * math.sin(a)) for a in np.linspace(0, TAU, 120)]

    def draw_ring(front):
        for i in range(0, len(ring) - 1, 2):
            a = i / len(ring) * TAU
            if (math.sin(a) <= 0) == front:
                c.line([ring[i], ring[i + 1]], (255, 236, 110), 4)
    draw_ring(False)
    if not near:
        earth_small(c, ex, ey, t, cx, cy)
    P.sun(c, cx, cy, lerp(40, 92, k), t)
    draw_ring(True)
    if near:
        earth_small(c, ex, ey, t, cx, cy)
    # trail + day counter
    if u > 0:
        days = int(round(1 + 364 * u))
        K.label(c, ex, ey - 70 if not near else ey + 70, f"Day {days}", 26, k=1.0)
    K.label(c, 640, 60, "1 trip around the Sun = 1 year = 365 days", 30, k=tl.prog("mo_year", t, 0.4, 0.6))
    if t >= T("mo_trip", 0.92):
        K.sparkles(c, ex, ey, 90, t, 10, 1.0, seed=3)
    bk = tl.prog("mo_bday", t, 0.4, 0.7)
    if bk > 0:
        P.cake(c, ex + 190, ey - 10, 0.9, t, bk)
        K.label(c, ex + 190, ey + 30, "Happy birthday!", 24, k=bk)
    laugh = T("mo_laugh") <= t
    crew_corner(c, tl, t, laugh)
    if T("mo_cake", 0.3) <= t:
        K.bubble(c, 900, 470, 70, 50, tl.prog("mo_cake", t, 0.3, 0.5), tail=(1040, 590))
        if tl.prog("mo_cake", t, 0.3, 0.5) > 0.3:
            P.cake(c, 900, 505, 0.6, t, 1.0)
    K.flash(c, 0.7 * (1 - tl.prog("mo_year", t, 0.0, 0.25)))
    K.sub_band(c, tl, t)
    return c


def earth_small(c, x, y, t, sx, sy):
    lon0 = -t * 40
    s = sun_for(lon0, 20, sx - x, -(sy - y), 0)
    K.globe(c, x, y, 40, lon=lon0, lat=20, sun=s)
    # the Moon zipping around it
    a = t * 2.4
    mx, my = x + math.cos(a) * 62, y - math.sin(a) * 20
    c.circle(mx, my, 9, P.MOON, w=2)


# ==================================================================== remember

FACTS = ["The Earth spins around once a day. That makes day and night.",
         "The Earth goes around the Sun once a year.",
         "The Moon shines with light from the Sun."]


def icon_spin(c, x, y, r, t=0.0):
    lon0 = -t * 40
    K.globe(c, x, y, r * 0.8, lon=lon0, lat=15, sun=sun_for(lon0, 15, -1, 0.2, 0.2))
    pts = [(x + math.cos(a) * r * 1.0, y + r * 0.45 + math.sin(a) * r * 0.25) for a in np.linspace(0.4, 2.7, 16)]
    c.line(pts, (255, 196, 60), 4)


def icon_orbit(c, x, y, r, t=0.0):
    c.ellipse(x, y, r * 0.95, r * 0.42, None, ol=(240, 180, 50), w=3)
    P.sun(c, x, y, r * 0.3, t, face=False, rays=False, glow=False)
    a = t * 1.5
    ex, ey = x + math.cos(a) * r * 0.95, y - math.sin(a) * r * 0.42
    K.globe(c, ex, ey, r * 0.2, lon=-t * 40, lat=15)


def icon_moonlight(c, x, y, r, t=0.0):
    P.sun(c, x - r * 0.5, y - r * 0.45, r * 0.36, t, face=False, rays=False, glow=False)
    K.arrow(c, x - r * 0.12, y - r * 0.2, x + r * 0.12, y + r * 0.0, (255, 196, 60), 5, 1.0, head=12)
    P.moon_ball(c, x + r * 0.42, y + r * 0.36, r * 0.46, sun_dir=225)


def remember(tl, t):
    ks = [tl.prog("r_f1", t, 0.0, 0.25), tl.prog("r_f2", t, 0.0, 0.25), tl.prog("r_f3", t, 0.0, 0.25)]
    active = None
    for i, e in enumerate(("r_f1", "r_f2", "r_f3")):
        if tl.t(e) <= t < tl.ev(e).end + 0.4:
            active = i
    c = K.remember_card(t, FACTS, ks, [icon_spin, icon_orbit, icon_moonlight], active)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== quiz

def icon_gone(c, x, y, r, t=0.0):
    c.rect(x - r, y - r * 0.8, x + r, y + r * 0.8, (40, 46, 100), r=12, w=3)
    for i, (dx, dy) in enumerate(((-0.6, -0.4), (0.5, -0.5), (0.1, 0.1), (-0.3, 0.4), (0.7, 0.3))):
        K.star(c, x + dx * r, y + dy * r * 0.8, 5, (255, 250, 220))
    K.text(c, x, y + 4, "?", r * 0.9, (255, 214, 80), stroke=3)


def icon_facing(c, x, y, r, t=0.0):
    P.sun(c, x - r * 0.75, y - r * 0.1, r * 0.3, t, face=False, rays=True, glow=False)
    lon0 = -t * 30
    K.globe(c, x + r * 0.3, y, r * 0.6, lon=lon0, lat=15, sun=sun_for(lon0, 15, -1, 0, 0))


def icon_own(c, x, y, r, t=0.0):
    P.moon_phase(c, x, y + r * 0.1, r * 0.6, 0.5)
    c.circle(x + r * 0.55, y - r * 0.55, r * 0.22, (255, 250, 160), w=3)
    c.rect(x + r * 0.47, y - r * 0.36, x + r * 0.63, y - r * 0.24, (180, 180, 190), w=2)
    K.text(c, x - r * 0.75, y - r * 0.6, "?", r * 0.5, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))


def icon_from_sun(c, x, y, r, t=0.0):
    icon_moonlight(c, x, y, r, t)


def quiz(tl, t):
    T = tl.t
    if t < T("q2"):
        c = K.quiz_card(t, "At night, is the Sun gone, or is our side facing away from it?",
                        ["The Sun is gone", "Facing away"], 1,
                        ask=tl.prog("q_open", t) * 0.4 + tl.prog("q1", t, 0.0, 0.3) * 0.6,
                        count=tl.prog("q1_count", t), reveal=tl.prog("q1_ans", t, 0.0, 0.35),
                        icons=[icon_gone, icon_facing], number=1, answer_text="Facing away from the Sun!")
    else:
        c = K.quiz_card(t, "Where does moonlight come from?",
                        ["From the Sun", "The Moon's own light"], 0,
                        ask=tl.prog("q2", t, 0.0, 0.3), count=tl.prog("q2_count", t),
                        reveal=tl.prog("q2_ans", t, 0.0, 0.35),
                        icons=[icon_from_sun, icon_own], number=2, answer_text="From the Sun!")
    K.sub_band(c, tl, t)
    return c


# ======================================================================= recap

CARD_W, CARD_H = 214, 178


def _sky(ic, top, bot):
    return P.card_bg(ic, top, bot)


def card_planet(ic, t):
    w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
    ic.img.paste(K.space_bg().crop((0, 0, int(w * SS), int(h * SS))), (0, 0))
    K.globe(ic, w / 2 - 20, h / 2 - 14, 52, lon=-t * 25, lat=18)
    P.try_draw(P1.turtle, ic, w / 2 + 50, h / 2 + 40, 0.22, -1, t, 0, "open", 0.6)


def card_continents(ic, t):
    w, h = _sky(ic, (130, 196, 246), (210, 236, 255))
    K.globe(ic, w / 2, h / 2 - 6, 56, lon=-t * 25 + 20, lat=15, style="continents")
    if P2:
        P.try_draw(P2.albatross, ic, 50, 50, 0.22, 1, t, 0, "open", 1.0)


def card_oceans(ic, t):
    w, h = _sky(ic, (90, 170, 236), (30, 90, 170))
    for i in range(4):
        ic.line([(0, 40 + i * 30 + 4 * math.sin(t * 2 + i)), (w, 44 + i * 30)], (150, 206, 244), 3, cap=False)
    if P3:
        P.try_draw(P3.whale, ic, w / 2 + 6, h / 2 + 6, 0.2, 1, t)


def card_mountains(ic, t):
    w, h = _sky(ic, (150, 205, 250), (226, 242, 255))
    ic.poly([(-10, h - 30), (70, 40), (150, h - 30)], (140, 130, 150), w=2.5)
    ic.poly([(48, 78), (70, 40), (92, 78), (80, 70), (70, 80), (58, 70)], (255, 255, 255), w=2)
    ic.poly([(110, h - 30), (165, 70), (190, 70), (240, h - 30)], (120, 96, 90), w=2.5)
    k = 0.5 + 0.5 * math.sin(t * 5)
    ic.ellipse(178, 66, 14, 6, (255, 120, 40), ol=None)
    for i in range(3):
        ic.circle(178 + 8 * i, 50 - 14 * i - 4 * k, 9 + 3 * i, (210, 208, 214), ol=None)
    ic.rect(0, h - 30, w, h, (120, 180, 100), ol=None)
    if P4:
        P.try_draw(P4.snow_leopard, ic, 70, h - 26, 0.42, 1, t)


def card_rivers(ic, t):
    w, h = _sky(ic, (150, 205, 250), (200, 236, 210))
    ic.rect(0, 60, w, h, (120, 190, 92), ol=None)
    pts = [(40, 60), (70, 90), (60, 120), (110, 150), (170, h)]
    ic.line(pts, (64, 146, 222), 26)
    ic.line(pts, (120, 190, 240), 8)
    if P5:
        P.try_draw(P5.otter, ic, 100, 140, 0.32, 1, t)


def card_desert(ic, t):
    w, h = _sky(ic, (250, 200, 110), (255, 236, 180))
    P.sun(ic, w - 40, 36, 20, t, face=False, glow=False)
    ic.ellipse(60, h + 10, 120, 70, (236, 196, 120), ol=None)
    ic.ellipse(180, h + 20, 120, 80, (226, 180, 100), ol=None)
    if P6:
        P.try_draw(P6.camel, ic, 100, h - 20, 0.32, 1, t)


def card_forest(ic, t):
    w, h = _sky(ic, (60, 140, 80), (30, 90, 50))
    for x, y, r in ((30, 40, 50), (110, 20, 60), (190, 50, 50), (60, 140, 50), (170, 150, 50)):
        ic.circle(x, y, r, (50, 130, 70), ol=None)
    ic.rect(150, 60, 166, h, (110, 76, 50), ol=None)
    if P7:
        P.try_draw(P7.toucan, ic, 120, 120, 0.5, 1, t)


def card_poles(ic, t):
    w, h = _sky(ic, (160, 210, 250), (230, 244, 255))
    ic.poly([(0, 110), (60, 96), (140, 104), (w, 92), (w, h), (0, h)], (246, 250, 255), w=2.5)
    ic.poly([(150, 104), (176, 50), (200, 98)], (210, 232, 250), w=2)
    if P8:
        P.try_draw(P8.pebble, ic, 80, 150, 0.62, 1, t)
    elif P2:
        P.try_draw(P2.penguin, ic, 80, 150, 0.5, 1, t)


def card_seasons(ic, t):
    w, h = _sky(ic, (150, 205, 250), (226, 242, 255))
    ic.rect(0, h - 36, w / 2, h, (120, 190, 92), ol=None)
    ic.rect(w / 2, h - 36, w, h, (246, 250, 255), ol=None)
    ic.rect(w / 2 - 8, 60, w / 2 + 8, h - 36, (130, 90, 60), w=2)
    pts_l = [(w / 2 - 6, 70)] + [(w / 2 + math.cos(a) * 70, 70 + math.sin(a) * 50) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, 20)]
    ic.poly(pts_l, (90, 165, 85), w=2.5)
    pts_r = [(w / 2 + 6, 70)] + [(w / 2 + math.cos(a) * 70, 70 + math.sin(a) * 50) for a in np.linspace(-math.pi / 2, math.pi / 2, 20)]
    ic.poly(pts_r, (255, 255, 255), w=2.5)
    for i in range(10):
        x = (37 * i + t * 20) % (w / 2) + w / 2
        y = (53 * i + t * 40) % h
        ic.circle(x, y, 2.5, (255, 255, 255), ol=None)
    if PR:
        P.try_draw(PR.rooster, ic, 40, h - 30, 0.9, 0.0, t)


def card_daynight(ic, t):
    w, h = _sky(ic, (16, 18, 52), (44, 40, 100))
    lon0 = -t * 30
    K.globe(ic, w / 2 + 20, h / 2 - 6, 54, lon=lon0, lat=15, sun=sun_for(lon0, 15, -1, 0.1, 0.3))
    P.moon_phase(ic, w - 30, 30, 14, 0.3)
    P.owl(ic, 50, h - 20, 0.62, 1, t, 0, "open", 0.0)


CARDS = [("Our Planet", card_planet), ("Continents", card_continents), ("Oceans", card_oceans),
         ("Mountains", card_mountains), ("Rivers & Lakes", card_rivers), ("Deserts", card_desert),
         ("Rainforests", card_forest), ("The Poles", card_poles), ("Seasons", card_seasons),
         ("Day & Night", card_daynight)]
POPS = [("rc_2", f) for f in (0.05, 0.25, 0.45, 0.62, 0.82)] + [("rc_3", f) for f in (0.05, 0.24, 0.44, 0.64, 0.82)]


def recap(tl, t):
    T = tl.t
    c = Canvas(K.space_bg().copy())
    K.twinkle(c, t, 40)
    tk = tl.prog("rc_open", t, 0.0, 0.8)
    K.ribbon(c, 640, 70, 560, 70, (240, 180, 50), tk)
    lk = tl.prog("rc_open", t, 0.0, 0.6) * (1 - tl.prog("rc_2", t, 0.0, 0.08))
    if lk > 0.01:
        K.logo(c, 640, 300, 72, t, lk)
        K.crew(c, tl, t, 640, 540, 1.0 * pop(lk), 1, fly=1)
        K.sparkles(c, 640, 400, 380, t, 14, lk, seed=17)
    if tk > 0.3:
        K.text(c, 640, 70, "Season 1: our whole world!", 38, (255, 255, 255), stroke=4)
    hold = tl.prog("rc_hold", t, 0.0, 1.0)
    for i, (name, fn) in enumerate(CARDS):
        ev, f = POPS[i]
        k = clamp((t - T(ev, f)) / 0.35)
        if k <= 0.01:
            continue
        row, col = divmod(i, 5)
        x = 152 + 244 * col
        y = 250 + 230 * row + 4 * math.sin(t * 2 + i)
        if hold > 0:
            y += -10 * math.sin(math.pi * clamp(hold * 4 - i * 0.25))

        def draw(ic, fn=fn, name=name, i=i):
            fn(ic, t)
            w, h = ic.img.size[0] / SS, ic.img.size[1] / SS
            ic.rect(0, h - 34, w, h, (20, 22, 56), ol=None)
            K.text(ic, w / 2, h - 17, f"{i + 1}  {name}", 21, (255, 255, 255))
        K.inset(c, x, y, CARD_W, CARD_H, k, draw, bg=(30, 30, 60), radius=20)
    if hold > 0.05:
        K.sparkles(c, 640, 360, 560, t, 18, hold, seed=13)
    K.sub_band(c, tl, t)
    return c


# ======================================================================== home

def home(tl, t):
    T = tl.t
    c = Canvas(K.home_bg("night").copy())
    lon = 30 - 4 * t
    back = tl.prog("e_back", t, 0.0, 0.7)
    K.old_globe(c, K.GLOBE_X, SY, 1.0, lon=lon, glow=0.8 * (1 - back) + 0.1, t=t)
    e = ease(back)
    x = lerp(GCX, CUSH_X, e)
    y = lerp(GCY + 40, SY, e) - 90 * math.sin(math.pi * e)
    s = CREW_S * lerp(0.15, 1, e ** 0.7)
    sleep = t >= T("e_curl", 0.2)
    extra = {"whiskers": {"pose": "sleep", "dy": 6}} if sleep else None
    K.crew(c, tl, t, x, y, s, 1, fly=1 - back, extra=extra,
           look={"luna": (1, -0.5), "pip": (1, -0.5)}, eyes={"luna": "happy"} if T("e_luna") <= t < T("e_nap") else None)
    if sleep:
        D.zzz(c, CUSH_X - 10, SY - 130, t)
    # Professor Hoot: awake at night, then off out of the window
    ok = ease(tl.prog("e_back", t, 0.2, 0.9))
    fly_out = ease(tl.prog("e_luna", t, 0.3, 1.0) * 0.5 + tl.prog("e_nap", t, 0.0, 1.0) * 0.5)
    ox = lerp(lerp(GCX, OWL_PERCH[0], ok), 1360, fly_out)
    oy = lerp(lerp(GCY, OWL_PERCH[1], ok), 80, fly_out) - 60 * math.sin(math.pi * fly_out)
    if fly_out < 1:
        P.owl(c, ox, oy, 1.45 * lerp(0.2, 1, ok), -1 if fly_out <= 0 else 1, t, hoot_mouth(tl, t), "wide" if
              tl.talking("hoot", t) else "open", 1.0 if (ok < 1 or fly_out > 0) else 0.0, look=(-1, -0.2))
    K.flash(c, 0.6 * (1 - tl.prog("e_back", t, 0.0, 0.3)))
    K.end_card(c, tl.prog("e_end", t, 0.0, 0.25), "The End of Season 1", "See you next season!", t)
    K.sub_band(c, tl, t)
    return c


SCENE_FUNCS = {"title": title, "sill": sill, "space": space, "map": map_, "hawaii": hawaii, "moon": moon,
               "remember": remember, "quiz": quiz, "recap": recap, "home": home}
