import sys


def test_stderr_is_none():
    """
    Issue 1761 - Issues with installing rdflib
    Due to standard input/output overwrites, there is possibility that `sys.stderr.isatty`
    raises `AttributeError`. So it should be checked before executing.
    """
    sys.stderr = None
    import rdflib
