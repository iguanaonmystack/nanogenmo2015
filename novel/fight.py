import random
import itertools

from tools import Weapon

class FightAction:
    def __init__(self, subject, verb, weapon, strike_power, victim, victim_health, victim_part):
        self.subject = subject
        self.verb = verb
        self.weapon = weapon
        self.strike_power = strike_power
        self.victim = victim
        self.victim_health = victim_health
        self.victim_part = victim_part

class Fight:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.actions = []
    
    def __call__(self):
        for person, opponent in itertools.cycle((
            (self.p1, self.p2), (self.p2, self.p1))):
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
            verb = random.choice(weapon.verbs)
            target = random.choice(weapon.targets)
            self.actions.append(FightAction(
                person, verb, weapon, weapon.power,
                opponent, opponent.health, target))
            opponent.injure(weapon.power)
            if opponent.dead:
                break

