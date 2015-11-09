import math
import random

class Event:
    def __init__(self, time, person, worldview):
        self.time = time
        self.worldview = worldview
        self.person = person
    def clauses(self):
        """A generator that yields diary text."""
        raise NotImplementedError('Must be implemented in Event subclass')

class Terrain(Event):

    def clauses(self):
        if self.worldview.visited == 1:
            # first visit
            yield from self.first_visit()
        else:
            yield from self.subsequent_visit()

    def first_visit(self):
        yield "I've come across a %s" % (
            self.worldview.terrain)

    def subsequent_visit(self):
        yield "I'm back at the %s" % (
            self.worldview.terrain)
        if self.worldview.visited > 1:
            yield "It's been %d hours since I was last here" % (
                self.worldview.visited - 1)

class Thirst(Event):
    def __init__(self, thirst, *args, **kw):
        super().__init__(*args, **kw)
        self.thirst = thirst

    def clauses(self):
        if self.thirst > 10:
            yield "I'm really thirsty"
        elif self.thirst > 7:
            if random.random() > 0.5:
                yield "I'm thirsty"
        else:
            yield "I'm getting thirsty"

class Occupants(Event):
    
    def clauses(self):
        if self.worldview.visited == 1:
            # first consecutive tick in this tile
            peoplelist = []
            for p in self.worldview.people:
                if p is self.person:
                    continue
                peoplelist.append(p.name)
            if len(peoplelist) > 1:
                peoplelist[-1] = 'and ' + peoplelist[-1]
            are = 'are' if len(peoplelist) != 1 else 'is'
            if random.random() > 0.5:
                if len(peoplelist) > 2:
                    yield '%s %s here' % (', '.join(peoplelist), are)
                else:
                    yield '%s %s here' % (' '.join(peoplelist), are)
            else:
                yield 'I can see %s' % (' '.join(peoplelist))
        else:
            # Only log if someone arrived or departed.
            # TODO
            pass

class Emotion(Event):
    def __init__(self, emotion, *args, **kw):
        super().__init__(*args, **kw)
        self.emotion = emotion

    def clauses(self):
        if random.random() > 0.3:
            yield random.choice([
                "I'm feeling %s",
                "I'm %s"]) % (self.emotion)

class Motivation(Event):
    def __init__(self, motivation, *args, **kw):
        super().__init__(*args, **kw)
        self.motivation = motivation

    def clauses(self):
        yield random.choice([
            "I need to %s",
            "gotta %s",
            "I have to %s",
            "I want to %s"]) % (self.motivation)

class Knowledge(Event):
    def __init__(self, what, noun, posneg, specific, *args, **kw):
        super().__init__(*args, **kw)
        self.what = what
        self.noun = noun
        self.posneg = posneg
        self.specific = specific

    def clauses(self):
        if not self.specific or random.random() > 0.8:
            yield "I %sknow the %s of %s" % (
                self.posneg < 0 and "don't " or '',
                self.what,
                self.noun)
            if self.specific:
                yield "it is %s" % self.specific
        else:
            yield 'there is %s %s' % (self.noun, self.specific)

class Surroundings(Event):
    def __init__(self, item, *args, **kw):
        super().__init__(*args, **kw)
        self.item = item

    def clauses(self):
        yield "there is %s here" % (self.item)

class Action(Event):
    def __init__(self, verb, *args, **kw):
        super().__init__(*args, **kw)
        self.verb = verb

    def clauses(self):
        yield "I %s" % (self.verb)

class Movement(Event):
    def __init__(self, direction, *args, **kw):
        super().__init__(*args, **kw)
        self.direction = direction

    def clauses(self):
        neighbour = getattr(self.worldview, self.direction, None)
        yield "I move %s%s" % (
            self.direction,
            ' to the %s' % (neighbour.terrain) if neighbour else ''
        )

class Tick(Event):
    def __init__(self, hour, *args, **kw):
        super().__init__(*args, **kw)
        self.hour = hour

    def clauses(self):
        if self.hour > 0 and self.hour % 24 == 0:
            days = self.hour // 24
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(days % 10, 'th')
            yield random.choice([
                "I've now been in the game for %d full days" % (days),
                "this is now my %d%s day in the game" % (days + 1, suffix)])

class Chill(Event):
    def clauses(self):
        return ['and here I am']

class Attack(Event):
    def __init__(self, opponent, *args, **kw):
        super().__init__(*args, **kw)
        self.opponent = opponent
    def clauses(self):
        yield "I attack %s" % self.opponent.name

class Attacked(Event):
    def __init__(self, opponent, *args, **kw):
        super().__init__(*args, **kw)
        self.opponent = opponent
    def clauses(self):
        yield "%s attacks me" % self.opponent.name

class Fight(Event):
    def __init__(self, fight, *args, **kw):
        super().__init__(*args, **kw)
        self.fight = fight
    
    def clauses(self):
        for action in self.fight.actions:
            weapon_adjective = random.choice(action.weapon.adjectives)
            if action.subject is self.person:
                yield "I %s %s with my %s %s in the %s" % (
                    action.verb, action.victim,
                    weapon_adjective, action.weapon.name,
                    action.victim_part)
                victim_health = action.victim_health - action.strike_power
                if action.victim_health - action.strike_power <= 0.0:
                    yield "I've killed %s" % (action.victim)
            else:
                yield "%s %s me in the %s with their %s %s" % (
                    action.subject, action.verb,
                    action.victim_part,
                    weapon_adjective, action.weapon.name)
                if action.victim_health - action.strike_power < 0.1:
                    yield "I don't think I'll last much longer"
