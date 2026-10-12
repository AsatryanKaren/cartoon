"""Extra synthesized sound effects for the London film (48 kHz float, numpy only)."""
import numpy as np

from audio import SR, band, env_adsr, place

TAU = 2 * np.pi


def _t(d):
    return np.arange(int(d * SR)) / SR


def _bell(f0, d, partials, decay=1.0):
    t = _t(d)
    x = sum(g * np.sin(TAU * f0 * r * t) * np.exp(-t * k * decay) for r, g, k in partials)
    return x * np.minimum(1, t / 0.004)


def sfx_bong(rng):
    """Big Ben's great bell: a deep E with a hum note and inharmonic shimmer."""
    x = _bell(165.0, 4.5, ((0.5, 0.7, 0.45), (1.0, 1.0, 0.7), (1.2, 0.45, 0.9), (1.5, 0.3, 1.1),
                          (2.0, 0.35, 1.3), (2.6, 0.15, 2.0), (3.3, 0.08, 2.6)))
    t = _t(4.5)
    x *= 1 + 0.06 * np.sin(TAU * 1.3 * t)          # slow beating of a real bell
    return x * 0.32


def sfx_chime(rng):
    """The Westminster quarter chime (first phrase): E G# F# B."""
    out = np.zeros(int(3.4 * SR))
    for k, n in enumerate((76, 72, 74, 67)):
        f = 440.0 * 2 ** ((n - 69) / 12)
        place(out, k * 0.62, _bell(f, 1.6, ((1, 1, 2.0), (2, 0.4, 3.0), (2.76, 0.2, 4.0), (0.5, 0.3, 1.5))), 0.3)
    return out


def sfx_static(rng):
    """Radio warming up: crackly noise that settles."""
    d = 1.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 800, 7000) * (0.4 + 0.6 * (rng.random(len(t)) < 0.08))
    return x * np.exp(-t * 2.5) * 0.35


def sfx_burner(rng):
    """Balloon burner: a roaring whoosh of flame."""
    d = 1.3
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 80, 1600)
    x *= 0.8 + 0.2 * np.sin(TAU * 17 * t)
    return x * env_adsr(len(t), 0.08, 0.5) * 0.55


def _gull_call(rng, f0=1300.0, d=0.32):
    t = _t(d)
    u = t / d
    f = f0 * (1 + 0.35 * np.sin(np.pi * u)) * (1 - 0.25 * u)
    ph = TAU * np.cumsum(f) / SR
    x = sum((1 / h) * np.sin(h * ph) for h in range(1, 6))
    x = band(x + 0.3 * rng.standard_normal(len(t)), 500, 6000)
    return x * env_adsr(len(t), 0.02, 0.1)


def sfx_gulls(rng):
    """Distant seagulls over the sea."""
    out = np.zeros(int(2.4 * SR))
    for k in range(5):
        place(out, rng.uniform(0, 2.0), _gull_call(rng, rng.uniform(1100, 1600), rng.uniform(0.2, 0.35)),
              rng.uniform(0.1, 0.25))
    return out


def sfx_squawk(rng):
    """One cheeky close seagull: 'ha-ha-haaa'."""
    out = np.zeros(int(1.2 * SR))
    for k, (dt, f, d) in enumerate(((0.0, 1200, 0.16), (0.2, 1300, 0.16), (0.42, 1250, 0.4))):
        place(out, dt, _gull_call(rng, f, d), 0.5)
    return out


def sfx_rustle(rng):
    """Paper mail sack rustling."""
    out = np.zeros(int(0.9 * SR))
    for _ in range(9):
        m = int(rng.uniform(0.03, 0.08) * SR)
        place(out, rng.uniform(0, 0.8), band(rng.standard_normal(m), 2000, 9000) * np.hanning(m), 0.3)
    return out


def sfx_rain(rng):
    """Rain shower: hiss plus little drips."""
    d = 6.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 1500, 9000) * 0.18
    for _ in range(90):
        m = int(0.02 * SR)
        tt = np.arange(m) / SR
        drop = np.sin(TAU * rng.uniform(1800, 3500) * tt) * np.exp(-tt * 200)
        place(x, rng.uniform(0, d - 0.05), drop, rng.uniform(0.05, 0.2))
    return x * env_adsr(len(t), 1.0, 1.5)


def sfx_ring(rng):
    """Old phone box bell: brrring-brrring."""
    out = np.zeros(int(1.4 * SR))
    for start in (0.0, 0.6):
        d = 0.4
        t = _t(d)
        x = (np.sin(TAU * 1100 * t) + 0.6 * np.sin(TAU * 1450 * t)) * (np.sin(TAU * 20 * t) > 0)
        place(out, start, x * env_adsr(len(t), 0.005, 0.03), 0.4)
    return out


def sfx_march(rng):
    """Two stamping boots and a snare roll."""
    out = np.zeros(int(1.2 * SR))
    for dt in (0.0, 0.5):
        m = int(0.15 * SR)
        tt = np.arange(m) / SR
        place(out, dt, band(rng.standard_normal(m), 60, 900) * np.exp(-tt * 30), 0.8)
    m = int(0.35 * SR)
    tt = np.arange(m) / SR
    roll = band(rng.standard_normal(m), 1500, 7000) * (0.5 + 0.5 * np.sin(TAU * 30 * tt)) * np.exp(-tt * 6)
    place(out, 0.75, roll, 0.4)
    return out


def sfx_achoo(rng):
    """A small dog's sneeze: breath in, then a sharp 'choo'."""
    out = np.zeros(int(1.0 * SR))
    m = int(0.35 * SR)
    place(out, 0.0, band(rng.standard_normal(m), 600, 3000) * np.linspace(0, 1, m) ** 2, 0.25)
    m = int(0.25 * SR)
    tt = np.arange(m) / SR
    place(out, 0.4, band(rng.standard_normal(m), 900, 6000) * np.exp(-tt * 14), 0.8)
    return out


def sfx_horn2(rng):
    """Big boat horn on the Thames."""
    d = 1.6
    t = _t(d)
    x = sum((1.0 / h) * np.sin(TAU * 98.0 * h * t) for h in range(1, 9))
    return band(x, 50, 2000) * env_adsr(len(t), 0.1, 0.4) * 0.25


def sfx_engine(rng):
    """Bus diesel rumble."""
    d = 3.0
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 40, 300) * (0.6 + 0.4 * np.sin(TAU * 11 * t))
    x += 0.3 * np.sin(TAU * 48 * t) * (0.7 + 0.3 * np.sin(TAU * 3 * t))
    return x * env_adsr(len(t), 0.4, 0.8) * 0.45


def sfx_ding(rng):
    """Bus bell: ding-ding."""
    out = np.zeros(int(1.0 * SR))
    for dt in (0.0, 0.22):
        place(out, dt, _bell(1760, 0.6, ((1, 1, 8), (2.4, 0.3, 12))), 0.35)
    return out


def sfx_cheep(rng):
    """Tiny chicks cheeping."""
    out = np.zeros(int(0.9 * SR))
    for _ in range(6):
        d = rng.uniform(0.06, 0.1)
        t = _t(d)
        f = rng.uniform(3200, 4200) * (1 + 0.3 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
        place(out, rng.uniform(0, 0.75), x, rng.uniform(0.15, 0.3))
    return out


def sfx_bells(rng):
    """Tower Bridge warning bells: fast ringing."""
    out = np.zeros(int(2.0 * SR))
    for k in range(10):
        place(out, k * 0.18, _bell(1320, 0.4, ((1, 1, 10), (2.7, 0.3, 16))), 0.25)
    return out


def sfx_tick(rng):
    """Clockwork ticks."""
    out = np.zeros(int(2.0 * SR))
    for k in range(4):
        m = int(0.03 * SR)
        tt = np.arange(m) / SR
        place(out, k * 0.5, band(rng.standard_normal(m), 2000, 8000) * np.exp(-tt * 150), 0.5)
    return out


def sfx_pour(rng):
    """Tea pouring: a gurgling, rising trickle."""
    d = 1.4
    t = _t(d)
    x = band(rng.standard_normal(len(t)), 600, 3000) * (0.6 + 0.4 * np.sin(TAU * 9 * t))
    for _ in range(14):
        m = int(0.04 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(500, 900) * (1 + t[min(len(t) - 1, int(rng.uniform(0, 1) * len(t)))])
        place(x, rng.uniform(0, d - 0.05), np.sin(TAU * f * tt) * np.exp(-tt * 60), 0.6)
    return x * env_adsr(len(t), 0.1, 0.3) * 0.25


EXTRA_SFX = {
    "bong": (sfx_bong, 0.9), "chime": (sfx_chime, 0.8), "static": (sfx_static, 0.5),
    "burner": (sfx_burner, 0.45), "gulls": (sfx_gulls, 0.5), "squawk": (sfx_squawk, 0.6),
    "rustle": (sfx_rustle, 0.5), "rain": (sfx_rain, 0.55), "ring": (sfx_ring, 0.45),
    "march": (sfx_march, 0.6), "achoo": (sfx_achoo, 0.7), "horn2": (sfx_horn2, 0.6),
    "engine": (sfx_engine, 0.45), "ding": (sfx_ding, 0.5), "cheep": (sfx_cheep, 0.55),
    "bells": (sfx_bells, 0.5), "tick": (sfx_tick, 0.5), "pour": (sfx_pour, 0.5),
}
