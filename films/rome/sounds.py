"""Extra synthesised sound effects for the Rome film (48 kHz float samples).

Self-contained (numpy only) so importing it never pulls in the audio engine.
"""
import numpy as np

SR = 48000
TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a, r):
    t = np.arange(n) / SR
    d = n / SR
    return np.minimum(1.0, t / max(a, 1e-4)) * np.minimum(1.0, (d - t) / max(r, 1e-4))


def _band(noise, lo, hi):
    f = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(len(noise), 1 / SR)
    f[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(f, len(noise))


def _place(buf, start, x, gain=1.0):
    i = int(start * SR)
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += gain * x[:j - i]


def vespa(rng):
    """Little scooter: a buzzing two-stroke engine passing by plus a 'meep-meep' horn."""
    d = 2.2
    t = _t(d)
    n = len(t)
    u = t / d
    f = 70 + 60 * np.sin(np.pi * np.minimum(1, u * 1.2))           # revs up, then fades away
    ph = TAU * np.cumsum(f) / SR
    eng = np.sign(np.sin(ph)) * 0.4 + np.sin(2 * ph) * 0.3
    eng = _band(eng + 0.3 * rng.standard_normal(n), 60, 2500)
    pass_by = np.exp(-((u - 0.45) / 0.22) ** 2)
    out = eng * pass_by * 0.55
    for st in (0.12, 0.34):
        tt = _t(0.17)
        x = np.sign(np.sin(TAU * 420 * tt)) * 0.5 + np.sin(TAU * 525 * tt) * 0.5
        _place(out, st, _band(x, 200, 4000) * _env(len(tt), 0.005, 0.03), 0.6)
    return out


def chug(rng):
    """Train wheels: a few seconds of 'clickety-clack'."""
    d = 3.0
    out = np.zeros(int(d * SR))
    k = 0
    tt = 0.0
    while tt < d - 0.2:
        m = int(0.09 * SR)
        x = _band(rng.standard_normal(m), 150, 1800) * np.exp(-np.arange(m) / SR * 45)
        _place(out, tt, x, 0.7 if k % 2 == 0 else 0.45)
        tt += 0.16 if k % 2 == 0 else 0.34
        k += 1
    t = _t(d)
    return out * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.6)


def whistle(rng):
    """Two-tone train whistle."""
    d = 1.3
    t = _t(d)
    f = np.where(t < 0.5, 660, 740) * (1 + 0.004 * np.sin(TAU * 5 * t))
    ph = TAU * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(1.5 * ph) + 0.3 * np.sin(2 * ph)
    x += 0.25 * _band(rng.standard_normal(len(t)), 1500, 5000)
    return x * _env(len(t), 0.05, 0.3) * 0.35


def fountain(rng):
    """Splashing fountain bed, a few seconds long."""
    d = 4.0
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 400, 7000)
    x *= 0.7 + 0.3 * np.sin(TAU * 0.7 * t) * np.sin(TAU * 1.3 * t + 1)
    for _ in range(30):
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        fr = rng.uniform(900, 2000) * (1 + 1.2 * tt / 0.05)
        _place(x, rng.uniform(0, d - 0.1), np.sin(TAU * np.cumsum(fr) / SR) * np.exp(-tt * 70), 0.8)
    return x * _env(len(t), 0.8, 1.2) * 0.35


def flutter(rng):
    """Pigeon wings: quick soft flaps."""
    d = 0.9
    out = np.zeros(int(d * SR))
    for k in range(7):
        m = int(0.07 * SR)
        x = _band(rng.standard_normal(m), 300, 3500) * np.hanning(m)
        _place(out, k * 0.11, x, 0.8 - k * 0.08)
    return out * 0.6


def coo(rng):
    """Pigeon 'croo-croo'."""
    out = np.zeros(int(0.9 * SR))
    for st in (0.0, 0.38):
        t = _t(0.32)
        f = 330 + 90 * np.sin(np.pi * t / 0.32)
        ph = TAU * np.cumsum(f) / SR
        x = np.sin(ph) * (0.6 + 0.4 * np.sin(TAU * 28 * t))
        _place(out, st, x * _env(len(t), 0.03, 0.1), 0.45)
    return out


def splat(rng):
    """Soft dough landing on a cat."""
    d = 0.5
    t = _t(d)
    x = _band(rng.standard_normal(len(t)), 80, 1200) * np.exp(-t * 14)
    x += np.sin(TAU * np.cumsum(140 * np.exp(-t * 6)) / SR) * np.exp(-t * 12) * 0.8
    return x * np.minimum(1, t / 0.003) * 0.7


def plink(rng):
    """Coin dropping into water: a bright 'plink' then a bloop."""
    d = 0.7
    t = _t(d)
    ring = sum(g * np.sin(TAU * f * t) * np.exp(-t * k)
               for f, g, k in ((2600, 0.5, 16), (4100, 0.3, 22), (6300, 0.15, 30)))
    tt = t - 0.12
    bloop = np.where(tt > 0, np.sin(TAU * np.cumsum(np.where(tt > 0, 500 + 1600 * np.clip(tt, 0, 1) / 0.08, 0)) / SR)
                     * np.exp(-np.clip(tt, 0, None) * 30), 0)
    return (ring * np.minimum(1, t / 0.002) + 0.6 * bloop) * 0.6


def sparkle(rng):
    """Magic twinkle: a quick run of high bell notes."""
    d = 1.2
    out = np.zeros(int(d * SR))
    notes = [84, 88, 91, 96, 100]
    for k, n in enumerate(notes):
        f = 440 * 2 ** ((n - 69) / 12)
        t = _t(0.6)
        x = (np.sin(TAU * f * t) + 0.3 * np.sin(TAU * 2 * f * t)) * np.exp(-t * 8)
        _place(out, k * 0.09, x, 0.35)
    return out


def pant(rng):
    """Out-of-breath huffing."""
    d = 1.6
    out = np.zeros(int(d * SR))
    for k in range(5):
        m = int(0.22 * SR)
        x = _band(rng.standard_normal(m), 500, 3000) * np.hanning(m)
        _place(out, k * 0.31, x, 0.5 if k % 2 == 0 else 0.35)
    return out


def bells(rng):
    """Distant church bells (Rome has hundreds)."""
    d = 4.0
    out = np.zeros(int(d * SR))
    for k, n in enumerate((67, 64, 60, 67, 64, 60)):
        f = 440 * 2 ** ((n - 69) / 12)
        t = _t(2.2)
        x = sum(g * np.sin(TAU * f * h * t) * np.exp(-t * (1.5 + h)) for h, g in ((1, 1), (2.4, 0.4), (3.0, 0.25)))
        _place(out, k * 0.6, x * np.minimum(1, t / 0.003), 0.25)
    return out


EXTRA_SFX = {
    "vespa": (vespa, 0.7), "chug": (chug, 0.5), "whistle": (whistle, 0.45), "fountain": (fountain, 0.45),
    "flutter": (flutter, 0.5), "coo": (coo, 0.5), "splat": (splat, 0.8), "plink": (plink, 0.7),
    "sparkle": (sparkle, 0.5), "pant": (pant, 0.45), "bells": (bells, 0.4),
}
