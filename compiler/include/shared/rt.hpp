#ifndef CPPRT_H
#define CPPRT_H

#include <vector>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <stdint.h>
#include <string>
//#include <cstdint>
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <chrono>
#include <map>
#include <unordered_map>


namespace pydd {
std::vector<const char*> callstack;

void append_to_call_stack(const char* funcname) {
  callstack.push_back(funcname);
}

void print_call_stack() {
  std::cout << "=========== Pydd call stack =========" << std::endl;
  for (auto f: callstack) {
    std::cout << f << std::endl;
  }
}

void _debug_print(int n) {
  std::cout << "[DEBUG] location stamp: " <<  n << std::endl;
}

  template <typename T>
  size_t len(T* container) {
    return container->size();
  }

  template <typename T>
  size_t len(std::initializer_list<T> ls) {
    return ls.size();
  }


  template <typename T>
  void print(T e) {
    //print(e);
    std::cout << e << std::endl;
  }

  template <typename T, typename... Args>
  void print(T first, Args... args) {
    print(first);
    print(args...);
  }

  template <typename T>
  void print(std::vector<T>* v) {
    for(T e: *v) {
      print(e, " ");
    }
    print('\n');
  }

  template <typename T>
  T& getitem(std::vector<T>* container, size_t i) {
    return container->at(i);
  }

  //template <typename K, typename V>
  int getitem(typename std::map<int, int>::iterator& it) {
    return it->first;
  }

  template <typename T>
  void setitem(std::vector<T>* container, T v, size_t i) {
    (*container)[i] = v;
  }

  template <typename K, typename V>
  void setitem(std::map<K, V>* container, V v, K i) {
    (*container)[i] = v;
  }

  template <typename K, typename V>
  V getitem(std::map<K, V>* container, K i) {
    return (*container)[i];
  }

  template <typename K, typename V>
  void setitem(std::unordered_map<K, V>* container, V v, K i) {
    (*container)[i] = v;
  }

  template <typename K, typename V>
  V getitem(std::unordered_map<K, V> *container, K i) {
      return (*container)[i];
  }


  std::vector<int>* range(size_t len) {
    std::vector<int>* ret = new std::vector<int>();
    ret->resize(len);
    for (int i = 0; i < len; ++i) {
      (*ret)[i] = i;
    }
    return ret;
  }

  template <typename T>
  void append(std::vector<T>* vec, T v) {
    vec->push_back(v);
  }
  
  template <typename T>
  T pair_first(std::pair<T, bool>& pa) {
    return pa.first;
  }

  template <typename T>
  bool pair_second(std::pair<T, bool>& pa) {
    return pa.second;
  }

  template <typename T>
  T build_tuple(T x) {
    return x;
  }

  template<typename T>
  std::vector<T>* build_list(std::initializer_list<T> t) {
    std::vector<T>* v = new std::vector<T>(t);
    return v;
  }

  template <typename T>
  T abs(T x) {
    return std::abs(x);
  }
  
  double pow(double base, double exp) {
    return std::pow(base, exp);
  }

  double log(double x) {
    return std::log(x);
  }

  template <typename T>
  T iadd(T x, T y) {
    return x + y;
  }
  /*
    template <typename T>
    T add(T x, T y) {
    return x + y;
    }

    template <typename T>
    T sub(T x, T y) {
    return x - y;
    }
  */
  template <typename T>
  double truediv(T x, T y) {
    return (double)x / y;
  }

  int int32() {
    return 0;
  }

  int64_t int64() {
    return 0;
  }

  float float32() {
    return 0;
  }

  double float64() {
    return 0;
  }

  bool boolean() {
    return 0;
  }

  template <typename T>
  int int32(T x) {
    return (int)x;
  }

int stoi(std::string& s) {
  return std::atoi(s.c_str());
  // printf("stoi..%d\n", std::stoi(s));
  // return std::stoi(s);
}

int hextoi(std::string& s) {
  unsigned int x;   
  std::stringstream ss;
  ss << std::hex << s;
  ss >> x;
  return x;
}

int strtol(std::string& s, int base) {
  return std::strtol(s.c_str(), NULL, base);
}

  template <typename T>
  int64_t int64(T x) {
    return (int64_t)x;
  }

  template <typename T>
  float float32(T x) {
    return (float)x;
  }

  template <typename T>
  double float64(T x) {
    return (double)x;
  }

int randint(int low, int high) {
  //srand(time(NULL));
  int n = std::rand() % (high-low+1) + low;
  return n;
}

// inline function to swap two numbers
inline void swap(char *x, char *y) {
	char t = *x; *x = *y; *y = t;
}

// function to reverse buffer[i..j]
inline char* reverse(char *buffer, int i, int j)
{
	while (i < j)
		swap(&buffer[i++], &buffer[j--]);

	return buffer;
}

// Iterative function to implement itoa() function in C
char* itoa(int value, char* buffer, int base)
{
	// invalid input
	if (base < 2 || base > 32)
		return buffer;

	// consider absolute value of number
	int n = abs(value);
  //int n = value;

	int i = 0;
	while (n) {
		//int r = n % base;
    int r;
    if (base == 16) {
      r = n - (n >> 4)*16;
    }
    else {
      r = n % base;
    }

		if (r >= 10) 
			buffer[i++] = 65 + (r - 10);
		else
			buffer[i++] = 48 + r;

		//n = n / base;
    if (base == 16) {
      n = n >> 4;
    }
    else {
      n = n / base;
    }
	}

	// if number is 0
	if (i == 0)
		buffer[i++] = '0';

	// If base is 10 and value is negative, the resulting string 
	// is preceded with a minus sign (-)
	// With any other base, value is always considered unsigned
	if (value < 0 && base == 10)
		buffer[i++] = '-';

	buffer[i] = '\0'; // null terminate string

	// reverse the string and return it
	return reverse(buffer, 0, i - 1);
}

inline std::string hex(int n) {
  char hex[17] = {0};

  //sprintf(hex, "%x", n);
  itoa(n, hex, 16);
 
  std::string s(hex);
  //printf("hex: %d, %s\n", n, s.c_str());
  return s;
}



class Timer
{
public:
  Timer() : beg_(clock_::now()) {}
  void reset() { beg_ = clock_::now(); }
  double elapsed() const { 
    return std::chrono::duration_cast<second_>
      (clock_::now() - beg_).count(); }

private:
  typedef std::chrono::high_resolution_clock clock_;
  typedef std::chrono::duration<double, std::ratio<1> > second_;
  std::chrono::time_point<clock_> beg_;
};


Timer glb_timer;

double time() {
  return glb_timer.elapsed();
}

}


/* deprecated */
template <typename T>
class Vector {
  std::vector<T> _v;
public:
  Vector(std::initializer_list<T> t) {
    _v = std::vector<T>(t);
  }

  void append(T e) {
    _v.push_back(e);
  }

  T& at(int i) {
    return _v.at(i);
  }

  size_t size() {
    return _v.size();
  }
};

  
template <typename T>
struct Iter {
  //typename std::vector<T>::iterator cur;
  //typename std::vector<T>::iterator end;
  size_t index;
  typename std::vector<T>* vec;
};

template <typename T>
Iter<T>* getiter(std::vector<T>* v) {
  Iter<T>* iter = new Iter<T>();
  iter->index = 0;
  iter->vec = v;

  return iter;
}

template <typename T>
std::pair<T, bool> iternext(Iter<T>* it) {
  T v;
  
  bool hasNext = false;
  if (it->index < it->vec->size()) {
    hasNext = true;
    v = (*it->vec)[it->index];
  }
  //printf("v: %d\n", v);
  //fflush(stdout);
  std::pair<T, bool> p(v, hasNext);
  it->index++;
  return p;
}

template <typename T>
T& at(Vector<T>* container, size_t i) {
  return container->at(i);
}

template <typename T>
T static_getitem(std::vector<T>* container, size_t i) {
  return container->at(i);
}

#endif
