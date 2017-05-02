# coding: utf-8
from bisect import bisect_left, bisect_right
from abc import abstractmethod
import fnmatch
import re
from toolz.functoolz import memoize
from pyparsing import Regex, NoMatch, Literal, White, ZeroOrMore, StringEnd,\
    Optional, OneOrMore
from operator import xor, or_
from itertools import product, chain, starmap

def left_pad(code, expected_length, padding='0'):
    n = len(code)
    if n > expected_length:
        raise ValueError
    return (padding * (expected_length - n)) + code

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError

def create_bisection_range_filler(codes, name=None):
    sorted_codes = sorted(codes)
    def range_filler(start, end):
        left_idx = index(sorted_codes, start)
        right_idx = index(sorted_codes, end)
        return [sorted_codes[idx] for idx in range(left_idx, right_idx + 1)]
    if name is not None:
        range_filler.__name__ = name
    return range_filler

def create_fnmatch_wildcard_matcher(codes, name=None):
    sorted_codes = sorted(codes)
    def fnmatch_wildcard_matcher(pattern):
        return fnmatch.filter(sorted_codes, pattern)
    
    if name is not None:
        fnmatch_wildcard_matcher.__name__ = name
    return fnmatch_wildcard_matcher

def create_vocabulary_checker(codes, name=None):
    code_set = set(codes)
    def check(code):
        return code in code_set
    if name is not None:
        check.__name__ = str(name)
    return check

class Vocabulary(object):
    @abstractmethod
    def parse(self, expression):
        '''
        Convert a string containing codes, patterns (codes with wildcards), and code ranges to a set of standardized 
        codes.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def _match_pattern(self, pattern):
        raise NotImplementedError
    
    @abstractmethod
    def standardize(self, code):
        '''
        Convert a code or pattern (code with wildcards) to a standard form.  The standard form should ensure that 
        two codes have the same meaning if and only if they are identical.  For example, leading zeros, whitespace, 
        dashes, or capitalization may be standardized.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def _fill_range(self, lower, upper):
        raise NotImplementedError
    
    @abstractmethod
    def check(self, code):
        '''
        Check a code against the known lexicon.  Return True if the code matches a known code and
        False otherwise.
        '''
        raise NotImplementedError
    
    def strict_parse(self, expression, *args, **kwargs):
        '''
        Same as parse, but only returns codes that are present in the known lexicon.
        '''
        return self.filter(self.parse(expression, *args, **kwargs))
    
    def match_pattern(self, pattern):
        '''
        Return a set of codes matching pattern, where pattern may contain wildcards.  Different vocabularies
        may interpret wildcards slightly differently, but the general idea is that "*" matches anything.  In 
        some vocabularies that might mean any valid substring, while in others it might mean any valid 
        character.  
        '''
        standardized_pattern = self.standardize(pattern)
        result = self._match_pattern(standardized_pattern)
        if not result and '*' not in pattern:
            result = set([standardized_pattern])
        return result
    
    def strict_match_pattern(self, pattern):
        '''
        Same as match_pattern, but only return codes that are present in the known lexicon.
        '''
        return self.filter(self.match_pattern(pattern))
    
    def fill_range(self, lower, upper):
        '''
        Return the set of all codes that are greater than or equal to lower and less than or equal to upper.  Not 
        every code system is totally ordered.  In some cases, only a partial order is available, and in those cases
        lower and upper must be comparable.  If lower and upper are not comparable, raise NotImplementedError.
        '''
        return set(map(self.standardize, self._fill_range(self.standardize(lower), self.standardize(upper))))
    
    def strict_fill_range(self, lower, upper):
        '''
        Same as fill_range, but only return codes that are present in the known lexicon.
        '''
        return self.filter(self.fill_range(lower, upper))
    
    def fill_set_range(self, lowers, uppers):
        '''
        Return the set of all codes that are greater than or equal to lower and less than or equal to upper for 
        some lower in lowers and some upper in uppers.  Any incomparable pairs will be skipped.  If no pairs are 
        comparable, raise a NotImplementedError.
        '''
        result = set([])
        any_implemented = False
        for lower, upper in product(lowers, uppers):
            try:
                result.update(self._fill_range(lower, upper))
                any_implemented = True
            except NotImplementedError:
                pass
        if not any_implemented:
            raise NotImplementedError('No comparable code pairs found.')
        return result
    
    def strict_fill_set_range(self, lowers, uppers):
        '''
        Same as fill_set_range, but only return codes that are present in the known lexicon.
        '''
        return self.filter(self.fill_set_range(lowers, uppers))
    
    def fill_pattern_range(self, lower, upper):
        '''
        Return the set of all codes that are greater than or equal to A and less than or equal to B for 
        some A matching lower and some B matching upper.  Any incomparable pairs will be skipped.  If no pairs are 
        comparable, raise a NotImplementedError.
        '''
        lowers = self.match_pattern(lower)
        uppers = self.match_pattern(upper)
        return self.fill_set_range(lowers, uppers)
    
    def strict_fill_pattern_range(self, lower, upper):
        '''
        Same as fill_pattern_range, but only return codes that are present in the known lexicon.
        '''
        return self.filter(self.fill_pattern_range(lower, upper))
    
    def filter(self, codes):
        '''
        Return only those codes that are in the known lexicon.  Codes are standardized.
        '''
        return set(map(self.standardize, filter(self.check, codes)))

@memoize
def create_parser(regexes, pattern_matchers, range_fillers, quote_pairs=[('\'','\''), ('"','"')], delimiters=[','], 
                  require_quotes=False, require_delimiter=False, allow_empty=True):
    if isinstance(regexes, basestring) or isinstance(regexes, re._pattern_type):
        regexes = [regexes]
        pattern_matchers = [pattern_matchers]
        range_fillers = [range_fillers]
    assert len(regexes) == len(pattern_matchers)
    assert len(regexes) == len(range_fillers)
    
    code_patterns = list(starmap(lambda regex, pattern_matcher: Regex(regex).setParseAction(lambda s, loc, toks: frozenset(pattern_matcher(toks[0]))), zip(regexes, pattern_matchers)))
    if require_quotes:
        quoted_code_patterns = [NoMatch() for _ in code_patterns]
    else:
        quoted_code_patterns = code_patterns
    for opener, closer in quote_pairs:
        quoted_code_patterns = list(starmap(lambda quoted_code_pattern, code_pattern: quoted_code_pattern | (Literal(opener).suppress() + code_pattern + Literal(closer).suppress()), zip(quoted_code_patterns, code_patterns)))
    
    code_ranges = map(lambda quoted_code_pattern: quoted_code_pattern + Literal('-').suppress() + quoted_code_pattern, quoted_code_patterns)
    code_ranges = list(starmap(lambda code_range, range_filler: code_range.setParseAction(lambda s, loc, toks: frozenset(range_filler(toks[0], toks[1]))), zip(code_ranges, range_fillers)))
    
    quoted_code_ranges = [NoMatch() for _ in code_ranges]
    for opener, closer in quote_pairs:
        quoted_code_ranges = list(starmap(lambda quoted_code_range, code_pattern: quoted_code_range | (Literal(opener).suppress() + code_pattern + Literal('-').suppress() + code_pattern + Literal(closer).suppress()), zip(quoted_code_ranges, code_patterns)))
    quoted_code_ranges = list(starmap(lambda quoted_code_range, range_filler: quoted_code_range.setParseAction(lambda s, loc, toks: frozenset(range_filler(toks[0], toks[1]))), zip(quoted_code_ranges, range_fillers)))
    any_code_ranges = list(starmap(or_, zip(quoted_code_ranges, code_ranges)))
    quoted_code_pattern = reduce(xor, quoted_code_patterns)
    any_code_range = reduce(xor, any_code_ranges)
    any_delim = reduce(xor, map(Literal, delimiters))
    if allow_empty:
        any_delim = OneOrMore(any_delim)
    code_list_continuation = any_delim.suppress() + (any_code_range | quoted_code_pattern)
    if not require_delimiter:
        code_list_continuation |= White().suppress() + (any_code_range | quoted_code_pattern)
    code_list = (any_code_range | quoted_code_pattern) + ZeroOrMore(code_list_continuation) + Optional(reduce(or_, map(Literal, delimiters))).suppress() + StringEnd()
    return code_list

all_quote_pairs = (('\'','\''), ('"','"'), ('‘','’'))
class RegexVocabularyBase(Vocabulary):
    def standardize(self, code):
        code_ = code.strip()
        assert self.exact_regex.match(code_), '%s is not a properly formatted code for %s' % (code, type(self).__name__)
        return self._standardize(code_)
    
    @abstractmethod
    def _standardize(self, code):
        raise NotImplementedError

class RegexVocabulary(RegexVocabularyBase):
    def __init__(self, regex, ignore_case=False):
        if ignore_case:
            self.regex = re.compile(regex, re.IGNORECASE)
            self.exact_regex = re.compile('^%s$' % regex, re.IGNORECASE)
        else:
            self.regex = re.compile(regex)
            self.exact_regex = re.compile('^%s$' % regex)
        
    def parse(self, expression,  quote_pairs=all_quote_pairs,
              delimiters=(',',), require_quotes=False, require_delimiter=False):
        parser = create_parser(self.regex, self.match_pattern, self.fill_set_range, quote_pairs=tuple(quote_pairs),
                               delimiters=tuple(delimiters), require_quotes=require_quotes, require_delimiter=require_delimiter)
        return set(chain(*parser.parseString(expression)))
    
    def __or__(self, other):
        if isinstance(other, RegexVocabulary):
            return RegexUnionVocabulary(self, other)
        else:
            return NotImplemented
        
    def __ror__(self, other):
        return self.__or__(other)

class RegexUnionVocabulary(RegexVocabularyBase):
    def __init__(self, *arguments):
        self.arguments = arguments
        
    def parse(self, expression,  quote_pairs=all_quote_pairs,
              delimiters=(',',), require_quotes=False, require_delimiter=False):
        parser = create_parser(tuple([arg.regex for arg in self.arguments]), tuple([arg.match_pattern for arg in self.arguments]), 
                               tuple([arg.fill_set_range for arg in self.arguments]), quote_pairs=tuple(quote_pairs),
                               delimiters=tuple(delimiters), require_quotes=require_quotes, require_delimiter=require_delimiter)
        return set(chain(*parser.parseString(expression)))
    
    def __or__(self, other):
        if isinstance(other, RegexVocabulary):
            return RegexUnionVocabulary(other, *self.arguments)
        elif isinstance(other, RegexUnionVocabulary):
            return RegexUnionVocabulary(*(other.arguments + self.arguments))
        else:
            return NotImplemented
        
    def __ror__(self, other):
        return self.__or__(other)

class LexiconVocabulary(Vocabulary):
    def __init__(self, lexicon):
        self.lexicon_set = set(lexicon)
        
    def check(self, code):
        try:
            return self.standardize(code) in self.lexicon_set
        except AssertionError:
            return False

class LexicographicVocabulary(LexiconVocabulary):
    def __init__(self, lexicon):
        LexiconVocabulary.__init__(self, lexicon)
        self.raw_sorted_lexicon = sorted(self.lexicon_set)
        self.sorted_lexicon = sorted(map(self.orderfy, self.lexicon_set))
        
    def orderfy(self, code):
        return code
    
    def deorderfy(self, ordobj):
        return ordobj

class LexicographicRangeFillVocabulary(LexicographicVocabulary):
    def _fill_range(self, lower, upper):
        left_idx = bisect_left(self.sorted_lexicon, self.orderfy(lower))
        right_idx = bisect_right(self.sorted_lexicon, self.orderfy(upper))
        return map(self.deorderfy, self.sorted_lexicon[left_idx:right_idx])

class LexicographicPatternMatchVocabulary(LexicographicVocabulary):
    def _match_pattern(self, pattern):
        return fnmatch.filter(self.raw_sorted_lexicon, pattern)

class NoWildcardsVocabulary(Vocabulary):
    def _match_pattern(self, pattern):
        if '*' in pattern:
            raise NotImplementedError('%s does not support wildcards.' % type(self).__name__)
        return set([pattern])

class NoRangeFillVocabulary(Vocabulary):
    def _fill_range(self, lower, upper):
        raise NotImplementedError('%s does not support range filling.' % type(self).__name__)
# class ParserMeta(type):
#     def __init__(cls, name, bases, dct):
#         super(ParserMeta, cls).__init__(name, bases, dct)
#         
# 
# class ParserVocabulary(Vocabulary):
#     def __init__(self, ):
#     '''
#     Subclasses should define 
#     '''
#     def parse(self, expression):
#         self.parser.

    
# 
# class Vocabulary(object):
#     @abstractmethod
#     def parse(self, expression, delimiter=',;\s', range_delimiter='-'):
#         delimiter_pattern = re.compile('[^%s]+' % delimiter)
#         range_delimiter_pattern = re.compile(range_delimiter)
#         
#         # Remove any whitespace around range delimiters
#         delimiter_range_delimiter_reduction_pattern = re.compile('\s*%s\s*' % range_delimiter)
#         reduced_expression = delimiter_range_delimiter_reduction_pattern.sub(range_delimiter, expression)
#         
#         # Break into parts by delimiter
#         parts = delimiter_pattern.findall(reduced_expression)
#         
#         # Now look for any ranges or wild cards
#         codes = set()
#         for raw_part in parts:
#             # Remove quotes
#             part = raw_part.replace('\'', '').replace('"', '').replace('’', '').replace('‘', '')
#             
#             # Handle ranges and patterns
#             if range_delimiter_pattern.search(part):
#                 raw_start, raw_end = re.split("'?\s*%s\s*'?" % range_delimiter, part)
#                 starts = self.match_pattern(raw_start)
#                 assert starts
#                 ends = self.match_pattern(raw_end)
#                 assert ends
#                 for start in starts:
#                     for end in ends:
#                         codes.update(self.fill_range(start, end))
#             else:
#                 matches = self.match_pattern(part)
#                 assert matches
#                 codes.update(matches)
#         return codes
# #                 
# #                 
# #                 if '*' in start:
# #                     starts = wild_card_fillers[(code_type, code_system)](start)
# #                 else:
# #                     starts = [start]
# #                 if '*' in end:
# #                     ends = wild_card_fillers[(code_type, code_system)](end)
# #                 else:
# #                     ends = [end]
# #                 codes.extend(list(set(starts+ends+range_fillers[(code_type, code_system)](min(starts), max(ends)))))
# #             elif '*' in part:
# #                 codes.extend(wild_card_fillers[(code_type, code_system)](part))
# #             else:
# #                 codes.append(part)
# #         return [code_processors[(code_type, code_system)](code) for code in codes]
#     
#     @abstractmethod
#     def standardize(self, code):
#         raise NotImplementedError
#     
#     @abstractmethod
#     def _fill_range(self, lower, upper):
#         raise NotImplementedError
#     
#     def fill_range(self, lower, upper):
#         return [self.standardize(code) for code in self._fill_range(self.standardize(lower), self.standardize(upper))]
#     
#     @abstractmethod
#     def _match_pattern(self, pattern):
#         raise NotImplementedError
#     
#     def match_pattern(self, pattern):
#         return [self.standardize(code) for code in self._match_pattern(self.standardize(pattern))]
#     
# 
#     
