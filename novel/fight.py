import logging
import random
import itertools

from .tools import Weapon

class FightAction:
    def __init__(self, subject, verb, weapon, strike_power, victim, victim_health, victim_part):
        self.subject = subject
        self.verb = verb
        self.weapon = weapon
        self.strike_power = strike_power
        self.victim = victim
        self.victim_health = victim_health
        self.victim_part = victim_part

class Escape:
    def __init__(self, person):
        self.person = person

class Fight:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.actions = []
    
    def __call__(self):
        for person, opponent in itertools.cycle((
            (self.p1, self.p2), (self.p2, self.p1))):
            # attacked person gets a chance to escape
            if person == self.p2:
                if random.random() < person.escapologist:
                    self.actions.append(Escape(person))
                    break
            # pick best weapon:
            weapons = [t for t in person.tools if isinstance(t, Weapon)]
            weapons = sorted(weapons, key=lambda w: -w.power)
            best_power = weapons[0].power
            choices = []
            for weapon in weapons:
                if weapon.power == best_power:
                    choices.append(weapon)
                else:
                    break
            weapon = random.choice(choices)
            # pick target and action
            verb = random.choice(weapon.verbs)
            target = random.choice(weapon.targets)
            self.actions.append(FightAction(
                person, verb, weapon, weapon.power,
                opponent, opponent.health, target))
            assert weapon.power > 0
            opponent.injure(weapon.power)
            logging.debug("injured opponent %f, health now %f",
                weapon.power, opponent.health)
            # each attack has a chance of fatally wounding opponent
            if random.random() < 0.05:
                logging.debug('opponent is fatally wounded')
                opponent.health_delta -= 0.10
            # cleanup
            if opponent.dead:
                print("*", person.name, "killed", opponent.name)
                break

