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
    _story = importlib.import_module(f"films.{name}.story")
    _scenes = importlib.import_module(f"films.{name}.scenes")


def scenes():
    return _scenes


def __getattr__(attr):
    if _story is not None and hasattr(_story, attr):
        return getattr(_story, attr)
    return getattr(common, attr)
