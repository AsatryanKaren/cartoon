"""Copenhagen props and new characters, drawn in the flat cartoon style.

Characters: Saga (a scruffy grey cygnet who becomes a white swan), Bodil (a
jolly baker seal), the cheeky harbour ducks and the rabbit royal guards.
Places: Nyhavn's gabled houses and wooden ships, Our Saviour's twisting spire,
copper roofs, the Amalienborg palace, the Little Mermaid on her rock, Tivoli's
lanterns, carousel and old wooden roller coaster. Props: the flying trunk, the
fairy-tale book, pastries, open sandwiches, candles, blankets and cocoa.
"""
import math

import numpy as np

import draw as D
from draw import OUT, lerp, clamp, ease, mix

# ----------------------------------------------------------------- palette

WATER = (60, 112, 160)
WATER_L = (130, 180, 215)
COBBLE = (176, 160, 146)
COBBLE_D = (150, 134, 122)
COPPER = (110, 184, 160)
COPPER_D = (80, 150, 130)
BRASS = (236, 190, 80)
LEATHER = (150, 86, 52)
LEATHER_D = (116, 62, 38)
WOOD = (166, 112, 70)
WOOD_D = (120, 78, 48)
DK_RED = (200, 16, 46)
HOUSE_COLS = [(244, 196, 70), (226, 92, 60), (90, 150, 200), (246, 150, 70), (236, 226, 200),
              (150, 190, 120), (214, 110, 120), (250, 214, 120), (120, 160, 190), (230, 130, 90)]
LANTERN_COLS = [(255, 90, 90), (255, 200, 80), (120, 220, 120), (110, 180, 255), (255, 150, 220), (255, 240, 200)]


def heart(c, x, y, r, col, ol=None):
    c.circle(x - r * 0.5, y, r * 0.6, col, ol=ol, w=1.5)
    c.circle(x + r * 0.5, y, r * 0.6, col, ol=ol, w=1.5)
    c.poly([(x - r * 1.05, y + r * 0.15), (x + r * 1.05, y + r * 0.15), (x, y + r * 1.2)], col, ol=None)
    c.circle(x - r * 0.5, y, r * 0.5, col, ol=None)
    c.circle(x + r * 0.5, y, r * 0.5, col, ol=None)


def star(c, x, y, r, col, ol=OUT, w=1.5):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, col, ol=ol, w=w)


# ------------------------------------------------------------------- trunk

def trunk(c, x, y, s=1.0, lid=0.0, glow=0.0, part="all", tilt=0.0, t=0.0):
    """The old flying trunk. Origin = bottom centre, ~200 wide, ~100 tall (closed).
    lid: 0 closed .. 1 wide open (hinged at the back). part: all | back | front."""
    c.push(x, y, s)
    if tilt:
        # cheap tilt: offset the left and right ends
        pass
    if glow > 0.01 and part in ("all", "back"):
        for k in range(3):
            u = (t * 0.8 + k / 3) % 1.0
            c.ellipse(0, -50, (110 + 60 * u), (60 + 40 * u), None, ol=mix((255, 236, 150), (255, 255, 255), u),
                      w=3 * (1 - u) * glow + 0.5)
        rng = np.random.default_rng(int(t * 8))
        for k in range(int(10 * glow)):
            sx, sy = rng.uniform(-120, 120), rng.uniform(-130, 10)
            star(c, sx, sy, rng.uniform(3, 8), (255, 250, 200), ol=None)
    if part in ("all", "back"):
        if lid > 0.02:
            # open lid standing up behind (seen from the inside)
            h = 60 * math.sin(lid * math.pi / 2)
            c.poly([(-100, -96), (100, -96), (96, -96 - h), (-96, -96 - h)], LEATHER_D, w=2.5)
            c.poly([(-90, -98), (90, -98), (86, -94 - h * 0.9), (-86, -94 - h * 0.9)], (190, 70, 70), ol=None)
            # inside back wall
            c.rect(-100, -96, 100, -60, (170, 60, 60), w=2.5)
    if part in ("all", "front"):
        # box
        c.rect(-100, -70 if lid > 0.02 else -78, 100, 0, LEATHER, w=3, r=6)
        if lid <= 0.02:
            # closed rounded lid
            c.rect(-104, -104, 104, -70, LEATHER, w=3, r=12)
            c.line([(-100, -74), (100, -74)], LEATHER_D, 3, cap=False)
        top = -104 if lid <= 0.02 else -70
        # straps and brass corners
        for sx in (-56, 56):
            c.rect(sx - 9, top + 2, sx + 9, 0, (110, 66, 40), w=2)
            c.rect(sx - 11, -40, sx + 11, -30, BRASS, w=1.5, r=2)
        for cx in (-100, 100):
            c.poly([(cx, top + 4), (cx - 16 * (1 if cx > 0 else -1), top + 4), (cx, top + 20)], BRASS, w=1.5)
            c.poly([(cx, -2), (cx - 16 * (1 if cx > 0 else -1), -2), (cx, -18)], BRASS, w=1.5)
        # lock
        c.rect(-12, top - 4 if lid <= 0.02 else top - 2, 12, top + 18, BRASS, w=2, r=3)
        c.circle(0, top + 8, 3, OUT, ol=None)
        # handle on the side
        c.arc(-100, -50, 10, 12, 90, 270, OUT, 3)
        c.arc(100, -50, 10, 12, -90, 90, OUT, 3)
        # little stickers from travels
        c.ellipse(28, -30, 14, 10, (240, 220, 160), w=1.5)
        c.rect(-34, -46, -16, -24, (120, 170, 210), w=1.5, r=2)
    c.pop()


# --------------------------------------------------------------- the book

def book_cover(c, x, y, s=1.0, ang=0.0):
    """Closed fairy-tale book lying flat-ish (seen from the front)."""
    c.push(x, y, s)
    c.rect(-60, -16, 60, 0, (250, 240, 214), w=2.5, r=2)
    c.rect(-64, -24, 64, -14, (40, 90, 150), w=2.5, r=3)
    c.rect(-64, -8, 64, 2, (40, 90, 150), w=2.5, r=3)
    c.pop()


def book_open(c, x, y, w=620, h=380, page="trunk", t=0.0):
    """Open picture book (overlay). page: trunk | duckling."""
    c.push(x, y)
    c.poly([(-w / 2 - 16, -h / 2 - 6), (w / 2 + 16, -h / 2 - 6), (w / 2 + 16, h / 2 + 14), (-w / 2 - 16, h / 2 + 14)],
           (40, 90, 150), w=3)
    c.rect(-w / 2, -h / 2, -2, h / 2, (252, 246, 228), w=2.5, r=4)
    c.rect(2, -h / 2, w / 2, h / 2, (252, 246, 228), w=2.5, r=4)
    c.line([(0, -h / 2), (0, h / 2)], (200, 190, 170), 3)
    lx, rx = -w / 4, w / 4
    if page == "trunk":
        c.text(lx, -h / 2 + 40, "The Flying Trunk", 26, (60, 70, 120))
        for k in range(6):
            c.line([(lx - 110, -h / 2 + 90 + k * 34), (lx + 110 - 30 * (k == 5), -h / 2 + 90 + k * 34)],
                   (180, 170, 160), 3)
        # picture: a trunk flying over rooftops under the moon
        c.rect(rx - 130, -h / 2 + 30, rx + 130, h / 2 - 30, (60, 70, 130), w=2)
        D.moon(c, rx + 80, -h / 2 + 80, 22, sky=(60, 70, 130))
        for k in range(5):
            hx = rx - 130 + k * 52
            hh = 50 + 26 * ((k * 7) % 3)
            c.rect(hx, h / 2 - 30 - hh, hx + 52, h / 2 - 30, HOUSE_COLS[k], w=1.5)
            c.poly([(hx, h / 2 - 30 - hh), (hx + 26, h / 2 - 60 - hh), (hx + 52, h / 2 - 30 - hh)],
                   (150, 70, 60), w=1.5)
        bob = math.sin(t * 2) * 6
        trunk(c, rx - 30, -10 + bob, 0.45)
        for k in range(3):
            c.line([(rx - 90 - k * 12, -40 + k * 10 + bob), (rx - 140 - k * 4, -40 + k * 10 + bob)],
                   (255, 255, 255), 2)
    else:
        c.text(lx, -h / 2 + 40, "The Ugly Duckling", 26, (60, 70, 120))
        for k in range(6):
            c.line([(lx - 110, -h / 2 + 90 + k * 34), (lx + 110 - 30 * (k == 5), -h / 2 + 90 + k * 34)],
                   (180, 170, 160), 3)
        c.rect(rx - 130, -h / 2 + 30, rx + 130, h / 2 - 30, (170, 210, 240), w=2)
        c.rect(rx - 128, 40, rx + 128, h / 2 - 32, (90, 150, 200), ol=None)
        cygnet(c, rx - 70, 70, 0.5, 1, t, white=0.0, swim=True, seed=1.0)
        cygnet(c, rx + 50, 70, 0.6, -1, t, white=1.0, swim=True, seed=2.0)
        heart(c, rx - 10, -60, 14, (240, 90, 120))
    c.pop()


# --------------------------------------------------------------- characters

def cygnet(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", white=0.0, wing=0.0, fly=False,
           swim=False, walk=0.0, seed=4.0, look=(0.0, 0.0), sad=False):
    """Saga. white: 0 scruffy grey cygnet .. 1 young white swan. ~120 tall at s=1.
    Origin = between the feet (or the waterline when swim). wing: 0 folded .. 1 raised; fly flaps."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    body = mix((150, 150, 160), (252, 252, 255), white)
    shade = mix((118, 118, 132), (214, 222, 240), white)
    beak = mix((70, 70, 80), (246, 140, 50), white)
    c.push(x, y, s, flip=face < 0)
    if not swim and not fly:
        foot = mix((80, 80, 90), (60, 60, 66), white)
        for k, fx in enumerate((-10, 12)):
            sw = math.sin(walk + k * math.pi) * 8 if walk else 0
            lift = -max(0.0, math.cos(walk + k * math.pi)) * 5 if walk else 0
            c.stroke([(fx, -22), (fx + sw, -4 + lift)], foot, 6)
            c.poly([(fx + sw - 10, lift), (fx + sw + 14, lift), (fx + sw + 2, -8 + lift)], foot, w=1.5)
        c.push(0, -18)
    elif fly:
        c.push(0, -30)
        # tucked feet trailing behind
        c.stroke([(-30, -10), (-52, -4)], (70, 70, 80), 4)
    # tail tuft
    c.poly([(-56, -30), (-40, -20), (-36, -36)], body, w=2)
    # far wing when flying
    fl = math.sin(t * 9 + seed) if fly else 0.0
    if fly:
        _wing(c, 6, -40, fl, mix(shade, OUT, 0.15), far=True)
    c.ellipse(-4, -26, 44, 24, body, w=2.5)
    if swim:
        c.rect(-48, -18, 44, 0, body, ol=None)
        c.line([(-50, -1), (46, -1)], OUT, 2.5)
    # scruffy fluff tufts (fewer as she becomes a swan)
    if white < 0.7:
        rng = np.random.default_rng(int(seed * 10))
        for k in range(7):
            fx, fy = rng.uniform(-40, 30), rng.uniform(-46, -10)
            c.poly([(fx - 4, fy), (fx + rng.uniform(-6, 6), fy - 10), (fx + 4, fy)], body, w=1.2)
    # near wing
    if fly:
        _wing(c, -4, -34, fl, shade)
    else:
        wa = wing
        c.poly([(-36, -28), (-24, -40 - 30 * wa), (6, -48 - 50 * wa), (24, -34 - 14 * wa), (14, -18), (-20, -14)],
               shade, w=2)
    # neck (gets longer and more elegant as a swan)
    nl = 1.0 + 0.25 * white
    bend = 4 if sad else 0
    pts = [(26, -30), (34, -48 * nl), (32, -64 * nl + bend), (26, -78 * nl + bend * 2)]
    c.stroke(pts, body, 15)
    hx, hy = 30, -86 * nl + bend * 2.5
    c.ellipse(hx, hy, 15, 13, body, w=2.5)
    c.stroke(pts[-2:], body, 11, ol=None)
    if white < 0.7:
        c.poly([(hx - 8, hy - 10), (hx - 4, hy - 22), (hx + 2, hy - 11)], body, w=1.5)   # head tuft
    # beak
    jaw = mouth * 6
    c.poly([(hx + 10, hy - 4), (hx + 34, hy + 1), (hx + 32, hy + 4), (hx + 10, hy + 3)], beak, w=2)
    c.poly([(hx + 10, hy + 3), (hx + 30, hy + 5 + jaw), (hx + 27, hy + 8 + jaw), (hx + 9, hy + 7)],
           mix(beak, (0, 0, 0), 0.2), w=2)
    if white > 0.5:
        c.circle(hx + 12, hy - 5, 3, (40, 40, 40), ol=None)
    ex, ey = hx + 3 + look[0] * 1.5, hy - 3 + look[1] * 1.5
    if eyes == "closed":
        c.arc(ex, ey, 4, 3, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(ex, ey + 1, 4, 4, 200, 340, OUT, 2)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        c.circle(ex, ey, 4.5 * big, (255, 255, 255), w=1.5)
        c.circle(ex + 1, ey, 2.6 * big, (30, 25, 30), ol=None)
        c.circle(ex + 1.8, ey - 1.2, 1, (255, 255, 255), ol=None)
    if sad:
        c.line([(ex - 6, ey - 8), (ex + 4, ey - 6)], OUT, 1.5)
    c.pop()
    if not swim:
        c.pop()


def _wing(c, sx, sy, fl, col, far=False):
    """A feathered wing from the shoulder (sx, sy); fl -1..1 flaps it up and down."""
    lift = 60 * fl + (8 if far else 0)
    tipx, tipy = sx - 50, sy - 40 - lift
    pts = [(sx + 18, sy), (sx + 6, sy - 24 - lift * 0.5), (tipx + 10, tipy - 6), (tipx, tipy)]
    # trailing edge: scalloped primaries back toward the body
    n = 5
    for k in range(1, n + 1):
        u = k / n
        bx = lerp(tipx, sx - 26, u)
        by = lerp(tipy, sy + 2, u)
        pts.append((bx + 8, by + 10 - 2 * (k % 2)))
        pts.append((bx + 2, by + 4))
    c.poly(pts, col, w=2)
    for k in range(3):
        u = (k + 1) / 4
        c.line([(lerp(sx + 4, tipx, u), lerp(sy - 10 - lift * 0.3, tipy, u)),
                (lerp(sx - 10, tipx + 8, u) + 6, lerp(sy, tipy + 10, u) + 6)], mix(col, OUT, 0.3), 1.5)


def duck(c, x, y, s=1.0, face=1, t=0.0, laugh=0.0, walk=0.0, seed=0.0, fall=0.0, swim=False):
    """A cheeky mallard drake. ~70 tall at s=1. laugh 0..1 shakes and opens the beak."""
    shake = math.sin(t * 30) * 2 * laugh
    c.push(x + shake, y - abs(math.sin(t * 12 + seed)) * 4 * laugh, s, flip=face < 0)
    if fall:
        c.push(0, -20)
        c.tf[-1] = (c.tf[-1][0], c.tf[-1][1], c.tf[-1][2], c.tf[-1][3] * (1 - 2 * fall))
    if not swim:
        for k, fx in enumerate((-6, 8)):
            sw = math.sin(walk + k * math.pi) * 6 if walk else 0
            c.stroke([(fx, -16), (fx + sw, -3)], (250, 150, 50), 4)
            c.poly([(fx + sw - 7, 0), (fx + sw + 9, 0), (fx + sw + 1, -5)], (250, 150, 50), w=1.5)
    c.poly([(-30, -28), (-20, -22), (-22, -34)], (240, 240, 236), w=1.5)
    c.ellipse(-2, -26, 28, 15, (190, 170, 150), w=2.5)
    if swim:
        c.rect(-30, -18, 26, 0, (190, 170, 150), ol=None)
    c.ellipse(-6, -28, 16, 9, (120, 100, 90), ol=None)
    c.rect(4, -40, 20, -32, (250, 250, 250), ol=None)          # white collar
    c.stroke([(14, -32), (16, -46)], (40, 130, 80), 12)
    c.circle(16, -52, 11, (40, 130, 80), w=2)
    jaw = 6 * laugh * abs(math.sin(t * 14))
    c.poly([(24, -55), (40, -52), (38, -48), (24, -49)], (250, 210, 60), w=1.5)
    c.poly([(24, -49), (38, -47 + jaw), (36, -44 + jaw), (24, -46)], (230, 180, 40), w=1.5)
    if laugh > 0.3:
        c.arc(18, -55, 3, 3, 200, 340, OUT, 2)
    else:
        c.circle(18, -55, 2.2, (20, 20, 20), ol=None)
    if fall:
        c.pop()
    c.pop()


def bodil(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, eyes="open", arm=0.0, seed=6.0, pot=False):
    """Bodil, a round jolly grandmother seal in a baker's hat and apron. ~170 tall at s=1, upright."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    grey, light = (130, 140, 150), (176, 186, 196)
    c.push(x, y, s, flip=face < 0)
    sway = math.sin(t * 1.5 + seed) * 2
    # tail flippers
    c.poly([(-30, -6), (-62, 4), (-56, -14)], grey, w=2)
    c.poly([(-24, -8), (-50, 14), (-40, -14)], grey, w=2)
    c.ellipse(0 + sway * 0.3, -60, 46, 62, grey, w=3)
    c.ellipse(8, -50, 30, 44, light, ol=None)
    # apron
    c.poly([(-22, -96), (30, -96), (40, -10), (-30, -10)], (250, 250, 246), w=2.5)
    c.line([(-26, -92), (38, -92)], (220, 90, 90), 4)
    for k in range(3):
        c.line([(-24 + 6 * k, -40 + k * 12), (34 - 4 * k, -40 + k * 12)], (240, 200, 200), 2, cap=False)
    # flippers (arms)
    a = arm
    c.poly([(-36, -84), (-56, -60 + 30 * a), (-46, -50 + 26 * a), (-28, -70)], grey, w=2.2)
    c.poly([(34, -84), (60 + 6 * a, -66 - 40 * a), (62 + 10 * a, -54 - 40 * a), (32, -68)], grey, w=2.2)
    if pot:
        px, py = 66 + 10 * a, -60 - 40 * a
        c.rect(px - 10, py - 20, px + 14, py + 6, (240, 240, 240), w=2, r=4)
        c.arc(px + 16, py - 8, 7, 8, -90, 90, OUT, 2)
    # head
    hx, hy = 12 + sway, -134
    c.ellipse(hx, hy, 36, 32, grey, w=3)
    c.ellipse(hx + 14, hy + 12, 20, 13, light, ol=None)
    # baker's hat
    c.rect(hx - 26, hy - 34, hx + 26, hy - 22, (255, 255, 255), w=2.5, r=3)
    for dx in (-18, 0, 18):
        c.circle(hx + dx, hy - 44, 15, (255, 255, 255), w=2.5)
    c.rect(hx - 24, hy - 46, hx + 24, hy - 25, (255, 255, 255), ol=None)
    # eyes: kind and dark
    for ex in (hx - 4, hx + 18):
        ey = hy - 6
        if eyes == "closed":
            c.arc(ex, ey, 6, 4, 20, 160, OUT, 2.5)
        elif eyes == "happy":
            c.arc(ex, ey + 2, 6, 6, 200, 340, OUT, 2.5)
        else:
            c.ellipse(ex, ey, 6, 7, (30, 25, 30), ol=None)
            c.circle(ex + 2, ey - 3, 2, (255, 255, 255), ol=None)
    # little round glasses
    for ex in (hx - 4, hx + 18):
        c.circle(ex, hy - 6, 10, None, w=1.5)
    c.line([(hx + 6, hy - 7), (hx + 8, hy - 7)], OUT, 1.5)
    # nose, mouth, whiskers
    c.ellipse(hx + 16, hy + 6, 7, 5, (60, 50, 55), ol=None)
    if mouth > 0.05:
        c.ellipse(hx + 16, hy + 16 + 3 * mouth, 6, 2 + 5 * mouth, (120, 40, 50), w=1.5)
    else:
        c.arc(hx + 16, hy + 14, 7, 4, 20, 160, OUT, 2)
    for dy in (-3, 3):
        c.line([(hx + 26, hy + 10), (hx + 50, hy + 8 + dy * 2)], OUT, 1.2, cap=False)
        c.line([(hx + 4, hy + 10), (hx - 20, hy + 8 + dy * 2)], OUT, 1.2, cap=False)
    c.pop()


def rabbit_guard(c, x, y, s=1.0, face=1, t=0.0, hat=True, march=0.0, look=0.0, ears=0.0, seed=0.0, eyes="open"):
    """A Danish royal guard: a stern white rabbit, navy jacket, light-blue trousers, white crossbelts,
    tall black bearskin hat. ears: 0..1 springs the ears up when the hat is gone. ~190 tall at s=1."""
    c.push(x, y, s, flip=face < 0)
    navy, sky = (40, 52, 96), (120, 160, 210)
    for k, fx in enumerate((-10, 10)):
        sw = math.sin(march + k * math.pi) * 10 if march else 0
        lift = -max(0.0, math.cos(march + k * math.pi)) * 8 if march else 0
        c.stroke([(fx, -50), (fx + sw, -6 + lift)], sky, 13)
        c.line([(fx, -48), (fx + sw, -8 + lift)], (255, 255, 255), 2, cap=False)
        c.ellipse(fx + sw + 4, -3 + lift, 11, 5, (30, 30, 34), w=2)
    c.rect(-22, -110, 22, -48, navy, w=2.5, r=8)
    c.line([(-20, -106), (20, -54)], (250, 250, 250), 4)
    c.line([(20, -106), (-20, -54)], (250, 250, 250), 4)
    for k in range(3):
        c.circle(0, -96 + k * 16, 2, BRASS, ol=None)
    # arm with rifle shouldered
    c.stroke([(14, -104), (24, -78)], navy, 10)
    c.stroke([(26, -150), (26, -60)], (90, 70, 50), 5)
    c.ellipse(24, -76, 6, 5, (255, 255, 255), w=1.5)
    c.stroke([(-14, -104), (-20, -70)], navy, 10)
    c.ellipse(-20, -68, 6, 5, (255, 255, 255), w=1.5)
    # head
    hx, hy = 2 + look * 4, -128
    if not hat or ears > 0:
        e = ears if not hat else 0.0
        for ex, ang in ((-8, -0.15), (10, 0.15)):
            L = 20 + 30 * e
            c.ellipse(hx + ex + math.sin(ang) * L * 0.5, hy - 14 - L * 0.5, 7, L * 0.55 + 4, (250, 250, 250), w=2)
            c.ellipse(hx + ex + math.sin(ang) * L * 0.5, hy - 14 - L * 0.5, 3.5, L * 0.45, (250, 190, 200), ol=None)
    c.ellipse(hx, hy, 20, 18, (250, 250, 250), w=2.5)
    c.circle(hx + 15, hy + 4, 3, (240, 140, 160), ol=None)
    if eyes == "wide":
        c.circle(hx + 6, hy - 3, 4, (255, 255, 255), w=1.5)
        c.circle(hx + 6, hy - 3, 2, (30, 25, 30), ol=None)
    else:
        c.line([(hx + 1, hy - 3), (hx + 11, hy - 3)], OUT, 2.5)       # stern eye
    c.line([(hx + 2, hy - 9), (hx + 12, hy - 7)], OUT, 2)                # frown
    c.line([(hx + 10, hy + 9), (hx + 16, hy + 9)], OUT, 1.5)
    if hat:
        bearskin(c, hx - 2, hy - 8, 1.0)
    c.pop()


def bearskin(c, x, y, s=1.0):
    """Tall black bearskin hat; origin = its bottom centre."""
    c.push(x, y, s)
    c.ellipse(0, -36, 26, 40, (26, 24, 30), w=2.5)
    c.rect(-24, -38, 24, 0, (26, 24, 30), ol=None)
    c.line([(-24, -36), (-24, 0)], OUT, 2.5)
    c.line([(24, -36), (24, 0)], OUT, 2.5)
    for k in range(6):
        c.line([(-18 + k * 7, -60 + (k % 2) * 6), (-16 + k * 7, -48 + (k % 2) * 6)], (60, 58, 66), 1.5)
    c.line([(-22, -2), (22, -2)], BRASS, 2)
    c.pop()


# ------------------------------------------------------------------- food

def cinnamon_snail(c, x, y, r=34, unroll=0.0):
    """Kanelsnegl: a spiral bun seen from the top-front. unroll shrinks it."""
    rr = r * (1 - 0.8 * unroll)
    if rr < 3:
        return
    c.ellipse(x, y, rr, rr * 0.7, (214, 150, 80), w=2.5)
    pts = []
    for k in range(40):
        u = k / 39
        a = u * 3.2 * math.tau
        pts.append((x + math.cos(a) * rr * u * 0.9, y + math.sin(a) * rr * 0.7 * u * 0.9))
    c.line(pts, (150, 90, 40), 2.5)
    c.line([(x - rr * 0.6, y - rr * 0.3), (x + rr * 0.4, y + rr * 0.1)], (255, 250, 240), 2)


def pastry(c, x, y, s=1.0, kind=0):
    """Wienerbrød: kind 0 = round with jam centre, 1 = braid with icing, 2 = cinnamon snail."""
    c.push(x, y, s)
    if kind == 0:
        c.ellipse(0, 0, 20, 12, (226, 170, 90), w=2)
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            c.ellipse(math.cos(a) * 10, math.sin(a) * 6, 8, 5, (236, 186, 110), ol=None)
        c.ellipse(0, -1, 8, 5, (220, 60, 70), w=1.5)
    elif kind == 1:
        c.rect(-24, -8, 24, 8, (220, 160, 80), w=2, r=6)
        for k in range(4):
            c.line([(-18 + k * 12, -6), (-12 + k * 12, 6)], (190, 120, 60), 2)
        c.line([(-20, -2), (-8, 2), (4, -2), (16, 2)], (255, 255, 250), 2)
    else:
        cinnamon_snail(c, 0, 0, 16)
    c.pop()


def smorrebrod(c, x, y, s=1.0, lift=0.0):
    """Open sandwich on a plate: dark rye, egg slices, shrimps, cucumber and dill."""
    c.push(x, y, s)
    c.ellipse(0, 4, 50, 12, (250, 250, 250), w=2)
    c.push(0, -lift)
    c.rect(-34, -12, 34, 2, (90, 60, 44), w=2, r=3)
    for k, dx in enumerate((-22, -8, 6, 20)):
        c.ellipse(dx, -14, 8, 5, (255, 255, 250), w=1.5)
        c.circle(dx, -14, 3, (250, 200, 50), ol=None)
    for dx in (-16, 12):
        c.arc(dx, -20, 6, 5, 180, 360, (250, 150, 140), 4)
    c.line([(-30, -18), (-26, -24), (-22, -20)], (90, 160, 70), 2)
    c.line([(24, -20), (28, -26), (31, -20)], (90, 160, 70), 2)
    c.pop()
    c.pop()


def mug(c, x, y, s=1.0, col=(220, 80, 80), t=0.0, steam=True):
    c.push(x, y, s)
    c.rect(-14, -30, 14, 0, col, w=2.5, r=4)
    c.arc(16, -16, 8, 9, -90, 90, OUT, 3)
    c.ellipse(0, -30, 13, 4, (110, 60, 40), w=1.5)
    c.circle(-4, -32, 3, (255, 255, 255), ol=None)
    if steam:
        for k in range(2):
            u = (t * 0.5 + k * 0.5) % 1.0
            sx = -4 + k * 8
            pts = [(sx + 4 * math.sin(u * 6 + j), -36 - j * 6 - u * 10) for j in range(5)]
            c.line(pts, mix((255, 255, 255), (230, 200, 180), u), 2, cap=False)
    c.pop()


def candle(c, x, y, s=1.0, t=0.0, lit=True, col=(250, 246, 236)):
    c.push(x, y, s)
    c.ellipse(0, 0, 18, 5, (200, 170, 120), w=1.5)
    c.rect(-8, -40, 8, 0, col, w=2, r=2)
    c.line([(0, -40), (0, -46)], OUT, 1.5)
    if lit:
        f = 1 + 0.12 * math.sin(t * 13) + 0.08 * math.sin(t * 7.3)
        c.ellipse(0, -54, 8 * f, 12 * f, (255, 200, 80), ol=None)
        c.ellipse(0, -52, 4 * f, 7 * f, (255, 250, 210), ol=None)
    c.pop()


def blanket(c, x, y, w, h, col=(200, 60, 60), col2=(250, 220, 200)):
    """Plaid blanket draped as a soft lump; origin = bottom centre."""
    c.push(x, y)
    c.poly([(-w / 2, 0), (-w / 2 + 10, -h * 0.7), (-w * 0.2, -h), (w * 0.2, -h), (w / 2 - 10, -h * 0.7), (w / 2, 0)],
           col, w=2.5)
    for k in range(1, 4):
        xx = -w / 2 + k * w / 4
        c.line([(xx, -h * 0.85), (xx * 1.05, 0)], col2, 3, cap=False)
    for k in range(1, 3):
        yy = -h * k / 3
        c.line([(-w / 2 + 8, yy), (w / 2 - 8, yy)], col2, 3, cap=False)
    c.pop()


# -------------------------------------------------------------- buildings

def gable_house(c, x, base, w, h, col, kind=0, lit=0.0, rng=None, roof=None):
    """A tall narrow Nyhavn house: kind 0 stepped gable, 1 curved gable, 2 pitched roof facing the street."""
    trim = (250, 246, 236)
    roof = roof or (120, 66, 56)
    top = base - h
    c.rect(x, top, x + w, base, col, w=2.5)
    cx = x + w / 2
    if kind == 0:
        st = [(x, top), (x + w * 0.12, top), (x + w * 0.12, top - 18), (x + w * 0.28, top - 18), (x + w * 0.28, top - 36),
              (x + w * 0.42, top - 36), (x + w * 0.42, top - 52), (x + w * 0.58, top - 52), (x + w * 0.58, top - 36),
              (x + w * 0.72, top - 36), (x + w * 0.72, top - 18), (x + w * 0.88, top - 18), (x + w * 0.88, top),
              (x + w, top)]
        c.poly(st, col, w=2.5)
        c.rect(x + w * 0.42, top - 34, x + w * 0.58, top - 12, (250, 246, 236), w=1.5, r=4)
    elif kind == 1:
        pts = [(x, top)]
        for k in range(13):
            u = k / 12
            yy = top - 56 * math.sin(math.pi * u) ** 0.8 - 8 * math.sin(3 * math.pi * u)
            pts.append((x + w * u, yy))
        c.poly(pts, col, w=2.5)
        c.circle(cx, top - 26, 9, (250, 246, 236), w=1.5)
    else:
        c.poly([(x - 6, top + 2), (cx, top - 46), (x + w + 6, top + 2)], roof, w=2.5)
        c.rect(cx - 8, top - 26, cx + 8, top - 6, (250, 246, 236), w=1.5)
    # windows with white frames
    rows = int((h - 70) // 64)
    for r in range(rows):
        for k in range(2 if w < 110 else 3):
            n = 2 if w < 110 else 3
            wx = x + w * (k + 0.5) / n
            wy = top + 30 + r * 64
            on = lit > 0 and rng is not None and rng.random() < lit
            glass = (255, 214, 120) if on else (70, 96, 130)
            c.rect(wx - 11, wy, wx + 11, wy + 34, glass, ol=trim, w=3)
            c.line([(wx, wy), (wx, wy + 34)], trim, 2, cap=False)
            c.line([(wx - 11, wy + 15), (wx + 11, wy + 15)], trim, 2, cap=False)
    # ground floor: door and cellar café sign
    c.rect(cx - 12, base - 44, cx + 12, base, mix(col, OUT, 0.45), w=2, r=8)
    c.line([(x + 2, base - 52), (x + w - 2, base - 52)], mix(col, (255, 255, 255), 0.4), 3, cap=False)


def ship(c, x, y, s=1.0, t=0.0, hull=(40, 60, 90), stripe=(240, 230, 210), face=1, masts=2, flag=True,
         sails=False, seed=0.0):
    """Old wooden sailing ship moored in the canal; origin = waterline centre. ~300 long, masts ~260 tall."""
    bob = math.sin(t * 1.3 + seed) * 2
    c.push(x, y + bob, s, flip=face < 0)
    mast_x = [-60, 50] if masts == 2 else [0]
    for mx in mast_x:
        c.stroke([(mx, -40), (mx, -260 if mx < 0 else -230)], (120, 84, 54), 7)
        for yy in (-200, -150):
            c.line([(mx - 50, yy), (mx + 50, yy)], (120, 84, 54), 4)
        c.line([(mx, -250), (-150, -46)], (90, 70, 60), 1.2, cap=False)
        c.line([(mx, -250), (150, -46)], (90, 70, 60), 1.2, cap=False)
        if sails:
            c.poly([(mx - 46, -196), (mx + 46, -196), (mx + 52, -154), (mx - 52, -154)], (250, 244, 226), w=2)
    if flag:
        f = math.sin(t * 6 + seed) * 3
        mx = mast_x[0]
        top = -260 if mx < 0 else -230
        c.poly([(mx, top), (mx + 38, top + 4 + f), (mx + 36, top + 26 + f), (mx, top + 24)], DK_RED, w=1.5)
        c.line([(mx + 12, top + 2), (mx + 12 + f * 0.3, top + 25)], (255, 255, 255), 4, cap=False)
        c.line([(mx + 1, top + 13), (mx + 37, top + 15 + f)], (255, 255, 255), 4, cap=False)
    # bowsprit
    c.line([(140, -46), (200, -80)], (120, 84, 54), 5)
    c.line([(200, -80), (50, -230)], (90, 70, 60), 1.2, cap=False)
    # hull
    c.poly([(-150, -56), (150, -56), (172, -66), (130, 0), (-130, 0), (-160, -66)], hull, w=3)
    c.line([(-152, -42), (156, -42)], stripe, 5, cap=False)
    for k in range(6):
        c.circle(-100 + k * 40, -28, 5, mix(hull, (0, 0, 0), 0.3), w=1.5)
    c.rect(-150, -66, 150, -56, (150, 100, 60), w=2)
    c.pop()


def our_saviour_spire(c, x, base, s=1.0, col=(46, 44, 50), gold=BRASS, lw=2.5):
    """The Church of Our Saviour: brick tower with a black and gold corkscrew spire."""
    c.push(x, base, s)
    c.rect(-34, -200, 34, 0, (176, 108, 80), w=lw)
    c.rect(-38, -210, 38, -196, (150, 90, 70), w=lw)
    for k in range(3):
        c.rect(-12, -180 + k * 54, 12, -150 + k * 54, (60, 50, 60), w=1.5, r=8)
    c.poly([(-30, -210), (30, -210), (24, -250), (-24, -250)], col, w=lw)
    # corkscrew spire
    pts_l, pts_r = [], []
    H = 230
    for k in range(25):
        u = k / 24
        wdt = 22 * (1 - u) + 2
        yy = -250 - H * u
        pts_l.append((-wdt, yy))
        pts_r.append((wdt, yy))
    c.poly(pts_l + pts_r[::-1], col, w=lw)
    # the gold outside staircase spiralling round
    spiral = []
    for k in range(60):
        u = k / 59
        wdt = 22 * (1 - u) + 2
        a = u * 4 * math.tau
        spiral.append((math.sin(a) * (wdt + 7), -250 - H * u))
    for i in range(len(spiral) - 1):
        a = (i / 59) * 4 * math.tau
        if math.cos(a) > -0.3:
            c.line([spiral[i], spiral[i + 1]], gold, 6 * (1 - i / 75), cap=False)
    c.circle(0, -250 - H - 8, 7, gold, w=1.5)
    c.line([(0, -250 - H - 14), (0, -250 - H - 36)], col, 2)
    c.pop()


def copper_dome(c, x, base, s=1.0, wall=(214, 206, 190), lw=2.5):
    """A big green copper dome on columns (like the Marble Church)."""
    c.push(x, base, s)
    c.rect(-90, -90, 90, 0, wall, w=lw)
    for k in range(9):
        c.rect(-82 + k * 20, -84, -74 + k * 20, -6, mix(wall, (255, 255, 255), 0.4), w=1)
    c.rect(-96, -100, 96, -88, mix(wall, OUT, 0.15), w=lw)
    c.ellipse(0, -100, 86, 90, COPPER, w=lw)
    c.rect(-88, -100, 88, -96, mix(wall, OUT, 0.15), ol=None)
    for k in range(-3, 4):
        c.line([(k * 22, -100), (k * 8, -182)], COPPER_D, 2)
    c.rect(-16, -206, 16, -184, COPPER, w=lw)
    c.ellipse(0, -208, 18, 14, COPPER, w=lw)
    c.line([(0, -220), (0, -246)], BRASS, 3)
    c.circle(0, -248, 4, BRASS, ol=None)
    c.pop()


def town_tower(c, x, base, s=1.0, col=(196, 96, 72), lw=2.5):
    """Tall slim brick tower with a pointy copper top (like the City Hall tower)."""
    c.push(x, base, s)
    c.rect(-24, -260, 24, 0, col, w=lw)
    for k in range(5):
        c.rect(-8, -240 + k * 48, 8, -214 + k * 48, (70, 60, 70), w=1.2, r=6)
    c.rect(-28, -290, 28, -258, mix(col, (255, 255, 255), 0.2), w=lw)
    c.circle(0, -274, 10, (250, 246, 230), w=1.5)
    c.poly([(-28, -290), (0, -380), (28, -290)], COPPER, w=lw)
    c.line([(0, -380), (0, -400)], BRASS, 2)
    c.pop()


def dragon_spire(c, x, base, s=1.0, lw=2.0):
    """The old Stock Exchange's spire of four twisted dragon tails, on a long copper roof."""
    c.push(x, base, s)
    c.rect(-160, -60, 160, 0, (200, 110, 80), w=lw)
    c.poly([(-166, -60), (166, -60), (150, -90), (-150, -90)], COPPER, w=lw)
    c.poly([(-20, -90), (20, -90), (12, -120), (-12, -120)], COPPER, w=lw)
    pts = []
    for k in range(30):
        u = k / 29
        wdt = 12 * (1 - u) + 1
        pts.append((math.sin(u * 4 * math.tau) * wdt, -120 - 110 * u))
    c.line(pts, COPPER_D, 5)
    c.line([(-2, -120), (0, -232)], COPPER, 3)
    c.pop()


def skyline(c, x0, x1, base, rng, hmin, hmax, cols, win=None, p=0.0):
    x = x0
    while x < x1:
        w = rng.uniform(40, 90)
        h = rng.uniform(hmin, hmax)
        col = cols[rng.integers(len(cols))]
        c.rect(x, base - h, x + w, base, col, ol=None)
        if rng.random() < 0.5:
            c.poly([(x, base - h), (x + w / 2, base - h - w * 0.5), (x + w, base - h)], col, ol=None)
        if win:
            for wy in np.arange(base - h + 12, base - 10, 22):
                for wx in np.arange(x + 8, x + w - 10, 18):
                    if rng.random() < p:
                        c.rect(wx, wy, wx + 7, wy + 10, win, ol=None)
        x += w - 4


def amalienborg(c, x, base, s=1.0, lit=False):
    """One of the four rococo Amalienborg palaces: long pale facade, columns, copper roof, crown."""
    c.push(x, base, s)
    wall = (226, 214, 196)
    c.rect(-300, -200, 300, 0, wall, w=2.5)
    c.poly([(-310, -200), (310, -200), (290, -250), (-290, -250)], (90, 90, 96), w=2.5)
    # central pavilion
    c.rect(-90, -230, 90, 0, mix(wall, (255, 255, 255), 0.25), w=2.5)
    c.poly([(-100, -230), (0, -280), (100, -230)], mix(wall, (255, 255, 255), 0.25), w=2.5)
    c.circle(0, -250, 14, (240, 230, 210), w=1.5)
    for k in range(4):
        cx = -66 + k * 44
        c.rect(cx - 8, -224, cx + 8, -40, (246, 240, 228), w=1.5)
    c.poly([(-30, -300), (-36, -320), (-18, -310), (0, -326), (18, -310), (36, -320), (30, -300)], BRASS, w=1.5)
    c.rect(-30, -300, 30, -290, BRASS, w=1.5)
    for side in (-1, 1):
        for k in range(4):
            wx = side * (130 + k * 46)
            for wy in (-170, -100):
                glass = (255, 214, 130) if lit else (90, 110, 140)
                c.rect(wx - 12, wy, wx + 12, wy + 40, glass, ol=(250, 246, 236), w=2.5)
            c.rect(wx - 12, -40, wx + 12, 0, mix(wall, OUT, 0.3), w=1.5, r=8) if k == 3 else None
    c.rect(-24, -60, 24, 0, (110, 80, 60), w=2, r=12)
    c.pop()


def sentry_box(c, x, base, s=1.0):
    """Sentry box: little wooden hut with a peaked roof and a crown."""
    c.push(x, base, s)
    c.rect(-34, -150, 34, 0, (60, 80, 120), w=2.5)
    c.rect(-26, -136, 26, 0, (30, 40, 70), w=2)
    c.poly([(-42, -148), (0, -186), (42, -148)], (60, 80, 120), w=2.5)
    c.circle(0, -164, 8, BRASS, w=1.5)
    for k in range(4):
        c.line([(-34, -120 + k * 30), (-26, -120 + k * 30)], (230, 230, 240), 2, cap=False)
    c.pop()


def horse_statue(c, x, base, s=1.0, col=(100, 160, 140)):
    """Equestrian statue on a tall pedestal (the king in the middle of the palace square)."""
    c.push(x, base, s)
    c.rect(-56, -150, 56, 0, (200, 196, 190), w=2.5)
    c.rect(-66, -162, 66, -146, (220, 216, 210), w=2.5)
    c.rect(-62, -12, 62, 0, (220, 216, 210), w=2.5)
    sh = mix(col, OUT, 0.25)
    # far legs, tail, body, near legs, neck and head
    c.stroke([(-30, -196), (-36, -164)], sh, 9)
    c.stroke([(30, -196), (40, -166)], sh, 9)
    c.stroke([(-46, -206), (-62, -176), (-58, -166)], col, 9)
    c.ellipse(0, -204, 52, 22, col, w=2.5)
    c.stroke([(-22, -196), (-26, -164)], col, 10)
    c.stroke([(22, -196), (28, -180), (20, -164)], col, 10)
    c.stroke([(38, -212), (56, -246)], col, 18)
    c.poly([(48, -258), (80, -244), (82, -234), (54, -236)], col, w=2.5)
    c.poly([(48, -258), (54, -270), (58, -256)], col, w=2)
    c.line([(30, -214), (48, -252)], sh, 4)
    # the rider, in a long cloak and a laurel wreath
    c.poly([(-14, -226), (14, -226), (10, -270), (-8, -270)], col, w=2.5)
    c.poly([(-10, -226), (-30, -206), (-6, -212)], sh, w=2)
    c.stroke([(8, -258), (30, -248)], col, 7)
    c.circle(2, -282, 11, col, w=2.5)
    c.arc(2, -284, 12, 8, 180, 360, (200, 190, 100), 2)
    c.pop()


def mermaid(c, x, base, s=1.0, col=(96, 150, 128), shade=(70, 120, 104)):
    """The Little Mermaid statue on her rock (bronze gone green). Origin = rock top-centre."""
    c.push(x, base, s)
    # rock
    c.poly([(-140, 40), (-120, -10), (-70, -34), (10, -40), (80, -30), (130, 0), (150, 40)], (120, 116, 110), w=3)
    for (a, b) in (((-90, -20), (-60, 10)), ((30, -30), (70, 0)), ((-20, -10), (10, 20))):
        c.line([a, b], (96, 92, 88), 2)
    # tail curled to the side, fins near the rock edge
    c.poly([(-20, -40), (40, -44), (86, -36), (110, -46), (122, -64), (104, -58), (96, -40), (60, -30), (0, -30)],
           shade, w=2.5)
    c.poly([(108, -48), (130, -70), (118, -76), (102, -58)], shade, w=2)
    c.ellipse(4, -48, 40, 18, col, w=2.5)
    # body, sitting, leaning forward
    c.poly([(-26, -50), (-18, -112), (8, -120), (14, -86), (16, -50)], col, w=2.5)
    # arm resting on knee
    c.stroke([(-6, -108), (20, -86), (36, -60)], col, 8)
    # head bowed, long hair
    c.ellipse(-4, -132, 14, 16, col, w=2.5)
    c.poly([(-16, -140), (-22, -110), (-30, -96), (-14, -104), (-6, -122)], shade, w=2)
    c.arc(4, -128, 4, 3, 20, 160, OUT, 1.5)
    c.pop()


def lantern_string(c, x0, y0, x1, y1, sag, n, t=0.0, lit=1.0, seed=0, r=7):
    pts = [(lerp(x0, x1, u), lerp(y0, y1, u) + sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 24)]
    c.line(pts, (40, 36, 46), 1.5, cap=False)
    for k in range(n):
        u = (k + 0.5) / n
        px, py = lerp(x0, x1, u), lerp(y0, y1, u) + sag * 4 * u * (1 - u)
        col = LANTERN_COLS[(k + seed) % len(LANTERN_COLS)]
        on = clamp(lit * (n + 4) - k)
        if on > 0:
            c.circle(px, py + r + 2, r * 2.0, mix((40, 30, 70), col, 0.3 * on), ol=None)
        c.circle(px, py + r + 2, r, mix((70, 60, 80), col, 0.25 + 0.75 * on), w=1.2)
        if on > 0:
            c.circle(px - 2, py + r, r * 0.35, mix(col, (255, 255, 255), 0.7), ol=None)


def carousel(c, x, base, s=1.0, t=0.0, lit=1.0):
    """Tivoli carousel: striped canopy, gold poles, horses going up and down."""
    c.push(x, base, s)
    c.ellipse(0, 0, 170, 26, (180, 60, 70), w=2.5)
    c.rect(-170, -14, 170, 0, (180, 60, 70), ol=None)
    c.ellipse(0, -14, 170, 26, (220, 90, 90), w=2.5)
    c.rect(-12, -230, 12, -14, BRASS, w=2)
    ang = t * 1.2
    order = []
    for k in range(6):
        a = ang + k * math.tau / 6
        order.append((math.sin(a), a, k))
    order.sort()
    for depth, a, k in order:
        px = math.cos(a) * 140
        py = -14 + depth * 14
        hy = -120 + 20 * math.sin(t * 3 + k)
        sc = 0.8 + 0.2 * (depth + 1) / 2
        c.line([(px, -230), (px, py)], BRASS, 3 * sc)
        cols = [(255, 255, 255), (250, 210, 120), (200, 230, 255)]
        hc = cols[k % 3]
        fc = 1 if math.sin(a) > 0 else -1
        c.push(px, py + hy, sc, flip=fc < 0)
        c.ellipse(0, 0, 30, 14, hc, w=2)
        c.stroke([(22, -6), (34, -26)], hc, 10)
        c.ellipse(40, -28, 12, 7, hc, w=2)
        c.stroke([(-16, 8), (-26, 26)], hc, 5)
        c.stroke([(16, 8), (28, 22)], hc, 5)
        c.poly([(-30, -4), (-44, 4), (-30, 6)], (220, 160, 80), w=1.5)
        c.rect(-6, -14, 8, -8, (220, 60, 80), w=1)
        c.pop()
    # canopy
    stripes = [(240, 80, 80), (255, 240, 220)]
    for k in range(12):
        x0 = -190 + k * (380 / 12)
        x1 = x0 + 380 / 12
        c.poly([(x0, -230), (x1, -230), (lerp(x1, 0, 0.92), -310), (lerp(x0, 0, 0.92), -310)],
               stripes[k % 2], w=1.5)
    for k in range(12):
        x0 = -190 + k * (380 / 12)
        c.poly([(x0, -230), (x0 + 380 / 12, -230), (x0 + 380 / 24, -212)], stripes[(k + 1) % 2], w=1.5)
    c.poly([(-16, -310), (0, -350), (16, -310)], BRASS, w=2)
    c.circle(0, -356, 7, (240, 80, 80), w=1.5)
    for k in range(13):
        bx = -190 + k * (380 / 12)
        on = (math.sin(t * 4 + k) > -0.3) * lit
        c.circle(bx, -232, 4, mix((120, 100, 80), (255, 240, 170), on), ol=None)
    c.pop()


# The wooden roller coaster's track: (x, y) points in screen space, start at the station.
COASTER = [(120, 610), (300, 610), (420, 560), (560, 360), (700, 220), (790, 168), (860, 176), (930, 300),
           (1010, 470), (1080, 520), (1150, 430), (1200, 360), (1250, 380), (1300, 470), (1320, 560),
           (1260, 610), (1000, 620), (700, 622), (400, 618), (120, 610)]


def coaster_point(u):
    """Position and slope angle along the coaster track, u in 0..1 (station to station)."""
    pts = COASTER
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    d = clamp(u) * total
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L:
            k = d / max(1e-6, L)
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k)), math.atan2(b[1] - a[1], b[0] - a[0])
        d -= L
    return pts[-1], 0.0


def coaster_track(c, lit=1.0):
    """Wooden trestle and rails for the first, visible part of COASTER (up to the big hill and dip)."""
    pts = COASTER[:15]
    wood, wood_d = (176, 128, 84), (126, 88, 58)
    # trestle legs
    xs = np.linspace(330, 1310, 30)
    for xx in xs:
        # find track height at xx along the upper run
        yy = None
        for a, b in zip(pts, pts[1:]):
            if a[0] <= xx <= b[0]:
                yy = lerp(a[1], b[1], (xx - a[0]) / max(1e-6, b[0] - a[0]))
                break
        if yy is None:
            continue
        c.line([(xx, yy + 6), (xx, 640)], wood_d, 4, cap=False)
    tops = []
    for xx in xs:
        yy = 640
        for a, b in zip(pts, pts[1:]):
            if a[0] <= xx <= b[0]:
                yy = lerp(a[1], b[1], (xx - a[0]) / max(1e-6, b[0] - a[0]))
                break
        tops.append(yy)
    for k in range(len(xs) - 1):
        for yy in range(640, 140, -60):
            if yy - 60 > max(tops[k], tops[k + 1]) + 8:
                c.line([(xs[k], yy), (xs[k + 1], yy - 60)], mix(wood_d, (40, 30, 60), 0.3), 1.5, cap=False)
    # rails
    c.line(pts, OUT, 12)
    c.line(pts, wood, 8)
    c.line([(x, y - 3) for x, y in pts], (230, 200, 150), 2)
    if lit > 0:
        for k in range(len(pts) - 1):
            for j in range(4):
                u = j / 4
                lx, ly = lerp(pts[k][0], pts[k + 1][0], u), lerp(pts[k][1], pts[k + 1][1], u)
                c.circle(lx, ly + 10, 3, mix((120, 100, 80), (255, 236, 160), lit), ol=None)


def coaster_car(c, x, y, ang, s=1.0, col=(220, 60, 60)):
    """A little open car; drawn rotated by the slope angle around (x, y) on the rail."""
    pts = [(-46, -6), (46, -6), (40, -34), (-40, -34)]
    ca, sa = math.cos(ang), math.sin(ang)

    def r(p):
        return (x + (p[0] * ca - p[1] * sa) * s, y + (p[0] * sa + p[1] * ca) * s)
    c.poly([r(p) for p in pts], col, w=2.5)
    c.line([r((-40, -28)), r((40, -28))], BRASS, 3)
    for wx in (-28, 28):
        cx, cy = r((wx, -4))
        c.circle(cx, cy, 7 * s, (60, 56, 60), w=2)


def mountain_facade(c, x, base, s=1.0, lit=1.0):
    """The painted rocky 'mountain' that the old wooden coaster runs through."""
    c.push(x, base, s)
    rock, rock_d = (130, 120, 140), (100, 94, 116)
    c.poly([(-260, 0), (-200, -170), (-120, -240), (-40, -200), (40, -300), (120, -230), (200, -260), (280, 0)],
           rock, w=3)
    for (a, b) in (((-180, -120), (-120, -60)), ((20, -240), (70, -150)), ((150, -200), (200, -120)),
                   ((-80, -150), (-30, -90))):
        c.line([a, b], rock_d, 3)
    c.poly([(30, -300), (40, -300), (60, -266), (12, -266)], (240, 240, 250), ol=None)
    c.ellipse(-60, -40, 70, 60, (40, 32, 50), w=3)                       # tunnel
    c.rect(-130, -40, 10, 0, (40, 32, 50), ol=None)
    c.pop()


def firework(c, x, y, t, t0, col, r=90, dur=1.6):
    if t < t0 or t > t0 + dur + 0.6:
        return
    u = t - t0
    if u < 0.6:
        k = u / 0.6
        c.circle(x, lerp(y + 300, y, ease(k)), 3, (255, 240, 200), ol=None)
        return
    k = clamp((u - 0.6) / dur)
    rr = r * ease(min(1, k * 1.6))
    fade = 1 - k
    for j in range(16):
        a = j * math.tau / 16
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr + 30 * k * k
        cc = mix((30, 26, 60), col, fade)
        c.line([(x + math.cos(a) * rr * 0.55, y + math.sin(a) * rr * 0.55 + 30 * k * k), (px, py)], cc, 3, cap=False)
        c.circle(px, py, 4 * fade + 1, mix((30, 26, 60), (255, 255, 230), fade), ol=None)


def bakery_boat(c, x, y, s=1.0, t=0.0):
    """Bodil's bakery boat: wooden hull, striped awning, a counter. Origin = waterline centre."""
    bob = math.sin(t * 1.2) * 2
    c.push(x, y + bob, s)
    c.poly([(-230, -70), (230, -70), (250, -84), (200, 0), (-200, 0), (-246, -84)], (60, 120, 110), w=3)
    c.line([(-236, -52), (236, -52)], (250, 220, 120), 5, cap=False)
    c.text(0, -30, "BAGERI", 26, (255, 246, 220), stroke=2)
    c.rect(-230, -84, 230, -70, (150, 100, 60), w=2)
    # awning posts and awning
    for px in (-200, 200):
        c.line([(px, -84), (px, -300)], (120, 84, 54), 6)
    cols = [(220, 60, 70), (255, 246, 230)]
    for k in range(10):
        x0 = -220 + k * 44
        c.poly([(x0, -300), (x0 + 44, -300), (x0 + 44, -270), (x0, -270)], cols[k % 2], w=1.5)
        c.poly([(x0, -270), (x0 + 44, -270), (x0 + 22, -254)], cols[k % 2], w=1.5)
    c.pop()


def counter(c, x, y, s=1.0):
    """Counter front of the bakery boat (drawn over Bodil). Origin = counter top centre."""
    c.push(x, y, s)
    c.rect(-200, 0, 200, 70, (196, 140, 90), w=3)
    for k in range(5):
        c.line([(-200 + k * 80 + 40, 6), (-200 + k * 80 + 40, 66)], (160, 108, 66), 2, cap=False)
    c.rect(-210, -8, 210, 4, (230, 210, 180), w=2.5, r=3)
    c.pop()
