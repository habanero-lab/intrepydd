from dummytypes import *

def hello():

    # Supported primitive types
    # (* means in progress)
    
    # - int
    # - float
    # - bool
    # - string*
    # - list*
    # - tuple*
    
    
    a, b, c = 0, 0, True
    d = (a + b) * -a
    ls = [0, 1, 1, 2]
    e = ls[0]
    if a:
        ls[1] = 3
    elif b:
        ls[1] = 4
    elif c:
        ls[1] = 5
    else:
        ls[1] = 6
        
    for e in ls:
        print(e)

    for i in range(3):
        print(ls[i])
    
    
hello()
