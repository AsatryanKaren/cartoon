"""Athens -- one function per scene, each (tl, t) -> Canvas.

Animation is keyed to script events (tl.t("id", fraction)) so it stays in
sync with the speech. Static backgrounds are drawn once and cached; the
flight over the Aegean and the walk through the Plaka scroll wide cached
layers under a camera. The myths are told as black-figure vase paintings.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.moonfish import scenes as MF
from films.athens import props as P

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA, "socrates": P.SOCRATES}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1, "socrates": 4.4}
NIGHT = ((30, 36, 90), 0.3)
MOON_TINT = ((40, 50, 110), 0.32)
SUNSET_TINT = ((240, 120, 80), 0.12)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def rgba(w, h):
    return Canvas(Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0)), size=(w, h))


def sky_img(stops, w=W, h=H):
    return D.gradient(int(w * SS), int(h * SS), stops)


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


def moving(t, keys):
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    return v


def arc_y(u, height):
    return -4 * height * u * (1 - u)


def between(tl, t, a, b, fa=0.0, fb=0.0):
    return tl.t(a, fa) <= t < tl.t(b, fb)


def kitty(c, tl, t, who, x, y, s=1.0, face=1, pose="stand", walk=0.0, **kw):
    mouth = kw.pop("mouth", tl.mouth(who, t))
    D.cat(c, x, y, PAL[who], s, face, pose, walk=walk, t=t, mouth=mouth, seed=SEED[who], **kw)
    if who == "socrates":
        P.beard(c, x, y, s, face, pose, kw.get("head_dy", 0.0), t=t)


def walker(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    """A cat walking along x keys (time, x); faces its direction of travel."""
    x = smooth(t, keys)
    v = moving(t, keys)
    if abs(v) > 20:
        face = 1 if v > 0 else -1
        if pose in ("stand", "sit"):
            pose = "walk"
    kitty(c, tl, t, who, x, y, s, face, pose, walk=x / (12 * s) if pose == "walk" else 0.0, **kw)
    return x, face, pose


def sophia(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("sophia", t))
    hop = kw.pop("hop", abs(math.sin(t * 8)) * 5 if tl.talking("sophia", t) else 0.0)
    P.owl(c, x, y, s, face, t, mouth=mouth, hop=hop, **kw)


def yaya(c, tl, t, x, y, s=1.0, face=1, **kw):
    mouth = kw.pop("mouth", tl.mouth("yaya", t))
    P.owl(c, x, y, s, face, t, mouth=mouth, gran=True, seed=5.5, **kw)


def owl_on_luna(c, tl, t, x, y, s, face, pose, walk=0.0, **kw):
    """Sophia riding on Luna's back (Luna drawn at x, y, scale s)."""
    if pose in ("stand", "walk", "crouch"):
        bob = math.sin(walk * 2) * 2 * s if pose == "walk" else 0
        ox, oy = x - 4 * s * face, y - 74 * s + bob + (8 * s if pose == "crouch" else 0)
    else:
        ox, oy = x - 22 * s * face, y - 48 * s
    sophia(c, tl, t, ox, oy, 0.5 * s, face, sling=True, **kw)


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


def sea_band(c, x0, x1, y0, y1, col, hi, rng, n=80):
    c.rect(x0, y0, x1, y1, col, ol=None)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0 + 4, y1 - 2)
        ww = rng.uniform(10, 46) * (0.4 + (y - y0) / max(1, y1 - y0))
        c.line([(x - ww / 2, y), (x + ww / 2, y)], hi, 2, cap=False)


def city_blocks(c, rng, x0, x1, base, hmin, hmax, cols, win=None, p=0.3, ol=None):
    """Rows of flat-roofed white Athens buildings."""
    x = x0
    while x < x1:
        w = rng.uniform(30, 80)
        h = rng.uniform(hmin, hmax)
        col = cols[rng.integers(len(cols))]
        c.rect(x, base - h, x + w + 1, base + 2, col, ol=ol, w=1.2)
        if win:
            for wy in np.arange(base - h + 8, base - 6, 12):
                for wx in np.arange(x + 5, x + w - 5, 10):
                    if rng.random() < p:
                        c.rect(wx, wy, wx + 4, wy + 5, win, ol=None)
        x += w


def flash(c, tl, t, ids):
    """Lightning: a quick double white flash after each (event, frac)."""
    a = 0.0
    for ev, f in ids:
        dt = t - tl.t(ev, f)
        if 0 <= dt < 0.45:
            a = max(a, 0.55 * math.exp(-dt * 10) + (0.35 if 0.16 < dt < 0.24 else 0))
    return blend_over(c, (240, 244, 255), a)


# ======================================================================= title

def title_bg():
    def make():
        c = Canvas(sky_img([(0, (86, 120, 196)), (0.35, (190, 170, 210)), (0.62, (255, 196, 150)),
                            (1, (255, 214, 160))]))
        soft_glow(c, 300, 380, 300, (255, 230, 180), 0.6)
        c.circle(300, 390, 50, (255, 238, 190), ol=None)
        # far hills (Hymettus) and the sea glint
        c.poly([(0, 420), (200, 380), (420, 400), (700, 360), (980, 390), (W, 370), (W, 470), (0, 470)],
               (170, 140, 170), ol=None)
        rng = np.random.default_rng(2)
        sea_band(c, 0, 420, 420, 450, (150, 160, 210), (255, 220, 190), rng, n=30)
        c.poly([(0, 450), (W, 440), (W, 520), (0, 520)], (196, 160, 170), ol=None)
        city_blocks(c, rng, -20, W + 20, 520, 14, 50, [(240, 214, 200), (226, 196, 190), (250, 226, 206)])
        # the Acropolis
        top = P.acropolis_rock(c, 820, 560, 820, 200, top_w=520, col=(214, 160, 120), shade=(186, 132, 106),
                               dark=(150, 104, 90), green=(150, 150, 100), seed=3)
        P.parthenon(c, 860, top + 2, 330, 150, col=(255, 236, 214), shade=(236, 200, 180), dark=(200, 160, 150),
                    lw=2)
        P.temple_far(c, 640, top + 2, 70, 50, (250, 230, 210), (210, 170, 160), ol=OUT, lw=1.5, n=4)
        rng = np.random.default_rng(5)
        city_blocks(c, rng, -20, W + 20, 600, 30, 80, [(252, 240, 226), (246, 226, 206), (255, 246, 232),
                                                       (240, 214, 190)], win=(120, 110, 140), p=0.25, ol=OUT)
        # foreground: ancient marble ledge, olive tree frame
        c.rect(-10, 600, W + 10, H + 10, (236, 222, 200), w=2.5)
        for x in range(0, W, 160):
            c.line([(x + 40, 600), (x + 40, H)], (206, 190, 170), 2, cap=False)
        c.rect(-10, 590, W + 10, 606, (250, 240, 222), w=2.5)
        P.olive_tree(c, 90, 600, 1.5, seed=3)
        P.olive_tree(c, 1220, 600, 1.2, seed=8)
        P.broken_column(c, 1040, 600, 150, 22)
        return c.img
    return cached("title_bg", make)


def title(tl, t):
    c = Canvas(title_bg().copy())
    c.tint = ((255, 160, 120), 0.08)
    kitty(c, tl, t, "luna", 520, 596, 0.85, 1, "sit", look=(1, -1), mouth=0, tail=math.sin(t * 1.5))
    kitty(c, tl, t, "whiskers", 680, 596, 0.9, -1, "sit", look=(1, -1), mouth=0)
    # an owl on top of the broken column
    P.owl(c, 1040, 446, 0.75, -1, t, eyes="open", look=(-1, 0))
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(600, 96 - 30 * (1 - k), "Whiskers and the", 44, mix((90, 100, 170), (255, 246, 220), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(600, 180, "OWL OF ATHENS", 24 + 52 * k2, mix((90, 100, 170), (255, 222, 130), k2), stroke=5 * k2)
    if k2 > 0:
        P.meander(c, 600 - 300 * k2, 600 + 300 * k2, 226, 16, col=mix((90, 100, 170), (255, 236, 200), k2))
    return c


# ======================================================================= storm

WIN = (764, 114, 1076, 366)
SILL_Y = 372


def window_mask():
    def make():
        m = Image.new("L", (W * SS, H * SS), 0)
        ImageDraw.Draw(m).rectangle([WIN[0] * SS, WIN[1] * SS, WIN[2] * SS, WIN[3] * SS], fill=255)
        return m
    return cached("winmask", make)


def outside_bg(kind):
    def make():
        if kind == "storm":
            c = Canvas(sky_img([(0, (20, 24, 46)), (0.5, (40, 44, 70)), (1, (54, 56, 84))]))
            for x, y, s in ((830, 170, 1.1), (1000, 150, 1.3), (920, 230, 0.9)):
                D.cloud(c, x, y, s, col=(62, 64, 92))
        elif kind == "night":
            c = Canvas(sky_img([(0, (14, 18, 48)), (0.5, (40, 44, 96)), (1, (60, 62, 120))]))
            D.stars(c, 8, 80, W, 360)
            D.moon(c, 1010, 180, 30, sky=(40, 44, 96))
        else:
            c = Canvas(sky_img([(0, (110, 180, 240)), (0.6, (190, 226, 250)), (1, (210, 236, 252))]))
        roof = (40, 40, 70) if kind != "day" else (150, 110, 100)
        c.poly([(740, 366), (800, 318), (900, 318), (960, 366)], roof, ol=None)
        c.rect(820, 296, 838, 330, roof, ol=None)
        c.poly([(960, 366), (1010, 330), (1100, 330), (1100, 366)], mix(roof, (0, 0, 0), 0.15), ol=None)
        return c.img
    return cached(("outside", kind), make)


def window_frame(c, night=True):
    bar = (150, 150, 180) if night else (240, 240, 240)
    c.rect(756, 106, 1084, 374, None, w=8)
    c.line([(920, 110), (920, 370)], bar, 6, cap=False)
    c.line([(760, 240), (1080, 240)], bar, 6, cap=False)


def draw_outside(c, fn, kind="night"):
    oc = Canvas(outside_bg(kind).copy())
    fn(oc)
    c.img.paste(oc.img, (0, 0), window_mask())
    window_frame(c, kind != "day")


def room_bg(night=True):
    def make():
        c = Canvas(MF.room(night).copy())
        if night:
            # Luna's reading lamp: a warm pool of light on the rug
            c.rect(300, 470, 316, 600, (90, 80, 100), w=2)
            c.ellipse(308, 604, 34, 8, (90, 80, 100), w=2)
            soft_glow(c, 330, 560, 420, (255, 214, 150), 0.35)
            c.poly([(270, 470), (346, 470), (330, 420), (286, 420)], (250, 220, 150), w=2.5)
        return c.img
    return cached(("room", night), make)


def rain(c, t, x0, y0, x1, y1, n=70, col=(170, 190, 230)):
    rng = np.random.default_rng(1)
    for k in range(n):
        x = rng.uniform(x0, x1)
        sp = rng.uniform(500, 700)
        y = y0 + ((rng.uniform(0, 1) * (y1 - y0) + t * sp) % (y1 - y0))
        c.line([(x, y), (x - 6, y + 18)], col, 1.5, cap=False)


def book(c, x, y, s=1.0, page=0.0):
    """An open picture book lying on the rug."""
    c.push(x, y, s)
    c.poly([(-70, -6), (0, -16), (70, -6), (70, 4), (0, -6), (-70, 4)], (150, 60, 50), w=2.5)
    c.poly([(-66, -10), (0, -22), (0, -10), (-66, 0)], (250, 242, 222), w=2)
    c.poly([(66, -10), (0, -22), (0, -10), (66, 0)], (250, 242, 222), w=2)
    c.poly([(-56, -10), (-10, -18), (-10, -12), (-56, -4)], P.TERRA, ol=None)
    c.circle(-34, -10, 4, P.BLACKFIG, ol=None)
    for k in range(3):
        c.line([(10, -16 + k * 3.5), (56, -9 + k * 3)], (150, 140, 130), 1, cap=False)
    if 0 < page < 1:                                     # a page turning over
        ang = page * math.pi
        px = 60 * math.cos(ang)
        c.poly([(0, -22), (px, -10 - 14 * math.sin(ang)), (px, -2 - 10 * math.sin(ang)), (0, -10)],
               (255, 250, 236), w=1.5)
    c.pop()


# --------------------------------------------------------------- vase frieze

FX0, FY0, FX1, FY1 = 90, 92, 1190, 560        # the painted panel


def frieze_bg(night=False):
    def make():
        c = Canvas(bg=(52, 34, 30))
        # the page of the book: parchment with a soft edge
        c.rect(40, 30, W - 40, H - 30, (246, 232, 200), w=3, r=10)
        c.rect(56, 46, W - 56, H - 46, (240, 224, 188), ol=None, r=8)
        clay = P.TERRA if not night else (190, 96, 56)
        c.rect(FX0, FY0, FX1, FY1, clay, w=3)
        # glaze shading: lighter in the middle like a round vase
        for k in range(10):
            f = k / 10
            c.rect(FX0 + 300 * f, FY0 + 4, FX1 - 300 * f, FY1 - 4, mix(clay, P.TERRA_L, f * 0.6), ol=None)
        P.meander(c, FX0, FX1, FY0 + 6, 26)
        P.meander(c, FX0, FX1, FY1 - 32, 26)
        c.rect(FX0, FY0, FX1, FY1, None, w=3)
        # ground line
        c.rect(FX0 + 10, 492, FX1 - 10, 498, P.BLACKFIG, ol=None)
        if night:
            rng = np.random.default_rng(4)
            for _ in range(26):
                x, y = rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 50, 300)
                c.poly([(x, y - 6), (x + 2, y - 2), (x + 6, y), (x + 2, y + 2), (x, y + 6), (x - 2, y + 2),
                        (x - 6, y), (x - 2, y - 2)], P.TERRA_L, ol=None)
            c.circle(980, 170, 36, P.TERRA_L, ol=None)
            c.circle(992, 162, 30, mix(clay, P.TERRA_L, 0.45), ol=None)
        return c.img
    return cached(("frieze", night), make)


def bf_city(c, x, base, s=1.0):
    """A little black-figure hill with a temple on top: the city both gods want."""
    c.push(x, base, s)
    c.poly([(-150, 0), (-90, -60), (90, -60), (150, 0)], P.BLACKFIG, ol=None)
    c.rect(-60, -76, 60, -60, P.BLACKFIG, ol=None)
    for k in range(5):
        c.rect(-52 + k * 24, -130, -40 + k * 24, -76, P.BLACKFIG, ol=None)
    c.rect(-64, -142, 64, -130, P.BLACKFIG, ol=None)
    c.poly([(-66, -142), (0, -172), (66, -142)], P.BLACKFIG, ol=None)
    c.line([(-40, -150), (40, -150)], P.TERRA_L, 1.5, cap=False)
    c.pop()


def bf_person(c, x, base, s, t, cheer=0.0, k=0, face=1, yuck=0.0):
    c.push(x, base - abs(math.sin(t * 7 + k)) * 8 * cheer, s, flip=face < 0)
    col = P.BLACKFIG
    c.poly([(-10, 0), (-6, -40), (8, -40), (12, 0)], col, ol=None)
    c.ellipse(0, -52, 9, 13, col, ol=None)
    c.circle(2 - 4 * yuck, -72, 8, col, ol=None)
    for side in (-1, 1):
        a = math.radians(-90 - side * (30 + 50 * cheer)) if cheer else math.radians(90 - side * 20)
        c.line([(0, -58), (math.cos(a) * 22, -58 + math.sin(a) * 22)], col, 4)
    c.pop()


def frieze_myth(tl, t):
    T = tl.t
    c = Canvas(frieze_bg().copy())
    bf_city(c, 640, 492, 1.0)
    # Poseidon on the right raises his trident and strikes the rock
    arm = ease(tl.prog("s_rock", t, 0.0, 0.3)) * (1 - ease(tl.prog("s_rock", t, 0.32, 0.45)))
    lunge = ease(tl.prog("s_rock", t, 0.3, 0.42)) * (1 - ease(tl.prog("s_salt", t, 0.3, 0.6)))
    P.bf_figure(c, 960 - 40 * lunge, 492, 1.25, "poseidon", arm=arm, face=-1)
    # the salty spring
    if t >= T("s_rock", 0.35):
        u = ease(tl.prog("s_rock", t, 0.35, 0.6))
        for k in range(5):
            ph = t * 4 + k
            hh = (60 + 40 * math.sin(ph)) * u
            x = 820 + k * 12 - 24
            c.line([(x, 492), (x + 6 * math.sin(ph), 492 - hh), (x + 18, 492 - hh * 0.7)], P.BLACKFIG, 3)
        for k in range(4):
            yy = 470 + k * 6
            c.arc(820, yy, 40 - k * 6, 6, 0, 180, P.BLACKFIG, 2)
    # Athena on the left plants the olive tree
    plant = ease(tl.prog("s_olive", t, 0.0, 0.25))
    P.bf_figure(c, 300, 492, 1.25, "athena", arm=0.4 * plant)
    grow = ease(tl.prog("s_olive", t, 0.15, 0.7))
    P.bf_olive(c, 450, 492, grow)
    # the people of the city: they taste the salt water (yuck), then cheer for the olive tree
    cheer = ease(tl.prog("s_olive", t, 0.6, 0.9))
    yuck = ease(tl.prog("s_salt", t, 0.5, 0.75)) * (1 - cheer)
    for k, (px, f) in enumerate(((560, 1), (600, 1), (700, -1), (735, -1))):
        face = f if yuck < 0.5 else -1
        bf_person(c, px, 492, 1.0, t, cheer=cheer, k=k, face=face if cheer < 0.5 else (1 if px < 640 else -1),
                  yuck=yuck)
    if yuck > 0.3:
        c.text(760, 300, "Yuck!", 30, P.BLACKFIG)
    if cheer > 0.2:
        c.text(640, 230, "ΑΘΗΝΑΙ", 30 * cheer, P.BLACKFIG)
        rng = np.random.default_rng(int(t * 3))
        for _ in range(6):
            x, y = 450 + rng.uniform(-110, 110), 300 + rng.uniform(-80, 60)
            c.circle(x, y, 3, P.TERRA_L, ol=None)
    # the page turns in from the right at the start
    return c


def frieze_owl(tl, t):
    c = Canvas(frieze_bg(night=True).copy())
    P.bf_figure(c, 420, 492, 1.3, "athena", arm=0.15)
    P.bf_olive(c, 820, 492, 1.0, seed=9)
    # the owl on a branch, asking
    P.bf_owl(c, 820, 360, 0.9, blink=D.blink(t, 1.1))
    for k in range(3):
        u = (t * 0.45 + k / 3) % 1.0
        x = 880 + 50 * u + 12 * k
        y = 300 - 120 * u
        c.text(x, y, "?", 26 + 22 * u, mix(P.TERRA_L, (250, 230, 200), u))
    return c


def storm(tl, t):
    T = tl.t
    if T("s_myth") <= t < T("s_dinner"):
        c = frieze_myth(tl, t)
        return finish(c, tl, t, 0.4)
    c = Canvas(room_bg(True).copy())
    thump = T("s_thump", 0.45)

    def outside(oc):
        rain(oc, t, 760, 110, 1080, 370)
        if thump - 0.5 <= t < thump + 0.7:          # Sophia blown against the glass
            u = clamp((t - (thump - 0.5)) / 0.5)
            if t < thump:
                x, y = lerp(1200, 990, u), lerp(160, 240, u) + arc_y(u, 40)
                P.owl(oc, x, y, 0.9, -1, t, eyes="wide", flap=1.0, wet=1.0)
            else:
                v = clamp((t - thump) / 0.7)
                P.owl(oc, 990, lerp(250, 330, v * v), 1.0, -1, t, eyes="closed", wet=1.0, flap=0.4 * (1 - v))
    draw_outside(c, outside, "storm")
    # rain streaks on the glass and a windowsill full of pot plants
    rain(c, t * 0.25, 770, 120, 1070, 360, n=16, col=(140, 160, 210))
    c.tint = NIGHT
    # the book on the rug
    turning = T("s_dinner", 0.8) <= t < T("s_dinner", 1.0) + 0.3
    book(c, 600, 640, 1.0, page=tl.prog("s_dinner", t, 0.8, 1.0) if turning else 0)
    # ---- Whiskers: asleep by the lamp; wakes at the thump; goes to sit under the window
    if t < T("s_dinner"):
        kitty(c, tl, t, "whiskers", 300, 640, 0.95, 1, "sleep")
    elif t < thump:
        kitty(c, tl, t, "whiskers", 330, 640, 0.95, 1, "sit", eyes="closed" if t < T("s_dinner", 0.1) else "open",
              look=(1, 0.5))
    else:
        keys = [(thump + 0.6, 330), (T("s_sophia", 0.5), 760)]
        eyes = "wide" if t < T("s_sophia", 0.3) else "open"
        if T("s_know") <= t < T("s_know", 1):
            eyes = "happy"
        pose = "sit" if t > T("s_sophia", 0.6) else "stand"
        x, f, p = walker(c, tl, t, "whiskers", keys, 640, 0.95, 1, pose, eyes=eyes,
                         look=(1, -1) if t > T("s_sophia", 0.6) else (1, 0),
                         head_dy=-8 if T("s_know") <= t < T("s_where") else 0)
    # ---- Luna: reading on the rug, then up onto the windowsill
    if t < thump + 0.3:
        eyes = "wide" if t >= thump else "open"
        kitty(c, tl, t, "luna", 520, 640, 0.95, 1, "sit", look=(1, 1) if t < thump else (1, -1), eyes=eyes)
    elif t < T("s_sophia", 0.35):
        u = tl.prog("s_sophia", t, 0.0, 0.35)
        if u < 0.4:
            x = lerp(520, 780, ease(u / 0.4))
            kitty(c, tl, t, "luna", x, 640, 0.95, 1, "walk", walk=x / 12)
        else:
            v = (u - 0.4) / 0.6
            D.cat(c, lerp(780, 880, v), lerp(640, SILL_Y, v) + arc_y(v, 110), D.LUNA, lerp(0.95, 0.8, v), 1, "leap",
                  t=t, seed=1.3)
    else:
        lface = -1 if T("s_know") <= t < T("s_south", 1) else 1
        kitty(c, tl, t, "luna", 880, SILL_Y, 0.8, lface, "sit", look=(1, 0) if lface > 0 else (1, 0.8))
    # ---- Sophia on the sill (inside: Luna opened the window for her)
    if t >= T("s_sophia"):
        wet = 1 - clamp((t - T("s_home")) / 6)
        sophia(c, tl, t, 1010, SILL_Y, 0.9, -1, wet=wet, sling=True,
               eyes="happy" if T("s_know") <= t < T("s_know", 1) + 0.3 else "open",
               look=(-1, 0.6) if t >= T("s_know") else (-1, 0))
    # ---- thought bubble: South... mostly (a compass needle spinning)
    k = ease(tl.prog("s_south", t, 0.0, 0.2)) * (1 - ease(tl.prog("s_night", t, 0.4, 0.6)))
    if k > 0.02:
        bx, by = 560, 360
        for f, r in ((0.3, 8), (0.6, 13)):
            c.circle(lerp(720, bx, f), lerp(520, by + 70, f), r * k, (255, 255, 255), w=2)
        c.circle(bx, by, 80 * k, (255, 255, 255), w=2.5)
        c.circle(bx, by, 60 * k, (240, 236, 220), w=2)
        c.text(bx, by - 46 * k, "N", 14 * k + 1, (200, 60, 60))
        c.text(bx, by + 46 * k, "S", 14 * k + 1, OUT)
        a = t * 9
        c.line([(bx - math.cos(a) * 40 * k, by - math.sin(a) * 40 * k), (bx, by)], (60, 60, 70), 4)
        c.line([(bx, by), (bx + math.cos(a) * 40 * k, by + math.sin(a) * 40 * k)], (220, 60, 60), 4)
    c.tint = None
    c = flash(c, tl, t, [("s_open", 0.4), ("s_thump", 0.05)])
    if t >= T("s_night"):
        c = blend_over(c, (10, 10, 30), 0.5 * tl.prog("s_night", t, 0.4, 1.0))
    return finish(c, tl, t, 0.35)


# ===================================================================== airship

def meadow_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 180, 240)), (0.55, (190, 226, 250)), (1, (220, 240, 250))]))
        for x, y, s in ((200, 120, 1.0), (900, 90, 0.8), (1150, 200, 0.6)):
            D.cloud(c, x, y, s)
        c.poly([(0, 470), (300, 420), (640, 450), (980, 400), (W, 440), (W, H), (0, H)], (150, 196, 120), ol=None)
        c.poly([(0, 560), (260, 520), (520, 545), (700, 600), (W, 560), (W, H), (0, H)], (120, 180, 100), ol=None)
        # the cats' cottage far off on the left
        c.rect(120, 470, 210, 530, (250, 228, 190), w=2)
        c.poly([(110, 472), (165, 430), (220, 472)], (190, 90, 70), w=2)
        c.rect(150, 490, 172, 512, (120, 190, 240), w=1.5)
        D.tree(c, 280, 540, 0.6)
        # the hilltop the cats stand on
        c.poly([(220, H), (420, 610), (640, 590), (900, 612), (1100, H)], (104, 166, 90), w=2.5)
        rng = np.random.default_rng(3)
        for _ in range(26):
            D.flower(c, rng.uniform(260, 1060), rng.uniform(640, 715), [(240, 90, 120), (255, 220, 90),
                     (250, 250, 250)][rng.integers(3)], s=0.6)
        D.tree(c, 1150, 640, 0.9)
        D.bush(c, 60, 680, 1.0)
        return c.img
    return cached("meadow", make)


def aegean_bg():
    WW = 3200

    def make():
        c = Canvas(sky_img([(0, (70, 150, 236)), (0.5, (170, 214, 250)), (0.6, (210, 232, 250)), (1, (40, 110, 190))],
                           w=WW), size=(WW, H))
        rng = np.random.default_rng(8)
        for _ in range(9):
            D.cloud(c, rng.uniform(0, WW), rng.uniform(60, 220), rng.uniform(0.5, 1.0))
        sea_band(c, 0, WW, 420, H, (36, 110, 196), (150, 210, 250), rng, n=420)
        c.rect(0, 420, WW, 432, (70, 140, 210), ol=None)
        # islands with white cube houses and blue domes
        for ix in (300, 1100, 1800, 2600, 3100):
            iw = rng.uniform(260, 420)
            ih = rng.uniform(60, 110)
            c.poly([(ix - iw / 2, 440), (ix - iw * 0.3, 440 - ih * 0.8), (ix, 440 - ih), (ix + iw * 0.25, 440 - ih * 0.7),
                    (ix + iw / 2, 440)], (196, 170, 130), w=2)
            for k in range(9):
                hx = ix - iw * 0.3 + rng.uniform(0, iw * 0.55)
                hy = 440 - ih * rng.uniform(0.1, 0.7)
                c.rect(hx, hy - 14, hx + 18, hy, (252, 250, 246), w=1.2)
                c.rect(hx + 6, hy - 8, hx + 11, hy, (40, 100, 190), ol=None)
            c.ellipse(ix + 10, 440 - ih * 0.85, 12, 10, (40, 100, 200), w=1.5)
            c.rect(ix - 2, 440 - ih * 0.85, ix + 22, 440 - ih * 0.85 + 16, (252, 250, 246), w=1.2)
            c.ellipse(ix, 446, iw * 0.45, 4, (220, 240, 255), ol=None)
        for sx in (700, 1500, 2300):                     # little sailing boats
            c.poly([(sx - 26, 560), (sx + 26, 560), (sx + 18, 574), (sx - 18, 574)], (250, 250, 250), w=2)
            c.poly([(sx, 556), (sx, 500), (sx + 26, 552)], (250, 250, 250), w=2)
        return c.img
    return cached("aegean", make), WW


def athens_bg():
    def make():
        c = Canvas(sky_img([(0, (96, 170, 236)), (0.6, (196, 226, 248)), (1, (230, 240, 246))]))
        for x, y, s in ((180, 110, 0.8), (1060, 80, 0.7)):
            D.cloud(c, x, y, s)
        c.poly([(0, 380), (180, 330), (380, 360), (620, 310), (900, 350), (1100, 320), (W, 350), (W, 460), (0, 460)],
               (176, 180, 200), ol=None)                  # Mount Hymettus, hazy
        rng = np.random.default_rng(11)
        city_blocks(c, rng, -20, W + 20, 470, 20, 50, [(236, 232, 226), (226, 222, 216), (244, 238, 228)])
        top = P.acropolis_rock(c, 820, 520, 640, 170, top_w=420, seed=4)
        P.parthenon(c, 860, top + 2, 260, 120, lw=2)
        P.temple_far(c, 690, top + 2, 50, 40, P.MARBLE, P.MARBLE_S, ol=OUT, lw=1.2, n=4)
        P.olive_tree(c, 600, 520, 0.4, seed=1)
        P.olive_tree(c, 1060, 520, 0.4, seed=2)
        rng = np.random.default_rng(12)
        city_blocks(c, rng, -20, W + 20, 600, 40, 120, [(252, 248, 240), (246, 236, 218), (250, 240, 226),
                                                        (238, 214, 186)], win=(80, 120, 170), p=0.3, ol=OUT)
        city_blocks(c, rng, -20, W + 20, 720, 60, 130, [(250, 246, 238), (244, 230, 210), (236, 220, 196)],
                    win=(60, 100, 160), p=0.3, ol=OUT)
        for x in (140, 420, 980):
            P.bougainvillea(c, x, 600, 34, 18, seed=x)
        return c.img
    return cached("athens_view", make)


def airship_crew(c, tl, t, ax, ay, s, cats=True, owl=True, sleep_w=False, w_eyes="open", l_eyes="open"):
    """The cats (and Sophia) sitting on the airship's deck. Call between part='back' and 'front'."""
    gy = ay + 142 * s
    if cats:
        kitty(c, tl, t, "luna", ax - 46 * s, gy, 0.36 * s / 0.9, 1, "sit", eyes=l_eyes, look=(1, 0.3))
        kitty(c, tl, t, "whiskers", ax + 20 * s, gy, 0.38 * s / 0.9, 1 if not sleep_w else -1, "sit", eyes=w_eyes)
    if owl:
        sophia(c, tl, t, ax - 10 * s, gy - 12 * s, 0.32 * s / 0.9, 1, sling=True)


def airship_close(tl, t):
    """Close on the gondola: the cats among the honey jars, clouds rushing past."""
    T = tl.t
    c = Canvas(sky_img([(0, (80, 160, 236)), (0.7, (180, 220, 250)), (1, (210, 234, 252))]))
    for k in range(5):
        x = (k * 340 - t * 120) % (W + 400) - 200
        D.cloud(c, x, 140 + 90 * (k % 3), 0.7 + 0.25 * (k % 2))
    if t >= T("a_kittens"):
        # far below: the blue sea
        c.rect(0, 600, W, H, (40, 120, 200), ol=None)
    ax, ay, s = 640, 230, 2.6
    bob = math.sin(t * 1.2) * 6
    P.airship(c, ax, ay + bob, s, t, part="back")
    gy = ay + bob + 142 * s
    hugging = T("a_honey") <= t < T("a_sea")
    kitty(c, tl, t, "luna", 470, gy, 1.0, 1, "sit", look=(1, -0.3) if not hugging else (1, 0),
          eyes="happy" if T("a_honey", 0.6) < t < T("a_sea") else "open")
    sophia(c, tl, t, 560, gy - 16, 0.85, 1, sling=True, look=(1, 0))
    wx = 760
    if hugging:
        P.honey_jar(c, wx + 70, gy - 4, 1.4)
    kitty(c, tl, t, "whiskers", wx, gy, 1.05, 1, "sit",
          eyes="happy" if hugging and not tl.talking("whiskers", t) else "open",
          head_dy=-6 if t >= T("a_kittens") and tl.talking("whiskers", t) else 0, look=(-1, 0))
    P.airship(c, ax, ay + bob, s, t, part="front")
    return c


def airship(tl, t):
    T = tl.t
    if T("a_honey") <= t < T("a_sea") or T("a_kittens") <= t < T("a_land"):
        return finish(airship_close(tl, t), tl, t, 0.45)
    if T("a_tale") <= t < T("a_kittens"):
        return finish(frieze_owl(tl, t), tl, t, 0.4)
    if T("a_sea") <= t < T("a_tale"):
        bg, WW = aegean_bg()
        u = tl.prog("a_sea", t)
        cam = lerp(0, WW - W, u * 0.9)
        c = view(bg, cam)
        ax = lerp(-200, 1500, u)
        ay = 220 + 16 * math.sin(t * 0.9)
        P.airship(c, ax, ay, 0.55, t, part="back")
        airship_crew(c, tl, t, ax, ay, 0.55)
        P.airship(c, ax, ay, 0.55, t, part="front")
        return finish(c, tl, t, 0.4)
    if t >= T("a_land"):
        c = Canvas(athens_bg().copy())
        ax = smooth(t, [(T("a_land"), -300), (T("a_look"), 330), (T("a_down", 0.15), 360)], r=0.5)
        ay = smooth(t, [(T("a_land"), 160), (T("a_look"), 210), (T("a_down", 0.1), 250)], r=0.5)
        ay += 6 * math.sin(t * 1.1)
        s = 0.7
        dropping = t >= T("a_down", 0.15)
        rope = 0 if not dropping else 240 * ease(tl.prog("a_down", t, 0.15, 0.35))
        P.airship(c, ax, ay, s, t, part="back", rope=rope)
        on_deck = not dropping or t < T("a_down", 0.35)
        airship_crew(c, tl, t, ax, ay, s, cats=on_deck, owl=on_deck, l_eyes="wide" if t >= T("a_look") else "open")
        P.airship(c, ax, ay, s, t, part="front")
        if dropping and not on_deck:
            rx = ax + 70 * s
            for k, (who, lag) in enumerate((("luna", 0.0), ("whiskers", 0.12))):
                u = clamp((tl.prog("a_down", t, 0.35, 0.9) - lag) / 0.8)
                if 0 < u < 1:
                    y = lerp(ay + 150 * s, ay + 150 * s + 240 * s, u)
                    D.cat(c, rx - 14, y + 40, PAL[who], 0.3, 1, "leap", t=t, seed=SEED[who], eyes="wide")
                    if who == "luna":
                        P.owl(c, rx - 18, y + 14, 0.18, 1, t, sling=True)
        return finish(c, tl, t, 0.4)
    # ---- the meadow at home: the airship comes down, the cats climb the rope
    c = Canvas(meadow_bg().copy())
    s = 0.9
    ax = smooth(t, [(T("a_open"), -300), (T("a_narr", 0.8), 520), (T("a_climb", 0.6), 540), (T("a_climb", 1.0), 1500)],
                r=0.4)
    ay = smooth(t, [(T("a_open"), 120), (T("a_narr", 0.8), 170), (T("a_climb", 0.6), 170), (T("a_climb", 1.0), -60)],
                r=0.4)
    ay += 5 * math.sin(t * 1.0)
    rope = 0.0
    if t >= T("a_narr", 0.7):
        rope = (600 - (ay + 150 * s)) / s * ease(tl.prog("a_narr", t, 0.7, 1.0))
    climb = tl.prog("a_climb", t, 0.0, 0.55)
    P.airship(c, ax, ay, s, t, part="back", rope=rope)
    in_ship = climb >= 1
    if in_ship:
        airship_crew(c, tl, t, ax, ay, s)
    P.airship(c, ax, ay, s, t, part="front")
    rx = ax + 70 * s
    if not in_ship:
        if climb <= 0:
            # standing on the hill, looking up at the ship
            look_up = t >= T("a_narr", 0.3)
            kitty(c, tl, t, "luna", 560, 606, 0.9, 1, "stand", look=(1, -1) if look_up else (1, 0),
                  eyes="wide" if T("a_narr", 0.4) < t < T("a_rope") else "open")
            owl_on_luna(c, tl, t, 560, 606, 0.9, 1, "stand", look=(1, -1))
            kitty(c, tl, t, "whiskers", 720, 610, 0.95, -1, "sit", look=(1, -1) if look_up else (1, 0),
                  eyes="open" if look_up else "closed")
        else:
            for who, lag, x0 in (("luna", 0.0, 560), ("whiskers", 0.35, 720)):
                u = clamp((climb - lag) / 0.65)
                if u <= 0:
                    kitty(c, tl, t, who, x0, 608, 0.9, -1 if who == "whiskers" else 1, "sit", look=(1, -1),
                          eyes="wide")
                    continue
                if u >= 1:
                    continue
                if u < 0.25:
                    v = u / 0.25
                    x = lerp(x0, rx - 16, v)
                    y = lerp(606, 560, v) + arc_y(v, 60)
                else:
                    v = (u - 0.25) / 0.75
                    x = rx - 16 + 4 * math.sin(v * 20)
                    y = lerp(560, ay + 160 * s + 40, v)
                D.cat(c, x, y, PAL[who], 0.7, 1, "leap", t=t, seed=SEED[who], eyes="wide" if who == "whiskers" else "open",
                      head_dy=0)
                if who == "luna":
                    P.owl(c, x - 30, y - 50, 0.4, 1, t, sling=True, eyes="wide")
    return finish(c, tl, t, 0.35)


def _stub(tl, t):
    return Canvas(bg=(60, 60, 60))


SCENE_FUNCS = {"title": title, "storm": storm, "airship": airship}
for _n in ("plaka", "yogurt", "theatre", "agora", "acropolis", "home"):
    SCENE_FUNCS.setdefault(_n, _stub)
CONTINUOUS = set()
EXTRA_CUTS = ["s_myth", "s_dinner", "a_honey", "a_sea", "a_tale", "a_kittens", "a_land"]
