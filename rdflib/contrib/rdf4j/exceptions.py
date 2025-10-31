"""RDF4J exceptions."""


class RepositoryError(Exception):
    """Raised when interactions on a repository result in an error."""


class RepositoryFormatError(RepositoryError):
    """Raised when the repository format is invalid."""


class RepositoryNotFoundError(RepositoryError):
    """Raised when the repository is not found."""


class RepositoryNotHealthyError(RepositoryError):
    """Raised when the repository is not healthy."""


class RepositoryAlreadyExistsError(RepositoryError):
    """Raised when the repository already exists."""


class RDF4JUnsupportedProtocolError(Exception):
    """Raised when the server does not support the protocol version."""
