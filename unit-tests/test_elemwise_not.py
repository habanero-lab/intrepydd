# Python code to test Intrepydd's elemwise_not function by calling func_elemwise_not.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_elemwise_not.pydd, adapted to Python
def python_elemwise_not(A):
    C = np.logical_not(A)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_elemwise_not():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_elemwise_not.pydd"])  # Compile func_elemwise_not.pydd
    import func_elemwise_not
    # Check that Intrepydd & Python implementations of elemwise_not behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[True,False],[True,True]])
    assert (func_elemwise_not.func(A) == python_elemwise_not(A)).all()

