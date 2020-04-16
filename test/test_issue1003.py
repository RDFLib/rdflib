from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS

g = Graph()

base = Namespace("http://example.org/")

title = Literal("Title", lang="en")
description = Literal("Test Description", lang="en")
creator = URIRef("https://creator.com")
cs = URIRef("")

g.add((cs, RDF.type, SKOS.ConceptScheme))
g.add((cs, DCTERMS.creator, creator))
g.add((cs, DCTERMS.source, URIRef("nick")))

# Bind a few prefix, namespace pairs for more readable output
g.bind("dct", DCTERMS)
g.bind("skos", SKOS)

# this one should not have @base in the output
assert "@base" not in g.serialize(format='turtle').decode("utf-8")
# this one should have @base in the output
assert "@base" in g.serialize(format='turtle', base=base).decode("utf-8")

# and same for N3 (same serializer used)
assert "@base" not in g.serialize(format='n3').decode("utf-8")
assert "@base" in g.serialize(format='n3', base=base).decode("utf-8")
