import random
import bisect
import logging

from . import event
from . import fight
from . import terrains

class Goals(list):
    def __init__(self, person, *args, **kw):
        super().__init__(*args, **kw)
        self.person = person

    def __contains__(self, item):
        if isinstance(item, type):
            # search for a type of goal
            for i in self:
                if isinstance(i, item):
                    return True
            return False
        else:
            return super().__contains__(item)

    def add(self, goal, *args, **kw):
        if isinstance(goal, type):
            kw['person'] = self.person
            goal = goal(*args, **kw)
        bisect.insort(self, goal)

    def add_or_replace(self, goal, *args, **kw):
        if isinstance(goal, type):
            for item in self:
                if isinstance(item, goal):
                    self.remove(item)
                    break
        else:
            for item in self:
                if item.__class__ == goal.__class__:
                    self.remove(item)
                    break
        self.add(goal, *args, **kw)

class Goal:
    """A (potentially) multi-move aim of a person."""
    def __init__(self, priority, person=None):
        self.priority = priority
        self.person = person
        self.subgoals = []
        logging.debug("Goal created for %s: %s (%d)", self.person, self.__class__, self.priority)
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.priority)
    def __lt__(self, other):
        return self.priority < other.priority
    def possible(self):
        """Is this goal possible to achieve right now?"""
        return True
    def achieve(self):
        """Make person perform the necessary actions to achieve this
        goal."""
        logging.debug('goal %s achieved', self)
        self.person.goals.remove(self)
        for subgoal in self.subgoals:
            logging.debug('subgoal %s achieved', subgoal)
            subgoal.person.goals.remove(subgoal)

class GoTo(Goal):
    """Character aims to reach a certain location."""
    def __init__(self, prop, *args, **kw):
        super().__init__(*args, **kw)
        self.prop = prop
        self.person.log(event.Motivation, 'get to %s' % self.prop.__doc__)
    def possible(self):
        logging.debug("Calculating path to %s", self.prop)
        self.path = self.person.worldview.path_to(self.prop)
        if self.path is None:
            logging.debug('no path available')
            # Character doesn't know where there is water; explore.
            self.person.log(event.Knowledge, 'location', self.prop.__doc__, -1, None)
            self.person.goals.add_or_replace(Explore, None, self.priority)
            return False
        elif self.path[0][1] == '':
            logging.debug('already at target')
            # already at water, so this goal is redundant
            self.person.log(event.Surroundings, 'water')
            self.person.goals.remove(self)
            return False
        else:
            logging.debug('successful path calculated')
            self.person.log(event.Knowledge, 'location', self.prop.__doc__, 1, self.path[0][1])
            return True
    def achieve(self):
        # don't call super; we don't want to remove ourself until dest reached.
        direction = self.path[0][1]
        self.person._move(direction, getattr(self.person.tile, direction))

class Drink(Goal):
    """Character aims to quench their thirst."""
    def possible(self):
        if isinstance(self.person.worldview.terrain, terrains.Lake):
            return True
        return False
    def achieve(self):
        super().achieve()
        self.person.thirst = 0
        self.person.log(event.Action, "drink")

class Fight(Goal):
    """Character is spoiling for a fight."""
    def __init__(self, opponent, *args, **kw):
        super().__init__(*args, **kw)
        self.opponent = opponent
    def possible(self):
        if self.opponent in self.person.tile.people:
            return True
        return False
    def achieve(self):
        super().achieve()
        self.person.log(event.Attack, self.opponent)
        self.opponent.log(event.Attacked, self.person)
        duel = fight.Fight(self.person, self.opponent)
        duel()
        if not self.person.dead:
            self.person.log(event.Fight, duel)
        else:
            self.opponent.log(event.Fight, duel)

class Explore(Goal):
    def __init__(self, direction, *args, **kw):
        super().__init__(*args, **kw)
        self.direction = direction
    def possible(self):
        return True
    def achieve(self):
        super().achieve()
        direction = self.direction
        if direction is None:
            neighbours = self.person.tile.neighbours
            direction = random.choice(list(sorted(neighbours)))
        self.person._move(direction, getattr(self.person.tile, direction))

class Escape(Explore):
    # just subclass Explore for now
    def __init__(self, *args, **kw):
        super().__init__(None, *args, **kw)

class Rest(Goal):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
    def possible(self):
        # only rest when alone.
        if len(self.person.tile.people) > 1:
            return False
        return True
    def achieve(self):
        # This compensates for the hourly +=1 but player will
        # not be able to stay awake just by resting (unless they
        # rest /every/ move).
        self.person.awake -= 1
        if self.person.awake < 0:
            self.person.awake = 0
        self.person.log(event.Rest)
