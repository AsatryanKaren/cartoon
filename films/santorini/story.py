"""Film: "Whiskers and the Missing Sun" -- Whiskers and Luna go to Santorini.

It has rained for a whole week. Luna builds a giant jigsaw of Santorini's
famous sunset, but the very last piece -- the sun -- is missing ("don't look
at me," says Whiskers, who has been sitting in the same spot all day). A
dripping pelican, Captain Stelios, lands on the windowsill on his way home to
Santorini and flies the cats (and stowaway Pip) there in his beak pouch.
At the old port Whiskers tries to steal an octopus from a taverna's drying
line, which slingshots him into the harbour. Too lazy for the 588 zig-zag
steps, he rides Fasolaki the donkey -- until he hears her puff, and learns
that she has carried visitors up the cliff all her life but never once seen
the Oia sunset. So Whiskers carries her bags, and the friends walk the
clifftop path together, past windmills and chapel bells, to Oia, where the
whole crowd claps as the sun sinks into the sea. Back home the missing sun
turns up stuck to Whiskers' bottom. Moral: any load is lighter when friends
share it.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.santorini import sounds

TITLE = "Whiskers and the Missing Sun"
PLACE = "Santorini"            # folder in the catcute library
SCENES = ["title", "puzzle", "flight", "harbour", "steps", "path", "sunset", "home"]

CAST = {
    **CAST,
    # Captain Stelios: a big, jolly old pelican in a fisherman's cap, flying home to Santorini
    "stelios": Voice("bm_daniel", 0.98, -2, ["Daniel"], 168, "en-gb+m1", 32, 150),
    # Fasolaki ("little green bean"): a gentle, hard-working old donkey of the zig-zag steps
    "fasolaki": Voice("af_aoede", 0.94, -1, ["Kathy"], 170, "en-us+f2", 46, 155),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "stelios": (150, 225, 255),
    "fasolaki": (255, 225, 150),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
# Island colour: bright major for the sea and sky, Greek minor (Am Dm E Am) for dances and longing
ISLAND = [(57, MIN), (62, MIN), (64, MAJ), (57, MIN)]
MOODS = {
    "s_title":   dict(bpm=72, prog=[(64, MAJ), (61, MIN), (57, MAJ), (59, MAJ)], drums=False, mel=0.5, oct=76, vol=0.8),
    "s_rain":    dict(bpm=66, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MIN)], drums=False, mel=0.3, oct=74, vol=0.6),
    "s_dream":   dict(bpm=80, prog=[(64, MAJ), (69, MAJ), (61, MIN), (66, MIN)], drums=False, mel=0.5, oct=81, vol=0.7),
    "s_pelican": dict(bpm=108, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.65, oct=74, vol=0.78),
    "s_fly":     dict(bpm=88, prog=[(62, MAJ), (67, MAJ), (64, MIN), (69, MAJ)], drums=False, mel=0.55, oct=78, vol=0.8),
    "s_caldera": dict(bpm=64, prog=[(64, MAJ), (59, MAJ), (61, MIN), (57, MAJ)], drums=False, mel=0.4, oct=79, vol=0.85),
    "s_port":    dict(bpm=120, prog=ISLAND, drums=True, mel=0.75, oct=76, vol=0.8),
    "s_octopus": dict(bpm=150, prog=[(57, MIN), (56, MAJ), (57, MIN), (64, MAJ)], drums=True, mel=0.85, oct=74, vol=0.82),
    "s_donkey":  dict(bpm=96, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=74, vol=0.78),
    "s_tired":   dict(bpm=60, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=False, mel=0.25, oct=74, vol=0.58),
    "s_resolve": dict(bpm=76, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.7),
    "s_walk":    dict(bpm=112, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.7, oct=78, vol=0.8),
    "s_hurry":   dict(bpm=138, prog=ISLAND, drums=True, mel=0.8, oct=76, vol=0.82),
    "s_sunset":  dict(bpm=58, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.4, oct=79, vol=0.85),
    "s_clap":    dict(bpm=126, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.75, oct=78, vol=0.85),
    "s_home":    dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "s_title", "puzzle": "s_rain", "flight": "s_fly", "harbour": "s_port", "steps": "s_donkey",
         "path": "s_walk", "sunset": "s_sunset", "home": "s_home"}
MUSIC_CUES = [("pz_luna", 0.0, "s_dream"), ("pz_land", 0.0, "s_pelican"), ("fl_dawn", 0.3, "s_caldera"),
              ("hb_mine", 0.0, "s_octopus"), ("hb_oia", 0.0, "s_port"), ("st_puff", 0.0, "s_tired"),
              ("st_carry", 0.0, "s_resolve"), ("pa_hurry", 0.0, "s_hurry"), ("su_clap", 0.0, "s_clap"),
              ("su_end", 0.5, "s_fly")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("waves", 0.0), ("gull", 0.4)]),
    S("narrator", "Whiskers and the Missing Sun.", "title", "t_name"),
    A("title", 1.0, "t_hold", [("bell", 0.2)]),

    # --------------------------------------------------------------- puzzle
    A("puzzle", 1.0, "pz_open", [("rain", 0.0)]),
    S("narrator", "It had rained all week, and the cats hadn't seen the sun even once.",
      "puzzle", "pz_narr", [("rain", 0.3)]),
    S("narrator", "So Luna built a giant puzzle of the Greek island of Santorini.", "puzzle", "pz_build"),
    S("luna", "White houses, blue domes... and in Oia, everybody claps when the sun goes down!", "puzzle", "pz_luna"),
    A("puzzle", 1.0, "pz_look", [("rain", 0.1)]),
    S("luna", "But look. The very last piece is missing. The sun!", "puzzle", "pz_missing"),
    S("whiskers", "Don't look at me. I've been sitting right here all day.", "puzzle", "pz_sit"),
    A("puzzle", 1.0, "pz_land", [("flap", 0.0), ("gulp", 0.75)]),
    S("stelios", "Kalispera, little cats! I'm flying home to Santorini, where the sun always shines.", "puzzle", "pz_stelios"),
    S("whiskers", "Do they have fish there?", "puzzle", "pz_fish"),
    S("stelios", "Grilled octopus! Tomato fritters! Hop in my beak, there's plenty of room.",
      "puzzle", "pz_hop"),
    A("puzzle", 1.2, "pz_jump", [("meow", 0.15), ("gulp", 0.4), ("gulp", 0.7)]),
    S("pip", "Wait for me!", "puzzle", "pz_pip", [("gulp", 0.8)]),
    A("puzzle", 0.6, "pz_end", [("flap", 0.2)]),

    # --------------------------------------------------------------- flight
    S("narrator", "So off they flew, tucked inside a pelican's beak, far away to the south.", "flight", "fl_narr",
      [("flap", 0.1), ("whoosh", 0.6)]),
    A("flight", 1.8, "fl_fly", [("flap", 0.2), ("flap", 0.7)]),
    S("whiskers", "It smells like a fish shop in here. I love it.", "flight", "fl_smell"),
    A("flight", 1.4, "fl_dawn", [("flap", 0.3)]),
    S("narrator", "At sunrise they saw it: a ring of cliffs in the deep blue sea, around a sleeping volcano.",
      "flight", "fl_caldera", [("gull", 0.6)]),
    S("luna", "The houses look like sugar cubes, sprinkled on the cliffs!", "flight", "fl_sugar"),
    A("flight", 1.2, "fl_land", [("whoosh", 0.1), ("splash", 0.75)]),

    # -------------------------------------------------------------- harbour
    A("harbour", 0.8, "hb_open", [("waves", 0.0), ("gull", 0.5)]),
    S("stelios", "Welcome to the old port! First, breakfast at my cousin's taverna.", "harbour", "hb_welcome"),
    S("narrator", "There were tomato fritters, grilled octopus, and more octopus, hanging up to dry.",
      "harbour", "hb_narr", [("sizzle", 0.0)]),
    A("harbour", 0.8, "hb_munch", [("munch", 0.1)]),
    S("whiskers", "That big one is mine. Nobody move.", "harbour", "hb_mine"),
    A("harbour", 1.7, "hb_pull", [("stretch", 0.1), ("stretch", 0.35), ("boing", 0.55), ("whoosh", 0.6),
                                  ("splash", 0.86)]),
    S("whiskers", "I'm fine! I'm just... washing the octopus.", "harbour", "hb_wash"),
    S("luna", "Whiskers! The sunset is in Oia, at the top of the island.", "harbour", "hb_oia"),
    S("stelios", "Then up the steps you go. Five hundred and eighty-eight of them!", "harbour", "hb_steps"),
    S("whiskers", "Five hundred? I'm a cat, not a mountain goat.", "harbour", "hb_goat"),
    A("harbour", 0.6, "hb_end", [("hoof", 0.3)]),

    # ---------------------------------------------------------------- steps
    A("steps", 0.8, "st_open", [("hoof", 0.0), ("bray", 0.6)]),
    S("fasolaki", "Need a ride, little ones? I'm Fasolaki. I carry everybody up the steps.", "steps", "st_faso"),
    S("whiskers", "Finally! Someone who understands me.", "steps", "st_ride"),
    A("steps", 2.4, "st_climb", [("hoof", 0.0), ("hoof", 0.25), ("hoof", 0.5), ("hoof", 0.75)]),
    S("whiskers", "This is the life! A little faster, please!", "steps", "st_life", [("hoof", 0.2)]),
    A("steps", 1.0, "st_puff", [("hoof", 0.1)]),
    S("luna", "Whiskers, listen. She's puffing.", "steps", "st_listen"),
    S("fasolaki", "Don't worry. I've climbed these steps every day of my life.", "steps", "st_foal"),
    S("fasolaki", "I only wish I could see the Oia sunset, just once. But by evening, I'm too tired.",
      "steps", "st_wish"),
    A("steps", 1.0, "st_think"),
    S("whiskers", "Then today, nobody carries me. I carry you. Well... your bags.", "steps", "st_carry",
      [("pop", 0.1)]),
    S("luna", "And we'll all walk to Oia together!", "steps", "st_together", [("bray", 0.9)]),
    A("steps", 0.6, "st_end"),

    # ----------------------------------------------------------------- path
    S("narrator", "So the friends walked the cliff path together, past windmills, blue domes and ringing bells.",
      "path", "pa_narr", [("bells", 0.5)]),
    A("path", 2.0, "pa_walk", [("hoof", 0.1), ("hoof", 0.5), ("wind", 0.6)]),
    S("whiskers", "Heavy bags. Little legs. Very far.", "path", "pa_heavy"),
    S("pip", "I'll help! A mouse can carry a lot more than you think.", "path", "pa_pip"),
    S("fasolaki", "You know, a heavy load is lighter when friends share it.", "path", "pa_share"),
    A("path", 1.2, "pa_wind", [("wind", 0.0), ("bell", 0.6)]),
    S("luna", "Hurry! The sun is getting low!", "path", "pa_hurry"),
    A("path", 1.2, "pa_run", [("hoof", 0.0), ("hoof", 0.4)]),

    # --------------------------------------------------------------- sunset
    A("sunset", 1.0, "su_open", [("murmur", 0.0)]),
    S("narrator", "In Oia, everyone waited on the rooftops and walls.",
      "sunset", "su_narr", [("murmur", 0.4)]),
    A("sunset", 2.6, "su_sink", [("murmur", 0.0), ("sparkle", 0.8)]),
    S("fasolaki", "Oh... It's even more beautiful than I dreamed.", "sunset", "su_dream"),
    S("whiskers", "Worth every single step. Even the four hundred I complained about.", "sunset", "su_worth"),
    A("sunset", 1.8, "su_clap", [("applause", 0.0), ("cheer", 0.2), ("bray", 0.6)]),
    S("luna", "Everybody's clapping for the sun!", "sunset", "su_clap_say", [("applause", 0.0)]),
    S("stelios", "Bravo! And now, little cats, the night flight home.", "sunset", "su_home", [("flap", 0.7)]),
    A("sunset", 1.0, "su_end", [("flap", 0.2)]),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open", [("purr", 0.3)]),
    S("narrator", "Back home, the rain had stopped at last.", "home", "h_narr"),
    S("luna", "But our puzzle still has no sun.", "home", "h_puzzle"),
    A("home", 1.0, "h_stand", [("pop", 0.5)]),
    S("pip", "Whiskers! It's stuck on your bottom!", "home", "h_bottom"),
    S("whiskers", "I was keeping it warm. On purpose.", "home", "h_purpose"),
    A("home", 1.4, "h_piece", [("click", 0.3), ("sparkle", 0.45), ("applause", 0.65)]),
    S("narrator", "Because any load feels lighter, and any road feels shorter, when friends share it.",
      "home", "h_moral"),
    A("home", 2.6, "h_end", [("purr", 0.2)]),
]
