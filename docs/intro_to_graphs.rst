.. _rdflib_graph: Navigating Graphs

=================
Navigating Graphs
=================

An RDF Graph is a set of RDF triples, and we try to mirror exactly this in RDFLib, and the graph tries to emulate a container type. 

Graphs as Iterators
-------------------

RDFLib graphs override :meth:`~rdflib.graph.Graph.__iter__` in order to support iteration over the contained triples:

.. code-block:: python

    for subject,predicate,obj_ in someGraph:
       assert (subject,predicate,obj_) in someGraph, "Iterator / Container Protocols are Broken!!"

Set Operations on RDFLib Graphs 
-------------------------------

:meth:`~rdflib.graph.Graph.__iadd__` and :meth:`~rdflib.graph.Graph.__isub__` are overridden to support adding and subtracting Graphs to/from each other (in place):

* G1 += G1
* G2 -= G2

.. warning: If you are using blank-nodes set-operations on graphs may or may not do what you want, 

Basic Triple Matching
---------------------

RDFLib graphs support basic triple pattern matching with a :meth:`~rdflib.graph.Graph.triples` function.

.. automethod:: rdflib.graph.Graph.triples
    :noindex:

This function is a generator of triples that match the pattern given by the arguments.  The arguments of these are RDF terms that restrict the triples that are returned.  Terms that are :data:`None` are treated as a wildcard.





:class:`~rdflib.graph.Graph` methods for accessing triples
-----------------------------------------------------------

.. automethod:: rdflib.graph.Graph.add
    :noindex:
.. automethod:: rdflib.graph.Graph.set
    :noindex:
.. automethod:: rdflib.graph.Graph.label
    :noindex:
.. automethod:: rdflib.graph.Graph.preferredLabel
    :noindex:
.. automethod:: rdflib.graph.Graph.remove
    :noindex:
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





