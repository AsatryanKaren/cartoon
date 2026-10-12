"""Episode 7 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # bouncy, warm marimba-like jungle groove
    "w_jungle": dict(bpm=100, prog=[(57, MIN), (62, MIN), (55, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=79,
                     vol=0.74),
    # very slow and sleepy, for Mossy the sloth
    "w_slow": dict(bpm=56, prog=[(60, MAJ), (57, MIN), (53, MAJ), (55, MAJ)], drums=False, mel=0.25, oct=72,
                   vol=0.66),
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


def _chirp(f0, f1, d, harm=(1.0, 0.3)):
    t = _t(d)
    f = f0 + (f1 - f0) * t / d
    ph = TAU * np.cumsum(f) / SR
    x = sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harm))
    return x * np.sin(np.pi * t / d) ** 1.2


def rain(rng):
    """A warm tropical shower: soft hiss with lots of little drops, fading in and out."""
    d = 3.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 600, 7000) * 0.5
    for _ in range(260):
        i = int(rng.uniform(0, d - 0.02) * SR)
        n = int(0.006 * SR)
        x[i:i + n] += rng.uniform(0.5, 1.5) * np.exp(-np.arange(n) / (0.0015 * SR)) * rng.choice((-1, 1))
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return _norm(x * env, 0.45)


def jungle(rng):
    """Jungle ambience: bird whistles, a far-away hoot, insects humming."""
    d = 4.0
    out = _band(rng.standard_normal(int(d * SR)), 3500, 6000) * 0.05
    out *= 0.6 + 0.4 * np.sin(TAU * 7 * _t(d))
    for _ in range(9):
        s = rng.uniform(0, d - 0.4)
        f0 = rng.uniform(1800, 3200)
        x = _chirp(f0, f0 * rng.uniform(0.7, 1.4), rng.uniform(0.08, 0.2))
        i = int(s * SR)
        out[i:i + len(x)] += x * rng.uniform(0.2, 0.45)
    for s in (0.8, 1.3):
        x = _chirp(420, 380, 0.35, (1.0, 0.2))
        i = int(s * SR)
        out[i:i + len(x)] += x * 0.4
    env = np.minimum(1, _t(d) / 0.3) * np.minimum(1, (d - _t(d)) / 0.6)
    return _norm(out * env, 0.4)


def thump(rng):
    """A soft landing on leaves."""
    d = 0.5
    t = _t(d)
    x = np.sin(TAU * (90 - 50 * t) * t) * np.exp(-t * 12)
    x += _band(rng.standard_normal(len(t)), 300, 3000) * np.exp(-t * 18) * 0.5
    return _norm(x, 0.7)


def drip(rng):
    """A water drop: a short rising plink."""
    return _norm(_chirp(700, 1500, 0.09, (1.0,)), 0.5)


def squawk(rng):
    """Toucan call: two raspy croaks."""
    d = 0.6
    out = np.zeros(int(d * SR))
    for s in (0.0, 0.25):
        n = int(0.18 * SR)
        t = np.arange(n) / SR
        f = 520 + 200 * np.sin(np.pi * t / 0.18)
        ph = TAU * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.4
        x = x * (0.6 + 0.4 * np.sin(TAU * 60 * t)) * np.sin(np.pi * t / 0.18)
        i = int(s * SR)
        out[i:i + n] += x
    return _norm(_band(out, 300, 5000), 0.5)


def flap(rng):
    """Wing flaps."""
    d = 0.7
    out = np.zeros(int(d * SR))
    for k in range(5):
        n = int(0.08 * SR)
        x = _band(rng.standard_normal(n), 200, 2000) * np.sin(np.pi * np.arange(n) / n) ** 2
        i = int(k * 0.13 * SR)
        out[i:i + n] += x
    return _norm(out, 0.5)


def snore(rng):
    """A big cat's sleepy rumbling snore."""
    d = 1.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 60, 400) * (0.5 + 0.5 * np.sin(TAU * 28 * t))
    env = np.sin(np.pi * np.minimum(1, t / 1.2)) ** 2
    return _norm(x * env, 0.5)


def growl(rng):
    """A big yawn with a little growl at the end."""
    d = 1.2
    t = _t(d)
    f = 180 - 60 * t
    ph = TAU * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.5 * np.sin(2 * ph)) * (0.6 + 0.4 * np.sin(TAU * 32 * t))
    x += _band(rng.standard_normal(len(t)), 200, 1500) * 0.4
    return _norm(x * np.sin(np.pi * t / d), 0.55)


def hoot(rng):
    """A howler-monkey-ish 'ooh ooh' from far away."""
    d = 0.9
    out = np.zeros(int(d * SR))
    for s in (0.0, 0.32):
        x = _chirp(300, 420, 0.28, (1.0, 0.5, 0.2))
        i = int(s * SR)
        out[i:i + len(x)] += x
    return _norm(out, 0.45)


def creak(rng):
    """A bending branch creaks."""
    d = 0.6
    t = _t(d)
    f = 140 + 60 * np.sin(TAU * 1.2 * t)
    pulses = (np.sin(TAU * np.cumsum(f) / SR) > 0.95).astype(float)
    x = _band(pulses + 0.1 * rng.standard_normal(len(t)), 300, 3000)
    return _norm(x * np.sin(np.pi * t / d), 0.5)


def fall(rng):
    """A long falling whistle."""
    d = 2.2
    t = _t(d)
    f = 1400 * (0.25 ** (t / d))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.2)
    return _norm(x, 0.35)


def screech(rng):
    """An eagle's high cry."""
    d = 0.8
    x = _chirp(2400, 1600, d, (1.0, 0.4, 0.2))
    x = x * (0.7 + 0.3 * np.sin(TAU * 40 * _t(d)))
    return _norm(x, 0.4)


EXTRA_SFX = {"rain": (rain, 0.5), "jungle": (jungle, 0.5), "thump": (thump, 0.7), "drip": (drip, 0.5),
             "squawk": (squawk, 0.5), "flap": (flap, 0.45), "snore": (snore, 0.5), "growl": (growl, 0.5),
             "hoot": (hoot, 0.4), "creak": (creak, 0.5), "fall": (fall, 0.45), "screech": (screech, 0.4)}
