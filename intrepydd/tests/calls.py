
def getfloat() -> float64:
    return 3.14

def main():
    j = inc(100)
    print(j)
    k = getfloat()
    print(k)

def inc(i: int) -> int:
    return i + 1

def getlen() -> int64:
    return len([1, 2, 3])

main()

