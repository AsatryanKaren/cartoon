"""Film: "Whiskers and the Swan Castle" -- Whiskers and Luna go to Munich and Neuschwanstein.

One rainy autumn afternoon Pip finds an old storybook in the attic trunk: "The
Swan Castle", stamped "Library of Neuschwanstein Castle -- please return by
1886". It is 140 years overdue, and its last page is missing. Luna wants to
take it home; Whiskers only agrees when Pip mentions pretzels and apple
strudel. They travel the cats' favourite way -- in a box: Pip posts them,
book and all, and the little yellow post van drives them through the night to
Munich. At Marienplatz the Glockenspiel dances, and Whiskers' giant pretzel
rolls away across the square into Resi, a red squirrel in a Bavarian hat, who
takes them on Hansl the horse's hay wagon to a village of painted houses (an
apple strudel and a mountain of cream: a cream beard, "Bavarian fashion -- on
purpose"). Whiskers insists on carrying the book through the dark forest. On
the Marienbruecke, showing off as "Sir Whiskers the Swan Knight", he drops it
into the gorge. "On purpose", he says -- then, for once, tells the truth: it was
his fault. He climbs down beside the waterfall and brings it back, soaked. At
the castle Ludwig, the old swan who keeps the library, is overjoyed; Whiskers
owns up again, and Ludwig calls him a true knight. The last page was never
written -- so the cats write the ending together, on a balcony above the moonlit
swan lake. Ludwig posts them home "Return to Sender", and on the windowsill
Whiskers reads Pip the new last page. Moral: anyone can make a mistake; the
brave ones say "that was me".
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.munich import sounds

TITLE = "Whiskers and the Swan Castle"
PLACE = "Munich"            # folder in the catcute library
SCENES = ["title", "attic", "post", "square", "village", "forest", "bridge", "castle", "lake", "home"]

CAST = {
    **CAST,
    # Resi: a quick, cheerful red squirrel in a little green Bavarian hat with a feather
    "resi": Voice("af_jessica", 1.05, 2, ["Samantha"], 188, "en-us+f4", 72, 172),
    # Ludwig: a grand old white swan with a tiny crown and spectacles, keeper of the castle library
    "ludwig": Voice("bm_fable", 0.9, -2, ["Daniel"], 160, "en-gb+m1", 32, 145),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "resi": (255, 196, 140),
    "ludwig": (205, 235, 255),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    # storybook: soft music-box over warm chords
    "m_title":  dict(bpm=70, prog=[(62, MAJ), (67, MAJ), (59, MIN), (57, MAJ)], drums=False, mel=0.55, oct=81, vol=0.75),
    "m_rain":   dict(bpm=84, prog=[(60, MAJ), (57, MIN), (65, MAJ), (67, MAJ)], drums=False, mel=0.45, oct=79, vol=0.65),
    "m_book":   dict(bpm=72, prog=[(62, MAJ), (59, MIN), (55, MAJ), (57, MAJ)], drums=False, mel=0.5, oct=81, vol=0.7),
    "m_post":   dict(bpm=110, prog=[(65, MAJ), (60, MAJ), (65, MAJ), (70, MAJ)], drums=True, mel=0.6, oct=77, vol=0.75),
    "m_night":  dict(bpm=66, prog=[(57, MIN), (65, MAJ), (60, MAJ), (64, MAJ)], drums=False, mel=0.3, oct=76, vol=0.6),
    # oompah: brass-band bounce, tonic/dominant
    "m_oompah": dict(bpm=126, prog=[(58, MAJ), (65, MAJ), (65, MAJ), (58, MAJ)], drums=True, mel=0.75, oct=74, vol=0.85),
    "m_chase":  dict(bpm=144, prog=[(60, MAJ), (67, MAJ), (65, MAJ), (67, MAJ)], drums=True, mel=0.8, oct=76, vol=0.82),
    # Laendler: a swaying country tune for the hay wagon and the painted village
    "m_wagon":  dict(bpm=104, prog=[(67, MAJ), (62, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.65, oct=79, vol=0.78),
    "m_strudel": dict(bpm=132, prog=[(65, MAJ), (70, MAJ), (72, MAJ), (65, MAJ)], drums=True, mel=0.8, oct=77, vol=0.82),
    "m_forest": dict(bpm=76, prog=[(62, MIN), (58, MAJ), (60, MAJ), (57, MIN)], drums=False, mel=0.35, oct=74, vol=0.62),
    "m_wonder": dict(bpm=68, prog=[(62, MAJ), (67, MAJ), (71, MIN), (69, MAJ)], drums=False, mel=0.45, oct=81, vol=0.78),
    "m_oops":   dict(bpm=60, prog=[(57, MIN), (53, MAJ), (55, MAJ), (52, MIN)], drums=False, mel=0.2, oct=72, vol=0.55),
    "m_brave":  dict(bpm=92, prog=[(62, MIN), (58, MAJ), (60, MAJ), (62, MAJ)], drums=True, mel=0.5, oct=74, vol=0.75),
    "m_castle": dict(bpm=66, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.45, oct=77, vol=0.72),
    "m_swans":  dict(bpm=62, prog=[(62, MAJ), (59, MIN), (67, MAJ), (69, MAJ)], drums=False, mel=0.4, oct=81, vol=0.72),
    "m_home":   dict(bpm=64, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "m_title", "attic": "m_rain", "post": "m_post", "square": "m_oompah", "village": "m_wagon",
         "forest": "m_forest", "bridge": "m_wonder", "castle": "m_castle", "lake": "m_swans", "home": "m_home"}
MUSIC_CUES = [("a_book", 0.0, "m_book"), ("a_pretzel", 0.0, "m_rain"),
              ("p_road", 0.0, "m_night"), ("p_dawn", 0.3, "m_post"),
              ("s_roll", 0.0, "m_chase"), ("s_resi", 0.0, "m_oompah"),
              ("v_eat", 0.0, "m_strudel"), ("v_go", 0.0, "m_wagon"),
              ("b_show", 0.0, "m_wagon"), ("b_drop", 0.2, "m_oops"), ("b_climb", 0.0, "m_brave"),
              ("b_safe", 0.0, "m_wonder")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.4, "t_open", [("chime", 0.05)]),
    S("narrator", "Whiskers and the Swan Castle.", "title", "t_name"),
    A("title", 1.2, "t_hold", [("honk", 0.4)]),

    # ---------------------------------------------------------------- attic
    A("attic", 0.9, "a_open", [("rain", 0.0)]),
    S("narrator", "One rainy autumn afternoon, Pip found a treasure in the attic.",
      "attic", "a_narr", [("rain", 0.3)]),
    A("attic", 0.8, "a_pip", [("thud", 0.85)]),
    S("pip", "Look! An old storybook!", "attic", "a_found"),
    S("luna", "The Swan Castle. It looks like a castle from a dream!", "attic", "a_book",
      [("chime", 0.05)]),
    S("luna", "Look at the stamp. Neuschwanstein Castle Library. Please return by eighteen eighty-six!",
      "attic", "a_stamp"),
    S("whiskers", "That's not late. That's ancient.", "attic", "a_ancient"),
    S("luna", "And the last page is torn out! Nobody knows how it ends.", "attic", "a_page"),
    S("luna", "A borrowed book should go home. Let's take it back.", "attic", "a_back"),
    S("whiskers", "To the mountains? No, thank you.", "attic", "a_no"),
    S("pip", "Bavaria. Land of giant pretzels and apple strudel.", "attic", "a_pretzel"),
    A("attic", 0.6, "a_ears"),
    S("whiskers", "I'll get the box.", "attic", "a_box", [("meow", 0.9)]),
    A("attic", 0.6, "a_end"),

    # ----------------------------------------------------------------- post
    S("narrator", "So Pip packed the book, and the two cats with it.", "post", "p_narr", [("tape", 0.5)]),
    S("whiskers", "A box and a long ride. Best trip ever.", "post", "p_best"),
    A("post", 0.9, "p_stamp", [("stamp", 0.55)]),
    S("pip", "Oops. That stamp was for the box.", "post", "p_oops"),
    A("post", 1.2, "p_van", [("posthorn", 0.1), ("engine", 0.45)]),
    A("post", 1.4, "p_road", [("engine", 0.0), ("engine", 0.5)]),
    S("narrator", "All night, the yellow post van drove south, to Munich.", "post", "p_south"),
    A("post", 1.4, "p_dawn", [("engine", 0.0), ("posthorn", 0.75)]),

    # --------------------------------------------------------------- square
    A("square", 1.0, "s_open", [("thud", 0.15), ("glock", 0.3)]),
    S("luna", "Munich! Look, the little figures on the tower are dancing!", "square", "s_look",
      [("glock", 0.2)]),
    S("whiskers", "Never mind dancing. I smell pretzels!", "square", "s_smell"),
    A("square", 1.0, "s_grab", [("tuba", 0.1)]),
    A("square", 1.6, "s_roll", [("roll", 0.0), ("roll", 0.45), ("thud", 0.95)]),
    S("resi", "Servus! Is this runaway pretzel yours?", "square", "s_resi", [("chitter", 0.0)]),
    S("whiskers", "I let it roll on purpose. Pretzels need exercise.", "square", "s_purpose"),
    S("resi", "I'm Resi! Where are you going with that big book?", "square", "s_where"),
    S("luna", "To the Swan Castle, to give it back!", "square", "s_castle"),
    S("resi", "That's my forest! Hop on Hansl's hay wagon!", "square", "s_hop",
      [("neigh", 0.8)]),
    A("square", 0.9, "s_end", [("clop", 0.2)]),

    # -------------------------------------------------------------- village
    A("village", 1.2, "v_ride", [("clop", 0.0), ("clop", 0.5)]),
    S("narrator", "Hansl the horse pulled them to a village of painted houses.",
      "village", "v_narr", [("clop", 0.4)]),
    S("resi", "Nobody passes our village without trying the apple strudel!", "village", "v_strudel"),
    A("village", 2.0, "v_eat", [("squirt", 0.45), ("squirt", 0.6), ("gulp", 0.85)]),
    S("whiskers", "A cream beard. On purpose. It's Bavarian fashion.", "village", "v_beard"),
    S("luna", "Careful with the book!", "village", "v_careful"),
    S("whiskers", "Relax. I'll carry it. I'm very responsible.", "village", "v_carry"),
    A("village", 0.9, "v_go", [("neigh", 0.1), ("clop", 0.5)]),

    # --------------------------------------------------------------- forest
    A("forest", 1.0, "f_in", [("owl", 0.3)]),
    S("narrator", "Beyond the village lay the deep, dark Bavarian forest.", "forest", "f_narr"),
    A("forest", 0.9, "f_eyes", [("twig", 0.4)]),
    S("whiskers", "Resi? Why do the trees have eyes?", "forest", "f_why"),
    S("resi", "Those are only deer, silly. Say hello!", "forest", "f_deer"),
    A("forest", 1.2, "f_bow", [("chitter", 0.6)]),
    A("forest", 0.7, "f_end"),

    # --------------------------------------------------------------- bridge
    A("bridge", 1.2, "b_view", [("falls", 0.0)]),
    S("luna", "The Swan Castle! Even more beautiful than in the book!", "bridge", "b_wow"),
    S("whiskers", "Behold! Sir Whiskers, the Swan Knight!", "bridge", "b_show"),
    A("bridge", 1.4, "b_drop", [("whoosh", 0.25), ("falls", 0.4)]),
    S("whiskers", "I dropped it on purpose. To see if books can fly.", "bridge", "b_fly"),
    S("luna", "Whiskers. That book waited a hundred and forty years to go home.", "bridge", "b_waited"),
    A("bridge", 0.9, "b_quiet", [("falls", 0.0)]),
    S("whiskers", "No. It wasn't on purpose. I was showing off. It was my fault.", "bridge", "b_fault"),
    S("whiskers", "So I'll get it back.", "bridge", "b_back"),
    A("bridge", 2.4, "b_climb", [("falls", 0.0), ("pebble", 0.2), ("pebble", 0.45), ("splash", 0.62),
                                  ("pebble", 0.8)]),
    S("resi", "Pull, everybody!", "bridge", "b_pull"),
    A("bridge", 1.0, "b_up", [("pop", 0.6)]),
    S("luna", "You did it! It's soggy, but safe!", "bridge", "b_safe", [("jingle", 0.1)]),
    A("bridge", 0.6, "b_end"),

    # --------------------------------------------------------------- castle
    A("castle", 1.0, "c_door", [("knock", 0.2), ("knock", 0.45), ("creak", 0.75)]),
    S("ludwig", "Good evening. I am Ludwig, keeper of the castle library.", "castle", "c_ludwig"),
    S("luna", "We came to return a book. It's a tiny bit late.", "castle", "c_late"),
    S("ludwig", "The Swan Castle! Welcome home, old friend!", "castle", "c_home",
      [("honk", 0.9)]),
    S("whiskers", "It's wet because I dropped it. My fault. I'm sorry.", "castle", "c_sorry"),
    A("castle", 0.7, "c_pause"),
    S("ludwig", "Telling the truth when it's hard? That is what a true knight does.",
      "castle", "c_knight"),
    S("luna", "But how does the story end?", "castle", "c_end"),
    S("ludwig", "It was never written. Perhaps you should write it.", "castle", "c_write",
      [("sparkle", 0.6)]),
    A("castle", 1.0, "c_quill", [("sparkle", 0.2)]),

    # ----------------------------------------------------------------- lake
    A("lake", 1.6, "l_open", [("honk", 0.3)]),
    S("whiskers", "And they all ate apple strudel, happily ever after.", "lake", "l_strudel"),
    S("luna", "And the cat told the truth. That was the bravest thing of all.", "lake", "l_truth"),
    A("lake", 1.6, "l_hold", [("purr", 0.2), ("honk", 0.7)]),
    S("ludwig", "A perfect ending. Now, home you go. Return to sender!", "lake", "l_send",
      [("stamp", 0.95)]),
    A("lake", 0.8, "l_end"),

    # ----------------------------------------------------------------- home
    A("home", 1.0, "h_open", [("posthorn", 0.1), ("thud", 0.7)]),
    S("pip", "You're back! How does the story end?", "home", "h_pip", [("tape", 0.6)]),
    S("whiskers", "We wrote it ourselves, Pip. Listen.", "home", "h_read"),
    S("whiskers", "And the cat said, it was my fault. And everybody still loved him.", "home", "h_page"),
    A("home", 1.0, "h_hug", [("purr", 0.2)]),
    S("narrator", "Because anyone can make a mistake. The truly brave say: that was me.",
      "home", "h_moral"),
    A("home", 2.6, "h_end"),
]
