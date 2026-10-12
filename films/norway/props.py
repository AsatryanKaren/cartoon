"""Norway props and new characters for "Whiskers and the Dancing Lights".

Flat outlined style with draw.Canvas primitives. Characters are in local
space: origin between the feet, facing right. A few mountain helpers
(snowfall, pines, peaks, subtitle shading) are imported read-only from the
Mont Blanc film.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix
from films.montblanc.props import (snowfall, shade_bottom, overlay, pine, snow_mound, peak,  # noqa: F401
                                   SNOW, SNOW_SH, SNOW_DEEP)

WOOD = (204, 160, 104)
WOOD_D = (162, 118, 72)
FJORD = (34, 78, 140)
FJORD_D = (24, 56, 110)
CLIFF = (96, 104, 124)
CLIFF_D = (72, 78, 98)
MOSS = (92, 140, 84)


# ================================================================ aurora

def aurora_rgb(t, w, h, ribbons, strength=1.0, grid=4):
    """Northern lights as a small RGB float array (h//grid, w//grid, 3), values 0..255.

    ribbons: [(base_y, amp, freq, speed, height, x0, x1)] in fractions of the region.
    Each ribbon is a curtain: bright green at its lower edge, fading up into purple,
    with drifting vertical rays.
    """
    lw, lh = max(2, w // grid), max(2, h // grid)
    X = np.linspace(0, 1, lw)[None, :]
    Y = np.linspace(0, 1, lh)[:, None]
    out = np.zeros((lh, lw, 3), np.float32)
    green = np.array([70, 255, 150], np.float32)
    teal = np.array([60, 220, 200], np.float32)
    purple = np.array([200, 90, 255], np.float32)
    for k, (yb, amp, fq, sp, hgt, x0, x1) in enumerate(ribbons):
        base = (yb + amp * np.sin(math.tau * (fq * X + sp * t * 0.05) + k * 1.7)
                + amp * 0.45 * np.sin(math.tau * (fq * 2.3 * X - sp * t * 0.07) + k))
        d = base - Y                                  # > 0 above the lower edge
        body = np.where(d > 0, np.exp(-np.maximum(d, 0) / hgt), np.exp(np.minimum(d, 0) / 0.015))
        rays = 0.55 + 0.45 * np.sin(math.tau * (38 * X + 1.5 * np.sin(math.tau * (2.2 * X + 0.04 * t + k)))
                                    + t * (0.6 + 0.2 * k))
        rays = rays * (0.75 + 0.25 * np.sin(math.tau * (9 * X - 0.05 * t * (k + 1))))
        u = np.clip((X - x0) / max(1e-3, x1 - x0), 0, 1)
        env = np.sin(math.pi * u) ** 1.2 * (0.65 + 0.35 * np.sin(math.tau * (1.3 * X - 0.03 * t) + k * 2))
        inten = body * rays * env * strength
        m = np.clip(d / (hgt * 1.6), 0, 1)[..., None]
        col = np.where(m < 0.5, green * (1 - m * 2) + teal * (m * 2), teal * (2 - m * 2) + purple * (m * 2 - 1))
        out += inten[..., None] * col
    return np.clip(out, 0, 255)


def apply_aurora(img, t, ribbons, strength, region, mirror=None, mirror_k=0.45):
    """Screen-blend the aurora over img (supersampled) inside region=(x0, y0, x1, y1) (output px).

    mirror: (y_line, y_bottom) -- also reflect it, dimmed, onto water between those rows.
    """
    if strength <= 0.01:
        return img
    x0, y0, x1, y1 = region
    w, h = x1 - x0, y1 - y0
    arr = aurora_rgb(t, w, h, ribbons, strength)
    small = Image.fromarray(arr.astype(np.uint8), "RGB")
    layer = small.resize((w * SS, h * SS), Image.BILINEAR)
    box = (x0 * SS, y0 * SS, x1 * SS, y1 * SS)
    img.paste(ImageChops.screen(img.crop(box), layer), box)
    if mirror is not None:
        yl, yb = mirror
        mh = yb - yl
        refl = small.transpose(Image.FLIP_TOP_BOTTOM).resize((w * SS, int(mh * SS * 1.0)), Image.BILINEAR)
        refl = refl.point(lambda v: int(v * mirror_k))
        box2 = (x0 * SS, yl * SS, x1 * SS, yl * SS + refl.size[1])
        img.paste(ImageChops.screen(img.crop(box2), refl), box2)
    return img


# ============================================================ characters

PUFFIN = dict(black=(40, 40, 52), white=(250, 250, 246), face=(236, 236, 230), beak1=(110, 120, 140),
              beak2=(250, 200, 70), beak3=(236, 92, 50), feet=(250, 128, 50))


def puffin(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, hop=0.0, fly=0.0, eyes="open", seed=5.0,
           wing=None):
    """Tuva the puffin. fly: 0..1 wings spread and flapping."""
    p = PUFFIN
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y - hop, s, flip=face < 0)
    waddle = math.sin(walk) * 0.08 if walk else 0.0
    # feet
    for fx, ph in ((-8, 0), (8, math.pi)):
        lift = -max(0.0, math.cos(walk + ph)) * 5 if walk else 0
        if fly > 0.5:
            c.poly([(fx - 4, -10), (fx + 8, -6), (fx - 4, -2)], p["feet"], w=2)
        else:
            c.poly([(fx - 6, lift), (fx + 12, lift), (fx + 2, lift - 10)], p["feet"], w=2)
    c.push(0, -10, 1.0)
    ox, oy, sx, sy = c.tf[-1]
    c.tf[-1] = (ox + waddle * 30 * sx, oy, sx, sy)
    # far wing (when flying)
    flap = math.sin(t * 22) if fly > 0 else 0.0
    if fly > 0:
        ang = -0.6 + 0.9 * flap
        tip = (-6 + 52 * math.cos(ang) * fly - 20, -40 - 52 * math.sin(ang) * fly)
        c.poly([(-6, -44), tip, (8, -30)], mix(p["black"], (0, 0, 0), 0.2), w=2)
    # body
    c.ellipse(0, -30, 22, 32, p["black"], w=2.5)
    c.ellipse(7, -26, 14, 24, p["white"], ol=None)
    # wing
    if fly > 0:
        ang = -0.4 + 1.0 * flap
        tip = (-4 + 56 * math.cos(ang) * fly - 22, -36 - 56 * math.sin(ang) * fly)
        c.poly([(-10, -40), tip, (4, -24)], p["black"], w=2.5)
    else:
        wv = wing if wing is not None else 0.0
        c.push(-6, -40)
        c.poly([(0, 0), (-10 - 10 * wv, 26 - 22 * wv), (6, 24)], p["black"], w=2.5)
        c.pop()
    # head
    hx, hy = 6, -68
    c.circle(hx, hy, 19, p["black"], w=2.5)
    c.ellipse(hx + 6, hy + 1, 13, 13, p["face"], ol=None)
    if eyes == "closed":
        c.arc(hx + 8, hy - 3, 4, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(hx + 8, hy, 4, 4, 200, 340, OUT, 2)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.circle(hx + 8, hy - 3, 4.6 * big, (236, 90, 60), w=1.5)
        c.circle(hx + 8.5, hy - 3, 2.8 * big, (20, 20, 25), ol=None)
        c.circle(hx + 9.5, hy - 4.5, 1, (255, 255, 255), ol=None)
        c.line([(hx + 12, hy - 6), (hx + 16, hy - 9)], (90, 90, 110), 1.5, cap=False)
    # beak: tall striped triangle; the lower half drops open
    bx = hx + 15
    jaw = 8 * mouth
    def half(top, bot, tipy, dy):
        pts = [(bx, top + dy), (bx + 22, tipy + dy), (bx, bot + dy)]
        c.poly(pts, p["beak3"], w=2)
        f = lambda u: ((bx + 22 * u, lerp(top, tipy, u) + dy), (bx + 22 * u, lerp(bot, tipy, u) + dy))
        a0, a1 = f(0.22)
        b0, b1 = f(0.4)
        c.poly([a0, b0, b1, a1], p["beak2"], ol=None)
        c.poly([(bx + 1, top + dy + 1), a0, a1, (bx + 1, bot + dy - 1)], p["beak1"], ol=None)
        c.line([(bx + 9, lerp(top, tipy, 0.5) + dy + 2), (bx + 9, lerp(bot, tipy, 0.5) + dy - 2)], p["beak3"], 1.5,
               cap=False)
    if jaw > 0.5:
        c.poly([(bx, hy), (bx + 20, hy + 2), (bx, hy + 4 + jaw)], D.MOUTH, ol=None)
    half(hy + 1, hy + 15, hy + 1 - jaw * 0.6, jaw)
    half(hy - 15, hy + 1, hy + 1, 0)
    c.pop()
    c.pop()


MOOSE = dict(body=(128, 86, 56), dark=(96, 62, 40), muzzle=(156, 110, 76), antler=(228, 204, 156),
             antler_d=(196, 170, 120), hoof=(60, 44, 36))


def _antler(c, x, y, col, shade, spread=1.0):
    """A palmate moose antler, base at (x, y), opening up and to the back."""
    c.push(x, y, 1.0)
    pts = [(0, 0), (-18, -10), (-48 * spread, -18), (-66 * spread, -34), (-70 * spread, -52), (-58 * spread, -50),
           (-56 * spread, -66), (-44 * spread, -58), (-36 * spread, -76), (-26 * spread, -60), (-14 * spread, -74),
           (-8 * spread, -54), (4, -64), (6, -40), (16, -46), (12, -20), (8, -6)]
    c.poly(pts, col, w=2.5)
    c.poly([(0, 0), (-18, -10), (-44 * spread, -20), (-30 * spread, -24), (-10, -14)], shade, ol=None)
    c.pop()


def moose(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, eyes="open", lie=0.0, head_up=0.0,
          seed=7.0, shadow=None, eyeglow=False):
    """Magnus the moose. lie: 0 standing .. 1 lying down. shadow: colour to draw as a flat silhouette."""
    m = MOOSE
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    col = (lambda k: shadow) if shadow else (lambda k: m[k])
    ol = mix(shadow, (0, 0, 0), 0.3) if shadow else OUT
    c.push(x, y, s, flip=face < 0)
    lie = clamp(lie)
    leg_len = 170 * (1 - lie) + 30 * lie
    by = -leg_len - 40
    # legs
    def leg(lx, phase, k):
        if lie > 0.5:
            c.ellipse(lx + 10, -14, 34, 13, col(k), ol=ol, w=2.5)
            return
        sw = math.sin(walk + phase) if walk else 0.0
        knee = (lx + sw * 10, by + leg_len * 0.55)
        foot = (lx + sw * 22, -max(0.0, math.cos(walk + phase)) * 10 if walk else 0)
        c.stroke([(lx, by + 10), knee, foot], col(k), 16, ol=ol)
        c.ellipse(foot[0] + 2, foot[1] - 4, 11, 7, col("hoof") if not shadow else shadow, ol=ol, w=2)
    leg(-70, math.pi, "dark")
    leg(68, 0, "dark")
    # tail stub
    c.ellipse(-112, by - 20, 12, 16, col("dark"), ol=ol, w=2.5)
    # body + hump
    c.ellipse(0, by, 116, 62, col("body"), ol=ol, w=3)
    c.ellipse(52, by - 46, 66, 38, col("body"), ol=None)
    c.arc(52, by - 46, 66, 38, 190, 320, ol, 3)
    if not shadow:
        c.ellipse(10, by + 30, 80, 20, mix(m["body"], (255, 230, 200), 0.12), ol=None)
    leg(-46, 0, "body")
    leg(90, math.pi, "body")
    # neck + head
    hdy = -18 * head_up
    hx, hy = 150, by - 52 + hdy
    c.poly([(70, by - 70), (120, hy - 30), (150, hy + 10), (96, by + 10)], col("body"), ol=None)
    c.line([(70, by - 74), (122, hy - 30)], ol, 3)
    c.push(hx, hy, 1.22)
    hx, hy = 0, 0
    # antlers (back one first)
    if not shadow:
        _antler(c, hx - 18, hy - 30, m["antler_d"], mix(m["antler_d"], (0, 0, 0), 0.15), 0.85)
    else:
        _antler(c, hx - 18, hy - 30, shadow, shadow, 0.85)
    # ears
    c.poly([(hx - 22, hy - 22), (hx - 52, hy - 34), (hx - 30, hy - 10)], col("dark"), ol=ol, w=2.5)
    # head: long face with a bulbous nose
    c.ellipse(hx, hy - 4, 34, 30, col("body"), ol=ol, w=3)
    c.poly([(hx + 10, hy - 26), (hx + 62, hy - 6), (hx + 66, hy + 22), (hx + 10, hy + 26)], col("body"), ol=None)
    c.line([(hx + 10, hy - 26), (hx + 62, hy - 8)], ol, 3)
    c.ellipse(hx + 58, hy + 10, 26, 22, col("muzzle"), ol=ol, w=3)
    c.ellipse(hx + 30, hy + 18, 30, 16, col("muzzle"), ol=None)
    jaw = 12 * mouth
    if jaw > 1 and not shadow:
        c.ellipse(hx + 52, hy + 30 + jaw * 0.4, 18, 4 + jaw * 0.6, D.MOUTH, w=2)
    c.line([(hx + 34, hy + 30 + jaw * 0.3), (hx + 72, hy + 26 + jaw * 0.6)], ol, 2.5)
    # dewlap ("bell")
    c.poly([(hx + 4, hy + 28), (hx + 14, hy + 60), (hx + 24, hy + 30)], col("dark"), ol=ol, w=2)
    if not shadow:
        c.ellipse(hx + 68, hy + 4, 4, 6, (60, 36, 30), ol=None)        # nostril
    # eye
    ex, ey = hx + 8, hy - 10
    if eyeglow:
        c.circle(ex, ey, 6, (255, 236, 120), ol=None)
        c.circle(ex + 22, ey + 2, 5, (255, 236, 120), ol=None)
    elif not shadow:
        if eyes == "closed":
            c.arc(ex, ey, 7, 5, 20, 160, OUT, 3)
        elif eyes == "happy":
            c.arc(ex, ey + 3, 7, 7, 200, 340, OUT, 3)
        else:
            c.ellipse(ex, ey, 7, 8.5, (255, 255, 255), w=2.5)
            c.ellipse(ex + 2, ey + 1, 4, 5.5, (60, 40, 30), ol=None)
            c.circle(ex + 3, ey - 2, 1.6, (255, 255, 255), ol=None)
            c.arc(ex, ey - 6, 9, 6, 200, 330, OUT, 2)      # kind heavy brow
    # front antler
    if not shadow:
        _antler(c, hx - 6, hy - 30, m["antler"], m["antler_d"], 1.0)
    else:
        _antler(c, hx - 6, hy - 30, shadow, shadow, 1.0)
    c.pop()
    c.pop()


def moose_back(s=1.0, lie=0.0):
    """(x, y) of the top of the moose's back (for riders), local to its feet, unscaled facing right."""
    leg_len = 170 * (1 - lie) + 30 * lie
    return (-10 * s, (-leg_len - 40 - 58) * s)


def reindeer(c, x, y, s=1.0, face=1, walk=0.0, col=(30, 36, 70)):
    """Flat silhouette reindeer for far ridges."""
    c.push(x, y, s, flip=face < 0)
    for lx, ph in ((-24, 0), (-16, math.pi), (18, math.pi), (26, 0)):
        sw = math.sin(walk + ph) * 6
        c.line([(lx, -36), (lx + sw, 0)], col, 4, cap=False)
    c.ellipse(0, -44, 34, 14, col, ol=None)
    c.poly([(24, -50), (38, -72), (48, -70), (36, -46)], col, ol=None)
    c.ellipse(46, -70, 10, 6, col, ol=None)
    for side in (0, 6):
        base = (36 + side, -78)
        c.line([base, (30 + side, -96), (22 + side, -108)], col, 2.5, cap=False)
        c.line([(32 + side, -92), (40 + side, -102)], col, 2, cap=False)
        c.line([(27 + side, -102), (30 + side, -112)], col, 2, cap=False)
    c.pop()


# ================================================================ things

def flag(c, x, y, s=1.0, t=0.0, pole=90):
    """A Norwegian flag on a little pole, waving."""
    c.push(x, y, s)
    c.line([(0, 0), (0, -pole)], (240, 240, 240), 4)
    c.circle(0, -pole - 3, 4, (250, 210, 70), w=1.5)
    fw, fh = 58, 40
    def P(u, v):
        return (2 + u * fw, -pole + v * fh + 4 * math.sin(t * 4 + u * 4) * u)
    def quad(u0, v0, u1, v1, col):
        c.poly([P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)], col, ol=None)
    quad(0, 0, 1, 1, (200, 30, 46))
    quad(0.27, 0, 0.45, 1, (255, 255, 255))
    quad(0, 0.38, 1, 0.62, (255, 255, 255))
    quad(0.32, 0, 0.40, 1, (0, 40, 104))
    quad(0, 0.44, 1, 0.56, (0, 40, 104))
    c.line([P(u, 0) for u in np.linspace(0, 1, 6)] + [P(1, 1)] + [P(u, 1) for u in np.linspace(1, 0, 6)],
           OUT, 2, cap=False)
    c.pop()


def crate(c, x, y, s=1.0, lid=0.0, label="NORGE", lid_side=1):
    """Wooden fish crate (bottom centre at x, y), 120 x 80. lid: 0 shut .. 1 flipped open."""
    c.push(x, y, s)
    c.rect(-60, -80, 60, 0, WOOD, w=2.5, r=3)
    for yy in (-54, -27):
        c.line([(-58, yy), (58, yy)], WOOD_D, 2, cap=False)
    c.rect(-60, -80, -48, 0, WOOD_D, w=2)
    c.rect(48, -80, 60, 0, WOOD_D, w=2)
    c.text(0, -40, label, 18, (60, 80, 140))
    # little fish stencil
    c.ellipse(-22, -18, 10, 5, (60, 80, 140), ol=None)
    c.poly([(-12, -18), (-4, -24), (-4, -12)], (60, 80, 140), ol=None)
    # lid hinged at the far edge
    if lid is None:
        pass
    elif lid < 0.02:
        c.rect(-64, -88, 64, -78, WOOD_D, w=2.5, r=2)
    else:
        a = math.pi * 0.62 * ease(lid)
        hx = -64 * lid_side
        ex = hx + lid_side * 128 * math.cos(a)
        ey = -84 - 128 * math.sin(a)
        c.line([(hx, -84), (ex, ey)], OUT, 12, cap=False)
        c.line([(hx, -84), (ex, ey)], WOOD_D, 8, cap=False)
    c.pop()


def crate_inside(c, x, y, s=1.0):
    """Dark inside of an open crate (draw before whatever pops out, then crate_front)."""
    c.push(x, y, s)
    c.rect(-58, -86, 58, -70, (90, 64, 40), ol=None)
    c.pop()


def fish(c, x, y, s=1.0, ang=0.0, col=(170, 186, 200)):
    c.push(x, y, s)
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)
    c.poly([R(-22, 0), R(-34, -10), R(-32, 0), R(-34, 10)], mix(col, (0, 0, 0), 0.15), w=2)
    pts = [R(22 * math.cos(a), 9 * math.sin(a)) for a in np.linspace(0, math.tau, 16)]
    c.poly(pts, col, w=2)
    ex, ey = R(12, -2)
    c.circle(ex, ey, 2, OUT, ol=None)
    c.pop()


def fish_van(c, x, y, s=1.0, t=0.0, door=0.0, wheel=0.0, crates=True, inside=None):
    """Small blue delivery van facing right, bottom of the wheels at y. door: 0 shut .. 1 slid open.

    inside(c): draws the cargo seen through the open side door (crate stack etc).
    """
    c.push(x, y, s)
    body = (78, 140, 196)
    dark = (52, 104, 160)
    c.ellipse(0, 4, 230, 10, mix(body, (40, 40, 50), 0.6), ol=None)
    # body
    c.poly([(-210, -40), (-210, -226), (90, -226), (120, -220), (176, -150), (206, -138), (210, -40)], body, w=3)
    c.rect(-210, -70, 210, -40, dark, w=3)
    # cab window
    c.poly([(98, -210), (124, -208), (168, -150), (98, -150)], (190, 226, 250), w=2.5)
    c.line([(110, -204), (128, -170)], (255, 255, 255), 3)
    c.rect(186, -120, 208, -104, (255, 236, 150), w=2)      # headlight
    # cargo opening
    ox0, ox1, oy0, oy1 = -190, 40, -212, -76
    c.rect(ox0, oy0, ox1, oy1, (40, 46, 62), w=2.5)
    if inside is not None:
        inside(c)
    # sliding door
    dx = (ox1 - ox0) * clamp(door) * 0.98
    if door < 0.99:
        a = ox0 + dx
        b = ox1 + dx
        c.rect(a, oy0, min(b, 92), oy1, body, w=2.5)
        if b < 92:
            c.text((a + b) / 2, -160, "FRESH FISH", 22, (255, 255, 255), stroke=2, stroke_fill=dark)
            c.push((a + b) / 2, -114, 1.2)
            fish(c, 0, 0, 1.2, 0, (255, 255, 255))
            c.pop()
        c.rect(a + 10, -144, a + 30, -136, (40, 46, 62), ol=None, r=3)
    else:
        c.rect(42, oy0, 92, oy1, body, w=2.5)
    c.line([(ox0, oy0 - 4), (96, oy0 - 4)], dark, 4, cap=False)
    # roof sign
    c.rect(-150, -252, 40, -226, (250, 250, 246), w=2.5, r=4)
    c.text(-55, -239, "FROM NORWAY", 16, (200, 40, 50))
    # wheels
    for wx in (-130, 130):
        c.circle(wx, -30, 32, (44, 44, 52), w=3)
        c.circle(wx, -30, 15, (190, 190, 200), w=2)
        for k in range(3):
            a = wheel + k * math.tau / 3
            c.line([(wx, -30), (wx + 12 * math.cos(a), -30 + 12 * math.sin(a))], (110, 110, 120), 3, cap=False)
    c.pop()


def cargo_plane(c, x, y, s=1.0, t=0.0, tilt=0.0):
    """Big propeller cargo plane facing right; (x, y) is the fuselage centre."""
    c.push(x, y, s)
    ca, sa = math.cos(tilt), math.sin(tilt)
    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)
    def poly(pts, col, **kw):
        c.poly([R(px, py) for px, py in pts], col, **kw)
    body, dark = (236, 238, 244), (196, 202, 214)
    stripe = (60, 110, 190)
    # tail
    poly([(-300, -20), (-360, -150), (-318, -150), (-240, -30)], body, w=3)
    poly([(-350, -130), (-318, -150), (-300, -120)], (200, 40, 50), ol=None)
    poly([(-330, -10), (-400, -20), (-396, 4), (-300, 10)], dark, w=2.5)
    # far wing
    poly([(-20, -40), (60, -40), (40, -54), (-40, -54)], dark, w=2)
    # fuselage
    pts = [(-340, -18)] + [(-240 + 480 * u, -46 - 6 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 8)] + \
          [(280, -40), (330, -16), (342, 4), (320, 30), (240, 44), (-200, 44), (-300, 20), (-350, 0)]
    poly(pts, body, w=3)
    poly([(-330, 4), (330, 4), (326, 14), (-320, 14)], stripe, ol=None)
    poly([(286, -36), (318, -16), (290, -12)], (60, 80, 110), w=2)          # cockpit
    for k in range(9):
        px, py = R(-200 + k * 52, -18)
        c.circle(px, py, 6, (150, 190, 230), w=1.5)
    cx_, cy_ = R(-20, 28)
    c.text(cx_, cy_, "CARGO", 18, stripe)
    # high wing + engines
    poly([(-60, -50), (90, -50), (110, -60), (-80, -62)], dark, w=2.5)
    for ex in (-10, 60):
        poly([(ex - 30, -62), (ex + 30, -62), (ex + 36, -48), (ex - 26, -46)], (210, 214, 226), w=2.5)
        px, py = R(ex + 40, -56)
        blur = 0.5 + 0.5 * math.sin(t * 40 + ex)
        c.ellipse(px, py, 4, 26 + 4 * blur, (200, 210, 225), w=1.5)
        c.circle(px, py, 4, (70, 70, 80), ol=None)
    c.pop()


def bryggen_house(c, x, y, w, h, col, seed=0, trim=(250, 248, 240)):
    """A tall narrow wooden Bergen harbour house: gable end facing us, bottom-left at x, y."""
    rng = np.random.default_rng(seed)
    gh = w * 0.95
    dark = mix(col, (0, 0, 0), 0.22)
    c.poly([(x, y), (x, y - h), (x + w / 2, y - h - gh), (x + w, y - h), (x + w, y)], col, w=2.5)
    for k in range(1, int(w // 9)):
        xx = x + k * 9
        top = y - h - gh * (1 - abs((xx - x) / w * 2 - 1))
        c.line([(xx, y - 2), (xx, top + 6)], dark, 1.5, cap=False)
    # roof edge boards
    c.line([(x - 4, y - h + 4), (x + w / 2, y - h - gh - 4), (x + w + 4, y - h + 4)], trim, 5)
    c.line([(x - 4, y - h + 4), (x + w / 2, y - h - gh - 4), (x + w + 4, y - h + 4)], OUT, 1.5, cap=False)
    # hoist beam in the gable + loft door
    c.rect(x + w / 2 - 9, y - h - gh * 0.5, x + w / 2 + 9, y - h - gh * 0.22, dark, w=2)
    c.line([(x + w / 2, y - h - gh * 0.62), (x + w / 2 + 22, y - h - gh * 0.62)], OUT, 4, cap=False)
    # windows
    rows = max(2, int(h // 70))
    cols = 2 if w < 130 else 3
    for r in range(rows):
        wy = y - h + 26 + r * (h - 90) / max(1, rows - 1) if rows > 1 else y - h + 30
        for k in range(cols):
            wx = x + w * (k + 0.5) / cols
            c.rect(wx - 11, wy - 15, wx + 11, wy + 15, (60, 74, 96), ol=OUT, w=2)
            c.rect(wx - 11, wy - 15, wx + 11, wy + 15, None, ol=trim, w=3)
            c.line([(wx, wy - 14), (wx, wy + 14)], trim, 2, cap=False)
            c.line([(wx - 10, wy), (wx + 10, wy)], trim, 2, cap=False)
    # door at street level
    c.rect(x + w / 2 - 14, y - 40, x + w / 2 + 14, y, mix(dark, (60, 40, 30), 0.4), w=2, r=3)


def waffle(c, x, y, s=1.0, bite=0.0, cheese=False, steam=0.0, t=0.0):
    """Norwegian heart waffle: a scalloped golden disc split into five hearts (seen at an angle)."""
    c.push(x, y, s)
    gold, dark = (236, 178, 88), (196, 128, 56)
    gone = int(round(clamp(bite) * 5))
    keep = [k for k in range(5) if k < 5 - gone]
    ry = 0.62

    def ang(k, f):
        return -math.pi / 2 + (k + f) * math.tau / 5
    for k in keep:                                       # two lobes per heart on the rim
        for f in (0.27, 0.73):
            a = ang(k, f)
            c.ellipse(math.cos(a) * 26, math.sin(a) * 26 * ry, 10, 10 * ry, gold, w=2.5)
    for k in keep:
        a0, a1 = ang(k, 0), ang(k, 1)
        pts = [(0, 0)] + [(math.cos(a) * 28, math.sin(a) * 28 * ry) for a in np.linspace(a0, a1, 6)]
        c.poly(pts, gold, ol=None)
    for k in keep:
        for f in (0, 1):
            a = ang(k, f)
            c.line([(0, 0), (math.cos(a) * 32, math.sin(a) * 32 * ry)], dark, 2, cap=False)
        for rr, f in ((12, 0.5), (22, 0.3), (22, 0.7)):
            a = ang(k, f)
            c.circle(math.cos(a) * rr, math.sin(a) * rr * ry, 1.8, dark, ol=None)
    if cheese and keep:
        for k in range(3):
            c.poly([(-16 + k * 8, -6 + k * 2), (6 + k * 8, -10 + k * 2), (10 + k * 8, -3 + k * 2),
                    (-12 + k * 8, 1 + k * 2)], (214, 150, 86), w=1.5)
    if steam > 0:
        for k in range(3):
            u = (t * 0.6 + k / 3) % 1.0
            pts = [(-14 + 14 * k + 5 * math.sin(t * 3 + v * 6 + k), -12 - 50 * u - 22 * v) for v in np.linspace(0, 1, 6)]
            c.line(pts, mix((255, 255, 255), (230, 230, 230), u), (3.5 * (1 - u) + 1) * steam)
    c.pop()


def brunost(c, x, y, s=1.0):
    """A block of Norwegian brown cheese (bottom centre x, y)."""
    c.push(x, y, s)
    c.poly([(-26, 0), (-26, -30), (-10, -42), (34, -42), (34, -12), (18, 0)], (196, 136, 76), w=2.5)
    c.poly([(-26, -30), (-10, -42), (34, -42), (18, -30)], (226, 168, 104), w=2)
    c.poly([(18, -30), (34, -42), (34, -12), (18, 0)], (168, 112, 60), w=2)
    c.rect(-22, -24, 14, -8, (250, 240, 220), w=1.5, r=2)
    c.pop()


def waffle_stand(c, x, y, s=1.0, t=0.0):
    """A little red waffle hut with a striped awning (bottom centre x, y). Counter top is at y-120."""
    c.push(x, y, s)
    red, dark = (186, 52, 46), (140, 36, 34)
    c.rect(-150, -280, 150, 0, red, w=3)
    for k in range(1, 30):
        xx = -150 + k * 10
        c.line([(xx, -278), (xx, -2)], dark, 1.5, cap=False)
    c.poly([(-170, -280), (0, -350), (170, -280)], (70, 56, 50), w=3)
    c.rect(-128, -250, 128, -130, (60, 46, 42), w=2.5)            # serving hatch
    c.rect(-128, -250, 128, -236, (255, 214, 120), ol=None)
    # awning
    for k in range(8):
        a = -150 + k * 300 / 8
        col = (255, 255, 255) if k % 2 else (200, 40, 50)
        c.poly([(a, -264), (a + 300 / 8, -264), (a + 300 / 8 + 4, -228), (a + 4, -228)], col, w=2)
        c.ellipse(a + 300 / 16 + 4, -228, 300 / 16, 8, col, w=2)
    c.rect(-110, -320, 110, -284, (250, 246, 230), w=2.5, r=6)
    c.text(0, -302, "VAFLER", 26, (186, 52, 46))
    c.rect(-160, -132, 160, -112, (226, 196, 150), w=3, r=3)      # counter
    c.pop()


def waffle_iron(c, x, y, s=1.0, t=0.0, open_=0.6):
    c.push(x, y, s)
    c.ellipse(0, -10, 44, 14, (50, 50, 58), w=2.5)
    c.ellipse(0, -14, 36, 9, (236, 178, 88), ol=None)
    a = math.pi * 0.42 * open_
    tx, ty = -44 + 88 * math.cos(a), -10 - 88 * math.sin(a)
    c.line([(-44, -12), (tx, ty)], OUT, 14)
    c.line([(-44, -12), (tx, ty)], (70, 70, 80), 10)
    c.rect(36, -16, 74, -8, (120, 70, 40), w=2, r=3)
    c.pop()


def longship(c, x, y, s=1.0, t=0.0, oar=0.0, front=None, deck=None):
    """Viking longship facing right with a dragon head; (x, y) is the waterline centre.

    deck(c): draws passengers between the far and near hull sides.
    front: called after the hull for things in front of it.
    """
    c.push(x, y, s)
    wood, dark, light = (150, 94, 56), (112, 66, 40), (186, 128, 78)
    # mast + sail (behind)
    c.rect(-8, -360, 8, -40, (120, 76, 44), w=2.5)
    c.rect(-150, -344, 150, -334, (120, 76, 44), w=2.5, r=4)
    bil = 10 + 4 * math.sin(t * 1.4)
    for k in range(6):
        a, b = -146 + k * 292 / 6, -146 + (k + 1) * 292 / 6
        col = (200, 44, 50) if k % 2 == 0 else (250, 244, 230)
        bot = -124 + bil * math.sin(math.pi * (k + 0.5) / 6)
        c.poly([(a, -334), (b, -334), (b, bot + bil * 0.0), (a, bot)], col, ol=None)
    c.poly([(-146, -334), (146, -334), (146, -124)] + [(146 - 292 * u, -124 + bil * math.sin(math.pi * u))
                                                         for u in np.linspace(0, 1, 9)], None, w=3)
    c.line([(-140, -124), (-30, -40)], (90, 70, 50), 2, cap=False)
    c.line([(150, -124), (40, -40)], (90, 70, 50), 2, cap=False)
    # far gunwale
    c.poly([(-250, -64), (250, -64), (250, -52), (-250, -52)], dark, ol=None)
    if deck is not None:
        deck(c)
    # hull
    hull = [(-300, -120)] + [(-300 + 600 * u, -18 + 50 * (1 - math.sin(math.pi * u) ** 0.5) - 30)
                              for u in np.linspace(0.05, 0.95, 14)] + [(300, -120), (262, -60), (-262, -60)]
    hull = [(-290, -110), (-262, -60), (262, -60), (290, -110), (282, -40), (230, 8), (-230, 8), (-282, -40)]
    c.poly(hull, wood, w=3)
    for k, yy in enumerate((-42, -24, -8)):
        c.line([(-270 + k * 16, yy), (270 - k * 16, yy)], dark, 2.5, cap=False)
    # shields
    for k in range(9):
        sx_ = -210 + k * 52
        col = [(200, 44, 50), (250, 210, 80), (60, 110, 180), (250, 244, 230)][k % 4]
        c.circle(sx_, -62, 20, col, w=2.5)
        c.line([(sx_ - 20, -62), (sx_ + 20, -62)], mix(col, (0, 0, 0), 0.25), 3, cap=False)
        c.circle(sx_, -62, 6, (170, 170, 180), w=2)
    # oars (under the shields)
    for k in range(5):
        ox = -180 + k * 90
        a = math.radians(20 + 14 * math.sin(oar + k * 0.2))
        c.line([(ox, -50), (ox - 140 * math.sin(a) * 0.6, -50 + 140 * math.cos(a))], (130, 84, 50), 5, cap=False)
    # stern spiral
    c.poly([(-282, -40), (-300, -110), (-322, -170), (-300, -200), (-276, -186), (-286, -160), (-268, -110),
            (-262, -60)], wood, w=3)
    c.arc(-298, -182, 14, 14, 0, 300, dark, 3)
    # dragon neck + head
    c.poly([(262, -60), (290, -110), (300, -170), (324, -220), (350, -236), (372, -226), (350, -206), (330, -170),
            (320, -110), (282, -40)], wood, w=3)
    for k in range(5):
        yy = -110 - k * 24
        c.line([(296 + k * 5, yy), (318 + k * 4, yy - 6)], dark, 2.5, cap=False)
    # head
    c.push(352, -236, 1.7)
    c.poly([(-26, 8), (-14, -18), (12, -24), (48, -14), (60, 0), (40, 6), (54, 14), (20, 16), (-10, 22)], light, w=3)
    c.poly([(40, 6), (54, 14), (20, 16)], (120, 40, 40), ol=None)
    for k in range(3):
        c.poly([(24 + k * 9, 6), (28 + k * 9, 12), (32 + k * 9, 6)], (250, 250, 240), w=1)
    c.circle(16, -10, 6, (250, 220, 80), w=2)
    c.circle(17, -10, 2.5, OUT, ol=None)
    for k in range(4):                               # curly mane
        c.arc(-18 + k * 6, -24 - k * 3, 9, 9, 180, 360, dark, 3)
    c.poly([(-12, -18), (-30, -40), (-4, -24)], dark, w=2)
    c.pop()
    if front is not None:
        front(c)
    c.pop()


def troll_rock(c, x, y, s=1.0, t=0.0, col=(118, 120, 132)):
    """A big mossy boulder that looks just like a sleeping troll's head."""
    c.push(x, y, s)
    dark = mix(col, (0, 0, 0), 0.25)
    c.poly([(-120, 0), (-124, -60), (-96, -130), (-40, -164), (30, -166), (90, -132), (122, -70), (126, 0)], col, w=3)
    c.poly([(30, -166), (90, -132), (122, -70), (126, 0), (60, 0), (80, -80)], dark, ol=None)
    # mossy hair
    for k in range(7):
        a = math.pi * (0.15 + 0.7 * k / 6)
        hx, hy = math.cos(a) * -100, -60 - math.sin(a) * 100
        c.ellipse(hx, hy, 26, 14, MOSS, w=2)
    c.poly([(-50, -160), (-30, -196), (-18, -164)], MOSS, w=2)
    # big nose, closed eyes, smile
    c.ellipse(30, -66, 30, 40, mix(col, (255, 255, 255), 0.08), w=3)
    c.arc(-14, -98, 12, 8, 20, 160, OUT, 3)
    c.arc(56, -102, 12, 8, 20, 160, OUT, 3)
    c.arc(24, -30, 40, 14, 20, 160, OUT, 3)
    # snow cap
    c.poly([(-90, -136), (-40, -170), (30, -172), (86, -138), (40, -146), (0, -136), (-40, -146)], SNOW, w=2)
    c.pop()


def stave_church(c, x, y, s=1.0, col=(80, 48, 36), roof=(56, 34, 28)):
    """A tiny dark wooden stave church with stacked roofs and dragon finials."""
    c.push(x, y, s)
    for k, (w2, top, bot) in enumerate(((70, -60, 0), (52, -110, -50), (34, -150, -100), (18, -190, -140))):
        c.rect(-w2 * 0.8, bot - 10, w2 * 0.8, bot, col, w=2)
        c.poly([(-w2, bot - 6), (0, top), (w2, bot - 6)], roof, w=2.5)
        c.line([(w2 - 6, bot - 10), (w2 + 8, bot - 22)], roof, 4)
        c.line([(-w2 + 6, bot - 10), (-w2 - 8, bot - 22)], roof, 4)
    c.line([(0, -190), (0, -214)], roof, 4)
    c.rect(-12, -36, 12, 0, (40, 26, 20), w=2, r=6)
    c.pop()


def red_house(c, x, y, s=1.0, lit=True, snow_roof=False):
    """A small red Norwegian wooden house with white trim and a turf/snow roof."""
    c.push(x, y, s)
    red = (176, 46, 40)
    c.rect(-60, -70, 60, 0, red, w=2.5)
    for k in range(1, 12):
        c.line([(-60 + k * 10, -68), (-60 + k * 10, -2)], mix(red, (0, 0, 0), 0.2), 1.5, cap=False)
    c.poly([(-72, -66), (0, -116), (72, -66)], SNOW if snow_roof else (80, 120, 70), w=2.5)
    c.line([(-72, -66), (0, -116), (72, -66)], (250, 250, 246), 3)
    win = (255, 220, 120) if lit else (70, 80, 110)
    for wx in (-30, 30):
        c.rect(wx - 12, -54, wx + 12, -30, win, w=2)
        c.line([(wx, -54), (wx, -30)], (250, 250, 246), 2, cap=False)
    c.rect(-8, -34, 8, 0, (250, 250, 246), w=2)
    c.pop()


def norway_mountain(c, x, base, w, h, col, snow=SNOW, ol=OUT, seed=0, snowline=0.35, flat=0.0):
    """A rounded Norwegian mountain (fjell) with patchy snow near the top."""
    rng = np.random.default_rng(seed)
    n = 18
    pts = []
    for i in range(n + 1):
        u = i / n
        prof = math.sin(math.pi * u) ** (0.8 + flat)
        pts.append((x - w / 2 + w * u, base - h * prof + rng.uniform(-6, 6) * (0 < i < n)))
    c.poly(pts, col, ol=ol, w=2.5)
    cap = [p for p in pts if p[1] < base - h * (1 - snowline)]
    if len(cap) >= 2:
        yb = base - h * (1 - snowline)
        poly = cap[:]
        for k in range(len(cap) - 1, -1, -1):
            px = cap[k][0]
            poly.append((px, max(cap[k][1] + 4, yb + rng.uniform(-14, 16))))
        c.poly(poly, snow, ol=None)
