import intrepydd
from intrepydd.lang import *

@intrepydd.compile
def fib(n: int32) -> int32:
    if n <= 1: 
        return n
    return fib(n - 1) + fib(n - 2)

assert fib(19) == 4181