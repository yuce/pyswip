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

from collections import deque
from typing import IO

from pyswip.prolog import Prolog


__all__ = "solve", "prolog_source"

_PROLOG_FILE = "hanoi.pl"

Prolog.consult(_PROLOG_FILE, relative_to=__file__)


def make_notify_function(file):
    state = {"step": 1}

    def f(from_to):
        frm, to = from_to
        print(f"{state['step']}. Move disk from {frm} pole to {to} pole.", file=file)
        state["step"] += 1

    return f


class Notifier:
    def __init__(self, fun):
        self.fun = fun

    def notify(self, t):
        return not self.fun(t)


class Tower:
    def __init__(self, disk_count=3, file=None):
        if disk_count < 1 or disk_count > 9:
            raise ValueError("disk_count must be between 1 and 9")
        self.disk_count = disk_count
        self.file = file
        self.disks = dict(
            left=deque(range(disk_count, 0, -1)),
            center=deque(),
            right=deque(),
        )
        self.started = False
        self.step = 0

    def draw(self) -> None:
        print("\n Step", self.step, file=self.file)
        print(file=self.file)
        for i in range(self.disk_count):
            n = self.disk_count - i - 1
            print(" ", end=" ", file=self.file)
            for pole in ["left", "center", "right"]:
                if len(self.disks[pole]) - n > 0:
                    print(self.disks[pole][n], end=" ", file=self.file)
                else:
                    print(" ", end=" ", file=self.file)
            print(file=self.file)
        print("-" * 9, file=self.file)
        print(" ", "L", "C", "R", file=self.file)

    def move(self, r) -> None:
        if not self.started:
            self.draw()
            self.started = True
        self.disks[str(r[1])].append(self.disks[str(r[0])].pop())
        self.step += 1
        self.draw()


def solve(disk_count: int = 3, simple: bool = False, file: IO = None) -> None:
    """
    Solves the Towers of Hanoi problem.

    :param disk_count:
        Number of disks to use
    :param simple:
        If set to ``True``, only the moves are printed.
        Otherwise all states are drawn.
    :param file:
        The file-like object to output the steps of the solution.
        By default stdout is used.

    >>> solve(3, simple=True)
    1. Move disk from left pole to right pole.
    2. Move disk from left pole to center pole.
    3. Move disk from right pole to center pole.
    4. Move disk from left pole to right pole.
    5. Move disk from center pole to left pole.
    6. Move disk from center pole to right pole.
    7. Move disk from left pole to right pole.
    """
    if simple:
        Prolog.register_foreign(make_notify_function(file), name="notify")
    else:
        tower = Tower(disk_count, file=file)
        notifier = Notifier(tower.move)
        Prolog.register_foreign(notifier.notify)
    list(Prolog.query("hanoi(%s)", disk_count))


def prolog_source() -> str:
    """
    Returns the Prolog source file that solves the Towers of Hanoi problem.
    """
    from pathlib import Path

    path = Path(__file__).parent / _PROLOG_FILE
    with open(path) as f:
        return f.read()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("disk_count", type=int, choices=list(range(1, 10)))
    parser.add_argument("-s", "--simple", action="store_true")
    args = parser.parse_args()
    solve(args.disk_count, simple=args.simple)


if __name__ == "__main__":
    main()
