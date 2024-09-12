# Python code to test Intrepydd's matmult function by calling func_matmult.func()
# Author: Akihiro Hayashi (ahayashi@rice.edu)

import numpy as np;

# Copy of Intrepydd code from func_matmult.pydd, adapted to Python
def python_matmult(A, B):
    C = np.matmul(A, B)
    return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_matmult():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_matmult.pydd"])  # Compile func_matmult.pydd
    import func_matmult
    # Check that Intrepydd & Python implementations of matmult behave the same
    # Not all test cases will have an equivalent python_* function to compare with
    #A = np.array([[-1.2, 3.4, -5.6],[7.8, -9.0, 1.2]])
    #B = np.array([[3.4, -5.6], [7.8, 9.0], [-1.2, 3.4]])

    n = 100
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)

    assert np.allclose(func_matmult.f0(A, B), python_matmult(A, B))
    assert np.allclose(func_matmult.f1(A, B), python_matmult(A, B))

    #assert (abs(func_matmult.f0(A, B) - python_matmult(A, B)) < 0.000001).all()
    #assert (abs(func_matmult.func(A.astype('float64'), B.astype('float64')) - python_matmult(A, B)) < 0.000001).all()

