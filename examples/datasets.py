"""
An RDFLib Dataset is a slight extension to ConjunctiveGraph: it uses simpler terminology
and has a few additional convenience method extensions, for example add() can be used to
add quads directly to a specific Graph within the Dataset.

This example file shows how to decalre a Dataset, add content to it, serialise it, query it
and remove things from it.
"""

from rdflib import Dataset, URIRef, Literal, Namespace

#
#   Create & Add
#

# Create an empty Dataset
d = Dataset()
# Add a namespace prefix to it, just like for Graph
d.bind("ex", Namespace("http://example.com/"))

# Declare a Graph URI to be used to identify a Graph
graph_1 = URIRef("http://example.com/graph-1")

# Add an empty Graph, identified by graph_1, to the Dataset
d.graph(identifier=graph_1)

# Add two quads to Graph graph_1 in the Dataset
d.add(
    (
        URIRef("http://example.com/subject-x"),
        URIRef("http://example.com/predicate-x"),
        Literal("Triple X"),
        graph_1,
    )
)
d.add(
    (
        URIRef("http://example.com/subject-z"),
        URIRef("http://example.com/predicate-z"),
        Literal("Triple Z"),
        graph_1,
    )
)

# Add another quad to the Dataset to a non-existent Graph:
# the Graph is created automatically
d.add(
    (
        URIRef("http://example.com/subject-y"),
        URIRef("http://example.com/predicate-y"),
        Literal("Triple Y"),
        URIRef("http://example.com/graph-2"),
    )
)

# printing the Dataset like this: print(d.serialize(format="trig"))
# produces a result like this:
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
print("Printing Serialised Dataset:")
print("---")
print(d.serialize(format="trig"))
print("---")
print()
print()

#
#   Use & Query
#

# print the length of the Dataset, i.e. the count of all triples in all Graphs
# we should get
"""
3
"""
print("Printing Dataset Length:")
print("---")
print(len(d))
print("---")
print()
print()

# Query one graph in the Dataset for all it's triples
# we should get
"""
(rdflib.term.URIRef('http://example.com/subject-z'), rdflib.term.URIRef('http://example.com/predicate-z'), rdflib.term.Literal('Triple Z'))
(rdflib.term.URIRef('http://example.com/subject-x'), rdflib.term.URIRef('http://example.com/predicate-x'), rdflib.term.Literal('Triple X'))
"""
print("Printing all triple from one Graph in the Dataset:")
print("---")
for triple in d.triples((None, None, None, graph_1)):
    print(triple)
print("---")
print()
print()

# Query the union of all graphs in the dataset for all triples
# we should get Nothing:
"""
"""
# A Dataset's default union graph does not exist by default (default_union property is False)
print("Attempt #1 to print all triples in the Dataset:")
print("---")
for triple in d.triples((None, None, None, None)):
    print(triple)
print("---")
print()
print()

# Set the Dataset's default_union property to True and re-query
d.default_union = True
print("Attempt #2 to print all triples in the Dataset:")
print("---")
for triple in d.triples((None, None, None, None)):
    print(triple)
print("---")
print()
print()


#
#   Remove
#

# Remove Graph graph_1 from the Dataset
d.remove_graph(graph_1)

# printing the Dataset like this: print(d.serialize(format="trig"))
# now produces a result like this:

"""
ex:graph-2 {
    ex:subject-y ex:predicate-y "Triple Y" .
}
"""
print("Printing Serialised Dataset after graph_1 removal:")
print("---")
print(d.serialize(format="trig").strip())
print("---")
print()
print()
