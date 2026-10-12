"""Film: "Whiskers and the Yellow Tram" -- Whiskers and Luna go to Lisbon.

One summer morning a wonderful smell drifts in through the window: grilled
sardines! Outside, Tiago -- a curly black Portuguese water dog on a little
yellow scooter with a sidecar -- is cooking breakfast on a tiny grill. He is
riding home to Lisbon for the Sardine Festival, when the whole city grills
sardines and dances in the streets, and he invites the cats along. Pip stays
to guard the house. They putter all day and all night across the hills of
Spain and Portugal, and at sunrise cross the big red bridge over the Tagus.
At Belem, by the old tower where the explorers' ships sailed out, Whiskers
eats a mountain of custard tarts and sneezes cinnamon all over Luna ("on
purpose -- cinnamon is good for fur"). Tiago goes to help his grandmother
with her grill and sends the cats up on tram 28: "Meet me at sunset at Avo's
house below the castle -- the one with the blue tiles." The little yellow tram
rattles up the steep hills; full of tarts, Whiskers falls asleep, and when
Luna hops off at the castle, the tram carries him away. Luna searches the
castle of Sao Jorge with Dom Pavao, a grand, kind peacock, but there are too
many roofs. Whiskers wakes at the end of the line alone, gets lost in a city
where every street goes up or down, rides the Santa Justa lift to spot the
castle, and follows his nose through the Alfama to Avo Lurdes' grill. She
offers him a sardine -- and he can't eat it: "Sardines don't taste right
without Luna." That feeling has a name in Lisbon: saudade. So Tiago and Avo
play a fado, loud enough to reach the castle; Dom Pavao knows the song and
sends Luna running down the steps. Reunited, the cats share sardines under the
paper lanterns of the festival. Tiago drives them home with Avo's gift, a
blue tile painted with two cats, which now hangs by the windowsill. Moral:
missing someone just means they live in your heart.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.lisbon import sounds

TITLE = "Whiskers and the Yellow Tram"
PLACE = "Lisbon"            # folder in the catcute library
SCENES = ["title", "sill", "ride", "belem", "tram", "castle", "lost", "alfama", "festa", "home"]

CAST = {
    **CAST,
    # Tiago: a cheerful, curly black Portuguese water dog with a yellow scooter, a grill and a guitar
    "tiago": Voice("em_alex", 0.98, 0, ["Jorge"], 176, "pt+m3", 42, 160),
    # Avo Lurdes: Tiago's grandmother, an old white water dog in a black fado shawl
    "avo": Voice("ef_dora", 0.9, -2, ["Monica"], 160, "pt+f2", 38, 150),
    # Dom Pavao: the grand, kind old peacock who keeps the castle of Sao Jorge
    "pavao": Voice("bm_fable", 0.94, -1, ["Daniel"], 162, "en-gb+m1", 34, 150),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "tiago": (255, 222, 110),
    "avo": (205, 240, 190),
    "pavao": (140, 232, 225),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "l_quiet":  dict(bpm=60, prog=[(62, MAJ), (57, MAJ), (59, MIN), (55, MAJ)], drums=False, mel=0.0, oct=74, vol=0.12),
    "l_title":  dict(bpm=76, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MAJ)], drums=False, mel=0.45, oct=76, vol=0.7),
    "l_morning": dict(bpm=104, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=77, vol=0.78),
    "l_road":   dict(bpm=112, prog=[(67, MAJ), (60, MAJ), (62, MAJ), (67, MAJ)], drums=True, mel=0.65, oct=79, vol=0.78),
    "l_night":  dict(bpm=70, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.3, oct=79, vol=0.6),
    "l_dawn":   dict(bpm=88, prog=[(62, MAJ), (67, MAJ), (59, MIN), (69, MAJ)], drums=False, mel=0.55, oct=78, vol=0.72),
    "l_river":  dict(bpm=100, prog=[(64, MAJ), (69, MAJ), (61, MIN), (71, MAJ)], drums=True, mel=0.6, oct=76, vol=0.75),
    "l_tarts":  dict(bpm=132, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.8, oct=76, vol=0.8),
    "l_tram":   dict(bpm=118, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.7, oct=74, vol=0.78),
    "l_uhoh":   dict(bpm=126, prog=[(57, MIN), (56, MAJ), (57, MIN), (52, MAJ)], drums=True, mel=0.7, oct=72, vol=0.75),
    "l_sad":    dict(bpm=60, prog=[(57, MIN), (53, MAJ), (60, MAJ), (52, MAJ)], drums=False, mel=0.25, oct=74, vol=0.6),
    "l_castle": dict(bpm=84, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MAJ)], drums=False, mel=0.4, oct=74, vol=0.66),
    "l_lost":   dict(bpm=104, prog=[(64, MIN), (60, MAJ), (62, MAJ), (59, MAJ)], drums=True, mel=0.55, oct=76, vol=0.7),
    "l_hope":   dict(bpm=96, prog=[(60, MAJ), (67, MAJ), (69, MIN), (65, MAJ)], drums=True, mel=0.6, oct=76, vol=0.75),
    "l_festa":  dict(bpm=124, prog=[(67, MAJ), (62, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.8, oct=74, vol=0.8),
    "l_warm":   dict(bpm=72, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.4, oct=77, vol=0.68),
    "l_home":   dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "l_title", "sill": "l_morning", "ride": "l_road", "belem": "l_river", "tram": "l_tram",
         "castle": "l_castle", "lost": "l_lost", "alfama": "l_sad", "festa": "l_quiet", "home": "l_home"}
MUSIC_CUES = [("r_night", 0.0, "l_night"), ("r_wake", 0.0, "l_dawn"),
              ("b_eat", 0.0, "l_tarts"), ("b_plan", 0.0, "l_river"),
              ("tr_hop", 0.4, "l_uhoh"), ("c_miss", 0.0, "l_sad"),
              ("l_lift", 0.0, "l_hope"), ("l_dusk", 0.5, "l_lost"),
              ("a_song", 0.0, "l_quiet"), ("a_hug", 0.0, "l_warm"),
              ("f_luna", 0.0, "l_warm"), ("f_fire", 0.0, "l_festa"),
              ("h_moral", 0.0, "l_home")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("tram_bell", 0.15), ("gull", 0.55)]),
    S("narrator", "Whiskers and the Yellow Tram.", "title", "t_name"),
    A("title", 0.9, "t_hold", [("guitar_flourish", 0.05)]),

    # ----------------------------------------------------------------- sill
    A("sill", 0.8, "s_open", [("sniff", 0.35), ("sniff", 0.7)]),
    S("narrator", "One summer morning, a wonderful smell floated in.", "sill", "s_narr",
      [("sizzle", 0.0)]),
    S("whiskers", "Grilled sardines? I must be dreaming.", "sill", "s_dream", [("sniff", 0.1)]),
    S("luna", "You're not dreaming! Look, a dog on a yellow scooter!", "sill", "s_look"),
    A("sill", 0.8, "s_scooter", [("scooter", 0.0), ("beep", 0.75), ("sizzle", 0.85)]),
    S("tiago", "Good morning, little cats! I'm Tiago. Would you like a sardine?", "sill", "s_tiago",
      [("sizzle", 0.0)]),
    S("whiskers", "Would I LIKE a sardine!", "sill", "s_yes"),
    A("sill", 0.7, "s_eat", [("whoosh", 0.05), ("munch", 0.45), ("munch", 0.7)]),
    S("tiago", "I'm riding home to Lisbon. Tonight the whole city grills sardines and dances!", "sill", "s_fest", [("guitar_flourish", 0.7)]),
    S("luna", "Sardines and dancing? Can we come?", "sill", "s_come"),
    S("tiago", "Of course! Hop in the sidecar!", "sill", "s_hop", [("whoosh", 0.75)]),
    S("pip", "I'll guard the house! Bring me back a story!", "sill", "s_pip"),
    A("sill", 1.0, "s_go", [("scooter", 0.0), ("beep", 0.2), ("scooter", 0.5)]),

    # ----------------------------------------------------------------- ride
    S("narrator", "So off they puttered, all day and all night.", "ride",
      "r_narr", [("scooter", 0.0), ("scooter", 0.5)]),
    A("ride", 1.5, "r_ride", [("scooter", 0.0), ("scooter", 0.35), ("beep", 0.5), ("scooter", 0.7)]),
    A("ride", 1.2, "r_night", [("scooter_soft", 0.0), ("snore", 0.4), ("snore", 0.75)]),
    S("tiago", "Wake up, friends! There it is. Lisbon, and the river Tagus!", "ride", "r_wake", [("gull", 0.6)]),
    A("ride", 1.5, "r_bridge", [("scooter", 0.0), ("bridge_hum", 0.1), ("gull", 0.5), ("scooter", 0.6)]),
    S("luna", "What an enormous red bridge!", "ride", "r_luna"),
    A("ride", 0.5, "r_end", [("scooter", 0.0)]),

    # ---------------------------------------------------------------- belem
    S("narrator", "By the river stood the Tower of Belém, where explorers once sailed out to sea.", "belem", "b_narr", [("waves", 0.0), ("gull", 0.4)]),
    A("belem", 0.9, "b_look", [("waves", 0.0), ("gull", 0.6)]),
    S("tiago", "And here they bake the best custard tarts in the world!", "belem", "b_nata",
      [("shop_bell", 0.05)]),
    S("whiskers", "One for me, and one for me, and one for me...", "belem", "b_eat",
      [("munch", 0.2), ("munch", 0.5), ("munch", 0.8)]),
    A("belem", 1.3, "b_gobble", [("munch", 0.05), ("munch", 0.2), ("munch", 0.35), ("gulp", 0.5),
                                 ("munch", 0.65), ("burp", 0.85)]),
    A("belem", 0.8, "b_sneeze", [("sniff", 0.05), ("sniff", 0.25), ("sneeze", 0.45), ("poof", 0.5)]),
    S("whiskers", "I sneezed on purpose. Cinnamon is good for fur.", "belem", "b_purpose"),
    S("tiago", "Ha! Now I must go and help my grandma.", "belem", "b_go"),
    S("tiago", "Take tram twenty-eight to the castle. Meet me at sunset at Avó's house, the one with blue tiles!", "belem", "b_plan", [("tram_bell", 0.9)]),
    S("luna", "Tram twenty-eight. Blue tiles. Come on, Whiskers!", "belem", "b_ok"),
    A("belem", 0.5, "b_end", [("scooter", 0.2)]),

    # ----------------------------------------------------------------- tram
    S("narrator", "The little yellow tram rattled up the steep, narrow hills.", "tram", "tr_narr", [("tram_run", 0.0)]),
    A("tram", 1.5, "tr_climb", [("tram_bell", 0.05), ("tram_run", 0.1), ("tram_run", 0.55), ("tram_bell", 0.8)]),
    S("luna", "Laundry lines! Painted tiles! Whiskers, look!", "tram", "tr_look", [("tram_run", 0.0)]),
    S("whiskers", "Mm-hm. I'm watching. With my eyes closed.", "tram", "tr_zzz", [("snore", 0.85)]),
    A("tram", 1.0, "tr_ride", [("tram_run", 0.0), ("snore", 0.3), ("snore", 0.7)]),
    S("luna", "Our stop, Whiskers! Come on!", "tram", "tr_stop", [("brakes", 0.0)]),
    A("tram", 0.9, "tr_hop", [("bell_jingle", 0.15), ("tram_bell", 0.5), ("tram_run", 0.6), ("snore", 0.75)]),
    S("luna", "Whiskers? Whiskers! Wait for me!", "tram", "tr_wait", [("bell_jingle", 0.2)]),
    A("tram", 0.9, "tr_gone", [("tram_bell", 0.3), ("bell_jingle", 0.1)]),

    # --------------------------------------------------------------- castle
    S("narrator", "Luna searched the whole castle, but Whiskers was nowhere.", "castle",
      "c_narr", [("bell_jingle", 0.3)]),
    A("castle", 0.9, "c_search", [("bell_jingle", 0.1), ("peacock", 0.6)]),
    S("pavao", "Dom Pavão, keeper of the castle. Why so sad, little cat?", "castle", "c_pavao",
      [("fan", 0.05)]),
    S("luna", "I lost my friend. He's orange, and round, and loves sardines.", "castle", "c_lost"),
    S("pavao", "Come! From my wall you can see all of Lisbon.", "castle", "c_look"),
    A("castle", 1.3, "c_view", [("flap", 0.1), ("gull", 0.6)]),
    S("luna", "So many roofs. So many streets. I miss him already.", "castle", "c_miss"),
    A("castle", 0.5, "c_end"),

    # ----------------------------------------------------------------- lost
    S("narrator", "Far away, Whiskers woke up all alone.", "lost", "l_narr",
      [("tram_bell", 0.0)]),
    S("whiskers", "Luna? Luna! Oh no. Where am I?", "lost", "l_where"),
    A("lost", 1.2, "l_wander", [("steps", 0.0), ("gull", 0.4), ("steps", 0.6)]),
    S("whiskers", "Up a hill, down a hill. And every street smells of sardines!",
      "lost", "l_streets"),
    A("lost", 1.4, "l_lift", [("lift_ding", 0.05), ("lift_hum", 0.15)]),
    S("whiskers", "There's the castle! I'm coming, Luna!", "lost", "l_castle",
      [("lift_ding", 0.95)]),
    A("lost", 1.2, "l_dusk", [("steps", 0.0), ("steps", 0.4), ("sniff", 0.75), ("sniff", 0.9)]),

    # --------------------------------------------------------------- alfama
    S("avo", "You must be Whiskers! Tiago told me. Have a sardine, dear.", "alfama",
      "a_avo", [("sizzle", 0.0)]),
    A("alfama", 0.6, "a_plate", [("clink", 0.3)]),
    S("whiskers", "Thank you. But I can't. Sardines don't taste right without Luna.", "alfama", "a_cant"),
    S("avo", "We have a word for that. Saudade. Missing someone you love.", "alfama",
      "a_saudade"),
    S("tiago", "So let's play a fado, loud enough to reach the castle!", "alfama", "a_fado"),
    A("alfama", 1.2, "a_song", [("fado", 0.0)]),
    A("alfama", 1.0, "a_song2", [("bell_jingle", 0.7)]),
    S("pavao", "Avó Lurdes' fado! Follow the music, Luna!", "alfama", "a_follow"),
    A("alfama", 1.0, "a_run", [("bell_jingle", 0.05), ("steps", 0.2), ("bell_jingle", 0.5), ("steps", 0.6)]),
    S("luna", "Whiskers!", "alfama", "a_luna", [("bell_jingle", 0.0)]),
    S("whiskers", "Luna!", "alfama", "a_whis"),
    A("alfama", 1.2, "a_hug", [("purr", 0.1)]),

    # ---------------------------------------------------------------- festa
    S("narrator", "That night, under a thousand lanterns, Lisbon danced.", "festa", "f_narr",
      [("arraial", 0.0)]),
    A("festa", 1.4, "f_dance", [("cheer", 0.6)]),
    S("whiskers", "Now they taste perfect. One for you, and one for me.", "festa", "f_share", [("sizzle", 0.0)]),
    A("festa", 0.7, "f_eat", [("munch", 0.2), ("munch", 0.6)]),
    S("luna", "I had saudade too, Whiskers. All afternoon.", "festa", "f_luna"),
    S("whiskers", "Next time I fall asleep on a tram... please wake me up.", "festa", "f_next"),
    A("festa", 1.3, "f_fire", [("firework", 0.1), ("firework", 0.35), ("cheer", 0.45), ("firework", 0.6),
                               ("firework", 0.8)]),

    # ----------------------------------------------------------------- home
    A("home", 0.7, "h_open", [("scooter", 0.0), ("beep", 0.6)]),
    S("narrator", "Tiago drove them home, with a present from Avó.",
      "home", "h_narr"),
    S("pip", "You're back! Did you bring me a story?", "home", "h_pip"),
    S("whiskers", "A story, and a sardine. And Pip? I missed you.", "home", "h_miss"),
    S("narrator", "Because missing someone means they live in your heart. In Lisbon, they call it saudade.", "home", "h_moral"),
    A("home", 1.5, "h_end", [("guitar_flourish", 0.1), ("purr", 0.4)]),
]
