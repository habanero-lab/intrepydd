from . import defuse
import ast
from . import mytypes
from .utils import get_operator_expansion_func
from . import glb

### Options ###
# 0: Nothing, 1: Debug
verbose_level = 1

# Class used to expand operators into vector library calls
class OperatorExpansion(ast.NodeTransformer):

    def visit_BinOp(self, N: ast.BinOp):
        left = N.left
        right = N.right

        left = self.visit(N.left)
        right = self.visit(N.right)

        # If the expression contains a vector, try to expand the operator into a function
        if hasattr(N, 'type') and mytypes.is_array(N.type):
            func_name = get_operator_expansion_func(N.op)

            # Throw an error when the operator cannot be expanded into a library function
            if func_name == 'n/a':
                msg = "Unidentified operator %s\n" % N.op
                glb.exit_on_node(N, msg)

            if verbose_level >= 1:
                print('[Verbose] found BinOp (%s) to convert into global func: %s' % (N.op, func_name))

            # Transform the BinOp into the correct function call
            func = ast.Name(id=func_name, ctx=ast.Load())
            args = [left, right]

            N = ast.Call(func=func, args=args, keywords=[])

        return N


    def visit_AugAssign(self, N):        
        if hasattr(N.target, "type") and mytypes.is_array(N.target.type):
            op = N.op
            func = ''
            if isinstance(op, ast.Add):
                func = 'plus_eq'   # maybe this should be add_eq
            elif isinstance(op, ast.Sub):
                func = 'sub_eq'
            elif isinstance(op, ast.Mul):
                func = 'mul_eq'
            elif isinstance(op, ast.Div):
                func = 'div_eq'
            else:
                return N

            args = [N.target, N.value]
            call = ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=args, keywords=[])

            return call
        
        return N

