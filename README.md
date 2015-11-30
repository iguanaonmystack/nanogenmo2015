# There is an Orange Here

## Or: The Reasonably Hungry Procedurally Generated Games.

This is my first attempt at NaNoGenMo, an idea by [@tinysubversions](https://twitter.com/tinysubversions/status/396305662000775168). There are many more details at [their github](https://github.com/dariusk/NaNoGenMo-2015) but the basic idea is to write a program that generates a 50,000 word novel.

My attempt is inspired primarily by:

 * Most obviously, *the Hunger Games* and *Battle Royale*, as the premise of the generated novel is a bunch of people fighting to the death in the open; and
 * *Idlewild* by Nick Sagan, which is written in the style of multiple diary entries by the main characters.

To generate a novel, which can take between 10 seconds and several minutes depending on how the random numbers work out, install Python 3.x and run the following command:

    $ pip3 install Pillow  # to enable character icon generation.
    $ python3 -u novel.py -x 6 -y 6 -p 6 > output/novel.md

The -x, -y, and -p parameters define the size of the world and number of players. Add "-r [num]" to set the random seed to (supposedly) generate the same novel again, though for some non-obvious reason that doesn't always happen.

My code is licensed under the MIT licence; see [LICENSE](LICENSE) for details.

## Example output

An example generated novel is [here](output/novel.md).

## How it works

The novel works procedurally using a random number generator that can be seeded from a command line option.

 1. Generate the world/arena. This consists of a grid of tiles, each of whom are aware of their neighbours in a giant linked list. Each tile is populated:
 
    - Tiles are assigned as Forested areas, lakes, and meadows at random.
    - Each tile's terrain is assigned some random adjectives to make them
      more distinct. These are used for descriptions.
    - Each tile is also assigned some props at random, which are mostly
      used for descriptions but some have special meanings, for instance
      the characters require water to sate their thirst, and a tree or bush
      to sleep in. There were also going to be tools and weapons lying around
      to be claimed by players, but I didn't get around to implementing that.

 1. Generate the characters/players.

    - Characters are given a name assigned at random from a list of England
      and Wales baby names.
    - They are placed on the middle tile of the world.
    - They are assigned various personality traits, for example bravery, as
      well as keeping track of their current needs, for example sleep.
    - They are assigned a diary each, which tracks their events.

 1. The game then starts and progresses in a loop:

    - Each player has a pre-move stage, where they get hungrier, heal their
      wounds, or continue to lose health. They also observe the world at this
      point (assuming they haven't died!)
    - After all players' pre-move stage, each player has their main action.
      This involves assessing the character's vital stats and surroundings,
      and generating a list of goals, which persist until completed. A goal
      might be something like Fight, Escape, or Find Water.
    - The top priority goal is then acted on, if it can be, and if achieved,
      removed from the person's goal list.
    - Dead players are reaped each loop.

 1. Some actions involve two players getting into a fight. This creates
    a fight simulator where each player takes turn in attacking the other.
    Each player has a collection of weapons they can use, though I only
    had time to implement fists and feet. The plan was to have players find
    weapons around the landscape that they could arm themselves with.

 1. Players still alive, who are currently resting (and so logically able
      to write a diary), have their diary entry generated.

    - While the events that happened to the players are logged in the diary,
      the actual text isn't generated and written out until this stage.
      This allows for some flexibility in becoming too repetitive, and has
      the potential for each character's diary to have a different writing
      style (though I ran out of time to implement this, save for a custom
      salutation at the start of the entry).
    
    - Each player gets an icon to help differentiate them in the user's mind.
      Other options might be to have a different font face. Ideally the
      different writing styles planned would have done the heavy lifting here.

 1. When everyone but one person is dead, the game ends.

## Thoughts

 * This was harder than I expected! While the most algorithmy thing in the code is Dijkstra's algorithm for pathfinding, I needed to write an awful lot of boilerplate code before I could even get any non-debugging output generated. World generation probably took most of the time - it was necessary not only for players to exist in, but also to provide cues for descriptions.
 
 * Getting natural-sounding generated language is a tricky problem. I didn't have time to play around with some of the ideas I had, like defining a formal grammar that the application then fits the right nouns, verbs, etc into.

 * I either have less spare time than I thought, or I'm not as fast a programmer as I'd like to be. I've always been aware that my brain slows down as the evening progresses, and with a full time programming job I'm often coded out by the end of the working day! However, I set myself a target of at least one meaningful (if small) git commit per day, and managed to achieve that. The final output is (kinda) readable.

 * I definitely enjoy coding for leisure, especially when it's on problems that interest me or are generally interesting. I have no love for boilerplate code and I found myself wishing that Python had an idiom for object member initialisation like this:

        def __init__(self, a, b, c, d=1):
            self.a = a
            self.b = b
            self.c = c
            self.d = d


 * My first big project with Python 3.x turned out okay, even if I ended up wanting to use a Python 2-only library that didn't go through 2to3 very well.

 * I definitely recommend NaNoGenMo to anybody who wants to try it. Some of the [other entries](https://github.com/dariusk/NaNoGenMo-2015/issues) I've seen are really inspired, especially the ones that, unlike me, knew what the limitations of generated prose are! I might try something simpler next year :)

 * The title of this project, "There is an Orange Here," was taken from a line in one of the randomly generated novels. The orange prop is an in-joke. Please don't touch the orange. No good will come of it.

 * If anybody wants to hack on my code, please feel free to fork!

