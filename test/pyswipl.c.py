
from pyswip import *

def cstr2pystr(c_string):
	result = []
	for item in c_string:
		if item in ["\x00", None]:
			break
			
		r = []
		for x in item:
			if item == "\x00":
				break
			r.append(x)
		
		result.append("".join(r))
		
	return result

def pyswipl_run(query):
		# /**********************************************************/
		# /* Create a Python list to hold the lists of bindings.    */
		# /**********************************************************/
		answerList_Py = []

		# /**********************************************************/
		# /* Open a foreign frame and initialize the term refs.     */
		# /**********************************************************/
		swipl_fid = PL_open_foreign_frame()
		swipl_head = PL_new_term_ref()  #		/* Used in unpacking the binding List       */
		swipl_args = PL_new_term_refs(2)  #		/* The compound term for arguments to run/2 */
		swipl_goalCharList = swipl_args  #		/* Alias for arg 1                          */
		swipl_bindingList = swipl_args + 1  #         /* Alias for arg 2                          */

		# /**********************************************************/
		# /* Pack the query string into the argument compund term.  */
		# /**********************************************************/
#		goalString = "abcdefghijklmnopqrs"
		PL_put_list_chars(swipl_goalCharList, query)

		# /**********************************************************/
		# /* Generate a predicate to pyrun/2                        */
		# /**********************************************************/
		swipl_predicate = PL_predicate("pyrun", 2, None)

		# /**********************************************************/
		# /* Open the query, and iterate through the solutions.     */
		# /**********************************************************/
		swipl_qid = PL_open_query(None, PL_Q_NORMAL, swipl_predicate, swipl_args)
		while PL_next_solution(swipl_qid):
			# /**********************************************************/
			# /* Create a Python list to hold the bindings.             */
			# /**********************************************************/
			bindingList_Py = []

			# /**********************************************************/
			# /* Step through the bindings and add each to the list.    */
			# /**********************************************************/
			swipl_list = PL_copy_term_ref(swipl_bindingList)
			answer = (c_char_p*1024)()
			while PL_get_list(swipl_list, swipl_head, swipl_list):
				PL_get_chars(swipl_head, answer, CVT_ALL | CVT_WRITE | BUF_RING)
				bindingList_Py.append(cstr2pystr(answer))

			# /**********************************************************/
			# /* Add this binding list to the list of all solutions.    */
			# /**********************************************************/
			answerList_Py.append(bindingList_Py)

		# /**********************************************************/
		# /* Free this foreign frame...                             */
		# /* Added by Nathan Denny, July 18, 2001.                  */
		# /* Fixes a bug with running out of global stack when      */
		# /* asserting _lots_ of facts.                             */
		# /**********************************************************/
		PL_close_query(swipl_qid)
		PL_discard_foreign_frame(swipl_fid)
	
		# /**********************************************************/
		# /* Return the list of solutions.                          */
		# /**********************************************************/
		return answerList_Py
		
def initialize():
	# /**********************************************************/
	# /* Initialize the prolog kernel.                          */
	# /* The kernel is embedded (linked in) so I am setting the */
	# /* the startup path to be the current directory. Also,    */
	# /* I'm sending the -q flag to supress the startup banner. */
	# /**********************************************************/
	
	plargs = (c_char_p * 3)()
	plargs[0] = "./"
	plargs[1] = "-q"
	plargs[2] = "\x00"
	PL_initialise(2, plargs)
	
	swipl_fid = PL_open_foreign_frame()
	swipl_load = PL_new_term_ref()

	PL_chars_to_term("assert(pyrun(GoalString,BindingList):-(atom_codes(A,GoalString),atom_to_term(A,Goal,BindingList),call(Goal))).", swipl_load)

	PL_call(swipl_load, None)
	PL_discard_foreign_frame(swipl_fid)

def finalize():
	PL_halt(0)

def test():
	initialize()
	assertion = "assertz(father(yalcin,yuce))."
	query = "father(yalcin,Y)."
	
	print assertion
	print pyswipl_run(assertion)
	
	print query
	print pyswipl_run(query)
	
	finalize()
	
if __name__ == "__main__":
	test()
