from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


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


@dataclass(frozen=True)
class RepositoryResult:
    """RDF4J repository result object."""

    identifier: str
    uri: str
    readable: bool
    writable: bool
    title: str | None = None


class Repository:
    def __init__(self, identifier: str, http_client: httpx.Client):
        """RDF4J repository client."""
        self._identifier = identifier
        self._http_client = http_client

    @property
    def identifier(self):
        """Repository identifier."""
        return self._identifier

    def health(self) -> bool:
        """Check if the repository is healthy.

        :returns: Returns True if the repository is healthy, otherwise an error is raised.
        :raises httpx.RequestError: On network/connection issues.
        :raises RepositoryNotFoundError: If the repository is not found.
        :raises RepositoryNotHealthyError: If the repository is not healthy.
        """
        headers = {
            "Content-Type": "application/sparql-query",
            "Accept": "application/sparql-results+json",
        }
        try:
            response = self._http_client.post(
                f"/repositories/{self._identifier}", headers=headers, content="ASK {}"
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 404:
                raise RepositoryNotFoundError(
                    f"Repository {self._identifier} not found."
                )
            raise RepositoryNotHealthyError(
                f"Repository {self._identifier} is not healthy. {err.response.status_code} - {err.response.text}"
            )
        except httpx.RequestError:
            raise


class RepositoryManager:
    """Client to manage server-level repository operations.

    This includes listing, creating, and deleting of repositories.
    """

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    def list(self) -> list[RepositoryResult]:
        """List all available repositories.

        :returns: List of repository results.
        :raises httpx.RequestError: On network/connection issues.
        :raises RepositoryFormatError: If the response format is unrecognized.
        """
        headers = {
            "Accept": "application/sparql-results+json",
        }
        try:
            response = self._http_client.get("/repositories", headers=headers)
            response.raise_for_status()

            try:
                data = response.json()
                results = data["results"]["bindings"]
                return [
                    RepositoryResult(
                        identifier=repo["id"]["value"],
                        uri=repo["uri"]["value"],
                        readable=repo["readable"]["value"],
                        writable=repo["writable"]["value"],
                        title=repo.get("title", {}).get("value"),
                    )
                    for repo in results
                ]
            except (KeyError, ValueError) as err:
                raise RepositoryFormatError(f"Unrecognised response format: {err}")
        except httpx.RequestError:
            raise

    def get(self, repository_id: str) -> Repository:
        """Get a repository by ID.

        This performs a health check before returning the repository object.

        :param repository_id: The identifier of the repository.
        :returns: The repository instance.
        :raises httpx.RequestError: On network/connection issues.
        :raises RepositoryNotFoundError: If the repository is not found.
        :raises RepositoryNotHealthyError: If the repository is not healthy.
        """
        repo = Repository(repository_id, self._http_client)
        try:
            repo.health()
            return repo
        except (httpx.RequestError, RepositoryNotFoundError, RepositoryNotHealthyError):
            raise

    def create(
        self, repository_id: str, data: str, format: str = "text/turtle"
    ) -> Repository:
        """Create a new repository.

        :param repository_id: The identifier of the repository.
        :param data: The repository configuration in RDF.
        :param format: The repository configuration format.
        :raises httpx.RequestError: On network/connection issues.
        :raises RepositoryAlreadyExistsError: If the repository already exists.
        :raises RepositoryNotHealthyError: If the repository is not healthy.
        """
        try:
            headers = {"Content-Type": format}
            response = self._http_client.put(
                f"/repositories/{repository_id}", headers=headers, content=data
            )
            response.raise_for_status()
            return self.get(repository_id)
        except httpx.RequestError:
            raise
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 409:
                raise RepositoryAlreadyExistsError(
                    f"Repository {repository_id} already exists."
                )
            raise

    def delete(self, repository_id: str) -> None:
        """Delete a repository.

        :param repository_id: The identifier of the repository.
        :raises httpx.RequestError: On network/connection issues.
        :raises RepositoryNotFoundError: If the repository is not found.
        :raises RepositoryError: If the repository is not deleted successfully.
        """
        try:
            response = self._http_client.delete(f"/repositories/{repository_id}")
            response.raise_for_status()
            if response.status_code != 204:
                raise RepositoryError(
                    f"Unexpected response status code when deleting repository {repository_id}: {response.status_code} - {response.text.strip()}"
                )
        except httpx.RequestError:
            raise
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 404:
                raise RepositoryNotFoundError(f"Repository {repository_id} not found.")
            raise


class RDF4JClient:
    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """RDF4J client.

        :param base_url: The base URL of the RDF4J server.
        :param auth: Authentication tuple (username, password).
        :param timeout: Request timeout in seconds (default: 30.0).
        :param kwargs: Additional keyword arguments to pass to the httpx.Client.
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self._http_client = httpx.Client(
            base_url=base_url, auth=auth, timeout=timeout, **kwargs
        )
        self._repository_manager = RepositoryManager(self._http_client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def repositories(self):
        """Server-level repository management operations."""
        return self._repository_manager

    def close(self):
        self._http_client.close()
