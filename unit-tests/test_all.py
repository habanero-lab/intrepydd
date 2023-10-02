# Python code to test Intrepydd's all function by calling func_all.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_all.pydd, adapted to Python
def python_all(A):
    x = np.all(A)
    return x

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_all():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_all.pydd"])  # Compile func_all.pydd
    import func_all
    # Check that Intrepydd & Python implementations of all behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    boolA = np.array([[True,False],[True,True]])
    assert (func_all.funcBool(boolA) == python_all(boolA))

    intA = np.array([[-1, 4, 5],[2, 3, 4]]);
    assert (func_all.funcInt(intA) == python_all(intA))

    doubleA = np.array([[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]]);
    assert (func_all.funcDouble(doubleA) == python_all(doubleA))
