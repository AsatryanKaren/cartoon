"""Episode 3 sounds (48 kHz mono float). EXTRA_SFX maps names to (function, gain); MOODS adds music."""
import numpy as np

SR = 48000
TAU = 2 * np.pi
MAJ, MIN = (0, 4, 7), (0, 3, 7)

MOODS = {
    # slow, deep and dreamy for the dive into the deep Pacific
    "w_deep": dict(bpm=60, prog=[(50, MIN), (46, MAJ), (53, MAJ), (48, MAJ)], drums=False, mel=0.3, oct=74,
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


def whalesong(rng):
    """A gentle whale call: two long gliding hums with vibrato, a little echo."""
    d = 3.2
    t = _t(d)
    out = np.zeros(len(t))
    for st, dur, f0, f1 in ((0.0, 1.5, 220, 330), (1.5, 1.6, 300, 180)):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        u = tt / dur
        f = f0 + (f1 - f0) * (3 * u * u - 2 * u ** 3) + 6 * np.sin(TAU * 5 * tt)
        ph = TAU * np.cumsum(f) / SR
        x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
        env = np.sin(np.pi * u) ** 1.5
        i = int(st * SR)
        out[i:i + n] += (x * env)[:len(out) - i]
    echo = np.zeros_like(out)
    k = int(0.28 * SR)
    echo[k:] = out[:-k] * 0.35
    return _norm(out + echo, 0.5)


def spout(rng):
    """Whale blowing out of its blowhole: a breathy whoosh of spray."""
    d = 1.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 400, 5000)
    env = np.minimum(1, t / 0.05) * np.exp(-t * 2.6)
    drops = np.zeros(len(t))
    for _ in range(30):
        i = int(rng.uniform(0.3, 1.1) * SR)
        n = int(0.01 * SR)
        drops[i:i + n] += rng.uniform(0.2, 0.6) * np.sin(TAU * rng.uniform(1500, 3000) * np.arange(n) / SR) \
            * np.exp(-np.arange(n) / SR * 400)
    return _norm(x * env + drops * 0.4, 0.55)


def lap(rng):
    """One cat lap at the water: a tiny wet click."""
    t = _t(0.12)
    f = 900 + 1400 * t / 0.12
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 40)
    x += _band(rng.standard_normal(len(t)), 1000, 6000) * np.exp(-t * 80) * 0.5
    return _norm(x, 0.45)


def boing(rng):
    """Comic yuck-boing: a wobbly falling spring."""
    d = 0.7
    t = _t(d)
    f = 520 * np.exp(-t * 1.6) * (1 + 0.12 * np.sin(TAU * 14 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return _norm(x, 0.5)


def wind(rng):
    """A gust of wind over the sea."""
    d = 2.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 1400)
    sweep = np.sin(np.pi * t / d) ** 1.5 * (0.7 + 0.3 * np.sin(TAU * 0.9 * t))
    return _norm(x * sweep, 0.5)


def waves(rng):
    """A wave washing up the sand and drawing back."""
    d = 2.8
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 200, 6000)
    env = np.minimum(1, t / 0.5) * np.exp(-np.maximum(0, t - 0.5) * 1.4)
    fizz = _band(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-np.abs(t - 1.2) * 3) * 0.4
    return _norm(x * env + fizz, 0.5)


def snip(rng):
    """Crab claws: snip-snip."""
    out = np.zeros(int(0.35 * SR))
    for st in (0.0, 0.15):
        n = int(0.03 * SR)
        tt = np.arange(n) / SR
        x = _band(rng.standard_normal(n), 2500, 9000) * np.exp(-tt * 200)
        x += np.sin(TAU * 1800 * tt) * np.exp(-tt * 150) * 0.6
        i = int(st * SR)
        out[i:i + n] += x
    return _norm(out, 0.5)


def bloop(rng):
    """Bubbles rising: three quick rising 'bloop's."""
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        d = 0.12
        t = np.arange(int(d * SR)) / SR
        f0 = rng.uniform(260, 420)
        f = f0 * (1 + 2.2 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int((k * 0.16 + rng.uniform(0, 0.04)) * SR)
        out[i:i + len(x)] += x * (1 - 0.2 * k)
    return _norm(out, 0.5)


EXTRA_SFX = {"whalesong": (whalesong, 0.6), "spout": (spout, 0.5), "lap": (lap, 0.5), "boing": (boing, 0.5),
             "wind": (wind, 0.45), "waves": (waves, 0.45), "snip": (snip, 0.5), "bloop": (bloop, 0.5)}
