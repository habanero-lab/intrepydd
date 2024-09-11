from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(name='Kernel app',
      ext_modules=cythonize("kernel.pyx"),
      include_dirs=[numpy.get_include()])
