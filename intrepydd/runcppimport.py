# import subprocess
import sys
import os

# subprocess.call(["ls", "/404"],stderr=sys.stdout.buffer)
import cppimport
sys.path.append(os.getcwd())

module = sys.argv[1]
#print(module)
hashfile = ".%s.cpp.cppimporthash" % module
if os.path.isfile(hashfile):
    os.remove(hashfile)
cppimport.imp(module)

