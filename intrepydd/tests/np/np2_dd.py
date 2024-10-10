

def inc_3d(xs: Array(double, 3)) -> double: # type: double    
    for i in range(xs.shape[0]):
        for j in range(xs.shape[1]):
            for k in range(xs.shape[2]):
                xs[i, j, k] += 1
    
