"""RDF4J client module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from rdflib.contrib.rdf4j.exceptions import (
    RDF4JUnsupportedProtocolError,
    RepositoryAlreadyExistsError,
    RepositoryError,
    RepositoryFormatError,
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
)


@dataclass(frozen=True)
class RepositoryListingResult:
    """RDF4J repository listing result.

    Parameters:
        identifier: Repository identifier.
        uri: Repository URI.
        readable: Whether the repository is readable by the client.
        writable: Whether the repository is writable by the client.
        title: Repository title.
    """

    identifier: str
    uri: str
    readable: bool
    writable: bool
    title: str | None = None


class Repository:
    """RDF4J repository client.

    Parameters:
        identifier: The identifier of the repository.
        http_client: The httpx.Client instance.
    """

    def __init__(self, identifier: str, http_client: httpx.Client):
        self._identifier = identifier
        self._http_client = http_client

    @property
    def identifier(self):
        """Repository identifier."""
        return self._identifier

    def health(self) -> bool:
        """Repository health check.

        Returns:
            bool: True if the repository is healthy, otherwise an error is raised.

        Raises:
            RepositoryNotFoundError: If the repository is not found.
            RepositoryNotHealthyError: If the repository is not healthy.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
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
    """A client to manage server-level repository operations."""

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    def list(self) -> list[RepositoryListingResult]:
        """List all available repositories.

        Returns:
            list[RepositoryListingResult]: List of repository results.

        Raises:
            RepositoryFormatError: If the response format is unrecognized.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
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
                    RepositoryListingResult(
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
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    def get(self, repository_id: str) -> Repository:
        """Get a repository by ID.

        !!! note
            This performs a health check before returning the repository object.

        Parameters:
            repository_id: The identifier of the repository.

        Returns:
            Repository: The repository instance.

        Raises:
            RepositoryNotFoundError: If the repository is not found.
            RepositoryNotHealthyError: If the repository is not healthy.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        repo = Repository(repository_id, self._http_client)
        try:
            repo.health()
            return repo
        except (RepositoryNotFoundError, RepositoryNotHealthyError, httpx.RequestError):
            raise

    def create(
        self, repository_id: str, data: str, format: str = "text/turtle"
    ) -> Repository:
        """Create a new repository.

        Parameters:
            repository_id: The identifier of the repository.
            data: The repository configuration in RDF.
            format: The repository configuration format.

        Raises:
            RepositoryAlreadyExistsError: If the repository already exists.
            RepositoryNotHealthyError: If the repository is not healthy.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
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

        Parameters:
            repository_id: The identifier of the repository.

        Raises:
            RepositoryNotFoundError: If the repository is not found.
            RepositoryError: If the repository is not deleted successfully.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
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
    """RDF4J client.

    Parameters:
        base_url: The base URL of the RDF4J server.
        auth: Authentication tuple (username, password).
        timeout: Request timeout in seconds (default: 30.0).
        kwargs: Additional keyword arguments to pass to the httpx.Client.
    """

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        if not base_url.endswith("/"):
            base_url += "/"
        self._http_client = httpx.Client(
            base_url=base_url, auth=auth, timeout=timeout, **kwargs
        )
        if self.protocol < 12:
            self.close()
            raise RDF4JUnsupportedProtocolError(
                f"RDF4J server protocol version {self.protocol} is not supported. Minimum required version is 12."
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

    @property
    def protocol(self) -> float:
        try:
            response = self._http_client.get(
                "/protocol", headers={"Accept": "text/plain"}
            )
            response.raise_for_status()
            return float(response.text.strip())
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    def close(self):
        """Close the underlying httpx.Client."""
        self._http_client.close()
