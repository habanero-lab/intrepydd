# Python code to test Intrepydd's any function by calling func_any.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_any.pydd, adapted to Python
def python_any(A):
    x = np.any(A)
    return x

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_all():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_any.pydd"])  # Compile func_any.pydd
    import func_any
    # Check that Intrepydd & Python implementations of any behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    boolA = np.array([[True,False],[True,True]])
    assert (func_any.funcBool(boolA) == python_any(boolA))

    intA = np.array([[-1, 4, 5],[2, 3, 4]]);
    assert (func_any.funcInt(intA) == python_any(intA))

    doubleA = np.array([[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]]);
    assert (func_any.funcDouble(doubleA) == python_any(doubleA))
