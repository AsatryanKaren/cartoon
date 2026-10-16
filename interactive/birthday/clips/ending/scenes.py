"""ending: both branches lead here, so the room shows neutral decorations only (the banner, two balloons
and a small vase of flowers). Knock, knock! Pip comes in: "Surprise! Happy birthday, Pip!" -- confetti,
and the cake with a candle. Close-up: Whiskers thanks the viewer, Luna's moral, Pip: let's eat cake!
Whiskers (holding a slice): "Finally!". The End."""
import math

from PIL import ImageFilter

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix
from interactive.birthday import shared as S

PY = 650
LX, WX = 700, 840
x0d, y0d, x1d, y1d = S.DOOR


def neutral_decor(c, t):
    for k, (dx, ci) in enumerate(((-40, 0), (30, 1))):
        S.party_balloon(c, S.TABLE[0] + 10 + dx, 250 + 30 * k, 38, S.BALLOON_COLS[ci], t,
                        string=S.TABLE[2] - 250 - 30 * k - 38, seed=k)
    S.vase(c, 1180, S.TABLE[2] - 6, 0.55)
    S.bouquet(c, 1180, S.TABLE[2] - 6 - 36, 0.5, t)


def party(tl, t):
    T = tl.t
    c = Canvas(S.party_bg(True).copy())
    neutral_decor(c, t)
    S.cake(c, S.CAKE_AT[0] - 20, S.CAKE_AT[1], 0.75, t, candle_on=True)
    # the door: knocks, then it swings open
    for f in (0.3, 0.45, 0.6):
        dt = t - T("e_open", f)
        if 0 < dt < 0.3:
            for j in range(3):
                c.arc(x1d - 10, y0d + 170, 20 + j * 14 + 30 * dt, 20 + j * 14 + 30 * dt, 300, 420, (120, 80, 60), 3)
    op = ease(tl.prog("e_door", t, 0.0, 0.35))
    if op > 0:
        c.rect(x0d, y0d, x1d, y1d, (90, 70, 80), ol=None)
        c.rect(x0d, y1d - 30, x1d, y1d, (130, 100, 90), ol=None)
        wd = (x1d - x0d) * (1 - 0.8 * op)
        c.poly([(x0d, y0d), (x0d + wd, y0d + 20 * op), (x0d + wd, y1d - 10 * op), (x0d, y1d)], (178, 112, 72), w=3)
        c.circle(x0d + wd - 16, y0d + 170, 8, (250, 210, 80), w=2)
    # Pip comes in
    if t >= T("e_door", 0.2):
        px = S.smooth(t, [(T("e_door", 0.2), x0d + 60), (T("e_door", 1), 470)], r=0.2)
        moving = t < T("e_door", 1)
        eyes = "open"
        if T("e_surprise", 0.2) <= t < T("e_wow", 0.5):
            eyes = "wide" if t < T("e_wow") else "happy"
        if T("e_wow", 0.5) <= t:
            eyes = "happy"
        hop = abs(math.sin(t * 7)) * 12 if T("e_wow", 0.4) <= t else 0
        D.mouse(c, px, PY - 4, 1.9, 1, t, walk=px / 6 if moving else 0, mouth=tl.mouth("pip", t), eyes=eyes,
                hop=hop if not moving else abs(math.sin(px / 9)) * 5, proud=T("e_wow") <= t)
        if T("e_wow", 0.5) <= t:
            S.hearts(c, px + 20, PY - 120, t)
    # the cats wait, then jump: Surprise!
    jump = 0.0
    if T("e_surprise") <= t < T("e_surprise", 1):
        jump = 40 * abs(math.sin(math.pi * tl.prog("e_surprise", t) * 2))
    look = (1, 0)
    D.cat(c, LX, PY - jump, D.LUNA, 1.0, -1, "stand", t=t, mouth=tl.mouth("luna", t), seed=1.3,
          eyes="happy" if T("e_surprise") <= t else "open", look=look)
    D.cat(c, WX, PY - jump * 0.8, D.WHISKERS, 1.0, -1, "stand", t=t, mouth=tl.mouth("whiskers", t), seed=0,
          eyes="happy" if T("e_surprise") <= t else "open", look=look)
    if t < T("e_door"):
        ears = clamp(tl.prog("e_open", t, 0.25, 0.4))
        if ears > 0:
            S.sparkle(c, LX - 52, PY - 160, 10 * ears)
            S.sparkle(c, WX - 52, PY - 160, 10 * ears)
    dt = t - T("e_surprise")
    S.confetti(c, LX - 40, PY - 140, dt, n=36, seed=3, spread=380, up=480)
    S.confetti(c, WX - 40, PY - 140, dt - 0.1, n=36, seed=5, spread=380, up=480)
    return S.cam(c, 40, 40, 1180)


def thanks_bg():
    def make():
        img = S.party_bg(True).crop((240 * SS, 170 * SS, (240 + 900) * SS, (170 + 506) * SS)).resize((W * SS, H * SS))
        return img.filter(ImageFilter.GaussianBlur(4 * SS))
    return S.cached("bd_thanks_bg", make)


def thanks(tl, t):
    T = tl.t
    c = Canvas(thanks_bg().copy())
    w2 = math.sin(math.pi * t)
    happy_w = T("e_thanks", 0.6) <= t < T("e_moral") or t >= T("e_finally")
    paw_l = None
    if t >= T("e_eat", 0.6):
        u = ease((t - T("e_eat", 0.6)) / 0.5)
        paw_l = (lerp(-110, -150, u), lerp(-40, -230, u) + 3 * w2)
    S.cat_front(c, 400, 715 + 3 * w2, D.WHISKERS, 1.0, t, mouth=tl.mouth("whiskers", t),
                eyes="happy" if happy_w else "open", tilt=-4 + 2 * w2, breath=w2, blink=S.blink4(t),
                look=(0.3, 0.4) if T("e_eat", 0.6) <= t < T("e_finally") else (0.0, 0.0), paw_l=paw_l)
    if paw_l is not None:
        S.cake_slice(c, 400 + paw_l[0], 715 + 3 * w2 + paw_l[1] - 22, 1.1)
    S.cat_front(c, 880, 725 - 3 * w2, D.LUNA, 0.95, t, mouth=tl.mouth("luna", t),
                eyes="happy" if t >= T("e_moral", 1) else "open", tilt=4 - 2 * w2, breath=-w2,
                blink=S.blink4(t + 1.3))
    S.cake(c, 640, 706, 1.05, t, candle_on=True)
    hop = abs(math.sin(t * 6)) * 18 if T("e_eat") <= t < T("e_eat", 1) else 0
    D.mouse(c, 790, 700, 2.3, -1, t, mouth=tl.mouth("pip", t), proud=True, hop=hop,
            eyes="happy" if t >= T("e_eat") else "open")
    if t >= T("e_finally"):
        S.hearts(c, 300, 300, t, n=3)
    k = ease(tl.prog("e_end", t, 0.2, 0.6))
    if k > 0:
        c.text(W / 2, 110, "The End", 30 + 46 * k, mix((90, 70, 90), (255, 240, 200), k), stroke=4 * k)
    return c


SCENE_FUNCS = {"party": party, "thanks": thanks}
CONTINUOUS = {"thanks"}
