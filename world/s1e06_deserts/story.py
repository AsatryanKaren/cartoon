"""Whiskers & Luna's World, Episode 6: "Deserts".

A hot sunny morning on the windowsill: Whiskers wants the sunniest, warmest place on Luna's globe
for a nap. Luna points to the Sahara -- a desert. Is it the heat that makes a desert? No: a desert
is a place where very little rain falls (an inset shows a rain cloud that only lets one drop fall).
The friends fly onto the magic map, where the deserts of the world glow yellow; the biggest hot
desert is the Sahara, which covers about a third of Africa ("the world's biggest litter box!").
On a sand dune in the Sahara they see how the wind blows the sand into waves and hills, and meet
Humphrey the camel. Thirsty Whiskers is sure the hump is full of water and pokes a straw into it:
nothing comes out -- the hump is full of FAT, a food store, and a camel can go many days without
drinking. Humphrey carries them to an oasis, a green spot with water and palm trees, where Fizz
the fennec fox shows how her huge ears let the heat out (and hear a beetle under the sand). When
the sun sets the desert gets cold -- no clouds to keep the warmth in -- and under the stars
Humphrey tells them the biggest desert of all is icy Antarctica, because so little snow falls
there (a callback to Episode 2).

Facts: 1) a desert is a place where very little rain falls; 2) the Sahara, in Africa, is the
biggest hot desert; 3) a camel's hump stores fat, not water.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e06_deserts import sounds

TITLE = "06 - Deserts"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "dunes", "oasis", "night", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Humphrey: a big, slow, kind and very calm camel with long eyelashes
    "humphrey": Voice("bm_daniel", 0.9, -2, ["Daniel"], 150, "en-gb+m2", 32, 140),
    # Fizz: a tiny, quick, bouncy fennec fox with enormous ears
    "fizz": Voice("af_kore", 1.08, 3, ["Samantha"], 190, "en-us+f2", 75, 175),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "humphrey": (250, 214, 140), "fizz": (255, 180, 120)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "dunes": "w_desert", "oasis": "w_sea",
         "night": "w_night", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("d_straw", 0.0, "w_funny"), ("d_hump", 0.0, "w_desert"),
              ("o_ears", 0.0, "w_funny"), ("o_cold", 0.0, "w_sea"), ("n_ant", 0.0, "w_wonder")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode six. Deserts!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.2, "s_open", [("spin", 0.15)]),
    S("whiskers", "Luna, find me the warmest, sunniest place on your globe. For a nap.",
      "sill", "s_warm"),
    S("luna", "Hmm. How about a desert? Like the Sahara, here in Africa!", "sill", "s_sahara",
      [("spin", 0.2), ("pop", 0.75)]),
    S("pip", "What makes a desert a desert? Is it the heat?", "sill", "s_what"),
    S("luna", "Nope! A desert is a place where very little rain falls. Hardly ever!", "sill", "s_rain",
      [("pop", 0.3)]),
    A("sill", 2.0, "s_rainact", [("drip", 0.45)]),
    S("whiskers", "No rain? No baths? Perfect!", "sill", "s_bath"),
    S("luna", "Hold on to the cushion!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.4, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Up into space they flew!", "map", "m_narr", [("spin", 0.5)]),
    A("map", 1.8, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "See the yellow patches? Those are deserts, all over the world.",
      "map", "m_yellow", [("ding", 0.45), ("ding", 0.6), ("ding", 0.75)]),
    A("map", 1.4, "m_zoom", [("whoosh", 0.1)]),
    S("luna", "This giant one is the Sahara. The biggest hot desert in the world!", "map", "m_big",
      [("ding", 0.3)]),
    S("pip", "Wow! It covers about a third of Africa!", "map", "m_third", [("pop", 0.3)]),
    A("map", 1.0, "m_thirdact"),
    S("whiskers", "So it's the world's biggest litter box.", "map", "m_litter"),
    S("luna", "Whiskers!", "map", "m_luna"),
    A("map", 0.9, "m_laugh"),
    A("map", 2.5, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ----------------------------------------------------------------- dunes
    A("dunes", 1.6, "d_land", [("sandpuff", 0.5)]),
    S("narrator", "They landed in the Sahara. Phew, it was hot!", "dunes", "d_narr"),
    S("pip", "Look! The sand is all in waves!", "dunes", "d_waves"),
    A("dunes", 1.4, "d_gust", [("wind", 0.0)]),
    S("humphrey", "Those are sand dunes. The wind blows the sand into hills.",
      "dunes", "d_dunes", [("wind", 0.4)]),
    A("dunes", 1.4, "d_windact", [("ding", 0.5)]),
    S("humphrey", "Hello! I'm Humphrey the camel. Welcome to my desert.", "dunes", "d_hello"),
    S("luna", "Humphrey, does it ever rain here?", "dunes", "d_ask"),
    S("humphrey", "Hardly ever. Some years, not a single drop!", "dunes", "d_drop"),
    S("whiskers", "Oh, I know! Your hump is full of water!", "dunes", "d_know"),
    A("dunes", 2.2, "d_straw", [("whoosh", 0.1), ("pop", 0.42), ("slurp", 0.55)]),
    S("whiskers", "Hmm. Nothing's coming out.", "dunes", "d_nothing"),
    S("humphrey", "Hee hee, that tickles! My hump isn't full of water. It's full of fat!",
      "dunes", "d_fat", [("boing", 0.05)]),
    A("dunes", 2.2, "d_hump", [("pop", 0.1), ("ding", 0.6)]),
    S("humphrey", "The fat is my food store. And I can go many days without a drink.",
      "dunes", "d_store"),
    S("whiskers", "I knew that. I was testing your hump on purpose. It passed.", "dunes", "d_purpose"),
    A("dunes", 0.9, "d_laugh"),
    S("humphrey", "Hop on! I know a green place.", "dunes", "d_hop"),
    A("dunes", 2.0, "d_ride", [("whoosh", 0.1), ("pop", 0.3), ("pop", 0.45)]),

    # ----------------------------------------------------------------- oasis
    A("oasis", 1.6, "o_open", [("sparkle", 0.4)]),
    S("narrator", "Over the dunes, they found an oasis.", "oasis", "o_narr"),
    S("luna", "An oasis is a green spot in the desert, with water and palm trees!", "oasis", "o_what",
      [("pop", 0.6)]),
    A("oasis", 1.2, "o_look", [("splash", 0.4)]),
    S("fizz", "Psst! Down here! I'm Fizz, a fennec fox!", "oasis", "o_fizz", [("pop", 0.05)]),
    S("pip", "Wow! Your ears are huge!", "oasis", "o_huge"),
    S("fizz", "My big ears let heat out, to keep me cool. And they hear everything!",
      "oasis", "o_cool"),
    A("oasis", 1.6, "o_ears", [("ding", 0.2), ("scritch", 0.6)]),
    S("whiskers", "Mine too. I can hear a tin of tuna open from three rooms away.", "oasis", "o_tuna"),
    A("oasis", 0.9, "o_laugh"),
    S("fizz", "But at night, the desert gets cold!", "oasis", "o_cold"),
    S("luna", "Cold? In the desert?", "oasis", "o_q"),
    S("fizz", "Yes! There are no clouds, like a blanket, to keep the warm in.", "oasis", "o_blanket"),
    A("oasis", 2.2, "o_sunset", [("whoosh", 0.3)]),

    # ----------------------------------------------------------------- night
    A("night", 1.4, "n_open", [("sparkle", 0.3)]),
    S("whiskers", "Brrr! Hot all day, and cold all night? Make up your mind, desert!", "night", "n_brr",
      [("chatter", 0.1)]),
    A("night", 1.6, "n_temp", [("ding", 0.2), ("ding", 0.7)]),
    S("pip", "But look at all the stars!", "night", "n_stars", [("sparkle", 0.2)]),
    A("night", 1.2, "n_starsact"),
    S("humphrey", "Here's a surprise. The biggest desert of all is icy Antarctica!",
      "night", "n_ant", [("pop", 0.6)]),
    S("luna", "But Antarctica is covered in ice!", "night", "n_ice"),
    S("humphrey", "Yes. But hardly any snow falls there. So it's a desert too!",
      "night", "n_snow"),
    A("night", 1.8, "n_antact", [("ding", 0.4)]),
    S("whiskers", "Then my water bowl is a desert. Nobody filled it.", "night", "n_bowl"),
    A("night", 0.9, "n_laugh"),
    A("night", 1.6, "n_off", [("sparkle", 0.1), ("whoosh", 0.4)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. A desert is a place where very little rain falls.", "remember", "r_f1",
      [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. The Sahara, in Africa, is the biggest hot desert.", "remember", "r_f2",
      [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. A camel's hump stores fat, not water.", "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! What makes a place a desert? Lots of heat, or very little rain?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Very little rain! Even cold places can be deserts.", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. What is inside a camel's hump? Water, or fat?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "Fat! Not water, Whiskers!", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("whiskers", "Ahh. Home. No more sand. Well... a little sand.", "home", "h_sand",
      [("sandpuff", 0.75)]),
    S("pip", "Goodnight, Humphrey! Goodnight, Fizz!", "home", "h_pip", [("spin", 0.3)]),
    A("home", 1.2, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, the rainforests! Goodnight, sandy world.", "home", "h_next",
      [("sparkle", 0.2)]),
    A("home", 2.6, "h_end"),
]
