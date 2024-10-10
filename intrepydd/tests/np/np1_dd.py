

def sum_3d(xs: Array(double, 3)) -> double: # type: double
    sum = 0.0
    for i in range(xs.shape(0)):
        for j in range(xs.shape(1)):
            for k in range(xs.shape(2)):
                sum += xs[i, j, k]
    return sum
