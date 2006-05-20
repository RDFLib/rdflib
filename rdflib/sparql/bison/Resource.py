from rdflib import URIRef, BNode
from Util import ListRedirect
from sets import Set

class Resource(object):
    """
    Represents a sigle resource in a triple pattern.  It consists of an identifier 
    (URIReff or BNode) and a list of rdflib.sparql.bison.Triples.PropertyValue instances
    """
    def __init__(self,identifier,propertyValueList=None):        
        self.identifier = (identifier is not None and not isinstance(identifier,BNode)) and URIRef(identifier) or BNode()
        self.propVals = propertyValueList is not None and propertyValueList or []
                
    def __repr__(self):
        resId = isinstance(self.identifier,BNode) and '_:'+self.identifier or self.identifier
        #print type(self.identifier)
        return "%s%s"%(resId,self.propVals and ' %s'%self.propVals or '')
    
    def extractPatterns(self) :
        for prop,objs in self.propVals:
            for obj in objs:
                yield (self.identifier,prop,obj)
                        
class TwiceReferencedBlankNode(Resource):            
    """
    Represents BNode in triple patterns in this form:
    [ :prop1 :val1 ] :prop2 :val2
    """
    def __init__(self,props1,props2):
        self.identifier = BNode()
        self.propVals = list(Set(props1+props2))
        
class ParsedCollection(ListRedirect):
    """
    An RDF Collection
    """
    reducable = False
    def __init__(self,graphNodeList):
        self._list = graphNodeList
    def __repr__(self):
        return "<RDF Collection: %s>"%self._list
        