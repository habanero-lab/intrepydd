from enum import Enum
import ast
from . import libfuncs
from . import mytypes

'''
Support def use analysis.

Todo:
 - Element-wise analysis
 - Standardize options, print (verbose and warning), and assert
'''

# Fuctions whose arguments are read-only
a1l = 'arg1_len'
adm = 'arg_max_dim'
rsm = 'red_sum'
mml = 'matmult'
pure_funcs = {
    'len': 0, 'boolean': 0, 'int32': 0, 'int64': 0, 'float32': 0, 'float64': 0, 'range': 1,
    'zeros': a1l, 'zeros_2d': 2, 'empty': a1l, 'empty_2d': 2,
    'empty_like': adm, 'get_row': 1, 'get_col': 1, 'Array': 0,
    'sum_rows': 1, 'shape': 0, 'stride': 0, 'dsyrk': 2,
    # Reduction
    'sum': rsm, 'prod': 0, 'min': 0, 'max': 0, 'argmin': 0, 'argmax': 0,
    'any': 0, 'all': 0, 'allclose': 0, 'where': 1,
    # Element-wise unary
    'abs': adm, 'minus': adm, 'isnan': adm, 'isinf': adm, 'elemwise_not': adm, 'sqrt': adm,
    'exp': adm, 'cos': adm, 'sin': adm, 'tan': adm, 'acos': adm, 'asin': adm, 'atan': adm,
    # Element-wise binary
    'add': adm, 'sub': adm, 'mul': adm, 'maximum': adm, 'pow': adm, 'div': adm, 'log': adm,
    'eq': adm, 'neq': adm, 'lt': adm, 'gt': adm, 'le': adm, 'ge': adm,
    'logical_and': adm, 'logical_or': adm, 'logical_xor': adm, 'logical_not': adm,
    # Matrix operations
    'transpose': 2, 'innerprod': 0, 'matmult': mml,
    'lu': 2, 'qr': 2, 'eig': 2, 'svd': 2, 'tril': 2, 'triu': 2, 'diag': 2, 'kron': 2, 'convolve': 2,
    # Sparse matrix operations
    'empty_spm': 2, 'csr_to_spm': 2, 'arr_to_spm': 2,
    'getval': 0, 'getnnz': 0, 'getcol': 0, 'nnz': 0,
    'spm_add': 2, 'spm_mul': 2, 'spmm': 2, 'spmv': 1,
    'spmm_dense': 2, 'sparse_diags': 2, 'spm_diags': 2,
    # Heap
    'heapinit': 1, 'heappeek': 0, 'heapsize': 0,
}

upd_funcs = {
    'append': 0, 'set_row': 0, 'set_col': 0, 'plus_eq': 0, 'minus_eq': 0,
    # Sparse matrix operations
    'spm_to_csr': [1,2,3], 'spm_set_item': 0, 'spm_set_item_unsafe': 0,
    # Heap
    'heappush': 0, 'heappop': 0,
}

### Utilities ###
def vector_include(vect1, vect2):
    n = len(vect1)
    if len(vect2) <= n:
        return False
    for i in range(n):
        if vect1[i] != vect2[i]:
            return False
    return True

def vector_compare(vect1, vect2):
    n = len(vect1) if len(vect1) < len(vect2) else len(vect2)
    for i in range(n):
        if (vect1[i] < vect2[i]):
            return -1
        elif (vect1[i] > vect2[i]):
            return 1
    return 0


############################################################################################

class DefUseAnalysis(ast.NodeVisitor):
    '''
    Information per AST node
    '''
    class LevelTreeNode:
        class Kind(Enum):
            UNDEF = -1
            FUNC = 0
            FOR = 1
            FOR_IN = 2
            WHILE = 3
            WHILE_IN = 4
            IF = 5
            IF_IN = 6
            ELSE = 7
            ELSE_IN = 8
            ASSIGN = 9
            AUG_ASSIGN = 10
            ANN_ASSIGN = 11
            CALL = 12
            RETURN = 13

        def __init__(self, level, ast_node, kind, prev, parent):
            if isinstance(level, list):
                self.level = tuple(level)
            else:
                self.level = level
            self.ast_node = ast_node
            self.kind = kind
            # Variable sets
            self.vars_use = set()       # Exposed use (not self-defined value)
            self.vars_def = set()       # Must def
            self.vars_cond_def = set()  # Must def within body (If/Else/Loop)
            self.vars_may_def = set()
            self.vars_em_def = set()
            # Tree link
            self.prev = prev
            self.next = None
            self.parent = parent
            self.child = None

        def show(self):
            print('[Verbose] dump LevelTreeNode of level:', self.level, '-', self.kind)
            if self.vars_use: print(' - vars_use', self.vars_use)
            if self.vars_def: print(' - vars_def', self.vars_def)
            if self.vars_may_def: print(' - vars_may_def', self.vars_may_def)
            if self.vars_em_def: print(' - vars_em_def', self.vars_em_def)
            if self.vars_cond_def: print(' - vars_cond_def', self.vars_cond_def)

        def copy(self):
            cp = DefUseAnalysis.LevelTreeNode(self.level, self.ast_node, self.kind,
                                              self.prev, self.parent)
            cp.vars_use = self.vars_use.copy()
            cp.vars_def = self.vars_def.copy()
            cp.vars_may_def = self.vars_may_def.copy()
            cp.vars_em_def = self.vars_em_def.copy()
            cp.vars_cond_def = self.vars_cond_def.copy()
            cp.next = self.next
            cp.child = self.child
            return cp

        def is_assign(self):
            return (self.kind is DefUseAnalysis.LevelTreeNode.Kind.ASSIGN
                    or self.kind is DefUseAnalysis.LevelTreeNode.Kind.AUG_ASSIGN
                    or self.kind is DefUseAnalysis.LevelTreeNode.Kind.ANN_ASSIGN)

        def update_child_level(self):
            ch = self.child
            nl = list(self.level)
            nl.append(0)
            while ch:
                nl[-1] = ch.level[-1]
                ch.level = tuple(nl)
                if ch.child:
                    ch.update_child_level()
                ch = ch.next

    def __init__(self):
        '''
        Information per Function Definition
        '''
        self.curr_func = None
        self.level_tree_head = None
        self.level_tree_current = None
        self.status = []        # Current level during traverse
        self.var_to_nodes = {}  # Key: variable, Value: LevelTreeNodes to ref variable

    def verify_fields(self):
        assert not self.level_tree_head
        assert not self.level_tree_current
        assert not self.status
        assert not self.var_to_nodes

    def show_fields(self, show_all, curr = None):
        is_top = False
        if curr is None:
            curr = self.level_tree_head
            is_top = True

        if show_all or (curr.kind is self.LevelTreeNode.Kind.FOR
                        or curr.kind is self.LevelTreeNode.Kind.WHILE):
            curr.show()
        if curr.child:
            self.show_fields(show_all, curr.child)
        if curr.next:
            self.show_fields(show_all, curr.next)

        if is_top:
            print("[Verbose] dump mapping: variable -> levels to use\n", end = ' - ')
            for var in self.var_to_nodes:
                print(var, ':', end = ' ')
                for node in self.var_to_nodes[var]:
                    print(node.level, end = ', ')
                print(end = ' ')
            print('')

    def delete_tree_branches(self, curr):
        next = curr.next
        if next:
            next.prev = None
            curr.next = None
            self.delete_tree_branches(next)
            del next
        child = curr.child
        if child:
            curr.child = None
            child.parent = None
            self.delete_tree_branches(child)
            del child
        curr = None

    def clear_level_tree_information(self):
        self.var_to_nodes.clear()
        self.status.clear()

        tmp = self.level_tree_head
        self.level_tree_head = None
        self.level_tree_current = None
        if tmp:
            self.delete_tree_branches(tmp)
            del tmp

    def define_var(self, var):
        self.level_tree_current.vars_def.add(var)

    def define_em_var(self, var):
        self.level_tree_current.vars_em_def.add(var)

    def define_em_var_recurse(self, N):
        if isinstance(N, ast.Name) and N.id in self.curr_func.typemap:
            ty = self.curr_func.typemap[N.id]
            assert ty
            if isinstance(ty, mytypes.IterableType):
                self.define_em_var(N.id)

        for node in ast.iter_child_nodes(N):
            self.define_em_var_recurse(node)

    def check_and_def_em_subscr(self, N):
        if isinstance(N, ast.Subscript) and isinstance(N.value, ast.Name):
            self.define_em_var(N.value.id)

    def check_and_def_em_func(self, N):
        if not isinstance(N, ast.Call):
            return

        args = N.args
        if isinstance(N.func, ast.Name):
            func = N.func.id
            if func in pure_funcs:
                return
            elif func in upd_funcs:
                upd = upd_funcs[func]
                if isinstance(upd, int):
                    self.define_em_var_recurse(args[upd])
                else:
                    assert isinstance(upd, list)
                    for u in upd:
                        if u < len(args):
                            self.define_em_var_recurse(args[u])
                return

        for arg in args:
            self.define_em_var_recurse(arg)

    def use_var(self, var):
        if var not in self.level_tree_current.vars_use:
            self.level_tree_current.vars_use.add(var)
            if var in self.var_to_nodes:
                self.var_to_nodes[var].add(self.level_tree_current)
            else:
                self.var_to_nodes[var] = {self.level_tree_current}

    def add_level_tree_head(self, N, kind):
        self.status = [0]
        self.level_tree_head = self.LevelTreeNode(self.status, N, kind, None, None)
        self.level_tree_current = self.level_tree_head

    def update_level_tree_with_sibling(self, N, kind):
        self.status[-1] += 1
        prev = self.level_tree_current
        next = self.LevelTreeNode(self.status, N, kind, prev, None)
        prev.next = next
        self.level_tree_current = next
        return next

    def update_level_tree_with_child(self, N, kind):
        self.status.append(0)
        parent = self.level_tree_current
        child = self.LevelTreeNode(self.status, N, kind, None, parent)
        parent.child = child
        self.level_tree_current = child
        return child

    def collect_child_def_use(self, level_node):
        vars_use = set()
        vars_def = set()
        vars_may_def = set()
        vars_em_def = set()
        node = level_node.child
        while node:
            vars_use |= (node.vars_use - vars_def)
            vars_def |= node.vars_def
            vars_may_def |= (node.vars_may_def | node.vars_cond_def)
            vars_em_def |= node.vars_em_def
            node = node.next
        vars_may_def -= vars_def
        vars_em_def -= vars_def
        level_node.vars_use |= vars_use
        level_node.vars_cond_def |= vars_def
        level_node.vars_may_def |= vars_may_def
        level_node.vars_em_def |= vars_em_def

        self.status.pop()
        assert tuple(self.status) == level_node.level
        self.level_tree_current = level_node


############################################################################################

    def visit_body_core(self, N: ast.stmt):
        if isinstance(N, ast.Expr) and isinstance(N.value, ast.Call):
            self.visit_Call(N, True)
        else:
            self.visit(N)

    def visit_body(self, stmts: list):
        for stmt in stmts:
            self.visit_body_core(stmt)

    def visit_FunctionDef_main(self, N: ast.FunctionDef):
        self.add_level_tree_head(N, self.LevelTreeNode.Kind.FUNC)
        for item in N.args.args:
            self.visit(item)
            self.define_var(item.arg)
        if N.args.vararg is not None:
            self.visit(N.args.vararg)
            self.define_var(N.args.vararg.arg)
        for item in N.args.kwonlyargs:
            self.visit(item)
            self.define_var(item.arg)
        for item in N.args.kw_defaults:
            self.visit(item)
        if N.args.kwarg is not None:
            self.visit(N.args.kwarg)
            self.define_var(N.args.kwarg.arg)
        for item in N.args.defaults:
            self.visit(item)
        for item in N.decorator_list:
            self.visit(item)

        self.visit_body(N.body)

    def visit_FunctionDef(self, N: ast.FunctionDef):
        self.curr_func = N
        self.verify_fields()
        self.visit_FunctionDef_main(N)

        # Note: perform analysis here

        self.clear_level_tree_information()

    def visit_For_head(self, N: ast.For):
        for_node = self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.FOR)
        self.visit(N.iter)

        self.update_level_tree_with_child(N.target, self.LevelTreeNode.Kind.FOR_IN)
        if isinstance(N.target, ast.Name):
            self.define_var(N.target.id)
        else:
            # Loop iterator is not scalar
            self.visit(N.target)

        return for_node

    def visit_For(self, N: ast.For):
        for_node = self.visit_For_head(N)

        self.visit_body(N.body)
        self.collect_child_def_use(for_node)

        assert not N.orelse

    def visit_While_head(self, N: ast.While):
        while_node = self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.WHILE)
        self.visit(N.test)

        self.update_level_tree_with_child(None, self.LevelTreeNode.Kind.WHILE_IN)

        return while_node

    def visit_While(self, N: ast.While):
        while_node = self.visit_While_head(N)

        self.visit_body(N.body)
        self.collect_child_def_use(while_node)

        assert not N.orelse

    def visit_If(self, N: ast.If):
        if_node = self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.IF)
        self.visit(N.test)

        self.update_level_tree_with_child(None, self.LevelTreeNode.Kind.IF_IN)
        self.visit_body(N.body)
        self.collect_child_def_use(if_node)

        if N.orelse:
            else_node = self.update_level_tree_with_sibling(None, self.LevelTreeNode.Kind.ELSE)
            self.update_level_tree_with_child(None, self.LevelTreeNode.Kind.ELSE_IN)
            self.visit_body(N.orelse)
            self.collect_child_def_use(else_node)
            vars_def = if_node.vars_cond_def & else_node.vars_cond_def
            if vars_def:
                else_node.vars_def |= vars_def
                else_node.vars_cond_def -= vars_def

    def visit_Assign(self, N: ast.Assign):
        self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.ASSIGN)
        self.visit(N.value)
        for item in N.targets:
            if isinstance(item, ast.Name):
                self.define_var(item.id)
            else:
                # Assignment to non-scalar variable
                self.visit(item)
                self.check_and_def_em_subscr(item)

    def visit_AugAssign(self, N: ast.AugAssign):
        self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.AUG_ASSIGN)
        self.visit(N.value)
        if isinstance(N.target, ast.Name):
            self.use_var(N.target.id)
            self.define_var(N.target.id)
        else:
            # AugAssignment to non-scalar variable
            self.visit(N.target)
            self.check_and_def_em_subscr(N.target)

    def visit_AnnAssign(self, N: ast.AnnAssign):
        self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.ANN_ASSIGN)
        self.visit(N.annotation)
        self.visit(N.value)
        if isinstance(N.target, ast.Name):
            self.define_var(N.target.id)
        else:
            # AnnAssignment to non-scalar variable
            self.visit(N.target)
            self.check_and_def_em_subscr(N.target)

    def visit_Call(self, N, is_stmt = False):
        if is_stmt:
            assert isinstance(N, ast.Expr)
            self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.CALL)
            Nv = N.value
        else:
            Nv = N

        self.visit(Nv.func)
        for item in Nv.args:
            self.visit(item)
        for item in Nv.keywords:
            self.visit(item)

        if self.curr_func:
            self.check_and_def_em_func(Nv)

    def visit_Return(self, N: ast.Return):
        if N.value:
            self.update_level_tree_with_sibling(N, self.LevelTreeNode.Kind.RETURN)
            self.visit(N.value)

    def visit_Name(self, N: ast.Name):
        # modify to not use function names
        self.use_var(N.id)
