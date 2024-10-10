#ifndef ELEMWISE_HPP
#define ELEMWISE_HPP

#include <cstdlib>
#include <iterator>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "py/operation.hpp"
#include "py/util.hpp"
//#include "py/array_alloc.hpp"
#include "shared/NpArray.hpp"

//#define ELEMWISE_DEBUG


namespace py = pybind11;

namespace pydd {

  // Operators
  template<typename T>
  py::array_t<T> unary(py::array_t<T> &arr, T (*operation)(T)) {
    auto data = arr.mutable_data();
    int total = arr.size();

    T dummy = 0;
    
    //py::array_t<T> arr0 = alloc_same_shape_array(arr, dummy, "");
    py::array_t<T> arr0(*pydd::shape(arr));
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((T*)data0)[i] = operation(((T*)data)[i]);
    }
    return arr0;
  }

  template<typename T>
  py::array_t<bool> unary_logical(py::array_t<T> &arr, bool (*operation)(T)) {
    auto data = arr.mutable_data();
    int total = arr.size();

    bool dummy = 0;
    py::array_t<bool> arr0(*pydd::shape(arr));
    //py::array_t<bool> arr0 = alloc_same_shape_array(arr, dummy, "?");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((bool*)data0)[i] = operation(((T*)data)[i]);
    }
    return arr0;
  }

  template<typename T>
  py::array_t<double> unary_double(py::array_t<T> &arr, double (*operation)(T)) {
    auto data = arr.mutable_data();
    int total = arr.size();

    double dummy = 0;
    py::array_t<double> arr0(*pydd::shape(arr));
    //py::array_t<double> arr0 = alloc_same_shape_array(arr, dummy, "d");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((double*)data0)[i] = operation(((T*)data)[i]);
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<double> binary_scalar(py::array_t<T1> &arr, T2 arg, double (*operation)(T1, T2)) {
    auto data = arr.mutable_data();
    int total = arr.size();

    double dummy = 0;
    py::array_t<double> arr0(*pydd::shape(arr));
    //py::array_t<double> arr0 = alloc_same_shape_array(arr, dummy, "d");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((double*)data0)[i] = operation(((T1*)data)[i], arg);
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<double> binary_scalar(T1 arg, py::array_t<T2> &arr, double (*operation)(T1, T2)) {
    auto data = arr.mutable_data();
    int total = arr.size();

    double dummy = 0;
    py::array_t<double> arr0(*pydd::shape(arr));
    //py::array_t<double> arr0 = alloc_same_shape_array(arr, dummy, "d");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((double*)data0)[i] = operation(arg, ((T2*)data)[i]);
    }
    return arr0;
  }

  template<typename T>
  inline py::array_t<T> alloc_nd_array(std::vector<py::ssize_t> shape, T ret_type, std::string format) {
    py::buffer_info buf;
    buf.ptr = NULL;
    buf.itemsize = sizeof(T);
    buf.format = format;
    buf.ndim = shape.size();
    buf.shape = shape;
    buf.strides = shape;
    buf.strides[buf.ndim-1] = buf.itemsize;
    for (int d = buf.ndim-2; d >= 0; d--)
      buf.strides[d] = buf.shape[d+1] * buf.strides[d+1];
    return py::array_t<T>(buf);
  }

  template<typename T1, typename T2>
  bool is_same_shape(py::array_t<T1> &arr1, py::array_t<T2> &arr2) {
    int ndim = arr1.ndim();
    if (arr2.ndim() != ndim)
      return false;
    for (int d = 0; d < ndim; d++) {
      if (arr1.shape(d) != arr2.shape(d))
	return false;
    }
    return true;
  }

  template<typename T1, typename T2>
  bool is_consistent_shape(py::array_t<T1> &arr1, py::array_t<T2> &arr2,
			   std::vector<int> &step1, std::vector<int> &step2, std::vector<py::ssize_t> &shape) {
    int diff0 = arr1.ndim() - arr2.ndim();
    int diff = diff0;
    int ndim = (diff >= 0) ? arr1.ndim() : arr2.ndim();

    for (int d = 0; d < ndim; d++) {
      if (diff < 0) {
	step1.push_back(0);
	step2.push_back(1);
	shape.push_back(arr2.shape(d));
	diff++;
      } else if (diff > 0) {
	step1.push_back(1);
	step2.push_back(0);
	shape.push_back(arr1.shape(d));
	diff--;
      } else {
	int d1 = (diff0 >= 0) ? d : d + diff0;
	int d2 = (diff0 <= 0) ? d : d - diff0;
	if (arr1.shape(d1) == arr2.shape(d2)) {
	  step1.push_back(1);
	  step2.push_back(1);
	  shape.push_back(arr1.shape(d1));
	} else if (arr1.shape(d1) == 1) {
	  step1.push_back(0);
	  step2.push_back(1);
	  shape.push_back(arr2.shape(d2));
	} else if (arr2.shape(d2) == 1) {
	  step1.push_back(1);
	  step2.push_back(0);
	  shape.push_back(arr1.shape(d1));
	} else {
	  return false;
	}
      }
    }
    return true;
  }

  /*
  template<typename T>
  void compatibility_check(std::vector<py::array_t<T>> *arrs) {
#ifdef ELEMWISE_DEBUG
    std::cout << "[Verbose] compatibility_check by list\n";
#endif
    int n = arrs->size();
    int ndim = 0;
    for (int i = 0; i < n; i++) {
      int nd = (*arrs)[i].ndim();
      if (nd > ndim)
	ndim = nd;
    }

    for (int d = 0; d < ndim; d++) {
      int size = 1;
      for (int i = 0; i < n; i++) {
	int nd = (*arrs)[i].ndim();
	int idx = d + nd - ndim;
	if (idx >= 0) {
	  int sz = (*arrs)[i].shape(idx);
#ifdef ELEMWISE_DEBUG
	  std::cout << "[Verbose] dim = " << d << ", i = " << i << ", sz = " << sz << ", size = " << size << std::endl;
#endif
	  if (size == 1) {
	    size = sz;
	  } else if (sz != 1 && sz != size) {
	    std::cerr << "[Error] Element-wise binary operation assumes consistent shape arrays.\n";
	    exit(-1);
	  }
	}
      }
    }
#ifdef ELEMWISE_DEBUG
    std::cout << "[Verbose] Arguments satisfied compatibility for element-wise operation\n";
#endif
  }
  */

  void compatibility_check0(void* arrays[], int count) {
#ifdef ELEMWISE_DEBUG
    std::cout << "[Verbose] compatibility_check by variadic arguments\n";
#endif
    if (count == 0)
      return;

    int ndim = 0;
    for (int i = 0; i < count; i++) {
      py::array_t<double> *array = (py::array_t<double> *) arrays[i];
      int nd = array->ndim();
#ifdef ELEMWISE_DEBUG
      std::cout << "[Verbose] array at " << array << " with ndim = " << nd << std::endl;
#endif
      if (nd > ndim)
	ndim = nd;
    }

    for (int d = 0; d < ndim; d++) {
      int size = 1;
      for (int i = 0; i < count; i++) {
	py::array_t<double> *array = (py::array_t<double> *) arrays[i];
	int nd = array->ndim();
	int idx = d + nd - ndim;
	if (idx >= 0) {
	  int sz = array->shape(idx);
#ifdef ELEMWISE_DEBUG
	  std::cout << "[Verbose] dim = " << d << ", i = " << i << ", sz = " << sz << ", size = " << size << std::endl;
#endif
	  if (size == 1) {
	    size = sz;
	  } else if (sz != 1 && sz != size) {
	    
	    std::string msg = "[Error] Element-wise binary operation assumes consistent shape arrays.\n";
	    std::cerr << msg;
	    for (int j = 0; j < count; ++j) {
	      py::array_t<double> *array = (py::array_t<double> *) arrays[j];
	      std::cerr << array->shape(0) << std::endl;	      
	    }
	    throw new std::length_error(msg);
	    
	    //exit(-1);
	  }
	}
      }
    }
#ifdef ELEMWISE_DEBUG
    std::cout << "[Verbose] Arguments satisfied compatibility for element-wise operation\n";
#endif
  }

  template <typename T, typename... Args>
  inline void compatibility_check0(void* arrays[], int count, py::array_t<T> &first, Args... args) {
    arrays[count] = &first;
    compatibility_check0(arrays, count+1, args...);
  }

  template <typename T, typename... Args>
  inline void compatibility_check(py::array_t<T> &first, Args... args) {
    void* arrays[128];
    compatibility_check0(arrays, 0, first, args...);
  }

  template<typename T1, typename T2>
  py::array_t<double> binary(py::array_t<T1> &arr1, py::array_t<T2> &arr2, double (*operation)(T1, T2)) {
    bool is_same = is_same_shape(arr1, arr2);
    std::vector<int> step1, step2;
    std::vector<py::ssize_t> shape;
    if (!is_same && !is_consistent_shape(arr1, arr2, step1, step2, shape)) {
      std::cerr << "[Error] Element-wise binary operation assumes consistent shape arrays.\n";
      exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();

    double dummy = 0;
    py::array_t<double> arr0;
    if (is_same) {
      int total = arr1.size();
      arr0 = pydd::empty(pydd::shape(arr1), dummy);
      //arr0 = alloc_same_shape_array(arr1, dummy, "d");
      auto data0 = arr0.mutable_data();
      for (int i = 0; i < total; i++) {
	((double*)data0)[i] = operation(((T1*)data1)[i], ((T2*)data2)[i]);
      }
    } else {
      int ndim = shape.size();
      if (ndim > 5) {
	std::cerr << "[Error] Unsupported dimensionality.\n";
	exit(-1);
      }

      //arr0 = pydd::empty(&shape, dummy);
      arr0 = alloc_nd_array(shape, dummy, "d");
      auto data0 = arr0.mutable_data();

      if (ndim < 5) {
	step1.insert(step1.begin(), 5 - ndim, 1);
	step2.insert(step2.begin(), 5 - ndim, 1);
	shape.insert(shape.begin(), 5 - ndim, 1);
      }
      std::vector<int> stride0(5, 1), stride1(5, 1), stride2(5, 1);
      for (int d = 3; d >= 0; d--) {
	stride0[d] = shape[d+1] * stride0[d+1];
	stride1[d] = (step1[d+1] == 1 ? shape[d+1] : 1) * stride1[d+1];
	stride2[d] = (step2[d+1] == 1 ? shape[d+1] : 1) * stride2[d+1];
      }

      for (int i0_0 = 0; i0_0 < shape[0]; i0_0++) {
	int os0_0 = i0_0 * stride0[0];
	int os1_0 = (step1[0] == 1) ? i0_0 * stride1[0] : 0;
	int os2_0 = (step2[0] == 1) ? i0_0 * stride2[0] : 0;
	for (int i0_1 = 0; i0_1 < shape[1]; i0_1++) {
	  int os0_1 = os0_0 + i0_1 * stride0[1];
	  int os1_1 = os1_0 + ((step1[1] == 1) ? i0_1 * stride1[1] : 0);
	  int os2_1 = os2_0 + ((step2[1] == 1) ? i0_1 * stride2[1] : 0);
	  for (int i0_2 = 0; i0_2 < shape[2]; i0_2++) {
	    int os0_2 = os0_1 + i0_2 * stride0[2];
	    int os1_2 = os1_1 + ((step1[2] == 1) ? i0_2 * stride1[2] : 0);
	    int os2_2 = os2_1 + ((step2[2] == 1) ? i0_2 * stride2[2] : 0);
	    for (int i0_3 = 0; i0_3 < shape[3]; i0_3++) {
	      int os0_3 = os0_2 + i0_3 * stride0[3];
	      int os1_3 = os1_2 + ((step1[3] == 1) ? i0_3 * stride1[3] : 0);
	      int os2_3 = os2_2 + ((step2[3] == 1) ? i0_3 * stride2[3] : 0);
	      if (step1[4] == 1 && step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3 + i0_4]);
	      } else if (step1[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3]);
	      } else if (step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3], ((T2*)data2)[os2_3 + i0_4]);
	      } else {
		assert(0);
	      }
	    }
	  }
	}
      }
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<double> binary(py::array_t<T1> &arr1, py::array_t<T2> &arr2,
			     py::array_t<T2> &out, double (*operation)(T1, T2)) {
    bool is_same = is_same_shape(arr1, arr2);
    std::vector<int> step1, step2;
    std::vector<py::ssize_t> shape;
    if (!is_same && !is_consistent_shape(arr1, arr2, step1, step2, shape)) {
      std::cerr << "[Error] Element-wise binary operation assumes consistent shape arrays.\n";
      exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    auto data0 = out.mutable_data();

    double dummy = 0;
    py::array_t<double> arr0;
    if (is_same) {
      int total = arr1.size();
      for (int i = 0; i < total; i++) {
	((double*)data0)[i] = operation(((T1*)data1)[i], ((T2*)data2)[i]);
      }
    } else {
      int ndim = shape.size();
      if (ndim > 5) {
	std::cerr << "[Error] Unsupported dimensionality.\n";
	exit(-1);
      }

      if (ndim < 5) {
	step1.insert(step1.begin(), 5 - ndim, 1);
	step2.insert(step2.begin(), 5 - ndim, 1);
	shape.insert(shape.begin(), 5 - ndim, 1);
      }
      std::vector<int> stride0(5, 1), stride1(5, 1), stride2(5, 1);
      for (int d = 3; d >= 0; d--) {
	stride0[d] = shape[d+1] * stride0[d+1];
	stride1[d] = (step1[d+1] == 1 ? shape[d+1] : 1) * stride1[d+1];
	stride2[d] = (step2[d+1] == 1 ? shape[d+1] : 1) * stride2[d+1];
      }

      for (int i0_0 = 0; i0_0 < shape[0]; i0_0++) {
	int os0_0 = i0_0 * stride0[0];
	int os1_0 = (step1[0] == 1) ? i0_0 * stride1[0] : 0;
	int os2_0 = (step2[0] == 1) ? i0_0 * stride2[0] : 0;
	for (int i0_1 = 0; i0_1 < shape[1]; i0_1++) {
	  int os0_1 = os0_0 + i0_1 * stride0[1];
	  int os1_1 = os1_0 + ((step1[1] == 1) ? i0_1 * stride1[1] : 0);
	  int os2_1 = os2_0 + ((step2[1] == 1) ? i0_1 * stride2[1] : 0);
	  for (int i0_2 = 0; i0_2 < shape[2]; i0_2++) {
	    int os0_2 = os0_1 + i0_2 * stride0[2];
	    int os1_2 = os1_1 + ((step1[2] == 1) ? i0_2 * stride1[2] : 0);
	    int os2_2 = os2_1 + ((step2[2] == 1) ? i0_2 * stride2[2] : 0);
	    for (int i0_3 = 0; i0_3 < shape[3]; i0_3++) {
	      int os0_3 = os0_2 + i0_3 * stride0[3];
	      int os1_3 = os1_2 + ((step1[3] == 1) ? i0_3 * stride1[3] : 0);
	      int os2_3 = os2_2 + ((step2[3] == 1) ? i0_3 * stride2[3] : 0);
	      if (step1[4] == 1 && step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3 + i0_4]);
	      } else if (step1[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3]);
	      } else if (step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((double*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3], ((T2*)data2)[os2_3 + i0_4]);
	      } else {
		assert(0);
	      }
	    }
	  }
	}
      }
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<bool> binary_logical_scalar(py::array_t<T1> &arr, T2 arg, bool (*operation)(T1, T2)) {
    auto dara = arr.mutable_data();
    int total = arr.size();

    bool dummy = 0;
    py::array_t<bool> arr0(*pydd::shape(arr));
    //py::array_t<bool> arr0 = alloc_same_shape_array(arr, dummy, "?");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((bool*)data0)[i] = operation(((T1*)dara)[i], arg);
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<bool> binary_logical_scalar(T1 arg, py::array_t<T2> &arr, bool (*operation)(T1, T2)) {
    auto dara = arr.mutable_data();
    int total = arr.size();

    bool dummy = 0;
    py::array_t<bool> arr0(*pydd::shape(arr));
    //py::array_t<bool> arr0 = alloc_same_shape_array(arr, dummy, "?");
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < total; i++) {
      ((bool*)data0)[i] = operation(arg, ((T2*)dara)[i]);
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<bool> binary_logical(py::array_t<T1> &arr1, py::array_t<T2> &arr2, bool (*operation)(T1, T2)) {
    bool is_same = is_same_shape(arr1, arr2);
    std::vector<int> step1, step2;
    std::vector<py::ssize_t> shape;
    if (!is_same && !is_consistent_shape(arr1, arr2, step1, step2, shape)) {
      std::cerr << "[Error] Element-wise binary operation assumes consistent shape arrays.\n";
      exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();

    bool dummy = 0;
    py::array_t<bool> arr0;
    if (is_same) {
      int total = arr1.size();
      arr0 = pydd::empty(pydd::shape(arr1), dummy);
      //arr0 = alloc_same_shape_array(arr1, dummy, "?");
      auto data0 = arr0.mutable_data();
      for (int i = 0; i < total; i++) {
	((bool*)data0)[i] = operation(((T1*)data1)[i], ((T2*)data2)[i]);
      }
    } else {
      int ndim = shape.size();
      if (ndim > 5) {
	std::cerr << "[Error] Unsupported dimensionality.\n";
	exit(-1);
      }

      //arr0 = pydd::empty(&shape, dummy);
      arr0 = alloc_nd_array(shape, dummy, "?");
      auto data0 = arr0.mutable_data();

      if (ndim < 5) {
	step1.insert(step1.begin(), 5 - ndim, 1);
	step2.insert(step2.begin(), 5 - ndim, 1);
	shape.insert(shape.begin(), 5 - ndim, 1);
      }
      std::vector<int> stride0(5, 1), stride1(5, 1), stride2(5, 1);
      for (int d = 3; d >= 0; d--) {
	stride0[d] = shape[d+1] * stride0[d+1];
	stride1[d] = (step1[d+1] == 1 ? shape[d+1] : 1) * stride1[d+1];
	stride2[d] = (step2[d+1] == 1 ? shape[d+1] : 1) * stride2[d+1];
      }

      for (int i0_0 = 0; i0_0 < shape[0]; i0_0++) {
	int os0_0 = i0_0 * stride0[0];
	int os1_0 = (step1[0] == 1) ? i0_0 * stride1[0] : 0;
	int os2_0 = (step2[0] == 1) ? i0_0 * stride2[0] : 0;
	for (int i0_1 = 0; i0_1 < shape[1]; i0_1++) {
	  int os0_1 = os0_0 + i0_1 * stride0[1];
	  int os1_1 = os1_0 + ((step1[1] == 1) ? i0_1 * stride1[1] : 0);
	  int os2_1 = os2_0 + ((step2[1] == 1) ? i0_1 * stride2[1] : 0);
	  for (int i0_2 = 0; i0_2 < shape[2]; i0_2++) {
	    int os0_2 = os0_1 + i0_2 * stride0[2];
	    int os1_2 = os1_1 + ((step1[2] == 1) ? i0_2 * stride1[2] : 0);
	    int os2_2 = os2_1 + ((step2[2] == 1) ? i0_2 * stride2[2] : 0);
	    for (int i0_3 = 0; i0_3 < shape[3]; i0_3++) {
	      int os0_3 = os0_2 + i0_3 * stride0[3];
	      int os1_3 = os1_2 + ((step1[3] == 1) ? i0_3 * stride1[3] : 0);
	      int os2_3 = os2_2 + ((step2[3] == 1) ? i0_3 * stride2[3] : 0);
	      if (step1[4] == 1 && step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((bool*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3 + i0_4]);
	      } else if (step1[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((bool*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3 + i0_4], ((T2*)data2)[os2_3]);
	      } else if (step2[4] == 1) {
		for (int i0_4 = 0; i0_4 < shape[4]; i0_4++)
		  ((bool*)data0)[os0_3 + i0_4] = operation(((T1*)data1)[os1_3], ((T2*)data2)[os2_3 + i0_4]);
	      } else {
		assert(0);
	      }
	    }
	  }
	}
      }
    }
    return arr0;
  }

  // Intrepydd functions
  // Unray on array
  template<typename T>
  py::array_t<T> minus(py::array_t<T> arr) {
    return unary(arr, ope_minus);
  }
  template<typename T>
  py::array_t<T> abs(py::array_t<T> arr) {
    return unary(arr, ope_abs);
  }
  template<typename T>
  py::array_t<bool> elemwise_not(py::array_t<T> arr) {
    return unary_logical(arr, ope_not);
  }
  template<typename T>
  py::array_t<bool> logical_not(py::array_t<T> arr) {
    return unary_logical(arr, ope_not);
  }
  template<typename T>
  py::array_t<bool> isnan(py::array_t<T> arr) {
    return unary_logical(arr, ope_isnan);
  }
  template<typename T>
  py::array_t<bool> isinf(py::array_t<T> arr) {
    return unary_logical(arr, ope_isinf);
  }
  template<typename T>
  py::array_t<double> sqrt(py::array_t<T> arr) {
    return unary_double(arr, ope_sqrt);
  }
  template<typename T>
  py::array_t<double> exp(py::array_t<T> arr) {
    return unary_double(arr, ope_exp);
  }
  template<typename T>
  py::array_t<double> log(py::array_t<T> arr) {
    return unary_double(arr, ope_log);
  }
  template<typename T>
  py::array_t<double> cos(py::array_t<T> arr) {
    return unary_double(arr, ope_cos);
  }
  template<typename T>
  py::array_t<double> sin(py::array_t<T> arr) {
    return unary_double(arr, ope_sin);
  }
  template<typename T>
  py::array_t<double> tan(py::array_t<T> arr) {
    return unary_double(arr, ope_tan);
  }
  template<typename T>
  py::array_t<double> acos(py::array_t<T> arr) {
    return unary_double(arr, ope_acos);
  }
  template<typename T>
  py::array_t<double> asin(py::array_t<T> arr) {
    return unary_double(arr, ope_asin);
  }
  template<typename T>
  py::array_t<double> atan(py::array_t<T> arr) {
    return unary_double(arr, ope_atan);
  }


  // Binary on array and scalar
  template<typename T1, typename T2>
  py::array_t<double> add(py::array_t<T1> x1, T2 x2) {
    return binary_scalar(x1, x2, ope_add2);
  }
  template<typename T1, typename T2>
  py::array_t<double> sub(py::array_t<T1> x1, T2 x2) {
    return binary_scalar(x1, x2, ope_sub2);
  }
  template<typename T1, typename T2>
  py::array_t<double> mul(py::array_t<T1> x1, T2 x2) {
    return binary_scalar(x1, x2, ope_mul2);
  }
  template<typename T1, typename T2>
  py::array_t<double> div(py::array_t<T1> arr, T2 arg) {
    return binary_scalar(arr, arg, ope_div2);
  }
  template<typename T1, typename T2>
  py::array_t<double> pow(py::array_t<T1> arr, T2 arg) {
    return binary_scalar(arr, arg, ope_pow);
  }
  template<typename T1, typename T2>
  py::array_t<double> log(py::array_t<T1> arr, T2 arg) {
    return binary_scalar(arr, arg, ope_log2);
  }
  template<typename T1, typename T2>
  py::array_t<double> maximum(py::array_t<T1> arr, T2 arg) {
    return binary_scalar(arr, arg, ope_max2);
  }
  template<typename T1, typename T2>
  py::array_t<double> add(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_add2);
  }
  template<typename T1, typename T2>
  py::array_t<double> sub(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_sub2);
  }
  template<typename T1, typename T2>
  py::array_t<double> mul(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_mul2);
  }
  template<typename T1, typename T2>
  py::array_t<double> div(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_div2);
  }
  template<typename T1, typename T2>
  py::array_t<double> pow(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_pow);
  }
  template<typename T1, typename T2>
  py::array_t<double> log(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_log2);
  }
  template<typename T1, typename T2>
  py::array_t<double> maximum(T1 arg, py::array_t<T2> arr) {
    return binary_scalar(arg, arr, ope_max2);
  }

  // Binary on array and array
template<typename T>
void _add(py::array_t<T> x1, py::array_t<T> x2, py::array_t<T> out) {
  const T* x1_data = x1.data();
  const T* x2_data = x2.data();
  T* out_data = out.mutable_data();
  int size = out.size();
  for (int i = 0; i < size; ++i) {
    out_data[i] = x1_data[i] + x2_data[i];
  }
}

template<typename T>
void _add(py::array_t<T> x1, T x2, py::array_t<T> out) {
  const T* x1_data = x1.data();
  T* out_data = out.mutable_data();
  int size = out.size();
  for (int i = 0; i < size; ++i) {
    out_data[i] = x1_data[i] + x2;
  }
}

template<typename T>
void _sub(py::array_t<T> x1, py::array_t<T> x2, py::array_t<T> out) {
  const T* x1_data = x1.data();
  const T* x2_data = x2.data();
  T* out_data = out.mutable_data();
  int size = out.size();
  for (int i = 0; i < size; ++i) {
    out_data[i] = x1_data[i] - x2_data[i];
  }
}

template<typename T>
void _mul(py::array_t<T> x1, py::array_t<T> x2, py::array_t<T> out) {
  const T* x1_data = x1.data();
  const T* x2_data = x2.data();
  T* out_data = out.mutable_data();
  int size = out.size();
  for (int i = 0; i < size; ++i) {
    out_data[i] = x1_data[i] * x2_data[i];
  }
}

template<typename T>
void _div(py::array_t<T> x1, py::array_t<T> x2, py::array_t<double> out) {
  const T* x1_data = x1.data();
  const T* x2_data = x2.data();
  T* out_data = out.mutable_data();
  int size = out.size();
  for (int i = 0; i < size; ++i) {
    out_data[i] = ((double)x1_data[i]) / x2_data[i];
  }
}



  template<typename T1, typename T2>
  py::array_t<double> add(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_add2);
  }
  template<typename T1, typename T2>
  py::array_t<double> sub(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_sub2);
  }
  template<typename T1, typename T2>
  py::array_t<double> mul(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_mul2);
  }
  template<typename T1, typename T2>
  py::array_t<double> div(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_div2);
  }
  template<typename T1, typename T2>
  py::array_t<double> pow(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_pow);
  }
  template<typename T1, typename T2>
  py::array_t<double> log(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_log2);
  }
  template<typename T1, typename T2>
  py::array_t<double> maximum(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary(x1, x2, ope_max2);
  }

  template<typename T>
  py::array_t<T> add(py::array_t<T> x1, py::array_t<T> x2) {
    return binary(x1, x2, ope_add2);
  }
  template<typename T>
  py::array_t<T> sub(py::array_t<T> x1, py::array_t<T> x2) {    
    return binary(x1, x2, ope_sub2);
  }
  template<typename T>
  void sub(py::array_t<T>& x1, py::array_t<T>& x2, py::array_t<T>& out) {
    binary(x1, x2, out, ope_sub2);
  }
  template<typename T>
  py::array_t<T> mul(py::array_t<T> x1, py::array_t<T> x2) {
    return binary(x1, x2, ope_mul2);
  }
  template<typename T>
  py::array_t<T> maximum(py::array_t<T> x1, py::array_t<T> x2) {
    return binary(x1, x2, ope_max);
  }

  // Binary (logical) on array and scalar
  template<typename T1, typename T2>
  py::array_t<bool> eq(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> neq(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_not_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> lt(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_less);
  }
  template<typename T1, typename T2>
  py::array_t<bool> gt(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_greater);
  }
  template<typename T1, typename T2>
  py::array_t<bool> le(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_less_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> ge(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_greater_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_and(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_logical_and);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_or(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_logical_or);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_xor(py::array_t<T1> arr, T2 arg) {
    return binary_logical_scalar(arr, arg, ope_logical_xor);
  }
  template<typename T1, typename T2>
  py::array_t<bool> eq(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> neq(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_not_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> lt(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_less);
  }
  template<typename T1, typename T2>
  py::array_t<bool> gt(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_greater);
  }
  template<typename T1, typename T2>
  py::array_t<bool> le(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_less_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> ge(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_greater_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_and(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_logical_and);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_or(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_logical_or);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_xor(T1 arg, py::array_t<T2> arr) {
    return binary_logical_scalar(arg, arr, ope_logical_xor);
  }

  // Binary (logical) on array and array
  template<typename T1, typename T2>
  py::array_t<bool> eq(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> neq(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_not_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> lt(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_less);
  }
  template<typename T1, typename T2>
  py::array_t<bool> gt(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_greater);
  }
  template<typename T1, typename T2>
  py::array_t<bool> le(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_less_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> ge(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_greater_equal);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_and(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_logical_and);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_or(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_logical_or);
  }
  template<typename T1, typename T2>
  py::array_t<bool> logical_xor(py::array_t<T1> x1, py::array_t<T2> x2) {
    return binary_logical(x1, x2, ope_logical_xor);
  }

  // Scalar operations
  //  - T abs(T val) is defined in shared/rt.hpp
  template<typename T>
  bool logical_not(T val) {
    return ope_not(val);
  }
  template<typename T>
  bool isnan(T val) {
    return ope_isnan(val);
  }
  template<typename T>
  bool isinf(T val) {
    return ope_isinf(val);
  }
  template<typename T>
  double sqrt(T var) {
    return ope_sqrt(var);
  }
  template<typename T>
  double exp(T val) {
    return ope_exp(val);
  }
  template<typename T>
  double log(T val) {
    return ope_log(val);
  }
  template<typename T>
  double cos(T val) {
    return ope_cos(val);
  }
  template<typename T>
  double sin(T val) {
    return ope_sin(val);
  }
  template<typename T>
  double tan(T val) {
    return ope_tan(val);
  }
  template<typename T>
  double acos(T val) {
    return ope_acos(val);
  }
  template<typename T>
  double asin(T val) {
    return ope_asin(val);
  }
  template<typename T>
  double atan(T val) {
    return ope_atan(val);
  }
  template<typename T1, typename T2>
  double maximum(T1 var1, T2 var2) {
    return ope_max2(var1, var2);
  }
  template<typename T1, typename T2>
  double pow(T1 var1, T2 var2) {
    return ope_pow(var1, var2);
  }
  template<typename T1, typename T2>
  double log(T1 val1, T2 val2) {
    return ope_log2(val1, val2);
  }
  template<typename T1, typename T2>
  bool logical_xor(T1 x1, T2 x2) {
    return ope_logical_xor(x1, x2);
  }
}

#endif  // ELEMWISE_HPP
