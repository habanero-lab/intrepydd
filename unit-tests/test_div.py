#test div function (elementwise).
#Author: Ankush Mandal (ankush@gatech.edu)
import numpy as np

def test_div():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_div.pydd"]) # Compile func_div.pydd
    import func_div
    arr1 = np.array([[-24, 15, 0], [0, -4, 2]], dtype = np.int32)
    arr2 = np.array([[-1, -14, 5], [-3, 7, 1]], dtype = np.int32)
    assert( func_div.do_div(arr1, arr2).all() == np.divide(arr1, arr2).all() )
    arr1 = np.array([-6.5, 9.2, 0.0, -0.0], dtype = np.float64)
    val_array = np.array([-2.3, 1.7], dtype = np.float64)
    
    for val in val_array:
        assert np.array_equal(func_div.do_div2(arr1, val), np.divide(arr1, val))
        #assert( func_div.do_div2(arr1, val).all() == np.divide(arr1, val).all() )
