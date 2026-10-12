"""Whiskers & Luna's World, Episode 4: "Mountains and Volcanoes".

On the windowsill Whiskers asks why Luna's globe is so bumpy. The bumps are mountains -- and Luna
shows how they grow with Whiskers' blanket: she and Pip push its two ends together and the
blanket folds up into a mountain, just like the giant pieces of the ground do (very, very slowly).
"Nap Mountain!" The friends fly into the magic map: there are mountains all over the world, but
the tallest are in the Himalayas, in Asia. There Tashi the snow leopard shows them Mount Everest,
the tallest mountain on Earth: almost nine kilometres high, taller than twenty big skyscrapers
stacked up (but, as Bluebell told them, the deepest ocean is deeper still). The higher you go,
the colder it gets -- snow on top even in summer. Shivering Whiskers wants a warm mountain, so
they fly to the Galapagos Islands, where Iggy the marine iguana shows them a volcano. Whiskers
thinks it is a giant pot of hot chocolate; it is magma, rock so hot it melts, and lava when it
comes out. The volcano erupts and Whiskers tries to toast his fish from very far away with a very
long fishing rod -- it comes back as charcoal. Lava cools into new rock: many islands, like Iggy's,
were made by volcanoes.

Facts: 1) mountains grow when the land pushes together; 2) Mount Everest is the tallest mountain
on Earth; 3) volcanoes have hot melted rock inside.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e04_mountains_volcanoes import sounds

TITLE = "04 - Mountains and Volcanoes"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "peaks", "trip", "volcano", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Tashi: a calm, kind snow leopard of the Himalayas with a huge fluffy tail
    "tashi": Voice("bf_isabella", 0.95, -1, ["Kate"], 160, "en-gb+f3", 40, 145),
    # Iggy: a sturdy, sunbathing, easy-going marine iguana of the Galapagos Islands
    "iggy": Voice("am_fenrir", 0.98, -1, ["Ralph"], 165, "en-us+m3", 35, 150),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "tashi": (210, 230, 250), "iggy": (170, 235, 150)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "peaks": "w_peaks", "trip": "w_map",
         "volcano": "w_island", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("s_fold", 0.3, "w_funny"), ("s_pip2", 0.0, "w_home"),
              ("v_rumble", 0.0, "w_lava"), ("v_purpose", 0.4, "w_funny"), ("v_cool", 0.0, "w_island")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode four. Mountains and Volcanoes!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.2, "s_open", [("spin", 0.15)]),
    S("whiskers", "Luna, why is your globe so bumpy? Did it get goosebumps?", "sill", "s_bumpy"),
    S("luna", "Those bumps are mountains, Whiskers!", "sill", "s_mount", [("ding", 0.6)]),
    S("pip", "But how does a mountain grow?", "sill", "s_grow"),
    S("luna", "I'll show you. Pip, push the other end of the blanket!", "sill", "s_show"),
    A("sill", 1.6, "s_push", [("ruffle", 0.1), ("ruffle", 0.5)]),
    S("luna", "The ground is made of giant pieces. They push together, very, very slowly.",
      "sill", "s_pieces", [("ruffle", 0.5)]),
    S("luna", "And where they push, the land folds up, like this. That's how mountains grow!",
      "sill", "s_fold", [("ruffle", 0.2), ("pop", 0.75)]),
    A("sill", 2.0, "s_foldact", [("ding", 0.2)]),
    S("whiskers", "Hey, my blanket is a mountain now. Nap Mountain!", "sill", "s_nap"),
    A("sill", 0.8, "s_laugh"),
    S("pip", "Which mountain is the tallest in the world?", "sill", "s_pip2"),
    S("luna", "Let's go and see! Hold on to the cushion!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.4, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Up, up into space they flew!", "map", "m_narr", [("spin", 0.5)]),
    A("map", 2.4, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "There are mountains all over the world.", "map", "m_all",
      [("pop", 0.3), ("pop", 0.45), ("pop", 0.6), ("pop", 0.75)]),
    S("luna", "But the tallest ones are here, in Asia. The Himalayas!", "map", "m_him", [("ding", 0.7)]),
    S("whiskers", "The Him-a-what? Bless you.", "map", "m_bless"),
    A("map", 0.8, "m_laugh"),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ----------------------------------------------------------------- peaks
    A("peaks", 1.4, "p_land", [("wind", 0.0)]),
    S("narrator", "They landed high up in the Himalaya mountains.", "peaks", "p_narr"),
    A("peaks", 1.0, "p_look", [("wind", 0.2)]),
    S("tashi", "Welcome to the roof of the world. I'm Tashi, a snow leopard.", "peaks", "p_hello"),
    S("tashi", "And that is Mount Everest. The tallest mountain on Earth!", "peaks", "p_ever",
      [("ding", 0.6)]),
    A("peaks", 1.6, "p_everact", [("sparkle", 0.2)]),
    S("tashi", "It's almost nine kilometres high. Taller than twenty big skyscrapers, stacked up!",
      "peaks", "p_sky", [("pop", 0.6)]),
    A("peaks", 2.6, "p_skyact", [("pop", 0.0), ("pop", 0.1), ("pop", 0.2), ("pop", 0.3), ("ding", 0.75)]),
    S("pip", "But Bluebell said the deepest ocean is even deeper!", "peaks", "p_deep"),
    S("tashi", "She's right. Everest could hide in it, top and all!", "peaks", "p_hide", [("bloop", 0.3)]),
    A("peaks", 1.8, "p_hideact", [("bloop", 0.1)]),
    S("pip", "Brrr! Why is it so cold up here?", "peaks", "p_cold", [("wind", 0.0)]),
    S("tashi", "The higher you go, the colder it gets. So there's snow on top, even in summer.",
      "peaks", "p_higher"),
    A("peaks", 2.4, "p_coldact", [("ding", 0.2), ("ding", 0.45), ("ding", 0.7)]),
    S("whiskers", "Snow in summer? I want a warm mountain, please.", "peaks", "p_warm", [("chatter", 0.0)]),
    S("luna", "I know a mountain that's hot inside. A volcano!", "peaks", "p_volc"),
    S("tashi", "Goodbye, little ones. Fly safely!", "peaks", "p_bye"),
    A("peaks", 1.4, "p_go", [("whoosh", 0.3)]),

    # ------------------------------------------------------------------ trip
    A("trip", 1.0, "tr_go", [("whoosh", 0.1)]),
    S("narrator", "Away they flew, to the Galapagos Islands, in the Pacific Ocean.", "trip", "tr_narr"),
    A("trip", 2.0, "tr_path", [("whoosh", 0.1), ("sparkle", 0.85)]),

    # --------------------------------------------------------------- volcano
    A("volcano", 1.4, "v_land", [("waves", 0.2)]),
    S("whiskers", "Ooh! A giant pot of hot chocolate!", "volcano", "v_choc", [("bubble", 0.4)]),
    S("iggy", "Ha! That's a volcano, my furry friend. I'm Iggy, an iguana.", "volcano", "v_hello"),
    S("iggy", "Deep inside is magma. Rock so hot, it melts!", "volcano", "v_magma", [("bubble", 0.5)]),
    A("volcano", 1.6, "v_magmaact", [("bubble", 0.2)]),
    S("iggy", "And when it comes out, we call it lava.", "volcano", "v_lava", [("bubble", 0.6)]),
    A("volcano", 1.2, "v_rumble", [("rumble", 0.0)]),
    S("pip", "The ground is shaking!", "volcano", "v_shake", [("rumble", 0.0)]),
    S("iggy", "Stay up there, nice and far away. She's erupting!", "volcano", "v_stay"),
    A("volcano", 2.8, "v_erupt", [("boom", 0.05), ("rumble", 0.1), ("sizzle", 0.6)]),
    S("whiskers", "Lava? Perfect for toasting my fish. From far, far away.", "volcano", "v_toast"),
    A("volcano", 2.6, "v_fish", [("zip", 0.05), ("sizzle", 0.4), ("poof", 0.6), ("zip", 0.7)]),
    S("whiskers", "Hot! Hot! Hot! It's charcoal!", "volcano", "v_hot", [("boing", 0.0)]),
    S("iggy", "Lava is hotter than any oven. Never go near it!", "volcano", "v_oven"),
    S("whiskers", "I knew that. I made it crispy on purpose.", "volcano", "v_purpose", [("crunch", 0.85)]),
    A("volcano", 0.9, "v_laugh", [("crunch", 0.1)]),
    S("iggy", "Look. When lava cools down, it turns into hard new rock.", "volcano", "v_cool",
      [("sizzle", 0.1)]),
    A("volcano", 1.4, "v_coolact", [("ding", 0.4)]),
    S("iggy", "My whole island was made by a volcano. Lots of islands were!", "volcano", "v_island",
      [("pop", 0.6)]),
    A("volcano", 2.2, "v_islandact", [("bubble", 0.1), ("ding", 0.75)]),
    A("volcano", 1.2, "v_bye", [("sparkle", 0.3)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. Mountains grow when the land pushes together.", "remember", "r_f1",
      [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. Mount Everest is the tallest mountain on Earth.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Volcanoes have hot, melted rock inside.", "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Which is the tallest mountain on Earth? Mount Everest, or Nap Mountain?",
      "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Mount Everest! Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. What is inside a volcano? Hot chocolate, or hot melted rock?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "Hot melted rock! Sorry, Whiskers.", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("whiskers", "Ahh. Nap Mountain. My favourite mountain in the world.", "home", "h_nap",
      [("whoosh", 0.1)]),
    S("pip", "Goodnight, Tashi! Goodnight, Iggy!", "home", "h_pip", [("spin", 0.3)]),
    A("home", 1.2, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, rivers and lakes! Goodnight, bumpy world.", "home", "h_next",
      [("sparkle", 0.2)]),
    A("home", 2.6, "h_end"),
]
