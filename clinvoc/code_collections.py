from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
from operator import eq, or_
from toolz.functoolz import curry, flip

class Selector(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError
    
class Any(Selector):
    def __eq__(self, other):
        return True

star = Any()

# def statictuple(levels, default):
#     def create

def codecoll(name, levels):
    name_ = name
    levels_ = levels
    class _coll(CodeCollection):
        name = name_
        levels = levels_
        levels_set = set(levels)
        level_class = namedtuple(name, levels)
        level_class.__new__.__defaults__ = (star,) * len(levels)
        
    _coll.__name__ = name
    return _coll

def _equal_on_levels(levels):
    def _eq(tup1, tup2):
        for level in levels:
            if tup1[level] != tup2[level]:
                return False
            return True
    return _eq

def _fallback(*funcs):
    def _func(*args, **kwargs):
        for func in funcs:
            try:
                return func(*args, **kwargs)
            except:
                pass
        raise ValueError()
    return _func

def _levels_kernel(levels):
    def _ker(tup):
        return tuple(map(_fallback(tup.__getattribute__, tup.__getitem__), levels))
    return _ker

class CodeCollection(object):
    def __init__(self, *items):
#         self.level_class = namedtuple(self.name, self.levels)
#         self.level_class.__new__.__defaults__ = [Any()] * len(self.levels)
        self.keys = set()
        self.dict = defaultdict(set)
        for k, v in items:
            key = self.level_class(*k)
            if not self._is_concrete_key(key):
                raise KeyError()
            else:
                self.dict[key] = v
                self.keys.add(key)
            
    def _is_concrete_key(self, key):
        return isinstance(key, self.level_class) and all(map(flip(isinstance)(basestring), key))

    def _key_match(self, key):
        return filter(curry(eq)(key), self.keys)
    
    def get(self, *args, **kwargs):
        key = self.level_class(*args, **kwargs)
        keys = self._key_match(key)
        if not keys:
            raise KeyError()
        return reduce(or_, map(self.dict.get, keys))
    
    def __getitem__(self, key):
        return self.get(*key)
    
    def collectlevels(self, *levels):
        if not levels:
            levels = self.levels
        ker = _levels_kernel(levels)
        result_dict = dict()
        for k, v in self.dict.items():
            kernel = ker(k)
            if kernel not in result_dict:
                result_dict[kernel] = set()
            result_dict[kernel].update(v)
        if not set(levels) <= self.levels_set:
            raise KeyError()
        return result_dict
    
#     def set(self, *args, **kwargs):
#         value = args[-1]
#         reduced_args = args[:-1]
#         key = self.level_class(*reduced_args, **kwargs)
#         keys = self._key_match(key)
#         if len(keys) > 1:
#             raise KeyError()
#         self.keys.add(key)
#         self.dict[key] = value
#     
#     def add(self, *args, **kwargs):
#         key = self.level_class(*args, **kwargs)
#         def _add(val):
#             keys = self._key_match(key)
#             if isinstance(val, basestring):
#                 for k in keys:
#                     self.dict
        
        
        
    