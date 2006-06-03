"""
DatasetClause ::= 'FROM' ( IRIref | 'NAMED' IRIref )
See: http://www.w3.org/TR/rdf-sparql-query/#specifyingDataset

'A SPARQL query may specify the dataset to be used for matching.  The FROM clauses 
give IRIs that the query processor can use to create the default graph and the 
FROM NAMED clause can be used to specify named graphs. '
"""

from rdflib.Graph import Graph
from rdflib import URIRef

class IRIRef(URIRef):    
    pass

class RemoteGraph(URIRef):
    """
    Currently not implemented
    """
    def __init__(self,iriRef):
        pass
        #raise Exception("Currently not supported")
        #super(RemoteGraph,self).__init__(identifier=iriRef)              
      
    
class NamedGraph(IRIRef):
    pass
#    def __init__(self,iriRef):
#        super(NamedGraph,self).__init__(identifier=iriRef)        