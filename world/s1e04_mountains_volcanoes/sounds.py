"""Episode 4 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # airy and wide, high in the snowy Himalayas
    "w_peaks": dict(bpm=76, prog=[(62, MAJ), (57, MAJ), (59, MIN), (55, MAJ)], drums=False, mel=0.45, oct=81,
                    vol=0.72),
    # sunny, bouncy island tune
    "w_island": dict(bpm=100, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=True, mel=0.6, oct=77,
                     vol=0.76),
    # rumbling, exciting (but not scary) eruption music
    "w_lava": dict(bpm=120, prog=[(50, MIN), (46, MAJ), (48, MAJ), (45, MIN)], drums=True, mel=0.55, oct=74,
                   vol=0.8),
}


def _t(d):
    return np.arange(int(d * SR)) / SR


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def ruffle(rng):
    """A blanket sliding and bunching up: soft papery swish."""
    d = 0.7
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 600, 5000)
    env = np.sin(np.pi * t / d) ** 2 * (0.7 + 0.3 * np.sin(TAU * 9 * t))
    return _norm(x * env, 0.4)


def wind(rng):
    """Cold mountain wind: a long hollow whistle-gust."""
    d = 2.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 200, 1600)
    whistle = np.sin(TAU * np.cumsum(700 + 120 * np.sin(TAU * 0.6 * t)) / SR) * 0.12
    sweep = np.sin(np.pi * t / d) ** 1.5 * (0.7 + 0.3 * np.sin(TAU * 0.8 * t))
    return _norm((x + whistle) * sweep, 0.5)


def chatter(rng):
    """Teeth chattering with cold: quick little clicks."""
    out = np.zeros(int(0.9 * SR))
    for k in range(12):
        n = int(0.02 * SR)
        tt = np.arange(n) / SR
        x = _band(rng.standard_normal(n), 2000, 7000) * np.exp(-tt * 260)
        i = int(k * 0.07 * SR)
        out[i:i + n] += x * (1 - k / 14)
    return _norm(out, 0.4)


def bloop(rng):
    """Something sinking into deep water: a low gulp and bubbles."""
    out = np.zeros(int(0.8 * SR))
    for k in range(3):
        d = 0.14
        t = np.arange(int(d * SR)) / SR
        f0 = rng.uniform(200, 340)
        f = f0 * (1 + 2.0 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int((k * 0.18 + rng.uniform(0, 0.04)) * SR)
        out[i:i + len(x)] += x * (1 - 0.2 * k)
    return _norm(out, 0.5)


def waves(rng):
    """A wave washing over black lava rocks."""
    d = 2.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 200, 6000)
    env = np.minimum(1, t / 0.4) * np.exp(-np.maximum(0, t - 0.4) * 1.5)
    return _norm(x * env, 0.45)


def bubble(rng):
    """Thick bubbling, like a pot of something hot: blorp, blorp."""
    out = np.zeros(int(1.0 * SR))
    for k in range(5):
        d = 0.1
        t = np.arange(int(d * SR)) / SR
        f0 = rng.uniform(90, 160)
        f = f0 * (1 + 1.5 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int((k * 0.18 + rng.uniform(0, 0.05)) * SR)
        out[i:i + len(x)] += x
    return _norm(out, 0.5)


def rumble(rng):
    """Deep ground rumble (the volcano waking up)."""
    d = 2.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 25, 160)
    x += 0.4 * np.sin(TAU * 42 * t) * (0.6 + 0.4 * np.sin(TAU * 7 * t))
    env = np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.6)
    return _norm(x * env, 0.7)


def boom(rng):
    """The eruption: a big soft boom with a hissing tail."""
    d = 2.0
    t = _t(d)
    low = np.sin(TAU * np.cumsum(70 * np.exp(-t * 1.5) + 30) / SR) * np.exp(-t * 2.2)
    noise = _band(rng.standard_normal(len(t)), 60, 900) * np.exp(-t * 1.6)
    hiss = _band(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 1.2) * 0.25
    return _norm(low + 0.8 * noise + hiss, 0.75)


def sizzle(rng):
    """Hot sizzle and steam hiss."""
    d = 1.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 3000, 11000)
    crackle = np.zeros(len(t))
    for _ in range(60):
        i = int(rng.uniform(0, d - 0.01) * SR)
        crackle[i:i + 60] += rng.uniform(-1, 1)
    env = np.minimum(1, t / 0.08) * np.exp(-t * 1.4)
    return _norm((x + 0.6 * crackle) * env, 0.45)


def zip(rng):
    """A telescope fishing rod shooting out: a fast rising zip."""
    d = 0.45
    t = _t(d)
    f = 300 + 2400 * (t / d) ** 1.5
    x = np.sign(np.sin(TAU * np.cumsum(f) / SR)) * 0.3 + _band(rng.standard_normal(len(t)), 1500, 6000) * 0.5
    env = np.sin(np.pi * t / d)
    return _norm(x * env, 0.35)


def poof(rng):
    """A puff of smoke."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 2500)
    env = np.minimum(1, t / 0.02) * np.exp(-t * 6)
    return _norm(x * env, 0.5)


def boing(rng):
    """Comic ouch-boing: a wobbly falling spring."""
    d = 0.7
    t = _t(d)
    f = 560 * np.exp(-t * 1.6) * (1 + 0.12 * np.sin(TAU * 14 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return _norm(x, 0.5)


def crunch(rng):
    """A crunchy bite of very burnt fish."""
    out = np.zeros(int(0.5 * SR))
    for k in range(6):
        n = int(0.03 * SR)
        tt = np.arange(n) / SR
        x = _band(rng.standard_normal(n), 800, 6000) * np.exp(-tt * 120)
        i = int((k * 0.06 + rng.uniform(0, 0.02)) * SR)
        out[i:i + n] += x * rng.uniform(0.5, 1.0)
    return _norm(out, 0.5)


EXTRA_SFX = {"ruffle": (ruffle, 0.45), "wind": (wind, 0.4), "chatter": (chatter, 0.4), "bloop": (bloop, 0.5),
             "waves": (waves, 0.4), "bubble": (bubble, 0.5), "rumble": (rumble, 0.65), "boom": (boom, 0.6),
             "sizzle": (sizzle, 0.4), "zip": (zip, 0.4), "poof": (poof, 0.45), "boing": (boing, 0.5),
             "crunch": (crunch, 0.5)}
