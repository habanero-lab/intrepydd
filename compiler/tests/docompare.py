def foo(x: int32, y: int32) -> int32:
    return int32(x < y)   # Desired output: 0 or 1

foo(0,1)
foo(2,1)
