import random
import logging
from copy import copy, deepcopy

from .world import World, Tile, opposite_direction
from .diary import Diary
from . import tools
from . import event
from . import goals
from . import props

class Worldview(Tile):
    def __init__(self, posx, posy, terrain):
        super().__init__(posx, posy, terrain)
        self.visited = 0

    def locality_copy(self):
        """Copy the worldview and its immediate neighbours."""
        new = copy(self)
        new.north = copy(self.north)
        new.south = copy(self.south)
        new.east = copy(self.east)
        new.west = copy(self.west)
        return new

    def is_most_recent_location(self, person):
        """Test whether this location is the last place the current
        person has visited."""

class Person:
    def __init__(self, world, name, gender, tile=None):
        self.name = name
        self.gender = gender
        self.world = world
        self.tile = tile
        # (Imemdiately) available tools
        self.tools = [tools.Fist(adjectives=['left']),
            tools.Fist(adjectives=['right']),
            tools.Foot(adjectives=['left']),
            tools.Foot(adjectives=['right'])]
        # Other inventory
        self.inventory = []
        # several-move missions to consider
        self.goals = goals.Goals(self)
        
        # log
        self.diary = Diary(self)

        # fixed behaviour attributes
        self.shy = 0.9
        self.explorer = 0.9
        self.escapologist = 0.2

        # knowledge
        self.previous_worldview = None # Tile
        self.worldview = None # Tile
        
        # current status/needs
        self.time = 0
        self.health_delta = 0.03 # how much they heal each day
        self.health = 1.0
        self.thirst = 0
        self.awake = 0
        self.sleeping = False

    @property
    def dead(self):
        return self.health == 0
    
    def __lt__(self, other):
        """Allow sorting of people."""
        return self.name < other.name

    @classmethod
    def from_random(cls, world, namegen):
        return cls(world, *namegen())

    def __str__(self):
        return "%s" % (self.name)

    def __repr__(self):
        return "Person(%r, %r, %r)" % ( 
            self.world, self.name, self.gender)

    def injure(self, amount):
        """Injure this person by a certain amount (amount<=1.0)
        
        amount may be negative to heal"""
        self.health -= amount
        if self.health < 0.0:
            self.health = 0.0
        if self.health > 1.0:
            self.health = 1.0
    
    def log(self, event_cls, *args, **kw):
        """Convenience method for self.diary.log(...)"""
        args = list(args)
        args.append(self.time)
        args.append(self)
        args.append(self.worldview.locality_copy())
        self.diary.log(self.time, event_cls(*args, **kw))

    def tick(self, i):
        # update stats

        self.time = i
        if not self.sleeping:
            self.thirst += 1
        self.awake += 1

        # heal/continue to die
        self.injure(-self.health_delta)
        if self.health_delta < 0.03:
            self.health_delta += 0.05

        # update worldview
        self.observe()
        def increase_last_visited_count(tile):
            tile.visited += 1
        self.worldview.recursive_update(increase_last_visited_count)

        self.log(event.Tick, i)

    def observe(self):
        # update worldview
        if self.worldview is None:
            self.worldview = Worldview(
                self.tile.posx, self.tile.posy, self.tile.terrain)
        self.worldview.people = copy(self.tile.people)
        self.worldview.terrain = copy(self.tile.terrain) # TODO check for copy of props list - if someone picks up something this character shouldn't know
        
    def action(self):
        # Sleep cycle:
        if self.sleeping:
            self.awake -= 2 # 2 to compensate for +=1 in tick()
            # TODO there are probably some things that should also
            #  have a chance of waking the character up.
            # And being fought should always wake them up
            if self.awake < 4 and random.random() < 0.3:
                self.sleeping = False
                self.log(event.Wake)
            else:
                # Player continues to sleep
                return

        self.log(event.Terrain)

        # Analyse character's needs and goals:

        if self.thirst > 6:
            self.log(event.Thirst, self.thirst)
            goto_goal = goals.GoTo(props.Water, self.thirst, person=self)
            drink_goal = goals.Drink(self.thirst + 1, person=self)
            drink_goal.subgoals.append(goto_goal)
            self.goals.add_or_replace(goto_goal)
            self.goals.add_or_replace(drink_goal)

        if len(self.worldview.people) > 1:
            self.log(event.Occupants)
            # run away if shy # TODO or hide
            if random.random() < self.shy:
                self.log(event.Emotion, 'afraid')
                self.log(event.Motivation, 'escape')
                self.goals.add_or_replace(goals.Escape, 5)
                # TODO calc priority better
            else:
                # TODO pick opponent more cannily
                opponent = self.worldview.people.random(self, 1)[0]
                self.goals.add_or_replace(goals.Fight, opponent, 5)
                # TODO calc priority better
        
        if self.awake > 10:
            self.log(event.Emotion, 'sleepy')
            if self.awake > 15:
                self.sleeping = True
                self.log(event.Sleep)
                return
            elif goals.GoTo not in self.goals:
                # TODO implement more specific search in self.goals
                # TODO find somewhere proper to hide to sleep.
                self.goals.add_or_replace(goals.GoTo,
                    props.PlaceToSleep, self.awake)
            else:
                # Chararacter is somewhere suitable to sleep
                self.sleeping = True
                self.log(event.Sleep)

        # Add low-priority rest function if nothing better to do.
        if goals.Rest not in self.goals:
            self.goals.add(goals.Rest, 1)

        # Add low-priority explore function if nothing better to do.
        if goals.Explore not in self.goals:
            self.goals.add(goals.Explore, None, 1)

        # Perform highest priority action that is currently possible:

        logging.debug('choosing highest priority goal from %r', self.goals)
        goal_cache = []
        # Pick highest priority goal:
        while True:
            top_goals = []
            top_goals.append(self.goals[-1])
            for i in range(len(self.goals) - 2, -1, -1):
                if self.goals[i].priority == top_goals[0].priority:
                    top_goals.append(self.goals[i])
                    continue
                break
            logging.debug('Top goals: %r', top_goals)
            if len(top_goals) > 1:
                goal = random.choice(top_goals)
                logging.debug("Randomly selected goal %s", goal)
            else:
                goal = top_goals[0]
                logging.debug("Selected goal: %s", goal)

            # is goal possible right now?
            logging.debug('checking goal possible')
            if goal.possible():
                logging.debug('achieving goal')
                goal.achieve()
                break
            else:
                logging.debug('goal not possible')
                goal_cache.append(goal)
                if goal in self.goals: # possible() may have removed itself
                    self.goals.remove(goal)
                continue
        for goal in goal_cache:
            self.goals.add(goal)

    def _move(self, direction, newtile):
        assert newtile is not None, 'tried to move %s to empty tile' % direction
        self.log(event.Movement, direction)
        self.tile.people.remove(self)
        self.tile = newtile
        self.previous_worldview = self.worldview
        self.worldview = getattr(self.worldview, direction, None)
        if not self.worldview:
            self.observe()
        setattr(self.previous_worldview, direction, self.worldview)
        setattr(self.worldview, opposite_direction(direction),
            self.previous_worldview)
        self.tile.people.add(self)

