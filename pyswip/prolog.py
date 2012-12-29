# -*- coding: utf-8 -*-


# prolog.py -- Prolog class
# Copyright (c) 2007-2012 Yüce Tekol
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys
import atexit

from pyswip.core import *


class PrologError(Exception):
    pass
    

def _initialize():
    args = []
    args.append("./")
    args.append("-q")
    args.append("-nosignals")
    if SWI_HOME_DIR is not None:
        args.append("--home=%s" % SWI_HOME_DIR)
    
    s_plargs = len(args)
    plargs = (c_char_p*s_plargs)()
    for i in range(s_plargs):
        plargs[i] = args[i]
        
    result = PL_initialise(s_plargs, plargs)
    # For some reason, PL_initialise is returning 1, even though everything is
    # working
#    if result != 0:
#        raise PrologError("Could not initialize Prolog environment."
#                          "PL_initialise returned %d" % result)
        
    swipl_fid = PL_open_foreign_frame()
    swipl_load = PL_new_term_ref()
    PL_chars_to_term("asserta(pyrun(GoalString,BindingList) :- "
                     "(atom_chars(A,GoalString),"
                     "atom_to_term(A,Goal,BindingList),"
                     "call(Goal))).", swipl_load)
    PL_call(swipl_load, None)
    PL_discard_foreign_frame(swipl_fid)
_initialize()

# Since the program is terminated when we call PL_halt, we monkey patch sys.exit
# to be able to intercept the exit status and ensure that PL_halt is the last
# function called from those registered in atexit. What we do here is very, very
# ugly. Any better way is welcome.
_original_sys_exit = sys.exit
def _patched_sys_exit(code=0):
    # Since atexit process exit functions from last to first, we put PL_halt as
    # the first one, so it will run last
    atexit._exithandlers.insert(0, (PL_halt, (code,), {}))
sys.exit = _patched_sys_exit


from pyswip.easy import getTerm

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

