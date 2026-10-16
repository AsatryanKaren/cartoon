"""flowers: Luna and Whiskers pick poppies, daisies and roses in the garden by the house, then put the
bouquet in a vase in the living room. Whiskers smells them too... ah... ah... achoo! The sneeze blows
the petals all over the room -- and now the whole house is decorated. It's even prettier now."""
import math

import numpy as np

import draw as D
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S
from interactive.pond_or_tree import shared as P

GY = P.GY
PATCH = [(170, "poppy", 80), (215, "daisy", 92), (255, "rose", 76), (300, "poppy", 96), (345, "daisy", 84),
         (390, "rose", 98), (435, "daisy", 78), (480, "poppy", 90), (525, "rose", 82), (570, "daisy", 94)]
PICK_ORDER = [3, 4, 2, 5, 1, 6, 0, 7]          # these get picked (the last two stay)
NAMED = {"poppies": 7, "daisies": 9, "roses": 8}

PY = 640
STOOL_X = 640
VASE_TOP = PY - 70 - 66
LX, WX = 440, 830


def pick(tl, t):
    T = tl.t
    c = P.view(P.garden_bg(False), 0)
    a, b = T("f_narr", 0.1), T("f_narr", 1.0)
    picked = int(clamp((t - a) / (b - a)) * len(PICK_ORDER) + 0.001) if t >= a else 0
    gone = set(PICK_ORDER[:picked])
    for k, (x, kind, h) in enumerate(PATCH):
        if k in gone:
            continue
        sw = 2 * math.sin(t * 1.5 + k)
        c.line([(x, GY + 40), (x + sw, GY + 40 - h)], (80, 150, 70), 4, cap=False)
        c.ellipse(x - 10, GY + 40 - h * 0.4, 12, 5, S.LEAF, w=1.5)
        S.flower_head(c, x + sw, GY + 40 - h, kind, 18)
    for word, k in NAMED.items():
        kk = clamp((t - S.word_time(tl, "f_names", word)) / 0.8)
        if 0 < kk < 1:
            x, _, h = PATCH[k]
            S.sparkle(c, x + 24, GY + 10 - h, 18 * math.sin(math.pi * kk))
    walk0 = T("f_carry")
    lx = S.smooth(t, [(0, 330), (walk0, 330), (T("f_carry", 1), 640)], r=0.2)
    wx = S.smooth(t, [(0, 620), (walk0 + 0.2, 620), (T("f_carry", 1) + 0.2, 900)], r=0.2)
    lmov, wmov = t > walk0, t > walk0 + 0.2
    # Luna (picking, then carrying the bouquet)
    bob = 0 if lmov else -6 * abs(math.sin(t * 3)) * (a <= t < b)
    D.cat(c, lx, GY, D.LUNA, 1.0, 1, "walk" if lmov else ("crouch" if a <= t < b and math.sin(t * 3) > 0.3 else "stand"),
          walk=lx / 12 if lmov else 0, t=t, mouth=tl.mouth("luna", t), seed=1.3,
          eyes="happy" if T("f_names", 0.8) <= t else "open", look=(1, 0.6))
    S.bouquet(c, lx + 74, GY - 40 + bob, 0.5, t, n=max(2, picked + 2))
    # Whiskers smelling the last flowers
    D.cat(c, wx, GY, D.WHISKERS, 1.0, -1 if not wmov else 1, "walk" if wmov else "stand", walk=wx / 12 if wmov else 0,
          t=t, mouth=tl.mouth("whiskers", t), seed=0, eyes="happy" if t < walk0 else "open", look=(1, 0.5))
    return S.cam(c, 60, 140, 1000)


def petals_init():
    rng = np.random.default_rng(17)
    out = []
    cols = [S.FLOWER_PETAL_COLS[k] for k in ("poppy", "daisy", "rose")]
    for k in range(110):
        if k < 50:
            tx, ty = rng.uniform(40, 1240), rng.uniform(PY - 40, 712)      # the floor
        elif k < 70:
            tx, ty = rng.uniform(300, 900), rng.uniform(72, 150)          # on the banner
        else:
            tx, ty = rng.uniform(20, 1260), rng.uniform(180, 540)         # the walls
        out.append((tx, ty, rng.uniform(0.8, 2.2), rng.uniform(-300, 300), cols[k % 3], rng.uniform(0, 6.28)))
    return out


PETALS = petals_init()


def petals(c, tl, t, t0):
    ox, oy = STOOL_X + 6, VASE_TOP - 70
    dt = t - t0
    if dt <= 0:
        return
    for tx, ty, dur, lift, col, ph in PETALS:
        u = clamp(dt / dur)
        e = 1 - (1 - u) ** 2
        x = lerp(ox, tx, e) + 20 * math.sin(dt * 4 + ph) * (1 - u)
        y = lerp(oy, ty, e) - (260 + lift * 0.3) * math.sin(math.pi * e) * (1 - u * 0.5)
        rx = 7 * abs(math.cos(dt * 5 + ph)) * (1 - u) + 7 * u if u < 1 else 7
        c.ellipse(x, y, max(3.5, rx * 1.4), 6.5, col, ol=(150, 80, 90), w=1.2)


def room(tl, t):
    T = tl.t
    c = Canvas(S.party_bg(True).copy())
    S.cake(c, S.CAKE_AT[0], S.CAKE_AT[1], 0.75, t)
    S.stool(c, STOOL_X, PY, 1.0)
    S.vase(c, STOOL_X, PY - 70, 1.0)
    achoo = S.word_time(tl, "f_sniff", "achoo") + 0.15
    # bouquet: Luna puts it in the vase; after the sneeze only bare stems are left
    k = ease(tl.prog("f_vase", t, 0.15, 0.6))
    bx = lerp(LX + 74, STOOL_X, k)
    by = lerp(PY - 40, VASE_TOP, k) - 60 * math.sin(math.pi * k)
    S.bouquet(c, bx, by, lerp(0.5, 0.9, k), t, petals=0.0 if t >= achoo else 1.0)
    petals(c, tl, t, achoo)
    # ---- Luna
    leyes = "open"
    if T("f_petals") <= t < T("f_deco"):
        leyes = "wide"
    if T("f_true") <= t:
        leyes = "happy"
    D.cat(c, LX, PY, D.LUNA, 1.0, 1, "stand", t=t, mouth=tl.mouth("luna", t), seed=1.3, eyes=leyes,
          look=(1, -0.6) if T("f_blow") <= t < T("f_deco") else (1, 0))
    # ---- Whiskers
    wx = S.smooth(t, [(T("f_vase"), 1400), (T("f_vase", 0.9), WX)], r=0.2)
    pose, eyes, look, hdy, sq = ("walk" if t < T("f_vase", 0.95) else "stand"), "open", (1, 0), 0.0, 1.0
    t_ah = S.word_time(tl, "f_sniff", "ah")
    if T("f_sniff") <= t < t_ah:
        wx -= 40 * ease((t - T("f_sniff")) / 0.6)
        pose, eyes = "crouch", "closed"
    elif t_ah <= t < achoo:
        wx -= 40
        u = (t - t_ah) / max(0.1, achoo - t_ah)
        pose, eyes, look, hdy = "stand", "closed", (0, -1), -10 * u - 3 * math.sin(t * 12)
    elif achoo <= t < T("f_blow", 0.5):
        u = ease(clamp((t - achoo) / 0.3))
        wx = wx - 40 + 70 * u
        sq = 1 - 0.18 * math.sin(math.pi * min(1.0, (t - achoo) / 0.3))
        eyes = "closed" if t < achoo + 0.4 else "wide"
    elif t >= T("f_blow", 0.5):
        wx += 30
        eyes = "happy" if T("f_deco") <= t else "wide"
        look = (1, -0.6)
    D.cat(c, wx, PY, D.WHISKERS, 1.0, -1, pose, walk=wx / 12 if pose == "walk" else 0, t=t,
          mouth=tl.mouth("whiskers", t), seed=0, eyes=eyes, look=look, head_dy=hdy, squash=sq)
    if achoo <= t < achoo + 0.5:                      # the sneeze blast
        u = (t - achoo) / 0.5
        for j in range(5):
            yy = PY - 90 + (j - 2) * 14
            c.line([(wx - 70 - 40 * u, yy), (wx - 120 - 160 * u, yy + (j - 2) * 10 * u)], (255, 255, 255), 4)
    return S.cam(c, 60, 50, 1160)


SCENE_FUNCS = {"pick": pick, "room": room}
