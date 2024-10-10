#Intrepydd code to test sum function (Reduction).
#Author: Armand Behroozi (armandb@umich.edu)
import numpy as np

def test_sum():
    import subprocess
    subprocess.run(["../intrepydd/pyddc", "func_sum.pydd"])  # Compile func_sum.pydd
    import func_sum
    arr_1d = [-15, 5, 0, 7]
    x = np.array(arr_1d) #default datatype on my machine was int64
    assert( func_sum.sum_wrapper(x) == sum(x) )
    arr_2d = [[-24, 7], [6, 0]]
    y = np.array(arr_2d) #default datatype on my machine was int64
    assert( func_sum.sum_wrapper(y) == sum(map(sum, y)) )

    # test for axis (2D, int)
    z = np.array([[-24, 7, 1], [6, 0, 3]])
    assert( func_sum.sum_wrapper2(z, 0) == np.sum(z, axis=0) ).all()
    assert( func_sum.sum_wrapper2(z, 1) == np.sum(z, axis=1) ).all()
    assert( func_sum.sum_wrapper2(z, -1) == np.sum(z, axis=-1) ).all()

    # test for axis (2D, float)
    w = np.array([[-24.0, 7.0, 1.0], [6.0, 0.0, 3.0]])
    assert( func_sum.sum_wrapper3(w, 0) == np.sum(w, axis=0) ).all()
    assert( func_sum.sum_wrapper3(w, 1) == np.sum(w, axis=1) ).all()
    assert( func_sum.sum_wrapper3(w, -1) == np.sum(w, axis=-1) ).all()

    # test for axis (3D, int)
    u = np.arange(3 * 2 * 4).reshape(3, 2, 4)
    assert( func_sum.sum_wrapper4(u, 0) == np.sum(u, axis=0) ).all()
    assert( func_sum.sum_wrapper4(u, 1) == np.sum(u, axis=1) ).all()
    assert( func_sum.sum_wrapper4(u, 2) == np.sum(u, axis=2) ).all()
    assert( func_sum.sum_wrapper4(u, -1) == np.sum(u, axis=-1) ).all()
