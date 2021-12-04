"""
HextuplesSerializer RDF graph serializer for RDFLib.
See <https://github.com/ontola/hextuples> for details about the format.
"""
from typing import IO, TYPE_CHECKING, Optional, Union
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term import Literal, URIRef, Node
from rdflib.serializer import Serializer
import warnings

__all__ = ["HextuplesSerializer"]


class HextuplesSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store: Union[Graph, ConjunctiveGraph]):
        self.default_context: Optional[Node]
        if store.context_aware:
            if TYPE_CHECKING:
                assert isinstance(store, ConjunctiveGraph)
            self.contexts = list(store.contexts())
            self.default_context = store.default_context.identifier
            if store.default_context:
                self.contexts.append(store.default_context)
        else:
            self.contexts = [store]
            self.default_context = None

        Serializer.__init__(self, store)

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args
    ):
        if base is not None:
            warnings.warn("HextuplesSerializer does not support base.")
        if encoding != "utf-8":
            warnings.warn("NTSerializer always uses UTF-8 encoding.")

        for context in self.contexts:
            for triple in context:
                stream.write(
                    _hex_line(triple, context.identifier).encode()
                )
        stream.write("\n".encode())


def _hex_line(triple, context):
    return "[%s, %s, %s, %s, %s, %s]\n" % (
        _iri_or_bn(triple[0]),
        _iri_or_bn(triple[1]),
        _literal(triple[2]) if type(triple[2]) == Literal else _iri_or_bn(triple[2]),
        (f'"{triple[2].datatype}"' if triple[2].datatype is not None else '""') if type(triple[2]) == Literal else '""',
        (f'"{triple[2].language}"' if triple[2].language is not None else '""') if type(triple[2]) == Literal else '""',
        _iri_or_bn(context)
    )


def _iri_or_bn(i_):
    if type(i_) == URIRef:
        return f"\"{i_}\""
    else:
        return f"\"{i_.n3()}\""


def _literal(i_):
    raw_datatype = [
        "http://www.w3.org/2001/XMLSchema#integer",
        "http://www.w3.org/2001/XMLSchema#long",
        "http://www.w3.org/2001/XMLSchema#int",
        "http://www.w3.org/2001/XMLSchema#short",
        "http://www.w3.org/2001/XMLSchema#positiveInteger",
        "http://www.w3.org/2001/XMLSchema#negativeInteger",
        "http://www.w3.org/2001/XMLSchema#nonPositiveInteger",
        "http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
        "http://www.w3.org/2001/XMLSchema#unsignedLong",
        "http://www.w3.org/2001/XMLSchema#unsignedInt",
        "http://www.w3.org/2001/XMLSchema#unsignedShort",

        "http://www.w3.org/2001/XMLSchema#float",
        "http://www.w3.org/2001/XMLSchema#double",
        "http://www.w3.org/2001/XMLSchema#decimal",

        "http://www.w3.org/2001/XMLSchema#boolean"
    ]
    if hasattr(i_, "datatype"):
        if str(i_.datatype) in raw_datatype:
            return f"{i_}"
        else:
            return f"\"{i_}\""
    else:
        if str(i_) in ["true", "false"]:
            return f"{i_}"
        else:
            return f"\"{i_}\""
