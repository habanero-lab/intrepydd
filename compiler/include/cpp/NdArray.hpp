#ifndef ARRAY_HPP
#define ARRAY_HPP

#include "shared/types.hpp"

namespace pybind11 {
template<typename T>
class array_t {
  Int64Type _ndim;
  std::vector<Int64Type>* _shapes;
  Int64Type _size;
  T* _data;
public:
  array_t();
  array_t(std::vector<Int64Type>& shapes);
  array_t(std::initializer_list<Int64Type> shapes);
  Int64Type shape(Int64Type i);
  T* mutable_data();
  Int64Type ndim()  { return _ndim; }
};

template<typename T>
array_t<T>::array_t() {
  
}

template<typename T>
array_t<T>::array_t(std::vector<Int64Type>& shapes) {
  _shapes = new std::vector<Int64Type>(shapes);
  _size = 0;
  _ndim = shapes.size();
  for (auto i: shapes) {
    _size *= i;
  }
  _data = (T*)malloc(sizeof(T) * _size);
}

template<typename T>
array_t<T>::array_t(std::initializer_list<Int64Type> shapes) {
  _shapes = new std::vector<Int64Type>();
  _size = 0;
  _ndim = shapes.size();
  for (auto i: shapes) {
    _shapes->push_back(i);
  }
  _data = (T*)malloc(sizeof(T) * _size);
}

template<typename T>
Int64Type array_t<T>::shape(Int64Type i) {
  return _shapes->at(i);
}

template<typename T>
T* array_t<T>::mutable_data() {
  return _data;
}



}

namespace py = pybind11;

#endif
