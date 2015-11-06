import math
import random

class Event:
    def __init__(self, worldview):
        self.worldview = worldview
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
        yield "I'm back at the %s at" % (
            self.worldview.terrain)
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
                if p is self:
                    continue
                peoplelist.append(p.name)
            peoplelist[-1] = 'and ' + peoplelist[-1]
            yield '%s are here' % ', '.join(peoplelist)
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
            "Gotta %s",
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
        yield "I %sknow the %s of %s" % (
            self.posneg < 0 and "don't " or '',
            self.what,
            self.noun)
        if self.specific:
            yield "It is %s" % self.specific

class Surroundings(Event):
    def __init__(self, item, *args, **kw):
        super().__init__(*args, **kw)
        self.item = item

    def clauses(self):
        yield "There is %s here" % (self.item)

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
                "This is now my %d%s day in the game" % (days + 1, suffix)])
