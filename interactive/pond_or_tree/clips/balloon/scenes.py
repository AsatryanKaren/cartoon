"""balloon: everyone climbs into Pip's balloon -- whoosh, up, up, up! High over the lake everything looks
tiny. Above the island, Pip (the bravest mouse in the meadow) slides down a rope, grabs the ball and is
pulled back up. They float home and land on the lawn at sunset -- "Home sweet home!"."""
import math

from PIL import Image

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix
from interactive.pond_or_tree import shared as S

BS = 1.25                     # balloon scale


def crew(tl, t, pip_on_rim=True, ball_in=False):
    def draw(c):
        happy = t >= tl.t("bl_got")
        D.cat(c, -24, -58, D.LUNA, 0.48, 1, "sit", t=t, mouth=tl.mouth("luna", t), seed=1.3,
              eyes="happy" if happy else "open", look=(1, 0.5))
        D.cat(c, 22, -60, D.WHISKERS, 0.48, 1, "sit", t=t, mouth=tl.mouth("whiskers", t), seed=0,
              eyes="wide" if tl.t("bl_tiny") <= t < tl.t("bl_tiny", 1) else ("happy" if happy else "open"),
              look=(1, 1) if tl.t("bl_tiny") <= t < tl.t("bl_over", 1) else (1, 0))
        if ball_in:
            S.ball(c, -2, -96, 14, 0.5)
        if pip_on_rim:
            D.mouse(c, 58, -90, 1.0, 1, t, mouth=tl.mouth("pip", t), proud=True,
                    eyes="happy" if happy else "open")
    return draw


def sky_bg():
    def make():
        return D.gradient(W * SS, H * SS, S.SKY)
    return S.cached("bl_sky", make)


def fly(tl, t):
    T = tl.t
    alt = S.smooth(t, [(0, 0), (T("bl_lift", 0.4), 0), (T("bl_rise", 1), 900)], r=0.4)
    img = sky_bg().copy()
    c = Canvas(img)
    # clouds slide down as we rise
    for k, (cx, cy, s) in enumerate(((200, 120, 0.9), (900, -200, 1.1), (520, -520, 0.8), (1100, 160, 0.7),
                                     (300, -800, 1.0))):
        D.cloud(c, cx + 20 * math.sin(t * 0.3 + k), cy + alt * 0.8, s)
    # the ground falls away
    if 300 + alt < H - 2:
        g0 = 300                                   # only the land and water, not the bg's own sky
        top = int(round((g0 + alt) * SS))
        part = S.lake_bg().crop((0, g0 * SS, W * SS, g0 * SS + H * SS - top))
        if part.size[1] > 0:
            mask = Image.new("L", part.size, 255)
            sky_part = S.lake_bg().crop((0, g0 * SS, W * SS, g0 * SS + 1)).resize(part.size)
            # keep the sky pixels of the ground strip transparent (they sit above the hills)
            import numpy as np
            a = np.asarray(part).astype(int)
            b = np.asarray(sky_part).astype(int)
            mask = Image.fromarray(((np.abs(a - b).sum(axis=2) > 12) * 255).astype("uint8"))
            c.img.paste(part, (0, top), mask)
    # far below: the lake, with the island drifting into view
    if alt > 700:
        band = 560 + (900 - alt)
        c.rect(0, band, W, H, S.WATER, ol=None)
        for k in range(6):
            c.line([(0, band + 14 + k * 24), (W, band + 14 + k * 24)], mix(S.WATER, S.WATER_L, 0.25), 2, cap=False)
        ix = S.smooth(t, [(T("bl_tiny"), 1500), (T("bl_over", 1), 640)], r=0.4)
        iy = band + 92
        c.ellipse(ix, iy, 170, 34, (214, 196, 140), ol=(120, 100, 70), w=3)
        c.ellipse(ix, iy - 8, 130, 22, (130, 190, 100), ol=None)
        D.tree(c, ix - 80, iy - 10, 0.4)
        if t < T("bl_rope", 0.5):
            S.ball(c, ix + 40, iy - 18, 14, 0.2)
    # the balloon
    bx = S.smooth(t, [(T("bl_lift", 0.4), 300), (T("bl_rise", 1), 640)], r=0.4)
    by = 592 - min(alt, 120) + 6 * math.sin(t * 1.2)
    flame = 1.0 if (T("bl_lift", 0.2) <= t < T("bl_rise", 0.6)) else 0.0
    rope = tl.prog("bl_rope", t, 0.0, 0.25) if t < T("bl_rope", 0.9) else 0.0
    pip_down = T("bl_rope", 0.2) <= t < T("bl_rope", 0.9)
    got = t >= T("bl_rope", 0.9)
    # rope and Pip on it (behind the basket's front)
    if T("bl_rope") <= t < T("bl_rope", 0.9):
        bottom_y = 560 + 92 - 20
        ry = lerp(by, bottom_y, ease(rope) if t < T("bl_rope", 0.55) else
                  1 - ease(tl.prog("bl_rope", t, 0.55, 0.9)) * 1.0)
        c.line([(bx + 30, by - 10), (bx + 30, ry)], (150, 110, 70), 4, cap=False)
        if pip_down:
            if t < T("bl_rope", 0.45):
                py = lerp(by - 20, bottom_y, ease(tl.prog("bl_rope", t, 0.2, 0.45)))
            elif t < T("bl_rope", 0.55):
                py = bottom_y
            else:
                py = ry
            D.mouse(c, bx + 30, py + 10, 1.2, 1, t, proud=True, eyes="happy" if t >= T("bl_rope", 0.5) else "open")
            if t >= T("bl_rope", 0.5):
                S.ball(c, bx + 48, py - 6, 14, t * 3)
    S.balloon(c, bx, by, BS, t, flame=flame, inside=crew(tl, t, pip_on_rim=not pip_down, ball_in=got))
    # camera: a closer shot that keeps the basket (and the island below) in view
    w, h = 914, 514
    x0 = int(clamp(bx - w / 2, 0, W - w))
    y0 = H - h
    img = c.img.crop((x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS)).resize((W * SS, H * SS))
    return Canvas(img)


def home(tl, t):
    T = tl.t
    s0 = tl.scenes["home"][0]
    camx = S.smooth(t, [(s0, 920), (T("bl_float", 0.65), 920), (T("bl_home", 1), 520)], r=0.4)
    c = S.view(S.garden_bg(True), camx)
    c.push(-camx, 0)
    S.water_glints(c, S.STREAM_X + 100, S.GW, 610, 700, t, n=20, col=(255, 220, 170))
    u = tl.prog("bl_float", t, 0.0, 0.55)
    bx = lerp(1900, 1560, ease(u))
    by = lerp(150, S.GY, ease(u))
    flame = 1.0 if 0.2 < u < 0.45 else 0.0
    out = t >= T("bl_float", 0.7)
    S.balloon(c, bx, by, BS, t, flame=flame, inside=None if out else crew(tl, t, True, True))
    if out:
        walk0 = T("bl_float", 0.75)

        def walker(x0, delay):
            return S.smooth(t, [(walk0 + delay, x0), (T("bl_home", 1) + delay, x0 - 560)], r=0.3)
        moving = walk0 <= t < T("bl_home", 1) + 0.4
        end = t >= T("bl_end")
        wx, lx, px = walker(1440, 0.0), walker(1620, 0.15), walker(1730, 0.3)
        D.cat(c, lx, S.GY, D.LUNA, 1.0, -1, "walk" if moving else "stand", walk=-lx / 12 if moving else 0, t=t,
              mouth=tl.mouth("luna", t), seed=1.3, eyes="happy" if end else "open")
        D.cat(c, wx, S.GY, D.WHISKERS, 1.0, -1, "walk" if moving else "stand", walk=-wx / 12 if moving else 0,
              t=t, mouth=tl.mouth("whiskers", t), seed=0, eyes="happy" if t >= T("bl_home") else "open")
        S.ball(c, wx - 90, S.GY - 22, 22, -wx / 22)
        D.mouse(c, px, S.GY, 1.4, -1, t, walk=-px / 6 if moving else 0, mouth=tl.mouth("pip", t),
                eyes="happy" if end else "open")
    c.pop()
    return c


SCENE_FUNCS = {"fly": fly, "home": home}
