import numpy as np

def geti(xs: Array(), i: int):
    print(xs[i])

def seti(xs: Array(), i: int, v: double):
    xs[i] = v
    
def get_shape(xs: Array(), i: int):
    return xs.shape[i]
    
def getij(xs: Array(), i: int, j: int):
    print(xs[i, j])
