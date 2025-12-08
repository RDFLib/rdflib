from __future__ import annotations

from dataclasses import asdict, dataclass, field


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
