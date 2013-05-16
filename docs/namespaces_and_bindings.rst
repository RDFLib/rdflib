.. _namespaces_and_bindings: Namespaces and Bindings

=======================
Namespaces and Bindings
=======================

RDFLib provides several short-cuts to working with many URIs in the same namespace. 

The :mod:`rdflib.namespace` defines the :class:`rdflib.namespace.Namespace` class which lets you easily create URIs in a namespace::

	from rdflib import Namespace

	n = Namespace("http://example.org/")
	n.Person # as attribute
	# = rdflib.term.URIRef(u'http://example.org/Person')

	n['first%20name'] # as item - for things that are not valid python identifiers
	# = rdflib.term.URIRef(u'http://example.org/first%20name')

The ``namespace`` module also defines many common namespaces such as RDF, RDFS, OWL, FOAF, SKOS, etc. 

Namespaces can also be associated with prefixes, in a :class:`rdflib.namespace.NamespaceManager`, i.e. using ``foaf`` for ``http://xmlns.com/foaf/0.1/``. Each RDFLib graph has a :attr:`~rdflib.graph.Graph.namespace_manager` that keeps a list of namespace to prefix mappings. The namespace manager is populated when reading in RDF, and these prefixes are used when serialising RDF, or when parsing SPARQL queries. Additional prefixes can be bound with the :meth:`rdflib.graph.bind` method.


Namespaces in SPARQL Queries
----------------------------

The ``initNs`` argument supplied to :meth:`~rdflib.graph.Graph.query` is a dictionary of namespaces to be expanded in the query string. 
If you pass no ``initNs`` argument, the namespaces registered with the graphs namespace_manager are used::

	...
	from rdflib.namespace import FOAF
	graph.query('SELECT * WHERE { ?p a foaf:Person }', initNs={ 'foaf': FOAF })


In order to use an empty prefix (e.g. ``?a :knows ?b``), use a ``PREFIX`` directive with no prefix in the SPARQL query to set a default namespace:

.. code-block:: sparql

    PREFIX : <http://xmlns.com/foaf/0.1/>



