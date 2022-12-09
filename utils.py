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
'''.split('\n')[1:]

def alvl_subject_list():
    return deepcopy(A_LVL_SUBJECTS)

def match_in_subject_list(subj_list, candidate):
    if candidate == '':
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