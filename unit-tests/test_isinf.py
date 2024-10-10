# Python code to test Intrepydd's isinf function by calling func_isinf.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_isinf.pydd, adapted to Python
def python_isinf(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.isinf(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_isinf():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_isinf.pydd"])  # Compile func_isinf.pydd
    import func_isinf
    # Check that Intrepydd & Python implementations of isinf behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[-0.1, 0.2, mt.nan],[-0.5, -1, mt.inf]]
    assert (func_isinf.func(np.array(x_arr)) == python_isinf(x_arr)).all()
