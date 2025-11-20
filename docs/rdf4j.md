[Eclipse RDF4J](https://rdf4j.org/) is an open-source Java framework for working with RDF. Out of the box, it supports running database servers and allows clients to interact with them through an HTTP protocol known as the RDF4J REST API. This API fully supports all SPARQL 1.1 W3C Recommendations and also provides additional operations for managing RDF4J concepts such as repositories and transactions. For more details about the RDF4J REST API and its capabilities, see the [official documentation](https://rdf4j.org/documentation/reference/rest-api/).

RDFLib provides two options to interface with the RDF4J REST API:

1. **Store integration** - A full RDFLib Store implementation that lets users interact with RDF4J repositories seamlessly through RDFLib’s `Graph` and `Dataset` classes.
2. **RDF4J Client** - A lower-level client that gives users more control over interactions with the RDF4J REST API. It covers all operations supported by the RDF4J REST API, including managing repositories and transactions.

To use RDFLib with RDF4J, first install RDFLib with the optional `rdf4j` extra.

```shell
pip install rdflib[rdf4j]
```

## RDFLib RDF4J Store

An RDF4J Store connects to a single RDF4J repository. If you need to work with multiple repositories, you can create multiple Store instances. The RDF4J Store exposes only the subset of repository operations that integrate cleanly with RDFLib’s Graph and Dataset interfaces. If you need to perform additional operations such as managing repositories, you should use the RDF4J Client instead.

### Connecting to an existing repository

To get started, import the RDF4J Store class, create an instance of it, and pass it to the store parameter when creating a `Graph` or `Dataset`.

The following example connects to a local RDF4J server running on port 7200 and accesses an existing repository with the identifier `my-repository`.

If the server requires basic authentication, you can optionally pass a (username, password) tuple to the `auth` parameter.

```python
from rdflib.plugins.stores.rdf4j import RDF4JStore

store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("admin", "admin"),
)
```

### Creating a new repository

If the repository does not exist, an exception will be raised. To create the repository, set the `create` parameter to `True`. This will create the repository using RDF4J’s default configuration settings and then connect to it.

```python
store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("admin", "admin"),
    create=True,
)
```

To create a repository with a custom RDF4J configuration, pass the `configuration` as a string to the configuration parameter.

```python
store = RDF4JStore(
    base_url="http://localhost:7200/",
    repository_id="my-repository",
    auth=("admin", "admin"),
    configuration=configuration,
    create=True,
)
```

### Using the store with RDFLib

Once the store is created, you can create a `Graph` or `Dataset` object and use it as you would with any other RDFLib store.

```python
from rdflib import Dataset

ds = Dataset(store=store)
```

For more information on how to use RDFLib Graphs and Datasets, see the subsections under [Usage](index.md).

## RDF4J Client

...
