from copy import deepcopy
import regex
import editdistance
import utils

# ---------------------------------------------------------------------------- #
#                            Description of Outputs                            #
# ---------------------------------------------------------------------------- #
'''
    hsp:                    The desired Highest Standard Passed Label
    status:                 Whether the HSP Classification criteria was passed, failed, or algo is unsure
    type:                   The specific educational qualification which the submitted document represents
    score:                  The numeric score specific to the educational qualification
    remarks:                Additional Remarks
'''

# ---------------------------------------------------------------------------- #
#                          Analyze N-Level Certificate                         #
# ---------------------------------------------------------------------------- #

def nlvl(full_ocr_result):
    output = {
        'hsp': 'O-Level & Below',
        'status': '',
        'score': '',
        'type': '',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Find out whether this person is N(A) or N(T)
    type_pattern = r'normal\s*\((\w+)\)\s*level'
    type_search = regex.search(type_pattern, full_pdf_text)
    subtype = type_search.group(1)
    if subtype == 'technical':
        output['type'] = 'Singapore-Cambridge General Certificate of Education Normal (Technical) Level'
    elif subtype == 'academic':
        output['type'] = 'Singapore-Cambridge General Certificate of Education Normal (Academic) Level'

    # Find out whether this person mistakenly submitted the RESULT SLIP instead of the correct N-Level certificate
    result_slip_search = regex.search(r'(result\s*slip){e<=1}', full_pdf_text)
    if result_slip_search is None:
        # It is an N-Level certificate
        hsp_criteria_pattern_cert = r'(graded\s*6\s*or\sbetter\:\s*(\w+)){e<=3}'
        hsp_criteria_search_cert = regex.search(hsp_criteria_pattern_cert, full_pdf_text)
        if hsp_criteria_search_cert is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_cert = utils.word2num(hsp_criteria_search_cert.group(2))
            if num_pass_subjects_cert is None:
                # Couldn't detect
                output['status'] = 'unsure'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_cert >= 1:
                output['status'] = 'passed'
            else:
                output['status'] = 'failed' 
    else:
        # The person likely mistakenly submitted a result slip
        output['remarks'] += 'Result Slip was submitted instead of the proper N-Level certificate. '
        # Check using a separate method for the result slip
        hsp_criteria_pattern_slip = r'(graded\s*5\s*or\sbetter\:\s*(\d+)){e<=3}'
        hsp_criteria_search_slip = regex.search(hsp_criteria_pattern_slip, full_pdf_text)
        if hsp_criteria_search_slip is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_slip = utils.word2num(hsp_criteria_search_slip.group(2))
            if num_pass_subjects_slip is None:
                # Couldn't detect
                output['status'] = 'unsure'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_slip >= 1:
                output['status'] = 'passed'
            else:
                output['status'] = 'failed' 
    return output
        
# ---------------------------------------------------------------------------- #
#                          Analyze O-Level Certificate                         #
# ---------------------------------------------------------------------------- #

def olvl(full_ocr_result):
    output = {
        'hsp': 'O-Level & Below',
        'status': '',
        'score': '',
        'type': 'Singapore-Cambridge General Certificate of Education Ordinary Level',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Find out whether this person mistakenly submitted the RESULT SLIP instead of the correct O-Level certificate
    result_slip_search = regex.search(r'(result\s*slip){e<=1}', full_pdf_text)
    if result_slip_search is None:
        # It is an O-Level certificate
        hsp_criteria_pattern_cert = r'(graded\s*6\s*or\sbetter\:\s*(\w+)){e<=3}'
        hsp_criteria_search_cert = regex.search(hsp_criteria_pattern_cert, full_pdf_text)
        if hsp_criteria_search_cert is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_cert = utils.word2num(hsp_criteria_search_cert.group(2))
            if num_pass_subjects_cert is None:
                # Couldn't detect
                output['status'] = 'unsure'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_cert >= 1:
                output['status'] = 'passed'
            else:
                output['status'] = 'failed' 
    else:
        # The person likely mistakenly submitted a result slip
        output['remarks'] += 'Result Slip was submitted instead of the proper N-Level certificate. '
        # Check using a separate method for the result slip
        hsp_criteria_pattern_slip = r'(graded\s*6\s*or\sbetter\:\s*(\d+)){e<=3}'
        hsp_criteria_search_slip = regex.search(hsp_criteria_pattern_slip, full_pdf_text)
        if hsp_criteria_search_slip is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
        else:
            num_pass_subjects_slip = utils.word2num(hsp_criteria_search_slip.group(2))
            if num_pass_subjects_slip is None:
                # Couldn't detect
                output['status'] = 'unsure'
                output['remarks'] += 'Unable to detect if passed HSP Criteria, requires human intervention. '
            elif num_pass_subjects_slip >= 1:
                output['status'] = 'passed'
            else:
                output['status'] = 'failed' 
    return output

# ---------------------------------------------------------------------------- #
#                         Analyze NITEC / Higher NITEC                         #
# ---------------------------------------------------------------------------- #

def nitec(full_ocr_result, higher_nitec=False):
    output = {
        'hsp': 'Higher NITEC' if higher_nitec else 'NITEC',
        'status': '',
        'score': '',
        'type': 'Higher National ITE Certificate' if higher_nitec else 'National ITE Certificate',
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
    transcript_confirm_search_2 = regex.search(r'(examination\s*results){e<=2}', full_pdf_text)
    if transcript_confirm_search is None and transcript_confirm_search_2 is None:
        # This means the person didn't submit the transcript we wanted
        output['status'] = 'unsure'
        output['remarks'] = 'ITE Certificate/Some other document was submitted instead of the Academic Transcript. '
        return output

    # Extract GPA
    gpa_search = regex.search(r'(point\s*average\:\s*([\d\.]+)\s*result\:\s*awarded){e<=5}', full_pdf_text)
    if gpa_search is None:
        # Couldn't detect using GPA, try to detect using the award confirmation
        award_confirmation_search = regex.search(r'(awarded\s*the\s*higher\s*national\s*ite\s*certificate\s*in){e<=5}', full_pdf_text) if higher_nitec else regex.search(r'(awarded\s*the\s*\s*national\s*ite\s*certificate\s*in){e<=5}', full_pdf_text) 
        if award_confirmation_search is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] = 'Unable to detect GPA or NITEC Confirmation in transcript, requires human intervention. Check that the full transcript was provided. '
        else:
            # There was an award confirmation
            output['status'] = 'passed'
            output['remarks'] = 'Unable to detect GPA in transcript, awarded passed based on NITEC Confirmation. '
    else:
        gpa = float(gpa_search.group(2))
        output['score'] = gpa
        if gpa >= 1:
            output['status'] = 'passed'
        else:
            output['status'] = 'failed'
    return output

# ---------------------------------------------------------------------------- #
#                                 Analzye Poly                                 #
# ---------------------------------------------------------------------------- #

def poly(full_ocr_result, poly):
    output = {
        'hsp': 'Poly Diploma',
        'status': '',
        'score': '',
        'type': '',
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
    transcript_confirm_search_2 = regex.search(r'(examination\s*results){e<=2}', full_pdf_text)
    if transcript_confirm_search is None and transcript_confirm_search_2 is None:
        # This means the person didn't submit the transcript we wanted
        output['status'] = 'unsure'
        output['type'] = f'{poly.upper()} Diploma'
        output['remarks'] = 'Poly Certificate/Some other document was submitted instead of the Academic Transcript. '
        return output

    # If the person submitted a SP transcript, check that it is a PACE transcript
    # PACE = Professional & Adult Continuing Education Academy
    if poly == 'sp':
        sp_pace_search = regex.search(r'(professional\s*\&adult\s*continuing\s*education){e<=3}', full_pdf_text)
        if sp_pace_search is not None:
            # it is a SP PACE transcript
            output['type'] = 'SP PACE Transcript'
            output['remarks'] = 'Applicant submitted a SP Professional & Adult Continuing Education Transcript. '
            poly = 'sp_pace'
    
    output['type'] = f'{poly.upper()} Diploma'

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
            output['status'] = 'unsure'
            output['remarks'] = 'Unable to detect GPA or Diploma Confirmation in transcript, requires human intervention. Check that the full transcript was provided. '
        else:
            # There is an award confirmation
            output['status'] = 'passed'
            output['remarks'] = 'Unable to detect GPA, awarded passed based on Diploma Confirmation. '
    else:
        gpa = float(gpa_search.group(2))
        output['score'] = gpa
        if gpa >= 1:
            output['status'] = 'passed'
        else:
            output['status'] = 'failed'
    return output
    
# ---------------------------------------------------------------------------- #
#                          Technical Engineer Diploma                          #
# ---------------------------------------------------------------------------- #

def ted(full_ocr_result):
    output = {
        'hsp': 'Poly Diploma',
        'status': '',
        'score': '',
        'type': 'Technical Engineer Diploma',
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
    transcript_confirm_search_2 = regex.search(r'(examination\s*results){e<=2}', full_pdf_text)
    if transcript_confirm_search is None and transcript_confirm_search_2 is None:
        # This means the person didn't submit the transcript we wanted
        output['status'] = 'unsure'
        output['remarks'] = 'TED Certificate/Some other document was submitted instead of the Academic Transcript. '
        return output

    # Extract GPA
    gpa_search = regex.search(r'(point\s*average\:\s*([\d\.]+)\s*result\:\s*awarded){e<=5}', full_pdf_text)
    if gpa_search is None:
        # Couldn't detect using GPA, try to detect using the award confirmation
        award_confirmation_search = regex.search(r'(awarded\s*the\s*technical\s*engineer\s*diploma\s*in){e<=3}', full_pdf_text)
        if award_confirmation_search is None:
            # Couldn't detect
            output['status'] = 'unsure'
            output['remarks'] = 'Unable to detect GPA or TED Confirmation in transcript, requires human intervention. Check that the full transcript was provided. '
        else:
            # There is an award confirmation
            output['status'] = 'passed'
            output['remarks'] = 'Unable to detect GPA, awarded passed based on TED Confirmation. '
    else:
        gpa = float(gpa_search.group(2))
        output['score'] = gpa
        if gpa >= 1:
            output['status'] = 'passed'
        else:
            output['status'] = 'failed'
    return output

# ---------------------------------------------------------------------------- #
#                                Analyze A-Level                               #
# ---------------------------------------------------------------------------- #

def alvl(full_ocr_result):
    output = {
        'hsp': '', # Full A-Level or Partial A-Level
        'status': 'passed', # Always passed for IB Case
        'score': '',
        'type': 'Singapore-Cambridge General Certificate of Education Advanced Level',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Identify if the certificate or the result slip was submitted
    result_slip_search = regex.search(r'(result\s*slip){e<=1}', full_pdf_text)
    if result_slip_search is None:
        # The person submitted the correct A-Level certificate
        main_subj_search_regex = r'(level\s*grade\s*authority\s*(.*)\s*director\-general){e<=5}'
    else:
        # The person submitted the A-Level Results Slip
        output['remarks'] += 'Result Slip was submitted instead of the proper A-Level certificate. '
        main_subj_search_regex = r'(level\s*grade\s*authority\s*(.*)\s*serial){e<=5}'

    # Perform extraction of subjects from main certificate
    main_subj_search = regex.search(main_subj_search_regex, full_pdf_text)
    main_subj_search_2 = regex.search(r'(general\s*paper\s*.*dir){e<=2}', full_pdf_text)
    main_subj_search_3 = regex.search(r'(knowledge\s*and\s*.*dir){e<=2}', full_pdf_text)
    if main_subj_search is None and main_subj_search_2 is None and main_subj_search_3 is None:
        # Very hard to extract subjects without mistakes, revert to human intervention
        output['hsp'] = 'Partial A-Level'
        output['status'] = 'unsure'
        output['remarks'] = 'Unable to extract A Level subjects. Human intervention required. '
        return output
    else:
        if main_subj_search is not None:
            working_result = main_subj_search.group(2)
        elif main_subj_search_2 is not None:
            working_result = main_subj_search_2.group(1)
        else:
            working_result = main_subj_search_3.group(1)
        main_subj_string = regex.sub(r'\d\d+', '', working_result)
        subjects = []
        subject_template = {'name':'','level':'','grade':''}
        for i in range(6):
            subjects.append(deepcopy(subject_template))
        subject_counters = {
            'name': 0,
            'level': 0,
            'grade': 0
        }
        subject_list = utils.alvl_subject_list()
        for token in main_subj_string.split(' '):
            if editdistance.eval(token, 'cambridge') <= 2:
                # Current token is the Cambridge separator
                continue
            
            if len(token) == 1 and token in 'abcdesu':
                # Current token represents a H1/H2 grade
                subjects[subject_counters['grade']]['grade'] = token
                subject_counters['grade'] += 1
                continue

            h_search = regex.search(r'h(\d)', token)
            if h_search is not None:
                # Current token represents a HX Level
                subjects[subject_counters['level']]['level'] = int(h_search.group(1))
                subject_counters['level'] += 1
                continue
            
            if editdistance.eval(token, 'dist') <= 1:
                subjects[subject_counters['grade']]['grade'] = 'dist'
                subject_counters['grade'] += 1
                continue
            if editdistance.eval(token, 'merit') <= 1:
                subjects[subject_counters['grade']]['grade'] = 'merit'
                subject_counters['grade'] += 1
                continue
            if editdistance.eval(token, 'pass') <= 1:
                subjects[subject_counters['grade']]['grade'] = 'pass'
                subject_counters['grade'] += 1
                continue

            match = utils.match_in_subject_list(subject_list, token)
            if match is not None:
                if subject_counters['name'] > 5:
                    continue
                subjects[subject_counters['name']]['name'] = match
                subject_counters['name'] += 1
                subject_list.remove(match) 
                continue

    # If the three counts do not match, it means the algo failed to detect all the grades and the results must be discarded
    if subject_counters['name'] != subject_counters['level'] or subject_counters['name'] != subject_counters['grade'] or subject_counters['level'] != subject_counters['grade']:
        output['hsp'] = 'Partial A-Level'
        output['status'] = 'unsure'
        output['remarks'] = 'Failed to extract all A Level subjects. Human intervention required. '
        return output

    # TODO: Extraction of PW in the future. Assume PW cert is appended to main cert.
    # For now, we will assume Proj Work is A.
    if subjects[-1]['name'] != '':
        subjects.append({'name': 'project work', 'level': 1, 'grade': 'a'})
    else:
        subjects[-1] = {'name': 'project work', 'level': 1, 'grade': 'a'}

    # Direct implementation of flowchart logic
    num_h1 = sum([1 for subj in subjects if subj['level'] == 1]) + 1 # Due to PW assumption
    num_h2 = sum([1 for subj in subjects if subj['level'] == 2])
    took_gp = 'general paper' in [subj['name'] for subj in subjects]

    if took_gp:
        for subj in subjects:
            if subj['name'] == 'general paper':
                passed_gp = subj['grade'] in 'abcd'
        if passed_gp:
            if num_h1 >= 2:
                if num_h2 >= 2:
                    output['hsp'] = 'Full A-Level'
                    output['status'] = 'passed'
                elif num_h2 == 1:
                    output['hsp'] = 'Partial A-Level'
                    output['status'] = 'passed'
                else: # num_h2 is 0
                    output['hsp'] = 'Partial A-Level'
                    output['status'] = 'failed'
            else: # num_h1 is 0 or 1
                if num_h2 >= 1:
                    output['hsp'] = 'Partial A-Level'
                    output['status'] = 'passed'
                else:
                    output['hsp'] = 'Partial A-Level'
                    output['status'] = 'failed'
        else: # fail GP
            if num_h2 >= 1:
                output['hsp'] = 'Partial A-Level'
                output['status'] = 'passed'
            else: # num_h2 is 0
                output['hsp'] = 'Partial A-Level'
                output['status'] = 'failed'
    elif 'knowledge and inquiry' in [subj['name'] for subj in subjects]: 
        # might have taken KI, we double confirm
        for subj in subjects:
            if subj['name'] == 'knowledge and inquiry':
                passed_ki = subj['grade'] in 'abcd'
        if passed_ki:
            if num_h2 >= 2:
                output['hsp'] = 'Full A-Level'
                output['hsp'] = 'passed'
            else: # num_h2 is only 1 as it is KI
                output['hsp'] = 'Partial A-Level'
                output['hsp'] = 'passed'
        else: # failed KI
            if num_h2 == 1:
                output['hsp'] = 'Partial A-Level'
                output['hsp'] = 'passed'
            elif num_h2 == 0:
                output['hsp'] = 'Partial A-Level'
                output['hsp'] = 'failed'
    output['score'] = utils.calculate_rank_points(subjects)
    return output
# ---------------------------------------------------------------------------- #
#                      Analyze International Baccalaureate                     #
# ---------------------------------------------------------------------------- #

def ib(full_ocr_result):
    output = {
        'hsp': '', # Full A-Level or Partial A-Level
        'status': 'passed', # Always passed for IB Case
        'score': '',
        'type': 'International Baccalaureate Diploma',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Attempt extraction of IB Points
    ib_points_regex_1 = r'(satisfied\.\s*total\s*(\d+)){e<=4}'
    ib_points_regex_2 = r'(total\s*points\s*\:\s*(\d+)\s*result){e<=4}'
    ib_points_search_1 = regex.search(ib_points_regex_1, full_pdf_text)
    if ib_points_search_1 is None:
        # First search failed, try the second one. The transcript may be a different type
        ib_points_search_2 = regex.search(ib_points_regex_2, full_pdf_text)
        if ib_points_search_2 is None:
            # Both searches failed
            output['hsp'] = 'Partial A-Level'
            output['status'] = 'unsure'
            output['remarks'] = 'Unable to detect IB Points. Human intervention is required. '
            return output
        else:
            # Found IB Points through 2nd method
            ib_points = int(ib_points_search_2.group(2))
    else:
        # Found IB Points through 1st method
        ib_points = int(ib_points_search_1.group(2))
    output['score'] = ib_points
    if ib_points >= 24:
        output['hsp'] = 'Full A-Level'
    else:
        output['hsp'] = 'Partial A-Level'
    return output

# ---------------------------------------------------------------------------- #
#                           Analyze NUS High Diploma                           #
# ---------------------------------------------------------------------------- #

def nush(full_ocr_result):
    output = {
        'hsp': '', # Full A-Level or Partial A-Level
        'status': 'passed', # Always passed for IB Case
        'score': '',
        'type': 'NUS High Diploma',
        'remarks': ''
    }

    # Get full text of the entire pdf
    texts = []
    for page_result in full_ocr_result:
        texts.append([line[1][0] for line in page_result])
    merged_texts = [' '.join(x).lower() for x in texts]
    full_pdf_text = ' '.join(merged_texts)

    # Attempt extraction of CAP
    cap_search = regex.search(r'(graduation\s*cap\s*with\s*mother\s*tongue\s*\:\s*([\d\.]+)){e<=4}', full_pdf_text)
    if cap_search is None:
        # Failed to find CAP
        output['hsp'] = 'Partial A-Level'
        output['status'] = 'unsure'
        output['remarks'] = 'Unable to find Graduation CAP. Human intervention is required. '
    else:
        # Found CAP
        cap = float(cap_search.group(2))
        if cap > 10.0:
            # The OCR likely didn't pick up the decimal point
            cap /= 10.0
        output['score'] = cap
        if cap >= 2.5:
            output['hsp'] = 'Full A-Level'
        else:
            output['hsp'] = 'Partial A-Level'
    return output