# Plugins

![rdflib plugin "architecture"](_static/plugins-diagram.svg)

Many parts of RDFLib are extensible with plugins, [see setuptools' 'Creating and discovering plugins'](https://packaging.python.org/guides/creating-and-discovering-plugins/). These pages list the plugins included in RDFLib core.

* [`Parser Plugins`][rdflib.plugins.parsers]
* [`Serializer Plugins`][rdflib.plugins.serializers]
* [`Store Plugins`][rdflib.plugins.stores]
* [`Query Results Plugins`][rdflib.plugins.sparql.results]

## Plugin stores

### Built In

The following Stores are contained within the rdflib core package:

| Name | Class |
| --- | --- |
| Auditable | [`AuditableStore`][rdflib.plugins.stores.auditable.AuditableStore] |
| Concurrent | [`ConcurrentStore`][rdflib.plugins.stores.concurrent.ConcurrentStore] |
| SimpleMemory | [`SimpleMemory`][rdflib.plugins.stores.memory.SimpleMemory] |
| Memory | [`Memory`][rdflib.plugins.stores.memory.Memory] |
| SPARQLStore | [`SPARQLStore`][rdflib.plugins.stores.sparqlstore.SPARQLStore] |
| SPARQLUpdateStore | [`SPARQLUpdateStore`][rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore] |
| BerkeleyDB | [`BerkeleyDB`][rdflib.plugins.stores.berkeleydb.BerkeleyDB] |
| default | [`Memory`][rdflib.plugins.stores.memory.Memory] |

### External

The following Stores are defined externally to rdflib's core package, so look to their documentation elsewhere for specific details of use.

| Name | Repository | Notes |
| --- | --- | --- |
| SQLAlchemy | [github.com/RDFLib/rdflib-sqlalchemy](https://github.com/RDFLib/rdflib-sqlalchemy) | An SQLAlchemy-backed, formula-aware RDFLib Store. Tested dialects are: SQLite, MySQL & PostgreSQL |
| leveldb | [github.com/RDFLib/rdflib-leveldb](https://github.com/RDFLib/rdflib-leveldb) | An adaptation of RDFLib BerkeleyDB Store's key-value approach, using LevelDB as a back-end |
| Kyoto Cabinet | [github.com/RDFLib/rdflib-kyotocabinet](https://github.com/RDFLib/rdflib-kyotocabinet) | An adaptation of RDFLib BerkeleyDB Store's key-value approach, using Kyoto Cabinet as a back-end |
| HDT | [github.com/RDFLib/rdflib-hdt](https://github.com/RDFLib/rdflib-hdt) | A Store back-end for rdflib to allow for reading and querying [HDT](https://www.rdfhdt.org/) documents |
| Oxigraph | [github.com/oxigraph/oxrdflib](https://github.com/oxigraph/oxrdflib) | Works with the [Pyoxigraph](https://oxigraph.org/pyoxigraph) Python graph database library |
| pycottas | [github.com/arenas-guerrero-julian/pycottas](https://github.com/arenas-guerrero-julian/pycottas) | A Store backend for querying compressed [COTTAS](https://pycottas.readthedocs.io/#cottas-files) files |

*If you have, or know of a Store implementation and would like it listed here, please submit a Pull Request!*

### Use

You can use these stores like this:

```python
from rdflib import Graph

# use the default memory Store
graph = Graph()

# use the BerkeleyDB Store
graph = Graph(store="BerkeleyDB")
```

In some cases, you must explicitly *open* and *close* a store, for example:

```python
from rdflib import Graph

# use the BerkeleyDB Store
graph = Graph(store="BerkeleyDB")
graph.open("/some/folder/location")
# do things ...
graph.close()
```

## Plugin parsers

These serializers are available in default RDFLib, you can use them by passing the name to graph's [`parse()`][rdflib.graph.Graph.parse] method:

```python
graph.parse(my_url, format='n3')
```

The `html` parser will auto-detect RDFa, HTurtle or Microdata.

It is also possible to pass a mime-type for the `format` parameter:

```python
graph.parse(my_url, format='application/rdf+xml')
```

If you are not sure what format your file will be, you can use [`guess_format()`][rdflib.util.guess_format] which will guess based on the file extension.

| Name    | Class                                                         |
|---------|---------------------------------------------------------------|
| json-ld | [`JsonLDParser`][rdflib.plugins.parsers.jsonld.JsonLDParser]  |
| hext    | [`HextuplesParser`][rdflib.plugins.parsers.hext.HextuplesParser] |
| n3      | [`N3Parser`][rdflib.plugins.parsers.notation3.N3Parser]       |
| nquads  | [`NQuadsParser`][rdflib.plugins.parsers.nquads.NQuadsParser]  |
| patch   | [`RDFPatchParser`][rdflib.plugins.parsers.patch.RDFPatchParser] |
| nt      | [`NTParser`][rdflib.plugins.parsers.ntriples.NTParser]        |
| trix    | [`TriXParser`][rdflib.plugins.parsers.trix.TriXParser]        |
| turtle  | [`TurtleParser`][rdflib.plugins.parsers.notation3.TurtleParser] |
| xml     | [`RDFXMLParser`][rdflib.plugins.parsers.rdfxml.RDFXMLParser]  |

### Multi-graph IDs

Note that for correct parsing of multi-graph data, e.g. TriG, HexTuple, etc., into a `Dataset`, as opposed to a context-unaware `Graph`, you will need to set the `publicID` of the `Dataset` to the identifier of the `default_context` (default graph), for example:

```python
d = Dataset()
d.parse(
    data=""" ... """,
    format="trig",
    publicID=d.default_context.identifier
)
```

(from the file tests/test_serializer_hext.py)

## Plugin serializers

These serializers are available in default RDFLib, you can use them by
passing the name to a graph's [`serialize()`][rdflib.graph.Graph.serialize] method:

```python
print graph.serialize(format='n3')
```

It is also possible to pass a mime-type for the `format` parameter:

```python
graph.serialize(my_url, format='application/rdf+xml')
```

| Name | Class |
|------|-------|
| json-ld | [`JsonLDSerializer`][rdflib.plugins.serializers.jsonld.JsonLDSerializer] |
| n3 | [`N3Serializer`][rdflib.plugins.serializers.n3.N3Serializer] |
| nquads | [`NQuadsSerializer`][rdflib.plugins.serializers.nquads.NQuadsSerializer] |
| nt | [`NTSerializer`][rdflib.plugins.serializers.nt.NTSerializer] |
| hext | [`HextuplesSerializer`][rdflib.plugins.serializers.hext.HextuplesSerializer] |
| patch | [`PatchSerializer`][rdflib.plugins.serializers.patch.PatchSerializer] |
| pretty-xml | [`PrettyXMLSerializer`][rdflib.plugins.serializers.rdfxml.PrettyXMLSerializer] |
| trig | [`TrigSerializer`][rdflib.plugins.serializers.trig.TrigSerializer] |
| trix | [`TriXSerializer`][rdflib.plugins.serializers.trix.TriXSerializer] |
| turtle | [`TurtleSerializer`][rdflib.plugins.serializers.turtle.TurtleSerializer] |
| longturtle | [`LongTurtleSerializer`][rdflib.plugins.serializers.longturtle.LongTurtleSerializer] |
| xml | [`XMLSerializer`][rdflib.plugins.serializers.rdfxml.XMLSerializer] |

### JSON-LD

JSON-LD - 'json-ld' - has been incorporated into RDFLib since v6.0.0.

### RDF Patch

The RDF Patch Serializer - 'patch' - uses the RDF Patch format defined at https://afs.github.io/rdf-patch/. It supports serializing context aware stores as either addition or deletion patches; and also supports serializing the difference between two context aware stores as a Patch of additions and deletions.

### HexTuples

The HexTuples Serializer - 'hext' - uses the HexTuples format defined at https://github.com/ontola/hextuples.

For serialization of non-context-aware data sources, e.g. a single `Graph`, the 'graph' field (6th variable in the Hextuple) will be an empty string.

For context-aware (multi-graph) serialization, the 'graph' field of the default graph will be an empty string and the values for other graphs will be Blank Node IDs or IRIs.

### Longturtle

Longturtle is just the turtle format with newlines preferred over compactness - multiple nodes on the same line to enhance the format's text file version control (think Git) friendliness - and more modern forms of prefix markers - PREFIX instead of @prefix - to make it as similar to SPARQL as possible.

Longturtle is Turtle 1.1 compliant and will work wherever ordinary turtle works, however some very old parsers don't understand PREFIX, only @prefix...

## Plugin query results

Plugins for reading and writing of (SPARQL) [`Result`][rdflib.query.Result] - pass `name` to either [`parse()`][rdflib.query.Result.parse] or [`serialize()`][rdflib.query.Result.serialize]

### Parsers

| Name | Class |
| ---- | ----- |
| csv  | [`CSVResultParser`][rdflib.plugins.sparql.results.csvresults.CSVResultParser] |
| json | [`JSONResultParser`][rdflib.plugins.sparql.results.jsonresults.JSONResultParser] |
| tsv  | [`TSVResultParser`][rdflib.plugins.sparql.results.tsvresults.TSVResultParser] |
| xml  | [`XMLResultParser`][rdflib.plugins.sparql.results.xmlresults.XMLResultParser] |

### Serializers

| Name | Class |
| ---- | ----- |
| csv  | [`CSVResultSerializer`][rdflib.plugins.sparql.results.csvresults.CSVResultSerializer] |
| json | [`JSONResultSerializer`][rdflib.plugins.sparql.results.jsonresults.JSONResultSerializer] |
| txt  | [`TXTResultSerializer`][rdflib.plugins.sparql.results.txtresults.TXTResultSerializer] |
| xml  | [`XMLResultSerializer`][rdflib.plugins.sparql.results.xmlresults.XMLResultSerializer] |
