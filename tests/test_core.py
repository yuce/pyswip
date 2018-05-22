
import unittest
from pyswip.core import open_lib, _findSwipl

class CoreTest(unittest.TestCase):
    
    def test_open_lib(self):
        path, swi_home = _findSwipl()
        lib = open_lib(path)
        self.assertIsNotNone(lib)

        args = [
            "./",
            "-q",  # quiet
            "-nosignals", # Inhibit signal handling by SWI
        ]
        if swi_home is not None:
            args.append("--home=%s" % swi_home)

        result = lib.initialise(len(args),args)
        self.assertTrue(result)
        # # result is a boolean variable (i.e. 0 or 1) indicating whether the
        # # initialisation was successful or not.
        # if not result:
        #     raise PrologError("Could not initialize the Prolog environment."
        #                     "PL_initialise returned %d" % result)

        swipl_fid = lib.open_foreign_frame()
        swipl_load = lib.new_term_ref()
        lib.chars_to_term("asserta(pyrun(GoalString,BindingList) :- "
                        "(atom_chars(A,GoalString),"
                        "atom_to_term(A,Goal,BindingList),"
                        "call(Goal))).", swipl_load)
        lib.call(swipl_load, None)
        lib.discard_foreign_frame(swipl_fid)
        
