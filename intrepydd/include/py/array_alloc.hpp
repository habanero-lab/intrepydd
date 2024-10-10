#ifndef ARRAY_ALLOC_HPP
#define ARRAY_ALLOC_HPP

template<typename T1, typename T2>
inline py::array_t<T2> alloc_same_shape_array(py::array_t<T1> &arr, T2 ret_type, std::string format) {
  py::buffer_info buf = arr.request();
  buf.ptr = NULL;
  if (!format.empty())
    buf.format = format;
  py::ssize_t size = sizeof(T2);
  if (buf.itemsize != size) {
    double scale = (double) size / buf.itemsize;
    buf.itemsize = size;
    for (int d = 0; d < buf.ndim; d++)
      buf.strides[d] *= scale;
  }
  return py::array_t<T2>(buf);
}

template<typename T>
inline py::array_t<T> alloc_0d_array(T ret_value, std::string format) {
  py::buffer_info buf;
  buf.ptr = NULL;
  buf.itemsize = sizeof(T);
  buf.format = format;
  buf.ndim = 1;
  buf.shape = std::vector<py::ssize_t> {1};
  buf.strides = std::vector<py::ssize_t> {buf.itemsize};
  py::array_t<T> arr = py::array_t<T>(buf);
  auto data = arr.mutable_data();
  ((T*)data)[0] = ret_value;
  return arr;
}

template<typename T>
inline py::array_t<T> alloc_1d_array(py::ssize_t size, T ret_type, std::string format) {
  py::buffer_info buf;
  buf.ptr = NULL;
  buf.itemsize = sizeof(T);
  buf.format = format;
  buf.ndim = 1;
  buf.shape = std::vector<py::ssize_t> {size};
  buf.strides = std::vector<py::ssize_t> {buf.itemsize};
  return py::array_t<T>(buf);
}

template<typename T>
inline py::array_t<T> alloc_2d_array(py::ssize_t nrows, py::ssize_t ncols, T ret_type, std::string format) {
  py::buffer_info buf;
  buf.ptr = NULL;
  buf.itemsize = sizeof(T);
  buf.format = format;
  buf.ndim = 2;
  buf.shape = std::vector<py::ssize_t> {nrows, ncols};
  buf.strides = std::vector<py::ssize_t> {ncols * buf.itemsize, buf.itemsize};
  return py::array_t<T>(buf);
}

#endif  // ARRAY_ALLOC_HPP
