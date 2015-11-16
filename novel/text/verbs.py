import os
import json
import logging

data = json.load(open(os.path.join(os.path.dirname(__file__), 'verbs.json')))

def find(word):
    for datum in data['verbs']:
        for tense, form in datum.items():
            if form == word:
                return datum
    raise RuntimeError('Unknown verb: %s' % word)

def past(word):
    """Simple past tense"""
    tenses = find(word)
    return tenses['past']

def present_1s(word):
    """Simple present, 1st person singular"""
    tenses = find(word)
    try:
        return tenses['present_1s']
    except KeyError:
        return tenses['present']

def present_3s(word):
    """Simle present, 3rd person singular"""
    tenses = find(word)
    return tenses['present'] + 's'

def conjugate(word, time, person, number):
    """
    time -- 'past', 'present'
    person -- 1, 2, 3
    number -- 'singular', 'plural'
    """
    if time == 'past':
        return past(word)
    elif time == 'present':
        return globals().get('present%d%s' % (person, number[0]))
    return NotImplementedError()

