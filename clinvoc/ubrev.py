import re
from .base import RegexVocabulary

_ubrev_split_regex = re.compile('([0-9]+)([A-z]*)')
def ubrev_split(code):
    match = _ubrev_split_regex.match(code)
    number_part = match.groups()[0]
    letter_part = match.groups()[1]
    return number_part, letter_part

def ubrev_join(number_part, letter_part):
    digits = 4 - len(letter_part)
    return (('%%.%dd' % digits) % int(number_part)) + letter_part

class UBREV(RegexVocabulary):
    regex = re.compile('[\d]{1,2}\.?(([\d]{1,2})|([\d][A-z]))')
    @staticmethod
    def _fill_range(start, end):
        start_number, start_letter = ubrev_split(start)
        end_number, end_letter = ubrev_split(end)
        assert start_letter == end_letter
        result = []
        for num in range(int(start_number), int(end_number) + 1):
            result.append(ubrev_join(num, start_letter))
        return result
    
    @staticmethod
    def _match_pattern(pattern):
        assert '*' not in pattern 
        return set([pattern])
    
    @staticmethod
    def standardize(code):
        return ubrev_join(*ubrev_split(code))
