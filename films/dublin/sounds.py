"""Dublin sound effects and Irish folk music, synthesised with numpy (48 kHz mono float).

The film's music moods are 4/4 band loops, so the real folk tunes -- the
traditional jig "The Irish Washerwoman" (public domain) on fiddle, tin whistle,
bodhran drum and plucked guitar -- are rendered here as long "sound effects"
placed on the pub and busking moments. EXTRA_SFX maps names to (function(rng), gain).
"""
import numpy as np

from films.vienna.sounds import violin, pluck, piano

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

def fiddle(f, d):
    """A brighter, quicker folk fiddle than the concert violin: little vibrato, bowed edge."""
    n = int(d * SR)
    t = np.arange(n) / SR
    ph = TAU * np.cumsum(f * (1 + 0.002 * np.sin(TAU * 6.5 * t))) / SR
    x = sum((1.0 / h) * (1.0 if h % 2 else 0.7) * np.sin(h * ph) for h in range(1, 11))
    return x * _env(n, 0.015, min(0.06, d * 0.3))


def whistle(f, d, rng=None):
    """Tin whistle: nearly pure tone, a touch of breath."""
    n = int(d * SR)
    t = np.arange(n) / SR
    ph = TAU * np.cumsum(f * (1 + 0.003 * np.sin(TAU * 5.0 * t) * np.minimum(1, t / 0.2))) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    rng = rng or np.random.default_rng(1)
    breath = _band(rng.standard_normal(n), 2000, 7000) * 0.05
    return (x + breath) * _env(n, 0.02, min(0.05, d * 0.3))


def bodhran(strong=True, rng=None):
    rng = rng or np.random.default_rng(2)
    t = _t(0.3)
    f = 70 + 60 * np.exp(-t * 30)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * (11 if strong else 18))
    x += _band(rng.standard_normal(len(t)), 200, 2000) * np.exp(-t * 60) * 0.3
    return x * (1.0 if strong else 0.45)


# ============================================================ the jig
# "The Irish Washerwoman" (traditional), 6/8 in G: eighth notes as midi numbers, 0 = hold
_PICKUP = [74, 72]
_A = [
    [71, 67, 67, 62, 67, 67], [71, 67, 71, 74, 72, 71], [72, 69, 69, 64, 69, 69], [72, 71, 72, 76, 74, 72],
    [71, 67, 67, 62, 67, 67], [71, 67, 71, 74, 72, 71], [72, 71, 72, 69, 74, 72], [71, 67, 67, 67, 0, 0],
]
_B = [
    [71, 74, 74, 79, 74, 74], [71, 74, 74, 79, 74, 74], [72, 76, 76, 79, 76, 76], [72, 76, 76, 79, 76, 76],
    [71, 74, 74, 79, 74, 74], [71, 74, 74, 79, 74, 74], [72, 71, 72, 69, 74, 72], [71, 67, 67, 67, 0, 0],
]
_CH_A = [(43, (55, 59, 62)), (43, (55, 59, 62)), (38, (54, 57, 62)), (38, (54, 57, 62)),
         (43, (55, 59, 62)), (43, (55, 59, 62)), (38, (54, 57, 62)), (43, (55, 59, 62))]
_CH_B = [(43, (55, 59, 62)), (43, (55, 59, 62)), (36, (55, 60, 64)), (36, (55, 60, 64)),
         (43, (55, 59, 62)), (43, (55, 59, 62)), (38, (54, 57, 62)), (43, (55, 59, 62))]
TUNE = _A + _B
CHORDS = _CH_A + _CH_B


def jig_track(dur, bpm=118, lead="both", vol=1.0, drum=True, fade_in=0.3, fade_out=1.2, seed=0):
    """A jig of length dur seconds (bpm = dotted-quarter beats per minute), looping the tune."""
    rng = np.random.default_rng(seed)
    e8 = 60.0 / bpm / 3
    bar = 6 * e8
    out = np.zeros(int((dur + 3) * SR))
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        k = b % len(TUNE)
        t0 = b * bar
        notes = TUNE[k]
        for i, m in enumerate(notes):
            if not m:
                continue
            ln = 1
            while i + ln < 6 and notes[i + ln] == 0:
                ln += 1
            d = ln * e8 * 1.02
            # swing: the first eighth of each triplet a little long
            st = t0 + i * e8 + (0.012 if i % 3 == 1 else 0.0)
            if lead in ("fiddle", "both"):
                _place(out, st, fiddle(_midi(m), d), 0.15)
            if lead in ("whistle", "both"):
                _place(out, st, whistle(_midi(m + 12), d, rng), 0.11 if lead == "both" else 0.2)
        root, chord = CHORDS[k]
        for half in (0, 3):
            _place(out, t0 + half * e8, pluck(_midi(root), bar * 0.5, 0.6, 4.0), 0.3)
            for j, m in enumerate(chord):
                _place(out, t0 + half * e8 + 2 * e8 + j * 0.01, pluck(_midi(m), 0.3, 0.7, 8.0), 0.07)
        if drum:
            _place(out, t0, bodhran(True, rng), 0.35)
            _place(out, t0 + 3 * e8, bodhran(True, rng), 0.28)
            for i in (2, 5):
                _place(out, t0 + i * e8, bodhran(False, rng), 0.25)
    out = out[:int(dur * SR)]
    n = len(out)
    env = np.ones(n)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    env[:fi] = np.linspace(0, 1, fi)
    env[-fo:] *= np.linspace(1, 0, fo)
    return _norm(out * env, 0.6 * vol)


def make_jig(dur, **kw):
    return lambda rng: jig_track(dur, **kw)


def fiddle_flourish(rng):
    """Fergal's quick fiddle run up the scale."""
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate([67, 69, 71, 72, 74, 76, 78, 79]):
        _place(out, k * 0.085, fiddle(_midi(m), 0.12 if k < 7 else 0.8), 0.5)
    return _norm(out, 0.55)


def whistle_air(rng):
    """A slow tin-whistle phrase (a little air)."""
    out = np.zeros(int(5.0 * SR))
    phrase = [(74, 0.5), (76, 0.25), (79, 0.75), (78, 0.25), (76, 0.5), (74, 0.5), (71, 1.0), (74, 1.2)]
    t = 0.0
    for m, d in phrase:
        _place(out, t, whistle(_midi(m + 12), d * 0.98, rng), 0.5)
        t += d
    return _norm(out, 0.5)


# ============================================================ effects

def rain(rng):
    d = 5.0
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 800, 9000) * 0.25
    for _ in range(260):
        i = int(rng.uniform(0, d - 0.02) * SR)
        m = int(0.006 * SR)
        x[i:i + m] += _band(rng.standard_normal(m + 64), 2500, 9000)[:m] * rng.uniform(0.2, 0.7)
    return x * _env(n, 0.8, 1.5) * 0.6


def tink(rng):
    t = _t(0.9)
    x = sum(g * np.sin(TAU * f * t) * np.exp(-t * k) for f, g, k in ((2637, 0.6, 5), (3951, 0.3, 8), (5274, 0.2, 12)))
    return x * np.minimum(1, t / 0.002) * 0.6


def pop(rng):
    t = _t(0.25)
    x = np.sin(TAU * np.cumsum(500 + 900 * np.exp(-t * 40)) / SR) * np.exp(-t * 30)
    x += _band(rng.standard_normal(len(t)), 800, 6000) * np.exp(-t * 80) * 0.6
    return x * 0.8


def paper(rng):
    d = 0.8
    n = int(d * SR)
    x = _band(rng.standard_normal(n), 1500, 9000)
    am = np.abs(_band(rng.standard_normal(n), 5, 40))
    return x * am / (am.max() + 1e-9) * _env(n, 0.05, 0.2) * 0.6


def horn(rng):
    """Ship's horn: two low, warm blasts."""
    out = np.zeros(int(3.0 * SR))
    for st, d in ((0.0, 1.1), (1.4, 1.4)):
        t = _t(d)
        ph = TAU * 110 * t
        x = sum(g * np.sin(h * ph) for h, g in ((1, 1.0), (2, 0.6), (3, 0.4), (4, 0.2), (5, 0.1)))
        x += 0.6 * np.sin(TAU * 138.6 * t)
        _place(out, st, x * _env(len(t), 0.08, 0.25), 0.4)
    return _band(out, 60, 2500) * 0.8


def waves(rng):
    d = 4.0
    n = int(d * SR)
    t = np.arange(n) / SR
    x = _band(rng.standard_normal(n), 100, 2500)
    swell = 0.3 + 0.7 * np.sin(np.pi * t / d) ** 2 * (0.6 + 0.4 * np.sin(TAU * 0.6 * t))
    return x * swell * _env(n, 0.6, 1.0) * 0.5


def gulls(rng):
    out = np.zeros(int(2.4 * SR))
    for k in range(3):
        d = rng.uniform(0.3, 0.45)
        t = _t(d)
        u = t / d
        f = 1400 + 700 * np.sin(np.pi * u) - 500 * u
        x = np.sin(TAU * np.cumsum(f) / SR) + 0.4 * np.sin(2 * TAU * np.cumsum(f) / SR)
        _place(out, k * 0.55 + rng.uniform(0, 0.1), x * _env(len(t), 0.02, 0.1) * (1 - 0.2 * k), 0.4)
    return out


def taps(rng):
    """Hard-shoe dance taps: a quick rattle of heel and toe."""
    out = np.zeros(int(1.4 * SR))
    pat = [0, 0.12, 0.18, 0.3, 0.42, 0.48, 0.6, 0.72, 0.78, 0.9, 1.02, 1.08]
    for st in pat:
        t = _t(0.05)
        x = _band(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 120)
        x += np.sin(TAU * 900 * t) * np.exp(-t * 90) * 0.4
        _place(out, st + rng.uniform(0, 0.01), x, rng.uniform(0.5, 0.9))
    return out * 0.7


def munch(rng):
    out = np.zeros(int(1.2 * SR))
    for k in range(5):
        t = _t(0.12)
        x = _band(rng.standard_normal(len(t)), 300, 3500) * np.exp(-t * 30)
        _place(out, k * 0.2 + rng.uniform(0, 0.03), x, rng.uniform(0.5, 0.9))
    return out * 0.7


def boom(rng):
    """Head first into the bodhran: a big drum boom and a wobble."""
    t = _t(1.4)
    f = 55 + 70 * np.exp(-t * 12) + 6 * np.sin(TAU * 7 * t) * np.exp(-t * 2)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    x += _band(rng.standard_normal(len(t)), 100, 3000) * np.exp(-t * 25) * 0.5
    return x * 0.9


def cheer(rng):
    d = 2.2
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(9):
        dd = rng.uniform(0.5, 1.2)
        t = _t(dd)
        f = rng.uniform(200, 420) * (1 + 0.2 * np.sin(np.pi * t / dd))
        v = np.sin(TAU * np.cumsum(f) / SR)
        v = _band(np.sign(v) * np.abs(v) ** 0.5, 150, 3000)
        _place(out, rng.uniform(0, 0.5), v * _env(len(t), 0.05, 0.3), 0.15)
    for _ in range(40):
        i = int(rng.uniform(0, d - 0.05) * SR)
        m = int(0.01 * SR)
        out[i:i + m] += _band(rng.standard_normal(m + 64), 800, 6000)[:m] * 0.5
    return out * _env(n, 0.05, 0.8) * 0.6


def clop(rng):
    """Pony hooves on a country road, about four seconds."""
    out = np.zeros(int(4.0 * SR))
    st = 0.0
    k = 0
    while st < 3.7:
        t = _t(0.08)
        x = np.sin(TAU * (600 if k % 2 else 480) * t) * np.exp(-t * 70)
        x += _band(rng.standard_normal(len(t)), 600, 4000) * np.exp(-t * 90) * 0.4
        _place(out, st, x, 0.6)
        st += 0.17 if k % 2 == 0 else 0.33
        k += 1
    return out * _env(len(out), 0.3, 0.6) * 0.7


def baa(rng):
    d = 0.8
    t = _t(d)
    f = 330 + 30 * np.sin(np.pi * t / d) + 22 * np.sin(TAU * 9 * t)   # bleating vibrato
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 8))
    x = _band(x, 200, 4000)
    return x * _env(len(t), 0.05, 0.3) * 0.5


def chime(rng):
    """Rainbow shimmer: a rising glissando of bells."""
    out = np.zeros(int(2.5 * SR))
    for k, m in enumerate([72, 76, 79, 84, 88, 91]):
        t = _t(1.4)
        f = _midi(m)
        x = np.sin(TAU * f * t) * np.exp(-t * 3) + 0.3 * np.sin(TAU * f * 2.76 * t) * np.exp(-t * 7)
        _place(out, k * 0.13, x, 0.35)
    return out


def wind(rng):
    d = 4.5
    n = int(d * SR)
    out = np.zeros(n)
    noise = rng.standard_normal(n)
    chunks = 30
    step = n // chunks
    for c in range(chunks):
        u = c / chunks
        lo = 250 + 350 * np.sin(np.pi * u * 2) ** 2
        seg = _band(noise[c * step:(c + 1) * step + step], lo, lo * 1.8)
        w = np.hanning(len(seg))
        out[c * step:c * step + len(seg)] += (seg * w)[:n - c * step]
    return out * _env(n, 0.8, 1.2) * 0.6


def scrabble(rng):
    out = np.zeros(int(1.0 * SR))
    for k in range(12):
        t = _t(0.04)
        x = _band(rng.standard_normal(len(t)), 1200, 7000) * np.exp(-t * 80)
        _place(out, k * 0.07 + rng.uniform(0, 0.03), x, rng.uniform(0.3, 0.7))
    return out * 0.7


def pebbles(rng):
    out = np.zeros(int(1.6 * SR))
    for k in range(8):
        t = _t(0.1)
        f = rng.uniform(1500, 3000)
        x = np.sin(TAU * f * t) * np.exp(-t * 50) + _band(rng.standard_normal(len(t)), 1000, 6000) * np.exp(-t * 70) * 0.5
        _place(out, k * 0.16 + k * k * 0.004 + rng.uniform(0, 0.03), x, 0.6 * (1 - k / 10))
    return out * 0.6


def crackle(rng):
    d = 3.0
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 80, 900) * 0.25
    for _ in range(40):
        i = int(rng.uniform(0, d - 0.05) * SR)
        m = int(rng.uniform(0.002, 0.008) * SR)
        x[i:i + m] += _band(rng.standard_normal(m + 64), 1500, 9000)[:m] * rng.uniform(0.3, 1.0)
    return x * _env(len(t), 0.4, 0.8) * 0.6


def bubble(rng):
    out = np.zeros(int(2.5 * SR))
    for k in range(14):
        t = _t(0.08)
        f = rng.uniform(300, 700) * (1 + 2.5 * t / 0.08)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 40)
        _place(out, rng.uniform(0, 2.3), x, rng.uniform(0.2, 0.45))
    return out


EXTRA_SFX = {
    "jig": (make_jig(49.4), 0.42),
    "busk": (make_jig(9.0, lead="fiddle", drum=False, bpm=112, seed=3), 0.45),
    "fiddle": (fiddle_flourish, 0.5),
    "whistle": (whistle_air, 0.45),
    "rain": (rain, 0.45),
    "tink": (tink, 0.4),
    "pop": (pop, 0.6),
    "paper": (paper, 0.4),
    "horn": (horn, 0.6),
    "waves": (waves, 0.4),
    "gulls": (gulls, 0.35),
    "taps": (taps, 0.5),
    "munch": (munch, 0.55),
    "boom": (boom, 0.8),
    "cheer": (cheer, 0.6),
    "clop": (clop, 0.4),
    "baa": (baa, 0.55),
    "chime": (chime, 0.45),
    "wind": (wind, 0.4),
    "scrabble": (scrabble, 0.5),
    "pebbles": (pebbles, 0.5),
    "crackle": (crackle, 0.5),
    "bubble": (bubble, 0.4),
}
