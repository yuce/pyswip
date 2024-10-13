# Copyright (c) 2007-2024 Yüce Tekol and PySwip Contributors
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

from typing import Union
from pathlib import Path


def resolve_path(path: Union[str, Path], relative_to: Union[str, Path] = "") -> Path:
    path = Path(path).expanduser()
    if path.is_absolute() or not relative_to:
        return path
    relative_to = Path(relative_to).expanduser()
    if relative_to.is_symlink():
        raise ValueError("Symbolic links are not supported")
    if relative_to.is_dir():
        return relative_to / path
    elif relative_to.is_file():
        return relative_to.parent / path
    raise ValueError("relative_to must be either a filename or a directory")
