# Python code to test Intrepydd's ge function by calling func_ge.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_ge.pydd, adapted to Python
def python_ge(A, B):
    C = np.greater_equal(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_ge():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_ge.pydd"])  # Compile func_ge.pydd
    import func_ge
    # Check that Intrepydd & Python implementations of ge behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_ge.func(A, B) == python_ge(A, B)).all()
    assert (func_ge.func(A.astype('float64'), B.astype('float64')) == python_ge(A, B)).all()

