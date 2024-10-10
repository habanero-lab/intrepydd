import cppimport
import numpy as np
import demos
import time
import ctypes

print('\n================= demo1 =================')
# Invoke the Intrepydd function demo1()
demos.demo1()

xs = np.arange(1000000).reshape(100,100,100).astype('double')
print('\n================= demo2 =================')
print('before calling demo2:')

t1 = time.time()
sum1 = demos.sum(xs)
t2 = time.time()
print('elapsed time for sum:', t2-t1, 's')
print('sum:', sum1)

print('\n================= demo3 =================')
# Invoke the Intrepydd function demo2() with a Numpy array
# demo2() modifys the Numpy array in-place, without copying
t1 = time.time()
demos.inc(xs, 1.0)
t2 = time.time()
print('elapsed time for increment:', t2-t1, 's')


print('after calling demo2:')
t1 = time.time()
sum1 = demos.sum(xs)
t2 = time.time()
print('elapsed time for sum:', t2-t1, 's')
print('sum:', sum1)


print('\n================= demo4 =================')
a = demos.create_array()
print("create an numpy array in Intrepydd...")
print(a)

s = demos.do_sum()
print('sum in pydd:', s)
