"""London -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync with the speech. Static backgrounds are drawn once and cached; the
balloon flight and the bus ride scroll a wide cached layer under a camera.
"""
import math

import numpy as np
from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.london import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1}
NIGHT = ((30, 36, 90), 0.3)
SUNNY = (255, 222, 90)

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


def rgba(w, h):
    return Canvas(Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)), size=(w, h))


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


def between(tl, t, a, b, fa=0.0, fb=0.0):
    """True while t is between event a (at fraction fa) and event b (at fraction fb)."""
    return tl.t(a, fa) <= t < tl.t(b, fb)


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)


def pip(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("pip", t))
    D.mouse(c, x, y, s, face, t, mouth=mouth, **kw)


def ruby(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("ruby", t))
    P.robin(c, x, y, s, face, t, mouth=mouth, **kw)


def gus(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("gus", t))
    P.gull(c, x, y, s, face, t, mouth=mouth, **kw)


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    x = smooth(t, keys)
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    if who == "pip":
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        kw.pop("hop", None)
        pip(c, tl, t, x, y, s, face, walk=x / 6 if moving else 0.0, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        kitty(c, tl, t, who, x, y, s, face, pose, walk=x / 12 if moving else 0.0, **kw)
    return x


def bubble(c, x, y, rx, ry, k, tail=(0, 0)):
    """White thought bubble scaled by k with puffs trailing toward tail."""
    if k <= 0.02:
        return
    for f, r in ((0.3, 8), (0.6, 13)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, (255, 255, 255), w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.32 * k, (255, 255, 255), w=2)
    c.ellipse(x, y, rx * k, ry * k, (255, 255, 255), ol=None)


def finish(c, tl, t, strength=0.5):
    P.shade_bottom(c, tl, t, strength)
    return c


def blend_over(c, col, a):
    if a <= 0.003:
        return c
    return Canvas(Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, a)))


def zoom(c, cx, cy, z):
    """Zoom the finished frame by z (>= 1) around (cx, cy), clamped to the frame."""
    if z <= 1.001:
        return c
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, W - w)
    y0 = clamp(cy - h / 2, 0, H - h)
    box = tuple(int(round(v * SS)) for v in (x0, y0, x0 + w, y0 + h))
    return Canvas(c.img.resize((W * SS, H * SS), Image.BILINEAR, box=box))


def soft_glow(c, x, y, r, col, alpha):
    """Blurred round glow pasted onto a canvas (for suns, lamps)."""
    from PIL import ImageDraw, ImageFilter
    m = Image.new("L", c.img.size, 0)
    ImageDraw.Draw(m).ellipse([(x - r * 0.6) * SS, (y - r * 0.6) * SS, (x + r * 0.6) * SS, (y + r * 0.6) * SS],
                              fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(r * 0.35 * SS))
    c.img.paste(Image.new("RGB", c.img.size, col), (0, 0), m)


def sky_img(stops, w=W, h=H):
    return D.gradient(w * SS, h * SS, stops)


def water_band(c, x0, x1, y0, y1, col, hi, rng, n=60):
    c.rect(x0, y0, x1, y1, col, ol=None)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0 + 4, y1 - 2)
        ww = rng.uniform(14, 50) * (0.5 + (y - y0) / max(1, y1 - y0))
        c.line([(x - ww / 2, y), (x + ww / 2, y)], hi, 2, cap=False)


def skyline(c, rng, x0, x1, base, hmin, hmax, col, win=None, p=0.25):
    x = x0
    while x < x1:
        w = rng.uniform(40, 100)
        h = rng.uniform(hmin, hmax)
        c.rect(x, base - h, x + w + 1, base + 2, col, ol=None)
        if rng.random() < 0.4:
            c.rect(x + w * 0.3, base - h - 16, x + w * 0.3 + 7, base - h, col, ol=None)
        if win:
            for wy in np.arange(base - h + 10, base - 6, 13):
                for wx in np.arange(x + 6, x + w - 6, 11):
                    if rng.random() < p:
                        c.rect(wx, wy, wx + 4, wy + 6, win, ol=None)
        x += w


# ======================================================================= title

def title_bg():
    def make():
        c = Canvas(sky_img([(0, (50, 58, 124)), (0.3, (120, 104, 170)), (0.55, (240, 160, 150)),
                            (0.66, (255, 206, 140)), (1, (255, 206, 140))]))
        D.stars(c, 4, 40, W, 160, col=(255, 240, 220))
        soft_glow(c, 1060, 452, 220, (255, 226, 170), 0.7)
        c.circle(1060, 452, 46, (255, 236, 170), ol=None)
        rng = np.random.default_rng(6)
        skyline(c, rng, -20, W + 20, 478, 20, 70, (150, 110, 150), win=(255, 220, 150), p=0.12)
        c.tint = ((90, 60, 130), 0.25)
        P.st_pauls(c, 600, 478, 0.55, col=(170, 130, 160), shade=(150, 110, 145), dome=(150, 120, 160), ol=None)
        P.tower_bridge(c, 1160, 452, 0.3, stone=(190, 150, 170), shade=(160, 120, 150), roof=(110, 90, 130),
                       blue=(130, 140, 190), w=1.2)
        P.london_eye(c, 975, 296, 160, rim=(250, 236, 236), cap=(255, 236, 200), legs=True)
        P.parliament(c, 270, 640, 520, 64, stone=(214, 176, 150), shade=(178, 140, 130), roof=(90, 80, 110),
                     win=(255, 214, 140))
        P.big_ben(c, 220, 520, 470, 3, 58, stone=(222, 184, 150), shade=(184, 146, 132), roof=(90, 80, 110), lit=0.6)
        c.tint = None
        rng = np.random.default_rng(3)
        water_band(c, 0, W, 520, 620, (90, 86, 150), (250, 196, 150), rng, n=90)
        for k in range(40):                      # sun's glitter path on the river
            y = rng.uniform(524, 615)
            x = 1060 + rng.normal(0, 30 + (y - 520) * 0.6)
            ww = rng.uniform(10, 40)
            c.line([(x - ww / 2, y), (x + ww / 2, y)], (255, 224, 170), 3, cap=False)
        # embankment wall the cats sit on
        stone = (176, 150, 140)
        c.rect(-10, 620, W + 10, H + 10, stone, w=2.5)
        for y in (650, 685):
            c.line([(0, y), (W, y)], mix(stone, (0, 0, 0), 0.15), 2, cap=False)
        for x in range(0, W, 80):
            c.line([(x + (40 if (x // 80) % 2 else 0), 620), (x + (40 if (x // 80) % 2 else 0), 650)],
                   mix(stone, (0, 0, 0), 0.15), 2, cap=False)
        c.rect(-10, 608, W + 10, 624, mix(stone, (255, 255, 255), 0.2), w=2.5, r=3)
        P.lamp_post(c, 90, 616, 1.0, lit=1.0)
        P.lamp_post(c, 1200, 616, 1.0, lit=1.0)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    T = tl.t
    c = Canvas(title_bg().copy())
    c.tint = ((90, 60, 130), 0.18)
    kitty(c, tl, t, "luna", 520, 612, 0.85, 1, "sit", look=(-1, -1), mouth=0, tail=math.sin(t * 1.5))
    D.mouse(c, 598, 612, 1.0, -1, t)
    kitty(c, tl, t, "whiskers", 680, 612, 0.9, -1, "sit", look=(1, -1), mouth=0)
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(590, 112 - 30 * (1 - k), "Whiskers and the", 44, mix((60, 60, 130), (255, 236, 200), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(590, 196, "STROKE OF FOUR", 24 + 50 * k2, mix((60, 60, 130), (255, 214, 120), k2), stroke=5 * k2)
    return c


# ======================================================================= radio

WIN = (764, 114, 1076, 366)      # inner glass of the room window
SILL_Y = 372


def window_mask():
    def make():
        from PIL import ImageDraw
        m = Image.new("L", (W * SS, H * SS), 0)
        ImageDraw.Draw(m).rectangle([WIN[0] * SS, WIN[1] * SS, WIN[2] * SS, WIN[3] * SS], fill=255)
        return m
    return cached("winmask", make)


def outside_bg(night):
    def make():
        if night:
            c = Canvas(sky_img([(0, (14, 18, 48)), (0.5, (40, 44, 96)), (1, (60, 62, 120))]))
            D.stars(c, 8, 80, W, 360)
            D.moon(c, 1010, 180, 26, sky=(40, 44, 96))
            roof = (40, 40, 70)
        else:
            c = Canvas(sky_img([(0, (150, 166, 190)), (0.5, (196, 206, 220)), (1, (210, 216, 226))]))
            for x, y, s in ((820, 160, 0.8), (1000, 200, 0.9), (900, 260, 0.6)):
                D.cloud(c, x, y, s, col=(236, 238, 244))
            roof = (150, 110, 100)
        # neighbours' roofs and chimneys at the bottom of the window
        c.poly([(740, 366), (800, 318), (900, 318), (960, 366)], roof, ol=None)
        c.rect(820, 296, 838, 330, roof, ol=None)
        c.poly([(960, 366), (1010, 330), (1100, 330), (1100, 366)], mix(roof, (0, 0, 0), 0.15), ol=None)
        return c.img
    return cached(("outside", night), make)


def room_bg(night=False):
    def make():
        c = Canvas(MF.room(night).copy())
        P.side_table(c, 330, 600, 1.0)
        return c.img
    return cached(("room", night), make)


def window_frame(c, night=False):
    bar = (240, 240, 240) if not night else (150, 150, 180)
    c.rect(756, 106, 1084, 374, None, w=8)
    c.line([(920, 110), (920, 370)], bar, 6, cap=False)
    c.line([(760, 240), (1080, 240)], bar, 6, cap=False)


def draw_outside(c, fn, night=False):
    """Draw fn(oc) onto the sky outside and show it through the window glass."""
    oc = Canvas(outside_bg(night).copy())
    fn(oc)
    c.img.paste(oc.img, (0, 0), window_mask())
    window_frame(c, night)


def radio(tl, t):
    T = tl.t
    c = Canvas(room_bg().copy())
    glow = clamp((t - T("r_narr", 0.5)) / 0.6) * (1 - clamp((t - T("r_luna")) / 1.0))
    P.radio(c, 330, 500, 0.95, glow=glow, t=t)

    # ---- outside: the balloon comes down, the cats get in, it rises
    by = smooth(t, [(T("r_balloon"), -160), (T("r_balloon", 0.85), 352), (T("r_jump", 0.75), 352),
                    (T("r_jump", 1.0), 120)], r=0.3)
    sway = math.sin(t * 1.1) * 0.6
    bx = 852 + 6 * math.sin(t * 0.7)
    flame = 1.0 if (T("r_balloon") < t < T("r_balloon", 0.35) or t > T("r_jump", 0.8)) else 0.0

    def outside(oc):
        if t < T("r_balloon"):
            return
        P.balloon(oc, bx, by, 0.75, t, part="back", flame=flame, sway=sway)
        rim = by - 0.75 * 70
        if t >= T("r_jump", 0.42):
            kitty(oc, tl, t, "luna", bx - 30, by - 18, 0.42, 1, "sit", eyes="happy", look=(1, -1))
        if t >= T("r_jump", 0.66):
            kitty(oc, tl, t, "whiskers", bx + 28, by - 18, 0.42, -1, "sit", eyes="wide", mouth=0.3)
        if t < T("r_ruby", 0.1) or t >= T("r_jump", 0.25):
            ruby(oc, tl, t, bx - 62, rim, 0.75, 1)
        P.balloon(oc, bx, by, 0.75, t, part="front")
        if t >= T("r_jump", 0.82):
            P.mail_sack(oc, bx + 70, by + 4, 0.6, wiggle=math.sin(t * 9))
    draw_outside(c, outside)

    # ---- Ruby on the windowsill
    if T("r_ruby", 0.1) <= t < T("r_jump", 0.25):
        hop = abs(math.sin(t * 7)) * 6 if tl.talking("ruby", t) else 0
        ruby(c, tl, t, 1048, SILL_Y, 1.15, -1, hop=hop, wave=1.0 if between(tl, t, "r_hop", "r_jump") else 0)

    # ---- Whiskers on the sill
    if t < T("r_cakes"):
        kitty(c, tl, t, "whiskers", 960, SILL_Y, 0.8, 1, "sleep")
        D.zzz(c, 1010, 300, t)
    elif t < T("r_jump", 0.45):
        startle = clamp((t - T("r_cakes")) / 0.3)
        eyes = "happy" if t < T("r_cakes", 1) + 0.2 else "open"
        if T("r_balloon") <= t < T("r_ruby"):
            eyes = "wide"
        face = -1
        if T("r_ruby", 0.1) <= t:
            face = 1
        kitty(c, tl, t, "whiskers", 950, SILL_Y, 0.8, face, "sit", eyes=eyes, head_dy=-10 * (1 - startle),
              look=(1, 0.5) if face < 0 else (1, 0))
    elif t < T("r_jump", 0.66):
        u = tl.prog("r_jump", t, 0.45, 0.66)
        D.cat(c, lerp(950, bx + 28, u), lerp(SILL_Y, by - 18, u) + arc_y(u, 90), D.WHISKERS, lerp(0.8, 0.45, u),
              1, "leap", t=t, eyes="wide", mouth=0.4)

    # ---- Luna
    if t < T("r_jump", 0.05):
        lx = smooth(t, [(T("r_cakes"), 470), (T("r_balloon", 0.2), 470), (T("r_balloon", 0.8), 700)])
        face = -1 if t < T("r_luna") else 1
        pose = "sit" if t < T("r_balloon", 0.2) else "stand"
        if abs(smooth(t + 0.05, [(T("r_balloon", 0.2), 470), (T("r_balloon", 0.8), 700)]) - lx) > 1:
            pose = "walk"
        eyes = "happy" if between(tl, t, "r_luna", "r_cakes", 0.3) else "open"
        if T("r_balloon", 0.6) <= t < T("r_ruby", 0.2):
            eyes = "wide"
        look = (1, -1) if t >= T("r_balloon", 0.5) else ((1, -0.5) if face < 0 else (1, 0))
        kitty(c, tl, t, "luna", lx, 612, 1.0, face, pose, walk=lx / 12, eyes=eyes, look=look)
    elif t < T("r_jump", 0.24):
        u = tl.prog("r_jump", t, 0.05, 0.24)
        D.cat(c, lerp(700, 860, u), lerp(612, SILL_Y, u) + arc_y(u, 120), D.LUNA, 0.9, 1, "leap", t=t, seed=1.3)
    elif t < T("r_jump", 0.3):
        kitty(c, tl, t, "luna", 860, SILL_Y, 0.85, 1, "crouch", mouth=0)
    elif t < T("r_jump", 0.42):
        u = tl.prog("r_jump", t, 0.3, 0.42)
        D.cat(c, lerp(860, bx - 30, u), lerp(SILL_Y, by - 18, u) + arc_y(u, 80), D.LUNA, lerp(0.85, 0.45, u), 1,
              "leap", t=t, seed=1.3)

    # ---- Pip sneaks along the floor and up to the window
    if T("r_jump", 0.55) <= t < T("r_jump", 0.8):
        u = tl.prog("r_jump", t, 0.55, 0.72)
        px = lerp(-40, 860, u)
        if u < 1:
            D.mouse(c, px, 616, 1.0, 1, t, walk=px / 6, hop=abs(math.sin(px / 9)) * 5)
        else:
            v = tl.prog("r_jump", t, 0.72, 0.8)
            D.mouse(c, lerp(860, 1000, v), lerp(616, 340, v) + arc_y(v, 60), 0.9, 1, t, eyes="wide")

    # ---- thought bubbles: Big Ben for Luna, cakes for Whiskers
    k = ease(tl.prog("r_luna", t, 0.1, 0.3)) * (1 - ease(tl.prog("r_cakes", t, 0.0, 0.2)))
    if k > 0.02:
        bubble(c, 560, 300, 110, 120, k, tail=(500, 470))
        P.big_ben(c, 560, 300 + 105 * k, 210 * k, 3, 58, w=1.5)
    k = ease(tl.prog("r_cakes", t, 0.2, 0.5)) * (1 - ease(tl.prog("r_sea", t, 0.0, 0.25)))
    if k > 0.02:
        bubble(c, 820, 210, 100, 80, k, tail=(920, 290))
        P.cake_stand(c, 820, 210 + 60 * k, 0.9 * k)
    return finish(c, tl, t, 0.25)


# ===================================================================== balloon

WW = 4600            # width of the flight panorama
CAM_END = WW - W
HZ = 470             # horizon


def flight_sky(grey):
    def make():
        if grey:
            return sky_img([(0, (120, 130, 150)), (0.6, (176, 184, 198)), (1, (190, 196, 206))])
        return sky_img([(0, (96, 168, 236)), (0.6, (186, 222, 250)), (1, (214, 236, 252))])
    return cached(("fsky", grey), make)


def field_patch(c, x0, x1, rng, cols):
    """Patchwork fields between x0 and x1 below the horizon, in perspective rows."""
    rows = [(HZ + 10, HZ + 40), (HZ + 40, HZ + 90), (HZ + 90, HZ + 160), (HZ + 160, H + 10)]
    for y0, y1 in rows:
        x = x0
        while x < x1:
            w = rng.uniform(90, 200) * (0.6 + (y0 - HZ) / 150)
            w = min(w, x1 - x)
            c.rect(x, y0, x + w, y1, cols[rng.integers(len(cols))], ol=None)
            c.line([(x, y0), (x, y1)], (70, 120, 60), 3, cap=False)
            x += w
        c.line([(x0, y0), (x1, y0)], (70, 120, 60), 3, cap=False)


def flight_world():
    def make():
        c = rgba(WW, H)
        rng = np.random.default_rng(12)
        greens = [(140, 196, 110), (166, 210, 120), (120, 180, 96), (200, 210, 120), (176, 200, 100)]
        # ---- home countryside
        c.poly([(0, HZ + 12)] + [(x, HZ - 18 + 14 * math.sin(x / 140)) for x in range(0, 1240, 40)] +
               [(1240, HZ + 12)], (120, 170, 130), ol=None)
        field_patch(c, 0, 1200, rng, greens)
        for x in (180, 420, 760, 1010):
            D.tree(c, x, HZ + 70, 0.32, leaf=(80, 150, 80))
        for k, x in enumerate((300, 340, 380, 880, 920)):
            c.rect(x, HZ + 26, x + 30, HZ + 50, (240, 226, 200), w=1.5)
            c.poly([(x - 4, HZ + 26), (x + 15, HZ + 12), (x + 34, HZ + 26)], (200, 90, 70), w=1.5)
        c.rect(600, HZ + 6, 612, HZ + 50, (230, 220, 200), w=1.5)
        c.poly([(598, HZ + 6), (606, HZ - 18), (614, HZ + 6)], (110, 110, 130), w=1.5)
        # ---- beach and sea
        c.poly([(1180, HZ + 10), (1300, HZ + 10), (1240, H + 10), (1150, H + 10)], (240, 220, 160), ol=None)
        c.rect(1260, HZ, 2980, H + 10, (70, 140, 200), ol=None)
        for _ in range(260):
            x, y = rng.uniform(1300, 2960), rng.uniform(HZ + 6, H)
            ww = rng.uniform(12, 40) * (0.4 + (y - HZ) / 200)
            c.line([(x - ww / 2, y), (x + ww / 2, y)], (150, 200, 235), 2, cap=False)
        # a sailing boat and a ferry
        c.poly([(1700, 560), (1780, 560), (1768, 576), (1712, 576)], (250, 250, 250), w=2)
        c.poly([(1740, 556), (1740, 500), (1700, 556)], (255, 255, 255), w=2)
        c.poly([(2300, 520), (2440, 520), (2420, 540), (2316, 540)], (240, 240, 240), w=2)
        c.rect(2330, 504, 2410, 520, (250, 250, 250), w=2)
        c.rect(2380, 490, 2394, 504, (214, 40, 46), w=1.5)
        # ---- the white cliffs of Dover with a lighthouse
        cliff = [(2980, H + 10), (2980, 560)]
        for x in range(2980, 3200, 20):
            cliff.append((x + 10, 500 + rng.uniform(-6, 6)))
        cliff += [(3200, 500), (3200, H + 10)]
        c.rect(2960, HZ - 4, WW, H + 10, (140, 196, 110), ol=None)
        c.poly([(2960, H + 10), (2960, HZ + 8), (3000, HZ + 2), (3200, HZ + 2)], (70, 140, 200), ol=None)
        c.poly([(2960, H + 10), (3005, 520), (3040, 530), (3080, 515), (3130, 525), (3200, 512), (3200, H + 10)],
               (250, 248, 240), w=2.5)
        for x in range(3010, 3200, 26):
            c.line([(x, 530), (x - 8, H)], (220, 220, 214), 3, cap=False)
        c.poly([(2960, H + 10), (2990, 600), (3200, 640), (3200, H + 10)], (70, 140, 200), ol=None)
        c.rect(3100, 440, 3116, 500, (250, 250, 250), w=2)
        for y in (450, 470, 490):
            c.rect(3100, y, 3116, y + 6, (214, 40, 46), ol=None)
        c.rect(3096, 432, 3120, 442, (40, 40, 50), w=1.5)
        # ---- England, then London
        field_patch(c, 3200, 3500, rng, greens)
        rng2 = np.random.default_rng(21)
        skyline(c, rng2, 3420, WW, 530, 24, 60, (176, 168, 176), win=(120, 130, 150), p=0.2)
        ox = CAM_END
        P.st_pauls(c, ox + 780, 530, 0.5)
        P.london_eye(c, ox + 950, 450, 80, rim=(250, 250, 252), legs=True)
        P.parliament(c, ox + 1010, ox + 1230, 530, 34)
        P.big_ben(c, ox + 1150, 530, 230, 3, 0, w=1.5)
        # the Thames
        pts_top = [(x, 548 + 16 * math.sin((x - 3420) / 160)) for x in range(3420, WW + 20, 20)]
        pts_bot = [(x, y + 34) for x, y in pts_top[::-1]]
        c.poly(pts_top + pts_bot, (90, 120, 150), w=2)
        P.tower_bridge(c, ox + 560, 556, 0.32, w=1.2)
        c.rect(3420, 600, WW, H + 10, (196, 186, 180), ol=None)
        skyline(c, rng2, 3420, WW, 720, 40, 110, (200, 160, 140), win=(90, 110, 140), p=0.4)
        return c.img
    return cached("fworld", make)


def flight_clouds(c, cam, t, grey):
    rng = np.random.default_rng(31)
    col = mix((255, 255, 255), (210, 214, 224), grey)
    for k in range(9):
        wx = rng.uniform(0, WW + 600)
        y = rng.uniform(70, 330)
        s = rng.uniform(0.6, 1.3)
        par = 0.35 + 0.1 * k / 9
        x = (wx - cam * par + t * 6) % (WW * 0.5 + 400) - 200
        D.cloud(c, x, y, s, col=col)


def balloon_rig(c, tl, t, bx, by, s, rainy=0.0, flame=0.0):
    """The balloon with everyone aboard."""
    T = tl.t
    P.balloon(c, bx, by, s, t, part="back", flame=flame, sway=math.sin(t * 0.9) * 0.5)
    rim = by - 70 * s
    cs = 0.58 * s
    # Luna
    leyes = "open"
    if between(tl, t, "b_narr", "b_shut"):
        leyes = "happy"
    if between(tl, t, "b_pip", "b_london", 0.2):
        leyes = "wide" if t < T("b_luna") else "happy"
    llook = (1, 1) if t < T("b_shut") else ((1, 0) if t < T("b_london") else (1, -0.3))
    lface = 1
    kitty(c, tl, t, "luna", bx - 36 * s, by - 30 * s, cs, lface, "sit", eyes=leyes, look=llook, wet=rainy)
    # Whiskers: eyes squeezed shut most of the flight
    weyes = "closed" if T("b_narr", 0.3) <= t < T("b_london", 0.4) else "open"
    if t >= T("b_ruby", 0.8):
        weyes = "wide"
    wface = -1 if t < T("b_london", 0.3) else 1
    kitty(c, tl, t, "whiskers", bx + 34 * s, by - 30 * s, cs, wface, "sit", eyes=weyes, wet=rainy,
          head_dy=6 if weyes == "closed" else 0)
    # Ruby on the rim
    ruby(c, tl, t, bx - 78 * s, rim, 0.85 * s, 1, wave=1.0 if between(tl, t, "b_ruby", "b_meet", 0, 0.5) else 0.0)
    P.balloon(c, bx, by, s, t, part="front")
    # mail sack hanging on the side, Pip pops out
    wig = math.sin(t * 14) if between(tl, t, "b_sack", "b_pip", 0.1) else 0.0
    sx, sy = bx + 102 * s, by - 2 * s
    c.line([(bx + 80 * s, rim), (sx, sy - 52 * s)], (120, 90, 60), 2)
    if t >= T("b_pip"):
        k = ease(tl.prog("b_pip", t, 0.0, 0.15))
        pip(c, tl, t, sx + 2 * s, sy - (40 + 20 * k) * s, 0.9 * s, -1, proud=between(tl, t, "b_pip", "b_luna"))
    P.mail_sack(c, sx, sy, 0.9 * s, wiggle=wig)


def balloon(tl, t):
    T = tl.t
    cam = smooth(t, [(T("b_narr"), 0), (T("b_sail", 1), 2200), (T("b_luna", 1), 3000), (T("b_london", 0.9), CAM_END)],
                 r=0.5)
    grey = clamp((cam - 2500) / 800)
    sky = flight_sky(False) if grey <= 0 else Image.blend(flight_sky(False), flight_sky(True), grey)
    c = Canvas(sky.copy())
    flight_clouds(c, cam, t, grey)
    paste_layer(c, flight_world(), cam, 0)
    # a few gulls over the sea
    if 1100 < cam < 3200:
        for k in range(3):
            gx = (1700 + k * 420 - cam * 0.9 + t * 40 * (k + 1)) % 1600 - 160
            P.gull(c, gx, 260 + 40 * k + 10 * math.sin(t * 2 + k), 0.35, 1, t + k, fly=1)
    bob = 8 * math.sin(t * 1.3)
    bx = smooth(t, [(T("b_luna", 1), 600), (T("b_london", 0.6), 330), (T("b_land"), 330), (T("b_land", 1), 1000)])
    by = smooth(t, [(T("b_land"), 650), (T("b_land", 1), 540)]) + bob
    s = smooth(t, [(T("b_land"), 1.22), (T("b_land", 1), 0.3)])
    rainy = clamp((t - T("b_ruby", 0.8)) / 2.0)
    flame = 1.0 if (T("b_narr") <= t < T("b_narr", 0.3) or T("b_london", 0.3) <= t < T("b_london", 0.6)
                    or T("b_land") <= t < T("b_land", 0.2)) else 0.0
    balloon_rig(c, tl, t, bx, by, s, rainy, flame)
    if rainy > 0:
        c = blend_over(c, (110, 120, 140), 0.15 * rainy)
        P.rain(c, t, n=int(150 * rainy), col=(220, 228, 240))
    return finish(c, tl, t, 0.35)


# ======================================================================= guard

PAVE = 610
BOX_X, BOX_S = 300, 1.8
SENTRY_X = 900


def palace(c, x0, x1, base, h):
    stone, shade = (226, 220, 206), (196, 188, 172)
    c.rect(x0, base - h, x1, base, stone, w=2.5)
    c.rect(x0, base - h, x1, base - h + 16, shade, w=2)
    cx = (x0 + x1) / 2
    for x in np.arange(x0 + 20, x1 - 20, 40):
        for y in (base - h + 34, base - h + 100):
            c.rect(x, y, x + 18, y + 40, (90, 100, 116), w=1.5)
            c.rect(x - 3, y - 6, x + 21, y, shade, ol=None)
    # central portico with columns and a pediment
    c.rect(cx - 150, base - h - 10, cx + 150, base, stone, w=2.5)
    for k in range(7):
        xx = cx - 130 + k * 43
        c.rect(xx, base - h + 30, xx + 14, base - 20, (240, 236, 226), w=1.5)
    c.poly([(cx - 160, base - h - 10), (cx, base - h - 64), (cx + 160, base - h - 10)], stone, w=2.5)
    c.circle(cx, base - h - 32, 12, P.GOLD, w=1.5)
    c.line([(cx, base - h - 64), (cx, base - h - 130)], (60, 60, 70), 3)
    c.poly([(cx, base - h - 130), (cx + 54, base - h - 120), (cx, base - h - 104)], (200, 40, 50), w=1.5)
    c.rect(cx - 2, base - h - 128, cx + 26, base - h - 117, (250, 210, 70), ol=None)


def guard_bg():
    def make():
        c = Canvas(sky_img([(0, (120, 128, 148)), (0.6, (170, 176, 190)), (1, (186, 190, 200))]))
        for x, y, s in ((200, 100, 1.4), (620, 70, 1.6), (1050, 110, 1.3)):
            D.cloud(c, x, y, s, col=(150, 156, 172))
        palace(c, -40, W + 40, 470, 230)
        c.rect(-10, 470, W + 10, 530, (196, 190, 176), ol=None)          # forecourt
        for x in (150, 640, 1130):
            c.rect(x - 22, 380, x + 22, 530, (214, 208, 194), w=2)
            c.circle(x, 372, 16, P.GOLD, w=2)
        P.railings(c, -10, W + 10, 530, h=110)
        # wet pavement
        c.rect(-10, 530, W + 10, H + 10, (126, 130, 140), ol=None)
        for y in range(560, H, 40):
            c.line([(0, y), (W, y)], (112, 116, 126), 2, cap=False)
        rng = np.random.default_rng(8)
        for k in range(26):
            x, y = rng.uniform(0, W), rng.uniform(548, H)
            c.line([(x, y), (x + rng.uniform(20, 60), y)], (160, 166, 180), 2, cap=False)
        for x, y, rx in ((520, 660, 70), (1040, 690, 90), (140, 700, 60)):
            c.ellipse(x, y, rx, rx * 0.18, (150, 160, 180), ol=(110, 116, 128), w=1.5)
            c.ellipse(x - rx * 0.3, y - 2, rx * 0.3, 3, (200, 210, 226), ol=None)
        # reflections of the box and the sentry box in the wet stones
        c.rect(BOX_X - 50, 600, BOX_X + 50, 650, (150, 110, 120), ol=None)
        c.rect(SENTRY_X - 56, 600, SENTRY_X + 56, 640, (150, 150, 160), ol=None)
        P.sentry_box(c, SENTRY_X, 600, 1.0)
        P.lamp_post(c, 1170, 600, 1.15, lit=0.3)
        return c.img
    return cached("guard_bg", make)


def guard(tl, t):
    T = tl.t
    c = Canvas(guard_bg().copy())
    s0 = tl.scenes["guard"][0]

    # ---- Biscuit
    march = 0.0
    if between(tl, t, "g_guard", "g_ask"):
        march = (tl.prog("g_guard", t) * 2.0) % 1.0
    hat = 0.0
    if T("g_sneeze", 0.25) <= t < T("g_sneeze", 0.6):
        u = tl.prog("g_sneeze", t, 0.25, 0.6)
        hat = 140 * math.sin(math.pi * u)
    beyes = "open"
    blook = (0.0, 0.0)
    if between(tl, t, "g_boo", "g_rule"):
        blook = (1.0, 0.3)                       # eyes slide toward the silly cat
    if between(tl, t, "g_tip", "g_hero"):
        blook = (-1.0, 0.0)                      # "that way" -- with the eyes only
    if T("g_sneeze", 0.15) <= t < T("g_sneeze", 0.32):
        beyes = "squeeze"
    if T("g_sneeze", 0.6) <= t:
        beyes = "happy"
    bmouth = 0.35 * tl.mouth("biscuit", t)
    if T("g_sneeze", 0.24) <= t < T("g_sneeze", 0.34):
        bmouth = 1.0
    nose = 1.0 if T("g_sneeze") <= t < T("g_sneeze", 0.25) else 0.0
    P.corgi_guard(c, SENTRY_X, PAVE, 1.0, -1, t, mouth=bmouth, eyes=beyes, look=blook, march=march, hat_dy=hat,
                  nose=nose)
    # a raindrop lands on his nose
    if T("g_sneeze") <= t < T("g_sneeze", 0.2):
        u = tl.prog("g_sneeze", t, 0.0, 0.15)
        c.ellipse(SENTRY_X - 40, lerp(300, PAVE - 154, u), 4, 6, (170, 210, 255), w=1.5)

    # ---- the phone box (back), cats inside, then the front frame
    shake = math.sin(t * 60) * 3 if T("g_box", 0.55) <= t < T("g_box", 0.7) else 0.0
    P.phone_box(c, BOX_X + shake, PAVE, BOX_S, part="back")
    inside = T("g_box", 0.3) <= t < T("g_box", 0.6)
    if inside:
        ring = t >= T("g_box", 0.55)
        kitty(c, tl, t, "luna", BOX_X - 22 + shake, PAVE - 28, 0.6, 1, "sit", eyes="wide" if ring else "happy",
              wet=1.0)
        kitty(c, tl, t, "whiskers", BOX_X + 20 + shake, PAVE - 28, 0.62, -1, "sit",
              eyes="wide" if ring else "happy", wet=1.0)
        D.mouse(c, BOX_X + 2 + shake, PAVE - 28, 0.8, 1, t, eyes="wide" if ring else "happy")
    P.phone_box(c, BOX_X + shake, PAVE, BOX_S, part="front")
    if T("g_box", 0.55) <= t < T("g_box", 0.75):
        for k in range(3):
            u = (t * 3 + k / 3) % 1.0
            c.arc(BOX_X, PAVE - 400, 30 + 50 * u, 20 + 30 * u, 200, 340, (255, 255, 255), 3)
        c.text(BOX_X + 90, PAVE - 400, "BRRING!", 24, (255, 240, 120), stroke=3)

    # ---- the cats (outside the box)
    wet = 1.0
    ring_out = tl.prog("g_box", t, 0.6, 0.85)
    run_off = tl.prog("g_sneeze", t, 0.55, 1.0)

    # Luna
    if not inside:
        if t < T("g_box", 0.3):
            lk = [(s0, -150), (T("g_narr", 0.9), 480), (T("g_box"), 480), (T("g_box", 0.3), BOX_X - 18)]
            actor(c, tl, t, "luna", lk, PAVE, 0.9, 1, wet=wet, look=(1, -0.5))
        elif t < T("g_box", 0.85):
            u = ring_out
            D.cat(c, lerp(BOX_X - 10, 560, u), PAVE + arc_y(u, 120), D.LUNA, 0.9, 1, "leap", t=t, wet=wet, seed=1.3,
                  eyes="wide")
        else:
            lx = lerp(560, 1500, ease(run_off))
            pose = "walk" if 0 < run_off < 1 else "stand"
            eyes = "happy" if between(tl, t, "g_sneeze", "g_sneeze", 0.35, 0.6) else "open"
            look = (1, -1) if between(tl, t, "g_guard", "g_still", 0, 1) else (1, -0.4)
            kitty(c, tl, t, "luna", lx, PAVE, 0.9, 1, pose, walk=lx / 12, wet=wet, eyes=eyes, look=look)
    # Pip
    if not inside:
        if t < T("g_box", 0.3):
            pk = [(s0, -240), (T("g_narr", 0.9), 400), (T("g_box"), 400), (T("g_box", 0.3), BOX_X)]
            actor(c, tl, t, "pip", pk, PAVE, 1.0, 1)
        else:
            px = lerp(BOX_X, 420, ease(ring_out)) if t < T("g_box", 0.85) else lerp(420, 1450, ease(run_off))
            hop = arc_y(ring_out, 50) * -1 if t < T("g_box", 0.85) else abs(math.sin(px / 9)) * 5 * (0 < run_off < 1)
            pip(c, tl, t, px, PAVE, 1.0, 1, hop=hop, walk=px / 6 if 0 < run_off < 1 else 0,
                eyes="happy" if between(tl, t, "g_sneeze", "g_sneeze", 0.35, 0.6) else "open")
    # Whiskers
    if not inside:
        if t < T("g_box", 0.3):
            wk = [(s0 + 0.6, -60), (T("g_narr", 0.95), 640), (T("g_box"), 640), (T("g_box", 0.3), BOX_X + 16)]
            shakeoff = between(tl, t, "g_fur", "g_box", 0.1, 0)
            sq = 1.0 + (0.06 * math.sin(t * 40) if shakeoff else 0.0)
            actor(c, tl, t, "whiskers", wk, PAVE, 0.95, 1, wet=wet, squash=sq,
                  eyes="closed" if shakeoff else "open", look=(1, -0.5))
            if shakeoff:
                rng = np.random.default_rng(int(t * 12))
                for _ in range(10):
                    a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
                    d = rng.uniform(60, 110)
                    c.ellipse(640 + math.cos(a) * d, PAVE - 70 + math.sin(a) * d * 0.8, 3, 5, (170, 210, 255), w=1)
        elif t < T("g_box", 0.85):
            u = ring_out
            D.cat(c, lerp(BOX_X + 10, 680, u), PAVE + arc_y(u, 160), D.WHISKERS, 0.95, 1, "leap", t=t, wet=wet,
                  eyes="wide", mouth=0.5)
        else:
            wx = smooth(t, [(T("g_box", 0.85), 680), (T("g_still", 0.2), 680), (T("g_still", 0.9), 770)])
            if run_off > 0:
                wx = lerp(770, 1600, ease(run_off))
            pose = "stand"
            if 0 < run_off < 1 or (T("g_still", 0.2) <= t < T("g_still", 0.9)):
                pose = "walk"
            eyes = "open"
            head = 0.0
            mouth = tl.mouth("whiskers", t)
            sq = 1.0
            if between(tl, t, "g_boo", "g_rule"):
                u = tl.prog("g_boo", t)
                pose = "crouch" if u < 0.75 else "leap"
                eyes = "happy" if u < 0.4 else ("wide" if u > 0.75 else "open")
                if u < 0.75:
                    sq = 1 + 0.08 * math.sin(t * 18)
            if between(tl, t, "g_rule", "g_tip"):
                eyes = "wide"
            if between(tl, t, "g_hero", "g_sneeze", 0, 0.25):
                eyes = "happy"
            if between(tl, t, "g_sneeze", "g_sneeze", 0.35, 0.6):
                eyes = "happy"
                mouth = 0.6 + 0.3 * math.sin(t * 15)
            kitty(c, tl, t, "whiskers", wx, PAVE, 0.95, 1, pose, walk=wx / 12, wet=wet, eyes=eyes, mouth=mouth,
                  squash=sq, look=(1, -0.6), head_dy=head)

    # ---- rain over everything
    P.rain(c, t, n=170, col=(214, 222, 238))
    P.splashes(c, t, 540, 710)
    return finish(c, tl, t, 0.4)


# ======================================================================= chips

GROUND = 664
TRAY = (712, 670)


def chips_tray(c, x, y, s=1.0, chips=9, fish=True, t=0.0):
    c.push(x, y, s)
    c.poly([(-58, -6), (58, -6), (46, 8), (-46, 8)], (246, 244, 236), w=2)
    rng = np.random.default_rng(9)
    spots = [(rng.uniform(-40, 40), rng.uniform(-22, -10), rng.uniform(-0.8, 0.8)) for _ in range(9)]
    for k, (dx, dy, a) in enumerate(spots[:chips]):
        P.chip(c, dx, dy, 1.0, a)
    if fish:
        P.fried_fish(c, 6, -28, 1.0, -0.15)
    c.poly([(-58, -6), (-70, -30), (-40, -12)], (236, 232, 222), w=2)
    c.poly([(58, -6), (70, -30), (40, -12)], (236, 232, 222), w=2)
    for k in range(3):
        u = (t * 0.5 + k / 3) % 1.0
        c.line([(-20 + 20 * k + 5 * math.sin(t * 3 + k + u * 5), -34 - 50 * u), (-20 + 20 * k, -44 - 50 * u)],
               mix((255, 255, 255), (220, 226, 236), u), 3)
    c.pop()


def embankment_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 170, 230)), (0.55, (196, 224, 246)), (1, (214, 234, 250))]))
        # a rainbow after the rain
        for k, col in enumerate([(240, 90, 90), (250, 170, 80), (250, 230, 110), (120, 200, 120), (110, 160, 230),
                                 (150, 120, 210)]):
            r = 520 - k * 12
            c.arc(640, 520, r, r * 0.8, 180, 360, mix(col, (214, 234, 250), 0.45), 12)
        for x, y, s in ((180, 110, 1.0), (1120, 80, 0.9), (520, 60, 0.7)):
            D.cloud(c, x, y, s, col=(236, 240, 248))
        rng = np.random.default_rng(14)
        skyline(c, rng, -20, W + 20, 410, 30, 90, (196, 190, 196), win=(130, 150, 170), p=0.25)
        P.london_eye(c, 960, 214, 186, rim=(250, 250, 252), legs=True)
        c.rect(-10, 404, W + 10, 418, (170, 160, 150), ol=None)
        water_band(c, -10, W + 10, 418, 556, (86, 130, 168), (150, 190, 220), rng, n=80)
        # a tour boat on the Thames
        c.poly([(470, 500), (670, 500), (650, 524), (490, 524)], (250, 250, 250), w=2)
        c.rect(500, 478, 640, 500, (150, 200, 230), w=2)
        c.rect(500, 474, 640, 480, (214, 40, 46), w=1.5)
        # river wall with balustrade
        stone = (204, 192, 170)
        c.rect(-10, 556, W + 10, 600, stone, w=2.5)
        for x in range(10, W, 36):
            c.rect(x, 566, x + 16, 594, mix(stone, (255, 255, 255), 0.2), w=1.5, r=6)
        c.rect(-10, 548, W + 10, 562, mix(stone, (255, 255, 255), 0.25), w=2.5, r=3)
        c.rect(-10, 600, W + 10, H + 10, (186, 180, 172), ol=None)
        for y in range(622, H, 32):
            c.line([(0, y), (W, y)], (170, 164, 156), 2, cap=False)
        for x, y, rx in ((330, 690, 60), (980, 700, 80)):
            c.ellipse(x, y, rx, rx * 0.16, (180, 210, 240), ol=(150, 160, 170), w=1.5)
        P.plane_tree(c, 60, 610, 1.1)
        P.kiosk(c, 210, 650, 1.0)
        P.lamp_post(c, 820, 650, 1.0, lit=0.0)
        P.plane_tree(c, 1230, 610, 1.15)
        return c.img
    return cached("emb_bg", make)


def chips(tl, t):
    T = tl.t
    c = Canvas(embankment_bg().copy())
    lamp_top = (820, 452)
    # ---- the bus arrives during the chase
    bx = smooth(t, [(T("c_chase", 0.2), -420), (T("c_chase", 0.48), 640), (T("c_chase", 0.68), 640),
                    (T("c_chase", 1.0), 1700)], r=0.2)
    bus_on = T("c_chase", 0.2) <= t
    BY, BS = 772, 0.95
    deck = BY - 170 * BS

    # ---- the tray of fish and chips
    nchips = 9 if t < T("c_swoop", 0.35) else 8
    has_fish = t < T("c_chase", 0.12)
    chips_tray(c, TRAY[0], TRAY[1], 1.35, nchips, has_fish, t)

    # ---- cats on the pavement (before they jump on the bus)
    jump = tl.prog("c_chase", t, 0.5, 0.66)
    on_bus = t >= T("c_chase", 0.66)
    weyes = "happy"
    if t >= T("c_sniff"):
        weyes = "closed"
    if t >= T("c_swoop", 0.3):
        weyes = "wide"
    if t >= T("c_ta"):
        weyes = "open"
    wpose = "sit"
    if t >= T("c_hey"):
        wpose = "stand"
    if not on_bus:
        if jump <= 0:
            pip(c, tl, t, 500, GROUND, 1.0, 1, eyes="wide" if t >= T("c_swoop", 0.3) else "open")
            kitty(c, tl, t, "luna", 420, GROUND, 0.95, 1, "sit",
                  eyes="wide" if between(tl, t, "c_swoop", "c_hey", 0.3) else "open",
                  look=(1, -1) if t >= T("c_swoop", 0.4) else (1, 0))
            wx = 600
            head = 12 if between(tl, t, "c_sniff", "c_swoop", 0, 0.3) else 0
            look = (1, -1) if between(tl, t, "c_swoop", "c_chase", 0.4, 0) else (1, 0.5)
            kitty(c, tl, t, "whiskers", wx, GROUND, 1.0, 1, wpose, eyes=weyes, head_dy=head, look=look)
            if wpose == "stand" and between(tl, t, "c_hey", "c_chase", 0, 0.1):
                c.text(wx + 40, GROUND - 190, "!", 46, (230, 50, 50), stroke=3)
        else:
            for who, x0, x1, s in (("luna", 420, 520, 0.95), ("whiskers", 600, 640, 1.0)):
                pal = D.LUNA if who == "luna" else D.WHISKERS
                D.cat(c, lerp(x0, x1, jump), lerp(GROUND, deck - 4, jump) + arc_y(jump, 120), pal, lerp(s, 0.75, jump),
                      1, "leap", t=t, seed=SEED[who])
            D.mouse(c, lerp(500, 740, jump), lerp(GROUND, deck - 34, jump) + arc_y(jump, 100), 1.0, 1, t)

    # ---- the bus
    if bus_on:
        wheel = bx / 26
        P.bus(c, bx, BY, BS, 1, wheel, part="back")
        if on_bus:
            kitty(c, tl, t, "luna", bx - 120, deck, 0.75, 1, "stand")
            kitty(c, tl, t, "whiskers", bx, deck, 0.78, 1, "stand", eyes="open")
        P.bus(c, bx, BY, BS, 1, wheel, part="front")
        if on_bus:
            D.mouse(c, bx + 100, deck - 34, 1.0, 1, t)

    # ---- Gus
    if T("c_swoop") <= t < T("c_swoop", 0.6):
        u = tl.prog("c_swoop", t, 0.0, 0.6)
        if u < 0.5:
            v = ease(u / 0.5)
            gx, gy = lerp(1400, TRAY[0] + 20, v), lerp(80, TRAY[1] - 20, v)
            gus(c, tl, t, gx, gy, 0.9, -1, fly=1)
        else:
            v = ease((u - 0.5) / 0.5)
            gx, gy = lerp(TRAY[0] + 20, lamp_top[0], v), lerp(TRAY[1] - 20, lamp_top[1], v) + arc_y(v, 120)
            gus(c, tl, t, gx, gy, 0.9, 1, fly=1, chip=True)
    elif T("c_swoop", 0.6) <= t < T("c_chase"):
        gus(c, tl, t, lamp_top[0], lamp_top[1], 0.9, -1, chip=t < T("c_ta", 0.5),
            eyes="happy" if between(tl, t, "c_ta", "c_hey", 0.6) else "open")
    elif T("c_chase") <= t < T("c_chase", 0.56):
        u = tl.prog("c_chase", t, 0.0, 0.56)
        if u < 0.25:
            v = ease(u / 0.25)
            gx, gy = lerp(lamp_top[0], TRAY[0] + 10, v), lerp(lamp_top[1], TRAY[1] - 24, v)
            gus(c, tl, t, gx, gy, 0.9, -1, fly=1)
        else:
            v = (u - 0.25) / 0.75
            gx, gy = lerp(TRAY[0] + 10, bx + 200 * BS, ease(v)), lerp(TRAY[1] - 24, deck - 30, v) + arc_y(v, 200)
            gus(c, tl, t, gx, gy, 0.9, 1, fly=1, fish=True)
    elif t >= T("c_chase", 0.56):
        gus(c, tl, t, bx + 205 * BS, deck - 34 * BS, 0.75, -1, fish=True)
    return finish(c, tl, t, 0.4)


# ========================================================================= bus

SW = 3600


def street_layer():
    def make():
        c = rgba(SW + W, H)
        rng = np.random.default_rng(17)
        shop_row(c, rng)
        return c.img
    return cached("street", make)


def shop_row(c, rng):
    P.shop_row(c, 0, SW + 200, 560, rng)
    # copy the first screen at the end so the layer wraps
    c.rect(-10, 560, SW + W + 10, 600, (196, 190, 182), ol=None)
    c.line([(0, 560), (SW + W, 560)], OUT, 2, cap=False)
    for x in range(0, SW + W, 50):
        c.line([(x, 560), (x - 14, 600)], (176, 170, 162), 2, cap=False)
    c.rect(-10, 600, SW + W + 10, H + 10, (90, 92, 100), ol=None)
    for x in range(0, SW + W, 120):
        c.rect(x, 664, x + 60, 672, (240, 240, 230), ol=None)
    for x in range(260, SW + W, 520):
        P.lamp_post(c, x, 580, 0.9)


def street_far():
    def make():
        c = Canvas(sky_img([(0, (110, 170, 230)), (0.6, (196, 224, 246)), (1, (214, 234, 250))]))
        for x, y, s in ((200, 90, 0.9), (700, 60, 1.1), (1150, 120, 0.8)):
            D.cloud(c, x, y, s)
        rng = np.random.default_rng(19)
        skyline(c, rng, -20, W + 20, 420, 40, 110, (190, 196, 210), win=(160, 170, 190), p=0.2)
        P.st_pauls(c, 960, 420, 1.0, col=(210, 210, 214), shade=(186, 186, 192), dome=(170, 182, 190))
        return c.img
    return cached("street_far", make)


def street_clock(c, x, base):
    c.rect(x - 7, base - 300, x + 7, base, (40, 46, 56), w=2)
    c.rect(x - 16, base - 16, x + 16, base, (40, 46, 56), w=2)
    P.clock_face(c, x, base - 340, 42, 3, 30)


def bridge_wide_bg():
    def make():
        c = Canvas(sky_img([(0, (120, 176, 232)), (0.55, (210, 226, 240)), (1, (240, 226, 200))]))
        for x, y, s in ((160, 100, 1.0), (1100, 70, 1.1)):
            D.cloud(c, x, y, s)
        rng = np.random.default_rng(23)
        skyline(c, rng, -20, W + 20, 470, 40, 120, (196, 196, 206), win=(150, 160, 180), p=0.2)
        water_band(c, -10, W + 10, 470, H + 10, (80, 128, 170), (150, 190, 222), rng, n=120)
        return c.img
    return cached("bwide_bg", make)


def tall_ship(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-150, -20), (150, -20), (120, 20), (-130, 20)], (120, 70, 50), w=2.5)
    c.line([(-150, -14), (150, -14)], (240, 220, 160), 3, cap=False)
    for mx, h in ((-70, 300), (20, 360), (100, 280)):
        c.line([(mx, -20), (mx, -20 - h)], (90, 60, 40), 4)
        for k, w in enumerate((60, 50, 40)):
            yy = -40 - h * 0.28 * k
            c.poly([(mx - w, yy - h * 0.24), (mx + w, yy - h * 0.24), (mx + w * 0.9, yy), (mx - w * 0.9, yy)],
                   (250, 246, 232), w=2)
        c.poly([(mx, -20 - h), (mx + 30, -14 - h), (mx, -8 - h)], (214, 40, 46), w=1.5)
    c.pop()


def bridge_wide(tl, t, open_=0.0, ship=None, bus_x=None, gull_pos=None, cats_top=False):
    c = Canvas(bridge_wide_bg().copy())
    if ship is not None:
        tall_ship(c, ship, 640, 0.95)
    P.tower_bridge(c, 640, 470, 1.1, open_)
    if bus_x is not None:
        P.bus(c, bus_x, 462, 0.24, 1, bus_x / 6)
    if cats_top:
        top = 470 - 232 * 1.1
        D.cat(c, 760, top, D.LUNA, 0.18, 1, "sit", t=t, seed=1.3)
        D.cat(c, 790, top, D.WHISKERS, 0.18, 1, "sit", t=t)
        P.gull(c, 815, top, 0.2, -1, t)
    if gull_pos is not None:
        P.gull(c, gull_pos[0], gull_pos[1], 0.3, 1, t, fly=gull_pos[2], fish=True)
    return c


def bus(tl, t):
    T = tl.t
    if t >= T("u_bridge"):
        u = tl.prog("u_bridge", t)
        bxp = lerp(-150, 1450, u)
        gx = lerp(bxp + 40, 832, ease(clamp(u * 1.6)))
        gy = lerp(440, 470 - 300 * 1.1, ease(clamp(u * 1.6)))
        c = bridge_wide(tl, t, 0.0, bus_x=bxp, gull_pos=(gx, gy, 1 if u < 0.62 else 0))
        return finish(c, tl, t, 0.3)
    s0 = tl.scenes["bus"][0]
    dist = (t - s0) * 260.0
    c = Canvas(street_far().copy())
    paste_layer(c, street_layer(), dist % SW, 0)
    # the street clock rolls past while Pip reads it
    if between(tl, t, "u_half", "u_bridge", 0.0, 0):
        u = tl.prog("u_half", t, -0.15, 1.2)
        street_clock(c, lerp(1500, -200, u), 600)
    BX, BY, BS = 640, 704, 1.15
    deck = BY - 170 * BS
    bob = 2 * math.sin(t * 9)
    P.bus(c, BX, BY + bob, BS, 1, dist / 30, part="back")
    luna_eyes = "wide" if between(tl, t, "u_wrong", "u_nobody") else "open"
    kitty(c, tl, t, "luna", 470, deck + bob, 1.0, -1 if between(tl, t, "u_wrong", "u_wrong", 0, 0.5) else 1,
          "stand", eyes=luna_eyes, look=(1, 0))
    weyes = "open"
    if between(tl, t, "u_gus", "u_half"):
        weyes = "closed"
    kitty(c, tl, t, "whiskers", 640, deck + bob, 1.05, 1, "crouch" if t < T("u_nobody", 1) else "stand",
          eyes=weyes, tail=math.sin(t * 6) * 1.5)
    P.bus(c, BX, BY + bob, BS, 1, dist / 30, part="front")
    pk = 1 if t < T("u_half") else -1
    pip(c, tl, t, 760, deck - 36 * BS + bob, 1.0, pk, proud=between(tl, t, "u_half", "u_bridge"),
        eyes="wide" if between(tl, t, "u_half", "u_bridge") else "open")
    # Gus rides the front rail with the fish, laughing
    laugh = between(tl, t, "u_gus", "u_half")
    hop = abs(math.sin(t * 10)) * 10 if laugh else 0
    gus(c, tl, t, BX + 205 * BS, deck - 34 * BS + bob - hop, 0.85, -1, fish=True, eyes="happy" if laugh else "open",
        mouth=0.0)
    return finish(c, tl, t, 0.4)


# ====================================================================== bridge

DECK = 600           # top of the high walkway in the close-up
NEST = (930, 612)


def bridge_top_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 170, 232)), (0.6, (206, 226, 244)), (1, (246, 230, 206))]))
        for x, y, s in ((140, 90, 1.0), (560, 140, 0.8)):
            D.cloud(c, x, y, s)
        # the city far below
        rng = np.random.default_rng(29)
        skyline(c, rng, -20, W + 20, 500, 20, 70, (186, 186, 200), win=(150, 160, 180), p=0.2)
        P.st_pauls(c, 380, 500, 0.6, col=(200, 200, 208), shade=(176, 176, 186), dome=(160, 172, 182))
        water_band(c, -10, W + 10, 500, DECK, (90, 136, 176), (160, 200, 226), rng, n=60)
        # the tower on the right, close up
        stone, shade, roof = P.STONE, P.STONE_D, P.SLATE
        c.rect(1010, 200, 1300, DECK + 20, stone, w=3)
        c.rect(1200, 200, 1300, DECK + 20, shade, ol=None)
        c.rect(1010, 200, 1300, DECK + 20, None, w=3)
        for wy in (300, 420):
            c.rect(1070, wy, 1120, wy + 80, mix(roof, (20, 20, 30), 0.2), w=2.5, r=24)
        c.rect(990, 170, 1080, 214, stone, w=3)
        c.poly([(988, 170), (1034, 60), (1080, 170)], roof, w=3)
        c.line([(1034, 60), (1034, 30)], P.GOLD, 4)
        c.poly([(1060, 200), (1150, 20), (1300, 20), (1300, 200)], roof, w=3)
        # walkway deck with a blue and white railing
        c.rect(-10, DECK, W + 10, H + 10, (150, 170, 196), w=3)
        c.rect(-10, DECK, W + 10, DECK + 18, (196, 214, 232), w=2.5)
        for x in range(0, W, 120):
            c.line([(x, DECK + 18), (x + 40, H)], (130, 150, 176), 3, cap=False)
        c.rect(-10, DECK - 64, 1010, DECK - 54, P.BRIDGE_BLUE, w=2)
        for x in range(10, 1000, 34):
            c.line([(x, DECK - 54), (x, DECK)], P.BRIDGE_BLUE, 4, cap=False)
        return c.img
    return cached("btop_bg", make)


def bridge_close(tl, t):
    T = tl.t
    s0 = tl.scenes["bridge"][0]
    c = Canvas(bridge_top_bg().copy())
    # ---- nest, chicks and Gus
    P.nest(c, NEST[0], NEST[1], 1.0, part="back")
    fed = t >= T("br_give", 0.9)
    for k, dx in enumerate((-36, 0, 36)):
        P.chick(c, NEST[0] + dx, NEST[1] - 6, 1.0 + 0.1 * (k == 1), t * (1.6 if fed else 1), seed=k,
                beak=0.2 if fed and k == 1 else None)
    if T("br_give", 0.6) <= t < T("br_give", 0.9):
        u = tl.prog("br_give", t, 0.6, 0.9)
        P.fried_fish(c, lerp(1010, NEST[0], u), lerp(NEST[1] - 70, NEST[1] - 30, u) + arc_y(u, 40), 1.0, 0.3)
    elif fed:
        P.fried_fish(c, NEST[0] + 6, NEST[1] - 26, 0.9, -0.2)
    P.nest(c, NEST[0], NEST[1], 1.0, part="front")
    gface = -1
    gsad = 1.0 if between(tl, t, "br_aha", "br_give", 0.6, 0.6) else 0.0
    geyes = "happy" if t >= T("br_kind") else "open"
    holds_fish = t < T("br_give", 0.6)
    flying = 0
    gx, gy = 1060, DECK + 10
    if t >= T("br_oi"):
        u = tl.prog("br_oi", t, 0.7, 1.0)
        if u > 0:
            flying = 1
            gx, gy = lerp(1060, 1500, ease(u)), lerp(DECK + 10, 80, ease(u))
            gface = 1
    if t >= T("br_tow"):
        flying = 1
        gx, gy = -200, -200
    hop = abs(math.sin(t * 9)) * 8 if (tl.talking("gus", t) and t >= T("br_oi")) else 0
    gus(c, tl, t, gx, gy - hop, 1.15, gface, fish=holds_fish, sad=gsad, eyes=geyes, fly=flying)

    # ---- the cats
    climb = tl.prog("br_climb", t, 0.0, 0.45)
    if t < T("br_tow", 0.62):
        # Luna and Pip follow up the edge
        lx = smooth(t, [(s0, 120), (T("br_climb", 0.5), 120), (T("br_climb", 1.0), 380), (T("br_kind"), 380),
                        (T("br_kind", 0.4), 470)])
        ly = DECK + lerp(220, 0, ease(tl.prog("br_climb", t, 0.15, 0.55)))
        leyes = "open"
        if between(tl, t, "br_aha", "br_chicks", 0.5):
            leyes = "wide"
        if t >= T("br_kind"):
            leyes = "happy"
        if between(tl, t, "br_never", "br_oi"):
            leyes = "closed"
        moving = T("br_climb", 0.5) < t < T("br_climb", 1.0) or T("br_kind") < t < T("br_kind", 0.4)
        if t >= T("br_tow"):
            leyes = "wide"
        if t < T("br_tow", 0.5):
            kitty(c, tl, t, "luna", lx, ly, 0.95, 1, "walk" if moving else "stand", walk=lx / 12, eyes=leyes)
        px = lx + 70 if t < T("br_climb", 1.0) else 300
        if t < T("br_tow"):
            pip(c, tl, t, px - 160, ly, 1.0, 1, proud=between(tl, t, "br_up", "br_never"))
        # Whiskers climbs over the railing and stalks the thief
        if t >= T("br_tow", 0.6):
            pass
        elif climb < 1:
            wx, wy = 300, DECK + lerp(240, 0, ease(climb))
            kitty(c, tl, t, "whiskers", wx, wy, 1.0, 1, "stand", look=(1, -1))
        else:
            wx = smooth(t, [(T("br_climb", 0.45), 300), (T("br_climb", 1.0), 640), (T("br_aha", 0.3), 700)])
            pose = "stand"
            if T("br_climb", 0.45) < t < T("br_climb", 1.0):
                pose = "walk"
            weyes = "open"
            if between(tl, t, "br_aha", "br_aha", 0.0, 0.5):
                pose = "crouch"
            if between(tl, t, "br_aha", "br_chicks", 0.5, 1.0):
                weyes = "wide"
            if between(tl, t, "br_think", "br_give", 0, 0.1):
                pose, weyes = "sit", "closed"
            if between(tl, t, "br_give", "br_open"):
                pose = "sit"
                weyes = "happy" if t >= T("br_give", 0.5) else "open"
            if t >= T("br_up"):
                pose = "sit"
                weyes = "open"
            kitty(c, tl, t, "whiskers", wx, DECK, 1.0, 1, pose, walk=wx / 12, eyes=weyes,
                  look=(1, 0.6) if t >= T("br_aha", 0.5) else (1, 0))
        # little hearts for the kind cat
        if T("br_kind") <= t < T("br_open"):
            for k in range(4):
                u = (t * 0.4 + k / 4) % 1.0
                hx, hy = 600 + 40 * math.sin(k * 2.3 + t), DECK - 200 - 160 * u
                r = 8 * (1 - u * 0.4)
                col = mix((240, 90, 120), (250, 200, 210), u)
                c.circle(hx - r * 0.55, hy, r * 0.65, col, ol=None)
                c.circle(hx + r * 0.55, hy, r * 0.65, col, ol=None)
                c.poly([(hx - r * 1.15, hy + 2), (hx + r * 1.15, hy + 2), (hx, hy + r * 1.4)], col, ol=None)

    # ---- the gull taxi: Gus's friends tow Ruby's balloon in
    if t >= T("br_tow"):
        u = tl.prog("br_tow", t)
        bx = smooth(t, [(T("br_tow"), -500), (T("br_tow", 0.45), 520), (T("br_tow", 0.8), 520),
                        (T("br_tow", 1.0), 1500)])
        by = DECK + 6 - 260 * ease(tl.prog("br_tow", t, 0.8, 1.0))
        BS = 1.0
        P.balloon(c, bx, by, BS, t, part="back", flame=1.0 if u > 0.8 else 0.0)
        if u >= 0.62:
            kitty(c, tl, t, "luna", bx - 36, by - 30, 0.6, 1, "sit", eyes="happy")
        if u >= 0.72:
            kitty(c, tl, t, "whiskers", bx + 34, by - 30, 0.6, 1, "sit", eyes="happy")
        ruby(c, tl, t, bx - 80, by - 70, 0.9, 1)
        P.balloon(c, bx, by, BS, t, part="front")
        if u >= 0.72:
            D.mouse(c, bx + 70, by - 70, 0.9, 1, t)
        # four towing gulls, ropes from their feet to the envelope
        for k in range(4):
            gxk = bx + 220 + 70 * (k % 2) + 30 * k
            gyk = by - 520 + 70 * k + 10 * math.sin(t * 5 + k)
            c.line([(bx + 100, by - 380 + 30 * k), (gxk - 6, gyk - 30)], (120, 90, 60), 2)
            P.gull(c, gxk, gyk, 0.7, 1, t + k * 0.3, fly=1, fish=False)
        # jumping in
        if 0.5 <= u < 0.62:
            v = (u - 0.5) / 0.12
            D.cat(c, lerp(470, bx - 36, v), lerp(DECK, by - 30, v) + arc_y(v, 90), D.LUNA, lerp(0.95, 0.6, v), 1,
                  "leap", t=t, seed=1.3)
        if 0.6 <= u < 0.72:
            v = (u - 0.6) / 0.12
            D.cat(c, lerp(700, bx + 34, v), lerp(DECK, by - 30, v) + arc_y(v, 90), D.WHISKERS, lerp(1.0, 0.6, v), -1,
                  "leap", t=t)
        if u < 0.7:
            D.mouse(c, lerp(300, bx + 70, clamp((u - 0.62) / 0.08)), DECK, 1.0, 1, t)
    # gentle push-in on the nest while Gus explains
    z = 1.2 + 0.3 * ease(tl.prog("br_chicks", t, 0.0, 0.6)) * (1 - ease(tl.prog("br_think", t, 0.3, 1.0)))
    c = zoom(c, 700 + 120 * (z - 1.2) / 0.3, 470, z)
    return c


def bridge(tl, t):
    T = tl.t
    if T("br_open") <= t < T("br_oi"):
        u = tl.prog("br_open", t, 0.0, 1.0)
        op = ease(clamp((t - T("br_open")) / (T("br_never", 0.6) - T("br_open"))))
        ship = lerp(1700, -500, clamp((t - T("br_open", 0.4)) / (T("br_oi") - T("br_open", 0.4))))
        c = bridge_wide(tl, t, op, ship=ship, cats_top=True)
        return finish(c, tl, t, 0.3)
    return finish(bridge_close(tl, t), tl, t, 0.3)


# ====================================================================== bigben

def westminster_bg():
    def make():
        c = Canvas(sky_img([(0, (98, 150, 220)), (0.55, (220, 210, 220)), (1, (255, 214, 160))]))
        for x, y, s in ((200, 120, 1.1), (640, 80, 0.8)):
            D.cloud(c, x, y, s, col=(255, 246, 236))
        c.circle(160, 300, 40, (255, 236, 170), ol=None)
        rng = np.random.default_rng(31)
        skyline(c, rng, -20, W + 20, 520, 20, 60, (200, 180, 196), win=None)
        P.parliament(c, -20, 900, 610, 120)
        water_band(c, -10, W + 10, 610, H + 10, (86, 120, 160), (220, 190, 160), rng, n=90)
        return c.img
    return cached("west_bg", make)


def clock_stage_bg():
    def make():
        c = Canvas(bg=P.STONE)
        stone, shade = P.STONE, P.STONE_D
        for x in range(-20, W + 40, 64):
            c.rect(x, 0, x + 10, H, shade, ol=None)
        for y in range(40, H, 90):
            c.line([(0, y), (W, y)], shade, 3, cap=False)
        return c.img
    return cached("cstage", make)


def big_dial(c, x, y, r, hours, minutes):
    c.rect(x - r * 1.35, y - r * 1.35, x + r * 1.35, y + r * 1.35, P.STONE, w=4)
    c.rect(x - r * 1.25, y - r * 1.25, x + r * 1.25, y + r * 1.25, mix(P.GOLD, P.STONE, 0.5), w=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.circle(x + sx * r * 1.12, y + sy * r * 1.12, r * 0.08, P.GOLD, w=2)
    P.clock_face(c, x, y, r, hours, minutes, w=4)


def bong_rings(c, x, y, r, dt):
    if 0 <= dt < 1.2:
        for k in range(3):
            u = dt / 1.2 + k * 0.12
            if u < 1:
                c.circle(x, y, r * (1.05 + 0.9 * u), None, ol=mix((255, 240, 180), P.STONE, u), w=6 * (1 - u) + 1)


def bigben(tl, t):
    T = tl.t
    s0 = tl.scenes["bigben"][0]
    # ---- wide: the gull taxi races to the tower
    if t < T("bb_tick"):
        c = Canvas(westminster_bg().copy())
        P.big_ben(c, 1060, 900, 860, 3, 58)
        u = clamp((t - s0) / (T("bb_tick") - s0))
        bx = lerp(-300, 640, ease(u))
        by = 560 + 12 * math.sin(t * 2)
        BS = 0.85
        by = 600 + 12 * math.sin(t * 2)
        P.balloon(c, bx, by, BS, t, part="back", flame=1.0 if T("bb_hold", 0.8) < t else 0.0)
        kitty(c, tl, t, "luna", bx - 30, by - 26, 0.5, 1, "sit", look=(1, -1))
        kitty(c, tl, t, "whiskers", bx + 30, by - 26, 0.5, 1, "sit", eyes="wide")
        ruby(c, tl, t, bx - 68, by - 60, 0.9, 1, wave=1.0 if tl.talking("ruby", t) else 0.0)
        P.balloon(c, bx, by, BS, t, part="front")
        D.mouse(c, bx + 60, by - 60, 0.8, 1, t)
        for k in range(4):
            gxk = bx + 230 + 60 * (k % 2) + 30 * k
            gyk = by - 450 + 60 * k + 8 * math.sin(t * 6 + k)
            c.line([(bx + 90, by - 320 + 24 * k), (gxk - 4, gyk - 24)], (120, 90, 60), 2)
            P.gull(c, gxk, gyk, 0.65, 1, t + k * 0.3, fly=1)
        return finish(c, tl, t, 0.3)
    # ---- close-up: the minute hand clicks up to twelve
    if t < T("bb_bong"):
        c = Canvas(clock_stage_bg().copy())
        u = tl.prog("bb_tick", t)
        m = 59 + math.floor(u * 4 + 0.001) / 4
        big_dial(c, 640, 360, 250, 3, m)
        return c
    # ---- the bongs, then tea beside the clock
    c = Canvas(clock_stage_bg().copy())
    shake = 0.0
    bongs = [T("bb_bong", f) for f in (0.05, 0.3, 0.55, 0.8)]
    last = max([b for b in bongs if b <= t], default=None)
    dt = t - last if last is not None else 9
    if dt < 0.5:
        shake = 6 * math.sin(dt * 60) * (1 - dt / 0.5)
    CX, CY, R = 340 + shake, 330, 230
    big_dial(c, CX, CY, R, 4, 0)
    bong_rings(c, CX, CY, R, dt)
    if dt < 0.9 and t < T("bb_heard"):
        k = 1 - dt / 0.9
        c.text(CX, CY + R * 0.42, "BONG!", 30 + 34 * (1 - k), mix(P.STONE, (120, 60, 40), k), stroke=3 * k,
               stroke_fill=(255, 240, 200))
    # balloon at the right with everyone (close: the envelope runs off the top)
    bx, by, BS = 880 + shake * 0.5, 724 + 5 * math.sin(t * 1.4), 2.0
    P.balloon(c, bx, by, BS, t, part="back")
    rim = by - 70 * BS
    tea = t >= T("bb_tea", 0.3)
    leyes = "wide" if t < T("bb_bong", 0.3) else "happy"
    if t >= T("bb_tea"):
        leyes = "happy" if between(tl, t, "bb_cheers", "bb_cheers", 0, 1) or t < T("bb_narr") else "open"
    kitty(c, tl, t, "luna", bx - 84, by - 58 * BS, 1.15, 1, "sit", eyes=leyes, look=(-1, -0.5))
    weyes = "wide" if t < T("bb_heard") else "happy"
    if between(tl, t, "bb_sorry", "bb_purpose"):
        weyes = "open"
    wmouth = tl.mouth("whiskers", t)
    if between(tl, t, "bb_narr", "bb_scones", 0.5, 0):
        wmouth = 0.3 + 0.3 * abs(math.sin(t * 9))          # munching
    wface = -1 if t < T("bb_sorry") else 1
    kitty(c, tl, t, "whiskers", bx + 74, by - 58 * BS, 1.18, wface, "sit", eyes=weyes, mouth=wmouth)
    P.balloon(c, bx, by, BS, t, part="front")
    ruby(c, tl, t, bx - 160, rim, 1.4, 1, wave=1.0 if tl.talking("ruby", t) else 0)
    gus(c, tl, t, bx + 172, rim + 4, 1.1, -1, eyes="happy" if t >= T("bb_purpose") else "open")
    pip(c, tl, t, bx - 8, rim, 1.2, 1, eyes="happy" if t >= T("bb_heard") else "wide")
    if tea:
        k = ease(tl.prog("bb_tea", t, 0.3, 0.8))
        y = rim - 4
        P.teapot(c, bx - 100, y - 30 * (1 - k), 0.9)
        P.teacup(c, bx - 40, y, 1.0, steam=1.0, t=t)
        nsc = 3
        if t >= T("bb_narr", 0.5):
            nsc = 2
        if t >= T("bb_scones", 0.5):
            nsc = 1
        c.push(bx + 100, y)
        c.line([(0, 0), (0, -90)], P.GOLD, 4)
        c.circle(0, -94, 5, P.GOLD, w=1.5)
        c.ellipse(0, -2, 40, 6, (246, 248, 252), w=1.5)
        for kk in range(nsc):
            P.scone(c, -22 + 22 * kk, -4, 0.85)
        c.ellipse(0, -50, 28, 5, (246, 248, 252), w=1.5)
        for dx, col in ((-12, (250, 190, 210)), (12, (200, 230, 160))):
            c.rect(dx - 8, -64, dx + 8, -52, col, w=1.5, r=2)
        c.pop()
        P.teacup(c, bx + 40, y, 1.0, steam=1.0, t=t + 1)
        # Whiskers' scone with jam and cream
        if between(tl, t, "bb_narr", "bb_sorry", 0.5, 0):
            P.scone(c, bx + 74 + 46 * wface, by - 58 * BS - 92, 1.1)
    # sparkles of joy at the end
    if t >= T("bb_cheers"):
        for k in range(10):
            a = t * 0.8 + k * 0.63
            px, py = bx + 260 * math.cos(a), by - 330 + 120 * math.sin(a * 1.3)
            r = 3 + 3 * abs(math.sin(t * 4 + k))
            c.poly([(px, py - 2 * r), (px + r * 0.5, py), (px, py + 2 * r), (px - r * 0.5, py)], (255, 236, 150),
                   ol=None)
    return finish(c, tl, t, 0.35)


# ======================================================================== home

def sea_night():
    def make():
        c = Canvas(sky_img([(0, (14, 18, 48)), (0.6, (40, 44, 96)), (1, (66, 64, 118))]))
        D.stars(c, 23, 160, W, 440)
        D.moon(c, 1040, 140, 56, sky=(20, 26, 64))
        rng = np.random.default_rng(5)
        water_band(c, -10, W + 10, 500, H + 10, (30, 44, 88), (90, 100, 160), rng, n=100)
        for k in range(18):
            y = 506 + k * 11
            c.line([(1040 - 50 + k, y), (1040 + 50 - k, y)], (220, 220, 190), 2, cap=False)
        c.poly([(0, 500), (120, 470), (260, 500)], (24, 30, 60), ol=None)        # far coast
        c.rect(70, 450, 80, 480, (240, 240, 230), ol=None)
        return c.img
    return cached("sea_night", make)


def home(tl, t):
    T = tl.t
    s0 = tl.scenes["home"][0]
    if t < T("h_sill"):
        c = Canvas(sea_night().copy())
        u = clamp((t - s0) / (T("h_sill") - s0))
        bx = lerp(-120, 1400, u)
        by = 430 + 10 * math.sin(t * 1.2)
        c.tint = NIGHT
        P.balloon(c, bx, by, 0.5, t, part="back", flame=1.0 if 0.3 < u < 0.4 else 0)
        kitty(c, tl, t, "luna", bx - 18, by - 14, 0.3, 1, "sit", eyes="closed")
        kitty(c, tl, t, "whiskers", bx + 18, by - 14, 0.3, 1, "sit", eyes="closed")
        P.balloon(c, bx, by, 0.5, t, part="front")
        ruby(c, tl, t, bx - 44, by - 35, 0.55, 1)
        c.tint = None
        return c
    c = Canvas(room_bg(True).copy())
    glow = 1.0 if T("h_radio") <= t < T("h_moral", 0.5) else 0.0
    P.radio(c, 330, 500, 0.95, glow=glow, t=t)
    # outside: Ruby's balloon floats away into the night
    u = tl.prog("h_sill", t, 0.0, 1.0) * 0.4 + tl.prog("h_next", t) * 0.3 + tl.prog("h_tea", t) * 0.3

    def outside(oc):
        bx, by = lerp(860, 1180, u), lerp(352, 160, u)
        P.balloon(oc, bx, by, 0.6, t, part="all", flame=1.0 if u < 0.15 else 0.0)
        ruby(oc, tl, t, bx - 46, by - 42, 0.6, -1, wave=1.0)
    if u < 1:
        draw_outside(c, outside, night=True)
    else:
        draw_outside(c, lambda oc: None, night=True)
    c.tint = NIGHT
    # souvenirs on the sill: a teacup and a Royal Air Mail tag
    P.teacup(c, 1068, SILL_Y, 0.8)
    c.rect(780, SILL_Y - 22, 820, SILL_Y - 2, (250, 240, 220), w=1.5, r=3)
    c.line([(780, SILL_Y - 12), (768, SILL_Y - 20)], P.RED, 2)
    c.text(800, SILL_Y - 12, "MAIL", 8, P.RED_D)
    asleep = t >= T("h_radio", 0.4)
    if asleep:
        D.cat(c, 870, SILL_Y, D.LUNA, 0.8, -1, "sleep", t=t + 1, seed=1.3)
        D.cat(c, 965, SILL_Y, D.WHISKERS, 0.8, 1, "sleep", t=t)
        D.mouse(c, 918, SILL_Y - 36, 1.0, 1, t, eyes="closed")
    else:
        kitty(c, tl, t, "luna", 870, SILL_Y, 0.75, 1, "sit", look=(1, -1), eyes="open")
        kitty(c, tl, t, "whiskers", 980, SILL_Y, 0.75, -1, "sit", eyes="happy" if t >= T("h_tea") else "open")
        D.mouse(c, 925, SILL_Y, 0.9, 1, t)
    c.tint = None
    if asleep:
        D.zzz(c, 1010, 300, t)
    z = 1 + ease(tl.prog("h_moral", t, 0.0, 1.0)) * 1.0
    if t >= T("h_end"):
        z = 2.0
    c = zoom(c, 920, 290, z)
    k = ease(tl.prog("h_end", t, 0.2, 0.5))
    if k > 0:
        c.text(W / 2, 655, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "radio": radio, "balloon": balloon, "guard": guard, "chips": chips, "bus": bus,
               "bridge": bridge, "bigben": bigben, "home": home}

CONTINUOUS = set()
EXTRA_CUTS = ["u_bridge", "br_open", "br_oi", "bb_tick", "bb_bong", "h_sill"]
