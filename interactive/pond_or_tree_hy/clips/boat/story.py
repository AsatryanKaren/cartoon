"""Armenian clip "boat": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.boat.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.boat import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 35  # English clip + the extra time the Armenian lines take
SCRIPT = armenian("boat", _en.SCRIPT)
