
"""

SPARQL Update statements can be applied with :meth:`rdflib.graph.Graph.update`

"""

import rdflib

if __name__=='__main__':

    g = rdflib.Graph()
    g.load("foaf.rdf")

    g.update('''
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    INSERT
        { ?s a dbpedia:Human . }
    WHERE
        { ?s a foaf:Person . }
    ''')

    for x in g.subjects(
            rdflib.RDF.type, rdflib.URIRef('http://dbpedia.org/resource/Human')):
        print(x)
