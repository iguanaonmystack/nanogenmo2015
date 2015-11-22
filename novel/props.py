import random

class Prop:
    def __str__(self):
        return self.indefinite
    def noteworthy(self, other_props):
        return True

class PlaceToSleep(Prop):
    indefinite = 'a place to sleep'
    definite = 'the place to sleep'

class Tree(PlaceToSleep):
    indefinite = 'a tree'
    definite = 'the tree'
    def noteworthy(self, other_props):
        tree_count = 0
        for prop in other_props:
            if prop.__class__ == Tree: tree_count += 1
        if tree_count > 1: # 1 is us.
            return False
        return True

class Bush(PlaceToSleep):
    indefinite = 'a bush'
    definite = 'the bush'

class Water(Prop):
    indefinite = 'water'
    definite = 'water'
    def noteworthy(self, other_props):
        if self.__class__ == Water: return False
        return True

class Brook(Water):
    indefinite = 'a brook'
    definite = 'the brook'

class Stream(Water):
    indefinite = 'a stream'
    definite = 'the stream'

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
    @property
    def indefinite(self):
        if self.item[0] in 'aeiou':
            return 'an ' + self.item
        return 'a ' + self.item
    @property
    def definite(self):
        return 'the ' + self.item
