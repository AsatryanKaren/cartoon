"""Dublin -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in sync
with the speech. Static backgrounds are drawn once and cached; wide "world"
backgrounds are viewed through a panning camera.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.prague.scenes import track, smooth, arc_y, world_view, sparkles, hearts, bubble, shiver
from films.montblanc.props import shade_bottom
from films.dublin import props as P

SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "fergal": 0.6, "bridie": 3.3}
PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def sky(w, h, stops):
    return D.gradient(int(w * SS), int(h * SS), stops)


def overlay(c, col, alpha):
    if alpha <= 0.003:
        return c
    out = Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha)))
    out.tf = list(c.tf)
    return out


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", yfn=None, **kw):
    """Draw a character moving along x keyframes; faces the way it moves. yfn(x) -> ground y."""
    x = smooth(t, keys)
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    yy = yfn(x) if yfn else y
    if who == "pip":
        mouth = kw.pop("mouth", tl.mouth("pip", t))
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        kw.pop("hop", None)
        D.mouse(c, x, yy, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    elif who == "fergal":
        P.fergal(c, x, yy, s, face, t, mouth=kw.pop("mouth", tl.mouth("fergal", t)),
                 walk=x / 10 if moving else 0.0, **kw)
    elif who == "bridie":
        P.bridie(c, x, yy, s, face, t, mouth=kw.pop("mouth", tl.mouth("bridie", t)),
                 walk=x / 14 if moving else 0.0, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kitty(c, tl, t, who, x, yy, s, face, pose, walk=x / 12 if moving else 0.0, **kw)
    return x


def title_text(c, k, k2, line1, line2, col1=(255, 240, 200), col2=(255, 250, 225), y=150):
    if k > 0:
        c.text(W / 2, y - 30 * (1 - k), line1, 46, mix((120, 170, 210), col1, k), stroke=3 * k)
    if k2 > 0:
        c.text(W / 2, y + 85, line2, 30 + 62 * k2, mix((120, 170, 210), col2, k2), stroke=5 * k2,
               stroke_fill=(40, 70, 50))


def the_end(c, tl, t, event, y=640, a=0.3, b=0.55):
    k = ease(tl.prog(event, t, a, b))
    if k > 0:
        c.text(W / 2, y, "The End", 30 + 40 * k, mix((250, 228, 190), (255, 214, 90), k), stroke=4 * k)


DAY_SKY = [(0, (110, 170, 230)), (0.55, (176, 214, 240)), (1, (214, 234, 246))]
GREY_SKY = [(0, (120, 130, 146)), (0.6, (160, 168, 180)), (1, (186, 192, 200))]
DUSK_SKY = [(0, (70, 90, 160)), (0.4, (180, 140, 170)), (0.7, (250, 180, 140)), (1, (255, 214, 160))]
NIGHT = ((30, 36, 90), 0.3)


def hills_layer(c, w, base, seed=1, cols=(P.GRASS_L, P.GRASS, P.GRASS_D), walls=True, amp=50):
    """Rolling green hills in a few bands, criss-crossed by stone walls."""
    rng = np.random.default_rng(seed)
    for band, col in enumerate(cols):
        y0 = base + band * 70
        ph = rng.uniform(0, 6)
        pts = [(x, y0 - amp * (0.6 + 0.4 * math.sin(x / (260 - band * 40) + ph)) + 20 * math.sin(x / 90 + ph * 2))
               for x in range(-40, int(w) + 60, 30)]
        c.poly(pts + [(w + 60, H + 10), (-40, H + 10)], col, ol=None)
        c.line(pts, mix(col, (40, 80, 40), 0.35), 2, cap=False)
        if walls:
            for k in range(int(w / 260)):
                x0 = rng.uniform(0, w)
                n = int(rng.integers(3, 6))
                seg = []
                for j in range(n):
                    xx = x0 + j * 50
                    yy = y0 - amp * (0.6 + 0.4 * math.sin(xx / (260 - band * 40) + ph)) + 20 * math.sin(xx / 90 + ph * 2)
                    seg.append((xx, yy + 18 + j * 10 + band * 6))
                P.stone_wall(c, seg, 0.55 + 0.15 * band, seed=int(seed * 10 + k + band * 100))


# =================================================================== title

def title_bg():
    def make():
        c = Canvas(sky(W, H, DAY_SKY))
        for x, y, s in ((200, 120, 1.1), (560, 80, 0.8), (1080, 150, 1.2)):
            D.cloud(c, x, y, s)
        hills_layer(c, W, 420, seed=3, amp=40)
        P.castle_ruin(c, 980, 410, 0.55)
        P.round_tower(c, 250, 420, 0.48)
        rng = np.random.default_rng(5)
        for _ in range(9):
            P.sheep(c, rng.uniform(60, 1220), rng.uniform(520, 600), 0.32, int(rng.choice([-1, 1])),
                    t=rng.uniform(0, 9), graze=rng.uniform(0, 1))
        # foreground stone wall the cats sit on
        c.rect(0, 640, W, H, P.GRASS_D, ol=None)
        P.stone_wall(c, [(-20, 660), (W + 20, 652)], 1.6, seed=9)
        for x in range(0, W, 46):
            D.flower(c, x + 10, 712, (255, 230, 120) if x % 92 else (250, 250, 250), 0.6)
        return c.img
    return cached("title", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    k = ease(tl.prog("t_open", t, 0.0, 0.9))
    P.rainbow(c.img, 640, 560, 520, band=15, alpha=0.55, reveal=k)
    D.cat(c, 560, 628, D.WHISKERS, 0.8, 1, "sit", t=t, seed=0, look=(1, -1))
    D.cat(c, 680, 630, D.LUNA, 0.76, -1, "sit", t=t, seed=1.3, look=(-1, -1), tail=math.sin(t * 1.5))
    D.butterfly(c, 760 + 60 * math.sin(t * 0.8), 480 + 30 * math.sin(t * 1.3), t, 0.7)
    k1 = ease(tl.prog("t_open", t, 0.0, 0.7))
    k2 = ease(tl.prog("t_open", t, 0.35, 1.0))
    title_text(c, k1, k2, "Whiskers and the", "RAINBOW'S END", y=130)
    return c


# ================================================================== garden (home)

POND = (930, 610, 250, 66)        # cx, cy, rx, ry
SILL_Y = 412


def garden_bg(mode):
    """The cats' house and garden. mode: 'rain' (grey, wet) or 'evening' (golden, after the rain)."""
    def make():
        rainy = mode == "rain"
        c = Canvas(sky(W, H, GREY_SKY if rainy else DUSK_SKY))
        if rainy:
            for x, y, s in ((300, 90, 1.6), (700, 60, 1.9), (1100, 100, 1.7), (900, 160, 1.2)):
                D.cloud(c, x, y, s, (150, 158, 172))
        else:
            c.glow(1060, 300, 240, 200, (255, 236, 180), (250, 190, 150), steps=10)
            c.circle(1060, 300, 46, (255, 236, 160), ol=None)
            for x, y, s in ((800, 120, 1.1), (1180, 170, 0.9)):
                D.cloud(c, x, y, s, (255, 226, 214))
        # distant hills, garden fence, trees
        far = (120, 150, 120) if rainy else (140, 150, 120)
        c.poly([(0, 430), (300, 390), (700, 420), (1000, 380), (W, 420), (W, 500), (0, 500)], far, ol=None)
        D.tree(c, 700, 470, 0.9, leaf=(80, 140, 84) if rainy else (100, 150, 80))
        D.tree(c, 1180, 470, 1.0, leaf=(70, 130, 80) if rainy else (90, 140, 70))
        grass = (96, 156, 86) if rainy else (130, 170, 84)
        c.rect(0, 470, W, H, grass, ol=None)
        for x in range(560, W + 20, 44):
            c.rect(x, 420, x + 30, 486, (210, 190, 150) if rainy else (230, 200, 150), w=2, r=3)
            c.poly([(x, 420), (x + 15, 406), (x + 30, 420)], (210, 190, 150) if rainy else (230, 200, 150), w=2)
        c.rect(560, 440, W, 452, (196, 176, 136) if rainy else (214, 186, 136), w=2)
        # the stream: comes in under the fence, through the pond, out at the bottom right
        water = (110, 130, 160) if rainy else (150, 150, 190)
        water_l = (160, 180, 210) if rainy else (230, 200, 200)
        c.poly([(1150, 486), (1190, 486), (1110, 560), (1050, 580), (1010, 560)], water, ol=None)
        c.poly([(1080, 640), (1150, 640), (1240, 700), (1290, 700), (1290, H), (1180, H)], water, ol=None)
        # pond
        cx, cy, rx, ry = POND
        c.ellipse(cx, cy, rx + 16, ry + 10, (120, 110, 100), ol=None)
        c.ellipse(cx, cy, rx, ry, water, w=3)
        c.ellipse(cx - 40, cy - 16, rx * 0.6, ry * 0.4, water_l, ol=None)
        for k in range(7):
            a = k * 0.9
            c.ellipse(cx + math.cos(a) * (rx + 6), cy + math.sin(a) * (ry + 4), 16, 9, STONE_C, ol=OUT, w=1.5)
        D.lily_pad(c, cx + 120, cy + 20, 26)
        D.lily_pad(c, cx - 150, cy + 10, 22)
        for x, col in ((620, (240, 120, 160)), (660, (250, 220, 90)), (1240, (240, 120, 160)), (760, (250, 250, 250))):
            D.flower(c, x, 690, col, 0.9)
        D.bush(c, 640, 520, 0.9, (80, 140, 80) if rainy else (100, 150, 80))
        # the house
        wall = (232, 214, 182) if rainy else (246, 222, 184)
        c.rect(-10, 60, 540, H, wall, w=3)
        for y in range(80, H, 34):
            c.line([(-10, y), (540, y)], mix(wall, (150, 120, 90), 0.12), 1.5, cap=False)
        c.poly([(-30, 70), (560, 70), (520, 0), (-30, 0)], (150, 70, 60), w=3)
        c.rect(-20, 62, 560, 78, (120, 120, 130), w=2)        # gutter
        c.rect(520, 78, 536, H, (120, 120, 130), w=2)         # drainpipe
        # window: warm room inside, open casements
        c.rect(110, 150, 450, SILL_Y, (110, 80, 70) if rainy else (130, 90, 70), w=4)
        inside = D.gradient(320 * SS, 250 * SS, [(0, (255, 214, 150)), (1, (220, 150, 100))])
        c.img.paste(inside, (120 * SS, 158 * SS))
        c.rect(150, 300, 260, 340, (196, 100, 80), ol=None)       # sofa back inside
        c.circle(400, 230, 22, (255, 240, 180), ol=None)           # lamp
        c.rect(394, 250, 406, 330, (150, 110, 80), ol=None)
        c.rect(120, 158, 440, SILL_Y, None, w=4)
        c.line([(280, 158), (280, SILL_Y - 6)], (250, 250, 240), 6, cap=False)
        c.poly([(110, 150), (60, 170), (60, 400), (110, SILL_Y)], (250, 250, 240), w=3)   # open casements
        c.poly([(450, 150), (500, 170), (500, 400), (450, SILL_Y)], (250, 250, 240), w=3)
        c.poly([(116, 166), (72, 182), (72, 390), (116, 400)], (170, 200, 220), ol=None)
        c.poly([(444, 166), (488, 182), (488, 390), (444, 400)], (170, 200, 220), ol=None)
        c.rect(90, SILL_Y, 470, SILL_Y + 18, (250, 248, 240), w=3, r=3)
        # flower box under the sill
        c.rect(120, SILL_Y + 18, 440, SILL_Y + 56, (150, 96, 60), w=2.5)
        for k in range(8):
            D.flower(c, 140 + k * 40, SILL_Y + 22, ((240, 90, 120), (250, 210, 80), (250, 250, 250))[k % 3], 0.7)
        c.rect(150, 520, 260, H, (130, 70, 60), w=3)           # back door
        c.circle(240, 620, 5, P.GOLD, w=1.5)
        return c.img
    return cached(("garden", mode), make)


STONE_C = (150, 146, 140)


def pond_ripples(c, t, k=1.0, col=(170, 190, 220)):
    cx, cy, rx, ry = POND
    for i in range(6):
        u = (t * 0.5 + i / 6) % 1
        px = cx - 160 + (i * 67) % 320
        py = cy - 30 + (i * 23) % 60
        r = 6 + 20 * u
        c.ellipse(px, py, r, r * 0.3, None, ol=mix(col, (110, 130, 160), u), w=1.5 * k)


def map_card(c, x, y, k, t, scale=1.0):
    """The bottle's map, unrolling into view."""
    if k <= 0.01:
        return
    img = cached("mapimg", lambda: P.map_img())
    w0, h0 = img.size[0] / SS, img.size[1] / SS
    s = scale * ease(k)
    ww, hh = int(w0 * s * SS), int(h0 * s * SS * (0.15 + 0.85 * ease(k)))
    if ww < 4 or hh < 4:
        return
    c.img.paste(img.resize((ww, hh)), (int(x * SS - ww / 2), int(y * SS - hh / 2)))
    c.rect(x - ww / SS / 2, y - hh / SS / 2, x + ww / SS / 2, y + hh / SS / 2, None, w=3, r=4)
    if k > 0.8:
        sparkles(c, x + ww / SS / 2 - 40, y - hh / SS / 2 + 30, t, r=26, n=5, k=0.8)


def goldfish_pot(sub, t):
    sub.rect(0, 0, 240, 240, (255, 236, 190), ol=None)
    sub.glow(120, 140, 110, 90, (255, 240, 170), (255, 236, 190), steps=6)
    sub.ellipse(120, 170, 70, 46, (230, 180, 60), w=3)
    sub.ellipse(120, 132, 66, 14, (250, 210, 80), w=3)
    sub.ellipse(120, 132, 58, 9, (120, 170, 220), ol=None)
    for k in range(4):
        fx = 80 + k * 28 + 6 * math.sin(t * 3 + k)
        fy = 120 - 20 * abs(math.sin(t * 2.4 + k * 1.3))
        sub.ellipse(fx, fy, 13, 8, (250, 130, 40), w=2)
        sub.poly([(fx - 12, fy), (fx - 24, fy - 8), (fx - 24, fy + 8)], (250, 130, 40), w=2)
        sub.circle(fx + 6, fy - 2, 2, OUT, ol=None)
    sparkles(sub, 120, 120, t, r=60, n=5, k=1.0)


def bottle(tl, t):
    T = tl.t
    c = Canvas(garden_bg("rain").copy())
    cx, cy, rx, ry = POND
    pond_ripples(c, t)
    # the bottle bobbing on the pond until Whiskers grabs it
    grab = T("b_dive", 0.72)
    held = t >= grab
    if not held:
        bx = cx + 60 + 12 * math.sin(t * 0.7)
        by = cy - 6 + 4 * math.sin(t * 2.1)
        P.bottle(c, bx, by, 0.9, 10 * math.sin(t * 1.3))
        if t >= T("b_spot"):
            sparkles(c, bx, by - 10, t, r=30, n=5, k=0.9)
    # Luna on the sill, later hops down to the lawn
    l_down = T("b_got", 0.2)
    if t < l_down:
        look = (1, 0.6) if t >= T("b_spot") else (0, 0.4)
        kitty(c, tl, t, "luna", 360, SILL_Y, 0.78, 1, "sit", look=look)
    else:
        u = tl.prog("b_got", t, 0.2, 0.6)
        if u < 1:
            x = lerp(360, 600, ease(u))
            y = lerp(SILL_Y, 670, ease(u)) + arc_y(u, 60)
            kitty(c, tl, t, "luna", x, y, 0.8, 1, "leap" if u < 0.9 else "stand")
        else:
            gx = 600 if t < T("b_go", 0.2) else lerp(600, 1500, ease(tl.prog("b_go", t, 0.2, 1.0)))
            kitty(c, tl, t, "luna", gx, 670, 0.8, 1, "walk" if t >= T("b_go", 0.2) else "stand",
                  walk=gx / 12, eyes="happy" if T("b_gold") <= t < T("b_goldfish") else "open")
    # Whiskers: sulking on the sill, leaps at the 'fish', swims, climbs out with the bottle
    d0 = T("b_dive")
    if t < d0:
        eyes = "wide" if t >= T("b_fish") else ("closed" if t < T("b_spot") and not tl.talking("whiskers", t) else "open")
        kitty(c, tl, t, "whiskers", 220, SILL_Y, 0.8, 1, "sit", eyes=eyes,
              look=(1, 0.6) if t >= T("b_look") else (0, 0), head_dy=4 if t < T("b_spot") else 0)
    elif t < T("b_dive", 0.42):
        u = tl.prog("b_dive", t, 0.08, 0.42)
        x = lerp(220, cx + 30, u)
        y = lerp(SILL_Y, cy, u) + arc_y(u, 170)
        kitty(c, tl, t, "whiskers", x, y, 0.8, 1, "crouch" if u <= 0 else "leap", eyes="wide")
    elif t < T("b_dive", 0.8):
        u = tl.prog("b_dive", t, 0.42, 0.8)
        for k in range(3):
            r = 30 + 160 * ((u * 1.4 + k * 0.3) % 1)
            c.ellipse(cx + 30, cy, r, r * 0.25, None, ol=(200, 214, 236), w=2)
        if u < 0.25:
            for k in range(8):
                a = k * math.pi / 7
                c.ellipse(cx + 30 + math.cos(a) * 70 * u * 4, cy - math.sin(a) * 90 * u * 4 + 40 * (u * 4) ** 2,
                          5, 8, (190, 214, 240), ol=None)
        kitty(c, tl, t, "whiskers", lerp(cx + 30, cx + 60, min(1, u * 2)), cy + 4, 0.8, 1, "swim", wet=1,
              eyes="wide" if u < 0.6 else "happy")
        if held:
            P.bottle(c, cx + 60 + 34, cy - 18, 0.6, -20)
    else:
        u = tl.prog("b_dive", t, 0.8, 1.0)
        x = lerp(cx - 40, 740, ease(u))
        y = lerp(cy + 10, 670, ease(u))
        wet = 1 - 0.6 * tl.prog("b_goldfish", t)
        face = 1 if t < T("b_got", 0.3) else -1
        eyes = "happy" if T("b_got") <= t < T("b_got", 0.5) else ("wide" if t >= T("b_goldfish") else "open")
        kitty(c, tl, t, "whiskers", x, y, 0.8, face, "stand", wet=wet, eyes=eyes,
              squash=1 - 0.12 * math.sin(math.pi * u))
        if t < T("b_cork"):
            P.bottle(c, x + face * 70, y - 70, 0.55, -10 * face)
        elif t < T("b_go", 0.2):
            P.bottle(c, x + face * 40, y - 8, 0.6, 0, map_in=t < T("b_cork", 0.5), cork=t < T("b_cork", 0.3))
        if t >= T("b_go", 0.2):
            pass
    if t >= T("b_go", 0.25):
        gx = lerp(740, 1600, ease(tl.prog("b_go", t, 0.25, 1.0)))
        kitty(c, tl, t, "whiskers", gx, 672, 0.8, 1, "walk", walk=gx / 12)
    # cork pops
    if T("b_cork", 0.3) <= t < T("b_cork", 0.8):
        u = tl.prog("b_cork", t, 0.3, 0.8)
        c.poly([(700 + 80 * u, 600 - 160 * u + 200 * u * u), (712 + 80 * u, 600 - 160 * u + 200 * u * u),
                (712 + 80 * u, 612 - 160 * u + 200 * u * u)], (190, 140, 90), w=1.5)
    # rain: heavy at first, softer later
    P.rain_streaks(c, t, 1.0 - 0.6 * tl.prog("b_map", t), seed=3, n=140)
    # the map
    mk = tl.prog("b_cork", t, 0.5, 1.0) * (1 - tl.prog("b_goldfish", t, 0.0, 0.15))
    if mk > 0:
        map_card(c, 640, 270, mk, t, 0.92)
    # thought bubble: a pot of goldfish
    bk = tl.prog("b_goldfish", t, 0.1, 0.3) * (1 - tl.prog("b_go", t, 0.0, 0.3))
    if bk > 0 and t < T("b_go", 0.25):
        bubble(c, 860, 250, 120, bk, lambda sub: goldfish_pot(sub, t), t, bg=(255, 236, 190), tail=(-0.6, 1))
    shade_bottom(c, tl, t, 0.45)
    return c


# =================================================================== ferry

FW = 2400
SEA_Y = 470


def sea_bg():
    def make():
        c = Canvas(sky(FW, H, [(0, (120, 176, 230)), (0.6, (190, 220, 240)), (1, (220, 236, 246))]), size=(FW, H))
        for x, y, s in ((200, 120, 1.3), (700, 80, 1.0), (1200, 140, 1.4), (1700, 90, 1.1), (2200, 130, 1.2)):
            D.cloud(c, x, y, s)
        # Dublin Bay on the right: Howth head, the Poolbeg chimneys, the city
        c.poly([(1500, SEA_Y), (1640, SEA_Y - 70), (1760, SEA_Y - 86), (1880, SEA_Y - 40), (1940, SEA_Y)],
               (110, 150, 110), ol=None)
        c.poly([(2000, SEA_Y), (2050, SEA_Y - 20), (FW, SEA_Y - 30), (FW, SEA_Y)], (120, 150, 130), ol=None)
        c.poly([(2100, SEA_Y - 22), (2300, SEA_Y - 70), (FW, SEA_Y - 60), (FW, SEA_Y - 25)], (130, 160, 150),
               ol=None)
        for k, xx in enumerate((2060, 2090)):
            c.poly([(xx - 7, SEA_Y - 10), (xx - 5, SEA_Y - 150), (xx + 5, SEA_Y - 150), (xx + 7, SEA_Y - 10)],
                   (240, 240, 236), w=1.5)
            for j in range(5):
                yy = SEA_Y - 22 - j * 26
                c.rect(xx - 6.5, yy - 12, xx + 6.5, yy, (210, 60, 50), ol=None)
        rng = np.random.default_rng(4)
        for k in range(20):
            xx = 2130 + k * 14
            hh = rng.uniform(16, 50)
            c.rect(xx, SEA_Y - 20 - hh, xx + 12, SEA_Y - 20, mix((200, 200, 210), (170, 170, 190), rng.random()),
                   ol=None)
        P.spire(c, 2280, SEA_Y - 30, 140)
        # sea
        sea = D.gradient(FW * SS, (H - SEA_Y) * SS, [(0, (70, 130, 170)), (1, (36, 76, 120))])
        c.img.paste(sea, (0, SEA_Y * SS))
        return c.img
    return cached("sea", make)


def waves_fg(c, t, y0, y1, drift=60.0, n=50, seed=2, x0=0, x1=W, col=(160, 200, 225)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = rng.uniform(x0, x1 + 80)
        y = rng.uniform(y0, y1)
        ln = 14 + 36 * (y - y0) / max(1, y1 - y0)
        ph = rng.uniform(0, 6.28)
        xx = (x - drift * t) % (x1 - x0 + 80) + x0 - 40
        k = 0.5 + 0.5 * math.sin(t * 2 + ph)
        c.arc(xx, y, ln * (0.6 + 0.4 * k), 6, 200, 340, col, 2.5)


def deck_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (120, 176, 230)), (0.6, (190, 220, 240)), (1, (220, 236, 246))]))
        for x, y, s in ((220, 110, 1.2), (760, 70, 0.9), (1150, 130, 1.1)):
            D.cloud(c, x, y, s)
        return c.img
    return cached("deck", make)


def ferry(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["ferry"]
    close = t >= T("f_wobble")
    if not close:
        u = (t - s0) / max(1e-6, T("f_wobble") - s0)
        fx = lerp(420, 1250, u)
        camx = clamp(fx - 520, 0, FW - W)
        c = world_view(sea_bg(), camx, 0)
        waves_fg(c, t, SEA_Y + 10, H, drift=0, n=120, seed=3, x0=0, x1=FW)
        bob = 5 * math.sin(t * 1.4)
        s = 0.72
        fy = SEA_Y + 150 + bob
        P.ferry(c, fx, fy, s, t)
        # the cats at the bow rail
        D.cat(c, fx + 300 * s, fy - 100 * s, D.LUNA, 0.36, 1, "sit", t=t, seed=1.3)
        D.cat(c, fx + 255 * s, fy - 96 * s, D.WHISKERS, 0.38, 1, "sit", t=t, seed=0)
        # bow wave and wake
        for k in range(4):
            uu = (t * 0.8 + k / 4) % 1
            c.ellipse(fx + 380 * s - 40 * uu, fy + 4, 30 + 60 * uu, 8, None, ol=P.FOAM, w=3 * (1 - uu) + 0.5)
            c.ellipse(fx - 360 * s - 180 * uu, fy + 2, 40 + 80 * uu, 6, None, ol=P.FOAM, w=3 * (1 - uu) + 0.5)
        for k in range(3):
            P.gull(c, fx + 120 + 200 * k + 30 * math.sin(t + k), 180 + 30 * math.sin(t * 0.7 + k * 2), t, 0.8,
                   seed=k)
        c.pop()
        return c
    # close shot on the front deck, the sea rocking
    roll = math.sin(t * 1.3) * 18
    c = Canvas(deck_bg().copy())
    hy = 400 + roll
    # Dublin coming over the horizon
    k = ease(tl.prog("f_look", t, 0.0, 1.0)) if t < T("f_arrive") else 1.0
    if k > 0:
        dx = lerp(1500, 760, k) + 30 * tl.prog("f_arrive", t)
        c.poly([(dx - 300, hy), (dx - 200, hy - 50), (dx - 80, hy - 60), (dx, hy - 26), (dx + 600, hy - 30),
                (dx + 700, hy)], (120, 156, 126), ol=None)
        for xx in (dx + 80, dx + 106):
            c.poly([(xx - 6, hy - 20), (xx - 4, hy - 140), (xx + 4, hy - 140), (xx + 6, hy - 20)], (240, 240, 236),
                   w=1.5)
            for j in range(5):
                c.rect(xx - 5.5, hy - 34 - j * 24, xx + 5.5, hy - 22 - j * 24, (210, 60, 50), ol=None)
        for j in range(16):
            hh = 20 + (j * 37) % 40
            c.rect(dx + 150 + j * 18, hy - 26 - hh, dx + 164 + j * 18, hy - 26, (200, 200, 214), ol=None)
        P.spire(c, dx + 300, hy - 26, 120)
    c.rect(0, hy, W, H, (60, 120, 166), ol=None)
    waves_fg(c, t, hy + 10, 520, drift=40, n=60, seed=5, col=(140, 190, 220))
    # deck and rail
    c.rect(0, 560, W, H, (120, 132, 128), ol=None)
    for x in range(-40, W + 40, 90):
        c.line([(x, 560), (x - 60, H)], (104, 116, 112), 2, cap=False)
    c.rect(0, 552, W, 566, (40, 140, 90), ol=None)
    c.line([(0, 470), (W, 470)], (250, 250, 250), 7, cap=False)
    c.line([(0, 510), (W, 510)], (250, 250, 250), 4, cap=False)
    for x in range(20, W, 70):
        c.line([(x, 470), (x, 556)], (250, 250, 250), 4, cap=False)
    c.line([(0, 470), (W, 470)], OUT, 1.5, cap=False)
    # the cats: Whiskers clings to the rail, Luna on her toes looking out
    wob = math.sin(t * 1.3)
    sq = 1.0
    kitty(c, tl, t, "whiskers", 430 + 10 * wob, 640, 1.0, 1, "crouch", eyes="wide" if t < T("f_look") else "open",
          squash=sq, tail=wob)
    if t < T("f_look"):
        shiver(c, 470, 560, t, 1.0)
    look_k = t >= T("f_look")
    kitty(c, tl, t, "luna", 720, 640, 1.0, 1, "stand", look=(1, -0.3) if look_k else (-1, 0.2),
          eyes="happy" if T("f_arrive") <= t else "open", head_dy=-8 if look_k else 0)
    for k in range(2):
        P.gull(c, 900 + 200 * k + 60 * math.sin(t * 0.8 + k), 150 + 40 * math.sin(t * 0.6 + k), t, 1.1, -1, seed=k)
    shade_bottom(c, tl, t, 0.4)
    return c


# =================================================================== dublin

DW = 3200
STREET_Y = 600
BR0, BR1 = 1950, 3050


def deck_y(x):
    if x <= BR0 or x >= BR1:
        return STREET_Y
    u = (x - BR0) / (BR1 - BR0)
    return STREET_Y - 70 * math.sin(math.pi * u)


def dublin_bg():
    def make():
        c = Canvas(sky(DW, H, [(0, (120, 170, 226)), (0.6, (196, 222, 240)), (1, (226, 238, 246))]), size=(DW, H))
        for x, y, s in ((200, 90, 1.0), (900, 70, 1.2), (1700, 110, 1.0), (2500, 80, 1.3), (3000, 120, 0.9)):
            D.cloud(c, x, y, s)
        # the Georgian terrace
        x = -30
        k = 0
        rng = np.random.default_rng(11)
        while x < 1800:
            w = 236
            h = 380 + 20 * (k % 2)
            brick = mix(P.BRICK, (196, 110, 80), rng.uniform(0, 0.5))
            P.georgian_house(c, x, STREET_Y, w, h, brick, P.DOOR_COLS[k % len(P.DOOR_COLS)], seed=k)
            x += w
            k += 1
        # the quays: buildings across the river
        cols = [(230, 200, 140), (180, 90, 80), (120, 150, 190), (240, 230, 210), (200, 120, 90), (150, 180, 140),
                (236, 196, 110), (190, 150, 190)]
        P.custom_house(c, 2950, 470, 0.8)
        P.spire(c, 2200, 470, 300)
        xx = 1790
        j = 0
        while xx < DW + 40:
            w = 90 + (j * 37) % 60
            P.quay_building(c, xx, 470, w, 150 + (j * 53) % 90, cols[j % len(cols)], seed=j)
            xx += w
            j += 1
        # far quay wall, the Liffey
        c.rect(1790, 470, DW, 500, (160, 156, 146), w=2)
        river = D.gradient((DW - 1790) * SS, (H - 500) * SS, [(0, P.RIVER), (1, P.RIVER_D)])
        c.img.paste(river, (1790 * SS, 500 * SS))
        # near quay on the street side
        c.rect(1790, STREET_Y, BR0 + 10, H, (170, 166, 156), w=2)
        c.rect(BR1 - 10, STREET_Y, DW, H, (170, 166, 156), w=2)
        # pavement and road in front of the houses
        c.rect(-10, STREET_Y, 1800, STREET_Y + 26, (196, 192, 184), w=2)
        c.rect(-10, STREET_Y + 26, 1800, H, (110, 108, 116), ol=None)
        for yy in range(STREET_Y + 40, H, 22):
            for xx in range(-10 + (yy // 22 % 2) * 20, 1800, 40):
                c.rect(xx, yy, xx + 36, yy + 18, (124, 122, 130), ol=None, r=4)
        # lamp posts
        for lx in (400, 1100, 1700):
            c.rect(lx - 4, STREET_Y - 200, lx + 4, STREET_Y, (40, 44, 50), ol=None)
            c.rect(lx - 12, STREET_Y - 226, lx + 12, STREET_Y - 196, (250, 236, 180), w=2)
            c.poly([(lx - 15, STREET_Y - 226), (lx, STREET_Y - 240), (lx + 15, STREET_Y - 226)], (40, 44, 50), w=2)
        # the Ha'penny Bridge
        P.hapenny_bridge(c, BR0, BR1, lambda u: STREET_Y - 70 * math.sin(math.pi * u), 1.0)
        return c.img
    return cached("dublin", make)


def dublin(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["dublin"]
    # cats' path along the street, then up onto the bridge
    keys_l = [(s0, 120), (T("d_map", 0.0), 1150), (T("d_walk"), 1150), (T("d_walk", 1), 2350)]
    keys_w = [(s0, -20), (T("d_map", 0.0), 1010), (T("d_walk", 0.1), 1010), (T("d_walk", 1), 2220)]
    lx = smooth(t, keys_l)
    camx = clamp(lx - 640, 0, DW - W)
    camx = min(camx, 1880)
    c = world_view(dublin_bg(), camx, 0)
    if camx > 1100:
        P.notes  # river shimmer
        rng = np.random.default_rng(3)
        for _ in range(40):
            x = rng.uniform(1800, DW)
            y = rng.uniform(510, H)
            ph = rng.uniform(0, 6)
            k = 0.5 + 0.5 * math.sin(t * 1.6 + ph)
            if k > 0.25:
                c.line([(x - 18 * k, y), (x + 18 * k, y)], P.RIVER_L, 2, cap=False)
    # Fergal busking in the middle of the bridge
    fx = 2560
    talking = tl.talking("fergal", t)
    play = 0.0 if talking or t >= T("d_fergal") and t < T("d_music", 0.8) else 1.0
    P.fergal(c, fx, deck_y(fx), 0.9, -1, t, mouth=tl.mouth("fergal", t), play=play,
             eyes="happy" if t >= T("d_music") else "open")
    c.ellipse(fx - 90, deck_y(fx - 90) - 4, 22, 7, (110, 100, 90), w=2)          # cap for coins
    if play:
        P.notes(c, fx - 30, deck_y(fx) - 220, t, 1.2)
    # the cats
    sp = 0.85
    actor(c, tl, t, "luna", keys_l, 0, sp, yfn=deck_y,
          look=(1, 0) if t < T("d_fergal") else (1, -0.4))
    wfacing = 1
    actor(c, tl, t, "whiskers", keys_w, 0, sp, yfn=deck_y, face=wfacing,
          eyes="wide" if T("d_penny") <= t < T("d_west") else "open")
    if T("d_map") <= t < T("d_walk", 0.2):
        P.map_img  # noqa
        mx = smooth(t, keys_l) + 70
        c.rect(mx - 30, deck_y(mx) - 130, mx + 30, deck_y(mx) - 90, (238, 222, 176), w=2)
        c.line([(mx - 20, deck_y(mx) - 116), (mx + 16, deck_y(mx) - 104)], (150, 70, 50), 2, cap=False)
    c.pop()
    shade_bottom(c, tl, t, 0.35)
    return c


# =================================================================== pub

def pub_bg():
    def make():
        wall = (122, 74, 48)
        c = Canvas(bg=wall)
        # wood panelling
        for x in range(0, W, 80):
            c.rect(x + 4, 60, x + 76, 440, mix(wall, (150, 96, 60), 0.4), w=2, r=4)
        c.rect(0, 440, W, 470, (90, 54, 34), ol=None)
        c.rect(0, 0, W, 60, (70, 44, 30), ol=None)
        for x in range(0, W, 160):
            c.rect(x, 0, x + 26, 60, (56, 34, 22), ol=None)
        # window with the night street
        c.rect(560, 90, 760, 300, (40, 50, 90), w=4)
        D.stars(c, 3, 10, 200, 100)
        c.line([(660, 90), (660, 300)], (90, 54, 34), 5, cap=False)
        c.line([(560, 200), (760, 200)], (90, 54, 34), 5, cap=False)
        c.circle(720, 130, 14, (250, 246, 215), ol=None)
        # bar counter on the right with shelves
        c.rect(860, 120, W, 160, (90, 54, 34), w=2)
        c.rect(860, 230, W, 250, (90, 54, 34), w=2)
        rng = np.random.default_rng(2)
        for row, y in ((0, 120), (1, 230)):
            x = 880
            while x < W - 20:
                kind = rng.integers(3)
                if kind == 0:   # jar
                    col = [(220, 180, 90), (180, 90, 80), (120, 160, 90)][rng.integers(3)]
                    c.rect(x, y - 40, x + 26, y, col, w=2, r=4)
                    c.rect(x - 2, y - 46, x + 28, y - 38, (230, 230, 220), w=1.5)
                    x += 38
                elif kind == 1:  # teapot
                    c.ellipse(x + 18, y - 18, 20, 16, (60, 110, 170), w=2)
                    c.line([(x + 36, y - 22), (x + 48, y - 32)], (60, 110, 170), 4)
                    c.circle(x + 18, y - 36, 4, (60, 110, 170), w=1.5)
                    x += 58
                else:            # plate
                    c.circle(x + 18, y - 22, 20, (240, 240, 250), w=2)
                    c.circle(x + 18, y - 22, 12, (80, 120, 200), ol=None)
                    x += 46
        c.rect(860, 330, W, 470, (100, 60, 36), w=3)
        c.rect(850, 320, W, 340, (140, 90, 56), w=3)
        for x in range(880, W, 80):
            c.rect(x, 350, x + 60, 450, (110, 68, 42), w=2, r=4)
        # fireplace on the left
        c.rect(20, 220, 200, 460, (150, 146, 140), w=3)
        c.rect(50, 300, 170, 460, (40, 30, 30), w=2)
        c.rect(10, 206, 210, 226, (110, 70, 44), w=2)
        # floor
        c.rect(0, 470, W, H, (150, 104, 66), ol=None)
        for y in range(490, H, 40):
            c.line([(0, y), (W, y)], (130, 88, 56), 2, cap=False)
        for k in range(14):
            x = (k * 173) % W
            y = 470 + (k * 47) % 250
            c.line([(x, y), (x, y + 40)], (130, 88, 56), 2, cap=False)
        # lamps
        for lx in (300, 640, 980):
            c.line([(lx, 0), (lx, 50)], (40, 30, 30), 2, cap=False)
            c.glow(lx, 72, 70, 50, (255, 230, 160), (130, 82, 54), steps=8)
            c.poly([(lx - 26, 76), (lx - 14, 50), (lx + 14, 50), (lx + 26, 76)], (200, 140, 60), w=2)
        # a rug for the dance floor
        c.ellipse(640, 600, 250, 46, (160, 50, 50))
        c.ellipse(640, 600, 210, 34, (200, 140, 70), ol=None)
        c.ellipse(640, 600, 170, 24, (170, 60, 60), ol=None)
        # the table on the right
        c.rect(940, 520, 1220, 540, (110, 68, 42), w=3, r=4)
        c.rect(960, 540, 980, 660, (90, 54, 34), w=2)
        c.rect(1180, 540, 1200, 660, (90, 54, 34), w=2)
        return c.img
    return cached("pub", make)


def fire(c, x, y, t, s=1.0):
    for k in range(5):
        h = 50 + 20 * math.sin(t * 7 + k * 1.7)
        xx = x - 40 + k * 20
        c.poly([(xx - 14 * s, y), (xx + 2 * math.sin(t * 9 + k), y - h * s), (xx + 14 * s, y)],
               (255, 150 + 20 * (k % 2), 50), ol=None)
        c.poly([(xx - 7 * s, y), (xx, y - h * 0.5 * s), (xx + 7 * s, y)], (255, 230, 120), ol=None)


def pub(tl, t):
    T = tl.t
    c = Canvas(pub_bg().copy())
    fire(c, 110, 452, t)
    # musicians
    P.pub_musician(c, 250, 560, 0.95, 1, t, "badger", seed=0.3)
    P.pub_musician(c, 380, 566, 0.95, 1, t, "fox", seed=1.1)
    talking = tl.talking("fergal", t)
    P.fergal(c, 500, 600, 0.9, -1 if not talking else 1, t, mouth=tl.mouth("fergal", t), play=0 if talking else 1,
             eyes="happy" if t >= T("p_laugh") else "open")
    if not talking:
        P.notes(c, 470, 380, t, 1.2)
    P.notes(c, 300, 420, t + 0.7, 1.0)
    # dancers on the rug (they step aside when Whiskers dances)
    aside = ease(tl.prog("p_jig", t, 0.0, 0.15))
    stepping = 1.0 if t < T("p_jig") else 0.4
    P.dancer(c, lerp(600, 560, aside), 620, 0.95, 1, t, (60, 120, 200), seed=0.0, step=stepping)
    P.dancer(c, lerp(700, 780, aside), 626, 0.95, -1, t, (40, 150, 90), (150, 120, 100), seed=1.6, step=stepping)
    # soda bread on the table
    bread_left = 1 - tl.prog("p_eat", t, 0.05, 0.9)
    if bread_left > 0.05:
        P.soda_bread(c, 1060, 522, 0.7 + 0.5 * bread_left, bitten=1 - bread_left)
    c.ellipse(1060, 524, 70, 10, (240, 240, 250), w=2)                      # plate
    # Luna
    jig0, jig1 = T("p_jig"), T("p_jig", 1)
    if t < T("p_dance"):
        kitty(c, tl, t, "luna", 1150, 660, 0.85, -1, "sit", eyes="happy" if t < T("p_bread") else "open",
              tail=math.sin(t * 6))
    else:
        keys = [(T("p_dance"), 1150), (T("p_dance", 1), 820)]
        lx = actor(c, tl, t, "luna", keys, 660, 0.85)
        if False:
            pass
    # Whiskers
    if t < T("p_dance", 0.4):
        full = tl.prog("p_eat", t)
        eyes = "wide" if T("p_bread") <= t < T("p_eat") else ("happy" if t >= T("p_eat") else "open")
        mouth = tl.mouth("whiskers", t)
        if T("p_eat") <= t < T("p_eat", 0.9):
            mouth = 0.5 + 0.5 * math.sin(t * 18)
        kitty(c, tl, t, "whiskers", 985, 660, 0.85 + 0.05 * full, 1, "sit", eyes=eyes, mouth=mouth,
              squash=1 - 0.12 * full, look=(1, -0.6) if t >= T("p_bread") else (-1, 0))
    elif t < jig0:
        keys = [(T("p_dance", 0.4), 985), (jig0, 660)]
        actor(c, tl, t, "whiskers", keys, 660, 0.9, squash=0.88)
    elif t < T("p_jig", 0.78):
        # the jig: hops, flicks, spins, faster and faster -- then off toward the drum
        u = tl.prog("p_jig", t, 0.0, 0.78)
        speed = 6 + 10 * u
        hop = abs(math.sin(t * speed)) * (24 + 10 * u)
        x = 660 + 40 * math.sin(t * 3) if u < 0.6 else lerp(660, 420, ease((u - 0.6) / 0.4))
        face = 1 if math.sin(t * 2.5 * (1 + u)) > 0 else -1
        pose = "leap" if math.sin(t * speed * 2) > 0.3 else "stand"
        kitty(c, tl, t, "whiskers", x, 660 - hop, 0.9, face if u < 0.6 else -1, pose,
              eyes="happy" if u < 0.55 else "wide", squash=0.88 + 0.12 * math.sin(t * speed * 2))
        if u > 0.6:
            for k in range(3):
                c.line([(x + 60 + 20 * k, 600 - 20 * k), (x + 110 + 20 * k, 600 - 20 * k)], (255, 240, 200), 3)
    else:
        # crashed head-first into the bodhran: the drum sits on his head
        u = tl.prog("p_jig", t, 0.78, 1.0)
        x = 420
        off = t >= T("p_laugh", 0.5)
        kitty(c, tl, t, "whiskers", x, 660, 0.9, -1, "stand", eyes="closed" if not off else "happy",
              squash=1 - 0.1 * math.sin(min(1, u * 3) * math.pi))
        if not off:
            hx, hy = x - 52 * 0.9, 660 - 86 * 0.9
            c.ellipse(hx, hy - 6, 44, 30, (230, 214, 180), w=3)
            c.ellipse(hx, hy - 6, 34, 22, (40, 30, 30), ol=None)
            for k in range(3):
                a = t * 4 + k * 2.1
                D.zzz  # stars spin round his head
                sx, sy = hx + math.cos(a) * 54, hy - 40 + math.sin(a) * 14
                c.poly([(sx, sy - 9), (sx + 3, sy - 3), (sx + 9, sy - 2), (sx + 4, sy + 3), (sx + 6, sy + 9),
                        (sx, sy + 5), (sx - 6, sy + 9), (sx - 4, sy + 3), (sx - 9, sy - 2), (sx - 3, sy - 3)],
                       (255, 230, 90), w=1.5)
        else:
            c.ellipse(x - 120, 650, 34, 12, (230, 214, 180), w=2.5)
    return c


# =================================================================== road

RW = 4400
ROAD_Y = 640


def road_bg():
    def make():
        c = Canvas(sky(RW, H, DAY_SKY), size=(RW, H))
        for x in range(150, RW, 420):
            D.cloud(c, x, 90 + (x * 7) % 80, 1.0 + 0.3 * ((x // 420) % 2))
        hills_layer(c, RW, 400, seed=7, amp=46)
        P.round_tower(c, 1500, 470, 0.7)
        P.castle_ruin(c, 2700, 470, 0.85)
        P.cottage(c, 3700, 440, 0.6)
        rng = np.random.default_rng(8)
        for _ in range(40):
            P.sheep(c, rng.uniform(0, RW), rng.uniform(470, 560), rng.uniform(0.3, 0.42),
                    int(rng.choice([-1, 1])), t=rng.uniform(0, 9), graze=rng.uniform(0, 1))
        # the road
        c.rect(-10, ROAD_Y - 30, RW + 10, ROAD_Y + 30, (196, 176, 136), ol=None)
        c.line([(-10, ROAD_Y - 30), (RW + 10, ROAD_Y - 30)], (150, 130, 100), 2, cap=False)
        c.rect(-10, ROAD_Y + 30, RW + 10, H, P.GRASS_D, ol=None)
        P.stone_wall(c, [(-10, ROAD_Y - 32), (RW + 10, ROAD_Y - 32)], 1.0, seed=3)
        for x in range(0, RW, 37):
            c.line([(x, H), (x + 6, H - 18 - (x * 13) % 14)], (60, 130, 60), 3)
        return c.img
    return cached("road", make)


def road(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["road"]
    stop0, stop1 = T("r_ends"), T("r_end", 0.4)
    # caravan position: rolls, stops for the clover, rolls on
    keys = [(s0, 500), (stop0, 3000), (stop1, 3000), (s1, 3500)]
    cx = smooth(t, keys, r=0.6)
    v = (smooth(t + 0.05, keys, 0.6) - smooth(t - 0.05, keys, 0.6)) / 0.1
    moving = v > 5
    camx = clamp(cx - 560, 0, RW - W)
    c = world_view(road_bg(), camx, 0)
    s = 0.72
    # pony + caravan
    P.caravan(c, cx, ROAD_Y, s, t, roll=cx / 40)
    P.pony(c, cx + 320 * s, ROAD_Y, 0.85, 1, t, walk=cx / 14 if moving else 0.0)
    rider_y = ROAD_Y - 112 * s
    P.fergal(c, cx + 150 * s, rider_y, 0.62, 1, t, mouth=tl.mouth("fergal", t), sit=True, reins=True,
             eyes="happy" if t >= T("r_norain") else "open")
    roof = ROAD_Y - 255 * s
    wet = clamp(tl.prog("r_rain", t, 0.3, 1.0)) * (1 - tl.prog("r_rainbow", t, 0.2, 1.0))
    look_up = T("r_rainbow", 0.2) <= t < T("r_spot")
    kitty(c, tl, t, "luna", cx - 30, roof, 0.55, 1, "stand" if look_up or t >= T("r_ends") else "sit",
          look=(1, -1) if look_up else (0, 0), wet=wet, eyes="happy" if T("r_rainbow", 0.5) <= t < T("r_ends", 1) else "open")
    # Whiskers on the roof; hops down for the clover and back up
    j0, j1 = T("r_spot"), T("r_end", 0.3)
    if t < j0:
        kitty(c, tl, t, "whiskers", cx + 50, roof, 0.55, 1, "sit", wet=wet,
              eyes="wide" if T("r_puddle") <= t < T("r_norain") else "open")
    elif t < j1:
        u = tl.prog("r_spot", t, 0.0, 0.8)
        gx = cx + 260
        if u < 1:
            x, y = lerp(cx + 50, gx, u), lerp(roof, ROAD_Y + 20, u) + arc_y(u, 60)
            kitty(c, tl, t, "whiskers", x, y, 0.55, 1, "leap")
        else:
            kitty(c, tl, t, "whiskers", gx, ROAD_Y + 20, 0.62, -1 if t < T("r_clover", 0.3) else 1, "sit",
                  eyes="wide" if t < T("r_clover", 0.5) else "happy", look=(0, 1) if t < T("r_clover", 0.3) else (1, 0))
            P.clover(c, gx + 30 * (-1 if t < T("r_clover", 0.3) else 1), ROAD_Y - 30, 1.0)
            sparkles(c, gx + 30 * (-1 if t < T("r_clover", 0.3) else 1), ROAD_Y - 30, t, r=26, n=5, k=0.9)
    else:
        u = tl.prog("r_end", t, 0.3, 0.7)
        if u < 1:
            x, y = lerp(cx + 260, cx + 50, u), lerp(ROAD_Y + 20, roof, u) + arc_y(u, 80)
            kitty(c, tl, t, "whiskers", x, y, 0.55, -1, "leap")
        else:
            kitty(c, tl, t, "whiskers", cx + 50, roof, 0.55, 1, "sit", eyes="happy")
            P.clover(c, cx + 50 + 26, roof - 40, 0.6)
    c.pop()
    # weather: the shower, then the rainbow toward the west
    rk = tl.prog("r_rain", t, 0.0, 0.4) * (1 - tl.prog("r_rainbow", t, 0.0, 0.3))
    if rk > 0:
        c2 = overlay(c, (90, 100, 120), 0.35 * rk)
        c = c2
        P.rain_streaks(c, t, rk, seed=6, n=140)
    bk = tl.prog("r_rainbow", t, 0.15, 0.85)
    if bk > 0:
        fade = 1 - 0.5 * tl.prog("r_end", t)
        P.rainbow(c.img, 820, 520, 470, band=15, alpha=0.6 * fade, reveal=bk)
    shade_bottom(c, tl, t, 0.35)
    return c


# =================================================================== cliffs

EDGE_X = 600
TOP_Y = 520
LEDGE = (470, 652)
PATH = [(470, 652), (520, 640), (560, 610), (548, 580), (590, 556), (630, TOP_Y)]


def cliffs_bg():
    def make():
        c = Canvas(sky(W, H, [(0, (120, 170, 226)), (0.55, (190, 216, 238)), (1, (230, 236, 240))]))
        for x, y, s in ((180, 110, 1.1), (620, 70, 0.9), (1000, 130, 1.2)):
            D.cloud(c, x, y, s)
        # the ocean
        sea = D.gradient(W * SS, (H - 380) * SS, [(0, (90, 150, 190)), (1, (40, 90, 140))])
        c.img.paste(sea, (0, 380 * SS))
        # far cliffs receding along the coast to the left
        for k, (x0, top, base, col) in enumerate(((0, 330, 400, (150, 136, 120)), (120, 300, 440, (136, 120, 106)),
                                                  (260, 250, 500, (120, 104, 92)))):
            x1 = x0 + 260 + 60 * k
            c.poly([(x0, top + 6), (x1 - 40, top), (x1, top + 30), (x1 - 10, base), (x0 - 30, base)], col, w=2)
            c.poly([(x0 - 30, top - 6), (x1 - 40, top - 10), (x1, top + 30), (x0, top + 6)], (110, 170, 90), w=2)
            for j in range(6):
                yy = top + 20 + j * (base - top - 20) / 6
                c.line([(x0 - 20, yy), (x1 - 8, yy - 6)], mix(col, (80, 70, 60), 0.4), 1.5, cap=False)
            for j in range(3):
                c.arc(x0 + 40 + j * 70, base + 4, 30, 6, 200, 340, P.FOAM, 2)
        # O'Brien's Tower on the far headland
        tx, ty = 250, 312
        c.rect(tx - 10, ty - 46, tx + 10, ty, (176, 166, 150), w=1.5)
        for k in range(3):
            c.rect(tx - 10 + k * 8, ty - 52, tx - 6 + k * 8, ty - 46, (176, 166, 150), w=1)
        # the near cliff: grassy top on the right, a sheer striped face falling to the sea
        face = [(EDGE_X, TOP_Y), (EDGE_X - 30, 560), (EDGE_X - 20, 600), (EDGE_X - 60, 640), (LEDGE[0] + 70, 650),
                (LEDGE[0] - 60, 650), (LEDGE[0] - 40, 664), (LEDGE[0] - 70, H + 10), (W + 10, H + 10), (W + 10, TOP_Y)]
        c.poly(face, (128, 108, 94), w=3)
        for j in range(9):
            yy = TOP_Y + 20 + j * 22
            c.line([(EDGE_X - 80, yy), (EDGE_X + 40, yy + 4)], (100, 84, 74), 2, cap=False)
        # the ledge
        c.poly([(LEDGE[0] - 70, 650), (LEDGE[0] + 80, 650), (LEDGE[0] + 70, 666), (LEDGE[0] - 60, 668)],
               (150, 130, 112), w=2.5)
        c.ellipse(LEDGE[0] - 30, 650, 16, 5, (110, 170, 90), ol=None)
        # zig-zag goat path up the face
        c.line(PATH, (160, 140, 120), 8, cap=False)
        # grass on the clifftop
        top = [(EDGE_X - 10, TOP_Y + 4)] + [(EDGE_X + k * 60, TOP_Y - 6 * math.sin(k * 0.9)) for k in range(12)]
        c.poly(top + [(W + 10, TOP_Y + 40), (W + 10, H + 10), (EDGE_X + 120, H + 10), (EDGE_X + 30, TOP_Y + 40)],
               P.GRASS, ol=None)
        c.line(top, (60, 120, 60), 3, cap=False)
        c.rect(EDGE_X + 30, TOP_Y + 40, W + 10, H + 10, P.GRASS, ol=None)
        for k in range(30):
            x = EDGE_X + 40 + (k * 97) % (W - EDGE_X - 40)
            y = TOP_Y + 30 + (k * 53) % 170
            c.line([(x, y), (x + 4, y - 12)], P.GRASS_D, 2.5)
        for k in range(6):
            D.flower(c, 760 + k * 90, 700 - (k % 2) * 20, (250, 250, 250) if k % 2 else (250, 210, 90), 0.6)
        # a few stones on the edge
        for k in range(4):
            c.ellipse(EDGE_X + 30 + k * 26, TOP_Y + 6, 12, 7, (150, 146, 140), w=1.5)
        return c.img
    return cached("cliffs", make)


def cliffs(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["cliffs"]
    c = Canvas(cliffs_bg().copy())
    # sea foam at the foot of the cliff
    for k in range(5):
        u = (t * 0.3 + k / 5) % 1
        c.arc(380 - 60 * k, 712 - 6 * u, 40 + 30 * u, 8, 200, 340, P.FOAM, 3 * (1 - u) + 0.5)
    for k in range(3):
        P.gull(c, 200 + 300 * k + 80 * math.sin(t * 0.4 + k), 220 + 50 * math.sin(t * 0.5 + k * 2), t, 0.8,
               1 if k % 2 else -1, seed=k)
    # the rainbow, ending right on the ledge; it fades once Dot is safe
    fade = 1 - tl.prog("c_fading", t, 0.0, 1.0) * 0.35 - tl.prog("c_gone", t, 0.0, 0.8) * 0.65
    if fade > 0.01:
        P.rainbow(c.img, LEDGE[0] + 430, LEDGE[1], 430, band=14, alpha=0.62 * fade)
        if t < T("c_rescue"):
            sparkles(c, LEDGE[0] + 10, LEDGE[1] - 20, t, r=40, n=6, k=fade)
    # Dot the lamb: on the ledge, then led up the path
    r0, r1 = T("c_rescue", 0.25), T("c_rescue", 0.9)
    path_u = clamp((t - r0) / max(1e-6, r1 - r0))

    def along(u):
        segs = list(zip(PATH, PATH[1:]))
        f = u * len(segs)
        i = min(len(segs) - 1, int(f))
        (xa, ya), (xb, yb) = segs[i]
        return lerp(xa, xb, f - i), lerp(ya, yb, f - i)

    gave = t >= T("c_give", 0.6)
    if t < r0:
        bleat = 0.8 if (T("c_help", 0.9) <= t < T("c_help", 1) or T("c_see", 0.3) <= t < T("c_see", 0.6)) else 0
        P.sheep(c, LEDGE[0] - 10 + 3 * math.sin(t * 8) * (t > T("c_help")), LEDGE[1] - 2, 0.5, 1, t, lamb=True,
                baa=bleat, eyes="wide", seed=1.0)
    elif t < r1:
        dx, dy = along(path_u - 0.12 if path_u > 0.12 else 0)
        P.sheep(c, dx, dy, 0.5, 1, t, lamb=True, walk=t * 6, eyes="wide", seed=1.0)
    else:
        u2 = tl.prog("c_rescue", t, 0.9, 1.0)
        dx = lerp(PATH[-1][0], 760, ease(u2))
        P.sheep(c, dx, TOP_Y, 0.5, 1, t, lamb=True, eyes="happy" if t >= T("c_thanks") else "open",
                clover_on=gave, seed=1.0, walk=t * 6 if u2 < 1 else 0)
    # Bridie: runs in calling for help, then cuddles her lamb
    if t >= T("c_help", 0.0):
        keys = [(T("c_help"), 1400), (T("c_help", 0.7), 1020)]
        if t >= T("c_rescue", 0.9):
            keys = [(T("c_rescue", 0.9), 1020), (T("c_thanks", 0.3), 900)]
        worried = t < T("c_rescue", 0.9)
        actor(c, tl, t, "bridie", keys, TOP_Y + 4, 0.75, face=-1, worried=worried,
              eyes="happy" if T("c_thanks") <= t < T("c_sad") or t >= T("c_pot") else "open",
              look=(-1, 1) if worried else (-1, 0))
    # Luna
    lkeys = [(s0, 1400), (T("c_narr", 0.9), 820)]
    if t >= T("c_rescue"):
        lkeys = [(s0, 1400), (T("c_narr", 0.9), 820), (T("c_rescue"), 820), (T("c_rescue", 0.2), 700)]
    reach = T("c_rescue", 0.6) <= t < T("c_rescue", 0.95)
    actor(c, tl, t, "luna", lkeys, TOP_Y + 4, 0.75, face=-1, pose="crouch" if reach else "stand",
          look=(-1, 0.8) if T("c_help") <= t < T("c_thanks") else (-1, 0),
          eyes="happy" if T("c_luck") <= t else "open")
    # Whiskers
    wkeys = [(s0, 1500), (T("c_narr", 0.95), 940), (T("c_run"), 940), (T("c_run", 1), EDGE_X + 50)]
    if t < T("c_rescue"):
        eyes = "wide" if T("c_help") <= t < T("c_forget") else ("happy" if T("c_come") <= t < T("c_run") else "open")
        look = (-1, 1) if T("c_see") <= t < T("c_forget") else (-1, 0)
        if T("c_think") <= t < T("c_forget"):
            look = (-1, 1) if math.sin((t - T("c_think")) * 5) > 0 else (-1, -1)
        actor(c, tl, t, "whiskers", wkeys, TOP_Y + 4, 0.75, face=-1, eyes=eyes, look=look)
    elif t < r0:
        u = tl.prog("c_rescue", t, 0.0, 0.25)
        # climbs down the path to the ledge
        x, y = along(1 - u)
        D.cat(c, x, y, D.WHISKERS, 0.6, -1, "crouch", t=t, seed=0, eyes="open", look=(-1, 1))
    elif t < r1:
        x, y = along(min(1.0, path_u + 0.06))
        D.cat(c, x, y, D.WHISKERS, 0.6, 1, "walk", walk=t * 9, t=t, seed=0, look=(-1, 0))
    else:
        u2 = tl.prog("c_rescue", t, 0.9, 1.0)
        x = lerp(PATH[-1][0] + 20, 690, ease(u2))
        eyes = "happy" if T("c_thanks") <= t < T("c_gone") or t >= T("c_pot") else "open"
        sad = T("c_gone", 0.4) <= t < T("c_luck", 0.5)
        kitty(c, tl, t, "whiskers", x, TOP_Y + 4, 0.75, 1 if t < T("c_gone", 0.3) or t >= T("c_pot") else -1,
              "sit" if sad else "stand", eyes=eyes, look=(-1, -0.6) if sad else (1, 0),
              head_dy=6 if sad else 0)
        if T("c_give") <= t < T("c_give", 0.6):
            u3 = tl.prog("c_give", t, 0.2, 0.6)
            P.clover(c, lerp(x + 40, 750, u3), lerp(TOP_Y - 70, TOP_Y - 48, u3), 0.7)
        if T("c_thanks") <= t < T("c_gone"):
            hearts(c, 830, TOP_Y - 100, t, 1.0)
    if T("c_rescue", 0.15) <= t < T("c_rescue", 0.8):
        rng = np.random.default_rng(int(t * 4))
        for k in range(3):
            u = (t * 1.6 + k / 3) % 1
            c.circle(520 + 30 * k - 20 * u, 600 + 120 * u * u, 3, (140, 120, 104), ol=None)
    # warm evening light as the rainbow goes
    ek = tl.prog("c_gone", t, 0.0, 1.0)
    if ek > 0:
        c = overlay(c, (255, 190, 120), 0.18 * ek)
    shade_bottom(c, tl, t, 0.4)
    return c


# =================================================================== supper

def cottage_bg():
    def make():
        wall = (240, 236, 222)
        c = Canvas(bg=wall)
        for k in range(12):
            x, y = (k * 211) % W, 60 + (k * 97) % 380
            c.ellipse(x, y, 30, 10, mix(wall, (200, 190, 170), 0.3), ol=None)
        c.rect(0, 0, W, 40, (110, 80, 56), ol=None)
        for x in range(60, W, 220):
            c.rect(x, 0, x + 30, 56, (100, 70, 48), w=2)
        # hearth
        c.rect(120, 150, 560, 520, (176, 168, 156), w=3)
        for k in range(18):
            x = 130 + (k * 61) % 420
            y = 160 + (k * 37) % 340
            c.ellipse(x, y, 18, 10, (160, 152, 140), w=1.5)
        c.rect(190, 260, 490, 520, (60, 44, 40), w=3)
        c.rect(100, 130, 580, 158, (120, 84, 56), w=3)
        c.line([(250, 270), (430, 270)], (40, 40, 44), 5, cap=False)
        c.line([(340, 270), (340, 330)], (40, 40, 44), 4, cap=False)
        for k in range(3):
            c.circle(160 + k * 30, 120, 12, (230, 230, 240), w=2)
        # dresser with blue-and-white plates
        c.rect(860, 120, 1180, 520, (160, 110, 70), w=3)
        for row in range(3):
            c.rect(870, 150 + row * 90, 1170, 160 + row * 90, (130, 86, 54), ol=None)
            for k in range(5):
                px = 900 + k * 60
                c.circle(px, 130 + row * 90, 24, (246, 246, 250), w=2)
                c.circle(px, 130 + row * 90, 15, (70, 110, 200), ol=None)
                c.circle(px, 130 + row * 90, 7, (246, 246, 250), ol=None)
        c.rect(870, 400, 1170, 510, (140, 94, 60), w=2)
        # window with night and stars
        c.rect(620, 150, 800, 300, (30, 40, 90), w=4)
        D.stars(c, 2, 12, 180, 150)
        c.line([(710, 150), (710, 300)], (250, 248, 240), 5, cap=False)
        c.rect(612, 296, 808, 310, (250, 248, 240), w=2)
        # flagstone floor
        c.rect(0, 520, W, H, (150, 140, 128), ol=None)
        for k in range(26):
            x = (k * 163) % W
            y = 530 + (k * 41) % 180
            c.ellipse(x, y, 60, 18, (164, 154, 140), w=1.5)
        # the table in front
        c.rect(560, 560, 1100, 584, (150, 100, 64), w=3, r=4)
        c.rect(590, 584, 610, H, (120, 80, 50), w=2)
        c.rect(1050, 584, 1070, H, (120, 80, 50), w=2)
        return c.img
    return cached("cottage", make)


def supper(tl, t):
    T = tl.t
    c = Canvas(cottage_bg().copy())
    fire(c, 340, 512, t, 1.2)
    P.chowder_pot(c, 340, 410, 0.9, t)
    c.glow(340, 470, 220, 120, (255, 210, 140), (240, 236, 222), steps=6) if False else None
    # bowls and bread on the table
    P.soda_bread(c, 1010, 560, 0.8)
    for bx in (720, 880):
        c.ellipse(bx, 552, 40, 12, (246, 246, 250), w=2.5)
        c.ellipse(bx, 548, 32, 7, (240, 190, 80), ol=None)
        for k in range(2):
            u = (t * 0.4 + k / 2) % 1
            c.circle(bx - 10 + 20 * k + 6 * math.sin(t * 2 + k), 530 - 50 * u, 6 + 6 * u,
                     mix((255, 255, 255), (240, 236, 222), u), ol=None)
    # cats at the table
    eat = T("s_eat") <= t < T("s_eat", 1)
    w_mouth = 0.5 + 0.5 * math.sin(t * 16) if eat and math.sin(t * 2) > 0 else tl.mouth("whiskers", t)
    kitty(c, tl, t, "whiskers", 720, 600, 0.9, -1 if t < T("s_true", 0.7) else 1, "sit", mouth=w_mouth,
          eyes="wide" if t < T("s_true") else "happy" if t < T("s_gave") or t >= T("s_luckier", 0.4) else "open",
          look=(-1, -0.4) if t < T("s_true", 0.7) else (1, 0))
    if T("s_true") <= t < T("s_eat"):
        hearts(c, 720, 440, t)
    kitty(c, tl, t, "luna", 880, 600, 0.85, -1, "sit", eyes="happy" if t >= T("s_luckier", 0.5) else "open",
          look=(-1, 0))
    # Bridie by the fire with Dot asleep, clover in her wool
    P.bridie(c, 1030, 690, 0.8, -1, t, mouth=tl.mouth("bridie", t), sit=True, eyes="happy")
    P.sheep(c, 1150, 700, 0.45, -1, t, lamb=True, eyes="closed", clover_on=True, seed=1.0)
    D.zzz(c, 1130, 640, t)
    # Fergal plays a slow air in the corner
    play = 1.0 if t >= T("s_music") or t < T("s_true") else 0.6
    P.fergal(c, 580, 690, 0.8, 1, t, play=play, eyes="closed" if t >= T("s_music") else "happy")
    if t >= T("s_music"):
        P.notes(c, 620, 480, t, 1.1, col=(120, 90, 60))
    c.tint = None
    return c


# =================================================================== home

def home(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["home"]
    c = Canvas(garden_bg("evening").copy())
    P.rainbow(c.img, 900, 520, 520, band=14, alpha=0.5)
    cx, cy, rx, ry = POND
    pond_ripples(c, t, col=(240, 210, 210))
    sill = t >= T("h_moral")
    if not sill:
        # Pip by the pond, the cats walk in through the garden
        D.mouse(c, 700, 668, 1.1, 1 if t < T("h_open", 0.6) else 1, t, mouth=tl.mouth("pip", t),
                eyes="happy" if t >= T("h_better") else "open",
                hop=abs(math.sin(t * 8)) * 6 if T("h_open", 0.5) <= t < T("h_narr", 0.5) else 0)
        lkeys = [(s0, 1500), (T("h_narr", 0.8), 820)]
        wkeys = [(s0, 1640), (T("h_narr", 0.9), 960)]
        if t >= T("h_float"):
            lkeys = [(s0, 1500), (T("h_narr", 0.8), 820), (T("h_float", 0.0), 820), (T("h_float", 0.4), 1000)]
        lx = actor(c, tl, t, "luna", lkeys, 690, 0.8, face=-1,
                   eyes="happy" if t >= T("h_float", 0.6) else "open")
        wx = actor(c, tl, t, "whiskers", wkeys, 700, 0.82, face=-1,
                   eyes="happy" if T("h_better") <= t < T("h_send") or t >= T("h_float", 0.6) else "open")
        # the bottle with the new map: carried, then set afloat on the stream
        if t < T("h_float", 0.4):
            if t >= T("h_send"):
                P.bottle(c, lx - 40, 660, 0.55, 0)
        else:
            u = tl.prog("h_float", t, 0.4, 1.0)
            pts = [(1060, 640), (1120, 650), (1190, 680), (1260, 712), (1340, 740)]
            f = u * (len(pts) - 1)
            i = min(len(pts) - 2, int(f))
            bx, by = lerp(pts[i][0], pts[i + 1][0], f - i), lerp(pts[i][1], pts[i + 1][1], f - i)
            P.bottle(c, bx, by + 3 * math.sin(t * 3), 0.55, 20 + 8 * math.sin(t * 2))
            sparkles(c, bx, by - 20, t, r=22, n=4, k=1 - u)
        return c
    # the windowsill at sunset: the three friends together, then The End
    kitty(c, tl, t, "luna", 340, SILL_Y, 0.78, -1, "sit", eyes="happy")
    D.mouse(c, 280, SILL_Y, 1.0, 1, t, eyes="happy")
    sleepy = t >= T("h_end", 0.3)
    if sleepy:
        D.cat(c, 200, SILL_Y, D.WHISKERS, 0.75, 1, "sleep", t=t, seed=0)
        D.zzz(c, 240, SILL_Y - 70, t)
    else:
        kitty(c, tl, t, "whiskers", 190, SILL_Y, 0.78, 1, "sit", eyes="happy")
    zk = ease(tl.prog("h_moral", t, 0.0, 1.0))
    w = lerp(1280, 760, zk)
    h = w * H / W
    ccx, ccy = lerp(640, 300, zk), lerp(360, 300, zk)
    x0, y0 = clamp(ccx - w / 2, 0, W - w), clamp(ccy - h / 2, 0, H - h)
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    c = Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))
    the_end(c, tl, t, "h_end", y=640, a=0.3, b=0.6)
    shade_bottom(c, tl, t, 0.35)
    return c


SCENE_FUNCS = {"title": title, "bottle": bottle, "ferry": ferry, "dublin": dublin, "pub": pub, "road": road,
               "cliffs": cliffs, "supper": supper, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["f_wobble", "h_moral"]
