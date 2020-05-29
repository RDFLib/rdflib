from rdflib import Graph

graph1 = """
_:0 <http://purl.obolibrary.org/obo/RO_0002350> <http://www.gbif.org/species/0000001> .
"""
graph2 = """
_:0 <http://purl.obolibrary.org/obo/RO_0002350> <http://www.gbif.org/species/0000002> .
"""

g = Graph()
g.parse(data=graph1, format="nt")
g.parse(data=graph2, format="nt")

for triple in g:
    print(triple)