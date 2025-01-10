"""
This module contains a number of common tasks using the RDFLib Dataset class.

An RDFLib Dataset is an object that stores multiple Named Graphs - instances of RDFLib
Graph identified by IRI - within it and allows whole-of-dataset or single Graph use.

Dataset extends Graph's Subject, Predicate, Object structure to include Graph -
archaically called Context - producing quads of s, p, o, g.

There is an older implementation of a Dataset-like class in RDFLib < 7.x called
ConjunctiveGraph that is now deprecated.

Sections in this module:

1. Creating & Growing Datasets
2. Looping & Counting triples/quads in Datasets
3. Manipulating Graphs with Datasets
"""

from rdflib import Dataset, Graph, Literal, URIRef

# Note regarding `mypy: ignore_errors=true`:
#
# This example is using URIRef values as context identifiers. This is contrary
# to the type hints, but it does work. Most likely, the type hints are wrong.
# Ideally we should just use `# type: ignore` comments for the lines that are
# causing problems, but the error occurs on different lines with different
# Python versions, so the only option is to ignore errors for the whole file.

# mypy: ignore_errors=true

#######################################################################################
#   1. Creating & Growing
#######################################################################################

# Create an empty Dataset
d = Dataset()

# Add a namespace prefix to it, just like for Graph
d.bind("ex", "http://example.com/")

# Declare a Graph identifier to be used to identify a Graph
# A string or a URIRef may be used, but safer to always use a URIRef for usage consistency
graph_1_id = URIRef("http://example.com/graph-1")

# Add an empty Graph, identified by graph_1_id, to the Dataset
d.graph(identifier=graph_1_id)

# Add two quads to the Dataset which are triples + graph ID
# These insert the triple into the GRaph specified by the ID
d.add(
    (
        URIRef("http://example.com/subject-x"),
        URIRef("http://example.com/predicate-x"),
        Literal("Triple X"),
        graph_1_id,
    )
)

d.add(
    (
        URIRef("http://example.com/subject-z"),
        URIRef("http://example.com/predicate-z"),
        Literal("Triple Z"),
        graph_1_id,
    )
)

# We now have 2 distinct quads in the Dataset to the Dataset has a length of 2
assert len(d) == 2

# Add another quad to the Dataset specifying a non-existent Graph.
# The Graph is created automatically
d.add(
    (
        URIRef("http://example.com/subject-y"),
        URIRef("http://example.com/predicate-y"),
        Literal("Triple Y"),
        URIRef("http://example.com/graph-2"),
    )
)

assert len(d) == 3


# You can print the Dataset like you do a Graph but you must specify a quads format like
# 'trig' or 'trix', not 'turtle', unless the default_union parameter is set to True, and
# then you can print the entire Dataset in triples.
# print(d.serialize(format="trig").strip())

# you should see something like this:
"""
@prefix ex: <http://example.com/> .

ex:graph-1 {
    ex:subject-x ex:predicate-x "Triple X" .

    ex:subject-z ex:predicate-z "Triple Z" .
}

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .
}
"""


# Print out one graph in the Dataset, using a standard Graph serialization format - longturtle
print(d.get_graph(URIRef("http://example.com/graph-2")).serialize(format="longturtle"))

# you should see something like this:
"""
PREFIX ex: <http://example.com/>

ex:subject-y
    ex:predicate-y "Triple Y" ;
.
"""


#######################################################################################
#   2. Looping & Counting
#######################################################################################

# Loop through all quads in the dataset
for s, p, o, g in d.quads((None, None, None, None)):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
"""

# Loop through all the quads in one Graph - just constrain the Graph field
for s, p, o, g in d.quads((None, None, None, graph_1_id)):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
"""

# Looping through triples in one Graph still works too
for s, p, o in d.triples((None, None, None, graph_1_id)):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
"""

# Looping through triples across the whole Dataset will produce nothing
# unless we set the default_union parameter to True, since each triple is in a Named Graph

# Setting the default_union parameter to True essentially presents all triples in all
# Graphs as a single Graph
d.default_union = True
for s, p, o in d.triples((None, None, None)):
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/subject-y, http://example.com/predicate-y, Triple Y
"""

# You can still loop through all quads now with the default_union parameter to True
for s, p, o, g in d.quads((None, None, None)):
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
"""

# Adding a triple in graph-1 to graph-2 increases the number of distinct of quads in
# the Dataset
d.add(
    (
        URIRef("http://example.com/subject-z"),
        URIRef("http://example.com/predicate-z"),
        Literal("Triple Z"),
        URIRef("http://example.com/graph-2"),
    )
)

for s, p, o, g in d.quads((None, None, None, None)):
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this, with the 'Z' triple in graph-1 and graph-2:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-2
"""

# but the 'length' of the Dataset is still only 3 as only distinct triples are counted
assert len(d) == 3


# Looping through triples sees the 'Z' triple only once
for s, p, o in d.triples((None, None, None)):
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/subject-y, http://example.com/predicate-y, Triple Y
"""

#######################################################################################
#   3. Manipulating Graphs
#######################################################################################

# List all the Graphs in the Dataset
for x in d.graphs():
    print(x)

# this returns the graphs, something like:
"""
<http://example.com/graph-1> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].
<urn:x-rdflib:default> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].
<http://example.com/graph-2> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].
"""

# So try this
for x in d.graphs():
    print(x.identifier)

# you should see something like this, noting the default, currently empty, graph:
"""
urn:x-rdflib:default
http://example.com/graph-2
http://example.com/graph-1
"""

# To add to the default Graph, just add a triple, not a quad, to the Dataset directly
d.add(
    (
        URIRef("http://example.com/subject-n"),
        URIRef("http://example.com/predicate-n"),
        Literal("Triple N"),
    )
)
for s, p, o, g in d.quads((None, None, None, None)):
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this, noting the triple in the default Graph:
"""
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-2
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
http://example.com/subject-n, http://example.com/predicate-n, Triple N, urn:x-rdflib:default
"""

# Loop through triples per graph
for x in d.graphs():
    print(x.identifier)
    for s, p, o in x.triples((None, None, None)):
        print(f"\t{s}, {p}, {o}")

# you should see something like this:
"""
urn:x-rdflib:default
	http://example.com/subject-n, http://example.com/predicate-n, Triple N
http://example.com/graph-1
	http://example.com/subject-x, http://example.com/predicate-x, Triple X
	http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/graph-2
	http://example.com/subject-y, http://example.com/predicate-y, Triple Y
	http://example.com/subject-z, http://example.com/predicate-z, Triple Z
"""

# The default_union parameter includes all triples in the Named Graphs and the Default Graph
for s, p, o in d.triples((None, None, None)):
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-n, http://example.com/predicate-n, Triple N
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/subject-y, http://example.com/predicate-y, Triple Y
"""

# To remove a graph
d.remove_graph(graph_1_id)

# To remove the default graph
d.remove_graph(URIRef("urn:x-rdflib:default"))

# print what's left - one graph, graph-2
print(d.serialize(format="trig"))

# you should see something like this:
"""
@prefix ex: <http://example.com/> .

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}
"""

# To add a Graph that already exists, you must give it an Identifier or else it will be assigned a Blank Node ID
g_with_id = Graph(identifier=URIRef("http://example.com/graph-3"))
g_with_id.bind("ex", "http://example.com/")

# Add a distinct triple to the exiting Graph, using Namepspace IRI shortcuts
# g_with_id.bind("ex", "http://example.com/")
g_with_id.add(
    (
        URIRef("http://example.com/subject-k"),
        URIRef("http://example.com/predicate-k"),
        Literal("Triple K"),
    )
)
d.add_graph(g_with_id)
print(d.serialize(format="trig"))

# you should see something like this:
"""
@prefix ex: <http://example.com/> .

ex:graph-3 {
    ex:subject_k ex:predicate_k "Triple K" .
}

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}
"""

# If you add a Graph with no specified identifier...
g_no_id = Graph()
g_no_id.bind("ex", "http://example.com/")

g_no_id.add(
    (
        URIRef("http://example.com/subject-l"),
        URIRef("http://example.com/predicate-l"),
        Literal("Triple L"),
    )
)
d.add_graph(g_no_id)

# now when we print it, we will see a Graph with a Blank Node id:
print(d.serialize(format="trig"))

# you should see somthing like this, but with a different Blank Node ID , as this is rebuilt each code execution
"""
@prefix ex: <http://example.com/> .

ex:graph-3 {
    ex:subject-k ex:predicate-k "Triple K" .
}

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}

_:N9cc8b54c91724e31896da5ce41e0c937 {
    ex:subject-l ex:predicate-l "Triple L" .
}
"""
