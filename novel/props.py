import random

class Prop:
    """a prop"""
    def __str__(self):
        return self.__class__.__doc__
    def noteworthy(self, other_props):
        return True

class PlaceToSleep(Prop):
    """a place to sleep"""

class Tree(PlaceToSleep):
    """a tree"""
    def noteworthy(self, other_props):
        tree_count = 0
        for prop in other_props:
            if prop.__class__ == Tree: tree_count += 1
        if tree_count > 1: # 1 is us.
            return False
        return True

class Bush(PlaceToSleep):
    """a bush"""

class Water(Prop):
    """water"""
    def noteworthy(self, other_props):
        if self.__class__ == Water: return False
        return True

class Brook(Water):
    """a brook"""

class Stream(Water):
    """a stream"""

class Landmark(Prop):
    """a non-functional but distinctive prop"""
    def __init__(self):
        super().__init__()
        # TODO - can we randomly generate these?
        self.item = random.choice([
            'giant lightning-struck tree',
            'statue of a polar bear',
            'pair of fallen telegraph poles',
            'ancient-looking well',
            'abandoned car',
            'derelict shack',
            'orange'])
    def __str__(self):
        if self.item[0] in 'aeiou':
            return 'an ' + self.item
        return 'a ' + self.item

