.. _namespaces_and_bindings: Namespaces and Bindings

=======================
Namespaces and Bindings
=======================

RDFLib provides several short-cuts to working with many URIs in the same namespace. 

The :mod:`rdflib.namespace` defines the :class:`rdflib.namespace.Namespace` class which lets you easily create URIs in a namespace::

	from rdflib import Namespace

	n = Namespace("http://example.org/")
	n.Person  # as attribute
	# = rdflib.term.URIRef("http://example.org/Person")

	n['first%20name']  # as item - for things that are not valid python identifiers
	# = rdflib.term.URIRef("http://example.org/first%20name")

Note that if a name string is valid for use in an RDF namespace but not valid as a Python identifier, such as '1234', it must be addressed with the "item" syntax (using the "attribute" syntax will raise a Syntax Error).

The ``namespace`` module also defines many common namespaces such as RDF, RDFS, OWL, FOAF, SKOS, PROF, etc.

Namespaces can also be associated with prefixes, in a :class:`rdflib.namespace.NamespaceManager`, i.e. using ``foaf`` for ``http://xmlns.com/foaf/0.1/``. Each RDFLib graph has a :attr:`~rdflib.graph.Graph.namespace_manager` that keeps a list of namespace to prefix mappings. The namespace manager is populated when reading in RDF, and these prefixes are used when serialising RDF, or when parsing SPARQL queries. Additional prefixes can be bound with the :meth:`rdflib.graph.bind` method.

NamespaceManager
----------------


Each graph comes with a `NamespaceManager`__ instance in the `namespace_manager` field; you can use the `bind` method of this instance to bind a prefix to a namespace URI::

	myGraph.namespace_manager.bind('prefix', URIRef('scheme:my-namespace-uri:'))
        myGraph.namespace_manager.bind('owl', OWL_NS, override=False)

It has a method to normalize a given url :

	myGraph.namespace_manager.normalizeUri(t)


For simple output, or simple serialisation, you often want a nice
readable representation of a term.  All terms have a
``.n3(namespace_manager = None)`` method, which will return a suitable
N3 format::

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
   
   >>> l.n3(g.namespace_manager)
   '"2"^^xsd:integer'
   
The namespace manage also has a useful method compute_qname
g.namespace_manager.compute_qname(x) which takes an url and decomposes it into the parts::

    self.assertEqual(g.compute_qname(URIRef("http://foo/bar#baz")),
	            ("ns2", URIRef("http://foo/bar#"), "baz"))
   
__ http://rdflib.net/rdflib-2.4.0/html/public/rdflib.syntax.NamespaceManager.NamespaceManager-class.html


Namespaces in SPARQL Queries
----------------------------

The ``initNs`` argument supplied to :meth:`~rdflib.graph.Graph.query` is a dictionary of namespaces to be expanded in the query string. 
If you pass no ``initNs`` argument, the namespaces registered with the graphs namespace_manager are used::

    from rdflib.namespace import FOAF
    graph.query('SELECT * WHERE { ?p a foaf:Person }', initNs={ 'foaf': FOAF })


In order to use an empty prefix (e.g. ``?a :knows ?b``), use a ``PREFIX`` directive with no prefix in the SPARQL query to set a default namespace:

.. code-block:: sparql

    PREFIX : <http://xmlns.com/foaf/0.1/>



