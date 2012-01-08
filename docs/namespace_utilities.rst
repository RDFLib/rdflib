.. _namespace_utilities:

===================
Namespace Utilities
===================

RDFLib provides mechanisms for managing Namespaces.

In particular, there is a :class:`~rdflib.namespace.Namespace` class that takes as its argument the base URI of the namespace.

.. code-block:: pycon

    >>> from rdflib.namespace import Namespace
    >>> fuxi = Namespace('http://metacognition.info/ontologies/FuXi.n3#')

Fully qualified URIs in the namespace can be constructed either by attribute or by dictionary access on Namespace instances:

.. code-block:: pycon

    >>> fuxi.ruleBase
    u'http://metacognition.info/ontologies/FuXi.n3#ruleBase'
    >>> fuxi['ruleBase']
    u'http://metacognition.info/ontologies/FuXi.n3#ruleBase'

Automatic handling of unknown predicates
-----------------------------------------

As a programming convenience, a namespace binding is automatically created when :class:`rdflib.term.URIRef` predicates are added to the graph:

.. code-block:: pycon

    >>> from rdflib import Graph, URIRef
    >>> g = Graph()
    >>> g.add((URIRef("http://example0.com/foo"),
    ...        URIRef("http://example1.com/bar"),
    ...        URIRef("http://example2.com/baz")))
    >>> g.serialize(format="n3")
    @prefix ns1: <http://example1.com/> .

    <http://example0.com/foo> ns1:bar <http://example2.com/baz> .

Namespace manager
-----------------

The :class:`rdflib.namespace.NamespaceManager` takes a :class:`rdflib.graph.Graph` as an argument

Importable namespaces
-----------------------

The following namespaces are available by directly importing from rdflib:

* RDF
* RDFS
* OWL
* XSD

.. code-block:: pycon

	>>> from rdflib import OWL
	>>> OWL.seeAlso
	rdflib.term.URIRef('http://www.w3.org/2002/07/owl#seeAlso')


Modules
--------

.. automodule:: rdflib.namespace
    :members:

.. autoclass:: rdflib.namespace.Namespace
    :members:

.. autofunction:: rdflib.namespace.split_uri
