import numpy as np
import regex
import editdistance

# ---------------------------------------------------------------------------- #
#                            Description of Outputs                            #
# ---------------------------------------------------------------------------- #
'''
    hsp:                    The desired Highest Standard Passed Label
    criteria_passed:        Whether the HSP Classification criteria was PASSED or FAILED
    specific_doc_class:     The specific educational qualification which the submitted document represents
    remarks:                Additional Remarks
'''

def word2num(word):
    if regex.search(r'[a-z]+', word) is None:
        # there are no letters in there
        return None
    indices = np.full((11), np.inf)
    for i, reference in enumerate(['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']):
        indices[i] = editdistance.eval(word, reference)
    return np.argmin(indices)

# ---------------------------------------------------------------------------- #
#                          Analyze N-Level Certificate                         #
# ---------------------------------------------------------------------------- #

def nlvl(full_ocr_result, first_page_merged_text):
    output = {
        'hsp': 'O-Level & Below',
        'criteria_passed': '',
        'specific_doc_class': '',
        'remarks': ''
    }

    # Find out whether this person is N(A) or N(T)
    specific_doc_class_pattern = r'normal\s*\((\w+)\)\s*level'
    specific_doc_class_search = regex.search(specific_doc_class_pattern, first_page_merged_text)
    subtype = specific_doc_class_search.group(1)
    if subtype == 'technical':
        output['specific_doc_class'] = 'Normal (Technical)'
    elif subtype == 'academic':
        output['specific_doc_class'] = 'Normal (Academic)'

    # Find out whether this person mistakenly submitted the RESULT SLIP instead of the correct N-Level certificate
    result_slip_search = regex.search(r'(result\s*slip){e<=1}', first_page_merged_text)
    if result_slip_search is None:
        # It is an N-Level certificate
        hsp_criteria_pattern_cert = r'(graded\s*6\s*or\sbetter\:\s*(\w+)){e<=3}'
        hsp_criteria_search_cert = regex.search(hsp_criteria_pattern_cert, first_page_merged_text)
        if hsp_criteria_search_cert is None:
            # Couldn't detect
            output['criteria_passed'] = 'UNSURE'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_cert = word2num(hsp_criteria_search_cert.group(2))
            if num_pass_subjects_cert is None:
                # Couldn't detect
                output['criteria_passed'] = 'UNSURE'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_cert >= 1:
                output['criteria_passed'] = 'PASSED'
            else:
                output['criteria_passed'] = 'FAILED' 
    else:
        # The person likely mistakenly submitted a result slip
        output['remarks'] += 'Result Slip was submitted instead of the proper N-Level certificate. '
        # Check using a separate method for the result slip
        hsp_criteria_pattern_slip = r'(graded\s*5\s*or\sbetter\:\s*(\d+)){e<=3}'
        hsp_criteria_search_slip = regex.search(hsp_criteria_pattern_slip, first_page_merged_text)
        if hsp_criteria_search_slip is None:
            # Couldn't detect
            output['criteria_passed'] = 'UNSURE'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_slip = word2num(hsp_criteria_search_slip.group(2))
            if num_pass_subjects_slip is None:
                # Couldn't detect
                output['criteria_passed'] = 'UNSURE'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_slip >= 1:
                output['criteria_passed'] = 'PASSED'
            else:
                output['criteria_passed'] = 'FAILED' 
    return output
        
# ---------------------------------------------------------------------------- #
#                          Analyze O-Level Certificate                         #
# ---------------------------------------------------------------------------- #

def olvl(full_ocr_result, first_page_merged_text):
    output = {
        'hsp': 'O-Level & Below',
        'criteria_passed': '',
        'specific_doc_class': 'Ordinary Level',
        'remarks': ''
    }

    # Find out whether this person mistakenly submitted the RESULT SLIP instead of the correct O-Level certificate
    result_slip_search = regex.search(r'(result\s*slip){e<=1}', first_page_merged_text)
    if result_slip_search is None:
        # It is an O-Level certificate
        hsp_criteria_pattern_cert = r'(graded\s*6\s*or\sbetter\:\s*(\w+)){e<=3}'
        hsp_criteria_search_cert = regex.search(hsp_criteria_pattern_cert, first_page_merged_text)
        if hsp_criteria_search_cert is None:
            # Couldn't detect
            output['criteria_passed'] = 'UNSURE'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_cert = word2num(hsp_criteria_search_cert.group(2))
            if num_pass_subjects_cert is None:
                # Couldn't detect
                output['criteria_passed'] = 'UNSURE'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_cert >= 1:
                output['criteria_passed'] = 'PASSED'
            else:
                output['criteria_passed'] = 'FAILED' 
    else:
        # The person likely mistakenly submitted a result slip
        output['remarks'] += 'Result Slip was submitted instead of the proper N-Level certificate. '
        # Check using a separate method for the result slip
        hsp_criteria_pattern_slip = r'(graded\s*6\s*or\sbetter\:\s*(\d+)){e<=3}'
        hsp_criteria_search_slip = regex.search(hsp_criteria_pattern_slip, first_page_merged_text)
        if hsp_criteria_search_slip is None:
            # Couldn't detect
            output['criteria_passed'] = 'UNSURE'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_slip = word2num(hsp_criteria_search_slip.group(2))
            if num_pass_subjects_slip is None:
                # Couldn't detect
                output['criteria_passed'] = 'UNSURE'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_slip >= 1:
                output['criteria_passed'] = 'PASSED'
            else:
                output['criteria_passed'] = 'FAILED' 
    return output