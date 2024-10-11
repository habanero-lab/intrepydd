import warnings
import logging
import ast
from . import mytypes
from . import glb

#from glb import dump

def deprecated(message):
  def deprecated_decorator(func):
      def deprecated_func(*args, **kwargs):
          warnings.warn("{} is a deprecated function. {}".format(func.__name__, message),
                        category=DeprecationWarning,
                        stacklevel=2)
          warnings.simplefilter('default', DeprecationWarning)
          return func(*args, **kwargs)
      return deprecated_func
  return deprecated_decorator


def get_logger(name):
    return logging.getLogger(name)
  

def setup_logger(logger_name, log_file=None, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(message)s')
    #formatter = logging.Formatter('%(message)s')
    if log_file:
        fileHandler = logging.FileHandler(log_file, mode='w')
        fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    if log_file:
        l.addHandler(fileHandler)
    l.addHandler(streamHandler)
    return l

    
def get_annotation_type(N):
    if isinstance(N, ast.Name):
        id = N.id
        if id == 'int' or id == 'int32' or id == 'I':
            return mytypes.int32
        elif id == 'int64' or id == 'long' or id == 'J':
            return mytypes.int64
        elif id == 'double' or id == 'float64' or id == 'D':
            return mytypes.float64
        elif id == 'float' or id == 'float32' or id == 'F':
            return mytypes.float32
        elif id == 'bool' or id == 'Z':
            return mytypes.bool
    
    elif isinstance(N, ast.Call):
        # Numpy array type
        if N.func.id == 'Array':
            args = N.args
            etype = mytypes.float64                
            ndim = -1
            layout = 'K'
            if len(args) > 0:
                etype = get_annotation_type(args[0])
            if len(args) > 1:
                ndim = args[1].n                
            if len(args) > 2:
                layout = args[2].id
            return mytypes.NpArray(etype, ndim, layout)
        elif N.func.id == 'SparseMat':
            args = N.args
            etype = mytypes.float64
            if len(args) > 0:
                etype = get_annotation_type(args[0])
            return mytypes.SparseMat(etype)
        elif N.func.id == 'Heap':
            args = N.args
            etype = mytypes.float64
            if len(args) > 0:
                etype = get_annotation_type(args[0])
            return mytypes.Heap(etype)
        elif N.func.id == 'Dict':
            args = N.args
            assert len(args) == 2, "Type annotation `Dict` must have two arguments"
            return mytypes.DictType(get_annotation_type(N.args[0]), get_annotation_type(N.args[1]))
        elif N.func.id == 'List':
            return mytypes.ListType(get_annotation_type(N.args[0]))
            
    elif isinstance(N, ast.Subscript):
        if isinstance(N.value, ast.Name):
            if N.value.id == 'List':
                if N.slice.id == 'float':
                    return mytypes.float64_list
                if N.slice.id == 'int':
                    return mytypes.int64_list   
                
    else:
        glb.exit_on_unsupported_type_ann(N)

def get_operator_expansion_func(op):
    if isinstance(op, ast.Add):
        return 'add'
    elif isinstance(op, ast.Div):
        return 'div'
    elif isinstance(op, ast.Eq):
        return 'eq'
    elif isinstance(op, ast.Gt):
        return 'gt'
    elif isinstance(op, ast.GtE):
        return 'ge'
    elif isinstance(op, ast.LtE):
        return 'le'
    elif isinstance(op, ast.Lt):
        return 'lt'
    elif isinstance(op, ast.Mult):
        return 'mul'
    elif isinstance(op, ast.NotEq):
        return 'neq'
    elif isinstance(op, ast.Sub):
        return 'sub'
    else:
        return 'n/a'

