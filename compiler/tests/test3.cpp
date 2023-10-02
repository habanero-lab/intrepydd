<%
cfg['compiler_args'] = ['-std=c++11', '-I/home/tong/DDARING/src/phase1-toolchain/compiler/include/']
setup_pybind11(cfg)
%>

#include <iostream>
#include <vector>
#include <cstdlib>
#include <cstdio>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "headers.hpp"

namespace py = pybind11;


void print_ls(pydd::Vector<int>* vec) {
/* Declarations */
double sum;
int e;

sum = 0.0;
for (int _i = 0; _i < pydd::len(vec); _i += 1) {
e = pydd::at(vec, _i);
sum += pydd::pow(e, 2);
pydd::print(e);
};
pydd::print(pydd::pow(sum, (double)1 / 2));
}

void hello() {
/* Declarations */
int a;
double b;
bool c;
pydd::Vector<int>* ls1;
pydd::Vector<int>* ls2;
int i;
int j;

a = 0; b = 0.0; c = true;
ls1 = new pydd::Vector<int>{0, 1, 1, 2};
ls2 = new pydd::Vector<int>{};
for (int _i = 0; _i < pydd::len(ls1); _i += 1) {
i = _i;
j = 0;
if (i == 0) {
j = 10;
} else {
j = i + 1;
};
ls2->append(j);
};
print_ls(ls2);
}

PYBIND11_PLUGIN(test3) {
  pybind11::module m("test3", "auto-compiled c++ extension");
  m.def("print_ls", &print_ls,py::arg().noconvert());
  m.def("hello", &hello);
  return m.ptr();
}
