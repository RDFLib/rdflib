"""GraphDB client module."""

from __future__ import annotations

import httpx

import rdflib.contrib.rdf4j
from rdflib.contrib.rdf4j import RDF4JClient
from rdflib.contrib.rdf4j.exceptions import (
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
)


class Repository(rdflib.contrib.rdf4j.client.Repository):
    """GraphDB Repository client.

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
    """GraphDB Repository Manager"""

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


class GraphDBClient(RDF4JClient):
    """GraphDB Client"""

    # Use the GraphDB RepositoryManager class.
    repository_manager_cls = RepositoryManager
