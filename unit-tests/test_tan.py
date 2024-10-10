# Python code to test Intrepydd's tan function by calling func_tan.func()
# Author: Caleb Voss (cvoss@gatech.edu)

import numpy as np
import math

# Copy of Intrepydd code from func_tan.pydd, adapted to Python
def python_tan(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(math.tan(x_arr[i][j]))
        a_arr.append(row)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_tan():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_tan.pydd"])  # Compile func_tan.pydd
    import func_tan
    # Check that Intrepydd & Python implementations of tan behave the same
    x_arr =  [[0, 1.57, 1.58],[-1.57, -1.58, 3]]
    assert (func_tan.func(np.array(x_arr)) == python_tan(x_arr)).all()
    assert (func_tan.func(np.array(x_arr).astype('float64')) == python_tan(x_arr)).all()

