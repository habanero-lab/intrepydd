import numpy as np
import intrepydd
from intrepydd.lang import *


def foo(a: Array(float64, 2), r: Array(float64, 2), b: Array(float64, 2), iters: int32):
    for i in range(iters):
        c = 1.0 / (a @ b)
        b = r @ c
    return b
        

foo1 = intrepydd.compile(foo)

N = 100000
a = np.random.randn(N)
b = np.random.randn(N)
assert np.allclose(foo(a, b), foo1(a, b))