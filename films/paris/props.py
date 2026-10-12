"""Paris props and new characters, drawn with draw.Canvas primitives.

Landmarks (Eiffel Tower, Sacre-Coeur, Louvre pyramid), Haussmann buildings,
a riverboat, a train, a picnic basket, croissants -- and the locals: Colette
(a chic white cat with a beret), Monsieur Gaston (bulldog baker) and Pierre
(a painter pigeon).
"""
import math

import numpy as np

import draw as D
from draw import OUT, mix, clamp

COLETTE = dict(body=(246, 243, 238), dark=(214, 208, 204), belly=(255, 255, 255),
               ear=(255, 176, 190), eye=(120, 196, 110), stripes=False, collar=(225, 60, 95))
FLOUR = (250, 248, 242)


def floured(pal, k):
    """A palette dusted with flour (k = 0..1)."""
    if k <= 0:
        return pal
    return dict(pal, body=mix(pal["body"], FLOUR, k), dark=mix(pal["dark"], (225, 222, 215), k),
                belly=mix(pal["belly"], FLOUR, k), ear=mix(pal["ear"], FLOUR, k * 0.6))


# ------------------------------------------------------------- head spots

def head_pos(pose, walk=0.0, head_dy=0.0):
    """Where draw.cat puts the head centre (cat-local coordinates)."""
    if pose == "sit":
        return 18, -106 + head_dy
    if pose == "crouch":
        return 52, -64 + head_dy
    if pose == "leap":
        return 58, -74
    if pose == "sleep":
        return 46, -40
    bob = math.sin(walk * 2) * 2 if walk else 0
    return 52, -86 + bob + head_dy


def beret(c, x, y, s, face, pose, walk=0.0, head_dy=0.0, col=(205, 40, 60)):
    hx, hy = head_pos(pose, walk, head_dy)
    c.push(x, y, s, flip=face < 0)
    c.ellipse(hx - 2, hy - 30, 27, 11, col)
    c.ellipse(hx + 2, hy - 36, 16, 6, mix(col, (255, 255, 255), 0.15), ol=None)
    c.line([(hx - 2, hy - 41), (hx + 1, hy - 47)], OUT, 3)
    c.pop()


# ------------------------------------------------------------------ food

def croissant(c, x, y, s=1.0, ang=0.0, col=(226, 160, 70)):
    c.push(x, y, s)
    dark = mix(col, (150, 80, 30), 0.45)
    segs = [(-22, 4, 8, 6), (-12, -2, 10, 9), (0, -5, 12, 11), (12, -2, 10, 9), (22, 4, 8, 6)]
    ca, sa = math.cos(ang), math.sin(ang)
    for k, (dx, dy, rx, ry) in enumerate(segs):
        px, py = dx * ca - dy * sa, dx * sa + dy * ca
        c.ellipse(px, py, rx, ry, col if k % 2 == 0 else mix(col, dark, 0.3), w=2)
    for dx, dy in ((-12, -2), (0, -5), (12, -2)):
        px, py = dx * ca - dy * sa, dx * sa + dy * ca
        c.circle(px - 3, py - 4, 2.2, mix(col, (255, 240, 200), 0.6), ol=None)
    c.pop()


def baguette(c, x, y, s=1.0, ang=-0.3):
    c.push(x, y, s)
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for k in range(13):
        u = k / 12 * math.tau
        px, py = 50 * math.cos(u), 8 * math.sin(u)
        pts.append((px * ca - py * sa, px * sa + py * ca))
    c.poly(pts, (222, 170, 90), w=2)
    for k in (-30, -12, 6, 24):
        a = (k * ca - (-3) * sa, k * sa + (-3) * ca)
        b = ((k + 10) * ca - (-5) * sa, (k + 10) * sa + (-5) * ca)
        c.line([a, b], (245, 215, 150), 2.5)
    c.pop()


# ------------------------------------------------------------ landmarks

def eiffel(c, x, y, h, col=(150, 104, 74), lat=None, lights=0.0, sparkle=0.0, t=0.0, ol=OUT, w=2.0,
           glow_sky=None):
    """The Eiffel Tower standing at (x, y) with height h.

    lights: 0..1 golden night lighting. sparkle: 0..1 amount of white twinkles.
    """
    lat = lat or mix(col, (40, 26, 30), 0.35)
    hw0 = 0.22 * h

    def hw(u):
        return hw0 * (1 - u) ** 2.6 + 0.012 * h

    if lights > 0 and glow_sky is not None:
        c.glow(x, y - 0.45 * h, 0.35 * h, 0.6 * h, mix(glow_sky, (255, 200, 110), 0.35 * lights), glow_sky,
               steps=8)
    body = mix(col, (255, 196, 90), lights * 0.85)
    lat = mix(lat, (210, 130, 50), lights * 0.8)
    # legs with the big arch
    a, b = hw0 * 0.62, 0.13 * h
    up = 0.17
    for side in (-1, 1):
        pts = [(x + side * hw(0), y), (x + side * hw(up * 0.5), y - up * 0.5 * h), (x + side * hw(up), y - up * h),
               (x, y - up * h)]
        for k in range(10, -1, -1):
            th = math.radians(90 * k / 10)
            pts.append((x + side * a * math.cos(th), y - b * math.sin(th)))
        c.poly(pts, body, ol=ol, w=w)
        # lattice X in the leg
        xo, xi = x + side * hw(0) * 0.86, x + side * a * 1.08
        c.line([(xo, y - 2), (x + side * hw(up) * 0.7, y - up * h * 0.95)], lat, w * 0.7, cap=False)
        c.line([(xi, y - 2), (x + side * hw(up) * 0.9, y - up * h * 0.6)], lat, w * 0.7, cap=False)
    # first platform
    c.rect(x - hw(up) - 0.02 * h, y - (up + 0.03) * h, x + hw(up) + 0.02 * h, y - up * h, body, ol=ol, w=w)
    # middle section
    u0, u1 = up + 0.03, 0.40
    c.poly([(x - hw(u0), y - u0 * h), (x - hw(u1), y - u1 * h), (x + hw(u1), y - u1 * h), (x + hw(u0), y - u0 * h)],
           body, ol=ol, w=w)
    c.ellipse(x, y - u0 * h, hw(u0) * 0.55, 0.05 * h, mix(body, lat, 0.5), ol=None)
    for k in range(3):
        v0, v1 = u0 + (u1 - u0) * k / 3, u0 + (u1 - u0) * (k + 1) / 3
        c.line([(x - hw(v0) * 0.9, y - v0 * h), (x + hw(v1) * 0.9, y - v1 * h)], lat, w * 0.6, cap=False)
        c.line([(x + hw(v0) * 0.9, y - v0 * h), (x - hw(v1) * 0.9, y - v1 * h)], lat, w * 0.6, cap=False)
    # second platform
    c.rect(x - hw(u1) - 0.012 * h, y - (u1 + 0.02) * h, x + hw(u1) + 0.012 * h, y - u1 * h, body, ol=ol, w=w)
    # upper spire
    u2, u3 = u1 + 0.02, 0.88
    c.poly([(x - hw(u2), y - u2 * h), (x - hw(u3), y - u3 * h), (x + hw(u3), y - u3 * h), (x + hw(u2), y - u2 * h)],
           body, ol=ol, w=w)
    n = 7
    for k in range(n):
        v0, v1 = u2 + (u3 - u2) * k / n, u2 + (u3 - u2) * (k + 1) / n
        c.line([(x - hw(v0) * 0.85, y - v0 * h), (x + hw(v1) * 0.85, y - v1 * h)], lat, w * 0.5, cap=False)
        c.line([(x + hw(v0) * 0.85, y - v0 * h), (x - hw(v1) * 0.85, y - v1 * h)], lat, w * 0.5, cap=False)
    # top cabin + antenna
    c.rect(x - hw(u3) - 0.01 * h, y - 0.91 * h, x + hw(u3) + 0.01 * h, y - u3 * h, body, ol=ol, w=w)
    c.line([(x, y - 0.91 * h), (x, y - 1.0 * h)], ol or body, w * 1.2, cap=False)
    if lights > 0:
        c.circle(x, y - 1.0 * h, 0.012 * h + 1, mix(body, (255, 255, 230), lights), ol=None)
    if sparkle > 0:
        rng = np.random.default_rng(int(t * 12))
        for _ in range(int(70 * sparkle)):
            u = rng.uniform(0.0, 0.95) ** 0.8
            sx = x + rng.uniform(-1, 1) * hw(u) * 0.95
            sy = y - u * h
            r = rng.uniform(0.6, 1.6) * max(1.5, 0.008 * h)
            c.circle(sx, sy, r * 1.8, (255, 250, 210), ol=None)
            c.line([(sx - r * 3.2, sy), (sx + r * 3.2, sy)], (255, 255, 255), max(0.8, r * 0.5), cap=False)
            c.line([(sx, sy - r * 3.2), (sx, sy + r * 3.2)], (255, 255, 255), max(0.8, r * 0.5), cap=False)


def sacre_coeur(c, x, y, s=1.0, col=(246, 242, 232), shade=(214, 208, 196), tint_win=(120, 110, 130)):
    """The white basilica on its hill: base at y, centred on x."""
    c.push(x, y, s)
    # campanile behind
    c.rect(150, -330, 196, -120, col)
    c.ellipse(173, -330, 26, 30, col)
    c.line([(173, -360), (173, -392)], OUT, 3)
    c.rect(160, -300, 186, -250, tint_win, r=10)
    # side wings
    for side in (-1, 1):
        cx = side * 150
        c.rect(cx - 70, -170, cx + 70, 0, col)
        c.rect(cx - 70, -186, cx + 70, -170, shade)
        c.ellipse(cx, -230, 44, 48, col)
        c.rect(cx - 44, -222, cx + 44, -186, col)
        c.ellipse(cx, -262, 10, 16, col)
        c.line([(cx, -278), (cx, -296)], OUT, 2.5)
        for k in range(-1, 2):
            c.rect(cx + k * 34 - 9, -120, cx + k * 34 + 9, -70, tint_win, r=9)
    # central drum and great dome
    c.rect(-110, -200, 110, 0, col)
    c.rect(-70, -330, 70, -200, col)
    for k in range(-2, 3):
        c.rect(k * 26 - 8, -310, k * 26 + 8, -240, tint_win, r=8)
    c.rect(-78, -340, 78, -326, shade)
    c.poly([(-70, -340)] + [(-70 * math.cos(math.radians(a)), -340 - 120 * math.sin(math.radians(a)) ** 0.9)
                           for a in range(0, 181, 10)][1:], col)
    for k in (-35, 0, 35):
        c.arc(k * 0.6, -400, abs(k) * 0.1 + 6, 60, 200, 340, shade, 2)
    c.rect(-10, -490, 10, -455, col)
    c.ellipse(0, -492, 14, 12, col)
    c.line([(0, -504), (0, -530)], OUT, 3)
    c.line([(-8, -520), (8, -520)], OUT, 3)
    # porch with three arches
    c.rect(-110, -110, 110, 0, shade)
    c.poly([(-120, -110), (0, -150), (120, -110)], col)
    for k in (-1, 0, 1):
        c.rect(k * 62 - 22, -80, k * 62 + 22, 0, tint_win, r=22)
    c.pop()


def pyramid(c, x, y, s=1.0, glass=(140, 190, 225), frame=(70, 90, 120)):
    c.push(x, y, s)
    c.poly([(-150, 0), (0, -130), (150, 0)], glass, w=3)
    for k in range(1, 6):
        u = k / 6
        c.line([(-150 + 150 * u, -130 * u), (150 - 150 * u, -130 * u)], frame, 1.5, cap=False)
        c.line([(-150 + 300 * u, 0), (-150 + 300 * u + (150 - (-150 + 300 * u)) * 0.0, 0)], frame, 1.5, cap=False)
    for k in range(1, 8):
        u = k / 8
        c.line([(-150 + 300 * u, 0), (0, -130)], frame, 1.2, cap=False)
    c.poly([(-150, 0), (0, -130), (-40, 0)], mix(glass, (255, 255, 255), 0.35), ol=None)
    c.pop()


def building(c, x, base, w, floors, wall, roof, rng, night=0.0, shop=None):
    """A Haussmann-style building: cream stone, tall windows, iron balconies,
    blue-grey mansard roof with dormers and chimney pots."""
    fh = 52
    top = base - floors * fh - 30
    c.rect(x, top, x + w, base, wall, w=2.5)
    c.rect(x - 4, top - 6, x + w + 4, top + 4, mix(wall, (0, 0, 0), 0.15), w=2)
    # mansard roof
    c.poly([(x - 2, top - 4), (x + 16, top - 62), (x + w - 16, top - 62), (x + w + 2, top - 4)], roof, w=2.5)
    nd = max(1, int(w // 60))
    for k in range(nd):
        dx = x + w * (k + 0.5) / nd
        c.rect(dx - 11, top - 50, dx + 11, top - 16, mix(wall, (255, 255, 255), 0.3), w=2)
        c.poly([(dx - 15, top - 48), (dx, top - 62), (dx + 15, top - 48)], roof, w=2)
        lit = night > 0 and rng.random() < 0.5
        c.rect(dx - 6, top - 42, dx + 6, top - 20, (255, 214, 120) if lit else (70, 80, 110), ol=None)
    for cx in (x + 22, x + w - 30):
        c.rect(cx, top - 86, cx + 16, top - 56, mix(wall, (120, 70, 60), 0.4), w=2)
        for k in range(3):
            c.rect(cx + 1 + k * 5, top - 94, cx + 5 + k * 5, top - 86, (205, 110, 70), w=1)
    # windows
    nw = max(2, int(w // 46))
    for f in range(floors):
        wy = top + 34 + f * fh
        for k in range(nw):
            wx = x + w * (k + 0.5) / nw
            lit = night > 0 and rng.random() < 0.45
            glass = (255, 210, 110) if lit else mix((90, 110, 150), (60, 70, 100), night)
            c.rect(wx - 10, wy - 16, wx + 10, wy + 16, glass, w=2)
            c.line([(wx, wy - 16), (wx, wy + 16)], mix(wall, (255, 255, 255), 0.4), 1.5, cap=False)
            if f in (1, floors - 1):
                c.rect(wx - 15, wy + 10, wx + 15, wy + 18, None, ol=(50, 50, 60), w=1.8)
                for bx in range(-12, 15, 6):
                    c.line([(wx + bx, wy + 10), (wx + bx, wy + 18)], (50, 50, 60), 1.2, cap=False)
    if shop:
        awn, label = shop
        c.rect(x + 6, base - 70, x + w - 6, base, mix(wall, (60, 40, 40), 0.55), w=2)
        c.rect(x + 16, base - 60, x + w - 16, base - 4, (255, 226, 160) if night else (190, 210, 220), w=2)
        stripes = int((w - 4) // 18)
        for k in range(stripes):
            c.poly([(x + 2 + k * 18, base - 90), (x + 2 + (k + 1) * 18, base - 90),
                    (x + 2 + (k + 1) * 18, base - 72), (x + 2 + k * 18, base - 72)],
                   awn if k % 2 == 0 else (250, 245, 235), w=1.5)
        if label:
            c.text(x + w / 2, base - 104, label, 15, (255, 240, 200), stroke=2)
    return top


def street_lamp(c, x, y, s=1.0, lit=0.0):
    c.push(x, y, s)
    dark = (40, 46, 60)
    c.rect(-3, -150, 3, 0, dark, ol=None)
    c.rect(-9, -12, 9, 0, dark, ol=None)
    c.line([(0, -150), (16, -150), (22, -142)], dark, 3, cap=False)
    if lit > 0:
        c.glow(22, -126, 40, 40, mix((255, 230, 150), (255, 240, 180), 0.5), (255, 230, 150), steps=1)
    c.poly([(14, -142), (30, -142), (27, -114), (17, -114)], mix((210, 220, 230), (255, 225, 130), lit), w=2)
    c.pop()


def lamp_glow(c, x, y, s, sky, lit):
    """Soft halo behind a lit lamp (draw before the lamp)."""
    if lit > 0:
        c.glow(x + 22 * s, y - 128 * s, 46 * s, 46 * s, mix(sky, (255, 220, 140), 0.6 * lit), sky, steps=6)


def tree_round(c, x, y, s=1.0, leaf=(96, 160, 90)):
    c.push(x, y, s)
    c.rect(-7, -80, 7, 0, (110, 80, 60), w=2)
    for dx, dy, r in ((-26, -100, 30), (24, -102, 30), (0, -128, 36), (0, -92, 32)):
        c.circle(dx, dy, r, leaf)
    for dx, dy, r in ((-26, -100, 25), (24, -102, 25), (0, -128, 31), (0, -92, 27)):
        c.circle(dx, dy, r, leaf, ol=None)
    c.circle(-10, -134, 10, mix(leaf, (255, 255, 200), 0.25), ol=None)
    c.pop()


# ------------------------------------------------------------- vehicles

def basket(c, x, y, s=1.0, lid=0.0, tag=True, back=False):
    """Wicker picnic basket. lid: 0 closed .. 1 both flaps open.
    back=True draws only the back wall (to put cats inside, then draw front)."""
    c.push(x, y, s)
    wick, dark = (200, 150, 85), (160, 110, 60)
    if back:
        c.rect(-80, -80, 80, -40, mix(wick, (0, 0, 0), 0.35), w=2.5)
        c.pop()
        return
    c.poly([(-84, -78), (84, -78), (74, 0), (-74, 0)], wick, w=3)
    for k in range(1, 6):
        yy = -78 + k * 13
        c.line([(-84 + k * 1.7, yy), (84 - k * 1.7, yy)], dark, 2, cap=False)
    for k in range(-7, 8):
        c.line([(k * 11, -78), (k * 10, 0)], mix(wick, dark, 0.5), 1.5, cap=False)
    c.rect(-88, -84, 88, -74, dark, w=2.5, r=4)
    # handle (folds down when the lids are open)
    if lid < 0.3:
        c.arc(0, -84, 50, 46, 180, 360, OUT, 7)
        c.arc(0, -84, 50, 46, 180, 360, dark, 4)
    # lids, hinged at the sides
    if lid < 0.02:
        c.rect(-86, -92, 86, -84, wick, w=2.5, r=3)
    else:
        ang = math.radians(115 * lid)
        L = 84
        for side in (-1, 1):
            hx, hy = side * 86, -86
            ex, ey = hx - side * L * math.cos(ang), hy - L * math.sin(ang)
            nx, ny = side * 8 * math.sin(ang), -8 * math.cos(ang) * 0 + 0
            c.poly([(hx, hy), (ex, ey), (ex + side * 8 * math.sin(ang), ey + 8 * math.cos(ang) * -1 + 0),
                    (hx + side * 8 * math.sin(ang), hy)], wick, w=2.5)
    if tag:
        c.line([(60, -80), (72, -60)], OUT, 1.5, cap=False)
        c.poly([(64, -62), (92, -56), (88, -40), (60, -46)], (250, 245, 225), w=1.8)
        c.text(76, -51, "PARIS", 7, (200, 40, 50))
    c.pop()


def train(c, x, y, s=1.0, t=0.0, wheel=0.0, cars=3, steam=True, night=0.0):
    """Little steam train, locomotive at the right. (x, y) = front bottom of loco."""
    c.push(x, y, s)
    red, blue, black = (210, 60, 60), (60, 90, 170), (45, 45, 55)
    win = mix((200, 230, 245), (255, 215, 120), night)
    # carriages
    for k in range(cars):
        cx = -260 - k * 230
        col = (70, 140, 100) if k % 2 == 0 else (70, 120, 180)
        c.rect(cx - 100, -110, cx + 100, -26, col, r=8)
        c.rect(cx - 106, -122, cx + 106, -108, mix(col, (0, 0, 0), 0.3), r=6)
        for j in range(4):
            c.rect(cx - 84 + j * 44, -96, cx - 56 + j * 44, -64, win, w=2, r=4)
        c.rect(cx - 100, -40, cx + 100, -30, (240, 220, 150), ol=None)
        for wx in (cx - 60, cx + 60):
            c.circle(wx, -18, 16, black)
            c.line([(wx, -18), (wx + 12 * math.cos(wheel), -18 + 12 * math.sin(wheel))], (160, 160, 170), 2)
        c.rect(cx + 100, -50, cx + 130, -40, black, ol=None)
    # loco
    c.rect(-150, -150, -60, -26, red, r=6)
    c.rect(-160, -164, -50, -148, black, r=4)
    c.rect(-136, -130, -98, -96, win, w=2, r=4)
    c.ellipse(-60, -78, 6, 40, red)
    c.rect(-62, -118, 40, -40, blue, r=24)
    c.ellipse(40, -79, 14, 39, mix(blue, (255, 255, 255), 0.2))
    c.circle(44, -79, 8, (255, 230, 120) if night else (230, 230, 200), w=2)
    for k in (-30, 0, 24):
        c.rect(k - 3, -118, k + 3, -40, (240, 200, 80), ol=None)
    c.rect(-6, -158, 16, -116, black)
    c.rect(-12, -166, 22, -156, black, r=3)
    c.ellipse(-30, -124, 14, 10, (240, 200, 80))
    c.poly([(40, -20), (72, -6), (40, -6)], (230, 60, 60))
    c.rect(-150, -36, 52, -24, black, ol=None)
    for wx, r in ((-120, 22), (-60, 22), (2, 16), (34, 16)):
        c.circle(wx, -22, r, black)
        c.circle(wx, -22, r * 0.45, red, ol=None)
        c.line([(wx, -22), (wx + r * 0.8 * math.cos(wheel * 30 / r), -22 + r * 0.8 * math.sin(wheel * 30 / r))],
               (200, 200, 210), 2)
    c.line([(-120 + 16 * math.cos(wheel), -22 + 16 * math.sin(wheel)), (-60 + 16 * math.cos(wheel),
                                                                          -22 + 16 * math.sin(wheel))],
           (190, 190, 200), 4)
    if steam:
        for k in range(6):
            u = (t * 0.9 + k / 6) % 1.0
            px = 5 - 260 * u
            py = -170 - 90 * u + 8 * math.sin(u * 9)
            r = 10 + 34 * u
            col = mix((255, 255, 255), (200, 210, 225), u) if not night else mix((150, 150, 175), (70, 70, 110), u)
            c.circle(px, py, r, col, ol=None)
    c.pop()


def boat(c, x, y, s=1.0, t=0.0, flag=True):
    """Bateau-mouche: long hull, glass cabin, French flag at the stern. (x, y) = waterline centre."""
    c.push(x, y + 3 * math.sin(t * 1.6), s)
    c.poly([(-300, -40), (290, -40), (330, -70), (316, -40), (290, 0), (-280, 0), (-310, -40)],
           (40, 60, 110), w=3)
    c.rect(-306, -50, 300, -38, (245, 245, 250), w=2.5)
    c.line([(-280, -18), (290, -18)], (230, 200, 90), 3, cap=False)
    # cabin
    c.rect(-230, -100, 180, -50, (190, 225, 240), w=2.5, r=6)
    for k in range(9):
        xx = -230 + 410 * k / 9
        c.line([(xx, -100), (xx, -50)], (90, 110, 140), 2, cap=False)
    c.rect(-240, -110, 190, -98, (245, 245, 250), w=2.5, r=4)
    # deck rail at the front
    c.line([(190, -78), (300, -78)], (60, 60, 70), 2, cap=False)
    for k in range(6):
        c.line([(190 + k * 22, -78), (190 + k * 22, -50)], (60, 60, 70), 2, cap=False)
    if flag:
        c.line([(-290, -50), (-290, -130)], OUT, 3)
        wv = math.sin(t * 5)
        for i, col in enumerate(((40, 70, 170), (250, 250, 250), (220, 50, 60))):
            x0 = -290 - i * 16
            c.poly([(x0, -128 + wv * i), (x0 - 16, -128 + wv * (i + 1)), (x0 - 16, -102 + wv * (i + 1)),
                    (x0, -102 + wv * i)], col, w=1.5)
    c.pop()


# ------------------------------------------------------------ characters

def bulldog(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, mouth=0.0, eyes="open", brow=0.0, arm=0.0,
            hold=None, seed=0.5):
    """Monsieur Gaston: a round bulldog baker on two legs, white hat and apron.
    brow: 0 friendly .. 1 cross. arm: 0 down .. 1 raised (waving what he holds)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    fur, dark, apron = (205, 160, 120), (160, 115, 85), (252, 252, 248)
    c.push(x, y, s, flip=face < 0)
    # legs
    for k, ph in ((-18, 0), (18, math.pi)):
        lift = max(0.0, math.sin(walk + ph)) * 10 if walk else 0
        sw = math.cos(walk + ph) * 8 if walk else 0
        c.stroke([(k, -50), (k + sw, -8 - lift)], dark, 16)
        c.ellipse(k + sw + 6, -6 - lift, 13, 7, dark)
    # back arm
    c.stroke([(-34, -118), (-48, -80)], fur, 15)
    c.ellipse(-48, -76, 9, 9, fur)
    # body + apron
    c.ellipse(0, -100, 52, 62, fur)
    c.poly([(-36, -130), (36, -130), (42, -50), (-42, -50)], apron, w=2.5)
    c.rect(-46, -104, 46, -96, apron, w=2)
    c.rect(-14, -96, 14, -76, mix(apron, (230, 225, 220), 0.5), w=1.5)
    # head
    hx, hy = 14, -176
    for side in (-1, 1):
        c.poly([(hx + side * 28, hy - 26), (hx + side * 50, hy - 18), (hx + side * 38, hy + 2)], dark)
    c.ellipse(hx, hy, 44, 38, fur)
    # chef hat
    c.rect(hx - 28, hy - 52, hx + 28, hy - 30, apron, w=2.5)
    for dx, r in ((-20, 18), (0, 24), (20, 18)):
        c.circle(hx + dx, hy - 62, r, apron)
    c.rect(hx - 26, hy - 54, hx + 26, hy - 32, apron, ol=None)
    # jowls & muzzle
    c.ellipse(hx + 14, hy + 16, 30, 18, mix(fur, (255, 240, 220), 0.5))
    c.ellipse(hx + 16, hy + 2, 11, 8, (60, 45, 45))
    for ex in (hx - 6, hx + 20):
        if eyes == "closed":
            c.arc(ex, hy - 12, 6, 4, 20, 160, OUT, 3)
        else:
            c.circle(ex, hy - 12, 6.5, (255, 255, 255), w=2)
            c.circle(ex + 1.5, hy - 12, 3.5, (30, 25, 25), ol=None)
        tilt = 6 * brow
        c.line([(ex - 9, hy - 24 - (tilt if ex < hx else -tilt) * 0.5),
                (ex + 9, hy - 24 + (tilt if ex < hx else -tilt) * 0.5)], (90, 60, 50), 4)
    if mouth > 0.05:
        c.ellipse(hx + 16, hy + 22, 13, 3 + 9 * mouth, D.MOUTH, w=2)
        c.ellipse(hx + 16, hy + 24 + 5 * mouth, 7, 3, D.TONGUE, ol=None)
    else:
        c.arc(hx + 16, hy + 24, 12, 5, 200 if brow > 0.5 else 20, 340 if brow > 0.5 else 160, OUT, 2.5)
    # lower teeth (bulldog underbite)
    c.poly([(hx + 6, hy + 22), (hx + 9, hy + 14), (hx + 12, hy + 22)], (255, 255, 255), w=1.2)
    c.poly([(hx + 22, hy + 22), (hx + 25, hy + 14), (hx + 28, hy + 22)], (255, 255, 255), w=1.2)
    # front arm (raised to wave)
    ang = math.radians(lerp_(80, -60, arm) + 10 * math.sin(t * 14) * arm)
    sx, sy = 34, -118
    hxx, hyy = sx + 42 * math.cos(ang), sy + 42 * math.sin(ang)
    c.stroke([(sx, sy), (hxx, hyy)], fur, 15)
    if hold in ("baguette", "pin"):
        baguette(c, hxx + 40 * math.cos(ang), hyy + 40 * math.sin(ang), 1.0, ang)
    c.ellipse(hxx, hyy, 10, 10, fur)
    c.pop()


def lerp_(a, b, t):
    return a + (b - a) * t


def pigeon(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, eyes="open", brush=0.0, wing=0.0, seed=0.7):
    """Pierre, a plump grey painter pigeon with a beret and a brush."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    grey, dgrey = (165, 170, 185), (120, 125, 140)
    c.push(x, y, s, flip=face < 0)
    bob = abs(math.sin(walk)) * 4 if walk else 0
    for k, ph in ((-6, 0), (8, math.pi)):
        lift = max(0.0, math.sin(walk + ph)) * 6 if walk else 0
        c.line([(k, -14), (k, -2 - lift)], (230, 110, 110), 3)
        c.line([(k - 5, -lift), (k + 7, -lift)], (230, 110, 110), 3)
    # tail
    c.poly([(-30, -40 - bob), (-62, -30 - bob), (-58, -18 - bob), (-26, -26 - bob)], dgrey)
    c.ellipse(0, -36 - bob, 34, 24, grey)
    # wing (raises when he gestures)
    wa = wing * 0.9
    c.push(-4, -40 - bob)
    pts = [(0, 0), (-34 * math.cos(wa), -34 * math.sin(wa) - 2), (-30 * math.cos(wa) + 8, -30 * math.sin(wa) + 12),
           (8, 10)]
    c.poly(pts, dgrey)
    c.line([(-10, 2), (-24 * math.cos(wa), -24 * math.sin(wa) + 4)], mix(dgrey, (0, 0, 0), 0.2), 2)
    c.pop()
    # iridescent neck + head
    c.ellipse(18, -58 - bob, 14, 16, (110, 160, 140))
    c.ellipse(20, -56 - bob, 10, 8, (150, 110, 170), ol=None)
    hx, hy = 24, -78 - bob
    c.circle(hx, hy, 15, grey)
    c.poly([(hx + 12, hy - 2), (hx + 28, hy + 3 + 2 * mouth), (hx + 12, hy + 6)], (240, 190, 80), w=2)
    if mouth > 0.1:
        c.poly([(hx + 12, hy + 5), (hx + 24, hy + 8 + 6 * mouth), (hx + 12, hy + 8)], (220, 150, 60), w=1.5)
    if eyes == "closed":
        c.arc(hx + 4, hy - 4, 4, 3, 20, 160, OUT, 2)
    else:
        c.circle(hx + 4, hy - 4, 4.5, (255, 140, 60), w=1.5)
        c.circle(hx + 5, hy - 4, 2, (20, 20, 20), ol=None)
    # beret
    c.ellipse(hx - 4, hy - 14, 17, 7, (60, 60, 90))
    c.line([(hx - 4, hy - 21), (hx - 2, hy - 26)], OUT, 2.5)
    # brush in the foot-ish wing tip, waving a bit
    if brush > 0:
        ang = -0.9 + 0.4 * math.sin(t * 6) * brush
        bx, by = 26, -36 - bob
        ex, ey = bx + 34 * math.cos(ang), by + 34 * math.sin(ang)
        c.line([(bx, by), (ex, ey)], (150, 100, 60), 3)
        c.circle(ex, ey, 4, (230, 70, 90), w=1.5)
        c.ellipse(bx, by, 8, 6, dgrey)
    c.pop()


def easel(c, x, y, s=1.0, painting=None, progress=1.0):
    """Wooden easel with a little canvas. painting(c, w, h) draws inside."""
    c.push(x, y, s)
    wood = (150, 105, 65)
    c.stroke([(-40, 0), (-8, -190)], wood, 6)
    c.stroke([(40, 0), (8, -190)], wood, 6)
    c.stroke([(0, 10), (0, -170)], mix(wood, (0, 0, 0), 0.2), 5)
    c.rect(-52, -88, 52, -80, wood, w=2)
    c.rect(-50, -176, 50, -90, (250, 248, 240), w=2.5)
    if painting:
        painting(c, progress)
    c.pop()
