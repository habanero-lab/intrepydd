from enum import Enum
import ast
from . import glb
from . import libfuncs
from . import mytypes

'''
Sparse and dense array optimizations.

Todo:
 - For sparse, consider 1-D dense matrix with broadcast
  -- sparse_dim: Verify_expression and scalarize_array_op
  -- Valid.MATMULT: Handle matmat_multiply
  -- Valid.TRANSPOSE: Handle innerprod, vectmat, matvect
 - Type system support
  -- dense_opt_recurse: Determine type in addition to current dim support
   --- Use found type for pre_stmts, e.g., pre_stmts[expr] = FOUND_TYPE
  -- eval_node_dense: Use above type for newly created tar_var
 - Standardize options, print (verbose and warning), and assert
'''

### Options ###
# 0: Nothing, 1: Warning, 2: Debug (light), 3: Debug (moderate), 4: Debug (heavy)
verbose_level = 1
dumpfunc = ast.dump
sparse_par = False
dense_par = False
rt_shape_check = True
ew_prestmt = False
test_pldi_algo = False

### Globals ###
ew_funcs = {
    # Map to UnaryOp
    'minus': ast.USub, 'not': ast.Not,
    # Map to BinOp
    'add': ast.Add, 'sub': ast.Sub, 'mul': ast.Mult, 'div': ast.Div,
    'plus_eq': ast.Add, 'minus_eq': ast.Sub,
    # Map to Compare
    'eq': ast.Eq, 'neq': ast.NotEq, 'lt': ast.Lt, 'gt': ast.Gt, 'le': ast.LtE, 'ge': ast.GtE,
    # Map to BoolOp
    'logical_and': ast.And, 'logical_or': ast.Or,
    # Map to no-op
    'set_row': None,
    # Kept as Call (with scalarization)
    'abs': 1, 'isnan': 1, 'isinf': 1, 'sqrt': 1, 'exp': 1,
    'cos': 1, 'sin': 1, 'tan': 1, 'acos': 1, 'asin': 1, 'atan': 1,
    'pow': 2, 'log': 2, 'maximum': 2, 'logical_xor': 2,
}

sparse_dim = 2
set_row_val_idx = 2

### Utilities ###
new_var_count = 0
new_var_base = '__var'
def new_var(ty: mytypes.MyType, func: ast.FunctionDef):
    found = True
    while found:
        global new_var_count, new_var_base
        new_var_count += 1
        name = new_var_base + str(new_var_count)
        found = name in func.typemap
    func.typemap[name] = ty
    return name

def new_name(var: str, ctx: ast.expr_context, ty1 = None, ty2 = None):
    ret = ast.Name(var, ctx())
    if ty1: ret.type = ty1
    elif ty2: ret.type = ty2
    else: ret.type = None
    return ret
    
def new_assign(var: str, expr: ast.expr, ty = None):
    tar = new_name(var, ast.Store, ty, (expr.type if hasattr(expr, 'type') else None))
    ret = ast.Assign(targets = [tar], value = expr)
    return ret

def new_aug_assign(var: str, op:ast.operator, expr: ast.expr, ty = None):
    tar = new_name(var, ast.Store, ty, (expr.type if hasattr(expr, 'type') else None))
    ret = ast.AugAssign(target = tar, op = op, value = expr)
    return ret

def new_subscript_elem(index):
    if isinstance(index, str):
        return ast.Name(index, ast.Load())
    else:
        return index

def new_subscript(array:str, index, ty = None):
    if isinstance(index, list):
        idxArg = ast.Tuple(list(map(lambda x: new_subscript_elem(x), index)), ast.Load())
    else:
        idxArg = new_subscript_elem(index)
    ret = ast.Subscript(ast.Name(array, ast.Load()), ast.Index(idxArg), ast.Load())
    ret.type = ty
    return ret

def new_call(func: str, args: list, ty = None):
    ret = ast.Call(func = ast.Name(func, ast.Load()), args = args, keywords = [])
    ret.type = ty
    return ret

def contains_var(expr: ast.expr, var: str):
    if isinstance(expr, ast.Name) and expr.id is var:
        return True
    for node in ast.iter_child_nodes(expr):
        if contains_var(node, var):
            return True
    return False

def is_assign_stmt(stmt: ast.stmt):
    return (isinstance(stmt, ast.Assign) or isinstance(stmt, ast.AnnAssign)
            or isinstance(stmt, ast.AugAssign)
            or is_call_to(stmt, 'plus_eq') or is_call_to(stmt, 'minus_eq')
            or is_call_to(stmt, 'set_row'))

def is_call_to(N: ast.expr, name):
    if isinstance(N, ast.Call) and isinstance(N.func, ast.Name):
        fid = N.func.id
    elif (isinstance(N, ast.Expr) and isinstance(N.value, ast.Call)
          and isinstance(N.value.func, ast.Name)):
        fid = N.value.func.id
    else:
        return False

    if isinstance(name, list) or isinstance(name, dict) or isinstance(name, set):
        return fid in name
    else:
        return fid == name

def is_var_with_type(N: ast.expr, func: ast.FunctionDef, type_class, ndim = -1):
    if isinstance(N, ast.Name) and N.id in func.typemap:
        ty = func.typemap[N.id]
        # print(ty, 'vs', (N.type if hasattr(N, 'type') else ast.dump(N))) # TEST
        return isinstance(ty, type_class) and (ndim == -1 or ty.ndim == ndim)
    return False

def is_scalar_var(N: ast.expr, func: ast.FunctionDef):
    if isinstance(N, ast.Num):
        return True
    if isinstance(N, ast.Name) and N.id in func.typemap:
        ty = func.typemap[N.id]
        # print(ty, 'vs', (N.type if hasattr(N, 'type') else ast.dump(N))) # TEST
        return (isinstance(ty, mytypes.IntType) or isinstance(ty, mytypes.FloatType)
                or isinstance(ty, mytypes.BoolType))
    if (isinstance(N, ast.Subscript) and isinstance(N.slice, ast.Index)
        and isinstance(N.value, ast.Name) and N.value.id in func.typemap):
        ty = func.typemap[N.value.id]
        if hasattr(ty, 'ndim'):
            ln = len(N.slice.elts) if isinstance(N.slice, ast.Tuple) else 1
            return ty.ndim == ln
    return False

def is_scalar_expr(N: ast.expr, func: ast.FunctionDef):
    # Todo: Handle BoolOp and Compare
    if isinstance(N, ast.UnaryOp):
        return is_scalar_expr(N.operand, func)
    elif isinstance(N, ast.BinOp):
        return is_scalar_expr(N.left, func) and is_scalar_expr(N.right, func)
    else:
        return is_scalar_var(N, func)

def is_array_slice(expr: ast.expr, func: ast.FunctionDef, is_assign = False):
    if is_assign:
        call_check = is_call_to(expr, 'set_row')
        expected = 3 # Todo: Can change due to set_row signature
    else:
        call_check = is_call_to(expr, 'get_row')
        expected = 2 # Todo: Can change due to get_row signature
    if call_check:
        assert len(expr.args) == expected
        if (is_var_with_type(expr.args[0], func, mytypes.NpArray)
            and (is_scalar_var(expr.args[1], func) or is_scalar_expr(expr.args[1], func))):
            return True
    return False

def get_array_slice_target(expr: ast.expr):
    return expr.args[0]

def get_array_slice_index(expr: ast.expr):
    return expr.args[1]

def collect_arrays(expr: ast.expr, func: ast.FunctionDef, arrays = None):
    if arrays is None:
        arrays = []
    if is_var_with_type(expr, func, mytypes.NpArray):
        arrays.append(expr.id)
    if not is_call_to(expr, 'get_row'): # Todo: Handle array slice
        for node in ast.iter_child_nodes(expr):
            collect_arrays(node, func, arrays)
    return arrays

def get_ret_etype(N: ast.expr):
    if not isinstance(N, ast.Call) or not isinstance(N.func, ast.Name):
        return None
    dummy = [mytypes.float64_ndarray, mytypes.float64_ndarray]
    ty = libfuncs.get_type(N.func.id, 'pydd', dummy)
    # print(ty, 'vs', (N.type if hasattr(N, 'type') else ast.dump(N))) # TEST
    assert ty and hasattr(ty, 'etype')
    return ty.etype


############################################################################################

class ArrayOptimization(ast.NodeVisitor):

    class OptInfo:
        def __init__(self, target_call: ast.Call, full_expr: bool,
                     src_var: str, tar_var: str, pre_stmts: dict,
                     src_slice = None, tar_slice = None):
            self.target_call = target_call  # call to outermost function (e.g., spm_mul)
            self.full_expr = full_expr      # if original stmt is "tar_var = target_call"
            self.src_var = src_var          # sparse/dense matrix name to use
            self.tar_var = tar_var          # sparse/dense matrix name to store
            self.pre_stmts = pre_stmts      # key: ast.Call, value: temp var (type/name)
            self.src_slice = src_slice      # Index if src is array slice
            self.tar_slice = tar_slice      # Index if tar is array slice

        def show(self):
            print('[Verbose] dump OptInfo:')
            if self.target_call: print(' - target_call:', dumpfunc(self.target_call))
            print(' - full_expr:', self.full_expr)
            if self.src_var: print(' - src_var:', self.src_var)
            if self.tar_var: print(' - tar_var:', self.tar_var)
            if self.src_slice: print(' - src_slice:', dumpfunc(self.src_slice))
            if self.tar_slice: print(' - tar_slice:', dumpfunc(self.tar_slice))
            for expr in self.pre_stmts: print(' - pre_stmt:', dumpfunc(expr))

    class Valid(Enum):
        INVALID = -1
        SCALAR = 0
        S_MAT = 1
        D_MAT = 2
        S_MUL = 3
        D_ELEM = 4
        MATMULT = 5
        TRANSPOSE = 6

    def __init__(self):
        self.curr_func = None
        self.enable_sparse = False
        self.enable_dense = False

    def verify_expression(self, expr: ast.expr, src_spm: str, pre_stmts: dict, set_pre = True):
        res = self.Valid.INVALID

        if is_scalar_var(expr, self.curr_func):
            res = self.Valid.SCALAR
        elif is_scalar_expr(expr, self.curr_func):
            if set_pre:
                pre_stmts[expr] = expr.type if hasattr(expr, 'type') else mytypes.float64
            res = self.Valid.SCALAR
        elif isinstance(expr, ast.Name) and expr.id == src_spm:
            res = self.Valid.S_MAT
        elif is_var_with_type(expr, self.curr_func, mytypes.NpArray, sparse_dim):
            res = self.Valid.D_MAT
        elif is_call_to(expr, 'transpose'):
            if set_pre:
                pre_stmts[expr] = mytypes.float64_2darray
                res = self.Valid.D_MAT
            else:
                res = self.Valid.TRANSPOSE
        elif is_call_to(expr, 'matmult'):
            v = list(map(lambda x: self.verify_expression(x, src_spm, pre_stmts, False), expr.args))
            if ((v[0] == self.Valid.D_MAT or v[0] == self.Valid.D_ELEM
                 or v[0] == self.Valid.MATMULT or v[0] == self.Valid.TRANSPOSE)
                and (v[1] == self.Valid.D_MAT or v[1] == self.Valid.D_ELEM
                     or v[1] == self.Valid.MATMULT or v[1] == self.Valid.TRANSPOSE)):
                if set_pre:
                    if v[0] != self.Valid.D_MAT: pre_stmts[expr.args[0]] = mytypes.float64_2darray
                    if v[1] != self.Valid.D_MAT: pre_stmts[expr.args[1]] = mytypes.float64_2darray
                res = self.Valid.MATMULT
        elif isinstance(expr, ast.Call):
            v = list(map(lambda x: self.verify_expression(x, src_spm, pre_stmts), expr.args))
            if (is_call_to(expr, 'spm_mul')
                and (((v[0] == self.Valid.S_MAT or v[0] == self.Valid.S_MUL)
                      and v[1] != self.Valid.INVALID)
                     or ((v[1] == self.Valid.S_MAT or v[1] == self.Valid.S_MUL)
                         and v[0] != self.Valid.INVALID))):
                res = self.Valid.S_MUL
            elif is_call_to(expr, ew_funcs):
                if ((len(v) == 1
                     and (v[0] == self.Valid.D_MAT
                          or v[0] == self.Valid.D_ELEM or v[0] == self.Valid.MATMULT))
                    or (len(v) == 2
                        and (v[0] == self.Valid.SCALAR or v[0] == self.Valid.D_MAT
                             or v[0] == self.Valid.D_ELEM or v[0] == self.Valid.MATMULT)
                        and (v[1] == self.Valid.SCALAR or v[1] == self.Valid.D_MAT
                             or v[1] == self.Valid.D_ELEM or v[1] == self.Valid.MATMULT)
                        and (v[0] != self.Valid.SCALAR or v[1] != self.Valid.SCALAR))):
                    res = self.Valid.D_ELEM

        return res

    def contains_func_call(self, expr: ast.expr):
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
            return True
        for node in ast.iter_child_nodes(expr):
            if self.contains_func_call(node):
                return True
        return False

    def verify_and_collect_info(self, stmt: ast.stmt, target_call: ast.Call):
        if not any(list(map(lambda x: self.contains_func_call(x), target_call.args))):
            if verbose_level >= 2: print('[Verbose] No function to fuse for spm_mul.')
            return None

        src_spm = None
        arg0 = target_call.args[0]
        while arg0:
            if is_call_to(arg0, 'spm_mul'):
                arg0 = arg0.args[0]
            else:
                if is_var_with_type(arg0, self.curr_func, mytypes.SparseMat):
                    src_spm = arg0.id
                arg0 = None
        if not src_spm:
            if verbose_level >= 2: print('[Verbose] No src_spm found.')
            return None

        pre_stmts = {}
        if self.verify_expression(target_call, src_spm, pre_stmts) != self.Valid.S_MUL:
            if verbose_level >= 2: print('[Verbose] Invalid expression.')
            return None

        if ((isinstance(stmt, ast.Assign) or isinstance(stmt, ast.AnnAssign))
            and target_call is stmt.value and stmt.targets[0].id is not src_spm):
            assert len(stmt.targets) == 1
            assert is_var_with_type(stmt.targets[0], self.curr_func, mytypes.SparseMat)
            tar_spm = stmt.targets[0].id
            full_expr = True
        else:
            ty = self.curr_func.typemap[src_spm]
            tar_spm = new_var(ty, self.curr_func)
            full_expr = False

        opt_info = self.OptInfo(target_call, full_expr, src_spm, tar_spm, pre_stmts)
        if verbose_level >= 2:
            print('[Verbose] spm_mul with elem-wise operations found.')
            if verbose_level >= 3:
                opt_info.show()

        return opt_info

    def sparse_opt_analysis(self, stmt: ast.stmt, expr: ast.expr, opt_list: list):
        if is_call_to(expr, 'spm_mul'):
            opt_info = self.verify_and_collect_info(stmt, expr)
            if opt_info:
                opt_list.append(opt_info)
            else:
                for arg in expr.args:
                    self.sparse_opt_analysis(stmt, arg, opt_list)
        else:
            for node in ast.iter_child_nodes(expr):
                self.sparse_opt_analysis(stmt, node, opt_list)

    def find_reusable_var(self, opt_list: list, opt_info: OptInfo, pre_stmt: ast.expr):
        # Todo: return var name if same expression exists
        return None

    def replace_func_arg_by_var(self, expr, target_expr: ast.expr, var: str):
        if isinstance(expr, ast.stmt) and expr.value is target_expr:
            expr.value = ast.Name(var, ast.Load())
            
        if isinstance(expr, ast.Call):
            for i in range(len(expr.args)):
                if expr.args[i] is target_expr:
                    expr.args[i] = ast.Name(var, ast.Load())

        for node in ast.iter_child_nodes(expr):
            self.replace_func_arg_by_var(node, target_expr, var)

    def assign_new_vars(self, opt_list: list):
        for opt_info in opt_list:
            for expr in opt_info.pre_stmts:
                var = self.find_reusable_var(opt_list, opt_info, expr)
                if not var:
                    ty = opt_info.pre_stmts[expr]
                    var = new_var(ty, self.curr_func)
                    opt_info.pre_stmts[expr] = var
                self.replace_func_arg_by_var(opt_info.target_call, expr, var)

    def update_pre_stmts(self, start: int, opt_list: list, target_expr: ast.expr, var: str):
        for i in range(start, len(opt_list)):
            for expr in opt_list[i].pre_stmts:
                self.replace_func_arg_by_var(expr, target_expr, var)

    def generate_init_spm(self, src_spm: str, tar_spm: str):
        shape0 = new_call('shape', [ast.Name(src_spm, ast.Load()), ast.Num(0)])
        shape1 = new_call('shape', [ast.Name(src_spm, ast.Load()), ast.Num(1)])
        return new_assign(tar_spm, new_call('empty_spm', [shape0, shape1]))

    def generate_for(self, idx: str, func: str, arg0: str, arg1, body: list, is_pfor = False):
        arg1Ast = ast.Num(arg1) if isinstance(arg1, int) else ast.Name(arg1, ast.Load())
        rangeCall = new_call('range', [new_call(func, [ast.Name(arg0, ast.Load()), arg1Ast])])
        ret = ast.For(ast.Name(idx, ast.Store()), rangeCall, body, [])
        ret.is_pfor = is_pfor
        if is_pfor: self.curr_func.has_pfor = True

        return ret

    def scalarize_matmult(self, args: list, row: str, col: str, stmts: list):
        assert len(args) == 2
        assert is_var_with_type(args[0], self.curr_func, mytypes.NpArray, sparse_dim)
        assert is_var_with_type(args[1], self.curr_func, mytypes.NpArray, sparse_dim)

        res = new_var(mytypes.float64, self.curr_func)
        stmts.append(new_assign(res, ast.Num(0.0)))

        idx = new_var(mytypes.int32, self.curr_func)
        left = new_subscript(args[0].id, [row, idx])
        right = new_subscript(args[1].id, [idx, col])
        aug = new_aug_assign(res, ast.Add(), ast.BinOp(left, ast.Mult(), right))

        for_stmt = self.generate_for(idx, 'shape', args[0].id, 1, [aug])
        stmts.append(for_stmt)
        return ast.Name(res, ast.Load())

    def scalarize_array_op(self, expr: ast.expr, src_spm: str,
                           row: str, col: str, value: str, stmts: list):
        if is_scalar_var(expr, self.curr_func):
            return expr
        elif isinstance(expr, ast.Name) and expr.id == src_spm:
            return ast.Name(value, ast.Load())
        elif is_var_with_type(expr, self.curr_func, mytypes.NpArray, sparse_dim):
            return new_subscript(expr.id, [row, col])
        elif is_call_to(expr, 'matmult'):
            return self.scalarize_matmult(expr.args, row, col, stmts)
        elif is_call_to(expr, 'spm_mul'):
            left = self.scalarize_array_op(expr.args[0], src_spm, row, col, value, stmts)
            right = self.scalarize_array_op(expr.args[1], src_spm, row, col, value, stmts)
            assert left and right
            return ast.BinOp(left, ast.Mult(), right)
        elif is_call_to(expr, ew_funcs):
            ewf = ew_funcs[expr.func.id]
            if isinstance(ewf, int):
                assert len(expr.args) == ewf
                for i in range(ewf):
                    expr.args[i] = self.scalarize_array_op(expr.args[i], src_spm,
                                                           row, col, value, stmts)
                return expr
            else:
                op = ewf()
                if len(expr.args) == 1:
                    operand = self.scalarize_array_op(expr.args[0], src_spm, row, col, value, stmts)
                    assert operand and isinstance(op, ast.unaryop)
                    return ast.UnaryOp(op, operand)
                elif len(expr.args) == 2:
                    left = self.scalarize_array_op(expr.args[0], src_spm, row, col, value, stmts)
                    right = self.scalarize_array_op(expr.args[1], src_spm, row, col, value, stmts)
                    assert left and right
                    if isinstance(op, ast.operator): return ast.BinOp(left, op, right)
                    elif isinstance(op, ast.cmpop): return ast.Compare(left, [op], [right])
                    elif isinstance(op, ast.boolop): return ast.BoolOp(op, [left, right])
        return None

    def generate_body(self, target_call: ast.expr, src_spm: str, tar_spm: str,
                      row: str, col: str, cidx: str, value: str):
        col_def = new_assign(col, new_call('getcol', [ast.Name(src_spm, ast.Load()),
                                                      ast.Name(row, ast.Load()),
                                                      ast.Name(cidx, ast.Load())]))
        val_def = new_assign(value, new_call('getval', [ast.Name(src_spm, ast.Load()),
                                                          ast.Name(row, ast.Load()),
                                                          ast.Name(cidx, ast.Load())]))
        stmts = [col_def, val_def]

        body_expr = self.scalarize_array_op(target_call, src_spm, row, col, value, stmts)
        assert body_expr
        stmts.append(ast.Expr(new_call('spm_set_item_unsafe',
                                       [ast.Name(tar_spm, ast.Load()), body_expr,
                                        ast.Name(row, ast.Load()), ast.Name(col, ast.Load())])))
        return stmts

    def sparse_opt_codegen(self, opt_info: OptInfo):
        stmts = []
        for expr in opt_info.pre_stmts:
            var = opt_info.pre_stmts[expr]
            if var:
                stmts.append(new_assign(var, expr))

        row = new_var(mytypes.int32, self.curr_func)
        cidx = new_var(mytypes.int32, self.curr_func)
        col = new_var(mytypes.int32, self.curr_func)
        value = new_var(mytypes.float64, self.curr_func)

        init = self.generate_init_spm(opt_info.src_var, opt_info.tar_var)
        stmts.append(init)

        body = self.generate_body(opt_info.target_call, opt_info.src_var, opt_info.tar_var,
                                  row, col, cidx, value)
        for_inner = self.generate_for(cidx, 'getnnz', opt_info.src_var, row, body)
        for_outer = self.generate_for(row, 'shape', opt_info.src_var, 0, [for_inner], sparse_par)
        stmts.append(for_outer)
        if verbose_level >= 4:
            print('[Verbose] Generated code:')
            for stmt in stmts: print(dumpfunc(stmt))

        return stmts


    def is_fusable_elemwise(self, expr: ast.expr, dims: list, ew_prs: list):
        global set_row_val_idx
        if is_call_to(expr, 'set_row'):
            return is_array_slice(expr, self.curr_func, True) and dims[set_row_val_idx] != -1

        args = expr.args
        n = len(args)
        assert n == len(dims)

        if min(dims) == -1:
            return False

        for i in range(n):
            if dims[i] < max(dims) and is_call_to(args[i], ew_funcs):
                if not ew_prestmt:
                    return False
                ew_prs.append(i)

        return True

    def dense_opt_recurse(self, stmt: ast.stmt, expr: ast.expr, opt_list: list):
        global set_row_val_idx

        dim = -1
        pre_stmts = {}
        if is_scalar_var(expr, self.curr_func):
            dim = 0
        elif is_scalar_expr(expr, self.curr_func):
            pre_stmts[expr] = expr.type if hasattr(expr, 'type') else mytypes.float64
            dim = 0
        elif is_var_with_type(expr, self.curr_func, mytypes.NpArray):
            dim = self.curr_func.typemap[expr.id].ndim
        elif is_array_slice(expr, self.curr_func):
            tar_dim = self.curr_func.typemap[get_array_slice_target(expr).id].ndim
            if tar_dim > 0:
                dim = tar_dim - 1
        elif isinstance(expr, ast.Call):
            n = len(expr.args)
            dims = list(range(n))
            pres = list(range(n))
            for i in range(n):
                dims[i], pres[i] = self.dense_opt_recurse(stmt, expr.args[i], opt_list)

            ew_prs = []
            if is_call_to(expr, ew_funcs) and self.is_fusable_elemwise(expr, dims, ew_prs):
                s = set_row_val_idx if is_call_to(expr, 'set_row') else 0
                dim = max(dims[s:])
                for i in range(s, n):
                    if i in ew_prs:
                        if not self.eval_node_dense(stmt, expr.args[i], dims[i], pres[i], opt_list):
                            assert dims[i] >= 1 and isinstance(expr, ast.Call)
                            etype = get_ret_etype(expr)
                            pre_stmts[expr.args[i]] = mytypes.NpArray(etype, dims[i])
                    else:
                        pre_stmts.update(pres[i])
            else:
                for i in range(n):
                    self.eval_node_dense(stmt, expr.args[i], dims[i], pres[i], opt_list)

                if is_call_to(expr, 'transpose'):
                    if verbose_level >= 1 and dims[0] != 2:
                        print('[Warning] transpose assumes a 2-D array as argument.')
                    dim = 2
                elif is_call_to(expr, 'spmv'):
                    if verbose_level >= 1 and (dims[0] != 1 or dims[1] != 1):
                        print('[Warning] spmv assumes 2-D/1-D arrays as arguments.')
                    dim = 1
                elif is_call_to(expr, 'spmm_dense'):
                    if verbose_level >= 1 and (dims[0] != 2 or dims[1] != 2):
                        print('[Warning] spmm_dense assumes 2-D arrays as arguments.')
                    dim = 1
                elif is_call_to(expr, 'matmat_multiply'):
                    if verbose_level >= 1 and (dims[0] != 2 or dims[1] != 2):
                        print('[Warning] matmat_multiply assumes 2-D arrays as arguments.')
                    dim = 2
                elif is_call_to(expr, 'vectmat_multiply'):
                    if verbose_level >= 1 and (dims[0] != 1 or dims[1] != 2):
                        print('[Warning] vectmat_multiply assumes 1-D/2-D arrays as arguments.')
                    dim = 1
                elif is_call_to(expr, 'matvect_multiply'):
                    if verbose_level >= 1 and (dims[0] != 2 or dims[1] != 1):
                        print('[Warning] matvect_multiply assumes 2-D/1-D arrays as arguments.')
                    dim = 1
                elif is_call_to(expr, 'innerprod'):
                    if verbose_level >= 1 and (dims[0] != 1 or dims[1] != 1):
                        print('[Warning] innerprod assumes 1-D arrays as arguments.')
                    dim = 0
                elif is_call_to(expr, 'matmult') and dims[0] >= 1 and dims[1] >= 1:
                    assert dims[0] <= 2 and dims[1] <= 2
                    dim = dims[0] + dims[1] - 2
                    # 2+2: matmat, 1+2: vectmat, 2+1: matvect, 1+1: innerprod

                if dim == 0:
                    pre_stmts[expr] = mytypes.float64
                elif dim >= 1:
                    pre_stmts[expr] = mytypes.NpArray(mytypes.float64, dim)

        if test_pldi_algo: expr.ndims = dim  # Test for PLDI algo
        return dim, pre_stmts

    def get_src_var_without_slice(self, expr: ast.expr, pre_stmts: dict, type_class, ndim = -1):
        if isinstance(expr, ast.Name) and expr.id in self.curr_func.typemap:
            ty = self.curr_func.typemap[expr.id]
            if isinstance(ty, type_class) and (ndim == -1 or ty.ndim == ndim):
                return expr.id

        if not is_array_slice(expr, self.curr_func):
            for node in ast.iter_child_nodes(expr):
                if not node in pre_stmts:
                    var = self.get_src_var_without_slice(node, pre_stmts, type_class, ndim)
                    if var:
                        return var
        return None

    def get_src_var_with_slice(self, expr: ast.expr, pre_stmts: dict, type_class, ndim = -1):
        if is_array_slice(expr, self.curr_func):
            arr = get_array_slice_target(expr)
            if isinstance(arr, ast.Name) and arr.id in self.curr_func.typemap:
                ty = self.curr_func.typemap[arr.id]
                if isinstance(ty, type_class) and (ndim == -1 or ty.ndim - 1 == ndim):
                    return arr.id, get_array_slice_index(expr)

        for node in ast.iter_child_nodes(expr):
            if not node in pre_stmts:
                var, slice = self.get_src_var_with_slice(node, pre_stmts, type_class, ndim)
                if var and slice:
                    return var, slice
        return None, None

    def get_src_var(self, expr: ast.expr, pre_stmts: dict, type_class, ndim = -1):
        src_var = self.get_src_var_without_slice(expr, pre_stmts, type_class, ndim)
        if src_var:
            return src_var, None

        return self.get_src_var_with_slice(expr, pre_stmts, type_class, ndim)

    def is_nesting_fusable_funcs(self, args: list):
        for arg in args:
            if is_call_to(arg, ew_funcs) or is_array_slice(arg, self.curr_func):
                return True
        return False

    def get_target_var(self, stmt: ast.stmt, expr: ast.expr):
        tar_var, tar_slice = None, None
        if (isinstance(stmt, ast.Assign) or isinstance(stmt, ast.AnnAssign)) and expr is stmt.value:
            assert len(stmt.targets) == 1
            assert is_var_with_type(stmt.targets[0], self.curr_func, mytypes.NpArray)
            tar_var = stmt.targets[0].id
        elif is_call_to(stmt, 'plus_eq') or is_call_to(stmt, 'minus_eq'):
            arg = stmt.value.args[0]
            if is_array_slice(arg, self.curr_func):
                tar_var = get_array_slice_target(arg).id
                tar_slice = get_array_slice_index(arg)
            else:
                assert is_var_with_type(arg, self.curr_func, mytypes.NpArray)
                tar_var = arg.id
        elif is_call_to(stmt, 'set_row'):
            assert is_array_slice(expr, self.curr_func, True)
            tar_var = get_array_slice_target(expr).id
            tar_slice = get_array_slice_index(expr)

        return tar_var, tar_slice

    def eval_node_dense(self, stmt: ast.stmt, expr: ast.expr,
                        dim: int, pre_stmts: dict, opt_list: list):
        global set_row_val_idx

        if dim <= 0 or not is_call_to(expr, ew_funcs):
            return None
        elif not self.is_nesting_fusable_funcs(expr.args):
            if verbose_level >= 2: print('[Verbose] No nested dense elem-wise operations.')
            return None
        elif verbose_level >= 2: print('[Verbose] Nested dense elem-wise operations found.')

        if is_call_to(expr, 'set_row'):
            target_call = expr.args[set_row_val_idx]
        else:
            target_call = expr
        assert isinstance(target_call, ast.Call)

        src_var, src_slice = self.get_src_var(target_call, pre_stmts, mytypes.NpArray, dim)
        assert src_var

        tar_var, tar_slice = self.get_target_var(stmt, expr)
        if tar_var:
            ty0 = self.curr_func.typemap[tar_var]
            if ty0.ndim == -1:
                self.curr_func.typemap[tar_var] = mytypes.NpArray(ty0.etype, dim)
            else:
                ty0_ndim = ty0.ndim - 1 if tar_slice else ty0.ndim
                assert ty0_ndim == dim
            full_expr = True
        else:
            ty = mytypes.NpArray(get_ret_etype(target_call), dim)
            tar_var = new_var(ty, self.curr_func)
            full_expr = False

        opt_info = self.OptInfo(target_call, full_expr, src_var, tar_var, pre_stmts,
                                src_slice, tar_slice)
        opt_list.append(opt_info)
        if verbose_level >= 3:
            opt_info.show()

        return opt_info

    # Test for PLDI algo
    def to_split(self, N: ast.Call, A: ast.Call):
        ewf1 = is_call_to(N, ew_funcs) and N.ndims >= 1
        ewf2 = is_call_to(A, ew_funcs) and A.ndims >= 1
        return ewf1 != ewf2 or ewf1 and ewf2 and N.ndims != A.ndims

    def split_subtrees_for_fusion(self, N, trees: dict):
        if isinstance(N, ast.Assign) or isinstance(N, ast.AnnAssign):
            trees[N.targets[0].id] = N.value
            self.split_subtrees_for_fusion(N.value, trees)
        elif isinstance(N, ast.Call):
            for A in reversed(N.args):
                if isinstance(A, ast.Call):
                    if self.to_split(N, A):
                        v = new_var(mytypes.NpArray(mytypes.float64, A.ndims), self.curr_func)
                        trees[v] = A
                    self.split_subtrees_for_fusion(A, trees)

    def test_PLDI_dense_algo(self, stmt: ast.stmt):
        trees = {}
        self.split_subtrees_for_fusion(stmt, trees)
        print('Test for PLDI dense algo:')
        for v in trees:
            print(v+':', dumpfunc(trees[v]))

    def dense_opt_analysis(self, stmt: ast.stmt, expr: ast.expr, opt_list: list):
        dim, pre_stmts = self.dense_opt_recurse(stmt, expr, opt_list)
        self.eval_node_dense(stmt, expr, dim, pre_stmts, opt_list)

        if test_pldi_algo: self.test_PLDI_dense_algo(stmt)  # Test for PLDI algo

    def generate_compatibility_check(self, target_call: ast.Call):
        arrays = collect_arrays(target_call, self.curr_func)
        if len(arrays) >= 2:
            args0 = list(map(lambda x: ast.Name(x, ast.Load()), arrays))
            check = new_call('compatibility_check', args0)
            # args = ast.List(args0, ast.Load())
            # args.type = mytypes.ListType(mytypes.float64_ndarray)
            # check = new_call('compatibility_check', [args])
            return ast.Expr(check)
        return None

    def generate_init_dense(self, src_var: str, tar_var: str, iv: list):
        ss = list(map(lambda x: new_call('shape', [ast.Name(src_var, ast.Load()), ast.Num(x)]), iv))
        shapes = ast.List(ss, ast.Load())
        shapes.type = mytypes.int64_list

        et = self.curr_func.typemap[tar_var].etype
        if isinstance(et, mytypes.IntType):
            ef = 'int32' if et.width == 32 else 'int64'
        elif isinstance(et, mytypes.FloatType):
            ef = 'float32' if et.width == 32 else 'float64'
        elif isinstance(et, mytypes.BoolType):
            ef = 'boolean'
        else:
            assert False
        etype = new_call(ef, [])
        return new_assign(tar_var, new_call('empty', [shapes, etype]))

    def scalarize_dense_array_op(self, expr: ast.expr, indices: list):
        if is_scalar_var(expr, self.curr_func):
            return expr
        elif is_var_with_type(expr, self.curr_func, mytypes.NpArray):
            n = len(indices) - self.curr_func.typemap[expr.id].ndim
            return new_subscript(expr.id, indices[n:])
        elif is_array_slice(expr, self.curr_func):
            arr = get_array_slice_target(expr)
            idx = get_array_slice_index(expr)
            n = len(indices) - (self.curr_func.typemap[arr.id].ndim - 1)
            return new_subscript(arr.id, [idx] + indices[n:])
        elif is_call_to(expr, ew_funcs):
            ewf = ew_funcs[expr.func.id]
            if isinstance(ewf, int):
                nargs = len(expr.args)
                if verbose_level >= 1 and nargs != ewf:
                    print('[Waraning] Unmatched # args in for func:', expr.func.id)
                for i in range(nargs):
                    expr.args[i] = self.scalarize_dense_array_op(expr.args[i], indices)
                return expr
            else:
                op = ewf()
                if len(expr.args) == 1:
                    operand = self.scalarize_dense_array_op(expr.args[0], indices)
                    assert operand and isinstance(op, ast.unaryop)
                    return ast.UnaryOp(op, operand)
                elif len(expr.args) == 2:
                    left = self.scalarize_dense_array_op(expr.args[0], indices)
                    right = self.scalarize_dense_array_op(expr.args[1], indices)
                    assert left and right
                if isinstance(op, ast.operator): return ast.BinOp(left, op, right)
                elif isinstance(op, ast.cmpop): return ast.Compare(left, [op], [right])
                elif isinstance(op, ast.boolop): return ast.BoolOp(op, [left, right])
        return None

    def dense_opt_codegen(self, opt_info: OptInfo):
        stmts = []
        for expr in opt_info.pre_stmts:
            var = opt_info.pre_stmts[expr]
            if var:
                stmts.append(new_assign(var, expr))

        src_dim = self.curr_func.typemap[opt_info.src_var].ndim
        src_lw = 1 if opt_info.src_slice else 0
        idxvec = list(range(src_lw, src_dim))
        indices = list(map(lambda x: new_var(mytypes.int32, self.curr_func), idxvec))

        if rt_shape_check:
            check = self.generate_compatibility_check(opt_info.target_call)
            if check:
                stmts.append(check)

        if (not opt_info.full_expr
            or (not opt_info.tar_slice
                and not contains_var(opt_info.target_call, opt_info.tar_var))):
            init = self.generate_init_dense(opt_info.src_var, opt_info.tar_var, idxvec)
            stmts.append(init)

        body_expr = self.scalarize_dense_array_op(opt_info.target_call, indices)
        assert body_expr
        idcs = [opt_info.tar_slice] + indices if opt_info.tar_slice else indices
        loop = ast.Assign([new_subscript(opt_info.tar_var, idcs)], body_expr)
        for i in reversed(idxvec):
            pf = dense_par and i == src_lw
            loop = self.generate_for(indices[i-src_lw], 'shape', opt_info.src_var, i, [loop], pf)
        assert isinstance(loop, ast.For)
        stmts.append(loop)
        if verbose_level >= 4:
            print('[Verbose] Generated code:')
            for stmt in stmts: print(dumpfunc(stmt))

        return stmts


    def array_opt(self, stmts: list, analysis, codegen):
        new_stmts = []
        transformed = False
        for stmt in stmts:
            if is_assign_stmt(stmt):
                opt_list = []
                analysis(stmt, stmt.value, opt_list)
                if opt_list:
                    transformed = True
                    self.assign_new_vars(opt_list)
                    for opt_info in opt_list:
                        new_stmts.extend(codegen(opt_info))
                        if not opt_info.full_expr:
                            self.replace_func_arg_by_var(stmt,
                                                         opt_info.target_call,
                                                         opt_info.tar_var)
                            self.update_pre_stmts(opt_list.index(opt_info)+1, opt_list,
                                                  opt_info.target_call,
                                                  opt_info.tar_var)

                    if not opt_list[-1].full_expr: # Only Last can be full_expr
                        if verbose_level >= 4:
                            print('[Verbose] Replaced statement:\n', dumpfunc(stmt))
                        new_stmts.append(stmt)
                else:
                    new_stmts.append(stmt)
            else:
                self.visit(stmt)
                new_stmts.append(stmt)

        if transformed:
            stmts.clear()
            stmts.extend(new_stmts)

    def visit_body(self, stmts: list):
        if self.enable_sparse:
            self.array_opt(stmts, self.sparse_opt_analysis, self.sparse_opt_codegen)
        if self.enable_dense:
            self.array_opt(stmts, self.dense_opt_analysis, self.dense_opt_codegen)


############################################################################################

    def visit_FunctionDef(self, N: ast.FunctionDef):
        if verbose_level >= 2: print('[Verbose] Array opt for function:', N.name)
        self.curr_func = N
        self.enable_sparse = 'sparse_opt' in glb.options and glb.options['sparse_opt']
        self.enable_dense = 'dense_opt' in glb.options and glb.options['dense_opt']
        self.visit_body(N.body)

    def visit_For(self, N: ast.For):
        self.visit_body(N.body)
        assert not N.orelse

    def visit_While(self, N: ast.While):
        self.visit_body(N.body)
        assert not N.orelse

    def visit_If(self, N: ast.If):
        self.visit_body(N.body)
        self.visit_body(N.orelse)
