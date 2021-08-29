import warnings

from rdflib.term import Literal
from rdflib.serializer import Serializer

from rdflib.plugins.serializers.nt import _quoteLiteral

__all__ = ["NQuadsSerializer"]


class NQuadsSerializer(Serializer):
    def __init__(self, store):
        if not store.context_aware:
            raise Exception(
                "NQuads serialization only makes " "sense for context-aware stores!"
            )

        super(NQuadsSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NQuadsSerializer does not support base.")
        if encoding is not None and encoding.lower() != self.encoding.lower():
            warnings.warn("NQuadsSerializer does not use custom encoding.")
        encoding = self.encoding
        for context in self.store.contexts():
            for triple in context:
                stream.write(
                    _nq_row(triple, context.identifier).encode(encoding, "replace")
                )
        stream.write("\n".encode("latin-1"))


def _nq_row(triple, context):
    if isinstance(triple[2], Literal):
        return "%s %s %s %s .\n" % (
            triple[0].n3(),
            triple[1].n3(),
            _quoteLiteral(triple[2]),
            context.n3(),
        )
    else:
        return "%s %s %s %s .\n" % (
            triple[0].n3(),
            triple[1].n3(),
            triple[2].n3(),
            context.n3(),
        )
