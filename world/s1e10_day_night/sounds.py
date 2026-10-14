"""Episode 10 sound effects (48 kHz mono float). EXTRA_SFX maps names to (function, gain)."""
import numpy as np

from world.s1e01_our_planet.sounds import bloop

SR = 48000
TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def _norm(x, peak=0.5):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def hoot(rng):
    """Owl call: hoo ... hoo-hoo, soft and breathy."""
    out = np.zeros(int(1.5 * SR))
    for start, d, f0 in ((0.0, 0.42, 410), (0.62, 0.2, 395), (0.86, 0.42, 380)):
        t = _t(d)
        f = f0 * (1 + 0.04 * np.sin(np.pi * t / d)) - 25 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) + 0.25 * np.sin(2 * TAU * np.cumsum(f) / SR)
        x += 0.08 * rng.standard_normal(len(t))
        x *= np.sin(np.pi * t / d) ** 1.5
        i = int(start * SR)
        out[i:i + len(x)] += x
    return _norm(out, 0.45)


def click(rng):
    """Torch switch click."""
    n = int(0.08 * SR)
    t = _t(0.08)
    x = rng.standard_normal(n) * np.exp(-t * 160) + 0.6 * np.sin(TAU * 2400 * t) * np.exp(-t * 90)
    return _norm(x, 0.5)


def boing(rng):
    """Cartoon spring 'boing' (Whiskers flung off the spinning Earth)."""
    d = 0.7
    t = _t(d)
    f = 180 + 260 * np.exp(-t * 4) * (1 + 0.35 * np.sin(TAU * 11 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    return _norm(x * _env(len(t), 0.005, 0.1), 0.5)


EXTRA_SFX = {"hoot": (hoot, 0.55), "click": (click, 0.5), "boing": (boing, 0.55), "bloop": (bloop, 0.5)}
