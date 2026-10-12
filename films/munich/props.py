"""Props, landmarks and new characters for "Whiskers and the Swan Castle".

All drawn in the shared flat style: origin at the bottom centre unless noted,
local units = output pixels at s=1.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix

# palette
CASTLE_W = (246, 242, 234)
CASTLE_SH = (206, 204, 218)
ROOF = (78, 104, 156)
ROOF_D = (58, 78, 124)
GATE = (200, 146, 112)
GATE_SH = (168, 116, 92)
ROCK = (150, 140, 136)
ROCK_D = (112, 104, 106)
FIR = (44, 98, 72)
FIR_D = (30, 72, 56)
POST_YELLOW = (252, 204, 40)
CARD = (206, 160, 104)
CARD_D = (172, 126, 78)
BOOK_BLUE = (58, 86, 160)
BOOK_D = (40, 60, 120)
GOLD = (240, 196, 80)
PAPER = (252, 244, 222)
PRETZEL = (176, 96, 44)
PRETZEL_L = (214, 140, 72)
BAV_BLUE = (90, 160, 225)


def rot(pts, ang, cx=0.0, cy=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


# ================================================================ scenery

def fir(c, x, y, s=1.0, col=FIR, dark=FIR_D, trunk=(100, 70, 50), ol=OUT):
    """Tall Bavarian spruce: stacked drooping tiers."""
    c.push(x, y, s)
    c.rect(-7, -30, 7, 0, trunk, ol=ol, w=2)
    tiers = ((60, -40, -110), (52, -80, -150), (44, -120, -190), (34, -160, -226), (22, -196, -256))
    for w2, bot, top in tiers:
        pts = [(-w2, bot), (-w2 * 0.55, bot - 8), (-w2 * 0.2, bot + 2), (0, top), (w2 * 0.2, bot + 2),
               (w2 * 0.55, bot - 8), (w2, bot)]
        pts = [(-w2, bot), (0, top), (w2, bot), (w2 * 0.5, bot - 6), (0, bot + 3), (-w2 * 0.5, bot - 6)]
        c.poly(pts, col, ol=ol, w=2.5)
        c.poly([(0, top), (w2, bot), (w2 * 0.5, bot - 6), (w2 * 0.15, bot - 2)], dark, ol=None)
    c.pop()


def fir_flat(c, x, y, s, col):
    """Silhouette spruce for far layers (no outline)."""
    c.push(x, y, s)
    c.poly([(-50, 0), (0, -260), (50, 0)], col, ol=None)
    for k in range(5):
        yy = -40 - k * 44
        w2 = 52 - k * 9
        c.poly([(-w2, yy), (0, yy - 70), (w2, yy)], col, ol=None)
    c.pop()


def alp(c, x, base, w, h, rock=(150, 150, 176), snow=(250, 250, 255), shade=(214, 220, 238), seed=0, cap=0.38,
        ol=OUT):
    """A craggy Alpine peak (wider shoulders than a cone)."""
    rng = np.random.default_rng(seed)
    pts = [(x - w / 2, base)]
    n = 7
    for i in range(1, n):
        u = i / n
        px = x - w / 2 + w * u
        bump = math.sin(math.pi * u) ** 1.4
        py = base - h * bump + rng.uniform(-0.06, 0.06) * h
        pts.append((px, py))
    pts.append((x + w / 2, base))
    top_i = min(range(len(pts)), key=lambda i: pts[i][1])
    c.poly(pts, rock, ol=ol, w=2.5)
    # shade right side
    c.poly(pts[top_i:] + [(pts[top_i][0] + w * 0.05, base)], mix(rock, (40, 40, 70), 0.22), ol=None)
    # snow cap
    tx, ty = pts[top_i]
    yb = ty + h * cap
    cap_pts = [p for p in pts if p[1] < yb]
    if len(cap_pts) >= 1:
        left = [p for p in pts if p[1] < yb]
        lx = min(p[0] for p in left) - w * 0.05
        rx = max(p[0] for p in left) + w * 0.05
        zig = []
        m = 6
        for i in range(m + 1):
            u = i / m
            zig.append((lerp(rx, lx, u), yb + (rng.uniform(4, 18) if i % 2 else -rng.uniform(0, 8)) * h / 260))
        c.poly(left + zig, snow, ol=ol, w=2)
        c.poly([(tx, ty)] + [p for p in left if p[0] > tx] + [(rx, yb), (tx + 8, yb)], shade, ol=None)


def hill(c, pts_y, x0, x1, col, ol=None, base=H + 400):
    """Smooth rolling hill line through sample heights."""
    n = len(pts_y)
    xs = np.linspace(x0, x1, 60)
    ys = np.interp(np.linspace(0, n - 1, 60), np.arange(n), pts_y)
    pts = [(x0, base)] + list(zip(xs, ys)) + [(x1, base)]
    c.poly(pts, col, ol=None)
    if ol:
        c.line(list(zip(xs, ys)), ol, 2.5)


def rock_face(c, pts, col=ROCK, dark=ROCK_D, seed=0):
    c.poly(pts, col, w=2.5)
    rng = np.random.default_rng(seed)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    for _ in range(int(len(pts) * 1.5)):
        x = rng.uniform(min(xs) + 20, max(xs) - 20)
        y = rng.uniform(min(ys) + 20, max(ys) - 20)
        c.line([(x, y), (x + rng.uniform(-30, 30), y + rng.uniform(10, 40))], dark, 2)


# =========================================================== Neuschwanstein

def _cone(c, x, top, base, w, roof=ROOF, roof_d=ROOF_D, ol=OUT, lw=2.5, finial=True):
    c.poly([(x - w, base), (x, top), (x + w, base)], roof, ol=ol, w=lw)
    c.poly([(x, top), (x + w, base), (x + w * 0.25, base)], roof_d, ol=None)
    if finial:
        c.line([(x, top), (x, top - (base - top) * 0.15)], (230, 200, 90), max(1.5, lw * 0.6))


def _windows(c, x0, x1, y, n, wh, col, arch=True, ww=None):
    ww = ww or max(3.0, (x1 - x0) / n * 0.38)
    for i in range(n):
        cx = lerp(x0, x1, (i + 0.5) / n)
        c.rect(cx - ww / 2, y - wh, cx + ww / 2, y, col, ol=None)
        if arch:
            c.ellipse(cx, y - wh, ww / 2, ww / 2, col, ol=None)


def neuschwanstein(c, x, y, s=1.0, lit=0.0, night=0.0, ol=OUT):
    """The white fairy-tale castle seen from the side, origin at the middle of its base (on the cliff).

    lit: 0..1 window glow; night: 0..1 darkens walls toward moonlight blue.
    Roughly 520 wide and 470 tall at s=1.
    """
    wall = mix(CASTLE_W, (150, 160, 205), night * 0.55)
    sh = mix(CASTLE_SH, (110, 120, 170), night * 0.55)
    gate = mix(GATE, (110, 96, 130), night * 0.5)
    gsh = mix(GATE_SH, (90, 78, 110), night * 0.5)
    roof = mix(ROOF, (50, 62, 110), night * 0.4)
    roofd = mix(ROOF_D, (36, 44, 86), night * 0.4)
    win_dark = mix((70, 80, 110), (40, 46, 80), night)
    win = mix(win_dark, (255, 214, 110), lit)
    lw = 2.5
    c.push(x, y, s)
    # ---- left low wing (Kemenate) with stepped gable
    c.rect(-250, -150, -140, 0, wall, ol=ol, w=lw)
    c.rect(-250, -150, -230, 0, sh, ol=None)
    c.poly([(-256, -150), (-195, -215), (-134, -150)], roof, ol=ol, w=lw)
    _windows(c, -240, -150, -100, 3, 22, win)
    _windows(c, -240, -150, -40, 3, 18, win)
    # ---- square tower (behind palas, left)
    c.rect(-150, -300, -96, 0, wall, ol=ol, w=lw)
    c.rect(-150, -300, -138, 0, sh, ol=None)
    for k in range(4):                                       # crenellations
        c.rect(-152 + k * 15, -316, -142 + k * 15, -300, wall, ol=ol, w=2)
    _windows(c, -146, -100, -250, 2, 20, win)
    _cone(c, -100, -350, -300, 9, roof, roofd, ol, 2)
    # ---- the palas: tall main block with steep roof
    c.rect(-100, -330, 60, 0, wall, ol=ol, w=lw)
    c.rect(-100, -330, -82, 0, sh, ol=None)
    c.poly([(-108, -330), (-20, -410), (68, -330)], roof, ol=ol, w=lw)
    c.poly([(-20, -410), (68, -330), (10, -330)], roofd, ol=None)
    # stepped gable front on the palas roof
    c.rect(-40, -380, 0, -330, wall, ol=ol, w=2)
    c.poly([(-44, -380), (-20, -404), (4, -380)], wall, ol=ol, w=2)
    _windows(c, -36, -4, -350, 2, 14, win)
    for row, (yy, hh) in enumerate(((-270, 34), (-200, 34), (-130, 30), (-60, 26))):
        _windows(c, -90, 52, yy, 5, hh, win)
    # balcony band
    c.rect(-104, -172, 64, -164, sh, ol=ol, w=2)
    # corner turrets of the palas
    for tx in (-100, 60):
        c.rect(tx - 9, -380, tx + 9, -300, wall, ol=ol, w=2)
        _cone(c, tx, -430, -380, 12, roof, roofd, ol, 2)
    # ---- the slender tall round tower (in front, right)
    c.rect(66, -360, 104, -20, wall, ol=ol, w=lw)
    c.rect(66, -360, 76, -20, sh, ol=None)
    c.rect(60, -372, 110, -356, wall, ol=ol, w=2)          # gallery ring
    for k in range(6):
        c.rect(60 + k * 8.5, -380, 65 + k * 8.5, -372, wall, ol=ol, w=1.5)
    _cone(c, 85, -470, -372, 28, roof, roofd, ol, lw)
    _windows(c, 74, 96, -300, 1, 26, win)
    _windows(c, 74, 96, -220, 1, 22, win)
    _windows(c, 74, 96, -140, 1, 18, win)
    # little stair turret clinging to the tower
    c.rect(100, -250, 120, -60, wall, ol=ol, w=2)
    _cone(c, 110, -290, -250, 13, roof, roofd, ol, 2)
    # ---- gatehouse (reddish), right
    c.rect(110, -150, 250, 0, gate, ol=ol, w=lw)
    c.rect(110, -150, 126, 0, gsh, ol=None)
    for k in range(9):
        c.rect(110 + k * 15.5, -162, 118 + k * 15.5, -150, gate, ol=ol, w=1.5)
    for tx in (118, 242):
        c.rect(tx - 12, -200, tx + 12, -110, gate, ol=ol, w=2)
        _cone(c, tx, -240, -200, 15, roof, roofd, ol, 2)
    c.rect(166, -70, 200, 0, mix(gsh, (60, 40, 40), 0.4), ol=ol, w=2, r=0)
    c.ellipse(183, -70, 17, 17, mix(gsh, (60, 40, 40), 0.4), ol=ol, w=2)
    c.rect(167, -70, 199, -2, mix(gsh, (60, 40, 40), 0.4), ol=None)
    _windows(c, 132, 236, -100, 4, 16, win)
    # ---- warm window glow halo
    if lit > 0.3 and night > 0.3:
        pass
    c.pop()


def castle_cliff(c, x, y, s=1.0, col=ROCK, dark=ROCK_D, night=0.0, seed=3):
    """The rocky crag the castle sits on, origin at the top centre."""
    col = mix(col, (70, 76, 110), night * 0.5)
    dark = mix(dark, (50, 54, 86), night * 0.5)
    c.push(x, y, s)
    pts = [(-290, 0), (290, 0), (300, 60), (330, 120), (350, 260), (380, 420), (-420, 420), (-360, 260),
           (-320, 140), (-300, 60)]
    rock_face(c, pts, col, dark, seed)
    c.pop()


# ===================================================================== book

def book(c, x, y, s=1.0, ang=0.0, wet=0.0, ol=OUT):
    """The closed storybook (blue cloth, gold swan), centred at x, y. ~70x90 at s=1."""
    cover = mix(BOOK_BLUE, (40, 70, 110), wet * 0.4)
    c.push(x, y, s)
    def R(pts):
        return rot(pts, ang)
    c.poly(R([(-36, -46), (38, -46), (38, 46), (-36, 46)]), PAPER, ol=ol, w=2.5)        # page block
    c.poly(R([(-40, -48), (34, -48), (34, 44), (-40, 44)]), cover, ol=ol, w=2.5)
    c.poly(R([(-40, -48), (-30, -48), (-30, 44), (-40, 44)]), mix(cover, (0, 0, 0), 0.25), ol=None)
    c.poly(R([(-24, -36), (26, -36), (26, 32), (-24, 32)]), cover, ol=GOLD, w=1.5)
    # gold swan emblem: body, neck curve
    for px, py, r in ((-4, 6, 9), (6, 8, 7), (8, -4, 3), (7, -12, 3), (9, -18, 3.5)):
        q = R([(px, py)])[0]
        c.circle(q[0], q[1], r, GOLD, ol=None)
    q = R([(13, -18)])[0]
    c.circle(q[0], q[1], 2, (240, 130, 50), ol=None)
    if wet > 0.05:
        for k in range(3):
            dx, dy = R([(-20 + 18 * k, 40 + 4 * math.sin(k))])[0]
            c.ellipse(dx, dy + 6, 2.5, 4, (170, 210, 255), ol=None)
    c.pop()


def book_open(c, x, y, w=560, h=360, torn=False, page="castle"):
    """A big open storybook seen from above (for close-ups). Centre x, y."""
    c.rect(x - w / 2 - 14, y - h / 2 - 10, x + w / 2 + 14, y + h / 2 + 14, BOOK_D, r=10)
    c.rect(x - w / 2, y - h / 2, x, y + h / 2, PAPER, w=2.5)
    if torn:
        # right page torn out: ragged stub
        pts = [(x, y - h / 2)]
        for k in range(14):
            pts.append((x + 26 + (8 if k % 2 else 0), y - h / 2 + h * k / 13))
        pts.append((x, y + h / 2))
        c.poly(pts, PAPER, w=2.5)
        c.rect(x + 50, y - h / 2, x + w / 2, y + h / 2, mix(BOOK_D, (0, 0, 0), 0.15), ol=None)
        c.text(x + w / 4 + 20, y, "?", 90, mix(BOOK_D, (255, 255, 255), 0.3))
    else:
        c.rect(x, y - h / 2, x + w / 2, y + h / 2, PAPER, w=2.5)
    c.line([(x, y - h / 2), (x, y + h / 2)], mix(PAPER, (0, 0, 0), 0.3), 3)
    return (x - w / 2, y - h / 2, x, y + h / 2)


def castle_painting(w, h, night=False):
    """A little storybook painting of the castle (an Image of w x h output px, supersampled)."""
    sky = [(0, (255, 214, 170)), (0.6, (250, 236, 210)), (1, (250, 236, 210))] if not night else \
        [(0, (30, 36, 80)), (1, (80, 76, 130))]
    pc = Canvas(D.gradient(w * SS, h * SS, sky), size=(w, h))
    alp(pc, w * 0.2, h * 0.75, w * 0.6, h * 0.45, seed=1, ol=None)
    alp(pc, w * 0.85, h * 0.75, w * 0.5, h * 0.38, seed=2, ol=None)
    pc.poly([(0, h * 0.72), (w * 0.4, h * 0.6), (w, h * 0.7), (w, h), (0, h)], (90, 140, 90), ol=None)
    pc.poly([(w * 0.3, h), (w * 0.38, h * 0.66), (w * 0.62, h * 0.64), (w * 0.72, h)], (150, 140, 136), ol=None)
    neuschwanstein(pc, w * 0.5, h * 0.66, w / 1000, lit=1.0 if night else 0.0, night=1.0 if night else 0.0,
                   ol=(90, 80, 90))
    pc.ellipse(w * 0.5, h * 0.93, w * 0.5, h * 0.07, (120, 170, 210), ol=None)
    return pc.img


# =================================================================== parcel

def parcel(c, x, y, s=1.0, lid=0.0, label=True, stamp="", w=200, h=120, front=True, back=True):
    """Cardboard parcel, origin bottom centre. lid: 0 closed, 1 flaps open.
    back/front let a scene draw cats between the back and the front of the box."""
    c.push(x, y, s)
    hw = w / 2
    d = 24
    if back and lid > 0.5:
        c.poly([(-hw + d, -h - d), (hw + d, -h - d), (hw + d - 10, -h - d - 56), (-hw + d + 10, -h - d - 56)],
               mix(CARD, (255, 255, 255), 0.08), w=2.5)                                          # back flap up
        c.poly([(-hw, -h), (-hw + d, -h - d), (hw + d, -h - d), (hw, -h)], mix(CARD_D, (40, 20, 10), 0.45), w=2.5)
    if front:
        c.rect(-hw, -h, hw, 0, CARD, w=2.5)
        c.poly([(hw, -h), (hw + d, -h - d), (hw + d, -d), (hw, 0)], CARD_D, w=2.5)
        if lid > 0.5:
            c.poly([(-hw, -h), (-hw - 20, -h - 50), (-hw + 8, -h - 46), (-hw + d, -h - d)], CARD, w=2)   # side flaps
            c.poly([(hw + d, -h - d), (hw + d + 26, -h - 60), (hw + d + 12, -h - 30), (hw, -h)], CARD_D, w=2)
            c.poly([(-hw, -h), (hw, -h), (hw - 4, -h + 40), (-hw + 4, -h + 40)], mix(CARD, (0, 0, 0), 0.08), w=2.5)
        else:
            c.poly([(-hw, -h), (-hw + d, -h - d), (hw + d, -h - d), (hw, -h)], mix(CARD, (255, 255, 255), 0.1), w=2.5)
            c.poly([(-10 + 12, -h - d), (10 + 12, -h - d), (10, -h), (-10, -h)], (232, 216, 172), ol=None)
            c.rect(-10, -h, 10, 0, (232, 216, 172), ol=None)                                     # tape
        if label and not stamp:
            c.rect(hw - 86, -h + 50, hw - 12, -h + 98, (255, 252, 240), w=2)
            for k in range(3):
                c.line([(hw - 78, -h + 64 + k * 11), (hw - 26 - 10 * (k == 2), -h + 64 + k * 11)], (90, 90, 120), 2)
            c.rect(hw - 30, -h + 53, hw - 16, -h + 61, (220, 60, 60), ol=None)
        if stamp:
            c.push(-hw + 62, -h + 76)
            c.rect(-56, -15, 56, 15, None, ol=(200, 40, 40), w=3, r=4)
            c.text(0, 0, stamp, 10, (200, 40, 40))
            c.pop()
    c.pop()


def stamp_mark(c, x, y, s=1.0, ang=0.0):
    """A postage stamp (stuck on Whiskers' forehead): perforated edge, a tiny post horn."""
    c.push(x, y, s)
    pts = rot([(-12, -14), (12, -14), (12, 14), (-12, 14)], ang)
    c.poly(pts, (255, 252, 240), ol=OUT, w=1.5)
    inner = rot([(-9, -11), (9, -11), (9, 11), (-9, 11)], ang)
    c.poly(inner, (230, 80, 80), ol=None)
    c.circle(*rot([(0, 0)], ang)[0], 4, POST_YELLOW, ol=None)
    c.pop()


# ===================================================================== van

def post_van(c, x, y, s=1.0, face=1, t=0.0, wheel=0.0, lights=0.0, open_door=0.0):
    """The little yellow post van, origin bottom centre, ~330 long."""
    c.push(x, y, s, flip=face < 0)
    body = POST_YELLOW
    dark = (214, 160, 20)
    c.rect(-160, -150, 90, -26, body, w=3, r=10)                # box
    c.poly([(90, -120), (128, -116), (160, -70), (164, -26), (90, -26)], body, w=3)   # cab
    c.poly([(98, -112), (126, -110), (150, -74), (98, -74)], (170, 210, 235), w=2)    # windscreen
    c.line([(104, -106), (114, -86)], (235, 245, 255), 3)
    c.rect(-160, -40, 164, -26, dark, w=2)                      # sill
    c.rect(154, -52, 168, -36, (255, 250, 220) if lights < 0.5 else (255, 240, 160), w=2, r=3)
    c.rect(-164, -60, -156, -40, (220, 60, 50), w=1.5, r=2)
    # black post horn emblem
    c.push(-35, -90)
    c.arc(0, 0, 26, 18, 200, 520, (30, 30, 30), 6)
    c.circle(26, 2, 8, (30, 30, 30), ol=None)
    c.poly([(-26, -4), (-40, -12), (-40, 8)], (30, 30, 30), ol=None)
    c.pop()
    c.line([(-150, -138), (80, -138)], mix(body, (255, 255, 255), 0.4), 3)
    if open_door > 0:
        c.rect(-160, -146, -160 - 60 * open_door, -30, dark, w=2.5)
    for wx in (-110, 110):
        c.circle(wx, -18, 22, (40, 40, 46), w=3)
        c.circle(wx, -18, 10, (190, 190, 200), w=2)
        for k in range(3):
            a = wheel + k * 2.094
            c.line([(wx, -18), (wx + 9 * math.cos(a), -18 + 9 * math.sin(a))], (100, 100, 110), 2)
    if lights > 0:
        c.poly([(166, -46), (420, -90), (420, 10)], mix((255, 240, 170), (255, 255, 255), 0.2), ol=None)
    c.pop()


def headlight_beam(c, x, y, s, face, k):
    pass


# ================================================================== pretzel

def pretzel(c, x, y, r=40, ang=0.0, bite=0.0):
    """A big Bavarian pretzel centred at x, y, radius r, rotated by ang."""
    th = r * 0.24

    def P(px, py):
        return rot([(px * r, py * r)], ang)[0]
    loop_l = [P(-0.48 + 0.42 * math.cos(a), -0.05 + 0.5 * math.sin(a)) for a in np.linspace(0, math.tau, 26)]
    loop_r = [P(0.48 + 0.42 * math.cos(a), -0.05 + 0.5 * math.sin(a)) for a in np.linspace(0, math.tau, 26)]
    c.push(x, y)
    # outer belly arc
    belly = [P(0.95 * math.cos(a), 0.15 + 0.78 * math.sin(a)) for a in np.linspace(math.pi * 1.05, math.pi * 1.95, 18)]
    belly = [P(0.95 * math.cos(a), -0.1 + 0.85 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 20)]
    belly = [(px, -py) for px, py in belly]
    for pts in (belly, loop_l, loop_r):
        c.line(pts, OUT, th + 5)
    for pts in (belly, loop_l, loop_r):
        c.line(pts, PRETZEL, th)
    # crossed arms in the middle
    c.line([P(-0.4, 0.75), P(0.35, -0.2)], OUT, th + 5)
    c.line([P(0.4, 0.75), P(-0.35, -0.2)], OUT, th + 5)
    c.line([P(-0.4, 0.75), P(0.35, -0.2)], PRETZEL, th)
    c.line([P(0.4, 0.75), P(-0.35, -0.2)], PRETZEL, th)
    for pts in (belly[3:-3], loop_l[2:9]):
        c.line(pts, PRETZEL_L, th * 0.3)
    rng = np.random.default_rng(5)
    for _ in range(14):
        a = rng.uniform(0, math.tau)
        u = rng.choice([0, 1, 2])
        if u == 0:
            px, py = 0.95 * math.cos(a), 0.1 - abs(0.85 * math.sin(a))
            px, py = px, -(-0.1 + 0.85 * -abs(math.sin(a)))
        cx_, cy_ = (-0.48 if u == 1 else 0.48), -0.05
        if u:
            px, py = cx_ + 0.42 * math.cos(a), cy_ + 0.5 * math.sin(a)
        else:
            px, py = 0.95 * math.cos(a), 0.1 + 0.85 * abs(math.sin(a))
        q = P(px, py)
        c.rect(q[0] - 1.6, q[1] - 1.2, q[0] + 1.6, q[1] + 1.2, (255, 255, 255), ol=None)
    c.pop()


# ================================================================== strudel

def strudel(c, x, y, s=1.0, eaten=0.0, cream=0.0):
    """Apple strudel on a plate with a heap of whipped cream. origin = plate centre."""
    c.push(x, y, s)
    c.ellipse(0, 0, 90, 18, (250, 250, 255), w=2.5)
    c.ellipse(0, -2, 70, 12, (230, 234, 245), ol=None)
    L = 120 * (1 - eaten)
    if L > 4:
        x0 = -60
        c.rect(x0, -38, x0 + L, -4, (226, 178, 98), w=2.5, r=14)
        for k in range(int(L // 22)):
            c.line([(x0 + 14 + k * 22, -34), (x0 + 6 + k * 22, -14)], (190, 130, 60), 2.5)
        c.rect(x0 + L - 8, -34, x0 + L, -8, (240, 210, 140), ol=None)
        # icing sugar
        for k in range(10):
            c.circle(x0 + 8 + (k * 37) % max(10, L - 10), -34 + (k % 3) * 2, 1.6, (255, 255, 255), ol=None)
    if cream > 0.02:
        h = 24 + 70 * cream
        c.push(48, -6)
        pts = [(-34 - 10 * cream, 0), (-26, -h * 0.35), (-30, -h * 0.4), (-16, -h * 0.7), (-20, -h * 0.72),
               (0, -h), (20, -h * 0.72), (16, -h * 0.7), (30, -h * 0.4), (26, -h * 0.35), (34 + 10 * cream, 0)]
        c.poly(pts, (255, 253, 245), w=2.5)
        c.line([(-22, -h * 0.3), (14, -h * 0.5)], (232, 230, 236), 2)
        c.pop()
    c.pop()


def cream_beard(c, x, y, s=1.0, face=1, k=1.0):
    """Whipped-cream beard on a sitting cat's chin (cat at x, y, scale s, facing face)."""
    if k <= 0.02:
        return
    c.push(x, y, s, flip=face < 0)
    hx, hy = 18, -106
    for dx, dy, r in ((6, 26, 14), (18, 30, 16), (30, 26, 13), (12, 40, 12), (24, 42, 11), (18, 52, 9)):
        c.circle(hx + dx, hy + dy, r * k, (255, 253, 245), w=2)
    for dx, dy, r in ((6, 26, 12), (18, 30, 14), (30, 26, 11), (12, 40, 10), (24, 42, 9)):
        c.circle(hx + dx, hy + dy, r * k, (255, 253, 245), ol=None)
    c.circle(hx + 4, hy - 30, 6 * k, (255, 253, 245), w=1.5)       # dollop on the head
    c.pop()


# ================================================================= village

def painted_house(c, x, y, w=220, h=170, wall=(250, 240, 214), roof=(150, 70, 52), shutter=(60, 120, 80),
                  mural=(120, 160, 200), seed=0, balcony=True, door=True, night=0.0):
    """A Bavarian house with painted window frames, flower boxes and a wooden balcony. origin bottom centre."""
    rng = np.random.default_rng(seed)
    c.push(x, y)
    hw = w / 2
    c.rect(-hw, -h, hw, 0, wall, w=2.5)
    c.rect(-hw, -h, -hw + 12, 0, mix(wall, (0, 0, 0), 0.08), ol=None)
    # roof: wide overhanging gable
    c.poly([(-hw - 26, -h + 4), (0, -h - w * 0.36), (hw + 26, -h + 4)], roof, w=2.5)
    c.poly([(0, -h - w * 0.36), (hw + 26, -h + 4), (hw * 0.2, -h + 4)], mix(roof, (0, 0, 0), 0.18), ol=None)
    c.poly([(-hw - 26, -h + 4), (0, -h - w * 0.36), (hw + 26, -h + 4), (hw + 14, -h + 4), (0, -h - w * 0.36 + 14),
            (-hw - 14, -h + 4)], mix(roof, (255, 255, 255), 0.15), ol=None)
    # gable window
    c.rect(-12, -h - 46, 12, -h - 18, (90, 110, 140), w=2)
    # mural in the gable / between windows (Lueftlmalerei)
    my = -h + 46
    c.circle(0, my, 15, mix(wall, mural, 0.6), ol=None)
    c.circle(0, my, 9, mix(wall, (230, 190, 80), 0.6), ol=None)
    for k in range(6):
        a = k * math.pi / 3
        c.ellipse(math.cos(a) * 21, my + math.sin(a) * 21, 4.5, 4.5, mix(wall, (200, 80, 80), 0.5), ol=None)
    winc = mix((90, 110, 140), (255, 210, 110), night)
    for row, wy in enumerate((-h + 24, -56)):
        for wx in (-hw * 0.6, hw * 0.6):
            c.rect(wx - 16, wy, wx + 16, wy + 34, winc, w=2)
            c.line([(wx, wy), (wx, wy + 34)], (250, 250, 250), 2)
            # painted frame
            c.rect(wx - 22, wy - 6, wx + 22, wy - 1, mix(wall, mural, 0.7), ol=None)
            c.poly([(wx - 22, wy - 6), (wx, wy - 16), (wx + 22, wy - 6)], mix(wall, mural, 0.7), ol=None)
            c.rect(wx - 30, wy, wx - 18, wy + 34, shutter, w=1.5)
            c.rect(wx + 18, wy, wx + 30, wy + 34, shutter, w=1.5)
            # flower box
            c.rect(wx - 20, wy + 34, wx + 20, wy + 42, (140, 90, 50), w=1.5)
            for k in range(5):
                c.circle(wx - 16 + k * 8, wy + 32, 4, ((220, 50, 60), (250, 120, 160), (230, 60, 50))[k % 3],
                         ol=None)
    if balcony:
        by = -h + 74
        c.rect(-hw - 8, by, hw + 8, by + 8, (130, 84, 50), w=2)
        for k in range(int(w // 14) + 1):
            c.rect(-hw - 6 + k * 14, by + 8, -hw + 2 + k * 14, by + 30, (150, 100, 60), ol=None)
        c.rect(-hw - 8, by + 30, hw + 8, by + 36, (130, 84, 50), w=2)
        for k in range(int(w // 30)):
            c.circle(-hw + 10 + k * 30, by + 38, 5, (230, 60, 60), ol=None)
    if door:
        c.rect(-20, -60, 20, 0, (120, 76, 46), w=2)
        c.ellipse(0, -60, 20, 14, (120, 76, 46), w=2)
        c.rect(-19, -60, 19, -2, (120, 76, 46), ol=None)
        c.circle(10, -30, 2.5, GOLD, ol=None)
    c.pop()


def maypole(c, x, y, h=420, flags=True):
    c.line([(x, y), (x, y - h)], OUT, 12)
    c.line([(x, y), (x, y - h)], (255, 255, 255), 8)
    n = int(h / 22)
    for k in range(n):
        yy = y - k * 22
        c.poly([(x - 4, yy), (x + 4, yy - 9), (x + 4, yy - 16), (x - 4, yy - 7)], BAV_BLUE, ol=None)
    for k, yy in enumerate((y - h * 0.45, y - h * 0.62, y - h * 0.78)):
        w = 50 - k * 10
        c.line([(x - w, yy), (x + w, yy)], (110, 80, 50), 3)
        for sx in (-1, 1):
            c.rect(x + sx * w - 7, yy, x + sx * w + 7, yy + 18, (250, 250, 250), w=1.5)
            c.rect(x + sx * w - 5, yy + 4, x + sx * w + 5, yy + 14, BAV_BLUE, ol=None)
    # wreath and top
    c.ellipse(x, y - h * 0.9, 26, 8, (70, 140, 70), w=2)
    for k in range(4):
        c.line([(x - 22 + k * 15, y - h * 0.9), (x - 24 + k * 15, y - h * 0.9 + 26)],
               ((230, 60, 60), BAV_BLUE, (255, 255, 255), (250, 200, 60))[k], 3)
    c.poly([(x - 10, y - h), (x, y - h - 30), (x + 10, y - h)], (70, 140, 70), w=2)


def onion_church(c, x, y, s=1.0, wall=(250, 246, 236), dome=(70, 130, 90), night=0.0):
    """Village church with a green onion dome tower. origin bottom centre of the tower."""
    c.push(x, y, s)
    c.rect(60, -140, 220, 0, wall, w=2.5)                       # nave
    c.poly([(50, -140), (140, -200), (230, -140)], (160, 74, 56), w=2.5)
    for wx in (90, 140, 190):
        c.rect(wx - 8, -110, wx + 8, -60, (90, 110, 150), w=1.5)
        c.ellipse(wx, -110, 8, 8, (90, 110, 150), w=1.5)
    c.rect(-34, -280, 34, 0, wall, w=2.5)                       # tower
    c.rect(-34, -280, -24, 0, mix(wall, (0, 0, 0), 0.08), ol=None)
    c.circle(0, -230, 18, (250, 250, 250), w=2)                 # clock
    c.line([(0, -230), (0, -242)], OUT, 2)
    c.line([(0, -230), (9, -228)], OUT, 2)
    c.rect(-12, -190, 12, -150, (90, 110, 150), w=1.5)
    c.ellipse(0, -190, 12, 10, (90, 110, 150), w=1.5)
    # onion dome
    pts = []
    for a in np.linspace(0, math.pi, 22):
        r = 44 * math.sin(a) ** 0.8 * (1 - 0.35 * (1 - math.cos(a)) / 2)
        pts.append((0, 0))
    prof = [(26, -280), (40, -296), (44, -314), (36, -334), (18, -348), (6, -360), (6, -368), (12, -376),
            (6, -390), (0, -400)]
    pts = prof + [(-px, py) for px, py in reversed(prof)]
    c.poly(pts, dome, w=2.5)
    c.poly(prof + [(0, -280)], mix(dome, (0, 0, 0), 0.2), ol=None)
    c.line([(0, -400), (0, -430)], GOLD, 3)
    c.line([(-8, -418), (8, -418)], GOLD, 3)
    c.pop()


# ===================================================================== square

def town_hall(c, x, y, s=1.0, t=0.0, spin=0.0):
    """Munich's New Town Hall: dark neo-gothic facade, tall tower with the Glockenspiel.
    origin = bottom centre of the tower. spin: phase of the dancing figures."""
    st = (150, 130, 112)
    st_d = (118, 100, 88)
    st_l = (176, 158, 138)
    c.push(x, y, s)
    # long facade, both sides of the tower
    for x0, x1 in ((-520, -60), (60, 520)):
        c.rect(x0, -330, x1, 0, st, w=2.5)
        # gothic gables along the roof line
        n = int((x1 - x0) // 92)
        for k in range(n):
            gx = x0 + 46 + k * 92
            c.poly([(gx - 40, -330), (gx, -400), (gx + 40, -330)], st, w=2)
            c.poly([(gx - 30, -334), (gx, -386), (gx + 30, -334)], st_d, ol=None)
            c.line([(gx, -400), (gx, -416)], st_d, 3)
            c.rect(gx - 12, -372, gx + 12, -340, (70, 70, 90), ol=None)
            c.ellipse(gx, -372, 12, 10, (70, 70, 90), ol=None)
        # arched windows: 3 rows
        for row, wy in enumerate((-290, -210, -130)):
            for k in range(n):
                wx = x0 + 46 + k * 92
                for dx in (-18, 18):
                    c.rect(wx + dx - 9, wy, wx + dx + 9, wy + 46, (70, 76, 96), w=1.5)
                    c.ellipse(wx + dx, wy, 9, 9, (70, 76, 96), w=1.5)
                    c.rect(wx + dx - 8, wy, wx + dx + 8, wy + 45, (70, 76, 96), ol=None)
        # arcade at street level
        for k in range(n * 2):
            ax = x0 + 23 + k * 46
            c.rect(ax - 16, -60, ax + 16, 0, (60, 52, 50), w=1.5)
            c.ellipse(ax, -60, 16, 16, (60, 52, 50), w=1.5)
            c.rect(ax - 15, -60, ax + 15, -1, (60, 52, 50), ol=None)
        c.rect(x0, -76, x1, -68, st_l, ol=None)
        c.rect(x0, -330, x1, -320, st_l, ol=None)
    # the tower
    c.rect(-60, -720, 60, 0, st_l, w=2.5)
    c.rect(-60, -720, -46, 0, st, ol=None)
    for wy in (-640, -560):
        c.rect(-14, wy, 14, wy + 50, (70, 76, 96), w=1.5)
        c.ellipse(0, wy, 14, 12, (70, 76, 96), w=1.5)
    # clock
    c.circle(0, -690, 22, (250, 246, 230), w=2)
    c.line([(0, -690), (0, -706)], OUT, 2.5)
    c.line([(0, -690), (12, -686)], OUT, 2.5)
    # glockenspiel: two balconies (oriels) with little figures
    for k, (by, fy) in enumerate(((-480, -486), (-380, -386))):
        c.rect(-80, by, 80, by + 12, st_d, w=2)
        c.rect(-74, by - 74, 74, by, (90, 70, 66), w=2)
        c.rect(-74, by - 74, 74, by - 66, st_d, ol=None)
    # spire top: octagonal top with small green domes
    c.rect(-50, -780, 50, -720, st_l, w=2.5)
    for k in range(6):
        c.rect(-52 + k * 18, -796, -44 + k * 18, -780, st_l, w=1.5)
    c.poly([(-36, -796), (0, -880), (36, -796)], (90, 140, 120), w=2.5)
    c.circle(0, -884, 6, GOLD, w=1.5)
    for sx in (-56, 56):
        c.rect(sx - 8, -780, sx + 8, -730, st_l, w=1.5)
        c.poly([(sx - 10, -780), (sx, -812), (sx + 10, -780)], (90, 140, 120), w=1.5)
    c.pop()


def glock_figures(c, x, y, s=1.0, spin=0.0):
    """The Glockenspiel's little figures on their turntables (drawn over town_hall's oriels)."""
    c.push(x, y, s)
    for k, (by, fy) in enumerate(((-480, -486), (-380, -386))):
        for j in range(5):
            ph = spin * (1 if k == 0 else -1) + j * math.tau / 5
            fx = 52 * math.sin(ph)
            depth = math.cos(ph)
            if depth < -0.2:
                continue
            col = ((200, 50, 50), (60, 100, 200), (240, 200, 60), (60, 150, 80), (230, 230, 230))[j]
            hop = abs(math.sin(spin * 4 + j)) * 5 if k == 1 else 0
            c.rect(fx - 6, fy - 40 - hop, fx + 6, fy - 12 - hop, col, w=1.5)
            c.circle(fx, fy - 47 - hop, 6, (250, 220, 190), w=1.5)
            if k == 0:  # knights: a lance and a little horse
                c.ellipse(fx, fy - 14, 14, 8, (240, 240, 240), w=1.5)
                c.line([(fx, fy - 30), (fx + 22 * depth * (1 if j % 2 else -1), fy - 40)], (180, 150, 90), 2)
            else:       # coopers: a hoop over the head
                c.ellipse(fx, fy - 60 - hop, 10, 3, (190, 140, 60), ol=None)
            c.line([(fx - 4, fy - 12 - hop), (fx - 5, fy - hop)], OUT, 2)
            c.line([(fx + 4, fy - 12 - hop), (fx + 5, fy - hop)], OUT, 2)
    c.pop()


def frauenkirche(c, x, y, s=1.0, col=(176, 98, 70), dome=(90, 150, 120), ol=OUT):
    """The twin brick towers of the Frauenkirche with their green 'onion' caps."""
    c.push(x, y, s)
    for tx in (-70, 70):
        c.rect(tx - 44, -560, tx + 44, 0, col, ol=ol, w=2.5)
        c.rect(tx - 44, -560, tx - 32, 0, mix(col, (0, 0, 0), 0.15), ol=None)
        for wy in (-500, -400, -300):
            c.rect(tx - 10, wy, tx + 10, wy + 60, mix(col, (40, 30, 40), 0.5), ol=None)
            c.ellipse(tx, wy, 10, 10, mix(col, (40, 30, 40), 0.5), ol=None)
        prof = [(44, -560), (50, -590), (44, -620), (28, -646), (14, -664), (8, -680), (0, -690)]
        pts = [(tx + px, py) for px, py in prof] + [(tx - px, py) for px, py in reversed(prof)]
        c.poly(pts, dome, ol=ol, w=2.5)
        c.poly([(tx + px, py) for px, py in prof] + [(tx, -560)], mix(dome, (0, 0, 0), 0.2), ol=None)
        c.line([(tx, -690), (tx, -716)], GOLD, 3)
    c.rect(-26, -380, 26, 0, col, ol=ol, w=2.5)
    c.pop()


def mary_column(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-40, -30, 40, 0, (190, 180, 170), w=2.5)
    c.rect(-26, -60, 26, -30, (200, 190, 180), w=2)
    c.rect(-9, -300, 9, -60, (180, 170, 166), w=2)
    c.rect(-14, -306, 14, -296, (190, 180, 170), w=2)
    c.ellipse(0, -326, 10, 22, GOLD, w=2)
    c.circle(0, -352, 7, GOLD, w=2)
    c.ellipse(0, -362, 9, 3, GOLD, ol=None)
    c.pop()


def pretzel_stand(c, x, y, s=1.0):
    """A little wooden stall with a blue-white diamond awning and pretzels on pegs. origin bottom centre."""
    c.push(x, y, s)
    c.rect(-110, -90, 110, 0, (170, 110, 64), w=2.5)
    for k in range(5):
        c.line([(-110, -72 + k * 18), (110, -72 + k * 18)], (140, 88, 50), 2)
    c.rect(-118, -100, 118, -88, (130, 84, 50), w=2)
    for px in (-96, 96):
        c.rect(px - 5, -210, px + 5, -100, (130, 84, 50), w=2)
    # awning: Bavarian diamonds
    c.poly([(-130, -200), (130, -200), (140, -160), (-140, -160)], (255, 255, 255), w=2.5)
    for k in range(10):
        xx = -126 + k * 28
        c.poly([(xx, -180), (xx + 14, -198), (xx + 28, -180), (xx + 14, -162)], BAV_BLUE, ol=None)
    for k in range(10):
        xx = -140 + k * 28
        c.ellipse(xx + 14, -158, 14, 8, (255, 255, 255) if k % 2 else BAV_BLUE, w=2)
    # pretzels hanging
    for k, px in enumerate((-60, -10, 40)):
        pretzel(c, px, -132, 18, 0.1 * (k - 1))
    c.text(0, -46, "BREZN", 18, (255, 240, 200), stroke=2)
    c.pop()


# ================================================================= animals

RESI = dict(fur=(206, 98, 44), dark=(150, 64, 30), belly=(252, 226, 190), hat=(66, 112, 70), band=(150, 60, 50))


def resi(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", walk=0.0, hop=0.0, wave=0.0, seed=4.7,
         hold=None):
    """Resi the red squirrel: sits upright, huge bushy tail, little green Bavarian hat with a feather.
    ~120 tall at s=1 (hat top)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = RESI
    c.push(x, y - hop, s, flip=face < 0)
    # tail: big S-curve plume behind
    sway = math.sin(t * 2.4 + seed) * 4
    pts = [(-16, -10), (-38, -22), (-48, -48), (-40, -78), (-24, -96), (-30 + sway, -112)]
    for k, (px, py) in enumerate(pts):
        c.circle(px, py, 16 + 4 * math.sin(k / 5 * math.pi), p["fur"], w=2.5)
    for k, (px, py) in enumerate(pts):
        c.circle(px + 2, py, 12 + 4 * math.sin(k / 5 * math.pi), p["fur"], ol=None)
    c.circle(-30 + sway, -116, 9, p["dark"], ol=None)
    # feet
    for fx, ph in ((-4, 0), (14, math.pi)):
        lift = -max(0.0, math.cos(walk + ph)) * 5 if walk else 0
        c.ellipse(fx + (math.sin(walk + ph) * 5 if walk else 0), lift - 3, 10, 5, p["dark"], w=2)
    # body
    c.ellipse(2, -30, 20, 28, p["fur"], w=2.5)
    c.ellipse(8, -26, 12, 20, p["belly"], ol=None)
    hx, hy = 10, -66
    # ears with tufts
    for ex, ey in ((hx - 9, hy - 16), (hx + 7, hy - 18)):
        c.poly([(ex - 6, ey + 6), (ex, ey - 12), (ex + 6, ey + 6)], p["fur"], w=2)
        c.line([(ex, ey - 12), (ex - 2, ey - 20)], p["dark"], 3)
    c.ellipse(hx, hy, 17, 15, p["fur"], w=2.5)
    c.ellipse(hx + 10, hy + 5, 9, 7, p["belly"], ol=None)
    c.circle(hx + 17, hy + 1, 3, (60, 30, 30), ol=None)
    for ex in (hx + 4,):
        ey = hy - 3
        if eyes == "closed":
            c.arc(ex, ey, 4, 3, 20, 160, OUT, 2)
        elif eyes == "happy":
            c.arc(ex, ey + 1, 4, 4, 200, 340, OUT, 2)
        elif eyes == "wide":
            c.circle(ex, ey, 5, (255, 255, 255), w=1.5)
            c.circle(ex + 1, ey, 2.8, (25, 20, 25), ol=None)
        else:
            c.ellipse(ex, ey, 3.4, 4.2, (25, 20, 25), ol=None)
            c.circle(ex + 1.2, ey - 1.6, 1.3, (255, 255, 255), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 12, hy + 10, 3.5, 1.2 + 3.5 * mouth, D.MOUTH, w=1.5)
    else:
        c.arc(hx + 12, hy + 8, 3, 2, 0, 180, OUT, 1.5)
    # hat: green felt Tyrolean hat with a feather
    c.push(hx - 2, hy - 13)
    c.ellipse(0, 0, 17, 4, p["hat"], w=2)
    c.poly([(-10, -1), (-8, -14), (0, -17), (8, -14), (10, -1)], p["hat"], w=2)
    c.rect(-10, -5, 10, -1, p["band"], ol=None)
    c.line([(-6, -4), (-18, -24)], (240, 240, 240), 3)
    c.line([(-8, -6), (-16, -20)], (120, 120, 120), 1.5)
    c.pop()
    # arms / paws
    if wave:
        a = -1.3 + 0.5 * math.sin(t * 10)
        c.stroke([(12, -44), (12 + 20 * math.cos(a), -44 + 20 * math.sin(a))], p["fur"], 6)
    else:
        c.ellipse(16, -42, 5, 4, p["dark"], w=1.5)
        c.ellipse(8, -40, 5, 4, p["dark"], w=1.5)
    c.pop()


HORSE = dict(coat=(196, 124, 62), dark=(150, 90, 44), mane=(252, 230, 168), hoof=(70, 56, 50))


def horse(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, eyes="open", head=0.0, seed=6.1):
    """Hansl, a sturdy Haflinger: chestnut coat, blond mane. origin between the hooves, ~220 tall."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = HORSE
    c.push(x, y, s, flip=face < 0)
    by = -110
    # tail
    sw = math.sin(t * 2 + seed) * 6
    c.stroke([(-86, by - 18), (-104, by + 10 + sw * 0.3), (-100 + sw, by + 60)], p["mane"], 14)

    def leg(lx, ph, col):
        if walk:
            a = math.sin(walk + ph) * 0.35
            lift = max(0.0, math.cos(walk + ph)) * 10
        else:
            a, lift = 0.0, 0.0
        kx, ky = lx + math.sin(a) * 46, by + 50
        fx, fy = kx + math.sin(a * 0.6) * 50, -lift
        c.stroke([(lx, by + 10), (kx, ky), (fx, fy - 10)], col, 18)
        c.rect(fx - 11, fy - 14, fx + 11, fy, p["hoof"], w=2)
        c.rect(fx - 11, fy - 22, fx + 11, fy - 14, (250, 246, 236), ol=None)
    leg(-64, math.pi, p["dark"])
    leg(62, 0, p["dark"])
    c.ellipse(0, by, 100, 52, p["coat"], w=3)
    c.ellipse(10, by + 20, 70, 22, mix(p["coat"], (255, 255, 255), 0.15), ol=None)
    leg(-50, 0, p["coat"])
    leg(76, math.pi, p["coat"])
    # harness collar
    c.ellipse(80, by - 16, 16, 40, (120, 60, 40), w=2.5)
    c.circle(80, by - 50, 5, GOLD, w=1.5)
    # neck + head
    nod = math.sin(walk * 2) * 4 if walk else 0
    hd = head * 40
    hx, hy = 150, by - 70 + nod + hd
    c.poly([(60, by - 40), (100, by - 90), (hx - 10, hy - 20), (hx + 6, hy + 10), (110, by + 10), (70, by + 20)],
           p["coat"], w=3)
    c.ellipse(hx + 10, hy + 10, 40, 24, p["coat"], w=3)
    c.ellipse(hx + 40, hy + 18, 20, 18, mix(p["coat"], (255, 255, 255), 0.25), w=2.5)
    c.circle(hx + 48, hy + 14, 3, OUT, ol=None)
    c.line([(hx + 34, hy + 30), (hx + 52, hy + 30)], OUT, 2)
    c.poly([(hx - 10, hy - 6), (hx - 4, hy - 34), (hx + 6, hy - 6)], p["coat"], w=2.5)    # ear
    # blaze
    c.poly([(hx + 6, hy - 6), (hx + 18, hy - 4), (hx + 46, hy + 8), (hx + 40, hy + 12)], (250, 246, 236), ol=None)
    ex, ey = hx + 10, hy
    if eyes == "closed":
        c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
    else:
        c.circle(ex, ey, 6, (255, 255, 255), w=2)
        c.circle(ex + 1.5, ey, 3.5, (40, 30, 30), ol=None)
        c.circle(ex + 2.5, ey - 1.5, 1.2, (255, 255, 255), ol=None)
    # blond mane flopping over the neck and forelock
    for k in range(6):
        u = k / 5
        mx, my = lerp(70, hx - 8, u), lerp(by - 54, hy - 18, u)
        c.ellipse(mx - 4, my + 4 + math.sin(t * 3 + k) * 1.5, 14, 18, p["mane"], w=2)
    for k in range(6):
        u = k / 5
        mx, my = lerp(70, hx - 8, u), lerp(by - 54, hy - 18, u)
        c.ellipse(mx - 4, my + 4 + math.sin(t * 3 + k) * 1.5, 11, 15, p["mane"], ol=None)
    c.ellipse(hx + 4, hy - 12, 12, 8, p["mane"], w=2)
    c.pop()


def hay_wagon(c, x, y, s=1.0, wheel=0.0, hay=True):
    """Wooden hay wagon (shaft to the right), origin bottom centre, ~300 long."""
    c.push(x, y, s)
    if hay:
        for dx, dy, r in ((-110, -100, 40), (-60, -118, 46), (0, -122, 48), (60, -116, 44), (106, -98, 36)):
            c.circle(dx, dy, r, (240, 210, 110), w=2.5)
        for dx, dy, r in ((-110, -100, 36), (-60, -118, 42), (0, -122, 44), (60, -116, 40), (106, -98, 32)):
            c.circle(dx, dy, r, (240, 210, 110), ol=None)
        rng = np.random.default_rng(2)
        for _ in range(30):
            hx, hy = rng.uniform(-130, 130), rng.uniform(-150, -80)
            c.line([(hx, hy), (hx + rng.uniform(-10, 10), hy + rng.uniform(-8, 8))], (200, 160, 70), 1.5)
    c.rect(-150, -86, 150, -50, (166, 108, 62), w=2.5)
    for k in range(6):
        c.line([(-150 + k * 60, -86), (-150 + k * 60, -50)], (130, 84, 50), 2)
    c.line([(150, -60), (250, -70)], (130, 84, 50), 6)
    for wx in (-100, 100):
        c.circle(wx, -34, 34, (150, 96, 56), w=3)
        c.circle(wx, -34, 26, (190, 140, 90), ol=None)
        for k in range(6):
            a = wheel + k * math.pi / 3
            c.line([(wx, -34), (wx + 28 * math.cos(a), -34 + 28 * math.sin(a))], (130, 84, 50), 3)
        c.circle(wx, -34, 7, (110, 70, 44), w=2)
    c.pop()


DEER = dict(coat=(170, 112, 70), dark=(126, 80, 50), light=(236, 214, 180))


def deer(c, x, y, s=1.0, face=1, t=0.0, bow=0.0, antlers=True, eyes="open", seed=7.0, fawn=False):
    """A roe deer standing side-on; bow lowers the head. origin between the hooves (~180 tall)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = DEER
    c.push(x, y, s, flip=face < 0)
    by = -96
    for lx, col in ((-44, p["dark"]), (40, p["dark"]), (-32, p["coat"]), (52, p["coat"])):
        c.stroke([(lx, by + 6), (lx + 2, by + 50), (lx, -4)], col, 9)
        c.ellipse(lx + 1, -3, 6, 4, OUT, ol=None)
    c.ellipse(0, by, 62, 28, p["coat"], w=2.5)
    c.ellipse(-56, by - 8, 10, 10, p["light"], w=2)            # white rump
    if fawn:
        for dx, dy in ((-20, -12), (0, -16), (20, -12), (-10, -2), (12, -2), (30, -6)):
            c.circle(dx, by + dy, 3.5, (250, 240, 220), ol=None)
    b = bow
    hx, hy = 70 + 16 * b, by - 64 + 64 * b
    c.poly([(36, by - 14), (54, by - 50 + 30 * b), (hx - 6, hy + 4), (hx + 8, hy + 14), (60, by + 10)],
           p["coat"], w=2.5)
    c.ellipse(hx + 6, hy + 6, 24, 15, p["coat"], w=2.5)
    c.ellipse(hx + 24, hy + 12, 10, 8, p["dark"], w=2)
    c.circle(hx + 31, hy + 10, 3, OUT, ol=None)
    c.ellipse(hx - 8, hy - 10, 6, 13, p["coat"], w=2)          # ears
    c.ellipse(hx + 2, hy - 13, 6, 13, p["coat"], w=2)
    if antlers and not fawn:
        c.line([(hx, hy - 12), (hx - 2, hy - 46), (hx - 12, hy - 58)], (120, 90, 60), 4)
        c.line([(hx - 2, hy - 32), (hx + 10, hy - 42)], (120, 90, 60), 4)
        c.line([(hx + 8, hy - 12), (hx + 12, hy - 44), (hx + 22, hy - 54)], (120, 90, 60), 4)
    ex, ey = hx + 8, hy
    if eyes == "closed":
        c.arc(ex, ey, 4, 3, 20, 160, OUT, 2)
    else:
        c.ellipse(ex, ey, 4, 4.5, (30, 24, 24), ol=None)
        c.circle(ex + 1, ey - 1.5, 1.3, (255, 255, 255), ol=None)
    c.pop()


def glow_eyes(c, x, y, t, s=1.0, seed=0.0):
    """Two shiny eyes in the dark."""
    if D.blink(t, seed):
        return
    for dx in (-9 * s, 9 * s):
        c.ellipse(x + dx, y, 5 * s, 4 * s, (250, 240, 150), ol=None)
        c.ellipse(x + dx, y, 2 * s, 3.5 * s, (40, 30, 20), ol=None)


SWAN = dict(white=(252, 252, 255), shade=(214, 222, 238), beak=(240, 132, 44), knob=(36, 30, 36))


def swan(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", swim=True, crown=False, specs=False,
         wing=0.0, seed=8.0, bob=True, tint=None):
    """A swan. swim: sitting on the water (origin = waterline centre); otherwise standing on webbed feet
    (origin = between the feet). Ludwig wears a crown and round spectacles. ~150 tall at s=1."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    p = SWAN
    wh, sh = p["white"], p["shade"]
    if tint:
        wh, sh = mix(wh, tint[0], tint[1]), mix(sh, tint[0], tint[1])
    yb = math.sin(t * 1.6 + seed) * 2 if (swim and bob) else 0
    c.push(x, y + yb, s, flip=face < 0)
    if not swim:
        for fx in (-12, 14):
            c.stroke([(fx, -50), (fx, -6)], (60, 56, 60), 6)
            c.poly([(fx - 10, 0), (fx + 14, 0), (fx + 2, -8)], (60, 56, 60), w=1.5)
        c.push(0, -42)
    # body: a plump teardrop with an upturned tail
    c.poly([(-78, -44), (-58, -34), (-40, -28)], wh, w=2)                    # tail tip
    c.ellipse(-4, -26, 62, 28, wh, w=2.5)
    if swim:
        c.rect(-60, -24, 56, 0, wh, ol=None)
        c.line([(-64, -1), (60, -1)], OUT, 2.5)
    wa = wing
    c.poly([(-56, -34), (-30, -54 - 34 * wa), (10, -62 - 44 * wa), (40, -48 - 22 * wa), (30, -30), (-20, -20)],
           sh, w=2)
    for k in range(3):
        c.line([(-34 + k * 20, -30), (-26 + k * 20, -48 - 28 * wa)], mix(sh, (150, 160, 190), 0.4), 1.5)
    # neck: S-curve
    nx = [44, 54, 50, 36, 34, 44]
    ny = [-34, -60, -84, -104, -124, -138]
    pts = list(zip(nx, ny))
    c.stroke(pts, wh, 18)
    hx, hy = 52, -142
    c.ellipse(hx, hy, 17, 13, wh, w=2.5)
    c.stroke(pts[-3:], wh, 14, ol=None)
    # face: black patch, beak with knob
    c.poly([(hx + 6, hy - 6), (hx + 18, hy - 4), (hx + 18, hy + 6), (hx + 8, hy + 4)], p["knob"], ol=None)
    c.circle(hx + 20, hy - 6, 4, p["knob"], ol=None)
    jaw = mouth * 8
    c.poly([(hx + 16, hy - 4), (hx + 44, hy + 2), (hx + 42, hy + 6), (hx + 16, hy + 4)], p["beak"], w=2)
    c.poly([(hx + 16, hy + 4), (hx + 40, hy + 7 + jaw), (hx + 36, hy + 10 + jaw), (hx + 14, hy + 8)],
           mix(p["beak"], (0, 0, 0), 0.15), w=2)
    ex, ey = hx + 4, hy - 4
    if eyes == "closed":
        c.arc(ex, ey, 4, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(ex, ey + 1, 4, 4, 200, 340, OUT, 2)
    else:
        c.circle(ex, ey, 3, (25, 20, 25), ol=None)
        c.circle(ex + 1, ey - 1, 1, (255, 255, 255), ol=None)
    if specs:
        c.circle(ex + 1, ey, 7, None, w=1.5)
        c.line([(ex - 6, ey - 1), (hx - 14, hy - 4)], OUT, 1.5)
    if crown:
        cx_, cy_ = hx - 2, hy - 12
        c.poly([(cx_ - 11, cy_), (cx_ - 12, cy_ - 14), (cx_ - 6, cy_ - 7), (cx_, cy_ - 17), (cx_ + 6, cy_ - 7),
                (cx_ + 12, cy_ - 14), (cx_ + 11, cy_)], GOLD, w=1.8)
        c.circle(cx_, cy_ - 4, 2, (220, 60, 80), ol=None)
    if not swim:
        c.pop()
    c.pop()


def ripple(c, x, y, t, w=60, col=(200, 220, 250), seed=0.0):
    for k in range(2):
        u = (t * 0.6 + k * 0.5 + seed) % 1.0
        c.ellipse(x, y, w * (0.6 + 0.6 * u), 5 * (0.6 + 0.6 * u), None, ol=mix(col, (60, 80, 120), u), w=2)


def quill(c, x, y, s=1.0, ang=-0.6):
    c.push(x, y, s)
    pts = rot([(0, 0), (8, -30), (14, -80), (4, -110), (-6, -80), (-4, -30)], ang)
    c.poly(pts, (255, 255, 255), w=2)
    c.line(rot([(0, 0), (4, -106)], ang), (180, 180, 190), 1.5)
    c.line(rot([(0, 0), (0, 8)], ang), OUT, 2)
    c.pop()


def sparkles(c, x, y, t, n=10, r=60, seed=0, col=(255, 240, 160)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        a = rng.uniform(0, math.tau) + t * 0.6
        rr = r * rng.uniform(0.3, 1.0)
        tw = 0.5 + 0.5 * math.sin(t * 6 + k * 1.7)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        sz = 3 + 5 * tw
        c.poly([(px - sz, py), (px, py - sz * 0.3), (px + sz, py), (px, py + sz * 0.3)], col, ol=None)
        c.poly([(px, py - sz), (px + sz * 0.3, py), (px, py + sz), (px - sz * 0.3, py)], col, ol=None)


# ============================================================== helpers

def overlay(c, col, alpha):
    if alpha <= 0.003:
        return
    c.img = Image.blend(c.img, Image.new("RGB", c.img.size, col), min(1.0, alpha))
    c.d = ImageDraw.Draw(c.img)


_shade_masks = {}


def shade_bottom(c, tl, t, strength=0.5, top=548):
    """Darken the bottom of the frame softly while a subtitle shows (readability on bright scenes)."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    if k <= 0:
        return
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    if q not in _shade_masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _shade_masks[q] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((16, 18, 34), (0, top * SS, W * SS, H * SS), _shade_masks[q])
