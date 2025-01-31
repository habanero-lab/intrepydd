import ast

class ReturnExprToStmt(ast.NodeTransformer):
    def visit_Return(self, node):
        if not isinstance(node.value, ast.Name):
            assign = ast.Assign(targets = [ast.Name(id = '__ret', ctx = ast.Store())], value = node.value, lineno = node.lineno, col_offset = node.col_offset)
            node.value = ast.Name(id = '__ret', ctx = ast.Load())
            return [assign] + [node]
        else:
            return node
