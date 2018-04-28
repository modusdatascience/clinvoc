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
    def __init__(self, treat_nonterminal_as_pattern=True, match_terminal_only=False, use_decimals=None, 
                 use_leading_zeros=None):
        '''
        The ICD vocabularies have some inconsistencies in usage.  It's therefore necessary to specify a few
        preferences when creating the vocabulary.  A terminal code is one that is maximally specific, meaning 
        there are no codes under it in the hierarchy.  Standardized codes will always have decimals and leading
        zeros.
        
        
        Parameters
        ----------
        
        
        treat_nonterminal_as_pattern : bool
            Some people will leave use non-terminal codes to mean any code under this code in the hierarchy. To
            follow this convention, set treat_nonterminal_as_pattern=True.
            
        match_terminal_only : bool
            Set match_terminal_only=True to include only terminal codes in the lexicon.  Otherwise, non-terminal
            codes will be included as well.  Note that match_terminal_only=True is not equivalent to 
            treat_nonterminal_as_pattern=False.  These are separate, independent settings.
        
        use_decimals : bool
            Use decimal notation.  Only one of use_decimals and use_leading_zeros can be True.  If either 
            use_decimals or use_leading_zeros is None, it will be set to the opposite of the other.  If both
            are None, use_decimals will prevail.
            
        use_leading_zeros : bool
            Use leading zeros instead of decimal notation.  Only one of use_decimals and use_leading_zeros can be True.
            If either use_decimals or use_leading_zeros is None, it will be set to the opposite of the other.  If both
            are None, use_decimals will prevail.
        
            
        '''
        self.treat_nonterminal_as_pattern = treat_nonterminal_as_pattern
        self.match_terminal_only = match_terminal_only
        self.use_decimals = use_decimals if use_decimals is not None else not use_leading_zeros
        self.use_leading_zeros = use_leading_zeros if use_leading_zeros is not None else not self.use_decimals
        assert not (self.use_decimals and self.use_leading_zeros)
        assert self.use_decimals or self.use_leading_zeros
        if self.use_decimals:
            self.regex_text = self.decimal_regex
        else:
            self.regex_text = self.nondecimal_regex
#             
#         if self.allow_decimal and not self.require_decimal:
#             self.regex_text = '(%s)|(%s)' % (self.decimal_regex, self.nondecimal_regex)
#         elif self.allow_decimal:
#             self.regex_text = self.decimal_regex
#         elif not self.require_decimal:
#             self.regex_text = self.nondecimal_regex
#         else:
#             raise ValueError('Can\'t have require_decimal=True and allow_decimal=False.')
        
        RegexVocabulary.__init__(self, self.regex_text)
        self.terminal_lexicon_set = set(self.pre_lexicon)
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
    