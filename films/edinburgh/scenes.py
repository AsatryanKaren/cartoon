"""Scenes of "Whiskers and the Loch Ness Secret". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.edinburgh import props as P
from films.moonfish.scenes import room as moonfish_room   # read-only reuse of the home room

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "dougal": 5.5, "hamish": 6.6, "nessie": 9.1}

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


def jump_y(u, h):
    u = clamp(u)
    return -4 * h * u * (1 - u)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def shake(c, amount, t):
    """Camera shake: shift the whole picture a little."""
    if amount <= 0.3:
        return c
    dx = int(math.sin(t * 91) * amount * SS)
    dy = int(math.cos(t * 77) * amount * SS)
    img = Image.new("RGB", c.img.size, (20, 20, 30))
    img.paste(c.img, (dx, dy))
    return Canvas(img)


# ------------------------------------------------------------ characters

def body_center(pose):
    return {"sit": (6, -60), "sleep": (0, -30), "crouch": (0, -46), "leap": (10, -50)}.get(pose, (4, -56))


def puff_halo(c, x, y, s, face, pose, k, t):
    """Fur standing on end: a spiky orange halo behind the cat."""
    if k <= 0.02:
        return
    bx, by = body_center(pose)
    cx, cy = x + face * bx * s, y + by * s
    pts = []
    n = 22
    for i in range(n * 2):
        a = i * math.pi / n
        r = (62 + (30 if i % 2 == 0 else 0) * k + 3 * math.sin(t * 30 + i)) * s
        pts.append((cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r))
    c.poly(pts, D.WHISKERS["body"], w=2.5)


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, puff=0.0, cam=False, wink=False, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    puff_halo(c, x, y, s, face, pose, puff, t)
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if cam and pose == "sit":
        c.push(x, y, s, flip=face < 0)
        c.line([(4, -86), (24, -60), (40, -82)], (60, 50, 50), 2)
        P.camera(c, 26, -58, 0.7)
        c.pop()
    if wink and pose == "sit":
        pal = PAL[who]
        c.push(x, y, s, flip=face < 0)
        hx, hy = 18, -106 + kw.get("head_dy", 0.0)
        ex, ey = hx + 22, hy - 4
        c.ellipse(ex, ey, 9, 11, pal["body"], ol=None)
        c.arc(ex, ey + 2, 7, 6, 200, 340, OUT, 3)
        c.pop()


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
    elif who == "dougal":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop0 = kw.pop("hop", 0.0)
        hop = abs(math.sin(x / (10 * s))) * 6 * s if moving else hop0
        P.dougal(c, x, y, s, face, t, mouth=mouth, walk=x / (7 * s) if moving else 0.0, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def dougal(c, tl, t, x, y, s=0.9, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("dougal", t))
    wag = kw.pop("wag", None)
    if wag is None and mouth > 0.05:
        wag = math.sin(t * 14)
    P.dougal(c, x, y, s, face, t, mouth=mouth, wag=wag if wag is not None else math.sin(t * 4), **kw)


def thought_bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    if k <= 0.02:
        return
    for f, r in ((0.35, 9), (0.65, 14)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def speed_lines(c, x, y, face, n=5, ln=90, col=(255, 255, 255)):
    for k in range(n):
        yy = y - 20 - k * 16
        c.line([(x - face * (40 + 10 * (k % 2)), yy), (x - face * (40 + ln - 20 * (k % 3)), yy)], col, 3)


def dust(c, x, y, t, k, seed=0):
    if k <= 0:
        return
    rng = np.random.default_rng(seed)
    for i in range(6):
        u = (t * 2 + i / 6) % 1.0
        c.circle(x + rng.uniform(-30, 30) - 30 * u, y - 10 - 20 * u, (6 + 10 * u) * k, (226, 214, 196), ol=None)


# ================================================================== title

def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (30, 36, 92)), (0.35, (92, 76, 140)), (0.6, (226, 132, 120)),
                                               (0.75, (250, 190, 140)), (1, (250, 190, 140))]))
        D.stars(c, 6, 50, W, 220, col=(255, 240, 230))
        c.glow(980, 470, 380, 200, (255, 222, 170), (226, 132, 120), steps=12)
        # far hills of Fife across the water
        P.hill(c, [500, 488, 494, 480, 492, 486], 0, W, (120, 92, 140))
        c.rect(0, 500, W, 540, (190, 130, 140), ol=None)
        for k in range(6):
            c.line([(860 + k * 20, 506 + k * 6), (1100 - k * 20, 506 + k * 6)], (255, 214, 170), 2)
        # the castle, glowing in the dusk
        P.castle_rock(c, 820, 590, 0.82, night=0.35, lit=0.85, t=0.0, ol=(60, 44, 70), flag=False)
        # Old Town roofline below the castle
        rng = np.random.default_rng(8)
        x = 360
        while x < W:
            w = rng.uniform(50, 90)
            h = rng.uniform(60, 130)
            col = (88, 70, 104)
            c.rect(x, 620 - h, x + w, 640, col, ol=None)
            c.rect(x + 8, 620 - h - 18, x + 20, 620 - h, col, ol=None)
            for wy in range(int(620 - h + 14), 600, 26):
                for wx in range(int(x + 10), int(x + w - 10), 18):
                    if rng.random() < 0.4:
                        c.rect(wx, wy, wx + 7, wy + 10, (255, 210, 120), ol=None)
            x += w + 2
        P.st_giles(c, 560, 640, 0.42, col=(88, 70, 104), ol=None)
        # Calton Hill, where the cats sit
        c.poly([(0, H), (0, 590), (120, 574), (260, 580), (380, 610), (470, 660), (520, H)], (70, 96, 84), w=2.5)
        P.heather_patch(c, 160, 640, 260, seed=3)
        P.heather_patch(c, 360, 690, 200, seed=4)
        P.thistle(c, 440, 700, 0.9)
        P.thistle(c, 30, 640, 0.7)
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    P.goose_vee(c, -160 + 70 * t, 270 + 6 * math.sin(t), t, n=7, s=0.22, tint=((60, 40, 90), 0.5))
    c.tint = ((90, 60, 120), 0.22)
    kat(c, tl, t, "whiskers", 150, 590, 0.62, 1, "sit", look=(1, -0.5))
    kat(c, tl, t, "luna", 236, 594, 0.6, 1, "sit", look=(1, -0.5), tail=math.sin(t * 1.5))
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(W / 2, 74 - 30 * (1 - k), "Whiskers and the", 44, mix((40, 40, 100), (255, 246, 236), k),
           stroke=3 * k, stroke_fill=(60, 40, 90))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 148, "LOCH NESS SECRET", 26 + 50 * k2, mix((40, 40, 100), (255, 255, 255), k2), stroke=5 * k2,
           stroke_fill=(30, 70, 70))
    return c


# ==================================================================== tin

WIN_BOX = (760, 110, 1080, 374)


def window_overlay(c, tl, t, geese_k):
    """Geese flying across the room's window (drawn clipped to the glass)."""
    if geese_k <= 0 or geese_k >= 1:
        return
    x0, y0, x1, y1 = WIN_BOX
    bg = moonfish_room(False)
    sub = Canvas(bg.crop((x0 * SS, y0 * SS, x1 * SS, y1 * SS)).copy(), size=(x1 - x0, y1 - y0))
    gx = lerp(-80, 520, geese_k)
    P.goose_vee(sub, gx, 120, t, n=7, s=0.24)
    c.img.paste(sub.img, (x0 * SS, y0 * SS))
    c.rect(756, 106, 1084, 374, None, w=8)
    c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
    c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
    c.rect(740, 370, 1100, 392, (255, 250, 240), r=4)


def tin(tl, t):
    T = tl.t
    c = Canvas(moonfish_room(False).copy())
    gk = tl.prog("i_geese", t, 0.0, 1.0) * 0.55 + tl.prog("i_camera", t, 0.0, 1.0) * 0.45
    if T("i_geese") <= t < T("i_care"):
        window_overlay(c, tl, t, gk)
    eating = t < T("i_narr", 0.95)
    empty = t >= T("i_narr", 0.95)
    tx, ty = 560, 640
    # the tin
    P.tin(c, tx, ty, 1.3, lid=1.0)
    lid_lifted = T("i_lid") <= t
    if not lid_lifted:
        P.tin_lid_leaning(c, tx + 150, ty + 4, 1.0)
    # Whiskers
    leap0 = T("i_end", 0.25)
    if t < leap0:
        if T("i_gone") <= t < T("i_lid", 0.3):
            kat(c, tl, t, "whiskers", 330, 680, 1.2, 1, "sleep")                 # flat out: life is over
        else:
            hd = 10 if T("i_empty") <= t < T("i_gone") else 0
            look = (1, 0.6) if hd else ((1, -1) if T("i_geese") <= t < T("i_care") else (1, 0))
            eyes = "wide" if T("i_life") <= t < T("i_north") else "open"
            m = None
            if eating:
                m = 0.25 + 0.25 * math.sin(t * 14)
            kw = {} if m is None else {"mouth": m}
            kat(c, tl, t, "whiskers", 380, 680, 1.2, 1, "sit", head_dy=hd, look=look, eyes=eyes, **kw)
            if eating:
                bite = (t * 0.7) % 1.0
                P.shortbread(c, 380 + 66, 680 - 116, 1.1, ang=0.4, bite=bite)
                for k in range(3):
                    u = (t * 1.6 + k / 3) % 1.0
                    c.circle(440 + 10 * k, 570 + 100 * u, 3, P.SHORTBREAD_D, ol=None)
            if T("i_life") <= t < T("i_north"):
                P.sparkles(c, 430, 500, t, n=8, r=70, seed=2)
    else:
        u = tl.prog("i_end", t, 0.25, 0.75)
        kat(c, tl, t, "whiskers", lerp(380, 880, u), lerp(680, 370, u) + jump_y(u, 90), 0.8, 1,
            "leap" if u < 0.95 else "stand")
    # Luna
    lx, ly = 800, 680
    cam = t >= T("i_care", 0.95)
    if t < T("i_end", 0.0):
        hold = T("i_lid", 0.2) <= t < T("i_north")
        look = (-1, -1) if T("i_geese") <= t < T("i_care") else (-1, 0)
        if hold:
            look = (-1, -0.3)
        kat(c, tl, t, "luna", lx, ly, 1.15, -1, "sit", look=look, cam=cam)
        if hold:
            P.tin_lid_leaning(c, lx - 86, ly - 36, 0.7)
    else:
        u = tl.prog("i_end", t, 0.0, 0.5)
        kat(c, tl, t, "luna", lerp(lx, 980, u), lerp(ly, 370, u) + jump_y(u, 110), 0.8, 1,
            "leap" if u < 0.95 else "stand")
    if lid_lifted and t >= T("i_north"):
        P.tin_lid_leaning(c, tx + 150, ty + 4, 1.0)
    # Pip, with his camera
    px, py = 660, 700
    if t >= T("i_north"):
        keys = [(T("i_north"), 1100), (T("i_north", 0.4), 660)]
    else:
        keys = [(0, 1100)]
    if t >= T("i_north"):
        x = actor(c, tl, t, "pip", keys, py, 1.6, -1, proud=T("i_north", 0.4) <= t < T("i_north", 1.0))
        handed = t >= T("i_care", 0.95)
        if not handed:
            camk = tl.prog("i_care", t, 0.3, 0.95)
            if t >= T("i_camera", 0.5):
                cx_ = lerp(x - 20, lx - 10, ease(camk))
                cy_ = lerp(py - 50, ly - 170, ease(camk)) + jump_y(camk, 30)
                P.camera(c, cx_, cy_, 1.0, flash=max(0.0, 1 - abs(tl.prog("i_care", t, 0.0, 1.0) - 0.9) * 12))
    # the contest close-up
    k = ease(tl.prog("i_read", t, 0.0, 0.12)) * (1 - ease(tl.prog("i_life", t, 0.7, 1.0)))
    if T("i_read") <= t < T("i_north"):
        P.lid_card(c, 640, 270, k, t)
    return finish(c, tl, t, 0.35)


# ================================================================== geese

def fly_sky():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (110, 170, 230)), (0.6, (196, 226, 246)), (1, (226, 240, 240))]))
        return c.img
    return cached("fly_sky", make)


def flying(tl, t):
    T = tl.t
    c = Canvas(fly_sky().copy())
    for k, (cx, cy, sc, sp) in enumerate(((200, 120, 1.0, 30), (700, 80, 0.8, 24), (1100, 170, 1.2, 36),
                                         (450, 230, 0.7, 20))):
        x = (cx - sp * t) % (W + 400) - 200
        D.cloud(c, x, cy, sc)
    # rolling hills scroll below
    off = t * 60
    ys = [560 + 30 * math.sin((i * 80 + off) / 180) + 16 * math.sin((i * 80 + off) / 70) for i in range(18)]
    P.hill(c, ys, 0, W, (128, 164, 150), ol=None)
    off2 = t * 150
    xs = np.linspace(0, W, 20)
    ys2 = [640 + 24 * math.sin((x + off2) / 150) + 10 * math.sin((x + off2) / 61) for x in xs]
    P.hill(c, ys2, 0, W, (110, 160, 90), ol=(70, 110, 64))
    # stone walls and sheep on the near hills
    for k in range(8):
        wx = (k * 220 - off2) % (W + 220) - 110
        wy = 640 + 24 * math.sin((wx + off2) / 150) + 10 * math.sin((wx + off2) / 61)
        c.line([(wx - 60, wy + 30), (wx + 60, wy + 60)], (170, 170, 160), 4)
        sx = wx + 70
        sy = wy + 50
        c.ellipse(sx, sy, 12, 8, (250, 250, 246), w=1.5)
        c.circle(sx + 10, sy - 2, 4, (60, 60, 60), ol=None)
    # the skein of geese ahead
    P.goose_vee(c, 1120 + 10 * math.sin(t * 0.7), 150, t, n=7, s=0.3)
    # Luna's goose
    lgx, lgy = 820 + 20 * math.sin(t * 0.8), 300 + 10 * math.sin(t * 1.6)
    P.goose(c, lgx, lgy, 1.2, 1, t, part="back", seed=1.0)
    kat(c, tl, t, "luna", lgx - 18, lgy - 4, 0.55, 1, "crouch", look=(1, -0.3), cam=False)
    P.goose(c, lgx, lgy, 1.2, 1, t, part="front", seed=1.0)
    # Whiskers' goose: lower, working harder, sagging
    dip = math.sin(math.pi * tl.prog("g_dip", t, 0.15, 0.85)) if T("g_dip") <= t < T("g_haar") else 0.0
    wgx, wgy = 400 + 14 * math.sin(t * 0.9), 420 + 14 * math.sin(t * 2.3) + 160 * dip
    P.goose(c, wgx, wgy, 1.25, 1, t, part="back", seed=0.0, carry=True)
    eyes = "wide" if dip > 0.1 or T("g_low") <= t < T("g_dip") else "open"
    kat(c, tl, t, "whiskers", wgx - 20, wgy - 2, 0.6, 1, "crouch", eyes=eyes, look=(0.5, 1 if dip > 0.1 else 0))
    P.goose(c, wgx, wgy, 1.25, 1, t, part="front", seed=0.0, carry=True)
    if dip > 0.3:
        for k in range(3):
            c.line([(wgx - 60 + 40 * k, wgy - 120), (wgx - 60 + 40 * k, wgy - 160 - 30 * dip)], (255, 255, 255), 3)
    return finish(c, tl, t, 0.35)


def arthurs_seat_bg():
    """Dawn view from the top of Arthur's Seat over Edinburgh."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (150, 180, 220)), (0.45, (250, 214, 190)), (0.62, (252, 236, 210)),
                                               (1, (252, 236, 210))]))
        c.glow(1080, 380, 260, 150, (255, 246, 220), (250, 220, 196), steps=10)
        # the Firth of Forth and Fife beyond
        P.hill(c, [372, 360, 366, 356, 368, 362], 0, W, (176, 170, 196))
        c.rect(0, 380, W, 420, (200, 210, 226), ol=None)
        # New Town and the Old Town ridge
        rng = np.random.default_rng(5)
        x = 0
        while x < W:
            w = rng.uniform(40, 80)
            h = rng.uniform(30, 70)
            col = mix((170, 150, 150), (140, 120, 130), rng.uniform(0, 1))
            c.rect(x, 470 - h, x + w, 480, col, ol=None)
            x += w + 1
        # Scott Monument
        c.push(470, 480, 0.5)
        c.poly([(-30, 0), (-30, -120), (-14, -200), (0, -330), (14, -200), (30, -120), (30, 0)], (110, 96, 104),
               ol=None)
        c.pop()
        P.castle_rock(c, 760, 520, 0.6, t=0.0, ol=(80, 70, 80))
        x = 860
        while x < 1240:
            w = rng.uniform(46, 80)
            h = rng.uniform(70, 120)
            P.tenement(c, x, 540, w, h, mix((176, 156, 140), (150, 134, 126), rng.uniform(0, 1)), seed=int(x),
                       ol=(90, 80, 90), door=False)
            x += w + 2
        P.st_giles(c, 1010, 540, 0.36, ol=(90, 80, 90))
        P.hill(c, [560, 540, 548, 536, 552], 400, W, (120, 150, 110))
        # the crag of Arthur's Seat, foreground
        c.poly([(0, H), (0, 560), (80, 534), (200, 522), (330, 530), (450, 560), (560, 610), (660, 680), (700, H)],
               (120, 108, 100), w=2.5)
        c.poly([(0, 600), (80, 572), (200, 560), (330, 566), (440, 590), (520, 630), (560, 680), (0, 690)],
               (110, 150, 90), ol=None)
        for x, y in ((90, 600), (240, 590), (400, 640)):
            for k in range(5):
                c.circle(x + k * 12 - 24, y - abs(k - 2) * 6, 13, (90, 120, 70), w=1.5)
                c.circle(x + k * 12 - 24, y - abs(k - 2) * 6 - 6, 3.5, (250, 210, 60), ol=None)   # gorse
        for px in (220, 520):
            c.rect(px - 3, 470, px + 3, 545 if px == 220 else 600, (140, 130, 120), w=2)
        c.rect(196, 520, 244, 548, (170, 160, 150), w=2)                                       # summit pillar
        return c.img
    return cached("aseat", make)


def haar_fog():
    return cached("haar", lambda: P.fog_layer(seed=3, density=1.3))


def landing(tl, t):
    T = tl.t
    c = Canvas(arthurs_seat_bg().copy())
    # geese glide down onto the hill
    u = tl.prog("g_land", t, 0.0, 0.75)
    gx = lerp(-120, 330, ease(u))
    gy = lerp(260, 520, ease(u))
    landed = t >= T("g_land", 0.75)
    hop = tl.prog("g_land", t, 0.8, 1.0)
    lk = ease(hop)
    for k, (dx, dy, who) in enumerate(((0, 0, "whiskers"), (170, -20, "luna"))):
        away = ease(tl.prog("g_reveal", t, 0.0, 0.6))
        x = gx + dx + 900 * away
        y = (gy + dy if not landed else 520 + dy + 0) - 380 * away
        flap_away = away > 0
        flap = None if (not landed or flap_away) else 1.2
        P.goose(c, x, y, 1.0, 1, t, part="back", seed=k, flap=flap)
        if t < T("g_land", 0.8):
            kat(c, tl, t, who, x - 16, y - 2, 0.5, 1, "crouch")
        P.goose(c, x, y, 1.0, 1, t, part="front", seed=k, flap=flap)
    if t >= T("g_land", 0.8):
        rev = T("g_reveal") <= t
        look = (1, -0.3) if rev else (0, 0)
        kat(c, tl, t, "whiskers", lerp(314, 120, lk), lerp(518, 560, lk) + jump_y(lk, 40), 0.75, 1,
            "stand" if lk >= 1 else "leap", look=look)
        kat(c, tl, t, "luna", lerp(484, 330, lk), lerp(498, 540, lk) + jump_y(lk, 50), 0.75, 1,
            "stand" if lk >= 1 else "leap", look=look, eyes="wide" if T("g_wow") <= t < T("g_end") else "open")
    fk = 1.0 - ease(tl.prog("g_reveal", t, 0.05, 0.8))
    P.apply_fog(c, haar_fog(), fk)
    if t < T("g_reveal", 0.3):
        # drifting wisps in front for movement
        for k in range(4):
            x = (k * 380 + 30 * t) % (W + 400) - 200
            D.cloud(c, x, 470 + 60 * k % 200, 2.0, (238, 238, 240))
    return finish(c, tl, t, 0.4)


def geese(tl, t):
    if t < tl.t("g_haar"):
        return flying(tl, t)
    return landing(tl, t)


# =================================================================== mile

MILE_W = 2700
GROUND = 620


def mile_bg():
    def make():
        c = Canvas(D.gradient(MILE_W * SS, H * SS, [(0, (150, 190, 230)), (0.7, (220, 232, 240)), (1, (220, 232, 240))]),
                   size=(MILE_W, H))
        for x, y, s in ((300, 90, 0.9), (1100, 60, 1.1), (1900, 110, 0.8), (2500, 70, 1.0)):
            D.cloud(c, x, y, s)
        # the castle at the top of the street, seen through the gap
        P.castle_rock(c, 2420, 470, 0.6, t=0.0)
        rng = np.random.default_rng(12)
        cols = [(196, 176, 150), (176, 160, 146), (204, 186, 160), (166, 150, 140), (188, 164, 140), (210, 196, 176)]
        x = -20
        k = 0
        specials = {}
        while x < 2160:
            w = rng.uniform(150, 210)
            h = rng.uniform(330, 420)
            shop = None
            if 1060 < x + w / 2 < 1260 and "shop" not in specials:
                shop = ("TABLET & TOFFEE", (40, 96, 70))
                specials["shop"] = x
            elif 300 < x < 500 and "s2" not in specials:
                shop = ("TARTAN WEAVERS", (130, 40, 50))
                specials["s2"] = x
            elif 1800 < x < 2000 and "s3" not in specials:
                shop = ("SHORTBREAD", (40, 60, 120))
                specials["s3"] = x
            if 1400 < x < 1660:
                x = 1700           # St Giles stands back in its own square
                continue
            P.tenement(c, x, GROUND, w, h, cols[k % len(cols)], seed=k, gable=(k % 3 == 1), shop=shop,
                       door=not shop)
            x += w + 4
            k += 1
        P.st_giles(c, 1560, GROUND, 1.0)
        c.rect(1414, GROUND - 160, 1700, GROUND, P.STONE_SH, w=2.5)
        for wx in range(1440, 1690, 60):
            c.poly([(wx, GROUND - 30), (wx, GROUND - 120), (wx + 15, GROUND - 140), (wx + 30, GROUND - 120),
                    (wx + 30, GROUND - 30)], (80, 90, 130), w=2)
        P.close_arch(c, 900, GROUND, "Advocate's Close")
        # pavement + cobbles
        c.rect(0, GROUND, MILE_W, GROUND + 18, (180, 176, 170), w=2)
        c.rect(0, GROUND + 18, MILE_W, H, (130, 124, 120), ol=None)
        for row, y in enumerate(range(GROUND + 26, H, 18)):
            for xx in range(-20 + (row % 2) * 20, MILE_W, 40):
                c.rect(xx + 2, y, xx + 36, y + 14, mix((150, 144, 138), (118, 112, 110), (xx * 7 % 13) / 13),
                       ol=(96, 90, 92), w=1.5, r=5)
        # lamp posts + flags
        for lx in (240, 1300, 2050):
            c.rect(lx - 4, GROUND - 220, lx + 4, GROUND + 6, (40, 44, 50), ol=None)
            c.poly([(lx - 16, GROUND - 220), (lx + 16, GROUND - 220), (lx + 10, GROUND - 252), (lx - 10, GROUND - 252)],
                   (250, 236, 180), w=2)
        for fx in (700, 1900):
            P.saltire(c, fx, GROUND - 260, 1.0, 0.0, pole=40)
        return c.img
    return cached("mile", make)


def mile(tl, t):
    T = tl.t
    s0 = tl.scenes["mile"][0]
    camx = smooth(t, [(s0, 0), (T("m_hello"), 300), (T("m_run", 0.2), 300), (T("m_run", 1.0), 1060)], r=0.4)
    c = view(mile_bg(), camx)
    c.push(-camx, 0)
    # badger piper
    P.badger_piper(c, 560, GROUND + 20, 0.85, 1, t)
    # Dougal pops out of the close
    dk = tl.prog("m_hello", t, 0.0, 0.25)
    zoom_on = T("m_zoom") <= t < T("m_zoom", 0.92)
    lookx = -1
    if t >= T("m_hello"):
        if t < T("m_run", 0.3):
            dx = lerp(900, 980, ease(dk))
            dougal(c, tl, t, dx, GROUND + 40 + jump_y(dk, 30), 0.95, -1,
                   eyes="wide" if zoom_on else "open")
            if T("m_tablet", 0.3) <= t < T("m_eat", 0.85):
                P.tablet_bag(c, 925, GROUND + 44, 0.9)
        else:
            u = tl.prog("m_run", t, 0.3, 1.0)
            actor(c, tl, t, "dougal", [(T("m_run", 0.3), 980), (T("m_run", 1.0), 1700)], GROUND + 40, 0.95)
    # cats
    wx_keys = [(s0, -150), (T("m_open", 0.9), 640)]
    lx_keys = [(s0, -20), (T("m_open", 0.95), 780)]
    if t < T("m_eat"):
        actor(c, tl, t, "whiskers", wx_keys, GROUND + 50, 0.9, 1, eyes="wide" if T("m_tablet") <= t else "open")
    elif t < T("m_zoom"):
        u = tl.prog("m_eat", t, 0.0, 0.3)
        x = lerp(640, 860, ease(u))
        chew = tl.prog("m_eat", t, 0.3, 0.85)
        kat(c, tl, t, "whiskers", x, GROUND + 50, 0.9, 1, "crouch" if 0 < chew < 1 else "stand",
            mouth=0.3 + 0.3 * math.sin(t * 16) if 0 < chew < 1 else 0.0,
            eyes="wide" if chew >= 1 else "happy")
        if chew > 0.85:
            tremble = math.sin(t * 60) * 2
            c.line([(x - 70, GROUND - 40 + tremble), (x - 90, GROUND - 60)], (255, 255, 255), 3)
            c.line([(x + 70, GROUND - 40), (x + 90, GROUND - 60 + tremble)], (255, 255, 255), 3)
    elif t < T("m_calm"):
        # sugar rush: zooming up and down the street
        u = tl.prog("m_zoom", t, 0.0, 0.92)
        if u < 1:
            ph = u * 3.0
            leg = int(ph)
            f = ph - leg
            a, b = (380, 1260) if leg % 2 == 0 else (1260, 380)
            x = lerp(a, b, ease(f))
            face = 1 if b > a else -1
            kat(c, tl, t, "whiskers", x, GROUND + 50, 0.9, face, "walk", walk=t * 40, eyes="wide", mouth=0.6)
            if 0.1 < f < 0.9:
                speed_lines(c, x, GROUND + 50, face)
                dust(c, x - face * 50, GROUND + 50, t, 1.0, seed=leg)
            lookx = 1 if x > 780 else -1
        else:
            kat(c, tl, t, "whiskers", 640, GROUND + 50, 0.9, 1, "stand", eyes="wide", squash=0.8)
    elif t < T("m_run"):
        jit = math.sin(t * 70) * 3
        kat(c, tl, t, "whiskers", 640 + jit, GROUND + 50, 0.9, 1, "stand", eyes="wide", head_dy=math.sin(t * 50) * 2)
    else:
        u = tl.prog("m_run", t, 0.0, 0.5)
        x = lerp(640, 1800, ease(u))
        kat(c, tl, t, "whiskers", x, GROUND + 50, 0.9, 1, "walk", walk=t * 40, eyes="wide", mouth=0.5)
        speed_lines(c, x, GROUND + 50, 1)
    if t < T("m_run", 0.35):
        luna_look = (lookx, 0) if zoom_on else (1, 0)
        actor(c, tl, t, "luna", lx_keys, GROUND + 56, 0.9, 1 if not (zoom_on and lookx < 0) else -1,
              look=luna_look)
    else:
        actor(c, tl, t, "luna", [(T("m_run", 0.35), 780), (T("m_run", 1.0), 1640)], GROUND + 56, 0.9)
    c.pop()
    return finish(c, tl, t, 0.45)


# ================================================================= castle

def castle_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 176, 230)), (0.55, (206, 228, 244)), (1, (206, 228, 244))]))
        for x, y, s in ((200, 100, 1.0), (900, 70, 0.8), (1150, 150, 0.7)):
            D.cloud(c, x, y, s)
        # the Firth of Forth and Fife
        P.hill(c, [300, 290, 296, 286, 294], 0, W, (150, 160, 190))
        c.rect(0, 310, W, 350, (150, 190, 220), ol=None)
        # New Town rows and Princes Street Gardens
        P.hill(c, [350, 346, 352], 0, W, (176, 166, 160))
        rng = np.random.default_rng(4)
        for row, y in enumerate((376, 404, 432)):
            x = -10 + row * 17
            while x < W:
                w = rng.uniform(40, 70)
                col = mix((200, 186, 170), (170, 156, 150), rng.uniform(0, 1))
                c.rect(x, y - 26, x + w, y, col, ol=(120, 110, 110), w=1.5)
                c.poly([(x, y - 26), (x + w, y - 26), (x + w - 6, y - 36), (x + 6, y - 36)], (110, 116, 130),
                       ol=(120, 110, 110), w=1.5)
                for wx in range(int(x + 6), int(x + w - 6), 12):
                    c.rect(wx, y - 20, wx + 5, y - 10, (90, 100, 130), ol=None)
                x += w + 3
        c.rect(0, 440, W, 520, (110, 160, 96), ol=None)
        for x in range(20, W, 60):
            r = 22 + (x * 7 % 9)
            c.circle(x, 470 + (x % 3) * 10, r, (80, 130, 76), w=2)
        # the Scott Monument, a Gothic rocket
        c.push(420, 470, 0.8)
        c.poly([(-36, 0), (-36, -110), (-20, -180), (-10, -260), (0, -330), (10, -260), (20, -180), (36, -110),
                (36, 0)], (120, 104, 100), w=2.5)
        for y in (-110, -180, -250):
            c.line([(-30, y), (30, y)], (90, 76, 80), 3)
        c.poly([(-14, -20), (-14, -80), (0, -96), (14, -80), (14, -20)], (60, 60, 80), ol=None)
        c.pop()
        # castle wall: the battlement where the gun stands
        c.rect(0, 560, W, 610, (178, 160, 140), w=2.5)
        for y in range(564, 610, 24):
            for x in range(-20 + (y // 26 % 2) * 30, W, 60):
                c.rect(x, y, x + 56, y + 24, mix((178, 160, 140), (150, 134, 122), ((x * 3 + y) % 7) / 7),
                       ol=(130, 116, 108), w=1.5)
        for x in range(0, W, 120):
            c.rect(x, 530, x + 70, 560, (178, 160, 140), w=2.5)
        # the castle itself: a stone tower and gatehouse on the left
        c.rect(0, 120, 220, 610, (170, 152, 134), w=2.5)
        for bx in range(0, 220, 30):
            c.rect(bx, 96, bx + 18, 120, (170, 152, 134), w=2)
        for wy in (180, 300, 420):
            c.poly([(80, wy + 60), (80, wy + 16), (100, wy), (120, wy + 16), (120, wy + 60)], (60, 60, 80), w=2)
        for y in range(140, 600, 40):
            c.line([(4, y), (216, y)], (150, 134, 120), 2, cap=False)
        P.saltire(c, 160, 96, 1.4, 0.0, pole=70)
        # gun platform
        c.rect(840, 600, 1100, 640, (150, 136, 124), w=2.5)
        c.rect(0, 610, W, H, (164, 156, 146), ol=None)
        for y in range(620, H, 34):
            c.line([(0, y), (W, y)], (140, 132, 124), 2, cap=False)
        P.time_ball_sign(c, 1180, 670)
        return c.img
    return cached("castle", make)


def castle(tl, t):
    T = tl.t
    c = Canvas(castle_bg().copy())
    gun_t = T("c_gun", 0.12)
    recoil = math.exp(-(t - gun_t) * 6) if t >= gun_t else 0.0
    P.cannon(c, 960, 604, 1.1, recoil=recoil)
    if t >= gun_t:
        P.smoke_puff(c, 960 + 150, 534, clamp((t - gun_t) / 2.5), 1.6, seed=3)
        fl = clamp(1 - (t - gun_t) * 6)
        if fl > 0:
            c.glow(1110, 534, 120 * fl, 80 * fl, (255, 250, 210), (255, 200, 120), steps=6)
    gunning = T("c_gun") <= t < T("c_daily")
    # Dougal and Luna
    up = T("c_gun", 0.15) <= t < T("c_gun", 0.8)
    look_up = (0.6, -1) if up else (1, 0)
    dougal(c, tl, t, 360, 700, 1.0, 1, eyes="wide" if gunning else ("happy" if t >= T("c_end") else "open"),
           hop=abs(math.sin(t * 10)) * 8 if t >= T("c_end") else 0.0)
    kat(c, tl, t, "luna", 540, 700, 0.95, 1, "sit", look=look_up, eyes="wide" if gunning and not up else
        ("happy" if t >= T("c_end") else "open"))
    # Whiskers: launched by the boom, lands hugging the barrel
    wx, wy = 760, 700
    if t < gun_t:
        kat(c, tl, t, "whiskers", wx, wy, 0.95, -1 if t < T("c_quiet", 1.0) else 1, "sit",
            look=(-1, 0) if t < T("c_quiet", 1.0) else (1, 0))
    elif t < T("c_gun", 0.45):
        u = (t - gun_t) / (T("c_gun", 0.45) - gun_t)
        y = lerp(wy, -260, ease(u * 1.2))
        kat(c, tl, t, "whiskers", wx + 40 * u, y, 0.95, 1, "leap", eyes="wide", mouth=0.9, puff=1.0)
    elif t < T("c_gun", 0.86):
        u = tl.prog("c_gun", t, 0.72, 0.86)
        if u > 0:
            kat(c, tl, t, "whiskers", 1040, lerp(-160, 534, u ** 2), 0.85, -1, "leap", eyes="wide", puff=1.0)
    else:
        land = t - T("c_gun", 0.86)
        sq = 1 - 0.25 * math.exp(-land * 6) * abs(math.cos(land * 18))
        settled = t >= T("c_purpose")
        puff = 0.0 if settled else max(0.25, 1 - land * 0.5)
        if not settled:
            kat(c, tl, t, "whiskers", 1040, 538, 0.85, -1, "crouch", eyes="wide", puff=puff, squash=sq,
                look=(0, 0.5))
        else:
            kat(c, tl, t, "whiskers", 1040, 538, 0.85, -1, "sit", eyes="happy" if tl.mouth("whiskers", t) < 0.1
                else "open", look=(-1, 0))
    if T("c_gun", 0.12) <= t < T("c_gun", 0.4):
        c.text(1100, 420, "BOOM!", 90, (255, 230, 90), stroke=6, stroke_fill=(140, 40, 30))
    amt = 14 * math.exp(-(t - gun_t) * 3) if t >= gun_t else 0.0
    c = shake(c, amt, t)
    return finish(c, tl, t, 0.45)


# ================================================================== bobby

def bobby_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (176, 196, 214)), (0.6, (226, 230, 230)), (1, (226, 230, 230))]))
        for x, y, s in ((250, 100, 1.0), (1000, 80, 1.2)):
            D.cloud(c, x, y, s, (246, 246, 248))
        # kirkyard trees
        for x, y, s in ((120, 520, 1.2), (1180, 520, 1.3), (760, 470, 0.9)):
            D.tree(c, x, y, s, leaf=(90, 140, 90), trunk=(110, 80, 60))
        P.kirk(c, 840, 520, 0.95)
        # kirkyard: grass and gravestones behind the railings
        c.rect(0, 500, W, 600, (110, 150, 96), ol=None)
        rng = np.random.default_rng(9)
        for k in range(16):
            x = 40 + k * 80 + rng.uniform(-20, 20)
            y = 540 + rng.uniform(-20, 30)
            P.gravestone(c, x, y, rng.uniform(30, 46), rng.uniform(46, 76),
                         mix((160, 160, 156), (130, 128, 124), rng.uniform(0, 1)), kind=k % 3)
        # a dog's little grave with flowers
        P.gravestone(c, 990, 580, 34, 44, (190, 120, 110), kind=0)
        c.text(990, 556, "BOBBY", 9, (250, 230, 200))
        for dx in (-14, 0, 14):
            D.flower(c, 990 + dx, 590, (230, 80, 80), 0.6)
        P.iron_railing(c, 0, W, 610, 74)
        # pavement + cobbles
        c.rect(0, 610, W, H, (170, 164, 156), ol=None)
        for y in range(630, H, 30):
            c.line([(0, y), (W, y)], (146, 140, 134), 2, cap=False)
        # Greyfriars Bobby on his pillar
        P.bobby_statue(c, 250, 690, 1.15)
        return c.img
    return cached("bobby", make)


def memory_bubble(c, tl, t, k):
    """A sepia picture: Bobby lying by his master's grave as the seasons pass."""
    if k <= 0.02:
        return
    cx, cy, rx, ry = 860, 230, 250 * k, 150 * k
    sep, sep_d = (236, 214, 176), (150, 110, 80)
    c.ellipse(cx, cy, rx + 8, ry + 8, (255, 250, 240), w=3)
    c.ellipse(cx, cy, rx, ry, sep, ol=None)
    if k < 0.9:
        return
    u = tl.prog("b_story", t, 0.0, 1.0)
    c.push(cx, cy + 70, 1.0)
    c.line([(-200, 0), (200, 0)], sep_d, 3)
    P.gravestone(c, 40, 0, 40, 70, (210, 186, 150), ol=sep_d)
    P.dougal(c, -20, 0, 0.6, 1, t, eyes="closed", sit=False, bonnet=False, wag=0.0, ol=sep_d,
             col=((196, 170, 130), (170, 140, 104), (220, 200, 160)))
    # seasons: snow, then falling leaves, then sun
    rng = np.random.default_rng(4)
    season = int(u * 3) % 3
    for i in range(14):
        px = rng.uniform(-200, 200)
        py = ((t * 30 + rng.uniform(0, 200)) % 200) - 210
        if abs(px) < 220 * math.sqrt(max(0.0, 1 - (py + 70) ** 2 / 150 ** 2)):
            if season == 0:
                c.circle(px, py, 3, (255, 255, 255), ol=None)
            elif season == 1:
                c.ellipse(px, py, 5, 3, (200, 120, 60), ol=None)
    if season == 2:
        c.circle(130, -150, 22, (250, 220, 150), ol=None)
    c.text(0, -170, ["winter", "autumn", "summer"][season] + "...", 18, sep_d)
    c.pop()


def bobby(tl, t):
    T = tl.t
    c = Canvas(bobby_bg().copy())
    s0 = tl.scenes["bobby"][0]
    leaving = t >= T("b_go", 0.15)
    # Dougal sits by the statue, copying Bobby's pose
    dougal(c, tl, t, 430, 700, 0.95, -1 if t < T("b_friend") else 1, sit=True,
           eyes="closed" if T("b_story", 0.3) <= t < T("b_friend") else "open")
    if leaving:
        u = tl.prog("b_go", t, 0.15, 1.0)
        gx = lerp(1400, 600, ease(min(1, u * 2))) if u < 0.5 else lerp(600, 1500, ease((u - 0.5) * 2))
        gy = lerp(300, 610, ease(min(1, u * 2))) if u < 0.5 else lerp(610, 120, ease((u - 0.5) * 2))
        face = -1 if u < 0.5 else 1
        for k, (dx, who) in enumerate(((0, "luna"), (180, "whiskers"))):
            x, y = gx + dx * face, gy - 10 * k
            P.goose(c, x, y, 1.0, face, t, part="back", seed=k)
            if u >= 0.5:
                kat(c, tl, t, who, x - face * 16, y - 2, 0.5, face, "crouch")
            P.goose(c, x, y, 1.0, face, t, part="front", seed=k)
        if u < 0.5:
            kat(c, tl, t, "luna", 600, 700, 0.9, 1, "sit", look=(1, -0.5))
            kat(c, tl, t, "whiskers", 760, 700, 0.9, -1, "sit", look=(1, -0.5))
    else:
        sad = T("b_story", 0.5) <= t < T("b_lunch")
        kat(c, tl, t, "luna", 600, 700, 0.9, -1, "sit", look=(-1, -0.3), head_dy=6 if sad else 0,
            eyes="closed" if T("b_friend") <= t < T("b_friend", 0.5) else "open")
        kat(c, tl, t, "whiskers", 760, 700, 0.9, -1, "sit", look=(-1, 0))
    k = ease(tl.prog("b_story", t, 0.0, 0.15)) * (1 - ease(tl.prog("b_friend", t, 0.6, 1.0)))
    if T("b_story") <= t < T("b_lunch"):
        memory_bubble(c, tl, t, k)
    glint = tl.prog("b_wait", t, 0.3, 1.0) if T("b_wait", 0.3) <= t < T("b_go") else 0.0
    if glint > 0:
        P.sparkles(c, 250 + 30, 690 - 300, t, n=6, r=30, seed=3, col=(255, 236, 160))
    return finish(c, tl, t, 0.45)


# ============================================================== highlands

HL_W = 2900
PATH = 650


def highlands_bg():
    def make():
        c = Canvas(D.gradient(HL_W * SS, H * SS, [(0, (150, 180, 214)), (0.5, (220, 220, 232)), (1, (220, 220, 232))]),
                   size=(HL_W, H))
        for x, y, s in ((300, 110, 1.2), (1100, 80, 1.0), (1800, 130, 1.3), (2600, 90, 1.1)):
            D.cloud(c, x, y, s, (246, 246, 250))
        # misty mountain ranges
        rng = np.random.default_rng(2)
        for layer, (base, amp, col) in enumerate(((380, 150, (170, 176, 204)), (420, 120, (146, 150, 186)),
                                                  (460, 90, (120, 122, 160)))):
            ys = [base - amp * abs(math.sin(i * 0.9 + layer * 2.1)) - rng.uniform(0, 30) for i in range(26)]
            P.hill(c, ys, 0, HL_W, col)
            c.rect(0, base + 10, HL_W, base + 40, mix(col, (230, 230, 240), 0.5), ol=None)
        # a loch with a castle on its island
        c.rect(0, 470, HL_W, 540, (120, 150, 190), ol=None)
        for k in range(30):
            x = rng.uniform(0, HL_W)
            y = rng.uniform(480, 535)
            c.line([(x, y), (x + rng.uniform(30, 80), y)], (170, 196, 226), 2)
        P.loch_castle(c, 760, 505, 0.62)
        P.urquhart(c, 99999, 0)  # (unused far away: keeps the drawing deterministic)
        # purple heather hills
        P.hill(c, [520, 500, 530, 510, 490, 520, 500, 540, 515, 500, 520, 506], 0, HL_W, (120, 100, 136),
               ol=(80, 66, 96))
        for x in range(60, HL_W, 140):
            P.heather_patch(c, x, 540 + 10 * math.sin(x), 120, seed=x, n=7)
        P.hill(c, [600, 580, 590, 570, 586, 600, 580, 592, 576, 590], 0, HL_W, (98, 124, 80), ol=(66, 90, 58))
        for x in range(30, HL_W, 90):
            P.heather_patch(c, x, 610 + 8 * math.sin(x * 0.3), 90, seed=x + 1, n=6)
        # the path
        c.rect(0, PATH - 10, HL_W, H, (110, 134, 84), ol=None)
        c.poly([(0, PATH + 6), (HL_W, PATH - 4), (HL_W, PATH + 30), (0, PATH + 40)], (196, 176, 136), ol=None)
        for x in range(20, HL_W, 110):
            P.heather_patch(c, x, 700, 110, seed=x + 2, n=8)
        for x in (200, 690, 1320, 2050, 2600):
            P.thistle(c, x, 712, 0.9)
        # the stag's knoll
        c.poly([(1440, 520), (1560, 470), (1650, 452), (1740, 470), (1860, 520)], (124, 100, 136), ol=None)
        # boulder, Scots pine, signpost
        c.poly([(1080, PATH + 10), (1090, PATH - 50), (1130, PATH - 80), (1190, PATH - 70), (1214, PATH - 20),
                (1210, PATH + 10)], (150, 146, 150), w=2.5)
        c.line([(1120, PATH - 60), (1150, PATH - 20)], (120, 116, 124), 2)
        tx = 1980
        c.rect(tx - 14, PATH - 280, tx + 14, PATH + 6, (150, 90, 60), w=2.5)
        for dx, dy, r in ((-60, -300, 50), (40, -320, 60), (-10, -360, 50), (70, -270, 40), (-80, -250, 36)):
            c.ellipse(tx + dx, PATH + dy, r * 1.5, r * 0.6, (50, 100, 70), w=2.5)
        sx = 2560
        c.rect(sx - 6, PATH - 160, sx + 6, PATH + 6, (130, 96, 64), w=2)
        c.poly([(sx - 10, PATH - 160), (sx + 110, PATH - 160), (sx + 130, PATH - 140), (sx + 110, PATH - 120),
                (sx - 10, PATH - 120)], (240, 236, 220), w=2.5)
        c.text(sx + 56, PATH - 140, "LOCH NESS", 16, (40, 70, 60))
        return c.img
    return cached("highlands", make)


def highlands(tl, t):
    T = tl.t
    s0 = tl.scenes["highlands"][0]
    ride0, ride1 = T("h_ride"), T("h_end", 0.6)
    # Hamish's route: walk left to the boulder, then carry the cats right to the signpost
    hk = [(s0, 1700), (T("h_bump", 0.55), 1380), (T("h_ride", 0.15), 1380), (T("h_ride", 0.38), 1760),
          (T("h_ride", 0.46), 1730), (T("h_left"), 2200), (T("h_left", 0.95), 2380), (T("h_end"), 2370)]
    hx = smooth(t, hk, r=0.3)
    riding = t >= T("h_ride", 0.15)
    if t < T("h_bump"):
        camx = smooth(t, [(s0, 0), (T("h_narr", 0.1), 0), (T("h_narr", 1.0), 640)], r=0.5)
    elif not riding:
        camx = 640 + 120 * ease(tl.prog("h_bump", t, 0.0, 0.5))
    else:
        camx = clamp(hx - 640, 760, HL_W - W)
    camx = smooth(t, [(s0, 0), (T("h_narr", 0.1), 0), (T("h_narr", 1.0), 640), (T("h_bump", 0.5), 760),
                      (T("h_ride", 0.15), 760), (T("h_ride", 0.38), 1120), (T("h_left"), 1560),
                      (T("h_left", 0.95), 1620)], r=0.4)
    c = view(highlands_bg(), camx)
    c.push(-camx, 0)
    P.stag(c, 1650, 446, 0.34, -1, t, roar=math.sin(math.pi * tl.prog("h_narr", t, 0.8, 1.0)), col=(150, 80, 50))
    # geese bring the cats in
    u = tl.prog("h_fly", t, 0.0, 0.6)
    lk = ease(tl.prog("h_fly", t, 0.6, 0.8))
    for k, (dx, who) in enumerate(((0, "whiskers"), (160, "luna"))):
        if u < 1:
            x, y = lerp(-200, 360, ease(u)) + dx, lerp(250, 560, ease(u)) - 10 * k
        else:
            x = 360 + dx + 900 * ease(tl.prog("h_fly", t, 0.8, 1.0))
            y = 560 - 10 * k - 400 * ease(tl.prog("h_fly", t, 0.8, 1.0))
        if t < T("h_fly", 1.0):
            P.goose(c, x, y, 1.0, 1, t, part="back", seed=k)
            if t < T("h_fly", 0.6):
                kat(c, tl, t, who, x - 16, y - 2, 0.5, 1, "crouch")
            P.goose(c, x, y, 1.0, 1, t, part="front", seed=k)
    on_back = riding
    hop = tl.prog("h_ride", t, 0.0, 0.15)
    walking = abs(speed(t, hk)) > 15
    face_h = -1 if t < T("h_ride", 0.1) else 1
    bumped = T("h_bump", 0.55) <= t < T("h_fringe", 0.3)
    peek = ease(tl.prog("h_end", t, 0.1, 0.4)) * (1 - ease(tl.prog("h_end", t, 0.85, 1.0)))
    hs = 0.78
    P.hamish(c, hx, PATH + 30, hs, face_h, t, mouth=tl.mouth("hamish", t), walk=hx / 30 if walking else 0.0,
             dizzy=1.0 if bumped else 0.0, peek=peek,
             head_dy=-10 * math.sin(math.pi * tl.prog("h_ride", t, 0.38, 0.5)))
    # cats
    if t >= T("h_fly", 0.6):
        if not on_back:
            ckeys_w = [(T("h_fly", 0.75), 290), (T("h_narr", 0.2), 290), (T("h_narr", 1.0), 1000),
                       (T("h_bump"), 1020)]
            ckeys_l = [(T("h_fly", 0.75), 470), (T("h_narr", 0.25), 470), (T("h_narr", 1.0), 1120),
                       (T("h_bump"), 1130)]
            if hop <= 0:
                if t < T("h_fly", 0.8):
                    kat(c, tl, t, "whiskers", lerp(344, 290, lk), lerp(558, PATH + 36, lk) + jump_y(lk, 30), 0.72,
                        1, "leap" if lk < 1 else "stand")
                    kat(c, tl, t, "luna", lerp(494, 470, lk), lerp(548, PATH + 38, lk) + jump_y(lk, 30), 0.72, 1,
                        "leap" if lk < 1 else "stand")
                else:
                    look = (1, -0.4) if T("h_bump") <= t else (1, 0)
                    actor(c, tl, t, "whiskers", ckeys_w, PATH + 36, 0.72, 1, look=look)
                    actor(c, tl, t, "luna", ckeys_l, PATH + 38, 0.72, 1, look=look)
            else:
                for who, x0, y0, dx in (("whiskers", 1020, PATH + 36, -40), ("luna", 1130, PATH + 38, 40)):
                    tx = hx + dx * hs
                    ty = PATH + 30 - 190 * hs
                    kat(c, tl, t, who, lerp(x0, tx, hop), lerp(y0, ty, hop) + jump_y(hop, 60), 0.6, 1,
                        "leap" if hop < 1 else "sit")
        else:
            bump = math.sin(math.pi * tl.prog("h_ride", t, 0.38, 0.55))
            bump2 = math.sin(math.pi * tl.prog("h_left", t, 0.9, 1.0)) if t < T("h_end") else 0.0
            bounce = abs(math.sin(hx / 30)) * 6 if walking else 0.0
            for k, (who, dx) in enumerate((("whiskers", -60), ("luna", 30))):
                x = hx + dx * hs
                y = PATH + 30 - 188 * hs - bounce - 70 * (bump + bump2) * (1 + 0.3 * k)
                eyes = "wide" if bump + bump2 > 0.1 else "open"
                if who == "whiskers" and T("h_left") <= t < T("h_end"):
                    eyes = "wide"
                kat(c, tl, t, who, x, y, 0.6, 1, "sit", eyes=eyes, look=(1, 0.3))
    c.pop()
    return finish(c, tl, t, 0.45)


# =================================================================== loch

LOCH_Y = 470


def loch_bg(night):
    def make():
        if night:
            sky = [(0, (14, 18, 52)), (0.5, (38, 44, 96)), (0.66, (60, 60, 120)), (1, (60, 60, 120))]
        else:
            sky = [(0, (70, 76, 150)), (0.35, (190, 120, 150)), (0.6, (250, 176, 120)), (1, (250, 176, 120))]
        c = Canvas(D.gradient(W * SS, H * SS, sky))
        if night:
            D.stars(c, 11, 120, W, 400)
            D.moon(c, 1040, 130, 40, sky=(30, 36, 86))
        else:
            c.glow(700, 430, 340, 120, (255, 226, 160), (250, 176, 120), steps=10)
        n = 1.0 if night else 0.0
        far = mix((150, 110, 150), (40, 44, 86), n)
        mid = mix((110, 80, 120), (30, 34, 70), n)
        near = mix((80, 66, 96), (24, 26, 56), n)
        P.hill(c, [430, 400, 420, 410, 430, 440, 450], 0, W, far)
        P.hill(c, [380, 420, 440, 450, 460, 466], 0, 900, mid)
        P.hill(c, [470, 440, 400, 370, 380, 420, 460], 600, W, mid)
        water = D.gradient(W * SS, (H - LOCH_Y) * SS,
                           [(0, mix((236, 170, 140), (50, 60, 110), n)), (1, mix((90, 70, 120), (16, 20, 50), n))])
        c.img.paste(water, (0, LOCH_Y * SS))
        P.urquhart(c, 1060, LOCH_Y + 4, 0.7, ol=mix(OUT, (10, 10, 30), n), night=n)
        # reflections
        if night:
            for k in range(12):
                y = LOCH_Y + 16 + k * 12
                w = 50 - k * 2
                c.line([(1040 - w, y), (1040 + w, y)], (220, 220, 190), 2)
        else:
            for k in range(10):
                y = LOCH_Y + 10 + k * 12
                c.line([(640 - 90 + k * 7, y), (760 - k * 7, y)], (255, 220, 170), 2)
        # pebbly shore, foreground
        shore = mix((150, 130, 120), (50, 50, 80), n * 0.8)
        c.poly([(0, H), (0, 590), (200, 576), (420, 586), (620, 616), (760, 660), (840, H)], shore, w=2.5)
        rng = np.random.default_rng(6)
        for _ in range(60):
            x = rng.uniform(10, 700)
            y = rng.uniform(600, 715)
            if y > 590 + x * 0.12:
                c.ellipse(x, y, rng.uniform(6, 14), rng.uniform(4, 8), mix(shore, (255, 255, 255), rng.uniform(0, 0.2)),
                          ol=mix(OUT, (10, 10, 30), n), w=1.5)
        for x in (60, 640):
            P.thistle(c, x, 640 if x < 300 else 690, 0.8)
        return c.img
    return cached(("loch", night), make)


def loch_frame(tl, t, night):
    """Blend of the dusk and night pictures of the loch."""
    if night <= 0.01:
        return Canvas(loch_bg(False).copy())
    if night >= 0.99:
        return Canvas(loch_bg(True).copy())
    q = round(night * 20) / 20
    key = ("lochmix", q)
    if key not in _cache:
        _cache[key] = Image.blend(loch_bg(False), loch_bg(True), q)
        # keep at most a few blends in memory
        for k in [k for k in _cache if isinstance(k, tuple) and k[0] == "lochmix" and k != key][:-3]:
            _cache.pop(k)
    return Canvas(_cache[key].copy())


NX, NY = 830, 520


def loch(tl, t):
    T = tl.t
    night = ease(tl.prog("l_wait1", t, 0.0, 1.0)) * 0.5 + ease(tl.prog("l_wait2", t, 0.0, 1.0)) * 0.5
    c = loch_frame(tl, t, night)
    tint = ((30, 36, 90), 0.3 * night)
    # Nessie rises
    rise = ease(tl.prog("l_rise", t, 0.35, 0.95))
    if T("l_grab") <= t:
        rise = 1 - 0.35 * ease(tl.prog("l_grab", t, 0.15, 0.5))
    bub = tl.prog("l_rise", t, 0.0, 0.5)
    if T("l_rise") <= t:
        if bub < 1:
            P.bubbles(c, NX, NY, t, 1.0, n=10, seed=2)
        P.ripple(c, NX, NY + 4, t, 120, (200, 220, 250))
        if rise > 0.02:
            shy = 0.6 if t < T("l_hello") else (0.3 if t < T("l_grab") else 1.0)
            P.nessie(c, NX, NY, 0.55, -1, t, mouth=tl.mouth("nessie", t), rise=rise, shy=shy,
                     look=(-1, 0.4) if t >= T("l_grab") else (-1, 0), tint=((40, 50, 110), 0.25),
                     water=(42, 50, 96), humps=True)
            # waterline over the neck base
            c.rect(NX - 50, NY, NX + 50, NY + 16, mix((50, 60, 110), (16, 20, 50), 0.3), ol=None)
            c.line([(NX - 60, NY), (NX + 60, NY)], (170, 190, 230), 2)
    c.tint = tint
    # Luna watches; Whiskers waits, then naps
    luna_eyes = "wide" if T("l_hello") <= t else "open"
    kat(c, tl, t, "luna", 250, 630, 0.9, 1, "sit", look=(1, -0.3), eyes=luna_eyes, cam=t < T("l_smile"))
    asleep = T("l_nap", 0.7) <= t < T("l_wake", 0.6)
    if asleep:
        kat(c, tl, t, "whiskers", 420, 640, 0.9, 1, "sleep")
        P.camera(c, 520, 636, 0.9)
        c.tint = None
        D.zzz(c, 470, 560, t)
        c.tint = tint
    else:
        holding = t < T("l_nap", 0.7) or t >= T("l_grab")
        eyes = "wide" if t >= T("l_wake", 0.6) else "open"
        kat(c, tl, t, "whiskers", 420, 640, 0.9, 1, "sit", look=(1, -0.3), eyes=eyes)
        if holding:
            up = ease(tl.prog("l_grab", t, 0.0, 0.3)) if t >= T("l_grab") else 0.4
            P.camera(c, 420 + 42, 640 - 70 - 30 * up, 1.0)
    # Luna nudges him awake
    if T("l_wake") <= t < T("l_wake", 0.6):
        c.text(430, 540, "!", 40, (255, 240, 120), stroke=3)
    c.tint = None
    return finish(c, tl, t, 0.25)


def nessie_scene(tl, t):
    T = tl.t
    if t >= T("n_ride"):
        return ride(tl, t)
    c = loch_frame(tl, t, 1.0)
    tint = ((30, 36, 90), 0.3)
    low = ease(tl.prog("n_yes", t, 0.3, 1.0))
    sad = t < T("n_safe", 0.5)
    rise = 0.65 if t < T("n_safe") else lerp(0.65, 1.0, ease(tl.prog("n_safe", t, 0.4, 0.8)))
    P.ripple(c, NX, NY + 4, t, 120, (200, 220, 250))
    eyes = "open"
    if not sad:
        eyes = "happy" if tl.mouth("nessie", t) < 0.1 and t < T("n_yes") else "open"
    P.nessie(c, NX, NY, 0.55, -1, t, mouth=tl.mouth("nessie", t), rise=rise, shy=0.9 if sad else 0.0,
             look=(-1, 0.8) if sad else (-1, 0), lower=low, eyes=eyes, tint=((40, 50, 110), 0.25), blush=0.9,
             water=(42, 50, 96))
    c.rect(NX - 50, NY, NX + 50, NY + 16, (20, 24, 56), ol=None)
    c.line([(NX - 60, NY), (NX + 60, NY)], (170, 190, 230), 2)
    if T("n_yes", 0.85) <= t:
        P.smoke_puff(c, NX - 120, NY - 10, tl.prog("n_yes", t, 0.85, 1.0), 0.8, seed=5, col=(200, 220, 250))
    c.tint = tint
    kat(c, tl, t, "luna", 250, 630, 0.9, 1, "sit", look=(1, -0.3),
        eyes="happy" if T("n_safe", 0.6) <= t else "open")
    put_down = ease(tl.prog("n_safe", t, 0.0, 0.3))
    wl = (1, -0.3) if t < T("n_think") or t >= T("n_pause") else (-0.5, -1)
    kat(c, tl, t, "whiskers", 420, 640, 0.9, 1, "sit", look=wl, head_dy=6 if T("n_pause") <= t < T("n_safe") else 0)
    if t < T("n_safe"):
        P.camera(c, 462, 540, 1.0)
    else:
        P.camera(c, lerp(462, 360, put_down), lerp(540, 690, put_down), 1.0)
    c.tint = None
    # the thought bubble: a mountain of shortbread
    k = ease(tl.prog("n_think", t, 0.1, 0.35)) * (1 - ease(tl.prog("n_pause", t, 0.0, 0.3)))
    if T("n_think") <= t < T("n_safe"):
        thought_bubble(c, 330, 250, 190, 120, k, tail=(400, 470))
        if k > 0.9:
            for row in range(5):
                for i in range(5 - row):
                    P.shortbread(c, 330 - (4 - row) * 30 + i * 60, 320 - row * 26, 1.0, ang=0.1 * ((i + row) % 2))
            c.text(330, 170, "FOR LIFE", 22, (190, 40, 50))
            P.sparkles(c, 330, 250, t, n=8, r=130, seed=4)
    return finish(c, tl, t, 0.2)


def ride_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (12, 16, 48)), (0.55, (40, 46, 100)), (1, (40, 46, 100))]))
        D.stars(c, 21, 160, W, 380)
        D.moon(c, 900, 150, 60, sky=(26, 32, 80))
        P.hill(c, [420, 380, 400, 360, 390, 410, 400], 0, W, (30, 34, 72))
        P.hill(c, [470, 440, 430, 455, 470], 0, 700, (24, 26, 60))
        water = D.gradient(W * SS, (H - 470) * SS, [(0, (40, 50, 104)), (1, (12, 16, 44))])
        c.img.paste(water, (0, 470 * SS))
        P.urquhart(c, 300, 474, 0.75, ol=(10, 10, 30), night=1.0)
        for k in range(18):
            y = 480 + k * 13
            w = 70 - k * 2.5
            c.line([(900 - w, y), (900 + w, y)], (230, 226, 190), 2)
        return c.img
    return cached("ride", make)


def ride(tl, t):
    T = tl.t
    c = Canvas(ride_bg().copy())
    u = tl.prog("n_ride", t, 0.0, 1.0) * 0.4 + tl.prog("n_riding", t, 0.0, 1.0) * 0.15 + \
        tl.prog("n_know", t, 0.0, 1.0) * 0.15 + tl.prog("n_end", t, 0.0, 1.0) * 0.3
    x = lerp(380, 1100, u)
    y = 600
    # wake
    for k in range(5):
        wx = x - 380 - k * 70
        c.line([(wx, y + 4 + k * 3), (wx - 60, y + 8 + k * 5)], (150, 170, 220), 2)
    if T("n_end", 0.3) <= t:
        P.goose_vee(c, lerp(600, 1300, tl.prog("n_end", t, 0.3, 1.0)), 150, t, n=7, s=0.22,
                    tint=((10, 10, 30), 0.85))
    tint = ((40, 50, 110), 0.25)
    P.nessie(c, x, y, 0.62, 1, t, mouth=tl.mouth("nessie", t), rise=1.0, shy=0.0, eyes="happy", tint=tint,
             water=(28, 34, 80))
    c.tint = ((30, 36, 90), 0.3)
    bob = math.sin(t * 1.6) * 3
    kat(c, tl, t, "luna", x - 140 * 0.62, y - 40 * 0.62 + bob, 0.55, 1, "sit", look=(1, -0.3),
        eyes="happy" if tl.mouth("luna", t) < 0.1 else "open")
    kat(c, tl, t, "whiskers", x - 270 * 0.62, y - 30 * 0.62 + bob, 0.55, 1, "sit", look=(1, -0.3),
        eyes="happy" if tl.mouth("whiskers", t) < 0.1 else "open")
    c.tint = None
    # water line in front of the humps
    c.rect(x - 420, y + 1, x - 40, y + 30, (34, 40, 90), ol=None)
    c.line([(x - 420, y), (x - 40, y)], (150, 170, 220), 2)
    return finish(c, tl, t, 0.2)


# =================================================================== home

SILL = 546


def home_bg():
    def make():
        wall = (226, 206, 176)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, H, mix(wall, (255, 255, 255), 0.2), ol=None)
        win = Canvas(D.gradient(1000 * SS, 480 * SS, [(0, (20, 26, 70)), (1, (70, 70, 130))]), size=(1000, 480))
        D.stars(win, 5, 60, 1000, 300)
        D.moon(win, 780, 110, 44, sky=(30, 36, 86))
        for x, w, h, col in ((40, 220, 160, (60, 56, 90)), (300, 180, 210, (70, 64, 100)),
                             (520, 260, 140, (56, 52, 86)), (800, 200, 190, (66, 60, 96))):
            win.rect(x, 480 - h, x + w, 480, col, ol=None)
            win.poly([(x - 14, 480 - h), (x + w / 2, 480 - h - 60), (x + w + 14, 480 - h)], (50, 40, 70), ol=None)
            for wx in range(int(x) + 26, int(x + w) - 30, 60):
                win.rect(wx, 480 - h + 40, wx + 26, 480 - h + 74, (255, 214, 120), ol=None)
        D.tree(win, 930, 480, 1.0, leaf=(50, 70, 80), trunk=(50, 40, 50))
        c.img.paste(win.img, (140 * SS, 60 * SS))
        for x0, x1 in ((50, 170), (1110, 1230)):
            # tartan curtains, a souvenir
            P.tartan(c, x0, 0, x1, 640, base=P.TARTAN_GREEN, bands=((P.TARTAN_NAVY, 0.3), (P.TARTAN_RED, 0.08)),
                     line=(230, 210, 120), step=30, r=8)
        c.rect(30, 0, 1250, 16, (150, 100, 60))
        c.rect(0, 572, W, H, mix(wall, (0, 0, 0), 0.06), ol=None)
        c.rect(130, 52, 1150, 544, None, w=10)
        c.line([(640, 60), (640, 300)], (240, 236, 230), 10, cap=False)
        c.line([(140, 300), (1140, 300)], (240, 236, 230), 10, cap=False)
        c.rect(130, 52, 1150, 544, None, ol=(240, 236, 230), w=6)
        c.rect(100, 540, 1180, 572, (250, 246, 236), r=5)
        # the empty shortbread tin, now holding Pip's things
        P.tin(c, 1050, 546, 0.6, lid=1.0)
        return c.img
    return cached("home", make)


def home(tl, t):
    T = tl.t
    c = Canvas(home_bg().copy())
    # the geese glide past outside and the cats drop in through the open window
    u = tl.prog("o_open", t, 0.0, 0.7)
    if u < 1:
        P.goose_vee(c, lerp(100, 1300, u), 200, t, n=5, s=0.4, tint=((20, 20, 50), 0.4))
    drops = (("luna", 520, 0.45, 0.6), ("whiskers", 700, 0.55, 0.75))
    asleep = t >= T("o_end", 0.15)
    showing = T("o_photo") <= t < T("o_wink")
    for who, x, a, b in drops:
        k = tl.prog("o_open", t, a, b)
        if k <= 0:
            continue
        y = lerp(150, SILL, k ** 2)
        if k < 1:
            kat(c, tl, t, who, x, y, 0.95, 1 if who == "luna" else -1, "leap", eyes="wide")
        elif asleep:
            kat(c, tl, t, who, x + (30 if who == "luna" else -30), SILL, 0.9, 1 if who == "luna" else -1, "sleep")
        else:
            face = 1 if who == "luna" else -1
            look = (face, 0)
            if who == "whiskers" and T("o_none") <= t < T("o_photo"):
                look = (1, -1)          # innocent look at the ceiling
            if T("o_look") <= t < T("o_moral"):
                look = (0.5 * face, -0.8)
            kat(c, tl, t, who, x, SILL, 0.95, face, "sit", look=look,
                eyes="happy" if T("o_moral") <= t else "open",
                wink=(who == "whiskers" and T("o_wink") <= t < T("o_wink", 0.8)))
    # Pip
    if asleep:
        D.mouse(c, 610, SILL - 30, 1.1, 1, t, eyes="closed")
        D.zzz(c, 700, 380, t)
    else:
        keys = [(T("o_open"), 980), (T("o_pip"), 980), (T("o_pip", 0.5), 610)]
        actor(c, tl, t, "pip", keys, SILL, 1.3, -1, proud=T("o_rock") <= t < T("o_just"),
              eyes="happy" if T("o_moral") <= t else "open")
    k = ease(tl.prog("o_photo", t, 0.2, 0.5)) * (1 - ease(tl.prog("o_just", t, 0.6, 1.0)))
    if showing and k > 0:
        P.photo(c, 640, 260, k, t, blink_eye=T("o_look", 0.45) <= t < T("o_look", 0.6))
    kend = ease(tl.prog("o_end", t, 0.25, 0.55))
    if kend > 0:
        c.text(W / 2, 640, "The End", 30 + 44 * kend, mix((226, 206, 176), (255, 250, 236), kend), stroke=4 * kend,
               stroke_fill=(30, 70, 70))
    return finish(c, tl, t, 0.3)


SCENE_FUNCS = {"title": title, "tin": tin, "geese": geese, "mile": mile, "castle": castle, "bobby": bobby,
               "highlands": highlands, "loch": loch, "nessie": nessie_scene, "home": home}
CONTINUOUS = {"nessie"}
EXTRA_CUTS = ["g_haar", "n_ride"]
