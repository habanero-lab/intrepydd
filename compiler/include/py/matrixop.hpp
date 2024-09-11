#ifndef MATRIXOP_HPP
#define MATRIXOP_HPP

#include <cstdlib>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
//#include "array_alloc.hpp"
#include "NpArray.hpp"
#include <mkl.h>
#include <mkl_cblas.h>
#include <mkl_blas.h>

namespace py = pybind11;

namespace pydd {
  // Operators
  template<typename T1, typename T2>
  py::array_t<double> vectmat_multiply(py::array_t<T1> &arr1, py::array_t<T2> &arr2) {
    if (arr1.ndim() != 1 || arr2.ndim() != 2 || arr1.shape(0) != arr2.shape(0)) {
      std::cerr << "[Error] matrix-vector multiply assumes compatible 1-D/2-D arrays.\n";
      exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    int ni = arr2.shape(0);
    int nj = arr2.shape(1);

    double dummy = 0;
    //py::array_t<double> arr0 = alloc_1d_array(nj, dummy, "d");
    py::array_t<double> arr0 = empty(nj, dummy);
    auto data0 = arr0.mutable_data();
    for (int j = 0; j < nj; j++) {
      ((double*)data0)[j] = 0;
    }
    for (int i = 0; i < ni; i++) {
      for (int j = 0; j < nj; j++) {
	((double*)data0)[j] += ((T1*)data1)[i] * ((T2*)data2)[i*nj+j];
      }
    }
    return arr0;
  }

  template<typename T1, typename T2>
  py::array_t<double> matvect_multiply(py::array_t<T1> &arr1, py::array_t<T2> &arr2) {
    if (arr1.ndim() != 2 || arr2.ndim() != 1 || arr1.shape(1) != arr2.shape(0)) {
      std::cerr << "[Error] matrix-vector multiply assumes compatible 2-D/1-D arrays.\n";
      exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    int ni = arr1.shape(0);
    int nj = arr1.shape(1);

    double dummy = 0;
    //py::array_t<double> arr0 = alloc_1d_array(ni, dummy, "d");
    py::array_t<double> arr0 = empty(ni, dummy);
    auto data0 = arr0.mutable_data();
    for (int i = 0; i < ni; i++) {
      double tmp = 0;
      for (int j = 0; j < nj; j++) {
	tmp += ((T1*)data1)[i*nj+j] * ((T2*)data2)[j];
      }
      ((double*)data0)[i] = tmp;
    }
    return arr0;
  }

  template<typename T1, typename T2>
  int matmult1(py::array_t<T1> arr1, py::array_t<T2> arr2, py::array_t<double> out ) {
    if (arr1.ndim() != 2 || arr2.ndim() != 2 || arr1.shape(1) != arr2.shape(0)) {
      std::cerr << "[Error] matrix-matrix multiply assumes compatible 2-D arrays.\n";
      exit(-1);
    }

    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    int ni = arr1.shape(0);  // arr1[i,k]
    int nk = arr1.shape(1);  // == arr2.shape(0)
    int nj = arr2.shape(1);  // arr2[k,j]
    int nrows1 = ni;
    int ncols1 = nk;
    int ncols2 = nj;

    auto data0 = out.mutable_data();
   
    cblas_dgemm(CblasColMajor, CblasNoTrans, CblasNoTrans,
		nrows1, ncols2, ncols1,
		1, data1, nrows1, data2, ncols1, 0, data0, nrows1);        
  }

  template<typename T1, typename T2>
  py::array_t<double> matmat_multiply(py::array_t<T1> &arr1, py::array_t<T2> &arr2, int version) {
    if (arr1.ndim() != 2 || arr2.ndim() != 2 || arr1.shape(1) != arr2.shape(0)) {
      std::cerr << "[Error] matrix-matrix multiply assumes compatible 2-D arrays.\n";
      exit(-1);
    }

    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    int ni = arr1.shape(0);  // arr1[i,k]
    int nk = arr1.shape(1);  // == arr2.shape(0)
    int nj = arr2.shape(1);  // arr2[k,j]

    double dummy = 0;
    //py::array_t<double> arr0 = alloc_2d_array(ni, nj, dummy, "d");
    py::array_t<double> arr0 = empty({ni, nj}, dummy);
    auto data0 = arr0.mutable_data();
    if (version == 0) {
      cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
      		  ni, nj, nk,
      		  1, data1, nk, data2, nj, 0, data0, nj);

      // for (int i = 0; i < ni; i++) {
      // 	for (int j = 0; j < nj; j++) {
      // 	  ((double*)data0)[i*nj+j] = 0;
      // 	}
      // 	for (int k = 0; k < nk; k++) {
      // 	  for (int j = 0; j < nj; j++) {
      // 	    ((double*)data0)[i*nj+j] += ((T1*)data1)[i*nk+k] * ((T2*)data2)[k*nj+j];
      // 	  }
      // 	}
      // }
      
    } else if (version == 1) {
      int Ti = 64;
      int Tj = 128;
      int Tk = 32;
      for (int it = 0; it < ni; it+=Ti) {
	int iup = it+Ti > ni ? ni : it+Ti;
	for (int jt = 0; jt < nj; jt+=Tj) {
	  int jup = jt+Tj > nj ? nj : jt+Tj;
	  for (int i = it; i < iup; i++) {
	    for (int j = jt; j < jup; j++) {
	      ((double*)data0)[i*nj+j] = 0;
	    }
	  }
	}
	for (int kt = 0; kt < nk; kt+=Tk) {
	  int kup = kt+Tk > nk ? nk : kt+Tk;
	  for (int jt = 0; jt < nj; jt+=Tj) {
	    int jup = jt+Tj > nj ? nj : jt+Tj;
	    for (int i = it; i < iup; i++) {
	      for (int k = kt; k < kup; k++) {
		for (int j = jt; j < jup; j++) {
		  ((double*)data0)[i*nj+j] += ((T1*)data1)[i*nk+k] * ((T2*)data2)[k*nj+j];
		}
	      }
	    }
	  }
	}
      }
    }
    else {
      std::cerr << "[Error] Unsupported version in matrix-matrix multiply.\n";
      exit(-1);
    }
    return arr0;
  }

  // Intrepydd functions
  template<typename T>
  py::array_t<T> transpose(py::array_t<T> arr) {
    if (arr.ndim() != 2) {
      std::cerr << "[Error] Transpose assumes same 2-D array.\n";
      exit(-1);
    }
    auto data = arr.mutable_data();
    int total = arr.size();
    int nrows = arr.shape(0);
    int ncols = arr.shape(1);

    T dummy = 0;
    //py::array_t<T> arr0 = alloc_2d_array(ncols, nrows, dummy, arr.request().format);
    py::array_t<T> arr0 = empty({ncols, nrows}, dummy);

    auto data0 = arr0.mutable_data();
    for (int i = 0; i < nrows; i++) {
      int offset = i * ncols;
      for (int j = 0; j < ncols; j++) {
	((T*)data0)[j*nrows+i] = ((T*)data)[offset+j];
      }
    }
    return arr0;
  }

  template<typename T>
  int transpose1(py::array_t<T> arr, py::array_t<T> out) {
    if (arr.ndim() != 2) {
      std::cerr << "[Error] Transpose assumes same 2-D array.\n";
      exit(-1);
    }
    auto data = arr.mutable_data();
    int total = arr.size();
    int nrows = arr.shape(0);
    int ncols = arr.shape(1);


    auto data0 = out.mutable_data();
    for (int i = 0; i < nrows; i++) {
      int offset = i * ncols;
      for (int j = 0; j < ncols; j++) {
	((T*)data0)[j*nrows+i] = ((T*)data)[offset+j];
      }
    }

    return 0;
  }

  template<typename T1, typename T2>
  double innerprod(py::array_t<T1> arr1, py::array_t<T2> arr2) {
    if (arr1.ndim() != 1 || arr2.ndim() != 1 || arr1.shape(0) != arr2.shape(0)) {
      //std::cerr << "[Error] Inner product assumes same size 1-D arrays.\n";
      std::string msg = "Inner product assumes same size 1-D arrays.\n";
      msg += "arr1.ndim: " + std::to_string(arr1.ndim()) + ", arr2.ndim: " + std::to_string(arr2.ndim()) + "\n";
      throw std::invalid_argument(msg);
      //exit(-1);
    }
    auto data1 = arr1.mutable_data();
    auto data2 = arr2.mutable_data();
    int total = arr1.size();

    
    
    double result = cblas_ddot(total, data1, 1, data2, 1);
    return result;
    // double result = 0;
    // for (int i = 0; i < total; i++) {
    //   result += ((T1*)data1)[i] * ((T2*)data2)[i];
    // }
    // return result;
  }

  template<typename T1, typename T2>
  double innerprod1(int N, T1* X, T2* Y) {
    double result = cblas_ddot(N, X, 1, Y, 1);
    return result;
    // double result = 0;
    // for (int i = 0; i < total; i++) {
    //   result += ((T1*)data1)[i] * ((T2*)data2)[i];
    // }
    // return result;
  }



  template<typename T1, typename T2>
  py::array_t<double> matmult(py::array_t<T1> arr1, py::array_t<T2> arr2, int version=0) {
    int ndim1 = arr1.ndim();
    int ndim2 = arr2.ndim();
    if (ndim1 == 1) {
      if (ndim2 == 1) {
        double result = innerprod(arr1, arr2); // Maybe fixme: this should return a scalar here
        py::array_t<double> ret_arr({1});
        pydd::setitem_1d(ret_arr, result, 0);
        return ret_arr;
        //return alloc_0d_array(result, "d");
      } else if (ndim2 == 2) {
        return vectmat_multiply(arr1, arr2);
      }
    } else if (ndim1 == 2) {
      if (ndim2 == 1) {
        return matvect_multiply(arr1, arr2);
      } else if (ndim2 == 2) {
        return matmat_multiply(arr1, arr2, version);
      }
    }
    std::cerr << "[Error] Unsupported array multiplication.\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> syrk(py::array_t<T> arr, int version=0) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T1, typename T2>
  py::array_t<double> syr2k(py::array_t<T1> arr1, py::array_t<T2> arr2, int version=0) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T1, typename T2>
  py::array_t<double> symm(py::array_t<T1> arr1, py::array_t<T2> arr2, int version=0) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T1, typename T2>
  py::array_t<double> trmm(py::array_t<T1> arr1, py::array_t<T2> arr2, int version=0) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> lu(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> ludcmp(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> qr(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> eig(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> svd(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> tril(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> triu(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T>
  py::array_t<double> diag(py::array_t<T> arr, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T1, typename T2>
  py::array_t<double> kron(py::array_t<T1> arr1, py::array_t<T2> arr2, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }

  template<typename T1, typename T2>
  py::array_t<double> convolve(py::array_t<T1> arr1, py::array_t<T2> arr2, int version) {
    std::cerr << "[Error] Unsupported yet (WIP).\n";
    exit(-1);
  }
}

#endif  // MATRIXOP_HPP
