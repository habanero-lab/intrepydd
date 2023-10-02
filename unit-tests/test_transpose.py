#test matrix transpose.
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def python_transpose(arr):
    return arr.T

def test_transpose():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_transpose.pydd"])  # Compile func_cos.pydd
    import func_transpose as M
    arr = [[-24, 15, 0], [1, 2, -3]]
    y = np.array(arr)
    print(y[0])
    y1 = M.getrow(y, 0)
    print(y1.flags['OWNDATA'])

    
    print(y[:,0])
    y2 = M.getcol(y, 0)
    print(len(y2))

    assert(np.array_equal(y.T, M.transpose_wrapper(y)))
    
    # assert( func_transpose.transpose_wrapper(y).all() == python_transpose(y).all() ) # Tong: this doesn't work

test_transpose()
