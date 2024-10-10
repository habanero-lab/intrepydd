# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess


# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_1():
    out = subprocess.run(["../intrepydd/pyddc", "func_import.pydd"], stdout=subprocess.PIPE) 
    import func_import as M
    M.f1()
    print(out.stdout)
    
test_1()
