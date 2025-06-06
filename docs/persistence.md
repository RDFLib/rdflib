# Persistence

RDFLib provides an [`abstracted Store API`][rdflib.store.Store]
for persistence of RDF and Notation 3. The [`Graph`][rdflib.graph.Graph] class works with instances of this API (as the first argument to its constructor) for triple-based management of an RDF store including: garbage collection, transaction management, update, pattern matching, removal, length, and database management ([`Graph.open()`][rdflib.graph.Graph.open] / [`Graph.close()`][rdflib.graph.Graph.close] / [`Graph.destroy()`][rdflib.graph.Graph.destroy]).

Additional persistence mechanisms can be supported by implementing this API for a different store.

## Stores currently shipped with core RDFLib

* [`Memory`][rdflib.plugins.stores.memory.Memory] - not persistent!
* [`BerkeleyDB`][rdflib.plugins.stores.berkeleydb.BerkeleyDB] - on disk persistence via Python's [berkeleydb package](https://pypi.org/project/berkeleydb/)
* [`SPARQLStore`][rdflib.plugins.stores.sparqlstore.SPARQLStore] - a read-only wrapper around a remote SPARQL Query endpoint
* [`SPARQLUpdateStore`][rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore] - a read-write wrapper around a remote SPARQL query/update endpoint pair

## Usage

In most cases, passing the name of the store to the Graph constructor is enough:

```python
from rdflib import Graph

graph = Graph(store='BerkeleyDB')
```

Most stores offering on-disk persistence will need to be opened before reading or writing. When peristing a triplestore, rather than a ConjuntiveGraph quadstore, you need to specify an identifier with which you can open the graph:

```python
graph = Graph('BerkeleyDB', identifier='mygraph')

# first time create the store:
graph.open('/home/user/data/myRDFLibStore', create=True)

# work with the graph:
data = """
PREFIX : <https://example.org/>

:a :b :c .
:d :e :f .
:d :g :h .
"""
graph.parse(data=data, format="ttl")

# when done!
graph.close()
```

When done, [`close()`][rdflib.graph.Graph.close] must be called to free the resources associated with the store.

## Additional store plugins

More store implementations are available in RDFLib extension projects:

* [rdflib-sqlalchemy](https://github.com/RDFLib/rdflib-sqlalchemy) – a store which supports a wide-variety of RDBMS backends
* [rdflib-leveldb](https://github.com/RDFLib/rdflib-leveldb) – a store on top of Google's [LevelDB](https://code.google.com/p/leveldb/) key-value store
* [rdflib-kyotocabinet](https://github.com/RDFLib/rdflib-kyotocabinet) – a store on top of the [Kyoto Cabinet](http://fallabs.com/kyotocabinet/) key-value store

## Example

* [`examples.berkeleydb_example`][examples.berkeleydb_example] contains an example for using a BerkeleyDB store.
* [`examples.sparqlstore_example`][examples.sparqlstore_example] contains an example for using a SPARQLStore.
