// #ifndef NPARRAY_HPP
// #define NPARRAY_HPP

// #include <ctime>
// #include <cstdlib>
// #include <pybind11/pybind11.h>
// #include <pybind11/numpy.h>
// #include "rt.hpp"


// namespace py = pybind11;
// //namespace detail = pybind11::detail;

// namespace pydd {

// /*! 
//   Global/built-in functions that operate on Numpy arrays go here. 

//   py::array_t is a C++ class that wraps a Numpy array.
//   It only supports a couple essentional interfaces such as
//   getting the shape, accessing each element etc.
// */

// typedef std::initializer_list<ssize_t> Ssize_tList;
// typedef int64_t Int64Type;

// Int64Type len(py::array& arr) {
//   return arr.shape(0);
// }

// template <typename T>
// Int64Type shape(py::array_t<T>& arr, int i) {
//   return arr.shape(i);
// }

// template <typename T>
// std::vector<Int64Type>* shape(py::array_t<T>& arr) {
//   std::vector<Int64Type>* s = new std::vector<Int64Type>();
//   for (int i = 0; i < arr.ndim(); ++i) {
//     s->push_back(arr.shape(i));
//   }
//   return s;
// }

// template <typename T>
// Int64Type stride(py::array_t<T>& arr, int i) {
//   return arr.strides(i);
// }

// template <typename T>
// Int64Type ndim(py::array_t<T>& arr) {
//   return arr.ndim();
// }

// // template <typename T>
// // void append(py::array_t<T>& arr, T i) {
// //   arr.append(i);
// // }

  
// inline Int64Type byte_offset(py::array& arr, Ssize_tList indices) {
//   ssize_t offset = 0;
//   for (int i = 0; i < indices.size(); ++i) {
//     ssize_t j = i;
//     if (j < 0) {
//       j = arr.shape(i) + j;
//     }

//     offset += *(indices.begin()+j) * arr.strides(j) / arr.itemsize();
//   }

//   return offset;
// }

// inline Int64Type byte_offset(py::array& arr, ssize_t i) {
//   if (i >= 0) {
//     return i;
//   }
//   else {
//     return arr.size() + i;
//   }
// }

// // template <typename T>
// // inline const T& getitem(py::array_t<T>& arr, ssize_t i) {
// //   return *((T*)arr.data() + byte_offset(arr, i));
// // }

// // template <typename T>
// // inline const T& getitem(py::array_t<T>& arr, Ssize_tList indices) {
// //   ssize_t offset = byte_offset(arr, indices);
// //   return getitem(arr, offset);
// // }

// // template <typename T>
// // inline void setitem(py::array_t<T>& arr, ssize_t i, char op, int v) {
// //   ssize_t offset = byte_offset(arr, i);
// //   *((T*)arr.mutable_data() + offset) = v;
// // }

// // template <typename T>
// // inline void setitem(py::array_t<T>& arr, ssize_t i, char op, T v) {
// //   ssize_t offset = byte_offset(arr, i);
// //   *((T*)arr.mutable_data() + offset) = v;
// // }

// // template <typename T>
// // inline void setitem(py::array_t<T>& arr, Ssize_tList i, char op, int v) {
// //   ssize_t offset = byte_offset(arr, i);
// //   *((T*)arr.mutable_data() + offset) = v;
// // }

// // template <typename T>
// // inline void setitem(py::array_t<T>& arr, Ssize_tList i, char op, T v) {
// //   ssize_t offset = byte_offset(arr, i);
// //   *((T*)arr.mutable_data() + offset) = v;
// // }


// template<typename T, typename... Ix>
// inline T& getitem(py::array_t<T>& arr, Ix... args) {
//   return arr.mutable_at(args...);
// }

// template<typename T, typename... Ix>
// inline void setitem(py::array_t<T>& arr, T v, Ix... args) {
//   arr.mutable_at(args...) = v;
// }

// template<typename T>
// inline T& getitem_1d(py::array_t<T>& arr, size_t i) {
//   return arr.mutable_data()[i];
// }

// template<typename T>
// inline void setitem_1d(py::array_t<T>& arr, T v, size_t i) {
//   arr.mutable_data()[i] = v;
// }

// template<typename T>
// inline T& getitem_1d(T* data, size_t i) {
//   return data[i];
// }

// template<typename T>
// inline void setitem_1d(T* data, T v, size_t i) {
//   data[i] = v;
// }

// template<typename T>
// inline T& getitem_2d(py::array_t<T>& arr, size_t i, size_t j) {
//   size_t s1 = arr.shape(1);
//   return arr.mutable_data()[i*s1+j];
// }

// template<typename T>
// inline void setitem_2d(py::array_t<T>& arr, T v, size_t i, size_t j) {
//   size_t s1 = arr.shape(1);
//   arr.mutable_data()[i*s1+j] = v;
// }

// template<typename T>
// inline T& getitem_2d(T* data, Int64Type s1, size_t i, size_t j) {
//   return data[i*s1+j];
// }

// template<typename T>
// inline void setitem_2d(T* data, Int64Type s1, T v, size_t i, size_t j) {
//   data[i*s1+j] = v;
// }


// // template<typename T, typename... Ix>
// // void setitem(py::array_t<T>& arr, int v, Ix... args) {
// //   arr.mutable_at(args...) = v;
// // }

// //template <typename T>
// // void reshape(py::array arr, Ssize_tList t) {
// //   arr.resize(t);
// // }

// // enum ElementType {
// //   int32,
// //   int64,
// //   float32,
// //   float64,
// // };

// template<typename T>
// py::array_t<T> empty_like(py::array_t<T>& proto) {
//   py::array_t<T> arr(*proto.shape());
//   return arr;
// }

// template<typename T>
// py::array_t<double> empty_like_d(py::array_t<T>& proto) {
//   py::array_t<double> arr(*proto.shape());
//   return arr;
// }

// template<typename T>
// void init_to_zeros(py::array_t<T> arr) {
//   auto d = arr.mutable_data();
//   for (int i = 0; i < arr.size(); ++i) {
//     *((T*)d) = 0;
//     d++;
//   }
// }

// template<typename T=double>
// py::array empty(Ssize_tList s, T e=T()) {
//   py::array_t<T> arr(s);
//   return arr;
// }

// // template<typename T=double>
// // py::array empty(std::vector<int>* s, T e=T()) {
// //   py::array_t<T> arr(*s);
// //   return arr;
// // }

// template<typename T=double>
// py::array empty(std::vector<Int64Type>* s, T e=T()) {
//   py::array_t<T> arr(*s);
//   return arr;
// }

// template<typename T=double>
// py::array empty_2d(std::vector<Int64Type>* s, T e=T()) {
//   py::array_t<T> arr(*s);
//   return arr;
// }

// template<typename T=double>
// py::array empty(size_t s, T e=T()) {
//   py::array_t<T> arr(s);
//   return arr;
// }

// template<typename T=double>
// py::array zeros(Ssize_tList s, T e=T()) {
//   py::array_t<T> arr = empty(s, e);
//   init_to_zeros(arr);
//   return arr;
// }

// template<typename T=double>
// py::array zeros(std::vector<int>* s, T e=T()) {
//   py::array_t<T> arr = empty(s, e);
//   init_to_zeros(arr);
//   return arr;
// }

// template<typename T=double>
// py::array zeros_2d(std::vector<Int64Type>* s, T e=T()) {
//   py::array_t<T> arr = empty_2d(s, e);
//   init_to_zeros(arr);
//   return arr;
// }

// // template<typename T=double>
// // py::array zeros_2d(std::vector<int>* s, T e=T()) {
// //   py::array_t<T> arr = empty_2d(s, e);
// //   init_to_zeros(arr);
// //   return arr;
// // }

// template<typename T=double>
// py::array zeros(std::vector<Int64Type>* s, T e=T()) {
//   py::array_t<T> arr = empty(s, e);
//   init_to_zeros(arr);
//   return arr;
// }

// template<typename T=double>
// py::array zeros(size_t s, T e=T()) {
//   py::array_t<T> arr = empty(s, e);
//   init_to_zeros(arr);
//   return arr;
// }

// // py::array zeros(size_t s, std::string dtype="double") {
// //   py::array arr = empty(s, dtype);
// //   init_to_zeros(arr);
// //   return arr;
// // }

// int rand() {
//   srand(time(0));
//   return std::rand();  
// }

// int rand(int min, int max) {
//   return pydd::rand()%(max-min + 1) + min;
// }


// /*! @deprecated for now */ 
// template <typename T>
// class NpArray {
//   py::array_t<T>& _arr; 
// public:
//   NpArray(py::array_t<T>& x): _arr(x) {
    
//   }

//   size_t shape(int i) {
//     return _arr.shape(i);
//   }

//   size_t strides(int i) {
//     return _arr.strides
//       (i);
//   }

//   template<typename... Ix>
//   T& at(Ix... args) {
//     return _arr.mutable_at(args...);
//   }
// };

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

// // template <typename T, ssize_t Dims>
// // class MutableNpArray: public py::detail::unchecked_mutable_reference <T, Dims> {
// //   friend class py::array;
// //   using Base = py::detail::unchecked_reference<T, Dims>;

// //   template<typename... Ix>
// //   T& at(Ix... args) {
// //     return _buf(args...);
// //   }

// // };

// }

// #endif  // NPARRAY_HPP
