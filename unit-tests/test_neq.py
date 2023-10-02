# Python code to test Intrepydd's neq function by calling func_neq.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_neq.pydd, adapted to Python
def python_neq(A, B):
    C = np.not_equal(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_neq():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_neq.pydd"])  # Compile func_neq.pydd
    import func_neq
    # Check that Intrepydd & Python implementations of neq behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_neq.func(A, B) == python_neq(A, B)).all()
    assert (func_neq.func(A.astype('float64'), B.astype('float64')) == python_neq(A, B)).all()

