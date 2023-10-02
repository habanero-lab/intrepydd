#ifndef NPARRAY_HPP
#define NPARRAY_HPP

#include <ctime>
#include <cstdlib>
#include "rt.hpp"
#include <cassert>

namespace py = pybind11;

namespace pydd {

/*! 
  py::array_t<T> is a C++ class that wraps a Numpy array.
  It only supports a couple essentional interfaces such as
  getting the shape, accessing each element etc.
*/

typedef std::initializer_list<ssize_t> Ssize_tList;
typedef std::initializer_list<long> longList;
typedef int64_t Int64Type;

// template <typename T>
// Int64Type len(py::array_t<T>& arr) {
//   return arr.shape(0);
// }

template <typename T>
Int64Type len(py::array_t<T> arr) {
  return arr.shape(0);
}

template <typename T>
Int64Type shape(py::array_t<T>& arr, int i) {
  return arr.shape(i);
}

template <typename T>
Int64Type stride(py::array_t<T>& arr, int i) {
  return arr.strides(i);
}

template <typename T>
std::vector<Int64Type>* shape(py::array_t<T>& arr) {
  std::vector<Int64Type>* s = new std::vector<Int64Type>();
  for (int i = 0; i < arr.ndim(); ++i) {
    s->push_back(arr.shape(i));
  }
  return s;
}

template <typename T>
Int64Type ndim(py::array_t<T>& arr) {
  return arr.ndim();
}

template <typename T>
inline Int64Type byte_offset(py::array_t<T>& arr, Ssize_tList indices) {
  ssize_t offset = 0;
  for (int i = 0; i < indices.size(); ++i) {
    ssize_t j = i;
    if (j < 0) {
      j = arr.shape(i) + j;
    }

    offset += *(indices.begin()+j) * arr.strides(j) / arr.itemsize();
  }

  return offset;
}

template <typename T>
inline Int64Type byte_offset(py::array_t<T>& arr, ssize_t i) {
  if (i >= 0) {
    return i;
  }
  else {
    return arr.size() + i;
  }
}

// template <typename T>
// inline const T& getitem(py::array_t<T>& arr, ssize_t i) {
//   return *((T*)arr.data() + byte_offset(arr, i));
// }

// template <typename T>
// inline const T& getitem(py::array_t<T>& arr, Ssize_tList indices) {
//   ssize_t offset = byte_offset(arr, indices);
//   return getitem(arr, offset);
// }

// template <typename T>
// inline void setitem(py::array_t<T>& arr, ssize_t i, char op, int v) {
//   ssize_t offset = byte_offset(arr, i);
//   *((T*)arr.mutable_data() + offset) = v;
// }

// template <typename T>
// inline void setitem(py::array_t<T>& arr, ssize_t i, char op, T v) {
//   ssize_t offset = byte_offset(arr, i);
//   *((T*)arr.mutable_data() + offset) = v;
// }

// template <typename T>
// inline void setitem(py::array_t<T>& arr, Ssize_tList i, char op, int v) {
//   ssize_t offset = byte_offset(arr, i);
//   *((T*)arr.mutable_data() + offset) = v;
// }

// template <typename T>
// inline void setitem(py::array_t<T>& arr, Ssize_tList i, char op, T v) {
//   ssize_t offset = byte_offset(arr, i);
//   *((T*)arr.mutable_data() + offset) = v;
// }


template<typename T, typename... Ix>
inline T& getitem(py::array_t<T> arr, Ix... args) {
  return arr.mutable_at(args...);
}

template<typename T1, typename T2, typename... Ix>
inline void setitem(py::array_t<T1> arr, T2 v, Ix... args) {
  arr.mutable_at(args...) = v;
}

template<typename T>
inline T& getitem_1d(py::array_t<T>& arr, size_t i) {
  return arr.mutable_data()[i];
}

template<typename T1, typename T2>
inline void setitem_1d(py::array_t<T1>& arr, T2 v, size_t i) {
  arr.mutable_data()[i] = v;
}

template<typename T>
inline T& getitem_1d(T* data, size_t i) {
  return data[i];
}

template<typename T1, typename T2>
inline void setitem_1d(T1* data, T2 v, size_t i) {
  data[i] = v;
}

template<typename T>
inline T& getitem_2d(py::array_t<T>& arr, size_t i, size_t j) {
  size_t s1 = arr.shape(1);
  return arr.mutable_data()[i*s1+j];
}

template<typename T1, typename T2>
inline void setitem_2d(py::array_t<T1>& arr, T2 v, size_t i, size_t j) {
  size_t s1 = arr.shape(1);
  arr.mutable_data()[i*s1+j] = v;
}

template<typename T>
inline T& getitem_2d(T* data, Int64Type s1, size_t i, size_t j) {
  return data[i*s1+j];
}

template<typename T1, typename T2>
inline void setitem_2d(T1* data, Int64Type s1, T2 v, size_t i, size_t j) {
  data[i*s1+j] = v;
}

template<typename T>
py::array_t<T> get_row(py::array_t<T>& arr, size_t i) {
  T* arr_data = arr.mutable_data();
  T* start = arr_data + arr.shape(1) * i;
  /* Note: the last argument specifies parent object that owns the data */
  py::array_t<T> ret = py::array_t<T>(arr.shape(1), start, arr); 
  return ret;
}

// template<typename T>
// py::array_t<T> sum_rows(py::array_t<T>& arr, py::array_t<int>& rows) {
//   int s1 = arr.shape(1);
//   py::array_t<T> ret = py::array_t<T>(s1);
//   T* ret_data = ret.mutable_data();
//   for (int i = 0; i < s1; ++i) {
//     ret_data[i] = 0;
//   }
  
//   T* arr_data = arr.mutable_data();

//   assert (rows.ndim() == 1);
//   const int* rows_data = rows.data();
//   for (int r = 0; r < rows.shape(0); r+=2) {
//     T* start = arr_data + s1 * rows_data[r];
//     for (int i = 0; i < s1; ++i) {
//       ret_data[i] += arr_data[i+s1 * rows_data[r]] + arr_data[i+s1 * rows_data[r+1]];
//     }
//   }
  
//   return ret;
// }


template<typename T>
py::array_t<T> sum_rows(py::array_t<T>& arr, py::array_t<int>& rows) {
  int s1 = arr.shape(1);
  py::array_t<T> ret = py::array_t<T>(s1);
  T* ret_data = ret.mutable_data();
  for (int i = 0; i < s1; ++i) {
    ret_data[i] = 0;
  }
  
  T* arr_data = arr.mutable_data();

  assert (rows.ndim() == 1);
  const int* rows_data = rows.data();
  for (int r = 0; r < rows.shape(0); r++) {
    T* start = arr_data + s1 * rows_data[r];
    for (int i = 0; i < s1; ++i) {
      //ret_data[i] += start[i];
      ret_data[i] += arr_data[i+s1 * rows_data[r]];
    }
  }
  
  return ret;
}

template<typename T>
void plus_eq(py::array_t<T> A, py::array_t<T> B) {
  assert(A.ndim() == B.ndim());
  assert(A.size() == B.size());

  T* A_data = A.mutable_data();
  const T* B_data = B.mutable_data();
  for (int i = 0; i < A.size(); ++i) {
    A_data[i] += B_data[i];    
  }
}

template<typename T>
void minus_eq(py::array_t<T>& A, py::array_t<T> B) {
  assert(A.ndim() == B.ndim());
  assert(A.size() == B.size());

  T* A_data = A.mutable_data();
  const T* B_data = B.mutable_data();
  for (int i = 0; i < A.size(); ++i) {
    A_data[i] -= B_data[i];    
  }
}

template<typename T>
py::array_t<T> get_col(py::array_t<T>& arr, size_t i) {
  T* arr_data = arr.mutable_data();
  T* start = arr_data + i;
  py::array_t<T> ret = py::array_t<T>({arr.shape(0)}, {arr.shape(1)}, start, arr); /* FIXME: this code compiles but I don't know what it does with the data pointer */
  return ret;

  // py::array_t<T> ret = py::array_t<T>(arr.shape(0));
  // T* arr_data = arr.mutable_data();
  // T* ret_data = ret.mutable_data();

  // int s1 = arr.shape(1);
  // for (int j = 0; j < ret.size(); ++j) {
  //   ret_data[j] = arr_data[i + j*s1];
  // }
  // return ret;
}

template<typename T>
void set_row(py::array_t<T>& arr, size_t i, T v) {
  T* arr_data = arr.mutable_data();
  T* start = arr_data + arr.shape(1) * i;
  for (int j = 0; j < arr.shape(1); ++j) {
    start[j] = v;
  }
}

template<typename T>
void set_row(py::array_t<T>& arr, size_t i, py::array_t<T> values) {
  T* arr_data = arr.mutable_data();
  T* arr_start = arr_data + arr.shape(1) * i;
  T* value_start = values.mutable_data();
  for (int j = 0; j < arr.shape(1); ++j) {
    arr_start[j] = value_start[j];
  }
}

template<typename T>
void set_col(py::array_t<T>& arr, size_t i, T v) {
  T* arr_data = arr.mutable_data();

  int s1 = arr.shape(1);
  for (int j = 0; j < arr.shape(0); ++j) {
    arr_data[i + j*s1] = v;
  }
}


// template<typename T, typename... Ix>
// void setitem(py::array_t<T>& arr, int v, Ix... args) {
//   arr.mutable_at(args...) = v;
// }

//template <typename T>
// void reshape(py::array arr, Ssize_tList t) {
//   arr.resize(t);
// }

// enum ElementType {
//   int32,
//   int64,
//   float32,
//   float64,
// };

// py::array empty(Ssize_tList s, std::string dtype="double") {
//   if (dtype == "int" || dtype == "int32") {
//     py::array_t<int> arr(s);
//     return arr;
//   }
//   else if (dtype == "int64") {
//     py::array_t<int64_t> arr(s);
//     return arr;
//   }
//   else if (dtype == "float" || dtype == "float32") {
//     py::array_t<float> arr(s);
//     return arr;
//   }
//   else if (dtype == "double" || dtype == "float64") {
//     py::array_t<double> arr(s);
//     return arr;
//   }
//   else {
//     std::cerr << "bad dtype: " << dtype << "\n";
//     exit(0);
//   }
  
// }


// py::array empty(size_t s, std::string dtype="double") {
//   if (dtype == "int" || dtype == "int32") {
//     py::array_t<int> arr(s);
//     return arr;
//   }
//   else if (dtype == "int64") {
//     py::array_t<int64_t> arr(s);
//     return arr;
//   }
//   else if (dtype == "float" || dtype == "float32") {
//     py::array_t<float> arr(s);
//     return arr;
//   }
//   else if (dtype == "double" || dtype == "float64") {
//     py::array_t<double> arr(s);
//     return arr;
//   }
//   else {
//     std::cerr << "bad dtype: " << dtype << "\n";
//     exit(0);
//   }
  
// }

template<typename T>
void init_to_zeros(py::array_t<T> arr) {
  auto d = arr.mutable_data();
  for (int i = 0; i < arr.size(); ++i) {
    *((T*)d) = 0;
    d++;
  }
}

template<typename T>
void fill(py::array_t<T> arr, T v) {
  auto d = arr.mutable_data();
  memset(d, v, arr.nbytes());
}

template<typename T>
inline void fill(py::array_t<T> arr, double v) {
  auto d = arr.mutable_data();
  memset(d, static_cast<T>(v), arr.nbytes());
}

static unsigned int g_seed = 123456789;


template<typename T=double>
py::array_t<T> numpy_random_rand(Ssize_tList s, T e=T()) {
  py::array_t<T> arr(s);
  auto d = arr.mutable_data();
  //#pragma omp parallel for
  for (int i = 0; i < arr.size(); ++i) {
    float x = ((float)rand()/(float)(RAND_MAX));
    *((T*)d) = x;
    //*((T*)d) = i;
    d++;
  }

  return arr;
}

template<typename T=double>
py::array_t<T> arange(Ssize_tList s, T e=T()) {
  py::array_t<T> arr(s);
  auto d = arr.mutable_data();
  for (int i = 0; i < arr.size(); ++i) {
    //*((T*)d) = rand();
    *((T*)d) = i;
    d++;
  }

  return arr;
}

template<typename T=double>
py::array_t<T> empty(Ssize_tList s, T e=T()) {
  py::array_t<T> arr(s);
  return arr;
}

template<typename T=double>
py::array_t<T> empty(std::vector<int>* s, T e=T()) {
  py::array_t<T> arr(*s);
  return arr;
}

template<typename T=double>
py::array_t<T> empty(std::vector<Int64Type>* s, T e=T()) {
  py::array_t<T> arr(*s);
  return arr;
}
//
//template<typename T=double>
//py::array_t<T> empty(std::vector<ssize_t>* s, T e=T()) {
//  py::array_t<T> arr(*s);
//  return arr;
//}


template<typename T=double>
py::array_t<T> empty(size_t s, T e=T()) {
  //py::array_t<T> arr(s);
  //return arr;
  return empty({(long) s}, e);
}

template<typename T=double>
py::array_t<T> empty_2d(std::vector<Int64Type>* s, T e=T()) {
  py::array_t<T> arr(*s);
  return arr;
}

template<typename T>
py::array_t<T> empty_like(py::array_t<T>& proto) {
  py::array_t<T> arr;
  if (proto.ndim() == 1) {
    arr = py::array_t<T>(proto.shape(0));
  }
  else if (proto.ndim() == 2) {
    arr = py::array_t<T>({proto.shape(0), proto.shape(1)});
  }
  else {
    assert(false && "only suuport 1d or 2d array");
  }
  return arr;
}

template<typename T>
py::array_t<double> empty_like_d(py::array_t<T>& proto) {
  py::array_t<double> arr(*proto.shape());
  return arr;
}

template<typename T=double>
py::array_t<T> copy(py::array_t<T> arr) {
  py::array_t<T> arr1 = empty_like(arr);
  auto d = arr.mutable_data();
  auto d1 = arr1.mutable_data();
  memcpy(d1, d, arr.nbytes());

  return arr1;
}


template<typename T=double>
py::array_t<T> zeros(Ssize_tList s, T e=T()) {
  py::array_t<T> arr = empty(s, e);
  //init_to_zeros(arr);
  fill(arr, 0);
  return arr;
}

template<typename T=double>
py::array_t<T> zeros(std::vector<int>* s, T e=T()) {
  py::array_t<T> arr = empty(s, e);
  fill(arr, 0);
  //init_to_zeros(arr);
  return arr;
}

template<typename T=double>
py::array_t<T> zeros_2d(std::vector<Int64Type>* s, T e=T()) {
  py::array_t<T> arr = empty_2d(s, e);
  fill(arr, 0);
  //init_to_zeros(arr);
  return arr;
}

template<typename T=double>
py::array_t<T> zeros(std::vector<Int64Type>* s, T e=T()) {
  py::array_t<T> arr = empty(s, e);
  fill(arr, 0);
  //init_to_zeros(arr);
  return arr;
}

template<typename T=double>
py::array_t<T> zeros(size_t s, T e=T()) {
  py::array_t<T> arr = empty(s, e);
  //init_to_zeros(arr);
  fill(arr, 0);
  return arr;
}

int rand() {
  std::srand(std::time(0));
  return std::rand();  
}

int rand(int min, int max) {
  return pydd::rand()%(max-min + 1) + min;
}


/*! @deprecated for now */ 
template <typename T>
class NpArray {
  py::array_t<T>& _arr; 
public:
  NpArray(py::array_t<T>& x): _arr(x) {
    
  }

  size_t shape(int i) {
    return _arr.shape(i);
  }

  size_t strides(int i) {
    return _arr.strides
      (i);
  }

  template<typename... Ix>
  T& at(Ix... args) {
    return _arr.mutable_at(args...);
  }
};

// template <typename T>
// class UCNpArray {
//   py::detail::unchecked_mutable_reference<T, -1l> _buf;
// public:
//   UCNpArray(py::array_t<T>& x): _buf(x.mutable_unchecked()) {
    
//   }

//   size_t shape(int i) {
//     return _buf.shape(i);
//   }

//   size_t strides(int i) {
//     return _buf.strides(i);
//   }


//   template<typename... Ix>
//   T& at(Ix... args) {
//     return _buf(args...);
//   }
// };

}

#endif  // NPARRAY_HPP
