.. _intro_to_using_sparql:

====================
Querying with SPARQL
====================


Run a Query
^^^^^^^^^^^

The RDFLib comes with an implementation of the `SPARQL 1.1 Query
<http://www.w3.org/TR/sparql11-query/>`_ and `SPARQL 1.1 Update
<http://www.w3.org/TR/sparql11-update/>`_ query languages.

Queries can be evaluated against a graph with the
:meth:`rdflib.graph.Graph.query` method, and updates with
:meth:`rdflib.graph.Graph.update`.

The query method returns a :class:`rdflib.query.Result` instance. For
SELECT queries, iterating over this returns
:class:`rdflib.query.ResultRow` instances, each containing a set of
variable bindings. For ``CONSTRUCT``/``DESCRIBE`` queries, iterating over the
result object gives the triples. For ``ASK`` queries, iterating will yield
the single boolean answer, or evaluating the result object in a
boolean-context (i.e. ``bool(result)``)

For example...

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
    
    qres = g.query(knows_query)
    for row in qres:
        print(f"{row.aname} knows {row.bname}")



The results are tuples of values in the same order as your ``SELECT``
arguments. Alternatively, the values can be accessed by variable
name, either as attributes, or as items, e.g. ``row.b`` and ``row["b"]`` are
equivalent. The above, given the appropriate data, would print something like:

.. code-block:: text

    Timothy Berners-Lee knows Edd Dumbill
    Timothy Berners-Lee knows Jennifer Golbeck
    Timothy Berners-Lee knows Nicholas Gibbins
    ...

As an alternative to using ``SPARQL``\s ``PREFIX``, namespace
bindings can be passed in with the ``initNs`` kwarg, see
:doc:`namespaces_and_bindings`.

Variables can also be pre-bound, using the ``initBindings`` kwarg which can
pass in a ``dict`` of initial bindings. This is particularly
useful for prepared queries, as described below.

Update Queries
^^^^^^^^^^^^^^

Update queries are performed just like reading queries but using the :meth:`rdflib.graph.Graph.update` method. An
example:

.. code-block:: python

    from rdflib import Graph

    # Create a Graph, add in some test data
    g = Graph()
    g.parse(
        data="""
            <x:> a <c:> .
            <y:> a <c:> .
        """,
        format="turtle"
    )

    # Select all the things (s) that are of type (rdf:type) c:
    qres = g.query("""SELECT ?s WHERE { ?s a <c:> }""")

    for row in qres:
        print(f"{row.s}")
    # prints:
    # x:
    # y:

    # Add in a new triple using SPATQL UPDATE
    g.update("""INSERT DATA { <z:> a <c:> }""")

    # Select all the things (s) that are of type (rdf:type) c:
    qres = g.query("""SELECT ?s WHERE { ?s a <c:> }""")

    print("After update:")
    for row in qres:
        print(f"{row.s}")
    # prints:
    # x:
    # y:
    # z:

    # Change type of <y:> from <c:> to <d:>
    g.update("""
             DELETE { <y:> a <c:> }
             INSERT { <y:> a <d:> }
             WHERE { <y:> a <c:> }
             """)
    print("After second update:")
    qres = g.query("""SELECT ?s ?o WHERE { ?s a ?o }""")
    for row in qres:
        print(f"{row.s} a {row.o}")
    # prints:
    # x: a c:
    # z: a c:
    # y: a d:



Querying a Remote Service
^^^^^^^^^^^^^^^^^^^^^^^^^

The ``SERVICE`` keyword of SPARQL 1.1 can send a query to a remote SPARQL endpoint.

.. code-block:: python

    import rdflib

    g = rdflib.Graph()
    qres = g.query(
        """
        SELECT ?s
        WHERE {
          SERVICE <http://dbpedia.org/sparql> {
            ?s a ?o .
          }
        }
        LIMIT 3
        """
    )

    for row in qres:
        print(row.s)



This example sends a query to `DBPedia <https://dbpedia.org/>`_'s SPARQL endpoint service so that it can run the query
and then send back the result:

.. code-block:: text

    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.openlinksw.com/schemas/virtcxml#FacetCategoryPattern>
    <http://www.w3.org/2001/XMLSchema#anyURI> <http://www.w3.org/2000/01/rdf-schema#Datatype>
    <http://www.w3.org/2001/XMLSchema#anyURI> <http://www.w3.org/2000/01/rdf-schema#Datatype>

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
        "SELECT ?s WHERE { ?person foaf:knows ?s .}",
        initNs = { "foaf": FOAF }
    )

    g = rdflib.Graph()
    g.load("foaf.rdf")

    tim = rdflib.URIRef("http://www.w3.org/People/Berners-Lee/card#i")

    for row in g.query(q, initBindings={'person': tim}):
        print(row)


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
