[GraphDB by Ontotext](https://graphdb.ontotext.com/) is an enterprise-ready semantic graph database that supports many W3C standards.

Ontotext provides GraphDB in two editions:

- **GraphDB Free** — free to use, with limits on concurrency, scalability, and available connectors.
- **GraphDB Enterprise** — commercial edition that removes the Free edition’s limits and adds enterprise features and additional connectors.

The simplest way to get started with GraphDB is to run it in a container. The [ontotext/graphdb](https://hub.docker.com/r/ontotext/graphdb/) image on Docker Hub includes instructions on how to run and operate the database.

!!! note

    From GraphDB 11 onwards, all editions (including GraphDB Free) require a license. You can register for one on the [GraphDB website](https://www.ontotext.com/products/graphdb/).

GraphDB supports programmatic access via a set of REST APIs. It implements the [RDF4J REST API](https://rdf4j.org/documentation/reference/rest-api/), which allows you to manage repositories, perform SPARQL queries and updates, and manage RDF data. If you only need these capabilities, see the [RDFLib RDF4J](rdf4j.md) documentation for details on using the RDFLib RDF4J Store or Client.

GraphDB also provides its own REST API for administrative and maintenance-related actions. See the GraphDB documentation at https://graphdb.ontotext.com/documentation/. If you need programmatic access to these GraphDB-specific features, the following sections describe how to use RDFLib's GraphDB Client.
