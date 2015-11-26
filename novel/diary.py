import sys
import random
import logging
import hashlib
try:
    from PIL import Image
except ImportError:
    print("run `pip install Pillow` to enable diary icon generation",
        file=sys.stderr)
    Image = None

class Diary:
    def __init__(self, person):
        self.person = person
        self.events = []
        self._punct = ['. ', '. ', '; ', '; ', ', ', ', ', '! ']
        self.time = None # most recent update time
        self.icon = None

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
        start = True
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
                if end or start:
                    start = False
                    yield clause[0].upper() + clause[1:] # TODO this is bad
                else:
                    yield clause
        if i != -1:
            yield random.choice(['.', '!'])

        self.events[:] = []

    def write_icon(self):
        """Generate and write out the icon to a file."""
        hash_ = hashlib.sha256(self.person.name.encode('utf-8')).digest()
        image = Image.new('L', (5, 5)) # Alt: 'RGBA' for colour
        pixels = image.load()
        for i in range(5):
            for j in range(5):
                byte = hash_[i * 5 + j]
                #r = ((byte & 0xc0) >> 6) * 85
                #g = ((byte & 0x30) >> 4) * 85
                #b = ((byte & 0x0c) >> 2) * 85
                #a = ((byte & 0x03) >> 0) * 85
                pixels[i, j] = byte
        image = image.resize((100, 100))
        image.save("output/icon-%s.png" % (self.person.seq_id,))
        self.icon = image

    def print(self):
        if Image and not self.icon:
            self.write_icon()
        if self.icon:
            print()
            print("<img align='left' alt='%s' src='icon-%s.png'>" % (
                self.person.name, self.person.seq_id))
            print()
        print(self.person.name)
        print('-' * len(self.person.name))
        print()
        for clause in self.write():
            print(clause, end='')
        print()
        print()
