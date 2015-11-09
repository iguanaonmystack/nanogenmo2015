import operator
import random

class World(list):
    def __init__(self, x, y):
        self.sizex = x
        self.sizey = y

    @classmethod
    def from_random(cls, x, y):
        self = cls(x, y)
        for i in range(x):
            row = []
            self.append(row)
            for j in range(y):
                tile = Tile.from_random(i, j)
                row.append(tile)
                if j:
                    tile.west = self[i][j - 1]
                    self[i][j - 1].east = tile
                if i:
                    tile.south = self[i - 1][j]
                    self[i - 1][j].north = tile
        return self
    
    def __str__(self):
        s = []
        for x in reversed(range(self.sizex)):
            for y in range(self.sizey):
                s.append("%s | " % (self[x][y]))
            s.append('\n')
        return ''.join(s)


class Tile:
    terrains = [
        'river',
        'forest',
        'meadow',
    ]

    def __init__(self, posx, posy, terrain):
        self.terrain = terrain
        self.posx = posx
        self.posy = posy
        self.west = None
        self.east = None
        self.north = None
        self.south = None
        class PeopleSet(set):
            def __str__(self):
                return ', '.join(str(p) for p in self)
            def random(self, person, k):
                return random.sample(
                    [p for p in sorted(self) if p is not person], k)
        self.people = PeopleSet()

    @classmethod
    def from_random(cls, posx, posy):
        terrain = random.choice(cls.terrains)
        return cls(posx, posy, terrain)
    
    def __str__(self):
        return "%06s %2d" % (self.terrain, len(self.people))

    def __repr__(self):
        return "<Tile terrain=%r people=%r>" % (self.terrain, self.people)

    @property
    def neighbours(self):
        d = {}
        for direction in ('north', 'east', 'south', 'west'):
            if getattr(self, direction) is not None:
                d[direction] = getattr(self, direction)
        return d

    
    def path_to(self, target_terrain):
        visited_nodes = set()
        distances = {}
        parents = {}
        dest = _find(self, visited_nodes, distances, parents,
            target=target_terrain)
        if dest is not None:
            path = [(dest, '')]
            while path[0][0] != self:
                path = [parents[path[0][0]]] + path
            return path
        return None

    def recursive_update(self, action):
        visited_nodes = set()
        distances = {}
        parents = {}
        _find(self, visited_nodes, distances, parents,
            target=None, action=action)

def _find(current, visited_nodes, distances, parents, target=None, action=None):
    # Dijkstra's algorithm.
    if current.terrain == target:
        return current
    for direction, neighbour in current.neighbours.items():
        if neighbour not in visited_nodes:
            dist = distances.setdefault(current, 0) + 1
            if neighbour in distances:
                if dist < distances[neighbour]:
                    distances[neighbour] = dist
                    parents[neighbour] = current, direction
            else:
                distances[neighbour] = dist
                parents[neighbour] = current, direction
    if action:
        action(current)
    visited_nodes.add(current)
    unvisited_distances = [
        (k, v) for k, v in distances.items() if k not in visited_nodes]
    if unvisited_distances:
        sorted_distances = sorted(
            unvisited_distances,
            key=operator.itemgetter(1))
        nearest_unvisited, dist = sorted_distances[0]
        return _find(nearest_unvisited, visited_nodes, distances, parents,
            target=target, action=action)
    else:
        # no unvisted nodes, unable to find target
        return None


def opposite_direction(direction):
    d = {'north': 'south',
        'east': 'west',
        'south': 'north',
        'west': 'east'}
    return d[direction]

