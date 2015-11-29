import os
import time
import logging

from .world import World, Tile
from .person import Person
from .namegen import namegen
from . import event

def novel(x, y, num_people):
    world = World.from_random(x, y)
    names = []
    
    people = []
    for i in range(num_people):
        person = Person.from_random(world, namegen)
        person.seq_id = i
        person.tile = world[x//2][y//2]
        person.tile.people.add(person)
        people.append(person)

    print('Map of Arena')
    print('------------' + '-'*len(str(i + 1)))
    print()
    print(world)
    print()
    print('Key:')
    print()
    print('    ~~ = water; || = forest; [empty] = meadows. | = border separator')
    print()
    print("Dramatis Personae")
    print('-----------------')
    print()
    for person in people:
        print('*', person)
    print()

    last_diary = None
    tick = -1
    while True:
        tick += 1
        #print('Map for time period', i + 1)
        #print('--------------------' + '-'*len(str(i + 1)))
        #print()
        #print(world)

        # update everyone's stats and have them look around:
        logging.debug('ticking %d people', len(people))
        for person in people:
            person.tick(tick)

            if person.dead:
                print("*", person.name, "collapses from their wounds")
        
        # do actions:
        for person in people:
            # TODO randomise to avoid first player always attacking first.
            person.action()

            # grim reaper:
            for person in people:
                if person.thirst > 24:
                    print("*", person.name, 'perishes from thirst.')
                    person.injure(100000)
                    assert person.dead, person.health
                    
                if person.dead:
                    people.remove(person)
                    #person.diary.print()
                    print("*", person.name, "has died")
                    if len(people) != 1:
                        print("* %d people remain" % len(people))
                    else:
                        print("* 1 person remains")
                    print()
                    person.tile.people.remove(person)

        for person in people:
            if person.diary.events \
            and isinstance(person.diary.events[-1], (event.Rest, event.Wake)):
                person.diary.print()
                last_diary = person

        if len(people) == 1:
            person = people[0]
            person.diary.print()
            print("*", person.name, 'has won.')
            break
        if len(people) == 0:
            print("*", "Everybody has died.")
            break
        

