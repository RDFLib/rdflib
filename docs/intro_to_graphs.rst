.. _intro_to_parsing_graphs: Parsing RDF

==============================================
Introduction to parsing RDF into rdflib graphs
==============================================

Reading an NT file
-------------------

RDF data has various syntaxes (``xml``, ``n3``, ``ntriples``, ``trix``, etc) that you might want to read. The simplest format is ``ntriples``. Create the file :file:`demo.nt` in the current directory with these two lines:

.. code-block:: n3

    <http://bigasterisk.com/foaf.rdf#drewp> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .
    <http://bigasterisk.com/foaf.rdf#drewp> <http://example.com/says> "Hello world" .

In an interactive python interpreter, try this:

.. code-block:: pycon

    >>> from rdflib.graph import Graph
    >>> g = Graph()
    >>> g.parse("demo.nt", format="nt")
    <Graph identifier=HCbubHJy0 (<class 'rdflib.graph.Graph'>)>
    >>> len(g)
    2
    >>> import pprint
    >>> for stmt in g:
    ...     pprint.pprint(stmt)
    ... 
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://example.com/says'),
     rdflib.term.Literal(u'Hello world'))
    (rdflib.term.URIRef('http://bigasterisk.com/foaf.rdf#drewp'),
     rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
     rdflib.term.URIRef('http://xmlns.com/foaf/0.1/Person'))

The final lines show how ``rdflib`` represents the two statements in the file. The statements themselves are just length-3 tuples; and the subjects, predicates, and objects are all rdflib types.

Reading remote graphs
---------------------

Reading graphs from the net is just as easy:

.. code-block:: pycon

    >>> g.parse("http://bigasterisk.com/foaf.rdf")
    >>> len(g)
    42

The format defaults to ``xml``, which is the common format for .rdf files you'll find on the net.

Graphs as Iterators
-------------------

RDFLib graphs also override :meth:`__iter__` in order to support iteration over the contained triples:

.. code-block:: python

    for subject,predicate,obj_ in someGraph:
       assert (subject,predicate,obj_) in someGraph, "Iterator / Container Protocols are Broken!!"

Set Operations on RDFLib Graphs 
-------------------------------

:meth:`__iadd__` and :meth:`__isub__` are overridden to support adding and subtracting Graphs to/from each other (in place):

* G1 += G1
* G2 -= G2

Basic Triple Matching
---------------------

RDFLib graphs support basic triple pattern matching with a :meth:`triples` function.

.. automethod:: rdflib.graph.Graph.triples
    :noindex:

This function is a generator of triples that match the pattern given by the arguments.  The arguments of these are RDF terms that restrict the triples that are returned.  Terms that are :data:`None` are treated as a wildcard.

Managing Triples
----------------

Adding Triples
^^^^^^^^^^^^^^
Triples can be added either of two ways:

Triples can be added with with the :meth:`parse` function.

.. automethod:: rdflib.graph.Graph.parse
    :noindex:

The first argument can be a *source* of many kinds, but the most common is the serialization (in various formats: RDF/XML, Notation 3, NTriples of an RDF graph as a string.  The ``format`` parameter is one of ``n3``, ``xml``, or ``ntriples``.  ``publicID`` is the name of the graph into which the RDF serialization will be parsed.

Triples can also be added with the :meth:`add` function: 

.. automethod:: rdflib.graph.Graph.add
    :noindex:

Removing Triples
^^^^^^^^^^^^^^^^

Similarly, triples can be removed by a call to :meth:`remove`:

.. automethod:: rdflib.graph.Graph.remove
    :noindex:



.. module:: rdflib.graph

:class:`~rdflib.graph.Graph` methods for accessing triples
-----------------------------------------------------------

.. automethod:: rdflib.graph.Graph.add
.. automethod:: rdflib.graph.Graph.set
.. automethod:: rdflib.graph.Graph.label
.. automethod:: rdflib.graph.Graph.remove
.. automethod:: rdflib.graph.Graph.triples
.. automethod:: rdflib.graph.Graph.value
.. automethod:: rdflib.graph.Graph.subjects
.. automethod:: rdflib.graph.Graph.objects
.. automethod:: rdflib.graph.Graph.predicates
.. automethod:: rdflib.graph.Graph.subject_objects
.. automethod:: rdflib.graph.Graph.subject_predicates
.. automethod:: rdflib.graph.Graph.predicate_objects


Full documentation
------------------

.. toctree::
   :maxdepth: 2

   using_graphs

