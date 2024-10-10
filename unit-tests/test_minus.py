# Python code to test Intrepydd's minus function by calling func_minus.func()
# Author: Caleb Voss (cvoss@gatech.edu)

import numpy as np

# Copy of Intrepydd code from func_minus.pydd, adapted to Python
def python_minus(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(-x_arr[i][j])
        a_arr.append(row)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_minus():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_minus.pydd"])  # Compile func_minus.pydd
    import func_minus
    # Check that Intrepydd & Python implementations of minus behave the same
    x_arr =  [[0, 1.57, 57],[-1.57, 5.7e-12, 3]]
    assert (func_minus.func(np.array(x_arr)) == python_minus(x_arr)).all()
    assert (func_minus.func(np.array(x_arr).astype('float64')) == python_minus(x_arr)).all()

