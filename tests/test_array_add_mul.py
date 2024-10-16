import numpy as np
import intrepydd
from intrepydd.lang import *

def foo(a: Array(float64, 1), b: Array(float64, 1)):
    return 0.5 * a + b

foo1 = intrepydd.compile(foo)

N = 100000
a = np.random.randn(N)
b = np.random.randn(N)
assert np.allclose(foo(a, b), foo1(a, b))