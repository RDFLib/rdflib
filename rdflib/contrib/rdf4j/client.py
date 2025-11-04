"""RDF4J client module."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from typing import Any, BinaryIO, Iterable

import httpx

from rdflib import BNode
from rdflib.contrib.rdf4j.exceptions import (
    RDF4JUnsupportedProtocolError,
    RDFLibParserError,
    RepositoryAlreadyExistsError,
    RepositoryError,
    RepositoryFormatError,
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
)
from rdflib.contrib.rdf4j.util import (
    build_context_param,
    build_infer_param,
    build_spo_param,
    rdf_payload_to_stream,
)
from rdflib.graph import Dataset, Graph
from rdflib.term import IdentifiedNode, Literal, URIRef

SubjectType = t.Union[IdentifiedNode, None]
PredicateType = t.Union[URIRef, None]
ObjectType = t.Union[IdentifiedNode, Literal, None]


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
    def http_client(self):
        return self._http_client

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
            response = self.http_client.post(
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

    def size(
        self, graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None = None
    ) -> int:
        """The number of statements in the repository or in the specified graph name.

        Args:
            graph_name: Graph name(s) to restrict to.

                Default value `None` queries all graphs.

                To query just the default graph, use
                [`DATASET_DEFAULT_GRAPH_ID`][rdflib.graph.DATASET_DEFAULT_GRAPH_ID].

        Returns:
            The number of statements.

        Raises:
            RepositoryFormatError: Fails to parse the repository size.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        params = {}
        build_context_param(params, graph_name)
        try:
            response = self.http_client.get(
                f"/repositories/{self.identifier}/size", params=params
            )
            response.raise_for_status()
            try:
                value = int(response.text)
                if value >= 0:
                    return value
                raise ValueError(f"Invalid repository size: {value}")
            except ValueError as err:
                raise RepositoryFormatError(
                    f"Failed to parse repository size: {err}"
                ) from err
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    def graphs(self) -> list[IdentifiedNode]:
        """Get a list of all graph names in the repository.

        Returns:
            A list of graph names.

        Raises:
            RepositoryFormatError: Fails to parse the repository graph names.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        try:
            headers = {
                "Accept": "application/sparql-results+json",
            }
            response = self.http_client.get(
                f"/repositories/{self.identifier}/contexts", headers=headers
            )
            response.raise_for_status()
            try:
                values = []
                for row in response.json()["results"]["bindings"]:
                    value = row["contextID"]["value"]
                    value_type = row["contextID"]["type"]
                    if value_type == "uri":
                        values.append(URIRef(value))
                    elif value_type == "bnode":
                        values.append(BNode(value))
                    else:
                        raise ValueError(f"Invalid graph name type: {value_type}")
                return values
            except Exception as err:
                raise RepositoryFormatError(
                    f"Failed to parse repository graph names: {err}"
                ) from err
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    def get(
        self,
        subj: SubjectType = None,
        pred: PredicateType = None,
        obj: ObjectType = None,
        graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None = None,
        infer: bool = True,
        content_type: str | None = None,
    ) -> Graph | Dataset:
        """Get RDF statements from the repository matching the filtering parameters.

        Args:
            subj: Subject of the statement to filter by, or `None` to match all.
            pred: Predicate of the statement to filter by, or `None` to match all.
            obj: Object of the statement to filter by, or `None` to match all.
            graph_name: Graph name(s) to restrict to.

                Default value `None` queries all graphs.

                To query just the default graph, use
                [`DATASET_DEFAULT_GRAPH_ID`][rdflib.graph.DATASET_DEFAULT_GRAPH_ID].

            infer: Specifies whether inferred statements should be included in the result.
            content_type: The content type of the response.
                A triple-based format returns a [Graph][rdflib.graph.Graph], while a
                quad-based format returns a [`Dataset`][rdflib.graph.Dataset].

        Returns:
            A [`Graph`][rdflib.graph.Graph] or [`Dataset`][rdflib.graph.Dataset] object.

        Raises:
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        if content_type is None:
            content_type = "application/n-quads"
        headers = {"Accept": content_type}
        params = {}
        build_context_param(params, graph_name)
        build_spo_param(params, subj, pred, obj)
        build_infer_param(params, infer=infer)

        try:
            response = self.http_client.get(
                f"/repositories/{self.identifier}/statements",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            triple_formats = [
                "application/n-triples",
                "text/turtle",
                "application/rdf+xml",
            ]
            try:
                if content_type in triple_formats:
                    return Graph().parse(data=response.text, format=content_type)
                return Dataset().parse(data=response.text, format=content_type)
            except Exception as err:
                raise RDFLibParserError(f"Error parsing RDF: {err}") from err
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    # TODO: This only covers appending statements to a repository.
    #       We still need to implement sparql update and transaction document.
    def upload(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        base_uri: str | None = None,
        content_type: str | None = None,
    ):
        """Upload and append statements to the repository."""
        # TODO: docstring
        stream, should_close = rdf_payload_to_stream(data)
        try:
            headers = {"Content-Type": content_type or "application/n-quads"}
            params = {}
            if base_uri is not None:
                params["baseURI"] = base_uri
            response = self.http_client.post(
                f"/repositories/{self.identifier}/statements",
                headers=headers,
                params=params,
                content=stream,
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise
        finally:
            if should_close:
                stream.close()

    def overwrite(
        self,
        data: str | bytes | BinaryIO | Graph | Dataset,
        graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None = None,
        base_uri: str | None = None,
        content_type: str | None = None,
    ):
        # TODO: Add docstring.
        stream, should_close = rdf_payload_to_stream(data)

        try:
            headers = {"Content-Type": content_type or "application/n-quads"}
            params = {}
            build_context_param(params, graph_name)
            if base_uri is not None:
                params["baseURI"] = base_uri
            response = self.http_client.put(
                f"/repositories/{self.identifier}/statements",
                headers=headers,
                params=params,
                content=stream,
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise
        finally:
            if should_close:
                stream.close()

    def delete(
        self,
        subj: SubjectType = None,
        pred: PredicateType = None,
        obj: ObjectType = None,
        graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None = None,
    ) -> None:
        """Deletes statements from the repository matching the filtering parameters.

        Args:
            subj: Subject of the statement to filter by, or `None` to match all.
            pred: Predicate of the statement to filter by, or `None` to match all.
            obj: Object of the statement to filter by, or `None` to match all.
            graph_name: Graph name(s) to restrict to.

                Default value `None` queries all graphs.

                To query just the default graph, use
                [`DATASET_DEFAULT_GRAPH_ID`][rdflib.graph.DATASET_DEFAULT_GRAPH_ID].

        Raises:
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        params = {}
        build_context_param(params, graph_name)
        build_spo_param(params, subj, pred, obj)

        try:
            response = self.http_client.delete(
                f"/repositories/{self.identifier}/statements",
                params=params,
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise


class RepositoryManager:
    """A client to manage server-level repository operations."""

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    @property
    def http_client(self):
        return self._http_client

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
            response = self.http_client.get("/repositories", headers=headers)
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

        !!! Note
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
        repo = Repository(repository_id, self.http_client)
        try:
            repo.health()
            return repo
        except (RepositoryNotFoundError, RepositoryNotHealthyError, httpx.RequestError):
            raise

    def create(
        self, repository_id: str, data: str, content_type: str = "text/turtle"
    ) -> Repository:
        """Create a new repository.

        Parameters:
            repository_id: The identifier of the repository.
            data: The repository configuration in RDF.
            content_type: The repository configuration content type.

        Raises:
            RepositoryAlreadyExistsError: If the repository already exists.
            RepositoryNotHealthyError: If the repository is not healthy.
            httpx.RequestError: On network/connection issues.
            httpx.HTTPStatusError: Unhandled status code error.
        """
        try:
            headers = {"Content-Type": content_type}
            response = self.http_client.put(
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
            response = self.http_client.delete(f"/repositories/{repository_id}")
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
        self._repository_manager = RepositoryManager(self.http_client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def http_client(self):
        return self._http_client

    @property
    def repositories(self):
        """Server-level repository management operations."""
        return self._repository_manager

    @property
    def protocol(self) -> float:
        try:
            response = self.http_client.get(
                "/protocol", headers={"Accept": "text/plain"}
            )
            response.raise_for_status()
            return float(response.text.strip())
        except (httpx.RequestError, httpx.HTTPStatusError):
            raise

    def close(self):
        """Close the underlying httpx.Client."""
        self.http_client.close()
