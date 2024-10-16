import intrepydd
from intrepydd.lang import *

@intrepydd.compile
def foo() -> float64:
    a = 1.0
    b = 2.0
    c = (a + b) * 3.0 
    return c

assert foo() == 9.0