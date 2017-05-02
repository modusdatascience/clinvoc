import fnmatch
from .base import LexicographicPatternMatchVocabulary,\
    LexicographicRangeFillVocabulary, RegexVocabulary,\
    LexicographicVocabulary

def _expand_icd_codes(codes):
    result = []
    for code in codes:
        if '.' in code:
            part1, part2 = code.split('.')
            result.append(part1)
            for i in range(1, len(part2)):
                result.append('.'.join([part1, part2[:i]]))
        result.append(code)
    return sorted(set(result))

class ICDBase(RegexVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary):
    def __init__(self, treat_nonterminal_as_pattern=True, match_terminal_only=False):
        self.treat_nonterminal_as_pattern = treat_nonterminal_as_pattern
        self.match_terminal_only = match_terminal_only
        RegexVocabulary.__init__(self, self.regex_text)
        self.terminal_lexicon_set = set(map(self.standardize, self.pre_lexicon))
        if self.match_terminal_only:
            LexicographicVocabulary.__init__(self, self.terminal_lexicon_set)
        else:
            LexicographicVocabulary.__init__(self, _expand_icd_codes(self.terminal_lexicon_set))
    
    def _match_pattern(self, pattern):
        if '*' not in pattern and pattern not in self.terminal_lexicon_set and self.treat_nonterminal_as_pattern:
            result = fnmatch.filter(self.raw_sorted_lexicon, pattern + '*')
        else:
            result = fnmatch.filter(self.raw_sorted_lexicon, pattern)
        return result