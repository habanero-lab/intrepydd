from dummytypes import * 

def foo(n: double):
    d: Dict(int, double) = {}
    d[0] = cos(1.1)
    d[1] = 2.2
    d[2] = n

    for i in d:
        print('key:', i)
        print('value:', d[i])
        print('')
        
foo(3.0)
