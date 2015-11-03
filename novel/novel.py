import csv
import time
import random
import bisect
import itertools

from world import World, Tile
from person import Person

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
    world = World.from_random(x, y)
    names = []
    with open('names.csv') as csvfile:
        namegen = NameGenerator(csvfile)
    
    people = []
    for i in range(3):
        person = Person.from_random(world, namegen)
        person.tile = world[x//2][y//2]
        person.tile.people.add(person)
        people.append(person)

    print("Dramatis Personae")
    print('-----------------')
    print()
    for person in people:
        print(person)
    print()

    # tick:
    for i in range(100):
        print('Map for time period', i + 1)
        print('--------------------' + '-'*len(str(i + 1)))
        print()
        print(world)

        # update everyone's stats and have them look around:
        for person in people:
            person.tick()
        
        # do actions:
        for person in people:
            person.action()

        for person in people:
            print(person.name)
            print('-' * len(person.name))
            print()
            print(person.diary())
            print()

        # grim reaper:
        for person in people:
            if person.dead:
                # died during their turn
                print("*", person.name, 'has died.')
                print()
            elif person.thirst > 10:
                print("*", person.name, 'has died of thirst.')
                print()
                person.dead = True
                
            if person.dead:
                people.remove(person)

        if len(people) == 1:
            print("*", people[0].name, 'has won.')
            break
        if len(people) == 0:
            print("*", "Everybody has died.")
            break
        
if __name__ == '__main__':
    import sys
    novel(int(sys.argv[1]), int(sys.argv[2]))

