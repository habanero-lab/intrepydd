Intrepydd compiles Python code with type annotations to optimized C++ code. Check out our paper to learn more: [Intrepydd: performance, productivity, and portability for data science application kernels](https://dl.acm.org/doi/10.1145/3426428.3426915).

# Requirements
Anaconda (Python3) is required to run Intrepydd. Besides, `requirements.txt` contains the required packages:

```bash
pip install -r requirements.txt
```

# Usage
To run the unit tests:

```bash
cd unit-tests
pytest test_*
```