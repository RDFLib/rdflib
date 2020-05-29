from rdflib import URIRef, Graph

g1 = Graph().parse(data='<http://ex.org/res/1> a <http://auth.edu/ns#Resource> .', format='turtle')
ttl1 = g1.serialize(format='turtle', base='http://ex.org/res/')
print(ttl1.decode())

g2 = Graph()
g2.parse(data=ttl1, format='turtle', publicID=URIRef('http://ns.org/'))
# ttl1 = g2.serialize(format='turtle', base='http://ex.org/res')
# print(ttl1.decode())
for t in g2:
print(t)

for t in g1:
print(t)


## To see the changes you have to go under rdflib\rdflib\plugins\parsers\notation3.py line number and change to 
## this "ns = join(self._baseURI, ns)" to ns = self._baseURI if want to change the original base URI. 