import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
S = 2  # supersampling factor
OUT = (45, 35, 45)

FONT_SUB = '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'
FONT_TITLE = '/System/Library/Fonts/Supplemental/ChalkboardSE.ttc'

WHISKERS = {'fur': (242, 150, 58), 'belly': (255, 228, 185), 'stripe': (204, 104, 34),
            'eye': (130, 190, 70), 'inner': (250, 170, 180)}
LUNA = {'fur': (150, 156, 172), 'belly': (242, 242, 248), 'stripe': None,
        'eye': (240, 190, 50), 'inner': (250, 175, 190)}


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def lerp(a, b, k):
    return a + (b - a) * k


def smooth(k):
    k = clamp(k)
    return k * k * (3 - 2 * k)


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, clamp(k))) for a, b in zip(c1, c2))


@lru_cache(maxsize=None)
def font(path, size, index=0):
    return ImageFont.truetype(path, int(size * S), index=index)


@lru_cache(maxsize=None)
def grad(top, bot):
    k = np.linspace(0, 1, H * S, dtype=np.float32)[:, None]
    col = np.array(top, np.float32) * (1 - k) + np.array(bot, np.float32) * k
    arr = np.repeat(col[:, None, :], W * S, axis=1).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')


class C:
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    def ell(self, cx, cy, rx, ry, fill=None, outline=None, w=0):
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
                       fill=fill, outline=outline, width=int(w * S))

    def circ(self, cx, cy, r, fill=None, outline=None, w=0):
        self.ell(cx, cy, r, r, fill, outline, w)

    def poly(self, pts, fill=None, outline=None, w=0):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline, width=int(w * S))

    def line(self, pts, fill, w):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, int(w * S)), joint='curve')

    def tline(self, pts, fill, w):
        self.line(pts, fill, w)
        for x, y in (pts[0], pts[-1]):
            self.circ(x, y, w / 2, fill=fill)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=0, r=0):
        box = [x0 * S, y0 * S, x1 * S, y1 * S]
        if r:
            self.d.rounded_rectangle(box, radius=r * S, fill=fill, outline=outline, width=int(w * S))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(w * S))

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w):
        self.d.arc([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], a0, a1,
                   fill=fill, width=max(1, int(w * S)))

    def chord(self, cx, cy, rx, ry, a0, a1, fill):
        self.d.chord([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], a0, a1, fill=fill)

    def text(self, x, y, s, fnt, fill, anchor='mm', stroke=0, stroke_fill=None):
        self.d.text((x * S, y * S), s, font=fnt, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=stroke_fill)

    def bg(self, img):
        self.img.paste(img)


# ---------------------------------------------------------------- characters

def blink_closed(t, seed):
    return (t * 0.9 + seed * 1.7) % 3.7 < 0.13


def face(c, hx, hy, r, f, st, mouth, closed, look, t, seed, happy=False, whisk=True):
    belly = st['belly']
    fx = f * r * 0.12
    c.ell(hx + fx - r * 0.2, hy + r * 0.35, r * 0.3, r * 0.24, fill=belly)
    c.ell(hx + fx + r * 0.2, hy + r * 0.35, r * 0.3, r * 0.24, fill=belly)
    shut = closed or blink_closed(t, seed)
    for sx in (-1, 1):
        ex, ey = hx + fx + sx * r * 0.38, hy - r * 0.06
        if happy:
            c.arc(ex, ey + r * 0.06, r * 0.17, r * 0.15, 200, 340, OUT, r * 0.07)
        elif shut:
            c.arc(ex, ey - r * 0.04, r * 0.17, r * 0.12, 20, 160, OUT, r * 0.07)
        else:
            c.ell(ex, ey, r * 0.2, r * 0.25, fill=(255, 255, 255), outline=OUT, w=r * 0.05)
            ix = ex + look[0] * r * 0.06 + f * r * 0.04
            iy = ey + look[1] * r * 0.08
            c.ell(ix, iy, r * 0.14, r * 0.19, fill=st['eye'])
            c.ell(ix, iy, r * 0.06, r * 0.15, fill=(20, 20, 25))
            c.circ(ix - r * 0.05, iy - r * 0.08, r * 0.045, fill=(255, 255, 255))
    nx, ny = hx + fx, hy + r * 0.2
    c.poly([(nx - r * 0.1, ny - r * 0.05), (nx + r * 0.1, ny - r * 0.05), (nx, ny + r * 0.07)],
           fill=(230, 115, 140), outline=OUT, w=r * 0.03)
    if mouth > 0.08:
        my = ny + r * 0.2 + r * 0.08 * mouth
        mry = r * 0.05 + r * 0.15 * mouth
        c.ell(nx, my, r * 0.13 + r * 0.03 * mouth, mry, fill=(125, 35, 50), outline=OUT, w=r * 0.04)
        if mouth > 0.4:
            c.ell(nx, my + mry * 0.45, r * 0.08, mry * 0.4, fill=(240, 120, 140))
    else:
        c.arc(nx - r * 0.07, ny + r * 0.1, r * 0.07, r * 0.07, 0, 180, OUT, r * 0.04)
        c.arc(nx + r * 0.07, ny + r * 0.1, r * 0.07, r * 0.07, 0, 180, OUT, r * 0.04)
    if whisk:
        for sx in (-1, 1):
            for k in range(3):
                x0 = nx + sx * r * 0.32
                y0 = ny + r * 0.1 + k * r * 0.07
                c.line([(x0, y0), (x0 + sx * r * 0.8, y0 - r * 0.12 + k * r * 0.14)], (60, 50, 60), r * 0.025)


def head(c, hx, hy, r, f, st, mouth, closed, look, t, seed, happy=False, sil=False, tilt=0.0):
    fur = st['fur']
    for sx in (-1, 1):
        base_out = (hx + sx * r * 0.82, hy - r * 0.35)
        tip = (hx + sx * r * 0.7 + tilt * r * 0.3, hy - r * 1.5)
        base_in = (hx + sx * r * 0.1, hy - r * 0.9)
        c.poly([base_out, tip, base_in], fill=fur, outline=OUT, w=r * 0.07)
        if not sil:
            c.poly([(lerp(base_out[0], tip[0], 0.25), lerp(base_out[1], tip[1], 0.25)),
                    (lerp(tip[0], hx + sx * r * 0.5, 0.2), lerp(tip[1], hy, 0.2)),
                    (lerp(base_in[0], tip[0], 0.25), lerp(base_in[1], tip[1], 0.25))], fill=st['inner'])
    c.ell(hx, hy, r * 1.05, r, fill=fur, outline=OUT, w=r * 0.07)
    if sil:
        return
    if st['stripe']:
        for k in (-1, 0, 1):
            c.tline([(hx + k * r * 0.22, hy - r * 0.95), (hx + k * r * 0.18, hy - r * 0.62)], st['stripe'], r * 0.12)
    face(c, hx, hy, r, f, st, mouth, closed, look, t, seed, happy)


def tail(c, pts, fur, w):
    c.tline(pts, OUT, w + 5)
    c.tline(pts, fur, w)


def cat(c, x, y, st, f=1, t=0.0, mouth=0.0, pose='sit', walk=0.0, s=1.0, look=(0, 0), seed=0,
        sil=False, squash=1.0, happy=False, closed=False, wet=False):
    fur, belly, stripe = st['fur'], st['belly'], st['stripe']
    if sil:
        st = dict(st, belly=fur, inner=fur, stripe=None)
        belly, stripe = fur, None

    def P(dx, dy):
        return x + f * dx * s, y + dy * s * squash

    bob = 2 * math.sin(t * 14) * mouth
    if pose == 'sit':
        wag = math.sin(t * 2.2 + seed)
        tail(c, [P(-35 - 55 * u + 10 * u * wag, -14 - 85 * u ** 1.6) for u in np.linspace(0, 1, 12)], fur, 14 * s)
        bx, by = P(0, -56)
        c.ell(bx, by, 46 * s, 57 * s * squash, fill=fur, outline=OUT, w=4 * s)
        if not sil:
            ex, ey = P(12, -50)
            c.ell(ex, ey, 22 * s, 38 * s * squash, fill=belly)
            if stripe:
                for k in range(3):
                    sx, sy = P(-30, -80 + k * 20)
                    c.tline([(sx, sy), (sx + f * 14 * s, sy + 4 * s)], stripe, 7 * s)
        hx, hy = P(-20, -24)
        c.ell(hx, hy, 26 * s, 25 * s * squash, fill=fur, outline=OUT, w=4 * s)
        for dx in (6, 28):
            px, py = P(dx, -6)
            c.ell(px, py, 14 * s, 8 * s, fill=belly, outline=OUT, w=3 * s)
        hx, hy = P(14, -124)
        head(c, hx, hy + bob, 40 * s, f, st, mouth, closed, look, t, seed, happy, sil)
    elif pose in ('walk', 'jump'):
        wag = math.sin(t * 3 + seed)
        tail(c, [P(-60 - 30 * u, -64 - 65 * u + 14 * u * wag) for u in np.linspace(0, 1, 12)], fur, 13 * s)
        legs = [(-44, math.pi, True), (32, 0, True), (-26, 0, False), (50, math.pi, False)]
        def leg(lx, ph, far):
            col = mix(fur, OUT, 0.25) if far else fur
            if pose == 'walk':
                sw = 14 * math.sin(2 * math.pi * walk + ph)
                lift = max(0, math.sin(2 * math.pi * walk + ph + math.pi / 2)) * 5
                top, foot = P(lx, -48), P(lx + sw, -6 - lift)
            else:
                d = 26 if lx > 0 else -26
                top, foot = P(lx, -48), P(lx + d, -22)
            c.tline([top, foot], OUT, 21 * s)
            c.tline([top, foot], col, 15 * s)
            c.ell(foot[0], foot[1], 11 * s, 7 * s, fill=belly if not far else col, outline=OUT, w=3 * s)
        for l in legs:
            if l[2]:
                leg(*l)
        bx, by = P(0, -60)
        c.ell(bx, by, 66 * s, 35 * s, fill=fur, outline=OUT, w=4 * s)
        if not sil:
            ex, ey = P(8, -40)
            c.ell(ex, ey, 40 * s, 12 * s, fill=belly)
            if stripe:
                for k in range(3):
                    sx, sy = P(-30 + k * 20, -92)
                    c.tline([(sx, sy), (sx - f * 3 * s, sy + 16 * s)], stripe, 7 * s)
        for l in legs:
            if not l[2]:
                leg(*l)
        hb = 3 * math.sin(4 * math.pi * walk) if pose == 'walk' else 0
        hx, hy = P(62, -104)
        head(c, hx, hy + hb + bob, 38 * s, f, st, mouth, closed, look, t, seed, happy, sil)
    elif pose == 'sleep':
        breathe = 1 + 0.03 * math.sin(t * 2 + seed)
        bx, by = P(0, -30)
        c.ell(bx, by, 72 * s, 31 * s * breathe, fill=fur, outline=OUT, w=4 * s)
        if stripe and not sil:
            for k in range(3):
                sx, sy = P(-35 + k * 22, -58)
                c.tline([(sx, sy), (sx - f * 2 * s, sy + 15 * s)], stripe, 7 * s)
        tail(c, [P(-62 + 115 * u, -8 + 5 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 12)], fur, 13 * s)
        hx, hy = P(58, -36)
        head(c, hx, hy, 33 * s, f, st, mouth, True, look, t, seed, False, sil)
    if wet and not sil:
        hx, hy = P(14, -124) if pose == 'sit' else P(62, -104)
        for k in range(3):
            ph = (t * 0.8 + k * 0.33) % 1
            dx = (-30 + k * 30) * s
            c.ell(hx + dx, hy + 20 * s + ph * 60 * s, 4 * s, 6 * s, fill=(120, 170, 240))


def mouse(c, x, y, f=1, t=0.0, mouth=0.0, walk=None, s=1.2, hop=0.0, closed=False, happy=False):
    grey, light, pink = (168, 168, 182), (218, 218, 228), (240, 160, 175)
    if walk is not None:
        hop += abs(math.sin(math.pi * walk * 2)) * 4

    def P(dx, dy):
        return x + f * dx * s, y + dy * s - hop

    c.tline([P(-28 - 45 * u, -10 - 22 * math.sin(math.pi * u * 1.3) + 4 * math.sin(t * 3 + u * 5))
             for u in np.linspace(0, 1, 10)], pink, 4 * s)
    for dx in (-12, 14):
        px, py = P(dx, -3)
        c.ell(px, py, 8 * s, 4 * s, fill=pink, outline=OUT, w=2 * s)
    bx, by = P(0, -22)
    c.ell(bx, by, 30 * s, 22 * s, fill=grey, outline=OUT, w=3 * s)
    ex, ey = P(8, -15)
    c.ell(ex, ey, 16 * s, 11 * s, fill=light)
    ex, ey = P(12, -56)
    c.circ(ex, ey, 13 * s, fill=grey, outline=OUT, w=3 * s)
    c.circ(ex, ey, 8 * s, fill=pink)
    hx, hy = P(28, -36)
    c.ell(hx, hy, 21 * s, 17 * s, fill=grey, outline=OUT, w=3 * s)
    ex, ey = P(28, -58)
    c.circ(ex, ey, 13 * s, fill=grey, outline=OUT, w=3 * s)
    c.circ(ex, ey, 8 * s, fill=pink)
    ex, ey = P(34, -40)
    if happy:
        c.arc(ex, ey + 2 * s, 5 * s, 4 * s, 200, 340, OUT, 2 * s)
    elif closed or blink_closed(t, 5):
        c.arc(ex, ey - 1 * s, 5 * s, 3 * s, 20, 160, OUT, 2 * s)
    else:
        c.circ(ex, ey, 5 * s, fill=(20, 20, 25))
        c.circ(ex - 1.5 * s, ey - 2 * s, 1.6 * s, fill=(255, 255, 255))
    nx, ny = P(49, -34)
    c.circ(nx, ny, 4 * s, fill=(210, 90, 120))
    for k in (-1, 0, 1):
        c.line([P(44, -32), P(62, -36 + k * 6)], (80, 80, 90), 1.2 * s)
    if mouth > 0.08:
        mx, my = P(40, -26)
        c.ell(mx, my, 4 * s, (2 + 4 * mouth) * s, fill=(125, 35, 50))


def fish(c, x, y, s, body, glow=None):
    if glow:
        for k in range(3, 0, -1):
            c.ell(x, y, (66 + k * 10) * s, (34 + k * 10) * s, fill=mix(glow[1], glow[0], k / 4))
    c.poly([(x - 50 * s, y), (x - 88 * s, y - 30 * s), (x - 80 * s, y), (x - 88 * s, y + 30 * s)],
           fill=body, outline=OUT, w=3 * s)
    c.ell(x, y, 60 * s, 30 * s, fill=body, outline=OUT, w=3 * s)
    for k in range(3):
        c.arc(x - 18 * s + k * 16 * s, y, 10 * s, 16 * s, 300, 60, mix(body, OUT, 0.35), 2 * s)
    c.circ(x + 34 * s, y - 6 * s, 6 * s, fill=(255, 255, 255), outline=OUT, w=2 * s)
    c.circ(x + 35 * s, y - 6 * s, 3 * s, fill=(20, 20, 25))
    c.arc(x + 48 * s, y + 6 * s, 6 * s, 4 * s, 90, 200, OUT, 2 * s)


def butterfly(c, x, y, t):
    flap = abs(math.sin(t * 14))
    for sx in (-1, 1):
        c.ell(x + sx * 12 * flap, y - 6, 12 * flap + 2, 10, fill=(250, 120, 180), outline=OUT, w=2)
        c.ell(x + sx * 9 * flap, y + 8, 8 * flap + 2, 7, fill=(255, 200, 80), outline=OUT, w=2)
    c.ell(x, y, 3, 12, fill=OUT)


def frog(c, x, y, t, croak):
    c.ell(x, y + 6, 46, 11, fill=(60, 130, 70), outline=(30, 70, 40), w=2)
    c.ell(x, y - 8, 24, 15, fill=(95, 175, 85), outline=OUT, w=3)
    if croak > 0:
        c.ell(x + 2, y + 2, 10 + 8 * croak, 6 + 6 * croak, fill=(205, 235, 150), outline=OUT, w=2)
    for sx in (-1, 1):
        c.circ(x + sx * 11, y - 24, 8, fill=(95, 175, 85), outline=OUT, w=3)
        c.circ(x + sx * 11, y - 24, 4, fill=(20, 20, 25))


def cloud(c, x, y, s=1.0, col=(255, 255, 255)):
    for dx, dy, r in ((-40, 5, 30), (0, -12, 40), (40, 5, 30), (15, 10, 32), (-15, 10, 30)):
        c.circ(x + dx * s, y + dy * s, r * s, fill=col)


def stars(c, t, n, seed, x0=0, x1=W, y0=0, y1=450, k=1.0):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        ph = rnd.uniform(0, 6.28)
        b = (0.55 + 0.45 * math.sin(t * rnd.uniform(1, 3) + ph)) * k
        r = rnd.choice((1.2, 1.6, 2.2))
        c.circ(x, y, r, fill=mix((40, 40, 90), (255, 255, 230), b))


def zzz(c, x, y, t):
    fnt_cache = {}
    for k in range(3):
        ph = (t * 0.45 + k / 3) % 1
        size = int(18 + 22 * ph)
        if size not in fnt_cache:
            fnt_cache[size] = font(FONT_SUB, size)
        c.text(x + 25 * ph + 10 * math.sin(ph * 6), y - 90 * ph, 'z', fnt_cache[size],
               mix((255, 255, 255), (180, 200, 255), ph), stroke=2, stroke_fill=(90, 90, 140))


# ---------------------------------------------------------------- room

@lru_cache(maxsize=None)
def room_layer(variant):
    img = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    c = C(img)
    wall, stripe = (250, 232, 200), (243, 222, 186)
    c.rect(0, 0, W, 520, fill=wall)
    for x in range(0, W, 80):
        c.rect(x, 0, x + 30, 520, fill=stripe)
    c.rect(0, 505, W, 525, fill=(205, 160, 120))
    c.rect(0, 525, W, H, fill=(196, 136, 86))
    for i, y in enumerate((560, 610, 670)):
        c.line([(0, y), (W, y)], (170, 112, 68), 3)
        for x in range(i * 90, W, 260):
            c.line([(x, y - (50 if i else 35)), (x, y)], (170, 112, 68), 3)
    c.rect(180, 110, 560, 330, fill=(0, 0, 0, 0))
    c.rect(174, 104, 566, 336, outline=(255, 255, 255), w=12)
    c.line([(370, 110), (370, 330)], (255, 255, 255), 9)
    c.line([(180, 220), (560, 220)], (255, 255, 255), 9)
    for sx, x in ((1, 150), (-1, 590)):
        c.poly([(x, 80), (x + sx * 70, 80), (x + sx * 40, 250), (x + sx * 55, 370), (x, 370)],
               fill=(205, 75, 90), outline=(150, 50, 65), w=3)
        c.line([(x + sx * 25, 85), (x + sx * 18, 365)], (175, 55, 72), 3)
    c.rect(120, 70, 620, 82, fill=(150, 100, 70), r=5)
    c.rect(150, 326, 590, 346, fill=(235, 215, 195), outline=(170, 140, 120), w=3, r=4)
    c.rect(760, 150, 930, 275, fill=(170, 120, 70), r=6)
    c.rect(772, 162, 918, 263, fill=(180, 220, 245))
    fish(c, 850, 213, 0.6, (250, 170, 70))
    c.ell(640, 645, 290, 46, fill=(110, 140, 200))
    c.ell(640, 645, 230, 32, fill=(150, 175, 230))
    c.poly([(855, 590), (945, 590), (932, 616), (868, 616)], fill=(220, 60, 70), outline=OUT, w=3)
    c.ell(900, 590, 45, 9, fill=(140, 35, 50), outline=OUT, w=3)
    if variant == 'night':
        arr = np.asarray(img).astype(np.float32)
        arr[..., :3] *= np.array([0.42, 0.42, 0.62], np.float32)
        img = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    elif variant == 'afternoon':
        arr = np.asarray(img).astype(np.float32)
        arr[..., :3] = np.minimum(255, arr[..., :3] * np.array([1.02, 0.95, 0.85], np.float32))
        img = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    return img


def room(c, variant):
    c.img.paste(room_layer(variant), (0, 0), room_layer(variant))


# ---------------------------------------------------------------- subtitles

def subtitle(c, ln, names):
    if not ln:
        return
    fnt = font(FONT_SUB, 30)
    who = names[ln['ch']]
    text = (who + ': ' if who else '') + ln['text']
    words, rows, cur = text.split(), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if fnt.getlength(trial) / S > 1100 and cur:
            rows.append(cur)
            cur = wd
        else:
            cur = trial
    rows.append(cur)
    col = (255, 240, 190) if ln['ch'] == 'N' else (255, 255, 255)
    y = 690 - (len(rows) - 1) * 38
    for r in rows:
        c.text(W / 2, y, r, fnt, col, stroke=3, stroke_fill=(20, 15, 30))
        y += 38
