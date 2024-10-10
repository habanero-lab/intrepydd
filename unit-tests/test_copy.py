# Author: Tong Zhou (tz@gatech.edu)
import sys
import numpy as np
import subprocess
import importlib
import os

def get_module():
    pyddname = os.path.basename(__file__).replace('test', 'func') + 'dd'
    out = subprocess.run(["../intrepydd/pyddc", pyddname], stdout=subprocess.PIPE)
    print(out.stdout)
    m = importlib.import_module(pyddname.replace('.pydd', ''))
    return m


def test_1():
    m = get_module()
    a = np.array([1,2,3], dtype=np.float64)
    b = m.f0(a)
    print(a, b)
    b[0] = 100
    assert a[0] == 1
    print(a, b)
    
test_1()
