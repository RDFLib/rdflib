import warnings

from rdflib.serializer import Serializer
from rdflib.py3compat import b

from rdflib.plugins.serializers.nt import _xmlcharref_encode

__all__ = ['NQuadsSerializer']

class NQuadsSerializer(Serializer):

    def __init__(self, store):
        if not store.context_aware: 
            raise Exception("NQuads serialization only makes sense for context-aware stores!")

        super(NQuadsSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NQuadsSerializer does not support base.")
        if encoding is not None:
            warnings.warn("NQuadsSerializer does not use custom encoding.")
        encoding = self.encoding
        for context in self.store.contexts():
            for triple in context:
                stream.write(_nq_row(triple, context.identifier).encode(encoding, "replace"))
        stream.write(b("\n"))

def _nq_row(triple,context):
    return u"%s %s %s %s .\n" % (triple[0].n3(),
                                triple[1].n3(),
                                _xmlcharref_encode(triple[2].n3()), 
                                context.n3())

