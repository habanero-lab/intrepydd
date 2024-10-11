from . import glb
from .symboltable import symtab
from .glb import dump
from . import mytypes
from . import utils
import ast

class Scanner(ast.NodeVisitor):
    def __init__(self):
        self.cur_func = None
    
    def visit_Module(self, N):
        self.generic_visit(N)

    def visit_Import(self, N):        
        glb.cpp_module.add_imported_module(N.names[0])
        
    def visit_FunctionDef(self, N: ast.FunctionDef):
        N.ret_type = mytypes.void
        if N.returns:
            N.ret_type = utils.get_annotation_type(N.returns)
        N.localtypes = {} 
        symtab.register_user_func(N)
        
        
