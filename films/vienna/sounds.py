"""Vienna sound effects and waltz music, synthesised with numpy (48 kHz mono float).

The film's music moods are 4/4, so the real waltzes (3/4, oom-pah-pah with a
singing violin -- the opening of Strauss' Blue Danube, which is public domain)
are rendered here as long "sound effects" placed on the dancing moments.
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

def violin(f, d, vib=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    vdepth = 0.004 * vib * np.minimum(1, t / 0.25)
    ph = TAU * np.cumsum(f * (1 + vdepth * np.sin(TAU * 5.6 * t))) / SR
    x = sum((1.0 / h) * (0.9 if h % 2 else 0.6) * np.sin(h * ph) for h in range(1, 9))
    bow = 1 + 0.08 * np.sin(TAU * 3.1 * t)
    return x * _env(n, 0.05, min(0.18, d * 0.4)) * bow


def pluck(f, d, bright=1.0, decay=5.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = sum((bright ** (h - 1)) / h * np.sin(TAU * f * h * t) * np.exp(-t * decay * (1 + 0.4 * h))
            for h in range(1, 6))
    return x * _env(n, 0.003, 0.05)


def piano(f, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = sum(g * np.sin(TAU * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * k)
            for h, g, k in ((1, 1.0, 2.2), (2, 0.5, 3.0), (3, 0.25, 4.0), (4, 0.12, 6.0), (5, 0.06, 8.0)))
    return x * _env(n, 0.004, 0.08)


def glock(f, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = (np.sin(TAU * f * t) * np.exp(-t * 3.5) + 0.4 * np.sin(TAU * f * 2.76 * t) * np.exp(-t * 7)
         + 0.2 * np.sin(TAU * f * 5.4 * t) * np.exp(-t * 12))
    return x * _env(n, 0.002, 0.05)


# ============================================================ the waltz

# (bar, beat, midi, beats) -- the opening tune of the Blue Danube, in D major
_D, _A7, _G, _EM = (50, (62, 66, 69)), (45, (61, 64, 67)), (43, (62, 67, 71)), (52, (64, 67, 71))
TUNE = []
_bars = [
    [(2, 62, 1)], [(0, 62, 1), (1, 66, 1), (2, 69, 1)], [(0, 69, 3)], [(1, 81, 1), (2, 81, 1)],
    [(1, 78, 1), (2, 78, 1)], [(2, 62, 1)], [(0, 62, 1), (1, 66, 1), (2, 69, 1)], [(0, 69, 3)],
    [(1, 81, 1), (2, 81, 1)], [(1, 79, 1), (2, 79, 1)], [(2, 61, 1)], [(0, 61, 1), (1, 64, 1), (2, 71, 1)],
    [(0, 71, 3)], [(1, 83, 1), (2, 83, 1)], [(1, 79, 1), (2, 79, 1)], [(2, 61, 1)],
    [(0, 61, 1), (1, 64, 1), (2, 71, 1)], [(0, 71, 3)], [(1, 83, 1), (2, 83, 1)], [(1, 78, 1), (2, 78, 1)],
    [(2, 62, 1)], [(0, 62, 1), (1, 66, 1), (2, 69, 1)], [(0, 74, 3)], [(1, 86, 1), (2, 86, 1)],
    [(1, 81, 1), (2, 81, 1)], [(2, 62, 1)], [(0, 62, 1), (1, 66, 1), (2, 69, 1)], [(0, 74, 3)],
    [(1, 86, 1), (2, 86, 1)], [(1, 83, 1), (2, 83, 1)], [(2, 64, 1)], [(0, 64, 1), (1, 67, 1), (2, 71, 1)],
    [(0, 73, 2), (2, 76, 1)], [(0, 79, 1), (1, 76, 1), (2, 73, 1)], [(0, 74, 3)], [],
]
for _b, notes in enumerate(_bars):
    for beat, m, d in notes:
        TUNE.append((_b, beat, m, d))
CHORDS = ([_D] * 10 + [_A7] * 10 + [_D] * 5 + [_G] * 5 + [_EM] * 2 + [_A7] * 2 + [_D] * 2)
NBARS = len(_bars)


def waltz_track(dur, bpm=172, lead="violin", vol=1.0, fade_in=0.4, fade_out=1.2, ritard=False, seed=0):
    """Oom-pah-pah waltz of length dur seconds, looping the tune."""
    beat = 60.0 / bpm
    bar = 3 * beat
    out = np.zeros(int((dur + 3) * SR))
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        k = b % NBARS
        root, chord = CHORDS[k]
        t0 = b * bar
        # Viennese lilt: beat 2 comes a little early
        beats = (0.0, beat * 0.88, beat * 2.0)
        if lead == "musicbox":
            _place(out, t0, glock(_midi(root + 24), 1.2), 0.25)
            for bt in beats[1:]:
                for m in chord:
                    _place(out, t0 + bt, glock(_midi(m + 12), 0.6), 0.07)
        else:
            _place(out, t0, pluck(_midi(root), bar * 1.1, 0.6, 3.0), 0.5)
            _place(out, t0, pluck(_midi(root - 12), bar * 1.1, 0.4, 2.5), 0.35)
            for bt in beats[1:]:
                for m in chord:
                    _place(out, t0 + bt, piano(_midi(m), 0.4), 0.09)
                    _place(out, t0 + bt, pluck(_midi(m + 12), 0.25, 0.5, 9), 0.04)
        for (bb, bt, m, d) in TUNE:
            if bb != k:
                continue
            st = t0 + beats[bt] if bt < 3 else t0 + bt * beat
            if lead == "violin":
                _place(out, st, violin(_midi(m), d * beat * 1.05), 0.16)
                _place(out, st, violin(_midi(m - 12), d * beat * 1.05, 0.7), 0.06)
                _place(out, st, piano(_midi(m), 0.8), 0.05)
            elif lead == "piano":
                _place(out, st, piano(_midi(m), max(0.6, d * beat)), 0.22)
            else:
                _place(out, st, glock(_midi(m + 12), max(0.8, d * beat * 1.2)), 0.2)
    out = out[:int(dur * SR)]
    n = len(out)
    env = np.ones(n)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    env[:fi] = np.linspace(0, 1, fi)
    env[-fo:] *= np.linspace(1, 0, fo)
    return _norm(out * env, 0.6 * vol)


def make_waltz(dur, **kw):
    return lambda rng: waltz_track(dur, **kw)


# ============================================================ city sounds

def chime(rng):
    out = np.zeros(int(2.4 * SR))
    for k, m in enumerate((86, 90, 93, 98, 102)):
        _place(out, k * 0.09, glock(_midi(m), 1.8), 0.5)
    return _norm(out, 0.4)


def crinkle(rng):
    d = 0.9
    out = np.zeros(int(d * SR))
    for _ in range(40):
        m = int(rng.uniform(0.005, 0.02) * SR)
        x = _band(rng.standard_normal(m), 1500, 9000) * _env(m, 0.001, 0.004)
        _place(out, rng.uniform(0, d - 0.03), x, rng.uniform(0.3, 1.0))
    return _norm(out, 0.35)


def thump(rng):
    d = 0.4
    t = _t(d)
    x = np.sin(TAU * np.cumsum(60 + 80 * np.exp(-t * 25)) / SR) * np.exp(-t * 12)
    x += _band(rng.standard_normal(len(t)), 100, 800) * np.exp(-t * 30) * 0.4
    return _norm(x, 0.6)


def engine(rng):
    d = 4.0
    t = _t(d)
    f = 48 + 4 * np.sin(TAU * 0.3 * t)
    ph = TAU * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.4 + np.sin(2 * ph) * 0.3
    x = _band(x, 30, 600) + _band(rng.standard_normal(len(t)), 80, 400) * 0.3
    return _norm(x * _env(len(t), 0.5, 0.8), 0.4)


def bass(rng):
    """The double bass booming inside its case: a deep plucked note."""
    d = 1.6
    t = _t(d)
    f = 41.2
    x = sum((1 / h) * np.sin(TAU * f * h * t) * np.exp(-t * (2 + h)) for h in range(1, 6))
    x += _band(rng.standard_normal(len(t)), 60, 300) * np.exp(-t * 20) * 0.3
    return _norm(x * _env(len(t), 0.004, 0.2), 0.6)


def honk(rng):
    d = 0.7
    t = _t(d)
    x = np.zeros(len(t))
    for f in (330, 415):
        x += np.sign(np.sin(TAU * f * t)) * 0.5
    x = _band(x, 200, 3000) * _env(len(t), 0.02, 0.08)
    x[int(0.28 * SR):int(0.36 * SR)] *= 0.1
    return _norm(x, 0.4)


def brakes(rng):
    d = 1.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 2.5) * _env(len(t), 0.01, 0.2)
    return _norm(x, 0.3)


def bells(rng):
    """Deep cathedral bells of St. Stephen's."""
    d = 6.0
    out = np.zeros(int(d * SR))
    for k, f in enumerate((98, 123.5, 98, 146.8)):
        m = int(4.0 * SR)
        tt = np.arange(m) / SR
        x = sum(g * np.sin(TAU * f * r * tt) * np.exp(-tt * dk)
                for r, g, dk in ((0.5, 0.6, 0.6), (1, 1.0, 0.8), (1.19, 0.5, 1.2), (1.5, 0.4, 1.5), (2, 0.35, 1.8),
                                 (2.74, 0.2, 2.5)))
        _place(out, k * 1.3, x * _env(m, 0.003, 0.3), 0.6)
    return _norm(out, 0.5)


def clop(rng):
    out = np.zeros(int(1.4 * SR))
    for k, st in enumerate((0.0, 0.3, 0.7, 1.0)):
        m = int(0.08 * SR)
        tt = np.arange(m) / SR
        x = (np.sin(TAU * rng.uniform(700, 900) * tt) * 0.6 + _band(rng.standard_normal(m), 900, 4000) * 0.5)
        _place(out, st, x * np.exp(-tt * 60), 1.0 - 0.15 * (k % 2))
    return _norm(out, 0.45)


def neigh(rng):
    d = 1.3
    t = _t(d)
    u = t / d
    f = 600 + 500 * np.sin(np.pi * np.minimum(1, u * 1.4)) - 250 * u
    f = f * (1 + 0.05 * np.sin(TAU * 18 * t))
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6))
    x = _band(x, 200, 5000) * _env(len(t), 0.05, 0.35)
    return _norm(x, 0.45)


def sniff(rng):
    out = np.zeros(int(0.8 * SR))
    for k in range(3):
        m = int(0.12 * SR)
        x = _band(rng.standard_normal(m), 1500, 6000) * np.sin(np.linspace(0, np.pi, m))
        _place(out, k * 0.22, x)
    return _norm(out, 0.35)


def piano_tune(rng):
    """A coffee-house pianist: the opening of Mozart's Eine kleine Nachtmusik (G major)."""
    notes = [(0, 67, 0.5), (0.75, 62, 0.25), (1.0, 67, 0.5), (1.75, 62, 0.25), (2.0, 67, 0.25), (2.25, 62, 0.25),
             (2.5, 67, 0.25), (2.75, 71, 0.25), (3.0, 74, 1.0),
             (4.0, 72, 0.5), (4.75, 69, 0.25), (5.0, 72, 0.5), (5.75, 69, 0.25), (6.0, 72, 0.25), (6.25, 69, 0.25),
             (6.5, 66, 0.25), (6.75, 69, 0.25), (7.0, 62, 1.0)]
    beat = 0.42
    out = np.zeros(int(4.2 * SR))
    for st, m, d in notes:
        _place(out, st * beat, piano(_midi(m), max(0.5, d * beat * 2)), 0.6)
    for st, m in ((0, 43), (1, 50), (2, 43), (3, 47), (4, 50), (5, 54), (6, 50), (7, 43)):
        _place(out, st * beat, piano(_midi(m), 0.9), 0.35)
    return _norm(out, 0.45)


def munch(rng):
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        m = int(0.09 * SR)
        x = _band(rng.standard_normal(m), 400, 4000) * _env(m, 0.003, 0.05, 25)
        _place(out, k * 0.18, x, 1.0 - 0.2 * k)
    return _norm(out, 0.4)


def squirt(rng):
    d = 0.6
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1200, 7000) * _env(len(t), 0.01, 0.1)
    x *= 0.6 + 0.4 * np.sin(TAU * 30 * t)
    return _norm(x, 0.35)


def splat(rng):
    d = 0.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 150, 2500) * np.exp(-t * 14)
    x += np.sin(TAU * np.cumsum(220 * np.exp(-t * 8)) / SR) * np.exp(-t * 10) * 0.6
    return _norm(x, 0.55)


def bell(rng):
    """The little bell over the coffee-house door."""
    out = np.zeros(int(1.4 * SR))
    for k in range(3):
        _place(out, k * 0.12, glock(_midi(96 - 2 * (k % 2)), 1.1), 0.6)
    return _norm(out, 0.35)


def yowl(rng):
    d = 0.8
    t = _t(d)
    u = t / d
    f = 700 + 500 * np.sin(np.pi * u) + 30 * np.sin(TAU * 9 * t)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6)) * _env(len(t), 0.03, 0.2)
    return _norm(x, 0.45)


def boing(rng):
    d = 0.6
    t = _t(d)
    f = 180 + 260 * np.exp(-t * 6) * (1 + 0.3 * np.sin(TAU * 14 * t))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _norm(x, 0.45)


def creak(rng):
    d = 1.0
    t = _t(d)
    f = 120 + 60 * np.sin(np.pi * t / d)
    pulses = (np.sin(TAU * np.cumsum(f) / SR) > 0.95).astype(float)
    x = _band(pulses + 0.1 * rng.standard_normal(len(t)), 300, 3000) * _env(len(t), 0.1, 0.3)
    return _norm(x, 0.3)


def scrape(rng):
    """Paws skidding across a polished parquet floor."""
    d = 1.0
    t = _t(d)
    f = 900 - 500 * t / d
    x = np.sin(TAU * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(TAU * 40 * t))
    x = x * 0.4 + _band(rng.standard_normal(len(t)), 1500, 6000) * 0.4
    return _norm(x * _env(len(t), 0.02, 0.25), 0.4)


def crash(rng):
    """Cymbal crash + a drum thud (Whiskers lands in the orchestra)."""
    d = 2.2
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 3000, 14000) * np.exp(-t * 2.2)
    x += np.sin(TAU * np.cumsum(70 + 60 * np.exp(-t * 20)) / SR) * np.exp(-t * 7) * 0.9
    return _norm(x * _env(len(t), 0.002, 0.3), 0.6)


def laugh(rng):
    """A ballroom full of giggles: many short 'ha' syllables."""
    d = 2.6
    out = np.zeros(int(d * SR))
    for v in range(10):
        f0 = rng.uniform(220, 520)
        st = rng.uniform(0, 0.4)
        for k in range(rng.integers(4, 8)):
            m = int(0.11 * SR)
            tt = np.arange(m) / SR
            ph = TAU * f0 * (1 - 0.1 * tt / 0.11) * tt
            x = sum(np.sin(h * ph) / h for h in range(1, 8))
            x = _band(x + 0.3 * rng.standard_normal(m), 300, 3500) * np.sin(np.pi * tt / 0.11) ** 2
            _place(out, st + k * rng.uniform(0.16, 0.22), x, rng.uniform(0.3, 0.7))
    return _norm(out * _env(len(out), 0.05, 0.8), 0.4)


def cheer(rng):
    """Applause and cheers."""
    d = 3.5
    out = np.zeros(int(d * SR))
    for _ in range(260):
        m = int(0.012 * SR)
        x = _band(rng.standard_normal(m), 800, 8000) * _env(m, 0.001, 0.008)
        _place(out, rng.uniform(0, d - 0.1), x, rng.uniform(0.2, 0.8))
    for _ in range(6):
        m = int(0.6 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(400, 700) * (1 + 0.2 * np.sin(np.pi * tt / 0.6))
        x = sum(np.sin(h * TAU * np.cumsum(f) / SR) / h for h in range(1, 5)) * np.sin(np.pi * tt / 0.6)
        _place(out, rng.uniform(0, d - 0.7), _band(x, 300, 3000), 0.15)
    return _norm(out * _env(len(out), 0.1, 1.0), 0.45)


# Waltz lengths are matched to the action moments they play under (see the timing printed by
# timeline.py): the lesson, the first (failed) dance, the second dance and the dance at home.
EXTRA_SFX = {
    "waltz_short": (make_waltz(14.0, bpm=168, fade_in=1.0, fade_out=3.0), 0.68),
    "waltz_lesson": (make_waltz(9.2, bpm=150, lead="piano", fade_in=0.3, fade_out=0.3), 0.62),
    "waltz_fail": (make_waltz(9.25, bpm=172, fade_in=0.2, fade_out=0.12), 0.6),
    "waltz_big": (make_waltz(14.8, bpm=176, fade_in=0.2, fade_out=1.6, seed=2), 0.65),
    "waltz_end": (make_waltz(8.0, bpm=172, fade_in=0.2, fade_out=2.5, seed=3), 0.6),
    "musicbox": (make_waltz(11.0, bpm=150, lead="musicbox", fade_in=0.2, fade_out=2.0), 0.4),
    "chime": (chime, 0.35), "crinkle": (crinkle, 0.45), "thump": (thump, 0.55), "engine": (engine, 0.45),
    "bass": (bass, 0.6), "honk": (honk, 0.35), "brakes": (brakes, 0.3), "bells": (bells, 0.45),
    "clop": (clop, 0.5), "neigh": (neigh, 0.45), "sniff": (sniff, 0.45), "piano": (piano_tune, 0.4),
    "munch": (munch, 0.5), "squirt": (squirt, 0.45), "splat": (splat, 0.6), "bell": (bell, 0.4),
    "yowl": (yowl, 0.55), "boing": (boing, 0.45), "creak": (creak, 0.35), "scrape": (scrape, 0.5),
    "crash": (crash, 0.55), "laugh": (laugh, 0.85), "cheer": (cheer, 0.5),
}
