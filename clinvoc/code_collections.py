from abc import ABCMeta, abstractmethod
from collections import defaultdict
from operator import eq, or_
from toolz.functoolz import curry, flip, complement
from itertools import chain
from six.moves import reduce
from six import string_types, next
from terminaltables.ascii_table import AsciiTable
from clinvoc.utilities import flatten, tupify
from toolz.curried import keymap, valmap
import csv
from functools import partial
from toolz.dicttoolz import merge
from pyparsing import ParseException

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
    
    @classmethod
    def from_csv(cls, path_or_file, vocabs, vocab_level='vocab', name=None, header=True, ignore=[], **csv_kwargs):
        '''
        Construct CodeCollection(s) from a CSV file.
        
        path_or_file : string or file-like
            Either the path to a CSV file or a file-like object (such as a file or StringIO).
            
        vocabs : dict
            A dict in which the keys are either strings (if a header is available) or column numbers
            and the values are Vocabulary objects.  All cells in the specified fields will be parsed 
            by the specified vocabularies.  The number of code collections returned will be equal to 
            the number of key-value pairs in vocabs.
        
        header : bool or list
            If True, use the first row of the csv as a header.  If False, no header will be used.  If a 
            list, the elements of the list will be used as a header and must match the number of columns 
            in the CSV file.
        
        ignore : list
            A list of strings (if a header is available) or column numbers specifying fields in the CSV 
            that should be ignored.
            
        
        csv_kwargs : dict
            Arguments to pass to csv.reader.
        
        Returns
        -------
        
        
        dict
            The keys are the same those of vocabs and the values are CodeCollection objects.
        
        '''
        # Open file if path provided
        if isinstance(path_or_file, string_types):
            infile = open(path_or_file, 'r')
        else:
            infile = path_or_file
        
        # Figure out header
        reader = csv.reader(infile, **csv_kwargs)
        if header == True:
            header = next(reader)
        else:
            header = header
        header_map = None
        first = True
        
        # Parse the file
        results = list()
        for i, row in enumerate(reader):
            if header == False:
                header = list(range(len(row)))
            if header_map is None:
                header_map = dict(zip(header, list(range(len(row)))))
                header_map = merge(
                                   dict(zip(list(range(len(row))), list(range(len(row))))),
                                   header_map
                                   )
            if first:
                if len(header) != len(row):
                    raise ValueError('Header length does not match row length!')
                ignore_cols = sorted(map(header_map.__getitem__, ignore))
                vocab_keys = list(vocabs.keys())
                vocab_map = dict(zip(vocab_keys, map(header_map.__getitem__, vocab_keys)))
                level_cols = tuple(filter(complement((set(vocab_map.values()) | set(ignore_cols)).__contains__), 
                                             range(len(header))))
                levels = tuple(map(header.__getitem__, level_cols)) + (vocab_level,)
                first = False
            keys = tuple(map(row.__getitem__, level_cols))
            for vocab_key, vocab  in vocabs.items():
                to_parse = row[vocab_map[vocab_key]]
                if not to_parse.strip():
                    results.append((keys + (vocab_key,), set()))
                else:
                    try:
                        results.append((keys + (vocab_key,), vocab.parse(to_parse)))
                    except ParseException:
                        raise ValueError('Unable to parse field %s of row %d: "%s"' % 
                                         (str(vocab_key), i, str(to_parse)))
        
        # Instantiate the CodeCollection objects
        return cls(*results, levels=levels, name=name)
        
        
    
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
    
    
        
            
        
