#ifndef OPERATION_HPP
#define OPERATION_HPP

#include <cmath>

namespace pydd {
  template<typename T>
  inline T ope_minus(T x) { return -x; }
  template<typename T>
  inline T ope_abs(T x) { return abs(x); }
  template<typename T>
  inline bool ope_not(T x) { return !x; }
  template<typename T>
  inline bool ope_isnan(T x) { return std::isnan(x); }
  template<typename T>
  inline bool ope_isinf(T x) { return std::isinf(x); }
  template<typename T>
  inline double ope_sqrt(T x) { return std::sqrt(x); }
  template<typename T>
  inline double ope_exp(T x) { return std::exp(x); }
  template<typename T>
  inline double ope_log(T x) { return log(x); }
  template<typename T>
  inline double ope_cos(T x) { return cos(x); }
  template<typename T>
  inline double ope_sin(T x) { return sin(x); }
  template<typename T>
  inline double ope_tan(T x) { return tan(x); }
  template<typename T>
  inline double ope_acos(T x) { return acos(x); }
  template<typename T>
  inline double ope_asin(T x) { return asin(x); }
  template<typename T>
  inline double ope_atan(T x) { return atan(x); }

  template<typename T>
  inline T ope_nnz(T x, T y) { return x != 0 ? y + 1 : y; }
  template<typename T>
  inline T ope_add(T x, T y) { return x + y; }
  template<typename T>
  inline T ope_sub(T x, T y) { return x - y; }
  template<typename T>
  inline T ope_mul(T x, T y) { return x * y; }
  template<typename T>
  inline T ope_div(T x, T y) { return x / y; }
  template<typename T>
  inline T ope_min(T x, T y) { return x < y ? x : y; }
  template<typename T>
  inline T ope_max(T x, T y) { return x > y ? x : y; }

  template<typename T1, typename T2>
  inline double ope_add2(T1 x, T2 y) { return x + y; }
  template<typename T1, typename T2>
  inline double ope_sub2(T1 x, T2 y) { return x - y; }
  template<typename T1, typename T2>
  inline double ope_mul2(T1 x, T2 y) { return x * y; }
  template<typename T1, typename T2>
  inline double ope_div2(T1 x, T2 y) { return x / y; }
  template<typename T1, typename T2>
  inline double ope_pow(T1 base, T2 exp) { return pow(base, exp); }
  template<typename T1, typename T2>
  inline double ope_log2(T1 x, T2 base) { return log(x) / log(base); }
  template<typename T1, typename T2>
  inline double ope_max2(T1 x, T2 y) { return x > y ? double(x) : double(y); }

  template<typename T1, typename T2>
  inline bool ope_equal(T1 x, T2 y) { return x == y; }
  template<typename T1, typename T2>
  inline bool ope_not_equal(T1 x, T2 y) { return x != y; }
  template<typename T1, typename T2>
  inline bool ope_less(T1 x, T2 y) { return x < y; }
  template<typename T1, typename T2>
  inline bool ope_greater(T1 x, T2 y) { return x > y; }
  template<typename T1, typename T2>
  inline bool ope_less_equal(T1 x, T2 y) { return x <= y; }
  template<typename T1, typename T2>
  inline bool ope_greater_equal(T1 x, T2 y) { return x >= y; }
  template<typename T1, typename T2>
  inline bool ope_close(T1 x, T2 y) { return abs(x) <= y; }

  template<typename T1, typename T2>
  inline bool ope_logical_and(T1 x, T2 y) { return x && y; }
  template<typename T1, typename T2>
  inline bool ope_logical_or(T1 x, T2 y) { return x || y; }
  template<typename T1, typename T2>
  inline bool ope_logical_xor(T1 x, T2 y) { return !x != !y; }
}

#endif  // OPERATION_HPP
