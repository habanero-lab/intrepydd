# Python code to test Intrepydd's cos function by calling func_cos.func()
# Author: Caleb Voss (cvoss@gatech.edu)

import numpy as np
import math

# Copy of Intrepydd code from func_cos.pydd, adapted to Python
def python_cos(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(math.cos(x_arr[i][j]))
        a_arr.append(row)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_cos():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_cos.pydd"])  # Compile func_cos.pydd
    import func_cos
    # Check that Intrepydd & Python implementations of cos behave the same
    x_arr =  [[0, 1.57, 2],[-3.1415, 5.7e-12, 3]]
    assert (func_cos.func(np.array(x_arr)) == python_cos(x_arr)).all()
    assert (func_cos.func(np.array(x_arr).astype('float64')) == python_cos(x_arr)).all()

