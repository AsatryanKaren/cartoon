"""Episode 1 sound effects (48 kHz mono float). EXTRA_SFX maps names to (function, gain)."""
import numpy as np

SR = 48000
TAU = 2 * np.pi


def bloop(rng):
    """Bubbles rising from the deep: three rising 'bloop's."""
    out = np.zeros(int(0.7 * SR))
    for k in range(3):
        d = 0.12
        t = np.arange(int(d * SR)) / SR
        f0 = rng.uniform(260, 420)
        f = f0 * (1 + 2.2 * t / d)
        x = np.sin(TAU * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int((k * 0.16 + rng.uniform(0, 0.04)) * SR)
        out[i:i + len(x)] += x * (1 - 0.2 * k)
    return (out / (np.abs(out).max() + 1e-9) * 0.5).astype(np.float32)


EXTRA_SFX = {"bloop": (bloop, 0.55)}
