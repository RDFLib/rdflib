#$Id: NTSerializer.py,v 1.6 2003/10/29 15:25:24 kendall Exp $

from rdflib.syntax.serializer import AbstractSerializer

class NTSerializer(AbstractSerializer):
    
    short_name = "nt"

    def __init__(self, store):
        """
        I serialize RDF graphs in NTriples format.
        """
        super(NTSerializer, self).__init__(store)

    def _output(self, stream):
        self._stream = stream
	write = self.write; store = self.store
	#this might be faster as a map()?
	for triple in store:
            s, p, o = triple
	    #concating seems faster than string interp in
	    #this loop, esp since these are likely to be short
	    #strings, commonly
            write(s.n3() + u" " + p.n3() + u" " +  o.n3() + u".\n")
