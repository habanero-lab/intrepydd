#test int64 function (rt.hpp).
#Author: Ankush Mandal (ankush@gatech.edu)
import numpy as np

def test_int64():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_int64.pydd"]) # Compile func_int64.pydd
    import func_int64

    f = (np.int64)(0.0)
    assert( func_int64.do_int64() == f)

    val_array = np.array([-17, 23, 0], dtype = np.int32)
    for val in val_array:
        assert( func_int64.do_int64_2(val) == np.int64(val) )

    val_array = np.array([-17.45, 23.49, -0.0, 0.0], dtype = np.float32)
    for val in val_array:
        assert( func_int64.do_int64_3(float(val)) == np.int64(val) )

    val_array = np.array([-8589934592.987, 567534512675.6008, -0.0, 0.0], dtype = np.float64)
    for val in val_array:
        assert( func_int64.do_int64_4(val) == np.int64(val) )
