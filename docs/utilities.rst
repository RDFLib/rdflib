Utilities & convenience functions
=================================

For RDF programming, RDFLib and Python may not be the fastest tools,
but we try hard to make them the easiest and most convenient to use and thus the *fastest* overall!

This is a collection of hints and pointers for hassle-free RDF coding.

Functional properties
---------------------

Use :meth:`~rdflib.graph.Graph.value` and
:meth:`~rdflib.graph.Graph.set` to work with :term:`functional
property` instances, i.e. properties than can only occur once for a resource.

.. code-block:: python

    from rdflib import Graph, URIRef, Literal, BNode
    from rdflib.namespace import FOAF, RDF

    g = Graph()
    g.bind("foaf", FOAF)

    # Add demo data
    bob = URIRef("http://example.org/people/Bob")
    g.add((bob, RDF.type, FOAF.Person))
    g.add((bob, FOAF.name, Literal("Bob")))
    g.add((bob, FOAF.age, Literal(38)))

    # To get a single value, use 'value'
    print(g.value(bob, FOAF.age))
    # prints: 38

    # To change a single of value, use 'set'
    g.set((bob, FOAF.age, Literal(39)))
    print(g.value(bob, FOAF.age))
    # prints: 39


Slicing graphs
--------------

Python allows slicing arrays with a ``slice`` object, a triple of
``start``, ``stop`` and ``step-size``:

.. code-block:: python

    for i in range(20)[2:9:3]:
        print(i)
    # prints:
    # 2, 5, 8


RDFLib graphs override ``__getitem__`` and we pervert the slice triple
to be a RDF triple instead. This lets slice syntax be a shortcut for
:meth:`~rdflib.graph.Graph.triples`,
:meth:`~rdflib.graph.Graph.subject_predicates`,
:meth:`~rdflib.graph.Graph.contains`, and other Graph query-methods:

.. code-block:: python

    from rdflib import Graph, URIRef, Literal, BNode
    from rdflib.namespace import FOAF, RDF

    g = Graph()
    g.bind("foaf", FOAF)

    # Add demo data
    bob = URIRef("http://example.org/people/Bob")
    bill = URIRef("http://example.org/people/Bill")
    g.add((bob, RDF.type, FOAF.Person))
    g.add((bob, FOAF.name, Literal("Bob")))
    g.add((bob, FOAF.age, Literal(38)))
    g.add((bob, FOAF.knows, bill))

    print(g[:])
    # same as
    print(iter(g))

    print(g[bob])
    # same as
    print(g.predicate_objects(bob))

    print(g[bob: FOAF.knows])
    # same as
    print(g.objects(bob, FOAF.knows))

    print(g[bob: FOAF.knows: bill])
    # same as
    print((bob, FOAF.knows, bill) in g)

    print(g[:FOAF.knows])
    # same as
    print(g.subject_objects(FOAF.knows))


See :mod:`examples.slice` for a complete example. 

.. note:: Slicing is convenient for run-once scripts for playing around
          in the Python ``REPL``, however since slicing returns
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
readable representation of a term.  All terms (URIRef, Literal etc.) have a
``n3``, method, which will return a suitable N3 format:

.. code-block:: python

    from rdflib import Graph, URIRef, Literal
    from rdflib.namespace import FOAF

    # A URIRef
    person = URIRef("http://xmlns.com/foaf/0.1/Person")
    print(person.n3())
    # prints: <http://xmlns.com/foaf/0.1/Person>

    # Simplifying the output with a namespace prefix:
    g = Graph()
    g.bind("foaf", FOAF)

    print(person.n3(g.namespace_manager))
    # prints foaf:Person

    # A typed literal
    l = Literal(2)
    print(l.n3())
    # prints "2"^^<http://www.w3.org/2001/XMLSchema#integer>

    # Simplifying the output with a namespace prefix
    # XSD is built in, so no need to bind() it!
    l.n3(g.namespace_manager)
    # prints: "2"^^xsd:integer

Parsing data from a string
--------------------------

You can parse data from a string with the ``data`` param:

.. code-block:: python

    from rdflib import Graph

    g = Graph().parse(data="<a:> <p:> <p:>.")
    for r in g.triples((None, None, None)):
        print(r)
    # prints: (rdflib.term.URIRef('a:'), rdflib.term.URIRef('p:'), rdflib.term.URIRef('p:'))

Command Line tools
------------------

RDFLib includes a handful of commandline tools, see :mod:`rdflib.tools`.
