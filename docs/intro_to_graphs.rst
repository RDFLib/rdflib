.. _rdflib_graph: Navigating Graphs

=================
Navigating Graphs
=================

An RDF Graph is a set of RDF triples, and we try to mirror exactly this in RDFLib. The Python
:meth:`~rdflib.graph.Graph` tries to emulate a container type.

Graphs as Iterators
-------------------

RDFLib graphs override :meth:`~rdflib.graph.Graph.__iter__` in order to support iteration over the contained triples:

.. code-block:: python

    for s, p, o in someGraph:
        if not (s, p, o) in someGraph:
            raise Exception("Iterator / Container Protocols are Broken!!")

This loop iterates through all the subjects(s), predicates (p) & objects (o) in ``someGraph``.

Contains check
--------------

Graphs implement :meth:`~rdflib.graph.Graph.__contains__`, so you can check if a triple is in a graph with a
``triple in graph`` syntax:

.. code-block:: python

    from rdflib import URIRef
    from rdflib.namespace import RDF

    bob = URIRef("http://example.org/people/bob")
    if (bob, RDF.type, FOAF.Person) in graph:
        print("This graph knows that Bob is a person!")
	 
Note that this triple does not have to be completely bound:

.. code-block:: python

    if (bob, None, None) in graph:
        print("This graph contains triples about Bob!")

.. _graph-setops:

Set Operations on RDFLib Graphs 
-------------------------------

Graphs override several pythons operators: :meth:`~rdflib.graph.Graph.__iadd__`, :meth:`~rdflib.graph.Graph.__isub__`,
etc. This supports addition, subtraction and other set-operations on Graphs:

============ =============================================================
operation    effect
============ =============================================================
``G1 + G2``  return new graph with union (triples on both)
``G1 += G2`` in place union / addition
``G1 - G2``  return new graph with difference (triples in G1, not in G2)
``G1 -= G2`` in place difference / subtraction
``G1 & G2``  intersection (triples in both graphs)
``G1 ^ G2``  xor (triples in either G1 or G2, but not in both)
============ =============================================================

.. warning:: Set-operations on graphs assume Blank Nodes are shared between graphs. This may or may not be what you want. See :doc:`merging` for details.

Basic Triple Matching
---------------------

Instead of iterating through all triples, RDFLib graphs support basic triple pattern matching with a
:meth:`~rdflib.graph.Graph.triples` function. This function is a generator of triples that match a pattern given by
arguments, i.e. arguments restrict the triples that are returned. Terms that are :data:`None` are treated as a wildcard.
For example:

.. code-block:: python

    g.load("some_foaf.ttl")
    # find all subjects (s) of type (rdf:type) person (foaf:Person)
    for s, p, o in g.triples((None, RDF.type, FOAF.Person)):
        print(f"{s} is a person")

    # find all subjects of any type
    for s, p, o in g.triples((None,  RDF.type, None)):
        print(f"{s} is a {o}")

    # create a graph
    bobgraph = Graph()
    # add all triples with subject 'bob'
    bobgraph += g.triples((bob, None, None))

If you are not interested in whole triples, you can get only the bits you want with the methods
:meth:`~rdflib.graph.Graph.objects`, :meth:`~rdflib.graph.Graph.subjects`, :meth:`~rdflib.graph.Graph.predicates`,
:meth:`~rdflib.graph.Graph.predicate_objects`, etc. Each take parameters for the components of the triple to constraint:

.. code-block:: python

    for person in g.subjects(RDF.type, FOAF.Person):
        print("{} is a person".format(person))

Finally, for some properties, only one value per resource makes sense (i.e they are *functional properties*, or have a
max-cardinality of 1). The :meth:`~rdflib.graph.Graph.value` method is useful for this, as it returns just a single
node, not a generator:

.. code-block:: python

    # get any name of bob
    name = g.value(bob, FOAF.name)
    # get the one person that knows bob and raise an exception if more are found
    mbox = g.value(predicate = FOAF.name, object=bob, any=False)


:class:`~rdflib.graph.Graph` methods for accessing triples
-----------------------------------------------------------

Here is a list of all convenience methods for querying Graphs:

.. automethod:: rdflib.graph.Graph.triples
    :noindex:
.. automethod:: rdflib.graph.Graph.value
    :noindex:
.. automethod:: rdflib.graph.Graph.subjects
    :noindex:
.. automethod:: rdflib.graph.Graph.objects
    :noindex:
.. automethod:: rdflib.graph.Graph.predicates
    :noindex:
.. automethod:: rdflib.graph.Graph.subject_objects
    :noindex:
.. automethod:: rdflib.graph.Graph.subject_predicates
    :noindex:
.. automethod:: rdflib.graph.Graph.predicate_objects
    :noindex:
