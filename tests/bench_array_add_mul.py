import timeit
import numpy as np
import numba
import intrepydd
from test_array_add_mul import foo


N = 1000000
a = np.random.randn(N)
b = np.random.randn(N)
print('np:', timeit.timeit(lambda: foo(a, b), number=1000) / 1000)

foo_pydd = intrepydd.compile(foo)
foo_nb = numba.jit(foo)
print('pydd:', timeit.timeit(lambda: foo_pydd(a, b), number=1000) / 1000)
print('numba:', timeit.timeit(lambda: foo_nb(a, b), number=1000) / 1000)