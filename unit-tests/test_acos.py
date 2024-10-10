# Python code to test Intrepydd's acos function by calling func_acos.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_acos.pydd, adapted to Python
def python_acos(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.acos(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_acos():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_acos.pydd"])  # Compile func_acos.pydd
    import func_acos
    # Check that Intrepydd & Python implementations of acos behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[-0.1, 0.2, 0],[-0.5, -1, 1]]
    assert (func_acos.func(np.array(x_arr)) == python_acos(x_arr)).all()
    assert (func_acos.func(np.array(x_arr).astype('float64')) == python_acos(x_arr)).all()

