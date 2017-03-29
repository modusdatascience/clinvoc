import os
from .resources import resources
from .base import create_bisection_range_filler, Vocabulary, create_fnmatch_wildcard_matcher,\
    left_pad

def parse_code(code):
    code = code.upper()
    assert code[0] != ' '
    code = code.strip()
    if len(code) > 3:
        result = code[:3] + '.' + code[3:]
    else:
        result = code
    return result

def read_text_file(filename):
    result = {}
    with open(filename, 'rb') as infile:
        for line in infile:
            code = line[:7]
            desc = line[8:].strip()
            result[parse_code(code)] = desc
    return result


class ICD10PCS(Vocabulary):
    all_icd10_px_codes = read_text_file(os.path.join(resources, 'icd10pcs_codes_2016.txt')).keys()
    all_icd10_px_codes.sort()
    _fill_range = staticmethod(create_bisection_range_filler(all_icd10_px_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd10_px_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        if '.' not in code:
            result = left_pad(result, 7)
            result = result[:3] + '.' + result[3:]
        else:
            result = left_pad(result, 8)
        return result

class ICD10CM(Vocabulary):
    all_icd10_dx_codes = read_text_file(os.path.join(resources, 'icd10cm_codes_2016.txt')).keys()
    all_icd10_dx_codes.sort()
    _fill_range = staticmethod(create_bisection_range_filler(all_icd10_dx_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd10_dx_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        return result
