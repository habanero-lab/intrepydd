# Python code to test Intrepydd's sqrt function by calling func_sqrt.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_sqrt.pydd, adapted to Python
def python_sqrt(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.sqrt(x_arr[i][j]))
        a_arr.append(row);
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_sqrt():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_sqrt.pydd"])  # Compile func_sqrt.pydd
    import func_sqrt
    # Check that Intrepydd & Python implementations of sqrt behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[1, 2, 3],[4, 5, 6]]
    assert (func_sqrt.func(np.array(x_arr).astype('int32')) == python_sqrt(x_arr)).all()

