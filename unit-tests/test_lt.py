# Python code to test Intrepydd's lt function by calling func_lt.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_lt.pydd, adapted to Python
def python_lt(A, B):
    C = np.less(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_lt():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_lt.pydd"])  # Compile func_lt.pydd
    import func_lt
    # Check that Intrepydd & Python implementations of lt behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_lt.func(A, B) == python_lt(A, B)).all()
    assert (func_lt.func(A.astype('float64'), B.astype('float64')) == python_lt(A, B)).all()

