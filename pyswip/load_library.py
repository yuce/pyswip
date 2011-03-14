from ctypes import *
from ctypes.util import find_library
import sys

def loadLibrary():
    '''tries to load the swi-prolog shared library'''
    # try to get lib path from the swipl executable
    # TODO: check whether this is reliable(different versions)
    from subprocess import Popen, PIPE
    try:
        if sys.platform[:3] in ('win', 'cyg'):
            # probably raises OSError:
            cmd = Popen(['swipl', '--dump-runtime-variables'], stdout=PIPE)
            ret = cmd.communicate()
            
            ret = ret[0].replace('\r\n', '').split(';') # use .decode() in python3
            if ret[9] == 'PLSHARED="yes"':
                print('shared true')
                path = (ret[1].split('=',1)[1] + '/bin/' +
                        ret[4].split('=',1)[1][4:][:5] + '.' +
                        ret[7].split('=',1)[1]).replace('"', '')
                print(path)
            else:
                raise OSError
        else: # assume UNIX-like
            # probably raises OSError:
            cmd = Popen(['swipl', '--dump-runtime-variables'], stdout=PIPE)
            ret = cmd.communicate()
            
            ret = ret[0].replace('\n', '').split(';') # use .decode() in python3
            
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
