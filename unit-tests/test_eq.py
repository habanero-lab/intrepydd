# Python code to test Intrepydd's eq function by calling func_eq.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_eq.pydd, adapted to Python
def python_eq(A, B):
    C = np.equal(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_eq():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_eq.pydd"])  # Compile func_eq.pydd
    import func_eq
    # Check that Intrepydd & Python implementations of eq behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_eq.func(A, B) == python_eq(A, B)).all()
    assert (func_eq.func(A.astype('float64'), B.astype('float64')) == python_eq(A, B)).all()

