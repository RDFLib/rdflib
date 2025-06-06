# Loading and saving RDF

## Reading RDF files

RDF data can be represented using various syntaxes (`turtle`, `rdf/xml`, `n3`, `n-triples`, `trix`, `JSON-LD`, etc.). The simplest format is `ntriples`, which is a triple-per-line format.

Create the file `demo.nt` in the current directory with these two lines in it:

```turtle
<http://example.com/drewp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
<http://example.com/drewp> <http://example.com/says> "Hello World" .
```

On line 1 this file says "drewp is a FOAF Person:. On line 2 it says "drep says "Hello World"".

RDFLib can guess what format the file is by the file ending (".nt" is commonly used for n-triples) so you can just use [`parse()`][rdflib.graph.Graph.parse] to read in the file. If the file had a non-standard RDF file ending, you could set the keyword-parameter `format` to specify either an Internet Media Type or the format name (a [list of available parsers][rdflib.plugins.parsers] is available).

In an interactive python interpreter, try this:

```python
from rdflib import Graph

g = Graph()
g.parse("demo.nt")

print(len(g))
# prints: 2

import pprint
for stmt in g:
    pprint.pprint(stmt)
# prints:
# (rdflib.term.URIRef('http://example.com/drewp'),
#  rdflib.term.URIRef('http://example.com/says'),
#  rdflib.term.Literal('Hello World'))
# (rdflib.term.URIRef('http://example.com/drewp'),
#  rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
#  rdflib.term.URIRef('http://xmlns.com/foaf/0.1/Person'))
```

The final lines show how RDFLib represents the two statements in the file: the statements themselves are just length-3 tuples ("triples") and the subjects, predicates, and objects of the triples are all rdflib types.

## Reading remote RDF

Reading graphs from the Internet is easy:

```python
from rdflib import Graph

g = Graph()
g.parse("http://www.w3.org/People/Berners-Lee/card")
print(len(g))
# prints: 86
```

[`parse()`][rdflib.Graph.parse] can process local files, remote data via a URL, as in this example, or RDF data in a string (using the `data` parameter).

## Saving RDF

To store a graph in a file, use the [`serialize()`][rdflib.Graph.serialize] function:

```python
from rdflib import Graph

g = Graph()
g.parse("http://www.w3.org/People/Berners-Lee/card")
g.serialize(destination="tbl.ttl")
```

This parses data from http://www.w3.org/People/Berners-Lee/card and stores it in a file `tbl.ttl` in this directory using the turtle format, which is the default RDF serialization (as of rdflib 6.0.0).

To read the same data and to save it as an RDF/XML format string in the variable `v`, do this:

```python
from rdflib import Graph

g = Graph()
g.parse("http://www.w3.org/People/Berners-Lee/card")
v = g.serialize(format="xml")
```

The following table lists the RDF formats you can serialize data to with rdflib, out of the box, and the `format=KEYWORD` keyword used to reference them within `serialize()`:

| RDF Format | Keyword | Notes |
|------------|---------|-------|
| Turtle | turtle, ttl or turtle2 | turtle2 is just turtle with more spacing & linebreaks |
| RDF/XML | xml or pretty-xml | Was the default format, rdflib < 6.0.0 |
| JSON-LD | json-ld | There are further options for compact syntax and other JSON-LD variants |
| N-Triples | ntriples, nt or nt11 | nt11 is exactly like nt, only utf8 encoded |
| Notation-3 | n3 | N3 is a superset of Turtle that also caters for rules and a few other things |
| Trig | trig | Turtle-like format for RDF triples + context (RDF quads) and thus multiple graphs |
| Trix | trix | RDF/XML-like format for RDF quads |
| N-Quads | nquads | N-Triples-like format for RDF quads |

## Working with multi-graphs

To read and query multi-graphs, that is RDF data that is context-aware, you need to use rdflib's [`Dataset`][rdflib.Dataset] class. This an extension to [`Graph`][rdflib.Graph] that know all about quads (triples + graph IDs).

If you had this multi-graph data file (in the `trig` format, using new-style `PREFIX` statement (not the older `@prefix`):

```turtle
PREFIX eg: <http://example.com/person/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

eg:graph-1 {
    eg:drewp a foaf:Person .
    eg:drewp eg:says "Hello World" .
}

eg:graph-2 {
    eg:nick a foaf:Person .
    eg:nick eg:says "Hi World" .
}
```

You could parse the file and query it like this:

```python
from rdflib import Dataset
from rdflib.namespace import RDF

g = Dataset()
g.parse("demo.trig")

for s, p, o, g in g.quads((None, RDF.type, None, None)):
    print(s, g)
```

This will print out:

```
http://example.com/person/drewp http://example.com/person/graph-1
http://example.com/person/nick http://example.com/person/graph-2
```
