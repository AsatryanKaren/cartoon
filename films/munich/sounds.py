"""Bavarian sound effects, synthesised with numpy (48 kHz mono float).

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


def _bell(f, d, decays=(5, 7, 10, 14)):
    t = _t(d)
    parts = ((1, 1.0), (2.0, 0.45), (3.0, 0.25), (4.2, 0.12))
    return sum(g * np.sin(TAU * f * h * t) * np.exp(-t * k) for (h, g), k in zip(parts, decays)) \
        * np.minimum(1, t / 0.002)


def chime(rng):
    """Storybook music box: a little rising arpeggio of bell notes."""
    out = np.zeros(int(2.4 * SR))
    for k, n in enumerate((74, 78, 81, 86, 90)):
        f = 440 * 2 ** ((n - 69) / 12)
        _place(out, k * 0.16, _bell(f, 1.6, (4, 6, 9, 13)), 1.0 - 0.1 * k)
    return _norm(out, 0.5)


def glock(rng):
    """The Glockenspiel on the town hall: a tune of tuned bells, a little far away."""
    tune = (72, 76, 79, 76, 77, 74, 79, 72)
    out = np.zeros(int(3.6 * SR))
    for k, n in enumerate(tune):
        f = 440 * 2 ** ((n - 69) / 12)
        _place(out, k * 0.34, _bell(f, 1.4, (3, 5, 8, 11)), 0.8 + 0.2 * (k % 2))
    out = _band(out, 200, 6000)
    return _norm(out, 0.45)


def rain(rng):
    """Rain on the window: soft hiss with tiny drops."""
    d = 5.0
    n = int(d * SR)
    x = 0.35 * _band(rng.standard_normal(n), 800, 7000)
    for _ in range(160):
        m = int(0.012 * SR)
        drop = _band(rng.standard_normal(m), 2000, 9000) * np.exp(-np.arange(m) / m * 6)
        _place(x, rng.uniform(0, d - 0.02), drop, rng.uniform(0.2, 0.8))
    return _norm(x * _env(n, 0.8, 1.2), 0.35)


def thud(rng):
    """A parcel or a heavy book landing."""
    d = 0.5
    t = _t(d)
    x = np.sin(TAU * (80 + 60 * np.exp(-t * 25)) * t) * np.exp(-t * 14)
    x += 0.5 * _band(rng.standard_normal(len(t)), 100, 1500) * np.exp(-t * 30)
    return _norm(x, 0.6)


def tape(rng):
    """Sticky tape pulled off the roll: a rising crackly rip."""
    d = 0.7
    n = int(d * SR)
    t = _t(d)
    grains = (rng.random(n) < 0.18 + 0.2 * t / d) * rng.standard_normal(n)
    x = _band(grains, 1500, 9000) * np.sin(np.pi * t / d) ** 0.6
    return _norm(x, 0.45)


def stamp(rng):
    """A rubber stamp: a quick knock with a soft wooden body."""
    d = 0.35
    t = _t(d)
    x = (np.sin(TAU * 220 * t) + 0.5 * np.sin(TAU * 530 * t)) * np.exp(-t * 30)
    x += _band(rng.standard_normal(len(t)), 300, 4000) * np.exp(-t * 60)
    return _norm(x, 0.6)


def posthorn(rng):
    """The post horn: a bright little brass call, three notes."""
    out = np.zeros(int(1.5 * SR))
    for start, n, d in ((0.0, 72, 0.22), (0.25, 77, 0.22), (0.5, 81, 0.7)):
        f = 440 * 2 ** ((n - 69) / 12)
        t = _t(d)
        vib = 1 + 0.004 * np.sin(TAU * 5.5 * t)
        ph = TAU * np.cumsum(f * vib) / SR
        x = sum((0.9 ** h) * np.sin(h * ph) for h in range(1, 9))
        _place(out, start, x * _env(len(t), 0.03, 0.08))
    return _norm(_band(out, 200, 6000), 0.4)


def engine(rng):
    """The post van humming along the road."""
    d = 4.5
    n = int(d * SR)
    t = _t(d)
    f = 48 + 3 * np.sin(TAU * 0.3 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 7))
    x += 0.6 * _band(rng.standard_normal(n), 60, 500)
    x += 0.2 * _band(rng.standard_normal(n), 1000, 3000) * (0.5 + 0.5 * np.sin(TAU * 0.5 * t))
    return _norm(x * _env(n, 0.8, 1.0), 0.4)


def tuba(rng):
    """Oompah: a tuba bass note and a brass chord answer, twice."""
    out = np.zeros(int(2.0 * SR))

    def brass(f, d, bright):
        t = _t(d)
        ph = TAU * f * t
        x = sum((bright ** h) * np.sin(h * ph) for h in range(1, 10))
        return x * _env(len(t), 0.03, 0.08)
    for k in range(2):
        b = k * 0.9
        _place(out, b, brass(58.3 if k == 0 else 43.7, 0.4, 0.6), 1.0)
        for f in (233, 294, 349):
            _place(out, b + 0.45, brass(f, 0.3, 0.75), 0.25)
    return _norm(_band(out, 40, 5000), 0.5)


def roll(rng):
    """Something round and bready rolling over cobblestones: a run of little bumps."""
    d = 2.4
    n = int(d * SR)
    out = np.zeros(n)
    tt = 0.0
    k = 0
    while tt < d - 0.1:
        m = int(0.05 * SR)
        bump = _band(rng.standard_normal(m), 120, 1500) * _env(m, 0.002, 0.04, 30)
        _place(out, tt, bump, rng.uniform(0.5, 1.0))
        tt += 0.11 + 0.02 * np.sin(k)
        k += 1
    return _norm(out * _env(n, 0.05, 0.5), 0.4)


def chitter(rng):
    """Squirrel chatter: fast high chirps."""
    out = np.zeros(int(0.8 * SR))
    for k in range(7):
        d = 0.045
        t = _t(d)
        f = rng.uniform(3200, 4200) - 1500 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.004, 0.02)
        _place(out, k * 0.085, x, rng.uniform(0.6, 1.0))
    return _norm(out, 0.4)


def neigh(rng):
    """A friendly horse whinny: wobbling pitch going up then down."""
    d = 1.3
    t = _t(d)
    u = t / d
    f = 420 + 380 * np.sin(np.pi * np.minimum(1, u * 1.6)) * (1 - u) + 30 * np.sin(TAU * 11 * t) * (u > 0.2)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 8))
    x += 0.4 * _band(rng.standard_normal(len(t)), 800, 4000)
    return _norm(_band(x * _env(len(t), 0.05, 0.4), 150, 5000), 0.45)


def clop(rng):
    """Hooves on a road: a steady clip-clop."""
    d = 3.0
    out = np.zeros(int(d * SR))
    for k in range(int(d / 0.25)):
        m = int(0.05 * SR)
        t = np.arange(m) / SR
        f = 900 if k % 2 else 700
        x = np.sin(TAU * f * t) * np.exp(-t * 80) + 0.4 * _band(rng.standard_normal(m), 600, 3000) * np.exp(-t * 90)
        _place(out, k * 0.25 + (0.04 if k % 2 else 0), x, 0.8 if k % 2 else 1.0)
    return _norm(out * _env(len(out), 0.3, 0.6), 0.4)


def squirt(rng):
    """Whipped cream from a piping bag: a wet hissing pfft."""
    d = 0.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 400, 3500) * np.sin(np.pi * t / d) ** 0.5
    x *= 1 + 0.5 * np.sin(TAU * 30 * t)
    return _norm(x, 0.5)


def gulp(rng):
    """A big happy gulp."""
    d = 0.35
    t = _t(d)
    f = 300 - 200 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 10)
    return _norm(x, 0.55)


def owl(rng):
    """Owl hoot in the dark wood: hoo... hoo-hoo."""
    out = np.zeros(int(1.8 * SR))
    for start, d in ((0.0, 0.45), (0.75, 0.2), (1.0, 0.5)):
        t = _t(d)
        f = 400 - 30 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) + 0.15 * _band(rng.standard_normal(len(t)), 300, 1200)
        _place(out, start, x * _env(len(t), 0.06, 0.15))
    return _norm(out, 0.35)


def twig(rng):
    """A twig snapping underfoot."""
    d = 0.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 50)
    x[int(0.04 * SR):] += _band(rng.standard_normal(len(t) - int(0.04 * SR)), 1000, 6000) * np.exp(-t[:len(t) - int(0.04 * SR)] * 60)
    return _norm(x, 0.5)


def falls(rng):
    """The waterfall in the gorge: a deep steady rush."""
    d = 5.0
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 100, 2500) + 0.4 * _band(rng.standard_normal(n), 2500, 7000)
    return _norm(x * _env(n, 1.0, 1.5), 0.35)


def pebble(rng):
    """Little stones clattering down the rocks."""
    out = np.zeros(int(1.0 * SR))
    tt = 0.0
    for k in range(6):
        m = int(0.03 * SR)
        x = _band(rng.standard_normal(m), 1500, 7000) * _env(m, 0.001, 0.02, 60)
        _place(out, tt, x, 1.0 - 0.12 * k)
        tt += rng.uniform(0.07, 0.18)
    return _norm(out, 0.4)


def pop(rng):
    """Pulled up out of the gorge: a cartoon pop."""
    d = 0.25
    t = _t(d)
    f = 300 + 900 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.1, 10)
    return _norm(x, 0.5)


def knock(rng):
    """A knock on a big wooden castle door."""
    out = np.zeros(int(0.7 * SR))
    for start in (0.0, 0.2):
        d = 0.25
        t = _t(d)
        x = (np.sin(TAU * 110 * t) + 0.7 * np.sin(TAU * 260 * t)) * np.exp(-t * 25)
        x += 0.6 * _band(rng.standard_normal(len(t)), 200, 2500) * np.exp(-t * 50)
        _place(out, start, x)
    return _norm(out, 0.6)


def creak(rng):
    """The great door creaking open."""
    d = 1.4
    t = _t(d)
    f = 140 + 60 * np.sin(TAU * 0.6 * t) + 20 * np.sin(TAU * 7 * t)
    pulses = (np.sin(TAU * np.cumsum(f) / SR) > 0.7).astype(float)
    x = _band(pulses, 150, 3000) * np.sin(np.pi * t / d) ** 0.7
    return _norm(x, 0.35)


def honk(rng):
    """A swan's soft trumpet call."""
    out = np.zeros(int(1.0 * SR))
    for start in (0.0, 0.38):
        d = 0.3
        t = _t(d)
        f = 520 + 40 * np.sin(np.pi * t / d)
        ph = TAU * np.cumsum(f) / SR
        x = sum((0.75 ** h) * np.sin(h * ph) for h in range(1, 8))
        x = _band(x, 300, 3500) * _env(len(t), 0.03, 0.1)
        _place(out, start, x)
    return _norm(out, 0.35)


def sparkle(rng):
    """Storybook magic: a cascade of high twinkles."""
    out = np.zeros(int(1.8 * SR))
    for k in range(14):
        f = rng.uniform(2000, 5000)
        _place(out, k * 0.08 + rng.uniform(0, 0.03), _bell(f, 0.6, (9, 12, 16, 20)), rng.uniform(0.4, 1.0))
    return _norm(out, 0.4)


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
    "chime": (chime, 0.45), "glock": (glock, 0.5), "rain": (rain, 0.4), "thud": (thud, 0.6), "tape": (tape, 0.4),
    "stamp": (stamp, 0.6), "posthorn": (posthorn, 0.45), "engine": (engine, 0.35), "tuba": (tuba, 0.5),
    "roll": (roll, 0.45), "chitter": (chitter, 0.4), "neigh": (neigh, 0.45), "clop": (clop, 0.4),
    "squirt": (squirt, 0.45), "gulp": (gulp, 0.5), "owl": (owl, 0.4), "twig": (twig, 0.45),
    "falls": (falls, 0.35), "pebble": (pebble, 0.45), "pop": (pop, 0.5), "knock": (knock, 0.6),
    "creak": (creak, 0.4), "honk": (honk, 0.45), "sparkle": (sparkle, 0.4), "jingle": (jingle, 0.45),
}
