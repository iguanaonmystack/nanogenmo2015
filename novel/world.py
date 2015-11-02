import random

class World(list):
    def __init__(self, x, y):
        self.sizex = x
        self.sizey = y

    @classmethod
    def from_random(cls, x, y):
        self = cls(x, y)
        for i in range(x):
            row = []
            self.append(row)
            for j in range(y):
                tile = Tile.from_random()
                row.append(tile)
                if j:
                    tile.west = self[i][j - 1]
                    self[i][j - 1].east = tile
                if i:
                    tile.south = self[i - 1][j]
                    self[i - 1][j].north = tile
        return self
    
    def __str__(self):
        s = []
        for x in reversed(range(self.sizex)):
            for y in range(self.sizey):
                s.append("%s | " % (self[x][y]))
            s.append('\n')
        return ''.join(s)


class Tile:
    terrains = {
        'water',
        'forest',
        'meadow',
    }

    def __init__(self, terrain):
        self.terrain = terrain
        self.west = None
        self.east = None
        self.north = None
        self.south = None
        class PeopleSet(set):
            def __str__(self):
                return ', '.join(str(p) for p in self)
        self.people = PeopleSet()

    @classmethod
    def from_random(cls):
        terrain = random.choice(list(cls.terrains))
        return cls(terrain)
    
    def __str__(self):
        return "%06s %2d" % (self.terrain, len(self.people))

    @property
    def neighbours(self):
        d = {}
        for direction in ('north', 'east', 'south', 'west'):
            if getattr(self, direction) is not None:
                d[direction] = getattr(self, direction)
        return d

    
    def find_nearest(self, terrain):
        pass


def opposite_direction(direction):
    d = {'north': 'south',
        'east': 'west',
        'south': 'north',
        'west': 'east'}
    return d[direction]
