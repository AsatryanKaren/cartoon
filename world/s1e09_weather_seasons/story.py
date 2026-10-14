"""Whiskers & Luna's World, Episode 9: "Weather and Seasons".

One windy autumn morning Whiskers sees the tree outside losing its leaves: is it broken? No, says
Luna, it's autumn, the seasons are changing. Whiskers wants to skip straight to summer (his sunny
nap spot), and Pip asks why there are seasons at all. The magic map takes them to a farm on a hill
near home, where Sir Rufus, a grand and slightly vain weather-vane rooster, spins on the barn roof:
the wind turns him, and wind is just moving air. Hazel the squirrel, busy saving acorns for winter,
shows them her tree through the year: blossom in spring, sunny long days in summer, orange falling
leaves in autumn, and snow in winter (water in the clouds freezes). Four seasons, round and round.
Is summer when the Earth gets closer to the Sun? "A common mistake!" Sir Rufus takes them to space:
the Earth travels around the Sun once a year, and it is tilted, always leaning the same way. When
our half leans toward the Sun we get strong sunshine and long days (summer); leaning away gives weak
sunshine and short days (winter). The distance stays about the same: it's the tilt. And when Europe
leans toward the Sun, Australia leans away, so summer in Europe is winter in Australia. Back at the
farm grey clouds bring rain (from clouds, like Drip in the water cycle). The sun comes out: rainbow
weather! Whiskers puts on his sunglasses and stares at the sun looking for the rainbow; Rufus tells
him to turn around -- the rainbow was behind him all along ("I looked at the sun on purpose. For my
suntan."). A far-away flash, then "one, two, three"... rumble: light is faster than sound, so the
flash comes first and the thunder after. At home, Pip notices that Luna's old globe is tilted too.

Facts: 1) there are four seasons: spring, summer, autumn and winter; 2) we have seasons because the
Earth is tilted; 3) a rainbow needs sun and rain together.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e09_weather_seasons import sounds

TITLE = "09 - Weather and Seasons"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "farm", "orbit", "weather", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Sir Rufus: a grand, dramatic, slightly vain weather-vane rooster
    "rufus": Voice("bm_fable", 1.0, 1, ["Daniel"], 176, "en-gb+m3", 50, 160),
    # Hazel: a quick, busy, cheerful squirrel who knows the seasons
    "hazel": Voice("af_river", 1.08, 2, ["Samantha"], 190, "en-us+f2", 72, 175),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "rufus": (255, 214, 120), "hazel": (240, 180, 140)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "farm": "w_farm", "orbit": "w_wonder",
         "weather": "w_rainy", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("f_spring", 0.0, "w_seasons"), ("f_whyq", 0.0, "w_farm"),
              ("w_sun", 0.0, "w_farm"), ("w_look", 0.3, "w_funny"), ("w_flash", 0.0, "w_rainy"),
              ("w_bye", 0.0, "w_farm")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode nine. Weather and Seasons!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("wind", 0.0)]),
    S("narrator", "One windy morning, the leaves were falling from the tree outside.", "sill", "s_narr",
      [("rustle", 0.3)]),
    S("whiskers", "Luna! The tree is losing all its leaves. Is it broken?", "sill", "s_broken"),
    S("luna", "It's not broken, silly. It's autumn! The seasons are changing.", "sill", "s_autumn",
      [("spin", 0.3)]),
    A("sill", 1.2, "s_autact", [("rustle", 0.1)]),
    S("whiskers", "Can we skip to summer? I miss my sunny nap spot.", "sill", "s_skip"),
    S("pip", "Why do we even have seasons?", "sill", "s_why"),
    S("luna", "Let's ask someone who knows all about weather. Hold on!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.4, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Up into the sky they flew!", "map", "m_narr", [("spin", 0.5)]),
    A("map", 2.4, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "Here's our home, in Europe. And nearby, on a hill, lives a very famous rooster.",
      "map", "m_farm", [("ding", 0.2)]),
    A("map", 2.8, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------ farm
    A("farm", 1.6, "f_land", [("wind", 0.0), ("pop", 0.7)]),
    S("narrator", "On top of a red barn stood a shiny weather-vane rooster.", "farm", "f_narr"),
    A("farm", 1.4, "f_spin", [("creak", 0.0), ("crow", 0.55)]),
    S("rufus", "Cock-a-doodle-doo! Behold! Sir Rufus, the finest weather rooster in the world!",
      "farm", "f_hello", [("fanfare", 0.0)]),
    S("pip", "Why are you spinning round?", "farm", "f_spinq"),
    S("rufus", "The wind spins me! Wind is just moving air. Feel it push!", "farm", "f_wind",
      [("creak", 0.3)]),
    A("farm", 1.8, "f_windact", [("wind", 0.0), ("rustle", 0.3)]),
    S("pip", "Whoa! I can't see the air, but I can feel it!", "farm", "f_feel"),
    S("hazel", "Excuse me! Coming through! Acorns for winter!", "farm", "f_hazel", [("scamper", 0.0)]),
    S("rufus", "Ah, Hazel. My squirrel friend knows the seasons best. After me, of course.", "farm",
      "f_friend"),
    S("hazel", "My tree changes all year. Watch! In spring, it grows flowers.", "farm", "f_spring",
      [("sparkle", 0.7)]),
    A("farm", 1.4, "f_springact", [("chirp", 0.2)]),
    S("hazel", "Summer is warm and sunny, with long days.", "farm", "f_summer", [("sparkle", 0.1)]),
    A("farm", 1.4, "f_summeract"),
    S("hazel", "In autumn, the leaves turn orange, and fall.", "farm", "f_autumn", [("rustle", 0.1)]),
    A("farm", 1.4, "f_autumnact", [("rustle", 0.2)]),
    S("hazel", "In winter, it's so cold that the water in the clouds freezes. Snow!", "farm", "f_winter",
      [("sparkle", 0.8)]),
    A("farm", 1.6, "f_winteract", [("chime", 0.1)]),
    S("luna", "Spring, summer, autumn, winter. Four seasons, and then round again!", "farm", "f_four",
      [("ding", 0.1), ("ding", 0.3), ("ding", 0.5), ("ding", 0.7)]),
    A("farm", 1.6, "f_fouract", [("spin", 0.1)]),
    S("whiskers", "But why can't it be summer all the time?", "farm", "f_whyq"),
    S("pip", "Is summer when the Earth gets closer to the Sun?", "farm", "f_closer"),
    S("rufus", "A common mistake! To space, my friends! I shall show you!", "farm", "f_space",
      [("crow", 0.75)]),
    A("farm", 1.8, "f_go", [("whoosh", 0.2), ("sparkle", 0.6)]),

    # ----------------------------------------------------------------- orbit
    A("orbit", 1.4, "o_open", [("sparkle", 0.2)]),
    S("narrator", "Far out in space, the Earth travels around the Sun.", "orbit", "o_narr"),
    S("rufus", "One trip around the Sun takes a whole year. And look! The Earth is tilted. It leans!",
      "orbit", "o_tilt", [("ding", 0.75)]),
    A("orbit", 1.6, "o_tiltact", [("pop", 0.1)]),
    S("luna", "And it always leans the same way, all the way round.", "orbit", "o_same"),
    A("orbit", 4.2, "o_trip", [("spin", 0.0), ("ding", 0.25), ("ding", 0.5), ("ding", 0.75), ("ding", 1.0)]),
    S("rufus", "When our half leans toward the Sun, we get strong sunshine and long days. Summer!",
      "orbit", "o_summer", [("sparkle", 0.85)]),
    A("orbit", 1.4, "o_summeract"),
    S("rufus", "When our half leans away, the sunshine is weak, and the days are short. Winter!",
      "orbit", "o_winter", [("chime", 0.85)]),
    A("orbit", 1.4, "o_winteract"),
    S("pip", "So it's not because the Earth gets closer?", "orbit", "o_not"),
    S("rufus", "No! The Earth stays about the same distance from the Sun. It's all about the tilt!",
      "orbit", "o_tiltans", [("ding", 0.5)]),
    A("orbit", 1.6, "o_dist", [("pop", 0.1), ("pop", 0.5)]),
    S("luna", "And when Europe leans toward the Sun, Australia leans away.", "orbit", "o_aus",
      [("whoosh", 0.0)]),
    A("orbit", 1.4, "o_ausact", [("pop", 0.1), ("pop", 0.5)]),
    S("rufus", "So, summer in Europe is winter in Australia!", "orbit", "o_swap", [("ding", 0.3)]),
    S("whiskers", "Then I'll spend every winter in Australia. Summer forever!", "orbit", "o_forever"),
    A("orbit", 1.0, "o_laugh"),
    A("orbit", 1.6, "o_back", [("whoosh", 0.2), ("sparkle", 0.6)]),

    # --------------------------------------------------------------- weather
    A("weather", 1.4, "w_open", [("rain", 0.2)]),
    S("narrator", "Back at the farm, grey clouds rolled in.", "weather", "w_narr", [("rain", 0.3)]),
    S("pip", "Rain! Where does rain come from?", "weather", "w_where", [("plip", 0.2)]),
    S("luna", "From clouds! Remember Drip? Water goes up into the clouds, and falls as rain.", "weather",
      "w_drip"),
    A("weather", 1.4, "w_dripact", [("plip", 0.2), ("plip", 0.6)]),
    S("rufus", "Aha! The sun is out, and it's still raining. Rainbow weather!", "weather", "w_sun",
      [("sparkle", 0.3)]),
    S("whiskers", "A rainbow? I'll look right at the sun. Sunglasses on!", "weather", "w_look",
      [("pop", 0.8)]),
    A("weather", 2.2, "w_squint", [("boing", 0.7)]),
    S("whiskers", "I can't see a rainbow. Just sun. Lots of sun.", "weather", "w_nothing"),
    S("rufus", "Turn around! The sun must be behind you, shining on the raindrops.", "weather", "w_turn"),
    A("weather", 2.4, "w_rainbow", [("whoosh", 0.1), ("sparkle", 0.35), ("chime", 0.45)]),
    S("whiskers", "I knew that. I looked at the sun on purpose. For my suntan.", "weather", "w_purpose"),
    A("weather", 1.0, "w_laugh"),
    A("weather", 1.0, "w_flash", [("zap", 0.1)]),
    S("pip", "Ooh! A flash of lightning, far away!", "weather", "w_flashq"),
    S("rufus", "Let's count. One... two... three...", "weather", "w_count"),
    A("weather", 1.4, "w_rumble", [("thunder", 0.0)]),
    S("hazel", "Thunder! Light is faster than sound. So you see the flash first, and hear the rumble after.",
      "weather", "w_thunder"),
    S("rufus", "It's far, far away. Farewell, my friends!", "weather", "w_bye", [("crow", 0.7)]),
    A("weather", 1.6, "w_byeact", [("whoosh", 0.3), ("sparkle", 0.6)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. There are four seasons: spring, summer, autumn and winter.", "remember",
      "r_f1", [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. We have seasons because the Earth is tilted.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. A rainbow needs sun and rain together.", "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Why do we have seasons? Because the Earth gets closer to the Sun? "
      "Or because the Earth is tilted?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Because the Earth is tilted! Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. What makes a rainbow? Snow and wind, or sun and rain?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "Sun and rain, together!", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("pip", "Look! Luna's globe is tilted too, just like the real Earth!", "home", "h_pip",
      [("spin", 0.4)]),
    A("home", 1.0, "h_tilt", [("ding", 0.2)]),
    S("whiskers", "Autumn's not so bad. Perfect weather for a cosy nap.", "home", "h_nap"),
    A("home", 1.2, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, day and night! Goodnight!", "home", "h_next", [("sparkle", 0.2)]),
    A("home", 2.6, "h_end"),
]
