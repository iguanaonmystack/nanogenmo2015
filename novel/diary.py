import random

class Diary:
    def __init__(self):
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
        self.time = time
        self.events.append(event)

    def write(self):
        between = False
        end = False
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
        yield random.choice(['.', '!'])

        self.events[:] = []
