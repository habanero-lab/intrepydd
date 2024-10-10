#!/usr/bin/env python
import sys
import CppHeaderParser

try:
    cppHeader = CppHeaderParser.CppHeader("reduction.hpp")
except CppHeaderParser.CppParseError as e:
    print(e)
    sys.exit(1)

funcs = {}

def get_pydd_type(s):
    s = s.replace('py::array_t', 'Array')
    
    s = s.replace('<', '(')
    s = s.replace('>', ')')

    if s == 'py::array':
        s = 'Array()'
    elif s == 'float':
        s = 'float32'
    elif s == 'double':
        s = 'float64'
    elif s == 'int':
        s = 'int32'
    elif s == 'size_t':
        s = 'int64'
    
    return s

def find_func_in_header(func, header):
    cppHeader = CppHeaderParser.CppHeader(header)

    for f in cppHeader.functions:
        name = f['name']
        if name == func:
            ret = get_pydd_type(f['returns'])
            params = []
            
            for p in f['parameters']:
                params.append('%s: %s' % (p['name'], get_pydd_type(p['type'])))
                #print('%s %s(%s)' % (ret, name, ', '.join(params)))
            print('  - `(%s) -> %s`' % (', '.join(params), ret))

def find_func(func):
    headers = ['rt.hpp', 'reduction.hpp', 'elemwise.hpp', 'NpArray.hpp', 'matrixop.hpp', 'sparsemat.hpp']
    for h in headers:
        print('in ' + h)
        find_func_in_header(func, h)
        
find_func('sum')    

#print("CppHeaderParser view of %s"%cppHeader)

#sampleClass = cppHeader.classes["SampleClass"]~
