"""The film being worked on. `film.load("rome")` selects films/rome/.

Other modules read film settings through this module (film.SCRIPT,
film.SCENES, film.CAST ...): the film's story.py first, then common.py.
"""
import importlib

import common

NAME = None
_story = None
_scenes = None


def load(name):
    global NAME, _story, _scenes
    NAME = name
    # "rome" -> films/rome/ ; "world/s1e01_our_planet" -> world/s1e01_our_planet/ (a series folder)
    pkg = name.replace("/", ".") if "/" in name else f"films.{name}"
    _story = importlib.import_module(f"{pkg}.story")
    _scenes = importlib.import_module(f"{pkg}.scenes")


def scenes():
    return _scenes


def __getattr__(attr):
    if _story is not None and hasattr(_story, attr):
        return getattr(_story, attr)
    return getattr(common, attr)
