# Python code to test Intrepydd's le function by calling func_le.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_le.pydd, adapted to Python
def python_le(A, B):
    C = np.less_equal(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_le():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_le.pydd"])  # Compile func_le.pydd
    import func_le
    # Check that Intrepydd & Python implementations of le behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_le.func(A, B) == python_le(A, B)).all()
    assert (func_le.func(A.astype('float64'), B.astype('float64')) == python_le(A, B)).all()

