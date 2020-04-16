from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS

"""
Testing scenarios:
    1. no base set
    2. base set at graph creation
    3. base set at serialization
    4. base set at both graph creation & serialization, serialization overrides
"""

# variables
base = Namespace("http://example.org/")
title = Literal("Title", lang="en")
description = Literal("Test Description", lang="en")
creator = URIRef("https://creator.com")
cs = URIRef("")

# starting graph
g = Graph()
g.add((cs, RDF.type, SKOS.ConceptScheme))
g.add((cs, DCTERMS.creator, creator))
g.add((cs, DCTERMS.source, URIRef("nick")))
g.bind("dct", DCTERMS)
g.bind("skos", SKOS)


# 1. no base set
g1 = Graph()
g1 += g
# @base should not be in output
assert "@base" not in g.serialize(format='turtle').decode("utf-8")


# 2. base set at graph creation
g2 = Graph(base=base)
g2 += g
# @base should be in output
assert "@base" in g2.serialize(format='turtle').decode("utf-8")


# 3. base set at serialization
g3 = Graph()
g3 += g
# @base should be in output
assert "@base" in g3.serialize(format='turtle', base=base).decode("utf-8")


# 4. base set at both graph creation & serialization, serialization overrides
g4 = Graph(base=Namespace("http://nothing.com/"))
g4 += g

# @base should be in output and it should be http://example.org/ (graph init copy)
assert "@base <http://nothing.com/>" in g4.serialize(format='turtle').decode("utf-8")
# @base should be in output and it should be http://example.org/, not http://nothing.com/ (serialization overwritten)
assert "@base <http://example.org/>" in g4.serialize(format='turtle', base=base).decode("utf-8")
# just checking that the graph init base isn't sneakily in output
assert "@base <http://nothing.com/>" not in g4.serialize(format='turtle', base=base).decode("utf-8")
