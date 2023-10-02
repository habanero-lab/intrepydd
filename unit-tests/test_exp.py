# Python code to test Intrepydd's exp function by calling func_exp.func()
# Author: Caleb Voss (cvoss@gatech.edu)

import numpy as np
import math

# Copy of Intrepydd code from func_exp.pydd, adapted to Python
def python_exp(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(math.exp(x_arr[i][j]))
        a_arr.append(row)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_exp():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_exp.pydd"])  # Compile func_exp.pydd
    import func_exp
    # Check that Intrepydd & Python implementations of exp behave the same
    x_arr =  [[0, 1.57, 57],[-1.57, 5.7e-12, 3]]
    assert (func_exp.func(np.array(x_arr)) == python_exp(x_arr)).all()
    assert (func_exp.func(np.array(x_arr).astype('float64')) == python_exp(x_arr)).all()

