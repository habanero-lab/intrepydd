<%
cfg['compiler_args'] = ['-std=c++11', '-I/home/tong/DDARING/src/phase1-toolchain/compiler/include/']
cfg['linker_args'] = []
setup_pybind11(cfg)
%>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "rt.hpp"
#include "NpArray.hpp"

namespace py = pybind11;


void hello() {
/* Declarations */
int a;
int b;
bool c;
int d;
std::vector<int>* ls;
int e;
int i;

a = 0; b = 0; c = true;
d = ((a + b) * -a);
ls = new std::vector<int>{0, 1, 1, 2};
e = pydd::getitem(ls, 0);
if (a) {
pydd::setitem(ls, 3, 1);
} else if (b) {
pydd::setitem(ls, 4, 1);
} else if (c) {
pydd::setitem(ls, 5, 1);
} else {
pydd::setitem(ls, 6, 1);
};
for (int _i = 0; _i < pydd::len(ls); _i += 1) {
e = pydd::getitem(ls, _i);
pydd::print(e);
};
for (int _i = 0; _i < 3; _i += 1) {
i = _i;
pydd::print(pydd::getitem(ls, i));
};
}

PYBIND11_PLUGIN(test1) {
  pybind11::module m("test1", "auto-compiled c++ extension");
  m.def("hello", &hello);
  return m.ptr();
}
