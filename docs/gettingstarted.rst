.. _gettingstarted:

===========================
Getting started with rdflib
===========================

The primary interface that ``rdflib`` exposes for working with RDF is :class:`~rdflib.graph.Graph`. The package uses various Python idioms that offer an appropriate way to introduce RDF to a Python programmer who hasn't worked with RDF before.

``rdflib`` graphs are not sorted containers; they have ordinary ``set`` operations (e.g. :meth:`~rdflib.Graph.add` to add a triple) plus methods that search triples and return them in arbitrary order.

``rdflib`` graphs also redefine certain built-in Python methods in order to behave in a predictable way; they `emulate container types <http://docs.python.org/release/2.5.2/ref/sequence-types.html>`_ and are best thought of as a set of 3-item triples:

.. code-block:: text

    [
        (subject,  predicate,  object),
        (subject1, predicate1, object1),
        ... 
        (subjectN, predicateN, objectN)
     ]

A tiny usage example:

.. code-block:: pycon

    >>> import rdflib
    >>> g = rdflib.Graph()
    >>> result = g.parse("http://www.w3.org/People/Berners-Lee/card")
    >>> print("graph has %s statements." % len(g))
    graph has 79 statements.
    >>> for subj, pred, obj in g:
    ...     if (subj, pred, obj) not in g:
    ...         raise Exception("It better be!")
    >>> s = g.serialize(format='n3')

A more extensive example:


.. code-block:: python

    from rdflib.graph import Graph
    from rdflib import Literal, BNode, Namespace
    from rdflib import RDF

    g = Graph()

    # Bind a few prefix, namespace pairs.
    g.bind("dc", "http://http://purl.org/dc/elements/1.1/")
    g.bind("foaf", "http://xmlns.com/foaf/0.1/")

    # Create a namespace object for the Friend of a friend namespace.
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    # Create an identifier to use as the subject for Donna.
    donna = BNode()

    # Add triples using store's add method.
    g.add((donna, RDF.type, FOAF["Person"]))
    g.add((donna, FOAF["nick"], Literal("donna", lang="foo")))
    g.add((donna, FOAF["name"], Literal("Donna Fales")))

    # Iterate over triples in store and print them out.
    print("--- printing raw triples ---")
    for s, p, o in g:
        print((s, p, o))

    # For each foaf:Person in the store print out its mbox property.
    print("--- printing mboxes ---")
    for person in g.subjects(RDF.type, FOAF["Person"]):
        for mbox in g.objects(person, FOAF["mbox"]):
            print(mbox)

