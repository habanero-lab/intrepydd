import numpy as np
import intrepydd as pydd
from intrepydd.lang import *
import inspect

def sinkhorm_wmd(K: Array(float64, 2), M: Array(float64, 2), r: Array(float64, 1), x: Array(float64, 2), max_iter: int32, values: Array(float64, 1), columns: Array(int32, 1), indexes: Array(int32, 1), ncols_c: int32) -> Array(float64, 1):
    c = csr_to_spm(values, columns, indexes, ncols_c)
    it = 0
    while it < max_iter:
        u = 1.0 / x
        v = c.spm_mul(div(1.0, K.T @ u))
        x = spmm_dense(div(1.0, r).mul(K), v)
        r[0] = 0

        it += 1

    u = 1.0 / x    
    v = c.spm_mul(div(1.0, K.T @ u))
    return mul(u, spmm_dense(mul(K, M), v)).sum(0)

cppcode, pycode = pydd.compile_from_src(inspect.getsource(sinkhorm_wmd), dumppy=True, licm=True, dense_array_opt=True, sparse_array_opt=True)
print(cppcode)