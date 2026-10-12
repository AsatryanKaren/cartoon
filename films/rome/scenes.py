"""Rome film: one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync whatever the speech lengths turn out to be. Static backgrounds are
drawn once and cached; characters, water, smoke and props are drawn live.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix, OUT
from films.rome import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "nico": 3.0, "rosa": 4.2}
NIGHT = ((40, 50, 115), 0.32)
DUSK = ((255, 140, 80), 0.10)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def view(bg, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    if bg.size == (W * SS, H * SS) and not x and not y:
        return Canvas(bg.copy())
    return Canvas(bg.crop((x, y, x + W * SS, y + H * SS)))


# ------------------------------------------------------------------ motion

def track(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def arc_y(u, height):
    return -4 * height * u * (1 - u)


def coin_on_luna(tl, t):
    return tl.t("p_collar", 0.8) <= t < tl.t("pz_eat", 0.3)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """Draw a character moving along x keyframes; faces its direction of travel."""
    x = smooth(t, keys)
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    mouth = kw.pop("mouth", tl.mouth(who, t))
    if who == "pip":
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "nico":
        P.pigeon(c, x, y, s, face, t, walk=x / 5 if moving and not kw.get("fly") else 0.0, mouth=mouth, **kw)
    elif who == "rosa":
        P.rosa(c, x, y, s, face, pose, t=t, mouth=mouth, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        D.cat(c, x, y, PAL[who], s, face, pose, walk=x / 12 if moving else 0.0, t=t,
              mouth=mouth, seed=SEED[who], **kw)
        if who == "luna" and coin_on_luna(tl, t):
            P.collar_coin(c, x, y, s, face, pose, kw.get("head_dy", 0.0))
    return x


def cat(c, tl, t, who, x, y, face=1, pose="sit", s=1.0, **kw):
    """A character standing still."""
    return actor(c, tl, t, who, [(0, x)], y, s, face, pose, **kw)


def flyer(c, tl, t, keys_x, keys_y, s=1.4, land=None, face=None, **kw):
    """Nico along x/y keyframes; flaps while airborne (land: time he touches down)."""
    x, y = smooth(t, keys_x), smooth(t, keys_y)
    vx = (smooth(t + 0.05, keys_x) - smooth(t - 0.05, keys_x)) / 0.1
    vy = (smooth(t + 0.05, keys_y) - smooth(t - 0.05, keys_y)) / 0.1
    fly = abs(vx) + abs(vy) > 25
    f = face if face is not None else 1
    if abs(vx) > 25:
        f = 1 if vx > 0 else -1
    P.pigeon(c, x, y, s, f, t, mouth=kw.pop("mouth", tl.mouth("nico", t)), fly=fly, **kw)
    return x, y


def hearts(c, x, y, t, t0, n=4):
    for k in range(n):
        u = ((t - t0) * 0.5 + k / n) % 1.0
        if t < t0:
            return
        hx = x + 30 * math.sin(k * 2.1 + u * 4)
        hy = y - 120 * u
        r = 8 * (1 - u * 0.4)
        col = mix((240, 80, 110), (255, 200, 210), u)
        c.circle(hx - r * 0.5, hy, r * 0.6, col, ol=None)
        c.circle(hx + r * 0.5, hy, r * 0.6, col, ol=None)
        c.poly([(hx - r * 1.05, hy + 1), (hx + r * 1.05, hy + 1), (hx, hy + r * 1.2)], col, ol=None)


def speed_lines(c, x, y, face, t):
    for k in range(5):
        yy = y - 30 - k * 18
        x0 = x - face * (70 + 20 * ((t * 9 + k * 0.37) % 1.0))
        c.line([(x0, yy), (x0 - face * (50 + 10 * k % 30), yy)], (255, 255, 255), 3)


def dust(c, x, y, t, t0, dur=0.8):
    u = (t - t0) / dur
    if 0 <= u < 1:
        for k in range(5):
            r = 10 + 26 * u
            c.circle(x - 30 * k * u, y - 8 - 10 * math.sin(k) * u, r * (1 - 0.1 * k),
                     mix((230, 220, 200), (255, 255, 255), u), ol=None)


def bang(c, x, y, s, label, col=(255, 230, 90)):
    c.push(x, y, s)
    pts = []
    for k in range(16):
        r = 46 if k % 2 == 0 else 28
        a = k * math.tau / 16
        pts.append((math.cos(a) * r * 1.3, math.sin(a) * r))
    c.poly(pts, col, w=3)
    c.pop()
    c.text(x, y, label, 30 * s, (200, 50, 40), stroke=2, stroke_fill=(255, 255, 255))


def window_light(img, col, strength, win=(760, 110, 1080, 370)):
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)

    def p(u, v):
        return (lerp(lerp(650, 900, u), lerp(470, 790, u), v) * SS, lerp(548, 700, v) * SS)
    gap = 0.03
    for u0, u1 in ((0, 0.5 - gap), (0.5 + gap, 1)):
        for v0, v1 in ((0, 0.5 - gap), (0.5 + gap, 1)):
            md.polygon([p(u0, v0), p(u1, v0), p(u1, v1), p(u0, v1)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(7 * SS)).point(lambda a: int(a * strength))
    img.paste(Image.new("RGB", img.size, col), (0, 0), mask)


# ------------------------------------------------------------------- title

def roman_skyline(c, base, col, s=1.0, x0=0, width=W, seed=2, detail=None):
    """Silhouette skyline: domes, bell towers, pines, cypresses and a little Colosseum."""
    rng = np.random.default_rng(seed)
    x = x0 - 40
    while x < x0 + width + 40:                                          # rooftops
        w_ = rng.uniform(50, 110) * s
        h_ = rng.uniform(30, 80) * s
        c.rect(x, base - h_, x + w_, base + 40, col, ol=None)
        x += w_ - 2
    for px, kind in detail:
        if kind == "dome":
            c.rect(px - 46 * s, base - 150 * s, px + 46 * s, base, col, ol=None)
            c.ellipse(px, base - 150 * s, 62 * s, 70 * s, col, ol=None)
            c.rect(px - 70 * s, base - 150 * s, px + 70 * s, base - 140 * s, col, ol=None)
            c.rect(px - 8 * s, base - 240 * s, px + 8 * s, base - 210 * s, col, ol=None)
            c.poly([(px - 12 * s, base - 240 * s), (px + 12 * s, base - 240 * s), (px, base - 262 * s)], col,
                   ol=None)
            c.rect(px - 140 * s, base - 90 * s, px + 140 * s, base, col, ol=None)
        elif kind == "smalldome":
            c.ellipse(px, base - 70 * s, 34 * s, 40 * s, col, ol=None)
            c.rect(px - 40 * s, base - 70 * s, px + 40 * s, base, col, ol=None)
            c.rect(px - 4 * s, base - 124 * s, px + 4 * s, base - 100 * s, col, ol=None)
        elif kind == "tower":
            c.rect(px - 16 * s, base - 170 * s, px + 16 * s, base, col, ol=None)
            c.poly([(px - 20 * s, base - 170 * s), (px + 20 * s, base - 170 * s), (px, base - 200 * s)], col,
                   ol=None)
        elif kind == "colosseum":
            c.rect(px - 120 * s, base - 110 * s, px + 70 * s, base, col, ol=None)
            c.poly([(px + 70 * s, base - 110 * s), (px + 120 * s, base - 50 * s), (px + 120 * s, base),
                    (px + 70 * s, base)], col, ol=None)
        elif kind == "pine":
            P.umbrella_pine(c, px, base + 5, 0.7 * s, col=col, ol=None)
        elif kind == "cypress":
            P.cypress(c, px, base + 5, 0.7 * s, col=col, ol=None)


def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (70, 70, 140)), (0.35, (190, 110, 140)), (0.62, (255, 170, 100)),
                                               (0.8, (255, 210, 140)), (1, (255, 210, 140))]))
        c.glow(700, 470, 260, 200, (255, 236, 170), (255, 180, 110), steps=12)
        c.circle(700, 470, 70, (255, 240, 190), ol=None)
        for x, y, s in ((180, 120, 0.9), (1080, 90, 0.7), (520, 60, 0.6)):
            D.cloud(c, x, y, s, col=(255, 205, 190))
        roman_skyline(c, 520, (150, 90, 110), 0.9, seed=5,
                      detail=[(140, "pine"), (330, "colosseum"), (520, "tower"), (870, "dome"), (1090, "smalldome"),
                              (1200, "pine"), (640, "cypress"), (1000, "cypress")])
        roman_skyline(c, 575, (110, 60, 86), 1.0, seed=9, detail=[(60, "cypress"), (430, "pine"), (1240, "tower")])
        # terracotta rooftop in the foreground
        c.poly([(0, 600), (W, 580), (W, H), (0, H)], (196, 96, 64))
        for k, y in enumerate(range(606, H + 20, 22)):
            c.line([(0, y), (W, y - 20 * (1 - (y - 600) / 140))], (160, 70, 50), 3, cap=False)
            for x in range(-20 + (k % 2) * 18, W, 36):
                c.arc(x + 18, y - 4, 18, 9, 0, 180, (220, 120, 80), 3)
        c.rect(980, 520, 1040, 600, (180, 90, 70))
        c.rect(970, 510, 1050, 528, (150, 70, 56))
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    for k in range(5):                                      # swallows
        u = (t * 0.05 + k * 0.21) % 1.0
        bx, by = lerp(-50, W + 50, u), 200 + 60 * math.sin(k * 2 + u * 6)
        flap = 8 * math.sin(t * 9 + k)
        c.line([(bx - 12, by - flap), (bx, by), (bx + 12, by - flap)], (90, 60, 80), 3)
    c.tint = DUSK
    cat(c, tl, t, "whiskers", 520, 612, 1, "sit", s=0.95, look=(0.6, -0.8))
    cat(c, tl, t, "luna", 640, 608, 1, "sit", s=0.9, look=(0.6, -1), tail=math.sin(t * 1.5))
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.7))
    c.text(W / 2, 110 - 30 * (1 - k), "Whiskers and the", 46, mix((90, 80, 140), (255, 236, 190), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 196, "WISHING COIN", 30 + 62 * k2, mix((90, 80, 140), (255, 214, 90), k2), stroke=5 * k2)
    k3 = ease(tl.prog("t_name", t, 0.5, 1.0))
    if k3 > 0:
        c.text(W / 2, 268, "a Roman adventure", 30, mix((200, 120, 130), (255, 245, 225), k3), stroke=2 * k3)
    if k2 > 0.9:                                             # spinning coin glint
        spin = math.cos(t * 3)
        P.coin(c, W / 2 + 385, 196, 22, spin)
        g = (t * 0.6) % 1.0
        if g < 0.3:
            P.twinkle(c, W / 2 + 395, 182, 16 * math.sin(math.pi * g / 0.3))
    return c


# ---------------------------------------------------------------- the room

def room(night=False):
    def make():
        if night:
            wall, floor, sky = (92, 88, 130), (88, 66, 70), [(0, (20, 26, 64)), (1, (60, 62, 120))]
        else:
            wall, floor, sky = (250, 228, 190), (196, 136, 88), [(0, (120, 190, 245)), (1, (205, 235, 255))]
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, 520, mix(wall, (255, 255, 255) if not night else (60, 60, 90), 0.25), ol=None)
        c.rect(0, 520, W, H, floor, ol=None)
        for y in range(540, H, 36):
            c.line([(0, y), (W, y)], mix(floor, (0, 0, 0), 0.12), 2, cap=False)
        c.rect(0, 506, W, 524, mix(wall, (0, 0, 0), 0.25), ol=None)
        win = D.gradient(320 * SS, 260 * SS, sky)
        c.img.paste(win, (760 * SS, 110 * SS))
        if night:
            c.push(760, 110)
            D.stars(c, 5, 30, 320, 260)
            c.pop()
            D.moon(c, 990, 180, 32, sky=(40, 44, 96))
        else:
            c.circle(1010, 170, 34, (255, 222, 90), ol=None)
            D.cloud(c, 850, 210, 0.7)
        c.rect(756, 106, 1084, 374, None, w=8)
        mull = (240, 240, 240) if not night else (150, 150, 180)
        c.line([(920, 110), (920, 370)], mull, 6, cap=False)
        c.line([(760, 240), (1080, 240)], mull, 6, cap=False)
        c.rect(740, 370, 1100, 392, (255, 250, 240) if not night else (150, 146, 170), r=4)
        c.ellipse(520, 612, 190, 40, (200, 70, 80) if not night else (110, 60, 90))
        c.ellipse(520, 612, 150, 28, (230, 120, 110) if not night else (130, 80, 110), ol=None)
        c.rect(150, 440, 210, 520, (190, 100, 70), r=6)
        for dx, dy in ((-30, -10), (0, -40), (30, -12), (-15, -30), (18, -36)):
            c.ellipse(180 + dx, 440 + dy, 14, 30, (80, 160, 90))
        # a framed picture of the Moon Fish pond (Film 1) on the wall
        tint = 0.35 if night else 0.0
        c.rect(380, 170, 560, 300, mix((150, 100, 60), (60, 60, 90), tint), w=3, r=4)
        c.rect(394, 184, 546, 286, mix((30, 40, 90), (20, 20, 50), tint), ol=None)
        c.circle(510, 210, 12, (250, 246, 215), ol=None)
        c.rect(394, 250, 546, 286, (30, 50, 96), ol=None)
        c.ellipse(470, 266, 26, 6, (240, 236, 200), ol=None)
        c.poly([(494, 266), (506, 260), (506, 272)], (240, 236, 200), ol=None)
        window_light(c.img, (255, 236, 185) if not night else (150, 160, 220), 0.22 if not night else 0.14)
        return c.img
    return cached(("room", night), make)


def bowl(c, x, y):
    c.push(x, y)
    c.poly([(-40, -28), (40, -28), (28, 0), (-28, 0)], (90, 150, 220))
    c.ellipse(0, -28, 40, 8, (70, 120, 190))
    c.ellipse(0, -30, 30, 5, (170, 110, 70), ol=None)
    c.text(0, -12, "W", 16, (255, 255, 255))
    c.pop()


def card_at(c, x, y, s, flat=1.0, flip=1.0, t=0.0):
    """The postcard at (x, y); flat squashes it vertically (lying on the floor), flip turns it."""
    c.push(x, y, s)
    ox, oy, sx, sy = c.tf[-1]
    c.tf[-1] = (ox, oy, sx * flip if abs(flip) > 0.08 else sx * 0.08, sy * flat)
    if abs(flip) < 0.35:
        c.rect(-160, -110, 160, 110, (255, 252, 240), w=3, r=6)
    else:
        P.postcard(c, 0, 0, 1.0, t)
    c.pop()


def postcard(tl, t):
    T = tl.t
    c = Canvas(room(False).copy())
    bowl(c, 1160, 610)
    # Whiskers: asleep until the card hits him
    if t < T("p_hey"):
        D.cat(c, 520, 615, D.WHISKERS, 1.0, 1, "sleep", t=t, mouth=0)
        if t < T("p_card", 0.8):
            D.zzz(c, 580, 540, t)
    else:
        startled = T("p_hey") <= t < T("p_hey", 1)
        wide = startled or T("p_pizza") <= t < T("p_pizza", 1) + 0.6
        look = (1, 0.6) if T("p_look") <= t < T("p_pizza") else (1, -0.3)
        cat(c, tl, t, "whiskers", 520, 615, 1, "sit", eyes="wide" if wide else "open", look=look,
            head_dy=-8 * max(0.0, 1 - (t - T("p_hey")) / 0.3))
    # Luna
    lface = 1 if t >= T("p_pip_in", 0.3) else -1
    leyes = "happy" if T("p_go") <= t < T("p_go", 1) + 0.3 else "open"
    llook = (1, 0.7) if T("p_look") <= t < T("p_zoom") else (1, 0)
    cat(c, tl, t, "luna", 790, 612, lface, "sit", eyes=leyes, look=llook)
    # Pip comes in from the right with his lucky coin
    if t >= T("p_pip_in"):
        px = smooth(t, [(T("p_pip_in"), 1360), (T("p_pip_in", 1), 960)])
        lift = 30 * ease(tl.prog("p_pip", t, 0.1, 0.4))
        happy = T("p_collar", 0.8) < t
        actor(c, tl, t, "pip", [(T("p_pip_in"), 1360), (T("p_pip_in", 1), 960)], 618, 1.4, face=-1,
              proud=T("p_pip") <= t < T("p_collar", 0.5), eyes="happy" if happy else "open")
        # the coin: in Pip's paws, then tossed to Luna's collar
        u = tl.prog("p_collar", t, 0.5, 0.8)
        if u < 1:
            cx0, cy0 = px - 20, 618 - 30 - lift
            cx1, cy1 = P.collar_point(790, 612, 1.0, lface, "sit")
            cx, cy = lerp(cx0, cx1, u), lerp(cy0, cy1, u) + arc_y(u, 80)
            P.coin(c, cx, cy, 11, math.cos(t * 9) if 0 < u else 1.0)
            if T("p_pip", 0.65) < t < T("p_pip", 0.85):
                P.twinkle(c, cx + 6, cy - 6, 14)
        elif t < T("p_collar", 1):
            cx, cy = P.collar_point(790, 612, 1.0, lface, "sit")
            P.twinkle(c, cx + 4, cy - 4, 14 * math.sin(math.pi * tl.prog("p_collar", t, 0.8, 1.0)))
    # the postcard
    if t >= T("p_card"):
        if t < T("p_card", 0.8):
            u = tl.prog("p_card", t, 0.0, 0.8)
            x = lerp(900, 575, ease(u)) + 70 * math.sin(u * 3 * math.pi) * (1 - u)
            y = lerp(250, 565, u)
            card_at(c, x, y, 0.22, 1.0, math.cos(u * 16), t)
        elif t < T("p_hey"):
            card_at(c, 578, 568, 0.22, 0.9, 1.0, t)
        elif t < T("p_zoom"):
            u = ease(tl.prog("p_hey", t, 0.0, 0.3))
            card_at(c, lerp(560, 650, u), lerp(500, 660, u) + arc_y(u, 40), 0.22, lerp(1.0, 0.3, u), 1.0, t)
        else:
            k = ease(tl.prog("p_zoom", t, 0.0, 0.3)) * (1 - ease(tl.prog("p_pizza", t, 0.0, 0.25)))
            card_at(c, lerp(650, 640, k), lerp(660, 300, k), lerp(0.22, 1.55, k), lerp(0.3, 1.0, k), 1.0, t)
            if 0.9 < k:
                g = (t * 0.8) % 1.0
                P.twinkle(c, 640 + 150, 300 - 120, 18 * math.sin(math.pi * g))
                P.twinkle(c, 640 - 190, 300 + 40, 12 * math.sin(math.pi * ((g + 0.5) % 1)))
    # a dreamy pizza over Whiskers' head
    k = ease(tl.prog("p_pizza", t, 0.2, 0.5)) * (1 - ease(tl.prog("p_go", t, 0.5, 0.9)))
    if k > 0.02:
        for dx, dy, r in ((40, 470, 6), (60, 440, 10)):
            c.circle(dx + 520, dy, r * k, (255, 255, 255), w=2)
        c.ellipse(620, 370, 90 * k, 60 * k, (255, 255, 255), w=2.5)
        if k > 0.6:
            P.pizza(c, 620, 378, 60 * k, persp=0.55)
    return c


# ----------------------------------------------------------------- train

TW = 2560


def _rgba(w):
    return Canvas(Image.new("RGBA", (w * SS, H * SS), (0, 0, 0, 0)), size=(w, H))


def _wrap(fn, x):
    for off in (-TW, 0, TW):
        fn(x + off)


def train_layers():
    def make():
        sky = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 180, 240)), (0.55, (200, 230, 250)), (1, (220, 240, 250))]))
        sky.circle(1050, 110, 46, (255, 230, 120), ol=None)
        for x, y, s in ((200, 90, 1.0), (620, 150, 0.7), (900, 70, 0.8)):
            D.cloud(sky, x, y, s)
        rng = np.random.default_rng(3)
        # far hills with little villages
        far = _rgba(TW)
        pts = [(x, 400 + 26 * math.sin(math.tau * x / TW * 3) + 14 * math.sin(math.tau * x / TW * 7))
               for x in range(0, TW + 20, 20)]
        far.poly(pts + [(TW, 560), (0, 560)], (168, 200, 176), ol=None)
        for vx in (300, 1100, 1900):
            def village(x):
                for k in range(5):
                    bx = x + k * 26
                    far.rect(bx, 392 - (k % 3) * 8, bx + 24, 430, [(232, 190, 130), (222, 150, 110),
                                                                     (240, 214, 170)][k % 3], ol=None)
                    far.rect(bx - 2, 388 - (k % 3) * 8, bx + 26, 394 - (k % 3) * 8, (190, 100, 80), ol=None)
                far.rect(x + 50, 360, x + 62, 400, (232, 200, 150), ol=None)
                P.cypress(far, x - 20, 432, 0.22, col=(100, 140, 110), ol=None)
                P.cypress(far, x + 150, 434, 0.25, col=(100, 140, 110), ol=None)
            _wrap(village, vx)
        # mid fields with pines, cypresses and olive groves
        mid = _rgba(TW)
        pts = [(x, 470 + 16 * math.sin(math.tau * x / TW * 2 + 1)) for x in range(0, TW + 20, 20)]
        mid.poly(pts + [(TW, 600), (0, 600)], (140, 186, 104), ol=None)
        for k in range(10):
            x0 = k * TW / 10
            col = [(222, 204, 120), (170, 200, 110), (200, 214, 120)][k % 3]
            mid.poly([(x0 + 20, 500), (x0 + 230, 498), (x0 + 250, 540), (x0, 542)], col, ol=None)
            for j in range(4):
                mid.line([(x0 + 10 + j * 8, 506 + j * 9), (x0 + 236 + j * 3, 504 + j * 9)], mix(col, (0, 0, 0), 0.1),
                         2, cap=False)
        for x in range(60, TW, 210):
            kind = (x // 210) % 4
            if kind == 0:
                _wrap(lambda xx: P.umbrella_pine(mid, xx, 520, 0.55), x)
            elif kind == 1:
                _wrap(lambda xx: [P.cypress(mid, xx + d, 522, 0.42) for d in (0, 34, 68)], x)
            elif kind == 2:
                _wrap(lambda xx: [P.olive(mid, xx + d, 526, 0.42) for d in (0, 50)], x)
            else:
                def farm(xx):
                    mid.rect(xx, 470, xx + 90, 524, (236, 196, 140))
                    mid.poly([(xx - 8, 472), (xx + 45, 446), (xx + 98, 472)], (196, 100, 76))
                    mid.rect(xx + 14, 486, xx + 30, 506, (90, 120, 90), w=2)
                    mid.rect(xx + 58, 486, xx + 74, 506, (90, 120, 90), w=2)
                _wrap(farm, x)
        # near: grassy bank with bushes and poppies, behind the track
        near = _rgba(TW)
        near.rect(0, 560, TW, H, (112, 168, 86), ol=None)
        for x in range(40, TW, 160):
            _wrap(lambda xx: D.bush(near, xx, 584, 0.6, col=(86, 150, 76)), x + rng.uniform(-30, 30))
        for _ in range(260):
            fx, fy = rng.uniform(0, TW), rng.uniform(588, 612)
            _wrap(lambda xx: near.circle(xx, fy, 3.2, (230, 50, 50), ol=None), fx)
        for x in range(0, TW, 128):
            _wrap(lambda xx: (near.rect(xx, 530, xx + 7, 598, (150, 120, 90), w=2),
                              near.rect(xx - 6, 534, xx + 13, 540, (150, 120, 90), w=2)), x)
            near.line([(x, 540), (x + 128, 546)], (60, 56, 64), 1.5, cap=False)
        # Rome skyline (does not tile; it slides in at the end of the journey)
        sk = _rgba(1500)
        roman_skyline(sk, 480, (200, 190, 210), 1.0, seed=4, width=1500,
                      detail=[(150, "smalldome"), (380, "tower"), (560, "colosseum"), (900, "dome"),
                              (1150, "smalldome"), (1300, "tower"), (720, "cypress"), (1220, "cypress")])
        roman_skyline(sk, 500, (214, 168, 140), 0.7, seed=8, width=1500, detail=[(300, "pine"), (1060, "pine")])
        return sky.img, far.img, mid.img, near.img, sk.img
    return cached("train", make)


def paste_wrap(img, layer, off):
    ox = int(off * SS) % (TW * SS)
    w2, h2 = W * SS, H * SS
    a = layer.crop((ox, 0, min(ox + w2, TW * SS), h2))
    img.paste(a, (0, 0), a)
    if ox + w2 > TW * SS:
        b = layer.crop((0, 0, ox + w2 - TW * SS, h2))
        img.paste(b, (a.size[0], 0), b)


def train_speed(tl, t):
    s0, s1 = tl.scenes["train"]
    up = 0.35 + 0.65 * ease((t - s0) / 2.5)
    down = 1 - ease((t - tl.t("tr_view", 0.4)) / max(1e-3, tl.t("tr_end", 0.8) - tl.t("tr_view", 0.4)))
    return 900 * up * down


def train_dist(tl, t):
    s0 = tl.scenes["train"][0]
    n = max(1, int((t - s0) / 0.04))
    h = (t - s0) / n
    return sum(train_speed(tl, s0 + (k + 0.5) * h) for k in range(n)) * h


def train(tl, t):
    T = tl.t
    sky, far, mid, near, sk = train_layers()
    d = train_dist(tl, t)
    v = train_speed(tl, t)
    img = sky.copy()
    paste_wrap(img, far, d * 0.06)
    # Rome slides into view and stops in the middle
    d_end, d_view = cached(("tdist", tl.scenes["train"], T("tr_view")),
                           lambda: (train_dist(tl, tl.scenes["train"][1]), train_dist(tl, T("tr_view"))))
    par = 1900.0 / max(1.0, d_end - d_view)
    if t > T("tr_view") - 0.5:
        sx = -520 + par * (d_end - d)
        if sx < W:
            img.paste(sk, (int(sx * SS), 0), sk)
    paste_wrap(img, mid, d * 0.3)
    paste_wrap(img, near, d * 0.75)
    c = Canvas(img)
    # track
    c.rect(0, 618, W, 650, (150, 136, 120), ol=None)
    off = d % 46
    for k in range(-1, W // 46 + 2):
        x = k * 46 - off
        c.rect(x, 626, x + 22, 636, (110, 80, 60), ol=None)
    c.line([(0, 622), (W, 622)], (90, 90, 100), 5, cap=False)
    c.rect(0, 650, W, H, (120, 172, 90), ol=None)
    rng = np.random.default_rng(1)
    for k in range(40):                                       # fast grass tufts in front
        x = (rng.uniform(0, W + 200) - d * 1.3) % (W + 200) - 100
        y = rng.uniform(664, 712)
        for j in (-1, 0, 1):
            c.line([(x, y), (x + j * 8, y - 18)], (90, 145, 70), 3, cap=False)
    # train + passengers
    bob = math.sin(t * 13) * 1.5 * (v / 900)
    wheel = d / 22
    look_out = t >= T("tr_look")
    sleepy = t < T("tr_yet")

    def cats_fn(cc):
        for who, wx in (("whiskers", -590), ("luna", -490)):
            pal = PAL[who]
            mouth = tl.mouth(who, t)
            if who == "whiskers":
                eyes = "closed" if sleepy or (T("tr_not", 1) < t < T("tr_now")) else "open"
                if look_out and t < T("tr_rome", 1):
                    eyes = "wide"
            else:
                eyes = "wide" if T("tr_view") <= t < T("tr_rome") else (
                    "happy" if T("tr_rome") <= t else "open")
            lean = -10 * ease(tl.prog("tr_look", t, 0.2, 1.0)) if who == "whiskers" else -6 * ease(
                tl.prog("tr_look", t, 0.0, 0.7))
            hy = -128 + lean
            cc.push(wx - 4, hy, 0.78)
            if eyes == "open" and D.blink(t, SEED[who]):
                eyes = "closed"
            D._head(cc, 0, 0, pal, pal["body"], pal["dark"], pal["belly"], mouth, eyes,
                    (0.2, -0.6) if look_out else (1, 0), t)
            cc.pop()
            for px in (-18, 14):
                cc.ellipse(wx + px, -110, 11, 7, pal["body"])
            if who == "luna" and coin_on_luna(tl, t):
                P.coin(cc, wx - 8 * 0.78 - 4, hy + 38 * 0.78, 5)
        if sleepy:
            D.zzz(cc, -560, -170, t)

    P.steam_train(c, 1230, 618 + bob, 1.0, t, wheel, cats_fn)
    P.smoke(c, 1230 - 320 + 240, 618 - 300, t, v / 900, n=8 if v > 50 else 4)
    return c


# --------------------------------------------------------------- streets

SW, SG = 3300, 560          # street world width, building base line
SY = 648                    # where characters stand


def nasone(c, x, y, t):
    """A 'nasone', Rome's little iron drinking fountain."""
    c.rect(x - 18, y - 96, x + 18, y, (70, 96, 84), r=6)
    c.ellipse(x, y - 96, 18, 6, (90, 116, 104))
    c.stroke([(x + 16, y - 70), (x + 34, y - 66), (x + 38, y - 56)], (70, 96, 84), 7)
    k = (t * 3) % 1.0
    c.line([(x + 38, y - 54), (x + 40, y - 6)], (170, 220, 240), 3, cap=False)
    c.ellipse(x + 40, y - 2, 10, 3, (170, 220, 240), ol=None)
    c.circle(x + 39, y - 54 + 48 * k, 2, (230, 250, 255), ol=None)


NASONE_X = 1640


def streets_bg(dusk=False):
    def make():
        if dusk:
            sky = [(0, (90, 80, 150)), (0.25, (240, 140, 110)), (1, (255, 200, 140))]
        else:
            sky = [(0, (110, 180, 240)), (0.3, (190, 225, 250)), (1, (220, 240, 250))]
        c = Canvas(D.gradient(SW * SS, H * SS, sky), size=(SW, H))
        rng = np.random.default_rng(11)
        # distant dome peeking above the roofs
        c.ellipse(2260, 150, 80, 90, (210, 200, 180))
        c.rect(2240, 40, 2280, 70, (210, 200, 180))
        c.rect(2160, 150, 2360, 260, (210, 200, 180))
        cols = [(226, 170, 90), (205, 112, 76), (236, 166, 140), (240, 206, 122), (240, 222, 182), (220, 132, 74)]
        shops = {1: ("GELATO", (240, 120, 160)), 3: ("PIZZA", (210, 50, 50)), 5: ("CAFFÈ", (60, 120, 80)),
                 8: ("PANE", (220, 150, 40))}
        x, k = -40, 0
        tops = []
        while x < SW + 40:
            w_ = rng.uniform(280, 420)
            h_ = rng.uniform(430, 540)
            top = P.building(c, x, w_, h_, SG, cols[k % len(cols)], rng, shop=shops.get(k),
                             shutters=[(80, 128, 92), (110, 140, 100), (120, 90, 70)][k % 3])
            tops.append((x, w_, top))
            x += w_
            k += 1
        # washing lines between buildings
        for (x0, w0, t0), (x1, w1, t1) in list(zip(tops, tops[1:]))[1::2]:
            y = max(t0, t1) + 130
            a, b = x0 + w0 - 80, x0 + w0 + 80
            pts = [(lerp(a, b, u), y + 26 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)]
            c.line(pts, (80, 70, 70), 2, cap=False)
            for j, u in enumerate((0.2, 0.45, 0.7)):
                px, py = lerp(a, b, u), y + 26 * math.sin(math.pi * u)
                col = [(250, 250, 250), (110, 160, 220), (240, 120, 120)][j]
                c.rect(px - 12, py, px + 12, py + 30 - 8 * j, col, w=2)
        # pavement and cobbled street
        c.rect(0, SG, SW, SG + 26, (200, 190, 176))
        P.cobbles(c, 0, SW, SG + 26, H, (168, 158, 150))
        for lx in range(500, SW, 900):                        # street lamps
            c.rect(lx - 4, SG - 300, lx + 4, SG + 10, (60, 56, 64), ol=None)
            c.line([(lx, SG - 300), (lx + 30, SG - 320)], (60, 56, 64), 5)
            c.poly([(lx + 18, SG - 320), (lx + 42, SG - 320), (lx + 38, SG - 290), (lx + 22, SG - 290)],
                   (255, 230, 150))
        for px in (260, 1180, 2500):                          # flower pots
            c.poly([(px - 26, SG + 10), (px + 26, SG + 10), (px + 18, SG - 34), (px - 18, SG - 34)],
                   (200, 100, 70))
            for dx, dy in ((-14, -50), (0, -64), (14, -50)):
                c.circle(px + dx, SG + dy, 16, (80, 150, 80))
                c.circle(px + dx, SG + dy - 6, 5, (240, 70, 80), ol=None)
        return c.img
    return cached(("streets", dusk), make)


def streets(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["streets"]
    wk = [(s0, 120), (T("st_walk", 1), 820), (T("st_wh", 1), 1240), (T("st_end", 0.15), 1240),
          (s1, 1900)]
    lk = [(s0, 260), (T("st_walk", 1), 960), (T("st_wh", 1), 1380), (T("st_end", 0.05), 1380),
          (s1, 2060)]
    wx, lx = smooth(t, wk), smooth(t, lk)
    camx = clamp((wx + lx) / 2 - W / 2 + 160, 0, SW - W)
    c = view(streets_bg(), camx)
    c.push(-camx, 0)
    nasone(c, NASONE_X, SY - 4, t)
    # the Vespa zooms through right to left
    vu = tl.prog("st_vespa", t, 0.05, 0.75)
    jump = tl.prog("st_vespa", t, 0.22, 0.5)
    if 0 < vu < 1:
        vx = lerp(camx + W + 250, camx - 300, vu)
        P.vespa(c, vx, SY + 6, 1.0, -1, t, wheel=-vx / 22)
        speed_lines(c, vx + 60, SY - 20, -1, t)
    wpose, lpose, wy, ly = "stand", "stand", SY, SY + 3
    weyes, leyes = "open", "open"
    if 0 < jump < 1:
        wpose, lpose = "leap", "leap"
        wy = SY + arc_y(jump, 190)
        ly = SY + 3 + arc_y(clamp(jump * 1.1), 210)
        weyes = leyes = "wide"
    after = T("st_vespa", 0.5) <= t < T("st_follow")
    if T("st_vespa", 0.5) <= t < T("st_nico"):
        wpose, weyes = "sit", "wide"
    if T("st_vespa", 0.1) <= t < T("st_vespa", 0.22):
        weyes = leyes = "wide"
    nico_on = t >= T("st_nico") - 0.3
    look = (1, -0.8) if nico_on and t < T("st_end") else (1, 0)
    actor(c, tl, t, "whiskers", wk, wy, pose=wpose, eyes=weyes, look=look,
          squash=1 - 0.2 * math.sin(math.pi * tl.prog("st_vespa", t, 0.5, 0.58)))
    actor(c, tl, t, "luna", lk, ly, pose=lpose, eyes="happy" if T("st_luna") <= t < T("st_luna", 1) else leyes,
          look=look)
    # Nico swoops down onto the nasone, later flies on ahead
    if nico_on:
        top = SY - 4 - 100
        kx = [(T("st_nico") - 0.3, camx + W + 80), (T("st_land", 0.8), NASONE_X), (T("st_follow", 0.85), NASONE_X),
              (s1, NASONE_X + 900)]
        ky = [(T("st_nico") - 0.3, -60), (T("st_land", 0.8), top), (T("st_follow", 0.85), top), (s1, top - 400)]
        flyer(c, tl, t, kx, ky, 1.5, face=-1, eyes="happy" if T("st_intro", 0.6) <= t < T("st_intro", 1) else "open")
    c.pop()
    if T("st_vespa", 0.12) <= t < T("st_vespa", 0.3):
        bang(c, W - 220, 200, 0.9 + 0.1 * math.sin(t * 30), "BEEP!")
    return c


# ------------------------------------------------------------- colosseum

CW, CG = 1900, 640
COL_X = 1180
DRUM = (1060, 590)          # top centre of the fallen column drum


def colosseum_bg():
    def make():
        c = Canvas(D.gradient(CW * SS, H * SS, [(0, (100, 170, 235)), (0.6, (200, 230, 250)), (1, (220, 240, 250))]),
                   size=(CW, H))
        for x, y, s in ((200, 100, 1.1), (700, 60, 0.8), (1500, 110, 1.0), (1800, 70, 0.7)):
            D.cloud(c, x, y, s)
        c.poly([(0, 520), (CW, 510), (CW, H), (0, H)], (176, 196, 130), ol=None)
        P.umbrella_pine(c, 1780, 545, 1.15, lean=-20)
        P.cypress(c, 1640, 548, 0.7)
        P.colosseum(c, COL_X, 560, 1.0)
        P.umbrella_pine(c, 330, 560, 1.2, lean=30)
        P.umbrella_pine(c, 700, 548, 0.9, lean=-10)
        P.cypress(c, 120, 560, 0.9)
        c.rect(0, 556, CW, H, (214, 196, 160), ol=None)              # travertine paving
        for y in range(572, H, 26):
            c.line([(0, y), (CW, y)], (196, 176, 140), 2, cap=False)
        rng = np.random.default_rng(2)
        for y in range(572, H, 26):
            for x in np.arange(rng.uniform(0, 80), CW, 120):
                c.line([(x, y), (x - 6, y + 26)], (196, 176, 140), 2, cap=False)
        c.rect(0, 552, CW, 562, (190, 170, 130), ol=None)
        # broken columns and a fallen drum
        for bx, h in ((660, 190), (710, 120)):
            c.rect(bx - 18, CG - 60 - h, bx + 18, CG - 60, (236, 222, 196))
            for fl in (-8, 0, 8):
                c.line([(bx + fl, CG - 56 - h), (bx + fl, CG - 64)], (210, 192, 160), 2, cap=False)
            c.rect(bx - 26, CG - 62, bx + 26, CG - 48, (220, 204, 176))
        x, y = DRUM
        c.rect(x - 60, y, x + 60, y + 58, (232, 216, 186))
        for fl in range(-50, 60, 14):
            c.line([(x + fl, y + 6), (x + fl, y + 54)], (210, 192, 160), 2, cap=False)
        c.ellipse(x, y, 60, 14, (244, 234, 212))
        return c.img
    return cached("colosseum", make)


def colosseum(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["colosseum"]
    camx = 560 * ease(tl.prog("co_reveal", t, 0.0, 0.9))
    if t >= T("co_end"):
        camx += 180 * ease(tl.prog("co_end", t))
    c = view(colosseum_bg(), camx)
    c.push(-camx, 0)
    # Luna and Whiskers
    lk = [(s0, 180), (T("co_reveal", 0.9), 900), (T("co_end", 0.1), 900), (s1, 1500)]
    wk = [(s0, 40), (T("co_reveal", 0.95), 760), (T("co_hero", 0.7), 760), (T("co_hero", 1), 960),
          (T("co_pose"), 980)]
    pu = tl.prog("co_pose", t)
    if t < T("co_pose", 0.0) or t >= s1:
        actor(c, tl, t, "whiskers", wk, CG, eyes="wide" if T("co_nico") <= t < T("co_cheese") else "open",
              look=(0.5, -1) if t < T("co_hero") else (1, 0))
    else:
        if pu < 0.18:                                                  # hop up onto the drum
            u = pu / 0.18
            x, y, pose = lerp(980, DRUM[0] - 6, ease(u)), lerp(CG, DRUM[1] + 4, u) + arc_y(u, 90), "leap"
        else:
            x, y, pose = DRUM[0] - 6, DRUM[1] + 4, "stand"
        if t >= T("co_end"):
            x = smooth(t, [(T("co_end"), DRUM[0] - 6), (T("co_end", 0.25), DRUM[0] + 60), (s1, 1600)])
            y = lerp(DRUM[1] + 4, CG, ease(tl.prog("co_end", t, 0.0, 0.25))) + arc_y(tl.prog("co_end", t, 0, 0.25), 50)
            pose = "walk" if tl.prog("co_end", t) > 0.25 else "leap"
        roar = 0.3 <= pu < 0.55
        sq = 1 + 0.12 * math.sin(math.pi * clamp((pu - 0.3) / 0.25)) if roar else 1.0
        eyes = "happy" if 0.18 <= pu < 0.3 or T("co_lunch") <= t < T("co_lunch", 1) else (
            "wide" if 0.7 <= pu < 0.95 else "open")
        D.cat(c, x, y, D.WHISKERS, 1.0, 1, pose, walk=x / 12 if pose == "walk" else 0, t=t,
              mouth=0.9 if roar else tl.mouth("whiskers", t), eyes=eyes, squash=sq, head_dy=-6 if roar else 0,
              look=(0.4, -1) if 0.7 <= pu < 1 else (1, 0))
        if roar:
            for k in range(3):
                r = 30 + 40 * ((pu - 0.3) / 0.25 + k * 0.33) % 1.0 * 1.5
                c.arc(x + 90, y - 100, r, r * 1.1, -50, 50, (255, 255, 255), 3)
        # pigeons land on the hero
        if pu >= 0.6 and t < T("co_end", 0.3):
            spots = [(x + 52, y - 166, 0.62), (x - 20, y - 76, 0.6), (x + 20, y - 80, 0.68)]
            for k, (px, py, ks) in enumerate(spots):
                u = clamp((pu - 0.6 - k * 0.06) / 0.18) if t < T("co_end") else 1.0
                leave = tl.prog("co_end", t, 0.0, 0.3)
                fx = lerp(px + 400 + k * 60, px, ease(u)) + 500 * leave * leave
                fy = lerp(py - 300, py, ease(u)) - 400 * leave
                fly = u < 1 or leave > 0
                P.pigeon(c, fx, fy, ks, -1 if k != 1 else 1, t + k, fly=fly, cap=False,
                         body=[(160, 160, 170), (140, 150, 170), (176, 170, 176)][k], seed=k * 1.7)
    actor(c, tl, t, "luna", lk, CG + 4, eyes="happy" if T("co_hero") <= t < T("co_hero", 1) or (
        T("co_pose", 0.65) <= t < T("co_end")) else "open", look=(1, -0.5) if t < T("co_hero") else (1, 0))
    # Nico perches on the tall broken column
    perch = (660, CG - 60 - 190 - 2)
    kx = [(s0, -100), (T("co_reveal", 0.8), perch[0]), (T("co_end", 0.3), perch[0]), (s1, 1700)]
    ky = [(s0, 200), (T("co_reveal", 0.8), perch[1]), (T("co_end", 0.3), perch[1]), (s1, 150)]
    flyer(c, tl, t, kx, ky, 1.3, face=1 if t < T("co_cheese") else 1)
    c.pop()
    return c


# ---------------------------------------------------------------- piazza

PG = 640                    # where cats stand in the piazza
ROSA_X, ROSA_Y = 960, 524
CRATE = (640, 760, 594)     # x0, x1, top
RAW = [(668, 590), (732, 590)]


def piazza_bg(dusk=False):
    def make():
        sky = [(0, (110, 180, 240)), (0.5, (200, 230, 250)), (1, (220, 240, 250))]
        if dusk:
            sky = [(0, (90, 80, 150)), (0.3, (240, 140, 110)), (1, (255, 200, 140))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        rng = np.random.default_rng(21)
        # back buildings and a church with a dome
        cols = [(240, 214, 160), (232, 168, 128), (246, 228, 196), (226, 182, 120)]
        x = -30
        k = 0
        while x < W + 30:
            w_ = rng.uniform(220, 300)
            P.building(c, x, w_, rng.uniform(330, 400), 470, cols[k % 4], rng,
                       shutters=[(90, 130, 100), (120, 90, 70)][k % 2])
            x += w_
            k += 1
        cx = 420
        c.ellipse(cx, 150, 90, 96, (196, 186, 170))
        c.rect(cx - 4, 30, cx + 4, 56, (180, 170, 150), ol=None)
        c.rect(cx - 14, 50, cx + 14, 64, (196, 186, 170))
        c.rect(cx - 160, 150, cx + 160, 470, (246, 236, 214))
        c.poly([(cx - 180, 160), (cx, 100), (cx + 180, 160)], (236, 224, 200))
        for px in (-130, -60, 60, 130):
            c.rect(cx + px - 12, 190, cx + px + 12, 450, (252, 246, 232), ol=(200, 190, 170), w=2)
        c.rect(cx - 36, 340, cx + 36, 470, (130, 90, 60), r=36)
        c.circle(cx, 250, 26, (120, 140, 170), w=3)
        # obelisk
        ox = 230
        c.rect(ox - 34, 520, ox + 34, 560, (220, 210, 190))
        c.poly([(ox - 18, 520), (ox + 18, 520), (ox + 12, 230), (ox - 12, 230)], (236, 222, 196))
        c.poly([(ox - 12, 230), (ox + 12, 230), (ox, 206)], (236, 222, 196))
        c.line([(ox, 206), (ox, 186)], (90, 80, 70), 3)
        c.line([(ox - 8, 194), (ox + 8, 194)], (90, 80, 70), 3)
        # paving
        c.rect(0, 470, W, 500, (206, 196, 180))
        P.cobbles(c, 0, W, 500, H, (176, 166, 156), rng_seed=9)
        # cafe table with umbrella on the left
        c.line([(90, 300), (90, 600)], (90, 80, 80), 5)
        c.poly([(-10, 330), (90, 280), (190, 330)], (60, 130, 90))
        c.poly([(40, 330), (90, 280), (140, 330)], (255, 250, 240), ol=None)
        c.ellipse(90, 540, 50, 10, (250, 250, 250))
        c.line([(90, 540), (90, 600)], (90, 80, 80), 4)
        # wood-fired oven
        c.rect(1110, 420, 1270, 600, (196, 120, 90))
        c.ellipse(1190, 420, 80, 70, (176, 96, 76))
        c.rect(1110, 420, 1270, 430, (176, 96, 76), ol=None)
        for y in range(440, 600, 22):
            for x in range(1114 + (y // 22 % 2) * 18, 1266, 36):
                c.rect(x, y, x + 32, y + 18, (206, 132, 100), ol=(160, 90, 70), w=1.5)
        c.rect(1150, 470, 1230, 540, (60, 30, 30), r=40)
        c.rect(1176, 330, 1204, 360, (120, 70, 60))
        # crate with raw pizzas, waiting for the oven
        x0, x1, top = CRATE
        c.rect(x0, top, x1, PG + 6, (196, 150, 98))
        for y in range(top + 14, PG + 6, 16):
            c.line([(x0 + 4, y), (x1 - 4, y)], (170, 125, 80), 2, cap=False)
        return c.img
    return cached(("piazza", dusk), make)


def stand(c, t, tl, front=True):
    """Rosa's pizza cart: posts, awning, sign (back) and counter (front)."""
    x0, x1 = 800, 1110
    if not front:
        for px in (x0 + 10, x1 - 10):
            c.rect(px - 5, 250, px + 5, 480, (120, 86, 60))
        n = 8
        for k in range(n):
            a = x0 - 10 + (x1 - x0 + 20) * k / n
            b = x0 - 10 + (x1 - x0 + 20) * (k + 1) / n
            c.poly([(a, 250), (b, 250), (b + 4, 290), (a + 4, 290)], (210, 50, 50) if k % 2 == 0 else (255, 250, 240),
                   ol=None)
        c.poly([(x0 - 10, 250), (x1 + 10, 250), (x1 + 14, 290), (x0 - 6, 290)], None)
        for k in range(n):
            a = x0 - 6 + (x1 - x0 + 20) * (k + 0.5) / n
            c.ellipse(a, 292, (x1 - x0) / n / 2, 8, (210, 50, 50) if k % 2 == 0 else (255, 250, 240), w=2)
        c.rect(x0 + 40, 206, x1 - 40, 246, (60, 120, 80), r=6)
        c.text((x0 + x1) / 2, 226, "PIZZA DA ROSA", 22, (255, 240, 200))
        return
    c.rect(x0, 474, x1, 610, (232, 210, 170), r=4)
    c.rect(x0 - 10, 466, x1 + 10, 482, (176, 120, 80), r=3)
    for k in range(3):
        c.rect(x0 + 20 + k * 98, 500, x0 + 88 + k * 98, 580, [(60, 130, 80), (255, 250, 240), (210, 50, 50)][k],
               w=2, r=4)
    for wx in (x0 + 50, x1 - 50):
        c.circle(wx, 620, 26, (90, 70, 60))
        c.circle(wx, 620, 10, (190, 180, 170), w=2)


def dough(c, x, y, r, t, spin=True):
    rx = r * (0.55 + 0.45 * abs(math.cos(t * 7))) if spin else r
    c.ellipse(x, y, rx, r * 0.32, P.DOUGH, w=2.5)
    c.ellipse(x, y, rx * 0.7, r * 0.2, mix(P.DOUGH, (255, 255, 255), 0.4), ol=None)


def piazza(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["piazza"]
    c = Canvas(piazza_bg().copy())
    stand(c, t, tl, front=False)
    # raw pizzas on the crate (the left one swallows the coin)
    for k, (px, py) in enumerate(RAW):
        P.pizza(c, px, py, 26, raw=True)
    # Rosa
    rosa_talk = tl.talking("rosa", t)
    toss = tl.prog("pz_toss", t)
    amazed = T("pz_toss", 0.45) <= t < T("pz_hat")
    P.rosa(c, ROSA_X, ROSA_Y, 1.0, -1, "sit", t=t, mouth=tl.mouth("rosa", t),
           eyes="wide" if amazed else ("happy" if T("pz_bravo") <= t < T("pz_bravo", 1) else "open"),
           look=(1, -1) if T("pz_narr") <= t < T("pz_toss", 0.3) else (1, 0.2))
    stand(c, t, tl, front=True)
    # the spinning dough above Rosa's paws
    hand = (ROSA_X - 30, 392)
    if t < T("pz_toss", 0.1):
        hop = abs(math.sin(t * 3.2)) * 70 if t >= T("pz_narr") else 0
        dough(c, hand[0], hand[1] - 20 - hop, 46, t)
    # Whiskers + Luna
    wk = [(s0, -150), (T("pz_arrive", 1), 420), (T("pz_toss", 0.3), 420), (T("pz_toss", 0.36), 520),
          (T("pz_toss", 0.42), 380), (T("pz_toss", 0.5), 430), (T("pz_end", 0.1), 430), (s1 + 0.3, 1450)]
    lk = [(s0, -300), (T("pz_arrive", 1), 576), (T("pz_end"), 576), (s1, 1600)]
    wx = smooth(t, wk)
    wy, wpose, weyes, sq = PG, "stand", "open", 1.0
    lu = tl.prog("pz_toss", t, 0.5, 0.64)
    if 0 < lu < 1:
        wpose, wy, weyes = "leap", PG + arc_y(lu, 150), "wide"
    if T("pz_toss", 0.64) <= t < T("pz_toss", 0.72):
        weyes = "wide"
    if T("pz_toss", 0.72) <= t:
        sq = 1 - 0.18 * math.sin(math.pi * tl.prog("pz_toss", t, 0.72, 0.8))
    if T("pz_born") <= t < T("pz_born", 1):
        weyes = "happy"
    if T("pz_hat") <= t < T("pz_hat", 1):
        weyes = "happy"
    if T("pz_toss", 0.72) <= t < T("pz_toss", 0.85):
        weyes = "closed"
    eating = T("pz_eat") <= t < T("pz_go")
    if eating:
        wpose = "sit"
    look = (0.5, -1) if T("pz_toss", 0.1) <= t < T("pz_toss", 0.72) else (1, 0)
    actor(c, tl, t, "whiskers", wk, wy, pose=wpose, eyes=weyes, look=look, squash=sq,
          mouth=0.6 + 0.3 * math.sin(t * 14) if eating and tl.mouth("whiskers", t) == 0 else tl.mouth("whiskers", t))
    # dough hat: from landing until Rosa takes it back for baking
    if T("pz_toss", 0.72) <= t < T("pz_bravo", 0.35):
        k = ease(tl.prog("pz_toss", t, 0.72, 0.8))
        P.dough_hat(c, wx, wy, 1.0, 1, wpose, t, k)
    lpose = "sit" if T("pz_arrive", 1) < t < T("pz_go") else "stand"
    laugh = T("pz_toss", 0.75) <= t < T("pz_hat", 1)
    actor(c, tl, t, "luna", lk, PG + 2, pose=lpose, eyes="happy" if laugh else "open",
          look=(0.5, -1) if T("pz_toss", 0.1) <= t < T("pz_toss", 0.72) else (1, 0),
          mouth=0.4 + 0.3 * math.sin(t * 15) if laugh and not tl.talking("luna", t) else tl.mouth("luna", t))
    # the big toss
    if T("pz_toss", 0.1) <= t < T("pz_toss", 0.72):
        u = tl.prog("pz_toss", t, 0.1, 0.72)
        land_x = smooth(T("pz_toss", 0.72), wk) + 52
        if u < 0.45:
            v = u / 0.45
            x, y = lerp(hand[0], 700, v), lerp(hand[1], -120, ease(v) ** 0.6)
        else:
            v = (u - 0.45) / 0.55
            x, y = lerp(700, land_x, v), lerp(-120, wy - 120, v * v)
        dough(c, x, y, 56, t)
    elif T("pz_toss", 0.72) <= t < T("pz_toss", 0.8):
        bang(c, wx + 120, wy - 200, 0.8, "SPLAT!", (255, 250, 230))
    # Rosa takes the dough back, then slices fly over
    if T("pz_bravo", 0.35) <= t < T("pz_bravo", 0.6):
        u = tl.prog("pz_bravo", t, 0.35, 0.6)
        dough(c, lerp(wx + 50, hand[0], u), lerp(PG - 120, hand[1], u) + arc_y(u, 120), 46, t, spin=False)
    wslice = (wx + 68, PG - 76)
    lslice = (576 + 66, PG - 74)
    if T("pz_bravo", 0.6) <= t < T("pz_eat"):
        u = ease(tl.prog("pz_bravo", t, 0.6, 1.0))
        for (sx, sy) in (wslice, lslice):
            P.slice_(c, lerp(hand[0], sx, u), lerp(hand[1], sy, u) + arc_y(u, 100), 0.8, 180 - 90 * u)
    if eating:
        u = tl.prog("pz_eat", t)
        if u < 0.45:
            P.slice_(c, wslice[0] - 34, wslice[1] - 10, 0.8, 200, bitten=u / 0.45)
        elif u < 0.6:
            uu = (u - 0.45) / 0.15
            P.slice_(c, lerp(hand[0], wslice[0] - 34, uu), lerp(hand[1], wslice[1] - 10, uu) + arc_y(uu, 80), 0.8,
                     200)
        else:
            P.slice_(c, wslice[0] - 34, wslice[1] - 10, 0.8, 200, bitten=(u - 0.6) / 0.4 * 0.8)
        P.slice_(c, lslice[0] - 34, lslice[1] - 8, 0.8, 200, bitten=u * 0.5)
    # the coin slips off Luna's collar into a raw pizza -- nobody notices
    if T("pz_eat", 0.3) <= t:
        cx0, cy0 = P.collar_point(576, PG + 2, 1.0, 1, "sit")
        u = tl.prog("pz_eat", t, 0.3, 0.42)
        tx, ty = RAW[0][0] - 6, RAW[0][1] - 2
        cx, cy = lerp(cx0, tx, u), lerp(cy0, ty, u) + arc_y(u, 40)
        if u < 1:
            P.coin(c, cx, cy, 6, math.cos(t * 12))
        else:
            c.ellipse(tx, ty, 6, 2.4, P.GOLD, w=1.5)
            g = tl.prog("pz_eat", t, 0.42, 0.62)
            if 0 < g < 1:
                P.twinkle(c, tx + 4, ty - 8, 16 * math.sin(math.pi * g))
    # Nico perched on the sign
    flyer(c, tl, t, [(s0, -80), (T("pz_arrive", 0.9), 830), (T("pz_end", 0.2), 830), (s1, 1500)],
          [(s0, 120), (T("pz_arrive", 0.9), 206), (T("pz_end", 0.2), 206), (s1, 60)], 1.2,
          eyes="happy" if laugh else "open")
    return c


# -------------------------------------------------------------- fountain

FG = 575                     # basin rim line (fountain scenes)


def trevi_bg(night=False):
    def make():
        if night:
            sky = [(0, (14, 18, 48)), (0.4, (40, 44, 96)), (1, (60, 62, 120))]
        else:
            sky = [(0, (120, 120, 190)), (0.3, (250, 170, 130)), (1, (255, 210, 150))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        s, gy = (0.78, 560) if night else (0.92, FG)
        if night:
            D.stars(c, 4, 60, W, 110)
            D.moon(c, 1150, 60, 30, sky=(20, 26, 64))
            c.tint = ((40, 50, 110), 0.3)
        P.trevi_static(c, 640, gy, s)
        c.tint = None
        c.rect(0, gy + 14, W, H, (214, 200, 176), ol=None)
        P.cobbles(c, 0, W, gy + 14, H, (200, 186, 166) if not night else (130, 124, 140), rng_seed=6)
        if night:
            # warm floodlight glow on the facade
            glow = Image.new("RGB", c.img.size, (255, 222, 160))
            mask = Image.new("L", c.img.size, 0)
            ImageDraw.Draw(mask).ellipse([(640 - 520) * SS, 60 * SS, (640 + 520) * SS, 640 * SS], fill=95)
            mask = mask.filter(ImageFilter.GaussianBlur(60 * SS))
            c.img.paste(glow, (0, 0), mask)
            for lx in (90, 1190):                                       # lanterns
                c.rect(lx - 5, 380, lx + 5, 690, (40, 40, 50), ol=None)
                c.glow(lx, 370, 60, 60, (255, 230, 150), (130, 120, 140), steps=8)
                c.poly([(lx - 18, 350), (lx + 18, 350), (lx + 14, 390), (lx - 14, 390)], (255, 230, 150))
        return c.img
    return cached(("trevi", night), make)


def fountain(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["fountain"]
    if T("fo_dash") <= t < T("fo_munch"):
        return dash(tl, t)
    if T("fo_munch") <= t < T("fo_back"):
        return munch(tl, t)
    c = Canvas(trevi_bg(False).copy())
    P.trevi_water(c, 640, FG, 0.92, t)
    c.tint = DUSK
    y = 655
    # Nico on the basin rim
    flyer(c, tl, t, [(s0, 1400), (T("fo_arrive", 0.8), 820)], [(s0, 100), (T("fo_arrive", 0.8), FG - 12)], 1.3,
          face=-1, eyes="wide" if T("fo_gone") <= t < T("fo_wait") else "open")
    # Luna
    sad = T("fo_gone", 0.5) <= t < T("fo_found")
    lk = [(s0, -200), (T("fo_arrive", 0.9), 600), (T("fo_hug"), 600), (T("fo_hug", 0.4), 520)]
    if t < T("fo_beauty"):
        leyes, llook = "open", (0.5, -1)
    elif t < T("fo_reach"):
        leyes, llook = "happy" if t < T("fo_beauty", 1) else "open", (0.5, -1)
    elif t < T("fo_gone"):
        leyes, llook = "open", (-0.3, 1)
    elif t < T("fo_gone", 0.5):
        leyes, llook = "wide", (0, 0.5)
    elif t < T("fo_found"):
        leyes, llook = ("closed" if T("fo_sad") <= t < T("fo_sad", 1) else "open"), (-1, 0.6)
    else:
        leyes, llook = ("happy" if t >= T("fo_purpose", 0.3) else "wide"), (-1, 0)
    lpose = "sit" if T("fo_beauty") <= t < T("fo_hug") else "stand"
    lface = -1 if t >= T("fo_sad") else 1
    lx = actor(c, tl, t, "luna", lk, y + 2, pose=lpose, face=lface, eyes=leyes, look=llook,
               head_dy=8 if sad else 0)
    if T("fo_reach", 0.5) <= t < T("fo_gone", 1):                    # "!" -- the coin is gone
        k = ease(tl.prog("fo_reach", t, 0.5, 0.7))
        c.text(lx + 30, y - 210, "!", 40 + 20 * k, (255, 240, 120), stroke=3)
    if T("fo_sad") <= t < T("fo_wait", 1):                             # a tear
        u = ((t - T("fo_sad")) * 0.8) % 1.0
        ex = lx - 18 - 22
        c.ellipse(ex, y - 100 - 4 + 8 + 50 * u, 4, 6, (150, 200, 255), w=1.5)
    # Whiskers
    if t < T("fo_back"):
        wk = [(s0, -360), (T("fo_arrive", 0.95), 420), (T("fo_run"), 420), (T("fo_run", 0.35), -300)]
        run = t >= T("fo_run")
        determined = T("fo_think", 0.6) <= t
        wpose = "sit" if T("fo_beauty") <= t < T("fo_think", 0.6) else "stand"
        weyes = "wide" if T("fo_gone") <= t < T("fo_think") else "open"
        if t < T("fo_run", 0.35):
            wx = actor(c, tl, t, "whiskers", wk, y, pose=wpose, eyes=weyes,
                       look=(1, -0.2) if T("fo_gone") <= t else (0.5, -1), head_dy=-4 if determined else 0)
            if run:
                speed_lines(c, wx, y, -1, t)
                dust(c, wx + 60, y, t, T("fo_run", 0.05))
        else:
            dust(c, -40, y, t, T("fo_run", 0.3))
    else:
        bu = tl.prog("fo_back", t)
        wx = smooth(t, [(T("fo_back"), -150), (T("fo_back", 0.7), 420)])
        moving = bu < 0.7
        wob = math.sin(t * 9) * 4 if moving else 0
        pose = "stand" if moving else "sit"
        if moving:
            pose = "walk"
        sq = 0.86 + 0.03 * math.sin(t * 6) if t < T("fo_purpose", 1) else 1.0
        weyes = "closed" if bu < 0.95 else ("happy" if T("fo_purpose") <= t else "open")
        D.cat(c, wx, y + wob * 0, D.WHISKERS, 1.0, 1, pose, walk=wx / 12 if moving else 0, t=t,
              mouth=tl.mouth("whiskers", t) if t >= T("fo_found") else 0.25, eyes=weyes, squash=sq, seed=0)
        hx, hy = P.head_pos(pose)
        if t < T("fo_found", 0.05):                                    # coin in his mouth
            P.coin(c, wx + (hx + 17) * 1.0, y + (hy + 18) * sq, 9)
        else:
            u = ease(tl.prog("fo_found", t, 0.05, 0.25))
            cx, cy = wx + 75, lerp(y + hy + 18, y - 6, u)
            if t < T("fo_hug"):
                P.coin(c, cx, cy, 8)
                if T("fo_found", 0.25) <= t < T("fo_found", 0.6):
                    P.twinkle(c, cx + 6, cy - 8, 16 * math.sin(math.pi * tl.prog("fo_found", t, 0.25, 0.6)))
        if moving:
            for k in range(3):                                         # panting puffs
                u = ((t * 1.4) + k / 3) % 1.0
                c.circle(wx + 90 + 30 * u, y - 110 - 20 * u, 6 + 8 * u, (255, 255, 255), ol=None)
    if t >= T("fo_hug"):
        hearts(c, 470, y - 170, t, T("fo_hug", 0.3))
    c.tint = None
    return c


def dash(tl, t):
    """Whiskers races back across Rome at sunset -- and hops over the Vespa."""
    T = tl.t
    u = tl.prog("fo_dash", t)
    wx = lerp(2600, 300, u)
    camx = clamp(wx - W / 2 - 100, 0, SW - W)
    c = view(streets_bg(True), camx)
    c.push(-camx, 0)
    vu = tl.prog("fo_dash", t, 0.05, 0.6)
    vx = lerp(camx - 300, camx + W + 300, vu)
    jump = tl.prog("fo_dash", t, 0.22, 0.42)
    if 0 < vu < 1:
        P.vespa(c, vx, SY + 6, 1.0, 1, t, wheel=vx / 22)
    c.tint = DUSK
    if 0 < jump < 1:
        D.cat(c, wx, SY + arc_y(jump, 200), D.WHISKERS, 1.0, -1, "leap", t=t, eyes="wide", mouth=0.5)
    else:
        D.cat(c, wx, SY, D.WHISKERS, 1.0, -1, "walk", walk=t * 22, t=t, eyes="open", head_dy=6)
    speed_lines(c, wx, SY, -1, t)
    c.tint = None
    c.pop()
    return c


def munch(tl, t):
    """Back at Rosa's: Whiskers eats the whole pizza at top speed and finds the coin."""
    T = tl.t
    u = tl.prog("fo_munch", t)
    c = Canvas(piazza_bg(True).copy())
    stand(c, t, tl, front=False)
    P.rosa(c, ROSA_X, ROSA_Y, 1.0, -1, "sit", t=t, eyes="wide", mouth=0.5 if u > 0.3 else 0.0)
    stand(c, t, tl, front=True)
    # baked pizza on the crate, vanishing bite by bite
    eaten = clamp((u - 0.1) / 0.6)
    P.pizza(c, 700, 590, 46, eaten=eaten)
    if u < 0.7:
        rng = np.random.default_rng(int(t * 12))
        for k in range(6):
            c.circle(640 + rng.uniform(-40, 60), 520 + rng.uniform(-40, 30), rng.uniform(3, 6), P.CRUST, ol=None)
    c.tint = DUSK
    shake = math.sin(t * 40) * 4 if 0.1 < u < 0.7 else 0
    found = u >= 0.78
    D.cat(c, 560 + shake, PG, D.WHISKERS, 1.0, 1, "stand" if not found else "sit", t=t,
          mouth=0.7 + 0.3 * math.sin(t * 30) if 0.1 < u < 0.7 else (0.4 if found else 0.0),
          eyes="closed" if 0.1 < u < 0.7 else ("happy" if found else "open"),
          squash=lerp(1.0, 0.86, clamp((u - 0.1) / 0.6)))
    c.tint = None
    if found:
        k = ease(clamp((u - 0.78) / 0.1))
        cx, cy = 560 + 40, PG - 160 - 30 * k
        P.coin(c, cx, cy, 10, math.cos(t * 5))
        P.twinkle(c, cx + 10, cy - 10, 20 * k)
    if 0.1 < u < 0.7:
        bang(c, 700, 420, 0.75 + 0.05 * math.sin(t * 20), "NOM!", (255, 250, 230))
    return c


# ------------------------------------------------------------------ wish

def wish(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["wish"]
    c = Canvas(trevi_bg(True).copy())
    P.trevi_water(c, 640, 560, 0.78, t, night=0.15)
    y = 662
    lx, wx = 690, 500
    tu = tl.prog("wi_toss", t)
    # coin over the shoulder into the pool
    if T("wi_toss", 0.15) <= t < T("wi_toss", 0.62):
        u = tl.prog("wi_toss", t, 0.15, 0.62)
        x0, y0 = P.collar_point(lx, y, 1.0, -1, "stand")
        x1, y1 = 760, 530
        cx, cy = lerp(x0, x1, u), lerp(y0, y1, u) + arc_y(u, 360)
        for k in range(6):                                          # sparkle trail
            uu = max(0.0, u - k * 0.035)
            tx, ty = lerp(x0, x1, uu), lerp(y0, y1, uu) + arc_y(uu, 360)
            P.twinkle(c, tx, ty, 9 * (1 - k / 6), mix((255, 250, 200), (255, 200, 120), k / 6))
        P.coin(c, cx, cy, 9, math.cos(t * 14))
    if T("wi_toss", 0.62) <= t < T("wi_ask", 0.5):                   # rings in the pool + twinkles
        u = (t - T("wi_toss", 0.62))
        for k in range(3):
            r = 10 + 90 * ((u * 0.6 + k * 0.3) % 1.0)
            c.ellipse(760, 532, r, r * 0.18, None, ol=(220, 255, 255), w=2)
        for k in range(5):
            a = k * 1.3
            P.twinkle(c, 760 + math.cos(a) * 60 * min(1, u), 500 - math.sin(a) * 40 * min(1, u) - 30 * u,
                      12 * max(0.0, 1 - u / 2.5))
    c.tint = NIGHT
    # Nico on the rim
    flyer(c, tl, t, [(s0, 900), (T("wi_bye", 0.5), 900), (s1, 1500)], [(s0, 560 - 12), (T("wi_bye", 0.5), 548),
                                                                        (s1, -100)], 1.2, face=-1,
          eyes="happy" if t >= T("wi_same") else "open")
    # Luna: turns her back to the fountain and tosses
    lface = 1 if t < T("wi_how", 0.6) else -1
    if T("wi_ask") <= t:
        lface = -1
    lpose = "stand" if T("wi_toss") <= t < T("wi_toss", 0.4) else "sit"
    if T("wi_toss") <= t < T("wi_toss", 0.15):
        lpose = "crouch"
    if t < T("wi_toss"):
        lface = -1
    leyes = "closed" if T("wi_toss", 0.15) <= t < T("wi_toss", 0.6) else (
        "happy" if t >= T("wi_same") else "open")
    cat(c, tl, t, "luna", lx, y + 2, lface, lpose, eyes=leyes,
        look=(0.5, -1) if T("wi_toss", 0.6) <= t < T("wi_ask") else (1, 0),
        head_dy=-6 if T("wi_toss", 0.15) <= t < T("wi_toss", 0.3) else 0)
    if t < T("wi_toss", 0.15):
        P.collar_coin(c, lx, y + 2, 1.0, lface, lpose)
    # Whiskers
    weyes = "closed" if T("wi_nap") <= t < T("wi_beat", 0.6) else (
        "happy" if t >= T("wi_same") else "open")
    cat(c, tl, t, "whiskers", wx, y, 1, "sit", eyes=weyes,
        look=(0.8, -1) if T("wi_toss", 0.2) <= t < T("wi_ask") else (1, 0))
    if T("wi_nap") <= t < T("wi_beat", 0.6):
        D.zzz(c, wx + 40, y - 170, t)
    if t >= T("wi_same"):
        hearts(c, 570, y - 190, t, T("wi_same", 0.2), n=3)
    c.tint = None
    return c


# ------------------------------------------------------------------ home

def hills_night():
    def make():
        sky = D.gradient(W * SS, H * SS, [(0, (14, 18, 48)), (0.56, (40, 44, 96)), (0.8, (96, 78, 130)),
                                          (1, (96, 78, 130))])
        c = Canvas(sky)
        D.stars(c, 3, 140, W, 450)
        D.moon(c, 300, 140, 70, sky=(20, 26, 64))
        c.poly([(0, 470), (250, 430), (600, 480), (900, 440), (W, 480), (W, H), (0, H)], (38, 60, 78), ol=None)
        c.poly([(0, 560), (W, 520), (W, H), (0, H)], (30, 50, 60), ol=None)
        c.rect(0, 586, W, 596, (70, 66, 80), ol=None)
        c.rect(1040, 470, 1160, 560, (60, 60, 90))
        c.poly([(1026, 474), (1100, 420), (1174, 474)], (80, 50, 70))
        c.rect(1080, 500, 1120, 530, (255, 220, 120), w=2)
        return c.img
    return cached("hills", make)


def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    if t < T("h_arrive"):
        c = Canvas(hills_night().copy())
        u = tl.prog("h_narr", t, 0.0, 1.0)
        tx = lerp(-200, 1000, ease(u))
        c.tint = ((20, 26, 64), 0.45)
        P.steam_train(c, tx, 590, 0.4, t, tx / 9, win=(255, 220, 130))
        P.smoke(c, tx + 0.4 * (-320 + 240), 590 - 0.4 * 300, t, 0.5, n=6, col=(150, 150, 180))
        c.tint = None
        return c
    if t < T("h_sill"):
        c = Canvas(room(True).copy())
        bowl(c, 1160, 610)
        c.tint = ((30, 36, 90), 0.2)
        # Pip waiting on the rug
        pip_hop = abs(math.sin(t * 8)) * 12 if T("h_pip") <= t < T("h_pip", 1) or T("h_best") <= t < T(
            "h_best", 1) + 0.6 else 0
        D.mouse(c, 700, 622, 1.4, -1, t, mouth=tl.mouth("pip", t), hop=pip_hop,
                eyes="happy" if t >= T("h_best") or T("h_pip") <= t < T("h_pip", 1) else "open")
        lk = [(T("h_arrive"), -160), (T("h_arrive", 0.9), 300)]
        wk = [(T("h_arrive"), -360), (T("h_arrive", 1), 470)]
        actor(c, tl, t, "luna", lk, 614, eyes="happy" if T("h_brought") <= t < T("h_brought", 1) else "open")
        wx = actor(c, tl, t, "whiskers", wk, 612, eyes="happy" if t >= T("h_slice") else "open",
                   head_dy=8 if t < T("h_arrive", 1) else 0)
        # the pizza box Whiskers pushes in with his nose
        bx = wx + 110
        c.tint = None
        c.rect(bx - 50, 600, bx + 50, 626, (250, 246, 236), w=2.5)
        lid = ease(tl.prog("h_gift", t, 0.2, 0.7))
        if lid > 0:
            P.pizza(c, bx, 600, 44, eaten=0.5)
            c.poly([(bx - 50, 600), (bx + 50, 600), (bx + 50 - 20 * lid, 600 - 70 * lid),
                    (bx - 50 + 20 * lid, 600 - 70 * lid)], (250, 246, 236), w=2.5)
            c.text(bx, 600 - 36 * lid, "PIZZA", 14 + 4 * lid, (210, 50, 50))
        else:
            c.rect(bx - 50, 592, bx + 50, 602, (250, 246, 236), w=2.5)
            c.text(bx, 614, "ROMA", 14, (210, 50, 50))
        return c
    # close-up on the windowsill, like the end of Film 1
    c = Canvas(room(True).copy())
    card_at(c, 1050, 330, 0.16, 1.0, 1.0, t)                              # the postcard leans on the window
    c.tint = ((30, 36, 90), 0.25)
    D.cat(c, 870, 372, D.LUNA, 0.8, -1, "sleep", t=t + 1, seed=1.3)
    D.cat(c, 960, 372, D.WHISKERS, 0.8, 1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
    D.mouse(c, 918, 336, 1.0, 1, t, eyes="closed")
    c.tint = None
    D.zzz(c, 1000, 300, t)
    x0, y0 = 610, 110
    c = Canvas(c.img.crop((x0 * SS, y0 * SS, (x0 + W // 2) * SS, (y0 + H // 2) * SS)).resize((W * SS, H * SS)))
    k = ease(tl.prog("h_end", t, 0.25, 0.55))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "postcard": postcard, "train": train, "streets": streets,
               "colosseum": colosseum, "piazza": piazza, "fountain": fountain, "wish": wish, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["fo_dash", "fo_munch", "fo_back", "h_arrive", "h_sill"]
