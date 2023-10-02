# Python code to test Intrepydd's logical_not function by calling func_logical_not.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;

# Copy of Intrepydd code from func_logical_not.pydd, adapted to Python
def python_logical_not(A):
    C = np.logical_not(A)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_logical_not():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_logical_not.pydd"])  # Compile func_logical_not.pydd
    import func_logical_not
    # Check that Intrepydd & Python implementations of logical_not behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = 3;
    B = np.array([[3,2.1,0],[1,0, 2.2]])
    assert (func_logical_not.func1(A) == python_logical_not(A)).all()
    assert (func_logical_not.func2(B) == python_logical_not(B)).all()

