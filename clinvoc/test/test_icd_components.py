from nose.tools import assert_equal
from clinvoc.icd import _expand_icd_codes


def test_expand_icd9cm_codes():
    codes = ['123.45', '678.91']
    expanded = _expand_icd_codes(codes)
    assert_equal(expanded, ['123', '123.4', '123.45', '678',
                            '678.9', '678.91'])

if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])