#test int32 function (rt.hpp).
#Author: Ankush Mandal (ankush@gatech.edu)
import numpy as np

def test_int32():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_int32.pydd"]) # Compile func_int32.pydd
    import func_int32
    f = np.int32(0)
    assert( func_int32.do_int32() == f)
    val_array = np.array([-17.93, 61.39, -0.0, 0.0], dtype = np.float32)
    for val in val_array:
        assert( func_int32.do_int32_2(float(val)) == np.int32(val) )
