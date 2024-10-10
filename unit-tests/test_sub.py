#Intrepydd code to test sub function (elementwise).
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def test_sub():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_sub.pydd"])  # Compile func_sub.pydd
    import func_sub
    arr1 = [[-24, 15, 0], [1, 2, -3]]
    arr2 = [[-1, -14, 5], [7, 1, 0]]
    x = np.array(arr1) #default datatype on my machine was int64
    y = np.array(arr2)
    assert( (func_sub.sub_wrapper(x, y) == np.subtract(x, y)).all() )
