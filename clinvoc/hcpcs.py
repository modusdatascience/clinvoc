from .base import RegexVocabulary, left_pad
import re
from clinvoc.base import NoWildcardsVocabulary, NoRangeFillVocabulary

_hcpcs_split_regex = re.compile('([A-z]*)([0-9]+)')
def hcpcs_split(code):
    match = _hcpcs_split_regex.match(code)
    letter_part = match.groups()[0]
    number_part = match.groups()[1]
    return letter_part, number_part

def hcpcs_join(letter_part, number_part):
    digits = 5 - len(letter_part)
    return letter_part + (('%%.%dd' % digits) % int(number_part))

class HCPCS(RegexVocabulary, NoWildcardsVocabulary):
    def __init__(self):
        level_1_regex = '(\d{4}F)|(\d{4}T)|(\d{1,5})'
        level_2_regex = '[A-V]\d{4}'
        RegexVocabulary.__init__(self, '(%s)|(%s)' % (level_1_regex, level_2_regex))
        
    @staticmethod
    def _fill_range(start, end):
        start_letter, start_number = hcpcs_split(start)
        end_letter, end_number = hcpcs_split(end)
        assert start_letter == end_letter
        result = []
        for num in range(int(start_number), int(end_number) + 1):
            result.append(hcpcs_join(start_letter, num))
        return result
    
    @staticmethod
    def _standardize(code):
        return left_pad(code.strip().upper(), 5)

class HCPCSModifier(RegexVocabulary, NoWildcardsVocabulary, NoRangeFillVocabulary):
    def __init__(self):
        RegexVocabulary.__init__(self, '[A-Za-z\d]{2}')
    
    @staticmethod
    def _standardize(code):
        result = code.strip()
        assert len(result) == 2
        return result
    