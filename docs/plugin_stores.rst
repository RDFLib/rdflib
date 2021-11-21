.. _plugin_stores: Plugin stores

=============
Plugin stores
=============
 
Built In
--------

The following Stores are contained within the rdflib core package:

================= ============================================================
Name              Class                                                       
================= ============================================================
Auditable         :class:`~rdflib.plugins.stores.auditable.AuditableStore`
Concurrent        :class:`~rdflib.plugins.stores.concurrent.ConcurrentStore`
SimpleMemory      :class:`~rdflib.plugins.stores.memory.SimpleMemory`
Memory            :class:`~rdflib.plugins.stores.memory.Memory`
SPARQLStore       :class:`~rdflib.plugins.stores.sparqlstore.SPARQLStore`
SPARQLUpdateStore :class:`~rdflib.plugins.stores.sparqlstore.SPARQLUpdateStore`
BerkeleyDB        :class:`~rdflib.plugins.stores.berkeleydb.BerkeleyDB`
default           :class:`~rdflib.plugins.stores.memory.Memory`
================= ============================================================

External
--------

The following Stores are defined externally to rdflib's core package, so look to their documentation elsewhere for 
specific details of use.

================= ==================================================== =============================================================================================
Name              Repository                                           Notes
================= ==================================================== =============================================================================================
SQLAlchemy        `<https://github.com/RDFLib/rdflib-sqlalchemy>`_     An SQLAlchemy-backed, formula-aware RDFLib Store. Tested dialects are: SQLite, MySQL & PostgreSQL
leveldb           `<https://github.com/RDFLib/rdflib-leveldb>`_        An adaptation of RDFLib BerkeleyDB Store’s key-value approach, using LevelDB as a back-end
Kyoto Cabinet     `<https://github.com/RDFLib/rdflib-kyotocabinet>`_   An adaptation of RDFLib BerkeleyDB Store’s key-value approach, using Kyoto Cabinet as a back-end
HDT               `<https://github.com/RDFLib/rdflib-hdt>`_            A Store back-end for rdflib to allow for reading and querying `HDT <https://www.rdfhdt.org/>`_ documents
Oxigraph          `<https://github.com/oxigraph/oxrdflib>`_            Works with the `Pyoxigraph <https://oxigraph.org/pyoxigraph>`_ Python graph database library
================= ==================================================== =============================================================================================

_If you have, or know of a Store implementation and would like it listed here, please submit a Pull Request!_

Use
---

You can use these stores like this:

.. code-block:: python

    from rdflib import Graph
    
    # use the default memory Store
    graph = Graph()
    
    # use the BerkeleyDB Store
    graph = Graph(store="BerkeleyDB")


In some cases, you must explicitly _open_ and _close_ a store, for example:

.. code-block:: python

    from rdflib import Graph
    
    # use the BerkeleyDB Store
    graph = Graph(store="BerkeleyDB")
    graph.open("/some/folder/location")
    # do things ...
    graph.close()
    
