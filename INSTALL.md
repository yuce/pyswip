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

2) Make sure `swipl` executable is on the `PATH`.

2) `pip install pyswip`

3) Run a quick test by running following code at your Python console:
    ```python
    from pyswip import Prolog
    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    ```

## MacOS

1) Get a recent version of SWI-Prolog from http://www.swi-prolog.org/Download.html and install it.

2) `pip install pyswip`

3) Make sure `swipl` executable is on the `PATH` and the directory that contains `libswipl.dylib` is in the `DYLD_FALLBACK_LIBRARY_PATH` environment variable. For example, if SWI-Prolog is in `/Applications/SWI-Prolog.app` directory, the following may work:
    ```
    export PATH=$PATH:PATH=$PATH:/Applications/SWI-Prolog.app/Contents/swipl/bin/x86_64-darwin15.6.0
    export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/swipl/lib/x86_64-darwin15.6.0
    ```

4) Run a quick test by running following code at your Python console:
    ```python
    from pyswip import Prolog
    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    ```


## Other UNIX

**TODO**
