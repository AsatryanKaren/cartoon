"""Amsterdam sound effects, synthesised with numpy (48 kHz mono float).

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


def bell(rng):
    """Bicycle bell: a quick double 'tring-tring' of a bright metal dome."""
    out = np.zeros(int(1.1 * SR))
    f0 = rng.uniform(1850, 2150)
    for k, start in enumerate((0.0, 0.16)):
        t = _t(0.9)
        x = sum(g * np.sin(TAU * f0 * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 5), (1.34, 0.45, 7), (2.71, 0.35, 10), (4.1, 0.15, 16)))
        x *= 1 + 0.4 * np.sin(TAU * 32 * t) * np.exp(-t * 6)      # the striker rattle
        click = rng.standard_normal(len(t)) * np.exp(-t * 300) * 0.4
        _place(out, start, (x + click) * np.minimum(1, t / 0.001))
    return _norm(out, 0.5)


def knock(rng):
    """A stork's beak tapping on glass: three sharp tocks."""
    out = np.zeros(int(0.8 * SR))
    for k in range(3):
        t = _t(0.12)
        x = (np.sin(TAU * 1250 * t) + 0.6 * np.sin(TAU * 2900 * t)) * np.exp(-t * 70)
        x += _band(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 200) * 0.5
        _place(out, k * 0.2, x, 1.0 - 0.15 * k)
    return _norm(out, 0.55)


def creak(rng):
    """Old wood creaking (window hinge, windmill)."""
    d = 1.0
    t = _t(d)
    f = 180 + 70 * np.sin(TAU * 0.8 * t) + 30 * rng.standard_normal()
    ph = TAU * np.cumsum(f) / SR
    pulses = (np.sin(TAU * 38 * t) > 0.6).astype(float)
    x = np.sign(np.sin(ph)) * pulses
    x = _band(x, 150, 3500) * np.sin(np.pi * t / d) ** 1.5
    return _norm(x, 0.35)


def clatter(rng):
    """A stork clattering its bill: fast wooden rattle."""
    d = 0.9
    n = int(d * SR)
    out = np.zeros(n)
    k, tt = 0, 0.0
    while tt < d - 0.05:
        m = int(0.025 * SR)
        click = _band(rng.standard_normal(m), 700, 4500) * _env(m, 0.001, 0.015, 120)
        _place(out, tt, click, 1.0 - 0.6 * tt / d)
        tt += 0.045 + 0.01 * rng.random()
    return _norm(out, 0.5)


def flap(rng):
    """Big wing beat: a soft low whoosh."""
    d = 0.55
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 1400) * np.sin(np.pi * t / d) ** 2
    x += _band(rng.standard_normal(len(t)), 60, 200) * np.sin(np.pi * t / d) ** 4 * 0.8
    return _norm(x, 0.45)


def gull(rng):
    """Seagull cry: two falling squawks."""
    out = np.zeros(int(1.0 * SR))
    for start, dur in ((0.0, 0.32), (0.4, 0.42)):
        t = _t(dur)
        u = t / dur
        f = 1500 + 500 * np.sin(np.pi * np.minimum(1, u * 1.5)) - 500 * u
        ph = TAU * np.cumsum(f) / SR
        x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6)) * _env(len(t), 0.02, 0.1)
        x += _band(rng.standard_normal(len(t)), 2000, 6000) * 0.15 * _env(len(t), 0.02, 0.1)
        _place(out, start, x)
    return _norm(out, 0.35)


def thud(rng):
    """Soft landing on a wooden deck."""
    d = 0.4
    t = _t(d)
    x = np.sin(TAU * (90 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18)
    x += _band(rng.standard_normal(len(t)), 200, 2000) * np.exp(-t * 50) * 0.5
    return _norm(x, 0.55)


def organ(rng):
    """A Dutch street organ (draaiorgel): a little oom-pah-pah waltz in C, about 9 s."""
    beat = 0.34
    mel = [(76, 1), (79, 1), (84, 1), (83, 2), (79, 1), (77, 1), (81, 1), (84, 1), (83, 2), (79, 1),
           (76, 1), (79, 1), (84, 1), (86, 1), (84, 1), (83, 1), (81, 1), (79, 1), (77, 1), (76, 3)]
    chords = [(48, (0, 4, 7)), (43, (0, 4, 10)), (43, (0, 4, 10)), (48, (0, 4, 7)),
              (48, (0, 4, 7)), (41, (0, 4, 7)), (43, (0, 4, 10)), (48, (0, 4, 7))]
    total = sum(b for _, b in mel) * beat + 1.0
    out = np.zeros(int(total * SR))

    def pipe(note, dur, g):
        f = 440 * 2 ** ((note - 69) / 12)
        t = _t(dur)
        vib = 1 + 0.004 * np.sin(TAU * 6 * t)
        ph = TAU * np.cumsum(f * vib) / SR
        x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.2 * np.sin(4 * ph)
        x += 0.15 * np.sign(np.sin(ph))
        return x * _env(len(t), 0.015, 0.05) * g

    tt = 0.0
    for note, b in mel:
        _place(out, tt, pipe(note, b * beat * 0.92, 0.5))
        _place(out, tt, pipe(note - 12, b * beat * 0.92, 0.18))
        tt += b * beat
    bars = int(np.ceil(tt / (3 * beat)))
    for k in range(bars):
        root, q = chords[k % len(chords)]
        t0 = k * 3 * beat
        _place(out, t0, pipe(root, beat * 0.8, 0.45))
        for j in (1, 2):
            for iv in q:
                _place(out, t0 + j * beat, pipe(root + 12 + iv, beat * 0.5, 0.12))
        # little drum of the organ
        m = int(0.08 * SR)
        _place(out, t0, _band(rng.standard_normal(m), 60, 300) * _env(m, 0.002, 0.06, 20), 0.6)
    fade = np.ones(len(out))
    fade[-SR:] = np.linspace(1, 0, SR)
    return _norm(out * fade, 0.5)


def moo(rng):
    """A friendly cow 'moo'."""
    d = 1.1
    t = _t(d)
    u = t / d
    f = 150 + 40 * np.sin(np.pi * np.minimum(1, u * 1.2)) - 20 * u
    ph = TAU * np.cumsum(f) / SR
    open_ = np.sin(np.pi * np.minimum(1, u * 1.1)) ** 0.7
    x = sum((1 / h) * (0.4 + 0.6 * open_ * (h > 2)) * np.sin(h * ph) for h in range(1, 10))
    x = _band(x, 80, 2500) * _env(len(t), 0.08, 0.3)
    return _norm(x, 0.5)


def munch(rng):
    """Crunchy happy munching."""
    out = np.zeros(int(0.8 * SR))
    for k in range(4):
        m = int(0.07 * SR)
        x = _band(rng.standard_normal(m), 600, 5000) * _env(m, 0.003, 0.04, 30)
        _place(out, k * 0.17, x, 0.8 + 0.2 * rng.random())
    return _norm(out, 0.45)


def rumble(rng):
    """A giant cheese wheel rolling over cobbles: low thumping roll."""
    d = 2.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 40, 260) * 1.2
    k, tt = 0, 0.0
    while tt < d - 0.1:
        m = int(0.09 * SR)
        tm = np.arange(m) / SR
        bump = np.sin(TAU * (70 + 40 * np.exp(-tm * 40)) * tm) * np.exp(-tm * 30)
        _place(x, tt, bump, 1.6)
        tt += 0.14 + 0.04 * rng.random()
    return _norm(x * _env(n, 0.1, 0.3), 0.55)


def clatter_clogs(rng):
    """A pile of wooden clogs tumbling down: many hollow wooden knocks."""
    d = 1.8
    out = np.zeros(int(d * SR))
    big = np.sin(TAU * (80 + 50 * np.exp(-_t(0.5) * 20)) * _t(0.5)) * np.exp(-_t(0.5) * 9)
    _place(out, 0.0, big, 1.2)
    for _ in range(22):
        tt = rng.uniform(0.0, 1.4) ** 1.3
        f = rng.uniform(500, 1100)
        m = int(0.12 * SR)
        tm = np.arange(m) / SR
        x = (np.sin(TAU * f * tm) + 0.5 * np.sin(TAU * f * 2.3 * tm)) * np.exp(-tm * 45)
        _place(out, tt, x, rng.uniform(0.3, 0.8))
    return _norm(out, 0.6)


def squeak(rng):
    """A squeaky wobbling bicycle: rusty chain squeak."""
    d = 0.5
    t = _t(d)
    f = 1700 + 500 * np.sin(np.pi * t / d) + rng.uniform(-150, 150)
    ph = TAU * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.4 * np.sin(2 * ph)) * (0.6 + 0.4 * np.sin(TAU * 25 * t)) * _env(len(t), 0.03, 0.12)
    return _norm(x, 0.3)


EXTRA_SFX = {
    "bell": (bell, 0.45), "knock": (knock, 0.55), "creak": (creak, 0.35), "clatter": (clatter, 0.45),
    "flap": (flap, 0.45), "gull": (gull, 0.35), "thud": (thud, 0.5), "organ": (organ, 0.38),
    "moo": (moo, 0.45), "munch": (munch, 0.45), "rumble": (rumble, 0.6), "clatter_clogs": (clatter_clogs, 0.6),
    "squeak": (squeak, 0.3),
}
