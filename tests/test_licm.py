import intrepydd
from intrepydd.lang import *


def foo(max_iters: int32, a: Array(int32, 2), b: Array(int32, 2)):
    i = 0
    while i < max_iters:
        a += b + 1
        i += 1
    return a 

foo = intrepydd.compile(foo, licm=True)