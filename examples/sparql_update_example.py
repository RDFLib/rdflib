
"""

Process SPARQL Update

"""

import rdflib
from rdflib.plugins.sparql import processUpdate

g = rdflib.Graph()
g.load("foaf.rdf")

processUpdate(g, '''
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbpedia: <http://dbpedia.org/resource/>
INSERT
    { ?s a dbpedia:Human . }
WHERE
    { ?s a foaf:Person . }
''')

for x in g.subjects(
        rdflib.RDF.type, rdflib.URIRef('http://dbpedia.org/resource/Human')):
    print x
