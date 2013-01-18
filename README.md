RDFLib
======

RDFLib is a Python library for working with RDF, a simple yet 
powerful language for representing information as graphs.

RDFLib may be installed with setuptools (easy_install) or pip::

    $ easy_install rdflib
or

    $ pip install rdflib

Getting Started
---------------

RDFLib aims to be a pythonic RDF API, a Graph is a python collection
of RDF Subject,Predicate,Object Triples: 

```python
import rdflib
g=rdflib.Graph()
g.load('http://dbpedia.org/resource/Semantic_Web')

for s,p,o in g: 
  print s,p,o
```

The components of the triples are URIs (resources) or Literals
(values), URIs are grouped together by *namespace*, common namespaces are 
included in RDFLib: 

```python

semweb=rdflib.URIRef('http://dbpedia.org/resource/Semantic_Web')
type=g.value(semweb, rdflib.RDFS.label) 
```

Where `rdflib.RDFS` is the RDFS Namespace, `graph.value` returns an
object of the triple-pattern given (or an arbitrary one if more
exist). New Namespaces can also be defined:

```python

dbpedia=Namespace('http://dbpedia.org/ontology/')

abstracts=list(x for x in g.objects(semweb, dbpedia['abstract']) if x.language=='en')
```

See also *./examples*


Features 
--------

The library contains parsers and serializers for RDF/XML, N3,
NTriples, N-Quads, Turtle, TriX, RDFa and Microdata.

The library presents a Graph interface which can be backed by
any one of a number of Store implementations. 

This core RDFLib package includes store implementations for 
in memory storage and persistent storage on top of the Berkeley DB. 

RDFLib is open source and is maintained on [GitHub](http://github.com/RDFLib/rdflib/). RDFLib releases, current and previous 
are listed on [PyPi](pypi.python.org/pypi/rdflib/)

RDFLib has a plugin-architecture for store-implementation, as well as parsers/serializers, several other projects exist which extend RDFLib features:

 * [rdfextras](https://github.com/RDFLib/rdfextras) - for SPARQL Support
 * [rdflib-json](https://github.com/RDFLib/rdflib-jsonld) - Serializer and parser for [json-ld](http://json-ld.org)
 * [rdflib-sparqlstore](https://github.com/RDFLib/rdflib-sparqlstore) - a store implementation on top of a SPARQL endpoint accessed over HTTP
 * [rdflib-mysql](https://github.com/RDFLib/rdflib-mysql) - a store implementation of top of MySQL


Support
-------

More information is available on the project webpage:

https://github.com/RDFLib/rdflib/

Continuous integration status details available from travis.ci:

[![Build Status](https://travis-ci.org/RDFLib/rdflib.png?branch=master)](https://travis-ci.org/RDFLib/rdflib)

The RDFExtras project offers several additional stores as well as a 
SPARQL engine for use with RDFLib: 

https://github.com/RDFLib/rdfextras/

The documentation can be built by doing::

    $ python setup.py build_sphinx

And is also available from ReadTheDocs: 

http://readthedocs.org/docs/rdflib/

Support is available through the rdflib-dev group: 

http://groups.google.com/group/rdflib-dev

and on the IRC channel #rdflib on the freenode.net server

