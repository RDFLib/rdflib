=============================================
Frequently Asked Questions about using RDFLib
=============================================

Questions about parsing
=======================

Questions about manipulating
============================

Questions about serializing
===========================

Which serialization method is the most efficient?
=================================================

Currently, the "nt" output format uses the most efficient
serialization; "rdf/xml" should also be efficient.  You can
serialize to these formats using code similar to the following::

	myGraph.serialize(target_nt, format="nt")
	myGraph.serialize(target_rdfxml, format="xml")

How can I use some of the abbreviated RDF/XML syntax?
=====================================================

Use the "pretty-xml" `format` argument to the `serialize` method::

	myGraph.serialize(target_pretty, format="pretty-xml")

How can I control the binding of prefixes to XML namespaces when using RDF/XML?
===============================================================================

Each graph comes with a `NamespaceManager`__ instance in the `namespace_manager` field; you can use the `bind` method of this instance to bind a prefix to a namespace URI::


	myGraph.namespace_manager.bind('prefix', URIRef('scheme:my-namespace-uri:'))

__ http://rdflib.net/rdflib-2.4.0/html/public/rdflib.syntax.NamespaceManager.NamespaceManager-class.html

Does RDFLib support serialization to the `TriX`__ format?
=========================================================

Yes, both parsing and serialising is supported::

	graph.serialize(format="trix") and graph.load(source, format="trix")

__ http://www.w3.org/2004/03/trix/
