An Intrepydd program can perform basic operations on a numpy ndarray.
Currently only the following interfaces are supported (`r` is the ndarray):

- `r.ndim()` returns the number of dimensions
  
- `r.shape(dim)` returns the size of dimension `dim`

- `r.data(1, 2, ...)` and `r.mutable_data(1, 2, ...)` returns a pointer to the const T or T data, respectively, at the given indices. The latter is only available to proxies obtained via `a.mutable_unchecked()`.
  - The number of arguments has to match `r.ndim()` to index correctly. If the argument number is less than `r.ndim()`, a raw pointer is returned, which means nothing in Intrepydd code.

- `r.itemsize()` returns the size of an item in bytes, i.e. sizeof(T).

- `r.strides(dim)` returns the stride of dimension `dim`