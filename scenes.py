"""One function per scene. Each takes (tl, t) and returns a Canvas.

Animation is keyed to script events (tl.t("id", fraction)), so it stays in
sync whatever length the speech and stretched action moments end up being.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1}
NIGHT = ((40, 50, 115), 0.38)

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def view(bg, camx=0.0, camy=0.0):
    """A Canvas holding the visible part of a (possibly larger) background."""
    x, y = int(round(camx * SS)), int(round(camy * SS))
    img = bg.crop((x, y, x + W * SS, y + H * SS)) if bg.size != (W * SS, H * SS) or x or y else bg.copy()
    return Canvas(img)


# ------------------------------------------------------------------ motion

def track(t, keys):
    """Piecewise-linear value through [(time, value), ...]."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    """Track with eased starts and stops (box-filtered over +-r seconds)."""
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def actor(c, tl, t, who, keys, y, s=1.0, face=1, pose="stand", **kw):
    x = smooth(t, keys)
    v = (smooth(t + 0.05, keys) - smooth(t - 0.05, keys)) / 0.1
    moving = abs(v) > 20
    if moving:
        face = 1 if v > 0 else -1
    mouth = kw.pop("mouth", tl.mouth(who, t))
    if who == "pip":
        hop = abs(math.sin(x / 9)) * 5 if moving else kw.pop("hop", 0.0)
        D.mouse(c, x, y, s, face, t, walk=x / 6 if moving else 0.0, mouth=mouth, hop=hop, **kw)
    else:
        if moving and pose == "stand":
            pose = "walk"
        D.cat(c, x, y, PAL[who], s, face, pose, walk=x / 12 if moving else 0.0, t=t,
              mouth=mouth, seed=SEED[who], **kw)
    return x


# --------------------------------------------------------------- settings

def night_sky(w, h, horizon):
    return D.gradient(w * SS, h * SS, [(0, (14, 18, 48)), (horizon * 0.7, (40, 44, 96)),
                                       (horizon, (96, 78, 130)), (1, (96, 78, 130))])


def room(night=False):
    def make():
        if night:
            wall, floor, sky = (92, 88, 130), (88, 66, 70), [(0, (20, 26, 64)), (1, (60, 62, 120))]
        else:
            wall, floor, sky = (250, 228, 190), (196, 136, 88), [(0, (120, 190, 245)), (1, (205, 235, 255))]
        c = Canvas(bg=wall)
        for x in range(0, W, 64):
            c.rect(x + 28, 0, x + 36, 520, mix(wall, (255, 255, 255) if not night else (60, 60, 90), 0.25),
                   ol=None)
        c.rect(0, 520, W, H, floor, ol=None)
        for y in range(540, H, 36):
            c.line([(0, y), (W, y)], mix(floor, (0, 0, 0), 0.12), 2, cap=False)
        c.rect(0, 506, W, 524, mix(wall, (0, 0, 0), 0.25), ol=None)
        # window
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
        c.line([(920, 110), (920, 370)], (240, 240, 240) if not night else (150, 150, 180), 6, cap=False)
        c.line([(760, 240), (1080, 240)], (240, 240, 240) if not night else (150, 150, 180), 6, cap=False)
        c.rect(740, 370, 1100, 392, (255, 250, 240) if not night else (150, 146, 170), r=4)
        # rug, plant, bowl
        c.ellipse(520, 612, 190, 40, (200, 70, 80) if not night else (110, 60, 90))
        c.ellipse(520, 612, 150, 28, (230, 120, 110) if not night else (130, 80, 110), ol=None)
        c.rect(150, 440, 210, 520, (190, 100, 70), r=6)
        for dx, dy in ((-30, -10), (0, -40), (30, -12), (-15, -30), (18, -36)):
            c.ellipse(180 + dx, 440 + dy, 14, 30, (80, 160, 90))
        window_light(c.img, (255, 236, 185) if not night else (150, 160, 220), 0.22 if not night else 0.14)
        return c.img
    return cached(("room", night), make)


def window_light(img, col, strength):
    """Soft patch of light the window throws on the floor: four panes, blurred edges."""
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)

    def p(u, v):   # window (u across, v down) -> floor point, light falling down-left
        return (lerp(lerp(650, 900, u), lerp(470, 790, u), v) * SS, lerp(548, 700, v) * SS)

    gap = 0.03
    for u0, u1 in ((0, 0.5 - gap), (0.5 + gap, 1)):
        for v0, v1 in ((0, 0.5 - gap), (0.5 + gap, 1)):
            md.polygon([p(u0, v0), p(u1, v0), p(u1, v1), p(u0, v1)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(7 * SS)).point(lambda a: int(a * strength))
    img.paste(Image.new("RGB", img.size, col), (0, 0), mask)


def bowl(c, x, y, jig=0.0):
    c.push(x + jig, y)
    c.poly([(-40, -28), (40, -28), (28, 0), (-28, 0)], (90, 150, 220))
    c.ellipse(0, -28, 40, 8, (70, 120, 190))
    c.ellipse(0, -30, 30, 5, (170, 110, 70), ol=None)
    c.text(0, -12, "W", 16, (255, 255, 255))
    c.pop()


# =================================================================== scenes

def title(tl, t):
    def make():
        c = Canvas(night_sky(W, H, 0.75))
        D.stars(c, 1, 120, W, 420)
        D.moon(c, 1010, 150, 58, sky=(30, 34, 80))
        c.poly([(0, 520), (300, 470), (620, 520), (900, 480), (W, 540), (W, H), (0, H)], (40, 62, 82), ol=None)
        c.poly([(0, 600), (380, 560), (W, 640), (W, H), (0, H)], (34, 54, 66), ol=None)
        c.ellipse(940, 655, 260, 40, (30, 48, 92), ol=None)
        c.ellipse(1010, 655, 46, 9, (230, 226, 190), ol=None)
        return c.img
    c = Canvas(cached("title", make).copy())
    c.tint = ((20, 26, 50), 0.55)
    D.cat(c, 300, 585, D.WHISKERS, 0.9, 1, "sit", t=t, seed=0, eyes="open", look=(1, -1))
    D.cat(c, 400, 590, D.LUNA, 0.85, 1, "sit", t=t, seed=1.3, look=(1, -1),
          tail=math.sin(t * 1.5))
    c.tint = None
    rng = np.random.default_rng(3)
    for k in range(14):                              # fireflies
        x = rng.uniform(0, W) + 30 * math.sin(t * 0.7 + k)
        y = rng.uniform(380, 680) + 20 * math.sin(t * 1.1 + k * 2)
        a = 0.5 + 0.5 * math.sin(t * 3 + k)
        c.circle(x, y, 2 + 2 * a, mix((60, 70, 60), (255, 250, 150), a), ol=None)
    k = ease(tl.prog("t_open", t, 0.0, 0.8))
    c.text(W / 2, 170 - 30 * (1 - k), "Whiskers and the", 46, mix((30, 34, 80), (255, 230, 170), k),
           stroke=3 * k)
    k2 = ease(tl.prog("t_open", t, 0.3, 1.0))
    c.text(W / 2, 255, "MOON FISH", 30 + 64 * k2, mix((30, 34, 80), (255, 245, 200), k2), stroke=5 * k2)
    return c


def morning(tl, t):
    c = Canvas(room(False).copy())
    T = tl.t
    jig = 0.0
    for f in (0.45, 0.62):
        dt = t - T("m_bowl", f)
        if 0 < dt < 0.4:
            jig = math.sin(dt * 60) * 8 * (1 - dt / 0.4)
    bowl(c, 1000, 600, jig)
    # Whiskers on the rug
    if t < T("m_wake") - 0.4:
        say = tl.talking("whiskers", t)
        D.cat(c, 520, 615, D.WHISKERS, 1.0, 1, "sit" if say else "sleep", t=t, eyes="closed",
              mouth=tl.mouth("whiskers", t), head_dy=6 if say else 0)
        if not say:
            D.zzz(c, 580, 540, t)
    else:
        startle = clamp((t - T("m_wake") + 0.4) / 0.3)
        D.cat(c, 520, 615, D.WHISKERS, 1.0, 1, "sit", t=t, mouth=tl.mouth("whiskers", t),
              eyes="wide" if t < T("m_end") else "open", look=(1, 0), head_dy=-6 * (1 - startle))
    # Luna
    keys = [(T("m_luna_in"), -120), (T("m_luna_in", 1), 360),
            (T("m_bowl"), 360), (T("m_bowl", 0.4), 930), (T("m_bowl", 0.7), 930),
            (tl.ev("m_wake").end + 0.3, 930), (tl.ev("m_wake").end + 1.8, 700)]
    face = 1 if t < T("m_bowl", 0.7) else -1
    actor(c, tl, t, "luna", keys, 612, face=face)
    return c


def thought_bubble(tl, t, scale):
    bw, bh = 520, 260
    inner = Canvas(D.gradient(bw * SS, bh * SS, [(0, (14, 18, 48)), (0.55, (40, 44, 96)), (0.56, (30, 48, 92)),
                                                  (1, (22, 36, 76))]), size=(bw, bh))
    D.stars(inner, 9, 30, bw, 130)
    inner.poly([(0, 150), (120, 128), (260, 146), (400, 124), (bw, 144), (bw, 160), (0, 160)], (24, 40, 50), ol=None)
    if t >= tl.t("l_fish"):
        x = bw / 2 + 120 * math.sin((t - tl.t("l_fish")) * 0.9)
        D.moon_fish(inner, x, 205, t, 0.8)
    mask = Image.new("L", inner.img.size, 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).ellipse([0, 0, bw * SS - 1, bh * SS - 1], fill=255)
    c_img = inner.img
    if scale < 0.999:
        sz = (max(2, int(bw * SS * scale)), max(2, int(bh * SS * scale)))
        c_img, mask = c_img.resize(sz), mask.resize(sz)
    return c_img, mask


def legend(tl, t):
    c = Canvas(room(False).copy())
    T = tl.t
    bowl(c, 1000, 600)
    if t >= T("l_out"):
        actor(c, tl, t, "whiskers", [(T("l_out", 0.15), 470), (T("l_out", 1), 1400)], 615)
        actor(c, tl, t, "luna", [(T("l_out"), 700), (T("l_out", 1), 1500)], 612, face=-1)
        return c
    lie = T("l_tasty", 1) + 1.5 < t < T("l_think", 0.4)
    D.cat(c, 470, 615, D.WHISKERS, 1.0, 1, "sleep" if lie else "sit", t=t,
          mouth=tl.mouth("whiskers", t),
          eyes="wide" if T("l_tasty") <= t < T("l_tasty", 1) + 0.5 else "open", look=(1, -0.5))
    D.cat(c, 700, 612, D.LUNA, 1.0, -1, "sit", t=t, mouth=tl.mouth("luna", t), seed=1.3,
          look=(1, 0))
    # thought bubble: grows in on the legend, pops at "tasty?"
    a = ease((t - T("l_tom")) / 0.6)
    b = 1 - ease((t - T("l_tasty")) / 0.4)
    k = min(a, b)
    if k > 0.02:
        cx, cy = 640, 210
        for (dx, dy, r) in ((60, 140, 10), (40, 115, 16)):
            c.circle(cx + dx * k, cy + dy, r * k, (255, 255, 255), w=2)
        for ang in range(0, 360, 30):
            rr = math.radians(ang)
            c.circle(cx + math.cos(rr) * 268 * k, cy + math.sin(rr) * 136 * k, 34 * k, (255, 255, 255), w=2)
        img, mask = thought_bubble(tl, t, k)
        c.ellipse(cx, cy, 266 * k, 136 * k, (255, 255, 255), w=0.1)
        c.img.paste(img, (int((cx - 260 * k) * SS), int((cy - 130 * k) * SS)), mask)
    return c


# ------------------------------------------------------------------ garden

GW, GG = 3800, 600        # garden world width, ground line
FENCE = 3300


def garden_bg():
    def make():
        c = Canvas(D.gradient(GW * SS, H * SS, [(0, (110, 185, 245)), (0.7, (200, 232, 255)), (1, (200, 232, 255))]),
                   size=(GW, H))
        rng = np.random.default_rng(5)
        for x in range(150, GW, 520):
            D.cloud(c, x + rng.uniform(-60, 60), rng.uniform(80, 180), rng.uniform(0.7, 1.2))
        pts = [(x, 430 + 40 * math.sin(x / 300)) for x in range(0, GW + 50, 50)]
        c.poly(pts + [(GW, H), (0, H)], (150, 205, 120), ol=None)
        for x in range(100, GW, 420):
            D.tree(c, x + rng.uniform(-50, 50), 470, rng.uniform(0.7, 0.95))
        c.rect(0, GG - 40, GW, H, (110, 185, 90), ol=None)
        c.rect(0, GG + 20, GW, H, (95, 165, 80), ol=None)
        for x in range(60, GW, 260):
            D.bush(c, x + rng.uniform(-40, 40), GG - 30, rng.uniform(0.7, 1.1))
        cols = [(250, 120, 150), (255, 230, 90), (180, 140, 250), (255, 255, 255)]
        for _ in range(140):
            D.flower(c, rng.uniform(0, GW), rng.uniform(GG - 20, H - 10), cols[rng.integers(4)], rng.uniform(0.6, 1))
        # fence
        for x in range(FENCE - 50, FENCE + 60, 34):
            c.poly([(x, GG + 6), (x, 395), (x + 15, 380), (x + 30, 395), (x + 30, GG + 6)], (196, 150, 98))
        c.rect(FENCE - 56, 430, FENCE + 66, 446, (170, 125, 80))
        c.rect(FENCE - 56, 520, FENCE + 66, 536, (170, 125, 80))
        return c.img
    return cached("garden", make)


def arc_y(u, height):
    return -4 * height * u * (1 - u)


def garden(tl, t):
    T = tl.t
    s0 = tl.scenes["garden"][0]
    # Whiskers' path
    wk = [(s0, 260), (T("g_narr", 0.3), 260), (T("g_walk", 1), 700), (T("g_chase"), 700),
          (T("g_shout", 1), 2050), (T("g_miss", 0.2), 2100), (T("g_miss", 0.55), 2260),
          (T("g_on"), 2260), (T("g_fence", 1), 3040), (T("g_grumble"), 3040), (T("g_grumble", 1), 3180),
          (T("g_jump_w"), 3180)]
    lk = [(s0, 380), (T("g_narr", 0.2), 380), (T("g_walk", 1), 830), (T("g_chase", 0.3), 830),
          (T("g_tease"), 1900), (T("g_tease", 0.6), 2120), (T("g_on"), 2120), (T("g_fence", 1), 3170)]
    wx = smooth(t, wk)
    lx = smooth(t, lk)
    # jumps override paths
    lj = tl.prog("g_jump_l", t, 0.15, 0.75)
    if t >= T("g_jump_l", 0.15):
        lx = lerp(3170, 3480, ease(lj))
    wj = tl.prog("g_jump_w", t)
    if t >= T("g_jump_w"):
        if wj < 0.25:
            wx = lerp(3180, 3250, ease(wj / 0.25))
        elif wj < 0.55:
            wx = 3260 + 6 * math.sin(t * 25)
        else:
            wx = lerp(3260, 3460, ease((wj - 0.55) / 0.3))
    if t >= T("g_end"):
        wx += 260 * tl.prog("g_end", t)
        lx += 300 * tl.prog("g_end", t)

    camx = clamp((wx + lx) / 2 - W / 2 + 60, 0, GW - W)
    c = view(garden_bg(), camx)
    c.push(-camx, 0)

    # butterfly
    if T("g_look") - 0.5 < t < T("g_miss", 0.9):
        if t < T("g_chase"):
            u = ease((t - T("g_look") + 0.5) / (T("g_chase") - T("g_look") + 0.5))
            bx, by = lerp(wx + 700, wx + 220, u), lerp(300, 450, u)
        else:
            bx = wx + 170 + 40 * math.sin(t * 3)
            by = 450 + 30 * math.sin(t * 5)
            up = tl.prog("g_miss", t, 0.15, 0.9)
            by -= 600 * up * up
            bx += 300 * up
        D.butterfly(c, bx, by, t)

    # Luna
    lpose, ly = "stand", GG
    if T("g_ready", 0.7) < t < T("g_jump_l", 0.15):
        lpose = "crouch"
    if T("g_jump_l", 0.15) <= t < T("g_jump_l", 0.75):
        lpose, ly = "leap", GG + arc_y(lj, 270)
    lmov = abs(smooth(t + 0.05, lk) - smooth(t - 0.05, lk)) > 1 or t >= T("g_end")
    lface = -1 if T("g_tease") - 0.2 < t < T("g_on") or T("g_jump_l", 0.75) < t < T("g_end") else 1
    D.cat(c, lx, ly, D.LUNA, 1.0, lface if not lmov else 1, "walk" if (lmov and lpose == "stand") else lpose,
          walk=lx / 12 if lmov else 0, t=t, mouth=tl.mouth("luna", t), seed=1.3,
          eyes="happy" if T("g_tease") < t < T("g_tease", 1) else "open", look=(1, -0.6))

    # Whiskers
    wpose, wy, squash, eyes = "stand", GG, 1.0, "open"
    wmov = abs(smooth(t + 0.05, wk) - smooth(t - 0.05, wk)) > 1 or t >= T("g_end")
    if T("g_chase") <= t < T("g_shout", 1):                 # bounding chase
        wy = GG + arc_y((t * 2.2) % 1.0, 30)
    if T("g_miss", 0.2) <= t < T("g_miss", 0.55):           # big leap for the butterfly
        wpose, wy = "leap", GG + arc_y(tl.prog("g_miss", t, 0.2, 0.55), 170)
    if T("g_miss", 0.55) <= t < T("g_tease"):
        wpose, squash = "sit", 1 - 0.2 * max(0, 1 - (t - T("g_miss", 0.55)) / 0.3)
        eyes = "closed"
    if T("g_tease") <= t < T("g_on"):
        wpose = "sit"
    if T("g_jump_w") <= t < T("g_jump_w", 1):
        if wj < 0.25:
            wpose, wy = "leap", GG - 200 * ease(wj / 0.25)
        elif wj < 0.55:
            wpose, wy, eyes = "stand", GG - 215, "wide"
        elif wj < 0.85:
            u = (wj - 0.55) / 0.3
            wpose, wy, eyes = "leap", GG - 215 * (1 - u * u) - 40 * math.sin(math.pi * u), "wide"
        else:
            wpose, squash = "stand", 1 - 0.25 * math.sin(math.pi * (wj - 0.85) / 0.15)
    if T("g_tada") <= t < T("g_end"):
        eyes = "happy"
    wface = -1 if T("g_purpose") - 0.3 < t < T("g_on") else 1
    if wmov and wpose == "stand":
        wpose = "walk"
    D.cat(c, wx, wy, D.WHISKERS, 1.0, 1 if wmov else wface, wpose, walk=wx / 12 if wmov else 0, t=t,
          mouth=tl.mouth("whiskers", t), eyes=eyes, squash=squash,
          look=(1, -1) if T("g_look") <= t < T("g_miss", 0.6) else (0.5, 0))
    c.pop()
    return c


# ------------------------------------------------------------------ meadow

MW, MG = 3000, 610


def meadow_bg(sunset):
    def make():
        if sunset:
            sky = [(0, (90, 80, 150)), (0.45, (240, 140, 120)), (0.62, (255, 200, 130)), (1, (255, 200, 130))]
            hill1, hill2, ground = (150, 120, 120), (130, 120, 90), (140, 140, 70)
        else:
            sky = [(0, (120, 190, 245)), (0.65, (215, 238, 255)), (1, (215, 238, 255))]
            hill1, hill2, ground = (150, 200, 150), (130, 190, 110), (150, 200, 90)
        c = Canvas(D.gradient(MW * SS, H * SS, sky), size=(MW, H))
        pts = [(x, 420 + 50 * math.sin(x / 260 + 1)) for x in range(0, MW + 50, 50)]
        c.poly(pts + [(MW, H), (0, H)], hill1, ol=None)
        pts = [(x, 480 + 30 * math.sin(x / 180)) for x in range(0, MW + 50, 50)]
        c.poly(pts + [(MW, H), (0, H)], hill2, ol=None)
        c.rect(0, MG - 50, MW, H, ground, ol=None)
        rng = np.random.default_rng(8)
        for _ in range(900):
            x, y = rng.uniform(0, MW), rng.uniform(MG - 60, H)
            h = rng.uniform(20, 50)
            c.line([(x, y), (x + rng.uniform(-8, 8), y - h)], mix(ground, (40, 90, 30), rng.uniform(0.2, 0.5)), 2,
                   cap=False)
        for _ in range(90):
            D.flower(c, rng.uniform(0, MW), rng.uniform(MG - 40, H), [(255, 255, 255), (250, 150, 190),
                                                                      (255, 220, 90)][rng.integers(3)], 0.6)
        # Pip's rock
        c.ellipse(1450, MG - 6, 46, 26, (150, 150, 160))
        c.ellipse(1440, MG - 18, 30, 10, (175, 175, 185), ol=None)
        return c.img
    return cached(("meadow", sunset), make)


def meadow(tl, t):
    T = tl.t
    s0, s1 = tl.scenes["meadow"]
    wk = [(s0, -200), (T("md_walk", 1), 1130), (T("md_walk2"), 1130), (T("md_walk2", 1), 1900),
          (T("md_sun"), 1900), (s1, 3250)]
    lk = [(s0, -80), (T("md_walk", 1), 1260), (T("md_walk2"), 1260), (T("md_walk2", 1), 2030),
          (T("md_sun"), 2030), (s1, 3380)]
    pk = [(s0, 1450), (T("md_walk2", 0.15), 1450), (T("md_walk2", 1), 2160), (T("md_sun"), 2160), (s1, 3520)]
    wx, lx = smooth(t, wk), smooth(t, lk)
    camx = clamp((wx + lx) / 2 - W / 2, 0, MW - W)
    k = ease(tl.prog("md_walk2", t, 0.0, 1.0) * 0.4 + tl.prog("md_sun", t) * 0.4 + tl.prog("md_sunset", t) * 0.2)
    day, eve = view(meadow_bg(False), camx), view(meadow_bg(True), camx)
    img = Image.blend(day.img, eve.img, k) if 0 < k < 1 else (day.img if k <= 0 else eve.img)
    c = Canvas(img)
    # the sun sinks as the evening comes (drawn live so the day/sunset blend has one sun)
    sx, sy = lerp(1050, 760, k), lerp(110, 455, k)
    c.circle(sx, sy, lerp(50, 70, k), mix((255, 230, 100), (255, 225, 150), k), ol=None)
    c.push(-camx, 0)
    looking = T("md_look") <= t < T("md_down")
    lface = (1 if int((t - T("md_look")) * 2.5) % 2 else -1) if looking else 1
    wface = (-1 if int((t - T("md_look")) * 2.5) % 2 else 1) if looking else 1
    # Pip pops up on the rock when he calls out
    if t >= T("md_halt") - 0.2:
        pop = ease((t - T("md_halt") + 0.2) / 0.35)
        proud = T("md_pip") <= t < T("md_pip", 1)
        on_rock = t < T("md_walk2", 0.15)
        py = MG - 30 + (1 - pop) * 40 if on_rock else MG
        happy = T("md_way") <= t < T("md_way", 1) + 0.3
        actor(c, tl, t, "pip", pk, py, 1.6, face=-1 if on_rock else 1, proud=proud,
              eyes="happy" if happy else "open")
    look_down = (0.8, 1.0) if T("md_down") <= t < T("md_walk2") else (1, 0)
    actor(c, tl, t, "whiskers", wk, MG, face=wface, look=look_down)
    actor(c, tl, t, "luna", lk, MG + 4, face=lface, look=look_down)
    # swaying foreground grass
    rng = np.random.default_rng(12)
    for _ in range(220):
        x, h = rng.uniform(0, MW), rng.uniform(40, 90)
        if not camx - 40 < x < camx + W + 40:
            continue
        sway = 10 * math.sin(t * 1.6 + x / 70)
        c.line([(x, H + 5), (x + sway, H - h)], mix((80, 150, 60), (120, 90, 60), k), 4, cap=False)
    c.pop()
    return c


# ------------------------------------------------------------- pond / realize

PG = 1262          # bank feet line (world y)
FISH = (820, 1250)
FROGS = [(1060, 1300, 1), (1185, 1225, -1), (930, 1390, 1)]


def pond_bg():
    def make():
        c = Canvas(night_sky(W, 2 * H, 0.62), size=(W, 2 * H))
        D.stars(c, 2, 260, W, 850)
        D.moon(c, 860, 230, 64, sky=(20, 26, 64))
        # tree line silhouette
        rng = np.random.default_rng(6)
        for x in range(-40, W + 80, 70):
            r = rng.uniform(50, 90)
            c.circle(x, 960 - r * 0.6, r, (22, 36, 52), ol=None)
        c.rect(0, 950, W, 2 * H, (24, 46, 52), ol=None)
        # pond
        c.ellipse(820, 1270, 560, 170, (30, 50, 96), ol=(18, 30, 40), w=4)
        for k in range(6):
            c.ellipse(820, 1180 + k * 34, 300 - k * 20, 3, (44, 68, 120), ol=None)
        # bank
        c.poly([(0, 1180), (360, 1210), (460, 1300), (380, 1440), (0, 1440)], (40, 78, 58), ol=None)
        for x in range(10, 440, 22):
            c.line([(x, 1220 + (x % 3) * 8), (x + 6, 1180 + (x % 5) * 6)], (60, 110, 70), 3, cap=False)
        for x, y, _ in FROGS:
            D.lily_pad(c, x, y + 4, 40)
        for x, y in ((700, 1380), (1240, 1320), (560, 1330)):
            D.lily_pad(c, x, y, 26)
        # reeds
        for x in (1250, 1265, 1280, 470, 485):
            c.line([(x, 1300), (x - 8, 1140)], (50, 90, 60), 4, cap=False)
            c.ellipse(x - 7, 1160, 5, 16, (110, 70, 50), ol=None)
        return c.img
    return cached("pond", make)


def pond_common(tl, t, camy, fish_broken, frogs_laugh=False):
    c = view(pond_bg(), 0, camy)
    c.push(0, -camy)
    D.moon_fish(c, FISH[0], FISH[1], t, 1.0, broken=fish_broken)
    for i, (x, y, f) in enumerate(FROGS):
        croak = 0.0
        for e in tl.events:
            for name, frac in e.sfx or []:
                if name == "ribbit":
                    dt = t - (e.start + e.dur * frac) - i * 0.05
                    if 0 < dt < 0.45:
                        croak = max(croak, math.sin(math.pi * dt / 0.45))
        c.tint = NIGHT
        D.frog(c, x, y, 1.0, f, t, croak, laugh=frogs_laugh, seed=i * 1.1)
        c.tint = None
    return c


def fireflies(c, t, camy, n=10):
    rng = np.random.default_rng(4)
    for k in range(n):
        x = rng.uniform(0, W) + 40 * math.sin(t * 0.5 + k)
        y = rng.uniform(1000, 1300) + 30 * math.sin(t * 0.8 + k * 3)
        a = 0.5 + 0.5 * math.sin(t * 2.5 + k * 1.7)
        c.circle(x, y, 2 + 2 * a, mix((60, 80, 70), (255, 250, 160), a), ol=None)


def pond(tl, t):
    T = tl.t
    s0 = tl.scenes["pond"][0]
    pj = tl.prog("p_pounce", t)
    broken = 0.0
    if t >= T("p_pounce", 0.38):
        broken = 1.0
    c = pond_common(tl, t, H, broken)
    fireflies(c, t, H)
    c.tint = NIGHT
    actor(c, tl, t, "pip", [(s0, -60), (T("p_arrive", 0.8), 420)], PG + 8, 1.3,
          eyes="wide" if t >= T("p_pounce", 0.38) else "open")
    actor(c, tl, t, "luna", [(s0, -260), (T("p_arrive", 0.8), 150)], PG - 6, look=(1, 0.5),
          eyes="wide" if t >= T("p_pounce", 0.38) else "open")
    wkeys = [(s0, -130), (T("p_arrive", 0.85), 300)]
    if t < T("p_crouch"):
        actor(c, tl, t, "whiskers", wkeys, PG, look=(1, 0.6),
              eyes="wide" if t >= T("p_glow") else "open")
    elif t < T("p_pounce", 0.05):
        D.cat(c, 300 + 3 * math.sin(t * 18), PG, D.WHISKERS, 1.0, 1, "crouch", t=t,
              mouth=tl.mouth("whiskers", t), look=(1, 0.6), tail=math.sin(t * 9), eyes="wide")
    elif pj < 0.38:
        u = (pj - 0.05) / 0.33
        D.cat(c, lerp(300, FISH[0], u), PG + arc_y(u, 230) + 20 * u * u, D.WHISKERS, 1.0, 1, "leap", t=t,
              eyes="wide", mouth=0.6)
    else:
        u = (pj - 0.38) / 0.62
        # splash: water drops flying out, then rings
        rng = np.random.default_rng(21)
        for k in range(26):
            ang = rng.uniform(math.pi * 1.1, math.pi * 1.9)
            sp = rng.uniform(200, 420)
            tt = (t - T("p_pounce", 0.38))
            x = FISH[0] + math.cos(ang) * sp * tt
            y = FISH[1] + math.sin(ang) * sp * tt + 700 * tt * tt
            if y < FISH[1] + 20:
                c.ellipse(x, y, 5, 7, (170, 210, 255), ol=None)
        for k in range(3):
            r = 40 + 260 * ((u * 1.5 + k * 0.25) % 1.0)
            c.ellipse(FISH[0], FISH[1], r, r * 0.25, None, ol=(140, 170, 220), w=2)
        if u > 0.25:
            D.cat(c, FISH[0] - 30, FISH[1] + 4, D.WHISKERS, 1.0, 1, "swim", t=t, wet=1, eyes="closed")
    c.tint = None
    c.pop()
    return c


def realize(tl, t):
    T = tl.t
    # camera: tilt up to the moon on "look up", back down during the narration
    camy = H - (H - 60) * ease(tl.prog("r_up", t)) + (H - 60) * ease(tl.prog("r_narr", t, 0.2, 0.9))
    broken = 1 - ease(tl.prog("r_blub", t, 0.0, 1.0) * 0.5 + tl.prog("r_out", t) * 0.5)
    laughing = T("r_laugh") <= t < T("r_friend")
    c = pond_common(tl, t, camy, broken, frogs_laugh=laughing)
    fireflies(c, t, camy)
    c.tint = NIGHT
    gig = (lambda ph: abs(math.sin(t * 8 + ph)) * 6) if laughing else (lambda ph: 0)
    lmouth = 0.5 + 0.4 * math.sin(t * 16) if laughing else tl.mouth("luna", t)
    up = T("r_lookup") <= t < T("r_narr", 0.7)
    D.mouse(c, 420, PG + 8 - gig(1), 1.3, 1 if not laughing else -1, t,
            mouth=0.5 + 0.4 * math.sin(t * 15) if laughing else tl.mouth("pip", t),
            eyes="happy" if laughing or t >= T("r_two") else "open")
    D.cat(c, 150, PG - 6 - gig(2), D.LUNA, 1.0, 1, "stand", t=t, mouth=lmouth, seed=1.3,
          eyes="happy" if laughing or T("r_friend") <= t < T("r_two", 1) else "open",
          look=(0.5, -1) if up else (1, 0.5))
    # Whiskers: paddling, then climbs out dripping
    if t < T("r_out", 0.6):
        u = tl.prog("r_out", t, 0.0, 0.6)
        D.cat(c, lerp(FISH[0] - 30, 390, ease(u)), FISH[1] + 4 + 6 * math.sin(t * 4), D.WHISKERS, 1.0,
              -1 if t >= T("r_out") else 1, "swim", t=t, wet=1, mouth=tl.mouth("whiskers", t),
              eyes="wide")
    else:
        u = tl.prog("r_out", t, 0.6, 1.0)
        wet = 1 - 0.7 * tl.prog("r_laugh", t, 0, 1)
        sq = 1 - 0.15 * math.sin(math.pi * u) if u < 1 else 1
        D.cat(c, lerp(390, 300, ease(u)), lerp(PG + 30, PG, ease(u)) - gig(0), D.WHISKERS, 1.0,
              1 if t < T("r_laugh") else -1, "stand", t=t, wet=wet,
              mouth=0.5 + 0.4 * math.sin(t * 14) if laughing else tl.mouth("whiskers", t),
              eyes="happy" if laughing or t >= T("r_home") else "open", squash=sq,
              look=(0.5, -1) if up and t >= T("r_up", 0.6) else (1, 0.4))
    c.tint = None
    c.pop()
    return c


# -------------------------------------------------------------------- home

def hills_night():
    def make():
        c = Canvas(night_sky(W, H, 0.8))
        D.stars(c, 3, 140, W, 450)
        D.moon(c, 300, 140, 70, sky=(20, 26, 64))
        c.poly([(0, 470), (250, 430), (600, 480), (900, 440), (W, 480), (W, H), (0, H)], (38, 60, 78), ol=None)
        c.poly([(0, 560), (W, 520), (W, H), (0, H)], (30, 50, 60), ol=None)
        c.poly([(0, 600), (W, 580), (W, 620), (0, 640)], (70, 80, 100), ol=None)   # path
        # home in the distance with a lit window
        c.rect(70, 470, 190, 560, (60, 60, 90))
        c.poly([(56, 474), (130, 420), (204, 474)], (80, 50, 70))
        c.rect(110, 500, 150, 530, (255, 220, 120), w=2)
        return c.img
    return cached("hills", make)


def home(tl, t):
    T = tl.t
    if t < T("h_sill"):
        c = Canvas(hills_night().copy())
        s0 = tl.scenes["home"][0]
        end = T("h_walk", 1) + 0.6
        c.tint = NIGHT
        for who, off, y in (("luna", 0, 612), ("whiskers", 110, 610), ("pip", 220, 614)):
            keys = [(s0, 1400 + off), (end, 80 + off)]
            actor(c, tl, t, who, keys, y, 0.75 if who != "pip" else 1.0)
        c.tint = None
        return c
    c = Canvas(room(True).copy())
    c.tint = ((30, 36, 90), 0.25)
    D.cat(c, 870, 372, D.LUNA, 0.8, -1, "sleep", t=t + 1, seed=1.3)
    D.cat(c, 960, 372, D.WHISKERS, 0.8, 1, "sleep", t=t, mouth=tl.mouth("whiskers", t))
    D.mouse(c, 918, 336, 1.0, 1, t, eyes="closed")
    c.tint = None
    D.zzz(c, 1000, 300, t)
    # close-up: the window area at 2x is exactly one output frame of supersampled pixels
    x0, y0 = 610, 110
    c = Canvas(c.img.crop((x0 * SS, y0 * SS, (x0 + W // 2) * SS, (y0 + H // 2) * SS)).resize((W * SS, H * SS)))
    k = ease(tl.prog("h_end", t, 0.25, 0.55))
    if k > 0:
        c.text(W / 2, 655, "The End", 30 + 40 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"title": title, "morning": morning, "legend": legend, "garden": garden,
               "meadow": meadow, "pond": pond, "realize": realize, "home": home}

# scene starts that continue the previous shot (no fade through black)
CONTINUOUS = {"legend", "realize"}
