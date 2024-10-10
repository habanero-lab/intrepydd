# Python code to test Intrepydd's exp function by calling func_log.func()
# Author: Mang Yu (mangyu2@illinois.edu)

import numpy as np

# numpy implementation of log
def python_log(x_arr, y_arr):
    a_arr = np.log(x_arr)/np.log(y_arr)
    print(a_arr)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_exp():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_log.pydd"])  # Compile func_log.pydd
    import func_log

    # Check that Intrepydd & Python implementations of exp behave the same
    x_arr =  np.array([[5, 1.57, 57], [1.57, 3.2, 2]], dtype='float64')
    y_arr =  np.array([[2, 3, 4], [2, 3, 4]], dtype='int32')

    assert (func_log.func(x_arr, y_arr) == python_log(x_arr, y_arr)).all()

