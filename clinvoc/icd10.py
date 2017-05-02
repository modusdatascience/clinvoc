import os
from .resources import resources
from .base import RegexVocabulary
from .icd import _expand_icd_codes, ICDBase

def parse_code(code):
    code = code.upper()
    assert code[0] != ' '
    code = code.strip()
    if len(code) > 3:
        result = code[:3] + '.' + code[3:]
    else:
        result = code
    return result

def _read_text_file(filename):
    result = []
    with open(filename, 'rb') as infile:
        for line in infile:
            result.append(line[:7])
    return result

_all_icd10_pcs_codes = _read_text_file(os.path.join(resources, 'icd10pcs_codes_2016.txt'))
_all_icd10_cm_codes = _read_text_file(os.path.join(resources, 'icd10cm_codes_2016.txt'))

class ICD10Base(ICDBase):
    regex_text = '[A-TV-Z0-9\*][A-Z0-9\*][A-Z0-9\*]((\.[A-Z0-9\*]{1,4})|([A-Z0-9\*]{0,4}))'
#     def __init__(self):
#         RegexVocabulary.__init__(self, self.regex_text)
        
    def _standardize(self, code):
        code_ = code.strip().upper()
        if '.' in code_:
            result = code_
        else:
            result = code_[:3]
            if len(code_) > 3:
                result += '.' + code_[3:]
        return result

class ICD10PCS(ICD10Base):
    pre_lexicon = _all_icd10_pcs_codes
#     def __init__(self):
#         ICD10Base.__init__(self)
#         LexicographicVocabulary.__init__(self, _all_icd10_pcs_codes)
      
# class ICD10PCSExpanded(ICD10Base):
#     def __init__(self):
#         ICD10Base.__init__(self)
#         LexicographicVocabulary.__init__(self, _expand_icd_codes(map(self.standardize, _all_icd10_pcs_codes)))
  
class ICD10CM(ICD10Base):
    pre_lexicon = _all_icd10_cm_codes
#     def __init__(self):
#         ICD10Base.__init__(self)
#         LexicographicVocabulary.__init__(self, _all_icd10_cm_codes)
# 
# class ICD10CMExpanded(ICD10Base):
#     def __init__(self):
#         ICD10Base.__init__(self)
#         LexicographicVocabulary.__init__(self, _expand_icd_codes(map(self.standardize, _all_icd10_cm_codes)))

def ICD10Mixed(*args, **kwargs):
    return ICD10PCS(*args, **kwargs) | ICD10CM(*args, **kwargs)
    
