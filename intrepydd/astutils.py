import ast
from . import mytypes
from . import glb
#from glb import dump


def get_line_number(N):
    return N.lineno


def get_lineno(N):
    return N.lineno


def has_lineno(N):
    return hasattr(N, 'lineno')


def has_location(N):
    return hasattr(N, 'lineno') and hasattr(N, 'col_offset')
    
def is_name(N):
    return isinstance(N, ast.Name)


def is_assign(N):
    return isinstance(N, ast.Assign) or isinstance(N, ast.AnnAssign)


def is_aug_assign(N):
    return isinstance(N, ast.AugAssign)


def is_assign_to_name(N):
    if is_assign(N):
        targets = N.targets
        assert len(targets) == 1, "multiple targets in Assign not supported"
        return is_name(targets[0])
    return False


def is_alloc_site(N):
    if not is_assign(N):
        return False
    rhs = N.value

    # if 'zeros' in ast.dump(rhs):
    #     print('call', rhs)
    # if is_call(rhs):
    #     print('call', rhs)
    return is_call_to(rhs, 'empty') or \
        is_call_to(rhs, 'zeros') or \
        is_call_to(rhs, 'empty_like') or \
        is_call_to(rhs, 'zeros_like')


def is_bin_op(N):
    return isinstance(N, ast.BinOp)


def get_bin_op_left(N):
    return N.left


def get_bin_op_right(N):
    return N.right


def get_bin_op_operands(N):
    return (N.left, N.right)


def is_setitem(N):
    if is_assign(N):
        tar = N.targets[0]
        return isinstance(tar, ast.Subscript)
    return False


def get_setitem_base(N: ast.Assign):
    return N.targets[0].value.id


def get_setitem_value(N: ast.Assign):
    return N.value


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


def is_call(N):
    return isinstance(N, ast.Call)


def create_call(funcname, argnames):
    if type(argnames) == str:
        argnames = [argnames]
    args = []
    for arg in argnames:
        args.append(ast.Name(id=arg, ctx=ast.Load()))
    call = ast.Call(func=ast.Name(id=funcname, ctx=ast.Load()), args=args, keywords=[])
    
    return call
    

def is_local_def(N):
    return is_assign_to_name(N)


def get_defined_name(N) -> str:
    return N.targets[0].id


def is_for(N):
    return isinstance(N, ast.For)


def is_while(N):
    return isinstance(N, ast.While)


def is_loop(N):
    return isinstance(N, ast.For) or isinstance(N, ast.While)


def get_loop_body(N) -> list:
    return N.body


def get_assign_target(N) -> str:
    targets = N.targets
    assert len(targets) == 1, "multiple targets in Assign not supported"
    return targets[0].id


def get_rhs(N):
    if is_assign(N):
        return N.value
    else:
        assert False


def get_lhs(N):
    if is_assign(N):
        targets = N.targets
        assert len(targets) == 1, "multiple targets in Assign not supported"
        return targets[0]
    elif is_aug_assign(N):
        return N.target
    else:
        return False
    
        
def is_rhs_name(N):
    return is_name(get_rhs(N))


def get_name_id(N):
    assert is_name(N)
    return N.id
