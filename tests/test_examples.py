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

"""
Run several complex examples using pySwip. The main goal of these tests is
ensure stability in several platforms.
"""

import pytest

examples = [
    "create_term.py",
    "father.py",
    "register_foreign.py",
    "register_foreign_simple.py",
    "knowledgebase.py",
    "hanoi/hanoi_simple.py",
    "sendmoremoney/money.py",
    "sendmoremoney/money_new.py",
]


@pytest.mark.parametrize("example", examples)
def test_example(example):
    path = example_path(example)
    execfile(path)


def example_path(path):
    import os.path

    return os.path.normpath(
        os.path.join(
            os.path.split(os.path.abspath(__file__))[0], "..", "examples", path
        )
    ).replace("\\", "\\\\")


def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update(
        {
            "__file__": filepath,
            "__name__": "__main__",
        }
    )
    with open(filepath, "rb") as file:
        exec(compile(file.read(), filepath, "exec"), globals, locals)
