#Intrepydd code to test min function.
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def test_min():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_min.pydd"])  # Compile func_min.pydd
    import func_min
    arr_2d = [[-24.5, 7.1], [6.3, 0.0]]
    y = np.array(arr_2d) #default datatype on my machine was float64
    assert( func_min.min_wrapper(y) == min(map(min, y)) )

