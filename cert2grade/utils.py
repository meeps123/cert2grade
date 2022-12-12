import regex
import editdistance
import numpy as np
from copy import deepcopy

A_LVL_SUBJECTS = '''
china studies in english
general paper
geography
history
economics
bengali
gujarati
hindi
french
literature in english
german
japanese
panjabi
urdu
mathematics
physics
chemistry
biology
art
english language and linguistics 
theatre studies and drama
computing
spanish
management of business
principles of accounting
china studies in english
further mathematics
music
knowledge and inquiry
chemistry 
chinese language 
translation
china studies in chinese
chinese language and literature
malay language
malay language and literature
tamil language
tamil language and literature
project work
research
geopolitics: geographies of war & peace
molecular biology
semiconductor physics & devices
game theory
proteomics
essentials of modern physics
linear algebra
'''.split('\n')[1:]

def alvl_subject_list():
    return deepcopy(A_LVL_SUBJECTS)

GRADE_TO_H1RP = {
    'a': 10,
    'b': 8.75,
    'c': 7.5,
    'd': 6.25,
    'e': 5,
    's': 2.5,
    'u': 0
}

def calculate_rank_points(subjects):
    h1_subjs = [subj for subj in subjects if subj['level'] == 1]
    h1_subjs.sort(key=lambda x: x['grade'])
    h2_subjs = [subj for subj in subjects if subj['level'] == 2]
    h2_subjs.sort(key=lambda x: x['grade'])

    if len(h2_subjs) == 4: # 4H2 2H1 case, treat weakest H2 as a H1
        h2_subjs[-1]['level'] = 1
        h1_subjs.append(h2_subjs[-1]) # Move to h1 array
        del h2_subjs[-1]

    rp = 0.0

    for h1 in h1_subjs:
        rp += GRADE_TO_H1RP[h1['grade']]
    for h2 in h2_subjs:
        rp += GRADE_TO_H1RP[h2['grade']]*2
    
    return rp

def match_in_subject_list(subj_list, candidate):
    if candidate == '' or regex.search(r'\w', candidate) is None:
        return None
    for subj in subj_list:
        if regex.search(r'(' + candidate + r'){e<=1}', subj) is not None:
            return subj
    return None

def word2num(word):
    if regex.search(r'[a-z]+', word) is None:
        # there are no letters in there
        return None
    indices = np.full((11), np.inf)
    for i, reference in enumerate(['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']):
        indices[i] = editdistance.eval(word, reference)
    return np.argmin(indices)

