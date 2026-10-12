"""Copenhagen -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync with the speech. Static backgrounds are drawn once and cached; Nyhavn
(shared by the harbour and bakery scenes) and the palace-to-mermaid walk are
wide cached layers under a panning camera. The fairy-tale book appears as a
big picture-book page.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.copenhagen import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "saga": 4.0, "bodil": 6.0}

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


def saga(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("saga", t))
    P.cygnet(c, x, y, s, face, t, mouth=mouth, seed=SEED["saga"], **kw)


def bodil(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("bodil", t))
    P.bodil(c, x, y, s, face, t, mouth=mouth, **kw)


def mover(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """Draw a character moving along x keys [(time, x)]; faces its direction of travel."""
    x = smooth(t, keys)
    v = moving(t, keys)
    walking = abs(v) > 15
    if walking:
        face = 1 if v > 0 else -1
    if who == "pip":
        pip(c, tl, t, x, y, s, face, walk=x / (6 * s) if walking else 0.0, **kw)
    elif who == "saga":
        saga(c, tl, t, x, y, s, face, walk=x / (9 * s) if walking else 0.0, **kw)
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


def ripples(c, t, x0, x1, y0, y1, n=24, seed=2, col=(170, 210, 240)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = (rng.uniform(x0, x1) + t * rng.uniform(8, 20)) % (x1 - x0) + x0
        y = rng.uniform(y0, y1)
        ww = rng.uniform(10, 34) * (0.5 + 0.5 * math.sin(t * 2 + k))
        if ww > 4:
            c.line([(x - ww / 2, y), (x + ww / 2, y)], col, 2, cap=False)


def water(c, x0, x1, y0, y1, rng, col=P.WATER, hi=P.WATER_L, n=60):
    c.rect(x0, y0, x1, y1, col, ol=None)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0 + 4, y1 - 2)
        ww = rng.uniform(10, 50) * (0.4 + (y - y0) / max(1, y1 - y0))
        c.line([(x - ww / 2, y), (x + ww / 2, y)], hi, 2, cap=False)


def question(c, x, y, k=1.0):
    if k > 0.05:
        c.text(x, y, "?", 40 * k, (255, 255, 255), stroke=3)


def trunk_ride(c, tl, t, x, y, s, riders, lid=1.0, glow=0.0, pip_point=False, eyes=None):
    """The open trunk with passengers peeking out. riders: list of names (whiskers, luna, pip, saga)."""
    eyes = eyes or {}
    P.trunk(c, x, y, s, lid=lid, glow=glow, part="back", t=t)
    spots = {"luna": (-46, 1), "whiskers": (40, -1)}
    for who in ("luna", "whiskers"):
        if who in riders:
            dx, f = spots[who]
            kitty(c, tl, t, who, x + dx * s, y - 28 * s, 0.72 * s, f, "sit", eyes=eyes.get(who, "open"),
                  look=(1, -0.3))
    P.trunk(c, x, y, s, lid=lid, part="front", t=t)
    if "pip" in riders:
        pip(c, tl, t, x + 70 * s, y - 70 * s, 0.6 * s, 1, eyes="open", proud=pip_point)


# ======================================================================= title

TITLE_COLS = [(240, 80, 80), (250, 160, 60), (250, 210, 70), (110, 200, 110), (80, 170, 230), (180, 120, 220)]


def harbour_houses(c, x0, x1, base, rng, hmin=200, hmax=300, lit=0.0, scale=1.0):
    x = x0
    k = int(rng.integers(10))
    while x < x1:
        w = rng.uniform(96, 140) * scale
        h = rng.uniform(hmin, hmax) * scale
        kind = int(rng.integers(3))
        P.gable_house(c, x, base, w, h, P.HOUSE_COLS[k % len(P.HOUSE_COLS)], kind, lit=lit, rng=rng)
        x += w
        k += 1 + int(rng.integers(2))


def title_bg():
    def make():
        c = Canvas(sky_img([(0, (70, 90, 170)), (0.4, (190, 150, 200)), (0.62, (255, 196, 160)),
                            (1, (255, 214, 170))]))
        D.stars(c, 3, 30, W, 200)
        soft_glow(c, 640, 420, 420, (255, 226, 180), 0.4)
        rng = np.random.default_rng(8)
        P.skyline(c, -20, W + 20, 470, rng, 30, 90, [(170, 140, 180), (180, 150, 186)])
        P.our_saviour_spire(c, 1130, 470, 0.6, col=(90, 76, 100), gold=(230, 190, 120), lw=1.6)
        P.copper_dome(c, 150, 470, 0.6, wall=(200, 180, 190), lw=1.6)
        rng = np.random.default_rng(3)
        harbour_houses(c, -40, W + 40, 520, rng, 150, 220, lit=0.4, scale=0.8)
        water(c, 0, W, 520, H, np.random.default_rng(4), col=(80, 100, 160), hi=(255, 200, 170), n=110)
        P.ship(c, 170, 600, 0.75, 0.0, hull=(60, 50, 50), seed=1)
        P.ship(c, 1110, 610, 0.7, 0.0, hull=(40, 70, 110), face=-1, seed=2)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    ripples(c, t, 0, W, 530, 700, n=30, col=(255, 220, 190))
    sparkles(c, t, 0, W, 0, 260, n=16, seed=3)
    y = 470 + 10 * math.sin(t * 1.6)
    x = 640 + 30 * math.sin(t * 0.5)
    for k in range(3):
        c.line([(x - 140 - k * 30, y - 40 + k * 18), (x - 230 - k * 40, y - 40 + k * 18)], (255, 250, 240), 3)
    trunk_ride(c, tl, t, x, y, 1.15, ("luna", "whiskers", "pip"), lid=1.0, glow=0.5, eyes={"whiskers": "happy"})
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(640, 70 - 30 * (1 - k), "Whiskers and the", 40, mix((90, 100, 170), (255, 250, 236), k), stroke=3 * k)
    word = "FLYING TRUNK"
    n = len(word)
    for i, ch in enumerate(word):
        kk = ease(tl.prog("t_open", t, 0.25 + 0.5 * i / n, 0.4 + 0.5 * i / n))
        if kk <= 0 or ch == " ":
            continue
        xx = 640 + (i - (n - 1) / 2) * 54
        yy = 150 + 6 * math.sin(t * 3 + i) + 30 * (1 - kk)
        c.text(xx, yy, ch, 70 * (0.5 + 0.5 * kk), TITLE_COLS[i % len(TITLE_COLS)], stroke=5)
    return c


# ======================================================================= rain (home)

TRUNK_HOME = (930, 600)
WIN = (760, 110, 1080, 370)
SILL_Y = 372


def room_rain_bg():
    def make():
        c = Canvas(MF.room(False).copy())
        x0, y0, x1, y1 = WIN
        win = D.gradient((x1 - x0) * SS, (y1 - y0) * SS, [(0, (110, 118, 140)), (1, (160, 166, 180))])
        c.img.paste(win, (x0 * SS, y0 * SS))
        D.cloud(c, 850, 170, 0.9, (140, 146, 164))
        D.cloud(c, 1000, 150, 1.0, (130, 136, 156))
        c.rect(756, 106, 1084, 374, None, w=8)
        c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
        c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
        c.rect(740, 370, 1100, 392, (255, 250, 240), r=4)
        img = Image.blend(c.img, Image.new("RGB", c.img.size, (70, 80, 120)), 0.28)
        c = Canvas(img)
        # a little lamp glowing on a stool
        c.rect(250, 470, 330, 520, (150, 100, 70), w=2.5, r=4)
        c.line([(290, 470), (290, 390)], OUT, 4)
        c.poly([(258, 392), (322, 392), (306, 350), (274, 350)], (250, 210, 140), w=2.5)
        soft_glow(c, 290, 380, 180, (255, 220, 150), 0.35)
        return c.img
    return cached("room_rain", make)


def room_window_open(c, t, k):
    """The window swinging open (k 0..1): two casements fold out to the sides."""
    x0, y0, x1, y1 = WIN
    c.rect(x0, y0, x1, y1, (100, 108, 132), ol=None)
    D.cloud(c, 860, 180, 0.8, (130, 136, 156))
    c.rect(756, 106, 1084, 374, None, w=8)
    for side in (-1, 1):
        hinge = x0 if side < 0 else x1
        w = 160 * (1 - 0.8 * ease(k))
        xa = hinge
        xb = hinge - side * w
        c.poly([(xa, y0), (xb, y0 + 20 * k), (xb, y1 - 20 * k), (xa, y1)], (190, 200, 220), ol=(240, 240, 240), w=5)


def rain_streaks(c, t, k=1.0):
    x0, y0, x1, y1 = WIN
    rng = np.random.default_rng(5)
    for j in range(26):
        x = rng.uniform(x0 + 6, x1 - 6)
        sp = rng.uniform(300, 420)
        y = y0 + ((t * sp + rng.uniform(0, 400)) % (y1 - y0))
        c.line([(x, y), (x - 3, min(y1 - 4, y + 18))], (220, 228, 245), 1.5, cap=False)
    for j in range(10):
        x = rng.uniform(x0 + 10, x1 - 10)
        y = y0 + ((t * 20 + rng.uniform(0, 300)) % (y1 - y0 - 10))
        c.circle(x, y, 2.5, (210, 220, 240), ol=None)


def rain(tl, t):
    T = tl.t
    c = Canvas(room_rain_bg().copy())
    opening = ease(tl.prog("r_go", t, 0.3, 0.5)) if t >= T("r_go") else 0.0
    if opening > 0:
        room_window_open(c, t, opening)
    rain_streaks(c, t)
    # ---- the trunk: sits, glows, floats, lid opens, flies out of the window
    tx, ty = TRUNK_HOME
    glow = 0.0
    lid = 0.0
    ts = 0.9
    if t >= T("r_click"):
        glow = ease(tl.prog("r_click", t, 0.0, 0.3))
        rise = ease(tl.prog("r_click", t, 0.3, 0.9))
        shake = math.sin(t * 40) * 3 * (1 - rise) * (t < T("r_click", 0.9))
        tx += shake
        ty -= 80 * rise
        ty += 6 * math.sin(t * 2.2) * rise
    if t >= T("r_go"):
        lid = ease(tl.prog("r_go", t, 0.0, 0.1))
        out = ease(tl.prog("r_go", t, 0.5, 0.95))
        tx = lerp(tx, 920, out)
        ty = lerp(ty, 290, out)
        ts = lerp(0.9, 0.12, out)
    riders = []
    if t >= T("r_go", 0.05):
        riders.append("whiskers")
    if t >= T("r_go", 0.2):
        riders.append("luna")
    if t >= T("r_go", 0.32):
        riders.append("pip")
    # ---- Luna
    if t < T("r_pip", 0.3):
        kitty(c, tl, t, "luna", 830, SILL_Y, 0.75, 1, "sit", look=(1, -0.5), tail=math.sin(t * 1.2))
    elif t < T("r_pip", 0.6):
        u = tl.prog("r_pip", t, 0.3, 0.6)
        D.cat(c, lerp(830, 640, u), lerp(SILL_Y, 650, u) + arc_y(u, 60), D.LUNA, lerp(0.75, 0.85, u), -1, "leap",
              t=t, seed=1.3)
    elif "luna" not in riders and t < T("r_go", 0.1):
        face = -1 if t < T("r_pah") else 1
        reading = T("r_read") <= t < T("r_read", 1.0)
        kitty(c, tl, t, "luna", 640, 650, 0.85, face, "sit", look=(1, 0.5) if reading else (1, -0.3))
    elif "luna" not in riders:
        u = tl.prog("r_go", t, 0.1, 0.2)
        D.cat(c, lerp(640, tx - 40, u), lerp(650, ty - 20, u) + arc_y(u, 120), D.LUNA, 0.8, 1, "leap",
              t=t, seed=1.3)
    # ---- Pip with the book
    bx = smooth(t, [(T("r_pip"), -120), (T("r_pip", 0.7), 330)], r=0.1)
    if t < T("r_pip"):
        pass
    elif "pip" not in riders and t < T("r_go", 0.18):
        book_y = 634 if t >= T("r_pip", 0.7) else 636 + 2 * math.sin(t * 20)
        if t < T("r_pip", 0.75):
            P.book_cover(c, bx - 60, book_y, 0.9)
            pip(c, tl, t, bx, 640, 0.9, 1, walk=bx / 6 if t < T("r_pip", 0.7) else 0)
        else:
            P.book_cover(c, 290, 636, 0.9)
            pip(c, tl, t, 380, 640, 0.9, -1 if t < T("r_pah") else 1, eyes="open")
    elif "pip" not in riders:
        P.book_cover(c, 290, 636, 0.9)
        u = tl.prog("r_go", t, 0.18, 0.32)
        pip(c, tl, t, lerp(380, tx + 60, u), lerp(640, ty - 60, u) + arc_y(u, 160), 0.8, 1, hop=0)
    if t >= T("r_go", 0.18):
        P.book_cover(c, 290, 636, 0.9)
    # ---- Whiskers
    if "whiskers" not in riders:
        if t < T("r_pah", 0.1):
            kitty(c, tl, t, "whiskers", 470, 650, 0.9, 1, "sit", look=(-0.5, 0.6) if t < T("r_pip") else (-1, 0),
                  tail=math.sin(t * 0.8) * 0.3)
        elif t < T("r_pah", 0.6):
            mover(c, tl, t, "whiskers", [(T("r_pah", 0.1), 470), (T("r_pah", 0.55), 800)], 650, 0.9)
        elif t < T("r_pah", 0.78):
            u = tl.prog("r_pah", t, 0.6, 0.78)
            D.cat(c, lerp(800, 920, u), lerp(650, ty - 100, u) + arc_y(u, 90), D.WHISKERS, 0.85, 1, "leap",
                  t=t, seed=0.0)
        else:
            pass   # drawn sitting on the trunk below
    # draw trunk and anyone sitting on top
    if not riders:
        P.trunk(c, tx, ty, ts, glow=glow, t=t)
        if t >= T("r_pah", 0.78):
            eyes = "wide" if t >= T("r_click", 0.3) else "open"
            kitty(c, tl, t, "whiskers", tx - 10, ty - 98 * ts, 0.8, 1 if t < T("r_fly") else -1, "sit",
                  eyes=eyes, look=(0, 1) if t >= T("r_click", 0.3) else (1, 0))
    else:
        trunk_ride(c, tl, t, tx, ty, ts, riders, lid=lid, glow=glow,
                   eyes={"whiskers": "wide", "luna": "happy"})
    # ---- the picture book page while Luna reads
    if T("r_read") - 0.3 <= t < T("r_read", 1.0) + 0.3:
        k = ease(clamp((t - T("r_read") + 0.3) / 0.5)) * ease(clamp((T("r_read", 1.0) + 0.3 - t) / 0.5))
        c = blend_over(c, (30, 30, 50), 0.45 * k)
        c.push(640, 320 + 400 * (1 - k))
        P.book_open(c, 0, 0, page="trunk", t=t)
        c.pop()
    z = 1 + 0.25 * ease(tl.prog("r_click", t, 0.2, 0.8)) * (1 - ease(tl.prog("r_go", t, 0.4, 0.8)))
    c = zoom(c, 900, 420, z)
    return finish(c, tl, t)


# ======================================================================= flight

def flight_bg(dawn):
    def make():
        if dawn:
            c = Canvas(sky_img([(0, (110, 120, 200)), (0.45, (240, 170, 180)), (0.7, (255, 210, 160)),
                                (1, (250, 230, 190))]))
            soft_glow(c, 1050, 520, 360, (255, 236, 180), 0.6)
            for x, y, s in ((200, 160, 1.0), (560, 110, 0.7), (900, 210, 0.8)):
                D.cloud(c, x, y, s, (255, 222, 214))
            # Copenhagen on the horizon
            rng = np.random.default_rng(11)
            P.skyline(c, 640, W + 20, 560, rng, 18, 50, [(150, 120, 160), (170, 136, 170)])
            P.our_saviour_spire(c, 880, 560, 0.42, col=(90, 70, 100), gold=(250, 200, 120), lw=1.4)
            P.copper_dome(c, 1010, 560, 0.42, wall=(190, 160, 180), lw=1.4)
            P.town_tower(c, 1150, 560, 0.4, col=(170, 100, 110), lw=1.4)
            P.dragon_spire(c, 760, 560, 0.4, lw=1.2)
            water(c, 0, W, 560, H, np.random.default_rng(12), col=(120, 120, 180), hi=(255, 210, 190), n=120)
        else:
            c = Canvas(sky_img([(0, (16, 20, 56)), (0.6, (40, 50, 110)), (1, (60, 70, 130))]))
            D.stars(c, 21, 120, W, 520)
            D.moon(c, 1060, 130, 40, sky=(30, 36, 80))
            water(c, 0, W, 560, H, np.random.default_rng(12), col=(30, 40, 90), hi=(110, 130, 190), n=120)
            for x, y, s in ((150, 470, 1.4), (520, 500, 1.2), (900, 480, 1.5), (1220, 510, 1.1)):
                D.cloud(c, x, y, s, (70, 80, 130))
        return c.img
    return cached(("flight", dawn), make)


def flight(tl, t):
    T = tl.t
    k = ease(tl.prog("f_dawn", t, 0.0, 0.9))
    if k <= 0:
        c = Canvas(flight_bg(False).copy())
    elif k >= 1:
        c = Canvas(flight_bg(True).copy())
    else:
        c = Canvas(Image.blend(flight_bg(False), flight_bg(True), k))
    # drifting clouds for speed
    for j in range(5):
        cx = (1500 - (t * (60 + j * 25) + j * 330) % 1700)
        cy = 200 + j * 70
        D.cloud(c, cx, cy, 0.6 + 0.1 * j, mix((90, 100, 150), (255, 236, 230), k))
    # trunk path
    s0 = T("f_narr")
    x = smooth(t, [(s0, -200), (T("f_fly", 0.8), 560), (T("f_land"), 640), (T("f_land", 1.0), 1150)], r=0.3)
    y = smooth(t, [(s0, 330), (T("f_fly"), 300), (T("f_land"), 330), (T("f_land", 1.0), 600)], r=0.3)
    s = smooth(t, [(s0, 1.0), (T("f_land"), 1.0), (T("f_land", 1.0), 0.35)], r=0.3)
    y += 10 * math.sin(t * 2.0)
    for j in range(4):
        c.line([(x - 130 * s - j * 26, y - 70 * s + j * 20 * s), (x - 260 * s - j * 30, y - 70 * s + j * 20 * s)],
               mix((170, 180, 230), (255, 255, 255), k), 3)
    scared = T("f_fly", 0.3) <= t < T("f_dawn", 0.2)
    trunk_ride(c, tl, t, x, y, s, ("luna", "whiskers", "pip"), lid=1.0, glow=0.25 * (1 - k),
               pip_point=T("f_look") <= t < T("f_land"),
               eyes={"whiskers": "wide" if scared else "open", "luna": "happy" if k > 0.5 else "open"})
    if scared:
        # Whiskers' fur all puffed up
        hx, hy = x + 40 * s - 13 * s, y - 12 * s - 76 * s
        for j in range(9):
            a = -math.pi * (0.1 + 0.8 * j / 8)
            c.line([(hx + math.cos(a) * 26 * s, hy + math.sin(a) * 24 * s),
                    (hx + math.cos(a) * 36 * s, hy + math.sin(a) * 34 * s)], D.WHISKERS["body"], 4)
    if k > 0.3:
        c.push(0, 0)
        for j in range(3):
            gx = (300 + j * 200 + t * 40) % 1400 - 60
            gy = 220 + 40 * j + 6 * math.sin(t * 3 + j)
            fl = math.sin(t * 8 + j) * 6
            c.line([(gx - 12, gy + fl), (gx, gy), (gx + 12, gy + fl)], (250, 250, 250), 3)
        c.pop()
    return finish(c, tl, t)


# ======================================================================= nyhavn + bakery

NY_W = 2300
QUAY = 560          # quay edge (top of the stone wall)
FEET = 670          # where everyone stands
TRUNK_NY = 700      # world x where the trunk lands
COUNTER_X = 1620
DUCK_HOME = [(1330, 1), (1410, -1)]


def nyhavn_bg():
    def make():
        c = Canvas(size=(NY_W, H))
        c.img.paste(sky_img([(0, (110, 180, 240)), (0.5, (190, 225, 250)), (1, (220, 240, 250))], NY_W, H), (0, 0))
        for x, y, s in ((200, 80, 0.8), (800, 60, 0.6), (1400, 100, 0.9), (2000, 70, 0.7)):
            D.cloud(c, x, y, s)
        P.our_saviour_spire(c, 1740, 330, 0.7, lw=2)
        P.copper_dome(c, 520, 330, 0.75)
        rng = np.random.default_rng(31)
        harbour_houses(c, -30, NY_W + 30, 450, rng, 220, 300)
        # canal
        water(c, 0, NY_W, 450, QUAY, np.random.default_rng(32), n=140)
        # far quay strip under the houses
        c.rect(-10, 444, NY_W + 10, 456, (170, 160, 150), w=2)
        # moored ships (their hulls sit in the canal)
        P.ship(c, 260, 540, 0.85, 0.0, hull=(40, 60, 90), seed=1)
        P.ship(c, 1040, 538, 0.8, 0.0, hull=(130, 50, 40), stripe=(250, 230, 160), face=-1, seed=2)
        P.ship(c, 2150, 540, 0.85, 0.0, hull=(40, 90, 70), seed=3)
        P.bakery_boat(c, COUNTER_X + 20, 548, 0.8)
        # quay wall and cobbles
        c.rect(-10, QUAY, NY_W + 10, H + 10, P.COBBLE, w=3)
        rng = np.random.default_rng(33)
        for row, y in enumerate(range(QUAY + 14, H, 22)):
            off = (row % 2) * 20
            for x in range(-20 + off, NY_W + 20, 40):
                c.ellipse(x + rng.uniform(-3, 3), y, 17, 8, mix(P.COBBLE, P.COBBLE_D, rng.uniform(0, 0.7)), ol=None)
        c.rect(-10, QUAY - 4, NY_W + 10, QUAY + 10, (210, 200, 186), w=2.5)
        for bx in (120, 520, 900, 1300, 1900, 2250):
            c.rect(bx - 12, QUAY - 26, bx + 12, QUAY + 4, (60, 60, 70), w=2, r=6)
            c.rect(bx - 15, QUAY - 30, bx + 15, QUAY - 22, (60, 60, 70), w=2, r=3)
        # flower pots and café tables near the houses' side
        for fx in (420, 1180, 2050):
            c.rect(fx - 18, 600, fx + 18, 630, (190, 100, 70), w=2)
            for dx in (-10, 0, 10):
                D.flower(c, fx + dx, 604, [(240, 80, 100), (250, 210, 70), (240, 140, 200)][(dx // 10 + 1) % 3], 0.6)
        return c.img
    return cached("nyhavn", make)


def stall(c, x, t, items):
    """The bakery counter (drawn in front of Bodil) with pastries on top. x = screen x of the counter centre."""
    P.counter(c, x, QUAY + 2, 0.8)
    for k, kind in enumerate(items):
        if kind is None:
            continue
        P.pastry(c, x - 120 + k * 60, QUAY - 4, 0.9, kind)


def nyhavn_cam(tl, t):
    T = tl.t
    return smooth(t, [(T("n_bump"), 0), (T("n_narr", 0.1), 0), (T("n_ducks", 0.2), 520), (T("n_go"), 520),
                      (T("n_go", 0.9), 640)], r=0.4)


def nyhavn(tl, t):
    T = tl.t
    camx = nyhavn_cam(tl, t)
    c = view(nyhavn_bg(), camx)
    c.push(-camx, 0)
    ripples(c, t, camx, camx + W, 466, 548, n=26, col=(170, 210, 240))
    bodil(c, tl, t, COUNTER_X + 20, QUAY + 40, 0.85, -1, mouth=0)
    stall(c, COUNTER_X, t, [0, 1, 2, 0, 1])
    # ---- the trunk drops in
    u = tl.prog("n_bump", t, 0.0, 0.35)
    ty = lerp(-150, FEET, u * u)
    sq = 1.0
    if t >= T("n_bump", 0.35):
        ty = FEET
    landed = t >= T("n_bump", 0.35)
    if not landed:
        trunk_ride(c, tl, t, TRUNK_NY, ty, 0.8, ("luna", "whiskers", "pip"), eyes={"whiskers": "wide"})
    else:
        P.trunk(c, TRUNK_NY, FEET, 0.8, lid=0.0 if t > T("n_bump", 0.75) else 1.0)
    # ---- ducks (laughing at Saga, then waddling off towards the trunk)
    for j, (dx, f) in enumerate(DUCK_HOME):
        if t < T("n_tease", 0.2):
            laugh = 1.0 if t >= T("n_ducks", 0.2) else 0.3
            P.duck(c, dx, FEET + 4, 0.9, f if t < T("n_ducks", 0.15) else -1, t, laugh=laugh, seed=j)
        else:
            keys = [(T("n_tease", 0.2), dx), (T("n_go", 1.0), dx - 1200)]
            x = smooth(t, keys)
            P.duck(c, x, FEET + 4 + j * 6, 0.9, -1, t, laugh=0.4, walk=x / 5, seed=j)
    # ---- Saga
    if t < T("n_ugly"):
        saga(c, tl, t, 1250, FEET, 0.9, -1, sad=True, eyes="closed" if t > T("n_ducks", 0.5) else "open",
              look=(0, 1))
    else:
        happy = t >= T("n_saga", 0.3)
        saga(c, tl, t, 1250, FEET, 0.9, -1, sad=not happy, eyes="happy" if T("n_saga", 0.3) <= t < T("n_saga", 1)
              else "open", wing=0.6 if T("n_hungry") <= t < T("n_hungry", 0.6) else 0.0)
    # ---- cats and Pip
    if landed:
        b = T("n_bump", 0.4)
        if t < T("n_bump", 0.75):
            u = tl.prog("n_bump", t, 0.4, 0.75)
            D.cat(c, lerp(TRUNK_NY - 20, 600, u), lerp(FEET - 70, FEET, u) + arc_y(u, 80), D.LUNA, 0.85, -1, "leap",
                  t=t, seed=1.3)
            D.cat(c, lerp(TRUNK_NY + 20, 820, u), lerp(FEET - 70, FEET, u) + arc_y(u, 60), D.WHISKERS, 0.85, 1,
                  "leap", t=t, seed=0.0)
            pip(c, tl, t, lerp(TRUNK_NY + 50, 760, u), lerp(FEET - 70, FEET, u) + arc_y(u, 120), 0.75, 1)
        else:
            lkeys = [(T("n_narr", 0.5), 600), (T("n_ducks", 0.6), 1000), (T("n_grey"), 1000), (T("n_grey", 0.4), 1110),
                     (T("n_go", 0.1), 1110), (T("n_go", 1.0), 1080)]
            wkeys = [(T("n_narr", 0.6), 820), (T("n_ducks", 0.7), 860), (T("n_pastry"), 860), (T("n_go", 0.05), 860),
                     (T("n_go", 0.8), 1400)]
            pkeys = [(T("n_narr", 0.55), 760), (T("n_ducks", 0.65), 950), (T("n_go", 0.2), 950),
                     (T("n_go", 1.0), 1170)]
            look_up = t < T("n_ducks")
            mover(c, tl, t, "whiskers", wkeys, FEET, 0.85, 1, look=(1, -1) if look_up else (1, 0),
                  eyes="wide" if T("n_pastry") <= t < T("n_go") else "open")
            mover(c, tl, t, "luna", lkeys, FEET, 0.85, 1, look=(1, -1) if look_up else (1, 0))
            mover(c, tl, t, "pip", pkeys, FEET, 0.8, 1)
    c.pop()
    return finish(c, tl, t)


def snail_wrap(c, x, y, s, k, t):
    """Whiskers wrapped in a long cinnamon ribbon: k 0..1 how much is wrapped."""
    if k <= 0:
        return
    n = int(1 + 5 * k)
    for j in range(n):
        yy = y - 14 * s - j * 18 * s
        c.ellipse(x - 2 * s, yy, 62 * s, 12 * s, (214, 150, 80), w=2.5)
        c.arc(x - 2 * s, yy - 2 * s, 50 * s, 7 * s, 200, 340, (150, 90, 40), 2)
        c.line([(x - 40 * s, yy - 4 * s), (x + 30 * s, yy - 6 * s)], (255, 250, 240), 1.5)


def bakery(tl, t):
    T = tl.t
    camx = 640
    c = view(nyhavn_bg(), camx)
    c.push(-camx, 0)
    ripples(c, t, camx, camx + W, 466, 548, n=26, col=(170, 210, 240))
    # ---- Bodil behind the counter
    arm = 0.0
    if T("b_hello") <= t < T("b_hello", 1):
        arm = 0.6 + 0.4 * math.sin(t * 8)
    if T("b_hello", 0.5) <= t < T("b_hello", 1):
        arm = 0.5
    beyes = "happy" if T("b_nolid") <= t < T("b_nolid", 1) or T("b_roll") <= t < T("b_purpose", 1) else "open"
    bodil(c, tl, t, COUNTER_X + 20, QUAY + 40, 0.85, -1, arm=arm, eyes=beyes)
    snail_left = 1.0 - ease(tl.prog("b_snail", t, 0.05, 0.4))
    stall(c, COUNTER_X, t, [0, 1, None, 0, 1])
    # giant cinnamon snail and the open sandwich
    P.cinnamon_snail(c, COUNTER_X - 30, QUAY - 14, 46, unroll=1 - snail_left)
    lid_lift = 0.0
    if T("b_lid") <= t < T("b_stole", 1.0):
        lid_lift = 18 * ease(tl.prog("b_lid", t, 0.2, 0.5)) * (1 - ease(tl.prog("b_lid", t, 0.75, 0.95)))
    if t >= T("b_hello", 0.6) and t < T("b_snail"):
        P.smorrebrod(c, COUNTER_X - 150, QUAY - 2, 0.9, lift=lid_lift)
    # ---- the trunk at the far left, the ducks peck its lock
    tx, ty, glow = TRUNK_NY, FEET, 0.0
    ducks_on = t < T("b_away", 0.6)
    if t >= T("b_peck", 0.5):
        glow = ease(tl.prog("b_peck", t, 0.5, 0.8))
    if t >= T("b_peck", 0.7):
        u = ease(tl.prog("b_peck", t, 0.7, 1.0))
        ty -= 40 * u + 4 * math.sin(t * 30) * (1 - u)
    if t >= T("b_oh"):
        u = tl.prog("b_oh", t, 0.0, 1.0)
        u2 = tl.prog("b_away", t, 0.0, 0.8)
        tx = lerp(TRUNK_NY, TRUNK_NY + 120, u) + 300 * ease(u2)
        ty = lerp(FEET - 40, FEET - 260, ease(u)) - 400 * ease(u2)
    if tx < camx + W + 200 and ty > -200:
        P.trunk(c, tx, ty, 0.62, glow=glow, t=t)
    for j in range(2):
        if t < T("b_oh"):
            dx = TRUNK_NY - 35 + j * 110
            peck = abs(math.sin(t * 9 + j)) * (T("b_peck") <= t < T("b_peck", 0.5))
            P.duck(c, dx, FEET + 4, 0.8, 1 - 2 * j, t + peck * 0.1, laugh=0.2 + 0.8 * peck, seed=j)
        elif j == 0 and ducks_on:
            # one duck clings to the trunk, then drops into the canal
            u = tl.prog("b_away", t, 0.0, 0.45)
            if u < 0.01:
                P.duck(c, tx - 40, ty - 50, 0.7, 1, t, laugh=1.0, seed=j)
            else:
                fx = lerp(tx - 40, TRUNK_NY + 200, u)
                fy = lerp(ty - 50, QUAY - 10, u * u)
                if u < 1:
                    P.duck(c, fx, fy, 0.7, 1, t, laugh=1.0, seed=j, fall=u)
        elif j == 1:
            P.duck(c, TRUNK_NY + 80, FEET + 4, 0.8, -1, t, laugh=0.0, seed=j)
    if T("b_away", 0.45) <= t < T("b_away", 1.0) + 0.5:
        u = (t - T("b_away", 0.45)) / 1.0
        for j in range(8):
            a = math.pi * (0.1 + 0.8 * j / 7)
            r = 60 * u
            c.circle(TRUNK_NY + 200 + math.cos(a) * r, QUAY - 20 - math.sin(a) * r * 1.2 + 80 * u * u, 4 * (1 - u) + 1,
                     (200, 230, 255), ol=None)
    # ---- Luna, Pip, Saga, Whiskers on the quay
    alarm = t >= T("b_oh")
    saga(c, tl, t, 1250, FEET, 0.9, -1 if alarm else 1, eyes="wide" if alarm and t < T("b_follow") else "open",
          wing=0.5 if T("b_follow") <= t < T("b_follow", 0.7) else 0.0)
    lx = smooth(t, [(T("b_oh"), 1080), (T("b_oh", 0.4), 1040)], r=0.1)
    kitty(c, tl, t, "luna", lx, FEET, 0.85, -1 if alarm else 1, "stand",
          eyes="wide" if alarm else "open", look=(1, -0.6) if alarm else (1, -0.4))
    laughing = T("b_roll") <= t < T("b_roll", 1)
    pip(c, tl, t, 1170, FEET + 6, 0.8, -1 if alarm else 1, eyes="happy" if laughing else "open",
        hop=abs(math.sin(t * 9)) * 10 if laughing else None)
    # Whiskers: at the counter, the sandwich puzzle, the cinnamon whirl
    wx = 1440
    if t < T("b_snail", 0.1):
        tilt = T("b_lid", 0.4) <= t < T("b_stole", 1)
        kitty(c, tl, t, "whiskers", wx, FEET, 0.85, 1, "stand",
              eyes="wide" if t < T("b_hello") else "open", look=(1, -1) if not tilt else (0, 1),
              head_dy=8 if tilt else 0)
        if T("b_lid", 0.4) <= t < T("b_stole", 0.5):
            question(c, wx + 60, FEET - 170, ease(tl.prog("b_lid", t, 0.4, 0.6)))
    else:
        pull = ease(tl.prog("b_snail", t, 0.1, 0.4))
        spin = tl.prog("b_snail", t, 0.4, 0.8)
        x = lerp(wx, 1370, pull) + (lerp(0, -30, spin))
        wrapped = ease(spin)
        if spin <= 0:
            # walking backwards, pulling the ribbon
            kitty(c, tl, t, "whiskers", x, FEET, 0.85, 1, "walk", walk=-x / 10, eyes="happy")
            sx, sy = COUNTER_X - 30, QUAY - 14
            pts = [(lerp(sx - 20, x + 60, u), lerp(sy, FEET - 70, u) + 26 * math.sin(u * math.pi) - 10 * u)
                   for u in np.linspace(0, 1, 12)]
            c.stroke(pts, (214, 150, 80), 9)
        elif spin < 1:
            face = 1 if int(t * 10) % 2 == 0 else -1
            kitty(c, tl, t, "whiskers", x, FEET, 0.85, face, "stand", eyes="wide")
            snail_wrap(c, x, FEET - 12, 0.85, wrapped, t)
            pts = [(lerp(COUNTER_X - 30, x, u), lerp(QUAY - 14, FEET - 60, u) + 20 * math.sin(u * math.pi))
                   for u in np.linspace(0, 1, 10)]
            c.stroke(pts, (214, 150, 80), 9 * (1 - spin))
        else:
            hop = -abs(math.sin((t - T("b_snail", 0.8)) * 6)) * 14 * (t < T("b_snail", 1.0))
            kitty(c, tl, t, "whiskers", x, FEET + hop, 0.85, -1 if alarm else 1, "stand",
                  eyes="happy" if T("b_purpose") <= t < T("b_purpose", 1) else ("wide" if alarm else "open"),
                  look=(1, -0.5))
            snail_wrap(c, x, FEET - 12 + hop, 0.85, 1.0, t)
    c.pop()
    z = 1.0
    if T("b_lid") <= t < T("b_snail"):
        z = 1 + 0.35 * ease(tl.prog("b_lid", t, 0.0, 0.4)) * (1 - ease(tl.prog("b_nolid", t, 0.6, 1.0)))
    c = zoom(c, 1440 - camx + 100, 520, z)
    return finish(c, tl, t)


# ======================================================================= palace + mermaid

PA_W = 2500
PA_FEET = 660


def palace_bg():
    def make():
        c = Canvas(size=(PA_W, H))
        c.img.paste(sky_img([(0, (120, 180, 236)), (0.6, (200, 226, 246)), (1, (226, 240, 250))], PA_W, H), (0, 0))
        for x, y, s in ((300, 90, 0.8), (1100, 70, 0.6), (1700, 110, 0.9), (2300, 80, 0.7)):
            D.cloud(c, x, y, s)
        # the palace square
        P.copper_dome(c, 1330, 560, 0.85)          # the Marble Church dome rises behind the square
        P.amalienborg(c, 520, 560, 0.95)
        P.amalienborg(c, -300, 560, 0.9)
        c.rect(-10, 556, 1500, H + 10, (220, 206, 186), w=2.5)
        rng = np.random.default_rng(41)
        for row, y in enumerate(range(574, H, 26)):
            for x in range(-20 + (row % 2) * 30, 1500, 60):
                c.ellipse(x, y, 26, 9, mix((220, 206, 186), (190, 176, 160), rng.uniform(0.2, 0.8)), ol=None)
        P.horse_statue(c, 1060, 600, 0.9)
        P.sentry_box(c, 120, 600, 0.95)
        P.sentry_box(c, 880, 600, 0.95)
        # the waterfront: harbour, far shore, trees and the Little Mermaid
        rng = np.random.default_rng(42)
        P.skyline(c, 1480, PA_W + 20, 420, rng, 20, 60, [(170, 176, 196), (160, 170, 190)])
        water(c, 1480, PA_W, 420, 600, np.random.default_rng(43), n=90)
        for x in (1500, 1620, 2440):
            D.tree(c, x, 600, 0.8, leaf=(96, 160, 90))
        c.rect(1480, 596, PA_W + 10, H + 10, (196, 186, 170), w=2.5)
        c.rect(1480, 590, PA_W + 10, 604, (220, 212, 198), w=2.5)
        for x in range(1500, PA_W, 90):
            c.line([(x, 612), (x, H)], (176, 166, 150), 2, cap=False)
        D.bush(c, 1470, 600, 0.9)
        P.mermaid(c, 2120, 540, 0.9)
        return c.img
    return cached("palace", make)


def guard_hat_path(tl, t):
    """Where the snatched bearskin is: (x, y, on_whiskers) or None while on the guard."""
    T = tl.t
    if t < T("p_swoop", 0.4):
        return None
    if t < T("p_swoop", 0.62):
        u = tl.prog("p_swoop", t, 0.4, 0.62)
        tx, ty = trunk_swoop(tl, t)
        if u < 0.55:
            return tx, ty + 10, False
        k = (u - 0.55) / 0.45
        return lerp(tx, 650, k), lerp(ty + 10, 520, k * k), False
    if t < T("p_back", 0.2):
        return "whiskers"
    if t < T("p_back", 0.75):
        u = ease(tl.prog("p_back", t, 0.2, 0.75))
        return lerp(650, 762, u), lerp(530, 520, u) + arc_y(u, 60), False
    return None


def trunk_swoop(tl, t):
    u = tl.prog("p_swoop", t, 0.1, 0.8)
    x = lerp(-250, 1600, u)
    y = 430 - 260 * (2 * u - 1) ** 2 + 60 * (u > 0.5) * (u - 0.5)
    y = lerp(-150, y, min(1, u * 5))
    return x, y


def palace(tl, t):
    T = tl.t
    camx = smooth(t, [(T("p_back", 0.6), 0), (T("p_fit", 0.0), 1220)], r=0.4)
    c = view(palace_bg(), camx)
    c.push(-camx, 0)
    if camx + W > 1500:
        ripples(c, t, max(1480, camx), camx + W, 430, 590, n=20, col=(170, 210, 240))
    # ---- guards
    hat = guard_hat_path(tl, t)
    lost = hat is not None
    ears = ease(tl.prog("p_swoop", t, 0.42, 0.55)) if lost else 0.0
    P.rabbit_guard(c, 200, 640, 0.95, 1, t, march=0.0)
    gx = 762
    P.rabbit_guard(c, gx, 640, 0.95, -1, t, hat=not lost, ears=ears, look=-1 if lost else 0,
                   eyes="wide" if lost else "open")
    # ---- the trunk swooping overhead
    if T("p_swoop", 0.1) <= t < T("p_swoop", 0.8):
        tx, ty = trunk_swoop(tl, t)
        P.trunk(c, tx, ty, 0.6, glow=0.4, t=t)
        P.duck(c, tx + 20, ty - 60, 0.6, 1, t, laugh=1.0, seed=3)
    if isinstance(hat, tuple):
        P.bearskin(c, hat[0], hat[1], 0.95)
    # ---- the gang
    run_in = T("p_narr")
    to_mer0, to_mer1 = T("p_mer", 0.0), T("p_fit", 0.0)
    lkeys = [(run_in, -150), (T("p_narr", 0.7), 470), (to_mer0, 470), (to_mer1, 1680), (T("p_run", 0.2), 1680),
             (T("p_run", 1.0), 2700)]
    wkeys = [(run_in, -250), (T("p_narr", 0.8), 600), (to_mer0, 600), (to_mer1, 1540), (T("p_run", 0.3), 1540),
             (T("p_run", 1.0), 2600)]
    pkeys = [(run_in, -90), (T("p_narr", 0.7), 540), (to_mer0, 540), (to_mer1, 1610), (T("p_run", 0.1), 1610),
             (T("p_run", 1.0), 2700)]
    dkeys = [(run_in, -50), (T("p_narr", 0.6), 380), (to_mer0, 380), (to_mer1, 1840), (T("p_run", 0.2), 1840),
             (T("p_run", 1.0), 2800)]
    sitting = T("p_fit") <= t < T("p_there")
    looking_up = T("p_swoop", 0.1) <= t < T("p_swoop", 0.6)
    mover(c, tl, t, "saga", dkeys, PA_FEET, 0.85, 1, sad=T("p_fit") <= t < T("p_fit", 1),
          look=(0, -1) if looking_up else (0, 0))
    mover(c, tl, t, "luna", lkeys, PA_FEET, 0.82, 1, pose="sit" if sitting else "stand",
          look=(1, -1) if looking_up else (1, 0))
    wx, wf = mover(c, tl, t, "whiskers", wkeys, PA_FEET, 0.82, 1, pose="sit" if sitting else "stand",
                   eyes="happy" if T("p_royal") <= t < T("p_royal", 1) else "open",
                   look=(1, -1) if looking_up else (1, 0))
    if hat == "whiskers":
        hx = wx + 52 * 0.82 * wf
        P.bearskin(c, hx + 2 * wf, PA_FEET - 0.82 * 84, 0.9)
    pp = T("p_there") <= t < T("p_run")
    mover(c, tl, t, "pip", pkeys, PA_FEET, 0.75, 1, proud=pp)
    if pp:
        # the trunk far away, heading for Tivoli
        u = tl.prog("p_there", t)
        P.trunk(c, camx + lerp(1000, 1250, u), 150 - 30 * u, 0.22, glow=0.6, t=t)
    c.pop()
    return finish(c, tl, t)


# ======================================================================= tivoli

def tivoli_bg():
    def make():
        c = Canvas(sky_img([(0, (14, 16, 48)), (0.55, (40, 40, 100)), (1, (90, 60, 120))]))
        D.stars(c, 51, 90, W, 380)
        D.moon(c, 1180, 90, 30, sky=(20, 22, 60))
        rng = np.random.default_rng(52)
        P.skyline(c, -20, W + 20, 500, rng, 40, 120, [(36, 34, 70), (44, 40, 80)], win=(255, 210, 120), p=0.25)
        P.town_tower(c, 120, 500, 0.8, col=(60, 46, 80), lw=2)
        # the painted mountain the coaster runs through, and the trestle
        P.mountain_facade(c, 1060, 640, 1.0)
        P.coaster_track(c, lit=1.0)
        # ground: garden path with flower beds
        c.rect(-10, 630, W + 10, H + 10, (70, 60, 76), w=2.5)
        for x in range(0, W, 70):
            c.ellipse(x + 20, 676, 30, 7, (84, 74, 92), ol=None)
        c.rect(-10, 626, W + 10, 640, (110, 90, 70), w=2)
        # lamp posts
        for lx in (40, 960):
            c.line([(lx, 640), (lx, 470)], (40, 40, 50), 6)
            soft_glow(c, lx, 460, 90, (255, 220, 150), 0.5)
            c.circle(lx, 460, 14, (255, 236, 170), w=2.5)
        return c.img
    return cached("tivoli", make)


STRINGS = [((-20, 40), (420, 70), 60, 14), ((380, 60), (840, 30), 50, 14), ((800, 30), (1300, 70), 60, 14),
           ((-20, 200), (300, 140), 40, 9)]


def coaster_u_of(tl, t):
    """Car position along the track during the ride."""
    T = tl.t
    if t < T("tv_ride", 0.12):
        return 0.0
    if t < T("tv_ride", 0.5):
        return 0.3 * ease(tl.prog("tv_ride", t, 0.12, 0.5)) ** 1.3
    if t < T("tv_ride", 0.85):
        return lerp(0.3, 1.0, ease(tl.prog("tv_ride", t, 0.5, 0.85)))
    return 1.0


def tivoli(tl, t):
    T = tl.t
    c = Canvas(tivoli_bg().copy())
    lit = ease(tl.prog("tv_narr", t, 0.05, 0.95))
    for k, ((x0, y0), (x1, y1), sag, n) in enumerate(STRINGS):
        P.lantern_string(c, x0, y0, x1, y1, sag, n, t, lit=clamp(lit * 1.3 - k * 0.1), seed=k)
    P.carousel(c, 220, 600, 0.62, t, lit=lit)
    # ---- fireworks at the end
    if t >= T("tv_cheer"):
        t0 = T("tv_cheer")
        for k, (fx, fy, col) in enumerate(((300, 160, (255, 120, 120)), (640, 110, (255, 230, 120)),
                                           (980, 150, (140, 220, 255)), (480, 200, (200, 150, 255)),
                                           (820, 90, (140, 255, 160)))):
            P.firework(c, fx, fy, t, t0 + k * 0.5, col, r=80 + 10 * k)
            P.firework(c, fx + 60, fy + 30, t, t0 + 2.6 + k * 0.6, col, r=70)
    # ---- the trunk, stuck on top of the coaster (until Saga brings it down)
    peak = (790, 160)
    fly0, fly1 = T("tv_fly", 0.15), T("tv_fly", 0.95)
    dpos = None
    trunk_pos = peak
    trunk_glow = 0.2
    if t >= T("tv_fly"):
        u = tl.prog("tv_fly", t)
        if u < 0.15:
            dpos = (lerp(400, 470, u / 0.15), PA_FEET + 2 - abs(math.sin(t * 10)) * 10, False)
        elif u < 0.5:
            k = ease((u - 0.15) / 0.35)
            dpos = (lerp(470, 740, k), lerp(PA_FEET, 120, k) + arc_y(k, 40), True)
        elif u < 0.6:
            dpos = (740 + 8 * math.sin(t * 4), 120, True)
        else:
            k = ease((u - 0.6) / 0.35)
            dpos = (lerp(740, 900, k), lerp(120, 560, k), True)
            trunk_pos = (dpos[0] + 50, dpos[1] + 70)
            if u >= 0.95:
                dpos = (910, PA_FEET, False)
                trunk_pos = (1050, 660)
        trunk_glow = 0.2 + 0.6 * (0.5 <= u < 0.95)
    if t >= T("tv_swan") or (t >= T("tv_fly") and tl.prog("tv_fly", t) >= 0.95):
        trunk_pos = (1050, 660)
    # coaster car
    cu = coaster_u_of(tl, t)
    (cx, cy), ang = P.coaster_point(cu)
    riding = T("tv_ride", 0.12) <= t < T("tv_ride", 0.88)
    if riding:
        ca, sa = math.cos(ang), math.sin(ang)
        D.cat(c, cx + 24 * sa, cy - 24 * ca, D.WHISKERS, 0.5, 1, "sit", t=t, eyes="wide",
              mouth=0.6 if cu > 0.3 else 0.0, seed=0.0)
    P.coaster_car(c, cx, cy, ang, 0.9)
    near_peak = T("tv_ride", 0.44) <= t < T("tv_ride", 0.56)
    P.trunk(c, trunk_pos[0], trunk_pos[1], 0.42, glow=trunk_glow, t=t)
    if near_peak:
        c.text(cx + 40, cy - 70, "!", 40, (255, 255, 255), stroke=3)
    # ---- Saga's flight
    if dpos is not None and dpos[2]:
        white = clamp((dpos[1] - PA_FEET) / (120 - PA_FEET) * 1.4) if tl.prog("tv_fly", t) < 0.5 else 1.0
        soft = clamp(1 - abs(tl.prog("tv_fly", t) - 0.5) * 4)
        if soft > 0:
            sparkles(c, t, dpos[0] - 120, dpos[0] + 120, dpos[1] - 160, dpos[1] + 40, n=18, seed=7, k=1.2 * soft)
        saga(c, tl, t, dpos[0], dpos[1], 0.9, 1, fly=True, white=white, eyes="happy")
    # ---- everyone on the path
    swan = t >= T("tv_swan") or (dpos is not None and not dpos[2] and tl.prog("tv_fly", t) > 0.9)
    enter = T("tv_narr", 0.3)
    lkeys = [(enter, -150), (T("tv_lights", 0.8), 550), (T("tv_ride"), 550), (T("tv_ride", 0.1), 540)]
    pkeys = [(enter, -80), (T("tv_lights", 0.75), 650)]
    dkeys = [(enter, -50), (T("tv_lights", 0.7), 400)]
    if dpos is None:
        mover(c, tl, t, "saga", dkeys, PA_FEET, 0.9, 1, look=(0, -1) if t < T("tv_cant") else (0, 0),
              sad=T("tv_cant") <= t < T("tv_spread"))
    elif not dpos[2]:
        saga(c, tl, t, dpos[0], dpos[1], 0.9, 1 if not swan else -1, white=1.0 if swan else 0.0,
              wing=1.0 if T("tv_iam") <= t < T("tv_cheer", 1) else 0.0, eyes="happy" if swan else "open")
    luna_eyes = "happy" if t >= T("tv_swan") else "open"
    luna_x, _ = mover(c, tl, t, "luna", lkeys, PA_FEET, 0.85, 1, look=(1, -1) if t < T("tv_cant") else (-1, 0),
                      eyes=luna_eyes)
    pip(c, tl, t, smooth(t, pkeys), PA_FEET, 0.8, 1 if t < T("tv_spread") else -1,
        eyes="happy" if t >= T("tv_swan") else "open",
        hop=abs(math.sin(t * 9)) * 12 if t >= T("tv_cheer") else None, proud=T("tv_swan") <= t < T("tv_iam"))
    # Whiskers: to the station, the ride, dizzy, then with the others
    if t < T("tv_ride", 0.12):
        wkeys = [(enter, -250), (T("tv_lights", 0.85), 780), (T("tv_ride", 0.0), 780), (T("tv_ride", 0.1), 200)]
        mover(c, tl, t, "whiskers", wkeys, PA_FEET, 0.85, 1, look=(1, -1) if t < T("tv_me") else (1, 0))
    elif t >= T("tv_ride", 0.88):
        wkeys = [(T("tv_ride", 0.88), 200), (T("tv_miss", 1.0), 240), (T("tv_high", 0.2), 240),
                 (T("tv_high", 0.9), 770)]
        dizzy = t < T("tv_high")
        x = smooth(t, wkeys)
        if dizzy:
            sway = math.sin(t * 5) * 8
            kitty(c, tl, t, "whiskers", x + sway, PA_FEET, 0.85, 1, "stand", eyes="closed" if int(t * 2) % 2 else "happy",
                  head_dy=4 * math.sin(t * 5))
            for j in range(4):
                a = t * 4 + j * math.pi / 2
                P.star(c, x + 50 + math.cos(a) * 40, PA_FEET - 140 + math.sin(a) * 10, 7, (255, 230, 90))
        else:
            mover(c, tl, t, "whiskers", wkeys, PA_FEET, 0.85, 1 if t < T("tv_fly") else -1,
                  look=(-1, 0) if t < T("tv_fly") else (-1, -1),
                  eyes="happy" if t >= T("tv_swan") else "open")
    if t >= T("tv_cheer"):
        hearts_up(c, t, 680, 520, 1.0, 4, seed=2)
    c = zoom(c, 640, 360, 1.0)
    return finish(c, tl, t)


# ======================================================================= hygge

def hygge_bg():
    def make():
        c = Canvas(bg=(150, 96, 60))
        # wooden cabin walls
        for x in range(0, W, 70):
            c.rect(x, 0, x + 70, 520, mix((166, 108, 68), (140, 90, 56), (x // 70) % 2 * 0.6), ol=None)
            c.line([(x, 0), (x, 520)], (110, 70, 44), 2, cap=False)
        c.rect(-10, -10, W + 10, 40, (110, 70, 44), w=2.5)
        # two round portholes with Nyhavn by night
        for px in (330, 950):
            c.circle(px, 210, 100, (60, 50, 50), w=3)
            win = Canvas(size=(200, 200), bg=(20, 24, 60))
            D.stars(win, int(px), 14, 200, 80)
            rng = np.random.default_rng(int(px) + 1)
            harbour_houses(win, -20, 220, 150, rng, 80, 120, lit=0.7, scale=0.55)
            water(win, 0, 200, 150, 200, rng, col=(30, 40, 80), hi=(255, 210, 120), n=30)
            m = Image.new("L", (200 * SS, 200 * SS), 0)
            ImageDraw.Draw(m).ellipse([8 * SS, 8 * SS, 192 * SS, 192 * SS], fill=255)
            c.img.paste(win.img, (int((px - 100) * SS), int(110 * SS)), m)
            c.circle(px, 210, 92, None, ol=(200, 160, 80), w=8)
            for a in range(8):
                ang = a * math.tau / 8
                c.circle(px + math.cos(ang) * 92, 210 + math.sin(ang) * 92, 4, (240, 210, 120), w=1)
        # shelf with jars and a hanging lamp
        c.rect(560, 150, 740, 162, (110, 70, 44), w=2)
        for k, col in enumerate(((240, 200, 120), (200, 120, 90), (230, 230, 200), (150, 190, 140))):
            c.rect(570 + k * 44, 112, 600 + k * 44, 150, col, w=2, r=4)
        c.line([(650, 0), (650, 60)], OUT, 3)
        c.poly([(620, 60), (680, 60), (700, 96), (600, 96)], (220, 120, 60), w=2.5)
        soft_glow(c, 650, 110, 300, (255, 210, 140), 0.45)
        # floor, bench and table
        c.rect(-10, 520, W + 10, H + 10, (120, 76, 48), ol=None)
        c.rect(-10, 500, W + 10, 560, (176, 70, 70), w=2.5, r=10)        # bench cushion along the wall
        for x in range(60, W, 160):
            c.line([(x, 506), (x + 20, 554)], (200, 100, 100), 3, cap=False)
        c.rect(150, 600, 1130, 630, (176, 122, 76), w=3, r=6)
        c.rect(150, 628, 1130, H + 10, (150, 100, 62), w=3)
        for x in (180, 1100):
            c.rect(x - 10, 630, x + 10, H + 10, (130, 86, 54), w=2)
        # embroidered runner on the table
        c.rect(300, 602, 980, 616, (250, 246, 236), w=2)
        for x in range(320, 980, 30):
            c.circle(x, 609, 3, (220, 60, 70), ol=None)
        # warm candle glows (cached, the flames flicker per frame)
        for x in (260, 640, 1040):
            soft_glow(c, x, 560, 220, (255, 200, 120), 0.4)
        return c.img
    return cached("hygge", make)


def hygge(tl, t):
    T = tl.t
    c = Canvas(hygge_bg().copy())
    # Bodil pours cocoa at the right
    pouring = T("hy_narr", 0.5) <= t < T("hy_hygge")
    bodil(c, tl, t, 1150, 640, 0.95, -1, arm=0.6 if pouring else 0.0, pot=True,
          eyes="happy" if t >= T("hy_cosy") else "open")
    # cats on the bench, wrapped in blankets
    sleepy = t >= T("hy_cosy", 0.3)
    kitty(c, tl, t, "luna", 430, 600, 0.9, 1, "sit", eyes="happy" if sleepy else "open", look=(1, 0))
    P.blanket(c, 432, 600, 120, 70, (90, 120, 200), (230, 236, 250))
    kitty(c, tl, t, "whiskers", 600, 600, 0.95, 1, "sit",
          eyes="closed" if sleepy else ("happy" if T("hy_word") <= t < T("hy_word", 1) else "open"),
          look=(1, 0))
    P.blanket(c, 604, 600, 132, 74, (200, 60, 60), (250, 220, 200))
    saga(c, tl, t, 860, 600, 0.95, -1, white=1.0, eyes="happy" if sleepy else "open")
    if sleepy:
        D.zzz(c, 640, 460, t)
    # table things
    for x in (260, 640, 1040):
        P.candle(c, x, 640, 1.0, t)
    P.mug(c, 470, 660, 1.0, (90, 140, 220), t)
    P.mug(c, 560, 664, 1.1, (220, 80, 80), t)
    P.mug(c, 800, 660, 1.0, (250, 200, 90), t)
    P.mug(c, 730, 650, 0.45, (240, 140, 200), t)
    pip(c, tl, t, 720, 640, 0.75, 1, eyes="happy" if sleepy else "open")
    P.pastry(c, 950, 650, 1.0, 2)
    P.pastry(c, 340, 652, 1.0, 0)
    if pouring:
        u = tl.prog("hy_narr", t, 0.5, 1.0)
        c.line([(1080, 520), (lerp(1060, 990, u), 600)], (110, 60, 40), 5)
    c = zoom(c, 700, 480, 1.25 + 0.05 * ease(tl.prog("hy_cosy", t)))
    return finish(c, tl, t)


# ======================================================================= home

def home_sky_bg():
    def make():
        c = Canvas(sky_img([(0, (120, 160, 230)), (0.5, (250, 200, 180)), (0.8, (255, 226, 170)),
                            (1, (240, 236, 200))]))
        soft_glow(c, 300, 560, 360, (255, 236, 180), 0.6)
        for x, y, s in ((220, 160, 0.8), (720, 90, 0.6), (1100, 200, 0.9)):
            D.cloud(c, x, y, s, (255, 236, 230))
        c.ellipse(300, 760, 700, 260, (110, 170, 100), w=3)
        c.ellipse(1050, 780, 600, 280, (96, 156, 90), w=3)
        # the cats' house on the hill
        c.rect(860, 470, 1000, 560, (250, 228, 190), w=2.5)
        c.poly([(845, 474), (930, 420), (1015, 474)], (196, 92, 70), w=2.5)
        c.rect(890, 500, 930, 530, (255, 220, 130), w=2)
        D.tree(c, 1080, 560, 0.5)
        D.tree(c, 200, 600, 0.6)
        return c.img
    return cached("home_sky", make)


def home_room_bg():
    def make():
        c = Canvas(MF.room(False).copy())
        return c.img
    return cached("home_room", make)


def home(tl, t):
    T = tl.t
    if t < T("h_land"):
        c = Canvas(home_sky_bg().copy())
        u = clamp((t - T("h_fly")) / max(1e-6, T("h_land") - T("h_fly")))
        x = lerp(1400, 700, ease(u))
        y = lerp(240, 420, ease(u)) + 8 * math.sin(t * 2)
        s = lerp(0.9, 0.5, ease(u))
        for j in range(3):
            c.line([(x + 130 * s + j * 26, y - 60 * s + j * 18 * s), (x + 250 * s + j * 30, y - 60 * s + j * 18 * s)],
                   (255, 255, 255), 3)
        c.push(x, y)
        c.tf[-1] = (c.tf[-1][0], c.tf[-1][1], -1.0, 1.0)
        trunk_ride(c, tl, t, 0, 0, s, ("luna", "whiskers", "pip"), eyes={"luna": "happy", "whiskers": "happy"})
        c.pop()
        # Saga flying alongside, then peeling away with a wave
        peel = ease(tl.prog("h_narr", t, 0.6, 1.0))
        dx = x - 40 + 400 * peel
        dy = y - 160 * s - 300 * peel
        saga(c, tl, t, dx, dy, 0.8 * (1 - 0.4 * peel), -1 if peel < 0.3 else 1, fly=True, white=1.0, eyes="happy")
        return finish(c, tl, t)
    c = Canvas(home_room_bg().copy())
    # trunk sails in through the window and lands
    u = tl.prog("h_land", t, 0.0, 0.5)
    tx = lerp(920, TRUNK_HOME[0], ease(u))
    ty = lerp(260, TRUNK_HOME[1], u * u)
    ts = lerp(0.15, 0.9, ease(u))
    if u < 1:
        trunk_ride(c, tl, t, tx, ty, ts, ("luna", "whiskers", "pip"), eyes={"luna": "happy", "whiskers": "wide"})
    else:
        P.trunk(c, TRUNK_HOME[0], TRUNK_HOME[1], 0.9, lid=0.0)
        P.book_cover(c, 290, 662, 0.9)
        # cats hop up onto the windowsill
        k = tl.prog("h_land", t, 0.55, 0.9)
        lit = t >= T("h_home", 0.5)
        P.candle(c, 900, SILL_Y, 0.8, t, lit=lit)
        if lit:
            soft_glow(c, 900, SILL_Y - 50, 160, (255, 210, 140), 0.25)
        if k < 1:
            D.cat(c, lerp(880, 820, k), lerp(560, SILL_Y, k) + arc_y(k, 120), D.LUNA, 0.75, -1, "leap", t=t, seed=1.3)
            D.cat(c, lerp(960, 990, k), lerp(560, SILL_Y, k) + arc_y(k, 110), D.WHISKERS, 0.75, 1, "leap", t=t)
        else:
            kitty(c, tl, t, "luna", 820, SILL_Y, 0.75, 1, "sit", look=(1, 0),
                  eyes="happy" if t >= T("h_moral") else "open")
            kitty(c, tl, t, "whiskers", 990, SILL_Y, 0.75, -1, "sit",
                  eyes="happy" if T("h_perfect") <= t else "open", look=(1, 0))
            if t >= T("h_perfect"):
                kb = ease(tl.prog("h_perfect", t, 0.0, 0.3))
                P.blanket(c, 994, SILL_Y, 100 * kb, 58 * kb, (200, 60, 60), (250, 220, 200))
                P.mug(c, 870, SILL_Y, 0.7, (90, 140, 220), t)
                P.mug(c, 940, SILL_Y, 0.7, (220, 80, 80), t)
        pip(c, tl, t, lerp(980, 380, ease(tl.prog("h_land", t, 0.6, 1.0))), 665, 0.85, -1 if t < T("h_book") else 1)
        # Saga flies past the window at the very end, waving
        if t >= T("h_moral", 0.5):
            v = (t - T("h_moral", 0.5)) / 5.0
            if v < 1:
                saga(c, tl, t, lerp(1120, 700, v), 210 + 20 * math.sin(v * 6), 0.35, -1, fly=True, white=1.0,
                      eyes="happy")
                # redraw the window frame bars over her
                c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
                c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
        if T("h_book") - 0.3 <= t < T("h_book", 1.0) + 0.3:
            kk = ease(clamp((t - T("h_book") + 0.3) / 0.5)) * ease(clamp((T("h_book", 1.0) + 0.3 - t) / 0.5))
            c = blend_over(c, (30, 30, 50), 0.45 * kk)
            c.push(640, 320 + 400 * (1 - kk))
            P.book_open(c, 0, 0, page="duckling", t=t)
            c.pop()
        if t >= T("h_end", 0.3):
            k2 = ease(tl.prog("h_end", t, 0.3, 0.6))
            c.text(640, 80, "The End", 56 * (0.6 + 0.4 * k2), mix((250, 228, 190), (240, 100, 90), k2), stroke=4 * k2)
    z = 1.0
    if t >= T("h_real"):
        z = 1 + 0.4 * ease(tl.prog("h_real", t, 0.0, 0.5)) * (1 - ease(tl.prog("h_end", t, 0.0, 0.5)))
    c = zoom(c, 905, 330, z)
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "rain": rain, "flight": flight, "nyhavn": nyhavn, "bakery": bakery,
               "palace": palace, "tivoli": tivoli, "hygge": hygge, "home": home}
CONTINUOUS = {"bakery"}
EXTRA_CUTS = ["h_land"]
