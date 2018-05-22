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

import os
import glob
import warnings
from subprocess import Popen, PIPE
from ctypes.util import find_library

from .const import *
from .swipl import *

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
        ret = ret[0].decode().replace(';', '').splitlines()
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

            elif platform == "dar":
                dllName = 'lib' + rtvars['PLLIB'][2:] + '.' + rtvars['PLSOEXT']
                path = os.path.join(rtvars['PLBASE'], 'lib', rtvars['PLARCH'])
                baseName = os.path.join(path, dllName)

                if os.path.exists(baseName):
                    fullName = baseName
                else:  # We will search for versions
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
        ret = [line.decode("utf-8") for line in ret if len(line) > 0]
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

    # Maybe the exec is on path?
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
    names = ['libswipl.dylib', 'libpl.dylib']
    
    path = os.environ.get('SWI_HOME_DIR')
    if path is None:
        path = os.environ.get('SWI_LIB_DIR')
        if path is None:
            path = os.environ.get('PLBASE')
            if path is None:
                raise Exception("SWI-Prolog home not found")  # XXX:
    
    paths = [path]

    for name in names:
        for path in paths:
            (path_res, back_path) = walk(path, name)

            if path_res is not None:
                os.environ['SWI_LIB_DIR'] = back_path
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
    paths = ['.', './lib', '/usr/lib/', '/usr/local/lib', '/opt/local/lib']
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
        
        if path is None:
            (path, swiHome) = _findSwiplMacOSHome()

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


# Find the path and resource file. SWI_HOME_DIR shall be treated as a constant
# by users of this module
# (_path, SWI_HOME_DIR) = _findSwipl()
# _fixWindowsPath(_path)

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

# IOFUNCTIONS
class IOFUNCTIONS(Structure):
    _fields_ = [("read",Sread_function),
                ("write",Swrite_function),
                ("seek",Sseek_function),
                ("close",Sclose_function),
                ("seek64",Sseek64_function),
                ("reserved",intptr_t*2)]

# IOENC
ENC_UNKNOWN,ENC_OCTET,ENC_ASCII,ENC_ISO_LATIN_1,ENC_ANSI,ENC_UTF8,ENC_UNICODE_BE,ENC_UNICODE_LE,ENC_WCHAR = tuple(range(9))
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



# #PL_EXPORT(IOSTREAM *)  Sopen_string(IOSTREAM *s, char *buf, size_t sz, const char *m);
# Sopen_string = _lib.Sopen_string
# Sopen_string.argtypes = [POINTER(IOSTREAM), c_char_p, c_size_t, c_char_p]
# Sopen_string.restype = POINTER(IOSTREAM)

# #PL_EXPORT(int)         Sclose(IOSTREAM *s);
# Sclose = _lib.Sclose
# Sclose.argtypes = [POINTER(IOSTREAM)]


# #PL_EXPORT(int)         PL_unify_stream(term_t t, IOSTREAM *s);
# PL_unify_stream = _lib.PL_unify_stream
# PL_unify_stream.argtypes = [term_t, POINTER(IOSTREAM)]
