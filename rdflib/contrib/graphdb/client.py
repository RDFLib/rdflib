"""GraphDB client module."""

from __future__ import annotations

import typing as t

import httpx

import rdflib.contrib.rdf4j
from rdflib import Graph, Literal, URIRef
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
    AccessControlEntry,
    ClearGraphAccessControlEntry,
    GraphDBRepository,
    PluginAccessControlEntry,
    RepositoryConfigBean,
    RepositoryConfigBeanCreate,
    RepositorySizeInfo,
    StatementAccessControlEntry,
    SystemAccessControlEntry,
    _parse_operation,
    _parse_plugin,
    _parse_policy,
    _parse_role,
)
from rdflib.contrib.rdf4j import RDF4JClient

FileContent = t.Union[
    bytes,
    str,
    t.IO[bytes],
    t.Tuple[t.Optional[str], t.Union[bytes, str, t.IO[bytes]]],
    t.Tuple[t.Optional[str], t.Union[bytes, str, t.IO[bytes]], t.Optional[str]],
]

FilesType = t.Union[
    t.Mapping[str, FileContent],
    t.Iterable[t.Tuple[str, FileContent]],
]

_ALLOWED_FGAC_SCOPES = {"statement", "clear_graph", "plugin", "system"}


class FGACRulesManager:
    """GraphDB Fine-Grained Access Control Rules Manager."""

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

    def list(
        self,
        scope: t.Literal["statement", "clear_graph", "plugin", "system"] | None = None,
        operation: t.Literal["read", "write", "*"] | None = None,
        subject: str | URIRef | None = None,
        predicate: str | URIRef | None = None,
        obj: str | URIRef | Literal | None = None,
        graph: t.Literal["*", "named", "default"] | URIRef | Graph | None = None,
        plugin: str | None = None,
        role: str | None = None,
        policy: t.Literal["allow", "deny", "abstain"] | None = None,
    ) -> t.List[
        SystemAccessControlEntry
        | StatementAccessControlEntry
        | PluginAccessControlEntry
        | ClearGraphAccessControlEntry
    ]:
        """
        List ACL rules for the repository.

        Parameters:
            scope: The scope of the FGAC rule (`statement`, `clear_graph`, `plugin`, `system`).
            operation: The operation of the FGAC rule (`read`, `write`, `*`).
            subject: The subject of the FGAC rule in Turtle format (for example, `<http://example.com/Mary>`).
            predicate: The predicate of the FGAC rule in Turtle format (for example, `<http://www.w3.org/2000/01/rdf-schema#label>`).
            obj: The object of the FGAC rule in Turtle format (for example, `"Mary"@en`).
            graph: The graph of the FGAC rule in Turtle format (for example, `<http://example.org/graphs/graph1>`).
            plugin: The plugin name for the FGAC rule with plugin scope (for example, `elasticsearch-connector`).
            role: The role associated with the FGAC rule.
            policy: The policy for the FGAC rule (`allow`, `deny`, `abstain`).

        Returns:
            A list of FGAC rules.

        Raises:
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
            ResponseFormatError: If the response cannot be parsed.
        """
        params: dict[str, str] = {}
        if scope is not None:
            if scope not in _ALLOWED_FGAC_SCOPES:
                raise ValueError(f"Invalid FGAC scope filter: {scope!r}")
            params["scope"] = scope
        if operation is not None:
            params["operation"] = _parse_operation(operation)
        if subject is not None:
            if isinstance(subject, URIRef):
                params["subject"] = subject.n3()
            elif isinstance(subject, str):
                params["subject"] = subject
            else:
                raise ValueError(f"Invalid FGAC subject filter: {subject!r}")
        if predicate is not None:
            if isinstance(predicate, URIRef):
                params["predicate"] = predicate.n3()
            elif isinstance(predicate, str):
                params["predicate"] = predicate
            else:
                raise ValueError(f"Invalid FGAC predicate filter: {predicate!r}")
        if obj is not None:
            if isinstance(obj, (URIRef, Literal)):
                params["object"] = obj.n3()
            elif isinstance(obj, str):
                params["object"] = obj
            else:
                raise ValueError(f"Invalid FGAC object filter: {obj!r}")
        if graph is not None:
            if isinstance(graph, URIRef):
                params["context"] = graph.n3()
            elif isinstance(graph, Graph):
                params["context"] = graph.identifier.n3()
            elif isinstance(graph, str):
                params["context"] = graph
            else:
                raise ValueError(f"Invalid FGAC graph filter: {graph!r}")
        if plugin is not None:
            params["plugin"] = _parse_plugin(plugin)
        if role is not None:
            params["role"] = _parse_role(role)
        if policy is not None:
            params["policy"] = _parse_policy(policy)

        try:
            response = self._http_client.get(
                f"/rest/repositories/{self.identifier}/acl", params=params
            )
            response.raise_for_status()
            try:
                payload = response.json()
            except (ValueError, TypeError) as err:
                raise ResponseFormatError(
                    f"Failed to parse GraphDB response: {err}"
                ) from err

            if not isinstance(payload, list):
                raise ResponseFormatError(
                    "Failed to parse GraphDB response: expected a list of ACL entries."
                )

            try:
                return [AccessControlEntry.from_dict(acl) for acl in payload]
            except (ValueError, TypeError) as err:
                raise ResponseFormatError(
                    f"Failed to parse GraphDB response: {err}"
                ) from err
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            if err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def set(self, acl_rules: t.Sequence[AccessControlEntry]):
        """
        Set ACL rules for the repository.

        !!! Note
            This method overwrites existing ACL rules in the repository.
            If you want to add new rules without overwriting existing ones,
            use the [`add`][rdflib.contrib.graphdb.client.FGACRulesManager.add] method.

        Parameters:
            acl_rules: The list of ACL rules to set.

        Raises:
            BadRequestError: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
            ValueError: If the ACL rules are not provided as a sequence or are not AccessControlEntry instances.
        """
        acl_rules_list = list(acl_rules)
        if any(not isinstance(rule, AccessControlEntry) for rule in acl_rules_list):
            raise ValueError("All ACL rules must be AccessControlEntry instances.")

        payload = [rule.as_dict() for rule in acl_rules_list]
        headers = {"Content-Type": "application/json"}
        try:
            response = self._http_client.put(
                f"/rest/repositories/{self.identifier}/acl",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            if err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            if err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def add(self, acl_rules: t.Sequence[AccessControlEntry], position: int | None = None):
        """
        Add ACL rules to the repository.

        You can also provide an optional URL request parameter position that specifies the position of the rules to be added.
        The position is zero-based (0 is the first position). If the position parameter is not provided, the rules are added at
        the end of the list.

        Parameters:
            acl_rules: The list of ACL rules to add.
            position: The zero-based position to add the rules at.

        Raises:
            BadRequestError: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
            ValueError: If the position is not an integer or is a negative integer.
            ValueError: If the ACL rules are not provided as a sequence or are not AccessControlEntry instances.
        """
        acl_rules_list = list(acl_rules)
        if any(not isinstance(rule, AccessControlEntry) for rule in acl_rules_list):
            raise ValueError("All ACL rules must be AccessControlEntry instances.")

        payload = [rule.as_dict() for rule in acl_rules_list]
        headers = {"Content-Type": "application/json"}
        params = {}
        if position is not None:
            if not isinstance(position, int):
                raise ValueError("Position must be an integer.")
            if position < 0:
                raise ValueError("Position must be a positive integer.")
            params["position"] = str(position)
        try:
            response = self._http_client.post(
                f"/rest/repositories/{self.identifier}/acl",
                headers=headers,
                json=payload,
                params=params,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            if err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            if err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def delete(self, acl_rules: t.Sequence[AccessControlEntry]):
        """
        Delete ACL rules from the repository.

        The provided FGAC rules are removed from the list regardless of their position.

        Parameters:
            acl_rules: The list of ACL rules to delete.

        Raises:
            BadRequestError: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
            ValueError: If the ACL rules are not provided as a sequence or are not AccessControlEntry instances.
        """
        acl_rules_list = list(acl_rules)
        if any(not isinstance(rule, AccessControlEntry) for rule in acl_rules_list):
            raise ValueError("All ACL rules must be AccessControlEntry instances.")

        payload = [rule.as_dict() for rule in acl_rules_list]
        headers = {"Content-Type": "application/json"}
        try:
            response = self._http_client.delete(
                f"/rest/repositories/{self.identifier}/acl",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            if err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            if err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise


class Repository(rdflib.contrib.rdf4j.client.Repository):
    """GraphDB Repository client.

    Overrides specific methods of the RDF4J Repository class and also provides GraphDB-only functionality
    (such as FGAC ACL management) made available through the GraphDB REST API.

    Parameters:
        identifier: The identifier of the repository.
        http_client: The httpx.Client instance.
    """

    def __init__(self, identifier: str, http_client: httpx.Client):
        super().__init__(identifier, http_client)
        self._fgac_rules_manager: FGACRulesManager | None = None

    @property
    def acl_rules(self) -> FGACRulesManager:
        if self._fgac_rules_manager is None:
            self._fgac_rules_manager = FGACRulesManager(
                self.identifier, self.http_client
            )
        return self._fgac_rules_manager

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

    This manager client overrides specific RDF4J RepositoryManager class methods to provide GraphDB-specific implementations.
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
    """GraphDB Repository Management client.

    The functionality provided by this management client accepts an optional location parameter to operate on external
    GraphDB locations.
    """

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    def list(self, location: str | None = None) -> list[GraphDBRepository]:
        """List all repositories.

        Parameters:
            location: The location of the repositories.

        Returns:
            list[GraphDBRepository]: List of GraphDB repositories.

        Raises:
            InternalServerError: If the server returns an internal error.
            ResponseFormatError: If the response cannot be parsed.
        """
        params = {}
        if location is not None:
            params["location"] = location
        response = self.http_client.get("/rest/repositories", params=params)
        response.raise_for_status()
        try:
            return [GraphDBRepository.from_dict(repo) for repo in response.json()]
        except (ValueError, TypeError) as err:
            raise ResponseFormatError(
                f"Failed to parse GraphDB response: {err}"
            ) from err
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

    def create(
        self,
        config: RepositoryConfigBeanCreate | str,
        location: str | None = None,
        files: FilesType | None = None,
    ):
        """Create a new repository.

        Parameters:
            config: Repository configuration. When a `RepositoryConfigBeanCreate` is
                provided, the request is sent as JSON. When a string is provided, it
                is treated as Turtle content and sent as multipart/form-data part
                `config` (required by GraphDB) with the content type `text/turtle`.
            location: Optional repository location (query param `location`).
            files: Optional extra multipart parts for GraphDB-specific files (e.g.
                `obdaFile`, `owlFile`, `propertiesFile`, `constraintFile`,
                `dbMetadataFile`, `lensesFile`). Keys must be the form part names;
                values may be file content or httpx-style file tuples. Ignored when
                `config` is a dataclass (JSON payload).

        Raises:
            BadRequestError: If the request is invalid.
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
        """
        params = {}
        if location is not None:
            params["location"] = location

        def _normalize_file_content(field: str, value: FileContent) -> FileContent:
            if isinstance(value, tuple):
                # fill in the missing filename with the field name
                if len(value) == 2:
                    filename, content = value
                    return (filename or field, content)
                filename, content, content_type = value
                return (filename or field, content, content_type)
            return (field, value)

        try:
            if isinstance(config, str):
                extra_parts: list[tuple[str, FileContent]] = []
                if files is not None:
                    if isinstance(files, t.Mapping):
                        extra_parts = list(files.items())
                    else:
                        extra_parts = list(files)

                    if any(field == "config" for field, _ in extra_parts):
                        raise ValueError(
                            "Do not pass a 'config' multipart part via files; use the config argument instead."
                        )

                multipart_files: list[tuple[str, FileContent]] = [
                    ("config", ("config.ttl", config, "text/turtle"))
                ]
                for field, content in extra_parts:
                    multipart_files.append(
                        (field, _normalize_file_content(field, content))
                    )

                response = self.http_client.post(
                    "/rest/repositories",
                    params=params,
                    files=multipart_files,
                )
            else:
                if files is not None:
                    raise ValueError(
                        "Additional files can only be provided when config is a Turtle string."
                    )
                response = self.http_client.post(
                    "/rest/repositories",
                    headers={"Content-Type": "application/json"},
                    json=config.as_dict(),
                    params=params,
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            if err.response.status_code == 400:
                raise BadRequestError(f"Invalid request: {err.response.text}") from err
            if err.response.status_code == 401:
                raise UnauthorisedError(
                    f"Request is unauthorised: {err.response.text}"
                ) from err
            if err.response.status_code == 403:
                raise ForbiddenError(
                    f"Request is forbidden: {err.response.text}"
                ) from err
            if err.response.status_code == 500:
                raise InternalServerError(
                    f"Internal server error: {err.response.text}"
                ) from err
            raise

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
                json=config.as_dict(),
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

    @t.overload
    def validate(
        self,
        repository_id: str,
        *,
        content_type: str,
        content: str,
        location: str | None = None,
        shapes_repository_id: None = None,
    ) -> str: ...

    @t.overload
    def validate(
        self,
        repository_id: str,
        *,
        content: t.IO[bytes],
        content_type: str | None = None,
        location: str | None = None,
        shapes_repository_id: None = None,
    ) -> str: ...

    @t.overload
    def validate(
        self,
        repository_id: str,
        *,
        shapes_repository_id: str,
        location: str | None = None,
    ) -> str: ...

    def validate(
        self,
        repository_id: str,
        *,
        content_type: str | None = None,
        content: str | t.IO[bytes] | None = None,
        location: str | None = None,
        shapes_repository_id: str | None = None,
    ) -> str:
        """Validate repository data using SHACL shapes.

        Parameters:
            repository_id: The identifier of the repository.
            content_type: Content type of the request body (required for text payloads).
            content: SHACL shapes payload; string for text-based validation or file-like
                (binary) object for multipart validation.
            location: Optional repository location.
            shapes_repository_id: ID of repository containing SHACL shapes; when
                provided, no content is sent and shapes are fetched from that
                repository.

        Returns:
            str: Validation report as RDF Turtle.

        Raises:
            UnauthorisedError: If the request is unauthorised.
            ForbiddenError: If the request is forbidden.
            InternalServerError: If the server returns an internal error.
        """
        params = {}
        if location is not None:
            params["location"] = location

        if shapes_repository_id is not None:
            if content is not None:
                raise ValueError(
                    "content must not be provided when shapes_repository_id is set."
                )
            if content_type is not None:
                raise ValueError(
                    "content_type must not be provided when shapes_repository_id is set."
                )
            headers = {"Accept": "text/turtle"}
            try:
                response = self.http_client.post(
                    url=f"/rest/repositories/{repository_id}/validate/repository/{shapes_repository_id}",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as err:
                if err.response.status_code == 401:
                    raise UnauthorisedError("Request is unauthorised.") from err
                if err.response.status_code == 403:
                    raise ForbiddenError("Request is forbidden.") from err
                if err.response.status_code == 500:
                    raise InternalServerError(
                        f"Internal server error: {err.response.text}"
                    ) from err
                raise

        if content is None:
            raise ValueError("content must be provided.")

        is_file_like = hasattr(content, "read") and not isinstance(content, str)

        if is_file_like:
            headers = {"Accept": "text/turtle"}
            file_part = (
                "shapes.ttl",
                t.cast(t.IO[bytes], content),
                content_type or "text/turtle",
            )
            files: FilesType = {"file": file_part}
            try:
                response = self.http_client.post(
                    url=f"/rest/repositories/{repository_id}/validate/file",
                    params=params,
                    headers=headers,
                    files=files,
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as err:
                if err.response.status_code == 401:
                    raise UnauthorisedError("Request is unauthorised.") from err
                if err.response.status_code == 403:
                    raise ForbiddenError("Request is forbidden.") from err
                if err.response.status_code == 500:
                    raise InternalServerError(
                        f"Internal server error: {err.response.text}"
                    ) from err
                raise
        else:
            if not content_type:
                raise ValueError("content_type must be provided for text validation.")

            headers = {"Content-Type": content_type, "Accept": "text/turtle"}
            try:
                response = self.http_client.post(
                    url=f"/rest/repositories/{repository_id}/validate/text",
                    params=params,
                    headers=headers,
                    content=content,
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as err:
                if err.response.status_code == 401:
                    raise UnauthorisedError("Request is unauthorised.") from err
                if err.response.status_code == 403:
                    raise ForbiddenError("Request is forbidden.") from err
                if err.response.status_code == 500:
                    raise InternalServerError(
                        f"Internal server error: {err.response.text}"
                    ) from err
                raise


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
    def repositories(self) -> RepositoryManager:
        """Server-level repository management operations (GraphDB-specific)."""
        if self._repository_manager is None:
            self._repository_manager = RepositoryManager(self.http_client)
        return self._repository_manager

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
