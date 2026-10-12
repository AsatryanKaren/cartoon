"""Mountain sound effects, synthesised with numpy (48 kHz mono float).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
names to (function, gain) for the film's script.
"""
import numpy as np

SR = 48000
TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r, decay=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.minimum(1.0, (n / SR - t) / max(r, 1e-4))
    if decay:
        e *= np.exp(-t * decay)
    return e


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _place(buf, start, x, gain=1.0):
    i = int(start * SR)
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += gain * x[:j - i]


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def wind(rng):
    """Howling gust: band noise with a slowly gliding resonance."""
    d = 4.0
    n = int(d * SR)
    t = _t(d)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks, step = 40, n // 40
    for c in range(chunks):
        u = c / chunks
        f = 350 + 450 * np.sin(np.pi * u) ** 2 + 120 * np.sin(u * 17)
        seg = _band(noise[c * step:c * step + 2 * step], f * 0.8, f * 1.25)
        _place(out, c * step / SR, seg * np.hanning(len(seg)))
    low = _band(rng.standard_normal(n), 60, 400) * 0.6
    x = (out + low) * np.sin(np.pi * t / d) ** 1.5
    return _norm(x, 0.55)


def jingle(rng):
    """Luna's little collar bell: two quick bright rings."""
    out = np.zeros(int(0.9 * SR))
    for k, start in enumerate((0.0, 0.12)):
        t = _t(0.7)
        f0 = 2650 + 90 * k
        x = sum(g * np.sin(TAU * f0 * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 7), (1.51, 0.5, 10), (2.42, 0.3, 14), (3.9, 0.15, 20)))
        x *= 1 + 0.25 * np.sin(TAU * 18 * t)
        _place(out, start, x * np.minimum(1, t / 0.002), 0.7 if k else 1.0)
    return _norm(out, 0.5)


def crunch(rng):
    """One footstep in snow: a short burst of crackly grains."""
    d = 0.28
    n = int(d * SR)
    t = _t(d)
    grains = (rng.random(n) < 0.08) * rng.standard_normal(n)
    x = _band(grains + 0.3 * rng.standard_normal(n), 900, 7000) * np.sin(np.pi * t / d) ** 0.7
    return _norm(x, 0.5)


def hum(rng):
    """Cable car: electric hum with wheels rolling over the cable pylon."""
    d = 3.0
    t = _t(d)
    x = 0.5 * np.sin(TAU * 100 * t) + 0.25 * np.sin(TAU * 200 * t) + 0.12 * np.sin(TAU * 300 * t)
    x *= 0.7 + 0.3 * np.sin(TAU * 0.7 * t)
    x += 0.4 * _band(rng.standard_normal(len(t)), 150, 900)
    for k in range(3):
        tt = 0.5 + k * 0.9
        click = _band(rng.standard_normal(int(0.08 * SR)), 300, 3000) * _env(int(0.08 * SR), 0.002, 0.05, 30)
        _place(x, tt, click, 1.2)
    return _norm(x * _env(len(t), 0.4, 0.6), 0.45)


def clunk(rng):
    """Heavy metal latch of the cable car doors."""
    d = 0.6
    t = _t(d)
    x = (np.sin(TAU * 90 * t) + 0.6 * np.sin(TAU * 143 * t) + 0.3 * np.sin(TAU * 410 * t)) * np.exp(-t * 9)
    x += _band(rng.standard_normal(len(t)), 200, 2500) * np.exp(-t * 40) * 0.8
    return _norm(x, 0.6)


def train(rng):
    """A train chugging along: rhythmic wheel clacks over the rails."""
    d = 5.0
    n = int(d * SR)
    out = np.zeros(n)
    beat = 0.36
    k = 0
    while k * beat < d - 0.3:
        tt = k * beat + (0.09 if k % 2 else 0)
        m = int(0.07 * SR)
        click = _band(rng.standard_normal(m), 200, 3500) * _env(m, 0.002, 0.05, 40)
        _place(out, tt, click, 1.0 if k % 4 == 0 else 0.6)
        k += 1
    out += 0.15 * _band(rng.standard_normal(n), 60, 300)
    return _norm(out * _env(n, 0.5, 1.0), 0.45)


def whistle(rng):
    """Train whistle: two-tone chord with breath."""
    d = 1.2
    t = _t(d)
    x = sum(np.sin(TAU * f * t) + 0.3 * np.sin(TAU * 2 * f * t) for f in (587, 740, 880))
    x += 0.5 * _band(rng.standard_normal(len(t)), 1500, 5000)
    return _norm(x * _env(len(t), 0.06, 0.3), 0.45)


def cowbell(rng):
    """Alpine cowbell clonk, slightly detuned each time."""
    d = 1.2
    t = _t(d)
    f = rng.uniform(520, 600)
    x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * dk)
            for h, g, dk in ((1, 1.0, 4), (1.48, 0.7, 5), (2.03, 0.4, 7), (2.94, 0.25, 9)))
    x += _band(rng.standard_normal(len(t)), 800, 4000) * np.exp(-t * 60) * 0.5
    out = np.zeros(int(1.6 * SR))
    _place(out, 0, x)
    _place(out, 0.28, x, 0.6)
    return _norm(out, 0.5)


def marmot(rng):
    """Marmot alarm whistle: a sharp high chirp, twice."""
    out = np.zeros(int(0.8 * SR))
    for start in (0.0, 0.32):
        d = 0.18
        t = _t(d)
        f = 2900 + 600 * np.sin(np.pi * t / d) - 800 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.05)
        _place(out, start, x)
    return _norm(out, 0.45)


def bark(rng):
    """Big deep friendly woof."""
    d = 0.42
    t = _t(d)
    f = 150 + 120 * np.exp(-t * 12) - 30 * t
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 9))
    x += 0.35 * _band(rng.standard_normal(len(t)), 300, 2500)
    x *= _env(len(t), 0.01, 0.15, 3)
    return _norm(_band(x, 80, 3000), 0.6)


def crackle(rng):
    """Fireplace: soft roar with random pops."""
    d = 3.5
    n = int(d * SR)
    x = 0.25 * _band(rng.standard_normal(n), 100, 900)
    for _ in range(45):
        m = int(rng.uniform(0.004, 0.02) * SR)
        pop = rng.standard_normal(m) * np.exp(-np.arange(m) / m * 5)
        _place(x, rng.uniform(0, d - 0.05), pop, rng.uniform(0.3, 1.0))
    return _norm(x * _env(n, 0.3, 0.6), 0.4)


def poof(rng):
    """Soft thump into deep snow."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 80, 1800) * np.exp(-t * 9) * np.minimum(1, t / 0.005)
    x += np.sin(TAU * (70 + 40 * np.exp(-t * 20)) * t) * np.exp(-t * 12) * 0.8
    return _norm(x, 0.6)


def swish(rng):
    """Sled runners hissing over snow."""
    d = 1.0
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 2500, 9000) * np.sin(np.pi * t / d) ** 2
    return _norm(x, 0.4)


EXTRA_SFX = {
    "wind": (wind, 0.5), "jingle": (jingle, 0.45), "crunch": (crunch, 0.35), "hum": (hum, 0.35),
    "clunk": (clunk, 0.55), "train": (train, 0.5), "whistle": (whistle, 0.4), "cowbell": (cowbell, 0.4),
    "marmot": (marmot, 0.45), "bark": (bark, 0.7), "crackle": (crackle, 0.45), "poof": (poof, 0.7),
    "swish": (swish, 0.35),
}
