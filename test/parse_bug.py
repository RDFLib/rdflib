from StringIO import StringIO
from rdflib.InMemoryTripleStore import InMemoryTripleStore
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef

def toString(store):
    s = StringIO()
    store.output(s)
    return s.getvalue()


ts = InMemoryTripleStore()
ts.add(URIRef("http://foo/"), URIRef("http://someslotsite/"), Literal("foo") )
text = toString(ts)
print text
ts.parse(StringIO(text))
