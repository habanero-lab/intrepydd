# Python code to test Intrepydd's eq function by calling func_eq.func()
# Author: Matthew Sternberg (msternberg6@gatech.edu)

import numpy as np
import subprocess

def python_np_mult(A, B):
    C = np.multiply(A, B)
    return C

def python_np_add(A, B):
    C = np.add(A, B)
    return C

def python_np_sub(A, b):
    C = np.subtract(A, b)
    return C

def op_expand_mult_test():
    import func_op_expand
    A = np.array([1, 2, 3, 4])
    B = np.array([5, 6, 2, 10])    
    assert (func_op_expand.wrapper_np_mult(A, B) == python_np_mult(A, B)).all()

def op_expand_add_test():
    import func_op_expand
    A = np.array([2, -1, 5, 6])
    B = np.array([0, 5, -1, 8])
    assert (func_op_expand.wrapper_np_add(A, B) == python_np_add(A, B)).all()

def op_expand_sub_test():
    import func_op_expand
    A = np.array([2, -3, 0])
    b = 3
    assert (func_op_expand.wrapper_np_sub(A, b) == python_np_sub(A, b)).all()

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_op_expand():
    subprocess.run(["../compiler/pyddc", "func_op_expand.pydd"])  # Compile func_op_expand.pydd
    
    op_expand_mult_test()
    op_expand_add_test()
    op_expand_sub_test()
