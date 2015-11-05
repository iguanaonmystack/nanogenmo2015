import random
import event

class Diary:
    def __init__(self):
        self.events = []

    def log(self, event):
        self.events.append(event)

    def write(self):
        for event in self.events:
            for clause in event.clauses():
                yield clause + random.choice(['. ', '; ', ', ', '! '])

        self.events[:] = []
