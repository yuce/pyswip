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


def resolve_path(filename: str, relative_to: Union[str, Path] = "") -> Path:
    if not relative_to:
        return Path(filename)
    relative_to = Path(relative_to)
    if not relative_to.exists():
        raise FileNotFoundError(None, "Relative path does not exist", str(relative_to))
    if relative_to.is_symlink():
        raise ValueError("Symbolic links are not supported")
    if relative_to.is_dir():
        return relative_to / filename
    elif relative_to.is_file():
        return relative_to.parent / filename
    raise ValueError("relative_to must be either a filename or a directory")
