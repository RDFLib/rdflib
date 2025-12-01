from __future__ import annotations

from dataclasses import dataclass, field


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
