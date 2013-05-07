.. _plugin_parsers: Plugin parsers

==============
Plugin parsers
==============

These serializers are available in default RDFLib, you can use them by 
passing the name to graph's :meth:`~rdflib.graph.Graph.parse` method: 

.. code-block:: python

	graph.parse(my_url, format='n3')

The ``html`` parser will auto-detect RDFa, HTurtle or Microdata.

===================== ====================================================================
Name                  Class                                                               
===================== ====================================================================
application/rdf+xml   :class:`~rdflib.plugins.parsers.rdfxml.RDFXMLParser`
application/svg+xml   :class:`~rdflib.plugins.parsers.structureddata.RDFaParser`
application/xhtml+xml :class:`~rdflib.plugins.parsers.structureddata.RDFaParser`
html                  :class:`~rdflib.plugins.parsers.structureddata.StructuredDataParser`
hturtle               :class:`~rdflib.plugins.parsers.hturtle.HTurtleParser`
mdata                 :class:`~rdflib.plugins.parsers.structureddata.MicrodataParser`
microdata             :class:`~rdflib.plugins.parsers.structureddata.MicrodataParser`
n3                    :class:`~rdflib.plugins.parsers.notation3.N3Parser`
nquads                :class:`~rdflib.plugins.parsers.nquads.NQuadsParser`
nt                    :class:`~rdflib.plugins.parsers.nt.NTParser`
rdfa                  :class:`~rdflib.plugins.parsers.structureddata.RDFaParser`
rdfa1.0               :class:`~rdflib.plugins.parsers.structureddata.RDFa10Parser`
rdfa1.1               :class:`~rdflib.plugins.parsers.structureddata.RDFaParser`
text/html             :class:`~rdflib.plugins.parsers.structureddata.StructuredDataParser`
trix                  :class:`~rdflib.plugins.parsers.trix.TriXParser`
turtle                :class:`~rdflib.plugins.parsers.notation3.TurtleParser`
xml                   :class:`~rdflib.plugins.parsers.rdfxml.RDFXMLParser`
===================== ====================================================================
