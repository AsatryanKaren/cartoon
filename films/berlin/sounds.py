"""Berlin sound effects, synthesised with numpy (48 kHz mono float).

Each function takes a numpy Generator and returns samples; EXTRA_SFX maps
names to (function, gain). A few generic ones are borrowed (read-only) from
earlier films; the Berlin ones (U-Bahn door chime and hiss, rail rattle, van
horn and roller door, pretzel boing, jam squish, paint brush, TV Tower lift,
sparrows, river boat horn) are new.
"""
import numpy as np

from films.athens import sounds as ATH
from films.norway import sounds as NOR
from films.amsterdam import sounds as AMS
from films.montblanc import sounds as MB

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


def _bell(f, d, decay=3.0):
    t = _t(d)
    x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * decay * k)
            for h, g, k in ((1, 1.0, 1.0), (2.0, 0.5, 1.6), (2.76, 0.3, 2.2), (5.4, 0.15, 3.5)))
    return x * np.minimum(1, t / 0.003)


# ------------------------------------------------------------------ city

def honk(rng):
    """Friendly two-tone van horn: hoo-hoonk."""
    out = np.zeros(int(0.9 * SR))
    for k, (f, d) in enumerate(((330, 0.18), (330, 0.42))):
        t = _t(d)
        x = np.sign(np.sin(TAU * f * t)) * 0.5 + np.sign(np.sin(TAU * f * 1.26 * t)) * 0.5
        x = _band(x, 200, 3000) * _env(len(t), 0.01, 0.04)
        _place(out, k * 0.26, x)
    return _norm(out, 0.5)


def vandoor(rng):
    """A roller door rattling up (or down) the back of the van."""
    d = 1.1
    out = np.zeros(int(d * SR))
    k, tt = 0, 0.0
    while tt < d - 0.08:
        n = int(0.03 * SR)
        x = _band(rng.standard_normal(n), 600, 5000) * _env(n, 0.002, 0.02, 60)
        _place(out, tt, x, 0.6 + 0.4 * rng.random())
        tt += 0.045 + 0.01 * rng.random()
        k += 1
    n = int(0.25 * SR)
    t = _t(0.25)
    clunk = np.sin(TAU * 90 * t) * np.exp(-t * 22) + _band(rng.standard_normal(n), 100, 900) * np.exp(-t * 30)
    _place(out, d - 0.26, clunk, 1.5)
    return _norm(out, 0.55)


def scurry(rng):
    """Tiny mouse feet pattering over cardboard."""
    out = np.zeros(int(1.0 * SR))
    for k in range(14):
        n = int(0.025 * SR)
        x = _band(rng.standard_normal(n), 1500, 7000) * _env(n, 0.001, 0.015, 120)
        _place(out, k * 0.065 + rng.uniform(0, 0.015), x, rng.uniform(0.5, 1.0))
    return _norm(out, 0.4)


def cushion(rng):
    """A soft cushion plopped down: muffled whump."""
    d = 0.4
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 60, 600) * np.exp(-t * 14) * np.minimum(1, t / 0.01)
    x += 0.6 * np.sin(TAU * 70 * t) * np.exp(-t * 18)
    return _norm(x, 0.55)


def sparrows(rng):
    """City sparrows: quick bright chirps."""
    out = np.zeros(int(2.2 * SR))
    tt = 0.0
    while tt < 1.9:
        d = rng.uniform(0.05, 0.1)
        t = _t(d)
        f0 = rng.uniform(3200, 4400)
        f = f0 * (1 + 0.25 * np.sin(np.pi * t / d)) - 900 * t / d
        x = np.sin(TAU * np.cumsum(f) / SR) * _env(len(t), 0.005, 0.02)
        _place(out, tt, x, rng.uniform(0.4, 0.9))
        tt += rng.uniform(0.08, 0.3)
    return _norm(out, 0.35)


def boing(rng):
    """Cartoon spring: a pretzel snaps round Whiskers' neck."""
    d = 0.7
    t = _t(d)
    f = 220 + 90 * np.sin(TAU * 9 * t) * np.exp(-t * 4)
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _norm(x, 0.5)


def squish(rng):
    """Biting into a soft doughnut."""
    d = 0.45
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 9) * np.minimum(1, t / 0.03)
    x *= 0.6 + 0.4 * np.sin(TAU * 30 * t)
    return _norm(x, 0.45)


def chime(rng):
    """U-Bahn door warning: a quick bright two-note beep-beep, then a lower note."""
    out = np.zeros(int(1.2 * SR))
    for k, n in enumerate((84, 84, 79)):
        t = _t(0.22)
        x = (np.sin(TAU * _midi(n) * t) + 0.3 * np.sin(TAU * _midi(n) * 2 * t)) * _env(len(t), 0.005, 0.06)
        _place(out, k * 0.25, x)
    return _norm(out, 0.45)


def hiss(rng):
    """Pneumatic doors closing: tssshh + thunk."""
    d = 0.8
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 2500, 9000) * _env(len(t), 0.02, 0.3) * np.exp(-t * 2)
    n = int(0.2 * SR)
    tt = _t(0.2)
    thunk = np.sin(TAU * 110 * tt) * np.exp(-tt * 25)
    _place(x, 0.55, thunk, 2.0)
    return _norm(x, 0.45)


def rattle(rng):
    """Train wheels over rail joints: ta-dum ta-dum, with a hum."""
    d = 3.0
    t = _t(d)
    out = 0.15 * np.sin(TAU * 98 * t) * (0.6 + 0.4 * np.sin(TAU * 0.5 * t))
    out += 0.08 * _band(rng.standard_normal(len(t)), 80, 900)
    tt = 0.1
    while tt < d - 0.3:
        for dt in (0.0, 0.14):
            n = int(0.08 * SR)
            x = _band(rng.standard_normal(n), 150, 2000) * _env(n, 0.002, 0.05, 40)
            _place(out, tt + dt, x, 0.9)
        tt += 0.62
    out *= _env(len(t), 0.3, 0.6)
    return _norm(out, 0.5)


def boat(rng):
    """A river boat's mellow horn."""
    d = 1.6
    t = _t(d)
    x = sum(g * np.sin(TAU * f * t) for f, g in ((147, 1.0), (294, 0.5), (220, 0.6), (440, 0.2)))
    x *= _env(len(t), 0.08, 0.4)
    return _norm(x, 0.45)


def brush(rng):
    """A wet paint brush swept across a wall."""
    d = 0.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 1200, 6000) * np.sin(np.pi * t / d) ** 1.5
    return _norm(x, 0.3)


def clap(rng):
    """Happy little claps."""
    out = np.zeros(int(1.4 * SR))
    for k in range(7):
        n = int(0.06 * SR)
        x = _band(rng.standard_normal(n), 700, 5000) * _env(n, 0.001, 0.04, 50)
        _place(out, k * 0.17 + rng.uniform(0, 0.02), x)
    return _norm(out, 0.45)


def lift(rng):
    """The TV Tower lift: a smooth rising hum."""
    d = 3.2
    t = _t(d)
    f = 110 + 70 * t / d
    ph = TAU * np.cumsum(f) / SR
    x = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.1 * _band(rng.standard_normal(len(t)), 200, 1500)
    return _norm(x * _env(len(t), 0.5, 0.8), 0.4)


def pop(rng):
    d = 0.12
    t = _t(d)
    f = 900 * np.exp(-t * 20) + 300
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t * 40)
    return _norm(x, 0.5)


def bells(rng):
    """Church bells across the city."""
    out = np.zeros(int(3.0 * SR))
    for k, n in enumerate((67, 64, 60, 67, 62)):
        _place(out, k * 0.45, _bell(_midi(n), 2.0, 1.4), 0.8)
    return _norm(out, 0.5)


EXTRA_SFX = {
    "thump": (ATH.sfx_thump, 0.6), "sniff": (ATH.sfx_sniff, 0.5), "splat": (ATH.sfx_splat, 0.7),
    "sparkle": (ATH.sfx_sparkle, 0.4), "engine": (NOR.engine, 0.45), "sizzle": (NOR.sizzle, 0.4),
    "crunch": (NOR.crunch, 0.4), "rumble": (AMS.rumble, 0.6), "jingle": (MB.jingle, 0.45),
    "honk": (honk, 0.4), "vandoor": (vandoor, 0.45), "scurry": (scurry, 0.4), "cushion": (cushion, 0.5),
    "sparrows": (sparrows, 0.35), "boing": (boing, 0.45), "squish": (squish, 0.5), "chime": (chime, 0.45),
    "hiss": (hiss, 0.45), "rattle": (rattle, 0.5), "boat": (boat, 0.4), "brush": (brush, 0.35),
    "clap": (clap, 0.45), "lift": (lift, 0.4), "pop": (pop, 0.5), "bells": (bells, 0.4),
}
