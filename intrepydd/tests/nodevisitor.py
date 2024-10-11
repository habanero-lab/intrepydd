import ast
import sys

class v(ast.NodeVisitor):
    def generic_visit(self, node):
        print(ast.dump(node))
        #print(type(node).__name__)
        ast.NodeVisitor.generic_visit(self, node)


x = v()
f = sys.argv[1]
s = open(f).read()
t = ast.parse(s)
x.visit(t)
