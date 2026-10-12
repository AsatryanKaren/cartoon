"""Episode 2 sound effects (48 kHz mono float). EXTRA_SFX maps names to (function, gain)."""
import numpy as np

SR = 48000
TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _norm(x, peak=0.5):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def flap(rng):
    """Big wings: three soft whumps of air."""
    out = np.zeros(int(0.9 * SR))
    for k in range(3):
        d = 0.16
        t = _t(d)
        x = _band(rng.standard_normal(len(t)), 80, 900) * np.sin(np.pi * t / d) ** 2
        i = int(k * 0.26 * SR)
        out[i:i + len(x)] += x * (1 - 0.2 * k)
    return _norm(out, 0.5)


def caw(rng):
    """A friendly sea-bird call: two nasal, falling 'kyaa's."""
    out = np.zeros(int(0.8 * SR))
    for k, st in enumerate((0.0, 0.3)):
        d = 0.24
        t = _t(d)
        f = 900 - 300 * t / d + 40 * np.sin(TAU * 30 * t)
        ph = TAU * np.cumsum(f) / SR
        x = sum(np.sin(h * ph) / h ** 0.7 for h in range(1, 8))
        x *= np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
        i = int(st * SR)
        out[i:i + len(x)] += x * (1 - 0.25 * k)
    return _norm(_band(out, 300, 6000), 0.45)


def roar(rng):
    """A small, friendly cartoon lion roar."""
    d = 1.0
    t = _t(d)
    f = 110 + 50 * np.sin(np.pi * np.minimum(1, t / 0.6))
    ph = TAU * np.cumsum(f) / SR
    buzz = sum(np.sin(h * ph) / h for h in range(1, 12))
    grit = _band(rng.standard_normal(len(t)), 150, 1500) * 0.6
    x = (buzz + grit) * np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.5) * 5)
    return _norm(x, 0.5)


def boing(rng):
    d = 0.45
    t = _t(d)
    f = 180 + 260 * np.exp(-t * 9) + 30 * np.sin(TAU * 14 * t) * np.exp(-t * 5)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _norm(x, 0.5)


def wind(rng):
    """Icy polar wind."""
    d = 2.2
    n = int(d * SR)
    t = _t(d)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks = 20
    step = n // chunks
    for c in range(chunks):
        u = c / chunks
        lo = 400 + 700 * np.sin(TAU * u * 1.3) ** 2
        seg = _band(noise[c * step:(c + 2) * step], lo, lo * 1.6)
        w = np.hanning(len(seg))
        out[c * step:c * step + len(seg)] += (seg * w)[:n - c * step]
    return _norm(out * np.sin(np.pi * t / d), 0.4)


def poof(rng):
    """Landing in deep snow."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 60, 2500) * np.exp(-t * 9) * np.minimum(1, t / 0.005)
    return _norm(x, 0.55)


def crackle(rng):
    """Frost creeping: tiny crystal ticks with a rising shimmer."""
    d = 1.2
    out = np.zeros(int(d * SR))
    for _ in range(40):
        st = rng.uniform(0, d - 0.05) ** 0.8
        m = int(0.03 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(2500, 6000)
        x = np.sin(TAU * f * tt) * np.exp(-tt * 160)
        i = int(st * SR)
        out[i:i + m] += x * rng.uniform(0.3, 1.0)
    t = _t(d)
    out += 0.25 * np.sin(TAU * (1800 + 900 * t) * t) * np.sin(np.pi * t / d) ** 2
    return _norm(out, 0.4)


def brr(rng):
    """Chattering teeth."""
    d = 0.9
    t = _t(d)
    clicks = np.zeros(len(t))
    for k in range(int(d * 22)):
        i = int(k / 22 * SR)
        m = int(0.012 * SR)
        clicks[i:i + m] += _band(rng.standard_normal(m), 1500, 7000) * np.exp(-np.arange(m) / SR * 300)
    return _norm(clicks * np.sin(np.pi * t / d) ** 0.5, 0.45)


def squeak(rng):
    """Little penguin squawk."""
    d = 0.22
    t = _t(d)
    f = rng.uniform(700, 900) * (1 + 0.5 * np.sin(np.pi * t / d))
    ph = TAU * np.cumsum(f) / SR
    x = sum(np.sin(h * ph) / h for h in range(1, 6)) * np.sin(np.pi * t / d)
    return _norm(x, 0.4)


EXTRA_SFX = {"flap": (flap, 0.5), "caw": (caw, 0.45), "roar": (roar, 0.45), "boing": (boing, 0.45),
             "wind": (wind, 0.4), "poof": (poof, 0.55), "crackle": (crackle, 0.4), "brr": (brr, 0.45),
             "squeak": (squeak, 0.4)}
