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


class RDFLibParserError(Exception):
    """Raised when there is an error parsing the RDF document."""


class RepositoryTransactionError(Exception):
    """Raised when there is an error with the transaction."""


class TransactionClosedError(RepositoryTransactionError):
    """Raised when the transaction has been closed."""


class TransactionPingError(RepositoryTransactionError):
    """Raised when there is an error pinging the transaction."""


class TransactionCommitError(RepositoryTransactionError):
    """Raised when there is an error committing the transaction."""


class TransactionRollbackError(RepositoryTransactionError):
    """Raised when there is an error rolling back the transaction."""
