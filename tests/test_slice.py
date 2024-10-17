import numpy as np
import intrepydd
from intrepydd.lang import *

def foo(a: Array(float64, 1), b: Array(float64, 2), rows: List(int32)):
    for i in rows:
        a += get_row(b, i)
    return a


foo1 = intrepydd.compile(foo, print_cpp=True)

N = 10000
a = np.random.randn(N)
b = np.random.randn(N, N)
rows = np.random.randint(N, size=N//10)
assert np.allclose(foo(a, b, rows), foo1(a, b, rows))   