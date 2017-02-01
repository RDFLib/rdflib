
"""

SPARQL Queries be prepared (i.e parsed and translated to SPARQL algebra)
by the :meth:`rdflib.plugins.sparql.prepareQuery` method.

When executing, variables can be bound with the
``initBindings`` keyword parameter


"""

import rdflib
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import FOAF

if __name__=='__main__':

    q = prepareQuery(
        'SELECT ?s WHERE { ?person foaf:knows ?s .}',
        initNs = { "foaf": FOAF })

    g = rdflib.Graph()
    g.load("foaf.rdf")

    tim = rdflib.URIRef("http://www.w3.org/People/Berners-Lee/card#i")

    for row in g.query(q, initBindings={'person': tim}):
        print(row)
