# Upgrading from version 6 to 7

## Python version

RDFLib 7 requires Python 3.8.1 or later.

## New behaviour for `publicID` in `parse` methods

Before version 7, the `publicID` argument to the [`parse()`][rdflib.graph.ConjunctiveGraph.parse] and [`parse()`][rdflib.graph.Dataset.parse] methods was used as the name for the default graph, and triples from the default graph in a source were loaded into the graph
named `publicID`.

In version 7, the `publicID` argument is only used as the base URI for relative URI resolution as defined in [IETF RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986#section-5.1.4).

To accommodate this change, ensure that use of the `publicID` argument is consistent with the new behaviour.

If you want to load triples from a format that does not support named graphs into a named graph, use the following code:

```python
from rdflib import ConjunctiveGraph

cg = ConjunctiveGraph()
cg.get_context("example:graph_name").parse("http://example.com/source.ttl", format="turtle")
```

If you want to move triples from the default graph into a named graph, use the following code:

```python
from rdflib import ConjunctiveGraph

cg = ConjunctiveGraph()
cg.parse("http://example.com/source.trig", format="trig")
destination_graph = cg.get_context("example:graph_name")
for triple in cg.default_context.triples((None, None, None)):
    destination_graph.add(triple)
    cg.default_context.remove(triple)
```
