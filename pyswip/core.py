# -*- coding: utf-8 -*-


# pyswip -- Python SWI-Prolog bridge
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


import os
import re
import sys
import glob
import warnings
from subprocess import Popen, PIPE
from ctypes import *
from ctypes.util import find_library


# To initialize the SWI-Prolog environment, two things need to be done: the
# first is to find where the SO/DLL is located and the second is to find the
# SWI-Prolog home, to get the saved state.
#
# The goal of the (entangled) process below is to make the library installation
# independent.


def _findSwiplPathFromFindLib():
    """
    This function resorts to ctype's find_library to find the path to the
    DLL. The biggest problem is that find_library does not give the path to the
    resource file.

    :returns:
        A path to the swipl SO/DLL or None if it is not found.

    :returns type:
        {str, None}
    """
    
    path = (find_library('swipl') or 
            find_library('pl') or 
            find_library('libswipl')) # This last one is for Windows
    return path
    

def _findSwiplFromExec():
    """
    This function tries to use an executable on the path to find SWI-Prolog
    SO/DLL and the resource file.

    :returns:
        A tuple of (path to the swipl DLL, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    platform = sys.platform[:3]
    
    fullName = None
    swiHome = None

    try: # try to get library path from swipl executable.
        
        # We may have pl or swipl as the executable
        try:
            cmd = Popen(['swipl', '-dump-runtime-variables'], stdout=PIPE)
        except OSError:
            cmd = Popen(['pl', '-dump-runtime-variables'], stdout=PIPE)
        ret = cmd.communicate()

        # Parse the output into a dictionary
        ret = ret[0].replace(';', '').splitlines()
        ret = [line.split('=', 1) for line in ret]
        rtvars = dict((name, value[1:-1]) for name, value in ret) # [1:-1] gets
                                                                  # rid of the
                                                                  # quotes

        if rtvars['PLSHARED'] == 'no':
            raise ImportError('SWI-Prolog is not installed as a shared '
                              'library.')
        else: # PLSHARED == 'yes'
            swiHome = rtvars['PLBASE']   # The environment is in PLBASE
            if not os.path.exists(swiHome):
                swiHome = None
            
            # determine platform specific path
            if platform == "win":
                dllName = rtvars['PLLIB'][:-4] + '.' + rtvars['PLSOEXT']
                path = os.path.join(rtvars['PLBASE'], 'bin')
                fullName = os.path.join(path, dllName)
                
                if not os.path.exists(fullName):
                    fullName = None

            elif platform == "cyg":
                # e.g. /usr/lib/pl-5.6.36/bin/i686-cygwin/cygpl.dll
                
                dllName = 'cygpl.dll'
                path = os.path.join(rtvars['PLBASE'], 'bin', rtvars['PLARCH'])
                fullName = os.path.join(path, dllName)
                
                if not os.path.exists(fullName):
                    fullName = None
                
            else: # assume UNIX-like
                # The SO name in some linuxes is of the form libswipl.so.5.10.2,
                # so we have to use glob to find the correct one
                dllName = 'lib' + rtvars['PLLIB'][2:] + '.' + rtvars['PLSOEXT']
                path = os.path.join(rtvars['PLBASE'], 'lib', rtvars['PLARCH'])
                baseName = os.path.join(path, dllName)

                if os.path.exists(baseName):
                    fullName = baseName
                else:  # We will search for versions
                    pattern = baseName + '.*'
                    files = glob.glob(pattern)
                    if len(files) == 0:
                        fullName = None
                    elif len(files) == 1:
                        fullName = files[0]
                    else:  # Will this ever happen?
                        fullName = None
                
    except (OSError, KeyError): # KeyError from accessing rtvars
        pass
    
    return (fullName, swiHome)
    

def _findSwiplWin():
    """
    This function uses several heuristics to gues where SWI-Prolog is installed
    in Windows. It always returns None as the path of the resource file because,
    in Windows, the way to find it is more robust so the SWI-Prolog DLL is
    always able to find it.

    :returns:
        A tuple of (path to the swipl DLL, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    dllNames = ('swipl.dll', 'libswipl.dll')

    # First try: check the usual installation path (this is faster but
    # hardcoded)
    programFiles = os.getenv('ProgramFiles')
    paths = [os.path.join(programFiles, r'pl\bin', dllName)
             for dllName in dllNames]
    for path in paths:
        if os.path.exists(path):
            return (path, None)

    # Second try: use the find_library
    path = _findSwiplPathFromFindLib()
    if path is not None and os.path.exists(path):
        return (path, None)
    
    # Third try: use reg.exe to find the installation path in the registry
    # (reg should be installed in all Windows XPs)
    try:
        cmd = Popen(['reg', 'query', 
            r'HKEY_LOCAL_MACHINE\Software\SWI\Prolog', 
            '/v', 'home'], stdout=PIPE)
        ret = cmd.communicate()

        # Result is like:
        # ! REG.EXE VERSION 3.0
        #
        # HKEY_LOCAL_MACHINE\Software\SWI\Prolog
        #    home        REG_SZ  C:\Program Files\pl
        # (Note: spaces may be \t or spaces in the output)
        ret = ret[0].splitlines()
        ret = [line for line in ret if len(line) > 0]
        pattern = re.compile('[^h]*home[^R]*REG_SZ( |\t)*(.*)$')
        match = pattern.match(ret[-1])
        if match is not None:
            path = match.group(2)
            
            paths = [os.path.join(path, 'bin', dllName)
                     for dllName in dllNames]
            for path in paths:
                if os.path.exists(path):
                    return (path, None)
            
    except OSError:
        # reg.exe not found? Weird...
        pass

    # May the exec is on path?
    (path, swiHome) = _findSwiplFromExec()
    if path is not None:
        return (path, swiHome)
    
    # Last try: maybe it is in the current dir
    for dllName in dllNames:
        if os.path.exists(dllName):
            return (dllName, None)

    return (None, None)
    
def _findSwiplLin():
    """
    This function uses several heuristics to guess where SWI-Prolog is
    installed in Linuxes.

    :returns:
        A tuple of (path to the swipl so, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    # May the exec is on path?
    (path, swiHome) = _findSwiplFromExec()
    if path is not None:
        return (path, swiHome)

    # If it is not, use  find_library
    path = _findSwiplPathFromFindLib()
    if path is not None:
        return (path, swiHome)
    
    # Our last try: some hardcoded paths.
    paths = ['/lib', '/usr/lib', '/usr/local/lib', '.', './lib']
    names = ['libswipl.so', 'libpl.so']

    path = None
    for name in names:
        for try_ in paths:
            try_ = os.path.join(try_, name)
            if os.path.exists(try_):
                path = try_
                break
            
    if path is not None:
        return (path, swiHome)
    
    return (None, None)

    
def _findSwiplDar():
    """
    This function uses several heuristics to gues where SWI-Prolog is
    installed in MacOS.

    :returns:
        A tuple of (path to the swipl so, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    # Help with MacOS is welcome!!
    paths = ['.', './lib']
    names = ['libswipl.dylib', 'libpl.dylib']

    for name in names:
        for path in paths:
            path = os.path.join(path, name)
            if os.path.exists(path):
                return (path, None)

    return (None, None)


def _findSwipl():
    """
    This function makes a big effort to find the path to the SWI-Prolog shared
    library. Since this is both OS dependent and installation dependent, we may
    not aways succeed. If we do, we return a name/path that can be used by
    CDLL(). Otherwise we raise an exception.

    :return: Tuple. Fist element is the name or path to the library that can be
             used by CDLL. Second element is the path were SWI-Prolog resource
             file may be found (this is needed in some Linuxes)
    :rtype: Tuple of strings
    :raises ImportError: If we cannot guess the name of the library
    """

    # Now begins the guesswork
    platform = sys.platform[:3]
    if platform == "win": # In Windows, we have the default installer
                                   # path and the registry to look
        (path, swiHome) = _findSwiplWin()
                          
    elif platform in ("lin", "cyg"):
        (path, swiHome) = _findSwiplLin()
                
    elif platform == "dar":  # Help with MacOS is welcome!!
        (path, swiHome) = _findSwiplDar()

    else:
        raise EnvironmentError('The platform %s is not supported by this '
                               'library. If you want it to be supported, '
                               'please open an issue.' % platform)

    # This is a catch all raise
    if path is None:
        raise ImportError('Could not find the SWI-Prolog library in this '
                          'platform. If you are sure it is installed, please '
                          'open an issue.')
    else:
        return (path, swiHome)

    
def _fixWindowsPath(dll):
    """
    When the path to the DLL is not in Windows search path, Windows will not be
    able to find other DLLs on the same directory, so we have to add it to the
    path. This function takes care of it.

    :parameters:
      -  `dll` (str) - File name of the DLL
    """

    if sys.platform[:3] != 'win':
        return # Nothing to do here

    pathToDll = os.path.dirname(dll)
    currentWindowsPath = os.getenv('PATH')
    
    if pathToDll not in currentWindowsPath:
        # We will prepend the path, to avoid conflicts between DLLs
        newPath = pathToDll + ';' + currentWindowsPath
        os.putenv('PATH', newPath)

        
class c_void(Structure):
    _fields_ = [('dummy', c_int)]

    
c_void_p = POINTER(c_void)

# Find the path and resource file. SWI_HOME_DIR shall be treated as a constant
# by users of this module
(_path, SWI_HOME_DIR) = _findSwipl()
_fixWindowsPath(_path)

# Load the library
_lib = CDLL(_path)

# PySWIP constants
PYSWIP_MAXSTR = 1024
c_int_p = POINTER(c_int)
c_long_p = POINTER(c_long)
c_double_p = POINTER(c_double)
    
# constants (from SWI-Prolog.h)
# PL_unify_term() arguments
PL_VARIABLE = 1  # nothing 
PL_ATOM = 2  # const char
PL_INTEGER = 3  # int
PL_FLOAT = 4  # double
PL_STRING = 5  # const char *
PL_TERM = 6  #
# PL_unify_term()
PL_FUNCTOR = 10  # functor_t, arg ...
PL_LIST = 11  # length, arg ...
PL_CHARS = 12  # const char *
PL_POINTER = 13  # void *
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
    
argv = (c_char_p*(len(sys.argv) + 1))()
for i, arg in enumerate(sys.argv):
    argv[i] = arg
    
argv[-1] = None
argc = len(sys.argv)

# types

atom_t = c_ulong
term_t = c_ulong
fid_t = c_ulong
module_t = c_void_p
predicate_t = c_void_p
record_t = c_void_p
qid_t = c_ulong
PL_fid_t = c_ulong
control_t = c_void_p
PL_engine_t = c_void_p
functor_t = c_ulong
PL_atomic_t = c_ulong
foreign_t = c_ulong
pl_wchar_t = c_wchar


##_lib.PL_initialise(len(sys.argv), _argv)

PL_initialise = _lib.PL_initialise
##PL_initialise.argtypes = [c_int, c_c

PL_open_foreign_frame = _lib.PL_open_foreign_frame
PL_open_foreign_frame.restype = fid_t

PL_new_term_ref = _lib.PL_new_term_ref
PL_new_term_ref.restype = term_t

PL_new_term_refs = _lib.PL_new_term_refs
PL_new_term_refs.restype = term_t

PL_chars_to_term = _lib.PL_chars_to_term
PL_chars_to_term.argtypes = [c_char_p, term_t]

PL_call = _lib.PL_call
PL_call.argtypes = [term_t, module_t]

PL_call_predicate = _lib.PL_call_predicate
PL_call_predicate.argtypes = [module_t, c_int, predicate_t, term_t]

PL_discard_foreign_frame = _lib.PL_discard_foreign_frame
PL_discard_foreign_frame.argtypes = [fid_t]

PL_put_list_chars = _lib.PL_put_list_chars
PL_put_list_chars.argtypes = [term_t, c_char_p]

#PL_EXPORT(void)		PL_register_atom(atom_t a);
PL_register_atom = _lib.PL_register_atom

#PL_EXPORT(void)		PL_unregister_atom(atom_t a);
PL_unregister_atom = _lib.PL_unregister_atom

#PL_EXPORT(atom_t)	PL_functor_name(functor_t f);
PL_functor_name = _lib.PL_functor_name

#PL_EXPORT(int)		PL_functor_arity(functor_t f);
PL_functor_arity = _lib.PL_functor_arity

#			/* Get C-values from Prolog terms */
#PL_EXPORT(int)		PL_get_atom(term_t t, atom_t *a);
PL_get_atom = _lib.PL_get_atom
PL_get_atom.argtypes = [term_t, c_ulong]

#PL_EXPORT(int)		PL_get_bool(term_t t, int *value);
PL_get_bool = _lib.PL_get_bool

#PL_EXPORT(int)		PL_get_atom_chars(term_t t, char **a);
PL_get_atom_chars = _lib.PL_get_atom_chars  # FIXME

##define PL_get_string_chars(t, s, l) PL_get_string(t,s,l)
#					/* PL_get_string() is depricated */
#PL_EXPORT(int)		PL_get_string(term_t t, char **s, size_t *len);
PL_get_string = _lib.PL_get_string
PL_get_string_chars = PL_get_string
#PL_get_string_chars.argtypes = [term_t, POINTER(c_char_p), c_int_p]

#PL_EXPORT(int)		PL_get_chars(term_t t, char **s, unsigned int flags);
PL_get_chars = _lib.PL_get_chars  # FIXME:

#PL_EXPORT(int)		PL_get_list_chars(term_t l, char **s,
#					  unsigned int flags);
#PL_EXPORT(int)		PL_get_atom_nchars(term_t t, size_t *len, char **a);
#PL_EXPORT(int)		PL_get_list_nchars(term_t l,
#					   size_t *len, char **s,
#					   unsigned int flags);
#PL_EXPORT(int)		PL_get_nchars(term_t t,
#				      size_t *len, char **s,
#				      unsigned int flags);
#PL_EXPORT(int)		PL_get_integer(term_t t, int *i);
PL_get_integer = _lib.PL_get_integer

#PL_get_integer.argtypes = [term_t, c_int_p]

#PL_EXPORT(int)		PL_get_long(term_t t, long *i);
PL_get_long = _lib.PL_get_long

#PL_get_long.argtypes = [term_t, c_long_p]

#PL_EXPORT(int)		PL_get_pointer(term_t t, void **ptr);
#PL_EXPORT(int)		PL_get_float(term_t t, double *f);
PL_get_float = _lib.PL_get_float

#PL_get_float.argtypes = [term_t, c_double_p]

#PL_EXPORT(int)		PL_get_functor(term_t t, functor_t *f);
PL_get_functor = _lib.PL_get_functor
PL_get_functor.argtypes = [term_t, c_ulong]
#PL_get_functor.argtypes = [term_t, POINTER(functor_t)]

#PL_EXPORT(int)		PL_get_name_arity(term_t t, atom_t *name, int *arity);
PL_get_name_arity = _lib.PL_get_name_arity

#PL_EXPORT(int)		PL_get_module(term_t t, module_t *module);
#PL_EXPORT(int)		PL_get_arg(int index, term_t t, term_t a);
PL_get_arg = _lib.PL_get_arg

#PL_EXPORT(int)		PL_get_list(term_t l, term_t h, term_t t);
#PL_EXPORT(int)		PL_get_head(term_t l, term_t h);
PL_get_head = _lib.PL_get_head
#PL_EXPORT(int)		PL_get_tail(term_t l, term_t t);
PL_get_tail = _lib.PL_get_tail
#PL_EXPORT(int)		PL_get_nil(term_t l);
PL_get_nil = _lib.PL_get_nil
#PL_EXPORT(int)		PL_get_term_value(term_t t, term_value_t *v);
#PL_EXPORT(char *)	PL_quote(int chr, const char *data);

PL_put_atom_chars = _lib.PL_put_atom_chars
PL_put_atom_chars.argtypes = [term_t, c_char_p]

PL_atom_chars = _lib.PL_atom_chars
PL_atom_chars.argtypes = [atom_t]
PL_atom_chars.restype = c_char_p

PL_predicate = _lib.PL_predicate
PL_predicate.argtypes = [c_char_p, c_int, c_char_p]
PL_predicate.restype = predicate_t

PL_pred = _lib.PL_pred
PL_pred.argtypes = [functor_t, module_t]
PL_pred.restype = predicate_t

PL_open_query = _lib.PL_open_query
PL_open_query.argtypes = [module_t, c_int, predicate_t, term_t]
PL_open_query.restype = qid_t

PL_next_solution = _lib.PL_next_solution
PL_next_solution.argtypes = [qid_t]

PL_copy_term_ref = _lib.PL_copy_term_ref
PL_copy_term_ref.argtypes = [term_t]
PL_copy_term_ref.restype = term_t

PL_get_list = _lib.PL_get_list
PL_get_list.argtypes = [term_t, term_t, term_t]

PL_get_chars = _lib.PL_get_chars  # FIXME

PL_close_query = _lib.PL_close_query
PL_close_query.argtypes = [qid_t]

#void PL_cut_query(qid)
PL_cut_query = _lib.PL_cut_query
PL_cut_query.argtypes = [qid_t]

PL_halt = _lib.PL_halt
PL_halt.argtypes = [c_int]

# PL_EXPORT(int)        PL_cleanup(int status);
PL_cleanup = _lib.PL_cleanup


PL_unify_integer = _lib.PL_unify_integer
PL_unify = _lib.PL_unify

PL_unify_arg = _lib.PL_unify_arg

# Verify types

PL_term_type = _lib.PL_term_type
PL_term_type.argtypes = [term_t]
PL_term_type.restype = c_int

PL_is_variable = _lib.PL_is_variable
PL_is_variable.argtypes = [term_t]
PL_is_variable.restype = c_int

PL_is_ground = _lib.PL_is_ground
PL_is_ground.argtypes = [term_t]
PL_is_ground.restype = c_int

PL_is_atom = _lib.PL_is_atom
PL_is_atom.argtypes = [term_t]
PL_is_atom.restype = c_int

PL_is_integer = _lib.PL_is_integer
PL_is_integer.argtypes = [term_t]
PL_is_integer.restype = c_int

PL_is_string = _lib.PL_is_string
PL_is_string.argtypes = [term_t]
PL_is_string.restype = c_int

PL_is_float = _lib.PL_is_float
PL_is_float.argtypes = [term_t]
PL_is_float.restype = c_int

#PL_is_rational = _lib.PL_is_rational
#PL_is_rational.argtypes = [term_t]
#PL_is_rational.restype = c_int

PL_is_compound = _lib.PL_is_compound
PL_is_compound.argtypes = [term_t]
PL_is_compound.restype = c_int

PL_is_functor = _lib.PL_is_functor
PL_is_functor.argtypes = [term_t, functor_t]
PL_is_functor.restype = c_int

PL_is_list = _lib.PL_is_list
PL_is_list.argtypes = [term_t]
PL_is_list.restype = c_int

PL_is_atomic = _lib.PL_is_atomic
PL_is_atomic.argtypes = [term_t]
PL_is_atomic.restype = c_int

PL_is_number = _lib.PL_is_number
PL_is_number.argtypes = [term_t]
PL_is_number.restype = c_int

#			/* Assign to term-references */
#PL_EXPORT(void)		PL_put_variable(term_t t);
PL_put_variable = _lib.PL_put_variable
#PL_EXPORT(void)		PL_put_atom(term_t t, atom_t a);
#PL_EXPORT(void)		PL_put_atom_chars(term_t t, const char *chars);
#PL_EXPORT(void)		PL_put_string_chars(term_t t, const char *chars);
#PL_EXPORT(void)		PL_put_list_chars(term_t t, const char *chars);
#PL_EXPORT(void)		PL_put_list_codes(term_t t, const char *chars);
#PL_EXPORT(void)		PL_put_atom_nchars(term_t t, size_t l, const char *chars);
#PL_EXPORT(void)		PL_put_string_nchars(term_t t, size_t len, const char *chars);
#PL_EXPORT(void)		PL_put_list_nchars(term_t t, size_t l, const char *chars);
#PL_EXPORT(void)		PL_put_list_ncodes(term_t t, size_t l, const char *chars);
#PL_EXPORT(void)		PL_put_integer(term_t t, long i);
PL_put_integer = _lib.PL_put_integer
PL_put_integer.argtypes = [term_t, c_long]
PL_put_integer.restype = None
#PL_EXPORT(void)		PL_put_pointer(term_t t, void *ptr);
#PL_EXPORT(void)		PL_put_float(term_t t, double f);
#PL_EXPORT(void)		PL_put_functor(term_t t, functor_t functor);
PL_put_functor = _lib.PL_put_functor
#PL_EXPORT(void)		PL_put_list(term_t l);
PL_put_list = _lib.PL_put_list
#PL_EXPORT(void)		PL_put_nil(term_t l);
PL_put_nil = _lib.PL_put_nil
#PL_EXPORT(void)		PL_put_term(term_t t1, term_t t2);
PL_put_term = _lib.PL_put_term

#			/* construct a functor or list-cell */
#PL_EXPORT(void)		PL_cons_functor(term_t h, functor_t f, ...);
#class _PL_cons_functor(object):
PL_cons_functor = _lib.PL_cons_functor  # FIXME:
    
#PL_EXPORT(void)		PL_cons_functor_v(term_t h, functor_t fd, term_t a0);
PL_cons_functor_v = _lib.PL_cons_functor_v
PL_cons_functor_v.argtypes = [term_t, functor_t, term_t]
PL_cons_functor_v.restype = None

#PL_EXPORT(void)		PL_cons_list(term_t l, term_t h, term_t t);
PL_cons_list = _lib.PL_cons_list

#
# term_t PL_exception(qid_t qid)
PL_exception = _lib.PL_exception
PL_exception.argtypes = [qid_t]
PL_exception.restype = term_t
#
PL_register_foreign = _lib.PL_register_foreign

#
#PL_EXPORT(atom_t)	PL_new_atom(const char *s);
PL_new_atom = _lib.PL_new_atom
PL_new_atom.argtypes = [c_char_p]
PL_new_atom.restype = atom_t

#PL_EXPORT(functor_t)	PL_new_functor(atom_t f, int a);
PL_new_functor = _lib.PL_new_functor
PL_new_functor.argtypes = [atom_t, c_int]
PL_new_functor.restype = functor_t

#		 /*******************************
#		 *      RECORDED DATABASE	*
#		 *******************************/
#
#PL_EXPORT(record_t)	PL_record(term_t term);
PL_record = _lib.PL_record

#PL_EXPORT(void)		PL_recorded(record_t record, term_t term);
PL_recorded = _lib.PL_recorded

#PL_EXPORT(void)		PL_erase(record_t record);
PL_erase = _lib.PL_erase
#
#PL_EXPORT(char *)	PL_record_external(term_t t, size_t *size);
#PL_EXPORT(int)		PL_recorded_external(const char *rec, term_t term);
#PL_EXPORT(int)		PL_erase_external(char *rec);

PL_new_module = _lib.PL_new_module
PL_new_module.argtypes = [atom_t]
PL_new_module.restype = module_t

intptr_t = c_long
ssize_t = intptr_t
wint_t = c_uint

#typedef struct
#{
#  int __count;
#  union
#  {
#    wint_t __wch;
#    char __wchb[4];
#  } __value;            /* Value so far.  */
#} __mbstate_t;

class _mbstate_t_value(Union):
    _fields_ = [("__wch",wint_t),
                ("__wchb",c_char*4)]

class mbstate_t(Structure):
    _fields_ = [("__count",c_int),
                ("__value",_mbstate_t_value)]

# stream related funcs
Sread_function = CFUNCTYPE(ssize_t, c_void_p, c_char_p, c_size_t)
Swrite_function = CFUNCTYPE(ssize_t, c_void_p, c_char_p, c_size_t)
Sseek_function = CFUNCTYPE(c_long, c_void_p, c_long, c_int)
Sseek64_function = CFUNCTYPE(c_int64, c_void_p, c_int64, c_int)
Sclose_function = CFUNCTYPE(c_int, c_void_p)
Scontrol_function = CFUNCTYPE(c_int, c_void_p, c_int, c_void_p)

# IOLOCK
IOLOCK = c_void_p

# IOFUNCTIONS
class IOFUNCTIONS(Structure):
    _fields_ = [("read",Sread_function),
                ("write",Swrite_function),
                ("seek",Sseek_function),
                ("close",Sclose_function),
                ("seek64",Sseek64_function),
                ("reserved",intptr_t*2)]

# IOENC
ENC_UNKNOWN,ENC_OCTET,ENC_ASCII,ENC_ISO_LATIN_1,ENC_ANSI,ENC_UTF8,ENC_UNICODE_BE,ENC_UNICODE_LE,ENC_WCHAR = range(9)
IOENC = c_int

# IOPOS
class IOPOS(Structure):
    _fields_ = [("byteno",c_int64),
                ("charno",c_int64),
                ("lineno",c_int),
                ("linepos",c_int),
                ("reserved", intptr_t*2)]

# IOSTREAM
class IOSTREAM(Structure):
    _fields_ = [("bufp",c_char_p),
                ("limitp",c_char_p),
                ("buffer",c_char_p),
                ("unbuffer",c_char_p),
                ("lastc",c_int),
                ("magic",c_int),
                ("bufsize",c_int),
                ("flags",c_int),
                ("posbuf",IOPOS),
                ("position",POINTER(IOPOS)),
                ("handle",c_void_p),
                ("functions",IOFUNCTIONS),
                ("locks",c_int),
                ("mutex",IOLOCK),
                ("closure_hook",CFUNCTYPE(None, c_void_p)),
                ("closure",c_void_p),
                ("timeout",c_int),
                ("message",c_char_p),
                ("encoding",IOENC)]
IOSTREAM._fields_.extend([("tee",IOSTREAM),
                ("mbstate",POINTER(mbstate_t)),
                ("reserved",intptr_t*6)])



#PL_EXPORT(IOSTREAM *)	Sopen_string(IOSTREAM *s, char *buf, size_t sz, const char *m);
Sopen_string = _lib.Sopen_string
Sopen_string.argtypes = [POINTER(IOSTREAM), c_char_p, c_size_t, c_char_p]
Sopen_string.restype = POINTER(IOSTREAM)

#PL_EXPORT(int)		Sclose(IOSTREAM *s);
Sclose = _lib.Sclose
Sclose.argtypes = [POINTER(IOSTREAM)]


#PL_EXPORT(int)  	PL_unify_stream(term_t t, IOSTREAM *s);
PL_unify_stream = _lib.PL_unify_stream
PL_unify_stream.argtypes = [term_t, POINTER(IOSTREAM)]

