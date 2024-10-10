import cppimport
import numpy as np
import np1_py
import time

np1_dd = cppimport.imp("np1_dd")
print(np1_dd)

def test2():
    xs = np.arange(12000).reshape(30,20,20).astype('double')
    #xs = np.arange(12).reshape(3,2,2).astype('float')


    # t1 = time.time()
    # sum1 = code.sum_3d(xs)
    # t2 = time.time()
    # print('cpp sum:', sum1, t2-t1)

    t1 = time.time()
    sum1 = np1_dd.sum_3d(xs)
    t2 = time.time()
    print('cpp sum:', sum1, t2-t1)

    t1 = time.time()
    sum2 = np1_py.sum_3d(xs)
    t2 = time.time()
    print('py sum:', sum2, t2-t1)
    
    assert sum1 == sum2

    # code.inc_3d(xs)
    # print('increment each element..')
    # print('cpp sum:', code.sum_3d(xs))
    # print('py sum:', sum_3d(xs))

test2()
