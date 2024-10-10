# Python code to test Intrepydd's allclose function by calling func_allclose.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_allclose.pydd, adapted to Python
def python_allclose(A, u):
    x = np.all(A <= abs(u))
    return x

# Callcloseed by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_allclose():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_allclose.pydd"])  # Compile func_allclose.pydd
    import func_allclose
    # Check that Intrepydd & Python implementations of allclose behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[1.2, -3.4, 5.6],[7.8, -9.0, 1.2]]);
    u = 9.0
    assert (func_allclose.func(A, u) == python_allclose(A, u))
    assert (func_allclose.func(A.astype('float64'), u) == python_allclose(A, u)).all()
