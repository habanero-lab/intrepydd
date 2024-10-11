import argparse
import configparser
import ast
import os
import platform
import sys
import importlib
import traceback
import logging
from . import mytypes
from . import libfuncs
from .symboltable import symtab
from . import astutils
from . import utils


class UnsupportedException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class UnhandledNodeException(Exception):
    def __init__(self, N):
        Exception.__init__(self, ast.dump(N))

class UndefinedSymbolException(Exception):
    def __init__(self, module, funcname):
        self.module = module
        self.funcname = funcname
        Exception.__init__(self)

    def __str__(self):
        if not self.module:
            self.module = 'built-in'
        s = 'undefined function `%s` in module `%s`' % (self.funcname, self.module)
        return s    
        
# class UnhandledNodeException(Exception):
#     def __init__(self, N):
#         Exception.__init__(self, ast.dump(N))

# def dump(N):
#     print(ast.dump(N))
                

def dump(N, msg=''):
    print(msg, ast.dump(N))
                

args = None
options = {}
func_versions = {}

def init():
    '''
    Set up global stuff
    '''
    global args, options, func_versions
    options = {}
    func_versions = {}
    parse_args()
    setup_loggers()


def setup_loggers():
    # l = utils.setup_logger('ea', 'ea.log')
    # if args.verbose:
    #     l.setLevel(logging.DEBUG)

    l = utils.setup_logger('type', 'type.log')
    if args.dump_type:
        l.setLevel(logging.DEBUG)

    
        
def parse_args():
    global args, options, func_versions
    desc ='''Compiles an Intrepydd program into native code that can be imported as a Python module.
    The command-line options below are for experimental features under development.
    '''
    parser = argparse.ArgumentParser(description=desc)        
    parser.add_argument('file', help='input file')
    # parser.add_argument('--pymodule', default=True,
    #                     action='store_true', help='produce a python module')
    parser.add_argument('-host', default='py', help='[py|cpp]')
    parser.add_argument('-I', default='', help='Header file search location, separated by `:`')
    parser.add_argument('-compiler-flags', default='', help='Compiler flags, separated by `:`')
    parser.add_argument('-linker-flags', default='', help='Linker flags, separated by `:`')
    parser.add_argument('-func-version', default='', help='Specify the version number of a function')
    parser.add_argument('-opt-level', default=2, help='Optimization level, defaults to 2')
    parser.add_argument('-O0', default=False, action='store_true', help='Generate Python code (in progress)')
    parser.add_argument('-O1', default=False, action='store_true', help='Generate Numba code (in progress)')
    parser.add_argument('-O2', default=False, action='store_true', help='Generate native code (default)')
    parser.add_argument('-g', default=False, action='store_true', help='Generate code with debug info')
    parser.add_argument('-dumppy', default=False, action='store_true', help='Dump Python code from optimized AST via O2')
    parser.add_argument('-blas', default=True, action='store_true', help='Use BLAS calls')
    parser.add_argument('-verbose', default=False, action='store_true', help='General verbose flag')
    parser.add_argument('-cpp', default=False, action='store_true', help='Set host to cpp')
    parser.add_argument('-no-compile', default=False, action='store_true', help='Just generate cpp file but not compile it')
#    parser.add_argument('-g', default=False, action='store_true', help='Enable debug mode')
    parser.add_argument('-unchecked-access', default=True, action='store_true', help='Fast but unchecked array access')
    parser.add_argument('-licm', default=False, action='store_true', help='Loop Invariant Code Motion')
    parser.add_argument('-licm-array', default=False, action='store_true', help='Loop Invariant Code Motion for array references')
    parser.add_argument('-licm-ast', default=False, action='store_true', help='Loop Invariant Code Motion for AST-level expressions (general)')
    parser.add_argument('-array-opt', default=False, action='store_true', help='Sparse/dense array optimizations')
    parser.add_argument('-sparse-opt', default=False, action='store_true', help='Sparse array optimizations')
    parser.add_argument('-dense-opt', default=False, action='store_true', help='Dense array optimizations')
    parser.add_argument('-slice-opt', default=False, action='store_true', help='Use raw pointers for slices')
    # Tong: This option is potentially buggy, disable for now
    # parser.add_argument('-alloc-opt', default=False, action='store_true', help='Array allocation optimizations via escape analsis')

    parser.add_argument('-dump-type', default='', help='Dump type info for locals (defaults to all locals). Possible values: "*" (all), "!__" (no __xx vars), "[var_name]"')
    
    args = parser.parse_args()

    if args.O2:
        args.opt_level = 2
    elif args.O1:
        args.opt_level = 1
    elif args.O0:
        args.opt_level = 0
    else:
        args.opt_level = 2

    if args.cpp:
        args.host = 'cpp'
    if args.func_version:    
        funcs = args.func_version.split(',')
        for f in funcs:
            items = f.split(':')
            funcname = items[0]
            version = items[1]
            func_versions[funcname] = version

    if args.dumppy:
        options['dumppy'] = True

    if args.licm:
        options['licm_array'] = True
        options['licm_ast'] = True

    if args.licm_array:
        options['licm_array'] = True

    if args.licm_ast:
        options['licm_ast'] = True

    if args.array_opt:
        options['sparse_opt'] = True
        options['dense_opt'] = True
    if args.sparse_opt:
        options['sparse_opt'] = True
    if args.dense_opt:
        options['dense_opt'] = True

    #print(args)

def get_func_version(name):
    return func_versions.get(name, 0)

def parse_config_file():
    global options
    C = configparser.ConfigParser()
    C.read("config.ini")
    for section in C.sections():
        opts = C.options(section)
        print(opts)
        for opt in opts:
            options[opt] = C.get(section, opt)
    
    print(options)
            
def get_option(o):
    return options[o]

cpp_ofs = None

def open_cpp_ofs(mod_name):
    global cpp_ofs
    cpp_ofs = open(mod_name+'.cpp', 'w')

def close_cpp_ofs(mod_name):
    global cpp_ofs
    cpp_ofs.close()

class CppModule(object):
    def __init__(self, name):
        self.ofs = open(name+'.cpp', 'w')
        self.pymodule = False
        self.funcs = []
        self.imports = {}
        if args.opt_level == 2:
            self.pymodule = True

    def close(self):
        self.ofs.close()      

    def writeln(self, s=''):
        print(s, file=self.ofs)

    def write(self, s):
        print(s, file=self.ofs, end='')

    def add_function(self, N):
        self.funcs.append(N)

    def add_imported_module(self, alias):
        realname = alias.name
        asname = alias.asname
        cppmodname = realname
        if is_imported_module_standard(cppmodname):
            cppmodname = 'std'            
        
        if asname:
            self.imports[asname] = cppmodname
        else:
            self.imports[realname] = cppmodname

    def get_module_namespace(self, name):
        return self.imports[name]

    def is_module(self, name):
        return name in self.imports

    def do_pymodule_header(self):
        if not self.pymodule:
            return


        cxxflags = ['-std=c++11']
        if platform.system() == 'Darwin':
            cxxflags += ['-stdlib=libc++']
        for p in get_include_paths():
            cxxflags.append('-I' + p)
        if args.I:
            for p in args.I.split(':'):
                cxxflags.append('-I' + p)

        cxxflags += libfuncs.get_compiler_flags()
        if args.compiler_flags:    
            cxxflags += args.compiler_flags.split(':')
        cfg = '<%\n'
        cfg += "cfg['compiler_args'] = %s\n" % str(cxxflags)

        linker_flags = libfuncs.get_linker_flags()

        if args.linker_flags:    
            linker_flags += args.linker_flags.split(':')
        cfg += "cfg['linker_args'] = %s\n" % str(linker_flags)
        cfg += "setup_pybind11(cfg)\n"
        cfg += '%>'
        self.writeln(cfg)
        self.writeln('')

    def do_default_include(self):
        self.writeln('#include "shared/rt.hpp"')
        if args.host == 'cpp':
            self.writeln('#include "cpp/NdArray.hpp"')
        elif args.host == 'py':
            self.writeln('#include <pybind11/pybind11.h>')
            self.writeln('#include <pybind11/stl.h>')
            self.writeln('#include <pybind11/numpy.h>')
        else:
            assert False
        
        for h in libfuncs.get_header_files():
            self.writeln('#include "%s"' % h)
            
        self.writeln('')

        if args.host == 'py':    
            self.writeln('namespace py = pybind11;\n')


    def do_py_footer(self):
        if not self.pymodule:
            return
        m = get_module_name()
        self.writeln('PYBIND11_PLUGIN(%s) {' % m)
        self.writeln('  pybind11::module m("%s", "auto-compiled c++ extension");' % m)
        for F in self.funcs:
            fn = F.name
            s = '  m.def("%s", &%s::%s,' % (fn, m, fn)
            for arg in F.args.args:
                s += 'py::arg().noconvert(),'
            self.writeln(s[:-1] + ');')
        self.writeln('  return m.ptr();')
        self.writeln('}')  

def is_imported_module_standard(name):
    if name == 'cmath':
        return True
    return False

    
cpp_module = None
        
def open_cpp_module(name):
    global cpp_module
    cpp_module = CppModule(name)

def close_cpp_module():
    cpp_module.close()
        
def get_basefile():
    return os.path.basename(args.file)

def get_filepath():
    d = os.path.dirname(args.file)
    if d:
        return d
    else:
        return '.'

def get_module_name():
    return os.path.basename(get_module_fullname())

def get_module_fullname():
    return args.file.replace('.pydd', '').replace('.py', '').replace('.cpp', '')

def get_module_path(s):
    return os.path.dirname(get_module_fullname())
    
def get_include_paths():
    paths = []
    paths.append(get_compiler_path() + '/include/')
    paths.append(get_compiler_path() + '/library/')
    return paths

def get_compiler_path():
    return os.path.dirname(os.path.realpath(__file__))

    
def is_user_defined_func(name):
    # Assume all non-user-defined functions are built-in
    return symtab.is_user_defined_symbol(name)

def get_module_func_ret_type(module, func, arg_types):
    path = "%s/library/%s/metadata.py" % (get_compiler_path(), module)
    spec = importlib.util.spec_from_file_location('metadata', path)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    funcinfo = M.funcinfo
    
def get_imported_module_info(module):
    path = "%s/library/%s/metadata.py" % (get_compiler_path(), module)
    spec = importlib.util.spec_from_file_location('metadata', path)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    return M
    

def import_file(full_name, path):
    """Import a python module from a path. 3.4+ only.

    Does not call sys.modules[full_name] = path
    """
    spec = importlib.util.spec_from_file_location(full_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


unrecognized_type_annotation = 'unrecognized type annotation'
unsupported_node = 'unsupported node'

def exit_on_unsupported_node(N):
    exit_on_node(N, 'unsupported node')

def exit_on_unsupported_type_ann(N):
    exit_on_node(N, 'unrecognized type annotation')

def exit_on_node(N, msg=""):
#    print('node', vars(N))
    if args.verbose:
        traceback.print_stack()
        print('=================== Stack Trace Ends =================')
    print('error:', msg)
    print('problematic node:', ast.dump(N))
    if astutils.has_location(N):
        print('line number:', astutils.get_lineno(N))
        print('column offset:', N.col_offset)
        print('problematic line:\n')
        lineno = 0
        for line in open(args.file):
            lineno += 1
            if lineno == N.lineno:
                print(line)
        for i in range(N.col_offset):
            print(' ', end='')
        print('^')    
    sys.exit(1)
