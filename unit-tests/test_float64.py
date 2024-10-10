#test float64 function (rt.hpp).
#Author: Ankush Mandal (ankush@gatech.edu)
import numpy as np

def test_float64():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_float64.pydd"]) # Compile func_float64.pydd
    import func_float64

    f = (np.float64)(0.0)
    assert( func_float64.do_float64() == f)

    val_array = np.array([-17, 23, 0], dtype = np.int32)
    for val in val_array:
        assert( func_float64.do_float64_2(val) == np.float64(val) )

    val_array = np.array([-17.45, 23.49, float.fromhex('0x1p-126'), float.fromhex('0x1p-127'), float.fromhex('0x1p-149'), -0.0, 0.0], dtype = np.float32)
    for val in val_array:
        assert( func_float64.do_float64_3(float(val)) == np.float64(val) )

    val_array = np.array([-8589934592, 0xffffffffff, 0], dtype = np.int64)
    for val in val_array:
        assert( func_float64.do_float64_4(val) == np.float64(val) )
