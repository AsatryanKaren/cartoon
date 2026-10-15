"""boat: everyone jumps into Pip's little rowboat. Whiskers rows them round in circles ("just warming
up!"), then across to the island, where Luna scoops up the ball. They row home down the stream and
step out at the bottom of the garden at sunset -- "Home sweet home!"."""
import math

import draw as D
from draw import ease, lerp, clamp, mix
from interactive.pond_or_tree import shared as S

ISL_BALL = (2030, 586)
BOAT_Y = 652


def crew(tl, t, rowing, has_ball, scoop=0.0):
    def draw(c):
        D.mouse(c, -96, -36, 1.25, 1, t, mouth=tl.mouth("pip", t), proud=True,
                eyes="happy" if t >= tl.t("b_hooray") else "open")
        D.cat(c, -18, -30, D.WHISKERS, 0.6, 1, "sit", t=t, mouth=tl.mouth("whiskers", t), seed=0,
              eyes="happy" if t >= tl.t("b_got") else "open", look=(1, 0),
              head_dy=6 * math.sin(t * 5) if rowing else 0)
        D.cat(c, 70 + 14 * scoop, -30, D.LUNA, 0.6, 1, "sit", t=t, mouth=tl.mouth("luna", t), seed=1.3,
              eyes="happy" if t >= tl.t("b_got") else "open", look=(1, 0.4), head_dy=10 * scoop)
        if has_ball:
            S.ball(c, 100, -78, 18, 0.4)
    return draw


def row(tl, t):
    T = tl.t
    bx = S.smooth(t, [(0, 640), (T("b_push"), 640), (T("b_narr", 1), 800), (T("b_row", 1), 1080),
                      (T("b_cross"), 1080), (T("b_cross", 1), 1830)], r=0.35)
    camx = clamp(bx - 560, 0, S.LW_ - S.W)
    c = S.lake_view(camx)
    c.push(-camx, 0)
    S.water_glints(c, 560, 2600, 660, 710, t, n=40)
    rowing = T("b_narr", 0.3) <= t < T("b_got")
    got = t >= T("b_got", 0.3)
    # ball on the island until Luna scoops it up
    if not got:
        S.ball(c, ISL_BALL[0], ISL_BALL[1], 22, 0.2)
    scoop = math.sin(math.pi * tl.prog("b_got", t, 0, 0.6)) if T("b_got") <= t < T("b_got", 0.6) else 0.0
    # spin round in circles
    spin = tl.prog("b_circle", t, 0.1, 1.0) * 0.6 + tl.prog("b_warm", t, 0.0, 0.8) * 0.4
    k = math.cos(2 * math.pi * 2 * spin)
    bob = 3 * math.sin(t * 1.8)
    c.push(bx, BOAT_Y + bob)
    ox, oy, sx, sy = c.tf[-1]
    c.tf[-1] = (ox, oy, sx * (k if abs(k) > 0.06 else 0.06 * (1 if k >= 0 else -1)), sy)
    oar = 0.5 + 0.55 * math.sin(t * 5) if rowing else 0.9
    S.rowboat(c, 0, 0, 1.0, inside=crew(tl, t, rowing, got, scoop), oar=oar)
    c.pop()
    # little ripples at the stern while rowing
    if rowing:
        for j in range(2):
            r = 30 + 60 * ((t * 0.8 + j * 0.5) % 1.0)
            c.ellipse(bx - 150, BOAT_Y + 8, r, r * 0.2, None, ol=S.WATER_L, w=2)
    c.pop()
    # camera: closer on the boat
    sx0 = bx - camx - 474
    x0, y0, w = int(clamp(sx0, 0, S.W - 948)), 187, 948
    img = c.img.crop((x0 * S.SS, y0 * S.SS, (x0 + w) * S.SS, (y0 + 533) * S.SS)).resize((S.W * S.SS, S.H * S.SS))
    return S.Canvas(img)


def home(tl, t):
    T = tl.t
    s0 = tl.scenes["home"][0]
    camx = S.smooth(t, [(s0, 920), (T("b_float", 0.6), 920), (T("b_home", 1), 520)], r=0.4)
    c = S.view(S.garden_bg(True), camx)
    c.push(-camx, 0)
    S.water_glints(c, S.STREAM_X + 100, S.GW, 610, 700, t, n=20, col=(255, 220, 170))
    bx = S.smooth(t, [(s0, 2450), (T("b_float", 0.5), 1940)], r=0.4)
    hop = tl.prog("b_float", t, 0.55, 0.8)
    out = hop >= 0.5
    walk0 = T("b_float", 0.8)

    def walker(x0, delay, until=None):
        return S.smooth(t, [(walk0 + delay, x0), (T("b_home", 1) + delay, x0 - 640)], r=0.3)

    if not out:
        S.rowboat(c, bx, 640 + 3 * math.sin(t * 1.8), 1.0, inside=crew(tl, t, False, True))
        c.pop()
        return c
    S.rowboat(c, bx, 640 + 3 * math.sin(t * 1.8), 1.0)
    end = t >= T("b_end")
    # Whiskers nudges the ball home with his nose
    wx = walker(1760, 0.0)
    lx = walker(1930, 0.15)
    px = walker(2060, 0.3)
    moving = walk0 <= t < T("b_home", 1) + 0.3
    D.cat(c, lx, S.GY, D.LUNA, 1.0, -1, "walk" if moving else "stand", walk=-lx / 12 if moving else 0, t=t,
          mouth=tl.mouth("luna", t), seed=1.3, eyes="happy" if end else "open")
    D.cat(c, wx, S.GY, D.WHISKERS, 1.0, -1, "walk" if moving else "stand", walk=-wx / 12 if moving else 0,
          t=t, mouth=tl.mouth("whiskers", t), seed=0, eyes="happy" if t >= T("b_home") else "open")
    S.ball(c, wx - 90, S.GY - 22, 22, -wx / 22)
    D.mouse(c, px, S.GY, 1.4, -1, t, walk=-px / 6 if moving else 0, mouth=tl.mouth("pip", t),
            eyes="happy" if end else "open")
    c.pop()
    return c


SCENE_FUNCS = {"row": row, "home": home}
