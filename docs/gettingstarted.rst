.. _gettingstarted:

===============================
Getting started with RDFLib
===============================

Installation
============

RDFLib is open source and is maintained in a
`GitHub <http://github.com/RDFLib/rdflib/>`_ repository. RDFLib releases, current and previous,
are listed on `PyPi <http://pypi.python.org/pypi/rdflib/>`_

The best way to install RDFLib is to use ``pip`` (sudo as required):

.. code-block :: bash

    $ pip install rdflib

If you want the latest code to run, clone the master branch of the GitHub repo and use that or you can  ``pip install``
directly from GitHub:

.. code-block :: bash

    $ pip install git+https://github.com/RDFLib/rdflib.git@master#egg=rdflib


Support
=======
Usage support is available via questions tagged with ``[rdflib]`` on `StackOverflow <https://stackoverflow.com/questions/tagged/rdflib>`__
and development support, notifications and detailed discussion through the rdflib-dev group (mailing list):

    http://groups.google.com/group/rdflib-dev

If you notice an bug or want to request an enhancement, please do so via our Issue Tracker in Github:

    `<http://github.com/RDFLib/rdflib/issues>`_

How it all works
================
*The package uses various Python idioms
that offer an appropriate way to introduce RDF to a Python programmer
who hasn't worked with RDF before.*

The primary interface that RDFLib exposes for working with RDF is a
:class:`~rdflib.graph.Graph`.

RDFLib graphs are un-sorted containers; they have ordinary ``set``
operations (e.g. :meth:`~rdflib.Graph.add` to add a triple) plus
methods that search triples and return them in arbitrary order.

RDFLib graphs also redefine certain built-in Python methods in order
to behave in a predictable way: they `emulate container types
<http://docs.python.org/release/2.5.2/ref/sequence-types.html>`_ and
are best thought of as a set of 3-item tuples ("triples", in RDF-speak):

.. code-block:: text

    [
        (subject0, predicate0, object0),
        (subject1, predicate1, object1),
        ...
        (subjectN, predicateN, objectN)
     ]

A tiny example
==============

.. code-block:: python

    from rdflib import Graph

    # Create a Graph
    g = Graph()

    # Parse in an RDF file hosted on the Internet
    g.parse("http://www.w3.org/People/Berners-Lee/card")

    # Loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # Check if there is at least one triple in the Graph
        if (subj, pred, obj) not in g:
           raise Exception("It better be!")

    # Print the number of "triples" in the Graph
    print(f"Graph g has {len(g)} statements.")
    # Prints: Graph g has 86 statements.

    # Print out the entire Graph in the RDF Turtle format
    print(g.serialize(format="turtle"))

Here a :class:`~rdflib.graph.Graph` is created and then an RDF file online, Tim Berners-Lee's social network details, is
parsed into that graph. The ``print()`` statement uses the ``len()`` function to count the number of triples in the
graph.

A more extensive example
========================

.. code-block:: python

    from rdflib import Graph, Literal, RDF, URIRef
    # rdflib knows about quite a few popular namespaces, like W3C ontologies, schema.org etc.
    from rdflib.namespace import FOAF , XSD

    # Create a Graph
    g = Graph()

    # Create an RDF URI node to use as the subject for multiple triples
    donna = URIRef("http://example.org/donna")

    # Add triples using store's add() method.
    g.add((donna, RDF.type, FOAF.Person))
    g.add((donna, FOAF.nick, Literal("donna", lang="en")))
    g.add((donna, FOAF.name, Literal("Donna Fales")))
    g.add((donna, FOAF.mbox, URIRef("mailto:donna@example.org")))

    # Add another person
    ed = URIRef("http://example.org/edward")

    # Add triples using store's add() method.
    g.add((ed, RDF.type, FOAF.Person))
    g.add((ed, FOAF.nick, Literal("ed", datatype=XSD.string)))
    g.add((ed, FOAF.name, Literal("Edward Scissorhands")))
    g.add((ed, FOAF.mbox, Literal("e.scissorhands@example.org", datatype=XSD.anyURI)))

    # Iterate over triples in store and print them out.
    print("--- printing raw triples ---")
    for s, p, o in g:
        print((s, p, o))

    # For each foaf:Person in the store, print out their mbox property's value.
    print("--- printing mboxes ---")
    for person in g.subjects(RDF.type, FOAF.Person):
        for mbox in g.objects(person, FOAF.mbox):
            print(mbox)

    # Bind the FOAF namespace to a prefix for more readable output
    g.bind("foaf", FOAF)

    # print all the data in the Notation3 format
    print("--- printing mboxes ---")
    print(g.serialize(format='n3'))


A SPARQL query example
======================

.. code-block:: python

    from rdflib import Graph

    # Create a Graph, pare in Internet data
    g = Graph().parse("http://www.w3.org/People/Berners-Lee/card")

    # Query the data in g using SPARQL
    # This query returns the 'name' of all ``foaf:Person`` instances
    q = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?name
        WHERE {
            ?p rdf:type foaf:Person .

            ?p foaf:name ?name .
        }
    """

    # Apply the query to the graph and iterate through results
    for r in g.query(q):
        print(r["name"])

    # prints: Timothy Berners-Lee



More examples
=============
There are many more :doc:`examples <apidocs/examples>` in the :file:`examples` folder in the source distribution.
