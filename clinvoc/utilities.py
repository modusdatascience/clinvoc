from multipledispatch.dispatcher import Dispatcher
from collections import Iterable
from six import string_types


tupify = Dispatcher('tupify')

@tupify.register((object, string_types))
def tupify(obj):
    return (obj,)

@tupify.register(Iterable)
def tupify(obj):
    return tuple(obj)

