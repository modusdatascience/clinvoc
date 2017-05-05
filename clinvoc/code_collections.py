from abc import ABCMeta, abstractmethod
from collections import defaultdict
from operator import eq, or_
from toolz.functoolz import curry, flip

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

star = Star()
na = NA()

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
            if not self._is_concrete_key(key):
                raise KeyError()
            else:
                self.dict[key] = v
                self.keys.add(key)
        if levels is None:
            levels = (na,) * key_size
        self.levels = levels
        self.key_size = key_size
        self.level_index = dict(zip(levels, range(self.key_size)))
    
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
        return isinstance(key, tuple) and all(map(flip(isinstance)(basestring), key))

    def _key_match(self, key):
        return filter(curry(eq)(key), self.keys)
    
    def get(self, *args, **kwargs):
        key = self._process_key_args(*args, **kwargs)
        keys = self._key_match(key)
        if not keys:
            raise KeyError()
        return reduce(or_, map(self.dict.get, keys))
    
    def __getitem__(self, key):
        return self.get(*key)
    
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
    
        
