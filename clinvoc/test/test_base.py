from nose.tools import assert_equal
import clinvoc
from clinvoc.hcpcs import HCPCS

def test_version_tagging():
    assert_equal(HCPCS()._version, clinvoc.__version__)
    
if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])