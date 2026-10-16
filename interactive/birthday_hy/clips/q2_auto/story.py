"""Armenian clip "q2_auto": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.q2_auto.story import *  # noqa: F401,F403
from interactive.birthday.clips.q2_auto import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 6  # English clip + the extra time the Armenian lines take
SCRIPT = armenian("q2_auto", _en.SCRIPT)
