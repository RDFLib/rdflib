from rdflib.syntax.serializers import Serializer
from rdflib.Graph import Graph


class N3Serializer(Serializer):

    def __init__(self, store):
        """
        I serialize RDF graphs in N3 format.
        """
        super(N3Serializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None):
        if base is not None:
            print "TODO: N3Serializer does not support base"
        encoding = self.encoding
        self._ser(self.store, stream)


    def _ser(self, store, stream):

        for s, p, o in store:
            nodes = []
            for node in s,p,o:
                if isinstance(node, Graph):
                    stream.write('{\n ')
                    self._ser(node, stream)
                    stream.write(' } ')
                else:
                    stream.write(node.n3().encode(self.encoding, "replace"))
                stream.write(' ')
            stream.write('.\n')

