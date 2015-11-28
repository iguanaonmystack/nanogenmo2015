import math
import random
import logging

from .text import verbs
from .fight import Escape, FightAction
from . import util

class Event:
    def __init__(self, time, person, worldview):
        self.time = time
        self.worldview = worldview
        self.person = person
    def clauses(self, diary):
        """A generator that yields diary text."""
        raise NotImplementedError('Must be implemented in Event subclass')

class Terrain(Event):

    def clauses(self, diary):
        logging.debug('Last visited tile %s: %d', self.worldview, self.worldview.visited)
        if self.worldview.visited == 1:
            # first visit
            yield from self.first_visit(diary)
        else:
            yield from self.subsequent_visit(diary)
        # TODO better segues when terrain type hasn't changed between tiles

    def first_visit(self, diary):
        logging.debug('diary.time %r, self.time: %r', diary.time, self.time)
        description = str(self.worldview.terrain)
        adjectives = list(self.worldview.terrain.adjectives)
        # TODO - synonyms?
        description = ', '.join(adjectives) + (' ' if adjectives else '') + description
        reltime = util.reltime(self.time, diary.time)
        if diary.time - self.time:
            time_before = False
            if random.random() < 0.4:
                time_before = True
            yield "%sI came across a %s%s" % (
                reltime + ' ' if time_before else '',
                description,
                '' if time_before else ' ' + reltime)
            is_ = 'was'
        else:
            yield "I'm now in a %s" % description
            is_ = 'is'
        for prop in self.worldview.terrain.props:
            if prop.noteworthy(self.worldview.terrain.props):
                yield "there %s %s here" % (is_, prop)

    def subsequent_visit(self, diary):
        description = str(self.worldview.terrain)
        adjectives = list(self.worldview.terrain.adjectives)
        # TODO - synonyms?
        description = ', '.join(adjectives) + (' ' if adjectives else '') + description
        noteworthy = []
        for prop in self.worldview.terrain.props:
            if prop.noteworthy(self.worldview.terrain.props):
                noteworthy.append(prop.definite)
        if len(noteworthy) > 1:
            noteworthy[-1] = 'and ' + noteworthy[-1]
        if noteworthy:
            comma = ', ' if len(noteworthy) > 3 else ' '
            description += ' with ' + comma.join(noteworthy)
        logging.debug('subsequent visit diary time %d, self time %d', diary.time, self.time)
        if not diary.time - self.time:
            yield "I'm now back at the %s" % (description)
            if self.worldview.visited > 2:
                yield "it's been %d hours since I was last here" % (
                    self.worldview.visited - 1)
        else:
            yield "I returned to the %s" % (description)
            yield util.reltime(self.time, diary.time)
            if self.worldview.visited > 2:
                yield "it was the first time I had been here for %d hours" % (
                    self.worldview.visited - 1)

class Thirst(Event):
    def __init__(self, thirst, *args, **kw):
        super().__init__(*args, **kw)
        self.thirst = thirst

    def clauses(self, diary):
        if self.thirst > 10:
            yield "I'm really thirsty"
        elif self.thirst > 7:
            if random.random() > 0.5:
                yield "I'm thirsty"
        else:
            yield "I'm getting thirsty"

class Occupants(Event):
    
    def clauses(self, diary):
        tense = 'present'
        here = 'here'
        if diary.time - self.time:
            tense = 'past'
            here = 'there'
        if self.worldview.visited == 1:
            # first consecutive tick in this tile
            peoplelist = []
            for p in self.worldview.people:
                if p is self.person:
                    continue
                peoplelist.append(p.name)
            if len(peoplelist) > 1:
                peoplelist[-1] = 'and ' + peoplelist[-1]
            number = 'plural' if len(peoplelist) != 1 else 'singular'
            if random.random() > 0.5:
                are = verbs.conjugate('is', tense, 3, number)
                if len(peoplelist) > 2:
                    yield '%s %s %s' % (', '.join(peoplelist), are, here)
                else:
                    yield '%s %s %s' % (' '.join(peoplelist), are, here)
            else:
                can = verbs.conjugate('can', tense, 1, 'singular')
                yield 'I %s see %s' % (can, ', '.join(peoplelist))
        else:
            # Only log if someone arrived or departed.
            # TODO
            pass

class Emotion(Event):
    def __init__(self, emotion, *args, **kw):
        super().__init__(*args, **kw)
        self.emotion = emotion

    def clauses(self, diary):
        if random.random() > 0.3:
            tense = 'present'
            if diary.time - self.time:
                tense = 'past'
            am = verbs.conjugate('am', tense, 1, 'singular')
            feel = verbs.conjugate('felt', tense, 1, 'singular')
            yield random.choice([
                "I %s feeling %s" % (am, self.emotion),
                "I %s %s" % (feel, self.emotion)])

class Motivation(Event):
    def __init__(self, motivation, *args, **kw):
        super().__init__(*args, **kw)
        self.motivation = motivation

    def clauses(self, diary):
        verbs = ['need to', 'must', 'have to', 'want to', 'gotta']
        if diary.time - self.time:
            verbs = ['needed to', 'had to', 'wanted to']
        verb = random.choice(verbs)
        yield "I %s %s" % (verb, self.motivation)

class Knowledge(Event):
    def __init__(self, what, noun, posneg, specific, *args, **kw):
        super().__init__(*args, **kw)
        self.what = what
        self.noun = noun
        self.posneg = posneg
        self.specific = specific

    def clauses(self, diary):
        know = 'know'
        is_ = 'is'
        if diary.time - self.time:
            know = 'knew'
            is_ = 'was'
        if not self.specific or random.random() > 0.8:
            yield "I %s%s the %s of %s" % (
                know,
                self.posneg < 0 and " not" or '',
                self.what,
                self.noun)
            if self.specific:
                yield "it %s %s" % (is_, self.specific)
        else:
            yield 'there %s %s %s' % (is_, self.noun, self.specific)

class Surroundings(Event):
    def __init__(self, item, *args, **kw):
        super().__init__(*args, **kw)
        self.item = item

    def clauses(self, diary):
        yield "there is %s here" % (self.item)

class Action(Event):
    def __init__(self, verb, *args, **kw):
        super().__init__(*args, **kw)
        self.verb = verb

    def clauses(self, diary):
        verb = self.verb
        if diary.time - self.time:
            verb = verbs.past_1s(self.verb)
        yield "I %s" % (self.verb)

class Movement(Event):
    def __init__(self, direction, *args, **kw):
        super().__init__(*args, **kw)
        self.direction = direction

    def clauses(self, diary):
        neighbour = getattr(self.worldview, self.direction, None)
        move = verbs.past_1s('move')
        yield "I %s %s%s" % (
            move,
            self.direction,
            ' to the %s' % (neighbour.terrain) if neighbour else ''
        )

class Tick(Event):
    def __init__(self, hour, *args, **kw):
        super().__init__(*args, **kw)
        self.hour = hour

    def clauses(self, diary):
        if self.hour > 0 and self.hour % 24 == 0:
            days = self.hour // 24
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get((days + 1) % 10, 'th')
            if diary.time - self.time:
                yield random.choice([
                    "I had been in the game for %d full days" % (days),
                    "it was then my %d%s day in the game" % (days + 1, suffix)])
            else:
                yield random.choice([
                    "I've now been in the game for %d full days" % (days),
                    "this is now my %d%s day in the game" % (days + 1, suffix)])

class Attack(Event):
    def __init__(self, opponent, *args, **kw):
        super().__init__(*args, **kw)
        self.opponent = opponent
    def clauses(self, diary):
        attack = 'attack'
        if diary.time - self.time:
            attack = 'attacked'
        yield "I %s %s" % (attack, self.opponent.name)

class Attacked(Event):
    def __init__(self, opponent, *args, **kw):
        super().__init__(*args, **kw)
        self.opponent = opponent
    def clauses(self, diary):
        attack = 'attacks'
        if diary.time - self.time:
            attack = 'attacked'
        yield "%s %s me" % (self.opponent.name, attack)

class Fight(Event):
    def __init__(self, fight, *args, **kw):
        super().__init__(*args, **kw)
        self.fight = fight
    
    def clauses(self, diary):
        for action in self.fight.actions:
            if isinstance(action, Escape):
                if action.person == self.person:
                    yield random.choice([
                        'I got away',
                        'I ran and escaped'])
                else:
                    yield random.choice([
                        '%s got away' % action.person,
                        '%s ran away' % action.person])
                continue
            # FightAction:
            weapon_adjective = random.choice(action.weapon.adjectives)
            if action.subject is self.person:
                yield "I %s %s with my %s %s in the %s" % (
                    verbs.past_1s(action.verb), action.victim,
                    weapon_adjective, action.weapon.name,
                    action.victim_part)
                victim_health = action.victim_health - action.strike_power
                logging.debug('victim health now %f', victim_health)
                if action.victim_health - action.strike_power <= 0.0:
                    yield "I killed %s" % (action.victim)
            else:
                yield "%s %s me in the %s with their %s %s" % (
                    action.subject, verbs.past_3s(action.verb),
                    action.victim_part,
                    weapon_adjective, action.weapon.name)
                if action.victim_health - action.strike_power < 0.1:
                    yield "I didn't think I'd last much longer"

class Sleep(Event):
    def clauses(self, diary):
        yield "I fell asleep"
class Wake(Event):
    def clauses(self, diary):
        yield "I woke up"
class Rest(Event):
    def clauses(self, diary):
        if random.random() < 0.7:
            return
        yield random.choice([
            "I'm now resting",
            "I'll stay here for a while",
            "going to take a nap now",
            "I'm laying low for a bit",
            "that's this diary up to date",
            "bye for now"])

