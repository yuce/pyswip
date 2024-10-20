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

from pyswip.prolog import Prolog
from pyswip.easy import registerForeign


class Notifier:
    def __init__(self, fun):
        self.fun = fun

    def notify(self, t):
        return not self.fun(t)

    notify.arity = 1


class Tower:
    def __init__(self, N=3, interactive=False):
        """N is the number of disks"""
        self.N = N
        self.disks = dict(left=deque(range(N, 0, -1)), center=deque(), right=deque())
        self.started = False
        self.interactive = interactive
        self.step = 0

    def move(self, r):
        if not self.started:
            self.step += 1
            if self.draw():
                return True
            self.started = True
        disks = self.disks
        disks[str(r[1])].append(disks[str(r[0])].pop())
        self.step += 1
        return self.draw()

    def draw(self):
        disks = self.disks
        print("\n Step", self.step)
        for i in range(self.N):
            n = self.N - i - 1
            print(" ", end=" ")
            for pole in ["left", "center", "right"]:
                if len(disks[pole]) - n > 0:
                    print(disks[pole][n], end=" ")
                else:
                    print(" ", end=" ")
            print()
        print("-" * 9)
        print(" ", "L", "C", "R")
        if self.interactive:
            cont = input("Press 'n' to finish: ")
            return cont.lower() == "n"


def main():
    n = 3
    tower = Tower(n, True)
    notifier = Notifier(tower.move)
    registerForeign(notifier.notify)
    Prolog.consult("hanoi.pl", relative_to=__file__)
    list(Prolog.query("hanoi(%d)" % n))


if __name__ == "__main__":
    main()
