.. _plugin_serializers: Plugin serializers

==================
Plugin serializers
==================

These serializers are available in default RDFLib, you can use them by 
passing the name to a graph's :meth:`~rdflib.graph.Graph.serialize` method::

	print graph.serialize(format='n3')

It is also possible to pass a mime-type for the ``format`` parameter::
    
	graph.serialize(my_url, format='application/rdf+xml')

========== ===============================================================
Name       Class                                                          
========== ===============================================================
json-ld    :class:`~rdflib.plugins.serializers.jsonld.JsonLDSerializer`
n3         :class:`~rdflib.plugins.serializers.n3.N3Serializer`
nquads     :class:`~rdflib.plugins.serializers.nquads.NQuadsSerializer`
nt         :class:`~rdflib.plugins.serializers.nt.NTSerializer`
hext       :class:`~rdflib.plugins.serializers.hext.HextuplesSerializer`
patch      :class:`~rdflib.plugins.serializers.patch.PatchSerializer`
pretty-xml :class:`~rdflib.plugins.serializers.rdfxml.PrettyXMLSerializer`
trig       :class:`~rdflib.plugins.serializers.trig.TrigSerializer`
trix       :class:`~rdflib.plugins.serializers.trix.TriXSerializer`
turtle     :class:`~rdflib.plugins.serializers.turtle.TurtleSerializer`
longturtle :class:`~rdflib.plugins.serializers.longturtle.LongTurtleSerializer`
xml        :class:`~rdflib.plugins.serializers.rdfxml.XMLSerializer`
========== ===============================================================


JSON-LD
-------
JSON-LD - 'json-ld' - has been incorporated into RDFLib since v6.0.0.

RDF Patch
---------

The RDF Patch Serializer - 'patch' - uses the RDF Patch format defined at https://afs.github.io/rdf-patch/. It supports serializing context aware stores as either addition or deletion patches; and also supports serializing the difference between two context aware stores as a Patch of additions and deletions.

HexTuples
---------
The HexTuples Serializer - 'hext' - uses the HexTuples format defined at https://github.com/ontola/hextuples.

For serialization of non-context-aware data sources, e.g. a single ``Graph``, the 'graph' field (6th variable in the 
Hextuple) will be an empty string.

For context-aware (multi-graph) serialization, the 'graph' field of the default graph will be an empty string and 
the values for other graphs will be Blank Node IDs or IRIs.

Longturtle
----------
Longturtle is just the turtle format with newlines preferred over compactness - multiple nodes on the same line 
to enhance the format's text file version control (think Git) friendliness - and more modern forms of prefix markers - 
PREFIX instead of @prefix - to make it as similar to SPARQL as possible.

Longturtle is Turtle 1.1 compliant and will work wherever ordinary turtle works, however some very old parsers don't 
understand PREFIX, only @prefix...
