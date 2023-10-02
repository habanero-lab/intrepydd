# Python code to test Intrepydd's isnan function by calling func_isnan.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_isnan.pydd, adapted to Python
def python_isnan(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.isnan(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_isnan():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_isnan.pydd"])  # Compile func_isnan.pydd
    import func_isnan
    # Check that Intrepydd & Python implementations of isnan behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[-0.1, 0.2, mt.nan],[-0.5, -1, mt.inf]]
    assert (func_isnan.func(np.array(x_arr)) == python_isnan(x_arr)).all()
