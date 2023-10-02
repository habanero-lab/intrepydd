# Python code to test Intrepydd's zeros function by calling func_zeros.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_zeros.pydd, adapted to Python
def python_zeros(shape):
    C = np.zeros(shape, dtype=int)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_zeros():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_zeros.pydd"])  # Compile func_zeros.pydd
    import func_zeros
    # Check that Intrepydd & Python implementations of zeros behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    # Currently we cannot give a shape as a List/Array
    shape = 2
    assert (func_zeros.func(shape) == python_zeros(shape)).all()

