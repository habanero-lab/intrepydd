#!/usr/bin/env python3

from . import launcher
from . import glb
import cppimport
import sys
import os, errno
import io
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_indented_as_string(filename):
    try:
        output = subprocess.check_output(["clang-format", filename])
        return output
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
            # handle file not found error.
        else:
            pass
            # Something else went wrong while trying to run `wget`
    

            

def create_indented_cpp(filename):
    '''
    Create a stripped/valid cpp file from the generated kernel.cpp
    '''
    
    header = ''
    body = ''
    footer = ''
    state = 0
    for line in open(filename):
        if state == 0:
            header += line
        elif state == 1:
            if not line.startswith('PYBIND11_PLUGIN('):
                body += line
        elif state == 2:
            footer += line
            
        if state == 0 and line.startswith('namespace py'):
            state = 1

        if state == 1 and line.startswith('PYBIND11_PLUGIN('):
            state = 2
            footer += line


    newname = filename.replace('.cpp', '_indented.cpp')
    newfile = open(newname, 'w')
    newfile.write(body)
    newfile.close()
    output = ''
    try:
        body = subprocess.check_output(["clang-format", newname]).decode("utf-8")
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("[Tips]: installing clang-format (apt install clang-format) will indent the generated cpp file")
            # handle file not found error.
        else:
            print("cpp file formatting failed")
            
            # Something else went wrong while trying to run `wget`
            
    newfile = open(newname, 'w')
    newfile.write(header)
    newfile.write(body)
    newfile.write(footer)
    newfile.close()
    os.rename(newname, filename)

def compile(file):
    sys.argv[0] = file
    main()

def main():
    glb.init()
    os.chdir(glb.get_filepath())

    # Remove old files
    module = glb.get_module_name()
    # subprocess.call(['find', '.', '-name',
    #                  '%s.cpython*.so' % module,
    #                  '-or', '-name', '%s.cpp' % module,
    #                  '-delete'])   

    # Launch compiler
    launcher.main()


    if glb.args.host == 'cpp':
        sys.exit(0)

    if glb.args.opt_level == 2:
        if glb.args.no_compile:
            sys.exit(0)
    ### Doesn't seem to a general solution, commented out for now    
        #   if sys.platform.startswith('darwin'):
        #        os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.9"
        #        os.environ["CC"] = "clang"
        #        os.environ["CXX"] = "clang++"

        sys.path.append(os.getcwd())

        import time
        time_start = time.time()
        gcc_err = open(module+'_gcc.err', 'w')
        gcc_out = open(module+'_gcc.out', 'w')
        ret = subprocess.call(
            [sys.executable, glb.get_compiler_path()+"/runcppimport.py", module],
            stderr=gcc_err, stdout=gcc_out)

        time_end = time.time()
        print(time_end - time_start)
        if not glb.args.file.endswith('.cpp'):
            create_indented_cpp(module+'.cpp')
        if ret != 0:
            print("Compilation failed, gcc return code: %d."%ret)
            print("Check `./%s_gcc.err` for details." % module)

            if glb.args.verbose:
                for line in open(module+'_gcc.err', 'r'):
                    if 'error:' in line:
                        print(bcolors.FAIL+line+bcolors.ENDC)
                    else:
                        print(line)

            sys.exit(ret)            

    
if __name__ == "__main__":
    main()