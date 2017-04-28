from .base import left_pad, RegexVocabulary, LexiconVocabulary
from operator import add
from toolz.curried import partial
from itertools import product
import os
from clinvoc.resources import resources
import csv
import re


def code_to_tup(code):
    if '-' in code:
        part1, part2, part3 = code.split('-')
        part1 = left_pad(part1, 5)
        part2 = left_pad(part2, 4)
        part3 = left_pad(part3, 2)
        return part1 + part2 + part3
    else:
        raise ValueError
    
def tup_to_code(tup):
    return ''.join(tup)

with open(os.path.join(resources, 'ndctext', 'package.txt')) as infile:
    reader = csv.reader(infile, delimiter='\t')
    reader.next()
    all_ndc_codes = []
    for row in reader:
        try:
            all_ndc_codes.append(code_to_tup(row[2]))
        except:
            print row[2]
            raise
        
all_ndc_codes.sort()
all_ndc_codes = map(tup_to_code, all_ndc_codes)
    
class NDC(RegexVocabulary, LexiconVocabulary): # Diamond inheritance!
    regex = re.compile(r'([\d\*]{1,5}-[\d\*]{1,4}-[\d\*]{1,2})|([\d\*]{4,9}[a-zA-Z\d\*]{1,2})')
    lexicon = set(all_ndc_codes)
    def _match_pattern(self, pattern):
        return set(map(self.standardize, 
                       set(map(partial(reduce, add), product(*map(lambda x: [x] if x != '*' else list(map(str, range(10))), 
                                                                  pattern))))))
    
    def _standardize(self, code):
        if '-' in code:
            return reduce(add, code_to_tup(code))
        else:
            return left_pad(code, 11)
    
    def _fill_range(self, start, end):
        raise NotImplementedError('NDC does not support range filling')
    
    
