# Upgrading from version 7 to 8

!!! warning "In Development"
    This page is in development and will only be completed with the release of RDFLib v8.

## Python version

RDFLib 8 requires Python 3.11 or later. Python 3.10 reached end of life on
1 October 2026. Users who need Python 3.10 must remain on RDFLib 7.x.

The optional `lxml` dependency now requires version 4.9.1 or later for
Python 3.11 compatibility.

## Jelly

RDFLib 8 reads and writes [Jelly](https://w3id.org/jelly), a binary format for
RDF and SPARQL query results, with the format name `jelly`. See
[Jelly](plugins.md#jelly) and [Jelly-SPARQL](plugins.md#jelly-sparql).

For this, RDFLib now depends on [pyjelly](https://w3id.org/jelly/pyjelly),
which depends on [protobuf](https://pypi.org/project/protobuf/) 6.30 or later.
pyjelly is only imported when a Jelly format is used.

If you installed pyjelly before to use Jelly with RDFLib, nothing changes: the
format names are the same.
