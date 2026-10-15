"""ending: home on the windowsill that evening, Whiskers hugging his ball. Then Whiskers and Luna turn to
the viewer: "You helped us choose! Thank you, friend!", Luna's moral, and Pip says bye bye. The End."""
import math

from PIL import ImageFilter

import draw as D
from draw import Canvas, W, H, SS, ease, mix, clamp
from films.moonfish.scenes import room
from interactive.pond_or_tree import shared as S


def sill(tl, t):
    T = tl.t
    c = Canvas(room(True).copy())
    c.tint = ((30, 36, 90), 0.18)
    D.cat(c, 800, 372, D.LUNA, 0.8, 1, "sit", t=t, mouth=tl.mouth("luna", t), seed=1.3,
          eyes="happy" if t < T("e_never") else "open", look=(1, 0.3))
    S.ball(c, 880, 352, 20, 0.3)
    D.cat(c, 950, 372, D.WHISKERS, 0.8, -1, "sit", t=t, mouth=tl.mouth("whiskers", t), seed=0,
          eyes="happy" if t < T("e_never") else "open", look=(1, 0.6), head_dy=6)
    D.mouse(c, 1040, 372, 1.0, -1, t, mouth=tl.mouth("pip", t),
            eyes="happy" if t >= T("e_never", 0.8) else "open")
    c.tint = None
    if t < T("e_never"):
        # little hearts float up from the hug
        for k in range(3):
            u = ((t * 0.4) + k / 3) % 1.0
            x, y = 880 + 30 * math.sin(t + k * 2), 320 - 70 * u
            col = mix((255, 120, 150), (60, 66, 120), u)
            c.circle(x - 4, y, 5, col, ol=None)
            c.circle(x + 4, y, 5, col, ol=None)
            c.poly([(x - 9, y + 2), (x + 9, y + 2), (x, y + 12)], col, ol=None)
    x0, y0 = 610, 110
    return Canvas(c.img.crop((x0 * SS, y0 * SS, (x0 + W // 2) * SS, (y0 + H // 2) * SS)).resize((W * SS, H * SS)))


def thanks_bg():
    def make():
        img = room(True).crop((300 * SS, 60 * SS, (300 + 853) * SS, (60 + 480) * SS)).resize((W * SS, H * SS))
        return img.filter(ImageFilter.GaussianBlur(3 * SS))
    return S.cached("thanks_bg", make)


def thanks(tl, t):
    T = tl.t
    c = Canvas(thanks_bg().copy())
    w2 = math.sin(math.pi * t)
    happy_w = T("e_thanks", 0.55) <= t < T("e_moral") or t >= T("e_bye")
    S.cat_front(c, 440, 715 + 3 * w2, D.WHISKERS, 1.0, t, mouth=tl.mouth("whiskers", t),
                eyes="happy" if happy_w else "open", ear=0.0, tilt=-4 + 2 * w2, breath=w2,
                blink=S.blink4(t), ball_hug=True)
    happy_l = t >= T("e_moral", 1) or t < T("e_moral")
    S.cat_front(c, 860, 725 - 3 * w2, D.LUNA, 0.95, t, mouth=tl.mouth("luna", t),
                eyes="happy" if happy_l and t >= T("e_bye") else "open", tilt=4 - 2 * w2, breath=-w2,
                blink=S.blink4(t + 1.3))
    hop = abs(math.sin(t * 6)) * 18 if t >= T("e_bye") else 0
    D.mouse(c, 655, 690, 2.4, 1, t, mouth=tl.mouth("pip", t), proud=True, hop=hop,
            eyes="happy" if t >= T("e_bye") else "open")
    k = ease(tl.prog("e_end", t, 0.2, 0.6))
    if k > 0:
        c.text(W / 2, 110, "The End", 30 + 46 * k, mix((70, 66, 100), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"sill": sill, "thanks": thanks}
CONTINUOUS = {"thanks"}
