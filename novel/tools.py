class Tool:
    def __init__(self, *, adjectives=None):
        self.adjectives = []
        if adjectives:
            self.adjectives = adjectives[:]
        self.health = 1.0

class Weapon(Tool):
    def __init__(self, *, power=0.05, **kwargs):
        super().__init__(**kwargs)
        self.power = power

class Fist(Weapon):
    name = 'fist'
    verbs = ['punch', 'pummel', 'punch', 'swipe']
    targets = ['face', 'arm', 'chest', 'stomach', 'neck', 'ear']

class Foot(Weapon):
    name = 'foot'
    verbs = ['kick', 'tackle', 'swipe']
    targets = ['chest', 'shin', 'leg', 'groin']

