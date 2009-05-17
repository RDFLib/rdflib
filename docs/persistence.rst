.. _persistence:

===========
Persistence
===========


RDFLib provides an abstracted Store API for persistence of RDF and Notation 3. The :class:`Graph` class works with instances of this API (as the first argument to its constructor) for triple-based management of an RDF store including: garbage collection, transaction management, update, pattern matching, removal, length, and database management (:meth:`open` / :meth:`close` / :meth:`destroy`) .  Additional persistence mechanisms can be supported by implementing this API for a different store.  

Currently supported databases:

* MySQL 
* SQLite
* Berkeley DB
* Zope Object Database
* Random access memory
* Redland RDF Application Framework

Store instances can be created with the :meth:`plugin` function:

.. code-block:: python

    from rdflib import plugin
    from rdflib.store import Store
    plugin.get('.. one of the supported Stores ..',Store)(identifier=.. id of conjunctive graph ..)

