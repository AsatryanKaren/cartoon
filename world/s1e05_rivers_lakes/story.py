"""Whiskers & Luna's World, Episode 5: "Rivers and Lakes".

On a rainy morning Whiskers grumbles at the rain on the window: where does it all go? On an
adventure, says Luna -- into rivers, and down to the sea. The friends fly into the magic map:
blue lines are rivers, all over the world. The Nile in Africa is very, very long; the Amazon in
South America is the biggest river, carrying the most water. They fly to the snowy Alps, where a
little cloud lets go of Drip, a talking raindrop. The sun melts the snow too (like the snow on
Everest), tiny streams run down the mountain and join together into a river. Riding the cushion
down the river with Drip, they meet Ollie the otter, sliding past: rivers always flow downhill.
Whiskers dropped his fish snack at the top and tries to paddle back up the river -- and slides
backwards down it ("on purpose. It's called relaxing."). The river flows into a big calm lake,
water with land all around; careful Whiskers (remembering the salty sea) tastes it: fresh, not
salty! The river flows on to the sea, where the warm sun lifts Drip up as invisible vapour into
a cloud, and he will fall as rain on the mountains again: the water cycle, round and round.
Back home the rain has stopped, and a raindrop on the window winks.

Facts: 1) rivers flow downhill to the sea; 2) river and lake water is fresh, not salty;
3) water goes round and round in the water cycle.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from world import kit as K
from world.s1e05_rivers_lakes import sounds

TITLE = "05 - Rivers and Lakes"
PLACE = "World/Season 1"
SCENES = ["title", "sill", "map", "peak", "river", "lake", "sea", "remember", "quiz", "home"]

CAST = {
    **CAST,
    # Ollie: a playful, bouncy river otter who loves sliding down the river
    "ollie": Voice("am_liam", 1.04, 1, ["Fred"], 182, "en-us+m2", 55, 165),
    # Drip: a tiny, cheerful talking raindrop
    "drip": Voice("bf_lily", 1.06, 3, ["Kate"], 190, "en-gb+f4", 85, 175),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "ollie": (230, 200, 150), "drip": (150, 220, 255)}

MOODS = {**K.KIT_MOODS, **sounds.MOODS}
MUSIC = {"title": "w_intro", "sill": "w_home", "map": "w_wonder", "peak": "w_wonder", "river": "w_river",
         "lake": "w_lake", "sea": "w_sea", "remember": "w_remember", "quiz": "w_quiz", "home": "w_night"}
MUSIC_CUES = [("m_flat", 0.3, "w_map"), ("p_jump", 0.5, "w_river"), ("v_snack", 0.0, "w_funny"),
              ("v_on", 0.0, "w_river"), ("l_last", 0.0, "w_funny"), ("l_animals", 0.0, "w_lake"),
              ("e_up", 0.0, "w_wonder")]
EXTRA_SFX = {**K.KIT_SFX, **sounds.EXTRA_SFX}

S = Say
A = Act
TICKS = [("tick", 0.0), ("tick", 0.333), ("tick", 0.667)]

SCRIPT = [
    # ----------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("sparkle", 0.1), ("spin", 0.3)]),
    S("narrator", "Whiskers and Luna's World. Episode five. Rivers and Lakes!", "title", "t_name"),
    A("title", 1.2, "t_hold", [("sparkle", 0.2)]),

    # ------------------------------------------------------------------ sill
    A("sill", 1.4, "s_open", [("rain", 0.0)]),
    S("narrator", "One rainy morning, the rain went pitter patter on the window.", "sill", "s_narr",
      [("rain", 0.2)]),
    S("whiskers", "Rain, rain, go away. Where does all this rain go, anyway?", "sill", "s_where"),
    S("luna", "On a big adventure, Whiskers! Rain runs into rivers, and rivers run all the way to the sea.",
      "sill", "s_adv", [("spin", 0.2)]),
    A("sill", 1.2, "s_advact", [("plip", 0.1), ("plip", 0.5)]),
    S("pip", "Let's follow one little raindrop, all the way!", "sill", "s_follow"),
    S("luna", "Hold on to the cushion!", "sill", "s_hold", [("spin", 0.3)]),
    A("sill", 2.0, "s_glow", [("sparkle", 0.0), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------- map
    A("map", 1.4, "m_fly", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("narrator", "Up into space they flew!", "map", "m_narr", [("spin", 0.5)]),
    A("map", 2.4, "m_flat", [("whoosh", 0.1), ("sparkle", 0.6)]),
    S("luna", "Look! The blue lines are rivers. They're everywhere!", "map", "m_rivers", [("sparkle", 0.5)]),
    A("map", 1.2, "m_riv", [("ding", 0.2)]),
    S("luna", "This is the Nile, in Africa. It's very, very long!", "map", "m_nile", [("ding", 0.1)]),
    A("map", 1.6, "m_nileact", [("sparkle", 0.2)]),
    S("luna", "And this is the Amazon, in South America. It's the biggest river, carrying the most water!",
      "map", "m_amazon", [("ding", 0.1)]),
    A("map", 1.4, "m_amzact", [("splash", 0.2)]),
    S("whiskers", "The most water? That's a lot of bath time.", "map", "m_bath"),
    A("map", 0.8, "m_laugh"),
    S("luna", "Our raindrop's journey starts up in the mountains. To the Alps!", "map", "m_alps"),
    A("map", 3.0, "m_path", [("whoosh", 0.05), ("whoosh", 0.7)]),

    # ------------------------------------------------------------------ peak
    A("peak", 1.6, "p_land", [("sparkle", 0.2), ("pop", 0.7)]),
    S("narrator", "High in the snowy Alps, a little cloud was full of rain.", "peak", "p_narr"),
    A("peak", 1.4, "p_drop", [("plip", 0.2), ("plip", 0.5), ("plip", 0.85)]),
    S("drip", "Wheee! Hello! I'm Drip, a raindrop!", "peak", "p_hello", [("pop", 0.05)]),
    S("pip", "Hello, Drip! Where are you going?", "peak", "p_where"),
    S("drip", "Downhill! And look, the sun is melting the snow. More drops are coming with me!", "peak",
      "p_melt", [("sparkle", 0.3)]),
    A("peak", 1.6, "p_meltact", [("plip", 0.1), ("plip", 0.3), ("plip", 0.55), ("babble", 0.6)]),
    S("luna", "Melting snow, just like on Mount Everest. Tiny streams are running down the mountain!",
      "peak", "p_streams", [("babble", 0.2)]),
    A("peak", 1.8, "p_join", [("babble", 0.1)]),
    S("drip", "And when the streams join together, they make a river!", "peak", "p_river", [("ding", 0.5)]),
    A("peak", 1.2, "p_riveract", [("sparkle", 0.2)]),
    S("drip", "Come on! Jump in!", "peak", "p_jump"),
    A("peak", 1.6, "p_go", [("splash", 0.35), ("wheee", 0.5)]),

    # ----------------------------------------------------------------- river
    A("river", 1.4, "v_open", [("babble", 0.0)]),
    S("ollie", "Wheee! Make way! Otter coming through!", "river", "v_hello", [("wheee", 0.0), ("splash", 0.7)]),
    S("ollie", "Hi! I'm Ollie the otter. This river is my playground!", "river", "v_name"),
    S("pip", "Ollie, why does the river keep going down, down, down?", "river", "v_why"),
    S("ollie", "Rivers always flow downhill. From the high mountains, down to the low sea.", "river",
      "v_down", [("ding", 0.6)]),
    A("river", 1.8, "v_downact", [("whoosh", 0.1), ("sparkle", 0.5)]),
    S("whiskers", "Wait! I dropped my fish snack up there! Paddle back up, everyone!", "river", "v_snack"),
    A("river", 2.6, "v_paddle", [("paddle", 0.05), ("paddle", 0.35), ("boing", 0.62), ("wheee", 0.68)]),
    S("ollie", "Ha ha! You can't paddle up a river, Whiskers. The water always runs downhill!", "river",
      "v_cant"),
    S("whiskers", "I knew that. I was going backwards on purpose. It's called... relaxing.", "river",
      "v_purpose"),
    A("river", 1.0, "v_laugh"),
    A("river", 1.4, "v_on", [("wheee", 0.2), ("splash", 0.8)]),

    # ------------------------------------------------------------------ lake
    A("lake", 1.4, "l_open", [("quack", 0.6)]),
    S("narrator", "Then the river flowed into a big, calm lake.", "lake", "l_narr"),
    S("ollie", "A lake is a big pool of water, with land all around it.", "lake", "l_what", [("pop", 0.5)]),
    A("lake", 1.6, "l_whatact", [("ding", 0.2)]),
    S("whiskers", "Hmm. Last time I drank from the sea, it was salty. Bleh!", "lake", "l_last"),
    A("lake", 1.4, "l_sip", [("lap", 0.25), ("lap", 0.45), ("lap", 0.65)]),
    S("whiskers", "Hey! This water isn't salty at all!", "lake", "l_fresh", [("ding", 0.0)]),
    S("ollie", "River and lake water is fresh, not salty. That's why so many animals drink it.", "lake",
      "l_animals", [("quack", 0.7)]),
    A("lake", 1.6, "l_drinkact", [("lap", 0.2), ("quack", 0.6)]),
    S("drip", "The river flows on, out of the lake. Next stop, the sea!", "lake", "l_next"),
    A("lake", 1.6, "l_go", [("wheee", 0.3)]),

    # ------------------------------------------------------------------- sea
    A("sea", 1.4, "e_open", [("waves", 0.1)]),
    S("narrator", "At last, the river reached the big, salty sea.", "sea", "e_narr"),
    S("drip", "I made it! From the mountains, all the way to the sea!", "sea", "e_made", [("splash", 0.1)]),
    S("pip", "Is this the end of your journey, Drip?", "sea", "e_end"),
    S("drip", "Oh no! The warm sun is lifting me up, up, up!", "sea", "e_up", [("rise", 0.2)]),
    A("sea", 1.8, "e_rise", [("rise", 0.0), ("sparkle", 0.6)]),
    S("luna", "The sun warms the water, and it rises as invisible vapour. It makes the clouds!", "sea",
      "e_vapour"),
    A("sea", 1.0, "e_cloud", [("pop", 0.4)]),
    S("drip", "And then I fall as rain again, back on the mountains!", "sea", "e_rain", [("plip", 0.6)]),
    A("sea", 3.2, "e_cycle", [("whoosh", 0.05), ("ding", 0.2), ("ding", 0.45), ("ding", 0.7), ("ding", 0.95)]),
    S("luna", "That's the water cycle. Water goes round and round, again and again!", "sea", "e_round",
      [("sparkle", 0.5)]),
    A("sea", 1.2, "e_roundact", [("spin", 0.1)]),
    S("ollie", "Bye bye, Drip! See you next time it rains!", "sea", "e_bye"),
    A("sea", 1.2, "e_byeact", [("sparkle", 0.3)]),

    # -------------------------------------------------------------- remember
    A("remember", 0.8, "r_open", [("sparkle", 0.2)]),
    S("narrator", "Remember! One. Rivers flow downhill, all the way to the sea.", "remember", "r_f1",
      [("ding", 0.05)]),
    A("remember", 0.9, "r_p1"),
    S("narrator", "Two. River and lake water is fresh, not salty.", "remember", "r_f2", [("ding", 0.05)]),
    A("remember", 0.9, "r_p2"),
    S("narrator", "Three. Water goes round and round, in the water cycle.", "remember", "r_f3",
      [("ding", 0.05)]),
    A("remember", 1.6, "r_hold"),

    # ------------------------------------------------------------------ quiz
    A("quiz", 0.6, "q_open", [("pop", 0.2)]),
    S("narrator", "Quiz time! Does a river flow uphill, or downhill?", "quiz", "q1"),
    A("quiz", 1.0, "q1_count", TICKS),
    S("narrator", "Downhill! Well done!", "quiz", "q1_ans", [("chime", 0.0)]),
    A("quiz", 0.8, "q1_end"),
    S("narrator", "Next. Is lake water salty, or fresh?", "quiz", "q2"),
    A("quiz", 1.0, "q2_count", TICKS),
    S("narrator", "Fresh! Not salty at all.", "quiz", "q2_ans", [("chime", 0.0)]),
    A("quiz", 1.0, "q2_end"),

    # ------------------------------------------------------------------ home
    A("home", 1.4, "h_back", [("sparkle", 0.1), ("whoosh", 0.3)]),
    S("narrator", "And with a twinkle, they were home again. The rain had stopped.", "home", "h_narr"),
    S("pip", "Look! A raindrop on the window! Is that you, Drip?", "home", "h_pip", [("plip", 0.5)]),
    A("home", 1.0, "h_wink", [("sparkle", 0.2)]),
    S("whiskers", "Round and round, like me on my cushion. Goodnight.", "home", "h_nap"),
    A("home", 1.2, "h_curl", [("purr", 0.15)]),
    S("narrator", "Next time, deserts, where it hardly ever rains! Goodnight, rivers and lakes.", "home",
      "h_next", [("sparkle", 0.2)]),
    A("home", 2.6, "h_end"),
]
