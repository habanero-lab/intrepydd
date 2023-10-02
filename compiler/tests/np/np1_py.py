import numpy as np

def sum_3d(xs: np.ndarray) -> int:
    sum = 0
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            for k in range(xs.shape[2]):
                sum += xs[i, j, k]
    return sum
