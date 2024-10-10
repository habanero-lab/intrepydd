#Intrepydd code to test prod function (Reduction).
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def python_prod(arr):
    return np.prod(arr)

def test_prod():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_prod.pydd"])  # Compile func_prod.pydd
    import func_prod
    arr_1d = [-15, -5, 2, 7]
    x = np.array(arr_1d) #default datatype on my machine was int64
    assert( func_prod.prod_wrapper(x) == python_prod(x) )
    arr_2d = [[-24, 7], [6, 2]]
    y = np.array(arr_2d) #default datatype on my machine was int64
    assert( func_prod.prod_wrapper(y) == python_prod(y) )
