import tracemalloc
import numpy as np
from memory_profiler import memory_usage
from memory_profiler import profile
import gc

#@profile
def foo(a, r, b, iters):
    for i in range(iters):
        #mem_usage_before = memory_usage()
        c = a @ b
        b = r @ (1.0 / c)
        #mem_usage_after = memory_usage()
        #print(f"Memory usage before: {mem_usage_before}, after: {mem_usage_after}")
    return b

#@profile
def foo1(a, r, b, iters):
    c = np.empty_like(a)
    t = np.empty_like(c)
    for i in range(iters):
        #mem_usage_before = memory_usage()
        
        # c = a @ b
        np.matmul(a, b, out=c) 
        # b = r @ c
        np.divide(1.0, c, out=c)
        np.matmul(r, c, out=b)
        
        #mem_usage_after = memory_usage()

        #print(f"Memory usage before: {mem_usage_before}, after: {mem_usage_after}")
    return b


# Example usage with dummy arrays
a = np.random.rand(2000, 2000)
r = np.random.rand(2000, 2000)
b = np.random.rand(2000, 2000)
iters = 3

assert np.allclose(foo(a, r, b, iters), foo1(a, r, b, iters))

#foo(a, r, b, iters)
#foo1(a, r, b, iters)
import timeit
print(timeit.timeit(lambda: foo(a, r, b, iters), number=30) / 30)
print(timeit.timeit(lambda: foo1(a, r, b, iters), number=30) / 30)
