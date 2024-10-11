import sys
import ast
from pprint import pprint
from . import mytypes
from . import glb
from . import libfuncs
from . import astutils
from .glb import UnhandledNodeException
from .symboltable import symtab
from .licmarray import get_num_array_dim
from .utils import deprecated
from . import utils


def dump(N):
    print(ast.dump(N))

class ModuleGen(ast.NodeVisitor):
    # WARN: name can be a full path
    def __init__(self):
        self.name = glb.get_module_name()
        self.funcs = []
        self.cur_func = None
        self.cur_node = None        
        self.inv_subs = set()
        self.has_main = False
        self.type_logger = utils.get_logger('type')
        

    def writeln(self, s=''):
        glb.cpp_module.writeln(s)

    def write(self, s):
        glb.cpp_module.write(s)

    def visit_Module(self, node):
        module = glb.get_module_name()
        # Gen cppimport headers (compiler flags etc)
        if glb.args.host == 'py':
            glb.cpp_module.do_pymodule_header()
        # Gen default includes
        glb.cpp_module.do_default_include()
        
        # Gen functions declarations
        glb.cpp_module.writeln("namespace %s {" % module)
        glb.cpp_module.writeln("/* Function declarations */")
        for f in glb.cpp_module.funcs:
            self.gen_func_header(f)
        glb.cpp_module.writeln("")
        # Gen function definitions
            
        self.generic_visit(node)
        glb.cpp_module.writeln("}") # namespace ends    
        # Gen cppimport footer
        if glb.args.host == 'py':    
            glb.cpp_module.do_py_footer()

        if self.has_main and glb.args.host == 'cpp':
            self.gen_real_main()
    
        
    def visit_Import(self, node):
        self.generic_visit(node)


    def dump_local_type(self, N):
        if not glb.args.dump_type:
            return
        print('=== local types for function "%s" ===' % N.name)
        typemap = symtab.get_func_symbol_table(N.name)
        if glb.args.dump_type == '*':
            for var in typemap:
                print("    %s: %s" % (var, typemap[var]))
        

    def visit_FunctionDef(self, N):
        self.dump_local_type(N)
        self.cur_func = N
        if N.name == 'main':
            self.has_main = True
        self.register(N)
        
        self.do_func_header(N)
        self.do_var_decls(N)
        # self.do_func_args(N)
        self.do_func_body(N)
        self.writeln('}\n')
        #self.generic_visit(node)

        
    def register(self, N):
        self.funcs.append(N)


    def gen_debug_info(self, N):
        if not glb.args.g:
            return
        s = 'pydd::append_to_call_stack("%s");' % N.name
        self.writeln(s)
        

    def gen_real_main(self):
        s = '''
        int main(int argc, void** argv) { %s::main(); }
        ''' % glb.get_module_name()
        self.writeln(s)

    def gen_func_header(self, N: ast.FunctionDef):
        s = '%s %s(' % (N.ret_type.get_declare_str(), N.name)
        
        args = []
        for arg in N.args.args:            
            args.append(
                arg.type.get_declare_str() + " " + arg.arg
                )
        s += ', '.join(args) + ');\n'
        glb.cpp_module.write(s)
            

    def do_var_decls(self, N: ast.FunctionDef):
        self.writeln('/* Declarations */')
        args = []
        
        for arg in N.args.args:
            args.append(arg.arg)

        s = ''     
        for v in N.typemap:
            if v in args:
                continue
            ty = N.typemap[v]
            s += ty.get_declare_str() + ' ' + v + ';\n'

        arraydims = self.get_array_dim_info(N)
        if 'licm_array' in glb.options and glb.options['licm_array']:
            if hasattr(N, 'inv_array_dim'):
                for array_id in N.inv_array_dim:
                    #print('array', array_id, 'dim', N.inv_array_dim[array_id])
                    if array_id in args:
                        continue
                    self.gen_data_ptr_decls(array_id, N.inv_array_dim[array_id])
            
            for v in args:
                ty = self.get_local_type(v)
            # for v in N.typemap:
            #     ty = self.get_local_type(v)
                if isinstance(ty, mytypes.NpArray):
                    etype = ty.etype.get_cpp_name()
                    s += '%s* %s_data_ptr_pydd = %s.mutable_data();\n' \
                        % (etype, v, v)
                    if ty.ndim == 2:    
                        s += 'int %s_shape1_pydd = %s.shape(1);\n' \
                            % (v, v)
                    
        self.writeln(s+'\n')

    
    def get_array_dim_info(self, F):
        if hasattr(F, 'inv_array_dim'):
            return F.inv_array_dim
        else:
            return {}

        
    @deprecated('')
    def gen_data_ptr(self, name):
        assert type(name) == str, type(name)
        ty = self.get_local_type(name)
        if not isinstance(ty, mytypes.NpArray):
            return

        s = ''
        data_ptr = name + '_data_ptr_pydd'
        arr_shape1 = name + '_shape1_pydd'

        s += '%s* %s = %s.mutable_data();\n' % (ty.get_elt_type(), data_ptr, name)
        s += '%s %s = %s.shape(1);\n' % (mytypes.int64, arr_shape1, name)
        self.writeln(s)


    def gen_data_ptr_decls(self, name, ndim):
        assert type(name) == str, type(name)
        ty = self.get_local_type(name)
        if not isinstance(ty, mytypes.NpArray):
            return

        data_ptr = name + '_data_ptr_pydd'
        s = '%s* %s;\n' % (ty.get_elt_type(), data_ptr)
        for d in range(1, ndim):
            arr_shape_d = '%s_shape%i_pydd' % (name, d)
            s += '%s %s;\n' % (mytypes.int64, arr_shape_d)
        self.write(s)

        
    def gen_data_ptr_assign(self, name, ndim):
        assert type(name) == str, type(name)

        data_ptr = name + '_data_ptr_pydd'
        s = '%s = %s.mutable_data();\n' % (data_ptr, name)
        for d in range(1, ndim):
            arr_shape_d = '%s_shape%i_pydd' % (name, d)
            s += '%s = %s.shape(%i);\n' % (arr_shape_d, name, d)
        return s

    
    def do_func_header(self, N: ast.FunctionDef):
        s = '%s %s(' % (N.ret_type.get_declare_str(), N.name)
        
        args = []
        for arg in N.args.args:            
            args.append(
                arg.type.get_declare_str() + " " + arg.arg
                )
        s += ', '.join(args) + ')'
        self.write(s)
        self.writeln(' {')
        
            
    def do_func_body(self, N: ast.FunctionDef):
        for stmt in N.body:
            if self.should_ignore(stmt):
                continue

            self.cur_node = stmt
            
            s = self.eval_node(stmt)
            #print('stmt: ', s)
            self.writeln(s + ';')

    def is_str_stmt(self, N):
        if isinstance(N, ast.Expr):
            if isinstance(N.value, ast.Str):
                return True
        return False    

    def should_ignore(self, stmt):
        if self.is_str_stmt(stmt):
            return True
        return False

    def eval(self, N):
        return self.eval_node(N)

    def eval_node(self, N):
        s = ''
        if isinstance(N, str): # a little hacky
            s = N 
        elif isinstance(N, ast.Assign):
            s = self.eval_Assign(N)
        elif isinstance(N, ast.AnnAssign):
            s = self.eval_AnnAssign(N)
        elif isinstance(N, ast.Name):
            s = self.eval_name(N)
        elif isinstance(N, ast.Num):
            s = self.eval_Num(N)
        elif isinstance(N, ast.For):
            s = self.eval_For(N)
        elif isinstance(N, ast.While):
            s = self.eval_While(N)
        elif isinstance(N, ast.If):
            s = self.eval_if(N)
        elif isinstance(N, ast.Return):
            s = self.eval_Return(N)
        elif isinstance(N, ast.NameConstant):
            s = self.eval_name_constant(N)
        elif isinstance(N, ast.List):
            s = self.eval_List(N)
        elif isinstance(N, ast.Tuple):
            s = self.eval_Tuple(N)
        elif isinstance(N, ast.Expr):
            s = self.eval_Expr(N)
        elif isinstance(N, ast.BoolOp):
            s = self.eval_BoolOp(N)
        elif isinstance(N, ast.Str):
            s = self.eval_Str(N)
        elif isinstance(N, ast.Subscript):
            s = self.eval_Subscript(N)
        elif isinstance(N, ast.Dict):
            s = self.eval_Dict(N)
        elif isinstance(N, ast.Call):
            s = self.eval_Call(N)
        elif isinstance(N, ast.Compare):
            s = self.eval_Compare(N)
        elif isinstance(N, ast.UnaryOp):
            s = self.eval_UnaryOp(N)    
        elif isinstance(N, ast.BinOp):
            s = self.eval_BinOp(N)    
        elif isinstance(N, ast.Continue):
            s = self.eval_Continue(N)
        elif isinstance(N, ast.Break):
            s = self.eval_Break(N)
        elif isinstance(N, ast.Pass):
            s = self.eval_Pass(N)
        elif isinstance(N, ast.AugAssign):
            s = self.eval_AugAssign(N)
        elif isinstance(N, ast.Attribute):
            s = self.eval_Attribute(N)
        elif isinstance(N, ast.Assert):
            s = self.eval_Assert(N)
        else:
            glb.exit_on_unsupported_node(N)
        return s
                
    def get_type(self, N):
        if not hasattr(N, 'type'):
            self.do_node(N)
        return a.type
            
    def eval_name(self, N):
        return N.id


    def eval_AugAssign(self, N:ast.AugAssign):
        N.targets = [N.target]
        N.value = self.eval_BinOp_raw(N.op, N.target, N.value)
        return self.eval_Assign(N)

    def eval_AnnAssign(self, N):
        N.targets = [N.target]
        return self.eval_Assign(N)

    def is_array_slice(self, N):
        if isinstance(N, ast.Call) and N.func.id == "get_row":
            return True
        return False
    
    def eval_Assign(self, N: ast.Assign):
        assigns = []        
        for target in N.targets:
            # Assign to one var
            if isinstance(target, ast.Name):
                lhs = target.id
                rhs = N.value
                # if glb.args.slice_opt and self.is_array_slice(rhs):
                #     # R.H.S is array slice, special codegen may be needed
                #     s = self.gen_unboxed_slice(target, N.value)                    
                # else:
                
                s = '%s = %s' % (target.id, self.eval(N.value))    
                assigns.append(s)
                
            # Assign to multiple vars    
            elif isinstance(target, ast.Tuple):
                var_tp = target.elts
                value_tp = N.value.elts
                assert len(var_tp) == len(value_tp)
                for i in range(len(var_tp)):
                    s = '%s = %s' % (var_tp[i].id, self.eval(value_tp[i]))
                    assigns.append(s)
            # Assign to subscript
            # Need some interpretation
            elif isinstance(target, ast.Subscript):
                #s = self.eval_get_or_set_item(self.eval(target.value), self.eval_Subscript_slice(target.slice), self.eval(N.value))
                s = self.eval_get_or_set_item(self.eval(target.value), target, self.eval(N.value))

                # s = "pydd::setitem(%s, %s, %s)" % \
                #   (self.eval(target.value), self.eval(N.value),
                #    self.eval_Subscript_slice(target.slice))
                assigns.append(s)
                
            else:
                glb.exit_on_unsupported_node(N)
            
        #print(assigns)        
        return '; '.join(assigns)


    def get_call_arg_str(self, call, i):
        assert isinstance(call, ast.Call)
        args = call.args
        arg = args[i]
        if isinstance(arg, ast.Name):
            return arg.id
        
    
    def get_data_type(self, slice_call):
        assert isinstance(slice_call, ast.Call)
        funcid = slice_call.func.id
        args = slice_call.args
        if funcid == 'get_row':
            ty = self.get_local_type(args[0].id)
            return ty.etype.get_cpp_name()
        else:
            assert False, "get_data_type only supports get_row call"
        

    def gen_unboxed_slice(self, N):
        s = ''
        base = self.get_call_arg_str(N, 0)
        index = self.get_call_arg_str(N, 1)
        s = '%s_data_ptr_pydd + %s_shape1_pydd * %s' % (base, base, index)
        return s
    
    # def gen_unboxed_slice(self, target, value):
    #     s = ''
    #     lhs = target.id
    #     table = symtab.get_func_symbol_table(self.cur_func.name)
    #     table.register_unboxed_array(lhs, (lhs+"_data"))
    #     ty = self.get_data_type(value)
    #     base = self.get_call_arg_str(value, 0)
    #     index = self.get_call_arg_str(value, 1)
    #     s = '%s* %s_%s_data = %s_data_ptr_pydd + %s_shape1_pydd * %s' \
    #                     % (ty, base, index, base, base, index)
    #     table.register_unboxed_array(lhs, '%s_%s_data' % (base, index))
    #     return s
        

    def eval_Num(self, N: ast.Num):
#        dump(N)
        #return '(%s)%s' % (N.type, str(N.n))
        return '%s' % (str(N.n))
    
        
    def eval_name_constant(self, N: ast.Num):
        if isinstance(N.value, bool):
            if N.value is True:
                return "true"
            else:
                return "false"
        else:
            glb.exit_on_unsupported_node(N)

            
    def eval_While(self, N):
        s = ''
        #print('while at line %d inv set:' % astutils.get_line_number(N))
        if hasattr(N, 'inv_subscripts'):
            seen = set()
            for sub in N.inv_subscripts:
                name = sub.value.id
                ty = self.get_local_type(name)
                if isinstance(ty, mytypes.NpArray):
                    self.inv_subs.add(sub)
                    #print(name)
                    if name not in seen:
                        seen.add(name)
                        ndim = get_num_array_dim(sub)
                        assert ndim > 0
                        s += self.gen_data_ptr_assign(name, ndim)
            #print('')

        cond = self.eval(N.test)
        s += 'while (%s) {\n' % cond
        for expr in N.body:
            s += self.eval(expr) + ';\n'
        s += '}'
        return s

    
    def is_dict(self, N):
        return isinstance(N.type, mytypes.DictType)

    
    def eval_For(self, N: ast.For):
        s = ''
        #print('for at line %d inv set:' % astutils.get_line_number(N))
        if hasattr(N, 'inv_subscripts'):
            seen = set()
            for sub in N.inv_subscripts:
                name = sub.value.id
                ty = self.get_local_type(name)
                if isinstance(ty, mytypes.NpArray):
                    self.inv_subs.add(sub)
                    #print(name)
                    if name not in seen:
                        seen.add(name)
                        ndim = get_num_array_dim(sub)
                        assert ndim > 0
                        s += self.gen_data_ptr_assign(name, ndim)
            #print('')

        if N.is_pfor:
            libfuncs.used_packages += ['shared/omp']
            s += '#pragma omp parallel for'
            if N.vars_private:
                s += ' private(%s)' % N.vars_private
            if N.vars_lastprivate:
                s += ' lastprivate(%s)' % N.vars_lastprivate
            s += '\n'
        if self.is_dict(N.iter):
            s += self.eval_For_Dict(N)
        else:
            s += self.eval_For_Array(N)        
        
        return s

    def eval_For_Dict(self, N):
        target = self.eval_node(N.target)
        iter = self.eval_node(N.iter)
        start = '%s->begin()' % iter
        end = '%s->end()' % iter
        index = '_it'

        s = 'for (%s::iterator %s = %s; %s != %s; %s++) {\n' % \
          (N.iter.type.get_cpp_name(), index, start, index, end, index)
        s += '%s = %s->first;\n' % (target, index)
        for expr in N.body:
            s += self.eval_node(expr) + ';\n'
        s += '}'
        return s


    def eval_For_Array(self, N):
        target = self.eval_node(N.target)
        iter = self.eval_node(N.iter)

        start = '0'
        end = 'pydd::len(%s)' % iter
        step = '1'
        index = '_i'

        if self.is_range_for(N):
            start, end, step = self.get_range_args(N.iter)
        
        s = 'for (int %s = %s; %s < %s; %s += %s) {\n' % (index, start, index, end, index, step)
        if self.is_range_for(N):
            s += '%s = %s;\n' % (target, index)
        else:
            if glb.args.slice_opt and astutils.is_name(iter):
                s += '%s = pydd::getitem%s(%s, %s);\n' % (target, self.get_dimension_suffix(iter), iter, index)
            else:
                s += '%s = pydd::getitem(%s, %s);\n' % (target, iter, index)
        for expr in N.body:
            s += self.eval_node(expr) + ';\n'
        s += '}'
        return s

    def is_range_for(self, N: ast.For):
        if isinstance(N.iter, ast.Call):
            if N.iter.func.id == 'range':
                return True

        return False

    def get_range_args(self, N: ast.Call):
        if len(N.args) == 1:
            return (0, self.eval(N.args[0]), 1)
        elif len(N.args) == 2:
            return (self.eval(N.args[0]), self.eval(N.args[1]), 1)
        elif len(N.args) == 3:
            return (self.eval(N.args[0]), self.eval(N.args[1]), self.eval(N.args[2]))
        else:
            assert False
        return

    def eval_if(self, N: ast.If):
        '''        
        if 'test':
          'body'
        'orelse':

        '''
        test = self.eval(N.test)
        s = 'if (%s) {\n' % test
        for expr in N.body:
            s += self.eval(expr) + ';\n'
        s += '} '

        if not N.orelse:
            return s

        s += 'else '
        if isinstance(N.orelse[0], ast.If):
            assert len(N.orelse) == 1
            s += self.eval_if(N.orelse[0])
        else:
            s += '{\n'
            for expr in N.orelse:
                s += self.eval(expr) + ';\n'
            s += '}'    
        return s

    
    def get_local_type(self, name):
        if name not in self.cur_func.typemap:
            assert False, 'name not found:' + name
        return self.cur_func.typemap[name]


    def get_dimension_suffix(self, var):
        ty = self.get_local_type(var)
        call = ''
        if ty.get_dimension() == 1:
            call += '_1d'
        elif ty.get_dimension() == 2:
            call += '_2d'
        else:
            pass
        return call    

    
    def eval_get_or_set_item(self, base, sub, value=None):
        indices = self.eval_Subscript_slice(sub.slice)
        assert isinstance(indices, list)
        basetype = self.get_local_type(base)
        call = 'getitem'
        args = []

        if value != None:
            call = 'setitem'
        args.append(base)

        # if sub not in self.inv_subs:
        #     print(base)
        #     print('sub:', ast.dump(sub))
        #     print(basetype.get_dimension())

        ## This is missing _data_ptr assigns
        # if basetype.get_dimension() > 0:
        #     #ndim = get_num_array_dim(sub)
        #     ndim = basetype.get_dimension()
        #     if ndim == 1:
        #         call += '_1d'
        #         args[0] = base+'_data_ptr_pydd'
        #     elif ndim == 2:
        #         call += '_2d'
        #         args[0] = base+'_data_ptr_pydd'
        #         args.append(base+'_shape1_pydd')
        #     if sub in self.inv_subs:    
        #         self.inv_subs.remove(sub)
            
        if sub in self.inv_subs:
            ndim = get_num_array_dim(sub)
            if ndim == 1:
                call += '_1d'
                args[0] = base+'_data_ptr_pydd'
            elif ndim == 2:
                call += '_2d'
                args[0] = base+'_data_ptr_pydd'
                args.append(base+'_shape1_pydd')
                
            self.inv_subs.remove(sub)    
        elif glb.args.unchecked_access and isinstance(basetype, mytypes.NpArray):
            if basetype.get_dimension() == 1:
                call += '_1d'
            elif basetype.get_dimension() == 2:
                call += '_2d'
        else:
            # -- This is getitem but is not array, like a dict getitem
            pass

        
        if value:
            args.append(value)
            
        args += indices
        s = "pydd::%s(%s)" % (call, ', '.join(args))
        return s
        

    def eval_Subscript(self, N: ast.Subscript):
        '''
        Fields: N.value[N.slice]
        '''
        # basetype = self.get_local_type(N.value.id)
        # call = 'getitem'
        # if isinstance(basetype, mytypes.NpArray):
        #     if basetype.get_dimension() == 1:
        #         call = 'getitem_1d'
        #     elif basetype.get_dimension() == 2:
        #         call = 'getitem_2d'
        # s = "pydd::%s(%s, %s)" % \
        #           (call, self.eval(N.value), self.eval_Subscript_slice(N.slice))
        # return self.eval_get_or_set_item(N.value.id, self.eval_Subscript_slice(N.slice))
        return self.eval_get_or_set_item(N.value.id, N)

    def eval_Subscript_slice(self, v):
        '''
        a[0] returns ['0']
        #a[0,1] returns '{0, 1}'
        a[0,1] returns ['0', '1']
        '''
        indices = []
        if isinstance(v, ast.Tuple):
            for e in v.elts:
                indices.append(self.eval(e))            
        else:
            indices.append(self.eval(v))
        return indices


    def eval_Dict(self, N: ast.Dict):
        assert len(N.keys) == 0, "Support for initialized dict is \
under development, please create an empty Dict and then add elements \
for now"

        # s = 'new std::map<%s, %s>{' % (N.type.key, N.type.value)
        s = 'new std::unordered_map<%s, %s>{' % (N.type.key, N.type.value)
        s += '}'
        return s

    def eval_Str(self, N):
        return '"%s"' % N.s
    
    def eval_Expr(self, N: ast.Expr):
        if isinstance(N.value, ast.Call):
            return self.eval_Call(N.value)
        else:
            raise glb.exit_on_unsupported_node(N)

    def eval_Call(self, N: ast.Call):
        # eg: Call(func=Name(id='print', ctx=Load()), args=[Name(id='i', ctx=Load())], keywords=[])
        # todo
        
        funcname  = ''
        ns = ''
        # Get function name and namespace if any
        if isinstance(N.func, ast.Name):
            funcname = N.func.id
            # if funcname == 'sub':
            #     print("funcname", funcname, 'in', self.cur_func.name)
            if glb.is_user_defined_func(funcname):
                ns = ''
            elif funcname.startswith('_') or libfuncs.is_global_func(funcname):
                ns = 'pydd'
            else:
                glb.exit_on_node(N, 'Unrecognized function: '+funcname)
            
        elif isinstance(N.func, ast.Attribute):
            if hasattr(N, 'is_module_call'):
                ns = glb.cpp_module.get_module_namespace(N.func.value.id)
                funcname = N.func.attr
            else:
                glb.exit_on_node(N, "Attribute call not supported")


        # Generate the actual call and args
        if funcname == 'get_row_ptr':
            return self.gen_unboxed_slice(N)
        s = ''
        if ns:  
            s = ns + '::' + funcname
        else:
            s = funcname
   
        s += '('
        args = []
        for arg in N.args:
            # if isinstance(arg, ast.List):
            #     args.append(self.eval_ListArg(arg))
            if isinstance(arg, ast.Tuple):
                args.append(self.eval_ListArg(arg))
            else:
                realarg = self.eval(arg)
                # Func name ends with 1 implies using slice opt
                # if funcname.endswith('1'):
                    # name = arg.id
                    # table = symtab.get_func_symbol_table(self.cur_func.name)
                    # if table.is_unboxed(name):                        
                    #     realarg = table.get_unboxed_ptr(name)
                args.append(realarg)

        # if ns != '' and libfuncs.get_version_count(funcname, ns) > 1:
        #     args.append(str(glb.get_func_version(funcname))) 
       
        s += ', '.join(args)
        s += ')'
        return s

    def eval_Attribute(self, N):
        s = 'pydd::getattr_%s(%s)' % (N.attr, self.eval(N.value))
        return s

    # def is_builtin_func(self, N):
        
    #     if isinstance(N.func, ast.Name):
    #         funcname = N.func.id
    #         for F in self.funcs:
    #             if funcname == F.name:
    #                 return False
    #         return True
    #         # if N.func.id == 'print':
    #         #     return True
    #         # elif N.func.id == 'len':
    #         #     return True
    #     else:
    #         assert False
        
    #     return False
        
    def eval_List(self, N: ast.List):
        s = 'new std::vector<%s>{' % N.type.etype    
        s += ', '.join(list(map(lambda x: self.eval_node(x), N.elts)))
        s += '}'
        return s

    def eval_ListArg(self, N):
        s = '{'
        s += ', '.join(list(map(lambda x: self.eval_node(x), N.elts)))
        s += '}'
        return s
        
    def eval_Compare(self, N: ast.Compare):
        assert len(N.ops) == len(N.comparators)
        compares = []
        l = N.left
        for i in range(len(N.ops)):
            op = N.ops[i]
            r = N.comparators[i]
            compares.append(self.eval_cmpop(op, l, r))
            l = r
        return '&&'.join(compares)    

    def eval_cmpop(self, op, l, r):
        s = ''
        lhs = self.eval(l)
        rhs = self.eval(r)
        if isinstance(op, ast.Eq):
            s = '%s == %s' % (lhs, rhs)
        elif isinstance(op, ast.NotEq):
            s = '%s != %s' % (lhs, rhs)
        elif isinstance(op, ast.Lt):
            s = '%s < %s' % (lhs, rhs)
        elif isinstance(op, ast.LtE):
            s = '%s <= %s' % (lhs, rhs) 
        elif isinstance(op, ast.Gt):
            s = '%s > %s' % (lhs, rhs)
        elif isinstance(op, ast.GtE):
            s = '%s >= %s' % (lhs, rhs)
        else:
            raise UnhandledNodeException(op)

        return '(%s)' % s

    def eval_BoolOp(self, N):
        op = N.op
        opstr = ''
        s = ''
        if isinstance(op, ast.And):
            opstr = ' && '
            s = opstr.join(list(map(lambda x: self.eval(x), N.values)))
        elif isinstance(op, ast.Or):
            opstr = ' || '
            s = opstr.join(list(map(lambda x: self.eval(x), N.values)))
        else:
            glb.exit_on_unsupported_node(N)

        return s    
            

    def eval_BinOp(self, N: ast.BinOp):
        return '(' + self.eval_BinOp_raw(N.op, N.left, N.right) + ')'

    def eval_BinOp_raw(self, op, left, right):
        lhs = self.eval(left)
        rhs = self.eval(right)
        s = ''
        if isinstance(op, ast.Add):
            s += '%s + %s' % (lhs, rhs)
        elif isinstance(op, ast.Sub):
            s += '%s - %s' % (lhs, rhs)
        elif isinstance(op, ast.Mult):
            s += '%s * %s' % (lhs, rhs)
        elif isinstance(op, ast.Div):
            s += '((double)%s) / %s' % (lhs, rhs)
        elif isinstance(op, ast.FloorDiv):
            s += '%s / %s' % (lhs, rhs)
        elif isinstance(op, ast.Pow):
            s += 'pydd::pow(%s, %s)' % (lhs, rhs)
        elif isinstance(op, ast.LShift):
            s += '%s << %s' % (lhs, rhs)
        else:
            raise UnhandledNodeException('unrecognized op: '+op)
        return s

    def eval_UnaryOp(self, N):
        operand = self.eval(N.operand)
        s = ''
        if isinstance(N.op, ast.USub):
            s = '-%s' % operand 
        elif isinstance(N.op, ast.Not):
            s = '!%s' % operand 
        else:
            raise UnhandledNodeException(N)
        return s
            
    def eval_Continue(self, N: ast.Continue):        
        return 'continue'

    def eval_Break(self, N: ast.Break):        
        return 'break'

    def eval_Pass(self, N: ast.Break):        
        return '// pass'

    def eval_Return(self, N: ast.Return):        
        return 'return ' + self.eval(N.value)
        
    def eval_Assert(self, N: ast.Assign):
        
        return 'assert ' + self.eval(N.test)
        
        
    def visit_ImportFrom(self, node):
        self.generic_visit(node)

    def report(self):
        pprint(self.stats)

