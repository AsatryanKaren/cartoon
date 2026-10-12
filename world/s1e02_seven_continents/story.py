"""Whiskers & Luna's World, Episode 2: "The Seven Continents".

On a rainy morning Whiskers asks why Luna's globe is covered in colourful
blobs (sweets? cheese?). They are continents -- the big pieces of land -- and
there are seven. The nap cushion flies them into the magic map, where Albert
the albatross (the bird with the longest wings, who glides over oceans for
thousands of miles) teaches them a little song: "Four A's, two Americas, and
Europe -- that makes seven!" (Whiskers makes it 421.) Then a flying tour:
Europe (home, the Eiffel Tower), Africa (lion, elephant, pyramids), Asia
(the biggest continent: panda, Great Wall), Australia (kangaroo) and down to
the bottom of the world, where Whiskers expects a warm sunny beach -- and
freezes into a cat-sicle: Antarctica is the coldest place on Earth, covered
in thick ice, and no people live there all year. Then South America (the
Amazon, llamas) and North America (bald eagle, bison), and home.

Facts: 1) the Earth's land is split into seven continents; 2) Asia is the
biggest continent; 3) Antarctica is the coldest continent, covered in ice.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e02_seven_continents import sounds

TITLE = "02 - The Seven Continents"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "tour", "ice", "tour2", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Albert: a jolly, sea-going albatross with very long wings and a sailor's cheer
    "albert": Voice("bm_fable", 1.0, 0, ["Oliver"], 176, "en-gb+m4", 45, 160),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "albert": (255, 236, 160)}

MOODS = {
    **K.KIT_MOODS,
    "w_ice": dict(bpm=76, prog=[(64, K.MIN), (60, K.MAJ), (67, K.MAJ), (62, K.MAJ)], drums=False, mel=0.5,
                  oct=86, vol=0.7),
    "w_song": dict(bpm=120, prog=[(60, K.MAJ), (67, K.MAJ), (65, K.MAJ), (67, K.MAJ)], drums=True, mel=0.8,
                   oct=76, vol=0.8),
}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "tour": "w_map", "ice": "w_ice",
         "tour2": "w_map", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_names", 0.0, "w_map"), ("m_as", 0.0, "w_song"), ("m_go", 0.0, "w_map"),
              ("s_cheese", 0.5, "w_funny"), ("s_many", 0.0, "w_home"),
              ("i_purpose", 0.3, "w_funny"), ("i_go", 0.6, "w_ice")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode two. The Seven Continents!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("spin", 0.15)]),
    S("narrator", "One rainy morning, Luna was spinning her old globe.", "sill", "s_narr", [("spin", 0.2)]),
    S("whiskers", "Luna, what are those colourful blobs on your globe? Sweets?", "sill", "s_blobs"),
    S("luna", "They're not sweets, Whiskers! The big pieces of land are called continents.",
      "sill", "s_cont", [("pop", 0.7)]),
    S("whiskers", "Continents? Is that a kind of cheese?", "sill", "s_cheese"),
    A("sill", 1.2, "s_cheese2", [("pop", 0.1)]),
    S("pip", "How many continents are there, Luna?", "sill", "s_many"),
    S("luna", "Seven! Let's fly to them all. Hold on to the cushion!", "sill", "s_seven",
      [("spin", 0.7)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.6, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Whoosh! Up into the magic map!", "map", "m_narr"),
    A("map", 2.2, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "Look! Each colour is one continent.", "map", "m_colours"),
    A("map", 2.8, "m_names", [("ding", 0.04 + 0.13 * i) for i in range(7)]),
    A("map", 1.6, "m_bird", [("flap", 0.0), ("caw", 0.55)]),
    S("albert", "Ahoy, little flyers! I'm Albert the albatross.", "map", "m_hello"),
    S("albert", "I have the longest wings of any bird. I glide over the oceans for miles and miles!",
      "map", "m_wings", [("whoosh", 0.5)]),
    S("pip", "Albert, how can we remember all seven continents?", "map", "m_how"),
    S("albert", "Easy! Sing along! Four A's: Africa, Antarctica, Asia, Australia.", "map", "m_as",
      [("ding", 0.45), ("ding", 0.6), ("ding", 0.74), ("ding", 0.9)]),
    S("albert", "Two Americas, North and South.", "map", "m_ams",
      [("ding", 0.5), ("ding", 0.85)]),
    S("albert", "And Europe! That makes seven!", "map", "m_eu", [("ding", 0.2), ("chime", 0.75)]),
    S("whiskers", "Four, two, one... four hundred and twenty one continents!", "map", "m_421"),
    S("pip", "No, silly! Four plus two plus one makes seven!", "map", "m_sum",
      [("pop", 0.3), ("pop", 0.55), ("chime", 0.85)]),
    A("map", 1.2, "m_sum2"),
    S("albert", "Follow me! Off we go!", "map", "m_go", [("caw", 0.0)]),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("flap", 0.4)]),

    # ------------------------------------------------------------------ tour
    A("tour", 1.6, "u_eu", [("whoosh", 0.1)]),
    S("luna", "First, Europe. That's where we live! Remember the Eiffel Tower?", "tour", "u_eu1",
      [("pop", 0.6)]),
    S("whiskers", "Home of the finest cats!", "tour", "u_eu2"),
    A("tour", 2.2, "u_af", [("whoosh", 0.1), ("flap", 0.5)]),
    S("albert", "Africa! Lions and elephants live here. And look, the pyramids of Egypt!", "tour", "u_af1",
      [("pop", 0.15), ("roar", 0.25), ("pop", 0.62)]),
    A("tour", 0.8, "u_af2"),
    A("tour", 2.2, "u_as", [("whoosh", 0.1), ("flap", 0.5)]),
    S("albert", "Asia! It's the biggest continent of all.", "tour", "u_as1", [("ding", 0.6)]),
    A("tour", 2.4, "u_big", [("sparkle", 0.1), ("pop", 0.5)]),
    S("pip", "It's huge! Who's that, munching bamboo?", "tour", "u_as2", [("pop", 0.6)]),
    S("luna", "A giant panda! And the Great Wall of China.", "tour", "u_as3", [("pop", 0.55)]),
    A("tour", 2.2, "u_au", [("whoosh", 0.1), ("flap", 0.5)]),
    S("albert", "Australia! Kangaroos hop here, with babies in their pouches.", "tour", "u_au1",
      [("boing", 0.3), ("boing", 0.6)]),
    S("whiskers", "A pocket for babies? I'd use it for snacks.", "tour", "u_au2"),
    A("tour", 1.0, "u_au3"),
    A("tour", 2.4, "u_an", [("whoosh", 0.1), ("flap", 0.4)]),
    S("albert", "Next stop, the bottom of the world: Antarctica!", "tour", "u_an1"),
    S("whiskers", "The bottom of the world? A warm, sunny beach! Sunglasses on!", "tour",
      "u_an2", [("pop", 0.8)]),
    A("tour", 1.6, "u_land", [("whoosh", 0.2)]),

    # ------------------------------------------------------------------- ice
    A("ice", 1.6, "i_open", [("wind", 0.0), ("poof", 0.62)]),
    A("ice", 1.8, "i_freeze", [("crackle", 0.1), ("brr", 0.6)]),
    S("whiskers", "B-b-b-brr! Where's the b-b-beach?", "ice", "i_brr"),
    S("albert", "Ha ha! Antarctica is the coldest place on Earth, all covered in thick ice!", "ice",
      "i_cold", [("wind", 0.4)]),
    S("luna", "Nobody lives here all year. Scientists only visit.", "ice", "i_people"),
    A("ice", 2.0, "i_penguins", [("squeak", 0.2), ("squeak", 0.5), ("squeak", 0.75)]),
    S("pip", "But the penguins love it!", "ice", "i_pip"),
    S("whiskers", "I knew that. I froze on purpose. To stay fresh.", "ice", "i_purpose"),
    A("ice", 1.4, "i_laugh"),
    S("albert", "Come on, frosty! Somewhere warmer!", "ice", "i_go"),
    A("ice", 1.6, "i_off", [("whoosh", 0.2), ("flap", 0.3)]),

    # ----------------------------------------------------------------- tour2
    A("tour2", 2.6, "v_sa", [("whoosh", 0.1), ("flap", 0.5)]),
    S("albert", "South America! The Amazon, the biggest rainforest in the world.", "tour2", "v_sa1",
      [("pop", 0.6)]),
    S("pip", "And llamas, high up in the mountains!", "tour2", "v_sa2", [("pop", 0.3)]),
    A("tour2", 2.2, "v_na", [("whoosh", 0.1), ("flap", 0.5)]),
    S("albert", "North America! Bald eagles soar here, and big bison roam.", "tour2",
      "v_na1", [("pop", 0.3), ("pop", 0.7)]),
    A("tour2", 2.4, "v_all", [("whoosh", 0.05)] + [("ding", 0.35 + 0.08 * i) for i in range(7)]),
    S("luna", "Seven continents, all around the world!", "tour2", "v_all1", [("chime", 0.6)]),
    S("albert", "Now I'll glide home. Goodbye, friends!", "tour2", "v_bye", [("caw", 0.7)]),
    A("tour2", 2.0, "v_bye2", [("flap", 0.1), ("whoosh", 0.4)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. The Earth's land is split into seven continents.", "remember", "r_f1",
      [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. Asia is the biggest continent.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Antarctica is the coldest continent, covered in ice.", "remember", "r_f3",
      [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! How many continents are there? Five, or seven?", "quiz", "q1"),
    A("quiz", 1.3, "q1_count", TICKS),
    S("narrator", "Seven! Four A's, two Americas, and Europe!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Which continent is the coldest? Africa, or Antarctica?", "quiz", "q2"),
    A("quiz", 1.3, "q2_count", TICKS),
    S("narrator", "Antarctica! Brrr! Well done!", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.6, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home.", "home", "h_narr"),
    S("pip", "Seven continents in one day!", "home", "h_pip",
      [("spin", 0.4)]),
    S("whiskers", "Sure. But first, a nap. A nice, warm one.", "home", "h_nap"),
    A("home", 1.4, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, the five oceans! Goodnight!", "home", "h_next", [("sparkle", 0.2)]),
    A("home", 3.0, "h_end"),
]
