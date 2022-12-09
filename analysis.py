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
    score:                  The numeric score specific to the educational qualification
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
        'score': '',
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
        'score': '',
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

# ---------------------------------------------------------------------------- #
#                         Analyze NITEC / Higher NITEC                         #
# ---------------------------------------------------------------------------- #

def nitec(full_ocr_result, higher_nitec=False):
    output = {
        'hsp': 'Higher NITEC' if higher_nitec else 'NITEC',
        'criteria_passed': '',
        'specific_doc_class': '',
        'score': '',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Ensure that the person submitted the transcript and not some other document
    transcript_confirm_search = regex.search(r'(transcript){e<=2}', full_pdf_text)
    if transcript_confirm_search is None:
        # This means the person didn't submit the transcript we wanted
        output['criteria_passed'] = 'UNSURE'
        output['specific_doc_class'] = 'Non-Transcript'
        output['remarks'] = 'ITE Certificate/Some other document was submitted instead of the Academic Transcript. '
        return output
    output['specific_doc_class'] = 'Transcript'

    # Extract GPA
    gpa_search = regex.search(r'(point\s*average\:\s*([\d\.]+)\s*result\:\s*awarded\s*the\s*national){e<=5}', full_pdf_text)
    if gpa_search is None:
        # Couldn't detect
        output['criteria_passed'] = 'UNSURE'
        output['remarks'] = 'Unable to detect GPA in transcript, requires human intervention. Check that the full transcript was provided. '
    else:
        gpa = float(gpa_search.group(2))
        output['score'] = gpa
        if gpa >= 1:
            output['criteria_passed'] = 'PASSED'
        else:
            output['criteria_passed'] = 'FAILED'
    return output

# ---------------------------------------------------------------------------- #
#                                 Analzye Poly                                 #
# ---------------------------------------------------------------------------- #

def poly(full_ocr_result, poly):
    output = {
        'hsp': 'Poly Diploma',
        'criteria_passed': '',
        'specific_doc_class': '',
        'score': '',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Ensure that the person submitted the transcript and not some other document
    transcript_confirm_search = regex.search(r'(transcript){e<=2}', full_pdf_text)
    if transcript_confirm_search is None:
        # This means the person didn't submit the transcript we wanted
        output['criteria_passed'] = 'UNSURE'
        output['specific_doc_class'] = f'{poly.upper()} Non-Transcript'
        output['remarks'] = 'Poly Certificate/Some other document was submitted instead of the Academic Transcript. '
        return output
    output['specific_doc_class'] = f'{poly.upper()} Transcript'

    # If the person submitted a SP transcript, check that it is a PACE transcript
    # PACE = Professional & Adult Continuing Education Academy
    if poly == 'sp':
        sp_pace_search = regex.search(r'(professional\s*\&adult\s*continuing\s*education){e<=3}', full_pdf_text)
        if sp_pace_search is not None:
            # it is a SP PACE transcript
            output['specific_doc_class'] = 'SP PACE Transcript'
            output['remarks'] = 'Applicant submitted a SP Professional & Adult Continuing Education Transcript. '
            poly = 'sp_pace'
    
    # Extract GPA
    poly_gpa_regexes = {
        'np': r'(graduating\s*gpa\s*\:\s*([\d\.]+)){e<=3}',
        'nyp': r'(grade\s*point\s*average\s*\:\s*([\d\.]+)){e<=4}',
        'rp': r'(point\s*average\s*\(\s*gpa\s*\)\s*\:\s*([\d\.]+)\s*\/4\.00\s*awarded\s*the\s*diploma){e<=5}',
        'sp': r'(diploma\s*awarded\s*semester\s*gpa\s*\:\s*[\d\.]+\s*cumulative\s*gpa\s*\:\s*([\d\.]+)){e<=5}',
        'sp_pace': r'(cumulative\s*gpa\s*\:\s*([\d\.]+)\s*completed.*end\s*of\s*academic\s*transcript){e<=4}',
        'tp': r'(cumulative\s*grade\s*point\s*average\s*score\s*\:\s*([\d\.]+)){e<=4}',
    }
    poly_award_confirm_regexes = {
        'np': r'(the\s*student\s*has\s*completed\s*the){e<=2}',
        'nyp': r'(successfully\s*completed\s*all\s*course\s*requirements){e<=5}',
        'rp': r'(awarded\s*the\s*diploma\s*in){e<=2}',
        'sp': r'(diploma\s*awarded){e<=2}',
        'sp_pace': r'(completed.*end\s*of\s*academic\s*transcript){e<=3}',
        'tp': r'(awarded\s*the\s*diploma\s*in){e<=2}',
    }

    gpa_search = regex.search(poly_gpa_regexes[poly], full_pdf_text)
    if gpa_search is None:
        # Couldn't detect using GPA, try to detect using the award confirmation
        award_confirmation_search = regex.search(poly_award_confirm_regexes[poly], full_pdf_text)
        if award_confirmation_search is None:
            # Also cannot detect the award confirmation
            output['criteria_passed'] = 'UNSURE'
            output['remarks'] = 'Unable to detect GPA or Diploma Confirmation in transcript, requires human intervention. Check that the full transcript was provided. '
        else:
            # There is an award confirmation
            output['criteria_passed'] = 'PASSED'
            output['remarks'] = 'Unable to detect GPA, awarded PASSED basde on Diploma Confirmation. '
    else:
        gpa = float(gpa_search.group(2))
        output['score'] = gpa
        if gpa >= 1:
            output['criteria_passed'] = 'PASSED'
        else:
            output['criteria_passed'] = 'FAILED'
    return output
    