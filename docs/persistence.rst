.. _persistence:

===========
Persistence
===========


``rdflib`` provides an abstracted Store API for persistence of RDF and Notation 3. The :class:`~rdflib.graph.Graph` class works with instances of this API (as the first argument to its constructor) for triple-based management of an RDF store including: garbage collection, transaction management, update, pattern matching, removal, length, and database management (:meth:`~rdflib.graph.Graph.open` / :meth:`~rdflib.graph.Graph.close` / :meth:`~rdflib.graph.Graph.destroy`).  

Additional persistence mechanisms can be supported by implementing this API for a different store.

Currently supported stores
--------------------------

* Random access memory
* Sleepycat (via Python's ``bsddb`` or ``bsddb3`` packages)

Usage
-----

Store instances can be created with the :meth:`plugin` function:

.. code-block:: python

    from rdflib import plugin
    from rdflib.store import Store
    plugin.get('.. one of the supported Stores ..',Store)(identifier=.. id of conjunctive graph ..)


Additional store plugins in ``rdfextras``
-----------------------------------------

* Berkeley DB
* MySQL
* PostgreSQL
* Redland RDF Application Framework
* SQLite
* Zope Object Database (ZODB3)

