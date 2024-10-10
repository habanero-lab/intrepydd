# Python code to test Intrepydd's gt function by calling func_gt.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_gt.pydd, adapted to Python
def python_gt(A, B):
    C = np.greater(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_gt():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_gt.pydd"])  # Compile func_gt.pydd
    import func_gt
    # Check that Intrepydd & Python implementations of gt behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    A = np.array([[-1.2, 3.4444444444445, -5.6666666],[7.8, -9.0, 1.2]])
    B = np.array([[3.4,  3.4444444444444, 7.88888888],[9.0, -1.2, 3.4]])    
    assert (func_gt.func(A, B) == python_gt(A, B)).all()
    assert (func_gt.func(A.astype('float64'), B.astype('float64')) == python_gt(A, B)).all()

test_gt()
