import numpy as np

def shape(a, i):
    return a.shape[i]

def stride(a, i):
    return a.strides[i]

def zeros(shape, dtype):
    return np.zeros(shape, type(dtype))
        
def empty(shape, dtype):
    return np.empty(shape, type(dtype))

