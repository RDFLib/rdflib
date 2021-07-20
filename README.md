![](docs/_static/RDFlib.png)    

RDFLib
======
[![Build Status](https://travis-ci.org/RDFLib/rdflib.png?branch=master)](https://travis-ci.org/RDFLib/rdflib)
[![Coveralls branch](https://img.shields.io/coveralls/RDFLib/rdflib/master.svg)](https://coveralls.io/r/RDFLib/rdflib?branch=master)
[![GitHub stars](https://img.shields.io/github/stars/RDFLib/rdflib.svg)](https://github.com/RDFLib/rdflib/stargazers)
[![PyPI](https://img.shields.io/pypi/v/rdflib.svg)](https://pypi.python.org/pypi/rdflib)
[![PyPI](https://img.shields.io/pypi/pyversions/rdflib.svg)](https://pypi.python.org/pypi/rdflib)

RDFLib is a pure Python package for working with [RDF](http://www.w3.org/RDF/). RDFLib contains most things you need to work with RDF, including:

* parsers and serializers for RDF/XML, N3, NTriples, N-Quads, Turtle, TriX, Trig and JSON-LD
* a Graph interface which can be backed by any one of a number of Store implementations
* store implementations for in-memory, persistent on disk (Berkeley DB) and remote SPARQL endpoints
* a SPARQL 1.1 implementation - supporting SPARQL 1.1 Queries and Update statements
* SPARQL function extension mechanisms

## RDFlib Family of packages
The RDFlib community maintains many RDF-related Python code repositories with different purposes. For example:

* [rdflib](https://github.com/RDFLib/rdflib) - the RDFLib core
* [sparqlwrapper](https://github.com/RDFLib/sparqlwrapper) - a simple Python wrapper around a SPARQL service to remotely execute your queries
* [pyLODE](https://github.com/RDFLib/pyLODE) - An OWL ontology documentation tool using Python and templating, based on LODE.

Please see the list for all packages/repositories here:

* <https://github.com/RDFLib>

## Versions & Releases

* `6.0.1-alpha` current `master` branch
* `6.x.y` current release and support Python 3.7+ only. Many improvements over 5.0.0
* `5.x.y` supports Python 2.7 and 3.4+ and is [mostly backwards compatible with 4.2.2](https://rdflib.readthedocs.io/en/stable/upgrade4to5.html).

See <https://rdflib.dev> for the release schedule.

## Documentation
See <https://rdflib.readthedocs.io> for our documentation built from the code. Note that there are `latest`, `stable` `5.0.0` and `4.2.2` documentation versions, matching releases.

## Installation
The stable release of RDFLib may be installed with Python's package management tool *pip*:

    $ pip install rdflib

Alternatively manually download the package from the Python Package
Index (PyPI) at https://pypi.python.org/pypi/rdflib

The current version of RDFLib is 6.0.0, see the ``CHANGELOG.md`` file for what's new in this release.

### Installation of the current master branch (for developers)

With *pip* you can also install rdflib from the git repository with one of the following options:

    $ pip install git+https://github.com/rdflib/rdflib@master

or

    $ pip install -e git+https://github.com/rdflib/rdflib@master#egg=rdflib

or from your locally cloned repository you can install it with one of the following options:

    $ python setup.py install

or

    $ pip install -e .

## Getting Started
RDFLib aims to be a pythonic RDF API. RDFLib's main data object is a `Graph` which is a Python collection
of RDF *Subject, Predicate, Object* Triples:

To create graph and load it with RDF data from DBPedia then print the results:

```python
from rdflib import Graph
g = Graph()
g.parse('http://dbpedia.org/resource/Semantic_Web')

for s, p, o in g:
    print(s, p, o)
```
The components of the triples are URIs (resources) or Literals
(values).

URIs are grouped together by *namespace*, common namespaces are included in RDFLib:

```python
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
```

You can use them like this:

```python
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

g = Graph()
semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
type = g.value(semweb, RDFS.label)
```
Where `RDFS` is the RDFS Namespace, `g.value` returns an object of the triple-pattern given (or an arbitrary one if more exist).

Or like this, adding a triple to a graph `g`:

```python
g.add((
    URIRef("http://example.com/person/nick"),
    FOAF.givenName,
    Literal("Nick", datatype=XSD.string)
))
```
The triple (in n-triples notation) `<http://example.com/person/nick> <http://xmlns.com/foaf/0.1/givenName> "Nick"^^<http://www.w3.org/2001/XMLSchema#string> .`
is created where the property `FOAF.giveName` is the URI `<http://xmlns.com/foaf/0.1/givenName>` and `XSD.string` is the
URI `<http://www.w3.org/2001/XMLSchema#string>`.

You can bind namespaces to prefixes to shorten the URIs for RDF/XML, Turtle, N3, TriG, TriX & JSON-LD serializations:

 ```python
g.bind("foaf", FOAF)
g.bind("xsd", XSD)
```
This will allow the n-triples triple above to be serialised like this:
 ```python
print(g.serialize(format="turtle"))
```

With these results:
```turtle
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<http://example.com/person/nick> foaf:givenName "Nick"^^xsd:string .
```

New Namespaces can also be defined:

```python
dbpedia = Namespace('http://dbpedia.org/ontology/')

abstracts = list(x for x in g.objects(semweb, dbpedia['abstract']) if x.language=='en')
```

See also [./examples](./examples)


## Features
The library contains parsers and serializers for RDF/XML, N3,
NTriples, N-Quads, Turtle, TriX, JSON-LD, RDFa and Microdata.

The library presents a Graph interface which can be backed by
any one of a number of Store implementations.

This core RDFLib package includes store implementations for
in-memory storage and persistent storage on top of the Berkeley DB.

A SPARQL 1.1 implementation is included - supporting SPARQL 1.1 Queries and Update statements.

RDFLib is open source and is maintained on [GitHub](https://github.com/RDFLib/rdflib/). RDFLib releases, current and previous
are listed on [PyPI](https://pypi.python.org/pypi/rdflib/)

Multiple other projects are contained within the RDFlib "family", see <https://github.com/RDFLib/>.

## Running tests

### Running the tests on the host

Run the test suite with `nose`.
```shell
nosetests
```

### Running test coverage on the host with coverage report

Run the test suite and generate a HTML coverage report with `nose` and `coverage`.
```shell
nosetests --with-timer --timer-top-n 42 --with-coverage --cover-tests --cover-package=rdflib
```

There is also a script, `run_tests.py` to run everything.

### Running the tests in a Docker container

Run the test suite inside a Docker container for cross-platform support. This resolves issues such as installing BerkeleyDB on Windows and avoids the host and port issues on macOS.
```shell
make tests
```

Tip: If the underlying Dockerfile for the test runner changes, use `make build`.

### Running the tests in a Docker container with coverage report

Run the test suite inside a Docker container with HTML coverage report.
```shell
make coverage
```

### Viewing test coverage

Once tests have produced HTML output of the coverage report, view it by running:
```shell
python -m http.server --directory=cover
```

## Contributing

RDFLib survives and grows via user contributions!
Please read our [contributing guide](https://rdflib.readthedocs.io/en/stable/developers.html) to get started.
Please consider lodging Pull Requests here:

* <https://github.com/RDFLib/rdflib/pulls>

You can also raise issues here:

* <https://github.com/RDFLib/rdflib/issues>

## Support & Contacts
For general "how do I..." queries, please use https://stackoverflow.com and tag your question with `rdflib`.
Existing questions:

* <https://stackoverflow.com/questions/tagged/rdflib>

If you want to contact the rdflib maintainers, please do so via:

* the rdflib-dev mailing list: <https://groups.google.com/group/rdflib-dev>
* the chat, which is available at [gitter](https://gitter.im/RDFLib/rdflib) or via matrix [#RDFLib_rdflib:gitter.im](https://matrix.to/#/#RDFLib_rdflib:gitter.im)
