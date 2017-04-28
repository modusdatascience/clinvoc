# coding: utf-8
from bisect import bisect_left, bisect_right
from abc import abstractmethod
import fnmatch
import re
from toolz.functoolz import memoize
from pyparsing import Regex, NoMatch, Literal, White, ZeroOrMore, StringEnd,\
    Optional
from operator import or_
from itertools import product, chain

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
        raise NotImplementedError
    
    @abstractmethod
    def _match_pattern(self, pattern):
        raise NotImplementedError
    
    @abstractmethod
    def standardize(self, code):
        raise NotImplementedError
    
    @abstractmethod
    def _fill_range(self, lower, upper):
        raise NotImplementedError
    
    @abstractmethod
    def check(self, code):
        raise NotImplementedError
    
    def strict_parse(self, expression, *args, **kwargs):
        return self.filter(self.parse(expression, *args, **kwargs))
    
    def match_pattern(self, pattern):
        if '*' in pattern:
            return set([self.standardize(code) for code in self._match_pattern(self.standardize(pattern))])
        else:
            return set([self.standardize(pattern)])
    
    def strict_match_pattern(self, pattern):
        return self.filter(self.match_pattern(pattern))
    
    def fill_range(self, lower, upper):
        return set(map(self.standardize, self._fill_range(self.standardize(lower), self.standardize(upper))))
    
    def strict_fill_range(self, lower, upper):
        return self.filter(self.fill_range(lower, upper))
    
    def fill_set_range(self, lowers, uppers):
        result = set([])
        for lower, upper in product(lowers, uppers):
            result.update(self._fill_range(lower, upper))
        return result
    
    def strict_fill_set_range(self, lowers, uppers):
        return self.filter(self.fill_set_range(lowers, uppers))
    
    def fill_pattern_range(self, lower, upper):
        lowers = self.match_pattern(lower)
        uppers = self.match_pattern(upper)
        return self.fill_set_range(lowers, uppers)
    
    def strict_fill_pattern_range(self, lower, upper):
        return self.filter(self.fill_pattern_range(lower, upper))
    
    def filter(self, codes):
        return set(filter(self.check, codes))

class SimpleParseVocabulary(Vocabulary):
    def parse(self, expression, delimiter=',;\s', range_delimiter='-'):
        delimiter_pattern = re.compile('[^%s]+' % delimiter)
        range_delimiter_pattern = re.compile(range_delimiter)
        
        # Remove any whitespace around range delimiters
        delimiter_range_delimiter_reduction_pattern = re.compile('\s*%s\s*' % range_delimiter)
        reduced_expression = delimiter_range_delimiter_reduction_pattern.sub(range_delimiter, expression)
        
        # Break into parts by delimiter
        parts = delimiter_pattern.findall(reduced_expression)
        
        # Now look for any ranges or wild cards
        codes = set()
        for raw_part in parts:
            # Remove quotes
            part = raw_part.replace('\'', '').replace('"', '').replace('’', '').replace('‘', '')
            
            # Handle ranges and patterns
            if range_delimiter_pattern.search(part):
                raw_start, raw_end = re.split("'?\s*%s\s*'?" % range_delimiter, part)
                starts = self.match_pattern(raw_start)
                assert starts
                ends = self.match_pattern(raw_end)
                assert ends
                for start in starts:
                    for end in ends:
                        codes.update(self.fill_range(start, end))
            else:
                matches = self.match_pattern(part)
                assert matches
                codes.update(matches)
        return codes

@memoize
def create_parser(regex, pattern_matcher, range_filler, quote_pairs=[('\'','\''), ('"','"')], delimiters=[','], 
                  require_quotes=False, require_delimiter=False):
    code_pattern = Regex(regex)
    code_pattern.setParseAction(lambda s, loc, toks: frozenset(pattern_matcher(toks[0])))
    if require_quotes:
        quoted_code_pattern = NoMatch()
    else:
        quoted_code_pattern = code_pattern
    for opener, closer in quote_pairs:
        quoted_code_pattern ^= Literal(opener).suppress() + code_pattern + Literal(closer).suppress()
    
    code_range = quoted_code_pattern + Literal('-').suppress() + quoted_code_pattern
    code_range.setParseAction(lambda s, loc, toks: frozenset(range_filler(toks[0], toks[1])))
    code_list_continuation = reduce(or_, map(Literal, delimiters)).suppress() + (code_range | quoted_code_pattern)
    if not require_delimiter:
        code_list_continuation |= White().suppress() + (code_range | quoted_code_pattern)
    code_list = (code_range | quoted_code_pattern) + ZeroOrMore(code_list_continuation) + Optional(reduce(or_, map(Literal, delimiters))).suppress() + StringEnd()
    return code_list

all_quote_pairs = (('\'','\''), ('"','"'), ('‘','’'))
class RegexVocabulary(Vocabulary):
    def __init__(self, regex):
        self.regex = re.compile(regex)
        
    def parse(self, expression,  quote_pairs=all_quote_pairs,
              delimiters=(',',), require_quotes=False, require_delimiter=False):
        parser = create_parser(self.regex, self.match_pattern, self.fill_set_range, quote_pairs=tuple(quote_pairs),
                               delimiters=tuple(delimiters), require_quotes=require_quotes, require_delimiter=require_delimiter)
        return set(chain(*parser.parseString(expression)))
    
    def standardize(self, code):
        assert self.regex.match(code), '%s is not a properly formatted code for %s' % (code, type(self).__name__)
        return self._standardize(code)
    
    @abstractmethod
    def _standardize(self, code):
        raise NotImplementedError

class LexiconVocabulary(Vocabulary):
    def __init__(self, lexicon):
        self.lexicon_set = set(map(self.standardize, lexicon))
        
    def check(self, code):
        return self.standardize(code) in self.lexicon_set

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
