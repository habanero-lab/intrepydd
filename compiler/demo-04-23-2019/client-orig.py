import cppimport
import numpy as np
import time
import ctypes

def demo1():
    '''
    Print an array of ints.
    '''
    a = [1,2,3]
    for i in a:
        print(i)

        
def demo2(xs, value):
    '''
    Increment every element in array `xs` by `value`.
    Assume the array is 3d.
    '''
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            for k in range(xs.shape[2]):
                xs[i, j, k] += value

def demo3(xs):
    '''
    Sum up all elements in 3d array `xs`
    '''
    sum = 0
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            for k in range(xs.shape[2]):
                sum += xs[i, j, k]
    return sum


print('\n================= demo1 =================')
demo1() # invoke the Intrepydd function


print('\n================= demo2 =================')
xs = np.arange(12).reshape(2,2,3).astype('double')

print('before calling demo2:', xs)

demo2(xs, 3.0)
print('after calling demo2:', xs)



print('\n================= demo3 =================')
xs = np.arange(1000000).reshape(100,100,100).astype('double')
t1 = time.time()
#sum1 = demo3(xs)
sum1 = np.sum(xs)
t2 = time.time()
print('sum:', sum1)
print('elapsed time for sum:', t2-t1, 's')

