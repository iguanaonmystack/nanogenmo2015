import csv
import time
import random
import bisect
import itertools

class World(list):
    def __init__(self, x, y):
        self.sizex = x
        self.sizey = y
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
    
    def __str__(self):
        s = []
        for x in reversed(range(self.sizex)):
            for y in range(self.sizey):
                s.append("%s | " % (self[x][y]))
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
        terrain = random.choice(list(cls.terrains.keys()))
        return cls(terrain)
    
    def __str__(self):
        return "%s %s" % (self.terrain, len(self.people))

    @property
    def neighbours(self):
        return [t for t in (self.north, self.east, self.south, self.west) if t]

class Person:
    def __init__(self, world, name, gender, tile=None):
        self.name = name
        self.gender = gender
        self.world = world
        self.tile = tile

        # behaviour attributes
        self.flighty = 0.5

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
        self.tile.people.remove(self)
        self.tile = random.choice(self.tile.neighbours)
        self.tile.people.add(self)

    def action(self):
        pass

class NameGenerator:
    def __init__(self, csvfile):
        self.choices = []
        self.weights = []
        reader = csv.reader(csvfile)
        for firstname, gender, weighting in reader:
            self.choices.append((firstname, gender))
            self.weights.append(int(weighting))
            self.cumdist = list(itertools.accumulate(self.weights))

    def __call__(self):
        x = random.random() * self.cumdist[-1]
        return self.choices[bisect.bisect(self.cumdist, x)]

def novel(x, y):
    world = World(x, y)
    names = []
    with open('names.csv') as csvfile:
        namegen = NameGenerator(csvfile)
    
    people = []
    for i in range(12):
        person = Person.from_random(world, namegen)
        person.tile = world[x//2][y//2]
        person.tile.people.add(person)
        people.append(person)

    print("Dramatis Personae:")
    for person in people:
        print(person)
    
    print()
    print(world)

    # tick:
    for i in range(10):
        time.sleep(1)
        # move people:
        for person in people:
            person.move()
        # do actions:
        for person in people:
            person.action()
        print()
        print(world)

if __name__ == '__main__':
    import sys
    random.seed(0)
    novel(int(sys.argv[1]), int(sys.argv[2]))
