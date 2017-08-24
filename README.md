RDFLib
======
[![Build Status](https://travis-ci.org/RDFLib/rdflib.png?branch=master)](https://travis-ci.org/RDFLib/rdflib)
[![Coveralls branch](https://img.shields.io/coveralls/RDFLib/rdflib/master.svg)](https://coveralls.io/r/RDFLib/rdflib?branch=master)
[![GitHub stars](https://img.shields.io/github/stars/RDFLib/rdflib.svg)](https://github.com/RDFLib/rdflib/stargazers)
[![PyPI](https://img.shields.io/pypi/v/rdflib.svg)](https://pypi.python.org/pypi/rdflib)
[![PyPI](https://img.shields.io/pypi/pyversions/rdflib.svg)](https://pypi.python.org/pypi/rdflib)


RDFLib is a Python library for working with RDF, a simple yet
powerful language for representing information as graphs.

RDFLib may be installed with pip (use sudo as required):

    $ pip install rdflib

Alternatively manually download the package from the Python Package
Index (PyPI) at https://pypi.python.org/pypi/rdflib

The current version of RDFLib is 4.2.2, see the ``CHANGELOG.md``
file for what's new.


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

dbpedia=rdflib.Namespace('http://dbpedia.org/ontology/')

abstracts=list(x for x in g.objects(semweb, dbpedia['abstract']) if x.language=='en')
```

See also [./examples](./examples)


Features
--------

The library contains parsers and serializers for RDF/XML, N3,
NTriples, N-Quads, Turtle, TriX, RDFa and Microdata.

The library presents a Graph interface which can be backed by
any one of a number of Store implementations.

This core RDFLib package includes store implementations for
in memory storage and persistent storage on top of the Berkeley DB.

A SPARQL 1.1 implementation is included - supporting SPARQL 1.1 Queries and Update statements.

RDFLib is open source and is maintained on [GitHub](https://github.com/RDFLib/rdflib/). RDFLib releases, current and previous
are listed on [PyPI](https://pypi.python.org/pypi/rdflib/)

RDFLib has a plugin-architecture for store-implementation, as well as parsers/serializers, several other projects exist which extend RDFLib features:

 * [rdflib-jsonld](https://github.com/RDFLib/rdflib-jsonld) - Serializer and parser for [json-ld](http://json-ld.org)

Support
-------

More information is available on the project webpage:

https://github.com/RDFLib/rdflib/

The documentation can be built by doing::

    $ python setup.py build_sphinx

And is also available from ReadTheDocs:

https://rdflib.readthedocs.io

Support is available through the rdflib-dev group:

https://groups.google.com/group/rdflib-dev

and on the IRC channel #rdflib on the freenode.net server
