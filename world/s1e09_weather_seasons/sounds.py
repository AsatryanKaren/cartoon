"""Episode 9 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

from world.s1e03_five_oceans import sounds as S3
from world.s1e05_rivers_lakes import sounds as S5

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # a bouncy country tune for the farm on the hill
    "w_farm": dict(bpm=116, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.6, oct=79,
                   vol=0.76),
    # a gentle turning waltz-like loop for the tree through the year
    "w_seasons": dict(bpm=84, prog=[(65, MAJ), (69, MIN), (70, MAJ), (72, MAJ)], drums=False, mel=0.5, oct=81,
                      vol=0.7),
    # soft and grey, for the rain
    "w_rainy": dict(bpm=76, prog=[(57, MIN), (65, MAJ), (60, MAJ), (64, MIN)], drums=False, mel=0.35, oct=79,
                    vol=0.66),
}


def _t(d):
    return np.arange(int(d * SR)) / SR


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


_band = S3._band


def wind(rng):
    """A long autumn gust: band noise with a gliding resonance (3.2 s)."""
    d = 3.2
    n = int(d * SR)
    t = _t(d)
    noise = rng.standard_normal(n + SR)
    out = np.zeros(n)
    chunks = 32
    step = n // chunks
    for c in range(chunks):
        u = c / chunks
        f = 320 + 420 * np.sin(np.pi * u) ** 2 + 80 * np.sin(u * 11)
        seg = _band(noise[c * step:c * step + 2 * step], f * 0.8, f * 1.3)
        w = np.hanning(len(seg))
        m = min(len(seg), n - c * step)
        out[c * step:c * step + m] += (seg * w)[:m]
    low = _band(rng.standard_normal(n), 60, 300) * 0.4
    return _norm((out + low) * np.sin(np.pi * t / d) ** 1.4, 0.5)


def rustle(rng):
    """Dry leaves skittering (1.2 s)."""
    d = 1.2
    out = np.zeros(int(d * SR))
    for _ in range(40):
        m = int(rng.uniform(0.01, 0.04) * SR)
        tm = np.arange(m) / SR
        x = _band(rng.standard_normal(m), 1800, 9000) * np.exp(-tm * 90)
        i = int(rng.uniform(0, d - 0.05) * SR)
        out[i:i + m] += x * rng.uniform(0.2, 1.0)
    t = _t(d)
    return _norm(out * np.sin(np.pi * t / d) ** 0.6, 0.4)


def creak(rng):
    """A metal weather vane squeaking as it turns."""
    d = 1.1
    t = _t(d)
    f = 900 + 260 * np.sin(TAU * 1.3 * t) + 120 * np.sin(TAU * 4.1 * t)
    ph = TAU * np.cumsum(f) / SR
    pulses = 0.5 + 0.5 * np.sign(np.sin(TAU * 22 * t))
    x = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * pulses
    x = _band(x, 400, 5000) * np.sin(np.pi * t / d) ** 1.2
    return _norm(x, 0.3)


def crow(rng):
    """Cock-a-doodle-doo: four bright syllables, the last one long."""
    sylls = [(0.0, 0.11, 620, 640), (0.14, 0.09, 700, 720), (0.26, 0.14, 820, 860), (0.44, 0.55, 900, 640)]
    out = np.zeros(int(1.1 * SR))
    for t0, d, f0, f1 in sylls:
        t = _t(d)
        f = f0 + (f1 - f0) * (t / d) ** 1.5 + 18 * np.sin(TAU * 7 * t)
        ph = TAU * np.cumsum(f) / SR
        x = sum(np.sin(k * ph) * (0.8 ** k) for k in range(1, 9))
        x *= np.minimum(1, t / 0.015) * np.minimum(1, (d - t) / 0.04)
        x += _band(rng.standard_normal(len(t)), 1500, 5000) * 0.15 * np.sin(np.pi * t / d)
        i = int(t0 * SR)
        out[i:i + len(x)] += x
    return _norm(_band(out, 300, 6000), 0.5)


def fanfare(rng):
    """A short, grand ta-da for a vain rooster."""
    notes = [(0.0, 0.12, 67), (0.13, 0.12, 72), (0.26, 0.5, 76)]
    out = np.zeros(int(0.9 * SR))
    for t0, d, m in notes:
        t = _t(d)
        f = 440 * 2 ** ((m - 69) / 12)
        x = sum(np.sin(TAU * f * k * t) * (0.7 ** k) for k in range(1, 7))
        x *= np.minimum(1, t / 0.01) * np.exp(-t * 2.5) * np.minimum(1, (d - t) / 0.03)
        i = int(t0 * SR)
        out[i:i + len(x)] += x
    return _norm(out, 0.4)


def scamper(rng):
    """Tiny squirrel feet scampering over leaves (1.0 s)."""
    out = np.zeros(int(1.0 * SR))
    for k in range(14):
        m = int(0.03 * SR)
        tm = np.arange(m) / SR
        x = _band(rng.standard_normal(m), 1500, 7000) * np.exp(-tm * 120)
        i = int((k * 0.065 + rng.uniform(0, 0.015)) * SR)
        out[i:i + m] += x * (0.6 + 0.4 * rng.random())
    return _norm(out, 0.4)


def chirp(rng):
    """Spring birdsong: two quick chirps."""
    out = np.zeros(int(0.8 * SR))
    for t0 in (0.0, 0.22, 0.42):
        d = 0.12
        t = _t(d)
        f = 2800 + 1600 * np.sin(np.pi * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
        i = int(t0 * SR)
        out[i:i + len(x)] += x
    return _norm(out, 0.35)


def zap(rng):
    """Far-away lightning: a soft crackle (not loud)."""
    d = 0.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 14)
    return _norm(x, 0.3)


def thunder(rng):
    """Gentle, far-away thunder: a low rolling rumble (2.6 s)."""
    d = 2.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 30, 220)
    env = np.minimum(1, t / 0.35) * np.exp(-t * 1.1) * (0.7 + 0.3 * np.sin(TAU * 1.7 * t + 1) ** 2)
    return _norm(x * env, 0.6)


EXTRA_SFX = {"wind": (wind, 0.35), "rustle": (rustle, 0.4), "creak": (creak, 0.3), "crow": (crow, 0.45),
             "fanfare": (fanfare, 0.4), "scamper": (scamper, 0.45), "chirp": (chirp, 0.35), "zap": (zap, 0.3),
             "thunder": (thunder, 0.55), "rain": S5.EXTRA_SFX["rain"], "plip": S5.EXTRA_SFX["plip"],
             "boing": S5.EXTRA_SFX["boing"]}
