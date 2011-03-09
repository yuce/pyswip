from ctypes import *
from ctypes.util import find_library
import sys

def loadLibrary():
    '''tries to load the swi-prolog shared library'''
    for libname in ('swipl', 'pl'):
        # try to use find_library from ctypes
        print('try find_library()...')
        path = find_library(libname)
        if path:
            try:
                CDLL(path) # TODO: just check whether it's loadable?
                break
            except OSError:
                pass
        # try to simply open the lib
        print('try CDLL()...')
        try:
            if sys.platform[:3] in ('win', 'cyg'):
                try:
                    path = '%s.dll' % libname
                    CDLL(path)
                    break
                except:
                    path = 'lib%s.dll' % libname
            elif sys.platform[:3] in ('dar', 'os2'):
                path = 'lib%s.dylib' % libname
            else: # assume UNIX-like
                path = 'lib%s.so' % libname
            CDLL(path)
            break
        except OSError:
            # try current working directory
            try:
                print('try cwd...')
                path = './' + path
                CDLL(path)
                break
            except OSError:
                pass
    else:
        # try to get lib path from the swipl executable
        # TODO: check whether this is reliable(different versions)
        # does not work for windows currently
        print('try swipl executable...')
        from subprocess import check_output
        
        try:
            # probably raises OSError:
            ret = check_output(['swipl', '--dump-runtime-variables'])
            ret = ret.replace('\n', '').split(';') # use .decode() in python3
            
            if ret[9] == 'PLSHARED="yes"':
                print('shared true')
                path = (ret[1].split('=',1)[1] + '/lib/' +
                        ret[2].split('=',1)[1] + '/lib' +
                        ret[4].split('=',1)[1][3:] + '.' +
                        ret[7].split('=',1)[1]).replace('"', '')
            else:
                raise OSError
        except OSError:
            raise ImportError('Could not find library "libswipl" or "libpl"')
    print('return')
    return CDLL(path)


lib = loadLibrary()
print(lib)
