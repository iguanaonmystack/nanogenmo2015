import random

class World:
    def __init__(self, x, y):
        self.coord = []
        self.sizex = x
        self.sizey = y
        for i in range(x):
            row = []
            self.coord.append(row)
            for j in range(y):
                row.append(Tile.from_random())
    
    def __str__(self):
        s = []
        for x in reversed(range(self.sizex)):
            for y in range(self.sizey):
                s.append("%s(%d,%d) | " % (self.coord[x][y], x, y))
            s.append('\n')
        return ''.join(s)


class Tile:
    terrains = {
        '~': 'water',
        '#': 'forest',
        '_': 'meadow',
    }

    def __init__(self, terrain):
        self.terrain = terrain

    @classmethod
    def from_random(cls):
        terrain = random.choice(list(cls.terrains.keys()))
        return cls(terrain)
    
    def __str__(self):
        return self.terrain

def novel(x, y):
    world = World(x, y)
    print(world)

if __name__ == '__main__':
    import sys
    random.seed(0)
    novel(int(sys.argv[1]), int(sys.argv[2]))
