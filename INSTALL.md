# PySwip INSTALL

PySwip has no dependencies beyond Python's standard library. Some operating systems do not install the full standard library. In that case make sure that your Python setup includes `ctypes`.

We recommend installing PySwip into a virtual environment. Python3 already has built-in support for that. You can create a virtual environment in `pyswip_env` directory using:
```
python3 -m venv pyswip_env
```

After that, you have to activate the virtual environment. On UNIX-like platorms (Linux, MacOS, FreeBSD, etc.) with BASH/csh/tcsh shell:
```
source pyswip_env/bin/activate
```

On Windows:
```
pyswip_env\Scripts\activate
```

See the [Python documentation](https://docs.python.org/3/library/venv.html) for more information.

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

### FreeBSD

1) SWI-Prolog can be installed using `pkg`:
    ```
    pkg install swi-pl
    ```

2) `pip install pyswip`

3) Run a quick test by running following code at your Python console:
    ```python
    from pyswip import Prolog
    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    ```
