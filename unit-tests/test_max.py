# Python code to test Intrepydd's argmax function by calling func_max.func()
# Author: Mang Yu (mangyu2@illinois.edu)

import numpy as np

# Copy of Intrepydd code from func_argmax.pydd, adapted to Python
def python_max(x_arr):
    max = np.amax(x_arr)
    return max

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_max():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_max.pydd"])  # Compile func_argmax.pydd
    import func_max
    
    # Check that Intrepydd & Python implementations of max behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr_int = np.arange(100, dtype='int32').reshape((10,10))
    x_arr_float = np.arange(100, dtype='float32').reshape((10,10))

    assert (func_max.func_int(x_arr_int) == python_max(x_arr_int)).all()
    assert (func_max.func_float(x_arr_float) == python_max(x_arr_float)).all()
