from dataclasses import dataclass


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
