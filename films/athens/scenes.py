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
        P.temple_far(c, 690, top + 2, 70, 50, (250, 230, 210), (210, 170, 160), ol=OUT, lw=1.5, n=4)
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
    kitty(c, tl, t, "luna", 540, 598, 1.0, 1, "sit", look=(1, -1), mouth=0, tail=math.sin(t * 1.5))
    kitty(c, tl, t, "whiskers", 720, 598, 1.05, -1, "sit", look=(1, -1), mouth=0)
    # an owl on top of the broken column
    P.owl(c, 1040, 446, 0.75, -1, t, eyes="open", look=(-1, 0))
    c.tint = None
    k = ease(tl.prog("t_open", t, 0.0, 0.6))
    c.text(330, 90 - 30 * (1 - k), "Whiskers and the", 42, mix((90, 100, 170), (255, 246, 220), k), stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(330, 166, "OWL OF ATHENS", 24 + 46 * k2, mix((90, 100, 170), (255, 222, 130), k2), stroke=5 * k2)
    if k2 > 0:
        P.meander(c, 330 - 260 * k2, 330 + 260 * k2, 208, 16, col=mix((90, 100, 170), (255, 236, 200), k2))
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
                                                        (238, 214, 186)], win=(80, 120, 170), p=0.12, ol=OUT)
        city_blocks(c, rng, -20, W + 20, 720, 60, 130, [(250, 246, 238), (244, 230, 210), (236, 220, 196)],
                    win=(60, 100, 160), p=0.12, ol=OUT)
        for x in (140, 420, 980):
            P.bougainvillea(c, x, 600, 34, 18, seed=x)
        return c.img
    return cached("athens_view", make)


def airship_crew(c, tl, t, ax, ay, s, cats=True, owl=True, sleep_w=False, w_eyes="open", l_eyes="open"):
    """The cats (and Sophia) sitting on the airship's deck. Call between part='back' and 'front'."""
    gy = ay + 124 * s
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
    gy = ay + bob + 122 * s
    hugging = T("a_honey") <= t < T("a_sea")
    kitty(c, tl, t, "luna", 470, gy, 1.0, 1, "sit", look=(1, -0.3) if not hugging else (1, 0),
          eyes="happy" if T("a_honey", 0.6) < t < T("a_sea") else "open")
    sophia(c, tl, t, 580, gy - 30, 0.85, 1, sling=True, look=(1, 0))
    wx = 720
    kitty(c, tl, t, "whiskers", wx, gy, 1.05, 1, "sit",
          eyes="happy" if hugging and not tl.talking("whiskers", t) else "open",
          head_dy=-6 if t >= T("a_kittens") and tl.talking("whiskers", t) else 0, look=(-1, 0))
    for jx, js in ((830, 1.3), (880, 1.2), (405, 1.2)):
        P.honey_jar(c, jx, gy + 4, js)
    P.airship(c, ax, ay + bob, s, t, part="front", jars=False)
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
        ax = lerp(150, 1300, u)
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



# ======================================================================= plaka

PW = 1700                    # one loop of the Plaka street (the maze goes round and round)
STAND_X = 820
STREET_Y = 622


def plaka_far():
    def make():
        c = Canvas(sky_img([(0, (90, 168, 238)), (0.5, (176, 220, 250)), (1, (220, 238, 250))]))
        D.cloud(c, 200, 90, 0.8)
        D.cloud(c, 560, 60, 0.6)
        # the Acropolis looming over the rooftops: so close, yet so far
        top = P.acropolis_rock(c, 900, 470, 900, 230, top_w=600, seed=6)
        P.parthenon(c, 960, top + 2, 360, 150, lw=2.5)
        P.temple_far(c, 720, top + 2, 60, 46, P.MARBLE, P.MARBLE_S, ol=OUT, lw=1.5, n=4)
        P.olive_tree(c, 560, 380, 0.5, seed=4)
        P.olive_tree(c, 1260, 390, 0.5, seed=5)
        return c.img
    return cached("plaka_far", make)


def plaka_layer():
    def make():
        c = rgba(PW + W, H)
        rng = np.random.default_rng(21)
        walls = [P.WHITEWASH, P.OCHRE, (246, 214, 190), P.WHITEWASH, (236, 226, 200), (250, 220, 160)]
        shutters = [P.GBLUE, (60, 140, 110), P.GBLUE, (170, 70, 60), P.GBLUE_L]
        # houses: the same sequence is drawn twice so the street loops seamlessly
        plan = []
        x = 0
        k = 0
        while x < PW:
            w = rng.uniform(170, 260)
            if x + w > PW - 120:
                w = PW - x
            plan.append((x, x + w, rng.uniform(230, 330), walls[k % len(walls)], shutters[k % len(shutters)],
                         "tile" if rng.random() < 0.4 else "flat", rng.random() < 0.35, rng.random() < 0.5, k))
            x += w
            k += 1
        for off in (0, PW):
            hr = np.random.default_rng(5)
            for (x0, x1, h, wall, sh, roof, bal, boug, k) in plan:
                if x0 + off > PW + W + 50:
                    continue
                P.house(c, x0 + off, x1 + off, STREET_Y - 12, h, wall, hr, door=(x1 - x0) > 150, roof=roof,
                        shutter=sh, balcony=bal, boug=boug, seed=k,
                        sign="TAVERNA" if k == 2 else None)
            # cobbled street
            c.rect(off, STREET_Y - 14, off + PW, H + 10, (214, 204, 190), w=2.5)
            for y in range(STREET_Y + 6, H, 22):
                c.line([(off, y), (off + PW, y)], (190, 180, 166), 2, cap=False)
            sr = np.random.default_rng(9)
            for _ in range(140):
                cx, cy = off + sr.uniform(0, PW), sr.uniform(STREET_Y, H)
                c.ellipse(cx, cy, sr.uniform(8, 16), 4, (200, 190, 176), ol=None)
            # pots, lamps and steps along the walls
            for px in (120, 560, 1120, 1480):
                P.basil_pot(c, off + px, STREET_Y - 8, 0.8)
            for lx in (380, 1300):
                c.line([(off + lx, STREET_Y - 260), (off + lx + 30, STREET_Y - 260)], (60, 60, 70), 3)
                c.rect(off + lx + 22, STREET_Y - 258, off + lx + 40, STREET_Y - 232, (255, 236, 170), w=2, r=3)
            # the souvlaki stand, always in the same spot
            P.souvlaki_stand(c, off + STAND_X, STREET_Y + 4, 1.0, smoke=False)
        return c.img
    return cached("plaka_layer", make)


def plaka(tl, t):
    T = tl.t
    c = Canvas(plaka_far().copy())
    # camera: still while they arrive, then twice round the maze, back at the stand
    u = ease(tl.prog("p_maze", t, 0.05, 0.95))
    cam = 2 * PW * u - 120
    camm = cam % PW
    paste_layer(c, plaka_layer(), camm)
    stand_sx = STAND_X - camm if STAND_X - camm > -300 else STAND_X - camm + PW
    # smoke from the grill (drawn live)
    for k in range(4):
        uu = (t * 0.35 + k / 4) % 1.0
        c.circle(stand_sx - 20 + k * 14 + 18 * math.sin(t + k), STREET_Y - 120 - uu * 90, 8 + 14 * uu,
                 mix((230, 230, 236), (250, 246, 236), uu), ol=None)
    walking = T("p_maze", 0.05) <= t < T("p_maze", 0.95)
    # arrive from the left
    lx = smooth(t, [(T("p_narr"), -160), (T("p_narr", 0.7), 430), (T("p_maze"), 430), (T("p_maze", 0.05), 450),
                    (T("p_maze", 0.95), 450), (T("p_three"), 540)])
    wx = smooth(t, [(T("p_narr", 0.1), -120), (T("p_narr", 0.8), 620), (T("p_maze"), 640), (T("p_maze", 0.05), 680),
                    (T("p_maze", 0.95), 680), (T("p_three"), 760)])
    stepping = walking or abs(moving(t, [(T("p_narr"), -160), (T("p_narr", 0.7), 430)])) > 20 \
        or T("p_maze", 0.95) <= t < T("p_three")
    wpose = "walk" if (walking or abs(moving(t, [(T("p_narr", 0.1), -120), (T("p_narr", 0.8), 620)])) > 20
                       or T("p_maze", 0.95) <= t < T("p_three")) else "stand"
    phase = cam / 12
    lpose = "walk" if stepping else "stand"
    lface = 1
    if T("p_ask") <= t < T("p_never", 1):
        lpose = "stand"
    kitty(c, tl, t, "luna", lx, STREET_Y + 30, 0.9, lface, lpose, walk=(lx + cam) / 12,
          eyes="wide" if T("p_three") <= t < T("p_three", 1) else "open")
    owl_on_luna(c, tl, t, lx, STREET_Y + 30, 0.9, lface, lpose, walk=(lx + cam) / 12,
                look=(1, 0) if not T("p_ask") <= t < T("p_ask", 1) else (1, 0))
    sniff = t >= T("p_purpose", 0.5)
    wface = 1
    if T("p_ask") <= t < T("p_never", 1) or T("p_three") <= t < T("p_purpose", 0.5):
        wface = -1
    weyes = "happy" if sniff else ("closed" if T("p_never") <= t < T("p_never", 0.6) else "open")
    kitty(c, tl, t, "whiskers", wx, STREET_Y + 32, 0.95, wface, wpose, walk=(wx + cam) / 12 + 1,
          eyes=weyes, head_dy=-8 if sniff else 0, look=(1, -0.5))
    if sniff:                                              # the smell, wafting to his nose
        for k in range(3):
            uu = (t * 0.6 + k / 3) % 1.0
            sx = lerp(stand_sx - 30, wx + 80, uu)
            sy = STREET_Y - 120 + 40 * uu + 10 * math.sin(uu * 9 + k)
            c.line([(sx, sy), (sx + 10, sy - 6), (sx + 20, sy)], (255, 255, 255), 3)
    # a counter for the third pass
    if T("p_three") <= t < T("p_purpose"):
        k = ease(tl.prog("p_three", t, 0.0, 0.3))
        c.text(stand_sx, STREET_Y - 300, "x3", 20 + 30 * k, (255, 240, 200), stroke=4)
    return finish(c, tl, t, 0.4)


# ====================================================================== yogurt

BOWL_X = 760
YARD_Y = 596


def yard_bg():
    def make():
        c = Canvas(sky_img([(0, (90, 168, 238)), (0.5, (176, 220, 250)), (1, (220, 238, 250))]))
        D.cloud(c, 160, 80, 0.7)
        top = P.acropolis_rock(c, 900, 420, 820, 250, top_w=520, seed=7)
        P.parthenon(c, 940, top + 2, 330, 150, lw=2.5)
        P.olive_tree(c, 560, 330, 0.5, seed=2)
        # neighbouring rooftops
        c.rect(-10, 300, 260, 420, (246, 226, 200), w=2.5)
        c.poly([(-20, 302), (120, 250), (270, 302)], (200, 104, 70), w=2.5)
        c.rect(1100, 280, W + 10, 420, (250, 244, 232), w=2.5)
        c.ellipse(1190, 282, 46, 34, (40, 100, 200), w=2.5)
        c.rect(1140, 282, 1240, 300, (250, 244, 232), ol=None)
        c.line([(1190, 248), (1190, 230)], OUT, 2, cap=False)
        c.line([(1182, 238), (1198, 238)], OUT, 2, cap=False)
        # back wall of the little courtyard
        c.rect(-10, 400, W + 10, YARD_Y - 6, P.WHITEWASH, w=3)
        c.rect(-10, 392, W + 10, 408, (236, 230, 216), w=2.5)
        rng = np.random.default_rng(4)
        for _ in range(18):                               # old plaster patches
            x, y = rng.uniform(0, W), rng.uniform(420, 600)
            c.rect(x, y, x + rng.uniform(20, 50), y + rng.uniform(10, 20), (238, 232, 218), ol=None, r=4)
        # blue door with a bougainvillea arch
        c.rect(170, 450, 290, YARD_Y - 6, P.GBLUE, w=3)
        c.ellipse(230, 450, 60, 34, P.GBLUE, w=3)
        c.rect(172, 450, 288, 480, P.GBLUE, ol=None)
        c.line([(230, 418), (230, YARD_Y - 8)], mix(P.GBLUE, (0, 0, 0), 0.3), 2, cap=False)
        c.circle(262, 560, 4, (240, 200, 90), w=1.5)
        P.bougainvillea(c, 230, 400, 150, 46, seed=1)
        P.bougainvillea(c, 110, 470, 50, 90, seed=2)
        P.bougainvillea(c, 360, 450, 50, 60, seed=3)
        # window with shutters and geraniums
        c.rect(560, 440, 640, 530, (60, 70, 90), w=2.5)
        c.rect(530, 440, 560, 530, P.GBLUE, w=2.5)
        c.rect(640, 440, 670, 530, P.GBLUE, w=2.5)
        c.rect(550, 530, 650, 542, (230, 224, 210), w=2)
        for k in range(4):
            c.circle(565 + k * 22, 524, 9, (230, 60, 70) if k % 2 else (250, 160, 60), w=1.5)
        # string of lights across the yard
        pts = [(x, 412 + 30 * math.sin(math.pi * x / W)) for x in range(0, W + 1, 40)]
        c.line(pts, (60, 60, 70), 2, cap=False)
        for k, (x, y) in enumerate(pts[1:-1]):
            c.circle(x, y + 8, 6, [(255, 220, 120), (255, 170, 120), (180, 220, 255)][k % 3], w=1.5)
        # taverna corner
        P.taverna_table(c, 1080, YARD_Y + 30, 1.4)
        P.chair(c, 1220, YARD_Y + 34, 1.2)
        P.chair(c, 950, YARD_Y + 34, 1.2, col=P.GBLUE_L)
        P.basil_pot(c, 420, YARD_Y, 1.0)
        P.basil_pot(c, 470, YARD_Y + 4, 0.8)
        # stone floor
        c.rect(-10, YARD_Y - 6, W + 10, H + 10, (226, 216, 200), w=2.5)
        for y in range(YARD_Y + 14, H, 26):
            c.line([(0, y), (W, y)], (204, 192, 176), 2, cap=False)
        for x in range(0, W, 90):
            for k, y in enumerate(range(YARD_Y - 6, H, 26)):
                c.line([(x + (45 if k % 2 else 0), y), (x + (45 if k % 2 else 0), y + 26)], (204, 192, 176), 2,
                       cap=False)
        # a doorstep where somebody kind leaves food for the cats
        c.rect(BOWL_X - 90, YARD_Y + 30, BOWL_X + 90, YARD_Y + 46, (240, 236, 226), w=2)
        return c.img
    return cached("yard", make)


def yogurt(tl, t):
    T = tl.t
    c = Canvas(yard_bg().copy())
    dive0, splat = T("y_dive", 0.3), T("y_dive", 0.55)
    up = T("y_dive", 0.85)
    eaten = 0.0 if t < splat else 0.6 + 0.4 * tl.prog("y_lick", t)
    P.yogurt_bowl(c, BOWL_X, YARD_Y + 32, 1.3, eaten=eaten, honey=t < splat)
    # ---- Luna and Sophia
    lkeys = [(T("y_narr"), -140), (T("y_narr", 0.6), 390), (T("y_go", 0.3), 390), (T("y_go", 1.0), 1500)]
    lx = smooth(t, lkeys)
    lmov = abs(moving(t, lkeys)) > 20
    laugh = T("y_beard") <= t < T("y_lick")
    lpose = "walk" if lmov else ("sit" if T("y_dive", 0.7) <= t < T("y_go", 0.3) else "stand")
    kitty(c, tl, t, "luna", lx, YARD_Y + 40, 1.15, 1, lpose, walk=lx / 12, eyes="happy" if laugh and
          not tl.talking("luna", t) else ("wide" if splat <= t < up else "open"))
    if t < T("y_dive", 0.7) or t >= T("y_go", 0.3):
        owl_on_luna(c, tl, t, lx, YARD_Y + 40, 1.15, 1, lpose, walk=lx / 12)
    else:
        # Sophia hops down to laugh at Whiskers
        sophia(c, tl, t, 575, YARD_Y + 40, 0.9, 1, sling=True,
               eyes="happy" if laugh else "open",
               hop=abs(math.sin(t * 9)) * 10 if T("y_beard") <= t < T("y_beard", 1) + 0.6 else 0)
    # ---- Whiskers
    if t < dive0:
        wx = smooth(t, [(T("y_narr", 0.1), -120), (T("y_narr", 0.75), 560)])
        mv = abs(moving(t, [(T("y_narr", 0.1), -120), (T("y_narr", 0.75), 560)])) > 20
        pose = "walk" if mv else ("crouch" if t > T("y_dive", 0.1) else "stand")
        kitty(c, tl, t, "whiskers", wx, YARD_Y + 44, 1.2, 1, pose, walk=wx / 12, eyes="happy" if mv else "wide",
              head_dy=-10 if mv else 0)
        if mv:
            for k in range(3):
                uu = (t * 0.6 + k / 3) % 1.0
                sx = lerp(BOWL_X, wx + 80, uu)
                sy = YARD_Y - 30 - 50 * uu
                c.line([(sx, sy), (sx + 10, sy - 6), (sx + 20, sy)], (255, 250, 230), 3)
    elif t < splat:
        u = (t - dive0) / (splat - dive0)
        D.cat(c, lerp(560, BOWL_X - 40, u), YARD_Y + 44 + arc_y(u, 120), D.WHISKERS, 1.2, 1, "leap", t=t,
              eyes="happy", mouth=0.6)
    elif t < up:
        # head in the bowl: only his bottom and tail stick out, wiggling
        wig = math.sin(t * 14) * 6
        c.push(BOWL_X - 30, YARD_Y + 20)
        D._tail(c, (-40 + wig, -30), 60, math.sin(t * 9), D.WHISKERS["body"])
        c.ellipse(-20 + wig * 0.5, -30, 46, 32, D.WHISKERS["body"])
        for dx in (-34, -16):
            c.line([(dx + wig * 0.5, -56), (dx + 5, -42)], D.WHISKERS["dark"], 5)
        c.pop()
        P.yogurt_bowl(c, BOWL_X, YARD_Y + 32, 1.3, eaten=0.3, honey=False)
        for k in range(8):                                 # yogurt splashes
            a = math.radians(200 + k * 18)
            dt = t - splat
            r = 40 + dt * 260
            if dt < 0.6:
                c.circle(BOWL_X + math.cos(a) * r, YARD_Y - 10 + math.sin(a) * r * 0.6 + 200 * dt * dt, 7,
                         P.YOGURT, w=2)
    else:
        lick = tl.prog("y_lick", t)
        size = 1.25 - 0.55 * lick
        thinking = T("y_think") <= t < T("y_think", 1)
        wx = smooth(t, [(T("y_go", 0.1), 650), (T("y_go", 0.9), 1500)])
        mv = t >= T("y_go", 0.12)
        pose = "walk" if mv else "sit"
        mouth = tl.mouth("whiskers", t)
        if T("y_lick") <= t < T("y_lick", 1):
            mouth = 0.5 + 0.5 * abs(math.sin(t * 8))
        head_dy = 0
        look = (1, 0)
        if T("y_up") <= t < T("y_go"):
            head_dy, look = -10, (1, -1)
        kitty(c, tl, t, "whiskers", wx, YARD_Y + 44, 1.2, 1 if not thinking else -1, pose, walk=wx / 12,
              eyes="closed" if thinking else "open", mouth=mouth, head_dy=head_dy, look=look)
        if not mv:
            P.beard(c, wx, YARD_Y + 44, 1.2, 1 if not thinking else -1, "sit", head_dy, col=P.YOGURT, t=t,
                    drip=True, size=size)
        if thinking:
            k = ease(tl.prog("y_think", t, 0.4, 0.6))
            if k > 0.02:
                bx, by = 520, 300
                for f, r in ((0.3, 8), (0.6, 12)):
                    c.circle(lerp(600, bx, f), lerp(470, by + 60, f), r * k, (255, 255, 255), w=2)
                c.circle(bx, by, 70 * k, (255, 255, 255), w=2.5)
                P.honey_jar(c, bx, by + 30 * k, 1.3 * k)
    return finish(c, tl, t, 0.4)



# ===================================================================== theatre

SEAT_C = (640, 760)          # centre of the seat arcs (below the frame)
TOP_ROW = 250
STAGE_Y = 640


def theatre_bg():
    def make():
        c = Canvas(sky_img([(0, (110, 170, 230)), (0.5, (196, 220, 240)), (1, (230, 236, 240))]))
        # the Acropolis rock rising behind, with the Parthenon peeking over the top
        top = P.acropolis_rock(c, 760, 300, 1300, 260, top_w=900, seed=9)
        P.parthenon(c, 900, top + 2, 300, 130, lw=2)
        # marble seats: rows of arcs rising from the stage
        cx, cy = SEAT_C
        rows = 10
        for k in range(rows, -1, -1):
            r0 = 230 + k * 40
            rx, ry = r0 * 1.25, r0
            col = mix(P.MARBLE, P.MARBLE_S, 0.25 if k % 2 else 0.0)
            c.ellipse(cx, cy, rx, ry, col, w=2)
            c.ellipse(cx, cy - 10, rx - 2, ry - 12, mix(col, P.MARBLE_D, 0.35), ol=None)
        # stairways between the seat blocks
        for a in (-60, -35, -12, 12, 35, 60):
            ar = math.radians(a - 90)
            pts = [(cx + math.cos(ar) * 230 * 1.25, cy + math.sin(ar) * 230),
                   (cx + math.cos(ar) * 630 * 1.25, cy + math.sin(ar) * 630)]
            c.line(pts, P.MARBLE_D, 7, cap=False)
            c.line(pts, mix(P.MARBLE, P.MARBLE_S, 0.5), 3, cap=False)
        # the great arched wall on both sides (the Odeon's stage building)
        for side in (-1, 1):
            x0 = 0 if side < 0 else W - 230
            stone = (214, 176, 140)
            c.rect(x0 - 10 if side < 0 else x0, 60, x0 + 230 + (0 if side < 0 else 10), STAGE_Y, stone, w=3)
            for row, (yy, hh) in enumerate(((110, 120), (270, 130), (440, 150))):
                for k in range(2):
                    ax = x0 + 60 + k * 110
                    c.rect(ax - 32, yy, ax + 32, yy + hh, (110, 150, 210), w=2.5)
                    c.ellipse(ax, yy, 32, 30, (110, 150, 210), w=2.5)
                    c.rect(ax - 30, yy, ax + 30, yy + 10, (110, 150, 210), ol=None)
            for yy in range(80, STAGE_Y, 40):
                c.line([(x0, yy), (x0 + 230, yy)], (190, 150, 120), 1.5, cap=False)
            c.rect(x0 - 10 if side < 0 else x0, 60, x0 + 230 + (0 if side < 0 else 10), 74, (226, 192, 156), w=2.5)
        # the stage floor: a half circle of grey and white marble
        c.rect(-10, STAGE_Y - 10, W + 10, H + 10, (210, 204, 196), w=3)
        c.ellipse(640, STAGE_Y + 120, 520, 150, (236, 232, 224), w=3)
        for k in range(1, 6):
            c.ellipse(640, STAGE_Y + 120, 520 - k * 90, 150 - k * 26, (236, 232, 224) if k % 2 == 0
                      else (196, 190, 184), w=2)
        return c.img
    return cached("theatre_bg", make)


def seat_y(row):
    """y of a seat row's front edge at the centre (row 0 = lowest)."""
    return SEAT_C[1] - (230 + row * 40) + 10


def echo_words(c, t, t0, word, x, y):
    """Fading copies of a shouted word, bouncing back off the seats."""
    for k in range(3):
        dt = t - (t0 + k * 0.45)
        if 0 <= dt < 1.4:
            a = 1 - dt / 1.4
            c.text(x + (k - 1) * 220, y - k * 30 - dt * 20, word, 30 - k * 6,
                   mix((236, 232, 224), (90, 100, 160), a), stroke=2 * a, stroke_fill=mix((236, 232, 224), OUT, a))


def theatre(tl, t):
    T = tl.t
    c = Canvas(theatre_bg().copy())
    soc_down = t >= T("th_lost")
    # ---- Socrates: on the top row, unnoticed, until the 'echo' answers back
    if not soc_down:
        sy = seat_y(10)
        stand = t >= T("th_reveal", 0.55)
        kitty(c, tl, t, "socrates", 640, sy, 0.42, -1, "stand" if stand else "sleep" if t < T("th_way") else "sit",
              look=(1, 1), eyes="closed" if t < T("th_way") else "open")
    else:
        kitty(c, tl, t, "socrates", 960, seat_y(1), 0.95, -1, "sit", look=(1, 0.4),
              eyes="happy" if tl.talking("whiskers", t) else "open")
    # ---- our cats on the stage
    lkeys = [(T("th_narr"), -140), (T("th_narr", 0.8), 420)]
    wkeys = [(T("th_narr", 0.1), -120), (T("th_narr", 0.9), 620)]
    lx, wx = smooth(t, lkeys), smooth(t, wkeys)
    lmv, wmv = abs(moving(t, lkeys)) > 20, abs(moving(t, wkeys)) > 20
    shout = tl.talking("whiskers", t) and t < T("th_argue")
    look_up = T("th_dont") <= t < T("th_lost")
    lpose = "walk" if lmv else "stand"
    kitty(c, tl, t, "luna", lx, STAGE_Y + 40, 1.0, 1, lpose, walk=lx / 12,
          look=(1, -1) if look_up else ((1, 0.5) if soc_down else (1, 0)),
          eyes="wide" if T("th_dont") <= t < T("th_dont", 1) + 1.0 else "open")
    owl_on_luna(c, tl, t, lx, STAGE_Y + 40, 1.0, 1, lpose, walk=lx / 12, look=(1, -1) if look_up else (1, 0),
                eyes="wide" if T("th_dont") <= t < T("th_argue") else "open")
    wface = 1 if not soc_down else 1
    kitty(c, tl, t, "whiskers", wx, STAGE_Y + 42, 1.05, wface, "walk" if wmv else ("stand" if not soc_down else "sit"),
          walk=wx / 12, head_dy=-10 if shout else 0,
          look=(1, -1) if (look_up or shout) else (1, 0),
          eyes="wide" if T("th_dont") <= t < T("th_argue") else ("happy" if T("th_echo1") <= t < T("th_way") else "open"))
    if shout:                                     # sound rings rolling up into the seats
        for k in range(3):
            u = ((t - T("th_hello")) * 1.4 + k / 3) % 1.0
            c.arc(wx + 90, STAGE_Y - 80, 40 + 300 * u, 30 + 200 * u, 200, 340, mix((255, 255, 255), (220, 220, 230), u),
                  3 * (1 - u) + 1)
    # ---- the echoes
    echo_words(c, t, T("th_echo1"), "hello!", 640, 380)
    if T("th_echo2") <= t:
        echo_words(c, t, T("th_echo2"), "...don't!", 640, 380)
    # ---- zoom up to the top row on the reveal
    z = 1.0
    if T("th_reveal") <= t < T("th_lost"):
        z = 1 + 1.6 * ease(tl.prog("th_reveal", t, 0.0, 0.5))
    if z > 1.001:
        c = zoom(c, 640, seat_y(10) - 30, z)
    return finish(c, tl, t, 0.4)


# ======================================================================= agora

GROUND = 640


def agora_bg():
    def make():
        c = Canvas(sky_img([(0, (80, 70, 140)), (0.35, (220, 120, 120)), (0.6, (255, 176, 110)),
                            (0.75, (255, 214, 140)), (1, (255, 214, 140))]))
        soft_glow(c, 260, 400, 320, (255, 220, 150), 0.7)
        c.circle(260, 410, 48, (255, 232, 160), ol=None)
        # hill with the Temple of Hephaestus on the left; the Acropolis glowing on the right
        c.poly([(0, 470), (120, 410), (420, 420), (560, 470)], (170, 110, 110), ol=None)
        P.temple_far(c, 260, 418, 220, 120, (250, 200, 160), (200, 140, 120), ol=OUT, lw=1.8, n=6)
        top = P.acropolis_rock(c, 1000, 480, 700, 210, top_w=430, col=(214, 140, 104), shade=(180, 110, 90),
                               dark=(150, 90, 80), green=(140, 120, 90), seed=10)
        P.parthenon(c, 1040, top + 2, 280, 120, col=(255, 222, 190), shade=(236, 186, 160), dark=(200, 140, 130),
                    lw=2)
        c.rect(-10, 470, W + 10, 520, (190, 140, 120), ol=None)
        P.olive_tree(c, 600, 520, 0.9, seed=11, leaf=(130, 130, 90), leaf_l=(180, 170, 130))
        P.olive_tree(c, 80, 540, 1.0, seed=12, leaf=(130, 130, 90), leaf_l=(180, 170, 130))
        # the dusty ground of the old market place
        c.rect(-10, 520, W + 10, H + 10, (226, 186, 150), w=2.5)
        rng = np.random.default_rng(3)
        for _ in range(60):
            x, y = rng.uniform(0, W), rng.uniform(530, H)
            c.ellipse(x, y, rng.uniform(4, 12), 2.5, (206, 166, 132), ol=None)
        # ruins: a row of old columns, blocks and a fallen drum
        for x, h in ((380, 150), (470, 230), (1180, 200)):
            P.broken_column(c, x, 560, h, 22, col=(250, 226, 200), shade=(222, 190, 166))
        P.marble_block(c, 190, 600, 190, 60, col=(250, 226, 200), shade=(222, 190, 166))
        P.marble_block(c, 1070, 590, 170, 50, col=(250, 226, 200), shade=(222, 190, 166))
        P.broken_column(c, 330, 700, 200, 26, col=(250, 226, 200), shade=(222, 190, 166), lying=True)
        P.broken_column(c, 900, 630, 90, 30, col=(250, 226, 200), shade=(222, 190, 166), top_break=False)
        return c.img
    return cached("agora_bg", make)


LOUNGERS = [(190, 540, 0, "sleep", 0.7, 1), (1070, 540, 1, "sleep", 0.7, -1), (470, 330, 2, "sleep", 0.5, 1),
            (1180, 360, 3, "sit", 0.5, -1), (120, 702, 4, "sleep", 0.8, 1)]


def agora(tl, t):
    T = tl.t
    c = Canvas(agora_bg().copy())
    c.tint = SUNSET_TINT
    leave = T("ag_cats", 0.1)
    # ---- the lounging cats of Athens on the ruins
    for k, (x, y, pal, pose, s, face) in enumerate(LOUNGERS):
        if t < T("ag_follow", 0.6):
            P.street_cat(c, x, y, pal, s, face, pose, t=t + k, eyes="closed" if pose == "sleep" else "open")
        else:
            u = clamp((t - leave - k * 0.35) / 4.0)
            if u <= 0:
                P.street_cat(c, x, y, pal, s, 1, "stand", t=t + k)
            else:
                xx = lerp(x, 1500, u)
                yy = lerp(y, GROUND + 30, min(1, u * 3))
                P.street_cat(c, xx, yy, pal, max(s, 0.75), 1, "walk", t=t + k, walk=xx / 10)
    # ---- Socrates on the short column
    if t < leave:
        kitty(c, tl, t, "socrates", 900, 552, 0.85, -1, "sit", look=(1, 0.3),
              eyes="closed" if T("ag_nothing", 0.2) <= t < T("ag_nothing", 0.5) else "open")
    else:
        u = clamp((t - leave) / 4.0)
        kitty(c, tl, t, "socrates", lerp(900, 1500, u), lerp(552, GROUND + 40, min(1, u * 4)), 0.9, 1, "walk",
              walk=t * 4)
    # ---- Luna, Sophia, Whiskers
    gone = clamp((t - T("ag_cats", 0.35)) / 3.6)
    lx = lerp(520, 1500, gone)
    wx = lerp(680, 1600, gone)
    lpose = "walk" if gone > 0 else "sit"
    sad = T("ag_sad") <= t < T("ag_hoo")
    kitty(c, tl, t, "luna", lx, GROUND + 50, 1.0, 1, lpose, walk=lx / 12,
          look=(1, 0) if not T("ag_nothing") <= t < T("ag_ask") else (1, -0.2),
          eyes="happy" if T("ag_hoo") <= t < T("ag_hoo", 1) else "open")
    if gone <= 0:
        sophia(c, tl, t, 410, GROUND + 50, 0.85, 1, sling=True, look=(1, 0),
               eyes="closed" if sad and not tl.talking("sophia", t) and t < T("ag_admit") else "open",
               hop=abs(math.sin(t * 9)) * 8 if tl.talking("sophia", t) and t >= T("ag_hoo") else 0)
    else:
        owl_on_luna(c, tl, t, lx, GROUND + 50, 1.0, 1, "walk", walk=lx / 12)
    admit = T("ag_quiet", 0.5) <= t < T("ag_admit", 1)
    wface = -1 if T("ag_quiet", 0.4) <= t < T("ag_admit", 1) or T("ag_hoo") <= t < T("ag_ask") else 1
    if T("ag_ask") <= t < T("ag_cats"):
        wface = 1
    kitty(c, tl, t, "whiskers", wx, GROUND + 52, 1.05, wface, "walk" if gone > 0 else "sit", walk=wx / 12,
          eyes="closed" if admit and not tl.talking("whiskers", t) else "open",
          head_dy=8 if admit else 0, look=(1, 0.6) if admit else (1, 0))
    c.tint = None
    if T("ag_hoo") <= t < T("ag_hoo", 1) + 0.3:
        k = ease(tl.prog("ag_hoo", t, 0.3, 0.6))
        c.text(470, 470 - 20 * k, "?", 30 + 20 * k, (255, 240, 200), stroke=3)
        c.text(520, 440 - 30 * k, "?", 22 + 18 * k, (255, 240, 200), stroke=3)
    return finish(c, tl, t, 0.45)


# =================================================================== acropolis

def slope_bg():
    def make():
        c = Canvas(sky_img([(0, (16, 20, 56)), (0.6, (44, 50, 108)), (1, (70, 70, 130))]))
        D.stars(c, 31, 120, W, 400)
        D.moon(c, 1080, 120, 40, sky=(30, 36, 80))
        # city lights far below on the left
        rng = np.random.default_rng(14)
        city_blocks(c, rng, -20, 700, 560, 10, 40, [(50, 50, 90), (60, 60, 100)])
        for _ in range(120):
            x, y = rng.uniform(0, 680), rng.uniform(520, 600)
            c.circle(x, y, rng.uniform(1, 2.2), (255, 220, 140), ol=None)
        # the rock slope with a zig-zag path climbing to the walls at the top right
        c.poly([(0, H), (0, 640), (400, 560), (760, 380), (1000, 220), (W, 170), (W, H)], (150, 120, 120), w=2.5)
        c.poly([(1000, 220), (W, 170), (W, 120), (1010, 150)], (190, 180, 190), w=2.5)   # the old walls
        for x in range(1020, W, 40):
            c.line([(x, 150 - (x - 1010) * 0.11), (x, 220 - (x - 1000) * 0.18)], (160, 150, 165), 1.5, cap=False)
        P.parthenon(c, 1180, 130, 200, 90, col=(220, 220, 240), shade=(180, 180, 210), dark=(130, 130, 170), lw=1.5)
        path = slope_path_pts()
        c.line(path, (190, 160, 150), 26, cap=True)
        c.line(path, (210, 184, 170), 18, cap=True)
        for x, y, s, sd in ((240, 650, 1.1, 21), (560, 520, 0.9, 22), (880, 340, 0.8, 23), (420, 700, 1.3, 24),
                            (760, 480, 0.8, 25)):
            P.olive_tree(c, x, y, s, seed=sd, leaf=(70, 100, 90), leaf_l=(140, 170, 170), trunk=(80, 70, 80))
        return c.img
    return cached("slope_bg", make)


def slope_path_pts():
    return [(-40, 700), (300, 640), (620, 560), (500, 470), (820, 400), (980, 260), (1100, 230)]


def on_path(u):
    """Point along the slope path for u in 0..1 (arc-length-ish)."""
    pts = slope_path_pts()
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    d = clamp(u) * sum(seg)
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L:
            f = d / L
            return lerp(a[0], b[0], f), lerp(a[1], b[1], f), 1 if b[0] >= a[0] else -1
        d -= L
    return pts[-1][0], pts[-1][1], 1


def maidens_bg():
    def make():
        c = Canvas(sky_img([(0, (16, 20, 56)), (0.6, (44, 50, 108)), (1, (70, 70, 130))]))
        D.stars(c, 32, 140, W, 300)
        P.caryatid_porch(c, 640, 600, 760, 520, col=(232, 232, 244), shade=(190, 190, 214), dark=(120, 120, 160))
        c.rect(-10, 600, W + 10, H + 10, (150, 140, 150), w=2.5)
        rng = np.random.default_rng(2)
        for _ in range(30):
            x, y = rng.uniform(0, W), rng.uniform(610, H)
            c.ellipse(x, y, rng.uniform(8, 20), 3, (136, 126, 140), ol=None)
        P.olive_tree(c, 90, 610, 1.2, seed=31, leaf=(70, 100, 90), leaf_l=(140, 170, 170), trunk=(80, 70, 80))
        return c.img
    return cached("maidens_bg", make)


def parthenon_bg():
    def make():
        c = Canvas(sky_img([(0, (12, 16, 50)), (0.6, (40, 46, 104)), (1, (76, 72, 136))]))
        D.stars(c, 33, 160, W, 360)
        return c.img
    return cached("parthenon_sky", make)


def parthenon_front():
    def make():
        c = rgba(W, H)
        P.parthenon(c, 640, 600, 980, 440, col=(236, 234, 246), shade=(196, 196, 220), dark=(130, 130, 170), lw=3)
        c.rect(-10, 596, W + 10, H + 10, (150, 140, 150), w=2.5)
        for x in range(0, W, 120):
            c.line([(x, 600), (x - 40, H)], (136, 126, 140), 2, cap=False)
        return c.img
    return cached("parthenon_front", make)


CORNICE_Y = 600 - 440 * (0.08 + 0.58 + 0.025 + 0.16) + 2     # where the owls perch


def acropolis(tl, t):
    T = tl.t
    if t < T("ac_maidens"):
        # ---- shot 1: the secret path up the moonlit slope
        c = Canvas(slope_bg().copy())
        c.tint = MOON_TINT
        s0 = tl.scenes["acropolis"][0]
        u0 = clamp((t - s0) / (T("ac_maidens") - s0 + 1.0))
        group = [("street", 0), ("street", 1), ("socrates", None), ("luna", None), ("whiskers", None), ("street", 3)]
        for k, (who, pal) in enumerate(group):
            u = u0 * 1.15 - k * 0.07
            if not 0 < u < 1:
                continue
            x, y, f = on_path(u)
            s = lerp(0.75, 0.45, u)
            if who == "street":
                P.street_cat(c, x, y + 6, pal, s, f, "walk", t=t, walk=t * 6 + k)
            else:
                kitty(c, tl, t, who, x, y + 6, s, f, "walk", walk=t * 6 + k)
                if who == "luna":
                    owl_on_luna(c, tl, t, x, y + 6, s, f, "walk", walk=t * 6 + k)
        c.tint = None
        return finish(c, tl, t, 0.4)
    if t < T("ac_top"):
        # ---- shot 2: the Porch of the Maidens
        c = Canvas(maidens_bg().copy())
        c.tint = MOON_TINT
        walk_in = tl.prog("ac_maidens", t, 0.0, 0.6)
        lx = lerp(-100, 460, ease(walk_in))
        wx = lerp(-200, 700, ease(walk_in))
        mv = walk_in < 1
        kitty(c, tl, t, "luna", lx, 650, 1.0, 1, "walk" if mv else "sit", walk=lx / 12, look=(1, -1))
        if mv:
            owl_on_luna(c, tl, t, lx, 650, 1.0, 1, "walk", walk=lx / 12, look=(1, -1))
        else:
            sophia(c, tl, t, lx - 70, 652, 0.8, 1, sling=True, look=(1, -1))
        bowl_joke = t >= T("ac_ladies", 0.55)
        kitty(c, tl, t, "whiskers", wx, 654, 1.1, 1 if not bowl_joke else -1, "walk" if mv else "sit", walk=wx / 12,
              look=(1, -1) if not bowl_joke else (1, 0.3), eyes="wide" if T("ac_ladies") <= t < T("ac_ladies", 0.5)
              else "open")
        kitty(c, tl, t, "socrates", 1000, 652, 0.95, -1, "sit", look=(1, -0.5), mouth=0)
        c.tint = None
        if bowl_joke:                                     # a thought bubble: carrying his little bowl
            k = ease(tl.prog("ac_ladies", t, 0.55, 0.7))
            bx, by = 820, 330
            for f, r in ((0.3, 8), (0.6, 12)):
                c.circle(lerp(720, bx, f), lerp(500, by + 70, f), r * k, (255, 255, 255), w=2)
            c.circle(bx, by, 80 * k, (255, 255, 255), w=2.5)
            if k > 0.3:
                MF.bowl(c, bx, by + 30 * k, jig=math.sin(t * 20) * 3)
                c.text(bx, by - 40 * k, "phew!", 16 * k, OUT)
        return finish(c, tl, t, 0.4)
    # ---- shot 3: the Parthenon under the rising full moon
    c = Canvas(parthenon_bg().copy())
    rise = ease(tl.prog("ac_top", t, 0.0, 0.8))
    my = lerp(430, 150, rise)
    soft_glow(c, 1000, my, 330, (150, 150, 200), 0.6 + 0.2 * rise)
    D.moon(c, 1000, my, 70, sky=(40, 46, 104))
    lay = parthenon_front()
    c.img.paste(lay, (0, 0), lay)
    c.tint = ((40, 50, 110), 0.18)
    # the owl family on the cornice
    dance = t >= T("ac_dance")
    for k, (x, s) in enumerate(((300, 0.7), (380, 0.62), (860, 0.66), (940, 0.7))):
        hop = abs(math.sin(t * 6 + k)) * 10 if dance else 0
        P.owl(c, x, CORNICE_Y, s, 1 if x < 640 else -1, t + k, hop=hop, seed=k + 6.0,
              eyes="happy" if T("ac_fly", 0.6) <= t else "open", look=(0, 1),
              flap=0.8 if dance and k % 2 == 0 else 0)
    ya_hop = abs(math.sin(t * 6)) * 8 if dance else 0
    yaya(c, tl, t, 560, CORNICE_Y, 0.95, 1, look=(0, 1), hop=ya_hop,
         eyes="happy" if T("ac_fly", 0.7) <= t < T("ac_thanks") or dance else "open")
    # Sophia flies up to her grandma
    fly = tl.prog("ac_fly", t, 0.05, 0.75)
    if fly <= 0:
        owl_y = 600
        sophia(c, tl, t, 690, 600, 0.8, -1, sling=False, look=(0, -1), eyes="happy" if tl.talking("sophia", t) else "open")
    elif fly < 1:
        x = lerp(690, 660, fly)
        y = lerp(600, CORNICE_Y, ease(fly)) + math.sin(fly * 10) * 14
        sophia(c, tl, t, x, y, 0.8, -1, flap=1.0, eyes="wide" if fly < 0.6 else "happy", mouth=0)
    else:
        sophia(c, tl, t, 660, CORNICE_Y, 0.75, -1, hop=abs(math.sin(t * 6 + 1)) * 8 if dance else 0,
               eyes="happy" if not tl.talking("sophia", t) else "open")
    # cats on the steps
    hop = (lambda k: abs(math.sin(t * 6 + k)) * 16) if dance else (lambda k: 0)
    kitty(c, tl, t, "luna", 470, 660 - hop(1), 0.95, 1, "sit", look=(1, -1),
          eyes="happy" if T("ac_fly", 0.7) <= t and not tl.talking("luna", t) else "open")
    kitty(c, tl, t, "whiskers", 820, 664 - hop(2), 1.0, -1, "sit", look=(1, -1),
          eyes="happy" if dance else "open")
    kitty(c, tl, t, "socrates", 1060, 664 - hop(3), 0.9, -1, "sit", look=(1, -1), mouth=0)
    for k, (x, pal) in enumerate(((180, 0), (300, 2), (1180, 1))):
        P.street_cat(c, x, 666 - hop(k + 4), pal, 0.8, 1 if x < 640 else -1, "sit", t=t + k, look=(1, -1))
    c.tint = None
    if dance:                                     # musical notes in the night
        for k in range(5):
            u = ((t - T("ac_dance")) * 0.4 + k / 5) % 1.0
            x = 200 + k * 220 + 30 * math.sin(t * 2 + k)
            c.text(x, 560 - 300 * u, "♪", 30, mix((255, 230, 150), (60, 60, 110), u))
    return finish(c, tl, t, 0.4)


# ======================================================================== home

def dusk_sea():
    def make():
        c = Canvas(sky_img([(0, (40, 40, 100)), (0.4, (170, 100, 140)), (0.62, (255, 170, 120)), (1, (255, 200, 140))]))
        D.stars(c, 41, 40, W, 180)
        c.circle(900, 440, 46, (255, 210, 150), ol=None)
        rng = np.random.default_rng(6)
        sea_band(c, -10, W + 10, 450, H + 10, (60, 70, 130), (255, 180, 140), rng, n=160)
        for k in range(16):
            y = 456 + k * 14
            c.line([(900 - 60 + 2 * k, y), (900 + 60 - 2 * k, y)], (255, 200, 150), 3, cap=False)
        return c.img
    return cached("dusk_sea", make)


def sill_props(c, t):
    """The olive tree in a pot and the jar of honey: gifts from the owls."""
    c.push(1060, SILL_Y)
    c.poly([(-26, -40), (26, -40), (20, 0), (-20, 0)], P.TERRA, w=2.5)
    for k in range(4):
        c.rect(-18 + k * 10, -30, -13 + k * 10, -24, P.BLACKFIG, ol=None)
    c.pop()
    P.olive_tree(c, 1060, SILL_Y - 38, 0.32, seed=40)
    P.honey_jar(c, 790, SILL_Y, 0.9)


def home(tl, t):
    T = tl.t
    s0 = tl.scenes["home"][0]
    if t < T("h_sill"):
        c = Canvas(dusk_sea().copy())
        u = clamp((t - s0) / (T("h_sill") - s0))
        ax = lerp(-260, 1500, u)
        ay = 220 + 10 * math.sin(t * 1.0)
        P.airship(c, ax, ay, 0.6, t, part="back")
        airship_crew(c, tl, t, ax, ay, 0.6, owl=False, w_eyes="closed", l_eyes="closed")
        P.airship(c, ax, ay, 0.6, t, part="front", lit=1.0)
        return finish(c, tl, t, 0.4)
    c = Canvas(room_bg(True).copy())
    owl_u = tl.prog("h_owl", t, 0.1, 0.8)

    def outside(oc):
        if 0 < owl_u < 1:                          # an owl's silhouette crossing the moon
            x = lerp(760, 1120, owl_u)
            y = 190 + 20 * math.sin(owl_u * 6)
            P.owl(oc, x, y, 0.5, 1, t, flap=1.0, eyes="closed")
    draw_outside(c, outside, "night")
    c.tint = NIGHT
    sill_props(c, t)
    asleep = t >= T("h_moral", 0.5)
    if asleep:
        D.cat(c, 870, SILL_Y, D.LUNA, 0.8, -1, "sleep", t=t + 1, seed=1.3)
        D.cat(c, 965, SILL_Y, D.WHISKERS, 0.8, 1, "sleep", t=t)
        D.mouse(c, 918, SILL_Y - 36, 1.0, 1, t, eyes="closed")
    else:
        looking = T("h_owl") <= t < T("h_moral")
        kitty(c, tl, t, "luna", 870, SILL_Y, 0.75, 1, "sit", look=(1, -1) if looking else (1, 0))
        kitty(c, tl, t, "whiskers", 980, SILL_Y, 0.75, -1 if not looking else 1, "sit", look=(1, -1) if looking
              else (1, 0.4), eyes="happy" if T("h_together", 0.7) <= t < T("h_owl") else "open")
        mouth = tl.mouth("pip", t)
        D.mouse(c, 925, SILL_Y, 0.9, 1 if not looking else 1, t, mouth=mouth,
                hop=abs(math.sin(t * 8)) * 6 if tl.talking("pip", t) else 0)
    c.tint = None
    if asleep:
        D.zzz(c, 1010, 300, t)
    z = 1 + ease(tl.prog("h_moral", t, 0.0, 1.0)) * 0.9
    if t >= T("h_end"):
        z = 1.9
    c = zoom(c, 920, 290, z)
    k = ease(tl.prog("h_end", t, 0.25, 0.5))
    if k > 0:
        c.text(W / 2, 640, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "storm": storm, "airship": airship, "plaka": plaka, "yogurt": yogurt,
               "theatre": theatre, "agora": agora, "acropolis": acropolis, "home": home}
CONTINUOUS = set()
EXTRA_CUTS = ["s_myth", "s_dinner", "a_honey", "a_sea", "a_tale", "a_kittens", "a_land", "th_lost",
              "ac_maidens", "ac_top", "h_sill"]
