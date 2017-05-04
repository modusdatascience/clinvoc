from clinvoc.code_collections import codecoll, star
from nose.tools import assert_equal

def test_code_collections():
    Coll = codecoll('coll', ['level1', 'level2'])
    coll = Coll((('1', 'a'), {'1','2'}), 
                (('1', 'b'), {'3','4'}),
                (('2', 'a'), {'1','4'}),
                (('2', 'b'), {'5','2'}))
    assert_equal(coll['1'], {'1', '2', '3', '4'})
    assert_equal(coll['1', star], {'1', '2', '3', '4'})
    assert_equal(coll[star, 'a'], {'1', '2', '4'})
    assert_equal(coll.get(level2='a'), {'1', '2', '4'})
    assert_equal(coll.get('1', level2='a'), {'1', '2'})
    assert_equal(coll.collectlevels('level1'), {('1',): {'1', '2', '3', '4'},
                                                ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels('level2'), {('a',): {'1', '2', '4'},
                                                ('b',): {'2', '3', '4' ,'5'}})

if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])
    
    

