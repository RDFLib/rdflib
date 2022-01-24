"""
HextuplesSerializer RDF graph serializer for RDFLib.
See <https://github.com/ontola/hextuples> for details about the format.
"""
import json
import warnings
from typing import IO, Optional, Type, Union

from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import RDF, XSD
from rdflib.serializer import Serializer
from rdflib.term import BNode, Literal, Node, URIRef

__all__ = ["HextuplesSerializer"]


class HextuplesSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store: Union[Graph, ConjunctiveGraph]):
        self.default_context: Optional[Node]
        self.graph_type: Type[Graph]
        if isinstance(store, ConjunctiveGraph):
            self.graph_type = ConjunctiveGraph
            self.contexts = list(store.contexts())
            if store.default_context:
                self.default_context = store.default_context
                self.contexts.append(store.default_context)
            else:
                self.default_context = None
        else:
            self.graph_type = Graph
            self.contexts = [store]
            self.default_context = None

        Serializer.__init__(self, store)

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = "utf-8",
        **kwargs,
    ):
        if base is not None:
            warnings.warn(
                "base has no meaning for Hextuples serialization. "
                "I will ignore this value"
            )

        if encoding not in [None, "utf-8"]:
            warnings.warn(
                f"Hextuples files are always utf-8 encoded. "
                f"I was passed: {encoding}, "
                "but I'm still going to use utf-8 anyway!"
            )

        if self.store.formula_aware is True:
            raise Exception(
                "Hextuple serialization can't (yet) handle formula-aware stores"
            )

        for context in self.contexts:
            for triple in context:
                hl = self._hex_line(triple, context)
                if hl is not None:
                    stream.write(hl.encode())

    def _hex_line(self, triple, context):
        if isinstance(
            triple[0], (URIRef, BNode)
        ):  # exclude QuotedGraph and other objects
            # value
            value = (
                triple[2]
                if isinstance(triple[2], Literal)
                else self._iri_or_bn(triple[2])
            )

            # datatype
            if isinstance(triple[2], URIRef):
                # datatype = "http://www.w3.org/1999/02/22-rdf-syntax-ns#namedNode"
                datatype = "globalId"
            elif isinstance(triple[2], BNode):
                # datatype = "http://www.w3.org/1999/02/22-rdf-syntax-ns#blankNode"
                datatype = "localId"
            elif isinstance(triple[2], Literal):
                if triple[2].datatype is not None:
                    datatype = f"{triple[2].datatype}"
                else:
                    if triple[2].language is not None:  # language
                        datatype = RDF.langString
                    else:
                        datatype = XSD.string
            else:
                return None  # can't handle non URI, BN or Literal Object (QuotedGraph)

            # language
            if isinstance(triple[2], Literal):
                if triple[2].language is not None:
                    language = f"{triple[2].language}"
                else:
                    language = ""
            else:
                language = ""

            return (
                json.dumps(
                    [
                        self._iri_or_bn(triple[0]),
                        triple[1],
                        value,
                        datatype,
                        language,
                        self._context(context),
                    ]
                )
                + "\n"
            )
        else:  # do not return anything for non-IRIs or BNs, e.g. QuotedGraph, Subjects
            return None

    def _iri_or_bn(self, i_):
        if isinstance(i_, URIRef):
            return f"{i_}"
        elif isinstance(i_, BNode):
            return f"{i_.n3()}"
        else:
            return None

    def _context(self, context):
        if self.graph_type == Graph:
            return ""
        if context.identifier == "urn:x-rdflib:default":
            return ""
        elif context is not None and self.default_context is not None:
            if context.identifier == self.default_context.identifier:
                return ""
        return context.identifier
