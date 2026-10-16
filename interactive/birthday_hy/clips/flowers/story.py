"""Armenian clip "flowers": the English clip's picture and timing, Armenian lines (see ../../lines.py)."""
from interactive.birthday.clips.flowers.story import *  # noqa: F401,F403
from interactive.birthday.clips.flowers import story as _en
from interactive.birthday_hy.lines import armenian

PLACE = "Interactive/birthday_hy"
LANG = "hy"
FILM_SECONDS = 30
SCRIPT = armenian("flowers", _en.SCRIPT)
