import csv
import random
import bisect
import itertools

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

class Person:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    @classmethod
    def from_random(cls, namegen):
        return cls(*namegen())

    def __str__(self):
        return "%s (%s)" % (self.name, self.gender)

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
        people.append(Person.from_random(namegen))

    print(world)
    for person in people:
        print(person)

if __name__ == '__main__':
    import sys
    random.seed(0)
    novel(int(sys.argv[1]), int(sys.argv[2]))
