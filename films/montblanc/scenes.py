"""Scenes of "Whiskers and the White Mountain". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.montblanc import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "bruno": 3.3, "margot": 4.4}

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


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", scarf=False, walk=0.0, **kw):
    """A cat (Whiskers optionally in his scarf), mouth from the voice track unless given."""
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if scarf and who == "whiskers" and kw.get("squash", 1.0) == 1.0:
        P.whiskers_scarf(c, x, y, s, face, pose, t, kw.get("head_dy", 0.0), walk)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", scarf=False, **kw):
    x = smooth(t, keys)
    v = speed(t, keys)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "bruno":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        P.bruno(c, x, y, s, face, t, walk=x / (26 * s) if moving else 0.0, mouth=mouth, **kw)
    elif who == "margot":
        mouth = kw.pop("mouth", tl.mouth(who, t))
        hop = abs(math.sin(x / (10 * s))) * 6 * s if moving else kw.pop("hop", 0.0)
        P.margot(c, x, y, s, face, t, mouth=mouth, walk=x / (7 * s) if moving else 0.0, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, scarf, walk=x / (12 * s) if moving else 0.0, **kw)
    return x


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def finish(c, tl, t):
    P.shade_bottom(c, tl, t)
    return c


def thought_bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    """White cloud-shaped bubble scaled by k, with two small trailing puffs toward tail."""
    if k <= 0.02:
        return
    for f, r in ((0.35, 9), (0.65, 14)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def fondue_pot(c, x, y, s=1.0, t=0.0, steam=True):
    c.push(x, y, s)
    c.rect(-44, -26, 44, 0, (80, 80, 92), w=2.5, r=4)
    for lx in (-34, 34):
        c.line([(lx, -26), (lx * 1.2, 0)], OUT, 3)
    fl = 1 + 0.15 * math.sin(t * 13)
    c.ellipse(0, -30, 11, 13 * fl, (255, 150, 50), ol=None)
    c.ellipse(0, -28, 6, 7 * fl, (255, 236, 120), ol=None)
    c.rect(50, -86, 112, -74, (120, 70, 40), w=2.5, r=5)              # handle
    c.ellipse(0, -62, 64, 30, (198, 74, 52), w=3)
    c.ellipse(-20, -66, 22, 12, (226, 110, 86), ol=None)
    c.ellipse(0, -86, 64, 14, (150, 50, 38), w=3)
    c.ellipse(0, -86, 55, 10, (255, 212, 90), ol=None)
    for k in range(4):
        u = (t * 0.9 + k * 0.27) % 1.0
        bx = -36 + 24 * k
        c.circle(bx, -86, 3 + 4 * math.sin(math.pi * u), (255, 236, 150), w=1.5)
    if steam:
        for k in range(3):
            u = (t * 0.5 + k / 3) % 1.0
            pts = [(-20 + 20 * k + 6 * math.sin(t * 3 + v * 6 + k), -100 - 70 * u - 30 * v) for v in np.linspace(0, 1, 6)]
            c.line(pts, mix((255, 255, 255), (230, 220, 200), u), 4 * (1 - u) + 1)
    c.pop()


# =================================================================== title

def title_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (58, 70, 140)), (0.32, (140, 116, 182)), (0.58, (246, 168, 164)),
                                               (0.8, (255, 214, 164)), (1, (255, 214, 164))]))
        c.glow(1010, 470, 380, 260, (255, 238, 196), (246, 176, 164), steps=12)
        D.stars(c, 4, 40, W, 160, col=(255, 240, 230))
        far = dict(rock=(140, 112, 152), snow=(255, 236, 238), shade=(222, 190, 216), ol=(96, 74, 110))
        P.peak(c, 120, 590, 460, 290, seed=1, **far)
        P.peak(c, 1170, 590, 520, 330, seed=2, **far)
        P.peak(c, 1000, 600, 300, 200, seed=5, **far)
        P.mont_blanc(c, 640, 600, 0.82, snow=(255, 244, 242), shade=(226, 196, 222), rock=(130, 104, 142),
                     ol=(96, 74, 110), glow=(255, 220, 196))
        c.poly([(0, 610), (220, 585), (430, 606), (650, 590), (900, 612), (1100, 586), (W, 600), (W, H), (0, H)],
               (232, 226, 246), ol=None)
        c.poly([(0, 660), (260, 628), (520, 660), (800, 676), (1050, 650), (W, 664), (W, H), (0, H)],
               (248, 244, 255), ol=None)
        c.poly([(0, 690), (W, 700), (W, H), (0, H)], (226, 220, 244), ol=None)
        for x, y, s in ((40, 690, 0.95), (110, 700, 0.75), (1180, 690, 1.0), (1250, 706, 0.8), (1100, 712, 0.6)):
            P.pine(c, x, y, s, col=(60, 96, 100), dark=(44, 74, 86))
        # a rock ledge for the cats
        c.poly([(200, 700), (232, 652), (300, 640), (420, 646), (470, 700)], (120, 108, 140), w=2.5)
        c.poly([(226, 660), (300, 636), (420, 642), (446, 662), (330, 656)], (250, 246, 255), w=2)
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    c.tint = ((90, 70, 130), 0.22)
    kat(c, tl, t, "whiskers", 290, 650, 0.78, 1, "sit", scarf=True, look=(1, -1))
    kat(c, tl, t, "luna", 372, 652, 0.74, 1, "sit", look=(1, -1), tail=math.sin(t * 1.5))
    c.tint = None
    P.snowfall(c, t, n=70, seed=3, speed=38, drift=14, size=(1.2, 3.2))
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(W / 2, 86 - 30 * (1 - k), "Whiskers and the", 44, mix((60, 70, 140), (255, 248, 236), k),
           stroke=3 * k, stroke_fill=(70, 50, 100))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 162, "WHITE MOUNTAIN", 28 + 52 * k2, mix((60, 70, 140), (255, 255, 255), k2), stroke=5 * k2,
           stroke_fill=(70, 50, 110))
    return finish(c, tl, t)


# ================================================================ postcard

def room_bg():
    def make():
        wall, floor = (236, 214, 178), (186, 128, 84)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, 520, mix(wall, (255, 255, 255), 0.25), ol=None)
        c.rect(0, 520, W, H, floor, ol=None)
        for y in range(540, H, 36):
            c.line([(0, y), (W, y)], mix(floor, (0, 0, 0), 0.12), 2, cap=False)
        c.rect(0, 506, W, 524, mix(wall, (0, 0, 0), 0.25), ol=None)
        win = Canvas(D.gradient(320 * SS, 260 * SS, [(0, (150, 176, 210)), (1, (222, 228, 236))]), size=(320, 260))
        win.poly([(0, 200), (120, 170), (320, 190), (320, 260), (0, 260)], (170, 150, 120), ol=None)
        win.rect(200, 120, 320, 210, (190, 100, 80), ol=None)
        win.poly([(190, 124), (260, 80), (330, 124)], (120, 70, 60), ol=None)
        D.tree(win, 90, 236, 0.9, leaf=(230, 130, 50))
        for dx, dy in ((60, -150), (110, -175), (40, -120)):
            win.circle(90 + dx - 60, 236 + dy, 18, (250, 180, 60), ol=None)
        c.img.paste(win.img, (760 * SS, 110 * SS))
        c.rect(756, 106, 1084, 374, None, w=8)
        c.line([(920, 110), (920, 370)], (240, 240, 240), 6, cap=False)
        c.line([(760, 240), (1080, 240)], (240, 240, 240), 6, cap=False)
        c.rect(740, 370, 1100, 392, (255, 250, 240), r=4)
        c.ellipse(520, 612, 190, 40, (70, 110, 170))
        c.ellipse(520, 612, 150, 28, (110, 150, 200), ol=None)
        c.rect(150, 440, 210, 520, (190, 100, 70), r=6)
        for dx, dy in ((-30, -10), (0, -40), (30, -12), (-15, -30), (18, -36)):
            c.ellipse(180 + dx, 440 + dy, 14, 30, (80, 160, 90))
        # a framed picture of the pond (Film 1)
        c.rect(400, 150, 560, 270, (150, 100, 60), w=3)
        pic = Canvas(D.gradient(140 * SS, 100 * SS, [(0, (30, 36, 80)), (1, (70, 70, 130))]), size=(140, 100))
        D.moon(pic, 100, 30, 14, sky=(40, 44, 96))
        pic.ellipse(70, 86, 70, 14, (40, 60, 110), ol=None)
        pic.ellipse(70, 86, 20, 4, (240, 236, 200), ol=None)
        c.img.paste(pic.img, (410 * SS, 160 * SS))
        return c.img
    return cached("room", make)


def postcard_card():
    def make():
        img = P.postcard_img()
        w, h = img.size
        card = Image.new("RGB", (w + 24 * SS, h + 24 * SS), (255, 252, 240))
        card.paste(img, (12 * SS, 12 * SS))
        return card
    return cached("postcard_card", make)


def falling_leaves(c, t):
    rng = np.random.default_rng(9)
    for k in range(5):
        u = ((t * 0.12 + rng.uniform()) % 1.0)
        x = 790 + rng.uniform(0, 260) + 20 * math.sin(t * 2 + k)
        y = 120 + 240 * u
        c.ellipse(x, y, 5, 3, (240, 150, 60), ol=None)


def postcard(tl, t):
    T = tl.t
    c = Canvas(room_bg().copy())
    falling_leaves(c, t)
    c.rect(756, 106, 1084, 374, None, w=8)
    s0, s1 = tl.scenes["postcard"]
    # Whiskers: asleep, mumbles about pillows, wakes for cheese, dashes off to pack
    wy = 615
    if t < T("pc_ears"):
        talk = T("pc_pillow") - 0.2 <= t < T("pc_pillow", 1) + 0.2
        kat(c, tl, t, "whiskers", 520, wy, 1.0, 1, "sit" if talk else "sleep", eyes="closed",
            head_dy=8 if talk else 0)
        if not talk:
            D.zzz(c, 580, 540, t)
    elif t < T("pc_end"):
        startle = clamp((t - T("pc_ears")) / 0.3)
        excited = t >= T("pc_pack")
        hop = abs(math.sin((t - T("pc_pack")) * 7)) * 22 if excited and t > T("pc_pack", 0.55) else 0
        kat(c, tl, t, "whiskers", 520, wy - hop, 1.0, 1, "stand" if excited else "sit",
            eyes="happy" if excited and tl.mouth("whiskers", t) < 0.1 else "wide", look=(0, -1),
            head_dy=-8 * (1 - startle))
    else:
        actor(c, tl, t, "whiskers", [(T("pc_end"), 520), (T("pc_end", 0.9), 1450)], wy, eyes="happy")
    # Luna sits by the window
    lpose = "sit"
    leyes = "happy" if t >= T("pc_end") or T("pc_mb") <= t < T("pc_mb", 1) else "open"
    kat(c, tl, t, "luna", 870, 612, 1.0, -1, lpose, eyes=leyes, look=(1, 0.2), tail=math.sin(t * 1.5))
    # Pip runs in with the postcard held high
    pk = [(T("pc_pip"), -80), (T("pc_pip", 1), 330)]
    if t >= T("pc_pip") - 0.3:
        px = actor(c, tl, t, "pip", pk, 624, 1.4, face=1, eyes="happy" if t >= T("pc_end") else "open",
                   proud=T("pc_pip_say") <= t < T("pc_pip_say", 1))
        if t < T("pc_mb"):
            bob = abs(math.sin(px / 9)) * 5 if speed(t, pk) > 20 else 0
            c.rect(px - 40, 624 - 118 - bob, px + 40, 624 - 66 - bob, (255, 252, 240), w=2.5, r=2)
            c.rect(px - 32, 624 - 110 - bob, px + 32, 624 - 74 - bob, (120, 180, 235), ol=None)
            c.poly([(px - 26, 624 - 74 - bob), (px - 2, 624 - 106 - bob), (px + 22, 624 - 74 - bob)],
                   (255, 255, 255), ol=None)
    # The postcard, big, while they read it
    k = min(ease((t - T("pc_mb")) / 0.4), 1 - ease((t - T("pc_fondue", 1)) / 0.4))
    if k > 0.01:
        card = postcard_card()
        cw, ch = card.size
        sc = 0.95 * k
        im = card.resize((max(2, int(cw * sc)), max(2, int(ch * sc))))
        cx, cy = 360, 250
        c.rect(cx - cw / SS * sc / 2 + 8, cy - ch / SS * sc / 2 + 8, cx + cw / SS * sc / 2 + 8,
               cy + ch / SS * sc / 2 + 8, (150, 120, 100), ol=None)
        c.img.paste(im, (int((cx - cw / SS * sc / 2) * SS), int((cy - ch / SS * sc / 2) * SS)))
        c.rect(cx - cw / SS * sc / 2, cy - ch / SS * sc / 2, cx + cw / SS * sc / 2, cy + ch / SS * sc / 2,
               None, w=2.5)
    # Whiskers dreams of fondue
    k = min(ease((t - T("pc_fondue", 0.5)) / 0.4), 1 - ease((t - T("pc_pack", 0.6)) / 0.3))
    if k > 0.02:
        thought_bubble(c, 610, 300, 150, 92, k, tail=(560, 470))
        if k > 0.6:
            fondue_pot(c, 600, 360, 0.9 * k, t)
    return finish(c, tl, t)


# =================================================================== train

TW = 2 * W            # far layer tile width
MWT = 3 * W           # mid layer tile width
RAIL = 584
V_NEAR = 900.0


def _wrap_layer(tile):
    w, h = tile.size
    out = Image.new(tile.mode, (w + W * SS, h))
    out.paste(tile, (0, 0))
    out.paste(tile.crop((0, 0, W * SS, h)), (w, 0))
    return out


def train_far():
    def make():
        c = Canvas(D.gradient(TW * SS, H * SS, [(0, (100, 170, 236)), (0.55, (214, 236, 255)), (1, (214, 236, 255))]),
                   size=(TW, H))
        rng = np.random.default_rng(14)
        for k in range(9):
            x = k * TW / 9 + rng.uniform(-40, 40)
            w, h = rng.uniform(380, 560), rng.uniform(240, 330)
            for dx in (-TW, 0, TW):
                P.peak(c, x + dx, 470, w, h, rock=(120, 128, 160), snow=(250, 252, 255), shade=(206, 218, 240),
                       cap=0.5, seed=k, ol=(80, 84, 110))
        for x in (300, 1500, 2200):
            for dx in (-TW, 0, TW):
                D.cloud(c, x + dx, 120 + (x % 70), 0.8)
        return _wrap_layer(c.img)
    return cached("train_far", make)


def train_mid(snowy):
    def make():
        top = 300
        hh = H - top
        img = Image.new("RGBA", (MWT * SS, hh * SS), (0, 0, 0, 0))
        c = Canvas(img, size=(MWT, hh))
        g1, g2 = ((236, 242, 252), (214, 226, 244)) if snowy else ((130, 190, 100), (106, 168, 86))

        def hill(base, amp, n1, n2):
            return [(x, base + amp * math.sin(math.tau * n1 * x / MWT) + amp * 0.5 * math.sin(math.tau * n2 * x / MWT + 1))
                    for x in range(0, MWT + 40, 40)]
        c.poly(hill(140, 26, 5, 11) + [(MWT, hh), (0, hh)], g2, ol=None)
        c.poly(hill(210, 18, 7, 13) + [(MWT, hh), (0, hh)], g1, ol=None)
        rng = np.random.default_rng(21 if snowy else 22)
        for k in range(26):
            x = rng.uniform(0, MWT)
            y = 150 + 50 * math.sin(math.tau * 5 * x / MWT) * 0.3 + rng.uniform(0, 30)
            for dx in (-MWT, 0, MWT):
                P.pine(c, x + dx, y + 20, rng.uniform(0.45, 0.7), snowy=snowy)
        for k, x in enumerate((500, 1700, 2900)):
            for dx in (-MWT, 0, MWT):
                P.chalet(c, x + dx, 236, 0.55, snow_roof=snowy)
        if not snowy:
            for x in (900, 1150, 2300, 3500):
                for dx in (-MWT, 0, MWT):
                    P.cow(c, x + dx, 262, 0.55, face=1 if x % 2 else -1)
        tile = c.img
        out = Image.new("RGBA", (tile.size[0] + W * SS, tile.size[1]), (0, 0, 0, 0))
        out.paste(tile, (0, 0))
        out.paste(tile.crop((0, 0, W * SS, tile.size[1])), (tile.size[0], 0))
        return out
    return cached(("train_mid", snowy), make)


def chamonix_bg():
    CW = 2 * W + 400

    def make():
        c = Canvas(D.gradient(CW * SS, H * SS, [(0, (96, 168, 238)), (0.6, (214, 236, 255)), (1, (214, 236, 255))]),
                   size=(CW, H))
        stop = CW - W
        for x, w, h, sd in ((200, 500, 280, 1), (700, 460, 250, 2), (stop - 100, 520, 300, 3), (stop + 1150, 480, 300, 4)):
            P.peak(c, x, 520, w, h, rock=(120, 128, 160), snow=(250, 252, 255), shade=(206, 218, 240), seed=sd,
                   ol=(80, 84, 110))
        P.mont_blanc(c, stop + 720, 540, 1.08, rock=(118, 116, 140))
        D.cloud(c, stop + 300, 150, 0.7)
        c.poly([(0, 480), (CW, 470), (CW, H), (0, H)], (236, 242, 252), ol=None)
        for x in range(60, CW, 170):
            P.pine(c, x, 470 + (x % 3) * 6, 0.55)
        for k, x in enumerate(range(140, CW, 260)):
            P.chalet(c, x, 500 + (k % 2) * 12, 0.6 + 0.08 * (k % 3), lit=False)
        P.church(c, stop + 1080, 512, 0.75)
        # station platform and sign
        c.rect(0, 560, CW, 600, (200, 196, 200), ol=None)
        c.rect(stop + 230, 260, stop + 240, 560, (80, 80, 90), ol=None)
        c.rect(stop + 120, 250, stop + 350, 302, (250, 250, 250), w=3, r=6)
        c.text(stop + 235, 276, "CHAMONIX", 30, (40, 60, 120))
        return c.img
    return cached("chamonix", make), CW


def train_scene_motion(tl, t):
    """Positions (near ground scroll, chamonix scroll) and the tunnel geometry."""
    T = tl.t
    T0 = T("tr_tunnel", 0.05)
    L = 1800.0
    t_switch = T0 + (W + 50 + 360) / V_NEAR
    t_stop = T("tr_cham", 1)
    if t < t_switch:
        near = V_NEAR * (t - tl.scenes["train"][0])
    else:
        u = clamp((t - t_switch) / (t_stop - t_switch))
        near = V_NEAR * (t_switch - tl.scenes["train"][0]) + V_NEAR * (t_stop - t_switch) * (u - u * u / 2)
    in_x = W + 50 - V_NEAR * (t - T0) if t >= T0 else None
    return near, in_x, L, t_switch, t_stop


def train_inside(tl, t):
    def inside(c, k, a, b, cc, d):
        c.rect(a + 3, b + 3, cc - 3, d - 3, (238, 224, 196), ol=None, r=6)
        c.rect(a + 10, b + 60, cc - 10, d, (70, 110, 170), ol=None, r=6)     # seat backs
        mid = (a + cc) / 2
        if k == 0:
            look_up = T_in(tl, t, "tr_look", "tr_ice")
            kat(c, tl, t, "whiskers", mid - 20, d + 20, 0.86, 1, "sit", scarf=True,
                eyes="wide" if look_up else "open", look=(1, -0.6) if look_up else (1, 0))
        elif k == 1:
            kat(c, tl, t, "luna", mid - 10, d + 20, 0.84, -1 if tl.talking("luna", t) else 1, "sit",
                eyes="happy" if tl.talking("whiskers", t) else "open", look=(1, -0.5))
    return inside


def T_in(tl, t, a, b):
    return tl.t(a) <= t < tl.ev(b).end


def train(tl, t):
    T = tl.t
    s0 = tl.scenes["train"][0]
    near, in_x, L, t_switch, t_stop = train_scene_motion(tl, t)
    after = t >= t_switch
    if not after:
        far = train_far()
        fx = int(((t - s0) * 30) % TW)
        img = far.crop((fx * SS, 0, (fx + W) * SS, H * SS))
        ksnow = ease(tl.prog("tr_look", t, 0.0, 1.0) * 0.5 + tl.prog("tr_ice", t) * 0.5)
        mx = int(((t - s0) * 260) % MWT)
        crops = [train_mid(s).crop((mx * SS, 0, (mx + W) * SS, (H - 300) * SS)) for s in (False, True)]
        mid = crops[0] if ksnow <= 0 else crops[1] if ksnow >= 1 else Image.blend(crops[0], crops[1], ksnow)
        img.paste(mid, (0, 300 * SS), mid)
        c = Canvas(img)
        gcol = mix((150, 176, 110), (236, 240, 250), ksnow)
    else:
        bg, CW = chamonix_bg()
        u = clamp((t - t_switch) / (t_stop - t_switch))
        cx = (CW - W) * (1 - (1 - u) ** 2)
        c = view(bg, cx)
        gcol = (236, 240, 250)
    # catenary poles and wire
    for k in range(-1, 4):
        px = k * 520 - (near * 0.95) % 520 + 80
        c.rect(px - 5, 236, px + 5, RAIL, (110, 110, 120), w=2)
        c.line([(px - 30, 248), (px + 30, 248)], (90, 90, 100), 3)
    c.line([(0, 252), (W, 252)], (60, 60, 70), 2, cap=False)
    # track bed
    c.rect(0, RAIL - 6, W, H, gcol, ol=None)
    c.rect(0, RAIL + 8, W, RAIL + 40, (150, 140, 136), ol=None)
    for k in range(-1, W // 46 + 2):
        sx = k * 46 - near % 46
        c.rect(sx, RAIL + 4, sx + 24, RAIL + 16, (110, 80, 60), ol=None)
    c.line([(0, RAIL + 2), (W, RAIL + 2)], (70, 70, 80), 5, cap=False)
    c.rect(0, RAIL + 40, W, H, mix(gcol, (180, 190, 210), 0.3), ol=None)
    # the train, gently rocking
    rock = 1.5 * math.sin(near / 60) if (t < t_stop) else 0
    inside = train_inside(tl, t)
    P.train_car(c, 30, RAIL + rock, 560, False, inside, near / 40, height=300)
    c.rect(588, RAIL - 140 + rock, 612, RAIL - 50 + rock, (60, 60, 70), ol=None)
    P.train_car(c, 610, RAIL + rock * 0.7, 430, True, None, near / 40, height=300)
    # tunnel: a rocky mountain the train runs through
    if in_x is not None and in_x + L > -50 and in_x < W + 50:
        a, b = max(-50, in_x), min(W + 50, in_x + L)

        def top(x):
            u = clamp((x - in_x) / L)
            return 250 - 230 * math.sin(math.pi * u) ** 0.7 + 22 * math.sin((x - in_x) / 41)
        xs = np.linspace(a, b, 40)
        c.poly([(a, H)] + [(x, top(x)) for x in xs] + [(b, H)], (124, 110, 104), w=3)
        rng = np.random.default_rng(31)
        for k in range(70):                       # rock texture moving with the mountain
            rx, ry = in_x + rng.uniform(0, L), rng.uniform(0, H)
            if a < rx < b and ry > top(rx) + 20:
                c.ellipse(rx, ry, rng.uniform(20, 60), rng.uniform(8, 18),
                          mix((124, 110, 104), (70, 60, 60), rng.uniform(0.2, 0.5)), ol=None)
        for x in xs:                              # snowy crest
            if top(x) < 200:
                c.ellipse(x, top(x) + 6, 26, 10, P.SNOW, ol=None)
        for fx in (in_x, in_x + L):
            if -140 < fx < W + 140:
                c.ellipse(fx, H, 120, 460, (40, 34, 40), ol=None)
                c.ellipse(fx, H, 120, 460, None, ol=(150, 140, 130), w=16)
        for k in range(int(L // 300) + 1):
            lx = in_x + 150 + k * 300
            if a < lx < b:
                c.circle(lx, 300, 6, (255, 220, 140), ol=None)
    return finish(c, tl, t)



# ================================================================ cablecar

CCW, CCH = 1900, 2700
CA, CB = (150.0, 2250.0), (1640.0, 340.0)


def cable_bg():
    def make():
        c = Canvas(D.gradient(CCW * SS, CCH * SS, [(0, (60, 120, 214)), (0.5, (150, 200, 245)), (1, (215, 236, 255))]),
                   size=(CCW, CCH))
        # Mont Blanc dome seen beyond the needles, high up
        P.mont_blanc(c, 1100, 1250, 1.3, rock=(118, 116, 140))
        for x, base, w, h, sd in ((200, 1500, 500, 420, 1), (520, 1600, 420, 360, 2), (1700, 1550, 500, 380, 3)):
            P.peak(c, x, base, w, h, seed=sd, rock=(120, 128, 160), shade=(206, 218, 240), ol=(80, 84, 110))
        for x, y, s in ((300, 700, 1.4), (900, 1000, 1.1), (1500, 1300, 1.3), (200, 1200, 1.0)):
            D.cloud(c, x, y, s)
        # forested lower slopes and valley floor
        c.poly([(0, 1700), (400, 1760), (900, 1900), (CCW, 1880), (CCW, CCH), (0, CCH)], (232, 240, 250), ol=None)
        c.poly([(0, 2050), (CCW, 2020), (CCW, CCH), (0, CCH)], (150, 196, 120), ol=None)
        c.poly([(0, 2160), (CCW, 2200), (CCW, 2230), (0, 2190)], (120, 170, 220), ol=None)   # river
        rng = np.random.default_rng(41)
        for k in range(60):
            x = rng.uniform(0, CCW)
            y = 1800 + (x / CCW) * 80 + rng.uniform(0, 220)
            P.pine(c, x, y, rng.uniform(0.35, 0.6), snowy=y < 1950)
        for k, x in enumerate(range(100, CCW, 150)):
            P.chalet(c, x, 2280 + (k % 3) * 30, 0.35)
        P.church(c, 880, 2300, 0.4)
        # the great rock needle with the top station
        cliff = [(1150, CCH), (1180, 1900), (1300, 1500), (1400, 1100), (1500, 800), (1560, 520), (1600, 400),
                 (1660, 300), (1760, 300), (1790, 420), (1820, 700), (1860, 1100), (CCW, 1300), (CCW, CCH)]
        c.poly(cliff, (124, 116, 122), w=3)
        for k in range(26):
            y = rng.uniform(450, 2000)
            x = rng.uniform(1300, 1850) if y < 1200 else rng.uniform(1250, 1880)
            c.ellipse(x, y, 34, 7, mix(P.SNOW, (124, 116, 122), 0.25), ol=None)
            c.line([(x - 10, y + 40), (x + 14, y + 110)], (108, 100, 110), 3)
        c.rect(1640, 220, 1830, 330, (200, 200, 210), w=3)
        for wx in range(1660, 1820, 36):
            c.rect(wx, 240, wx + 22, 270, (120, 170, 210), w=2)
        c.rect(1610, 280, 1660, 330, (60, 60, 70), w=2)
        c.rect(1700, 140, 1712, 220, (180, 180, 190), w=2)              # antenna
        c.circle(1706, 136, 8, (220, 60, 60), w=2)
        # cables
        for off in (0, 10):
            c.line([(CA[0], CA[1] + off), (CB[0], CB[1] + off)], (50, 50, 60), 2.5, cap=False)
        c.rect(CA[0] - 60, CA[1] - 20, CA[0] + 60, CA[1] + 120, (200, 200, 210), w=3)
        return c.img
    return cached("cable", make)


def cablecar(tl, t):
    T = tl.t
    s0 = tl.scenes["cablecar"][0]
    u = lerp(0.12, 0.975, ease(clamp((t - T("cc_narr", 0.3)) / (T("cc_arrive", 0.8) - T("cc_narr", 0.3)))))
    gx, gy = lerp(CA[0], CB[0], u), lerp(CA[1], CB[1], u)
    sc = 1.45
    camx = clamp(gx - 600, 0, CCW - W)
    camy = clamp(gy - 190, 0, CCH - H)
    c = view(cable_bg(), camx, camy)
    c.push(-camx, -camy)
    # passing clouds in front (parallax)
    for k, (cx, cy) in enumerate(((400, 1500), (1300, 900), (700, 600), (1500, 1800))):
        D.cloud(c, cx + 30 * math.sin(t * 0.2 + k) + (camx * 0.3), cy + camy * 0.15, 1.3, col=(255, 255, 255))
    # eagles circling past while Luna points them out
    if T("cc_down", 0.5) < t < T("cc_pretty", 1):
        for k in range(2):
            a = (t - T("cc_down")) * 0.6 + k * 2.2
            D_x = gx + 380 * math.cos(a) + 60 * k
            D_y = gy + 250 + 140 * math.sin(a) - 120 * k
            P.eagle(c, D_x, D_y, t + k, 0.9, face=-1 if math.sin(a) > 0 else 1)
    peek = t >= T("cc_peek", 0.4)
    talking_l = tl.talking("luna", t)

    def inside(cc, R):
        jit = 0 if peek else 1.5 * math.sin(t * 40)
        wx, wy = R(-62, 214)
        kat(cc, tl, t, "whiskers", wx + jit, wy, 0.8, 1, "sit", scarf=True,
            eyes="closed" if not peek else ("happy" if t >= T("cc_pretty", 0.6) else "wide"),
            look=(1, 0.6), tail=0.0)
        lx, ly = R(62, 214)
        kat(cc, tl, t, "luna", lx + 10, ly, 0.76, -1 if talking_l else 1, "sit",
            eyes="happy" if T("cc_pretty", 0.5) <= t else "open", look=(1, 0.5) if not talking_l else (1, 0))
    swing = 0.035 * math.sin(t * 1.4) + (0.08 * math.sin((t - T("cc_arrive", 0.8)) * 9) *
                                         math.exp(-(t - T("cc_arrive", 0.8)) * 2) if t > T("cc_arrive", 0.8) else 0)
    P.cable_cabin(c, gx, gy, sc, swing, inside)
    c.pop()
    return finish(c, tl, t)


# ==================================================================== snow

SW_, SG = 1800, 600


def snow_bg():
    def make():
        c = Canvas(D.gradient(SW_ * SS, H * SS, [(0, (66, 136, 228)), (0.6, (196, 226, 255)), (1, (196, 226, 255))]),
                   size=(SW_, H))
        for x, w, h, sd in ((160, 420, 260, 1), (560, 380, 220, 2), (1700, 460, 280, 3)):
            P.peak(c, x, 480, w, h, seed=sd, rock=(120, 128, 160), shade=(206, 218, 240), ol=(80, 84, 110))
        P.mont_blanc(c, 1240, 486, 0.6, rock=(118, 116, 140))
        c.poly([(0, 470)] + [(x, 480 + 14 * math.sin(x / 140)) for x in range(0, SW_ + 40, 40)] + [(SW_, H), (0, H)],
               (234, 240, 252), ol=None)
        c.poly([(0, 560)] + [(x, 560 + 22 * math.sin(x / 210 + 1)) for x in range(0, SW_ + 40, 40)] + [(SW_, H), (0, H)],
               P.SNOW, ol=None)
        for x in range(0, SW_, 90):
            c.ellipse(x + 30, 640 + 30 * math.sin(x), 60, 6, (226, 234, 250), ol=None)
        # cable car top station on the left
        c.rect(-10, 330, 230, SG + 10, (200, 200, 212), w=3)
        c.rect(30, 360, 200, 420, (120, 170, 210), w=2.5)
        c.rect(150, 480, 210, SG + 10, (90, 90, 100), w=2.5)
        c.rect(-10, 320, 240, 336, P.SNOW, w=2.5, r=6)
        c.line([(0, 250), (60, 330)], (50, 50, 60), 3)
        # signpost to the summit
        c.rect(1480, 470, 1490, SG + 4, (130, 90, 60), w=2)
        c.poly([(1420, 476), (1570, 476), (1590, 494), (1570, 512), (1420, 512)], (230, 200, 90), w=2.5)
        c.text(1500, 494, "SOMMET 4808 m", 15, (60, 40, 30))
        # Margot's burrow
        c.ellipse(1060, SG + 2, 46, 14, (60, 50, 50), w=2.5)
        for x, s in ((330, 0.8), (1650, 0.9), (1760, 0.7)):
            P.pine(c, x, 500, s)
        return c.img
    return cached("snow", make)


def snow_drift(c, x, y, wob=0.0):
    P.snow_mound(c, x, y + 4, 125, 78 + wob)


def snow(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["snow"]
    camx = smooth(t, [(s0, 0), (T("sn_play", 0.35), 0), (T("sn_play", 0.7), 260), (T("sn_end"), 260),
                      (s1, 420)], 0.5)
    c = view(snow_bg(), camx)
    # clouds roll in at the end
    kc = ease(tl.prog("sn_clouds", t, 0.2, 1.0) * 0.7 + tl.prog("sn_end", t) * 0.3)
    c.push(-camx, 0)
    if kc > 0:
        for k in range(4):
            D.cloud(c, lerp(2100 + 200 * k, 1200 + 180 * k, kc), 120 + 60 * (k % 2), 1.6,
                    col=mix((240, 240, 250), (150, 156, 176), kc))
    DX = 840
    # --- Luna
    lj = tl.prog("sn_play", t, 0.03, 0.15)
    leyes = "happy" if T("sn_fun") <= t < T("sn_fun", 1) or T("sn_play", 0.25) <= t < T("sn_purpose", 1) else "open"
    if t < T("sn_play", 0.03):
        actor(c, tl, t, "luna", [(s0, 120), (T("sn_out", 0.8), 520)], SG + 2, eyes=leyes)
    elif t < T("sn_play", 0.15):
        kat(c, tl, t, "luna", lerp(520, 650, lj), SG + 2 + P_arc(lj, 110), 1.0, 1, "leap", eyes="happy")
    elif t < T("sn_play", 0.3):
        kat(c, tl, t, "luna", 650, SG + 6, 1.0, 1, "swim", eyes="happy", mouth=laughing(t))
    elif t < T("sn_end"):
        lx = smooth(t, [(T("sn_play", 0.3), 650), (T("sn_pop"), 650), (T("sn_pop", 0.9), 700)])
        face = -1 if T("sn_margot") <= t else 1
        kat(c, tl, t, "luna", lx, SG + 2, 1.0, 1 if T("sn_pop") <= t < T("sn_margot") or t >= T("sn_top") else face,
            "walk" if T("sn_pop") < t < T("sn_pop", 0.9) else "stand", walk=lx / 12, eyes=leyes, look=(1, -0.3))
        for k in range(5):                    # snow flecks on her fur
            c.circle(lx - 30 + 16 * k, SG - 70 + 9 * (k % 2), 4, P.SNOW, ol=None)
    else:
        actor(c, tl, t, "luna", [(T("sn_end"), 700), (s1 + 0.4, 1500)], SG + 2)
    # --- Whiskers
    wob = 0.0
    if t < T("sn_cold"):
        actor(c, tl, t, "whiskers", [(s0 + 0.5, 0), (T("sn_out", 1), 360)], SG, scarf=True)
    elif t < T("sn_play", 0.35):
        dance = t < T("sn_cold", 1) + 0.2
        hop = abs(math.sin(t * 11)) * 16 if dance else 0
        kat(c, tl, t, "whiskers", 360, SG - hop, 1.0, 1 if int(t * 3) % 2 or not dance else -1, "walk" if dance else "stand",
            scarf=True, walk=t * 22 if dance else 0, eyes="wide" if dance else "open")
    elif t < T("sn_play", 0.55):
        x = smooth(t, [(T("sn_play", 0.35), 360), (T("sn_play", 0.53), 690)], 0.15)
        kat(c, tl, t, "whiskers", x, SG, 1.0, 1, "walk", scarf=True, walk=x / 12)
    elif t < T("sn_play", 0.63):
        kat(c, tl, t, "whiskers", 690 + 2 * math.sin(t * 20), SG, 1.0, 1, "crouch", scarf=True,
            tail=math.sin(t * 9), eyes="wide")
    elif t < T("sn_play", 0.78):
        u = tl.prog("sn_play", t, 0.63, 0.78)
        kat(c, tl, t, "whiskers", lerp(690, DX, u), SG + P_arc(u, 150) + 30 * u * u, 1.0, 1, "leap", scarf=True,
            eyes="wide", mouth=0.5)
    # the drift (Whiskers inside it after the dive)
    inside = T("sn_play", 0.78) <= t < T("sn_end", 0.5)
    if inside:
        wob = 3 * math.sin(t * 16) if tl.talking("whiskers", t) else 0
        if t < T("sn_pop", 0.75):
            wave = math.sin(t * 6)
            pts = [(DX - 10 + 10 * math.sin(u * 3 + t * 5) * u + 40 * wave * u * u, SG - 70 - 100 * u) for u in np.linspace(0, 1, 8)]
            c.stroke(pts, D.WHISKERS["body"], 15)
            for k in (2, 5):
                c.line([pts[k], (pts[k][0] + 9, pts[k][1] - 5)], D.WHISKERS["dark"], 4)
    snow_drift(c, DX, SG, wob)
    if inside and t >= T("sn_pop", 0.75):
        kat(c, tl, t, "whiskers", DX - 30, SG - 58, 1.0, 1 if t < T("sn_margot") else 1, "swim",
            eyes="wide" if t < T("sn_pop", 0.9) else "open", look=(1, 0))
        c.ellipse(DX - 10, SG - 98, 26, 9, P.SNOW, ol=None)          # snow hat
    if T("sn_play", 0.78) <= t < T("sn_play", 0.95) or T("sn_pop", 0.75) <= t < T("sn_pop", 0.95):
        t0 = T("sn_play", 0.78) if t < T("sn_play", 0.95) else T("sn_pop", 0.75)
        poof(c, DX, SG - 50, t - t0)
    if T("sn_play", 0.15) <= t < T("sn_play", 0.3):
        poof(c, 650, SG - 20, t - T("sn_play", 0.15))
    if t >= T("sn_end", 0.5):
        actor(c, tl, t, "whiskers", [(T("sn_end", 0.5), DX - 30), (s1 + 0.6, 1500)], SG, scarf=True)
    # --- Margot pops out of her burrow
    if t >= T("sn_pop", 0.1):
        pop = ease((t - T("sn_pop", 0.1)) / 0.35)
        if t < T("sn_end"):
            face = 1 if t >= T("sn_clouds", 0.25) else -1
            P.margot(c, 1060, SG + 70 * (1 - pop), 1.3, face, t, mouth=tl.mouth("margot", t),
                     eyes="wide" if t < T("sn_margot") else "open", wave=1.0 if t >= T("sn_clouds", 0.25) else 0.0,
                     hop=abs(math.sin(t * 9)) * 8 if T("sn_margot") <= t < T("sn_margot", 0.4) else 0)
        else:
            actor(c, tl, t, "margot", [(T("sn_end"), 1060), (s1 + 0.4, 1800)], SG + 2, 1.3)
        c.rect(1000, SG + 2, 1120, SG + 120, P.SNOW, ol=None)
        c.arc(1060, SG + 2, 46, 14, 0, 180, OUT, 2.5)
    c.pop()
    P.snowfall(c, t, n=40, seed=5, speed=30, drift=10, size=(1.2, 2.6))
    if kc > 0:
        P.overlay(c, (120, 128, 156), 0.3 * kc)
    return finish(c, tl, t)


def P_arc(u, h):
    return -4 * h * u * (1 - u)


def poof(c, x, y, dt):
    """A burst of snow puffs, dt seconds after impact."""
    if dt < 0 or dt > 0.9:
        return
    rng = np.random.default_rng(int(x))
    for k in range(14):
        a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        sp = rng.uniform(150, 360)
        px = x + math.cos(a) * sp * dt
        py = y + math.sin(a) * sp * dt + 500 * dt * dt
        r = rng.uniform(8, 20) * (1 - dt / 0.9)
        c.circle(px, py, r, P.SNOW, ol=(190, 205, 230), w=1.5)


# =================================================================== storm

STW, STG = 3100, 610
FOG = (222, 226, 238)


def storm_bg():
    def make():
        c = Canvas(D.gradient(STW * SS, H * SS, [(0, (120, 130, 158)), (0.7, (196, 202, 220)), (1, (196, 202, 220))]),
                   size=(STW, H))
        for k in range(8):
            P.peak(c, 200 + k * 400, 500, 520, 260, rock=(150, 156, 178), snow=(214, 220, 234),
                   shade=(190, 198, 218), seed=k, ol=None)
        c.poly([(0, 520)] + [(x, STG - 20 + 16 * math.sin(x / 170)) for x in range(0, STW + 40, 40)] + [(STW, H), (0, H)],
               (236, 240, 248), ol=None)
        rng = np.random.default_rng(51)
        for k in range(18):
            x = rng.uniform(0, STW)
            P.pine(c, x, STG - 30, rng.uniform(0.5, 0.8), col=(110, 130, 130), dark=(96, 112, 116))
        for x in range(0, STW, 120):
            c.ellipse(x + 40, 660 + 20 * math.sin(x * 0.7), 80, 8, (222, 228, 240), ol=None)
        # the big rock where Luna shelters
        c.poly([(1520, STG + 10), (1540, 520), (1600, 470), (1680, 490), (1720, 560), (1730, STG + 10)], (120, 116, 128), w=3)
        c.poly([(1540, 520), (1600, 466), (1680, 486), (1620, 500)], P.SNOW, w=2)
        return c.img
    return cached("storm", make)


def ding(c, x, y, dt):
    """Golden rings and a little bell icon: the sound of Luna's bell through the storm."""
    if not 0 <= dt < 1.0:
        return
    for k in range(3):
        u = dt * 1.4 - k * 0.2
        if 0 < u < 1:
            r = 20 + 90 * u
            col = mix((250, 205, 60), FOG, u)
            c.arc(x, y, r, r, 120, 240, col, 5 * (1 - u) + 1)
    if dt < 0.8:
        c.circle(x + 10, y - 4, 13, (250, 210, 70), w=2.5)
        c.circle(x + 10, y + 4, 3, OUT, ol=None)


def storm(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["storm"]
    # Whiskers' path; the camera follows him, then Bruno
    wk = [(s0, 180), (T("st_narr", 0.9), 520), (T("st_walk"), 520), (T("st_walk", 0.85), 1380)]
    bk = [(T("st_bark"), 2150), (T("st_bark", 1), 1640), (T("st_carry"), 1640), (s1, 2650)]
    wx = smooth(t, wk)
    if t < T("st_carry"):
        focus = wx
    else:
        focus = smooth(t, bk)
    if T("st_bark") <= t < T("st_carry"):
        focus = lerp(wx, 1560, ease(tl.prog("st_bark", t)))
    camx = clamp(focus - 520, 0, STW - W)
    c = view(storm_bg(), camx)
    c.push(-camx, 0)
    fog = smooth(t, [(s0, 0.2), (T("st_narr", 0.3), 0.3), (T("st_narr", 0.95), 0.94), (T("st_where", 0.1), 0.94),
                     (T("st_where", 0.7), 0.42), (T("st_carry"), 0.42), (s1, 0.25)], 0.2)
    lost = T("st_narr", 0.85) <= t < T("st_walk", 0.5)
    # Bruno's chalet glowing ahead (only at the end)
    if t >= T("st_carry"):
        c.tint = (FOG, 0.55)
        P.chalet(c, 2930, STG - 6, 1.1, lit=True)
        c.tint = None
        c.glow(2905, STG - 90, 60, 40, (255, 220, 140), (226, 220, 220), steps=6)
    # Luna and Margot: walking with him at first, sheltering by the rock later
    if t < T("st_narr", 0.85):
        lx = smooth(t, [(s0, 330), (T("st_narr", 0.9), 690)])
        kat(c, tl, t, "luna", lx, STG + 2, 1.0, 1, "walk", walk=lx / 12, head_dy=8, eyes="closed")
        mx = smooth(t, [(s0, 450), (T("st_narr", 0.9), 820)])
        P.margot(c, mx, STG + 2, 1.2, 1, t, walk=mx / 7)
    elif t >= T("st_walk", 0.5) and t < T("st_carry"):
        happy = t >= T("st_walk", 0.85)
        ring = math.sin(t * 20) * 4 if t < T("st_walk", 0.9) else 0
        kat(c, tl, t, "luna", 1490, STG + 2, 1.0, -1, "stand", eyes="happy" if happy else "open", head_dy=ring)
        P.margot(c, 1580, STG + 2, 1.2, -1, t, mouth=tl.mouth("margot", t), eyes="happy" if happy else "open")
    # Whiskers
    if t < T("st_carry"):
        if T("st_alone") <= t < T("st_bell", 0.3):
            shiver = 2 * math.sin(t * 50)
            kat(c, tl, t, "whiskers", wx + shiver, STG, 1.0, 1, "sit", scarf=True, eyes="open", look=(0, 0.6),
                head_dy=6)
        else:
            mv = abs(speed(t, wk)) > 20
            looking = T("st_where") <= t < T("st_alone")
            face = (1 if int((t - T("st_where")) * 2.5) % 2 else -1) if looking else 1
            perk = T("st_bell", 0.3) <= t < T("st_walk")
            kat(c, tl, t, "whiskers", wx, STG, 1.0, 1 if mv else face, "walk" if mv else "stand", scarf=True,
                walk=wx / 12 if mv else 0, eyes="wide" if perk or looking else
                ("happy" if t >= T("st_walk", 0.85) else "open"),
                head_dy=8 if (mv and t < T("st_narr", 0.9)) else 0, look=(1, -0.3))
    # Bruno emerges from the white with his lantern
    if t >= T("st_bark"):
        bx = smooth(t, bk)
        near = clamp((2200 - bx) / 500) if t < T("st_carry") else 0.85
        c.tint = (FOG, 0.85 * (1 - near))
        face = -1 if t < T("st_carry") else 1
        mv = abs(speed(t, bk)) > 15
        P.bruno(c, bx, STG + 4, 0.85, face, t, walk=bx / 22 if mv else 0, mouth=tl.mouth("bruno", t), lantern=True)
        c.tint = None
        if t >= T("st_back", 0.85):
            # riding on his back: Whiskers and Luna, Margot on his head
            hop = clamp((t - T("st_back", 0.85)) / 0.4)
            f = face
            bob = abs(math.sin(bx / 22)) * 3 if mv else 0
            kat(c, tl, t, "luna", bx - 52 * 0.85 * f, lerp(STG, STG - 150, ease(hop)) - bob, 0.62, f, "sit",
                eyes="happy")
            kat(c, tl, t, "whiskers", bx + 18 * 0.85 * f, lerp(STG, STG - 154, ease(hop)) - bob, 0.62, f, "sit",
                scarf=True, eyes="happy")
            P.margot(c, bx + 110 * 0.85 * f, lerp(STG, STG - 222, ease(hop)) - bob, 0.8, f, t, eyes="happy")
    # bell rings drawn through the storm
    for e in ("st_bell", "st_follow", "st_walk"):
        for name, frac in tl.ev(e).sfx:
            if name == "jingle":
                bxp = 1490 if t > T("st_walk") else camx + W - 80
                ding(c, bxp, STG - 120, t - T(e, frac))
    c.pop()
    P.overlay(c, FOG, fog * (0.75 if not lost else 1.0))
    P.snowfall(c, t, n=200, seed=7, speed=320, drift=-380, size=(1.5, 4.5), streak=3.0,
               camx=camx, parallax=0.3)
    P.snowfall(c, t, n=40, seed=8, speed=420, drift=-500, size=(4, 7), camx=camx, parallax=0.6)
    return finish(c, tl, t)


# ================================================================== chalet

TABLE_Y = 520
POT = (800, 520)


def chalet_bg():
    def make():
        c = Canvas(bg=(150, 96, 58))
        for k, y in enumerate(range(0, 560, 34)):
            c.rect(0, y, W, y + 34, (164, 106, 64) if k % 2 else (150, 96, 58), ol=None)
            c.line([(0, y + 33), (W, y + 33)], (110, 66, 40), 2, cap=False)
            for x in range((k * 157) % 300, W, 300):
                c.ellipse(x, y + 17, 9, 5, (130, 82, 50), ol=None)
        c.rect(0, 556, W, H, (128, 82, 50), ol=None)
        for x in range(-40, W, 110):
            c.line([(x, 560), (x - 60, H)], (104, 66, 40), 2, cap=False)
        # window with the night outside
        c.rect(1030, 140, 1230, 360, (36, 46, 96), w=6)
        c.line([(1130, 140), (1130, 360)], (110, 66, 40), 6, cap=False)
        c.line([(1030, 250), (1230, 250)], (110, 66, 40), 6, cap=False)
        c.rect(1018, 356, 1242, 372, (170, 110, 70), r=3)
        for x0, x1 in ((990, 1040), (1220, 1270)):
            c.rect(x0, 120, x1, 400, (196, 50, 56), r=8)
            for yy in range(130, 400, 24):
                c.line([(x0 + 4, yy), (x1 - 4, yy)], (230, 220, 210), 2, cap=False)
        # shelf with cheese wheels and a cowbell
        c.rect(500, 200, 900, 214, (110, 70, 44))
        for x, r in ((560, 34), (640, 28), (710, 30)):
            c.ellipse(x, 182, r, 18, (250, 200, 90))
            c.poly([(x, 182), (x + r, 176), (x + r, 190)], (255, 236, 160), ol=None)
        c.poly([(800, 160), (840, 160), (850, 198), (790, 198)], (220, 180, 70))
        c.line([(790, 160), (850, 160)], (200, 40, 50), 5)
        # skis leaning on the wall
        for dx in (0, 22):
            c.rect(1170 + dx, 400, 1184 + dx, 640, (220, 70, 60), r=7)
        # fireplace
        c.rect(40, 230, 400, 252, (120, 76, 46), r=3)
        c.rect(60, 252, 380, 560, (150, 146, 150))
        for y in range(262, 560, 36):
            for x in range(60 + (y // 36 % 2) * 30, 380, 60):
                c.rect(x + 2, y, x + 56, y + 32, (166, 162, 168), w=1.5, r=4)
        c.rect(110, 380, 330, 560, (40, 26, 22), w=3, r=10)
        c.rect(100, 0, 340, 230, (150, 146, 150))
        # rug and table
        c.ellipse(250, 630, 230, 46, (190, 60, 60))
        c.ellipse(250, 630, 190, 34, (220, 100, 80), ol=None)
        c.rect(590, 520, 610, 700, (110, 70, 44))
        c.rect(970, 520, 990, 700, (110, 70, 44))
        # hanging lamp
        c.line([(790, 0), (790, 70)], OUT, 3)
        c.poly([(750, 100), (790, 66), (830, 100)], (60, 90, 70))
        c.glow(790, 104, 60, 26, (255, 240, 180), (164, 106, 64), steps=6)
        return c.img
    return cached("chalet", make)


def table_front(c):
    c.rect(556, TABLE_Y, 1024, TABLE_Y + 16, (240, 236, 226), w=2.5)
    for x in range(556, 1024, 26):
        c.rect(x, TABLE_Y, x + 13, TABLE_Y + 16, (200, 50, 56), ol=None)
    c.poly([(556, TABLE_Y + 16), (1024, TABLE_Y + 16), (1014, TABLE_Y + 66), (566, TABLE_Y + 66)],
           (236, 232, 222), w=2.5)
    for x in range(570, 1010, 40):
        c.rect(x, TABLE_Y + 18, x + 20, TABLE_Y + 64, (205, 60, 64), ol=None)
    for y in range(TABLE_Y + 26, TABLE_Y + 64, 20):
        c.line([(566, y), (1014, y)], (205, 60, 64), 4, cap=False)


def fire(c, t, x=220, y=556):
    c.glow(x, y - 66, 100, 64, (255, 170, 80), (40, 26, 22), steps=8)
    c.rect(x - 70, y - 20, x + 70, y - 6, (100, 60, 40), w=2, r=5)
    for k in range(5):
        fx = x - 56 + k * 28
        h = 70 + 30 * math.sin(t * 7 + k * 1.7) + 15 * math.sin(t * 13 + k)
        sway = 8 * math.sin(t * 5 + k)
        c.poly([(fx - 18, y - 12), (fx + sway, y - 12 - h), (fx + 18, y - 12)], (255, 130, 50), ol=None)
        c.poly([(fx - 9, y - 12), (fx + sway * 0.7, y - 12 - h * 0.6), (fx + 9, y - 12)], (255, 220, 100), ol=None)


def cheese_string(c, a, b, thick):
    pts = []
    for u in np.linspace(0, 1, 14):
        x = lerp(a[0], b[0], u)
        y = lerp(a[1], b[1], u) + 40 * math.sin(math.pi * u) * (1 - abs(a[1] - b[1]) / 400)
        pts.append((x, y))
    c.line(pts, (220, 170, 60), thick + 3)
    c.line(pts, (255, 214, 90), thick)


def chalet(tl, t):
    T = tl.t
    c = Canvas(chalet_bg().copy())
    fire(c, t)
    P.snowfall(c, t, n=30, seed=11, speed=40, drift=12, size=(1.5, 3), region=(1036, 146, 1224, 354))
    c.rect(1030, 140, 1230, 360, None, w=6)
    c.line([(1130, 140), (1130, 360)], (110, 66, 40), 6, cap=False)
    c.line([(1030, 250), (1230, 250)], (110, 66, 40), 6, cap=False)
    asleep = t >= T("ch_zzz")
    if asleep:
        table_front(c)
        fondue_pot(c, POT[0], POT[1] + 4, 1.05, t, steam=False)
        P.overlay(c, (30, 24, 60), 0.38)
        fire(c, t)
        c.tint = ((60, 40, 60), 0.2)
        P.bruno(c, 520, 692, 0.85, -1, t, sit=True, eyes="closed")
        kat(c, tl, t, "luna", 150, 664, 0.9, 1, "sleep", mouth=0)
        kat(c, tl, t, "whiskers", 300, 672, 0.9, 1, "sleep", mouth=0)
        P.margot(c, 420, 668, 0.95, -1, t, eyes="closed")
        c.tint = None
        D.zzz(c, 330, 580, t)
        return finish(c, tl, t)
    # Bruno by the fire
    P.bruno(c, 420, 692, 0.85, 1, t, sit=True, mouth=tl.mouth("bruno", t),
            eyes="happy" if T("ch_win") <= t < T("ch_munch", 1) else "open")
    # Whiskers and the great cheese pull
    dip = tl.prog("ch_dip", t)
    pull = clamp(tl.prog("ch_dip", t, 0.3, 1.0) * 0.6 + tl.prog("ch_win", t) * 0.4)
    snapped = t >= T("ch_munch", 0.1)
    ws = 1.15
    WY = 566
    if T("ch_dip", 0.3) <= t < T("ch_munch", 0.1):
        wx = lerp(650, 600, ease(pull))
        kat(c, tl, t, "whiskers", wx, WY, ws, 1, "stand", scarf=True, eyes="wide" if pull > 0.5 else "open",
            look=(1, -0.8), squash=1.0)
        paw = (wx + 46, WY - 74)
    else:
        sit_x = 650
        mouth = laughing(t, 0.7) * 0.6 if T("ch_munch", 0.2) <= t < T("ch_sorry") else tl.mouth("whiskers", t)
        kat(c, tl, t, "whiskers", sit_x, WY, ws, 1, "sit", scarf=True, mouth=mouth,
            eyes="happy" if (T("ch_munch", 0.2) <= t < T("ch_sorry") or T("ch_bell", 0.5) <= t) else "open",
            look=(1, 0) if t < T("ch_sorry") else (1, 0))
        paw = (sit_x + 40, WY - 58)
    # fork and cheese
    pot_top = (POT[0] - 6, POT[1] - 86 * 1.05)
    if t < T("ch_dip", 0.3):
        tip = (lerp(paw[0] + 50, pot_top[0], ease(dip / 0.3)), lerp(paw[1] - 20, pot_top[1] + 4, ease(dip / 0.3)))
    elif not snapped:
        tip = (lerp(pot_top[0] - 20, 760, ease(pull)), lerp(pot_top[1] - 10, 190, ease(pull)))
    else:
        u = clamp((t - T("ch_munch", 0.1)) / 0.35)
        tip = (lerp(760, paw[0] + 40, u), lerp(190, paw[1] - 40, u))
    c.tint = None
    # the fondue pot sits on the table (drawn before the table front so its stand hides behind the cloth)
    if T("ch_dip", 0.25) <= t < T("ch_munch", 0.1):
        cheese_string(c, pot_top, tip, lerp(10, 3, pull))
    # Luna across the table
    sad = T("ch_sorry") <= t < T("ch_bell", 0.5)
    kat(c, tl, t, "luna", 975, WY, 1.15, -1, "sit", eyes="closed" if sad else (
        "happy" if T("ch_win") <= t < T("ch_munch", 1) or t >= T("ch_bell", 0.5) else "open"),
        head_dy=6 if sad else 0, mouth=laughing(t) * 0.7 if T("ch_win", 0.6) <= t < T("ch_munch", 1) else tl.mouth("luna", t))
    table_front(c)
    fondue_pot(c, POT[0], POT[1] + 4, 1.05, t)
    # Margot on the table, hopping with laughter
    hop = abs(math.sin(t * 9)) * 8 if T("ch_munch") <= t < T("ch_munch", 1) else 0
    P.margot(c, 895, TABLE_Y + 2, 1.15, -1, t, mouth=tl.mouth("margot", t), hop=hop,
             eyes="happy" if T("ch_munch") <= t < T("ch_munch", 1) else "open",
             wave=1.0 if T("ch_win") <= t < T("ch_win", 1) else 0.0)
    if T("ch_dip", 0.25) <= t:
        c.line([paw, tip], (150, 150, 160), 4)
        c.circle(tip[0], tip[1], 9, (255, 214, 90) if not snapped or t < T("ch_munch", 0.4) else (230, 190, 120),
                 w=2)
    if snapped and t < T("ch_munch", 1):
        c.ellipse(paw[0] + 4, paw[1] - 70, 20, 10, (255, 214, 90), w=2)       # cheese on his nose
    return finish(c, tl, t)


# ================================================================== summit

def ridge_y(x):
    if x < 0:
        return 760 - 0.7 * x
    if x < 520:
        return 760 - 380 * (x / 520) ** 0.85
    if x < 880:
        return 380 - 8 * math.sin((x - 520) / 360 * math.pi)
    return 380 + 260 * ((x - 880) / 220) ** 1.3


def summit_layers(dawn):
    def make():
        if dawn:
            sky = [(0, (90, 120, 200)), (0.35, (240, 160, 170)), (0.62, (255, 210, 150)), (1, (255, 226, 180))]
            cl, cl_sh, snow, shade = (255, 236, 226), (236, 186, 190), (255, 244, 236), (236, 196, 206)
            far = dict(rock=(150, 120, 150), snow=(255, 228, 220), shade=(230, 186, 200), ol=(110, 80, 110))
        else:
            sky = [(0, (14, 20, 56)), (0.5, (40, 52, 110)), (0.75, (90, 90, 150)), (1, (110, 106, 160))]
            cl, cl_sh, snow, shade = (130, 140, 186), (100, 108, 156), (170, 184, 224), (130, 140, 190)
            far = dict(rock=(70, 74, 110), snow=(150, 160, 206), shade=(120, 128, 180), ol=(30, 34, 60))
        sk = Canvas(D.gradient(W * SS, H * SS, sky))
        if not dawn:
            D.stars(sk, 12, 160, W, 380)
        fg = Canvas(Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)))
        for x, w, h, sd in ((150, 300, 150, 1), (420, 240, 110, 2), (1180, 280, 130, 3)):
            P.peak(fg, x, 520, w, h, seed=sd, cap=0.6, **far)
        rng = np.random.default_rng(61)
        fg.rect(0, 540, W, H, cl, ol=None)
        for k in range(22):
            x = rng.uniform(-50, W + 50)
            y = rng.uniform(500, 680)
            P.soft_cloud(fg, x, y, rng.uniform(0.8, 1.6), col=cl, shade=cl_sh)
        pts = [(x, ridge_y(x)) for x in range(0, W + 20, 20)]
        fg.poly(pts + [(W, H), (0, H)], snow, w=3)
        fg.poly([(880, 380)] + [(x, ridge_y(x)) for x in range(880, W + 20, 20)] + [(W, H), (900, H)], shade, ol=None)
        fg.poly([(0, 760), (260, 600), (500, 400), (560, H), (0, H)], mix(snow, shade, 0.35), ol=None)
        for k in range(10):
            P.soft_cloud(fg, 1000 + 70 * k + rng.uniform(-30, 30), 640 + rng.uniform(0, 70), 1.1, col=cl, shade=cl_sh)
        rockc = far["rock"]
        for x0, dy, w_ in ((120, 60, 50), (300, 90, 70), (420, 150, 40), (980, 70, 60), (1120, 40, 80), (220, 170, 60)):
            y0 = ridge_y(x0) + dy
            fg.poly([(x0 - w_, y0 + 14), (x0 - w_ * 0.3, y0 - 18), (x0 + w_ * 0.4, y0 - 10), (x0 + w_, y0 + 14)],
                    rockc, w=2.5)
            fg.poly([(x0 - w_ * 0.5, y0 - 8), (x0 - w_ * 0.3, y0 - 18), (x0 + w_ * 0.4, y0 - 10), (x0 + w_ * 0.2, y0 - 4)],
                    snow, ol=None)
        for k in range(9):
            x0 = 40 + 110 * k
            y0 = ridge_y(x0) + 60 + 40 * (k % 3)
            fg.line([(x0, y0), (x0 + 90, y0 - 28 if x0 < 520 else y0 + 10)], shade, 3)
        # summit marker
        fg.line([(700, 374), (700, 284)], (90, 70, 60), 5)
        fg.poly([(700, 286), (760, 300), (700, 316)], (220, 50, 60), w=2)
        return sk.img, fg.img
    return cached(("summit", dawn), make)


def summit_close_bg():
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (100, 130, 210)), (0.4, (246, 170, 170)), (0.66, (255, 214, 156)),
                                               (1, (255, 230, 186))]))
        return c.img

    def make_fg():
        fg = Canvas(Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)))
        rng = np.random.default_rng(62)
        fg.rect(0, 470, W, H, (255, 236, 226), ol=None)
        for k in range(16):
            P.soft_cloud(fg, rng.uniform(-50, W + 50), rng.uniform(430, 560), rng.uniform(1.0, 1.8),
                         col=(255, 236, 226), shade=(240, 196, 196))
        fg.poly([(0, 560), (300, 540), (700, 556), (1000, 590), (W, 620), (W, H), (0, H)], (255, 246, 240), w=3)
        fg.poly([(0, 640), (500, 630), (W, 680), (W, H), (0, H)], (240, 214, 220), ol=None)
        return fg.img
    return cached("summit_close", make), cached("summit_close_fg", make_fg)


def summit(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["summit"]
    if t >= T("su_above"):
        return summit_close(tl, t)
    k = ease(tl.prog("su_sunrise", t, 0.0, 0.85))
    (sk0, fg0), (sk1, fg1) = summit_layers(False), summit_layers(True)
    sky = sk0 if k <= 0 else sk1 if k >= 1 else Image.blend(sk0, sk1, k)
    c = Canvas(sky.copy())
    sy = lerp(660, 290, ease(tl.prog("su_sunrise", t, 0.05, 1.0)))
    if t >= T("su_sunrise"):
        P.sun(c, 1090, sy, 46, t, rays=k > 0.5, sky=mix((110, 106, 160), (255, 214, 160), k))
    fg = fg0 if k <= 0 else fg1 if k >= 1 else Image.blend(fg0, fg1, k)
    c.img.paste(fg, (0, 0), fg)
    # the rope team climbs the ridge
    lead = smooth(t, [(s0, -60), (T("su_narr", 1), 520), (T("su_top", 0.8), 830)], 0.4)
    order = [("bruno", 0, 0.62), ("luna", 115, 0.72), ("whiskers", 210, 0.72), ("margot", 290, 0.75)]
    if t >= T("su_top", 0.8):
        spots = {"bruno": 830, "luna": 715, "whiskers": 620, "margot": 540}
    else:
        spots = {who: lead - off for who, off, _ in order}
    moving = abs(speed(t, [(s0, -60), (T("su_narr", 1), 520), (T("su_top", 0.8), 830)])) > 10
    c.tint = (mix((40, 50, 110), (255, 170, 120), k), lerp(0.4, 0.12, k))
    anchors = []
    for who, off, s in order:
        x = spots[who]
        y = ridge_y(x) + 4
        face = 1
        if who == "bruno":
            P.bruno(c, x, y, s, face, t, walk=x / 13 if moving else 0, mouth=tl.mouth("bruno", t),
                    eyes="happy" if t > T("su_sunrise", 0.5) else "open")
            anchors.append((x - 20 * s, y - 120 * s))
        elif who == "margot":
            jump = abs(math.sin(t * 8)) * 18 if T("su_made") <= t < T("su_made", 1) else 0
            P.margot(c, x, y, s, face, t, walk=x / 4 if moving else 0, mouth=tl.mouth("margot", t), hop=jump,
                     eyes="happy" if T("su_made") <= t else "open", wave=1.0 if T("su_made") <= t < T("su_made", 1) else 0)
            anchors.append((x, y - 30 * s - jump))
        else:
            kat(c, tl, t, who, x, y, s, face, "walk" if moving else "stand", scarf=True, walk=x / 7 if moving else 0,
                eyes="happy" if t > T("su_sunrise", 0.6) else "open", look=(1, -0.4))
            anchors.append((x - 6, y - 50 * s))
    for a, b in zip(anchors, anchors[1:]):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 14)
        c.line([a, mid, b], (220, 70, 60), 3)
    c.tint = None
    return finish(c, tl, t)


def summit_close(tl, t):
    T = tl.t
    sk, fg = summit_close_bg()
    c = Canvas(sk.copy())
    P.sun(c, 1010, 330, 60, t, sky=(249, 184, 166), halo=(255, 226, 172))
    c.img.paste(fg, (0, 0), fg)
    lean = ease(tl.prog("su_hold", t, 0.0, 0.4))
    turn = t >= T("su_thanks") - 0.2
    kat(c, tl, t, "luna", lerp(430, 470, lean), 600, 1.25, 1, "sit",
        eyes="happy" if t >= T("su_pillows") else "open", look=(1, -0.3))
    kat(c, tl, t, "whiskers", 650, 604, 1.3, -1 if turn else 1, "sit", scarf=True,
        eyes="happy" if (t >= T("su_hold") or T("su_pillows", 0.6) <= t < T("su_thanks")) else "open",
        look=(1, -0.3), head_dy=4 * lean)
    P.margot(c, 880, 616, 1.2, 1, t, eyes="happy")
    P.snowfall(c, t, n=24, seed=13, speed=20, drift=8, size=(1.5, 3), col=(255, 240, 210))
    return finish(c, tl, t)


# ==================================================================== sled

SLOPE = 0.36


def sled_y(x):
    if x < 3600:
        return 260 + SLOPE * x
    if x < 4400:
        u = x - 3600
        return 260 + SLOPE * 3600 + SLOPE * (u - u * u / 1600)
    return 260 + SLOPE * 3600 + SLOPE * 400


def sled_dy(x):
    if x < 3600:
        return SLOPE
    if x < 4400:
        return SLOPE * (1 - (x - 3600) / 800)
    return 0.0


def sled_sky():
    def make():
        c = Canvas(D.gradient(2 * W * SS, (H + 220) * SS, [(0, (70, 140, 230)), (0.6, (200, 228, 255)),
                                                           (1, (200, 228, 255))]), size=(2 * W, H + 220))
        for k in range(7):
            P.peak(c, 150 + k * 380, 600, 480, 300, seed=k + 20, rock=(120, 128, 160), shade=(206, 218, 240),
                   ol=(80, 84, 110))
        P.mont_blanc(c, 1700, 610, 0.6, rock=(118, 116, 140))
        for x in (300, 1100, 1900):
            D.cloud(c, x, 140, 0.9)
        return c.img
    return cached("sled_sky", make)


def sled_pines():
    rng = np.random.default_rng(71)
    out = []
    for k in range(40):
        x = 200 + k * 130 + rng.uniform(-40, 40)
        out.append((x, rng.uniform(0.6, 1.0), rng.random() < 0.35))
    return out


DRIFT_X = 4720


def sled(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["sled"]
    t_go, t_end = T("sl_ride", 0.05), T("sl_crash", 0.12)
    u = clamp((t - t_go) / (t_end - t_go))
    sx = 300 + (DRIFT_X - 180 - 300) * (u ** 1.7 * 0.6 + u * 0.4)
    sy = sled_y(sx)
    focus = sx if t < T("sl_crash") else lerp(sx, DRIFT_X - 80, ease(tl.prog("sl_crash", t, 0, 0.5)))
    camx = focus - 520
    camy = sled_y(focus) - lerp(430, 590, 1 - sled_dy(focus) / SLOPE)
    sky = sled_sky()
    ox = int(clamp(camx * 0.12, 0, W - 1))
    oy = int(clamp(camy * 0.1, 0, 219))
    c = Canvas(sky.crop((ox * SS, oy * SS, (ox + W) * SS, (oy + H) * SS)))
    c.push(-camx, -camy)
    # slope
    xs = np.arange(camx - 40, camx + W + 80, 40)
    surf = [(x, sled_y(x)) for x in xs]
    c.poly(surf + [(xs[-1], camy + H + 10), (xs[0], camy + H + 10)], P.SNOW, w=3)
    c.poly([(x, y + 30) for x, y in surf] + [(x, y + 80) for x, y in surf[::-1]], (226, 234, 250), ol=None)
    pines = sled_pines()
    for x, s, front in pines:
        if not front and camx - 100 < x < camx + W + 100:
            P.pine(c, x, sled_y(x) - 4, s)
    # village at the bottom
    for k, x in enumerate((5050, 5250, 5450)):
        if x - 200 < camx + W:
            P.chalet(c, x, sled_y(x) - 2, 0.9, snow_roof=True)
    # the drift
    crash = t >= T("sl_crash", 0.12)
    dy0 = sled_y(DRIFT_X)
    riders = [("margot", 120), ("whiskers", 55), ("luna", -25), ("bruno", -110)]
    if not crash:
        ang = math.atan(sled_dy(sx))
        bump = abs(math.sin(sx / 90)) * 8 if t > t_go else 0
        ca, sa = math.cos(ang), math.sin(ang)
        bs = 1.1
        # snow spray from the runners
        if t > t_go:
            rng = np.random.default_rng(3)
            for k in range(18):
                age = (t * 2.5 + k / 18) % 1.0
                bx = sx - 150 * bs * ca - age * 160 + rng.uniform(-20, 20)
                by = sy - 150 * bs * sa - 50 * age + 160 * age * age - rng.uniform(0, 30) * age
                c.circle(bx, by, 10 * (1 - age) + 2, P.SNOW, ol=(200, 214, 236), w=1.5)
        for who, lx in riders:
            px = sx + (lx * ca + 30 * sa) * bs
            py = sy + (lx * sa - 30 * ca) * bs - bump
            if who == "bruno":
                P.bruno(c, px, py + 40, 0.58, 1, t, sit=True, mouth=tl.mouth("bruno", t),
                        eyes="happy" if t > t_go else "open")
            elif who == "margot":
                P.margot(c, px, py, 0.85, 1, t, eyes="happy" if t > t_go else "open", mouth=tl.mouth("margot", t))
            else:
                wide = who == "whiskers" and t_go < t < T("sl_ride", 0.45)
                kat(c, tl, t, who, px, py, 0.76, 1, "sit", scarf=True,
                    eyes="wide" if wide else ("happy" if t > t_go else "open"),
                    mouth=0.7 if wide else tl.mouth(who, t), head_dy=-4 if wide else 0)
        P.sled(c, sx, sy - bump, bs, ang)
        P.snow_mound(c, DRIFT_X, dy0 + 2, 250, 130)
    else:
        dt = t - T("sl_crash", 0.12)
        ub = tl.prog("sl_crash", t, 0.12, 0.4)
        P.sled(c, DRIFT_X - 300, dy0, 1.1, 0.0)
        out = t >= T("sl_bye") - 0.3
        if ub < 1:
            # everyone flies into the drift
            for k, (who, lx) in enumerate(riders):
                x0, x1 = DRIFT_X - 300 + lx * 1.1, DRIFT_X - 140 + 80 * k
                px = lerp(x0, x1, ub)
                py = lerp(dy0 - 30, dy0 - 80, ub) - 260 * ub * (1 - ub) * (1 + 0.3 * k)
                if who in ("whiskers", "luna"):
                    kat(c, tl, t, who, px, py, 0.76, 1, "leap", eyes="wide", mouth=0.6, scarf=True)
                elif who == "margot":
                    P.margot(c, px, py, 0.85, 1, t, eyes="wide")
                else:
                    P.bruno(c, px, py, 0.58, 1, t, eyes="wide", mouth=0.5)
        if not out:
            if ub >= 1:
                P.bruno(c, DRIFT_X + 110, dy0 - 100, 0.62, -1, t, sit=True, eyes="happy", mouth=tl.mouth("bruno", t))
        P.snow_mound(c, DRIFT_X, dy0 + 2, 250, 130)
        if ub >= 1 and not out:
            pop = lambda f: ease(clamp((t - T("sl_crash", f)) / 0.25))
            kat(c, tl, t, "luna", DRIFT_X - 140, dy0 - 80 - 30 * pop(0.5), 0.95, 1, "swim", eyes="happy",
                mouth=laughing(t) * 0.8)
            kat(c, tl, t, "whiskers", DRIFT_X - 20, dy0 - 105 - 30 * pop(0.6), 0.95, 1, "swim", eyes="happy",
                mouth=tl.mouth("whiskers", t) or laughing(t, 1.2) * 0.8)
            P.margot(c, DRIFT_X + 70, dy0 - 110 - 30 * pop(0.75), 1.1, -1, t, eyes="happy")
        poof(c, DRIFT_X - 100, dy0 - 80, dt - (T("sl_crash", 0.4) - T("sl_crash", 0.12)))
        poof(c, DRIFT_X, dy0 - 100, dt - (T("sl_crash", 0.42) - T("sl_crash", 0.12)))
        if out:
            # goodbyes: Margot waves from the top of the drift, Bruno beside it; the cats head for the village
            P.bruno(c, DRIFT_X + 330, dy0 + 2, 0.7, -1, t, sit=True, mouth=tl.mouth("bruno", t), eyes="happy")
            P.margot(c, DRIFT_X + 10, dy0 - 124, 1.2, -1 if t < T("sl_end") else 1, t, mouth=tl.mouth("margot", t),
                     wave=1.0, eyes="happy")
            wk = [(T("sl_bye") - 0.3, DRIFT_X - 200), (T("sl_end", 0.1), DRIFT_X - 200), (s1 + 0.5, DRIFT_X + 800)]
            lk = [(T("sl_bye") - 0.3, DRIFT_X - 330), (T("sl_end", 0.05), DRIFT_X - 330), (s1 + 0.5, DRIFT_X + 700)]
            actor(c, tl, t, "luna", lk, dy0 + 4, 0.9, face=1, eyes="happy")
            actor(c, tl, t, "whiskers", wk, dy0 + 4, 0.9, face=1, scarf=True,
                  eyes="happy" if not tl.talking("whiskers", t) else "open")
    for x, s, front in pines:
        if front and camx - 100 < x < camx + W + 100:
            P.pine(c, x + 60, sled_y(x + 60) + 170, s * 1.3)
    c.pop()
    if T("sl_ride", 0.1) < t < T("sl_crash", 0.1):
        rng = np.random.default_rng(int(t * 8))
        for k in range(6):
            y = rng.uniform(80, 640)
            x = rng.uniform(0, W)
            c.line([(x, y), (x + 120, y + 120 * SLOPE)], (255, 255, 255), 2)
    return finish(c, tl, t)


# ==================================================================== home

def home_bg():
    def make():
        wall = (236, 214, 178)
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, H, mix(wall, (255, 255, 255), 0.25), ol=None)
        win = Canvas(D.gradient(1000 * SS, 480 * SS, [(0, (16, 22, 60)), (0.7, (50, 56, 112)), (1, (70, 70, 130))]),
                     size=(1000, 480))
        D.stars(win, 14, 50, 1000, 180)
        D.moon(win, 820, 90, 32, sky=(30, 36, 80))
        for x, w, h in ((40, 220, 180), (300, 180, 230), (520, 260, 160), (800, 200, 210)):
            win.rect(x, 480 - h, x + w, 480, (60, 56, 90), ol=None)
            win.poly([(x - 14, 480 - h), (x + w / 2, 480 - h - 60), (x + w + 14, 480 - h)], P.SNOW, ol=None)
            for wx in range(int(x) + 26, int(x + w) - 30, 60):
                win.rect(wx, 480 - h + 40, wx + 26, 480 - h + 74, (255, 214, 120), ol=None)
        win.rect(0, 460, 1000, 480, P.SNOW, ol=None)
        c.img.paste(win.img, (140 * SS, 60 * SS))
        for x0, x1 in ((50, 170), (1110, 1230)):
            c.rect(x0, 0, x1, 640, (70, 110, 170), r=10)
            for xx in range(int(x0) + 20, int(x1), 30):
                c.line([(xx, 10), (xx, 630)], (56, 92, 150), 3, cap=False)
        c.rect(30, 0, 1250, 16, (150, 100, 60))
        c.rect(0, 560, W, H, mix(wall, (0, 0, 0), 0.06), ol=None)
        return c.img
    return cached("home", make)


def home_frame(c):
    c.rect(130, 52, 1150, 544, None, w=10)
    c.line([(640, 60), (640, 540)], (240, 236, 230), 10, cap=False)
    c.line([(140, 300), (1140, 300)], (240, 236, 230), 10, cap=False)
    c.rect(130, 52, 1150, 544, None, ol=(240, 236, 230), w=6)
    c.rect(100, 540, 1180, 572, (250, 246, 236), r=5)
    # postcard on the sill and a snow globe
    card = cached("home_card", lambda: P.postcard_img(420, 280).resize((168 * SS, 112 * SS)))
    c.rect(946, 422, 1124, 543, (255, 252, 240), w=2.5)
    c.img.paste(card, (951 * SS, 427 * SS))
    c.rect(250, 520, 330, 543, (130, 86, 54), w=2.5, r=4)
    c.circle(290, 484, 40, (200, 226, 250), w=2.5)
    P.mont_blanc(c, 290, 510, 0.07, ol=None)
    c.circle(276, 468, 9, (240, 248, 255), ol=None)


def home(tl, t):
    T = tl.t
    c = Canvas(home_bg().copy())
    P.snowfall(c, t, n=90, seed=15, speed=45, drift=15, size=(1.5, 4), region=(140, 60, 1140, 540))
    home_frame(c)
    curl = t >= T("h_curl")
    Y = 546
    c.tint = ((40, 40, 100), 0.1)
    if not curl:
        look_out = T("h_snow") <= t < T("h_socks", 0.2)
        kat(c, tl, t, "luna", 450, Y, 1.25, 1, "sit", eyes="happy" if T("h_socks", 0.4) <= t else "open",
            mouth=laughing(t) * 0.6 if T("h_socks", 0.9) <= t else tl.mouth("luna", t))
        D.mouse(c, 625, Y + 2, 1.9, 1, t, mouth=tl.mouth("pip", t), proud=T("h_pip") <= t < T("h_pip", 1),
                eyes="happy" if T("h_socks", 0.4) <= t else "open")
        kat(c, tl, t, "whiskers", 830, Y, 1.25, -1, "sit", look=(-0.3, -1) if look_out else (1, 0.3),
            eyes="happy" if T("h_together", 0.6) <= t < T("h_snow") else "open")
    else:
        kat(c, tl, t, "luna", 500, Y + 2, 1.15, 1, "sleep", mouth=0)
        D.mouse(c, 655, Y + 2, 1.5, -1, t, eyes="closed")
        kat(c, tl, t, "whiskers", 800, Y + 2, 1.15, -1, "sleep", mouth=0)
        D.zzz(c, 820, 430, t)
    c.tint = None
    k = ease(tl.prog("h_end", t, 0.15, 0.45))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 44 * k, mix((236, 214, 178), (255, 250, 236), k), stroke=4 * k,
               stroke_fill=(70, 50, 60))
    return finish(c, tl, t)


SCENE_FUNCS = {"title": title, "postcard": postcard, "train": train, "cablecar": cablecar, "snow": snow,
               "storm": storm, "chalet": chalet, "summit": summit, "sled": sled, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["ch_zzz", "su_above", "h_curl"]
