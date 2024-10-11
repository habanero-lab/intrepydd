Intrepydd compiles Python code with type annotations to optimized C++ code. Check out our paper to learn more: [Intrepydd: performance, productivity, and portability for data science application kernels](https://dl.acm.org/doi/10.1145/3426428.3426915).

# Install
Anaconda (Python3) is required to run Intrepydd. Install intrepydd using `pip`:

```bash
pip install intrepydd
```

# Usage Example

```bash
import intrepydd
from intrepydd import float64

def foo() -> float64:
    a = 1.0
    b = 2.0
    c = (a + b) * 3.0 # type: float64
    return c

foo1 = intrepydd.compile(foo)
print(foo1())
```