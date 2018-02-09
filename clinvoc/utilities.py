from multipledispatch.dispatcher import Dispatcher
from collections import Iterable
from six import string_types

tupify = Dispatcher('tupify')
@tupify.register(Iterable)
def tupify_iterable(obj):
    return tuple(obj)

flatten = Dispatcher('flatten')
@flatten.register(object, Iterable)
def flatten_iterable(depth, arg):
    if depth > 0:
        return sum(tuple(tupify(flatten(depth-1, x)) for x in arg), tuple())
    else:
        return arg

def tup_of_obj(x):
    return (x,)

tupify.register((object, string_types))(tup_of_obj)
flatten.register(object, (object, string_types))(lambda x,y: tup_of_obj(y))
# Currying for flatten
flatten.register(object)(lambda x: (lambda y: flatten(x, y)))
