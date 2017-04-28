from .base import left_pad, RegexVocabulary, LexiconVocabulary
from operator import add
from toolz.curried import partial
from itertools import product
import os
from clinvoc.resources import resources
import csv

def _read_text_file(filename):
    with open(filename, 'rb') as infile:
        reader = csv.reader(infile, delimiter='\t')
        reader.next()
        _all_ndc_codes = []
        for row in reader:
            _all_ndc_codes.append(row[2])
    return _all_ndc_codes

_all_ndc_codes = _read_text_file(os.path.join(resources, 'ndctext', 'package.txt'))
        
class NDC(RegexVocabulary, LexiconVocabulary): # Diamond inheritance!
    def __init__(self):
        RegexVocabulary.__init__(self, r'([\d\*]{1,5}\-[a-zA-Z\d\*]{1,4}\-(([\d\*]{1,2})|([a-zA-Z\*][\d\*]?)|(0[a-zA-Z\*])))|([\d\*]{4,9}[a-zA-Z\d\*]{1,2})')
        LexiconVocabulary.__init__(self, _all_ndc_codes)
    
    def _match_pattern(self, pattern):
        return set(map(self.standardize, 
                       set(map(partial(reduce, add), product(*map(lambda x: [x] if x != '*' else list(map(str, range(10))), 
                                                                  pattern))))))
    
    def _standardize(self, code):
        if '-' in code:
            part1, part2, part3 = code.split('-')
            part1 = left_pad(part1, 5)
            part2 = left_pad(part2, 4)
            part3 = left_pad(part3, 2)
            return part1 + part2 + part3
        else:
            return left_pad(code, 11)
    
    def _fill_range(self, start, end):
        raise NotImplementedError('NDC does not support range filling')
    
    
