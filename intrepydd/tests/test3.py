from iptypes import List

def print_ls(vec: List(int)):
    sum = 0.0
    for e in vec:
        sum += e ** 2
        print(e)
    print(sum**(1/2))    
    
def hello():
    # Supported primitive types
    # (* is in progress)
    
    # - int
    # - float
    # - bool
    # - list
    # - string*
    # - tuple*
    a, b, c = 0, 0.0, True
    ls1 = [0, 1, 1, 2]
    ls2 = [] # type: [int]
    for i in range(len(ls1)):
        j = 0
        if i == 0:
            j = 10
        else:
            j = i + 1
                        
        ls2.append(j)
        
    print_ls(ls2)
    
hello()
