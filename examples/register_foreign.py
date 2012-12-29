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


from pyswip import Prolog, registerForeign, Atom


def atom_checksum(*a):
    if isinstance(a[0], Atom):
        r = sum(ord(c)&0xFF for c in str(a[0]))
        a[1].value = r&0xFF
        return True
    else:
        return False

p = Prolog()
registerForeign(atom_checksum, arity=2)
print list(p.query("X='Python', atom_checksum(X, Y)", catcherrors=False))
