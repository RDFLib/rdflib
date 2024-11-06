from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, final
from uuid import uuid4
from weakref import WeakValueDictionary


class InternedBlankNode(str):
    _intern_cache: WeakValueDictionary[str, InternedBlankNode] = WeakValueDictionary()
    _lock = threading.Lock()

    __slots__ = ("__weakref__",)

    def __new__(cls, value: str | None = None) -> InternedBlankNode:
        if value is None:
            value = str(uuid4()).replace("-", "0")

        with cls._lock:
            if value in cls._intern_cache:
                return cls._intern_cache[value]

            instance = super().__new__(cls, value)
            object.__setattr__(instance, "value", value)
            cls._intern_cache[value] = instance
            return instance


@final
@dataclass(frozen=True, eq=False)
class BlankNode(InternedBlankNode):
    """
    An RDF blank node representing an anonymous resource.

    Specification: https://www.w3.org/TR/rdf12-concepts/#section-blank-nodes

    This implementation uses object interning to ensure that blank nodes
    with the same identifier reference the same object instance, optimizing
    memory usage. The class is marked final to ensure the :py:meth:`IRI.__new__`
    implementation cannot be overridden.

    :param value:
        A blank node identifier. If :py:obj:`None` is provided, an identifier
        will be generated.
    """

    value: str = field(default_factory=lambda: str(uuid4()).replace("-", "0"))

    def __str__(self) -> str:
        return f"_:{self.value}"

    def __reduce__(self) -> str | tuple[Any, ...]:
        return self.__class__, (self.value,)


__all__ = ["BlankNode"]


if __name__ == "__main__":
    import timeit

    bnode = BlankNode("123")
    with_time = timeit.timeit(lambda: hash(bnode), number=1000000)
    print(f"BlankNode - Average time per hash: {with_time / 1000000:.9f} seconds")

    print(id(bnode), id(bnode.value))

    bnode2 = BlankNode("123")
    print(id(bnode), id(bnode2))
    print(id(bnode.value), id(bnode2.value))

    print(bnode is bnode2)
