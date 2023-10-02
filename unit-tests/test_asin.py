# Python code to test Intrepydd's asin function by calling func_asin.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;
import math as mt;

# Copy of Intrepydd code from func_asin.pydd, adapted to Python
def python_asin(x_arr):
    a_arr = []
    for i in range(len(x_arr)):
        row = []
        for j in range(len(x_arr[i])):
            row.append(mt.asin(x_arr[i][j]))
        a_arr.append(row);
    print(a_arr)
    return a_arr

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_asin():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_asin.pydd"])  # Compile func_asin.pydd
    import func_asin
    # Check that Intrepydd & Python implementations of asin behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    x_arr = [[-0.1, 0.2, 0],[-0.5, -1, 1]]
    assert (func_asin.func(np.array(x_arr)) == python_asin(x_arr)).all()
    assert (func_asin.func(np.array(x_arr).astype('float64')) == python_asin(x_arr)).all()

