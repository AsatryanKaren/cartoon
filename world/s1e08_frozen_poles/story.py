"""Whiskers & Luna's World, Episode 8: "The Frozen Poles".

One chilly morning Whiskers spots "whipped cream" on the top and bottom of Luna's globe. It is
ice: the top of the Earth is the North Pole, the bottom is the South Pole. Whiskers imagines a
giant stripy pole sticking out of the world, perfect for scratching. The cushion flies them up
into space, where the poles are the very top and bottom points of the spinning Earth, and the
globe flattens into the magic map. First stop: Antarctica, where Pebble the little Adelie
penguin explains that under all that ice there is land, a whole continent. Pebble has never met
a polar bear and sends a message north: "Hello from the bottom of the world!" Whiskers decides to
simply carry Pebble north to meet one -- but at the hot middle of the Earth (the equator) the
penguin starts to cook. Luna stops him: polar bears live in the north and penguins in the
south, so they never meet. They take Pebble home and carry the message alone. At the top of the
world there is no pole at all, only floating sea ice on the Arctic Ocean, with Arctic foxes,
walruses, seals -- and Bjorn the polar bear, who has never met a penguin either and sends a
message back. Bjorn shows (with a torch on a ball) why the poles are so cold: the sun's light
hits them only at a slant, so it is spread thin and weak. In summer the sun does not set for
weeks; in winter it stays dark for weeks, and the northern lights dance.

Facts: 1) the North Pole is at the top of the Earth, the South Pole at the bottom;
2) polar bears live in the north, penguins live in the south; 3) the poles are the coldest
places, because the sun's light there is weak.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e08_frozen_poles import sounds

TITLE = "08 - The Frozen Poles"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "south", "trip", "north", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Pebble: a small, chirpy, polite Adelie penguin from Antarctica
    "pebble": Voice("bf_alice", 1.06, 3, ["Kate"], 186, "en-gb+f2", 78, 170),
    # Bjorn: a huge, gentle, slow-laughing polar bear from the Arctic
    "bjorn": Voice("am_onyx", 0.9, -2, ["Ralph"], 150, "en-us+m3", 28, 140),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "pebble": (190, 236, 255), "bjorn": (236, 236, 200)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "south": "w_ice", "trip": "w_map",
         "north": "w_ice", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("s_pole", 0.0, "w_funny"), ("s_go", 0.0, "w_home"),
              ("tr_hot", 0.0, "w_funny"), ("tr_never", 0.0, "w_map"), ("tr_purpose", 0.0, "w_funny"),
              ("tr_back", 0.0, "w_map"), ("no_why", 0.0, "w_wonder"), ("no_night", 0.2, "w_night")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode eight. The Frozen Poles!", "title", "t_name"),
    A("title", 1.1, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.2, "s_open", [("spin", 0.15)]),
    S("narrator", "One chilly morning, Luna was spinning her old globe.", "sill", "s_narr", [("spin", 0.2)]),
    S("whiskers", "Luna, your globe has whipped cream on top. And on the bottom! Can I lick it?",
      "sill", "s_cream"),
    S("luna", "That's not cream, Whiskers. It's ice! The very top of the Earth is the North Pole.",
      "sill", "s_north", [("ding", 0.7)]),
    S("luna", "And the very bottom is the South Pole.", "sill", "s_south", [("ding", 0.5)]),
    S("whiskers", "A pole? A giant stripy pole, sticking out of the world? Perfect for scratching!",
      "sill", "s_pole", [("pop", 0.35)]),
    A("sill", 1.3, "s_scratch", [("scratch", 0.1), ("scratch", 0.5)]),
    S("pip", "Let's go and see if there's really a pole!", "sill", "s_go"),
    S("luna", "Hold on to the cushion!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.5, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Whoosh! Up into space they flew.", "map", "m_narr"),
    S("luna", "Look! The North Pole is the very top point of the Earth.", "map", "m_np", [("ding", 0.6)]),
    S("luna", "And the South Pole is the very bottom point.", "map", "m_sp", [("ding", 0.6)]),
    S("pip", "The Earth spins around between them, like a top!", "map", "m_top", [("spin", 0.2)]),
    A("map", 1.4, "m_spin", [("sparkle", 0.3)]),
    S("whiskers", "I don't see any pole sticking out.", "map", "m_nopole"),
    A("map", 2.3, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "On a map, the North Pole is up at the top, and the South Pole is down at the bottom.",
      "map", "m_mapnp", [("ding", 0.25), ("ding", 0.75)]),
    S("pip", "Let's go to the bottom first. South!", "map", "m_south"),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("whoosh", 0.75)]),

    # ----------------------------------------------------------------- south
    A("south", 1.6, "so_land", [("wind", 0.0), ("crunch", 0.55)]),
    S("narrator", "They landed in Antarctica, at the bottom of the world.", "south", "so_narr"),
    A("south", 1.5, "so_slide", [("squeak", 0.1), ("swish", 0.3), ("squeak", 0.8)]),
    S("pebble", "Hello, hello! Welcome to Antarctica! I'm Pebble.", "south", "so_hello"),
    S("pip", "Hello, Pebble! Is all this ice floating on the sea?", "south", "so_float"),
    S("pebble", "No! Under the ice there is land. A whole continent, covered in thick, thick ice.",
      "south", "so_land1", [("pop", 0.3)]),
    A("south", 2.2, "so_cut", [("ding", 0.3)]),
    S("pebble", "Lots of penguins live down here, in the south.", "south", "so_live",
      [("squeak", 0.2), ("squeak", 0.6)]),
    S("pip", "Are there polar bears here too?", "south", "so_bears"),
    S("pebble", "Polar bears? I've never met one! Are they really big, and white, and fluffy?",
      "south", "so_never"),
    S("pebble", "Please give one a message: Hello from the bottom of the world!", "south", "so_msg",
      [("pop", 0.4)]),
    S("whiskers", "Why send a message? I'll just take you with us! Hop on!", "south", "so_hop"),
    A("south", 2.0, "so_off", [("boing", 0.15), ("whoosh", 0.55)]),

    # ------------------------------------------------------------------ trip
    A("trip", 1.5, "tr_fly", [("whoosh", 0.1)]),
    S("narrator", "So they flew north, with a penguin on board.", "trip", "tr_narr"),
    A("trip", 1.6, "tr_warm", [("sizzle", 0.4)]),
    S("pebble", "Phew! It's getting so hot! I'm a penguin, not a fried egg!", "trip", "tr_hot",
      [("sizzle", 0.0)]),
    S("luna", "Whiskers, stop! Penguins live in the south. Polar bears live in the north.", "trip",
      "tr_stop", [("ding", 0.45), ("ding", 0.85)]),
    S("luna", "They live at opposite ends of the world, so they never meet!", "trip", "tr_never"),
    A("trip", 1.8, "tr_diag", [("sparkle", 0.2)]),
    S("whiskers", "I knew that. I gave Pebble a sauna on purpose. Penguins love saunas.", "trip",
      "tr_purpose"),
    S("pebble", "We do not!", "trip", "tr_not", [("squeak", 0.0)]),
    A("trip", 1.0, "tr_laugh"),
    S("narrator", "So they took Pebble home, and carried the message north.", "trip", "tr_back"),
    A("trip", 3.0, "tr_path", [("whoosh", 0.05), ("squeak", 0.3), ("whoosh", 0.45)]),

    # ----------------------------------------------------------------- north
    A("north", 1.6, "no_land", [("wind", 0.0), ("crunch", 0.55)]),
    S("narrator", "At the top of the world, they landed on the Arctic sea ice.", "north", "no_narr"),
    S("pip", "Look! An Arctic fox! And walruses, and seals!", "north", "no_animals", [("pop", 0.1)]),
    S("whiskers", "But where's the pole? Not even a little stripy one.", "north", "no_pole"),
    A("north", 1.0, "no_rise", [("crunch", 0.2)]),
    S("bjorn", "Ho ho! There's no real pole, little cat. The North Pole is just a place: the very top "
               "of the Earth.", "north", "no_spot"),
    S("bjorn", "I'm Bjorn. Welcome to the Arctic!", "north", "no_name"),
    S("whiskers", "A message for you, from Pebble the penguin: Hello from the bottom of the world!",
      "north", "no_msg", [("pop", 0.1)]),
    S("bjorn", "A penguin! I've never met one. Tell Pebble: Hello from the top!", "north", "no_reply"),
    A("north", 0.9, "no_wave"),
    S("luna", "Bjorn, is there land under this ice?", "north", "no_landq"),
    S("bjorn", "No land at all! This is the Arctic Ocean. The sea ice floats on top, like an ice cube "
               "in a drink.", "north", "no_float", [("crack", 0.6)]),
    A("north", 2.0, "no_cut", [("bloop", 0.3)]),
    S("pip", "Brr! But why are the poles so cold?", "north", "no_why"),
    S("bjorn", "In the middle of the Earth, the sunshine comes straight down. Strong and hot!",
      "north", "no_straight"),
    S("bjorn", "But here, it comes in at a slant. It spreads out thin, so it's weak.", "north",
      "no_slant"),
    A("north", 2.6, "no_torch", [("ding", 0.2), ("ding", 0.6)]),
    S("bjorn", "In summer, the sun doesn't set for weeks. In winter, it stays dark for weeks!",
      "north", "no_days"),
    A("north", 2.0, "no_night", [("sparkle", 0.6)]),
    S("whiskers", "Weeks and weeks of night? The best nap ever!", "north", "no_nap"),
    S("luna", "And look! The northern lights, like we saw in Norway!", "north", "no_lights",
      [("sparkle", 0.3)]),
    A("north", 2.2, "no_aurora", [("sparkle", 0.4)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. The North Pole is at the top of the Earth. The South Pole is at the "
                  "bottom.", "remember", "r_f1", [("ding", 0.05)]),
    A("remember", 0.7, "r_p1"),
    S("narrator", "Two. Polar bears live in the north. Penguins live in the south.", "remember", "r_f2",
      [("ding", 0.05)]),
    A("remember", 0.7, "r_p2"),
    S("narrator", "Three. The poles are the coldest places, because the sun's light there is weak.",
      "remember", "r_f3", [("ding", 0.05)]),
    A("remember", 1.4, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Which pole is at the top of the Earth? The North Pole, or the South Pole?",
      "quiz", "q1"),
    A("quiz", 1.1, "q1_count", TICKS),
    S("narrator", "The North Pole! Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.7, "q1_end"),
    S("narrator", "Next. Where do penguins live? Near the North Pole, or near the South Pole?", "quiz",
      "q2"),
    A("quiz", 1.1, "q2_count", TICKS),
    S("narrator", "Near the South Pole! Penguins and polar bears never meet.", "quiz", "q2_ans",
      [("chime", 0.0)]),
    A("quiz", 0.9, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.5, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again.", "home", "h_narr"),
    S("pip", "Pebble and Bjorn will never meet. But now they're pen pals!", "home", "h_pip",
      [("spin", 0.3)]),
    S("whiskers", "Being the mail cat is hard work. Time for a long, polar night nap.", "home", "h_nap"),
    A("home", 1.3, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, weather and seasons! Goodnight, frozen poles.", "home", "h_next",
      [("sparkle", 0.2)]),
    A("home", 2.8, "h_end"),
]
