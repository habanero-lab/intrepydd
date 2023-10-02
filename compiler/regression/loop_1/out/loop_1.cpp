<%
cfg['compiler_args'] = ['-std=c++11', '-I/Users/jun/git/DDARING/src/phase1-toolchain/compiler/include/']
setup_pybind11(cfg)
%>

#include <iostream>
#include <vector>
#include <cstdlib>
#include <cstdio>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "rt.hpp"
#include "NpArray.hpp"

namespace py = pybind11;


double sum_1d(size_t size, py::array_t<double> a) {
/* Declarations */
double f;
size_t c;

f = 0.0;
for (int _i = 0; _i < size; _i += 1) {
c = _i;
f += pydd::at(a,c);
};
return f;
}

PYBIND11_PLUGIN(loop_1) {
  pybind11::module m("loop_1", "auto-compiled c++ extension");
  m.def("sum_1d", &sum_1d,py::arg().noconvert(),py::arg().noconvert());
  return m.ptr();
}
