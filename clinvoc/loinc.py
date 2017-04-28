import csv
from .base import RegexVocabulary, LexiconVocabulary, create_bisection_range_filler, create_fnmatch_wildcard_matcher, \
    LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary
import os
from .resources import resources
from clinvoc.base import LexicographicVocabulary

def read_text_file(filename):
    codes = []
    with open(filename, 'rb') as infile:
        reader = csv.reader(infile, delimiter=',', quoting=csv.QUOTE_ALL)
        reader.next()
        for line in reader:
            codes.append(line[0])
    return codes

def split_and_sort_codes(codes):
    splitted = [tuple(int(x) for x in code.split('-')) for code in codes]
    splitted.sort()
    return splitted

def join_codes(codes):
    return ['-'.join(map(str, pair)) for pair in codes]

all_splitted_loinc_codes = split_and_sort_codes(read_text_file(os.path.join(resources, 'LOINC_2.59_Text', 'loinc.csv')))
all_loinc_codes = join_codes(all_splitted_loinc_codes)
splitted_range_filler = create_bisection_range_filler(all_splitted_loinc_codes, 'splitted_range_filler')
pattern_matcher = create_fnmatch_wildcard_matcher(all_loinc_codes, 'pattern_matcher')
class LOINC(RegexVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary):
    def __init__(self):
        RegexVocabulary.__init__(self, '[\d\*]{1,5}\-[\d\*]')
        LexiconVocabulary.__init__(self, all_loinc_codes)
        LexicographicVocabulary.__init__(self, all_loinc_codes)
        
    def _standardize(self, code):
        # Remove leading zeroes
        return code.lstrip('0')
        
