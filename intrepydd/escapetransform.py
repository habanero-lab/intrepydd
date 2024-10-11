import sys
import ast
from pprint import pprint
import traceback

from . import mytypes
from . import glb
from . import utils
from . import libfuncs
from .symboltable import symtab
from .glb import UnhandledNodeException
from .glb import dump
from .astutils import *


class AllocHoistTransformer(ast.NodeTransformer):
    def __init__(self):
        self.logger = utils.get_logger('ea')


    def visit_FunctionDef(self, F: ast.FunctionDef):
        body = F.body
        visited = set()
        for stmt in body:
            if is_loop(stmt):
                self.do_loop(stmt, body, visited)
        
        return F


    def do_loop(self, N, outerbody, visited):
        '''
        Each loop is associated with a set of allocation sites
        that are candidate for hoisting. This function removes
        these sites from the loop body and insert them immediately
        before the loop.
        '''
        if N in visited:
            return
        
        loopbody = N.body
        sites = N.alloc_sites
        
        for site in sites:    
            siteindex = loopbody.index(site)
            self.logger.debug("hoist site: %s" % site)
            arrayname = get_assign_target(site)
            fillcall = ast.Expr(create_call('fill', [arrayname, '0']))
            ast.copy_location(fillcall, site)
            # This will cause dumped python file line issue
            loopbody[siteindex] = fillcall

        #N.alloc_sites.clear()
        index = outerbody.index(N)

        sites.reverse()
        for site in sites:
            outerbody.insert(index, site)

        for stmt in loopbody:
            if is_loop(stmt):                
                self.do_loop(stmt, loopbody, visited)

        visited.add(N)


