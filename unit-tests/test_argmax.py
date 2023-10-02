# Python code to test Intrepydd's argmax function by calling func_argmax.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;

# Copy of Intrepydd code from func_argmax.pydd, adapted to Python
def python_argmax(x_arr):
    am = x_arr.argmax()
    index_tuple = np.unravel_index(am, x_arr.shape)
    index_arr = np.array(index_tuple)
    return index_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_argmax():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_argmax.pydd"])  # Compile func_argmax.pydd
    import func_argmax
    # Check that Intrepydd & Python implementations of argmax behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
             [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
             [[0, 0, 0], [0, 0, 0], [0, 0.1, 0]]]
    x_np_arr = np.array(x_arr)
    assert np.array_equal(func_argmax.func(x_np_arr), python_argmax(x_np_arr))
    assert (func_argmax.func(x_np_arr) == python_argmax(x_np_arr)).all()
