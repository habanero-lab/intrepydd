import sys
from pathlib import Path
import inspect

int64 = None
int32 = None
float64 = None
float32 = None
from . import glb, launcher

def Array(ty, ndim):
    pass
    return

def compile_from_file(file, args):
    sys.argv = sys.argv[:1]  # to make it work when hit "compile" multiple times in the web version
    sys.argv += [file] + args + ["-v"]
    glb.init()
    
    #print(glb.args)
    #os.chdir(glb.get_filepath())
    launcher.main()

def compile_from_src(src, no_cfg=False, dense_array_opt=False, sparse_array_opt=False, licm=False, slice_opt=False):
    import datetime
    filename = f'./kernel_{datetime.datetime.now().isoformat("_", "milliseconds").replace("-", "_").replace(":", "_").replace(".", "_")}.pydd'
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

def compile(fn, dense_array_opt=False, sparse_array_opt=False, licm=False, slice_opt=False):
    source_code = inspect.getsource(fn)
    cpp_code = compile_from_src(source_code, dense_array_opt, sparse_array_opt, licm, slice_opt)
    module_name = ''
    for line in cpp_code.split():
        if line.startswith('PYBIND11_PLUGIN('):
            module_name = line.split('PYBIND11_PLUGIN(')[1].split(')')[0]
            break
    assert module_name != ''
    #print(module_name)
    #exit(1)
    filename = f'{module_name}.cpp'
    Path(filename).write_text(cpp_code)
    import cppimport
    module = cppimport.imp(filename.replace('.cpp', ''))
    return getattr(module, fn.__name__)