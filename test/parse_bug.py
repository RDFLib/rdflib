from rdflib.TripleStore import TripleStore
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef


ts = TripleStore()
ts.add((URIRef("http://foo/"), URIRef("http://someslotsite/"), Literal("foo")))
test = ts.serialize()
print text
ts.parse(text)



