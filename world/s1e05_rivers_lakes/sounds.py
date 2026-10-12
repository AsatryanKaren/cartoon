"""Episode 5 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

from world.s1e03_five_oceans import sounds as S3

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # bouncy and flowing, for sliding down the river
    "w_river": dict(bpm=112, prog=[(60, MAJ), (57, MIN), (62, MIN), (55, MAJ)], drums=True, mel=0.6, oct=79,
                    vol=0.78),
    # calm and glassy, for the lake
    "w_lake": dict(bpm=70, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.35, oct=81,
                   vol=0.68),
}


def _t(d):
    return np.arange(int(d * SR)) / SR


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def _drop(rng, f0=None, d=0.09):
    """One water drop: a short rising sine 'plip'."""
    t = _t(d)
    f0 = f0 or rng.uniform(700, 1100)
    f = f0 * (1 + 1.6 * t / d)
    return np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 45)


def plip(rng):
    """A single raindrop landing."""
    x = np.zeros(int(0.3 * SR))
    d = _drop(rng, 900)
    x[:len(d)] += d
    return _norm(x, 0.5)


def rain(rng):
    """Soft rain on a window: a hiss with little drop ticks (3.5 s)."""
    dur = 3.5
    t = _t(dur)
    hiss = S3._band(rng.standard_normal(len(t)), 1500, 9000) * 0.25
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.8)
    x = hiss * env
    for _ in range(40):
        i = int(rng.uniform(0, dur - 0.1) * SR)
        d = _drop(rng, rng.uniform(1200, 2600), 0.05) * rng.uniform(0.15, 0.4)
        x[i:i + len(d)] += d * env[i]
    return _norm(x, 0.45)


def babble(rng):
    """A babbling mountain stream (2.5 s)."""
    dur = 2.5
    t = _t(dur)
    x = S3._band(rng.standard_normal(len(t)), 300, 2500) * (0.6 + 0.4 * np.sin(TAU * 3.1 * t) ** 2) * 0.3
    for _ in range(26):
        i = int(rng.uniform(0, dur - 0.1) * SR)
        d = _drop(rng, rng.uniform(400, 900), 0.07) * rng.uniform(0.3, 0.7)
        x[i:i + len(d)] += d
    env = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.6)
    return _norm(x * env, 0.5)


def paddle(rng):
    """Frantic paddling: six quick little splashes."""
    x = np.zeros(int(1.4 * SR))
    for k in range(6):
        n = int(0.12 * SR)
        tt = np.arange(n) / SR
        s = S3._band(rng.standard_normal(n), 500, 5000) * np.exp(-tt * 35)
        i = int(k * 0.21 * SR)
        x[i:i + n] += s * (0.7 + 0.3 * rng.random())
    return _norm(x, 0.5)


def wheee(rng):
    """A slide: a long falling-then-rising whistle with splashy noise."""
    d = 1.0
    t = _t(d)
    f = 700 + 500 * np.sin(np.pi * t / d)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.4
    x += S3._band(rng.standard_normal(len(t)), 800, 5000) * np.sin(np.pi * t / d) ** 2 * 0.4
    return _norm(x, 0.45)


def quack(rng):
    """A friendly duck quack."""
    d = 0.22
    t = _t(d)
    f = 420 * (1 - 0.3 * t / d)
    ph = TAU * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 9)) * np.minimum(1, t / 0.02) * np.exp(-t * 9)
    x = S3._band(x, 500, 3500)
    return _norm(x, 0.5)


def rise(rng):
    """Magic rising up: a soft upward shimmer."""
    d = 1.6
    t = _t(d)
    x = np.zeros(len(t))
    for k, f0 in enumerate((660, 880, 990, 1320)):
        f = f0 * (1 + 0.5 * t / d)
        x += np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * (0.6 ** k)
    return _norm(x, 0.35)


EXTRA_SFX = {"plip": (plip, 0.55), "rain": (rain, 0.45), "babble": (babble, 0.45), "paddle": (paddle, 0.55),
             "wheee": (wheee, 0.45), "quack": (quack, 0.45), "rise": (rise, 0.4),
             "lap": S3.EXTRA_SFX["lap"], "boing": S3.EXTRA_SFX["boing"], "waves": S3.EXTRA_SFX["waves"]}
