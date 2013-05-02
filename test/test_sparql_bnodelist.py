"""

syntax tests for a few corner-cases not touched by the 
official tests.

"""

from rdflib.plugins.sparql import prepareQuery

def test_sparql_bnodelist(): 
    
    prepareQuery('select * where { ?s ?p ( [] ) . }')
    prepareQuery('select * where { ?s ?p ( [ ?p2 ?o2 ] ) . }')
    prepareQuery('select * where { ?s ?p ( [ ?p2 ?o2 ] [] ) . }')
    prepareQuery('select * where { ?s ?p ( [] [ ?p2 ?o2 ] [] ) . }')
    
    

    
