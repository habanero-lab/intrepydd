#ifndef CPPRT_H
#define CPPRT_H

#include <vector>
#include <cstdio>
#include <iostream>
#include <cstdint>
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <map>

#include <pybind11/pybind11.h>
namespace py = pybind11;
using namespace pybind11::literals;

namespace pydd {

template <typename T>
void print(std::vector<T>* v) {
  for(T e: *v) {
    py::print(e, "end"_a=" ");
  }
}

template <typename T>
void print(T e) {
  py::print(e);
}

template <typename T, typename... Args>
void print(T first, Args... args) {
  py::print(first);
  print(args...);
}


}

#endif
