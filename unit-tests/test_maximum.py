# Python code to test Intrepydd's maximum function
# Author: Sitao Huang (shuang91@illinois.edu)

import numpy as np

# Called by pytest tool, which automatically calls all test_* functions in test_*.py files in this directory
def test_maximum():
    import subprocess
    subprocess.run(["../compiler/pyddc", "func_maximum.pydd"])  # Compile func_argmax.pydd
    import func_maximum
    
    data_int64 = np.random.randint(10, size=(10,10))
    data_f64_a = np.random.normal(loc=3.0, size=(10,10))
    data_f64_b = np.random.normal(loc=3.0, size=(10,10))

    # Check that Intrepydd and Numpy implementations of maximum behave the same
    ref_result  = np.maximum(data_f64_a, data_f64_b)
    test_result = func_maximum.maximum_test(data_f64_a, data_f64_b)
    assert(np.array_equal(ref_result, test_result))

    ref_result  = np.maximum(data_f64_a, data_int64)
    test_result = func_maximum.maximum_test_2(data_f64_a, data_int64)
    assert(np.array_equal(ref_result, test_result))

    ref_result  = np.maximum(data_f64_a, 3)
    test_result = func_maximum.maximum_test_scalar(data_f64_a, 3)
    assert(np.array_equal(ref_result, test_result))

    ref_result  = np.maximum(4, data_f64_a)
    test_result = func_maximum.maximum_test_scalar_2(4, data_f64_a)
    assert(np.array_equal(ref_result, test_result))
