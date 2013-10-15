.. _gettingstarted:

===============================
Getting started with RDFLib
===============================

Installation
============

RDFLib is open source and is maintained in a 
`GitHub <http://github.com/RDFLib/rdflib/>`_ repository. RDFLib releases, current and previous 
are listed on `PyPi <http://pypi.python.org/pypi/rdflib/>`_

The best way to install RDFLib is to use ``easy_install`` or ``pip``:

.. code-block :: bash

    $ easy_install rdflib

Support is available through the rdflib-dev group:

    http://groups.google.com/group/rdflib-dev

and on the IRC channel `#rdflib <irc://irc.freenode.net/swig>`_ on the freenode.net server

The primary interface that RDFLib exposes for working with RDF is a
:class:`~rdflib.graph.Graph`. The package uses various Python idioms
that offer an appropriate way to introduce RDF to a Python programmer
who hasn't worked with RDF before.

RDFLib graphs are not sorted containers; they have ordinary ``set``
operations (e.g. :meth:`~rdflib.Graph.add` to add a triple) plus
methods that search triples and return them in arbitrary order.

RDFLib graphs also redefine certain built-in Python methods in order
to behave in a predictable way; they `emulate container types
<http://docs.python.org/release/2.5.2/ref/sequence-types.html>`_ and
are best thought of as a set of 3-item triples:

.. code-block:: text

    [
        (subject,  predicate,  object),
        (subject1, predicate1, object1),
        ... 
        (subjectN, predicateN, objectN)
     ]

A tiny usage example:

.. code-block:: python

    import rdflib

    g = rdflib.Graph()
    result = g.parse("http://www.w3.org/People/Berners-Lee/card")

    print("graph has %s statements." % len(g))
    # prints graph has 79 statements.

    for subj, pred, obj in g:
       if (subj, pred, obj) not in g:
           raise Exception("It better be!")

    s = g.serialize(format='n3')

A more extensive example:


.. code-block:: python

    from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
    from rdflib.namespace import DC, FOAF

    g = Graph()

    # Create an identifier to use as the subject for Donna.
    donna = BNode()

    # Add triples using store's add method.
    g.add( (donna, RDF.type, FOAF.Person) )
    g.add( (donna, FOAF.nick, Literal("donna", lang="foo")) )
    g.add( (donna, FOAF.name, Literal("Donna Fales")) )
    g.add( (donna, FOAF.mbox, URIRef("mailto:donna@example.org")) )

    # Iterate over triples in store and print them out.
    print("--- printing raw triples ---")
    for s, p, o in g:
        print((s, p, o))

    # For each foaf:Person in the store print out its mbox property.
    print("--- printing mboxes ---")
    for person in g.subjects(RDF.type, FOAF.Person):
        for mbox in g.objects(person, FOAF.mbox):
            print(mbox)

    # Bind a few prefix, namespace pairs for more readable output
    g.bind("dc", DC)
    g.bind("foaf", FOAF)
	
    print( g.serialize(format='n3') )
			
Many more :doc:`examples <apidocs/examples>` can be found in the :file:`examples` folder in the source distribution.
