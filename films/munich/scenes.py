"""Scenes of "Whiskers and the Swan Castle". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.munich import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "resi": 4.7, "ludwig": 8.0}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


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


def speed(t, keys):
    return (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


# ------------------------------------------------------------ characters

STAMPED = [None]      # set per frame: whether Whiskers wears the postage stamp


def head_point(pose, head_dy=0.0, walk=0.0):
    """Local position of the forehead and the mouth of a cat in a pose (facing right, s=1)."""
    if pose == "sit":
        hx, hy = 18, -106 + head_dy
    elif pose == "sleep":
        hx, hy = 46, -40
    elif pose == "crouch":
        hx, hy = 52, -40 - 38 + 14 + head_dy
    elif pose == "leap":
        hx, hy = 58, -74
    else:
        bob = math.sin(walk * 2) * 2 if walk else 0
        hx, hy = 52, -86 + bob + head_dy
    return (hx + 6, hy - 20), (hx + 17, hy + 17)


def book_slab(c, x, y, s=1.0, ang=0.0, wet=0.0):
    """The storybook seen edge-on (lying flat), centred at x, y."""
    cover = mix(P.BOOK_BLUE, (40, 70, 110), wet * 0.4)
    c.push(x, y, s)
    c.poly(P.rot([(-34, -8), (34, -8), (34, 8), (-34, 8)], ang), cover, w=2.5)
    c.poly(P.rot([(-30, -3), (34, -3), (34, 4), (-30, 4)], ang), P.PAPER, ol=None)
    c.poly(P.rot([(-34, -8), (-28, -8), (-28, 8), (-34, 8)], ang), P.GOLD, ol=None)
    c.pop()


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, beard=0.0, carry=False, mouthbook=False,
        headbook=False, **kw):
    """A cat. Whiskers wears his postage stamp (after Pip's mistake), maybe a cream beard or the book."""
    mouth = kw.pop("mouth", tl.mouth(who, t))
    if mouthbook:
        mouth = 0.0
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    fore, mpt = head_point(pose, kw.get("head_dy", 0.0), walk)
    if carry and pose in ("stand", "walk"):
        book_slab(c, x - face * 6 * s, y - 86 * s, 0.85 * s, wet=kw.get("wet", 0.0))
    if who == "whiskers" and STAMPED[0]:
        P.stamp_mark(c, x + face * fore[0] * s, y + fore[1] * s, 0.55 * s, ang=0.25 * face)
    if who == "whiskers" and beard > 0 and pose == "sit":
        P.cream_beard(c, x, y + kw.get("head_dy", 0.0) * s, s, face, beard)
    if headbook:
        book_slab(c, x + face * fore[0] * s, y + (fore[1] - 4) * s, 1.3 * s, ang=0.1 * math.sin(t * 7))
    if mouthbook:
        book_slab(c, x + face * (mpt[0] + 6) * s, y + (mpt[1] + 4) * s, 0.55 * s, ang=0.5 * face,
                  wet=kw.get("wet", 0.0))


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    x = smooth(t, keys)
    v = speed(t, keys)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop0 = kw.pop("hop", 0.0)
        hop = abs(math.sin(x / 9)) * 5 if moving else hop0
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "resi":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop0 = kw.pop("hop", 0.0)
        hop = abs(math.sin(x / (14 * s))) * 10 * s if moving else hop0
        P.resi(c, x, y, s, face, t, mouth=mouth, walk=x / (8 * s) if moving else 0.0, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def ludwig(c, tl, t, x, y, s=1.0, face=-1, swim=False, **kw):
    mouth = kw.pop("mouth", tl.mouth("ludwig", t))
    wing = kw.pop("wing", 0.25 * mouth + 0.1 * (mouth > 0.1) * math.sin(t * 3))
    P.swan(c, x, y, s, face, t, mouth=mouth, swim=swim, crown=True, specs=True, wing=wing, seed=SEED["ludwig"], **kw)


def resi(c, tl, t, x, y, s=0.8, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("resi", t))
    P.resi(c, x, y, s, face, t, mouth=mouth, **kw)


def thought_bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 9), (0.65, 14)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def jump_y(u, h):
    """Parabolic hop offset for progress u in [0, 1]."""
    u = clamp(u)
    return -4 * h * u * (1 - u)


# ================================================================== title

def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (54, 56, 122)), (0.3, (146, 104, 168)), (0.55, (246, 160, 140)),
                                               (0.7, (255, 206, 156)), (1, (255, 206, 156))]))
        D.stars(c, 4, 40, W, 150, col=(255, 240, 230))
        c.glow(330, 470, 420, 240, (255, 236, 190), (246, 166, 146), steps=12)
        far = dict(rock=(150, 112, 160), snow=(255, 230, 236), shade=(226, 190, 216), ol=(110, 80, 120))
        P.alp(c, 120, 520, 520, 300, seed=1, **far)
        P.alp(c, 560, 520, 560, 250, seed=2, **far)
        P.alp(c, 1180, 520, 620, 330, seed=3, **far)
        # forested hills
        P.hill(c, [520, 488, 500, 470, 492, 476, 506], 0, W, (84, 86, 118))
        rng = np.random.default_rng(4)
        for x in np.linspace(0, W, 46):
            P.fir_flat(c, x + rng.uniform(-10, 10), 520 + rng.uniform(-10, 14), rng.uniform(0.22, 0.32), (70, 72, 104))
        # the castle on its crag
        P.castle_cliff(c, 930, 470, 0.46, col=(150, 126, 146), dark=(112, 92, 118), seed=5)
        P.neuschwanstein(c, 930, 472, 0.55, lit=0.75, night=0.2, ol=(84, 64, 96))
        for x, y, s in ((780, 560, 0.34), (820, 600, 0.4), (1080, 570, 0.36), (1110, 610, 0.42), (740, 620, 0.42)):
            P.fir_flat(c, x, y, s, (60, 62, 92))
        # lake
        lake = D.gradient(W * SS, 110 * SS, [(0, (176, 132, 170)), (1, (96, 84, 140))])
        c.img.paste(lake, (0, 610 * SS))
        for k in range(10):
            y = 620 + k * 9
            c.line([(260 - 60 + k * 6, y), (400 - k * 6, y)], (255, 220, 180), 2)
        c.line([(0, 610), (W, 610)], (110, 80, 120), 2)
        # foreground rock for the cats
        c.poly([(0, H), (0, 600), (90, 584), (200, 588), (330, 604), (420, 650), (450, H)], (90, 70, 96), w=2.5)
        c.poly([(0, 604), (90, 588), (200, 592), (300, 604), (200, 600), (90, 598)], (120, 96, 120), ol=None)
        P.fir_flat(c, 40, 610, 0.9, (50, 48, 74))
        P.fir_flat(c, 1240, 720, 1.0, (50, 48, 74))
        P.fir_flat(c, 1170, 730, 0.75, (56, 54, 80))
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    for k, (x0, y0, sp) in enumerate(((560, 650, 9.0), (700, 676, -7.0))):
        x = x0 + sp * t
        P.ripple(c, x, y0 + 2, t, 50, (230, 190, 210), seed=k * 0.4)
        P.swan(c, x, y0, 0.42, 1 if sp > 0 else -1, t, swim=True, seed=k * 2.0, tint=((240, 170, 170), 0.18))
    c.tint = ((90, 60, 120), 0.25)
    kat(c, tl, t, "whiskers", 190, 594, 0.62, 1, "sit", look=(1, -0.5))
    kat(c, tl, t, "luna", 262, 598, 0.6, 1, "sit", look=(1, -0.5), tail=math.sin(t * 1.5))
    c.tint = None
    # twinkling window lights
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(W / 2, 80 - 30 * (1 - k), "Whiskers and the", 44, mix((60, 60, 130), (255, 246, 236), k),
           stroke=3 * k, stroke_fill=(70, 50, 100))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 156, "SWAN CASTLE", 28 + 52 * k2, mix((60, 60, 130), (255, 255, 255), k2), stroke=5 * k2,
           stroke_fill=(70, 50, 110))
    return c


# ================================================================== attic

def room_bg():
    def make():
        wall, floor = (232, 210, 176), (180, 124, 84)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, 520, mix(wall, (255, 255, 255), 0.25), ol=None)
        c.rect(0, 520, W, H, floor, ol=None)
        for y in range(540, H, 36):
            c.line([(0, y), (W, y)], mix(floor, (0, 0, 0), 0.12), 2, cap=False)
        c.rect(0, 506, W, 524, mix(wall, (0, 0, 0), 0.25), ol=None)
        # rainy window
        win = Canvas(D.gradient(320 * SS, 260 * SS, [(0, (120, 132, 150)), (1, (170, 178, 190))]), size=(320, 260))
        win.poly([(0, 190), (90, 160), (200, 182), (320, 170), (320, 260), (0, 260)], (110, 120, 120), ol=None)
        win.rect(180, 110, 300, 210, (150, 110, 100), ol=None)
        win.poly([(170, 114), (240, 70), (310, 114)], (110, 80, 80), ol=None)
        D.tree(win, 80, 236, 0.85, leaf=(200, 120, 60))
        for dx, dy in ((70, 40), (180, 30), (250, 60), (120, 20)):
            D.cloud(win, dx, dy, 0.6, (150, 158, 172))
        c.img.paste(win.img, (760 * SS, 110 * SS))
        c.rect(756, 106, 1084, 374, None, w=8)
        c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
        c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
        c.rect(740, 370, 1100, 392, (255, 250, 240), r=4)
        # rug, bookshelf, lamp
        c.ellipse(520, 612, 190, 40, (130, 70, 90))
        c.ellipse(520, 612, 150, 28, (170, 100, 120), ol=None)
        c.rect(40, 250, 230, 520, (140, 90, 56), w=3)
        for k, yy in enumerate((316, 386, 456)):
            c.rect(52, yy - 58, 218, yy, (110, 70, 44), ol=None)
            x = 58
            rng = np.random.default_rng(k)
            while x < 200:
                bw = rng.uniform(10, 18)
                bh = rng.uniform(36, 54)
                col = ((180, 60, 60), (60, 110, 170), (90, 150, 90), (220, 170, 70), (150, 90, 160))[rng.integers(5)]
                c.rect(x, yy - bh, x + bw, yy, col, w=1.5)
                x += bw + 2
        c.rect(30, 240, 240, 252, (120, 76, 48), w=2)
        c.rect(30, 456, 240, 470, (120, 76, 48), w=2)
        c.rect(40, 470, 230, 520, (140, 90, 56), w=3)
        # a framed picture of the pond (Film 1)
        c.rect(400, 150, 560, 270, (150, 100, 60), w=3)
        pic = Canvas(D.gradient(140 * SS, 100 * SS, [(0, (30, 36, 80)), (1, (70, 70, 130))]), size=(140, 100))
        D.moon(pic, 100, 30, 14, sky=(40, 44, 96))
        pic.ellipse(70, 86, 70, 14, (40, 60, 110), ol=None)
        pic.ellipse(70, 86, 20, 4, (240, 236, 200), ol=None)
        c.img.paste(pic.img, (410 * SS, 160 * SS))
        # attic hatch with a ladder, top left
        c.rect(270, 0, 380, 30, (90, 62, 40), w=3)
        for x in (284, 366):
            c.line([(x, 30), (x - 10, 520)], (150, 104, 66), 8)
        for y in range(80, 520, 64):
            c.line([(284 - 10 * y / 520, y), (366 - 10 * y / 520, y)], (150, 104, 66), 6)
        return c.img
    return cached("room", make)


def rain(c, t, region=(760, 110, 1080, 370), n=36):
    x0, y0, x1, y1 = region
    rng = np.random.default_rng(3)
    for k in range(n):
        u = (t * rng.uniform(1.4, 2.0) + rng.uniform()) % 1.0
        x = x0 + rng.uniform(0, x1 - x0)
        y = y0 + u * (y1 - y0)
        c.line([(x, y), (x - 3, min(y1, y + 18))], (210, 220, 236), 1.5, cap=False)


def book_insert(tl, t, c, k, torn=False, stamp_pulse=0.0):
    """The big open storybook, scaled by k, centred above the room."""
    if k <= 0.01:
        return
    def make(torn_):
        bc = Canvas(bg=(0, 0, 0), size=(640, 380))
        bc.img = Image.new("RGB", (640 * SS, 380 * SS), (0, 0, 0))
        bc.d = ImageDraw.Draw(bc.img)
        x, y = 320, 190
        P.book_open(bc, x, y, 600, 340, torn=torn_)
        if not torn_:
            pic = P.castle_painting(250, 190)
            bc.img.paste(pic, (45 * SS, 40 * SS))
            bc.rect(45, 40, 295, 230, None, w=2.5)
            bc.text(170, 262, "The Swan Castle", 22, (60, 60, 110))
            for kk in range(4):
                bc.line([(66, 292 + kk * 14), (274 - 30 * (kk == 3), 292 + kk * 14)], (170, 160, 150), 2)
            for kk in range(7):
                bc.line([(346, 52 + kk * 16), (594 - 40 * (kk == 6), 52 + kk * 16)], (170, 160, 150), 2)
        else:
            for kk in range(14):
                bc.line([(46, 48 + kk * 18), (294 - 60 * (kk == 13), 48 + kk * 18)], (170, 160, 150), 2)
            bc.text(170, 330, "...and then?", 16, (120, 110, 130))
        return bc.img
    img = cached(("insert", torn), lambda: make(torn))
    iw, ih = img.size
    sc = k
    im = img.resize((max(2, int(iw * sc)), max(2, int(ih * sc))))
    mask = cached(("insert_mask", torn), lambda: img.convert("L").point(lambda v: 255 if v > 0 else 0))
    mk = mask.resize(im.size)
    cx, cy = 640, 236
    c.img.paste(im, (int((cx - iw / SS * sc / 2) * SS), int((cy - ih / SS * sc / 2) * SS)), mk)
    if not torn and k > 0.6:
        # library stamp on the right page
        sp = 1 + 0.15 * stamp_pulse
        c.push(cx + 150 * sc, cy + 70 * sc, sc * sp)
        pts = P.rot([(-120, -46), (120, -46), (120, 46), (-120, 46)], -0.12)
        c.poly(pts, None, ol=(200, 50, 60), w=3)
        for j, (txt, sz) in enumerate((("NEUSCHWANSTEIN", 17), ("CASTLE LIBRARY", 17), ("RETURN BY 1886", 15))):
            dx, dy = P.rot([(0, -26 + j * 26)], -0.12)[0]
            c.text(dx, dy, txt, sz, (200, 50, 60))
        c.pop()


def attic(tl, t):
    T = tl.t
    STAMPED[0] = False
    c = Canvas(room_bg().copy())
    rain(c, t)
    c.rect(756, 106, 1084, 374, None, w=8)
    wy = 615
    # Whiskers: asleep on the rug, mumbles, wakes for pretzels, dashes off for the box
    if t < T("a_ears"):
        talk = any(T(i) - 0.2 <= t < T(i, 1) + 0.2 for i in ("a_ancient", "a_no"))
        kat(c, tl, t, "whiskers", 590, wy, 1.0, 1, "sit" if talk else "sleep", eyes="closed",
            head_dy=8 if talk else 0)
        if not talk:
            D.zzz(c, 650, 540, t)
    elif t < T("a_end"):
        startle = clamp((t - T("a_ears")) / 0.3)
        excited = t >= T("a_box")
        hop = abs(math.sin((t - T("a_box")) * 7)) * 22 if excited and t > T("a_box", 0.6) else 0
        kat(c, tl, t, "whiskers", 590, wy - hop, 1.0, 1, "stand" if excited else "sit",
            eyes="happy" if excited and tl.mouth("whiskers", t) < 0.1 else "wide", look=(0, -1),
            head_dy=-8 * (1 - startle))
    else:
        actor(c, tl, t, "whiskers", [(T("a_end"), 590), (T("a_end", 0.95), 1450)], wy, eyes="happy")
    # Luna by the window
    leyes = "happy" if T("a_book") <= t < T("a_book", 1) or t >= T("a_end") else "open"
    kat(c, tl, t, "luna", 870, 612, 1.0, -1, "sit", eyes=leyes, look=(0, 0.3), tail=math.sin(t * 1.5))
    # Pip climbs down the ladder and pushes the book across the floor
    if t >= T("a_pip") - 0.2:
        down = ease(tl.prog("a_pip", t, 0.0, 0.35))
        if down < 1:
            py = lerp(60, 600, down)
            D.mouse(c, 330, py, 1.3, 1, t, eyes="open")
            book_slab(c, 330, py - 60, 0.8)
        else:
            keys = [(T("a_pip", 0.4), 300), (T("a_pip", 1.0), 380)]
            px = actor(c, tl, t, "pip", keys, 628, 1.3, eyes="happy" if T("a_found") <= t < T("a_found", 1) else "open",
                       proud=T("a_found") <= t < T("a_found", 1))
            if t < T("a_end"):
                book_slab(c, px + 66, 622, 1.1)
    # the storybook close-up
    k = min(ease((t - T("a_book")) / 0.4), 1 - ease((t - T("a_page", 1)) / 0.4))
    torn = t >= T("a_page") - 0.15
    pulse = math.sin(clamp(tl.prog("a_stamp", t, 0.0, 0.3)) * math.pi)
    book_insert(tl, t, c, 0.92 * k, torn=torn, stamp_pulse=pulse)
    # Whiskers dreams of pretzels and strudel
    k = min(ease((t - T("a_pretzel", 0.4)) / 0.4), 1 - ease((t - T("a_box", 0.3)) / 0.3))
    if k > 0.02:
        thought_bubble(c, 600, 300, 150, 92, k, tail=(640, 480))
        if k > 0.6:
            P.pretzel(c, 560, 300, 50 * k, 0.1 * math.sin(t * 2))
            P.strudel(c, 660, 340, 0.6 * k, cream=0.6)
    return finish(c, tl, t, 0.35)


# ================================================================== post

def street_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (70, 70, 140)), (0.45, (210, 130, 140)), (0.62, (255, 190, 140)),
                                               (1, (255, 190, 140))]))
        # neighbour houses far
        for x, w, h, col in ((-20, 240, 260, (150, 110, 130)), (900, 200, 300, (140, 100, 130)),
                             (1080, 240, 240, (160, 116, 136))):
            c.rect(x, 560 - h, x + w, 560, col, ol=None)
            c.poly([(x - 10, 560 - h), (x + w / 2, 500 - h), (x + w + 10, 560 - h)], mix(col, (60, 40, 60), 0.3),
                   ol=None)
            for wx in range(int(x) + 30, int(x + w) - 30, 60):
                c.rect(wx, 560 - h + 50, wx + 26, 560 - h + 86, (255, 214, 140), ol=None)
        # the cats' house
        c.rect(240, 110, 860, 600, (236, 214, 178), w=3)
        c.poly([(220, 116), (550, -40), (880, 116)], (170, 80, 64), w=3)
        c.rect(420, 170, 640, 360, (120, 150, 200), w=4)                # the window
        c.rect(424, 174, 636, 356, (255, 220, 150), ol=None)
        c.line([(530, 174), (530, 356)], (240, 240, 240), 5, cap=False)
        c.line([(424, 265), (636, 265)], (240, 240, 240), 5, cap=False)
        c.rect(404, 356, 656, 374, (255, 250, 240), w=2.5, r=3)          # the windowsill
        c.rect(300, 420, 380, 600, (120, 76, 46), w=3)                   # door
        c.circle(366, 512, 4, P.GOLD, ol=None)
        c.rect(290, 596, 400, 612, (170, 160, 150), w=2)                 # step
        for wx in (720, 800):
            c.rect(wx - 26, 180, wx + 26, 250, (255, 214, 140), w=3)
        # street
        c.rect(0, 600, W, H, (110, 104, 120), ol=None)
        c.rect(0, 600, W, 618, (170, 160, 160), w=2)
        for x in range(40, W, 160):
            c.rect(x, 668, x + 70, 676, (230, 220, 180), ol=None)
        # lamp post
        c.rect(1000, 330, 1010, 610, (60, 60, 70), w=2)
        c.glow(1005, 330, 60, 60, (255, 240, 180), (230, 170, 150), steps=8)
        c.rect(990, 314, 1020, 340, (255, 236, 160), w=2.5)
        return c.img
    return cached("street", make)


ROAD_Y = 600


def road_layers():
    def make():
        night = D.gradient(W * SS, H * SS, [(0, (16, 20, 56)), (0.6, (44, 50, 106)), (1, (70, 64, 120))])
        nc = Canvas(night)
        D.stars(nc, 21, 110, W, 360)
        D.moon(nc, 1060, 120, 34, sky=(30, 36, 80))
        dawn = D.gradient(W * SS, H * SS, [(0, (90, 120, 190)), (0.45, (240, 170, 160)), (0.7, (255, 214, 160)),
                                           (1, (255, 214, 160))])
        dc = Canvas(dawn)
        dc.glow(980, 560, 380, 200, (255, 240, 200), (250, 190, 160), steps=10)
        # far Alps tile (RGBA)
        fw = 2 * W
        far = Canvas(Image.new("RGBA", (fw * SS + W * SS, H * SS), (0, 0, 0, 0)), size=(fw + W, H))
        rng = np.random.default_rng(8)
        for k in range(9):
            x = k * fw / 8
            for off in (0, fw):
                P.alp(far, x + off, 560, rng.uniform(300, 460), rng.uniform(160, 260), rock=(78, 76, 124),
                      snow=(170, 170, 210), shade=(140, 140, 186), seed=k, ol=None)
        # mid hills with firs
        mw = 2 * W
        mid = Canvas(Image.new("RGBA", (mw * SS + W * SS, H * SS), (0, 0, 0, 0)), size=(mw + W, H))
        ys = [560, 520, 540, 500, 530, 512, 548, 520, 560]
        for off in (0, mw):
            P.hill(mid, ys, off, off + mw, (40, 56, 72), base=620)
            for x in np.linspace(0, mw, 30, endpoint=False):
                yy = np.interp(x, np.linspace(0, mw, len(ys)), ys)
                P.fir_flat(mid, off + x + 13 * math.sin(x), yy + 20, 0.36 + 0.08 * math.sin(x * 3), (30, 46, 62))
        return night, dawn, far.img, mid.img
    return cached("road", make)


def munich_skyline(c, x, y, col):
    """Dark silhouette of Munich: the twin onion towers and the town hall tower, flat-coloured."""
    c.push(x, y)
    for bx, bw, bh in ((-260, 90, 60), (-170, 70, 90), (-90, 100, 70), (150, 120, 60), (270, 80, 80)):
        c.rect(bx, -bh, bx + bw, 0, col, ol=None)
        c.poly([(bx - 4, -bh), (bx + bw / 2, -bh - 26), (bx + bw + 4, -bh)], col, ol=None)
    for tx in (-28, 28):
        c.rect(tx - 18, -230, tx + 18, 0, col, ol=None)
        c.poly([(tx - 18, -230), (tx - 20, -244), (tx - 12, -258), (tx, -272), (tx + 12, -258), (tx + 20, -244),
                (tx + 18, -230)], col, ol=None)
    c.rect(80, -260, 112, 0, col, ol=None)
    c.poly([(80, -260), (96, -300), (112, -260)], col, ol=None)
    c.pop()


def post(tl, t):
    T = tl.t
    STAMPED[0] = t >= T("p_stamp", 0.55)
    if t < T("p_van"):
        return post_room(tl, t)
    if t < T("p_road"):
        return post_street(tl, t)
    return post_road(tl, t)


def post_room(tl, t):
    T = tl.t
    c = Canvas(room_bg().copy())
    rain(c, t)
    c.rect(756, 106, 1084, 374, None, w=8)
    close = ease(tl.prog("p_oops", t, 0.65, 0.95))
    sink = 70 * close
    bx, by = 560, 650
    P.parcel(c, bx, by, 1.4, lid=1.0 if close < 1 else 0.0, front=False)
    if close < 1:
        kat(c, tl, t, "luna", bx - 60, by - 92 + sink, 0.9, 1, "sit", look=(1, -0.2),
            eyes="happy" if T("p_best") <= t < T("p_stamp") else "open")
        wz = T("p_best", 0.0) <= t < T("p_stamp", 0.4)
        kat(c, tl, t, "whiskers", bx + 50, by - 92 + sink, 0.9, -1, "sit", eyes="closed" if wz else (
            "wide" if T("p_stamp", 0.55) <= t < T("p_oops") else "open"), look=(-1, -1))
    P.parcel(c, bx, by, 1.4, lid=1.0 if close < 1 else 0.0, back=False, label=close >= 1)
    # Pip with the tape roll, then the stamp
    u = tl.prog("p_stamp", t, 0.2, 0.75)
    px = lerp(820, 640, math.sin(math.pi * u))
    py = 640 + jump_y(u, 120) * 1.0 - 60 * math.sin(math.pi * u)
    D.mouse(c, px, py, 1.3, -1, t, mouth=tl.mouth("pip", t), eyes="happy" if t < T("p_stamp") else "open",
            proud=T("p_oops") <= t < T("p_oops", 1))
    if T("p_stamp") <= t < T("p_stamp", 0.55):
        P.stamp_mark(c, px - 30, py - 70, 1.0)
    if t < T("p_stamp"):
        c.circle(px - 30, 600, 16, (220, 210, 170), w=2.5)          # tape roll
        c.circle(px - 30, 600, 7, (180, 130, 80), w=2)
        if T("p_narr", 0.3) <= t < T("p_narr", 0.8):
            u2 = tl.prog("p_narr", t, 0.3, 0.8)
            c.line([(px - 46, 600), (px - 46 - 120 * u2, 560 - 20 * u2)], (232, 216, 172), 6)
    return finish(c, tl, t, 0.35)


def post_street(tl, t):
    T = tl.t
    c = Canvas(street_bg().copy())
    u = tl.prog("p_van", t)
    drive = ease(clamp((u - 0.62) / 0.38))
    vx = 820 + 900 * drive ** 1.6
    door = clamp((u - 0.12) / 0.1) * (1 - clamp((u - 0.5) / 0.08))
    P.post_van(c, vx, 640, 1.0, 1, t, wheel=-vx / 22, lights=0.6, open_door=door)
    # the parcel is lifted into the van
    a = ease(clamp((u - 0.2) / 0.28))
    if a < 0.98:
        px = lerp(345, vx - 175, a)
        py = lerp(598, 560, a) - 90 * math.sin(math.pi * a)
        P.parcel(c, px, py, 0.55 * (1 - 0.3 * a), lid=0.0, label=True)
    # Pip waves from the windowsill
    D.mouse(c, 530, 356, 1.0, 1, t, eyes="happy", hop=abs(math.sin(t * 6)) * 6)
    return finish(c, tl, t, 0.35)


def post_road(tl, t):
    T = tl.t
    night, dawn, far, mid = road_layers()
    k = ease(tl.prog("p_dawn", t, 0.0, 0.7))
    img = night.copy() if k <= 0 else (dawn.copy() if k >= 1 else Image.blend(night, dawn, k))
    c = Canvas(img)
    # Munich appears on the horizon at dawn
    if k > 0:
        mx = lerp(1500, 960, ease(tl.prog("p_dawn", t, 0.1, 1.0)))
        munich_skyline(c, mx, 560, mix((60, 50, 90), (130, 96, 120), k))
    ox = (t * 30) % (2 * W)
    crop = far.crop((int(ox * SS), 0, int(ox * SS) + W * SS, H * SS))
    c.img.paste(crop, (0, 0), crop)
    ox = (t * 110) % (2 * W)
    crop = mid.crop((int(ox * SS), 0, int(ox * SS) + W * SS, H * SS))
    c.img.paste(crop, (0, 0), crop)
    c.d = ImageDraw.Draw(c.img)
    road = mix((50, 52, 70), (120, 110, 120), k)
    c.rect(0, ROAD_Y - 30, W, H, mix((30, 44, 52), (90, 120, 80), k), ol=None)
    c.rect(0, ROAD_Y - 4, W, ROAD_Y + 70, road, ol=None)
    off = (t * 700) % 200
    for x in range(-200, W + 200, 200):
        c.rect(x - off, ROAD_Y + 30, x - off + 90, ROAD_Y + 38, (230, 220, 170), ol=None)
    for x in range(-100, W + 300, 240):
        xx = x - (t * 1100) % 240
        c.rect(xx, ROAD_Y + 80, xx + 10, ROAD_Y + 130, mix((60, 50, 40), (140, 110, 80), k), ol=None)
    c.rect(0, ROAD_Y + 96, W, ROAD_Y + 102, mix((60, 50, 40), (140, 110, 80), k), ol=None)
    bounce = abs(math.sin(t * 9)) * 2
    P.post_van(c, 600, ROAD_Y + 26 - bounce, 0.9, 1, t, wheel=-t * 14, lights=1 - k)
    return finish(c, tl, t, 0.3)


# ================================================================= square

SQ_W = 2 * W
SQ_Y = 650
TH = (640, 606, 0.68)       # town hall position and scale


def cobbles(c, x0, x1, y0, y1, base=(190, 176, 156), seed=1):
    c.rect(x0, y0, x1, y1, base, ol=None)
    rng = np.random.default_rng(seed)
    y = y0 + 6
    row = 0
    while y < y1:
        h = 8 + (y - y0) * 0.08
        x = x0 - (row % 2) * h
        while x < x1:
            w = h * rng.uniform(1.3, 1.9)
            col = mix(base, (120, 104, 96) if rng.random() < 0.5 else (230, 220, 200), rng.uniform(0.1, 0.35))
            c.ellipse(x + w / 2, y + h / 2, w / 2 - 1, h / 2 - 1, col, ol=None)
            x += w
        y += h
        row += 1


def facade(c, x, y, w, h, col, seed=0, gable="step"):
    """A town house front with windows and a gable. origin bottom-left."""
    rng = np.random.default_rng(seed)
    c.rect(x, y - h, x + w, y, col, w=2.5)
    top = y - h
    if gable == "step":
        steps = [(x, top), (x + w * 0.1, top), (x + w * 0.1, top - 24), (x + w * 0.25, top - 24), (x + w * 0.25, top - 48),
                 (x + w * 0.4, top - 48), (x + w * 0.4, top - 72), (x + w * 0.6, top - 72), (x + w * 0.6, top - 48),
                 (x + w * 0.75, top - 48), (x + w * 0.75, top - 24), (x + w * 0.9, top - 24), (x + w * 0.9, top),
                 (x + w, top)]
        c.poly(steps, col, w=2.5)
    elif gable == "curve":
        pts = [(x + w * u, top - 70 * math.sin(math.pi * u) ** 0.6) for u in np.linspace(0, 1, 16)]
        c.poly(pts, col, w=2.5)
        c.circle(x + w / 2, top - 76, 8, col, w=2)
    else:
        c.poly([(x - 10, top), (x + w / 2, top - 60), (x + w + 10, top)], (150, 74, 56), w=2.5)
    c.rect(x, y - h, x + 8, y, mix(col, (0, 0, 0), 0.08), ol=None)
    n = max(2, int(w // 52))
    for row in range(int((h - 90) // 64)):
        wy = top + 30 + row * 64
        for k in range(n):
            wx = x + (k + 0.5) * w / n
            c.rect(wx - 11, wy, wx + 11, wy + 34, (80, 96, 130), w=2)
            c.rect(wx - 15, wy + 34, wx + 15, wy + 38, (250, 250, 250), ol=None)
    c.rect(x + w * 0.3, y - 64, x + w * 0.7, y, mix(col, (60, 40, 30), 0.5), w=2)


def pigeon(c, x, y, t, s=1.0, face=1, seed=0.0):
    peck = max(0.0, math.sin(t * 3 + seed * 5)) ** 6
    c.push(x, y, s, flip=face < 0)
    c.ellipse(0, -12, 14, 9, (150, 150, 168), w=2)
    c.poly([(-12, -14), (-24, -10), (-12, -8)], (120, 120, 140), w=1.5)
    hx, hy = 12 + 4 * peck, -22 + 12 * peck
    c.circle(hx, hy, 6, (130, 140, 160), w=2)
    c.circle(hx + 2, hy - 1, 1.5, OUT, ol=None)
    c.poly([(hx + 5, hy), (hx + 10, hy + 2), (hx + 5, hy + 3)], (230, 170, 80), ol=None)
    c.line([(-2, -4), (-3, 0)], (200, 110, 110), 2)
    c.line([(4, -4), (5, 0)], (200, 110, 110), 2)
    c.pop()


def square_bg():
    def make():
        c = Canvas(D.gradient(SQ_W * SS, H * SS, [(0, (120, 182, 238)), (0.6, (206, 232, 250)), (1, (206, 232, 250))]),
                   size=(SQ_W, H))
        for x, y, s in ((200, 90, 1.0), (900, 60, 0.8), (1500, 110, 1.1), (2200, 70, 0.9)):
            D.cloud(c, x, y, s)
        P.frauenkirche(c, 400, 606, 0.62)
        # houses left of the town hall
        facade(c, -20, 606, 150, 230, (240, 214, 150), 1, "curve")
        facade(c, 130, 606, 150, 210, (236, 190, 180), 2, "step")
        x, y, s = TH
        P.town_hall(c, x, y, s)
        # houses on the right side of the square
        cols = [(246, 226, 160), (226, 200, 210), (200, 226, 206), (246, 236, 220), (236, 196, 160), (210, 220, 236),
                (246, 216, 186), (226, 236, 196)]
        xx = 1000
        k = 0
        while xx < SQ_W:
            w = 170 + 50 * ((k * 7) % 3)
            h = 200 + 30 * ((k * 5) % 3)
            facade(c, xx, 606, w, h, cols[k % len(cols)], k + 3, ("step", "curve", "roof")[k % 3])
            xx += w
            k += 1
        cobbles(c, 0, SQ_W, 606, H)
        c.line([(0, 606), (SQ_W, 606)], mix((190, 176, 156), (0, 0, 0), 0.3), 2.5)
        P.mary_column(c, 1060, 640, 0.8)
        P.pretzel_stand(c, 1290, 640, 0.9)
        # a chestnut tree and benches near the wagon
        D.tree(c, 2480, 640, 1.2, leaf=(100, 160, 80), trunk=(120, 84, 56))
        for bx in (760, 1600):
            c.rect(bx - 50, 612, bx + 50, 620, (140, 96, 60), w=2)
            c.rect(bx - 44, 620, bx - 38, 640, (90, 64, 44), ol=None)
            c.rect(bx + 38, 620, bx + 44, 640, (90, 64, 44), ol=None)
        return c.img
    return cached("square", make)


def square(tl, t):
    T = tl.t
    STAMPED[0] = True
    camx = smooth(t, [(T("s_grab"), 0), (T("s_grab", 0.6), 420), (T("s_roll", 0.1), 420),
                      (T("s_roll", 0.85), 1280)], 0.5)
    camx = clamp(camx, 0, SQ_W - W)
    c = view(square_bg(), camx)
    c.push(-camx, 0)
    x, y, s = TH
    P.glock_figures(c, x, y, s, spin=t * 1.1)
    for k, px in enumerate((150, 196, 230, 880)):
        pigeon(c, px, 652 + (k % 2) * 8, t, 0.9, 1 if k % 2 else -1, seed=k)
    # Hansl and the hay wagon
    P.hay_wagon(c, 2180, SQ_Y, 0.8, wheel=0.0)
    P.horse(c, 2410, SQ_Y + 2, 0.72, 1, t, head=0.15 + 0.1 * math.sin(t * 0.8))
    u0 = tl.prog("s_open", t)
    # the post van drives away
    if u0 < 0.6:
        vx = lerp(760, -420, ease(u0 / 0.6))
        P.post_van(c, vx, 676, 0.9, -1, t, wheel=vx / 20)
    # the parcel pops open, the cats hop out
    open_ = u0 > 0.15
    bx, by = 460, 668
    P.parcel(c, bx, by, 0.9, lid=1.0 if open_ else 0.0, front=False, label=False)
    pose_s = 0.78
    lu = clamp((u0 - 0.3) / 0.25)
    wu = clamp((u0 - 0.45) / 0.25)
    inside = []
    if lu <= 0 and open_:
        inside.append(("luna", bx - 30))
    if wu <= 0 and open_:
        inside.append(("whiskers", bx + 30))
    for who, ix in inside:
        kat(c, tl, t, who, ix, by - 40, 0.7, 1, "sit", eyes="wide" if who == "whiskers" else "open")
    P.parcel(c, bx, by, 0.9, lid=1.0 if open_ else 0.0, back=False, label=not open_)
    # Luna
    if lu > 0:
        if t < T("s_grab"):
            lx = lerp(bx - 30, 360, lu)
            ly = lerp(by - 40, SQ_Y, lu) + jump_y(lu, 50)
            pose = "leap" if 0 < lu < 1 else "sit"
            kat(c, tl, t, "luna", lx, ly, pose_s, 1, pose, look=(0.4, -1) if t >= T("s_look") else (1, 0),
                eyes="happy" if T("s_look") <= t < T("s_look", 1) and tl.mouth("luna", t) < 0.1 else "open")
        else:
            keys = [(T("s_roll", 0.0), 360), (T("s_roll", 1.0), 1640), (T("s_end", 0.1), 1640),
                    (T("s_end", 0.7), 2200)]
            hu = tl.prog("s_end", t, 0.72, 0.92)
            ly = lerp(SQ_Y, 548, hu) + jump_y(hu, 40)
            lx = actor(c, tl, t, "luna", keys, ly, pose_s, 1, pose="sit" if hu >= 1 else "stand", look=(1, 0))
    # Whiskers and the giant pretzel
    pr_x, pr_ang, pr_on = 1370, 0.0, True
    if wu > 0:
        if t < T("s_grab"):
            wx = lerp(bx + 30, 580, wu)
            wy = lerp(by - 40, SQ_Y, wu) + jump_y(wu, 50)
            pose = "leap" if 0 < wu < 1 else "sit"
            sniff = T("s_smell") <= t
            kat(c, tl, t, "whiskers", wx, wy, pose_s, 1, pose, eyes="closed" if sniff and tl.mouth("whiskers", t) < 0.1
                else "open", look=(1, -0.6), head_dy=-6 if sniff else 0)
        elif t < T("s_roll"):
            keys = [(T("s_grab"), 580), (T("s_grab", 0.55), 1300)]
            wx = actor(c, tl, t, "whiskers", keys, SQ_Y, pose_s, 1)
            if t >= T("s_grab", 0.62):
                pr_on = False
                kat_pretzel = True
                lift = ease(tl.prog("s_grab", t, 0.62, 0.8))
                P.pretzel(c, wx + 62 * pose_s, SQ_Y - 40 - 40 * lift, 40, 0.0)
        else:
            u = tl.prog("s_roll", t)
            keys = [(T("s_roll", 0.1), 1300), (T("s_roll", 0.9), 1760), (T("s_end", 0.1), 1760),
                    (T("s_end", 0.75), 2120)]
            hop = 0.0
            if t >= T("s_end", 0.75):
                hop = 1.0
            wy = SQ_Y
            on_hay = t >= T("s_end", 0.75)
            hu = tl.prog("s_end", t, 0.75, 0.95)
            if on_hay:
                wy = lerp(SQ_Y, 548, hu) + jump_y(hu, 40)
            wx = actor(c, tl, t, "whiskers", keys, wy, pose_s, 1, pose="sit" if hu >= 1 else "stand",
                       eyes="wide" if u < 0.9 and t < T("s_resi") else "open")
            pr_on = False
        if pr_on:
            P.pretzel(c, pr_x, 610, 40, 0.15)
    else:
        P.pretzel(c, pr_x, 610, 40, 0.15)
    # the runaway pretzel
    if t >= T("s_roll"):
        u = tl.prog("s_roll", t)
        px = lerp(1340, 1872, ease(clamp((u - 0.03) / 0.82)) ** 1.3)
        if t < T("s_end"):
            bump = abs(math.sin(px / 14)) * 4 * (u < 0.85)
            P.pretzel(c, px, SQ_Y - 40 - bump, 40, (px - 1340) / 40)
    # Luna on the hay
    if t >= T("s_end", 0.8):
        pass
    # Resi
    if t >= T("s_roll", 0.5):
        keys = [(T("s_roll", 0.55), 2120), (T("s_roll", 0.85), 1920), (T("s_end", 0.1), 1920),
                (T("s_end", 0.7), 2060)]
        ru = tl.prog("s_end", t, 0.75, 0.95)
        ry = lerp(SQ_Y, 552, ru) + jump_y(ru, 40)
        actor(c, tl, t, "resi", keys, ry, 0.8, -1, wave=1.0 if T("s_resi") <= t < T("s_resi", 0.6) else 0.0,
              eyes="happy" if T("s_hop") <= t < T("s_hop", 1) else "open")
    if t >= T("s_end", 0.75):
        # Luna hops onto the hay too
        pass
    c.pop()
    return finish(c, tl, t, 0.4)


# ================================================================ village

VW = 2 * W
VY = 660


def village_bg():
    def make():
        c = Canvas(D.gradient(VW * SS, H * SS, [(0, (110, 176, 236)), (0.55, (214, 236, 250)), (1, (214, 236, 250))]),
                   size=(VW, H))
        for x, y, s in ((300, 80, 0.9), (1100, 60, 1.1), (1900, 90, 0.8)):
            D.cloud(c, x, y, s)
        rng = np.random.default_rng(3)
        for k in range(8):
            P.alp(c, 160 + k * 340 + rng.uniform(-40, 40), 470, rng.uniform(420, 560), rng.uniform(250, 360), seed=k)
        P.hill(c, [480, 440, 470, 430, 460, 420, 450, 430, 470], 0, VW, (120, 176, 96), ol=OUT)
        for x in np.linspace(0, VW, 40):
            yy = np.interp(x, np.linspace(0, VW, 9), [480, 440, 470, 430, 460, 420, 450, 430, 470])
            if rng.random() < 0.6:
                P.fir(c, x + rng.uniform(-20, 20), yy + 10, rng.uniform(0.28, 0.38), col=(60, 120, 80), dark=(44, 96, 66))
        P.hill(c, [560, 540, 556, 530, 548, 540, 560], 0, VW, (140, 196, 104), ol=OUT)
        # the village on the right
        P.onion_church(c, 2300, 560, 0.75)
        P.maypole(c, 1980, 600, 360)
        houses = [(1700, 230, 170, (250, 240, 214), (60, 120, 80)), (2120, 200, 160, (252, 230, 200), (160, 60, 50)),
                  (2500, 220, 170, (240, 236, 220), (60, 90, 150))]
        for k, (hx, w, h, wall, sh) in enumerate(houses):
            P.painted_house(c, hx, 600, w, h, wall=wall, shutter=sh, seed=k)
        # meadow, road, flowers
        P.hill(c, [612, 606, 616, 604, 612, 608, 614], 0, VW, (150, 206, 110), ol=OUT)
        c.poly([(0, 640), (VW, 640), (VW, 700), (0, 700)], (206, 176, 128), ol=None)
        c.line([(0, 640), (VW, 640)], (170, 140, 100), 2.5)
        c.line([(0, 700), (VW, 700)], (170, 140, 100), 2.5)
        c.rect(0, 700, VW, H, (130, 190, 96), ol=None)
        for _ in range(140):
            x, y = rng.uniform(0, VW), rng.uniform(612, 636)
            c.circle(x, y, 2.5, ((255, 255, 255), (250, 210, 60), (230, 80, 120))[rng.integers(3)], ol=None)
        # a wooden fence along the road
        for x in range(0, VW, 70):
            c.rect(x, 600, x + 7, 640, (150, 104, 66), w=1.5)
        c.line([(0, 612), (VW, 612)], (150, 104, 66), 4)
        c.line([(0, 626), (VW, 626)], (150, 104, 66), 4)
        return c.img
    return cached("village", make)


def bakery_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 176, 236)), (1, (214, 236, 250))]))
        P.alp(c, 120, 300, 420, 220, seed=4)
        P.alp(c, 1160, 300, 460, 240, seed=6)
        cobbles(c, 0, W, 520, H, base=(196, 184, 160), seed=4)
        P.painted_house(c, 640, 540, 640, 470, wall=(250, 238, 210), roof=(160, 76, 56), shutter=(60, 120, 80),
                        seed=9, balcony=True, door=False)
        # shop window + sign
        c.rect(450, 380, 830, 520, (120, 76, 46), w=3)
        c.rect(462, 392, 818, 520, (255, 236, 190), ol=None)
        for k in range(5):
            P.pretzel(c, 500 + k * 72, 440, 20, 0.0)
            c.rect(480 + k * 72, 476, 522 + k * 72, 492, (226, 178, 98), w=1.5, r=6)
        c.rect(520, 330, 760, 370, (60, 90, 60), w=2.5, r=6)
        c.text(640, 350, "BÄCKEREI", 26, (255, 236, 160))
        # hanging pretzel sign on a wrought-iron bracket
        c.line([(930, 300), (1030, 300)], OUT, 4)
        c.line([(930, 330), (1000, 300)], OUT, 3)
        c.line([(1010, 300), (1010, 316)], OUT, 2)
        P.pretzel(c, 1010, 344, 30, 0.0)
        # geraniums
        for x in (380, 900):
            c.rect(x - 40, 500, x + 40, 520, (160, 90, 50), w=2)
            for k in range(7):
                c.circle(x - 34 + k * 11, 494 - (k % 2) * 6, 7, (226, 50, 60), w=1.5)
        # the table with a Bavarian diamond cloth
        c.rect(250, 556, 1030, H + 10, (255, 255, 255), w=3)
        for row in range(5):
            for k in range(30):
                xx = 250 + k * 28 + (14 if row % 2 else 0)
                yy = 572 + row * 34
                if xx < 1020:
                    c.poly([(xx, yy), (xx + 14, yy - 16), (xx + 28, yy), (xx + 14, yy + 16)], P.BAV_BLUE, ol=None)
        c.rect(250, 548, 1030, 562, (250, 250, 250), w=3)
        return c.img
    return cached("bakery", make)


def piping_bag(c, x, y, ang=2.2, s=1.0):
    c.push(x, y, s)
    pts = P.rot([(0, 0), (40, -14), (44, 14)], ang)
    c.poly(pts, (240, 240, 250), w=2)
    tip = P.rot([(0, 0), (-8, -4), (-8, 4)], ang)
    c.poly(tip, (200, 200, 210), w=1.5)
    c.pop()


def village(tl, t):
    T = tl.t
    STAMPED[0] = True
    if t < T("v_strudel"):
        return village_ride(tl, t)
    return village_bakery(tl, t)


def village_ride(tl, t):
    T = tl.t
    keys = [(T("v_ride"), 200), (tl.ev("v_narr").end + 0.3, 1600)]
    wx = smooth(t, keys, 0.6)
    moving = speed(t, keys) > 5
    camx = clamp(wx - 420, 0, VW - W)
    c = view(village_bg(), camx)
    c.push(-camx, 0)
    from films.montblanc.props import cow
    for x, y, f in ((700, 600, 1), (1180, 596, -1)):
        cow(c, x, y, 0.55, f, t)
    bob = abs(math.sin(wx / 30)) * 3 if moving else 0
    P.hay_wagon(c, wx, VY - bob * 0.3, 0.8, wheel=wx / 27)
    P.horse(c, wx + 230, VY + 2, 0.72, 1, t, walk=wx / 22 if moving else 0.0)
    top = VY - 98 - bob
    resi(c, tl, t, wx - 90, top + 4, 0.7, 1)
    kat(c, tl, t, "luna", wx - 20, top, 0.7, 1, "sit", look=(1, -0.3), eyes="happy" if moving else "open")
    kat(c, tl, t, "whiskers", wx + 50, top + 2, 0.7, 1, "sit", look=(1, -0.2), eyes="happy" if moving else "open")
    c.pop()
    return finish(c, tl, t, 0.4)


def village_bakery(tl, t):
    T = tl.t
    c = Canvas(bakery_bg().copy())
    u = tl.prog("v_eat", t) if t < T("v_beard") else 1.0
    eaten = ease(clamp((u - 0.1) / 0.35))
    cream = ease(clamp((u - 0.45) / 0.2)) * (1 - ease(clamp((u - 0.7) / 0.12)))
    beard = 1.0 if u >= 0.82 else 0.0
    lean = ease(clamp(u / 0.1)) * (1 - ease(clamp((u - 0.85) / 0.1)))
    dive = math.sin(math.pi * clamp((u - 0.68) / 0.16))
    # behind the table (cats are cut off by the tablecloth drawn after)
    wy = 604
    going = t >= T("v_go")
    if not going:
        chomp = 0.5 + 0.5 * math.sin(t * 22) if 0.1 < u < 0.45 else None
        kw = {}
        if chomp is not None:
            kw["mouth"] = chomp
        kat(c, tl, t, "whiskers", 520 + 40 * lean, wy, 1.05, 1, "sit", head_dy=12 * lean + 26 * dive, beard=beard,
            eyes="closed" if (0.1 < u < 0.45 or dive > 0.2) else ("happy" if beard and tl.mouth("whiskers", t) < 0.1
                                                                     else "open"), look=(1, 0.6), **kw)
    else:
        keys = [(T("v_go"), 520), (T("v_go", 0.9), 1450)]
        actor(c, tl, t, "whiskers", keys, wy, 1.05, 1, carry=True)
    lmouth = laughing(t) * 0.7 if T("v_beard", 0.3) <= t < T("v_carry") else tl.mouth("luna", t)
    kat(c, tl, t, "luna", 900, wy, 1.05, -1, "sit", mouth=lmouth, look=(-1, 0.4),
        eyes="happy" if T("v_beard", 0.3) <= t < T("v_carry") else "open")
    # table top items
    c.rect(250, 548, 1030, 562, (250, 250, 250), w=3)
    for row in range(5):
        pass
    tablecloth = cached("cloth", lambda: bakery_bg().crop((0, 548 * SS, W * SS, H * SS)))
    c.img.paste(tablecloth, (0, 548 * SS))
    P.strudel(c, 650, 556, 1.1, eaten=eaten, cream=cream)
    # Resi on the table with a piping bag
    squirt = 0.45 < u < 0.66
    rx = 790
    resi(c, tl, t, rx, 552, 0.85, -1, eyes="happy" if T("v_beard") <= t < T("v_carry") else "open")
    if t < T("v_beard"):
        piping_bag(c, rx - 30, 500 + (6 * math.sin(t * 20) if squirt else 0), 2.6, 1.1)
    return finish(c, tl, t, 0.45)


# ================================================================= forest

FW = W + 420
FY = 650


def forest_bg():
    def make():
        c = Canvas(D.gradient(FW * SS, H * SS, [(0, (40, 70, 70)), (0.45, (190, 160, 96)), (0.62, (120, 130, 80)),
                                                (1, (50, 70, 44))]), size=(FW, H))
        rng = np.random.default_rng(6)
        for x in np.linspace(-40, FW + 40, 34):
            P.fir_flat(c, x + rng.uniform(-20, 20), 600 + rng.uniform(-20, 10), rng.uniform(0.9, 1.3), (96, 120, 96))
        for x in np.linspace(-40, FW + 40, 24):
            P.fir_flat(c, x + rng.uniform(-30, 30), 620 + rng.uniform(-10, 10), rng.uniform(1.1, 1.5), (60, 86, 66))
        # light shafts
        shafts = Image.new("RGBA", c.img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shafts)
        for x0 in (300, 700, 1150, 1480):
            pts = [(x0, 0), (x0 + 70, 0), (x0 - 160, 720), (x0 - 330, 720)]
            sd.polygon([(px * SS, py * SS) for px, py in pts], fill=(255, 236, 170, 46))
        shafts = shafts.filter(ImageFilter.GaussianBlur(12 * SS))
        base = c.img.convert("RGBA")
        base.alpha_composite(shafts)
        c.img = base.convert("RGB")
        c.d = ImageDraw.Draw(c.img)
        # mid trees with trunks
        for x in (120, 420, 880, 1180, 1420, 1640):
            P.fir(c, x, 612, 1.5, col=(40, 84, 62), dark=(28, 62, 48))
        # forest floor
        c.rect(0, 600, FW, H, (70, 96, 54), ol=None)
        c.poly([(0, 630), (FW, 626), (FW, 690), (0, 694)], (160, 128, 86), ol=None)
        c.line([(0, 630), (FW, 626)], (110, 86, 60), 2.5)
        c.line([(0, 694), (FW, 690)], (110, 86, 60), 2.5)
        for _ in range(26):
            x, y = rng.uniform(0, FW), rng.uniform(604, 626)
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.5
                c.line([(x, y), (x + math.cos(a) * 26, y + math.sin(a) * 22)], (90, 140, 70), 4)
        for x, y in ((240, 620), (760, 616), (1300, 622), (1560, 618)):
            c.rect(x - 3, y - 14, x + 3, y, (250, 246, 236), w=1.5)
            c.ellipse(x, y - 16, 12, 8, (220, 50, 40), w=2)
            for dx in (-5, 2, 6):
                c.circle(x + dx, y - 18 + abs(dx) * 0.3, 1.8, (255, 255, 255), ol=None)
        c.rect(0, 694, FW, H, (60, 84, 48), ol=None)
        return c.img
    return cached("forest", make)


def forest(tl, t):
    T = tl.t
    STAMPED[0] = True
    camx = smooth(t, [(T("f_in"), 0), (T("f_eyes"), 300), (T("f_end"), 300), (T("f_end", 1), 420)], 0.5)
    c = view(forest_bg(), camx)
    c.push(-camx, 0)
    # glowing eyes in the dark
    if T("f_eyes", 0.2) <= t < T("f_deer", 0.2):
        P.glow_eyes(c, 1040, 520, t, 1.0, seed=1)
        P.glow_eyes(c, 1160, 566, t, 0.8, seed=2)
    # the deer step out
    if t >= T("f_deer"):
        k = ease(tl.prog("f_deer", t, 0.0, 0.8))
        bow = math.sin(math.pi * tl.prog("f_bow", t, 0.1, 0.7))
        P.deer(c, lerp(1260, 1030, k), FY - 6, 0.9, -1, t, bow=bow)
        P.deer(c, lerp(1330, 1150, k), FY, 0.6, -1, t, bow=bow * 0.8, fawn=True, seed=3)
    c.tint = ((30, 40, 70), 0.12)
    scared = T("f_eyes", 0.3) <= t < T("f_deer", 0.5)
    bowing = math.sin(math.pi * tl.prog("f_bow", t, 0.3, 0.8))
    rk = [(T("f_in"), 120), (T("f_in", 1), 800), (T("f_end"), 800), (T("f_end", 1), 1560)]
    actor(c, tl, t, "resi", rk, FY, 0.8, 1, eyes="happy" if T("f_deer") <= t < T("f_bow") else "open")
    lk = [(T("f_in"), 0), (T("f_in", 1), 670), (T("f_end", 0.15), 670), (T("f_end", 1), 1400)]
    actor(c, tl, t, "luna", lk, FY, 0.85, 1, head_dy=10 * bowing, eyes="happy" if bowing > 0.3 else "open")
    wk = [(T("f_in"), -120), (T("f_in", 1), 540), (T("f_end", 0.3), 540), (T("f_end", 1), 1260)]
    actor(c, tl, t, "whiskers", wk, FY, 0.85, 1, carry=True, eyes="wide" if scared else (
        "happy" if bowing > 0.3 else "open"), head_dy=10 * bowing, look=(1, -0.3) if scared else (0, 0))
    c.tint = None
    # foreground ferns
    c.pop()
    for x in (0, 1270):
        P.fir(c, x, 760, 1.9, col=(24, 50, 38), dark=(16, 36, 28))
    return finish(c, tl, t, 0.3)


# ================================================================= bridge

BH = 1200
DECK = 470
FALL_X = (560, 650)
LEDGE = (770, 952)


def bridge_bg():
    def make():
        c = Canvas(D.gradient(W * SS, BH * SS, [(0, (110, 164, 228)), (0.3, (250, 214, 168)), (0.45, (150, 140, 130)),
                                                (1, (60, 60, 70))]), size=(W, BH))
        D.cloud(c, 200, 80, 0.9, (255, 246, 236))
        D.cloud(c, 560, 50, 0.7, (255, 246, 236))
        P.alp(c, 160, 330, 520, 250, seed=11, rock=(160, 150, 180))
        P.alp(c, 520, 330, 460, 200, seed=12, rock=(160, 150, 180))
        P.alp(c, 1180, 300, 560, 260, seed=13, rock=(160, 150, 180))
        # forested slopes across the gorge
        P.hill(c, [360, 330, 300, 320, 290, 300, 330], 0, W, (70, 116, 80), base=BH)
        rng = np.random.default_rng(14)
        for x in np.linspace(0, W, 44):
            P.fir_flat(c, x + rng.uniform(-12, 12), 360 + rng.uniform(-30, 10), rng.uniform(0.3, 0.42), (54, 96, 66))
        # the castle on its crag, across the gorge
        P.castle_cliff(c, 960, 300, 0.42, seed=15)
        P.neuschwanstein(c, 960, 302, 0.5)
        for x, y in ((800, 380), (830, 420), (1110, 400), (1160, 430), (1220, 420)):
            P.fir_flat(c, x, y, 0.42, (50, 90, 62))
        # back wall of the gorge
        c.poly([(260, 420), (1020, 420), (980, BH), (300, BH)], (110, 104, 108), ol=None)
        for k in range(30):
            x, y = rng.uniform(300, 980), rng.uniform(560, BH)
            c.line([(x, y), (x + rng.uniform(-20, 20), y + rng.uniform(20, 60))], (90, 86, 92), 2)
        # mossy rock lip the waterfall pours over
        c.ellipse(605, 522, 80, 18, (96, 120, 90), w=2.5)
        # left gorge wall
        P.rock_face(c, [(0, 430), (300, 430), (360, 600), (400, 760), (380, 900), (430, 1060), (420, BH), (0, BH)],
                    seed=16)
        # right gorge wall with climbing steps and the ledge
        P.rock_face(c, [(1280, 430), (740, 430), (720, 560), (770, 620), (760, 700), (810, 740), (800, 820),
                        (840, 860), (830, 930), (700, 940), (690, 975), (850, 985), (870, 1100), (840, BH),
                        (1280, BH)], seed=17)
        for x0, x1, y in ((715, 790, 620), (760, 830, 740), (800, 860, 860)):
            c.rect(x0, y - 6, x1, y + 6, (176, 166, 160), w=2, r=4)
        c.rect(690, 948, 860, 962, (176, 166, 160), w=2.5, r=5)
        c.ellipse(840, 940, 12, 6, (90, 140, 70), ol=None)
        for x, y, s in ((40, 470, 0.7), (130, 480, 0.6), (1220, 470, 0.7), (1150, 480, 0.55), (920, 480, 0.5)):
            P.fir(c, x, y, s)
        # pool at the bottom
        c.rect(300, 1130, 980, BH, (80, 130, 160), ol=None)
        c.line([(300, 1130), (980, 1130)], (200, 230, 240), 3)
        # the Marienbruecke: iron truss, deck and railing
        iron, iron_d = (92, 92, 104), (60, 60, 72)
        c.rect(0, DECK + 2, W, DECK + 18, iron, w=2.5)
        c.rect(0, DECK + 18, W, DECK + 26, iron_d, ol=None)
        c.rect(0, DECK + 74, W, DECK + 84, iron, w=2)
        for k in range(0, W + 60, 60):
            c.line([(k, DECK + 26), (k + 60, DECK + 74)], iron, 4)
            c.line([(k + 60, DECK + 26), (k, DECK + 74)], iron, 4)
            c.line([(k, DECK + 26), (k, DECK + 74)], iron_d, 3)
        c.rect(0, DECK - 52, W, DECK - 44, iron, w=2)               # top rail
        for k in range(0, W + 40, 40):
            c.line([(k, DECK - 44), (k + 40, DECK + 2)], iron_d, 2.5)
            c.line([(k + 40, DECK - 44), (k, DECK + 2)], iron_d, 2.5)
        for k in range(0, W, 120):
            c.rect(k - 4, DECK - 56, k + 4, DECK + 4, iron, w=1.5)
        c.rect(0, DECK - 4, W, DECK + 4, (150, 120, 90), w=2)       # wooden planks
        return c.img
    return cached("bridge", make)


def waterfall(c, t, camy):
    x0, x1 = FALL_X
    top, bot = 530, 1130
    c.rect(x0, top - 6, x1, bot, (170, 214, 240), ol=None)
    rng = np.random.default_rng(5)
    for k in range(26):
        x = rng.uniform(x0 + 4, x1 - 4)
        u = (t * rng.uniform(0.9, 1.3) + rng.uniform()) % 1.0
        y = top + u * (bot - top)
        c.line([(x, y), (x, min(bot, y + 60))], (240, 250, 255), 3, cap=False)
    c.line([(x0, top), (x0, bot)], (120, 170, 200), 2.5, cap=False)
    c.line([(x1, top), (x1, bot)], (120, 170, 200), 2.5, cap=False)
    for k in range(9):
        a = t * 2 + k
        c.circle(lerp(x0 - 20, x1 + 20, (k + 0.5) / 9) + 6 * math.sin(a), bot - 6 + 4 * math.cos(a * 1.3),
                 16 + 4 * math.sin(a * 2), (236, 246, 252), ol=None)
    # spray drifting onto the ledge
    for k in range(6):
        u = (t * 0.8 + k / 6) % 1.0
        c.circle(x1 + 10 + 80 * u, 930 - 40 * math.sin(math.pi * u), 6 * (1 - u) + 2, (230, 244, 252), ol=None)


def bridge(tl, t):
    T = tl.t
    STAMPED[0] = True
    camy = smooth(t, [(T("b_drop", 0.3), 0), (T("b_drop", 0.65), 420), (T("b_drop", 0.85), 420),
                      (T("b_drop", 1.0), 0), (T("b_climb", 0.1), 0), (T("b_climb", 0.45), 400),
                      (T("b_climb", 0.95), 400), (T("b_pull", 0.0), 250), (T("b_up", 0.3), 120),
                      (T("b_up", 0.7), 0)], 0.4)
    camy = clamp(camy, 0, BH - H)
    c = view(bridge_bg(), 0, camy)
    c.push(0, -camy)
    waterfall(c, t, camy)
    # --- Whiskers
    wpos, wpose, wface, wkw = (620, DECK), "stand", 1, {}
    has_head_book = T("b_show", 0.3) <= t < T("b_drop", 0.25)
    wet = ease(tl.prog("b_climb", t, 0.6, 0.7))
    walk = 0.0
    if t < T("b_show"):
        keys = [(T("b_view"), -120), (T("b_view", 1), 620)]
        x = smooth(t, keys)
        moving = speed(t, keys) > 20
        wpos, walk = (x, DECK), (x / 10 if moving else 0.0)
    elif t < T("b_drop", 0.5):
        u = tl.prog("b_show", t, 0.0, 0.3)
        wpos = (620, lerp(DECK, DECK - 50, u) + jump_y(u, 30))
        wpose = "leap" if 0 < u < 1 else "stand"
        if T("b_drop") <= t:
            wkw["eyes"] = "wide"
    elif t < T("b_climb"):
        u = tl.prog("b_drop", t, 0.5, 0.65)
        wpos = (620, lerp(DECK - 50, DECK, u) + jump_y(u, 20))
        quiet = T("b_quiet") <= t < T("b_fault", 0.3)
        wpose = "sit" if T("b_fly", 1) <= t else "stand"
        if quiet:
            wkw.update(eyes="closed", head_dy=10)
    else:
        path = [(0.0, 620, DECK), (0.1, 650, DECK - 50), (0.2, 750, 614), (0.3, 795, 734), (0.4, 830, 854),
                (0.5, 790, 950), (0.62, 760, 950)]
        u = tl.prog("b_climb", t)
        if t < T("b_pull"):
            i = max(k for k in range(len(path)) if path[k][0] <= u)
            if i + 1 < len(path):
                (u0, x0, y0), (u1, x1, y1) = path[i], path[i + 1]
                f = ease((u - u0) / (u1 - u0))
                wpos = (lerp(x0, x1, f), lerp(y0, y1, f) + jump_y(f, 26))
                wpose = "leap" if 0.1 < f < 0.9 else "crouch"
                wface = 1 if x1 >= x0 else -1
            else:
                wpos, wpose, wface = (760, 950), "crouch" if u < 0.66 else "stand", -1
        else:
            # pulled up the cliff on the vine
            k = ease(tl.prog("b_pull", t, 0.1, 1.0)) * 0.7 + ease(tl.prog("b_up", t, 0.0, 0.6)) * 0.3
            pts = [(760, 950), (800, 800), (760, 640), (700, DECK)]
            seg = min(2, int(k * 3))
            f = k * 3 - seg
            if k >= 1:
                wpos, wface = (700, DECK), -1
            else:
                (x0, y0), (x1, y1) = pts[seg], pts[seg + 1]
                wpos, wface = (lerp(x0, x1, f), lerp(y0, y1, f)), -1
                wpose = "leap"
            if k >= 1:
                wpose = "stand"
    mouthbook = T("b_climb", 0.6) <= t < T("b_safe")
    carry = t >= T("b_safe")
    # --- the book
    if has_head_book:
        pass
    elif T("b_drop", 0.25) <= t < T("b_climb", 0.6):
        u = ease(tl.prog("b_drop", t, 0.25, 0.75))
        bx = lerp(640, 790, u)
        by = lerp(DECK - 150, 942, u ** 1.6)
        book_slab(c, bx, by, 0.9, ang=u * 9 if u < 1 else 0.0)
    kat(c, tl, t, "whiskers", wpos[0], wpos[1], 0.82, wface, wpose, walk=walk, wet=wet, headbook=has_head_book,
        mouthbook=mouthbook, carry=carry, **wkw)
    if T("b_climb", 0.6) <= t < T("b_climb", 0.75):
        dt = t - T("b_climb", 0.62)
        for k in range(10):
            a = k / 10 * math.pi + math.pi
            r = 30 + 160 * clamp(dt / 0.6)
            c.circle(760 + math.cos(a) * r, 920 + math.sin(a) * r * 0.6, 7 * (1 - clamp(dt / 0.6)) + 1,
                     (220, 240, 255), ol=None)
    # --- vine from the deck
    vine_on = T("b_climb", 0.75) <= t < T("b_up", 0.6)
    lx, rx = 470, 360
    pulling = T("b_pull") <= t < T("b_up", 0.6)
    tug = 8 * math.sin(t * 7) if pulling else 0
    if vine_on:
        drop = ease(tl.prog("b_climb", t, 0.75, 0.95))
        end = (lerp(560, wpos[0], drop), lerp(DECK - 30, wpos[1] - 50, drop))
        mid = ((560 + end[0]) / 2 + 30, (DECK + end[1]) / 2)
        c.line([(lx + 40 - tug, DECK - 52), (560, DECK - 30), mid, end], (70, 120, 50), 5)
        for k in range(6):
            u = (k + 0.5) / 6
            px, py = lerp(560, end[0], u), lerp(DECK - 30, end[1], u)
            c.ellipse(px + 6, py, 7, 4, (90, 160, 70), ol=None)
    # --- Luna and Resi
    lkeys = [(T("b_view"), -260), (T("b_view", 1), lx)]
    lpose = "stand"
    leyes = "happy" if T("b_wow") <= t < T("b_wow", 1) or t >= T("b_safe") else "open"
    if T("b_waited") <= t < T("b_fault"):
        leyes = "open"
    actor(c, tl, t, "luna", lkeys, DECK, 0.8, 1, pose="sit" if T("b_fly") <= t < T("b_climb") else lpose,
          eyes=leyes, look=(1, -0.6) if t < T("b_show") else (1, 0.3))
    rkeys = [(T("b_view"), -380), (T("b_view", 1), rx)]
    actor(c, tl, t, "resi", rkeys, DECK, 0.72, 1, hop=abs(math.sin(t * 12)) * 6 if t >= T("b_safe") else 0.0,
          eyes="happy" if t >= T("b_safe") else "open")
    c.pop()
    return finish(c, tl, t, 0.4)


# ================================================================= castle

GY = 630


def gate_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (60, 54, 120)), (0.35, (180, 110, 150)), (0.6, (250, 170, 140)),
                                               (1, (250, 170, 140))]))
        D.stars(c, 30, 30, W, 120, col=(255, 240, 230))
        g, gs = P.GATE, P.GATE_SH
        P.neuschwanstein(c, 600, 160, 0.34, lit=0.8, night=0.3)      # the white castle rising behind
        c.rect(120, 140, 1160, GY, g, w=3)
        rng = np.random.default_rng(31)
        for row in range(int((GY - 150) / 22)):
            y = 150 + row * 22
            off = 0 if row % 2 else 30
            for x in range(120 + off, 1160, 60):
                c.rect(x + 2, y + 2, x + 56, y + 18, mix(g, gs, rng.uniform(0.2, 0.7)), ol=None)
        for k in range(18):
            c.rect(120 + k * 58, 112, 150 + k * 58, 140, g, w=2)
        # corner towers with cones
        for tx in (120, 1160):
            c.rect(tx - 70, 60, tx + 70, GY, g, w=3)
            c.rect(tx - 70, 60, tx - 50, GY, gs, ol=None)
            P._cone(c, tx, -110, 60, 84)
            for wy in (180, 320):
                c.rect(tx - 14, wy, tx + 14, wy + 50, (70, 60, 80), w=2)
                c.ellipse(tx, wy, 14, 12, (70, 60, 80), w=2)
        # the archway
        c.rect(500, 330, 780, GY, (60, 40, 40), w=3)
        c.ellipse(640, 330, 140, 130, (60, 40, 40), w=3)
        c.rect(503, 330, 777, GY - 2, (60, 40, 40), ol=None)
        c.arc(640, 330, 158, 148, 180, 360, (230, 214, 190), 16)
        for x in (440, 840):                                          # lanterns
            c.line([(x, 300), (x, 330)], OUT, 3)
            c.glow(x, 360, 50, 50, (255, 230, 150), g, steps=8)
            c.rect(x - 14, 336, x + 14, 382, (255, 220, 120), w=2.5, r=3)
            c.poly([(x - 18, 336), (x, 318), (x + 18, 336)], (60, 60, 70), w=2)
        cobbles(c, 0, W, GY, H, base=(150, 130, 130), seed=7)
        return c.img
    return cached("gate", make)


def library_bg():
    def make():
        wall = (232, 204, 150)
        c = Canvas(bg=wall)
        c.rect(0, 0, W, 70, (110, 70, 44), ol=None)                     # coffered ceiling
        for x in range(0, W, 80):
            c.rect(x + 8, 8, x + 72, 62, (140, 92, 56), w=2)
            c.circle(x + 40, 35, 6, P.GOLD, ol=None)
        c.rect(0, 70, W, 100, (50, 80, 150), ol=None)                   # blue and gold frieze
        for x in range(0, W, 40):
            c.poly([(x, 100), (x + 20, 74), (x + 40, 100)], P.GOLD, ol=None)
        # tall arched windows with the night outside
        for wx in (150, 1130):
            win = D.gradient(160 * SS, 300 * SS, [(0, (20, 26, 70)), (1, (60, 60, 120))])
            c.img.paste(win, ((wx - 80) * SS, 180 * SS))
            c.ellipse(wx, 180, 80, 70, (20, 26, 70), ol=None)
            D.stars(c, wx, 8, W, 1)
            c.arc(wx, 180, 80, 70, 180, 360, (150, 110, 70), 8)
            c.line([(wx - 80, 180), (wx - 80, 480)], (150, 110, 70), 8)
            c.line([(wx + 80, 180), (wx + 80, 480)], (150, 110, 70), 8)
            c.line([(wx, 120), (wx, 480)], (150, 110, 70), 5)
            c.line([(wx - 80, 320), (wx + 80, 320)], (150, 110, 70), 5)
            c.rect(wx - 96, 478, wx + 96, 494, (170, 126, 80), w=2.5)
            for k in range(5):
                c.circle(wx - 60 + k * 30, 230 + (k % 2) * 40, 1.6, (255, 250, 220), ol=None)
        # the Swan Knight mural
        c.rect(400, 120, 880, 360, (180, 140, 70), w=3)
        mur = Canvas(D.gradient(450 * SS, 210 * SS, [(0, (250, 220, 170)), (0.6, (200, 210, 220)), (1, (90, 130, 170))]),
                     size=(450, 210))
        P.alp(mur, 90, 130, 220, 110, seed=2, ol=None)
        P.alp(mur, 380, 130, 200, 90, seed=3, ol=None)
        mur.rect(0, 130, 450, 210, (90, 130, 180), ol=None)
        mur.poly([(170, 160), (300, 160), (280, 182), (190, 182)], (150, 100, 60), w=2)            # boat
        mur.poly([(180, 160), (176, 120), (190, 160)], (240, 240, 250), ol=None)
        mur.rect(222, 112, 238, 160, (200, 200, 220), w=2)                                         # knight
        mur.circle(230, 104, 9, (210, 210, 230), w=2)
        mur.line([(244, 160), (252, 90)], (180, 160, 120), 3)
        P.swan(mur, 340, 166, 0.42, 1, 0.0, swim=True, bob=False)
        mur.line([(300, 164), (352, 150)], P.GOLD, 2)
        c.img.paste(mur.img, (415 * SS, 135 * SS))
        # bookshelves
        for x0, x1 in ((250, 380), (900, 1030)):
            c.rect(x0, 130, x1, 600, (120, 76, 46), w=3)
            for k, yy in enumerate(range(190, 600, 70)):
                c.rect(x0 + 8, yy - 56, x1 - 8, yy, (90, 56, 34), ol=None)
                rng = np.random.default_rng(k + x0)
                x = x0 + 10
                while x < x1 - 20:
                    bw = rng.uniform(9, 15)
                    col = ((160, 50, 50), (50, 90, 150), (70, 120, 70), (190, 150, 60), (120, 70, 130))[rng.integers(5)]
                    c.rect(x, yy - rng.uniform(36, 52), x + bw, yy, col, w=1.2)
                    x += bw + 1
                c.rect(x0, yy, x1, yy + 8, (120, 76, 46), w=1.5)
        c.rect(0, 600, W, H, (150, 96, 56), ol=None)                    # parquet
        for x in range(-200, W + 200, 60):
            c.line([(x, 600), (x - 80, H)], (126, 78, 46), 2)
        c.line([(0, 600), (W, 600)], (90, 56, 34), 3)
        c.ellipse(640, 668, 380, 40, (40, 70, 140), w=2.5)              # carpet
        c.ellipse(640, 668, 340, 30, (60, 96, 170), ol=None)
        return c.img
    return cached("library", make)


def lectern(c, x, y, glow=0.0, t=0.0):
    c.rect(x - 8, y - 110, x + 8, y, (110, 70, 44), w=2.5)
    c.rect(x - 40, y - 8, x + 40, y, (110, 70, 44), w=2.5)
    if glow > 0:
        c.glow(x, y - 130, 90 * glow + 10, 60 * glow + 8, (255, 246, 200), (232, 204, 150), steps=8)
    c.poly([(x - 60, y - 112), (x + 60, y - 136), (x + 64, y - 124), (x - 56, y - 100)], (110, 70, 44), w=2.5)
    c.poly([(x - 54, y - 116), (x, y - 128), (x + 2, y - 140), (x - 52, y - 128)], P.PAPER, w=2)
    c.poly([(x, y - 128), (x + 54, y - 140), (x + 52, y - 152), (x + 2, y - 140)],
           mix(P.PAPER, (255, 250, 200), glow), w=2)


def chandelier(c, t, x=640, y=150):
    c.line([(x, 70), (x, y - 20)], OUT, 3)
    c.ellipse(x, y, 110, 18, None, ol=P.GOLD, w=5)
    for k in range(7):
        cx = x - 100 + k * 33.3
        cy = y + 6 * math.sin(math.pi * k / 6)
        c.rect(cx - 3, cy - 22, cx + 3, cy - 4, (255, 250, 230), w=1)
        fl = 1 + 0.2 * math.sin(t * 13 + k * 2)
        c.ellipse(cx, cy - 28, 4, 7 * fl, (255, 190, 60), ol=None)
        c.ellipse(cx, cy - 27, 2, 4 * fl, (255, 250, 200), ol=None)


def castle(tl, t):
    T = tl.t
    STAMPED[0] = True
    if t < T("c_sorry"):
        return castle_gate(tl, t)
    return castle_library(tl, t)


def castle_gate(tl, t):
    T = tl.t
    c = Canvas(gate_bg().copy())
    k = ease(tl.prog("c_door", t, 0.7, 1.0))
    # warm interior through the opening door
    if k > 0:
        c.glow(640, 500, 140 * k + 4, 160 * k + 4, (255, 236, 170), (60, 40, 40), steps=8)
        if k > 0.3:
            ludwig(c, tl, t, 650, GY - 2, 1.0, -1, swim=False,
                   eyes="happy" if T("c_home") <= t < T("c_home", 1) else "open",
                   wing=0.8 if T("c_home") <= t < T("c_home", 1) else None) if T("c_home") <= t < T("c_home", 1) \
                else ludwig(c, tl, t, 650, GY - 2, 1.0, -1, swim=False)
    for side in (-1, 1):
        w = 136 * (1 - 0.85 * k)
        x0 = 640 + side * 136
        x1 = x0 - side * w
        c.poly([(x0, GY), (x0, 330 - (0 if side < 0 else 0)), (x1, 330 + 20 * k), (x1, GY)], (140, 86, 50), w=2.5)
        for j in range(4):
            xx = lerp(x0, x1, (j + 0.5) / 4)
            c.line([(xx, 340 + 10 * k), (xx, GY - 6)], (110, 66, 40), 2)
        c.circle(lerp(x0, x1, 0.85), 480, 6, P.GOLD, w=1.5)
    # the arch top over the doors
    c.ellipse(640, 330, 136, 120, None, ol=OUT, w=3)
    c.d.chord(c._box(640, 330, 134, 118), 180, 360, fill=c.c((60, 40, 40)))
    knock = 0
    for f in (0.2, 0.45):
        dt = t - T("c_door", f)
        if 0 < dt < 0.15:
            knock = 1
    resi(c, tl, t, 250, GY, 0.8, 1)
    kat(c, tl, t, "luna", 360, GY, 0.85, 1, "sit", look=(1, -0.6), eyes="happy" if T("c_late", 0.4) <= t else "open")
    kat(c, tl, t, "whiskers", 470, GY - 8 * knock, 0.85, 1, "stand", carry=True, wet=0.3, look=(1, -0.6))
    return finish(c, tl, t, 0.4)


def castle_library(tl, t):
    T = tl.t
    c = Canvas(library_bg().copy())
    chandelier(c, t)
    glow = ease(tl.prog("c_write", t, 0.5, 1.0))
    lectern(c, 760, 628, glow, t)
    if glow > 0:
        P.sparkles(c, 780, 490, t, 12, 70 * glow + 10, seed=4)
    if t >= T("c_quill"):
        u = tl.prog("c_quill", t)
        qx = 790 + 20 * math.sin(t * 9)
        qy = 440 + 8 * math.cos(t * 13)
        P.quill(c, qx, qy, 0.7)
        P.sparkles(c, qx, qy + 10, t, 6, 30, seed=7)
    happy = T("c_knight", 0.3) <= t
    ludwig(c, tl, t, 940, 628, 1.05, -1, swim=False, eyes="happy" if T("c_knight", 0.6) <= t < T("c_write") else "open")
    resi(c, tl, t, 300, 640, 0.85, 1, eyes="happy" if happy else "open")
    kat(c, tl, t, "luna", 430, 640, 0.95, 1, "sit", look=(1, -0.4), eyes="happy" if happy and tl.mouth("luna", t) < 0.1
        else "open")
    sorry = T("c_sorry") <= t < T("c_knight", 0.3)
    kat(c, tl, t, "whiskers", 580, 640, 0.95, 1, "sit", look=(1, -0.6), head_dy=8 if sorry else 0,
        eyes="happy" if T("c_knight", 0.6) <= t < T("c_write") else "open", wet=0.15)
    return finish(c, tl, t, 0.35)


# =================================================================== lake

def night_castle_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (12, 16, 48)), (0.55, (44, 50, 108)), (0.8, (76, 70, 130)),
                                               (1, (40, 46, 90))]))
        D.stars(c, 41, 160, W, 380)
        D.moon(c, 1080, 120, 46, sky=(24, 30, 72))
        for x, w, h, sd in ((160, 560, 300, 1), (600, 520, 240, 2), (1120, 600, 320, 3)):
            P.alp(c, x, 560, w, h, rock=(56, 60, 104), snow=(150, 160, 210), shade=(110, 120, 170), seed=sd,
                  ol=(30, 30, 60))
        P.hill(c, [560, 520, 540, 500, 530, 520, 560], 0, W, (26, 40, 56), base=H)
        rng = np.random.default_rng(42)
        for x in np.linspace(0, W, 50):
            P.fir_flat(c, x + rng.uniform(-10, 10), 570 + rng.uniform(-30, 10), rng.uniform(0.28, 0.4), (20, 32, 46))
        c.glow(560, 300, 340, 260, (120, 110, 150), (44, 50, 108), steps=10)
        P.castle_cliff(c, 560, 420, 0.6, night=1.0, seed=43)
        P.neuschwanstein(c, 560, 422, 0.72, lit=1.0, night=1.0, ol=(30, 30, 60))
        for x, y, s in ((380, 520, 0.5), (420, 560, 0.55), (740, 540, 0.5), (780, 580, 0.55)):
            P.fir_flat(c, x, y, s, (20, 32, 46))
        lake = D.gradient(W * SS, 120 * SS, [(0, (40, 50, 100)), (1, (20, 26, 60))])
        c.img.paste(lake, (0, 600 * SS))
        c.line([(0, 600), (W, 600)], (70, 80, 140), 2)
        return c.img
    return cached("nightcastle", make)


def balcony_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (14, 18, 52)), (0.5, (50, 56, 116)), (1, (60, 60, 120))]))
        D.stars(c, 51, 150, W, 300)
        D.moon(c, 260, 120, 40, sky=(24, 30, 72))
        for x, w, h, sd in ((700, 600, 230, 4), (1120, 560, 260, 5), (330, 400, 180, 6)):
            P.alp(c, x, 380, w, h, rock=(56, 60, 104), snow=(150, 160, 210), shade=(110, 120, 170), seed=sd,
                  ol=(30, 30, 60))
        P.hill(c, [390, 370, 386, 366, 380, 372, 390], 0, W, (26, 40, 56), base=H)
        lake = D.gradient(W * SS, 200 * SS, [(0, (40, 54, 110)), (1, (26, 34, 76))])
        c.img.paste(lake, (0, 392 * SS))
        c.line([(0, 392), (W, 392)], (80, 90, 150), 2)
        rng2 = np.random.default_rng(52)
        for k in range(16):                                   # moon path on the water
            y = 400 + k * 10
            w = 14 + k * 5
            x0 = 260 + rng2.uniform(-1, 1) * w * 0.6
            c.line([(x0 - w, y), (x0 + w * rng2.uniform(0.2, 1.0), y)], (200, 200, 184), 2)
        for x in (900, 940, 1010, 1060):                        # village lights across the lake
            c.circle(x, 384, 2.5, (255, 220, 140), ol=None)
        # a white castle tower at the left edge
        c.rect(0, 120, 100, 600, P.CASTLE_W, w=3)
        c.rect(0, 120, 20, 600, P.CASTLE_SH, ol=None)
        c.rect(40, 220, 64, 280, (255, 214, 120), w=2)
        c.ellipse(52, 220, 12, 12, (255, 214, 120), w=2)
        P._cone(c, 40, -30, 120, 80)
        # balustrade
        st, sts = (210, 206, 226), (170, 166, 196)
        c.rect(0, 560, W, 590, st, w=3)
        c.rect(0, 582, W, 590, sts, ol=None)
        for x in range(30, W, 56):
            c.poly([(x - 10, 590), (x + 10, 590), (x + 6, 610), (x + 14, 640), (x + 6, 680), (x + 10, 700),
                    (x - 10, 700), (x - 6, 680), (x - 14, 640), (x - 6, 610)], st, w=2)
        c.rect(0, 700, W, H, sts, w=3)
        return c.img
    return cached("balcony", make)


def lake(tl, t):
    T = tl.t
    STAMPED[0] = True
    if t < T("l_strudel"):
        c = Canvas(night_castle_bg().copy())
        for k in range(14):
            rng = np.random.default_rng(k)
            x, y = rng.uniform(0, W), rng.uniform(0, 300)
            tw = 0.5 + 0.5 * math.sin(t * 3 + k * 2)
            c.circle(x, y, 1 + 2 * tw, (255, 250, 220), ol=None)
        for k in range(6):
            c.line([(1080 - 50 + k * 8, 612 + k * 16), (1080 + 50 - k * 8, 612 + k * 16)], (200, 200, 180), 2.5)
        for k, (x0, y0, sp) in enumerate(((300, 650, 10.0), (420, 676, 8.0), (900, 664, -9.0))):
            x = x0 + sp * (t - T("l_open"))
            P.ripple(c, x, y0 + 2, t, 50, (150, 160, 210), seed=k * 0.3)
            P.swan(c, x, y0, 0.5, 1 if sp > 0 else -1, t, swim=True, seed=k * 1.7, tint=((120, 130, 200), 0.3))
        return finish(c, tl, t, 0.4)
    c = Canvas(balcony_bg().copy())
    for k, (x0, y0, sp) in enumerate(((560, 470, 6.0), (640, 500, 5.0), (1000, 450, -4.0))):
        x = x0 + sp * (t - T("l_strudel"))
        P.ripple(c, x, y0 + 2, t, 34, (150, 160, 210), seed=k * 0.3)
        P.swan(c, x, y0, 0.3, 1 if sp > 0 else -1, t, swim=True, seed=k * 1.7, tint=((120, 130, 200), 0.3))
    Y = 562
    c.tint = ((60, 70, 150), 0.18)
    send = t >= T("l_send")
    pu = tl.prog("l_send", t)
    bx = 720
    pop = ease(clamp(pu / 0.15)) if send else 0.0
    lid = 0.0 if pu > 0.82 else 1.0
    if pop > 0:
        P.parcel(c, bx, Y, 0.8 * pop, lid=lid, front=False)
    lean = ease(tl.prog("l_hold", t, 0.1, 0.4)) * (1 - ease(tl.prog("l_send", t, 0.0, 0.2)))
    # Luna and Whiskers: on the rail, then hop into the box
    lu = clamp((pu - 0.3) / 0.18) if send else 0.0
    wu = clamp((pu - 0.45) / 0.18) if send else 0.0
    for who, x0, u, s in (("luna", 480, lu, 0.85), ("whiskers", 600, wu, 0.85)):
        if u <= 0:
            x = x0 + (24 if who == "luna" else -6) * lean
            kat(c, tl, t, who, x, Y, s, 1, "sit", look=(1, -0.2) if t < T("l_hold") else (1, 0),
                head_dy=8 * lean if who == "luna" else 0,
                eyes="happy" if (lean > 0.5 or T(("l_truth" if who == "whiskers" else "l_strudel")) <= t <
                                 T(("l_truth" if who == "whiskers" else "l_strudel"), 1)) else "open")
        elif u < 1:
            x = lerp(x0, bx - 30 if who == "luna" else bx + 26, u)
            y = lerp(Y, Y - 30, u) + jump_y(u, 50)
            kat(c, tl, t, who, x, y, s * 0.9, 1, "leap")
        elif lid > 0.5:
            kat(c, tl, t, who, bx - 30 if who == "luna" else bx + 26, Y - 30, s * 0.82, 1, "sit", eyes="happy")
    if pop > 0:
        P.parcel(c, bx, Y, 0.8 * pop, lid=lid, back=False, label=False, stamp="RETURN TO SENDER" if pu > 0.94 else "")
    if lean > 0.5:
        D.zzz(c, 640, 420, t) if False else None
    resi(c, tl, t, 360, Y, 0.75, 1, wave=1.0 if t >= T("l_send", 0.6) else 0.0)
    ludwig(c, tl, t, 930, Y, 0.9, -1, swim=False, wing=0.9 if t >= T("l_send", 0.85) else None) \
        if t >= T("l_send", 0.85) else ludwig(c, tl, t, 930, Y, 0.9, -1, swim=False)
    c.tint = None
    if T("l_hold") <= t < T("l_send"):
        for k in range(3):                     # little hearts
            u = (t * 0.4 + k / 3) % 1.0
            hx, hy = 560 + 20 * math.sin(t * 2 + k), 440 - 80 * u
            sz = 6 * (1 - u) + 3
            c.circle(hx - sz * 0.5, hy, sz * 0.6, (240, 110, 140), ol=None)
            c.circle(hx + sz * 0.5, hy, sz * 0.6, (240, 110, 140), ol=None)
            c.poly([(hx - sz, hy + 2), (hx + sz, hy + 2), (hx, hy + sz * 1.3)], (240, 110, 140), ol=None)
    return finish(c, tl, t, 0.35)


# =================================================================== home

SILL = 546


def home_bg():
    def make():
        wall = (236, 214, 178)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, H, mix(wall, (255, 255, 255), 0.25), ol=None)
        win = Canvas(D.gradient(1000 * SS, 480 * SS, [(0, (110, 180, 240)), (1, (214, 238, 252))]), size=(1000, 480))
        # rainbow after the rain
        for k, col in enumerate(((230, 80, 80), (245, 160, 60), (250, 220, 80), (110, 200, 110), (90, 150, 230),
                                 (150, 110, 210))):
            win.arc(560, 520, 460 - k * 16, 400 - k * 16, 180, 360, col, 16)
        for x, y, s in ((160, 90, 0.9), (780, 70, 0.8)):
            D.cloud(win, x, y, s)
        for x, w, h, col in ((40, 220, 160, (200, 150, 130)), (300, 180, 210, (220, 190, 150)),
                             (520, 260, 140, (190, 160, 170)), (800, 200, 190, (210, 170, 140))):
            win.rect(x, 480 - h, x + w, 480, col, ol=None)
            win.poly([(x - 14, 480 - h), (x + w / 2, 480 - h - 60), (x + w + 14, 480 - h)], (170, 80, 64), ol=None)
            for wx in range(int(x) + 26, int(x + w) - 30, 60):
                win.rect(wx, 480 - h + 40, wx + 26, 480 - h + 74, (130, 170, 210), ol=None)
        D.tree(win, 930, 480, 1.0, leaf=(230, 140, 60))
        c.img.paste(win.img, (140 * SS, 60 * SS))
        for x0, x1 in ((50, 170), (1110, 1230)):
            c.rect(x0, 0, x1, 640, (120, 60, 70), r=10)
            for xx in range(int(x0) + 20, int(x1), 30):
                c.line([(xx, 10), (xx, 630)], (100, 48, 58), 3)
        c.rect(30, 0, 1250, 16, (150, 100, 60))
        c.rect(0, 572, W, H, mix(wall, (0, 0, 0), 0.06), ol=None)
        c.rect(130, 52, 1150, 544, None, w=10)
        c.line([(640, 60), (640, 540)], (240, 236, 230), 10, cap=False)
        c.line([(140, 300), (1140, 300)], (240, 236, 230), 10, cap=False)
        c.rect(130, 52, 1150, 544, None, ol=(240, 236, 230), w=6)
        c.rect(100, 540, 1180, 572, (250, 246, 236), r=5)
        return c.img
    return cached("home", make)


def home(tl, t):
    T = tl.t
    STAMPED[0] = True
    c = Canvas(home_bg().copy())
    bx = 640
    drop = ease(tl.prog("h_open", t, 0.3, 0.7))
    by = lerp(-160, SILL, drop ** 2)
    if drop >= 1:
        dt = t - T("h_open", 0.7)
        by = SILL - abs(math.sin(dt * 12)) * 16 * math.exp(-dt * 5)
    opened = t >= T("h_pip", 0.65)
    asleep = t >= T("h_end", 0.1)
    P.parcel(c, bx, by, 1.4, lid=1.0 if opened else 0.0, front=False)
    if opened:
        pop = ease(tl.prog("h_pip", t, 0.7, 0.95))
        lean = ease(tl.prog("h_hug", t, 0.0, 0.4))
        dy = (1 - pop) * 90 + 14 * asleep
        kat(c, tl, t, "luna", bx - 60 + 14 * lean, by - 112 + dy, 0.95, 1, "sit", head_dy=6 * lean,
            eyes="closed" if asleep else ("happy" if lean > 0.5 else "open"), look=(1, 0))
        kat(c, tl, t, "whiskers", bx + 66, by - 112 + dy, 0.95, -1, "sit",
            eyes="closed" if asleep else ("happy" if lean > 0.5 and tl.mouth("whiskers", t) < 0.1 else "open"),
            look=(-1, 0.2))
    P.parcel(c, bx, by, 1.4, lid=1.0 if opened else 0.0, back=False, label=False, stamp="RETURN TO SENDER")
    # Pip runs along the sill, opens the box, then sits on its edge
    if t >= T("h_open", 0.6):
        keys = [(T("h_open", 0.6), -60), (T("h_open", 1.0), 420), (T("h_hug"), 420), (T("h_hug", 0.6), 640)]
        if t < T("h_hug", 0.3):
            actor(c, tl, t, "pip", keys, SILL, 1.4, 1, eyes="happy" if t >= T("h_page") else "open",
                  proud=T("h_pip") <= t < T("h_pip", 0.6))
        else:
            u = tl.prog("h_hug", t, 0.3, 0.6)
            px = lerp(500, 640, u)
            py = lerp(SILL, SILL - 120 * 1.4 + 14, u) + jump_y(u, 40)
            D.mouse(c, px, py, 1.2, 1, t, mouth=tl.mouth("pip", t), eyes="closed" if asleep else "happy")
    if asleep:
        D.zzz(c, 760, 330, t)
    k = ease(tl.prog("h_end", t, 0.2, 0.5))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 44 * k, mix((236, 214, 178), (255, 250, 236), k), stroke=4 * k,
               stroke_fill=(70, 50, 60))
    return finish(c, tl, t, 0.3)


SCENE_FUNCS = {"title": title, "attic": attic, "post": post, "square": square, "village": village,
               "forest": forest, "bridge": bridge, "castle": castle, "lake": lake, "home": home}
CONTINUOUS = set()
EXTRA_CUTS = ["p_van", "p_road", "v_strudel", "c_sorry", "l_strudel"]
