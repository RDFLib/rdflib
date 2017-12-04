import rdflib
from wf import wf_kernel

g = rdflib.Graph()
g.parse('sample.rdf', format='turtle')

print('Two authors from same organization who authored mutual paper')
print(wf_kernel(g, rdflib.URIRef('http://data.semanticweb.org/person/abraham-bernstein'),
				rdflib.URIRef('http://data.semanticweb.org/person/andre-locher')))
print('Completely different authors')
print(wf_kernel(g, rdflib.URIRef('http://data.semanticweb.org/person/abraham-bernstein'),
				rdflib.URIRef('http://data.semanticweb.org/person/heiko-stoermer')))
print(wf_kernel(g, rdflib.URIRef('http://data.semanticweb.org/person/andre-locher'),
				rdflib.URIRef('http://data.semanticweb.org/person/heiko-stoermer')))