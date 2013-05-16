.. _upgrade2to3: Upgrading from RDFLib version 2.X to 3.X

========================================
Upgrading from RDFLib version 2.X to 3.X
========================================

Introduction
============
This page details the changes required to upgrade from RDFLib 2.X to 3.X. 

Some older Linux distributions still ship 2.4.X. If needed, you can also install 2.4 using easy_install/setup tools.

Version 3.0 reorganised some packages, and moved non-core parts of rdflib to the `rdfextras project <http://code.google.com/p/rdfextras/>`_


Features moved to rdfextras
===========================

  * SPARQL Support is now in rdfextras / rdflib-sparql
  * The RDF Commandline tools are now in rdfextras
 
.. warning:: If you install packages with just distutils - you will need to register the sparql plugins manually - we strongly recommend installing with setuptools or distribute!
  To register the plugins add this somewhere in your program:

  .. code-block:: python 

        rdflib.plugin.register('sparql', rdflib.query.Processor,
                           'rdfextras.sparql.processor', 'Processor')
        rdflib.plugin.register('sparql', rdflib.query.Result,
                           'rdfextras.sparql.query', 'SPARQLQueryResult')


Unstable features that were removed
===================================

 The RDBMS back stores (MySQL/PostgreSQL) were removed, but are in the process of being moved to rdfextras. The Redland, SQLite and ZODB stores were all removed. 

Packages/Classes that were renamed
==================================

Previously all packages and classes had colliding names, i.e. both package and the class was called "Graph"::

    from rdflib.Graph import Graph, ConjunctiveGraph 

Now all packages are lower-case, i.e::

    from rdflib.graph import Graph, ConjunctiveGraph

Most classes you need are available from the top level rdflib package::

    from rdflib import Graph, URIRef, BNode, Literal

Namespace classes for RDF, RDFS, OWL are now directly in the rdflib package, i.e. in 2.4::

    from rdflib.RDF import RDFNS as RDF

in 3.0::

    from rdflib import RDF

