"""Props for Episode 2: Albert the albatross, one famous animal or place per continent,
penguins and ice for Antarctica, small quiz / fact icons."""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, OUT, lerp, clamp, mix, ease
from world import kit as K
from films.paris.props import eiffel, head_pos

WHITE = (250, 250, 248)
WING = (70, 74, 92)
WING_L = (104, 108, 128)
BEAK = (250, 196, 150)
BEAK_D = (214, 150, 110)
FOOT = (236, 170, 170)

# continent colours from the "continents" map style (so insets and charts match the map)
CCOL = {"North America": (255, 168, 80), "South America": (140, 206, 90), "Europe": (172, 140, 232),
        "Africa": (255, 214, 86), "Asia": (240, 118, 128), "Australia": (84, 200, 190),
        "Antarctica": (226, 236, 248)}


# ============================================================================ Albert

def _wing(c, sx, sy, ang, length, col, tipcol):
    """A long narrow albatross wing from the shoulder (sx, sy), pointing at angle ang (rad, 0 = back)."""
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    pts = [(sx + px * 14, sy + py * 14)]
    for u, wd in ((0.25, 20), (0.55, 17), (0.8, 12), (1.0, 3)):
        pts.append((sx + dx * length * u + px * wd, sy + dy * length * u + py * wd))
    for u, wd in ((0.85, -6), (0.55, -9), (0.25, -12)):
        pts.append((sx + dx * length * u + px * wd, sy + dy * length * u + py * wd))
    pts.append((sx - px * 12, sy - py * 12))
    c.poly(pts, col, w=2.5)
    # dark feather tips
    tip = [(sx + dx * length * u + px * wd, sy + dy * length * u + py * wd)
           for u, wd in ((0.7, 15), (1.0, 3), (0.75, -7))]
    c.poly(tip, tipcol, ol=None)


def albatross(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", flap=0.0, stand=False, wave=0.0,
              look=(0.0, 0.0), seed=3.0):
    """Albert the albatross, side view facing right (face=1).

    Flying: (x, y) = body centre; flap 0..1 = how much the wings beat (0 = gliding).
    stand=True: (x, y) = feet on the ground, wings folded (wave lifts the front wing)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    if stand:
        c.push(0, -74, 1.0)
        for fx in (-8, 12):                                  # legs + webbed feet
            c.stroke([(fx, 26), (fx + 2, 72)], FOOT, 7)
            c.poly([(fx - 10, 74), (fx + 22, 74), (fx + 6, 66)], FOOT, w=2)
    else:
        c.push(0, 0, 1.0)
        c.stroke([(-40, 18), (-62, 26)], FOOT, 6)            # tucked feet trailing behind
    b = (0.5 - 0.5 * math.cos(t * 7.0)) * flap          # 0 = wings up, 1 = wings down
    glide = 6 * math.sin(t * 2.2) * (1 - flap)
    if not stand:
        _wing(c, -6, -14, math.radians(-128 - 70 * b + glide), 190, WING, (44, 46, 60))
    # tail
    c.poly([(-58, -8), (-92, -14), (-96, 2), (-60, 10)], WING, w=2.5)
    # body
    c.ellipse(0, 0, 66, 30, WHITE)
    if stand:
        # folded wing along the back
        c.poly([(-30, -24), (30, -26), (52, -14), (10, 6), (-82, -2)], WING, w=2.5)
        c.line([(-60, -6), (20, -10)], WING_L, 2)
    # head + neck
    c.ellipse(46, -22, 26, 20, WHITE, ol=None)
    hx, hy = 64, -34
    c.circle(hx, hy, 24, WHITE)
    c.ellipse(36, -14, 22, 16, WHITE, ol=None)
    # beak (lower jaw opens with mouth)
    m = clamp(mouth)
    c.poly([(hx + 14, hy + 6), (hx + 62, hy + 10 + 8 * m), (hx + 60, hy + 16 + 10 * m), (hx + 14, hy + 14)],
           BEAK_D, w=2.5)
    c.poly([(hx + 12, hy - 4), (hx + 58, hy + 2), (hx + 68, hy + 6), (hx + 64, hy + 14), (hx + 56, hy + 9),
            (hx + 14, hy + 9)], BEAK, w=2.5)
    c.line([(hx + 24, hy + 3), (hx + 40, hy + 4)], BEAK_D, 2)
    # eye with the albatross' dark 'eyebrow' smudge
    ex, ey = hx + 6, hy - 6
    c.ellipse(ex - 2, ey - 3, 13, 6, (196, 196, 206), ol=None)
    if eyes == "closed":
        c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
    elif eyes == "happy":
        c.arc(ex, ey + 3, 6, 6, 200, 340, OUT, 2.5)
    else:
        big = 1.25 if eyes == "wide" else 1.0
        c.ellipse(ex, ey, 6 * big, 7 * big, (255, 255, 255), w=2)
        c.ellipse(ex + 1 + look[0] * 2, ey + 1 + look[1] * 2, 3.4 * big, 4.6 * big, (40, 30, 30), ol=None)
        c.circle(ex + 2 + look[0] * 2, ey - 1, 1.3, (255, 255, 255), ol=None)
    # front wing
    if stand:
        if wave > 0.01:
            a = math.radians(-50 - 25 * math.sin(t * 9))
            _wing(c, 14, -18, lerp(math.radians(-170), a, clamp(wave)), 130, WING_L, WING)
    else:
        _wing(c, 8, -12, math.radians(-58 + 70 * b - glide), 200, WING_L, WING)
    c.pop()
    c.pop()


# ======================================================================= animals

def lion(c, x, y, s=1.0, t=0.0, roar=0.0):
    """Friendly lion sitting, front view. (x, y) = bottom centre."""
    c.push(x, y, s)
    body, mane, mane_d = (236, 186, 92), (196, 112, 46), (160, 84, 34)
    c.ellipse(0, -60, 54, 62, body)
    c.ellipse(-26, -6, 22, 12, body)
    c.ellipse(26, -6, 22, 12, body)
    c.stroke([(48, -20), (82, -30), (92, -60)], body, 9)
    c.circle(94, -64, 10, mane_d)
    for i in range(14):
        a = i / 14 * math.tau + math.sin(t * 2) * 0.03
        c.circle(math.cos(a) * 58, -136 + math.sin(a) * 56, 24, mane if i % 2 else mane_d)
    c.circle(0, -136, 58, mane, ol=None)
    c.circle(0, -134, 44, body)
    c.circle(-30, -170, 12, body)
    c.circle(30, -170, 12, body)
    for ex in (-16, 16):
        c.ellipse(ex, -144, 6, 8, (60, 40, 30), ol=None)
        c.circle(ex + 2, -147, 2, (255, 255, 255), ol=None)
    c.ellipse(0, -118, 20, 14, (250, 226, 170), ol=None)
    c.poly([(-9, -128), (9, -128), (0, -118)], (120, 70, 60), w=1.5)
    if roar > 0.05:
        c.ellipse(0, -104, 10 + 4 * roar, 4 + 10 * roar, (140, 50, 50), w=2)
    else:
        c.arc(-6, -114, 6, 5, 0, 180, OUT, 2)
        c.arc(6, -114, 6, 5, 0, 180, OUT, 2)
    c.pop()


def elephant(c, x, y, s=1.0, t=0.0, face=1):
    """Elephant side view. (x, y) = feet."""
    c.push(x, y, s, flip=face < 0)
    g, gd = (160, 166, 180), (128, 132, 148)
    for lx in (-60, 40):
        c.rect(lx - 16, -60, lx + 16, 0, gd, r=6)
    c.stroke([(-92, -90), (-108, -60)], g, 6)
    c.ellipse(-10, -96, 96, 62, g)
    for lx in (-40, 60):
        c.rect(lx - 17, -56, lx + 17, 0, g, r=6)
    c.circle(84, -122, 46, g)
    sw = math.sin(t * 2) * 6
    c.stroke([(116, -110), (138, -70), (136 + sw, -30), (150 + sw, -18)], g, 22)
    c.poly([(108, -100), (122, -96), (132, -86)], (255, 252, 240), w=2)
    c.ellipse(52, -118, 36, 46, gd)
    c.circle(96, -136, 5, (40, 30, 30), ol=None)
    c.pop()


def pyramids(c, x, y, s=1.0):
    """Three pyramids of Giza. (x, y) = ground centre."""
    c.push(x, y, s)
    for px, h, w in ((-110, 90, 100), (90, 70, 80), (-10, 140, 150)):
        c.poly([(px - w, 0), (px, -h * 1.0), (px + w, 0)], (236, 200, 120), w=3)
        c.poly([(px, -h), (px + w, 0), (px + w * 0.25, 0)], (206, 164, 92), ol=None)
        for k in range(1, 5):
            yy = -h * k / 5
            hw = w * (1 - k / 5)
            c.line([(px - hw, yy), (px + hw, yy)], (214, 176, 100), 1.5, cap=False)
    c.pop()


def panda(c, x, y, s=1.0, t=0.0, chew=0.0):
    """Giant panda sitting and munching bamboo. (x, y) = bottom centre."""
    c.push(x, y, s)
    blk, wht = (44, 42, 50), (250, 250, 250)
    c.ellipse(-36, -16, 30, 20, blk)
    c.ellipse(36, -16, 30, 20, blk)
    c.ellipse(0, -66, 62, 64, wht)
    c.ellipse(0, -96, 64, 22, blk, ol=None)            # shoulder band
    # bamboo
    c.stroke([(-56, -40), (70, -190)], (130, 190, 80), 9)
    for u in (0.3, 0.6):
        bx, by = lerp(-56, 70, u), lerp(-40, -190, u)
        c.line([(bx - 6, by + 2), (bx + 6, by - 2)], (90, 150, 60), 3)
    for lx, ly, a in ((54, -170, -0.4), (70, -150, 0.5)):
        c.ellipse(lx + 12 * math.cos(a), ly + 12 * math.sin(a), 16, 6, (110, 180, 80))
    c.ellipse(-30, -70, 18, 30, blk)                  # arm holding the bamboo
    c.ellipse(34, -76, 18, 26, blk)
    # head
    hy = -150 + math.sin(t * 6) * 2 * chew
    c.circle(-34, hy - 36, 16, blk)
    c.circle(34, hy - 36, 16, blk)
    c.ellipse(0, hy, 50, 44, wht)
    for ex in (-18, 18):
        c.ellipse(ex, hy - 4, 12, 15, blk, ol=None)
        c.circle(ex + (2 if ex > 0 else -2), hy - 6, 4.5, (255, 255, 255), ol=None)
        c.circle(ex + (2 if ex > 0 else -2), hy - 6, 2.5, (30, 30, 30), ol=None)
    c.ellipse(0, hy + 14, 7, 5, blk, ol=None)
    m = 0.5 + 0.5 * math.sin(t * 12) if chew else 0
    c.ellipse(0, hy + 25, 5 + 2 * m, 2 + 4 * m, (150, 60, 70), ol=OUT, w=1.5)
    c.pop()


def great_wall(c, x, y, s=1.0, w=520):
    """The Great Wall winding over green hills. (x, y) = left end of the ground line."""
    c.push(x, y, s)
    hills = [(0, 0)] + [(w * u, -60 * math.sin(u * math.pi * 2.2) ** 2 - 30 * u) for u in np.linspace(0, 1, 30)] \
        + [(w, 0)]
    c.poly(hills + [(w, 40), (0, 40)], (120, 186, 100), ol=None)
    top = [(px, py - 18) for px, py in hills[1:-1]]
    bot = [(px, py + 2) for px, py in hills[1:-1]]
    c.poly(top + bot[::-1], (206, 176, 136), w=2.5)
    for i, (px, py) in enumerate(top[:-1]):
        if i % 2 == 0:
            c.rect(px - 4, py - 8, px + 4, py, (206, 176, 136), w=1.5)
    for u in (0.22, 0.68):
        i = int(u * (len(top) - 1))
        px, py = top[i]
        c.rect(px - 18, py - 40, px + 18, py + 18, (196, 164, 124), w=2.5)
        c.poly([(px - 24, py - 40), (px, py - 58), (px + 24, py - 40)], (170, 70, 60), w=2.5)
        c.rect(px - 6, py - 30, px + 6, py - 16, (80, 60, 50), ol=None)
    c.pop()


def kangaroo(c, x, y, s=1.0, t=0.0, hop=0.0, face=1):
    """Kangaroo with a joey peeking from her pouch. (x, y) = feet."""
    c.push(x, y - hop, s, flip=face < 0)
    fur, fur_d, belly = (196, 130, 80), (160, 100, 60), (236, 200, 160)
    c.stroke([(-30, -40), (-90, -10), (-130, 6)], fur_d, 16)          # tail
    c.ellipse(10, 0, 44, 10, fur_d)                                     # big feet
    c.ellipse(-10, -46, 38, 44, fur)                                    # haunch
    c.ellipse(16, -100, 34, 52, fur)                                    # body
    c.ellipse(28, -88, 20, 34, belly, ol=None)
    c.arc(34, -78, 18, 14, 10, 170, fur_d, 3)                          # pouch
    c.circle(36, -96, 12, fur)                                          # joey
    c.circle(31, -99, 2.5, (30, 20, 20), ol=None)
    c.circle(42, -98, 2.5, (30, 20, 20), ol=None)
    c.ellipse(34, -112, 4, 8, fur)
    c.stroke([(36, -122), (56, -106)], fur, 7)                          # arm
    c.ellipse(30, -164, 24, 22, fur)                                    # head
    c.ellipse(52, -158, 18, 12, fur)
    c.circle(64, -160, 4, (40, 30, 30), ol=None)
    c.ellipse(14, -194, 8, 20, fur)                                     # ears
    c.ellipse(28, -198, 8, 20, fur)
    c.circle(38, -168, 4, (40, 30, 30), ol=None)
    c.circle(39, -169, 1.4, (255, 255, 255), ol=None)
    c.pop()


def penguin(c, x, y, s=1.0, face=1, t=0.0, waddle=0.0, eyes="open", flap=0.0, seed=0.0):
    """Emperor penguin. (x, y) = feet."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    rock = math.sin(waddle) * 0.08
    c.push(x, y, s, flip=face < 0)
    c.push(0, 0, 1.0)
    bk, wh, gold = (40, 44, 60), (252, 252, 250), (255, 196, 70)
    c.ellipse(-12, -2, 14, 6, (240, 160, 60))
    c.ellipse(12, -2, 14, 6, (240, 160, 60))
    sh = math.sin(rock) * 40
    c.ellipse(sh * 0.3, -60, 38, 60, bk)
    c.ellipse(6 + sh * 0.3, -54, 28, 50, wh, ol=None)
    fa = math.sin(t * 10) * flap
    c.poly([(-30 + sh * 0.3, -90), (-50 + sh * 0.3, -40 + 10 * fa), (-36 + sh * 0.3, -40)], bk, w=2)
    hx = 10 + sh * 0.4
    c.circle(hx, -126, 26, bk)
    c.ellipse(hx + 10, -112, 12, 14, gold, ol=None)
    c.ellipse(hx + 8, -98, 16, 8, (255, 230, 150), ol=None)
    c.poly([(hx + 20, -128), (hx + 44, -120), (hx + 20, -116)], (60, 50, 60), w=1.5)
    c.line([(hx + 24, -121), (hx + 38, -120)], (250, 150, 80), 2)
    if eyes == "closed":
        c.arc(hx + 10, -134, 5, 3, 20, 160, (255, 255, 255), 2)
    elif eyes == "happy":
        c.arc(hx + 10, -132, 5, 5, 200, 340, (255, 255, 255), 2.5)
    else:
        c.circle(hx + 10, -134, 5, (255, 255, 255), ol=None)
        c.circle(hx + 11, -134, 2.6, (20, 20, 30), ol=None)
    c.pop()
    c.pop()


def llama(c, x, y, s=1.0, t=0.0, face=1):
    """Llama standing. (x, y) = feet."""
    c.push(x, y, s, flip=face < 0)
    wool, wool_d = (246, 236, 214), (214, 200, 174)
    for lx in (-40, 30):
        c.rect(lx - 8, -60, lx + 8, 0, wool_d, r=4)
    c.ellipse(-4, -76, 64, 34, wool)
    for lx in (-30, 40):
        c.rect(lx - 9, -58, lx + 9, 0, wool, r=4)
    c.circle(-66, -84, 12, wool)
    c.rect(36, -170, 64, -70, wool, r=12)
    c.ellipse(62, -170, 30, 18, wool)
    c.ellipse(84, -164, 12, 10, wool_d, ol=None)
    for ex in (40, 54):
        c.ellipse(ex, -196, 6, 16, wool)
    c.circle(64, -176, 4, (40, 30, 30), ol=None)
    c.circle(65, -177, 1.4, (255, 255, 255), ol=None)
    c.rect(34, -116, 66, -104, (220, 60, 80), r=3, w=2)      # colourful collar
    c.pop()


def jungle_tree(c, x, y, s=1.0, col=(60, 150, 70)):
    c.push(x, y, s)
    c.rect(-8, -120, 8, 0, (120, 84, 56), r=3)
    for dx, dy, r in ((-30, -126, 36), (30, -130, 38), (0, -160, 44), (-12, -112, 26), (20, -110, 26)):
        c.circle(dx, dy, r, mix(col, (0, 0, 0), 0.1 if dy < -140 else 0.0))
    c.pop()


def eagle(c, x, y, s=1.0, t=0.0, face=1):
    """Bald eagle soaring, wings spread (front-ish view). (x, y) = body centre."""
    c.push(x, y, s, flip=face < 0)
    br, br_d = (110, 70, 44), (80, 50, 30)
    fl = math.sin(t * 3) * 8
    for side in (-1, 1):
        pts = [(side * 14, -6), (side * 70, -26 - fl), (side * 130, -30 - fl * 1.6), (side * 160, -18 - fl * 2),
               (side * 140, -6 - fl * 1.6), (side * 150, 4 - fl * 1.4), (side * 124, 4 - fl), (side * 128, 14 - fl),
               (side * 90, 10 - fl * 0.6), (side * 14, 16)]
        c.poly(pts, br, w=2.5)
    c.poly([(-14, 30), (14, 30), (20, 58), (-20, 58)], (255, 255, 255), w=2.5)    # white tail
    c.ellipse(0, 10, 22, 30, br_d)
    c.circle(0, -26, 20, (255, 255, 255))                                         # white head
    c.poly([(8, -26), (28, -22), (24, -12), (8, -16)], (250, 200, 60), w=2)       # yellow beak
    c.circle(6, -32, 3, (30, 20, 20), ol=None)
    c.line([(0, -38), (12, -36)], OUT, 2)
    c.pop()


def bison(c, x, y, s=1.0, t=0.0, face=1):
    """American bison, side view. (x, y) = feet."""
    c.push(x, y, s, flip=face < 0)
    br, br_d, br_l = (112, 76, 52), (80, 52, 36), (150, 104, 70)
    for lx in (-60, 40):
        c.rect(lx - 10, -46, lx + 10, 0, br_d, r=4)
    c.ellipse(-30, -66, 70, 40, br_l)
    c.ellipse(30, -84, 56, 58, br)                         # hump
    for lx in (-50, 50):
        c.rect(lx - 11, -44, lx + 11, 0, br, r=4)
    c.stroke([(-96, -70), (-110, -40)], br_d, 5)
    c.ellipse(84, -64, 32, 34, br_d)                        # shaggy head
    c.ellipse(90, -34, 16, 14, br_d)                        # beard
    c.arc(72, -98, 16, 12, 180, 300, (240, 236, 220), 5)    # horn
    c.circle(96, -72, 4, (20, 14, 10), ol=None)
    c.pop()


def cat_crowd(c, x, y, s=1.0, t=0.0):
    """Three European cats in a row (for 'home of the finest cats')."""
    pals = [dict(D.LUNA, body=(250, 248, 244), dark=(220, 214, 208), belly=(255, 255, 255), collar=(220, 60, 90)),
            dict(D.WHISKERS, body=(80, 76, 86), dark=(56, 52, 62), belly=(200, 196, 206), stripes=False),
            dict(D.WHISKERS, body=(214, 170, 120), dark=(170, 120, 80), collar=(70, 160, 90))]
    for i, pal in enumerate(pals):
        D.cat(c, x + (i - 1) * 70 * s, y, pal, 0.55 * s, 1 if i < 2 else -1, "sit", t=t, seed=i * 1.3)


# ===================================================================== little props

def sunglasses(c, x, y, s, face=1, pose="sit", head_dy=0.0, k=1.0, frost=0.0):
    """Cool sunglasses on a cat drawn with draw.cat(x, y, s, face, pose)."""
    if k <= 0.01:
        return
    hx, hy = head_pos(pose, head_dy=head_dy)
    c.push(x, y, s, flip=face < 0)
    c.push(hx + 10, hy - 4 - 30 * (1 - k), 1.0)
    lens = mix((30, 30, 40), (200, 230, 250), frost)
    for ex in (-12, 12):
        c.ellipse(ex, 0, 13, 10, lens, w=2.5)
        c.line([(ex - 6, -4), (ex - 1, -7)], (255, 255, 255), 2)
    c.line([(-1, -2), (1, -2)], OUT, 3)
    c.line([(-24, -2), (-38, -6)], OUT, 3)
    c.pop()
    c.pop()


def icicles(c, x, y, s, face=1, pose="sit", k=1.0, t=0.0):
    """Icicles hanging from a frozen cat's chin and whiskers."""
    if k <= 0.01:
        return
    hx, hy = head_pos(pose)
    c.push(x, y, s, flip=face < 0)
    for dx, ln in ((0, 18), (10, 26), (22, 20), (36, 14), (48, 22), (-10, 12)):
        L = ln * k
        bx, by = hx + dx, hy + 22 + (8 if dx > 40 or dx < -5 else 0)
        c.poly([(bx - 4, by), (bx + 4, by), (bx, by + L)], (210, 238, 255), ol=(120, 170, 210), w=1.5)
    c.pop()


def frozen(pal, k):
    """A cat palette frosted blue (k = 0..1)."""
    if k <= 0:
        return pal
    ice = (196, 226, 250)
    return dict(pal, body=mix(pal["body"], ice, 0.65 * k), dark=mix(pal["dark"], (150, 196, 236), 0.65 * k),
                belly=mix(pal["belly"], (236, 248, 255), 0.7 * k), ear=mix(pal["ear"], ice, 0.5 * k))


def cheese(c, x, y, r=40):
    c.poly([(x - r, y + r * 0.5), (x + r, y + r * 0.5), (x + r, y - r * 0.1), (x - r * 0.6, y - r * 0.6)],
           (255, 210, 80), w=3)
    c.poly([(x + r, y - r * 0.1), (x - r * 0.6, y - r * 0.6), (x - r, y + r * 0.5 - r * 0.6 + r * 0.6),
            ], (255, 230, 130), ol=None)
    for hx, hy, hr in ((-0.4, 0.2, 0.12), (0.2, 0.25, 0.09), (0.55, 0.05, 0.1)):
        c.circle(x + hx * r, y + hy * r, hr * r, (230, 170, 50), ol=None)


def sweet(c, x, y, r=22, col=(240, 100, 140)):
    for side in (-1, 1):
        c.poly([(x + side * r * 0.8, y), (x + side * r * 1.6, y - r * 0.6), (x + side * r * 1.6, y + r * 0.6)],
               mix(col, (255, 255, 255), 0.3), w=2)
    c.circle(x, y, r, col, w=2.5)
    c.arc(x, y, r * 0.6, r * 0.6, 200, 320, (255, 255, 255), 3)


def fish_snack(c, x, y, s=1.0, col=(120, 180, 230)):
    c.push(x, y, s)
    c.ellipse(0, 0, 20, 11, col, w=2)
    c.poly([(-18, 0), (-32, -10), (-32, 10)], col, w=2)
    c.circle(10, -2, 2.5, OUT, ol=None)
    c.pop()


def beach(c, x, y, s=1.0, t=0.0):
    """Daydream beach: sun, sand, sea, palm tree and a parasol."""
    c.push(x, y, s)
    c.circle(50, -60, 22, (255, 220, 90), ol=None)
    c.rect(-90, -10, 90, 10, (90, 170, 230), ol=None)
    c.ellipse(0, 20, 96, 24, (250, 220, 150), ol=None)
    c.stroke([(-40, 20), (-46, -20), (-36, -60)], (150, 100, 60), 7)
    for a in (-2.6, -1.8, -0.9, -0.3):
        c.ellipse(-36 + 26 * math.cos(a), -62 + 12 * math.sin(a), 26, 8, (80, 170, 80), ol=None)
    c.line([(30, 24), (36, -16)], (90, 80, 80), 3)
    c.poly([(6, -12), (36, -34), (66, -12)], (240, 90, 100), w=2)
    c.pop()


def thermometer(c, x, y, s=1.0, level=1.0, t=0.0):
    """A big thermometer; level 1 = warm (full) ... 0 = freezing (empty, blue)."""
    c.push(x, y, s)
    c.rect(-18, -170, 18, 0, (255, 255, 255), r=18, w=3)
    c.circle(0, 12, 28, (255, 255, 255), w=3)
    col = mix((90, 160, 240), (230, 70, 70), clamp(level))
    top = lerp(-10, -150, clamp(level))
    c.rect(-9, top, 9, 4, col, ol=None, r=8)
    c.circle(0, 12, 20, col, ol=None)
    for k in range(6):
        yy = -30 - k * 22
        c.line([(18, yy), (28, yy)], OUT, 2.5)
    c.pop()


def station(c, x, y, s=1.0):
    """A small red research station on legs (for 'scientists only visit')."""
    c.push(x, y, s)
    for lx in (-50, 50):
        c.rect(lx - 5, -30, lx + 5, 0, (120, 120, 130), w=2)
    c.rect(-70, -80, 70, -30, (220, 70, 60), r=8, w=3)
    for wx in (-40, 0, 40):
        c.rect(wx - 12, -66, wx + 12, -48, (190, 226, 250), r=3, w=2)
    c.line([(40, -80), (40, -116)], (90, 90, 100), 3)
    c.poly([(40, -116), (66, -108), (40, -100)], (255, 200, 60), w=2)
    c.pop()


def snowflake(c, x, y, r, col=(140, 196, 240), w=4):
    for i in range(6):
        a = i * math.pi / 3
        ex, ey = x + math.cos(a) * r, y + math.sin(a) * r
        c.line([(x, y), (ex, ey)], col, w)
        for f in (0.55,):
            bx, by = x + math.cos(a) * r * f, y + math.sin(a) * r * f
            for da in (0.6, -0.6):
                c.line([(bx, by), (bx + math.cos(a + da) * r * 0.3, by + math.sin(a + da) * r * 0.3)], col, w * 0.7)


# =========================================================================== icons

def icon_seven(c, x, y, r, t=0.0):
    """Globe in continent colours with a '7' badge."""
    K.globe(c, x, y, r * 0.9, lon=-t * 30 + 40, lat=15, style="continents")
    c.circle(x + r * 0.62, y + r * 0.58, r * 0.38, (226, 70, 80), w=2.5)
    K.text(c, x + r * 0.62, y + r * 0.6, "7", r * 0.5, (255, 255, 255), stroke=2)


SIZES = [("Asia", 44.6), ("Africa", 30.4), ("North America", 24.7), ("South America", 17.8),
         ("Antarctica", 14.2), ("Europe", 10.2), ("Australia", 8.6)]   # million square km (approx.)


def icon_biggest(c, x, y, r, t=0.0):
    """Mini bar chart: Asia's bar towers over the rest."""
    n = len(SIZES)
    bw = r * 1.4 / n
    for i, (name, a) in enumerate(SIZES):
        h = r * 1.3 * a / SIZES[0][1]
        bx = x - r * 0.7 + i * bw
        c.rect(bx, y + r * 0.65 - h, bx + bw - 2, y + r * 0.65, CCOL[name] if name != "Antarctica" else (200, 214, 232),
               w=1.5)
    K.star(c, x - r * 0.7 + bw / 2, y + r * 0.65 - r * 1.3 - 6, r * 0.2, (255, 220, 80), ol=OUT)


def icon_cold(c, x, y, r, t=0.0):
    """A penguin on an ice floe with a snowflake."""
    c.ellipse(x, y + r * 0.62, r * 0.85, r * 0.2, (230, 244, 255), ol=(120, 170, 210), w=2)
    penguin(c, x - r * 0.12, y + r * 0.62, r / 160, 1, t)
    snowflake(c, x + r * 0.52, y - r * 0.45, r * 0.26, (90, 160, 230), 3)


def icon_number(n, col):
    def f(c, x, y, r, t=0.0):
        c.circle(x, y, r * 0.95, col, w=4)
        K.text(c, x, y + 4, str(n), r * 1.3, (255, 255, 255), stroke=4)
    return f


def icon_hot(c, x, y, r, t=0.0):
    """Africa: hot sun over sand dunes and a lion's mane."""
    c.circle(x, y, r * 0.95, (255, 236, 170), w=3)
    for i in range(10):
        a = i / 10 * math.tau + t
        c.line([(x + math.cos(a) * r * 0.42, y - r * 0.25 + math.sin(a) * r * 0.42),
                (x + math.cos(a) * r * 0.56, y - r * 0.25 + math.sin(a) * r * 0.56)], (250, 170, 60), 4)
    c.circle(x, y - r * 0.25, r * 0.3, (255, 200, 70), w=2.5)
    c.poly([(x - r * 0.85, y + r * 0.5), (x - r * 0.3, y + r * 0.15), (x + r * 0.2, y + r * 0.45),
            (x + r * 0.6, y + r * 0.2), (x + r * 0.9, y + r * 0.45), (x + r * 0.5, y + r * 0.85),
            (x - r * 0.5, y + r * 0.85)], (240, 196, 110), ol=None)
