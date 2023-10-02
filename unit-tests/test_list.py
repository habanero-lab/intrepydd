# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess
import importlib
import os

def test_1():
    pyddname = os.path.basename(__file__).replace('test', 'func') + 'dd'
    out = subprocess.run(["../compiler/pyddc", pyddname], stdout=subprocess.PIPE)
    M = importlib.import_module(pyddname.replace('.pydd', ''))
    
    # print(M.f1())
    # print(M.f2())
    # print(M.f3())
    M.f4([5,6,7])
    M.f5([5.0,6.0,7.0])
#    M.f6([False, True])
    print(out.stdout)
    
test_1()
