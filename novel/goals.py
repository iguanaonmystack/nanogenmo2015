import random
import bisect
import logging

from . import event
from . import fight

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

    def add(self, goal_cls, *args, **kw):
        kw['person'] = self.person
        goal = goal_cls(*args, **kw)
        bisect.insort(self, goal)

    def add_inst(self, goal):
        bisect.insort(self, goal)

    def add_or_replace(self, goal_cls, *args, **kw):
        for item in self:
            if isinstance(item, goal_cls):
                self.remove(item)
                break
        self.add(goal_cls, *args, **kw)

class Goal:
    """A (potentially) multi-move aim of a person."""
    def __init__(self, priority, person=None):
        self.priority = priority
        self.person = person
        logging.debug("Goal created for %s: %s (%d)", self.person, self.__class__, self.priority)
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

class GoTo(Goal):
    """Character aims to reach a certain location."""
    def __init__(self, terrain, *args, **kw):
        super().__init__(*args, **kw)
        self.terrain = terrain
        self.person.log(event.Motivation, 'get to ' + self.terrain)
    def possible(self):
        self.path = self.person.worldview.path_to(self.terrain)
        if self.path is None:
            # Character doesn't know where there is water; explore.
            self.person.log(event.Knowledge, 'location', self.terrain, -1, None)
            self.person.goals.add_or_replace(Explore, None, self.priority)
            return False
        elif self.path[0][1] == '':
            # already at water, so this goal is redundant
            self.person.log(event.Surroundings, 'water')
            self.person.goals.remove(self)
            return False
        else:
            self.person.log(event.Knowledge, 'location', self.terrain, 1, self.path[0][1])
            return True
    def achieve(self):
        # don't call super; we don't want to remove ourself until dest reached.
        direction = self.path[0][1]
        self.person._move(direction, getattr(self.person.tile, direction))

class Drink(Goal):
    """Character aims to quench their thirst."""
    def possible(self):
        if self.person.worldview.terrain == 'river':
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
        self.sleeping = False
    def possible(self):
        # don't wake up if asleep
        if self.sleeping:
            return True
        # only rest/sleep when alone.
        if len(self.person.tile.people) > 1:
            return False
        self.person.log(event.Chill)
        return True
    def achieve(self):
        if self.person.awake > 6:
            # fall asleep rather than resting
            self.sleeping = True
            self.person.log(event.Sleep)
        self.person.awake -= 2 # 2 to compensate for per-tick increase by 1
        if self.person.awake < 3:
            if random.random() < 0.3:
                # Wake up
                self.sleeping = False
        if self.person.awake < 0:
            self.person.awake = 0
