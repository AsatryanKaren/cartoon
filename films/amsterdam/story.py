"""Film: "Whiskers and the Wobbly Bicycle" -- Whiskers and Luna go to Amsterdam.

A stork mailman, Joost, taps on the window with a letter from Luna's cousin
Bram, who lives on a houseboat: come to the Tulip Parade, where the whole city
rides bicycles covered in flowers. Joost flies the cats (and a stowaway Pip)
over the sea, the tulip fields and the windmills. In Amsterdam the bikes ring
at Whiskers, a giant cheese runs away with him at the cheese market, and his
first bicycle lesson ends in the canal. He wants to give up -- but everybody
wobbles at first. Luna holds his seat, lets go, and he rides on his own,
all the way to the front of the Tulip Parade.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.amsterdam import sounds

TITLE = "Whiskers and the Wobbly Bicycle"
PLACE = "Amsterdam"            # folder in the catcute library
SCENES = ["title", "letter", "flight", "canal", "market", "lesson", "dusk", "parade", "home"]

CAST = {
    **CAST,
    # Joost: a tall, kind stork mailman with a satchel
    "joost": Voice("am_eric", 0.95, -1, ["Ralph"], 165, "en-us+m2", 32, 150),
    # Bram: Luna's cheerful tuxedo cousin, who lives on a houseboat
    "bram": Voice("am_liam", 1.05, 1, ["Fred"], 184, "en-us+m4", 58, 168),
    # Mies: a jolly cow who sells cheese and stroopwafels at the market
    "mies": Voice("af_kore", 0.98, -1, ["Kathy"], 176, "en-us+f2", 45, 160),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "joost": (190, 235, 255),
    "bram": (255, 196, 110),
    "mies": (200, 245, 170),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "a_title":  dict(bpm=80, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=False, mel=0.5, oct=76, vol=0.8),
    "a_home":   dict(bpm=96, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.55, oct=77, vol=0.72),
    "a_fly":    dict(bpm=88, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.55, oct=78, vol=0.8),
    "a_tulips": dict(bpm=116, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.75, oct=79, vol=0.82),
    "a_city":   dict(bpm=126, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=True, mel=0.7, oct=76, vol=0.8),
    "a_market": dict(bpm=108, prog=[(65, MAJ), (70, MAJ), (72, MAJ), (65, MAJ)], drums=True, mel=0.65, oct=77, vol=0.78),
    "a_chase":  dict(bpm=152, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=True, mel=0.85, oct=74, vol=0.85),
    "a_lesson": dict(bpm=120, prog=[(67, MAJ), (64, MIN), (60, MAJ), (62, MAJ)], drums=True, mel=0.6, oct=79, vol=0.78),
    "a_sad":    dict(bpm=62, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.28, oct=74, vol=0.62),
    "a_try":    dict(bpm=92, prog=[(60, MAJ), (57, MIN), (53, MAJ), (55, MAJ)], drums=False, mel=0.5, oct=76, vol=0.75),
    "a_ride":   dict(bpm=124, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (72, MAJ)], drums=True, mel=0.8, oct=79, vol=0.85),
    "a_parade": dict(bpm=132, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.85, oct=79, vol=0.85),
    "a_night":  dict(bpm=62, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "a_title", "letter": "a_home", "flight": "a_fly", "canal": "a_city", "market": "a_market",
         "lesson": "a_lesson", "dusk": "a_sad", "parade": "a_parade", "home": "a_night"}
MUSIC_CUES = [("f_tulips", 0.0, "a_tulips"), ("m_roll", 0.0, "a_chase"), ("m_purpose", 0.0, "a_market"),
              ("le_splash", 0.3, "a_sad"), ("d_promise", 0.0, "a_try"), ("d_ride", 0.0, "a_ride")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.6, "t_open", [("bell", 0.3)]),
    S("narrator", "Whiskers and the Wobbly Bicycle.", "title", "t_name"),
    A("title", 1.6, "t_hold", [("bell", 0.4)]),

    # --------------------------------------------------------------- letter
    A("letter", 1.2, "l_open", [("purr", 0.1)]),
    S("narrator", "One windy spring morning, somebody tapped on the window.",
      "letter", "l_narr", [("knock", 0.72)]),
    A("letter", 0.8, "l_knock", [("knock", 0.1), ("knock", 0.55)]),
    S("whiskers", "Go away. I'm closed for napping.", "letter", "l_closed"),
    A("letter", 0.6, "l_window", [("creak", 0.1)]),
    S("joost", "Special delivery for Miss Luna! Airmail from Amsterdam!", "letter", "l_joost",
      [("clatter", 0.95)]),
    S("luna", "It's from my cousin Bram! He lives on a boat, on the canals!", "letter", "l_bram"),
    S("luna", "Come to the Tulip Parade! The whole city rides bicycles covered in flowers!",
      "letter", "l_parade"),
    S("whiskers", "Bicycles? Cats don't ride bicycles. Cats ride sofas.", "letter", "l_sofas"),
    S("luna", "And there's a cheese market. And stroopwafels, waffles with syrup inside!",
      "letter", "l_cheese"),
    A("letter", 0.6, "l_think"),
    S("whiskers", "Where is my suitcase?", "letter", "l_suitcase", [("meow", 0.9)]),
    S("joost", "Hop into my basket. I'm flying that way!", "letter", "l_hop"),
    A("letter", 1.4, "l_go", [("whoosh", 0.2), ("flap", 0.55), ("flap", 0.8)]),

    # --------------------------------------------------------------- flight
    S("narrator", "So the stork carried them over the sea, above the clouds.",
      "flight", "f_narr", [("flap", 0.1), ("gull", 0.7)]),
    A("flight", 1.6, "f_fly", [("flap", 0.2), ("flap", 0.6), ("gull", 0.4)]),
    S("whiskers", "Please don't drop us. I'm a very fragile cat.", "flight", "f_fragile"),
    A("flight", 0.9, "f_wriggle"),
    S("pip", "Surprise! Did you really think I'd miss this?", "flight", "f_pip"),
    A("flight", 0.6, "f_land"),
    S("luna", "Pip! Oh look, tulip fields! Like a giant rainbow blanket!", "flight", "f_rainbow"),
    A("flight", 1.8, "f_tulips", [("flap", 0.1), ("creak", 0.4), ("flap", 0.7)]),
    S("whiskers", "Hello, windmills! They're waving at us!", "flight", "f_mills"),
    A("flight", 1.2, "f_city", [("flap", 0.3)]),

    # ---------------------------------------------------------------- canal
    S("narrator", "In Amsterdam, tall skinny houses lined the canals, and bicycles were everywhere.",
      "canal", "c_narr", [("bell", 0.6)]),
    A("canal", 1.2, "c_walk", [("bell", 0.5), ("bell", 0.85)]),
    S("whiskers", "Whoa! Why is everybody ringing at me?", "canal", "c_ring",
      [("bell", 0.15), ("bell", 0.55), ("whoosh", 0.6)]),
    A("canal", 1.0, "c_dodge", [("bell", 0.1), ("whoosh", 0.2), ("bell", 0.5), ("whoosh", 0.6)]),
    S("bram", "Luna! Over here, on the houseboat!", "canal", "c_bram"),
    A("canal", 0.9, "c_hop", [("whoosh", 0.25), ("thud", 0.55)]),
    S("bram", "Welcome, cousins! Whiskers, orange is the luckiest colour in Holland!",
      "canal", "c_orange"),
    S("whiskers", "Finally. A city that understands me.", "canal", "c_finally"),
    A("canal", 0.8, "c_end"),

    # --------------------------------------------------------------- market
    S("narrator", "Then Bram took them to the cheese market, piled high with big yellow cheeses.",
      "market", "m_narr", [("organ", 0.0)]),
    A("market", 0.8, "m_look"),
    S("mies", "Hallo, little cats! A warm stroopwafel for each of you!", "market", "m_hallo", [("moo", 0.0)]),
    A("market", 1.2, "m_eat", [("munch", 0.3), ("munch", 0.6)]),
    S("whiskers", "Syrup... inside a waffle? This country is a genius.", "market", "m_genius"),
    A("market", 0.6, "m_lean"),
    S("mies", "Careful, Whiskers! Not that cheese, it's the biggest one!", "market", "m_careful"),
    A("market", 2.8, "m_roll", [("rumble", 0.0), ("rumble", 0.3), ("rumble", 0.55), ("clatter_clogs", 0.82)]),
    S("whiskers", "I did that on purpose. I was testing the wheels.", "market", "m_purpose"),
    S("bram", "Ha! If you can ride a cheese, you can ride a bicycle!", "market", "m_ride"),
    A("market", 0.7, "m_end"),

    # --------------------------------------------------------------- lesson
    S("narrator", "So Bram found three little bicycles, and the lesson began.", "lesson", "le_narr"),
    A("lesson", 1.2, "le_luna", [("bell", 0.6)]),
    S("luna", "Look, Whiskers! It's just like flying!", "lesson", "le_flying"),
    A("lesson", 1.8, "le_wobble", [("squeak", 0.1), ("squeak", 0.45), ("squeak", 0.8)]),
    S("whiskers", "Left, right, left... which way is up?", "lesson", "le_which", [("squeak", 0.3)]),
    A("lesson", 1.3, "le_splash", [("squeak", 0.05), ("splash", 0.3)]),
    S("whiskers", "That's it. I give up. Cats are not made for bicycles.", "lesson", "le_giveup"),
    A("lesson", 0.9, "le_drip"),

    # ----------------------------------------------------------------- dusk
    S("narrator", "That evening, Whiskers sat by the canal all alone, still dripping.",
      "dusk", "d_narr"),
    A("dusk", 1.0, "d_sit"),
    S("bram", "Every kitten in Amsterdam falls in the canal once. I fell in three times!",
      "dusk", "d_bram"),
    S("luna", "Falling off just means you're learning. The trick is getting back on.", "dusk", "d_trick"),
    S("luna", "And this time, I'll hold on to your seat. I promise.", "dusk", "d_promise"),
    A("dusk", 1.8, "d_try", [("bell", 0.1), ("squeak", 0.5)]),
    S("whiskers", "Luna, I'm doing it! Keep holding on!", "dusk", "d_doing"),
    S("luna", "I let go ages ago! You're riding all by yourself!", "dusk", "d_letgo"),
    A("dusk", 1.4, "d_ride", [("bell", 0.3), ("bell", 0.45)]),
    S("whiskers", "I'm riding! I'm really riding!", "dusk", "d_riding"),
    A("dusk", 0.6, "d_end"),

    # --------------------------------------------------------------- parade
    S("narrator", "The next morning, the Tulip Parade rolled through the city.", "parade", "p_narr",
      [("organ", 0.0)]),
    A("parade", 2.4, "p_ride", [("bell", 0.2), ("bell", 0.5), ("bell", 0.75)]),
    S("mies", "Hooray for the orange cat!", "parade", "p_hooray", [("moo", 0.9)]),
    S("pip", "Faster, Whiskers! Ring the bell!", "parade", "p_faster"),
    A("parade", 1.0, "p_bell", [("bell", 0.1), ("bell", 0.4), ("bell", 0.7)]),
    S("whiskers", "Look, Luna! Not one single wobble!", "parade", "p_wobble"),
    A("parade", 1.6, "p_end", [("clatter", 0.3), ("bell", 0.6)]),

    # ----------------------------------------------------------------- home
    A("home", 1.1, "h_fly", [("flap", 0.2), ("flap", 0.6)]),
    S("narrator", "That night, Joost flew the three friends all the way home.", "home", "h_narr"),
    A("home", 0.7, "h_sill"),
    S("joost", "Goodbye, little cyclists! Keep on pedalling!", "home", "h_bye", [("clatter", 0.95)]),
    S("pip", "Whiskers, will you teach me to ride a bicycle?", "home", "h_teach"),
    S("whiskers", "Sure, Pip. Lesson one, you fall in. Lesson two, you get back on.",
      "home", "h_lesson"),
    A("home", 1.3, "h_curl", [("purr", 0.2)]),
    S("narrator", "Because everybody wobbles at first. The brave part is getting back on.",
      "home", "h_moral"),
    A("home", 2.6, "h_end"),
]
