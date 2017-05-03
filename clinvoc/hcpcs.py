from .base import RegexVocabulary, left_pad, NoWildcardsVocabulary, NoRangeFillVocabulary, NoCheckVocabulary,\
    ProcedureVocabulary, ModifierVocabulary
import re
from itertools import product

_hcpcs_split_regex = re.compile('^([A-Z]*)([0-9]+)([A-Z]*)$')
def hcpcs_split(code):
    match = _hcpcs_split_regex.match(code)
    letter_part = match.groups()[0]
    number_part = match.groups()[1]
    return letter_part, number_part

def hcpcs_join(letter_part, number_part):
    digits = 5 - len(letter_part)
    return letter_part + (('%%.%dd' % digits) % int(number_part))

class HCPCS(RegexVocabulary, NoCheckVocabulary, ProcedureVocabulary):
    vocab_name = 'HCPCS'
    def __init__(self):
        RegexVocabulary.__init__(self, '([\*ABCDEGHJKLMPQRSTVX\d][\d\*]{3}[FMTU\d\*])|([\d\*]{1,4}[FMTU\d\*])|([\d\*]{1,5})', ignore_case=True)
        
    def _fill_range(self, lower, upper):
        lower_start_letter, lower_number, lower_end_letter = _hcpcs_split_regex.match(lower).groups()
        upper_start_letter, upper_number, upper_end_letter = _hcpcs_split_regex.match(upper).groups()
        assert lower_start_letter == upper_start_letter
        assert lower_end_letter == upper_end_letter
        result = []
        for num in range(int(lower_number), int(upper_number) + 1):
            n = 5 - len(lower_start_letter) - len(lower_end_letter)
            result.append(lower_start_letter + left_pad(str(num), n) + lower_end_letter)
        return result
    
    _places = ['ABCDEGHJKLMPQRSTVX0123456789'] + \
                 3 * ['0123456789'] + \
                 ['FMTU0123456789']
                 
    def _match_pattern(self, pattern):
        options = []
        for i, item in enumerate(pattern):
            if item == '*':
                options.append(self._places[i])
            else:
                options.append([item])
        return map(''.join, product(*options))
    
    def _standardize(self, code):
        return left_pad(code.strip().upper(), 5)

class HCPCSModifier(RegexVocabulary, NoWildcardsVocabulary, NoRangeFillVocabulary, NoCheckVocabulary, ModifierVocabulary):
    vocab_name = 'HCPCSMOD'
    def __init__(self):
        RegexVocabulary.__init__(self, '[A-Za-z\d]{2}')
    
    def _standardize(self, code):
        result = code.strip().upper()
        assert len(result) == 2
        return result
    