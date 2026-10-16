"""Armenian clip "ending": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.pond_or_tree.clips.ending.story import *  # noqa: F401,F403
from interactive.pond_or_tree.clips.ending import story as _en
from interactive.pond_or_tree_hy.lines import armenian

PLACE = "Interactive/pond_or_tree_hy"
LANG = "hy"
FILM_SECONDS = 31  # English clip + the extra time the Armenian lines take
SCRIPT = armenian("ending", _en.SCRIPT)
