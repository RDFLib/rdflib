.. _persistence: Persistence

===========
Persistence
===========

RDFLib provides an :class:`abstracted Store API <rdflib.store.Store>`
for persistence of RDF and Notation 3. The
:class:`~rdflib.graph.Graph` class works with instances of this API
(as the first argument to its constructor) for triple-based management
of an RDF store including: garbage collection, transaction management,
update, pattern matching, removal, length, and database management
(:meth:`~rdflib.graph.Graph.open` / :meth:`~rdflib.graph.Graph.close`
/ :meth:`~rdflib.graph.Graph.destroy`).

Additional persistence mechanisms can be supported by implementing
this API for a different store.

Stores currently shipped with core RDFLib
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :class:`Memory <rdflib.plugins.memory.IOMemory>` (not persistent!)
* :class:`~rdflib.plugins.sleepycat.Sleepycat` (on disk persistence via Python's :ref:`bsddb` or :ref:`bsddb3` packages)
* :class:`~rdflib.plugins.stores.sparqlstore.SPARQLStore` - a read-only wrapper around a remote SPARQL Query endpoint. 
* :class:`~rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore` - a read-write wrapper around a remote SPARQL query/update endpoint pair. 

Usage
^^^^^

Most cases passing the name of the store to the Graph constructor is enough: 

.. code-block:: python

    from rdflib import Graph

    graph = Graph(store='Sleepycat')


Most store offering on-disk persistence will need to be opened before reading or writing :

.. code-block:: python

   graph = Graph('Sleepycat')

   # first time create the store:
   graph.open('/home/user/data/myRDFLibStore', create = True) 
   
   # work with the graph: 
   graph.add( mytriples ) 

   # when done!
   graph.close() 



When done, :meth:`~rdflib.graph.Graph.close` must be called to free the resources associated with the store. 
	

Additional store plugins
^^^^^^^^^^^^^^^^^^^^^^^^

More store implementations are available in RDFLib extension projects: 

 * `rdflib-sqlalchemy <https://github.com/RDFLib/rdflib-sqlalchemy>`_, which supports stored on a wide-variety of RDBMs backends, 
 * `rdflib-leveldb <https://github.com/RDFLib/rdflib-leveldb>`_ - a store on to of Google's `LevelDB <https://code.google.com/p/leveldb/>`_ key-value store. 
 * `rdflib-kyotocabinet <https://github.com/RDFLib/rdflib-kyotocabinet>`_ - a store on to of the `Kyoto Cabinet <http://fallabs.com/kyotocabinet/>`_ key-value store. 

Example
^^^^^^^

* :mod:`examples.sleepycat_example` contains an example for using a Sleepycat store. 
* :mod:`examples.sparqlstore_example` contains an example for using a SPARQLStore. 
