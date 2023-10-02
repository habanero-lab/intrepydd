import cmath

def counts_array(k: int) -> Array(float64):
    counts = empty(k, int32())
    counts[0] = cmath.exp(2.0, 2.0)
    return counts

def empty1(k: int, j: int) -> Array(float64):
    counts = empty([k, j], float32())
    return counts
