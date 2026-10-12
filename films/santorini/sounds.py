"""Santorini sound effects, synthesised with numpy (48 kHz mono float).

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
    if 0 <= i < len(buf):
        buf[i:j] += gain * x[:j - i]


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


# ---------------------------------------------------------------- weather / sea

def rain(rng):
    """Steady rain on a window: soft hiss plus little pattering drops."""
    d = 5.0
    n = int(d * SR)
    hiss = _band(rng.standard_normal(n), 1500, 9000) * 0.25
    out = hiss.copy()
    for _ in range(260):
        m = int(0.02 * SR)
        drop = _band(rng.standard_normal(m), 2000, 7000) * np.exp(-_t(0.02) * 220)
        _place(out, rng.uniform(0, d - 0.05), drop, rng.uniform(0.2, 0.8))
    return _norm(out * _env(n, 0.6, 1.0), 0.45)


def waves(rng):
    """Gentle Aegean waves lapping: two slow swells of filtered noise."""
    d = 4.5
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 150, 2200)
    swell = np.sin(np.pi * np.clip(t / 2.2, 0, 1)) ** 2 + 0.8 * np.sin(np.pi * np.clip((t - 2.0) / 2.4, 0, 1)) ** 2
    return _norm(x * swell * _env(n, 0.3, 0.5), 0.4)


def gull(rng):
    """A seagull's cry: two falling, nasal 'kyow' calls."""
    out = np.zeros(int(1.0 * SR))
    for k, st in enumerate((0.0, 0.38)):
        d = 0.3
        t = _t(d)
        f = 1500 - 700 * (t / d) + 120 * np.sin(TAU * 28 * t)
        ph = TAU * np.cumsum(f) / SR
        x = sum(np.sin(h * ph) / h for h in range(1, 6)) * np.sin(np.pi * t / d) ** 0.6
        _place(out, st, _band(x, 600, 6000), 1.0 - 0.3 * k)
    return _norm(out, 0.4)


def flap(rng):
    """Big wing beats (a pelican): three soft whumps."""
    out = np.zeros(int(1.2 * SR))
    for k in range(3):
        d = 0.22
        t = _t(d)
        x = _band(rng.standard_normal(len(t)), 120, 1400) * np.sin(np.pi * t / d) ** 2
        _place(out, k * 0.36, x, 1.0 - 0.15 * k)
    return _norm(out, 0.5)


def wind(rng):
    """A warm sea breeze turning the windmill sails."""
    d = 3.5
    n = int(d * SR)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks, step = 30, n // 30
    for c in range(chunks):
        u = c / chunks
        f = 300 + 300 * np.sin(np.pi * u) ** 2
        seg = _band(noise[c * step:c * step + 2 * step], f * 0.8, f * 1.3)
        _place(out, c * step / SR, seg * np.hanning(len(seg)))
    return _norm(out * np.sin(np.pi * _t(d) / d), 0.4)


# ---------------------------------------------------------------- animals

def hoof(rng):
    """Clip-clop: four donkey hoofsteps on stone."""
    out = np.zeros(int(1.4 * SR))
    for k in range(4):
        d = 0.08
        t = _t(d)
        f0 = 900 if k % 2 == 0 else 760
        x = (np.sin(TAU * f0 * t) * 0.6 + _band(rng.standard_normal(len(t)), 800, 5000) * 0.5) * np.exp(-t * 70)
        _place(out, k * 0.32 + rng.uniform(-0.02, 0.02), x, 0.8 + 0.2 * (k % 2))
    return _norm(out, 0.45)


def bray(rng):
    """A friendly donkey 'hee-haw' (two rasping glides)."""
    out = np.zeros(int(1.6 * SR))
    for k, (f0, f1, st, d) in enumerate(((620, 780, 0.0, 0.45), (300, 220, 0.5, 0.7))):
        t = _t(d)
        f = f0 + (f1 - f0) * t / d
        ph = TAU * np.cumsum(f) / SR
        rasp = 0.6 + 0.4 * np.sign(np.sin(TAU * 34 * t))
        x = sum(np.sin(h * ph) / h ** 0.8 for h in range(1, 9)) * rasp * np.sin(np.pi * t / d) ** 0.5
        _place(out, st, _band(x, 150, 5000))
    return _norm(out, 0.5)


def gulp(rng):
    """A pelican pouch gulp: low, rubbery, falling 'glomp'."""
    d = 0.4
    t = _t(d)
    f = 260 * np.exp(-t * 5) + 70
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 7) * np.minimum(1, t / 0.01)
    return _norm(x, 0.6)


# ---------------------------------------------------------------- island sounds

def bell(rng):
    """A blue-domed chapel bell: bright, ringing partials."""
    d = 3.0
    t = _t(d)
    f0 = 660 + rng.uniform(-30, 30)
    x = sum(g * np.sin(TAU * f0 * h * t) * np.exp(-t * k)
            for h, g, k in ((0.5, 0.5, 1.2), (1.0, 1.0, 1.6), (1.19, 0.5, 2.0), (1.5, 0.4, 2.6),
                            (2.0, 0.3, 3.2), (2.74, 0.2, 4.5)))
    return _norm(x * np.minimum(1, t / 0.003), 0.5)


def bells(rng):
    """Two chapel bells answering each other."""
    out = np.zeros(int(4.0 * SR))
    _place(out, 0.0, bell(rng))
    _place(out, 0.55, bell(rng) * 0.7)
    _place(out, 1.1, bell(rng) * 0.6)
    return _norm(out, 0.5)


def boing(rng):
    """The octopus washing line stretching and springing: a wobbly twang."""
    d = 1.0
    t = _t(d)
    f = 110 + 160 * t / d + 40 * np.sin(TAU * 9 * t) * np.exp(-t * 2)
    x = np.sign(np.sin(TAU * np.cumsum(f) / SR)) * 0.4 + np.sin(TAU * np.cumsum(f * 2) / SR) * 0.4
    return _norm(_band(x, 80, 3000) * np.exp(-t * 2.5) * np.minimum(1, t / 0.005), 0.5)


def stretch(rng):
    """Rope creaking under strain."""
    d = 1.2
    n = int(d * SR)
    t = _t(d)
    pulses = (np.sin(TAU * (30 + 30 * t) * t) > 0.6).astype(float)
    x = _band(rng.standard_normal(n) * pulses, 300, 2500) * np.sin(np.pi * t / d)
    return _norm(x, 0.35)


def sizzle(rng):
    """Octopus on a charcoal grill."""
    d = 2.5
    n = int(d * SR)
    crackle = (rng.random(n) < 0.004) * rng.standard_normal(n) * 3
    x = _band(rng.standard_normal(n) * 0.3 + crackle, 2500, 11000)
    return _norm(x * _env(n, 0.2, 0.6), 0.35)


def munch(rng):
    """Crunchy fritter munches."""
    out = np.zeros(int(1.1 * SR))
    for k in range(4):
        d = 0.12
        g = (rng.random(int(d * SR)) < 0.15) * rng.standard_normal(int(d * SR))
        _place(out, k * 0.25, _band(g, 700, 6000) * np.sin(np.pi * _t(d) / d), 1.0)
    return _norm(out, 0.45)


def murmur(rng):
    """A crowd waiting for the sunset: soft overlapping voices."""
    d = 4.0
    n = int(d * SR)
    out = np.zeros(n)
    for _ in range(26):
        dd = rng.uniform(0.3, 0.8)
        t = _t(dd)
        f = rng.uniform(140, 260) * (1 + 0.1 * np.sin(TAU * rng.uniform(2, 5) * t))
        ph = TAU * np.cumsum(f) / SR
        x = sum(np.sin(h * ph) / h for h in range(1, 7)) * np.sin(np.pi * t / dd)
        _place(out, rng.uniform(0, d - dd), _band(x, 200, 2500), rng.uniform(0.3, 1.0))
    return _norm(out * _env(n, 0.5, 0.8), 0.25)


def applause(rng):
    """The famous Oia sunset applause: many hands, swelling and fading."""
    d = 4.0
    n = int(d * SR)
    out = np.zeros(n)
    for _ in range(700):
        m = int(0.03 * SR)
        clap = _band(rng.standard_normal(m), 600, 6000) * np.exp(-_t(0.03) * 160)
        _place(out, rng.uniform(0, d - 0.05) ** 1.0, clap, rng.uniform(0.3, 1.0))
    t = _t(d)
    shape = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 1.4)
    return _norm(out * shape, 0.55)


def cheer(rng):
    """A short happy 'hooray' from the crowd (a bright vocal swell)."""
    d = 1.4
    n = int(d * SR)
    out = np.zeros(n)
    for _ in range(14):
        t = _t(d)
        f = rng.uniform(220, 420) * (1 + 0.25 * np.sin(np.pi * t / d))
        ph = TAU * np.cumsum(f) / SR
        x = sum(np.sin(h * ph) / h for h in range(1, 8)) * np.sin(np.pi * t / d) ** 1.5
        out += _band(x, 300, 3500) * rng.uniform(0.4, 1.0)
    return _norm(out, 0.35)


def click(rng):
    """A puzzle piece clicking into place."""
    d = 0.12
    t = _t(d)
    x = np.sin(TAU * 1900 * t) * np.exp(-t * 90) + _band(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 200)
    return _norm(x, 0.5)


def pop(rng):
    """A cartoon 'pop' (a sticky piece coming free)."""
    d = 0.18
    t = _t(d)
    f = 300 + 1200 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 25)
    return _norm(x, 0.5)


def sparkle(rng):
    """A glittering run of high notes (magic sunset moment)."""
    out = np.zeros(int(1.6 * SR))
    for k, nt in enumerate((84, 88, 91, 96, 100)):
        t = _t(0.7)
        f = 440 * 2 ** ((nt - 69) / 12)
        _place(out, k * 0.12, np.sin(TAU * f * t) * np.exp(-t * 6), 0.8)
    return _norm(out, 0.35)


EXTRA_SFX = {
    "rain": (rain, 0.5), "waves": (waves, 0.5), "gull": (gull, 0.35), "flap": (flap, 0.5),
    "wind": (wind, 0.4), "hoof": (hoof, 0.5), "bray": (bray, 0.55), "gulp": (gulp, 0.6),
    "bell": (bell, 0.45), "bells": (bells, 0.45), "boing": (boing, 0.6), "stretch": (stretch, 0.5),
    "sizzle": (sizzle, 0.4), "munch": (munch, 0.5), "murmur": (murmur, 0.5), "applause": (applause, 0.7),
    "cheer": (cheer, 0.5), "click": (click, 0.6), "pop": (pop, 0.6), "sparkle": (sparkle, 0.45),
}
