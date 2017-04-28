import os
from .resources import resources
from .base import SimpleParseVocabulary, left_pad
from clinvoc.base import LexicographicPatternMatchVocabulary,\
    LexicographicRangeFillVocabulary, LexicographicVocabulary, \
    RegexVocabulary

def _read_text_file(filename):
    result = []
    with open(filename, 'rb') as infile:
        for line in infile:
            result.append(line[:5])
    return result

_all_icd9_cm_codes = _read_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_DX.txt'))
_all_icd9_pcs_codes = _read_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_SG.txt'))

class ICD9CM(RegexVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary):
    def __init__(self):
        v_regex = 'V[\d\*]{2}((\.[\d\*]{1,2})|([\d\*]{0,2}))'
        e_regex = 'E[\d\*]{3}((\.[\d\*]{1})|([\d\*]{0,1}))'
        n_regex = '[\d\*]{1,3}((\.[\d\*]{1,2})|([\d\*]{0,2}))'
        RegexVocabulary.__init__(self, '(%s)|(%s)|(%s)' % (v_regex, e_regex, n_regex))
        LexicographicVocabulary.__init__(self, _all_icd9_cm_codes)
        
    def _standardize(self, code):
        code_ = code.strip().upper()
        if '.' in code_:
            pre, post = code_.split('.')
            result = left_pad(pre, 3) + '.' + post
        else:
            if code_[0] == 'V':
                result = code_[:3]
                if len(code_) > 3:
                    result += '.' + code_[3:]
            elif code_[0] == 'E':
                result = code_[:4]
                if len(code_) > 4:
                    result += '.' + code_[4:]
            else:
                assert code_[0].isdigit()
                result = code_[:3] 
                if len(code_) > 3:
                    result += '.' + code_[3:]
        return result

class ICD9PCS(SimpleParseVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary):
    def __init__(self):
        LexicographicVocabulary.__init__(self, _all_icd9_pcs_codes)

    def standardize(self, code):
        code_ = code.strip().upper()
        if '.' in code_:
            pre, post = code_.split('.')
            result = left_pad(pre, 2) + '.' + post
        else:
            assert code_[0].isdigit()
            result = code_[:2] 
            if len(code_) > 2:
                result += '.' + code_[2:]
        return result




