"""Norway sound effects, synthesised with numpy (48 kHz mono float).

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


def _sweep(f, d):
    """Phase of a gliding frequency track f (array, Hz)."""
    return TAU * np.cumsum(f) / SR


# ------------------------------------------------------------------ nature

def wind(rng):
    """Cold mountain wind: band noise with a slowly gliding resonance."""
    d = 4.0
    n = int(d * SR)
    t = _t(d)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks, step = 40, n // 40
    for c in range(chunks):
        u = c / chunks
        f = 300 + 380 * np.sin(np.pi * u) ** 2 + 90 * np.sin(u * 13)
        seg = _band(noise[c * step:c * step + 2 * step], f * 0.8, f * 1.25)
        _place(out, c * step / SR, seg * np.hanning(len(seg)))
    low = _band(rng.standard_normal(n), 50, 350) * 0.6
    return _norm((out + low) * np.sin(np.pi * t / d) ** 1.5, 0.5)


def shimmer(rng):
    """The northern lights: a soft glassy chord that swells and sparkles."""
    d = 4.5
    t = _t(d)
    x = np.zeros(len(t))
    for f in (587.3, 740.0, 880.0, 1174.7, 1480.0):
        x += np.sin(TAU * f * t + 2 * np.sin(TAU * 0.3 * t)) * (0.6 + 0.4 * np.sin(TAU * rng.uniform(0.2, 0.6) * t))
    x *= np.sin(np.pi * t / d) ** 2
    for _ in range(22):
        m = int(0.4 * SR)
        tt = np.arange(m) / SR
        f = rng.choice([1760, 2217, 2637, 2960, 3520])
        _place(x, rng.uniform(0.3, d - 0.5), np.sin(TAU * f * tt) * np.exp(-tt * 9), 0.5)
    return _norm(x, 0.4)


def waves(rng):
    """Water lapping against a wooden hull."""
    d = 4.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 150, 1800) * (0.5 + 0.5 * np.sin(TAU * 0.6 * t) ** 2)
    for k in range(5):
        m = int(0.3 * SR)
        slap = _band(rng.standard_normal(m), 200, 2500) * _env(m, 0.01, 0.2, 10)
        _place(x, 0.4 + k * 0.75 + rng.uniform(-0.1, 0.1), slap, 1.5)
    return _norm(x * _env(n, 0.4, 0.8), 0.4)


def falls(rng):
    """A waterfall: a wide, steady roar."""
    d = 4.0
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 120, 6000) + 0.6 * _band(rng.standard_normal(n), 60, 300)
    return _norm(x * _env(n, 0.8, 1.2), 0.45)


def crunch(rng):
    """One footstep in snow."""
    d = 0.28
    n = int(d * SR)
    t = _t(d)
    grains = (rng.random(n) < 0.08) * rng.standard_normal(n)
    x = _band(grains + 0.3 * rng.standard_normal(n), 900, 7000) * np.sin(np.pi * t / d) ** 0.7
    return _norm(x, 0.5)


def stomp(rng):
    """A heavy hoof in deep snow: low thud plus crunch."""
    d = 0.5
    t = _t(d)
    x = np.sin(TAU * (60 + 50 * np.exp(-t * 18)) * t) * np.exp(-t * 10)
    x += 0.5 * _band(rng.standard_normal(len(t)), 600, 5000) * np.exp(-t * 16)
    return _norm(x, 0.6)


def snap(rng):
    """A twig cracking in the dark forest."""
    d = 0.25
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1200, 8000) * np.exp(-t * 60)
    x2 = _band(rng.standard_normal(len(t)), 800, 6000) * np.exp(-np.maximum(0, t - 0.05) * 70) * (t > 0.05)
    return _norm(x + 0.7 * x2, 0.6)


def bellow(rng):
    """A moose's long, low, friendly call."""
    d = 1.4
    t = _t(d)
    f = 110 + 50 * np.sin(np.pi * t / d) - 20 * t
    ph = _sweep(f, d)
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 10))
    x = _band(x, 70, 1800) * _env(len(t), 0.15, 0.4)
    return _norm(x, 0.55)


def puffin(rng):
    """A puffin's happy grumbly chuckle: 'arr-arr-arr'."""
    out = np.zeros(int(0.9 * SR))
    for k in range(3):
        d = 0.16
        t = _t(d)
        f = 380 + 140 * np.sin(np.pi * t / d) - 30 * k
        ph = _sweep(f, d)
        x = sum((1 / h) * np.sin(h * ph) for h in range(1, 7)) * (0.6 + 0.4 * np.sign(np.sin(TAU * 38 * t)))
        _place(out, k * 0.2, _band(x, 150, 3500) * _env(len(t), 0.01, 0.05), 1.0 - 0.2 * k)
    return _norm(out, 0.5)


def bells(rng):
    """Reindeer harness bells, a light jingle."""
    d = 1.6
    out = np.zeros(int(d * SR))
    for k in range(10):
        m = int(0.4 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(2600, 3400)
        x = (np.sin(TAU * f * tt) + 0.5 * np.sin(TAU * f * 1.52 * tt)) * np.exp(-tt * 14)
        _place(out, k * 0.12 + rng.uniform(0, 0.05), x, rng.uniform(0.4, 0.9))
    return _norm(out, 0.4)


# --------------------------------------------------------------- machines

def engine(rng):
    """A small delivery van chugging along."""
    d = 3.0
    n = int(d * SR)
    t = _t(d)
    f = 38 + 6 * np.sin(TAU * 0.5 * t)
    ph = _sweep(f, d)
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 8)) * (0.7 + 0.3 * np.sin(ph * 0.5) ** 2)
    x += 0.2 * _band(rng.standard_normal(n), 100, 900)
    return _norm(x * _env(n, 0.3, 0.8), 0.4)


def brakes(rng):
    """A short squeak of brakes."""
    d = 0.6
    t = _t(d)
    f = 1900 - 300 * t / d
    x = np.sin(_sweep(f, d)) * (0.7 + 0.3 * np.sin(TAU * 30 * t)) * _env(len(t), 0.03, 0.2)
    return _norm(x, 0.3)


def plane(rng):
    """Propeller cargo plane droning overhead."""
    d = 5.0
    n = int(d * SR)
    t = _t(d)
    buzz = sum((1 / h) * np.sin(TAU * 72 * h * t) for h in range(1, 8)) * (0.6 + 0.4 * np.sin(TAU * 18 * t))
    x = buzz * 0.5 + _band(rng.standard_normal(n), 80, 1200)
    return _norm(x * _env(n, 0.8, 1.2), 0.4)


def horn(rng):
    """A Viking horn: a long, low, hollow note that bends up."""
    d = 1.8
    t = _t(d)
    f = 147 + 8 * np.minimum(1, t / 0.3) + 2 * np.sin(TAU * 5 * t)
    ph = _sweep(f, d)
    x = sum((0.8 ** h) * np.sin(h * ph) for h in range(1, 9))
    x += 0.1 * _band(rng.standard_normal(len(t)), 300, 2000)
    return _norm(x * _env(len(t), 0.12, 0.45), 0.5)


def oars(rng):
    """Two oar strokes: a dip and a swirl of water."""
    out = np.zeros(int(1.5 * SR))
    for k in range(2):
        m = int(0.5 * SR)
        tt = np.arange(m) / SR
        x = _band(rng.standard_normal(m), 300, 3000) * np.exp(-tt * 7) * np.minimum(1, tt / 0.02)
        x += np.sin(TAU * 180 * tt) * np.exp(-tt * 25) * 0.4          # wooden knock
        _place(out, k * 0.7, x)
    return _norm(out, 0.45)


# -------------------------------------------------------------------- comedy

def sniff(rng):
    """Three quick sniffs."""
    out = np.zeros(int(0.8 * SR))
    for k in range(3):
        m = int(0.11 * SR)
        x = _band(rng.standard_normal(m), 2000, 7000) * np.sin(np.pi * np.arange(m) / m)
        _place(out, k * 0.17, x)
    return _norm(out, 0.35)


def thump(rng):
    """Landing in a wooden crate."""
    d = 0.5
    t = _t(d)
    x = (np.sin(TAU * 120 * t) + 0.5 * np.sin(TAU * 240 * t)) * np.exp(-t * 14)
    x += _band(rng.standard_normal(len(t)), 200, 2500) * np.exp(-t * 35) * 0.6
    return _norm(x, 0.6)


def slam(rng):
    """A crate lid banging shut."""
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 4000) * np.exp(-t * 30)
    x += (np.sin(TAU * 95 * t) + 0.6 * np.sin(TAU * 210 * t)) * np.exp(-t * 11)
    return _norm(x, 0.7)


def creak(rng):
    """An old wooden lid creaking open."""
    d = 0.7
    t = _t(d)
    f = 300 + 180 * t / d + 40 * np.sin(TAU * 7 * t)
    pulses = (np.sin(TAU * 55 * t) > 0.6).astype(float)
    x = np.sign(np.sin(_sweep(f, d))) * pulses
    return _norm(_band(x, 200, 3000) * _env(len(t), 0.05, 0.1), 0.35)


def bell(rng):
    """A harbour bell ringing twice."""
    out = np.zeros(int(2.4 * SR))
    for k in range(2):
        t = _t(1.8)
        f = 420
        x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 2), (2.0, 0.5, 3), (2.76, 0.35, 4), (5.4, 0.15, 7)))
        _place(out, k * 0.6, x)
    return _norm(out, 0.4)


def sizzle(rng):
    """A waffle iron hissing."""
    d = 1.4
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 3000, 11000) * (0.6 + 0.4 * rng.random(n))
    for _ in range(30):
        m = int(0.01 * SR)
        _place(x, rng.uniform(0, d - 0.02), rng.standard_normal(m) * np.exp(-np.arange(m) / m * 5), 0.8)
    return _norm(x * _env(n, 0.05, 0.4), 0.3)


def yowl(rng):
    """A startled cat's 'MRAOW!'."""
    d = 0.7
    t = _t(d)
    u = t / d
    f = 600 + 500 * np.sin(np.pi * np.minimum(1, u * 1.6)) - 200 * u + 25 * np.sin(TAU * 9 * t)
    ph = _sweep(f, d)
    x = sum((1.0 / h) * np.sin(h * ph) for h in range(1, 8))
    return _norm(x * _env(len(t), 0.02, 0.2), 0.5)


def boing(rng):
    """Cartoon hop."""
    d = 0.4
    t = _t(d)
    f = 220 + 260 * np.sin(np.pi * t / d) + 30 * np.sin(TAU * 18 * t)
    x = np.sin(_sweep(f, d)) * _env(len(t), 0.005, 0.15)
    return _norm(x, 0.4)


def munch(rng):
    """Crunchy waffle bites."""
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        m = int(0.09 * SR)
        x = _band(rng.standard_normal(m), 700, 6000) * _env(m, 0.003, 0.05, 25)
        _place(out, k * 0.18, x, 1.0 - 0.2 * k)
    return _norm(out, 0.4)


EXTRA_SFX = {
    "wind": (wind, 0.45), "shimmer": (shimmer, 0.4), "waves": (waves, 0.4), "falls": (falls, 0.45),
    "crunch": (crunch, 0.35), "stomp": (stomp, 0.6), "snap": (snap, 0.5), "bellow": (bellow, 0.6),
    "puffin": (puffin, 0.5), "bells": (bells, 0.35), "engine": (engine, 0.45), "brakes": (brakes, 0.3),
    "plane": (plane, 0.4), "horn": (horn, 0.5), "oars": (oars, 0.4), "sniff": (sniff, 0.45),
    "thump": (thump, 0.6), "slam": (slam, 0.65), "creak": (creak, 0.4), "bell": (bell, 0.35),
    "sizzle": (sizzle, 0.4), "yowl": (yowl, 0.6), "boing": (boing, 0.45), "munch": (munch, 0.5),
}
