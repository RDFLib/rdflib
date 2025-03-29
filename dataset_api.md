Incorporate the changes proposed from Martynas, with the exception of graphs(), which would now return a dictionary of graph names (URIRef or BNode) to Graph objects (as the graph's identifier would be removed).

```
add add_named_graph(name: IdentifiedNode, graph: Graph) method
add has_named_graph(name: IdentifiedNode) method
add remove_named_graph(name: IdentifiedNode) method
add replace_named_graph(name: IdentifiedNode, graph: Graph)) method
add graphs() method as an alias for contexts()
add default_graph property as an alias for default_context
add get_named_graph as an alias for get_graph
deprecate graph(graph) method
deprecate remove_graph(graph) method
deprecate contexts() method
Using IdentifiedNode as a super-interface for URIRef and BNode (since both are allowed as graph names in RDF 1.1).
```

Make the following enhancements to the triples, quads, and subject/predicate/object APIs.

Major changes:
P1. Remove `default_union` attribute and make the Dataset inclusive.
P2. Remove the Default Graph URI ("urn:x-rdflib:default").
P3. Remove Graph class's "identifier" attribute to align with the W3C spec, impacting Dataset methods which use the Graph class.
P4. Make the graphs() method of Dataset return a dictionary of named graph names to Graph objects.
Enhancements:
P5. Support passing of iterables of Terms to triples, quads, and related methods, similar to the triples_choices method.
P6. Default the triples method to iterate with `(None, None, None)`

With all of the above changes, including those changes proposed by Martynas, here are some examples:

```python
from rdflib import Dataset, Graph, URIRef, Literal
from rdflib.namespace import RDFS

# ============================================
# Adding Data to the Dataset
# ============================================

# Initialize the dataset
d = Dataset()

# Add a single triple to the Default Graph, and a single triple to a Named Graph
g1 = Graph()
g1.add(
    (
        URIRef("http://example.com/subject-a"),
        URIRef("http://example.com/predicate-a"),
        Literal("Triple A")
    )
)
# merge with the default graph
d.default_graph += g1
# or set the default graph
d.default_graph = g1

# Add a Graph to a Named Graph in the Dataset.
g2 = Graph()
g2.add(
    (
        URIRef("http://example.com/subject-b"),
        URIRef("http://example.com/predicate-b"),
        Literal("Triple B")
    )
)
d.add_named_graph(name=URIRef("http://example.com/graph-B"), g2)

# ============================================
# Iterate over the entire Dataset returning triples
# ============================================

for triple in d.triples():
    print(triple)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'))
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'))

# ============================================
# Iterate over the entire Dataset returning quads
# ============================================

for quad in d.quads():
    print(quad)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'), None)
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'), rdflib.term.URIRef('http://example.com/graph-B'))

# ============================================
# Get the Default graph
# ============================================

dg = d.default_graph  # same as current default_context

# ============================================
# Iterate on triples in the Default Graph only
# ============================================

for triple in d.triples(graph="default"):
    print(triple)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'))

# ============================================
# Access quads in Named Graphs only
# ============================================

for quad in d.quads(graph="named"):
    print(quad)
# Output:
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'), rdflib.term.URIRef('http://example.com/graph-B'))

# ============================================
# Equivalent to iterating over graphs()
# ============================================

for ng_name, ng_object in d.graphs().items():
    for quad in d.quads(graph=ng_name):
        print(quad)
# Output:
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'), rdflib.term.URIRef('http://example.com/graph-B'))

# ============================================
# Access triples in the Default Graph and specified Named Graphs.
# ============================================

for triple in d.triples(graph=["default", URIRef("http://example.com/graph-B")]):
    print(triple)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'))
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'))

# ============================================
# Access quads in the Default Graph and specified Named Graphs.
# ============================================

for quad in d.quads(graph=["default", URIRef("http://example.com/graph-B")]):
    print(quad)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'), None)
(rdflib.term.URIRef('http://example.com/subject-b'), rdflib.term.URIRef('http://example.com/predicate-b'), rdflib.term.Literal('Triple B'), rdflib.term.URIRef('http://example.com/graph-B'))

# ============================================
# "Slice" the dataset on specified predicates. Same can be done on subjects, objects, graphs
# ============================================

filter_preds = [URIRef("http://example.com/predicate-a"), RDFS.label]
for quad in d.quads((None, filter_preds, None, None)):
    print(quad)
# Output:
(rdflib.term.URIRef('http://example.com/subject-a'), rdflib.term.URIRef('http://example.com/predicate-a'), rdflib.term.Literal('Triple A'), None)

# ============================================
# Serialize the Dataset in a quads format.
# ============================================

print(d.serialize(format="nquads"))
# Output:
<http://example.com/subject-a> <http://example.com/predicate-a> "Triple A" .
<http://example.com/subject-b> <http://example.com/predicate-b> "Triple B" <http://example.com/graph-B> .
```
