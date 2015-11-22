import sys
import random
import inspect

from . import props

class Terrain:
    props_available = []
    # TODO - have themed adj groups, eg nice, horrible, creepy, friendly.
    #        to avoid contradictory adjectives being chosen
    adjectives_available = []
    def __init__(self):
        self.props = []
        for prop_cls, likelihood in self.props_available:
            if random.random() < likelihood:
                self.props.append(prop_cls())
        self.adjectives = []
        for adj, likelihood in self.adjectives_available:
            if random.random() < likelihood:
                self.adjectives.append(adj)
    def __str__(self):
        return self.__class__.__name__.lower()

class Meadow(Terrain):
    symbol = "  " # boring ol' meadow
    props_available = [
        (props.Bush, 0.8),
        (props.Brook, 0.1),
        (props.Stream, 0.1),
        (props.Landmark, 0.5)]
    adjectives_available = [
        ('beautiful', 0.1),
        ('lush', 0.1),
        ('desolate', 0.1),
        ('grassy', 0.1),
        ('barren', 0.1),
        ('wetland', 0.1),
        ('burnt', 0.1),
        ('hilly', 0.1),
        ('muddy', 0.1),
        ('rolling', 0.1)]

class Lake(Terrain):
    symbol = "~~" # waves?
    props_available = [
        (props.Water, 1),
        (props.Landmark, 0.1)]
    adjectives_available = [
        ('beautiful', 0.2),
        ('pretty', 0.2),
        ('boggy', 0.2),
        ('silty', 0.2),
        ('expansive', 0.2)]

    def __str__(self):
        """As far as the characters are concerned, this is the shoreline"""
        return 'beach'


class Forest(Terrain):
    symbol = '||' # trees?
    props_available = [(props.Tree, 0.9)] * 35 + [
        (props.Stream, 0.2),
        (props.Landmark, 0.3)]
    adjectives_available = [
        ('thick', 0.1),
        ('coniferous', 0.1),
        ('deciduous', 0.1),
        ('dark', 0.1),
        ('shadowy', 0.1),
        ('sun-lit', 0.1),
        ('sparse', 0.1),
        ('silent', 0.1),
        ('unwelcoming', 0.1),
        ('dappled', 0.1)]

terrains = [cls
    for name, cls
    in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(cls) and issubclass(cls, Terrain) and cls != Terrain]

