import sys
import ast
from pprint import pprint
import traceback
import logging

from . import mytypes as types
from . import glb
from . import utils
from . import libfuncs
from .symboltable import symtab
from .glb import UnhandledNodeException
from .glb import dump
from .astutils import *
from . import utils
import defuse


class EscapeAnalysis(defuse.DefUseAnalysis):
    def __init__(self):
        defuse.DefUseAnalysis.__init__(self)
        self.symbols = None
        self.logger = utils.get_logger('ea')

        
    def visit_FunctionDef(self, F: ast.FunctionDef):
        self.visit_FunctionDef_main(F)
        self.symbols = symtab.get_func_symbol_table(F.name)
        self.do_function(F)


    def do_function(self, F: ast.FunctionDef):
        F.aliased_var = []
        for stmt in F.body:
            self.do_stmt(stmt, F)
            

    def do_stmt(self, s, F):        
        if is_assign(s):
            rhs = get_rhs(s)
            if is_name(rhs):
                var = get_name_id(rhs)
                ty = symtab.get_local_type(F.name, var)
                if types.is_array(ty) and var not in F.aliased_var: 
                    F.aliased_var.append(var)
                    self.logger.debug("add aliased var: %s" % var)

        if is_loop(s):
            self.do_loop(s, F)

            
    def get_loop_private_vars(self, L):
        if is_for(L):
            defuse.DefUseAnalysis.visit_For(self, L)
        if is_while(L):
            defuse.DefUseAnalysis.visit_While(self, L)
        myinfo = self.level_tree_current
        vars_local = (myinfo.vars_may_def | myinfo.vars_cond_def) - myinfo.vars_use
        return vars_local
    
        
    def do_loop(self, L, F):
        privatevars = self.get_loop_private_vars(L)
        #print(privatevars)
        body = get_loop_body(L)
        sites = []
        L.alloc_sites = sites
        
        for stmt in body:
            self.do_stmt(stmt, F)
            if is_alloc_site(stmt):
                lhs = get_lhs(stmt)
                assert is_name(lhs)
                var = get_name_id(lhs)
                # if var == 'frontier':
                #     continue
                # if var == 'r':
                #     continue
                if var in F.aliased_var:
                    self.logger.debug('skip aliased var: %s' % var)
                    continue
                if var not in privatevars:
                    self.logger.debug('skip nonprivate var: %s' % var)
                    continue
                sites.append(stmt)


    # def do_stmt(self, s, F):
    #     # Check defs
    #     if is_local_def(s):
    #         var = get_defined_name(s)
    #         self.symbols.add_def(var, s)

    #     # Check uses    
    #     if is_setitem(s):
    #         var = get_setitem_base(s)
    #         self.symbols.add_use(var, s)
    #         value = get_setitem_value(s)
    #         if is_name(value):
    #             self.symbols.add_use(value.id, s)
    #         elif is_bin_op(value):
    #             for operand in get_bin_op_operands(value):
    #                 if is_name(operand):
    #                     self.symbols.add_use(operand.id, s)
    #         else:
    #             print('[unhandled]:', value)
        
    #     if is_loop(s):
    #         self.do_loop(s, F)

         
