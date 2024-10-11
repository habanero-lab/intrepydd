from . import mytypes
from . import glb

# Record some info for cpp functions

# {func_name => [return_type, cpp_module]}
# '' means built-in functions

# Fields (default value):
# 1. return type (mytypes.void)
# 2. cpp module ('')
# 3. number of versions (1)
# 4. a bit vector: availability in -O0,1,2 (4)
#      __,__,__
#      O2 O1 O0
#      4: only available in -O2
 
float64_reduction = (mytypes.float64, 'reduction')
int64List_reduction = (mytypes.int64_list, 'reduction')
bool_reduction = (mytypes.bool, 'reduction')
# TODO
# means return type should be the element type pf the first argument
# arg0ElemType_reduction = (mytypes.float64, 'reduction')
# arg0Type_elemwise = (mytypes.float64_ndarray, 'elemwise')

def func_zeros_ret_type(arg_types):
    ndim = -1
    shape_ty = arg_types[0]
    if mytypes.is_list(shape_ty) \
       or mytypes.is_tuple(shape_ty):
        ndim = shape_ty.get_init_size()
    if mytypes.is_int(shape_ty):
        ndim = -1

    # -- if data type not specified
    if len(arg_types) == 1:
        return mytypes.NpArray(mytypes.float64, ndim)
    # -- if data type specified    
    elif len(arg_types) == 2:
        return mytypes.NpArray(arg_types[1], ndim)
    else:
        assert False

def func_zeros_2d_ret_type(arg_types):
    if len(arg_types) == 1:
        return mytypes.float64_2darray
    elif len(arg_types) == 2:
        return mytypes.NpArray(arg_types[1], 2)
    else:
        assert False

def func_sum_ret_type(arg_types):
    if len(arg_types) == 1:
        return arg_types[0].get_elt_type() # Is this right Jun? => Right
    elif len(arg_types) == 2 and isinstance(arg_types[0], mytypes.NpArray):
        return arg_types[0]
    else:
        assert False

def array_or_scalar(arg_types, elt_type):
    if isinstance(arg_types[0], mytypes.NpArray):
        return mytypes.NpArray(elt_type)
    elif len(arg_types) > 1 and isinstance(arg_types[1], mytypes.NpArray):
        return mytypes.NpArray(elt_type)
    else:
        return elt_type
    
funcinfo = {
    'print': (mytypes.void, '', 1, 5),
    'append': (mytypes.void, ''),
    'fill': (mytypes.void, ''),
    'len': (mytypes.int64, '', 1, 5),
    'boolean': [mytypes.bool, ''],
    'int32': [mytypes.int32, ''],
    'int64': [mytypes.int64, ''],
    'float32': [mytypes.float32, ''],
    'float64': [mytypes.float64, ''],
    'time': [mytypes.float64, ''],
    'range': [mytypes.int32_list,
              'NpArray', 1, 5],
    'zeros': (func_zeros_ret_type,
              'NpArray'),
    'zeros_2d': (func_zeros_2d_ret_type,
              'NpArray'),
    'empty': 'zeros', # same as zeros
    'arange': 'empty',
    'copy': 'empty',
    'numpy_random_rand': 'zeros',
    'empty_2d': 'zeros_2d',
    'empty_like': (lambda arg_types: arg_types[0],
              'NpArray'),
    'get_row': (lambda arg_types: arg_types[0],
              'NpArray'),
    'get_row_ptr': (lambda arg_types: arg_types[0],
              'NpArray'),
    'get_col': 'get_row',

    'set_row': (mytypes.void, 'NpArray'),
    'set_col': (mytypes.void, 'NpArray'),
    'sum_rows': (lambda arg_types: arg_types[0], 'NpArray'),
    'plus_eq': (mytypes.void, 'NpArray'),
    'minus_eq': (mytypes.void, 'NpArray'),
    'shape': [mytypes.int64,
              'NpArray'],
    'stride': 'shape',
    'arraysub': [mytypes.void,
                 'NpArray'],
    'dsyrk': [mytypes.float64_ndarray,
                   'lib'],
    'omp': [mytypes.void,
            'omp'],
    # Reduction (TODO: add implementation versions)
    'sum': (lambda arg_types: func_sum_ret_type(arg_types), 'reduction'),
    'prod': 'sum', # means same as above
    'min': 'sum',
    'max': 'sum',
    'argmin': int64List_reduction,
    'argmax': int64List_reduction,
    'any': bool_reduction,
    'all': 'any',
    'allclose': 'any',
    'where': [mytypes.int32_1darray, 'reduction'],
    'where1': [mytypes.int32_1darray, 'reduction'],
    # Element-wise unary (TODO: add implementation versions)
    'abs': (lambda arg_types: array_or_scalar(arg_types, mytypes.float64), 'elemwise'),
    'minus': (lambda arg_types: arg_types[0], 'elemwise'),
    'isnan': (lambda arg_types: array_or_scalar(arg_types, mytypes.bool), 'elemwise'),
    'isinf': 'isnan',
    'elemwise_not': 'isnan',
    'sqrt': (lambda arg_types: array_or_scalar(arg_types, mytypes.float64), 'elemwise'),
    'exp': 'sqrt',
    'cos': 'sqrt',
    'sin': 'sqrt',
    'tan': 'sqrt',
    'acos': 'sqrt',
    'asin': 'sqrt',
    'atan': 'sqrt',
    # Element-wise binary (TODO: add implementation versions)
    'add': [lambda arg_types: arg_types[0] if arg_types[0].equals(arg_types[1]) else mytypes.float64_ndarray,
            'elemwise'],
    'sub': 'add',
    'mul': 'add',
    '_sub': (mytypes.void, 'elemwise'),
    'maximum': (lambda arg_types: array_or_scalar(arg_types, mytypes.float64), 'elemwise'),
    'pow': (lambda arg_types: array_or_scalar(arg_types, mytypes.float64), 'elemwise'),
    'div': 'pow',
    'log': 'pow',
    'eq': [mytypes.bool_ndarray,
           'elemwise'],
    'neq': 'eq',
    'lt': 'eq',
    'gt': 'eq',
    'le': 'eq',
    'ge': 'eq',
    'logical_and' : 'eq',
    'logical_or' : 'eq',
    'logical_xor' : (lambda arg_types: array_or_scalar(arg_types, mytypes.bool), 'elemwise'),
    'logical_not' : 'isnan',
    'compatibility_check' : [mytypes.bool, 'elemwise'],
    # Matrix operations
    'transpose': [lambda arg_types: arg_types[0],
                  'matrixop'],
    'innerprod': [mytypes.float64,
                  'matrixop'],
    'innerprod1': [mytypes.float64,
                  'matrixop'],
    'matmult1': [mytypes.int32,
                  'matrixop'],
    'transpose1': [mytypes.int32,
                  'matrixop'],
    'matmult': [mytypes.float64_ndarray,
                'matrixop', 2],
    'syrk': 'matmult',
    'syr2k': 'matmult',
    'symm': 'matmult',
    'trmm': 'matmult',
    'lu': 'matmult',
    'ludcmp': 'matmult',
    'qr': 'matmult',
    'eig': 'matmult',
    'svd': 'matmult',
    'tril': 'matmult',
    'triu': 'matmult',
    'diag': 'matmult',
    'kron': 'matmult',
    'convolve': 'matmult',
    # Sparse matrix operations
    'empty_spm': [mytypes.float64_sparray,   # TODO: can be int and etc
                  'sparsemat'],
    'csr_to_spm': 'empty_spm',
    'arr_to_spm': 'empty_spm',
    'spm_to_csr': [mytypes.int32,
                   'sparsemat'],
    'spm_set_item': [mytypes.void,
                     'sparsemat'],
    'spm_set_item_unsafe': 'spm_set_item',
    'getval': [mytypes.float64,
               'sparsemat'],
    'getnnz': [mytypes.int32,
               'sparsemat'],
    'getcol': 'getnnz',
    'nnz': 'getnnz',
    'spm_add': [mytypes.float64_sparray,
                'sparsemat'],
    'spm_mul': 'spm_add',
    'spmm': 'spm_add',
    'spmv': [mytypes.float64_ndarray,
             'sparsemat'],
    'spmm_dense': [mytypes.float64_2darray,
             'sparsemat'],
    'sparse_diags': 'empty_spm',
    'spm_diags': 'empty_spm',
    'spm_mask': [mytypes.float64_sparray,
            'sparsemat'],
    'heapinit_empty': [mytypes.int32_int32_heap,
                 'heapq'],
    'heapinit': [mytypes.float32_heap,
                 'heapq'],
    'heappush': [mytypes.void,
                 'heapq'],
    'heappop': [mytypes.float32_list,
                'heapq'],
    'heappop1': [mytypes.void,
                'heapq'],
    'heappeek': [mytypes.float32,
                 'heapq'],
    'heapsize': [mytypes.int32,
                 'heapq'],

    'heap_get_key': [mytypes.int32,
                 'heapq'],
    'randint': [mytypes.int32, ''],
    'hex': [mytypes.string, ''],
    'hextoi': [mytypes.int32, ''],
    'stoi': [mytypes.int32, ''],
    'strtol': [mytypes.int32, ''],
}

# {cpp_library => [compiler_flags, linker_flags]}
# FIXME: dont think this is in use anymore
packageinfo = {
    'NpArray': [],
    'reduction': [],
    'elemwise': [],
    'matrixop': [],
    'sparsemat': [],
    'heapq': [],
    'omp': ['-fopenmp', '-fopenmp'],
    'lib': ['-I /usr/include/openblas',
            '-lblas'],
}


#used_packages = {'NpArray', 'reduction', 'elemwise', 'matrixop', 'sparsemat', 'heapq', 'omp'}
used_packages = ['shared/NpArray', 'py/reduction', 'py/elemwise',
                'py/matrixop', 'py/sparsemat', 'py/heapq']
#used_packages = {'NpArray'}


# global/built-in/library?
def is_global_func(func_name, module=''):
    # # TODO: to fix this
    return func_name in funcinfo
    # opt_bits = get_opt_level_bits(func_name)
    # is_available = 2**glb.args.opt_level & opt_bits
    # return func_name in funcinfo and is_available

def get_func_info(funcname, module='pydd'):
    '''
    A function is uniquely identiied by its module, name and signature.
    But due to the format of funcinfo table, we don't deal with argument
    signature here.
    '''    
    if module == 'pydd':
        if funcname in funcinfo:
            v = funcinfo[funcname]
            while isinstance(v, str):
                v = funcinfo[v]
            return v

            # if isinstance(v, str):                
            #     return get_func_info(v, module)
            # else:
            #     return v
        else:
            raise glb.UndefinedSymbolException(module, funcname)
    else:
        m_info = glb.get_imported_module_info(module)
        v = m_info.funcinfo[funcname]
        while isinstance(v, str):
            v = m_info.funcinfo[v]
        return v

# def get_ret_type(call_sig):
# #    print(vars(call_sig))
#     info = get_func_info(call_sig.funcname, call_sig.module)
#     if info and len(info) > 0:
#         ty = info[0]
#         if callable(ty):
#             return ty(call_sig.arg_types)
#         else:
#             return ty
#     else:
#         return mytypes.void

def get_type(name, module, arg_types=None):
    '''
    Get type of an external symbol via table lookup
    '''
    info = get_func_info(name, module)
    if info and len(info) > 0:
        ty = info[0]
        if callable(ty):
            return ty(arg_types)
        else:
            return ty
    else:
        return mytypes.void

def get_package(func_name):
    info = get_func_info(func_name)
    if info and len(info) > 1:
        return info[1]
    else:
        return ''

def get_version_count(func_name, module='pydd'):
    # # TODO: to fix this
    # return 1
    if module == 'std':
        return 1
    info = get_func_info(func_name, module)
    if info and len(info) > 2:
        return info[2]
    return 1

def get_opt_level_bits(func_name):
    info = get_func_info(func_name)
    if info and len(info) > 3:
        return info[3]
    return 4

def is_in_O0(func_name):
    info = get_func_info(func_name)
    if info and len(info) > 3:
        return info[3] & 1
    return False

def is_in_O1(func_name):
    info = get_func_info(func_name)
    if info and len(info) > 3:
        return info[3] & 2
    return False

def is_in_O2(func_name):
    info = get_func_info(func_name)
    if info and len(info) > 3:
        return info[3] & 4
    return True

def add_function_module(func_name):
    return
    global used_packages
    p = get_package(func_name)
    if p:
        used_packages.add(p)

# def register_lib_call(func_name):
#     global used_packages
#     used_packages.add(get_package(func_name))

def get_header_files():
    s = []

    # packages = ['shared/NpArray', 'py/reduction', 'py/elemwise',
    #             'py/matrixop', 'py/sparsemat', 'py/heapq', 'shared/omp']
    packages = used_packages

    #for p in used_packages:
    for p in packages:
        if p.startswith('shared/'):
            s.append(p+'.hpp')
        elif p.startswith('py/'):
            if glb.args.host == 'py':
                s.append(p+'.hpp')

    for p in glb.cpp_module.imports:
        if glb.is_imported_module_standard(p):
            s.append(p)
        else:
            s.append('%s/%s.hpp' % (p, p))
        
    return s

def get_compiler_flags():
    s = []
    # for p in used_packages:
    #     flags = packageinfo[p]
    #     if len(flags) > 0:
    #         s.append(flags[0])
    return s

def get_linker_flags():
    s = []

    if glb.args.blas:
        # Anaconda should already have these
        # s += ['-liomp5', '-lmkl_core', '-lmkl_intel_thread',
        #       '-lmkl_intel_lp64', '-pthread']
        from pathlib import Path
        s += f"-m64 -L{Path.home()}/anaconda3/lib -Wl,--no-as-needed -lmkl_intel_ilp64 -lmkl_gnu_thread -lmkl_core -lgomp -lpthread -lm -ldl".split()
    
    # for p in used_packages:
    #     flags = packageinfo[p]
    #     if len(flags) > 1:
    #         s.append(flags[1])
    return s
