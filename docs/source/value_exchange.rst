Value Exchange Between Python and Prolog
========================================

String Interpolation from Python to Prolog
------------------------------------------

Currently there's limited support for converting Python values automatically to Prolog via a string interpolation mechanism.
This mechanism is available to be used with the following ``Prolog`` class methods:

* ``assertz``
* ``asserta``
* ``retract``
* ``query``

These methods take one string format argument, and zero or more arguments to replace placeholders with in the format to produce the final string.
Placeholder is ``%p`` for all types.

The following types are recognized:

* String
* Integer
* Float
* Boolean
* ``pyswip.Atom``
* ``pyswip.Variable``
* Lists of the types above

Other types are converted to strings using the ``str`` function.

.. list-table:: String Interpolation to Prolog
    :widths: 50 50
    :header-rows: 1

    * - Python Value
      - String
    * - str ``"Some value"``
      - ``"Some value"``
    * - int ``38``
      - ``38``
    * - float ``38.42``
      - ``38.42``
    * - bool ``True``
      - ``1``
    * - bool ``False``
      - ``0``
    * - ``pyswip.Atom("carrot")``
      - ``'carrot'``
    * - ``pyswip.Variable("Width")``
      - ``Width``
    * - list ``["string", 12, 12.34, Atom("jill")]``
      - ``["string", 12, 12.34, 'jill']``
    * - Other ``value``
      - ``str(value)``


The placeholders are set using ``%p``.

Example:

.. code-block:: python

    ids = [1, 2, 3]
    joe = Atom("joe")
    Prolog.assertz("user(%p,%p)", joe, ids)
    list(Prolog.query("user(%p,IDs)", joe))