import random
from copy import copy

from world import World, Tile, opposite_direction

class Worldview(Tile):
    def __init__(self, posx, posy, terrain):
        super().__init__(posx, posy, terrain)
        self.visited = 0

class Person:
    def __init__(self, world, name, gender, tile=None):
        self.name = name
        self.gender = gender
        self.world = world
        self.tile = tile
        
        # log
        self._log = []

        # fixed behaviour attributes
        self.shy = 0.5

        # knowledge
        self.previous_worldview = None # Tile
        self.worldview = None # Tile
        
        # current status/needs
        self.dead = False
        self.thirst = 0


    @classmethod
    def from_random(cls, world, namegen):
        return cls(world, *namegen())

    def __str__(self):
        return "%s" % (self.name)

    def __repr__(self):
        return "Person(%r, %r, %r)" % ( 
            self.world, self.name, self.gender)
    
    def log(self, fmt, *args):
        self._log.append(fmt % args)

    def diary(self):
        diary = '. '.join(self._log) + '.'
        self._log = []
        return diary

    def tick(self):
        # update stats
        self.thirst += 1

        # update worldview
        self.observe()
        def increase_last_visited_count(tile):
            tile.visited += 1
        self.worldview.recursive_update(increase_last_visited_count)

    def observe(self):
        # update worldview
        if self.worldview is None:
            self.worldview = Worldview(
                self.tile.posx, self.tile.posy, self.tile.terrain)
        self.worldview.people = copy(self.tile.people)
        
    def action(self):
        if self.worldview.visited == 1:
            self.log('I\'ve come across a %s at (%d, %d)',
                self.worldview.terrain,
                self.worldview.posx, self.worldview.posy)
        else:
            self.log('Back at %s at (%d, %d) after %d hours',
                self.worldview.terrain,
                self.worldview.posx, self.worldview.posy,
                self.worldview.visited - 1)

        # What will character decide to do?
        action = None

        # What is character's biggest need?
        need = None
        if self.thirst > 6:
            self.log('Thirsty')
            need = 'water'
        elif len(self.worldview.people) > 1:
            self.log('%s are here', ', '.join(
                p.name for p in self.worldview.people if p is not self))
            # run away if shy
            if random.random() < self.shy:
                self.log('Must escape')
                need = 'escape'
            else:
                self.log('Feeling brave')

        if need is None:
            # nothing in particular to do.
            self.log('Bored')
            action = 'explore'
        elif need == 'escape':
            action = 'explore'
        elif need == 'water':
            self.log('Need water')
            path = self.worldview.path_to('river')
            if path is None:
                # don't know any water, explore some more.
                self.log('I don\'t know where there is water')
                action = 'explore'
            elif path[0][1] == '':
                # we're already at water
                self.log('There is water here')
                action = 'drink'
            else:
                self.log('I know there is water %s', path[0][1])
                action = 'move ' + path[0][1]

        if action is None:
            self.log('Nothing to do')
            pass
        elif action in ('explore'):
            neighbours = self.tile.neighbours
            direction = random.choice(list(sorted(neighbours)))
            self._move(direction, neighbours[direction])
        elif action.startswith('move '):
            direction = action.split(' ', 1)[1]
            self._move(direction, getattr(self.tile, direction)) 
        elif action == 'drink':
            self.thirst = 0
            self.log('Thirst quenched')
  

    def _move(self, direction, newtile):
        self.log("Moving %s", direction)
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

