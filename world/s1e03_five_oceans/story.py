"""Whiskers & Luna's World, Episode 3: "The Five Oceans".

On the windowsill Whiskers asks why Luna's globe is so blue. Blue is water -- and all that
water is five big oceans. The friends fly up and the glowing Earth turns to show each ocean:
the giant Pacific (the biggest and deepest), the Atlantic, the Indian Ocean, the frozen Arctic
around the North Pole and the Southern Ocean around Antarctica. The globe flattens into the
magic map, with all five oceans glowing and joined into one big world ocean, and they fly to
the middle of the Pacific. There Bluebell, a singing blue whale (the biggest animal that ever
lived), says hello. Thirsty Whiskers laps up some sea water -- "Bleh! Salty!" -- and Bluebell
shows how rivers carry tiny bits of salt from the rocks into the sea, where the salt stays
when the water goes up into the clouds. The wind blows and makes waves. Bluebell takes them
down into the deep, deep Pacific (deeper than the tallest mountain is high). At a beach in the
evening, Nipper the crab shows them the tide going out: the Moon pulls the sea.

Facts: 1) there are five oceans; 2) the Pacific is the biggest and deepest ocean;
3) sea water is salty.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e03_five_oceans import sounds

TITLE = "03 - The Five Oceans"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "sea", "deep", "beach", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Bluebell: a huge, gentle, slow-speaking blue whale who sings
    "bluebell": Voice("bf_emma", 0.88, -2, ["Moira"], 150, "en-gb+f4", 35, 135),
    # Nipper: a small, quick, cheeky beach crab
    "nipper": Voice("am_puck", 1.08, 2, ["Fred"], 190, "en-us+m2", 70, 175),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "bluebell": (150, 232, 240), "nipper": (255, 160, 140)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "sea": "w_sea", "deep": "w_deep",
         "beach": "w_home", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("sea_sip", 0.0, "w_funny"), ("sea_salt1", 0.0, "w_sea"),
              ("b_moonfish", 0.0, "w_funny"), ("b_moon", 0.0, "w_wonder")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode three. The Five Oceans!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.2, "s_open", [("spin", 0.15)]),
    S("whiskers", "Luna, why is your globe so blue? Did it fall in the bath?", "sill", "s_blue"),
    S("luna", "Blue means water, Whiskers! Most of the Earth is covered by sea.", "sill", "s_sea",
      [("spin", 0.3)]),
    S("luna", "And all that sea is in five big oceans.", "sill", "s_five", [("pop", 0.4)]),
    A("sill", 1.0, "s_five2", [("ding", 0.1)]),
    S("pip", "Five oceans? Let's go and see them all!", "sill", "s_pip"),
    S("luna", "Hold on to the cushion!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.4, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Up into space they flew, and the Earth turned to show its oceans.", "map", "m_narr",
      [("spin", 0.5)]),
    A("map", 1.2, "m_turn1"),
    S("luna", "This giant one is the Pacific Ocean. It's the biggest and the deepest ocean of all!",
      "map", "m_pac", [("ding", 0.1)]),
    S("pip", "It covers almost half the world!", "map", "m_half"),
    A("map", 1.6, "m_turn2", [("spin", 0.1)]),
    S("luna", "Next, the Atlantic Ocean, between the Americas, and Europe and Africa.", "map", "m_atl",
      [("ding", 0.05)]),
    A("map", 1.4, "m_turn3", [("spin", 0.1)]),
    S("luna", "Here is the warm Indian Ocean.", "map", "m_ind", [("ding", 0.05)]),
    A("map", 1.4, "m_turn4", [("whoosh", 0.2)]),
    S("luna", "Up at the top, the Arctic Ocean. It's the smallest, and it's often frozen.", "map", "m_arc",
      [("ding", 0.05)]),
    A("map", 1.4, "m_turn5", [("whoosh", 0.2)]),
    S("luna", "And at the bottom, the cold Southern Ocean, all around Antarctica.", "map", "m_sou",
      [("ding", 0.05)]),
    A("map", 1.0, "m_count"),
    S("pip", "Pacific, Atlantic, Indian, Arctic, Southern. Five!", "map", "m_five",
      [("pop", 0.02), ("pop", 0.2), ("pop", 0.42), ("pop", 0.6), ("pop", 0.78)]),
    A("map", 2.6, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "And look! They are all joined up, like one big world ocean.", "map", "m_join",
      [("sparkle", 0.3)]),
    S("whiskers", "So where do we go? I vote for the biggest one. More room for napping.", "map", "m_vote"),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- sea
    A("sea", 1.4, "sea_land", [("splash", 0.5)]),
    S("narrator", "They landed in the middle of the Pacific Ocean.", "sea", "sea_narr"),
    A("sea", 1.6, "sea_song", [("whalesong", 0.0)]),
    S("pip", "What's that beautiful singing?", "sea", "sea_what"),
    A("sea", 1.6, "sea_rise", [("bloop", 0.0), ("spout", 0.55)]),
    S("bluebell", "Hellooo, little ones. I'm Bluebell, a blue whale.", "sea", "sea_hello"),
    S("bluebell", "Blue whales are the biggest animals that have ever lived. Even bigger than the dinosaurs!",
      "sea", "sea_big", [("pop", 0.6)]),
    A("sea", 1.6, "sea_bigact", [("ding", 0.1)]),
    S("whiskers", "All this flying made me thirsty. A whole ocean to drink!", "sea", "sea_thirst"),
    A("sea", 1.6, "sea_sip", [("lap", 0.2), ("lap", 0.42), ("lap", 0.64)]),
    S("whiskers", "Bleh! Bleh! Salty! Somebody put salt in the sea!", "sea", "sea_bleh", [("boing", 0.0)]),
    A("sea", 0.9, "sea_laugh"),
    S("bluebell", "Sea water is salty, Whiskers. Here is why.", "sea", "sea_why"),
    S("bluebell", "Rain washes tiny bits of salt out of the rocks. Rivers carry the salt down to the sea.",
      "sea", "sea_salt1", [("pop", 0.1)]),
    S("bluebell", "The sun warms the water, and it rises up into the clouds. But the salt stays behind.",
      "sea", "sea_salt2", [("sparkle", 0.4)]),
    A("sea", 2.0, "sea_saltact", [("ding", 0.6)]),
    S("whiskers", "I knew that. I tasted it on purpose. For science.", "sea", "sea_purpose"),
    A("sea", 0.9, "sea_laugh2"),
    A("sea", 1.2, "sea_gust", [("wind", 0.0)]),
    S("pip", "Whoa! Where do all these waves come from?", "sea", "sea_waves"),
    S("bluebell", "The wind makes the waves. It blows over the water and pushes it into bumps.",
      "sea", "sea_wind", [("wind", 0.3)]),
    A("sea", 1.8, "sea_windact", [("splash", 0.4)]),
    S("bluebell", "Now come with me. I'll show you my deep, deep home.", "sea", "sea_dive"),
    A("sea", 1.6, "sea_down", [("sparkle", 0.1), ("splash", 0.5)]),

    # ------------------------------------------------------------------ deep
    A("deep", 1.6, "d_open", [("bloop", 0.2)]),
    S("narrator", "In a magic bubble, they sank down, down, down.", "deep", "d_narr", [("bloop", 0.5)]),
    A("deep", 1.6, "d_sink", [("whalesong", 0.1)]),
    S("luna", "It's getting darker and darker!", "deep", "d_dark"),
    S("bluebell", "The Pacific is very, very deep. Its deepest place is deeper than the tallest mountain is high!",
      "deep", "d_deep", [("pop", 0.6)]),
    A("deep", 2.4, "d_mount", [("ding", 0.3)]),
    S("pip", "Look, a fish with its own lamp!", "deep", "d_lamp"),
    S("whiskers", "Ooh. A fish with a night light. Very cosy.", "deep", "d_cosy"),
    A("deep", 1.8, "d_up", [("whalesong", 0.0), ("bloop", 0.5)]),

    # ----------------------------------------------------------------- beach
    A("beach", 1.4, "b_open", [("waves", 0.0)]),
    S("narrator", "That evening, they rested on a quiet beach.", "beach", "b_narr"),
    S("nipper", "Hey! Watch your step! That's my rock pool!", "beach", "b_hey", [("snip", 0.05)]),
    S("luna", "Sorry! Why did the sea go so far out?", "beach", "b_why"),
    S("nipper", "It's the tide! Twice a day the sea comes in high, and goes out low.", "beach", "b_tide",
      [("waves", 0.3)]),
    A("beach", 2.6, "b_tideact", [("waves", 0.1), ("ding", 0.85)]),
    S("pip", "But what pulls all that water?", "beach", "b_pull"),
    S("nipper", "The Moon! It pulls the sea, just a little bit, like a gentle magnet.", "beach", "b_moon",
      [("sparkle", 0.3)]),
    A("beach", 2.2, "b_moonact", [("sparkle", 0.2)]),
    S("whiskers", "The Moon? I once chased a Moon Fish. It got away.", "beach", "b_moonfish"),
    A("beach", 0.9, "b_laugh", [("snip", 0.3)]),
    A("beach", 1.4, "b_bye", [("whalesong", 0.0), ("spout", 0.4)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. There are five oceans.", "remember", "r_f1", [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. The Pacific is the biggest and the deepest ocean.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Sea water is salty.", "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Which ocean is the biggest? The Atlantic, or the Pacific?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "The Pacific! It's the biggest and the deepest. Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Is sea water salty, or sweet?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "Salty! So don't drink it, like Whiskers did!", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("whiskers", "Ahh. My water bowl. Not salty at all.", "home", "h_bowl", [("lap", 0.0), ("lap", 0.15)]),
    S("pip", "Goodnight, Bluebell. Goodnight, five oceans!", "home", "h_pip", [("spin", 0.3)]),
    A("home", 1.2, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, mountains and volcanoes! Goodnight, big blue world.", "home", "h_next",
      [("sparkle", 0.2)]),
    A("home", 2.6, "h_end"),
]
