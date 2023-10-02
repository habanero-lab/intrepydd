# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess

# # Copy of Intrepydd code from func_zeros.pydd, adapted to Python
# def python_zeros(shape):
#     C = np.zeros(shape, dtype=int)
#     return C

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_print():
    out = subprocess.run(["../compiler/pyddc", "func_print.pydd"], stdout=subprocess.PIPE) 
    import func_print
    func_print.f1()
    print(out.stdout)
    
test_print()
