To run the Python implementation:
```bash
$ cd python
$ ./run.sh
```

To run the Numba implementation:
```bash
$ cd numba
$ ./run.sh
```

To run the Numba-cache implementation:
```bash
$ cd numba-cache
$ ./run.sh
```

To run the Intrepydd implementation:
```bash
$ cd intrepydd
$ ./comp.sh  # compile the Intrepydd kernel to a Python module
$ ./run.sh
```

Note that the this current version only runs the PR-nibble algorithm (the output matrix is printed out). The ISTA algorithm is commented out.