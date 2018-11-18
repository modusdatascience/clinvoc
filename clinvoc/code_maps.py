from clinvoc.code_systems import code_system_standardizers

class CodeMap(object):
    def __init__(self, code_sets, code_system_level=-1, standardizers=None, **kwargs):
        self.code_sets = code_sets
        if standardizers is not None:
            self.standardizers = standardizers
        else:
            self.standardizers = code_system_standardizers(**kwargs)
        index = dict()
        for tup, code_set in self.code_sets.items():
            code_system = tup[code_system_level]
            value = tup[:code_system_level] + tup[(code_system_level):][1:]
            index[code_system] = index.get(code_system, dict())
            for code in map(self.standardizers[code_system], code_set):
                index[code_system][code] = index[code_system].get(code, set())
                index[code_system][code].add(value)
        self.index = index
    
    @classmethod
    def from_code_collection(cls, collection, levels=tuple(), code_system_level=-1, 
                             standardizers=None, **kwargs):
        return cls(collection.collectlevels(*levels), code_system_level=code_system_level,
                   standardizers=standardizers, **kwargs)
    
    def __getitem__(self, arg):
        code_system, code = arg
        try:
            return self.index[code_system][self.standardizers[code_system](code)]
        except KeyError:
            return set()
        except ValueError:
            raise
    
    
        