# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess
import importlib
import os

def test_1():
    pyddname = os.path.basename(__file__).replace('test', 'func') + 'dd'    
    out = subprocess.run(["../intrepydd/pyddc", pyddname], stdout=subprocess.PIPE)
    M = importlib.import_module(pyddname.replace('.pydd', ''))
    assert M.f1(0, 1)
    assert not M.f1(2, 1)
    print(out.stdout)
    
test_1()
