# Namespaces and Bindings

RDFLib provides several short-cuts to working with many URIs in the same namespace.

The [`rdflib.namespace`][rdflib.namespace] module defines the [`Namespace`][rdflib.namespace.Namespace] class which lets you easily create URIs in a namespace:

```python
from rdflib import Namespace

EX = Namespace("http://example.org/")
EX.Person  # a Python attribute for EX. This example is equivalent to rdflib.term.URIRef("http://example.org/Person")

# use dict notation for things that are not valid Python identifiers, e.g.:
n['first%20name']  # as rdflib.term.URIRef("http://example.org/first%20name")
```

These two styles of namespace creation - object attribute and dict - are equivalent and are made available just to allow for valid RDF namespaces and URIs that are not valid Python identifiers. This isn't just for syntactic things like spaces, as per the example of `first%20name` above, but also for Python reserved words like `class` or `while`, so for the URI `http://example.org/class`, create it with `EX['class']`, not `EX.class`.

## Common Namespaces

The `namespace` module defines many common namespaces such as RDF, RDFS, OWL, FOAF, SKOS, PROF, etc. The list of the namespaces provided grows with user contributions to RDFLib.

These Namespaces, and any others that users define, can also be associated with prefixes using the [`NamespaceManager`][rdflib.namespace.NamespaceManager], e.g. using `foaf` for `http://xmlns.com/foaf/0.1/`.

Each RDFLib graph has a [`namespace_manager`][rdflib.graph.Graph.namespace_manager] that keeps a list of namespace to prefix mappings. The namespace manager is populated when reading in RDF, and these prefixes are used when serialising RDF, or when parsing SPARQL queries. Prefixes can be bound with the [`bind()`][rdflib.graph.Graph.bind] method:

```python
from rdflib import Graph, Namespace
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
g.bind("foaf", FOAF)  # bind an RDFLib-provided namespace to a prefix
g.bind("ex", EX)      # bind a user-declared namespace to a prefix
```


The [`bind()`][rdflib.graph.Graph.bind] method is actually supplied by the [`NamespaceManager`][rdflib.namespace.NamespaceManager] class - see next.

## NamespaceManager

Each RDFLib graph comes with a [`NamespaceManager`][rdflib.namespace.NamespaceManager] instance in the [`namespace_manager`][rdflib.graph.Graph.namespace_manager] field; you can use the [`bind()`][rdflib.namespace.NamespaceManager.bind] method of this instance to bind a prefix to a namespace URI, as above, however note that the [`NamespaceManager`][rdflib.namespace.NamespaceManager] automatically performs some bindings according to a selected strategy.

Namespace binding strategies are indicated with the `bind_namespaces` input parameter to [`NamespaceManager`][rdflib.namespace.NamespaceManager] instances and may be set via `Graph` also:

```python
from rdflib import Graph
from rdflib.namespace import NamespaceManager

g = Graph(bind_namespaces="rdflib")  # bind via Graph

g2 = Graph()
nm = NamespaceManager(g2, bind_namespaces="rdflib")  # bind via NamespaceManager
```


Valid strategies are:

- core:
  - binds several core RDF prefixes only
  - owl, rdf, rdfs, xsd, xml from the NAMESPACE_PREFIXES_CORE object
  - this is default
- rdflib:
  - binds all the namespaces shipped with RDFLib as DefinedNamespace instances
  - all the core namespaces and all the following: brick, csvw, dc, dcat
  - dcmitype, dcterms, dcam, doap, foaf, geo, odrl, org, prof, prov, qb, sdo
  - sh, skos, sosa, ssn, time, vann, void
  - see the NAMESPACE_PREFIXES_RDFLIB object in [`rdflib.namespace`][rdflib.namespace] for up-to-date list
- none:
  - binds no namespaces to prefixes
  - note this is NOT default behaviour
- cc:
  - using prefix bindings from prefix.cc which is a online prefixes database
  - not implemented yet - this is aspirational

### Re-binding

Note that regardless of the strategy employed, prefixes for namespaces can be overwritten with users preferred prefixes, for example:

```python
from rdflib import Graph
from rdflib.namespace import GEO  # imports GeoSPARQL's namespace

g = Graph(bind_namespaces="rdflib")  # binds GeoSPARQL's namespace to prefix 'geo'

g.bind('geosp', GEO, override=True)
```

[`NamespaceManager`][rdflib.namespace.NamespaceManager] also has a method to normalize a given url:

```python
from rdflib.namespace import NamespaceManager

nm = NamespaceManager(Graph())
nm.normalizeUri(t)
```

For simple output, or simple serialisation, you often want a nice readable representation of a term. All RDFLib terms have a `.n3()` method, which will return a suitable N3 format and into which you can supply a NamespaceManager instance to provide prefixes, i.e. `.n3(namespace_manager=some_nm)`:

```python
>>> from rdflib import Graph, URIRef, Literal, BNode
>>> from rdflib.namespace import FOAF, NamespaceManager

>>> person = URIRef("http://xmlns.com/foaf/0.1/Person")
>>> person.n3()
'<http://xmlns.com/foaf/0.1/Person>'

>>> g = Graph()
>>> g.bind("foaf", FOAF)

>>> person.n3(g.namespace_manager)
'foaf:Person'

>>> l = Literal(2)
>>> l.n3()
'"2"^^<http://www.w3.org/2001/XMLSchema#integer>'

>>> l.n3(NamespaceManager(Graph(), bind_namespaces="core"))
'"2"^^xsd:integer'
```

The namespace manager also has a useful method `compute_qname`. `g.namespace_manager.compute_qname(x)` (or just `g.compute_qname(x)`) which takes a URI and decomposes it into the parts:

```python
self.assertEqual(g.compute_qname(URIRef("http://foo/bar#baz")),
                ("ns2", URIRef("http://foo/bar#"), "baz"))
```

## Namespaces in SPARQL Queries

The `initNs` argument supplied to [`query()`][rdflib.graph.Graph.query] is a dictionary of namespaces to be expanded in the query string. If you pass no `initNs` argument, the namespaces registered with the graphs namespace_manager are used:

```python
from rdflib.namespace import FOAF
graph.query('SELECT * WHERE { ?p a foaf:Person }', initNs={'foaf': FOAF})
```

In order to use an empty prefix (e.g. `?a :knows ?b`), use a `PREFIX` directive with no prefix in the SPARQL query to set a default namespace:

```sparql
PREFIX : <http://xmlns.com/foaf/0.1/>
```
