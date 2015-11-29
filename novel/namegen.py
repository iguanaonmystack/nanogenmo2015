import os
import csv
import random
import bisect
import itertools

class _NameGenerator:
    def __init__(self, csvfile):
        self.choices = []
        self.weights = []
        self.past = set()
        reader = csv.reader(csvfile)
        for firstname, gender, weighting in reader:
            self.choices.append((firstname, gender))
            self.weights.append(int(weighting))
            self.cumdist = list(itertools.accumulate(self.weights))

    def __call__(self):
        choice = None
        while choice is None or choice in self.past:
            x = random.random() * self.cumdist[-1]
            choice = self.choices[bisect.bisect(self.cumdist, x)]
        self.past.add(choice)
        return choice

with open(os.path.join(os.path.dirname(__file__), 'names.csv')) as csvfile:
    # singleton object
    namegen = _NameGenerator(csvfile)

