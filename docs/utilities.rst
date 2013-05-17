Utilities and convenience functions
===================================

For RDF programming, RDFLib and Python may not execute the fastest,
but we try hard to make it the fastest and most convenient way to write!

This is a collection of hints and pointers for hassle free RDF-coding.

User-friendly labels
--------------------

Use :meth:`~rdflib.graph.Graph.label` to quickly look up the RDFS
label of something, or better use
:meth:`~rdflib.graph.Graph.preferredLabel` to find a label using
several different properties (i.e. either ``rdfs:label``,
``skos:preferredLabel``, ``dc:title``, etc.).

Functional properties
---------------------

Use :meth:`~rdflib.graph.Graph.value` and
:meth:`~rdflib.graph.Graph.set` to work with :term:`functional
properties`, i.e. properties than can only occur once for a resource.

Slicing graphs
--------------

Python allows slicing arrays with a ``slice`` object, a triple of
``start``, ``stop`` index and step-size::

   >>> range(10)[2:9:3] 
   [2, 5, 8]

RDFLib graphs override ``__getitem__`` and we pervert the slice triple
to be a RDF triple instead. This lets slice syntax be a shortcut for
:meth:`~rdflib.graph.Graph.triples`,
:meth:`~rdflib.graph.Graph.subject_predicates`,
:meth:`~rdflib.graph.Graph.contains`, and other Graph query-methods::

   graph[:] 
   # same as 
   iter(graph)

   graph[bob] 
   # same as 
   graph.predicate_objects(bob)

   graph[bob : FOAF.knows]
   # same as
   graph.objects(bob, FOAF.knows)
   
   graph[bob : FOAF.knows : bill] 
   # same as
   (bob, FOAF.knows, bill) in graph

   graph[:FOAF.knows]
   # same as
   graph.subject_objects(FOAF.knows)

   ...

See :mod:`examples.slice` for a complete example. 

.. note:: Slicing is convenient for run-once scripts of playing around
          in the Python ``REPL``. However, since slicing returns
          tuples of varying length depending on which parts of the
          slice are bound, you should be careful using it in more
          complicated programs. If you pass in variables, and they are
          ``None`` or ``False``, you may suddenly get a generator of
          different length tuples back than you expect.

SPARQL Paths
------------

`SPARQL property paths
<http://www.w3.org/TR/sparql11-property-paths/>`_ are possible using
overridden operators on URIRefs. See :mod:`examples.foafpaths` and
:mod:`rdflib.paths`.

Serializing a single term to N3
-------------------------------

For simple output, or simple serialisation, you often want a nice
readable representation of a term.  All terms have a
``.n3(namespace_manager = None)`` method, which will return a suitable
N3 format::

   >>> from rdflib import Graph, URIRef, Literal, BNode
   >>> from rdflib.namespace import FOAF, NamespaceManager

   >>> person = URIRef('http://xmlns.com/foaf/0.1/Person')
   >>> person.n3()
   u'<http://xmlns.com/foaf/0.1/Person>'

   >>> g = Graph()
   >>> g.bind("foaf", FOAF)

   >>> person.n3(g.namespace_manager)
   u'foaf:Person'

   >>> l = Literal(2)
   >>> l.n3()
   u'"2"^^<http://www.w3.org/2001/XMLSchema#integer>'
   
   >>> l.n3(g.namespace_manager)
   u'"2"^^xsd:integer'

Parsing data from a string
--------------------------

You can parse data from a string with the ``data`` param::

    graph.parse(data = '<urn:a> <urn:p> <urn:b>.', format='n3')

Commandline-tools
-----------------

RDFLib includes a handful of commandline tools, see :mod:`rdflib.tools`.
