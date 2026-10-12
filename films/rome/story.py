"""Film: "Whiskers and the Wishing Coin" -- the cats travel to Rome.

A postcard of the Trevi Fountain blows in through the window. Pip lends the
cats his lucky coin to make a wish, they take the train to Rome, meet Nico the
pigeon tour guide and Rosa the pizza cat, lose the coin in the pizza chaos --
and lazy Whiskers runs all the way back across Rome to find it.
"""
from common import *  # noqa: F401,F403
from films.rome.sounds import EXTRA_SFX  # noqa: F401

TITLE = "Whiskers and the Wishing Coin"
PLACE = "Rome"            # folder in the catcute library
SCENES = ["title", "postcard", "train", "streets", "colosseum", "piazza", "fountain", "wish", "home"]

CAST = {
    **CAST,
    "nico": Voice("im_nicola", 1.0, 1, ["Alex"], 186, "it+m3", 55, 165),
    "rosa": Voice("if_sara", 1.0, 0, ["Alice"], 180, "it+f2", 60, 160),
}
SUBTITLE_COLORS = {**SUBTITLE_COLORS, "nico": (190, 245, 205), "rosa": (255, 240, 150)}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # sunny Roman waltz-ish strolling tune
    "roma":       dict(bpm=104, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.7, oct=76, vol=0.8),
    # quick tarantella feel for the chases
    "tarantella": dict(bpm=150, prog=[(57, MIN), (62, MIN), (52, MAJ), (57, MIN)], drums=True, mel=0.85, oct=81,
                       vol=0.85),
    "trainride":  dict(bpm=126, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=True, mel=0.6, oct=74,
                       vol=0.8),
    "ancient":    dict(bpm=76, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.45, oct=76,
                       vol=0.75),
    "worry":      dict(bpm=66, prog=[(62, MIN), (58, MAJ), (55, MIN), (57, MAJ)], drums=False, mel=0.3, oct=74,
                       vol=0.65),
    "starry":     dict(bpm=70, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=79,
                       vol=0.7),
}
MUSIC = {"title": "title", "postcard": "morning", "train": "trainride", "streets": "roma",
         "colosseum": "ancient", "piazza": "tarantella", "fountain": "roma", "wish": "starry", "home": "home"}
MUSIC_CUES = [("fo_reach", 0.3, "worry"), ("fo_run", 0.0, "tarantella"), ("fo_found", 0.0, "roma")]

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("bells", 0.1)]),
    S("narrator", "Whiskers and the Wishing Coin.", "title", "t_name"),
    A("title", 1.2, "t_hold"),

    # ------------------------------------------------------------- postcard
    A("postcard", 1.4, "p_sleep", [("purr", 0.1)]),
    S("narrator", "One sunny morning, a postcard blew in through the window.",
      "postcard", "p_card", [("whoosh", 0.3)]),
    S("whiskers", "Hey! Who throws mail at a sleeping cat?", "postcard", "p_hey"),
    S("luna", "Whiskers, look! It's from Rome!", "postcard", "p_look"),
    A("postcard", 1.6, "p_zoom", [("sparkle", 0.1)]),
    S("luna", "It says: toss a coin in the Trevi Fountain, and your wish comes true.", "postcard", "p_read"),
    S("whiskers", "Rome? Isn't that where pizza comes from?", "postcard", "p_pizza"),
    S("luna", "Pizza, gelato, and wishes! Let's go!", "postcard", "p_go"),
    A("postcard", 1.2, "p_pip_in"),
    S("pip", "Wait! Take my lucky coin, and make a wish for me too!", "postcard", "p_pip", [("clink", 0.7)]),
    S("luna", "We will, Pip. I'll keep it safe, right here on my collar.", "postcard", "p_collar", [("clink", 0.8)]),
    A("postcard", 0.8, "p_end"),

    # ---------------------------------------------------------------- train
    S("narrator", "So the two cats hopped on the morning train, all the way to Italy.", "train", "tr_narr",
      [("whistle", 0.1), ("chug", 0.5)]),
    A("train", 2.0, "tr_ride", [("chug", 0.0), ("chug", 0.5)]),
    S("whiskers", "Are we there yet?", "train", "tr_yet"),
    S("luna", "Not yet.", "train", "tr_not"),
    A("train", 1.0, "tr_ride2", [("chug", 0.0)]),
    S("whiskers", "How about now?", "train", "tr_now"),
    S("luna", "Whiskers! Look outside!", "train", "tr_look"),
    A("train", 2.0, "tr_view", [("chug", 0.0), ("chug", 0.45)]),
    S("narrator", "Past olive groves and umbrella pines, the train rolled into Rome.", "train", "tr_rome",
      [("whistle", 0.6)]),
    A("train", 1.0, "tr_end", [("bells", 0.0)]),

    # -------------------------------------------------------------- streets
    A("streets", 1.6, "st_walk"),
    S("luna", "Narrow streets, flower boxes, and so many smells!", "streets", "st_luna"),
    S("whiskers", "Mostly pizza smells. I approve.", "streets", "st_wh"),
    A("streets", 1.6, "st_vespa", [("vespa", 0.0), ("whoosh", 0.35)]),
    S("whiskers", "Whoa! Who taught that bicycle to roar?", "streets", "st_whoa"),
    S("nico", "Ha! That is a Vespa, my friends. Welcome to Rome!", "streets", "st_nico", [("flutter", 0.0)]),
    A("streets", 0.8, "st_land", [("coo", 0.4)]),
    S("nico", "I am Nico, the best tour guide in the city. And I work for crumbs.", "streets", "st_intro"),
    S("luna", "We're looking for the Trevi Fountain. We have a wish to make!", "streets", "st_goal"),
    S("nico", "Ah, the fountain! Follow me. But first, a little tour!", "streets", "st_follow",
      [("flutter", 0.9)]),
    A("streets", 1.2, "st_end"),

    # ------------------------------------------------------------ colosseum
    A("colosseum", 2.0, "co_reveal"),
    S("nico", "Behold! The Colosseum! Almost two thousand years old!", "colosseum", "co_nico"),
    S("whiskers", "A giant cheese grater, with a bite out of it!", "colosseum", "co_cheese"),
    S("luna", "Whiskers, climb up there. You look like a hero!", "colosseum", "co_hero"),
    A("colosseum", 1.8, "co_pose", [("meow", 0.35), ("flutter", 0.7), ("coo", 0.85)]),
    S("whiskers", "Hero of Rome! Now, which way to lunch?", "colosseum", "co_lunch"),
    A("colosseum", 1.0, "co_end"),

    # --------------------------------------------------------------- piazza
    A("piazza", 1.2, "pz_arrive"),
    S("narrator", "In a little piazza, Rosa the cat was spinning pizza dough.",
      "piazza", "pz_narr"),
    S("rosa", "Ciao, little travellers! Hungry?", "piazza", "pz_ciao"),
    S("whiskers", "Signora, I was born hungry.", "piazza", "pz_born"),
    A("piazza", 2.6, "pz_toss", [("whoosh", 0.1), ("whoosh", 0.45), ("splat", 0.72)]),
    S("whiskers", "I meant to do that. Pizza hats are very fashionable.", "piazza", "pz_hat"),
    S("rosa", "Bravo! Then you get the very first slice.", "piazza", "pz_bravo"),
    A("piazza", 2.0, "pz_eat", [("clink", 0.3)]),
    S("luna", "Now, to the fountain, before the sun goes down!", "piazza", "pz_go"),
    A("piazza", 0.8, "pz_end"),

    # ------------------------------------------------------------- fountain
    A("fountain", 1.8, "fo_arrive", [("fountain", 0.0), ("fountain", 0.6)]),
    S("nico", "Ecco! The Trevi Fountain!", "fountain", "fo_ecco"),
    S("luna", "It's even more beautiful than the postcard.", "fountain", "fo_beauty", [("fountain", 0.2)]),
    A("fountain", 1.2, "fo_reach"),
    S("luna", "Oh no. Pip's coin. It's gone!", "fountain", "fo_gone"),
    S("luna", "It was his lucky coin. I promised to keep it safe.", "fountain", "fo_sad"),
    A("fountain", 1.2, "fo_think"),
    S("whiskers", "Wait here. I know where it is.", "fountain", "fo_wait"),
    S("narrator", "And Whiskers, the laziest cat in the world, ran all the way back.",
      "fountain", "fo_run", [("whoosh", 0.05)]),
    A("fountain", 1.5, "fo_dash", [("whoosh", 0.1), ("vespa", 0.2), ("whoosh", 0.55)]),
    A("fountain", 1.4, "fo_munch", [("splat", 0.15), ("splat", 0.4), ("clink", 0.8), ("sparkle", 0.8)]),
    A("fountain", 1.4, "fo_back", [("pant", 0.3)]),
    S("whiskers", "Found it. It was baked into my second slice.", "fountain", "fo_found", [("clink", 0.05)]),
    S("whiskers", "So I had to eat the whole pizza to find it. On purpose.", "fountain", "fo_purpose"),
    S("luna", "Oh, Whiskers. You ran all that way, for me and Pip.", "fountain", "fo_thanks"),
    A("fountain", 1.2, "fo_hug", [("purr", 0.1)]),

    # ----------------------------------------------------------------- wish
    S("nico", "Now turn around, and toss it over your shoulder. The Roman way!", "wish", "wi_how",
      [("fountain", 0.0)]),
    A("wish", 2.2, "wi_toss", [("whoosh", 0.15), ("sparkle", 0.35), ("plink", 0.62)]),
    S("luna", "What did you wish for, Whiskers?", "wish", "wi_ask"),
    S("whiskers", "A nap. And more pizza.", "wish", "wi_nap"),
    A("wish", 0.8, "wi_beat"),
    S("whiskers", "And that one day, we come back here with Pip.", "wish", "wi_pip"),
    S("luna", "That's exactly what I wished for too.", "wish", "wi_same"),
    S("nico", "Arrivederci, my friends! Come back soon!", "wish", "wi_bye", [("flutter", 0.6)]),
    A("wish", 1.4, "wi_end", [("bells", 0.1)]),

    # ----------------------------------------------------------------- home
    S("narrator", "Two days later, the train brought two tired cats home again.", "home", "h_narr",
      [("whistle", 0.3)]),
    A("home", 1.4, "h_arrive"),
    S("pip", "You're back! Did you make the wish?", "home", "h_pip"),
    S("luna", "We did. And Whiskers brought you something.", "home", "h_brought"),
    A("home", 1.0, "h_gift"),
    S("whiskers", "Real Roman pizza. I only ate half of it.", "home", "h_slice"),
    S("pip", "Best present ever!", "home", "h_best"),
    A("home", 1.2, "h_sill", [("purr", 0.2)]),
    S("narrator", "That night, three friends dreamed of fountains and pizza.",
      "home", "h_night"),
    S("narrator", "Because a wish is sweetest, when you make it for a friend.", "home", "h_moral"),
    A("home", 3.0, "h_end"),
]
