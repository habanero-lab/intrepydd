#test sparse_diags
#Author: Carl Pearson (pearson@illinois.edu)
import numpy as np

def test_sparse_diags():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_sparse_diags.pydd"]) 
    import func_sparse_diags as M

    vec_len = 100
    arr = np.random.normal(size=vec_len)
    vals = np.arange(0, dtype=np.float64)
    cols = np.arange(0, dtype=np.int32)
    idxs = np.arange(0, dtype=np.int32)

    # Sparse matrix is constructed with arr and dumped in CSR format
    M.dump(arr, vals, cols, idxs)

    cols_ref = np.arange(vec_len)
    idxs_ref = np.arange(vec_len+1)

    assert(np.array_equal(arr, vals))
    assert(np.array_equal(cols, cols_ref))
    assert(np.array_equal(idxs, idxs_ref))
