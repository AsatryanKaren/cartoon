"""Shared by every film: format, script entry types, and the cast's voices.

Characters keep the same voices in every film. A film may add its own
characters by extending CAST and SUBTITLE_COLORS in its story.py:

    CAST = {**CAST, "pigeon": Voice("im_nicola", 1.0, 0, ["Alex"], 180, "en-us+m1", 50, 160)}
"""
from dataclasses import dataclass, field

FILM_SECONDS = 355          # 5:55, every film
FPS = 24
WIDTH, HEIGHT = 1280, 720

@dataclass
class Voice:
    kokoro: str          # Kokoro neural voice (natural sounding, free, offline) -- the main engine
    k_speed: float       # Kokoro speed, 1.0 = normal
    k_pitch: float       # pitch shift in semitones applied after Kokoro (0 = none)
    mac: list            # macOS `say` voices, most preferred first (Premium/Enhanced first)
    rate: int            # words per minute for `say`
    espeak: str          # last-resort espeak-ng voice (robotic)
    pitch: int           # espeak-ng pitch 0-99
    speed: int           # espeak-ng words per minute


# Characters keep these voices in every film. Engines, best first:
# kokoro (if installed, see README) > macOS say > espeak-ng.
# With `say` and --premium the first installed entry of `mac` is used; otherwise the last.
CAST = {
    "narrator": Voice("bm_george", 0.95, 0, ["Daniel (Premium)", "Daniel (Enhanced)", "Daniel"], 172,
                      "en-gb+m3", 38, 150),
    "whiskers": Voice("am_michael", 0.92, 0, ["Eddy (English (US))"], 168, "en-us+m7", 30, 150),
    "luna":     Voice("af_heart", 1.05, 0, ["Flo (English (US))"], 182, "en-us+f3", 62, 165),
    "pip":      Voice("af_sky", 1.1, 4, ["Junior"], 196, "en-us+f4", 92, 180),
}

SUBTITLE_COLORS = {
    "narrator": (255, 255, 255),
    "whiskers": (255, 205, 150),
    "luna": (200, 215, 255),
    "pip": (255, 195, 210),
}


@dataclass
class Say:
    who: str
    text: str
    scene: str
    id: str = None
    sfx: list = field(default_factory=list)


@dataclass
class Act:
    scene: str
    weight: float
    id: str = None
    sfx: list = field(default_factory=list)



# Optional per-film hooks (a film's story.py may override any of these):
MUSIC = {}          # scene name -> mood name (default: the scene's own name, see audio.MOODS)
MOODS = {}          # extra/override moods: name -> dict like audio.MOODS entries
MUSIC_CUES = []     # [(event_id, fraction, mood)] mood changes in the middle of a scene
EXTRA_SFX = {}      # name -> (function(rng) -> float32 samples at 48 kHz, gain)
