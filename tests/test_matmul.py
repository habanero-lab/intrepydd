import numpy as np
import timeit
import intrepydd
from intrepydd.lang import *

def foo(a: Array(float64, 2), b: Array(float64, 2), c: Array(float64, 2)) -> Array(float64, 2):
    return c / (a @ b)


foo1 = intrepydd.compile(foo)

N = 2000
a = np.random.randn(N, N)
b = np.random.randn(N, N)
c = np.random.randn(N, N)
assert np.allclose(foo(a, b, c), foo1(a, b, c))
print(timeit.timeit(lambda: foo(a, b, c), number=10) / 10)
print(timeit.timeit(lambda: foo1(a, b, c), number=10) / 10)