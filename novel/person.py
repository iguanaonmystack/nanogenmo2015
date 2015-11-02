import random

from world import World, Tile, opposite_direction



class Person:
    def __init__(self, world, name, gender, tile=None):
        self.name = name
        self.gender = gender
        self.world = world
        self.tile = tile

        # fixed behaviour attributes
        self.flighty = 0.5

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

    def move(self):
        # chance of staying put
        if random.random() > self.flighty:
            return

        # move
        self.tile.people.remove(self)
        neighbours = self.tile.neighbours
        self.last_direction = random.choice(list(self.tile.neighbours))
        self.tile = neighbours[self.last_direction]
        self.tile.people.add(self)
        
        # update stats
        self.thirsty += 1

        # update worldview
        self.observe()
        

    def observe(self):
        # update worldview
        self.previous_worldview = self.worldview
        tile_as_observed = Tile(self.tile.terrain)
        if self.previous_worldview is not None and self.last_direction is not None:
            setattr(self.previous_worldview, self.last_direction, tile_as_observed)
            setattr(tile_as_observed, opposite_direction(self.last_direction), self.previous_worldview)
        self.worldview = tile_as_observed
        
    def action(self):
        # starting condition:
        if self.worldview is None:
            self.observe()

        # What is character's biggest need?
        need = 'water'

        if need == 'water':
            self.worldview.find_nearest('water')
