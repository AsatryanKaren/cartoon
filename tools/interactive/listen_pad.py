"""Write a soft, seamlessly looping 4 s pad (all partials whole cycles in 4 s) and put it on a listen clip."""
import subprocess, sys, wave
import numpy as np
SR, N = 48000, 4 * 48000
t = np.arange(N) / SR
x = np.zeros(N)
for f, g in ((174.5, 1.0), (220.0, 0.8), (261.5, 0.7), (349.25, 0.45), (87.25, 0.5)):
    x += g * (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t))
x *= 0.85 + 0.15 * np.sin(2 * np.pi * t / 2.0)
x = x / np.abs(x).max() * 0.12
pcm = (x * 32767).astype(np.int16)
wav = sys.argv[2]
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
mp4 = sys.argv[1]
tmp = mp4 + ".tmp.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-t", "4", "-movflags", "+faststart", tmp], check=True)
subprocess.run(["mv", tmp, mp4], check=True)
