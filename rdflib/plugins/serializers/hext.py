"""
HextuplesSerializer RDF graph serializer for RDFLib.
See <https://github.com/ontola/hextuples> for details about the format.
"""
from typing import IO, Optional

from rdflib.graph import Graph
from rdflib.term import Literal, URIRef, BNode
from rdflib.serializer import Serializer

__all__ = ["HextuplesSerializer"]


class HextuplesSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store: Graph):
        Serializer.__init__(self, store)
        self.encoding = "utf-8"

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args
    ):
        self.encoding = encoding
        for context in self.store.contexts():
            for triple in context:
                stream.write(
                    _hex_line(triple, context.identifier).encode(self.encoding)
                )
        stream.write("\n".encode(self.encoding))


def _hex_line(triple, context):
    return "[%s, %s, %s, %s, %s, %s]\n" % (
        _iri_or_bn(triple[0]),
        _iri_or_bn(triple[1]),
        triple[2] if type(triple[2]) == Literal else _iri_or_bn(triple[2]),
        (f'"{triple[2].datatype}"' if triple[2].datatype is not None else '""') if type(triple[2]) == Literal else '""',
        (f'"{triple[2].language}"' if triple[2].language is not None else '""') if type(triple[2]) == Literal else '""',
        _iri_or_bn(context)
    )


def _iri_or_bn(i_):
    if type(i_) == URIRef:
        return f"\"{i_}\""
    else:
        return f"\"{i_.n3()}\""
