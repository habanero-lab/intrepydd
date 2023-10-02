# Python code to test Intrepydd's add function by calling func_add.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_add.pydd, adapted to Python
def python_add(A, B):
    C = np.add(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_add():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_add.pydd"])  # Compile func_add.pydd
    import func_add
    # Check that Intrepydd & Python implementations of add behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    B = np.array([[3.4, -5.6, 7.8],[9.0, -1.2, 3.4]])    
    assert (func_add.func(A, B) == python_add(A, B)).all()
    assert (func_add.func(A.astype('float64'), B.astype('float64')) == python_add(A, B)).all()

test_add()
