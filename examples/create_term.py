# -*- coding:utf-8 -*-

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

from pyswip.prolog import Prolog, Swipl

def main():
    prolog = Prolog()
    lib = Swipl.lib
    
    a1 = lib.new_term_refs(2)
    a2 = a1 + 1
    t = lib.new_term_ref()
    ta = lib.new_term_ref()

    animal2 = lib.new_functor(lib.new_atom("animal"), 2)
    assertz = lib.new_functor(lib.new_atom("assertz"), 1)

    lib.put_atom_chars(a1, "gnu")
    lib.put_integer(a2, 50)
    lib.cons_functor_v(t, animal2, a1)
    lib.cons_functor_v(ta, assertz, t)
    lib.call(ta, None)
    
    print(list(prolog.query("animal(X,Y)", catcherrors=True)))

    
if __name__ == "__main__":
    main()
