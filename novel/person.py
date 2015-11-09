import random
from copy import copy, deepcopy

from world import World, Tile, opposite_direction
from diary import Diary
from fight import Fight
import tools
import event

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
        
        # log
        self.diary = Diary()

        # fixed behaviour attributes
        self.shy = 0.5
        self.explorer = 0.9

        # knowledge
        self.previous_worldview = None # Tile
        self.worldview = None # Tile
        
        # current status/needs
        self.time = 0
        self.health = 1.0
        self.thirst = 0

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
        """Injure this person by a certain amount (0.0<=amount<=1.0)"""
        self.health -= amount
        if self.health < 0.0:
            self.health = 0.0
    
    def log(self, event_cls, *args, **kw):
        """Convenience method for self.diary.log(...)"""
        args = list(args)
        args.append(self.time)
        args.append(self)
        args.append(self.worldview.locality_copy())
        self.diary.log(event_cls(*args, **kw))

    def tick(self, i):
        # update stats
        self.time = i
        self.thirst += 1

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
        
    def action(self):
        self.log(event.Terrain)

        # What will character decide to do?
        action = None

        # What is character's biggest need?
        need = None
        if self.thirst > 6:
            self.log(event.Thirst, self.thirst)
            need = 'water'
        elif len(self.worldview.people) > 1:
            self.log(event.Occupants)
            # run away if shy
            if random.random() < self.shy:
                self.log(event.Emotion, 'afraid')
                self.log(event.Motivation, 'escape')
                need = 'escape'
            else:
                # pick a person and attempt to fight them
                opponent = self.worldview.people.random(self, 1)[0]
                self.log(event.Attack, opponent)
                opponent.log(event.Attacked, self)
                fight = Fight(self, opponent)
                fight()
                if not self.dead:
                    self.log(event.Fight, fight)
                else:
                    opponent.log(event.Fight, fight)
                return

        if need is None:
            # nothing in particular to do.
            if random.random() < self.explorer:
                action = 'explore'
            else:
                action = None
        elif need == 'escape':
            action = 'explore'
        elif need == 'water':
            path = self.worldview.path_to('river')
            if path is None:
                # don't know any water, explore some more.
                self.log(event.Motivation, 'get to water')
                self.log(event.Knowledge, 'location', 'water', -1, None)
                self.log('I don\'t know where there is water')
                action = 'explore'
            elif path[0][1] == '':
                # we're already at water
                self.log(event.Surroundings, 'water')
                action = 'drink'
            else:
                self.log(event.Motivation, 'get to water')
                self.log(event.Knowledge, 'location', 'water', 1, path[0][1])
                action = 'move ' + path[0][1]

        if action is None:
            self.log(event.Chill)
        elif action in ('explore'):
            neighbours = self.tile.neighbours
            direction = random.choice(list(sorted(neighbours)))
            self._move(direction, neighbours[direction])
        elif action.startswith('move '):
            direction = action.split(' ', 1)[1]
            self._move(direction, getattr(self.tile, direction)) 
        elif action == 'drink':
            self.thirst = 0
            self.log(event.Action, "drink")
        else:
            self.log(event.Action, 'DEBUG SHOULD NOT REACH HERE')

    def _move(self, direction, newtile):
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

