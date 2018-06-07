
import sys
import atexit
from ctypes import *

from .const import *


__all__ = "Swipl",

class Swipl:
    lib = None


def open_lib(path):
    if Swipl.lib:
        return Swipl.lib
        
    _lib = CDLL(path, mode=RTLD_GLOBAL)

    def _(name, argtypes, restype):
        f = getattr(_lib, name)
        f.argtypes = argtypes
        f.restype = restype
        return f


    class Lib:

        atom_chars = _("PL_atom_chars", [atom_t], c_char_p)
        call = _("PL_call", [term_t, module_t], c_int)
        call_predicate = _("PL_call_predicate", [module_t, c_int, predicate_t, term_t], c_int)
        chars_to_term = check_strings(0, None)(_("PL_chars_to_term", [c_char_p, term_t], c_int))
        cleanup = _("PL_cleanup", [], c_int)
        cleanup.restype = c_int
        close_query = _("PL_close_query", [qid_t], None)
        compare = _("PL_compare", [term_t, term_t], c_int)
        cons_functor_v = _("PL_cons_functor_v", [term_t, functor_t, term_t], None)
        cons_list = _("PL_cons_list", [term_t, term_t, term_t], None)
        copy_term_ref = _("PL_copy_term_ref", [term_t], term_t)
        cut_query = _("PL_cut_query", [qid_t], None)
        discard_foreign_frame = _("PL_discard_foreign_frame", [fid_t], None)
        erase = _("PL_erase", [record_t], None)
        exception = _("PL_exception", [qid_t], term_t)
        functor_arity = _("PL_functor_arity", [functor_t], c_int)
        functor_name = _("PL_functor_name", [functor_t], atom_t)
        get_arg = _("PL_get_arg", [c_int, term_t, term_t], c_int)
        get_atom_chars = check_strings(None, 1)(_("PL_get_atom_chars", [term_t, POINTER(c_char_p)], c_int))
        get_atom = _("PL_get_atom", [term_t, POINTER(atom_t)], c_int)
        get_bool = _("PL_get_bool", [term_t, POINTER(c_int)], c_int)
        get_chars = _("PL_get_chars", [term_t, POINTER(c_char_p), c_uint], c_int)
        get_float = _("PL_get_float", [term_t, c_double_p], c_int)
        get_functor = _("PL_get_functor", [term_t, POINTER(functor_t)], c_int)
        get_head = _("PL_get_head", [term_t, term_t], c_int)
        get_integer = _("PL_get_integer", [term_t, POINTER(c_int)], c_int)
        get_list = _("PL_get_list", [term_t, term_t, term_t], c_int)
        get_long = _("PL_get_long", [term_t, POINTER(c_long)], c_int)
        get_name_arity = _("PL_get_name_arity", [term_t, POINTER(atom_t), POINTER(c_int)], c_int)
        get_nil = _("PL_get_nil", [term_t], c_int)
        get_string_chars = _("PL_get_string", [term_t, POINTER(c_char_p), c_int_p], c_int)
        get_tail = _("PL_get_tail", [term_t, term_t], c_int)
        halt = _("PL_halt", [c_int], None)
        initialise = check_strings(None, 1)(_lib.PL_initialise)
        is_atom = _("PL_is_atom", [term_t], c_int)
        is_atomic = _("PL_is_atomic", [term_t], c_int)
        is_callable = _("PL_is_callable", [term_t], c_int)
        is_compound = _("PL_is_compound", [term_t], c_int)
        is_float = _("PL_is_float", [term_t], c_int)
        is_functor = _("PL_is_functor", [term_t, functor_t], c_int)
        is_ground = _("PL_is_ground", [term_t], c_int)
        is_initialised = _lib.PL_is_initialised
        is_integer = _("PL_is_integer", [term_t], c_int)
        is_list = _("PL_is_list", [term_t], c_int)
        is_number = _("PL_is_number", [term_t], c_int)
        is_string = _("PL_is_string", [term_t], c_int)
        is_variable = _("PL_is_variable", [term_t], c_int)
        new_atom = check_strings(0, None)(_("PL_new_atom", [c_char_p], atom_t))
        new_functor = _("PL_new_functor", [atom_t, c_int], functor_t)
        new_module = _("PL_new_module", [atom_t], module_t)
        new_term_ref = _("PL_new_term_ref", [], term_t)
        new_term_refs = _("PL_new_term_refs", [c_int], term_t)
        next_solution = _("PL_next_solution", [qid_t], c_int)
        open_foreign_frame = _("PL_open_foreign_frame", [], fid_t)
        open_query = _("PL_open_query", [module_t, c_int, predicate_t, term_t], qid_t)
        pred = _("PL_pred", [functor_t, module_t], predicate_t)
        predicate = _("PL_predicate", [c_char_p, c_int, c_char_p], predicate_t)
        put_atom_chars = check_strings(1, None)(_("PL_put_atom_chars", [term_t, c_char_p], c_int))
        put_functor = _("PL_put_functor", [term_t, functor_t], None)
        put_integer = _("PL_put_integer", [term_t, c_long], None)
        put_list_chars = check_strings(1, None)(_("PL_put_list_chars", [term_t, c_char_p], c_int))
        put_list = _("PL_put_list", [term_t], None)
        put_nil = _("PL_put_nil", [term_t], None)
        put_term = _("PL_put_term", [term_t, term_t], None)
        put_variable = _("PL_put_variable", [term_t], None)
        record = _("PL_record", [term_t], record_t)
        recorded = _("PL_recorded", [record_t, term_t], None)
        register_atom = _("PL_register_atom", [atom_t], None)
        # register_foreign = check_strings(0, None)(_("PL_register_foreign", [c_char_p, c_int, CFUNCTYPE(foreign_t, c_int)], c_int))
        # register_foreign = _("PL_register_foreign", [c_char_p, c_int, CFUNCTYPE(foreign_t, c_int)], c_int)
        register_foreign = check_strings(0, None)(_lib.PL_register_foreign)
        #register_foreign = _lib.PL_register_foreign
        same_compound = _("PL_same_compound", [term_t, term_t], c_int)
        term_type = _("PL_term_type", [term_t], c_int)
        unify_arg = _("PL_unify_arg", [c_int, term_t, term_t], c_int)
        unify = _("PL_unify", [term_t, term_t], c_int)
        unify_integer = _("PL_unify_integer", [term_t, c_int_p], c_int)
        unregister_atom = _("PL_unregister_atom", [atom_t], None)

    Swipl.lib = Lib

    # create an exit hook which captures the exit code for our cleanup function
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
        if Lib.is_initialised(0, 0):
            # clean up the Prolog system using the caught exit code
            # if exit code is None, the program exits normally and we can use 0
            # instead.
            # TODO Prolog documentation says cleanup with code 0 may be interrupted
            # If the program has come to an end the prolog system should not
            # interfere with that. Therefore we may want to use 1 instead of 0.
            _lib.PL_cleanup(int(_hook.exit_code or 0))
            Swipl.lib = None

    return Lib


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
