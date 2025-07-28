
__all__ = "PrologError", "NestedQueryError"

class PrologError(Exception):
    pass


class NestedQueryError(PrologError):
    """
    SWI-Prolog does not accept nested queries, that is, opening a query while the previous one was not closed.
    As this error may be somewhat difficult to debug in foreign code, it is automatically treated inside PySwip
    """

    pass
