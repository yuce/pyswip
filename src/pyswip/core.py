# -*- coding: utf-8 -*-


# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2018 Yüce Tekol
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

from __future__ import print_function

import atexit
import glob
import os
import sys
from contextlib import contextmanager
from ctypes import *
from ctypes.util import find_library
from subprocess import Popen, PIPE


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

    path = (
        find_library("swipl") or find_library("pl") or find_library("libswipl")
    )  # This last one is for Windows
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

    try:  # try to get library path from swipl executable.
        # We may have pl or swipl as the executable
        cmd = Popen(["swipl", "--dump-runtime-variables"], stdout=PIPE)
        ret = cmd.communicate()

        # Parse the output into a dictionary
        ret = ret[0].decode().replace(";", "").splitlines()
        ret = [line.split("=", 1) for line in ret]
        rtvars = dict((name, value[1:-1]) for name, value in ret)  # [1:-1] gets
        # rid of the
        # quotes

        if rtvars["PLSHARED"] == "no":
            raise ImportError("SWI-Prolog is not installed as a shared " "library.")
        else:  # PLSHARED == 'yes'
            swiHome = rtvars["PLBASE"]  # The environment is in PLBASE
            if not os.path.exists(swiHome):
                swiHome = None

            # determine platform specific path.  First try runtime
            # variable `PLLIBSWIPL` introduced in 9.1.1/9.0.1
            if "PLLIBSWIPL" in rtvars:
                fullName = rtvars["PLLIBSWIPL"]
            # determine platform specific path
            elif platform == "win":
                dllName = rtvars["PLLIB"][:-4] + "." + rtvars["PLSOEXT"]
                path = os.path.join(rtvars["PLBASE"], "bin")
                fullName = os.path.join(path, dllName)

                if not os.path.exists(fullName):
                    fullName = None

            elif platform == "cyg":
                # e.g. /usr/lib/pl-5.6.36/bin/i686-cygwin/cygpl.dll

                dllName = "cygpl.dll"
                path = os.path.join(rtvars["PLBASE"], "bin", rtvars["PLARCH"])
                fullName = os.path.join(path, dllName)

                if not os.path.exists(fullName):
                    fullName = None

            elif platform == "dar":
                dllName = "lib" + rtvars["PLLIB"][2:] + "." + "dylib"
                path = os.path.join(rtvars["PLBASE"], "lib", rtvars["PLARCH"])
                baseName = os.path.join(path, dllName)

                if os.path.exists(baseName):
                    fullName = baseName
                else:  # We will search for versions
                    fullName = None

            else:  # assume UNIX-like
                # The SO name in some linuxes is of the form libswipl.so.5.10.2,
                # so we have to use glob to find the correct one
                dllName = "lib" + rtvars["PLLIB"][2:] + "." + rtvars["PLSOEXT"]
                path = os.path.join(rtvars["PLBASE"], "lib", rtvars["PLARCH"])
                baseName = os.path.join(path, dllName)

                if os.path.exists(baseName):
                    fullName = baseName
                else:  # We will search for versions
                    pattern = baseName + ".*"
                    files = glob.glob(pattern)
                    if len(files) == 0:
                        fullName = None
                    else:
                        fullName = files[0]

    except (OSError, KeyError):  # KeyError from accessing rtvars
        pass

    return (fullName, swiHome)


def _findSwiplWin():
    import re

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

    dllNames = ("swipl.dll", "libswipl.dll")

    # First try: check the usual installation path (this is faster but
    # hardcoded)
    programFiles = os.getenv("ProgramFiles")
    paths = [os.path.join(programFiles, r"pl\bin", dllName) for dllName in dllNames]
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
        cmd = Popen(
            ["reg", "query", r"HKEY_LOCAL_MACHINE\Software\SWI\Prolog", "/v", "home"],
            stdout=PIPE,
        )
        ret = cmd.communicate()

        # Result is like:
        # ! REG.EXE VERSION 3.0
        #
        # HKEY_LOCAL_MACHINE\Software\SWI\Prolog
        #    home        REG_SZ  C:\Program Files\pl
        # (Note: spaces may be \t or spaces in the output)
        ret = ret[0].splitlines()
        ret = [line.decode("utf-8") for line in ret if len(line) > 0]
        pattern = re.compile("[^h]*home[^R]*REG_SZ( |\t)*(.*)$")
        match = pattern.match(ret[-1])
        if match is not None:
            path = match.group(2)

            paths = [os.path.join(path, "bin", dllName) for dllName in dllNames]
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

    # Maybe the exec is on path?
    (path, swiHome) = _findSwiplFromExec()
    if path is not None:
        return (path, swiHome)

    # If it is not, use  find_library
    path = _findSwiplPathFromFindLib()
    if path is not None:
        return (path, swiHome)

    # Our last try: some hardcoded paths.
    paths = [
        "/lib",
        "/usr/lib",
        "/usr/local/lib",
        ".",
        "./lib",
        "/usr/lib/swi-prolog/lib/x86_64-linux",
    ]
    names = ["libswipl.so", "libpl.so"]

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


def walk(path, name):
    """
    This function is a 2-time recursive func,
    that findin file in dirs

    :parameters:
      -  `path` (str) - Directory path
      -  `name` (str) - Name of file, that we lookin for

    :returns:
        Path to the swipl so, path to the resource file

    :returns type:
        (str)
    """
    back_path = path[:]
    path = os.path.join(path, name)

    if os.path.exists(path):
        return path
    else:
        for dir_ in os.listdir(back_path):
            path = os.path.join(back_path, dir_)

            if os.path.isdir(path):
                res_path = walk(path, name)
                if res_path is not None:
                    return (res_path, back_path)

    return None


def _findSwiplMacOSHome():
    """
    This function is guesing where SWI-Prolog is
    installed in MacOS via .app.

    :parameters:
      -  `swi_ver` (str) - Version of SWI-Prolog in '[0-9].[0-9].[0-9]' format

    :returns:
        A tuple of (path to the swipl so, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    # Need more help with MacOS
    # That way works, but need more work
    names = ["libswipl.dylib", "libpl.dylib"]

    path = os.environ.get("SWI_HOME_DIR")
    if path is None:
        path = os.environ.get("SWI_LIB_DIR")
        if path is None:
            path = os.environ.get("PLBASE")
            if path is None:
                path = "/Applications/SWI-Prolog.app/Contents/"

    paths = [path]

    for name in names:
        for path in paths:
            (path_res, back_path) = walk(path, name)

            if path_res is not None:
                os.environ["SWI_LIB_DIR"] = back_path
                return (path_res, None)

    return (None, None)


def _findSwiplDar():
    """
    This function uses several heuristics to guess where SWI-Prolog is
    installed in MacOS.

    :returns:
        A tuple of (path to the swipl so, path to the resource file)

    :returns type:
        ({str, None}, {str, None})
    """

    # If the exec is in path
    (path, swiHome) = _findSwiplFromExec()
    if path is not None:
        return (path, swiHome)

    # If it is not, use  find_library
    path = _findSwiplPathFromFindLib()
    if path is not None:
        return (path, swiHome)

    # Last guess, searching for the file
    paths = [".", "./lib", "/usr/lib/", "/usr/local/lib", "/opt/local/lib"]
    names = ["libswipl.dylib", "libpl.dylib"]

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
    # check environment
    if "LIBSWIPL_PATH" in os.environ:
        return (os.environ["LIBSWIPL_PATH"], os.environ.get("SWI_HOME_DIR"))

    # Now begins the guesswork
    platform = sys.platform[:3]
    if platform == "win":  # In Windows, we have the default installer
        # path and the registry to look
        (path, swiHome) = _findSwiplWin()

    elif platform in ("lin", "cyg"):
        (path, swiHome) = _findSwiplLin()

    elif platform == "dar":  # Help with MacOS is welcome!!
        (path, swiHome) = _findSwiplDar()

        if path is None:
            (path, swiHome) = _findSwiplMacOSHome()

    else:
        # This should work for other UNIX
        (path, swiHome) = _findSwiplLin()

    # This is a catch all raise
    if path is None:
        raise ImportError(
            "Could not find the SWI-Prolog library in this "
            "platform. If you are sure it is installed, please "
            "open an issue."
        )
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

    if sys.platform[:3] != "win":
        return  # Nothing to do here

    pathToDll = os.path.dirname(dll)
    currentWindowsPath = os.getenv("PATH")

    if pathToDll not in currentWindowsPath:
        # We will prepend the path, to avoid conflicts between DLLs
        newPath = pathToDll + ";" + currentWindowsPath
        os.putenv("PATH", newPath)


_stringMap = {}


def str_to_bytes(string):
    """
    Turns a string into a bytes if necessary (i.e. if it is not already a bytes
    object or None).
    If string is None, int or c_char_p it will be returned directly.

    :param string: The string that shall be transformed
    :type string: str, bytes or type(None)
    :return: Transformed string
    :rtype: c_char_p compatible object (bytes, c_char_p, int or None)
    """
    if string is None or isinstance(string, (int, c_char_p)):
        return string

    if not isinstance(string, bytes):
        if string not in _stringMap:
            _stringMap[string] = string.encode()
        string = _stringMap[string]

    return string


def list_to_bytes_list(strList):
    """
    This function turns an array of strings into a pointer array
    with pointers pointing to the encodings of those strings
    Possibly contained bytes are kept as they are.

    :param strList: List of strings that shall be converted
    :type strList: List of strings
    :returns: Pointer array with pointers pointing to bytes
    :raises: TypeError if strList is not list, set or tuple
    """
    pList = c_char_p * len(strList)

    # if strList is already a pointerarray or None, there is nothing to do
    if isinstance(strList, (pList, type(None))):
        return strList

    if not isinstance(strList, (list, set, tuple)):
        raise TypeError("strList must be list, set or tuple, not " + str(type(strList)))

    pList = pList()
    for i, elem in enumerate(strList):
        pList[i] = str_to_bytes(elem)
    return pList


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
    for i, k in enumerate(strings):
        if not isinstance(k, int):
            raise TypeError(
                (
                    "Wrong type for index at {0} " + "in strings. Must be int, not {1}!"
                ).format(i, k)
            )

    # if given a single element, turn it into a list
    if isinstance(arrays, int):
        arrays = [arrays]
    elif arrays is None:
        arrays = []

    # check if all entries are integers
    for i, k in enumerate(arrays):
        if not isinstance(k, int):
            raise TypeError(
                (
                    "Wrong type for index at {0} " + "in arrays. Must be int, not {1}!"
                ).format(i, k)
            )

    # check if some index occurs in both
    if set(strings).intersection(arrays):
        raise ValueError(
            "One or more elements occur in both arrays and "
            + " strings. One parameter cannot be both list and string!"
        )

    # create the checker that will check all arguments given by argsToCheck
    # and turn them into the right datatype.
    def checker(func):
        def check_and_call(*args):
            args = list(args)
            for i in strings:
                arg = args[i]
                args[i] = str_to_bytes(arg)
            for i in arrays:
                arg = args[i]
                args[i] = list_to_bytes_list(arg)

            return func(*args)

        return check_and_call

    return checker


# Find the path and resource file. SWI_HOME_DIR shall be treated as a constant
# by users of this module
(_path, SWI_HOME_DIR) = _findSwipl()
_fixWindowsPath(_path)


# Load the library
_lib = CDLL(_path, mode=RTLD_GLOBAL)

#       /*******************************
#        *	      VERSIONS		*
#        *******************************/

PL_VERSION_SYSTEM = 1  # Prolog version
PL_VERSION_FLI = 2  # PL_* compatibility
PL_VERSION_REC = 3  # PL_record_external() compatibility
PL_VERSION_QLF = 4  # Saved QLF format version
PL_VERSION_QLF_LOAD = 5  # Min loadable QLF format version
PL_VERSION_VM = 6  # VM signature
PL_VERSION_BUILT_IN = 7  # Built-in predicate signature


# After SWI-Prolog 8.5.2, PL_version was renamed to PL_version_info
# to avoid a conflict with Perl. For more details, see the following:
# https://github.com/SWI-Prolog/swipl-devel/issues/900
# https://github.com/SWI-Prolog/swipl-devel/issues/910
try:
    if hasattr(_lib, "PL_version_info"):
        PL_version = _lib.PL_version_info  # swi-prolog > 8.5.2
    else:
        PL_version = _lib.PL_version  # swi-prolog <= 8.5.2
    PL_version.argtypes = [c_int]
    PL_version.restype = c_uint

    PL_VERSION = PL_version(PL_VERSION_SYSTEM)
    if PL_VERSION < 80200:
        raise Exception("swi-prolog >= 8.2.0 is required")
except AttributeError:
    raise Exception("swi-prolog version number could not be determined")


# PySwip constants
PYSWIP_MAXSTR = 1024
c_int_p = c_void_p
c_long_p = c_void_p
c_double_p = c_void_p
c_uint_p = c_void_p


#
# constants (from SWI-Prolog.h)
# /* PL_unify_term( arguments */


if PL_VERSION < 80200:
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
    # define PL_CODE_LIST     (14)       /* [ascii...] */
    # define PL_CHAR_LIST     (15)       /* [h,e,l,l,o] */
    # define PL_BOOL      (16)       /* PL_set_feature() */
    # define PL_FUNCTOR_CHARS (17)       /* PL_unify_term() */
    # define _PL_PREDICATE_INDICATOR (18)    /* predicate_t (Procedure) */
    # define PL_SHORT     (19)       /* short */
    # define PL_INT       (20)       /* int */
    # define PL_LONG      (21)       /* long */
    # define PL_DOUBLE    (22)       /* double */
    # define PL_NCHARS    (23)       /* unsigned, const char * */
    # define PL_UTF8_CHARS    (24)       /* const char * */
    # define PL_UTF8_STRING   (25)       /* const char * */
    # define PL_INT64     (26)       /* int64_t */
    # define PL_NUTF8_CHARS   (27)       /* unsigned, const char * */
    # define PL_NUTF8_CODES   (29)       /* unsigned, const char * */
    # define PL_NUTF8_STRING  (30)       /* unsigned, const char * */
    # define PL_NWCHARS   (31)       /* unsigned, const wchar_t * */
    # define PL_NWCODES   (32)       /* unsigned, const wchar_t * */
    # define PL_NWSTRING  (33)       /* unsigned, const wchar_t * */
    # define PL_MBCHARS   (34)       /* const char * */
    # define PL_MBCODES   (35)       /* const char * */
    # define PL_MBSTRING  (36)       /* const char * */

    REP_ISO_LATIN_1 = 0x0000  # output representation
    REP_UTF8 = 0x1000
    REP_MB = 0x2000

else:
    PL_VARIABLE = 1  # nothing
    PL_ATOM = 2  # const char *
    PL_INTEGER = 3  # int
    PL_RATIONAL = 4  # rational number
    PL_FLOAT = 5  # double
    PL_STRING = 6  # const char *
    PL_TERM = 7

    PL_NIL = 8  # The constant []
    PL_BLOB = 9  # non-atom blob
    PL_LIST_PAIR = 10  # [_|_] term

    # # PL_unify_term(
    PL_FUNCTOR = 11  # functor_t, arg ...
    PL_LIST = 12  # length, arg ...
    PL_CHARS = 13  # const char *
    PL_POINTER = 14  # void *
    # PlArg::PlArg(text, type
    PL_CODE_LIST = 15  # [ascii...]
    PL_CHAR_LIST = 16  # [h,e,l,l,o]
    PL_BOOL = 17  # PL_set_prolog_flag(
    PL_FUNCTOR_CHARS = 18  # PL_unify_term(
    _PL_PREDICATE_INDICATOR = 19  # predicate_t= Procedure
    PL_SHORT = 20  # short
    PL_INT = 21  # int
    PL_LONG = 22  # long
    PL_DOUBLE = 23  # double
    PL_NCHARS = 24  # size_t, const char *
    PL_UTF8_CHARS = 25  # const char *
    PL_UTF8_STRING = 26  # const char *
    PL_INT64 = 27  # int64_t
    PL_NUTF8_CHARS = 28  # size_t, const char *
    PL_NUTF8_CODES = 29  # size_t, const char *
    PL_NUTF8_STRING = 30  # size_t, const char *
    PL_NWCHARS = 31  # size_t, const wchar_t *
    PL_NWCODES = 32  # size_t, const wchar_t *
    PL_NWSTRING = 33  # size_t, const wchar_t *
    PL_MBCHARS = 34  # const char *
    PL_MBCODES = 35  # const char *
    PL_MBSTRING = 36  # const char *
    PL_INTPTR = 37  # intptr_t
    PL_CHAR = 38  # int
    PL_CODE = 39  # int
    PL_BYTE = 40  # int
    # PL_skip_list(
    PL_PARTIAL_LIST = 41  # a partial list
    PL_CYCLIC_TERM = 42  # a cyclic list/term
    PL_NOT_A_LIST = 43  # Object is not a list
    # dicts
    PL_DICT = 44

    REP_ISO_LATIN_1 = 0x0000  # output representation
    REP_UTF8 = 0x00100000
    REP_MB = 0x00200000

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
PL_PRUNED = PL_CUTTED
PL_REDO = 2

PL_FA_NOTRACE = 0x01  # foreign cannot be traced
PL_FA_TRANSPARENT = 0x02  # foreign is module transparent
PL_FA_NONDETERMINISTIC = 0x04  # foreign is non-deterministic
PL_FA_VARARGS = 0x08  # call using t0, ac, ctx
PL_FA_CREF = 0x10  # Internal: has clause-reference */

#        /*******************************
#        *       CALL-BACK      *
#        *******************************/

PL_Q_DEBUG = 0x01  # = TRUE for backward compatibility
PL_Q_NORMAL = 0x02  # normal usage
PL_Q_NODEBUG = 0x04  # use this one
PL_Q_CATCH_EXCEPTION = 0x08  # handle exceptions in C
PL_Q_PASS_EXCEPTION = 0x10  # pass to parent environment
PL_Q_DETERMINISTIC = 0x20  # call was deterministic

#        /*******************************
#        *         BLOBS        *
#        *******************************/

# define PL_BLOB_MAGIC_B 0x75293a00  /* Magic to validate a blob-type */
# define PL_BLOB_VERSION 1       /* Current version */
# define PL_BLOB_MAGIC   (PL_BLOB_MAGIC_B|PL_BLOB_VERSION)

# define PL_BLOB_UNIQUE  0x01        /* Blob content is unique */
# define PL_BLOB_TEXT    0x02        /* blob contains text */
# define PL_BLOB_NOCOPY  0x04        /* do not copy the data */
# define PL_BLOB_WCHAR   0x08        /* wide character string */

#        /*******************************
#        *      CHAR BUFFERS    *
#        *******************************/

# Changed in 8.1.22
if PL_VERSION < 80122:
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
    CVT_MASK = 0x00FF

    BUF_DISCARDABLE = 0x0000
    BUF_RING = 0x0100
    BUF_MALLOC = 0x0200

    CVT_EXCEPTION = 0x10000  # throw exception on error
else:
    CVT_ATOM = 0x00000001
    CVT_STRING = 0x00000002
    CVT_LIST = 0x00000004
    CVT_INTEGER = 0x00000008
    CVT_RATIONAL = 0x00000010
    CVT_FLOAT = 0x00000020
    CVT_VARIABLE = 0x00000040
    CVT_NUMBER = CVT_RATIONAL | CVT_FLOAT
    CVT_ATOMIC = CVT_NUMBER | CVT_ATOM | CVT_STRING
    CVT_WRITE = 0x00000080
    CVT_WRITE_CANONICAL = 0x00000080
    CVT_WRITEQ = 0x000000C0
    CVT_ALL = CVT_ATOMIC | CVT_LIST
    CVT_MASK = 0x00000FFF

    BUF_DISCARDABLE = 0x00000000
    BUF_STACK = 0x00010000
    BUF_RING = BUF_STACK
    BUF_MALLOC = 0x00020000
    BUF_ALLOW_STACK = 0x00040000

    CVT_EXCEPTION = 0x00001000  # throw exception on error


argv = list_to_bytes_list(sys.argv + [None])
argc = len(sys.argv)

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
# typedef uintptr_t       buf_mark_t;     /* buffer mark handle */

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
intptr_t = c_long
ssize_t = intptr_t
wint_t = c_uint
buf_mark_t = c_uint_p

PL_initialise = _lib.PL_initialise
PL_initialise = check_strings(None, 1)(PL_initialise)

PL_mark_string_buffers = _lib.PL_mark_string_buffers
PL_mark_string_buffers.argtypes = [buf_mark_t]

PL_release_string_buffers_from_mark = _lib.PL_release_string_buffers_from_mark
PL_release_string_buffers_from_mark.argtypes = [buf_mark_t]


@contextmanager
def PL_STRINGS_MARK():
    __PL_mark = buf_mark_t()
    PL_mark_string_buffers(byref(__PL_mark))
    try:
        yield
    finally:
        PL_release_string_buffers_from_mark(__PL_mark)


PL_open_foreign_frame = _lib.PL_open_foreign_frame
PL_open_foreign_frame.restype = fid_t

PL_foreign_control = _lib.PL_foreign_control
PL_foreign_control.argtypes = [control_t]
PL_foreign_control.restype = c_int

PL_foreign_context = _lib.PL_foreign_context
PL_foreign_context.argtypes = [control_t]
PL_foreign_context.restype = intptr_t

PL_retry = _lib._PL_retry
PL_retry.argtypes = [intptr_t]
PL_retry.restype = foreign_t

PL_new_term_ref = _lib.PL_new_term_ref
PL_new_term_ref.restype = term_t

PL_new_term_refs = _lib.PL_new_term_refs
PL_new_term_refs.argtypes = [c_int]
PL_new_term_refs.restype = term_t

PL_chars_to_term = _lib.PL_chars_to_term
PL_chars_to_term.argtypes = [c_char_p, term_t]
PL_chars_to_term.restype = c_int

PL_chars_to_term = check_strings(0, None)(PL_chars_to_term)

PL_call = _lib.PL_call
PL_call.argtypes = [term_t, module_t]
PL_call.restype = c_int

PL_call_predicate = _lib.PL_call_predicate
PL_call_predicate.argtypes = [module_t, c_int, predicate_t, term_t]
PL_call_predicate.restype = c_int

PL_discard_foreign_frame = _lib.PL_discard_foreign_frame
PL_discard_foreign_frame.argtypes = [fid_t]
PL_discard_foreign_frame.restype = None

PL_put_chars = _lib.PL_put_chars
PL_put_chars.argtypes = [term_t, c_int, c_size_t, c_char_p]
PL_put_chars.restype = c_int

PL_put_list_chars = _lib.PL_put_list_chars
PL_put_list_chars.argtypes = [term_t, c_char_p]
PL_put_list_chars.restype = c_int

PL_put_list_chars = check_strings(1, None)(PL_put_list_chars)

# PL_EXPORT(void)                PL_register_atom(atom_t a);
PL_register_atom = _lib.PL_register_atom
PL_register_atom.argtypes = [atom_t]
PL_register_atom.restype = None

# PL_EXPORT(void)                PL_unregister_atom(atom_t a);
PL_unregister_atom = _lib.PL_unregister_atom
PL_unregister_atom.argtypes = [atom_t]
PL_unregister_atom.restype = None

# PL_EXPORT(atom_t)      PL_functor_name(functor_t f);
PL_functor_name = _lib.PL_functor_name
PL_functor_name.argtypes = [functor_t]
PL_functor_name.restype = atom_t

# PL_EXPORT(int)         PL_functor_arity(functor_t f);
PL_functor_arity = _lib.PL_functor_arity
PL_functor_arity.argtypes = [functor_t]
PL_functor_arity.restype = c_int

#                       /* Get C-values from Prolog terms */
# PL_EXPORT(int)         PL_get_atom(term_t t, atom_t *a);
PL_get_atom = _lib.PL_get_atom
PL_get_atom.argtypes = [term_t, POINTER(atom_t)]
PL_get_atom.restype = c_int

# PL_EXPORT(int)         PL_get_bool(term_t t, int *value);
PL_get_bool = _lib.PL_get_bool
PL_get_bool.argtypes = [term_t, POINTER(c_int)]
PL_get_bool.restype = c_int

# PL_EXPORT(int)         PL_get_atom_chars(term_t t, char **a);
PL_get_atom_chars = _lib.PL_get_atom_chars  # FIXME
PL_get_atom_chars.argtypes = [term_t, POINTER(c_char_p)]
PL_get_atom_chars.restype = c_int

PL_get_atom_chars = check_strings(None, 1)(PL_get_atom_chars)

PL_get_string_chars = _lib.PL_get_string
PL_get_string_chars.argtypes = [term_t, POINTER(c_char_p), c_int_p]

PL_get_chars = _lib.PL_get_chars  # FIXME:
PL_get_chars.argtypes = [term_t, POINTER(c_char_p), c_uint]
PL_get_chars.restype = c_int

PL_get_chars = check_strings(None, 1)(PL_get_chars)

PL_get_integer = _lib.PL_get_integer
PL_get_integer.argtypes = [term_t, POINTER(c_int)]
PL_get_integer.restype = c_int

PL_get_long = _lib.PL_get_long
PL_get_long.argtypes = [term_t, POINTER(c_long)]
PL_get_long.restype = c_int

PL_get_float = _lib.PL_get_float
PL_get_float.argtypes = [term_t, c_double_p]
PL_get_float.restype = c_int

PL_get_functor = _lib.PL_get_functor
PL_get_functor.argtypes = [term_t, POINTER(functor_t)]
PL_get_functor.restype = c_int

PL_get_name_arity = _lib.PL_get_name_arity
PL_get_name_arity.argtypes = [term_t, POINTER(atom_t), POINTER(c_int)]
PL_get_name_arity.restype = c_int

PL_get_arg = _lib.PL_get_arg
PL_get_arg.argtypes = [c_int, term_t, term_t]
PL_get_arg.restype = c_int

PL_get_head = _lib.PL_get_head
PL_get_head.argtypes = [term_t, term_t]
PL_get_head.restype = c_int

PL_get_tail = _lib.PL_get_tail
PL_get_tail.argtypes = [term_t, term_t]
PL_get_tail.restype = c_int

PL_get_nil = _lib.PL_get_nil
PL_get_nil.argtypes = [term_t]
PL_get_nil.restype = c_int

PL_put_atom_chars = _lib.PL_put_atom_chars
PL_put_atom_chars.argtypes = [term_t, c_char_p]
PL_put_atom_chars.restype = c_int

PL_put_atom_chars = check_strings(1, None)(PL_put_atom_chars)

PL_atom_chars = _lib.PL_atom_chars
PL_atom_chars.argtypes = [atom_t]
PL_atom_chars.restype = c_char_p

PL_atom_wchars = _lib.PL_atom_wchars
PL_atom_wchars.argtypes = [atom_t, POINTER(c_size_t)]
PL_atom_wchars.restype = c_wchar_p

PL_predicate = _lib.PL_predicate
PL_predicate.argtypes = [c_char_p, c_int, c_char_p]
PL_predicate.restype = predicate_t

PL_predicate = check_strings([0, 2], None)(PL_predicate)

PL_pred = _lib.PL_pred
PL_pred.argtypes = [functor_t, module_t]
PL_pred.restype = predicate_t

PL_open_query = _lib.PL_open_query
PL_open_query.argtypes = [module_t, c_int, predicate_t, term_t]
PL_open_query.restype = qid_t

PL_next_solution = _lib.PL_next_solution
PL_next_solution.argtypes = [qid_t]
PL_next_solution.restype = c_int

PL_copy_term_ref = _lib.PL_copy_term_ref
PL_copy_term_ref.argtypes = [term_t]
PL_copy_term_ref.restype = term_t

PL_get_list = _lib.PL_get_list
PL_get_list.argtypes = [term_t, term_t, term_t]
PL_get_list.restype = c_int

PL_get_chars = _lib.PL_get_chars  # FIXME

PL_close_query = _lib.PL_close_query
PL_close_query.argtypes = [qid_t]
PL_close_query.restype = None

PL_cut_query = _lib.PL_cut_query
PL_cut_query.argtypes = [qid_t]
PL_cut_query.restype = None

PL_halt = _lib.PL_halt
PL_halt.argtypes = [c_int]
PL_halt.restype = None

PL_cleanup = _lib.PL_cleanup
PL_cleanup.restype = c_int

PL_unify_integer = _lib.PL_unify_integer
PL_unify_atom_chars = _lib.PL_unify_atom_chars

PL_unify_float = _lib.PL_unify_float
PL_unify_float.argtypes = [term_t, c_double]
PL_unify_float.restype = c_int

PL_unify_bool = _lib.PL_unify_bool
PL_unify_bool.argtypes = [term_t, c_int]
PL_unify_bool.restype = c_int

PL_unify_list = _lib.PL_unify_list
PL_unify_list.argtypes = [term_t, term_t, term_t]
PL_unify_list.restype = c_int

PL_unify_nil = _lib.PL_unify_nil
PL_unify_nil.argtypes = [term_t]
PL_unify_nil.restype = c_int

PL_unify_atom = _lib.PL_unify_atom
PL_unify_atom.argtypes = [term_t, atom_t]
PL_unify_atom.restype = c_int

PL_unify_atom_chars = _lib.PL_unify_atom_chars
PL_unify_atom_chars.argtypes = [term_t, c_char_p]
PL_unify_atom_chars.restype = c_int

PL_unify_string_chars = _lib.PL_unify_string_chars
PL_unify_string_chars.argtypes = [term_t, c_char_p]
PL_unify_string_chars.restype = c_void_p

PL_foreign_control = _lib.PL_foreign_control
PL_foreign_control.argtypes = [control_t]
PL_foreign_control.restypes = c_int

PL_foreign_context_address = _lib.PL_foreign_context_address
PL_foreign_context_address.argtypes = [control_t]
PL_foreign_context_address.restypes = c_void_p

PL_retry_address = _lib._PL_retry_address
PL_retry_address.argtypes = [c_void_p]
PL_retry_address.restypes = foreign_t

PL_unify = _lib.PL_unify
PL_unify.restype = c_int

PL_succeed = 1

PL_unify_arg = _lib.PL_unify_arg
PL_unify_arg.argtypes = [c_int, term_t, term_t]
PL_unify_arg.restype = c_int

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

PL_put_variable = _lib.PL_put_variable
PL_put_variable.argtypes = [term_t]
PL_put_variable.restype = None

PL_put_integer = _lib.PL_put_integer
PL_put_integer.argtypes = [term_t, c_long]
PL_put_integer.restype = None

PL_put_functor = _lib.PL_put_functor
PL_put_functor.argtypes = [term_t, functor_t]
PL_put_functor.restype = None

PL_put_list = _lib.PL_put_list
PL_put_list.argtypes = [term_t]
PL_put_list.restype = None

PL_put_nil = _lib.PL_put_nil
PL_put_nil.argtypes = [term_t]
PL_put_nil.restype = None

PL_put_term = _lib.PL_put_term
PL_put_term.argtypes = [term_t, term_t]
PL_put_term.restype = None

PL_cons_functor = _lib.PL_cons_functor  # FIXME:

PL_cons_functor_v = _lib.PL_cons_functor_v
PL_cons_functor_v.argtypes = [term_t, functor_t, term_t]
PL_cons_functor_v.restype = None

PL_cons_list = _lib.PL_cons_list
PL_cons_list.argtypes = [term_t, term_t, term_t]
PL_cons_list.restype = None

PL_exception = _lib.PL_exception
PL_exception.argtypes = [qid_t]
PL_exception.restype = term_t

PL_register_foreign = _lib.PL_register_foreign
PL_register_foreign = check_strings(0, None)(PL_register_foreign)

PL_new_atom = _lib.PL_new_atom
PL_new_atom.argtypes = [c_char_p]
PL_new_atom.restype = atom_t

PL_new_atom = check_strings(0, None)(PL_new_atom)

PL_new_functor = _lib.PL_new_functor
PL_new_functor.argtypes = [atom_t, c_int]
PL_new_functor.restype = functor_t

PL_compare = _lib.PL_compare
PL_compare.argtypes = [term_t, term_t]
PL_compare.restype = c_int

PL_same_compound = _lib.PL_same_compound
PL_same_compound.argtypes = [term_t, term_t]
PL_same_compound.restype = c_int

PL_record = _lib.PL_record
PL_record.argtypes = [term_t]
PL_record.restype = record_t

PL_recorded = _lib.PL_recorded
PL_recorded.argtypes = [record_t, term_t]
PL_recorded.restype = None

PL_erase = _lib.PL_erase
PL_erase.argtypes = [record_t]
PL_erase.restype = None

PL_new_module = _lib.PL_new_module
PL_new_module.argtypes = [atom_t]
PL_new_module.restype = module_t

PL_is_initialised = _lib.PL_is_initialised

intptr_t = c_long
ssize_t = intptr_t
wint_t = c_uint

PL_thread_self = _lib.PL_thread_self
PL_thread_self.restype = c_int

PL_thread_attach_engine = _lib.PL_thread_attach_engine
PL_thread_attach_engine.argtypes = [c_void_p]
PL_thread_attach_engine.restype = c_int


class _mbstate_t_value(Union):
    _fields_ = [("__wch", wint_t), ("__wchb", c_char * 4)]


class mbstate_t(Structure):
    _fields_ = [("__count", c_int), ("__value", _mbstate_t_value)]


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
    _fields_ = [
        ("read", Sread_function),
        ("write", Swrite_function),
        ("seek", Sseek_function),
        ("close", Sclose_function),
        ("seek64", Sseek64_function),
        ("reserved", intptr_t * 2),
    ]


# IOENC
(
    ENC_UNKNOWN,
    ENC_OCTET,
    ENC_ASCII,
    ENC_ISO_LATIN_1,
    ENC_ANSI,
    ENC_UTF8,
    ENC_UNICODE_BE,
    ENC_UNICODE_LE,
    ENC_WCHAR,
) = tuple(range(9))
IOENC = c_int


# IOPOS
class IOPOS(Structure):
    _fields_ = [
        ("byteno", c_int64),
        ("charno", c_int64),
        ("lineno", c_int),
        ("linepos", c_int),
        ("reserved", intptr_t * 2),
    ]


# IOSTREAM
class IOSTREAM(Structure):
    _fields_ = [
        ("bufp", c_char_p),
        ("limitp", c_char_p),
        ("buffer", c_char_p),
        ("unbuffer", c_char_p),
        ("lastc", c_int),
        ("magic", c_int),
        ("bufsize", c_int),
        ("flags", c_int),
        ("posbuf", IOPOS),
        ("position", POINTER(IOPOS)),
        ("handle", c_void_p),
        ("functions", IOFUNCTIONS),
        ("locks", c_int),
        ("mutex", IOLOCK),
        ("closure_hook", CFUNCTYPE(None, c_void_p)),
        ("closure", c_void_p),
        ("timeout", c_int),
        ("message", c_char_p),
        ("encoding", IOENC),
    ]


IOSTREAM._fields_.extend(
    [("tee", IOSTREAM), ("mbstate", POINTER(mbstate_t)), ("reserved", intptr_t * 6)]
)


Sopen_string = _lib.Sopen_string
Sopen_string.argtypes = [POINTER(IOSTREAM), c_char_p, c_size_t, c_char_p]
Sopen_string.restype = POINTER(IOSTREAM)

Sclose = _lib.Sclose
Sclose.argtypes = [POINTER(IOSTREAM)]

PL_unify_stream = _lib.PL_unify_stream
PL_unify_stream.argtypes = [term_t, POINTER(IOSTREAM)]


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

_isCleaned = False
# create a property for Atom's delete method in order to avoid segmentation fault
cleaned = property(_isCleaned)


# register the cleanup function to be executed on system exit
@atexit.register
def cleanupProlog():
    # only do something if prolog has been initialised
    if PL_is_initialised(None, None):
        # clean up the prolog system using the caught exit code
        # if exit code is None, the program exits normally and we can use 0
        # instead.
        # TODO Prolog documentation says cleanup with code 0 may be interrupted
        # If the program has come to an end the prolog system should not
        # interfere with that. Therefore we may want to use 1 instead of 0.
        PL_cleanup(int(_hook.exit_code or 0))
        _isCleaned = True
