"""Whiskers & Luna's World, Episode 1: "Our Planet".

On the windowsill Luna spins her old globe -- a little model of the Earth.
Whiskers wants to nap on it. The globe glows and the friends' nap cushion
flies them up into space, where they see that the Earth really is a ball
floating in space; the ball flattens out into the magic map (a map is the
globe made flat), with "You are here", a compass and "Never Eat Soggy
Waffles". So much blue! In the middle of the ocean they meet Grandpa Shelby,
a wise old sea turtle who has swum all the way around the world: almost three
quarters of the Earth is water. They ride his shell east around the world --
and at the edge of the map Whiskers panics that they will fall off the world.
They pop out on the other side: on a round Earth there is no edge.

Facts: 1) the Earth is round, like a ball; 2) almost three quarters of the
Earth is water; 3) maps show four directions: north, south, east and west.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e01_our_planet import sounds

TITLE = "01 - Our Planet"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "sea", "swim", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Grandpa Shelby: a wise, kind, very old sea turtle with spectacles and a white beard
    "shelby": Voice("bm_lewis", 0.98, -1, ["Ralph"], 160, "en-gb+m4", 30, 145),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "shelby": (180, 238, 190)}

MOODS = {**K.KIT_MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "sea": "w_sea", "swim": "w_map",
         "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.5, "w_map"), ("w_edge", 0.0, "w_funny"), ("w_globe", 0.0, "w_sea"),
              ("w_purpose", 0.3, "w_funny")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode one. Our Planet!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("spin", 0.15)]),
    S("narrator", "One sunny morning, Luna was spinning her old globe.", "sill", "s_narr", [("spin", 0.2)]),
    S("whiskers", "Luna, why do you keep spinning that ball? Can I nap on it?", "sill", "s_nap"),
    S("luna", "It's a globe, Whiskers! A little model of our whole world, the Earth.",
      "sill", "s_globe"),
    S("pip", "So the Earth is round? Like a ball?", "sill", "s_round"),
    S("luna", "Yes! The Earth is a giant ball, floating in space.", "sill", "s_space", [("sparkle", 0.4)]),
    A("sill", 1.0, "s_space2"),
    S("whiskers", "But the garden is flat. I've napped on all of it.", "sill", "s_flat"),
    S("luna", "That's because the Earth is so big, it looks flat when you're standing on it.", "sill", "s_big",
      [("pop", 0.1)]),
    A("sill", 2.2, "s_zoom"),
    S("luna", "Want to see the whole world? Hold on to the cushion!", "sill", "s_hold", [("spin", 0.6)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.8, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Whoosh! Up, up into space they flew!", "map", "m_narr"),
    S("pip", "Wow! The Earth really is a ball!", "map", "m_wow"),
    S("luna", "Now watch. A map is the globe, flattened out, so we see the whole world at once.",
      "map", "m_flatline"),
    A("map", 2.6, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "Look, here's our home. You are here!", "map", "m_home", [("pop", 0.55)]),
    A("map", 0.8, "m_here"),
    S("narrator", "Every map has four directions.", "map", "m_dirs", [("pop", 0.6)]),
    A("map", 0.8, "m_compass", [("sparkle", 0.1)]),
    S("luna", "North is up at the top. South is down at the bottom.", "map", "m_ns", [("ding", 0.1), ("ding", 0.6)]),
    S("luna", "East is this way, and west is that way.", "map", "m_ew", [("ding", 0.1), ("ding", 0.6)]),
    S("pip", "Never Eat Soggy Waffles! North, east, south, west!", "map", "m_nesw",
      [("pop", 0.05), ("pop", 0.17), ("pop", 0.29), ("pop", 0.41)]),
    S("whiskers", "I would never eat soggy waffles. Crispy ones, though...", "map", "m_waffle"),
    A("map", 0.9, "m_laugh"),
    S("pip", "Hey, why is there so much blue everywhere?", "map", "m_blue"),
    S("luna", "Blue means water. Let's go and find out!", "map", "m_go"),
    A("map", 3.2, "m_path", [("whoosh", 0.05), ("whoosh", 0.75)]),

    # ------------------------------------------------------------------- sea
    A("sea", 1.6, "sea_land", [("splash", 0.5)]),
    S("narrator", "They landed far out in the big blue ocean.", "sea", "sea_narr"),
    A("sea", 1.6, "sea_bubbles", [("bloop", 0.1), ("bloop", 0.4), ("bloop", 0.7)]),
    S("shelby", "Well, hello there, little travellers! Welcome to my ocean.", "sea", "sea_hello", [("splash", 0.0)]),
    S("whiskers", "Aaah! A talking rock!", "sea", "sea_rock"),
    S("shelby", "I'm not a rock! I'm Grandpa Shelby, the oldest turtle in the sea.", "sea", "sea_name"),
    S("shelby", "I swam all the way around the world. I kept going the same way, and came back home!", "sea", "sea_around"),
    S("luna", "Because the Earth is round!", "sea", "sea_round"),
    A("sea", 2.6, "sea_loop", [("sparkle", 0.85)]),
    S("pip", "Grandpa Shelby, is there really that much water?", "sea", "sea_much"),
    S("shelby", "Oh, yes. If you cut the Earth into four parts, almost three of them would be water.",
      "sea", "sea_four", [("pop", 0.85)]),
    A("sea", 2.6, "sea_pie", [("ding", 0.0), ("ding", 0.3), ("ding", 0.6)]),
    S("shelby", "Only one part is land.", "sea", "sea_land1", [("pop", 0.3)]),
    S("whiskers", "So the world is mostly... fish soup?", "sea", "sea_soup"),
    A("sea", 0.8, "sea_laugh"),
    S("shelby", "Ho ho! Climb on! Let's swim around the world!", "sea", "sea_climb"),
    A("sea", 1.6, "sea_hop", [("whoosh", 0.2), ("pop", 0.55), ("pop", 0.75)]),

    # ------------------------------------------------------------------ swim
    A("swim", 1.8, "w_go", [("splash", 0.1)]),
    S("narrator", "So they swam east, past Africa and Australia, across the giant Pacific.",
      "swim", "w_narr"),
    A("swim", 1.4, "w_more"),
    S("whiskers", "Stop! The edge of the map! We'll fall off the world!", "swim", "w_edge"),
    A("swim", 3.0, "w_fall", [("whoosh", 0.3), ("whoosh", 0.62), ("pop", 0.72), ("splash", 0.78)]),
    S("pip", "Whiskers, you can open your eyes now.", "swim", "w_eyes"),
    S("whiskers", "Am I in space?", "swim", "w_space"),
    S("luna", "No! We came out on the other side. The two edges of the map join up!", "swim", "w_join"),
    A("swim", 1.4, "w_joinact", [("pop", 0.1), ("pop", 0.4)]),
    A("swim", 2.6, "w_globe", [("spin", 0.1), ("sparkle", 0.7)]),
    S("shelby", "A round Earth has no edge. Keep going, and you come back to the start.",
      "swim", "w_noedge"),
    S("whiskers", "I knew that. I screamed on purpose. It was a sailor song.", "swim", "w_purpose"),
    A("swim", 1.2, "w_laugh"),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. The Earth is round, like a ball.", "remember", "r_f1", [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. Almost three quarters of the Earth is water.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Maps show four directions. North, south, east and west.", "remember", "r_f3",
      [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Is the Earth flat like a pancake, or round like a ball?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Round like a ball! Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Is there more land, or more water on Earth?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "More water! Almost three quarters of the Earth is water.", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.6, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("pip", "Let's swim around the world again tomorrow!", "home", "h_pip", [("spin", 0.3)]),
    S("whiskers", "Sure. But first, a nap. All the way around this cushion.", "home", "h_nap"),
    A("home", 1.4, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, the seven continents! Goodnight, round world.", "home", "h_next", [("sparkle", 0.2)]),
    A("home", 3.0, "h_end"),
]
