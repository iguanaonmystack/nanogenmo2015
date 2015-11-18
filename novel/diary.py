import random
import logging

class Diary:
    def __init__(self, person):
        self.person = person
        self.events = []
        self._punct = ['. ', '; ', ', ', '! ']
        self.time = None # most recent update time

    def punct(self):
        sentence_end = False
        ret = random.choice(self._punct)
        if ret in ('. ', '! '):
            sentence_end = True
            if random.random() < 0.2:
                ret += '\n\n'
        return ret, sentence_end

    def log(self, time, event):
        logging.debug('logging event %r with time %r', event, time)
        self.time = time
        self.events.append(event)

    def write(self):
        between = False
        end = False
        i = -1
        for i, event in enumerate(self.events):
            if between:
                punct, end = self.punct()
                yield punct
            between = False
            for j, clause in enumerate(event.clauses(self)):
                between = True
                if j > 0:
                    punct, end = self.punct()
                    yield punct
                if end:
                    yield clause[0].upper() + clause[1:] # TODO this is bad
                else:
                    yield clause
        if i != -1:
            yield random.choice(['.', '!'])

        self.events[:] = []

    def print(self):
        print(self.person.name)
        print('-' * len(self.person.name))
        print()
        for clause in self.write():
            print(clause, end='')
        print()
        print()
