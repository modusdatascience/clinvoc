from clinvoc.code_collections import star, CodeCollection, ind
from nose.tools import assert_equal, assert_raises

def test_code_collections():
    # Try it with named levels
    coll = CodeCollection((('1', 'a'), {'1','2'}), 
                          (('1', 'b'), {'3','4'}),
                          (('2', 'a'), {'1','4'}),
                          (('2', 'b'), {'5','2'}),
                          name='coll',
                          levels=['level1', 'level2'])
    assert_equal(coll['1'], {'1', '2', '3', '4'})
    assert_equal(coll['1', star], {'1', '2', '3', '4'})
    assert_equal(coll[star, 'a'], {'1', '2', '4'})
    assert_equal(coll.get(level2='a'), {'1', '2', '4'})
    assert_equal(coll.get('1', level2='a'), {'1', '2'})
    assert_equal(coll.collectlevels('level1'), {('1',): {'1', '2', '3', '4'},
                                                ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels('level2'), {('a',): {'1', '2', '4'},
                                                ('b',): {'2', '3', '4' ,'5'}})
    assert_equal(coll.collectlevels(0), {('1',): {'1', '2', '3', '4'},
                                         ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels(1), {('a',): {'1', '2', '4'},
                                         ('b',): {'2', '3', '4' ,'5'}})
    assert_equal(coll.collectlevels(), {('1', 'a'): {'1','2'}, 
                                        ('1', 'b'): {'3','4'},
                                        ('2', 'a'): {'1','4'},
                                        ('2', 'b'): {'5','2'}})
    
    # Try one without named levels
    coll = CodeCollection((('1', 'a'), {'1','2'}), 
                          (('1', 'b'), {'3','4'}),
                          (('2', 'a'), {'1','4'}),
                          (('2', 'b'), {'5','2'}),
                          )
    assert_equal(coll['1'], {'1', '2', '3', '4'})
    assert_equal(coll['1', star], {'1', '2', '3', '4'})
    assert_equal(coll[star, 'a'], {'1', '2', '4'})
    assert_raises(KeyError, lambda: coll.get(level2='a'))
    assert_raises(KeyError, lambda: coll.get('1', level2='a'))
    assert_equal(coll.collectlevels(0), {('1',): {'1', '2', '3', '4'},
                                         ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels(1), {('a',): {'1', '2', '4'},
                                         ('b',): {'2', '3', '4' ,'5'}})
    assert_raises(KeyError, lambda: coll.collectlevels('level1'))
    assert_raises(KeyError, lambda: coll.collectlevels('level2'))

def test_union():
    coll1 = CodeCollection((('1', 'a'), {'1','2'}), 
                           (('1', 'b'), {'3','4'}),
                           (('2', 'a'), {'1','4'}),
                           (('2', 'b'), {'5','2'}),
                           name='coll1',
                           levels=['level1', 'level2'])
    coll2 = CodeCollection((('1', 'a', '1'), {'1','2'}),
                           (('1', 'a', '2'), {'3','4'}),
                           (('1', 'b', '1'), {'3','5'}),
                           (('1', 'b', '2'), {'6','7'}),
                           (('2', 'a', '1'), {'7','8'}),
                           (('2', 'a', '2'), {'9','10'}),
                           (('2', 'b', '1'), {'11','12'}),
                           (('2', 'b', '2'), {'11','13'}),
                           name='coll2',
                           levels=['level1', 'level2', 'level3'])
    union = coll1.union(coll2)
    assert_equal(union.collectlevels(), {('1', 'a', ind): {'1','2'}, 
                                         ('1', 'b', ind): {'3','4'},
                                         ('2', 'a', ind): {'1','4'},
                                         ('2', 'b', ind): {'5','2'},
                                         ('1', 'a', '1'): {'1','2'},
                                         ('1', 'a', '2'): {'3','4'},
                                         ('1', 'b', '1'): {'3','5'},
                                         ('1', 'b', '2'): {'6','7'},
                                         ('2', 'a', '1'): {'7','8'},
                                         ('2', 'a', '2'): {'9','10'},
                                         ('2', 'b', '1'): {'11','12'},
                                         ('2', 'b', '2'): {'11','13'}})

def test_disjoint_union():
    coll1 = CodeCollection((('1', 'a'), {'1','2'}), 
                           (('1', 'b'), {'3','4'}),
                           (('2', 'a'), {'1','4'}),
                           (('2', 'b'), {'5','2'}),
                           name='coll1',
                           levels=['level1', 'level2'])
    coll2 = CodeCollection((('1', 'a', '1'), {'1','2'}),
                           (('1', 'a', '2'), {'3','4'}),
                           (('1', 'b', '1'), {'3','5'}),
                           (('1', 'b', '2'), {'6','7'}),
                           (('2', 'a', '1'), {'7','8'}),
                           (('2', 'a', '2'), {'9','10'}),
                           (('2', 'b', '1'), {'11','12'}),
                           (('2', 'b', '2'), {'11','13'}),
                           name='coll2',
                           levels=['level1', 'level2', 'level3'])
    union = coll1.disjoint_union(coll2)
    assert_equal(union.collectlevels(), {('coll1', '1', 'a', ind): {'1','2'}, 
                                         ('coll1', '1', 'b', ind): {'3','4'},
                                         ('coll1', '2', 'a', ind): {'1','4'},
                                         ('coll1', '2', 'b', ind): {'5','2'},
                                         ('coll2','1', 'a', '1'): {'1','2'},
                                         ('coll2','1', 'a', '2'): {'3','4'},
                                         ('coll2','1', 'b', '1'): {'3','5'},
                                         ('coll2','1', 'b', '2'): {'6','7'},
                                         ('coll2','2', 'a', '1'): {'7','8'},
                                         ('coll2','2', 'a', '2'): {'9','10'},
                                         ('coll2','2', 'b', '1'): {'11','12'},
                                         ('coll2','2', 'b', '2'): {'11','13'}})

def test_unequal_levels():
    '''
    Test using None to fill in unused levels.
    '''
    coll = CodeCollection((('1', 'a', '1'), {'1','2'}),
                          (('1', 'a', '2'), {'6'}),
                          (('1', 'b', None), {'3','4'}),
                          (('2', 'a', None), {'1','4'}),
                          (('2', 'b', None), {'5','2'}),
                          name='coll',
                          levels=['level1', 'level2', 'level3'])
    assert_equal(coll['1'], {'1', '2', '3', '4', '6'})
    assert_equal(coll['1', star], {'1', '2', '3', '4', '6'})
    assert_equal(coll[star, 'a'], {'1', '2', '4', '6'})
    assert_equal(coll.get(level2='a'), {'1', '2', '4', '6'})
    assert_equal(coll.get('1', level2='a'), {'1', '2', '6'})
    assert_equal(coll.collectlevels('level1'), {('1',): {'1', '2', '3', '4', '6'},
                                                ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels('level2'), {('a',): {'1', '2', '4', '6'},
                                                ('b',): {'2', '3', '4' ,'5'}})
    assert_equal(coll.collectlevels('level3'), {('1',): {'1', '2'},
                                                ('2',): {'6'},
                                                (None,): {'1', '2', '3', '4', '5'},
                                                })
    assert_equal(coll.collectlevels(0), {('1',): {'1', '2', '3', '4', '6'},
                                         ('2',): {'1', '2', '4' ,'5'}})
    assert_equal(coll.collectlevels(1), {('a',): {'1', '2', '4', '6'},
                                         ('b',): {'2', '3', '4' ,'5'}})
    assert_equal(coll.collectlevels(2), {('1',): {'1', '2'},
                                         ('2',): {'6'},
                                         (None,): {'1', '2', '3', '4', '5'},
                                         })
    assert_equal(coll.collectlevels(), {('1', 'a', '1'): {'1','2'}, 
                                        ('1', 'a', '2'): {'6'},
                                        ('1', 'b', None): {'3','4'},
                                        ('2', 'a', None): {'1','4'},
                                        ('2', 'b', None): {'5','2'}})

def test_select():
    coll = CodeCollection((('1', 'a'), {'1','2'}), 
                          (('1', 'b'), {'3','4'}),
                          (('2', 'a'), {'1','4'}),
                          (('2', 'b'), {'5','2'}),
                          name='coll',
                          levels=['level1', 'level2'])
    
    colla = CodeCollection((('1', 'a'), {'1','2'}), 
                          (('2', 'a'), {'1','4'}),
                          name='coll',
                          levels=['level1', 'level2'])
    assert_equal(coll.select(level2='a'), colla)

if __name__ == '__main__':
    import sys
    import nose
    # This code will run the test in this file.'
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0],
                            module_name,
                            '-s', '-v'])
    
    

