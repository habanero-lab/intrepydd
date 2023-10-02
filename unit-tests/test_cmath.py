# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess
import importlib
import math
import os

def test_1():
    pyddname = os.path.basename(__file__).replace('test', 'func') + 'dd'    
    out = subprocess.run(["../compiler/pyddc", pyddname], stdout=subprocess.PIPE)
    M = importlib.import_module(pyddname.replace('.pydd', ''))
    assert math.exp(1.1) == M.exp(1.1)
    assert math.log(1.1) == M.log(1.1) 
    
test_1()
