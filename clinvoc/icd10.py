import os
from .resources import resources
from .base import left_pad, ProcedureVocabulary, DiagnosisVocabulary
from .icd import ICDBase

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

def _standardize_icd10(code, use_decimals=False):
    code_ = code.strip().upper()
    if use_decimals:
        if '.' in code_:
            pre, post = code_.split('.')
            result = left_pad(pre, 3) + '.' + post
        else:
            result = left_pad(code_, 3)
    else:
        result = code_[:3]
        if len(code_) > 3:
            result += '.' + code_[3:]
    return result
    
_all_icd10_pcs_codes = map(_standardize_icd10, _read_text_file(os.path.join(resources, 'icd10pcs_codes_2016.txt')))
_all_icd10_cm_codes = map(_standardize_icd10, _read_text_file(os.path.join(resources, 'icd10cm_codes_2016.txt')))

class ICD10Base(ICDBase):
    decimal_regex = '([A-TV-Z0-9\*]?[A-Z0-9\*])?[A-Z0-9\*](\.[A-Z0-9\*]{1,4})?'
    nondecimal_regex = '[A-TV-Z0-9\*][A-Z0-9\*][A-Z0-9\*][A-Z0-9\*]{0,4}'
#     regex_text = '[A-TV-Z0-9\*][A-Z0-9\*][A-Z0-9\*]((\.[A-Z0-9\*]{1,4})|([A-Z0-9\*]{0,4}))'

    def _standardize(self, code):
        return _standardize_icd10(code, self.use_decimals)

class ICD10PCS(ICD10Base, ProcedureVocabulary):
    vocab_name = 'ICD10PCS'
    pre_lexicon = _all_icd10_pcs_codes
  
class ICD10CM(ICD10Base, DiagnosisVocabulary):
    vocab_name = 'ICD10CM'
    pre_lexicon = _all_icd10_cm_codes
