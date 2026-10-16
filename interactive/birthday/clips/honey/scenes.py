"""honey: the flowery meadow with the beehive. Bees buzz around; Whiskers dreams of honey. Buzzy the bee
will share some honey -- but first the thirsty flowers need water. Whiskers waters them (they perk up)
and then, swinging the can up high, waters himself too (on purpose, of course). Buzzy brings a little
pot of honey; everyone heads home."""
import math

import draw as D
from draw import Canvas, ease, lerp, clamp
from interactive.birthday import shared as S

GL = S.GL
LX, WX0 = 290, 500
CAN0 = 600                           # where the watering can waits
BUZZ = (640, 430)                    # where Buzzy hovers while talking
HIVE_DOOR = (S.HIVE[0], S.HIVE[1] - 84)


def whiskers_state(tl, t):
    """x, pose, can (grip x, grip y, angle) or None, wet 0..1"""
    T = tl.t
    if t < T("h_watering"):
        x = S.smooth(t, [(0, -120), (T("h_arrive", 0.9), WX0)], r=0.2)
        return x, ("walk" if t < T("h_arrive", 0.95) else "stand"), None, 0.0
    k = tl.prog("h_watering", t)
    if k < 0.12:
        x = lerp(WX0, 552, ease(k / 0.12))
        return x, "walk", None, 0.0
    if k < 0.18:
        u = ease((k - 0.12) / 0.06)
        x = 552
        return x, "stand", (lerp(CAN0, x + 70, u), lerp(GL - 64, GL - 76, u), 0.0), 0.0
    if k < 0.5:
        u = (k - 0.18) / 0.32
        x = lerp(552, 640, ease(u))
        return x, "walk" if 0.05 < u < 0.95 else "stand", (x + 70, GL - 76, 0.55 + 0.1 * math.sin(t * 6)), 0.0
    if k < 0.62:
        u = ease((k - 0.5) / 0.12)
        x = 640
        return x, "stand", (x + lerp(70, 62, u), lerp(GL - 76, GL - 205, u), lerp(0.4, 1.6, u)), 0.0
    if k < 0.85:
        x = 640
        wet = clamp((k - 0.66) / 0.1)
        return x, "stand", (x + 62 + 3 * math.sin(t * 8), GL - 205, 1.6), wet
    u = ease((k - 0.85) / 0.15)
    x = 640
    return x, "stand", (x + lerp(62, 96, u), lerp(GL - 205, GL - 64, u), lerp(1.6, 0.0, u)), 1.0


def meadow(tl, t):
    T = tl.t
    c = Canvas(S.meadow_bg().copy())
    S.little_bees(c, S.HIVE[0], S.HIVE[1] - 230, t, n=4, r=80, s=0.4)
    perk = ease(tl.prog("h_watering", t, 0.22, 0.48))
    S.thirsty_flowers(c, t, perk)
    if 0 < tl.prog("h_watering", t, 0.48, 0.6) < 1:
        for j, (fx, _) in enumerate(S.THIRSTY[::2]):
            S.sparkle(c, fx, GL - 130, 14 * math.sin(math.pi * tl.prog("h_watering", t, 0.48, 0.6)))
    wx, wpose, can, wet = whiskers_state(tl, t)
    if t >= T("h_wet"):
        wet = 1.0 - 0.5 * tl.prog("h_exit", t)
    # the can on the ground (before he picks it up / after he puts it down)
    if t < T("h_watering", 0.12):
        S.watering_can(c, CAN0, GL - 64, 1.0, 0.0)
    elif t >= T("h_watering", 1.0):
        S.watering_can(c, 640 + 96, GL - 64, 1.0, 0.0)
    # puddle once he is soaked
    if wet > 0.3:
        c.ellipse(645, GL + 4, 70 * min(1.0, wet), 10, (150, 200, 240), ol=None)
    # ---- Luna
    exit_t = T("h_exit", 0.1)
    lx = S.smooth(t, [(0, -260), (T("h_arrive", 0.9), LX), (exit_t, LX), (T("h_exit", 1), -300)])
    lmov = t < T("h_arrive", 0.95) or t > exit_t
    lface = -1 if t > exit_t else 1
    leyes = "open"
    if T("h_watering", 0.7) <= t < T("h_wet"):
        leyes = "wide"
    if T("h_pot", 0.6) <= t < T("h_exit") or T("h_wet", 0.6) <= t < T("h_fetch"):
        leyes = "happy"
    llook = (1, -0.6) if T("h_hear") <= t < T("h_love") else (1, -0.2)
    D.cat(c, lx, GL, D.LUNA, 1.0, lface, "walk" if lmov else "stand", walk=lx / 12 if lmov else 0, t=t,
          mouth=tl.mouth("luna", t), seed=1.3, eyes=leyes, look=llook)
    has_pot = t >= T("h_pot", 0.75)
    if has_pot:
        bob = 3 * math.sin(lx / 9) if lmov else 0
        S.honey_pot(c, lx + lface * 70, GL - 4 + bob, 0.6)
    if T("h_hear") <= t < T("h_love"):
        for k in range(2):
            u = ((t * 1.2) + k / 2) % 1.0
            c.arc(lx + 40, GL - 150, 18 + 20 * u, 18 + 20 * u, 300, 360 + 30, (255, 255, 255), 3)
    # ---- Whiskers
    wexit = T("h_exit")
    if t > wexit:
        wx = S.smooth(t, [(wexit, wx), (T("h_exit", 0.95), -160)], r=0.15)
        wpose = "walk"
    wface = -1 if t > wexit else 1
    weyes, wlook = "open", (1, 0.0)
    if T("h_love") <= t < T("h_fly_in"):
        weyes, wlook = "happy", (0, -1)
    if T("h_watering", 0.18) <= t < T("h_watering", 0.5):
        wlook = (1, 0.8)
    if T("h_watering", 0.6) <= t < T("h_watering", 0.85):
        weyes = "closed"
    if T("h_wet", 0.55) <= t < T("h_fetch") or T("h_pot", 0.5) <= t:
        weyes = "happy" if t < wexit else "open"
    D.cat(c, wx, GL, D.WHISKERS, 1.0, wface, wpose, walk=wx / 12 if wpose == "walk" else 0, t=t,
          mouth=tl.mouth("whiskers", t), seed=0, eyes=weyes, look=wlook, wet=wet)
    if T("h_love") <= t < T("h_fly_in"):
        S.hearts(c, wx + 50, GL - 150, t)
    if can is not None:
        gx, gy, ang = can
        tip = S.watering_can(c, gx, gy, 1.0, ang)
        k = tl.prog("h_watering", t)
        if 0.2 < k < 0.5:
            S.water_drops(c, tip[0], tip[1], t, vx=110, n=16, fall=0.45)
        if 0.64 < k < 0.84:
            S.water_drops(c, tip[0], tip[1], t, vx=-10, n=18, fall=0.32, spread=40)
            if k > 0.68:
                for j in range(6):                       # splashes on his head
                    a = t * 9 + j
                    c.ellipse(wx + 52 + 34 * math.cos(a), GL - 126 - 10 * abs(math.sin(a)), 4, 3,
                              (170, 215, 250), ol=None)
    # ---- Buzzy
    fly0, fly1 = T("h_fly_in"), T("h_fly_in", 1)
    bx, by, bface, carry = HIVE_DOOR[0], HIVE_DOOR[1], -1, False
    if t < fly0:
        bx, by = HIVE_DOOR[0] - 40, HIVE_DOOR[1] - 60
        bx += 30 * math.sin(t * 1.6)
        by += 14 * math.sin(t * 2.3)
        bface = -1 if math.cos(t * 1.6) > 0 else 1
    elif t < T("h_fetch"):
        u = ease(clamp((t - fly0) / (fly1 - fly0)))
        bx = lerp(HIVE_DOOR[0] - 40, BUZZ[0], u)
        by = lerp(HIVE_DOOR[1] - 60, BUZZ[1], u) - 60 * math.sin(math.pi * u)
        if T("h_watering") <= t:
            bx, by = lerp(BUZZ[0], 800, ease(tl.prog("h_watering", t, 0, 0.15))), BUZZ[1] - 40
            bface = -1
    elif t < T("h_pot"):
        k = tl.prog("h_fetch", t)
        if k < 0.45:
            u = ease(k / 0.45)
            bx, by = lerp(800, HIVE_DOOR[0] - 30, u), lerp(BUZZ[1] - 40, HIVE_DOOR[1] - 10, u)
            bface = 1
        else:
            u = ease((k - 0.55) / 0.45) if k > 0.55 else 0.0
            bx, by = lerp(HIVE_DOOR[0] - 30, LX + 150, u), lerp(HIVE_DOOR[1] - 10, 420, u)
            carry = k > 0.5
    else:
        bx, by = LX + 150, 420
        carry = t < T("h_pot", 0.6)
        if t >= T("h_go"):
            bx, by = lerp(LX + 150, 760, ease(tl.prog("h_go", t, 0, 0.6))), 400
    by += 8 * math.sin(t * 4)
    if not carry and t < T("h_pot", 0.75) and T("h_pot", 0.6) <= t:
        u = tl.prog("h_pot", t, 0.6, 0.75)                 # the pot drops into Luna's paws
        S.honey_pot(c, lerp(bx, LX + 70, u), lerp(by + 100, GL - 4, u * u), lerp(0.75, 0.6, u))
    beyes = "happy" if (T("h_bee") <= t < T("h_bee", 0.25) or T("h_pot") <= t) else "open"
    S.bee(c, bx, by, 1.0, bface, t, mouth=tl.mouth("buzzy", t), eyes=beyes, carry=carry,
          wave=1.0 if (T("h_bee") <= t < T("h_bee", 0.3) or t >= T("h_go", 0.5)) else 0.0, seed=0.3)
    return S.cam(c, 200, 160, 980)


SCENE_FUNCS = {"meadow": meadow}
