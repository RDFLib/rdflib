from rdflib.plugin import register
try:
    from rdflib.serializer import Serializer
    from rdflib.plugins.serializers.n3 import N3Serializer
except ImportError:
    from rdflib.syntax.serializer import Serializer
    from rdflib.syntax.serializers.N3Serializer import N3Serializer
from rdflib import BNode
from StringIO import StringIO
import sys

__all__ = ["Serializer", "TriGSerializer"]

class TriGSerializer(N3Serializer):
    def serialize(self, stream, base=None, encoding=None, spacious=None, **args):
        self.reset()
        if stream is None:
                stream = StringIO()
        self.stream = stream
        self.base = base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()
        self.startDocument()

        if self.store.context_aware:
            contexts = self.store.contexts()
        else:
            contexts = [self.store]
        for g in contexts:
            self.write("\n%s {" % self.store.qname(g.identifier))
            self.depth += 1
            s = N3Serializer(g, parent=self)
            s.serialize(self.stream)
            self.depth -= 1
            self.write("}\n")

        self.endDocument()
        self.write("\n")
      
        if isinstance(self.stream, StringIO): 
            return self.stream.getvalue()


