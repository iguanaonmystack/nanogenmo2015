import os
import csv
import time
import random
import bisect
import itertools

from .world import World, Tile
from .person import Person
from . import event

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

def novel(x, y, num_people):
    world = World.from_random(x, y)
    names = []
    with open(os.path.join(os.path.dirname(__file__), 'names.csv')) as csvfile:
        namegen = NameGenerator(csvfile)
    
    people = []
    for i in range(num_people):
        person = Person.from_random(world, namegen)
        person.tile = world[x//2][y//2]
        person.tile.people.add(person)
        people.append(person)

    print("Dramatis Personae")
    print('-----------------')
    print()
    for person in people:
        print('*', person)
    print()

    last_diary = None
    # tick:
    for i in range(1000):
        #print('Map for time period', i + 1)
        #print('--------------------' + '-'*len(str(i + 1)))
        #print()
        #print(world)

        # update everyone's stats and have them look around:
        for person in people:
            person.tick(i)
        
        # do actions:
        for person in people:
            person.action()

        for person in people:
            if person.diary.events \
                and isinstance(person.diary.events[-1], event.Chill):
                
                print(person.name)
                print('-' * len(person.name))
                print()
                for clause in person.diary.write():
                    print(clause, end='')
                print()
                print()
                last_diary = person

        # grim reaper:
        for person in people:
            if person.thirst > 10:
                print("*", person.name, 'perishes from thirst.')
                person.injure(-100000)
                
            if person.dead:
                people.remove(person)
                person.tile.people.remove(person)

        if len(people) == 1:
            person = people[0]
            print(person.name)
            print('-' * len(person.name))
            print()
            for clause in person.diary.write():
                print(clause, end='')
            print()
            print()
            print("*", person.name, 'has won.')
            break
        if len(people) == 0:
            print("*", "Everybody has died.")
            break
        

