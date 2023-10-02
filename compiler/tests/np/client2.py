import cppimport
import numpy as np
import np1_py
import time

pd = cppimport.imp("np2_dd")
print(pd)

def test2():
    xs = np.arange(12).reshape(3,2,2).astype('double')
    #xs = np.arange(12).reshape(3,2,2).astype('float')
    print(xs)
    # t1 = time.time()
    # sum1 = code.sum_3d(xs)
    # t2 = time.time()
    # print('cpp sum:', sum1, t2-t1)
    pd.inc_3d(xs)
    print(xs)

test2()
