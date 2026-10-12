"""Scenes of "Whiskers and the Missing Sun". One function per scene: (tl, t) -> Canvas.

Animation is keyed to script event ids (tl.t("id", frac)) as in Film 1.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.santorini import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def view(bg, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    return Canvas(bg.crop((x, y, x + W * SS, y + H * SS)))


def paste_layer(c, layer, camx=0.0, camy=0.0):
    x, y = int(round(camx * SS)), int(round(camy * SS))
    part = layer.crop((x, y, x + W * SS, y + H * SS))
    c.img.paste(part, (0, 0), part)


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


def arc_y(u, h):
    return -4 * h * u * (1 - u)


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="sit", walk=0.0, bundle=False, piece=False, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if bundle:
        if pose == "sit":
            P.bags_bundle(c, x - 22 * s * face, y - 60 * s, s * 0.9)
        else:
            P.bags_bundle(c, x - 6 * s * face, y - 82 * s, s * 0.95)
    if piece:
        bx = x - (44 if pose != "sit" else 30) * s * face
        P.piece(c, bx, y - 40 * s, s * 0.7)


def pip(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("pip", t))
    D.mouse(c, x, y, s, face, t, mouth=mouth, **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", camx=0.0, **kw):
    x = smooth(t, keys) - camx
    v = speed(t, keys)
    moving = abs(v) > 20 * s
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        pip(c, tl, t, x, y, s, face, walk=(x + camx) / 6 if moving else 0.0, hop=hop, **kw)
    else:
        if moving and pose in ("stand", "sit"):
            pose = "walk"
        kat(c, tl, t, who, x, y, s, face, pose, walk=(x + camx) / (12 * s) if moving else 0.0, **kw)
    return x


def stelios(c, tl, t, x, y, s=1.0, face=1, **kw):
    beak = kw.pop("beak", tl.mouth("stelios", t))
    P.pelican(c, x, y, s, face, t, beak=beak, **kw)


def faso(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("fasolaki", t))
    P.donkey(c, x, y, s, face, t, mouth=mouth, **kw)


def laughing(t, k=1.0):
    return 0.5 + 0.4 * math.sin(t * 15 * k)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def splash_fx(c, x, y, dt, s=1.0):
    if dt < 0 or dt > 1.2:
        return
    u = dt / 1.2
    for k in range(9):
        a = math.pi * (0.1 + 0.8 * k / 8)
        r = 70 * s * ease(min(1, u * 1.6))
        px, py = x + math.cos(a) * r, y - math.sin(a) * r * 1.4 + 160 * s * u * u
        c.circle(px, py, 7 * s * (1 - u) + 1, (210, 236, 255), w=1.5)
    c.ellipse(x, y, 80 * s * (0.4 + u), 14 * s * (0.4 + u), (200, 230, 255), ol=(255, 255, 255), w=2)


def rider_cat(tl, t, who, **kw):
    def draw(c, x, y):
        D.cat(c, x, y, PAL[who], 1.05, 1, "sit", t=t, mouth=kw.get("mouth", tl.mouth(who, t)),
              seed=SEED[who], eyes=kw.get("eyes", "open"), look=kw.get("look", (0, 0)), head_dy=kw.get("head_dy", 0))
    return draw


def riders(tl, t, who=("luna", "whiskers", "pip"), eyes=None):
    out = []
    for w in who:
        if w == "pip":
            out.append(("pip", None))
        else:
            pal = dict(PAL[w])
            pal["_mouth"] = tl.mouth(w, t)
            pal["_eyes"] = (eyes or {}).get(w, "open")
            out.append((w, pal))
    return out


# =================================================================== title

def caldera_layers(light="gold"):
    """Wide view of the caldera from a cliff-top terrace in Oia (used by title)."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (64, 110, 190)), (0.3, (150, 160, 210)), (0.5, (255, 196, 160)),
                                               (0.56, (255, 220, 170)), (0.57, (40, 96, 170)), (1, (16, 56, 128))]))
        P.sun(c, 900, 330, 46, (255, 200, 160), core=(255, 240, 180), halo=(255, 214, 160))
        # far rim of the caldera on the horizon
        c.poly([(560, 412), (640, 396), (760, 392), (880, 402), (1000, 398), (1140, 406), (1280, 400), (1280, 412)],
               (150, 110, 130), ol=(110, 80, 100), w=2)
        P.volcano_island(c, 980, 440, 300, 34, col=(110, 80, 96), top=(130, 96, 110), ol=(80, 60, 76))
        return c.img

    def make_fg():
        fg = P.rgba_canvas(W, H)
        def top(x):
            return 330 + 0.0006 * (x - 0) ** 2 if x < 600 else 546
        P.cliff_band(fg, -10, 560, lambda x: 300 + x * 0.42, 760, seed=3)
        P.village_top(fg, -20, 520, lambda x: 300 + x * 0.42, seed=5, density=1.2, domes=2, scale=1.25,
                      mills=((90, 0.7),))
        # terrace in front
        fg.rect(-10, 640, W + 10, H + 10, (238, 230, 214), w=3)
        for k in range(14):
            fg.line([(k * 100, 650), (k * 100 - 60, H)], (214, 204, 186), 2, cap=False)
        P.stone_wall(fg, 380, 1060, 646, 30)
        P.dome_church(fg, 1170, 640, 1.05)
        P.bougainvillea(fg, 1080, 520, 1.6, np.random.default_rng(4))
        return fg.img
    return cached(("cal", light), make), cached(("calfg", light), make_fg)


def title(tl, t):
    bg, fg = caldera_layers()
    c = Canvas(bg.copy())
    P.sparkle_path(c, t, 900, 420, 600, 30, 140, n=26, col=(255, 226, 170))
    P.sea_glints(c, t, 560, 1280, 430, 640, n=30, seed=2, col=(110, 160, 230))
    P.caique(c, 700 + 8 * t, 520, 0.45, bob=2 * math.sin(t * 1.5), sail=True)
    for k in range(3):
        P.gull(c, (200 + 70 * t + 260 * k) % 1500 - 100, 170 + 30 * k + 8 * math.sin(t + k), t, 0.8, seed=k)
    c.img.paste(fg, (0, 0), fg)
    c.tint = ((255, 170, 120), 0.12)
    kat(c, tl, t, "whiskers", 640, 616, 0.85, 1, "sit", look=(1, -0.5), mouth=0)
    kat(c, tl, t, "luna", 730, 616, 0.8, 1, "sit", look=(1, -0.5), mouth=0, tail=math.sin(t * 1.5))
    pip(c, tl, t, 800, 616, 0.9, 1, mouth=0)
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.7))
    c.text(W / 2, 80 - 30 * (1 - k), "Whiskers and the", 44, mix((60, 90, 160), (255, 250, 240), k),
           stroke=3 * k, stroke_fill=(30, 60, 130))
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 156, "MISSING SUN", 28 + 56 * k2, mix((60, 90, 160), (255, 236, 150), k2), stroke=5 * k2,
           stroke_fill=(30, 60, 130))
    return finish(c, tl, t)


# ================================================================== puzzle

WIN = (760, 110, 1080, 374)


def room_bg(mode):
    """mode: 'rain' (grey evening) or 'sun' (bright morning)."""
    def make():
        if mode == "rain":
            wall, floor = (176, 182, 204), (150, 110, 88)
            sky = [(0, (90, 100, 124)), (1, (150, 156, 170))]
        else:
            wall, floor = (250, 230, 192), (198, 138, 90)
            sky = [(0, (110, 180, 245)), (1, (205, 235, 255))]
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, 520, mix(wall, (255, 255, 255), 0.22), ol=None)
        c.rect(0, 520, W, H, floor, ol=None)
        for y in range(540, H, 36):
            c.line([(0, y), (W, y)], mix(floor, (0, 0, 0), 0.12), 2, cap=False)
        c.rect(0, 506, W, 524, mix(wall, (0, 0, 0), 0.25), ol=None)
        win = Canvas(D.gradient(320 * SS, 264 * SS, sky), size=(320, 264))
        if mode == "rain":
            win.poly([(0, 200), (120, 176), (320, 194), (320, 264), (0, 264)], (110, 116, 120), ol=None)
            D.tree(win, 90, 240, 0.9, leaf=(90, 120, 100), trunk=(90, 80, 70))
            for x, y, s in ((60, 50, 1.1), (220, 80, 1.3), (300, 30, 1.0)):
                D.cloud(win, x, y, s, col=(126, 132, 150))
        else:
            win.poly([(0, 200), (120, 176), (320, 194), (320, 264), (0, 264)], (140, 190, 110), ol=None)
            D.tree(win, 90, 240, 0.9)
            D.cloud(win, 230, 60, 0.7)
        c.img.paste(win.img, (WIN[0] * SS, WIN[1] * SS))
        # a little mouse hole for Pip
        c.ellipse(120, 520, 26, 30, (60, 44, 50), w=2.5)
        c.rect(90, 520, 150, 540, floor, ol=None)
        # bookshelf with travel books, a globe
        c.rect(180, 300, 420, 312, (150, 100, 70), r=3)
        for k, col in enumerate(((200, 80, 70), (70, 120, 190), (230, 190, 80), (90, 160, 110), (170, 110, 190))):
            c.rect(196 + 22 * k, 240 - 8 * (k % 2), 214 + 22 * k, 300, col, w=2, r=2)
        c.circle(360, 266, 30, (90, 160, 220), w=2.5)
        c.poly([(344, 252), (366, 246), (372, 270), (350, 280)], (110, 180, 110), ol=None)
        c.rect(352, 296, 368, 300, (150, 100, 70), ol=None)
        # sofa corner on the left
        c.rect(-20, 400, 70, 560, (110, 140, 190) if mode == "sun" else (90, 110, 150), r=16)
        return c.img
    return cached(("room", mode), make)


def puzzle_small(sun):
    def make():
        art = P.puzzle_art(560, 320, sun=sun, hole=not sun)
        return art.resize((480 * SS, 150 * SS), Image.LANCZOS)
    return cached(("pz_small", sun), make)


def puzzle_big(sun):
    def make():
        return P.puzzle_art(960, 548, sun=sun, hole=not sun)
    return cached(("pz_big", sun), make)


def room_puzzle(c, sun, x=290, y=548):
    c.rect(x - 6, y - 6, x + 486, y + 156, (90, 64, 50), ol=None, r=4)
    c.img.paste(puzzle_small(sun), (x * SS, y * SS))
    c.rect(x, y, x + 480, y + 150, None, w=2)


def window_parts(c, t, rain=True, open_k=0.0, inside=None):
    """Window: rain streaks, things outside (inside: callable), frame. open_k swings the panes in."""
    x0, y0, x1, y1 = WIN
    if inside:
        inside(c)
    if rain:
        rng = np.random.default_rng(5)
        for k in range(46):
            rx = rng.uniform(x0 + 6, x1 - 6)
            ph = rng.uniform(0, 1)
            yy = y0 + ((t * 1.6 + ph) % 1.0) * (y1 - y0 - 20)
            c.line([(rx, yy), (rx - 4, yy + 18)], (200, 210, 230), 1.5, cap=False)
    fc = (240, 240, 240) if not rain else (200, 204, 214)
    c.rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4, None, w=8)
    if open_k < 0.05:
        c.line([(920, y0), (920, y1)], fc, 6, cap=False)
        c.line([(x0, 240), (x1, 240)], fc, 6, cap=False)
        if rain:
            for k in range(8):
                dx = 790 + 36 * k
                dy = 140 + (k * 53) % 200
                c.ellipse(dx, dy, 3, 4, (210, 220, 240), ol=(150, 160, 190), w=1)
    else:
        wd = 160 * (1 - 0.8 * open_k)
        for side in (-1, 1):
            hx = x0 if side < 0 else x1
            ex = hx - side * wd
            c.poly([(hx, y0), (ex, y0 - 20 * open_k), (ex, y1 + 20 * open_k), (hx, y1)],
                   (210, 225, 240), ol=fc, w=5)
    c.rect(740, 370, 1100, 392, (255, 250, 240) if not rain else (200, 200, 214), r=4)


def puzzle_close(tl, t, sun=False, piece_k=None):
    c = Canvas(bg=(120, 86, 64))
    for y in range(0, H, 48):
        c.line([(0, y), (W, y)], (104, 74, 56), 3, cap=False)
    x0, y0 = 160, 60
    c.rect(x0 - 8, y0 - 8, x0 + 968, y0 + 556, (80, 56, 44), ol=None, r=6)
    c.img.paste(puzzle_big(sun), (x0 * SS, y0 * SS))
    c.rect(x0, y0, x0 + 960, y0 + 548, None, w=3)
    if piece_k is not None:
        # the sun piece flies in and clicks into place
        tx, ty = x0 + 960 * (4.5 / 8 + 0.0625), y0 + 548 * 1.5 / 5
        k = ease(piece_k)
        px, py = lerp(640, tx, k), lerp(820, ty, k) + arc_y(k, 120)
        if piece_k < 1:
            P.piece(c, px, py, 2.6)
    return c


def puzzle(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["puzzle"]
    if T("pz_look") <= t < T("pz_sit"):
        c = puzzle_close(tl, t)
        # Luna's paw points at the hole
        k = ease(tl.prog("pz_look", t, 0.2, 0.7))
        px, py = lerp(520, 640, k), lerp(820, 380, k) + 6 * math.sin(t * 3)
        c.stroke([(px - 30, 760), (px, py + 30)], D.LUNA["body"], 46)
        c.ellipse(px, py + 14, 30, 24, D.LUNA["body"])
        for dx in (-14, 0, 14):
            c.circle(px + dx, py - 2, 7, D.LUNA["belly"], w=1.5)
        return finish(c, tl, t, 0.6)

    c = Canvas(room_bg("rain").copy())
    # pelican arrives
    land = tl.prog("pz_land", t, 0.0, 0.7)
    opened = ease(tl.prog("pz_land", t, 0.6, 0.95))
    gone = tl.prog("pz_end", t, 0.0, 1.0)
    have_riders = t >= T("pz_jump", 0.75)
    jump_whis = (T("pz_jump", 0.3), T("pz_jump", 0.7))
    jump_luna = (T("pz_jump", 0.0), T("pz_jump", 0.4))
    jump_pip = (T("pz_pip", 0.5), T("pz_pip", 1.0) + 0.2)
    rid = []
    if t >= jump_luna[1]:
        rid.append("luna")
    if t >= jump_whis[1]:
        rid.append("whiskers")
    if t >= jump_pip[1]:
        rid.append("pip")

    def inside(cc):
        if t < T("pz_land"):
            return
        if gone > 0:
            cc.push(0, 0)
            P.pelican_fly(cc, lerp(1000, 1500, ease(gone)), lerp(250, -120, ease(gone)), 0.8, 1, t,
                          riders=riders(tl, t, rid), flap_speed=9)
            cc.pop()
        elif land < 1:
            u = ease(land)
            P.pelican_fly(cc, lerp(1400, 1000, u), lerp(-80, 230, u), 0.8, -1, t, flap_speed=9)
        else:
            stelios(cc, tl, t, 1000, 372, 0.82, -1, pouch=0.6 if rid else 0.0, riders=riders(tl, t, rid),
                    eyes="happy" if T("pz_hop") <= t < T("pz_hop", 1) else "open")

    window_parts(c, t, rain=True, open_k=opened, inside=None)
    # pelican is drawn over the opened window (he leans in) -- or behind closed glass
    inside(c)
    if t < T("pz_luna"):
        build = 1.0
    room_puzzle(c, False)
    # Pip at his mouse hole
    pip_x = smooth(t, [(s0, 120), (T("pz_pip", 0.0), 120), (T("pz_pip", 0.5), 700)], 0.2)
    if t < jump_pip[0]:
        actor(c, tl, t, "pip", [(s0, 120), (T("pz_pip", 0.0), 140), (T("pz_pip", 0.5), 700)], 540, 1.0, 1,
              eyes="happy" if t < T("pz_narr", 1) else "open")
    elif t < jump_pip[1]:
        u = (t - jump_pip[0]) / (jump_pip[1] - jump_pip[0])
        pip(c, tl, t, lerp(700, 905, u), lerp(540, 268, u) + arc_y(u, 120), 1.0, 1)
    # cats
    lk = (1, -0.6) if t >= T("pz_land", 0.4) else (0, 0.4)
    if t < jump_luna[0]:
        kat(c, tl, t, "luna", 230, 640, 0.9, 1, "sit", look=lk,
            eyes="happy" if T("pz_luna") <= t < T("pz_look") else "open")
    elif t < jump_luna[1]:
        u = (t - jump_luna[0]) / (jump_luna[1] - jump_luna[0])
        kat(c, tl, t, "luna", lerp(230, 900, u), lerp(640, 290, u) + arc_y(u, 160), 0.8, 1, "leap")
    if t < jump_whis[0]:
        face = -1 if t < T("pz_land", 0.4) else 1
        kat(c, tl, t, "whiskers", 830, 650, 0.95, face, "sit", look=lk,
            eyes="happy" if T("pz_hop") <= t < T("pz_hop", 1) else "open",
            head_dy=4 * math.sin(t * 2) if t < T("pz_luna") else 0)
    elif t < jump_whis[1]:
        u = (t - jump_whis[0]) / (jump_whis[1] - jump_whis[0])
        kat(c, tl, t, "whiskers", lerp(830, 930, u), lerp(650, 290, u) + arc_y(u, 110), 0.8, 1, "leap")
    if t < T("pz_land"):
        pass
    return finish(c, tl, t)


# ================================================================ flight

def flight_sky(kind):
    def make():
        if kind == "night":
            stops = [(0, (14, 20, 54)), (0.55, (40, 50, 110)), (0.7, (70, 70, 130)), (0.71, (20, 34, 80)),
                     (1, (10, 20, 54))]
        else:
            stops = [(0, (90, 140, 220)), (0.4, (250, 180, 170)), (0.7, (255, 214, 160)), (0.71, (60, 110, 180)),
                     (1, (30, 70, 140))]
        c = Canvas(D.gradient(W * SS, H * SS, stops))
        if kind == "night":
            D.stars(c, 21, 140, W, 480)
            D.moon(c, 1060, 140, 40, sky=(30, 38, 90))
        else:
            P.sun(c, 1000, 500, 54, (255, 214, 160), core=(255, 240, 190))
            # small islands on the horizon
            for x, w_, h_ in ((180, 160, 22), (420, 90, 14), (1200, 140, 18)):
                c.poly([(x - w_ / 2, 511), (x - w_ / 4, 511 - h_), (x + w_ / 5, 511 - h_ * 0.8), (x + w_ / 2, 511)],
                       (120, 100, 130), ol=None)
        return c.img
    return cached(("fsky", kind), make)


def caldera_aerial():
    """The whole caldera seen from the air, in morning light."""
    def make():
        c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 170, 236)), (0.22, (230, 214, 220)), (0.27, (250, 226, 200)),
                                               (0.28, (60, 120, 196)), (1, (20, 66, 150))]))
        P.sun(c, 1110, 120, 40, (210, 200, 226), core=(255, 246, 210), halo=(255, 230, 200))
        hz = 200
        # Therasia on the far left/back
        P.cliff_band(c, -20, 420, lambda x: 232 + 0.0004 * (x - 200) ** 2 - 12, 290, seed=11)
        P.village_top(c, 60, 300, lambda x: 232 + 0.0004 * (x - 200) ** 2 - 12, seed=12, density=0.6, domes=1,
                      scale=0.32)
        # the far, northern rim (Oia)
        P.cliff_band(c, 560, 1000, lambda x: 216 - 6 * math.sin((x - 560) / 440 * math.pi), 250, seed=13)
        P.village_top(c, 600, 980, lambda x: 216 - 6 * math.sin((x - 560) / 440 * math.pi), seed=14, density=0.8,
                      domes=2, scale=0.3, mills=((620, 0.16), (960, 0.16)))
        # main island curving round on the right, toward the viewer
        def top(x):
            return 230 + ((x - 960) / 320) ** 2 * 300 if x > 960 else 230
        P.cliff_band(c, 960, 1300, top, 760, seed=15)
        P.village_top(c, 980, 1290, top, seed=16, density=0.8, domes=3, scale=0.8)
        # sea glints are drawn live; volcano in the middle
        P.volcano_island(c, 600, 410, 460, 70, smoke=0.0)
        P.volcano_island(c, 290, 352, 180, 30, col=(84, 66, 70), top=(104, 80, 80))
        # the old port at the foot of the right cliff
        c.rect(1060, 560, 1300, 600, (220, 206, 186), w=2)
        for x in (1100, 1180):
            P.caique(c, x, 620, 0.28)
        return c.img
    return cached("aerial", make)


def flight(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["flight"]
    if t >= T("fl_caldera"):
        c = Canvas(caldera_aerial().copy())
        P.sea_glints(c, t, 0, 1000, 240, 700, n=60, seed=8, col=(120, 170, 236))
        for k in range(3):
            bx = (300 + 30 * t + 330 * k) % 900 + 50
            c.line([(bx - 30, 500 + 50 * k), (bx + 6, 500 + 50 * k)], (230, 240, 255), 2)
        # pelican glides across and comes down into the harbour
        u = tl.prog("fl_caldera", t, 0.0, 1.0)
        land = tl.prog("fl_land", t, 0.0, 0.75)
        if land <= 0:
            x = smooth(t, [(T("fl_caldera"), -100), (T("fl_sugar", 1), 820)], 0.4)
            y = 330 + 30 * math.sin(t * 0.8)
            P.pelican_fly(c, x, y, 0.75, 1, t, riders=riders(tl, t), glide=(t % 3) < 1.6, flap_speed=6)
        else:
            k = ease(land)
            x, y = lerp(820, 1150, k), lerp(330, 580, k)
            P.pelican_fly(c, x, y, lerp(0.75, 0.45, k), 1, t, riders=riders(tl, t), glide=True)
        splash_fx(c, 1150, 590, t - T("fl_land", 0.75), 0.6)
        for k in range(4):
            P.gull(c, (900 - 40 * t + 280 * k) % 1400 - 60, 140 + 40 * (k % 2), t, 0.6, seed=k)
        return finish(c, tl, t)

    dawn = ease(tl.prog("fl_dawn", t, 0.0, 1.0))
    a, b = flight_sky("night"), flight_sky("dawn")
    sky = a if dawn <= 0 else b if dawn >= 1 else Image.blend(a, b, dawn)
    c = Canvas(sky.copy())
    # scrolling sea waves and clouds (we fly left -> right, so the world slides left)
    sea_col = mix((60, 90, 150), (130, 180, 236), dawn)
    for k in range(40):
        rng_x = (k * 211) % 1400
        y = 520 + (k * 37) % 190
        f = (y - 510) / 210
        x = (rng_x - (t * 260 * (0.4 + f)) ) % 1400 - 60
        c.line([(x, y), (x + 20 + 40 * f, y)], sea_col, 2 + 2 * f, cap=False)
    if dawn < 0.5:
        for k in range(6):
            mx = 1060 + 0 * k
        rng = np.random.default_rng(3)
        for k in range(10):
            yy = 528 + k * 16
            w_ = 20 + 4 * k
            c.line([(1060 - w_, yy), (1060 + w_, yy)], (190, 196, 220), 2, cap=False)
    for k in range(6):
        cx = (k * 330 - t * 140 * (0.6 + 0.15 * (k % 3))) % 1700 - 200
        cy = 120 + 70 * (k % 3)
        D.cloud(c, cx, cy, 0.9 + 0.3 * (k % 2), col=mix((90, 96, 150), (255, 236, 236), dawn))
    bob = 14 * math.sin(t * 2.2)
    eyes = {}
    if T("fl_smell") <= t < T("fl_dawn"):
        eyes = {"whiskers": "happy"}
    P.pelican_fly(c, 560, 330 + bob, 1.55, 1, t, riders=riders(tl, t, eyes=eyes), flap_speed=5)
    for k in range(2):
        cx = (k * 800 + 400 - t * 420) % 1900 - 300
        D.cloud(c, cx, 640 + 40 * k, 1.4, col=mix((110, 116, 170), (255, 246, 240), dawn))
    if dawn < 1:
        c.tint = None
    return finish(c, tl, t)


# ================================================================ harbour

HW = 2300
QUAY = 668


def harbour_top(x):
    return 160 + 26 * math.sin(x / 260) + 14 * math.sin(x / 97)


def harbour_bg():
    def make():
        c = Canvas(D.gradient(HW * SS, H * SS, [(0, (110, 170, 240)), (0.3, (196, 226, 252)), (1, (196, 226, 252))]),
                   size=(HW, H))
        D.cloud(c, 300, 60, 0.8)
        D.cloud(c, 1300, 50, 0.7)
        P.cliff_band(c, -10, HW + 10, harbour_top, 480, seed=21)
        # the zig-zag steps scratched across the cliff face, with tiny donkeys
        zz = [(2280, 470), (1560, 410), (2240, 340), (1600, 280), (2200, 220)]
        for a, b in zip(zz, zz[1:]):
            c.line([a, b], (238, 220, 190), 9, cap=False)
            c.line([(a[0], a[1] + 6), (b[0], b[1] + 6)], (250, 250, 246), 4, cap=False)
        for k, (x, y) in enumerate(((1900, 438), (1800, 305), (2050, 246))):
            c.ellipse(x, y - 6, 9, 5, (120, 104, 100), ol=None)
            c.circle(x + 9 * (-1) ** k, y - 11, 3.5, (120, 104, 100), ol=None)
        P.village_top(c, -20, HW + 20, harbour_top, seed=22, density=1.0, domes=5, scale=0.8)
        # sea strip behind the quay
        c.rect(-10, 470, HW + 10, 610, P.SEA, ol=None)
        c.rect(-10, 470, HW + 10, 478, (60, 130, 200), ol=None)
        for x in (180, 520, 860):
            pass
        # taverna building against the cliff
        c.rect(1240, 330, 1790, 612, P.WHITE, w=3, r=3)
        c.rect(1700, 336, 1786, 608, P.WHITE_SH, ol=None)
        c.rect(1232, 318, 1798, 336, P.WHITE, w=3, r=3)
        c.rect(1380, 346, 1640, 384, (40, 90, 170), w=2.5, r=6)
        c.text(1510, 365, "TAVERNA  STELIOS", 22, (255, 255, 255))
        for x in (1290, 1660):
            c.rect(x, 404, x + 48, 452, (60, 130, 200), w=2.5, r=3)
            c.line([(x + 24, 404), (x + 24, 452)], OUT, 2, cap=False)
        c.rect(1490, 470, 1540, 612, (40, 90, 170), w=2.5, r=24)
        # awning
        for k in range(14):
            col = (40, 90, 170) if k % 2 == 0 else (250, 250, 250)
            c.poly([(1230 + 40 * k, 470), (1270 + 40 * k, 470), (1274 + 40 * k, 500), (1234 + 40 * k, 500)], col, ol=None)
        c.rect(1230, 466, 1790, 476, (40, 90, 170), w=2)
        for k in range(14):
            c.arc(1250 + 40 * k, 500, 20, 8, 0, 180, OUT, 2)
        for x in (1240, 1780):
            c.line([(x, 500), (x, 640)], (110, 80, 60), 5)
        # right: the gate to the steps
        c.rect(2060, 360, 2300, 612, P.WHITE, w=3)
        c.rect(2120, 450, 2200, 612, (90, 70, 66), w=3, r=40)
        c.rect(2100, 396, 2230, 430, (40, 90, 170), w=2, r=4)
        c.text(2165, 413, "FIRA  588", 18, (255, 255, 255))
        c.poly([(2120, 600), (2200, 600), (2196, 612), (2124, 612)], (236, 220, 196), ol=None)
        # the quay
        c.rect(-10, 600, HW + 10, H + 10, (232, 220, 196), w=3)
        c.rect(-10, 600, 1240, 614, (196, 182, 160), ol=None)
        rng = np.random.default_rng(4)
        for k in range(70):
            x = rng.uniform(0, HW)
            y = rng.uniform(620, 715)
            c.ellipse(x, y, rng.uniform(16, 34), rng.uniform(5, 9), (218, 204, 180), ol=None)
        for x in (60, 420, 760, 1100):
            c.rect(x - 10, 594, x + 10, 616, (90, 90, 96), w=2, r=4)   # bollards
        return c.img
    return cached("harbour", make)


def octo_line(c, tl, t, camx, pull=None):
    """The drying line between two poles, with octopus hanging. pull=(x, y) drags the big one."""
    xa, xb, y = 1800 - camx, 2080 - camx, 430
    for x in (xa, xb):
        c.rect(x - 6, y - 10, x + 6, QUAY, (120, 86, 60), w=2)
    big_x = 1940 - camx
    if pull is None:
        c.line([(xa, y), (xb, y)], (240, 230, 210), 2.5, cap=False)
        for k, ox in enumerate((1850, 1890, 1990, 2030)):
            P.octopus(c, ox - camx, y - 6, 0.6, t + k, sway=0.2 * math.sin(t + k))
        P.octopus(c, big_x, y - 8, 0.95, t)
    else:
        px, py = pull
        c.line([(xa, y), (big_x + (px - big_x) * 0.25, y + (py - y) * 0.3), (xb, y)], (240, 230, 210), 2.5)
        for k, ox in enumerate((1850, 1890, 1990, 2030)):
            P.octopus(c, ox - camx, y - 6 + 10, 0.6, t + k, sway=0.6 * math.sin(t * 3 + k))


def harbour(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["harbour"]
    camx = smooth(t, [(s0, 200), (T("hb_welcome", 0.9), 700), (T("hb_mine", 0.2), 700), (T("hb_mine", 1.0), 1000),
                      (T("hb_pull", 0.5), 1000), (T("hb_pull", 0.85), 640), (T("hb_goat", 1.0), 640),
                      (s1, 1000)], 0.5)
    c = view(harbour_bg(), camx, 0)
    P.sea_glints(c, t, -camx, 1240 - camx, 484, 596, n=40, seed=5, col=(110, 170, 236))
    for k, x in enumerate((180, 520, 860)):
        P.caique(c, x - camx, 560, 0.7, hull=[(40, 110, 190), (200, 70, 60), (60, 150, 120)][k],
                 bob=3 * math.sin(t * 1.4 + k), sail=k == 1)
    for k in range(3):
        P.gull(c, (300 + 50 * t + 400 * k) % 1500 - 100, 90 + 30 * k, t, 0.7, seed=k)
    W_ = lambda x: x - camx  # noqa: E731
    pull = None
    pu = tl.prog("hb_pull", t)
    launched = t >= T("hb_pull", 0.5)
    if T("hb_pull") <= t < T("hb_pull", 0.5):
        k = ease(tl.prog("hb_pull", t, 0.1, 0.48))
        pull = (W_(lerp(1940, 1760, k)), lerp(560, 600, k))
    octo_line(c, tl, t, camx, pull if pull else (None if not launched else None))
    if launched and t < T("hb_pull", 0.52):
        pass
    P.grill(c, W_(1690), 664, t)
    # table + food
    P.chair(c, W_(1340), QUAY, 1)
    P.table(c, W_(1460), QUAY, 170)
    eaten = tl.prog("hb_munch", t)
    P.plate(c, W_(1420), QUAY - 80, "fritters", t, n=max(0, 4 - int(eaten * 4)) if t >= T("hb_munch") else 4)
    P.plate(c, W_(1500), QUAY - 80, "octopus", t)
    # Pip on the table
    pip(c, tl, t, W_(1450), QUAY - 76, 0.9, 1 if t < T("hb_mine") else 1,
        eyes="happy" if T("hb_wash") <= t < T("hb_oia") else "open")
    # Stelios
    st_x = smooth(t, [(s0, 900), (T("hb_welcome"), 1180), (s1 - 2, 1180), (s1, 1500)], 0.4)
    st_face = 1 if t < T("hb_pull", 0.5) else -1
    stelios(c, tl, t, W_(st_x), QUAY, 0.85, st_face, walk=st_x / 30 if s0 + 0.2 < t < T("hb_welcome") else 0,
            wing_up=0.8 if T("hb_steps") <= t < T("hb_steps", 1) else 0.0,
            eyes="happy" if T("hb_wash") <= t < T("hb_oia") else "open")
    # Luna
    lu_keys = [(s0, 760), (T("hb_welcome", 0.6), 1360), (T("hb_oia"), 1360), (T("hb_oia", 0.4), 1270),
               (s1 - 1.5, 1270), (s1, 1700)]
    lx = smooth(t, lu_keys, 0.3)
    lmoving = abs(speed(t, lu_keys)) > 20
    if lmoving:
        actor(c, tl, t, "luna", lu_keys, QUAY, 0.8, camx=camx)
    elif t < T("hb_oia"):
        kat(c, tl, t, "luna", W_(lx), QUAY + 4, 0.8, 1, "sit",
            eyes="happy" if T("hb_wash") <= t < T("hb_oia") else "open")
    else:
        kat(c, tl, t, "luna", W_(lx), QUAY, 0.8, -1, "stand", look=(0.5, 0.3))
    # Whiskers
    if t < T("hb_mine"):
        wkeys = [(s0, 640), (T("hb_welcome", 0.6), 1560)]
        if t < T("hb_welcome", 0.7):
            actor(c, tl, t, "whiskers", wkeys, QUAY, 0.85, camx=camx)
        else:
            munch = T("hb_munch") <= t < T("hb_munch", 1)
            kat(c, tl, t, "whiskers", W_(1560), QUAY + 4, 0.85, -1, "sit",
                mouth=laughing(t, 0.8) if munch else tl.mouth("whiskers", t),
                eyes="happy" if munch or t < T("hb_narr") else "open",
                look=(0.5, -0.5) if T("hb_narr") <= t < T("hb_munch") else (0, 0))
    elif t < T("hb_pull"):
        keys = [(T("hb_mine"), 1560), (T("hb_mine", 1.0), 1940)]
        x = smooth(t, keys, 0.2)
        mv = abs(speed(t, keys)) > 20
        kat(c, tl, t, "whiskers", W_(x), QUAY, 0.85, 1, "walk" if mv else "stand", walk=x / 10, look=(0.5, -1))
    elif t < T("hb_pull", 0.5):
        k = ease(tl.prog("hb_pull", t, 0.1, 0.48))
        x = lerp(1940, 1760, k)
        jig = 3 * math.sin(t * 30) if k > 0.3 else 0
        # big octopus stretched between line and Whiskers' paws
        py = lerp(560, 600, k)
        P.octopus(c, W_(1940) + (W_(x) - W_(1940)) * 0.25, 430 + (py - 430) * 0.3 - 8, 0.95, t,
                  sway=lerp(0, -3, k), stretch=lerp(1.0, 1.4, k))
        kat(c, tl, t, "whiskers", W_(x) + jig, QUAY, 0.85, 1, "crouch" if k > 0.05 else "stand",
            look=(0.5, -1), eyes="closed" if k > 0.4 else "open", mouth=0.3 * k)
    elif t < T("hb_pull", 0.86):
        u = tl.prog("hb_pull", t, 0.5, 0.86)
        x = lerp(1760, 1080, u)
        y = lerp(QUAY - 40, 560, u) + arc_y(u, 340)
        kat(c, tl, t, "whiskers", W_(x), y, 0.85, -1, "leap", eyes="wide", mouth=0.8, squash=1.1)
        P.octopus(c, W_(x) - 50, y - 90, 0.7, t, sway=-1.2)
    else:
        # swimming, then climbing out wet
        out = tl.prog("hb_goat", t, 0.0, 0.5)
        if out <= 0:
            wy = 568 + 3 * math.sin(t * 4)
            kat(c, tl, t, "whiskers", W_(1080), wy, 0.85, 1, "swim", wet=1.0,
                eyes="happy" if T("hb_wash") <= t < T("hb_wash", 1) else "open")
            P.octopus(c, W_(1150), wy - 70, 0.6, t, sway=0.5 * math.sin(t * 2))
        else:
            keys = [(T("hb_goat"), 1080), (T("hb_goat", 0.5), 1150), (s1 - 1.5, 1150), (s1, 1600)]
            x = smooth(t, keys, 0.2)
            y = lerp(560, QUAY, ease(out))
            mv = abs(speed(t, keys)) > 20
            kat(c, tl, t, "whiskers", W_(x), y, 0.85, 1, "walk" if mv else "stand", walk=x / 10, wet=1.0 - 0.5 * out)
    splash_fx(c, W_(1080), 580, t - T("hb_pull", 0.86), 0.9)
    return finish(c, tl, t)
