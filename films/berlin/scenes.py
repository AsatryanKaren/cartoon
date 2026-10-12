"""Berlin -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync with the speech. Static backgrounds are drawn once and cached; the
Pariser Platz, the East Side Gallery and the TV Tower use wide or tall cached
layers under a moving camera. The story of the Wall is told as a picture-book
page.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.berlin import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "berti": 3.7}
NIGHT = ((30, 36, 90), 0.34)
DUSK = ((120, 70, 140), 0.18)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def sky_img(stops, w=W, h=H):
    return D.gradient(int(w * SS), int(h * SS), stops)


def view(bg, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    return Canvas(bg.crop((x, y, x + W * SS, y + H * SS)))


def track(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def moving(t, keys):
    return (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1


def arc_y(u, height):
    return -4 * height * u * (1 - u)


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def pip(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("pip", t))
    hop = kw.pop("hop", None)
    if hop is None:
        hop = abs(math.sin(t * 8)) * 5 if tl.talking("pip", t) else 0.0
    D.mouse(c, x, y, s, face, t, mouth=mouth, hop=hop, **kw)


def bear(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("berti", t))
    P.berti(c, x, y, s, face, t, mouth=mouth, **kw)


def mover(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """Draw a character moving along x keys [(time, x)]; faces its direction of travel."""
    x = smooth(t, keys)
    v = moving(t, keys)
    walking = abs(v) > 15
    if walking:
        face = 1 if v > 0 else -1
    if who == "pip":
        pip(c, tl, t, x, y, s, face, walk=x / (6 * s) if walking else 0.0, **kw)
    elif who == "berti":
        bear(c, tl, t, x, y, s, face, walk=x / (14 * s) if walking else 0.0, **kw)
    else:
        if walking and pose in ("stand", "sit"):
            pose = "walk"
        kitty(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if pose == "walk" else 0.0, **kw)
    return x, face


def finish(c, tl, t, strength=0.5, top=560, _masks={}):
    """Darken the bottom of the frame softly while a subtitle shows."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    q = int(round(k * strength * 20))
    if q > 0:
        key = (q, top)
        if key not in _masks:
            h = (H - top) * SS
            ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
            _masks[key] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
        c.img.paste((16, 18, 34), (0, top * SS, W * SS, H * SS), _masks[key])
    return c


def zoom(c, cx, cy, z):
    if z <= 1.001:
        return c
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, W - w)
    y0 = clamp(cy - h / 2, 0, H - h)
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def soft_glow(c, x, y, r, col, alpha):
    m = Image.new("L", c.img.size, 0)
    ImageDraw.Draw(m).ellipse([(x - r * 0.6) * SS, (y - r * 0.6) * SS, (x + r * 0.6) * SS, (y + r * 0.6) * SS],
                              fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(r * 0.35 * SS))
    c.img.paste(Image.new("RGB", c.img.size, col), (0, 0), m)


def blend_over(c, col, a):
    if a <= 0.003:
        return c
    return Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, a)))


def hearts_up(c, t, x, y, k=1.0, n=4, seed=0):
    for j in range(n):
        u = (t * 0.5 + j / n + seed * 0.13) % 1.0
        hx = x + 30 * math.sin(u * 6 + j * 1.7)
        hy = y - 120 * u
        P.heart(c, hx, hy, (8 + 6 * (1 - u)) * k, mix((240, 60, 100), (255, 200, 220), u), ol=OUT)


def sparkles(c, t, x0, x1, y0, y1, n=12, seed=1, col=(255, 250, 210), k=1.0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ph = rng.uniform(0, 6.28)
        r = (2 + 5 * max(0.0, math.sin(t * 3 + ph))) * k
        if r > 2.2:
            c.poly([(x, y - r * 2), (x + r * 0.4, y - r * 0.4), (x + r * 2, y), (x + r * 0.4, y + r * 0.4),
                    (x, y + r * 2), (x - r * 0.4, y + r * 0.4), (x - r * 2, y), (x - r * 0.4, y - r * 0.4)],
                   col, ol=None)


def river(c, x0, x1, y0, y1, rng, col=P.RIVER, hi=P.RIVER_L, n=60):
    c.rect(x0, y0, x1, y1, col, ol=None)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0 + 4, y1 - 2)
        ww = rng.uniform(10, 50) * (0.4 + (y - y0) / max(1, y1 - y0))
        c.line([(x - ww / 2, y), (x + ww / 2, y)], hi, 2, cap=False)


def ripples(c, t, x0, x1, y0, y1, n=24, seed=2, col=(170, 210, 240)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = (rng.uniform(x0, x1) + t * rng.uniform(8, 20)) % (x1 - x0) + x0
        y = rng.uniform(y0, y1)
        ww = rng.uniform(10, 34) * (0.5 + 0.5 * math.sin(t * 2 + k))
        if ww > 4:
            c.line([(x - ww / 2, y), (x + ww / 2, y)], col, 2, cap=False)


# ======================================================================= title

TITLE_COLS = [(240, 70, 80), (250, 150, 50), (250, 210, 60), (110, 200, 90), (70, 160, 230), (170, 110, 220)]


def title_bg():
    def make():
        c = Canvas(sky_img([(0, (96, 160, 230)), (0.45, (186, 206, 236)), (0.66, (255, 214, 170)),
                            (1, (255, 226, 180))]))
        soft_glow(c, 200, 420, 260, (255, 236, 190), 0.6)
        D.cloud(c, 1180, 230, 0.6, (255, 240, 236))
        D.cloud(c, 120, 260, 0.5, (255, 240, 236))
        rng = np.random.default_rng(4)
        P.skyline(c, -20, W + 20, 470, rng, 40, 110, [(196, 176, 196), (206, 186, 200), (186, 168, 190)])
        P.tv_tower(c, 1090, 470, 450, col=(236, 228, 236), shade=(206, 196, 214), lw=2.2)
        P.berliner_dom(c, 820, 470, 0.5, col=(176, 168, 176), dome=(110, 150, 136))
        P.brandenburg_gate(c, 230, 470, 0.36, lw=1.6)
        P.reichstag(c, 540, 470, 0.3, lw=1.4, flags=False)
        rng = np.random.default_rng(5)
        P.skyline(c, -20, W + 20, 488, rng, 14, 40, [(214, 170, 160), (226, 186, 170), (200, 160, 156)],
                  win=(250, 220, 170), p=0.3)
        river(c, 0, W, 488, 586, np.random.default_rng(6), col=(110, 140, 190), hi=(255, 214, 180), n=80)
        # embankment: stone wall with a painted strip of the Wall along the top
        c.rect(-10, 586, W + 10, H + 10, (196, 186, 170), w=2.5)
        for x in range(0, W, 90):
            c.line([(x, 600), (x, H)], (170, 160, 146), 2, cap=False)
        c.rect(-10, 580, W + 10, 600, (220, 212, 198), w=2.5)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    # a sightseeing boat drifting along the Spree
    bx = lerp(-200, 1500, (t - tl.t("t_open")) / 16.0)
    P.river_boat(c, bx, 560, 0.42, 1, t)
    ripples(c, t, 0, W, 500, 576, n=20, col=(255, 226, 196))
    kitty(c, tl, t, "luna", 560, 640, 1.0, 1, "sit", look=(1, -1), mouth=0, tail=math.sin(t * 1.5))
    kitty(c, tl, t, "whiskers", 720, 640, 1.05, -1, "sit", look=(1, -1), mouth=0)
    D.mouse(c, 640, 640, 0.9, 1, t, eyes="open")
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(640, 74 - 30 * (1 - k), "Whiskers and the", 40, mix((90, 100, 170), (255, 250, 236), k), stroke=3 * k)
    word = "PAINTED WALL"
    size = 66
    n = len(word)
    for i, ch in enumerate(word):
        kk = ease(tl.prog("t_open", t, 0.25 + 0.5 * i / n, 0.4 + 0.5 * i / n))
        if kk <= 0 or ch == " ":
            continue
        x = 640 + (i - (n - 1) / 2) * 50
        y = 150 + 6 * math.sin(t * 3 + i) + 30 * (1 - kk)
        c.text(x, y, ch, size * (0.5 + 0.5 * kk), TITLE_COLS[i % len(TITLE_COLS)], stroke=5)
    return c


# ======================================================================= sill (home)

SILL_Y = 372
WALL_X = 925


def beam_mask():
    def make():
        m = Image.new("L", (W * SS, H * SS), 0)
        ImageDraw.Draw(m).polygon([(990 * SS, 120 * SS), (1060 * SS, 120 * SS), (980 * SS, 372 * SS),
                                   (870 * SS, 372 * SS)], fill=90)
        ImageDraw.Draw(m).ellipse([850 * SS, 352 * SS, 1000 * SS, 386 * SS], fill=150)
        return m.filter(ImageFilter.GaussianBlur(10 * SS))
    return cached("beammask", make)


def room_bg():
    def make():
        c = Canvas(MF.room(False).copy())
        # a little bookshelf and a framed picture of the moon pond (from Film 1)
        c.rect(330, 250, 470, 330, (250, 244, 230), w=3)
        c.rect(340, 260, 460, 320, (60, 70, 120), w=2)
        D.moon(c, 420, 280, 12, sky=(60, 70, 120))
        c.ellipse(390, 308, 30, 6, (240, 236, 200), ol=None)
        c.rect(30, 360, 120, 520, (176, 120, 80), w=3)
        for k, yy in enumerate((400, 450, 500)):
            c.line([(30, yy), (120, yy)], (140, 90, 60), 3, cap=False)
            for j in range(4):
                c.rect(36 + j * 20, yy - 34 + (j % 2) * 4, 50 + j * 20, yy, [(200, 70, 70), (70, 120, 200),
                       (230, 190, 70), (90, 160, 90)][(j + k) % 4], w=1.5)
        return c.img
    return cached("room_day", make)


def sunbeam(c, k=1.0):
    if k > 0:
        c.img.paste((255, 236, 150), (0, 0), beam_mask() if k >= 1 else
                    beam_mask().point(lambda v: int(v * k)))


CUSH = [((80, 140, 220), 0), ((240, 120, 140), 1), ((120, 190, 120), 2)]


def sill_inside(tl, t):
    T = tl.t
    c = Canvas(room_bg().copy())
    sunbeam(c, 1.0)
    # ---- cushions
    built = 0.0
    if t >= T("s_build"):
        built = 3 * tl.prog("s_build", t, 0.05, 0.85)
    for k in range(3):
        if built <= k:                       # still on the pile at the left end (k=0 on top)
            col, pat = CUSH[k]
            P.cushion(c, 782, SILL_Y - 30 * (2 - k), 52, 30, col, pat)
    for k in range(3):
        u = clamp(built - k)
        if u > 0:
            col, pat = CUSH[k]
            px = lerp(782, WALL_X, ease(u))
            py = lerp(SILL_Y, SILL_Y - 32 * k, ease(u)) + arc_y(ease(u), 80)
            P.cushion(c, px, py, 58, 32, col, pat)
    # ---- Whiskers
    bump = T("s_bump", 0.5)
    if t < T("s_bump", 0.05):
        awake = t >= T("s_narr", 0.7)
        if not awake:
            kitty(c, tl, t, "whiskers", 520, 640, 0.95, 1, "sleep")
            D.zzz(c, 560, 560, t)
        else:
            kitty(c, tl, t, "whiskers", 520, 640, 0.95, 1, "crouch", look=(1, -1), eyes="wide")
    elif t < bump:
        u = tl.prog("s_bump", t, 0.05, 0.5)
        D.cat(c, lerp(520, 878, u), lerp(640, SILL_Y, u) + arc_y(u, 170), D.WHISKERS, lerp(0.95, 0.75, u), 1, "leap",
              t=t, seed=0.0)
    else:
        wx = smooth(t, [(bump, 878), (bump + 0.25, 858), (T("s_build"), 858), (T("s_build", 0.15), 848)], r=0.08)
        sq = 1.0 - 0.15 * math.exp(-(t - bump) * 8)
        turned = T("s_wall", 0.6) <= t < T("s_van")
        throwing = T("s_build", 0.05) <= t < T("s_build", 0.9)
        face = -1 if (turned or (throwing and (built % 1) < 0.35)) else 1
        eyes = "wide" if t < bump + 0.8 else ("happy" if T("s_wall") <= t < T("s_wall", 0.6) else "open")
        kitty(c, tl, t, "whiskers", wx, SILL_Y, 0.75, face, "sit", eyes=eyes, squash=sq,
              head_dy=-6 if T("s_wall") <= t < T("s_wall", 1) else 0, look=(1, 0) if not turned else (1, 0.5))
    # ---- Luna
    if t < T("s_bump", 0.1):
        kitty(c, tl, t, "luna", 1190, 640, 0.9, -1, "sit", look=(-1, -1), tail=math.sin(t * 1.2),
              eyes="open" if t > T("s_narr", 0.5) else "closed")
    elif t < bump:
        u = tl.prog("s_bump", t, 0.1, 0.5)
        D.cat(c, lerp(1190, 990, u), lerp(640, SILL_Y, u) + arc_y(u, 160), D.LUNA, lerp(0.9, 0.75, u), -1, "leap",
              t=t, seed=1.3)
    else:
        lx = smooth(t, [(bump, 985), (bump + 0.25, 1005), (T("s_build"), 1005), (T("s_build", 0.15), 1012)], r=0.08)
        sq = 1.0 - 0.15 * math.exp(-(t - bump) * 8)
        turned = T("s_wall", 0.3) <= t < T("s_van")
        eyes = "wide" if t < bump + 0.8 else "open"
        if T("s_wall", 0.3) <= t < T("s_pip"):
            eyes = "closed"
        kitty(c, tl, t, "luna", lx, SILL_Y, 0.75, 1 if turned else -1, "sit", eyes=eyes, squash=sq,
              head_dy=-5 if turned else 0, look=(1, -0.3))
    # ---- Pip: by the plant, then up on top of the cushion wall
    if t < T("s_pip"):
        pip(c, tl, t, 260, 640, 1.0, 1, eyes="open")
    else:
        u = tl.prog("s_pip", t, 0.0, 0.3)
        x = lerp(260, WALL_X, ease(u))
        y = lerp(640, SILL_Y - 100, ease(u)) + arc_y(u, 150)
        pip(c, tl, t, x, y, 0.85, 1 if u < 1 else -1, eyes="open")
    z = 1 + 0.75 * ease(tl.prog("s_bump", t, 0.55, 0.95))
    return zoom(c, 925, 300, z)


# ---- the street outside the house

STREET_Y = 640
VAN_STOP = 790


def street_bg(evening=False):
    def make():
        if evening:
            c = Canvas(sky_img([(0, (110, 120, 200)), (0.5, (240, 170, 160)), (1, (255, 214, 170))]))
        else:
            c = Canvas(sky_img([(0, (110, 180, 240)), (0.6, (196, 228, 250)), (1, (226, 240, 250))]))
        D.cloud(c, 980, 110, 0.8)
        D.cloud(c, 700, 70, 0.5)
        D.tree(c, 1180, 560, 1.1)
        D.tree(c, 640, 560, 0.8, leaf=(110, 176, 96))
        # the cats' house (the window with the sill is the ground-floor one on the left)
        c.rect(-10, 170, 560, 580, (250, 228, 190), w=3)
        c.poly([(-30, 176), (270, 40), (580, 176)], (196, 92, 70), w=3)
        c.rect(380, 70, 420, 130, (170, 80, 60), w=2.5)
        # door
        c.rect(470, 400, 540, 580, (120, 80, 140), w=3, r=4)
        c.circle(526, 494, 5, (250, 210, 70), w=1.5)
        c.rect(462, 392, 548, 402, (230, 210, 170), w=2)
        # a round attic window in the gable
        c.circle(270, 120, 34, (190, 226, 250), w=3)
        c.line([(236, 120), (304, 120)], (250, 250, 250), 4, cap=False)
        c.line([(270, 86), (270, 154)], (250, 250, 250), 4, cap=False)
        c.rect(-10, 170, 560, 186, (226, 200, 160), w=2)
        # the sill window (interior drawn per frame)
        c.rect(150, 560, 560, 584, (200, 190, 170), ol=None)
        # sidewalk + street
        c.rect(-10, 580, W + 10, 610, (210, 206, 200), w=2)
        for x in range(0, W, 80):
            c.line([(x, 580), (x, 610)], (180, 176, 170), 2, cap=False)
        c.rect(-10, 610, W + 10, H + 10, (110, 110, 120), ol=None)
        for x in range(0, W, 120):
            c.rect(x, 670, x + 60, 676, (240, 240, 240), ol=None)
        D.bush(c, 60, 584, 0.8)
        for k, fx in enumerate((200, 250, 300, 350, 400)):
            D.flower(c, fx, 444, [(240, 80, 100), (250, 210, 70), (240, 140, 200)][k % 3], 0.7)
        return c.img
    return cached(("street", evening), make)


WIN_BOX = (150, 270, 430, 440)


def house_window(c, tl, t, cats_fn):
    """The ground-floor window with the room inside and the cats on the sill (drawn by cats_fn)."""
    x0, y0, x1, y1 = WIN_BOX
    c.rect(x0, y0, x1, y1, (236, 214, 176), ol=None)
    c.rect(x0, y1 - 40, x1, y1, (200, 150, 110), ol=None)
    c.rect(x0 + 90, y0 + 30, x0 + 150, y0 + 70, (60, 70, 120), w=2)          # the moon picture
    for side in (0, 1):                                                       # curtains
        xa = x0 if side == 0 else x1 - 34
        c.poly([(xa, y0), (xa + 34, y0), (xa + (24 if side == 0 else 10), y1 - 50), (xa + (side * 34), y1 - 40)],
               (120, 170, 220), w=2)
    cats_fn(c)
    c.rect(x0, y0, x1, y1, None, w=6)
    c.rect(x0 - 12, y1, x1 + 12, y1 + 14, (255, 250, 240), w=2.5, r=3)
    # flower box
    c.rect(x0 + 10, y1 + 14, x1 - 10, y1 + 40, (150, 90, 60), w=2.5)


def van_inside_fn(cats_inside):
    def fn(c):
        P.armchair(c, -150, -92, 0.45)
        P.box(c, -100, -92, 50, 44, None)
        for who, x in cats_inside:
            if who == "pip":
                D.mouse(c, x, -94, 0.9, 1, 0.0)
            else:
                D.cat(c, x, -92, PAL[who], 0.55, 1, "sit", t=0.0, seed=SEED[who], eyes="open")
    return fn


def sill_street(tl, t):
    T = tl.t
    c = Canvas(street_bg().copy())
    # ---- the van arrives, opens, gets loaded, drives away
    arrive = tl.prog("s_van", t, 0.0, 0.6)
    vx = lerp(-500, VAN_STOP, 1 - (1 - arrive) ** 2)
    leave = tl.prog("s_drive", t, 0.45, 1.0)
    vx += 1500 * leave ** 2
    door = ease(tl.prog("s_van", t, 0.65, 0.95)) * (1 - ease(tl.prog("s_drive", t, 0.2, 0.42)))
    wheel = vx / 26
    jl = tl.prog("s_jump", t, 0.0, 0.35)
    jw = tl.prog("s_jump", t, 0.42, 0.78)
    jp = tl.prog("s_drive", t, 0.0, 0.2) if t >= T("s_drive") else 0.0
    inside = []
    if jl >= 1:
        inside.append(("luna", -200))
    if jw >= 1:
        inside.append(("whiskers", -120))
    if jp >= 1:
        inside.append(("pip", -160))
    s_van = 0.8

    # ---- the window with the cats
    def cats_fn(cc):
        cy = WIN_BOX[3]
        look_out = t >= T("s_van", 0.3)
        if jl <= 0:
            kitty(cc, tl, t, "luna", 340, cy, 0.55, 1, "sit", look=(1, 0.3) if look_out else (-1, 0),
                  eyes="wide" if T("s_van", 0.5) <= t < T("s_berlin") else "open")
        if jw <= 0:
            kitty(cc, tl, t, "whiskers", 230, cy, 0.55, 1 if look_out else -1, "sit", look=(1, 0.3),
                  eyes="wide" if T("s_van", 0.5) <= t < T("s_berlin") else "open")
        if t < T("s_wait"):
            pip(cc, tl, t, 288, cy - 2, 0.7, 1)
    house_window(c, tl, t, cats_fn)
    P.moving_van(c, vx, STREET_Y, s_van, door=door, wheel=wheel, inside=van_inside_fn(inside),
                 lights=0.0)
    # leaping cats (outside the window frame)
    dx0, dy0 = vx + (-150) * s_van, STREET_Y - 92 * s_van
    for who, u, x0 in (("luna", jl, 340), ("whiskers", jw, 230)):
        if 0 < u < 1:
            x = lerp(x0, dx0 - 20, u)
            y = lerp(WIN_BOX[3], dy0, u) + arc_y(u, 120)
            D.cat(c, x, y, PAL[who], lerp(0.55, 0.45, u), 1, "leap", t=t, seed=SEED[who])
    # Pip runs: off the sill, down the wall, along the pavement, into the van
    if T("s_wait") <= t < T("s_drive", 0.2):
        u = clamp((t - T("s_wait")) / max(0.1, T("s_drive", 0.2) - T("s_wait")))
        if u < 0.3:
            v = u / 0.3
            x, y = lerp(300, 440, v), lerp(WIN_BOX[3], 596, v) + arc_y(v, 60)
        elif u < 0.8:
            v = (u - 0.3) / 0.5
            x, y = lerp(440, dx0 - 40, v), 596
        else:
            v = (u - 0.8) / 0.2
            x, y = lerp(dx0 - 40, dx0, v), lerp(596, dy0, v) + arc_y(v, 50)
        pip(c, tl, t, x, y, 0.8, 1, walk=x / 5)
    return c


def sill(tl, t):
    T = tl.t
    if t < T("s_van"):
        return finish(sill_inside(tl, t), tl, t, 0.45)
    return finish(sill_street(tl, t), tl, t, 0.45)


# ======================================================================= van

def road_bg():
    WW = 2600

    def make():
        c = Canvas(sky_img([(0, (16, 20, 52)), (0.55, (40, 46, 100)), (1, (70, 70, 130))], w=WW), size=(WW, H))
        D.stars(c, 3, 160, WW, 380)
        for k in range(4):
            hx = k * 700
            c.poly([(hx - 200, 520), (hx + 150, 380), (hx + 520, 520)], (40, 50, 80), ol=None)
        rng = np.random.default_rng(3)
        P.skyline(c, 0, WW, 520, rng, 10, 40, [(36, 40, 70)], win=(250, 220, 150), p=0.2)
        c.rect(0, 520, WW, H, (40, 54, 60), ol=None)
        c.rect(0, 600, WW, H, (50, 50, 60), ol=None)
        for x in range(0, WW, 140):
            c.rect(x, 664, x + 70, 670, (220, 220, 200), ol=None)
        return c.img
    return cached("road", make), WW


def van_inside_bg():
    def make():
        c = Canvas(bg=(120, 86, 60))
        # wooden walls with planks, ribs on the ceiling, a floor
        for x in range(0, W, 70):
            c.line([(x, 0), (x, 620)], (100, 70, 48), 3, cap=False)
        for x in range(60, W, 300):
            c.rect(x, 0, x + 24, 620, (96, 66, 44), w=2)
        c.rect(0, 0, W, 60, (80, 56, 40), ol=None)
        c.rect(0, 610, W, H, (90, 66, 50), w=3)
        for y in range(630, H, 26):
            c.line([(0, y), (W, y)], (76, 54, 40), 2, cap=False)
        # a little vent window high up
        c.rect(590, 90, 690, 140, (40, 50, 90), w=3, r=6)
        # strap
        c.line([(0, 300), (W, 300)], (60, 110, 160), 6, cap=False)
        P.armchair(c, 290, 640, 1.15, col=(140, 80, 150))
        # a laundry basket with a blanket for Luna
        c.ellipse(990, 640, 120, 18, (150, 120, 80), w=2.5)
        c.poly([(870, 640), (890, 560), (1090, 560), (1110, 640)], (190, 160, 110), w=3)
        for k in range(8):
            c.line([(900 + k * 26, 566), (893 + k * 28, 636)], (160, 130, 90), 2, cap=False)
        c.ellipse(990, 562, 104, 16, (90, 140, 200), w=2.5)
        # the wall of boxes
        labels = [["BOOKS", "TOYS"], ["KITCHEN", "FRAGILE", ""], ["SOCKS", "BOOKS"]]
        y = 640
        for row, names in enumerate(labels):
            bw = 210 / len(names)
            for k, name in enumerate(names):
                P.box(c, 535 + bw * (k + 0.5), y, bw - 2, 96 - row * 4, name or None)
            y -= 96 - row * 4
        # floor lamp glow: none -- night
        return c.img
    return cached("vaninside", make)


BOX_TOP = 640 - 96 - 92 - 88


def passing_lights(c, t):
    """Street lights sliding across the inside of the van."""
    for k in range(2):
        u = ((t * 0.28) + k * 0.5) % 1.0
        x = lerp(-300, W + 300, u)
        m = Image.new("L", c.img.size, 0)
        ImageDraw.Draw(m).polygon([((x - 60) * SS, 0), ((x + 60) * SS, 0), ((x + 200) * SS, H * SS),
                                   ((x + 20) * SS, H * SS)], fill=46)
        c.img.paste((255, 220, 150), (0, 0), m)


def van(tl, t):
    T = tl.t
    if t < T("v_ride"):
        bg, WW = road_bg()
        u = tl.prog("v_narr", t)
        cam = (t * 160) % (WW - W)
        c = view(bg, cam)
        c.tint = None
        # street lamps rushing by
        for k in range(4):
            lx = (k * 420 - t * 380) % (W + 400) - 200
            P.gas_lamp(c, lx, 600, 1.2, lit=1.0)
        D.moon(c, 1060, 120, 34, sky=(30, 34, 80))
        # road sign
        sx = lerp(1500, -300, u)
        c.line([(sx, 600), (sx, 470)], (180, 180, 190), 6, cap=False)
        c.rect(sx - 80, 420, sx + 80, 480, (30, 120, 70), w=3, r=6)
        c.text(sx, 450, "BERLIN  ->", 24, (255, 255, 255))
        P.moving_van(c, 560, 640 + 2 * math.sin(t * 9), 0.9, wheel=t * 9, lights=1.0)
        return finish(c, tl, t, 0.4)
    c = Canvas(van_inside_bg().copy())
    sleep = t >= T("v_sleep", 0.15)
    rattle = 2 * math.sin(t * 14)
    # Whiskers on the armchair (left), Luna in the basket (right)
    never = t >= T("v_never1")
    if sleep:
        kitty(c, tl, t, "whiskers", 290, 552 + rattle * 0.3, 0.9, 1, "sleep")
        kitty(c, tl, t, "luna", 990, 566, 0.85, -1, "sleep")
        D.zzz(c, 330, 470, t)
        D.zzz(c, 1020, 480, t + 1)
    else:
        w_face = -1 if never and t >= T("v_never2") else 1
        kitty(c, tl, t, "whiskers", 300, 552 + rattle * 0.3, 0.9, w_face, "sit",
              look=(1, -0.6) if w_face > 0 else (1, 0), head_dy=-6 if t >= T("v_never2") else 0,
              eyes="closed" if t >= T("v_never2", 1) else "open")
        l_face = 1 if never else -1
        kitty(c, tl, t, "luna", 990, 566, 0.85, l_face, "sit", look=(1, -0.6) if l_face < 0 else (1, 0),
              head_dy=-6 if never else 0, eyes="closed" if t >= T("v_never1", 1) else "open")
    # Pip on top of the boxes, running between the two
    keys = [(T("v_ride"), 560), (T("v_run1", 0.1), 560), (T("v_run1", 0.8), 715), (T("v_run2", 0.1), 715),
            (T("v_run2", 0.8), 640)]
    px = smooth(t, keys, r=0.15)
    v = moving(t, keys)
    face = 1 if v > 10 else (-1 if v < -10 else (1 if t < T("v_run2") else 1))
    if T("v_cold") <= t < T("v_run1"):
        face = -1
    if T("v_says") <= t < T("v_run2"):
        face = 1
    py = BOX_TOP + 2
    if sleep:
        pip(c, tl, t, 640, py, 0.9, 1, eyes="closed")
    else:
        pip(c, tl, t, px, py, 0.9, face, walk=px / 5 if abs(v) > 10 else 0.0,
            eyes="happy" if T("v_together") <= t < T("v_never1") else "open")
    passing_lights(c, t)
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, (20, 26, 70)), 0.3)
    c = Canvas(c.img)
    return finish(c, tl, t, 0.4)


# ======================================================================= gate

GW = 2600
GATE_X = 1900
GROUND = 650


def gate_bg():
    def make():
        c = Canvas(sky_img([(0, (96, 168, 236)), (0.6, (190, 224, 250)), (1, (226, 240, 250))], w=GW), size=(GW, H))
        rng = np.random.default_rng(2)
        for _ in range(7):
            D.cloud(c, rng.uniform(0, GW), rng.uniform(50, 200), rng.uniform(0.5, 0.9))
        # far: the TV Tower, the Reichstag behind the trees
        P.tv_tower(c, 180, 560, 420, col=(226, 230, 240), shade=(196, 200, 214), lw=2)
        P.skyline(c, -20, GW + 20, 560, rng, 50, 120, [(206, 210, 226), (196, 202, 220), (214, 216, 230)])
        P.reichstag(c, 800, 560, 0.66, flags=True)
        for x in (330, 420, 1180, 1270, 1360):
            P.linden(c, x + rng.uniform(-20, 20), 600, rng.uniform(0.55, 0.7), leaf=(110, 160, 96),
                     leaf_l=(140, 186, 116))
        c.rect(520, 560, 1080, 600, (150, 196, 120), ol=None)                     # the lawn in front
        for x in range(530, 1080, 60):
            D.bush(c, x, 604, 0.45, col=(100, 160, 90))
        P.skyline(c, 2300, GW + 20, 600, rng, 120, 200, [(236, 222, 200), (226, 214, 196)], win=(120, 140, 170),
                  p=0.4, ol=OUT)
        # the plaza
        c.rect(0, 596, GW, H, (222, 214, 200), ol=None)
        for y in range(610, H, 22):
            c.line([(0, y), (GW, y)], (206, 198, 184), 2, cap=False)
        for x in range(0, GW, 60):
            c.line([(x, 600), (x - 40, H)], (210, 202, 188), 1.5, cap=False)
        c.rect(0, 592, GW, 602, (196, 188, 174), ol=None)
        # the Gate
        P.brandenburg_gate(c, GATE_X, 610, 0.96)
        # street things
        P.linden(c, 140, 640, 1.0)
        P.linden(c, 2520, 640, 1.05)
        P.gas_lamp(c, 1100, 640, 1.1)
        P.gas_lamp(c, 2350, 640, 1.1)
        P.ampelmann(c, 1240, 650, 1.0, green=True)
        return c.img
    return cached("gate_bg", make)


def gate_cam(tl, t):
    T = tl.t
    return smooth(t, [(T("g_open"), 0), (T("g_flag", 0.7), 0), (T("g_look", 0.85), GATE_X - 640),
                      (T("g_sniff", 0.5), GATE_X - 640), (T("g_sniff", 1.0), GATE_X - 400)], r=0.4)


def ghost_wall(c, x0, x1, base, h, a):
    """A see-through grey wall that stood here long ago."""
    if a <= 0.01:
        return c
    m = Image.new("L", c.img.size, 0)
    d = ImageDraw.Draw(m)
    d.rectangle([x0 * SS, (base - h) * SS, x1 * SS, base * SS], fill=int(200 * a))
    c.img.paste((150, 150, 160), (0, 0), m)
    for x in np.arange(x0, x1, 60):
        c.line([(x, base - h), (x, base)], mix((150, 150, 160), (90, 90, 100), a), 2, cap=False)
    c.rect(x0, base - h - 10, x1, base - h + 4, mix((150, 150, 160), (200, 200, 205), a), ol=None, r=6)
    return c


def gate(tl, t):
    T = tl.t
    cam = gate_cam(tl, t)
    c = view(gate_bg(), cam)
    c.tint = None
    # flags flapping by the gate
    for fx in (880, 1440, 2360):
        P.berlin_flag(c, fx - cam, 640, 1.0, t)
    # ---- the van, parked on the left
    door = ease(tl.prog("g_open", t, 0.0, 0.3))
    if cam < 800:
        P.moving_van(c, 380 - cam, 660, 0.72, door=door, wheel=0.0,
                     inside=van_inside_fn([("luna", -200), ("whiskers", -120), ("pip", -160)]
                                          if t < T("g_open", 0.4) else []))
    # ---- the wall that once stood here (Berti tells)
    ga = ease(tl.prog("g_wall", t, 0.15, 0.4)) * (1 - ease(tl.prog("g_glance", t, 0.2, 0.7)))
    ghost_wall(c, GATE_X - 380 - cam, GATE_X + 380 - cam, 640, 300, ga * 0.75)
    # ---- the cats jump out
    jump = tl.prog("g_open", t, 0.38, 0.7)
    dx0, dy0 = 380 - cam + (-150) * 0.72, 660 - 92 * 0.72
    wk = [(T("g_open"), 600), (T("g_look", 0.08), 600), (T("g_look", 0.85), GATE_X - 140),
          (T("g_sniff", 0.35), GATE_X - 140), (T("g_sniff", 1.0), GATE_X + 300)]
    lk = [(T("g_open"), 420), (T("g_look", 0.15), 420), (T("g_look", 0.9), GATE_X + 170)]
    pk = [(T("g_open"), 510), (T("g_look", 0.1), 510), (T("g_look", 0.88), GATE_X + 240)]
    bk = [(T("g_open"), GATE_X + 200), (T("g_narr", 0.6), GATE_X + 200), (T("g_hallo", 0.0), 1600),
          (T("g_hallo", 0.6), 800), (T("g_look", 0.1), 800), (T("g_look", 0.9), GATE_X + 20)]
    glance = T("g_glance") <= t < T("g_glance", 0.45)
    turned = t >= T("g_glance", 0.45) and t < T("g_sniff")
    # Berti
    if t >= T("g_narr", 0.6):
        bx = smooth(t, bk, r=0.3) - cam
        v = moving(t, bk)
        face = -1 if v < -10 else 1
        if abs(v) <= 10:
            face = -1 if t < T("g_look") else (-1 if T("g_horses", 0.5) <= t < T("g_sniff") else 1)
            if T("g_flag", 0.1) <= t < T("g_flag", 0.6):
                face = 1
        arm = 0.0
        wave = False
        if T("g_hallo") <= t < T("g_hallo", 1.0):
            arm, wave = 1.0, True
        if T("g_flag", 0.1) <= t < T("g_flag", 0.7) or T("g_horses", 0.0) <= t < T("g_horses", 0.5):
            arm = 1.0
        bear(c, tl, t, bx, GROUND + 4, 0.92, face, walk=smooth(t, bk) / 14 if abs(v) > 10 else 0.0, arm=arm, wave=wave,
             look=(0, -1) if arm > 0.5 and not wave else (0, 0))
    for who, keys, s in (("luna", lk, 0.85), ("whiskers", wk, 0.9)):
        if jump < 1 and t < T("g_open", 0.7):
            lag = 0.0 if who == "luna" else 0.25
            u = clamp((jump - lag) / 0.75)
            if u <= 0:
                continue
            x = lerp(dx0, keys[0][1] - cam, u)
            y = lerp(dy0, GROUND, u) + arc_y(u, 70)
            D.cat(c, x, y, PAL[who], lerp(0.5, s, u), 1, "leap", t=t, seed=SEED[who])
            continue
        x = smooth(t, keys, r=0.3) - cam
        v = moving(t, keys)
        walking = abs(v) > 15
        face = 1 if v >= 0 else -1
        look = (1, 0)
        eyes = "open"
        if t < T("g_hallo"):
            look = (1, -1)
            eyes = "wide" if T("g_narr", 0.3) <= t < T("g_narr", 1.0) else "open"
        elif not walking:
            bxx = smooth(t, bk, r=0.3) - cam
            face = 1 if bxx > x else -1
            if T("g_horses") <= t < T("g_dayoff", 1.0):
                look = (1, -1)
        if glance:
            face = 1 if who == "luna" and x < (smooth(t, wk, 0.3) - cam) else (1 if who == "luna" else -1)
            face = -1 if who == "luna" else 1
            # they look at each other ... luna is right of whiskers here
        if turned:
            face = 1 if who == "luna" else -1
            eyes = "closed"
        head_dy = 0
        if who == "whiskers" and T("g_sniff") <= t < T("g_sniff", 0.4):
            head_dy, eyes, look, face = -10, "closed", (1, -1), 1
        pose = "walk" if walking else "stand"
        kitty(c, tl, t, who, x, GROUND + (6 if who == "luna" else 0), s, face, pose,
              walk=(x + cam) / (12 * s), look=look, eyes=eyes, head_dy=head_dy)
    if jump >= 0.5:
        x = smooth(t, pk, r=0.3) - cam
        v = moving(t, pk)
        pip(c, tl, t, x, GROUND + 10, 0.8, 1 if v >= 0 else -1, walk=x / 5 if abs(v) > 10 else 0.0)
    # rumbling tummy lines
    if T("g_sniff") <= t < T("g_sniff", 0.5):
        wx = smooth(t, wk, r=0.3) - cam
        for k in range(3):
            c.arc(wx, GROUND - 40, 30 + k * 10, 14 + k * 5, 200, 340, (255, 255, 255), 2)
    z = 1 + 0.9 * ease(tl.prog("g_horses", t, 0.15, 0.45)) * (1 - ease(tl.prog("g_dayoff", t, 0.6, 1.0)))
    c = zoom(c, GATE_X - cam, 130, z)
    return finish(c, tl, t, 0.4)


# ======================================================================= imbiss

STAND_X = 790
COUNTER_Y = 600 - 150 * 0.92


def imbiss_bg():
    def make():
        c = Canvas(sky_img([(0, (100, 172, 238)), (0.6, (196, 226, 250)), (1, (228, 240, 250))]))
        D.cloud(c, 960, 100, 0.7)
        D.cloud(c, 560, 160, 0.5)
        rng = np.random.default_rng(7)
        # Alexanderplatz: tall blocks and the TV Tower
        P.skyline(c, -20, W + 20, 520, rng, 160, 300, [(206, 210, 222), (196, 200, 216), (220, 222, 232)],
                  win=(150, 170, 200), p=0.5, ol=OUT)
        P.tv_tower(c, 240, 600, 760, lw=2.6)
        # the world clock
        c.line([(1120, 600), (1120, 440)], (110, 110, 120), 8, cap=False)
        c.rect(1060, 400, 1180, 440, (230, 200, 120), w=2.5)
        for k in range(6):
            c.rect(1062 + k * 20, 404, 1078 + k * 20, 436, [(240, 120, 90), (120, 180, 220), (240, 220, 120)][k % 3],
                   ol=None)
        c.line([(1120, 400), (1120, 360)], (110, 110, 120), 3, cap=False)
        c.circle(1120, 352, 14, None, ol=(110, 110, 120), w=2)
        c.circle(1120, 352, 4, (240, 200, 70), ol=None)
        # paving
        c.rect(0, 590, W, H, (214, 206, 196), ol=None)
        for y in range(604, H, 24):
            c.line([(0, y), (W, y)], (198, 190, 180), 2, cap=False)
        for x in range(0, W, 70):
            c.line([(x, 592), (x - 30, H)], (204, 196, 186), 1.5, cap=False)
        c.rect(0, 586, W, 596, (190, 182, 172), ol=None)
        P.linden(c, 1230, 640, 0.9)
        P.imbiss(c, STAND_X, 600, 0.92, t=0.0)
        return c.img
    return cached("imbiss_bg", make)


WH_X, LU_X = 470, 1080


def imbiss(tl, t):
    T = tl.t
    c = Canvas(imbiss_bg().copy())
    # ---- what Hilde hands over
    hand = None
    pret_u = tl.prog("i_pretzel", t, 0.0, 0.18)
    donut_u = tl.prog("i_donut", t, 0.0, 0.2)
    if T("i_pretzel") <= t < T("i_pretzel", 0.18):
        hand = "pretzel"
    if T("i_donut") <= t < T("i_donut", 0.2):
        hand = "donut"
    hreach = 0.0
    if hand == "pretzel":
        hreach = math.sin(math.pi * pret_u)
    elif hand == "donut":
        hreach = math.sin(math.pi * donut_u)

    def hold(cc, x, y):
        if hand == "pretzel" and pret_u < 0.5:
            P.pretzel(cc, x + 30, y - 10, 0.8)
        if hand == "donut" and donut_u < 0.5:
            P.berliner(cc, x + 20, y, 0.9)
    hilde_talk = tl.mouth("hilde", t)
    P.hilde(c, STAND_X + 30, COUNTER_Y, 1.05, -1, t, mouth=hilde_talk, lean=max(hreach, 0.4 if tl.talking("hilde", t) else 0),
            arm=hreach, hold=hold,
            eyes="happy" if T("i_necklace") <= t < T("i_purpose", 1) or T("i_notpurpose") <= t < T("i_train") else "open")
    # ---- Whiskers walks in, sits facing the stand
    wk = [(T("i_narr"), -120), (T("i_narr", 0.8), WH_X), (T("i_off"), WH_X)]
    wx = smooth(t, wk, r=0.3)
    walking = abs(moving(t, wk)) > 15
    ws = 1.0
    sx_head = wx + 18 * ws
    sy_head = 650 - 106 * ws
    eyes = "open"
    head_dy = 0
    if T("i_narr") <= t < T("i_narr", 0.8):
        head_dy, eyes = -8, "closed"
    if T("i_pretzel", 0.62) <= t < T("i_necklace"):
        eyes = "wide"
    if T("i_purpose") <= t < T("i_purpose", 1):
        eyes, head_dy = "happy", -8
    if T("i_jam") <= t < T("i_notpurpose", 1):
        eyes = "wide"
    if t >= T("i_off"):
        eyes = "open"
        head_dy = 6
    # the pretzel: flying in, held, bitten, popped over the head
    p_fly = tl.prog("i_pretzel", t, 0.12, 0.24)
    worn = t >= T("i_pretzel", 0.62)
    if worn:
        P.pretzel_ring(c, sx_head - 2, 650 - 70 * ws, 0.95, "back")
    if walking:
        kitty(c, tl, t, "whiskers", wx, 650, ws, 1, "walk", walk=wx / 12, head_dy=head_dy, eyes=eyes)
    else:
        wob = 0.0
        if worn:
            wob = 3 * math.sin(t * 12) * math.exp(-(t - T("i_pretzel", 0.62)) * 2)
        kitty(c, tl, t, "whiskers", wx + wob, 650, ws, 1, "sit", head_dy=head_dy, eyes=eyes,
              look=(1, -0.5) if t < T("i_pretzel") else (1, 0))
    if worn:
        P.pretzel_ring(c, sx_head - 2, 650 - 70 * ws, 0.95, "front")
    if T("i_pretzel", 0.12) <= t < T("i_pretzel", 0.62):
        if p_fly < 1:
            px = lerp(STAND_X - 140, sx_head + 40, p_fly)
            py = lerp(COUNTER_Y - 60, sy_head + 10, p_fly) + arc_y(p_fly, 60)
            P.pretzel(c, px, py, 0.8)
        else:
            u = tl.prog("i_pretzel", t, 0.5, 0.62)
            px = sx_head + 40 - 40 * u
            py = sy_head + 10 - 90 * math.sin(math.pi * u) + 20 * u
            P.pretzel(c, px, py, 0.8)
            if T("i_pretzel", 0.25) <= t < T("i_pretzel", 0.5):
                # crumbs flying
                for k in range(4):
                    cu = ((t - T("i_pretzel", 0.25)) * 2 + k * 0.25) % 1.0
                    c.circle(px - 30 + 20 * k, py + 30 + 40 * cu, 3, P.PRETZEL_L, ol=None)
    # the doughnut
    d_fly = tl.prog("i_donut", t, 0.12, 0.3)
    if T("i_donut", 0.12) <= t < T("i_jam"):
        px = lerp(STAND_X - 140, sx_head + 40, d_fly)
        py = lerp(COUNTER_Y - 40, sy_head + 22, d_fly) + arc_y(d_fly, 60)
        P.berliner(c, px, py, 0.9, bite=1.0 if t >= T("i_donut", 0.45) else 0.0)
    # the jam squirt arcs across to Luna
    lx = smooth(t, [(T("i_narr"), LU_X), (T("i_train", 0.6), LU_X), (T("i_off", 1.0), 1500)], r=0.3)
    j = tl.prog("i_donut", t, 0.45, 0.58)
    if T("i_donut", 0.45) <= t < T("i_donut", 0.58):
        for k in range(6):
            u = clamp(j - k * 0.05)
            if u <= 0:
                continue
            x = lerp(sx_head + 60, lx + 6, u)
            y = lerp(sy_head + 20, 650 - 100, u) + arc_y(u, 120)
            c.circle(x, y, 13 - k, P.JAM, w=1.5)
    jam_k = 0.0
    if t >= T("i_donut", 0.58):
        jam_k = 1.0 - ease(tl.prog("i_train", t, 0.1, 0.4))
    # ---- Luna and Pip (on the right), then off to the train
    lv = moving(t, [(T("i_narr"), LU_X), (T("i_train", 0.6), LU_X), (T("i_off", 1.0), 1500)])
    lwalk = abs(lv) > 15
    leyes = "open"
    if T("i_jam") <= t < T("i_train"):
        leyes = "closed"
    if lwalk:
        kitty(c, tl, t, "luna", lx, 652, 0.95, 1, "walk", walk=lx / 12, head_dy=-4)
    else:
        kitty(c, tl, t, "luna", lx, 652, 0.95, -1, "sit", eyes=leyes, look=(1, 0),
              head_dy=-5 if T("i_jam") <= t < T("i_train") else 0)
    if jam_k > 0.02:
        P.jam_blob(c, lx - 30 * 0.95, 652 - 108 * 0.95, 1.0, jam_k)
        P.jam_blob(c, lx - 8, 652 - 130, 0.6, jam_k)
    pxk = smooth(t, [(T("i_narr"), LU_X + 90), (T("i_train", 0.7), LU_X + 90), (T("i_off", 1.0), 1560)], r=0.3)
    pv = moving(t, [(T("i_narr"), LU_X + 90), (T("i_train", 0.7), LU_X + 90), (T("i_off", 1.0), 1560)])
    laughing = T("i_necklace") <= t < T("i_purpose")
    pip(c, tl, t, pxk, 654, 0.85, 1 if pv > 10 else -1, walk=pxk / 5 if abs(pv) > 10 else 0.0,
        eyes="happy" if laughing else "open", hop=abs(math.sin(t * 10)) * 8 if laughing else None)
    # ---- Berti, on the left, a bit behind
    bk = [(T("i_narr"), -240), (T("i_narr", 0.9), 250), (T("i_off"), 250)]
    bxx = smooth(t, bk, r=0.3)
    bv = moving(t, bk)
    bear(c, tl, t, bxx, 640, 0.9, 1, walk=bxx / 14 if abs(bv) > 10 else 0.0,
         eyes="happy" if T("i_necklace") <= t < T("i_purpose") else "open",
         arm=0.6 if t >= T("i_off", 0.3) else 0.0)
    return finish(c, tl, t, 0.45)


# ======================================================================= ubahn

DECK_Y = 470 - 170 - 18          # top of the bridge arcade in the wide shot


def bridge_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 176, 238)), (0.55, (200, 226, 250)), (1, (230, 242, 250))]))
        D.cloud(c, 260, 90, 0.8)
        D.cloud(c, 1060, 130, 0.6)
        rng = np.random.default_rng(9)
        P.tv_tower(c, 1130, 420, 420, col=(226, 230, 240), shade=(196, 200, 214), lw=2)
        P.skyline(c, -20, W + 20, 430, rng, 50, 130, [(206, 196, 196), (196, 188, 190), (216, 206, 200)],
                  win=(150, 160, 190), p=0.3)
        # river banks
        c.rect(0, 420, W, 440, (150, 160, 140), ol=None)
        river(c, 0, W, 440, 640, np.random.default_rng(10), n=110)
        P.oberbaum(c, 640, 470, 1.0, span=700)
        # near bank: a riverside path with grass
        c.poly([(0, 640), (W, 620), (W, H), (0, H)], (120, 176, 100), w=2.5)
        c.poly([(0, 664), (W, 646), (W, 690), (0, 708)], (214, 200, 170), w=2)
        for x in (90, 1180):
            D.bush(c, x, 650, 0.8)
        return c.img
    return cached("bridge_bg", make)


def bridge_wide(tl, t, train_u, walkers=None):
    c = Canvas(bridge_bg().copy())
    ripples(c, t, 0, W, 450, 630, n=30)
    # a sightseeing boat
    bx = (t * 40) % (W + 600) - 300
    P.river_boat(c, W - bx, 600, 0.5, -1, t)
    # the train on the top deck (drawn over the arcade, under the tower tops it passes in front of)
    tx = lerp(-700, W + 1100, train_u)
    P.ubahn_train(c, tx, DECK_Y + 4, 0.42, cars=3)
    if walkers:
        walkers(c)
    return c


def platform_bg():
    def make():
        c = Canvas(sky_img([(0, (120, 180, 238)), (1, (210, 232, 250))]))
        rng = np.random.default_rng(13)
        P.skyline(c, -20, W + 20, 360, rng, 60, 160, [(210, 200, 196), (196, 190, 196)], win=(150, 160, 190), p=0.3)
        P.tv_tower(c, 1080, 360, 330, col=(226, 230, 240), shade=(196, 200, 214), lw=2)
        # station roof and posts
        c.rect(-10, 40, W + 10, 70, (70, 90, 110), w=3)
        for x in (60, 640, 1220):
            c.rect(x - 8, 70, x + 8, 560, (90, 110, 130), w=2.5)
        # the station sign
        c.rect(180, 110, 520, 160, (250, 250, 250), w=3, r=6)
        c.rect(196, 120, 232, 150, P.UBLUE, w=2, r=3)
        c.text(214, 135, "U", 22, (255, 255, 255))
        c.text(370, 135, "Warschauer Str.", 22, (40, 50, 80))
        # track bed
        c.rect(-10, 530, W + 10, 560, (90, 84, 80), ol=None)
        # platform (in front)
        c.rect(-10, 560, W + 10, H + 10, (196, 196, 200), w=2.5)
        c.rect(-10, 560, W + 10, 576, (250, 220, 60), ol=None)
        for x in range(0, W, 100):
            c.line([(x, 576), (x - 30, H)], (180, 180, 186), 2, cap=False)
        return c.img
    return cached("platform_bg", make)


TRAIN_S = 1.4
DOOR_R = 640 + 0.5 * 220 * TRAIN_S         # right door of the middle car (screen x)


def ubahn(tl, t):
    T = tl.t
    if t < T("u_board"):
        u = tl.prog("u_narr", t, 0.0, 1.0)
        return finish(bridge_wide(tl, t, u * 0.9), tl, t, 0.4)
    if t >= T("u_river"):
        def walkers(cc):
            u = tl.prog("u_river", t)
            x = lerp(200, 820, u)
            bear(cc, tl, t, x - 70, 690, 0.45, 1, walk=x / 7)
            kitty(cc, tl, t, "whiskers", x, 690, 0.45, 1, "walk", walk=x / 6)
        u = tl.prog("u_river", t)
        return finish(bridge_wide(tl, t, 0.55 + 0.45 * u, walkers), tl, t, 0.4)
    c = Canvas(platform_bg().copy())
    # ---- the train: waiting, doors close, then it leaves to the right
    go = tl.prog("u_gone", t, 0.05, 0.85)
    tx = 640 + 1900 * go ** 2
    doors = 1.0 - ease(tl.prog("u_board", t, 0.72, 0.88))
    board = tl.prog("u_board", t, 0.0, 0.6)
    inside_cats = board >= 1

    def inside(cc, dx):
        if dx > 0 and inside_cats:
            D.cat(cc, dx - 4, -32, D.LUNA, 0.62, -1, "sit", t=t, seed=1.3, look=(-1, 0))
            D.mouse(cc, dx + 18, -32, 0.6, -1, t)
    P.ubahn_train(c, tx + 452 * TRAIN_S, 560, TRAIN_S, cars=3, doors=doors, inside=inside)
    # Luna's face at the door window once the doors are shut
    if inside_cats and doors < 0.05:
        dxs = tx + 0.5 * 220 * TRAIN_S
        x0, y0 = dxs - 20 * TRAIN_S, 560 + (-150 + 22) * TRAIN_S
        x1, y1 = dxs + 20 * TRAIN_S, 560 + (-150 + 70) * TRAIN_S
        if -100 < x0 < W + 100:
            def face(tc):
                tc.rect(x0 - 10, y0 - 10, x1 + 10, y1 + 10, (150, 196, 220), ol=None)
                D.cat(tc, dxs + 13, (y0 + y1) / 2 + 106 * 0.72 + 6, D.LUNA, 0.72, -1, "sit", t=t, seed=1.3, look=(-1, 0),
                      eyes="open", mouth=tl.mouth("luna", t))
                tc.line([(x0 + 4, y1 - 6), (x0 + 20, y0 + 8)], (240, 250, 255), 2, cap=False)
            P.clip_draw(c, max(0, x0), y0, min(W, x1), y1, face)
    # ---- Luna and Pip walk to the door and climb in
    if not inside_cats:
        u = board
        if u < 0.75:
            v = u / 0.75
            x = lerp(-100, DOOR_R - 10, ease(v))
            kitty(c, tl, t, "luna", x, 668, 0.85, 1, "walk", walk=x / 10, head_dy=-4)
            pip(c, tl, t, x - 70, 672, 0.8, 1, walk=x / 5)
        else:
            v = (u - 0.75) / 0.25
            x = DOOR_R - 10
            D.cat(c, x, lerp(668, 560 - 30, v) + arc_y(v, 40), D.LUNA, lerp(0.85, 0.65, v), 1, "leap", t=t, seed=1.3)
            D.mouse(c, lerp(x - 70, x + 20, v), lerp(672, 530, v) + arc_y(v, 60), 0.7, 1, t)
    # ---- Whiskers runs in, too late; then watches the train leave
    wk = [(T("u_board", 0.55), -150), (T("u_board", 1.0), 560), (T("u_gone", 0.1), 560), (T("u_gone", 0.4), 820),
          (T("u_gone", 0.6), 860)]
    wx = smooth(t, wk, r=0.2)
    wv = moving(t, wk)
    sad = t >= T("u_gone", 0.6)
    if abs(wv) > 15:
        kitty(c, tl, t, "whiskers", wx, 672, 0.95, 1, "walk", walk=wx / 11)
        if t < T("u_board", 0.95):       # still licking jam
            P.jam_blob(c, wx + 75, 672 - 92, 0.5, 1.0)
    else:
        kitty(c, tl, t, "whiskers", wx, 672, 0.95, 1, "sit" if sad else "stand",
              eyes="wide" if T("u_wait") <= t < T("u_gone", 0.5) else "open", head_dy=8 if sad else 0,
              look=(1, 0.6) if sad else (1, 0))
    # ---- Berti arrives and comforts him
    bk = [(T("u_gone", 0.5), -200), (T("u_gone", 1.0), wx - 160), (T("u_walk", 1.0), wx - 160)]
    if t >= T("u_gone", 0.5):
        bxx = smooth(t, bk, r=0.2)
        bv = moving(t, bk)
        bear(c, tl, t, bxx, 668, 0.95, 1, walk=bxx / 14 if abs(bv) > 10 else 0.0,
             arm=0.45 if abs(bv) <= 10 else 0.0)
    return finish(c, tl, t, 0.45)


# ======================================================================= gallery

GAL_BASE = 600
GAL_PLAN = [("doves", 3, 1), ("rainbow", 4, 2), ("faces", 4, 3), ("hearts", 3, 4), ("sun", 3, 5), ("car", 3, 6),
            ("bubbles", 3, 7), ("hands", 3, 8), ("cats", 3, 9), ("flowers", 4, 10), ("bear", 2, 11)]
GAL_X0 = 60
GAL_WW = GAL_X0 + sum(n for _, n, _ in GAL_PLAN) * P.SEG + 140
PANEL_X0 = GAL_X0 + sum(n for k, n, _ in GAL_PLAN[:8]) * P.SEG
PANEL_X1 = PANEL_X0 + 3 * P.SEG
PANEL_TOP = GAL_BASE - P.WALL_H
GAL_END_CAM = (PANEL_X0 + PANEL_X1) / 2 - 640


def gallery_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 180, 240)), (0.6, (200, 228, 250)), (1, (230, 242, 250))], w=GAL_WW),
                   size=(GAL_WW, H))
        rng = np.random.default_rng(21)
        for _ in range(9):
            D.cloud(c, rng.uniform(0, GAL_WW), rng.uniform(50, 200), rng.uniform(0.5, 0.9))
        P.skyline(c, -20, GAL_WW + 20, 380, rng, 60, 160, [(210, 206, 214), (200, 198, 210), (220, 214, 214)],
                  win=(160, 170, 196), p=0.3)
        P.tv_tower(c, PANEL_X1 + 260, 380, 360, col=(226, 230, 240), shade=(196, 200, 214), lw=2)
        P.tv_tower(c, 900, 380, 300, col=(226, 230, 240), shade=(196, 200, 214), lw=2)
        for x in range(0, GAL_WW, 160):
            P.linden(c, x + rng.uniform(-30, 30), 360, rng.uniform(0.5, 0.65), leaf=(120, 170, 104),
                     leaf_l=(150, 190, 124))
        P.wall_run(c, GAL_X0, GAL_X0 + sum(n for _, n, _ in GAL_PLAN) * P.SEG, GAL_BASE,
                   [(k if k != "cats" else "blank", n, s) for k, n, s in GAL_PLAN])
        # pavement
        c.rect(0, GAL_BASE, GAL_WW, H, (204, 200, 196), ol=None)
        for y in range(GAL_BASE + 16, H, 26):
            c.line([(0, y), (GAL_WW, y)], (190, 186, 182), 2, cap=False)
        c.rect(0, GAL_BASE, GAL_WW, GAL_BASE + 8, (170, 166, 160), ol=None)
        for x in range(500, GAL_WW, 900):
            P.gas_lamp(c, x, 700, 1.1)
        return c.img
    return cached("gallery_bg", make)


def gal_cam(tl, t):
    T = tl.t
    return smooth(t, [(T("ga_narr"), 0), (T("ga_piece", 0.2), 120), (T("ga_smile"), 300),
                      (T("ga_walk", 1.0), GAL_END_CAM - 200), (T("ga_cushions", 1.0), GAL_END_CAM - 120),
                      (T("ga_brush", 1.0), GAL_END_CAM)], r=0.4)


def storybook_bg():
    def make():
        c = Canvas(bg=(60, 44, 40))
        c.rect(40, 30, W - 40, H - 30, (246, 232, 200), w=3, r=10)
        c.rect(70, 60, W - 70, H - 60, (236, 218, 180), w=2, r=8)
        c.circle(1060, 150, 40, (240, 200, 120), ol=None)
        D.cloud(c, 260, 140, 0.7, (250, 240, 220))
        for hx in (140, 240, 330, 940, 1040, 1130):
            c.rect(hx - 34, 380, hx + 34, 470, (214, 186, 150), w=2)
            c.poly([(hx - 40, 382), (hx, 344), (hx + 40, 382)], (190, 120, 90), w=2)
            c.rect(hx - 10, 410, hx + 10, 440, (150, 120, 100), ol=None)
        c.rect(70, 470, W - 70, H - 60, (206, 190, 150), ol=None)
        c.rect(70, 60, W - 70, H - 60, None, w=2, r=8)
        return c.img
    return cached("storybook", make)


SEPIA = ((150, 110, 70), 0.35)


def friend(c, x, y, kind, t, cheer=0.0, sad=0.0, face=1, seed=0.0):
    """Little storybook animals: a bunny, a fox, a duck, a bear."""
    c.push(x, y - abs(math.sin(t * 7 + seed)) * 10 * cheer, 1.0, flip=face < 0)
    cols = {"bunny": (240, 236, 230), "fox": (230, 130, 70), "duck": (250, 220, 90), "bear": (150, 100, 60)}
    col = cols[kind]
    c.ellipse(0, -30, 22, 30, col, w=2.5)
    hy = -74 + 6 * sad
    if kind == "bunny":
        for ex in (-8, 8):
            c.ellipse(ex, hy - 30, 6, 20, col, w=2)
    elif kind == "fox":
        for ex in (-12, 12):
            c.poly([(ex - 7, hy - 10), (ex, hy - 32), (ex + 7, hy - 10)], col, w=2)
    elif kind == "bear":
        for ex in (-14, 14):
            c.circle(ex, hy - 16, 8, col, w=2)
    c.circle(0, hy, 20, col, w=2.5)
    if kind == "duck":
        c.ellipse(16, hy + 4, 12, 6, (240, 150, 50), w=2)
    elif kind == "fox":
        c.poly([(10, hy - 2), (30, hy + 6), (10, hy + 12)], col, w=2)
        c.circle(29, hy + 6, 3, OUT, ol=None)
    else:
        c.circle(14, hy + 4, 3, OUT, ol=None)
    for ex in (-5, 8):
        if cheer > 0.3:
            c.arc(ex, hy - 4, 4, 4, 200, 340, OUT, 2)
        else:
            c.circle(ex, hy - 4, 2.5, OUT, ol=None)
    if sad > 0.3:
        c.arc(4, hy + 12, 6, 4, 200, 340, OUT, 2)
        c.circle(-6, hy + 4 + (t * 20 % 12), 2, (110, 170, 230), ol=None)
    else:
        c.arc(4, hy + 8, 6, 4, 20, 160, OUT, 2)
    # arm: waving or hugging
    a = -1.2 + 0.4 * math.sin(t * 6 + seed) if sad < 0.5 else 0.6
    c.line([(10, -44), (10 + 22 * math.cos(a), -44 + 22 * math.sin(a))], col, 6)
    c.pop()


def storybook(tl, t):
    """The story of the Wall, told as a picture-book page."""
    T = tl.t
    c = Canvas(storybook_bg().copy())
    fall = ease(tl.prog("ga_apart", t, 0.5, 0.75))
    hug = ease(tl.prog("ga_apart", t, 0.7, 1.0))
    # the grey wall across the middle, crumbling into blocks
    rng = np.random.default_rng(4)
    if hug < 0.45:
        fade = 1 - clamp(hug / 0.45)
        for j in range(9):
            for k in range(3):
                bx = 584 + k * 40 + (20 if j % 2 else 0) - 20
                by = 470 - 34 * (j + 0.5)
                dx = rng.uniform(-1, 1) * 200 * fall
                ty = 470 - 12 - rng.uniform(0, 30)
                cx = bx + dx
                cy = lerp(by, ty, fall)
                rot = rng.uniform(-0.6, 0.6) * fall
                w2, h2 = 19 * fade + 1, 16 * fade + 1
                cr, sr = math.cos(rot), math.sin(rot)
                pts = [(cx + px * cr - py * sr, cy + px * sr + py * cr)
                       for px, py in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
                c.poly(pts, (170, 168, 166), w=2)
    if hug > 0.3:
        sparkles(c, t, 520, 760, 380, 470, n=14, seed=5, col=(255, 220, 120))
    # friends on both sides: sad and waving, then running together for a hug
    left = [("bunny", 380, 0.0), ("bear", 470, 1.0)]
    right = [("fox", 800, 2.0), ("duck", 890, 3.0)]
    for kind, x, sd in left:
        xx = lerp(x, 600 + (x - 380) * 0.4, hug)
        friend(c, xx, 470, kind, t, cheer=hug, sad=1 - fall, face=1, seed=sd)
    for kind, x, sd in right:
        xx = lerp(x, 680 + (x - 800) * 0.4, hug)
        friend(c, xx, 470, kind, t, cheer=hug, sad=1 - fall, face=-1, seed=sd)
    if hug > 0.3:
        hearts_up(c, t, 640, 330, k=1.0, n=5)
    c.text(640, 530, "Friends apart..." if fall < 0.5 else "...friends together!", 34, (110, 80, 50))
    return c


def gallery(tl, t):
    T = tl.t
    if T("ga_apart") <= t < T("ga_smile"):
        return finish(storybook(tl, t), tl, t, 0.35)
    cam = gal_cam(tl, t)
    c = view(gallery_bg(), cam)
    # Whiskers' painting grows on the blank panel
    prog = 0.0
    if t >= T("ga_paint"):
        prog = tl.prog("ga_paint", t, 0.05, 0.95)
    if prog > 0:
        x0, x1 = PANEL_X0 - cam, PANEL_X1 - cam
        P.clip_draw(c, max(0, x0), PANEL_TOP, min(W, x1), GAL_BASE,
                    lambda tc: (P.mural(tc, "blank", x0, x1, PANEL_TOP, GAL_BASE),
                                P.painted_cats(tc, x0, x1, PANEL_TOP, GAL_BASE, prog)))
    # ---- Whiskers and Berti walk along the wall
    sx = PANEL_X0 - 60
    wk = [(T("ga_narr"), 40), (T("ga_narr", 1.0), 520), (T("ga_smile"), 620), (T("ga_walk", 1.0), GAL_END_CAM + 330),
          (T("ga_cushions", 0.5), GAL_END_CAM + 420), (T("ga_brush", 0.6), GAL_END_CAM + 420),
          (T("ga_brush", 1.0), sx)]
    bk = [(T("ga_narr"), -120), (T("ga_narr", 1.0), 380), (T("ga_smile"), 470), (T("ga_walk", 1.0), GAL_END_CAM + 180),
          (T("ga_cushions", 0.5), GAL_END_CAM + 260)]
    painting = T("ga_paint") <= t < T("ga_luna", 0.4)
    wx = smooth(t, wk, r=0.35) - cam
    wv = moving(t, wk)
    sorry = t >= T("ga_luna", 0.4)
    hugk = ease(tl.prog("ga_hug", t, 0.0, 0.4))
    # ladder of paint buckets that Whiskers stands on
    pots_on = t >= T("ga_brush", 0.4)
    if pots_on:
        for k, col in enumerate(((230, 60, 70), (250, 200, 60), (70, 140, 220), (120, 190, 90))):
            P.paint_pot(c, PANEL_X1 + 30 + k * 34 - cam, 660, col)
        c.rect(sx - 60 - cam, 600, sx + 60 - cam, 660, (180, 130, 80), w=2.5)          # a crate to stand on
        c.text(sx - cam, 630, "FARBE", 14, (110, 70, 40))
    if painting:
        # standing on the crate, brush in mouth, painting
        tip_keys = [(0.0, (0.22, 0.22)), (0.15, (0.4, 0.6)), (0.3, (0.3, 0.75)), (0.45, (0.4, 0.55)),
                    (0.6, (0.62, 0.75)), (0.75, (0.72, 0.55)), (0.86, (0.55, 0.2)), (1.0, (0.55, 0.25))]
        u = tl.prog("ga_paint", t, 0.05, 0.95)
        tu = track(u, [(a, b[0]) for a, b in tip_keys])
        tv = track(u, [(a, b[1]) for a, b in tip_keys])
        tx = PANEL_X0 - cam + (PANEL_X1 - PANEL_X0) * tu + 8 * math.sin(t * 12)
        ty = PANEL_TOP + P.WALL_H * tv + 6 * math.cos(t * 12)
        hx, hy = wx + 18 * 0.95 + 17 * 0.95, 600 - 106 * 0.95 + 15 * 0.95
        kitty(c, tl, t, "whiskers", wx, 600, 0.95, 1, "sit", look=(1, -0.5), eyes="open")
        c.line([(hx, hy), (tx, ty)], (150, 100, 60), 5)
        c.circle(tx, ty, 7, (240, 90, 100), w=1.5)
    else:
        face = 1
        eyes = "open"
        head_dy = 0
        pose = "walk" if abs(wv) > 15 else "stand"
        if T("ga_cushions") <= t < T("ga_paint"):
            pose, head_dy = "sit", 10
            face = -1 if t < T("ga_brush") else 1
        if sorry:
            face = 1
            pose = "sit" if hugk < 1 else "sit"
            eyes = "happy" if t >= T("ga_hug") else "open"
            wx = lerp(wx, wx + 40, hugk)
        y = 600 if t < T("ga_luna", 0.4) and t >= T("ga_paint") else 668
        if T("ga_luna", 0.4) > t >= T("ga_luna") or (t >= T("ga_luna", 0.4) and t < T("ga_luna", 0.4) + 0.01):
            y = 600
        if sorry:
            hop = tl.prog("ga_luna", t, 0.4, 0.9)
            y = lerp(600, 668, hop) + arc_y(hop, 50) if hop < 1 else 668
        kitty(c, tl, t, "whiskers", wx, y, 0.95, face, pose, walk=(wx + cam) / 12, eyes=eyes, head_dy=head_dy,
              look=(1, 0.5) if head_dy > 0 else (1, 0))
    # Berti
    bxx = smooth(t, bk, r=0.35) - cam
    bv = moving(t, bk)
    bface = 1
    if T("ga_cushions") <= t < T("ga_paint"):
        bface = 1
    if t >= T("ga_paint"):
        bface = 1
    clap = 0.0
    if T("ga_down") <= t:
        clap = 0.5 + 0.5 * math.sin(t * 14)
    bear(c, tl, t, bxx, 664, 0.95, bface, walk=(bxx + cam) / 14 if abs(bv) > 10 else 0.0,
         arm=1.0 if T("ga_brush") <= t < T("ga_brush", 0.7) else (0.7 if T("ga_piece") <= t < T("ga_piece", 0.7) else 0.0),
         brush=T("ga_brush") <= t < T("ga_brush", 0.7), clap=clap,
         eyes="happy" if t >= T("ga_hug") else "open", look=(0, -1) if T("ga_narr", 0.5) <= t < T("ga_apart") else (0, 0))
    # ---- Luna and Pip arrive from the right
    if t >= T("ga_paint", 0.85):
        lend = wx + cam + 150 - 40 * hugk
        lk = [(T("ga_paint", 0.85), GAL_END_CAM + W + 100), (T("ga_luna", 0.3), GAL_END_CAM + 1010),
              (T("ga_luna", 1.0), GAL_END_CAM + 1010), (T("ga_sorry", 0.6), lend + 20), (T("ga_hug", 0.4), lend)]
        lx = smooth(t, lk, r=0.3) - cam
        lv = moving(t, lk)
        leyes = "happy" if t >= T("ga_missed", 0.5) else ("wide" if T("ga_luna") <= t < T("ga_sorry") else "open")
        if abs(lv) > 15:
            kitty(c, tl, t, "luna", lx, 670, 0.92, -1, "walk", walk=(lx + cam) / 11)
        else:
            kitty(c, tl, t, "luna", lx, 670, 0.92, -1, "sit", eyes=leyes,
                  look=(-1, -1) if T("ga_luna") <= t < T("ga_sorry") else (1, 0))
        pk = [(T("ga_paint", 0.85), GAL_END_CAM + W + 200), (T("ga_luna", 0.3), GAL_END_CAM + 1110),
              (T("ga_down"), GAL_END_CAM + 1110)]
        pxx = smooth(t, pk, r=0.3) - cam
        pv = moving(t, pk)
        cheer = t >= T("ga_down")
        pip(c, tl, t, pxx, 674, 0.9, -1, walk=(pxx + cam) / 5 if abs(pv) > 10 else 0.0,
            eyes="happy" if cheer else "open", hop=abs(math.sin(t * 9)) * 22 if cheer else None)
        if t >= T("ga_hug"):
            hearts_up(c, t, (wx + lx) / 2, 520, k=1.0, n=4)
    return finish(c, tl, t, 0.4)


# ======================================================================= tower

TH = 1700
TOWER_BASE = TH - 90
TOWER_H = 1560
SPHERE_Y = TOWER_BASE - 640 * TOWER_H / 1000


def tower_bg():
    def make():
        c = Canvas(sky_img([(0, (30, 34, 90)), (0.45, (90, 70, 150)), (0.75, (230, 130, 120)), (1, (255, 190, 130))],
                           h=TH), size=(W, TH))
        D.stars(c, 6, 120, W, 700)
        D.moon(c, 1080, 220, 36, sky=(36, 40, 96))
        rng = np.random.default_rng(31)
        P.skyline(c, -20, W + 20, TOWER_BASE - 40, rng, 60, 200, [(70, 60, 110), (80, 66, 120), (60, 54, 100)],
                  win=(255, 214, 140), p=0.35)
        P.berliner_dom(c, 1040, TOWER_BASE + 10, 0.8, col=(110, 96, 130), dome=(80, 110, 120))
        P.tv_tower(c, 640, TOWER_BASE, TOWER_H, lit=1.0, col=(226, 222, 236), shade=(180, 176, 206), lw=3, beacon=False)
        rng = np.random.default_rng(32)
        P.skyline(c, -20, W + 20, TH, rng, 40, 110, [(56, 50, 90), (66, 56, 100)], win=(255, 220, 150), p=0.4,
                  ol=OUT)
        c.rect(0, TOWER_BASE, W, TH, (120, 110, 130), ol=None)
        for y in range(TOWER_BASE + 14, TH, 20):
            c.line([(0, y), (W, y)], (110, 100, 120), 2, cap=False)
        P.tv_tower(c, 640, TOWER_BASE, TOWER_H, lit=1.0, col=(226, 222, 236), shade=(180, 176, 206), lw=3,
                   beacon=False)
        return c.img
    return cached("tower_bg", make)


def tower_out(tl, t):
    T = tl.t
    camy = smooth(t, [(T("tw_narr"), TH - H), (T("tw_narr", 0.7), TH - H), (T("tw_up", 0.95), SPHERE_Y - 330)],
                  r=0.4)
    c = view(tower_bg(), 0, camy)
    # the friends walk to the tower door
    u = tl.prog("tw_narr", t, 0.0, 0.8)
    gy = TOWER_BASE - camy + 4
    if u < 1 and gy < H + 50:
        x = lerp(200, 600, u)
        kitty(c, tl, t, "luna", x, gy, 0.5, 1, "walk", walk=x / 5, mouth=0)
        kitty(c, tl, t, "whiskers", x - 56, gy, 0.5, 1, "walk", walk=x / 5 + 1, mouth=0)
        D.mouse(c, x + 40, gy, 0.5, 1, t, walk=x / 3)
        P.berti(c, x - 120, gy, 0.5, 1, t, walk=x / 6)
    # the lift: a little glowing cabin climbing the shaft
    lu = ease(tl.prog("tw_up", t, 0.0, 0.95))
    if t >= T("tw_narr", 0.8):
        ly = lerp(TOWER_BASE - 60, SPHERE_Y + 90, lu) - camy
        c.rect(640 - 12, ly - 22, 640 + 12, ly, (255, 236, 160), w=2, r=3)
        soft = mix((255, 236, 160), (255, 255, 255), 0.5)
        c.circle(640, ly - 11, 4, soft, ol=None)
    # beacon blink
    if math.sin(t * 3) > 0.2:
        by = TOWER_BASE - TOWER_H - 2 - camy
        if -20 < by < H:
            c.circle(640, by, 7, (255, 80, 70), ol=None)
    return c


def panorama_bg():
    def make():
        c = Canvas(sky_img([(0, (16, 20, 60)), (0.5, (40, 40, 110)), (0.72, (110, 70, 140)), (1, (40, 30, 70))]))
        D.stars(c, 9, 90, W, 260)
        D.moon(c, 1010, 170, 28, sky=(36, 36, 100))
        rng = np.random.default_rng(41)
        P.skyline(c, -20, W + 20, 420, rng, 20, 60, [(46, 40, 80), (54, 46, 90)], win=(255, 220, 150), p=0.35)
        # the river Spree winding through, with lights on the water
        pts = [(0, 470), (200, 450), (420, 470), (640, 440), (860, 455), (1080, 430), (W, 445)]
        c.poly(pts + [(W, 470), (1080, 455), (860, 480), (640, 466), (420, 494), (200, 476), (0, 496)],
               (60, 70, 130), ol=None)
        P.reichstag(c, 300, 430, 0.26, glow=1.0, lw=1.2, flags=False)
        soft_glow(c, 300, 362, 70, (255, 230, 160), 0.6)
        P.brandenburg_gate(c, 520, 432, 0.22, lw=1.2, night=1.0)
        soft_glow(c, 520, 400, 90, (255, 214, 140), 0.45)
        P.berliner_dom(c, 900, 432, 0.3, col=(96, 90, 120), dome=(80, 110, 120), lw=1.2)
        P.oberbaum(c, 1150, 462, 0.16, lw=1.0)
        rng = np.random.default_rng(42)
        P.skyline(c, -20, W + 20, 560, rng, 30, 90, [(40, 34, 70), (48, 40, 80)], win=(255, 220, 150), p=0.45)
        for _ in range(260):
            x, y = rng.uniform(0, W), rng.uniform(440, 560)
            c.circle(x, y, rng.uniform(1, 2.4), [(255, 230, 160), (255, 250, 220), (255, 200, 120)][rng.integers(3)],
                     ol=None)
        return c.img
    return cached("panorama", make)


def sphere_frame():
    """The inside of the TV Tower ball: dark walls with big slanted windows (RGBA, windows transparent)."""
    def make():
        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        c = Canvas(img)
        wall = (44, 46, 70)
        c.rect(0, 0, W, 110, wall, ol=None)
        c.rect(0, 540, W, H, wall, ol=None)
        c.poly([(0, 110), (W, 110), (W, 130), (0, 130)], (60, 64, 92), ol=None)
        # slanted struts between the window panes
        for k in range(7):
            x = -40 + k * 220
            c.poly([(x - 12, 110), (x + 12, 110), (x + 34, 540), (x + 10, 540)], wall, ol=None)
            c.line([(x + 12, 110), (x + 34, 540)], (70, 74, 104), 3, cap=False)
        # the ledge and the floor
        c.rect(-10, 520, W + 10, 560, (90, 90, 120), w=3)
        c.rect(-10, 560, W + 10, H + 10, (70, 60, 90), w=2)
        for y in range(580, H, 30):
            c.line([(0, y), (W, y)], (62, 54, 82), 2, cap=False)
        c.rect(-10, 100, W + 10, 116, (70, 74, 104), w=2)
        return c.img
    return cached("sphere_frame", make)


WALL_LINE = [(0, 500), (150, 470), (320, 452), (430, 440), (520, 430), (600, 450), (760, 470), (900, 452),
             (1060, 476), (W, 470)]


def firework(c, x, y, u, col):
    if u <= 0 or u >= 1:
        return
    r = 70 * ease(u)
    fade = 1 - u
    for k in range(12):
        a = k * math.tau / 12
        px, py = x + math.cos(a) * r, y + math.sin(a) * r + 30 * u * u
        c.circle(px, py, 3.5 * fade + 1, mix(col, (255, 255, 255), 0.3 * fade), ol=None)
        c.line([(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6 + 20 * u * u), (px, py)],
               mix(col, (40, 40, 110), u), 1.5, cap=False)


def tower_in(tl, t):
    T = tl.t
    c = Canvas(panorama_bg().copy())
    # city lights twinkle and brighten when the wall line fades
    bright = ease(tl.prog("tw_one", t, 0.2, 0.9))
    sparkles(c, t, 0, W, 430, 560, n=30, seed=3, col=(255, 240, 190), k=0.8 + 0.6 * bright)
    if bright > 0:
        soft_glow(c, 640, 500, 700, (255, 200, 140), 0.18 * bright)
    # the line where the wall once ran
    wa = ease(tl.prog("tw_wall", t, 0.2, 0.6)) * (1 - ease(tl.prog("tw_one", t, 0.0, 0.5)))
    if wa > 0.02:
        col = mix((60, 60, 110), (236, 236, 244), wa)
        c.line(WALL_LINE, mix((60, 60, 110), (40, 40, 60), wa), 14)
        c.line(WALL_LINE, col, 9)
        for x, y in WALL_LINE[1:-1]:
            c.circle(x, y, 7, col, ol=None)
    if T("tw_one") <= t < T("tw_one", 0.8):
        u = tl.prog("tw_one", t, 0.0, 0.8)
        for k, (x, y) in enumerate(WALL_LINE):
            for j in range(3):
                c.circle(x + 20 * j * u, y - 60 * u * (1 + j * 0.3) - 10 * j, 3 * (1 - u) + 1, (255, 250, 200),
                         ol=None)
    if t >= T("tw_lights"):
        for k, (fx, fy, col, off) in enumerate(((300, 240, (255, 120, 140), 0.0), (760, 200, (140, 220, 255), 0.35),
                                                 (1050, 260, (255, 220, 110), 0.65), (520, 180, (180, 255, 160), 0.9))):
            u = ((t - T("tw_lights")) * 0.6 + off) % 1.3
            firework(c, fx, fy, u, col)
    frame = sphere_frame()
    c.img.paste(frame, (0, 0), frame)
    # the friends at the window
    snug = ease(tl.prog("tw_two", t, 0.0, 0.5))
    bear(c, tl, t, 300, 640, 1.0, 1, look=(1, -1), arm=0.8 if T("tw_wall") <= t < T("tw_one", 1) else 0.0)
    kitty(c, tl, t, "whiskers", 560 + 20 * snug, 650, 1.0, 1, "sit", look=(1, -1),
          eyes="happy" if t >= T("tw_two", 0.6) else "open")
    kitty(c, tl, t, "luna", 720 - 20 * snug, 650, 1.0, -1 if t >= T("tw_two") else 1, "sit", look=(1, -1),
          eyes="happy" if t >= T("tw_two", 0.6) else "open")
    popping = T("tw_pop") <= t < T("tw_pop", 1.0)
    pip(c, tl, t, 860, 520, 0.95, -1, eyes="wide" if popping else "open")
    if popping:
        for side in (-1, 1):
            c.text(860 + side * 30, 440 - 10 * math.sin(t * 10), "pop!", 18, (255, 250, 220), stroke=2)
    if t >= T("tw_two", 0.6):
        hearts_up(c, t, 640, 500, k=0.9, n=3)
    return c


def tower(tl, t):
    T = tl.t
    if t < T("tw_pop"):
        return finish(tower_out(tl, t), tl, t, 0.4)
    return finish(tower_in(tl, t), tl, t, 0.4)


# ======================================================================= home

def home(tl, t):
    T = tl.t
    if t < T("h_sill"):
        c = Canvas(street_bg().copy())
        arrive = tl.prog("h_back", t, 0.0, 0.45)
        vx = lerp(-500, VAN_STOP, 1 - (1 - arrive) ** 2)
        door = ease(tl.prog("h_back", t, 0.5, 0.65))
        dx0, dy0 = vx - 150 * 0.8, STREET_Y - 92 * 0.8
        out = []
        for who, lag, x1 in (("luna", 0.0, 340), ("whiskers", 0.12, 230)):
            u = clamp((tl.prog("h_back", t, 0.68, 1.0) - lag) / 0.7)
            if t >= T("h_narr"):
                u = 1.0
            out.append((who, u, x1))

        def cats_fn(cc):
            for who, u, x1 in out:
                if u >= 1:
                    kitty(cc, tl, t, who, x1, WIN_BOX[3], 0.55, 1 if who == "whiskers" else -1, "sit", mouth=0,
                          eyes="happy")
            if t >= T("h_narr", 0.3):
                pip(cc, tl, t, 288, WIN_BOX[3] - 2, 0.7, 1, hop=abs(math.sin(t * 9)) * 8)
        house_window(c, tl, t, cats_fn)
        P.moving_van(c, vx, STREET_Y, 0.8, door=door, wheel=vx / 26,
                     inside=van_inside_fn([("luna", -200), ("whiskers", -120)] if t < T("h_back", 0.7) else []))
        for who, u, x1 in out:
            if 0 < u < 1:
                x = lerp(dx0, x1, u)
                y = lerp(dy0, WIN_BOX[3], u) + arc_y(u, 120)
                D.cat(c, x, y, PAL[who], lerp(0.45, 0.55, u), -1, "leap", t=t, seed=SEED[who])
        return finish(c, tl, t, 0.4)
    c = Canvas(room_bg().copy())
    sunbeam(c, 1.0)
    # the cushion wall is now a cosy bed for two
    for k, (col, pat) in enumerate(CUSH):
        P.cushion(c, 862 + k * 62, SILL_Y + 2, 64, 26, col, pat)
    lean = ease(tl.prog("h_share", t, 0.6, 0.9)) * (1 - ease(tl.prog("h_munch", t, 0.3, 0.6)))
    munch = t >= T("h_share", 0.9)
    happy = munch or T("h_bed", 0.5) <= t < T("h_pretzel")
    kitty(c, tl, t, "whiskers", 880 + 6 * lean, SILL_Y - 18, 0.72, 1, "sit", eyes="happy" if happy else "open",
          head_dy=10 * lean, look=(1, 0.4))
    kitty(c, tl, t, "luna", 972 - 6 * lean, SILL_Y - 18, 0.72, -1, "sit", eyes="happy" if happy else "open",
          head_dy=10 * lean, look=(1, 0.4))
    if t >= T("h_pretzel", 0.3):
        k = ease(tl.prog("h_pretzel", t, 0.3, 0.6))
        P.pretzel(c, 926, SILL_Y - 84 + 20 * (1 - k), 0.45 * k + 0.01)
        if munch and math.sin(t * 9) > 0:
            for j in range(3):
                c.circle(910 + j * 16, SILL_Y - 50 + (t * 60 + j * 9) % 20, 2.4, P.PRETZEL_L, ol=None)
    pip(c, tl, t, 790, SILL_Y, 0.8, 1, eyes="happy" if t >= T("h_munch") else "open")
    if t >= T("h_munch"):
        hearts_up(c, t, 926, 260, k=0.8, n=3)
    z = 1.6 + ease(tl.prog("h_moral", t, 0.0, 1.0)) * 0.5
    if t >= T("h_end"):
        z = 2.1
    c = zoom(c, 926, 300, z)
    k = ease(tl.prog("h_end", t, 0.25, 0.5))
    if k > 0:
        c.text(W / 2, 630, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return finish(c, tl, t, 0.4)


SCENE_FUNCS = {"title": title, "sill": sill, "van": van, "gate": gate, "imbiss": imbiss, "ubahn": ubahn,
               "gallery": gallery, "tower": tower, "home": home}
CONTINUOUS = set()
EXTRA_CUTS = ["s_van", "v_ride", "u_board", "u_river", "ga_apart", "ga_smile", "tw_pop", "h_sill"]
