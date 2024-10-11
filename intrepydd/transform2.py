import ast
from . import libfuncs
from . import glb
from . import scalarpriv
from . import licmarray
from . import licmast
from . import opexpansion
from . import arrayopt

class TypedTransformer(ast.NodeVisitor):
    def visit(self, tree):
        # Todo: invoke operator expansion
        #  - E.g., convert "A = B * C" into "A = mul(B, C)" when B and/or C has array type.
        #  - Create a new file for this functionality (similar to scalarpriv/loopinvariant below)
        opexpansion.OperatorExpansion().visit(tree)

        # Loop Invariant Code Motion for AST-level expressions (general)
        if 'licm_ast' in glb.options and glb.options['licm_ast']:
            licmast.LicmAstOptimization().visit(tree)

        # Sparse/dense array optimizations
        if ('sparse_opt' in glb.options and glb.options['sparse_opt']
            or 'dense_opt' in glb.options and glb.options['dense_opt']):
            arrayopt.ArrayOptimization().visit(tree)

        # Privatization for parallel loops (pfor)
        scalarpriv.ScalarPrivatization().visit(tree)

        # Loop Invariant Code Motion for array references
        if 'licm_array' in glb.options and glb.options['licm_array']:
            licmarray.LicmArrayAnalysis().visit(tree)
