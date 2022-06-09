import enum
import logging
import pprint
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, FrozenSet, Mapping, Optional, Sequence, Set, Tuple, Union

from rdflib.term import BNode, Identifier, Literal, Variable

logger = logging.getLogger(__name__)


ResultTypeInfoDict = Dict["ResultType", "ResultTypeInfo"]


class ResultTypeTrait(enum.Enum):
    GRAPH_RESULT = enum.auto()


class ResultType(str, enum.Enum):
    CONSTRUCT = "CONSTRUCT"
    DESCRIBE = "DESCRIBE"
    SELECT = "SELECT"
    ASK = "ASK"

    @classmethod
    @lru_cache(maxsize=None)
    def info_dict(cls) -> "ResultTypeInfoDict":
        return ResultTypeInfo.make_dict(
            ResultTypeInfo(ResultType.CONSTRUCT, {ResultTypeTrait.GRAPH_RESULT}),
            ResultTypeInfo(ResultType.DESCRIBE, {ResultTypeTrait.GRAPH_RESULT}),
            ResultTypeInfo(ResultType.CONSTRUCT, set()),
            ResultTypeInfo(ResultType.CONSTRUCT, set()),
        )

    @property
    def info(self) -> "ResultTypeInfo":
        return self.info_dict()[self]

    @classmethod
    @lru_cache(maxsize=None)
    def set(cls) -> Set["ResultType"]:
        return set(*cls)


@dataclass(frozen=True)
class ResultTypeInfo:
    type: ResultType
    traits: Set[ResultTypeTrait]

    @classmethod
    def make_dict(cls, *items: "ResultTypeInfo") -> ResultTypeInfoDict:
        return dict((info.type, info) for info in items)


BindingsType = Mapping[Variable, Optional[Identifier]]
BindingsSequenceType = Sequence[BindingsType]
CLiteralType = Union["CLiteral", "CLiteral"]


CIdentifier = Union[Identifier, CLiteralType]
CBindingSetType = FrozenSet[Tuple[Variable, CIdentifier]]
CBindingsType = Mapping[Variable, Optional[CIdentifier]]
CBindingsSequenceType = Sequence[CBindingsType]


@dataclass
class CLiteral:
    literal: Literal

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, CLiteral):
            return False
        try:
            return self.literal.eq(__o.literal)
        except TypeError:
            return self.literal == __o.literal


def comparable_node(node: Identifier) -> CIdentifier:
    if isinstance(node, Literal):
        return CLiteral(node)
    if isinstance(node, BNode):
        return BNode("urn:fdc:rdflib.github.io:20220526:collapsed-bnode")
    return node


def comparable_bindings(
    bindings: BindingsType,
) -> CBindingsType:
    result = {}
    for key, value in bindings.items():
        if value is None:
            # TODO: FIXME: This may be a bug in how we generate bindings
            continue
        result[key] = comparable_node(value)
    return result


def bindings_diff(
    lhs: CBindingsSequenceType, rhs: CBindingsSequenceType
) -> Tuple[CBindingsSequenceType, CBindingsSequenceType, CBindingsSequenceType]:
    rhs_only = []
    common = []
    lhs_matched = set()
    for rhs_bindings in rhs:
        found = False
        for lhs_index, lhs_bindings in enumerate(lhs):
            if lhs_index in lhs_matched:
                # cant match same entry more than once
                continue
            if rhs_bindings == lhs_bindings:
                lhs_matched.add(lhs_index)
                found = True
                break
        if found:
            common.append(rhs_bindings)
            continue
        else:
            rhs_only.append(rhs_bindings)
    lhs_only = [
        lhs_bindings
        for lhs_index, lhs_bindings in enumerate(lhs)
        if lhs_index not in lhs_matched
    ]
    return lhs_only, rhs_only, common


def assert_bindings_sequences_equal(
    lhs: BindingsSequenceType,
    rhs: BindingsSequenceType,
    invert: bool = False,
) -> None:
    clhs = [comparable_bindings(item) for item in lhs]
    crhs = [comparable_bindings(item) for item in rhs]
    lhs_only, rhs_only, common = bindings_diff(clhs, crhs)
    if logger.isEnabledFor(logging.DEBUG):
        logging.debug("common = \n%s", pprint.pformat(common, indent=1, width=80))
        logging.debug("lhs_only = \n%s", pprint.pformat(lhs_only, indent=1, width=80))
        logging.debug("rhs_only = \n%s", pprint.pformat(rhs_only, indent=1, width=80))
    if invert:
        assert lhs_only != [] or rhs_only != []
        assert (len(common) != len(lhs)) or (len(common) != len(rhs))
    else:
        assert lhs_only == []
        assert rhs_only == []
        assert (len(common) == len(lhs)) and (len(common) == len(rhs))
