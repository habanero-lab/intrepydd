#test mul function (elementwise).
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def test_mul():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_mul.pydd"]) # Compile func_mul.pydd
    import func_mul
    arr1 = [[-24, 15, 0], [1, 2, -3]]
    arr2 = [[-1, -14, 5], [7, 1, 0]]
    x = np.array(arr1) #default datatype on my machine was int64
    y = np.array(arr2)
    assert( (func_mul.mul_wrapper(x, y) == np.multiply(x, y)).all() )
