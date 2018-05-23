# PySWIP INSTALL

PySWIP has no dependencies beyond Python's standard library. Some operating systems do not install the full standard library. In that case make sure that your Python setup includes `ctypes`.

## Linux

1) Install SWI-Prolog using your package manager. On Debian, Ubuntu and similar distributions, you can do that by:
```
sudo apt install swi-prolog
```
If you don't want the X bindings, just use the `swi-prolog-nox` package.

2) `pip install pyswip`

3) Run a quick test by running following code at your Python console:
```python
from pyswip import Prolog
prolog = Prolog()
prolog.assertz("father(michael,john)")
```


## Windows

1) Get a recent version of SWI-Prolog from http://www.swi-prolog.org/Download.html and install it.

2) `pip install pyswip` (*recommended*) or [download](https://pypi.org/project/pyswip/#files) a Windows installer version of PySWIP and install it.

3) Run a quick test by running following code at your Python console:
```python
from pyswip import Prolog
prolog = Prolog()
prolog.assertz("father(michael,john)")
```


## MacOS

**TODO**

## Other UNIX

**TODO**
