# Python code to test Intrepydd's add function by calling func_where.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_where.pydd, adapted to Python
def python_where(A):
    B = np.where(A)
    return B

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_where():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_where.pydd"])  # Compile func_add.pydd
    import func_where
    # Check that Intrepydd & Python implementations of add behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([-1.2, 3.4, -5.6, 7.8, -9.0, 1.2])
    B = np.array([3.4, -5.6, 7.8, 9.0, -1.2, 3.4])
    assert (func_where.func(A < B) == python_where(A < B)).all()
    assert (func_where.func(A.astype('float64') < B.astype('float64')) == python_where(A < B)).all()

test_where()
