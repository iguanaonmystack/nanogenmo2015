import random
import event

class Diary:
    def __init__(self):
        self.events = []
        self._punct = ['. ', '; ', ', ', '! ']

    def punct(self):
        ret = random.choice(self._punct)
        if ret in ('. ', '! ') and random.random() < 0.1:
            ret += '\n\n'
        return ret

    def log(self, event):
        self.events.append(event)

    def write(self):
        punct = False
        for i, event in enumerate(self.events):
            if punct:
                yield self.punct()
            punct = False
            for j, clause in enumerate(event.clauses()):
                punct = True
                if j > 0:
                    yield self.punct()
                yield clause
        yield random.choice(['.', '!'])

        self.events[:] = []
