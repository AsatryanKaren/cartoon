"""Whiskers & Luna's World, Episode 10 (season finale): "Day and Night, Earth and Sun".

Early one morning the Sun is coming up and Whiskers asks where it was all night. Professor
Hoot, a wise owl on her way to bed, flies in: the Sun goes nowhere -- Pip shines a torch on
Luna's globe (the Sun), the lit side has day, the dark side night, and one turn of the Earth
takes a day, 24 hours. In space they watch home turn into the sunlight (sunrise) and away
(sunset): the Sun only looks like it moves because we spin. Whiskers tries to stop the Earth
for sunny naps forever and gets spun off, dizzy. On the day-and-night magic map they fly from
morning at home to night in Hawaii, where Grandpa Shelby (Episode 1) is going to bed: every
place has its own time. Whiskers spots the "Moon Fish" in the sea again (Film 1 callback) and
this time keeps his paws dry. Up at the Moon: it has no light of its own, sunlight bounces
off it; it goes around the Earth about once a month, so we see more or less of its sunny
side (phases); and the Earth goes around the Sun once a year, 365 days -- one trip each
birthday. Finale: a look back at the whole season, then the friends on the windowsill under
the stars. "The End of Season 1 -- see you next season!"

Facts: 1) the Earth spins around once a day, making day and night; 2) the Earth goes around
the Sun once a year; 3) the Moon shines with light from the Sun.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e10_day_night import sounds

TITLE = "10 - Day and Night, Earth and Sun"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "space", "map", "hawaii", "moon", "remember", "quiz", "recap", "home"]

CAST = {
    **CAST,
    # Professor Hoot: a wise, warm old owl with spectacles and a little scholar's cap
    "hoot": Voice("af_bella", 0.93, -2, ["Samantha"], 165, "en-us+f4", 40, 150),
    # Grandpa Shelby, the old sea turtle from Episode 1 (same voice)
    "shelby": Voice("bm_lewis", 0.98, -1, ["Ralph"], 160, "en-gb+m4", 30, 145),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "hoot": (255, 226, 140), "shelby": (180, 238, 190)}

MOODS = {**K.KIT_MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "space": "w_wonder", "map": "w_map", "hawaii": "w_sea",
         "moon": "w_wonder", "remember": "w_remember", "quiz": "w_quiz", "recap": "w_intro", "home": "w_night"}
MUSIC_CUES = [("p_stop", 0.4, "w_funny"), ("p_friend", 0.0, "w_wonder"), ("ha_fish", 0.0, "w_funny"),
              ("ha_secret", 0.0, "w_sea")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode ten. Day and Night, Earth and Sun!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("spin", 0.15)]),
    S("narrator", "One morning, the Sun was just coming up.", "sill", "s_narr"),
    S("whiskers", "Good morning, Sun. Where were you all night? Napping somewhere?", "sill", "s_where"),
    A("sill", 1.6, "s_owl", [("whoosh", 0.1), ("hoot", 0.7)]),
    S("hoot", "Hoo-hoo! Good morning! I'm Professor Hoot. I was up all night, so now it's my bedtime.",
      "sill", "s_hello"),
    S("hoot", "The Sun went nowhere! Pip, shine this torch on the globe.", "sill", "s_torch",
      [("click", 0.85)]),
    A("sill", 1.2, "s_beam"),
    S("luna", "The side facing the light has day. The other side has night!", "sill", "s_daynight",
      [("ding", 0.1), ("ding", 0.6)]),
    S("hoot", "The Earth spins around once a day. One turn takes twenty-four hours.",
      "sill", "s_spin", [("spin", 0.2)]),
    A("sill", 2.6, "s_turn", [("spin", 0.05), ("chime", 0.92)]),
    S("whiskers", "Twenty-four hours? That's how long my naps are.", "sill", "s_nap"),
    A("sill", 0.9, "s_laugh"),
    S("hoot", "Hoo! Come and see it from space!", "sill", "s_come", [("spin", 0.6)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ----------------------------------------------------------------- space
    A("space", 1.6, "p_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("pip", "Wow! The Earth is half bright, half dark!", "space", "p_wow"),
    S("hoot", "The Earth spins like a top. Watch our home.", "space", "p_watch"),
    A("space", 1.4, "p_turn1"),
    S("luna", "Here comes the sunlight. Sunrise!", "space", "p_rise", [("ding", 0.3)]),
    A("space", 1.8, "p_turn2"),
    S("luna", "And now we turn away. Sunset!", "space", "p_set", [("ding", 0.3)]),
    S("pip", "So the Sun only looks like it moves, because we spin!", "space", "p_looks"),
    A("space", 0.6, "p_ok"),
    S("whiskers", "No more sunsets! I'll stop the Earth!", "space", "p_stop"),
    A("space", 3.4, "p_push", [("whoosh", 0.03), ("pop", 0.16), ("whoosh", 0.45), ("whoosh", 0.62),
                                 ("boing", 0.78)]),
    S("whiskers", "Wheee! I'm dizzy!", "space", "p_dizzy"),
    S("hoot", "Hoo! The Earth is far too big to stop.", "space", "p_big"),
    S("whiskers", "I knew that. I was testing it. On purpose.", "space", "p_purpose"),
    A("space", 1.0, "p_laugh"),
    S("hoot", "When it's day on one side of the world, it's night on the other. Let's visit a friend!",
      "space", "p_friend"),
    A("space", 1.0, "p_tomap", [("whoosh", 0.3), ("sparkle", 0.5)]),

    # ------------------------------------------------------------------- map
    A("map", 1.2, "m_open", [("sparkle", 0.2)]),
    S("narrator", "On the magic map, the night side was dark.", "map", "m_narr"),
    A("map", 1.2, "m_pins", [("pop", 0.15), ("pop", 0.6)]),
    A("map", 3.2, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ---------------------------------------------------------------- hawaii
    A("hawaii", 1.4, "ha_land", [("sparkle", 0.1), ("pop", 0.55)]),
    S("shelby", "Hello again, little travellers! It's bedtime here in Hawaii.", "hawaii", "ha_hello",
      [("bloop", 0.0)]),
    S("pip", "But at home, it's breakfast time!", "hawaii", "ha_break"),
    S("shelby", "Every place has its own time. Goodnight!", "hawaii", "ha_time"),
    A("hawaii", 2.4, "ha_split", [("ding", 0.1), ("ding", 0.45)]),
    S("whiskers", "Look, in the water! The Moon Fish is back!", "hawaii", "ha_fish"),
    A("hawaii", 1.4, "ha_wiggle"),
    S("luna", "Whiskers, it's only the Moon, shining in the water!", "hawaii", "ha_remember"),
    S("whiskers", "I know. This time, my paws stay dry.", "hawaii", "ha_dry"),
    S("hoot", "And the Moon has a secret. Up we go!", "hawaii", "ha_secret",
      [("whoosh", 0.85)]),
    A("hawaii", 1.0, "ha_up", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ moon
    A("moon", 1.2, "mo_open", [("sparkle", 0.2)]),
    S("hoot", "The Moon makes no light. Sunlight bounces off it, like a mirror.", "moon", "mo_mirror"),
    A("moon", 1.6, "mo_rays", [("sparkle", 0.3)]),
    S("pip", "So moonlight is really sunlight!", "moon", "mo_pip"),
    S("hoot", "The Moon goes around the Earth about once a month.", "moon", "mo_month"),
    A("moon", 2.6, "mo_orbit"),
    S("luna", "So we see more or less of its sunny side. That's why it changes shape!", "moon", "mo_phase"),
    A("moon", 2.0, "mo_shapes", [("ding", 0.1), ("ding", 0.4), ("ding", 0.7)]),
    S("hoot", "And the Earth goes around the Sun once a year. Three hundred and sixty-five days!",
      "moon", "mo_year"),
    A("moon", 3.2, "mo_trip", [("whoosh", 0.1), ("chime", 0.92)]),
    S("pip", "So every birthday, I've been once around the Sun!", "moon", "mo_bday", [("pop", 0.6)]),
    S("whiskers", "Then I want birthday cake. In space.", "moon", "mo_cake"),
    A("moon", 0.9, "mo_laugh"),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. The Earth spins around once a day. That makes day and night.", "remember",
      "r_f1", [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. The Earth goes around the Sun once a year.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. The Moon shines with light from the Sun.", "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! At night, is the Sun gone, or is our side facing away from it?",
      "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Facing away! The Sun never stops shining.", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Where does moonlight come from?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "From the Sun! The Moon is like a mirror.", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ----------------------------------------------------------------- recap
    A("recap", 1.0, "rc_open", [("sparkle", 0.2)]),
    S("narrator", "What a season! Let's look back.", "recap", "rc_1"),
    S("narrator", "Our round planet, seven continents, five oceans, mountains, and rivers.", "recap", "rc_2",
      [("pop", 0.05), ("pop", 0.25), ("pop", 0.45), ("pop", 0.62), ("pop", 0.82)]),
    S("narrator", "Deserts, rainforests, the frozen poles, the seasons, and day and night!", "recap", "rc_3",
      [("pop", 0.05), ("pop", 0.24), ("pop", 0.44), ("pop", 0.64), ("pop", 0.82)]),
    A("recap", 2.4, "rc_hold", [("chime", 0.1), ("sparkle", 0.3)]),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "e_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("hoot", "Hoo! Now it's my turn to be awake. Goodnight, friends!", "home", "e_hoot", [("hoot", 0.0)]),
    S("luna", "Thank you for exploring the world with us!", "home", "e_luna"),
    S("whiskers", "Next season? Sure. After a nap. A whole season long.", "home", "e_nap"),
    A("home", 1.2, "e_curl", [("purr", 0.15)]),
    S("narrator", "The end of season one. See you next season!", "home", "e_end",
      [("sparkle", 0.2)]),
    A("home", 3.0, "e_fin"),
]
