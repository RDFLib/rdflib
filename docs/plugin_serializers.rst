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
n3         :class:`~rdflib.plugins.serializers.n3.N3Serializer`
nquads     :class:`~rdflib.plugins.serializers.nquads.NQuadsSerializer`
nt         :class:`~rdflib.plugins.serializers.nt.NTSerializer`
pretty-xml :class:`~rdflib.plugins.serializers.rdfxml.PrettyXMLSerializer`
trig       :class:`~rdflib.plugins.serializers.trig.TrigSerializer`
trix       :class:`~rdflib.plugins.serializers.trix.TriXSerializer`
turtle     :class:`~rdflib.plugins.serializers.turtle.TurtleSerializer`
xml        :class:`~rdflib.plugins.serializers.rdfxml.XMLSerializer`
========== ===============================================================

