import warnings
from typing import IO, Optional

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, ConjunctiveGraph, Graph, QuotedGraph
from rdflib.plugins.serializers.nt import _quoteLiteral
from rdflib.serializer import Serializer
from rdflib.term import BNode, Literal

__all__ = ["NQuadsSerializer"]


class NQuadsSerializer(Serializer):
    def __init__(self, store: Graph):
        if not store.context_aware:
            raise Exception(
                "NQuads serialization only makes " "sense for context-aware stores!"
            )

        super(NQuadsSerializer, self).__init__(store)
        self.store: ConjunctiveGraph

    def serialize(
        self,
        stream: IO[bytes],
        base: Optional[str] = None,
        encoding: Optional[str] = None,
        **args,
    ):
        if base is not None:
            warnings.warn("NQuadsSerializer does not support base.")
        if encoding is not None and encoding.lower() != self.encoding.lower():
            warnings.warn(
                "NQuadsSerializer does not use custom encoding. "
                f"Given encoding was: {encoding}"
            )
        encoding = self.encoding
        for context in list(self.store.contexts()):
            graph = self.store.graph(context)
            for triple in graph:
                stream.write(self._nq_row(triple, context).encode(encoding, "replace"))
        stream.write("".encode("latin-1"))

    def _nq_row(self, quad, context):
        subj, pred, obj = quad

        if isinstance(subj, QuotedGraph):
            subj = BNode(subj.identifier)

        if isinstance(obj, QuotedGraph):
            obj = BNode(obj.identifier)

        # TODO: Remove in 7.0
        if isinstance(context, Graph):
            context = context.identifier

        return "%s %s %s%s .\n" % (
            subj.n3(),
            pred.n3(),
            _quoteLiteral(obj) if isinstance(obj, Literal) else obj.n3(),
            " " + context.n3() if context and context != DATASET_DEFAULT_GRAPH_ID else "",
        )
