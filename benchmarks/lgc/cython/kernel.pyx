import numpy as np
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def func0(np.ndarray[np.int32_t, ndim=1] seeds, np.ndarray[np.int32_t, ndim=1] degrees, np.float64_t alpha, np.float64_t epsilon,
          np.int32_t num_nodes, np.ndarray[np.int32_t, ndim=1] adj_indices, np.ndarray[np.int32_t, ndim=1] adj_indptr):
    cdef np.int32_t i, j
    cdef np.int32_t num_seeds, seed, node_idx, src_idx, dst_idx
    cdef np.float64_t update
    cdef np.ndarray[np.float64_t, ndim=2] out
    cdef np.ndarray[np.float64_t, ndim=1] p, r, r_prime
    cdef np.ndarray[np.int32_t, ndim=1] frontier

    num_seeds = seeds.shape[0]
    out = np.empty([num_seeds, num_nodes], dtype=np.float64)
    for i in range(num_seeds):
        seed = seeds[i]
        p = np.zeros(num_nodes, dtype=np.float64)
        r = np.zeros(num_nodes, dtype=np.float64)
        r[seed] = 1.0

        frontier = np.array([seed], dtype=np.int32)
        while True:
            if len(frontier) == 0:
                break

            r_prime = r.copy()
            for node_idx in frontier:
                p[node_idx] += (2 * alpha) / (1 + alpha) * r[node_idx]
                r_prime[node_idx] = 0

            for src_idx in frontier:
                neighbors = adj_indices[adj_indptr[src_idx]:adj_indptr[src_idx + 1]]
                for dst_idx in neighbors:
                    update = ((1 - alpha) / (1 + alpha)) * r[src_idx] / degrees[src_idx]
                    r_prime[dst_idx] += update

            r = r_prime

            frontier = np.where((r >= degrees * epsilon) & (degrees > 0))[0].astype(np.int32)

        for j in range(num_nodes):
            out[i,j] = p[j]

    return out.T
