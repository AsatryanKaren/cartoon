"""Scottish sound effects, synthesised with numpy (48 kHz mono float).

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


def _midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def _bell(f, d, decays=(5, 7, 10, 14)):
    t = _t(d)
    parts = ((1, 1.0), (2.0, 0.45), (3.0, 0.25), (4.2, 0.12))
    return sum(g * np.sin(TAU * f * h * t) * np.exp(-t * k) for (h, g), k in zip(parts, decays)) \
        * np.minimum(1, t / 0.002)


def _reed(freq, n, bright=0.86):
    """A nasal chanter-like reed: many odd-ish harmonics."""
    t = np.arange(n) / SR
    ph = TAU * np.cumsum(np.full(n, freq) * (1 + 0.002 * np.sin(TAU * 5 * t))) / SR
    return sum((bright ** h) * (1.0 if h % 2 else 0.6) * np.sin(h * ph) for h in range(1, 14))


def pipes(rng):
    """Bagpipes: a steady drone on A with a chanter tune and quick grace notes."""
    d = 6.0
    n = int(d * SR)
    t = _t(d)
    drone = _reed(_midi(45), n, 0.8) * 0.5 + _reed(_midi(57), n, 0.8) * 0.35
    out = drone * _env(n, 0.4, 1.0)
    # pipe scale: A B C# D E F# G A' B' (mixolydian), a little air in 6/8 feel
    tune = [(69, 0.6), (73, 0.3), (76, 0.6), (73, 0.3), (69, 0.6), (71, 0.3), (73, 0.9),
            (76, 0.45), (78, 0.45), (81, 0.6), (78, 0.3), (76, 0.9)]
    tt = 0.35
    for k, (note, dur) in enumerate(tune):
        if tt + dur > d - 0.3:
            break
        # grace note: a high G flick before each melody note
        g = int(0.035 * SR)
        _place(out, tt, _reed(_midi(79), g) * _env(g, 0.003, 0.01), 0.5)
        m = int(dur * SR)
        _place(out, tt + 0.035, _reed(_midi(note), m) * _env(m, 0.01, 0.03), 0.75)
        tt += dur
    out = _band(out, 90, 6000)
    return _norm(out, 0.42)


def crunch(rng):
    """Biting shortbread: a crumbly crunch."""
    d = 0.3
    n = int(d * SR)
    grains = (rng.random(n) < 0.25) * rng.standard_normal(n)
    x = _band(grains, 1200, 9000) * _env(n, 0.002, 0.1, 9)
    return _norm(x, 0.5)


def tinclang(rng):
    """An empty biscuit tin rattling: a hollow metallic clang."""
    d = 1.0
    t = _t(d)
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * k)
            for f, g, k in ((410, 1.0, 6), (987, 0.6, 9), (1650, 0.4, 12), (2410, 0.3, 16)))
    x += 0.4 * _band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 40)
    return _norm(x * np.minimum(1, t / 0.002), 0.5)


def honk(rng):
    """One goose honk: a nasal falling 'hronk'."""
    d = 0.32
    t = _t(d)
    f = 380 - 90 * t / d
    ph = TAU * np.cumsum(f) / SR
    x = sum((0.85 ** h) * np.sin(h * ph) for h in range(1, 12))
    x = _band(x, 250, 4000) * _env(len(t), 0.02, 0.08)
    return _norm(x, 0.5)


def geese(rng):
    """A skein of wild geese calling as they fly over."""
    out = np.zeros(int(3.2 * SR))
    for k in range(9):
        h = honk(rng)
        _place(out, rng.uniform(0, 2.7), h, rng.uniform(0.4, 1.0))
    return _norm(out * _env(len(out), 0.5, 0.8), 0.45)


def wings(rng):
    """Big wings beating: soft whooshes in a steady rhythm."""
    d = 3.0
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(int(d / 0.42)):
        m = int(0.3 * SR)
        x = _band(rng.standard_normal(m), 200, 1800) * np.sin(np.pi * np.arange(m) / m) ** 2
        _place(out, k * 0.42, x, 0.8 + 0.2 * (k % 2))
    return _norm(out * _env(n, 0.3, 0.6), 0.35)


def thud(rng):
    """A soft landing on grass."""
    d = 0.45
    t = _t(d)
    x = np.sin(TAU * (70 + 60 * np.exp(-t * 25)) * t) * np.exp(-t * 14)
    x += 0.4 * _band(rng.standard_normal(len(t)), 100, 1500) * np.exp(-t * 30)
    return _norm(x, 0.55)


def shutter(rng):
    """Camera shutter: click-clack."""
    out = np.zeros(int(0.3 * SR))
    for start, f in ((0.0, 3000), (0.09, 2200)):
        m = int(0.03 * SR)
        x = _band(rng.standard_normal(m), f * 0.5, f * 2.5) * _env(m, 0.001, 0.02, 60)
        _place(out, start, x)
    return _norm(out, 0.5)


def yip(rng):
    """A small terrier's happy yip-yip."""
    out = np.zeros(int(0.5 * SR))
    for start in (0.0, 0.18):
        d = 0.11
        t = _t(d)
        f = 900 + 500 * np.sin(np.pi * t / d)
        ph = TAU * np.cumsum(f) / SR
        x = sum((0.6 ** h) * np.sin(h * ph) for h in range(1, 7))
        _place(out, start, x * _env(len(t), 0.005, 0.04))
    return _norm(_band(out, 300, 6000), 0.4)


def gulp(rng):
    d = 0.35
    t = _t(d)
    f = 300 - 200 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 10)
    return _norm(x, 0.55)


def zip_(rng):
    """Cartoon zoom: a fast rising whistle with a whoosh."""
    d = 0.45
    t = _t(d)
    f = 500 + 2200 * (t / d) ** 1.5
    x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.1)
    x += 0.5 * _band(rng.standard_normal(len(t)), 800, 5000) * np.sin(np.pi * t / d)
    return _norm(x, 0.4)


def boing(rng):
    """Cartoon spring landing."""
    d = 0.7
    t = _t(d)
    f = 180 + 120 * np.sin(TAU * 9 * t) * np.exp(-t * 4)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 4) * np.minimum(1, t / 0.005)
    return _norm(x, 0.45)


def gun(rng):
    """The One O'Clock Gun: a huge boom with a long rumbling echo off the city."""
    d = 3.5
    n = int(d * SR)
    t = _t(d)
    crack = _band(rng.standard_normal(n), 300, 8000) * np.exp(-t * 35)
    body = _band(rng.standard_normal(n), 30, 300) * np.exp(-t * 3.5)
    thump = np.sin(TAU * (40 + 50 * np.exp(-t * 12)) * t) * np.exp(-t * 4)
    x = 0.8 * crack + 1.4 * body + 1.2 * thump
    echo = np.zeros(n)
    _place(echo, 0.42, x[:n // 2] * 0.35)
    _place(echo, 0.95, x[:n // 2] * 0.18)
    return _norm(np.tanh(1.5 * (x + echo)), 0.9)


def yowl(rng):
    """Whiskers' startled cartoon yowl: a meow that shoots up."""
    d = 0.9
    t = _t(d)
    u = t / d
    f = 500 + 900 * np.minimum(1, u * 2.5) - 300 * u + 25 * np.sin(TAU * 14 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 7))
    return _norm(x * _env(len(t), 0.02, 0.3), 0.5)


def bell(rng):
    """A distant kirk bell, two slow strokes."""
    out = np.zeros(int(4.0 * SR))
    for k in range(2):
        _place(out, k * 1.6, _bell(220, 2.4, (1.2, 1.8, 2.6, 3.4)), 1.0)
    return _norm(_band(out, 80, 5000), 0.35)


def sparkle(rng):
    out = np.zeros(int(1.8 * SR))
    for k in range(14):
        f = rng.uniform(2000, 5000)
        _place(out, k * 0.08 + rng.uniform(0, 0.03), _bell(f, 0.6, (9, 12, 16, 20)), rng.uniform(0.4, 1.0))
    return _norm(out, 0.4)


def stag(rng):
    """A red deer stag's roar, far away across the glen."""
    d = 1.6
    t = _t(d)
    u = t / d
    f = 140 + 60 * np.sin(np.pi * u)
    ph = TAU * np.cumsum(f) / SR
    x = sum((0.8 ** h) * np.sin(h * ph) for h in range(1, 12)) * (1 + 0.4 * np.sin(TAU * 22 * t))
    x += 0.5 * _band(rng.standard_normal(len(t)), 200, 1500)
    return _norm(_band(x, 80, 3000) * _env(len(t), 0.15, 0.5), 0.35)


def moo(rng):
    """A deep, friendly Highland moo."""
    d = 1.4
    t = _t(d)
    u = t / d
    f = 110 + 30 * np.sin(np.pi * np.minimum(1, u * 1.2)) - 15 * u
    ph = TAU * np.cumsum(f) / SR
    x = sum((0.82 ** h) * np.sin(h * ph) for h in range(1, 14))
    x = _band(x, 60, 2500) * _env(len(t), 0.12, 0.35)
    return _norm(x, 0.5)


def clonk(rng):
    """Horns bumping into a rock: a hollow clonk."""
    d = 0.5
    t = _t(d)
    x = (np.sin(TAU * 320 * t) + 0.6 * np.sin(TAU * 750 * t) + 0.3 * np.sin(TAU * 1310 * t)) * np.exp(-t * 18)
    x += 0.5 * _band(rng.standard_normal(len(t)), 300, 3000) * np.exp(-t * 60)
    return _norm(x, 0.55)


def clomp(rng):
    """Heavy, slow hooves on soft ground."""
    d = 3.0
    out = np.zeros(int(d * SR))
    for k in range(int(d / 0.5)):
        m = int(0.12 * SR)
        tt = np.arange(m) / SR
        x = np.sin(TAU * (90 + 40 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 25)
        x += 0.3 * _band(rng.standard_normal(m), 200, 1500) * np.exp(-tt * 40)
        _place(out, k * 0.5 + (0.05 if k % 2 else 0), x)
    return _norm(out * _env(len(out), 0.2, 0.5), 0.45)


def lap(rng):
    """Small waves lapping on a pebbly shore."""
    d = 5.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 200, 2500) * (0.3 + 0.7 * np.sin(np.pi * ((t / 1.6) % 1.0)) ** 3)
    return _norm(x * _env(n, 0.8, 1.2), 0.3)


def owl(rng):
    out = np.zeros(int(1.8 * SR))
    for start, d in ((0.0, 0.45), (0.75, 0.2), (1.0, 0.5)):
        t = _t(d)
        f = 400 - 30 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) + 0.15 * _band(rng.standard_normal(len(t)), 300, 1200)
        _place(out, start, x * _env(len(t), 0.06, 0.15))
    return _norm(out, 0.32)


def bubbles(rng):
    """Bubbles rising from the deep: little blooping pops."""
    out = np.zeros(int(1.6 * SR))
    for k in range(9):
        m = int(0.07 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(300, 700) * (1 + 2.0 * tt / 0.07)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 45)
        _place(out, k * 0.15 + rng.uniform(0, 0.05), x, rng.uniform(0.5, 1.0))
    return _norm(out, 0.4)


def rise(rng):
    """Something big rising out of the water: a long gentle wash with drips."""
    d = 2.6
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 150, 3000) * np.sin(np.pi * t / d) ** 1.5
    for _ in range(16):
        m = int(0.06 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(800, 1500) * (1 + 1.5 * tt / 0.06)
        _place(x, rng.uniform(0.8, 2.4), np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 60), rng.uniform(0.2, 0.5))
    return _norm(x, 0.4)


def jingle(rng):
    """Luna's little collar bell."""
    out = np.zeros(int(0.9 * SR))
    for k, start in enumerate((0.0, 0.12)):
        t = _t(0.7)
        f0 = 2650 + 90 * k
        x = sum(g * np.sin(TAU * f0 * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 7), (1.51, 0.5, 10), (2.42, 0.3, 14), (3.9, 0.15, 20)))
        _place(out, start, x * np.minimum(1, t / 0.002), 0.7 if k else 1.0)
    return _norm(out, 0.5)


EXTRA_SFX = {
    "pipes": (pipes, 0.42), "crunch": (crunch, 0.5), "tinclang": (tinclang, 0.5), "honk": (honk, 0.45),
    "geese": (geese, 0.45), "wings": (wings, 0.35), "thud": (thud, 0.55), "shutter": (shutter, 0.5),
    "yip": (yip, 0.45), "gulp": (gulp, 0.5), "zip": (zip_, 0.4), "boing": (boing, 0.45), "gun": (gun, 0.85),
    "yowl": (yowl, 0.5), "bell": (bell, 0.4), "sparkle": (sparkle, 0.4), "stag": (stag, 0.4), "moo": (moo, 0.5),
    "clonk": (clonk, 0.5), "clomp": (clomp, 0.4), "lap": (lap, 0.35), "owl": (owl, 0.35),
    "bubbles": (bubbles, 0.45), "rise": (rise, 0.45), "jingle": (jingle, 0.45),
}
