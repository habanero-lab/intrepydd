

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
    //#include "NpArray.hpp"    

namespace py = pybind11;

// Passing in an array of doubles
void twice(py::array_t<double> xs) {
  py::buffer_info info = xs.request();
  auto ptr = static_cast<double *>(info.ptr);

  int n = 1;
  for (auto r: info.shape) {
    n *= r;
  }

  for (int i = 0; i <n; i++) {
    *ptr++ *= 2;
  }
}

// Passing in a generic array
double sum(py::array xs) {
  py::buffer_info info = xs.request();
  auto ptr = static_cast<double *>(info.ptr);

  int n = 1;
  for (auto r: info.shape) {
    n *= r;
  }

  double s = 0.0;
  for (int i = 0; i <n; i++) {
    s += *ptr++;
  }

  return s;
}

/*!
  Imaginary Intrepydd code:
  
  def sum_3d(xs: np.ndarray):
    sum = 0
    for i in range(xs.shape(0)):
      for j in range(xs.shape(1)):
        for k in range(xs.shape(2)):
          sum += xs.at(i, j, k)
    return sum

  A numpy array have these interfaces, and any operation
  is performed by a function call, rather than by operator
  overloading.
 */
double sum_3d(py::array_t<double> x) {
  pydd::NpArray<double>* r = new pydd::NpArray<double>(x);
  //py::detail::unchecked_mutable_reference<double, -1l> r = x.mutable_unchecked(); // x must have ndim = 3; can be non-writeable
  double sum = 0;
  for (ssize_t i = 0; i < r->shape(0); i++)
    for (ssize_t j = 0; j < r->shape(1); j++)
      for (ssize_t k = 0; k < r->shape(2); k++)
        sum += r->at(i, j, k);
  delete r;
  return sum;
}

void inc_3d(py::array_t<double> x) {
  pydd::NpArray<double>* r = new pydd::NpArray<double>(x);
  for (ssize_t i = 0; i < r->shape(0); i++)
    for (ssize_t j = 0; j < r->shape(1); j++)
      for (ssize_t k = 0; k < r->shape(2); k++)
        r->at(i, j, k) += 1.0;
  delete r;
}

// double sum_3d(py::array_t<double> x) {
//   py::detail::unchecked_mutable_reference<double, -1l> r = x.mutable_unchecked(); // x must have ndim = 3; can be non-writeable
//   double sum = 0;
//   for (ssize_t i = 0; i < r.shape(0); i++)
//     for (ssize_t j = 0; j < r.shape(1); j++)
//       for (ssize_t k = 0; k < r.shape(2); k++)
//         sum += r(i, j, k);
        
//   return sum;
// }

// void inc_3d(py::array_t<double> x) {
//   auto r = x.mutable_unchecked(); // Will throw if ndim != 3 or flags.writeable is false
//   for (ssize_t i = 0; i < r.shape(0); i++)
//     for (ssize_t j = 0; j < r.shape(1); j++)
//       for (ssize_t k = 0; k < r.shape(2); k++)
//         r(i, j, k) += 1.0;
// }

PYBIND11_PLUGIN(code) {
  pybind11::module m("code", "auto-compiled c++ extension");
  m.def("sum", &sum);
  m.def("sum_3d", &sum_3d, py::arg().noconvert());
  m.def("inc_3d", &inc_3d, py::arg().noconvert());
  m.def("twice", &twice);
  return m.ptr();
}
