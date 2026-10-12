"""Drawing helpers for the Rome film: Roman landmarks, locals and props.

Everything is drawn with draw.Canvas primitives in the same flat outlined
style as draw.py. Local space: origin at the base/feet, facing right, y up
is negative. Note Canvas.text does not scale with push(), so text sizes are
multiplied by the scale by hand.
"""
import math

import numpy as np

import draw as D
from draw import OUT, mix

STONE = (238, 224, 196)
STONE_D = (214, 196, 164)
STONE_L = (248, 240, 220)
TRAVERTINE = (228, 200, 158)
TRAV_D = (196, 160, 116)
TRAV_SH = (150, 108, 76)
PINE = (62, 112, 72)
PINE_D = (46, 90, 60)
CYPRESS = (44, 92, 62)
GOLD = (250, 200, 60)
DOUGH = (246, 226, 182)
SAUCE = (214, 60, 46)
CHEESE = (255, 228, 140)
CRUST = (222, 160, 80)

ROSA = dict(body=(248, 246, 240), dark=(222, 214, 206), belly=(255, 255, 255),
            ear=(250, 176, 186), eye=(96, 186, 120), stripes=False, collar=None)


def _text(c, x, y, s, size, *a, **kw):
    if size >= 4:
        c.text(x, y, s, size, *a, **kw)


# --------------------------------------------------------------- plants

def umbrella_pine(c, x, y, s=1.0, lean=0.0, col=PINE, ol=OUT):
    """The flat-topped Roman stone pine."""
    c.push(x, y, s)
    top = -250
    c.stroke([(0, 0), (6 + lean * 0.3, -90), (lean, top + 20)], (130, 100, 80), 12, ol=ol)
    c.stroke([(lean * 0.6 + 2, -170), (lean * 0.6 + 40, -215)], (130, 100, 80), 7, ol=ol)
    c.stroke([(lean * 0.6 + 2, -150), (lean * 0.6 - 44, -205)], (130, 100, 80), 7, ol=ol)
    for dx, dy, rx, ry in ((lean - 70, top - 4, 70, 30), (lean + 70, top - 2, 74, 30), (lean, top - 26, 92, 34),
                           (lean - 10, top + 6, 110, 26)):
        c.ellipse(dx, dy, rx, ry, col, ol=ol)
    for dx, dy, rx, ry in ((lean - 70, top - 4, 64, 25), (lean + 70, top - 2, 68, 25), (lean, top - 26, 86, 29),
                           (lean - 10, top + 6, 104, 21)):
        c.ellipse(dx, dy, rx, ry, col, ol=None)
    c.ellipse(lean - 20, top - 36, 50, 12, mix(col, (255, 255, 220), 0.15), ol=None)
    c.pop()


def cypress(c, x, y, s=1.0, col=CYPRESS, ol=OUT):
    c.push(x, y, s)
    c.rect(-5, -20, 5, 0, (110, 80, 60), ol=ol, w=2)
    c.poly([(0, -230), (18, -170), (24, -90), (18, -30), (0, -14), (-18, -30), (-24, -90), (-18, -170)], col,
           ol=ol)
    c.line([(4, -200), (10, -120), (6, -50)], mix(col, (255, 255, 255), 0.15), 3, cap=False)
    c.pop()


def olive(c, x, y, s=1.0):
    c.push(x, y, s)
    c.stroke([(0, 0), (-6, -40), (4, -70)], (120, 100, 80), 9)
    for dx, dy, r in ((-30, -80, 28), (20, -86, 30), (-4, -104, 30), (34, -70, 22)):
        c.circle(dx, dy, r, (128, 150, 104))
    for dx, dy, r in ((-30, -80, 23), (20, -86, 25), (-4, -104, 25), (34, -70, 17)):
        c.circle(dx, dy, r, (138, 162, 112), ol=None)
    c.pop()


# ---------------------------------------------------------------- locals

def pigeon(c, x, y, s=1.0, face=1, t=0.0, walk=0.0, mouth=0.0, fly=False, eyes="open", cap=True,
           body=(150, 160, 182), seed=3.0):
    """Nico the Roman pigeon (with his little flat cap)."""
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    dark = mix(body, (40, 40, 60), 0.3)
    light = mix(body, (255, 255, 255), 0.3)
    c.push(x, y, s, flip=face < 0)
    bob = math.sin(walk) * 3 if walk else 0.0
    if fly:
        c.push(0, -10, 1.0)
        flap = math.sin(t * 22)
        # far wing
        c.poly([(-4, -34), (-30 + 4 * flap, -34 - 46 * flap), (-6, -26)], dark, w=2.5)
    else:
        # feet
        for fx, ph in ((-5, 0), (7, math.pi)):
            lift = -max(0.0, math.cos(walk + ph)) * 5 if walk else 0
            fxx = fx + (math.sin(walk + ph) * 5 if walk else 0)
            c.line([(fx * 0.6, -10), (fxx, lift)], (230, 110, 90), 3)
            c.line([(fxx - 4, lift), (fxx + 6, lift)], (230, 110, 90), 3)
    c.poly([(-18, -32), (-46, -26), (-44, -16), (-14, -20)], dark, w=2.5)            # tail
    c.ellipse(0, -26, 25, 18, body, w=2.5)                                             # body
    c.ellipse(6, -20, 15, 9, light, ol=None)
    if not fly:
        c.ellipse(-6, -29, 17, 10, light, w=2)                                         # folded wing
        for k in (0, 1):
            c.line([(-14 + k * 8, -24), (-6 + k * 8, -33)], dark, 2.5, cap=False)
    hx, hy = 18 + bob, -54
    c.ellipse(13 + bob * 0.5, -40, 12, 14, (96, 168, 150), w=2.5)                     # shiny neck
    c.ellipse(15 + bob * 0.5, -36, 8, 7, (160, 110, 180), ol=None)
    c.circle(hx, hy, 12, body, w=2.5)
    # beak (opens when talking)
    c.poly([(hx + 9, hy - 2), (hx + 22, hy + 1), (hx + 9, hy + 3)], (70, 62, 70), w=1.5)
    if mouth > 0.05:
        c.poly([(hx + 9, hy + 3), (hx + 19, hy + 3 + 6 * mouth), (hx + 8, hy + 6)], (70, 62, 70), w=1.5)
    c.circle(hx + 10, hy - 3, 2.6, (240, 236, 230), ol=None)
    if eyes == "closed":
        c.arc(hx + 3, hy - 3, 3.5, 2.5, 20, 160, OUT, 2)
    elif eyes == "happy":
        c.arc(hx + 3, hy, 3.5, 3.5, 200, 340, OUT, 2)
    else:
        big = 1.3 if eyes == "wide" else 1.0
        c.circle(hx + 3, hy - 3, 4.2 * big, (250, 150, 60), w=1.5)
        c.circle(hx + 3.5, hy - 3, 2.2 * big, (20, 20, 20), ol=None)
    if cap:
        c.ellipse(hx - 1, hy - 10, 13, 6, (128, 92, 66), w=2)
        c.poly([(hx + 4, hy - 12), (hx + 20, hy - 9), (hx + 6, hy - 6)], (110, 78, 56), w=2)
    if fly:
        c.poly([(-2, -36), (-26 - 4 * flap, -36 - 52 * flap), (6 - 2 * flap, -34 - 40 * flap), (8, -28)], light,
               w=2.5)
        c.pop()
    c.pop()


def head_pos(pose, head_dy=0.0):
    """Where draw.cat puts the head centre (local space) for a pose."""
    if pose == "sit":
        return 18, -106 + head_dy
    if pose == "crouch":
        return 52, -64 + head_dy
    if pose == "leap":
        return 58, -74
    if pose == "sleep":
        return 46, -40
    return 52, -86 + head_dy


def rosa(c, x, y, s=1.0, face=1, pose="sit", t=0.0, mouth=0.0, eyes="open", look=(0, 0), head_dy=0.0, **kw):
    """Rosa: a round white Roman cat with a chef's hat and a red neckerchief."""
    D.cat(c, x, y, ROSA, s, face, pose, t=t, mouth=mouth, eyes=eyes, look=look, head_dy=head_dy, seed=4.2, **kw)
    hx, hy = head_pos(pose, head_dy)
    c.push(x, y, s, flip=face < 0)
    c.poly([(hx - 18, hy + 24), (hx + 24, hy + 24), (hx + 4, hy + 44)], (210, 50, 50), w=2)
    c.circle(hx + 3, hy + 25, 5, (190, 40, 40), w=2)
    c.rect(hx - 24, hy - 34, hx + 26, hy - 22, (255, 255, 255), w=2.5, r=3)
    for dx, dy, r in ((-14, -50, 17), (14, -50, 17), (0, -60, 19)):
        c.circle(hx + dx, hy + dy, r, (255, 255, 255), w=2.5)
    for dx, dy, r in ((-14, -50, 14), (14, -50, 14), (0, -60, 16)):
        c.circle(hx + dx, hy + dy, r, (255, 255, 255), ol=None)
    c.rect(hx - 22, hy - 36, hx + 24, hy - 24, (255, 255, 255), ol=None)
    c.pop()


def collar_coin(c, x, y, s, face, pose, head_dy=0.0, dx=0.0, dy=0.0):
    """Pip's lucky coin hanging on Luna's collar (next to her bell)."""
    hx, hy = head_pos(pose, head_dy)
    c.push(x, y, s, flip=face < 0)
    coin(c, hx - 8 + dx, hy + 38 + dy, 6.5)
    c.pop()


def collar_point(x, y, s, face, pose, head_dy=0.0):
    hx, hy = head_pos(pose, head_dy)
    return x + face * s * (hx - 8), y + s * (hy + 38)


def coin(c, x, y, r=7, spin=1.0):
    rx = max(1.2, r * abs(spin))
    c.ellipse(x, y, rx, r, GOLD, w=2)
    if abs(spin) > 0.4:
        c.ellipse(x, y, rx * 0.6, r * 0.6, (255, 226, 120), ol=None)
        c.circle(x - rx * 0.3, y - r * 0.35, r * 0.18, (255, 255, 230), ol=None)


def twinkle(c, x, y, r, col=(255, 250, 200)):
    c.poly([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r),
            (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], col, ol=None)


def dough_hat(c, x, y, s, face, pose, t, k=1.0):
    """Pizza dough draped over a cat's head (k: 0..1 how far it has slid on)."""
    hx, hy = head_pos(pose)
    c.push(x, y, s, flip=face < 0)
    yy = hy - 30 + 18 * k
    c.ellipse(hx + 2, yy, 50, 22, DOUGH, w=2.5)
    for dx, ln in ((-40, 22), (-18, 30), (30, 26), (44, 16)):
        c.stroke([(hx + dx, yy + 8), (hx + dx * 1.02, yy + 8 + ln * k)], DOUGH, 9, ol=OUT)
    for dx, dy, r in ((-16, -6, 7), (12, -10, 6), (22, 2, 5), (-2, 4, 5)):
        c.circle(hx + dx, yy + dy, r, SAUCE, ol=None)
    c.circle(hx + 4, yy - 4, 4, (90, 150, 70), ol=None)
    c.pop()


# ----------------------------------------------------------------- food

def pizza(c, x, y, r=40, raw=False, eaten=0.0, persp=0.38):
    """Whole pizza seen from a low angle (ellipse). eaten removes slices."""
    ry = r * persp
    if eaten >= 0.99:
        return
    if eaten <= 0.01:
        c.ellipse(x, y, r, ry, DOUGH if raw else CRUST, w=2.5)
        c.ellipse(x, y - 1, r * 0.84, ry * 0.8, SAUCE if raw else CHEESE, ol=None)
        if not raw:
            for k in range(6):
                a = k * 1.05 + 0.3
                c.ellipse(x + math.cos(a) * r * 0.5, y + math.sin(a) * ry * 0.5, r * 0.11, ry * 0.15, SAUCE,
                          ol=None)
            c.ellipse(x - r * 0.2, y - ry * 0.2, r * 0.1, ry * 0.12, (90, 150, 70), ol=None)
        else:
            for k in range(4):
                a = k * 1.6 + 0.6
                c.ellipse(x + math.cos(a) * r * 0.45, y + math.sin(a) * ry * 0.4, r * 0.14, ry * 0.18,
                          (255, 255, 245), ol=None)
        return
    # partly eaten: a pie with a wedge missing
    a0 = 360 * eaten
    box = c._box(x, y, r, ry)
    c.d.pieslice(box, a0 - 90, 270, fill=c.c(CRUST), outline=c.c(OUT), width=c._w(2.5))
    box2 = c._box(x, y - 1, r * 0.84, ry * 0.8)
    c.d.pieslice(box2, a0 - 90 + 4, 266, fill=c.c(CHEESE))


def slice_(c, x, y, s=1.0, ang=0.0, bitten=0.0):
    """A pizza slice held point-first (ang in degrees, 0 = point right)."""
    c.push(x, y, s)
    L = 46 * (1 - 0.7 * bitten)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)
    c.poly([R(L, 0), R(-10, -22), R(-16, -12), R(-16, 12), R(-10, 22)], CHEESE, w=2.5)
    c.stroke([R(-12, -20), R(-17, 0), R(-12, 20)], CRUST, 8, ol=OUT)
    for px, py in ((L * 0.35, 0), (L * 0.05, -9), (L * 0.05, 10)):
        if px < L - 6:
            cx_, cy_ = R(px, py)
            c.circle(cx_, cy_, 4.5, SAUCE, ol=None)
    c.pop()


def gelato(c, x, y, s=1.0, cols=((250, 180, 200), (190, 235, 170))):
    c.push(x, y, s)
    c.poly([(-11, -20), (11, -20), (0, 14)], (226, 170, 100), w=2)
    c.line([(-6, -12), (4, 2)], (190, 130, 70), 1.5, cap=False)
    c.circle(-5, -26, 11, cols[0], w=2)
    c.circle(6, -34, 11, cols[1], w=2)
    c.pop()


# ------------------------------------------------------------- vehicles

def vespa(c, x, y, s=1.0, face=1, t=0.0, col=(150, 214, 192), rider=True, wheel=0.0):
    """Scooter facing right, ridden by a dog in sunglasses."""
    c.push(x, y, s, flip=face < 0)
    for wx in (-58, 62):
        c.circle(wx, -22, 22, (50, 46, 52))
        c.circle(wx, -22, 10, (190, 190, 200), w=2)
        for k in range(3):
            a = wheel + k * 2.09
            c.line([(wx, -22), (wx + 8 * math.cos(a), -22 + 8 * math.sin(a))], (120, 120, 130), 2, cap=False)
    if rider:
        # dog rider (behind the leg shield)
        c.stroke([(-10, -78), (26, -54)], (150, 110, 80), 14)                 # leg
        c.ellipse(-22, -110, 26, 34, (176, 130, 92), w=2.5)                   # torso
        c.stroke([(-10, -122), (40, -116)], (176, 130, 92), 11)               # arm to handlebar
        c.ellipse(-12, -160, 24, 22, (176, 130, 92), w=2.5)                   # head
        c.ellipse(10, -152, 18, 12, (200, 160, 120), w=2.5)                   # snout
        c.circle(26, -156, 5, (40, 34, 38), ol=None)
        c.ellipse(-28, -150, 9, 20, (120, 84, 60), w=2)                       # ear
        c.ellipse(-12, -174, 26, 14, (230, 60, 60), w=2.5)                    # helmet
        c.rect(-12, -168, 16, -158, (30, 30, 40), r=3, w=1.5)                 # sunglasses
        c.arc(10, -146, 8, 5, 20, 120, OUT, 2)
    c.poly([(-90, -40), (-84, -70), (-50, -84), (-10, -80), (-10, -40)], col)  # rear cowl
    c.rect(-60, -42, 30, -32, mix(col, (0, 0, 0), 0.25), w=2)                   # floor board
    c.poly([(26, -36), (34, -100), (48, -104), (54, -40), (82, -30), (40, -30)], col)  # leg shield/front
    c.ellipse(-46, -86, 34, 8, (110, 70, 50), w=2.5)                            # seat
    c.line([(46, -104), (50, -122)], (90, 90, 100), 4)
    c.line([(38, -124), (60, -120)], (70, 70, 80), 5)
    c.circle(60, -110, 8, (255, 245, 190), w=2)                                 # headlight
    c.rect(-94, -66, -86, -56, (230, 70, 60), w=1.5)                            # tail light
    c.pop()


def steam_train(c, x, y, s, t, wheel, cats_fn=None, win=(60, 80, 120)):
    """Little red steam train facing right; x is the locomotive's front buffer.

    cats_fn(c) draws the passengers in the first carriage window (called in train space).
    """
    c.push(x, y, s)
    red, red_d, cream, green = (204, 54, 50), (160, 36, 40), (246, 230, 190), (70, 120, 90)
    # carriages (two), coupled behind the locomotive
    for k, cx0 in enumerate((-1240, -760)):
        c.rect(cx0, -184, cx0 + 440, -36, green, r=8)
        c.rect(cx0, -96, cx0 + 440, -82, cream, ol=None)
        c.poly([(cx0 - 10, -184), (cx0 + 450, -184), (cx0 + 430, -206), (cx0 + 10, -206)], (90, 80, 86))
        _text(c, cx0 + 220, -60, "ROMA", 18 * c.scale, cream)
        for wx in range(cx0 + 30, cx0 + 420, 100):
            c.rect(wx, -166, wx + 80, -108, win, r=6, w=2.5)
            c.line([(wx + 12, -158), (wx + 26, -118)], (110, 140, 180), 3, cap=False)
        for wx in (cx0 + 70, cx0 + 370):
            _wheel(c, wx, -22, 22, wheel)
        c.rect(cx0 + 440, -66, cx0 + 480, -56, (60, 60, 64), w=2)            # coupling
    # locomotive
    L = -320
    c.rect(L, -220, L + 120, -40, red_d, r=6)                                  # cab
    c.rect(L - 6, -232, L + 130, -216, (70, 60, 66), r=4)                      # cab roof
    c.rect(L + 20, -196, L + 96, -140, (250, 220, 140), r=6, w=2.5)            # cab window
    c.circle(L + 300, -120, 76, red)                                           # boiler front (round)
    c.rect(L + 110, -196, L + 300, -44, red, ol=None)
    c.line([(L + 110, -196), (L + 300, -196)], OUT, 3, cap=False)
    c.line([(L + 110, -44), (L + 300, -44)], OUT, 3, cap=False)
    c.circle(L + 300, -120, 60, (220, 80, 70), ol=None)
    c.circle(L + 320, -120, 22, (250, 225, 120), w=2.5)                        # lamp
    for bx in (L + 160, L + 220):
        c.rect(bx - 4, -200, bx + 4, -40, (230, 190, 90), ol=None)            # brass bands
    c.rect(L + 220, -290, L + 260, -196, (60, 56, 64))                         # chimney
    c.rect(L + 210, -300, L + 270, -284, (60, 56, 64), r=4)
    c.ellipse(L + 170, -206, 22, 16, (230, 190, 90))                           # dome
    c.rect(L - 10, -50, L + 380, -30, (60, 56, 64), r=3)                       # frame
    c.poly([(L + 370, -34), (L + 410, -6), (L + 370, -6)], (60, 56, 64))       # cow catcher
    for wx, r in ((L + 40, 26), (L + 140, 34), (L + 240, 34), (L + 330, 22)):
        _wheel(c, wx, -6 - r + 8, r, wheel * 26 / r)
    a = wheel * 26 / 34
    c.line([(L + 140 + 18 * math.cos(a), -32 + 18 * math.sin(a)), (L + 240 + 18 * math.cos(a), -32 + 18 * math.sin(a))],
           (200, 200, 210), 6)
    if cats_fn:
        cats_fn(c)
    c.pop()


def _wheel(c, x, y, r, a):
    c.circle(x, y, r, (60, 56, 64))
    c.circle(x, y, r * 0.7, (130, 50, 50), ol=None)
    for k in range(4):
        aa = a + k * math.pi / 4
        c.line([(x - r * 0.7 * math.cos(aa), y - r * 0.7 * math.sin(aa)),
                (x + r * 0.7 * math.cos(aa), y + r * 0.7 * math.sin(aa))], (60, 56, 64), 3, cap=False)
    c.circle(x, y, r * 0.2, (200, 200, 210), w=2)


def smoke(c, x, y, t, speed, n=7, col=(240, 240, 245)):
    """Puffs drifting back from a chimney at (x, y)."""
    for k in range(n):
        u = ((t * 0.9 + k / n) % 1.0)
        px = x - u * (120 + 260 * speed) + 10 * math.sin(k * 3)
        py = y - 30 - u * 120
        r = 14 + u * 40
        c.circle(px, py, r, mix(col, (200, 210, 230), u), ol=mix(col, (150, 150, 170), 0.6), w=2)


# ------------------------------------------------------------ landmarks

def colosseum(c, x, y, s=1.0, rng_seed=1):
    """The Colosseum, side view: outer wall intact on the left, broken on the right."""
    c.push(x, y, s)
    hw = 470
    tiers = [(-90, 0), (-180, -90), (-270, -180)]
    attic = (-350, -270)
    # profile of the broken outer wall (x -> top y), right part stepped down
    prof = [(-hw, -350), (130, -350), (150, -338), (168, -316), (200, -312), (226, -276), (262, -270),
            (290, -226), (330, -214), (352, -180), (400, -176), (420, -140), (hw, -136)]

    def top_at(px):
        for (x0, y0), (x1, y1) in zip(prof, prof[1:]):
            if x0 <= px <= x1:
                return y0 + (y1 - y0) * (px - x0) / max(1e-6, x1 - x0)
        return prof[-1][1]
    # inner ring seen through the broken part (darker, set back)
    c.poly([(60, -300), (hw - 20, -300), (hw - 20, -60), (60, -60)], TRAV_D)
    for ty0, ty1 in ((-300, -210), (-210, -130)):
        for ax in range(90, hw - 40, 50):
            c.rect(ax, ty0 + 22, ax + 26, ty1 - 6, TRAV_SH, ol=None, r=12)
        c.line([(60, ty1), (hw - 20, ty1)], mix(TRAV_D, (0, 0, 0), 0.2), 3, cap=False)
    # outer wall
    pts = [(-hw, 0)] + prof + [(hw, 0)]
    c.poly(pts, TRAVERTINE)
    spacing = 58
    for (ty0, ty1) in tiers:
        for k in range(-8, 9):
            ax = k * spacing
            if ax - 20 < -hw + 6 or ax + 20 > hw - 6:
                continue
            if top_at(ax - 22) > ty1 - 64 or top_at(ax + 22) > ty1 - 64:
                continue
            # arch opening: dark below, sky-ish showing through in the upper tiers
            col = TRAV_SH if ty1 == 0 else mix(TRAV_SH, (150, 170, 200), 0.25 if ty1 < -150 else 0.0)
            c.rect(ax - 18, ty0 + 20, ax + 18, ty1 - 4, col, ol=mix(TRAV_D, OUT, 0.4), w=2, r=17)
            # half columns between arches
            c.rect(ax + spacing / 2 - 6, ty0 + 6, ax + spacing / 2 + 6, ty1, mix(TRAVERTINE, (255, 255, 255), 0.18),
                   ol=None)
        # cornice
        xr = hw
        while xr > -hw and top_at(xr) > ty0 + 2:
            xr -= 4
        c.rect(-hw, ty0 - 2, xr, ty0 + 8, mix(TRAVERTINE, (255, 255, 255), 0.3), ol=mix(TRAV_D, OUT, 0.4), w=2)
    # attic with small square windows (only the intact part)
    for k in range(-8, 3):
        ax = k * spacing
        if ax - 10 > -hw + 10 and top_at(ax + 12) < attic[1] - 30:
            c.rect(ax - 9, -322, ax + 9, -302, TRAV_SH, ol=None, r=2)
    c.rect(-hw, -356, 132, -346, mix(TRAVERTINE, (255, 255, 255), 0.3), ol=mix(TRAV_D, OUT, 0.4), w=2)
    # weathering blotches
    rng = np.random.default_rng(rng_seed)
    for _ in range(40):
        px = rng.uniform(-hw + 20, hw - 20)
        py = rng.uniform(top_at(px) + 15, -10)
        c.ellipse(px, py, rng.uniform(6, 18), rng.uniform(3, 7), mix(TRAVERTINE, TRAV_D, 0.5), ol=None)
    c.poly(pts, None)
    c.pop()


def trevi_static(c, cx, gy, s=1.0):
    """The Trevi Fountain (stone parts). Water is drawn live by trevi_water."""
    c.push(cx, gy, s)
    # palace block with wings
    c.rect(-640, -540, 640, -60, STONE)
    c.rect(-646, -556, 646, -536, STONE_D)
    for wx0 in (-610, 290):
        for row, wy in enumerate((-500, -380, -250)):
            for col in range(3):
                x0 = wx0 + col * 112
                c.rect(x0, wy, x0 + 44, wy + 76, (96, 104, 128), ol=mix(STONE_D, OUT, 0.5), w=2)
                c.line([(x0 + 22, wy), (x0 + 22, wy + 76)], STONE_D, 2, cap=False)
                if row < 2:
                    c.poly([(x0 - 8, wy - 4), (x0 + 22, wy - 22), (x0 + 52, wy - 4)], STONE_L,
                           ol=mix(STONE_D, OUT, 0.5), w=2)
                c.rect(x0 - 6, wy + 76, x0 + 50, wy + 84, STONE_L, ol=mix(STONE_D, OUT, 0.5), w=2)
        for px in (wx0 - 16, wx0 + 312):
            c.rect(px, -536, px + 16, -60, STONE_L, ol=None)
    # central triumphal arch section
    c.rect(-270, -580, 270, -60, STONE_L)
    c.rect(-280, -592, 280, -572, STONE_D)
    c.rect(-150, -560, 150, -514, mix(STONE_L, STONE_D, 0.4), ol=mix(STONE_D, OUT, 0.5), w=2)
    _text(c, 0, -537, "AQVA VIRGO", 22 * c.scale, (150, 130, 100))
    for k, sx in enumerate((-215, -75, 75, 215)):                 # statues on the attic
        c.ellipse(sx, -604, 10, 10, (245, 245, 238), w=2)
        c.poly([(sx - 10, -594), (sx + 10, -594), (sx + 13, -570), (sx - 13, -570)], (245, 245, 238), w=2)
    c.poly([(-120, -592), (0, -628), (120, -592)], STONE_D)        # crest
    c.ellipse(0, -604, 26, 14, (245, 245, 238), w=2)
    for colx in (-225, -150, 150, 225):                           # big columns
        c.rect(colx - 17, -500, colx + 17, -150, STONE, ol=mix(STONE_D, OUT, 0.5), w=2)
        for fl in (-8, 0, 8):
            c.line([(colx + fl, -490), (colx + fl, -160)], STONE_D, 1.5, cap=False)
        c.rect(colx - 24, -512, colx + 24, -496, STONE_D, ol=mix(STONE_D, OUT, 0.5), w=2)
        c.rect(colx - 22, -152, colx + 22, -140, STONE_D, ol=mix(STONE_D, OUT, 0.5), w=2)
    c.rect(-280, -514, 280, -500, STONE_D, ol=mix(STONE_D, OUT, 0.5), w=2)
    for nx in (-188, 188):                                        # side niches + statues
        c.rect(nx - 20, -330, nx + 20, -200, (206, 192, 166), ol=mix(STONE_D, OUT, 0.5), w=2, r=20)
        c.circle(nx, -300, 8, (250, 250, 244), w=2)
        c.poly([(nx - 9, -292), (nx + 9, -292), (nx + 12, -214), (nx - 12, -214)], (250, 250, 244), w=2)
        c.rect(nx - 26, -460, nx + 26, -370, mix(STONE_L, STONE_D, 0.3), ol=mix(STONE_D, OUT, 0.5), w=2)
    # big central niche with Oceanus
    c.rect(-100, -470, 100, -150, (204, 188, 160), ol=mix(STONE_D, OUT, 0.5), w=3, r=100)
    for k in range(4):
        c.arc(0, -370, 80 - k * 16, 80 - k * 16, 180, 360, mix((204, 188, 160), STONE_D, 0.6), 2)
    marble = (252, 250, 245)
    c.ellipse(0, -330, 16, 16, marble, w=2)                       # head
    c.ellipse(4, -318, 12, 9, (230, 230, 225), ol=None)            # beard
    c.poly([(-26, -310), (26, -310), (34, -240), (14, -200), (-14, -200), (-34, -240)], marble, w=2)
    c.stroke([(24, -300), (52, -330), (60, -350)], marble, 10)     # raised arm
    c.poly([(-20, -250), (30, -260), (24, -220), (-26, -215)], (234, 228, 214), w=2)   # drapery
    c.ellipse(0, -196, 56, 16, marble, w=2)                        # shell chariot
    # rocks (scogliera)
    rng = np.random.default_rng(7)
    for _ in range(46):
        rx = rng.uniform(-360, 360)
        top = -60 - 150 * max(0.0, 1 - abs(rx) / 380) - rng.uniform(0, 30)
        ry = rng.uniform(top, -50)
        c.ellipse(rx, ry, rng.uniform(26, 54), rng.uniform(16, 30),
                  mix((206, 200, 184), (170, 166, 150), rng.uniform(0, 1)), ol=mix((150, 146, 130), OUT, 0.3), w=2)
    # sea horses: two simple rearing marble horses
    for hx, f in ((-150, -1), (150, 1)):
        c.push(hx, -130, 1.0, flip=f < 0)
        c.ellipse(0, 0, 32, 18, marble, w=2)
        c.poly([(18, -8), (40, -48), (56, -46), (34, -2)], marble, w=2)
        c.ellipse(52, -50, 14, 9, marble, w=2)
        c.stroke([(28, 10), (46, -10)], marble, 7)
        c.stroke([(-24, 4), (-50, 18), (-60, 6)], marble, 8)
        c.pop()
    # basin
    c.rect(-700, -70, 700, -6, (70, 190, 200), ol=None)
    c.pop()


def trevi_water(c, cx, gy, s, t, night=0.0):
    """Animated cascades, shimmering pool and the front rim of the basin."""
    c.push(cx, gy, s)
    wcol = mix((175, 238, 240), (120, 170, 210), night)
    for k, (wx, w_, top) in enumerate(((-110, 34, -170), (0, 46, -186), (110, 34, -170), (-250, 24, -110),
                                       (250, 24, -110))):
        c.rect(wx - w_, top, wx + w_, -40, mix(wcol, (255, 255, 255), 0.2), ol=None, r=8)
        for j in range(4):
            u = (t * 1.4 + j / 4 + k * 0.13) % 1.0
            yy = top + (-40 - top) * u
            c.line([(wx - w_ * 0.7 + j * w_ * 0.45, yy), (wx - w_ * 0.7 + j * w_ * 0.45, yy + 16)],
                   (255, 255, 255), 3, cap=False)
        c.ellipse(wx, -44, w_ + 22, 10, (250, 255, 255), ol=None)
    pool = mix((64, 186, 198), (40, 90, 140), night)
    c.rect(-700, -48, 700, -6, pool, ol=None)
    rng = np.random.default_rng(3)
    for k in range(26):
        px = rng.uniform(-660, 660)
        py = rng.uniform(-44, -12)
        a = 0.5 + 0.5 * math.sin(t * 2.2 + k)
        c.ellipse(px + 6 * math.sin(t + k), py, 14 + 10 * a, 2.2, mix(pool, (230, 255, 255), 0.4 + 0.4 * a), ol=None)
    # front rim of the basin
    c.rect(-720, -14, 720, 16, (226, 214, 190), w=3)
    c.rect(-720, -14, 720, -6, (240, 232, 212), ol=None)
    c.pop()


def building(c, x0, w, h, gy, col, rng, shop=None, shutters=(80, 128, 92)):
    """A Roman street facade from x0 to x0+w, standing on gy."""
    top = gy - h
    c.rect(x0, top, x0 + w, gy, col)
    c.rect(x0 - 6, top - 14, x0 + w + 6, top + 4, mix(col, (0, 0, 0), 0.2))           # cornice
    c.rect(x0 - 2, top - 24, x0 + w + 2, top - 14, (190, 96, 66), w=2)                  # roof tiles edge
    # plaster patches
    for _ in range(int(w / 70)):
        c.ellipse(x0 + rng.uniform(20, w - 20), rng.uniform(top + 20, gy - 40), rng.uniform(14, 30),
                  rng.uniform(8, 16), mix(col, (255, 255, 255), 0.12), ol=None)
    ncol = max(1, int((w - 30) // 90))
    pad = (w - ncol * 90) / 2
    rows = []
    y = top + 40
    while y + 90 < gy - 150:
        rows.append(y)
        y += 115
    for r, wy in enumerate(rows):
        for k in range(ncol):
            wx = x0 + pad + k * 90 + 24
            c.rect(wx, wy, wx + 42, wy + 72, (70, 62, 70), w=2.5)
            c.rect(wx - 16, wy, wx, wy + 72, shutters, w=2)
            c.rect(wx + 42, wy, wx + 58, wy + 72, shutters, w=2)
            for yy in range(int(wy) + 10, int(wy) + 72, 10):
                c.line([(wx - 14, yy), (wx - 2, yy)], mix(shutters, (0, 0, 0), 0.3), 1.5, cap=False)
                c.line([(wx + 44, yy), (wx + 56, yy)], mix(shutters, (0, 0, 0), 0.3), 1.5, cap=False)
            c.rect(wx - 6, wy - 8, wx + 48, wy, mix(col, (255, 255, 255), 0.35), w=2)
            if rng.random() < 0.55:                                                       # flower box
                c.rect(wx - 4, wy + 72, wx + 46, wy + 84, (150, 90, 60), w=2)
                for fx in range(int(wx), int(wx) + 44, 9):
                    c.circle(fx + 3, wy + 70, 6, (70, 140, 70), ol=None)
                    c.circle(fx + 4, wy + 66, 4, [(230, 50, 60), (250, 120, 160), (255, 255, 255)][rng.integers(3)],
                             ol=None)
            elif rng.random() < 0.4:                                                      # little balcony
                c.rect(wx - 10, wy + 72, wx + 52, wy + 78, (60, 56, 64), w=1.5)
                for bx in range(int(wx) - 8, int(wx) + 52, 8):
                    c.line([(bx, wy + 50), (bx, wy + 72)], (60, 56, 64), 2, cap=False)
                c.line([(wx - 10, wy + 50), (wx + 52, wy + 50)], (60, 56, 64), 3, cap=False)
    # ground floor
    c.rect(x0, gy - 120, x0 + w, gy, mix(col, (0, 0, 0), 0.08), ol=None)
    c.line([(x0, gy - 120), (x0 + w, gy - 120)], mix(col, (0, 0, 0), 0.3), 3, cap=False)
    dx = x0 + w * 0.22
    c.rect(dx - 26, gy - 104, dx + 26, gy, (120, 76, 52), w=2.5, r=24)                  # arched door
    c.line([(dx, gy - 100), (dx, gy)], (90, 56, 40), 2, cap=False)
    c.circle(dx + 12, gy - 46, 3, GOLD, ol=None)
    if shop:
        name, awn = shop
        sx0, sx1 = x0 + w * 0.42, x0 + w - 18
        c.rect(sx0, gy - 96, sx1, gy - 6, (120, 150, 170), w=2.5)
        c.rect(sx0 + 10, gy - 80, sx1 - 10, gy - 20, (170, 205, 220), ol=None)
        c.rect(sx0 - 4, gy - 136, sx1 + 4, gy - 108, (60, 56, 64), w=2)
        _text(c, (sx0 + sx1) / 2, gy - 122, name, 18 * c.scale, (255, 236, 180))
        n = 6
        for k in range(n):                                                              # striped awning
            a = sx0 - 10 + (sx1 - sx0 + 20) * k / n
            b = sx0 - 10 + (sx1 - sx0 + 20) * (k + 1) / n
            c.poly([(a, gy - 106), (b, gy - 106), (b + 6, gy - 82), (a + 6, gy - 82)],
                   awn if k % 2 == 0 else (255, 250, 240), ol=None)
        c.poly([(sx0 - 10, gy - 106), (sx1 + 10, gy - 106), (sx1 + 16, gy - 82), (sx0 - 4, gy - 82)], None)
    return top


def cobbles(c, x0, x1, y0, y1, base=(170, 160, 150), rng_seed=4):
    """Sampietrini: little square paving stones."""
    c.rect(x0, y0, x1, y1, base, ol=None)
    rng = np.random.default_rng(rng_seed)
    row = 0
    y = y0 + 4
    while y < y1:
        sz = 10 + (y - y0) * 0.12
        x = x0 - (sz * 0.5 if row % 2 else 0)
        while x < x1:
            c.rect(x + 1, y, x + sz - 2, y + sz * 0.55, mix(base, (255, 255, 255), rng.uniform(0.05, 0.22)),
                   ol=None, r=2)
            x += sz
        y += sz * 0.55 + 2
        row += 1


def postcard(c, cx, cy, s, t=0.0):
    """The postcard: the Trevi Fountain under a blue sky, 'Saluti da ROMA'."""
    c.push(cx, cy, s)
    c.rect(-160, -110, 160, 110, (255, 252, 240), w=3, r=6)
    sky = (120, 196, 245)
    c.rect(-146, -96, 146, 70, sky, ol=None)
    c.circle(110, -70, 16, (255, 226, 100), ol=None)
    D.cloud(c, -90, -70, 0.4)
    c.push(0, 48, 0.21)
    trevi_static(c, 0, 0, 1.0)
    trevi_water(c, 0, 0, 1.0, t)
    c.pop()
    c.rect(-146, 52, 146, 70, (226, 214, 190), ol=None)
    c.rect(-146, -96, 146, 70, None, w=2)
    _text(c, 0, 90, "Saluti da ROMA", 22 * c.scale, (200, 60, 60))
    c.pop()
