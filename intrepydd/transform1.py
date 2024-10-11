import ast
from . import libfuncs
from . import glb
'''
Support AST transformations that are independent from type information.

Todo:
 - Standardize options, print (verbose and warning), and assert
'''

### Options ###
# 0: Nothing, 1: Debug
verbose_level = 0

class TypeFreeTransformer(ast.NodeTransformer):
    def visit_Call(self, N):
        '''
        Conversion: "A.abs()" into "abs(A)"
        '''
        candidate = isinstance(N.func, ast.Attribute) and libfuncs.is_global_func(N.func.attr)
        if candidate and isinstance(N.func.value, ast.Name):
            candidate = not glb.cpp_module.is_module(N.func.value.id)

        if candidate:
            if verbose_level >= 1:
                print('[Verbose] found Attribute to convert into global func:', N.func.attr)

            
            func_name = N.func.attr
            func_ctx = self.visit(N.func.ctx)
            func_arg = self.visit(N.func.value)
            N.func = ast.Name(id=func_name, ctx=func_ctx)
            args = [func_arg]
        else:
            N.func = self.visit(N.func)
            args = []

        for arg in N.args:
            args.append(self.visit(arg))
        N.args = args
        keys = []
        for key in N.keywords:
            keys.append(self.visit(key))
        N.keys = keys

        return N

    def visit_Attribute(self, N):
        if N.attr == 'T':
            if verbose_level >= 1:
                print('[Verbose] found Attribute to convert into global func: transpose')

            # Conversion: "A.T" into "transpose(A)"
            func = ast.Name(id='transpose', ctx=ast.Load())
            args = [self.visit(N.value)]
            N = ast.Call(func=func, args=args, keywords=[])
        else:
            #print(ast.dump(N))
            N.value = self.visit(N.value)
            N.ctx = self.visit(N.ctx)

        return N

    def visit_BinOp(self, N):
        if isinstance(N.op, ast.MatMult):
            if verbose_level >= 1:
                print('[Verbose] found BinOp (@) to convert into global func: matmult')

            # Conversion: "A @ B" into "matmult(A, B)"
            func = ast.Name(id='matmult', ctx=ast.Load())
            arg1 = self.visit(N.left)
            arg2 = self.visit(N.right)
            args = [arg1, arg2]
            N = ast.Call(func=func, args=args, keywords=[])
        else:
            N.left = self.visit(N.left)
            N.op = self.visit(N.op)
            N.right = self.visit(N.right)

        return N


