"""Whiskers & Luna's World, Episode 7: "Rainforests".

A rainy morning: Whiskers can't nap in the sunny spot. Luna says that in a rainforest it rains
almost every day. On her globe she shows the Equator, the pretend line around the middle of the
Earth: rainforests grow near it, where it is warm all year. The friends fly up into space and see
the Equator and the green rainforests, the globe flattens into the magic map and they fly to the
biggest rainforest of all, the Amazon in South America. On the dark, steamy forest floor Whiskers
uses a giant leaf as an umbrella; it fills with (warm!) rain and tips over him. Coco the chatty
toucan shows them that a rainforest has layers like the floors of a building and lifts them up
through the understorey to the canopy, where most of the animals live. There they meet Mossy, a
very slow sloth who likes to hang and nap. Whiskers tries to nap upside down like Mossy -- and
falls through all the layers to the forest floor, right next to a sleeping jaguar. "I fell on
purpose. I was visiting every layer." Pip: you missed one! They rise above the canopy to the
emergent layer, where the tallest trees poke out and a harpy eagle lives.

Facts: 1) rainforests are warm and rainy, and grow near the Equator; 2) the Amazon is the biggest
rainforest; 3) rainforests have layers, and most animals live high up in the canopy.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e07_rainforests import sounds

TITLE = "07 - Rainforests"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "forest", "climb", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Coco: a chatty, colourful toco toucan who loves to show visitors around
    "coco": Voice("af_nova", 1.08, 1, ["Paulina"], 190, "en-us+f2", 70, 175),
    # Mossy: a very, very slow three-toed sloth with moss in his fur
    "mossy": Voice("am_santa", 0.78, -1, ["Ralph"], 110, "en-us+m3", 30, 100),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "coco": (255, 200, 110), "mossy": (196, 226, 160)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "forest": "w_jungle", "climb": "w_jungle",
         "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("f_umb", 0.0, "w_funny"), ("f_year", 0.0, "w_jungle"),
              ("c_rise2", 0.0, "w_wonder"), ("c_most", 0.0, "w_jungle"), ("k_hello", 0.0, "w_slow"),
              ("k_hang", 0.0, "w_funny"), ("k_top", 0.0, "w_wonder"), ("k_bye", 0.0, "w_slow"),
              ("k_week", 0.3, "w_funny")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode seven. Rainforests!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("rain", 0.0)]),
    S("narrator", "One rainy morning, Whiskers was feeling very grumpy.", "sill", "s_narr"),
    S("whiskers", "Rain, rain, go away. I can't nap in my sunny spot today.", "sill", "s_rain", [("rain", 0.3)]),
    S("luna", "Then don't go to a rainforest, Whiskers! There, it rains almost every day.", "sill", "s_every"),
    S("whiskers", "A forest... made of rain?", "sill", "s_made"),
    S("luna", "No, silly! A rainforest is a warm, wet forest, full of giant trees.", "sill", "s_warm",
      [("pop", 0.6)]),
    S("pip", "Where are the rainforests, Luna?", "sill", "s_where", [("spin", 0.4)]),
    S("luna", "Look. This is the Equator, a pretend line around the middle of the Earth.", "sill", "s_eq",
      [("sparkle", 0.5)]),
    S("luna", "Rainforests grow near the Equator, where it's warm all year.", "sill", "s_near", [("pop", 0.4)]),
    A("sill", 1.0, "s_near2"),
    S("luna", "Let's go and see the biggest one. Hold on to the cushion!", "sill", "s_hold", [("spin", 0.6)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.8, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Whoosh! Up into space they flew.", "map", "m_narr"),
    S("luna", "See the Equator? It goes all the way around the middle of the Earth.", "map", "m_eqline",
      [("sparkle", 0.3)]),
    A("map", 1.6, "m_eqspin"),
    S("pip", "And the dark green patches near it are the rainforests!", "map", "m_green", [("pop", 0.6)]),
    A("map", 2.6, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "The biggest rainforest of all is the Amazon, in South America!", "map", "m_amazon",
      [("ding", 0.75)]),
    A("map", 1.4, "m_zoom", [("sparkle", 0.3)]),
    S("narrator", "The Amazon is huge! Its trees cover a big part of South America.", "map", "m_huge"),
    S("whiskers", "That's a lot of trees. And a lot of rain.", "map", "m_lot"),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("whoosh", 0.75)]),

    # ---------------------------------------------------------------- forest
    A("forest", 1.8, "f_land", [("jungle", 0.0), ("thump", 0.55)]),
    S("narrator", "They landed on the forest floor. It was dark, and warm, and very wet.", "forest", "f_narr"),
    S("pip", "Why is it so dark down here?", "forest", "f_dark"),
    S("luna", "The trees are so tall, their leaves block out most of the sunshine.", "forest", "f_block"),
    A("forest", 0.9, "f_drip", [("rain", 0.1)]),
    S("whiskers", "Oh no, more rain! Good thing I brought an umbrella.", "forest", "f_umb", [("pop", 0.85)]),
    A("forest", 2.6, "f_fill", [("rain", 0.0), ("drip", 0.3), ("drip", 0.55), ("splash", 0.78)]),
    S("whiskers", "Hey... the rain is warm!", "forest", "f_wet"),
    S("luna", "Rainforests are warm all year round, and it rains almost every day.", "forest", "f_year"),
    A("forest", 1.0, "f_flyin", [("squawk", 0.2), ("flap", 0.4)]),
    S("coco", "Hola, amigos! Welcome to the Amazon!", "forest", "f_hola"),
    S("whiskers", "Aaah! A flying banana!", "forest", "f_banana"),
    S("coco", "I'm not a banana! I'm Coco the toucan. This is just my big, beautiful beak.", "forest", "f_name"),
    A("forest", 0.6, "f_laugh"),
    S("coco", "Down here on the forest floor live ants, and the jaguar. Shh! He's asleep.", "forest",
      "f_floor", [("snore", 0.7)]),
    S("coco", "But most animals live upstairs. A rainforest has layers, like the floors of a building!",
      "forest", "f_layers", [("ding", 0.75)]),
    S("pip", "Then let's go up!", "forest", "f_go"),
    A("forest", 1.2, "f_up", [("whoosh", 0.2), ("flap", 0.4)]),

    # ----------------------------------------------------------------- climb
    A("climb", 1.6, "c_rise", [("whoosh", 0.1)]),
    S("coco", "This is the understorey. Small trees and big leaves grow here, in the shade.", "climb", "c_under",
      [("ding", 0.05)]),
    S("pip", "Look! A tiny blue frog!", "climb", "c_frog", [("ribbit", 0.6)]),
    A("climb", 1.8, "c_rise2", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("coco", "And this is the canopy, the leafy roof of the forest!", "climb", "c_canopy", [("ding", 0.05)]),
    S("coco", "Most rainforest animals live up here, where there's sunshine, flowers and fruit.", "climb",
      "c_most", [("hoot", 0.8)]),
    A("climb", 2.2, "c_animals", [("squawk", 0.1), ("pop", 0.2), ("pop", 0.4), ("pop", 0.6), ("pop", 0.8)]),
    S("luna", "More kinds of plants and animals live in rainforests than anywhere else on land!", "climb",
      "c_more", [("sparkle", 0.4)]),
    A("climb", 1.4, "c_many", [("pop", 0.1), ("pop", 0.3), ("pop", 0.5), ("pop", 0.7)]),
    S("pip", "Hey, who's that, hanging upside down?", "climb", "c_who"),
    A("climb", 1.0, "c_sloth"),
    S("mossy", "Hel... lo... there.", "climb", "k_hello"),
    S("coco", "That's Mossy the sloth. He's one of the slowest animals in the world.", "climb", "k_slow"),
    S("mossy", "I... like... to hang... and nap.", "climb", "k_nap"),
    S("whiskers", "Napping in a tree? I'm a champion napper. Watch this!", "climb", "k_watch"),
    A("climb", 2.2, "k_hang", [("whoosh", 0.05), ("creak", 0.55), ("purr", 0.7)]),
    S("mossy", "Care... ful...", "climb", "k_careful", [("creak", 0.5)]),
    A("climb", 0.9, "k_slip", [("creak", 0.1), ("pop", 0.6)]),
    S("whiskers", "Whoa! Canopy! Understorey! Forest flooor!", "climb", "k_yell", [("fall", 0.0)]),
    A("climb", 1.2, "k_land", [("thump", 0.1)]),
    A("climb", 1.1, "k_eye", [("snore", 0.0)]),
    S("whiskers", "Oh. Hello, big kitty. Nice spots.", "climb", "k_kitty"),
    A("climb", 1.2, "k_yawn", [("growl", 0.1), ("whoosh", 0.6)]),
    S("luna", "Whiskers! Are you okay?", "climb", "k_ok"),
    S("whiskers", "I fell on purpose. I was visiting every layer.", "climb", "k_purpose"),
    S("pip", "You missed one! The emergent layer, at the very top!", "climb", "k_missed"),
    A("climb", 3.4, "k_top", [("whoosh", 0.1), ("whoosh", 0.5), ("sparkle", 0.9)]),
    S("coco", "The emergent trees are the tallest. They poke out above the canopy, and eagles live up here.",
      "climb", "k_emergent", [("screech", 0.85)]),
    S("luna", "And all these leaves help make the fresh air we breathe.", "climb", "k_air", [("sparkle", 0.3)]),
    A("climb", 1.0, "k_air2"),
    S("mossy", "Good... bye...", "climb", "k_bye"),
    S("whiskers", "He'll finish saying goodbye next week.", "climb", "k_week"),
    A("climb", 1.4, "k_laugh"),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. Rainforests are warm and rainy, and they grow near the Equator.", "remember",
      "r_f1", [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. The Amazon is the biggest rainforest in the world.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Rainforests have layers, and most animals live high up in the canopy.", "remember",
      "r_f3", [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Is a rainforest cold and dry, or warm and wet?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Warm and wet! It rains almost every day.", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Where do most rainforest animals live? On the forest floor, or high up in the canopy?",
      "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "High up in the canopy! Well done!", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.6, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again. The rain had stopped.", "home", "h_narr"),
    S("pip", "Can we visit Mossy again tomorrow?", "home", "h_pip", [("spin", 0.3)]),
    S("whiskers", "Sure. But first, a nap. The right way up.", "home", "h_nap"),
    A("home", 1.4, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, the frozen poles! Goodnight, rainforest.", "home", "h_next", [("sparkle", 0.2)]),
    A("home", 3.0, "h_end"),
]
