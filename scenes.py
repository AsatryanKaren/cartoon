import math
import random

from PIL import Image

from draw import (FONT_SUB, FONT_TITLE, H, LUNA, OUT, W, WHISKERS, C, butterfly, cat, clamp, cloud,
                  fish, font, frog, grad, lerp, mix, mouse, room, smooth, stars, zzz)

FLOOR = 605
SILL = 330
STRIDE = 95.0


def walk_between(x0, x1, k):
    """Position and walk phase while moving from x0 to x1 with eased progress k."""
    x = lerp(x0, x1, smooth(k))
    return x, abs(x - x0) / STRIDE


def hop(x0, y0, x1, y1, u, height):
    u = clamp(u)
    return lerp(x0, x1, u), lerp(y0, y1, u) - height * math.sin(math.pi * u)


def sky(c, a, b, k):
    if k <= 0:
        c.bg(grad(*a))
    elif k >= 1:
        c.bg(grad(*b))
    else:
        c.bg(Image.blend(grad(*a), grad(*b), k))


DAWN = ((120, 110, 190), (255, 180, 140))
DAY = ((110, 175, 240), (205, 232, 255))
GOLDEN = ((250, 165, 90), (255, 225, 160))
SUNSET = ((235, 120, 95), (255, 200, 140))
DUSK = ((70, 60, 130), (215, 120, 115))
NIGHT = ((10, 14, 45), (40, 46, 98))
TITLE = ((25, 20, 65), (85, 50, 120))


# ---------------------------------------------------------------- title

def sc_title(c, t, sc):
    c.bg(grad(*TITLE))
    stars(c, t, 140, 1, y1=520)
    for k in range(4, 0, -1):
        c.circ(1020, 160, 80 + k * 18, fill=mix((85, 60, 130), (130, 110, 170), 1 / k))
    c.circ(1020, 160, 80, fill=(250, 245, 215))
    c.circ(995, 140, 12, fill=(232, 226, 195))
    c.circ(1045, 185, 18, fill=(232, 226, 195))
    c.ell(640, 830, 900, 270, fill=(38, 28, 62))
    sil = {'fur': (22, 16, 40), 'belly': (22, 16, 40), 'stripe': None, 'eye': (0, 0, 0), 'inner': (0, 0, 0)}
    cat(c, 560, 580, sil, f=1, t=t, s=1.0, sil=True)
    cat(c, 700, 582, sil, f=1, t=t, s=0.9, sil=True, seed=2)
    a = smooth(sc.p('intro', t) * 1.4)
    bgc = (50, 35, 90)
    c.text(520, 200, 'Whiskers and the', font(FONT_TITLE, 58, 1), mix(bgc, (255, 220, 140), a),
           stroke=3 if a > 0.5 else 0, stroke_fill=(40, 20, 60))
    c.text(520, 275, 'Moon Fish', font(FONT_TITLE, 96, 1), mix(bgc, (255, 245, 220), a),
           stroke=4 if a > 0.5 else 0, stroke_fill=(40, 20, 60))
    a2 = smooth(sc.p('hold', t) * 2)
    c.text(520, 345, 'a little cat cartoon', font(FONT_SUB, 26), mix(bgc, (200, 190, 240), a2))


# ---------------------------------------------------------------- morning

def window_day(c, t, k, sun):
    sky(c, DAWN, DAY, k)
    sx, sy = lerp(260, 470, k), lerp(330, 170, k)
    c.circ(sx, sy, 34, fill=mix((255, 190, 120), (255, 240, 140), k))
    cloud(c, 300 + t * 4, 150, 0.6)
    room(c, sun)


def sc_morning(c, t, sc):
    k = smooth(t / sc.e('sunrise'))
    window_day(c, t, k, 'day')
    m = lambda ch: sc.mouth(ch, t)

    ps = sc.p('stretch', t)
    pb = sc.p('bowl', t)
    if ps < 0.45:
        cat(c, 370, SILL, WHISKERS, f=-1, t=t, mouth=m('W'), pose='sleep', seed=1)
        if t < sc.s('stretch'):
            zzz(c, 330, 250, t)
    elif ps < 1:
        u = (ps - 0.45) / 0.55
        x, y = hop(370, SILL, 430, FLOOR, u, 80)
        cat(c, x, y, WHISKERS, f=1, t=t, pose='jump' if u < 1 else 'sit', seed=1)
    elif pb <= 0:
        cat(c, 430, FLOOR, WHISKERS, f=1, t=t, mouth=m('W'), seed=1)
    elif pb < 1:
        x, ph = walk_between(430, 790, pb)
        cat(c, x, FLOOR, WHISKERS, f=1, t=t, pose='walk', walk=ph, seed=1)
    else:
        sad = t > sc.lines[-2]['s']
        cat(c, 790, FLOOR, WHISKERS, f=1, t=t, mouth=m('W'), seed=1, closed=sad and m('W') < 0.1,
            look=(0, 1) if sad else (0, 0))

    pl = sc.p('sunrise', t)
    if pl < 1:
        x, ph = walk_between(1400, 640, clamp(pl * 1.3))
        cat(c, x, FLOOR, LUNA, f=-1, t=t, pose='walk' if pl * 1.3 < 1 else 'sit', walk=ph, seed=3)
    elif pb <= 0:
        cat(c, 640, FLOOR, LUNA, f=-1, t=t, mouth=m('L'), seed=3, look=(-1, -1))
    elif pb < 1:
        x, ph = walk_between(640, 1010, pb)
        cat(c, x, FLOOR, LUNA, f=1, t=t, pose='walk', walk=ph, seed=3)
    else:
        cat(c, 1010, FLOOR, LUNA, f=-1, t=t, mouth=m('L'), seed=3, look=(-1, 0.5))


# ---------------------------------------------------------------- legend

def thought(c, x, y, a, t):
    if a <= 0:
        return
    col = (255, 255, 255)
    for i, (dx, dy, r) in enumerate(((0, 0, 8), (20, -30, 13), (45, -65, 18))):
        if a > i * 0.15:
            c.circ(x + dx, y + dy, r, fill=col, outline=OUT, w=3)
    if a > 0.45:
        sc = smooth((a - 0.45) / 0.55)
        cx, cy = x + 130, y - 160
        for dx, dy, r in ((-90, 0, 55), (-40, -40, 65), (30, -45, 70), (90, -5, 58), (40, 35, 60), (-40, 35, 55)):
            c.circ(cx + dx * sc, cy + dy * sc, r * sc + 4, fill=OUT)
        for dx, dy, r in ((-90, 0, 55), (-40, -40, 65), (30, -45, 70), (90, -5, 58), (40, 35, 60), (-40, 35, 55)):
            c.circ(cx + dx * sc, cy + dy * sc, r * sc, fill=col)
        if sc > 0.6:
            fish(c, cx + 10, cy - 5 + 4 * math.sin(t * 3), 1.15, (215, 225, 245),
                 glow=((255, 255, 255), (230, 240, 255)))


def sc_legend(c, t, sc):
    sky(c, DAY, GOLDEN, t / sc.dur * 0.6)
    c.circ(500, 160, 30, fill=(255, 235, 150))
    cloud(c, 260 + t * 3, 170, 0.7)
    room(c, 'afternoon')
    m = lambda ch: sc.mouth(ch, t)
    pm = sc.p('meow', t)
    jump = 22 * abs(math.sin(math.pi * pm * 2)) if 0 < pm < 1 else 0
    cat(c, 520, 615 - jump, LUNA, f=1, t=t, mouth=m('L') or (0.8 if 0.3 < pm < 0.8 else 0), seed=3)
    think_a = sc.p('think', t) if t < sc.lines[6]['s'] else max(0, 1 - (t - sc.lines[6]['s']) * 2)
    cat(c, 770, 615 - jump * 0.8, WHISKERS, f=-1, t=t, mouth=m('W') or (0.8 if 0.1 < pm < 0.6 else 0),
        seed=1, look=(1, -1) if think_a > 0 else (0, 0), happy=think_a > 0.6)
    thought(c, 820, 450, think_a, t)


# ---------------------------------------------------------------- garden

def flower(c, x, y, col, t, i):
    sway = 3 * math.sin(t * 1.5 + i)
    c.line([(x, y), (x + sway, y - 34)], (60, 130, 50), 3)
    for a in range(5):
        ang = a * 2 * math.pi / 5 + i
        c.circ(x + sway + 8 * math.cos(ang), y - 34 + 8 * math.sin(ang), 6, fill=col)
    c.circ(x + sway, y - 34, 5, fill=(255, 220, 80))


def wrap(base, off, period, lo=-200):
    return (base - off) % period + lo


def garden_bg(c, t, k, off):
    sky(c, DAY, GOLDEN, k)
    c.circ(lerp(1000, 820, k), lerp(110, 230, k), 55, fill=mix((255, 240, 140), (255, 190, 90), k))
    for i in range(5):
        cloud(c, wrap(i * 340 + t * 10, off * 0.1, 1700), 80 + (i % 3) * 45, 1 + 0.25 * (i % 2),
              mix((255, 255, 255), (255, 225, 200), k))
    for i in range(5):
        c.ell(wrap(i * 450, off * 0.3, 2250, -300), 590, 380, 170,
              fill=mix((140, 195, 115), (170, 170, 100), k))
    for i in range(4):
        x = wrap(i * 420 + 100, off * 0.6, 1680)
        for dx, dy, r in ((-40, 0, 45), (10, -25, 55), (55, 0, 42)):
            c.circ(x + dx, 548 + dy, r, fill=mix((80, 150, 70), (110, 130, 60), k))
    c.rect(0, 545, W, H, fill=mix((115, 185, 85), (150, 170, 80), k))
    c.ell(640, 640, 900, 40, fill=mix((200, 180, 130), (215, 175, 120), k))
    cols = [(240, 90, 110), (250, 250, 255), (180, 120, 230), (255, 160, 60)]
    for i in range(10):
        flower(c, wrap(i * 160, off, 1600), 575 + (i % 2) * 8, cols[i % 4], t, i)
    for i in range(10):
        flower(c, wrap(i * 190 + 70, off * 1.25, 1900), 712, cols[(i + 2) % 4], t, i + 3)


def fence(c, x):
    for dx in (-60, 0, 60):
        c.poly([(x + dx - 12, FLOOR + 5), (x + dx - 12, FLOOR - 110), (x + dx, FLOOR - 125),
                (x + dx + 12, FLOOR - 110), (x + dx + 12, FLOOR + 5)], fill=(170, 115, 70), outline=OUT, w=3)
    for y in (FLOOR - 85, FLOOR - 40):
        c.rect(x - 90, y, x + 90, y + 14, fill=(185, 128, 80), outline=OUT, w=3)


def sc_garden(c, t, sc):
    walking_names = ['walk0', 'walk', 'walk1', 'walk2_line', 'walk2']
    names = [n for n in walking_names if n in sc.marks]
    off = sc.time_in(names, t) * 150
    moving = any(sc.inside(n, t) for n in names)
    garden_bg(c, t, t / sc.dur, off)
    m = lambda ch: sc.mouth(ch, t)
    ph = off / STRIDE

    fx = lerp(1450, -250, sc.p('fence', t)) if sc.inside('fence', t) else None
    if fx is not None:
        fence(c, fx)

    pc = sc.p('chase', t)
    for st, x, seed, ch in ((LUNA, 600, 3, 'L'), (WHISKERS, 420, 1, 'W')):
        y, pose = FLOOR, 'walk' if moving else 'sit'
        if fx is not None:
            pose = 'walk'
            d = fx - x
            if abs(d) < 150:
                y -= 110 * math.cos(d / 150 * math.pi / 2)
                pose = 'jump'
            ph = (sc.time_in(['fence'], t) * 150 + off) / STRIDE
        if ch == 'W' and 0 < pc < 1:
            y -= 130 * math.sin(math.pi * pc)
            pose = 'jump'
        look = (1, -1) if ch == 'W' and sc.inside('walk2', t) else (0, 0)
        if pose == 'sit':
            look = (1 if ch == 'W' else -1, 0)
        cat(c, x, y, st, f=1, t=t, mouth=m(ch), pose=pose, walk=ph + seed * 0.3, seed=seed, look=look)

    if sc.inside('walk2', t) or sc.s('walk2') <= t < sc.e('chase') + 0.5:
        if t < sc.s('chase'):
            bx, by = 520 + 50 * math.sin(t * 1.7), 400 + 25 * math.sin(t * 3.1)
        else:
            u = clamp((t - sc.s('chase')) / (sc.e('chase') - sc.s('chase') + 0.5))
            bx, by = lerp(520, 1350, u), lerp(400, 60, u) + 20 * math.sin(t * 6)
        butterfly(c, bx, by, t)


# ---------------------------------------------------------------- meadow

def grass(c, t, off, y, n, h, col, seed):
    rnd = random.Random(seed)
    for i in range(n):
        base = rnd.uniform(0, 1500)
        x = wrap(base, off, 1500, -110)
        hh = h * rnd.uniform(0.6, 1.1)
        sw = 8 * math.sin(t * 1.3 + base * 0.01)
        c.poly([(x - 5, y), (x + sw, y - hh), (x + 5, y)], fill=col)


def sc_meadow(c, t, sc):
    k = t / sc.dur
    sky(c, SUNSET, DUSK, smooth(k))
    c.circ(lerp(900, 1000, k), lerp(320, 470, k), 70, fill=mix((255, 200, 110), (240, 120, 90), k))
    names = ['walk', 'walkn']
    off = sc.time_in(names, t) * 140
    moving = t >= sc.s('walk')
    for i in range(4):
        c.ell(wrap(i * 520, off * 0.3, 2080, -300), 600, 420, 160, fill=mix((120, 150, 90), (70, 80, 85), k))
    c.rect(0, 560, W, H, fill=mix((120, 160, 70), (75, 100, 70), k))
    grass(c, t, off * 0.7, 580, 70, 60, mix((90, 140, 60), (60, 85, 60), k), 7)
    m = lambda ch: sc.mouth(ch, t)
    ph = off / STRIDE
    pose = 'walk' if moving else 'sit'
    cat(c, 380, 625, WHISKERS, f=1, t=t, mouth=m('W'), pose=pose, walk=ph + 0.3, seed=1,
        look=(1, 0) if not moving else (0, 0))
    cat(c, 560, 625, LUNA, f=1, t=t, mouth=m('L'), pose=pose, walk=ph + 0.9, seed=3)
    rise = smooth(t / 0.7)
    eek = 18 * abs(math.sin(t * 12)) if t < sc.lines[0]['s'] + sc.lines[0]['dur'] else 0
    if moving:
        mouse(c, 790, 628, f=1, t=t, mouth=m('P'), walk=ph * 1.6)
    else:
        mouse(c, 790, 628 + 70 * (1 - rise), f=-1, t=t, mouth=m('P'), hop=eek)
    grass(c, t, off * 1.2, 650, 55, 80, mix((70, 125, 50), (45, 70, 50), k), 9)
    grass(c, t, off * 1.5, 725, 45, 110, mix((60, 110, 45), (40, 60, 45), k), 11)


# ---------------------------------------------------------------- pond

POND = (900, 585, 330, 85)
POND_COL = (22, 42, 85)


def pond_bg(c, t, moon_y, refl, frogs=False, croak=0.0):
    c.bg(grad(*NIGHT))
    stars(c, t, 160, 4, y1=440)
    if moon_y < 520:
        for k in range(4, 0, -1):
            c.circ(900, moon_y, 55 + k * 14, fill=mix((30, 34, 80), (75, 80, 130), 1 / k))
        c.circ(900, moon_y, 55, fill=(250, 245, 215))
        c.circ(880, moon_y - 15, 9, fill=(232, 226, 195))
        c.circ(920, moon_y + 15, 13, fill=(232, 226, 195))
    c.ell(640, 800, 1050, 360, fill=(22, 38, 48))
    for i in range(14):
        x = i * 100 + 20
        h = 70 + (i * 37) % 50
        c.poly([(x - 35, 460), (x, 460 - h), (x + 35, 460)], fill=(14, 28, 36))
    c.rect(0, 470, W, H, fill=(28, 58, 46))
    px, py, rx, ry = POND
    c.ell(px, py, rx + 10, ry + 8, fill=(40, 70, 55))
    c.ell(px, py, rx, ry, fill=POND_COL)
    if refl > 0:
        glow = mix(POND_COL, (230, 235, 205), refl)
        c.ell(px, py - 8, 50, 14, fill=mix(POND_COL, (120, 130, 150), refl))
        c.ell(px, py - 8, 36, 9, fill=glow)
        for k in range(5):
            w = 60 - k * 9
            dx = 8 * math.sin(t * 2 + k)
            c.line([(px - w + dx, py + 8 + k * 9), (px + w + dx, py + 8 + k * 9)], mix(POND_COL, glow, 0.7 - k * 0.1), 3)
    for x0 in (600, 625, 1200, 1225, 1245):
        c.line([(x0, 600), (x0 + 6 * math.sin(t + x0), 500)], (40, 80, 50), 4)
        c.ell(x0 + 6 * math.sin(t + x0), 510, 6, 16, fill=(95, 60, 40))
    if frogs:
        frog(c, 1080, 585, t, croak)
        frog(c, 760, 600, t, croak * 0.8)
    rnd = random.Random(8)
    for _ in range(9):
        bx, by = rnd.uniform(0, W), rnd.uniform(380, 560)
        sp = rnd.uniform(0.3, 0.8)
        c.circ(bx + 30 * math.sin(t * sp + bx), by + 20 * math.cos(t * sp * 1.3 + by), 3,
               fill=mix((40, 50, 40), (250, 245, 140), 0.5 + 0.5 * math.sin(t * 3 + bx)))


def water_front(c):
    px, py, rx, ry = POND
    c.chord(px, py, rx, ry, 0, 180, POND_COL)


def ripples(c, t, t0, n=3, strength=1.0):
    px, py = POND[0], POND[1] + 15
    for k in range(n):
        tau = (t - t0 - k * 0.5) % 2.5 if strength < 1 else t - t0 - k * 0.3
        if tau < 0:
            continue
        r = 40 + 110 * tau
        if r > 300:
            continue
        col = mix((140, 165, 220), POND_COL, r / 300)
        c.arc(px, py, r, r * 0.22, 0, 360, col, 3)


def splash(c, t, t0):
    tau = t - t0
    if not 0 <= tau < 1.6:
        return
    rnd = random.Random(3)
    for _ in range(34):
        a = math.radians(rnd.uniform(-165, -15))
        v = rnd.uniform(220, 480)
        x = POND[0] + math.cos(a) * v * tau
        y = POND[1] + math.sin(a) * v * tau + 0.5 * 900 * tau * tau
        if y < POND[1] + 20:
            r = rnd.uniform(4, 9) * (1 - tau / 1.6)
            c.ell(x, y, r, r * 1.3, fill=(170, 205, 255))


def sc_pond(c, t, sc):
    pm = sc.p('moonrise', t)
    moon_y = lerp(560, 160, smooth(pm))
    pond_bg(c, t, moon_y, smooth(pm * 1.2 - 0.2))
    m = lambda ch: sc.mouth(ch, t)
    pa = sc.p('arrive', t)
    walking = 0 < pa < 1
    for st, x0, x1, seed, ch in ((LUNA, -150, 420, 3, 'L'),):
        x, ph = walk_between(x0, x1, pa)
        cat(c, x, 625, st, f=1, t=t, mouth=m(ch), pose='walk' if walking else 'sit', walk=ph, seed=seed,
            look=(1, 0.6) if pm > 0.5 else (1, -1))
    x, ph = walk_between(-50, 280, pa)
    mouse(c, x, 630, f=1, t=t, mouth=m('P'), walk=ph if walking else None)

    pp = sc.p('pounce', t)
    if pp <= 0:
        x, ph = walk_between(-320, 580, pa)
        cat(c, x, 625, WHISKERS, f=1, t=t, mouth=m('W'), pose='walk' if walking else 'sit', walk=ph, seed=1,
            look=(1, 0.6) if pm > 0.5 else (0, 0), happy=t > sc.lines[2]['s'] and m('W') < 0.05 and pm >= 1)
    elif pp < 0.35:
        cat(c, 580, 625, WHISKERS, f=1, t=t, squash=1 - 0.25 * smooth(pp / 0.35), seed=1, look=(1, 1))
    elif pp < 1:
        u = (pp - 0.35) / 0.65
        x, y = hop(580, 625, 900, 660, u, 220)
        cat(c, x, y, WHISKERS, f=1, t=t, pose='jump', seed=1, look=(1, 1))
    else:
        bob = 3 * math.sin(t * 2)
        cat(c, 900, 668 + bob, WHISKERS, f=-1, t=t, mouth=m('W'), seed=1, wet=True,
            closed=t < sc.e('splash'))
        water_front(c)
        ripples(c, t, sc.e('pounce'), n=4)
        if t > sc.e('splash') + 1:
            ripples(c, t, sc.e('pounce'), n=2, strength=0.5)
    splash(c, t, sc.e('pounce'))


def sc_realize(c, t, sc):
    pl = sc.p('laugh', t)
    laughing = 0 < pl < 1
    croak = abs(math.sin(t * 9)) if laughing or t > sc.e('laugh') and t < sc.e('laugh') + 1 else 0
    pond_bg(c, t, 160, 1.0, frogs=True, croak=croak)
    m = lambda ch: sc.mouth(ch, t)
    lb = lambda ph: 12 * abs(math.sin(t * 9 + ph)) if laughing else 0
    lm = (0.6 + 0.4 * math.sin(t * 18)) if laughing else 0
    cat(c, 400, 625 - lb(0), LUNA, f=1, t=t, mouth=m('L') or lm, seed=3, happy=laughing)
    mouse(c, 265, 630, f=1, t=t, mouth=m('P') or lm, hop=lb(1), happy=laughing)
    lookup = sc.p('lookup', t)
    look = (0, -1) if 0 < lookup and t < sc.lines[1]['s'] + 2 else (-1, 0)
    if pl <= 0:
        bob = 3 * math.sin(t * 2)
        cat(c, 900, 668 + bob, WHISKERS, f=-1, t=t, mouth=m('W'), seed=1, wet=True, look=look)
        water_front(c)
        ripples(c, t, 0, n=2, strength=0.5)
    elif pl < 0.4:
        u = pl / 0.4
        x, y = hop(900, 668, 545, 625, u, 110)
        cat(c, x, y, WHISKERS, f=-1, t=t, pose='jump', seed=1, wet=True)
        water_front(c)
    else:
        cat(c, 545, 625 - lb(2), WHISKERS, f=-1, t=t, mouth=m('W') or lm, seed=1, wet=True,
            happy=laughing)


# ---------------------------------------------------------------- home

def sc_home(c, t, sc):
    sky(c, NIGHT, NIGHT, 0)
    stars(c, t, 40, 5, x0=185, x1=555, y0=115, y1=325)
    c.circ(470, 175, 34, fill=mix((40, 46, 98), (250, 245, 215), 1))
    c.circ(458, 166, 6, fill=(232, 226, 195))
    room(c, 'night')
    m = lambda ch: sc.mouth(ch, t)
    walk_end = sc.e('walkhome')
    pw = clamp(t / walk_end)
    pu = clamp((t - walk_end) / 1.2)
    spots = ((WHISKERS, -300, 330, 255, 1, 1, 'W'), (LUNA, -150, 520, 485, -1, 3, 'L'))
    for st, x0, x1, sx, sf, seed, ch in spots:
        if pw < 1:
            x, ph = walk_between(x0, x1, pw)
            cat(c, x, FLOOR, st, f=1, t=t, pose='walk', walk=ph, seed=seed)
        elif pu < 1:
            x, y = hop(x1, FLOOR, sx, SILL, pu, 120)
            cat(c, x, y, st, f=sf, t=t, pose='jump', seed=seed)
        else:
            cat(c, sx, SILL, st, f=sf, t=t, mouth=m(ch), pose='sleep', seed=seed)
    if pw < 1:
        x, ph = walk_between(-40, 440, pw)
        mouse(c, x, FLOOR, f=1, t=t, walk=ph)
    elif pu < 1:
        x, y = hop(440, FLOOR, 370, SILL - 4, pu, 140)
        mouse(c, x, y, f=1, t=t, s=1.0)
    else:
        mouse(c, 370, SILL - 4, f=1, t=t, mouth=m('P'), s=1.0, closed=True)
    if pu >= 1 and t > sc.s('quiet'):
        zzz(c, 300, 260, t)
        zzz(c, 440, 255, t + 1.3)
    pe = sc.p('end', t)
    if pe > 0:
        a = smooth(pe * 2.2)
        c.text(W / 2, 470, 'The End', font(FONT_TITLE, 120, 1), mix((70, 60, 110), (255, 235, 170), a),
               stroke=5 if a > 0.4 else 0, stroke_fill=(40, 25, 60))


DRAW = {
    'title': sc_title, 'morning': sc_morning, 'legend': sc_legend, 'garden': sc_garden,
    'meadow': sc_meadow, 'pond': sc_pond, 'realize': sc_realize, 'home': sc_home,
}
