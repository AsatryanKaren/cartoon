"""Extra synthesized sound effects for the Paris film (48 kHz float, numpy only)."""
import numpy as np

from audio import SR, band, env_adsr, place

TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def sfx_whistle(rng):
    """Train whistle: two detuned reedy tones with a breathy edge."""
    d = 1.3
    t = _t(d)
    n = len(t)
    x = np.zeros(n)
    for f in (587.0, 740.0, 880.0):
        vib = 1 + 0.004 * np.sin(TAU * 5.5 * t)
        ph = TAU * np.cumsum(f * vib) / SR
        x += sum((0.6 / h) * np.sin(h * ph) for h in (1, 2, 3))
    breath = band(rng.standard_normal(n), 1500, 6000) * 0.25
    e = env_adsr(n, 0.06, 0.35)
    e *= 0.85 + 0.15 * np.sin(TAU * 1.2 * t)
    return (x / 3 + breath) * e * 0.5


def sfx_chug(rng):
    """Train wheels: four bursts of 'chuff' noise with a clickety rhythm."""
    d = 2.4
    out = np.zeros(int(d * SR))
    for k in range(8):
        m = int(0.16 * SR)
        tt = np.arange(m) / SR
        burst = band(rng.standard_normal(m), 150, 2500) * np.exp(-tt * 22)
        place(out, k * 0.3, burst, 0.5 if k % 2 == 0 else 0.3)
        click = np.sin(TAU * 1800 * tt[:int(0.02 * SR)]) * np.exp(-tt[:int(0.02 * SR)] * 300)
        place(out, k * 0.3 + 0.15, click, 0.25)
    return out * env_adsr(len(out), 0.2, 0.6)


def sfx_bell(rng):
    """Church / shop bell: inharmonic partials with long decay."""
    d = 2.6
    t = _t(d)
    f0 = 392.0
    x = sum(g * np.sin(TAU * f0 * r * t) * np.exp(-t * k)
            for r, g, k in ((0.5, 0.6, 1.2), (1.0, 1.0, 1.6), (1.19, 0.5, 2.0), (1.5, 0.35, 2.5),
                            (2.0, 0.4, 3.0), (2.74, 0.2, 4.5)))
    return x * np.minimum(1, t / 0.003) * 0.35


def sfx_sparkle(rng):
    """Twinkling: quick random high pings."""
    d = 1.8
    out = np.zeros(int(d * SR))
    for _ in range(22):
        f = rng.uniform(2200, 5200)
        m = int(0.25 * SR)
        tt = np.arange(m) / SR
        ping = np.sin(TAU * f * tt) * np.exp(-tt * 18)
        place(out, rng.uniform(0, d - 0.3), ping, rng.uniform(0.1, 0.3))
    return out * env_adsr(len(out), 0.05, 0.5)


def sfx_horn(rng):
    """Riverboat horn: low, two notes in a fifth, slightly buzzy."""
    d = 1.6
    t = _t(d)
    x = np.zeros(len(t))
    for f in (110.0, 165.0):
        ph = TAU * f * t
        x += sum((1.0 / h) * np.sin(h * ph) for h in range(1, 8))
    return band(x, 60, 2500) * env_adsr(len(t), 0.08, 0.4) * 0.22


def sfx_poof(rng):
    """Soft flour poof."""
    d = 0.9
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 120, 1800) * np.exp(-t * 6) * np.minimum(1, t / 0.02)
    return x * 0.8


def sfx_accordion(rng):
    """A musette-style accordion chord swell (detuned reeds, tremolo)."""
    d = 1.6
    t = _t(d)
    x = np.zeros(len(t))
    for note in (57, 61, 64, 69):        # A major
        f = 440.0 * 2 ** ((note - 69) / 12)
        for det in (-0.004, 0.0, 0.004):   # wet musette tuning
            ph = TAU * f * (1 + det) * t
            x += sum((0.5 / h) * np.sin(h * ph) for h in (1, 2, 3, 4))
    x *= 0.85 + 0.15 * np.sin(TAU * 6 * t)
    return x / 12 * env_adsr(len(t), 0.12, 0.5) * 0.6


EXTRA_SFX = {
    "whistle": (sfx_whistle, 0.5),
    "chug": (sfx_chug, 0.45),
    "bell": (sfx_bell, 0.5),
    "sparkle": (sfx_sparkle, 0.45),
    "horn": (sfx_horn, 0.6),
    "poof": (sfx_poof, 0.6),
    "accordion": (sfx_accordion, 1.3),
}
