#$Id: NTSerializer.py,v 1.6 2003/10/29 15:25:24 kendall Exp $

from rdflib.syntax.serializer import AbstractSerializer

class NTSerializer(AbstractSerializer):
    
    short_name = "nt"

    def __init__(self, store):
        """
        I serialize RDF graphs in NTriples format.
        """
        super(NTSerializer, self).__init__(store)

    def serialize(self, stream):
        encoding = self.encoding
        write = lambda triple: stream.write((triple[0].n3() + u" " + \
                                             triple[1].n3() + u" " + triple[2].n3() + u".\n").encode(encoding, "replace"))
        map(write, self.store)
