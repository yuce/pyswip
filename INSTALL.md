# Installing PySwip

## Requirements

* Python 3.8 or later
* SWI-Prolog 9.0.4 or later
* 64bit Intel or ARM processor

> [!IMPORTANT]
> Make sure the SWI-Prolog architecture is the same as the Python architecture.
> If you are using a 64bit build of Python, use a 64bit build of SWI-Prolog, etc.

## Installing on All Platforms

PySwip is available to install from [Python Package Index](https://pypi.org/project/pyswip/).

> [!NOTE]
> We recommend installing PySwip into a Python virtual environment.
> See: [Creation of virtual environments](https://docs.python.orgs/3/library/venv.html)

You can install PySwip using:
```
pip install pyswip
```

You will need to have SWI-Prolog installed on your system.
Some operating systems have packages for SWI-Prolog.
Otherwise, you can download it from [SWI-Prolog's website](https://www.swi-prolog.org/Download.html) or build from source.

PySwip requires the location of the `libswpl` shared library and also the SWI-Prolog home directory.
In many cases, PySwip can find the shared library and the home directory automatically.
Otherwise, you can use the following environment variables:
* `SWI_HOME_DIR` - The SWI-Prolog home directory.
* `LIBSWIPL_PATH` - The location of the `libswipl` shared library.

You can get the locations mentioned above using the following commands:
```
swipl --dump-runtime-variables
```

That will output something like:
```
PLBASE="/home/yuce/swipl-9.3.8/lib/swipl";
...
PLLIBDIR="/home/yuce/swipl-9.3.8/lib/swipl/lib/x86_64-linux";
```
Use the value in the `PLBASE` variable as the value for the `SWI_HOME_DIR` environment variable.
Use the value in the `PLLIBDIR` variable as the value for the `LIBSWIPL_PATH` environment variable.

## Installing on Linux

### Arch Linux

Installing SWI-Prolog:
```
pacman -S swi-prolog
```

Installing PySwip:
(Alternative to the `pip install` way explained above)
```
pacman -S python-pyswip
```

### Fedora Workstation

Installing SWI-Prolog:
```
dnf install pl
```

Installing PySwip:
(Alternative to the `pip install` way explained above)
```
dnf install python3-pyswip
```

### Manjaro Linux

Same as the Arch Linux instructions.
See: https://manjaristas.org/branch_compare?q=pyswip

### Parabola GNU/Linux-libre

Same as the Arch Linux instructions.
See: https://www.parabola.nu/packages/?q=python-pyswip

### Debian, Ubuntu, Raspbian

Debian Bookworm, Ubuntu 24.04 and Raspberry Pi OS Bookworm have SWI-Prolog 9.0.4 in their repositories.

To install PySwip, use the `pip install` way explained above.

## Windows

Download a recent version of SWI-Prolog from https://www.swi-prolog.org/Download.html and install it.

To install PySwip, use the `pip install` way explained above.

## MacOS

The preferred way of installing SWI-Prolog on MacOS is using [Homebrew](https://brew.sh).

### Homebrew

Installing SWI-Prolog:
```
brew install swi-prolog
```

To install PySwip, use the `pip install` way explained above.

### Official SWI-Prolog App

Install SWI-Prolog from https://www.swi-prolog.org/Download.html.

If you get an error like `libgmp.X not found`, you have to set the `DYLD_FALLBACK_LIBRARY_PATH` environment variable before running Python:
```
export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/Frameworks
```

To install PySwip, use the `pip install` way explained above.

## Other UNIX

### OpenBSD

Install SWI-Prolog using the following on OpenBSD 7.6 and later:
```
pkg_add swi-prolog
```

To install PySwip, use the `pip install` way explained above.

### FreeBSD

SWI-Prolog can be installed using `pkg`:
```
pkg install swi-pl
```

To install PySwip, use the `pip install` way explained above.

## Test Drive

Run a quick test by running following code at your Python console:
    ```python
    from pyswip import Prolog
    prolog = Prolog()
    prolog.assertz("father(michael,john)")
    ```
