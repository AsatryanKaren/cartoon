"""Armenian clip "balloon": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.balloon.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.balloon import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 32
SCRIPT = armenian("balloon", _en.SCRIPT)
