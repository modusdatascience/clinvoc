import os
from .resources import resources
from .base import left_pad, LexicographicPatternMatchVocabulary,\
    LexicographicRangeFillVocabulary, RegexVocabulary
from .icd import ICDBase

def _read_text_file(filename):
    result = []
    with open(filename, 'rb') as infile:
        for line in infile:
            result.append(line[:5])
    return result

_all_icd9_cm_codes = _read_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_DX.txt'))
_all_icd9_pcs_codes = _read_text_file(os.path.join(resources, 'CMS32_DESC_SHORT_SG.txt'))

class ICD9CM(ICDBase):
    regex_text = '(%s)|(%s)|(%s)' % ('V[\d\*]{2}((\.[\d\*]{1,2})|([\d\*]{0,2}))', 
                                     'E[\d\*]{3}((\.[\d\*]{1})|([\d\*]{0,1}))', 
                                     '([\d\*]{1,3}(\.[\d\*]{1,2}))|([\d\*]{3,5})')
    pre_lexicon = _all_icd9_cm_codes
    
    def _standardize(self, code):
        code_ = code.strip().upper()
        if '.' in code_:
            pre_len = 4 if code[0] == 'E' else 3
            pre, post = code_.split('.')
            result = left_pad(pre, pre_len) + '.' + post
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

# class ICD9CMStrict(ICD9CMBase):
#     '''
#     Includes only terminal codes.
#     '''
#     def __init__(self, treat_nonterminal_as_pattern=True):
#         ICD9CMBase.__init__(self, treat_nonterminal_as_pattern)
#         self.terminal_lexicon_set = set(map(self.standardize, _all_icd9_cm_codes))
#         LexicographicVocabulary.__init__(self, self.terminal_lexicon_set)
#         
# class ICD9CMExpanded(ICD9CMBase):
#     '''
#     Includes terminal codes and their groupings.  For example, if 123.45 is a terminal code,
#     this expanded set will also include 123 and 123.4.
#     '''
#     def __init__(self, treat_nonterminal_as_pattern=True):
#         ICD9CMBase.__init__(self, treat_nonterminal_as_pattern)
#         self.terminal_lexicon_set = set(map(self.standardize, _all_icd9_cm_codes))
#         LexicographicVocabulary.__init__(self, _expand_icd_codes(self.terminal_lexicon_set))

class ICD9PCS(ICDBase):
    regex_text = '([\d\*]{1,2}(\.[\d\*]{1,3}))|([\d\*]{2,5})'
    pre_lexicon = _all_icd9_pcs_codes
#     def __init__(self, treat_nonterminal_as_pattern=True):
#         RegexVocabulary.__init__(self, self.regex_text)

    def _standardize(self, code):
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
    
# class ICD9PCSStrict(ICD9PCSBase):
#     def __init__(self):
#         ICD9PCSBase.__init__(self)
#         LexicographicVocabulary.__init__(self, _all_icd9_pcs_codes)
#     
# class ICD9PCSExpanded(ICD9PCSBase):
#     def __init__(self):
#         ICD9PCSBase.__init__(self)
#         LexicographicVocabulary.__init__(self, _expand_icd_codes(map(self.standardize, _all_icd9_pcs_codes)))
    
def ICD9Mixed(*args, **kwargs):
    return ICD9CM(*args, **kwargs) | ICD9PCS(*args, **kwargs)

