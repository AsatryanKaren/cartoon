"""tree: Whiskers and Luna leap up the big tree, branch by branch. In the nest at the top a little bird
saw the ball bounce down the hill to the river -- and from up there they can see the river too. Whiskers
slips, bounces off a branch and lands in a pile of leaves (on purpose, of course). Off to the river!"""
import math

import numpy as np

import draw as D
from draw import Canvas, W, H, SS, ease, lerp, clamp, mix
from interactive.pond_or_tree import shared as S

GT = 1360                     # ground line (world y); the world is 1280 x 1440
TRUNK_X = 600
BRANCHES = [(1, 1120, 640, 920), (-1, 880, 280, 560), (1, 640, 640, 930), (-1, 400, 230, 560)]
NEST = (330, 400)
PILE = (380, GT)
W_STEPS = [(760, GT), (800, 1120), (420, 880), (790, 640), (470, 400)]
L_STEPS = [(900, GT), (870, 1120), (350, 880), (840, 640)]


FAR_K = 0.3                   # the far landscape scrolls slower (parallax)


def far_bg():
    def make():
        h = H + int(FAR_K * H)
        c = Canvas(D.gradient(W * SS, h * SS, [(0, (100, 176, 240)), (0.55, (200, 232, 255)), (1, (200, 232, 255))]),
                   size=(W, h))
        D.cloud(c, 180, 160, 0.8)
        D.cloud(c, 1000, 260, 0.7)
        # far landscape (seen from the top of the tree): hills going down to a river, with a tiny red ball
        pts = [(x, 500 + 26 * math.sin(x / 150)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, h), (0, h)], (160, 208, 150), ol=None)
        pts = [(x, 640 + 30 * math.sin(x / 120 + 2)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, h), (0, h)], (146, 198, 136), ol=None)
        c.poly([(860, h), (1000, 640), (1080, 560), (1180, 520), (1280, 515), (1280, 545), (1200, 552),
                (1110, 600), (1050, 680), (940, h)], S.WATER, ol=None)
        S.ball(c, 1150, 548, 8)
        return c.img
    return S.cached("tree_far", make)


def bg():
    """The tree and the ground, on a transparent layer."""
    def make():
        from PIL import Image
        c = Canvas(Image.new("RGBA", (W * SS, 2 * H * SS), (0, 0, 0, 0)))
        pts = [(x, 980 + 40 * math.sin(x / 190)) for x in range(0, W + 50, 50)]
        c.poly(pts + [(W, 2 * H), (0, 2 * H)], (150, 205, 130), ol=None)
        c.rect(0, GT - 30, W, 2 * H, S.GRASS, ol=None)
        c.rect(0, GT + 30, W, 2 * H, S.GRASS_D, ol=None)
        # crown behind the trunk (open on the right so the view shows)
        for dx, dy, r in ((-220, 330, 150), (-60, 200, 170), (120, 250, 120), (-330, 520, 130), (-180, 620, 120),
                          (90, 470, 110), (140, 760, 100), (-150, 900, 100)):
            c.circle(TRUNK_X + dx, dy, r, S.LEAF_D)
            c.circle(TRUNK_X + dx, dy, r - 6, S.LEAF_D, ol=None)
        # trunk
        c.poly([(TRUNK_X - 80, GT + 10), (TRUNK_X - 52, GT - 80), (TRUNK_X - 40, 160), (TRUNK_X + 40, 160),
                (TRUNK_X + 52, GT - 80), (TRUNK_X + 84, GT + 10)], S.TRUNK, w=3)
        for k in range(9):
            y = 260 + k * 120
            c.arc(TRUNK_X + (-12 if k % 2 else 14), y, 12, 26, 90, 270, S.TRUNK_D, 3)
        c.ellipse(TRUNK_X + 8, 1000, 14, 20, (70, 46, 30))           # knot hole
        # branches
        for side, y, x0, x1 in BRANCHES:
            if side > 0:
                c.poly([(TRUNK_X + 20, y + 26), (x1, y + 6), (x1 + 10, y), (x1, y - 4), (TRUNK_X + 20, y - 2)],
                       S.TRUNK, w=3)
            else:
                c.poly([(TRUNK_X - 20, y + 26), (x0, y + 6), (x0 - 10, y), (x0, y - 4), (TRUNK_X - 20, y - 2)],
                       S.TRUNK, w=3)
        # top of the crown
        for dx, dy, r in ((-40, 90, 120), (-200, 150, 100), (80, 120, 100)):
            c.circle(TRUNK_X + dx, dy, r, S.LEAF)
            c.circle(TRUNK_X + dx, dy, r - 6, S.LEAF, ol=None)
        # leaf pile at the foot
        rng = np.random.default_rng(5)
        c.ellipse(PILE[0], PILE[1] - 16, 110, 34, (214, 140, 60))
        for _ in range(40):
            c.ellipse(PILE[0] + rng.uniform(-95, 95), PILE[1] - 16 + rng.uniform(-24, 18), 10, 6,
                      [(230, 160, 60), (200, 100, 50), (240, 200, 80)][rng.integers(3)], w=1.5)
        for x in (80, 1000, 1180):
            D.flower(c, x, GT + 40, (250, 140, 180))
        return c.img
    return S.cached("tree_bg", make)


def leaf_clumps(c, t):
    """Leaves at the branch tips (drawn in front)."""
    for side, y, x0, x1 in BRANCHES:
        x = x1 + 20 if side > 0 else x0 - 20
        sw = 3 * math.sin(t * 1.5 + y)
        for dx, dy, r in ((0, -30, 46), (side * 34, -6, 34), (-side * 20, 10, 30)):
            c.circle(x + dx + sw, y + dy, r, S.LEAF)
        for dx, dy, r in ((0, -30, 40), (side * 34, -6, 28)):
            c.circle(x + dx + sw, y + dy, r, S.LEAF_L, ol=None)


def climb(t, t0, t1, steps):
    """(x, y, airborne) while leaping up the branch steps between t0 and t1."""
    n = len(steps) - 1
    if t <= t0:
        return steps[0][0], steps[0][1], False
    if t >= t1:
        return steps[-1][0], steps[-1][1], False
    u = (t - t0) / (t1 - t0) * n
    k = int(u)
    f = u - k
    (xa, ya), (xb, yb) = steps[k], steps[k + 1]
    if f < 0.25:                                  # crouch before the leap
        return xa, ya, False
    v = (f - 0.25) / 0.75
    return lerp(xa, xb, ease(v)), lerp(ya, yb, v) - 160 * math.sin(math.pi * v), True


def whiskers_pos(tl, t):
    """x, y, pose, eyes, squash, face"""
    T = tl.t
    if t < T("t_climb"):
        x = S.smooth(t, [(0, -150), (T("t_arrive", 0.9), 760)])
        return x, GT, ("walk" if t < T("t_arrive", 0.95) else "stand"), "open", 1.0, 1
    if t < T("t_slip", 0.15):
        x, y, air = climb(t, T("t_climb"), T("t_climb", 0.95), W_STEPS)
        face = 1 if x < 600 or t > T("t_climb", 0.95) else -1
        if t >= T("t_climb", 0.95):
            face = 1 if t >= T("t_view") or t < T("t_bird") else -1
        if t >= T("t_slip"):
            x += 5 * math.sin(t * 30)
            return x, y, "stand", "wide", 1.0, 1
        return x, y, "leap" if air else "stand", "open", 1.0, face
    k = tl.prog("t_slip", t)
    if k < 0.4:                                   # fall to the branch below
        u = (k - 0.15) / 0.25
        return 470, lerp(400, 880, u * u), "leap", "wide", 1.0, 1
    if k < 0.5:                                   # boing!
        u = (k - 0.4) / 0.1
        return lerp(470, 440, u), 880 - 90 * math.sin(math.pi * u), "stand", "wide", 1 - 0.3 * math.sin(math.pi * u), 1
    if k < 0.78:
        u = (k - 0.5) / 0.28
        return lerp(440, PILE[0], u), lerp(880, GT - 10, u * u), "leap", "wide", 1.0, 1
    if t < T("t_go", 0.5):
        sq = 1 - 0.3 * max(0.0, 1 - (k - 0.78) / 0.12) if k < 1 else 1.0
        return PILE[0], GT - 22, "sit", "happy" if t >= T("t_purpose", 0.6) else "closed", sq, 1
    x = S.smooth(t, [(T("t_go", 0.5), PILE[0]), (T("t_exit", 1), 1500)])
    return x, GT, "walk", "open", 1.0, 1


def luna_pos(tl, t):
    T = tl.t
    if t < T("t_climb", 0.12):
        x = S.smooth(t, [(0, -300), (T("t_arrive", 0.9), 900)])
        return x, GT, ("walk" if t < T("t_arrive", 0.95) else "stand"), 1
    if t < T("t_purpose", 0.2):
        x, y, air = climb(t, T("t_climb", 0.12), T("t_climb", 1.0), L_STEPS)
        face = -1 if t > T("t_climb") and T("t_bird") <= t < T("t_view") else 1
        if not air and abs(y - 640) < 1:
            face = -1 if T("t_bird") <= t < T("t_view") else 1
        return x, y, "leap" if air else "stand", face
    if t < T("t_purpose", 0.9):
        u = tl.prog("t_purpose", t, 0.2, 0.9)
        return lerp(840, 520, u), lerp(640, GT, u) - 120 * math.sin(math.pi * u), "leap", -1
    if t < T("t_go", 0.5):
        return 520, GT, "stand", -1
    x = S.smooth(t, [(T("t_go", 0.5), 520), (T("t_exit", 1), 1650)])
    return x, GT, "walk", 1


def tree(tl, t):
    T = tl.t
    wx, wy, wpose, weyes, wsq, wface = whiskers_pos(tl, t)
    camy = clamp(S.smooth(t, [(0, GT), (T("t_climb"), GT), (T("t_climb", 1), 400), (T("t_slip", 0.15), 400),
                               (T("t_slip", 0.8), GT)], r=0.3) - 600, 0, H)
    fy = int(round(FAR_K * camy * SS))
    img = far_bg().crop((0, fy, W * SS, fy + H * SS))
    y0 = int(round(camy * SS))
    near = bg().crop((0, y0, W * SS, y0 + H * SS))
    img.paste(near, (0, 0), near)
    c = Canvas(img)
    c.push(0, -camy)
    # nest + bird
    S.nest(c, NEST[0], NEST[1], 0.9, "back")
    if t < T("t_go"):
        S.robin(c, NEST[0] + 6, NEST[1] - 14, 1.4, 1, t, mouth=tl.mouth("bird", t), cap=False, bag=False,
                wave=1.0 if T("t_bird") <= t < T("t_bird", 0.3) else 0.0)
    S.nest(c, NEST[0], NEST[1], 0.9, "front")
    # Luna
    lx, ly, lpose, lface = luna_pos(tl, t)
    lwalk = lx / 12 if lpose == "walk" else 0
    D.cat(c, lx, ly, D.LUNA, 0.9, lface, lpose, walk=lwalk, t=t, mouth=tl.mouth("luna", t), seed=1.3,
          look=(1, -1) if T("t_tall") <= t < T("t_climb") else (1, 0.2))
    # Whiskers
    look = (1, -1) if T("t_tall") <= t < T("t_climb") else (1, 0.3)
    D.cat(c, wx, wy, D.WHISKERS, 0.9, wface, wpose, walk=wx / 12 if wpose == "walk" else 0, t=t,
          mouth=tl.mouth("whiskers", t), eyes=weyes, look=look, squash=wsq, seed=0)
    if T("t_slip", 0.78) <= t < T("t_go", 0.5):
        # flying leaves, and one leaf stuck on his head
        dt = t - T("t_slip", 0.78)
        rng = np.random.default_rng(8)
        for k in range(14):
            ang = rng.uniform(math.pi * 1.1, math.pi * 1.9)
            sp = rng.uniform(150, 300)
            x = PILE[0] + math.cos(ang) * sp * dt + 20 * math.sin(t * 5 + k)
            y = GT - 30 + math.sin(ang) * sp * dt + 160 * dt * dt
            if y < GT:
                c.ellipse(x, y, 9, 5, [(230, 160, 60), (200, 100, 50)][k % 2], w=1.5)
        c.ellipse(PILE[0] + 16, GT - 22 - 150 * 0.9, 12, 7, (230, 160, 60), w=1.5)
    leaf_clumps(c, t)
    # the bird flies down to wave goodbye
    if t >= T("t_go"):
        u = tl.prog("t_go", t, 0, 0.6)
        S.robin(c, lerp(NEST[0], 760, ease(u)), lerp(NEST[1] - 20, GT - 180, ease(u)) + 8 * math.sin(t * 6),
                1.3, -1, t, fly=1.0, cap=False, bag=False, mouth=0.0)
    c.pop()
    # "I can see the river": a soft glow pointing out the tiny red ball
    k = tl.prog("t_see", t, 0.0, 0.8)
    if 0 < k < 1 and camy < 10:
        S.sparkle(c, 1150, 548 - FAR_K * camy - 26, 16 * math.sin(math.pi * k))
    return c


SCENE_FUNCS = {"tree": tree}
