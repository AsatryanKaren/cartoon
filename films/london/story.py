"""Film: "Whiskers and the Stroke of Four" -- the two cats go to London.

The old radio says that when Big Ben strikes four, all of London stops for
tea. Ruby the robin lands her Royal Air Mail balloon by the window, and the
cats (plus Pip, hidden in the mail sack) float across the sea to rainy
London. A King's Guard corgi who must not wiggle points them to the best fish
and chips -- which a cheeky seagull promptly steals. Whiskers chases the
"thief" across town on a red double-decker, up Tower Bridge, and finds three
hungry chicks. He gives them his fish, the bridge opens, the clock ticks on --
and Gus and his gull friends tow Ruby's balloon to Big Ben just as it strikes
four. Tea for everyone.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act
from films.london.sounds import EXTRA_SFX  # noqa: F401

TITLE = "Whiskers and the Stroke of Four"
PLACE = "London"            # folder in the catcute library
SCENES = ["title", "radio", "balloon", "guard", "chips", "bus", "bridge", "bigben", "home"]

CAST = {
    **CAST,
    # Ruby: a brisk, cheerful robin who flies the Royal Air Mail balloon
    "ruby": Voice("bf_lily", 1.05, 2, ["Kate"], 186, "en-gb+f4", 70, 170),
    # Biscuit: a very proper corgi King's Guard in a huge bearskin hat
    "biscuit": Voice("bm_lewis", 0.92, -1, ["Daniel"], 160, "en-gb+m1", 30, 145),
    # Gus: a scruffy, cheeky London seagull with a soft heart
    "gus": Voice("bm_fable", 1.05, 1, ["Oliver"], 184, "en-gb+m4", 55, 170),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "ruby": (255, 175, 140),
    "biscuit": (255, 230, 130),
    "gus": (185, 235, 245),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # stately, a little like a brass-band march for the title and Big Ben
    "l_title":  dict(bpm=80, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.5, oct=74, vol=0.8),
    "l_radio":  dict(bpm=98, prog=[(65, MAJ), (62, MIN), (70, MAJ), (72, MAJ)], drums=True, mel=0.55, oct=77, vol=0.75),
    "l_float":  dict(bpm=76, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=False, mel=0.5, oct=79, vol=0.75),
    "l_rain":   dict(bpm=88, prog=[(57, MIN), (62, MIN), (55, MAJ), (60, MAJ)], drums=True, mel=0.4, oct=76, vol=0.7),
    "l_guard":  dict(bpm=112, prog=[(60, MAJ), (67, MAJ), (65, MAJ), (67, MAJ)], drums=True, mel=0.6, oct=72, vol=0.8),
    "l_chips":  dict(bpm=104, prog=[(62, MAJ), (59, MIN), (67, MAJ), (69, MAJ)], drums=True, mel=0.65, oct=74, vol=0.8),
    "l_chase":  dict(bpm=150, prog=[(57, MIN), (65, MAJ), (67, MAJ), (57, MIN)], drums=True, mel=0.85, oct=76, vol=0.85),
    "l_nest":   dict(bpm=64, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.3, oct=77, vol=0.65),
    "l_hurry":  dict(bpm=132, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.75, oct=74, vol=0.85),
    "l_tea":    dict(bpm=92, prog=[(67, MAJ), (64, MIN), (72, MAJ), (74, MAJ)], drums=True, mel=0.55, oct=79, vol=0.75),
}
MUSIC = {"title": "l_title", "radio": "l_radio", "balloon": "l_float", "guard": "l_rain", "chips": "l_chips",
         "bus": "l_chase", "bridge": "l_nest", "bigben": "l_hurry", "home": "home"}
MUSIC_CUES = [("g_guard", 0.0, "l_guard"), ("c_swoop", 0.0, "l_chase"), ("br_open", 0.0, "l_hurry"),
              ("bb_bong", 0.0, "l_title"), ("bb_tea", 0.0, "l_tea")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("bong", 0.25)]),
    S("narrator", "Whiskers and the Stroke of Four.", "title", "t_name"),
    A("title", 1.6, "t_hold", [("chime", 0.1)]),

    # ---------------------------------------------------------------- radio
    A("radio", 1.2, "r_open", [("purr", 0.1)]),
    S("narrator", "One grey morning, the old radio crackled to life.", "radio", "r_narr",
      [("static", 0.6)]),
    A("radio", 0.7, "r_bong", [("bong", 0.1)]),
    S("narrator", "This is London. And when Big Ben strikes four, all of London stops... for tea.",
      "radio", "r_radio"),
    S("luna", "Big Ben! I want to hear it bong with my own ears!",
      "radio", "r_luna"),
    S("whiskers", "Did somebody say tea? With cakes?", "radio", "r_cakes"),
    S("whiskers", "London is across the sea, Luna. Cats don't swim.", "radio", "r_sea"),
    A("radio", 1.4, "r_balloon", [("burner", 0.2), ("burner", 0.7)]),
    S("ruby", "Royal Air Mail, coming through! Any post for London?", "radio", "r_ruby"),
    S("luna", "Us! Can you post two cats to London?", "radio", "r_post"),
    S("ruby", "Hop in, my dears! If the wind is kind, we'll land before four.", "radio", "r_hop"),
    A("radio", 1.4, "r_jump", [("whoosh", 0.15), ("whoosh", 0.5), ("burner", 0.85)]),

    # -------------------------------------------------------------- balloon
    S("narrator", "So the balloon floated up, over the fields and over the sea, to England.",
      "balloon", "b_narr", [("burner", 0.1)]),
    A("balloon", 1.6, "b_sail", [("gulls", 0.4)]),
    S("whiskers", "I'm not scared. I'm keeping my eyes shut on purpose.", "balloon", "b_shut"),
    A("balloon", 0.8, "b_sack", [("rustle", 0.2)]),
    S("pip", "Excuse me, is this the bag for London? Because I'm in it!", "balloon", "b_pip"),
    S("luna", "Pip! You came too!", "balloon", "b_luna"),
    A("balloon", 1.6, "b_london", [("burner", 0.3)]),
    S("ruby", "There's London! The Thames, Tower Bridge, the London Eye... and the rain.",
      "balloon", "b_ruby", [("rain", 0.8)]),
    S("ruby", "I've letters to deliver. Meet me at Big Ben at four o'clock!", "balloon", "b_meet"),
    A("balloon", 1.2, "b_land", [("burner", 0.1), ("whoosh", 0.6)]),

    # ---------------------------------------------------------------- guard
    S("narrator", "London was wet. Very wet. And cats do not like wet.", "guard", "g_narr", [("rain", 0.0)]),
    S("whiskers", "My fur! My beautiful fur! Is there anywhere dry in this city?", "guard", "g_fur",
      [("rain", 0.5)]),
    A("guard", 1.2, "g_box", [("whoosh", 0.1), ("ring", 0.55)]),
    A("guard", 0.8, "g_guard", [("march", 0.0)]),
    S("luna", "Excuse me, sir. Which way is Big Ben?", "guard", "g_ask"),
    A("guard", 1.0, "g_still"),
    S("whiskers", "Is he a statue? Hello? Boo!", "guard", "g_boo"),
    S("biscuit", "I am a King's Guard. Guards do not wiggle, giggle, or chat.", "guard", "g_rule"),
    S("biscuit", "But Big Ben is that way. And the best fish and chips are by the river.",
      "guard", "g_tip"),
    S("whiskers", "Fish? And chips? Sir, you are my hero.", "guard", "g_hero"),
    A("guard", 1.2, "g_sneeze", [("achoo", 0.25), ("whoosh", 0.4)]),

    # ---------------------------------------------------------------- chips
    S("narrator", "The rain stopped. And by the river, Whiskers found heaven, wrapped in paper.",
      "chips", "c_narr"),
    S("whiskers", "Hello, my lovely chips. Hello, my lovely fish.", "chips", "c_hello"),
    A("chips", 0.8, "c_sniff"),
    A("chips", 1.0, "c_swoop", [("squawk", 0.3), ("whoosh", 0.35)]),
    S("gus", "Ta very much, ginger!", "chips", "c_ta"),
    S("whiskers", "Hey! Thief! Come back with my fish!", "chips", "c_hey"),
    A("chips", 2.0, "c_chase", [("whoosh", 0.15), ("horn2", 0.6), ("whoosh", 0.8)]),

    # ------------------------------------------------------------------ bus
    A("bus", 1.2, "u_ride", [("engine", 0.0), ("ding", 0.3)]),
    S("luna", "Whiskers, this bus is going the wrong way! Big Ben is behind us!", "bus", "u_wrong"),
    S("whiskers", "Nobody steals a cat's fish. Nobody!", "bus", "u_nobody"),
    A("bus", 1.0, "u_gus", [("squawk", 0.4), ("engine", 0.1)]),
    S("pip", "Look at the clock! It's half past three already!", "bus", "u_half"),
    A("bus", 1.4, "u_bridge", [("engine", 0.0), ("ding", 0.8)]),

    # --------------------------------------------------------------- bridge
    A("bridge", 1.0, "br_climb"),
    S("whiskers", "Aha! Got you, you feathery... oh.", "bridge", "br_aha", [("cheep", 0.7)]),
    A("bridge", 1.0, "br_chicks", [("cheep", 0.1), ("cheep", 0.6)]),
    S("gus", "Sorry, mate. The rain stopped my fishing, and my little ones were starving.",
      "bridge", "br_sorry"),
    A("bridge", 1.0, "br_think"),
    S("whiskers", "Here. Have the fish. Have all of it. They need it more than me.", "bridge", "br_give",
      [("cheep", 0.9)]),
    S("luna", "Whiskers, that was so kind.", "bridge", "br_kind"),
    A("bridge", 0.8, "br_open", [("bells", 0.0), ("horn2", 0.5)]),
    S("pip", "The bridge is going up! And it's nearly four!", "bridge", "br_up"),
    S("luna", "We'll never get to Big Ben in time.", "bridge", "br_never"),
    S("gus", "Never say never to a seagull! Oi, lads! Fetch that balloon!", "bridge", "br_oi",
      [("squawk", 0.85)]),
    A("bridge", 1.4, "br_tow", [("squawk", 0.1), ("burner", 0.5), ("whoosh", 0.8)]),

    # --------------------------------------------------------------- bigben
    A("bigben", 1.4, "bb_fly", [("whoosh", 0.1), ("squawk", 0.4)]),
    S("ruby", "Hold on to your whiskers! Next stop, Big Ben!", "bigben", "bb_hold", [("burner", 0.9)]),
    A("bigben", 0.8, "bb_tick", [("tick", 0.0)]),
    A("bigben", 2.8, "bb_bong", [("bong", 0.05), ("bong", 0.3), ("bong", 0.55), ("bong", 0.8)]),
    S("luna", "I heard it! With my very own ears!", "bigben", "bb_heard"),
    A("bigben", 0.8, "bb_tea", [("clink", 0.5)]),
    S("narrator", "At four o'clock, high above London, everybody stopped for tea.", "bigben", "bb_narr",
      [("pour", 0.6)]),
    S("whiskers", "Scones! Jam! Cream! Is it four o'clock every day here?", "bigben", "bb_scones",
      [("clink", 0.9)]),
    S("gus", "You're alright, ginger. Sorry about your fish.", "bigben", "bb_sorry"),
    S("whiskers", "I gave it away. Completely on purpose.", "bigben", "bb_purpose"),
    A("bigben", 1.4, "bb_cheers", [("clink", 0.2), ("cheep", 0.5)]),

    # ----------------------------------------------------------------- home
    A("home", 1.6, "h_fly", [("burner", 0.3)]),
    S("narrator", "That night, the Royal Air Mail delivered two very special parcels home.", "home", "h_narr"),
    A("home", 1.2, "h_sill", [("purr", 0.2)]),
    S("luna", "Where shall we go next, Whiskers?", "home", "h_next"),
    S("whiskers", "Anywhere that stops for tea.", "home", "h_tea"),
    A("home", 1.0, "h_radio", [("bong", 0.2)]),
    S("narrator", "Because being kind might make you a little bit late. But it is never, ever the wrong time.",
      "home", "h_moral"),
    A("home", 2.8, "h_end"),
]
