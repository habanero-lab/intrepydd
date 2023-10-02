# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess


# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_1():
    out = subprocess.run(["../compiler/pyddc", "func_dict.pydd"], stdout=subprocess.PIPE) 
    import func_dict as M
    arr = np.array([1,2,3])
    g = {1: arr, 2: arr}
    M.f3(g, 1)
    print(out.stdout)
    
test_1()
