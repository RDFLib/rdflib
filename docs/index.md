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

RDFLib follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), which can be summarised as follows:

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

The RDFLib organisation on GitHub at [https://github.com/RDFLib](https://github.com/RDFLib) maintains this package and a number of other RDF and RDFLib-related packaged that you might also find useful.

## Further help & Contact

If you would like help with using RDFLib, rather than developing it, please post a question on StackOverflow using the tag `[rdflib]`. A list of existing `[rdflib]` tagged questions can be found [here](https://stackoverflow.com/questions/tagged/rdflib).

You might also like to join RDFLib's [dev mailing list](https://groups.google.com/group/rdflib-dev) or use RDFLib's [GitHub discussions section](https://github.com/RDFLib/rdflib/discussions).

The chat is available at [gitter](https://gitter.im/RDFLib/rdflib) or via matrix [#RDFLib_rdflib:gitter.im](https://matrix.to/#/#RDFLib_rdflib:gitter.im).


## History

RDFLib is one of the oldest continuously maintained Python libraries for Semantic Web/RDF work. Its history goes back 
to 2002, only a few years after RDF itself emerged from the W3C. The original author was Daniel “eikeon” Krech but, of 
course, there have been many, many contributors to it since then, just see the long and illustrious file of 
[CONTRIBUTORS](https://github.com/RDFLib/rdflib/blob/main/CONTRIBUTORS).

<h3 id="timeline-summary">Timeline summary</h3>

* **2002** — RDFLib begins
* **2004** — RDFLib 2.0
* **2005** — modern Graph abstraction emerges
* **2006** — SPARQL first supported
* **2010** — RDFLib 3.0; SPARQL temporarily separated into rdfextras
* **2013** — RDFLib 4.0; SPARQL 1.1 returns to core; Dataset introduced
* **2017** — 4.2.2, followed by a long stable period
* **2020** — RDFLib 5.0; final Python-2-supporting major version
* **2021** — RDFLib 6.0; Python 3 only, JSON-LD integrated
* **2023** — RDFLib 7.0
* **2026** — RDFLib 7.6, with RDF4J/GraphDB integration.

<h3 id="early-years">Early Years</h3>

RDFLib already had RDF/XML parsing, literals, blank nodes, triple stores and serialization right back in November 2002
with the 1.1 release with context support - now Named Graphs - appearing in December of that same year.

RDFLib 2.1, released in April 2005, merged the previous TripleStore and InformationStore concepts into the Graph class
which remains the centre of RDFLib today. N3 support arrived in the 2.3 series, and SPARQL query support was added in 
RDFLib 2.3.2 in August 2006.

<h3 id="teenager">Teenager</h3>

RDFLib 3.0.0 was released on 13 May 2010 and move a lot of functionality into plugins, to keep the core small. This is
still the approach today with RDF inferencing recently being added as a plugin.

In 2013, RDF 1.1 features started appearing in the 4.x releases and `SPARQStore` too. For the 4.1 release, RDFLib had 
over 2,000 unit tests.

<h3 id="stable-times">Stable times</h3>

From 2017 to 2020, RDFLib 4.2.2 was the stable release with 5.0.0 in April 2020 just rolling up small fixes and 
improvements that had accumulated over time: no major changes

<h3 id="post-python-2">Post Python 2</h3>

Version 6.0.0 arrived on 20 July 2021, dropping Python 2 and Python versions before 3.7. JSON-LD handling was 
internalised and type annotations started to get applied widely.

<h3 id="7-and-beyond">7 and beyond</h3>

RDFLib 7.0.0 was released on 2 August 2023. Its breaking changes were small, but it began cleaning up some long-standing 
RDFLib behaviours, particularly around `Dataset`, default graphs and the `publicID` argument to `parse()`. Python 3.7 
support was dropped.
