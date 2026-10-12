"""Zermatt sound effects, synthesised with numpy (48 kHz mono float).

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
    return 440.0 * 2 ** ((n - 69) / 12)


def _brass(f, d, vib=0.0, bright=1.0, a=0.12, r=0.4, bend=0.0):
    """A soft wooden horn tone: odd+even harmonics, slow attack, little lip-bend at the start."""
    t = _t(d)
    ff = f * (1 - bend * np.exp(-t * 9)) * (1 + vib * 0.006 * np.sin(TAU * 5 * t))
    ph = TAU * np.cumsum(ff) / SR
    x = sum((1 / h ** (1.6 - 0.6 * bright)) * np.sin(h * ph) for h in range(1, 9))
    x += 0.04 * _band(np.random.default_rng(3).standard_normal(len(t)), 300, 2500)      # breath
    return x * _env(len(t), a, r)


# ------------------------------------------------------------- the alphorn

def alphorn(rng):
    """The big, beautiful alphorn call (natural-horn notes), with a mountain echo."""
    notes = [(55, 0.0, 1.1), (60, 1.0, 0.8), (64, 1.7, 0.8), (67, 2.4, 1.6), (64, 3.9, 0.7), (72, 4.5, 2.2)]
    dry = np.zeros(int(7.0 * SR))
    for n, st, d in notes:
        _place(dry, st, _brass(_midi(n - 12), d + 0.3, vib=1.0, bend=0.03), 1.0)
    out = np.zeros(int(9.5 * SR))
    _place(out, 0, dry)
    for k, (dt, g) in enumerate(((0.9, 0.35), (1.8, 0.18))):
        _place(out, dt, _band(dry, 150, 2500), g)
    return _norm(out, 0.65)


def pfft(rng):
    """Whiskers' first try: a feeble raspberry of air through the horn."""
    d = 0.9
    n = int(d * SR)
    t = _t(d)
    buzz = (np.sin(TAU * 38 * t + 3 * np.sin(TAU * 7 * t)) > 0.3).astype(float)
    x = _band(rng.standard_normal(n) * (0.4 + 0.6 * buzz), 150, 2500) * np.sin(np.pi * t / d) ** 0.8
    return _norm(x, 0.5)


def squawk(rng):
    """Second try: a cracked honk that wobbles and squeaks off pitch."""
    d = 1.1
    t = _t(d)
    f = 180 + 70 * np.sin(TAU * 3.2 * t) + 260 * np.clip((t - 0.6) / 0.4, 0, 1) ** 2
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 10))
    x *= _env(len(t), 0.03, 0.15)
    return _norm(x, 0.5)


def inhale(rng):
    d = 0.9
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 500, 5000) * np.sin(np.pi * t / d) ** 2 * (0.4 + 0.6 * t / d)
    return _norm(x, 0.35)


def echo(rng):
    """A distant little 'baa-aa-aa' coming back off the mountain walls."""
    out = np.zeros(int(2.4 * SR))
    b = baa(rng)
    for k, g in enumerate((0.6, 0.35, 0.18)):
        _place(out, k * 0.55, _band(b, 300, 2200), g)
    return _norm(out, 0.4)


# ------------------------------------------------------------- animals

def baa(rng):
    """A sheep's bleat with its wobbly vibrato."""
    d = rng.uniform(0.7, 0.95)
    t = _t(d)
    f = rng.uniform(300, 380) + 30 * np.sin(np.pi * t / d) + 26 * np.sin(TAU * 9 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 9))
    x = _band(x, 220, 4200)
    return _norm(x * _env(len(t), 0.05, 0.3), 0.5)


def cuckoo(rng):
    """Cuckoo clock: two soft whistle-pipes, a little wooden clack."""
    out = np.zeros(int(1.0 * SR))
    for st, n in ((0.0, 79), (0.32, 75)):
        t = _t(0.3)
        x = np.sin(TAU * _midi(n) * t) + 0.2 * np.sin(TAU * 2 * _midi(n) * t)
        x += 0.15 * _band(rng.standard_normal(len(t)), 1500, 5000)
        _place(out, st, x * _env(len(t), 0.015, 0.1))
    clack = _band(rng.standard_normal(int(0.03 * SR)), 1500, 6000) * np.exp(-_t(0.03) * 120)
    _place(out, 0.0, clack, 0.5)
    return _norm(out, 0.5)


def birds(rng):
    out = np.zeros(int(3.0 * SR))
    for k in range(7):
        d = rng.uniform(0.06, 0.14)
        t = _t(d)
        f0 = rng.uniform(2800, 4200)
        f = f0 + rng.uniform(-900, 900) * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
        _place(out, rng.uniform(0, 2.7), x, rng.uniform(0.4, 1))
    return _norm(out, 0.35)


def flap(rng):
    out = np.zeros(int(0.9 * SR))
    for k in range(6):
        m = int(0.06 * SR)
        x = _band(rng.standard_normal(m), 300, 2500) * np.sin(np.pi * np.arange(m) / m)
        _place(out, k * 0.13, x, 1 - k * 0.12)
    return _norm(out, 0.45)


def sniff(rng):
    out = np.zeros(int(0.6 * SR))
    for k in range(3):
        m = int(0.08 * SR)
        x = _band(rng.standard_normal(m), 1500, 7000) * np.sin(np.pi * np.arange(m) / m)
        _place(out, k * 0.16, x)
    return _norm(out, 0.35)


def clop(rng):
    out = np.zeros(int(1.2 * SR))
    for k, st in enumerate((0.0, 0.18, 0.5, 0.68)):
        t = _t(0.08)
        x = np.sin(TAU * rng.uniform(700, 900) * t) * np.exp(-t * 60)
        x += _band(rng.standard_normal(len(t)), 1000, 4000) * np.exp(-t * 90) * 0.5
        _place(out, st, x)
    return _norm(out, 0.4)


# ------------------------------------------------------------- bells

def _bell(f, d, partials=((1, 1.0, 4), (1.48, 0.7, 5), (2.03, 0.4, 7), (2.94, 0.25, 9))):
    t = _t(d)
    return sum(g * np.sin(TAU * f * h * t) * np.exp(-t * dk) for h, g, dk in partials)


def cowbell(rng):
    """An alpine bell clonk (sheep or cow), slightly different each time."""
    f = rng.uniform(480, 640)
    x = _bell(f, 1.1) + _band(rng.standard_normal(int(1.1 * SR)), 800, 4000) * np.exp(-_t(1.1) * 60) * 0.5
    out = np.zeros(int(1.6 * SR))
    _place(out, 0, x)
    _place(out, rng.uniform(0.22, 0.34), x, 0.55)
    return _norm(out, 0.5)


def bigbell(rng):
    """Berta's enormous bell: a deep clang."""
    x = _bell(230, 2.0, ((1, 1.0, 2.2), (1.5, 0.7, 3), (2.1, 0.5, 4), (3.0, 0.3, 6), (4.2, 0.15, 8)))
    return _norm(x * np.minimum(1, _t(2.0) / 0.003), 0.55)


def bell(rng):
    """Shop-door bell."""
    out = np.zeros(int(1.0 * SR))
    for st in (0.0, 0.1, 0.2):
        _place(out, st, _bell(1900 + rng.uniform(-40, 40), 0.7, ((1, 1, 8), (2.4, 0.4, 12), (3.9, 0.2, 18))))
    return _norm(out, 0.4)


def ding(rng):
    x = _bell(1320, 1.4, ((1, 1, 3), (2.0, 0.3, 5), (3.0, 0.1, 8)))
    return _norm(x, 0.4)


def tick(rng):
    """Clock ticking for a few seconds."""
    d = 4.0
    out = np.zeros(int(d * SR))
    for k in range(int(d / 0.5)):
        m = int(0.02 * SR)
        x = _band(rng.standard_normal(m), 2000, 8000) * np.exp(-np.arange(m) / SR * 200)
        _place(out, k * 0.5, x, 0.9 if k % 2 else 0.6)
    return _norm(out, 0.3)


# ------------------------------------------------------------- vehicles

def engine(rng):
    """The sheep trailer's tractor-truck rumbling along."""
    d = 4.5
    n = int(d * SR)
    t = _t(d)
    f = 44 + 3 * np.sin(TAU * 0.3 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 7))
    x += 0.6 * _band(rng.standard_normal(n), 60, 500)
    return _norm(x * _env(n, 0.8, 1.0), 0.4)


def hum(rng):
    """Electric taxi: a gentle rising whine."""
    d = 3.0
    t = _t(d)
    f = 300 + 200 * np.minimum(1, t / 1.5)
    x = np.sin(TAU * np.cumsum(f) / SR) + 0.3 * np.sin(TAU * np.cumsum(2 * f) / SR)
    x += 0.2 * _band(rng.standard_normal(len(t)), 100, 800)
    return _norm(x * _env(len(t), 0.4, 0.8), 0.3)


def toot(rng):
    out = np.zeros(int(0.8 * SR))
    for st in (0.0, 0.25):
        t = _t(0.18)
        x = np.sign(np.sin(TAU * 520 * t)) * 0.4 + np.sin(TAU * 780 * t) * 0.4
        _place(out, st, _band(x, 300, 3000) * _env(len(t), 0.01, 0.03))
    return _norm(out, 0.4)


def cog(rng):
    """The rack railway: steady clack-clack of cogs and a soft electric hum."""
    d = 4.0
    n = int(d * SR)
    out = np.zeros(n)
    k = 0
    while k * 0.23 < d:
        m = int(0.04 * SR)
        x = _band(rng.standard_normal(m), 600, 4000) * np.exp(-np.arange(m) / SR * 80)
        _place(out, k * 0.23, x, 0.8 if k % 2 else 0.5)
        k += 1
    t = _t(d)
    out += 0.2 * np.sin(TAU * 120 * t) * (0.6 + 0.4 * np.sin(TAU * 0.5 * t))
    return _norm(out * _env(n, 0.3, 0.6), 0.35)


# ------------------------------------------------------------- odds & ends

def rustle(rng):
    d = 0.7
    n = int(d * SR)
    grains = (rng.random(n) < 0.04) * rng.standard_normal(n)
    x = _band(grains + 0.25 * rng.standard_normal(n), 1200, 8000) * np.sin(np.pi * _t(d) / d)
    return _norm(x, 0.4)


def pop(rng):
    d = 0.25
    t = _t(d)
    f = 300 + 900 * t / d
    return _norm(np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.1, 10), 0.5)


def sparkle(rng):
    out = np.zeros(int(1.2 * SR))
    for k in range(7):
        t = _t(0.4)
        x = np.sin(TAU * rng.uniform(2500, 5000) * t) * np.exp(-t * 14)
        _place(out, k * 0.11, x, 1 - k * 0.1)
    return _norm(out, 0.3)


def slip(rng):
    d = 0.5
    t = _t(d)
    f = 900 - 600 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.1)
    return _norm(x, 0.4)


def splosh(rng):
    """A thick, gloopy splash into melted chocolate."""
    d = 1.2
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 80, 1800) * np.exp(-t * 5) * np.minimum(1, t / 0.01)
    for _ in range(8):
        m = int(0.09 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(250, 500) * (1 + tt / 0.09)
        _place(x, rng.uniform(0.1, 0.9), np.sin(TAU * np.cumsum(f) / SR) * np.exp(-tt * 40), 0.4)
    return _norm(x, 0.6)


def bubble(rng):
    out = np.zeros(int(1.2 * SR))
    for k in range(6):
        m = int(0.08 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(200, 420) * (1 + 1.5 * tt / 0.08)
        _place(out, rng.uniform(0, 1.0), np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.08))
    return _norm(out, 0.4)


def munch(rng):
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        m = int(0.09 * SR)
        x = _band(rng.standard_normal(m), 400, 4000) * np.sin(np.pi * np.arange(m) / m)
        _place(out, k * 0.2, x, 0.8 + 0.2 * rng.random())
    return _norm(out, 0.45)


def wind(rng):
    d = 4.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 200, 900) * (0.6 + 0.4 * np.sin(TAU * 0.4 * t))
    return _norm(x * np.sin(np.pi * t / d) ** 1.5, 0.35)


EXTRA_SFX = {
    "alphorn": (alphorn, 0.75), "pfft": (pfft, 0.6), "squawk": (squawk, 0.6), "inhale": (inhale, 0.4),
    "echo": (echo, 0.45), "baa": (baa, 0.55), "cuckoo": (cuckoo, 0.6), "birds": (birds, 0.35),
    "flap": (flap, 0.4), "sniff": (sniff, 0.45), "clop": (clop, 0.4), "cowbell": (cowbell, 0.35),
    "bigbell": (bigbell, 0.5), "bell": (bell, 0.35), "ding": (ding, 0.35), "tick": (tick, 0.35),
    "engine": (engine, 0.4), "hum": (hum, 0.35), "toot": (toot, 0.4), "cog": (cog, 0.4),
    "rustle": (rustle, 0.45), "pop": (pop, 0.5), "sparkle": (sparkle, 0.35), "slip": (slip, 0.4),
    "splosh": (splosh, 0.7), "bubble": (bubble, 0.4), "munch": (munch, 0.5), "wind": (wind, 0.35),
}
