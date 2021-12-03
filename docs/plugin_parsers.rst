.. _plugin_parsers: Plugin parsers

==============
Plugin parsers
==============

These serializers are available in default RDFLib, you can use them by 
passing the name to graph's :meth:`~rdflib.graph.Graph.parse` method:: 

	graph.parse(my_url, format='n3')

The ``html`` parser will auto-detect RDFa, HTurtle or Microdata.

It is also possible to pass a mime-type for the ``format`` parameter::
    
	graph.parse(my_url, format='application/rdf+xml')

If you are not sure what format your file will be, you can use :func:`rdflib.util.guess_format` which will guess based on the file extension. 

========= ====================================================================
Name      Class                                                               
========= ====================================================================
json-ld   :class:`~rdflib.plugins.parsers.jsonld.JsonLDParser`
html      :class:`~rdflib.plugins.parsers.structureddata.StructuredDataParser`
n3        :class:`~rdflib.plugins.parsers.notation3.N3Parser`
nquads    :class:`~rdflib.plugins.parsers.nquads.NQuadsParser`
nt        :class:`~rdflib.plugins.parsers.ntriples.NTParser`
trix      :class:`~rdflib.plugins.parsers.trix.TriXParser`
turtle    :class:`~rdflib.plugins.parsers.notation3.TurtleParser`
xml       :class:`~rdflib.plugins.parsers.rdfxml.RDFXMLParser`
========= ====================================================================
