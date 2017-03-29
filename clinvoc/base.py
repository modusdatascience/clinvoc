# coding: utf-8
from bisect import bisect_left
from abc import abstractmethod
import fnmatch
import re

def left_pad(code, expected_length):
    n = len(code)
    if n > expected_length:
        raise ValueError
    return ('0' * (expected_length - n)) + code

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError

def create_bisection_range_filler(codes, name=None):
    def range_filler(start, end):
        left_idx = index(codes, start)
        right_idx = index(codes, end)
        return [codes[idx] for idx in range(left_idx, right_idx + 1)]
    if name is not None:
        range_filler.__name__ = name
    return range_filler

def create_fnmatch_wildcard_matcher(codes, name=None):
    def fnmatch_wildcard_matcher(pattern):
        return fnmatch.filter(codes, pattern)
    
    if name is not None:
        fnmatch_wildcard_matcher.__name__ = name
    return fnmatch_wildcard_matcher

class Vocabulary(object):
    @abstractmethod
    def parse(self, expression, delimiter=',;\s', range_delimiter='-'):
        delimiter_pattern = re.compile('[^%s]+' % delimiter)
        range_delimiter_pattern = re.compile(range_delimiter)
        
        # Break into parts by delimiter
        parts = delimiter_pattern.findall(expression)
        
        # Now look for any ranges or wild cards
        codes = set()
        for raw_part in parts:
            # Remove quotes
            part = raw_part.replace('\'', '').replace('"', '').replace('’', '').replace('‘', '')
            
            # Handle ranges and patterns
            if range_delimiter_pattern.search(part):
                raw_start, raw_end = re.split("'?%s'?" % range_delimiter, part)
                starts = self.match_pattern(raw_start)
                ends = self.match_pattern(raw_end)
                for start in starts:
                    for end in ends:
                        codes.update(self.fill_range(start, end))
            else:
                codes.update(self.match_pattern(part))
        return codes
#                 
#                 
#                 if '*' in start:
#                     starts = wild_card_fillers[(code_type, code_system)](start)
#                 else:
#                     starts = [start]
#                 if '*' in end:
#                     ends = wild_card_fillers[(code_type, code_system)](end)
#                 else:
#                     ends = [end]
#                 codes.extend(list(set(starts+ends+range_fillers[(code_type, code_system)](min(starts), max(ends)))))
#             elif '*' in part:
#                 codes.extend(wild_card_fillers[(code_type, code_system)](part))
#             else:
#                 codes.append(part)
#         return [code_processors[(code_type, code_system)](code) for code in codes]
    
    @abstractmethod
    def standardize(self, code):
        raise NotImplementedError
    
    @abstractmethod
    def _fill_range(self, lower, upper):
        raise NotImplementedError
    
    def fill_range(self, lower, upper):
        return [self.standardize(code) for code in self._fill_range(self.standardize(lower), self.standardize(upper))]
    
    @abstractmethod
    def _match_pattern(self, pattern):
        raise NotImplementedError
    
    def match_pattern(self, pattern):
        return [self.standardize(code) for code in self._match_pattern(self.standardize(pattern))]
    

    
