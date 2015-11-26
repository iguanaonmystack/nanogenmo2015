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

def past_1s(word):
    """Simple past tense, 1st person singular"""
    tenses = find(word)
    try:
        return tenses['past_1s']
    except KeyError:
        return tenses['past']

def past_2s(word):
    """Simple past tense, 2nd person singular"""
    tenses = find(word)
    try:
        return tenses['past_2s']
    except KeyError:
        return tenses['past']

def past_3s(word):
    """Simple past tense, 3rd person singular"""
    tenses = find(word)
    try:
        return tenses['past_3s']
    except KeyError:
        return tenses['past']

def past_1p(word):
    """Simple past tense, 1st person plural"""
    tenses = find(word)
    try:
        return tenses['past_1p']
    except KeyError:
        return tenses['past']

def past_2p(word):
    """Simple past tense, 2nd person plural"""
    tenses = find(word)
    try:
        return tenses['past_2p']
    except KeyError:
        return tenses['past']

def past_3p(word):
    """Simple past tense, 3rd person plural"""
    tenses = find(word)
    try:
        return tenses['past_3p']
    except KeyError:
        return tenses['past']

def present_1s(word):
    """Simple present, 1st person singular"""
    tenses = find(word)
    try:
        return tenses['present_1s']
    except KeyError:
        return tenses['present']

def present_3p(word):
    """Simle present, 3rd person plural"""
    tenses = find(word)
    try:
        return tenses['present_3p']
    except KeyError:
        return tenses['present']

def present_3s(word):
    """Simle present, 3rd person singular"""
    tenses = find(word)
    try:
        return tenses['present_3s']
    except KeyError:
        return tenses['present'] + 's'

def conjugate(word, time, person, number):
    """
    time -- 'past', 'present'
    person -- 1, 2, 3
    number -- 'singular', 'plural'
    """
    fname = '%s_%d%s' % (time, person, number[0])
    try:
        return globals()[fname](word)
    except KeyError:
        raise NotImplementedError(fname)

