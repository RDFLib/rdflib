from rdflib import URIRef, Namespace

class PrefixDeclaration(object):
    """
    PrefixDecl ::= 'PREFIX' QNAME_NS Q_IRI_REF
    See: http://www.w3.org/TR/rdf-sparql-query/#rPrefixDecl
    """
    def __init__(self,qName,iriRef):
        self.namespaceMapping = Namespace(iriRef)
        self.qName = qName[:-1]
        self.base = iriRef
        #print self.base,self.qName,self.namespaceMapping.knows

    def __repr__(self):
        return "%s -> %s"%(self.base,self.qName[:-1])
    
class BaseDeclaration(URIRef):
    """
    BaseDecl ::= 'BASE' Q_IRI_REF
    See: http://www.w3.org/TR/rdf-sparql-query/#rBaseDecl
    """
    pass
    