from enum import Enum
import ast
from . import libfuncs
from . import mytypes
from . import defuse
from . import arrayopt

'''
Loop Invariant Code Motion for AST-level expressions (general)
'''

### Options ###
# 0: Nothing, 1: Warning, 2: Debug (light), 3: Debug (moderate), 4: Debug (heavy)
verbose_level = 1

dumpfunc = ast.dump


############################################################################################

class LicmAstOptimization(defuse.DefUseAnalysis):
    def __init__(self):
        defuse.DefUseAnalysis.__init__(self)

    def contains_nonpure_func(self, expr):
        if (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name)
            and expr.func.id not in defuse.pure_funcs):
            return True

        for node in ast.iter_child_nodes(expr):
            if self.contains_nonpure_func(node):
                return True

        return False

    def is_invstmt_candidate(self, node):
        return (node.kind is self.LevelTreeNode.Kind.ASSIGN
                or node.kind is self.LevelTreeNode.Kind.ANN_ASSIGN)

    def is_loop_init(self, node):
        return (node.kind is self.LevelTreeNode.Kind.FOR_IN
                or node.kind is self.LevelTreeNode.Kind.WHILE_IN)

    def collect_invariant_statements(self, loop_node):
        invstmt_nodes = []
        vars_ro = (loop_node.vars_use - loop_node.vars_def - loop_node.vars_cond_def
                   - loop_node.vars_may_def - loop_node.vars_em_def)
        var_i = loop_node.child.vars_def
        vars_l = (loop_node.vars_cond_def - loop_node.vars_use - var_i)
        if verbose_level >= 2:
            print('[Verbose] Search invariant statements in:', loop_node.kind, loop_node.level)
            if verbose_level >= 3:
                print('[Verbose] read-only vars:', vars_ro)
                print('[Verbose] loop index:', var_i)
                print('[Verbose] local vars:', vars_l)

        node = loop_node.child
        while node:
            if (node not in invstmt_nodes and self.is_invstmt_candidate(node)
                and node.vars_def.issubset(vars_l) and node.vars_use.issubset(vars_ro)):
                group = [node]
                used = False
                succ = node.next
                while succ:
                    def_succ = (succ.vars_def | succ.vars_cond_def
                                | succ.vars_may_def | succ.vars_em_def)
                    if def_succ & node.vars_def:
                        if (self.is_invstmt_candidate(succ)
                            and def_succ.issubset(node.vars_def)
                            and not used
                            and succ.vars_use.issubset(vars_ro | node.vars_def)):
                            group.append(succ)
                        else:
                            break
                    elif succ.vars_use & node.vars_def:
                        used = True
                    succ = succ.next

                if not succ:
                    for n in group:
                        if not self.contains_nonpure_func(n.ast_node):
                            if verbose_level >= 2:
                                print('[Verbose] Invariant statement found at:', n.level)
                                if verbose_level >= 3:
                                    n.show()
                                    if verbose_level >= 4: print(dumpfunc(n.ast_node))
                            invstmt_nodes.append(n)
                            vars_ro |= n.vars_def

            node = node.next

        return invstmt_nodes

    def verify_and_collect_cs_expr(self, expr: ast.expr, vars_ro: set, cs_exprs: dict, top = False):
        ope_nest = -1
        num_dims = -1

        if isinstance(expr, ast.Num):
            ope_nest = 0
            num_dims = 0
        elif isinstance(expr, ast.Name):
            if expr.id in vars_ro:
                ope_nest = 0
            if expr.id in self.curr_func.typemap:
                ty = self.curr_func.typemap[expr.id]
                if hasattr(ty, 'ndim'): num_dims = ty.ndim
                else: num_dims = 0
        elif isinstance(expr, ast.UnaryOp):
            n, d = self.verify_and_collect_cs_expr(expr.operand, vars_ro, cs_exprs)
            if n >= 0:
                ope_nest = n + 1
            num_dims = d
        else:
            valid = False
            calc_max = True
            calc_matmult = False
            arg1_minus1 = False
            ch = []
            if isinstance(expr, ast.BinOp):
                valid = True
                ch.append(expr.left)
                ch.append(expr.right)
            elif isinstance(expr, ast.BoolOp):
                valid = True
                ch.extend(expr.values)
            elif isinstance(expr, ast.Compare):
                valid = True
                ch.append(expr.left)
                ch.extend(expr.comparators)
            elif isinstance(expr, ast.Call):
                pure = arrayopt.is_call_to(expr, defuse.pure_funcs)
                valid = pure and not top
                calc_max = False
                if pure:
                    d = defuse.pure_funcs[expr.func.id]
                    if isinstance(d, int):
                        num_dims = d
                    elif d == 'arg1_len':
                        if isinstance(expr.args[0], list): num_dims = len(expr.args[0])
                        else: num_dims = 1
                    elif d == 'arg_max_dim':
                        calc_max = True
                    elif d == 'red_sum':
                        if len(expr.args) == 1: num_dims = 0
                        else: arg1_minus1 = True
                    elif d == 'matmult':
                        calc_matmult = True
                ch.extend(expr.args)
            elif isinstance(expr, ast.Subscript) and isinstance(expr.slice, ast.Index):
                valid = True
                calc_max = False
                index = expr.slice
                if isinstance(expr.value, ast.Name) and expr.value.id in self.curr_func.typemap:
                    ty = self.curr_func.typemap[expr.value.id]
                    ln = len(index.elts) if isinstance(index, ast.Tuple) else 1
                    if hasattr(ty, 'ndim') and ty.ndim >= ln:
                        num_dims = ty.ndim - ln
                ch.append(expr.value)
                if isinstance(index, ast.Tuple): ch.extend(index.elts)
                else: ch.append(index)

            if ch:
                num = len(ch)
                n = list(range(num))
                d = list(range(num))
                for i in range(num):
                    n[i], d[i] = self.verify_and_collect_cs_expr(ch[i], vars_ro, cs_exprs)

                if valid and min(n) >= 0:
                    ope_nest = sum(n) + 1
                else:
                    for i in range(num):
                        self.check_and_update_cs_expr(ch[i], n[i], d[i], cs_exprs)

                if calc_max and min(d) >= 0:
                    num_dims = max(d)
                elif arg1_minus1 and d[0] >= 1:
                    num_dims = d[0] - 1
                    if num_dims == 0: num_dims = 1
                elif calc_matmult and d[0] >= 1 and d[1] >= 1:
                    num_dims = d[0] + d[1] - 2
                    # 2+2: matmat, 1+2: vectmat, 2+1: matvect, 1+1: innerprod
            elif valid:
                ope_nest = 0
                num_dims = 0

        return ope_nest, num_dims

    def check_and_update_cs_expr(self, expr: ast.expr,
                                 ope_nest: int, num_dims: int, cs_exprs: dict):
        if ope_nest <= 0:
            return

        ty = None
        if hasattr(expr, 'type'):
            ty = expr.type
        elif isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
            dummy = [mytypes.float64_ndarray, mytypes.float64_ndarray]
            ty = libfuncs.get_type(expr.func.id, 'pydd', dummy)

        if num_dims == -1 or not ty:
            if verbose_level >= 2:
                print('[Verbose] Invalid due to dimension (%s) or type (%s).' %(num_dims, ty))
                if verbose_level >= 4: print(dumpfunc(expr))
            return

        if isinstance(ty, mytypes.NpArray):
            assert num_dims >= 1
            ty = mytypes.NpArray(ty.etype, num_dims)
        cs_exprs[expr] = arrayopt.new_var(ty, self.curr_func)

        if verbose_level >= 2:
            print('[Verbose] Invariant expresson (nest-level = %s) found.' %ope_nest)
            if verbose_level >= 3:
                print('[Verbose] type =', ty, 'with ndims =', num_dims)
                if verbose_level >= 4: print(dumpfunc(expr))

    def collect_common_sub_expressions(self, loop_node, invstmt_nodes: list):
        cs_exprs = {}
        vars_ro = (loop_node.vars_use - loop_node.vars_def - loop_node.vars_cond_def
                   - loop_node.vars_may_def - loop_node.vars_em_def)
        for n in invstmt_nodes:
            vars_ro |= n.vars_def
        if verbose_level >= 2:
            print('[Verbose] Search invariant expressions in:', loop_node.kind, loop_node.level)
            if verbose_level >= 3:
                print('[Verbose] Read-only vars:', vars_ro)

        node = loop_node.child
        while node:
            if node not in invstmt_nodes:
                astn = None
                if node.is_assign() or node.kind is self.LevelTreeNode.Kind.CALL:
                    assert hasattr(node.ast_node, 'value')
                    astn = node.ast_node.value
                if astn:
                    b4size = len(cs_exprs)
                    n, d = self.verify_and_collect_cs_expr(astn, vars_ro, cs_exprs, True)
                    self.check_and_update_cs_expr(astn, n, d, cs_exprs)
                    if len(cs_exprs) > b4size:
                        node.has_cse = True

            node = node.next

        return cs_exprs

    def replace_cse_by_var(self, expr, cs_exprs: dict):
        if isinstance(expr, ast.stmt) and expr.value in cs_exprs:
            var = cs_exprs[expr.value]
            expr.value = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
        elif isinstance(expr, ast.UnaryOp) and expr.operand in cs_exprs:
            var = cs_exprs[expr.operand]
            expr.operand = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
        elif isinstance(expr, ast.BinOp):
            if expr.left in cs_exprs:
                var = cs_exprs[expr.left]
                expr.left = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
            if expr.right in cs_exprs:
                var = cs_exprs[expr.right]
                expr.right = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
        elif isinstance(expr, ast.BoolOp):
            n = len(expr.values)
            for i in range(n):
                if expr.values[i] in cs_exprs:
                    var = cs_exprs[expr.values[i]]
                    expr.values[i] = arrayopt.new_name(var, ast.Load,
                                                       self.curr_func.typemap[var])
        elif isinstance(expr, ast.Compare):
            if expr.left in cs_exprs:
                var = cs_exprs[expr.left]
                expr.left = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
            n = len(expr.comparators)
            for i in range(n):
                if expr.comparators[i] in cs_exprs:
                    var = cs_exprs[expr.comparators[i]]
                    expr.comparators[i] = arrayopt.new_name(var, ast.Load,
                                                            self.curr_func.typemap[var])
        elif isinstance(expr, ast.Call):
            n = len(expr.args)
            for i in range(n):
                if expr.args[i] in cs_exprs:
                    var = cs_exprs[expr.args[i]]
                    expr.args[i] = arrayopt.new_name(var, ast.Load,
                                                     self.curr_func.typemap[var])
        elif isinstance(expr, ast.Subscript) and isinstance(expr.slice, ast.Index):
            if expr.value in cs_exprs:
                var = cs_exprs[expr.value]
                expr.value = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])
            index = expr.slice
            if isinstance(index, ast.Tuple):
                n = len(index.elts)
                for i in range(n):
                    if index.elts[i] in cs_exprs:
                        var = cs_exprs[index.elts[i]]
                        index.elts[i] = arrayopt.new_name(var, ast.Load,
                                                          self.curr_func.typemap[var])
            elif index in cs_exprs:
                var = cs_exprs[index]
                expr.slice = arrayopt.new_name(var, ast.Load, self.curr_func.typemap[var])

        for node in ast.iter_child_nodes(expr):
            self.replace_cse_by_var(node, cs_exprs)

    def licm_codegen(self, loop_node, loop_node0, invstmt_nodes: list, cs_exprs: dict):
        assert tuple(self.status) == loop_node.level and self.level_tree_current is loop_node
        assert loop_node.prev and not loop_node.parent
        self.level_tree_current = loop_node.prev
        self.status[-1] -= 1

        children = []
        ch = loop_node.child
        while ch:
            if ch not in invstmt_nodes: children.append(ch)
            ch = ch.next

        stmts = []
        for inv in invstmt_nodes:
            self.status[-1] += 1
            inv.level = tuple(self.status)
            self.level_tree_current.next = inv
            inv.prev = self.level_tree_current
            inv.parent = None
            inv.next = None
            inv.child = None
            self.level_tree_current = inv
            stmts.append(inv.ast_node)

        for inv in cs_exprs:
            tar = cs_exprs[inv]
            ty = self.curr_func.typemap[tar]
            stmt = arrayopt.new_assign(tar, inv, ty)
            self.visit_Assign(stmt)
            stmts.append(stmt)

        self.status[-1] += 1
        loop_node0.level = tuple(self.status)
        self.level_tree_current.next = loop_node0
        loop_node0.prev = self.level_tree_current
        assert not loop_node0.parent and not loop_node0.next
        self.level_tree_current = loop_node0

        body = []
        for ch in children:
            if self.is_loop_init(ch):
                self.status.append(0)
                ch.level = tuple(self.status)
                self.level_tree_current.child = ch
                ch.parent = self.level_tree_current
                assert not ch.prev and not ch.child
                ch.next = None
                self.level_tree_current = ch
            else:
                stmt = ch.ast_node
                if hasattr(ch, 'has_cse') and ch.has_cse:
                    self.replace_cse_by_var(stmt, cs_exprs)
                    if ch.kind is self.LevelTreeNode.Kind.ASSIGN:
                        self.visit_Assign(stmt)
                    elif ch.kind is self.LevelTreeNode.Kind.AUG_ASSIGN:
                        self.visit_AugAssign(stmt)
                    elif ch.kind is self.LevelTreeNode.Kind.ANN_ASSIGN:
                        self.visit_AnnAssign(stmt)
                    else:
                        self.visit_Call(stmt, True)
                else:
                    self.status[-1] += 1
                    ch.level = tuple(self.status)
                    self.level_tree_current.next = ch
                    ch.prev = self.level_tree_current
                    assert not ch.parent
                    ch.update_child_level()
                    ch.next = None
                    self.level_tree_current = ch
                if ch.kind is not self.LevelTreeNode.Kind.ELSE:
                    body.append(stmt)

        self.collect_child_def_use(loop_node0)
        loop_node0.ast_node.body = body
        stmts.append(loop_node0.ast_node)
        return stmts


############################################################################################

    def visit_FunctionDef(self, N: ast.FunctionDef):
        if verbose_level >= 2: print('[Verbose] LICM ast for function:', N.name)
        defuse.DefUseAnalysis.visit_FunctionDef(self, N)

    def visit_body(self, stmts: list):
        new_stmts = []
        transformed = False
        for stmt in stmts:
            ss = []
            if isinstance(stmt, ast.For):
                ss = self.visit_For(stmt)
            elif isinstance(stmt, ast.While):
                ss = self.visit_While(stmt)
            if ss:
                if len(ss) >= 2:
                    transformed = True
                new_stmts.extend(ss)
            else:
                self.visit_body_core(stmt)
                new_stmts.append(stmt)

        if transformed:
            stmts.clear()
            stmts.extend(new_stmts)

    def visit_For(self, N: ast.For):
        for_node = self.visit_For_head(N)
        for_copy = for_node.copy()

        self.visit_body(N.body)
        self.collect_child_def_use(for_node)

        invstmt_nodes = self.collect_invariant_statements(for_node)
        cs_exprs = self.collect_common_sub_expressions(for_node, invstmt_nodes)
        stmts = self.licm_codegen(for_node, for_copy, invstmt_nodes, cs_exprs)

        assert not N.orelse

        return stmts

    def visit_While(self, N: ast.While):
        while_node = self.visit_While_head(N)
        while_copy = while_node.copy()

        self.visit_body(N.body)
        self.collect_child_def_use(while_node)

        invstmt_nodes = self.collect_invariant_statements(while_node)
        cs_exprs = self.collect_common_sub_expressions(while_node, invstmt_nodes)
        stmts = self.licm_codegen(while_node, while_copy, invstmt_nodes, cs_exprs)

        assert not N.orelse

        return stmts
