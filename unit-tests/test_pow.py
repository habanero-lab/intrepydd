# Python code to test Intrepydd's pow function by calling func_pow.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_pow.pydd, adapted to Python
def python_pow(A, B):
    C = np.power(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_pow():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_pow.pydd"])  # Compile func_pow.pydd
    import func_pow
    # Check that Intrepydd & Python implementations of pow behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([1.2, 3.4, 5.6])
    B = np.array([7.8, 9.0, 1.2])    
    assert (func_pow.func(A, B) == python_pow(A, B)).all()
    assert (func_pow.func(A.astype('float64'), B.astype('float64')) == python_pow(A, B)).all()

