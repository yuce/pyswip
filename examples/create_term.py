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

from pyswip.core import *
from pyswip.prolog import Prolog


def main():
    a1 = PL_new_term_refs(2)
    a2 = a1 + 1
    t = PL_new_term_ref()
    ta = PL_new_term_ref()

    animal2 = PL_new_functor(PL_new_atom("animal"), 2)
    assertz = PL_new_functor(PL_new_atom("assertz"), 1)

    PL_put_atom_chars(a1, "gnu")
    PL_put_integer(a2, 50)
    PL_cons_functor_v(t, animal2, a1)
    PL_cons_functor_v(ta, assertz, t)
    PL_call(ta, None)

    print(list(Prolog.query("animal(X,Y)", catcherrors=True)))


if __name__ == "__main__":
    main()
