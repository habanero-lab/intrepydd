#include<iostream>
#include<vector>
#include<cstdlib>
#include<cstdio>
#include<cpprt.h>
int main() {
/* Declarations */
int a;
double b;
bool c;
std::vector<int>* ls;
int e;

a = 0; b = 0.0; c = true;
ls = new std::vector<int>{0, 1, 1, 2};
for (int _i = 0; _i < pydd::len(ls); _i += 1) {
e = ls->at(_i);
pydd::print(e);
};
}
int vec_norm(std::vector<double>* vec, int ord) {
/* Declarations */
int a;

a = 0;
}
