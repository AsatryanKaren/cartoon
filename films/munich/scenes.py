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
        book_slab(c, x + face * fore[0] * s, y + (fore[1] - 14) * s, 0.9 * s, ang=0.08 * math.sin(t * 7))
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
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "resi":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / (14 * s))) * 10 * s if moving else kw.pop("hop", 0.0)
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


SCENE_FUNCS = {"title": title, "attic": attic, "post": post}
CONTINUOUS = set()
EXTRA_CUTS = ["p_van", "p_road"]
