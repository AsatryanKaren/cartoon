"""Shared kit for the series "Whiskers & Luna's World" (geography for ages 4-8).

Every episode imports this so the series looks and sounds the same:

    from world import kit as K
    from world.kit import kat, crew, sub_band          # (anything below)

QUICK REFERENCE (coordinates are output pixels, 1280x720, y down)
  Cast / motion
    kat(c, tl, t, who, x, y, s, face, pose, **kw)   draw whiskers/luna/pip with lip-sync mouth
    track(t, keys) / smooth(t, keys) / pop(k) / ease_out(k)   keyframe + easing helpers
    cushion(c, x, y, s, t, fly)                     the flying nap cushion (series signature ride)
    crew(c, tl, t, x, y, s, face, fly, who=..., eyes={}, look={})  friends sitting on the cushion
  Home (format part 1 and 7)
    home_bg(mood)          cached room + big window + window seat; mood "day" | "evening" | "night"
    SILL_Y, GLOBE_X, SPOT  where characters sit / where the old globe stands
    old_globe(c, x, y, s, lon, glow, t)   Luna's old globe on its wooden stand (spins, glows)
  The Earth
    globe(c, x, y, r, lon, lat, style, roll, sun, glow)  orthographic globe at any size/rotation;
                           style "earth" | "continents" | "toy"; sun=(lon,lat) adds a night side
    globe_xy(x, y, r, lon, lat, lon0, lat0, roll) -> (sx, sy, visible)  project a place onto a globe
    globe_to_map(c, k, t)  fullscreen morph: globe (k=0) flattening into the world map (k=1)
  The magic map (format part 2)
    map_view(lon, lat, zoom, style, labels) -> (Canvas, MapView)  world map floating in starry space
    draw_map(c, view, style) / map_clip(c, view)   draw map into a canvas / repaint space off its edges
    MapView.xy(lon, lat) -> screen (x, y);  lerp_view(a, b, k) for camera moves
    map_labels(c, view, "continents" | "oceans" | "all" | [names], k)
    map_label(c, view, lon, lat, text, size, col, k)
    map_highlight(c, view, continent, k, col)   glowing tint over one continent
    map_path(c, view, pts, u, col)  dotted travel path (lon/lat waypoints, smoothed) with arrow; returns head (x, y, angle)
    path_point(view, pts, u) -> (x, y, angle)
    you_are_here(c, x, y, t, k, text)  bouncing red pin with a label
    CONTINENT_LABELS, OCEAN_LABELS     name -> (lon, lat)
  Cards (format parts 5 and 6) and titles
    title_card(tl, t, t0, ep, topic)  series title card (spinning Earth, letters pop in)
    remember_card(t, facts, ks, icons, active, bg)   "Remember!" card, 3 facts revealed one by one
    quiz_card(t, question, choices, answer, ask, count, reveal, icons, number, answer_text)
    end_card(c, k, line1, line2)      "Next time ..." ribbon overlay
    icon_globe / icon_water / icon_compass(c, x, y, r, t)  ready-made fact icons
  Small helpers
    text(c, x, y, s, size, col, anchor, stroke)  text that respects c.push() scaling
    label(c, x, y, text, size, tip, k, col, bg)  rounded tag with an arrow to tip=(x, y)
    arrow(c, x0, y0, x1, y1, col, w, k)          arrow that grows with k
    compass(c, x, y, r, k, t, lit, words)        compass rose N/E/S/W (lit = letters to light up)
    inset(c, x, y, w, h, k, draw_fn, bg)         popup picture card; draw_fn(ic) draws in local 0..w,0..h
    bubble(c, x, y, rx, ry, k, tail)             thought bubble
    sparkles(c, x, y, rad, t, n, k, seed)        twinkling magic stars
    flash(c, k, col) / zoom(c, cx, cy, z)       fullscreen flash / camera push-in on a finished canvas
    sub_band(c, tl, t, strength)                 dark band behind subtitles while someone speaks
    space_bg()                                    cached starry backdrop
  Sound (merge into the episode's story.py)
    KIT_MOODS  w_intro w_home w_wonder w_map w_sea w_funny w_remember w_quiz w_night
    KIT_SFX    spin ding tick chime sparkle pop     e.g. EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

Typical quiz timing in a script: Say(question) -> Act(..., id="q1_count", sfx=[("tick", 0.0),
("tick", 0.333), ("tick", 0.667)]) -> Say(answer, id="q1_ans", sfx=[("chime", 0.0)]); the countdown
shows 3-2-1 over the Act, so give that Act a weight that comes out at about 3 seconds.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import draw as D
from draw import Canvas, W, H, SS, OUT, LW, ease, lerp, clamp, mix

TAU = 2 * math.pi

# ======================================================================= cast + motion

PAL = {"whiskers": D.WHISKERS, "luna": D.LUNA}
SEED = {"whiskers": 0.0, "luna": 1.3, "pip": 2.1}


def track(t, keys):
    """Piecewise-linear value through [(time, value), ...]."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(v0, v1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def smooth(t, keys, r=0.25):
    """track() with eased starts and stops."""
    return sum(track(t + r * k / 3, keys) for k in range(-3, 4)) / 7


def pop(k):
    """0..1 -> scale with a little overshoot (ease-out-back)."""
    k = clamp(k)
    s = 1.70158
    k -= 1
    return k * k * ((s + 1) * k + s) + 1


def ease_out(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def kat(c, tl, t, who, x, y, s=1.0, face=1, pose="sit", **kw):
    """Draw Whiskers, Luna or Pip; the mouth follows their speech unless mouth= is given."""
    mouth = kw.pop("mouth", tl.mouth(who, t) if tl is not None else 0.0)
    if who == "pip":
        kw.pop("look", None)
        kw.pop("head_dy", None)
        kw.pop("tail", None)
        walk = kw.pop("walk", 0.0)
        D.mouse(c, x, y, s, face, t, walk=walk, mouth=mouth, **kw)
    else:
        kw.pop("proud", None)
        kw.pop("hop", None)
        D.cat(c, x, y, PAL[who], s, face, pose, t=t, mouth=mouth, seed=SEED[who], **kw)


CUSHION = (226, 84, 92)
CUSHION_D = (186, 58, 72)
TASSEL = (255, 206, 80)


def cushion(c, x, y, s=1.0, t=0.0, fly=0.0, col=CUSHION):
    """Whiskers' plump nap cushion (origin: bottom centre). fly 0..1 makes the tassels flutter."""
    c.push(x, y, s)
    flap = math.sin(t * 14) * 6 * fly
    for side in (-1, 1):                                   # corner tassels
        bx = side * 118
        c.line([(bx, -16), (bx + side * 14, -6 + flap * side)], TASSEL, 3)
        c.poly([(bx + side * 10, -8 + flap * side), (bx + side * 22, -2 + flap * side),
                (bx + side * 16, 10 + flap * side)], TASSEL, w=2)
    dark = mix(col, (0, 0, 0), 0.22)
    c.rect(-122, -40, 122, 0, dark, r=18)
    c.rect(-118, -46, 118, -8, col, r=20)
    c.ellipse(0, -36, 100, 8, mix(col, (255, 255, 255), 0.25), ol=None)
    for bx in (-60, 0, 60):
        c.circle(bx, -26, 4, dark, w=1.5)
        c.arc(bx, -26, 14, 7, 200, 340, dark, 2)
    c.pop()


def crew(c, tl, t, x, y, s=1.0, face=1, fly=0.0, who=("whiskers", "luna", "pip"), eyes=None,
         look=None, extra=None):
    """The friends sitting on the flying cushion. (x, y) = cushion bottom centre.

    eyes / look: per-character overrides, e.g. eyes={"whiskers": "wide"}.
    extra: per-character dict of other kat() keywords (also pose=..., dy= vertical offset)."""
    eyes, look, extra = eyes or {}, look or {}, extra or {}
    bob = math.sin(t * 2.6) * 6 * fly
    if fly > 0.01:
        sparkles(c, x - face * 150 * s, y - 20 * s + bob, 60 * s, t, n=7, k=fly, seed=4)
    y = y + bob
    cushion(c, x, y, s, t, fly)
    top = y - 40 * s
    spots = {"whiskers": -52, "luna": 46, "pip": 104}
    if "pip" not in who:
        spots = {"whiskers": -44, "luna": 54}
    for w_ in ("luna", "whiskers", "pip"):
        if w_ not in who:
            continue
        sc = 0.62 * s if w_ != "pip" else 0.75 * s
        kw = dict(extra.get(w_, {}))
        if w_ in eyes:
            kw["eyes"] = eyes[w_]
        if w_ in look:
            kw["look"] = look[w_]
        pose = kw.pop("pose", "sit")
        kat(c, tl, t, w_, x + face * spots[w_] * s, top + kw.pop("dy", 0) * s, sc, face, pose, **kw)


# ============================================================================ helpers

def text(c, x, y, s, size, fill, anchor="mm", stroke=0, stroke_fill=OUT):
    """Canvas text whose size follows the current push() scale."""
    if size * c.scale < 1:
        return
    c.text(x, y, s, size * c.scale, fill, anchor=anchor, stroke=stroke * c.scale, stroke_fill=stroke_fill)


def text_w(s, size):
    return D.font(size).getlength(s) / SS


def wrap(s, size, width):
    """Split s into lines no wider than width (px) at this font size."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and text_w(trial, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def arrow(c, x0, y0, x1, y1, col=(255, 236, 90), w=8, k=1.0, head=22):
    """Outlined arrow from (x0, y0) toward (x1, y1); k grows it."""
    if k <= 0.01:
        return
    x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k)
    a = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - math.cos(a) * head, y1 - math.sin(a) * head
    c.stroke([(x0, y0), (bx, by)], col, w)
    px, py = -math.sin(a), math.cos(a)
    c.poly([(x1, y1), (bx + px * head * 0.7, by + py * head * 0.7), (bx - px * head * 0.7, by - py * head * 0.7)],
           col, w=3)


def label(c, x, y, s, size=30, tip=None, k=1.0, col=(48, 34, 40), bg=(255, 255, 255), arrow_col=None):
    """Rounded tag with text at (x, y); optional arrow from the tag to tip=(tx, ty)."""
    if k <= 0.01:
        return
    sc = pop(k)
    if tip is not None:
        tx, ty = tip
        a = math.atan2(ty - y, tx - x)
        hw = text_w(s, size) / 2 + 18
        hh = size * 0.7
        d = min(hw / max(1e-6, abs(math.cos(a))), hh / max(1e-6, abs(math.sin(a))))
        sx, sy = x + math.cos(a) * d, y + math.sin(a) * d
        arrow(c, sx, sy, tx, ty, arrow_col or bg, 6, ease_out(k * 1.3), head=18)
    c.push(x, y, sc)
    hw = text_w(s, size) / 2 + 18
    c.rect(-hw, -size * 0.7, hw, size * 0.7, bg, r=size * 0.6, w=3)
    text(c, 0, 1, s, size, col)
    c.pop()


def star(c, x, y, r, col=(255, 248, 200), ol=None):
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, col, ol=ol, w=2)


def sparkles(c, x, y, rad, t, n=10, k=1.0, seed=1, col=(255, 246, 190)):
    """Twinkling four-point stars scattered around (x, y)."""
    if k <= 0.01:
        return
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = rng.uniform(0, TAU) + t * rng.uniform(-0.6, 0.6)
        d = rad * math.sqrt(rng.uniform(0.05, 1))
        tw = 0.5 + 0.5 * math.sin(t * rng.uniform(4, 8) + i * 1.7)
        r = (4 + 9 * tw) * k * rng.uniform(0.6, 1.2)
        if r > 1:
            star(c, x + math.cos(a) * d, y + math.sin(a) * d, r, col)


def bubble(c, x, y, rx, ry, k, tail=(0, 0), fill=(255, 255, 255)):
    """Thought bubble centred at (x, y); tail points toward the thinker's head."""
    if k <= 0.02:
        return
    for f, r in ((0.3, 8), (0.6, 13)):
        c.circle(lerp(tail[0], x, f), lerp(tail[1], y + ry, f), r * k, fill, w=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.circle(x + math.cos(a) * rx * k, y + math.sin(a) * ry * k, ry * 0.3 * k, fill, w=2.5)
    c.ellipse(x, y, rx * k, ry * k, fill, ol=None)


def flash(c, k, col=(255, 252, 235)):
    """Blend the whole frame toward col by k (0..1)."""
    if k <= 0.003:
        return
    c.img.paste(col, (0, 0, c.img.size[0], c.img.size[1]), Image.new("L", c.img.size, int(clamp(k) * 255)))


def zoom(c, cx, cy, z):
    """Camera push-in: a new Canvas showing c magnified z times around (cx, cy)."""
    if z <= 1.001:
        return c
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, W - w)
    y0 = clamp(cy - h / 2, 0, H - h)
    img = c.img.resize(c.img.size, Image.BILINEAR, box=(x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS))
    return Canvas(img)


_shade = {}


def sub_band(c, tl, t, strength=0.55, top=560):
    """Soft dark band under the subtitles while somebody speaks (fades in and out)."""
    k = sum(1 / 3 for dt in (0.0, -0.25, 0.25) if tl.line_at(t + dt) is not None)
    q = int(round(k * strength * 20))
    if q <= 0:
        return
    if (q, top) not in _shade:
        h = (H - top) * SS
        ramp = np.linspace(0, 1, h) ** 1.4 * (q / 20) * 255
        _shade[(q, top)] = Image.fromarray(np.repeat(ramp[:, None], W * SS, axis=1).astype(np.uint8), "L")
    c.img.paste((18, 20, 36), (0, top * SS, W * SS, H * SS), _shade[(q, top)])


def inset(c, x, y, w, h, k, draw_fn, bg=(255, 255, 255), border=(255, 255, 255), radius=26):
    """Popup picture card centred at (x, y). draw_fn(ic) draws in local coords 0..w, 0..h."""
    if k <= 0.02:
        return
    ic = Canvas(size=(int(w), int(h)), bg=bg)
    draw_fn(ic)
    sc = pop(k)
    ww, hh = max(2, int(w * sc * SS)), max(2, int(h * sc * SS))
    img = ic.img.resize((ww, hh), Image.BILINEAR)
    mask = Image.new("L", (ww, hh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, ww - 1, hh - 1], radius=radius * sc * SS, fill=255)
    c.rect(x - w * sc / 2 + 6, y - h * sc / 2 + 8, x + w * sc / 2 + 6, y + h * sc / 2 + 8,
           (20, 20, 40), ol=None, r=radius * sc)
    c.img.paste(img, (int(round((x - w * sc / 2) * SS)), int(round((y - h * sc / 2) * SS))), mask)
    c.rect(x - w * sc / 2, y - h * sc / 2, x + w * sc / 2, y + h * sc / 2, None, ol=border, w=7, r=radius * sc)
    c.rect(x - w * sc / 2 - 3, y - h * sc / 2 - 3, x + w * sc / 2 + 3, y + h * sc / 2 + 3, None, ol=OUT, w=3,
           r=radius * sc + 3)


def compass(c, x, y, r, k=1.0, t=0.0, lit=(), words=None, spin=0.0):
    """Compass rose. lit: letters to light up ("N", "E", "S", "W"); words: {"N": "Never", ...}."""
    if k <= 0.01:
        return
    c.push(x, y, pop(k))
    c.circle(0, 0, r, (255, 250, 232), w=4)
    c.circle(0, 0, r * 0.8, None, ol=(200, 170, 120), w=2)
    rot = math.radians(spin)
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2 + rot
        long_ = i % 2 == 0
        rr = r * (0.78 if long_ else 0.48)
        wdt = r * (0.16 if long_ else 0.11)
        tip = (math.cos(a) * rr, math.sin(a) * rr)
        side = (math.cos(a + math.pi / 2) * wdt, math.sin(a + math.pi / 2) * wdt)
        col = (226, 60, 60) if i == 0 else (60, 70, 100) if long_ else (150, 160, 180)
        c.poly([tip, side, (0, 0)], col, w=2)
        c.poly([tip, (-side[0], -side[1]), (0, 0)], mix(col, (255, 255, 255), 0.35), w=2)
    c.circle(0, 0, r * 0.08, (250, 210, 80), w=2)
    for i, L in enumerate("NESW"):
        a = i * math.pi / 2 - math.pi / 2 + rot
        on = L in lit
        size = r * (0.42 if on else 0.32)
        px, py = math.cos(a) * r * 1.22, math.sin(a) * r * 1.22
        c.circle(px, py, size * 0.85 + (3 * math.sin(t * 6) if on else 0), (255, 226, 90) if on else (255, 255, 255),
                 w=3)
        text(c, px, py + 1, L, size, (226, 60, 60) if L == "N" else (40, 44, 70),
             stroke=2, stroke_fill=(255, 255, 255))
        if words and L in words and on:
            wx, wy = math.cos(a) * r * 1.22, math.sin(a) * r * 1.22
            ox = {"N": (0, -r * 0.5), "S": (0, r * 0.5), "E": (r * 0.25, r * 0.45), "W": (-r * 0.25, r * 0.45)}[L]
            label(c, wx + ox[0], wy + ox[1], words[L], max(16, r * 0.22), k=1.0)
    c.pop()


# ============================================================================== world

# Simple, recognisable outlines as (lon, lat) points.
NORTH_AMERICA = [
    (-168, 66), (-162, 70), (-150, 71), (-138, 69), (-125, 70), (-110, 68), (-95, 69), (-90, 68), (-86, 66),
    (-88, 64), (-94, 61), (-93, 58), (-88, 56), (-82, 55), (-79, 52), (-79, 57), (-77, 61), (-72, 62),
    (-65, 60), (-61, 56), (-56, 52), (-60, 47), (-66, 44), (-70, 42), (-74, 40), (-76, 36), (-80, 32),
    (-81, 28), (-80, 26), (-81, 25), (-82, 28), (-84, 30), (-89, 30), (-94, 29), (-97, 27), (-97, 22),
    (-95, 19), (-91, 19), (-90, 21), (-87, 21), (-88, 16), (-84, 15), (-83, 10), (-79, 9), (-77, 8),
    (-80, 7.5), (-85, 10), (-87, 13), (-92, 14), (-97, 16), (-105, 20), (-108, 25), (-114.5, 31.5),
    (-112.5, 28), (-110, 23), (-112, 25), (-114.5, 28), (-117, 32.5), (-120, 34.5), (-122.5, 37.5),
    (-124, 41), (-124, 46), (-125, 49), (-130, 54), (-135, 58), (-140, 60), (-147, 61), (-152, 59),
    (-158, 57), (-163, 55), (-158, 58), (-162, 60), (-165, 62)]
GREENLAND = [(-73, 78), (-60, 82), (-40, 83), (-22, 82), (-18, 77), (-22, 70), (-32, 68), (-42, 60),
             (-50, 62), (-54, 67), (-58, 75), (-68, 77)]
ARCTIC_ISLES = [
    [(-80, 73), (-70, 70), (-62, 66), (-66, 63), (-75, 65), (-85, 70)],
    [(-90, 80), (-75, 82), (-63, 81), (-78, 76), (-92, 77)],
    [(-118, 72), (-105, 73), (-100, 70), (-110, 68)],
    [(-85, 21.8), (-77, 20), (-74, 20.2), (-80, 23)],                       # Cuba
]
SOUTH_AMERICA = [
    (-77, 8), (-72, 12), (-64, 10.5), (-60, 8), (-52, 5), (-50, 0), (-44, -2), (-35, -5), (-35, -9),
    (-39, -14), (-40, -20), (-44, -23), (-48, -26), (-53, -33), (-58, -35), (-57, -38), (-62, -39),
    (-65, -42), (-66, -47), (-69, -51), (-68, -55), (-72, -54), (-75, -50), (-74, -44), (-73, -37),
    (-71, -30), (-70, -18), (-76, -14), (-81, -6), (-80, -2), (-80, 1), (-77, 4), (-78, 7)]
EURASIA = [
    (-9, 37), (-9, 43), (-2, 43.5), (-1.5, 46), (-4.5, 48), (-1, 49.5), (2, 51), (4, 52), (5, 53.4),
    (8, 54), (8.5, 57), (10.5, 57.7), (10.5, 54.5), (14, 54), (19, 54.5), (21, 57), (24, 57.5),
    (28, 59.5), (22, 60), (21, 61), (25, 65), (21, 64), (17.5, 61), (19, 59.5), (16.5, 57), (14, 55.5),
    (12.5, 56), (11, 58), (8, 58), (5, 59), (5, 62), (10, 64), (14, 67), (18, 69.5), (25, 71), (31, 70),
    (33, 69), (40, 67), (44, 68), (54, 68.5), (60, 69), (68, 69), (73, 72), (80, 73), (87, 75), (100, 77),
    (105, 78), (113, 74), (130, 72), (140, 72.5), (150, 71), (160, 70), (170, 70), (180, 68.5),
    (180, 65), (178, 62), (170, 60), (163, 56), (157, 51), (156, 57), (160, 61.5), (155, 59.5),
    (143, 59), (137, 54.5), (141, 52), (140, 48), (135, 43), (130, 42.5), (128, 38.5), (129.5, 35.5),
    (126.5, 34.5), (126, 37.5), (125, 39.7), (122, 40.5), (121.5, 39), (118, 39), (119, 37),
    (122.5, 37), (120.5, 34.5), (122, 31), (122, 29.5), (119.5, 25), (116, 22.8), (110.5, 21),
    (108, 21.5), (106.5, 20), (105.7, 18.5), (108.5, 15), (109, 11.5), (105, 8.6), (105, 10.5),
    (102, 12.5), (100.5, 13.5), (99, 10), (100.5, 7), (104, 1.3), (101, 3), (98.3, 8), (98.5, 13),
    (97.5, 16.5), (94.5, 16), (94, 19), (92, 21.5), (90, 22), (88, 21.5), (86.5, 20), (84.5, 18.5),
    (80.3, 15.5), (80, 11), (77.5, 8), (76.5, 9), (74.5, 14), (72.7, 20), (72.5, 21.5), (70, 22.5),
    (68.5, 23.5), (66.5, 25.5), (62, 25), (57.5, 25.7), (56.5, 27), (52, 28), (50, 30), (48, 30),
    (50, 27), (51.5, 25), (54, 24), (56, 26), (56.5, 24), (58.5, 23.5), (59.5, 22.5), (57.5, 19),
    (55, 17), (52, 15.5), (45, 13), (43, 13), (42.5, 16), (39, 21), (37, 25.5), (35, 28), (34.9, 29.5),
    (34.2, 31.3), (35, 33), (35.8, 35), (36, 36.7), (34, 36.3), (30, 36.3), (27.5, 37), (26.5, 39.5),
    (26.2, 40.6), (23, 40.3), (24, 38), (22.5, 36.5), (21, 38.5), (19.5, 40), (19.5, 42), (16, 43.5),
    (13.5, 45.5), (12.3, 45), (13.5, 43.5), (16, 41.5), (18.5, 40.2), (16.5, 39), (16, 38), (15.6, 40),
    (12.5, 41.5), (10.5, 43), (8.5, 44.3), (6, 43.1), (3, 43.3), (3.2, 42), (0.5, 40.5), (-0.5, 38.5),
    (-2, 36.8), (-5.6, 36), (-6.5, 36.8)]
EUROPE_ISLES = [
    [(-5.7, 50), (1.5, 51.2), (1.7, 52.7), (0, 53.5), (-1.5, 55), (-2, 57), (-1.8, 57.6), (-4, 58.6),
     (-5, 58.6), (-6, 57), (-5.5, 55.5), (-4.5, 54.7), (-3, 53.4), (-4.5, 52.8), (-5.2, 51.7), (-3, 51.4)],
    [(-6, 52.2), (-6, 54), (-7.3, 55.3), (-8.5, 54.5), (-10, 53.5), (-10, 51.6), (-8, 51.7)],
    [(-24, 65.5), (-22, 66.4), (-16, 66.5), (-13.5, 65.2), (-15, 64.3), (-19, 63.4), (-22.5, 63.8)],
    [(8.5, 41), (9.6, 41), (9.6, 39), (8.5, 39)],                                        # Corsica/Sardinia
    [(12.5, 38.1), (15.6, 38.2), (15.1, 36.7)],                                          # Sicily
]
ASIA_ISLES = [
    [(130, 31), (131, 34), (134, 34.5), (136, 34), (140, 35), (141, 38), (141.5, 41), (140, 41.5),
     (139.8, 38), (137, 37), (133, 35.5), (130.5, 33.5)],                               # Japan
    [(140, 42), (142, 42), (145.5, 43.3), (141.5, 45.4), (140, 43.5)],                    # Hokkaido
    [(95.5, 5.5), (98, 4), (104, -2), (106, -6), (102, -4), (97, 2)],                    # Sumatra
    [(105, -6), (114.5, -7.5), (114, -8.7), (106, -7.5)],                                # Java
    [(109, 1.5), (114, 4.5), (117, 7), (119, 5), (118, 1), (117, -1), (116, -4), (110.5, -3), (109, -1)],
    [(119.5, -1), (121, 1), (125, 1.5), (121.5, -1.5), (123, -5), (120.5, -5.5)],       # Sulawesi
    [(120, 18.5), (122.5, 18.5), (122, 14), (124, 12.5), (126, 7), (125, 6), (122, 7), (121, 12),
     (119.8, 16)],                                                                       # Philippines
    [(120.2, 22), (121, 25.2), (122, 25), (120.8, 22)],                                 # Taiwan
    [(80, 9.8), (82, 7.5), (81, 6), (80, 6.2), (79.8, 8)],                              # Sri Lanka
    [(108.6, 19.9), (110.5, 20.1), (110.6, 18.4), (108.7, 18.5)],                       # Hainan
    [(142, 46), (143.5, 49), (143, 54), (142.5, 54.3), (141.8, 50)],                     # Sakhalin
]
AFRICA = [
    (-17, 21), (-16, 25), (-13, 28), (-10, 30), (-9.5, 33), (-6, 35.8), (-2, 35.2), (3, 36.8),
    (10, 37.2), (11, 35), (10, 33.5), (15, 32), (20, 31), (20, 32.7), (23, 32.6), (25, 31.6), (29, 30.9),
    (32.3, 31.3), (34.2, 31.3), (34.9, 29.5), (34, 27.8), (32.6, 29.9), (33.5, 27), (35.5, 23.5),
    (37.3, 21), (38.5, 18), (39.5, 15.5), (41.5, 13.5), (43.3, 12), (44, 10.5), (51.2, 11.8), (51, 10.4),
    (48, 5), (44, 1), (41, -2), (39.3, -5), (39.5, -8), (40.5, -11), (40.5, -15), (37, -18), (35, -21),
    (35.5, -24), (32.8, -26), (31, -29.5), (28, -33), (25, -34), (20, -34.8), (18.4, -34), (17.8, -31),
    (15, -27), (14.5, -22.5), (11.8, -17), (13.5, -12), (12, -6), (9.5, -1), (9.5, 4), (6, 4.3),
    (3, 6.3), (-2, 4.8), (-7.5, 4.4), (-11.5, 7), (-13.5, 9.5), (-15, 11), (-17.5, 14.7), (-16.5, 17)]
MADAGASCAR = [(49.3, -12), (50.5, -15.5), (47, -25), (44, -25), (43.5, -21), (44.5, -16), (47, -14.5)]
AUSTRALIA = [
    (113.5, -22), (114, -26), (115, -34), (118, -35), (123, -34), (129, -31.6), (132, -32),
    (135.6, -34.8), (138.5, -35), (140, -38), (143.5, -38.8), (147, -38), (150, -37.5), (151.3, -33.5),
    (153.5, -28.5), (153, -25), (150.8, -22.5), (146, -19), (145.4, -15), (142.5, -10.7), (141.5, -13),
    (141.5, -17), (140, -17.6), (136.5, -15.6), (137, -12.3), (132.5, -11.5), (130, -13), (126, -14),
    (122, -17.5), (121, -19.5), (117, -20.7)]
OCEANIA_ISLES = [
    [(144.7, -40.7), (148.3, -41), (147.3, -43.3), (145.3, -42.5)],                       # Tasmania
    [(131, -1), (138, -1.5), (146, -5), (150.5, -10.5), (144, -8), (141, -9), (138, -8), (134, -4)],
    [(172.7, -34.5), (178.5, -37.7), (176.8, -40), (175, -41.5), (174.5, -39), (173, -35.5)],
    [(172.7, -40.5), (174.3, -41.5), (173, -43.5), (171, -45), (168.5, -46.6), (166.5, -46), (168, -44),
     (171, -42)],
]
ANTARCTICA = [
    (-180, -90), (-180, -78), (-160, -78), (-150, -76), (-135, -74.5), (-110, -74), (-100, -73), (-80, -73),
    (-68, -70), (-63, -64.5), (-58, -63.5), (-60, -66), (-62, -70), (-60, -75), (-45, -77.5), (-30, -76),
    (-20, -73), (-10, -71), (0, -70), (15, -70), (30, -69.5), (40, -68.5), (55, -66.5), (70, -67.5),
    (80, -67), (90, -66.5), (110, -66), (130, -66), (145, -67), (160, -70), (170, -72), (168, -78),
    (180, -78), (180, -90)]
LAKES = [
    [(28, 41.5), (27.8, 43.5), (30, 45.7), (32.5, 46), (33.5, 44.5), (36, 45.2), (38, 47), (39.5, 46.8),
     (37.5, 44.5), (40, 43.5), (41.5, 41.5), (38, 41), (35, 42), (31, 41.2)],              # Black Sea
    [(47, 44.5), (50, 46.7), (53, 47), (54.5, 44.5), (53, 41), (54, 37.3), (51, 36.8), (49, 38),
     (49.5, 40.5), (47.5, 42.5)],                                                          # Caspian Sea
]
DESERTS = [
    [(-16, 20), (-10, 28), (0, 31), (10, 31), (20, 30), (30, 30), (34, 26), (36, 20), (30, 16), (20, 15),
     (10, 15), (0, 15), (-12, 16)],                                                        # Sahara
    [(37, 28), (45, 30), (50, 26), (56, 22), (55, 18), (45, 15), (40, 20)],              # Arabia
    [(118, -21), (128, -19), (136, -20), (142, -24), (140, -30), (131, -30), (122, -28), (116, -25)],
    [(90, 45), (105, 45), (115, 42), (110, 38), (95, 39)],                                # Gobi
    [(15, -18), (24, -18), (26, -26), (20, -28), (16, -24)],                              # Kalahari
]

# label ids in the land raster
OCEAN, WAVE, LINE, GRID = 0, 1, 2, 3
NA, SA, EU, AF, AS, OC, AN, GL = 10, 11, 12, 13, 14, 15, 16, 17
LAND_SHAPES = ([(NA, NORTH_AMERICA), (GL, GREENLAND)] + [(NA, p) for p in ARCTIC_ISLES]
               + [(SA, SOUTH_AMERICA), (AS, EURASIA)] + [(EU, p) for p in EUROPE_ISLES]
               + [(AS, p) for p in ASIA_ISLES] + [(AF, AFRICA), (AF, MADAGASCAR), (OC, AUSTRALIA)]
               + [(OC, p) for p in OCEANIA_ISLES] + [(AN, ANTARCTICA)])
CONTINENT_IDS = {"north america": NA, "south america": SA, "europe": EU, "africa": AF, "asia": AS,
                 "australia": OC, "oceania": OC, "antarctica": AN, "greenland": GL}

CONTINENT_LABELS = {"North America": (-102, 46), "South America": (-60, -14), "Europe": (16, 53),
                    "Africa": (20, 6), "Asia": (92, 50), "Australia": (134, -25), "Antarctica": (20, -80)}
OCEAN_LABELS = {"Pacific Ocean": (-145, 8), "Atlantic Ocean": (-38, 22), "Indian Ocean": (78, -22),
                "Arctic Ocean": (-10, 80), "Southern Ocean": (-60, -64)}

STYLES = {
    # ocean, wave, outline, grid, land colours by id (None = use 'land'), desert colour
    "earth": dict(ocean=(64, 146, 222), wave=(116, 186, 240), line=(40, 52, 76), grid=None,
                  land={NA: (120, 190, 92), SA: (120, 190, 92), EU: (120, 190, 92), AF: (120, 190, 92),
                        AS: (120, 190, 92), OC: (120, 190, 92), AN: (240, 246, 252), GL: (236, 244, 250)},
                  desert=(236, 206, 128)),
    "continents": dict(ocean=(70, 150, 225), wave=(120, 188, 242), line=(40, 44, 70), grid=None,
                       land={NA: (255, 168, 80), SA: (140, 206, 90), EU: (172, 140, 232), AF: (255, 214, 86),
                             AS: (240, 118, 128), OC: (84, 200, 190), AN: (240, 246, 252), GL: (255, 168, 80)},
                       desert=None),
    "toy": dict(ocean=(122, 172, 186), wave=None, line=(96, 64, 44), grid=(100, 140, 150),
                land={NA: (238, 204, 140), SA: (204, 216, 140), EU: (228, 172, 158), AF: (242, 216, 146),
                      AS: (218, 190, 150), OC: (232, 182, 124), AN: (244, 238, 222), GL: (244, 238, 222)},
                desert=None),
}


def _xy(lon, lat, w, h):
    return ((lon + 180) / 360 * w, (90 - lat) / 180 * h)


@lru_cache(None)
def _raster(width, waves=False, grid=False):
    """Equirectangular label raster (uint8, height = width/2) and desert mask."""
    h = width // 2
    lab = Image.new("L", (width, h), OCEAN)
    d = ImageDraw.Draw(lab)
    u = width / 1024
    if waves:
        rng = np.random.default_rng(5)
        step = 34 * u
        for j in range(int(h / step) + 1):
            for i in range(int(width / step / 1.6) + 1):
                x = (i + (j % 2) * 0.5) * step * 1.6 + rng.uniform(-6, 6) * u
                y = j * step + rng.uniform(-5, 5) * u
                pts = [(x + k * 2.2 * u, y + math.sin(k * 0.8) * 2.2 * u) for k in range(9)]
                d.line(pts, fill=WAVE, width=max(1, int(1.6 * u)))
    ow = max(2, int(round(2.4 * u)))
    for _, poly in LAND_SHAPES:
        pts = [_xy(lo, la, width, h) for lo, la in poly]
        d.polygon(pts, fill=LINE)
        d.line(pts + [pts[0]], fill=LINE, width=2 * ow, joint="curve")
    for cid, poly in LAND_SHAPES:
        d.polygon([_xy(lo, la, width, h) for lo, la in poly], fill=cid)
    for poly in LAKES:
        pts = [_xy(lo, la, width, h) for lo, la in poly]
        d.polygon(pts, fill=OCEAN)
        d.line(pts + [pts[0]], fill=LINE, width=ow, joint="curve")
    arr = np.array(lab)
    # Europe / Asia split along the Urals, the Caspian, the Caucasus and the Bosporus
    lon = (np.arange(width) + 0.5) / width * 360 - 180
    lat = 90 - (np.arange(h) + 0.5) / h * 180
    border = np.where(lat >= 51, 60, np.where(lat >= 47, 52, np.where(lat > 41, 41, 26)))
    eu = lon[None, :] < border[:, None]
    arr[(arr == AS) & eu] = EU
    if grid:
        g = Image.fromarray(arr)
        gd = ImageDraw.Draw(g)
        for lo in range(-180, 180, 30):
            x = (lo + 180) / 360 * width
            gd.line([(x, 0), (x, h)], fill=GRID, width=max(1, int(u)))
        for la in range(-60, 90, 30):
            y = (90 - la) / 180 * h
            gd.line([(0, y), (width, y)], fill=GRID, width=max(1, int(u * (1.8 if la == 0 else 1))))
        arr = np.array(g)
    des = Image.new("L", (width, h), 0)
    dd = ImageDraw.Draw(des)
    for poly in DESERTS:
        dd.polygon([_xy(lo, la, width, h) for lo, la in poly], fill=255)
    des = np.array(des.filter(ImageFilter.GaussianBlur(3 * u))) > 110
    return arr, des


@lru_cache(None)
def texture(style="earth", width=2048, waves=False):
    """RGB uint8 array (width/2, width, 3): the coloured world in equirectangular projection."""
    st = STYLES[style]
    arr, des = _raster(width, waves, st["grid"] is not None)
    lut = np.zeros((256, 3), np.uint8)
    lut[:] = st["ocean"]
    lut[WAVE] = st["wave"] or st["ocean"]
    lut[LINE] = st["line"]
    if st["grid"]:
        lut[GRID] = st["grid"]
    for cid, col in st["land"].items():
        lut[cid] = col
    rgb = lut[arr]
    if st["desert"] is not None:
        land = (arr >= NA) & (arr != AN) & (arr != GL)
        rgb[des & land] = st["desert"]
    return rgb


# ---------------------------------------------------------------------------- globe

@lru_cache(maxsize=24)
def _globe_geom(rs, lat0, roll, th):
    n = 2 * rs
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (xx + 0.5 - rs) / rs
    y = (rs - yy - 0.5) / rs
    rr = x * x + y * y
    inside = rr <= 1.0
    x, y = x[inside], y[inside]
    z = np.sqrt(np.maximum(0, 1 - x * x - y * y))
    a = math.radians(roll)
    xr = x * math.cos(a) - y * math.sin(a)
    yr = x * math.sin(a) + y * math.cos(a)
    p0 = math.radians(lat0)
    lat = np.arcsin(np.clip(yr * math.cos(p0) + z * math.sin(p0), -1, 1))
    lon = np.degrees(np.arctan2(xr, z * math.cos(p0) - yr * math.sin(p0)))
    rows = np.clip(((90 - np.degrees(lat)) / 180 * th).astype(np.int32), 0, th - 1)
    L = np.array([-0.45, 0.55, 0.70])
    L /= np.linalg.norm(L)
    lam = np.maximum(0, x * L[0] + y * L[1] + z * L[2])
    shade = (0.62 + 0.45 * lam) * (1 - 0.18 * (1 - z) ** 2)
    spec = np.maximum(0, lam) ** 40 * 38
    return inside, rows, lon.astype(np.float32), lat.astype(np.float32), shade.astype(np.float32), \
        spec.astype(np.float32)


def globe_image(r_ss, lon=0.0, lat=15.0, style="earth", roll=0.0, sun=None, waves=False):
    """RGBA PIL image (about 2r x 2r supersampled pixels) of the globe."""
    rs = max(4, int(round(r_ss)))
    if rs > 240:                       # big globes: sample at half resolution, then scale up
        img = _globe_raw(rs // 2, lon, lat, style, roll, sun, waves)
        return img.resize((2 * rs, 2 * rs), Image.BILINEAR)
    return _globe_raw(rs, lon, lat, style, roll, sun, waves)


def _globe_raw(rs, lon, lat, style, roll, sun, waves):
    tw = 4096 if rs > 300 else 2048 if rs > 110 else 1024
    tex = texture(style, tw, waves)
    th = tex.shape[0]
    inside, rows, lonb, latb, shade, spec = _globe_geom(rs, round(lat, 1), round(roll, 1), th)
    glon = lonb + lon
    cols = ((glon + 540.0) * (tw / 360.0)).astype(np.int32) % tw
    rgb = tex[rows, cols].astype(np.float32)
    k = shade
    if sun is not None:
        slon, slat = math.radians(sun[0]), math.radians(sun[1])
        la = np.radians(latb)
        dot = np.sin(la) * math.sin(slat) + np.cos(la) * math.cos(slat) * np.cos(np.radians(glon) - slon)
        day = np.clip(dot * 5 + 0.5, 0, 1)
        k = shade * (0.3 + 0.7 * day)
        rgb *= (day[:, None] + (1 - day[:, None]) * np.array([0.55, 0.62, 1.0], np.float32))
    rgb *= k[:, None]
    rgb += spec[:, None]
    np.clip(rgb, 0, 255, out=rgb)
    out = np.zeros((2 * rs, 2 * rs, 4), np.uint8)
    out[inside, :3] = rgb.astype(np.uint8)
    out[inside, 3] = 255
    return Image.fromarray(out, "RGBA")


def globe(c, x, y, r, lon=0.0, lat=15.0, style="earth", roll=0.0, sun=None, glow=0.0, outline=True,
          waves=False, glow_col=(255, 240, 170)):
    """Draw the Earth as a ball centred at (x, y) with radius r (respects c.push scaling).

    lon: longitude facing the viewer (spin by changing it; it increases eastward, so
    lon = -t*20 turns the globe the way the real Earth turns). lat: latitude at the centre (tilt
    toward the viewer). roll: rotate the picture (e.g. -23.5 for an axis tilt).
    sun=(lon, lat): the point where the Sun is overhead -- the other side gets dark (night)."""
    if glow > 0.01:
        _halo(c, x, y, r, glow, glow_col)
    rs = r * c.scale * SS
    img = globe_image(rs, lon, lat, style, roll, sun, waves)
    px, py = c.P(x, y)
    c.img.paste(img, (int(round(px - img.size[0] / 2)), int(round(py - img.size[1] / 2))), img)
    if outline:
        c.circle(x, y, r, None, ol=OUT, w=LW + 1)


def _halo(c, x, y, r, k, col):
    """Additive-looking soft halo (drawn as fading rings blended into what is underneath)."""
    rad = r * (1.15 + 0.6 * k)
    px, py = c.P(x, y)
    R = int(rad * c.scale * SS)
    size = 2 * R + 4
    inner = round(r * c.scale * SS / max(1, R), 2)
    key = (R, inner)
    m = _halo_cache.get(key)
    if m is None:
        yy, xx = np.mgrid[0:size, 0:size]
        d = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2) / max(1, R)
        a = np.clip((1 - d) / max(1e-3, 1 - inner), 0, 1) ** 1.6
        m = Image.fromarray((a * 255).astype(np.uint8), "L")
        if len(_halo_cache) > 40:
            _halo_cache.clear()
        _halo_cache[key] = m
    m2 = m.point(lambda v: int(v * clamp(k)))
    c.img.paste(col, (int(px - size / 2), int(py - size / 2), int(px - size / 2) + size, int(py - size / 2) + size),
                m2)


_halo_cache = {}


def globe_xy(x, y, r, lon, lat, lon0=0.0, lat0=15.0, roll=0.0):
    """Screen position of (lon, lat) on a globe drawn with globe(c, x, y, r, lon0, lat0, roll=roll).
    Returns (sx, sy, visible) -- visible is False on the far side."""
    p, p0 = math.radians(lat), math.radians(lat0)
    dl = math.radians(lon - lon0)
    cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(dl)
    xr = math.cos(p) * math.sin(dl)
    yr = math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(dl)
    a = math.radians(roll)
    gx = xr * math.cos(a) + yr * math.sin(a)
    gy = -xr * math.sin(a) + yr * math.cos(a)
    return x + gx * r, y - gy * r, cosc > 0


# ------------------------------------------------------------------------ old globe

WOOD = (150, 98, 58)
WOOD_D = (112, 70, 40)
BRASS = (226, 184, 90)
BRASS_D = (176, 132, 56)


def old_globe(c, x, y, s=1.0, lon=0.0, glow=0.0, t=0.0, r=100):
    """Luna's old globe on a wooden stand. (x, y) = bottom of the stand. Globe centre is
    at (x, y - (r + 70) * s). glow 0..1 makes it shine with magic sparkles."""
    c.push(x, y, s)
    gy = -(r + 70)
    if glow > 0.01:
        _halo(c, 0, gy, r, glow, (255, 236, 150))
    c.ellipse(0, -8, 70, 16, WOOD_D)
    c.ellipse(0, -16, 64, 14, WOOD)
    c.rect(-10, -64, 10, -14, WOOD, r=4)
    c.ellipse(0, -66, 22, 8, WOOD_D)
    c.stroke([(0, -66), (0, gy + r + 6)], BRASS, 7)
    # back half of the meridian ring
    ring = r + 12
    a = math.radians(-23.5)
    pts = []
    for i in range(25):
        u = math.pi / 2 + math.pi * i / 24
        px, py = math.cos(u) * ring, math.sin(u) * ring
        pts.append((px * math.cos(a) - py * math.sin(a), gy + px * math.sin(a) + py * math.cos(a)))
    c.stroke(pts, BRASS_D, 6)
    globe(c, 0, gy, r, lon, 18, "toy", roll=-23.5)
    pts = []
    for i in range(25):
        u = -math.pi / 2 + math.pi * i / 24
        px, py = math.cos(u) * ring, math.sin(u) * ring
        pts.append((px * math.cos(a) - py * math.sin(a), gy + px * math.sin(a) + py * math.cos(a)))
    c.stroke(pts, BRASS, 7)
    top, bot = pts[0], pts[-1]
    c.circle(top[0], top[1], 6, BRASS, w=2)
    c.circle(bot[0], bot[1], 6, BRASS, w=2)
    if glow > 0.01:
        sparkles(c, 0, gy, r * 1.5, t, n=12, k=glow, seed=9)
    c.pop()


# ============================================================================ home

SILL_Y = 520          # the window-seat top where characters sit
GLOBE_X = 640         # where the old globe stands on the sill
SPOT = {"whiskers": 380, "luna": 860, "pip": 548, "cushion": 380}


@lru_cache(None)
def home_bg(mood="day"):
    """The friends' room: a big three-pane window above a wooden window seat.
    mood: "day" | "evening" | "night". Returns a supersampled RGB image (copy before drawing)."""
    night = mood == "night"
    eve = mood == "evening"
    wall = (246, 222, 186) if mood == "day" else (232, 186, 160) if eve else (88, 86, 128)
    c = Canvas(bg=wall)
    stripe = mix(wall, (255, 255, 255) if not night else (60, 60, 96), 0.3)
    for x in range(0, W, 70):
        c.rect(x + 30, 0, x + 40, H, stripe, ol=None)
    # outside
    sky = {"day": [(0, (110, 182, 246)), (1, (200, 234, 255))],
           "evening": [(0, (98, 92, 170)), (0.45, (238, 140, 130)), (1, (255, 210, 140))],
           "night": [(0, (16, 22, 60)), (1, (52, 58, 120))]}[mood]
    x0, y0, x1, y1 = 170, 40, 1110, SILL_Y - 34
    win = Canvas(D.gradient(int(x1 - x0) * SS, int(y1 - y0) * SS, sky), size=(x1 - x0, y1 - y0))
    ww, wh = x1 - x0, y1 - y0
    if night:
        D.stars(win, 3, 70, ww, wh * 0.7)
        D.moon(win, ww - 170, 90, 34, sky=(30, 36, 84))
    elif eve:
        win.glow(ww * 0.7, wh * 0.78, 260, 140, (255, 236, 170), (250, 170, 130), steps=10)
        win.circle(ww * 0.7, wh * 0.8, 44, (255, 220, 130), ol=None)
    else:
        win.circle(ww - 150, 86, 40, (255, 226, 96), ol=None)
        D.cloud(win, 170, 90, 0.8)
        D.cloud(win, 560, 130, 0.6)
    tint = (0, 0, 0) if not night else (20, 24, 60)
    k = 0 if mood == "day" else 0.15 if eve else 0.55
    win.poly([(0, wh * 0.72), (200, wh * 0.6), (420, wh * 0.7), (640, wh * 0.58), (ww, wh * 0.7), (ww, wh),
              (0, wh)], mix((150, 200, 120), tint, k), ol=None)
    win.poly([(0, wh * 0.86), (300, wh * 0.78), (700, wh * 0.84), (ww, wh * 0.8), (ww, wh), (0, wh)],
             mix((110, 176, 96), tint, k), ol=None)
    for hx, hw_, hh, col in ((640, 70, 60, (232, 120, 100)), (730, 56, 48, (240, 200, 120)),
                             (820, 64, 56, (200, 120, 150))):
        bx, by = hx, wh * 0.84
        win.rect(bx - hw_ / 2, by - hh, bx + hw_ / 2, by, mix((250, 240, 220), tint, k), ol=None)
        win.poly([(bx - hw_ / 2 - 8, by - hh), (bx, by - hh - 36), (bx + hw_ / 2 + 8, by - hh)],
                 mix(col, tint, k), ol=None)
        win.rect(bx - 8, by - hh * 0.6, bx + 8, by - hh * 0.25,
                 (255, 226, 130) if night or eve else mix((150, 200, 240), tint, k), ol=None)
    D.tree(win, 110, wh * 0.9, 0.9, leaf=mix((90, 165, 85), tint, k), trunk=mix((130, 90, 60), tint, k))
    c.img.paste(win.finish().resize((ww * SS, wh * SS)), (x0 * SS, y0 * SS))
    # frame + mullions
    frame = (255, 250, 240) if not night else (170, 166, 196)
    for mx in (483, 797):
        c.rect(mx - 6, y0, mx + 6, y1, frame, w=2)
    c.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 6, None, ol=frame, w=14)
    c.rect(x0 - 21, y0 - 21, x1 + 21, y1 + 10, None, ol=OUT, w=3)
    c.rect(x0, y0, x1, y1, None, ol=OUT, w=2)
    # curtains
    cur = (90, 130, 200) if not night else (70, 80, 140)
    for side in (-1, 1):
        cx = 150 if side < 0 else 1130
        pts = [(cx - 70, 10), (cx + 70, 10), (cx + 50, 240), (cx + 70, SILL_Y - 12), (cx - 70, SILL_Y - 12), (cx - 40, 240)]
        c.poly(pts, cur)
        for fx in (-35, 0, 35):
            c.line([(cx + fx, 20), (cx + fx * 0.6, 240), (cx + fx, SILL_Y - 22)], mix(cur, (0, 0, 0), 0.2), 3)
        c.rect(cx - 60, 234, cx + 60, 250, (250, 200, 80), r=6, w=2)
    c.rect(40, 0, 1240, 14, (150, 98, 58), r=6)
    # window seat
    seat = (196, 140, 92) if not night else (120, 92, 92)
    c.rect(60, SILL_Y - 4, 1220, SILL_Y + 22, mix(seat, (255, 255, 255), 0.15), r=6)
    c.rect(80, SILL_Y + 22, 1200, H + 10, seat)
    for px in (120, 470, 820):
        c.rect(px, SILL_Y + 56, px + 310, H - 20, mix(seat, (0, 0, 0), 0.1), r=8, w=2)
        c.circle(px + 155, SILL_Y + 70, 6, BRASS, w=2)
    # books on the sill + plant
    for i, (bw, bh, col) in enumerate(((22, 70, (210, 70, 70)), (18, 62, (70, 130, 200)),
                                      (26, 76, (240, 190, 70)), (16, 58, (100, 170, 100)))):
        bx = 1012 + sum(b[0] for b in ((22,), (18,), (26,), (16,))[:i])
        c.rect(bx, SILL_Y - bh, bx + bw, SILL_Y, col, w=2, r=2)
        c.line([(bx + 4, SILL_Y - bh + 10), (bx + bw - 4, SILL_Y - bh + 10)], (255, 255, 255), 2)
    c.rect(1104, SILL_Y - 50, 1156, SILL_Y, (196, 100, 70), r=6)
    for dx, dy in ((-24, -12), (0, -44), (24, -14), (-12, -32), (14, -38)):
        c.ellipse(1130 + dx, SILL_Y - 50 + dy, 12, 26, (80, 160, 90))
    if night:
        c.glow(640, 300, 700, 380, (120, 116, 170), (88, 86, 128), steps=6)
    return c.img


# ============================================================================ space

@lru_cache(None)
def space_bg():
    """Deep blue-violet starry backdrop (the magic map floats in it)."""
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (16, 18, 52)), (0.6, (38, 30, 86)), (1, (60, 40, 104))]))
    c.glow(300, 200, 420, 260, (70, 60, 140), (30, 28, 72), steps=10)
    c.glow(1000, 560, 420, 240, (80, 50, 120), (50, 36, 98), steps=10)
    rng = np.random.default_rng(12)
    for _ in range(260):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.0)
        c.circle(x, y, r, mix((255, 250, 220), (140, 150, 220), rng.random() * 0.5), ol=None)
    for _ in range(14):
        star(c, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(5, 9), (255, 248, 210))
    return c.img


def twinkle(c, t, n=24, seed=3):
    """A few animated twinkles on top of space_bg()."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        k = 0.5 + 0.5 * math.sin(t * rng.uniform(1.5, 4) + i)
        if k > 0.55:
            star(c, x, y, 3 + 6 * (k - 0.55), (255, 250, 220))


# ============================================================================== map

MW, MH = 1280, 640           # map size in map units (= output px at zoom 1)


def lonlat_to_map(lon, lat):
    return ((lon + 180) / 360 * MW, (90 - lat) / 180 * MH)


class MapView:
    """Camera on the magic map: centre (lon, lat) and zoom (1 = whole world 1280 px wide)."""

    def __init__(self, lon=0.0, lat=0.0, zoom=1.0):
        self.lon, self.lat, self.z = lon, lat, zoom
        self.cx, self.cy = lonlat_to_map(lon, lat)

    def m2s(self, mx, my):
        return W / 2 + (mx - self.cx) * self.z, H / 2 + (my - self.cy) * self.z

    def xy(self, lon, lat):
        return self.m2s(*lonlat_to_map(lon, lat))

    def rect(self):
        x0, y0 = self.m2s(0, 0)
        x1, y1 = self.m2s(MW, MH)
        return x0, y0, x1, y1


def lerp_view(a, b, k):
    """Camera move between two (lon, lat, zoom) tuples; zoom changes geometrically."""
    k = clamp(k)
    z = a[2] * (b[2] / a[2]) ** k
    # keep the motion steady on screen: interpolate the centre weighted by zoom
    wa, wb = a[2], b[2]
    f = (k * wb) / ((1 - k) * wa + k * wb) if (wa + wb) else k
    f = lerp(k, f, 0.6)
    return (lerp(a[0], b[0], f), lerp(a[1], b[1], f), z)


@lru_cache(None)
def map_image(style="earth", level=1):
    """Map picture: level 1 = SS px per map unit (2560 wide), level 2 = 2*SS (5120 wide)."""
    width = MW * SS * level
    if level == 1 and MW * SS * 2 <= 5120:
        return map_image(style, 2).reduce(2)
    return Image.fromarray(texture(style, width, waves=True))


def draw_map(c, v, style="earth"):
    """Paint the map as seen by MapView v into canvas c (with a soft shadow and an outline)."""
    x0, y0, x1, y1 = v.rect()
    c.rect(x0 + 10, y0 + 12, x1 + 10, y1 + 12, (12, 12, 34), ol=None, r=6)
    sx0, sy0 = max(0, int(math.floor(x0 * SS))), max(0, int(math.floor(y0 * SS)))
    sx1, sy1 = min(W * SS, int(math.ceil(x1 * SS))), min(H * SS, int(math.ceil(y1 * SS)))
    if sx1 - sx0 < 2 or sy1 - sy0 < 2:
        return
    level = 2 if v.z > 1.02 else 1
    src = map_image(style, level)
    p = SS * level                      # source px per map unit
    def to_map(px, py):
        return (v.cx + (px / SS - W / 2) / v.z, v.cy + (py / SS - H / 2) / v.z)
    mx0, my0 = to_map(sx0, sy0)
    mx1, my1 = to_map(sx1, sy1)
    box = (max(0, mx0 * p), max(0, my0 * p), min(src.size[0], mx1 * p), min(src.size[1], my1 * p))
    piece = src.resize((sx1 - sx0, sy1 - sy0), Image.BILINEAR, box=box)
    c.img.paste(piece, (sx0, sy0))
    c.rect(x0, y0, x1, y1, None, ol=OUT, w=4)


def map_clip(c, v):
    """Repaint the space around the map (hides anything drawn past the map's edges)."""
    x0, y0, x1, y1 = v.rect()
    bg = space_bg()
    for box in ((0, 0, W, y0), (0, y1, W, H), (0, y0, x0, y1), (x1, y0, W, y1)):
        a = [int(round(clamp(b, 0, W if i % 2 == 0 else H) * SS)) for i, b in enumerate(box)]
        if a[2] - a[0] > 0 and a[3] - a[1] > 0:
            c.img.paste(bg.crop(a), (a[0], a[1]))
    c.rect(x0, y0, x1, y1, None, ol=OUT, w=4)


def map_view(lon=0.0, lat=0.0, zoom=1.0, style="earth", labels=None, label_k=1.0, t=0.0):
    """A fresh Canvas with the magic map floating in space. Returns (canvas, MapView)."""
    v = MapView(lon, lat, zoom)
    c = Canvas(space_bg().copy())
    twinkle(c, t)
    draw_map(c, v, style)
    if labels:
        map_labels(c, v, labels, label_k)
    return c, v


def map_label(c, v, lon, lat, s, size=26, col=(255, 255, 255), k=1.0, stroke_col=OUT):
    if k <= 0.01:
        return
    x, y = v.xy(lon, lat)
    if -200 < x < W + 200 and -50 < y < H + 50:
        c.push(x, y, pop(k))
        text(c, 0, 0, s, size, col, stroke=3, stroke_fill=stroke_col)
        c.pop()


def map_labels(c, v, which="all", k=1.0):
    """Continent and/or ocean names; size grows gently with the zoom."""
    names = []
    if which in ("continents", "all"):
        names += [(n, p, (255, 255, 255)) for n, p in CONTINENT_LABELS.items()]
    if which in ("oceans", "all"):
        names += [(n, p, (210, 236, 255)) for n, p in OCEAN_LABELS.items()]
    if isinstance(which, (list, tuple)):
        allp = {**CONTINENT_LABELS, **OCEAN_LABELS}
        names = [(n, allp[n], (255, 255, 255)) for n in which]
    size = 22 * min(1.8, v.z ** 0.5)
    for n, (lo, la), col in names:
        map_label(c, v, lo, la, n, size, col, k)


@lru_cache(None)
def _continent_mask(cid):
    arr, _ = _raster(MW * SS * 2, True, False)
    m = Image.fromarray(((arr == cid) * 255).astype(np.uint8), "L")
    return m.reduce(2)


def map_highlight(c, v, name, k=1.0, col=(255, 240, 120), t=0.0):
    """Glowing tint over one continent ("africa", "europe", ...), pulsing gently."""
    if k <= 0.01:
        return
    cid = CONTINENT_IDS[name.lower()]
    mask = _continent_mask(cid)                     # SS px per map unit
    x0, y0, x1, y1 = v.rect()
    sx0, sy0 = max(0, int(x0 * SS)), max(0, int(y0 * SS))
    sx1, sy1 = min(W * SS, int(x1 * SS)), min(H * SS, int(y1 * SS))
    if sx1 - sx0 < 2 or sy1 - sy0 < 2:
        return
    p = SS
    mx0, my0 = v.cx + (sx0 / SS - W / 2) / v.z, v.cy + (sy0 / SS - H / 2) / v.z
    mx1, my1 = v.cx + (sx1 / SS - W / 2) / v.z, v.cy + (sy1 / SS - H / 2) / v.z
    # clamp: at fractional map edges the box can poke slightly outside the mask
    box = (max(0.0, mx0 * p), max(0.0, my0 * p), min(mask.size[0], mx1 * p), min(mask.size[1], my1 * p))
    piece = mask.resize((sx1 - sx0, sy1 - sy0), Image.BILINEAR, box=box)
    a = clamp(k) * (0.45 + 0.15 * math.sin(t * 5))
    piece = piece.point(lambda q: int(q * a))
    c.img.paste(col, (sx0, sy0, sx1, sy1), piece)


def spline(pts, n=14):
    """Catmull-Rom curve through the points."""
    if len(pts) < 3:
        return [(lerp(pts[0][0], pts[-1][0], i / n), lerp(pts[0][1], pts[-1][1], i / n)) for i in range(n + 1)]
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            u = j / n
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * u + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * u * u
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * u ** 3) for d in (0, 1)))
    out.append(pts[-1])
    return out


def _path_screen(v, pts):
    s = [v.xy(lo, la) for lo, la in spline(pts)]
    d = [0.0]
    for a, b in zip(s, s[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return s, d


def path_point(v, pts, u):
    """Screen (x, y, angle) at fraction u along the smoothed path."""
    s, d = _path_screen(v, pts)
    L = d[-1] * clamp(u)
    for i in range(1, len(s)):
        if d[i] >= L:
            f = (L - d[i - 1]) / max(1e-6, d[i] - d[i - 1])
            a, b = s[i - 1], s[i]
            return lerp(a[0], b[0], f), lerp(a[1], b[1], f), math.atan2(b[1] - a[1], b[0] - a[0])
    a, b = s[-2], s[-1]
    return b[0], b[1], math.atan2(b[1] - a[1], b[0] - a[0])


def map_path(c, v, pts, u=1.0, col=(255, 236, 110), w=5, dash=16, gap=11, head=True):
    """Dotted travel path through lon/lat waypoints, drawn up to fraction u. Returns head (x, y, angle)."""
    s, d = _path_screen(v, pts)
    L = d[-1] * clamp(u)
    pos = 0.0
    segs = []
    while pos < L:
        segs.append((pos, min(L, pos + dash)))
        pos += dash + gap

    def at(l):
        for i in range(1, len(s)):
            if d[i] >= l:
                f = (l - d[i - 1]) / max(1e-6, d[i] - d[i - 1])
                return lerp(s[i - 1][0], s[i][0], f), lerp(s[i - 1][1], s[i][1], f)
        return s[-1]
    for a, b in segs:
        pa, pb = at(a), at(b)
        c.line([pa, pb], OUT, w + 4)
    for a, b in segs:
        c.line([at(a), at(b)], col, w)
    hx, hy, ang = path_point(v, pts, u)
    if head and u > 0.02:
        r = 6 + w * 2
        tip = (hx + math.cos(ang) * r, hy + math.sin(ang) * r)
        l1 = (hx + math.cos(ang + 2.4) * r, hy + math.sin(ang + 2.4) * r)
        l2 = (hx + math.cos(ang - 2.4) * r, hy + math.sin(ang - 2.4) * r)
        c.poly([tip, l1, l2], col, w=3)
    return hx, hy, ang


def you_are_here(c, x, y, t=0.0, k=1.0, s="You are here!", size=24, side=1):
    """Bouncing red map pin at (x, y) (its tip) with a pulsing ring and a label."""
    if k <= 0.01:
        return
    sc = pop(k)
    for i in range(2):
        u = (t * 0.8 + i * 0.5) % 1.0
        c.ellipse(x, y, (10 + 30 * u) * sc, (4 + 12 * u) * sc, None, ol=mix((255, 90, 80), (255, 255, 255), u), w=3)
    bounce = abs(math.sin(t * 4)) * 8
    c.push(x, y - bounce, sc)
    c.poly([(0, 0), (-14, -30), (14, -30)], (226, 56, 60), w=3)
    c.circle(0, -38, 18, (236, 70, 70), w=3)
    c.circle(0, -38, 7, (255, 255, 255), ol=None)
    c.pop()
    if s:
        label(c, x + side * (text_w(s, size) / 2 + 40), y - 70 - bounce, s, size, k=k, col=(200, 40, 50))


# ===================================================================== globe -> map

def globe_to_map(c, k, t=0.0, r=230, style="earth", lon=0.0):
    """Fullscreen morph on c: a globe of radius r at the centre (k=0) stretches out into the
    flat world map at zoom 1 (k=1). Spin the globe to lon=0 before starting."""
    e = ease(k)
    gw = lerp(2 * r, MW, e)
    gh = lerp(2 * r, MH, e)
    rad = lerp(r, 6, ease(clamp(k * 1.4)))
    x0, y0 = W / 2 - gw / 2, H / 2 - gh / 2
    ww, hh = max(4, int(gw * SS)), max(4, int(gh * SS))
    if e < 0.999:
        g = globe_image(r * SS, lon, 0.0, style).convert("RGB").resize((ww, hh), Image.BILINEAR)
    m = map_image(style, 1).resize((ww, hh), Image.BILINEAR)
    blend = clamp((e - 0.15) / 0.6)
    img = m if e >= 0.999 else Image.blend(g, m, blend)
    mask = Image.new("L", (ww, hh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, ww - 1, hh - 1], radius=rad * SS, fill=255)
    c.rect(x0 + 10, y0 + 12, x0 + gw + 10, y0 + gh + 12, (12, 12, 34), ol=None, r=rad)
    c.img.paste(img, (int(x0 * SS), int(y0 * SS)), mask)
    c.rect(x0, y0, x0 + gw, y0 + gh, None, ol=OUT, w=4, r=rad)


# ============================================================================== cards

LOGO_COLS = [(255, 120, 90), (255, 200, 70), (130, 210, 100), (90, 190, 240), (190, 140, 240), (255, 150, 190)]


def logo(c, x, y, size, t=0.0, k=1.0, text_="Whiskers & Luna's World"):
    """Series logo: chunky multi-coloured letters popping in one by one (k 0..1)."""
    total = text_w(text_, size) + 2 * len(text_)
    cx = x - total / 2
    n = len(text_)
    j = 0
    for i, ch in enumerate(text_):
        w_ = text_w(ch, size) + 2
        if ch != " ":
            ki = clamp(k * (n + 6) / 6 - i / 6)
            if ki > 0.01:
                bob = math.sin(t * 3 + i * 0.5) * 3
                c.push(cx + w_ / 2, y + bob, pop(ki))
                col = LOGO_COLS[j % len(LOGO_COLS)] if ch not in "&'" else (255, 255, 255)
                text(c, 0, 0, ch, size, col, stroke=5, stroke_fill=OUT)
                c.pop()
            j += 1
        cx += w_


def ribbon(c, x, y, w, h, col=(226, 70, 80), k=1.0):
    """A banner ribbon with folded tails, centred at (x, y)."""
    if k <= 0.01:
        return
    w = w * ease_out(k)
    dark = mix(col, (0, 0, 0), 0.3)
    for side in (-1, 1):
        ex = x + side * w / 2
        c.poly([(ex - side * 20, y - h / 2 + 14), (ex + side * 50, y - h / 2 + 14), (ex + side * 30, y + 8),
                (ex + side * 50, y + h / 2 + 14), (ex - side * 20, y + h / 2 + 14)], dark)
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, r=10)


def title_card(tl, t, t0, ep, topic):
    """Series title card. t0 = when the card starts (the animation runs ~3 s, then idles).
    ep: episode number; topic: e.g. "Our Planet"."""
    tt = t - t0
    c = Canvas(space_bg().copy())
    twinkle(c, t, 40)
    k = ease_out(tt / 1.6)
    r = lerp(40, 170, k)
    gx, gy = 640, lerp(500, 400, k)
    globe(c, gx, gy, r, lon=-t * 18 + 20, lat=20, style="earth", glow=0.6 * k)
    if tt > 0.6:
        kk = ease_out((tt - 0.6) / 0.7)
        for who, dx, face in (("whiskers", -98, 1), ("luna", 98, -1)):
            yy = gy - math.sqrt(max(0, r * r - dx * dx)) + 6
            kat(c, tl, t, who, gx + dx * (r / 170), lerp(yy + 80, yy, kk) if kk < 1 else yy, 0.7 * kk, face, "sit",
                look=(0.5 * -face, -1))
        kat(c, tl, t, "pip", gx, gy - r + 2 - 60 * (1 - kk), 0.9 * kk, 1, proud=True)
    logo(c, 640, 92, 66, t, clamp((tt - 0.4) / 1.4))
    kb = clamp((tt - 1.6) / 0.6)
    label_ = f"Episode {ep}:  {topic}"
    ribbon(c, 640, 640, min(1180, max(560, 19 * len(label_) + 100)), 66, k=kb)   # widens for long topics
    if kb > 0.5:
        text(c, 640, 640, label_, 36, (255, 255, 255), stroke=3)
    sparkles(c, 640, 380, 300, t, n=14, k=k, seed=21)
    return c


def end_card(c, k, line1="Next time:", line2="", t=0.0):
    """Overlay ribbon for the last seconds: 'Next time: ...' (k fades/pops it in)."""
    if k <= 0.01:
        return
    y = lerp(-80, 96, ease_out(k))
    w = max(text_w(line2, 40), text_w(line1, 30)) + 120
    c.rect(640 - w / 2 + 6, y - 64 + 8, 640 + w / 2 + 6, y + 56 + 8, (20, 20, 40), ol=None, r=26)
    c.rect(640 - w / 2, y - 64, 640 + w / 2, y + 56, (255, 250, 236), r=26, w=4)
    text(c, 640, y - 30, line1, 30, (90, 100, 160))
    text(c, 640, y + 18, line2, 40, (226, 70, 80), stroke=2, stroke_fill=(255, 255, 255))
    sparkles(c, 640, y, w / 2 + 40, t, n=8, k=k, seed=31)


@lru_cache(None)
def _remember_bg():
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (96, 168, 238)), (1, (170, 220, 255))]))
    rng = np.random.default_rng(7)
    for _ in range(60):
        c.circle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 16),
                 mix((255, 255, 255), (150, 200, 250), rng.random() * 0.6), ol=None)
    c.rect(120, 140, 1160, 616, (20, 40, 80), ol=None, r=34)
    c.rect(110, 128, 1150, 604, (255, 252, 242), r=34, w=4)
    for y in range(230, 600, 140):
        c.line([(160, y + 46), (1100, y + 46)], (226, 220, 206), 2, cap=False)
    return c.img


ROW_COLS = [(236, 90, 90), (70, 150, 230), (90, 180, 100)]


def remember_card(t, facts, ks, icons=None, active=None, bg=None, title="Remember!"):
    """The 'Remember!' card. facts: 3 short strings; ks: reveal progress 0..1 for each;
    icons: list of fn(c, x, y, r, t) or None (shows the number); active: index to highlight."""
    c = Canvas((bg or _remember_bg()).copy())
    ribbon(c, 640, 120, 520, 82, (240, 180, 50), 1.0)
    for sx in (430, 850):
        star(c, sx, 118, 18 + 3 * math.sin(t * 4 + sx), (255, 255, 255), ol=OUT)
    text(c, 640, 120, title, 58, (255, 255, 255), stroke=4)
    for i, fact in enumerate(facts):
        k = ks[i] if i < len(ks) else 0
        if k <= 0.01:
            continue
        y = 236 + i * 128
        dx = (1 - ease_out(k)) * 500
        if active == i:
            c.rect(150 + dx, y - 56, 1110 + dx, y + 56, (255, 244, 190), ol=None, r=24)
        c.push(206 + dx, y, pop(k))
        c.circle(0, 0, 34, ROW_COLS[i % 3], w=3)
        text(c, 0, 1, str(i + 1), 40, (255, 255, 255), stroke=2)
        c.pop()
        c.push(312 + dx, y, pop(clamp(k * 1.2 - 0.1)))
        c.circle(0, 0, 50, (236, 244, 252), w=3)
        if icons and i < len(icons) and icons[i]:
            icons[i](c, 0, 0, 44, t)
        c.pop()
        size = 42
        lines = wrap(fact, size, 720)
        if len(lines) > 2:
            size = 34
            lines = wrap(fact, size, 740)
        for j, ln in enumerate(lines):
            text(c, 390 + dx, y + (j - (len(lines) - 1) / 2) * size * 1.15, ln, size, (48, 40, 60), anchor="lm")
    return c


@lru_cache(None)
def _quiz_bg():
    c = Canvas(D.gradient(W * SS, H * SS, [(0, (120, 86, 200)), (1, (70, 56, 150))]))
    rng = np.random.default_rng(3)
    for _ in range(26):
        c.text(rng.uniform(0, W), rng.uniform(0, H), "?", rng.uniform(40, 90), (140, 110, 216))
    return c.img


def quiz_card(t, question, choices=None, answer=0, ask=1.0, count=0.0, reveal=0.0, icons=None, number=1,
              answer_text=None):
    """Quiz card. ask/count/reveal are 0..1 progress values (question pops in, countdown 3-2-1,
    answer reveal). choices: up to 2 short strings (with icons: fn(c, x, y, r, t)); answer: index of
    the right choice; answer_text: the big answer banner shown at the reveal."""
    c = Canvas(_quiz_bg().copy())
    c.push(640, 66, pop(ask))
    c.rect(-150, -38, 150, 38, (255, 214, 70), r=38, w=4)
    text(c, 0, 1, f"Quiz time!  {number}" if number else "Quiz time!", 36, (110, 60, 30))
    c.pop()
    k = ease_out(ask)
    lines = wrap(question, 38, 960)
    qh = 40 + 46 * len(lines)
    qy = 112 + (1 - k) * -300
    c.rect(130, qy, 1150, qy + qh, (255, 255, 255), r=24, w=4)
    for j, ln in enumerate(lines):
        text(c, 640, qy + 42 + j * 46, ln, 38, (48, 40, 70))
    if choices:
        cy = 392
        for i, ch in enumerate(choices):
            cx = 360 if i == 0 else 920
            ki = clamp(ask * 2 - 0.5 - i * 0.3)
            if ki <= 0.01:
                continue
            right = i == answer
            sc = pop(ki) * (1 + 0.08 * ease_out(reveal) * (1 if right else -0.6))
            dim = 0.55 * ease_out(reveal) if not right else 0.0
            c.push(cx, cy, sc)
            col = mix((255, 255, 255), (120, 110, 150), dim)
            if right and reveal > 0:
                c.rect(-196, -146, 196, 146, (120, 220, 110), ol=None, r=34)
            c.rect(-180, -130, 180, 130, col, r=28, w=4)
            if icons and i < len(icons) and icons[i]:
                c.push(0, -24, 1.0)
                icons[i](c, 0, 0, 72, t)
                c.pop()
            text(c, 0, 92, ch, 32, mix((48, 40, 70), (120, 110, 150), dim))
            if right and reveal > 0.2:
                kk = pop((reveal - 0.2) / 0.5)
                c.push(150, -110, kk)
                c.circle(0, 0, 36, (70, 190, 90), w=4)
                c.line([(-16, 0), (-4, 13), (18, -14)], (255, 255, 255), 8)
                c.pop()
            c.pop()
    if 0 < count < 1 and reveal <= 0:
        cx, cy = (640, 392) if choices else (1110, 220)
        n = 3 - int(count * 3)
        f = (count * 3) % 1
        c.circle(cx, cy, 66, (255, 255, 255), w=4)
        pts = [(cx + math.sin(-a) * 56, cy - math.cos(a) * 56)
               for a in np.linspace(0, TAU * (1 - f), 40)]
        if len(pts) > 1:
            c.line(pts, (255, 196, 60), 12)
        c.push(cx, cy, 1 + 0.25 * (1 - ease_out(f * 3)))
        text(c, 0, 2, str(n), 72, (226, 70, 80), stroke=3, stroke_fill=(255, 255, 255))
        c.pop()
    if reveal > 0 and answer_text:
        kk = pop(reveal * 1.5)
        c.push(640, 604, kk)
        w_ = text_w(answer_text, 40) / 2 + 50
        c.rect(-w_, -40, w_, 40, (80, 190, 100), r=40, w=4)
        text(c, 0, 1, answer_text, 40, (255, 255, 255), stroke=3, stroke_fill=(30, 90, 40))
        c.pop()
        sparkles(c, 640, 600, 380, t, n=12, k=reveal, seed=8, col=(255, 240, 150))
    return c


# --------------------------------------------------------------- ready-made icons

def icon_globe(c, x, y, r, t=0.0):
    globe(c, x, y, r * 0.95, lon=-t * 30, lat=15)


def icon_water(c, x, y, r, t=0.0):
    """A ball cut into 4 parts: 3 blue (water), 1 green (land)."""
    pie(c, x, y, r * 0.95, [(64, 146, 222), (64, 146, 222), (64, 146, 222), (118, 190, 92)], 1.0)


def icon_compass(c, x, y, r, t=0.0):
    compass(c, x, y, r * 0.62, 1.0, t)


def pie(c, x, y, r, cols, k=1.0, start=-90, gap=0.0):
    """Pie split into len(cols) equal slices, drawn clockwise from the top; k reveals slices."""
    n = len(cols)
    shown = k * n
    for i, col in enumerate(cols):
        f = clamp(shown - i)
        if f <= 0:
            continue
        a0 = math.radians(start + 360 * i / n)
        a1 = math.radians(start + 360 * (i + f) / n)
        mid = (a0 + a1) / 2
        ox, oy = math.cos(mid) * gap, math.sin(mid) * gap
        pts = [(x + ox, y + oy)] + [(x + ox + math.cos(a) * r, y + oy + math.sin(a) * r)
                                    for a in np.linspace(a0, a1, 16)]
        c.poly(pts, col, w=3)


# ============================================================================== sound

MAJ, MIN = (0, 4, 7), (0, 3, 7)
KIT_MOODS = {
    "w_intro":    dict(bpm=104, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.75, oct=76, vol=0.85),
    "w_home":     dict(bpm=92, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.5, oct=77, vol=0.72),
    "w_wonder":   dict(bpm=72, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.4, oct=84, vol=0.72),
    "w_map":      dict(bpm=110, prog=[(62, MAJ), (67, MAJ), (59, MIN), (57, MAJ)], drums=True, mel=0.65, oct=78, vol=0.8),
    "w_sea":      dict(bpm=84, prog=[(55, MAJ), (52, MIN), (60, MAJ), (62, MAJ)], drums=False, mel=0.5, oct=79, vol=0.75),
    "w_funny":    dict(bpm=136, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.85, oct=72, vol=0.85),
    "w_remember": dict(bpm=96, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.45, oct=77, vol=0.68),
    "w_quiz":     dict(bpm=118, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=True, mel=0.35, oct=76, vol=0.6),
    "w_night":    dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(a, 1e-4)) * np.minimum(1.0, (n / SR - t) / max(r, 1e-4))


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def _bell(f, d, decay=5.0):
    t = _t(d)
    x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * decay * (1 + h * 0.3))
            for h, g in ((1, 1.0), (2.76, 0.35), (5.4, 0.15)))
    return x * np.minimum(1, t / 0.002)


def sfx_spin(rng):
    """Old globe spinning on its axle: slowing ratchet clicks over a soft whirr."""
    d = 1.6
    out = np.zeros(int(d * SR))
    tc = 0.0
    gap = 0.035
    while tc < d - 0.05:
        n = int(0.02 * SR)
        tt = np.arange(n) / SR
        click = _band(rng.standard_normal(n), 1500, 6000) * np.exp(-tt * 300)
        i = int(tc * SR)
        out[i:i + n] += click[:len(out) - i] * (1 - tc / d)
        tc += gap
        gap *= 1.07
    t = _t(d)
    whirr = _band(rng.standard_normal(len(t)), 200, 900) * (1 - t / d) * 0.25
    return _norm(out + whirr, 0.5)


def sfx_ding(rng):
    """Bright two-note glockenspiel 'ding-ding' for a new fact."""
    out = np.zeros(int(1.4 * SR))
    for k, (f, st) in enumerate(((1568, 0.0), (2093, 0.12))):
        x = _bell(f, 1.2, 3.5)
        i = int(st * SR)
        out[i:i + len(x)] += x[:len(out) - i] * (0.8 if k == 0 else 1.0)
    return _norm(out, 0.55)


def sfx_tick(rng):
    """Quiz clock tick."""
    t = _t(0.08)
    x = (np.sin(TAU * 2400 * t) + 0.5 * np.sin(TAU * 3700 * t)) * np.exp(-t * 90)
    x += _band(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 300) * 0.4
    return _norm(x, 0.5)


def sfx_chime(rng):
    """Correct answer: a happy rising arpeggio C-E-G-C."""
    out = np.zeros(int(1.8 * SR))
    for k, n in enumerate((72, 76, 79, 84)):
        f = 440 * 2 ** ((n - 69) / 12)
        x = _bell(f, 1.2, 3.0)
        i = int(k * 0.09 * SR)
        out[i:i + len(x)] += x[:len(out) - i]
    return _norm(out, 0.6)


def sfx_sparkle(rng):
    """Magic shimmer: a shower of tiny high bells."""
    d = 1.6
    out = np.zeros(int(d * SR))
    for _ in range(26):
        st = rng.uniform(0, d - 0.5)
        f = rng.uniform(2200, 5200)
        x = _bell(f, 0.5, 9.0) * rng.uniform(0.3, 1.0)
        i = int(st * SR)
        out[i:i + len(x)] += x[:len(out) - i]
    t = _t(d)
    return _norm(out * np.sin(np.pi * t / d) ** 0.5, 0.45)


def sfx_pop(rng):
    """Soft bubbly pop for labels and markers."""
    t = _t(0.16)
    f = 380 + 900 * t / 0.16
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 30)
    return _norm(x, 0.5)


KIT_SFX = {"spin": (sfx_spin, 0.5), "ding": (sfx_ding, 0.55), "tick": (sfx_tick, 0.6),
           "chime": (sfx_chime, 0.6), "sparkle": (sfx_sparkle, 0.5), "pop": (sfx_pop, 0.5)}
