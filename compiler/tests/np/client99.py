import cppimport
import numpy as np
import time

code = cppimport.imp("module1")
print(code)

def test1():
    xs = np.arange(12).reshape(3,4).astype('float')
    print(xs)
    print("np :", xs.sum())
    print("cpp:", code.sum(xs))
    
    print()
    code.twice(xs)
    print(xs)

def test2():
    xs = np.arange(12000).reshape(30,20,20).astype('float')
    #print(xs)

    t1 = time.time()
    sum1 = code.sum_3d(xs)
    t2 = time.time()
    print('cpp sum:', sum1, t2-t1)

    t1 = time.time()
    sum2 = sum_3d(xs)
    t2 = time.time()
    print('py sum:', sum2, t2-t1)

    code.inc_3d(xs)
    print('increment each element..')
    print('cpp sum:', code.sum_3d(xs))
    print('py sum:', sum_3d(xs))

def sum_3d(xs: np.ndarray):
    sum = 0
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            for k in range(xs.shape[2]):
                sum += xs[i, j, k]
    return sum           

if __name__ == '__main__':
    test2()
