from abc import ABCMeta, abstractmethod
from collections import defaultdict
from operator import eq, or_
from toolz.functoolz import curry, flip
from itertools import chain
from six.moves import reduce
from six import string_types
from terminaltables.ascii_table import AsciiTable
from clinvoc.utilities import flatten, tupify
from toolz.curried import keymap, valmap

class Selector(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError
    
class Star(Selector):
    def __eq__(self, other):
        return True

class NA(Selector):
    def __eq__(self, other):
        return False

class Ind(Selector):
    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

star = Star()
na = NA()
ind = Ind()


class CodeCollection(object):
    def __init__(self, *items, **kwargs):
        assert set(kwargs.keys()) <= {'levels', 'name'}
        self.name = kwargs.get('name', na)
        self.keys = set()
        self.dict = defaultdict(set)
        if 'levels' in kwargs:
            levels = tuple(kwargs['levels'])
            key_size = len(levels)
        else:
            levels = None
            key_size = None
        for k, v in items:
            if key_size is None:
                key_size = len(k)
            elif key_size != len(k):
                raise KeyError('All keys must have the same number of levels.')
            key = tuple(k)
            self.dict[key] = v
            self.keys.add(key)
        if levels is None:
            levels = [Ind() for _ in range(key_size)]
        self.levels = levels
        self.key_size = key_size
        self.level_index = dict(zip(levels, range(self.key_size)))
    
    def to_ascii_table(self):
        table_data = tuple(map(flatten(1), sorted(valmap(', '.join, keymap(flatten(float('inf')), self.dict)).items())))
        header = [[x if isinstance(x, string_types) else '' for x in self.levels] + ['',],]
        table = AsciiTable(header + list(map(list, table_data)), 'Collection: %s' % self.name)
        return table
        
    def __eq__(self, other):
        if not isinstance(other, CodeCollection):
            return NotImplemented
        return ((self.name == other.name) and 
                (self.keys == other.keys) and
                (self.dict == other.dict) and
                (self.levels == other.levels) and
                (self.key_size == other.key_size) and 
                (self.level_index == other.level_index))
    
    def __len__(self):
        return len(self.dict)
    
    def _levels_to_indices(self, levels):
        return [level if isinstance(level, int) else self.level_index[level] for level in levels]
    
    def _levels_kernel(self, levels):
        indices = self._levels_to_indices(levels)
        def _ker(tup):
            return tuple(map(tup.__getitem__, indices))
        return _ker
        
    def _process_key_args(self, *args, **kwargs):
        result = [star] * self.key_size
        used = set()
        for i, arg in enumerate(args):
            result[i] = arg
            used.add(i)
        
        for k, v in kwargs.items():
            i = self.level_index[k]
            if i in used:
                raise KeyError('Key %s appears more than once.' % k)
            else:
                result[i] = v
                used.add(i)
        
        return tuple(result)
    
    def _is_concrete_key(self, key):
        return isinstance(key, tuple) and all(map(flip(isinstance)(string_types), key))

    def _key_match(self, key):
        return filter(curry(eq)(key), self.keys)
    
    def get(self, *args, **kwargs):
        key = self._process_key_args(*args, **kwargs)
        keys = self._key_match(key)
        if not keys:
            raise KeyError()
        return reduce(or_, map(self.dict.get, keys), set())
    
    def __getitem__(self, key):
        return self.get(*key)
    
    def select(self, *args, **kwargs):
        key = self._process_key_args(*args, **kwargs)
        keys = list(self._key_match(key))
        return CodeCollection(*zip(keys, map(self.dict.get, keys)), name=self.name, levels=self.levels)
    
    def collectlevels(self, *levels):
        if not levels:
            levels = self.levels
        ker = self._levels_kernel(levels)
        result_dict = dict()
        for k, v in self.dict.items():
            kernel = ker(k)
            if kernel not in result_dict:
                result_dict[kernel] = set()
            result_dict[kernel].update(v)
        return result_dict
    
    def _unionize(self, size, pieces, offsets=None, filler=None):
        if offsets is None:
            offsets = [0] * len(pieces)
        if filler is None:
            filler = lambda i,j: ind
        items = defaultdict(set)
        for i, k, v in chain(*map(lambda tup: [(tup[0], k_, v_) for k_, v_ in tup[1].dict.items()], enumerate(pieces))):
            k_size = len(k)
            key = tuple([filler(i,j) for j in range(offsets[i])]) + k + tuple([filler(i,j) for j in range(offsets[i] + k_size, size)])
            items[key].update(v)
        return items.items()
    
    def union(self, *others, **kwargs):
        pieces = (self,) + others
        union_size = max(map(flip(getattr)('key_size'), pieces))
        items = self._unionize(union_size, pieces)
        return self.__class__(*items, **kwargs)
    
    def disjoint_union(self, *others, **kwargs):
        assert set(kwargs.keys()) <= {'levels', 'name', 'names'}
        pieces = (self,) + others
        union_size = max(map(flip(getattr)('key_size'), pieces)) + 1
        offsets = [1] * len(pieces)
        if 'names' in kwargs:
            names = kwargs['names']
            del kwargs['name']
        else:
            names = [piece.name for piece in pieces]
        def filler(i, j):
            return names[i] if j == 0 else ind
        items = self._unionize(union_size, pieces, offsets, filler)
        return self.__class__(*items, **kwargs)
    
    
        
            
        
