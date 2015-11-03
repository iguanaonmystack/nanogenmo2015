import random

from world import World, Tile, opposite_direction



class Person:
    def __init__(self, world, name, gender, tile=None):
        self.name = name
        self.gender = gender
        self.world = world
        self.tile = tile

        # fixed behaviour attributes
        self.shy = 0.5

        # knowledge
        self.previous_worldview = None # Tile
        self.last_direction = None
        self.worldview = None # Tile
        
        # current status/needs
        self.thirsty = 0


    @classmethod
    def from_random(cls, world, namegen):
        return cls(world, *namegen())

    def __str__(self):
        return "%s" % (self.name)

    def __repr__(self):
        return "Person(%r, %r, %r, %r)" % ( 
            self.world, self.name, self.gender, self.posx, self.posx)

    def tick(self):
       
        # update stats
        self.thirsty += 1

       

    def observe(self):
        # update worldview
        self.previous_worldview = self.worldview
        tile_as_observed = Tile(self.tile.terrain)
        if self.previous_worldview is not None and self.last_direction is not None:
            setattr(self.previous_worldview, self.last_direction, tile_as_observed)
            setattr(tile_as_observed, opposite_direction(self.last_direction), self.previous_worldview)
        self.worldview = tile_as_observed
        
    def action(self):
        # update worldview
        self.observe()

        # What will character decide to do?
        action = None

        # What is character's biggest need?
        need = None
        if self.thirsty > 6:
            need = 'water'
        elif len(self.tile.people) > 1:
            # run away if shy
            if random.random() < self.shy:
                need = 'escape'

        if need is None:
            # nothing in particular to do.
            action = 'explore'
        elif need == 'water':
            path = self.worldview.path_to('water')
            if path is None:
                # don't know any water, explore some more.
                action = 'explore'
            elif path[0][1] == '':
                # we're already at water
                action = 'drink'
            else:
                action = 'move ' + path[0][1]

        if action is None:
            pass
        elif action in ('explore', 'escape'):
            self.tile.people.remove(self)
            neighbours = self.tile.neighbours
            self.last_direction = random.choice(list(self.tile.neighbours))
            self.tile = neighbours[self.last_direction]
            self.tile.people.add(self)
        elif action.startswith('move '):
            direction = action.split(' ', 1)[1]
            self.tile.people.remove(self)
            self.last_direction = direction
            self.tile = getattr(self.tile, direction)
            self.tile.people.add(self)
        elif action == 'drink':
            self.thirst = 0
  


