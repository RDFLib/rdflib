![RDFLib logo](_static/RDFlib.png)

# RDFLib

RDFLib is a pure Python package for working with [RDF](http://www.w3.org/RDF/). It contains:

* **Parsers & Serializers**
    * for RDF/XML, N3, NTriples, N-Quads, Turtle, TriG, TriX, JSON-LD, HexTuples, RDFa and Microdata

* **Store implementations**
    * memory stores
    * persistent, on-disk stores, using databases such as BerkeleyDB
    * remote SPARQL endpoints

* **Graph interface**
    * to a single graph
    * or to multiple Named Graphs within a dataset

* **SPARQL 1.1 implementation**
    * both Queries and Updates are supported

!!! warning "Security considerations"
    RDFLib is designed to access arbitrary network and file resources, in some
    cases these are directly requested resources, in other cases they are
    indirectly referenced resources.

    If you are using RDFLib to process untrusted documents or queries you should
    take measures to restrict file and network access.

    For information on available security measures, see the RDFLib
    [Security Considerations](security_considerations.md)
    documentation.

## Getting started

If you have never used RDFLib, the following will help get you started:

* [Getting Started](gettingstarted.md)
* [Introduction to Parsing](intro_to_parsing.md)
* [Introduction to Creating RDF](intro_to_creating_rdf.md)
* [Introduction to Graphs](intro_to_graphs.md)
* [Introduction to SPARQL](intro_to_sparql.md)
* [Utilities](utilities.md)
* [Examples](apidocs/examples.md)

## In depth

If you are familiar with RDF and are looking for details on how RDFLib handles it, these are for you:

* [RDF Terms](rdf_terms.md)
* [Namespaces and Bindings](namespaces_and_bindings.md)
* [Persistence](persistence.md)
* [Merging](merging.md)
* [Changelog](changelog.md)
* [Upgrade 6 to 7](upgrade6to7.md)
* [Upgrade 5 to 6](upgrade5to6.md)
* [Upgrade 4 to 5](upgrade4to5.md)
* [Security Considerations](security_considerations.md)

## Versioning

RDFLib follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), which can be summarized as follows:

Given a version number `MAJOR.MINOR.PATCH`, increment the:

1. `MAJOR` version when you make incompatible API changes
2. `MINOR` version when you add functionality in a backwards-compatible manner
3. `PATCH` version when you make backwards-compatible bug fixes

## For developers

* [Developers guide](developers.md)
* [Documentation guide](docs.md)
* [Contributing guide](CONTRIBUTING.md)
* [Code of Conduct](CODE_OF_CONDUCT.md)
* [Persisting N3 Terms](persisting_n3_terms.md)
* [Type Hints](type_hints.md)
* [Decisions](decisions.md)

## Source Code

The rdflib source code is hosted on GitHub at [https://github.com/RDFLib/rdflib](https://github.com/RDFLib/rdflib) where you can lodge Issues and create Pull Requests to help improve this community project!

The RDFlib organisation on GitHub at [https://github.com/RDFLib](https://github.com/RDFLib) maintains this package and a number of other RDF and RDFlib-related packaged that you might also find useful.

## Further help & Contact

If you would like help with using RDFlib, rather than developing it, please post a question on StackOverflow using the tag `[rdflib]`. A list of existing `[rdflib]` tagged questions can be found [here](https://stackoverflow.com/questions/tagged/rdflib).

You might also like to join RDFlib's [dev mailing list](https://groups.google.com/group/rdflib-dev) or use RDFLib's [GitHub discussions section](https://github.com/RDFLib/rdflib/discussions).

The chat is available at [gitter](https://gitter.im/RDFLib/rdflib) or via matrix [#RDFLib_rdflib:gitter.im](https://matrix.to/#/#RDFLib_rdflib:gitter.im).
