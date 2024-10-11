#!/usr/bin/env python3

import ast
import sys
import os
from .typeinfer import TypeInferer
from .codegen import ModuleGen
from .scanner import Scanner
from .transform1 import TypeFreeTransformer
from .transform2 import TypedTransformer
from . import glb


def get_src_as_str():
    output = ''
    for line in open(glb.get_basefile()):
        sline = line.strip()
        if sline.startswith('pfor ') and sline[-1] == ':':
            sline = line.replace('pfor ', 'for ')
            line = sline.replace('\n', ' # type: pfor\n')
     
        output += line
    #print(output)        
    return output

def make_python_code(code):
    newcode = ''
    newcode += 'from pydd_debug import *'
    return

def gen_python_code(code):
    debug_path = os.path.dirname(os.path.realpath(__file__)) + '/debugging'
    prefix = 'import sys\n'
    prefix += 'sys.path.append("%s")\n' % debug_path
    prefix += 'from pydd_types import *\n'
    prefix += 'from pydd_python import *\n'
    prefix += 'from pydd_numpy import *\n'
    print(prefix+code, file=open(glb.get_module_name()+'.py', 'w'))

def gen_numba_code(code):
    print("Numba code generation is not supported yet!")
    sys.exit(0)

def gen_cpp_module(code):
    '''
    Each pydd file goes through three passes:

    - Scanner
      - Does some preprocessing stuff

    - TypeInferer
      - Does type inference

    - ModuleGen
      - Does the actul translation and generate the cpp module

    - TypeFreeTransformer
      - Apply AST transformations independent from type information

    - TypedTransformer
      - Apply AST transformations based on type information
    '''
    
    glb.open_cpp_module(glb.get_module_name())
    tree = ast.parse(code)
    if glb.args.verbose:
        print("AST parsing done.")

    scanner = Scanner()
    scanner.visit(tree)
    if glb.args.verbose:
        print("Scanner phase done.")        

    transform1 = TypeFreeTransformer()
    transform1.visit(tree)
    if glb.args.verbose:
        print("Transform1 phase done.")        

    analyzer = TypeInferer()
    analyzer.visit(tree)
    if glb.args.verbose:
        print("Type analyze phase done.")        

    transform2 = TypedTransformer()
    transform2.visit(tree)
    if glb.args.verbose:
        print("Transform2 phase done.")

    # This code is potentially buggy, to fix
    # if glb.args.alloc_opt:
    #     import escapeanalysis
    #     import escapetransform
    #     # This is hacky and inefficient but works for now 
    #     for _ in range(3):
    #         ea = escapeanalysis.EscapeAnalysis()
    #         ea.visit(tree)
    #         rewriter = escapetransform.AllocHoistTransformer()
    #         rewriter.visit(tree)

    if glb.args.g:
        import debugtransform
        rewriter = debugtransform.DebugTransformer()
        rewriter.visit(tree)

    if 'dumppy' in glb.options and glb.options['dumppy']:
        gen_python_code(ast.unparse(tree))

    module = ModuleGen()
    module.visit(tree)
    if glb.args.verbose:
        print("Code gen phase done.")

    glb.close_cpp_module()
        
def main():    
    # with open(f, "r") as source:
    #     tree = ast.parse(source.read())
    code = get_src_as_str()
    if glb.args.opt_level == 0:
        gen_python_code(code)
    elif glb.args.opt_level == 1:
        gen_numba_code(code)
    elif glb.args.opt_level == 2:
        if glb.args.file.find('.cpp') == -1:
            gen_cpp_module(code)
        
        
    
        
if __name__ == "__main__":
    main()

