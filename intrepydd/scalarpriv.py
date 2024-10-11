from enum import Enum
import ast
from . import libfuncs
from . import defuse

'''
Support scalar privatization for loop parallelization.

Todo:
 - Standardize options, print (verbose and warning), and assert
'''

### Options ###
# 0: Nothing, 1: Warning, 2: Debug (light), 3: Debug (moderate), 4: Debug (heavy)
verbose_level = 1
# To enable nested parallel loops
enable_nested_pfor = False

### Functions to access/modify ast.For nodes ###
def is_pfor(N: ast.For):
    return N.is_pfor

def serialize_pfor(N: ast.For, reason):
    N.is_pfor = False

    global verbose_level
    if verbose_level >= 1:
        print('[Warning] Serialize pfor at line', N.lineno, 'due to:', reason)

def add_private_sets(N: ast.For, vars_private, vars_lastprivate):
    assert N.is_pfor
    N.vars_private = vars_private
    N.vars_lastprivate = vars_lastprivate

    global verbose_level
    if verbose_level >= 2:
        ln = N.lineno if hasattr(N, 'lineno') else '???'
        print('[Verbose] Safe pfor at line', ln,
              'with private:', vars_private, '/ lastprivate:', vars_lastprivate)

is_first_to_enable_openmp = False
def enable_openmp():
    global is_first_to_enable_openmp
    if not is_first_to_enable_openmp:
        libfuncs.add_function_module('omp')
        is_first_to_enable_openmp = True

### Utilities ###
def to_csv(vars):
    s = ''
    if vars:
        s += vars.pop()
        for var in vars:
            s += ', %s' % var
    return s


############################################################################################

class ScalarPrivatization(defuse.DefUseAnalysis):

    def __init__(self):
        '''
        Information per Function Definition
        '''
        defuse.DefUseAnalysis.__init__(self)
        self.nodes_pfor = []  # LevelTreeNode list of pfor loops

    def verify_fields(self):
        defuse.DefUseAnalysis.verify_fields(self)
        assert not self.nodes_pfor

    def clear_level_tree_information(self):
        defuse.DefUseAnalysis.clear_level_tree_information(self)
        self.nodes_pfor.clear()

    def add_nodes_pfor(self, level_node, N: ast.For):
        if is_pfor(N):
            self.nodes_pfor.append(level_node)

    def serialize_enclosing_pfors(self, reason):
        curr = level_tree_current
        while curr:
            if curr.prev:
                curr = curr.prev
            else:
                curr = curr.parent
                if curr and (curr.kind is self.LevelTreeNode.Kind.FOR):
                    N = curr.ast_node
                    assert isinstance(N, ast.For)
                    if is_pfor(N):
                        serialize_pfor(N, reason)
                        self.nodes_pfor.remove(curr)
    '''
    Note:
    This algorithm to compute live-out set is not exact, i.e., the return value
    is set of variables that 'may' live out from the pfor specified by level_pfor.
    However, this decision is always safe in terms of privatization.
    '''
    def compute_vars_live_out(self, vars_target: set, level_pfor):
        vars_live_out = set()
        for var in vars_target:
            if var not in self.var_to_nodes:
                continue
            is_live_out = False
            for node_ref in self.var_to_nodes[var]:
                if defuse.vector_include(level_pfor, node_ref.level):
                    continue
                node_s = None
                node_t = node_ref
                curr = node_ref
                while curr:
                    if curr.prev:
                        if var in curr.prev.vars_def:
                            node_s = curr.prev
                            break
                        curr = curr.prev
                    else:
                        curr = curr.parent
                        if curr and (curr.kind is self.LevelTreeNode.Kind.FOR):
                            assert isinstance(curr.ast_node, ast.For)
                            node_t = curr
                if not node_s:
                    node_s = self.level_tree_head

                if (defuse.vector_compare(level_pfor, node_s.level) >= 0
                    and defuse.vector_compare(node_t.level, level_pfor) >= 0):
                    is_live_out = True
                    break
            if is_live_out:
                vars_live_out.add(var)
        return vars_live_out

    def get_outer_pfor(self, level_node):
        curr = level_node
        while curr:
            if curr.prev:
                curr = curr.prev
            else:
                curr = curr.parent
                if curr and (curr.kind is self.LevelTreeNode.Kind.FOR):
                    N = curr.ast_node
                    assert isinstance(N, ast.For)
                    if is_pfor(N):
                        return curr  # Return outer pfor
        return None

    def eval_pfor(self, level_node):
        N = level_node.ast_node
        assert is_pfor(N)

        is_parallel = False
        level = level_node.level
        if (not enable_nested_pfor) and self.get_outer_pfor(level_node):
            serialize_pfor(N, 'outer pfor (no nested pfor supported).')
        elif level_node.vars_use & (level_node.vars_may_def | level_node.vars_cond_def):
            serialize_pfor(N, 'exposed use.')
        elif self.compute_vars_live_out(level_node.vars_may_def, level):
            serialize_pfor(N, 'live-ouf of may-def variables.')
        else:
            is_parallel = True
            vars_private = level_node.vars_may_def
            vars_lastprivate = self.compute_vars_live_out(level_node.vars_cond_def, level)
            vars_private |= (level_node.vars_cond_def - vars_lastprivate)
            add_private_sets(N, to_csv(vars_private), to_csv(vars_lastprivate))
            enable_openmp()
        return is_parallel

    def eval_all_pfors(self):
        global verbose_level
        if verbose_level >= 3:
            self.show_fields(verbose_level >= 4)

        updated = []
        for node in self.nodes_pfor:
            if self.eval_pfor(node):
                updated.append(node)
        self.nodes_pfor = updated

        if verbose_level >= 3:
            print('')


############################################################################################

    def visit_FunctionDef(self, N: ast.FunctionDef):
        if N.has_pfor:
            self.verify_fields()

            self.visit_FunctionDef_main(N)

            self.eval_all_pfors()

            self.clear_level_tree_information()

    def visit_For_head(self, N: ast.For):
        for_node = self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.FOR)
        self.add_nodes_pfor(for_node, N)
        self.visit(N.iter)

        self.update_level_tree_with_child(N.target, self.LevelTreeNode.Kind.FOR_IN)
        if isinstance(N.target, ast.Name):
            self.define_var(N.target.id)
        else:
            # Loop iterator is not scalar
            self.visit(N.target)

        return for_node

    def visit_Continue(self, node):
        self.serialize_enclosing_pfors('continue')

    def visit_Break(self, node):
        self.serialize_enclosing_pfors('break')

    def visit_Assert(self, node):
        self.serialize_enclosing_pfors('assert')
