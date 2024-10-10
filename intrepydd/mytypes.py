
class MyType(object):
    def get_declare_str(self):
        if pass_by_ref(self):
            return self.get_cpp_name() + '*'
        else:
            return self.get_cpp_name()
        
    def equals(self, ty):
        if hasattr(self, 'etype') and hasattr(ty, 'etype'):
            return self.etype == ty.etype
        return self == ty

    # return true if types can be broadcasted
    # ex: (array<int>, int) -> true
    # ex: (array<double>, int) -> false
    # ex: (tuple<int>, int) -> false
    def can_broadcast_with(self, ty):
        if not (is_basic_type(self) or is_array(self)):
            return False
        if not (is_basic_type(ty) or is_array(ty)):
            return False
        e_type_1 = self if is_basic_type(self) else self.etype
        e_type_2 = ty if is_basic_type(ty) else ty.etype
        return e_type_1 == e_type_2

    
class IterableType(MyType):
    def get_elt_type(self):
        '''
        Returns the element type in a `for...in` clause
        '''
        return self.etype
        #raise NotImplementedError()

        
class ListType(IterableType):
    def __init__(self, etype):
        self.etype = etype
        self.initsize = 0
        
    def set_init_size(self, n):
        self.initsize = n

    def get_init_size(self):
        return self.initsize

    def get_cpp_name(self):
        return 'std::vector<%s>' % str(self.etype)
    
    def __str__(self):
        return 'std::vector<%s>' % str(self.etype)


class TupleType(MyType):
    def __init__(self, types):
        self.etypes = types

    def set_init_size(self, n):
        self.initsize = n

    def get_init_size(self):
        return self.initsize


class DictType(IterableType):
    def __init__(self, key_ty, value_ty):
        self.key = key_ty
        self.value = value_ty

    def get_elt_type(self):
        return self.key

    def equals(self, ty):
        if not isinstance(ty, DictType):
            return False
        else:
            return ty.key == self.key and ty.value == self.value

    def get_cpp_name(self):
        return 'std::unordered_map<%s, %s>' % (self.key, self.value)

    def __str__(self):
        #return 'std::map<%s, %s>' % (self.key, self.value)
        return 'std::unordered_map<%s, %s>' % (self.key, self.value)
        
class BoolType(MyType):
    def __init__(self):
        self.by_ref = False

    def get_cpp_name(self):
        return 'bool'

    def __str__(self):
        return 'bool'
        
class IntType(MyType):
    def __init__(self, w=64):
        self.by_ref = False
        self.width = w

    def get_width(self):
        return self.width

    def get_cpp_name(self):
        if self.width == 32:
            return 'int'
        elif self.width == 64:
            return 'int64_t'
        else:
            raise Exception()

    def __str__(self):
        if self.width == 32:
            return 'int'
        elif self.width == 64:
            return 'int64_t'
        else:
            raise Exception()

class FloatType(MyType):
    def __init__(self, w=64):
        self.by_ref = False
        self.width = w

    def get_width(self):
        return self.width

    def get_cpp_name(self):
        if self.width == 64:
            return 'double'
        elif self.width == 32:
            return 'float'
        else:
            assert False

    def __str__(self):
        if self.width == 64:
            return 'double'
        elif self.width == 32:
            return 'float'
        else:
            assert False

            
class StrType(MyType):
    def __str__(self):
        return "std::string"

    def get_cpp_name(self):
        return "std::string"
        
    def get_elt_type(self):
        return IntType()


class VoidType(MyType):
    def __init__(self):
        self.by_ref = False
        pass

    def get_cpp_name(self):
        return 'void'

    def __str__(self):
        return 'void'

    
class NpArray(IterableType):
    def __init__(self, dtype, ndim=-1, layout='K'):
        self.etype = dtype
        self.ndim = ndim
        self.layout = layout

    def get_pi_type(self):
        return PINpArray(self.etype, self.ndim, self.layout)

    def get_dimension(self):
        return self.ndim

    def equals(self, a):        
        #return self.etype == a.etype and self.layout == a.layout
        return hasattr(a, 'etype') and self.etype == a.etype

    def __str__(self):
        return "py::array_t<%s>" % self.etype
        #return "pydd::NpArray<%s>*" % self.etype
        
    def get_cpp_name(self):
        return "py::array_t<%s>" % self.etype.get_cpp_name()

    def get_new_str(self):
        return "py::array_t<%s>" % self.etype
        #return "new pydd::NpArray<%s>" % self.etype    

class PINpArray(MyType):
    def __init__(self, dtype, ndim, layout='K'):
        self.etype = dtype
        self.ndim = ndim
        self.layout = layout

    def get_cpp_name(self):
        return "py::array_t<%s>" % self.etype.get_cpp_name()

    def __str__(self):
        return 'py::array_t<%s>' % self.etype

class SparseMat(IterableType):
    def __init__(self, dtype, ndim=2, layout='K'):
        self.etype = dtype
        self.ndim = ndim
        self.layout = layout

    def get_cpp_name(self):
        return 'pydd::Sparse_matrix<%s>' % self.etype.get_cpp_name()    

    def __str__(self):
        return 'pydd::Sparse_matrix<%s>' % self.etype

class Heap(IterableType):
    def __init__(self, key_ty, val_ty):
        self.key = key_ty
        self.val = val_ty
        # self.etype = dtype
    
    def get_elt_type(self):
        return self.key

    def get_cpp_name(self):
        return 'pydd::Heap<%s, %s>' % \
               (self.key.get_cpp_name(), self.val.get_cpp_name())    

    def __str__(self):
        return 'pydd::Heap<%s, %s>' % (self.key, self.val)
    
def pass_by_ref(ty):
    if isinstance(ty, IntType) or \
      isinstance(ty, FloatType) or \
      isinstance(ty, NpArray) or \
      isinstance(ty, SparseMat) or \
      isinstance(ty, Heap) or \
      isinstance(ty, VoidType) or \
      isinstance(ty, StrType) or \
      isinstance(ty, BoolType):
        return False
    else:
        return True

def is_float(ty):
    return isinstance(ty, FloatType)
    
def is_all_float(t1, t2):
    return is_float(t1) and is_float(t2)
    
def is_int(ty):
    return isinstance(ty, IntType)
    
def is_all_int(t1, t2):
    return is_int(t1) and is_int(t2)

def is_array(ty):
    #return isinstance(ty, ListType) or isinstance(ty, NpArray)
    return isinstance(ty, NpArray)

def is_list(ty):
    return isinstance(ty, ListType)

def is_tuple(ty):
    return isinstance(ty, TupleType)


def is_basic_type(ty):
    return not hasattr(ty, 'etype')

    
bool = BoolType()  
int32 = IntType(32)
int64 = IntType(64)
float32 = FloatType(32)
double = float64 = FloatType(64)
float32_list = ListType(float32)
float64_list = ListType(float64)
int32_list = ListType(int32)
int64_list = ListType(int64)
void = VoidType()
string = StrType()
float64_ndarray = NpArray(float64)
float64_1darray = NpArray(float64, 1)
float64_2darray = NpArray(float64, 2)
float32_ndarray = NpArray(float32)
int32_ndarray = NpArray(int32)
int32_1darray = NpArray(int32, 1)
int64_ndarray = NpArray(int64)
bool_ndarray = NpArray(bool)
float64_sparray = SparseMat(float64)
float32_heap = Heap(float32, int32)
int32_int32_heap = Heap(int32, int32)

# Special types for return vars
arg_dependent_type = None
