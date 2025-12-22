from __future__ import annotations

import typing as t
from dataclasses import asdict, dataclass, field
from enum import Enum

from rdflib import Literal, URIRef
from rdflib.util import from_n3


@dataclass(frozen=True)
class RepositorySizeInfo:
    inferred: int
    total: int
    explicit: int

    def __post_init__(self):
        invalid = []
        if type(self.inferred) is not int:
            invalid.append("inferred")
        if type(self.total) is not int:
            invalid.append("total")
        if type(self.explicit) is not int:
            invalid.append("explicit")

        if invalid:
            raise ValueError(
                "Invalid RepositorySizeInfo values: ",
                [(x, self.__dict__[x], type(self.__dict__[x])) for x in invalid],
            )


@dataclass(frozen=True)
class OWLimParameter:
    name: str
    label: str
    value: str


@dataclass(frozen=True)
class RepositoryConfigBean:
    id: str
    title: str
    type: str
    sesameType: str  # noqa: N815
    location: str
    params: dict[str, OWLimParameter] = field(default_factory=dict)


@dataclass(frozen=True)
class RepositoryConfigBeanCreate:
    id: str
    title: str
    type: str
    sesameType: str  # noqa: N815
    location: str
    params: dict[str, OWLimParameter] = field(default_factory=dict)
    missingDefaults: dict[str, OWLimParameter] = field(  # noqa: N815
        default_factory=dict
    )

    def to_dict(self) -> dict:
        """Serialize the dataclass to a Python dict.

        Returns:
            dict: A dictionary representation of the dataclass suitable for use
                with httpx POST requests (e.g., via the `json` parameter).

        Examples:
            >>> config = RepositoryConfigBeanCreate(
            ...     id="test-repo",
            ...     title="Test Repository",
            ...     type="graphdb:FreeSailRepository",
            ...     sesameType="graphdb:FreeSailRepository",
            ...     location="",
            ... )
            >>> config_dict = config.to_dict()
            >>> isinstance(config_dict, dict)
            True
        """
        return asdict(self)


class RepositoryState(str, Enum):
    """Enumeration for repository state values."""

    INACTIVE = "INACTIVE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    STOPPING = "STOPPING"


@dataclass
class GraphDBRepository:
    id: t.Optional[str] = None
    title: t.Optional[str] = None
    uri: t.Optional[str] = None
    externalUrl: t.Optional[str] = None  # noqa: N815
    local: t.Optional[bool] = None
    type: t.Optional[str] = None
    sesameType: t.Optional[str] = None  # noqa: N815
    location: t.Optional[str] = None
    readable: t.Optional[bool] = None
    writable: t.Optional[bool] = None
    unsupported: t.Optional[bool] = None
    state: t.Optional[RepositoryState] = None

    @classmethod
    def from_dict(cls, data: dict) -> GraphDBRepository:
        if "state" in data and data["state"] is not None:
            data["state"] = RepositoryState(data["state"])
        return cls(**data)


@dataclass
class AccessControlEntry:
    scope: t.Literal["statement", "clear_graph", "plugin", "system"]
    policy: t.Literal["allow", "deny", "abstain"]
    role: str

    @classmethod
    def from_dict(
        cls, data: dict
    ) -> (
        SystemAccessControlEntry
        | StatementAccessControlEntry
        | PluginAccessControlEntry
        | ClearGraphAccessControlEntry
    ):
        """Create an AccessControlEntry subclass instance from raw GraphDB data."""
        if not isinstance(data, dict):
            raise TypeError("ACL entry must be a mapping.")

        scope = data.get("scope")
        if scope == "system":
            return SystemAccessControlEntry(
                scope="system",
                policy=_parse_policy(data.get("policy")),
                role=_parse_role(data.get("role")),
                operation=_parse_operation(data.get("operation")),
            )
        if scope == "statement":
            return StatementAccessControlEntry(
                scope="statement",
                policy=_parse_policy(data.get("policy")),
                role=_parse_role(data.get("role")),
                operation=_parse_operation(data.get("operation")),
                subject=_parse_subject(data.get("subject")),
                predicate=_parse_predicate(data.get("predicate")),
                object=_parse_object(data.get("object")),
                graph=_parse_graph(data.get("graph")),
            )
        if scope == "plugin":
            return PluginAccessControlEntry(
                scope="plugin",
                policy=_parse_policy(data.get("policy")),
                role=_parse_role(data.get("role")),
                operation=_parse_operation(data.get("operation")),
                plugin=_parse_plugin(data.get("plugin")),
            )
        if scope == "clear_graph":
            return ClearGraphAccessControlEntry(
                scope="clear_graph",
                policy=_parse_policy(data.get("policy")),
                role=_parse_role(data.get("role")),
                graph=_parse_graph(data.get("graph")),
            )

        raise ValueError(f"Unsupported FGAC scope: {scope!r}")


@dataclass
class SystemAccessControlEntry(AccessControlEntry):
    scope: t.Literal["system"]
    policy: t.Literal["allow", "deny", "abstain"]
    role: str
    operation: t.Literal["read", "write", "*"]


@dataclass
class StatementAccessControlEntry(AccessControlEntry):
    scope: t.Literal["statement"]
    policy: t.Literal["allow", "deny", "abstain"]
    role: str
    operation: t.Literal["read", "write", "*"]
    subject: t.Literal["*"] | URIRef
    predicate: t.Literal["*"] | URIRef
    object: t.Literal["*"] | URIRef | Literal
    graph: t.Literal["*", "named", "default"] | URIRef


@dataclass
class PluginAccessControlEntry(AccessControlEntry):
    scope: t.Literal["plugin"]
    policy: t.Literal["allow", "deny", "abstain"]
    role: str
    operation: t.Literal["read", "write", "*"]
    plugin: str


@dataclass
class ClearGraphAccessControlEntry(AccessControlEntry):
    scope: t.Literal["clear_graph"]
    policy: t.Literal["allow", "deny", "abstain"]
    role: str
    graph: t.Literal["*", "named", "default"] | URIRef


_ALLOWED_POLICIES = {"allow", "deny", "abstain"}
_ALLOWED_OPERATIONS = {"read", "write", "*"}
_ALLOWED_GRAPHS = {"*", "named", "default"}


def _parse_policy(policy: t.Any) -> t.Literal["allow", "deny", "abstain"]:
    if policy not in _ALLOWED_POLICIES:
        raise ValueError(f"Invalid FGAC policy: {policy!r}")
    return t.cast(t.Literal["allow", "deny", "abstain"], policy)


def _parse_operation(operation: t.Any) -> t.Literal["read", "write", "*"]:
    if operation not in _ALLOWED_OPERATIONS:
        raise ValueError(f"Invalid FGAC operation: {operation!r}")
    return t.cast(t.Literal["read", "write", "*"], operation)


def _parse_role(role: t.Any) -> str:
    if not isinstance(role, str):
        raise ValueError(f"Invalid FGAC role: {role!r}")
    return role


def _parse_plugin(plugin: t.Any) -> str:
    if not isinstance(plugin, str):
        raise ValueError(f"Invalid FGAC plugin: {plugin!r}")
    return plugin


def _parse_subject(subject: t.Any) -> t.Literal["*"] | URIRef:
    if subject == "*":
        return "*"
    if isinstance(subject, URIRef):
        return subject
    if isinstance(subject, str):
        parsed = _parse_with_n3(subject)
        if isinstance(parsed, URIRef):
            return parsed
    raise ValueError(f"Invalid FGAC subject: {subject!r}")


def _parse_predicate(predicate: t.Any) -> t.Literal["*"] | URIRef:
    if predicate == "*":
        return "*"
    if isinstance(predicate, URIRef):
        return predicate
    if isinstance(predicate, str):
        parsed = _parse_with_n3(predicate)
        if isinstance(parsed, URIRef):
            return parsed
    raise ValueError(f"Invalid FGAC predicate: {predicate!r}")


def _parse_object(obj: t.Any) -> t.Literal["*"] | URIRef | Literal:
    if obj == "*":
        return "*"
    if isinstance(obj, (URIRef, Literal)):
        return obj
    if isinstance(obj, str):
        parsed = _parse_with_n3(obj)
        if isinstance(parsed, (URIRef, Literal)):
            return parsed
    raise ValueError(f"Invalid FGAC object: {obj!r}")


def _parse_graph(graph: t.Any) -> t.Literal["*", "named", "default"] | URIRef:
    if graph in _ALLOWED_GRAPHS:
        return t.cast(t.Literal["*", "named", "default"], graph)
    if isinstance(graph, URIRef):
        return graph
    if isinstance(graph, str):
        parsed = _parse_with_n3(graph)
        if isinstance(parsed, URIRef):
            return parsed
    raise ValueError(f"Invalid FGAC graph: {graph!r}")


def _parse_with_n3(value: str) -> URIRef | Literal:
    try:
        parsed = from_n3(value)
    except Exception:
        parsed = None
    if isinstance(parsed, (URIRef, Literal)):
        return parsed
    try:
        return URIRef(value)
    except Exception as err:  # pragma: no cover - defensive
        raise ValueError(f"Unable to parse value {value!r} into an RDF term.") from err
