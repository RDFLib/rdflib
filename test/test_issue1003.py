from rdflib import Graph, Dataset, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS

"""
Testing scenarios:
    1. no base set
    2. base set at graph creation
    3. base set at serialization
    4. base set at both graph creation & serialization, serialization overrides
    5. multiple serialization side effect checking
    6. checking results for RDF/XML
    7. checking results for N3
    8. checking results for TriX & TriG
"""

# variables
base_one = Namespace("http://one.org/")
base_two = Namespace("http://two.org/")
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


# 1. no base set for graph, no base set for serialization
g1 = Graph()
g1 += g
# @base should not be in output
assert "@base" not in g.serialize(format="turtle")


# 2. base one set for graph, no base set for serialization
g2 = Graph(base=base_one)
g2 += g
# @base should be in output, from Graph (one)
assert "@base <http://one.org/> ." in g2.serialize(format="turtle")


# 3. no base set for graph, base two set for serialization
g3 = Graph()
g3 += g
# @base should be in output, from serialization (two)
assert "@base <http://two.org/> ." in g3.serialize(format="turtle", base=base_two)


# 4. base one set for graph, base two set for serialization, Graph one overrides
g4 = Graph(base=base_one)
g4 += g
# @base should be in output, from graph (one)
assert "@base <http://two.org/> ." in g4.serialize(format="turtle", base=base_two)
# just checking that the serialization setting (two) hasn't snuck through
assert "@base <http://one.org/> ." not in g4.serialize(format="turtle", base=base_two)


# 5. multiple serialization side effect checking
g5 = Graph()
g5 += g
# @base should be in output, from serialization (two)
assert "@base <http://two.org/> ." in g5.serialize(format="turtle", base=base_two)

# checking for side affects - no base now set for this serialization
# @base should not be in output
assert "@base" not in g5.serialize(format="turtle")


# 6. checking results for RDF/XML
g6 = Graph()
g6 += g
g6.bind("dct", DCTERMS)
g6.bind("skos", SKOS)
assert "@xml:base" not in g6.serialize(format="xml")
assert 'xml:base="http://one.org/"' in g6.serialize(format="xml", base=base_one)
g6.base = base_two
assert 'xml:base="http://two.org/"' in g6.serialize(format="xml")
assert 'xml:base="http://one.org/"' in g6.serialize(format="xml", base=base_one)

# 7. checking results for N3
g7 = Graph()
g7 += g
g7.bind("dct", DCTERMS)
g7.bind("skos", SKOS)
assert "@xml:base" not in g7.serialize(format="xml")
assert "@base <http://one.org/> ." in g7.serialize(format="n3", base=base_one)
g7.base = base_two
assert "@base <http://two.org/> ." in g7.serialize(format="n3")
assert "@base <http://one.org/> ." in g7.serialize(format="n3", base=base_one)

# 8. checking results for TriX & TriG
# TriX can specify a base per graph but setting a base for the whole
base_three = Namespace("http://three.org/")
ds1 = Dataset()
ds1.bind("dct", DCTERMS)
ds1.bind("skos", SKOS)
g8 = ds1.graph(URIRef("http://g8.com/"), base=base_one)
g9 = ds1.graph(URIRef("http://g9.com/"))
g8 += g
g9 += g
g9.base = base_two
ds1.base = base_three

trix = ds1.serialize(format="trix", base=Namespace("http://two.org/"))
assert '<graph xml:base="http://one.org/">' in trix
assert '<graph xml:base="http://two.org/">' in trix
assert '<TriX xml:base="http://two.org/"' in trix

trig = ds1.serialize(format="trig", base=Namespace("http://two.org/"))
assert "@base <http://one.org/> ." not in trig
assert "@base <http://three.org/> ." not in trig
assert "@base <http://two.org/> ." in trig
