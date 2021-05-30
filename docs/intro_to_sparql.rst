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
SELECT queries, iterating over this returns
:class:`rdflib.query.ResultRow` instances, each containing a set of
variable bindings. For CONSTRUCT/DESCRIBE queries, iterating over the
result object yields triples. For ASK queries, the single Boolean 
answer is obtained by iterating over the result object or by 
evaluating the result object in a Boolean context 
(i.e. ``bool(result)``).

Consider the example...

.. code-block:: python

    import rdflib
    g = rdflib.Graph()
    g.parse("http://danbri.org/foaf.rdf#")

    knows_query = """
    SELECT DISTINCT ?aname ?bname
    WHERE {
        ?a foaf:knows ?b .
        ?a foaf:name ?aname .
        ?b foaf:name ?bname .
    }"""

    for row in g.query(knows_query):
        print("%s knows %s" % row)

The results are tuples of values in the same order as your SELECT
arguments.  The values can be accessed individually by variable
name, either as attributes (``row.b``) or as items (``row["b"]``).

.. code-block:: text

    Dan Brickley knows Tim Berners-Lee
    Dan Brickley knows Dean Jackson
    Dan Brickley knows Mischa Tuffield
    Dan Brickley knows Ludovic Hirlimann
    Dan Brickley knows Libby Miller
    ...

As an alternative to using ``PREFIX`` in the SPARQL query, namespace
bindings can be passed in with the ``initNs`` kwarg (see
:doc:`namespaces_and_bindings`):

.. code-block:: python

    import rdflib 
    from rdflib import FOAF
    g = rdflib.Graph()
    g.parse("http://danbri.org/foaf.rdf#")
 
    result = g.query(knows_query, initNs={ 'foaf': FOAF })
 
    for row in result:
        print(f"{row.aname} knows {row['bname']}")
 
Variables can also be pre-bound, using ``initBindings`` kwarg can be
used to pass in a ``dict`` of initial bindings, this is particularly
useful for prepared queries, as described below.

Query a Remote Service
^^^^^^^^^^^^^^^^^^^^^^

The SERVICE keyword of SPARQL 1.1 can send a query to a remote SPARQL endpoint.

.. code-block:: python

    import rdflib

    g = rdflib.Graph()
    qres = g.query('''
    SELECT ?s
    WHERE {
      SERVICE <http://dbpedia.org/sparql> {
        ?s <http://purl.org/linguistics/gold/hypernym> <http://dbpedia.org/resource/Leveller> .
      }
    } LIMIT 3''')
    for row in qres:
        print(row.s)

This example sends a query to `DBPedia
<https://dbpedia.org/>`_'s SPARQL endpoint service so that it can run the query and then send back the result:

.. code-block:: text

    http://dbpedia.org/resource/Elizabeth_Lilburne
    http://dbpedia.org/resource/Thomas_Prince_(Leveller)
    http://dbpedia.org/resource/John_Lilburne

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
