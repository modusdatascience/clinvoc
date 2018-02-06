from clinvoc.code_collections import CodeCollection
from clinvoc.code_maps import CodeMap
from nose.tools import assert_equal

def test_code_maps():
    coll = CodeCollection(
                          (('a', 'ICD9CM'), {'709.9', '01.0'}),
                          (('a', 'ICD10CM'), {'L98.9', 'A00.0'}),
                          (('b', 'ICD9CM'), {'709.9', '02.0'}),
                          (('b', 'ICD10CM'), {'L98.9', 'A01.00'}),
                          )
    code_map = CodeMap.from_code_collection(coll)
    assert_equal(code_map['ICD9CM', '001.0'], {('a',),})
    assert_equal(code_map['ICD10CM', '001.0'], set())
    assert_equal(code_map['ICD10CM', 'A00.0'], {('a',),})
    assert_equal(code_map['ICD10CM', 'L98.9'], {('a',), ('b',)})
    assert_equal(code_map['ICD9CM', '709.9'], {('a',), ('b',)})

if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])
    
    