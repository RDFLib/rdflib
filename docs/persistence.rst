.. _persistence: Persistence

===========
Persistence
===========

``rdflib`` provides an abstracted Store API for persistence of RDF and Notation 3. The :class:`~rdflib.graph.Graph` class works with instances of this API (as the first argument to its constructor) for triple-based management of an RDF store including: garbage collection, transaction management, update, pattern matching, removal, length, and database management (:meth:`~rdflib.graph.Graph.open` / :meth:`~rdflib.graph.Graph.close` / :meth:`~rdflib.graph.Graph.destroy`).  

Additional persistence mechanisms can be supported by implementing this API for a different store.

Stores currently supported in rdflib
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Random access memory
* Sleepycat (via Python's ``bsddb`` or ``bsddb3`` packages)

Usage
^^^^^

Store instances can be created with the :meth:`plugin` function:

.. code-block:: python

    from rdflib import plugin
    from rdflib.store import Store
    plugin.get('.. one of the supported Stores ..',Store)(identifier=.. id of conjunctive graph ..)


Additional store plugins in ``rdfextras``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Berkeley DB
* MySQL (not Python 3)
* PostgreSQL
* SQLite
* Zope Object Database (ZODB3) (not Python 3)


Store operations
================

Example code to create a Sleepycat (``bsddb`` or ``bsddb3``) triple store, add some triples, and serialize the resulting graph. Finally, close the graph and
remove the database files that were created.

.. code-block:: python

    import rdflib
    from rdflib.graph import ConjunctiveGraph as Graph
    from rdflib import plugin
    from rdflib.store import Store, NO_STORE, VALID_STORE
    from rdflib.namespace import Namespace
    from rdflib.term import Literal
    from rdflib.term import URIRef
    from tempfile import mkdtemp

    default_graph_uri = "http://rdflib.net/rdfstore"
    configString = "/var/tmp/rdfstore"

    # Get the Sleepycat plugin. 
    store = plugin.get('Sleepycat', Store)('rdfstore')
    
    # Open previously created store, or create it if it doesn't exist yet
    graph = Graph(store="Sleepycat", 
                  identifier = URIRef(default_graph_uri))
    path = mkdtemp()
    rt = graph.open(path, create=False)
    if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
        graph.open(path, create=True)
    else:
        assert rt == VALID_STORE, "The underlying store is corrupt"

    print "Triples in graph before add: ", len(graph)

    # Now we'll add some triples to the graph & commit the changes
    rdflib = Namespace('http://rdflib.net/test/')
    graph.bind("test", "http://rdflib.net/test/")
    
    graph.add((rdflib['pic:1'], rdflib['name'], Literal('Jane & Bob')))
    graph.add((rdflib['pic:2'], rdflib['name'], Literal('Squirrel in Tree')))
    graph.commit()

    print "Triples in graph after add: ", len(graph)

    # display the graph in RDF/XML
    print graph.serialize()
    
    graph.close()
    
    # Clean up the mkdtemp spoor to remove the Sleepycat database files...
    import os
    for f in os.listdir(path): 
        os.unlink(path+'/'+f)
    os.rmdir(path)

The output will appear as follows:

.. code-block:: text

    Triples in graph before add:  0
    Triples in graph after add:  2
    <?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns="http://rdflib.net/test/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >
      <rdf:Description rdf:about="http://rdflib.net/test/pic:1">
        <name>Jane &amp; Bob</name>
      </rdf:Description>
      <rdf:Description rdf:about="http://rdflib.net/test/pic:2">
        <name>Squirrel in Tree</name>
      </rdf:Description>
    </rdf:RDF>
