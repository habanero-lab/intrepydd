from enum import Enum
import ast
from . import libfuncs
from . import defuse

'''
Analysis for Loop Invariant Code motion (focuses on array references as first step).

Identify outermost location where array base address & shape are invariant.
Thereby it is legal to move the base address & shape computation to the location.

Example:
    while t < times:        # x2's base & shape is invariant within this while loop.
        x1 = zeros(n, float64())
        for i in range(n):  # x1's base & shape is invariant within this for loop.
            x1[i] = x2[i,i]
        ...

At the AST-level, each loop (i.e., ast.For or ast.While) may have attribute
"inv_subscripts", a list of invariant references (i.e., ast.Subscript).

Todo:
 - If same array is used multiple times, it tries to combine the location if possible
 - Standardize options, print (verbose and warning), and assert
'''

### Options ###
# 0: Nothing, 1: Debug (light), 2: Debug (modelate), 3: Debug (heavy)
verbose_level = 0

### Functions to access/modify ast.For/While nodes ###
def set_inv_subscripts(N, subscripts):
    N.inv_subscripts = subscripts

    global verbose_level
    if verbose_level >= 1:
        print('[Verbose] Loop at line', N.lineno, 'has invariant array subscripts:', end=' ')
        for subscr in subscripts:
            print(subscr.value.id, end=', ')
        print()

def set_inv_array_dim(N: ast.FunctionDef, inv_array_dim):
    N.inv_array_dim = inv_array_dim

    global verbose_level
    if verbose_level >= 1:
        print('[Verbose] Max dimensionality', inv_array_dim)

### Utilities ###
def get_num_array_dim(N: ast.Subscript):
    if isinstance(N.slice, ast.Index):
        if isinstance(N.slice, ast.Tuple):
            return len(N.slice.elts)
        else:
            return 1
    else:
        return -1


############################################################################################

class LicmArrayAnalysis(defuse.DefUseAnalysis):

    def __init__(self):
        '''
        Information per Function Definition
        '''
        defuse.DefUseAnalysis.__init__(self)
        self.subscr_to_node = {}   # Key: subscript, Value: LevelTreeNode where subscript is invariant

    def verify_fields(self):
        defuse.DefUseAnalysis.verify_fields(self)
        assert not self.subscr_to_node

    def clear_level_tree_information(self):
        defuse.DefUseAnalysis.clear_level_tree_information(self)
        self.subscr_to_node.clear()

    def add_subscr_to_node(self, arr: ast.Subscript):
        self.subscr_to_node[arr] = self.level_tree_current

    def compute_outermost_invariant_loop(self, arr_id, node):
        inv_loop = None
        curr = node
        while curr:
            if curr.prev:
                curr = curr.prev
            else:
                curr = curr.parent
                if curr:
                    if (arr_id in curr.vars_def
                        or arr_id in curr.vars_may_def
                        or arr_id in curr.vars_cond_def):
                        break
                    elif (curr.kind is self.LevelTreeNode.Kind.FOR
                          or curr.kind is self.LevelTreeNode.Kind.WHILE):
                        inv_loop = curr
        return inv_loop

    def eval_invariant_loop(self, N: ast.FunctionDef):
        global verbose_level
        if verbose_level >= 2:
            self.show_fields(verbose_level >= 3)

        node_to_subscrs = {}  # Key: LevelTreeNode, Value: subscripts
        inv_array_dim = {}    # Key: array (ID), Value: max dimensionality
        for subscr in self.subscr_to_node:
            if isinstance(subscr.value, ast.Name):
                array_id = subscr.value.id
                inv_loop = self.compute_outermost_invariant_loop(array_id, self.subscr_to_node[subscr])
                ndim = get_num_array_dim(subscr)
                if inv_loop and ndim > 0:
                    self.subscr_to_node[subscr] = inv_loop
                    if inv_loop in node_to_subscrs:
                        node_to_subscrs[inv_loop].append(subscr)
                    else:
                        node_to_subscrs[inv_loop] = [subscr]

                    if array_id in inv_array_dim:
                        if ndim > inv_array_dim[array_id]:
                            inv_array_dim[array_id] = ndim
                    else:
                        inv_array_dim[array_id] = ndim

        for node in node_to_subscrs:
            subscripts = node_to_subscrs[node]
            set_inv_subscripts(node.ast_node, subscripts)

        set_inv_array_dim(N, inv_array_dim)


############################################################################################

    def visit_FunctionDef(self, N: ast.FunctionDef):
        self.verify_fields()

        self.visit_FunctionDef_main(N)

        self.eval_invariant_loop(N)

        self.clear_level_tree_information()

    def visit_Subscript(self, N: ast.Subscript):
        self.add_subscr_to_node(N)
        self.visit(N.value)
        self.visit(N.slice)
