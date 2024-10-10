# Python code to test Intrepydd's arraysub function by calling func_arraysub.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_arraysub.pydd, adapted to Python
def python_arraysub(A, i, j):
    x = A[i,j]
    return x

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_arraysub():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_arraysub.pydd"])  # Compile func_arraysub.pydd
    import func_arraysub
    # Check that Intrepydd & Python implementations of arraysub behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    i = 1
    j = 2
    assert (func_arraysub.func(A, 1, 2) == python_arraysub(A, 1, 2))
    assert (func_arraysub.func(A.astype('float64'), 1, 2) == python_arraysub(A, 1, 2))

