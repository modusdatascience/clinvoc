import csv
from .base import RegexVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary, \
    LexicographicVocabulary, left_pad, ObservationVocabulary
import os
from .resources import resources
from six import next
import io

def _read_text_file(filename):
    codes = []
    with io.open(filename, mode='rb') as infile:
        reader = csv.reader(infile, delimiter=',', quoting=csv.QUOTE_ALL)
        next(reader)
        while True:
            try:
                line = next(reader)
            except StopIteration:
                break
            except:
                raise
            codes.append(line[0])
    return codes

_all_loinc_codes = _read_text_file(os.path.join(resources, 'LOINC_2.59_Text', 'loinc.csv'))
class LOINC(RegexVocabulary, LexicographicPatternMatchVocabulary, LexicographicRangeFillVocabulary, ObservationVocabulary):
    vocab_name = 'LOINC'
    def __init__(self):
        RegexVocabulary.__init__(self, '[\d\*]{1,5}\-[\d\*]')
        LexicographicVocabulary.__init__(self, map(self.standardize, _all_loinc_codes))
        
    def _standardize(self, code):
        return left_pad(code, 7)
        
