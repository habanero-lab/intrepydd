This compiler compiles an Intrepydd program to a static library
or an executable.

# Dependencies
The following Python packages are required:

- typed_ast
- cppimport
- pybind11
- numpy

Just run

```
$ pip install typed_ast cppimport pybind11 numpy
```

# Build a Python Module

```python
# Intrepydd file demo/demos.pydd
def demo1():
  a = [1,2,3]
  for i in a:
    print(i)
    
```

Compile the intrepydd code to a Python module:

```
$ cd demo-04-23-2019/; ../pyddc demos.pydd
```

Invoke Intrepydd function in a client Python code:
```python
# Python file demo/client.py
import demos # import your Intrepydd module

demos.demo1()
```

Run the client Python file:
```
$ python client.py
```

# Python semantics
Note that in general Intrepydd imitates Python3's semantics
rather than Python2. For example, `/` in Intrepydd would be
a true division, and `//` is a floor division.

# Add new library call
Suppose you want to add a new library call `foo` which has
some custom compiler flag and linker flag requirement. You
can cluster all such library functions that have the same
compiler/linker flags (library dependences) into one header
file such as `foos.hpp`. Then edit file `libfuncs.py` and
add entry in `funcinfo` and `packageinfo`.

At compile time, the compiler looks up this table to determine
what header file to include, and what flags to supply to the
C++ compiler.

An existing example:

The library function `dsyrk` relies on cblas call `cblas_dsyrk`
so using this function requires additional compiler and linker
flags for the C++ compiler. Suppose cblas library is already
installed on the machine, to add `dsyrk` to Intrepydd,
the developer needs to first
reate a header file. This file should contain all function calls
that have the same third-party library dependences (such as blas).
In `include/`, a `lib.hpp` is created.

Then the developer needs to add such entries to `funcinfo` and
`packageinfo` in `libfuncs.py`:

```python
funcinfo = {
    ... # other existing stuff         
    'pydd_dsyrk': [mytypes.float64_ndarray,
                   'lib'],
}

packageinfo = {
    ...
    'lib': ['-I /usr/include/openblas',
              '-lblas']
}

```

Now the compiler knows `dsyrk` is defined in `lib.hpp`, including
which requires extra compiler flag `-I /usr/include/openblas` and
extra linker flag `-lblas`.
