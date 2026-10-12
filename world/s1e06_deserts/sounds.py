"""Episode 6 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # a warm, swaying desert tune (minor-ish, steady camel-walk tempo)
    "w_desert": dict(bpm=88, prog=[(57, MIN), (55, MAJ), (53, MAJ), (52, MAJ)], drums=True, mel=0.55, oct=77,
                     vol=0.74),
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


def wind(rng):
    """A dry desert gust with a sandy hiss."""
    d = 2.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 1200)
    hiss = _band(rng.standard_normal(len(t)), 3000, 9000) * 0.25
    sweep = np.sin(np.pi * t / d) ** 1.5 * (0.7 + 0.3 * np.sin(TAU * 0.9 * t))
    return _norm((x + hiss) * sweep, 0.5)


def sandpuff(rng):
    """A soft 'pff' of sand: a short noisy thump."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 120, 2500) * np.exp(-t * 7)
    x += np.sin(TAU * 90 * t) * np.exp(-t * 14) * 0.6
    return _norm(x, 0.5)


def slurp(rng):
    """Comic empty straw: a gurgly rising slurp that ends in air."""
    d = 0.9
    t = _t(d)
    f = 300 + 500 * t / d + 60 * np.sin(TAU * 18 * t)
    x = np.sin(TAU * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sign(np.sin(TAU * 11 * t))) * 0.6
    x += _band(rng.standard_normal(len(t)), 800, 5000) * 0.5
    env = np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)
    return _norm(x * env, 0.45)


def boing(rng):
    """Comic boing: a wobbly falling spring."""
    d = 0.7
    t = _t(d)
    f = 520 * np.exp(-t * 1.6) * (1 + 0.12 * np.sin(TAU * 14 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return _norm(x, 0.5)


def drip(rng):
    """One lonely raindrop: a little plink."""
    d = 0.4
    t = _t(d)
    f = 1200 + 900 * np.exp(-t * 30)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 18)
    return _norm(x, 0.45)


def scritch(rng):
    """A beetle scratching under the sand: tiny crackles."""
    d = 1.0
    out = np.zeros(int(d * SR))
    for _ in range(26):
        i = int(rng.uniform(0, d - 0.02) * SR)
        n = int(0.008 * SR)
        out[i:i + n] += _band(rng.standard_normal(n), 2000, 8000) * rng.uniform(0.3, 1.0)
    return _norm(out, 0.4)


def chatter(rng):
    """Teeth chattering in the cold: fast little clicks."""
    d = 0.9
    out = np.zeros(int(d * SR))
    for k in range(14):
        i = int(k * 0.06 * SR)
        n = int(0.012 * SR)
        tt = np.arange(n) / SR
        out[i:i + n] += np.sin(TAU * 2400 * tt) * np.exp(-tt * 400) + \
            _band(rng.standard_normal(n), 2000, 7000) * 0.4
    return _norm(out, 0.4)


EXTRA_SFX = {"wind": (wind, 0.45), "sandpuff": (sandpuff, 0.5), "slurp": (slurp, 0.5), "boing": (boing, 0.5),
             "drip": (drip, 0.5), "scritch": (scritch, 0.45), "chatter": (chatter, 0.45)}
