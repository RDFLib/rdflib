"""GraphDB exceptions."""


class GraphDBError(Exception):
    """Base class for GraphDB exceptions."""


class ResponseFormatError(GraphDBError):
    """Raised when the response format is invalid."""
