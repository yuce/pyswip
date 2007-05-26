# -*- coding: utf-8 -*-

# util.py -- Utilites for pyswip
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

from pyswip import *

class PrologRunner:
	"""PrologRunner
	This is a singleton class
	"""
	
	initialized = False
	
	def __init__(self):
		if not PrologRunner.initialized:
			PrologRunner.__initialize()
			PrologRunner.initialized = True
	
	def __del__(self):
		if PrologRunner.initialized:
			PrologRunner.__finalize()

	def query(cls, query, maxresult=-1, maxsubresult=1024):
		"""Run a prolog query and return result.
		If the query is a yes/no question, returns [{}] for yes, and [] for no.
		Otherwise returns a list of dicts with variables as keys.
		
		>>> prolog = PrologRunner()
		>>> prolog.query("assertz(father(michael,john)).")
		[{}]
		>>> prolog.query("assertz(father(michael,gina)).")
		[{}]
		>>> prolog.query("father(michael,john).")
		[{}]
		>>> prolog.query("father(michael,olivia).")
		[]
		>>> r = prolog.query("father(michael,X).")
		>>> {"X":"john"} in r
		True
		>>> {"X":"olivia"} in r
		False		
		"""
		assert cls.initialized
		
		answers = []
		swipl_fid = PL_open_foreign_frame()
		swipl_head = PL_new_term_ref()
		swipl_args = PL_new_term_refs(2)
		swipl_goalCharList = swipl_args
		swipl_bindingList = swipl_args + 1
	
		PL_put_list_chars(swipl_goalCharList, query)
		
		swipl_predicate = PL_predicate("pyrun", 2, None)
		swipl_qid = PL_open_query(None, PL_Q_NORMAL, swipl_predicate, swipl_args)
		while PL_next_solution(swipl_qid) and maxresult:
			maxresult -= 1
			bindings = []
			swipl_list = PL_copy_term_ref(swipl_bindingList)
			answer = (c_char_p*maxsubresult)()
			while PL_get_list(swipl_list, swipl_head, swipl_list):
				PL_get_chars(swipl_head, answer, CVT_ALL | CVT_WRITE | BUF_RING)
				bindings.append(cstr2pystr(answer))
				
			answers.append(bindings)
			
		PL_close_query(swipl_qid)
		PL_discard_foreign_frame(swipl_fid)
		
		return [dict([y.split("=") for y in x]) for x in answers]
	
	query = classmethod(query)

	def __initialize(cls):
		plargs = (c_char_p * 3)()
		plargs[0] = "./"
		plargs[1] = "-q"
		plargs[2] = "\x00"
		PL_initialise(2, plargs)
		
		swipl_fid = PL_open_foreign_frame()
		swipl_load = PL_new_term_ref()
	
		PL_chars_to_term("assert(pyrun(GoalString,BindingList):-(atom_chars(A,GoalString),atom_to_term(A,Goal,BindingList),call(Goal))).", swipl_load)
	
		PL_call(swipl_load, None)
		PL_discard_foreign_frame(swipl_fid)
	
	__initialize = classmethod(__initialize)
	
	def __finalize(cls):
		PL_halt(0)
		
	__finalize = classmethod(__finalize)
		
def _test():
	lines = [("assertz(father(michael,john)).","Michael is the father of John"),
			("assertz(father(michael,gina)).","Michael is the father of Gina"),
			("father(michael,john).","Is Michael father of John?"),
			("father(michael,olivia).","Is Michael father of Olivia?"),
			("father(michael,X).","Michael is the father of whom?"),
			("father(X,Y).","Who is the father of whom?")]
	
	prolog = PrologRunner()
	
	for code, comment in lines:
		print "?-", code, "[", comment, "]"
		print prolog.query(code)	
	
if __name__ == "__main__":
	_test()	
	import doctest
	doctest.testmod()

