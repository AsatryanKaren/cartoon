"""Barcelona sound effects, synthesised with numpy (48 kHz mono float).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
names to (function, gain) for the film's script. The flamenco guitar is a
small Karplus-Strong plucked-string model.
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


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------ guitar

def pluck(rng, freq, dur=1.6, bright=0.6, damp=0.996):
    """Karplus-Strong string: a noise burst circulating in a delay line."""
    n = int(dur * SR)
    p = max(2, int(round(SR / freq)))
    y = np.zeros(n + p + 1)
    burst = rng.uniform(-1, 1, p)
    burst = bright * burst + (1 - bright) * np.convolve(burst, np.ones(3) / 3, "same")
    y[:p] = burst
    k = p
    while k < n + p:
        m = min(p, n + p - k)
        prev = y[k - p:k - p + m + 1]
        y[k:k + m] = damp * 0.5 * (prev[:m] + prev[1:m + 1])
        k += m
    return y[p:p + n] * _env(n, 0.001, 0.05)


# open-position chord voicings (midi notes, low to high)
CHORDS = {
    "Am": [45, 52, 57, 60, 64],
    "G": [43, 47, 50, 55, 59, 67],
    "F": [41, 48, 53, 57, 60, 65],
    "E": [40, 47, 52, 56, 59, 64],
}


def _strum(rng, chord, down=True, spread=0.012, dur=1.2, gain=1.0, bright=0.7):
    notes = CHORDS[chord] if down else CHORDS[chord][::-1]
    out = np.zeros(int((dur + 0.2) * SR))
    for k, m in enumerate(notes):
        _place(out, k * spread * rng.uniform(0.7, 1.3), pluck(rng, _midi(m), dur, bright), gain)
    return out


def strum(rng):
    """One big flamenco flourish: a rasgueado roll landing on E."""
    out = np.zeros(int(2.4 * SR))
    for k in range(4):
        _place(out, k * 0.07, _strum(rng, "Am", down=k % 2 == 0, spread=0.006, dur=0.35, gain=0.5))
    _place(out, 0.32, _strum(rng, "E", spread=0.016, dur=2.0, gain=1.0, bright=0.8))
    return _norm(out, 0.6)


def flamenco(rng):
    """A few bars of Andalusian-cadence strumming (Am G F E) with a rasgueado."""
    beat = 0.21
    bars = ["Am", "G", "F", "E", "Am", "G", "F", "E"]
    out = np.zeros(int((len(bars) * 4 * beat + 2.0) * SR))
    pattern = [(0, True, 1.0), (1, False, 0.5), (1.5, True, 0.6), (2, True, 0.9), (3, False, 0.5), (3.5, True, 0.6)]
    for b, ch in enumerate(bars):
        t0 = b * 4 * beat
        for pos, down, g in pattern:
            _place(out, t0 + pos * beat, _strum(rng, ch, down, 0.009, 0.6, g, 0.75))
        # a little melody pluck on top
        top = CHORDS[ch][-1] + (2 if b % 2 else 0)
        _place(out, t0 + 2.5 * beat, pluck(rng, _midi(top + 12), 0.5, 0.9), 0.6)
    _place(out, len(bars) * 4 * beat, _strum(rng, "E", True, 0.02, 1.8, 1.2, 0.8))
    # palmas (hand claps) on 3 and 4
    for b in range(len(bars)):
        for pos in (2, 3):
            _place(out, b * 4 * beat + pos * beat, clap(rng) * 0.6)
    return _norm(out, 0.6)


def clap(rng):
    n = int(0.12 * SR)
    x = np.zeros(n)
    for k in range(3):
        m = int(0.02 * SR)
        burst = _band(rng.standard_normal(m), 800, 6000) * np.exp(-np.arange(m) / m * 6)
        _place(x, k * 0.008, burst, 1.0 - 0.25 * k)
    tail = _band(rng.standard_normal(n), 900, 5000) * np.exp(-_t(0.12) * 40) * 0.4
    return x + tail


def castanets(rng):
    """A rolling clack-clack-clack-CLACK."""
    out = np.zeros(int(0.9 * SR))
    times = [0.0, 0.06, 0.12, 0.18, 0.36, 0.54]
    for k, tt in enumerate(times):
        d = 0.05
        t = _t(d)
        f = rng.uniform(2100, 2500)
        x = (np.sin(TAU * f * t) + 0.6 * np.sin(TAU * f * 1.7 * t)) * np.exp(-t * 120)
        x += _band(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 200) * 0.6
        _place(out, tt, x, 1.0 if k in (3, 5) else 0.6)
    return _norm(out, 0.5)


# ------------------------------------------------------------- sea

def gull(rng):
    """Seagull cry: three falling squawks."""
    out = np.zeros(int(1.2 * SR))
    for k in range(3):
        d = 0.24 - 0.03 * k
        t = _t(d)
        f = 1500 + 500 * np.exp(-t * 18) - 600 * t / d + rng.uniform(-60, 60)
        ph = TAU * np.cumsum(f) / SR
        x = sum((0.8 / h) * np.sin(h * ph) for h in range(1, 6))
        x = np.tanh(2.5 * x) * _env(len(t), 0.01, 0.06)
        x += 0.15 * _band(rng.standard_normal(len(t)), 1500, 5000) * _env(len(t), 0.01, 0.06)
        _place(out, k * 0.3, x, 1.0 - 0.15 * k)
    return _norm(out, 0.45)


def waves(rng):
    """Gentle surf: two soft washes of filtered noise."""
    d = 5.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 150, 2500)
    sw = np.maximum(0, np.sin(np.pi * t / 2.5)) ** 2
    hiss = _band(rng.standard_normal(n), 2500, 8000) * np.maximum(0, np.sin(np.pi * (t - 0.6) / 2.5)) ** 4
    return _norm((x * (0.25 + sw) + 0.5 * hiss) * _env(n, 0.5, 1.0), 0.4)


def bigwave(rng):
    """A big wave rolling in and crashing."""
    d = 3.0
    n = int(d * SR)
    t = _t(d)
    rise = np.minimum(1, t / 1.0) ** 2
    crash = np.exp(-np.maximum(0, t - 1.0) * 2.2) * (t >= 1.0)
    x = _band(rng.standard_normal(n), 80, 4000) * (0.4 * rise * (t < 1.0) + crash)
    x += _band(rng.standard_normal(n), 3000, 9000) * crash * 0.5
    return _norm(x * _env(n, 0.05, 0.4), 0.6)


def horn(rng):
    """Ship's horn: deep, long, a bit wobbly."""
    d = 2.2
    t = _t(d)
    f = 110 * (1 + 0.004 * np.sin(TAU * 5 * t))
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 10))
    x += 0.7 * sum((1 / h) * np.sin(h * ph * 1.26) for h in range(1, 6))
    x = _band(x, 60, 1800)
    return _norm(x * _env(len(t), 0.15, 0.5), 0.55)


def flap(rng):
    """Wing flaps: soft whumps."""
    out = np.zeros(int(1.0 * SR))
    for k in range(5):
        m = int(0.1 * SR)
        x = _band(rng.standard_normal(m), 150, 1500) * np.sin(np.pi * np.arange(m) / m) ** 2
        _place(out, k * 0.16, x, 1.0 - 0.12 * k)
    return _norm(out, 0.45)


# ------------------------------------------------------------- kitchen / misc

def crash(rng):
    """A ceramic bowl smashing: a thud plus a spray of bright shards."""
    d = 1.6
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 300, 6000) * np.exp(-t * 18) * np.minimum(1, t / 0.002)
    x += np.sin(TAU * 140 * t) * np.exp(-t * 25) * 0.6
    for _ in range(26):
        tt = rng.uniform(0.0, 0.9) ** 1.6
        m = int(0.12 * SR)
        tk = np.arange(m) / SR
        f = rng.uniform(2500, 7000)
        ping = (np.sin(TAU * f * tk) + 0.5 * np.sin(TAU * f * 1.63 * tk)) * np.exp(-tk * rng.uniform(30, 70))
        _place(x, tt, ping, rng.uniform(0.15, 0.4) * (1 - tt))
    return _norm(x, 0.7)


def munch(rng):
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        m = int(0.09 * SR)
        x = _band(rng.standard_normal(m), 400, 4000) * np.sin(np.pi * np.arange(m) / m)
        _place(out, k * 0.2, x, 0.8 + 0.2 * rng.random())
    return _norm(out, 0.45)


def gulp(rng):
    d = 0.35
    t = _t(d)
    f = 300 + 500 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
    return _norm(x, 0.45)


def boing(rng):
    """Cartoon 'spicy!' boing."""
    d = 0.8
    t = _t(d)
    f = 220 + 340 * np.exp(-t * 4) * (1 + 0.3 * np.sin(TAU * 14 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    return _norm(x, 0.5)


def steam(rng):
    """Kettle-whistle steam out of the ears."""
    d = 1.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 3000, 9000) * 0.6
    x += 0.5 * np.sin(TAU * (1900 + 300 * t) * t)
    return _norm(x * _env(len(t), 0.08, 0.3), 0.4)


def ding(rng):
    """A tiny magic twinkle (the statue's wink)."""
    t = _t(0.9)
    x = sum(np.sin(TAU * f * t) * np.exp(-t * 6) for f in (1760, 2637))
    return _norm(x * np.minimum(1, t / 0.003), 0.4)


def sparkle(rng):
    out = np.zeros(int(1.0 * SR))
    for k in range(6):
        t = _t(0.4)
        f = 2000 + 400 * k + rng.uniform(-50, 50)
        _place(out, k * 0.07, np.sin(TAU * f * t) * np.exp(-t * 12), 0.6)
    return _norm(out, 0.35)


def bells(rng):
    """Church bells far away."""
    d = 3.6
    out = np.zeros(int(d * SR))
    for k, f in enumerate((392, 330, 294, 262)):
        t = _t(2.4)
        x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 1.6), (2.0, 0.5, 2.4), (2.76, 0.35, 3.5), (5.4, 0.15, 6)))
        _place(out, k * 0.45, x)
    return _norm(out, 0.4)


def clank(rng):
    """Construction crane: metal clank and a chain rattle."""
    d = 1.0
    t = _t(d)
    x = (np.sin(TAU * 310 * t) + 0.6 * np.sin(TAU * 487 * t) + 0.4 * np.sin(TAU * 1210 * t)) * np.exp(-t * 7)
    for k in range(6):
        m = int(0.03 * SR)
        _place(x, 0.25 + k * 0.07, _band(rng.standard_normal(m), 1500, 7000) * np.exp(-np.arange(m) / m * 4), 0.4)
    return _norm(x, 0.45)


EXTRA_SFX = {
    "strum": (strum, 0.6), "flamenco": (flamenco, 0.55), "castanets": (castanets, 0.45),
    "gull": (gull, 0.4), "waves": (waves, 0.4), "bigwave": (bigwave, 0.7), "horn": (horn, 0.55),
    "flap": (flap, 0.45), "crash": (crash, 0.8), "munch": (munch, 0.5), "gulp": (gulp, 0.45),
    "boing": (boing, 0.45), "steam": (steam, 0.35), "ding": (ding, 0.4), "sparkle": (sparkle, 0.4),
    "bells": (bells, 0.4), "clank": (clank, 0.4),
}
