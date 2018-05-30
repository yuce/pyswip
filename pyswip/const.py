from ctypes import c_void_p, c_wchar, c_long, c_uint

# PySWIP constants
PYSWIP_MAXSTR = 1024
c_int_p = c_void_p
c_long_p = c_void_p
c_double_p = c_void_p
c_uint_p = c_void_p

# constants (from SWI-Prolog.h)
# PL_unify_term() arguments
PL_VARIABLE = 1  # nothing
PL_ATOM = 2  # const char
PL_INTEGER = 3  # int
PL_FLOAT = 4  # double
PL_STRING = 5  # const char *
PL_TERM = 6  #
PL_NIL = 7
PL_LIST_PAIR = 9
PL_FUNCTOR = 10  # functor_t, arg ...
PL_LIST = 11  # length, arg ...
PL_CHARS = 12  # const char *
PL_POINTER = 13  # void *

PL_PARTIAL_LIST = 41
PL_CYCLIC_TERM = 42
PL_NOT_A_LIST = 43

#               /* PlArg::PlArg(text, type) */
#define PL_CODE_LIST     (14)       /* [ascii...] */
#define PL_CHAR_LIST     (15)       /* [h,e,l,l,o] */
#define PL_BOOL      (16)       /* PL_set_feature() */
#define PL_FUNCTOR_CHARS (17)       /* PL_unify_term() */
#define _PL_PREDICATE_INDICATOR (18)    /* predicate_t (Procedure) */
#define PL_SHORT     (19)       /* short */
#define PL_INT       (20)       /* int */
#define PL_LONG      (21)       /* long */
#define PL_DOUBLE    (22)       /* double */
#define PL_NCHARS    (23)       /* unsigned, const char * */
#define PL_UTF8_CHARS    (24)       /* const char * */
#define PL_UTF8_STRING   (25)       /* const char * */
#define PL_INT64     (26)       /* int64_t */
#define PL_NUTF8_CHARS   (27)       /* unsigned, const char * */
#define PL_NUTF8_CODES   (29)       /* unsigned, const char * */
#define PL_NUTF8_STRING  (30)       /* unsigned, const char * */
#define PL_NWCHARS   (31)       /* unsigned, const wchar_t * */
#define PL_NWCODES   (32)       /* unsigned, const wchar_t * */
#define PL_NWSTRING  (33)       /* unsigned, const wchar_t * */
#define PL_MBCHARS   (34)       /* const char * */
#define PL_MBCODES   (35)       /* const char * */
#define PL_MBSTRING  (36)       /* const char * */

#       /********************************
#       * NON-DETERMINISTIC CALL/RETURN *
#       *********************************/
#
#  Note 1: Non-deterministic foreign functions may also use the deterministic
#    return methods PL_succeed and PL_fail.
#
#  Note 2: The argument to PL_retry is a 30 bits signed integer (long).

PL_FIRST_CALL = 0
PL_CUTTED = 1
PL_REDO = 2

PL_FA_NOTRACE = 0x01  # foreign cannot be traced
PL_FA_TRANSPARENT = 0x02  # foreign is module transparent
PL_FA_NONDETERMINISTIC  = 0x04  # foreign is non-deterministic
PL_FA_VARARGS = 0x08  # call using t0, ac, ctx
PL_FA_CREF = 0x10  # Internal: has clause-reference */

#        /*******************************
#        *       CALL-BACK      *
#        *******************************/

PL_Q_DEBUG = 0x01  # = TRUE for backward compatibility
PL_Q_NORMAL = 0x02  # normal usage
PL_Q_NODEBUG =  0x04  # use this one
PL_Q_CATCH_EXCEPTION = 0x08  # handle exceptions in C
PL_Q_PASS_EXCEPTION = 0x10  # pass to parent environment
PL_Q_DETERMINISTIC = 0x20  # call was deterministic

#        /*******************************
#        *         BLOBS        *
#        *******************************/

#define PL_BLOB_MAGIC_B 0x75293a00  /* Magic to validate a blob-type */
#define PL_BLOB_VERSION 1       /* Current version */
#define PL_BLOB_MAGIC   (PL_BLOB_MAGIC_B|PL_BLOB_VERSION)

#define PL_BLOB_UNIQUE  0x01        /* Blob content is unique */
#define PL_BLOB_TEXT    0x02        /* blob contains text */
#define PL_BLOB_NOCOPY  0x04        /* do not copy the data */
#define PL_BLOB_WCHAR   0x08        /* wide character string */

#        /*******************************
#        *      CHAR BUFFERS    *
#        *******************************/

CVT_ATOM = 0x0001
CVT_STRING = 0x0002
CVT_LIST = 0x0004
CVT_INTEGER = 0x0008
CVT_FLOAT = 0x0010
CVT_VARIABLE = 0x0020
CVT_NUMBER = CVT_INTEGER | CVT_FLOAT
CVT_ATOMIC = CVT_NUMBER | CVT_ATOM | CVT_STRING
CVT_WRITE = 0x0040  # as of version 3.2.10
CVT_ALL = CVT_ATOMIC | CVT_LIST
CVT_MASK = 0x00ff

BUF_DISCARDABLE = 0x0000
BUF_RING = 0x0100
BUF_MALLOC = 0x0200

CVT_EXCEPTION = 0x10000  # throw exception on error

#                  /*******************************
#                  *             TYPES            *
#                  *******************************/
#
# typedef uintptr_t       atom_t;         /* Prolog atom */
# typedef uintptr_t       functor_t;      /* Name/arity pair */
# typedef void *          module_t;       /* Prolog module */
# typedef void *          predicate_t;    /* Prolog procedure */
# typedef void *          record_t;       /* Prolog recorded term */
# typedef uintptr_t       term_t;         /* opaque term handle */
# typedef uintptr_t       qid_t;          /* opaque query handle */
# typedef uintptr_t       PL_fid_t;       /* opaque foreign context handle */
# typedef void *          control_t;      /* non-deterministic control arg */
# typedef void *          PL_engine_t;    /* opaque engine handle */
# typedef uintptr_t       PL_atomic_t;    /* same a word */
# typedef uintptr_t       foreign_t;      /* return type of foreign functions */
# typedef wchar_t         pl_wchar_t;     /* Prolog wide character */
# typedef foreign_t       (*pl_function_t)(); /* foreign language functions */

atom_t = c_uint_p
functor_t = c_uint_p
module_t = c_void_p
predicate_t = c_void_p
record_t = c_void_p
term_t = c_uint_p
qid_t = c_uint_p
PL_fid_t = c_uint_p
fid_t = c_uint_p
control_t = c_void_p
PL_engine_t = c_void_p
PL_atomic_t = c_uint_p
foreign_t = c_uint_p
pl_wchar_t = c_wchar

# PL_initialise = _lib.PL_initialise
# PL_initialise = check_strings(None, 1)(PL_initialise)
# #PL_initialise.argtypes = [c_int, c_c??

# PL_open_foreign_frame = _lib.PL_open_foreign_frame
# PL_open_foreign_frame.restype = fid_t

# PL_new_term_ref = _lib.PL_new_term_ref
# PL_new_term_ref.restype = term_t

# PL_new_term_refs = _lib.PL_new_term_refs
# PL_new_term_refs.argtypes = [c_int]
# PL_new_term_refs.restype = term_t

# PL_chars_to_term = _lib.PL_chars_to_term
# PL_chars_to_term.argtypes = [c_char_p, term_t]
# PL_chars_to_term.restype = c_int

# PL_chars_to_term = check_strings(0, None)(PL_chars_to_term)

# PL_call = _lib.PL_call
# PL_call.argtypes = [term_t, module_t]
# PL_call.restype = c_int

# PL_call_predicate = _lib.PL_call_predicate
# PL_call_predicate.argtypes = [module_t, c_int, predicate_t, term_t]
# PL_call_predicate.restype = c_int

# PL_discard_foreign_frame = _lib.PL_discard_foreign_frame
# PL_discard_foreign_frame.argtypes = [fid_t]
# PL_discard_foreign_frame.restype = None

# PL_put_list_chars = _lib.PL_put_list_chars
# PL_put_list_chars.argtypes = [term_t, c_char_p]
# PL_put_list_chars.restype = c_int

# PL_put_list_chars = check_strings(1, None)(PL_put_list_chars)

# #PL_EXPORT(void)                PL_register_atom(atom_t a);
# PL_register_atom = _lib.PL_register_atom
# PL_register_atom.argtypes = [atom_t]
# PL_register_atom.restype = None

# #PL_EXPORT(void)                PL_unregister_atom(atom_t a);
# PL_unregister_atom = _lib.PL_unregister_atom
# PL_unregister_atom.argtypes = [atom_t]
# PL_unregister_atom.restype = None

# #PL_EXPORT(atom_t)      PL_functor_name(functor_t f);
# PL_functor_name = _lib.PL_functor_name
# PL_functor_name.argtypes = [functor_t]
# PL_functor_name.restype = atom_t

# #PL_EXPORT(int)         PL_functor_arity(functor_t f);
# PL_functor_arity = _lib.PL_functor_arity
# PL_functor_arity.argtypes = [functor_t]
# PL_functor_arity.restype = c_int

# #                       /* Get C-values from Prolog terms */
# #PL_EXPORT(int)         PL_get_atom(term_t t, atom_t *a);
# PL_get_atom = _lib.PL_get_atom
# PL_get_atom.argtypes = [term_t, POINTER(atom_t)]
# PL_get_atom.restype = c_int

# #PL_EXPORT(int)         PL_get_bool(term_t t, int *value);
# PL_get_bool = _lib.PL_get_bool
# PL_get_bool.argtypes = [term_t, POINTER(c_int)]
# PL_get_bool.restype = c_int

# #PL_EXPORT(int)         PL_get_atom_chars(term_t t, char **a);
# PL_get_atom_chars = _lib.PL_get_atom_chars  # FIXME
# PL_get_atom_chars.argtypes = [term_t, POINTER(c_char_p)]
# PL_get_atom_chars.restype = c_int

# PL_get_atom_chars = check_strings(None, 1)(PL_get_atom_chars)

# ##define PL_get_string_chars(t, s, l) PL_get_string(t,s,l)
# #                                       /* PL_get_string() is depricated */
# #PL_EXPORT(int)         PL_get_string(term_t t, char **s, size_t *len);
# PL_get_string = _lib.PL_get_string

# PL_get_string = check_strings(None, 1)(PL_get_string)

# PL_get_string_chars = PL_get_string
# #PL_get_string_chars.argtypes = [term_t, POINTER(c_char_p), c_int_p]

# #PL_EXPORT(int)         PL_get_chars(term_t t, char **s, unsigned int flags);
# PL_get_chars = _lib.PL_get_chars  # FIXME:

# PL_get_chars = check_strings(None, 1)(PL_get_chars)

# #PL_EXPORT(int)         PL_get_list_chars(term_t l, char **s,
# #                                         unsigned int flags);
# #PL_EXPORT(int)         PL_get_atom_nchars(term_t t, size_t *len, char **a);
# #PL_EXPORT(int)         PL_get_list_nchars(term_t l,
# #                                          size_t *len, char **s,
# #                                          unsigned int flags);
# #PL_EXPORT(int)         PL_get_nchars(term_t t,
# #                                     size_t *len, char **s,
# #                                     unsigned int flags);
# #PL_EXPORT(int)         PL_get_integer(term_t t, int *i);
# PL_get_integer = _lib.PL_get_integer
# PL_get_integer.argtypes = [term_t, POINTER(c_int)]
# PL_get_integer.restype = c_int

# #PL_EXPORT(int)         PL_get_long(term_t t, long *i);
# PL_get_long = _lib.PL_get_long
# PL_get_long.argtypes = [term_t, POINTER(c_long)]
# PL_get_long.restype = c_int

# #PL_EXPORT(int)         PL_get_pointer(term_t t, void **ptr);
# #PL_EXPORT(int)         PL_get_float(term_t t, double *f);
# PL_get_float = _lib.PL_get_float
# PL_get_float.argtypes = [term_t, c_double_p]
# PL_get_float.restype = c_int

# #PL_EXPORT(int)         PL_get_functor(term_t t, functor_t *f);
# PL_get_functor = _lib.PL_get_functor
# PL_get_functor.argtypes = [term_t, POINTER(functor_t)]
# PL_get_functor.restype = c_int

# #PL_EXPORT(int)         PL_get_name_arity(term_t t, atom_t *name, int *arity);
# PL_get_name_arity = _lib.PL_get_name_arity
# PL_get_name_arity.argtypes = [term_t, POINTER(atom_t), POINTER(c_int)]
# PL_get_name_arity.restype = c_int

# #PL_EXPORT(int)         PL_get_module(term_t t, module_t *module);
# #PL_EXPORT(int)         PL_get_arg(int index, term_t t, term_t a);
# PL_get_arg = _lib.PL_get_arg
# PL_get_arg.argtypes = [c_int, term_t, term_t]
# PL_get_arg.restype = c_int

# #PL_EXPORT(int)         PL_get_list(term_t l, term_t h, term_t t);
# #PL_EXPORT(int)         PL_get_head(term_t l, term_t h);
# PL_get_head = _lib.PL_get_head
# PL_get_head.argtypes = [term_t, term_t]
# PL_get_head.restype = c_int

# #PL_EXPORT(int)         PL_get_tail(term_t l, term_t t);
# PL_get_tail = _lib.PL_get_tail
# PL_get_tail.argtypes = [term_t, term_t]
# PL_get_tail.restype = c_int

# #PL_EXPORT(int)         PL_get_nil(term_t l);
# PL_get_nil = _lib.PL_get_nil
# PL_get_nil.argtypes = [term_t]
# PL_get_nil.restype = c_int

# #PL_EXPORT(int)         PL_get_term_value(term_t t, term_value_t *v);
# #PL_EXPORT(char *)      PL_quote(int chr, const char *data);

# PL_put_atom_chars = _lib.PL_put_atom_chars
# PL_put_atom_chars.argtypes = [term_t, c_char_p]
# PL_put_atom_chars.restype = c_int

# PL_put_atom_chars = check_strings(1, None)(PL_put_atom_chars)

# PL_atom_chars = _lib.PL_atom_chars
# PL_atom_chars.argtypes = [atom_t]
# PL_atom_chars.restype = c_char_p

# PL_predicate = _lib.PL_predicate
# PL_predicate.argtypes = [c_char_p, c_int, c_char_p]
# PL_predicate.restype = predicate_t

# PL_predicate = check_strings([0,2], None)(PL_predicate)

# PL_pred = _lib.PL_pred
# PL_pred.argtypes = [functor_t, module_t]
# PL_pred.restype = predicate_t

# PL_open_query = _lib.PL_open_query
# PL_open_query.argtypes = [module_t, c_int, predicate_t, term_t]
# PL_open_query.restype = qid_t

# PL_next_solution = _lib.PL_next_solution
# PL_next_solution.argtypes = [qid_t]
# PL_next_solution.restype = c_int

# PL_copy_term_ref = _lib.PL_copy_term_ref
# PL_copy_term_ref.argtypes = [term_t]
# PL_copy_term_ref.restype = term_t

# PL_get_list = _lib.PL_get_list
# PL_get_list.argtypes = [term_t, term_t, term_t]
# PL_get_list.restype = c_int

# PL_get_chars = _lib.PL_get_chars  # FIXME

# PL_close_query = _lib.PL_close_query
# PL_close_query.argtypes = [qid_t]
# PL_close_query.restype = None

# #void PL_cut_query(qid)
# PL_cut_query = _lib.PL_cut_query
# PL_cut_query.argtypes = [qid_t]
# PL_cut_query.restype = None

# PL_halt = _lib.PL_halt
# PL_halt.argtypes = [c_int]
# PL_halt.restype = None

# # PL_EXPORT(int)        PL_cleanup(int status);
# PL_cleanup = _lib.PL_cleanup
# PL_cleanup.restype = c_int

# PL_unify_integer = _lib.PL_unify_integer
# PL_unify = _lib.PL_unify
# PL_unify.restype = c_int

# #PL_EXPORT(int)          PL_unify_arg(int index, term_t t, term_t a) WUNUSED;
# PL_unify_arg = _lib.PL_unify_arg
# PL_unify_arg.argtypes = [c_int, term_t, term_t]
# PL_unify_arg.restype = c_int

# # Verify types

# PL_term_type = _lib.PL_term_type
# PL_term_type.argtypes = [term_t]
# PL_term_type.restype = c_int

# PL_is_variable = _lib.PL_is_variable
# PL_is_variable.argtypes = [term_t]
# PL_is_variable.restype = c_int

# PL_is_ground = _lib.PL_is_ground
# PL_is_ground.argtypes = [term_t]
# PL_is_ground.restype = c_int

# PL_is_atom = _lib.PL_is_atom
# PL_is_atom.argtypes = [term_t]
# PL_is_atom.restype = c_int

# PL_is_integer = _lib.PL_is_integer
# PL_is_integer.argtypes = [term_t]
# PL_is_integer.restype = c_int

# PL_is_string = _lib.PL_is_string
# PL_is_string.argtypes = [term_t]
# PL_is_string.restype = c_int

# PL_is_float = _lib.PL_is_float
# PL_is_float.argtypes = [term_t]
# PL_is_float.restype = c_int

# #PL_is_rational = _lib.PL_is_rational
# #PL_is_rational.argtypes = [term_t]
# #PL_is_rational.restype = c_int

# PL_is_compound = _lib.PL_is_compound
# PL_is_compound.argtypes = [term_t]
# PL_is_compound.restype = c_int

# PL_is_functor = _lib.PL_is_functor
# PL_is_functor.argtypes = [term_t, functor_t]
# PL_is_functor.restype = c_int

# PL_is_list = _lib.PL_is_list
# PL_is_list.argtypes = [term_t]
# PL_is_list.restype = c_int

# PL_is_atomic = _lib.PL_is_atomic
# PL_is_atomic.argtypes = [term_t]
# PL_is_atomic.restype = c_int

# PL_is_number = _lib.PL_is_number
# PL_is_number.argtypes = [term_t]
# PL_is_number.restype = c_int

# #                       /* Assign to term-references */
# #PL_EXPORT(void)                PL_put_variable(term_t t);
# PL_put_variable = _lib.PL_put_variable
# PL_put_variable.argtypes = [term_t]
# PL_put_variable.restype = None

# #PL_EXPORT(void)                PL_put_atom(term_t t, atom_t a);
# #PL_EXPORT(void)                PL_put_atom_chars(term_t t, const char *chars);
# #PL_EXPORT(void)                PL_put_string_chars(term_t t, const char *chars);
# #PL_EXPORT(void)                PL_put_list_chars(term_t t, const char *chars);
# #PL_EXPORT(void)                PL_put_list_codes(term_t t, const char *chars);
# #PL_EXPORT(void)                PL_put_atom_nchars(term_t t, size_t l, const char *chars);
# #PL_EXPORT(void)                PL_put_string_nchars(term_t t, size_t len, const char *chars);
# #PL_EXPORT(void)                PL_put_list_nchars(term_t t, size_t l, const char *chars);
# #PL_EXPORT(void)                PL_put_list_ncodes(term_t t, size_t l, const char *chars);
# #PL_EXPORT(void)                PL_put_integer(term_t t, long i);
# PL_put_integer = _lib.PL_put_integer
# PL_put_integer.argtypes = [term_t, c_long]
# PL_put_integer.restype = None

# #PL_EXPORT(void)                PL_put_pointer(term_t t, void *ptr);
# #PL_EXPORT(void)                PL_put_float(term_t t, double f);
# #PL_EXPORT(void)                PL_put_functor(term_t t, functor_t functor);
# PL_put_functor = _lib.PL_put_functor
# PL_put_functor.argtypes = [term_t, functor_t]
# PL_put_functor.restype = None

# #PL_EXPORT(void)                PL_put_list(term_t l);
# PL_put_list = _lib.PL_put_list
# PL_put_list.argtypes = [term_t]
# PL_put_list.restype = None

# #PL_EXPORT(void)                PL_put_nil(term_t l);
# PL_put_nil = _lib.PL_put_nil
# PL_put_nil.argtypes = [term_t]
# PL_put_nil.restype = None

# #PL_EXPORT(void)                PL_put_term(term_t t1, term_t t2);
# PL_put_term = _lib.PL_put_term
# PL_put_term.argtypes = [term_t, term_t]
# PL_put_term.restype = None

# #                       /* construct a functor or list-cell */
# #PL_EXPORT(void)                PL_cons_functor(term_t h, functor_t f, ...);
# #class _PL_cons_functor(object):
# PL_cons_functor = _lib.PL_cons_functor  # FIXME:

# #PL_EXPORT(void)                PL_cons_functor_v(term_t h, functor_t fd, term_t a0);
# PL_cons_functor_v = _lib.PL_cons_functor_v
# PL_cons_functor_v.argtypes = [term_t, functor_t, term_t]
# PL_cons_functor_v.restype = None

# #PL_EXPORT(void)                PL_cons_list(term_t l, term_t h, term_t t);
# PL_cons_list = _lib.PL_cons_list
# PL_cons_list.argtypes = [term_t, term_t, term_t]
# PL_cons_list.restype = None

# #
# # term_t PL_exception(qid_t qid)
# PL_exception = _lib.PL_exception
# PL_exception.argtypes = [qid_t]
# PL_exception.restype = term_t
# #
# PL_register_foreign = _lib.PL_register_foreign
# PL_register_foreign = check_strings(0, None)(PL_register_foreign)

# #
# #PL_EXPORT(atom_t)      PL_new_atom(const char *s);
# PL_new_atom = _lib.PL_new_atom
# PL_new_atom.argtypes = [c_char_p]
# PL_new_atom.restype = atom_t

# PL_new_atom = check_strings(0, None)(PL_new_atom)

# #PL_EXPORT(functor_t)   PL_new_functor(atom_t f, int a);
# PL_new_functor = _lib.PL_new_functor
# PL_new_functor.argtypes = [atom_t, c_int]
# PL_new_functor.restype = functor_t


# #                /*******************************
# #                *           COMPARE            *
# #                *******************************/
# #
# #PL_EXPORT(int)         PL_compare(term_t t1, term_t t2);
# #PL_EXPORT(int)         PL_same_compound(term_t t1, term_t t2);
# PL_compare = _lib.PL_compare
# PL_compare.argtypes = [term_t, term_t]
# PL_compare.restype = c_int

# PL_same_compound = _lib.PL_same_compound
# PL_same_compound.argtypes = [term_t, term_t]
# PL_same_compound.restype = c_int


# #                /*******************************
# #                *      RECORDED DATABASE       *
# #                *******************************/
# #
# #PL_EXPORT(record_t)    PL_record(term_t term);
# PL_record = _lib.PL_record
# PL_record.argtypes = [term_t]
# PL_record.restype = record_t

# #PL_EXPORT(void)                PL_recorded(record_t record, term_t term);
# PL_recorded = _lib.PL_recorded
# PL_recorded.argtypes = [record_t, term_t]
# PL_recorded.restype = None

# #PL_EXPORT(void)                PL_erase(record_t record);
# PL_erase = _lib.PL_erase
# PL_erase.argtypes = [record_t]
# PL_erase.restype = None

# #
# #PL_EXPORT(char *)      PL_record_external(term_t t, size_t *size);
# #PL_EXPORT(int)         PL_recorded_external(const char *rec, term_t term);
# #PL_EXPORT(int)         PL_erase_external(char *rec);

# PL_new_module = _lib.PL_new_module
# PL_new_module.argtypes = [atom_t]
# PL_new_module.restype = module_t

# PL_is_initialised = _lib.PL_is_initialised

intptr_t = c_long
ssize_t = intptr_t
wint_t = c_uint

# IOLOCK
IOLOCK = c_void_p
