# Story script. Items: (speaker, text[, tag]) or ('act', name, weight).
# Acts are silent action moments; their length is stretched so the film is exactly DURATION.

VOICES = {
    'N': ('Daniel', 172),
    'W': ('Eddy (English (US))', 168),
    'L': ('Flo (English (US))', 172),
    'P': ('Junior', 190),
}
NAMES = {'N': '', 'W': 'Whiskers', 'L': 'Luna', 'P': 'Pip'}

SCRIPT = [
    {'id': 'title', 'items': [
        ('act', 'intro', 1.5),
        ('N', "Whiskers and the Moon Fish."),
        ('act', 'hold', 1.5),
    ]},
    {'id': 'morning', 'items': [
        ('N', "In a small blue house at the edge of a quiet town, there lived two cats. "
              "Whiskers, an orange cat who loved naps more than anything in the world. "
              "And Luna, a grey cat who loved adventures even more."),
        ('act', 'sunrise', 2),
        ('L', "Whiskers! Wake up! The sun is already up."),
        ('W', "Five more minutes, Luna. The windowsill is so warm."),
        ('L', "You said that an hour ago. And the hour before that."),
        ('act', 'stretch', 2),
        ('W', "Fine, fine. I'm awake. Is it breakfast time?"),
        ('act', 'bowl', 2),
        ('L', "The bowl is empty. Again."),
        ('W', "Empty? That is a tragedy. That is the worst thing that has ever happened to anyone."),
        ('N', "It was not, in fact, the worst thing that had ever happened to anyone. "
              "But Whiskers was always very dramatic before breakfast."),
    ]},
    {'id': 'legend', 'items': [
        ('L', "Whiskers, have you ever heard of the Moon Fish?"),
        ('W', "The moon... what?"),
        ('L', "The Moon Fish. Old Tom from next door says it lives in the pond past the garden. "
              "On full moon nights, it glows like silver."),
        ('W', "A glowing fish. Is it big?"),
        ('L', "As big as the moon itself, they say."),
        ('act', 'think', 2),
        ('W', "That is a lot of breakfast."),
        ('L', "Tonight is a full moon. We could go and see it."),
        ('W', "Luna, I have only one rule. Never, ever miss a nap. "
              "But for a fish that big, I will make an exception."),
        ('act', 'meow', 1.5),
    ]},
    {'id': 'garden', 'items': [
        ('N', "So, as the afternoon turned golden, the two cats set off through the garden.", 'walk0'),
        ('act', 'walk', 2.5),
        ('W', "Are we there yet?", 'walk1'),
        ('L', "We just left the porch.", 'walk2_line'),
        ('act', 'walk2', 1.5),
        ('W', "Ooh! A butterfly! I must catch it!"),
        ('act', 'chase', 1.5),
        ('L', "Focus, Whiskers. The fish, remember?"),
        ('W', "Right. The fish. The very big fish. I am totally focused."),
        ('act', 'fence', 2.5),
        ('N', "They climbed over the old wooden fence, to where the grass grew tall and wild."),
    ]},
    {'id': 'meadow', 'items': [
        ('P', "Eek! Cats! Please don't eat me!"),
        ('L', "Don't worry, little one. We're not here for you. We're looking for the Moon Fish."),
        ('P', "The Moon Fish? Oh, I know that pond! My name is Pip. I can show you the way."),
        ('W', "You would help us? Even though we are... cats?"),
        ('P', "Everyone deserves a friend. Even cats. Just promise not to chase me."),
        ('W', "I promise. Mostly."),
        ('L', "Whiskers!"),
        ('W', "Completely! I promise completely."),
        ('act', 'walk', 2.5),
        ('N', "And so, a cat, another cat, and one very brave mouse walked on together, as the sun went down.", 'walkn'),
    ]},
    {'id': 'pond', 'items': [
        ('act', 'arrive', 2.5),
        ('P', "Here it is. The pond. Now, we wait for the moon."),
        ('act', 'moonrise', 3.5),
        ('L', "Look! There! In the water!"),
        ('W', "The Moon Fish! It's shining! It's huge! It's mine!"),
        ('act', 'pounce', 1.5),
        ('act', 'splash', 1.5),
        ('N', "Whiskers jumped. And with a great big splash, he landed right in the middle of the pond."),
        ('W', "Blub! It's cold! It's wet! Where did the fish go?"),
    ]},
    {'id': 'realize', 'items': [
        ('P', "Look up, Whiskers."),
        ('act', 'lookup', 2),
        ('L', "Oh, Whiskers. The Moon Fish isn't a fish at all. It's the moon, shining in the water."),
        ('W', "So I jumped into a pond... to catch the sky?"),
        ('P', "That's the bravest silly thing I have ever seen."),
        ('act', 'laugh', 2.5),
        ('N', "For a moment, nobody said a thing. Then all three of them started laughing, "
              "so hard that even the frogs joined in."),
        ('W', "Well. No breakfast. But I did get a bath. And a new friend."),
    ]},
    {'id': 'home', 'items': [
        ('N', "That night, the three friends walked home under the big silver moon."),
        ('act', 'walkhome', 2),
        ('N', "Whiskers curled up on the warm windowsill, with Luna beside him, "
              "and Pip snuggled up between their paws."),
        ('L', "Goodnight, Whiskers. Goodnight, Pip."),
        ('P', "Goodnight, Moon Fish."),
        ('W', "Five more minutes... then breakfast."),
        ('act', 'quiet', 1.5),
        ('N', "Because sometimes, the best thing you find on an adventure isn't what you were looking for. "
              "It's who you find along the way."),
        ('act', 'end', 3),
    ]},
]
