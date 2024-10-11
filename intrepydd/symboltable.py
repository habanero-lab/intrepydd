from . import libfuncs
from .utils import deprecated

class CallSig(object):
    def __init__(self, module, funcname, arg_types):
        self.module = module
        self.funcname = funcname
        self.arg_types = arg_types

    def __str__(self):
        s = 'call signature: %s::%s' % (self.module, self.funcname)
        return s


class FuncSymbolTable(object):
    '''
    Represents symbol table for a function
    '''
    def __init__(self):
        self.defs = {}
        self.uses = {}
        self.locals = []
        self.unboxed = {}
        

    def register_local(self, var):
        self.locals.append(var)


    def add_def(self, name, stmt):
        if name not in self.defs:
            self.defs[name] = []
        self.defs[name].append(stmt)    
        

    def add_use(self, name, stmt):
        if name not in self.uses:
            self.uses[name] = []
        self.uses[name].append(stmt)    
        

    def register_unboxed_array(self, var, info):
        self.unboxed[var] = info


    def is_unboxed(self, var):
        return var in self.unboxed

        
    def get_unboxed_ptr(self, var):
        return self.unboxed[var]
        

class SymbolTable(object):
    '''
    Each module has a symbol table.
    '''
    def __init__(self):
        self.user_globals = {}
        self.func_table = {}

    # def init_typemap(self):
    #     self.typemap = {} # for user defined functions

    # def register_type(self, name, ty):
    #     self.typemap[name] = ty

    def register_user_func(self, F):
        name = F.name
        self.user_globals[name] = F.ret_type
        self.func_table[name] = F.localtypes
        

    def get_local_type(self, funcname, name):
        assert type(funcname) == str, type(funcname)
        assert type(name) == str, type(name)
        table = self.func_table[funcname]
        msg = "local %s not found in %s" % (name, funcname)
        assert name in table, msg
        return table[name]
        

    @deprecated("Please use the next `get_type` below")
    def get_type(self, callSig: CallSig):
        name = callSig.funcname
        module = callSig.module

        if module == '': # this module            
            if name in self.user_globals:
                return self.user_globals[name]
            else:
                raise glb.UndefinedSymbolException(module, name)
        else: # either a global or a library function        
            return libfuncs.get_ret_type(callSig)


    def get_type(self, name, module, type_args=None):
        if module == '': # this module            
            if name in self.user_globals:
                return self.user_globals[name]
            else:
                raise glb.UndefinedSymbolException(module, name)
        else: # either a global or a library function        
            return libfuncs.get_type(name, module, type_args)


    def is_user_defined_symbol(self, name):
        return name in self.user_globals


    def get_func_symbol_table(self, func):
        return self.func_table[func]

    
    def register_unboxed_arrays(self, func, name):
        pass

    
    def __str__(self):
        s = 'User defined functions are:\n'
        for name in self.typemap:
            s += name + ' => ' + str(self.typemap[name]) + '\n'
        return s

    

symtab = SymbolTable()
