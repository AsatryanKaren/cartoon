"""kitchen: both branches lead here. On the kitchen counter the flour, the eggs and the milk go into the
big bowl; Luna stirs. Whiskers tastes the batter "just a little" -- three times -- until Luna saves it.
Whoosh into the oven, ding! -- out comes the cake: round, soft and yummy (pink icing, no apples or honey
showing, so it fits both branches). Now to decorate the house: Whiskers turns to the viewer and asks Q2.
Ends in the listening pose."""
import math

import draw as D
import film
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S

CY = S.KCY
BOWL_X = 720
LX, WX = 930, 520
FLOUR, EGGS, MILK = (1035, CY), (1112, CY), (1176, CY)
OVEN_MID = ((S.OVEN[0] + S.OVEN[2]) / 2, (S.OVEN[1] + S.OVEN[3]) / 2 + 20)


def word_times(tl, eid, word):
    """Times of every occurrence of a word in a line (by its position in the text)."""
    e = tl.ev(eid)
    word = S.word(eid, word).lower()
    low, out, i = e.text.lower(), [], 0
    while True:
        i = low.find(word, i)
        if i < 0:
            return out
        out.append(e.start + e.dur * i / max(1, len(e.text)))
        i += 1


def arc(p0, p1, u, h=120):
    return lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - h * math.sin(math.pi * u)


def kitchen(tl, t):
    T = tl.t
    c = Canvas(S.kitchen_bg().copy())
    # oven glow while baking
    glow = clamp(tl.prog("k_oven", t, 0.28, 0.4)) * (1 - clamp(tl.prog("k_oven", t, 0.85, 1.0)))
    if glow > 0:
        x0, y0, x1, y1 = S.OVEN
        c.rect(x0 + 30, y0 + 76, x1 - 30, y1 - 36, D.mix((70, 60, 70), (255, 170, 70), glow * (0.8 + 0.2 * math.sin(t * 6))),
               ol=None, r=8)
        for k in range(3):
            xx = x0 + 70 + k * 45
            c.line([(xx + 6 * math.sin(t * 5 + k + j), y0 - 10 - j * 14) for j in range(4)], (255, 200, 150), 3)
    # ---- ingredients
    S.flour_bag(c, FLOUR[0], FLOUR[1], 0.9)
    eggs_left = 2 if t >= S.word_time(tl, "k_narr", "eggs") else 3
    S.egg_box(c, EGGS[0], EGGS[1], 0.9, n=eggs_left)
    tf = S.word_time(tl, "k_narr", "flour")
    te = S.word_time(tl, "k_narr", "eggs")
    tm = S.word_time(tl, "k_narr", "milk")
    # milk bottle hops over the bowl, pours, hops back
    mk = clamp((t - tm + 0.2) / 1.6)
    if 0 < mk < 1:
        if mk < 0.3:
            mx, my = arc(MILK, (BOWL_X + 60, CY - 120), ease(mk / 0.3), 60)
            tilt = 0.0
        elif mk < 0.7:
            mx, my, tilt = BOWL_X + 60, CY - 120, -1.6 * ease(min(1, (mk - 0.3) / 0.1))
        else:
            mx, my = arc((BOWL_X + 60, CY - 120), MILK, ease((mk - 0.7) / 0.3), 60)
            tilt = -1.6 * (1 - ease((mk - 0.7) / 0.1))
        mouth = S.milk_bottle(c, mx, my, 0.9, tilt)
        if 0.38 < mk < 0.68:
            c.line([mouth, (mouth[0] - 6, CY - 82)], (255, 255, 255), 8)
    else:
        S.milk_bottle(c, MILK[0], MILK[1], 0.9)
    # ---- bowl or cake
    level = 0.35 + 0.65 * ease(clamp((t - tf) / 1.2))
    dips = word_times(tl, "k_taste", "taste") + word_times(tl, "k_taste", "more")
    ndip = sum(1 for d in dips if t >= d + 0.25)
    level -= 0.2 * ndip
    stirring = T("k_narr", 0.75) <= t < T("k_taste")
    bowl_x = BOWL_X + 80 * ease(tl.prog("k_leave", t, 0.1, 0.5))
    bk = tl.prog("k_oven", t, 0.08, 0.32)
    ck = tl.prog("k_oven", t, 0.82, 1.0)
    if t < T("k_oven", 0.08):
        S.mixing_bowl(c, bowl_x, CY, 1.0, level, spoon=(t * 7) if stirring else (0.6 if t < T("k_leave") else None))
    elif bk < 1:
        bx, by = arc((bowl_x, CY), (OVEN_MID[0], OVEN_MID[1] + 60), ease(bk), 160)
        S.mixing_bowl(c, bx, by, lerp(1.0, 0.55, bk), level)
    elif ck > 0:
        cx, cy = arc((OVEN_MID[0], OVEN_MID[1] + 60), (BOWL_X, CY), ease(ck), 170)
        S.cake(c, cx, cy, lerp(0.55, 1.0, ck), t)
    # flour puff + egg
    k = clamp((t - tf) / 0.9)
    if 0 < k < 1:
        px, py = arc((FLOUR[0], CY - 110), (BOWL_X, CY - 90), ease(min(1, k * 2)), 80)
        r = 18 + 50 * max(0.0, k - 0.5)
        for j in range(5):
            c.circle(px + math.cos(j * 1.3) * r * 0.8, py - abs(math.sin(j * 1.9)) * r * 0.6, r * 0.6,
                     D.mix((255, 255, 255), (255, 240, 206), max(0.0, k - 0.5) * 2), ol=None)
    k = clamp((t - te) / 0.6)
    if 0 < k < 1:
        ex, ey = arc((EGGS[0] - 24, CY - 26), (BOWL_X, CY - 90), ease(k), 140)
        S.egg(c, ex, ey, 12)
    # ---- Luna
    leyes = "open"
    if T("k_leave") <= t < T("k_leave", 0.6):
        leyes = "wide"
    if T("k_ready") <= t < T("k_decor"):
        leyes = "happy"
    oven_watch = T("k_oven", 0.05) <= t < T("k_oven", 0.95)
    lhop = 0.0
    if T("k_leave") <= t < T("k_leave", 0.5):
        lhop = 16 * math.sin(math.pi * tl.prog("k_leave", t, 0, 0.5))
    D.cat(c, LX, CY - lhop, D.LUNA, 1.0, -1, "stand", t=t, mouth=tl.mouth("luna", t), seed=1.3, eyes=leyes,
          look=(1, 0.5) if not oven_watch else (1, 0))
    # ---- Whiskers
    wx, pose, weyes = WX, "stand", "open"
    for d in dips:
        if d - 0.15 <= t < d + 0.35:
            u = math.sin(math.pi * (t - d + 0.15) / 0.5)
            wx, pose = WX + 40 * u, "crouch"
    face = -1 if oven_watch else 1
    if T("k_ready") <= t:
        weyes = "happy"
    mouth = tl.mouth("whiskers", t)
    if T("k_taste") <= t < T("k_leave") and not tl.talking("whiskers", t):
        mouth = 0.25 + 0.2 * math.sin(t * 12)
    D.cat(c, wx, CY, D.WHISKERS, 1.0, face, pose, t=t, mouth=mouth, seed=0, eyes=weyes,
          look=(1, 0.6) if pose == "crouch" else (1, 0))
    if ndip and face > 0:
        hx, hy = wx + 52 + 14, CY - 86 + 14 + (14 if pose == "crouch" else 0)
        for j in range(min(ndip, 3)):
            c.ellipse(hx + j * 9 - 4, hy + 2 + (j % 2) * 3, 7 + 2 * j, 5, (250, 226, 170), w=1.5)
    if T("k_ready") <= t:
        if t < T("k_decor"):
            for j in range(4):
                a = t * 2 + j * 1.6
                S.sparkle(c, BOWL_X + 120 * math.cos(a), CY - 90 + 50 * math.sin(a), 12)
        for j in range(3):                                 # warm steam
            u = ((t * 0.6) + j / 3) % 1.0
            c.line([(BOWL_X - 30 + j * 30 + 8 * math.sin(t * 3 + j + v), CY - 150 - 60 * u - v * 12) for v in range(3)],
                   D.mix((255, 255, 255), (255, 240, 206), u), 4)
    return S.cam(c, 200, 155, 1000)


def ask(tl, t):
    T = tl.t
    e = tl.ev("c_q")
    ph = t - film.FILM_SECONDS
    cues = [(S.word_time(tl, "c_q", "balloons"), -1), (S.word_time(tl, "c_q", "flowers"), 1)]
    point = S.point_track(tl, t, cues, e.end + 0.1)
    listen = S.listen_amount(t, t_on=T("c_end", 0.1), dur=0.5)
    s0 = tl.scenes["ask"][0]
    lean = ease((t - s0) / 0.6) * (1 - ease((t - T("c_q")) / 0.5)) \
        + ease((t - T("c_q")) / 0.5) * 0.4 * (1 - ease((t - T("c_end")) / 0.5))
    look = None
    if t < T("c_think", 0.45):
        look = (0.6, -1.0)                          # "Hmm." -- thinking
    elif t < S.word_time(tl, "c_q", "balloons") - 0.3:
        look = (0.0, 0.0)
    return S.closeup(S.q2_backdrop(), t, ph, listen=listen, mouth=tl.mouth("whiskers", t), point=point,
                     look=look, lean=lean)


SCENE_FUNCS = {"kitchen": kitchen, "ask": ask}
CONTINUOUS = {"ask"}
