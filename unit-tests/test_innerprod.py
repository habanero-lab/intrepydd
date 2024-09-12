# Python code to test Intrepydd's innerprod function by calling func_innerprod.func()
# Author: Sriraj (sriraj@gatech.edu)

import numpy as np;

# Copy of Intrepydd code from func_innerprod.pydd, adapted to Python
def python_innerprod(A, B):
    C = np.inner(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_innerprod():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_innerprod.pydd"])  # Compile func_innerprod.pydd
    import func_innerprod
    # Check that Intrepydd & Python implementations of innerprod behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    n = 1000
    A = np.random.randn(n)
    B = np.random.randn(n)
    assert(np.allclose(func_innerprod.func(A, B), python_innerprod(A, B)))

