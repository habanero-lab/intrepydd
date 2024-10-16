import os
import sys
from pathlib import Path
import inspect
import shutil
import hashlib
import importlib
import subprocess
from . import glb, launcher

def install_and_import(package):
    try:
        # Check if the package is already installed
        importlib.import_module(package)
        print(f"'{package}' is already installed.")
    except ImportError:
        # Package not found, install it
        print(f"'{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"'{package}' has been installed.")


def compile_from_file(file, args):
    sys.argv = sys.argv[:1]  # to make it work when hit "compile" multiple times in the web version
    sys.argv += [file] + args #+ ["-v"]
    glb.init()
    
    #os.chdir(glb.get_filepath())
    launcher.main()

def compile_from_src(src, no_cfg=False, dense_array_opt=False, sparse_array_opt=False, licm=False, slice_opt=False):
    import datetime
    dir = '/tmp/'
    filename = dir + f'kernel_{hashlib.sha256(src.encode()).hexdigest()}.pydd'
    p = Path(filename)
    p.write_text(src)
    args = []
    if dense_array_opt:
        args.append('-dense-opt')
    if sparse_array_opt:
        args.append('-sparse-opt')
    if licm:
        args.append('-licm')
    if slice_opt:
        args.append('-slice_opt')
    compile_from_file(filename, args)
    code = Path(filename.replace('.pydd', '.cpp')).read_text()
    if no_cfg and '%>\n' in code:
        code = code.split('%>\n')[1].strip()
    return code

def compile(fn, preserve_generated=False, dense_array_opt=False, sparse_array_opt=False, licm=False, slice_opt=False):
    source_code = inspect.getsource(fn)
    cpp_code = compile_from_src(source_code, dense_array_opt, sparse_array_opt, licm, slice_opt)
    module_name = ''
    for line in cpp_code.split():
        if line.startswith('PYBIND11_PLUGIN('):
            module_name = line.split('PYBIND11_PLUGIN(')[1].split(')')[0]
            break
    assert module_name != ''
    
    dir = '/tmp/'
    cpp_file = dir + module_name + '.cpp'
    copied_file = module_name + '.cpp'
    shutil.copy(cpp_file, copied_file)
    install_and_import('cppimport')
    module = cppimport.imp(module_name)
    Path(copied_file).unlink()
    Path('.rendered.' + copied_file).unlink(missing_ok=True)
    return getattr(module, fn.__name__)