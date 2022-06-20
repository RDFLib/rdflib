"""
TODO:
"""

__all__ = [
    "Error",
    "ParserError",
    "ResolutionError",
    "ResolutionForbiddenError",
]


class Error(Exception):
    """Base class for rdflib exceptions."""

    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        self.msg = msg


class ParserError(Error):
    """RDF Parser error."""

    def __init__(self, msg):
        Error.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ResolutionError(Error):
    """Resolution error.

    This includes the case when the URI scheme is not supported.
    """

    def __init__(self, msg):
        Error.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class ResolutionForbiddenError(Error):
    """Resolution of the given URL is not allowed."""

    def __init__(self, url):
        Error.__init__(self, self.__doc__)
        self.url = url

    def __str__(self):
        return f"Resolution of '{self.url}' is not allowed."


class UniquenessError(Error):
    """A uniqueness assumption was made in the context, and that is not true"""

    def __init__(self, values):
        Error.__init__(
            self,
            "\
Uniqueness assumption is not fulfilled. Multiple values are: %s"
            % values,
        )
