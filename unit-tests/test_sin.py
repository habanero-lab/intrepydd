# Python code to test Intrepydd's sin function by calling func_sin.func()
# Author: Caleb Voss (cvoss@gatech.edu)

import numpy as np
import math

# Copy of Intrepydd code from func_sin.pydd, adapted to Python
def python_sin(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(math.sin(x_arr[i][j]))
        a_arr.append(row)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_sin():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_sin.pydd"])  # Compile func_sin.pydd
    import func_sin
    # Check that Intrepydd & Python implementations of sin behave the same
    x_arr =  [[-1.1, 2.3, -4],[-2, 0, 3]]
    assert (func_sin.func(np.array(x_arr)) == python_sin(x_arr)).all()
    assert (func_sin.func(np.array(x_arr).astype('float64')) == python_sin(x_arr)).all()

