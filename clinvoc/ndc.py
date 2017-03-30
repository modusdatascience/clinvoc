from .base import Vocabulary
from clinvoc.base import left_pad

class NDC(Vocabulary):
    @staticmethod
    def _fill_range(start, end):
        return [start, end]
    
    @staticmethod
    def _match_pattern(pattern):
        return [pattern]
    
    @staticmethod
    def standardize(code):
        return left_pad(code, 11)