"""Vienna props and new characters for "Whiskers and the Two Left Paws".

Flat outlined style with draw.Canvas primitives. Characters are drawn in
local space: origin between the feet, facing right, y up is negative.
Buildings: origin at the middle of their base.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import draw as D
from draw import Canvas, W, H, SS, OUT, ease, lerp, clamp, mix

GOLD = (236, 190, 70)
GOLD_D = (190, 140, 40)
CREAM = (246, 234, 206)
STONE = (226, 214, 188)
STONE_D = (186, 170, 140)
COPPER = (110, 176, 150)
COPPER_D = (80, 138, 116)
SCHON = (244, 196, 72)          # Schonbrunn yellow
SCHON_D = (214, 160, 50)
CHOC = (74, 40, 30)
CHOC_D = (50, 26, 20)
CHOC_L = (110, 64, 44)
CREAM_W = (255, 252, 244)
RED = (200, 40, 50)

# palettes for extra cats (same keys as draw.WHISKERS / draw.LUNA)
MITZI = dict(body=(250, 236, 214), dark=(214, 140, 70), belly=(255, 250, 240),
             ear=(255, 170, 170), eye=(120, 180, 90), stripes=False, collar=None)
COUNTESS = dict(body=(252, 250, 246), dark=(222, 218, 214), belly=(255, 255, 255),
                ear=(255, 190, 200), eye=(130, 110, 220), stripes=False, collar=(246, 244, 240))
GUESTS = [
    dict(body=(70, 66, 74), dark=(46, 42, 50), belly=(220, 216, 220), ear=(240, 170, 180), eye=(230, 200, 70),
         stripes=False, collar=None),
    dict(body=(220, 170, 110), dark=(180, 126, 70), belly=(250, 232, 200), ear=(250, 170, 160), eye=(110, 170, 80),
         stripes=True, collar=None),
    dict(body=(236, 236, 240), dark=(190, 190, 200), belly=(255, 255, 255), ear=(250, 180, 190), eye=(80, 150, 220),
         stripes=False, collar=None),
    dict(body=(150, 110, 80), dark=(110, 76, 52), belly=(230, 210, 180), ear=(240, 160, 150), eye=(200, 170, 60),
         stripes=True, collar=None),
    dict(body=(120, 124, 140), dark=(90, 92, 110), belly=(220, 220, 230), ear=(240, 170, 190), eye=(120, 200, 140),
         stripes=False, collar=None),
    dict(body=(240, 200, 150), dark=(210, 160, 100), belly=(255, 240, 220), ear=(250, 170, 170), eye=(90, 160, 220),
         stripes=False, collar=None),
]
GOWNS = [(220, 90, 130), (120, 170, 230), (250, 210, 110), (170, 120, 210), (120, 200, 170), (240, 150, 110)]


# ================================================================ helpers

def shade_bottom(c, tl, t, strength=0.5, top=540, _masks={}):
    """Darken the bottom of the frame softly while a subtitle shows."""
    k = 0.0
    for dt in (0.0, -0.25, 0.25):
        if tl.line_at(t + dt) is not None:
            k += 1 / 3
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    key = (q, top)
    if key not in _masks:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.3 * (q / 20) * 255
        _masks[key] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((18, 14, 26), (0, top * SS, W * SS, H * SS), _masks[key])


def masked(c, pts, draw_fn):
    """Draw draw_fn(canvas) clipped to polygon pts (local coords of c)."""
    tmp = Canvas(c.img.copy())
    tmp.tf = list(c.tf)
    draw_fn(tmp)
    mask = Image.new("L", c.img.size, 0)
    ImageDraw.Draw(mask).polygon([c.P(x, y) for x, y in pts], fill=255)
    c.img.paste(tmp.img, (0, 0), mask)


def arch_window(c, x, y, w, h, fill, frame=None, ww=2.5, pointed=False):
    """Window with a round (or pointed) top; (x, y) = bottom centre."""
    fr = frame or OUT
    if pointed:
        pts = [(x - w / 2, y), (x - w / 2, y - h + w * 0.6), (x, y - h), (x + w / 2, y - h + w * 0.6), (x + w / 2, y)]
        c.poly(pts, fill, ol=fr, w=ww)
    else:
        c.rect(x - w / 2, y - h + w / 2, x + w / 2, y, fill, ol=None)
        c.ellipse(x, y - h + w / 2, w / 2, w / 2, fill, ol=None)
        c.arc(x, y - h + w / 2, w / 2, w / 2, 180, 360, fr, ww)
        c.line([(x - w / 2, y - h + w / 2), (x - w / 2, y), (x + w / 2, y), (x + w / 2, y - h + w / 2)], fr, ww)


# ================================================================ characters

HORSE = dict(body=(246, 244, 240), shade=(214, 212, 214), mane=(196, 198, 206), mane_d=(160, 162, 174),
             muzzle=(220, 196, 196), hoof=(110, 100, 100))


def horse(c, x, y, s=1.0, face=1, t=0.0, mouth=0.0, walk=0.0, eyes="open", prance=0.0, bow=0.0, hat=True,
          harness=True, seed=6.0, head_dy=0.0, rear=0.0):
    """Ferdinand, the old white Lipizzaner. walk: leg phase. prance: 0..1 high-stepping dance.
    bow: 0..1 elegant bow (head down, one foreleg forward). rear: 0..1 up on the hind legs."""
    m = HORSE
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    c.push(x, y, s, flip=face < 0)
    # rearing: rotate-ish by lifting the front
    leg_len = 118
    by = -leg_len - 40
    lift_front = 46 * rear

    def leg(lx, phase, col, front):
        top = (lx, by + 18 - (lift_front if front else 0) * (1 if lx > 0 else 0.8))
        if front and bow > 0 and lx > 0:
            foot = (lx + 46 * bow, -2)
            knee = (lx + 30 * bow, by + 74)
        elif prance > 0:
            up = max(0.0, math.sin(walk + phase))
            knee = (lx + 18 * up * (1 if front else -0.4), by + 60 - 26 * up * prance)
            foot = (lx + (8 if front else -6) * up, -46 * up * prance)
        elif walk:
            sw = math.sin(walk + phase)
            knee = (lx + sw * 10, by + 64)
            foot = (lx + sw * 22, -max(0.0, math.cos(walk + phase)) * 12)
        else:
            knee = (lx, by + 64)
            foot = (lx, 0)
        if front and rear > 0:
            knee = (lx + 30 * rear, top[1] + 36)
            foot = (lx + 22 * rear, top[1] + 64 - 10 * rear)
        c.stroke([top, knee, foot], col, 17)
        c.rect(foot[0] - 9, foot[1] - 12, foot[0] + 11, foot[1], m["hoof"], w=2, r=2)

    sh = m["shade"]
    leg(-62, math.pi, sh, False)
    leg(66, 0, sh, True)
    # tail (long, flowing)
    tw = math.sin(t * 2.4 + seed) * 0.4
    pts = [(-92 - 26 * u + 8 * math.sin(u * 4 + t * 3) * u, by - 22 + 120 * u ** 1.2 + 10 * tw * u)
           for u in np.linspace(0, 1, 8)]
    c.stroke(pts, m["mane"], 18)
    c.line([(p[0] + 4, p[1]) for p in pts[2:]], m["mane_d"], 3)
    # body
    c.push(0, by, 1.0)
    ang = -0.32 * rear
    def R(px, py):
        return (px * math.cos(ang) - py * math.sin(ang), px * math.sin(ang) + py * math.cos(ang))
    body_pts = [R(110 * math.cos(a), 52 * math.sin(a)) for a in np.linspace(0, math.tau, 40)]
    c.poly(body_pts, m["body"], w=3)
    c.poly([R(px, py) for px, py in ((-60, 30), (60, 30), (80, 40), (-70, 42))], mix(m["body"], sh, 0.4), ol=None)
    # dapple spots (old greys keep a few)
    for dx, dy, r in ((-50, -10, 7), (-20, 14, 5), (10, -18, 6), (-74, 12, 5)):
        px, py = R(dx, dy)
        c.circle(px, py, r, mix(m["body"], sh, 0.5), ol=None)
    if harness:
        a, b = R(56, -50), R(64, 40)
        c.line([a, b], (150, 40, 40), 9)
        c.line([a, b], (210, 70, 60), 5)
        mid = R(60, -4)
        c.circle(mid[0], mid[1], 6, GOLD, w=2)
    c.pop()
    leg(-40, 0, m["body"], False)
    leg(88, math.pi, m["body"], True)
    # neck + head
    nod = math.sin(walk * 2) * 3 if walk else 0
    hx, hy = 150 + 20 * rear, by - 92 + nod + head_dy + 54 * bow - 60 * rear
    neck_base = R(80, -30)
    nb = (neck_base[0], by + neck_base[1])
    c.poly([(nb[0] - 34, nb[1] - 20), (hx - 26, hy - 18), (hx + 6, hy + 16), (nb[0] + 30, nb[1] + 40)], m["body"],
           ol=None)
    c.line([(nb[0] - 34, nb[1] - 20), (hx - 26, hy - 18)], OUT, 3)
    c.line([(hx + 6, hy + 18), (nb[0] + 30, nb[1] + 40)], OUT, 3)
    # mane along the neck
    for k in range(6):
        u = k / 5
        mx, my = lerp(nb[0] - 38, hx - 30, u), lerp(nb[1] - 18, hy - 22, u)
        c.ellipse(mx - 6, my + 4, 15, 12, m["mane"], w=2)
    # head: long face
    c.push(hx, hy, 1.0)
    ha = 0.5 + 0.5 * bow
    def Hh(px, py):
        return (px * math.cos(ha) - py * math.sin(ha), px * math.sin(ha) + py * math.cos(ha))
    # ears
    c.poly([Hh(-14, -26), Hh(-8, -58), Hh(4, -26)], m["body"], w=2.5)
    c.poly([Hh(-10, -30), Hh(-7, -50), Hh(0, -30)], m["muzzle"], ol=None)
    head = [Hh(px, py) for px, py in ((-28, -16), (-6, -32), (30, -20), (78, -10), (92, 6), (86, 22), (60, 26),
                                       (10, 24), (-24, 14))]
    c.poly(head, m["body"], w=3)
    mz = Hh(78, 8)
    c.ellipse(mz[0], mz[1], 20, 18, m["muzzle"], ol=None)
    nos = Hh(86, 0)
    c.ellipse(nos[0], nos[1], 4, 5, (120, 90, 96), ol=None)
    if mouth > 0.05:
        mp = Hh(70, 22)
        c.ellipse(mp[0], mp[1] + 3 * mouth, 12, 3 + 7 * mouth, D.MOUTH, w=2)
    else:
        a, b = Hh(58, 20), Hh(80, 20)
        c.line([a, b], OUT, 2.5)
    # forelock
    fl = Hh(-6, -30)
    for dx in (-6, 4, 12):
        c.ellipse(fl[0] + dx, fl[1] + 4, 9, 13, m["mane"], w=2)
    # eye
    e = Hh(12, -6)
    if eyes == "closed":
        c.arc(e[0], e[1], 7, 5, 20, 160, OUT, 3)
    elif eyes == "happy":
        c.arc(e[0], e[1] + 3, 7, 7, 200, 340, OUT, 3)
    else:
        big = 1.2 if eyes == "wide" else 1.0
        c.ellipse(e[0], e[1], 7 * big, 9 * big, (255, 255, 255), w=2.5)
        c.ellipse(e[0] + 2, e[1] + 1, 4.5 * big, 6 * big, (70, 50, 40), ol=None)
        c.circle(e[0] + 3, e[1] - 2, 1.7, (255, 255, 255), ol=None)
        c.arc(e[0], e[1] - 6, 10, 6, 200, 330, OUT, 2)
    if harness:
        a, b = Hh(-10, 18), Hh(56, -18)
        c.line([a, b], (150, 40, 40), 4)
        a2 = Hh(30, 24)
        c.line([Hh(30, -26), a2], (150, 40, 40), 4)
        c.circle(Hh(30, -2)[0], Hh(30, -2)[1], 4, GOLD, w=1.5)
    if hat:
        hp = Hh(-6, -36)
        c.push(hp[0], hp[1], 1.0)
        c.ellipse(0, 2, 24, 6, (40, 36, 40), w=2)
        c.rect(-15, -22, 15, 2, (40, 36, 40), w=2, r=8)
        c.rect(-15, -6, 15, 0, (150, 40, 40), ol=None)
        c.pop()
    c.pop()
    c.pop()


def dancer(c, x, y, s=1.0, face=1, pal=None, t=0.0, mouth=0.0, eyes="open", look=(0.0, 0.0), step=0.0,
           arm=0.6, arm2=None, gown=None, bowtie=None, tiara=False, seed=0.0, lean=0.0, legs_up=0.0, hop=0.0):
    """A cat standing up on its hind legs, ready to waltz.

    step: leg phase.  arm: 0 down .. 1 reaching forward (to a partner).  gown: dress colour.
    bowtie: bow colour.  lean: lean forward (+) / back (-) in output px at the head.
    """
    pal = pal or D.WHISKERS
    if eyes == "open" and D.blink(t, seed):
        eyes = "closed"
    body, dark, belly = pal["body"], pal["dark"], pal["belly"]
    c.push(x, y - hop, s, flip=face < 0)
    sw = math.sin(step)
    # tail
    tw = math.sin(t * 2.5 + seed)
    pts = [(-20 - 34 * u, -58 + 30 * u - 40 * u * u + 8 * tw * u) for u in np.linspace(0, 1, 8)]
    c.stroke(pts, body, 11)
    # legs
    for k, (lx, ph, col) in enumerate(((-10, math.pi, dark), (12, 0, body))):
        s2 = math.sin(step + ph)
        foot = (lx + 12 * s2 + 6, -max(0.0, math.cos(step + ph)) * 8 * (1 if step else 0) - legs_up * 20 * (k == 0))
        c.stroke([(lx, -40), foot], col, 13)
        c.ellipse(foot[0] + 5, foot[1] - 2, 10, 5.5, col)
    # back arm
    a2 = arm if arm2 is None else arm2
    sh = (8 + lean * 0.5, -98)
    hand2 = (sh[0] + lerp(-4, 34, a2), sh[1] + lerp(46, -6, a2))
    c.stroke([sh, hand2], dark, 11)
    c.circle(hand2[0], hand2[1], 6.5, dark)
    # body
    c.poly([(-26, -40), (-22 + lean * 0.3, -110), (30 + lean * 0.4, -112), (28, -40)], body, ol=None)
    c.ellipse(0, -52, 30, 26, body)
    c.ellipse(4 + lean * 0.35, -96, 28, 30, body)
    c.poly([(-27, -50), (-24 + lean * 0.3, -96), (30 + lean * 0.4, -98), (29, -50)], body, ol=None)
    c.ellipse(10 + lean * 0.3, -80, 15, 26, belly, ol=None)
    if pal.get("stripes"):
        for dy in (-90, -72, -56):
            c.line([(-24, dy), (-12, dy + 5)], dark, 5)
    if gown:
        hem = 4 * math.sin(t * 5 + seed)
        gd = mix(gown, (0, 0, 0), 0.18)
        c.poly([(-22, -84), (26, -84), (44 + hem, -6), (-46 + hem, -6)], gown, w=2.5)
        c.poly([(-40 + hem, -14), (40 + hem, -14), (44 + hem, -6), (-46 + hem, -6)], gd, ol=None)
        for fx in (-20, 0, 20):
            c.line([(fx * 0.4 + 2, -80), (fx * 1.2 + hem, -10)], gd, 2, cap=False)
        c.rect(-20, -92, 24, -80, gown, w=2.5, r=4)
    # front arm
    hand = (sh[0] + 4 + lerp(-2, 40, arm), sh[1] + 4 + lerp(44, -10, arm))
    c.stroke([(sh[0] + 6, sh[1] + 2), hand], body, 12)
    c.circle(hand[0], hand[1], 7, body)
    hx, hy = 16 + lean, -140
    D._head(c, hx, hy, pal, body, dark, belly, mouth, eyes, look, t)
    if bowtie:
        bx, by = hx + 4, hy + 32
        c.poly([(bx - 14, by - 8), (bx, by), (bx - 14, by + 8)], bowtie, w=2)
        c.poly([(bx + 14, by - 8), (bx, by), (bx + 14, by + 8)], bowtie, w=2)
        c.circle(bx, by, 4, mix(bowtie, (0, 0, 0), 0.2), w=1.5)
    if tiara:
        tiara_on(c, hx, hy)
    c.pop()


def tiara_on(c, hx, hy):
    pts = [(hx - 22, hy - 26), (hx - 14, hy - 40), (hx - 6, hy - 32), (hx + 2, hy - 48), (hx + 10, hy - 32),
           (hx + 18, hy - 40), (hx + 24, hy - 25)]
    c.poly(pts, GOLD, w=2)
    c.circle(hx + 2, hy - 40, 3.5, (230, 80, 120), w=1.2)
    c.circle(hx - 14, hy - 35, 2.2, (120, 200, 255), ol=None)
    c.circle(hx + 18, hy - 35, 2.2, (120, 200, 255), ol=None)


def sitting_extras(c, x, y, s, face, apron=False, tiara=False, pearls=False, head_dy=0.0, cap=False):
    """Accessories for a cat drawn with draw.cat(pose='sit') at the same x, y, s, face."""
    c.push(x, y, s, flip=face < 0)
    hx, hy = 18, -106 + head_dy
    if apron:
        c.poly([(-4, -74), (36, -74), (40, -10), (-6, -10)], (255, 255, 255), w=2.5)
        c.rect(-4, -84, 36, -74, (255, 255, 255), w=2.5, r=3)
        c.rect(6, -48, 28, -34, (240, 200, 210), w=1.5, r=3)
        c.line([(-6, -74), (-24, -66)], (255, 255, 255), 4)
    if cap:
        c.ellipse(hx - 4, hy - 30, 22, 8, (255, 255, 255), w=2)
        c.ellipse(hx - 4, hy - 36, 16, 8, (255, 255, 255), w=2)
    if pearls:
        for k in range(9):
            a = math.pi * (0.15 + 0.7 * k / 8)
            c.circle(hx + 2 + 24 * math.cos(a), hy + 22 + 10 * math.sin(a), 3.2, (250, 248, 240), w=1.2)
    if tiara:
        tiara_on(c, hx, hy)
    c.pop()


# ================================================================ vehicles

def wheel(c, x, y, r, ang, rim=(40, 30, 30), hub=(200, 40, 50), spokes=10, w=3):
    c.circle(x, y, r, rim, w=w)
    c.circle(x, y, r * 0.8, mix(rim, (255, 255, 255), 0.1), ol=None)
    for k in range(spokes):
        a = ang + k * math.tau / spokes
        c.line([(x, y), (x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)], hub, 2.2, cap=False)
    c.circle(x, y, r * 0.18, hub, w=1.5)


def fiaker(c, x, y, s=1.0, t=0.0, wheel_ang=0.0, seat=None):
    """Black Fiaker carriage, facing right; shafts reach forward to the horse at about x+200.
    seat(c) is called (in local coords) to draw passengers before the side panel."""
    c.push(x, y, s)
    # back wheel (far)
    wheel(c, -90, -56, 56, wheel_ang, rim=(30, 26, 30), hub=(190, 40, 50), spokes=12)
    # shafts
    c.line([(60, -86), (260, -128)], (40, 36, 40), 7)
    c.line([(60, -86), (260, -128)], (80, 70, 70), 3)
    # hood (folded back) + seat back
    c.poly([(-150, -110), (-160, -190), (-130, -214), (-80, -200), (-70, -110)], (30, 28, 34), w=3)
    for k in range(3):
        c.arc(-118, -150, 36 + 12 * k, 52 + 10 * k, 200, 320, (70, 66, 76), 2.5)
    c.rect(-70, -170, -40, -110, (180, 30, 44), w=2.5, r=6)
    if seat:
        seat(c)
    # body
    c.poly([(-160, -110), (60, -110), (80, -150), (100, -150), (90, -96), (40, -60), (-140, -60), (-166, -84)],
           (34, 32, 38), w=3)
    c.poly([(-150, -104), (50, -104), (34, -72), (-136, -72)], (50, 48, 56), ol=None)
    c.line([(-150, -88), (40, -88)], GOLD, 2.5, cap=False)
    # coach lamp
    c.line([(84, -150), (84, -176)], (40, 36, 40), 3)
    c.rect(74, -200, 94, -176, (250, 230, 150), w=2, r=3)
    c.poly([(70, -200), (84, -212), (98, -200)], (40, 36, 40), w=2)
    # driver's box + step
    c.rect(60, -160, 110, -150, (34, 32, 38), w=2)
    # wheels (near)
    wheel(c, -100, -60, 58, wheel_ang, rim=(36, 30, 34), hub=(200, 44, 54), spokes=12)
    wheel(c, 50, -42, 42, wheel_ang * 1.4, rim=(36, 30, 34), hub=(200, 44, 54), spokes=10)
    c.pop()


def bass_case(c, x, y, s=1.0, lid=0.0, inside=None, ang=0.0):
    """Double bass case lying on its back (scroll to the left), lid hinged at the back.
    inside(c) draws what's in it (local coords, case floor at y=-18)."""
    c.push(x, y, s)
    shape = []
    # outline of a double bass: big lower bout right, neck to the left
    for a in np.linspace(-math.pi / 2, math.pi / 2, 16):
        shape.append((70 + 70 * math.cos(a), -30 + 30 * math.sin(a) * 0.9))
    shape = [(px, py) for px, py in shape]
    outline = [(-150, -24), (-150, -40), (-30, -44), (-6, -56), (20, -48), (70, -60)] + \
              [(70 + 72 * math.cos(a), -30 - 34 * math.sin(a)) for a in np.linspace(math.pi / 2, -math.pi / 2, 12)] + \
              [(70, 4), (20, -8), (-6, -2), (-30, -14), (-150, -14)]
    case = (110, 60, 40)
    case_d = (80, 40, 28)
    velvet = (170, 30, 60)
    if lid > 0.05:
        # open: velvet interior visible
        c.poly(outline, case_d, w=3)
        inner = [((px - 0) * 0.92, py * 0.9 - 4) for px, py in outline]
        c.poly(inner, velvet, ol=None)
        if inside:
            inside(c)
        # lid standing up behind (drawn as a thin slanted shape above)
    else:
        c.poly(outline, case, w=3)
        c.line([(-140, -30), (130, -30)], case_d, 2.5, cap=False)
        for hx in (-60, 40, 110):
            c.rect(hx - 5, -36, hx + 5, -24, GOLD, w=1.5)
    c.pop()


def bass_lid(c, x, y, s=1.0, lid=0.0):
    """The lid of the bass case, hinged along the back edge, drawn behind the case."""
    if lid <= 0.05:
        return
    c.push(x, y, s)
    k = lid
    outline = [(-150, -24), (-150, -40), (-30, -44), (-6, -56), (20, -48), (70, -60)] + \
              [(70 + 72 * math.cos(a), -30 - 34 * math.sin(a)) for a in np.linspace(math.pi / 2, -math.pi / 2, 12)] + \
              [(70, 4), (20, -8), (-6, -2), (-30, -14), (-150, -14)]
    pts = [(px, -40 + (py + 30) * (1 - k) * 0.6 - k * (py + 30) * 1.4 - 10 * k) for px, py in outline]
    c.poly(pts, (124, 70, 46), w=3)
    c.poly([(px * 0.9, py * 0.95 - 2) for px, py in pts], (150, 40, 70), ol=None)
    c.pop()


def bus(c, x, y, s=1.0, t=0.0, wheel_ang=0.0, roof=None, door=0.0, lights=False):
    """Orchestra tour coach, facing right. roof(c) draws the roof-rack cargo (local coords, roof at y=-232)."""
    c.push(x, y, s)
    body = (250, 244, 228)
    red = (190, 40, 54)
    # body
    c.rect(-300, -230, 300, -40, body, w=3, r=22)
    c.poly([(240, -230), (300, -210), (306, -60), (240, -60)], body, ol=None)
    c.rect(-300, -110, 306, -76, red, ol=None)
    c.line([(-298, -110), (304, -110)], OUT, 2, cap=False)
    c.line([(-298, -76), (304, -76)], OUT, 2, cap=False)
    # windows
    for k in range(7):
        wx = -284 + k * 70
        c.rect(wx, -214, wx + 60, -136, (150, 200, 230), w=2.5, r=6)
        c.line([(wx + 10, -200), (wx + 24, -150)], (200, 230, 250), 4)
    # windscreen
    c.poly([(222, -216), (280, -206), (298, -136), (222, -136)], (140, 190, 225), w=2.5)
    # door
    c.rect(200 - 40 * door, -200, 236 - 40 * door, -50, (130, 180, 210), w=2.5, r=4)
    # lettering
    c.text(-30, -93, "VIENNA WALTZ ORCHESTRA", 17, (255, 240, 200), stroke=0)
    for k in range(3):
        nx = -250 + k * 22
        c.circle(nx, -56, 5, (60, 50, 60), ol=None)
        c.line([(nx + 4, -56), (nx + 4, -76)], (60, 50, 60), 2, cap=False)
    # headlight
    c.circle(296, -70, 8, (255, 240, 170) if lights else (240, 240, 230), w=2)
    # roof rack
    c.rect(-260, -246, 180, -234, None, ol=(90, 90, 100), w=3)
    for k in range(9):
        c.line([(-250 + k * 52, -246), (-250 + k * 52, -232)], (90, 90, 100), 2.5, cap=False)
    if roof:
        roof(c)
    # wheels
    for wx in (-190, 180):
        c.ellipse(wx, -44, 54, 40, (60, 56, 64), ol=None)
        c.circle(wx, -38, 38, (40, 38, 44), w=3)
        c.circle(wx, -38, 20, (190, 190, 200), w=2)
        for k in range(5):
            a = wheel_ang + k * math.tau / 5
            c.circle(wx + 11 * math.cos(a), -38 + 11 * math.sin(a), 3, (120, 120, 130), ol=None)
    c.pop()


def violin_case(c, x, y, s=1.0, col=(60, 40, 50)):
    c.push(x, y, s)
    c.poly([(-50, 0), (-50, -20), (10, -24), (30, -30), (54, -24), (56, -2), (30, 4), (10, 0)], col, w=2.5)
    c.rect(-6, -18, 6, -8, GOLD, w=1.5)
    c.pop()


# ================================================================ landmarks

def zigzag_roof(c, pts, y0, y1, cols, rows=8, teeth=14, x0=-400, x1=400):
    """Fill polygon pts with St. Stephen's coloured zigzag tile bands."""
    def draw(tc):
        h = (y1 - y0) / rows
        tw = (x1 - x0) / teeth
        tc.rect(x0, y0 - 20, x1, y1 + 20, cols[0], ol=None)
        for r in range(rows):
            ya = y0 + r * h
            col = cols[(r % (len(cols) - 1)) + 1] if r % 2 else cols[0]
            for k in range(teeth + 1):
                xa = x0 + k * tw
                tc.poly([(xa, ya + h), (xa + tw / 2, ya), (xa + tw, ya + h), (xa + tw, ya + h * 1.5),
                         (xa + tw / 2, ya + h * 0.5), (xa, ya + h * 1.5)], col, ol=None)
        # a few light diamonds
        for r in range(1, rows, 2):
            for k in range(0, teeth, 2):
                cx, cy = x0 + (k + 1) * tw, y0 + (r + 0.75) * h
                tc.poly([(cx - 6, cy), (cx, cy - 7), (cx + 6, cy), (cx, cy + 7)], (250, 240, 200), ol=None)
    masked(c, pts, draw)
    c.poly(pts, None, w=3)


def stephansdom(c, x, y, s=1.0, sky=(150, 190, 230)):
    """St. Stephen's Cathedral seen from the south: zigzag roof, tall spire on the right."""
    c.push(x, y, s)
    wall = (214, 196, 160)
    wall_d = (176, 156, 120)
    # west towers (left)
    for tx in (-330, -270):
        c.rect(tx - 24, -300, tx + 24, 0, wall, w=3)
        c.poly([(tx - 26, -300), (tx, -360), (tx + 26, -300)], wall_d, w=3)
        arch_window(c, tx, -230, 18, 50, (70, 70, 96), pointed=True, ww=2)
        c.line([(tx, -360), (tx, -378)], OUT, 3)
        c.circle(tx, -380, 4, GOLD, w=1.5)
    # nave
    c.rect(-300, -170, 320, 0, wall, w=3)
    for bx in range(-260, 320, 80):
        c.poly([(bx - 8, 0), (bx - 8, -150), (bx, -176), (bx + 8, -150), (bx + 8, 0)], wall_d, w=2)
    for wx in range(-220, 320, 80):
        arch_window(c, wx, -40, 30, 100, (80, 90, 140), pointed=True, ww=2)
        c.line([(wx, -40), (wx, -118)], (60, 60, 90), 2, cap=False)
    # the roof
    roof = [(-300, -170), (-240, -390), (250, -390), (320, -170)]
    zigzag_roof(c, roof, -390, -170, [(240, 200, 70), (40, 110, 80), (40, 40, 50), (250, 240, 220)], rows=9,
                teeth=16, x0=-320, x1=340)
    # the south tower (Steffl)
    tx = 140
    c.rect(tx - 50, -330, tx + 50, 0, wall, w=3)
    c.poly([(tx - 50, -330), (tx - 40, -480), (tx + 40, -480), (tx + 50, -330)], wall, w=3)
    for wy in (-90, -200, -300, -420):
        arch_window(c, tx, wy, 24, 64, (70, 70, 96), pointed=True, ww=2)
    c.poly([(tx - 40, -480), (tx - 30, -600), (tx + 30, -600), (tx + 40, -480)], wall_d, w=3)
    arch_window(c, tx, -520, 18, 56, (70, 70, 96), pointed=True, ww=2)
    c.poly([(tx - 30, -600), (tx, -820), (tx + 30, -600)], wall_d, w=3)
    for k in range(9):           # crockets along the spire
        u = (k + 0.5) / 9
        yy = lerp(-600, -820, u)
        hw = 30 * (1 - u)
        c.circle(tx - hw - 3, yy, 4, wall, w=1.5)
        c.circle(tx + hw + 3, yy, 4, wall, w=1.5)
        c.line([(tx - hw * 0.8, yy), (tx + hw * 0.8, yy)], OUT, 1.5, cap=False)
    c.line([(tx, -820), (tx, -850)], OUT, 3)
    c.circle(tx, -852, 5, GOLD, w=1.5)
    # doors
    c.poly([(-120, 0), (-120, -70), (-96, -96), (-72, -70), (-72, 0)], (90, 60, 50), w=2.5)
    c.pop()


def opera(c, x, y, s=1.0):
    """Vienna State Opera: arcades below, a loggia of five arches above, green copper roofs."""
    c.push(x, y, s)
    st, sd = (232, 216, 184), (196, 176, 142)
    # side wings
    for sx in (-1, 1):
        c.rect(sx * 330 - 110, -230, sx * 330 + 110, 0, st, w=3)
        c.poly([(sx * 330 - 118, -230), (sx * 330 - 90, -290), (sx * 330 + 90, -290), (sx * 330 + 118, -230)],
               COPPER, w=3)
        for k in range(4):
            wx = sx * 330 - 75 + k * 50
            arch_window(c, wx, -40, 26, 70, (110, 90, 80), ww=2)
            arch_window(c, wx, -140, 22, 60, (110, 120, 150), ww=2)
    # central block + high roof behind
    c.poly([(-200, -330), (-150, -420), (150, -420), (200, -330)], COPPER, w=3)
    c.poly([(-150, -420), (150, -420), (130, -440), (-130, -440)], COPPER_D, w=2.5)
    c.rect(-220, -330, 220, 0, st, w=3)
    c.rect(-220, -330, 220, -310, sd, w=2.5)
    # ground arcade
    for k in range(5):
        wx = -160 + k * 80
        arch_window(c, wx, 0, 56, 110, (90, 70, 66), ww=2.5)
    c.line([(-220, -120), (220, -120)], OUT, 2.5, cap=False)
    # loggia
    for k in range(5):
        wx = -160 + k * 80
        arch_window(c, wx, -130, 50, 150, (120, 130, 170), ww=2.5)
        c.rect(wx - 34, -300, wx - 30, -130, sd, ol=None)
    # statues: two riders on top
    for sx in (-1, 1):
        px = sx * 170
        c.rect(px - 20, -350, px + 20, -330, sd, w=2)
        c.poly([(px - 18, -350), (px - 12, -380), (px + 14, -386), (px + 22, -350)], (90, 140, 130), w=2)
        c.circle(px + 4, -398, 9, (90, 140, 130), w=2)
    c.text(0, -320, "OPER", 14, (120, 90, 60))
    c.pop()


def riesenrad(c, x, y, r=260, rot=0.0, t=0.0, cabins=15, lit=0.0):
    """The giant Ferris wheel in the Prater. (x, y) = axle. Drawn with its support pylons."""
    st = (60, 64, 76)
    st_l = (110, 116, 130)
    base = y + r + 70
    # pylons (back)
    for sx in (-1, 1):
        c.line([(x, y), (x + sx * r * 0.62, base)], st, 7)
        c.line([(x, y), (x + sx * r * 0.42, base)], st, 5)
        for k in range(1, 6):
            u = k / 6
            a = (lerp(x, x + sx * r * 0.62, u), lerp(y, base, u))
            b = (lerp(x, x + sx * r * 0.42, u), lerp(y, base, u))
            c.line([a, b], st, 2, cap=False)
    # rims
    c.circle(x, y, r, None, ol=st, w=6)
    c.circle(x, y, r * 0.9, None, ol=st_l, w=3)
    n = 30
    for k in range(n):
        a = rot + k * math.tau / n
        c.line([(x, y), (x + math.cos(a) * r, y + math.sin(a) * r)], st_l if k % 2 else st, 1.6, cap=False)
        a2 = rot + (k + 0.5) * math.tau / n
        c.line([(x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a2) * r * 0.9, y + math.sin(a2) * r * 0.9)],
               st, 1.5, cap=False)
    c.circle(x, y, 18, st, w=3)
    c.circle(x, y, 8, (200, 50, 50), ol=None)
    # cabins
    for k in range(cabins):
        a = rot + k * math.tau / cabins
        px, py = x + math.cos(a) * r, y + math.sin(a) * r
        cabin(c, px, py, 1.0 * r / 260, lit)
    # base buildings
    c.rect(x - r * 0.75, base - 30, x + r * 0.75, base, (200, 70, 60), w=3)
    for k in range(6):
        wx = x - r * 0.65 + k * r * 0.26
        c.rect(wx, base - 24, wx + r * 0.12, base - 8, (250, 230, 170) if lit else (240, 220, 180), w=2)
    return base


def cabin(c, px, py, s=1.0, lit=0.0, inside=None):
    c.push(px, py, s)
    c.line([(0, 0), (0, 8)], OUT, 2.5, cap=False)
    c.rect(-22, 8, 22, 40, (210, 40, 46), w=2.5, r=4)
    c.poly([(-26, 10), (0, 0), (26, 10)], (180, 30, 40), w=2)
    winc = mix((240, 230, 210), (255, 220, 120), lit)
    for k in range(3):
        c.rect(-17 + k * 12, 14, -9 + k * 12, 28, winc, w=1.5)
    if inside:
        inside(c)
    c.pop()


def palace(c, x, y, s=1.0, lit=0.0):
    """Schonbrunn Palace: a long yellow front, green roof, central portico with a double stair."""
    c.push(x, y, s)
    wall = SCHON
    trim = (250, 244, 226)
    roof = (90, 120, 110)
    win = mix((90, 110, 100), (255, 214, 120), lit)
    # main block
    c.rect(-560, -200, 560, 0, wall, w=3)
    c.rect(-570, -224, 570, -200, roof, w=3)
    c.rect(-570, -210, 570, -200, trim, w=2)
    # wings slightly forward
    for sx in (-1, 1):
        c.rect(sx * 470 - 90, -214, sx * 470 + 90, 0, mix(wall, (255, 255, 255), 0.06), w=3)
        c.rect(sx * 470 - 96, -236, sx * 470 + 96, -214, roof, w=3)
    # centre pavilion
    c.rect(-140, -250, 140, 0, mix(wall, (255, 255, 255), 0.08), w=3)
    c.poly([(-150, -250), (0, -300), (150, -250)], trim, w=3)
    c.poly([(-120, -256), (0, -290), (120, -256)], wall, ol=None)
    for k in range(6):
        cx = -110 + k * 44
        c.rect(cx - 6, -240, cx + 6, -96, trim, w=2)
    # windows: two rows
    for row, (wy, hh) in enumerate(((-170, 46), (-80, 56))):
        for k in range(-13, 14):
            wx = k * 40
            if abs(wx) < 150:
                continue
            c.rect(wx - 11, wy, wx + 11, wy + hh, win, w=2)
            c.rect(wx - 14, wy - 6, wx + 14, wy, trim, ol=None)
    for k in range(5):
        cx = -88 + k * 44
        arch_window(c, cx, -110, 22, 60, win, ww=2)
    # double staircase
    c.poly([(-200, 0), (-80, -90), (-60, -90), (-160, 0)], trim, w=2.5)
    c.poly([(200, 0), (80, -90), (60, -90), (160, 0)], trim, w=2.5)
    c.rect(-80, -96, 80, -86, trim, w=2.5)
    for k in range(5):
        c.line([(-196 + k * 24, -2 - k * 18), (-160 + k * 20, -2 - k * 18)], OUT, 1.5, cap=False)
        c.line([(196 - k * 24, -2 - k * 18), (160 - k * 20, -2 - k * 18)], OUT, 1.5, cap=False)
    # flag
    c.line([(0, -300), (0, -350)], OUT, 2.5)
    c.poly([(0, -350), (34, -344), (0, -336)], (220, 40, 50), w=1.5)
    c.pop()


def gloriette(c, x, y, s=1.0, col=(240, 236, 220)):
    c.push(x, y, s)
    c.rect(-160, -70, 160, 0, col, w=2.5)
    for k in range(-7, 8):
        if k == 0:
            continue
        arch_window(c, k * 20, 0, 13, 54, (150, 170, 200), ww=1.5)
    arch_window(c, 0, 0, 30, 70, (150, 170, 200), ww=2)
    c.rect(-50, -94, 50, -70, col, w=2.5)
    c.poly([(-14, -94), (0, -116), (14, -94)], GOLD, w=2)
    c.pop()


def hedge_cone(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-22, 0), (0, -80), (22, 0)], (60, 120, 70), w=2.5)
    c.poly([(0, -80), (22, 0), (8, 0)], (44, 96, 56), ol=None)
    c.pop()


def fountain(c, x, y, s=1.0, t=0.0, water=True):
    c.push(x, y, s)
    c.ellipse(0, 0, 120, 26, (190, 186, 176), w=3)
    c.ellipse(0, -4, 104, 18, (110, 170, 210), ol=None)
    c.rect(-14, -70, 14, -4, (190, 186, 176), w=2.5)
    c.ellipse(0, -70, 40, 9, (190, 186, 176), w=2.5)
    if water:
        for k in range(6):
            a = k * math.pi / 5
            u = (t * 1.5 + k * 0.17) % 1.0
            pts = [(math.cos(a) * 46 * v, -74 - 40 * v + 52 * v * v) for v in np.linspace(0, 1, 8)]
            c.line(pts, (180, 220, 245), 3)
            c.circle(math.cos(a) * 46 * u, -74 - 40 * u + 52 * u * u, 2.5, (230, 245, 255), ol=None)
        c.line([(0, -72), (0, -110)], (190, 225, 245), 4)
    c.pop()


def chandelier(c, x, y, s=1.0, t=0.0, glow=True):
    c.push(x, y, s)
    c.line([(0, -400), (0, -60)], (150, 120, 60), 2.5, cap=False)
    if glow:
        c.glow(0, 0, 130, 80, (255, 236, 170), None, steps=1) if False else None
    for tier, (ry, rx, n) in enumerate(((-40, 50, 5), (0, 80, 7), (34, 56, 5))):
        c.ellipse(0, ry, rx, rx * 0.18, GOLD, w=2)
        for k in range(n):
            px = -rx + 2 * rx * k / (n - 1)
            c.rect(px - 2.5, ry - 18, px + 2.5, ry - 2, (255, 250, 236), w=1)
            fl = 1 + 0.15 * math.sin(t * 9 + k * 1.7 + tier)
            c.ellipse(px, ry - 23, 3.2, 5.5 * fl, (255, 210, 90), ol=None)
            c.ellipse(px, ry - 22, 1.6, 3 * fl, (255, 250, 220), ol=None)
        for k in range(n + 1):
            px = -rx * 0.9 + 1.8 * rx * k / n
            c.line([(px, ry + 2), (px, ry + 14)], (230, 240, 255), 1.5, cap=False)
            c.circle(px, ry + 16, 2.6, (210, 230, 255), ol=None)
    c.ellipse(0, 54, 10, 14, (210, 230, 255), w=1.5)
    c.pop()


# ================================================================ food & small things

def sachertorte(c, x, y, s=1.0, cut=True, bite=0.0, seal=True):
    """Chocolate Sachertorte on a plate; (x, y) = plate centre."""
    c.push(x, y, s)
    c.ellipse(0, 0, 80, 16, (250, 250, 246), w=2.5)
    c.ellipse(0, -2, 64, 11, (236, 236, 232), ol=None)
    # cake (side band, apricot stripe, glazed top)
    c.rect(-56, -46, 56, -6, CHOC, w=3, r=4)
    c.ellipse(0, -6, 56, 12, CHOC, ol=None)
    c.line([(-54, -26), (54, -26)], (240, 150, 60), 3, cap=False)
    c.ellipse(0, -46, 56, 13, CHOC_L, w=3)
    c.arc(-10, -50, 30, 6, 200, 300, (160, 110, 90), 2.5)
    if seal:
        c.circle(10, -48, 9, (60, 30, 24), w=1.5)
        c.circle(10, -48, 5, (90, 50, 36), ol=None)
    if cut:
        c.poly([(56, -46), (20, -40), (20, -2), (56, -6)], (90, 50, 36), w=2)
        c.line([(20, -24), (56, -26)], (240, 150, 60), 2.5, cap=False)
        c.poly([(56, -46), (20, -40), (30, -52)], CHOC_L, w=2)
    if bite > 0:
        for k in range(int(3 * bite) + 1):
            c.circle(-56 + k * 10, -40, 9, (236, 236, 232), ol=None)
    # whipped cream
    c.ellipse(-60, -8, 16, 8, CREAM_W, w=2)
    c.ellipse(-62, -14, 10, 6, CREAM_W, w=2)
    c.pop()


def slice_cake(c, x, y, s=1.0, plate=True):
    c.push(x, y, s)
    if plate:
        c.ellipse(0, 0, 42, 9, (250, 250, 246), w=2)
    c.poly([(-30, -4), (24, -4), (24, -36), (-30, -30)], CHOC, w=2.5)
    c.line([(-28, -18), (22, -20)], (240, 150, 60), 2.5, cap=False)
    c.poly([(-30, -30), (24, -36), (10, -42), (-34, -34)], CHOC_L, w=2)
    c.ellipse(28, -8, 12, 6, CREAM_W, w=2)
    c.pop()


def strudel(c, x, y, s=1.0):
    c.push(x, y, s)
    c.ellipse(0, 0, 50, 10, (250, 250, 246), w=2)
    c.ellipse(0, -16, 42, 16, (230, 180, 110), w=2.5)
    for k in range(5):
        c.arc(-28 + k * 14, -16, 6, 14, 280, 440, (190, 130, 70), 2)
    for k in range(9):
        c.circle(-30 + k * 7.5, -28 + 3 * math.sin(k), 1.6, (255, 255, 255), ol=None)
    c.ellipse(36, -6, 12, 9, (240, 210, 140), w=2)
    c.pop()


def coffee_cup(c, x, y, s=1.0, t=0.0, steam=True):
    c.push(x, y, s)
    c.ellipse(0, 0, 26, 6, (250, 250, 246), w=2)
    c.poly([(-16, -4), (-18, -30), (18, -30), (16, -4)], (250, 250, 246), w=2)
    c.arc(22, -18, 8, 8, 270, 450, OUT, 2.5)
    c.ellipse(0, -30, 18, 4, (200, 160, 110), w=1.5)
    c.ellipse(0, -31, 10, 2.5, (250, 236, 210), ol=None)
    if steam:
        for k in range(2):
            u = (t * 0.8 + k * 0.5) % 1.0
            pts = [(-4 + 8 * k + 5 * math.sin(v * 6 + t * 3), -36 - 30 * v * (0.4 + u)) for v in np.linspace(0, 1, 6)]
            c.line(pts, mix((255, 255, 255), (230, 220, 210), u), 2.5)
    c.pop()


def cream_can(c, x, y, s=1.0, ang=0.0):
    c.push(x, y, s)
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py):
        return (px * ca - py * sa, px * sa + py * ca)
    c.poly([R(-10, 0), R(-10, -50), R(10, -50), R(10, 0)], (200, 200, 214), w=2)
    c.poly([R(-6, -50), R(0, -66), R(6, -50)], (250, 250, 250), w=2)
    c.poly([R(-10, -30), R(10, -30), R(10, -18), R(-10, -18)], (220, 60, 80), ol=None)
    c.pop()


def cream_heap(c, x, y, s=1.0, k=1.0):
    """A swirly mountain of whipped cream; k grows it."""
    if k <= 0.02:
        return
    c.push(x, y, s * k)
    for (dx, dy, r) in ((-40, -16, 26), (40, -16, 26), (0, -20, 34), (-22, -46, 24), (22, -46, 24), (0, -70, 22),
                        (0, -92, 14)):
        c.circle(dx, dy, r, CREAM_W, w=2.5)
    for (dx, dy, r) in ((-40, -16, 22), (40, -16, 22), (0, -20, 30), (-22, -46, 20), (22, -46, 20), (0, -70, 18)):
        c.circle(dx, dy, r, CREAM_W, ol=None)
    c.arc(-10, -40, 16, 10, 200, 340, (230, 226, 216), 2)
    c.arc(10, -66, 10, 6, 200, 340, (230, 226, 216), 2)
    c.poly([(0, -104), (-6, -92), (6, -92)], CREAM_W, w=2)
    c.circle(0, -112, 7, (220, 40, 60), w=1.5)       # a cherry on top
    c.pop()


def newspaper(c, x, y, s=1.0, open_=1.0, t=0.0):
    """Newspaper with the contest advert. open_ 0 = crumpled wrapping, 1 = flat and readable."""
    c.push(x, y, s)
    if open_ < 0.5:
        c.poly([(-50, 0), (-60, -30), (-30, -44), (10, -40), (50, -50), (60, -14), (40, 4)], (236, 232, 218), w=2.5)
        for k in range(4):
            c.line([(-40 + k * 22, -6), (-30 + k * 20, -34)], (190, 186, 176), 2, cap=False)
        c.pop()
        return
    c.poly([(-130, 0), (-124, -150), (130, -156), (134, -4)], (240, 236, 222), w=2.5)
    c.text(0, -136, "VIENNA NEWS", 16, (60, 50, 50))
    c.line([(-116, -124), (120, -128)], OUT, 1.5, cap=False)
    c.text(0, -108, "GRAND WALTZ", 18, (180, 40, 50))
    c.text(0, -90, "CONTEST!", 18, (180, 40, 50))
    # tiny dancers and cake
    c.push(-70, -26, 0.32)
    dancer(c, -18, 0, 1.0, 1, D.LUNA, gown=(120, 170, 230), arm=1.0)
    dancer(c, 30, 0, 1.0, -1, D.WHISKERS, bowtie=(200, 40, 50), arm=1.0, eyes="happy")
    c.pop()
    c.push(60, -22, 0.6)
    sachertorte(c, 0, 0, 1.0, cut=False)
    c.pop()
    c.text(60, -6, "1st PRIZE", 9, (60, 50, 50))
    for k in range(5):
        c.line([(-122 + 2 * k, -76 + 0 * k), (-20, -76)], (200, 196, 186), 0.1, cap=False)
    c.pop()


def music_notes(c, x, y, t, t0, n=4, col=(255, 240, 200), s=1.0):
    if t < t0:
        return
    for k in range(n):
        u = ((t - t0) * 0.35 + k / n) % 1.0
        nx = x + 40 * math.sin(k * 2.3 + t * 1.5) * u + (k - n / 2) * 18
        ny = y - 110 * u
        a = 1 - u
        cc = mix(col, (255, 255, 255), u * 0.3)
        c.push(nx, ny, s * (0.8 + 0.3 * a))
        c.ellipse(0, 0, 6, 4.5, cc, ol=OUT, w=1.5)
        c.line([(5, 0), (5, -20)], OUT, 2, cap=False)
        if k % 2:
            c.line([(5, -20), (14, -14)], OUT, 2, cap=False)
        c.pop()


def confetti(c, t, t0, n=40, seed=3, area=(0, 0, W, 560)):
    if t < t0:
        return
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = area
    for k in range(n):
        x = rng.uniform(x0, x1)
        sp = rng.uniform(50, 110)
        y = y0 - 40 + ((t - t0) * sp + rng.uniform(0, y1 - y0)) % (y1 - y0 + 40)
        col = [(240, 80, 110), (250, 210, 80), (120, 190, 240), (140, 220, 150), (210, 140, 240)][k % 5]
        a = t * rng.uniform(2, 6) + k
        dx, dy = 6 * math.cos(a), 3
        c.poly([(x - dx, y - dy), (x + dx, y - dy), (x + dx * 0.8, y + dy), (x - dx * 0.8, y + dy)], col, ol=None)


def bentwood_chair(c, x, y, s=1.0, face=1, col=(110, 66, 40)):
    c.push(x, y, s, flip=face < 0)
    c.line([(-20, 0), (-16, -50)], col, 5)
    c.line([(20, 0), (18, -50)], col, 5)
    c.ellipse(0, -52, 26, 7, col, w=2)
    c.line([(-18, -52), (-24, -120)], col, 5)
    c.arc(-24, -98, 16, 22, 180, 360, col, 5)
    c.line([(-8, -52), (-14, -96)], col, 4)
    c.pop()


def marble_table(c, x, y, s=1.0):
    c.push(x, y, s)
    c.line([(0, 0), (0, -70)], (60, 50, 50), 6)
    c.ellipse(0, 0, 30, 6, (60, 50, 50), ol=None)
    c.ellipse(0, -72, 70, 13, (246, 244, 240), w=2.5)
    c.arc(-20, -72, 30, 6, 200, 290, (200, 200, 210), 1.5)
    c.pop()
