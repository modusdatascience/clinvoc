# coding: utf-8
from nose.tools import assert_equal  # @UnresolvedImport
from clinvoc.icd10 import ICD10CM, ICD10PCS
from clinvoc.icd9 import ICD9CM, ICD9PCS
from clinvoc.ubrev import UBREV

def test_icd10_cm():
    vocab = ICD10CM()
    assert_equal(vocab.parse('‘Z00.00’, ‘Z00.01’, ‘Z00.121’, ‘Z00.129’, ‘Z00.8’'), 
                 {'Z00.00', 'Z00.01', 'Z00.121', 'Z00.129', 'Z00.8'})
    assert_equal(vocab.parse('‘Z00.00-Z00.01’, ‘Z00.121’, ‘Z00.129’, ‘Z00.8’'), 
                 {'Z00.00', 'Z00.01', 'Z00.121', 'Z00.129', 'Z00.8'})
    assert_equal(vocab.parse('‘Z00.00-Z00.0*’, ‘Z00.121’, ‘Z00.129’, ‘Z00.8’'), 
                 {'Z00.00', 'Z00.01', 'Z00.121', 'Z00.129', 'Z00.8'})
    assert_equal(vocab.parse('‘Z00.0*-Z00.0*’, ‘Z00.121’, ‘Z00.129’, ‘Z00.8’'), 
                 {'Z00.00', 'Z00.01', 'Z00.121', 'Z00.129', 'Z00.8'})
    assert_equal(vocab.parse('  Z00.00 "Z00.01\'  Z00.121    Z00.129 Z00.8'), 
                 {'Z00.00', 'Z00.01', 'Z00.121', 'Z00.129', 'Z00.8'})

def test_icd10_pcs():
    vocab = ICD10PCS()
    assert_equal(vocab.parse("'0210093', '0210098', '0210099', '0211093', '0211098'"), 
                 {'021.0093', '021.0098', '021.0099', '021.1093', '021.1098'})
    assert_equal(vocab.parse("'0210093', '0210098 - 0210099', '0211093', '0211098'"), 
                 {'021.0093', '021.0098', '021.0099', '021.1093', '021.1098'})
    assert_equal(vocab.parse("'0210093', '021009*', '0211093', '0211098'"), 
                 {'021.0093', '021.0098', '021.0099', '021.1093', '021.1098', '021.009C',
                  '021.009F', '021.009W'})

def test_icd9_cm():
    vocab = ICD9CM()
    assert_equal(vocab.parse("250.33, 250.40, 250.41, 250.42, 250.43,"),
                 {'250.33', '250.40', '250.41', '250.42', '250.43'})
    assert_equal(vocab.parse("250.33, 250.40-250.43,"),
                 {'250.33', '250.40', '250.41', '250.42', '250.43'})
    assert_equal(vocab.parse("250.33, 250.4*,"),
                 {'250.33', '250.40', '250.41', '250.42', '250.43'})

def test_icd9_pcs():
    vocab = ICD9PCS()
    assert_equal(vocab.parse("'79.27', '79.33', '79.37', '79.63', '79.67'"),
                 {'79.27', '79.33', '79.37', '79.63', '79.67'})
    assert_equal(vocab.parse("'79.37', '79.33-79.37', '79.63', '79.67'"),
                 {'79.33', '79.37', '79.63', '79.67', '79.36', '79.34', '79.35'})
    assert_equal(vocab.parse("'79.37', '79.3*', '79.63', '79.67'"),
                 {'79.33', '79.37', '79.63', '79.67', '79.36', '79.34', '79.35', 
                  '79.32', '79.39', '79.30', '79.31', '79.38'})
    
def test_ubrev():
    vocab = UBREV()
    assert_equal(vocab.parse('116'), 
                 {'0116'})
    assert_equal(vocab.parse('116-118'), 
                 {'0116', '0117', '0118'})

if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])