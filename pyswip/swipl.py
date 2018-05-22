
import sys
import atexit
from ctypes import *

from .const import *


_swipl = None

def open_lib(path):
    global _swipl

    if _swipl:
        return _swipl
        
    _lib = CDLL(path)

    #create an exit hook which captures the exit code for our cleanup function
    class ExitHook(object):
        def __init__(self):
            self.exit_code = None
            self.exception = None

        def hook(self):
            self._orig_exit = sys.exit
            sys.exit = self.exit

        def exit(self, code=0):
            self.exit_code = code
            self._orig_exit(code)

    _hook = ExitHook()
    _hook.hook()
    
    
    # register the cleanup function to be executed on system exit
    @atexit.register
    def _cleanup():
        # only do something if Prolog has been initialised
        if _lib.PL_is_initialised(None, None):

            # clean up the Prolog system using the caught exit code
            # if exit code is None, the program exits normally and we can use 0
            # instead.
            # TODO Prolog documentation says cleanup with code 0 may be interrupted
            # If the program has come to an end the prolog system should not
            # interfere with that. Therefore we may want to use 1 instead of 0.
            _lib.PL_cleanup(int(_hook.exit_code or 0))
            _swipl = None

    # def define_fun(name, argtypes, restype):
    #     f = getattr(_lib, name)
    #     f.argtypes = argtypes
    #     f.restype = restype


    class Swipl:
        initialise = check_strings(None, 1)(_lib.PL_initialise)

        open_foreign_frame = _lib.PL_open_foreign_frame
        open_foreign_frame.restype = fid_t

        new_term_ref = _lib.PL_new_term_ref
        new_term_ref.restype = term_t

        new_term_refs = _lib.PL_new_term_refs
        new_term_refs.argtypes = [c_int]
        new_term_refs.restype = term_t

        chars_to_term = _lib.PL_chars_to_term
        chars_to_term.argtypes = [c_char_p, term_t]
        chars_to_term.restype = c_int
        chars_to_term = check_strings(0, None)(chars_to_term)

        call = _lib.PL_call
        call.argtypes = [term_t, module_t]
        call.restype = c_int

        call_predicate = _lib.PL_call_predicate
        call_predicate.argtypes = [module_t, c_int, predicate_t, term_t]
        call_predicate.restype = c_int

        discard_foreign_frame = _lib.PL_discard_foreign_frame
        discard_foreign_frame.argtypes = [fid_t]
        discard_foreign_frame.restype = None

        put_list_chars = _lib.PL_put_list_chars
        put_list_chars.argtypes = [term_t, c_char_p]
        put_list_chars.restype = c_int

        put_list_chars = check_strings(1, None)(put_list_chars)

        register_atom = _lib.PL_register_atom
        register_atom.argtypes = [atom_t]
        register_atom.restype = None

        unregister_atom = _lib.PL_unregister_atom
        unregister_atom.argtypes = [atom_t]
        unregister_atom.restype = None

        functor_name = _lib.PL_functor_name
        functor_name.argtypes = [functor_t]
        functor_name.restype = atom_t

        functor_arity = _lib.PL_functor_arity
        functor_arity.argtypes = [functor_t]
        functor_arity.restype = c_int

        get_atom = _lib.PL_get_atom
        get_atom.argtypes = [term_t, POINTER(atom_t)]
        get_atom.restype = c_int

        get_bool = _lib.PL_get_bool
        get_bool.argtypes = [term_t, POINTER(c_int)]
        get_bool.restype = c_int

        get_atom_chars = _lib.PL_get_atom_chars  # FIXME

        get_atom_chars.argtypes = [term_t, POINTER(c_char_p)]
        get_atom_chars.restype = c_int
        get_atom_chars = check_strings(None, 1)(get_atom_chars)

        get_string = _lib.PL_get_string
        get_string = check_strings(None, 1)(get_string)
        get_string_chars = get_string

        get_chars = _lib.PL_get_chars  # FIXME:
        get_chars = check_strings(None, 1)(get_chars)

        get_integer = _lib.PL_get_integer
        get_integer.argtypes = [term_t, POINTER(c_int)]
        get_integer.restype = c_int

        get_long = _lib.PL_get_long
        get_long.argtypes = [term_t, POINTER(c_long)]
        get_long.restype = c_int

        get_float = _lib.PL_get_float
        get_float.argtypes = [term_t, c_double_p]
        get_float.restype = c_int

        get_functor = _lib.PL_get_functor
        get_functor.argtypes = [term_t, POINTER(functor_t)]
        get_functor.restype = c_int

        get_name_arity = _lib.PL_get_name_arity
        get_name_arity.argtypes = [term_t, POINTER(atom_t), POINTER(c_int)]
        get_name_arity.restype = c_int

        get_arg = _lib.PL_get_arg
        get_arg.argtypes = [c_int, term_t, term_t]
        get_arg.restype = c_int

        get_head = _lib.PL_get_head
        get_head.argtypes = [term_t, term_t]
        get_head.restype = c_int

        get_tail = _lib.PL_get_tail
        get_tail.argtypes = [term_t, term_t]
        get_tail.restype = c_int

        get_nil = _lib.PL_get_nil
        get_nil.argtypes = [term_t]
        get_nil.restype = c_int

        put_atom_chars = _lib.PL_put_atom_chars
        put_atom_chars.argtypes = [term_t, c_char_p]
        put_atom_chars.restype = c_int
        put_atom_chars = check_strings(1, None)(put_atom_chars)

        atom_chars = _lib.PL_atom_chars
        atom_chars.argtypes = [atom_t]
        atom_chars.restype = c_char_p

        predicate = _lib.PL_predicate
        predicate.argtypes = [c_char_p, c_int, c_char_p]
        predicate.restype = predicate_t
        predicate = check_strings([0,2], None)(predicate)

        pred = _lib.PL_pred
        pred.argtypes = [functor_t, module_t]
        pred.restype = predicate_t

        open_query = _lib.PL_open_query
        open_query.argtypes = [module_t, c_int, predicate_t, term_t]
        open_query.restype = qid_t

        next_solution = _lib.PL_next_solution
        next_solution.argtypes = [qid_t]
        next_solution.restype = c_int

        copy_term_ref = _lib.PL_copy_term_ref
        copy_term_ref.argtypes = [term_t]
        copy_term_ref.restype = term_t

        get_list = _lib.PL_get_list
        get_list.argtypes = [term_t, term_t, term_t]
        get_list.restype = c_int

        get_chars = _lib.PL_get_chars  # FIXME

        close_query = _lib.PL_close_query
        close_query.argtypes = [qid_t]
        close_query.restype = None

        cut_query = _lib.PL_cut_query
        cut_query.argtypes = [qid_t]
        cut_query.restype = None

        halt = _lib.PL_halt
        halt.argtypes = [c_int]
        halt.restype = None

        cleanup = _lib.PL_cleanup
        cleanup.restype = c_int

        unify_integer = _lib.PL_unify_integer
        unify = _lib.PL_unify
        unify.restype = c_int

        unify_arg = _lib.PL_unify_arg
        unify_arg.argtypes = [c_int, term_t, term_t]
        unify_arg.restype = c_int

        term_type = _lib.PL_term_type
        term_type.argtypes = [term_t]
        term_type.restype = c_int

        is_variable = _lib.PL_is_variable
        is_variable.argtypes = [term_t]
        is_variable.restype = c_int

        is_ground = _lib.PL_is_ground
        is_ground.argtypes = [term_t]
        is_ground.restype = c_int

        is_atom = _lib.PL_is_atom
        is_atom.argtypes = [term_t]
        is_atom.restype = c_int

        is_integer = _lib.PL_is_integer
        is_integer.argtypes = [term_t]
        is_integer.restype = c_int

        is_string = _lib.PL_is_string
        is_string.argtypes = [term_t]
        is_string.restype = c_int

        is_float = _lib.PL_is_float
        is_float.argtypes = [term_t]
        is_float.restype = c_int

        is_compound = _lib.PL_is_compound
        is_compound.argtypes = [term_t]
        is_compound.restype = c_int

        is_functor = _lib.PL_is_functor
        is_functor.argtypes = [term_t, functor_t]
        is_functor.restype = c_int

        is_list = _lib.PL_is_list
        is_list.argtypes = [term_t]
        is_list.restype = c_int

        is_atomic = _lib.PL_is_atomic
        is_atomic.argtypes = [term_t]
        is_atomic.restype = c_int

        is_number = _lib.PL_is_number
        is_number.argtypes = [term_t]
        is_number.restype = c_int

        put_variable = _lib.PL_put_variable
        put_variable.argtypes = [term_t]
        put_variable.restype = None

        put_integer = _lib.PL_put_integer
        put_integer.argtypes = [term_t, c_long]
        put_integer.restype = None

        put_functor = _lib.PL_put_functor
        put_functor.argtypes = [term_t, functor_t]
        put_functor.restype = None

        put_list = _lib.PL_put_list
        put_list.argtypes = [term_t]
        put_list.restype = None

        put_nil = _lib.PL_put_nil
        put_nil.argtypes = [term_t]
        put_nil.restype = None

        put_term = _lib.PL_put_term
        put_term.argtypes = [term_t, term_t]
        put_term.restype = None

        cons_functor = _lib.PL_cons_functor  # FIXME:

        cons_functor_v = _lib.PL_cons_functor_v
        cons_functor_v.argtypes = [term_t, functor_t, term_t]
        cons_functor_v.restype = None

        cons_list = _lib.PL_cons_list
        cons_list.argtypes = [term_t, term_t, term_t]
        cons_list.restype = None

        exception = _lib.PL_exception
        exception.argtypes = [qid_t]
        exception.restype = term_t

        register_foreign = _lib.PL_register_foreign
        register_foreign = check_strings(0, None)(register_foreign)

        new_atom = _lib.PL_new_atom
        new_atom.argtypes = [c_char_p]
        new_atom.restype = atom_t
        new_atom = check_strings(0, None)(new_atom)

        new_functor = _lib.PL_new_functor
        new_functor.argtypes = [atom_t, c_int]
        new_functor.restype = functor_t

        compare = _lib.PL_compare
        compare.argtypes = [term_t, term_t]
        compare.restype = c_int

        same_compound = _lib.PL_same_compound
        same_compound.argtypes = [term_t, term_t]
        same_compound.restype = c_int

        record = _lib.PL_record
        record.argtypes = [term_t]
        record.restype = record_t

        recorded = _lib.PL_recorded
        recorded.argtypes = [record_t, term_t]
        recorded.restype = None

        erase = _lib.PL_erase
        erase.argtypes = [record_t]
        erase.restype = None

        new_module = _lib.PL_new_module
        new_module.argtypes = [atom_t]
        new_module.restype = module_t

        is_initialised = _lib.PL_is_initialised

    _swipl = Swipl

    return _swipl


# create a decorator that turns the incoming strings into c_char_p compatible
# butes or pointer arrays
def check_strings(strings, arrays):
    """
    Decorator function which can be used to automatically turn an incoming
    string into a bytes object and an incoming list to a pointer array if
    necessary.

    :param strings: Indices of the arguments must be pointers to bytes
    :type strings: List of integers
    :param arrays: Indices of the arguments must be arrays of pointers to bytes
    :type arrays: List of integers
    """

    # if given a single element, turn it into a list
    if isinstance(strings, int):
        strings = [strings]
    elif strings is None:
        strings = []

    # check if all entries are integers
    for i,k in enumerate(strings):
        if not isinstance(k, int):
            raise TypeError(('Wrong type for index at {0} '+
                    'in strings. Must be int, not {1}!').format(i,k))

    # if given a single element, turn it into a list
    if isinstance(arrays, int):
        arrays = [arrays]
    elif arrays is None:
        arrays = []

    # check if all entries are integers
    for i,k in enumerate(arrays):
        if not isinstance(k, int):
            raise TypeError(('Wrong type for index at {0} '+
                    'in arrays. Must be int, not {1}!').format(i,k))

    # check if some index occurs in both
    if set(strings).intersection(arrays):
        raise ValueError('One or more elements occur in both arrays and ' +
                ' strings. One parameter cannot be both list and string!')

    # create the checker that will check all arguments given by argsToCheck
    # and turn them into the right datatype.
    def checker(func):
        def check_and_call(*args):
            args = list(args)
            for i in strings:
                arg = args[i]
                args[i] = arg.encode()
            for i in arrays:
                arg = args[i]
                args[i] = list_to_bytes_list(arg)

            return func(*args)

        return check_and_call

    return checker


def list_to_bytes_list(str_list):
    """
    This function turns an array of strings into a pointer array
    with pointers pointing to the encodings of those strings
    Possibly contained bytes are kept as they are.

    :param strList: List of strings that shall be converted
    :type strList: List of strings
    :returns: Pointer array with pointers pointing to bytes
    :raises: TypeError if strList is not list, set or tuple
    """

    p_list = c_char_p * len(str_list)
    # if strList is already a pointerarray or None, there is nothing to do
    if isinstance(str_list, (p_list, type(None))):
        return str_list

    if not isinstance(str_list, (list, set, tuple)):
        raise TypeError("strList must be list, set or tuple, not " +
                str(type(str_list)))

    p_list = p_list()
    for i, elem in enumerate(str_list):
        p_list[i] = elem.encode()
    return p_list
