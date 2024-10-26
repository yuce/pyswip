Get Started
===========

Requirements
------------

* Python 3.9 or later
* SWI-Prolog 8.4.2 or later
* 64bit Intel or ARM processor

.. IMPORTANT::
    Make sure the SWI-Prolog architecture is the same as the Python architecture.
    If you are using a 64bit build of Python, use a 64bit build of SWI-Prolog, etc.


Installing PySwip
-----------------

.. _install_from_pypi:

PyPI
^^^^

PySwip is available to install from `Python Package Index <https://pypi.org/project/pyswip/>`_.

.. TIP::
    We recommend installing PySwip into a Python virtual environment.
    See: `Creation of virtual environments <https://docs.python.orgs/3/library/venv.html>`_

You can install PySwip using::

    pip install -U pyswip

You will need to have SWI-Prolog installed on your system.
See :ref:`install_swi_prolog`.

PySwip requires the location of the ``libswpl`` shared library and also the SWI-Prolog home directory.
In many cases, PySwip can find the shared library and the home directory automatically.
Otherwise, you can use the following environment variables:

* ``SWI_HOME_DIR``: The SWI-Prolog home directory. It must contain the ``swipl.home`` file.
  It's the ``$SWI_PROLOG_ROOT/lib/swipl`` directory if you have compiled SWI-Prolog form source.
* ``LIBSWIPL_PATH``: The location of the ``libswipl`` shared library.

You can get the locations mentioned above using the following commands::

    swipl --dump-runtime-variables

That will output something like::

    PLBASE="/home/yuce/swipl-9.3.8/lib/swipl";
    ...
    PLLIBDIR="/home/yuce/swipl-9.3.8/lib/swipl/lib/x86_64-linux";

Use the value in the ``PLBASE`` variable as the value for the ``SWI_HOME_DIR`` environment variable.
Use the value in the ``PLLIBDIR`` variable as the value for the ``LIBSWIPL_PATH`` environment variable.

Arch Linux / Manjaro Linux / Parabola GNU/Linux-libre
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These Linux distributions have PySwip in their package repositories.
You can use the following to install PySwip globally::

    pacman -S python-pyswip

.. NOTE::
    We recommend installing PySwip from :ref:`install_from_pypi`.

Fedora Workstation
^^^^^^^^^^^^^^^^^^

You can use the following to install PySwip globally::

    dnf install python3-pyswip

.. NOTE::
    We recommend installing PySwip from :ref:`install_from_pypi`.

.. _install_swi_prolog:

Installing SWI-Prolog
---------------------

Some operating systems have packages for SWI-Prolog.
Otherwise, you can download it from `SWI-Prolog's website <https://www.swi-prolog.org/Download.html>`_ or build from source.

Arch Linux / Manjaro Linux / Parabola GNU/Linux-libre
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SWI-Prolog is available in the standard package repository::

    pacman -S swi-prolog

Fedora Workstation
^^^^^^^^^^^^^^^^^^

Installing SWI-Prolog::

    dnf install pl

Debian, Ubuntu, Raspbian
^^^^^^^^^^^^^^^^^^^^^^^^

* Ubuntu 22.04 has SWI-Prolog 8.4.3 in its repository.
* Debian Bookworm, Ubuntu 24.04 and Raspberry Pi OS Bookworm have SWI-Prolog 9.0.4 in their repositories.

Use the following to install SWI-Prolog::

    apt install swi-prolog-nox


Windows
-------

Download a recent version of SWI-Prolog from https://www.swi-prolog.org/Download.html and install it.

MacOS
-----

The preferred way of installing SWI-Prolog on MacOS is using `Homebrew <https://brew.sh>`_.

Homebrew
^^^^^^^^

Installing SWI-Prolog::

    brew install swi-prolog


Official SWI-Prolog App
^^^^^^^^^^^^^^^^^^^^^^^

Install SWI-Prolog from https://www.swi-prolog.org/Download.html.

If you get an error like ``libgmp.X not found``, you have to set the ``DYLD_FALLBACK_LIBRARY_PATH`` environment variable before running Python::

    export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/Frameworks

OpenBSD
-------

Install SWI-Prolog using the following on OpenBSD 7.6 and later::

    pkg_add swi-prolog

FreeBSD
-------

SWI-Prolog can be installed using ``pkg``::

    pkg install swi-pl

Test Drive
----------

Run a quick test by running following code at your Python console::


    from pyswip import Prolog
    Prolog.assertz("father(michael,john)")
    print(list(Prolog.query("father(X,Y)")))


