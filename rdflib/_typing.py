# import sys
# from typing import TYPE_CHECKING, Optional, Tuple, TypeVar

# if sys.version_info >= (3, 10):
#     from typing import TypeAlias
# else:
#     from typing_extensions import TypeAlias

# if TYPE_CHECKING:
#     from rdflib.graph import Graph
#     from rdflib.term import IdentifiedNode, Identifier

# _SubjectType: TypeAlias = "IdentifiedNode"
# _PredicateType: TypeAlias = "IdentifiedNode"
# _ObjectType: TypeAlias = "Identifier"

# _TripleType = Tuple["_SubjectType", "_PredicateType", "_ObjectType"]
# _QuadType = Tuple["_SubjectType", "_PredicateType", "_ObjectType", "Graph"]
# _TriplePatternType = Tuple[
#     Optional["_SubjectType"], Optional["_PredicateType"], Optional["_ObjectType"]
# ]

# _GraphT = TypeVar("_GraphT", bound="Graph")
