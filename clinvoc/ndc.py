from .base import left_pad, RegexVocabulary, create_vocabulary_checker,\
    LexiconVocabulary
from operator import add
from toolz.functoolz import compose
from toolz.curried import partial
from itertools import product
import os
from clinvoc.resources import resources
import csv

pattern = r'([\d\*]{1,5}-[\d\*]{1,4}-[\d\*]{1,2})|([\d\*]{1,11})'

# def tup_to_code(tup):
#     return '-'.join(tup)

# def code_to_tup(code):
#     if '-' in code:
#         part1, part2, part3 = code.split('-')
#         part1 = left_pad(part1, 5)
#         part2 = left_pad(part2, 4)
#         part3 = left_pad(part3, 2)
#         return part1, part2, part3
#     else:
#         padded = left_pad(code, 11)
#         
#         has_letter = not code[-2].isdigit()
#         return int(padded[:5], int(padded[5:9]), code[-2] if has_letter else '', int(padded[10:]) if has_letter else int(padded[9:])

# def ints_to_int(ints):
#     int1, int2, int3 = ints
#     return (int1 * int(1e6)) + (int2 * int(1e2)) + int3

# def int_to_code(integer):
#     padded = left_pad(str(integer), 11)
#     return '-'.join([padded[:5], padded[5:9], padded[9:]])

def match_ndc_pattern(pattern):
    return set(map(self.standardize, set(map(partial(reduce, add), product(*map(lambda x: [x] if x != '*' else list(map(str, range(10))), pattern))))))

# def fill_ndc_range(lower, upper):
#     lower_ = ints_to_int(code_to_ints(lower))
#     upper_ = ints_to_int(code_to_ints(upper))
#     return set(map(int_to_code, range(lower_, upper_+1)))

# def standardize_ndc_code(code):
#     return tup_to_code(code_to_tup(code))

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
    regex = r'([\d\*]{1,5}-[\d\*]{1,4}-[\d\*]{1,2})|([\d\*]{1,9}[a-zA-Z\d\*]{1,2})'
    lexicon = set(all_ndc_codes)
    def _match_pattern(self, pattern):
        return set(map(self.standardize, 
                       set(map(partial(reduce, add), product(*map(lambda x: [x] if x != '*' else list(map(str, range(10))), 
                                                                  pattern))))))
    
    def standardize(self, code):
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
    
    
