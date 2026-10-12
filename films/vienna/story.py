"""Film: "Whiskers and the Two Left Paws" -- Whiskers and Luna go to Vienna.

Whiskers' breakfast fish comes wrapped in a newspaper from Vienna: a Grand
Waltz Contest at Schonbrunn Palace, tomorrow night! Whiskers, who has "two
left paws", wants nothing to do with dancing -- until Luna reads out the first
prize, the biggest Sachertorte in Vienna. A real Viennese orchestra is loading
its tour bus across the street, so the cats hide in a double bass case and
ride to Vienna on the roof rack (Whiskers sleeps on the velvet). At St.
Stephen's Cathedral they meet Ferdinand, an old white Lipizzaner who pulls a
Fiaker carriage and once danced at the famous Riding School; he drives them
round the Ring past the Opera. At Cafe Mitzi Whiskers eats the cake cabinet
and ends up under a mountain of whipped cream ("a cream hat -- on purpose").
Ferdinand's waltz lesson under the Prater's giant Ferris wheel is a disaster;
up in the wheel at sunset Whiskers admits he is scared everyone will laugh,
but he will dance anyway, for Luna. A shortcut through Schonbrunn's maze gets
them lost -- Whiskers' nose for chocolate gets them out. At the ball he trips
and the whole room laughs... Luna: forget the counting, just listen to the
music and hold my paw. Their wobbly, twirly, joyful waltz makes the whole
ballroom dance along; the Countess gives them the cake -- and Whiskers only
wants to dance once more. Home on the windowsill, he teaches Pip to waltz.
Moral: you don't need perfect steps to dance -- just the music, a friend and
a happy heart.
"""
from common import *  # noqa: F401,F403
from common import CAST, SUBTITLE_COLORS, Voice, Say, Act

from films.vienna import sounds

TITLE = "Whiskers and the Two Left Paws"
PLACE = "Vienna"            # folder in the catcute library
SCENES = ["title", "sill", "bus", "city", "cafe", "prater", "palace", "ball", "home"]

CAST = {
    **CAST,
    # Ferdinand: an old white Lipizzaner horse who pulls a Fiaker carriage; a gentle, proud old dancer
    "ferdinand": Voice("am_adam", 0.92, -2, ["Ralph"], 156, "en-us+m1", 28, 145),
    # Mitzi: the jolly calico cat who runs Cafe Mitzi
    "mitzi": Voice("af_sarah", 1.02, 0, ["Samantha"], 180, "en-us+f2", 56, 165),
    # the Countess: an elegant white cat with a tiara, hostess of the Grand Waltz
    "countess": Voice("bf_emma", 0.95, 1, ["Kate"], 170, "en-gb+f2", 60, 155),
}
SUBTITLE_COLORS = {
    **SUBTITLE_COLORS,
    "ferdinand": (215, 235, 255),
    "mitzi": (255, 225, 140),
    "countess": (240, 200, 255),
}

MAJ, MIN = (0, 4, 7), (0, 3, 7)
MOODS = {
    "v_title":  dict(bpm=72, prog=[(62, MAJ), (57, MAJ), (59, MIN), (55, MAJ)], drums=False, mel=0.45, oct=74, vol=0.7),
    "v_morning": dict(bpm=104, prog=[(65, MAJ), (62, MIN), (58, MAJ), (60, MAJ)], drums=True, mel=0.6, oct=77, vol=0.78),
    "v_sneak":  dict(bpm=128, prog=[(62, MIN), (60, MAJ), (58, MAJ), (57, MAJ)], drums=True, mel=0.7, oct=74, vol=0.8),
    "v_road":   dict(bpm=96, prog=[(67, MAJ), (62, MAJ), (64, MIN), (60, MAJ)], drums=True, mel=0.6, oct=79, vol=0.78),
    "v_city":   dict(bpm=110, prog=[(62, MAJ), (67, MAJ), (69, MAJ), (62, MAJ)], drums=True, mel=0.7, oct=74, vol=0.8),
    "v_cafe":   dict(bpm=92, prog=[(65, MAJ), (70, MAJ), (60, MAJ), (65, MAJ)], drums=False, mel=0.65, oct=77, vol=0.75),
    "v_cream":  dict(bpm=136, prog=[(60, MAJ), (65, MAJ), (67, MAJ), (60, MAJ)], drums=True, mel=0.8, oct=76, vol=0.8),
    "v_lesson": dict(bpm=120, prog=[(60, MAJ), (67, MAJ), (65, MAJ), (60, MAJ)], drums=False, mel=0.6, oct=72, vol=0.7),
    "v_sad":    dict(bpm=60, prog=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ)], drums=False, mel=0.25, oct=74, vol=0.6),
    "v_brave":  dict(bpm=66, prog=[(60, MAJ), (57, MIN), (53, MAJ), (55, MAJ)], drums=False, mel=0.35, oct=76, vol=0.68),
    "v_dusk":   dict(bpm=84, prog=[(65, MAJ), (60, MAJ), (62, MIN), (58, MAJ)], drums=False, mel=0.5, oct=77, vol=0.72),
    "v_maze":   dict(bpm=140, prog=[(57, MIN), (56, MAJ), (57, MIN), (52, MAJ)], drums=True, mel=0.8, oct=72, vol=0.78),
    "v_ball":   dict(bpm=76, prog=[(62, MAJ), (67, MAJ), (57, MAJ), (62, MAJ)], drums=False, mel=0.4, oct=79, vol=0.7),
    "v_hush":   dict(bpm=56, prog=[(57, MIN), (53, MAJ), (55, MAJ), (57, MIN)], drums=False, mel=0.15, oct=74, vol=0.5),
    "v_quiet":  dict(bpm=60, prog=[(62, MAJ), (57, MAJ), (59, MIN), (55, MAJ)], drums=False, mel=0.0, oct=74, vol=0.12),
    "v_home":   dict(bpm=66, prog=[(65, MAJ), (57, MIN), (58, MAJ), (60, MAJ)], drums=False, mel=0.4, oct=77, vol=0.7),
}
MUSIC = {"title": "v_quiet", "sill": "v_morning", "bus": "v_road", "city": "v_city", "cafe": "v_cafe",
         "prater": "v_lesson", "palace": "v_dusk", "ball": "v_ball", "home": "v_home"}
MUSIC_CUES = [("t_hold", 0.6, "v_title"), ("s_sneak", 0.0, "v_sneak"), ("s_drive", 0.3, "v_morning"),
              ("f_eat", 0.0, "v_cream"), ("f_bye", 0.0, "v_cafe"),
              ("p_demo", 0.0, "v_quiet"), ("p_whoops", 0.0, "v_lesson"), ("p_laugh", 0.0, "v_sad"),
              ("p_brave", 0.0, "v_brave"),
              ("pa_short", 0.0, "v_maze"), ("pa_out", 0.6, "v_ball"),
              ("ba_dance1", 0.0, "v_quiet"), ("ba_oh", 0.0, "v_hush"), ("ba_again", 0.0, "v_quiet"),
              ("ba_bravo", 0.0, "v_ball"), ("ba_end", 0.0, "v_quiet"),
              ("h_dance", 0.0, "v_quiet"), ("h_moral", 0.0, "v_home")]

EXTRA_SFX = sounds.EXTRA_SFX

S = Say
A = Act

SCRIPT = [
    # ---------------------------------------------------------------- title
    A("title", 1.3, "t_open", [("waltz_short", 0.0)]),
    S("narrator", "Whiskers and the Two Left Paws.", "title", "t_name"),
    A("title", 0.9, "t_hold", [("chime", 0.1)]),

    # ----------------------------------------------------------------- sill
    A("sill", 0.7, "s_open", [("crinkle", 0.5)]),
    S("narrator", "One morning, Whiskers' fish came wrapped in a newspaper from Vienna.", "sill", "s_narr",
      [("crinkle", 0.6)]),
    S("luna", "Whiskers, look! A Grand Waltz Contest, tomorrow night, at the palace in Vienna!", "sill", "s_look"),
    S("whiskers", "Dancing? No, thank you. I have two left paws.", "sill", "s_nope"),
    S("luna", "First prize is the biggest chocolate cake in Vienna. A Sachertorte!", "sill", "s_prize"),
    A("sill", 0.5, "s_think"),
    S("whiskers", "Luna. I have always wanted to dance.", "sill", "s_dance"),
    A("sill", 0.9, "s_twirl", [("whoosh", 0.1), ("thump", 0.6)]),
    S("pip", "Look! That bus is going to Vienna!", "sill", "s_bus", [("engine", 0.0)]),
    S("narrator", "It belonged to a real Viennese orchestra, on its way home.", "sill", "s_narr2",
      [("bass", 0.5)]),
    A("sill", 1.3, "s_sneak", [("whoosh", 0.05), ("thump", 0.35), ("whoosh", 0.45), ("thump", 0.7),
                               ("bass", 0.72)]),
    S("pip", "Bring me back a crumb of that cake!", "sill", "s_pip"),
    A("sill", 1.0, "s_drive", [("engine", 0.0), ("honk", 0.15)]),

    # ------------------------------------------------------------------ bus
    S("narrator", "So the cats rode all the way to Vienna, inside a double bass case.", "bus", "b_narr",
      [("engine", 0.0)]),
    A("bus", 1.6, "b_ride", [("engine", 0.0), ("bass", 0.3), ("engine", 0.5), ("bass", 0.75)]),
    S("whiskers", "Soft velvet, gentle humming... the best bed in the world.", "bus", "b_bed", [("purr", 0.2)]),
    S("luna", "Wake up, Whiskers! The river Danube! And there's Vienna!", "bus", "b_look"),
    A("bus", 1.3, "b_arrive", [("engine", 0.0), ("brakes", 0.85)]),

    # ----------------------------------------------------------------- city
    S("narrator", "Vienna! A city of palaces, music, and very fine cake.", "city", "c_narr",
      [("bells", 0.0)]),
    A("city", 1.0, "c_tumble", [("thump", 0.15), ("thump", 0.3), ("clop", 0.5), ("neigh", 0.85)]),
    S("ferdinand", "Good morning, little travellers! Ferdinand, at your service.", "city", "c_ferd"),
    S("luna", "Ferdinand, we've come for the Grand Waltz Contest!", "city", "c_luna"),
    S("ferdinand", "At Schönbrunn Palace, tonight! Hop in, I'll show you my city.", "city", "c_hop"),
    A("city", 1.8, "c_ride", [("clop", 0.0), ("clop", 0.25), ("clop", 0.5), ("clop", 0.75)]),
    S("ferdinand", "That's the Opera. And when I was young, I danced at the famous Riding School!", "city",
      "c_opera", [("clop", 0.3)]),
    S("whiskers", "A dancing horse? Then you can teach me! But first... I smell cake.", "city", "c_smell",
      [("sniff", 0.75)]),

    # ----------------------------------------------------------------- cafe
    S("narrator", "Vienna is famous for its coffee houses, and their cakes.", "cafe", "f_narr",
      [("clink", 0.3), ("piano", 0.0)]),
    S("mitzi", "Welcome to Café Mitzi! Sachertorte? Apple strudel? Whipped cream?", "cafe", "f_mitzi"),
    S("whiskers", "Yes. Yes. And yes, please!", "cafe", "f_yes"),
    A("cafe", 1.5, "f_eat", [("munch", 0.1), ("clink", 0.3), ("munch", 0.45), ("clink", 0.65), ("munch", 0.8)]),
    S("luna", "Whiskers, slow down! We have to practise dancing!", "cafe", "f_slow"),
    A("cafe", 1.0, "f_cream", [("squirt", 0.1), ("squirt", 0.35), ("splat", 0.6)]),
    S("whiskers", "I did that on purpose. It's a, um... cream hat.", "cafe", "f_purpose"),
    S("mitzi", "Ha! You'll need it. Good luck tonight, my darlings!", "cafe", "f_bye", [("bell", 0.6)]),
    A("cafe", 0.5, "f_end"),

    # --------------------------------------------------------------- prater
    S("narrator", "In the Prater park, under the giant Ferris wheel, Ferdinand gave a dancing lesson.",
      "prater", "p_narr"),
    S("ferdinand", "The waltz is easy. One, two, three. One, two, three.", "prater", "p_123"),
    A("prater", 1.5, "p_demo", [("waltz_lesson", 0.0), ("clop", 0.2), ("clop", 0.45), ("clop", 0.7)]),
    S("whiskers", "One, two... ouch! Three... whoops!", "prater", "p_whoops", [("thump", 0.4)]),
    A("prater", 1.2, "p_trip", [("yowl", 0.05), ("boing", 0.3), ("boing", 0.5), ("splash", 0.75)]),
    S("whiskers", "It's no good, Luna. At the ball, everyone will laugh at me.", "prater", "p_laugh"),
    A("prater", 1.4, "p_ride", [("creak", 0.1), ("creak", 0.6)]),
    S("luna", "We don't have to go, Whiskers. I don't want you to be sad.", "prater", "p_sad"),
    S("whiskers", "No. You dreamed of this. I'll dance, even if everybody laughs.", "prater", "p_brave"),
    A("prater", 1.1, "p_sunset", [("purr", 0.2)]),

    # --------------------------------------------------------------- palace
    S("narrator", "That evening, Schönbrunn Palace glowed like a golden cake.", "palace", "pa_narr",
      [("clop", 0.1), ("clop", 0.6)]),
    A("palace", 0.8, "pa_arrive", [("clop", 0.0), ("clop", 0.4), ("neigh", 0.8)]),
    S("whiskers", "A shortcut through the garden! Follow me!", "palace", "pa_short"),
    A("palace", 1.5, "pa_maze", [("whoosh", 0.1), ("boing", 0.35), ("whoosh", 0.55), ("boing", 0.8)]),
    S("luna", "Whiskers, we're lost! The contest is starting!", "palace", "pa_lost"),
    S("whiskers", "Wait... I smell chocolate. This way!", "palace", "pa_sniff", [("sniff", 0.2)]),
    A("palace", 0.9, "pa_out", [("whoosh", 0.2), ("chime", 0.7)]),

    # ----------------------------------------------------------------- ball
    S("narrator", "The ballroom sparkled with a hundred candles.", "ball", "ba_narr", [("chime", 0.1)]),
    S("countess", "Welcome, dancers, to the Grand Waltz! Maestro, if you please!", "ball", "ba_count"),
    A("ball", 2.0, "ba_dance1", [("waltz_fail", 0.0), ("thump", 0.72), ("scrape", 0.76), ("crash", 0.86)]),
    A("ball", 0.6, "ba_trip", [("laugh", 0.0)]),
    S("whiskers", "Oh no. They're all laughing at me.", "ball", "ba_oh"),
    S("luna", "Forget the counting, Whiskers. Just listen to the music, and hold my paw.", "ball", "ba_paw"),
    S("countess", "Maestro! Once more, from the beginning!", "ball", "ba_again"),
    A("ball", 2.6, "ba_dance2", [("waltz_big", 0.0)]),
    S("countess", "Bravo! That was the happiest waltz this palace has ever seen!", "ball", "ba_bravo",
      [("cheer", 0.0)]),
    S("countess", "And the prize goes to... Whiskers and Luna!", "ball", "ba_prize", [("cheer", 0.85)]),
    A("ball", 0.8, "ba_cake", [("chime", 0.2)]),
    S("whiskers", "Cake? Later. Can we dance one more time?", "ball", "ba_more"),
    A("ball", 1.3, "ba_end", [("waltz_short", 0.0)]),

    # ----------------------------------------------------------------- home
    A("home", 0.7, "h_open", [("engine", 0.0)]),
    S("narrator", "The orchestra bus brought them home, with a very big box of cake.", "home", "h_narr"),
    S("pip", "Whiskers! Can you really dance now?", "home", "h_pip"),
    S("whiskers", "Two left paws, Pip. But a happy heart. Come on, I'll show you.", "home", "h_show"),
    A("home", 1.7, "h_dance", [("musicbox", 0.0)]),
    S("narrator", "Because you don't need perfect steps to dance. You only need the music, a friend, and a "
      "happy heart.", "home", "h_moral"),
    A("home", 2.0, "h_end", [("purr", 0.3)]),
]
