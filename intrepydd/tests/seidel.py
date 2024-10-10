def kernel_seidel_2d(tsteps: int, n: int, A: Array(float64, 2)):

    for t in range(tsteps):
        for i in range(1, n-1):
            for j in range(1, n-1):
                A[i,j] = (A[i-1,j-1] + A[i-1,j] + A[i-1,j+1] \
                          + A[i,j-1] + A[i,j] + A[i,j+1] \
                          + A[i+1,j-1] + A[i+1,j] + A[i+1,j+1]) / 9.0
