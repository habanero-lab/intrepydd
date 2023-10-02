#test float32 function (rt.hpp).
#Author: Ankush Mandal (ankush@gatech.edu)
import numpy as np

def test_float32():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_float32.pydd"]) # Compile func_float32.pydd
    import func_float32
    f = (np.float32)(0.0)
    assert( func_float32.do_float32() == f)
    val_array = np.array([-17, 23, 0], dtype = np.int32)
    for val in val_array:
        assert( func_float32.do_float32_2(val) == np.float32(val) )
