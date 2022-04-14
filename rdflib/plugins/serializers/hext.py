"""
HextuplesSerializer RDF graph serializer for RDFLib.
See <https://github.com/ontola/hextuples> for details about the format.
"""
from typing import IO, Optional, Type, Union
import json
from rdflib.graph import Dataset, DATASET_DEFAULT_GRAPH_ID, Graph
from rdflib.term import Literal, URIRef, Node, BNode
from rdflib.serializer import Serializer
from rdflib.namespace import RDF, XSD
import warnings

__all__ = ["HextuplesSerializer"]


class HextuplesSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def __init__(self, store: Union[Graph, Dataset]):
        self.default_graph: Optional[Node]
        self.graph_type: Type[Graph]
        if isinstance(store, Dataset):
            self.graph_type = Dataset
            self.graphs = list(store.graphs())
            if store.default_graph:
                self.default_graph = store.default_graph
                self.graphs.append(store.default_graph)
            else:
                self.default_graph = None
        else:
            self.graph_type = Graph
            self.graphs = [store]
            self.default_graph = None

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

        for graph in self.graphs:
            for triple in graph:
                hl = self._hex_line(triple, graph)
                if hl is not None:
                    stream.write(hl.encode())

    def _hex_line(self, triple, graph):
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
                        self._contexturi(graph),
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

    def _contexturi(self, graph):
        if self.graph_type == Graph:
            return ""
        if graph.identifier == DATASET_DEFAULT_GRAPH_ID:
            return ""
        elif graph.identifier is not None and self.default_graph is not None:
            if graph.identifier == self.default_graph.identifier:
                return ""
        return graph.identifier
