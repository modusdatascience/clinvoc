import os
from .resources import resources
from .base import create_bisection_range_filler, create_fnmatch_wildcard_matcher,\
    left_pad, SimpleParseVocabulary

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

all_icd10_pcs_codes = read_text_file(os.path.join(resources, 'icd10pcs_codes_2016.txt')).keys()
all_icd10_pcs_codes.sort()
all_icd10_cm_codes = read_text_file(os.path.join(resources, 'icd10cm_codes_2016.txt')).keys()
all_icd10_cm_codes.sort()

class ICD10PCS(SimpleParseVocabulary):
    _fill_range = staticmethod(create_bisection_range_filler(all_icd10_pcs_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd10_pcs_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        if '.' not in code:
            result = left_pad(result, 7)
            result = result[:3] + '.' + result[3:]
        else:
            result = left_pad(result, 8)
        return result

class ICD10CM(SimpleParseVocabulary):
    _fill_range = staticmethod(create_bisection_range_filler(all_icd10_cm_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd10_cm_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        return result
