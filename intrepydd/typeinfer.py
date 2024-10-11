import sys
import ast
from pprint import pprint
import traceback

from . import mytypes
from .codegen import ModuleGen
from . import glb
from . import utils
from . import libfuncs
from .symboltable import symtab
from .glb import UnhandledNodeException
from .glb import dump
from .symboltable import CallSig

class TypeInferer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": []}
        self.cur_func = None
        
    def visit_Module(self, N):
        self.generic_visit(N)

    def get_cur_func(self):
        return self.cur_func
        
    def visit_FunctionDef(self, N: ast.FunctionDef):
        self.typemap = N.localtypes
        self.cur_func = N
        self.cur_func.has_pfor = False
       
        self.do_func_args(N)
        #self.gen_func_header(N)
        self.do_func_body(N)
        N.typemap = self.typemap
        #print(self.typemap)
        #self.generic_visit(node)

        glb.cpp_module.add_function(N)    
        
    def do_func_args(self, N: ast.FunctionDef):
        pendings = []
        for arg in N.args.args:
            if not arg.annotation:
                pendings.append(arg)
                continue
            ty = utils.get_annotation_type(arg.annotation)
            arg.type = ty
            
            for pending_arg in pendings:
                pending_arg.type = ty
                self.record_type(pending_arg)
                
            pendings.clear()
            self.record_type(arg)
        if len(pendings) > 0:
            print("Missing type annotations for argument ", end='')
            for arg in pendings:
                print('`%s`'%arg, end='')
            print()
            print('In function `%s`' % self.get_cur_func.name)    

    # def record_type(self, name, ty):
    #     self.typemap[name] = ty

    def record_type(self, N):
        # TODO: to check if an exsiting type is compatible with the new type
        if isinstance(N, ast.Name):
            self.typemap[N.id] = N.type
        elif isinstance(N, ast.arg):
            self.typemap[N.arg] = N.type
        else:
            glb.exit_on_unsupported_node(N)
            
            
    def do_func_body(self, N: ast.FunctionDef):
        for stmt in N.body:
            if self.is_str_stmt(stmt):
                continue
            self.do_node(stmt)

    def is_str_stmt(self, N):
        if isinstance(N, ast.Expr):
            if isinstance(N.value, ast.Str):
                return True
        return False    

    def do_node(self, N):
        if isinstance(N, ast.Assign):
            self.do_Assign(N)
        elif isinstance(N, ast.AnnAssign):
            self.do_AnnAssign(N)
        elif isinstance(N, ast.AugAssign):
            self.do_AugAssign(N)
        elif isinstance(N, ast.Num):
            self.do_Num(N)
        elif isinstance(N, ast.Name):
            self.do_name(N)
        elif isinstance(N, ast.For):
            self.do_For(N)
        elif isinstance(N, ast.While):
            self.do_While(N)
        elif isinstance(N, ast.If):
            self.do_If(N)
        elif isinstance(N, ast.Return):
            self.do_Return(N)
        elif isinstance(N, ast.NameConstant):
            self.do_name_constant(N)
        elif isinstance(N, ast.Tuple):
            self.do_Tuple(N)
        elif isinstance(N, ast.List):
            self.do_List(N)
        elif isinstance(N, ast.UnaryOp):
            self.do_UnaryOp(N)    
        elif isinstance(N, ast.BinOp):
            self.do_BinOp(N)
        elif isinstance(N, ast.BoolOp):
            self.do_BoolOp(N)
        elif isinstance(N, ast.Compare):
            self.do_Compare(N)    
        elif isinstance(N, ast.Expr):
            self.do_Expr(N)
        elif isinstance(N, ast.Str):
            self.do_Str(N)
        elif isinstance(N, ast.Subscript):
            self.do_Subscript(N)
            
        elif isinstance(N, ast.Call):
            self.do_Call(N)
    
        else:
            pass
                
    # def get_type(self, N):
    #     if not hasattr(N, 'type'):
    #         self.do_node(N)
    #     return a.type

    def get_symbol_type(self, name: ast.Name):
        assert type(name) == ast.Name, ast.dump(name)
        if name.id in self.typemap:
            return self.typemap[name.id]
        else:
            glb.exit_on_node(name, 'typed unresolved for symbol')
            raise Exception("typed unresolved for symbol `" + name + '`')

    def do_BoolOp(self, N):
        N.type = mytypes.bool

    def do_Compare(self, N):
        N.type = mytypes.bool
        
    def do_UnaryOp(self, N):
        self.do_node(N.operand)
        N.type = N.operand.type

    def do_BinOp(self, N):
        self.do_node(N.right)
        self.do_node(N.left)
        lty = N.left.type
        rty = N.right.type
        # print(ast.dump(N))
        # print(lty)
        # print(rty)
        if mytypes.is_all_float(lty, rty) or mytypes.is_all_int(lty, rty):
            if lty.get_width() >= rty.get_width():
                N.type = lty
            else:
                N.type = rty
            return
        
        
        if not N.left.type.can_broadcast_with(N.right.type):
            msg = "type unmatch in binary operator %s\n" % N.op
            msg += "left (%s): %s\n" % (N.left.type, ast.dump(N.left))
            msg += "right (%s): %s\n" % (N.right.type, ast.dump(N.right))
            if glb.args.verbose:
                print("nn")
                dump(N.left)
                dump(N.right)
            glb.exit_on_node(N, msg)

        # The list type should dominate if it exists in the BinOp
        # a = [1, 2, 3] * 4  <- a should have type array<int>
        # Otherwise, just take either of the two types, since they are the same
        N.type = N.left.type if hasattr(N.left.type, 'etype') else N.right.type

    def do_Str(self, N):
        N.type = mytypes.string

    def verify_array_dim(self, N: ast.Subscript):
        if N.value.id in self.typemap:
            ty = self.get_symbol_type(N.value)
            if (isinstance(ty, mytypes.NpArray) and ty.ndim != -1):
                print(ast.dump(N))
                if isinstance(N.slice, ast.Tuple):
                #if isinstance(N.slice, ast.Tuple):
                    ndim_found = len(N.slice.elts)
                else:
                    ndim_found = 1
                if ty.ndim != ndim_found:
                    msg = 'annotated # array dims = %d while found = %d' % (ty.ndim, ndim_found)
                    #glb.exit_on_node(N, msg)
                    
                    raise Exception(msg)

    def do_Subscript(self, N):
        if type(N.value) == ast.Attribute and N.value.attr == 'shape':
            glb.exit_on_node(N, "Please use `shape()` instead of `shape[]`")
            assert False, "haha"

        basetype = self.get_symbol_type(N.value)
        N.type = basetype.get_elt_type()
        if isinstance(basetype, mytypes.DictType):
            N.type = basetype.value

        libfuncs.add_function_module('arraysub')  # Arrays can be accessed without range/shape
        self.verify_array_dim(N)

    def do_Expr(self, N: ast.Expr):
        if isinstance(N.value, ast.Call):
            self.do_Call(N.value)
        else:
            glb.exit_on_unsupported_node(N)

    def do_Call(self, N: ast.Call):
        # eg: Call(func=Name(id='print', ctx=Load()), args=[Name(id='i', ctx=Load())], keywords=[])
        # Call(func=Attribute(value=Name(id='ls2', ctx=Load()), attr='append', ctx=Load()), args=[Name(id='j', ctx=Load())], keywords=[])
        # todo
        arg_types = []
        for arg in N.args:
            self.do_node(arg)
            if not hasattr(arg, "type"):
                glb.exit_on_node(N, "Node type unknown")
            arg_types.append(arg.type)
        for key in N.keywords:
            self.do_node(key)

        callSig = None
        module = ''
        funcname = ''
        try:
            if isinstance(N.func, ast.Name):
                # Either should be a user-defined function or a global function
                funcname = N.func.id

                if funcname.startswith('_'):
                    # functions like _add/_sub have no meaningful return value for now
                    return
                
                if not glb.is_user_defined_func(funcname):
                    module = 'pydd'
                    libfuncs.add_function_module(funcname)
            elif isinstance(N.func, ast.Attribute):
                # Should be a module.function
                f = N.func        
                if not glb.cpp_module.is_module(f.value.id):
                    glb.exit_on_unsupported_node(N)
                else:
                    module = f.value.id
                    funcname = f.attr
                    N.is_module_call = True
                    
            #callSig = CallSig(module, funcname, arg_types)

            N.type = symtab.get_type(funcname, module, arg_types)
            # if funcname == 'empty':
            #     print(arg_types)
            #     print("empty call type:", N.type.get_dimension())
            #     sys.exit(1)

        except glb.UndefinedSymbolException as e:
            glb.exit_on_node(N, str(e))

            
    def eval_type_comment(self, s: str):
        print("got type:", s)
        if s == '[int]':
            return mytypes.int64_list
        if s == 'int' or s == 'int32':
            return mytypes.int32
        elif s == 'int64':
            return mytypes.int64
        elif s == 'double' or s == 'float64':
            return mytypes.float64
        elif s == 'float' or s == 'float32':
            return mytypes.float32
        else:
            return Exception('Unrecognized type comment: ' + s)

    def do_AnnAssign(self, N: ast.AnnAssign):
        ty = utils.get_annotation_type(N.annotation)
        N.target.type = N.value.type = ty
        self.record_type(N.target)
        N.targets = [N.target]
        self.do_Assign_common(N)
           
    def do_AugAssign(self, N: ast.AugAssign):
        self.do_node(N.value)
        N.targets = [N.target]
        self.do_Assign_common(N)

    def do_Assign(self, N: ast.Assign):
        
        if N.type_comment:
            N.value.type = self.eval_type_comment(N.type_comment)
        else:
            #print("do_Assign", ast.dump(N))
            self.do_node(N.value)
            ty = N.value.type
        self.do_Assign_common(N) 
        

    def do_Assign_common(self, N):
        for target in N.targets:
            # Assign to one var
            if isinstance(target, ast.Name):
                if hasattr(target, 'type'):
                    continue
                target.type = N.value.type
                self.record_type(target)
            # Assign to multiple vars    
            elif isinstance(target, ast.Tuple):
                var_tp = target.elts
                value_tp = N.value.elts
                assert len(var_tp) == len(value_tp)
                for i in range(len(var_tp)):
                    var_tp[i].type = value_tp[i].type
                    self.record_type(var_tp[i])
            # TODO: var = BinOp
            
            if isinstance(target, ast.Subscript):
                self.verify_array_dim(target)
            


    def do_name(self, N):
        N.type = self.get_symbol_type(N)
        
    def do_tuple_assign(self, N: ast.Assign):
        value_tp = N.value.elts
        var_tp = N.targets[0].elts
        if len(value_tp) != len(var_tp):
            raise SyntaxError("# of elements in the left and right don't match in assignment") 

        for i in range(len(value_tp)):
            left = var_tp[i]
            right = value_tp[i]
            left.type = self.do_node(right)
            
        #raise UnsupportedException("Unsupported assignment syntax!")
            
    def do_Num(self, N: ast.Num):
#        dump(N)
        if isinstance(N.n, int):
            N.type = mytypes.int32
        elif isinstance(N.n, float):
            N.type = mytypes.float64
        else:
            raise UnhandledNodeException(N)
 #       print(N.type)
        
    def do_name_constant(self, N: ast.Num):
        if isinstance(N.value, bool):
            N.type = mytypes.bool
        else:
            raise UnhandledNodeException(N)

        
    def do_Tuple(self, N: ast.Tuple):
        types = []
        for ele in N.elts:            
            self.do_node(ele)
            types.append(ele.type)
        N.type = mytypes.TupleType(types)
        N.type.set_init_size(len(N.elts))

        
    def do_List(self, N: ast.List):
        types = []
        for ele in N.elts:            
            self.do_node(ele)
            types.append(ele.type)
            break        
        N.type = mytypes.ListType(types[0])
        N.type.set_init_size(len(N.elts))

        
    def annotate(self, node, type):
        node.type = type

        
    def do_For(self, N: ast.For):
        # Fields:
        # for 'target' in 'iter':
        #   'body'
        if N.type_comment == 'pfor':
            N.is_pfor = True
            self.cur_func.has_pfor = True
        else:
            N.is_pfor = False
            
        self.do_node(N.iter)
        container_ty = N.iter.type
        #N.target.type = N.iter.type.etype

        N.target.type = N.iter.type.get_elt_type()
        self.record_type(N.target)
        for expr in N.body:
            self.do_node(expr)

    def do_While(self, N: ast.While):
        for expr in N.body:
            self.do_node(expr)
            
    def do_If(self, N: ast.If):
        '''        
        if 'test':
          'body'
        'orelse':

        '''
        for expr in N.body:
            self.do_node(expr)
        
        if N.orelse:
            for expr in N.orelse:
                self.do_node(expr)
        
    def do_Return(self, N: ast.Return):
        # Return node doesn't need a type
        # TODO: could do a type check for return
        
        self.do_node(N.value)
        if self.cur_func.ret_type == mytypes.void:
            #assert False, "function return type unannotated!"
            self.cur_func.ret_type = N.value.type
        else:
            if not self.cur_func.ret_type.equals(N.value.type):
                m = 'Unmatched return types. \nPreviously: ' + str(self.cur_func.ret_type) + '\n'
                m += 'Now: ' + str(N.value.type)
                print(self.typemap)
                glb.exit_on_node(N, m)
        
        
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)

