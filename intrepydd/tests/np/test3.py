from typing import List

def vec_norm(vec: List[int], ord: int):
    for e in vec:
        print(e)
    
def main():
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
            continue
            
        ls2.append(j)
        
    vec_norm(ls2, 2)
    
