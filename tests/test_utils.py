# pyswip -- Python SWI-Prolog bridge
# Copyright (c) 2007-2024 Yüce Tekol and PySwip
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
import unittest
import tempfile
from pathlib import Path

from pyswip.utils import resolve_path


class UtilsTestCase(unittest.TestCase):
    def test_resolve_path_given_file(self):
        filename = "test_read.pl"
        path = resolve_path(filename)
        self.assertEqual(Path(filename), path)

    def test_resolve_path_given_dir(self):
        filename = "test_read.pl"
        path = resolve_path(filename, __file__)
        current_dir = Path(__file__).parent.absolute()
        self.assertEqual(current_dir / filename, path)

    def test_resolve_path_symbolic_link(self):
        current_dir = Path(__file__).parent.absolute()
        path = current_dir / "test_read.pl"
        temp_dir = tempfile.TemporaryDirectory("pyswip")
        try:
            symlink = Path(temp_dir.name) / "symlinked"
            os.symlink(path, symlink)
            self.assertRaises(ValueError, lambda: resolve_path("test_read.pl", symlink))
        finally:
            temp_dir.cleanup()
