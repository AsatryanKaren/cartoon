"""Lisbon sound effects and music pieces, synthesised with numpy (48 kHz mono float).

The Portuguese guitar (a bright, pear-shaped 12-string with doubled steel
courses) is a Karplus-Strong string played in pairs, slightly detuned. The
fado and the festival tune ("arraial") are rendered here as long "sound
effects" placed on the moments where they play.
EXTRA_SFX maps names to (function(rng), gain).
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
    return np.maximum(e, 0)


def _band(x, lo, hi):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _place(buf, start, x, gain=1.0):
    i = int(start * SR)
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += gain * x[:j - i]


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ============================================================ instruments

def ks(rng, freq, dur=1.4, bright=0.8, damp=0.997):
    """Karplus-Strong plucked string."""
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


def pguitar(rng, m, dur=1.2, gain=1.0):
    """Portuguese guitar note: a doubled steel course (unison/octave pair, slightly detuned)."""
    f = _midi(m)
    x = ks(rng, f, dur, 0.9, 0.9975) + 0.7 * ks(rng, f * 1.003, dur, 0.95, 0.997)
    if m < 64:
        x += 0.35 * ks(rng, f * 2, dur, 0.95, 0.996)
    return x * gain


def tremolo(rng, m, dur, rate=11.0):
    """The fado guitar's trademark trill of fast repeated notes on one pitch."""
    out = np.zeros(int((dur + 0.6) * SR))
    k = 0
    while k / rate < dur:
        _place(out, k / rate, pguitar(rng, m, 0.35), 0.55 + 0.25 * (k % 2))
        k += 1
    return out


def classical(rng, m, dur=1.2):
    """Soft nylon 'viola' (classical guitar) for the chords."""
    return ks(rng, _midi(m), dur, 0.45, 0.996)


def accordion(m, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = _midi(m)
    x = 0
    for det in (1.0, 1.004):
        ph = TAU * f * det * t
        x = x + sum((0.9 / h) * np.sin(h * ph) for h in range(1, 7))
    return x * _env(n, 0.03, 0.08) * (1 + 0.05 * np.sin(TAU * 5 * t))


# ============================================================ pieces

def guitar_flourish(rng):
    """A short Portuguese-guitar run ending on a ringing chord (A minor)."""
    out = np.zeros(int(3.2 * SR))
    run = [69, 71, 72, 74, 76, 74, 72, 71, 69]
    for k, m in enumerate(run):
        _place(out, k * 0.11, pguitar(rng, m, 0.6), 0.6)
    for k, m in enumerate((57, 64, 69, 72, 76)):
        _place(out, 1.05 + k * 0.03, pguitar(rng, m, 2.0), 0.55)
    return _norm(out, 0.55)


# fado in A minor: (beat, midi, beats); tremolo on long notes
_FADO_MEL = [
    (0, 76, 1), (1, 77, 0.5), (1.5, 76, 0.5), (2, 74, 1), (3, 72, 1),
    (4, 71, 2), (6, 72, 1), (7, 74, 1),
    (8, 76, 3), (11, 74, 1),
    (12, 72, 1), (13, 71, 1), (14, 69, 2),
    (16, 72, 1), (17, 74, 0.5), (17.5, 72, 0.5), (18, 71, 1), (19, 69, 1),
    (20, 68, 2), (22, 69, 1), (23, 71, 1),
    (24, 72, 1), (25, 71, 1), (26, 69, 1), (27, 68, 1),
    (28, 69, 4),
]
_FADO_CH = ["Am", "E7", "Am", "Am", "Dm", "E7", "E7", "Am"]
_VOICING = {"Am": (45, 52, 57, 60, 64), "E7": (40, 47, 50, 56, 59), "Dm": (50, 57, 62, 65),
            "G": (43, 50, 55, 59), "C": (48, 52, 55, 60, 64), "D": (50, 57, 62, 66), "D7": (50, 57, 60, 66)}


def fado_track(rng, beat=0.62, loops=1, tail=2.5):
    bars = 8
    total = loops * bars * 4 * beat
    out = np.zeros(int((total + tail + 1) * SR))
    for L in range(loops):
        t0 = L * bars * 4 * beat
        # viola: bass on 1 and 3, chord on 2 and 4
        for b, ch in enumerate(_FADO_CH):
            v = _VOICING[ch]
            for bt in range(4):
                tt = t0 + (b * 4 + bt) * beat
                if bt in (0, 2):
                    _place(out, tt, classical(rng, v[0] - (0 if bt == 0 else -7 if ch != "E7" else -7), 1.0), 0.5)
                else:
                    for k, m in enumerate(v[1:]):
                        _place(out, tt + k * 0.008, classical(rng, m, 0.5), 0.16)
        for (bt, m, d) in _FADO_MEL:
            st = t0 + bt * beat
            if d >= 2:
                _place(out, st, tremolo(rng, m, d * beat * 0.92), 0.5)
            else:
                _place(out, st, pguitar(rng, m, d * beat + 0.5), 0.6)
    # final ringing chord
    for k, m in enumerate((45, 57, 64, 69, 72, 76)):
        _place(out, loops * bars * 4 * beat + k * 0.04, pguitar(rng, m, tail + 0.5), 0.5)
    n = len(out)
    out *= _env(n, 0.05, 1.0)
    return _norm(out, 0.6)


def fado(rng):
    return fado_track(rng, beat=0.6, loops=1, tail=2.0)


# festival tune ("marcha popular" feel) in G major, 2/4 with accordion and drum
_ARR_MEL = [
    (0, 74, 0.5), (0.5, 76, 0.5), (1, 78, 1), (2, 79, 0.5), (2.5, 78, 0.5), (3, 76, 1),
    (4, 74, 0.5), (4.5, 76, 0.5), (5, 74, 0.5), (5.5, 72, 0.5), (6, 71, 2),
    (8, 72, 0.5), (8.5, 74, 0.5), (9, 76, 1), (10, 78, 0.5), (10.5, 76, 0.5), (11, 74, 1),
    (12, 72, 0.5), (12.5, 71, 0.5), (13, 69, 0.5), (13.5, 72, 0.5), (14, 71, 2),
]
_ARR_CH = ["G", "D7", "G", "G", "C", "G", "D7", "G"]


def arraial_track(rng, dur, beat=0.27):
    out = np.zeros(int((dur + 2) * SR))
    bars = 8
    loop = bars * 2 * beat * 2      # 8 bars of 4 beats (fast 2/4 pairs)
    nloops = int(np.ceil(dur / loop))
    for L in range(nloops):
        t0 = L * loop
        for b, ch in enumerate(_ARR_CH):
            v = _VOICING[ch]
            for bt in range(4):
                tt = t0 + (b * 4 + bt) * beat
                if bt % 2 == 0:
                    _place(out, tt, classical(rng, v[0] - 12, 0.5), 0.5)
                    n = int(0.2 * SR)
                    tk = np.arange(n) / SR
                    kick = np.sin(TAU * np.cumsum(60 + 80 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 16)
                    _place(out, tt, kick, 0.35)
                else:
                    for m in v[1:]:
                        _place(out, tt, accordion(m, beat * 0.6), 0.04)
                    sn = _band(rng.standard_normal(int(0.12 * SR)), 1500, 8000) * _env(int(0.12 * SR), 0.002, 0.08,
                                                                                        25)
                    _place(out, tt, sn, 0.12)
        for (bt, m, d) in _ARR_MEL:
            for rep in (0, 16):
                pass
            _place(out, t0 + bt * beat * 2, accordion(m, d * beat * 2 * 0.9), 0.13)
            _place(out, t0 + bt * beat * 2, pguitar(rng, m, 0.5), 0.12)
    out = out[:int(dur * SR)]
    out *= _env(len(out), 0.3, 2.0)
    return _norm(out, 0.55)


def make_arraial(dur):
    return lambda rng: arraial_track(rng, dur)


# ============================================================ effects

def sniff(rng):
    out = np.zeros(int(0.5 * SR))
    for k in range(2):
        n = int(0.12 * SR)
        x = _band(rng.standard_normal(n), 1500, 7000) * _env(n, 0.03, 0.06)
        _place(out, k * 0.18, x)
    return _norm(out, 0.4)


def sizzle(rng):
    d = 2.6
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 2500, 12000)
    crackle = np.zeros(n)
    for _ in range(40):
        i = rng.integers(0, n - 400)
        crackle[i:i + 200] += rng.uniform(0.5, 1.5) * np.exp(-np.arange(200) / 30) * rng.choice([-1, 1])
    x = x * (0.6 + 0.4 * np.sin(TAU * 0.7 * _t(d))) + 3 * crackle
    return _norm(x * _env(n, 0.3, 0.6), 0.35)


def scooter(rng):
    """Little two-stroke scooter: a buzzy putt-putt."""
    d = 2.5
    t = _t(d)
    f = 34 + 6 * np.sin(TAU * 0.4 * t)
    ph = TAU * np.cumsum(f) / SR
    pulses = (np.sin(ph) > 0.6).astype(float)
    body = _band(pulses + 0.3 * rng.standard_normal(len(t)), 60, 1800)
    buzz = np.sign(np.sin(ph * 4)) * 0.15
    x = (body + buzz) * _env(len(t), 0.2, 0.6)
    return _norm(x, 0.45)


def scooter_soft(rng):
    return scooter(rng) * 0.5


def beep(rng):
    out = np.zeros(int(0.6 * SR))
    for k in range(2):
        d = 0.13
        t = _t(d)
        x = np.sign(np.sin(TAU * 620 * t)) * 0.4 + np.sin(TAU * 930 * t) * 0.4
        _place(out, k * 0.2, _band(x, 300, 4000) * _env(len(t), 0.005, 0.02))
    return _norm(out, 0.4)


def tram_bell(rng):
    """Ding-ding! The tram's bell."""
    out = np.zeros(int(1.6 * SR))
    for k in range(2):
        t = _t(1.2)
        x = sum(g * np.sin(TAU * f * t) * np.exp(-t * dk)
                for f, g, dk in ((1320, 1.0, 4), (3150, 0.5, 7), (4870, 0.25, 11), (2210, 0.3, 6)))
        _place(out, k * 0.28, x * _env(len(t), 0.001, 0.1))
    return _norm(out, 0.5)


def tram_run(rng):
    """Rumbling wheels with clickety-clack rail joints and a squeal."""
    d = 3.2
    n = int(d * SR)
    t = _t(d)
    rumble = _band(rng.standard_normal(n), 50, 400) * 0.6
    x = rumble * _env(n, 0.3, 0.6)
    for k in range(int(d / 0.42)):
        for dd in (0.0, 0.09):
            m = int(0.05 * SR)
            click = _band(rng.standard_normal(m), 300, 3000) * np.exp(-np.arange(m) / m * 8)
            _place(x, k * 0.42 + dd, click, 0.8)
    sq = np.sin(TAU * (2600 + 80 * np.sin(TAU * 3 * t)) * t) * 0.06 * np.exp(-((t - 2.0) / 0.3) ** 2)
    return _norm(x + sq, 0.45)


def brakes(rng):
    d = 1.0
    t = _t(d)
    x = np.sin(TAU * (2900 - 300 * t) * t) * 0.5 + _band(rng.standard_normal(len(t)), 2000, 6000) * 0.2
    return _norm(x * _env(len(t), 0.05, 0.4), 0.3)


def munch(rng):
    out = np.zeros(int(0.5 * SR))
    for k in range(3):
        n = int(0.07 * SR)
        x = _band(rng.standard_normal(n), 400, 3500) * _env(n, 0.005, 0.04)
        _place(out, k * 0.13, x, 1 - 0.2 * k)
    return _norm(out, 0.5)


def gulp(rng):
    d = 0.3
    t = _t(d)
    f = 300 - 200 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.01, 0.1)
    return _norm(x, 0.5)


def burp(rng):
    d = 0.6
    t = _t(d)
    f = 95 + 15 * np.sin(TAU * 7 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 10)) * (1 + 0.3 * rng.standard_normal(len(t)))
    return _norm(_band(x, 60, 2000) * _env(len(t), 0.03, 0.2), 0.5)


def sneeze(rng):
    """Ah... ah... CHOO!"""
    out = np.zeros(int(1.6 * SR))
    for k, (st, f) in enumerate(((0.0, 380), (0.4, 430))):
        d = 0.28
        t = _t(d)
        ph = TAU * np.cumsum(f + 60 * t / d) / SR
        x = sum((0.7 / h) * np.sin(h * ph) for h in range(1, 6)) + 0.2 * rng.standard_normal(len(t))
        _place(out, st, _band(x, 150, 3000) * _env(len(t), 0.05, 0.1), 0.5)
    n = int(0.35 * SR)
    choo = _band(rng.standard_normal(n), 1200, 9000) * _env(n, 0.005, 0.25, 6)
    _place(out, 0.85, choo, 1.2)
    return _norm(out, 0.6)


def poof(rng):
    n = int(0.8 * SR)
    x = _band(rng.standard_normal(n), 100, 1500) * _env(n, 0.005, 0.5, 5)
    return _norm(x, 0.45)


def snore(rng):
    d = 1.6
    t = _t(d)
    inhale = _band(rng.standard_normal(len(t)), 80, 900) * (0.5 + 0.5 * np.sin(TAU * 38 * t))
    shape = np.where(t < 0.9, np.sin(np.pi * t / 0.9), 0) + np.where(t >= 0.9, 0.3 * np.sin(np.pi * (t - 0.9) / 0.7), 0)
    return _norm(inhale * np.maximum(shape, 0), 0.35)


def waves(rng):
    d = 5.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 150, 2500)
    sw = np.maximum(0, np.sin(np.pi * t / 2.5)) ** 2
    return _norm(x * sw * _env(n, 0.3, 0.8), 0.3)


def gull(rng):
    out = np.zeros(int(1.2 * SR))
    for k in range(3):
        d = 0.24 - 0.03 * k
        t = _t(d)
        f = 1500 + 500 * np.exp(-t * 18) - 600 * t / d + rng.uniform(-60, 60)
        ph = TAU * np.cumsum(f) / SR
        x = sum((0.8 / h) * np.sin(h * ph) for h in range(1, 6))
        x = np.tanh(2.5 * x) * _env(len(t), 0.01, 0.06)
        _place(out, k * 0.3, x, 1.0 - 0.15 * k)
    return _norm(out, 0.4)


def shop_bell(rng):
    t = _t(1.0)
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * dk) for f, g, dk in ((2400, 1, 5), (3700, 0.5, 8), (5600, 0.3, 12)))
    out = np.zeros(int(1.3 * SR))
    _place(out, 0, x)
    _place(out, 0.12, x, 0.6)
    return _norm(out, 0.4)


def bell_jingle(rng):
    """Luna's little collar bell."""
    out = np.zeros(int(0.9 * SR))
    for k in range(4):
        t = _t(0.5)
        f = 3300 + rng.uniform(-100, 100)
        x = (np.sin(TAU * f * t) + 0.5 * np.sin(TAU * f * 2.4 * t)) * np.exp(-t * 10)
        _place(out, k * 0.11 + rng.uniform(0, 0.03), x, 1 - 0.15 * k)
    return _norm(out, 0.35)


def bridge_hum(rng):
    d = 3.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 80, 600) * (0.7 + 0.3 * np.sin(TAU * 9 * t))
    x += 0.2 * np.sin(TAU * 110 * t)
    return _norm(x * _env(n, 0.8, 1.0), 0.3)


def peacock(rng):
    """A loud peacock 'may-AWW!'"""
    out = np.zeros(int(1.2 * SR))
    for k in range(2):
        d = 0.42
        t = _t(d)
        f = 700 + 500 * np.sin(np.pi * t / d) - 100 * k
        ph = TAU * np.cumsum(f) / SR
        x = np.tanh(3 * sum((1 / h) * np.sin(h * ph) for h in range(1, 6)))
        _place(out, k * 0.5, _band(x, 400, 5000) * _env(len(t), 0.02, 0.1), 1 - 0.3 * k)
    return _norm(out, 0.4)


def fan(rng):
    """The peacock's tail opening: a rustling shimmer."""
    d = 1.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 2000, 9000) * np.sin(np.pi * t / d) ** 2
    x += 0.2 * sum(np.sin(TAU * f * t) * np.exp(-((t - 0.3 - 0.12 * k) / 0.05) ** 2)
                   for k, f in enumerate((2093, 2637, 3136, 4186)))
    return _norm(x, 0.35)


def flap(rng):
    out = np.zeros(int(0.9 * SR))
    for k in range(4):
        n = int(0.12 * SR)
        x = _band(rng.standard_normal(n), 150, 1500) * _env(n, 0.01, 0.08)
        _place(out, k * 0.18, x)
    return _norm(out, 0.4)


def steps(rng):
    """Little padding paws on cobbles."""
    out = np.zeros(int(1.6 * SR))
    for k in range(8):
        n = int(0.04 * SR)
        x = _band(rng.standard_normal(n), 200, 1500) * _env(n, 0.002, 0.03)
        _place(out, k * 0.19, x, 0.6 + 0.3 * (k % 2))
    return _norm(out, 0.3)


def lift_ding(rng):
    t = _t(1.4)
    x = np.sin(TAU * 1046 * t) * np.exp(-t * 3) + 0.4 * np.sin(TAU * 2093 * t) * np.exp(-t * 5)
    out = np.zeros(int(1.8 * SR))
    _place(out, 0, x)
    t2 = _t(1.4)
    _place(out, 0.35, np.sin(TAU * 830 * t2) * np.exp(-t2 * 3), 0.9)
    return _norm(out, 0.4)


def lift_hum(rng):
    d = 4.0
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 60, 300) + 0.3 * np.sin(TAU * 98 * t) + 0.1 * np.sin(TAU * 196 * t)
    for k in range(4):
        m = int(0.3 * SR)
        _place(x, 0.5 + k * 0.9, _band(rng.standard_normal(m), 800, 3000) * _env(m, 0.05, 0.2) * 0.4)
    return _norm(x * _env(n, 0.4, 0.8), 0.3)


def cheer(rng):
    d = 2.6
    n = int(d * SR)
    t = _t(d)
    x = _band(rng.standard_normal(n), 300, 4000) * _env(n, 0.15, 1.2)
    for _ in range(14):
        st = rng.uniform(0, 1.6)
        dd = rng.uniform(0.25, 0.5)
        tt = _t(dd)
        f = rng.uniform(300, 800) * (1 + 0.3 * np.sin(np.pi * tt / dd))
        v = np.tanh(2 * sum((1 / h) * np.sin(h * TAU * np.cumsum(f) / SR) for h in range(1, 4)))
        _place(x, st, v * _env(len(tt), 0.03, 0.1), 0.15)
    return _norm(x, 0.45)


def firework(rng):
    d = 2.0
    n = int(d * SR)
    t = _t(d)
    whistle = np.sin(TAU * np.cumsum(1200 + 900 * t / 0.6) / SR) * (t < 0.6) * 0.15
    out = whistle * _env(n, 0.05, 0.1)
    m = int(1.3 * SR)
    boom = _band(rng.standard_normal(m), 40, 800) * _env(m, 0.003, 0.9, 4)
    _place(out, 0.62, boom, 1.0)
    for _ in range(25):
        k = int(0.05 * SR)
        _place(out, 0.75 + rng.uniform(0, 0.9), _band(rng.standard_normal(k), 3000, 9000) * np.exp(-np.arange(k) / k * 9),
               0.25)
    return _norm(out, 0.5)


EXTRA_SFX = {
    "guitar_flourish": (guitar_flourish, 0.55),
    "fado": (fado, 0.75),
    "arraial": (make_arraial(16.0), 0.55),
    "sniff": (sniff, 0.45), "sizzle": (sizzle, 0.4), "scooter": (scooter, 0.4), "scooter_soft": (scooter_soft, 0.3),
    "beep": (beep, 0.35), "tram_bell": (tram_bell, 0.45), "tram_run": (tram_run, 0.4), "brakes": (brakes, 0.3),
    "munch": (munch, 0.5), "gulp": (gulp, 0.5), "burp": (burp, 0.5), "sneeze": (sneeze, 0.65), "poof": (poof, 0.45),
    "snore": (snore, 0.45), "waves": (waves, 0.4), "gull": (gull, 0.35), "shop_bell": (shop_bell, 0.35),
    "bell_jingle": (bell_jingle, 0.4), "bridge_hum": (bridge_hum, 0.3), "peacock": (peacock, 0.4),
    "fan": (fan, 0.35), "flap": (flap, 0.4), "steps": (steps, 0.35), "lift_ding": (lift_ding, 0.35),
    "lift_hum": (lift_hum, 0.3), "cheer": (cheer, 0.5), "firework": (firework, 0.5),
}
