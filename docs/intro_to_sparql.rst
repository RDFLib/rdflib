.. _intro_to_using_sparql: Querying with SPARQL

=====================================================
Introduction to using SPARQL to query an rdflib graph
=====================================================

Create an Rdflib Graph
^^^^^^^^^^^^^^^^^^^^^^

You might parse some files into a new graph (see `Introduction to parsing <intro_to_parsing_graphs>`_) or open an on-disk rdflib store.

.. code-block:: python

    from rdflib.graph import Graph
    g = Graph()
    g.parse("http://bigasterisk.com/foaf.rdf")
    g.parse("http://www.w3.org/People/Berners-Lee/card.rdf")

LiveJournal produces FOAF data for their users, but they seem to use ``foaf:member_name`` for a person's full name. For this demo, I made ``foaf:name`` act as a synonym for ``foaf:member_name`` (a poor man's one-way ``owl:equivalentProperty``):

.. code-block:: python

    from rdflib.namespace import Namespace
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    g.parse("http://danbri.livejournal.com/data/foaf") 
    [g.add((s, FOAF['name'], n)) 
        for s,_,n in g.triples((None, FOAF['member_name'], None))]

Run a Query
^^^^^^^^^^^

The ``rdflib`` package concentrates on providing the core RDF types and interfaces for working with RDF. As indicated in the introduction, the package defines a plugin interface (for parsers, stores, and serializers) that other packages can use to implement parsers, stores, and serializers that will plug into the ``rdflib`` package.

In order to perform SPARQL queries, you need to install the companion ``rdfextras`` package which includes a SPARQL plugin implementation:

.. code-block:: bash
    
    $ easy_install rdfextras

In order to use the SPARQL plugin in your code, the plugin must first be registered. This binds the the imported SPARQL query processor implementation to the :meth:`rdflib.graph.Graph.query` method, which can then be passed a SPARQL query (a string). When called, the :meth:`~rdflib.graph.Graph.query` method returns a SPARQLQuery object whose ``result`` attribute is a list of results.

Continuing the example...

.. code-block:: python

    import rdflib
    from rdflib import plugin

    plugin.register(
        'sparql', rdflib.query.Processor,
        'rdfextras.sparql.processor', 'Processor')
    plugin.register(
        'sparql', rdflib.query.Result,
        'rdfextras.sparql.query', 'SPARQLQueryResult')

    qres = g.query(
        """SELECT DISTINCT ?aname ?bname
           WHERE {
              ?a foaf:knows ?b .
              ?a foaf:name ?aname .
              ?b foaf:name ?bname .
           }""",
        initNs=dict(
            foaf=Namespace("http://xmlns.com/foaf/0.1/")))
    
    for row in qres.result:
        print("%s knows %s" % row)

The results are tuples of values in the same order as your SELECT arguments.

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
