"""Episode 8 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # sparkly, slow and icy for the poles (high bell-like melody, no drums)
    "w_ice": dict(bpm=80, prog=[(64, MIN), (60, MAJ), (67, MAJ), (62, MAJ)], drums=False, mel=0.45, oct=86,
                  vol=0.7),
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
    """Icy polar wind: a howling band of noise that swells and fades."""
    d = 2.4
    n = int(d * SR)
    t = _t(d)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    step = n // 16
    for k in range(16):
        u = k / 16
        lo = 300 + 500 * np.sin(np.pi * u) ** 2
        seg = _band(noise[k * step:(k + 1) * step + step // 2], lo, lo * 2.2)
        win = np.hanning(len(seg))
        out[k * step:k * step + len(seg)] += seg[:n - k * step] * win[:n - k * step]
    hum = np.sin(TAU * np.cumsum(520 + 160 * np.sin(TAU * 0.4 * t)) / SR) * 0.15
    env = np.sin(np.pi * t / d) ** 1.2
    return _norm((out + hum) * env, 0.5)


def crunch(rng):
    """Landing on snow: a short crunchy thump."""
    d = 0.45
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 300, 5000) * (rng.random(len(t)) > 0.6)
    thump = np.sin(TAU * 80 * t) * np.exp(-t * 18)
    return _norm(x * np.exp(-t * 9) + thump * 1.5, 0.55)


def squeak(rng):
    """A happy little penguin squawk."""
    d = 0.32
    t = _t(d)
    f0 = rng.uniform(700, 900)
    f = f0 + 500 * np.sin(np.pi * t / d) + 40 * np.sin(TAU * 35 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum(np.sin(h * ph) / h for h in range(1, 6))
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.06)
    return _norm(x * env, 0.45)


def swish(rng):
    """Belly-sliding on ice."""
    d = 0.9
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1500, 7000)
    env = np.sin(np.pi * t / d) ** 2
    return _norm(x * env, 0.4)


def boing(rng):
    d = 0.45
    t = _t(d)
    f = 180 + 260 * np.exp(-t * 9) + 30 * np.sin(TAU * 14 * t) * np.exp(-t * 5)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _norm(x, 0.5)


def sizzle(rng):
    """A frying-pan sizzle (the poor hot penguin)."""
    d = 1.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 3000, 9000)
    crackle = (rng.random(len(t)) > 0.995) * rng.standard_normal(len(t)) * 4
    env = np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.3)
    return _norm((x + crackle) * env * (0.7 + 0.3 * np.sin(TAU * 7 * t)), 0.35)


def crack(rng):
    """Ice creaking and cracking."""
    d = 0.8
    t = _t(d)
    out = np.zeros(len(t))
    for k in range(5):
        i = int(rng.uniform(0, 0.5) * SR)
        n = int(0.06 * SR)
        tt = np.arange(n) / SR
        x = _band(rng.standard_normal(n), 200, 4000) * np.exp(-tt * 60)
        out[i:i + n] += x * rng.uniform(0.5, 1)
    creak = np.sin(TAU * np.cumsum(140 + 60 * np.sin(TAU * 3 * t)) / SR) * np.exp(-t * 4) * 0.4
    return _norm(out + creak, 0.5)


def scratch(rng):
    """Claws scratching a post."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 800, 6000)
    env = (0.5 + 0.5 * np.sign(np.sin(TAU * 9 * t))) * np.sin(np.pi * t / d)
    return _norm(x * env, 0.4)


def bloop(rng):
    """Bubbles under the ice."""
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        d = 0.12
        t = _t(d)
        f0 = rng.uniform(260, 420)
        f = f0 * (1 + 2.2 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int((k * 0.16 + rng.uniform(0, 0.04)) * SR)
        out[i:i + len(x)] += x * (1 - 0.2 * k)
    return _norm(out, 0.5)


EXTRA_SFX = {"wind": (wind, 0.5), "crunch": (crunch, 0.55), "squeak": (squeak, 0.5), "swish": (swish, 0.4),
             "boing": (boing, 0.5), "sizzle": (sizzle, 0.4), "crack": (crack, 0.55), "scratch": (scratch, 0.45),
             "bloop": (bloop, 0.5)}
