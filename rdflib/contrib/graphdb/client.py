"""GraphDB client module."""

from __future__ import annotations

import typing as t

import httpx

import rdflib.contrib.rdf4j
from rdflib import Graph
from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
    ResponseFormatError,
    UnauthorisedError,
)
from rdflib.contrib.graphdb.models import (
    RepositoryConfigBean,
    RepositoryConfigBeanCreate,
    RepositorySizeInfo,
)
from rdflib.contrib.rdf4j import RDF4JClient


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


class RepositoryManagement:
    """GraphDB Repository Management client."""

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    @property
    def http_client(self):
        return self._http_client

    @t.overload
    def get(
        self,
        repository_id: str,
        content_type: t.Literal["application/json"],
        location: str | None = None,
    ) -> RepositoryConfigBean: ...

    @t.overload
    def get(
        self,
        repository_id: str,
        content_type: None = None,
        location: str | None = None,
    ) -> RepositoryConfigBean: ...

    @t.overload
    def get(
        self,
        repository_id: str,
        content_type: t.Literal["text/turtle"],
        location: str | None = None,
    ) -> Graph: ...

    @t.overload
    def get(
        self,
        repository_id: str,
        content_type: str,
        location: str | None = None,
    ) -> RepositoryConfigBean | Graph: ...

    def get(
        self,
        repository_id: str,
        content_type: str | None = None,
        location: str | None = None,
    ) -> RepositoryConfigBean | Graph:
        """Get a repository's configuration.

        Parameters:
            repository_id: The identifier of the repository.
            content_type: The content type of the response. Can be `application/json` or
                `text/turtle`. Defaults to `application/json`.
            location: The location of the repository.

        Returns:
            RepositoryConfigBean: The repository configuration.
            Graph: The repository configuration in RDF.

        Raises:
            BadRequest: If the content type is not supported.
            ResponseFormatError: If the response cannot be parsed.
            RepositoryNotFoundError: If the repository is not found.
            InternalServerError: If the server returns an internal error.
        """
        if content_type is None:
            content_type = "application/json"
        if content_type not in ("application/json", "text/turtle"):
            raise ValueError(f"Unsupported content type: {content_type}.")
        headers = {"Accept": content_type}
        params = {}
        if location is not None:
            params["location"] = location
        try:
            response = self.http_client.get(
                f"/rest/repositories/{repository_id}", headers=headers, params=params
            )
            response.raise_for_status()

            if content_type == "application/json":
                try:
                    return RepositoryConfigBean(**response.json())
                except (ValueError, TypeError) as err:
                    raise ResponseFormatError(
                        "Failed to parse GraphDB response."
                    ) from err
            elif content_type == "text/turtle":
                try:
                    return Graph().parse(data=response.text, format="turtle")
                except Exception as err:
                    raise ResponseFormatError(f"Error parsing RDF: {err}") from err
            else:
                raise ValueError(f"Unhandled content type: {content_type}.")
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 404:
                raise RepositoryNotFoundError(
                    f"Repository {repository_id} not found."
                ) from err
            elif err.response.status_code == 500:
                raise InternalServerError("Internal server error.") from err
            raise

    def edit(self, repository_id: str, config: RepositoryConfigBeanCreate) -> None:
        """Edit a repository's configuration.

        Parameters:
            repository_id: The identifier of the repository.
            config: The repository configuration.

        Raises:
            BadRequest: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
        """
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = self.http_client.put(
                f"/rest/repositories/{repository_id}",
                headers=headers,
                json=config.to_dict(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            elif err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            elif err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            elif err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def delete(self, repository_id: str, location: str | None = None) -> None:
        """Delete a repository.

        Parameters:
            repository_id: The identifier of the repository.
            location: The location of the repository.

        Raises:
            BadRequest: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
        """
        params = {}
        if location is not None:
            params["location"] = location
        try:
            response = self.http_client.delete(
                f"/rest/repositories/{repository_id}", params=params
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            elif err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            elif err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            elif err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def restart(
        self, repository_id: str, sync: bool | None = None, location: str | None = None
    ) -> str:
        """Restart a repository.

        Parameters:
            repository_id: The identifier of the repository.
            sync: Whether to sync the repository.
            location: The location of the repository.

        Returns:
            str: The response text.

        Raises:
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            RepositoryNotFoundError: If the repository is not found.
        """
        params = {}
        if sync is not None:
            params["sync"] = str(sync).lower()
        if location is not None:
            params["location"] = location
        try:
            response = self.http_client.post(
                f"/rest/repositories/{repository_id}/restart", params=params
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 401:
                raise UnauthorisedError("Request is unauthorised.") from err
            elif err.response.status_code == 403:
                raise ForbiddenError("Request is forbidden.") from err
            elif err.response.status_code == 404:
                raise RepositoryNotFoundError(
                    f"Repository {repository_id} not found."
                ) from err
            raise

    def size(
        self, repository_id: str, location: str | None = None
    ) -> RepositorySizeInfo:
        """Get repository size.

        Parameters:
            repository_id: The identifier of the repository.
            location: The location of the repository.

        Raises:
            ResponseFormatError: If the response cannot be parsed.
        """
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


class TalkToYourGraph:
    """GraphDB Talk to Your Graph client."""

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    @property
    def http_client(self):
        return self._http_client

    def query(self, agent_id: str, tool_type: str, query: str) -> str:
        """Call agent query method/assistant tool.

        Parameters:
            agent_id: The agent identifier.
            tool_type: The tool type.
            query: The query for the tool.
        """
        headers = {"Content-Type": "text/plain", "Accept": "text/plain"}
        response = self.http_client.post(
            f"/rest/ttyg/agents/{agent_id}/{tool_type}", headers=headers, content=query
        )
        response.raise_for_status()
        return response.text


class GraphDBClient(RDF4JClient):
    """GraphDB Client"""

    # Use the GraphDB RepositoryManager class.
    repository_manager_cls = RepositoryManager

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str] | None = None,
        timeout: float = 30.0,
        **kwargs: t.Any,
    ):
        super().__init__(base_url, auth, timeout, **kwargs)
        self._repos: RepositoryManagement | None = None
        self._ttyg: TalkToYourGraph | None = None

    @property
    def repos(self) -> RepositoryManagement:
        if self._repos is None:
            self._repos = RepositoryManagement(self.http_client)
        return self._repos

    @property
    def ttyg(self):
        if self._ttyg is None:
            self._ttyg = TalkToYourGraph(self.http_client)
        return self._ttyg
