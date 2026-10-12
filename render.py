"""Render the film: timeline -> audio -> frames (in parallel) -> final video.

    python3 render.py --film rome        # full film -> out/rome.mp4  (default film: moonfish)
    python3 render.py --still 130        # one frame at t=130s -> out/still_130.png
    python3 render.py --stills 12        # contact sheet of 12 frames across the film
    python3 render.py --from 95 --to 160 # render just a stretch (for checking a scene)
    python3 render.py --premium          # prefer Premium/Enhanced macOS voices
"""
import argparse
import os
import pickle
import subprocess
import sys
import time
from multiprocessing import Pool, cpu_count

from PIL import Image

import audio
import draw as D
import film as story
import timeline

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")
FADE = 0.6

_tl = None


def cuts(tl):
    """Times where the picture fades through black."""
    out = [0.0, float(story.FILM_SECONDS)]
    sc = story.scenes()
    for name in story.SCENES[1:]:
        if name not in getattr(sc, "CONTINUOUS", ()):
            out.append(tl.scenes[name][0])
    for event_id in getattr(sc, "EXTRA_CUTS", ()):
        out.append(tl.t(event_id))
    return out


def frame(tl, i, cut_times):
    t = i / story.FPS
    name = tl.scene_at(t)
    img = story.scenes().SCENE_FUNCS[name](tl, t).finish()
    k = min(min(1.0, abs(t - c) / FADE) for c in cut_times)
    if k < 1:
        img = Image.blend(Image.new("RGB", img.size), img, k)
    line = tl.line_at(t)
    if line:
        D.subtitle(img, line.text, story.SUBTITLE_COLORS[line.who])
    return img


def _init(name, path):
    global _tl
    story.load(name)
    with open(path, "rb") as f:
        _tl = pickle.load(f)


def _render_chunk(job):
    k, a, b, path = job
    cut_times = cuts(_tl)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{story.WIDTH}x{story.HEIGHT}", "-r", str(story.FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path],
        stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(frame(_tl, i, cut_times).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on chunk {k}")
    return b - a


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--film", default="moonfish", help="folder name under films/")
    p.add_argument("--tts", default="auto", choices=["auto", "kokoro", "say", "espeak"])
    p.add_argument("--premium", action="store_true", help="prefer Premium/Enhanced macOS voices")
    p.add_argument("--still", type=float, help="render one frame at this time (s)")
    p.add_argument("--stills", type=int, help="contact sheet of N frames across the film")
    p.add_argument("--from", dest="t0", type=float, default=0.0)
    p.add_argument("--to", dest="t1", type=float, default=None)
    p.add_argument("--jobs", type=int, default=cpu_count())
    p.add_argument("-o", "--output")
    a = p.parse_args()
    story.load(a.film)
    if a.t1 is None:
        a.t1 = float(story.FILM_SECONDS)
    a.output = a.output or os.path.join(OUT, f"{a.film}.mp4")
    build = os.path.join(BUILD, a.film)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(build, exist_ok=True)
    started = time.time()

    tl = timeline.build(a.tts, a.premium)

    if a.still is not None:
        path = os.path.join(OUT, f"{a.film}_still_{a.still:g}.png")
        frame(tl, int(a.still * story.FPS), cuts(tl)).save(path)
        print(path)
        return
    if a.stills:
        n = a.stills
        cols = 4
        rows = (n + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 640, rows * 360))
        for k in range(n):
            t = (k + 0.5) * story.FILM_SECONDS / n
            img = frame(tl, int(t * story.FPS), cuts(tl)).resize((640, 360))
            sheet.paste(img, ((k % cols) * 640, (k // cols) * 360))
        path = os.path.join(OUT, f"{a.film}_contact_sheet.png")
        sheet.save(path)
        print(path)
        return

    full = a.t0 == 0 and a.t1 == story.FILM_SECONDS
    wav = os.path.join(build, "mix.wav")
    secs = audio.mix(tl, wav)
    timeline.write_srt(tl, os.path.splitext(a.output)[0] + ".srt")
    print(f"[audio] {secs:.3f}s mixed  ({time.time() - started:.0f}s)")

    tlpath = os.path.join(build, "timeline.pkl")
    with open(tlpath, "wb") as f:
        pickle.dump(tl, f)
    f0, f1 = int(round(a.t0 * story.FPS)), int(round(a.t1 * story.FPS))
    nchunks = a.jobs * 3
    step = (f1 - f0 + nchunks - 1) // nchunks
    jobs = []
    for k in range(nchunks):
        s, e = f0 + k * step, min(f1, f0 + (k + 1) * step)
        if s < e:
            jobs.append((k, s, e, os.path.join(build, f"chunk_{k:03}.mp4")))
    done = 0
    with Pool(a.jobs, initializer=_init, initargs=(a.film, tlpath)) as pool:
        for n in pool.imap_unordered(_render_chunk, jobs):
            done += n
            print(f"\r[video] {done}/{f1 - f0} frames", end="", flush=True)
    print(f"  ({time.time() - started:.0f}s)")

    listing = os.path.join(build, "chunks.txt")
    with open(listing, "w") as f:
        for _, _, _, path in jobs:
            f.write(f"file '{path}'\n")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing]
    if full:
        cmd += ["-i", wav]
    else:
        cmd += ["-ss", str(f0 / story.FPS), "-t", str((f1 - f0) / story.FPS), "-i", wav]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", a.output]
    subprocess.run(cmd, check=True)
    for _, _, _, path in jobs:
        os.remove(path)

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", a.output], capture_output=True, text=True).stdout.strip()
    print(f"[done] {a.output}  duration={dur}s  total time {time.time() - started:.0f}s")
    if full and abs(float(dur) - story.FILM_SECONDS) > 0.05:
        sys.exit(f"Duration is {dur}s, expected {story.FILM_SECONDS}s")


if __name__ == "__main__":
    main()
