import os
import regex
import analysis
from paddleocr import PaddleOCR

# ---------------------------------------------------------------------------- #
#                               Global variables                               #
# ---------------------------------------------------------------------------- #

GLOBAL_INPUT_DIR = 'data/input/'
GLOBAL_OCR = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

input_path = os.path.join(GLOBAL_INPUT_DIR, os.listdir(GLOBAL_INPUT_DIR)[0])

def churn(input_file):
    # Reject input file if it is not a PDF
    if os.path.splitext(input_file)[-1] != '.pdf':
        raise Exception('Input file is not a PDF.')
    
    # OCR the entire PDF
    full_ocr_result = GLOBAL_OCR.ocr(input_file, cls=True)

    # Consider the first page of the PDF to classify the general type of document.
    # The general classification will be used to do a type-specific analysis which will give the desired output.
    first_page_texts = [line[1][0] for line in full_ocr_result[0]]
    first_page_merged_text = ' '.join(first_page_texts).lower()
    category_counts = {}
    categories = {
        'nlvl' : r'normal\s*\(\w+\)\s*level', # for n-level
        'olvl' : r'ordinary\s*level', # for o-level
        'ite' : r'national\s*ite\s*certificate\sin', # for NITEC or Higher NTIEC
        'poly' : r'polytechnic', # for poly
        'ted' : r'technical\s*engineer\s*diploma', # for TED
        'alvl' : r'advanced\s*level', # for a-level
        'ib' : r'baccalaureate', # for IB
        'nush' : r'nus\s*high' # for NUS High
    }
    for category in categories:
        pattern = '(' + categories[category] + '){e<=1}'
        category_counts[category] = len(regex.findall(pattern, first_page_merged_text))
    max_count_category = max(category_counts, key=category_counts.get)
    if max_count_category == 'psle':
        return analysis.psle(full_ocr_result)
    elif max_count_category == 'nlvl':
        return analysis.nlvl(full_ocr_result)
    elif max_count_category == 'olvl':
        return analysis.olvl(full_ocr_result)
    elif max_count_category == 'ite':
        # Further differentiate between NITEC and H.NITEC
        if regex.search(r'(higher\s*national\s*ite\s*certificate\sin){e<=1}', first_page_merged_text) is not None:
            # its a Higher NITEC
            return analysis.nitec(full_ocr_result, higher_nitec=True)
        else:
            return analysis.nitec(full_ocr_result, higher_nitec=False)
    elif max_count_category == 'poly':
        # Further differentiate between the 5 local polys
        polys = {
            'rp': r'republic',
            'np': r'ngee\s*ann',
            'nyp': r'nanyang',
            'tp': r'temasek',
            'sp': r'singapore'
        }
        poly_counts = {}
        for poly in polys:
            poly_pattern = '(' + polys[poly] + '){e<=1}'
            poly_counts[poly] = len(regex.findall(poly_pattern, first_page_merged_text))
        max_count_poly = max(poly_counts, key=poly_counts.get)
        return analysis.poly(full_ocr_result, poly=max_count_poly)
    elif max_count_category == 'ted':
        return analysis.ted(full_ocr_result)
    elif max_count_category == 'alvl':
        return analysis.alvl(full_ocr_result)
    elif max_count_category == 'ib':
        return analysis.ib(full_ocr_result)
    elif max_count_category == 'nush':
        return analysis.nush(full_ocr_result)

print(churn(input_path))