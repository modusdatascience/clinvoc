import os
from .resources import resources
from .base import create_bisection_range_filler, create_fnmatch_wildcard_matcher, SimpleParseVocabulary

def parse_dx_code(code):
    code = code.upper()
    assert code[0] != ' '
    code = code.strip()
    if code[0] == 'V':
        result = code[:3]
        if len(code) > 3:
            result += '.' + code[3:]
    elif code[0] == 'E':
        result = code[:4]
        if len(code) > 4:
            result += '.' + code[3:]
    else:
        assert code[0].isdigit()
        result = code[:3] 
        if len(code) > 3:
            result += '.' + code[3:]
    return result

def read_dx_text_file(filename):
    result = {}
    with open(filename, 'rb') as infile:
        for line in infile:
            code = line[:5]
            desc = line[6:].strip()
            result[parse_dx_code(code)] = desc
    return result

def parse_px_code(code):
    code = code.upper()
    assert code[0] != ' '
    code = code.strip()
    if code[0] == 'V':
        raise ValueError('code')
        result = code[:3]
        if len(code) > 3:
            result += '.' + code[3:]
    elif code[0] == 'E':
        raise ValueError('code')
        result = code[:4]
        if len(code) > 4:
            result += '.' + code[3:]
    else:
        assert code[0].isdigit()
        result = code[:2] 
        if len(code) > 2:
            result += '.' + code[2:]
    return result

def read_px_text_file(filename):
    result = {}
    with open(filename, 'rb') as infile:
        for line in infile:
            code = line[:5]
            desc = line[6:].strip()
            result[parse_px_code(code)] = desc
    return result

# 
# 
# all_icd9_dx_codes = read_dx_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_DX.txt')).keys()
# all_icd9_dx_codes.sort()
# all_icd9_px_codes = read_px_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_SG.txt')).keys()
# all_icd9_px_codes.sort()
# 
# icd9_dx_range_fill = create_bisection_range_filler(all_icd9_dx_codes)
# icd9_px_range_fill = create_bisection_range_filler(all_icd9_px_codes)

class ICD9PCS(SimpleParseVocabulary):
    all_icd9_px_codes = read_px_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_SG.txt')).keys()
    all_icd9_px_codes.sort()
    _fill_range = staticmethod(create_bisection_range_filler(all_icd9_px_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd9_px_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        return result

class ICD9CM(SimpleParseVocabulary):
    all_icd9_dx_codes = read_dx_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_DX.txt')).keys()
    all_icd9_dx_codes.sort()
    _fill_range = staticmethod(create_bisection_range_filler(all_icd9_dx_codes, '_fill_range'))
    _match_pattern = staticmethod(create_fnmatch_wildcard_matcher(all_icd9_dx_codes, '_match_pattern'))
    def standardize(self, code):
        result = code.strip()
        return result


