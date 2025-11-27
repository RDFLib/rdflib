"""GraphDB client module."""

from __future__ import annotations

from typing import Any

import httpx

import rdflib.contrib.rdf4j
from rdflib.contrib.graphdb.exceptions import ResponseFormatError
from rdflib.contrib.graphdb.models import RepositorySizeInfo
from rdflib.contrib.rdf4j import RDF4JClient
from rdflib.contrib.rdf4j.exceptions import (
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
)


class Repository(rdflib.contrib.rdf4j.client.Repository):
    """GraphDB Repository client.

    Overrides specific methods of the RDF4J Repository class.

    Parameters:
        identifier: The identifier of the repository.
        http_client: The httpx.Client instance.
    """

    def health(self, timeout: int = 5) -> bool:
        """Repository health check.

        Parameters:
            timeout: A timeout parameter in seconds. If provided, the endpoint attempts
                to retrieve the repository within this timeout. If not, the passive
                check is performed.

        Returns:
            bool: True if the repository is healthy, otherwise an error is raised.

        Raises:
            RepositoryNotFoundError: If the repository is not found.
            RepositoryNotHealthyError: If the repository is not healthy.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        try:
            params = {"passive": str(timeout)}
            response = self.http_client.get(
                f"/repositories/{self.identifier}/health", params=params
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


class RepositoryManager(rdflib.contrib.rdf4j.client.RepositoryManager):
    """GraphDB Repository Manager.

    Overrides specific methods of the RDF4J RepositoryManager class.
    """

    def get(self, repository_id: str) -> Repository:
        """Get a repository by ID.

        !!! Note
            This performs a health check before returning the repository object.

        Parameters:
            repository_id: The identifier of the repository.

        Returns:
            Repository: The repository instance.

        Raises:
            RepositoryNotFoundError: If the repository is not found.
            RepositoryNotHealthyError: If the repository is not healthy.
        """
        _repo = super().get(repository_id)
        return Repository(_repo.identifier, _repo.http_client)


class GraphDB:
    """GraphDB REST API client."""

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    @property
    def http_client(self):
        return self._http_client

    def size(self, repository_id: str, location: str | None = None):
        params = {}
        if location:
            params["location"] = location
        response = self.http_client.get(
            f"/rest/repositories/{repository_id}/size", params=params
        )
        response.raise_for_status()
        try:
            return RepositorySizeInfo(**response.json())
        except (ValueError, TypeError) as err:
            raise ResponseFormatError("Failed to parse GraphDB response.") from err


class GraphDBClient(RDF4JClient):
    """GraphDB Client"""

    # Use the GraphDB RepositoryManager class.
    repository_manager_cls = RepositoryManager

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        super().__init__(base_url, auth, timeout, **kwargs)
        self._graphdb: GraphDB | None = None

    @property
    def graphdb(self):
        if self._graphdb is None:
            self._graphdb = GraphDB(self.http_client)
        return self._graphdb
