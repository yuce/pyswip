# -*- coding: utf-8 -*-

# prolog.py -- Prolog class
# (c) 2006-2007 Yüce TEKOL
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import atexit
from pyswip.core import *

def _initialize():
    plargs = (c_char_p*3)()
    plargs[0] = "./"
    plargs[1] = "-q"
    plargs[2] = "-nosignals"
    PL_initialise(3, plargs)
    swipl_fid = PL_open_foreign_frame()
    swipl_load = PL_new_term_ref()
    PL_chars_to_term("asserta(pyrun(GoalString,BindingList):-(atom_chars(A,GoalString),atom_to_term(A,Goal,BindingList),call(Goal))).", swipl_load)
    PL_call(swipl_load, None)
    PL_discard_foreign_frame(swipl_fid)
_initialize()

def _finalize():
    PL_halt(0)
atexit.register(_finalize)

from pyswip.easy import getTerm

class PrologError(Exception):
    pass
    

#### Prolog ####
class Prolog:
    """Easily query SWI-Prolog.
    This is a singleton class
    """
    class _QueryWrapper(object):
        __slots__ = "swipl_fid","swipl_qid","error"
        
        def __init__(self):
            self.error = False
    
        def __call__(self, query, maxresult, catcherrors, normalize):
            plq = catcherrors and (PL_Q_NODEBUG|PL_Q_CATCH_EXCEPTION) or PL_Q_NORMAL
            self.swipl_fid = PL_open_foreign_frame()
            swipl_head = PL_new_term_ref()
            swipl_args = PL_new_term_refs(2)
            swipl_goalCharList = swipl_args
            swipl_bindingList = swipl_args + 1
        
            PL_put_list_chars(swipl_goalCharList, query)
            
            swipl_predicate = PL_predicate("pyrun", 2, None)
            self.swipl_qid = swipl_qid = PL_open_query(None, plq,
                    swipl_predicate, swipl_args)
            while maxresult and PL_next_solution(swipl_qid):
                maxresult -= 1
                bindings = []
                swipl_list = PL_copy_term_ref(swipl_bindingList)
                t = getTerm(swipl_list)
                if normalize:
                    try:
                        v = t.value
                    except AttributeError:
                        v = {}
                        for r in [x.value for x in t]:
                            v.update(r)
                    yield v
                else:
                    yield t
                
            if PL_exception(self.swipl_qid):
                self.error = True
                PL_cut_query(self.swipl_qid)
                PL_discard_foreign_frame(self.swipl_fid)
                raise PrologError("".join(["Caused by: '", query, "'."]))
        
        def __del__(self):
            if not self.error:
                PL_close_query(self.swipl_qid)
                PL_discard_foreign_frame(self.swipl_fid)    
    
    def asserta(cls, assertion, catcherrors=False):
        cls.query(assertion.join(["asserta((", "))."]), catcherrors=catcherrors).next()
        
    asserta = classmethod(asserta)    
    
    def assertz(cls, assertion, catcherrors=False):
        cls.query(assertion.join(["assertz((", "))."]), catcherrors=catcherrors).next()
        
    assertz = classmethod(assertz)
    
    def consult(cls, filename, catcherrors=False):
        cls.query(filename.join(["consult('", "')"]), catcherrors=catcherrors).next()
    
    consult = classmethod(consult)

    def query(cls, query, maxresult=-1, catcherrors=True, normalize=True):
        """Run a prolog query and return a generator.
        If the query is a yes/no question, returns {} for yes, and nothing for no.
        Otherwise returns a generator of dicts with variables as keys.
        
        >>> prolog = Prolog()
        >>> prolog.assertz("father(michael,john)")
        >>> prolog.assertz("father(michael,gina)")
        >>> bool(list(prolog.query("father(michael,john)")))
        True
        >>> bool(list(prolog.query("father(michael,olivia)")))
        False
        >>> print sorted(prolog.query("father(michael,X)"))
        [{'X': 'gina'}, {'X': 'john'}]
        """
        #assert cls.initialized        
        return cls._QueryWrapper()(query, maxresult, catcherrors, normalize)
    
    query = classmethod(query)
    
        
def _test():
    lines = [("assertz(father(michael,john)).","Michael is the father of John"),
            ("assertz(father(michael,gina)).","Michael is the father of Gina"),
            ("father(michael,john).","Is Michael father of John?"),
            ("father(michael,olivia).","Is Michael father of Olivia?"),
            ("father(michael,X).","Michael is the father of whom?"),
            ("father(X,Y).","Who is the father of whom?")]
    
    prolog = Prolog()
    
    for code, comment in lines:
        print "?-", code, "[", comment, "]"
        print list(prolog.query(code))
        
    for r in prolog.query("father(X,Y)"):
        print r["X"], "is the father of", r["Y"]
        
    
if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    _test()

