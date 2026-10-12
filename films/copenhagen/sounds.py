"""Copenhagen sound effects, synthesised with numpy (48 kHz mono float).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
names to (function, gain). Generic ones are borrowed (read-only) from earlier
films; the Copenhagen ones (music box, trunk lock click, fairy-tale magic
shimmer, ship's bell, duck quacks, cinnamon-snail whirl, guard drum, hat plop,
Tivoli carousel organ, wooden roller-coaster rattle, fireworks) are new.
"""
import numpy as np

from films.athens import sounds as ATH
from films.norway import sounds as NOR
from films.berlin import sounds as BER
from films.london import sounds as LON

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
    if i < 0 or i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += gain * x[:j - i]


def _norm(x, peak=0.6):
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _tine(f, d, decay=4.0):
    """A music-box tine: bright, quick decay, slightly inharmonic."""
    t = _t(d)
    x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * decay * k)
            for h, g, k in ((1, 1.0, 1.0), (3.0, 0.35, 2.0), (5.1, 0.12, 3.5)))
    return x * np.minimum(1, t / 0.002)


# ------------------------------------------------------------------ magic

def musicbox(rng):
    """A little music-box phrase, like the start of a fairy tale."""
    notes = [74, 79, 83, 81, 79, 76, 78, 79, 83, 86]
    out = np.zeros(int(3.6 * SR))
    for k, n in enumerate(notes):
        _place(out, k * 0.27, _tine(_midi(n), 1.2), 0.8)
        if k % 3 == 0:
            _place(out, k * 0.27, _tine(_midi(n - 12), 1.2, 3.0), 0.4)
    return _norm(out, 0.5)


def click(rng):
    """The brass lock of the old trunk: a crisp double click."""
    out = np.zeros(int(0.3 * SR))
    for k, (f, g) in enumerate(((3200, 1.0), (2400, 0.8))):
        t = _t(0.05)
        x = (np.sin(TAU * f * t) + _band(rng.standard_normal(len(t)), 2000, 9000)) * np.exp(-t * 120)
        _place(out, k * 0.07, x, g)
    return _norm(out, 0.55)


def magic(rng):
    """Fairy-tale shimmer: rising glittering arpeggio over a soft swell."""
    d = 2.0
    out = np.zeros(int(d * SR))
    for k in range(16):
        n = 72 + [0, 4, 7, 11, 12, 16, 19, 23][k % 8] + 12 * (k >= 8)
        _place(out, k * 0.09, _tine(_midi(n), 0.8, 6.0), 0.5 + 0.03 * k)
    t = _t(d)
    swell = _band(rng.standard_normal(len(t)), 3000, 9000) * np.sin(np.pi * t / d) ** 2
    out += 0.15 * swell
    return _norm(out, 0.5)


# ------------------------------------------------------------------ harbour

def shipbell(rng):
    """A ship's bell on the harbour: ding-ding."""
    out = np.zeros(int(2.2 * SR))
    for k in range(2):
        t = _t(1.8)
        f = 880
        x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * dk)
                for h, g, dk in ((1, 1.0, 1.6), (2.4, 0.5, 2.5), (4.1, 0.25, 4.0), (0.5, 0.3, 1.2)))
        _place(out, k * 0.35, x * np.minimum(1, t / 0.002), 0.8)
    return _norm(out, 0.45)


def quack(rng):
    """A cheeky duck: quack-quack."""
    out = np.zeros(int(0.8 * SR))
    for k in range(2):
        d = 0.16
        t = _t(d)
        f = rng.uniform(380, 450) * (1 - 0.25 * t / d)
        ph = TAU * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * 0.6 + np.sin(2 * ph) * 0.4
        x = _band(x, 500, 3200) * _env(len(t), 0.01, 0.05)
        x *= 1 + 0.5 * np.sin(TAU * 35 * t)
        _place(out, k * 0.22 + rng.uniform(0, 0.03), x)
    return _norm(out, 0.5)


def whirl(rng):
    """A long pastry ribbon unspooling round and round: a spinning whoop."""
    d = 1.4
    t = _t(d)
    f = 300 + 500 * t / d + 120 * np.sin(TAU * 5 * t)
    x = np.sin(TAU * np.cumsum(f) / SR) * 0.4
    x += _band(rng.standard_normal(len(t)), 600, 3000) * (0.5 + 0.5 * np.sin(TAU * 5 * t)) * 0.5
    return _norm(x * _env(len(t), 0.05, 0.3), 0.45)


def drum(rng):
    """Royal guard side drum: a little rat-a-tat march."""
    out = np.zeros(int(2.0 * SR))
    pattern = [0, 0.25, 0.375, 0.5, 1.0, 1.25, 1.375, 1.5]
    for k, tt in enumerate(pattern):
        n = int(0.12 * SR)
        t = _t(0.12)
        snare = _band(rng.standard_normal(n), 1500, 8000) * np.exp(-t * 35)
        body = np.sin(TAU * 190 * t) * np.exp(-t * 30)
        _place(out, tt, snare * 0.7 + body * 0.6, 1.0 if k % 4 == 0 else 0.7)
    return _norm(out, 0.45)


def plop(rng):
    """A big furry hat landing on a cat: soft, fluffy whumpf."""
    d = 0.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 80, 900) * np.exp(-t * 16) * np.minimum(1, t / 0.008)
    x += 0.5 * np.sin(TAU * (120 - 60 * t) * t) * np.exp(-t * 14)
    return _norm(x, 0.55)


# ------------------------------------------------------------------ tivoli

def organ(rng):
    """Carousel band organ: oom-pah-pah with a reedy tune (about 6 s)."""
    bpm = 168
    beat = 60 / bpm
    tune = [79, 76, 79, 84, 83, 81, 79, 76, 77, 79, 81, 77, 76, 74, 72, 74, 76, 79]
    bass = [48, 43, 48, 43, 41, 48, 43, 48, 43]
    d = len(tune) * beat + 1.0
    out = np.zeros(int(d * SR))

    def reed(f, dd):
        t = _t(dd)
        x = sum((1 / h) * np.sin(TAU * f * h * t + 0.3 * np.sin(TAU * 5.5 * t)) for h in range(1, 6))
        return x * _env(len(t), 0.02, 0.06)

    for k, n in enumerate(tune):
        _place(out, k * beat, reed(_midi(n), beat * 0.9), 0.35)
    for k in range(len(tune)):
        tt = k * beat
        if k % 3 == 0:
            _place(out, tt, reed(_midi(bass[(k // 3) % len(bass)]), beat * 0.8), 0.5)
        else:
            for iv in (16, 19):
                _place(out, tt, reed(_midi(bass[(k // 3) % len(bass)] + iv), beat * 0.4), 0.15)
    return _norm(out, 0.5)


def coaster(rng):
    """The old wooden roller coaster: clackety climb, then a rushing rumble."""
    d = 4.0
    out = np.zeros(int(d * SR))
    tt, gap = 0.0, 0.16
    while tt < d - 0.1:
        n = int(0.04 * SR)
        t = _t(0.04)
        x = _band(rng.standard_normal(n), 300, 3000) * np.exp(-t * 70) + np.sin(TAU * 140 * t) * np.exp(-t * 60)
        _place(out, tt, x, 0.7)
        tt += gap
        gap = max(0.05, gap * 0.96)
    t = _t(d)
    rumble = _band(rng.standard_normal(len(t)), 40, 400) * np.minimum(1, t / 2.0)
    out += rumble * 0.8
    return _norm(out * _env(len(t), 0.05, 0.4), 0.5)


def fireworks(rng):
    """A rocket whistle, then a pop and crackle."""
    d = 2.4
    out = np.zeros(int(d * SR))
    t = _t(0.7)
    f = 900 + 1400 * t / 0.7
    whistle = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.05, 0.05) * 0.3
    _place(out, 0, whistle)
    t2 = _t(0.5)
    boom = _band(rng.standard_normal(len(t2)), 40, 600) * np.exp(-t2 * 9)
    _place(out, 0.72, boom, 1.0)
    for _ in range(40):
        n = int(0.012 * SR)
        x = _band(rng.standard_normal(n), 2000, 9000) * np.exp(-_t(0.012) * 300)
        _place(out, 0.8 + rng.uniform(0, 1.3), x, rng.uniform(0.2, 0.6))
    return _norm(out, 0.55)


EXTRA_SFX = {
    "musicbox": (musicbox, 0.5), "click": (click, 0.5), "magic": (magic, 0.45),
    "shipbell": (shipbell, 0.35), "quack": (quack, 0.4), "whirl": (whirl, 0.4), "drum": (drum, 0.4),
    "plop": (plop, 0.5), "organ": (organ, 0.45), "coaster": (coaster, 0.45), "fireworks": (fireworks, 0.5),
    # borrowed
    "rain": (ATH.sfx_rain, 0.35), "page": (ATH.sfx_page, 0.45), "thump": (ATH.sfx_thump, 0.55),
    "sparkle": (ATH.sfx_sparkle, 0.4), "flap": (ATH.sfx_flap, 0.5), "gulls": (ATH.sfx_gulls, 0.3),
    "wind": (NOR.wind, 0.4), "waves": (NOR.waves, 0.35), "creak": (NOR.creak, 0.4),
    "scurry": (BER.scurry, 0.4), "boing": (BER.boing, 0.45), "clap": (BER.clap, 0.45),
    "sparrows": (BER.sparrows, 0.35), "pour": (LON.sfx_pour, 0.4),
}
