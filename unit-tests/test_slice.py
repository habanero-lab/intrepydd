#test matrix transpose.
#Author: Tong Zhou
import numpy as np

def python_transpose(arr):
    return arr.T

def test_1():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_slice.pydd"])  # Compile func_cos.pydd
    import func_slice as M
    A = np.array([[-24, 15, 0], [1, 2, -3]])
    print(A)
    
    Ar0 = M.getrow(A, 0)    
    print(Ar0)
    Ar0[0] = 100
    print(A)

    Ac0 = M.getcol(A, 0)
    print(Ac0)
    Ac0[0] = 100
    print(A)
    # print(y1.flags['OWNDATA'])

    
    # print(y[:,0])
    # y2 = M.getcol(y, 0)
    # print(len(y2))

    #assert(np.array_equal(y.T, M.transpose_wrapper(y)))
    
    # assert( func_transpose.transpose_wrapper(y).all() == python_transpose(y).all() ) # Tong: this doesn't work

test_1()
