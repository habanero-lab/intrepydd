# Python code to test Intrepydd's atan function by calling func_atan.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_atan.pydd, adapted to Python
def python_atan(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.atan(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_atan():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_atan.pydd"])  # Compile func_atan.pydd
    import func_atan
    # Check that Intrepydd & Python implementations of atan behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[-0.1, 0.2, 0],[-0.5, -1, 1]]
    assert (func_atan.func(np.array(x_arr)) == python_atan(x_arr)).all()
    assert (func_atan.func(np.array(x_arr).astype('float64')) == python_atan(x_arr)).all()

