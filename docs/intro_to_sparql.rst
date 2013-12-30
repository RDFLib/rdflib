.. _intro_to_using_sparql:

====================
Querying with SPARQL
====================


Run a Query
^^^^^^^^^^^

The RDFLib comes with an implementation of the `SPARQL 1.1 Query
<http://www.w3.org/TR/sparql11-query/>`_ and `SPARQL 1.1 Update
<http://www.w3.org/TR/sparql11-update/>`_ languages.

Queries can be evaluated against a graph with the
:meth:`rdflib.graph.Graph.query` method, and updates with
:meth:`rdflib.graph.Graph.update`.

The query method returns a :class:`rdflib.query.Result` instance. For
SELECT queries, iterating over this return
:class:`rdflib.query.ResultRow` instances, each containing a set of
variable bindings. For CONSTRUCT/DESCRIBE queries, iterating over the
result object gives the triples. For ASK queries, iterating will yield
the single boolean answer, or evaluating the result object in a
boolean-context (i.e. ``bool(result)``)

Continuing the example...

.. code-block:: python

    import rdflib

    g = rdflib.Graph()

    # ... add some triples to g somehow ...
    g.parse("some_foaf_file.rdf")

    qres = g.query(
        """SELECT DISTINCT ?aname ?bname
           WHERE {
              ?a foaf:knows ?b .
              ?a foaf:name ?aname .
              ?b foaf:name ?bname .
           }""")

    for row in qres:
        print("%s knows %s" % row)

The results are tuples of values in the same order as your SELECT
arguments.  Alternatively, the values can be accessed by variable
name, either as attributes, or as items: ``row.b`` and ``row["b"]`` is
equivalent.

.. code-block:: text

    Timothy Berners-Lee knows Edd Dumbill
    Timothy Berners-Lee knows Jennifer Golbeck
    Timothy Berners-Lee knows Nicholas Gibbins
    Timothy Berners-Lee knows Nigel Shadbolt
    Dan Brickley knows binzac
    Timothy Berners-Lee knows Eric Miller
    Drew Perttula knows David McClosky
    Timothy Berners-Lee knows Dan Connolly
    ...

As an alternative to using ``PREFIX`` in the SPARQL query, namespace
bindings can be passed in with the ``initNs`` kwarg, see
:doc:`namespace_and_bindings`.

Variables can also be pre-bound, using ``initBindings`` kwarg can be
used to pass in a ``dict`` of initial bindings, this is particularly
useful for prepared queries, as described below.

Prepared Queries
^^^^^^^^^^^^^^^^

RDFLib lets you *prepare* queries before execution, this saves
re-parsing and translating the query into SPARQL Algebra each time.

The method :meth:`rdflib.plugins.sparql.prepareQuery` takes a query as
a string and will return a :class:`rdflib.plugins.sparql.sparql.Query`
object. This can then be passed to the
:meth:`rdflib.graph.Graph.query` method.

The ``initBindings`` kwarg can be used to pass in a ``dict`` of
initial bindings:

.. code-block:: python

	q = prepareQuery(
		'SELECT ?s WHERE { ?person foaf:knows ?s .}',
		initNs = { "foaf": FOAF })

	g = rdflib.Graph()
	g.load("foaf.rdf")

	tim = rdflib.URIRef("http://www.w3.org/People/Berners-Lee/card#i")

	for row in g.query(q, initBindings={'person': tim}):
		print row


Custom Evaluation Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For experts, it is possible to override how bits of SPARQL algebra are
evaluated. By using the `setuptools entry-point
<http://pythonhosted.org/distribute/setuptools.html#dynamic-discovery-of-services-and-plugins>`_
``rdf.plugins.sparqleval``, or simply adding to an entry to
:data:`rdflib.plugins.sparql.CUSTOM_EVALS`, a custom function can be
registered. The function will be called for each algebra component and
may raise ``NotImplementedError`` to indicate that this part should be
handled by the default implementation.

See :file:`examples/custom_eval.py`
