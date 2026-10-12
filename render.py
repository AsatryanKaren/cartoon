"""Render the cat cartoon: python render.py [--preview t1 t2 ...]"""
import multiprocessing as mp
import os
import subprocess
import sys

import numpy as np
from PIL import Image

from draw import H, S, W, C, subtitle
from scenes import DRAW
from story import NAMES
from timeline import BUILD, DURATION, FPS, ROOT, build

TOTAL_FRAMES = int(round(DURATION * FPS))
CHUNK = 360
SCENES = None


def scene_at(t):
    for sc in SCENES:
        if sc.start <= t < sc.end:
            return sc
    return SCENES[-1]


def render(t):
    sc = scene_at(t)
    lt = t - sc.start
    img = Image.new('RGB', (W * S, H * S))
    c = C(img)
    DRAW[sc.id](c, lt, sc)
    subtitle(c, sc.line_at(lt), NAMES)
    small = img.reduce(S)
    fade = min(1.0, t / 1.0, (DURATION - t) / 1.5)
    for b in SCENES[1:]:
        d = abs(t - b.start)
        if d < 0.35:
            fade *= d / 0.35
    if fade < 1:
        arr = (np.asarray(small).astype(np.float32) * max(0.0, fade)).astype(np.uint8)
        small = Image.fromarray(arr)
    return small


def render_chunk(i):
    f0, f1 = i * CHUNK, min(TOTAL_FRAMES, (i + 1) * CHUNK)
    out = os.path.join(BUILD, 'chunks', f'c{i:03d}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                          '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(render(f / FPS).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    return out


def main():
    global SCENES
    SCENES, unit, fixed = build()
    if len(sys.argv) > 2 and sys.argv[1] == '--preview':
        os.makedirs(os.path.join(BUILD, 'preview'), exist_ok=True)
        for s in sys.argv[2:]:
            t = float(s)
            render(t).save(os.path.join(BUILD, 'preview', f'p_{t:06.1f}.png'))
        return
    from audio import build_audio
    os.makedirs(os.path.join(BUILD, 'chunks'), exist_ok=True)
    wav = os.path.join(BUILD, 'audio.wav')
    build_audio(SCENES, wav)
    n = (TOTAL_FRAMES + CHUNK - 1) // CHUNK
    with mp.get_context('fork').Pool(max(1, os.cpu_count() - 2)) as pool:
        files = []
        for k, f in enumerate(pool.imap(render_chunk, range(n))):
            files.append(f)
            print(f'chunk {k + 1}/{n}', flush=True)
    lst = os.path.join(BUILD, 'chunks.txt')
    with open(lst, 'w') as fh:
        fh.writelines(f"file '{f}'\n" for f in files)
    out = os.path.join(ROOT, 'whiskers_and_the_moon_fish.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav,
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DURATION),
                    '-movflags', '+faststart', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
