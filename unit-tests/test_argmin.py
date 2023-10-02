# Python code to test Intrepydd's argmin function by calling func_argmin.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;

# Copy of Intrepydd code from func_argmin.pydd, adapted to Python
def python_argmin(x_arr):
    am = x_arr.argmin()
    index_tuple = np.unravel_index(am, x_arr.shape)
    index_arr = np.array(index_tuple)
    return index_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_argmin():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_argmin.pydd"])  # Compile func_argmin.pydd
    import func_argmin
    # Check that Intrepydd & Python implementations of argmin behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
             [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
             [[0, 0, 0], [0, 0, 0], [0, -0.1, 0]]]
    x_np_arr = np.array(x_arr)
    assert (func_argmin.func(x_np_arr) == python_argmin(x_np_arr)).all()
