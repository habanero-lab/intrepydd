# Python code to test Intrepydd's empty function by calling func_empty.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_empty.pydd, adapted to Python
def python_empty(shape):
    C = np.empty(shape, dtype=int)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_empty():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_empty.pydd"])  # Compile func_empty.pydd
    import func_empty
    # Check that Intrepydd & Python implementations of empty behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    # Currently we cannot give a shape as a List/Array
    shape = 2
    assert (func_empty.func(shape).shape == python_empty(shape).shape)

    shape = [2,3]
    assert (func_empty.func1(shape).shape == python_empty(shape).shape)

    shape = [2,3]
    print(func_empty.empty_bool(shape))

test_empty()    
