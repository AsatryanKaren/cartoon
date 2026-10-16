"""Armenian clip "ending": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.ending.story import *  # noqa: F401,F403
from interactive.birthday.clips.ending import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 29  # English clip + the extra time the Armenian lines take
SCRIPT = armenian("ending", _en.SCRIPT)
