.. _namespaces_and_bindings: Namespaces and Bindings

=======================
Namespaces and Bindings
=======================

Namespaces
----------
The ``initNs`` argument supplied to :meth:`~rdflib.graph.Graph.parse` is a dictionary of namespaces to be expanded in the query string. In a large program, it is common to use the same ``dict`` for every single query. You might even hack your graph instance so that the ``initNs`` arg is already filled in.

.. warning:: rdfextras.store.SPARQL.query does not support `initNs`. 

In order to use an empty prefix (e.g. ``?a :knows ?b``), use a ``BASE`` directive in the SPARQL query to set a default namespace:

.. code-block:: text

    BASE <http://xmlns.com/foaf/0.1/>

Bindings
--------

As with SQL queries, it is common to run the same SPARQL query many times with only a few terms changing each time. rdflib calls this ``initBindings``:

.. warning:: rdfextras.store.SPARQL.query does not support `initBindings`. 

.. code-block:: python

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    ns = dict(foaf=FOAF)
    drew = URIRef('http://bigasterisk.com/foaf.rdf#drewp')
    for row in g.query("""SELECT ?name 
                          WHERE { ?p foaf:name ?name }""", 
                       initNs=ns, initBindings={'p' : drew}):
        print row

Output:

.. code-block:: python

    (rdflib.Literal('Drew Perttula', language=None, datatype=None),)


