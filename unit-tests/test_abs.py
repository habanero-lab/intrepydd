# Python code to test Intrepydd's abs function by calling func_abs.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;

# Copy of Intrepydd code from func_abs.pydd, adapted to Python
def python_abs(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(abs(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_abs():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_abs.pydd"])  # Compile func_abs.pydd
    import func_abs
    # Check that Intrepydd & Python implementations of abs behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr =  [[-1.1, 2.3, -4],[-2, 0, 3]]
    assert (func_abs.func(np.array(x_arr)) == python_abs(x_arr)).all()
    assert (func_abs.func(np.array(x_arr).astype('float64')) == python_abs(x_arr)).all()

