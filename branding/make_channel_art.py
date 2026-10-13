"""YouTube channel art drawn with the film characters.

    python3 branding/make_channel_art.py   ->  branding/profile.png (800x800), branding/banner.png (2560x1440)

The banner keeps the cats and title inside YouTube's 1546x423 "safe area" (centre), which
is the only part shown on phones; the landmarks around it show on TVs and desktops.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import draw as D  # noqa: E402
from draw import Canvas, mix  # noqa: E402

OUT = D.OUT


def sky(c, w, h, stops):
    c.img.paste(D.gradient(w * D.SS, h * D.SS, stops), (0, 0))


# ------------------------------------------------------------ landmarks

def eiffel(c, x, y, s=1.0, col=(120, 90, 140)):
    c.push(x, y, s)
    c.poly([(-70, 0), (-18, -260), (18, -260), (70, 0), (40, 0), (0, -120), (-40, 0)], col)
    c.poly([(-18, -260), (-6, -420), (6, -420), (18, -260)], col)
    c.rect(-46, -130, 46, -116, col, r=2)
    c.rect(-24, -270, 24, -258, col, r=2)
    c.line([(0, -420), (0, -460)], col, 5)
    c.pop()


def big_ben(c, x, y, s=1.0, col=(150, 110, 120)):
    c.push(x, y, s)
    c.rect(-34, -330, 34, 0, col)
    c.rect(-40, -350, 40, -320, col)
    c.poly([(-36, -350), (0, -440), (36, -350)], col)
    c.circle(0, -285, 24, (255, 240, 200))
    c.line([(0, -285), (0, -302)], OUT, 3, cap=False)
    c.line([(0, -285), (12, -285)], OUT, 3, cap=False)
    c.pop()


def colosseum(c, x, y, s=1.0, col=(214, 170, 120)):
    c.push(x, y, s)
    c.poly([(-170, 0), (-170, -150), (120, -150), (170, -110), (170, 0)], col)
    for row, yy in enumerate((-125, -80, -35)):
        for k in range(7):
            ax = -150 + k * 44
            c.ellipse(ax + 14, yy + 8, 12, 16, mix(col, (90, 60, 50), 0.45), ol=None)
    c.pop()


def windmill(c, x, y, t, s=1.0, col=(190, 120, 90)):
    c.push(x, y, s)
    c.poly([(-36, 0), (-22, -150), (22, -150), (36, 0)], col)
    c.poly([(-28, -150), (0, -185), (28, -150)], (110, 80, 70))
    for k in range(4):
        a = t + k * math.pi / 2
        ex, ey = math.cos(a) * 120, -160 + math.sin(a) * 120
        c.stroke([(0, -160), (ex, ey)], (240, 230, 210), 10)
    c.circle(0, -160, 9, (110, 80, 70))
    c.pop()


def mountain(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-260, 0), (-30, -360), (40, -300), (260, 0)], (130, 140, 190))
    c.poly([(-30, -360), (-90, -265), (-50, -280), (-20, -250), (10, -290), (40, -300)], (250, 250, 255), ol=None)
    c.pop()


def pisa_like_tower(c, x, y, s=1.0, col=(240, 225, 200)):
    c.push(x, y, s)
    c.rect(-30, -260, 30, 0, col)
    for k in range(6):
        c.line([(-30, -40 * k - 20), (30, -40 * k - 20)], mix(col, (0, 0, 0), 0.25), 3, cap=False)
    c.ellipse(0, -265, 32, 10, col)
    c.pop()


def suitcase(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-90, -110, 90, 0, (200, 80, 70), r=14)
    c.rect(-30, -132, 30, -108, None, w=6, r=8)
    c.line([(-90, -55), (90, -55)], (150, 55, 50), 6, cap=False)
    c.circle(-50, -80, 14, (255, 220, 90), w=2)          # stickers
    c.rect(20, -95, 70, -65, (120, 190, 240), w=2, r=4)
    c.text(45, -80, "EU", 14, (255, 255, 255))
    c.pop()


# --------------------------------------------------------------- banner

def banner():
    W, H = 2560, 1440
    c = Canvas(size=(W, H))
    sky(c, W, H, [(0, (120, 190, 245)), (0.55, (255, 214, 170)), (0.75, (255, 196, 150)), (1, (255, 196, 150))])
    for x, y, s in ((300, 260, 2.2), (980, 180, 1.6), (1750, 230, 2.0), (2300, 150, 1.8)):
        D.cloud(c, x, y, s)
    c.circle(2180, 420, 90, (255, 236, 150), ol=None)
    # skyline of landmarks, left and right of the safe area
    mountain(c, 2370, 1180, 1.5)
    eiffel(c, 300, 1180, 1.4)
    big_ben(c, 470, 1180, 1.2)
    colosseum(c, 2020, 1180, 1.1)
    windmill(c, 110, 1180, 0.7, 1.1)
    pisa_like_tower(c, 2250, 1180, 1.1)
    # hills and ground
    pts = [(x, 1060 + 40 * math.sin(x / 260)) for x in range(0, W + 40, 40)]
    c.poly(pts + [(W, H), (0, H)], (130, 195, 110), ol=None)
    c.rect(0, 1180, W, H, (105, 175, 90), ol=None)
    rng = __import__("numpy").random.default_rng(3)
    for _ in range(160):
        D.flower(c, rng.uniform(0, W), rng.uniform(1190, H - 10),
                 [(250, 120, 150), (255, 230, 90), (180, 140, 250), (255, 255, 255)][rng.integers(4)],
                 rng.uniform(1.2, 1.8))
    # --- safe area: x 507..2053, y 508..931 ---
    c.rect(530, 540, 1555, 900, (255, 250, 240), w=6, r=60)
    c.text(1042, 655, "Whiskers & Luna", 100, (240, 140, 50), stroke=6, stroke_fill=(90, 50, 40))
    c.text(1042, 790, "Cat adventures around Europe", 58, (80, 110, 170))
    c.text(1042, 862, "New stories • Geography for kids", 38, (130, 120, 120))
    # characters on the right side of the safe area
    suitcase(c, 1790, 930, 1.6)
    D.cat(c, 1680, 760, D.WHISKERS, 1.55, 1, "sit", eyes="happy", seed=0.3)
    D.cat(c, 1905, 762, D.LUNA, 1.5, -1, "sit", look=(-1, 0), seed=1.7)
    D.mouse(c, 1790, 765, 2.2, 1, eyes="happy", proud=True)
    D.butterfly(c, 1640, 520, 0.3, 2.0)
    return c.finish()


# -------------------------------------------------------------- profile

def profile():
    S = 800
    c = Canvas(size=(S, S))
    sky(c, S, S, [(0, (120, 190, 245)), (0.62, (255, 214, 170)), (1, (255, 214, 170))])
    c.circle(610, 190, 60, (255, 236, 150), ol=None)
    D.cloud(c, 190, 170, 1.1)
    c.rect(0, 640, S, S, (105, 175, 90), ol=None)
    D.cat(c, 285, 690, D.WHISKERS, 2.25, 1, "sit", eyes="happy", seed=0.3)
    D.cat(c, 545, 692, D.LUNA, 2.15, -1, "sit", look=(-1, 0), seed=1.7)
    D.mouse(c, 410, 700, 2.6, 1, eyes="happy", proud=True)
    img = c.finish()
    # round mask preview is done by YouTube; keep the square image
    return img


if __name__ == "__main__":
    b, p = banner(), profile()
    b.save(os.path.join(HERE, "banner.png"))
    p.save(os.path.join(HERE, "profile.png"))
    print("saved", os.path.join(HERE, "banner.png"), b.size, os.path.join(HERE, "profile.png"), p.size)
