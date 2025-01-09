"""
This module contains a number of common tasks using the RDFLib Dataset class.

An RDFLib Dataset is an object that stores one Default Graph and zero or more Named
Graphs - all instances of RDFLib Graph identified by IRI - within it and allows
whole-of-dataset or single Graph use.

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

# Add another quad to the Dataset.
d.add(
    (
        URIRef("http://example.com/subject-y"),
        URIRef("http://example.com/predicate-y"),
        Literal("Triple Y"),
        URIRef("http://example.com/graph-2"),
    )
)

assert len(d) == 3

# Triples can be added to the Default Graph by not specifying a graph, or specifying the
# graph as None
d.add(
    (
        URIRef("http://example.com/subject-dg"),
        URIRef("http://example.com/predicate-dg"),
        Literal("Triple DG"),
    )
)

# Triples in the Default Graph contribute to the size/length of the Dataset
assert len(d) == 4

# You can print the Dataset like you do a Graph, in both "triples" and "quads" RDF
# mediatypes.
# Using trig, a "quads" or "graph aware" format:
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

{
    ex:subject-dg ex:predicate-dg "Triple DG" .
}
"""
# Using turtle, a "triples" format:
# print(d.serialize(format="turtle").strip())

# you should see something like this:
"""
@prefix ex: <http://example.com/> .

ex:subject-x ex:predicate-x "Triple X" .
ex:subject-z ex:predicate-z "Triple Z" .
ex:subject-y ex:predicate-y "Triple Y" .
ex:subject-dg ex:predicate-dg "Triple DG" .
"""


# Print out one graph in the Dataset, using a standard Graph serialization format - longturtle
print(d.get_named_graph(URIRef("http://example.com/graph-2")).serialize(format="longturtle"))

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
for s, p, o, g in d.quads():  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG", None
"""

# Loop through all the quads in one Graph - just constrain the Graph field
for s, p, o, g in d.quads((None, None, None, graph_1_id)):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
"""

# Or equivalently, use the "graph" parameter, similar to SPARQL Dataset clauses (FROM,
# FROM NAMED), to restrict the graphs.
for s, p, o, g in d.quads(graph=graph_1_id):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")
# (Produces the same result as above)

# To iterate through only the union of Named Graphs, you can use the special enum
# "named" with the graph parameter
for s, p, o, g in d.quads(graph=GraphEnum.named):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-y, http://example.com/predicate-y, Triple Y, http://example.com/graph-2
"""

# To iterate through the Default Graph, you can use the special enum "default" with
# the graph parameter
for s, p, o, g in d.quads(graph=GraphEnum.default):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG"
"""

# To iterate through multiple graphs, you can pass a list composed of Named Graph URIs
# and the special enums "named" and "default", for example to iterate through the
# default graph and a specified named graph:
for s, p, o, g in d.quads(graph=[graph_1_id, GraphEnum.default]):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}, {g}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X, http://example.com/graph-1
http://example.com/subject-z, http://example.com/predicate-z, Triple Z, http://example.com/graph-1
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG", None
"""

# Looping through triples in one Graph still works too
for s, p, o in d.triples((None, None, None, graph_1_id)):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
"""

# Again, the "graph" parameter can be used
for s, p, o in d.triples(graph=graph_1_id):  # type: ignore[arg-type]
    print(f"{s}, {p}, {o}")

# As the Dataset is inclusive, looping through triples across the whole Dataset will
# yield all triples in both the Default Graph and all Named Graphs.

for s, p, o in d.triples((None, None, None)):
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/subject-y, http://example.com/predicate-y, Triple Y
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG"
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
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG", None
"""

# The 'length' of the Dataset is now five as triples and quads count towards the size/length of a Dataset.
assert len(d) == 5

# Looping through triples sees the 'Z' triple only once
for s, p, o in d.triples((None, None, None)):
    print(f"{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/subject-x, http://example.com/predicate-x, Triple X
http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/subject-y, http://example.com/predicate-y, Triple Y
http://example.com/subject-dg, http://example.com/predicate-dg, "Triple DG"
"""

#######################################################################################
#   3. Manipulating Graphs
#######################################################################################

# List all the Graphs in the Dataset, as the Dataset's Named Graphs are a mapping from
# URIRefs to Graphs
for g_name, g_object in d.graphs().items():
    print(g_name, g_object)

# this returns the graphs, something like:
"""
<http://example.com/graph-1>, <http://example.com/graph-1> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].
<http://example.com/graph-2>, <http://example.com/graph-2> a rdfg:Graph;rdflib:storage [a rdflib:Store;rdfs:label 'Memory'].
"""

# So try this
for g_name in d.graphs():
    print(g_name)

# you should see something like this:
"""
http://example.com/graph-2
http://example.com/graph-1
"""

# Loop through triples per graph
for g_name, g_object in d.graphs():
    print(g_name)
    for s, p, o in g_object:
        print(f"\t{s}, {p}, {o}")

# you should see something like this:
"""
http://example.com/graph-1
	http://example.com/subject-x, http://example.com/predicate-x, Triple X
	http://example.com/subject-z, http://example.com/predicate-z, Triple Z
http://example.com/graph-2
	http://example.com/subject-y, http://example.com/predicate-y, Triple Y
	http://example.com/subject-z, http://example.com/predicate-z, Triple Z
"""

# To remove a graph
d.remove_named_graph(graph_1_id)

# print what's left - one named graph, graph-2, and the default graph:
print(d.serialize(format="trig"))

# you should see something like this:
"""
@prefix ex: <http://example.com/> .

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}

{
    ex:subject-dg ex:predicate-dg "Triple DG" .
}
"""

# To replace a Graph that already exists, you can use the replace_named_graph method

# Create a new Graph
g = Graph()

# Add a triple to the new Graph
g.add(
    (
        URIRef("http://example.com/subject-k"),
        URIRef("http://example.com/predicate-k"),
        Literal("Triple K"),
    )
)

# Add the new Graph to the Dataset
d.replace_named_graph(g, graph_1_id)

# print the updated Dataset
print(d.serialize(format="trig"))

# you should see something like this:
"""

@prefix ex: <http://example.com/> .

ex:graph-1 {
    ex:subject-k ex:predicate-k "Triple K" .
}

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}

{
    ex:subject-dg ex:predicate-dg "Triple DG" .
}
"""

# If you add a Graph with no specified identifier...
g_no_id = Graph()
g_no_id.add(
    (
        URIRef("http://example.com/subject-l"),
        URIRef("http://example.com/predicate-l"),
        Literal("Triple L"),
    )
)
d.add_named_graph(g_no_id)

# now when we print it, we will see a Graph with a Blank Node id:
print(d.serialize(format="trig"))

# you should see somthing like this, but with a different Blank Node ID , as this is rebuilt each code execution
"""
@prefix ex: <http://example.com/> .

ex:graph-1 {
    ex:subject-k ex:predicate-k "Triple K" .
}

ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .

    ex:subject-z ex:predicate-z "Triple Z" .
}

_:N9cc8b54c91724e31896da5ce41e0c937 {
    ex:subject-l ex:predicate-l "Triple L" .
}

{
    ex:subject-dg ex:predicate-dg "Triple DG" .
}
"""

# triples, quads, subjects, predicates, objects, subject_predicates, predicate_objects,
# subject_objects methods support passing a list of values for their parameters, for
# example:

# "Slice" the dataset on specified predicates.
filter_preds = [URIRef("http://example.com/predicate-k"),
                URIRef("http://example.com/predicate-y")]
for s, o in d.subject_objects(filter_preds):
    print(f"{s}, {o}")
# you should see something like this:
"""
http://example.com/subject-k, Triple K
http://example.com/subject-y, Triple Y
"""
