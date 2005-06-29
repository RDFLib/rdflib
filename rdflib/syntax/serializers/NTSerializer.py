#$Id: NTSerializer.py,v 1.6 2003/10/29 15:25:24 kendall Exp $

from rdflib.syntax.serializers import Serializer

class NTSerializer(Serializer):
    
    def __init__(self, store):
        """
        I serialize RDF graphs in NTriples format.
        """
        super(NTSerializer, self).__init__(store)

    def serialize(self, stream, base=None):
        if base is not None:
	    print "TODO: NTSerializer does not support base"
        encoding = self.encoding
        write = lambda triple: stream.write((triple[0].n3() + u" " + \
                                             triple[1].n3() + u" " + triple[2].n3() + u".\n").encode(encoding, "replace"))
        map(write, self.store)
